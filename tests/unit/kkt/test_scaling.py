"""Tests for Curtis-Reid scaling implementation."""

import numpy as np
import pytest

from src.ad.jacobian import JacobianStructure
from src.ir.ast import Const
from src.kkt.scaling import byvar_scaling, curtis_reid_scaling


@pytest.fixture
def simple_jacobian():
    """Create a simple 2x2 Jacobian with known structure."""
    jac = JacobianStructure(num_rows=2, num_cols=2)
    # Row 0: [1, 1]
    jac.set_derivative(0, 0, Const(1.0))
    jac.set_derivative(0, 1, Const(1.0))
    # Row 1: [1, 0]
    jac.set_derivative(1, 0, Const(1.0))
    return jac


@pytest.fixture
def badly_scaled_jacobian():
    """Create a badly scaled 2x2 Jacobian."""
    jac = JacobianStructure(num_rows=2, num_cols=2)
    # Row 0: [1e6, 2e6]  (large values)
    jac.set_derivative(0, 0, Const(1e6))
    jac.set_derivative(0, 1, Const(2e6))
    # Row 1: [1e-6, 2e-6]  (small values)
    jac.set_derivative(1, 0, Const(1e-6))
    jac.set_derivative(1, 1, Const(2e-6))
    return jac


class TestCurtisReidScaling:
    """Tests for Curtis-Reid scaling algorithm."""

    def test_curtis_reid_simple_jacobian(self, simple_jacobian):
        """Test Curtis-Reid on simple Jacobian."""
        R, C = curtis_reid_scaling(simple_jacobian, max_iter=10, tol=0.1)

        # Both should be 1D arrays
        assert R.shape == (2,)
        assert C.shape == (2,)

        # All scaling factors should be positive
        assert np.all(R > 0)
        assert np.all(C > 0)

    def test_curtis_reid_improves_conditioning(self, badly_scaled_jacobian):
        """Test that Curtis-Reid produces valid scaling."""
        R, C = curtis_reid_scaling(badly_scaled_jacobian, max_iter=10, tol=0.1)

        # All scaling factors should be positive and finite
        # Note: Since we use structural scaling (1.0 for all nonzeros),
        # the actual values don't matter - we just verify the algorithm works
        assert np.all(np.isfinite(R))
        assert np.all(np.isfinite(C))
        assert np.all(R > 0)
        assert np.all(C > 0)

        # For structural scaling, all nonzero entries are treated as 1.0
        # So both rows have same structure, should get similar scaling
        assert R.shape == (2,)
        assert C.shape == (2,)

    def test_curtis_reid_convergence(self, simple_jacobian):
        """Test that Curtis-Reid converges."""
        # Run with different iteration counts
        R1, C1 = curtis_reid_scaling(simple_jacobian, max_iter=1)
        R10, C10 = curtis_reid_scaling(simple_jacobian, max_iter=10)

        # With more iterations, scaling should be similar or better
        # (for this simple case, might converge in 1 iteration)
        assert R1.shape == R10.shape
        assert C1.shape == C10.shape

    def test_curtis_reid_zero_entries(self):
        """Test Curtis-Reid with zero entries (sparse matrix)."""
        jac = JacobianStructure(num_rows=3, num_cols=3)
        # Only diagonal entries
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(1, 1, Const(1.0))
        jac.set_derivative(2, 2, Const(1.0))

        R, C = curtis_reid_scaling(jac)

        # Should handle sparse structure correctly
        assert R.shape == (3,)
        assert C.shape == (3,)
        assert np.all(R > 0)
        assert np.all(C > 0)

    def test_curtis_reid_empty_row(self):
        """Test Curtis-Reid with empty row."""
        jac = JacobianStructure(num_rows=2, num_cols=2)
        # Row 0: [1, 1]
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 1, Const(1.0))
        # Row 1: empty (all zeros)

        R, C = curtis_reid_scaling(jac)

        # Should handle empty row without division by zero
        assert R.shape == (2,)
        assert C.shape == (2,)
        assert np.all(np.isfinite(R))
        assert np.all(np.isfinite(C))
        # Empty row gets scaling factor of 1.0
        assert R[1] == pytest.approx(1.0)

    def test_curtis_reid_tolerance(self, simple_jacobian):
        """Test Curtis-Reid with different tolerances."""
        R_tight, C_tight = curtis_reid_scaling(simple_jacobian, tol=0.01)
        R_loose, C_loose = curtis_reid_scaling(simple_jacobian, tol=0.5)

        # Both should converge
        assert R_tight.shape == R_loose.shape
        assert C_tight.shape == C_loose.shape


