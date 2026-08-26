"""Sprint 38 Day 12 / #1693: reflexive equality equations need their multiplier
fixed on the diagonal.

`dyncge` writes a mobile-factor price-equalisation condition as

    eqpf2(h_mob,i,j)..  pf(h_mob,j) =e= pf(h_mob,i);      Alias (i,j);

The relation is **reflexive**, so at `i = j` it reads `pf = pf`: no constraint,
and nothing for a KKT multiplier to price. GAMS generates an empty row while
`nu_eqpf2` stays free, and rejects the pair — `**** MCP pair eqpf2.nu_eqpf2 has
empty equation but associated variable is NOT fixed`, once per diagonal element.

Sections 3/3a/3b of the emitter all key off a CONDITION (head, whole-body, or
inferred lead/lag). dyncge has none anywhere: the emptiness is a property of the
equation's own algebra under an index identification. Section 2c has tested
exactly that for *inequality* multipliers since #942 — the test was never
inequality-specific, it was only ever applied to inequalities. Section 3c
applies the same test to equalities.

Per #1693's gate, this fixture is a **minimal synthetic model, not dyncge**.
"""

from __future__ import annotations

import re
import sys
import textwrap

import pytest


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit(source: str, tmp_path) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    p = tmp_path / "m.gms"
    p.write_text(textwrap.dedent(source))
    model = parse_model_file(str(p))
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(kkt)


REFLEXIVE = """
    Set i / i1*i3 /;
    Alias (i,j);
    Variable v(i), obj;
    Equation defobj, e(i,j);
    e(i,j).. v(j) =e= v(i);
    defobj.. obj =e= sum(i, sqr(v(i) - 1));
    Model m / all /;
    solve m using nlp minimizing obj;
"""


@pytest.mark.unit
def test_reflexive_equality_multiplier_is_fixed_on_the_diagonal(tmp_path):
    out = _emit(REFLEXIVE, tmp_path)

    assert re.search(r"nu_e\.fx\(i,j\)\$\(ord\(i\) = ord\(j\)\) = 0;", out), (
        "expected the equality multiplier to be pinned on the diagonal; without "
        "it GAMS rejects the pair with 'has empty equation but associated "
        "variable is NOT fixed'.\nEmitted .fx lines:\n"
        + "\n".join(ln for ln in out.splitlines() if ".fx(" in ln)
    )


@pytest.mark.unit
def test_the_guard_is_diagonal_only_not_a_blanket_fix(tmp_path):
    """Off-diagonal instances are genuine constraints and must stay free.

    This is #1693's REPLAN condition: pinning a multiplier on a non-tautological
    instance silently changes the solution rather than erroring.
    """
    out = _emit(REFLEXIVE, tmp_path)

    fx_lines = [ln for ln in out.splitlines() if ln.startswith("nu_e.fx(")]
    assert fx_lines, "no nu_e.fx line emitted"
    for ln in fx_lines:
        assert "$(" in ln, f"unconditional multiplier fix would kill live rows: {ln!r}"
        assert "ord(i) = ord(j)" in ln, f"guard is not diagonal-only: {ln!r}"


@pytest.mark.unit
def test_non_reflexive_equality_gets_no_diagonal_guard(tmp_path):
    """The negative control: an equality whose diagonal is a REAL constraint
    must not be touched. `v(j) =e= 2*v(i)` at i=j means `v = 2v`, i.e. `v = 0` —
    informative, not tautological."""
    out = _emit(
        REFLEXIVE.replace("e(i,j).. v(j) =e= v(i);", "e(i,j).. v(j) =e= 2*v(i);"),
        tmp_path,
    )

    assert not re.search(r"nu_e\.fx\(i,j\)\$\(ord\(i\) = ord\(j\)\)", out), (
        "fixed the multiplier of a diagonal instance that is a genuine "
        "constraint — that is a silently wrong answer, not a tidied empty row"
    )


@pytest.mark.unit
def test_single_index_equality_is_untouched(tmp_path):
    """No same-set index pair -> section 3c cannot apply."""
    out = _emit(
        """
        Set i / i1*i3 /;
        Variable v(i), obj;
        Equation defobj, e(i);
        e(i).. v(i) =e= 1;
        defobj.. obj =e= sum(i, sqr(v(i) - 1));
        Model m / all /;
        solve m using nlp minimizing obj;
        """,
        tmp_path,
    )
    assert "nu_e.fx" not in out
