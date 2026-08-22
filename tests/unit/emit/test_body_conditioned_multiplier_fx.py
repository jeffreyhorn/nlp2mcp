"""Multiplier `.fx` guards for equalities conditioned on the BODY, not the head.

Issue #1331 (twocge, Sprint 38 Day 9). The emitter fixes an equality's multiplier
to 0 wherever the equation is conditioned away, but it read only the condition on
the equation *head*::

    eq(i,j)$(ord(i) <> ord(j))..  a(i) - b(j) =e= 0;      -- handled
    eq(i,j)..  (a(i) - b(j))$(ord(i) <> ord(j)) =e= 0;    -- NOT handled

The two are semantically identical -- the row is structurally empty on the
diagonal either way -- but the second leaves ``eq_def.condition is None``, so the
multiplier was never fixed and GAMS rejected the pair with *"MCP pair eq.nu_eq has
empty equation but associated variable is NOT fixed"*.

The lift is only sound when the ``$`` spans the whole side **and the other side is
zero**. If the other side were a non-zero constant, a false condition gives
``0 =e= 5`` -- an *infeasible* row, not an empty one -- and fixing the multiplier
there would silently discard a real constraint rather than tidy an absent one. That
asymmetry is what the negative test below pins.
"""

import sys

import pytest


def _emit(gams_source: str, tmp_path, name: str) -> str:
    """Run the full parse -> KKT -> emit pipeline and return the emitted MCP text."""
    gams_file = tmp_path / f"{name}.gms"
    gams_file.write_text(gams_source)

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.emit.emit_gams import emit_gams_mcp
        from src.ir.normalize import normalize_model
        from src.ir.parser import parse_model_file
        from src.kkt.assemble import assemble_kkt_system

        model = parse_model_file(str(gams_file))
        normalize_model(model)
        j_eq, j_ineq = compute_constraint_jacobian(model)
        grad = compute_objective_gradient(model)
        kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
        return emit_gams_mcp(kkt)
    finally:
        sys.setrecursionlimit(old_limit)


#: `(expr)$c =e= 0` -- the twocge shape. The row is empty wherever `c` is false.
_BODY_CONDITIONED = """\
Set i / i1, i2 /;
Alias(i, j);
Variable a(i), b(i), obj;
Equation eq(i,j), objdef;
eq(i,j).. (a(i) - b(j))$(ord(i) <> ord(j)) =e= 0;
objdef.. obj =e= sum(i, a(i) + b(i));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""

#: The same restriction written on the HEAD -- already handled before #1331.
#: Included so the test proves the two forms now agree, rather than just that
#: the new path emits *something*.
_HEAD_CONDITIONED = """\
Set i / i1, i2 /;
Alias(i, j);
Variable a(i), b(i), obj;
Equation eq(i,j), objdef;
eq(i,j)$(ord(i) <> ord(j)).. a(i) - b(j) =e= 0;
objdef.. obj =e= sum(i, a(i) + b(i));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""

#: `(expr)$c =e= 5` -- NOT liftable. A false `c` gives `0 =e= 5`, which is an
#: INFEASIBLE row, not an empty one.
_NONZERO_OTHER_SIDE = """\
Set i / i1, i2 /;
Alias(i, j);
Variable a(i), b(i), obj;
Equation eq(i,j), objdef;
eq(i,j).. (a(i) - b(j))$(ord(i) <> ord(j)) =e= 5;
objdef.. obj =e= sum(i, a(i) + b(i));
Model m / eq, objdef /;
solve m using nlp minimizing obj;
"""


def _nu_fx_lines(emitted: str) -> list[str]:
    return [ln for ln in emitted.splitlines() if ln.startswith("nu_eq.fx(")]


@pytest.mark.unit
def test_body_conditioned_equality_gets_multiplier_fx(tmp_path):
    """FAIL-BEFORE (#1331): a body-wide `$` emitted no guard at all.

    twocge's emitted model contained ZERO `nu_*.fx(` lines, so GAMS aborted with
    `EXECERROR = 8` on eight empty pairs.
    """
    emitted = _emit(_BODY_CONDITIONED, tmp_path, "body_cond")
    lines = _nu_fx_lines(emitted)

    assert lines, (
        "expected a nu_eq.fx guard for the body-conditioned equality; "
        "without it GAMS reports 'empty equation but associated variable is NOT fixed'"
    )
    # The guard must be the COMPLEMENT of the active condition.
    assert any(
        "$(not (" in ln for ln in lines
    ), f"guard must negate the active condition, got: {lines}"
    assert any(
        "ord(i)" in ln and "ord(j)" in ln for ln in lines
    ), f"guard must carry the lifted condition, got: {lines}"


@pytest.mark.unit
def test_body_and_head_conditioned_forms_agree(tmp_path):
    """The two spellings are semantically identical, so their guards must match.

    This is the assertion that matters: it pins the *equivalence* rather than
    merely checking the new branch produces output.
    """
    body = _nu_fx_lines(_emit(_BODY_CONDITIONED, tmp_path, "body_eq"))
    head = _nu_fx_lines(_emit(_HEAD_CONDITIONED, tmp_path, "head_eq"))

    assert body and head, f"both forms must emit a guard; body={body} head={head}"
    assert body == head, (
        "a condition on the body and the same condition on the head describe the "
        f"same empty rows, so the emitted guards must be identical.\n"
        f"  body: {body}\n  head: {head}"
    )


@pytest.mark.unit
def test_nonzero_other_side_is_NOT_lifted(tmp_path):
    """`(expr)$c =e= 5` must NOT produce a guard — the row is infeasible, not empty.

    This is the negative half, and it is the one worth having: lifting here would
    fix a multiplier on a row that genuinely constrains the model, turning an
    infeasibility into a silently wrong answer.
    """
    emitted = _emit(_NONZERO_OTHER_SIDE, tmp_path, "nonzero_rhs")
    lines = _nu_fx_lines(emitted)

    assert not lines, (
        "a body condition against a NON-ZERO other side must not be lifted: "
        f"`0 =e= 5` is infeasible, not empty. Got: {lines}"
    )


@pytest.mark.unit
def test_whole_body_condition_returns_the_ACTIVE_condition(tmp_path):
    """Pin the helper's sense — callers negate it, so returning the complement
    would fix multipliers on exactly the live instances."""
    from src.emit.emit_gams import _whole_body_condition
    from src.ir.parser import parse_model_file

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        f = tmp_path / "sense.gms"
        f.write_text(_BODY_CONDITIONED)
        model = parse_model_file(str(f))
        cond = _whole_body_condition(model.equations["eq"])

        assert cond is not None, "the body-wide condition should be recoverable"
        # `<>` is the ACTIVE form as written in the source; the emptiness form
        # would be `=`. Returning the latter would invert every call site.
        assert "<>" in str(
            cond
        ), f"expected the ACTIVE condition (as written after `$`), got {cond!r}"

        # And a head-conditioned equation has no *body* condition to lift.
        f2 = tmp_path / "sense_head.gms"
        f2.write_text(_HEAD_CONDITIONED)
        model2 = parse_model_file(str(f2))
        assert (
            _whole_body_condition(model2.equations["eq"]) is None
        ), "a head condition is not a body condition; the helper must not claim it"
    finally:
        sys.setrecursionlimit(old_limit)
