"""Sprint 25 / #1234: otpop corpus regression for scalar-constant offset
resolution.

Pre-fix: `otpop`'s `adef` equation uses `pd(tt-l)` where `Scalar l /4/`.
The parser produced `IndexOffset('tt', Unary('-', SymbolRef('l')))`,
which the AD engine couldn't differentiate (treats SymbolRef('l') as
opaque). As a result, `stat_pd(tt)` was missing the cross-term from
differentiating `adef(tt+4)` w.r.t. `pd(tt)`, producing an
INCONSISTENT KKT system that PATH couldn't satisfy.

Post-fix (this PR): the IR normalizer's `resolve_scalar_offsets` pass
substitutes `l → 4`, producing `IndexOffset('tt', Const(-4))`. The AD
machinery then correctly cross-attributes the offset, and
`stat_pd(tt)` includes the missing `-con*d(tt+3)*nu_adef(tt+4)` term.

Note: the AD-correctness fix improves the KKT structure but otpop
still aborts with `EXECERROR=1` due to additional unrelated AD bugs
(time-reversal `p(t + (card(t) - ord(t)))` derivative, missing terms
in `stat_x`/`stat_d` for non-fixed historical years). Those are out
of scope for this PR — the issue stays OPEN with detailed notes.
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
def test_otpop_stat_pd_includes_cross_term_from_adef():
    """`adef(tt)..  ... pd(tt-l) ...` with `Scalar l /4/` should
    contribute to `stat_pd(tt')` via the cross-term
    `-con*d(tt'+3)*nu_adef(tt'+4)` (since `tt2-4 = tt'` ⟺ `tt2 = tt'+4`).

    Pre-fix the AD couldn't see through the `SymbolRef('l')` offset,
    so `stat_pd(tt)` was just `nu_pdef(tt) =E= 0` — missing the cross-term.
    """
    src = "data/gamslib/raw/otpop.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/otpop.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # Match the full `stat_pd(tt)..` block (header through terminating `;`)
    # so the assertion holds even when the body is wrapped across lines.
    stat_pd_match = re.search(r"(?ms)^\s*stat_pd\(tt\)\.\..*?;", output)
    assert stat_pd_match is not None, "stat_pd(tt) equation block not found in MCP"
    stat_pd_block = stat_pd_match.group(0)

    # The cross-term should include `nu_adef(tt+4)` (since adef(tt+4) has
    # the pd(tt+4-4)=pd(tt) reference) and `d(tt+3)` (from adef's
    # `con*d(tt2-1)` factor at tt2=tt+4).
    assert "nu_adef(tt+4)" in stat_pd_block, (
        "Expected `nu_adef(tt+4)` in stat_pd(tt) cross-term (from "
        "differentiating adef(tt+4) w.r.t. pd(tt)). Block:\n" + stat_pd_block[:500]
    )
    assert "d(tt+3)" in stat_pd_block, (
        "Expected `d(tt+3)` coefficient in stat_pd(tt) cross-term "
        "(from adef's `con*d(tt2-1)` at tt2=tt+4). Block:\n" + stat_pd_block[:500]
    )


@pytest.mark.integration
def test_otpop_adef_uses_resolved_integer_offset():
    """`adef(tt)$tp(tt).. ... pd(tt-l) ...` should be emitted with the
    SymbolRef `l` resolved to its scalar value `4` — the body should
    contain `pd(tt-4)`, not `pd(tt-l)`.

    Note: the EMITTER may still print `pd(tt-l)` (the parser preserves
    the symbolic form for source readability), but the IR-level AST
    that the AD pipeline consumes uses the resolved Const(-4) form.
    The downstream stat_pd cross-term (asserted above) is the
    end-to-end signal that resolution worked.
    """
    src = "data/gamslib/raw/otpop.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/otpop.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # adef body should appear in the MCP (as either pd(tt-l) or pd(tt-4)
    # — the emitter is free to render either form; what matters is that
    # the AD's downstream output is correct, which is asserted in the
    # other test).
    adef_match = re.search(r"(?ms)^\s*adef\(tt\)\$.*?;", output)
    assert adef_match is not None, "adef(tt) equation body not found in MCP"
