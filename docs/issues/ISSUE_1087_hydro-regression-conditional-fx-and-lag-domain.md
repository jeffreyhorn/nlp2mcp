# hydro: Regression — Conditional .fx Expansion + Lag-Domain Equation

**GitHub Issue:** [#1087](https://github.com/jeffreyhorn/nlp2mcp/issues/1087)
**Status:** OPEN
**Severity:** High — model_optimal regressed to model_infeasible
**Date:** 2026-03-14
**Affected Models:** hydro
**Regressing PRs:** #1076 (lag domain), parser (conditional .fx)

---

## Problem Summary

The hydro model (GAMSlib SEQ=167, "Hydrothermal Scheduling") regressed from model_optimal
to model_infeasible due to two bugs:

1. **PRIMARY:** `v.fx(tt)$(ord(tt) = 1) = 100e3` — the dollar condition is stripped,
   expanding the fix to ALL 7 elements instead of just element `'0'`
2. **SECONDARY:** `flow(tt-1)..` — the lag-domain equation is emitted as `flow(tt)..`
   without domain restriction (same pattern as catmix #1084 and pindyck #1088)

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/hydro.gms -o /tmp/hydro_mcp.gms
gams /tmp/hydro_mcp.gms lo=2
# **** SOLVER STATUS     1 Normal Completion
# **** MODEL STATUS      4 Infeasible
# 32 INFEASIBLE (INFES)
```

---

## Root Cause

### Bug 1: Conditional .fx Expanded to All Elements

**Original GAMS** (line 39):
```gams
v.fx(tt)$(ord(tt) = 1) = 100e3;
```
Fixes ONLY element `'0'` (where `ord(tt) = 1`) — the initial reservoir volume.

**Generated MCP** (lines 78-84):
```gams
v.fx('0') = 100000;
v.fx('1') = 100000;
v.fx('2') = 100000;
v.fx('3') = 100000;
v.fx('4') = 100000;
v.fx('5') = 100000;
v.fx('6') = 100000;
```

All 7 elements fixed to 100,000. With reservoir volume locked, the flow equations
(`v(tt) = v(tt-1) + (2000 - q(tt))*n`) become infeasible.

**Code location:** `src/ir/parser.py`, `_handle_conditional_assign_general` (line ~4507).
The method processes `v.fx(tt)$(ord(tt) = 1) = 100e3` by creating a `ConditionalStatement`
(informational only) then falling through to `_handle_assign` with a synthetic node that
has the dollar condition stripped. The effective assignment becomes `v.fx(tt) = 100e3`.

The subsequent `v.up(t) = 120e3` and `v.lo(t) = 60e3` apply only to subset `t = {1..6}`
and do NOT override `.fx` entries (GAMS `.fx` takes priority).

### Bug 2: flow(tt-1) Lag-Domain Not Restricted

**Original** (line 59):
```gams
flow(tt-1).. v(tt) =E= v(tt-1) + (2000 - q(tt))*n;
```
Generates equations for indices `{0,1,2,3,4,5}` (6 equations). Element `'0'` maps to
`tt='1'`: `v('1') = v('0') + ...`.

**Generated MCP** (line 206):
```gams
flow(tt).. v(tt) =E= v(tt-1) + (2000 - q(tt)) * n;
```
Generates for ALL `tt = {0..6}` — 7 equations. The spurious `flow('0')` equation uses
`v(-1) = 0`, creating `v(0) = 24000 - 12*q(0)` with `v(0)` fixed at 100,000 (infeasible).

Same root cause as catmix (#1084): `skip_lead_lag_inference=True` from PR #1076.

---

## Suggested Fix

### Bug 1: Respect dollar-conditions on .fx/.lo/.up assignments

In `_handle_conditional_assign_general` (line ~4507 of `src/ir/parser.py`), when the target
is a bound assignment (`bound_indexed` or `bound_scalar`), evaluate the dollar condition
against set members to filter which elements receive the bound.

**Approach:** Evaluate `$(ord(tt) = 1)` against `tt = {0,1,...,6}` to determine that only
`'0'` matches (ord = 1). Store `.fx = 100000` only for element `'0'`.

This requires an `ord()` evaluator, which is a common GAMS pattern for initial conditions.

### Bug 2: Handle lag-domain equations

See catmix (#1084) — shared pattern. Fix `skip_lead_lag_inference` to be conditional on
head-domain offset presence.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ir/parser.py:~4507` | Evaluate dollar-conditions on .fx/.lo/.up bound assignments |
| `src/emit/equations.py:469` | Make `skip_lead_lag_inference` conditional (shared with #1084) |
