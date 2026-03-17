# ps10_s_mn / ps5_s_mn: Loop-Initialized Parameters Not Captured ($141)

**GitHub Issue:** [#917](https://github.com/jeffreyhorn/nlp2mcp/issues/917)
**Models:** ps10_s_mn, ps5_s_mn (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $141 Symbol declared but no values assigned
**Status:** RESOLVED (Sprint 22 Day 12)

## Problem

The generated MCP files declare parameters (`Util_lic`, `Util_Lic2`, `MN_lic`) but never assign them values. These parameters are only initialized inside a `loop` statement in the original model, which the MCP transformation does not capture:

```gams
Parameters
    Util_lic(t)
    Util_Lic2(t)
    MN_lic(t)
;
```

GAMS error: `$141 Symbol declared but no values have been assigned`.

## Error Output

```
**** 141  Symbol declared but no values have been assigned. Check for missing
****         data definition, assignment, data loading or implicit assignment
****         via a solve statement.
```

6 compilation errors per model (12 total across both ps10_s_mn and ps5_s_mn).

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

The parameters `Util_lic`, `MN_lic`, etc. are populated iteratively through solve-loop results. The static KKT transformation extracts conditions for a single solve point and cannot capture this multi-solve iterative pattern. The parameters end up with no values (`ParameterDef.values = {}`) and no expressions (`ParameterDef.expressions = []`), but were still being declared in the Parameters block.

## Fix

**Commit:** `5456309c` (Sprint 22 Day 12)
**File:** `src/emit/original_symbols.py`

In `emit_original_parameters()`, added a check to skip emitting parameter declarations when the parameter has no values AND no expressions. These are loop-initialized reporting parameters that serve no purpose in the single-solve MCP and cause GAMS $141 errors:

```python
# Issue #917: Skip parameters with no values AND no expressions.
if not param_def.expressions:
    continue
```

Parameters that have expressions (computed assignments) are still declared, since the assignment will be emitted later.

**File:** `tests/unit/emit/test_original_symbols.py`

Updated `test_parameter_with_no_data` to reflect the new behavior and added `test_parameter_with_no_data_but_expressions_declared` to verify that parameters with expressions are still emitted.

## Verification

- ps10_s_mn and ps5_s_mn MCPs no longer declare `Util_lic`, `MN_lic`, `x_lic`, etc.
- Parameters with expressions (e.g., `noMHRC0`, `F`) are still correctly declared
- All 4,207 tests pass (+1 new test)
- No regressions

## Impact

2 models fixed (ps10_s_mn, ps5_s_mn: compilation error → compile cleanly).
Note: These models may still have path_syntax_error or mismatch issues due to the multi-solve pattern — the $141 compilation blocker is resolved but the models are fundamentally multi-solve.
