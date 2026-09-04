"""Regression tests for Pattern C Phase B-4 — the *full-collapse* member
(Sprint 39 Day 2, ISSUE_1714 / #1381).

B-4 fires when a multi-index ``Sum`` binds EVERY coordinate of a
higher-dimensional variable while the equation's own index binds none of them,
e.g. dyncge's::

    eqXp(i)..  Xp(i) =e= alpha(i)*(sum((h,j), pf(h,j)*F(h,j)) - Sp - Td)/pq(i);

⚠ WHAT THESE TESTS PIN, AND WHY THEY TARGET THE PREDICATE RATHER THAN THE EMIT.

The discriminating condition is **same set root, different symbol**, and during
implementation *each half alone was wrong, silently*:

* **canonical sets only** matched **nothing** — under ``Alias (i,j)`` the
  variable's ``j`` resolves to ``i``, so the test reported "related" for exactly
  the shape it exists to catch;
* **symbols only** matched the **whole corpus** — 10 goldens drifted against a
  measured baseline of zero (agreste, egypt, fawley, shale, tforss, turkey),
  because B-4 was rewriting emits the standard path already produced correctly.

The second version passed ``make test``, ``typecheck`` and ``lint``; only a leak
gate run against a measured baseline caught it. So the regression that matters is
**over- and under-matching of the predicate**, and that is what is asserted here.

⚠ These deliberately do NOT assert on emitted text. Measured: on both synthetic
shapes below the emitter produces byte-identical output with and without B-4 —
the standard path already handles them — so an emit-level assertion would pass
whether or not B-4 exists, i.e. it would prove nothing (the "a test that mirrors
the logic it checks" failure). The only shape that discriminates at the emit
level is dyncge itself, whose source is git-ignored and unavailable in CI.
"""

from __future__ import annotations

import sys

import pytest

# A 2-D variable fully bound by a multi-index Sum, with the equation's own index
# `c` sharing a set root with the variable's `j` via `Alias (i,j)` but written as
# a DIFFERENT symbol. This is dyncge's shape, minimised.
ALIAS_COLLISION = """\
Set i /i1*i3/, h /h1,h2/;
Alias (i,j);
Parameter a(i), q(i);
a(i) = 1; q(i) = 2;
Variables x(h,i), w(h,i), y(i), obj;
Equations eqy(i), eobj;
eqy(i)..  y(i) =e= a(i)*(sum((h,j), x(h,j)*w(h,j)) - 1)/q(i);
eobj..    obj =e= sum(i, y(i));
Model m /all/;
Solve m maximizing obj using nlp;
"""

# Structurally the same full-collapse shape, but the equation's index `c` and the
# variable's coordinates `(p,s)` come from UNRELATED sets — no alias, no shared
# root. The standard path already emits this correctly across the corpus, so B-4
# must decline it. This is the case the symbols-only predicate wrongly claimed.
UNRELATED_SETS = """\
Set c /c1*c3/, p /p1,p2/, s /s1,s2/;
Parameter a(c), q(c);
a(c) = 1; q(c) = 2;
Variables x(p,s), w(p,s), y(c), obj;
Equations eqy(c), eobj;
eqy(c)..  y(c) =e= a(c)*(sum((p,s), x(p,s)*w(p,s)) - 1)/q(c);
eobj..    obj =e= sum(c, y(c));
Model m /all/;
Solve m maximizing obj using nlp;
"""


def _b4_claims(gams_text: str, tmp_path) -> list[tuple[str, str]]:
    """Run the real emit pipeline, returning the (equation, variable) pairs that
    ``_find_full_collapse_pattern_c`` actually claimed."""
    gams_file = tmp_path / "m.gms"
    gams_file.write_text(gams_text)

    from src.kkt import stationarity as st

    claimed: list[tuple[str, str]] = []
    original = st._find_full_collapse_pattern_c

    def recording(eq_def, var_name, var_domain, model_ir):  # noqa: ANN001, ANN202
        out = original(eq_def, var_name, var_domain, model_ir)
        if out is not None:
            claimed.append((str(getattr(eq_def, "name", "?")), str(var_name)))
        return out

    old_limit = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    st._find_full_collapse_pattern_c = recording
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
        emit_gams_mcp(kkt)
    finally:
        st._find_full_collapse_pattern_c = original
        sys.setrecursionlimit(old_limit)
    return claimed


@pytest.mark.unit
def test_b4_claims_the_alias_collision_shape(tmp_path):
    """UNDER-matching guard.

    Fails against the canonical-sets-only predicate, which claimed nothing at
    all: ``Alias (i,j)`` collapses the variable's ``j`` onto the equation's
    ``i``, so a set-root comparison reports the two as related and the shape is
    rejected — the same conflation that produces the defect being fixed.
    """
    claimed = _b4_claims(ALIAS_COLLISION, tmp_path)
    assert ("eqy", "x") in claimed, (
        "B-4 must claim (eqy, x): a two-index Sum binds BOTH of x's coordinates "
        "while the equation index `i` binds neither, and `i`/`j` share a set root "
        f"under Alias (i,j) while being different symbols. Claimed: {claimed}"
    )


@pytest.mark.unit
def test_b4_declines_when_the_sets_are_unrelated(tmp_path):
    """OVER-matching guard — the corpus-leak regression.

    Fails against the symbols-only predicate, which claimed this shape and so
    rewrote emits the standard path already produced correctly. That version
    drifted 10 goldens against a zero-drift baseline while passing the full test
    suite, typecheck and lint.
    """
    claimed = _b4_claims(UNRELATED_SETS, tmp_path)
    assert claimed == [], (
        "B-4 must DECLINE the full-collapse shape when the equation's index and "
        "the variable's coordinates come from unrelated sets: the standard path "
        f"already emits it correctly, so claiming it is a corpus-wide leak. "
        f"Claimed: {claimed}"
    )
