# Min/Max Reformulation Bug: Spurious Lambda Variables

**GitHub Issue:** [#789](https://github.com/jeffreyhorn/nlp2mcp/issues/789)
**Issue:** Min/max reformulation creates spurious intermediate lambda variables that cause PATH solver to fail with infeasibility.

**Status:** Partially Fixed — structural fix applied (spurious lambda variables removed); mathematical reformulation for min/max in objective-defining equations remains open (#789)
**Severity:** Critical - Min/max reformulation is broken  
**Date:** 2025-11-03

---

## Problem Summary

The min/max reformulation in `src/kkt/reformulation.py` generates **two sets** of multiplier variables when it should only generate one:

1. ✅ **Correct:** `lam_comp_min_*` variables for complementarity constraints `(x - aux) >= 0`
2. ❌ **Bug:** `lambda_min_*` variables that have no purpose and create infeasibility

The spurious `lambda_min_*` variables:
- Have zero gradient (∂f/∂λ = 0)
- Don't participate in any constraints
- Create stationarity equations that force their bound multipliers to zero
- Cause PATH solver to fail with "MODEL STATUS 5 Locally Infeasible"

---

## Reproduction

### Test Case: `examples/min_max_test.gms`

```gams
Variables x, y, z, obj;
Equations objective, min_constraint;

objective.. obj =e= z;
min_constraint.. z =e= min(x, y);

x.lo = 1;
y.lo = 2;

Model min_max_nlp / objective, min_constraint / ;
Solve min_max_nlp using NLP minimizing obj ;
```

**Expected solution:** z* = 1 (minimum of x=1 and y=2)

### Generated MCP File Analysis

Running `nlp2mcp examples/min_max_test.gms` generates `min_max_test_mcp.gms` with:

#### Variables Created
```gams
Variables
    x, y, z, obj
    aux_min_min_constraint_0        ! ✅ Correct: auxiliary variable for min
    nu_min_constraint               ! ✅ Correct: multiplier for equality constraint

Positive Variables
    lambda_min_min_constraint_0_arg0        ! ❌ BUG: Spurious variable
    lambda_min_min_constraint_0_arg1        ! ❌ BUG: Spurious variable
    lam_comp_min_min_constraint_0_arg0      ! ✅ Correct: multiplier for (x - aux) >= 0
    lam_comp_min_min_constraint_0_arg1      ! ✅ Correct: multiplier for (y - aux) >= 0
    piL_x, piL_y                            ! ✅ Correct: bound multipliers
    piL_lambda_min_min_constraint_0_arg0    ! ❌ BUG: Bound multiplier for spurious var
    piL_lambda_min_min_constraint_0_arg1    ! ❌ BUG: Bound multiplier for spurious var
```

#### Stationarity Equations

**For auxiliary variable (line 79):**
```gams
stat_aux_min_min_constraint_0.. 
    0 + (-1) * nu_min_constraint 
      + 1 * lam_comp_min_min_constraint_0_arg0 
      + 1 * lam_comp_min_min_constraint_0_arg1 
    =E= 0;
```
✅ This is **correct**: `∂L/∂aux = -ν + λ₀ + λ₁ = 0`

**For spurious lambda variables (lines 80-81):**
```gams
stat_lambda_min_min_constraint_0_arg0.. 
    0 + 0 * nu_min_constraint 
      + 0 * lam_comp_min_min_constraint_0_arg0 
      + 0 * lam_comp_min_min_constraint_0_arg1 
      - piL_lambda_min_min_constraint_0_arg0 
    =E= 0;
```
❌ This is the **bug**: `0 - πᴸ = 0` forces `πᴸ = 0`, but then the complementarity condition `lambda >= 0 ⊥ πᴸ` is infeasible!

**For z variable (line 84):**
```gams
stat_z.. 
    1 + 1 * nu_min_constraint 
      + 0 * lam_comp_min_min_constraint_0_arg0 
      + 0 * lam_comp_min_min_constraint_0_arg1 
    =E= 0;
```
✅ This is **correct**: `∂f/∂z + ν = 0`, with ∂f/∂z = 1 (from objective), gives `ν = -1`

---

## PATH Solver Output Analysis

```
FINAL STATISTICS
Inf-Norm of Complementarity . .  5.1962e-01 eqn: (stat_aux_min_min_constraint_0)
Inf-Norm of Normal Map. . . . .  5.1962e-01 eqn: (stat_aux_min_min_constraint_0)

 ** EXIT - other error.

Major Iterations. . . . 116
Residual. . . . . . . . 7.089594e-01

**** MODEL STATUS      5 Locally Infeasible
```

**Infeasible Equations (from listing):**
1. `stat_aux_min_min_constraint_0`: residual 0.5196
2. `stat_z`: residual -0.5196 (should equal -1, gets -0.5196)
3. `min_constraint`: residual 0.0430

**Final Solution (infeasible):**
- `x = 1.0` ✅
- `y = 2.0` ✅
- `z = 2.5675` ❌ (should be 1.0)
- `aux_min_min_constraint_0 = 2.5244` ❌ (should be 1.0)
- `nu_min_constraint = -0.5196` ❌ (should be -1.0)

The solver cannot satisfy both:
- `stat_z`: requires `nu_min_constraint = -1`
- `stat_aux`: requires `-nu + lam₀ + lam₁ = 0`, i.e., `lam₀ + lam₁ = 1`

But the spurious `lambda_min_*` variables interfere with this system.

---

## Root Cause Analysis

### What the Code Does (Incorrect)

In `src/kkt/reformulation.py`, the `reformulate_min()` function creates:

```python
# Generate multiplier names (one per argument)
multiplier_names = []
for i in range(len(min_call.args)):
    mult_name = f"lambda_min_{min_call.context}_{min_call.index}_arg{i}"
    multiplier_names.append(mult_name)
```

Then in `reformulate_model()`:
```python
# 2. Add multiplier variables to model (all positive)
for mult_name in result.multiplier_names:
    mult_var = VariableDef(
        name=mult_name,
        domain=(),
        kind=VarKind.POSITIVE,  # Multipliers >= 0
        lo=0.0,
        up=None,
    )
    model.add_var(mult_var)
```

These `lambda_min_*` variables are added as **primal variables** to the model, which triggers:
1. Creation of stationarity equations `stat_lambda_min_*` (with zero gradient)
2. Creation of bound multipliers `piL_lambda_min_*`
3. Creation of bound complementarity constraints `comp_lo_lambda_min_*`

### What the Code Should Do (Correct)

The multipliers for the complementarity constraints `(x - aux) >= 0` **should only exist as paired MCP variables**, not as separate primal variables in the KKT system!

#### Correct Min Reformulation

For `z = min(x, y)`:

**MCP Pairs:**
```gams
Model mcp_model /
    stat_x.x,                          ! Stationarity for x
    stat_y.y,                          ! Stationarity for y
    stat_z.z,                          ! Stationarity for z
    stat_aux.aux_min,                  ! Stationarity for auxiliary variable
    (x - aux_min).lam_comp_x,          ! Complementarity: (x - aux) >= 0 ⊥ lam_x
    (y - aux_min).lam_comp_y,          ! Complementarity: (y - aux) >= 0 ⊥ lam_y
    min_constraint.nu_min,             ! Equality: z = aux
    objective.obj,                     ! Objective defining equation
    comp_lo_x.piL_x,                   ! Lower bound x >= 1
    comp_lo_y.piL_y                    ! Lower bound y >= 2
/;
```

**Variables:**
- Primal: `x, y, z, obj, aux_min` (5 variables)
- Multipliers: `lam_comp_x, lam_comp_y` (2 variables, paired with inequality constraints)
- Equality multipliers: `nu_min` (1 variable, paired with equality constraint)
- Bound multipliers: `piL_x, piL_y` (2 variables, paired with bound constraints)

**Total: 10 variables, 10 equations** ✅

#### What We Currently Generate (Wrong)

**Variables:**
- Primal: `x, y, z, obj, aux_min, lambda_min_arg0, lambda_min_arg1` ❌ (7 variables)
- Multipliers: `lam_comp_x, lam_comp_y` (2 variables)
- Equality multipliers: `nu_min` (1 variable)
- Bound multipliers: `piL_x, piL_y, piL_lambda_arg0, piL_lambda_arg1` ❌ (4 variables)

**Total: 14 variables, 14 equations** ❌

The extra `lambda_min_*` variables create:
- 2 extra stationarity equations (with zero gradient)
- 2 extra bound complementarity constraints
- 2 extra bound multiplier variables

This makes the system **over-constrained and infeasible**.

---

## Mathematical Explanation

### Correct Epigraph Reformulation

For `z = min(x, y)`, the epigraph form is:

**Complementarity conditions:**
```
(x - aux) >= 0  ⊥  λ_x >= 0
(y - aux) >= 0  ⊥  λ_y >= 0
```

**Stationarity for aux (from Lagrangian):**
```
∂L/∂aux = ∂f/∂aux - ∂h/∂aux · ν - λ_x - λ_y = 0
```

where:
- `∂f/∂aux = 0` (aux doesn't appear in objective directly)
- `∂h/∂aux = ∂(z - aux)/∂aux = -1` (from constraint `z = aux`)
- So: `0 - (-1) · ν - λ_x - λ_y = 0`
- Simplified: `ν = λ_x + λ_y`

**Key insight:** The λ variables appear **only in the stationarity equation for aux**, not as separate optimizable variables!

In MCP formulation:
- `λ_x` and `λ_y` are **paired with the inequality constraints** `(x - aux) >= 0`
- They are **not primal variables** that need their own stationarity equations
- They are **multiplier variables** that appear in the MCP pair: `equation.multiplier`

### Why Adding λ as Primal Variables Breaks the System

If we incorrectly add `λ_x` and `λ_y` as primal variables:

**Stationarity for λ_x:**
```
∂L/∂λ_x = 0 - π^L_λ_x = 0
```

This forces `π^L_λ_x = 0`.

**But the complementarity condition for the lower bound is:**
```
(λ_x - 0) >= 0  ⊥  π^L_λ_x >= 0
```

For this to be satisfied:
- Either `λ_x = 0` and `π^L_λ_x >= 0` (free)
- Or `λ_x > 0` and `π^L_λ_x = 0`

Since stationarity forces `π^L_λ_x = 0`, we must have `λ_x > 0`.

**But there's no constraint that determines what λ_x should be!** The gradient ∂L/∂λ_x = 0, so λ_x can be anything, which makes the system **underdetermined**.

Actually, looking more carefully at the PATH output, the system tries to find a solution but gets stuck because:
1. `stat_z` requires `ν = -1`
2. `stat_aux` requires `ν = λ₀ + λ₁` (from correct reformulation)
3. But `stat_aux` also incorrectly includes terms from treating λ as primal vars

This creates a contradiction that PATH cannot resolve.

---

## Fix Strategy

### Option 1: Don't Add Multipliers as Primal Variables (RECOMMENDED)

**Change in `reformulate_model()`:**

```python
# Current (WRONG):
for mult_name in result.multiplier_names:
    mult_var = VariableDef(
        name=mult_name,
        domain=(),
        kind=VarKind.POSITIVE,
        lo=0.0,
        up=None,
    )
    model.add_var(mult_var)  # ❌ This is the bug!
```

**Fixed:**
```python
# Don't add multipliers as primal variables!
# They will be created automatically when we add the complementarity constraints
# to the MCP model declaration.
```

**MCP Model Declaration:**

The multipliers should **only** appear in the MCP pairs:
```gams
Model mcp_model /
    ...,
    comp_comp_min_min_constraint_0_arg0.lam_comp_min_min_constraint_0_arg0,
    comp_comp_min_min_constraint_0_arg1.lam_comp_min_min_constraint_0_arg1,
    ...
/;
```

This tells PATH:
- `lam_comp_*` is a **paired variable** with the inequality constraint
- PATH will handle the complementarity `(x - aux) >= 0 ⊥ lam >= 0`
- **No stationarity equation needed** for lam

### Option 2: Track Multiplier Variables Separately

Add a new category to ModelIR:
```python
@dataclass
class ModelIR:
    ...
    complementarity_multipliers: set[str] = field(default_factory=set)
```

Then in `reformulate_model()`:
```python
# Mark multipliers as complementarity variables (not primal variables)
for mult_name in result.multiplier_names:
    model.complementarity_multipliers.add(mult_name)
```

Then in `build_stationarity_equations()`:
```python
# Skip complementarity multipliers when building stationarity equations
if var_name in kkt.model_ir.complementarity_multipliers:
    continue
```

This allows the multipliers to exist in the variable list (for MCP pairing) but prevents creation of stationarity equations for them.

---

## Implementation Plan

### Phase 1: Minimal Fix (Recommended)

1. **Remove primal variable creation for multipliers** in `reformulate_model()`:
   - Delete the loop that adds `lambda_min_*` / `mu_max_*` as primal variables
   - Keep only the auxiliary variable creation

2. **Keep complementarity constraint creation**:
   - The constraints `(x - aux) >= 0` are correct
   - These will be paired with multipliers in MCP model declaration

3. **Update MCP emission**:
   - Emit multiplier variable declarations in `Positive Variables` section
   - But don't add them to `model.variables` dictionary
   - Add them directly in MCP pairs: `constraint.multiplier`

### Phase 2: Proper Tracking (Future)

1. Add `complementarity_multipliers` set to ModelIR
2. Update reformulation to track these multipliers separately
3. Update stationarity builder to skip complementarity multipliers
4. Update MCP emitter to handle complementarity multipliers specially

---

## Testing Plan

1. **Fix the reformulation code**
2. **Regenerate `min_max_test_mcp.gms`**
3. **Verify variable count**:
   - Should have 10 variables (not 14)
   - Should have 10 equations (not 14)
4. **Run PATH solver**
5. **Verify solution**:
   - `x = 1.0`
   - `y = 2.0`
   - `z = 1.0`
   - `aux_min_min_constraint_0 = 1.0`
   - `nu_min_constraint = -1.0`
   - `lam_comp_min_min_constraint_0_arg0 > 0` (active)
   - `lam_comp_min_min_constraint_0_arg1 = 0` (slack)

---

## Related Issues

- This is similar to the non-convex problem issue where PATH fails to solve
- But unlike non-convex problems, this is a **code bug** not a mathematical limitation
- Once fixed, min/max reformulation should work correctly for convex problems

---

## References

- Ferris & Pang (1997): Engineering and Economic Applications of Complementarity Problems, Section 2.3.2
- GAMS Documentation: MCP Model Type (https://www.gams.com/latest/docs/UG_ModelSolve.html#UG_ModelSolve_MCP)
- PATH Solver Manual: Complementarity Pairs

---

## Next Steps

1. ✅ Document the bug (this file)
2. ⏳ Fix `reformulate_model()` to not add multipliers as primal variables
3. ⏳ Update MCP emission to handle complementarity multipliers
4. ⏳ Test with `min_max_test.gms`
5. ⏳ Add validation tests
6. ⏳ Test with other min/max examples (once available)

---

## Update 2025-11-03: Partial Fix and Remaining Issue

### Progress Made

Fixed the spurious lambda variables issue by:
1. Not adding complementarity multipliers as primal variables
2. Using standard KKT naming convention (`lam_<constraint>`)
3. Letting normal KKT assembly create multipliers
4. Fixed constraint naming to avoid double `comp_` prefix

**Result:** System now has correct structure (10 variables, 10 equations instead of 14/14)

### Remaining Issue: Mathematical Infeasibility

PATH solver now immediately detects infeasibility in three equations:
- `stat_z`: `1 + ν = 0` → `ν = -1`
- `min_constraint`: `z = aux`
- `stat_aux`: `-ν + λ₀ + λ₁ = 0` → `λ₀ + λ₁ = -1`

Since λ₀, λ₁ >= 0, the system `λ₀ + λ₁ = -1` is impossible.

### Root Cause Analysis

The issue is fundamental to how min/max appears in the objective:

**Problem:** minimize z where z = min(x, y)

**Epigraph reformulation:**
- Replace z = min(x, y) with z = aux
- Add constraints: aux <= x, aux <= y
- This creates: minimize z s.t. z = aux, aux <= x, aux <= y

**KKT Stationarity:**
- ∂L/∂z = 1 + ν = 0 → ν = -1 (negative multiplier!)
- ∂L/∂aux = -ν + λ₀ + λ₁ = 0 → λ₀ + λ₁ = ν = -1 (infeasible!)

The negative multiplier ν = -1 indicates the constraint z = aux is "pulling in the wrong direction" for a minimization problem.

### Hypothesis

The standard epigraph reformulation may not be correct for min/max that DEFINES the objective variable. The reformulation works for:
- Constraints containing min/max: `g(x) <= min(a, b)`
- Objectives directly minimizing min: `minimize min(a, b)` 

But NOT for:
- Objective variable defined by min: `minimize z` where `z = min(a, b)`

### Possible Solutions

1. **Different reformulation:** Instead of `z = aux` with `aux <= x, aux <= y`, use direct constraints `z <= x, z <= y` without auxiliary variable

2. **Reformulate at objective level:** Transform `minimize obj` where `obj = z, z = min(x,y)` into `minimize aux` with `aux <= x, aux <= y` directly

3. **Accept limitation:** Document that min/max in objective-defining equations requires manual reformulation

### Next Steps

- Research standard approaches for min/max in objective functions
- Test simpler case: `minimize min(x, y)` directly (no intermediate z variable)
- Consult MCP/PATH documentation on non-smooth objectives
- Consider whether this is a valid use case or should be rejected with helpful error

---

## Status

**Current state:** Code structure is correct, but mathematical formulation needs revision for min/max in objective-defining equations.

**Branch:** `test/minmax-path-solver-validation`

**Recommendation:** Merge structural fixes, create new issue for mathematical reformulation.
