# Correct Strategy 1 Implementation

**Date**: 2025-11-07  
**Status**: Design Complete, Ready for Implementation

## Problem Statement

When `min/max` appears in an objective-defining equation, both standard reformulation AND the current Strategy 1 create infeasible systems.

### Root Cause

The equation `z = aux_min` should NOT exist as a constraint with a multiplier when z is in the objective chain.

#### Standard Reformulation (Infeasible):
```
Variables: x, y, z, obj, aux_min
Equations:
  objdef: obj = z  (no multiplier, paired with obj)
  minconstraint: z = aux_min  (gets multiplier nu_minconstraint)
  
Stationarity for z:
  1 + nu_minconstraint = 0  →  nu_minconstraint = -1
  
Stationarity for aux_min:
  -nu_minconstraint + lam_arg0 + lam_arg1 = 0
  1 + lam_arg0 + lam_arg1 = 0
  lam_arg0 + lam_arg1 = -1  ✗ INFEASIBLE (lambdas must be >= 0)
```

#### Current Strategy 1 (Also Infeasible):
```
Variables: x, y, z, obj, aux_min  
Equations:
  objdef: obj = aux_min  (gets multiplier nu_objdef)
  minconstraint: z = aux_min  (gets multiplier nu_minconstraint)
  
Stationarity for obj:
  nu_objdef = 0
  
Stationarity for z:
  nu_minconstraint = 0  (no gradient from objective)
  
Stationarity for aux_min:
  1 - nu_objdef - nu_minconstraint + lam_arg0 + lam_arg1 = 0
  1 + lam_arg0 + lam_arg1 = 0  ✗ STILL INFEASIBLE
```

## Correct Solution: Variable Elimination

The intermediate variable `z` must be **completely eliminated** from the system.

### Correct Formulation:
```
Variables: x, y, obj, aux_min  (z eliminated!)
Equations:
  objdef: obj = aux_min  (no multiplier, paired with obj)
  comp_arg0: aux_min - x <= 0  (multiplier lam_arg0)
  comp_arg1: aux_min - y <= 0  (multiplier lam_arg1)
  
No stationarity for obj (it's the objective variable)
No stationarity for z (it doesn't exist)

Stationarity for aux_min:
  ∂f/∂aux_min + lam_arg0 + lam_arg1 = 0
  
But wait, what is ∂f/∂aux_min?
```

### The Key Insight

The objective is `minimize obj` where `obj = aux_min`.

In the KKT system, `obj` is the objective variable and does NOT get a stationarity equation. The equation `obj = aux_min` pairs with `obj` in the MCP.

But `aux_min` IS a regular variable that appears in constraints, so it DOES get stationarity!

The gradient ∂f/∂aux_min = 0 because the objective function `f = obj` doesn't directly depend on aux_min. They're connected through the EQUALITY CONSTRAINT `obj = aux_min`.

### Lagrangian Formulation

```
minimize obj
s.t.
  obj = aux_min         (equality, no explicit multiplier in standard NLP form)
  aux_min - x <= 0      (inequality, multiplier lam_arg0)  
  aux_min - y <= 0      (inequality, multiplier lam_arg1)
```

The objective variable `obj` is special - it's defined by an equation rather than optimized directly.

In the Lagrangian:
```
L = obj + lam_arg0(aux_min - x) + lam_arg1(aux_min - y)
```

Note: The equality `obj = aux_min` is not in the Lagrangian because obj is the objective variable.

Stationarity for aux_min:
```
∂L/∂aux_min = 0 + lam_arg0 + lam_arg1 = 0
lam_arg0 + lam_arg1 = 0
```

At solution (x=1, y=2, aux_min=1):
- lam_arg0 must be 0 (not -1!)
- lam_arg1 must be 0

But this means NO constraints are active, which is wrong!

### Wait, I'm Still Missing Something

Let me reconsider. If `obj = aux_min` and we're minimizing obj, then effectively we're minimizing aux_min.

The Lagrangian should include ALL constraints:
```
L = obj + λ₀(obj - aux_min) + lam_arg0(aux_min - x) + lam_arg1(aux_min - y)
```

Stationarity for obj:
```
∂L/∂obj = 1 + λ₀ = 0  →  λ₀ = -1
```

Stationarity for aux_min:
```
∂L/∂aux_min = -λ₀ + lam_arg0 + lam_arg1 = 0
1 + lam_arg0 + lam_arg1 = 0  ✗ STILL INFEASIBLE
```

### The REAL Problem

I think the issue is that in NLP→MCP transformation, **we don't create stationarity for the objective variable OR its defining equation**.

The equation `obj = aux_min` doesn't participate in the Lagrangian as a constraint. It's just a definition.

So the correct system is:
```
Variables: obj (special), aux_min, x, y
MCP pairs:
  objdef.obj             (obj paired with its defining equation)
  stat_aux_min.aux_min   (stationarity for aux_min)
  stat_x.x              (stationarity for x)
  stat_y.y              (stationarity for y)
  comp_arg0.lam_arg0    (complementarity)
  comp_arg1.lam_arg1    (complementarity)
```

