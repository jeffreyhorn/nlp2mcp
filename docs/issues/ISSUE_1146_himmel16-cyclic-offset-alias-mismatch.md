# himmel16: Cyclic Offset Alias Gradient Mismatch

**GitHub Issue:** [#1146](https://github.com/jeffreyhorn/nlp2mcp/issues/1146)
**Status:** OPEN
**Severity:** High — objective mismatch (43.0%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** himmel16

---

## Problem Summary

The himmel16 model (Himmelblau Problem 16) uses `Alias(i, j)` with cyclic
offset patterns where aliased indices wrap around the set boundary. The
large mismatch (43.0%) indicates significant gradient errors.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| himmel16 | 0.675 | 0.385 | 43.0% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/himmel16.gms -o /tmp/himmel16_mcp.gms
gams /tmp/himmel16_mcp.gms lo=2
# Objective: ~0.385, expected: ~0.675
```

---

## Root Cause Analysis

The himmel16 model uses:

```gams
Alias(i, j);
```

With cyclic offset patterns where variables at position `i` interact with
variables at position `i+1` (or `j` where `j` is the successor of `i`).
The cyclic (modular) wrapping at the boundary of the set creates additional
complexity.

### Potential Issues

1. **Cyclic IndexOffset handling**: The `circular=True` flag on IndexOffset
   nodes requires special handling in `_partial_collapse_sum` to correctly
   identify which element wraps around.

2. **Alias + offset combination**: When the alias `j` is combined with an
   offset like `i+1`, the AD engine must resolve both the alias relationship
   and the offset, which may not compose correctly.

3. **Index substitution for cyclic references**: After sum collapse, the
   `_apply_index_substitution` may not correctly handle the modular arithmetic
   needed for cyclic offsets.

### Investigation Steps

1. Generate the MCP and inspect stationarity equations
2. Identify the specific cyclic offset pattern in the equations
3. Check if `IndexOffset` with `circular=True` is correctly handled
4. Compare with hand-derived KKT conditions
5. Test if the polygon fix (if implemented) also helps himmel16

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/himmel16.gms` — Source model

## Current Status (2026-03-30)

Translates and solves to Optimal but objective does not match the NLP reference. Same alias differentiation root cause as qabel/abel (#1137), complicated by cyclic offsets.

## Phase 0: Acceptance Gate

> **Day-0 status (Sprint 29 Prep Task 3/4, 2026-06-25):** the 43% cold mismatch above is **stale (2026-03-30)**. On the current Day-0 DB himmel16 **matches warm** (`model_optimal_presolve`, 0.675 ≈ 0.675) and the harness verdict is **Case b**, `max_residual_row = stat_area`, rel = **2.000**, dual-transfer consistent → **PROCEED**. The fix is **cold-robustness** (himmel16 already matches warm), not headline +Match — Class A in `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md`. Also a Case-b validation target for the parent offset-alias-AD architecture (#1111/#1112).

### Hand-Derived KKT Shape

himmel16 maximizes `totarea` with `obj2..  totarea =e= sum(i, area(i))` and the cyclic-offset defining constraint
`areadef(i)..  area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1))` (`i++1` = circular successor).

The intermediate-variable `area(i)` appears in exactly two equations — the defining `areadef(i)` (coefficient `+1`) and the objective sum `obj2` (coefficient `+1`):

```
stat_area(i)..  nu_areadef(i) - nu_obj2  =E= 0
```

(The cyclic `i++1` offset enters the **`x`/`y`** stationarity rows via the `areadef` Jacobian-transpose with a wrapped index, `nu_areadef(i--1)` aliased back — that is where the offset-alias AD must compose `circular=True` with the alias. A `stat_area` residual of exactly **2.000** is the fingerprint of a missing/sign-flipped unit-coefficient cross-term in the intermediate-var row.)

### Expected Emit Pattern

`himmel16_mcp.gms` `stat_area(i)` should contain both unit-coefficient multiplier terms (`nu_areadef(i)` and `-nu_obj2`), and the `stat_x`/`stat_y` rows should carry the **wrapped** `areadef` cross-terms at `i++1`/`i--1` (cyclic). (Hypothesis — the actual builder `file:line` to be confirmed by the Day-0 trace.)

### Verification Methodology

```bash
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/himmel16.gms --json /tmp/phase0_himmel16.json
```

- **PROCEED (Case b):** `max_residual_row = stat_area`, rel ≈ 2.0. ✅ confirmed Day-0.
- **REPLAN (Case c):** clean residual but cold PATH diverges → non-convexity → Sprint 30. (Not the case here.)
- Post-fix: residual → 0 (Case a) and `compare_objective_match` on the **cold** solve; **add a property-test fixture** for the cyclic-offset-alias shape (parent #1111/#1112).

### PROCEED/REPLAN Signal

- **PROCEED** — Day-0 Case b on `stat_area`, rel ≈ 2.0 (✅ confirmed).
- **Traced Fix-Surface (Day-0):** **to be confirmed by the Day-0 trace** — the cyclic-offset-alias composition in `src/ad/derivative_rules.py` (`_partial_collapse_sum`, `_diff_varref` with `circular=True`) and the index-substitution in `src/kkt/stationarity.py` (`_replace_indices_in_expr`). Trace command: regenerate `himmel16_mcp.gms`, grep `stat_area`/`stat_x`/`stat_y`, and confirm which builder drops/mis-wraps the `areadef` cross-term; cite the `file:line`. Pairs with polygon #1143 (same offset-alias class) — a shared fix may land both.
