"""Tests for computational convexity test via dual KKT comparison."""

import pytest

from src.diagnostics.convexity_numerical import (
    ConvexityResult,
    _compare_results,
    check_convexity_from_results,
)

pytestmark = pytest.mark.unit


def _ok(model_status: int, objective_value: float | None = None) -> dict:
    """Build a solve result dict matching the real solver output shape.

    For model_status 4/5 (infeasible), mirrors solve_mcp which returns
    status="failure" with solver_status=1 (solver completed normally).
    """
    if model_status in {4, 5}:
        return {
            "status": "failure",
            "solver_status": 1,
            "model_status": model_status,
            "objective_value": None,
        }
    return {
        "status": "success",
        "solver_status": 1,
        "model_status": model_status,
        "objective_value": objective_value,
    }


def _fail(model_status: int | None = None, **extra) -> dict:
    """Build a failed/missing solve result dict (abnormal termination)."""
    return {
        "status": "failure",
        "solver_status": None,
        "model_status": model_status,
        "objective_value": None,
        **extra,
    }


class TestCompareResults:
    """Tests for _compare_results()."""

    def test_both_optimal_same_objective(self):
        """Both STATUS 1 with same objective → consistent."""
        cold = _ok(1, 7.955)
        warm = _ok(1, 7.955)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion
        assert result.obj_cold == 7.955
        assert result.obj_warm == 7.955
        assert result.abs_diff is not None
        assert result.abs_diff < 1e-10

    def test_both_optimal_different_objective(self):
        """Both STATUS 1 with different objectives → proven non-convex."""
        cold = _ok(1, 950.913)
        warm = _ok(1, 1075.547)
        result = _compare_results(cold, warm)
        assert result.is_nonconvex
        assert "Non-convex" in result.conclusion
        assert result.abs_diff == pytest.approx(124.634, abs=0.001)

    def test_cold_infeasible_warm_optimal(self):
        """Cold STATUS 5, warm STATUS 1 → likely non-convex."""
        cold = _ok(5)
        warm = _ok(1, 1075.547)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex  # Not proven, just likely
        assert "Likely non-convex" in result.conclusion

    def test_cold_optimal_warm_infeasible(self):
        """Cold STATUS 1, warm STATUS 5 → unusual."""
        cold = _ok(1, 950.913)
        warm = _ok(5)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Unusual" in result.conclusion

    def test_both_infeasible(self):
        """Both STATUS 5 → inconclusive."""
        cold = _ok(5)
        warm = _ok(5)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_status_2_locally_optimal_treated_as_optimal(self):
        """STATUS 2 (Locally Optimal) should be treated as optimal."""
        cold = _ok(2, 100.0)
        warm = _ok(1, 200.0)
        result = _compare_results(cold, warm)
        assert result.is_nonconvex
        assert "Non-convex" in result.conclusion

    def test_both_status_2_same_objective(self):
        """Both STATUS 2 with same objective → consistent."""
        cold = _ok(2, 7.955)
        warm = _ok(2, 7.955)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion

    def test_status_4_infeasible_cold_warm_optimal(self):
        """STATUS 4 (Infeasible) cold, STATUS 1 warm → likely non-convex."""
        cold = _ok(4)
        warm = _ok(1, 100.0)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Likely non-convex" in result.conclusion

    def test_status_4_and_5_both_infeasible(self):
        """STATUS 4 cold, STATUS 5 warm → both infeasible."""
        cold = _ok(4)
        warm = _ok(5)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_no_solve_results(self):
        """Missing model_status → inconclusive."""
        cold = _fail()
        warm = _fail()
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_relative_tolerance(self):
        """Small relative difference below tolerance → consistent."""
        cold = _ok(1, 1000.0)
        warm = _ok(1, 1000.05)
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 0.05 / 1000 = 5e-5 < 1e-4
        assert not result.is_nonconvex
        assert "Consistent" in result.conclusion

    def test_relative_tolerance_exceeded(self):
        """Relative difference above tolerance → non-convex."""
        cold = _ok(1, 1000.0)
        warm = _ok(1, 1001.0)
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 1.0 / 1001 ≈ 1e-3 > 1e-4
        assert result.is_nonconvex

    def test_denominator_uses_max_with_floor(self):
        """When both objectives near zero, floor of 1.0 prevents division issues."""
        cold = _ok(1, 0.0)
        warm = _ok(1, 0.0001)
        result = _compare_results(cold, warm, rel_tol=1e-4)
        # rel_diff = 0.0001 / max(0, 0.0001, 1.0) = 0.0001 / 1.0 = 1e-4
        # Exactly at threshold, not exceeded
        assert not result.is_nonconvex

    def test_failed_solve_not_trusted_as_optimal(self):
        """A solve with status='failure' and model_status=1 should NOT be trusted."""
        cold = {
            "status": "failure",
            "solver_status": 3,
            "model_status": 1,
            "objective_value": 100.0,
        }
        warm = _ok(1, 200.0)
        result = _compare_results(cold, warm)
        # Cold is not trusted, so this is inconclusive, not proven non-convex
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion

    def test_solver_status_not_1_not_trusted(self):
        """solver_status != 1 means abnormal termination — don't trust the result."""
        cold = {
            "status": "success",
            "solver_status": 2,
            "model_status": 1,
            "objective_value": 100.0,
        }
        warm = _ok(1, 200.0)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex

    def test_error_details_in_fallback_conclusion(self):
        """When solves fail, error details should appear in the conclusion."""
        cold = _fail(error="GAMS executable not found")
        warm = _fail(error="Timeout after 120 seconds")
        result = _compare_results(cold, warm)
        assert "GAMS executable not found" in result.conclusion
        assert "Timeout after 120 seconds" in result.conclusion

    def test_missing_fields_not_trusted(self):
        """Result dicts missing status/solver_status should not be trusted."""
        # Bare dict with just model_status — missing status and solver_status
        cold = {"model_status": 1, "objective_value": 100.0}
        warm = {"model_status": 1, "objective_value": 200.0}
        result = _compare_results(cold, warm)
        # Should NOT be proven non-convex — missing fields mean untrusted
        assert not result.is_nonconvex
        assert "Inconclusive" in result.conclusion


