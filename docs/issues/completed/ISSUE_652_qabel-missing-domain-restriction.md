# Issue: qabel Translation Bug - Missing Domain Restriction for Lead Index

**Status**: FIXED
**GitHub Issue**: #652 (https://github.com/jeffreyhorn/nlp2mcp/issues/652)
**Model**: `qabel.gms`
**Component**: Converter / Equation Domain Generation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Empty dynamic subsets (ku, ki, kt) | ✅ FIXED | Commit fe5ab5c (P4 fix) |
| Missing domain restriction for lead index | ✅ FIXED | This commit |

## Summary

The `qabel` model translation was generating equations with lead index references (`k+1`) without the necessary domain restrictions to prevent out-of-range access on the last element.

## Original Model Context

The `qabel.gms` model contains a state equation:
```gams
stateq(n,k).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k)) + c(n);
```

This equation defines the next state `x(n,k+1)` in terms of the current state.

## Bug Description

### Expected Output
```gams
stateq(n,k)$(ord(k) < card(k)).. x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

### Previous (Incorrect) Output
```gams
stateq(n,k).. x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

### Problem
The equation was generated for ALL elements of `k`, including the last one. When `k` is the last element, `k+1` references an element that doesn't exist in the set.

## Resolution

Added automatic domain restriction inference for lead/lag expressions in `src/emit/equations.py`:

1. Added `_collect_lead_lag_restrictions()` function that recursively walks expression trees to find `IndexOffset` nodes
2. For lead expressions (positive offset like `k+1`), adds restriction `ord(k) < card(k)`
3. For lag expressions (negative offset like `t-1`), adds restriction `ord(t) > 1`
4. Modified `emit_equation_def()` to detect these patterns and emit the appropriate domain condition

The fix correctly handles:
- IndexOffset nodes directly in expressions
- IndexOffset nodes inside VarRef/ParamRef/MultiplierRef/EquationRef indices
- Circular offsets (++/--) are correctly excluded as they wrap around

## Verification

```python
>>> from src.ir.parser import parse_model_file
>>> from src.emit.emit_gams import emit_gams_mcp
>>> # ... assemble KKT system ...
>>> # Now correctly emits:
>>> # stateq(n,k)$(ord(k) < card(k)).. x(n,k+1) =E= ...
```
