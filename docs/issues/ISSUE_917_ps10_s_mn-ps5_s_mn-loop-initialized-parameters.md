# ps10_s_mn / ps5_s_mn: Loop-Initialized Parameters Not Captured ($141)

**GitHub Issue:** [#917](https://github.com/jeffreyhorn/nlp2mcp/issues/917)
**Models:** ps10_s_mn, ps5_s_mn (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $141 Symbol declared but no values assigned

## Problem

The generated MCP files declare parameters (`Util_lic`, `Util_Lic2`, `MN_lic`, `pt`) but never assign them values. These parameters are only initialized inside a `loop` statement in the original model, which the MCP transformation does not capture:

```gams
Parameters
    Util_lic(t)
    Util_Lic2(t)
    MN_lic(t)
    pt(i,t)
;

Util_gap(t) = 1$(round(Util_lic(t), 10) <> round(Util_Lic2(t), 10));
```

GAMS error: `$141 Symbol declared but no values have been assigned`.

## Error Output

```
**** 141  Symbol declared but no values have been assigned. Check for missing
****         data definition, assignment, data loading or implicit assignment
****         via a solve statement.
```

6 compilation errors per model (same errors in both ps10_s_mn and ps5_s_mn).

## Root Cause

The original models initialize these parameters inside a loop that iterates over time periods and solves the model at each step:

```gams
loop(t,
   p(i) = pt(i,t);
   solve SB_lic maximizing Util using nlp;
   Util_lic(t) = Util.l;
   MN_lic(t) = SB_lic.modelstat;
   ...
);
```

The parameters `Util_lic`, `MN_lic`, `pt`, etc. are populated iteratively through solve-loop results. The static KKT transformation cannot capture this multi-solve iterative pattern — it extracts KKT conditions for a single solve point.

## Original GAMS Pattern

```gams
* ps10_s_mn.gms (abbreviated)
loop(t,
   p(i) = pt(i,t);
   solve SB_lic maximizing Util using nlp;
   Util_lic(t) = Util.l;
   Util_Lic2(t) = Util2.l;
   MN_lic(t) = SB_lic.modelstat;
);
```

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/ps10_s_mn.gms -o /tmp/ps10_s_mn_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ps10_s_mn_mcp.gms o=/tmp/ps10_s_mn_mcp.lst
grep '141' /tmp/ps10_s_mn_mcp.lst
```

## Suggested Fix

These models use a **multi-solve loop pattern** that is fundamentally incompatible with single-point KKT extraction:

1. **Flag as unsupported pattern** — detect loop-solve patterns and warn that the model requires iterative solving
2. **Extract single-iteration KKT** — transform only the inner NLP model for one iteration, initializing loop parameters with dummy values
3. **Emit loop-initialized parameters with default values** — assign zero or NA to prevent $141, though results would be meaningless without the solve loop

## Impact

6 compilation errors per model (12 total across both). Models cannot compile. The iterative solve-loop pattern is a fundamental limitation of static KKT transformation.
