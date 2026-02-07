# Issue: like Translation Bug - Missing Domain Restriction for Lead Index

**Status**: Open
**GitHub Issue**: #653 (https://github.com/jeffreyhorn/nlp2mcp/issues/653)
**Model**: `like.gms`
**Component**: Converter / Equation Domain Generation

## Summary

The `like` model translation generates an inequality constraint with a lead index reference (`g+1`) without the necessary domain restriction to prevent out-of-range access on the last element.

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
Or equivalently:
```gams
comp_rank(g)$(ord(g) < card(g)).. m(g+1) =G= 0;  * if m(g) term moved
```

### Actual Output
```gams
comp_rank(g).. m(g+1) =G= 0;
```

### Problems
1. Missing domain restriction `$(ord(g) < card(g))`
2. The equation is generated for ALL elements of `g`, including the last
3. When `g` is the last element (e.g., "three"), `g+1` is undefined
4. The constraint logic appears incomplete (should compare `m(g)` and `m(g+1)`)

## Root Cause

Two issues:
1. **Domain restriction not preserved**: The original model's `$(ord(g) < card(g))` condition is lost during translation
2. **Inequality transformation incomplete**: The original `m(g) =l= m(g+1)` should become `m(g+1) - m(g) >= 0`, but only part of the expression appears

## Steps to Reproduce

1. Parse `data/gamslib/gams/like.gms`
2. Translate to MCP format
3. Examine the `comp_rank` equation

```bash
python -c "
from src.ir.parser import Parser
from src.converter.converter import Converter

parser = Parser()
ir = parser.parse_file('data/gamslib/gams/like.gms')

# Check original equation
for name, eq in ir.equations.items():
    if 'rank' in name.lower():
        print(f'{name}: domain={eq.domain}, condition={eq.condition}')

converter = Converter(ir)
result = converter.convert()

# Find the rank constraint
for line in result.output.split('\n'):
    if 'rank' in line.lower() and '..' in line:
        print(line)
"
```

## Affected Components

- `src/ir/parser.py` - Equation condition extraction
- `src/converter/converter.py` - Domain condition preservation and inequality transformation

## Proposed Solution

1. Preserve the original equation's dollar condition during parsing
2. During KKT transformation, carry forward the domain condition to the complementarity equation
3. Ensure proper inequality-to-complementarity transformation captures both LHS and RHS

## Related Issues

- Similar to `qabel-missing-domain-restriction.md`
- Part of broader lead/lag domain restriction issue

## Priority

Medium - The missing domain restriction causes GAMS warnings and potential incorrect behavior.
