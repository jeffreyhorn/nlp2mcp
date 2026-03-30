# cclinpts: Alias-Aware Gradient Mismatch

**GitHub Issue:** [#1145](https://github.com/jeffreyhorn/nlp2mcp/issues/1145)
**Status:** OPEN
**Severity:** High — objective mismatch (69.9%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** cclinpts

---

## Problem Summary

The cclinpts model (Piecewise Linear Approximation) uses `Alias(j, jj)` in
bilinear constraint terms. The MCP objective diverges significantly from the
NLP reference.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| cclinpts | -3.00 | -9.98 | 69.9% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/cclinpts.gms -o /tmp/cclinpts_mcp.gms
gams /tmp/cclinpts_mcp.gms lo=2
# Objective: -9.98, expected: -3.00
```

---

## Root Cause Analysis

The cclinpts model uses:

```gams
Alias(j, jj);
```

With sum expressions that iterate over both `j` and `jj` as aliases of the
same underlying set. The large mismatch (69.9%) suggests that the gradient
computation is substantially wrong, likely due to:

1. **Missing cross-term gradients**: When `sum((j,jj), x(j)*A(j,jj)*x(jj))`
   is differentiated, the alias-aware multi-matching should produce both
   collapse paths (`j→target` and `jj→target`), but one or both may be
   failing.

2. **Index order mismatch**: Same as the qabel bug (#1089) — the fallback
   matching in `_partial_collapse_sum` may build `symbolic_wrt` in the wrong
   order.

3. **Alias resolution failure in `_diff_varref`**: The exact tuple comparison
   `('jj',) != ('j',)` prevents VarRef differentiation from recognizing that
   `jj` aliases `j`.

### Investigation Steps

1. Generate the MCP and inspect stationarity equations
2. Check which equations use `Alias(j, jj)` and identify the specific
   gradient terms that are wrong
3. Test if the multi-matching fix from PR #1136 helps
4. Compare with hand-derived KKT conditions

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/cclinpts.gms` — Source model

## Current Status (2026-03-30)

Translates but MCP compilation fails with $120/$149/$171 errors. Similar to polygon (#1143): literal elements used with arithmetic offsets in stationarity equations.
