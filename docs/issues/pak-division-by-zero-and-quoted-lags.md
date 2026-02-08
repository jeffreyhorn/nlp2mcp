# Issue: pak Translation Bugs - Division by Zero and Quoted Lag References

**Status**: Open
**GitHub Issue**: #651 (https://github.com/jeffreyhorn/nlp2mcp/issues/651)
**Model**: `pak.gms`
**Component**: Converter / Parameter Initialization / Index Expression Emission

## Summary

The `pak` model translation has two categories of bugs:

1. **Division by zero**: Computed parameters use uninitialized scalar divisors
2. **Quoted lag references**: Lead/lag index expressions emitted as quoted literals

## Bug 1: Division by Zero in Computed Parameters

### Problem
```gams
Scalars
    r /0.0/
    g /0.0/
;

dis = (1 + r) ** ((-1) * (card(t))) * (1 - alpha) * (1 + g) / (r - g);
```

The scalars `r` and `g` are initialized to 0.0, making `(r - g)` equal to zero. This causes a division-by-zero error at compile/evaluation time.

### Root Cause
The converter emits scalar declarations with default values of 0.0 when the original model initializes them via data statements or assignments that aren't captured. The original `pak.gms` model likely has:
```gams
Scalar r /0.03/;  * or assigned elsewhere
Scalar g /0.02/;
```

The parser/converter is losing the actual initialization values.

### Expected Fix
Either:
1. Preserve the original scalar initialization values from the source model
2. Guard the computation: `dis$(abs(r - g) > 1e-6) = ...`

## Bug 2: Quoted Lag References

### Problem
Multiple equations use quoted literals instead of proper lead expressions:
```gams
* Actual (incorrect)
... c("te+1") ...
... ti("te+1") ...
... ks("te+1",j) ...

* Expected (correct)
... c(te+1) ...
... ti(te+1) ...
... ks(te+1,j) ...
```

### Examples from Generated Code

Line 168:
```gams
* Incorrect: quoted literal
stat_c(te).. ... + ... c("te+1") ... =E= 0;
```

Line 176:
```gams
* Incorrect: quoted literal
kbal(te,j).. ks("te+1",j) =E= ks(te,j) + i(te,j);
```

### Expected Output
```gams
kbal(te,j)$(ord(te) < card(te)).. ks(te+1,j) =E= ks(te,j) + i(te,j);
```

### Root Cause
Same as robert.gms - the index expression emission is quoting lead/lag references instead of emitting them as dynamic index expressions.

## Steps to Reproduce

1. Parse `data/gamslib/raw/pak.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Check scalar values and search for quoted lag patterns

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/pak.gms')

# Check scalar values
for name, scalar in ir.scalars.items():
    print(f'{name}: {scalar}')

converter = Converter(ir)
result = converter.convert()
print(result.output[:2000])  # Check first part for scalar values
"
```

## Affected Components

- `src/ir/parser.py` - Scalar value extraction
- `src/emit/expr_to_gams.py` - Index expression emission
- `src/converter/converter.py` - Scalar and equation emission

## Priority

High - Division by zero causes runtime errors; quoted lags cause semantic incorrectness.
