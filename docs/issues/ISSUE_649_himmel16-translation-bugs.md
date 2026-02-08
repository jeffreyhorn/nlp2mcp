# Issue: himmel16 Translation Bugs - Constraint RHS and Stationarity Indexing

**Status**: PARTIALLY FIXED (Sprint 18 Day 3)
**GitHub Issue**: #649 (https://github.com/jeffreyhorn/nlp2mcp/issues/649)
**Model**: `himmel16.gms`
**Component**: Converter / KKT Transformation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Invalid .fx bound names (nested parens) | ✅ FIXED | Commit 494d31c (P3 fix) |
| Constraint RHS missing | ❌ OPEN | Not yet addressed |
| Stationarity equation indexing | ❌ OPEN | Not yet addressed |

## Summary

The `himmel16` model translation has two critical bugs:

1. **Inequality constraint missing RHS and sign flip**: The `maxdist` constraint loses its RHS constant and has incorrect sign
2. **Stationarity equation indexing bug**: The partial derivatives use `(x(i) - x(i))` instead of `(x(i) - x(j))`

## Original Model Context

The `himmel16.gms` model contains an inequality constraint:
```gams
maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i)-x(j)) + sqr(y(i)-y(j)) =l= 1;
```

This constrains the maximum distance between points to be at most 1.

## Bug 1: Constraint RHS Missing

### Expected Output
```gams
comp_maxdist(i,j)$(ord(i) < ord(j)).. 1 - (sqr(x(i) - x(j)) + sqr(y(i) - y(j))) =G= 0;
```

### Actual Output
```gams
comp_maxdist(i,j).. ((-1) * (sqr(x(i) - x(j)) + sqr(y(i) - y(j)))) =G= 0;
```

### Problems
1. The RHS `1` is missing from the transformed constraint
2. The domain restriction `$(ord(i) < ord(j))` is missing
3. The sign handling results in incorrect feasible region

### Root Cause
The converter's inequality-to-complementarity transformation is not correctly handling the RHS constant when transforming `LHS =l= RHS` to `RHS - LHS >= 0`.

## Bug 2: Stationarity Equation Indexing

### Expected Output
```gams
stat_x(i).. ... + sum(j, 2 * (x(i) - x(j)) * lam_maxdist(i,j)) =E= 0;
stat_y(i).. ... + sum(j, 2 * (y(i) - y(j)) * lam_maxdist(i,j)) =E= 0;
```

### Actual Output
```gams
stat_x(i).. ... + sum(j, 2 * (x(i) - x(i)) * lam_maxdist(i,j)) =E= 0;
stat_y(i).. ... + sum(j, 2 * (y(i) - y(i)) * lam_maxdist(i,j)) =E= 0;
```

### Problem
The partial derivative computation uses `(x(i) - x(i))` which is identically zero, instead of `(x(i) - x(j))` for the distance constraint.

### Root Cause
The symbolic differentiation or index substitution logic is incorrectly using the same index for both terms in the difference when computing gradients with respect to indexed variables.

## Steps to Reproduce

1. Parse `data/gamslib/raw/himmel16.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Examine the generated `comp_maxdist` and `stat_x`/`stat_y` equations

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/himmel16.gms')
converter = Converter(ir)
result = converter.convert()
print(result.output)
"
```

## Affected Components

- `src/converter/converter.py` - Inequality constraint transformation
- `src/ir/differentiation.py` - Symbolic differentiation with indexed variables
- KKT stationarity equation generation

## Related Issues

- Domain restriction preservation (the `$(ord(i) < ord(j))` condition)
- Indexed variable differentiation

## Priority

High - These bugs produce mathematically incorrect MCP formulations.

---

## Partial Resolution (Sprint 18 Day 3)

### Related Fix: Invalid .fx Bound Names (P3)

While not directly listed in the original issue, the himmel16 model also had invalid GAMS identifier names from `.fx` bounds. This was fixed in commit 494d31c:

**Problem**: Per-element `.fx` bounds like `x.fx("1") = 0` generated equation and multiplier names with parentheses:
```gams
nu_x_fx(1)(i)   * <- nested parens invalid GAMS identifier
x_fx(1)(i)..    * <- nested parens in equation name
```

**Fix**: Changed `_bound_name()` in `src/ir/normalize.py` to use underscores:
```gams
nu_x_fx_1       * <- valid identifier with underscores
x_fx_1..        * <- valid equation name
```

### Bug 1 REMAINING: Constraint RHS Missing

**Problem**: The `maxdist` constraint loses its RHS constant `1` during transformation:
```gams
* Original:
maxdist(i,j)$(ord(i) < ord(j)).. sqr(x(i)-x(j)) + sqr(y(i)-y(j)) =l= 1;

* Expected MCP form:
comp_maxdist(i,j)$(ord(i) < ord(j)).. 1 - (sqr(x(i) - x(j)) + sqr(y(i) - y(j))) =G= 0;

* Actual (WRONG):
comp_maxdist(i,j).. ((-1) * (sqr(x(i) - x(j)) + sqr(y(i) - y(j)))) =G= 0;
```

**Root Cause**: The inequality-to-complementarity transformation in the converter is not correctly handling the RHS constant when transforming `LHS =l= RHS` to `RHS - LHS >= 0`.

**Steps to Reproduce:**
```bash
python -c "
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
ir = parse_model_file('data/gamslib/raw/himmel16.gms')
normalized, _ = normalize_model(ir)
for eq in normalized:
    if 'maxdist' in eq.name.lower():
        print(f'{eq.name}: {eq}')
"
```

**Affected Files:** `src/ir/normalize.py`, `src/converter/converter.py`

### Bug 2 REMAINING: Stationarity Equation Indexing

**Problem**: The partial derivative uses `(x(i) - x(i))` instead of `(x(i) - x(j))`:
```gams
* Expected:
stat_x(i).. ... + sum(j, 2 * (x(i) - x(j)) * lam_maxdist(i,j)) =E= 0;

* Actual (WRONG):
stat_x(i).. ... + sum(j, 2 * (x(i) - x(i)) * lam_maxdist(i,j)) =E= 0;
```

**Root Cause**: The symbolic differentiation or index substitution logic is incorrectly using the same index for both terms in the difference when computing gradients with respect to indexed variables.

**Steps to Reproduce:**
```bash
python -c "
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model
ir = parse_model_file('data/gamslib/raw/himmel16.gms')
normalized, _ = normalize_model(ir)
J_eq, J_ineq = compute_constraint_jacobian(ir, normalized)
# Examine Jacobian entries for maxdist constraint
for (eq_name, var_name), expr in J_ineq.entries.items():
    if 'maxdist' in eq_name.lower() and var_name == 'x':
        print(f'd({eq_name})/d({var_name}) = {expr}')
"
```

**Affected Files:** `src/ad/gradient.py`, `src/ad/differentiation.py`
