"""Sprint 25 / #1322: gtm corpus regression for NA-cleanup emission.

Pre-fix (post-PR-#1321 with #1192 + #1320 in place): gtm reaches PATH
but returns `MODEL STATUS 4 Infeasible` because `supb(i)` and
`supa(i)` evaluate to `NA` for the three regions where `supc(i) = 0`.
The NA values propagate into PATH's symbolic Jacobian as gigantic
coefficients (~5e30), making the model numerically unsolvable.

Post-fix: `emit_post_assignment_na_cleanup` injects
`supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0;` and
`supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0;` after the
original parameter assignments. The cleanup resets NA values to 0,
eliminating the gigantic coefficients. PATH may still be unable to
converge from the default starting point (the model is non-convex
and the warm-start path is blocked by #1313's Error 141 cascade), but
the structural NA-pathology is gone.

This test asserts the cleanup lines are emitted in the correct
location. Whether gtm fully solves to match is a stretch goal beyond
the primary acceptance criterion of #1322.
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
def test_gtm_emits_supb_supa_na_cleanup():
    """Both `supb(i)` and `supa(i)` (which have division-based
    assignments) must have NA-cleanup lines emitted by my fix.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert (
        "supb(i)$(NOT (supb(i) > -inf and supb(i) < inf)) = 0;" in output
    ), "Expected NA-cleanup line for `supb(i)` (division-based assignment)."
    assert (
        "supa(i)$(NOT (supa(i) > -inf and supa(i) < inf)) = 0;" in output
    ), "Expected NA-cleanup line for `supa(i)` (division-based assignment)."


@pytest.mark.integration
def test_gtm_supc_no_cleanup_data_driven():
    """`supc(i)` is assigned from `sdat(i, "limit")` directly
    (no arithmetic division — its NA-ness would come from data, not
    arithmetic). It should NOT receive a cleanup line, because doing
    so might override intentional sentinel-NA values.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # supc cleanup line should NOT be present (no division in its
    # assignment expressions).
    assert (
        "supc(i)$(NOT (supc(i) > -inf and supc(i) < inf))" not in output
    ), "supc(i) is data-driven (no division in assignment); should not receive a cleanup line."


@pytest.mark.integration
def test_gtm_cleanup_section_after_pre_solve_assignments():
    """The cleanup section must be emitted AFTER the original
    parameter assignments (so the NA-detection runs on the
    post-assignment values), but BEFORE the equation definitions
    (so PATH sees clean values).
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    lines = output.splitlines()

    # Find the cleanup section start.
    cleanup_idx = None
    for i, line in enumerate(lines):
        if "Issue #1322" in line and "NA-cleanup" in line:
            cleanup_idx = i
            break
    assert cleanup_idx is not None, "Expected #1322 NA-cleanup header in emission."

    # Find the supc-from-sdat assignment (the first parameter assignment).
    supc_assign_idx = None
    for i, line in enumerate(lines):
        if line.startswith("supc(i) = sdat(i,"):
            supc_assign_idx = i
            break
    assert supc_assign_idx is not None, "Expected `supc(i) = sdat(i,...);` assignment."

    # Find the equation definitions section (`stat_d(j)..` is one of them).
    stat_eq_idx = None
    for i, line in enumerate(lines):
        if line.startswith("stat_d(j)..") or line.startswith("bdef.."):
            stat_eq_idx = i
            break
    assert stat_eq_idx is not None, "Expected stat_*/bdef equation definitions."

    # Cleanup section must come AFTER pre-solve assignments and BEFORE
    # equation definitions.
    assert supc_assign_idx < cleanup_idx < stat_eq_idx, (
        f"Expected ordering: supc_assign({supc_assign_idx}) < "
        f"cleanup({cleanup_idx}) < equations({stat_eq_idx})."
    )
