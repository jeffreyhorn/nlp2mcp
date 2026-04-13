"""Computational convexity test via dual KKT comparison.

Exploits a fundamental property of convex optimization: for a convex
minimization problem, every KKT point is a global minimum.  Two KKT
solutions with different objective values prove non-convexity.

The test runs two independent MCP solves:
1. Cold-start: PATH solves from default initialization (duals = 0).
2. Warm-start: NLP pre-solve provides primal + dual initialization.

If both reach STATUS 1 (Optimal) with different objectives, the problem
is provably non-convex.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConvexityResult:
    """Result of a computational convexity test."""

    is_nonconvex: bool
    """True if proven non-convex (two distinct KKT points found)."""

    obj_cold: float | None
    """Objective value from cold-start solve."""

    obj_warm: float | None
    """Objective value from warm-start solve."""

    status_cold: int | None
    """GAMS model status from cold-start solve."""

    status_warm: int | None
    """GAMS model status from warm-start solve."""

    abs_diff: float | None
    """Absolute difference between objectives."""

    rel_diff: float | None
    """Relative difference between objectives."""

    conclusion: str
    """Human-readable conclusion."""


def check_convexity_numerical(
    mcp_cold_path: str | Path,
    mcp_warm_path: str | Path,
    timeout: int = 60,
) -> ConvexityResult:
    """Run computational convexity test by comparing two MCP solves.

    Args:
        mcp_cold_path: Path to cold-start MCP file (no pre-solve).
        mcp_warm_path: Path to warm-start MCP file (with --nlp-presolve).
        timeout: GAMS solve timeout in seconds.

    Returns:
        ConvexityResult with the comparison outcome.
    """
    from scripts.gamslib.test_solve import solve_mcp

    cold_result = solve_mcp(Path(mcp_cold_path), timeout=timeout)
    warm_result = solve_mcp(Path(mcp_warm_path), timeout=timeout)

    return _compare_results(cold_result, warm_result)


def check_convexity_from_results(
    cold_result: dict[str, Any],
    warm_result: dict[str, Any],
) -> ConvexityResult:
    """Compare two existing solve results without re-running GAMS.

    Useful when the pipeline already has both cold and warm solve results.
    """
    return _compare_results(cold_result, warm_result)


def _compare_results(
    cold_result: dict[str, Any],
    warm_result: dict[str, Any],
    rel_tol: float = 1e-4,
) -> ConvexityResult:
    """Compare cold-start and warm-start solve results."""
    status_cold = cold_result.get("model_status")
    status_warm = warm_result.get("model_status")
    obj_cold = cold_result.get("objective_value")
    obj_warm = warm_result.get("objective_value")

    # Both STATUS 1 with objectives available
    if status_cold == 1 and status_warm == 1 and obj_cold is not None and obj_warm is not None:
        abs_diff = abs(obj_cold - obj_warm)
        denom = max(abs(obj_cold), abs(obj_warm), 1.0)
        rel_diff = abs_diff / denom

        if rel_diff > rel_tol:
            return ConvexityResult(
                is_nonconvex=True,
                obj_cold=obj_cold,
                obj_warm=obj_warm,
                status_cold=status_cold,
                status_warm=status_warm,
                abs_diff=abs_diff,
                rel_diff=rel_diff,
                conclusion=(
                    f"Non-convex (proven): two distinct KKT points "
                    f"(cold={obj_cold:.6g}, warm={obj_warm:.6g}, "
                    f"diff={abs_diff:.6g})"
                ),
            )
        else:
            return ConvexityResult(
                is_nonconvex=False,
                obj_cold=obj_cold,
                obj_warm=obj_warm,
                status_cold=status_cold,
                status_warm=status_warm,
                abs_diff=abs_diff,
                rel_diff=rel_diff,
                conclusion=(
                    f"Consistent: same KKT point "
                    f"(cold={obj_cold:.6g}, warm={obj_warm:.6g}) "
                    f"— convexity not disproven"
                ),
            )

    # STATUS 5 cold, STATUS 1 warm
    if status_cold == 5 and status_warm == 1:
        return ConvexityResult(
            is_nonconvex=False,
            obj_cold=obj_cold,
            obj_warm=obj_warm,
            status_cold=status_cold,
            status_warm=status_warm,
            abs_diff=None,
            rel_diff=None,
            conclusion=(
                "Likely non-convex: cold start infeasible (STATUS 5), " "warm start optimal"
            ),
        )

    # STATUS 1 cold, STATUS 5 warm
    if status_cold == 1 and status_warm == 5:
        return ConvexityResult(
            is_nonconvex=False,
            obj_cold=obj_cold,
            obj_warm=obj_warm,
            status_cold=status_cold,
            status_warm=status_warm,
            abs_diff=None,
            rel_diff=None,
            conclusion=("Unusual: cold start optimal, warm start infeasible (STATUS 5)"),
        )

    # Both STATUS 5
    if status_cold == 5 and status_warm == 5:
        return ConvexityResult(
            is_nonconvex=False,
            obj_cold=obj_cold,
            obj_warm=obj_warm,
            status_cold=status_cold,
            status_warm=status_warm,
            abs_diff=None,
            rel_diff=None,
            conclusion="Inconclusive: both solves infeasible (STATUS 5)",
        )

    # One or both failed to solve
    cold_status_str = f"STATUS {status_cold}" if status_cold else "no solve"
    warm_status_str = f"STATUS {status_warm}" if status_warm else "no solve"
    return ConvexityResult(
        is_nonconvex=False,
        obj_cold=obj_cold,
        obj_warm=obj_warm,
        status_cold=status_cold,
        status_warm=status_warm,
        abs_diff=None,
        rel_diff=None,
        conclusion=(f"Inconclusive: cold={cold_status_str}, warm={warm_status_str}"),
    )
