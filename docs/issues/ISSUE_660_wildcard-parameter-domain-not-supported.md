# Issue: Wildcard Parameter Domain (*) Not Supported

**Status**: Open
**GitHub Issue**: #660 (https://github.com/jeffreyhorn/nlp2mcp/issues/660)
**Models**: `least.gms`, `chenery.gms`
**Component**: Parser / Parameter Emission

## Summary

Parameters declared with wildcard domain `*` (e.g., `dat(i,*)`) are not properly handled during emission. The wildcard is emitted literally, causing GAMS Error 66 "Symbol not defined".

## Problem Description

GAMS allows parameters to be declared with a wildcard domain `*` that matches any set. When emitting such parameters, we currently emit the `*` literally, which is invalid syntax for parameter declarations.

### Example (least model)

**Original GAMS:**
```gams
Table dat(i,*) 'data table'
        x     y
   1    1    12
   2    2    14
   ...
```

**Emitted GAMS (incorrect):**
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

### Root Cause

1. The parser correctly stores the wildcard `*` as part of the parameter domain
2. The parameter emission in `emit_original_parameters()` emits domains as-is
3. GAMS doesn't accept `*` in parameter declarations - only in table definitions

## Affected Models

| Model | Parameter | Declaration | Issue |
|-------|-----------|-------------|-------|
| least | `dat(i,*)` | 2D table with wildcard | `*` in domain |
| chenery | `pdat(lmh,*,sde,i)` | 4D table with wildcard | `*` in domain |
| chenery | `ddat(lmh,*,i)` | 3D table with wildcard | `*` in domain |
| chenery | `tdat(lmh,*,t)` | 3D table with wildcard | `*` in domain |

## Steps to Reproduce

```bash
python -c "
from pathlib import Path
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system
import subprocess
import tempfile

model_name = 'least'
gams_file = Path(f'data/gamslib/raw/{model_name}.gms')

ir = parse_model_file(str(gams_file))

# Check how the parameter is stored
for name, param in ir.params.items():
    if name == 'dat':
        print(f'Parameter: {name}')
        print(f'Domain: {param.domain}')
        print(f'Values: {list(param.values.keys())[:5]}')
"
```

## Proposed Solutions

### Option 1: Infer Actual Domain from Data (Recommended)

When emitting parameters with `*` in domain, examine the actual data keys to determine the real set elements used:

```python
def _infer_wildcard_domain(param_def):
    \"\"\"Infer actual domain for wildcard positions from parameter data.\"\"\"
    # Collect unique values for each domain position
    if not param_def.values:
        return param_def.domain
    
    domain_values = [set() for _ in param_def.domain]
    for key in param_def.values.keys():
        for i, elem in enumerate(key):
            domain_values[i].add(elem)
    
    # Replace * with inferred set or keep original
    new_domain = []
    for i, d in enumerate(param_def.domain):
        if d == '*':
            # Create anonymous set from values
            new_domain.append(domain_values[i])
        else:
            new_domain.append(d)
    return new_domain
```

### Option 2: Create Anonymous Sets for Wildcards

Create explicit sets for wildcard domains:

```gams
* Original: dat(i,*)
* Emitted:
Set dat_dim2 /x, y/;
Parameters
    dat(i, dat_dim2)
;
```

### Option 3: Use GAMS Table Syntax

Emit wildcard parameters using Table syntax instead of Parameter syntax:

```gams
Table dat(i,*)
        x       y
   1    1.0     12.0
   2    2.0     14.0
;
```

**Note:** This requires preserving table structure during parsing.

## Analysis of Each Model

### least.gms

```gams
* Original:
Table dat(i,*) 'data table'
        x     y
   1    1    12
   2    2    14
   3    3    13
   4    4    16
   5    5    18
   6    6    17;

* Used in equations:
ddev(i).. dat(i,"y") =e= b1 + b2*exp(b3*dat(i,"x")) + dev(i);
```

The wildcard domain contains elements `x` and `y` which are used as explicit indices in equations.

### chenery.gms

Multiple tables with wildcards:

```gams
* pdat has wildcard in second position
Table pdat(lmh,*,sde,i) 'production data'
* Values like: low.a.distr.services 0.8

* ddat has wildcard in second position  
Table ddat(lmh,*,i) 'demand data'
* Values like: low.ynot.services 450.0
```

## Priority

Medium - Affects models using GAMS Table syntax with wildcards.

## Related Issues

- Table data block parsing (Sprint 18 goal)
- Parameter domain inference

## Affected Files

- `src/emit/original_symbols.py` - `emit_original_parameters()` function
- `src/ir/parser.py` - Parameter domain handling
- Potentially need new set inference logic