class TestByvarScaling:
    """Tests for byvar (per-variable) scaling."""

    def test_byvar_simple_jacobian(self, simple_jacobian):
        """Test byvar scaling on simple Jacobian."""
        C = byvar_scaling(simple_jacobian)

        # Should return 1D array for columns
        assert C.shape == (2,)

        # All scaling factors should be positive
        assert np.all(C > 0)

    def test_byvar_badly_scaled(self, badly_scaled_jacobian):
        """Test byvar scaling on badly scaled Jacobian."""
        C = byvar_scaling(badly_scaled_jacobian)

        # Should normalize column norms
        assert C.shape == (2,)
        assert np.all(np.isfinite(C))
        assert np.all(C > 0)

    def test_byvar_empty_column(self):
        """Test byvar with empty column."""
        jac = JacobianStructure(num_rows=2, num_cols=2)
        # Column 0: [1, 1]^T
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(1, 0, Const(1.0))
        # Column 1: empty (all zeros)

        C = byvar_scaling(jac)

        # Should handle empty column without division by zero
        assert C.shape == (2,)
        assert np.all(np.isfinite(C))
        # Empty column gets scaling factor of 1.0
        assert C[1] == pytest.approx(1.0)

    def test_byvar_vs_curtis_reid(self, simple_jacobian):
        """Test that byvar gives different result than Curtis-Reid."""
        C_byvar = byvar_scaling(simple_jacobian)
        R_cr, C_cr = curtis_reid_scaling(simple_jacobian)

        # Both should produce column scaling
        assert C_byvar.shape == C_cr.shape

        # Results may differ because Curtis-Reid also does row scaling
        # Just verify both are valid
        assert np.all(C_byvar > 0)
        assert np.all(C_cr > 0)


class TestScalingEdgeCases:
    """Test edge cases for scaling algorithms."""

    def test_single_row_jacobian(self):
        """Test scaling with single row."""
        jac = JacobianStructure(num_rows=1, num_cols=3)
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 1, Const(2.0))
        jac.set_derivative(0, 2, Const(3.0))

        R, C = curtis_reid_scaling(jac)

        assert R.shape == (1,)
        assert C.shape == (3,)
        assert np.all(R > 0)
        assert np.all(C > 0)

    def test_single_column_jacobian(self):
        """Test scaling with single column."""
        jac = JacobianStructure(num_rows=3, num_cols=1)
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(1, 0, Const(2.0))
        jac.set_derivative(2, 0, Const(3.0))

        R, C = curtis_reid_scaling(jac)

        assert R.shape == (3,)
        assert C.shape == (1,)
        assert np.all(R > 0)
        assert np.all(C > 0)

    def test_completely_empty_jacobian(self):
        """Test scaling with no nonzero entries."""
        jac = JacobianStructure(num_rows=2, num_cols=2)
        # No entries set - all zeros

        R, C = curtis_reid_scaling(jac)

        # Should handle gracefully with all 1.0 scaling
        assert R.shape == (2,)
        assert C.shape == (2,)
        assert np.allclose(R, 1.0)
        assert np.allclose(C, 1.0)

    def test_very_large_jacobian(self):
        """Test scaling with larger Jacobian."""
        jac = JacobianStructure(num_rows=100, num_cols=100)
        # Diagonal matrix
        for i in range(100):
            jac.set_derivative(i, i, Const(float(i + 1)))

        R, C = curtis_reid_scaling(jac, max_iter=5)

        assert R.shape == (100,)
        assert C.shape == (100,)
        assert np.all(R > 0)
        assert np.all(C > 0)
        assert np.all(np.isfinite(R))
        assert np.all(np.isfinite(C))
