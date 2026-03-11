# pak: MCP Unmatched Equation — comp_conl(1962) Lead/Lag Domain Mismatch

**GitHub Issue:** [#1042](https://github.com/jeffreyhorn/nlp2mcp/issues/1042)
**Status:** Fixed (resolved by #1045 / PR #1047)
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-03-10
**Fixed:** 2026-03-11
**Affected Models:** pak

---

## Problem Summary

After applying `_fx_` equation suppression (which fixed the `c_fx_1962` and `ks_fx_1962_*` errors), the pak model still had one remaining MCP pairing error:

```
**** MCP pair comp_conl.lam_conl has unmatched equation
     comp_conl(1962)
```

---

## Root Cause

The inequality constraint `comp_conl` and its paired multiplier `lam_conl` had mismatched active domains due to a lead expression combined with a subset-restricted stationarity condition.

### Set Structure
- `te` = {1962, 1963, ..., 1985} (24 elements — full time horizon)
- `t(te)` = {1963, 1964, ..., 1985} (23 elements — optimization period, excludes initial year)

### The Mismatch (Before Fix)

`comp_conl('1962')` was active (ord('1962')=1 <= 23), but its paired multiplier `lam_conl('1962')` was not referenced in any stationarity equation because `stat_c(te)$(t(te))` only activated for `te` in `t` = {1963..1985}. GAMS eliminated `lam_conl('1962')` as an orphaned variable, making `comp_conl('1962')` unmatched.

---

## Resolution

This issue was **automatically resolved** by the lead/lag stationarity fix in PR #1047 (Issue #1045).

### What Changed

The #1045 fix added proper IndexOffset handling in the Jacobian/stationarity computation. For the pak model, the constraint:
```gams
conl(te+1).. c(te+1) =g= (1 + p)*c(te);
```

Now correctly produces a stationarity equation for `c` with a **shifted multiplier term**:
```gams
stat_c(te).. ... + (1 + p) * lam_conl(te) + ((-1) * lam_conl(te-1))$(ord(te) > 1) =E= 0;
```

The key change: `stat_c(te)` is now **unconditional** (no `$(t(te))` restriction) because the lead/lag derivative from `conl(te+1)` creates a `lam_conl(te-1)` term that makes the stationarity equation valid for all `te` indices, including `te=1962`. This means `lam_conl(1962)` is now referenced in `stat_c(1962)` and is no longer orphaned.

### GAMS Result After Fix

```
SOLVER STATUS     1 Normal Completion
MODEL STATUS      5 Locally Infeasible
```

No MCP pairing errors — the "unmatched equation" is gone. The model reaches the PATH solver. The "Locally Infeasible" status is a separate convergence issue (the KKT system may need further tuning).

---

## Verification

- No code changes required — issue resolved by PR #1047
- Regenerated pak_mcp.gms confirms no unmatched equation errors
- 4,125 tests pass, quality gate clean

---

## Related Issues

- #1045 — etamac MCP locally infeasible (lead/lag stationarity fix) — FIXED in PR #1047
- #984 — etamac domain errors — FIXED
- #1043 — etamac unmatched totalcap equations — FIXED
