"""Sprint 25 / #1234: otpop corpus regression for scalar-constant offset
resolution + boundary `_fx_` deduplication.

Pre-fix: `otpop`'s `adef` equation uses `pd(tt-l)` where `Scalar l /4/`.
The parser produced `IndexOffset('tt', Unary('-', SymbolRef('l')))`,
which the AD engine couldn't differentiate (treats SymbolRef('l') as
opaque). As a result, `stat_pd(tt)` was missing the cross-term from
differentiating `adef(tt+4)` w.r.t. `pd(tt)`, producing an
INCONSISTENT KKT system that PATH couldn't satisfy. Separately, the
boundary year 1974 (in both `th = 1965*1974` and `t = 1974*1990`)
hit a duplicate-`x.fx`/`x_fx_1974`-equation conflict that GAMS
rejected with "MCP pair has unmatched equation" → EXECERROR=1.

Post-fix (this PR):
- The IR normalizer's `resolve_scalar_offsets` pass substitutes
  `l → 4`, producing `IndexOffset('tt', Const(-4))`. The AD
  machinery then correctly cross-attributes the offset, and
  `stat_pd(tt)` includes the missing `-con*d(tt+3)*nu_adef(tt+4)`
  term.
- The variable-bounds emit no longer writes `x.fx('1974') = 29.4`
  because `x_fx_1974` is in the MCP and fixes x("1974") through
  complementarity. The pair `x_fx_1974.nu_x_fx_1974` is matched.

End-to-end: otpop now reaches MODEL STATUS 1 Optimal at
`pi=2307.07` (was: EXECERROR=1 abort). The remaining objective gap
to the NLP's `pi=4217.80` is caused by two AD bugs that are
independent of the original symptom of #1234 and tracked under
their own issues (#1334 sum-collapse, #1335 missing zdef
cross-term). #1234 itself is closed.
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
def test_otpop_x_fx_1974_no_redundant_dot_fx():
    """Issue #1234 (boundary fix): otpop's `th = 1965*1974` and
    `t = 1974*1990` overlap on '1974'. The KKT pipeline emits an
    `x_fx_1974.. x("1974") - 29.4 =E= 0` equation paired with the
    multiplier `nu_x_fx_1974` because '1974' IS in the active
    stationarity domain for x.

    Pre-fix the emitter ALSO produced an unconditional
    `x.fx('1974') = 29.4` line in the variable-bounds section.
    GAMS held-fixed the column, leaving the `x_fx_1974` row empty
    and reporting "MCP pair x_fx_1974.nu_x_fx_1974 has unmatched
    equation" → EXECERROR=1.

    Post-fix the redundant `.fx` is suppressed when the eq is in
    the MCP (not in `suppressed_fx`), so the equation alone fixes
    x("1974") through complementarity.
    """
    src = "data/gamslib/raw/otpop.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/otpop.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    # The equation must be in the MCP, paired with its multiplier.
    assert 'x_fx_1974.. x("1974") - 29.4 =E= 0;' in output
    assert "x_fx_1974.nu_x_fx_1974" in output

    # The redundant `.fx('1974')` line must NOT appear.
    assert "x.fx('1974')" not in output

    # Suppressed siblings (1965-1973, outside `t`) DO emit `.fx` (each
    # appears at least once: in the variable-bounds section and again in
    # the suppressed-fx fallback section, GAMS treats duplicates as
    # last-write-wins).
    for year in (1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973):
        assert f"x.fx('{year}') = 29.4;" in output


@pytest.mark.integration
def test_otpop_adef_uses_resolved_integer_offset():
    """Smoke test: the conditional `adef(tt)$...` equation block survives
    the parse → normalize → AD → emit pipeline.

    What this test asserts: an `adef(tt)$...` block exists in the emitted
    MCP. Nothing more. The emitter renders the offset symbolically
    (`pd(tt-l)`) regardless of whether the IR has been rewritten — both
    forms are equivalent at the GAMS-text level, so asserting the
    rendered offset wouldn't validate scalar-offset resolution.

    The actual signal that scalar-offset resolution worked is the
    presence of the cross-term `nu_adef(tt+4) * d(tt+3)` in `stat_pd(tt)`
    — asserted in `test_otpop_stat_pd_includes_cross_term_from_adef`
    above. Without resolution, the AD engine treats `SymbolRef('l')` as
    opaque and the cross-term is missing entirely.

    This test stays separate to catch regressions where the adef block
    fails to emit at all (e.g., a normalize/AD bug that drops the
    equation), distinct from the cross-term test which would fail with
    a more specific message.
    """
    src = "data/gamslib/raw/otpop.gms"
    if not os.path.exists(src):
        pytest.skip("data/gamslib/raw/otpop.gms is gitignored on this runner.")

    output = _emit_mcp_for(src)

    adef_match = re.search(r"(?ms)^\s*adef\(tt\)\$.*?;", output)
    assert adef_match is not None, "adef(tt) equation body not found in MCP"
