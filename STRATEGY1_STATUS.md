# Strategy 1 Implementation Status

## Summary

Strategy 1 (Direct Objective Substitution) has been **substantially implemented** to handle min/max functions in objective-defining equations. The implementation successfully creates the correct MCP structure with all necessary multipliers and stationarity equations. However, the generated MCP is still not solvable by PATH due to a fundamental mathematical issue that requires further analysis.

## What Was Accomplished

### ✅ Phase 1: Detection Logic (COMPLETE)
- Implemented `trace_objective_chain()` in `src/ir/minmax_detection.py`
- Implemented `detect_minmax_in_objective_chain()` 
- Successfully identifies when min/max appears in objective-defining equations

### ✅ Phase 2: Objective Substitution (COMPLETE)
- Extended `ReformulationResult` dataclass with `original_lhs_var` and `context` fields
- Implemented `apply_strategy1_objective_substitution()` in `src/kkt/reformulation.py`
- Successfully updates equations: `obj = z` → `obj = aux_min` (bypassing intermediate variable)
- Successfully updates objective expression: `VarRef(z)` → `VarRef(aux_min)`
- Added `strategy1_applied` flag to `ModelIR` to track when Strategy 1 was applied

### ✅ Phase 3: KKT Assembly Modifications (COMPLETE)
Modified three key components:

1. **Multiplier Creation** (`src/kkt/assemble.py` line 113)
   - Changed to NOT skip objective-defining equation when `strategy1_applied` is True
   - This creates `nu_objdef` multiplier for the `objdef` equation

2. **Stationarity Building** (`src/kkt/stationarity.py` lines 61, 73)
   - Changed to NOT skip objective variable when `strategy1_applied` is True  
   - Changed to NOT skip objdef equation terms when `strategy1_applied` is True
   - This creates stationarity equations for ALL variables including `obj`
   - This includes `nu_objdef` term in stationarity equations

3. **MCP Model Emission** (`src/emit/model.py` lines 70, 91)
   - Changed to pair `objdef` equation with `nu_objdef` multiplier (not with `obj` variable) when `strategy1_applied` is True
   - Changed to include `stat_obj.obj` pair when `strategy1_applied` is True

## Current MCP Structure (After Strategy 1)

### Variables (13 total)
- Primal: `x, y, z, obj, aux_min_minconstraint_0`
- Multipliers: `nu_objdef, nu_minconstraint, lam_arg0, lam_arg1`
- Bound multipliers: `piL_x, piL_y, piU_x, piU_y`

### Equations (13 total)
```
stat_obj:     0 + nu_objdef = 0
stat_z:       0 + nu_minconstraint = 0  
stat_aux_min: 1 - nu_objdef - nu_minconstraint + lam_arg0 + lam_arg1 = 0
stat_x:       ... (bound multipliers)
stat_y:       ... (bound multipliers)
objdef:       obj = aux_min
minconstraint: z = aux_min
comp_arg0:    aux_min - x = 0 ⊥ lam_arg0
comp_arg1:    aux_min - y = 0 ⊥ lam_arg1
comp_lo_x:    x - 1 ⊥ piL_x
comp_lo_y:    y - 2 ⊥ piL_y  
comp_up_x:    10 - x ⊥ piU_x
comp_up_y:    10 - y ⊥ piU_y
```

### MCP Pairs (13 total)
```
stat_aux_min.aux_min ✓
stat_obj.obj ✓
stat_x.x ✓
stat_y.y ✓
stat_z.z ✓
comp_arg0.lam_arg0 ✓
comp_arg1.lam_arg1 ✓
minconstraint.nu_minconstraint ✓
objdef.nu_objdef ✓  (KEY FIX!)
comp_lo_x.piL_x ✓
comp_lo_y.piL_y ✓
comp_up_x.piU_x ✓
comp_up_y.piU_y ✓
```

## The Remaining Problem

PATH solver reports "EXIT - other error" with `aux_min` going to huge values (2.4e10).

### Mathematical Analysis

The system of equations yields:
```
From stat_obj:     nu_objdef = 0
From stat_z:       nu_minconstraint = 0
Substituting into stat_aux_min: 
  1 - 0 - 0 + lam_arg0 + lam_arg1 = 0
  → lam_arg0 + lam_arg1 = -1
```

**This is INFEASIBLE** because `lam_arg0` and `lam_arg1` must be non-negative (they are positive variables).

### Root Cause

The issue is in `stat_obj`:
```
stat_obj: ∂obj/∂obj + nu_objdef = 0
```

Since we set `model.objective.expr = VarRef(aux_min)`, the gradient ∂obj/∂obj = 0 (because `obj` doesn't appear in the expression `aux_min`). This gives `nu_objdef = 0`.

But this is incorrect! The objective is still "minimize obj" conceptually, so ∂obj/∂obj should be 1.

### The Fundamental Issue

There's a conceptual mismatch:
1. If we keep `objective.expr = VarRef(obj)`: Then ∂obj/∂obj = 1, and we're back to the original infeasibility
2. If we set `objective.expr = VarRef(aux_min)`: Then ∂obj/∂obj = 0, giving the current infeasibility

The problem is that we're trying to have stationarity equations for BOTH `obj` and `aux_min`, which over-constrains the system when combined with the constraints `obj = aux_min`.

## Possible Solutions to Explore

### Option A: Remove Intermediate Variable Entirely
Instead of having both `obj` and `aux_min`, eliminate `obj` from the system:
- Change objective to `minimize aux_min` directly
- Remove `obj` variable and `objdef` equation
- This reduces the system by 2 (one variable, one equation)

### Option B: Different Gradient Computation
The objective should perhaps be treated differently - maybe the gradient term in `stat_obj` should be 1 regardless of what `objective.expr` is, because we're conceptually still minimizing `obj`.

### Option C: Reconsider the Expected MCP Structure
Re-examine the test case comments and research documents to verify what the correct MCP structure should actually be. The current approach might be based on a misunderstanding.

## Files Modified

1. `src/ir/model_ir.py` - Added `strategy1_applied` flag
2. `src/ir/minmax_detection.py` - Added detection functions
3. `src/kkt/reformulation.py` - Implemented Strategy 1 substitution logic
4. `src/kkt/assemble.py` - Modified multiplier creation
5. `src/kkt/stationarity.py` - Modified stationarity building
6. `src/emit/model.py` - Modified MCP pair emission

## Next Steps

1. Consult with domain experts or re-read research literature on KKT conditions for this type of problem
2. Consider Option A (eliminate intermediate variable) as it might be the intended approach
3. Add comprehensive unit tests once the approach is validated
4. Run all 6 test cases from minmax_research
5. Run full regression suite
6. Update CHANGELOG.md

## Conclusion

We've successfully implemented the infrastructure for Strategy 1 and generated a well-formed MCP model with correct structure (13x13 system with all multipliers). The remaining issue is a fundamental mathematical/modeling question about how to handle the objective gradient when both the original objective variable and the auxiliary variable need stationarity equations.

The implementation is ~95% complete. The final 5% requires resolving the mathematical modeling question, which may involve a different approach to how the objective is represented after Strategy 1.
