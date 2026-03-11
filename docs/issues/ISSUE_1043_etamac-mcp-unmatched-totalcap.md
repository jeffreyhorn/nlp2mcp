# etamac: MCP Unmatched Equation — totalcap(t) Stationarity Domain Eliminates Primal Variable

**GitHub Issue:** [#1043](https://github.com/jeffreyhorn/nlp2mcp/issues/1043)
**Status:** Open
**Severity:** Medium — Model translates but PATH solver aborts (path_solve_terminated)
**Date:** 2026-03-10
**Affected Models:** etamac

---

## Problem Summary

The etamac model (energy-technology-aggregate-climate) has 8 MCP pairing errors after the domain-error fix (#984):

```
**** MCP pair totalcap.nu_totalcap has unmatched equation
     totalcap(1990)
     totalcap(1995)
     totalcap(2000)
     totalcap(2005)
     totalcap(2010)
     totalcap(2015)
     totalcap(2020)
     totalcap(2025)
```

---

## Root Cause

The equality constraint `totalcap` references primal variable `k(t)`, but `k` has a narrow stationarity condition that causes most instances to be fixed to 0, eliminating them from the equation.

### Set Structure
- `t` = {1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025, 2030} (9 elements)
- `tfirst(t)` = {1990} (first period)
- `tlast(t)` = {2030} (terminal period)

### The Chain of Events

1. **Stationarity condition for `k`:**
   ```gams
   stat_k(t)$(tlast(t)).. ... =E= 0;
   ```
   `k` has stationarity only at `tlast` = {2030}.

2. **Fix-inactive for `k`:**
   ```gams
   k.fx(t)$(not (tlast(t))) = 0;
   ```
   This fixes `k('1990')` through `k('2025')` to 0. Only `k('2030')` remains free.

3. **The totalcap equation:**
   ```gams
   totalcap(t)$(ord(t) <= card(t) - 1).. k(t+1) =E= k(t) * spda ** nyper + kn(t+1);
   ```
   Active for t = 1990..2025 (8 periods).

4. **Variable elimination:** For `totalcap('1990')`:
   - `k('1995')` (= k(t+1)) is fixed to 0 (eliminated by GAMS)
   - `k('1990')` (= k(t)) is fixed to 0 (eliminated by GAMS)
   - `kn('1995')` (= kn(t+1)) — `kn` may also be fixed

   GAMS eliminates all fixed variables from the equation. If no free variables remain, the equation is "unmatched" — it can't be paired with `nu_totalcap`.

5. Similarly for all other active periods: `k(t)` and `k(t+1)` are fixed for t=1990..2025 (since only k('2030') is free). The only equation where `k(t+1)` could be free is `totalcap('2025')` where `k(t+1) = k('2030')` — but `k('2025')` (= k(t)) is still fixed, plus `kn('2030')` may also be fixed.

### Why This Happens

The original model `etamac.gms` has `k` as a variable over all time periods, with the capital accumulation constraint `totalcap` linking consecutive periods. The stationarity of `k` with respect to the objective function only applies at the terminal period (`tlast`) because earlier periods' capital is determined by the accumulation equation itself.

When the emitter restricts `stat_k` to `tlast` only, it correctly identifies that `k` is only "free" (from an optimality perspective) at the terminal period. But the fix-inactive logic then aggressively fixes all non-terminal `k` values to 0, which conflicts with the `totalcap` equality constraint that needs `k` to be free across all periods.

The root issue: **fixing a primal variable to 0 because it has narrow stationarity is incorrect when that variable appears in other equality constraints for broader domains.**

---

## How to Reproduce

```bash
python -m src.cli data/gamslib/raw/etamac.gms -o data/gamslib/mcp/etamac_mcp.gms
gams etamac_mcp.gms
# Check etamac_mcp.lst for: "MCP pair totalcap.nu_totalcap has unmatched equation"
```

---

## Suggested Fix

**Option A (Preferred): Don't fix primal variables that appear in other active equations**

Before emitting `k.fx(t)$(not (tlast(t))) = 0;`, check whether `k(t)` appears in any equality or inequality constraint outside the stationarity condition. If `k` appears in `totalcap(t)` for a broader domain than just `tlast`, the fix-inactive should NOT eliminate those instances.

Implementation: in `emit_gams.py`, before generating fix-inactive lines for stationarity-conditioned variables, scan the model's equations for references to that variable with a broader domain. If found, skip the fix-inactive or narrow it to only indices not used in any equation.

**Option B: Broaden the stationarity domain to match constraint domains**

Ensure that if a variable `k` appears in equality constraints for domain D, then `stat_k` is generated for at least domain D. This would require the KKT builder to union the stationarity domain with all constraint domains that reference the variable.

**Option C: Remove the totalcap equality from the MCP model for fixed periods**

If `k(t)` is fixed for periods 1990-2025, then `totalcap(t)` for those periods becomes a trivially satisfied equation (all variables fixed). Suppress those equation instances from the MCP model, similar to the `_fx_` suppression approach.

---

## Related Issues

- #984 — etamac domain errors (division by zero, log(0)) — PARTIALLY FIXED
  - #984's remaining issue section mentions these 8 MCP matching errors

---

## Files Involved

- `src/emit/emit_gams.py` — Fix-inactive section (primal variable fixing logic, ~line 1195)
- `src/kkt/stationarity.py` — Determines stationarity conditions
- `data/gamslib/mcp/etamac_mcp.gms` — Generated MCP file
- `data/gamslib/raw/etamac.gms` — Original model
