# Issue: Division by Zero in Stationarity Equations

**Status**: Open
**GitHub Issue**: #659 (https://github.com/jeffreyhorn/nlp2mcp/issues/659)
**Models**: `chem.gms`, `dispatch.gms`, `jobt.gms`, `like.gms`
**Component**: KKT Stationarity / Variable Initialization

## Summary

Multiple models fail during GAMS model generation with "division by zero" errors. This occurs when variables appear in denominators of stationarity equations but have zero initial values.

## Problem Description

When differentiating expressions like `log(x/xb)` or `1/alpha`, the stationarity equations contain terms with variables in denominators. If these variables have zero initial values (the GAMS default), model generation fails.

### Example (chem model)

**Original equation:**
```gams
edef.. energy =e= sum(c, x(c)*(gplus(c) + log(x(c)/xb)));
```

**Generated stationarity equation:**
```gams
stat_x(c).. gplus(c) + log(x(c) / xb) + x(c) * 1 / (x(c) / xb) * 1 / xb ** 1 + ... =E= 0;
stat_xb.. sum(c, x(c) * 1 / (x(c) / xb) * ((-1) * x(c)) / xb ** 2) + ... =E= 0;
```

**Error:**
```
*** Error at line 39: division by zero (0)
*** Error at line 40: division by zero (0)
```

### Root Cause

1. Variables `x(c)` and `xb` have lower bounds but GAMS defaults their initial level (`.l`) to 0
2. During model generation, GAMS evaluates the expressions with current variable values
3. Division by zero occurs because the denominators evaluate to 0

## Affected Models

| Model | Variables in Denominators | Lower Bounds | Error Lines |
|-------|--------------------------|--------------|-------------|
| chem | `x(c)`, `xb` | `x.lo=0.001`, `xb.lo=0.01` | 39, 40, 49 |
| dispatch | Division in stationarity | Various | 45 |
| jobt | `alpha`, `rho` in `1/alpha`, `1/rho` | Scalars | 49, 50 |
| like | `m(g)`, `p(g)`, `s(g)` | Positive variables | 48, 49, 50, 60 |

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

model_name = 'chem'
gams_file = Path(f'data/gamslib/raw/{model_name}.gms')

ir = parse_model_file(str(gams_file))
normalized, _ = normalize_model(ir)
gradient = compute_objective_gradient(ir)
J_eq, J_ineq = compute_constraint_jacobian(ir, normalized)
kkt = assemble_kkt_system(ir, gradient, J_eq, J_ineq)
output = emit_gams_mcp(kkt, add_comments=False)

with tempfile.NamedTemporaryFile(mode='w', suffix='.gms', delete=False) as f:
    f.write(output)
    temp_path = f.name

result = subprocess.run(['gams', temp_path, 'lo=3'], capture_output=True, text=True)
print(result.stdout)
"
```

## Proposed Solutions

### Option 1: Initialize Variables to Lower Bounds (Recommended)

Add variable initialization to emitted GAMS that sets `.l` to the lower bound when present:

```gams
* Initialize variables to avoid division by zero
x.l(c) = x.lo(c);
xb.l = xb.lo;
```

**Implementation:**
- In `src/emit/emit_gams.py`, after emitting variable bounds, add initialization for variables that:
  1. Have a non-zero lower bound, OR
  2. Appear in denominators of any expression

### Option 2: Safe Initial Value for All Positive Variables

Initialize all positive variables to a small non-zero value:

```gams
* Default initialization for positive variables
x.l(c) = max(x.lo(c), 1e-6);
```

### Option 3: Emit Lower Bounds as Initial Values

When parsing variable bounds, if `.lo` is set but `.l` is not, automatically set `.l = .lo`:

```python
# In variable emission
if var.lo is not None and var.l is None:
    lines.append(f"{var_name}.l = {var_name}.lo;")
```

## Analysis of Each Model

### chem.gms

```gams
* Original bounds:
x.lo(c) = .001;
xb.lo   = .01;

* Stationarity contains:
log(x(c) / xb)           # x and xb in denominator via quotient rule
x(c) * 1 / (x(c) / xb)   # x and xb in explicit denominators
```

**Fix:** Initialize `x.l(c) = 0.001` and `xb.l = 0.01`

### dispatch.gms

Division in stationarity equations from differentiating expressions with variable denominators.

### jobt.gms

```gams
* Scalars used as divisors:
1/alpha
1/rho

* Error: Scalars alpha, rho = 0.0 (not properly initialized from source)
```

**Note:** This is related to the scalar initialization issue already documented in `jobt-division-by-zero-and-missing-restrictions.md`.

### like.gms

```gams
* Positive variables in log expressions:
log(m(g))   # m(g) in denominator
log(p(g))   # p(g) in denominator  
log(s(g))   # s(g) in denominator
```

**Fix:** Initialize positive variables to small non-zero values.

## Priority

High - These models compile successfully but fail during model generation due to numerical issues.

## Related Issues

- `jobt-division-by-zero-and-missing-restrictions.md` - Overlapping scalar initialization issue
- `pak-division-by-zero-and-quoted-lags.md` - Similar scalar initialization pattern

## Affected Files

- `src/emit/emit_gams.py` - Add variable initialization section
- `src/emit/templates.py` - Variable emission with initialization
