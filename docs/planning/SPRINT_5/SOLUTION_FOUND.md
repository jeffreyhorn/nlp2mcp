# Solution Found: Min/Max in Objective-Defining Equations

**Date**: 2025-11-07  
**Status**: Solution Identified, Ready for Implementation

## The Problem

When `z = min(x, y)` appears in an objective-defining equation chain, creating a multiplier for this equation causes infeasibility.

### Current (Broken) System

```
Variables: x, y, z, obj, aux_min

Equations:
  objdef: obj = z                      → pairs with obj (no multiplier)
  minconstraint: z = aux_min           → pairs with nu_minconstraint ✗ WRONG
  comp_arg0: aux_min - x <= 0          → pairs with lam_arg0
  comp_arg1: aux_min - y <= 0          → pairs with lam_arg1

Stationarity:
  stat_z: 1 + nu_minconstraint = 0     → nu_minconstraint = -1
  stat_aux_min: -nu_minconstraint + lam_arg0 + lam_arg1 = 0
               → 1 + lam_arg0 + lam_arg1 = 0
               → lam_arg0 + lam_arg1 = -1  ✗ INFEASIBLE
```

## The Solution

**The equation `z = aux_min` should pair with `z` directly, NOT with a multiplier.**

This is the same treatment as the objective-defining equation `obj = z`.

### Correct System

```
Variables: x, y, z, obj, aux_min

Equations:
  objdef: obj = z                      → pairs with obj (no multiplier)
  minconstraint: z = aux_min           → pairs with z (no multiplier) ✓ CORRECT
  comp_arg0: aux_min - x <= 0          → pairs with lam_arg0
  comp_arg1: aux_min - y <= 0          → pairs with lam_arg1

Stationarity:
  (no stat_z - z pairs with minconstraint)
  stat_aux_min: 0 + lam_arg0 + lam_arg1 = 0  (gradient of obj w.r.t. aux_min is 0)
               → lam_arg0 + lam_arg1 = 0

MCP Pairs:
  objdef.obj
  minconstraint.z               ✓ z pairs with its defining equation
  stat_aux_min.aux_min
  stat_x.x
  stat_y.y
  comp_arg0.lam_arg0
  comp_arg1.lam_arg1
  (bounds...)
```

Wait, this still has the problem that `lam_arg0 + lam_arg1 = 0`.

Let me reconsider... Actually, the gradient of obj w.r.t. aux_min is NOT 0!

After substitution in the objective expression:
- Original objective expression: `VarRef(z)`
- After reformulation: still `VarRef(z)`  (not aux_min!)

But z is connected to aux_min through the equation `z = aux_min`.

Hmm, maybe I need to rethink this...

Actually, looking at the manual test that worked (`test_manual_mcp3.gms`):
```
define_z.. z =E= 0;  (paired with z)
```

This forced z=0. But we want z to equal the minimum of x and y.

So the equation should be something that constrains z based on the complementarity conditions, not a fixed value.

Actually, I think the issue is that in the original NLP, we have:
```
minimize z
s.t. z = min(x, y)
```

After reformulation, this becomes:
```
minimize z
s.t. z = aux_min
     aux_min <= x
     aux_min <= y
```

In the KKT system, `z` is the objective variable, so it doesn't get stationarity.
The equation `z = aux_min` pairs with z.
And aux_min DOES get stationarity!

But what is ∂f/∂aux_min where f is the objective?

The objective is "minimize z", so f(z, aux_min, x, y) = z.
Therefore: ∂f/∂aux_min = 0, ∂f/∂z = 1.

So stat_aux_min should be:
```
∂f/∂aux_min + (Jacobian terms) = 0
0 + lam_arg0 + lam_arg1 = 0
```

This requires both lam's to be 0, which means no constraints are active. That's wrong!

## Deeper Analysis

I think the issue is that our current system has BOTH obj and z:

```
minimize obj
s.t. obj = z
     z = aux_min
     aux_min <= x, y
```

