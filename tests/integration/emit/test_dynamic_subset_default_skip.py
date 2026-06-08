"""Sprint 27 #1424: `_emit_dynamic_subset_defaults` must NOT blanket-populate a
dynamic subset that the model assigns itself.

The "Populate empty dynamic subsets for stationarity conditions" block
(Issue #952) emits `subset(parent) = yes;` for dynamic subsets with no static
members that are referenced in stationarity conditions. That is correct for
genuinely-empty subsets, but when the model populates the subset itself
element-wise (e.g. camshape's `first('i1') = yes; ... middle(first) = no`),
the blanket `first(i) = yes;` runs first and is NOT cleared by the element
assignment — so `first`/`last` become the whole parent set and `middle`
collapses to empty, corrupting every constraint domain.

The fix skips the blanket default for any subset the model populates via a
`set_assignment`. These tests guard both directions at emit level (no GAMS
needed → runs in CI):
  - a model-assigned (element-wise) subset gets NO blanket default;
  - a genuinely-empty subset referenced in stationarity STILL gets the
    blanket (Issue #952 preserved).
"""

from __future__ import annotations

import re
import sys

import pytest


def _emit_mcp_for_source(gams_src: str) -> str:
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


def _populate_block(emit: str) -> str:
    """The text of the '* Populate empty dynamic subsets ...' block, or ''."""
    lines = emit.splitlines()
    out: list[str] = []
    inblock = False
    for line in lines:
        if "Populate empty dynamic subsets" in line:
            inblock = True
            continue
        if inblock:
            if line.strip().startswith("$offImplicitAssign"):
                break
            out.append(line)
    return "\n".join(out)


# A model whose dynamic subset `bnd` is assigned ELEMENT-WISE only
# (the camshape-style corrupting case): `bnd` should NOT be blanket-populated.
_MODEL_ASSIGNED_SRC = """
Set i / i1, i2, i3 /;
Set bnd(i);
bnd('i1') = yes;
bnd('i3') = yes;
Variable x(i), z;
x.lo(i) = 0.5;
x.up(i) = 5;
Equation obj, con(i);
obj.. z =e= sum(i, x(i));
con(bnd(i)).. sqr(x(i)) =l= 4;
Model m / all /;
solve m using nlp maximizing z;
"""

# A model whose dynamic subset `dz` is NEVER assigned (genuinely empty) but is
# referenced in a constraint domain condition: the Issue #952 blanket default
# MUST still be emitted so the stationarity `$`-condition can evaluate.
_GENUINELY_EMPTY_SRC = """
Set i / i1, i2, i3 /;
Set dz(i);
Variable x(i), z;
x.lo(i) = 0.5;
x.up(i) = 5;
Equation obj, con(i);
obj.. z =e= sum(i, x(i));
con(i)$dz(i).. sqr(x(i)) =l= 4;
Model m / all /;
solve m using nlp maximizing z;
"""


@pytest.mark.integration
def test_model_assigned_subset_gets_no_blanket_default():
    """#1424: an element-wise model-assigned subset must NOT be blanket-populated
    with `bnd(i) = yes;` (which the element assignment would not clear)."""
    emit = _emit_mcp_for_source(_MODEL_ASSIGNED_SRC)
    block = _populate_block(emit)
    assert not re.search(r"^\s*bnd\(\w+\)\s*=\s*yes;", block, re.MULTILINE), (
        "Blanket `bnd(parent) = yes;` was emitted for a model-assigned subset — "
        "this corrupts the model's own element-wise population (#1424).\n"
        f"Populate block:\n{block}"
    )
    # The model's own element assignments must remain.
    assert re.search(r"bnd\(.i1.\)\s*=", emit), "model's own bnd('i1') assignment missing"


@pytest.mark.integration
def test_genuinely_empty_subset_keeps_blanket_default():
    """Issue #952 preserved: a referenced-but-never-assigned dynamic subset
    must STILL receive the blanket `dz(i) = yes;` default."""
    emit = _emit_mcp_for_source(_GENUINELY_EMPTY_SRC)
    block = _populate_block(emit)
    assert re.search(r"^\s*dz\(\w+\)\s*=\s*yes;", block, re.MULTILINE), (
        "Genuinely-empty dynamic subset `dz` lost its Issue #952 blanket default "
        "— the fix is skipping too broadly.\n"
        f"Populate block:\n{block!r}"
    )
