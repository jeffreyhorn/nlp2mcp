# Issue: abel Translation Bug - Missing Domain Restriction for Lead Index

**Status**: PARTIALLY FIXED (Sprint 18 Day 3)
**GitHub Issue**: #656 (https://github.com/jeffreyhorn/nlp2mcp/issues/656)
**Model**: `abel.gms`
**Component**: Converter / Equation Domain Generation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Empty dynamic subsets (ku, ki, kt) | ✅ FIXED | Commit fe5ab5c (P4 fix) |
| Missing domain restriction for lead index | ❌ OPEN | Not yet addressed |

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

1. Parse `data/gamslib/raw/abel.gms` (raw GAMS models must be downloaded locally)
2. Translate to MCP format
3. Examine the `stateq` equation

```bash
python -c "
from src.ir.parser import parse_model_file
from src.converter.converter import Converter

ir = parse_model_file('data/gamslib/raw/abel.gms')
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

---

## Partial Resolution (Sprint 18 Day 3)

### Related Fix: Empty Dynamic Subsets (P4)

The abel model uses dynamic subsets `ku(k)`, `ki(k)`, and `kt(k)` that were being declared but not initialized. This was fixed in commit fe5ab5c:

**Problem**: Dynamic subset assignment statements were parsed but not stored or emitted:
```gams
* Original assignments in abel.gms:
ku(k) = yes$(ord(k) < card(k));
ki(k) = yes$(ord(k) = 1);
kt(k) = not ku(k);

* Before fix: These assignments were missing from emitted GAMS
* After fix: These are now correctly emitted
```

**Fix**: Added `SetAssignment` dataclass and `emit_set_assignments()` function to capture and emit dynamic subset initialization.

**Verification:**
```python
>>> from src.ir.parser import parse_model_file
>>> from src.emit.original_symbols import emit_set_assignments
>>> ir = parse_model_file('data/gamslib/raw/abel.gms')
>>> print(emit_set_assignments(ir))
ku(k) = 1$ord(k) < card(k);
ki(k) = 1$ord(k) = 1;
kt(k) = not ku(k);
```

### Bug REMAINING: Missing Domain Restriction for Lead Index

**Problem**: The `stateq` equation uses `k+1` but lacks the domain restriction `$(ord(k) < card(k))`:
```gams
* Original:
stateq(n,k).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k)) + c(n);

* Expected output:
stateq(n,k)$(ord(k) < card(k)).. x(n,k+1) =E= ...

* Actual (WRONG):
stateq(n,k).. x(n,k+1) =E= ...
```

**Root Cause**: The converter does not analyze lead expressions in equation bodies to infer required domain restrictions. When an equation body contains `k+1`, the equation should only be generated for `ord(k) < card(k)`.

**Steps to Reproduce:**
```bash
python -c "
from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.gradient import compute_objective_gradient
from src.emit.emit_gams import emit_gams_mcp
from src.ir.normalize import normalize_model
from src.ir.parser import parse_model_file
from src.kkt.assemble import assemble_kkt_system

ir = parse_model_file('data/gamslib/raw/abel.gms')
normalized, _ = normalize_model(ir)
gradient = compute_objective_gradient(ir)
J_eq, J_ineq = compute_constraint_jacobian(ir, normalized)
kkt = assemble_kkt_system(ir, gradient, J_eq, J_ineq)
output = emit_gams_mcp(kkt, add_comments=False)

# Find the stateq equation - should have \$(ord(k) < card(k)) but doesn't
for line in output.split('\n'):
    if 'stateq' in line.lower() and '..' in line:
        print(line)
"
```

**Fix Approach:**
1. During equation body analysis, detect `IndexOffset` nodes with positive offsets
2. For lead references like `k+1`, add domain restriction `$(ord(k) < card(k))`
3. Handle terminal conditions separately if needed

**Affected Files:**
- `src/converter/converter.py` - Equation generation
- `src/emit/equations.py` - Equation emission with domain conditions
