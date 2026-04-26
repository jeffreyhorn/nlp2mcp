# qabel/abel: AD Drops `u`-Criterion Gradient When Sum Index is a Subset of Variable's Domain

**GitHub Issue:** [#1311](https://github.com/jeffreyhorn/nlp2mcp/issues/1311)
**Status:** RESOLVED in Sprint 25 Day 8 (this PR)
**Severity:** High — produced a numerically-wrong-but-syntactically-valid MCP for any model whose criterion uses `sum(subset, ...)` shapes; affected qabel and abel directly
**Date filed:** 2026-04-25
**Date resolved:** 2026-04-25
**Discovered:** Sprint 25 Day 8 PATH-solve reassessment (PR #1310, see `docs/planning/EPIC_4/SPRINT_25/DAY8_QABEL_ABEL_REASSESSMENT.md`)
**Supersedes classifications in:** `DAY7_COHORT_SWEEP.md` (qabel/abel were marked "Pattern C massive enumeration" / "AD-correct nonconvex noise"; both classifications are now refuted by the Day 8 verification)
**Related:**
- `#1150` (qabel/abel — original "Pattern A" classification; the AD piece is now resolved here, but qabel/abel may still need a separate fix for the phantom-stateq-enumeration variant before they fully match — see "Remaining work" below)

---

## Problem Summary

For models whose criterion contains a `sum(subset_index, ...)` aggregation where the bound index is a **subset of** the variable's declared domain (rather than the same name or an alias of it), the AD layer silently dropped the entire term from the gradient. The variable's stationarity equation was missing the corresponding contribution.

In abel/qabel, the criterion is:

```gams
criterion..
   j =e= .5 * sum((k, n, np), (x(n,k) - xtilde(n,k))   * w(n, np, k) * (x(np,k) - xtilde(np,k)))
      +  .5 * sum((ku, m, mp), (u(m, ku) - utilde(m, ku)) * lambda(m, mp) * (u(mp, ku) - utilde(mp, ku)));

* x is declared over (n, k); the x-quadratic sums (k, n, np) — bound `k` matches variable's `k`. Worked correctly.
* u is declared over (m, k); the u-quadratic sums (ku, m, mp) — bound `ku` is a SUBSET of `k`. AD returned Const(0.0).
```

Every `u(m, k)` partial returned `Const(0.0)` from `compute_objective_gradient`, INCLUDING indices `k_v` where `ku(k_v)` holds (i.e., where the u-quadratic sum is genuinely active).

---

## Root Cause

`src/ad/derivative_rules.py::_is_concrete_instance_of` checked
`set_def.members` directly when looking up a symbolic set name. A dynamic
subset declared as `Set ku(k);` has `domain=('k',)` and `members=[]` at parse
time — its actual membership is computed at runtime via assignments like
`ku(k) = yes$(ord(k) < card(k))`. The pre-fix code returned `False`
"definitively" when `concrete not in members` — so a sum like
`sum(ku, ...)` where `ku ⊆ k` rejected every concrete element of `k`,
even though those elements ARE the candidate population.

`src/ad/index_mapping.py::resolve_set_members` already had an issue-#723
fallback that handles the dynamic-subset case: when `members` is empty
but `domain` is non-empty, it recurses into the parent set. The fix
re-routes `_is_concrete_instance_of`'s set-name path through that
resolver instead of accessing `.members` directly.

---

## Fix (Sprint 25 Day 8, this PR)

Two changes:

1. **`src/ad/derivative_rules.py::_is_concrete_instance_of`** — replace
   the direct `set_def.members` access with a call to
   `resolve_set_members(symbolic, model_ir, quiet=True)`. The unified
   resolver handles plain sets, aliases, AND dynamic-subset → parent
   fallback, so the fix is structural rather than special-casing the
   dynamic-subset case at every membership-check site.
2. **`src/ad/index_mapping.py::resolve_set_members`** — add a
   `quiet: bool = False` kwarg that suppresses the per-call
   "Dynamic subset has no static members; falling back to parent set"
   warning when invoked from membership-check contexts. AD calls the
   resolver per-(sum-index, candidate) pair during differentiation, so
   without `quiet=True` the warning would fire dozens of times per
   equation translation. The original instantiation use sites still
   default to `quiet=False` (where the warning is actionable telemetry
   for unusual model shapes).

## Verification

Pre-fix repro (from the issue body):

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

Pre-fix: every `u(m, k) -> Const(0.0)`. Post-fix: every entry is a non-zero AST expression — the symmetric quadratic gradient

```
0.5 * (sum(mp__, (u(mp__, k_v) - utilde(mp__, k_v)) * lambda(m, mp__))
     + sum(m__,  (u(m__,  k_v) - utilde(m__,  k_v)) * lambda(m__,  m)))
```

correctly representing `((L + L^T)/2) * (u - utilde)|_{m_v}`.

Emitted abel `stat_u` post-fix:

```gams
stat_u(m,k).. (0.5 * (sum(mp__, (u(mp__,k) - utilde(mp__,k)) * lambda(m,mp__))
                   + sum(m__,  (u(m__,k)  - utilde(m__,k))  * lambda(m__,m)))
            + sum(n, ((-1) * b(n,m)) * nu_stateq(n,k)))$(ku(k)) =E= 0;
```

The criterion u-gradient and the stateq Lagrangian transpose are both present, gated by the equation-level `$(ku(k))` (which gives the runtime subset-restriction). For abel's card(k)=8, this is the complete and structurally correct stat_u.

## Tests

`tests/unit/ad/test_subset_domain_membership.py` — six cases:
- Concrete element of parent matches dynamic subset (the qabel/abel core fix).
- Concrete element NOT in parent does NOT match.
- Direct parent-set membership unchanged.
- Dynamic subset with no resolvable parent returns False definitively.
- Alias chain to dynamic subset resolves via the parent fallback.
- End-to-end abel: every u-entry in `compute_objective_gradient` is non-zero.

## Regression coverage

- 11/11 Tier 0 + Tier 1 canaries: byte-identical to pre-fix golden (the fix only changes emission for models with the launch-shaped or qabel/abel-shaped `sum(subset, ...)` pattern).
- 54/54 full matching set golden-file regression: 54/54 PASS — no model in the matching set was affected by the fix.

## Remaining work — qabel/abel still don't fully match the NLP baseline

Solving the post-fix MCPs:

| Model | NLP obj    | MCP pre-#1311 | MCP post-#1311 | Notes |
|-------|------------|---------------|----------------|-------|
| qabel | 46965.0362 | 51133.487     | 1.41e+17       | Worse |
| abel  | 225.1946   | 158.150       | 97.185         | Different local optimum found |

Post-fix, qabel's MCP objective explodes to ~1.4e17 and abel converges to a different local optimum (97 vs NLP 225). The reason isn't this issue — it's a **separate Pattern C variant** that inflates qabel's `stat_u` (and similarly its `stat_x`) with massive enumeration of stateq lag offsets `k-9 .. k-68` (qabel's card(k)=75; the enumeration spans 60 phantom offsets). That phantom enumeration was harmless when the criterion-gradient was missing (`stat_u` was effectively under-determined and PATH found *some* solution); now that the gradient is correctly present, the phantom enumeration scales the contribution incorrectly and pushes the solver away from the true optimum.

Documented in `DAY7_COHORT_SWEEP.md` §"#1150 qabel — Pattern C (massive enumeration variant)". Not in scope for #1311 — needs a separate issue file and a separate fix (likely in `src/kkt/stationarity.py::_compute_index_offset_key` enumeration logic).

## Files

- `src/ad/derivative_rules.py::_is_concrete_instance_of` — fixed.
- `src/ad/index_mapping.py::resolve_set_members` — added `quiet` kwarg.
- `src/ad/gradient.py::compute_objective_gradient` — entry point; not the bug but where verification happens.
- `tests/unit/ad/test_subset_domain_membership.py` — new regression tests.
- `data/gamslib/raw/{qabel,abel}.gms` — repro corpus.

## Status

**Resolved** in Sprint 25 Day 8 PR #1310. The "AD drops u-criterion gradient on subset-sum" surface is fixed. Qabel/abel full numerical recovery requires a separate Pattern C fix (filed as a follow-up issue).
