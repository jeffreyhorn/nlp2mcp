# Implementation Guide: Fix Min/Max Reformulation Sign Bug

**Date**: 2025-11-07  
**Solution**: Option C - Create constraints with explicit Unary negation  
**Status**: Ready for implementation

## Problem Statement

Min/max reformulation for objective-defining equations creates infeasible MCP systems. The issue is a **sign mismatch in the Jacobian computation** that causes stationarity equations to have incorrect signs.

### Current Behavior (Broken)

For `z = min(x, y)` in the objective:

1. **Reformulation creates**: `aux_min - x <= 0` (meaning aux_min <= x)
2. **Jacobian computes**: ∂(aux_min - x)/∂aux_min = **+1**
3. **Complementarity negates**: -(aux_min - x) >= 0, which is x - aux_min >= 0 ✓
4. **Stationarity generates**: `1 + lam_x + lam_y = 0` ✗ **WRONG SIGNS**
5. **PATH reports**: Infeasible (requires lam_x + lam_y = -1, but lambdas must be >= 0)

### Expected Behavior (Correct)

Stationarity should be: `1 - lam_x - lam_y = 0`, which gives `lam_x + lam_y = 1` ✓

This was verified with a manual MCP that PATH solved successfully to x=1, y=2, aux_min=1.

## Root Cause

The transformation pipeline has a sign inconsistency:

```
Reformulation → Normalization → Jacobian → Complementarity → Stationarity
```

- **Complementarity** (src/kkt/complementarity.py:79): Negates LE constraints: `g(x) <= 0` → `-g(x) >= 0`
- **Jacobian** (src/ad/constraint_jacobian.py): Computes ∂g/∂x from the **pre-negation** form
- **Stationarity** (src/kkt/stationarity.py:444): Uses Jacobian terms directly without accounting for negation

This causes the stationarity equation to have **positive** Jacobian terms (+lam) when they should be **negative** (-lam).

## Solution: Option C - Explicit Unary Negation

Create constraints with an explicit `Unary("-", ...)` node so the Jacobian sees the negation.

### Key Insight

If we create the constraint as:
```python
lhs = Unary("-", Binary("-", arg_expr, aux_var_ref))  # -(x - aux_min)
```

Then:
1. **Constraint is**: `-(x - aux_min) <= 0`
2. **Jacobian computes**: ∂(-(x - aux_min))/∂aux_min = -(-1) = **+1** ... wait, that's still wrong!

Actually, the correct formulation is:
```python
lhs = Binary("-", arg_expr, aux_var_ref)  # x - aux_min
relation = Rel.GE  # >= 0
```

But don't let complementarity.py negate it! It's already in the correct form.

Wait, let me reconsider...

### The Actual Correct Solution

The issue is that:
- We create `aux_min - x <= 0`
- Complementarity negates to get `x - aux_min >= 0` (correct direction)
- But Jacobian computed ∂(aux_min - x)/∂aux_min = +1 (wrong sign)

The solution is to make the Jacobian compute from the **post-negation** form.

Since complementarity does: `-g(x) >= 0` for `g(x) <= 0`

The Jacobian should compute: ∂(-g)/∂x = -∂g/∂x

### Concrete Implementation

**File**: `src/kkt/reformulation.py`, function `reformulate_min()` around line 490

**Current code**:
```python
lhs = Binary("-", aux_var_ref, arg_expr)  # aux_min - x
rhs = Const(0.0)
relation = Rel.LE  # <= 0
```

**Change to**:
```python
# Create: -(x - aux_min) <= 0, which is explicitly aux_min - x <= 0
# But wrap in Unary to make the negation explicit for Jacobian
inner = Binary("-", arg_expr, aux_var_ref)  # x - aux_min
lhs = Unary("-", inner)  # -(x - aux_min) = aux_min - x
rhs = Const(0.0)
relation = Rel.LE  # <= 0
```

Wait, this doesn't help because `Unary("-", x - aux)` still evaluates to `aux - x` and the derivative is still +1.

### The REAL Solution

The problem is in **stationarity.py**, not reformulation.py!

The Jacobian correctly computes ∂(aux_min - x)/∂aux_min = +1.

But in the stationarity equation, when we add `J^T λ` terms, we need to account for the fact that complementarity **negates** the constraint.

So instead of adding `λ * ∂g/∂x`, we should add `λ * ∂(-g)/∂x = -λ * ∂g/∂x`.

## Implementation Steps

### Step 1: Track which inequalities are negated

**File**: `src/kkt/complementarity.py`

When building `comp_ineq`, track whether the constraint was negated:

```python
@dataclass
class ComplementarityPair:
    equation: EquationDef
    variable: str
    variable_indices: tuple[str, ...]
    negated: bool = False  # NEW: Track if constraint was negated
```

In `build_complementarity_pairs()` around line 77:

