"""#1782 (Sprint 40 Day 7, P4): the Pattern C rewrite pairs the sum binder with the
VARIABLE position it occupies.

launch's ``dweight(s).. ... sum(ss$ge(ss,s), iweight(ss))`` with ``iweight(s)``:
the equation index ``s`` is absent from the reference, the binder ``ss`` carries
the variable's coordinate, and the row needs ``sum(ss, ge(s,ss)*nu_dweight(ss))``.
The legacy swap exchanged the binder with the EQ index, which is right only when
the variable is declared over the eq index's name, and fired only on an all-zero
offset key. turkpow breaks both:

* ``ht(m,v)`` / ``pr(t).. sum(mt, ... sum(v$vs(t,v), ht(mt,v)))``: the binder IS
  the variable's position name ``v``, so the eq coordinate was lost
  (``vs(v,v) * lam_pr(v)``, P2's ``vs(v,v)``), and the dimension-mismatch key
  ``(999, 0)`` never reached the swap;
* ``zh(m,b,t)`` / ``db(b,t).. sum(bp$bs(bp,b), zh(mh,bp,t))``: ``sum(bp,
  bs(bp,b) * lam_db(b,t))``, a multiplier not indexed by the summed index (#1307).

shale's ``cpu(m,t).. ... =l= sum(tf$ts(t,tf), h(m,tf))`` is the same shape over a
subset ``t(tf)`` and its parent (``ts(tf,tf)`` in P2), and its ``acap(t).. …
sum((m,tf)$ts(t,tf), nu(m)*h(m,tf))`` holds the related binder SECOND.

Since PR #1788 review round 2 there is no exchange at all: before
re-symbolisation, the symbolic binder becomes the variable's position name and the
representative's eq label a placeholder eq coordinate; afterwards only the
multiplier's eq index is pointed at it. In launch's form the eq coordinate and the
variable's own coordinate are BOTH spelled as the position name once re-symbolised,
so any whole-term exchange moved row-bound factors (``a(v)``, ``2*h(v)``) with the
multiplier; ``main``'s launch swap has that defect too for non-unit coefficients.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Equal arity; the binder `v` is the variable's declared domain name. NLP 7.68.
BINDER_IS_POSITION_NAME = """\
Set t / t1*t4 /;
Alias (t,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Positive Variable h(v);
Variable obj;
Equation pr(t), defobj;
pr(t).. sum(v$vs(t,v), h(v)) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# POSITIVE CONTROL: the variable declared over the eq index's name (launch's
# shape). Correct before this change, and unchanged by it.
LAUNCH_SHAPE = BINDER_IS_POSITION_NAME.replace("Positive Variable h(v);", "Positive Variable h(t);")

# turkpow's `stat_ht`: dimension mismatch, eq over a subset `t(te)`, dynamic `mt`,
# and `vs` a PARAMETER (its ParamRef indices take the declared-domain path). NLP 0.0944.
TURKPOW_HT = """\
Set te / 1975, 1978, 1983, 1988 /, t(te) / 1978, 1983, 1988 /, m / m1*m3 /, mt(m), lab / avail, cost /;
Alias (t,v);
mt(m) = ord(m) > 1;
Parameter vs(t,v);
vs(t,v) = 1$(ord(t) >= ord(v));
Parameter md(m,lab), kit(m,v);
md(m,"avail") = ord(m); kit(m,v) = 0.1;
Positive Variable h(m,v);
Variable obj;
Equation pr(te), defobj;
pr(t).. sum(mt, md(mt,"avail")*sum(v$vs(t,v), kit(mt,v) + h(mt,v))) =g= ord(t);
defobj.. obj =e= sum((m,v), ord(v)*sqr(h(m,v)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# turkpow's `stat_zh`: no name collision, dimension mismatch. NLP 112.264 (main: 558).
TURKPOW_ZH = """\
Set b / b1*b3 /, m / m1*m2 /, t / t1*t2 /;
Alias (b,bp);
Set bs(b,bp);
bs(b,bp) = yes$(ord(b) >= ord(bp));
Parameter d(b,t);
d(b,t) = 10 - 2*ord(b) + ord(t);
Positive Variable zh(m,b,t);
Variable obj;
Equation db(b,t), defobj;
db(b,t).. sum(bp$bs(bp,b), sum(m, zh(m,bp,t))) =g= d(b,t);
defobj.. obj =e= sum((m,b,t), ord(m)*power(4 - ord(b),4)*sqr(zh(m,b,t)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# shale's `cpu`: the binder ranges over the PARENT of the eq index's subset. NLP 9.9375.
SHALE_CPU = """\
Set tf / 1*5 /, t(tf) / 1*4 /, m / m1*m2 /;
Alias (tf,tfp);
Set ts(tf,tfp);
ts(tf,tfp)$(ord(tfp) < ord(tf)) = yes;
Parameter cap(m,tf);
cap(m,tf) = ord(m) + ord(tf);
Positive Variable h(m,tf), z(m,tf);
Variable obj;
Equation cpu(m,tf), defobj;
cpu(m,t).. cap(m,t)*z(m,t) =l= sum(tf$ts(t,tf), h(m,tf)) + 3;
defobj.. obj =e= sum((m,tf), ord(tf)*sqr(h(m,tf))) + sum((m,tf), sqr(z(m,tf) - 2));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# shale's `acap`: the related binder is the SECOND of a two-index sum (the gate
# used to try only the first, `m`). NLP 16.6848 (main: 180, phantom `ord(m) = k`).
SHALE_ACAP = """\
Set tf / 1*5 /, t(tf) / 1*4 /, m / m1*m2 /;
Alias (tf,tfp);
Set ts(tf,tfp);
ts(tf,tfp)$(ord(tfp) < ord(tf)) = yes;
Parameter nu(m);
nu(m) = ord(m);
Positive Variable h(m,tf);
Variable obj, phik(tf);
Equation acap(tf), defobj;
acap(t).. phik(t) =e= sum((m,tf)$ts(t,tf), nu(m)*h(m,tf));
defobj.. obj =e= sum((m,tf), ord(tf)*sqr(h(m,tf) - 1)) + sum(t, ord(t)*sqr(phik(t) - 3));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# The same shape as shale has it: `ts` a PARAMETER and the subset `t` missing the
# FIRST element. The offset substitution (#1162) turned the eq label into
# `ts(tf+1,tf)` before the swap; a Set's membership test is not rewritten, so the
# fixture above cannot show it. NLP 11.2545 (with the substitution: 25.618).
SHALE_ACAP_PARAM = """\
Set tf / 1975-79, 1980-84, 1985-89, 1990-94, 1995-99 /, t(tf) / 1980-84, 1985-89, 1990-94, 1995-99 /, m / m1*m2 /;
Alias (tf,tfp);
Parameter ts(tf,tfp);
ts(tf,tfp)$(ord(tfp) < ord(tf)) = 1;
Parameter nu(m), w(tf);
w(tf) = ord(tf);
nu(m) = ord(m);
Positive Variable h(m,tf);
Variable obj, phik(tf);
Equation acap(tf), defobj;
acap(t).. phik(t) =e= 0.5*sum((m,tf)$ts(t,tf), nu(m)*h(m,tf));
defobj.. obj =e= sum((m,tf), ord(tf)*sqr(h(m,tf) - 1)) + sum(t, w(t)*sqr(phik(t) - 3));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review: dinam's `mb(i,t).. es(i)*sum(tep$ts(t,tep), zmi(t,tep)*em(tep))`
# against `em(te)`. The eq coordinate already has its own index (`t`), so the
# binder is only the variable's coordinate. The round-1 binder <-> position
# exchange corrupted the bound coefficient (zmi(t,tep)) and kept a spurious sum.
# NLP 10.5238 (with the exchange: 11.779).
BOUND_COEFFICIENT = """\
Set te / 1*5 /, t(te) / 2*5 /, i / i1*i2 /;
Alias (te,tep);
Parameter ts(te,tep), zmi(te,tep), es(i), d(i,te);
ts(te,tep) = 1$(ord(te) >= ord(tep));
zmi(te,tep) = 2 - 0.3*(ord(te) - ord(tep));
es(i) = ord(i);
d(i,te) = ord(i) + ord(te);
Positive Variable em(te);
Variable obj;
Equation mb(i,te), defobj;
mb(i,t).. es(i)*sum(tep$ts(t,tep), zmi(t,tep)*em(tep)) =g= d(i,t);
defobj.. obj =e= sum(te, ord(te)*sqr(em(te)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# PR #1788 review: the coefficient sums over `w`, an alias of the binder's set.
# The placeholder eq coordinate must avoid it. NLP 1.2288 (when it took `w`: 1.600).
COEFFICIENT_SUM = """\
Set t / t1*t4 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter a(t);
a(t) = ord(t)/4;
Positive Variable h(v);
Variable obj;
Equation pr(t), defobj;
pr(t).. sum(v$vs(t,v), sum(w, a(w))*h(v)) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""


# PR #1788 review round 2: launch's form spells the eq coordinate AND the
# variable's own coordinate as the position name, so the exchange moved
# row-bound factors with the multiplier.
# - a coefficient of the binder (a(v) became a(t__kkt1)). NLP 1.8655 (exchange: 1.999).
ROW_BOUND_COEFFICIENT = """\
Set t / t1*t4 /;
Alias (t,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter a(t);
a(t) = 1 + ord(t)/2;
Positive Variable h(v);
Variable obj;
Equation pr(t), defobj;
pr(t).. sum(v$vs(t,v), a(v)*h(v)) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - the same with the variable declared over the eq index's name (launch's own
#   naming; `main` emits a(v) for a(t) here too).
ROW_BOUND_COEFFICIENT_LAUNCH_NAMING = ROW_BOUND_COEFFICIENT.replace(
    "Positive Variable h(v);", "Positive Variable h(t);"
)

# - a nonlinear derivative factor (2*h(v) became 2*h(t__kkt1)). NLP 8.9208 (13.617).
ROW_BOUND_NONLINEAR = """\
Set t / t1*t4 /;
Alias (t,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Variable h(v), obj;
Equation pr(t), defobj;
pr(t).. sum(v$vs(t,v), sqr(h(v))) =l= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v) - 2));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - an equation condition with its own binder `w`, an alias of the binder's set,
#   attached after re-symbolisation (the eq coordinate must not reuse `w`). NLP 7.68.
EQUATION_GUARD = """\
Set t / t1*t4 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter a(t) / t1 0.25, t2 0.5, t3 0.75, t4 1 /;
Positive Variable h(v);
Variable obj;
Equation pr(t), defobj;
pr(t)$(sum(w, a(w)) >= 1).. sum(v$vs(t,v), h(v)) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""


# - an equation condition over the EQ index: it must follow the eq coordinate,
#   not the variable's position (`ord(v) > 1`). NLP 1.8655 (on `ord(v)`: 2.924).
EQUATION_CONDITION_ON_EQ_INDEX = ROW_BOUND_COEFFICIENT.replace(
    "pr(t).. sum(v$vs(t,v), a(v)*h(v))", "pr(t)$(ord(t) > 1).. sum(v$vs(t,v), a(v)*h(v))"
)


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


def test_a_binder_NAMED_LIKE_the_variable_position_keeps_the_eq_coordinate(tmp_path):
    # FAIL-BEFORE: ((-1) * 1$(vs(t,t))) * lam_pr(t), with `t` uncontrolled.
    row = _row(_emit(tmp_path, BINDER_IS_POSITION_NAME), "stat_h(")
    assert row == (
        "stat_h(v).. 2 * ord(v) * h(v) + sum(t__kkt1, ((-1) * 1$(vs(t__kkt1,v)))"
        " * lam_pr(t__kkt1)) - piL_h(v) =E= 0;"
    ), row


def test_POSITIVE_CONTROL_the_launch_shape_is_unchanged(tmp_path):
    row = _row(_emit(tmp_path, LAUNCH_SHAPE), "stat_h(")
    assert row == (
        "stat_h(t).. 2 * ord(t) * h(t) + sum(v, ((-1) * 1$(vs(v,t))) * lam_pr(v)) - piL_h(t) =E= 0;"
    ), row


def test_turkpow_ht_shape_sums_the_eq_index_and_keeps_both_coordinates(tmp_path):
    # FAIL-BEFORE: (... * 1$(vs(v,v))) * lam_pr(v): P2's `vs(v,v)`, MCP 2.0 vs NLP 1.536
    # on the simpler variant. A first revision also lost the PARAMETER's renamed binder
    # to its declared domain: vs("t__kkt1","t__kkt1"), quoted.
    row = _row(_emit(tmp_path, TURKPOW_HT), "stat_h(")
    assert (
        'sum(t__kkt1, (((-1) * (md(m,"avail") * 1$(vs(t__kkt1,v)))$(mt(m)))'
        " * lam_pr(t__kkt1))$(t(t__kkt1)))" in row
    ), row
    assert '"t__kkt1"' not in row, row


def test_turkpow_zh_shape_indexes_the_multiplier_by_the_summed_index(tmp_path):
    # FAIL-BEFORE (#1307's shape): sum(bp, ((-1) * 1$(bs(bp,b))) * lam_db(b,t)).
    row = _row(_emit(tmp_path, TURKPOW_ZH), "stat_zh(")
    assert "sum(bp, ((-1) * 1$(bs(b,bp))) * lam_db(bp,t))" in row, row


def test_shale_cpu_shape_over_a_subset_and_its_parent(tmp_path):
    # FAIL-BEFORE: (((-1) * 1$(ts(tf,tf))) * lam_cpu(m,tf))$(t(tf)): the diagonal only.
    row = _row(_emit(tmp_path, SHALE_CPU), "stat_h(")
    assert (
        "sum(t__kkt1, (((-1) * 1$(ts(t__kkt1,tf))) * lam_cpu(m,t__kkt1))$(t(t__kkt1)))" in row
    ), row
    assert "ts(tf,tf)" not in row, row


def test_shale_acap_shape_uses_the_RELATED_binder_of_a_multi_index_sum(tmp_path):
    # FAIL-BEFORE: per-offset phantoms, ((... ts(tf,tf) ...) * nu_acap(tf+1))$(ord(m) = 1) ...
    row = _row(_emit(tmp_path, SHALE_ACAP), "stat_h(")
    assert row == (
        "stat_h(m,tf).. 2 * ord(tf) * (h(m,tf) - 1) + sum(t__kkt1, (((-1) * (nu(m)"
        " * 1$(ts(t__kkt1,tf)))) * nu_acap(t__kkt1))$(t(t__kkt1))) - piL_h(m,tf) =E= 0;"
    ), row


def test_shale_acap_with_a_PARAMETER_guard_skips_the_offset_substitution(tmp_path):
    row = _row(_emit(tmp_path, SHALE_ACAP_PARAM), "stat_h(")
    assert "1$(ts(t__kkt1,tf))" in row and "tf+1" not in row, row


def test_a_BOUND_coefficient_keeps_its_coordinate_and_the_binder_sum_goes(tmp_path):
    row = _row(_emit(tmp_path, BOUND_COEFFICIENT), "stat_em(")
    # The eq coordinate is the binder's own name `tep` (free once it stands for
    # `te`); the standard path's sum((i,t)$sameas(t,te), ...) pin is gone.
    assert row == (
        "stat_em(te).. 2 * ord(te) * em(te) + sum(tep, sum(i, (((-1) * (es(i) * zmi(tep,te)"
        " * 1$(ts(tep,te)))) * lam_mb(i,tep))$(t(tep)))) - piL_em(te) =E= 0;"
    ), row


def test_the_renamed_binder_avoids_a_COEFFICIENT_sum_binder(tmp_path):
    row = _row(_emit(tmp_path, COEFFICIENT_SUM), "stat_h(")
    assert "sum(w, a(w))" in row and "a(v)" not in row, row
    assert "sum(w, ((-1)" not in row, "the outer binder must not reuse `w`: " + row


def test_a_ROW_BOUND_coefficient_keeps_the_variable_position(tmp_path):
    row = _row(_emit(tmp_path, ROW_BOUND_COEFFICIENT), "stat_h(")
    assert row == (
        "stat_h(v).. 2 * ord(v) * h(v) + sum(t__kkt1, ((-1) * (a(v) * 1$(vs(t__kkt1,v))))"
        " * lam_pr(t__kkt1)) - piL_h(v) =E= 0;"
    ), row


def test_a_ROW_BOUND_coefficient_under_launch_naming(tmp_path):
    row = _row(_emit(tmp_path, ROW_BOUND_COEFFICIENT_LAUNCH_NAMING), "stat_h(")
    assert row == (
        "stat_h(t).. 2 * ord(t) * h(t) + sum(v, ((-1) * (a(t) * 1$(vs(v,t)))) * lam_pr(v))"
        " - piL_h(t) =E= 0;"
    ), row


def test_a_ROW_BOUND_nonlinear_factor_keeps_the_variable_position(tmp_path):
    row = _row(_emit(tmp_path, ROW_BOUND_NONLINEAR), "stat_h(")
    assert "2 * h(v) * 1$(vs(t__kkt1,v)) * lam_pr(t__kkt1)" in row, row
    assert "h(t__kkt1)" not in row, row


def test_the_eq_coordinate_avoids_an_EQUATION_CONDITION_binder(tmp_path):
    row = _row(_emit(tmp_path, EQUATION_GUARD), "stat_h(")
    assert "$(sum(w, a(w)) >= 1)" in row and "a(v)" not in row, row
    assert "sum(w, (" not in row, "the eq coordinate must not reuse `w`: " + row


def test_the_EQUATION_CONDITION_follows_the_eq_coordinate(tmp_path):
    assert "pr(t)$(ord(t) > 1).." in EQUATION_CONDITION_ON_EQ_INDEX, "fixture must apply"
    row = _row(_emit(tmp_path, EQUATION_CONDITION_ON_EQ_INDEX), "stat_h(")
    assert "$(ord(t__kkt1) > 1)" in row and "ord(v) > 1" not in row, row


def test_the_swap_needs_the_eq_index_ABSENT_from_every_reference():
    """`ao(t).. sum((mt,v)$vs(t,v), ... zt(mt,v,b,t))` holds `t` in the reference,
    so `t` binds its own position and nothing may be swapped. A first revision
    swapped there and broke turkpow's `stat_zt` (`opcostt(m,"t__kkt1",t)`)."""
    from src.ir.ast import Binary, Const, IndexOffset, VarRef
    from src.ir.symbols import EquationDef, Rel
    from src.kkt.stationarity import _index_absent_from_var_refs

    def eq(*refs):
        body = refs[0]
        for r in refs[1:]:
            body = Binary("+", body, r)
        return EquationDef(name="e", domain=("t",), relation=Rel.EQ, lhs_rhs=(body, Const(1.0)))

    assert _index_absent_from_var_refs(eq(VarRef("z", ("m", "v"))), "z", "t")
    assert not _index_absent_from_var_refs(eq(VarRef("z", ("m", "v", "t"))), "z", "t")
    # an offset counts by its base
    assert not _index_absent_from_var_refs(
        eq(VarRef("z", ("m", IndexOffset("t", Const(1), False)))), "z", "t"
    )
    # present in ANY reference is enough to refuse
    assert not _index_absent_from_var_refs(
        eq(VarRef("z", ("m", "v")), VarRef("z", ("m", "t"))), "z", "t"
    )
    # no reference at all: not "absent", there is nothing to swap
    assert not _index_absent_from_var_refs(eq(VarRef("y", ("t",))), "z", "t")
