# otpop: MCP Pair Unmatched Equations for Fixed Variable Subsets

**GitHub Issue:** [#915](https://github.com/jeffreyhorn/nlp2mcp/issues/915)
**Model:** otpop (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Execution — MCP pair unmatched equation
**Status:** FIXED
**Fixed:** 2026-03-10 (PR #1044 — `_fx_` equation suppression)

## Problem

The generated MCP file creates equations and multiplier variables for fixed variable instances (historical years 1965-1973), but these pairs are not included in the MCP model declaration. GAMS reports 19 "unmatched equation" errors at solve time:

```
**** MCP pair x_fx_1965.nu_x_fx_1965 has unmatched equation
**** MCP pair comp_lo_p.piL_p has unmatched equation
```

## Error Output

```
**** MCP pair x_fx_1965.nu_x_fx_1965 has unmatched equation
**** MCP pair x_fx_1966.nu_x_fx_1966 has unmatched equation
...
**** MCP pair x_fx_1973.nu_x_fx_1973 has unmatched equation
**** MCP pair comp_lo_p.piL_p has unmatched equation (for years 1965-1973)
```

19 execution errors. 0 compilation errors.

## Root Cause

The original otpop.gms fixes variables for historical years:

```gams
p.fx(th) = phis(th);    * fix p for historical years 1965-1973
x.fx(th) = x74;         * fix x for historical years 1965-1973
```

The KKT generator creates `x_fx` equations (fixed-value constraints) and `nu_x_fx` multipliers for these. However, the MCP model declaration only includes pairs for the non-historical years (1974+), leaving 9 equation-variable pairs unmatched.

Similarly, `comp_lo_p` (lower bound complementarity for `p`) is generated for all years but only paired for active years.

## Solution

PR #1044 implements `_fx_` equation suppression in the emitter:

1. `_compute_suppressed_fx_equations()` in `src/emit/emit_gams.py` detects `_fx_` equations whose target index falls outside the stationarity condition's active domain (e.g., `x_fx_1965` where `1965` is not in the optimization set `t`)
2. Suppressed equations are filtered from the MCP model statement, equation declarations, and equation definitions
3. Their multipliers are fixed to 0 via `.fx` assignments
4. The correct `.fx` values are re-emitted after the blanket fix-inactive lines

**Result:** All 9 `x_fx_*` unmatched errors eliminated. PATH solver now runs (model status: Locally Infeasible — a solve outcome, not a structural error).

## Files Changed

- `src/emit/emit_gams.py` — `_fx_eq_name()`, `_compute_suppressed_fx_equations()`, fix-inactive suppression logic
- `src/emit/model.py` — Filter suppressed equations from MCP model statement
- `src/emit/equations.py` — Filter suppressed equations from equation definitions
- `src/emit/templates.py` — Filter suppressed equations from equation declarations
- `src/kkt/kkt_system.py` — Added `suppressed_fx_equations` field
