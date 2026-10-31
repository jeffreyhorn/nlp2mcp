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


# PR #1788 review round 3: the representative must keep the default selector's
# collision checks (distinct variable / equation labels). Two aliased variable
# coordinates (`m`, `v`) and a representative `h(a,a)` gave `2*h(v,v)`.
# NLP 3.1690 (with h(v,v): 4.983).
MULTI_AXIS_ALIAS = """\
Set t / a, b, c /;
Alias (t,m,v);
Set s(t,v);
s(t,v) = yes$(ord(t) >= ord(v));
Parameter c(t,v);
c(t,v) = 1 + ord(t) + 2*ord(v);
Variable h(m,v), obj;
Equation e(t), defobj;
e(t).. sum((m,v)$s(t,v), sqr(h(m,v))) =l= ord(t);
defobj.. obj =e= sum((m,v), sqr(h(m,v) - 1)) + sum(v, ord(v)*h("a",v));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# PR #1788 review round 3: a binder over a SUBSET (`ss` of `s(i)`) against an eq
# index over the parent (`e(i)`) must not lend its name to the eq coordinate:
# sum(ss, ... lam_e(ss)) drops e('c'). NLP 3.0 (reusing `ss`: no solve).
SUBSET_BINDER = """\
Set i / a, b, c /, s(i) / a, b /, k / k1, k2 /;
Alias (s,ss);
Parameter a(i,i);
a(i,s) = 1$(ord(i) >= ord(s));
Positive Variable x(s,k);
Variable obj;
Equation e(i), defobj;
e(i).. sum((ss,k)$a(i,ss), x(ss,k)) =g= ord(i);
defobj.. obj =e= sum((s,k), ord(s)*sqr(x(s,k)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review round 4: with the PARENT-set binder `tep` reused as the eq
# coordinate, the equation condition's `card(t)` became `card(tep)` (5, not 4),
# so the guard was false everywhere. The eq coordinate now ranges over `t`'s own
# set, and `card()` operands are not renamed. NLP 10.5238 (card(tep): no solve).
PARENT_BINDER_CARD = BOUND_COEFFICIENT.replace("mb(i,t).. ", "mb(i,t)$(card(t) = 4).. ")

# The same for `ord(t)`: it counts within the subset, so `ord(tep)` selects other
# instances. (Its solve happens to agree; the emitted guard is what is pinned.)
PARENT_BINDER_ORD = BOUND_COEFFICIENT.replace("mb(i,t).. ", "mb(i,t)$(ord(t) > 1).. ")


# PR #1788 review round 5: a scalar already named like the placeholder alias.
# GAMS has one symbol namespace, so `Alias(t, t__kkt1)` beside `Scalar t__kkt1`
# did not compile ($195). NLP 7.68.
NAME_COLLISION = """\
Set t / t1*t4 /;
Alias (t,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Scalar t__kkt1 / 1 /;
Positive Variable h(v);
Variable obj;
Equation pr(t), defobj;
pr(t).. sum(v$vs(t,v), h(v)) =g= ord(t)*t__kkt1;
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# PR #1788 review round 5: independent sets `k` and `i` share the label `a`, so no
# representative is usable for the binder rewrite (its eq label is always among
# the variable's labels, or those repeat). The binder-only admission is withdrawn
# BEFORE consolidation and the pair keeps the pre-#1782 path. (That path is wrong
# here too, for the shared-label ambiguity tracked on #1778: `x(k,k)`, phantom
# offsets; NLP 2.6667.)
SHARED_LABELS = """\
Set i / a, b /, k / a /;
Alias (i,v);
Parameter c(i) / a 1, b 2 /;
Positive Variable x(k,v);
Variable obj;
Equation e(i), defobj;
e(i).. sum((k,v)$(ord(i) > 0), x(k,v)) =g= ord(i);
defobj.. obj =e= sum((k,v), c(v)*sqr(x(k,v)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review round 6: a DIRECT reference beside the sum (`x(t)` with
# `sum(tf$ts(t,tf), x(tf))`) rejects the binder rewrite, so the binder-only
# admissions must not consolidate first: the subset (`t(tf)`) admission here ...
MIXED_SUBSET = """\
Set tf / 1*5 /, t(tf) / 2*5 /;
Alias (tf,tfp);
Set ts(tf,tfp);
ts(tf,tfp)$(ord(tfp) < ord(tf)) = yes;
Variable x(tf), obj;
Equation e(tf), defobj;
e(t).. x(t) =e= 0.5*sum(tf$ts(t,tf), x(tf)) + 1;
defobj.. obj =e= sum(tf, ord(tf)*sqr(x(tf)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""

# ... and the later-binder admission (`h('m1',t)` beside `sum((m,tf)$ts(t,tf), ...)`).
# Both keep the pre-#1782 path, which is itself wrong for mixed references (the
# #1778 family): NLP 3.8221 / 12.8859, that path 85.953 / 28.0.
MIXED_LATER_BINDER = """\
Set tf / 1*5 /, t(tf) / 2*5 /, m / m1*m2 /;
Alias (tf,tfp);
Set ts(tf,tfp);
ts(tf,tfp)$(ord(tfp) < ord(tf)) = yes;
Positive Variable h(m,tf);
Variable obj;
Equation e(tf), defobj;
e(t).. h('m1',t) + 0.5*sum((m,tf)$ts(t,tf), h(m,tf)) =g= ord(t);
defobj.. obj =e= sum((m,tf), ord(tf)*sqr(h(m,tf)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review round 7: two INDEPENDENTLY named sums carry the same variable
# coordinate (only the second sum's binder is renamed, `w`). Rebinding only the
# first left `w` free, and the free-index wrap summed the whole derivative over it
# (MCP 5.440). Both binders are now rebound, each in its own scope. NLP 4.0.
MIXED_BINDERS = """\
Set t / t1*t4 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter a(t) / t1 1, t2 2, t3 3, t4 4 /;
Positive Variable h(v);
Variable obj;
Equation e(t), defobj;
e(t).. sum(v$vs(t,v), h(v)) + sum(w$vs(t,w), a(w)*h(w)) =g= 5 - ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""


# PR #1788 review round 8: COEFFICIENT_SUM combined with MIXED_BINDERS. The
# combined {v, w} -> v rebinding must not reach the coefficient's own
# `sum(w, a(w))` (it became `sum(w, a(v))`, MCP 31.392). NLP 25.3884.
COEFFICIENT_SUM_MIXED_BINDERS = """\
Set t / t1*t4 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter a(t) / t1 1, t2 2, t3 3, t4 4 /;
Positive Variable h(v);
Variable obj;
Equation e(t), defobj;
e(t).. sum(v$vs(t,v), sum(w, a(w))*h(v)) + sum(w$vs(t,w), h(w)) =g= 20*ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""


# PR #1788 review round 9:
# - a guard's own nested sum binds a rename DESTINATION: `{w: v}` inside
#   `sum(v, c(v,w))` captured it as `c(v,v)`, activating the first row's term
#   (15 -> 24 > 20). The nested binder is alpha-renamed. NLP 14.3662 (86.976).
CONDITION_SCOPE = """\
Set t / t1*t3 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter c(t,v);
c(t,v) = ord(t) + 3*ord(v);
Positive Variable h(v), z(t);
Variable obj;
Equation e(t), defobj;
e(t).. sum(w$(vs(t,w) and sum(v, c(v,w)) > 20), h(w)) + z(t) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v))) + sum(t, 5*sqr(z(t)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - a binder over a SUBSET beside one over the full set: the subset sum only
#   contributes where its membership holds, which one representative cannot
#   carry, so the shape keeps the pre-#1782 path (and `card(s)` is not rewritten).
MIXED_SUBSET_BINDER_CARD = """\
Set t / t1*t4 /, s(t) / t2, t4 /;
Alias (t,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Positive Variable h(v);
Variable obj;
Equation e(t), defobj;
e(t).. sum(v$vs(t,v), h(v)) + sum(s$vs(t,s), card(s)*h(s)) =g= 20*ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - `card(w)` of a rebound same-set binder becomes the set's `card(t)` rather
#   than leaving `w` free (the free-index wrap summed over it).
CARD_SAME_SET = """\
Set t / t1*t4 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Positive Variable h(v);
Variable obj;
Equation e(t), defobj;
e(t).. sum(v$vs(t,v), h(v)) + sum(w$vs(t,w), card(w)*h(w)) =g= 20*ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - the variable's positions permuted (`h(v,m)`, binder `m` at position 1): the
#   multiplier spelled `v` is a ROW coordinate, so the row-bound `h(v,m)` must not
#   move to the eq coordinate. ⚠ This exact shape also lists the binders out of
#   reference order (`(m,v)` vs `h(v,m)`), so the AD derivative is itself wrong
#   (#1776: positional binder pairing, `h(b,a)*sameas(b,a)`), and it does not
#   solve on any version. Only the stationarity property is pinned here.
PERMUTED_POSITIONS = """\
Set t / a, b, c /;
Alias (t,m,v);
Set s(t,v);
s(t,v) = yes$(ord(t) >= ord(v));
Variable h(v,m), obj;
Equation e(t), defobj;
e(t).. sum((m,v)$s(t,v), sqr(h(v,m))) =l= ord(t);
defobj.. obj =e= sum((v,m), sqr(h(v,m) - 1)) + sum(m, ord(m)*h("a",m));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review round 10:
# - an alias-named equation domain (`pr(q)`, Alias(t,q,w)): `card(w)` becomes
#   `card(t)`, and the free-index collector took the SET operand for an iterator
#   and summed over it (`sum((t,t__kkt1), ...)`). NLP 192.
CARD_ALIAS_EQ_DOMAIN = """\
Set t / t1*t4 /;
Alias (t,q,w);
Set vs(t,q);
vs(t,q) = yes$(ord(t) >= ord(q));
Positive Variable h(q);
Variable obj;
Equation pr(q), defobj;
pr(q).. sum(w$vs(q,w), card(w)*h(w)) =g= 20*ord(q);
defobj.. obj =e= sum(q, ord(q)*sqr(h(q)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - indexed `smax` in the guard binds its own index (a Call, not a Sum): `{w: v}`
#   captured `smax(v, c(v,w))` as `smax(v, c(v,v))`. NLP 14.3662 (no solve).
SMAX_CONDITION_SCOPE = """\
Set t / t1*t3 /;
Alias (t,v,w);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter c(t,v);
c(t,v) = ord(t) + 3*ord(v);
Positive Variable h(v), z(t);
Variable obj;
Equation e(t), defobj;
e(t).. sum(w$(vs(t,w) and smax(v, c(v,w)) > 8), h(w)) + z(t) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v))) + sum(t, 5*sqr(z(t)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - a three-axis aliased guard: every row coordinate needs a self-mapping, or the
#   dimension-mismatch alias_remap sends `v` to `w` (`s(E*,m,w,w)`). NLP 0.6667.
THREE_AXIS_GUARD = """\
Set t / a, b, c, d /;
Alias (t,m,v,w);
Set s(t,m,v,w);
s(t,m,v,w) = yes$(ord(t) >= ord(m) and ord(v) < ord(w));
Positive Variable x(m,v,w);
Variable obj;
Equation e(t), defobj;
e(t).. sum((m,v,w)$s(t,m,v,w), x(m,v,w)) =g= ord(t);
defobj.. obj =e= sum((m,v,w), sqr(x(m,v,w)));
Model mm / all /;
solve mm using nlp minimizing obj;
"""


# PR #1788 review round 11:
# - the alpha-rename inside a NESTED reduction must not pick an existing alias an
#   enclosing reduction binds: `sum(q, a(q)*smax(v, c(v,w)))` became
#   `sum(q, a(q)*smax(q, c(q,v)))` (no solve). It now always mints. NLP 14.3662.
NESTED_REDUCTION = """\
Set t / t1*t3 /;
Alias (t,v,w,q);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Parameter c(t,v), a(t);
c(t,v) = ord(t) + 3*ord(v);
a(t) = ord(t);
Positive Variable h(v), z(t);
Variable obj;
Equation e(t), defobj;
e(t).. sum(w$(vs(t,w) and sum(q, a(q)*smax(v, c(v,w))) > 40), h(w)) + z(t) =g= ord(t);
defobj.. obj =e= sum(v, ord(v)*sqr(h(v))) + sum(t, 5*sqr(z(t)));
Model m / all /;
solve m using nlp minimizing obj;
"""

# - two aliased equation axes (`e(t,m)` against `h(m,v)`): downstream alias
#   matching remapped the position-bound derivative (`h(v,v)`, `lam_e(E,v)`), so
#   the shape keeps the pre-#1782 path (itself wrong here, as on `main`).
TWO_EQ_AXES = """\
Set t / a, b, c /;
Alias (t,m,v);
Set vs(t,v);
vs(t,v) = yes$(ord(t) >= ord(v));
Variable h(m,v), obj;
Equation e(t,m), defobj;
e(t,m).. sum(v$vs(t,v), sqr(h(m,v))) =l= 0.5*ord(t);
defobj.. obj =e= sum((m,v), sqr(h(m,v) - 1));
Model mm / all /;
solve mm using nlp minimizing obj;
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
    # The eq coordinate is an alias of `t` itself (`tep` ranges over the PARENT
    # `te`, so it is not reused); the standard path's sum((i,t)$sameas(t,te), ...)
    # pin is gone.
    assert row == (
        "stat_em(te).. 2 * ord(te) * em(te) + sum(t__kkt1, sum(i, (((-1) * (es(i)"
        " * zmi(t__kkt1,te) * 1$(ts(t__kkt1,te)))) * lam_mb(i,t__kkt1))$(t(t__kkt1))))"
        " - piL_em(te) =E= 0;"
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


def test_the_representative_keeps_distinct_MULTI_AXIS_coordinates(tmp_path):
    row = _row(_emit(tmp_path, MULTI_AXIS_ALIAS), "stat_h(")
    assert "2 * h(m,v) * 1$(s(t__kkt1,v)) * lam_e(t__kkt1)" in row, row
    assert "h(v,v)" not in row, row


def test_a_SUBSET_binder_does_not_name_the_eq_coordinate(tmp_path):
    row = _row(_emit(tmp_path, SUBSET_BINDER), "stat_x(")
    assert "sum(i__kkt1, ((-1) * 1$(a(i__kkt1,s))) * lam_e(i__kkt1))" in row, row
    assert "lam_e(ss)" not in row, row


def test_a_PARENT_binder_is_not_reused_and_CARD_is_preserved(tmp_path):
    assert "mb(i,t)$(card(t) = 4).." in PARENT_BINDER_CARD, "fixture must apply"
    row = _row(_emit(tmp_path, PARENT_BINDER_CARD), "stat_em(")
    assert "$(card(t) = 4)" in row and "card(tep)" not in row, row
    assert "lam_mb(i,t__kkt1)" in row and "lam_mb(i,tep)" not in row, row


def test_a_PARENT_binder_is_not_reused_for_an_ORD_guard(tmp_path):
    assert "mb(i,t)$(ord(t) > 1).." in PARENT_BINDER_ORD, "fixture must apply"
    row = _row(_emit(tmp_path, PARENT_BINDER_ORD), "stat_em(")
    assert "$(ord(t__kkt1) > 1)" in row and "ord(tep)" not in row, row


def test_a_placeholder_never_takes_an_existing_IDENTIFIER(tmp_path):
    emit = _emit(tmp_path, NAME_COLLISION)
    row = _row(emit, "stat_h(")
    assert "sum(t__kkt2, ((-1) * 1$(vs(t__kkt2,v))) * lam_pr(t__kkt2))" in row, row
    assert "Alias(t, t__kkt1)" not in emit, "must not alias over the scalar t__kkt1"


@pytest.mark.parametrize(
    "fixture, stat, var_name, var_canon",
    [
        ("SHARED_LABELS", "stat_x", "x", {"k", "i"}),
        ("MIXED_SUBSET", "stat_x", "x", {"tf"}),
        ("MIXED_LATER_BINDER", "stat_h", "h", {"m", "tf"}),
    ],
)
def test_a_binder_only_admission_the_rewrite_cannot_serve_is_WITHDRAWN(
    monkeypatch, fixture, stat, var_name, var_canon
):
    """When the binder rewrite cannot run, the binder-only admission is withdrawn
    BEFORE consolidation, so the emit equals the pre-#1782 path: the same model
    with that admission switched off. Shared labels leave no usable representative
    (round 5); a direct reference beside the sum rejects the rewrite (round 6),
    for both the subset (`t(tf)`) and the later-binder admission."""
    import src.kkt.stationarity as st
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.config import Config
    from src.emit.expr_to_gams import expr_to_gams
    from src.ir.ast import Binary
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    source = globals()[fixture]

    def row() -> str:
        model = parse_model_text(source)
        eqs, _ = normalize_model(model)
        config = Config()
        gradient = compute_objective_gradient(model, config)
        j_eq, j_ineq = compute_constraint_jacobian(model, eqs, config)
        kkt = assemble_kkt_system(model, gradient, j_eq, j_ineq, config)
        return expr_to_gams(st.build_stationarity_equations(kkt, config)[stat].lhs_rhs[0])

    admitted = row()
    real = st._find_pattern_c_alias_sum

    def without_binder_only(*args, **kwargs):
        found = real(*args, **kwargs)
        return None if found is not None and found.get("binder_swap_only") else found

    monkeypatch.setattr(st, "_find_pattern_c_alias_sum", without_binder_only)
    assert admitted == row()

    # Non-vacuity: the pattern IS admitted for the binder rewrite on this model.
    monkeypatch.setattr(st, "_find_pattern_c_alias_sum", real)
    model = parse_model_text(source)
    eq = model.equations["e"]
    eq_canon = frozenset(st._resolve_alias_target(d, model) for d in eq.domain)
    found = st._find_pattern_c_alias_sum(
        Binary("-", eq.lhs_rhs[0], eq.lhs_rhs[1]),
        frozenset(var_canon),
        model,
        eq_canon,
        var_name,
    )
    assert found is not None and found.get("binder_swap_only"), found


def test_independently_named_sums_are_EACH_rebound(tmp_path):
    row = _row(_emit(tmp_path, MIXED_BINDERS), "stat_h(")
    assert "sum(w, ((-1) * (1$(vs(w,v)) + a(v) * 1$(vs(w,v)))) * lam_e(w))" in row, row
    assert "sum((" not in row, "no second binder may be left free and summed: " + row


def test_rebinding_respects_a_coefficient_sum_SCOPE(tmp_path):
    row = _row(_emit(tmp_path, COEFFICIENT_SUM_MIXED_BINDERS), "stat_h(")
    assert "sum(w, a(w)) * 1$(vs(t__kkt1,v))" in row and "a(v)" not in row, row


def test_a_nested_binder_that_is_a_rename_DESTINATION_is_alpha_renamed(tmp_path):
    row = _row(_emit(tmp_path, CONDITION_SCOPE), "stat_h(")
    assert "c(v,v)" not in row and "c(v__,v__)" not in row, row
    assert "sum(t__kkt1, c(t__kkt1,v)) > 20" in row, row


def test_CARD_of_a_rebound_binder_counts_its_set(tmp_path):
    row = _row(_emit(tmp_path, CARD_SAME_SET), "stat_h(")
    assert "sum((" not in row, "no rebound binder may be left free and summed: " + row


def test_a_MIXED_SUBSET_binder_keeps_the_pre_1782_path(monkeypatch):
    import src.kkt.stationarity as st
    from src.ir.parser import parse_model_text

    real = st._position_binders
    model = parse_model_text(MIXED_SUBSET_BINDER_CARD)
    eq = model.equations["e"]
    # Non-vacuity: without the same-set rule the binders {v, s} WOULD be accepted.
    assert real(eq, "h", 0) == {"v", "s"}
    assert real(eq, "h", 0, model) is None

    def stat_h() -> str:
        from src.ad.constraint_jacobian import compute_constraint_jacobian
        from src.ad.gradient import compute_objective_gradient
        from src.config import Config
        from src.emit.expr_to_gams import expr_to_gams
        from src.ir.normalize import normalize_model
        from src.kkt.assemble import assemble_kkt_system

        m = parse_model_text(MIXED_SUBSET_BINDER_CARD)
        eqs, _ = normalize_model(m)
        config = Config()
        gradient = compute_objective_gradient(m, config)
        j_eq, j_ineq = compute_constraint_jacobian(m, eqs, config)
        kkt = assemble_kkt_system(m, gradient, j_eq, j_ineq, config)
        return expr_to_gams(st.build_stationarity_equations(kkt, config)["stat_h"].lhs_rhs[0])

    current = stat_h()
    assert "card(v)" not in current, current
    monkeypatch.setattr(st, "_position_binders", lambda *a, **k: None)
    assert current == stat_h(), "the mixed-set shape must keep the pre-#1782 path"


def test_PERMUTED_positions_keep_the_row_bound_factor(tmp_path):
    row = _row(_emit(tmp_path, PERMUTED_POSITIONS), "stat_h(")
    assert "h(t__kkt1" not in row and ",t__kkt1)" not in row.split("lam_e")[0], row
    assert "lam_e(t__kkt1)" in row, row


def test_a_CARD_operand_is_never_summed_as_a_free_index(tmp_path):
    row = _row(_emit(tmp_path, CARD_ALIAS_EQ_DOMAIN), "stat_h(")
    assert "card(t)" in row and "sum((" not in row, row


def test_collect_free_indices_treats_card_and_smax_operands_as_BOUND():
    from src.ir.ast import Binary, Call, ParamRef, SymbolRef
    from src.ir.parser import parse_model_text
    from src.kkt.stationarity import _collect_free_indices

    model = parse_model_text(SMAX_CONDITION_SCOPE)
    card = Call("card", (SymbolRef("w"),))
    assert _collect_free_indices(card, model) == set()
    smax = Call("smax", (SymbolRef("v"), ParamRef("c", ("v", "w"))))
    assert _collect_free_indices(smax, model) == {"w"}
    # positive control: an ordinary Call still exposes its free indices
    ordv = Binary("+", Call("ord", (SymbolRef("v"),)), card)
    assert _collect_free_indices(ordv, model) == {"v"}


def test_an_indexed_SMAX_binder_is_scoped_and_alpha_renamed(tmp_path):
    row = _row(_emit(tmp_path, SMAX_CONDITION_SCOPE), "stat_h(")
    assert "c(v,v)" not in row and "smax(t__kkt1, c(t__kkt1,v)) > 8" in row, row


def test_a_THREE_AXIS_guard_keeps_every_row_coordinate(tmp_path):
    row = _row(_emit(tmp_path, THREE_AXIS_GUARD), "stat_x(")
    assert "1$(s(t__kkt1,m,v,w))" in row, row


def test_an_alpha_rename_never_reuses_an_ENCLOSING_binder(tmp_path):
    row = _row(_emit(tmp_path, NESTED_REDUCTION), "stat_h(")
    assert "smax(q," not in row and "sum(q, a(q) * smax(t__kkt1, c(t__kkt1,v)))" in row, row


def test_TWO_aliased_eq_axes_keep_the_pre_1782_path(monkeypatch):
    import src.kkt.stationarity as st
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.config import Config
    from src.emit.expr_to_gams import expr_to_gams
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_text
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_text(TWO_EQ_AXES)
    eq = model.equations["e"]
    # Non-vacuity: the binder IS found, and the new rule is what rejects it.
    binders = st._position_binders(eq, "h", 1, model)
    assert binders == {"v"}
    assert st._another_eq_axis_shares_the_binder_set(eq, "t", binders, model)

    def stat_h() -> str:
        m = parse_model_text(TWO_EQ_AXES)
        eqs, _ = normalize_model(m)
        config = Config()
        gradient = compute_objective_gradient(m, config)
        j_eq, j_ineq = compute_constraint_jacobian(m, eqs, config)
        kkt = assemble_kkt_system(m, gradient, j_eq, j_ineq, config)
        return expr_to_gams(st.build_stationarity_equations(kkt, config)["stat_h"].lhs_rhs[0])

    current = stat_h()
    assert "h(v,v)" not in current, current
    monkeypatch.setattr(st, "_position_binders", lambda *a, **k: None)
    assert current == stat_h(), "two aliased eq axes must keep the pre-#1782 path"


def test_the_representative_comes_from_the_MAJORITY_structure_group():
    """PR #1788 review round 12: the #1110 multi-pattern step switches to a
    majority-structure entry, so an eligible representative from the MINORITY
    would be replaced by an ineligible one after a binder-only admission had
    consolidated the offsets. ``_eligible_binder_rep`` mirrors that grouping."""
    from types import SimpleNamespace

    from src.ir.ast import Binary, Const, ParamRef
    from src.kkt.stationarity import _eligible_binder_rep

    plain = ParamRef("a", ("x",))  # structure A
    other = Binary("+", Const(1.0), ParamRef("a", ("x",)))  # structure B

    def jac(rows, cols, derivs):
        return SimpleNamespace(
            get_derivative=lambda r, c: derivs[(r, c)],
            index_mapping=SimpleNamespace(row_to_eq=rows, col_to_var=cols),
        )

    rows = {0: ("e", ("t1",)), 1: ("e", ("t2",)), 2: ("e", ("t3",))}
    cols = {0: ("h", ("t2",)), 1: ("h", ("t3",)), 2: ("h", ("t1",))}
    # (0,0): eq t1 / var t2 -> eligible; (1,1): t2/t3 eligible; (2,1): t3/t3 not.
    entries = [(0, 0), (1, 1), (2, 1)]

    # Majority = structure B {(1,1), (2,1)}; its eligible entry is (1,1), chosen
    # even though the minority entry (0,0) comes first.
    derivs = {(0, 0): plain, (1, 1): other, (2, 1): other}
    assert _eligible_binder_rep(jac(rows, cols, derivs), entries, 0) == (1, 1)

    # Only the MINORITY holds an eligible entry: majority = structure B over the
    # two ineligible entries (2,1) t3/t3 and (3,3) t1/t1 -> None, so the
    # admission is withdrawn before consolidation.
    rows[3], cols[3] = ("e", ("t1",)), ("h", ("t1",))
    derivs = {(0, 0): plain, (2, 1): other, (3, 3): other}
    assert _eligible_binder_rep(jac(rows, cols, derivs), [(0, 0), (2, 1), (3, 3)], 0) is None

    # Positive control: one structure group -> its first eligible entry.
    same = {(0, 0): plain, (1, 1): plain, (2, 1): plain}
    assert _eligible_binder_rep(jac(rows, cols, same), entries, 0) == (0, 0)


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
