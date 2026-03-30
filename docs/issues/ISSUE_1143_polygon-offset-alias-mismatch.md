# polygon: Offset-Alias Gradient Complete Failure (100% Mismatch)

**GitHub Issue:** [#1143](https://github.com/jeffreyhorn/nlp2mcp/issues/1143)
**Status:** OPEN
**Severity:** Critical — objective mismatch (100%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** polygon

---

## Problem Summary

The polygon model (Largest Small Polygon) uses offset-based aliasing with
`sum(j(i+1), ...)` patterns where `j` is an alias of `i` and the sum
iterates over the successor element. The MCP objective is 0.0 versus
the NLP objective of 0.780, indicating complete failure of the gradient
computation.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| polygon | 0.780 | 0.0 | 100% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/polygon.gms -o /tmp/polygon_mcp.gms
gams /tmp/polygon_mcp.gms lo=2
# Objective: 0.0, expected: 0.780
```

---

## Root Cause Analysis

The polygon model uses:

```gams
Alias(i, j);
```

With offset-indexed alias sums like:

```gams
eq(i).. var(i) =e= sum(j$(ord(j) = ord(i)+1), expr(i,j));
```

This pattern selects the successor element using an ordinal condition on the
alias. The combination of alias + offset creates a challenging pattern for the
AD engine.

### Why 100% Failure

A 100% mismatch (objective = 0.0) suggests that the gradient is entirely zero
for all primal variables, which would cause the stationarity equations to
degenerate to `0 = 0` or trivially satisfied conditions. This can happen when:

1. **All VarRef derivatives return 0**: The `_diff_varref` index matching fails
   for every variable reference because aliased+offset indices never match the
   expected `wrt_indices` tuple.

2. **Sum collapse produces empty results**: The `_partial_collapse_sum` cannot
   find a valid matching for offset-alias patterns, returning 0 derivative.

3. **Stationarity equations become trivial**: With zero objective gradient and
   zero constraint Jacobian terms, all stationarity equations are `piL - piU = 0`,
   and the solver converges to a trivial feasible point (all variables at bounds).

### Investigation Steps

1. Generate the MCP and check if stationarity equations contain any non-trivial terms
2. Test the AD output directly: differentiate the polygon objective w.r.t. each variable
3. Check if `_partial_collapse_sum` can handle `sum(j$(ord(j)=ord(i)+1), ...)`
4. Verify if the offset-alias pattern is fundamentally unsupported

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/polygon.gms` — Source model

## Current Status (2026-03-30)

Translates but MCP compilation fails with $120/$149/$171 errors. Stationarity equations use literal elements with arithmetic offsets (e.g., `theta(i1+1)`) and unknown alias sets. This is distinct from the standard alias differentiation root cause.
