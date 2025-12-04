# Parser: Square Bracket Indexing Not Supported

**GitHub Issue**: #406  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/406  
**Priority**: HIGH  
**Complexity**: Low  
**Estimated Effort**: 1-2 hours  
**Tier 2 Models Blocked**: jbearing.gms

## Summary

GAMS supports both parentheses `()` and square brackets `[]` for indexing parameters, variables, and sets. The parser currently only supports parentheses syntax, causing parse errors when square brackets are used.

## Current Behavior

When parsing jbearing.gms (line 62), the parser fails with:

```
Error: Parse error at line 62, column 46: Unexpected character: '['
  obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                                               ^
```

## Expected Behavior

The parser should accept both indexing syntaxes interchangeably:
- `wq(i)` - parentheses (currently supported)
- `wq[i]` - square brackets (not supported)

Both should be treated identically and produce the same IR.

## Examples

### Single Index
```gams
Parameter p(i);
Variable x(i);

* Both should work:
equation.. obj =e= p(i) * x(i);   * Currently works
equation.. obj =e= p[i] * x[i];   * Currently fails
```

### Multi-dimensional Index
```gams
Parameter data(i,j);

* Both should work:
equation.. cost =e= data(i,j);    * Currently works
equation.. cost =e= data[i,j];    * Currently fails
```

### Mixed Usage
```gams
* Should allow mixing in same expression:
equation.. obj =e= a(i) + b[i] + c(i,j) * d[i,j];
```

## GAMS Specification

From GAMS documentation:
- Square brackets `[]` and parentheses `()` are interchangeable for indexing
- This is purely stylistic preference
- Some modelers prefer `[]` for clarity or consistency with mathematical notation

## Reproduction

### Test File: jbearing.gms (lines 60-64)
```gams
defobj..
   obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                         *(sqr((v[i+1,j] - v[i,j])/hx) + sqr((v[i,j+1] - v[i,j])/hy))}
        +  (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (2*wq[i+1] + 2*wq[i])
                         *(sqr((v[i,j+1] - v[i,j])/hy) + sqr((v[i+1,j] - v[i,j])/hx))};
```

### Minimal Test Case
```gams
Set i / 1*5 /;
Parameter p(i) / 1 10, 2 20, 3 30 /;
Variable x(i);
Equation test;

test.. x[1] =e= p[1] + p[2];

Model m / all /;
```

## Implementation Plan

### Grammar Changes (src/gams/gams_grammar.lark)

Current:
```lark
var_ref: ID "(" index_list ")"
```

Updated:
```lark
var_ref: ID "(" index_list ")"
       | ID "[" index_list "]"
```

Similar changes needed for:
- Parameter references
- Set references  
- Any other indexed symbols

### Parser Changes

No semantic changes needed - square brackets should be treated identically to parentheses. The grammar change alone should be sufficient.

### Testing Requirements

1. Single-dimensional indexing with `[]`
2. Multi-dimensional indexing with `[]`
3. Mixed usage of `()` and `[]` in same expression
4. Square brackets in equation domains
5. Square brackets in sum expressions
6. Verify jbearing.gms parses successfully

## Impact

**Models Unlocked**: 1 (jbearing.gms)  
**Parse Rate Improvement**: 55.6% → 61.1% (+5.5 percentage points)

This is a simple grammar change with high impact for models using this common alternative syntax.

## Related Issues

None - this is a straightforward syntax support addition.

## References

- **GAMS Documentation**: Index notation and syntax alternatives
- **Tier 2 Model**: jbearing.gms (Journal bearing COPS 2.0 #16)
- **Analysis**: Tier 2 parsing status report (2025-12-03)
