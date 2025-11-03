"""Tests for apply_simplification function."""

import pytest

from src.ad.ad_core import apply_simplification
from src.ir.ast import Binary, Const, VarRef


class TestApplySimplification:
    """Test apply_simplification with different modes."""

    def test_mode_none_no_simplification(self):
        """Test that mode='none' returns expression unchanged."""
        # 1 + 1 should stay as is
        expr = Binary("+", Const(1), Const(1))
        result = apply_simplification(expr, "none")
        assert result == expr
        # Should not simplify to Const(2)
        assert result != Const(2)

    def test_mode_basic_constant_folding(self):
        """Test that mode='basic' applies basic simplification."""
        # 1 + 1 should simplify to 2
        expr = Binary("+", Const(1), Const(1))
        result = apply_simplification(expr, "basic")
        assert result == Const(2)

    def test_mode_basic_no_term_collection(self):
        """Test that mode='basic' does not collect like terms."""
        # x + x should not simplify to 2*x with basic mode
        expr = Binary("+", VarRef("x", ()), VarRef("x", ()))
        result = apply_simplification(expr, "basic")
        # Should remain as x + x (no term collection)
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_mode_advanced_constant_collection(self):
        """Test that mode='advanced' collects constants."""
        # 1 + x + 1 should simplify to x + 2
        expr = Binary("+", Binary("+", Const(1), VarRef("x", ())), Const(1))
        result = apply_simplification(expr, "advanced")
        # Should be x + 2 or 2 + x
        assert isinstance(result, Binary)
        assert result.op == "+"
        left, right = result.left, result.right
        components = {left, right}
        assert VarRef("x", ()) in components
        assert Const(2) in components

    def test_mode_advanced_like_term_collection(self):
        """Test that mode='advanced' collects like terms."""
        # x + x should simplify to 2*x
        expr = Binary("+", VarRef("x", ()), VarRef("x", ()))
        result = apply_simplification(expr, "advanced")
        # Should be 2 * x or x * 2
        assert isinstance(result, Binary)
        assert result.op == "*"
        left, right = result.left, result.right
        components = {left, right}
        assert VarRef("x", ()) in components
        assert Const(2) in components

    def test_invalid_mode_raises_error(self):
        """Test that invalid mode raises ValueError."""
        expr = Const(1)
        with pytest.raises(ValueError, match="Invalid simplification mode"):
            apply_simplification(expr, "invalid")

    def test_mode_advanced_with_coefficients(self):
        """Test that mode='advanced' collects coefficients."""
        # 2*x + 3*x should simplify to 5*x
        expr = Binary(
            "+",
            Binary("*", Const(2), VarRef("x", ())),
            Binary("*", Const(3), VarRef("x", ())),
        )
        result = apply_simplification(expr, "advanced")
        # Should be 5 * x or x * 5
        assert isinstance(result, Binary)
        assert result.op == "*"
        left, right = result.left, result.right
        components = {left, right}
        assert VarRef("x", ()) in components
        assert Const(5) in components

    def test_mode_advanced_cancellation(self):
        """Test that mode='advanced' handles cancellation."""
        # x - x should simplify to 0
        expr = Binary("-", VarRef("x", ()), VarRef("x", ()))
        result = apply_simplification(expr, "advanced")
        assert result == Const(0)
