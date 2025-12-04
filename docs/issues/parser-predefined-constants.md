# Parser: Predefined Constants (yes/no/inf/eps) Not Supported

**GitHub Issue**: #407  
**URL**: https://github.com/jeffreyhorn/nlp2mcp/issues/407  
**Priority**: HIGH  
**Complexity**: Low  
**Estimated Effort**: 1 hour  
**Tier 2 Models Blocked**: water.gms

## Summary

GAMS has several predefined constants that are automatically available in all models: `yes`, `no`, `inf`, `eps`, `na`, and others. The parser currently treats these as undefined symbols, causing errors when they're used.

## Current Behavior

When parsing water.gms (line 31), the parser fails with:

```
Error: Parse error at line 31, column 10: Undefined symbol 'yes' referenced [context: assignment] [domain: ('n',)]
  dn(n)  = yes;
           ^
```

## Expected Behavior

The parser should recognize GAMS predefined constants and treat them as built-in values:
- `yes` = 1 (boolean true)
- `no` = 0 (boolean false)  
- `inf` = positive infinity
- `eps` = machine epsilon (smallest representable value)
- `na` = not available / missing data marker

## Examples

### Boolean Constants
```gams
Parameter active(i);

* Set flags using yes/no
active('item1') = yes;  # Should evaluate to 1
active('item2') = no;   # Should evaluate to 0

* Use in conditionals
equation$(active(i) = yes).. x(i) =e= 1;
```

### Infinity Constant
```gams
Parameter bounds(i) / i1 inf, i2 100, i3 inf /;

* Use in variable bounds
Variable x;
x.lo = 0;
x.up = inf;  # Unbounded above
```

### Epsilon Constant
```gams
Parameter tolerance / eps /;

* Use for numerical comparisons
equation$(abs(value) > eps).. ...
```

## GAMS Predefined Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `yes` | 1 | Boolean true |
| `no` | 0 | Boolean false |
| `inf` | +∞ | Positive infinity |
| `-inf` | -∞ | Negative infinity |
| `eps` | ~2.2e-16 | Machine epsilon |
| `na` | Special | Not available marker |
| `undf` | Special | Undefined value marker |

## Reproduction

### Test File: water.gms (lines 29-33)
```gams
Set n      'nodes'
    rn(n)  'reservoir nodes'
    dn(n)  'demand nodes';

dn(n)  = yes;
dn(rn) =  no;
display dn;
```

### Minimal Test Case
```gams
Set i / 1*3 /;
Parameter flag(i);

* Should parse without error
flag('1') = yes;
flag('2') = no;
flag('3') = yes;

Variable x;
x.up = inf;
x.lo = -inf;

Model test / all /;
```

## Implementation Plan

### Option 1: Parser Symbol Table (Recommended)

Add predefined constants to the parser's symbol table during initialization:

```python
# In parser initialization
PREDEFINED_CONSTANTS = {
    'yes': 1.0,
    'no': 0.0,
    'inf': float('inf'),
    'eps': 2.2204460492503131e-16,  # sys.float_info.epsilon
    'na': None,  # Special marker
    'undf': None,  # Special marker
}
```

### Option 2: Grammar-level Recognition

Add predefined constants as terminals:

```lark
PREDEFINED_CONST: "yes"i | "no"i | "inf"i | "eps"i | "na"i | "undf"i

atom: NUMBER
    | PREDEFINED_CONST
    | var_ref
    | ...
```

**Recommendation**: Option 1 is simpler and more maintainable.

### Implementation Steps

1. Define predefined constants dictionary in parser
2. Check for predefined constants when resolving symbols
3. Return appropriate Const() node with predefined value
4. Handle special values (na, undf) appropriately
5. Add tests for all predefined constants

### Testing Requirements

1. `yes`/`no` in parameter assignments
2. `inf`/`-inf` in variable bounds
3. `eps` in numerical comparisons
4. `na` for missing data
5. Predefined constants in expressions
6. Case insensitivity (YES, Yes, yes should all work)
7. Verify water.gms parses successfully

## Impact

**Models Unlocked**: 1 (water.gms)  
**Parse Rate Improvement**: 55.6% → 61.1% (+5.5 percentage points)

This is a fundamental GAMS feature used in many models for boolean flags and bounds.

## Related Issues

None - this is a standard GAMS feature that should have been supported from the start.

## References

- **GAMS Documentation**: Predefined Symbols and Constants
- **Tier 2 Model**: water.gms (Water Distribution Network Design)
- **Analysis**: Tier 2 parsing status report (2025-12-03)
- **GAMS User's Guide**: Section on Special Values and Constants
