"""Sprint 27 #1374: the emitter must not produce exact-duplicate per-element
`var.fx(elem) = val;` initialization lines.

otpop fixes nine historical values (`x.fx('1965') = 29.4;` … `'1973'`). Those
emitted in BOTH the "Variable Bounds" section (from the source `fx_map`) AND
the "Fix suppressed _fx_ equations" restore pass (which re-emits the value
after the blanket `x.fx(...) = 0` from stationarity). When the variable's
`_fx_` equation is suppressed and the variable carries a stationarity
condition, the restore pass provides the single correct (blanket-surviving)
emission, so the Variable Bounds emission is a byte-identical duplicate.

The fix skips the earlier Variable Bounds emission in that case. This guard
asserts no exact-duplicate unconditional `var.fx(literal) = val;` line survives
in otpop's emit.
"""

from __future__ import annotations

import collections
import os
import re
import sys

import pytest

_FX_LITERAL_INIT = re.compile(r"^[A-Za-z_]\w*\.fx\('[^']*'\)\s*=\s*[^;]+;$")


def _emit_mcp_for(gms_path: str) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_file(gms_path)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)


@pytest.mark.integration
def test_otpop_no_duplicate_fx_literal_init():
    """#1374: otpop must not emit any `x.fx('<year>') = 29.4;` line twice."""
    src = "data/gamslib/raw/otpop.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/otpop.gms is gitignored on this runner.")

    lines = [ln.strip() for ln in _emit_mcp_for(src).splitlines()]
    fx_inits = [ln for ln in lines if _FX_LITERAL_INIT.match(ln)]
    dups = {ln: n for ln, n in collections.Counter(fx_inits).items() if n > 1}
    assert not dups, (
        "Found exact-duplicate `var.fx(literal) = val;` init line(s) in otpop "
        f"(#1374): {dups}"
    )
    # Sanity: the fixings are still present (exactly once) — the dedup must not
    # drop them entirely (that would unfix the historical values).
    assert "x.fx('1965') = 29.4;" in fx_inits, "otpop's x.fx('1965') fixing was dropped"
