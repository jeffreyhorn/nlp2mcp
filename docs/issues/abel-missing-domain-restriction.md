# Issue: abel Translation Bug - Missing Domain Restriction for Lead Index

**Status**: Open
**GitHub Issue**: #656 (https://github.com/jeffreyhorn/nlp2mcp/issues/656)
**Model**: `abel.gms`
**Component**: Converter / Equation Domain Generation

## Summary

The `abel` model translation generates a state equation with a lead index reference (`k+1`) without the necessary domain restriction to prevent out-of-range access on the last element.

## Original Model Context

The `abel.gms` model (linear-quadratic control problem) contains a state equation:
```gams
stateq(n,k).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k)) + c(n);
```

This is a dynamic system where the next state depends on current state and control.

## Bug Description

### Expected Output
```gams
stateq(n,k)$(ord(k) < card(k)).. x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

### Actual Output
```gams
stateq(n,k).. x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

### Problem
1. The equation is generated for ALL elements of `k`, including the last
2. When `k` is the last element (e.g., "q75"), `k+1` is undefined
3. GAMS will issue a warning and skip generating the equation for that case
4. This may cause the model to be under-determined or behave incorrectly

## Root Cause

The converter does not analyze lead expressions in equation bodies to infer required domain restrictions. The original model likely has this restriction, but it's lost during translation.

## Steps to Reproduce

1. Parse `data/gamslib/gams/abel.gms`
2. Translate to MCP format
3. Examine the `stateq` equation

```bash
python -c "
from src.ir.parser import Parser
from src.converter.converter import Converter

parser = Parser()
ir = parser.parse_file('data/gamslib/gams/abel.gms')
converter = Converter(ir)
result = converter.convert()

# Find the stateq equation
for line in result.output.split('\n'):
    if 'stateq' in line.lower() and '..' in line:
        print(line)
"
```

## Affected Components

- `src/converter/converter.py` - Equation generation
- Need logic to detect lead references and add domain restrictions

## Proposed Solution

1. During equation body analysis, detect `IndexOffset` nodes with positive offsets
2. For lead references like `k+1`, add domain restriction `$(ord(k) < card(k))`
3. Handle terminal conditions separately if needed

## Relationship to qabel

This is essentially the same issue as in `qabel.gms` - both are linear-quadratic control problems with the same state equation structure. The `abel` model is the base version, `qabel` is the quadratic version.

## Related Issues

- `qabel-missing-domain-restriction.md` - Identical issue
- Part of broader lead/lag domain restriction issue

## Priority

Medium - GAMS handles gracefully with warnings, but semantically the model may be incomplete.
