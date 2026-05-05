"""PR #1360 review (Copilot): per-instance `var.l(idx) = val` lines from
the `.fx → .l` side-effect (Issue #1349) MUST be emitted AFTER the bulk
`var.l(t,n) = 1` Variable Initialization. Otherwise the wildcard bulk
init clobbers the per-instance value.

clearlak surfaced this: `l.fx('dec', n) = 100` for ~120 elements expanded
into per-instance `l.l('dec', 'n_i') = 100;` overrides under "Variable
Bounds", which the subsequent `l.l(t,n) = 1;` POSITIVE init in the
Variable Initialization section immediately overwrote, defeating the
purpose of the #1349 fix.

The fix moves the `.l` overrides into a new "Fixed-Variable .l
Side-Effect (post-bulk-init)" section that emits AFTER the bulk init,
so the per-instance value wins.
"""

from __future__ import annotations

import sys

import pytest


def _emit_mcp_for_source(gams_src: str) -> str:
    """Emit MCP from in-memory GAMS source."""
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(gams_src)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)


# clearlak-shaped synthetic: a POSITIVE variable indexed over (t, n) with
# per-instance .fx assignments for one slice of the t domain. The bulk
# var-init pass (POSITIVE → `var.l(t,n) = 1`) would clobber the .fx
# side-effect without the post-init fix.
_SRC_FX_OVER_POSITIVE_VAR = """
Set t / dec, jan, feb /;
Set n / n1, n2, n3 /;
Positive Variables l(t,n);
Variable obj;
l.fx('dec', 'n1') = 100;
l.fx('dec', 'n2') = 100;
l.fx('dec', 'n3') = 100;
Equation Objective, Bal(n);
Objective.. obj =e= sum((t,n), l(t,n));
Bal(n).. sum(t, l(t,n)) =g= 50;
Model m /all/;
Solve m using nlp minimizing obj;
"""


@pytest.mark.unit
def test_fx_to_l_override_emitted_after_bulk_init():
    """The per-instance `l.l('dec', 'n_i') = 100` override must appear
    AFTER the bulk `l.l(t,n) = 1` (or any wildcard `l.l(...) = ...`)
    Variable Initialization line. Otherwise the bulk init clobbers it
    at GAMS evaluation time.
    """
    output = _emit_mcp_for_source(_SRC_FX_OVER_POSITIVE_VAR)
    lines = output.splitlines()

    # Find the bulk-init line index (matches `l.l(t,n) = ...` with the
    # set names as wildcards, NOT a quoted element label).
    bulk_init_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith("l.l(t,n) =")),
        None,
    )
    assert (
        bulk_init_idx is not None
    ), f"Expected a bulk `l.l(t,n) = ...` POSITIVE init line; output:\n{output}"

    # Find the per-instance override line index for one of the .fx targets.
    override_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip().startswith("l.l('dec','n1') =")),
        None,
    )
    assert override_idx is not None, (
        f"Expected `l.l('dec','n1') = 100;` override line "
        f"(Issue #1349 .fx → .l side-effect); output:\n{output}"
    )

    assert override_idx > bulk_init_idx, (
        f"Per-instance .l override (line {override_idx}) must appear AFTER "
        f"the bulk `l.l(t,n) = ...` init (line {bulk_init_idx}). "
        f"Otherwise the bulk init clobbers the override.\n"
        f"  bulk init line: {lines[bulk_init_idx]!r}\n"
        f"  override line:  {lines[override_idx]!r}"
    )


@pytest.mark.unit
def test_fx_to_l_override_section_header_present():
    """The post-init override section emits its own labeled comment block
    so the ordering intent is visible to maintainers reading the .gms.
    """
    output = _emit_mcp_for_source(_SRC_FX_OVER_POSITIVE_VAR)
    assert "Fixed-Variable .l Side-Effect (post-bulk-init)" in output, (
        "Expected the post-init `.l` override section to carry a labeled "
        f"comment header; output:\n{output}"
    )
