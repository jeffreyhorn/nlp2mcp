# Parameter-Assigned Bounds (lo_expr_map) Invisible to KKT Pipeline

**GitHub Issue:** #923 (https://github.com/jeffreyhorn/nlp2mcp/issues/923)
**Models:** sparta, aircraft (and any model with parameter-expression bounds)
**Category:** match_mismatch (LP models solve but don't match NLP objective)
**Severity:** KKT system incomplete — missing bound multipliers for expression-based bounds
**Sprint:** 21, Day 9
**Status:** RESOLVED

## Problem

When a variable bound is assigned via a parameter expression (e.g., `e.lo(t) = req(t)`), the parser stores the RHS in `var_def.lo_expr_map` because `req(t)` cannot be reduced to a constant. However, the KKT partitioner (`partition_constraints()`) only reads `var_def.lo` and `var_def.lo_map` (numeric storage), ignoring `lo_expr_map` entirely.

The result: no bound multiplier variable (`piL_e(t)`), no complementarity equation (`comp_lo_e(t)`), and no `piL_e(t)` term in the stationarity equation. The KKT system is incomplete.

## Root Cause

The partitioner only processed numeric bound fields (`lo`/`lo_map`/`up`/`up_map`/`fx`/`fx_map`) and ignored expression-based fields (`lo_expr`/`lo_expr_map`/`up_expr`/`up_expr_map`/`fx_expr`/`fx_expr_map`). The complementarity builder only used `Const(bound_def.value)` for bound values, with no mechanism for expression-based bounds.

## Fix

Two changes across 2 files:

1. **`src/kkt/partition.py`**: Extended `BoundDef` with an optional `expr: Expr | None` field. Added processing of `lo_expr`/`lo_expr_map` and `up_expr`/`up_expr_map` in `partition_constraints()` — creates `BoundDef` entries with the expression stored in the `expr` field for **lower** and **upper** expression-based bounds. Expression-based fixed bounds (`fx_expr`/`fx_expr_map`) are intentionally **not** wired into the KKT partition at this time.

2. **`src/kkt/complementarity.py`**: Added `_bound_expr()` helper that returns `bound_def.expr` when set, otherwise `Const(bound_def.value)`. Replaced all `Const(bound_def.value)` in uniform bound complementarity equation construction with `_bound_expr(bound_def)`, so expression-based lower/upper bounds participate correctly in the KKT equations.

No changes needed in `assemble.py` — the multiplier creation logic only checks for bound existence (not values), so it works correctly with expression-based lower/upper bounds handled by the partitioner.

### Limitations

Expression-based fixed bounds (`fx_expr`/`fx_expr_map`) remain **unsupported** in the KKT pipeline. They are not partitioned into `BoundDef` entries and therefore do not generate multipliers, complementarity equations, or stationarity terms.

## Verification

After fix:
- **sparta**: `piL_e(t)` multiplier created, `comp_lo_e(t).. e(t) - req(t) =G= 0` emitted, `stat_e(t)` includes `-piL_e(t)` term. Compiles cleanly, SOLVER STATUS 1, MODEL STATUS 1.
- **aircraft**: `piU_y(j,h)` multiplier created, `comp_up_y(j,h).. deltb(j,h) - y(j,h) =G= 0` emitted. Compiles cleanly, SOLVER STATUS 1, MODEL STATUS 1.
- Both models still have objective mismatches with their NLP counterparts, suggesting additional issues beyond expression-based bounds (separate investigation needed).
- All tests pass.
