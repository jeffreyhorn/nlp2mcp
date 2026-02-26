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

    def test_index_offset_with_symbol_offset_preserved(self):
        """IndexOffset with SymbolRef offset: offset is never substituted."""
        offset = SymbolRef("lag")
        idx = IndexOffset("t", offset, False)
        result = _substitute_index(idx, {"t": "t5", "lag": "lag2"})
        assert isinstance(result, IndexOffset)
        assert result.base == "t5"
        # offset is preserved as-is — it is not a sum index
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
