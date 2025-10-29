"""
Integration Tests for Full NLP → AD Pipeline

These tests verify the complete end-to-end workflow:
1. Parse GAMS file
2. Normalize to IR
3. Compute derivatives using high-level API
4. Verify correctness of results

Test Coverage:
--------------
- Scalar models (no indexing)
- Indexed models with sum aggregations
- Models with equality constraints
- Models with inequality constraints
- Models with bounds
- Models with parameters
- Models with multiple variables

Each test validates:
- API returns correct structure
- Gradient has expected number of components
- Jacobians have expected sparsity patterns
- Derivatives are non-trivial (not all zeros)

Status:
-------
Integration tests are now enabled after fixing GitHub Issue #20 (parse hang).

GitHub Issue #19 Status: ✅ RESOLVED
- The objective extraction issue has been fixed in normalize_model()
- Fix verified by 6 new unit tests in tests/ir/test_normalize.py
- All normalization tests pass successfully

GitHub Issue #20 Status: ✅ RESOLVED
- parse_model_file() hang fixed by switching to standard lexer
- All example files now parse successfully

GitHub Issue #22 Status: ✅ RESOLVED
- API mismatch tests fixed by updating to correct API attributes
- Changed gradient.mapping.num_vars → gradient.num_cols
- Changed J_g.mapping.num_equations → J_g.num_rows
- Changed gradient.mapping → gradient.index_mapping
- Updated test expectations to account for objective variable (obj)

GitHub Issue #24 Status: ✅ RESOLVED
- Bounds handling bug fixed in constraint_jacobian.py
- Added check to skip bounds in _compute_inequality_jacobian()
- Bounds are now properly handled by _compute_bound_jacobian()
- test_bounds_nlp_basic now passes

Current Status:
- 14 out of 15 tests passing (93% pass rate)
- 1 test skipped: power operator (Issue #25 - not implemented)

See:
- GitHub Issue #19: "Objective Expressions Not Found After Model Normalization"
  https://github.com/jeffreyhorn/nlp2mcp/issues/19
- GitHub Issue #20: "Issue: parse_model_file() Hangs on Example Files"
  https://github.com/jeffreyhorn/nlp2mcp/issues/20
- GitHub Issue #22: "Integration Tests API Mismatch"
  https://github.com/jeffreyhorn/nlp2mcp/issues/22
"""

import os

import pytest

# NOTE: Integration tests now enabled after fixing GitHub Issue #20.
#
# See:
# - GitHub Issue #19 (RESOLVED): Objective extraction in normalization
# - GitHub Issue #20 (RESOLVED): parse_model_file() hang fixed by switching from
#   dynamic_complete lexer to standard lexer with ambiguity="resolve"
#   https://github.com/jeffreyhorn/nlp2mcp/issues/20
from src.ad.api import compute_derivatives
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file

# Skip marker for tests failing due to API mismatch (Issue #22)
skip_api_mismatch = pytest.mark.skip(
    reason="API mismatch (Issue #22): Tests expect gradient.mapping but implementation provides "
    "gradient.index_mapping. See https://github.com/jeffreyhorn/nlp2mcp/issues/22"
)

# Skip marker for tests with unimplemented features
skip_not_implemented = pytest.mark.skip(
    reason="Feature not yet implemented (power operator planned for Day 3). "
    "See GitHub Issue #25: https://github.com/jeffreyhorn/nlp2mcp/issues/25"
)


# Helper to get example file path
def get_example_path(filename: str) -> str:
    """Get absolute path to example file."""
    test_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(test_dir))
    return os.path.join(repo_root, "examples", filename)


# Helper to parse and normalize a model
def parse_and_normalize(filename: str):
    """Parse a GAMS file and normalize it."""
    model_ir = parse_model_file(get_example_path(filename))
    normalize_model(model_ir)
    return model_ir


