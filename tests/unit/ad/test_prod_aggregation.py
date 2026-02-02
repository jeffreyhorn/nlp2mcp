"""
Tests for prod aggregation differentiation.

Sprint 17 Day 6: Tests for prod(indices, expr) derivatives using
logarithmic derivative approach.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, ParamRef, Prod, Sum, VarRef

pytestmark = pytest.mark.unit

# ============================================================================
# Basic Prod Differentiation Tests
# ============================================================================


@pytest.mark.unit
class TestBasicProdDifferentiation:
    """Tests for basic prod aggregation differentiation."""

    def test_prod_of_indexed_variable(self):
        """Test d/dx prod(i, x(i)) = prod(i, x(i)) * sum(i, 1/x(i) * 0) when x is scalar.

        Since x(i) doesn't match scalar x, body derivative is 0, so result is 0.
        """
        # prod(i, x(i))
        expr = Prod(("i",), VarRef("x", ("i",)))
        result = differentiate_expr(expr, "x")

        # Body derivative is 0 (x(i) doesn't match scalar x), so full derivative is 0
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_of_constant(self):
        """Test d/dx prod(i, 5) = 0 (constant body)."""
        # prod(i, 5)
        expr = Prod(("i",), Const(5.0))
        result = differentiate_expr(expr, "x")

        # Constant body has zero derivative
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_of_parameter(self):
        """Test d/dx prod(i, c) where c is a parameter = 0."""
        # prod(i, c)
        expr = Prod(("i",), ParamRef("c"))
        result = differentiate_expr(expr, "x")

        # Parameter derivative is 0
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_of_different_variable(self):
        """Test d/dx prod(i, y(i)) where y != x = 0."""
        # prod(i, y(i))
        expr = Prod(("i",), VarRef("y", ("i",)))
        result = differentiate_expr(expr, "x")

        # Different variable has zero derivative
        assert isinstance(result, Const)
        assert result.value == 0.0


# ============================================================================
# Prod with Non-Zero Derivatives
# ============================================================================


@pytest.mark.unit
class TestProdNonZeroDerivatives:
    """Tests where the prod body actually depends on the differentiation variable."""

    def test_prod_of_scalar_variable(self):
        """Test d/dx prod(i, x) = prod(i, x) * sum(i, 1/x).

        Here x is a scalar (no indices), so dx/dx = 1.
        Result: prod(i, x) * sum(i, 1/x * 1)
        """
        # prod(i, x) where x is scalar
        expr = Prod(("i",), VarRef("x", ()))
        result = differentiate_expr(expr, "x")

        # Should be: prod(i, x) * sum(i, 1/x)
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should be the original prod
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i",)
        assert isinstance(result.left.body, VarRef)
        assert result.left.body.name == "x"

        # Right should be sum(i, 1/x * 1) = sum(i, 1/x)
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i",)

    def test_prod_with_addition_in_body(self):
        """Test d/dx prod(i, x + c) where x is scalar, c is constant.

        d/dx (x + c) = 1, so result is prod(i, x+c) * sum(i, 1/(x+c))
        """
        # prod(i, x + 5)
        body = Binary("+", VarRef("x", ()), Const(5.0))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        # Should be: prod(i, x+5) * sum(i, (1+0)/(x+5))
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left is original prod
        assert isinstance(result.left, Prod)

        # Right is sum with body derivative
        assert isinstance(result.right, Sum)


# ============================================================================
# Prod with Arithmetic Operations
# ============================================================================


@pytest.mark.unit
class TestProdWithArithmetic:
    """Tests for prod aggregation with arithmetic expressions in body."""

    def test_prod_of_product_body(self):
        """Test d/dx prod(i, c*x) where c is parameter, x is scalar.

        Body derivative: d/dx(c*x) = c (product rule: x*0 + c*1)
        Result: prod(i, c*x) * sum(i, c / (c*x))
        """
        # prod(i, c*x)
        body = Binary("*", ParamRef("c"), VarRef("x", ()))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        # Should be: prod(i, c*x) * sum(i, body_derivative / body)
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left is original prod
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i",)

        # Right is sum of (derivative / body)
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i",)
        assert isinstance(result.right.body, Binary)
        assert result.right.body.op == "/"

    def test_prod_of_power(self):
        """Test d/dx prod(i, x^2) where x is scalar.

        Body derivative: d/dx(x^2) = 2*x
        Result: prod(i, x^2) * sum(i, 2*x / x^2) = prod(i, x^2) * sum(i, 2/x)
        """
        # prod(i, x^2)
        body = Call("power", (VarRef("x", ()), Const(2.0)))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        # Should be: prod(i, x^2) * sum(i, derivative / x^2)
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left is original prod
        assert isinstance(result.left, Prod)

        # Right is sum with logarithmic derivative body
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i",)


# ============================================================================
# Multiple Indices
# ============================================================================


@pytest.mark.unit
class TestProdMultipleIndices:
    """Tests for prod with multiple index variables."""

    def test_prod_two_indices_constant_body(self):
        """Test d/dx prod((i,j), 5) = 0."""
        # prod((i,j), 5)
        expr = Prod(("i", "j"), Const(5.0))
        result = differentiate_expr(expr, "x")

        # Constant body has zero derivative
        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_two_indices_scalar_variable(self):
        """Test d/dx prod((i,j), x) where x is scalar.

        Result: prod((i,j), x) * sum((i,j), 1/x)
        """
        # prod((i,j), x)
        expr = Prod(("i", "j"), VarRef("x", ()))
        result = differentiate_expr(expr, "x")

        # Should be: prod * sum with two indices
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left should preserve both indices
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i", "j")

        # Right sum should have both indices
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i", "j")

    def test_prod_two_indices_with_indexed_param(self):
        """Test d/dx prod((i,j), a(i)*x) where a is parameter, x is scalar.

        Result: prod * sum((i,j), a(i) / (a(i)*x))
        """
        # prod((i,j), a(i)*x)
        body = Binary("*", ParamRef("a", ("i",)), VarRef("x", ()))
        expr = Prod(("i", "j"), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"

        # Both prod and sum should have (i, j) indices
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i", "j")
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i", "j")


# ============================================================================
# Cobb-Douglas Form (Common in CGE Models)
# ============================================================================


@pytest.mark.unit
class TestCobbDouglasForm:
    """Tests for Cobb-Douglas style expressions: prod(i, x(i)^alpha(i))."""

    def test_cobb_douglas_constant_exponent(self):
        """Test d/dx prod(i, x^alpha) where x is scalar and alpha is constant.

        This is: prod(i, x^alpha)
        d/dx(x^alpha) = alpha * x^(alpha-1)
        Result: prod(i, x^alpha) * sum(i, alpha*x^(alpha-1) / x^alpha)
              = prod(i, x^alpha) * sum(i, alpha/x)
        """
        # prod(i, x^2)
        body = Call("power", (VarRef("x", ()), Const(2.0)))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert isinstance(result.right, Sum)

    def test_cobb_douglas_parameter_exponent(self):
        """Test d/dx prod(i, x^alpha(i)) where x is scalar and alpha is parameter.

        Body: x^alpha(i)
        d/dx(x^alpha(i)) = alpha(i) * x^(alpha(i)-1) (power rule)
        Result: prod(i, x^alpha(i)) * sum(i, alpha(i)/x)
        """
        # prod(i, x^alpha(i))
        body = Call("power", (VarRef("x", ()), ParamRef("alpha", ("i",))))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"

        # Prod preserved
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i",)

        # Sum with logarithmic derivative
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i",)


# ============================================================================
# Complex Expressions
# ============================================================================


@pytest.mark.unit
class TestComplexProdExpressions:
    """Tests for complex expressions within prod."""

    def test_prod_of_exp(self):
        """Test d/dx prod(i, exp(x)) where x is scalar.

        d/dx(exp(x)) = exp(x)
        Result: prod(i, exp(x)) * sum(i, exp(x)/exp(x)) = prod(i, exp(x)) * sum(i, 1)
        """
        # prod(i, exp(x))
        body = Call("exp", (VarRef("x", ()),))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert isinstance(result.right, Sum)

    def test_prod_of_log(self):
        """Test d/dx prod(i, log(x)) where x is scalar.

        d/dx(log(x)) = 1/x
        Result: prod(i, log(x)) * sum(i, (1/x) / log(x))
        """
        # prod(i, log(x))
        body = Call("log", (VarRef("x", ()),))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert isinstance(result.right, Sum)

    def test_prod_of_nested_expression(self):
        """Test d/dx prod(i, (x + c)^2) where x is scalar, c is constant.

        Body: (x+c)^2
        d/dx((x+c)^2) = 2*(x+c)^1 * 1 = 2*(x+c)
        Result: prod(i, (x+c)^2) * sum(i, 2*(x+c) / (x+c)^2)
        """
        # prod(i, (x+c)^2)
        inner = Binary("+", VarRef("x", ()), Const(3.0))
        body = Call("power", (inner, Const(2.0)))
        expr = Prod(("i",), body)
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert isinstance(result.right, Sum)


# ============================================================================
# Nested Prod and Sum
# ============================================================================


@pytest.mark.unit
class TestNestedProdSum:
    """Tests for nested prod and sum expressions."""

    def test_prod_of_sum(self):
        """Test d/dx prod(i, sum(j, x)) where x is scalar.

        Inner sum: sum(j, x) has derivative sum(j, 1)
        Outer prod uses logarithmic derivative
        """
        # prod(i, sum(j, x))
        inner_sum = Sum(("j",), VarRef("x", ()))
        expr = Prod(("i",), inner_sum)
        result = differentiate_expr(expr, "x")

        # Should get: prod(i, sum(j, x)) * sum(i, sum(j, 1) / sum(j, x))
        assert isinstance(result, Binary)
        assert result.op == "*"

        # Left is original prod
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i",)
        assert isinstance(result.left.body, Sum)

        # Right is sum with logarithmic derivative
        assert isinstance(result.right, Sum)

    def test_sum_of_prod(self):
        """Test d/dx sum(i, prod(j, x)) where x is scalar.

        Inner prod has derivative via logarithmic approach
        Outer sum just preserves the sum structure
        """
        # sum(i, prod(j, x))
        inner_prod = Prod(("j",), VarRef("x", ()))
        expr = Sum(("i",), inner_prod)
        result = differentiate_expr(expr, "x")

        # Should get: sum(i, prod(j, x) * sum(j, 1/x))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)

        # Body should be the product derivative
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"


# ============================================================================
# Edge Cases
# ============================================================================


@pytest.mark.unit
class TestProdEdgeCases:
    """Edge case tests for prod differentiation."""

    def test_prod_with_zero_in_body(self):
        """Test prod where body contains explicit zero - derivative is 0."""
        # prod(i, 0)
        expr = Prod(("i",), Const(0.0))
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_with_one_in_body(self):
        """Test prod(i, 1) - derivative is 0 since constant."""
        # prod(i, 1)
        expr = Prod(("i",), Const(1.0))
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_prod_single_index(self):
        """Test prod with a single index produces correct structure."""
        # prod(i, x)
        expr = Prod(("i",), VarRef("x", ()))
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert len(result.left.index_sets) == 1
        assert isinstance(result.right, Sum)
        assert len(result.right.index_sets) == 1

    def test_prod_three_indices(self):
        """Test prod with three indices."""
        # prod((i,j,k), x)
        expr = Prod(("i", "j", "k"), VarRef("x", ()))
        result = differentiate_expr(expr, "x")

        assert isinstance(result, Binary)
        assert result.op == "*"
        assert isinstance(result.left, Prod)
        assert result.left.index_sets == ("i", "j", "k")
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("i", "j", "k")
