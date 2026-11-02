"""#1787 (Sprint 40 Day 8, P4): a variable referenced twice, with the equation
index at DIFFERENT positions, gets one stationarity term per reference.

egypt's ``fodb(r,cf).. … + sum(rp$tranc(r,rp), trans(cf,rp,r) - trans(cf,r,rp))$ct(cf)``
against ``trans(c,r,rp)`` needs ``+nu_fodb(rp,c)$tranc(rp,r) - nu_fodb(r,c)$tranc(r,rp)``
(Prep Task 10 §2's hand-derived pair). Consolidating every Jacobian entry into one
representative kept a single term, built on a diagonal instance:
``1$(tranc(rp,rp))*nu_fodb(r,c)`` (P2's ``tranc(rp,rp)``).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# The bare shape. NLP 1.3333; before: no solve.
TWO_REFERENCES = """\
Set r / r1*r3 /, c / c1*c2 /;
Alias (r,rp);
Set tranc(r,rp);
tranc(r,rp) = yes$(ord(r) <> ord(rp));
Parameter d(r,c);
d(r,c) = ord(r) - 2 + ord(c)/4;
Positive Variable trans(c,r,rp);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,c).. sum(rp$tranc(r,rp), trans(c,rp,r) - trans(c,r,rp)) =e= d(r,c) - sum(rp, d(rp,c))/card(r);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# egypt's own shape: subset `cf(c)`, the outer `$ct(cf)`, a PARAMETER `tranc`, and
# another variable on the other side. NLP 33.25; before: 34.75 (silent).
EGYPT_SHAPE = """\
Set r / r1*r3 /, c / c1*c3 /, cf(c) / c1, c2 /, ct(c) / c2, c3 /;
Alias (r,rp);
Parameter tranc(r,rp), d(r,c);
tranc(r,rp) = 1$(ord(r) <> ord(rp));
d(r,c) = 2 + ord(r) - ord(c)/2;
Positive Variable trans(c,r,rp), fodder(r,c);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,cf).. fodder(r,cf) =e= d(r,cf) + sum(rp$tranc(r,rp), trans(cf,rp,r) - trans(cf,r,rp))$ct(cf);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp))) + sum((r,c), sqr(fodder(r,c) - 1));
Model m / all /;
solve m using nlp minimizing obj;
"""


