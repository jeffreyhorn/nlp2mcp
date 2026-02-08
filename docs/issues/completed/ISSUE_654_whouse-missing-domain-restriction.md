# Issue: whouse Translation Bug - Missing Domain Restriction for Lag Index

**Status**: FIXED
**GitHub Issue**: #654 (https://github.com/jeffreyhorn/nlp2mcp/issues/654)
**Model**: `whouse.gms`
**Component**: Converter / Equation Domain Generation

## Summary

The `whouse` model translation was generating a recurrence equation with a lag index reference (`t-1`) without the necessary domain restriction to prevent out-of-range access on the first element.

## Original Model Context

The `whouse.gms` model (warehouse problem) contains a stock balance equation:
```gams
sb(t).. stock(t) =e= stock(t-1) + buy(t) - sell(t) + istock(t);
```

Where `istock(t)` provides the initial stock for the first period.

## Bug Description

### Expected Output
```gams
sb(t)$(ord(t) > 1).. stock(t) =E= stock(t-1) + buy(t) - sell(t) + istock(t);
```

### Previous (Incorrect) Output
```gams
sb(t).. stock(t) =E= stock(t-1) + buy(t) - sell(t) + istock(t);
```

### Problem
The equation was generated for ALL elements of `t`, including the first one. When `t` is the first element, `t-1` references an element that doesn't exist in the set.

## Resolution

Added automatic domain restriction inference for lead/lag expressions in `src/emit/equations.py`:

1. Added `_collect_lead_lag_restrictions()` function that recursively walks expression trees to find `IndexOffset` nodes
2. For lead expressions (positive offset like `k+n`), adds restriction `ord(k) <= card(k) - n` (e.g., for `k+1`, emits `ord(k) <= card(k) - 1`)
3. For lag expressions (negative offset like `t-n`), adds restriction `ord(t) > n` (e.g., for `t-1`, emits `ord(t) > 1`)
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
>>> # sb(t)$(ord(t) > 1).. stock(t) =E= stock(t-1) + buy(t) - sell(t) + istock(t);
```
