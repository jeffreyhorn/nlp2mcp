# otpop: MCP Pair Unmatched Equations for Fixed Variable Subsets

**GitHub Issue:** [#915](https://github.com/jeffreyhorn/nlp2mcp/issues/915)
**Model:** otpop (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Execution — MCP pair unmatched equation

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

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms -o /tmp/otpop_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/otpop_mcp.gms o=/tmp/otpop_mcp.lst
grep 'MCP pair' /tmp/otpop_mcp.lst | head -10
```

## Suggested Fix

When variables are fixed for a subset of indices (`.fx` with domain condition), the KKT generator should either:
1. **Include all pairs in the MCP declaration** — generate the x_fx equations AND include them in the model block
2. **Skip equation generation for fixed indices** — don't create x_fx equations for indices where the variable is already fixed (redundant constraint)
3. **Fix the MCP model declaration** to include the missing pairs

## Impact

19 execution errors. Model compiles cleanly but cannot solve.
