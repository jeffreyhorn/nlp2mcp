"""
Tests for IndexOffset support in AD index substitution (Sprint 19 Day 12).

Covers:
- _substitute_index() with plain strings and IndexOffset nodes
- _apply_index_substitution() on VarRef/ParamRef with IndexOffset indices
- Full differentiation: d/dx(t) [x(t+1)] = 0 (different index)
- Full differentiation: d/dx(t+1) [x(t+1)] = 1 (matching IndexOffset index)
- Sum collapse with lead/lag variable
- DollarConditional substitution (bonus coverage)
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import (
    _apply_index_substitution,
    _is_concrete_instance_of,
    _partial_index_match,
    _substitute_index,
    _sum_should_collapse,
    differentiate_expr,
)
from src.ir.ast import (
    Binary,
    Const,
    DollarConditional,
    IndexOffset,
    ParamRef,
    Sum,
    SymbolRef,
    VarRef,
)

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# _substitute_index() — unit tests for the helper
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSubstituteIndex:
    """Unit tests for _substitute_index() helper."""

    def test_plain_string_substituted(self):
        """Plain string index is looked up in the substitution map."""
        result = _substitute_index("i", {"i": "i1"})
        assert result == "i1"

    def test_plain_string_not_in_map_unchanged(self):
        """Plain string index not in map is returned unchanged."""
        result = _substitute_index("j", {"i": "i1"})
        assert result == "j"

    def test_plain_string_empty_map(self):
        """Plain string with empty substitution map returns unchanged."""
        result = _substitute_index("i", {})
        assert result == "i"

    def test_index_offset_base_substituted(self):
        """IndexOffset base is substituted; offset and circular preserved."""
        idx = IndexOffset("t", Const(1.0), False)
        result = _substitute_index(idx, {"t": "t1"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t1"
        assert result.offset == Const(1.0)
        assert result.circular is False

    def test_index_offset_circular_preserved(self):
        """IndexOffset circular=True flag is preserved after substitution."""
        idx = IndexOffset("i", Const(1.0), True)
        result = _substitute_index(idx, {"i": "i3"})
        assert isinstance(result, IndexOffset)
        assert result.base == "i3"
        assert result.circular is True

    def test_index_offset_base_not_in_map_unchanged(self):
        """IndexOffset whose base is not in the map is returned unchanged."""
        idx = IndexOffset("t", Const(1.0), False)
        result = _substitute_index(idx, {"s": "s1"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t"
        assert result.offset == Const(1.0)
        assert result.circular is False

    def test_index_offset_empty_map_unchanged(self):
        """IndexOffset with empty substitution map is returned unchanged."""
        idx = IndexOffset("t", Const(2.0), False)
        result = _substitute_index(idx, {})
        assert isinstance(result, IndexOffset)
        assert result.base == "t"
        assert result.offset == Const(2.0)

    def test_index_offset_with_symbol_offset_substituted(self):
        """IndexOffset with SymbolRef offset: offset IS substituted."""
        offset = SymbolRef("lag")
        idx = IndexOffset("t", offset, False)
        result = _substitute_index(idx, {"t": "t5", "lag": "lag2"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t5"
        # offset SymbolRef is substituted when the name is in the map
        assert isinstance(result.offset, SymbolRef)
        assert result.offset.name == "lag2"

    def test_index_offset_offset_unchanged_when_not_in_map(self):
        """IndexOffset offset preserved when SymbolRef not in substitution map."""
        offset = SymbolRef("lag")
        idx = IndexOffset("t", offset, False)
        result = _substitute_index(idx, {"t": "t5"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t5"
        assert result.offset is offset

    def test_index_offset_negative_offset_preserved(self):
        """IndexOffset with negative offset: offset unchanged."""
        idx = IndexOffset("t", Const(-3.0), False)
        result = _substitute_index(idx, {"t": "t1"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t1"
        assert result.offset == Const(-3.0)


# ---------------------------------------------------------------------------
# _apply_index_substitution() — VarRef/ParamRef with IndexOffset
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestApplyIndexSubstitutionWithIndexOffset:
    """Tests for _apply_index_substitution() with IndexOffset in index tuples."""

    def test_varref_plain_index_substituted(self):
        """Plain string index in VarRef is substituted normally."""
        expr = VarRef("x", ("i",))
        result = _apply_index_substitution(expr, {"i": "i1"})
        assert isinstance(result, VarRef)
        assert result.name == "x"
        assert result.indices == ("i1",)

    def test_varref_index_offset_base_substituted(self):
        """IndexOffset base in VarRef index tuple is substituted."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        result = _apply_index_substitution(expr, {"t": "t1"})
        assert isinstance(result, VarRef)
        assert result.name == "x"
        assert len(result.indices) == 1
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "t1"
        assert idx.offset == Const(1.0)
        assert idx.circular is False

    def test_varref_mixed_plain_and_offset_indices(self):
        """VarRef with both plain string and IndexOffset indices."""
        expr = VarRef("x", ("i", IndexOffset("t", Const(1.0), False)))
        result = _apply_index_substitution(expr, {"i": "i3", "t": "t5"})
        assert isinstance(result, VarRef)
        assert result.indices[0] == "i3"
        assert isinstance(result.indices[1], IndexOffset)
        assert result.indices[1].base == "t5"

    def test_varref_index_offset_base_not_in_map(self):
        """IndexOffset base not in substitution map: VarRef returned with original base."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        result = _apply_index_substitution(expr, {"s": "s1"})
        assert isinstance(result, VarRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "t"  # unchanged

    def test_paramref_index_offset_substituted(self):
        """IndexOffset base in ParamRef index tuple is substituted."""
        expr = ParamRef("a", (IndexOffset("i", Const(1.0), True),))
        result = _apply_index_substitution(expr, {"i": "i2"})
        assert isinstance(result, ParamRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "i2"
        assert idx.circular is True

    def test_dollar_conditional_substituted(self):
        """DollarConditional: both value_expr and condition are substituted."""
        value_expr = VarRef("x", ("i",))
        condition = VarRef("mask", ("i",))
        expr = DollarConditional(value_expr, condition)
        result = _apply_index_substitution(expr, {"i": "i1"})
        assert isinstance(result, DollarConditional)
        assert isinstance(result.value_expr, VarRef)
        assert result.value_expr.indices == ("i1",)
        assert isinstance(result.condition, VarRef)
        assert result.condition.indices == ("i1",)


# ---------------------------------------------------------------------------
# Full differentiation with IndexOffset wrt_indices
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDifferentiateWithIndexOffset:
    """
    Full differentiation tests involving IndexOffset.

    Key semantic rule: x(t) and x(t+1) are distinct decision variables.
    The frozen-dataclass equality of VarRef means IndexOffset("t", Const(1), False)
    ≠ "t", so cross-index derivatives are automatically 0.
    """

    def test_diff_xt_wrt_xt1_is_zero(self):
        """d/dx(t) [x(t+1)] = 0 — different time index."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        # Differentiating w.r.t. x at plain index "t"
        result = differentiate_expr(expr, "x", ("t",))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_diff_xt1_wrt_xt1_is_one(self):
        """d/dx(t+1) [x(t+1)] = 1 — exact IndexOffset match."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        # Differentiating w.r.t. x at IndexOffset("t", Const(1), False)
        result = differentiate_expr(expr, "x", (IndexOffset("t", Const(1.0), False),))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_diff_xt_minus1_wrt_xt1_is_zero(self):
        """d/dx(t-1) [x(t+1)] = 0 — different offset."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        result = differentiate_expr(expr, "x", (IndexOffset("t", Const(-1.0), False),))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_diff_xt1_circular_wrt_xt1_linear_is_zero(self):
        """d/dx(t++1) [x(t+1)] = 0 — different circular flag."""
        linear = VarRef("x", (IndexOffset("t", Const(1.0), False),))
        # Differentiating w.r.t. x at circular IndexOffset
        result = differentiate_expr(linear, "x", (IndexOffset("t", Const(1.0), True),))
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_diff_xt1_circular_wrt_xt1_circular_is_one(self):
        """d/dx(t++1) [x(t++1)] = 1 — circular IndexOffset matches itself."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), True),))
        result = differentiate_expr(expr, "x", (IndexOffset("t", Const(1.0), True),))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_diff_sum_over_t_with_lead(self):
        """d/dx(t1+1) [sum(t, x(t+1))] collapses to 1.

        After sum collapse: only the t=t1 term survives (x(t1+1) matches x(t+1)
        when t=t1), so result = 1.
        """
        expr = Sum(("t",), VarRef("x", (IndexOffset("t", Const(1.0), False),)))
        wrt = (IndexOffset("t1", Const(1.0), False),)
        result = differentiate_expr(expr, "x", wrt)
        # Sum should collapse: the only contributing term is t=t1
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_diff_sum_with_plain_index_and_lead_body(self):
        """d/dx(t1) [sum(t, x(t+1))] = 0.

        x(t+1) is never x(t) for any integer t, so all derivatives are 0.
        """
        expr = Sum(("t",), VarRef("x", (IndexOffset("t", Const(1.0), False),)))
        # Differentiating w.r.t. plain x(t1)
        result = differentiate_expr(expr, "x", ("t1",))
        # No term in the sum produces x(t1), so result is 0 (or sum of zeros)
        if isinstance(result, Const):
            assert result.value == 0.0
        else:
            # Sum of zeros — the body should be zero
            assert isinstance(result, Sum)
            assert isinstance(result.body, Const)
            assert result.body.value == 0.0

    def test_diff_binary_with_lead_and_plain(self):
        """d/dx(t+1) [x(t) + x(t+1)] = 0 + 1 = 1 (structurally)."""
        expr = Binary(
            "+",
            VarRef("x", ("t",)),
            VarRef("x", (IndexOffset("t", Const(1.0), False),)),
        )
        wrt = (IndexOffset("t", Const(1.0), False),)
        result = differentiate_expr(expr, "x", wrt)
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Const)
        assert result.left.value == 0.0  # x(t) does not match x(t+1)
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0  # x(t+1) matches x(t+1)

    def test_diff_sum_over_t_with_lag(self):
        """d/dx(t1-1) [sum(t, x(t-1))] collapses to 1.

        Lag variant: sum over t of x(t-1), differentiate w.r.t. x(t1-1).
        """
        expr = Sum(("t",), VarRef("x", (IndexOffset("t", Const(-1.0), False),)))
        wrt = (IndexOffset("t1", Const(-1.0), False),)
        result = differentiate_expr(expr, "x", wrt)
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_diff_sum_param_times_lead_var(self):
        """d/dx(t1+1) [sum(t, a(t) * x(t+1))] produces product rule with a(t1).

        Product rule under sum collapse: the derivative of a(t)*x(t+1) w.r.t.
        x(t+1) gives x(t+1)*0 + a(t)*1, then substituting t→t1.
        """
        expr = Sum(
            ("t",),
            Binary(
                "*",
                ParamRef("a", ("t",)),
                VarRef("x", (IndexOffset("t", Const(1.0), False),)),
            ),
        )
        wrt = (IndexOffset("t1", Const(1.0), False),)
        result = differentiate_expr(expr, "x", wrt)
        # Product rule: x(t1+1)*0 + a(t1)*1  (unsimplified)
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Right term should be a(t1) * 1.0
        assert isinstance(result.right, Binary)
        assert result.right.op == "*"
        assert isinstance(result.right.left, ParamRef)
        assert result.right.left.name == "a"
        assert result.right.left.indices == ("t1",)
        assert isinstance(result.right.right, Const)
        assert result.right.right.value == 1.0


# ---------------------------------------------------------------------------
# IndexOffset handling in _is_concrete_instance_of, _sum_should_collapse, _partial_index_match
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIndexOffsetInCollapseFunctions:
    """Tests for IndexOffset support in sum collapse helper functions."""

    def test_is_concrete_instance_of_with_index_offset_no_crash(self):
        """_is_concrete_instance_of with IndexOffset doesn't crash, returns False."""
        io = IndexOffset("t1", Const(1.0), False)
        result = _is_concrete_instance_of(io, "t")
        assert result is False

    def test_is_concrete_instance_of_with_string_still_works(self):
        """_is_concrete_instance_of still works normally with strings."""
        assert _is_concrete_instance_of("t1", "t") is True
        assert _is_concrete_instance_of("t", "t") is False
        assert _is_concrete_instance_of("j1", "t") is False

    def test_sum_should_collapse_with_index_offset_wrt(self):
        """_sum_should_collapse matches IndexOffset base against symbolic index."""
        wrt = (IndexOffset("t1", Const(1.0), False),)
        assert _sum_should_collapse(("t",), wrt) is True

    def test_sum_should_collapse_index_offset_no_match(self):
        """_sum_should_collapse returns False when IndexOffset base doesn't match."""
        wrt = (IndexOffset("j1", Const(1.0), False),)
        assert _sum_should_collapse(("t",), wrt) is False

    def test_sum_should_collapse_mixed_str_and_index_offset(self):
        """_sum_should_collapse with mixed str and IndexOffset wrt_indices."""
        wrt = ("i1", IndexOffset("t1", Const(1.0), False))
        assert _sum_should_collapse(("i", "t"), wrt) is True

    def test_partial_index_match_with_index_offset(self):
        """_partial_index_match finds IndexOffset match by base index."""
        wrt = (IndexOffset("t1", Const(1.0), False), "extra")
        matched_sym, matched_conc, remaining, symbolic_wrt = _partial_index_match(("t",), wrt)
        assert matched_sym == ("t",)
        assert matched_conc == (IndexOffset("t1", Const(1.0), False),)
        assert remaining == ("extra",)
        assert symbolic_wrt is not None


