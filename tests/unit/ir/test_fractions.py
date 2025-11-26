"""Tests for fraction combining transformation (T2.1)."""

from src.ir.ast import Binary, Call, Const, SymbolRef
from src.ir.transformations.fractions import combine_fractions


class TestBasicFractionCombining:
    """Test basic fraction combining patterns."""

    def test_simple_two_fraction_combining(self):
        """x/a + y/a → (x + y)/a"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")

        # x/a + y/a
        expr = Binary("+", Binary("/", x, a), Binary("/", y, a))

        result = combine_fractions(expr)

        # Should be (x + y)/a
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.left.left == x
        assert result.left.right == y
        assert result.right == a

    def test_three_fraction_combining(self):
        """x/a + y/a + z/a → (x + y + z)/a"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        z = SymbolRef("z")
        a = SymbolRef("a")

        # x/a + y/a + z/a = (x/a + y/a) + z/a
        expr = Binary("+", Binary("+", Binary("/", x, a), Binary("/", y, a)), Binary("/", z, a))

        result = combine_fractions(expr)

        # Should be (x + y + z)/a
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.right == a

    def test_constant_denominator(self):
        """x/2 + y/2 → (x + y)/2"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        two = Const(2)

        # x/2 + y/2
        expr = Binary("+", Binary("/", x, two), Binary("/", y, two))

        result = combine_fractions(expr)

        # Should be (x + y)/2
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.left.left == x
        assert result.left.right == y
        assert result.right == two

    def test_mixed_terms_and_fractions(self):
        """a/c + b + d/c → (a + d)/c + b"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")

        # a/c + b + d/c = (a/c + b) + d/c
        expr = Binary("+", Binary("+", Binary("/", a, c), b), Binary("/", d, c))

        result = combine_fractions(expr)

        # Should combine a/c and d/c into (a+d)/c, keep b separate
        # Result: (a+d)/c + b
        assert isinstance(result, Binary)
        assert result.op == "+"


class TestComplexDenominators:
    """Test combining with complex denominators."""

    def test_function_call_denominator(self):
        """x/exp(y) + z/exp(y) → (x + z)/exp(y)"""
        x = SymbolRef("x")
        z = SymbolRef("z")
        y = SymbolRef("y")
        exp_y = Call("exp", (y,))

        # x/exp(y) + z/exp(y)
        expr = Binary("+", Binary("/", x, exp_y), Binary("/", z, exp_y))

        result = combine_fractions(expr)

        # Should be (x + z)/exp(y)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.left.left == x
        assert result.left.right == z
        assert result.right == exp_y

    def test_complex_denominator_expression(self):
        """a/(x*y) + b/(x*y) → (a + b)/(x*y)"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        x = SymbolRef("x")
        y = SymbolRef("y")
        xy = Binary("*", x, y)

        # a/(x*y) + b/(x*y)
        expr = Binary("+", Binary("/", a, xy), Binary("/", b, xy))

        result = combine_fractions(expr)

        # Should be (a + b)/(x*y)
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.right == xy


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_different_denominators_no_combining(self):
        """x/a + y/b → x/a + y/b (no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")
        b = SymbolRef("b")

        # x/a + y/b
        expr = Binary("+", Binary("/", x, a), Binary("/", y, b))

        result = combine_fractions(expr)

        # Should return unchanged (different denominators)
        assert result == expr

    def test_single_fraction_no_combining(self):
        """x/a → x/a (single fraction, no change)"""
        x = SymbolRef("x")
        a = SymbolRef("a")

        expr = Binary("/", x, a)

        result = combine_fractions(expr)

        # Should return unchanged (not addition)
        assert result == expr

    def test_non_addition_expression(self):
        """x*y → x*y (not addition, no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("*", x, y)

        result = combine_fractions(expr)

        assert result == expr

    def test_no_division_terms(self):
        """x + y → x + y (no divisions, no change)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        expr = Binary("+", x, y)

        result = combine_fractions(expr)

        # Should return unchanged (no fractions)
        assert result == expr

    def test_single_denominator_group(self):
        """a/x → a/x (only one fraction with denominator x)"""
        a = SymbolRef("a")
        x = SymbolRef("x")
        b = SymbolRef("b")

        # a/x + b (one fraction, one non-fraction)
        expr = Binary("+", Binary("/", a, x), b)

        result = combine_fractions(expr)

        # Should return unchanged (can't combine single fraction)
        assert result == expr


class TestMultipleGroups:
    """Test combining with multiple denominator groups."""

    def test_two_groups_of_fractions(self):
        """a/x + b/x + c/y + d/y → (a+b)/x + (c+d)/y"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        c = SymbolRef("c")
        d = SymbolRef("d")
        x = SymbolRef("x")
        y = SymbolRef("y")

        # a/x + b/x + c/y + d/y
        # = ((a/x + b/x) + c/y) + d/y
        t1 = Binary("/", a, x)
        t2 = Binary("/", b, x)
        t3 = Binary("/", c, y)
        t4 = Binary("/", d, y)
        expr = Binary("+", Binary("+", Binary("+", t1, t2), t3), t4)

        result = combine_fractions(expr)

        # Should combine into (a+b)/x + (c+d)/y
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Both sides should be divisions
        assert isinstance(result.left, Binary)
        assert result.left.op == "/" or result.right.op == "/"


class TestSizeBudgetConsiderations:
    """Test that transformations are beneficial (size considerations)."""

    def test_combining_reduces_operations(self):
        """Verify combining reduces operation count."""
        x = SymbolRef("x")
        y = SymbolRef("y")
        a = SymbolRef("a")

        # Original: x/a + y/a
        # Size: 2 divisions + 1 addition = 3 operations
        original = Binary("+", Binary("/", x, a), Binary("/", y, a))

        # After combining: (x + y)/a
        # Size: 1 addition + 1 division = 2 operations
        result = combine_fractions(original)

        # Result should have fewer operations
        assert isinstance(result, Binary)
        assert result.op == "/"


class TestNestedNumerators:
    """Test combining with complex numerators."""

    def test_complex_numerators(self):
        """(a*x)/c + (b*x)/c → (a*x + b*x)/c"""
        a = SymbolRef("a")
        b = SymbolRef("b")
        x = SymbolRef("x")
        c = SymbolRef("c")

        # (a*x)/c + (b*x)/c
        ax = Binary("*", a, x)
        bx = Binary("*", b, x)
        expr = Binary("+", Binary("/", ax, c), Binary("/", bx, c))

        result = combine_fractions(expr)

        # Should be (a*x + b*x)/c
        assert isinstance(result, Binary)
        assert result.op == "/"
        assert isinstance(result.left, Binary)
        assert result.left.op == "+"
        assert result.right == c
