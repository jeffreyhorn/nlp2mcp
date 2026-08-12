"""Shape fixture for the fawley constraint-index-diagonal binding (Issue #1111).

When a constraint's domain index is a declared **subset** of a variable's domain
index, the emitter's disjointness test — which compares index *names* — cannot
see the relationship (`Set cfq(cf)` vs `bq(c,cf)`: `cfq` is not literally in
`{c, cf}`), so it classifies the pair as "truly disjoint by NAME" and sums the
multiplier over the whole subset domain. That over-counts by `|cfq|`: the
per-cell derivative has already collapsed to the diagonal.

**Corpus-free by design** — the obvious spelling would parse
`data/gamslib/raw/fawley.gms` and `pytest.skip` when absent, but `ci.yml`
provisions only the five `--fast` fixtures, so such a fixture would skip on every
CI run and guard nothing (`SPRINT_37/P7_INFRA_CATALOG.md` §1.2).

**Suffix tolerance is load-bearing.** Real fawley emits the AD layer's
re-symbolised `cfq__`; this synthetic has no alias collision to force the suffix,
so it emits the plain `cfq`. The assertions match `cfq\\w*` rather than a literal
form — the same `__`-blindness that made the *first* narrowing attempt under-fire
on dinam/shale.
"""

from __future__ import annotations

import re

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.config import Config
from src.emit.expr_to_gams import expr_to_gams
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_text
from src.kkt.assemble import assemble_kkt_system
from src.kkt.stationarity import build_stationarity_equations

pytestmark = pytest.mark.unit


def _stat(source: str, name: str) -> str:
    model = parse_model_text(source)
    normalized_eqs, _ = normalize_model(model)
    config = Config()
    gradient = compute_objective_gradient(model, config)
    j_eq, j_ineq = compute_constraint_jacobian(model, normalized_eqs, config)
    kkt = assemble_kkt_system(model, gradient, j_eq, j_ineq, config)
    return expr_to_gams(build_stationarity_equations(kkt, config)[name].lhs_rhs[0])


# fawley's shape: `cfq` is a declared subset of `cf`, the constraint is indexed
# over `cfq`, and the variable `bq(c,cf)` carries the parent index. The
# coefficient references the PARENT (`cf` via char/bposs-style terms), never the
# subset — which is exactly what makes the derivative diagonal in this pair.
_SUBSET_DIAGONAL = """
Set c   / c1, c2 /
    cf  / f1, f2 /
    cfq(cf) / f1 /
    m   / m1 /;
Parameter char(c,m) / c1.m1 1.0, c2.m1 2.0 /;
Set bposs(cf,c) / f1.c1, f1.c2, f2.c1 /;
Variable obj, q(cf,m), bq(c,cf);
Equation objdef, pbal(cfq,m);
objdef.. obj =e= sum((c,cf), bq(c,cf)*bq(c,cf));
pbal(cfq,m).. q(cfq,m) =e= sum(c$bposs(cfq,c), char(c,m)*bq(c,cfq));
Model m1 /all/; Solve m1 using nlp minimizing obj;
"""


def test_subset_constraint_index_binds_to_its_parent():
    """The multiplier term must carry a `sameas` diagonal binding.

    Fail-before (measured on the committed golden): `stat_bq` contains exactly
    **1** `sameas` — the pre-existing `mbal` one — and the `pbal`/`qsb` terms are
    summed over the whole `cfq` domain unguarded, over-counting by `|cfq|`.

    Pass-after: the multiplier term acquires `$(sameas(cfq…, cf))`.
    """
    text = _stat(_SUBSET_DIAGONAL, "stat_bq")

    assert re.search(r"sameas\(cfq\w*,\s*cf\)", text), (
        "the subset constraint index is not bound to its parent — the multiplier "
        f"is still summed over the whole subset domain; got: {text}"
    )


def test_multiplier_is_still_summed_not_rewritten():
    """The binding is a guard, not an index rewrite.

    The correct shape keeps `sum(cfq…, … nu_pbal(cfq…,m) …)` and adds a `sameas`
    condition — mirroring the `mbal` term that was already correct in the golden.
    Rewriting the multiplier's index to `cf` instead would change which dual the
    row references.
    """
    text = _stat(_SUBSET_DIAGONAL, "stat_bq")

    assert re.search(
        r"nu_pbal\(cfq\w*,\s*m\)", text
    ), f"the multiplier index was rewritten rather than guarded; got: {text}"
    assert re.search(
        r"sum\(\(?cfq\w*", text
    ), f"the summation over the subset domain was removed entirely; got: {text}"


def test_binding_does_not_fire_without_the_subset_relation():
    """Negative control: no subset declaration ⇒ no `sameas` binding.

    `cfq` here is an independent set, not `cfq(cf)`, so the constraint index
    genuinely is disjoint from the variable's domain and the plain sum is
    correct. This is the discriminating half — conjunct 1 alone (the subset-parent
    relation) leaked onto dinam/prolog/shale in Sprint 37 Task 6.
    """
    independent = _SUBSET_DIAGONAL.replace("cfq(cf) / f1 /", "cfq / f1 /")
    text = _stat(independent, "stat_bq")

    assert not re.search(r"sameas\(cfq\w*,\s*cf\)", text), (
        "the binding fired without a declared subset relation — the predicate is "
        f"too broad; got: {text}"
    )
