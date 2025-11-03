"""Tests for power simplification rules."""

import pytest

from src.ad.ad_core import simplify_advanced
from src.ad.term_collection import simplify_power_rules
from src.ir.ast import Binary, Const, VarRef


class TestPowerMultiplication:
    """Test x^a * x^b → x^(a+b) simplification."""

    def test_power_times_power_same_base(self):
        """Test x^2 * x^3 → x^5."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(3))
        )
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(5))

    def test_variable_times_power(self):
        """Test x * x^2 → x^3."""
        expr = Binary("*", VarRef("x", ()), Binary("**", VarRef("x", ()), Const(2)))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(3))

    def test_power_times_variable(self):
        """Test x^2 * x → x^3."""
        expr = Binary("*", Binary("**", VarRef("x", ()), Const(2)), VarRef("x", ()))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(3))

    def test_variable_times_variable(self):
        """Test x * x → x^2."""
        expr = Binary("*", VarRef("x", ()), VarRef("x", ()))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(2))

    def test_cancel_to_one(self):
        """Test x^2 * x^(-2) → 1."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(-2))
        )
        result = simplify_power_rules(expr)
        assert result == Const(1)

    def test_simplify_to_base(self):
        """Test x^2 * x^(-1) → x."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(-1))
        )
        result = simplify_power_rules(expr)
        assert result == VarRef("x", ())

    def test_different_bases_no_simplification(self):
        """Test x^2 * y^3 stays unchanged."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("y", ()), Const(3))
        )
        result = simplify_power_rules(expr)
        assert result == expr

    def test_fractional_exponents(self):
        """Test x^0.5 * x^0.5 → x^1 → x."""
        expr = Binary(
            "*",
            Binary("**", VarRef("x", ()), Const(0.5)),
            Binary("**", VarRef("x", ()), Const(0.5)),
        )
        result = simplify_power_rules(expr)
        assert result == VarRef("x", ())

    def test_negative_exponents(self):
        """Test x^(-2) * x^(-3) → x^(-5)."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(-2)), Binary("**", VarRef("x", ()), Const(-3))
        )
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(-5))

    def test_indexed_variable(self):
        """Test x(i)^2 * x(i)^3 → x(i)^5."""
        expr = Binary(
            "*",
            Binary("**", VarRef("x", ("i",)), Const(2)),
            Binary("**", VarRef("x", ("i",)), Const(3)),
        )
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ("i",)), Const(5))


class TestPowerDivision:
    """Test x^a / x^b → x^(a-b) simplification."""

    def test_power_divide_power_same_base(self):
        """Test x^5 / x^2 → x^3."""
        expr = Binary(
            "/", Binary("**", VarRef("x", ()), Const(5)), Binary("**", VarRef("x", ()), Const(2))
        )
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(3))

    def test_power_divide_variable(self):
        """Test x^3 / x → x^2."""
        expr = Binary("/", Binary("**", VarRef("x", ()), Const(3)), VarRef("x", ()))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(2))

    def test_variable_divide_power(self):
        """Test x / x^2 → 1/x^1."""
        expr = Binary("/", VarRef("x", ()), Binary("**", VarRef("x", ()), Const(2)))
        result = simplify_power_rules(expr)
        # x / x^2 = x^(1-2) = x^(-1) = 1/x^1 (basic simplify would reduce x^1 to x)
        assert result == Binary("/", Const(1), Binary("**", VarRef("x", ()), Const(1)))

    def test_variable_divide_variable(self):
        """Test x / x → 1."""
        expr = Binary("/", VarRef("x", ()), VarRef("x", ()))
        result = simplify_power_rules(expr)
        assert result == Const(1)

    def test_equal_powers_cancel(self):
        """Test x^3 / x^3 → 1."""
        expr = Binary(
            "/", Binary("**", VarRef("x", ()), Const(3)), Binary("**", VarRef("x", ()), Const(3))
        )
        result = simplify_power_rules(expr)
        assert result == Const(1)

    def test_simplify_to_base(self):
        """Test x^2 / x → x."""
        expr = Binary("/", Binary("**", VarRef("x", ()), Const(2)), VarRef("x", ()))
        result = simplify_power_rules(expr)
        assert result == VarRef("x", ())

    def test_negative_result_exponent(self):
        """Test x^2 / x^5 → 1/x^3."""
        expr = Binary(
            "/", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(5))
        )
        result = simplify_power_rules(expr)
        # x^2 / x^5 = x^(2-5) = x^(-3) = 1/x^3
        assert result == Binary("/", Const(1), Binary("**", VarRef("x", ()), Const(3)))

    def test_different_bases_no_simplification(self):
        """Test x^2 / y^3 stays unchanged."""
        expr = Binary(
            "/", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("y", ()), Const(3))
        )
        result = simplify_power_rules(expr)
        assert result == expr


class TestNestedPowers:
    """Test (x^a)^b → x^(a*b) simplification."""

    def test_nested_powers(self):
        """Test (x^2)^3 → x^6."""
        expr = Binary("**", Binary("**", VarRef("x", ()), Const(2)), Const(3))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(6))

    def test_nested_fractional_powers(self):
        """Test (x^0.5)^2 → x^1 → x."""
        expr = Binary("**", Binary("**", VarRef("x", ()), Const(0.5)), Const(2))
        result = simplify_power_rules(expr)
        # Result should be x^1, which basic simplify will reduce to x
        assert result == Binary("**", VarRef("x", ()), Const(1))

    def test_nested_negative_powers(self):
        """Test (x^(-2))^3 → x^(-6)."""
        expr = Binary("**", Binary("**", VarRef("x", ()), Const(-2)), Const(3))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(-6))

    def test_nested_power_with_negative_outer(self):
        """Test (x^2)^(-1) → x^(-2)."""
        expr = Binary("**", Binary("**", VarRef("x", ()), Const(2)), Const(-1))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ()), Const(-2))

    def test_indexed_variable(self):
        """Test (x(i)^2)^3 → x(i)^6."""
        expr = Binary("**", Binary("**", VarRef("x", ("i",)), Const(2)), Const(3))
        result = simplify_power_rules(expr)
        assert result == Binary("**", VarRef("x", ("i",)), Const(6))


class TestPowerSimplificationIntegration:
    """Test power simplification integrated with simplify_advanced."""

    def test_multiplication_chain(self):
        """Test x * x * x simplifies correctly."""
        # Build: x * (x * x)
        inner = Binary("*", VarRef("x", ()), VarRef("x", ()))
        expr = Binary("*", VarRef("x", ()), inner)
        result = simplify_advanced(expr)
        # Should get x^3 through: x * (x*x) → x * x^2 → x^3
        assert result == Binary("**", VarRef("x", ()), Const(3))

    def test_power_with_constant_folding(self):
        """Test (x^2)^(1+1) → (x^2)^2 → x^4."""
        expr = Binary(
            "**", Binary("**", VarRef("x", ()), Const(2)), Binary("+", Const(1), Const(1))
        )
        result = simplify_advanced(expr)
        # (1+1) should fold to 2, then (x^2)^2 → x^4
        assert result == Binary("**", VarRef("x", ()), Const(4))

    def test_power_times_itself(self):
        """Test x^2 * x^2 → x^4."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(2))
        )
        result = simplify_advanced(expr)
        assert result == Binary("**", VarRef("x", ()), Const(4))

    def test_complex_power_division(self):
        """Test x^(2+3) / x^2 → x^5 / x^2 → x^3."""
        numerator = Binary("**", VarRef("x", ()), Binary("+", Const(2), Const(3)))
        denominator = Binary("**", VarRef("x", ()), Const(2))
        expr = Binary("/", numerator, denominator)
        result = simplify_advanced(expr)
        # (2+3) folds to 5, then x^5/x^2 → x^3
        assert result == Binary("**", VarRef("x", ()), Const(3))

    def test_power_with_term_collection(self):
        """Test (x+x)^2 simplifies to (2*x)^2."""
        inner_sum = Binary("+", VarRef("x", ()), VarRef("x", ()))
        expr = Binary("**", inner_sum, Const(2))
        result = simplify_advanced(expr)
        # x+x should collect to 2*x, giving (2*x)^2
        expected_base = Binary("*", Const(2), VarRef("x", ()))
        assert result == Binary("**", expected_base, Const(2))

    def test_division_with_multiplicative_cancel_and_power(self):
        """Test (2*x^3) / 2 / x → x^3 / x → x^2."""
        # (2*x^3) / 2
        numerator = Binary("*", Const(2), Binary("**", VarRef("x", ()), Const(3)))
        step1 = Binary("/", numerator, Const(2))
        # Then divide by x
        expr = Binary("/", step1, VarRef("x", ()))
        result = simplify_advanced(expr)
        # Should get x^2
        assert result == Binary("**", VarRef("x", ()), Const(2))

    def test_x_squared_times_x_cubed(self):
        """Test concrete example: x^2 * x^3 → x^5."""
        expr = Binary(
            "*", Binary("**", VarRef("x", ()), Const(2)), Binary("**", VarRef("x", ()), Const(3))
        )
        result = simplify_advanced(expr)
        assert result == Binary("**", VarRef("x", ()), Const(5))

    def test_derivative_like_pattern(self):
        """Test pattern common in derivatives: 2*x * x → (2*x)*x."""
        # (2*x) * x - this is a multiplication of (2*x) and x
        # Power rules only combine x^a * x^b, not (2*x) * x
        # The full simplification would need distributivity or more complex rules
        left = Binary("*", Const(2), VarRef("x", ()))
        expr = Binary("*", left, VarRef("x", ()))
        result = simplify_advanced(expr)
        # This won't fully simplify to 2*x^2 without distributive factoring
        # It will remain as (2*x)*x since power rules don't apply to this structure
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Just verify it's still a multiplication involving 2*x and x
        assert result.left == Binary("*", Const(2), VarRef("x", ()))
        assert result.right == VarRef("x", ())
