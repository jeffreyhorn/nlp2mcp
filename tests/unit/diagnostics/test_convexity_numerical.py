"""Tests for computational convexity test via dual KKT comparison."""

import pytest

from src.diagnostics.convexity_numerical import (
    ConvexityResult,
    _compare_results,
    check_convexity_from_results,
)

pytestmark = pytest.mark.unit


class TestCompareResults:
    """Tests for _compare_results()."""

    def test_both_optimal_same_objective(self):
        """Both STATUS 1 with same objective → consistent."""
        cold = {"model_status": 1, "objective_value": 7.955}
        warm = {"model_status": 1, "objective_value": 7.955}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion
        assert result.obj_cold == 7.955
        assert result.obj_warm == 7.955
        assert result.abs_diff is not None
        assert result.abs_diff < 1e-10

    def test_both_optimal_different_objective(self):
        """Both STATUS 1 with different objectives → proven non-convex."""
        cold = {"model_status": 1, "objective_value": 950.913}
        warm = {"model_status": 1, "objective_value": 1075.547}
        result = _compare_results(cold, warm)
        assert result.is_nonconvex
        assert "Non-convex" in result.conclusion
        assert result.abs_diff == pytest.approx(124.634, abs=0.001)

    def test_cold_infeasible_warm_optimal(self):
        """Cold STATUS 5, warm STATUS 1 → likely non-convex."""
        cold = {"model_status": 5, "objective_value": None}
        warm = {"model_status": 1, "objective_value": 1075.547}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex  # Not proven, just likely
        assert "Likely non-convex" in result.conclusion

    def test_cold_optimal_warm_infeasible(self):
        """Cold STATUS 1, warm STATUS 5 → unusual."""
        cold = {"model_status": 1, "objective_value": 950.913}
        warm = {"model_status": 5, "objective_value": None}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Unusual" in result.conclusion

    def test_both_infeasible(self):
        """Both STATUS 5 → inconclusive."""
        cold = {"model_status": 5, "objective_value": None}
        warm = {"model_status": 5, "objective_value": None}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_status_2_locally_optimal_treated_as_optimal(self):
        """STATUS 2 (Locally Optimal) should be treated as optimal."""
        cold = {"model_status": 2, "objective_value": 100.0}
        warm = {"model_status": 1, "objective_value": 200.0}
        result = _compare_results(cold, warm)
        assert result.is_nonconvex
        assert "Non-convex" in result.conclusion

    def test_both_status_2_same_objective(self):
        """Both STATUS 2 with same objective → consistent."""
        cold = {"model_status": 2, "objective_value": 7.955}
        warm = {"model_status": 2, "objective_value": 7.955}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion

    def test_status_4_infeasible_cold_warm_optimal(self):
        """STATUS 4 (Infeasible) cold, STATUS 1 warm → likely non-convex."""
        cold = {"model_status": 4, "objective_value": None}
        warm = {"model_status": 1, "objective_value": 100.0}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Likely non-convex" in result.conclusion

    def test_status_4_and_5_both_infeasible(self):
        """STATUS 4 cold, STATUS 5 warm → both infeasible."""
        cold = {"model_status": 4, "objective_value": None}
        warm = {"model_status": 5, "objective_value": None}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_no_solve_results(self):
        """Missing model_status → inconclusive."""
        cold = {"model_status": None, "objective_value": None}
        warm = {"model_status": None, "objective_value": None}
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_relative_tolerance(self):
        """Small relative difference below tolerance → consistent."""
        cold = {"model_status": 1, "objective_value": 1000.0}
        warm = {"model_status": 1, "objective_value": 1000.05}
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 0.05 / 1000 = 5e-5 < 1e-4
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion

    def test_relative_tolerance_exceeded(self):
        """Relative difference above tolerance → non-convex."""
        cold = {"model_status": 1, "objective_value": 1000.0}
        warm = {"model_status": 1, "objective_value": 1001.0}
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 1.0 / 1001 ≈ 1e-3 > 1e-4
        assert result.is_nonconvex

    def test_denominator_uses_max_with_floor(self):
        """When both objectives near zero, floor of 1.0 prevents division issues."""
        cold = {"model_status": 1, "objective_value": 0.0}
        warm = {"model_status": 1, "objective_value": 0.0001}
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 0.0001 / max(0, 0.0001, 1.0) = 0.0001 / 1.0 = 1e-4
        # Exactly at threshold, not exceeded
        assert not result.is_nonconvex


class TestCheckConvexityFromResults:
    """Tests for the public check_convexity_from_results wrapper."""

    def test_delegates_to_compare(self):
        """check_convexity_from_results delegates to _compare_results."""
        cold = {"model_status": 1, "objective_value": 100.0}
        warm = {"model_status": 1, "objective_value": 200.0}
        result = check_convexity_from_results(cold, warm)
        assert isinstance(result, ConvexityResult)
        assert result.is_nonconvex


class TestConvexityResultDataclass:
    """Tests for the ConvexityResult dataclass."""

    def test_fields_accessible(self):
        r = ConvexityResult(
            is_nonconvex=True,
            obj_cold=1.0,
            obj_warm=2.0,
            status_cold=1,
            status_warm=1,
            abs_diff=1.0,
            rel_diff=0.5,
            conclusion="test",
        )
        assert r.is_nonconvex is True
        assert r.obj_cold == 1.0
        assert r.conclusion == "test"
