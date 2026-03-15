# qabel: Regression — _partial_collapse_sum Builds symbolic_wrt in Wrong Order

**GitHub Issue:** [#1089](https://github.com/jeffreyhorn/nlp2mcp/issues/1089)
**Status:** PARTIALLY FIXED
**Severity:** High — model_optimal regressed to path_solve_terminated
**Progress:** Primary bug fixed: `symbolic_wrt` now built in `wrt_indices` position order via `concrete_to_symbolic` mapping. Model improved from path_solve_terminated to model_optimal, but objective mismatches (MCP=51133 vs NLP=46965, ~8.2%) due to secondary alias issue (x(np,k) != x(n,k) in `_diff_varref` — pre-existing).
**Date:** 2026-03-14
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

## Suggested Fix

Replace the `symbolic_wrt` construction at lines 1896-1903 of `derivative_rules.py`:

**Current (wrong):**
```python
symbolic_wrt = tuple(
    (IndexOffset(sum_idx, conc.offset, conc.circular) if isinstance(conc, IndexOffset) else sum_idx)
    for sum_idx, conc in zip(matched_sum_indices, matched_concrete, strict=True)
)
```

**Fixed:**
```python
# Build mapping: concrete_value -> symbolic_index
concrete_to_symbolic = {}
for sum_idx, conc in zip(matched_sum_indices, matched_concrete):
    key = conc if not isinstance(conc, IndexOffset) else conc
    concrete_to_symbolic[key] = sum_idx

# Rebuild in wrt_indices position order
symbolic_wrt = tuple(
    (IndexOffset(concrete_to_symbolic[idx], idx.offset, idx.circular)
     if isinstance(idx, IndexOffset)
     else concrete_to_symbolic[idx])
    for idx in wrt_indices
    if idx in concrete_to_symbolic
)
```

### Secondary Issue: Alias-Indexed Variable Differentiation

Even with Bug 1 fixed, the term `x(np,k)` in the body (where `np` is alias of `n`) would
differentiate to 0 w.r.t. `x(n,k)` because `('np','k') != ('n','k')`. The AD engine's
`_diff_varref` performs exact tuple matching without alias resolution. The correct derivative
should produce a Kronecker delta `sameas(np,n)`. This is a separate, pre-existing issue.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py:1896-1903` | Build `symbolic_wrt` in `wrt_indices` position order |
| `src/ad/derivative_rules.py:259-277` | (Secondary) Add alias-aware matching in `_diff_varref` |