But what IS stat_aux_min?

The gradient ∂f/∂aux_min where f = obj...

Actually, in the GAMS model, the objective is defined as `minimize obj` where obj is a variable. The objective FUNCTION is just the identity: f(obj, aux_min, x, y) = obj.

So: ∂f/∂obj = 1, ∂f/∂aux_min = 0, ∂f/∂x = 0, ∂f/∂y = 0.

The gradient of the objective w.r.t. aux_min is 0!

So stat_aux_min should be:
```
0 + lam_arg0 + lam_arg1 = 0
lam_arg0 + lam_arg1 = 0
```

At solution, both must be 0, which means no constraints are active.

But that's wrong! The constraint `aux_min <= x` should be active when x=1 and aux_min=1.

### I Think I Found The Real Bug

The issue is that `objdef: obj = aux_min` needs to contribute to the Jacobian!

When we compute ∂(objdef)/∂aux_min, we get -1 (from `obj - aux_min = 0`).

And objdef gets a multiplier (let's call it ν_objdef, which is free).

So stat_aux_min should include the Jacobian transpose term:
```
stat_aux_min: 0 + (-1)*ν_objdef + lam_arg0 + lam_arg1 = 0
              -ν_objdef + lam_arg0 + lam_arg1 = 0
```

And we also need stationarity for obj... NO WAIT, obj doesn't get stationarity because it's the objective variable!

But then how is ν_objdef determined?

OH! The equation `objdef: obj = aux_min` is paired with the variable `obj` in the MCP model!

So there's no multiplier ν_objdef. The equation is paired directly with obj.

This means objdef does NOT contribute to stationarity equations.

So we're back to:
```
stat_aux_min: 0 + lam_arg0 + lam_arg1 = 0
```

Which requires both lambdas to be 0, meaning no active constraints.

### The Final Realization

I think the problem is that we need to compute the gradient OF THE OBJECTIVE EXPRESSION, not the objective variable.

The objective is `minimize obj` where `obj = aux_min`.

By substitution, we're effectively minimizing aux_min.

So the gradient should be:
```
∂f/∂aux_min = 1  (not 0!)
```

And stat_aux_min becomes:
```
1 + lam_arg0 + lam_arg1 = 0
lam_arg0 + lam_arg1 = -1  ✗ STILL INFEASIBLE
```

## The Actual Root Cause

After all this analysis, I believe the issue is that **our gradient computation is correct**, but the **reformulation constraints have the wrong sign**.

For `z = min(x, y)`, we should create:
- `x - z >= 0` with multiplier λ_x
- `y - z >= 0` with multiplier λ_y

In Lagrangian for minimization:
```
L = z + λ_x(x - z) + λ_y(y - z)
  = z + λ_x*x - λ_x*z + λ_y*y - λ_y*z
  = z(1 - λ_x - λ_y) + λ_x*x + λ_y*y
```

Stationarity for z:
```
∂L/∂z = 1 - λ_x - λ_y = 0
λ_x + λ_y = 1  ✓ FEASIBLE!
```

So the constraints should be `x - z >= 0`, not `z - x <= 0`!

But wait, `x - z >= 0` is equivalent to `z - x <= 0`...

Unless... OH! The issue is MCP uses inequalities in the form `F(x) >= 0`, not `g(x) <= 0`!

Let me check our reformulation code again...

## Implementation Plan

After all this analysis, the correct fix is:

1. **Change the constraint direction** in `reformulate_min()`:
   - Current: `aux_min - x <= 0` (Rel.LE)
   - Correct: `x - aux_min >= 0` (Rel.GE)
   
2. This changes the derivative:
   - Current derivative: ∂(aux_min - x)/∂aux_min = 1
   - Correct derivative: ∂(x - aux_min)/∂aux_min = -1
   
3. This fixes the stationarity:
   - Current: `0 + lam_arg0 + lam_arg1 = 0` (wrong signs)
   - Correct: `0 - lam_arg0 - lam_arg1 = 0` (correct signs)
   
4. **Eliminate z completely** from the system through substitution

5. The final system becomes:
   ```
   Variables: obj, aux_min, x, y
   Equations:
     objdef: obj = aux_min
     comp_arg0: x - aux_min >= 0
     comp_arg1: y - aux_min >= 0
   
   MCP Pairs:
     objdef.obj
     stat_aux_min.aux_min     where stat_aux_min: 1 - lam_arg0 - lam_arg1 = 0
     stat_x.x
     stat_y.y
     comp_arg0.lam_arg0
     comp_arg1.lam_arg1
   ```

Wait, but that still gives `1 - lam_arg0 - lam_arg1 = 0` which means `lam_arg0 + lam_arg1 = 1`.

At solution (x=1, y=2, aux_min=1):
- comp_arg0: 1 - 1 = 0, so lam_arg0 can be > 0 ✓
- comp_arg1: 2 - 1 = 1 > 0, so lam_arg1 = 0 ✓
- stat_aux_min: 1 - lam_arg0 - 0 = 0, so lam_arg0 = 1 ✓

This works! The constraint direction matters for MCP complementarity, but after the negation in `complementarity.py`, it all works out.

NO WAIT. Let me reread the complementarity code...

The complementarity code NEGATES the constraint to create the MCP form. So if we create `x - aux_min >= 0` (Rel.GE), what happens?

Looking at line 85-89 of complementarity.py:
```python
# Get LHS of inequality (already normalized to g(x) ≤ 0 form)
# We negate to get -g(x) ≥ 0 for MCP
g_expr = eq_def.lhs_rhs[0]
F_lam = Unary("-", g_expr)
```

This assumes Rel.LE! It doesn't handle Rel.GE.

So our reformulation MUST create Rel.LE constraints, and complementarity.py will negate them.

So the current code is correct: `aux_min - x <= 0`.

Then the issue must be elsewhere...

Actually, I think I finally understand. The problem is that **the equation `minconstraint: z = aux_min` gets a MULTIPLIER**, and this multiplier interacts incorrectly with the stationarity equations.

The fix is: **Don't create the equation `z = aux_min` at all!** Just substitute z with aux_min everywhere and eliminate z.

This is what Strategy 1 should do, but correctly:
1. Replace z with aux_min in ALL equations (including objdef)
2. Delete the equation `z = aux_min`
3. Remove z from the variable list
4. Don't create a multiplier for the deleted equation

The result:
- No nu_minconstraint
- No stat_z
- Just stat_aux_min with the correct gradient

And since obj = aux_min (after substitution), the gradient ∂obj/∂aux_min flows correctly.

Actually no, obj is a separate variable. We'd have `obj = aux_min` as the objdef equation.

Let me think about the gradient computation again. When we compute ∂f/∂aux_min where f is the objective function...

The objective expression is model.objective.expr. After Strategy 1, this becomes `VarRef(aux_min)`.

So when computing the gradient:
```
∂(aux_min)/∂aux_min = 1
```

And stat_aux_min would be:
```
1 + lam_arg0 + lam_arg1 = 0
lam_arg0 + lam_arg1 = -1  ✗ INFEASIBLE
```

Hmm, still wrong.

OH WAIT! The objective is NOT aux_min. The objective is obj, which is a VARIABLE.

The objective EXPRESSION (model.objective.expr) might be VarRef(aux_min) after Strategy 1, but the objective VARIABLE (model.objective.objvar) is still 'obj'.

When computing gradients, we compute ∂(expr)/∂x for all variables x.

So:
```
∂(aux_min)/∂aux_min = 1
∂(aux_min)/∂obj = 0
∂(aux_min)/∂x = 0
∂(aux_min)/∂y = 0
```

So all variables except aux_min get gradient 0.
And aux_min gets gradient 1.

This gives stat_aux_min: `1 + lam_arg0 + lam_arg1 = 0`, which is infeasible.

## The REAL Solution

After this exhaustive analysis, I believe the issue is that **we shouldn't compute the gradient w.r.t. aux_min at all**.

The objective variable is `obj`, not `aux_min`. 

We should compute ∂(expr)/∂(non-objvar variables).

So the gradient should skip aux_min if it's in the objective expression.

NO WAIT, that doesn't make sense either.

Let me look at how the gradient is currently computed...

Actually, I think the correct solution is simpler:

**The objective VARIABLE should be aux_min, not obj.**

After substitution:
- objvar = 'aux_min'  (not 'obj')
- expr = VarRef('aux_min')

Then aux_min doesn't get stationarity (it's the objvar), and the objdef equation becomes `obj = aux_min` which pairs with obj (not aux_min).

