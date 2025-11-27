"""Tests for division simplification transformation."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.division import simplify_division


class TestDivisionSimplification:
    """Test suite for division simplification (T3.1)."""

    def test_simple_variable_cancellation(self):
        """Test: (x*y)/x → y"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x*y)/x
        expr = Binary("/", Binary("*", x, y), x)
        result = simplify_division(expr)

        # Expected: y
        assert isinstance(result, SymbolRef)
        assert result.name == "y"

    def test_multiple_factor_cancellation(self):
        """Test: (x*y*z)/x → y*z"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # (x*y*z)/x
        expr = Binary("/", Binary("*", Binary("*", x, y), z), x)
        result = simplify_division(expr)

        # Expected: y*z
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_constant_cancellation(self):
        """Test: (2*x)/(2) → x"""
        x = SymbolRef("x")
        two = Const(2)

        # (2*x)/2
        expr = Binary("/", Binary("*", two, x), Const(2))
        result = simplify_division(expr)

        # Expected: x
        assert isinstance(result, SymbolRef)
        assert result.name == "x"

    def test_multiple_common_factors(self):
        """Test: (2*x*y)/(2*x) → y"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        two = Const(2)

        # (2*x*y)/(2*x)
        expr = Binary("/", Binary("*", Binary("*", two, x), y), Binary("*", Const(2), x))
        result = simplify_division(expr)

        # Expected: y
        assert isinstance(result, SymbolRef)
        assert result.name == "y"

    def test_complete_cancellation(self):
        """Test: (x*y)/(x*y) → 1"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x*y)/(x*y)
        numerator = Binary("*", x, y)
        denominator = Binary("*", x, y)
        expr = Binary("/", numerator, denominator)
        result = simplify_division(expr)

        # Expected: 1
        assert isinstance(result, Const)
        assert result.value == 1

    def test_no_common_factors(self):
        """Test: (x*y)/(z*w) → (x*y)/(z*w) (unchanged)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        w = SymbolRef("w")

        # (x*y)/(z*w)
        expr = Binary("/", Binary("*", x, y), Binary("*", z, w))
        result = simplify_division(expr)

        # Expected: unchanged
        assert result == expr

    def test_zero_constant_not_canceled(self):
        """Test: (0*x)/(0) → (0*x)/(0) (unsafe, not canceled)"""
        x = SymbolRef("x")
        zero = Const(0)

        # (0*x)/0
        expr = Binary("/", Binary("*", zero, x), Const(0))
        result = simplify_division(expr)

        # Expected: unchanged (zero is unsafe to cancel)
        assert result == expr

    def test_function_call_not_canceled(self):
        """Test: (exp(x)*y)/exp(x) → (exp(x)*y)/exp(x) (conservative)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        exp_x = Call("exp", [x])

        # (exp(x)*y)/exp(x)
        expr = Binary("/", Binary("*", exp_x, y), Call("exp", [SymbolRef("x")]))
        result = simplify_division(expr)

        # Expected: unchanged (function calls not canceled)
        assert result == expr

    def test_non_division_unchanged(self):
        """Test: Non-division expressions are unchanged"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # x + y (not a division)
        expr = Binary("+", x, y)
        result = simplify_division(expr)

        # Expected: unchanged
        assert result == expr

    def test_partial_cancellation(self):
        """Test: (x*y*z)/(x*w) → (y*z)/w"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        w = SymbolRef("w")

        # (x*y*z)/(x*w)
        expr = Binary("/", Binary("*", Binary("*", x, y), z), Binary("*", x, w))
        result = simplify_division(expr)

        # Expected: (y*z)/w
        assert isinstance(result, Binary)
        assert result.op == "/"
        # Numerator should be y*z
        assert isinstance(result.left, Binary)
        assert result.left.op == "*"
        # Denominator should be w
        assert isinstance(result.right, SymbolRef)
        assert result.right.name == "w"

    def test_duplicate_factors_in_numerator(self):
        """Test: (x*x*y)/x → x*y (cancel only one x)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x*x*y)/x
        expr = Binary("/", Binary("*", Binary("*", x, x), y), x)
        result = simplify_division(expr)

        # Expected: x*y (only one x should be canceled)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_duplicate_factors_in_denominator(self):
        """Test: (x*y)/(x*x) → y/x (cancel only one x)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x*y)/(x*x)
        expr = Binary("/", Binary("*", x, y), Binary("*", x, x))
        result = simplify_division(expr)

        # Expected: y/x (only one x should be canceled)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, SymbolRef)
        assert result.left.name == "y"
        assert isinstance(result.right, SymbolRef)
        assert result.right.name == "x"

    def test_duplicate_factors_both_sides(self):
        """Test: (x*x*y)/(x*x) → y (cancel matching pairs)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # (x*x*y)/(x*x)
        expr = Binary("/", Binary("*", Binary("*", x, x), y), Binary("*", x, x))
        result = simplify_division(expr)

        # Expected: y (both x's should be canceled)
        assert isinstance(result, SymbolRef)
        assert result.name == "y"
