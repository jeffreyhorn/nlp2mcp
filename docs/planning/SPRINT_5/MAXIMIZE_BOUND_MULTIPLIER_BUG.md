# Maximize Bound Multiplier Sign Bug

**Date:** 2025-11-07  
**Status:** 🔴 BUG IDENTIFIED - Not yet fixed  
**Priority:** Medium (blocks maximize with min/max, but minimize works)

## Problem Summary

When using `maximize` objective (instead of `minimize`), the generated MCP has incorrect signs for bound multipliers in stationarity equations. This causes PATH solver to find infeasible or incorrect solutions.

## Symptoms

- Models with `maximize` objective fail PATH solver validation
- PATH reports infeasible solutions or converges to incorrect values
- Specifically affects models: test2_maximize_max, test4_maximize_min
- The issue is **independent** of min/max reformulation - it's a general maximize bug

## Evidence

### Test Case: test2_maximize_max.gms

**Model:**
```gams
Variables x, y, z, obj;
x.up = 10;
y.up = 20;

Equations objdef, maxconstraint;
objdef.. obj =e= z;
maxconstraint.. z =e= max(x, y);

Model test /all/;
Solve test using NLP maximizing obj;
```

**Expected Solution:**
- x = 10, y = 20, z = 20, obj = 20
- (Maximize max(x,y) means push both to their upper bounds, z = max = 20)

**Actual PATH Result:**
- z = 1440.5777 (completely wrong!)
- 3 INFEASIBLE equations
- PATH exits with "other error"

### Manual vs. Generated Comparison

**Manual Test (test2_maximize_max_manual_mcp.gms) - Line 31-32:**
```gams
stat_x.. lam_x + piL_x - piU_x =E= 0;
stat_y.. lam_y + piL_y - piU_y =E= 0;
```
Note: **Upper bound multiplier is SUBTRACTED** (`- piU_x`)

**Generated MCP (test2_maximize_max_final.gms):**
```gams
stat_x.. 0 + 0 * nu_objdef + 0 * nu_maxconstraint + 1 * lam_minmax_max_maxconstraint_0_arg0 + 0 * lam_minmax_max_maxconstraint_0_arg1 + piU_x =E= 0;
stat_y.. 0 + 0 * nu_objdef + 0 * nu_maxconstraint + 0 * lam_minmax_max_maxconstraint_0_arg0 + 1 * lam_minmax_max_maxconstraint_0_arg1 + piU_y =E= 0;
```
Note: **Upper bound multiplier is ADDED** (`+ piU_x`) - **WRONG!**

## Root Cause Analysis

### KKT Stationarity for Bounds

The correct KKT stationarity equation is:
```
∇L/∂x = ∇f/∂x + Σ(∂g/∂x · λ) + Σ(∂h/∂x · ν) - πᴸ + πᵁ = 0
```

Where:
- `πᴸ` is the **lower bound multiplier** (subtracted because bound is x ≥ L)
- `πᵁ` is the **upper bound multiplier** (added because bound is x ≤ U)

Wait, that's the formula for **minimization**. For **maximization**, the objective gradient flips sign:
```
maximize f(x)  →  minimize -f(x)
```

So for maximization:
```
∇L/∂x = -∇f/∂x + Σ(∂g/∂x · λ) + Σ(∂h/∂x · ν) - πᴸ + πᵁ = 0
```

The bound multiplier signs **do not change** with maximize vs. minimize. The issue is likely in how the stationarity equations are generated.

### Hypothesis: Bound Multiplier Sign Logic

Looking at `src/kkt/stationarity.py`, the bound multiplier signs are likely hardcoded for minimization:

```python
# Subtract π^L (lower bound multiplier)
if key in kkt.multipliers_bounds_lo:
    piL_name = create_bound_lo_multiplier_name(var_name)
    expr = Binary("-", expr, MultiplierRef(piL_name, var_indices))

# Add π^U (upper bound multiplier)
if key in kkt.multipliers_bounds_up:
    piU_name = create_bound_up_multiplier_name(var_name)
    expr = Binary("+", expr, MultiplierRef(piU_name, var_indices))
```

The signs are correct for minimization, but **the code doesn't account for maximize objective sense**.

## Investigation Needed

1. **Locate bound multiplier sign logic:** Check `src/kkt/stationarity.py` around line 410-430 (where bounds are added)
2. **Check if objective sense is available:** Does the KKT system know if it's minimize vs. maximize?
3. **Determine correct fix:**
   - Option A: Flip bound multiplier signs for maximize
   - Option B: Negate entire stationarity equation for maximize
   - Option C: Transform maximize to minimize earlier in pipeline

## Files to Investigate

1. **src/kkt/stationarity.py** - Lines ~410-430 (bound multiplier addition)
   - Function: `_build_stationarity_expr()` or similar
   - Look for `piL` and `piU` handling

2. **src/kkt/kkt_system.py** - Check if objective sense is stored
   - Does `KKTSystem` have a field for minimize/maximize?

3. **src/ir/model_ir.py** - Check how objective sense is captured from GAMS
   - Is the `Solve ... maximizing obj` directive captured?

4. **src/parser/gams_parser.py** - Check if solve statement sense is parsed
   - Does the parser extract "minimizing" vs "maximizing"?

## Expected Fix

The fix likely involves:

1. **Store objective sense** in KKTSystem or ModelIR:
   ```python
   @dataclass
   class KKTSystem:
       ...
       objective_sense: str = "minimize"  # or "maximize"
   ```

2. **Adjust bound multiplier signs** based on sense:
   ```python
   # In stationarity.py
   if objective_sense == "maximize":
       # For maximize, bound signs stay same (already correct)
       pass
   else:  # minimize
       # For minimize, bound signs are as implemented
       pass
   ```

   **OR** flip all signs:
   ```python
   if objective_sense == "maximize":
       # Flip both bound signs
       expr = Binary("+", expr, MultiplierRef(piL_name, ...))  # was -
       expr = Binary("-", expr, MultiplierRef(piU_name, ...))  # was +
   ```

3. **Test with manual MCP** to verify correct formulation

## Test Cases to Verify Fix

After fixing:
1. ✅ test2_maximize_max should find solution: x=10, y=20, z=20, obj=20
2. ✅ test4_maximize_min should find solution
3. ✅ Existing minimize tests (test1, test3, test6) should still pass
4. ✅ Create simple maximize without min/max to isolate the bound bug

## Minimal Reproduction Case

To isolate this bug from min/max reformulation, create:

```gams
* Simple maximize with bounds - no min/max
Variables x, obj;
x.up = 10;

Equations objdef;
objdef.. obj =e= x;

Model test /all/;
Solve test using NLP maximizing obj;
```

**Expected:** x = 10, obj = 10  
**If bug exists:** Incorrect signs in stationarity will cause wrong solution

## Related Issues

- This bug is **independent** of the min/max sign bug (which is now fixed)
- This bug was **masked** by working on minimize test cases first
- This bug likely affects **all maximize problems**, not just min/max

## Next Steps

1. Create minimal test case (maximize without min/max)
2. Confirm bug exists in simple case
3. Locate objective sense in IR/KKT system
4. Identify where bound multipliers are added to stationarity
5. Implement fix with objective sense awareness
6. Test on all maximize cases
7. Verify minimize cases still pass
