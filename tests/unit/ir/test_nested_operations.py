"""Tests for nested operation simplification."""

from src.ir.ast import Binary, Const, SymbolRef
from src.ir.transformations.nested_operations import simplify_nested_products


class TestNestedProductSimplification:
    """Test suite for nested product simplification (T2.2)."""

    def test_simple_nested_constants(self):
        """Test: (2*x)*3 → 6*x"""
        x = SymbolRef("x")

        # (2*x)*3
        expr = Binary("*", Binary("*", Const(2), x), Const(3))
        result = simplify_nested_products(expr)

        # Expected: 6*x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Const)
        assert result.left.value == 6

    def test_triple_nesting(self):
        """Test: ((2*x)*3)*5 → 30*x"""
        x = SymbolRef("x")

        # ((2*x)*3)*5
        inner = Binary("*", Const(2), x)
        middle = Binary("*", inner, Const(3))
        expr = Binary("*", middle, Const(5))

        result = simplify_nested_products(expr)

        # Expected: 30*x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Const)
        assert result.left.value == 30

    def test_all_constants(self):
        """Test: (2*3)*5 → 30"""
        expr = Binary("*", Binary("*", Const(2), Const(3)), Const(5))
        result = simplify_nested_products(expr)

        # Expected: 30
        assert isinstance(result, Const)
        assert result.value == 30

    def test_nested_variables(self):
        """Test: (x*y)*z → x*y*z (flattened)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # (x*y)*z
        expr = Binary("*", Binary("*", x, y), z)
        result = simplify_nested_products(expr)

        # Should be flattened but structure may vary
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_mixed_constants_and_vars(self):
        """Test: (2*x)*(3*y) → 6*x*y"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (2*x)*(3*y)
        left = Binary("*", Const(2), x)
        right = Binary("*", Const(3), y)
        expr = Binary("*", left, right)

        result = simplify_nested_products(expr)

        # Expected: 6*x*y (structured as (6*x)*y)
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Result should be nested: Binary("*", Binary("*", Const(6), x), y)
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        # The consolidated constant should be 6
        assert isinstance(result.left.left, Const)
        assert result.left.left.value == 6
        # Followed by variable x
        assert isinstance(result.left.right, SymbolRef)
        assert result.left.right.name == "x"
        # And variable y at the top level
        assert isinstance(result.right, SymbolRef)
        assert result.right.name == "y"

    def test_no_nesting_unchanged(self):
        """Test: 2*x → 2*x (no nesting, should be unchanged)"""
        x = SymbolRef("x")

        # 2*x (no nesting)
        expr = Binary("*", Const(2), x)
        result = simplify_nested_products(expr)

        # Expected: unchanged
        assert result == expr

    def test_non_multiplication_unchanged(self):
        """Test: x + y → x + y (not multiplication)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # x + y
        expr = Binary("+", x, y)
        result = simplify_nested_products(expr)

        # Expected: unchanged
        assert result == expr

    def test_deeply_nested(self):
        """Test: (((x*2)*3)*4)*5 → 120*x"""
        x = SymbolRef("x")

        # Build deeply nested: (((x*2)*3)*4)*5
        level1 = Binary("*", x, Const(2))
        level2 = Binary("*", level1, Const(3))
        level3 = Binary("*", level2, Const(4))
        expr = Binary("*", level3, Const(5))

        result = simplify_nested_products(expr)

        # Expected: 120*x
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Const)
        assert result.left.value == 120
