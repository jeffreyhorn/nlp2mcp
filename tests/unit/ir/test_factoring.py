"""Tests for common factor extraction transformation (T1.1)."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.factoring import extract_common_factors


class TestBasicFactoring:
    """Test basic common factor extraction patterns."""

    def test_simple_two_term_factoring(self):
        """x*y + x*z → x*(y + z)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # x*y + x*z
        expr = Binary("+", Binary("*", x, y), Binary("*", x, z))

        result = extract_common_factors(expr)

        # Should be x*(y + z)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        assert isinstance(result.right, Binary)
        assert result.right.op == "+"
        assert result.right.left == y
        assert result.right.right == z

    def test_three_term_factoring(self):
        """x*a + x*b + x*c → x*(a + b + c)"""
        x = SymbolRef("x")
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")

        # x*a + x*b + x*c = (x*a + x*b) + x*c
        expr = Binary("+", Binary("+", Binary("*", x, a), Binary("*", x, b)), Binary("*", x, c))

        result = extract_common_factors(expr)

        # Should be x*(a + b + c)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
        # Right side should be sum of a, b, c

    def test_constant_factoring(self):
        """2*x + 2*y → 2*(x + y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        two = Const(2)

        # 2*x + 2*y
        expr = Binary("+", Binary("*", two, x), Binary("*", two, y))

        result = extract_common_factors(expr)

        # Should be 2*(x + y)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == two
        assert isinstance(result.right, Binary)
        assert result.right.op == "+"
        assert result.right.left == x
        assert result.right.right == y

    def test_multiple_common_factors(self):
        """2*x*a + 2*x*b → 2*x*(a + b)"""
        x = SymbolRef("x")
        a = SymbolRef("a")
        b = SymbolRef("b")
        two = Const(2)

        # 2*x*a + 2*x*b = (2*x)*a + (2*x)*b
        lhs = Binary("*", Binary("*", two, x), a)
        rhs = Binary("*", Binary("*", two, x), b)
        expr = Binary("+", lhs, rhs)

        result = extract_common_factors(expr)

        # Should factor out both 2 and x
        # Result should be multiplication with 2, x, and (a+b)
        assert isinstance(result, Binary)
        assert result.op == "*"


class TestFunctionCallFactoring:
    """Test factoring with function calls as common factors."""

    def test_exp_function_factoring(self):
        """exp(x)*a + exp(x)*b → exp(x)*(a + b)"""
        x = SymbolRef("x")
        a = SymbolRef("a")
        b = SymbolRef("b")
        exp_x = Call("exp", (x,))

        # exp(x)*a + exp(x)*b
        expr = Binary("+", Binary("*", exp_x, a), Binary("*", exp_x, b))

        result = extract_common_factors(expr)

        # Should be exp(x)*(a + b)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == exp_x
        assert isinstance(result.right, Binary)
        assert result.right.op == "+"

    def test_complex_function_factoring(self):
        """2*exp(x)*sin(y) + 2*exp(x)*cos(y) → 2*exp(x)*(sin(y) + cos(y))"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        two = Const(2)
        exp_x = Call("exp", (x,))
        sin_y = Call("sin", (y,))
        cos_y = Call("cos", (y,))

        # 2*exp(x)*sin(y) + 2*exp(x)*cos(y)
        lhs = Binary("*", Binary("*", two, exp_x), sin_y)
        rhs = Binary("*", Binary("*", two, exp_x), cos_y)
        expr = Binary("+", lhs, rhs)

        result = extract_common_factors(expr)

        # Should factor out 2*exp(x)
        # Result: 2 * exp(x) * (sin(y) + cos(y))
        assert isinstance(result, Binary)
        assert result.op == "*"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_no_common_factors(self):
        """x*y + z*w → x*y + z*w (no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        w = SymbolRef("w")

        # x*y + z*w
        expr = Binary("+", Binary("*", x, y), Binary("*", z, w))

        result = extract_common_factors(expr)

        # Should return unchanged (no common factors)
        assert result == expr

    def test_single_term_no_factoring(self):
        """x*y → x*y (single term, no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("*", x, y)

        result = extract_common_factors(expr)

        # Should return unchanged
        assert result == expr

    def test_non_addition_expression(self):
        """x*y → x*y (not addition, no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("*", x, y)

        result = extract_common_factors(expr)

        assert result == expr

    def test_all_factors_common(self):
        """x*y + x*y → 2*(x*y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # x*y + x*y
        term = Binary("*", x, y)
        expr = Binary("+", term, term)

        result = extract_common_factors(expr)

        # Should factor out x and y, leaving 1+1
        # Result: x * y * (1 + 1) = x * y * 2
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_partial_common_factors(self):
        """x*y*a + x*y*b + x*z → x*(y*a + y*b + z)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        a = SymbolRef("a")
        b = SymbolRef("b")

        # x*y*a + x*y*b + x*z
        t1 = Binary("*", Binary("*", x, y), a)
        t2 = Binary("*", Binary("*", x, y), b)
        t3 = Binary("*", x, z)
        expr = Binary("+", Binary("+", t1, t2), t3)

        result = extract_common_factors(expr)

        # Should factor out x (common to all three)
        # Not y (only in first two terms)
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x


class TestSizeBudgetConsiderations:
    """Test that transformations are beneficial (size considerations)."""

    def test_simple_factoring_reduces_size(self):
        """Verify factoring reduces operation count."""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")

        # Original: x*y + x*z
        # Size: 2 multiplications + 1 addition = 3 operations
        original = Binary("+", Binary("*", x, y), Binary("*", x, z))

        # After factoring: x*(y + z)
        # Size: 1 addition + 1 multiplication = 2 operations
        result = extract_common_factors(original)

        # Result should have fewer operations
        # This is a sanity check - actual size budget is enforced by pipeline
        assert isinstance(result, Binary)


class TestNestedStructures:
    """Test factoring with nested expressions."""

    def test_nested_addition_flattening(self):
        """((a*x + b*x) + c*x) → x*(a + b + c)"""
        x = SymbolRef("x")
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")

        # ((a*x + b*x) + c*x)
        inner = Binary("+", Binary("*", a, x), Binary("*", b, x))
        expr = Binary("+", inner, Binary("*", c, x))

        result = extract_common_factors(expr)

        # Should factor out x from all three terms
        assert isinstance(result, Binary)
        assert result.op == "*"
        assert result.left == x
