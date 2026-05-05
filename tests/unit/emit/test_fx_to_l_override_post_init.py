"""Issue #1349: per-instance ``var.l(idx) = val`` lines emitted as the
``.fx → .l`` side-effect of an ``_fx_``-replaced source ``var.fx(idx) = val``
MUST emit AFTER the bulk ``var.l(t,n) = 1`` POSITIVE / denominator-FREE init
for the same variable, AND must be visible to the cross-variable topological
sort so dependent ``var.l = expr`` initializations see the override value.

clearlak surfaced the wrong-order shape: ``l.fx('dec', n) = 100`` for ~120
elements expanded into per-instance ``l.l('dec', 'n_i') = 100;`` overrides
under "Variable Bounds", and the subsequent ``l.l(t,n) = 1;`` POSITIVE init
in the Variable Initialization section immediately overwrote them.

The fix integrates the per-instance overrides INTO the same variable's
init group (after its bulk init / clamp lines) rather than emitting them
as a separate post-init section. That way:

1. The override emits AFTER the bulk init for the SAME variable (overriding
   the wildcard).
2. The override is visible to the topological sort, so any other variable
   whose ``.l = expr`` references this var's ``.l(idx)`` evaluates against
   the correct override value.
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
# side-effect without the integrated-override fix.
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
def test_fx_to_l_override_emitted_after_bulk_init_for_same_var():
    """The per-instance ``l.l('dec', 'n_i') = 100`` override must appear
    AFTER the bulk ``l.l(t,n) = 1`` (or any wildcard ``l.l(...) = ...``)
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


# Cross-var dependency: vy depends on vx via a `vy.l = vx.l('dec') * 2;`
# style assignment. vx has a `.fx → .l` override at 'dec'. The override
# must emit before vy's init so vy sees the correct value (200, not 2).
_SRC_FX_WITH_DEPENDENT_INIT = """
Set t / dec, jan /;
Variables vx(t), vy, obj;
vx.fx('dec') = 100;
vy.l = vx.l('dec') * 2;
Equation Objective, Bal(t);
Objective.. obj =e= sum(t, vx(t)) + vy;
Bal(t).. vx(t) =g= 1;
Model m /all/;
Solve m using nlp minimizing obj;
"""


@pytest.mark.unit
def test_fx_to_l_override_visible_to_dependent_var_init():
    """A dependent variable's `.l = expr` referencing the fixed variable's
    `.l('dec')` must emit AFTER the override line, so the dependent var
    evaluates against the override value (100), not the un-overridden
    state. Without integrating the override into the per-var init group
    + topo sort, the dependent var emits BEFORE the override and reads
    the wrong value.
    """
    output = _emit_mcp_for_source(_SRC_FX_WITH_DEPENDENT_INIT)
    lines = output.splitlines()

    override_idx = next(
        (
            i
            for i, ln in enumerate(lines)
            if ln.strip().startswith("vx.l('dec') =") or ln.strip().startswith('vx.l("dec") =')
        ),
        None,
    )
    # Element-quote style for the dependent line may differ from the override
    # line (expression-emit vs literal-key emit); accept either.
    dependent_idx = next(
        (
            i
            for i, ln in enumerate(lines)
            if ln.strip().startswith("vy.l =") and "vx.l(" in ln and "dec" in ln
        ),
        None,
    )
    assert (
        override_idx is not None
    ), f"Expected `vx.l('dec') = 100;` override line; output:\n{output}"
    assert (
        dependent_idx is not None
    ), f"Expected `vy.l = vx.l('dec') * 2;` dependent init line; output:\n{output}"
    assert dependent_idx > override_idx, (
        f"Dependent var init (line {dependent_idx}) must appear AFTER the fixed "
        f"variable's .l override (line {override_idx}) so it reads the override "
        f"value, not a pre-override state.\n"
        f"  override line:  {lines[override_idx]!r}\n"
        f"  dependent line: {lines[dependent_idx]!r}"
    )
