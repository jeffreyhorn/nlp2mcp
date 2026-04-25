# qabel/abel: AD Drops `u`-Criterion Gradient When Sum Index is a Subset of Variable's Domain

**GitHub Issue:** [#1311](https://github.com/jeffreyhorn/nlp2mcp/issues/1311)
**Status:** OPEN — targeted for Sprint 26 (or Sprint 25 Day 13 buffer if schedule allows)
**Severity:** High — produces a numerically-wrong-but-syntactically-valid MCP for any model whose criterion uses `sum(subset, ...)` shapes; affects qabel (8.88% rel_diff) and abel (29.77% rel_diff) directly; corpus audit needed for breadth
**Date filed:** 2026-04-25
**Discovered:** Sprint 25 Day 8 PATH-solve reassessment (PR #1310, see `docs/planning/EPIC_4/SPRINT_25/DAY8_QABEL_ABEL_REASSESSMENT.md`)
**Supersedes classifications in:** `DAY7_COHORT_SWEEP.md` (qabel/abel were marked "Pattern C massive enumeration" / "AD-correct nonconvex noise"; both classifications are now refuted by the Day 8 verification)
**Related:**
- `#1150` (qabel/abel — original "Pattern A" classification; do NOT close until #1311 lands)
- `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Pattern A rows for qabel/abel/cge-family

---

## Problem Summary

For models whose criterion contains a `sum(subset_index, ...)` aggregation where the bound index is a **subset of** the variable's declared domain (rather than the same name or an alias of it), the AD layer silently drops the entire term from the gradient. The variable's stationarity equation is missing the corresponding contribution.

In abel/qabel, the criterion is:

```gams
criterion..
   j =e= .5 * sum((k, n, np), (x(n,k) - xtilde(n,k))   * w(n, np, k) * (x(np,k) - xtilde(np,k)))
      +  .5 * sum((ku, m, mp), (u(m, ku) - utilde(m, ku)) * lambda(m, mp) * (u(mp, ku) - utilde(mp, ku)));

* x is declared over (n, k); the x-quadratic sums (k, n, np) — bound `k` matches variable's `k`. Works correctly.
* u is declared over (m, k); the u-quadratic sums (ku, m, mp) — bound `ku` is a SUBSET of `k`. AD returns Const(0.0).
```

Every `u(m, k)` partial returns `Const(0.0)` from `compute_objective_gradient`, INCLUDING indices `k_v` where `ku(k_v)` holds (i.e., where the u-quadratic sum is genuinely active). The expected derivative for `k_v ∈ ku` is `sum(mp, (lambda(m, mp) + lambda(mp, m))/2 * (u(mp, k_v) - utilde(mp, k_v)))`.

## Reproduction

```bash
.venv/bin/python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
from src.ad.gradient import compute_objective_gradient

m = parse_model_file('data/gamslib/raw/abel.gms')
normalize_model(m)
g = compute_objective_gradient(m)
for col_id in range(g.num_cols):
    var_name, idx = g.index_mapping.col_to_var[col_id]
    if var_name == 'u':
        d = g.get_derivative(col_id)
        print(f'{var_name}({\",\".join(idx)}) -> {d}')
"
```

Output (abridged — every line is `Const(0.0)`):
```
u(gov-expend,1964-i) -> Const(0.0)
u(gov-expend,1964-ii) -> Const(0.0)
...
u(money,1965-iv) -> Const(0.0)
```

In abel, `ku = {'1964-i' .. '1965-iii'}` (first 7 of 8 quarters). For all 7 of those `k` values, the derivative w.r.t. `u(m, k)` should be nonzero — but the AD returns 0.

## Why this wasn't caught earlier

- **Day 5 investigation** focused on the **x-quadratic** form (which is correct) and concluded "AD layer is byte-correct" for qabel/abel based on `stat_x` matching the symmetric quadratic shape. The doc didn't inspect `stat_u` or the u-quadratic.
- **Day 7 cohort sweep** classified abel as "Other (AD-correct, stateq convention or solver noise)" based on `stat_x` shape alone.
- **Day 8 hand-derivation** of `stat_x` against the formal KKT was correct in isolation but didn't catch that the OTHER stationarity equation (`stat_u`) was missing an entire term.
- The actual reveal came from running `compute_objective_gradient` directly and printing every entry — which exposed the `Const(0.0)` entries on u immediately. The lesson: when investigating mismatch in a model with multiple variable types, inspect EVERY variable's gradient, not just the most-studied one.

## Verification that this is THE bug, not just A bug

Multi-start NLP confirms both qabel and abel have UNIQUE NLP optima (5 starts × 2 models, all converged to the same objective). If the MCP's KKT system faithfully represents the unique NLP optimum, MCP and NLP must agree numerically. The 8.88% / 29.77% gaps are direct evidence of a missing or wrong KKT term. The hand-derivation showed `stat_x` is correct, leaving `stat_u` as the candidate site, which the AD inspection confirmed.

## Likely fix area

- `src/ad/derivative_rules.py::_diff_varref` — variable-reference differentiation, the matching path that decides whether a sum's bound index can bind to a variable index. Likely the place where "bound index is a SUBSET of variable's domain" needs to be recognized.
- `src/ad/index_mapping.py` — set/subset resolution; may need extending so that `ku ⊆ k` is treated as "ku binds elements valid for x(*, k)".

The fix likely requires:
1. Recognizing `ku(k)` declarations as parent-child set relationships.
2. In `_diff_varref` (or wherever the sum-bound-index match happens), accepting a bind from a child set to a parent-set variable index.
3. Emitting the conditional `$(ku(k))` guard on the resulting derivative term to preserve the source's restriction (the term is only active where `ku` membership holds).

## Expected impact

Direct: qabel and abel rel_diff → near zero (Match recoveries when Sprint 26 retests). +2 to the Match target.

Corpus-wide audit: the same `sum(subset, ...)` shape exists in CGE and stochastic models (per `AUDIT_ALIAS_AD_CARRYFORWARD.md`'s Pattern A table — #1138, #1140 cohorts). Some classifications in `DAY7_COHORT_SWEEP.md` may have been mis-attributed to "Pattern C" or "stochastic-dynamics" when the actual cause is this AD bug. Need to re-run the cohort sweep after #1311 lands.

## Files

- `src/ad/derivative_rules.py` — likely fix site (`_diff_varref` or `_partial_collapse_sum`).
- `src/ad/index_mapping.py` — supporting subset resolution.
- `src/ad/gradient.py::compute_objective_gradient` — entry point; not the bug but where verification happens.
- `data/gamslib/raw/{qabel,abel}.gms` — repro corpus.

## Status

Open as of Sprint 25 Day 8. Sprint 25's Day 14 retest does NOT include this fix. Sprint 26 carryforward.