```python
if eq_def.relation == Rel.LE:
    # g(x) <= 0 becomes -g(x) >= 0
    F_lam = Unary("-", g_expr)
    negated = True  # NEW
elif eq_def.relation == Rel.GE:
    # g(x) >= 0 stays as g(x) >= 0
    F_lam = g_expr
    negated = False  # NEW
```

Then store in the result:
```python
comp_ineq[eq_name] = ComplementarityPair(
    equation=comp_eq,
    variable=lam_name,
    variable_indices=eq_def.domain,
    negated=negated  # NEW
)
```

### Step 2: Negate Jacobian terms for negated constraints

**File**: `src/kkt/stationarity.py`

In `_add_jacobian_transpose_terms_scalar()` around line 420:

```python
def _add_jacobian_transpose_terms_scalar(
    expr: Expr,
    jacobian,
    col_id: int,
    multipliers: dict,
    name_func,
    skip_eq: str | None,
    kkt: KKTSystem = None,  # NEW: Pass KKT to check negation status
) -> Expr:
    """Add J^T multiplier terms to the stationarity expression (scalar version).

    For each row in the Jacobian that has a nonzero entry at col_id,
    add: ∂constraint/∂x · multiplier
    
    For negated constraints (LE inequalities), negate the Jacobian term.
    """
    if jacobian.index_mapping is None:
        return expr

    # Iterate over all rows in the Jacobian
    for row_id in range(jacobian.num_rows):
        # Check if this column appears in this row
        derivative = jacobian.get_derivative(row_id, col_id)
        if derivative is None:
            continue

        # Get constraint name and indices for this row
        eq_name, eq_indices = jacobian.index_mapping.row_to_eq[row_id]

        # Skip objective defining equation (not included in stationarity)
        if skip_eq and eq_name == skip_eq:
            continue

        # Get multiplier name for this constraint
        mult_name = name_func(eq_name)

        # Check if multiplier exists
        if mult_name not in multipliers:
            continue

        # Check if this constraint was negated by complementarity
        # NEW: For negated constraints, negate the Jacobian term
        if kkt and eq_name in kkt.complementarity_ineq:
            comp_pair = kkt.complementarity_ineq[eq_name]
            if comp_pair.negated:
                derivative = Unary("-", derivative)

        # Add term: derivative * multiplier
        mult_ref = MultiplierRef(mult_name, eq_indices)
        term = Binary("*", derivative, mult_ref)
        expr = Binary("+", expr, term)

    return expr
```

### Step 3: Update all calls to pass KKT

In `stationarity.py`, update calls to `_add_jacobian_transpose_terms_scalar()` around lines 400-410:

```python
# Add J_eq^T ν terms (equality constraint multipliers)
expr = _add_jacobian_transpose_terms_scalar(
    expr, kkt.J_eq, col_id, kkt.multipliers_eq, create_eq_multiplier_name, obj_defining_eq, kkt  # NEW: Pass kkt
)

# Add J_ineq^T λ terms (inequality constraint multipliers)
expr = _add_jacobian_transpose_terms_scalar(
    expr, kkt.J_ineq, col_id, kkt.multipliers_ineq, create_ineq_multiplier_name, None, kkt  # NEW: Pass kkt
)
```

### Step 4: Revert reformulation.py to simple form

**File**: `src/kkt/reformulation.py`

Simplify back to the original simple formulation:

```python
for i, arg_expr in enumerate(min_call.args):
    # Constraint: aux_min <= arg (for min reformulation)
    # Creates: aux_min - arg <= 0
    # Complementarity will negate: -(aux_min - arg) >= 0, i.e., arg - aux_min >= 0
    # Stationarity will negate the Jacobian term to get correct signs
    constraint_name = f"minmax_min_{min_call.context}_{min_call.index}_arg{i}"

    lhs = Binary("-", aux_var_ref, arg_expr)  # aux_min - arg
    rhs = Const(0.0)

    constraint = EquationDef(
        name=constraint_name,
        domain=(),
        relation=Rel.LE,  # <= 0
        lhs_rhs=(lhs, rhs),
    )

    constraints.append((constraint_name, constraint))
```

## Testing

After implementation, test with:

```bash
cd /Users/jeff/experiments/nlp2mcp
python -m src.cli tests/fixtures/minmax_research/test1_minimize_min.gms --output /tmp/test1_final.gms
cd /tmp && gams test1_final.gms
```

**Expected result**:
- PATH solver: "EXIT - solution found"
- Solution: x=1, y=2, z=1, obj=1, aux_min=1
- Stationarity equation: `1 - lam_arg0 - lam_arg1 = 0` (negative signs)

## Summary

The fix requires **3 file changes**:

1. **src/kkt/complementarity.py**: Add `negated` field to `ComplementarityPair` and set it based on whether constraint was negated
2. **src/kkt/stationarity.py**: Check `negated` flag and negate Jacobian term for negated constraints
3. **src/kkt/reformulation.py**: Simplify to use basic `aux_min - arg <= 0` formulation

This ensures that when complementarity negates a constraint, the stationarity equation accounts for it by negating the Jacobian term, resulting in correct signs.
