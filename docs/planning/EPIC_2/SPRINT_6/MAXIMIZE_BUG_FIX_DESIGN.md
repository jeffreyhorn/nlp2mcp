# Maximize Bug Fix Design

**Date:** 2025-11-12  
**Status:** DESIGN COMPLETE - Ready for Implementation  
**Priority:** Critical (blocks Sprint 6 Component 2)  
**Estimated Implementation Time:** 2-4 hours

## Problem Statement

Models with `maximize` objective have incorrect signs in stationarity equations. The objective gradient term is not negated for maximize, causing PATH solver failures and incorrect solutions.

**Bug Location:** `src/kkt/stationarity.py` (lines 395-420 and 263-269)

## Root Cause

The stationarity equation builder treats all objectives as minimize:
```
∇f + [constraint terms] - π^L + π^U = 0
```

For maximize objectives, it should be:
```
-∇f + [constraint terms] - π^L + π^U = 0
```

The bound multiplier signs (`-π^L + π^U`) are correct and should not change.

## Fix Options Evaluated

### Option A: Negate Gradient During Assembly ⭐ RECOMMENDED

**Implementation:**
Negate the gradient term when building the stationarity expression if objective sense is maximize.

**Location:** `src/kkt/gradient.py` in the gradient computation function

**Changes:**
```python
# In src/kkt/gradient.py (compute_gradient function)
def compute_gradient(model_ir: ModelIR, var_mapping: IndexMapping) -> Gradient:
    """Compute gradient of objective function.
    
    For maximize objectives, negates the gradient to transform:
        maximize f(x) → minimize -f(x)
    """
    obj_info = extract_objective_info(model_ir)
    
    # ... existing gradient computation code ...
    
    # Negate gradient for maximize objectives
    if model_ir.objective and model_ir.objective.sense == ObjSense.MAX:
        for col_id in range(gradient.num_cols):
            grad_expr = gradient.get_derivative(col_id)
            if grad_expr is not None:
                gradient.derivatives[col_id] = Unary("-", grad_expr)
    
    return gradient
```

**Pros:**
- ✅ Surgical fix at gradient computation level
- ✅ Stationarity code remains unchanged
- ✅ Semantically correct: gradient represents ∇(-f) for maximize
- ✅ No changes needed to bound multiplier logic
- ✅ Works for both scalar and indexed variables automatically
- ✅ Minimal code changes (10-15 lines)

**Cons:**
- ⚠️ Gradient now represents transformed objective, not original
- ⚠️ May be less intuitive when debugging gradient values

**Risk:** LOW - Isolated change, easy to test

---

### Option B: Negate at Stationarity Expression Build

**Implementation:**
Check objective sense when building each stationarity expression and negate gradient term.

**Location:** `src/kkt/stationarity.py` functions `_build_stationarity_expr` and `_build_indexed_stationarity_expr`

**Changes:**
```python
def _build_stationarity_expr(
    kkt: KKTSystem, col_id: int, var_name: str, var_indices: tuple[str, ...],
    obj_defining_eq: str | None
) -> Expr:
    # Start with gradient component
    grad_component = kkt.gradient.get_derivative(col_id)
    expr: Expr
    if grad_component is None:
        expr = Const(0.0)
    else:
        # Negate gradient for maximize objectives
        if kkt.model_ir.objective and kkt.model_ir.objective.sense == ObjSense.MAX:
            expr = Unary("-", grad_component)
        else:
            expr = grad_component
    
    # ... rest of function unchanged ...
```

Similar change needed in `_build_indexed_stationarity_expr`.

**Pros:**
- ✅ Gradient retains original objective meaning
- ✅ Clear where negation happens (in stationarity builder)
- ✅ No changes to gradient computation

**Cons:**
- ⚠️ Requires changes in multiple functions (2 places)
- ⚠️ Duplicates objective sense check logic
- ⚠️ More code to maintain

**Risk:** LOW-MEDIUM - Two functions to modify correctly

---

### Option C: Transform Maximize → Minimize Early (Parser/Normalization)

**Implementation:**
Transform `maximize f(x)` to `minimize -f(x)` during parsing or normalization phase.

**Location:** `src/ir/parser.py` or new normalization step

**Changes:**
```python
# In parser.py after capturing solve statement
if sense == ObjSense.MAX:
    # Transform maximize to minimize
    if obj_def_eq:
        # Negate the RHS of objective defining equation
        eq = self.model.equations[obj_def_eq]
        lhs, rhs = eq.lhs_rhs
        eq.lhs_rhs = (lhs, Unary("-", rhs))
    sense = ObjSense.MIN
```

**Pros:**
- ✅ Conceptually clean: single canonical form (minimize)
- ✅ No KKT code changes needed
- ✅ Eliminates maximize/minimize distinction downstream

**Cons:**
- ❌ Loses original problem formulation
- ❌ Harder to debug (user sees maximize, code sees minimize)
- ❌ May complicate error messages and output interpretation
- ❌ Requires careful handling of objective defining equation
- ❌ May break other assumptions about objective sense

**Risk:** MEDIUM-HIGH - Invasive change, affects entire pipeline

---

## Recommended Solution: Option A

**Rationale:**
1. **Simplicity:** Single-point fix in gradient computation
2. **Correctness:** Mathematically sound (gradient of transformed objective)
3. **Safety:** Minimal code changes, isolated impact
4. **Automatic:** Works for all variable types (scalar, indexed)
5. **Maintainability:** Clear and easy to understand

