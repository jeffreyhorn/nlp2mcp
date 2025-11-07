# Root Cause Analysis: Min/Max in Objective-Defining Equations

**Date**: 2025-11-07  
**Issue**: Both standard reformulation AND Strategy 1 create infeasible MCP systems

## Executive Summary

Testing has revealed that BOTH approaches create infeasible systems, but for **different reasons**:

1. **Standard reformulation** (no Strategy 1): Creates impossible constraint `λ₁ + λ₂ = -1` where λ ≥ 0
2. **Strategy 1** (current implementation): Creates over-constrained system requiring `ν_objdef = 0`

The root cause is that **the equation defining the intermediate variable (e.g., `z = aux_min`) needs special treatment** when that variable appears in the objective chain.

## Test Case

```gams
Variables x, y, z, obj;
x.lo = 1; x.up = 10;
y.lo = 2; y.up = 10;

Equations objdef, minconstraint;
objdef.. obj =e= z;
minconstraint.. z =e= min(x, y);

Model test / all /;
Solve test using NLP minimizing obj;
```

**Expected solution**: x=1, y=2, z=1, obj=1

## Standard Reformulation (No Strategy 1)

### Generated System

Variables:
- Primal: x, y, z, obj, aux_min
- Multipliers: nu_minconstraint (for z = aux_min), lam_arg0, lam_arg1 (for min constraints)

Equations:
```
stat_z:       1 + nu_minconstraint = 0
stat_aux_min: -nu_minconstraint + lam_arg0 + lam_arg1 = 0
minconstraint: z = aux_min
objdef:       obj = z
```

MCP Pairs:
```
stat_z.z
stat_aux_min.aux_min
minconstraint.nu_minconstraint  ← Gets multiplier
objdef.obj
```

### Why It Fails

1. **Objective gradient flows to z**: Since obj = z, we have ∂f/∂z = 1
2. **Stationarity for z**: `stat_z: 1 + nu_minconstraint = 0` → `nu_minconstraint = -1`
3. **Stationarity for aux_min**: `stat_aux_min: -nu_minconstraint + lam_arg0 + lam_arg1 = 0`
4. **Substituting nu_minconstraint = -1**: `1 + lam_arg0 + lam_arg1 = 0` → `lam_arg0 + lam_arg1 = -1`
5. **INFEASIBLE**: Multipliers must be non-negative (lam_arg0 ≥ 0, lam_arg1 ≥ 0)

PATH reports:
```
ThrRowEqnTwoInfeasible
     stat_aux_min_minconstraint_0
     minconstraint
     stat_z
```

## Strategy 1 (Current Implementation)

### Generated System

Variables:
- Primal: x, y, z, obj, aux_min
- Multipliers: nu_objdef, nu_minconstraint, lam_arg0, lam_arg1

Equations:
```
stat_obj:     nu_objdef = 0
stat_z:       nu_minconstraint = 0  (because ∂f/∂z = 0 after substitution)
stat_aux_min: 1 - nu_objdef - nu_minconstraint + lam_arg0 + lam_arg1 = 0
objdef:       obj = aux_min  (substituted from obj = z)
minconstraint: z = aux_min
```

MCP Pairs:
```
stat_obj.obj               ← NEW: obj gets stationarity
stat_z.z
stat_aux_min.aux_min
objdef.nu_objdef           ← NEW: objdef gets multiplier
minconstraint.nu_minconstraint
```

### Why It Fails

1. **Objective substitution**: Changed `obj = z` to `obj = aux_min`, so ∂obj/∂z = 0
2. **Two stationarity equations**: Both obj and z get stationarity conditions
3. **stat_obj forces**: `nu_objdef = 0` (no other terms)
4. **stat_z forces**: `nu_minconstraint = 0` (no gradient from objective)
5. **stat_aux_min requires**: `1 + lam_arg0 + lam_arg1 = 0` → `lam_arg0 + lam_arg1 = -1`
6. **INFEASIBLE**: Same problem as standard reformulation!

The system is over-constrained: we're creating stationarity for both z AND obj, but they're connected through the reformulation.

## The Real Problem

Both approaches fail because they treat the min-reformulation equation (`z = aux_min`) as a regular equality constraint that gets a multiplier. But this equation is special:

1. **It defines a variable in the objective chain**: z appears in obj = z
2. **It's created by reformulation**: It replaces the original `z = min(x,y)`
3. **The multiplier interacts with objective gradient**: Creates the infeasibility

## The Correct Solution

The equation `z = aux_min` should be **eliminated entirely** through substitution:

### Before (Infeasible):
```
objdef:       obj = z
minconstraint: z = aux_min
```

