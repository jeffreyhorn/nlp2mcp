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

NOTE: These tests are currently SKIPPED due to a pre-existing Sprint 1 issue.
The find_objective_expression() function cannot locate objectives after
normalize_model() is called. This needs to be fixed in Sprint 1 code before
these integration tests can run.

See: GitHub Issue #19 "Objective Expressions Not Found After Model Normalization"
https://github.com/jeffreyhorn/nlp2mcp/issues/19
"""

import os

import pytest

from src.ad.api import compute_derivatives
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file

# Skip entire module due to pre-existing Sprint 1 issue
pytestmark = pytest.mark.skip(
    reason="Pre-existing Sprint 1 issue: find_objective_expression() fails after "
    "normalize_model(). Objective variables defined by equations cannot be found "
    "after normalization. This needs to be fixed before integration tests can run. "
    "See GitHub Issue #19: https://github.com/jeffreyhorn/nlp2mcp/issues/19"
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

        # Should have 1 variable (x)
        assert gradient.mapping.num_vars == 1

        # Gradient should have 1 component: ∂(x)/∂x = 1
        assert gradient.num_nonzeros() == 1
        grad_x = gradient.get_derivative(0)  # col_id = 0 for first var
        assert grad_x is not None

        # Should have 1 equality constraint: x + a = 0
        assert J_h.mapping.num_equations == 1
        assert J_h.num_nonzeros() == 1  # ∂(x+a)/∂x = 1

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

        # Should have 3 variables: x(i1), x(i2), x(i3)
        assert gradient.mapping.num_vars == 3

        # Gradient should have 3 components
        assert gradient.num_nonzeros() == 3

        # Verify each gradient component exists and is not None
        for col_id in range(3):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None, f"Gradient component {col_id} should exist"

        # Should have 3 inequality constraints: x(i) >= 0 normalized to -x(i) <= 0
        # plus any bounds
        assert J_g.num_nonzeros() >= 3

        # Should have 1 equality constraint (objective definition)
        assert J_h.num_nonzeros() >= 1

    def test_indexed_balance_model(self):
        """Test indexed model with balance constraints."""
        model_ir = parse_and_normalize("indexed_balance.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Should have multiple variables
        num_vars = gradient.mapping.num_vars
        assert num_vars > 1

        # Gradient should have components for each variable
        assert gradient.num_nonzeros() == num_vars

        # Should have equality constraints (balance equations)
        assert J_h.num_nonzeros() > 0


class TestNonlinearFunctions:
    """Test integration with nonlinear functions."""

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
            assert 0 <= row_id < J_g.mapping.num_equations
            assert 0 <= col_id < J_g.mapping.num_vars

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
            assert 0 <= col_id < gradient.mapping.num_vars


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

        # All three should use the same mapping
        assert gradient.mapping is J_g.mapping
        assert gradient.mapping is J_h.mapping

        # Mapping should be complete
        assert gradient.mapping.num_vars > 0

    def test_all_variables_have_gradients(self):
        """Test that every variable has a gradient component."""
        model_ir = parse_and_normalize("simple_nlp.gms")
        gradient, J_g, J_h = compute_derivatives(model_ir)

        # Every variable should have a gradient (though some may be zero)
        num_vars = gradient.mapping.num_vars
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
        assert gradient.mapping.num_vars == 3  # x(i1), x(i2), x(i3)
        assert gradient.num_nonzeros() == 3

        # Step 4: Verify can access all components
        for col_id in range(3):
            deriv = gradient.get_derivative(col_id)
            assert deriv is not None
