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
