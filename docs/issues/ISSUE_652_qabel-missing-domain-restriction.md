# Issue: qabel Translation Bug - Missing Domain Restriction for Lead Index

**Status**: PARTIALLY FIXED (Sprint 18 Day 3)
**GitHub Issue**: #652 (https://github.com/jeffreyhorn/nlp2mcp/issues/652)
**Model**: `qabel.gms`
**Component**: Converter / Equation Domain Generation

## Fix Status

| Bug | Status | Fixed In |
|-----|--------|----------|
| Empty dynamic subsets (ku, ki, kt) | ✅ FIXED | Commit fe5ab5c (P4 fix) |
| Missing domain restriction for lead index | ❌ OPEN | Not yet addressed |

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

---

## Partial Resolution (Sprint 18 Day 3)

### Related Fix: Empty Dynamic Subsets (P4)

The qabel model uses dynamic subsets `ku(k)`, `ki(k)`, and `kt(k)` that were being declared but not initialized. This was fixed in commit fe5ab5c:

**Problem**: Dynamic subset assignment statements were parsed but not stored or emitted:
```gams
* Original assignments in qabel.gms:
ku(k) = ord(k) < card(k);
ki(k) = ord(k) = 1;
kt(k) = not ku(k);

* Before fix: These assignments were missing from emitted GAMS
* After fix: These are now correctly emitted
```

**Fix**: Added `SetAssignment` dataclass and `emit_set_assignments()` function to capture and emit dynamic subset initialization.

**Verification:**
```python
>>> from src.ir.parser import parse_model_file
>>> from src.emit.original_symbols import emit_set_assignments
>>> ir = parse_model_file('data/gamslib/raw/qabel.gms')
>>> print(emit_set_assignments(ir))
ku(k) = ord(k) < card(k);
ki(k) = ord(k) = 1;
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

ir = parse_model_file('data/gamslib/raw/qabel.gms')
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
