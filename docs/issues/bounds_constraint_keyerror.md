# Issue: Bounds Constraint KeyError in Integration Tests

## ✅ RESOLVED (2025-10-29)

**Resolution**: Fixed by adding bounds check in `_compute_inequality_jacobian()`
- Added check to skip bounds when processing inequalities in `src/ad/constraint_jacobian.py`
- Bounds (e.g., 'x_lo', 'x_up') are in `model_ir.inequalities` but not in `model_ir.equations`
- They are properly handled by `_compute_bound_jacobian()` which was already implemented
- Simple 3-line fix: check `if eq_name in model_ir.normalized_bounds: continue`
- **Result**: `test_bounds_nlp_basic` now passes, 14/15 integration tests passing (93%)

**Branch**: `fix/issue-24-bounds-constraint-keyerror`

## Summary

Integration test `test_bounds_nlp_basic` was failing with a `KeyError: 'x_lo'` when trying to compute derivatives for a model with variable bounds. The constraint Jacobian computation code attempted to look up bound constraints (e.g., `'x_lo'`, `'x_up'`) as equation names in the equations dictionary, but bounds are not equations and don't exist in that dictionary.

## Severity

- **Status**: RESOLVED ✅
- **Severity**: Medium - Bounds handling broken, blocked 1 integration test
- **Component**: Sprint 2 (AD / Automatic Differentiation)
- **Affects**: Models with variable bounds, constraint Jacobian computation
- **Discovered**: Sprint 2 Day 10 (2025-10-29) while fixing Issue #22
- **GitHub Issue**: #24 - https://github.com/jeffreyhorn/nlp2mcp/issues/24
- **Related Issue**: Issue #22 (Integration Tests API Mismatch) - RESOLVED
- **Type**: Implementation bug (incorrect handling of bounds)

## Problem Description

When computing the constraint Jacobian for models that include variable bounds (e.g., `x.lo = -1`, `x.up = 2`), the code in `src/ad/constraint_jacobian.py` attempts to look up these bounds as equation names in `model_ir.equations`, causing a KeyError.

### Error Details

**Test**: `TestScalarModels::test_bounds_nlp_basic` in `tests/ad/test_integration.py`

**Example File**: `examples/bounds_nlp.gms`
```gams
Variables
    x
    y
    obj ;

Equations
    objective
    nonlinear ;

objective..
    obj =e= x + y;

nonlinear..
    sin(x) + cos(y) =e= 0;

x.lo = -1;
x.up = 2;
y.lo = 0;
y.up = +INF;

Model bounds_nlp / objective, nonlinear / ;
Solve bounds_nlp using NLP minimizing obj ;
```

**Stack Trace**:
```
tests/ad/test_integration.py:128: in test_bounds_nlp_basic
    gradient, J_g, J_h = compute_derivatives(model_ir)
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/ad/api.py:178: in compute_derivatives
    J_h, J_g = compute_constraint_jacobian(model_ir)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
src/ad/constraint_jacobian.py:118: in compute_constraint_jacobian
    _compute_inequality_jacobian(model_ir, index_mapping, J_g)
src/ad/constraint_jacobian.py:197: in _compute_inequality_jacobian
    eq_def = model_ir.equations[eq_name]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'x_lo'
```

**Error Location**: `src/ad/constraint_jacobian.py:197`

**Failing Code**:
```python
def _compute_inequality_jacobian(model_ir, index_mapping, J_g):
    """Compute inequality constraint Jacobian (J_g)."""
    for eq_name, eq_indices in index_mapping.eq_to_row.keys():
        # Problem: eq_name might be 'x_lo', 'x_up', etc. (bounds)
        # But model_ir.equations only contains actual equations
        eq_def = model_ir.equations[eq_name]  # ❌ KeyError here
        # ...
```

## Root Cause

Variable bounds are stored separately from equations in the model IR, but the constraint Jacobian computation code treats them as regular inequality equations. The code attempts to look up bound constraint names in `model_ir.equations`, which only contains explicitly defined equations, not bound constraints.

### Key Observations:

1. **Bounds are not equations**: Bounds like `x.lo = -1` define constraints but aren't listed in the GAMS `Equations` section
2. **Separate storage**: Bounds are likely stored in `model_ir.normalized_bounds` or similar
3. **Different handling needed**: Bounds need special handling during Jacobian computation:
   - Lower bound: `x >= x_lo` → `-x + x_lo <= 0` (inequality)
   - Upper bound: `x <= x_up` → `x - x_up <= 0` (inequality)

