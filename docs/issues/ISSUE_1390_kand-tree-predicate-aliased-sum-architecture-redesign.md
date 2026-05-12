# kand: alias-AD per-instance enumeration produces 22 phantom-offset cross-terms in stat_y (tree-predicate-aliased Sum architecture redesign)

**GitHub Issue:** [#1390](https://github.com/jeffreyhorn/nlp2mcp/issues/1390)
**Status:** OPEN (filed Sprint 26 Day 7, 2026-05-12)
**Severity:** Medium — produces a valid MCP solve that converges to Optimal but with ~92.5% rel_diff vs the NLP optimum; not a localized AD-helper bug but an architecture-level reclassification.
**Date:** 2026-05-12
**Last Updated:** 2026-05-12
**Affected Models:** kand (target); likely affects other models with tree-predicate-aliased Sum bodies (stochastic-programming scenario-tree shapes).
**Target Sprint:** Sprint 27 (10–16h across architectural change + integration tests + Tier 0/1 byte-stable regression).
**Cross-references:**
- Predecessor: #1141 (now CLOSED 2026-05-12 via Sprint 26 Day 7 — see [docs/issues/completed/ISSUE_1141_kand-alias-tree-mismatch.md](completed/ISSUE_1141_kand-alias-tree-mismatch.md)).
- Sister Sprint 27 carryforwards (similar AD-architecture-level reclassifications):
  - #1381 (Pattern C Phase B redesign — Sprint 26 Day 3 reclassification).
  - #1385 (Option 1 short-circuit redesign — Sprint 26 Day 4 reclassification).
- Reclassification source: [docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md](../planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md) §"Issue #1141" (original keep-open rationale; superseded by Day 7 intractability discovery).

## Problem Summary

kand produces `solution_comparison.comparison_status = mismatch` with NLP-MCP rel_diff ~92.5% on the obj. The bug is rooted in how the AD / stationarity pipeline handles a tree-predicate-aliased Sum body: instead of emitting a single guarded cross-term, it enumerates over each static element of the `n` set and produces 22 phantom-offset terms.

Sprint 26 Day 6 scoping (`docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 6 §"kand alias-AD scoping") established the bug shape. Day 7 `SPRINT25_DAY2_DEBUG=1` trace analysis confirmed the root cause is AD-architecture-level — not a localized helper bug that fits inside Day 7's 4–6h budget. Reclassified to Sprint 27 per the Day 7 Task 5 contingency in `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md`.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/kand.gms \
  -o /tmp/kand_mcp.gms --skip-convexity-check --quiet

# Inspect the broken stat_y emit (22 phantom-offset terms):
grep -E "^stat_y\(j,t,n\)" /tmp/kand_mcp.gms
# Expected: 1 cross-term: sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner))
# Observed (the bug): 22 sum(nn, eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+k))$(...) terms for k=-8..+11

gams /tmp/kand_mcp.gms lo=2
# Solves Optimal but rel_diff ~92.5% vs NLP
```

## Bug shape (from Day 6 scoping)

**Source body** (`data/gamslib/raw/kand.gms:99–100`):

```gams
dembalx(j,tn(t,n))..
   sum(i, a(j,i)*x(i,t)) + y(j,tn) =g= dem(n,j) + eps*sum(tree(nn,n), y(j,t-1,nn));
```

**Set declarations** (`data/gamslib/raw/kand.gms:17–56`):
- `Alias (n,nn);` — `nn` is the alias of `n`.
- `tree(n,n)` is a static 9-element predicate over `(parent, child)` pairs:
  - `(n-1, n-4), (n-1, n-5), (n-1, n-6)`
  - `(n-2, n-7), (n-2, n-8), (n-2, n-9)`
  - `(n-3, n-10), (n-3, n-11), (n-3, n-12)`

**Expected `stat_y(j,t,n)` cross-term** (hand-derived from KKT):

```gams
... + sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner)) + ...
```

(For specific `n` values: `n=n-1` produces a cross-term over `n_inner ∈ {n-4, n-5, n-6}`; `n=n-2` produces one over `{n-7, n-8, n-9}`; `n=n-3` produces one over `{n-10, n-11, n-12}`; all other `n` values produce no cross-term from this Sum.)

**Current emit (broken)** — 22 phantom-offset terms:

```gams
stat_y(j,t,n).. (prob(n) * f(j,t) * 1$(tn(t,n)) + ((-1) * lam_dembalx(j,t,n))$(tn(t,n))
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+9))$(...))$(tn(t,n)))
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n+10))$(...))$(tn(t,n)))
  + ... [20 more terms with offsets k = -8..+11] ...
  + sum(nn, ((eps * 1$(tree(nn,n)) * lam_dembalx(j,t+1,n-8))$(...))$(tn(t,n)))
  - piL_y(j,t,n))$(tn(t,n)) =E= 0;
```

## Root cause (from Day 7 SPRINT25_DAY2_DEBUG=1 trace analysis)

The AD pipeline's cross-term enumeration step iterates over each static element of the `n` set (n-1, n-2, ..., n-9) as a candidate wrt_indices, producing one cross-term per element-substitution. Trace excerpt (Day 7, captured against current main):

```
[diff_varref] enter name='y' expr.indices=('p-2', 'time-1', 'nn') wrt_indices=('p-2', 'time-2', 'n-5') bound_indices=['nn']
[diff_varref] -> Const(0.0) [no match]
[diff_varref] enter name='y' expr.indices=('p-2', 'time-2', 'n-9') wrt_indices=('p-2', 'time-2', 'n-5') bound_indices=[]
[diff_varref] -> Const(0.0) [no match]
[diff_varref] enter name='y' expr.indices=('p-2', 'time-2', 'n-9') wrt_indices=('p-2', 'time-2', 'n-9') bound_indices=[]
[diff_varref] -> Const(1.0) [exact index match]
```

After enumeration, each match-positive concrete-element pair is converted back to symbolic + offset form for emit. This produces one phantom-offset term per static element relationship, NOT a single predicate-guarded Sum.

## Investigation pointers (Phase 0 / Sprint 27 prep work)

1. The fix surface is the AD-architecture choice: per-instance enumeration vs predicate-constrained-sum. Single-helper fixes won't suffice — the enumeration happens in `_compute_inequality_jacobian` / `_compute_equality_jacobian` (`src/ad/constraint_jacobian.py:903`, `:1027`) which iterates over each equation instance.

2. The correct architecture (hypothesized): when a constraint body has a Sum with a static-set predicate (`sum(tree(nn,n), ...)`), the stationarity cross-term should preserve the predicate structure rather than enumerate. This is analogous to Issue #666's `_preserve_subset_var_indices` (preserves subset VarRef indices) and Issue #1164/#1175's `KKTSystem.param_domain_widenings` (preserves widened parameter domains) — both Sprint 23+24 architectural changes.

3. **Phase 0 acceptance gate** (per Sprint 27 prep methodology established Sprint 26 Days 3 + 4): translate kand with a prototype patch + verify GAMS compile-clean + hand-derive `stat_y('p-1', 'time-2', 'n-4')` KKT instance vs the emit BEFORE committing the full implementation budget. The Sprint 26 Day 3 + Day 4 reclassifications established that prep-task design validation at the patch-site level is insufficient; empirical end-to-end correctness verification is required.

## Files involved (preliminary)

- `src/ad/constraint_jacobian.py` (`_compute_inequality_jacobian` + `_compute_equality_jacobian` per-equation enumeration; `_expand_sum_body` / `_expand_sums_with_unresolved_offsets` static-set substitution)
- `src/ad/derivative_rules.py` (`_partial_collapse_sum` + `_partial_index_match`; `_diff_varref` with `bound_indices`)
- `src/kkt/stationarity.py` (cross-term accumulation site)
- `data/gamslib/raw/kand.gms` (source — kept as the target reproducer)
- `data/gamslib/mcp/kand_mcp.gms` (current emit with 22 phantom terms)

## Effort estimate

10–16h across three sub-phases (architectural change + integration tests + Tier 0/1 byte-stable regression). Mirrors the Sprint 27 #1381 (Pattern C Phase B redesign) + #1385 (Option 1 short-circuit redesign) effort profiles for similar AD-architecture-level reclassifications.

## Related

- **#1141** — closed 2026-05-12 via Sprint 26 Day 7; the original alias-AD framing remains accurate; the close-and-refile follows the Day 7 §"intractable in budget" contingency per `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` Day 7 Task 5 contingency.
- **#1381** (Sprint 27): Pattern C Phase B redesign — similar AD-architecture-level reclassification from Sprint 26 Day 3.
- **#1385** (Sprint 27): Option 1 short-circuit redesign — similar reclassification from Sprint 26 Day 4.
- **Sprint 26 Prep Task 5**: `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Issue #1141" — original keep-open rationale; superseded by Day 7 intractability discovery.
