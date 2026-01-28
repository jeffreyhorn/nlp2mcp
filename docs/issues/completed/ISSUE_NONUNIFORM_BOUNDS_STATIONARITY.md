# Issue: Non-Uniform Bound Multipliers Not Included in Indexed Stationarity Equations

**Status:** Completed  
**Category:** KKT System Assembly  
**Affected Components:** `src/kkt/assemble.py`, `src/kkt/stationarity.py`  
**Priority:** Medium  
**GitHub Issue:** [#578](https://github.com/jeffreyhorn/nlp2mcp/issues/578)

## Summary

When a variable has non-uniform bounds (different bound values for different elements, e.g., `x("i1") >= 0`, `x("i2") >= 1`), the KKT system creates per-instance scalar multipliers for the bound complementarity equations. However, these scalar multipliers are **not included** in the indexed stationarity equations, which only reference uniform bound multipliers. This results in mathematically incomplete KKT conditions.

## Background: KKT Stationarity Conditions

For an optimization problem with variable bounds, the stationarity condition is:

```
∇f(x) + J_h^T ν + J_g^T λ - π^L + π^U = 0
```

Where:
- `∇f(x)` is the gradient of the objective
- `J_h^T ν` are terms from equality constraints
- `J_g^T λ` are terms from inequality constraints  
- `π^L` are lower bound multipliers (for `x >= lo`)
- `π^U` are upper bound multipliers (for `x <= up`)

For indexed variables `x(i)`, the stationarity equation should include bound multiplier terms for **all** instances.

## Current Behavior

### Uniform Bounds (Working Correctly)

For uniform bounds (same value for all elements):
```gams
Variables x(i);
x.lo(i) = 0;  * All elements have same lower bound
```

The system creates:
- **Indexed multiplier:** `piL_x(i)` with domain `("i",)`
- **Indexed stationarity:** `stat_x(i).. ∇f - piL_x(i) + ... = 0`

This is correct - the indexed multiplier appears in the indexed stationarity.

### Non-Uniform Bounds (Problem)

For non-uniform bounds (different values per element):
```gams
Variables x(i);
x.lo("i1") = 0;
x.lo("i2") = 1;  * Different bound values
```

The system creates:
- **Scalar multipliers:** `piL_x_i1`, `piL_x_i2` (one per instance)
- **Per-instance complementarity:** `comp_lo_x_i1.. x("i1") - 0 =G= 0`
- **Indexed stationarity:** `stat_x(i).. ∇f + ... = 0` (NO bound multiplier terms!)

The scalar multipliers `piL_x_i1` and `piL_x_i2` are **not included** in `stat_x(i)`.

## Reproduction

### Minimal Test Case

```python
from src.ir.model_ir import ModelIR, ObjectiveIR, ObjSense
from src.ir.symbols import EquationDef, VariableDef, Rel
from src.ir.ast import VarRef, Const
from src.kkt.assemble import assemble_kkt_system

# Create model with non-uniform bounds
model = ModelIR()
model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

model.equations["objdef"] = EquationDef(
    name="objdef",
    domain=(),
    relation=Rel.EQ,
    lhs_rhs=(VarRef("obj", ()), VarRef("x", ("i",))),
)

model.variables["obj"] = VariableDef(name="obj", domain=())
# Non-uniform bounds: x("i1") >= 0, x("i2") >= 1
model.variables["x"] = VariableDef(
    name="x", 
    domain=("i",), 
    lo_map={("i1",): 0.0, ("i2",): 1.0}
)

model.equalities = ["objdef"]
model.sets["i"] = SetDef(name="i", members=["i1", "i2"])

# ... set up gradient and Jacobians ...
kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

# Check stationarity equation for x
stat_x = kkt.stationarity["stat_x"]
# BUG: stat_x expression does NOT contain piL_x_i1 or piL_x_i2 terms
```

### Expected Stationarity Expression

For the indexed variable `x(i)` with non-uniform bounds, the stationarity should be:

```
stat_x(i).. ∇f(i) + J^T*ν - piL_x(i) = 0
```

Where `piL_x(i)` correctly references the bound multiplier for each instance.

### Actual Stationarity Expression

```
stat_x(i).. ∇f(i) + J^T*ν = 0
```

The `-piL_x(i)` term is **missing** because the system only looks for uniform bound multipliers stored under `(var_name, ())`.

## Root Cause Analysis

### In `stationarity.py` (`_build_indexed_stationarity_expr`)

```python
# Lines 196-209: Only checks for UNIFORM bounds
has_lower_uniform = (var_name, ()) in kkt.multipliers_bounds_lo
has_upper_uniform = (var_name, ()) in kkt.multipliers_bounds_up

if has_lower_uniform:
    mult_def = kkt.multipliers_bounds_lo[(var_name, ())]
    expr = Binary("-", expr, MultiplierRef(mult_def.name, mult_def.domain))
```

The code only looks for multipliers keyed by `(var_name, ())` (uniform bounds). It does **not** iterate over per-instance multipliers like `(var_name, ("i1",))`.

### In `assemble.py` (`_create_bound_lo_multipliers`)

```python
# For non-uniform bounds, creates SCALAR multipliers per instance
mult_name = create_bound_lo_multiplier_name_indexed(var_name, inst_indices)
multipliers[(var_name, inst_indices)] = MultiplierDef(
    name=mult_name,
    domain=(),  # Scalar multiplier - empty domain
    kind="bound_lo",
    associated_constraint=var_name,
)
```

The multipliers exist but have scalar domains `()`, making them incompatible with indexed stationarity equations.

## Impact

1. **Mathematically Incomplete KKT:** The stationarity conditions are missing terms, so the MCP solution may not satisfy true KKT optimality conditions.

2. **Practical Impact Limited:** Current gamslib models use uniform bounds, so this limitation doesn't affect them. The issue only manifests with non-uniform (per-element) bounds.

3. **Complementarity Still Works:** The per-instance complementarity equations `comp_lo_x_i1.piL_x_i1` are generated correctly, so the bound constraints themselves are enforced.

## Proposed Solutions

### Option A: Per-Instance Stationarity Equations

When a variable has non-uniform bounds, generate per-instance stationarity equations instead of indexed:

```gams
stat_x_i1.. ∇f("i1") + ... - piL_x_i1 = 0;
stat_x_i2.. ∇f("i2") + ... - piL_x_i2 = 0;
```

**Pros:** Simple to implement, maintains scalar multiplier approach  
**Cons:** Increases model size, loses elegance of indexed equations

### Option B: Indexed Bound Parameters

Create indexed parameters to hold the bound values and use indexed multipliers:

```gams
Parameter lo_x(i) / i1 0, i2 1 /;
Variable piL_x(i);
Equation comp_lo_x(i);
comp_lo_x(i).. x(i) - lo_x(i) =G= 0;
stat_x(i).. ∇f(i) + ... - piL_x(i) = 0;
```

**Pros:** Maintains indexed structure, more elegant GAMS code  
**Cons:** Requires generating bound parameters, more complex assembly logic

### Option C: Conditional Bound Terms (Advanced)

Use GAMS conditional expressions to include bound terms only where bounds exist:

```gams
stat_x(i).. ∇f(i) + ... - piL_x(i)$lo_x_exists(i) = 0;
```

**Pros:** Handles sparse bounds elegantly  
**Cons:** Complex GAMS generation, may have solver compatibility issues

## Recommended Fix

**Option B (Indexed Bound Parameters)** is recommended as it:
1. Maintains the indexed structure for cleaner GAMS code
2. Properly includes bound multipliers in stationarity
3. Is mathematically correct for the KKT system

Implementation steps:
1. In `assemble.py`: When non-uniform bounds are detected, create an indexed parameter `lo_x(i)` with the bound values
2. In `assemble.py`: Create indexed multiplier `piL_x(i)` instead of scalar per-instance multipliers
3. In `complementarity.py`: Generate indexed complementarity `comp_lo_x(i).. x(i) - lo_x(i) =G= 0`
4. In `stationarity.py`: The existing uniform bound handling will work since multiplier is now indexed

## Test Case

```python
def test_nonuniform_bounds_in_stationarity():
    """Test that non-uniform bound multipliers appear in stationarity."""
    # Setup model with x(i) where x("i1") >= 0, x("i2") >= 1
    # ...
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
    
    # Stationarity should include bound multiplier terms
    stat_expr = kkt.stationarity["stat_x"].lhs_rhs[0]
    stat_str = str(stat_expr)
    
    # Should contain bound multiplier reference
    assert "piL_x" in stat_str, "Bound multiplier missing from stationarity"
```

## Related Files

- `src/kkt/assemble.py`: Creates bound multipliers, contains DESIGN NOTE
- `src/kkt/stationarity.py`: Builds stationarity equations, missing non-uniform handling
- `src/kkt/complementarity.py`: Builds complementarity pairs, handles non-uniform correctly
- `tests/integration/kkt/test_kkt_full.py`: Contains `test_indexed_bounds_assembly_nonuniform`

## Notes

The current implementation documents this as a known limitation via DESIGN NOTE comments in `assemble.py`. The limitation was introduced as a pragmatic trade-off since gamslib models use uniform bounds. However, for full KKT correctness with arbitrary bounds, this issue should be addressed.
