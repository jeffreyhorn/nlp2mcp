# Issue: qabel Translation Bug - Missing Domain Restriction for Lead Index

**Status**: Open
**GitHub Issue**: #652 (https://github.com/jeffreyhorn/nlp2mcp/issues/652)
**Model**: `qabel.gms`
**Component**: Converter / Equation Domain Generation

## Summary

The `qabel` model translation generates equations with lead index references (`k+1`) without the necessary domain restrictions to prevent out-of-range access on the last element.

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

### Actual Output
```gams
stateq(n,k).. x(n,k+1) =E= sum(np, a(n,np) * x(np,k)) + sum(m, b(n,m) * u(m,k)) + c(n);
```

### Problem
The equation is generated for ALL elements of `k`, including the last one. When `k` is the last element, `k+1` references an element that doesn't exist in the set, causing:
- GAMS compilation warning about out-of-range index
- Equation not generated for that case (silently skipped)
- Potential incorrect model behavior

## Root Cause

The converter does not analyze lead/lag expressions in equation bodies to determine required domain restrictions. When an equation body contains `k+1`:
1. The equation should only be generated for `ord(k) < card(k)`
2. A terminal condition may need separate handling for the last element

## Steps to Reproduce

1. Parse `data/gamslib/raw/qabel.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Examine equations with lead references

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/qabel.gms')
converter = Converter(ir)
result = converter.convert()

# Find equations with lead references
for line in result.output.split('\n'):
    if '+1)' in line and '..' in line:
        print(line)
"
```

## Affected Components

- `src/converter/converter.py` - Equation generation
- Need new logic to detect lead/lag in equation body and add domain restrictions

## Proposed Solution

1. During equation emission, analyze the equation body for `IndexOffset` nodes
2. For each `IndexOffset` with positive offset, add `$(ord(idx) < card(idx))` to domain
3. For each `IndexOffset` with negative offset, add `$(ord(idx) > 1)` to domain (for lag)
4. Alternatively, preserve domain conditions from original model

## Related Issues

- Same pattern in `abel_mcp.gms`, `like_mcp.gms`, `jobt_mcp.gms`, `whouse_mcp.gms`
- General issue: domain restriction inference for lead/lag expressions

## Priority

Medium - GAMS handles this gracefully with warnings, but it's semantically incorrect and can cause subtle bugs.