**Trade-off accepted:**
- Gradient values represent transformed objective for maximize cases
- This is acceptable because gradients are internal KKT system components
- Users don't directly interact with gradient values

## Implementation Plan

### Step 1: Locate Gradient Computation (15 min)

Find the function in `src/kkt/gradient.py` that computes the gradient:
```bash
grep -n "def compute_gradient" src/kkt/gradient.py
```

### Step 2: Add Gradient Negation Logic (30 min)

**Before:**
```python
def compute_gradient(model_ir: ModelIR, var_mapping: IndexMapping) -> Gradient:
    # ... compute gradient ...
    return gradient
```

**After:**
```python
from src.ir.symbols import ObjSense

def compute_gradient(model_ir: ModelIR, var_mapping: IndexMapping) -> Gradient:
    # ... compute gradient ...
    
    # Negate gradient for maximize objectives
    # Transform: maximize f(x) → minimize -f(x)
    if model_ir.objective and model_ir.objective.sense == ObjSense.MAX:
        for col_id in range(gradient.num_cols):
            grad_expr = gradient.get_derivative(col_id)
            if grad_expr is not None:
                gradient.derivatives[col_id] = Unary("-", grad_expr)
    
    return gradient
```

### Step 3: Add Import (5 min)

Ensure `ObjSense` is imported at top of `gradient.py`:
```python
from src.ir.symbols import ObjSense
```

### Step 4: Test on Minimal Cases (1 hour)

Run the minimal test cases:
```bash
# These should now work correctly
python -m src.main tests/fixtures/maximize_debug/test_maximize_simple.gms
python -m src.main tests/fixtures/maximize_debug/test_maximize_upper_bound.gms
python -m src.main tests/fixtures/maximize_debug/test_maximize_both_bounds.gms

# Control test should still work
python -m src.main tests/fixtures/maximize_debug/test_minimize_upper_bound.gms
```

### Step 5: Verify Generated MCP (30 min)

Check generated stationarity equations for maximize cases:
```gams
* For maximize x with x.up = 10
* Should have: stat_x.. -1 + piU_x =E= 0
* NOT:         stat_x..  1 + piU_x =E= 0
```

### Step 6: Run Existing Tests (30 min)

```bash
make test
```

Ensure all existing minimize tests still pass.

### Step 7: Test on Original Bug Cases (30 min)

Test on the original failing cases from Sprint 5:
```bash
python -m src.main tests/fixtures/minmax_original/test2_maximize_max.gms
python -m src.main tests/fixtures/minmax_original/test4_maximize_min.gms
```

Both should now produce correct solutions.

## Regression Test Strategy

**New Test Cases to Add:**
1. `test_maximize_simple.gms` - Maximize without bounds (baseline)
2. `test_maximize_upper_bound.gms` - Critical case (triggers bug)
3. `test_maximize_lower_bound.gms` - Lower bound only
4. `test_maximize_both_bounds.gms` - Both bounds
5. `test_minimize_upper_bound.gms` - Control (verify minimize still works)

**Existing Tests to Verify:**
- All minimize test cases (test1, test3, test5, test6) must still pass
- Min/max reformulation tests with minimize objective

**Acceptance:**
- PATH solver finds correct solutions for maximize with bounds
- Generated MCP has correct stationarity equations
- No regression in minimize cases

## Files to Modify

1. **src/kkt/gradient.py** - Add gradient negation for maximize (PRIMARY CHANGE)
2. **tests/fixtures/maximize_debug/*.gms** - Already created
3. **docs/planning/EPIC_2/SPRINT_6/KKT_MAXIMIZE_THEORY.md** - Already created
4. **docs/planning/EPIC_2/SPRINT_6/MAXIMIZE_BUG_FIX_DESIGN.md** - This file

## Expected Impact

**Lines of Code Changed:** ~15 lines  
**Files Modified:** 1 Python file (gradient.py)  
**Risk Level:** LOW  
**Testing Time:** 2 hours  
**Total Implementation Time:** 2-4 hours

## Verification Checklist

- [ ] Gradient negation code added to gradient.py
- [ ] ObjSense imported correctly
- [ ] Minimal test cases pass (5 GAMS files)
- [ ] Generated MCP stationarity equations have correct signs
- [ ] PATH solver finds correct solutions for maximize
- [ ] All existing minimize tests still pass
- [ ] Original bug cases (test2_maximize_max, test4_maximize_min) fixed
- [ ] No new type errors or lint issues
- [ ] Documentation updated

## Alternative Approaches Rejected

### Why Not Option B?
- Requires changes in 2 functions
- Duplicates logic
- More maintenance burden

### Why Not Option C?
- Too invasive (affects parser and entire pipeline)
- Loses original problem formulation
- Higher risk of breaking other functionality
- Makes debugging harder

## Next Steps

1. Implement Option A in `src/kkt/gradient.py`
2. Run test suite
3. Verify with original bug cases
4. Update Sprint 6 implementation ticket
5. Proceed to Sprint 6 Day 1 implementation

## Notes

- This fix is a **prerequisite** for Sprint 6 Component 2 (Critical Bug Fixes)
- The fix should be merged before starting Sprint 6 Day 1
- Consider backporting to any release branches if needed
