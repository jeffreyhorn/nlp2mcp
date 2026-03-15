# qabel: Regression — _partial_collapse_sum Builds symbolic_wrt in Wrong Order

**GitHub Issue:** [#1089](https://github.com/jeffreyhorn/nlp2mcp/issues/1089)
**Status:** PARTIALLY FIXED
**Severity:** High — model_optimal regressed to path_solve_terminated
**Progress:** Primary bug (symbolic_wrt ordering) fixed in PR #1094. Model restored to model_optimal (MODEL STATUS 1). Objective mismatch (MCP=51133 vs NLP=46965, ~8.9%) is NOT caused by the secondary alias issue — it is a non-convex QCP local-optimum difference. The secondary alias issue (alias-aware `_diff_varref`) was attempted and reverted because it causes regressions in other models.
**Date:** 2026-03-14
**Last Updated:** 2026-03-15
**Affected Models:** qabel

---

## Problem Summary

The qabel model (GAMSlib SEQ=293, "Linear Quadratic Control Problem as QCP") regressed
from model_optimal to path_solve_terminated. PATH reports "Lemke: invertible basis could
not be computed" with 147 singularities out of 446 equations.

The root cause is a bug in the AD engine's `_partial_collapse_sum` function: its fallback
matching builds `symbolic_wrt` in `sum_index_sets` iteration order instead of `wrt_indices`
position order. This causes all objective gradient terms to return 0, making the KKT
system structurally singular.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel_mcp.gms
gams /tmp/qabel_mcp.gms lo=2
# **** SOLVER STATUS     13 System Failure
# **** MODEL STATUS      13 Error No Solution
# Lemke: invertible basis could not be computed.
# 147 singularities out of 446 equations
```

---

## Root Cause

### Model Structure

The objective expression contains:
```gams
sum((k, n, np), (x(n,k) - xtilde(n,k)) * w(n,np,k) * (x(np,k) - xtilde(np,k)))
```

Variable `x` has domain `(n, k)`. When differentiating w.r.t. `x('consumpt','q1')`:
- `wrt_indices = ('consumpt', 'q1')` — 2 elements
- `sum_index_sets = ('k', 'n', 'np')` — 3 elements
- Since 2 < 3, `_partial_collapse_sum` is invoked

### The Fallback Matching Bug

The fallback loop in `_partial_collapse_sum` (line ~1864 of `derivative_rules.py`) iterates
over `sum_index_sets` in order `(k, n, np)`:

1. `sum_idx='k'`: matches `wrt_idx='q1'` (q1 ∈ set k) → matched
2. `sum_idx='n'`: matches `wrt_idx='consumpt'` (consumpt ∈ set n) → matched
3. `sum_idx='np'`: no remaining wrt_indices → remaining

This builds:
- `matched_sum_indices = ['k', 'n']`
- `matched_concrete = ['q1', 'consumpt']`
- `symbolic_wrt = ('k', 'n')` — **follows sum_index_sets order**

The body contains `VarRef('x', ('n', 'k'))`. Differentiation checks:
```python
expr.indices == wrt_indices  →  ('n', 'k') == ('k', 'n')  →  False!
```

Result: `Const(0.0)` — the derivative is zero due to index order mismatch.

### Verified Empirically

```python
differentiate_expr(VarRef('x', ('n','k')), 'x', ('n','k'), config)  →  Const(1.0)  ✓
differentiate_expr(VarRef('x', ('n','k')), 'x', ('k','n'), config)  →  Const(0.0)  ✗
```

### The Correct Behavior

`symbolic_wrt` should preserve `wrt_indices` position order:
- Position 0: `consumpt` → maps to `n`
- Position 1: `q1` → maps to `k`
- Correct: `symbolic_wrt = ('n', 'k')`

---

## Fix Applied (Primary Bug — PR #1094)

The `symbolic_wrt` construction in `_partial_collapse_sum` was fixed to build in
`wrt_indices` position order using a positional `wrt_to_symbolic` list with
`used_match_positions` tracking. This was merged in PR #1094.

**Result:** qabel restored to MODEL STATUS 1 (Optimal), SOLVER STATUS 1 (Normal).

---

## Objective Mismatch Investigation

After the primary fix, qabel shows:
- NLP (CONOPT): obj = 46965.036
- MCP (PATH):   obj = 51133.487
- Mismatch: ~8.9%

### Is this caused by the secondary alias issue?

**No.** Investigation confirmed:

1. The `stat_x` stationarity equation in the generated MCP already includes the correct
   gradient terms. The `x(np,k)` term in the objective produces a `sameas(np,n)` guard
   through the existing `_partial_collapse_sum` machinery (which handles the remaining
   `np` index after collapsing `n` and `k`).

2. The objective mismatch is due to the non-convex nature of the QCP. The KKT system
   finds a different local optimum than CONOPT. Both are valid stationary points.

3. The MCP result (51133.487) is identical whether or not alias-aware `_diff_varref`
   is enabled — confirmed by testing on both `main` and the experimental branch.

---

## Attempted Fix: Alias-Aware `_diff_varref` (REVERTED)

### Approach

Added `_resolve_alias_root()` helper to follow alias chains to root set names, then
modified `_diff_varref` to return `sameas(e_idx, w_idx)` Kronecker deltas when indices
differ only by aliases of the same set.

### Why It Was Reverted

The alias-aware matching is **too aggressive** in summation contexts. When a model has:
```gams
Alias(i, j);
sum((i,j), p(i) * b(i,j) * p(j))
```

Differentiating w.r.t. `p(i)`, the term `p(j)` should NOT produce `sameas(j,i)` because
`j` is a **separate sum iteration variable** — it iterates independently over the same set.
The alias-aware `_diff_varref` incorrectly treats `p(j)` as equivalent to `p(i)` (since
both `i` and `j` alias the same root set), adding a spurious `sameas(j,i)` that restricts
the gradient to the diagonal only.

**Regression:** The `dispatch` model (GAMSlib SEQ=220) went from model_optimal to
objective mismatch (NLP=7.9546, MCP=8.061) because the gradient of the quadratic
`sum((i,j), p(i)*b(i,j)*p(j))` was incorrectly restricted by sameas guards.

### What Must Be Done Before Reattempting

A correct alias-aware differentiation would need to:

1. **Track summation context**: `_diff_varref` would need to know which indices are
   currently being iterated over by enclosing `sum()` expressions, so it can distinguish
   "same iteration variable via alias" from "different iteration variable on same set."

2. **Pass iteration context through the call chain**: The `differentiate_expr` recursive
   calls would need to carry a set of "active iteration indices" (indices bound by enclosing
   sums). When `_diff_varref` encounters an alias match, it should only produce `sameas()`
   if the alias index is NOT in the active iteration set.

3. **Handle nested sums**: The context tracking must handle arbitrarily nested sum
   expressions where the same set appears at multiple levels.

This is a significant refactor of the AD engine's calling convention and is deferred to
a future sprint.

---

## Files Modified

| File | Change | PR |
|------|--------|----|
| `src/ad/derivative_rules.py:~1896` | Build `symbolic_wrt` in `wrt_indices` position order | #1094 |

## Files NOT Modified (Secondary Issue Deferred)

| File | Change | Reason |
|------|--------|--------|
| `src/ad/derivative_rules.py:259-277` | Alias-aware matching in `_diff_varref` | Causes dispatch regression; needs summation-context tracking |