# ---------------------------------------------------------------------------
# _substitute_indices() from constraint_jacobian — IndexOffset support (#1045)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSubstituteIndicesIndexOffset:
    """Tests for _substitute_indices() in constraint_jacobian handling IndexOffset.

    Issue #1045: _substitute_indices didn't handle IndexOffset nodes in VarRef/ParamRef
    indices, so lead/lag variable references like k(t+1) were never concretized and
    produced zero Jacobian entries.
    """

    @staticmethod
    def _substitute_indices(expr, symbolic, concrete):
        from src.ad.constraint_jacobian import _substitute_indices

        return _substitute_indices(expr, symbolic, concrete)

    def test_varref_plain_index_substituted(self):
        """Baseline: plain string index in VarRef is substituted."""
        expr = VarRef("k", ("t",))
        result = self._substitute_indices(expr, ("t",), ("1990",))
        assert isinstance(result, VarRef)
        assert result.name == "k"
        assert result.indices == ("1990",)

    def test_varref_index_offset_base_substituted(self):
        """IndexOffset base in VarRef is substituted: k(t+1) with t→1990 → k(1990+1)."""
        expr = VarRef("k", (IndexOffset("t", Const(1.0), False),))
        result = self._substitute_indices(expr, ("t",), ("1990",))
        assert isinstance(result, VarRef)
        assert result.name == "k"
        assert len(result.indices) == 1
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "1990"
        assert idx.offset == Const(1.0)
        assert idx.circular is False

    def test_varref_index_offset_unmatched_base_unchanged(self):
        """IndexOffset whose base doesn't match symbolic indices is unchanged."""
        expr = VarRef("k", (IndexOffset("s", Const(1.0), False),))
        result = self._substitute_indices(expr, ("t",), ("1990",))
        assert isinstance(result, VarRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "s"  # unchanged

    def test_varref_mixed_plain_and_offset(self):
        """VarRef with both plain and IndexOffset indices: both are substituted."""
        expr = VarRef("x", ("i", IndexOffset("t", Const(1.0), False)))
        result = self._substitute_indices(expr, ("i", "t"), ("i1", "1990"))
        assert isinstance(result, VarRef)
        assert result.indices[0] == "i1"
        idx = result.indices[1]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "1990"

    def test_paramref_index_offset_base_substituted(self):
        """IndexOffset base in ParamRef is substituted."""
        expr = ParamRef("a", (IndexOffset("t", Const(1.0), False),))
        result = self._substitute_indices(expr, ("t",), ("1990",))
        assert isinstance(result, ParamRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "1990"

    def test_binary_with_index_offset_in_children(self):
        """Binary containing VarRefs with IndexOffset: both children substituted."""
        # k(t) * spda + k(t+1)
        expr = Binary(
            "+",
            VarRef("k", ("t",)),
            VarRef("k", (IndexOffset("t", Const(1.0), False),)),
        )
        result = self._substitute_indices(expr, ("t",), ("1990",))
        assert isinstance(result, Binary)
        assert isinstance(result.left, VarRef)
        assert result.left.indices == ("1990",)
        assert isinstance(result.right, VarRef)
        idx = result.right.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "1990"

    def test_index_offset_circular_preserved(self):
        """IndexOffset circular=True is preserved through substitution."""
        expr = VarRef("x", (IndexOffset("t", Const(1.0), True),))
        result = self._substitute_indices(expr, ("t",), ("1990",))
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.circular is True

    def test_differentiation_after_substitution_nonzero(self):
        """End-to-end: substitute then differentiate produces non-zero for matching lead/lag.

        For totalcap(1990): k(t+1) → k(1990+1), then d/dk(1990+1) should be 1.
        """
        # k(t+1) before substitution
        expr = VarRef("k", (IndexOffset("t", Const(1.0), False),))
        # Substitute t → "1990"
        subst = self._substitute_indices(expr, ("t",), ("1990",))
        # The result should be k(IndexOffset("1990", 1, False))
        assert subst.indices[0] == IndexOffset("1990", Const(1.0), False)
        # Now differentiate w.r.t. k at that exact index
        result = differentiate_expr(subst, "k", (IndexOffset("1990", Const(1.0), False),))
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_differentiation_after_substitution_plain_vs_offset(self):
        """After substitution, k(1990) and k(1990+1) are distinct variables.

        d/dk(1990) [k(1990+1)] = 0
        """
        expr = VarRef("k", (IndexOffset("t", Const(1.0), False),))
        subst = self._substitute_indices(expr, ("t",), ("1990",))
        # Differentiate w.r.t. k at plain index "1990" (no offset)
        result = differentiate_expr(subst, "k", ("1990",))
        assert isinstance(result, Const)
        assert result.value == 0.0


# ---------------------------------------------------------------------------
# _resolve_index_offsets() from constraint_jacobian — domain resolution (#1045)
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResolveIndexOffsets:
    """Tests for _resolve_index_offsets() that resolves IndexOffset to concrete elements.

    Issue #1045: After _substitute_indices turns k(t+1) into k(IndexOffset("1990", 1)),
    _resolve_index_offsets looks up the domain set and resolves it to k("1995") (the
    next element), enabling proper differentiation matching.
    """

    @staticmethod
    def _make_model_ir():
        """Create a minimal model_ir with a set t and variable k(t)."""
        from unittest.mock import MagicMock

        model_ir = MagicMock()
        # Set t = {1990, 1995, 2000, 2005, 2010}
        set_def = MagicMock()
        set_def.members = ["1990", "1995", "2000", "2005", "2010"]
        model_ir.sets = {"t": set_def}
        model_ir.aliases = {}
        # Variable k(t)
        var_def = MagicMock()
        var_def.domain = ("t",)
        model_ir.variables = {"k": var_def, "kn": var_def}
        # Parameter (empty for now) — align attribute name with real ModelIR
        model_ir.params = {}
        model_ir.parameters = model_ir.params
        return model_ir

    @staticmethod
    def _resolve(expr, model_ir):
        from src.ad.constraint_jacobian import _resolve_index_offsets

        return _resolve_index_offsets(expr, model_ir)

    def test_plain_varref_unchanged(self):
        """Plain VarRef without IndexOffset passes through unchanged."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", ("1990",))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, VarRef)
        assert result.indices == ("1990",)

    def test_lead_resolved_to_next_element(self):
        """k(IndexOffset("1990", 1)) resolves to k("1995")."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", (IndexOffset("1990", Const(1.0), False),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, VarRef)
        assert result.name == "k"
        assert result.indices == ("1995",)

    def test_lag_resolved_to_prev_element(self):
        """k(IndexOffset("2000", -1)) resolves to k("1995")."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", (IndexOffset("2000", Const(-1.0), False),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, VarRef)
        assert result.indices == ("1995",)

    def test_lead_out_of_bounds_returns_zero(self):
        """k(IndexOffset("2010", 1)) is out of bounds → Const(0)."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", (IndexOffset("2010", Const(1.0), False),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, Const)
        assert result.value == 0

    def test_lag_out_of_bounds_returns_zero(self):
        """k(IndexOffset("1990", -1)) is out of bounds → Const(0)."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", (IndexOffset("1990", Const(-1.0), False),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, Const)
        assert result.value == 0

    def test_circular_offset_wraps(self):
        """Circular IndexOffset wraps around: k(IndexOffset("2010", 1, circular=True)) → k("1990")."""
        model_ir = self._make_model_ir()
        expr = VarRef("k", (IndexOffset("2010", Const(1.0), True),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, VarRef)
        assert result.indices == ("1990",)

    def test_symbolic_base_unchanged(self):
        """IndexOffset with symbolic base (not in set) passes through unchanged."""
        model_ir = self._make_model_ir()
        # "t" is not a member of set t, so it's symbolic
        expr = VarRef("k", (IndexOffset("t", Const(1.0), False),))
        result = self._resolve(expr, model_ir)
        assert isinstance(result, VarRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "t"

    def test_binary_children_resolved(self):
        """IndexOffset in Binary children are resolved recursively."""
        model_ir = self._make_model_ir()
        expr = Binary(
            "+",
            VarRef("k", ("1990",)),
            VarRef("k", (IndexOffset("1990", Const(1.0), False),)),
        )
        result = self._resolve(expr, model_ir)
        assert isinstance(result, Binary)
        assert result.left.indices == ("1990",)
        assert result.right.indices == ("1995",)

    def test_end_to_end_substitute_resolve_differentiate(self):
        """Full pipeline: substitute → resolve → differentiate gives non-zero.

        For totalcap("1990"): k(t+1) → k(IndexOffset("1990",1)) → k("1995").
        Then d/dk("1995") gives 1.0.
        """
        from src.ad.constraint_jacobian import _substitute_indices

        model_ir = self._make_model_ir()
        # k(t+1) before substitution
        expr = VarRef("k", (IndexOffset("t", Const(1.0), False),))
        # Substitute t → "1990"
        subst = _substitute_indices(expr, ("t",), ("1990",))
        # Resolve IndexOffset
        resolved = self._resolve(subst, model_ir)
        assert isinstance(resolved, VarRef)
        assert resolved.indices == ("1995",)
        # Differentiate w.r.t. k("1995")
        result = differentiate_expr(resolved, "k", ("1995",))
        assert isinstance(result, Const)
        assert result.value == 1.0
