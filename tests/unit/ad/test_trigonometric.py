"""
Tests for trigonometric function differentiation.

Day 4: Tests for sin, cos, tan derivatives.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, Unary, VarRef


pytestmark = pytest.mark.unit

# ============================================================================
# Sine Function Tests
# ============================================================================


@pytest.mark.unit
class TestSinDifferentiation:
    """Tests for sin(x) differentiation."""

    def test_sin_variable(self):
        """Test d(sin(x))/dx = cos(x)"""
        # sin(x)
        expr = Call("sin", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: cos(x) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be cos(x)
        assert isinstance(result.left, Call)
        assert result.left.func == "cos"
        assert isinstance(result.left.args[0], VarRef)
        assert result.left.args[0].name == "x"

        # Right should be 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_sin_constant(self):
        """Test d(sin(5))/dx = 0"""
        # sin(5)
        expr = Call("sin", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: cos(5) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_sin_different_variable(self):
        """Test d(sin(y))/dx = 0"""
        # sin(y)
        expr = Call("sin", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: cos(y) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_sin_chain_rule(self):
        """Test d(sin(x^2))/dx = cos(x^2) * 2x"""
        # sin(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("sin", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: cos(x^2) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be cos(x^2)
        assert isinstance(result.left, Call)
        assert result.left.func == "cos"


# ============================================================================
# Cosine Function Tests
# ============================================================================


@pytest.mark.unit
class TestCosDifferentiation:
    """Tests for cos(x) differentiation."""

    def test_cos_variable(self):
        """Test d(cos(x))/dx = -sin(x)"""
        # cos(x)
        expr = Call("cos", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: -sin(x) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be -sin(x)
        assert isinstance(result.left, Unary)
        assert result.left.op == "-"
        assert isinstance(result.left.child, Call)
        assert result.left.child.func == "sin"

        # Right should be 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_cos_constant(self):
        """Test d(cos(5))/dx = 0"""
        # cos(5)
        expr = Call("cos", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: -sin(5) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_cos_different_variable(self):
        """Test d(cos(y))/dx = 0"""
        # cos(y)
        expr = Call("cos", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: -sin(y) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_cos_chain_rule(self):
        """Test d(cos(exp(x)))/dx = -sin(exp(x)) * exp(x)"""
        # cos(exp(x))
        inner = Call("exp", (VarRef("x"),))
        expr = Call("cos", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: -sin(exp(x)) * d(exp(x))/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be -sin(exp(x))
        assert isinstance(result.left, Unary)
        assert result.left.op == "-"
        assert isinstance(result.left.child, Call)
        assert result.left.child.func == "sin"


# ============================================================================
# Tangent Function Tests
# ============================================================================


@pytest.mark.unit
class TestTanDifferentiation:
    """Tests for tan(x) differentiation."""

    def test_tan_variable(self):
        """Test d(tan(x))/dx = 1/cos²(x)"""
        # tan(x)
        expr = Call("tan", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/cos²(x)) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/cos²(x)
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"

        # Numerator should be 1
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 1.0

        # Denominator should be cos²(x) = cos(x) * cos(x)
        assert isinstance(result.left.right, Binary)
        assert result.left.right.op == "*"

        # Right should be 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_tan_constant(self):
        """Test d(tan(5))/dx = 0"""
        # tan(5)
        expr = Call("tan", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/cos²(5)) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_tan_different_variable(self):
        """Test d(tan(y))/dx = 0"""
        # tan(y)
        expr = Call("tan", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/cos²(y)) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Right should be 0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_tan_chain_rule(self):
        """Test d(tan(x^2))/dx = (1/cos²(x^2)) * 2x"""
        # tan(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("tan", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: (1/cos²(x^2)) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/cos²(x^2)
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
class TestTrigonometricErrors:
    """Tests for error handling in trigonometric functions."""

    def test_sin_wrong_arg_count(self):
        """Test sin() with wrong number of arguments raises error"""
        # sin(x, y) - too many args
        expr = Call("sin", (VarRef("x"), VarRef("y")))
        with pytest.raises(ValueError, match="sin\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")

    def test_cos_wrong_arg_count(self):
        """Test cos() with wrong number of arguments raises error"""
        # cos() - no args
        expr = Call("cos", ())
        with pytest.raises(ValueError, match="cos\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")

    def test_tan_wrong_arg_count(self):
        """Test tan() with wrong number of arguments raises error"""
        # tan(x, y, z) - too many args
        expr = Call("tan", (VarRef("x"), VarRef("y"), VarRef("z")))
        with pytest.raises(ValueError, match="tan\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")
