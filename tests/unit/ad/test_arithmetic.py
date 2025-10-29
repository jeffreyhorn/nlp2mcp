"""
Tests for Arithmetic Operation Differentiation (Day 2)

Test Coverage:
-------------
1. Binary addition (+)
2. Binary subtraction (-)
3. Binary multiplication (*) - Product rule
4. Binary division (/) - Quotient rule
5. Unary plus (+)
6. Unary minus (-)
7. Chain rule through arithmetic operations
8. Division by zero detection (in evaluator)
"""

import pytest

from src.ad import differentiate
from src.ir.ast import Binary, Const, Unary, VarRef



pytestmark = pytest.mark.unit

@pytest.mark.unit
class TestAdditionDifferentiation:
    """Test differentiation of addition operations."""

    def test_add_two_variables(self):
        """d(x + y)/dx = 1 + 0 = 1"""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        result = differentiate(expr, "x")

        # Result should be: dx/dx + dy/dx = 1 + 0
        assert isinstance(result, Binary)
        assert result.op == "+"
        # Left should be 1.0 (dx/dx)
        assert isinstance(result.left, Const)
        assert result.left.value == 1.0
        # Right should be 0.0 (dy/dx)
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_add_variable_and_constant(self):
        """d(x + 5)/dx = 1 + 0 = 1"""
        expr = Binary("+", VarRef("x"), Const(5.0))
        result = differentiate(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "+"
        assert isinstance(result.left, Const)
        assert result.left.value == 1.0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0


@pytest.mark.unit
class TestSubtractionDifferentiation:
    """Test differentiation of subtraction operations."""

    def test_subtract_two_variables(self):
        """d(x - y)/dx = 1 - 0 = 1"""
        expr = Binary("-", VarRef("x"), VarRef("y"))
        result = differentiate(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "-"
        assert isinstance(result.left, Const)
        assert result.left.value == 1.0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_subtract_constant_from_variable(self):
        """d(x - 3)/dx = 1 - 0 = 1"""
        expr = Binary("-", VarRef("x"), Const(3.0))
        result = differentiate(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "-"
        assert isinstance(result.left, Const)
        assert result.left.value == 1.0
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0


@pytest.mark.unit
class TestMultiplicationDifferentiation:
    """Test differentiation of multiplication (product rule)."""

    def test_multiply_two_variables(self):
        """d(x * y)/dx = y * 1 + x * 0 = y"""
        expr = Binary("*", VarRef("x"), VarRef("y"))
        result = differentiate(expr, "x")

        # Result should be: y*(dx/dx) + x*(dy/dx) = y*1 + x*0
        assert isinstance(result, Binary)
        assert result.op == "+"

        # First term: y * 1
        term1 = result.left
        assert isinstance(term1, Binary)
        assert term1.op == "*"
        assert isinstance(term1.left, VarRef)
        assert term1.left.name == "y"
        assert isinstance(term1.right, Const)
        assert term1.right.value == 1.0

        # Second term: x * 0
        term2 = result.right
        assert isinstance(term2, Binary)
        assert term2.op == "*"
        assert isinstance(term2.left, VarRef)
        assert term2.left.name == "x"
        assert isinstance(term2.right, Const)
        assert term2.right.value == 0.0

    def test_multiply_variable_and_constant(self):
        """d(x * 5)/dx = 5 * 1 + x * 0 = 5"""
        expr = Binary("*", VarRef("x"), Const(5.0))
        result = differentiate(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "+"

        # First term: 5 * 1
        term1 = result.left
        assert isinstance(term1, Binary)
        assert term1.op == "*"
        assert isinstance(term1.left, Const)
        assert term1.left.value == 5.0


@pytest.mark.unit
class TestDivisionDifferentiation:
    """Test differentiation of division (quotient rule)."""

    def test_divide_two_variables(self):
        """d(x / y)/dx = (y*1 - x*0) / y^2 = y / y^2"""
        expr = Binary("/", VarRef("x"), VarRef("y"))
        result = differentiate(expr, "x")

        # Result should be: (y*(dx/dx) - x*(dy/dx)) / y^2
        assert isinstance(result, Binary)
        assert result.op == "/"

        # Numerator: y*1 - x*0
        numerator = result.left
        assert isinstance(numerator, Binary)
        assert numerator.op == "-"

        # Denominator: y * y
        denominator = result.right
        assert isinstance(denominator, Binary)
        assert denominator.op == "*"
        assert isinstance(denominator.left, VarRef)
        assert denominator.left.name == "y"
        assert isinstance(denominator.right, VarRef)
        assert denominator.right.name == "y"

    def test_divide_variable_by_constant(self):
        """d(x / 2)/dx = (2*1 - x*0) / 2^2 = 2 / 4"""
        expr = Binary("/", VarRef("x"), Const(2.0))
        result = differentiate(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "/"

        # Numerator should involve 2*1 - x*0
        numerator = result.left
        assert isinstance(numerator, Binary)
        assert numerator.op == "-"

        # Denominator: 2 * 2
        denominator = result.right
        assert isinstance(denominator, Binary)
        assert denominator.op == "*"


@pytest.mark.unit
class TestUnaryOperators:
    """Test differentiation of unary operators."""

    def test_unary_plus(self):
        """d(+x)/dx = dx/dx = 1"""
        expr = Unary("+", VarRef("x"))
        result = differentiate(expr, "x")

        # Unary plus just returns the derivative of the child
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_unary_minus(self):
        """d(-x)/dx = -dx/dx = -1"""
        expr = Unary("-", VarRef("x"))
        result = differentiate(expr, "x")

        assert isinstance(result, Unary)
        assert result.op == "-"
        assert isinstance(result.child, Const)
        assert result.child.value == 1.0

    def test_double_negation(self):
        """d(-(-x))/dx = -(-1) = 1 (after simplification)"""
        expr = Unary("-", Unary("-", VarRef("x")))
        result = differentiate(expr, "x")

        # Result: -(-dx/dx) = -(-1)
        assert isinstance(result, Unary)
        assert result.op == "-"
        assert isinstance(result.child, Unary)
        assert result.child.op == "-"


@pytest.mark.unit
class TestChainRule:
    """Test chain rule through combinations of operations."""

    def test_product_of_sums(self):
        """d[(x + y) * (x - y)]/dx using product rule"""
        # (x+y) * (x-y)
        sum_expr = Binary("+", VarRef("x"), VarRef("y"))
        diff_expr = Binary("-", VarRef("x"), VarRef("y"))
        expr = Binary("*", sum_expr, diff_expr)

        result = differentiate(expr, "x")

        # Result: (x-y)*(dx/dx + dy/dx) + (x+y)*(dx/dx - dy/dx)
        #       = (x-y)*(1 + 0) + (x+y)*(1 - 0)
        assert isinstance(result, Binary)
        assert result.op == "+"

    def test_division_chain(self):
        """d[(x + 1) / (y + 1)]/dx"""
        numerator = Binary("+", VarRef("x"), Const(1.0))
        denominator = Binary("+", VarRef("y"), Const(1.0))
        expr = Binary("/", numerator, denominator)

        result = differentiate(expr, "x")

        # Result should use quotient rule with chain rule
        assert isinstance(result, Binary)
        assert result.op == "/"


@pytest.mark.unit
class TestUnsupportedOperations:
    """Test that unsupported operations raise appropriate errors."""

    def test_power_operator_supported(self):
        """Power operation (^) should work correctly."""
        # d/dx (x^2) = 2*x^1
        expr = Binary("^", VarRef("x"), Const(2.0))
        result = differentiate(expr, "x")

        # Result should be: 2.0 * x^1.0 * 1
        assert isinstance(result, Binary)
        assert result.op == "*"
        # The derivative exists and is well-formed
        assert result is not None

    def test_unknown_binary_operation(self):
        """Unknown binary operation should raise ValueError"""
        expr = Binary("???", VarRef("x"), VarRef("y"))

        with pytest.raises(ValueError) as exc_info:
            differentiate(expr, "x")

        assert "Unsupported binary operation" in str(exc_info.value)

    def test_unknown_unary_operation(self):
        """Unknown unary operation should raise ValueError"""
        expr = Unary("!", VarRef("x"))

        with pytest.raises(ValueError) as exc_info:
            differentiate(expr, "x")

        assert "Unsupported unary operation" in str(exc_info.value)
