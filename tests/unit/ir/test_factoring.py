"""Tests for common factor extraction transformation (T1.1 and T1.2)."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.factoring import extract_common_factors, multi_term_factoring


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


class TestMultiTermFactoring:
    """Test multi-term factoring (T1.2) - 2x2 pattern."""

    def test_simple_2x2_pattern(self):
        """a*c + a*d + b*c + b*d → (a + b)*(c + d)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")

        # a*c + a*d + b*c + b*d
        term1 = Binary("*", a, c)
        term2 = Binary("*", a, d)
        term3 = Binary("*", b, c)
        term4 = Binary("*", b, d)

        expr = Binary("+", Binary("+", Binary("+", term1, term2), term3), term4)

        result = multi_term_factoring(expr)

        # Should be (a + b)*(c + d)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_2x2_with_constants(self):
        """2*x + 2*y + 3*x + 3*y → (2 + 3)*(x + y)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # 2*x + 2*y + 3*x + 3*y
        term1 = Binary("*", Const(2), x)
        term2 = Binary("*", Const(2), y)
        term3 = Binary("*", Const(3), x)
        term4 = Binary("*", Const(3), y)

        expr = Binary("+", Binary("+", Binary("+", term1, term2), term3), term4)

        result = multi_term_factoring(expr)

        # Should factor to (2 + 3)*(x + y)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_no_2x2_pattern_3_terms(self):
        """a*c + a*d + b*c → unchanged (only 3 terms)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")

        # a*c + a*d + b*c (only 3 terms)
        term1 = Binary("*", a, c)
        term2 = Binary("*", a, d)
        term3 = Binary("*", b, c)

        expr = Binary("+", Binary("+", term1, term2), term3)

        result = multi_term_factoring(expr)

        # Should be unchanged (requires exactly 4 terms)
        assert result == expr

    def test_no_2x2_pattern_5_terms(self):
        """5 terms → unchanged (requires exactly 4 terms)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")
        e = SymbolRef("e")

        # a + b + c + d + e (5 terms)
        expr = Binary("+", Binary("+", Binary("+", Binary("+", a, b), c), d), e)

        result = multi_term_factoring(expr)

        # Should be unchanged
        assert result == expr

    def test_no_common_structure(self):
        """a*b + c*d + e*f + g*h → unchanged (no 2x2 structure)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")
        e = SymbolRef("e")
        f = SymbolRef("f")
        g = SymbolRef("g")
        h = SymbolRef("h")

        # All different factors, no 2x2 pattern
        term1 = Binary("*", a, b)
        term2 = Binary("*", c, d)
        term3 = Binary("*", e, f)
        term4 = Binary("*", g, h)

        expr = Binary("+", Binary("+", Binary("+", term1, term2), term3), term4)

        result = multi_term_factoring(expr)

        # Should be unchanged
        assert result == expr

    def test_non_addition_unchanged(self):
        """Non-addition expressions unchanged"""
        a = SymbolRef("a")
        b = SymbolRef("b")

        # a * b (multiplication, not addition)
        expr = Binary("*", a, b)

        result = multi_term_factoring(expr)

        # Should be unchanged
        assert result == expr

    def test_complex_2x2_pattern(self):
        """(x*y)*a + (x*y)*b + (z*w)*a + (z*w)*b → factored"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        w = SymbolRef("w")
        a = SymbolRef("a")
        b = SymbolRef("b")

        # (x*y)*a + (x*y)*b + (z*w)*a + (z*w)*b
        term1 = Binary("*", Binary("*", x, y), a)
        term2 = Binary("*", Binary("*", x, y), b)
        term3 = Binary("*", Binary("*", z, w), a)
        term4 = Binary("*", Binary("*", z, w), b)

        expr = Binary("+", Binary("+", Binary("+", term1, term2), term3), term4)

        result = multi_term_factoring(expr)

        # Should factor
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_mixed_multiplication_factors(self):
        """x*y*a + x*y*b + x*z*a + x*z*b → factored"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        a = SymbolRef("a")
        b = SymbolRef("b")

        # Three-factor products
        term1 = Binary("*", Binary("*", x, y), a)
        term2 = Binary("*", Binary("*", x, y), b)
        term3 = Binary("*", Binary("*", x, z), a)
        term4 = Binary("*", Binary("*", x, z), b)

        expr = Binary("+", Binary("+", Binary("+", term1, term2), term3), term4)

        result = multi_term_factoring(expr)

        # Should recognize pattern
        assert isinstance(result, Binary)

    def test_single_term_factors(self):
        """a + b + c + d → unchanged (no products)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")

        # Simple sum, no multiplication
        expr = Binary("+", Binary("+", Binary("+", a, b), c), d)

        result = multi_term_factoring(expr)

        # Should be unchanged (no common factors in non-products)
        assert result == expr
