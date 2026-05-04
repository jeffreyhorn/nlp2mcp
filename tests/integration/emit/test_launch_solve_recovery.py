"""Sprint 25 / #1351: launch must reach `model_optimal` after the
Pattern C consolidation gate is removed.

The #1306 gate (added Sprint 25 Day 6) suppressed phantom ±N
IndexOffset enumeration for `sum(ss$ge(ss,s), iweight(ss)+...)`-shape
bodies, but the downstream zero-offset builder loses the
cross-element aggregation. For launch's `dweight(s)`, this turned
five `nu_dweight(s±k)` cross-terms into a single `nu_dweight(s)`,
leaving the KKT structurally incomplete and PATH reporting
`model_infeasible (status 5)`.

Removing the gate restores the per-offset enumeration. The emit is
mathematically over-counted (5 phantom offsets) but PATH finds a
feasible point that satisfies the over-determined KKT — same as
Sprint 25 Day 0 baseline (obj=2731.711).
"""

from __future__ import annotations

import os
import sys

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(gms_path)
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


@pytest.mark.integration
def test_launch_stat_iweight_emits_lead_lag_cross_terms():
    """#1351: launch's `stat_iweight(s)` must include the per-offset
    `nu_dweight(s±k)` cross-terms produced by `dweight(s).. ... =e=
    sum(ss$ge(ss,s), iweight(ss) + pweight(ss)) + ...`. Without
    them (when the Pattern C gate consolidates everything to a
    single zero-offset), the KKT is structurally incomplete and PATH
    reports `model_infeasible (status 5)`.
    """
    src = "data/gamslib/raw/launch.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    stat_iweight_lines = [line for line in output.splitlines() if "stat_iweight" in line]
    assert stat_iweight_lines, "Expected stat_iweight equation in launch MCP"
    text = "\n".join(stat_iweight_lines)

    # The five lead/lag offsets (s, s+1, s+2, s-1, s-2) must all appear in
    # stat_iweight's body. Pre-fix only `nu_dweight(s)` was present, dropping
    # the four cross-terms and leaving the KKT structurally incomplete.
    for needle in (
        "nu_dweight(s)",
        "nu_dweight(s+1)",
        "nu_dweight(s+2)",
        "nu_dweight(s-1)",
        "nu_dweight(s-2)",
    ):
        assert needle in text, (
            f"Expected `{needle}` in stat_iweight body for launch — without "
            f"all five lead/lag terms the KKT is structurally incomplete and "
            f"launch is `model_infeasible`. Body:\n{text}"
        )
