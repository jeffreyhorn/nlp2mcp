# Strategy 1 Implementation - Debug Notes

## Current State

Strategy 1 has been partially implemented but the generated MCP is still infeasible.

### What Works

1. **Detection Logic** ✓
   - `trace_objective_chain()` correctly identifies objective-defining variables
   - `detect_minmax_in_objective_chain()` correctly detects min/max in chain

2. **Equation Substitution** ✓
   - Strategy 1 correctly updates `objdef: obj = z` to `objdef: obj = aux_min`
   - Intermediate variable `z` is bypassed

3. **Objective Expression Update** ✓
   - `model.objective.expr` is updated from `VarRef(z)` to `VarRef(aux_min)`
   - This ensures `∂obj/∂z = 0` (stat_z has 0 gradient term instead of 1)

### The Remaining Problem

After Strategy 1, we have:
- `objdef: obj = aux_min` 
- `minconstraint: z = aux_min`

The generated MCP has:
- `objdef.obj` (equation paired with variable)
- `minconstraint.nu_minconstraint` (equation paired with multiplier)

This creates an infeasible system:

```
stat_aux_min: 1 - nu_minconstraint + lam_arg0 + lam_arg1 = 0
stat_z:       0 + nu_minconstraint = 0
```

From stat_z: `nu_minconstraint = 0`
Substituting: `1 + lam_arg0 + lam_arg1 = 0`
But lam's are positive → **INFEASIBLE**

### Root Cause

The `objdef` equation is treated as the "objective-defining equation" and paired with the objective variable `obj` instead of getting its own multiplier `nu_objdef`.

After Strategy 1, `objdef: obj = aux_min` should be treated as a **regular equality constraint** with a multiplier, not as a special objective-defining equation.

The stationarity equation for `aux_min` should include:
```
stat_aux_min: ∂obj/∂aux_min - nu_objdef - nu_minconstraint + ...
            = 1 - nu_objdef - nu_minconstraint + lam_arg0 + lam_arg1 = 0
```

With `nu_objdef` present, the system becomes feasible:
- From stat_z: `nu_minconstraint = 0`
- From stat_aux_min: `nu_objdef = 1 + lam_arg0 + lam_arg1` (feasible since nu_objdef is free)

### Why This Happens

The KKT assembly has special handling for the "objective variable":
1. No stationarity equation is created for it (it's skipped)
2. Its defining equation is paired with the variable, not a multiplier
3. This is correct for standard NLP → MCP transformation

But after Strategy 1, this special handling is INCORRECT because:
- We want stationarity for ALL variables (including former objective variable)
- ALL equality equations should have multipliers

### Attempted Fixes

1. **Changing `model.objective.objvar`** ✗
   - Tried setting it to `aux_min` but this just shifts the problem
   - The variable that's marked as "objective" gets skipped

2. **Setting `model.objective = None`** ✗
   - Breaks gradient computation which requires an objective

3. **Current approach** (in progress)
   - Keep `model.objective.objvar = obj` (don't change it)
   - Update `model.objective.expr = VarRef(aux_min)` (fixes gradient)
   - Need to tell KKT assembly to treat objdef as regular constraint

### Proposed Solution

After Strategy 1 substitution, we need to modify the KKT assembly behavior:

**Option A: Mark the defining equation for special treatment**
- Add a flag to indicate objdef should get a multiplier
- Modify complementarity builder to create `nu_objdef` 
- Modify stationarity builder to include `nu_objdef` term

**Option B: Eliminate the objective variable concept**
- After Strategy 1, treat ALL variables equally
- Create stationarity equations for all variables (don't skip any)
- Pair ALL equality equations with multipliers (no special cases)

**Option C: Transform to feasibility problem**
- Replace `minimize obj` with `minimize aux_min`
- Remove `obj` variable entirely from the model
- This fundamentally changes the problem structure

### Files Modified

- `src/ir/minmax_detection.py` - Added detection functions
- `src/kkt/reformulation.py` - Implemented `apply_strategy1_objective_substitution()`
- Extended `ReformulationResult` dataclass

### Next Steps

1. Decide on the correct approach (A, B, or C above)
2. Modify KKT assembly to implement chosen approach
3. Test with all 6 test cases
4. Run regression suite

### Test Case

`tests/fixtures/minmax_research/test1_minimize_min.gms`

Without Strategy 1: INFEASIBLE (as expected)
With Strategy 1: STILL INFEASIBLE (needs fix)

The fix is close - we've eliminated the infeasibility in `stat_z` by making the gradient term 0. Now we just need to add the `nu_objdef` multiplier to make the system fully consistent.
