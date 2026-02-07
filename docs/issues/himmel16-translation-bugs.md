# Issue: himmel16 Translation Bugs - Constraint RHS and Stationarity Indexing

**Status**: Open
**GitHub Issue**: #649 (https://github.com/jeffreyhorn/nlp2mcp/issues/649)
**Model**: `himmel16.gms`
**Component**: Converter / KKT Transformation

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

1. Parse `data/gamslib/gams/himmel16.gms`
2. Translate to MCP format
3. Examine the generated `comp_maxdist` and `stat_x`/`stat_y` equations

```bash
python -c "
from src.ir.parser import Parser
from src.converter.converter import Converter

parser = Parser()
ir = parser.parse_file('data/gamslib/gams/himmel16.gms')
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
