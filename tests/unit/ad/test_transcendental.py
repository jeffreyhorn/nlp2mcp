"""
Tests for transcendental and power function differentiation.

Day 3: Tests for power, exp, log, sqrt derivatives.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, VarRef

pytestmark = pytest.mark.unit

# ============================================================================
# Power Function Tests
# ============================================================================


@pytest.mark.unit
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

        # Left should be x^y (Binary("**", ...) for variable exponents)
        assert isinstance(result.left, Binary)
        assert result.left.op == "**"

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


@pytest.mark.unit
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


@pytest.mark.unit
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
# Base-10 Logarithm Function Tests
# ============================================================================


@pytest.mark.unit
class TestLog10Differentiation:
    """Tests for log10(x) differentiation."""

    def test_log10_variable(self):
        """Test d(log10(x))/dx = 1/(x * ln(10))"""
        # log10(x)
        expr = Call("log10", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(x * ln(10))) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(x * ln(10))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 1.0

        # Denominator should be x * ln(10)
        assert isinstance(result.left.right, Binary)
        assert result.left.right.op == "*"

    def test_log10_constant(self):
        """Test d(log10(5))/dx = 0"""
        # log10(5)
        expr = Call("log10", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(5 * ln(10))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log10_different_variable(self):
        """Test d(log10(y))/dx = 0"""
        # log10(y)
        expr = Call("log10", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(y * ln(10))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log10_chain_rule(self):
        """Test d(log10(x^2))/dx = (1/(x^2 * ln(10))) * 2x"""
        # log10(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("log10", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(x^2 * ln(10))) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(x^2 * ln(10))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"


# ============================================================================
# Base-2 Logarithm Function Tests
# ============================================================================


@pytest.mark.unit
class TestLog2Differentiation:
    """Tests for log2(x) differentiation."""

    def test_log2_variable(self):
        """Test d(log2(x))/dx = 1/(x * ln(2))"""
        # log2(x)
        expr = Call("log2", (VarRef("x"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(x * ln(2))) * 1
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(x * ln(2))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 1.0

        # Denominator should be x * ln(2)
        assert isinstance(result.left.right, Binary)
        assert result.left.right.op == "*"

    def test_log2_constant(self):
        """Test d(log2(5))/dx = 0"""
        # log2(5)
        expr = Call("log2", (Const(5.0),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(5 * ln(2))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log2_different_variable(self):
        """Test d(log2(y))/dx = 0"""
        # log2(y)
        expr = Call("log2", (VarRef("y"),))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(y * ln(2))) * 0
        assert isinstance(result, Binary)
        assert result.op == "*"

        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_log2_chain_rule(self):
        """Test d(log2(x^2))/dx = (1/(x^2 * ln(2))) * 2x"""
        # log2(x^2)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("log2", (inner,))
        result = differentiate_expr(expr, "x")

        # Should be: (1/(x^2 * ln(2))) * d(x^2)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be 1/(x^2 * ln(2))
        assert isinstance(result.left, Binary)
        assert result.left.op == "/"


# ============================================================================
# Square Root Function Tests
# ============================================================================


@pytest.mark.unit
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
# Gamma Function Tests
# ============================================================================


@pytest.mark.unit
class TestGammaDifferentiation:
    """Tests for gamma(x) differentiation.

    The gamma function derivative requires the psi (digamma) function:
    d(gamma(x))/dx = gamma(x) * psi(x)

    However, GAMS does not have a psi/digamma function, so we cannot
    emit valid GAMS code. Differentiation of gamma() should raise an error.
    """

    def test_gamma_raises_error(self):
        """Test that differentiating gamma(x) raises an error."""
        expr = Call("gamma", (VarRef("x"),))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")

    def test_gamma_constant_raises_error(self):
        """Test that differentiating gamma(constant) also raises an error.

        Even though d/dx[gamma(5)] = 0 mathematically, we still raise
        an error because we want to fail fast and clearly communicate
        that gamma models cannot be converted.
        """
        expr = Call("gamma", (Const(5.0),))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")

    def test_gamma_chain_rule_raises_error(self):
        """Test that differentiating gamma(expr) raises an error."""
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("gamma", (inner,))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")


# ============================================================================
# LogGamma Function Tests
# ============================================================================


@pytest.mark.unit
class TestLogGammaDifferentiation:
    """Tests for loggamma(x) differentiation.

    The loggamma function is ln(gamma(x)), and its derivative is the psi function:
    d(loggamma(x))/dx = psi(x)

    However, GAMS does not have a psi/digamma function, so we cannot
    emit valid GAMS code. Differentiation of loggamma() should raise an error.
    """

    def test_loggamma_raises_error(self):
        """Test that differentiating loggamma(x) raises an error."""
        expr = Call("loggamma", (VarRef("x"),))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")

    def test_loggamma_constant_raises_error(self):
        """Test that differentiating loggamma(constant) also raises an error."""
        expr = Call("loggamma", (Const(5.0),))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")

    def test_loggamma_chain_rule_raises_error(self):
        """Test that differentiating loggamma(expr) raises an error."""
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("loggamma", (inner,))
        with pytest.raises(ValueError, match="digamma/psi function"):
            differentiate_expr(expr, "x")


# ============================================================================
# Smooth Min/Max Function Tests
# ============================================================================


@pytest.mark.unit
class TestSminDifferentiation:
    """Tests for smin(a, b) differentiation.

    The smin function uses a smooth LogSumExp approximation:
    smin(a, b) ≈ -τ · ln(exp(-a/τ) + exp(-b/τ))

    Derivatives:
    ∂/∂a smin ≈ exp(-a/τ) / (exp(-a/τ) + exp(-b/τ))
    ∂/∂b smin ≈ exp(-b/τ) / (exp(-a/τ) + exp(-b/τ))
    """

    def test_smin_first_variable(self):
        """Test d(smin(x, y))/dx has correct structure"""
        # smin(x, y)
        expr = Call("smin", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "x")

        # Result should be: dsmin_da * 1 + dsmin_db * 0 = dsmin_da
        # Structure: (exp(-x/τ) / (exp(-x/τ) + exp(-y/τ))) * 1 + (...) * 0
        assert isinstance(result, Binary)
        assert result.op == "+"  # Sum of two terms

    def test_smin_second_variable(self):
        """Test d(smin(x, y))/dy has correct structure"""
        # smin(x, y)
        expr = Call("smin", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "y")

        # Result should be: dsmin_da * 0 + dsmin_db * 1 = dsmin_db
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smin_both_same_variable(self):
        """Test d(smin(x, x))/dx has correct structure"""
        # smin(x, x)
        expr = Call("smin", (VarRef("x"), VarRef("x")))
        result = differentiate_expr(expr, "x")

        # Both partial derivatives contribute
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smin_constants(self):
        """Test d(smin(2, 3))/dx = 0"""
        # smin(2, 3)
        expr = Call("smin", (Const(2.0), Const(3.0)))
        result = differentiate_expr(expr, "x")

        # Both da/dx and db/dx are 0
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smin_different_variable(self):
        """Test d(smin(x, y))/dz = 0"""
        # smin(x, y)
        expr = Call("smin", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "z")

        # Both partial derivatives contribute 0
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smin_chain_rule(self):
        """Test d(smin(x^2, y))/dx uses chain rule"""
        # smin(x^2, y)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("smin", (inner, VarRef("y")))
        result = differentiate_expr(expr, "x")

        # Chain rule: dsmin_da * d(x^2)/dx + dsmin_db * 0
        assert isinstance(result, Binary)
        assert result.op == "+"


@pytest.mark.unit
class TestSmaxDifferentiation:
    """Tests for smax(a, b) differentiation.

    The smax function uses a smooth LogSumExp approximation:
    smax(a, b) ≈ τ · ln(exp(a/τ) + exp(b/τ))

    Derivatives:
    ∂/∂a smax ≈ exp(a/τ) / (exp(a/τ) + exp(b/τ))
    ∂/∂b smax ≈ exp(b/τ) / (exp(a/τ) + exp(b/τ))
    """

    def test_smax_first_variable(self):
        """Test d(smax(x, y))/dx has correct structure"""
        # smax(x, y)
        expr = Call("smax", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "x")

        # Result should be: dsmax_da * 1 + dsmax_db * 0
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smax_second_variable(self):
        """Test d(smax(x, y))/dy has correct structure"""
        # smax(x, y)
        expr = Call("smax", (VarRef("x"), VarRef("y")))
        result = differentiate_expr(expr, "y")

        # Result should be: dsmax_da * 0 + dsmax_db * 1
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smax_constants(self):
        """Test d(smax(2, 3))/dx = 0"""
        # smax(2, 3)
        expr = Call("smax", (Const(2.0), Const(3.0)))
        result = differentiate_expr(expr, "x")

        # Both da/dx and db/dx are 0
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_smax_chain_rule(self):
        """Test d(smax(x^2, y))/dx uses chain rule"""
        # smax(x^2, y)
        inner = Call("power", (VarRef("x"), Const(2.0)))
        expr = Call("smax", (inner, VarRef("y")))
        result = differentiate_expr(expr, "x")

        # Chain rule: dsmax_da * d(x^2)/dx + dsmax_db * 0
        assert isinstance(result, Binary)
        assert result.op == "+"


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.unit
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

    def test_gamma_wrong_arg_count(self):
        """Test gamma() with wrong number of arguments raises error"""
        # gamma(x, y) - too many args
        expr = Call("gamma", (VarRef("x"), VarRef("y")))
        with pytest.raises(ValueError, match="gamma\\(\\) expects 1 argument, got 2"):
            differentiate_expr(expr, "x")

    def test_loggamma_wrong_arg_count(self):
        """Test loggamma() with wrong number of arguments raises error"""
        # loggamma() - no args
        expr = Call("loggamma", ())
        with pytest.raises(ValueError, match="loggamma\\(\\) expects 1 argument, got 0"):
            differentiate_expr(expr, "x")

    def test_smin_wrong_arg_count(self):
        """Test smin() with wrong number of arguments raises error"""
        # smin(x) - only 1 arg
        expr = Call("smin", (VarRef("x"),))
        with pytest.raises(ValueError, match="smin\\(\\) expects 2 arguments"):
            differentiate_expr(expr, "x")

    def test_smax_wrong_arg_count(self):
        """Test smax() with wrong number of arguments raises error"""
        # smax(x, y, z) - too many args
        expr = Call("smax", (VarRef("x"), VarRef("y"), VarRef("z")))
        with pytest.raises(ValueError, match="smax\\(\\) expects 2 arguments"):
            differentiate_expr(expr, "x")

    def test_unsupported_function(self):
        """Test unsupported function raises clear error"""
        # asin(x) - not yet implemented
        expr = Call("asin", (VarRef("x"),))
        with pytest.raises(
            ValueError, match="Differentiation not yet implemented for function 'asin'"
        ):
            differentiate_expr(expr, "x")
