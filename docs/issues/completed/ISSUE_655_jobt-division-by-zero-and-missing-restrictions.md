# Issue: jobt Translation Bugs - Division by Zero and Missing Domain Restrictions

**Status**: FIXED (Sprint 18)
**GitHub Issue**: #655 (https://github.com/jeffreyhorn/nlp2mcp/issues/655)
**Model**: `jobt.gms`
**Component**: Grammar / Scalar Parsing / Equation Domain Generation

## Fix Summary

| Bug | Status | Fixed In |
|-----|--------|----------|
| Division by zero in stationarity (variables) | FIXED | Commit 4e97c4a (P5 fix) |
| Division by zero from scalars (alpha, rho) | FIXED | Issue #651 scalar parsing fix |
| Missing domain restrictions for lag index | NOT A BUG | Already correctly implemented |

## Original Problem

### Bug 1: Division by Zero from Scalars

The `jobt` model uses scalars `alpha` and `rho` as divisors:
```gams
wd(t).. w(t) =g= p(t)/rho + (1 + 1/alpha)*h(t);
```

The MCP output initially showed `alpha = 0.0` and `rho = 0.0`, causing division by zero.

### Root Cause

Same as Issue #651 - the `scalar_item` grammar rule used `ID` which caused ambiguity in multi-line scalar declarations with descriptions:
```gams
Scalar
   rho   'worker productivity   (units per worker)' /   8 /
   alpha 'trainer capability (workers per trainer)' /   6 /
```

### Fix

The grammar fix in Issue #651 (using `SYMBOL_NAME` instead of `ID` in `scalar_item`) also fixed this model. Scalars now parse correctly:
- `alpha = 6.0` (was 0.0)
- `rho = 8.0` (was 0.0)

### Bug 2: Missing Domain Restrictions

The issue reported that recurrence equations like:
```gams
cb(t).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);
```

Were missing domain restrictions `$(ord(t) > 1)` for lag references.

**Finding**: This was already correctly implemented. The generated MCP file shows:
```gams
cb(t)$(ord(t) > 1).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);
wb(t)$(ord(t) > 1).. w(t) =E= w(t-1) - f(t) + h(t) + wi(t);
```

The domain restrictions are correctly generated for equations with lag references.

## Verification

```bash
# Translation succeeds and passes validation
python scripts/gamslib/batch_translate.py --model jobt --validate
# Success: 1 (100.0%), Validation Passed: 1

# Scalars have correct values
python -c "
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/jobt.gms')
print('alpha:', ir.params['alpha'].values)  # {(): 6.0}
print('rho:', ir.params['rho'].values)      # {(): 8.0}
"

# Domain restrictions are present
grep "t-1" data/gamslib/mcp/jobt_mcp.gms
# cb(t)$(ord(t) > 1).. s(t) =E= s(t-1) + ...
# wb(t)$(ord(t) > 1).. w(t) =E= w(t-1) - ...
```

## Files Modified

No additional changes needed - fixed by Issue #651 scalar parsing fix.
