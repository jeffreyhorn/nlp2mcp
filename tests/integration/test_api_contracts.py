"""
API Contract Tests

These tests validate that API boundaries between modules remain stable.
They catch breaking changes like Issue #22 (gradient.mapping.num_vars → gradient.num_cols)
and Issue #24 (bounds storage location).

Contract tests are integration tests that:
- Verify public API attributes exist
- Check API consistency (e.g., num_cols == len(instances))
- Prevent regression of known issues
- Fail fast when APIs change

Run these tests first in CI to catch API violations immediately.
"""

from pathlib import Path

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.derivative_rules import differentiate_expr
from src.ad.gradient import compute_objective_gradient
from src.ir.ast import Const, VarRef
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file

pytestmark = pytest.mark.integration


# Helper to get example file paths
def get_example_path(filename: str) -> Path:
    """Get absolute path to example file."""
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root / "examples" / filename


@pytest.mark.integration
class TestSparseGradientContract:
    """Tests that validate SparseGradient API stays stable."""

    def test_sparse_gradient_has_num_cols(self):
        """SparseGradient must have num_cols attribute.

        Regression test for Issue #22: Tests assumed gradient.mapping.num_vars
        existed when correct API was gradient.num_cols.
        """
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        gradient = compute_objective_gradient(model)

        # API contract: gradient.num_cols must exist
        assert hasattr(gradient, "num_cols"), "SparseGradient must have num_cols attribute"
        assert isinstance(gradient.num_cols, int), "num_cols must be an integer"
        assert gradient.num_cols > 0, "num_cols must be positive"

    def test_sparse_gradient_has_entries(self):
        """GradientVector must have entries dict mapping col_id → Expr."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        gradient = compute_objective_gradient(model)

        assert hasattr(gradient, "entries"), "GradientVector must have entries attribute"
        assert isinstance(gradient.entries, dict), "entries must be a dict"

        # Entries should map int → Expr
        for col_id, expr in gradient.entries.items():
            assert isinstance(col_id, int), f"entries key must be int, got {type(col_id)}"
            # expr should be an AST node (we don't check specific type to allow flexibility)
            assert expr is not None, "entries must map to non-None expressions"

    def test_sparse_gradient_has_index_mapping(self):
        """GradientVector must have index_mapping attribute (IndexMapping)."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        gradient = compute_objective_gradient(model)

        assert hasattr(gradient, "index_mapping"), (
            "GradientVector must have index_mapping attribute"
        )
        # index_mapping should be IndexMapping with required attributes
        assert hasattr(gradient.index_mapping, "num_vars"), "index_mapping must have num_vars"
        assert hasattr(gradient.index_mapping, "var_to_col"), (
            "index_mapping must have var_to_col mapping"
        )
        assert hasattr(gradient.index_mapping, "col_to_var"), (
            "index_mapping must have col_to_var mapping"
        )

    def test_num_cols_matches_mapping_num_vars(self):
        """num_cols must equal index_mapping.num_vars.

        Regression test for Issue #22: Ensures consistency between
        gradient.num_cols and gradient.index_mapping.num_vars.
        """
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        gradient = compute_objective_gradient(model)

        # These must be consistent
        assert gradient.num_cols == gradient.index_mapping.num_vars, (
            "num_cols must match number of variables in index_mapping"
        )

    def test_sparse_gradient_has_get_derivative_methods(self):
        """GradientVector must have get_derivative and get_derivative_by_name methods."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        gradient = compute_objective_gradient(model)

        assert hasattr(gradient, "get_derivative"), "GradientVector must have get_derivative method"
        assert hasattr(gradient, "get_derivative_by_name"), (
            "GradientVector must have get_derivative_by_name method"
        )
        assert callable(gradient.get_derivative), "get_derivative must be callable"
        assert callable(gradient.get_derivative_by_name), "get_derivative_by_name must be callable"


@pytest.mark.integration
class TestJacobianStructureContract:
    """Tests that validate JacobianStructure API stays stable."""

    def test_jacobian_structure_has_dimensions(self):
        """JacobianStructure must have num_rows and num_cols attributes."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)

        # Test equality Jacobian
        assert hasattr(j_eq, "num_rows"), "JacobianStructure must have num_rows"
        assert hasattr(j_eq, "num_cols"), "JacobianStructure must have num_cols"
        assert isinstance(j_eq.num_rows, int), "num_rows must be int"
        assert isinstance(j_eq.num_cols, int), "num_cols must be int"
        assert j_eq.num_rows >= 0, "num_rows must be non-negative"
        assert j_eq.num_cols > 0, "num_cols must be positive"

    def test_jacobian_structure_has_entries(self):
        """JacobianStructure entries must be dict[int, dict[int, Expr]]."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)

        assert hasattr(j_ineq, "entries"), "JacobianStructure must have entries"
        assert isinstance(j_ineq.entries, dict), "entries must be dict"

        # Keys should be row IDs (int), values should be dict of col_id → Expr
        for row_id, row_entries in j_ineq.entries.items():
            assert isinstance(row_id, int), f"entries key must be int (row_id), got {type(row_id)}"
            assert isinstance(row_entries, dict), (
                f"entries value must be dict, got {type(row_entries)}"
            )
            for col_id, expr in row_entries.items():
                assert isinstance(col_id, int), f"col_id must be int, got {type(col_id)}"
                assert expr is not None, "expr must not be None"

    def test_jacobian_structure_has_index_mapping(self):
        """JacobianStructure must have index_mapping attribute."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)

        assert hasattr(j_ineq, "index_mapping"), (
            "JacobianStructure must have index_mapping attribute"
        )
        # index_mapping should have methods to look up equations and variables
        assert hasattr(j_ineq.index_mapping, "get_eq_instance"), (
            "index_mapping must have get_eq_instance"
        )
        assert hasattr(j_ineq.index_mapping, "get_var_instance"), (
            "index_mapping must have get_var_instance"
        )

    def test_jacobian_structure_has_get_derivative_methods(self):
        """JacobianStructure must have get_derivative and get_derivative_by_names methods."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)

        assert hasattr(j_ineq, "get_derivative"), (
            "JacobianStructure must have get_derivative method"
        )
        assert hasattr(j_ineq, "get_derivative_by_names"), (
            "JacobianStructure must have get_derivative_by_names method"
        )
        assert callable(j_ineq.get_derivative), "get_derivative must be callable"
        assert callable(j_ineq.get_derivative_by_names), "get_derivative_by_names must be callable"


@pytest.mark.integration
class TestModelIRContract:
    """Tests that validate ModelIR structure from Sprint 1."""

    def test_model_ir_has_required_fields(self):
        """ModelIR must have all expected fields from Sprint 1."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)

        # Required fields from Sprint 1
        assert hasattr(model, "equations"), "ModelIR must have equations"
        assert hasattr(model, "normalized_bounds"), "ModelIR must have normalized_bounds"
        assert hasattr(model, "inequalities"), "ModelIR must have inequalities"
        assert hasattr(model, "sets"), "ModelIR must have sets"
        assert hasattr(model, "variables"), "ModelIR must have variables"

        # Check types
        assert isinstance(model.equations, dict), "equations must be dict"
        assert isinstance(model.normalized_bounds, dict), "normalized_bounds must be dict"
        assert isinstance(model.inequalities, list), "inequalities must be list"
        assert isinstance(model.sets, dict), "sets must be dict"
        assert isinstance(model.variables, dict), "variables must be dict"

    def test_bounds_not_in_equations(self):
        """Regression test for Issue #24: bounds are stored separately.

        Bounds should be in normalized_bounds dict, NOT in equations dict.
        They are listed in inequalities list for convenience.
        """
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)

        # Bounds should NOT be in equations dict
        for bound_name in model.normalized_bounds.keys():
            # Bound names like 'x_lo', 'x_up', 'x_lo(i1)' should NOT be in equations
            assert bound_name not in model.equations, (
                f"Bound {bound_name} should not be in equations dict (Issue #24)"
            )

    def test_bounds_in_inequalities_list(self):
        """Bounds should appear in inequalities list for iteration convenience."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)

        if not model.normalized_bounds:
            pytest.skip("No bounds in this model")

        # Every bound should be in inequalities list
        for bound_name in model.normalized_bounds.keys():
            assert bound_name in model.inequalities, (
                f"Bound {bound_name} should be in inequalities list"
            )

    def test_model_ir_has_objective(self):
        """ModelIR must have objective field."""
        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)

        assert hasattr(model, "objective"), "ModelIR must have objective"
        assert model.objective is not None, "objective should not be None for models with solve"

        # Objective should have required fields
        assert hasattr(model.objective, "objvar"), "objective must have objvar"
        assert hasattr(model.objective, "sense"), "objective must have sense"
        assert hasattr(model.objective, "expr"), "objective must have expr"


@pytest.mark.integration
class TestDifferentiationAPIContract:
    """Tests for differentiate_expr API signature."""

    def test_differentiate_accepts_wrt_indices(self):
        """differentiate_expr must accept wrt_indices parameter.

        Sprint 2 Day 7.5 added index-aware differentiation with wrt_indices parameter.
        This test ensures the API remains stable.
        """
        expr = VarRef("x", ("i1",))

        # Should accept wrt_indices parameter (Sprint 2 Day 7.5)
        result = differentiate_expr(expr, "x", wrt_indices=("i1",))
        assert result == Const(1.0), "d/dx(i1) x(i1) should be 1 when indices match"

        # Should also work without wrt_indices (backward compat)
        result_compat = differentiate_expr(expr, "x")
        assert isinstance(result_compat, Const), "Should return Const when compatible"

    def test_differentiate_returns_zero_for_index_mismatch(self):
        """differentiate_expr should return Const(0) when indices don't match.

        This is the key behavior for sparse Jacobian computation.
        """
        expr = VarRef("x", ("i1",))

        # Differentiate w.r.t. x(i2) - different index
        result = differentiate_expr(expr, "x", wrt_indices=("i2",))
        assert result == Const(0.0), "d/dx(i2) of x(i1) should be 0 (different indices)"

    def test_differentiate_wrt_indices_must_be_tuple(self):
        """wrt_indices parameter must be tuple, not string.

        Common mistake: passing "i" instead of ("i",).
        """
        expr = VarRef("x", ("i",))

        # Correct: tuple
        result = differentiate_expr(expr, "x", wrt_indices=("i",))
        assert result == Const(1.0)

        # Test that we handle None gracefully
        result_none = differentiate_expr(expr, "x", wrt_indices=None)
        assert isinstance(result_none, Const)


@pytest.mark.integration
class TestHighLevelAPIContract:
    """Tests for high-level API functions from src.ad.api module."""

    def test_compute_derivatives_returns_triple(self):
        """compute_derivatives must return (gradient, J_eq, J_ineq) triple."""
        from src.ad.api import compute_derivatives

        model = parse_model_file(get_example_path("simple_nlp.gms"))
        normalize_model(model)

        result = compute_derivatives(model)

        # Should return a tuple of 3 elements
        assert isinstance(result, tuple), "compute_derivatives must return tuple"
        assert len(result) == 3, "compute_derivatives must return 3-tuple"

        gradient, j_eq, j_ineq = result

        # Each should have the expected contract
        assert hasattr(gradient, "num_cols"), "gradient must have num_cols"
        assert hasattr(j_eq, "num_rows"), "J_eq must have num_rows"
        assert hasattr(j_ineq, "num_rows"), "J_ineq must have num_rows"
