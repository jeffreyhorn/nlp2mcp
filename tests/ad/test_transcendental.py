"""
Tests for transcendental and power function differentiation.

Day 3: Tests for power, exp, log, sqrt derivatives.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, VarRef

# ============================================================================
# Power Function Tests
# ============================================================================


class TestPowerDifferentiation:
    """Tests for power(base, exponent) differentiation."""

    def test_power_constant_exponent(self):
        """Test d(x^2)/dx = 2*x^1"""
        # power(x, 2)
        expr = Call("power", (VarRef("x"), Const(2.0)))
        result = differentiate_expr(expr, "x")

        # Should be: 2 * x^1 * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left side should be: 2 * x^1
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 2.0
        assert isinstance(result.left.right, Call)
        assert result.left.right.func == "power"

        # Right side should be: dx/dx = 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_power_constant_base(self):
        """Test d(2^x)/dx = 2^x * ln(2) * 1"""
        # power(2, x)
        expr = Call("power", (Const(2.0), VarRef("x")))
        result = differentiate_expr(expr, "x")

        # Should use general formula: a^b * (b/a * da/dx + ln(a) * db/dx)
        # With a=2 (constant), b=x: 2^x * (x/2 * 0 + ln(2) * 1) = 2^x * ln(2)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_power_both_variables(self):
        """Test d(x^y)/dx uses general formula"""
        # power(x, y)
        expr = Call("power", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "x")

        # Should use general formula: x^y * (y/x * 1 + ln(x) * 0)
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be x^y
        assert isinstance(result.left, Call)
        assert result.left.func == "power"

    def test_power_negative_exponent(self):
        """Test d(x^-1)/dx = -1 * x^-2"""
        # power(x, -1)
        expr = Call("power", (VarRef("x"), Const(-1.0)))
        result = differentiate_expr(expr, "x")

        # Should be: -1 * x^-2 * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_power_fractional_exponent(self):
        """Test d(x^0.5)/dx = 0.5 * x^-0.5"""
        # power(x, 0.5)
        expr = Call("power", (VarRef("x"), Const(0.5)))
        result = differentiate_expr(expr, "x")

        # Should be: 0.5 * x^-0.5 * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        left = result.left
        assert isinstance(left, Binary)
        assert left.op == "*"
        assert isinstance(left.left, Const)
        assert left.left.value == 0.5

    def test_power_chain_rule(self):
        """Test d(power(x^2, 3))/dx uses chain rule"""
        # power(x^2, 3)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("power", (inner, Const(3.0)))
        result = differentiate_expr(expr, "x")

        # Should be: 3 * (x^2)^2 * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"


# ============================================================================
# Exponential Function Tests
# ============================================================================


class TestExpDifferentiation:
    """Tests for exp(x) differentiation."""

    def test_exp_variable(self):
        """Test d(exp(x))/dx = exp(x)"""
        # exp(x)
        expr = Call("exp", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: exp(x) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.left, Call)
        assert result.left.func == "exp"
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0

    def test_exp_constant(self):
        """Test d(exp(5))/dx = 0"""
        # exp(5)
        expr = Call("exp", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: exp(5) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_exp_different_variable(self):
        """Test d(exp(y))/dx = 0"""
        # exp(y)
        expr = Call("exp", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: exp(y) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_exp_chain_rule(self):
        """Test d(exp(x^2))/dx = exp(x^2) * 2x"""
        # exp(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("exp", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: exp(x^2) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be exp(x^2)
        assert isinstance(result.left, Call)
        assert result.left.func == "exp"


# ============================================================================
# Logarithm Function Tests
# ============================================================================


class TestLogDifferentiation:
    """Tests for log(x) differentiation."""

    def test_log_variable(self):
        """Test d(log(x))/dx = 1/x"""
        # log(x)
        expr = Call("log", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/x) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/x
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 1.0

    def test_log_constant(self):
        """Test d(log(5))/dx = 0"""
        # log(5)
        expr = Call("log", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/5) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log_different_variable(self):
        """Test d(log(y))/dx = 0"""
        # log(y)
        expr = Call("log", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/y) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log_chain_rule(self):
        """Test d(log(x^2))/dx = (1/(x^2)) * 2x"""
        # log(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("log", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(x^2)) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(x^2)
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"


# ============================================================================
# Square Root Function Tests
# ============================================================================


class TestSqrtDifferentiation:
    """Tests for sqrt(x) differentiation."""

    def test_sqrt_variable(self):
        """Test d(sqrt(x))/dx = 1/(2*sqrt(x))"""
        # sqrt(x)
        expr = Call("sqrt", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(2*sqrt(x))) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(2*sqrt(x))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"

        # Denominator should be 2*sqrt(x)
        denominator = result.left.right
        assert isinstance(denominator, Binary)
        assert denominator.op == "*"
        assert isinstance(denominator.left, Const)
        assert denominator.left.value == 2.0
        assert isinstance(denominator.right, Call)
        assert denominator.right.func == "sqrt"

    def test_sqrt_constant(self):
        """Test d(sqrt(5))/dx = 0"""
        # sqrt(5)
        expr = Call("sqrt", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(2*sqrt(5))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_sqrt_different_variable(self):
        """Test d(sqrt(y))/dx = 0"""
        # sqrt(y)
        expr = Call("sqrt", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(2*sqrt(y))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_sqrt_chain_rule(self):
        """Test d(sqrt(x^2))/dx = (1/(2*sqrt(x^2))) * 2x"""
        # sqrt(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("sqrt", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(2*sqrt(x^2))) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(2*sqrt(x^2))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestTranscendentalErrors:
    """Tests for error handling in transcendental functions."""

    def test_power_wrong_arg_count(self):
        """Test power() with wrong number of arguments raises error"""
        # power(x) - missing exponent
        expr = Call("power", (VarRef("x"),))
        with pytest.raises(ValueError, match="power\\(\\) expects 2 arguments"):
            differentiate_expr(expr, "x")

    def test_exp_wrong_arg_count(self):
        """Test exp() with wrong number of arguments raises error"""
        # exp(x, y) - too many args
        expr = Call("exp", (VarRef("x"), VarRef("y")))
        with pytest.raises(ValueError, match="exp\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")

    def test_log_wrong_arg_count(self):
        """Test log() with wrong number of arguments raises error"""
        # log() - no args
        expr = Call("log", ())
        with pytest.raises(ValueError, match="log\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")

    def test_sqrt_wrong_arg_count(self):
        """Test sqrt() with wrong number of arguments raises error"""
        # sqrt(x, y) - too many args
        expr = Call("sqrt", (VarRef("x"), VarRef("y")))
        with pytest.raises(ValueError, match="sqrt\\(\\) expects 1 argument"):
            differentiate_expr(expr, "x")

    def test_unsupported_function(self):
        """Test unsupported function raises clear error"""
        # asin(x) - not yet implemented
        expr = Call("asin", (VarRef("x"),))
        with pytest.raises(
            ValueError, match="Differentiation not yet implemented for function 'asin'"
        ):
            differentiate_expr(expr, "x")