## Expected Behavior

The test expects:
1. Bounds to be converted to inequality constraints during normalization
2. These constraints to be included in the inequality Jacobian `J_g`
3. Derivatives computed correctly: `∂(x - bound)/∂x = 1`

**Expected Test Result**:
```python
def test_bounds_nlp_basic(self):
    model_ir = parse_and_normalize("bounds_nlp.gms")
    gradient, J_g, J_h = compute_derivatives(model_ir)
    
    # Should have gradient
    assert gradient.num_nonzeros() > 0  # ✅ This works
    
    # Bounds contribute to J_g (inequality constraints)
    assert J_g.num_nonzeros() > 0  # ❌ Fails before reaching this
```

## Investigation Needed

### 1. How are bounds stored in normalized model?

**Code to run**:
```python
from src.ir.parser import parse_model_file
from src.ir.normalize import normalize_model

model_ir = parse_model_file('examples/bounds_nlp.gms')
normalize_model(model_ir)

print("Equations:", list(model_ir.equations.keys()))
print("Inequalities:", list(model_ir.inequalities.keys()))
print("Equalities:", list(model_ir.equalities.keys()))
print("Normalized bounds:", model_ir.normalized_bounds if hasattr(model_ir, 'normalized_bounds') else 'N/A')

# Check ModelIR attributes
import inspect
print("\nModelIR attributes:")
for attr in dir(model_ir):
    if not attr.startswith('_'):
        print(f"  {attr}")
```

### 2. Where are bounds normalized?

**Files to check**:
- `src/ir/normalize.py` - Where normalization happens
- `src/ir/model.py` - ModelIR class definition
- Look for bound handling code

### 3. How should bounds be represented?

**Options**:
- **A**: Bounds stored as special inequality constraints with marker (e.g., `is_bound=True`)
- **B**: Bounds stored separately, need special Jacobian computation logic
- **C**: Bounds converted to regular inequality equations during normalization

## Proposed Solutions

### Option 1: Check if Constraint is a Bound (Recommended)

**Approach**: In `_compute_inequality_jacobian`, detect bound constraints and handle them specially

**Changes in** `src/ad/constraint_jacobian.py`:
```python
def _compute_inequality_jacobian(model_ir, index_mapping, J_g):
    """Compute inequality constraint Jacobian (J_g)."""
    for eq_name, eq_indices in index_mapping.eq_to_row.keys():
        # Check if this is a bound constraint
        if _is_bound_constraint(eq_name):
            # Handle bounds specially
            _compute_bound_jacobian(model_ir, eq_name, eq_indices, index_mapping, J_g)
        else:
            # Handle regular inequality equations
            eq_def = model_ir.equations[eq_name]
            _differentiate_constraint(eq_def, ...)

def _is_bound_constraint(eq_name: str) -> bool:
    """Check if equation name represents a bound constraint."""
    return eq_name.endswith('_lo') or eq_name.endswith('_up')

def _compute_bound_jacobian(model_ir, bound_name, eq_indices, index_mapping, J_g):
    """Compute Jacobian for a bound constraint."""
    # Extract variable name: 'x_lo' -> 'x'
    if bound_name.endswith('_lo'):
        var_name = bound_name[:-3]
        # Lower bound: -x + bound <= 0, so ∂/∂x = -1
        deriv = Expr(const=-1.0)
    elif bound_name.endswith('_up'):
        var_name = bound_name[:-3]
        # Upper bound: x - bound <= 0, so ∂/∂x = 1
        deriv = Expr(const=1.0)
    
    # Get variable column ID
    col_id = index_mapping.var_to_col.get((var_name, eq_indices))
    if col_id is not None:
        row_id = index_mapping.eq_to_row[(bound_name, eq_indices)]
        J_g.entries[row_id][col_id] = deriv
```

**Pros**:
- Minimal changes
- Bounds handled correctly
- Works with existing normalization

**Cons**:
- Assumes bound naming convention (`_lo`, `_up`)
- Need to verify this matches actual normalization

### Option 2: Store Bounds Separately in ModelIR

