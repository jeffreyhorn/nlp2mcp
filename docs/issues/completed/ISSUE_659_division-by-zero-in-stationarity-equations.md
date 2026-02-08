# Issue: Division by Zero in Stationarity Equations

**Status**: FIXED
**GitHub Issue**: #659 (https://github.com/jeffreyhorn/nlp2mcp/issues/659)
**Models**: `chem.gms`, `dispatch.gms`, `jobt.gms`, `like.gms`
**Component**: KKT Stationarity / Variable Initialization
**Fixed In**: Commit 4e97c4a (Sprint 18 Day 3, P5 fix)

## Summary

Multiple models failed during GAMS model generation with "division by zero" errors. This occurred when variables appeared in denominators of stationarity equations but had zero initial values.

## Resolution

**Fixed by P5 (commit 4e97c4a)**: Added variable initialization section in `src/emit/emit_gams.py` that:

1. Initializes variables with lower bounds to their lower bound values: `var.l = var.lo`
2. Initializes positive variables to ensure a minimum value of 1 using `max()`: `var.l = max(var.l, 1)`
3. Emits initialization statements before equation definitions

**Note**: The implementation uses 1.0 (not 1e-6) to avoid numerical issues in stationarity equations.
Values that are too small can cause scaling problems in the solver.

### Implementation

The fix adds the following logic to `emit_gams_mcp()`:

```python
# Sprint 18 Day 3 (P5 fix): Variable initialization to avoid division by zero
# Variables with level values, lower bounds, or positive type need initialization
# to prevent division by zero during model generation when they appear in
# denominators of stationarity equations (e.g., from differentiating log(x) or 1/x)
init_lines: list[str] = []
for var_name, var_def in kkt.model_ir.variables.items():
    # ... initialization logic based on bounds and variable type
```

### Verification

All affected models now compile without division by zero errors:

```bash
# chem.gms - NO division by zero errors
# dispatch.gms - NO division by zero errors
# jobt.gms - Stationarity division by zero fixed (scalar issue separate)
# like.gms - Division by zero fixed (domain restriction issue separate)
```

## Original Problem Description

When differentiating expressions like `log(x/xb)` or `1/alpha`, the stationarity equations contain terms with variables in denominators. If these variables have zero initial values (the GAMS default), model generation fails.

### Example (chem model)

**Original equation:**
```gams
edef.. energy =e= sum(c, x(c)*(gplus(c) + log(x(c)/xb)));
```

**Generated stationarity equation:**
```gams
stat_x(c).. gplus(c) + log(x(c) / xb) + x(c) * 1 / (x(c) / xb) * 1 / xb ** 1 + ... =E= 0;
stat_xb.. sum(c, x(c) * 1 / (x(c) / xb) * ((-1) * x(c)) / xb ** 2) + ... =E= 0;
```

**Error (before fix):**
```
*** Error at line 39: division by zero (0)
*** Error at line 40: division by zero (0)
```

**After P5 fix:**
Variables are initialized before equations:
```gams
* Initialize variables to avoid division by zero during model generation.
x.l(c) = x.lo(c);
xb.l = xb.lo;
```

## Related Issues

- `ISSUE_655_jobt-division-by-zero-and-missing-restrictions.md` - jobt also has scalar initialization issues (separate from P5 fix)
- `ISSUE_651_pak-division-by-zero-and-quoted-lags.md` - pak has scalar/parameter initialization issues (separate from P5 fix)
- `ISSUE_653_like-missing-domain-restriction.md` - like's division by zero fixed, but has separate domain restriction issue

## Affected Files

- `src/emit/emit_gams.py` - Added variable initialization section (P5 fix)
