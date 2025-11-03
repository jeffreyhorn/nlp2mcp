"""Tests for multiplicative cancellation simplification."""

import pytest

from src.ad.ad_core import simplify_advanced
from src.ad.term_collection import simplify_multiplicative_cancellation
from src.ir.ast import Binary, Const, VarRef


class TestMultiplicativeCancellation:
    """Test multiplicative cancellation: (c * x) / c → x."""

    def test_left_constant_cancels(self):
        """Test (c * x) / c → x when constant is on the left."""
        # 2 * x / 2 → x
        expr = Binary("/", Binary("*", Const(2), VarRef("x", ())), Const(2))
        result = simplify_multiplicative_cancellation(expr)
        assert result == VarRef("x", ())

    def test_right_constant_cancels(self):
        """Test (x * c) / c → x when constant is on the right."""
        # x * 3 / 3 → x
        expr = Binary("/", Binary("*", VarRef("x", ()), Const(3)), Const(3))
        result = simplify_multiplicative_cancellation(expr)
        assert result == VarRef("x", ())

    def test_different_constants_no_cancellation(self):
        """Test that different constants don't cancel."""
        # 2 * x / 3 → stays the same
        expr = Binary("/", Binary("*", Const(2), VarRef("x", ())), Const(3))
        result = simplify_multiplicative_cancellation(expr)
        assert result == expr

    def test_zero_denominator_no_cancellation(self):
        """Test that division by zero is not simplified."""
        # 0 * x / 0 → stays the same (don't simplify division by zero)
        expr = Binary("/", Binary("*", Const(0), VarRef("x", ())), Const(0))
        result = simplify_multiplicative_cancellation(expr)
        assert result == expr

    def test_complex_expression_cancels(self):
        """Test cancellation with complex expressions."""
        # 5 * (x + y) / 5 → x + y
        expr = Binary(
            "/",
            Binary("*", Const(5), Binary("+", VarRef("x", ()), VarRef("y", ()))),
            Const(5),
        )
        result = simplify_multiplicative_cancellation(expr)
        assert result == Binary("+", VarRef("x", ()), VarRef("y", ()))

    def test_nested_multiplication_left(self):
        """Test cancellation with nested multiplication."""
        # (2 * 3) * x / 2 → doesn't cancel (need to flatten first)
        expr = Binary("/", Binary("*", Binary("*", Const(2), Const(3)), VarRef("x", ())), Const(2))
        result = simplify_multiplicative_cancellation(expr)
        # Should not cancel because left factor is Binary("*", Const(2), Const(3)), not Const(2)
        assert result == expr

    def test_variable_no_cancellation(self):
        """Test that non-multiplication numerators don't cancel."""
        # x / 2 → stays the same
        expr = Binary("/", VarRef("x", ()), Const(2))
        result = simplify_multiplicative_cancellation(expr)
        assert result == expr

    def test_non_division_unchanged(self):
        """Test that non-division expressions are unchanged."""
        # 2 * x (not a division)
        expr = Binary("*", Const(2), VarRef("x", ()))
        result = simplify_multiplicative_cancellation(expr)
        assert result == expr

    def test_indexed_variable_cancels(self):
        """Test cancellation with indexed variables."""
        # 4 * x(i) / 4 → x(i)
        expr = Binary("/", Binary("*", Const(4), VarRef("x", ("i",))), Const(4))
        result = simplify_multiplicative_cancellation(expr)
        assert result == VarRef("x", ("i",))


