# pindyck: Regression — Lag-Domain Lost + skip_eq Applied to All Variables

**GitHub Issue:** [#1088](https://github.com/jeffreyhorn/nlp2mcp/issues/1088)
**Status:** OPEN
**Severity:** High — model_optimal regressed to model_infeasible
**Date:** 2026-03-14
**Affected Models:** pindyck
**Regressing PRs:** #1076 (lag domain), stationarity.py (skip_eq scope)

---

## Problem Summary

The pindyck model (GAMSlib SEQ=28, "Pindyck Optimal OPEC Pricing") regressed from
model_optimal to model_infeasible due to three bugs. PATH terminates immediately with
0 iterations and 68 infeasible equations.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/pindyck.gms -o /tmp/pindyck_mcp.gms
gams /tmp/pindyck_mcp.gms lo=2
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
# 68 INFEASIBLE (INFES), ITERATION COUNT 0
```

---

## Root Cause

### Bug 1: Equation Head Lag Domain Lost (Structural)

Four equations use lag-based head domains:
```gams
tdeq(t-1)..   td(t)  =e= 0.87*td(t-1) - 0.13*p(t) + demand(t);
seq(t-1)..    s(t)   =e= 0.75*s(t-1) + ...;
cseq(t-1)..   cs(t)  =e= cs(t-1) + s(t);
req(t-1)..    r(t)   =e= r(t-1) - d(t);
```

In GAMS, `tdeq(t-1)` generates equations only for `t = 1975,...,1990` (where `t-1` exists).
The MCP emits `tdeq(t)..` for ALL `t` including `1974`. The spurious equations at `t=1974`
conflict with fixed initial conditions.

**Code location:** `src/emit/equations.py:469` — `skip_lead_lag_inference=True` from PR #1076.

Same root cause as catmix (#1084) and hydro (#1087).

### Bug 2: Missing Objective-Defining Equation Contribution (Structural)

**Code location:** `src/kkt/stationarity.py:827`
```python
skip_eq = obj_info.defining_equation if not kkt.model_ir.strategy1_applied else None
```

This `skip_eq` (set to `'tprofit'`) is applied to ALL variables' stationarity, not just
the objective variable `profit`. The `tprofit` equation:
```gams
tprofit.. profit =e= sum(to, rev(to)*1.05**(1-ord(to)));
```

...contributes to the stationarity of `rev(to)` (coefficient = `1.05^(1-ord(to))`). But
since `tprofit` is skipped, the emitted stationarity is:
```gams
stat_rev(t)$(to(t)).. nu_drev(t) =E= 0;
```

This forces `nu_drev(to) = 0` for all `to`, disconnecting the objective from the KKT
system. The correct stationarity should be:
```gams
stat_rev(to).. nu_drev(to) - 1.05**(1-ord(to)) * nu_tprofit =E= 0;
```

### Bug 3: Loop-Based Variable Initialization Not Supported (Convergence)

The original model uses:
```gams
loop(t$to(t), r.l(t) = r.l(t-1)-d.l(t));
```

This computes `r.l` sequentially: 500, 489, 478, ... The MCP replaces this with `r.l(t) = 1`,
which is orders of magnitude off. Since `drev` involves `250/r(to)`, the linearization at
`r=1` produces enormous infeasibilities.

---

## Suggested Fix

### Bug 1: Handle lag-domain equations
See catmix (#1084) — shared pattern.

### Bug 2: Scope skip_eq to objective variable only

Change the stationarity builder to only skip `tprofit` for the objective variable `profit`:
```python
skip_eq = obj_info.defining_equation if (
    not kkt.model_ir.strategy1_applied and var_name == obj_info.objvar
) else None
```

Alternative: substitute `nu_tprofit = 1` (for max) / `-1` (for min) directly into
stationarity equations, since the objective equation's multiplier is fixed at ±1 by KKT.

### Bug 3: Support loop-based initialization
Broader infrastructure issue. Short-term: detect common patterns like
`loop(t$cond, x.l(t) = x.l(t-1) - y.l(t))` and emit sequential assignments.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/emit/equations.py:469` | Make `skip_lead_lag_inference` conditional (shared with #1084) |
| `src/kkt/stationarity.py:827` | Scope `skip_eq` to objective variable only |
| `src/ir/parser.py` | (Bug 3) Support loop-based .l initialization |
