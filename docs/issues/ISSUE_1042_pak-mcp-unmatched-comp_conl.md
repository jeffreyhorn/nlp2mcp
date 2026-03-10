# pak: MCP Unmatched Equation — comp_conl(1962) Lead/Lag Domain Mismatch

**GitHub Issue:** [#1042](https://github.com/jeffreyhorn/nlp2mcp/issues/1042)
**Status:** Open
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-03-10
**Affected Models:** pak

---

## Problem Summary

After applying `_fx_` equation suppression (which fixed the `c_fx_1962` and `ks_fx_1962_*` errors), the pak model still has one remaining MCP pairing error:

```
**** MCP pair comp_conl.lam_conl has unmatched equation
     comp_conl(1962)
```

---

## Root Cause

The inequality constraint `comp_conl` and its paired multiplier `lam_conl` have mismatched active domains due to a lead expression combined with a subset-restricted stationarity condition.

### Set Structure
- `te` = {1962, 1963, ..., 1985} (24 elements — full time horizon)
- `t(te)` = {1963, 1964, ..., 1985} (23 elements — optimization period, excludes initial year)

### Equation and Variable Domains

| Component | Domain | Active Indices |
|-----------|--------|---------------|
| `comp_conl(te)$(ord(te) <= card(te) - 1)` | te where ord <= 23 | 1962..1984 |
| `lam_conl(te)` (declared) | all te | 1962..1985 |
| `lam_conl.fx(te)$(not ...)` | te='1985' fixed to 0 | |
| `stat_c(te)$(t(te))` references `lam_conl(te)` | te in t | 1963..1985 |

### The Mismatch

`comp_conl('1962')` exists (ord('1962')=1 <= 23), and it is paired with `lam_conl('1962')` via the model statement `comp_conl.lam_conl`.

However, `lam_conl('1962')` does not appear in any active equation:
- `stat_c(te)$(t(te))` only exists for `te` in `t` = {1963..1985}
- `stat_c('1962')` does not exist (1962 not in `t`)
- So `lam_conl('1962')` has no coefficient in any equation

GAMS eliminates `lam_conl('1962')` as an orphaned variable, making `comp_conl('1962')` unmatched.

### Original Model Context

From `pak.gms`, the constraint is:
```gams
conl(te+1)..  c(te+1) =g= (1 + p)*c(te);
```

The original uses `te+1` in the equation head, meaning the equation exists for `te+1 = 1963..1985`, i.e., `te = 1962..1984`. The MCP emitter translates this as `comp_conl(te)$(ord(te) <= card(te) - 1)` to handle the lead restriction.

The stationarity for `c` is conditioned on `t(te)` = {1963..1985} because `c.fx('1962') = 33.999` fixes the initial value. The stationarity includes `lam_conl(te)` but only activates for `te` in `t`.

Result: `comp_conl('1962')` has a paired multiplier that GAMS eliminates.

---

## How to Reproduce

```bash
python -m src.cli data/gamslib/raw/pak.gms -o data/gamslib/mcp/pak_mcp.gms
gams pak_mcp.gms
# Check pak_mcp.lst for: "MCP pair comp_conl.lam_conl has unmatched equation"
```

---

## Suggested Fix

**Option A (Preferred): Fix `lam_conl('1962')` to 0 in the fix-inactive section**

The emitter already knows about the lead/lag restriction on `comp_conl`. It should also detect that `lam_conl('1962')` is orphaned (not referenced in any active stationarity equation) and fix it to 0. Then `comp_conl('1962')` should also be excluded from the model or its domain should be narrowed.

More precisely: when `comp_conl(te)$(cond)` has a different active domain than `stat_c(te)$(t(te))`, the indices in `comp_conl`'s domain but NOT in `stat_c`'s domain create orphaned multiplier instances. These should be detected and either:
1. The `comp_conl` equation should be further conditioned to exclude those indices, OR
2. The orphaned `lam_conl` instances should be fixed to 0 AND removed from the MCP model pairing

**Option B: Intersect inequality complement domain with stationarity domain**

When building the fix-inactive lines for inequality multipliers, intersect the inequality's condition with the stationarity condition of the primal variable it's paired with. This ensures `lam_conl.fx('1962') = 0` is emitted alongside the existing `lam_conl.fx('1985') = 0`.

---

## Files Involved

- `src/emit/emit_gams.py` — Fix-inactive section (inequality multiplier domain logic)
- `src/kkt/complementarity.py` — Builds inequality complementarity pairs
- `data/gamslib/mcp/pak_mcp.gms` — Generated MCP file
- `data/gamslib/raw/pak.gms` — Original model
