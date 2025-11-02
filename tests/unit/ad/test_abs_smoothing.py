"""
Tests for abs() smoothing with --smooth-abs flag.

Day 5: Tests for abs() smooth approximation using sqrt(x^2 + epsilon).
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.config import Config
from src.ir.ast import Binary, Call, Const, VarRef

pytestmark = pytest.mark.unit


class TestAbsSmoothing:
    """Tests for abs() smooth approximation."""

    def test_abs_with_smoothing_enabled(self):
        """Test abs(x) with smoothing returns derivative"""
        # abs(x) with smoothing enabled
        expr = Call("abs", (VarRef("x"),))
        config = Config(smooth_abs=True, smooth_abs_epsilon=1e-6)

        # Should not raise error
        derivative = differentiate_expr(expr, "x", config=config)

        # Derivative should be: x / sqrt(x^2 + epsilon)
        assert derivative is not None
        assert isinstance(derivative, Binary)
        assert derivative.op == "*"

    def test_abs_without_smoothing_raises_error(self):
        """Test abs(x) without smoothing raises error"""
        expr = Call("abs", (VarRef("x"),))
        config = Config(smooth_abs=False)

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x", config=config)

        error_msg = str(exc_info.value)
        assert "not differentiable" in error_msg
        assert "--smooth-abs" in error_msg

    def test_abs_with_none_config_raises_error(self):
        """Test abs(x) with None config raises error"""
        expr = Call("abs", (VarRef("x"),))

        with pytest.raises(ValueError) as exc_info:
            differentiate_expr(expr, "x", config=None)

        error_msg = str(exc_info.value)
        assert "not differentiable" in error_msg

    def test_abs_derivative_structure(self):
        """Test abs() derivative has correct structure: x / sqrt(x^2 + epsilon)"""
        expr = Call("abs", (VarRef("x"),))
        config = Config(smooth_abs=True, smooth_abs_epsilon=1e-6)

        derivative = differentiate_expr(expr, "x", config=config)

        # Should be: (x / sqrt(x^2 + epsilon)) * 1
        assert isinstance(derivative, Binary)
        assert derivative.op == "*"

        # First part: x / sqrt(x^2 + epsilon)
        division = derivative.left
        assert isinstance(division, Binary)
        assert division.op == "/"

        # Numerator: x
        assert isinstance(division.left, VarRef)
        assert division.left.name == "x"

        # Denominator: sqrt(x^2 + epsilon)
        sqrt_call = division.right
        assert isinstance(sqrt_call, Call)
        assert sqrt_call.func == "sqrt"

        # Inside sqrt: x^2 + epsilon
        inner = sqrt_call.args[0]
        assert isinstance(inner, Binary)
        assert inner.op == "+"

        # epsilon should be on the right
        epsilon = inner.right
        assert isinstance(epsilon, Const)
        assert epsilon.value == 1e-6

    def test_abs_custom_epsilon(self):
        """Test abs() with custom epsilon value"""
        expr = Call("abs", (VarRef("x"),))
        config = Config(smooth_abs=True, smooth_abs_epsilon=1e-4)

        derivative = differentiate_expr(expr, "x", config=config)

        # Extract epsilon from derivative structure
        division = derivative.left
        sqrt_call = division.right
        inner = sqrt_call.args[0]
        epsilon = inner.right

        assert isinstance(epsilon, Const)
        assert epsilon.value == 1e-4

    def test_abs_composite_expression(self):
        """Test abs(x^2) with smoothing"""
        # abs(x^2)
        inner = Binary("^", VarRef("x"), Const(2.0))
        expr = Call("abs", (inner,))
        config = Config(smooth_abs=True, smooth_abs_epsilon=1e-6)

        # Should apply chain rule
        derivative = differentiate_expr(expr, "x", config=config)

        assert derivative is not None
        # Should involve derivative of inner expression (2x) times derivative of abs

    def test_abs_different_variable(self):
        """Test abs(y) w.r.t. x with smoothing gives zero"""
        expr = Call("abs", (VarRef("y"),))
        config = Config(smooth_abs=True, smooth_abs_epsilon=1e-6)

        derivative = differentiate_expr(expr, "x", config=config)

        # Since y doesn't depend on x, derivative should simplify to 0
        # The derivative will be (y / sqrt(y^2 + eps)) * 0
        assert isinstance(derivative, Binary)
        assert derivative.op == "*"
        # The second operand should be 0 (derivative of y w.r.t. x)
        assert isinstance(derivative.right, Const)
        assert derivative.right.value == 0.0

    def test_epsilon_validation(self):
        """Test that negative epsilon raises error"""
        with pytest.raises(ValueError) as exc_info:
            Config(smooth_abs=True, smooth_abs_epsilon=-1e-6)

        error_msg = str(exc_info.value)
        assert "must be positive" in error_msg