class TestMultiplicativeCancellationIntegration:
    """Test multiplicative cancellation integrated with simplify_advanced."""

    def test_advanced_simplifies_nested_constant_then_cancels(self):
        """Test that advanced simplification folds constants then cancels."""
        # 2 * x / (1 + 1) → 2 * x / 2 → x
        expr = Binary("/", Binary("*", Const(2), VarRef("x", ())), Binary("+", Const(1), Const(1)))
        result = simplify_advanced(expr)
        assert result == VarRef("x", ())

    def test_advanced_simplifies_both_sides(self):
        """Test that both numerator and denominator are simplified."""
        # (2 * 3) * x / (1 + 1 + 4) → 6 * x / 6 → x
        expr = Binary(
            "/",
            Binary("*", Binary("*", Const(2), Const(3)), VarRef("x", ())),
            Binary("+", Binary("+", Const(1), Const(1)), Const(4)),
        )
        result = simplify_advanced(expr)
        assert result == VarRef("x", ())

    def test_cancellation_with_addition_in_numerator(self):
        """Test cancellation when numerator has addition."""
        # 3 * (x + y) / 3 → x + y
        expr = Binary(
            "/",
            Binary("*", Const(3), Binary("+", VarRef("x", ()), VarRef("y", ()))),
            Const(3),
        )
        result = simplify_advanced(expr)
        assert result == Binary("+", VarRef("x", ()), VarRef("y", ()))

    def test_partial_cancellation_one_term(self):
        """Test that only the matching factor cancels."""
        # (2 * x) / 2 → x (not 2 * x / 2)
        expr = Binary("/", Binary("*", Const(2), VarRef("x", ())), Const(2))
        result = simplify_advanced(expr)
        assert result == VarRef("x", ())

    def test_no_cancellation_different_denominators(self):
        """Test that different denominators don't cancel."""
        # 2 * x / 5 → stays the same
        expr = Binary("/", Binary("*", Const(2), VarRef("x", ())), Const(5))
        result = simplify_advanced(expr)
        # Should be unchanged (no simplification possible)
        assert isinstance(result, Binary)
        assert result.op == "/"

    def test_cancellation_then_further_simplification(self):
        """Test that cancellation enables further simplification."""
        # 2 * (x + 0) / 2 → x + 0 → x
        expr = Binary(
            "/",
            Binary("*", Const(2), Binary("+", VarRef("x", ()), Const(0))),
            Const(2),
        )
        result = simplify_advanced(expr)
        # Should cancel to (x + 0), then simplify to x
        assert result == VarRef("x", ())

    def test_cancellation_with_like_terms(self):
        """Test cancellation combined with term collection."""
        # 2 * (x + x) / 2 → x + x → 2*x
        expr = Binary(
            "/",
            Binary("*", Const(2), Binary("+", VarRef("x", ()), VarRef("x", ()))),
            Const(2),
        )
        result = simplify_advanced(expr)
        # Should cancel to (x + x), then collect to 2*x
        assert isinstance(result, Binary)
        assert result.op == "*"
        components = {result.left, result.right}
        assert VarRef("x", ()) in components
        assert Const(2) in components

    def test_deep_nesting_with_cancellation(self):
        """Test cancellation in deeply nested expressions."""
        # ((3 * x) / 3) + y → x + y
        inner = Binary("/", Binary("*", Const(3), VarRef("x", ())), Const(3))
        expr = Binary("+", inner, VarRef("y", ()))
        result = simplify_advanced(expr)
        # The division should simplify to x, giving x + y
        assert isinstance(result, Binary)
        assert result.op == "+"
        components = {result.left, result.right}
        assert VarRef("x", ()) in components
        assert VarRef("y", ()) in components

    def test_fractional_constants_cancel(self):
        """Test cancellation with fractional constants."""
        # 0.5 * x / 0.5 → x
        expr = Binary("/", Binary("*", Const(0.5), VarRef("x", ())), Const(0.5))
        result = simplify_advanced(expr)
        assert result == VarRef("x", ())

    def test_negative_constants_cancel(self):
        """Test cancellation with negative constants."""
        # (-2) * x / (-2) → x
        expr = Binary("/", Binary("*", Const(-2), VarRef("x", ())), Const(-2))
        result = simplify_advanced(expr)
        assert result == VarRef("x", ())