class TestCheckConvexityFromResults:
    """Tests for the public check_convexity_from_results wrapper."""

    def test_delegates_to_compare(self):
        """check_convexity_from_results delegates to _compare_results."""
        cold = _ok(1, 100.0)
        warm = _ok(1, 200.0)
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


class TestAttributionGates:
    """Sprint 39 P7 — a borrowed or aborted status must not become a verdict.

    ⚠ These exist because the two attribution gates were UNTESTED (PR #1740
    review): every fixture above omits `mcp_attribution`, so they exercise only
    the backward-compatible `None` path. Removing either gate would have left
    the suite green while reinstating the false result it was added to stop.
    """

    @staticmethod
    def _attributed(base: dict, verdict: str, completed: bool) -> dict:
        return {**base, "mcp_attribution": verdict, "mcp_completed_own_solve": completed}

    def test_an_EMBEDDED_ONLY_optimal_is_not_treated_as_optimal(self):
        """The `weapons` shape: the status is the source's, not ours.

        Without the gate both sides read as optimal at differing objectives and
        `_compare_results` would report **proven non-convex** — a strong claim
        from a solve that never happened.
        """
        cold = _ok(1, 950.913)
        warm = self._attributed(_ok(1, 1075.547), "EMBEDDED-ONLY", False)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex, "a borrowed status cannot prove non-convexity"
        assert "Non-convex" not in result.conclusion

    def test_an_ABORTED_own_mcp_is_not_treated_as_optimal(self):
        """`MCP-FAILED` with a stale MS-1 above its abort line."""
        cold = _ok(1, 950.913)
        warm = self._attributed(_ok(1, 1075.547), "MCP-FAILED", False)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex

    def test_an_EMBEDDED_ONLY_infeasible_is_not_treated_as_infeasible(self):
        """⚠ The infeasible path needs its own gate.

        The source reports infeasible, our MCP reports nothing. Without the
        guard this is read as the warm MCP being infeasible.
        """
        cold = self._attributed(_ok(5), "EMBEDDED-ONLY", False)
        warm = self._attributed(_ok(5), "EMBEDDED-ONLY", False)
        result = _compare_results(cold, warm)
        assert not result.is_nonconvex
        assert "infeasible" not in result.conclusion.lower(), result.conclusion

    def test_a_GENUINELY_infeasible_mcp_is_STILL_reported(self):
        """⚠⚠ THE REGRESSION GUARD, and the reason the gate is not MCP-SOLVED.

        A normally-completed MCP reporting model status 4/5 is `MCP-FAILED` —
        the verdict reserves `MCP-SOLVED` for a *usable* answer. An earlier
        revision required `MCP-SOLVED` on this path and so rejected **every real
        infeasible solve**, collapsing three branches into generic inconclusive
        outcomes. The signal here is `mcp_completed_own_solve`: our model ran and
        reported this status itself.
        """
        cold = self._attributed(_ok(5), "MCP-FAILED", True)
        warm = self._attributed(_ok(5), "MCP-FAILED", True)
        result = _compare_results(cold, warm)
        assert "infeasible" in result.conclusion.lower(), result.conclusion

    def test_results_without_the_new_fields_are_unchanged(self):
        """Backward compatibility: older result dicts keep their behaviour."""
        assert (
            _compare_results(_ok(1, 1.0), _ok(1, 1.0)).conclusion
            == _compare_results(
                self._attributed(_ok(1, 1.0), "MCP-SOLVED", True),
                self._attributed(_ok(1, 1.0), "MCP-SOLVED", True),
            ).conclusion
        )
