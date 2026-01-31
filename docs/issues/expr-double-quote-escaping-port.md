# Expression Emission: Double Quote Escaping Bug (port model)

**GitHub Issue:** #602
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/602
**Status:** Open
**Priority:** High
**Affects:** port model (and potentially others using quoted parameter indices)

## Summary

The expression emission code incorrectly escapes double quotes in parameter index strings, producing `""rating""` instead of `"rating"`. This causes GAMS compilation errors.

## Reproduction

### Input Model
File: `data/gamslib/raw/port.gms`

```gams
Table ydat(b,*) 'yield data'
                 rating  maturity  yield  tax-rate
   municip-a          2         9    4.3
   ...

Equation
   rdef     'rating definition'
   mdef     'maturity definition'
   idef     'total return definition';

rdef..     sum(b, ydat(b,"rating  ")*investment(b)) =l= 1.4*tinvest;
mdef..     sum(b, ydat(b,"maturity")*investment(b)) =l= 5.0*tinvest;
idef..     return  =e= sum(b, ydat(b,"yield")/100*(1-ydat(b,"tax-rate"))*investment(b));
```

### Steps to Reproduce

```bash
# Generate MCP file
python -m src.cli data/gamslib/raw/port.gms -o data/gamslib/mcp/port_mcp.gms

# Run GAMS (will fail with compilation errors)
gams data/gamslib/mcp/port_mcp.gms
```

### Expected Output

```gams
comp_mdef.. ((-1) * sum(b, ydat(b,"maturity") * investment(b))) =G= 0;
comp_rdef.. ((-1) * sum(b, ydat(b,"rating  ") * investment(b))) =G= 0;
idef.. return =E= sum(b, ydat(b,"yield") / 100 * (1 - ydat(b,"tax-rate")) * investment(b));
```

### Actual Output

```gams
comp_mdef.. ((-1) * sum(b, ydat(b,""maturity"") * investment(b))) =G= 0;
comp_rdef.. ((-1) * sum(b, ydat(b,""rating  "") * investment(b))) =G= 0;
idef.. return =E= sum(b, ydat(b,""yield"") / 100 * (1 - ydat(b,""tax-rate"")) * investment(b));
```

### GAMS Errors

```
**** 8  ')' expected
**** 37  '=l=' or '=e=' or '=g=' operator expected
**** 409  Unrecognizable item - skip to find a new statement
```

## Root Cause Analysis

The bug is in the expression-to-GAMS emission code. When emitting `ParamRef` or similar nodes that contain quoted string indices (like `"rating"`), the quotes are being doubled/escaped incorrectly.

### Likely Location

- `src/emit/expr_to_gams.py` - The `expr_to_gams()` function or related helpers
- Look for code handling `Const` nodes with string values or `ParamRef` indices

### Investigation Notes

1. The IR likely stores the index as `"rating"` (with quotes as part of the string)
2. During emission, the code adds another layer of quotes, producing `""rating""`
3. Need to check if quotes should be stripped during parsing or handled specially during emission

## Proposed Fix

Option A: Strip quotes during parsing when storing parameter indices
- Modify parser to store `rating` instead of `"rating"` in ParamRef indices
- Emit quotes only during GAMS output

Option B: Detect and handle quoted strings during emission
- Check if index string already starts/ends with quotes
- Don't add additional quotes if already present

Option A is cleaner as it normalizes the IR representation.

## Impact

- **port** model fails to compile
- Any model using quoted parameter indices (like `ydat(b,"rating")`) will be affected
- Common pattern in GAMS models with wildcard (*) dimensions

## Related Files

- `src/emit/expr_to_gams.py` - Expression emission
- `src/ir/parser.py` - Parameter reference parsing
- `data/gamslib/raw/port.gms` - Test case
- `data/gamslib/mcp/port_mcp.gms` - Generated output showing bug
