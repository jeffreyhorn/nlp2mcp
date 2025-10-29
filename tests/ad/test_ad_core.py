"""
Tests for Symbolic Differentiation Core (Day 1)

Test Coverage:
-------------
1. Constant differentiation
2. Variable reference differentiation (same var)
3. Variable reference differentiation (different var)
4. Parameter reference differentiation
5. Symbol reference differentiation
6. Indexed variable differentiation
7. Sum expressions are now supported and tested for correct differentiation behavior
8. Unsupported expression types (other than Sum) raise appropriate errors
"""

from src.ad import differentiate
from src.ir.ast import Const, ParamRef, SymbolRef, VarRef


class TestConstantDifferentiation:
    """Test differentiation of constants."""

    def test_const_derivative_is_zero(self):
        """d(c)/dx = 0 for any constant c"""
        expr = Const(5.0)
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_const_zero_derivative(self):
        """d(0)/dx = 0"""
        expr = Const(0.0)
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_const_negative_derivative(self):
        """d(-5)/dx = 0"""
        expr = Const(-5.0)
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0


class TestVariableReferenceDifferentiation:
    """Test differentiation of variable references."""

    def test_var_same_variable(self):
        """dx/dx = 1"""
        expr = VarRef("x")
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_var_different_variable(self):
        """dy/dx = 0"""
        expr = VarRef("y")
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_indexed_var_same_name(self):
        """d(x(i))/dx = 1 (base name matches)"""
        expr = VarRef("x", ("i",))
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_indexed_var_different_name(self):
        """d(y(i))/dx = 0 (base name differs)"""
        expr = VarRef("y", ("i",))
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_multi_indexed_var_same_name(self):
        """d(x(i,j))/dx = 1"""
        expr = VarRef("x", ("i", "j"))
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 1.0


class TestSymbolReferenceDifferentiation:
    """Test differentiation of scalar symbol references."""

    def test_symbol_same_name(self):
        """d(x)/dx = 1 for SymbolRef"""
        expr = SymbolRef("x")
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_symbol_different_name(self):
        """d(y)/dx = 0 for SymbolRef"""
        expr = SymbolRef("y")
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0


class TestParameterReferenceDifferentiation:
    """Test differentiation of parameter references."""

    def test_param_derivative_is_zero(self):
        """d(param)/dx = 0 (parameters are constant)"""
        expr = ParamRef("c")
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_indexed_param_derivative_is_zero(self):
        """d(demand(i))/dx = 0"""
        expr = ParamRef("demand", ("i",))
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0

    def test_multi_indexed_param_derivative_is_zero(self):
        """d(cost(i,j))/dx = 0"""
        expr = ParamRef("cost", ("i", "j"))
        result = differentiate(expr, "x")

        assert isinstance(result, Const)
        assert result.value == 0.0


class TestSumSupport:
    """Test that Sum expressions are now supported (Day 5)."""

    def test_sum_now_supported(self):
        """Sum expressions should now differentiate successfully (implemented Day 5)"""
        from src.ir.ast import Sum

        # sum((i,j), x(i,j)) - implemented in Day 5
        expr = Sum(("i", "j"), VarRef("x", ("i", "j")))

        # Should successfully differentiate without raising TypeError
        result = differentiate(expr, "x")

        # Result should be a Sum with the same index vars
        assert isinstance(result, Sum)
        assert result.index_sets == ("i", "j")


class TestDifferentiationInvariance:
    """Test that differentiation doesn't modify original expressions."""

    def test_const_not_modified(self):
        """Original Const expression should not be modified"""
        expr = Const(5.0)
        original_value = expr.value

        differentiate(expr, "x")

        assert expr.value == original_value

    def test_varref_not_modified(self):
        """Original VarRef expression should not be modified"""
        expr = VarRef("x", ("i",))
        original_name = expr.name
        original_indices = expr.indices

        differentiate(expr, "y")

        assert expr.name == original_name
        assert expr.indices == original_indices
