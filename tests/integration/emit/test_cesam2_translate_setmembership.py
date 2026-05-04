"""Sprint 25 / #1344: cesam2 translate regression for SetMembershipTest
on dynamically-populated subsets.

cesam2 declares dynamic subsets `icoeff`, `ival`, `nonzero` whose
membership is assigned at runtime (`nonzero(ii,jj) = yes$...`). Several
equations are conditioned on these via `$nonzero(ii,jj)`. Earlier in
Sprint 25 these `SetMembershipTest` conditions surfaced as soft
warnings (`Set membership for 'NONZERO' cannot be evaluated
statically because the set has no concrete members at compile time`),
but the cesam2 translate stage was being aborted by an unrelated
`Unknown expression type: IndexOffset` raised in the SetMembershipTest
emit path (#1338 family) and by `up_expr_map`/`lo_expr_map` keys with
subset/alias names being silently dropped (#1342, #1343).

This test asserts the translate-stage end-to-end completes for cesam2:
the AD/emit pipeline must produce a non-empty MCP without raising. The
SetMembershipTest soft-warning behavior is preserved (the translation
includes unevaluable instances and emits the `$nonzero(...)` guards
into GAMS).
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
def test_cesam2_translate_completes():
    """cesam2 translate must produce a non-empty MCP without raising.

    Pre-fix the run aborted at AD/emit time on a SetMembershipTest
    branch that fed `IndexOffset` into `expr_to_gams`'s default arm
    (`Unknown expression type: IndexOffset`). Post-fix translate
    completes and emits a non-empty MCP.
    """
    src = "data/gamslib/raw/cesam2.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/cesam2.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    assert output, "cesam2 emit returned empty output"
    # Sanity: the dynamic-subset guards survive into the MCP body.
    assert "$nonzero" in output.lower(), (
        "expected `$nonzero(...)` guard from cesam2's $-conditioned "
        "equations to appear in emitted MCP"
    )
