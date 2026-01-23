# Issue: x.stage() Stochastic Attribute Syntax Not Supported

**GitHub Issue:** [#554](https://github.com/jeffreyhorn/nlp2mcp/issues/554)  
**Status:** Closed (Fixed)  
**Priority:** Medium  
**Discovered:** Sprint 16 Day 6 (2026-01-23)  
**Affected Models:** apl1p, apl1pca

---

## Summary

The GAMS grammar does not support the `.stage()` attribute syntax used in stochastic programming models. This syntax is used to assign decision stages to variables for multi-stage stochastic optimization.

## Error Message

```
Parse error at line 74, column 8: Unexpected character: '('
  x.stage(g)
         ^
```

## Reproduction Steps

1. Run parse on model `apl1p`:
   ```bash
   python scripts/gamslib/batch_parse.py --model apl1p --verbose
   ```

2. Or directly:
   ```python
   from src.ir.parser import parse_model_file
   parse_model_file('data/gamslib/raw/apl1p.gms')
   ```

## Example GAMS Code (from apl1p.gms, lines 70-81)

```gams
* -----------------------------------------------
* setting decision stages
* -----------------------------------------------
x.stage(g)       = 1;
y.stage(g,dl)    = 2;
s.stage(dl)      = 2;
cmin.stage(g)    = 1;
cmax.stage(g)    = 1;
omax.stage(g)    = 2;
demand.stage(dl) = 2;
tcost.stage      = 1;
```

## Root Cause Analysis

The current grammar handles variable attributes like `.lo`, `.up`, `.fx`, `.l`, `.m` via the `BOUND_K` terminal and `ref_bound` rule:

```lark
BOUND_K: /(lo|up|fx|l|m)/i

ref_bound: ID "." BOUND_K "(" index_list ")"   -> bound_indexed
         | ID "." BOUND_K "[" index_list "]"   -> bound_indexed
         | ID "." BOUND_K                      -> bound_scalar
         | ID "." ID                           -> attr_access
```

The `.stage` attribute is not included in `BOUND_K`, and the fallback `ID "." ID` rule doesn't handle the indexed form `x.stage(g)`.

## Proposed Fix

### Option A: Extend BOUND_K (Minimal Change)

Add `stage` to the `BOUND_K` terminal:

```lark
BOUND_K: /(lo|up|fx|l|m|stage)/i
```

This would allow `x.stage(g)` to parse as a `bound_indexed` node.

### Option B: Add Separate Stage Rule (More Explicit)

Add a dedicated rule for stage assignments:

```lark
stage_stmt: ID "." "stage"i "(" index_list ")" ASSIGN expr SEMI  -> stage_indexed
          | ID "." "stage"i ASSIGN expr SEMI                     -> stage_scalar
```

### Recommendation

Option A is simpler and consistent with existing attribute handling. The `stage` attribute behaves syntactically like bounds (indexed or scalar).

## Affected Models

| Model | Line | Syntax |
|-------|------|--------|
| apl1p | 74-81 | `x.stage(g) = 1;` and similar |
| apl1pca | ~77-84 | Same pattern |

## Testing

After fix, verify:
1. Both apl1p and apl1pca parse successfully
2. No regressions in existing 36 parsing models
3. Stage attribute values are correctly captured in IR (if needed for translation)

## Related Issues

- Sprint 16 Day 6 grammar fixes (PR #553)
- P-1 keyword case fix enabled discovery of this secondary issue

## References

- GAMS Documentation: [Stochastic Programming](https://www.gams.com/latest/docs/UG_EMP_SP.html)
- Model source: `data/gamslib/raw/apl1p.gms`
