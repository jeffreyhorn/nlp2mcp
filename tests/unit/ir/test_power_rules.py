"""Tests for power expression consolidation."""

from src.ir.ast import Binary, Const, SymbolRef
from src.ir.transformations.power_rules import consolidate_powers


class TestPowerConsolidation:
    """Test suite for power expression consolidation (T2.3)."""

    def test_power_of_zero(self):
        """Test: x^0 → 1"""
        x = SymbolRef("x")

        # x^0
        expr = Binary("**", x, Const(0))
        result = consolidate_powers(expr)

        # Expected: 1
        assert isinstance(result, Const)
        assert result.value == 1

    def test_power_of_one(self):
        """Test: x^1 → x"""
        x = SymbolRef("x")

        # x^1
        expr = Binary("**", x, Const(1))
        result = consolidate_powers(expr)

        # Expected: x
        assert result == x

    def test_power_of_power(self):
        """Test: (x^2)^3 → x^6"""
        x = SymbolRef("x")

        # (x^2)^3
        inner = Binary("**", x, Const(2))
        expr = Binary("**", inner, Const(3))

        result = consolidate_powers(expr)

        # Expected: x^6
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 6

    def test_product_of_same_base(self):
        """Test: x^2 * x^3 → x^5"""
        x = SymbolRef("x")

        # x^2 * x^3
        left = Binary("**", x, Const(2))
        right = Binary("**", x, Const(3))
        expr = Binary("*", left, right)

        result = consolidate_powers(expr)

        # Expected: x^5
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 5

    def test_product_of_different_bases(self):
        """Test: x^2 * y^3 → x^2 * y^3 (unchanged)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # x^2 * y^3
        left = Binary("**", x, Const(2))
        right = Binary("**", y, Const(3))
        expr = Binary("*", left, right)

        result = consolidate_powers(expr)

        # Expected: unchanged (different bases)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_multiple_same_base(self):
        """Test: x^2 * x^3 * x^4 → x^9"""
        x = SymbolRef("x")

        # x^2 * x^3 * x^4
        pow1 = Binary("**", x, Const(2))
        pow2 = Binary("**", x, Const(3))
        pow3 = Binary("**", x, Const(4))

        expr = Binary("*", Binary("*", pow1, pow2), pow3)

        result = consolidate_powers(expr)

        # Expected: x^9
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 9

    def test_mixed_powers_and_factors(self):
        """Test: 2 * x^2 * x^3 → 2 * x^5"""
        x = SymbolRef("x")

        # 2 * x^2 * x^3
        pow1 = Binary("**", x, Const(2))
        pow2 = Binary("**", x, Const(3))

        expr = Binary("*", Binary("*", Const(2), pow1), pow2)

        result = consolidate_powers(expr)

        # Expected: 2 * x^5 (or x^5 * 2)
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_non_power_unchanged(self):
        """Test: x * y → x * y (not powers)"""
        x = SymbolRef("x")
        y = SymbolRef("y")

        # x * y
        expr = Binary("*", x, y)
        result = consolidate_powers(expr)

        # Expected: unchanged
        assert result == expr

    def test_bare_base_with_power(self):
        """Test: x * x^2 → x^3 (implicit exponent of 1 for bare base)"""
        x = SymbolRef("x")

        # x * x^2
        expr = Binary("*", x, Binary("**", x, Const(2)))
        result = consolidate_powers(expr)

        # Expected: x^3
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 3

    def test_power_with_bare_base(self):
        """Test: x^2 * x → x^3 (implicit exponent of 1 for bare base)"""
        x = SymbolRef("x")

        # x^2 * x
        expr = Binary("*", Binary("**", x, Const(2)), x)
        result = consolidate_powers(expr)

        # Expected: x^3
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 3

    def test_multiple_bare_bases(self):
        """Test: x * x * x → x^3"""
        x = SymbolRef("x")

        # x * x * x
        expr = Binary("*", Binary("*", x, x), x)
        result = consolidate_powers(expr)

        # Expected: x^3
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 3

    def test_mixed_bare_and_power(self):
        """Test: x * x^2 * x → x^4"""
        x = SymbolRef("x")

        # x * x^2 * x
        expr = Binary("*", Binary("*", x, Binary("**", x, Const(2))), x)
        result = consolidate_powers(expr)

        # Expected: x^4
        assert isinstance(result, Binary)
        assert result.op == "**"
        assert result.left == x
        assert isinstance(result.right, Const)
        assert result.right.value == 4

    def test_consolidation_resulting_in_exponent_one(self):
        """Test: x^3 * x^(-2) → x^1 → x"""
        x = SymbolRef("x")

        # x^3 * x^(-2)
        pow1 = Binary("**", x, Const(3))
        pow2 = Binary("**", x, Const(-2))
        expr = Binary("*", pow1, pow2)

        result = consolidate_powers(expr)

        # Expected: x (exponent=1 should simplify to base)
        assert result == x

    def test_consolidation_resulting_in_exponent_zero(self):
        """Test: x^2 * x^(-2) → x^0 → 1"""
        x = SymbolRef("x")

        # x^2 * x^(-2)
        pow1 = Binary("**", x, Const(2))
        pow2 = Binary("**", x, Const(-2))
        expr = Binary("*", pow1, pow2)

        result = consolidate_powers(expr)

        # Expected: 1 (exponent=0 should simplify to 1)
        assert isinstance(result, Const)
        assert result.value == 1
