# Issue: whouse Translation Bug - Missing Domain Restriction for Lag Index

**Status**: Open
**GitHub Issue**: #654 (https://github.com/jeffreyhorn/nlp2mcp/issues/654)
**Model**: `whouse.gms`
**Component**: Converter / Equation Domain Generation

## Summary

The `whouse` model translation generates a recurrence equation with a lag index reference (`t-1`) without the necessary domain restriction to prevent out-of-range access on the first element.

## Original Model Context

The `whouse.gms` model (warehouse problem) contains a stock balance equation:
```gams
sb(t).. stock(t) =e= stock(t-1) + buy(t) - sell(t) + istock(t);
```

Where `istock(t)` provides the initial stock for the first period.

## Bug Description

### Expected Output
The original model likely handles the first period specially:
```gams
sb(t)$(ord(t) > 1).. stock(t) =E= stock(t-1) + buy(t) - sell(t);
sb_init.. stock("q-1") =E= istock("q-1") + buy("q-1") - sell("q-1");
```

Or with conditional logic:
```gams
sb(t).. stock(t) =E= (stock(t-1) + buy(t) - sell(t))$(ord(t) > 1)
                   + (istock(t) + buy(t) - sell(t))$(ord(t) = 1);
```

### Actual Output
```gams
sb(t).. stock(t) =E= stock(t-1) + buy(t) - sell(t) + istock(t);
```

### Problems
1. No domain restriction for `ord(t) > 1` when using `t-1`
2. When `t` is the first element ("q-1"), `t-1` is undefined
3. The `istock(t)` term should only apply to the first period, not all periods
4. GAMS will generate a warning about out-of-range lag reference

## Root Cause

The converter does not:
1. Analyze lag expressions to detect potential out-of-range access
2. Infer or preserve domain restrictions for recurrence relations
3. Distinguish initial conditions from recurring dynamics

## Steps to Reproduce

1. Parse `data/gamslib/gams/whouse.gms`
2. Translate to MCP format
3. Examine the stock balance equation

```bash
python -c "
from src.ir.parser import Parser
from src.converter.converter import Converter

parser = Parser()
ir = parser.parse_file('data/gamslib/gams/whouse.gms')
converter = Converter(ir)
result = converter.convert()

# Find equations with lag references
for line in result.output.split('\n'):
    if '-1)' in line and '..' in line:
        print(line)
"
```

## Affected Components

- `src/converter/converter.py` - Equation generation
- Need logic to detect lag references and add appropriate domain restrictions

## Proposed Solution

1. During equation body analysis, detect `IndexOffset` nodes with negative offsets
2. For lag references like `t-1`, add domain restriction `$(ord(t) > 1)`
3. Alternatively, generate separate initial condition handling

## Related Issues

- Similar to `qabel-missing-domain-restriction.md` (but for lag instead of lead)
- Same pattern in `jobt_mcp.gms`
- Part of broader lead/lag domain restriction issue

## Priority

Medium - GAMS handles gracefully with warnings, but semantically incorrect for first period.
