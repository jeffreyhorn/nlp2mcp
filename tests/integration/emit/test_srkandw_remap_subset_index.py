"""Sprint 25 / #1350: srkandw stationarity-condition index remap.

`_remap_condition_to_domain` (Issue #1062) used naive position-based
substitution to map non-domain SymbolRef indices to var_domain entries.
For srkandw, the gradient condition `SetMembershipTest(tn, (t, sn))`
against y's domain `(j, t, n)` mapped position 1 (`sn`) to
`var_domain[1] = 't'`, producing the catastrophic `tn(t, t)` outer
guard at lines 129/150/151 of the emitted MCP. GAMS rejected with
`$171 Domain violation for set` because `tn(t,t)` is malformed
(both positions are the same `t`).

The fix uses the condition's set declared domain (`tn(t,n)` →
position 1 is parent `n`) to find the var_domain index that shares
an alias-root with `n` — which is `n` itself at position 2 of
y's domain. The corrected outer guard is `tn(t,n)`.
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
def test_srkandw_no_self_alias_tn_guard():
    """#1350: srkandw stat_y / y.fx / piL_y.fx must NOT contain `tn(t,t)`
    (both positions identical) — the gradient-condition `tn(t,sn)` must
    remap to `tn(t,n)` against y's declared domain `(j,t,n)`.

    Pre-fix the position-based remap mapped `sn` (cond position 1) to
    `var_domain[1] = t`, yielding `tn(t,t)`. GAMS rejected with `$171
    Domain violation for set`.
    """
    src = "data/gamslib/raw/srkandw.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/srkandw.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert "tn(t,t)" not in output, (
        "Found malformed `tn(t,t)` self-alias guard. The gradient condition "
        "`tn(t,sn)` must remap to `tn(t,n)` against y's domain (j,t,n), not "
        "to `tn(t,t)` via naive position-based substitution."
    )
    # Sanity: the corrected guard `tn(t,n)` should appear.
    assert "tn(t,n)" in output, "Expected the corrected `tn(t,n)` guard in stat_y body"
