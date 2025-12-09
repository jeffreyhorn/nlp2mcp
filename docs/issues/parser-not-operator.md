# Parser: `not` Operator Not Supported

## GitHub Issue
- **Issue #:** 431
- **URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/431

## Summary
The parser does not support the GAMS `not` operator for boolean negation.

## Affected Model
- **gastrans.gms** (Tier 2) - Gas Transmission Problem - Belgium

## Error
```
Error: Parse error at line 110, column 13: Unexpected character: 'a'
  ap(a) = not as(a);
              ^
```

## Root Cause
The grammar does not include a `not` operator for boolean negation. GAMS supports `not` as a unary operator that negates a boolean expression.

## GAMS Code Pattern
```gams
as(a) = sum(aij(a,i,j), adata(aij,'act'));
ap(a) = not as(a);
```

In this context, `as(a)` is a boolean parameter indicating active arcs, and `ap(a)` is the negation (passive arcs).

## Suggested Fix
Add `not` as a unary operator in the grammar, similar to how `MINUS` is handled for numeric negation:

1. Add `NOT_K` terminal: `NOT_K: /(?i:not)\b/`
2. Add to factor rule: `?factor: ... | NOT_K factor -> unaryop`
3. Handle in parser to produce boolean negation

## Complexity
Medium - requires grammar change and parser handling for boolean expressions.

## Test Case
```gams
Set a / a1, a2 /;
Parameter as(a) / a1 1, a2 0 /;
Parameter ap(a);
ap(a) = not as(a);
```

Expected: `ap('a1') = 0`, `ap('a2') = 1`
