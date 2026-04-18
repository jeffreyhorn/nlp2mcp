"""Regression tests for pre-solve parameter assignments that contain
``$``-conditional expressions.

Context: ``emit_pre_solve_param_assignments`` walks the raw Lark parse
tree to re-emit loop bodies that include a ``solve`` statement. Its
dispatcher (``_loop_tree_to_gams_subst_dispatch``) previously lacked
handlers for ``dollar_cond``, ``dollar_cond_paren`` and several atom
variants; those nodes fell through to the generic space-joiner, which
silently dropped the ``(...)`` that the grammar consumes. The result
on ``partssupply.gms`` was an emitted line

    icweight(i) = theta(i) $ not 0 + 1 - theta(i) + sqr(theta(i)) $ 0 ;

that GAMS rejects with Error 445 ("More than one operator in a row").
This test file pins the emitter to preserve parentheses on every
``$``-conditional shape that appears in realistic pre-solve bodies.
"""

import pytest

from src.emit.original_symbols import emit_pre_solve_param_assignments
from src.ir.parser import parse_model_text


@pytest.mark.integration
def test_pre_solve_dollar_cond_paren_both_sides_get_parens():
    """``(lhs_expr)$(cond)`` must emit parens on both sides.

    The original breakage was that ``(1 - a + sqr(a))$(0)`` lost its
    LHS grouping, so GAMS parsed ``... + sqr(a)$(0)`` — associativity
    moved with ``$``'s higher precedence and the semantics flipped.
    """
    code = """
    Set i / 1*2 /;
    Set t / 1*1 /;
    Parameter a(i) / '1' 0.5, '2' 0.25 /;
    Parameter q(i);
    Variable z;
    Equation obj;
    obj.. z =e= sum(i, a(i));
    Model m / obj /;
    loop(t,
        q(i) = a(i)$(not 0) + (1 - a(i) + sqr(a(i)))$(0);
        solve m using nlp maximizing z;
    );
    """
    model = parse_model_text(code)
    emitted = emit_pre_solve_param_assignments(model)

    # Condition parens preserved on both conditionals.
    assert "$(not 0)" in emitted
    assert "$(0)" in emitted
    # LHS grouping preserved when it's a compound (binop) expression.
    assert "(1 - a(i) + sqr(a(i)))$(0)" in emitted
    # Regression: no bigram that would parse as Error 445.
    assert "$ not" not in emitted
    assert "$ 0" not in emitted
    assert "sqr(a(i)) $" not in emitted


@pytest.mark.integration
def test_pre_solve_bare_dollar_cond_wraps_rhs():
    """``term $ term`` (grammar ``dollar_cond``) must wrap the RHS in
    parens to avoid operator-adjacency errors when the RHS is a unary/
    binary expression (e.g., ``not 0``, ``x + y``).
    """
    code = """
    Set i / 1*2 /;
    Set t / 1*1 /;
    Parameter a(i) / '1' 0.5, '2' 0.25 /;
    Parameter q(i);
    Variable z;
    Equation obj;
    obj.. z =e= sum(i, a(i));
    Model m / obj /;
    loop(t,
        q(i) = a(i)$not 0;
        solve m using nlp maximizing z;
    );
    """
    model = parse_model_text(code)
    emitted = emit_pre_solve_param_assignments(model)
    assert "$(not 0)" in emitted
    assert "$ not" not in emitted


@pytest.mark.integration
def test_pre_solve_partssupply_icweight_line_is_gams_valid():
    """End-to-end: translate the real partssupply source and assert the
    ``icweight`` assignment emitted from the solve-loop has no ``$ not``
    / ``sqr(...) $ 0`` bigrams that trip GAMS Error 445.
    """
    from pathlib import Path

    src = Path("data/gamslib/raw/partssupply.gms")
    if not src.exists():
        pytest.skip("partssupply.gms not present (CI without gamslib raw)")

    import sys

    sys.setrecursionlimit(50000)

    from src.ir.parser import parse_model_file

    model = parse_model_file(src)
    emitted = emit_pre_solve_param_assignments(model)
    # icweight assignment must be present and well-parenthesized.
    icw_lines = [ln for ln in emitted.splitlines() if ln.lstrip().startswith("icweight")]
    assert icw_lines, "icweight assignment was not emitted"
    icw = icw_lines[0]
    # Error-445 fingerprints:
    assert "$ not" not in icw
    assert "sqr(theta(i)) $" not in icw
    # Expected shape:
    assert "theta(i)$(not 0)" in icw
    assert "(1 - theta(i) + sqr(theta(i)))$(0)" in icw
