"""Tests for extract_gradient_conditions() — Issue #1112.

Dollar-condition propagation: extract equation-level guards from gradient
expressions that contain embedded DollarConditional or multiplicative
condition factors from _diff_sum() collapse.
"""

from __future__ import annotations

import pytest

from src.ad.gradient import (
    _extract_condition_from_expr,
    _is_condition_factor,
    extract_gradient_conditions,
)
from src.ad.index_mapping import IndexMapping
from src.ad.jacobian import GradientVector
from src.ir.ast import Binary, Const, DollarConditional, ParamRef, VarRef


def _make_gradient(entries: dict[str, list[tuple[tuple[str, ...], object]]]) -> GradientVector:
    """Build a GradientVector from a dict of var_name -> [(indices, derivative), ...].

    Creates a minimal IndexMapping and populates the gradient.
    """
    # Build col_to_var and var_to_col
    col_to_var: dict[int, tuple[str, tuple[str, ...]]] = {}
    var_to_col: dict[tuple[str, tuple[str, ...]], int] = {}
    col_id = 0
    for var_name, instances in entries.items():
        for indices, _ in instances:
            col_to_var[col_id] = (var_name, indices)
            var_to_col[(var_name, indices)] = col_id
            col_id += 1

    mapping = IndexMapping(
        col_to_var=col_to_var,
        var_to_col=var_to_col,
        num_vars=col_id,
    )
    gradient = GradientVector(index_mapping=mapping, num_cols=col_id)
    col_id = 0
    for _var_name, instances in entries.items():
        for _, deriv in instances:
            gradient.set_derivative(col_id, deriv)
            col_id += 1
    return gradient


@pytest.mark.unit
class TestIsConditionFactor:
    """Test _is_condition_factor helper."""

    def test_dollar_conditional_const_one(self):
        """DollarConditional(Const(1.0), cond) is a condition factor."""
        cond = ParamRef("xw", ("i", "j"))
        expr = DollarConditional(Const(1.0), cond)
        assert _is_condition_factor(expr) is cond

    def test_dollar_conditional_non_one(self):
        """DollarConditional(Const(2.0), cond) is NOT a condition factor."""
        cond = ParamRef("xw", ("i", "j"))
        expr = DollarConditional(Const(2.0), cond)
        assert _is_condition_factor(expr) is None

    def test_non_dollar_conditional(self):
        """A plain Const is not a condition factor."""
        assert _is_condition_factor(Const(1.0)) is None


@pytest.mark.unit
class TestExtractConditionFromExpr:
    """Test _extract_condition_from_expr patterns."""

    def test_top_level_dollar_conditional(self):
        """DollarConditional(deriv, cond) extracts cond."""
        cond = ParamRef("xw", ("i", "j"))
        deriv = VarRef("x", ("i", "j"))
        expr = DollarConditional(deriv, cond)
        assert _extract_condition_from_expr(expr) is cond

    def test_multiplicative_right(self):
        """Binary("*", deriv, DollarConditional(Const(1.0), cond)) extracts cond."""
        cond = ParamRef("xw", ("i", "j"))
        deriv = Binary("*", Const(2.0), VarRef("x", ("i", "j")))
        factor = DollarConditional(Const(1.0), cond)
        expr = Binary("*", deriv, factor)
        assert _extract_condition_from_expr(expr) is cond

    def test_multiplicative_left(self):
        """Binary("*", DollarConditional(Const(1.0), cond), deriv) extracts cond."""
        cond = ParamRef("tw", ("i",))
        factor = DollarConditional(Const(1.0), cond)
        deriv = VarRef("t", ("i",))
        expr = Binary("*", factor, deriv)
        assert _extract_condition_from_expr(expr) is cond

    def test_no_condition(self):
        """Plain expression without condition returns None."""
        expr = Binary("+", VarRef("x", ("i",)), Const(1.0))
        assert _extract_condition_from_expr(expr) is None

    def test_non_multiply_binary(self):
        """Binary("+", ...) is not a multiply — returns None."""
        cond = ParamRef("xw", ("i",))
        factor = DollarConditional(Const(1.0), cond)
        expr = Binary("+", Const(1.0), factor)
        assert _extract_condition_from_expr(expr) is None


@pytest.mark.unit
class TestExtractGradientConditions:
    """Test extract_gradient_conditions aggregation."""

    def test_all_entries_same_condition(self):
        """When all gradient entries share the same condition, return it."""
        cond = ParamRef("xw", ("i", "j"))
        factor = DollarConditional(Const(1.0), cond)
        gradient = _make_gradient(
            {
                "x": [
                    (("i1", "j1"), Binary("*", Const(2.0), factor)),
                    (("i1", "j2"), Binary("*", Const(3.0), factor)),
                    (("i2", "j1"), Binary("*", Const(4.0), factor)),
                ],
            }
        )
        result = extract_gradient_conditions(gradient)
        assert "x" in result
        assert repr(result["x"]) == repr(cond)

    def test_mixed_conditional_unconditional(self):
        """When some entries are unconditional, no common condition."""
        cond = ParamRef("xw", ("i", "j"))
        factor = DollarConditional(Const(1.0), cond)
        gradient = _make_gradient(
            {
                "x": [
                    (("i1", "j1"), Binary("*", Const(2.0), factor)),
                    (("i1", "j2"), Const(5.0)),  # unconditional
                ],
            }
        )
        result = extract_gradient_conditions(gradient)
        assert "x" not in result

    def test_zero_entries_skipped(self):
        """Zero gradient entries are skipped (don't break common condition)."""
        cond = ParamRef("xw", ("i", "j"))
        factor = DollarConditional(Const(1.0), cond)
        gradient = _make_gradient(
            {
                "x": [
                    (("i1", "j1"), Binary("*", Const(2.0), factor)),
                    (("i1", "j2"), Const(0.0)),  # zero — skipped
                    (("i2", "j1"), Binary("*", Const(3.0), factor)),
                ],
            }
        )
        result = extract_gradient_conditions(gradient)
        assert "x" in result

    def test_different_conditions_no_common(self):
        """When entries have different conditions, no common condition."""
        cond1 = ParamRef("xw", ("i", "j"))
        cond2 = ParamRef("tw", ("i",))
        factor1 = DollarConditional(Const(1.0), cond1)
        factor2 = DollarConditional(Const(1.0), cond2)
        gradient = _make_gradient(
            {
                "x": [
                    (("i1", "j1"), Binary("*", Const(2.0), factor1)),
                    (("i1", "j2"), Binary("*", Const(3.0), factor2)),
                ],
            }
        )
        result = extract_gradient_conditions(gradient)
        assert "x" not in result

    def test_multiple_variables(self):
        """Conditions extracted independently per variable."""
        cond_x = ParamRef("xw", ("i", "j"))
        cond_t = ParamRef("tw", ("i",))
        factor_x = DollarConditional(Const(1.0), cond_x)
        factor_t = DollarConditional(Const(1.0), cond_t)
        gradient = _make_gradient(
            {
                "x": [
                    (("i1", "j1"), Binary("*", Const(2.0), factor_x)),
                ],
                "t": [
                    (("i1",), Binary("*", Const(3.0), factor_t)),
                ],
                "y": [
                    (("i1",), Const(1.0)),  # unconditional
                ],
            }
        )
        result = extract_gradient_conditions(gradient)
        assert "x" in result
        assert "t" in result
        assert "y" not in result
