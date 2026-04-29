"""Sprint 25 / #1243: lmp2 corpus regression for FREE-var-in-denominator init.

Pre-fix: lmp2's emitted MCP contains
`stat_y(p).. prod(p__, y(p__)) * sum(p__, 1 / y(p__)) + nu_Products(p) =E= 0;`
but no `y.l(p) = ...;` initialization. Variable `y` is free, so
`y.l(p)` defaults to 0, and PATH aborts with EXECERROR=1 from the
`1/y(p__)` divisor at model-listing time.

Post-fix: the emitter scans stationarity equation bodies for FREE
VarRefs in divisor positions (or `log()`-argument positions) and
emits `var.l(d) = 1;` for each. For lmp2 this produces `y.l(p) = 1;`,
which satisfies `1/y(p) = 1` at the initial point — the structural
div-by-zero pathology is gone.

Note: lmp2 does not yet compile end-to-end because of #1323 (the `m`
dynamic-subset assignment is not extracted into the IR). This test
validates the emission only, which is the strict acceptance signal
for #1243. End-to-end pipeline acceptance is gated on #1323's fix.
"""

from __future__ import annotations

import os
import re
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
def test_lmp2_emits_y_l_init_for_stat_y_denominator():
    """The `stat_y(p)` equation contains `1/y(p__)` from `_diff_prod`'s
    logarithmic derivative. Variable `y` is FREE, so the emitter must
    inject `y.l(p) = 1;` to avoid EXECERROR=1.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert re.search(
        r"^\s*y\.l\(p\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "Expected `y.l(p) = 1;` line for FREE var `y` appearing in stat_y denominator."


@pytest.mark.integration
def test_lmp2_x_not_initialized_not_in_denominator():
    """`x(nn)` is FREE but does NOT appear in any stationarity-equation
    denominator (only as `cc(p,nn) * x(n)` in linear positions). It
    should NOT receive the new `.l = 1` init.
    """
    src = "data/gamslib/raw/lmp2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/lmp2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # `piL_x.l(nn) = 1;` is allowed (POSITIVE multiplier), but no plain
    # `x.l(nn) = 1;` should appear.
    assert not re.search(
        r"^\s*x\.l\(nn\)\s*=\s*1\s*;", output, re.MULTILINE
    ), "FREE var `x` is not in any denominator; should not receive #1243's auto-init."
