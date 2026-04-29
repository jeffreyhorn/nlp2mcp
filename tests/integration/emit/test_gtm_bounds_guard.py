"""Sprint 25 / #1192: gtm corpus-level regression for bounds-aware
conditional stationarity.

Pre-fix: the emitted `stat_s(i)` for gtm produced division by zero at
GAMS model-listing time for the three regions where `supc(i) = 0`
(mexico, alberta-bc, atlantic) because the supply-derivative term
contains `1/((supc-s)/supc) * 1/sqr(supc)`. GAMS aborted with
EXECERROR=3 before PATH ever saw the model.

Post-fix: the bounds-aware stationarity guard wraps the `stat_s(i)`
body in `$(s.up(i) - s.lo(i) > 1e-10)` and emits a
`s.fx(i)$(not (...)) = s.lo(i)` line (runtime bound, not a hard-coded
0) so the variable is fixed at its collapsed bound for those instances
and the stationarity row collapses to `0 =E= 0`.

The same PR also injects `$(supc(i) <> 0)` into `bdef` (the parsed-
source benefit equation; see `test_gtm_bdef_guard.py`) and an
NA-cleanup pass for division-based parameter assignments
(`emit_post_assignment_na_cleanup`; see `test_gtm_na_cleanup.py`).
With all three of those + the #1313 ``$include``-ordering fix, gtm
reaches `MODEL STATUS 1 Optimal` with `--nlp-presolve` (objective
`-543.5651` matching the NLP reference).

These tests assert the bounds-collapse guard pieces are present in
the emitted MCP. End-to-end solve verification lives in the pipeline
runner's per-model integration tests.
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
def test_gtm_stat_s_has_bounds_guard():
    """gtm's `stat_s(i)` must be conditioned on
    `s.up(i) - s.lo(i) > 1e-10` so the three zero-supc regions skip
    the div-by-zero derivative term.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # Find the stat_s line
    stat_s_lines = [line for line in output.splitlines() if line.startswith("stat_s(i)..")]
    assert stat_s_lines, "Expected `stat_s(i)..` in the gtm emission."

    stat_s = stat_s_lines[0]
    # The body must be wrapped in a bounds-collapse guard
    assert "s.up(i) - s.lo(i) > 1e-10" in stat_s, (
        "Pre-#1192 emission had no bounds-collapse guard, leading to "
        "EXECERROR=3 division-by-zero for mexico/alberta-bc/atlantic. "
        f"stat_s line:\n{stat_s}"
    )


@pytest.mark.integration
def test_gtm_s_fx_emits_for_collapsed_bounds():
    """gtm's `s` variable must have an `s.fx(i)$(not (s.up(i) -
    s.lo(i) > 1e-10)) = 0` line so GAMS fixes the variable for the
    three zero-supc regions.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    fx_lines = [line for line in output.splitlines() if line.startswith("s.fx(i)")]
    assert fx_lines, "Expected `s.fx(i)..` line in the gtm emission."

    # At least one of them carries the bounds-collapse condition
    assert any("s.up(i) - s.lo(i) > 1e-10" in line for line in fx_lines), (
        "Expected at least one `s.fx(i)$(not (s.up(i) - s.lo(i) > 1e-10)) = 0` "
        "line for the bounds-collapse fix.\n\n"
        "s.fx lines:\n" + "\n".join(fx_lines)
    )


@pytest.mark.integration
def test_gtm_emits_without_python_error():
    """Pipeline-level smoke: the gtm translation completes without
    Python errors (separate from whether the resulting MCP solves).
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    assert "Solve mcp_model using MCP" in output
    assert "stat_s(i)" in output
    assert "stat_d(j)" in output
    assert "stat_x(i,j)" in output
