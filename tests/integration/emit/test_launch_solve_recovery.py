"""Sprint 25 / #1351 / Sprint 26 Day 1 Phase A: launch's `stat_iweight(s)`
emits the Pattern C consolidated zero-offset term in the CORRECT shape.

Sprint 25 Day 6 (#1306) added a Pattern C consolidation gate that
suppressed phantom ±N IndexOffset enumeration for
`sum(ss$ge(ss,s), iweight(ss)+...)`-shape bodies. But the downstream
zero-offset builder lost the cross-element aggregation: for launch's
`dweight(s)`, the consolidated emit became a single `nu_dweight(s)`
term, leaving the KKT structurally incomplete (PATH reported
`model_infeasible (status 5)`).

Sprint 25 #1351 rolled back the gate (hardcoded
`allow_nonzero_offsets = True`), reverting to per-offset enumeration.
The emit was mathematically over-counted (5 phantom `nu_dweight(s±k)`
terms) but PATH found a feasible point — same objective as Sprint 25
Day 0 baseline (obj=2731.711).

Sprint 26 Day 1 Phase A restored the #1306 gate AND fixed the builder
(per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)"):
the consolidated zero-offset Sum iterates over the equation domain
with the body's condition, with the alias↔eq-domain indices swapped
so the multiplier is correctly indexed by the alias. The result is
the GAMS-equivalent of the target shape
`sum(ss$ge(s,ss), -nu_dweight(ss))` — structurally complete KKT, no
phantom offsets, single consolidated term.

This test guards both directions:
- If the gate is disabled (e.g. another #1351-style rollback), phantom
  `nu_dweight(s+1)` / `(s-1)` / etc. terms reappear → test fails.
- If the consolidation itself is dropped (no Pattern C term emitted),
  the alias-indexed `nu_dweight(ss)` is absent → test fails.
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
def test_launch_stat_iweight_emits_consolidated_pattern_c_term():
    """Sprint 26 Day 1 Phase A: launch's `stat_iweight(s)` emits a single
    consolidated Pattern C term ``sum(ss, ((-1) * 1$(ge(s,ss))) *
    nu_dweight(ss))`` instead of the over-counting 5 phantom-offset
    ``nu_dweight(s±k)`` terms from the #1351 stopgap.

    The shape is the GAMS-equivalent of the target ``sum(ss$ge(s,ss),
    -nu_dweight(ss))`` form from Sprint 25 SPRINT_LOG.md Day 11
    §"Open follow-ups (revised)".
    """
    src = "data/gamslib/raw/launch.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/launch.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    stat_iweight_lines = [line for line in output.splitlines() if "stat_iweight" in line]
    assert stat_iweight_lines, "Expected stat_iweight equation in launch MCP"
    text = "\n".join(stat_iweight_lines)

    # Positive invariant (Sprint 26 Day 1 Phase A): consolidated term must
    # appear with the alias-indexed multiplier and the swapped condition.
    assert "nu_dweight(ss)" in text, (
        "Expected consolidated alias-indexed `nu_dweight(ss)` multiplier in "
        "stat_iweight body for launch — Sprint 26 Day 1 Phase A consolidates "
        "the per-offset enumeration into a single term with the source alias "
        "as the multiplier index.\nBody:\n" + text
    )
    assert "ge(s,ss)" in text, (
        "Expected swapped condition `ge(s,ss)` in stat_iweight body for launch "
        "— the Pattern C builder swaps alias↔eq-domain indices in the body's "
        "condition.\nBody:\n" + text
    )

    # Negative invariant (#1351 failure mode): the over-counting phantom-offset
    # `nu_dweight(s±k)` terms must NOT reappear. These were the symptom of
    # the gate being disabled (the post-#1351 stopgap that the Sprint 26 Day 1
    # Phase A builder fix replaced with the correct consolidation).
    for needle in (
        "nu_dweight(s+1)",
        "nu_dweight(s+2)",
        "nu_dweight(s-1)",
        "nu_dweight(s-2)",
    ):
        assert needle not in text, (
            f"Found phantom-offset `{needle}` in stat_iweight body — the "
            f"Sprint 26 Day 1 Phase A gate should consolidate all such terms "
            f"into a single ``sum(ss$ge(s,ss), -nu_dweight(ss))`` term. "
            f"If this assertion fails, the gate may have been disabled (#1351 "
            f"regression).\nBody:\n{text}"
        )
