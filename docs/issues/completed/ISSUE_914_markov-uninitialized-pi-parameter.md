# markov: Uninitialized Parameter `pi` ($66)

**GitHub Issue:** [#914](https://github.com/jeffreyhorn/nlp2mcp/issues/914)
**Model:** markov (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $66 Symbol has no values assigned, $256 Solve error
**Status:** RESOLVED (Sprint 22 Day 12)

## Problem

The generated MCP file declares parameter `pi(s,i,sp,j,spp)` but never assigns it values. The stationarity equation `stat_z` references `pi`, causing GAMS error $66:

```
**** 66  Use of a symbol that has not been defined or assigned
****  66 equation stat_z.. symbol "pi" has no values assigned
```

## Error Output

```
**** 66  Use of a symbol that has not been defined or assigned
**** 256  Error(s) in analyzing solve statement
```

2 compilation errors.

## Root Cause

In the original markov.gms, `pi` is a **computed parameter** assigned via:

```gams
pi(s,i,sp,j,sp) = pr(i,j);
```

The computed assignment was correctly stored in the IR (`ParameterDef.expressions`), but the emitter's `emit_computed_parameter_assignments()` function skipped it because `"pi"` is in `PREDEFINED_GAMS_CONSTANTS = {"pi", "inf", "eps", "na"}`. The check `if param_name in PREDEFINED_GAMS_CONSTANTS: continue` did not distinguish between the built-in scalar constant `pi` (3.14159...) and a user-declared indexed parameter named `pi(s,i,sp,j,spp)`.

## Fix

**Commit:** `5456309c` (Sprint 22 Day 12)
**File:** `src/emit/original_symbols.py`

Changed all `PREDEFINED_GAMS_CONSTANTS` skip checks to also verify that the parameter has no domain. An indexed parameter (with a non-empty domain tuple) clearly cannot be the built-in scalar constant. The fix was applied at 4 locations in `emit_computed_parameter_assignments()` and `emit_interleaved_params_and_sets()`:

```python
# Before:
if param_name in PREDEFINED_GAMS_CONSTANTS:
    continue

# After:
if param_name in PREDEFINED_GAMS_CONSTANTS and not param_def.domain:
    continue
```

## Verification

- markov MCP now emits `pi(s,i,sp,j,sp) = pr(i,j);` at line 48
- All 4,207 tests pass
- No regressions

## Impact

1 model fixed (markov: compilation error → compiles cleanly).
