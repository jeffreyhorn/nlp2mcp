"""Unit tests for the #1224 parameter-valued-offset stationarity cross-term helpers
(src/kkt/stationarity.py) — and the PR #1444 review fixes:

- `_expr_mentions_var` must traverse index expressions (a var buried in an
  `IndexOffset` offset must be detected), or `_collect_signed_varrefs` could wrongly
  treat an unsupported shape as safe.
- `_reindex_condition_symbols` re-indexes the equation `$` condition to each
  var-ref's inverted indices, so the cross-term carries the condition (matching the
  generic builder).
"""

from __future__ import annotations

import pytest

from src.ir.ast import (
    Binary,
    Const,
    IndexOffset,
    ParamRef,
    SetMembershipTest,
    SymbolRef,
    Unary,
    VarRef,
)
from src.kkt.stationarity import (
    _collect_signed_varrefs,
    _expr_mentions_var,
    _negate_index_offset_expr,
    _reindex_condition_symbols,
)

pytestmark = pytest.mark.unit


class TestExprMentionsVar:
    def test_finds_bare_varref(self) -> None:
        assert _expr_mentions_var(VarRef("x", ("i",)), "x") is True

    def test_finds_var_inside_index_offset(self) -> None:
        # x(i + y(k)) — y appears only inside the IndexOffset offset. children()
        # does not yield indices, so this must be caught via explicit index traversal.
        e = VarRef("x", (IndexOffset("i", VarRef("y", ("k",)), False),))
        assert _expr_mentions_var(e, "y") is True

    def test_absent_var_not_found(self) -> None:
        e = VarRef("x", (IndexOffset("i", ParamRef("li", ("k",)), False),))
        assert _expr_mentions_var(e, "y") is False


class TestCollectSignedVarrefs:
    def test_lhs_positive_rhs_negative(self) -> None:
        # body x(...) - x(...): lhs sign +1, rhs sign -1.
        lhs = VarRef("x", ("l",))
        rhs = VarRef("x", (IndexOffset("l", Const(1.0), False),))
        refs_l = _collect_signed_varrefs(lhs, 1, "x")
        refs_r = _collect_signed_varrefs(rhs, -1, "x")
        assert refs_l is not None and refs_r is not None
        assert [s for s, _ in refs_l] == [1]
        assert [s for s, _ in refs_r] == [-1]

    def test_bails_on_var_inside_product(self) -> None:
        # var under a product (coeff * x) is out of scope → None (fall back to generic).
        e = Binary("*", ParamRef("a", ()), VarRef("x", ("i",)))
        assert _collect_signed_varrefs(e, 1, "x") is None

    def test_safe_when_other_structure_has_no_var(self) -> None:
        e = Binary("*", ParamRef("a", ()), ParamRef("b", ()))
        assert _collect_signed_varrefs(e, 1, "x") == []

    def test_bails_on_var_buried_in_nontarget_varref_index(self) -> None:
        # z(i + x(k)) — x (the target) is buried in a non-target var-ref's index;
        # the inversion can't handle it → bail (None), not a false "safe" result.
        e = VarRef("z", (IndexOffset("i", VarRef("x", ("k",)), False),))
        assert _collect_signed_varrefs(e, 1, "x") is None

    def test_target_with_param_offset_is_collected(self) -> None:
        # x(l, i+li(k)) — the target with a parameter offset (no nested var) is fine.
        e = VarRef("x", ("l", IndexOffset("i", ParamRef("li", ("k",)), False)))
        refs = _collect_signed_varrefs(e, 1, "x")
        assert refs is not None and len(refs) == 1 and refs[0][0] == 1


class TestNegateIndexOffsetExpr:
    def test_const_negated(self) -> None:
        assert _negate_index_offset_expr(Const(1.0)) == Const(-1.0)

    def test_param_wrapped_in_unary_minus(self) -> None:
        out = _negate_index_offset_expr(ParamRef("li", ("k",)))
        assert isinstance(out, Unary) and out.op == "-"
        assert out.child == ParamRef("li", ("k",))

    def test_double_negation_cancels(self) -> None:
        assert _negate_index_offset_expr(Unary("-", ParamRef("li", ("k",)))) == ParamRef(
            "li", ("k",)
        )


