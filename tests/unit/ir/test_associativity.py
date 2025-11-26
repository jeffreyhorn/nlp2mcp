"""Tests for associativity normalization transformation (T3.1)."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.associativity import normalize_associativity


class TestMultiplicationAssociativity:
    """Test associativity normalization for multiplication."""

    def test_simple_two_constant_consolidation(self):
        """(x * 2) * 3 → x * 6"""
        x = SymbolRef("x")

        # (x * 2) * 3
        expr = Binary("*", Binary("*", x, Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should be x * 6
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_three_constant_consolidation(self):
        """((x * 2) * 3) * 5 → x * 30"""
        x = SymbolRef("x")

        # ((x * 2) * 3) * 5
        expr = Binary("*", Binary("*", Binary("*", x, Const(2)), Const(3)), Const(5))

        result = normalize_associativity(expr)

        # Should be x * 30
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 30

    def test_multiple_variables_with_constants(self):
        """(x * 2) * y * 3 → (x * y) * 6"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x * 2) * y * 3 = ((x * 2) * y) * 3
        expr = Binary("*", Binary("*", Binary("*", x, Const(2)), y), Const(3))

        result = normalize_associativity(expr)

        # Should consolidate constants to 6
        # Result: (x * y) * 6
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_all_constants(self):
        """2 * 3 * 5 → 30"""
        # (2 * 3) * 5
        expr = Binary("*", Binary("*", Const(2), Const(3)), Const(5))

        result = normalize_associativity(expr)

        # Should be just 30
        assert isinstance(result, Const)
        assert result.value == 30

    def test_single_constant_no_change(self):
        """x * 2 → x * 2 (no consolidation needed)"""
        x = SymbolRef("x")

        expr = Binary("*", x, Const(2))

        result = normalize_associativity(expr)

        # Should return unchanged (only one constant)
        assert result == expr


class TestAdditionAssociativity:
    """Test associativity normalization for addition."""

    def test_simple_two_constant_consolidation(self):
        """(x + 2) + 3 → x + 5"""
        x = SymbolRef("x")

        # (x + 2) + 3
        expr = Binary("+", Binary("+", x, Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should be x + 5
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 5

    def test_three_constant_consolidation(self):
        """((x + 1) + 2) + 3 → x + 6"""
        x = SymbolRef("x")

        # ((x + 1) + 2) + 3
        expr = Binary("+", Binary("+", Binary("+", x, Const(1)), Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should be x + 6
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_multiple_variables_with_constants(self):
        """(x + 2) + y + 3 → (x + y) + 5"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x + 2) + y + 3 = ((x + 2) + y) + 3
        expr = Binary("+", Binary("+", Binary("+", x, Const(2)), y), Const(3))

        result = normalize_associativity(expr)

        # Should consolidate constants to 5
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.right, Const)
        assert result.right.value == 5

    def test_all_constants(self):
        """1 + 2 + 3 → 6"""
        # (1 + 2) + 3
        expr = Binary("+", Binary("+", Const(1), Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should be just 6
        assert isinstance(result, Const)
        assert result.value == 6


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_no_constants_no_change(self):
        """x * y → x * y (no constants)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("*", x, y)

        result = normalize_associativity(expr)

        # Should return unchanged
        assert result == expr

    def test_non_associative_operation(self):
        """x / y → x / y (division, not normalized)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("/", x, y)

        result = normalize_associativity(expr)

        # Should return unchanged (not multiplication or addition)
        assert result == expr

    def test_single_term(self):
        """x → x (single term, no operation)"""
        x = SymbolRef("x")

        result = normalize_associativity(x)

        # Should return unchanged
        assert result == x

    def test_nested_mixed_operations(self):
        """(x * 2) + 3 → should not mix operations"""
        x = SymbolRef("x")

        # (x * 2) + 3
        expr = Binary("+", Binary("*", x, Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should only consolidate the addition level
        # No change since only one constant at addition level
        assert isinstance(result, Binary)
        assert result.op == "+"


class TestFloatingPointConstants:
    """Test with floating-point constants."""

    def test_float_multiplication(self):
        """x * 2.5 * 4.0 → x * 10.0"""
        x = SymbolRef("x")

        # (x * 2.5) * 4.0
        expr = Binary("*", Binary("*", x, Const(2.5)), Const(4.0))

        result = normalize_associativity(expr)

        # Should be x * 10.0
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 10.0

    def test_float_addition(self):
        """x + 1.5 + 2.5 → x + 4.0"""
        x = SymbolRef("x")

        # (x + 1.5) + 2.5
        expr = Binary("+", Binary("+", x, Const(1.5)), Const(2.5))

        result = normalize_associativity(expr)

        # Should be x + 4.0
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 4.0


class TestComplexExpressions:
    """Test with complex nested expressions."""

    def test_function_calls_with_constants(self):
        """(exp(x) * 2) * 3 → exp(x) * 6"""
        x = SymbolRef("x")
        exp_x = Call("exp", (x,))

        # (exp(x) * 2) * 3
        expr = Binary("*", Binary("*", exp_x, Const(2)), Const(3))

        result = normalize_associativity(expr)

        # Should be exp(x) * 6
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == exp_x
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_deep_nesting(self):
        """(((x * 2) * 3) * 4) * 5 → x * 120"""
        x = SymbolRef("x")

        # Build deeply nested: (((x * 2) * 3) * 4) * 5
        expr = x
        for const_val in [2, 3, 4, 5]:
            expr = Binary("*", expr, Const(const_val))

        result = normalize_associativity(expr)

        # Should be x * 120 (2*3*4*5 = 120)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 120


class TestSizeBudgetConsiderations:
    """Test that transformations reduce operations."""

    def test_consolidation_reduces_operations(self):
        """Verify constant consolidation reduces operation count."""
        x = SymbolRef("x")

        # Original: ((x * 2) * 3) * 5
        # Size: 3 multiplications = 3 operations
        original = Binary("*", Binary("*", Binary("*", x, Const(2)), Const(3)), Const(5))

        # After: x * 30
        # Size: 1 multiplication = 1 operation
        result = normalize_associativity(original)

        # Result should have fewer operations
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.right, Const)
        assert result.right.value == 30


class TestMultipleNonConstants:
    """Test with multiple non-constant factors/terms."""

    def test_multiple_variables_multiplication(self):
        """(a * 2) * b * c * 3 → (a * b * c) * 6"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")

        # (a * 2) * b * c * 3 = (((a * 2) * b) * c) * 3
        expr = Binary("*", Binary("*", Binary("*", Binary("*", a, Const(2)), b), c), Const(3))

        result = normalize_associativity(expr)

        # Should consolidate constants to 6
        # Result: (a * b * c) * 6
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_multiple_variables_addition(self):
        """(a + 1) + b + c + 2 → (a + b + c) + 3"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")

        # (a + 1) + b + c + 2 = (((a + 1) + b) + c) + 2
        expr = Binary("+", Binary("+", Binary("+", Binary("+", a, Const(1)), b), c), Const(2))

        result = normalize_associativity(expr)

        # Should consolidate constants to 3
        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.right, Const)
        assert result.right.value == 3