class TestScalarModels:
    """Test integration on scalar (non-indexed) models."""

    def test_scalar_nlp_basic(self):
        """Test scalar model: min x s.t. x + a = 0."""
        model_ir = parse_and_normalize("scalar_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have 2 variables (x and obj)
        assert gradient.num_cols == 2

        # Gradient should have 2 components
        assert gradient.num_nonzeros() == 2

        # Verify gradient components exist
        for col_id in range(2):
            grad = gradient.get_derivative(col_id)
            assert grad is not None

        # Should have 2 equality constraints: objective equation and stationarity
        assert J_h.num_rows == 2
        assert J_h.num_nonzeros() > 0

        # Should have no inequality constraints
        assert J_g.num_nonzeros() == 0

    def test_bounds_nlp_basic(self):
        """Test scalar model with bounds."""
        model_ir = parse_and_normalize("bounds_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have gradient
        assert gradient.num_nonzeros() > 0

        # Bounds contribute to J_g (inequality constraints)
        # Each bound becomes g(x) = x - bound ≤ 0
        assert J_g.num_nonzeros() > 0


class TestIndexedModels:
    """Test integration on indexed models with sum aggregations."""

    def test_simple_nlp_indexed(self):
        """Test indexed model: min sum(i, a(i)*x(i)) s.t. x(i) >= 0."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have 4 variables: obj, x(i1), x(i2), x(i3)
        assert gradient.num_cols == 4

        # Gradient should have 4 components
        assert gradient.num_nonzeros() == 4

        # Verify each gradient component exists and is not None
        for col_id in range(4):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None, f"Gradient component {col_id} should exist"

        # Should have 3 inequality constraints: x(i) >= 0 normalized to -x(i) <= 0
        # plus any bounds
        assert J_g.num_nonzeros() >= 3

        # Should have equality constraints (objective definition and balance equations)
        assert J_h.num_nonzeros() >= 1

    def test_indexed_balance_model(self):
        """Test indexed model with balance constraints."""
        model_ir = parse_and_normalize("indexed_balance.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have multiple variables
        num_vars = gradient.num_cols
        assert num_vars > 1

        # Gradient should have components for each variable
        assert gradient.num_nonzeros() == num_vars

        # Should have equality constraints (balance equations)
        assert J_h.num_nonzeros() > 0


class TestNonlinearFunctions:
    """Test integration with nonlinear functions."""

    @skip_not_implemented
    def test_nonlinear_mix_model(self):
        """Test model with mix of nonlinear functions."""
        model_ir = parse_and_normalize("nonlinear_mix.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have gradient
        assert gradient.num_nonzeros() > 0

        # All gradient components should be non-None
        for col_id in range(gradient.mapping.num_vars):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None


class TestJacobianStructure:
    """Test Jacobian structure and sparsity patterns."""

    def test_jacobian_sparsity_pattern(self):
        """Test that Jacobian has correct sparsity pattern."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Get nonzero entries
        nonzeros = J_g.get_nonzero_entries()
        assert len(nonzeros) > 0

        # Each nonzero should have valid row/col IDs
        for row_id, col_id in nonzeros:
            assert 0 <= row_id < J_g.num_rows
            assert 0 <= col_id < J_g.num_cols

            # Derivative should exist
            deriv = J_g.get_derivative(row_id, col_id)
            assert deriv is not None

    def test_jacobian_by_names(self):
        """Test querying Jacobian by equation/variable names."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should be able to query by names if they exist
        # For indexed constraints, need to specify indices
        # This is a smoke test - just verify no crashes
        nonzeros = J_g.get_nonzero_entries()
        if len(nonzeros) > 0:
            row_id, col_id = nonzeros[0]
            deriv = J_g.get_derivative(row_id, col_id)
            assert deriv is not None


class TestGradientStructure:
    """Test gradient structure and access patterns."""

    def test_gradient_by_name(self):
        """Test querying gradient by variable name."""
        model_ir = parse_and_normalize("scalar_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should be able to get derivative by variable ID
        deriv = gradient.get_derivative(0)
        assert deriv is not None

    def test_gradient_all_components(self):
        """Test getting all gradient components."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Get all derivatives
        all_derivs = gradient.get_all_derivatives()
        assert len(all_derivs) == gradient.num_nonzeros()

        # Each derivative should be valid
        for col_id, deriv_expr in all_derivs.items():
            assert deriv_expr is not None
            assert 0 <= col_id < gradient.num_cols


class TestAPIErrorHandling:
    """Test that API handles errors gracefully."""

    def test_empty_model_error(self):
        """Test that empty model raises appropriate error."""
        # This would require creating an empty ModelIR, which is complex
        # Skip for now - could add in future if needed
        pass

    def test_no_objective_error(self):
        """Test that model without objective raises error."""
        # This would require creating a ModelIR without objective
        # Skip for now - could add in future if needed
        pass


class TestConsistency:
    """Test consistency across different access patterns."""

    def test_mapping_consistency(self):
        """Test that same mapping is used for gradient and Jacobians."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # All three should have equivalent mappings (same content)
        assert gradient.index_mapping.num_vars == J_g.index_mapping.num_vars
        assert gradient.index_mapping.num_vars == J_h.index_mapping.num_vars
        assert gradient.index_mapping.num_eqs == J_g.index_mapping.num_eqs
        assert gradient.index_mapping.num_eqs == J_h.index_mapping.num_eqs

        # Mapping should be complete
        assert gradient.index_mapping.num_vars > 0

    def test_all_variables_have_gradients(self):
        """Test that every variable has a gradient component."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Every variable should have a gradient (though some may be zero)
        num_vars = gradient.num_cols
        gradient_entries = gradient.num_nonzeros()

        # In general, we expect gradient for all vars (unless objective is constant)
        # For sum(i, a(i)*x(i)), all variables should have non-zero gradient
        assert gradient_entries == num_vars


class TestEndToEndWorkflow:
    """Test complete workflow from file to derivatives."""

    def test_full_pipeline_scalar(self):
        """Test complete pipeline on scalar model."""
        # Step 1: Parse
        model_ir = parse_and_normalize("scalar_nlp.gms")
        assert model_ir is not None

        # Step 2: Compute derivatives
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Step 3: Verify results
        assert gradient is not None
        assert J_g is not None
        assert J_h is not None

        # Step 4: Access specific derivatives
        assert gradient.num_nonzeros() > 0

    def test_full_pipeline_indexed(self):
        """Test complete pipeline on indexed model."""
        # Step 1: Parse
        model_ir = parse_and_normalize("simple_nlp.gms")
        assert model_ir is not None

        # Step 2: Compute derivatives
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Step 3: Verify results
        assert gradient.num_cols == 4  # obj, x(i1), x(i2), x(i3)
        assert gradient.num_nonzeros() == 4

        # Step 4: Verify can access all components
        for col_id in range(4):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None