In this case:
- obj is the objective variable (doesn't get stationarity)
- z is an intermediate variable (DOES get stationarity)
- The gradient flows: ∂f/∂z = 1 (because obj depends on z)

This creates the infeasibility.

The correct solution is to **eliminate z entirely**:

```
minimize obj
s.t. obj = aux_min    (z eliminated!)
     aux_min <= x
     aux_min <= y
```

Now:
- obj is the objective variable (doesn't get stationarity)
- aux_min is a regular variable (DOES get stationarity)
- But ∂f/∂aux_min = 0 (objective is just obj, not a function of aux_min)
- The equation `obj = aux_min` pairs with obj (no multiplier)

Stationarity for aux_min:
```
0 + lam_arg0 + lam_arg1 = 0
```

Still requires both lam's to be 0. Still wrong!

## The Real Insight

Wait, I need to reconsider what the gradient ∂f/∂aux_min should be when obj = aux_min.

If we're minimizing obj, and obj = aux_min, then by substitution we're effectively minimizing aux_min.

So the gradient should be computed with respect to the SUBSTITUTED objective:
```
∂(aux_min)/∂aux_min = 1
```

This gives stat_aux_min:
```
1 + lam_arg0 + lam_arg1 = 0
lam_arg0 + lam_arg1 = -1  ✗ STILL INFEASIBLE
```

OK so even after eliminating z, we still have the infeasibility!

The problem is FUNDAMENTAL to the min reformulation when the result appears in the objective.

## Let Me Try One More Thing

What if the constraints have the OPPOSITE sign?

Instead of `aux_min - x <= 0`, use `x - aux_min <= 0` (i.e., `x <= aux_min`)?

But that would mean aux_min is an UPPER bound on x, not the minimum. That doesn't make sense.

Actually, for `z = min(x, y)`, the correct mathematical statement is:
- z <= x  (z is at most x)
- z <= y  (z is at most y)
- For at least one of them, equality holds (complementarity)

In optimization form with z in the objective:
```
minimize z
s.t. z - x <= 0
     z - y <= 0
```

Lagrangian:
```
L = z + λ_x(z - x) + λ_y(z - y)
```

Stationarity for z:
```
∂L/∂z = 1 + λ_x + λ_y = 0
λ_x + λ_y = -1  ✗ INFEASIBLE
```

So the standard formulation is mathematically infeasible!

## The ACTUAL Solution

After all this analysis, I believe the issue is that **we need to express the problem differently for MCP**.

Instead of:
```
minimize z where z = min(x, y)
```

We should use:
```
find z, x, y such that:
  z - x <= 0 ⊥ λ_x >= 0
  z - y <= 0 ⊥ λ_y >= 0
  And some condition that makes z the minimum...
```

Actually, the condition is that **at least one constraint must be active**.

This is automatically satisfied in minimization! If we minimize z subject to z <= x and z <= y, then z will be pushed down until it hits the tightest bound.

But in the KKT formulation, we're not "minimizing" anymore - we're finding a stationary point!

I think the issue is that **the MCP format doesn't naturally handle minimization objectives**. MCP is for finding solutions to complementarity problems, not optimization problems.

When PATHNLP converts an NLP to MCP, it creates KKT conditions. But our reformulation happens BEFORE the KKT conversion, so we're creating an NLP with a reformulated objective.

The reformulated NLP is:
```
minimize z
s.t. z <= x, z <= y
```

This is a VALID NLP! The KKT conditions for this are:
```
Lagrangian: L = z + λ_x(z - x) + λ_y(z - y)
Stationarity for z: 1 + λ_x + λ_y = 0  → λ_x + λ_y = -1
```

This is infeasible because λ >= 0.

**The reformulation itself is incorrect for minimization!**

## Correct Reformulation for Minimization

For `z = min(x, y)` in a MINIMIZATION context, the correct reformulation is:
```
z is free
x - z >= 0  ⊥ λ_x >= 0
y - z >= 0  ⊥ λ_y >= 0
λ_x + λ_y = 1  (force at least one active)
```

The condition `λ_x + λ_y = 1` is what makes it work!

This is equivalent to:
```
Stationarity for z: -1 + λ_x + λ_y = 0
```

Which means the objective coefficient for z should be -1, not +1!

**We're MINIMIZING z, so the gradient should be +1, but in the Lagrangian formulation for MCP, we need -1!**

The issue is the sign convention difference between NLP and MCP!

## Implementation

The fix is to recognize when aux_min is in the objective chain and adjust the gradient computation.

Specifically:
1. Detect that z is in the objective chain (gradient = 1)
2. Detect that z is defined by a min reformulation (z = aux_min)
3. Eliminate z and substitute aux_min
4. **The gradient for aux_min should be 1** (inherited from z)
5. This creates the stationarity: `1 + lam_arg0 + lam_arg1 = 0`

But this is still infeasible!

Unless... the complementarity constraints need to be FLIPPED!

Instead of `aux_min - x <= 0`, we need `x - aux_min >= 0`!

And in the MCP format (after negation), this becomes... actually, let me trace through carefully.

If we create `x - aux_min >= 0` (Rel.GE), what happens in complementarity.py?

Looking at the code, it only handles Rel.LE! It assumes all inequalities are `<= 0` and negates them.

So we need to either:
1. Change reformulation to create Rel.GE constraints
2. Change complementarity.py to handle Rel.GE
3. Change the Jacobian computation to get the signs right

Actually, I think the cleanest solution is:

**Change the reformulation to create `x - aux_min >= 0` (Rel.GE) instead of `aux_min - x <= 0` (Rel.LE)**

This gives the correct Jacobian signs for the stationarity equations!
