# Issue: Wildcard Parameter Domain (*) Not Supported

**Status**: FIXED
**GitHub Issue**: #660 (https://github.com/jeffreyhorn/nlp2mcp/issues/660)
**Models**: `least.gms`, `chenery.gms`
**Component**: Parser / Parameter Emission

## Summary

Parameters declared with wildcard domain `*` (e.g., `dat(i,*)`) are not properly handled during emission. The wildcard is emitted literally, causing GAMS Error 66 "Symbol not defined".

## Problem Description

GAMS allows parameters to be declared with a wildcard domain `*` that matches any set. When emitting such parameters, we were emitting the `*` literally, which is invalid syntax for parameter declarations.

### Example (least model)

**Original GAMS:**
```gams
Table dat(i,*) 'data table'
        x     y
   1    1    12
   2    2    14
   ...
```

**Emitted GAMS (incorrect - before fix):**
```gams
Parameters
    dat(i,*)
;
```

**Error:**
```
*** Error 66 in /tmp/tmpcs7i4gkc.gms
    "dat" symbol not defined
*** Error 256: Equation references "dat" declared as Parameter
```

## Root Cause

Two issues were identified and fixed:

1. **Table parsing bug**: When table rows have numeric row labels (like `1`, `2`, `3`), the parser was skipping them because it only accepted `ID` tokens, not `NUMBER` tokens, for row labels.

2. **Wildcard emission bug**: The parameter emission in `emit_original_parameters()` was emitting wildcard domains as-is, which GAMS doesn't accept in parameter declarations.

## Fix Details

### Fix 1: Table Parsing with Numeric Row Labels

**File**: `src/ir/parser.py`

Changed the row label token check to accept both ID and NUMBER tokens:

```python
# Before:
if line_tokens[0].type != "ID":
    continue

# After:
# Row labels can be ID or NUMBER tokens (e.g., "1", "2" in table rows)
if line_tokens[0].type not in ("ID", "NUMBER"):
    continue
```

### Fix 2: Wildcard Domain Inference

**File**: `src/emit/original_symbols.py`

Added `_infer_wildcard_elements()` function that examines parameter data keys to determine what elements the wildcard represents. The fix:

1. Detects parameters with `*` in their domain
2. Infers actual set elements from the data keys
3. Creates anonymous sets (e.g., `dat_dim2`) to hold the inferred elements
4. Replaces `*` with the anonymous set name in the parameter domain

**Example output after fix:**
```gams
Sets
    dat_dim2 /x, y/
;

Parameters
    dat(i,dat_dim2) /1.y 127.0, 1.x -5.0, 2.y 151.0, .../
;
```

## Affected Models

| Model | Parameter | Declaration | Status |
|-------|-----------|-------------|--------|
| least | `dat(i,*)` | 2D table with wildcard | FIXED |
| chenery | `pdat(lmh,*,sde,i)` | 4D table with wildcard | FIXED |
| chenery | `ddat(lmh,*,i)` | 3D table with wildcard | FIXED |
| chenery | `tdat(lmh,*,t)` | 3D table with wildcard | FIXED |

## Testing

All quality checks pass:
- `make typecheck` - SUCCESS
- `make lint` - SUCCESS
- `make format` - SUCCESS
- `make test` - SUCCESS (3258 passed)

## Verification

```python
from src.ir.parser import parse_model_file
from src.emit.original_symbols import emit_original_parameters

ir = parse_model_file('data/gamslib/raw/least.gms')
result = emit_original_parameters(ir)
print(result)
# Output:
# Sets
#     dat_dim2 /x, y/
# ;
#
# Parameters
#     dat(i,dat_dim2) /1.y 127.0, 1.x -5.0, .../
# ;
```
