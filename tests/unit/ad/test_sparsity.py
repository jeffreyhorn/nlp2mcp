"""
Tests for Sparsity Tracking (Day 6)

Test Coverage:
-------------
1. Finding variables in simple expressions
2. Finding variables in complex expressions
3. Finding variables in sum aggregations
4. Sparsity pattern construction
5. Row/column dependency queries
6. Density computation
"""

import pytest

from src.ad.sparsity import (
    SparsityPattern,
    analyze_expression_sparsity,
    find_variables_in_expr,
)
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, SymbolRef, Unary, VarRef

pytestmark = pytest.mark.unit

# ============================================================================
# Test Variable Finding in Expressions
# ============================================================================


@pytest.mark.unit
class TestFindVariables:
    """Test finding variable names in expressions."""

    def test_constant_has_no_variables(self):
        """Test constant expression has no variables."""
        expr = Const(5.0)
        variables = find_variables_in_expr(expr)
        assert variables == set()

    def test_single_variable(self):
        """Test single variable reference."""
        expr = VarRef("x")
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_indexed_variable(self):
        """Test indexed variable (indices ignored, only base name)."""
        expr = VarRef("x", ("i",))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_multi_indexed_variable(self):
        """Test multi-indexed variable."""
        expr = VarRef("x", ("i", "j"))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_symbol_reference(self):
        """Test symbol reference treated as variable."""
        expr = SymbolRef("x")
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_parameter_has_no_variables(self):
        """Test parameter is not treated as variable."""
        expr = ParamRef("c")
        variables = find_variables_in_expr(expr)
        assert variables == set()

    def test_binary_addition(self):
        """Test binary addition with two variables."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        variables = find_variables_in_expr(expr)
        assert variables == {"x", "y"}

    def test_binary_with_constant(self):
        """Test binary operation with variable and constant."""
        expr = Binary("*", VarRef("x"), Const(2.0))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_binary_with_parameter(self):
        """Test binary operation with variable and parameter."""
        expr = Binary("*", ParamRef("c"), VarRef("x"))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_unary_operation(self):
        """Test unary operation."""
        expr = Unary("-", VarRef("x"))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_function_call_single_arg(self):
        """Test function call with single argument."""
        expr = Call("exp", (VarRef("x"),))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_function_call_multiple_args(self):
        """Test function call with multiple arguments."""
        expr = Call("power", (VarRef("x"), VarRef("y")))
        variables = find_variables_in_expr(expr)
        assert variables == {"x", "y"}

    def test_sum_aggregation(self):
        """Test sum aggregation."""
        expr = Sum(("i",), VarRef("x", ("i",)))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_nested_sum(self):
        """Test nested sum aggregation."""
        inner = Sum(("j",), VarRef("y", ("i", "j")))
        expr = Sum(("i",), inner)
        variables = find_variables_in_expr(expr)
        assert variables == {"y"}

    def test_complex_expression(self):
        """Test complex expression with multiple variables."""
        # (x + y) * exp(z)
        sum_expr = Binary("+", VarRef("x"), VarRef("y"))
        exp_expr = Call("exp", (VarRef("z"),))
        expr = Binary("*", sum_expr, exp_expr)

        variables = find_variables_in_expr(expr)
        assert variables == {"x", "y", "z"}

    def test_same_variable_multiple_times(self):
        """Test variable appearing multiple times (counted once)."""
        # x + x
        expr = Binary("+", VarRef("x"), VarRef("x"))
        variables = find_variables_in_expr(expr)
        assert variables == {"x"}

    def test_sum_with_multiple_variables(self):
        """Test sum body with multiple variables."""
        # sum(i, x(i) * y(i))
        body = Binary("*", VarRef("x", ("i",)), VarRef("y", ("i",)))
        expr = Sum(("i",), body)

        variables = find_variables_in_expr(expr)
        assert variables == {"x", "y"}


# ============================================================================
# Test Expression Sparsity Analysis
# ============================================================================


@pytest.mark.unit
class TestExpressionSparsityAnalysis:
    """Test analyzing which columns an expression depends on."""

    def test_single_variable_sparsity(self):
        """Test expression with single variable."""
        expr = VarRef("x")
        var_names_to_col_ids = {"x": [0], "y": [1]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        assert col_ids == {0}

    def test_multiple_variables_sparsity(self):
        """Test expression with multiple variables."""
        expr = Binary("+", VarRef("x"), VarRef("y"))
        var_names_to_col_ids = {"x": [0], "y": [1], "z": [2]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        assert col_ids == {0, 1}

    def test_indexed_variable_all_instances(self):
        """Test indexed variable includes all column instances."""
        expr = VarRef("x", ("i",))  # Could be any instance
        var_names_to_col_ids = {"x": [0, 1, 2], "y": [3]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        # All instances of x
        assert col_ids == {0, 1, 2}

    def test_sum_with_indexed_variable(self):
        """Test sum includes all instances of indexed variable."""
        # sum(i, x(i))
        expr = Sum(("i",), VarRef("x", ("i",)))
        var_names_to_col_ids = {"x": [0, 1, 2]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        assert col_ids == {0, 1, 2}

    def test_constant_expression_no_dependencies(self):
        """Test constant expression has no variable dependencies."""
        expr = Const(5.0)
        var_names_to_col_ids = {"x": [0], "y": [1]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        assert col_ids == set()

    def test_variable_not_in_mapping(self):
        """Test variable not in mapping is ignored."""
        expr = VarRef("z")  # z not in mapping
        var_names_to_col_ids = {"x": [0], "y": [1]}

        col_ids = analyze_expression_sparsity(expr, var_names_to_col_ids)

        assert col_ids == set()


# ============================================================================
# Test Sparsity Pattern
# ============================================================================


@pytest.mark.unit
class TestSparsityPattern:
    """Test sparsity pattern data structure."""

    def test_empty_pattern(self):
        """Test empty sparsity pattern."""
        pattern = SparsityPattern()

        assert pattern.num_nonzeros() == 0
        assert pattern.density(10, 10) == 0.0

    def test_add_single_dependency(self):
        """Test adding single dependency."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)

        assert pattern.num_nonzeros() == 1
        assert (0, 0) in pattern.nonzero_entries
        assert pattern.get_row_nonzeros(0) == {0}
        assert pattern.get_col_nonzeros(0) == {0}

    def test_add_multiple_dependencies(self):
        """Test adding multiple dependencies."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)
        pattern.add_dependency(0, 1)
        pattern.add_dependency(1, 0)

        assert pattern.num_nonzeros() == 3
        assert pattern.get_row_nonzeros(0) == {0, 1}
        assert pattern.get_row_nonzeros(1) == {0}
        assert pattern.get_col_nonzeros(0) == {0, 1}
        assert pattern.get_col_nonzeros(1) == {0}

    def test_add_duplicate_dependency(self):
        """Test adding same dependency twice (should not duplicate)."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)
        pattern.add_dependency(0, 0)

        assert pattern.num_nonzeros() == 1

    def test_density_calculation(self):
        """Test density calculation."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)
        pattern.add_dependency(0, 1)
        pattern.add_dependency(1, 0)

        # 3 nonzeros out of 2x3=6 total
        density = pattern.density(2, 3)
        assert density == 0.5

    def test_density_zero_dimensions(self):
        """Test density with zero dimensions."""
        pattern = SparsityPattern()
        assert pattern.density(0, 0) == 0.0

    def test_get_nonzeros_empty_row(self):
        """Test getting nonzeros from empty row."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)

        assert pattern.get_row_nonzeros(1) == set()

    def test_get_nonzeros_empty_col(self):
        """Test getting nonzeros from empty column."""
        pattern = SparsityPattern()
        pattern.add_dependency(0, 0)

        assert pattern.get_col_nonzeros(1) == set()

    def test_full_dense_pattern(self):
        """Test fully dense pattern."""
        pattern = SparsityPattern()
        for i in range(3):
            for j in range(3):
                pattern.add_dependency(i, j)

        assert pattern.num_nonzeros() == 9
        assert pattern.density(3, 3) == 1.0

    def test_diagonal_pattern(self):
        """Test diagonal sparsity pattern."""
        pattern = SparsityPattern()
        for i in range(3):
            pattern.add_dependency(i, i)

        assert pattern.num_nonzeros() == 3
        assert pattern.density(3, 3) == 3 / 9

        # Each row/col should have exactly one nonzero
        for i in range(3):
            assert pattern.get_row_nonzeros(i) == {i}
            assert pattern.get_col_nonzeros(i) == {i}
