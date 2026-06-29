"""Sprint 29 / #1447: `find_objective_expression` must scope the objvar's
defining-equation search to the SOLVED model's equations.

A source file may declare several models that share an objvar but define it
differently. maxmin is the canonical case:

    maxmin1a / mindist1a /        mindist1a(low).. mindist =l= sqrt(...)
    maxmin2  / defdist, mindist2 /  mindist2..     mindist =e= smin(low, dist)

When the solved model is `maxmin1a`, the objective is the bare objvar `mindist`
(its only equation, `mindist1a`, is an indexed `=l=` *constraint*, not a scalar
`=e=` definition). Scanning ALL equations would match `mindist2`'s scalar `=e=`
definition and return `smin(low, dist)` — which has no `mindist`, so the objvar's
own gradient (`-1` after the MAX→min negation) is silently dropped from
`stat_mindist`, leaving a residual of 1.0.

The fix restricts the Case-2 search to `model_ir.get_solved_model_equations()`.
"""

from __future__ import annotations

import sys

import pytest


def _objective_expr(gams_src: str):
    from src.ad.gradient import find_objective_expression
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text

    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        model = parse_model_text(gams_src)
        normalize_model(model)
        return find_objective_expression(model), model
    finally:
        sys.setrecursionlimit(old)


# Two models share objvar `z`: the SOLVED model `m_used` maximizes `z` with only
# an indexed `=l=` constraint, while `m_other` (NOT solved) defines `z =e= ...`.
_SRC_MULTIMODEL = """
Set i / i1, i2, i3 /;
Variable z, x(i);
Equation cap(i), zdef;
cap(i)..  z =l= x(i);
zdef..    z =e= sum(i, x(i));
Model m_used  / cap /;
Model m_other / zdef /;
Solve m_used using lp maximizing z;
"""


@pytest.mark.unit
def test_objective_scoped_to_solved_model_uses_bare_objvar():
    """When the solved model contains no scalar `=e=` definition of the objvar,
    the objective is the bare objvar (VarRef) — NOT a definition pulled from an
    unsolved sibling model."""
    from src.ir.ast import VarRef

    obj_expr, model = _objective_expr(_SRC_MULTIMODEL)
    assert model.get_solved_model_equations() == ["cap"] or set(
        model.get_solved_model_equations() or []
    ) == {"cap"}
    # The bug would return `zdef`'s RHS (sum(i, x(i))); the fix returns VarRef(z).
    assert isinstance(obj_expr, VarRef), (
        f"Expected the bare objvar VarRef(z) (zdef is not in the solved model "
        f"m_used), got: {obj_expr!r}"
    )
    assert obj_expr.name.lower() == "z"


@pytest.mark.unit
def test_objective_uses_defining_eq_when_in_solved_model():
    """Control: when the objvar's `=e=` definition IS in the solved model, it is
    still used (the scoping doesn't break the normal case)."""
    from src.ir.ast import VarRef

    src = """
Set i / i1, i2, i3 /;
Variable z, x(i);
Equation cap(i), zdef;
cap(i)..  x(i) =l= 10;
zdef..    z =e= sum(i, x(i));
Model m / cap, zdef /;
Solve m using lp maximizing z;
"""
    obj_expr, model = _objective_expr(src)
    # zdef IS in the solved model → its RHS (sum(i, x(i))) is the objective.
    assert not (
        isinstance(obj_expr, VarRef) and obj_expr.name.lower() == "z"
    ), f"Expected zdef's RHS as the objective, got bare objvar: {obj_expr!r}"
