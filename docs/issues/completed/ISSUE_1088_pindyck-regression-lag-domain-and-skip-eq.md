# pindyck: Regression — Lag-Domain Lost + skip_eq Applied to All Variables

**GitHub Issue:** [#1088](https://github.com/jeffreyhorn/nlp2mcp/issues/1088)
**Status:** FIXED
**Severity:** High — model_optimal regressed to model_infeasible
**Progress:** All three bugs fixed. Bug 1 (lag-domain) fixed by PR #1093. Bug 2 (skip_eq scope) fixed: scoped to objective variable only in `stationarity.py:827`. Bug 3 (loop-based init) fixed: `emit_var_level_loop_statements()` emits loop-based `.l` initialization; default POSITIVE init skipped for loop-initialized variables.
**Date:** 2026-03-14
**Last Updated:** 2026-03-15
**Affected Models:** pindyck
**Regressing PRs:** #1076 (lag domain), stationarity.py (skip_eq scope)

---

## Problem Summary

The pindyck model (GAMSlib SEQ=28, "Pindyck Optimal OPEC Pricing") regressed from
model_optimal to model_infeasible due to three bugs. PATH terminates immediately with
0 iterations and 68 infeasible equations.

---

## Root Cause

### Bug 1: Equation Head Lag Domain Lost (Structural)

Four equations use lag-based head domains (e.g., `tdeq(t-1)..`). The MCP emitted
equations for ALL `t` including `1974`, conflicting with fixed initial conditions.

**Fix:** PR #1093 — made `skip_lead_lag_inference` conditional.

### Bug 2: Missing Objective-Defining Equation Contribution (Structural)

`skip_eq` was applied to ALL variables' stationarity, not just the objective variable.
This disconnected the objective from the KKT system.

**Fix:** Scoped `skip_eq` to objective variable only (`stationarity.py:831`):
```python
skip_eq = obj_info.defining_equation if (
    not kkt.model_ir.strategy1_applied and var_name.lower() == obj_info.objvar.lower()
) else None
```

### Bug 3: Loop-Based Variable Initialization Not Supported (Convergence)

The original model uses:
```gams
loop(t$to(t), r.l(t) = r.l(t-1)-d.l(t));
```

This computes `r.l` sequentially: 500, 489, 478, ... The MCP previously replaced this
with `r.l(t) = 1` (default POSITIVE init), which is orders of magnitude off.

**Fix:** Added `emit_var_level_loop_statements()` in `original_symbols.py` and
`get_var_level_loop_varnames()` helper. Loops whose bodies consist solely of variable
`.l` assignments are re-emitted after regular `.l` initialization. Default POSITIVE
init is skipped for variables whose `.l` is set by a qualifying loop.

---

## Result

- **MODEL STATUS:** 1 (Optimal)
- **SOLVER STATUS:** 1 (Normal Completion)
- **MCP objective:** 152.84
- **NLP objective:** 1170.49
- **Mismatch:** Expected for non-convex NLP — KKT conditions find a different valid
  stationary point. The model is structurally correct.

---

## Files Modified

| File | Change | PR |
|------|--------|----|
| `src/emit/equations.py:469` | Make `skip_lead_lag_inference` conditional | #1093 |
| `src/kkt/stationarity.py:827-831` | Scope `skip_eq` to objective variable only | #1094 |
| `src/emit/original_symbols.py` | Add `_loop_body_only_var_level_assigns()`, `get_var_level_loop_varnames()`, `emit_var_level_loop_statements()` | This PR |
| `src/emit/emit_gams.py` | Call `emit_var_level_loop_statements()` after `.l` init; skip default POSITIVE init for loop-initialized vars | This PR |