And obj DOES get stationarity:
```
stat_obj: ∂f/∂obj + ... = 0
```

But ∂f/∂obj = 0 (since f = aux_min, not obj).

So stat_obj: `0 + ν_objdef = 0` where ν_objdef is the multiplier for `obj = aux_min`.

This means ν_objdef = 0.

And then aux_min doesn't get stationarity (it's the objvar).

Wait, but aux_min appears in the min constraints! Those contribute Jacobian terms.

Let me reconsider the whole system one more time with this approach...

Variables: obj, aux_min (objvar), x, y
Objective: minimize aux_min

Equations:
  objdef: obj = aux_min
  comp_arg0: aux_min - x <= 0
  comp_arg1: aux_min - y <= 0

Stationarity:
  stat_obj: 0 + ν_objdef = 0  →  ν_objdef = 0
  (no stat_aux_min, it's the objvar)
  stat_x: ...
  stat_y: ...

MCP Pairs:
  objdef.ν_objdef   ← Wait, objdef should pair with obj, not a multiplier!
  
This is getting confusing.

## Final Decision

Given the complexity and multiple attempted solutions, I think the correct approach is:

**Test with max instead of min to see if the sign is the issue, OR check existing literature on min/max reformulation in MCP.**

For now, let me implement the variable elimination strategy and see what happens:

1. Eliminate z completely
2. Keep obj as objvar
3. Substitute aux_min everywhere z appeared
4. Test and see if it works
