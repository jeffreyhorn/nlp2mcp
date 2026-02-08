# Parser: Negative Infinity (-inf) Not Supported in Table Data

**GitHub Issue**: #408  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/408  
**Priority**: HIGH  
**Complexity**: Low  
**Estimated Effort**: 0.5 hours  
**Tier 2 Models Blocked**: gastrans.gms

## Summary

GAMS supports `-inf` (negative infinity) as a special value in table data to represent unbounded lower limits. The parser currently only recognizes `inf` (positive infinity) but fails on `-inf`.

## Current Behavior

When parsing gastrans.gms (line 45), the parser fails with:

```
Error: Parse error at line 45, column 12: Unexpected character: '-'
  Antwerpen  -inf    -4.034    30   80.0   0
             ^
```

## Expected Behavior

The parser should recognize `-inf` as a special table value representing negative infinity, just as it currently recognizes `inf` for positive infinity.

## Examples

### Table with Bounds
```gams
Table data(i,*)
               lower    upper
    item1      -inf     100
    item2         0     inf
    item3      -inf     inf ;
```

### Common Use Case: Variable Bounds
```gams
Table bounds(i,*)
               lo       up
    x           0      100
    y        -inf      inf      * Unbounded variable
    z        -100      inf ;    * Only lower bound
```

## GAMS Specification

GAMS recognizes several special numeric values in table data:
- `inf` - Positive infinity (+∞)
- `-inf` - Negative infinity (-∞)
- `eps` - Machine epsilon
- `na` - Not available
- `undf` - Undefined

These are case-insensitive: `INF`, `Inf`, `inf` all work.

## Reproduction

### Test File: gastrans.gms (lines 43-47)
```gams
Table       slb(i,*) supply lower and upper bounds and costs
               slo       sup   plo    pup   c
   Anderlues     0     1.2       0   66.2   0
   Antwerpen  -inf    -4.034    30   80.0   0
   Arlon      -inf    -0.222     0   66.2   0
   Berneau       0     0         0   66.2   0
```

### Minimal Test Case
```gams
Set i / 1*3 /;

Table data(i,*)
           lower   upper
    1      -inf    100
    2         0    inf
    3      -inf    inf ;

Display data;
```

## Implementation Plan

### Grammar Changes (src/gams/gams_grammar.lark)

Current table value grammar likely has:
```lark
table_value: NUMBER
           | ID      * For 'inf', 'na', etc.
```

Need to ensure it can handle:
```lark
table_value: NUMBER
           | MINUS NUMBER  * For negative numbers
           | MINUS ID      * For -inf, -na, etc.
           | ID            * For inf, na, etc.
```

Or more elegantly:
```lark
table_value: signed_number
           | signed_special_value

signed_number: MINUS? NUMBER
signed_special_value: MINUS? SPECIAL_VALUE

SPECIAL_VALUE: "inf"i | "eps"i | "na"i | "undf"i
```

### Parser Changes

The parser should:
1. Recognize `-inf` as a token sequence
2. Convert it to `float('-inf')` in Python
3. Store in table data structure

### Testing Requirements

1. `-inf` in table first column
2. `-inf` in table middle columns
3. `-inf` in table last column
4. Mix of `-inf`, `inf`, and regular numbers
5. `-inf` with other special values (`-na`, `-eps` if valid)
6. Case insensitivity: `-INF`, `-Inf`, `-inf`
7. Verify gastrans.gms parses successfully

## Impact

**Models Unlocked**: 1 (gastrans.gms)  
**Parse Rate Improvement**: 55.6% → 61.1% (+5.5 percentage points)

This is a quick fix for a common pattern in optimization models with unbounded variables.

## Related Issues

- Related to predefined constants issue (if implementing that, this becomes trivial)
- Could implement both together as "special values" support

## Technical Notes

### Current Support

The parser likely already supports:
- `inf` (positive infinity)
- Negative numbers in tables: `-42.5`

### Missing Support

Just the combination: `-inf` (minus followed by inf keyword)

### Implementation Approach

If predefined constants are already recognized, this just needs:
1. Allow unary minus operator before special constants in table context
2. Or: recognize `-inf` as a single special token

**Simplest fix**: In table value parsing, if we see `MINUS` followed by `ID` where ID is a special constant, combine them.

## References

- **GAMS Documentation**: Special Values in Data Statements
- **Tier 2 Model**: gastrans.gms (Gas Transmission Problem - Belgium)
- **Analysis**: Tier 2 parsing status report (2025-12-03)
- **Related**: Issue on predefined constants support