# PR #1791 review: two references share a placement but use DIFFERENT binders
# (`sum(j$a(i,j), x(i,j)) + sum(k$b(i,k), x(i,k))`); each binder's mapping must be
# kept, or `b(i,k)` keeps an uncontrolled `k`. NLP 0.3241 (before: no solve).
BINDERS_PER_PLACEMENT = """\
Set i / i1*i3 /;
Alias (i,j,k);
Set a(i,j), b(i,j), c(i,j);
a(i,j) = yes$(ord(j) > ord(i)); b(i,j) = yes$(ord(j) = ord(i) + 1); c(i,j) = yes$(ord(j) < ord(i));
Parameter wt(i,j);
wt(i,j) = 1 + mod(7*ord(i) + 3*ord(j), 5)/4;
Positive Variable x(i,j);
Variable obj;
Equation e(i), defobj;
e(i).. sum(j$a(i,j), x(i,j)) + sum(k$b(i,k), x(i,k)) - sum(j$c(i,j), x(j,i)) =g= 3 - 2*ord(i);
defobj.. obj =e= sum((i,j), wt(i,j)*sqr(x(i,j)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# PR #1791 review: an equation condition with its own binder named like a row
# index (`sum(rp$tranc(r,rp), 1) > 0` in a row over `rp`): mapping `r` to `rp`
# captured it (`tranc(rp__,rp__)`). NLP 1.3333 (before: 2.222).
NESTED_CONDITION_BINDER = """\
Set r / r1*r3 /, c / c1*c2 /;
Alias (r,rp);
Set tranc(r,rp);
tranc(r,rp) = yes$(ord(r) <> ord(rp));
Parameter d(r,c);
d(r,c) = ord(r) - 2 + ord(c)/4;
Positive Variable trans(c,r,rp);
Variable obj;
Equation fodb(r,c), defobj;
fodb(r,c)$(sum(rp$tranc(r,rp), 1) > 0).. sum(rp$tranc(r,rp), trans(c,rp,r) - trans(c,r,rp)) =e= d(r,c) - sum(rp, d(rp,c))/card(r);
defobj.. obj =e= sum((c,r,rp), sqr(trans(c,r,rp)));
Model m / all /;
solve m using nlp minimizing obj;
"""


# PR #1791 review round 2:
# - a binder over a SUBSET in one placement (`sum(s$b(i,s), x(i,s))`, s(i) / i3 /):
#   a representative outside `s` lacks that sum, so the shape keeps the pre-#1787
#   path (identical to `main`).
SUBSET_BINDER_IN_PLACEMENT = """\
Set i / i1*i3 /, s(i) / i3 /;
Alias (i,j);
Set a(i,j), b(i,j), c(i,j);
a(i,j) = yes$(ord(j) > ord(i)); b(i,j) = yes; c(i,j) = yes$(ord(j) < ord(i));
Parameter wt(i,j);
wt(i,j) = 1 + mod(7*ord(i) + 3*ord(j), 5)/4;
Positive Variable x(i,j);
Variable obj;
Equation e(i), defobj;
e(i).. sum(j$a(i,j), x(i,j)) + sum(s$b(i,s), x(i,s)) - sum(j$c(i,j), x(j,i)) =g= 3 - 2*ord(i);
defobj.. obj =e= sum((i,j), wt(i,j)*sqr(x(i,j)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - an indexed `smax` in the guard: its fresh alias needs a self-mapping, or the
#   PARAMETER's declared domain turns `smax(j, wt(j))` into `wt(i)`. NLP 0.6667
#   (before: 1.000).
SMAX_GUARD = """\
Set i / i1*i3 /;
Alias (i,j,k);
Set a(i,j);
a(i,j) = yes$(ord(i) <> ord(j));
Parameter wt(i), d(i);
wt(i) = ord(i); d(i) = ord(i) - 2;
Positive Variable x(i,j);
Variable obj;
Equation e(i), defobj;
e(i).. sum(k$(a(i,k) and smax(j, wt(j)) > 2), x(i,k) - x(k,i)) =e= d(i);
defobj.. obj =e= sum((i,j), sqr(x(i,j)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - a `.off` set attribute in the equation condition follows the eq coordinate of
#   each term (`$(j.off = 0)` on the incoming one).
SET_ATTRIBUTE_CONDITION = """\
Set i / a, b, c /;
Alias (i,j);
Set aa(i,j);
aa(i,j) = yes$(ord(i) <> ord(j));
Positive Variable x(i,j);
Variable obj;
Equation e(i), defobj;
e(i)$(i.off = 0).. sum(j$aa(i,j), x(i,j) - x(j,i)) =e= 1;
defobj.. obj =e= sum((i,j), sqr(x(i,j)));
Model m / all /;
solve m using nlp minimizing obj;
"""


def _emit(tmp_path: Path, source: str) -> str:
    src = tmp_path / "model.gms"
    src.write_text(source)
    out = tmp_path / "out.gms"
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(out)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert proc.returncode == 0, proc.stderr
    return out.read_text()


def _row(emit: str, head: str) -> str:
    return next(line for line in emit.splitlines() if line.startswith(head))


def test_each_REFERENCE_gets_its_own_term(tmp_path):
    row = _row(_emit(tmp_path, TWO_REFERENCES), "stat_trans(")
    assert row == (
        "stat_trans(c,r,rp).. 2 * trans(c,r,rp) + 1$(tranc(rp,r)) * nu_fodb(rp,c)"
        " - 1$(tranc(r,rp)) * nu_fodb(r,c) - piL_trans(c,r,rp) =E= 0;"
    ), row


def test_the_EGYPT_shape_keeps_both_terms_under_its_conditions(tmp_path):
    row = _row(_emit(tmp_path, EGYPT_SHAPE), "stat_trans(")
    assert "1$(tranc(rp,r)))$(ct(c))) * nu_fodb(rp,c))$(cf(c))" in row, row
    assert "1$(tranc(r,rp)))$(ct(c))) * nu_fodb(r,c))$(cf(c))" in row, row
    assert "tranc(rp,rp)" not in row, row


def test_every_reference_KEEPS_its_binder_mapping(tmp_path):
    row = _row(_emit(tmp_path, BINDERS_PER_PLACEMENT), "stat_x(")
    assert "(1$(a(i,j)) + 1$(b(i,j)))) * lam_e(i)" in row and "b(i,k)" not in row, row


def test_a_condition_binder_never_CAPTURES_or_RE_CONTROLS_a_row_index(tmp_path):
    row = _row(_emit(tmp_path, NESTED_CONDITION_BINDER), "stat_trans(")
    assert "tranc(rp__,rp__)" not in row and "sum(rp," not in row, row
    assert "$(sum(r__kkt1$(tranc(rp,r__kkt1)), 1) > 0)" in row, row


def test_a_SUBSET_binder_keeps_the_pre_1787_path(monkeypatch):
    import src.kkt.stationarity as st
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.config import Config
    from src.emit.expr_to_gams import expr_to_gams
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_text(SUBSET_BINDER_IN_PLACEMENT)
    # Non-vacuity: the shape HAS two placements, so the path would be taken.
    assert st._multi_reference_layouts(model.equations["e"], "x") is not None

    def stat_x() -> str:
        m = parse_model_text(SUBSET_BINDER_IN_PLACEMENT)
        eqs, _ = normalize_model(m)
        config = Config()
        gradient = compute_objective_gradient(m, config)
        j_eq, j_ineq = compute_constraint_jacobian(m, eqs, config)
        kkt = assemble_kkt_system(m, gradient, j_eq, j_ineq, config)
        return expr_to_gams(st.build_stationarity_equations(kkt, config)["stat_x"].lhs_rhs[0])

    current = stat_x()
    monkeypatch.setattr(st, "_multi_reference_layouts", lambda *a, **k: None)
    assert current == stat_x(), "a subset binder must keep the pre-#1787 path"


def test_an_indexed_SMAX_in_the_guard_keeps_its_own_binder(tmp_path):
    row = _row(_emit(tmp_path, SMAX_GUARD), "stat_x(")
    assert "wt(i)" not in row and "wt(j)" not in row, row
    assert "smax(i__kkt1, wt(i__kkt1)) > 2" in row, row


def test_a_SET_ATTRIBUTE_in_the_condition_follows_the_eq_coordinate(tmp_path):
    row = _row(_emit(tmp_path, SET_ATTRIBUTE_CONDITION), "stat_x(")
    assert "* nu_e(i))$(i.off = 0)" in row and "* nu_e(j))$(j.off = 0)" in row, row


def test_the_layouts_need_every_eq_index_and_two_placements():
    from src.ir.parser import parse_model_text
    from src.kkt.stationarity import _multi_reference_layouts

    model = parse_model_text(TWO_REFERENCES)
    layouts = _multi_reference_layouts(model.equations["fodb"], "trans")
    assert layouts == [{"c": 0, "rp": 1, "r": 2}, {"c": 0, "r": 1, "rp": 2}], layouts
    # one placement only -> not this shape
    single = parse_model_text(TWO_REFERENCES.replace(" - trans(c,r,rp)", ""))
    assert _multi_reference_layouts(single.equations["fodb"], "trans") is None
