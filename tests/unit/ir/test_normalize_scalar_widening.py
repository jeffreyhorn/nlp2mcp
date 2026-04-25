"""Issue #1279 regression: when an equation declaration has the comma-shape
``Equation a, b(i);`` (multiple names with the parens attached to the
trailing one), only the trailing name should carry the domain. Earlier
names must remain SCALAR.

Pre-fix, this hit Lark's `eqn_head_domain_list` rule and the parser
indiscriminately applied the domain to ALL names — emitting `card(domain)`
identical instances of an otherwise-scalar equation, with a
correspondingly redundant multiplier vector. On robustlp this widened
``Equation defobj, cons(i);`` so that ``defobj`` was emitted as
``defobj(i).. obj =E= sum(j, c(j) * x(j))`` — `i` doesn't appear in the
body, so all card(i) instances are mathematically identical, and the
KKT system becomes rank-deficient (PATH terminates Locally Infeasible).

Note: the actual fix lives in `src/ir/parser.py::_handle_equations_block`'s
`eqn_head_domain_list` branch, NOT in `src/ir/normalize.py` as the
Sprint 25 Day 8 prompt initially suggested. The grammar collapses
``a, b(i)`` into a flat (id_list, domain_list) pair via Lark's Earley
parser without producing an `_ambig` node, so the fix has to land in
the post-parse handler. The test name is preserved per the Day 8 prompt
(scalar-widening invariant).
"""

from __future__ import annotations

import sys

import pytest


@pytest.mark.unit
def test_trailing_domain_does_not_widen_earlier_scalar_equation():
    """`Equation a, b(i);` must produce a scalar `a` and an `i`-domain `b`."""
    sys.setrecursionlimit(50000)
    from src.ir.parser import parse_model_text

    text = """
Set i / 1*3 /;
Variable obj, x(i);
Equation defobj, cons(i);
defobj.. obj =e= sum(i, x(i));
cons(i).. x(i) =l= 1;
Model m / defobj, cons /;
"""
    model = parse_model_text(text)
    assert "defobj" in model.equations
    assert "cons" in model.equations

    assert model.equations["defobj"].domain == (), (
        "Pre-fix: `defobj` inherited `(i,)` from the trailing-domain comma "
        "shape, generating card(i) identical instances of a body that has "
        "no `i` dependence. Post-fix: `defobj` must remain scalar so the "
        f"emission produces a single instance. Got domain={model.equations['defobj'].domain}"
    )
    assert model.equations["cons"].domain == ("i",), (
        "The trailing name must carry the domain — that's where the parens "
        f"attach syntactically. Got domain={model.equations['cons'].domain}"
    )


@pytest.mark.unit
def test_three_names_with_trailing_domain():
    """`Equation a, b, c(i);` → a scalar, b scalar, c(i)."""
    sys.setrecursionlimit(50000)
    from src.ir.parser import parse_model_text

    text = """
Set i / 1*2 /;
Variable z, x(i);
Equation a, b, c(i);
a.. z =e= 1;
b.. z =e= 2;
c(i).. x(i) =l= 1;
Model m / a, b, c /;
"""
    model = parse_model_text(text)
    assert model.equations["a"].domain == ()
    assert model.equations["b"].domain == ()
    assert model.equations["c"].domain == ("i",)


@pytest.mark.unit
def test_single_indexed_equation_unchanged():
    """`Equation eq(i);` (the non-comma single-name form) must continue to
    produce an `i`-domain equation. This locks in the previously-correct
    branch (`eqn_head_domain`) so the #1279 fix to `eqn_head_domain_list`
    doesn't regress it.
    """
    sys.setrecursionlimit(50000)
    from src.ir.parser import parse_model_text

    text = """
Set i / 1*2 /;
Variable z, x(i);
Equation eq(i);
eq(i).. x(i) =l= 1;
Model m / eq /;
solve m using lp minimizing z;
"""
    model = parse_model_text(text)
    assert model.equations["eq"].domain == ("i",)


@pytest.mark.unit
def test_comma_separated_no_domain_all_scalar():
    """`Equation a, b;` → both names scalar (the no-domain comma case)."""
    sys.setrecursionlimit(50000)
    from src.ir.parser import parse_model_text

    text = """
Variable z;
Equation a, b;
a.. z =e= 1;
b.. z =e= 2;
Model m / a, b /;
"""
    model = parse_model_text(text)
    assert model.equations["a"].domain == ()
    assert model.equations["b"].domain == ()


@pytest.mark.unit
def test_robustlp_defobj_emitted_scalar_end_to_end():
    """End-to-end check: parsing the full robustlp.gms produces a scalar
    `defobj` equation, NOT an `(i,)`-widened one. Skipped if the gamslib
    sources aren't available locally (CI). Mirrors the gamslib-skip
    convention used in `tests/unit/emit/test_nlp_presolve_include_path.py`
    and elsewhere.
    """
    sys.setrecursionlimit(50000)
    import os

    src = "data/gamslib/raw/robustlp.gms"
    if not os.path.exists(src):
        pytest.skip(
            "data/gamslib/raw/robustlp.gms is gitignored; run "
            "scripts/download_gamslib_raw.sh to populate the corpus."
        )

    from src.ir.parser import parse_model_file

    model = parse_model_file(src)
    defobj = model.equations.get("defobj")
    assert defobj is not None, "robustlp must declare a `defobj` equation"
    assert defobj.domain == (), (
        "`defobj` is declared scalar in `Equation defobj, cons(i);` and its "
        "body `obj =e= sum(j, c(j)*x(j))` has no `i` dependence. Pre-#1279 "
        "fix, the parser widened it to `defobj(i)`, producing a "
        "card(i)-redundant equation. Post-fix the equation must remain scalar. "
        f"Got domain={defobj.domain}"
    )