### After (Correct):
```
objdef:       obj = aux_min    (z eliminated)
(minconstraint removed)
```

This means:
1. **No multiplier nu_minconstraint** (equation doesn't exist)
2. **No stationarity for z** (variable eliminated from system)
3. **Direct connection**: obj → aux_min → {x, y} via min constraints
4. **Clean gradient flow**: ∂f/∂aux_min = 1, no intermediate multipliers

## Implementation Strategy

The correct Strategy 1 should:

1. **Detect objective chain**: Find all variables in equations defining the objective
2. **Detect min/max in chain**: Find min/max calls that define variables in the chain
3. **Substitute throughout**: Replace the intermediate variable (z) with aux_min everywhere
4. **Remove defining equation**: Delete the equation (minconstraint) entirely
5. **Don't create multiplier**: Since equation doesn't exist, no multiplier needed
6. **Don't create stationarity for z**: Variable z is eliminated

### Correct KKT System

Variables:
- Primal: x, y, obj, aux_min (z eliminated!)
- Multipliers: lam_arg0, lam_arg1 (no nu_minconstraint!)

Equations:
```
stat_aux_min: 1 + lam_arg0 + lam_arg1 = 0     (∂f/∂aux_min = 1)
stat_x:       -lam_arg0 - piL_x + piU_x = 0
stat_y:       -lam_arg1 - piL_y + piU_y = 0
objdef:       obj = aux_min                    (z eliminated)
```

MCP Pairs:
```
stat_aux_min.aux_min
stat_x.x
stat_y.y
objdef.obj
comp_arg0.lam_arg0    (x - aux_min >= 0)
comp_arg1.lam_arg1    (y - aux_min >= 0)
```

### Solution at x=1, y=2

```
aux_min = 1               (minimum of x and y)
obj = 1                   (from objdef)
lam_arg0 > 0              (x = aux_min, active constraint)
lam_arg1 = 0              (y > aux_min, slack)
stat_aux_min: 1 + lam_arg0 + 0 = 0  →  lam_arg0 = -1... 

WAIT, THIS IS STILL WRONG!
```

## Hold On...

Even with complete elimination, we still get `stat_aux_min: 1 + lam_arg0 + lam_arg1 = 0`.

The problem is the **SIGN** in the min reformulation!

### Sign Analysis

For `z = min(x, y)`, the standard KKT stationarity should be:

```
∂L/∂z = ∂f/∂z + ∂(Lagrangian constraints)/∂z = 0
```

If z is in the objective as `minimize z`, then ∂f/∂z = 1.

The complementarity constraints are:
- x - z >= 0 with multiplier λ_x
- y - z >= 0 with multiplier λ_y

The Lagrangian is:
```
L = f(z) + λ_x(x - z) + λ_y(y - z)
```

Stationarity for z:
```
∂L/∂z = ∂f/∂z + λ_x(-1) + λ_y(-1) = 0
      = 1 - λ_x - λ_y = 0
      = λ_x + λ_y = 1  ✓ FEASIBLE!
```

At solution (x=1, y=2, z=1):
- λ_x can be 1 (active constraint)
- λ_y = 0 (slack)
- Stationarity: 1 + 0 = 1 ✓

## The Bug in Our Implementation

Looking at the generated stationarity equation:
```
stat_aux_min.. 0 + (-1) * nu_minconstraint + 1 * lam_arg0 + 1 * lam_arg1 =E= 0;
```

The signs are WRONG! The multipliers have **positive** coefficients (+1), but they should be **negative** (-1) because the constraints are `x - z >= 0` and `y - z >= 0`, which means `-z` appears in the Lagrangian.

## Root Cause

The bug is in the **Jacobian transpose computation** in `src/kkt/stationarity.py`. When computing how inequality constraints contribute to stationarity equations, the signs may be incorrect for min/max constraints.

The reformulation creates constraints:
```
comp_minmax_min_*_arg0: -(aux_min - x) >= 0    (i.e., x - aux_min >= 0)
comp_minmax_min_*_arg1: -(aux_min - y) >= 0    (i.e., y - aux_min >= 0)
```

But the derivative ∂(x - aux_min)/∂aux_min = -1, so the Jacobian transpose should give **-lam** not **+lam**.

## Next Steps

1. Check the generated constraint equations for correct form
2. Verify the Jacobian computation in stationarity.py handles signs correctly
3. Likely need to fix either:
   - The constraint generation in reformulation.py (change sign)
   - The Jacobian computation in stationarity.py (handle negation correctly)
4. Re-test both standard reformulation and Strategy 1 after sign fix
