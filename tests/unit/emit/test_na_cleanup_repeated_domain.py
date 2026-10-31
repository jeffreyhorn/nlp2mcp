"""Sprint 40 Day 8 (Class B, gussrisk): the NA-cleanup line of a parameter whose
DECLARATION repeats a symbol.

gussrisk declares ``covar(stocks,stocks)`` and assigns ``covar(s,sp) = .../card(e)``
with ``Alias (stocks,s,sp)``. In GAMS a repeated controlling index is one
iterator, so ``covar(stocks,stocks)$(NOT (...)) = 0;`` touched only the DIAGONAL
while the assignment filled the full matrix. The cleanup is now indexed by
distinct per-position symbols: the assignment's LHS tuple, else unused aliases.
"""

from __future__ import annotations

import pytest

from src.emit.original_symbols import emit_post_assignment_na_cleanup
from src.ir.parser import parse_model_text

pytestmark = pytest.mark.unit

BASE = """\
Set i / a, b, c /;
Alias (i,j,k);
Parameter q(i,i), p(i,i);
q(i,j) = ord(i) + ord(j);
{assign}
Variable x(i), obj;
Equation e, defobj;
e.. sum((i,j), p(i,j)*x(i)) =e= 1;
defobj.. obj =e= sum(i, sqr(x(i)));
Model m / all /;
solve m using nlp minimizing obj;
"""


def _cleanup(assign: str) -> str:
    return emit_post_assignment_na_cleanup(parse_model_text(BASE.format(assign=assign)))


def test_the_cleanup_uses_the_ASSIGNMENT_lhs_not_the_repeated_declaration():
    out = _cleanup("p(i,j) = 1/q(i,j);")
    assert "p(i,j)$(NOT (p(i,j) > -inf and p(i,j) < inf)) = 0;" in out, out
    assert "p(i,i)" not in out, out


def test_without_a_usable_lhs_UNUSED_ALIASES_make_the_positions_distinct():
    # A literal in the LHS: no all-symbol LHS tuple -> unused aliases of `i`.
    out = _cleanup("p('a',j) = 1/q('a',j);")
    assert "p(i,j)$(NOT (p(i,j) > -inf" in out, out
    assert "p(i,i)" not in out, out


def test_POSITIVE_CONTROL_a_domain_without_repeats_is_unchanged():
    model = parse_model_text(
        BASE.replace("Parameter q(i,i), p(i,i);", "Parameter q(i,i), p(i,k);").format(
            assign="p(i,k) = 1/q(i,k);"
        )
    )
    out = emit_post_assignment_na_cleanup(model)
    assert "p(i,k)$(NOT (p(i,k) > -inf and p(i,k) < inf)) = 0;" in out, out
