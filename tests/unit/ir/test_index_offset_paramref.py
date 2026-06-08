"""Sprint 27 #1224: `IndexOffset.to_gams_string()` must render parameter-valued
offsets (e.g. mine's `i + li(k)`), not raise "Complex offset expressions not
yet supported".

mine (GAMSlib "Opencast Mining") uses parameter-valued index offsets:

    pr(k,l+1,i,j)$c(l,i,j).. x(l, i+li(k), j+lj(k)) =g= x(l+1,i,j);

where `li(k)`/`lj(k)` are parameters giving the per-neighbor lead amount. The
equation domain index `k` stays symbolic in the MCP, so the offset cannot be
reduced to a constant — but GAMS accepts a parameter expression as a lead/lag
amount and evaluates it at runtime. Before the fix, emit aborted with
`NotImplementedError: Complex offset expressions not yet supported:
ParamRef(li(k))`. The fix renders `base+li(k)` directly.

NOTE: this fix delivers translation only (+1 Translate). The KKT cross-term
for a parameter-valued offset is not yet inverted in the Jacobian, so mine's
emitted MCP is still `model_infeasible` — that deeper AD change is deferred to
Sprint 28 (see ISSUE_1224).
"""

from __future__ import annotations

import os
import sys

import pytest

from src.ir.ast import Const, IndexOffset, ParamRef, SymbolRef


@pytest.mark.unit
def test_paramref_offset_renders():
    """#1224: a ParamRef offset renders as `base+param(idx)` (GAMS-valid)."""
    assert (
        IndexOffset(base="i", offset=ParamRef("li", ("k",)), circular=False).to_gams_string()
        == "i+li(k)"
    )
    assert (
        IndexOffset(base="j", offset=ParamRef("lj", ("k",)), circular=False).to_gams_string()
        == "j+lj(k)"
    )


@pytest.mark.unit
def test_paramref_lag_offset_renders():
    """#1224 (PR review): the LAG form `i-li(k)` is parsed as
    `Unary('-', ParamRef(...))` and must render as `i-li(k)`, not raise."""
    from src.ir.ast import Unary

    lag = IndexOffset(base="i", offset=Unary("-", ParamRef("li", ("k",))), circular=False)
    assert lag.to_gams_string() == "i-li(k)"


@pytest.mark.unit
def test_const_and_symbol_offsets_unchanged():
    """Regression: the existing Const/SymbolRef offset rendering is unchanged."""
    assert IndexOffset(base="t", offset=Const(1), circular=False).to_gams_string() == "t+1"
    assert IndexOffset(base="t", offset=Const(-3), circular=False).to_gams_string() == "t-3"
    assert IndexOffset(base="i", offset=SymbolRef("j"), circular=False).to_gams_string() == "i+j"


@pytest.mark.unit
def test_circular_paramref_offset_unsupported():
    """Circular (`++`/`--`) lead/lag with a ParamRef offset is still rejected
    explicitly rather than silently mis-rendered."""
    with pytest.raises(NotImplementedError):
        IndexOffset(base="i", offset=ParamRef("li", ("k",)), circular=True).to_gams_string()


@pytest.mark.integration
def test_mine_translates_with_paramref_offset():
    """#1224 end-to-end: the mine model translates (no 'Complex offset' abort)
    and the `pr` complementarity renders the parameter-valued offsets."""
    src = "data/gamslib/raw/mine.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/mine.gms is gitignored on this runner.")

    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_file(src)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        emit = emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)

    assert (
        "i+li(k)" in emit and "j+lj(k)" in emit
    ), "mine's parameter-valued offsets must render in the emitted MCP."
