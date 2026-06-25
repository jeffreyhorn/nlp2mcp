# polygon: Offset-Alias Gradient Complete Failure (100% Mismatch)

**GitHub Issue:** [#1143](https://github.com/jeffreyhorn/nlp2mcp/issues/1143)
**Status:** OPEN
**Severity:** Critical — MCP compilation failure (was objective mismatch, now compile errors)
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

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** the "compile fails / 100% mismatch" status above is **stale (2026-03-30)**. On the current Day-0 DB polygon **matches warm** (`model_optimal_presolve`, 0.7797 ≈ 0.7797) and the harness verdict is **Case b**, `max_residual_row = stat_theta`, rel = **0.492**, dual-transfer consistent → **PROCEED**. The fix is **cold-robustness** (polygon already matches warm), not headline +Match — Class A in `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md`. Also a Case-b validation target for the parent offset-alias-AD architecture (#1111/#1112).

### Hand-Derived KKT Shape

polygon (Largest Small Polygon) optimizes over the angle variables `theta(i)` and radii `r(i)` with offset-alias constraints of the form `… sum(j$(ord(j) = ord(i)+1), expr(i,j)) …` (`j` = alias of `i`, successor element). The angle-variable stationarity must carry, for each constraint `g` in which `theta(i)` (and its offset image `theta(i+1)`) appears, the Jacobian-transpose term `∂g/∂theta(i) · nu_g` summed with the **offset-shifted** contribution from the `i-1`-indexed instance (where `theta(i)` appears as the `j=i` successor of row `i-1`):

```
stat_theta(i)..  ∂obj/∂theta(i) + sum(g, ∂g/∂theta(i)·nu_g)  +  [offset-image cross-term from row i-1]  =E= 0
```

A **non-integer** residual (0.492) indicates a *partial* / mis-scaled offset-alias cross-term (an offset image dropped or mis-weighted), not a cleanly missing unit term — consistent with the offset-alias AD composing the successor selection incorrectly.

### Expected Emit Pattern

`polygon_mcp.gms` `stat_theta(i)` should contain the direct `∂g/∂theta(i)·nu_g` terms **and** the offset-image cross-term contributed by the `ord(j)=ord(i)+1` selection at the predecessor row (the `theta(i)`-as-successor term). (Hypothesis — the actual builder `file:line` confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms --json /tmp/phase0_polygon.json
```

- **PROCEED (Case b):** `max_residual_row = stat_theta`, rel ≈ 0.49. ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) and `compare_objective_match` on the **cold** solve; **add a property-test fixture** for the `ord(j)=ord(i)+1` offset-alias shape (parent #1111/#1112).

### PROCEED/REPLAN Signal

- **PROCEED** — Day-0 Case b on `stat_theta`, rel ≈ 0.49 (✅ confirmed).
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the offset-alias successor selection in `src/ad/derivative_rules.py` (`_partial_collapse_sum`, `_diff_varref`) and the index-substitution in `src/kkt/stationarity.py` (`_replace_indices_in_expr`). Trace command: regenerate `polygon_mcp.gms`, grep `stat_theta`, and confirm which builder drops/mis-scales the offset-image cross-term; cite the `file:line`. Pairs with himmel16 #1146 (same offset-alias class) — a shared fix may land both.
