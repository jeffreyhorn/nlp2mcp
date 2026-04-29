"""Sprint 25 / #1320: gtm bdef divisor-guard corpus regression.

Pre-fix: emitted `bdef` body in gtm contained
`sum(i, supa(i)*s(i) - supb(i)*log((supc(i) - s(i))/supc(i)))` evaluated
unconditionally. For three regions (mexico, alberta-bc, atlantic) where
`supc(i) = 0` from empty `sdat(i, "limit")` cells, GAMS aborted at
model-listing time with EXECERROR=2 on the `log(0/0)` term.

Post-fix: `_inject_divisor_guards` adds `$(supc(i) <> 0)` to the
relevant `Sum` so the listing-time evaluation skips the degenerate
rows. gtm now reaches PATH (was previously aborting before PATH was
invoked).

Note: gtm's PATH solve currently still returns `MODEL STATUS 4
Infeasible` because of broader NA propagation through the supb/supa
parameters (those are computed from supc=0 in the original
parameter-assignment chain, ending up as NA). Reaching PATH at all is
the primary acceptance criterion for #1320; full match is a stretch
goal blocked by additional issues.
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
def test_gtm_bdef_has_supc_nonzero_guard():
    """gtm's emitted `bdef` line must contain `$(supc(i) <> 0)` (or the
    equivalent normalized form) on the offending supply-cost sum.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    bdef_lines = [line for line in output.splitlines() if line.startswith("bdef..")]
    assert bdef_lines, "Expected `bdef..` in the gtm emission."
    bdef = bdef_lines[0]

    # The supc-nonzero guard must appear on a Sum body. Accept either
    # `supc(i) <> 0` or `supc(i)<>0` (whitespace-flexible).
    assert (
        "supc(i) <> 0" in bdef or "supc(i)<>0" in bdef
    ), f"Pre-#1320 emission had no divisor guard on bdef. bdef line:\n{bdef}"


@pytest.mark.integration
def test_gtm_bdef_emits_without_python_error():
    """Smoke: gtm translation completes without Python errors and the
    emitted output retains all three sums in `bdef`.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    assert "bdef.. benefit =E= sum(j," in output
    # Three sums in bdef: over j (demand), over i (supply, now guarded),
    # over (i,j)$ij (transport).
    bdef_lines = [line for line in output.splitlines() if line.startswith("bdef..")]
    assert bdef_lines
    assert bdef_lines[0].count("sum(") == 3, (
        f"Expected 3 `sum(` aggregators in bdef; got "
        f"{bdef_lines[0].count('sum(')}.\n{bdef_lines[0]}"
    )


@pytest.mark.integration
def test_gtm_other_sums_in_bdef_unchanged():
    """The `sum(j, dema(j) * d(j) ** demb(j))` and the
    `sum((i,j)$ij(i,j), utc(i,j) * x(i,j))` aggregators in bdef have no
    divisor params and must NOT receive a spurious guard. The first sum
    has no condition; the second's condition is just `ij(i,j)`.
    """
    src = "data/gamslib/raw/gtm.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/gtm.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)
    bdef_lines = [line for line in output.splitlines() if line.startswith("bdef..")]
    assert bdef_lines
    bdef = bdef_lines[0]

    # The demand sum must remain unconditioned (uses `**` exponent, no division).
    assert "sum(j, dema(j)" in bdef, (
        "Expected `sum(j, dema(j) * ...)` to remain unconditioned in bdef.\n" + bdef
    )

    # The transport sum's condition must be just `ij(i,j)`, NOT
    # extended with a spurious divisor guard.
    assert "sum((i,j)$(ij(i,j))," in bdef, (
        "Expected `sum((i,j)$(ij(i,j)), ...)` (transport sum) to remain "
        "with only its original `ij(i,j)` condition.\n" + bdef
    )
