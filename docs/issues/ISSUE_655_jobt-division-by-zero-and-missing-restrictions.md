# Issue: jobt Translation Bugs - Division by Zero and Missing Domain Restrictions

**Status**: PARTIALLY FIXED (Sprint 18 Day 3)
**GitHub Issue**: #655 (https://github.com/jeffreyhorn/nlp2mcp/issues/655)
**Model**: `jobt.gms`
**Component**: Converter / Parameter Initialization / Equation Domain Generation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Division by zero in stationarity (variables) | ✅ FIXED | Commit 4e97c4a (P5 fix) |
| Division by zero from scalars (alpha, rho) | ❌ OPEN | Scalar initialization not captured |
| Missing domain restrictions for lag index | ❌ OPEN | Not yet addressed |

## Summary

The `jobt` model translation has two categories of bugs:

1. **Division by zero**: Scalars `alpha` and `rho` are initialized to 0.0 but used as divisors (NOT fixed by P5)
2. **Missing domain restrictions**: Recurrence equations use `t-1` without restricting to `ord(t) > 1`

**Note**: The P5 fix (commit 4e97c4a) addresses division by zero caused by **variables** in denominators (from differentiating log/power expressions), but does NOT fix division by zero from **scalar parameters** like `alpha` and `rho`.

## Bug 1: Division by Zero in Stationarity Equations

### Problem
```gams
Scalars
    alpha /0.0/
    rho /0.0/
;

* In stationarity equations:
... 1/alpha ...
... 1/rho ...
```

The scalars `alpha` and `rho` are initialized to 0.0, but they appear as divisors in the stationarity equations, causing division-by-zero errors.

### Root Cause
The original `jobt.gms` model initializes these parameters with non-zero values, but the parser/converter is losing the initialization:
```gams
* Original likely has:
Scalar alpha /0.5/;
Scalar rho /0.1/;
```

### Expected Fix
1. Preserve original scalar values during parsing
2. Or guard expressions: `(1/alpha)$(alpha <> 0)`

## Bug 2: Missing Domain Restrictions for Lag References

### Problem (Line 100)
```gams
* Actual (incorrect)
cb(t).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);
wb(t).. w(t) =E= w(t-1) - f(t) + h(t) + wi(t);

* Expected (correct)
cb(t)$(ord(t) > 1).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);
wb(t)$(ord(t) > 1).. w(t) =E= w(t-1) - f(t) + h(t) + wi(t);
```

### Issues
1. `s(t-1)`, `u(t-1)`, `w(t-1)` are referenced for all `t`
2. When `t` is the first element, these lag references are out of range
3. Initial conditions need separate handling

## Steps to Reproduce

1. Parse `data/gamslib/raw/jobt.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Check scalar values and equations with lag references

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/jobt.gms')

# Check scalar values
print('Scalars:')
for name, scalar in ir.scalars.items():
    if name in ['alpha', 'rho']:
        print(f'  {name}: {scalar}')

converter = Converter(ir)
result = converter.convert()

# Find equations with lag references
print('\nEquations with t-1:')
for line in result.output.split('\n'):
    if 't-1)' in line and '..' in line:
        print(f'  {line[:100]}...')
"
```

## Affected Components

- `src/ir/parser.py` - Scalar value extraction
- `src/converter/converter.py` - Equation domain generation
- Stationarity equation generation

## Proposed Solution

### For Division by Zero
1. Improve scalar value parsing to capture initialization data
2. Or add guards in generated expressions for potential division by zero

### For Missing Domain Restrictions
1. Analyze equation bodies for `IndexOffset` with negative offsets
2. Add `$(ord(t) > 1)` domain restriction for lag references
3. Generate separate initial condition equations if needed

## Related Issues

- `pak-division-by-zero-and-quoted-lags.md` - Same division by zero pattern
- `whouse-missing-domain-restriction.md` - Same lag restriction issue

## Priority

High - Division by zero causes runtime errors; missing restrictions cause warnings and potential semantic errors.

---

## Partial Resolution (Sprint 18 Day 3)

### Variable Division by Zero FIXED (P5)

The P5 fix in commit 4e97c4a added variable initialization in `src/emit/emit_gams.py` to prevent division by zero during model generation when **variables** appear in denominators:

- Variables with lower bounds are initialized to their lower bound: `var.l = var.lo`
- Positive variables without explicit bounds are initialized to a safe non-zero value (1e-6)

This fixes division by zero from expressions like `1/x` or `log(x)` when `x` is a variable.

### Scalar Division by Zero REMAINING

**Problem**: Scalars `alpha` and `rho` appear in expressions like `1/alpha` and `1/rho`, but are initialized to 0.0:

```gams
Scalars
    alpha /0.0/
    rho /0.0/
;
```

The P5 fix does NOT address this because these are scalar **parameters**, not variables. The fix requires:
1. Investigating how `alpha` and `rho` are initialized in the original `jobt.gms`
2. Ensuring the parser captures scalar initialization from all sources

### Domain Restrictions REMAINING

**Problem**: Recurrence equations use `t-1` without domain restrictions:

```gams
* Actual (incorrect)
cb(t).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);

* Expected (correct)
cb(t)$(ord(t) > 1).. s(t) =E= s(t-1) + p(t) - d(t) - u(t-1) + u(t) + si(t);
```

This requires separate work to detect lag expressions and add appropriate domain restrictions.
