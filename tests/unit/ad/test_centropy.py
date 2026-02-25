"""Tests for centropy() cross-entropy function differentiation (Issue #869)."""

import math

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ad.evaluator import evaluate
from src.ir.ast import Binary, Call, Const, VarRef

pytestmark = pytest.mark.unit


class TestCentropyDifferentiation:
    """Tests for centropy(x, y) = x * ln(x/y) differentiation."""

    def test_centropy_wrt_first_arg(self):
        """d/dx centropy(x, y) = ln(x/y) + 1 when y is constant."""
        expr = Call("centropy", (VarRef("x"), Const(2.0)))
        result = differentiate_expr(expr, "x")

        # Should be (ln(x/2) + 1) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_centropy_wrt_second_arg(self):
        """d/dy centropy(x, y) = -x/y when x is constant."""
        expr = Call("centropy", (Const(3.0), VarRef("y")))
        result = differentiate_expr(expr, "y")

        # Should be (-3/y) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_centropy_wrt_unrelated_var(self):
        """centropy(a, b) has zero derivative w.r.t. unrelated variable z."""
        expr = Call("centropy", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "z")
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_centropy_both_args_depend(self):
        """When both args depend on wrt variable, both terms contribute."""
        # centropy(x, x) = x * ln(1) = 0, d/dx = ln(1) + 1 + (-x/x) = 0 + 1 - 1 = 0
        expr = Call("centropy", (VarRef("x"), VarRef("x")))
        result = differentiate_expr(expr, "x")

        # Both x and y depend on x, so should get sum of two terms
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_centropy_numerical_wrt_x(self):
        """Numerical check: d/dx centropy(x, 2) at x=4 should be ln(4/2) + 1 = ln(2) + 1."""
        expr = Call("centropy", (VarRef("x"), Const(2.0)))
        result = differentiate_expr(expr, "x")

        val = evaluate(result, var_values={("x", ()): 4.0})
        expected = math.log(4.0 / 2.0) + 1.0  # ln(2) + 1 ≈ 1.693
        assert abs(val - expected) < 1e-10

    def test_centropy_numerical_wrt_y(self):
        """Numerical check: d/dy centropy(3, y) at y=2 should be -3/2 = -1.5."""
        expr = Call("centropy", (Const(3.0), VarRef("y")))
        result = differentiate_expr(expr, "y")

        val = evaluate(result, var_values={("y", ()): 2.0})
        expected = -3.0 / 2.0  # -1.5
        assert abs(val - expected) < 1e-10

    def test_centropy_numerical_both_depend(self):
        """Numerical check: d/dx centropy(x, x) = ln(x/x)+1 + (-x/x) = 0."""
        expr = Call("centropy", (VarRef("x"), VarRef("x")))
        result = differentiate_expr(expr, "x")

        val = evaluate(result, var_values={("x", ()): 5.0})
        assert abs(val - 0.0) < 1e-10

    def test_centropy_wrong_arity(self):
        """centropy with wrong number of args should raise ValueError."""
        with pytest.raises(ValueError, match="centropy.*expects 2 arguments"):
            expr = Call("centropy", (VarRef("x"),))
            differentiate_expr(expr, "x")

    def test_centropy_chain_rule(self):
        """d/dx centropy(x^2, y) applies chain rule to first arg."""
        # centropy(x^2, y): d/dx = (ln(x^2/y) + 1) * 2x
        x_sq = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("centropy", (x_sq, Const(1.0)))
        result = differentiate_expr(expr, "x")

        # At x=2: d/dx = (ln(4/1) + 1) * 2*2 = (ln(4) + 1) * 4
        val = evaluate(result, var_values={("x", ()): 2.0})
        expected = (math.log(4.0) + 1.0) * 4.0
        assert abs(val - expected) < 1e-10
