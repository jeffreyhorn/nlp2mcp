# Issue: like Translation Bug - Missing Domain Restriction for Lead Index

**Status**: FIXED
**GitHub Issue**: #653 (https://github.com/jeffreyhorn/nlp2mcp/issues/653)
**Model**: `like.gms`
**Component**: Converter / Equation Domain Generation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Division by zero during model generation | ✅ FIXED | Commit 4e97c4a (P5 fix) |
| Missing domain restriction for lead index | ✅ FIXED | This commit |

## Summary

The `like` model translation was generating an inequality constraint with a lead index reference (`g+1`) without the necessary domain restriction to prevent out-of-range access on the last element.

## Original Model Context

The `like.gms` model (maximum likelihood estimation) contains a ranking constraint:
```gams
rank(g)$(ord(g) < card(g)).. m(g) =l= m(g+1);
```

This enforces ordering on the means `m(g)` of mixture components.

## Bug Description

### Expected Output
```gams
comp_rank(g)$(ord(g) < card(g)).. m(g+1) - m(g) =G= 0;
```

### Previous (Incorrect) Output
```gams
comp_rank(g).. m(g+1) - m(g) =G= 0;
```

### Problem
The equation was generated for ALL elements of `g`, including the last one. When `g` is the last element (e.g., "three"), `g+1` is undefined.

## Resolution

Added automatic domain restriction inference for lead/lag expressions in `src/emit/equations.py`:

1. Added `_collect_lead_lag_restrictions()` function that recursively walks expression trees to find `IndexOffset` nodes
2. For lead expressions (positive offset like `g+1`), adds restriction `ord(g) < card(g)`
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
>>> # comp_rank(g)$(ord(g) < card(g)).. m(g+1) - m(g) =G= 0;
```