**Approach**: Add explicit `bounds` attribute to ModelIR and handle separately

**Changes in** `src/ir/model.py`:
```python
@dataclass
class ModelIR:
    # ... existing fields ...
    bounds: dict[str, dict[str, float]] = field(default_factory=dict)
    # Example: bounds = {'x': {'lo': -1, 'up': 2}, 'y': {'lo': 0}}
```

**Changes in** `src/ad/constraint_jacobian.py`:
```python
def _compute_inequality_jacobian(model_ir, index_mapping, J_g):
    """Compute inequality constraint Jacobian (J_g)."""
    
    # Handle regular inequality equations
    for eq_name, eq_indices in index_mapping.eq_to_row.keys():
        if eq_name not in model_ir.equations:
            continue  # Skip bounds (handled below)
        eq_def = model_ir.equations[eq_name]
        # ... differentiate ...
    
    # Handle bounds
    _compute_bounds_jacobian(model_ir, index_mapping, J_g)

def _compute_bounds_jacobian(model_ir, index_mapping, J_g):
    """Compute Jacobian entries for variable bounds."""
    for var_name, bounds_dict in model_ir.bounds.items():
        if 'lo' in bounds_dict:
            # Add lower bound row to J_g
            # ...
        if 'up' in bounds_dict:
            # Add upper bound row to J_g
            # ...
```

**Pros**:
- Clean separation of bounds and equations
- Explicit handling
- Easier to maintain

**Cons**:
- Requires changes to ModelIR structure
- Need to update normalization code
- More invasive changes

### Option 3: Skip Bounds in Equation Loop

**Approach**: Simple try/except to skip bounds temporarily

**Changes in** `src/ad/constraint_jacobian.py`:
```python
def _compute_inequality_jacobian(model_ir, index_mapping, J_g):
    """Compute inequality constraint Jacobian (J_g)."""
    for eq_name, eq_indices in index_mapping.eq_to_row.keys():
        try:
            eq_def = model_ir.equations[eq_name]
            # ... differentiate ...
        except KeyError:
            # Skip bounds for now (TODO: implement bounds handling)
            continue
```

**Pros**:
- Quick fix to unblock test
- Minimal changes

**Cons**:
- Doesn't actually fix bounds handling
- Test will still fail (won't compute bound derivatives)
- Temporary workaround only

## Recommended Approach

**Immediate**: Investigate how bounds are stored (Investigation Step 1)
- Run diagnostic code to see ModelIR structure
- Check what keys exist in `index_mapping.eq_to_row`

**Then**: Implement Option 1 if bounds use naming convention
- Quick fix with minimal changes
- Properly computes bound derivatives

**Future**: Consider Option 2 for cleaner architecture
- Separate PR after Option 1 works
- Better long-term design

## Files Affected

### Test Files
- `tests/ad/test_integration.py` - Remove `@skip_bounds_bug` marker after fix

### Implementation Files
- `src/ad/constraint_jacobian.py` - Main file needing changes
- `src/ir/normalize.py` - May need investigation/changes for how bounds are stored
- `src/ir/model.py` - May need changes if Option 2 chosen

### Example Files
- `examples/bounds_nlp.gms` - Test case file

## Test Execution

### Before Fix
```bash
$ python -m pytest tests/ad/test_integration.py::TestScalarModels::test_bounds_nlp_basic -xvs
SKIPPED (Bounds handling bug: Code tries to look up bounds (e.g., 'x_lo') as equations, 
causing KeyError. Bounds should be handled separately from equations.)
```

### After Fix (Expected)
```bash
$ python -m pytest tests/ad/test_integration.py::TestScalarModels::test_bounds_nlp_basic -xvs
PASSED
```

## Related Issues

- **GitHub Issue #22** (RESOLVED ✅): Integration Tests API Mismatch
  - https://github.com/jeffreyhorn/nlp2mcp/issues/22
  - This issue was discovered while fixing Issue #22
  - Bounds test initially thought to be API mismatch, but is actually a KeyError bug

## Next Steps

1. **Investigate**: Run diagnostic code to understand bounds storage
2. **Choose**: Select solution approach based on investigation
3. **Implement**: Fix constraint Jacobian computation for bounds
4. **Test**: Verify `test_bounds_nlp_basic` passes
5. **Document**: Update code comments explaining bounds handling