class TestReindexConditionSymbols:
    def test_inverts_setmembership_indices(self) -> None:
        # c(l,i,j) with the lead var-ref's map {l:l, i:i-li(k), j:j-lj(k)}.
        cond = SetMembershipTest("c", (SymbolRef("l"), SymbolRef("i"), SymbolRef("j")))
        name_map = {
            "l": "l",
            "i": IndexOffset("i", Unary("-", ParamRef("li", ("k",))), False),
            "j": IndexOffset("j", Unary("-", ParamRef("lj", ("k",))), False),
        }
        out = _reindex_condition_symbols(cond, name_map)
        assert isinstance(out, SetMembershipTest) and out.set_name == "c"
        assert out.indices[0] == SymbolRef("l")
        assert out.indices[1] == IndexOffset("i", Unary("-", ParamRef("li", ("k",))), False)
        assert out.indices[2] == IndexOffset("j", Unary("-", ParamRef("lj", ("k",))), False)

    def test_lag_term_shifts_l(self) -> None:
        # c(l,i,j) with the lag var-ref's map {l:l-1, i:i, j:j}.
        cond = SetMembershipTest("c", (SymbolRef("l"), SymbolRef("i"), SymbolRef("j")))
        name_map = {"l": IndexOffset("l", Const(-1.0), False), "i": "i", "j": "j"}
        out = _reindex_condition_symbols(cond, name_map)
        assert out.indices[0] == IndexOffset("l", Const(-1.0), False)
        assert out.indices[1] == SymbolRef("i")

    def test_unmapped_symbols_untouched(self) -> None:
        cond = SetMembershipTest("c", (SymbolRef("k"),))
        out = _reindex_condition_symbols(cond, {"l": "l"})
        assert out.indices[0] == SymbolRef("k")

    def test_paramref_guard_indices_remapped(self) -> None:
        # `$a(l)` (a ParamRef guard) with the lag map {l: l-1} must become a(l-1) —
        # ParamRef indices are not in .children(), so they need explicit remapping.
        cond = ParamRef("a", ("l",))
        out = _reindex_condition_symbols(cond, {"l": IndexOffset("l", Const(-1.0), False)})
        assert isinstance(out, ParamRef) and out.name == "a"
        assert out.indices == (IndexOffset("l", Const(-1.0), False),)

    def test_paramref_guard_param_offset_remap(self) -> None:
        # `$a(i)` with the lead map {i: i-li(k)} → a(i-li(k)).
        cond = ParamRef("a", ("i",))
        out = _reindex_condition_symbols(
            cond, {"i": IndexOffset("i", Unary("-", ParamRef("li", ("k",))), False)}
        )
        assert out.indices == (IndexOffset("i", Unary("-", ParamRef("li", ("k",))), False),)

    def test_varref_guard_indices_remapped(self) -> None:
        # `$x(l)` (a VarRef guard, with attribute preserved) → x(l-1).
        cond = VarRef("x", ("l",), "l")
        out = _reindex_condition_symbols(cond, {"l": IndexOffset("l", Const(-1.0), False)})
        assert isinstance(out, VarRef) and out.name == "x" and out.attribute == "l"
        assert out.indices == (IndexOffset("l", Const(-1.0), False),)

    def test_paramref_inside_binary_condition(self) -> None:
        # `a(l) > 0` with {l: l-1} → a(l-1) > 0 (ParamRef nested under Binary).
        cond = Binary(">", ParamRef("a", ("l",)), Const(0.0))
        out = _reindex_condition_symbols(cond, {"l": IndexOffset("l", Const(-1.0), False)})
        assert isinstance(out, Binary) and out.op == ">"
        assert out.left == ParamRef("a", (IndexOffset("l", Const(-1.0), False),))
