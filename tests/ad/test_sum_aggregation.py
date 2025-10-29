"""
Tests for sum aggregation differentiation.

Day 5: Tests for sum(indices, expr) derivatives.
"""

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, VarRef

# ============================================================================
# Basic Sum Differentiation Tests
# ============================================================================


class TestBasicSumDifferentiation:
    """Tests for basic sum aggregation differentiation."""

    def test_sum_of_indexed_variable(self):
        """Test d/dx sum(i, x(i)) = sum(i, 1)"""
        # sum(i, x(i))
        expr = Sum(("i",), VarRef("x", ("i",)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 1.0

    def test_sum_of_constant(self):
        """Test d/dx sum(i, 5) = sum(i, 0)"""
        # sum(i, 5)
        expr = Sum(("i",), Const(5.0))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_of_parameter(self):
        """Test d/dx sum(i, c) where c is a parameter = sum(i, 0)"""
        # sum(i, c)
        expr = Sum(("i",), ParamRef("c"))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_of_different_variable(self):
        """Test d/dx sum(i, y(i)) where y != x = sum(i, 0)"""
        # sum(i, y(i))
        expr = Sum(("i",), VarRef("y", ("i",)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0


# ============================================================================
# Sum with Arithmetic Operations
# ============================================================================


class TestSumWithArithmetic:
    """Tests for sum aggregation with arithmetic expressions."""

    def test_sum_of_product(self):
        """Test d/dx sum(i, c*x(i)) where c is parameter = sum(i, c*1 + x*0)"""
        # sum(i, c*x(i))
        expr = Sum(("i",), Binary("*", ParamRef("c"), VarRef("x", ("i",))))
        result = differentiate_expr(expr, "x")

        # Product rule: d/dx(c*x) = x*dc/dx + c*dx/dx = x*0 + c*1
        # Should be: sum(i, x(i)*0 + c*1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Left term should be x(i) * 0 (from x * dc/dx)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "*"
        assert isinstance(result.body.left.left, VarRef)
        assert result.body.left.left.name == "x"
        assert isinstance(result.body.left.right, Const)
        assert result.body.left.right.value == 0.0

        # Right term should be c * 1 (from c * dx/dx)
        assert isinstance(result.body.right, Binary)
        assert result.body.right.op == "*"
        assert isinstance(result.body.right.left, ParamRef)
        assert result.body.right.left.name == "c"
        assert isinstance(result.body.right.right, Const)
        assert result.body.right.right.value == 1.0

    def test_sum_of_addition(self):
        """Test d/dx sum(i, x(i) + y(i)) = sum(i, 1 + 0)"""
        # sum(i, x(i) + y(i))
        expr = Sum(("i",), Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",))))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 1 + 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Left should be 1, right should be 0
        assert isinstance(result.body.left, Const)
        assert result.body.left.value == 1.0
        assert isinstance(result.body.right, Const)
        assert result.body.right.value == 0.0

    def test_sum_of_power(self):
        """Test d/dx sum(i, x(i)^2) = sum(i, 2*x(i))"""
        # sum(i, x(i)^2)
        inner = Call("power", (VarRef("x", ("i",)), Const(2.0)))
        expr = Sum(("i",), inner)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 2*x(i)^1 * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"


# ============================================================================
# Multiple Indices
# ============================================================================


class TestMultipleIndices:
    """Tests for sum with multiple index variables."""

    def test_sum_two_indices(self):
        """Test d/dx sum((i,j), x(i,j)) = sum((i,j), 1)"""
        # sum((i,j), x(i,j))
        expr = Sum(("i", "j"), VarRef("x", ("i", "j")))
        result = differentiate_expr(expr, "x")

        # Should be: sum((i,j), 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i", "j")
        assert isinstance(result.body, Const)
        assert result.body.value == 1.0

    def test_sum_two_indices_with_product(self):
        """Test d/dx sum((i,j), a(i)*x(i,j)) = sum((i,j), a(i)*1 + x(i,j)*0)"""
        # sum((i,j), a(i)*x(i,j)) where a is parameter
        expr = Sum(("i", "j"), Binary("*", ParamRef("a", ("i",)), VarRef("x", ("i", "j"))))
        result = differentiate_expr(expr, "x")

        # Product rule: d/dx(a*x) = x*da/dx + a*dx/dx = x*0 + a*1
        # Should be: sum((i,j), x(i,j)*0 + a(i)*1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i", "j")
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Left term should be x(i,j) * 0 (from x * da/dx)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "*"
        assert isinstance(result.body.left.left, VarRef)
        assert result.body.left.left.name == "x"
        assert result.body.left.left.indices == ("i", "j")
        assert isinstance(result.body.left.right, Const)
        assert result.body.left.right.value == 0.0

        # Right term should be a(i) * 1 (from a * dx/dx)
        assert isinstance(result.body.right, Binary)
        assert result.body.right.op == "*"
        assert isinstance(result.body.right.left, ParamRef)
        assert result.body.right.left.name == "a"
        assert result.body.right.left.indices == ("i",)
        assert isinstance(result.body.right.right, Const)
        assert result.body.right.right.value == 1.0


# ============================================================================
# Nested Sums (Basic)
# ============================================================================


class TestNestedSums:
    """Tests for nested sum aggregations."""

    def test_nested_sum_simple(self):
        """Test d/dx sum(i, sum(j, x(i,j))) = sum(i, sum(j, 1))"""
        # sum(i, sum(j, x(i,j)))
        inner_sum = Sum(("j",), VarRef("x", ("i", "j")))
        expr = Sum(("i",), inner_sum)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, sum(j, 1))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Sum)
        assert result.body.index_sets == ("j",)
        assert isinstance(result.body.body, Const)
        assert result.body.body.value == 1.0

    def test_nested_sum_with_constant(self):
        """Test d/dx sum(i, sum(j, c)) = sum(i, sum(j, 0))"""
        # sum(i, sum(j, c))
        inner_sum = Sum(("j",), Const(5.0))
        expr = Sum(("i",), inner_sum)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, sum(j, 0))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Sum)
        assert result.body.index_sets == ("j",)
        assert isinstance(result.body.body, Const)
        assert result.body.body.value == 0.0


# ============================================================================
# Complex Expressions
# ============================================================================


class TestComplexSumExpressions:
    """Tests for complex expressions within sums."""

    def test_sum_of_exp(self):
        """Test d/dx sum(i, exp(x(i))) = sum(i, exp(x(i)))"""
        # sum(i, exp(x(i)))
        expr = Sum(("i",), Call("exp", (VarRef("x", ("i",)),)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, exp(x(i)) * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"

        # Left should be exp(x(i))
        assert isinstance(result.body.left, Call)
        assert result.body.left.func == "exp"

    def test_sum_of_log(self):
        """Test d/dx sum(i, log(x(i))) = sum(i, 1/x(i))"""
        # sum(i, log(x(i)))
        expr = Sum(("i",), Call("log", (VarRef("x", ("i",)),)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, (1/x(i)) * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"

        # Left should be 1/x(i)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "/"
