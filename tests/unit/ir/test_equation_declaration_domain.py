"""Sprint 25 / #1327: parser tracks declaration domain separately from body.

When an equation is declared as `Equation Constraints(mm);` and defined
as `Constraints(m).. ...`, the IR must capture both:
- `domain = ("m",)` (body head — used for iteration filtering)
- `declaration_domain = ("mm",)` (declared parent set — used for KKT
  multiplier / complementarity equation declarations to avoid GAMS
  Error 187 on dynamic subsets used as declaration domains)
"""

from __future__ import annotations

import sys

import pytest


def _parse(src: str):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ir.normalize import normalize_model
        from src.ir.parser import parse_model_text

        model = parse_model_text(src)
        normalize_model(model)
        return model
    finally:
        sys.setrecursionlimit(old)


@pytest.mark.unit
def test_subset_body_records_separate_declaration_domain():
    """`Equation E(mm); E(m).. ...` should yield
    `domain=("m",)` and `declaration_domain=("mm",)`.
    """
    src = """
    Set
       mm / m1*m3 /;
    Set
       m(mm) 'subset of mm';
    Variable obj, x(mm);
    Equation Objective, E(mm);
    Objective.. obj =e= sum(mm$(m(mm)), x(mm));
    E(m).. x(m) =e= 1;
    Model lp / all /;
    Solve lp using nlp minimizing obj;
    """
    model = _parse(src)
    eq = model.equations.get("E")
    assert eq is not None
    assert eq.domain == ("m",), f"Expected body domain ('m',), got {eq.domain!r}"
    assert eq.declaration_domain == (
        "mm",
    ), f"Expected declaration_domain ('mm',), got {eq.declaration_domain!r}"


@pytest.mark.unit
def test_matching_domains_leaves_declaration_domain_none():
    """`Equation E(p); E(p).. ...` (declaration matches body) should
    leave `declaration_domain` unset (None) for backward-compat —
    only the parent/subset case carries the new field.
    """
    src = """
    Set p / p1, p2 /;
    Variable obj, y(p);
    Equation Objective, E(p);
    Objective.. obj =e= sum(p, y(p));
    E(p).. y(p) =e= 1;
    Model lp / all /;
    Solve lp using nlp minimizing obj;
    """
    model = _parse(src)
    eq = model.equations.get("E")
    assert eq is not None
    assert eq.domain == ("p",)
    assert eq.declaration_domain is None, (
        f"Expected declaration_domain None when domains match, " f"got {eq.declaration_domain!r}"
    )


@pytest.mark.unit
def test_scalar_equation_unaffected():
    """Scalar equations (no domain) carry `domain=()` and
    `declaration_domain=None`.
    """
    src = """
    Variable x, obj;
    Equation Objective, E;
    Objective.. obj =e= x;
    E.. x =e= 1;
    Model lp / all /;
    Solve lp using nlp minimizing obj;
    """
    model = _parse(src)
    eq = model.equations.get("E")
    assert eq is not None
    assert eq.domain == ()
    assert eq.declaration_domain is None


@pytest.mark.unit
def test_scalar_decl_indexed_body_records_arity_mismatch():
    """Issue #1330: `Equation E;` (scalar declaration) followed by
    `E(i).. body` (indexed body) — GAMS broadcasts and the equation
    becomes effectively indexed by `i`, but the IR records the
    scalar declaration in `declaration_domain` and the body domain
    in `domain`. Arities differ (0 vs 1).

    Encountered in camcge's `gdeq` equation (#1330). The MCP emitter's
    declaration-line emit must use `declaration_domain` here so the
    `$include`'d source's scalar declaration is mirrored — otherwise
    GAMS error 318 ("Domain list redefined") fires under
    `--nlp-presolve`.
    """
    src = """
    Set i / a, b /;
    Variable x(i), obj;
    Equation Objective, E;
    Objective.. obj =e= sum(i, x(i));
    E(i).. x(i) =e= 1;
    Model lp / all /;
    Solve lp using nlp minimizing obj;
    """
    model = _parse(src)
    eq = model.equations.get("E")
    assert eq is not None
    assert eq.domain == ("i",), f"Expected body domain ('i',), got {eq.domain!r}"
    assert (
        eq.declaration_domain == ()
    ), f"Expected scalar declaration_domain (), got {eq.declaration_domain!r}"
    assert len(eq.declaration_domain) != len(eq.domain)


@pytest.mark.unit
def test_emit_uses_declaration_domain_even_when_arity_differs():
    """Issue #1330: the equation-declaration line in `emit_equations`
    should emit the source's `declaration_domain` even when arities
    differ from the body. GAMS broadcasts the declaration to match
    the body's indices at solve time, so a scalar declaration with
    an indexed body is valid and self-consistent.
    """
    import sys

    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    src = """
    Set i / a, b /;
    Variable x(i), obj;
    Equation Objective, E;
    Objective.. obj =e= sum(i, x(i));
    E(i).. x(i) =e= 1;
    Model lp / all /;
    Solve lp using nlp minimizing obj;
    """
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(src)
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        output = emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old)

    # The Equations declaration line should be `E` (no domain),
    # mirroring the source's scalar declaration. The body that
    # follows uses `E(i)..` with the body domain.
    import re

    # Look for the Equations block declaration of E.
    decl_match = re.search(r"^\s*E\s*$", output, re.MULTILINE)
    assert decl_match is not None, (
        "Expected `E` (scalar form) in Equations block; the emitted MCP "
        "should mirror the source's `Equation E;` scalar declaration even "
        "when the body uses `E(i)..` indexing.\nOutput excerpt:\n"
        + "\n".join(line for line in output.splitlines() if "E" in line and "Equation" not in line)[
            :500
        ]
    )

    # The body should use the indexed form.
    body_match = re.search(r"^\s*E\(i\)\s*\.\.", output, re.MULTILINE)
    assert body_match is not None, "Expected body `E(i)..` in equation definitions"
