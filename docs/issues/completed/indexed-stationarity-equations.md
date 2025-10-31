# Indexed Stationarity Equations: GAMS MCP Syntax Incompatibility

**GitHub Issue**: #47  
**Status**: Open  
**Related to**: GitHub Issue #46 (GAMS Code Generator Syntax Errors - parent issue)  
**Severity**: High  
**Affects**: Models with indexed variables (2 out of 5 test cases failing)

## Problem Summary

The current implementation generates element-specific stationarity equations (e.g., `stat_x_i1`, `stat_x_i2`) for indexed variables, but this approach is fundamentally incompatible with GAMS MCP Model declaration syntax. GAMS requires matching domains between equations and variables in Model MCP pairs, which our element-specific equations cannot provide.

## Failing Test Cases

1. **simple_nlp_mcp.gms** - Model with indexed variable `x(i)` over set `i = {i1, i2, i3}`
2. **indexed_balance_mcp.gms** - Model with indexed variable `supply(i)` over set `i = {i1, i2}`

## Current Implementation

### What We Generate Now

For an indexed variable `x(i)` where `i = {i1, i2, i3}`, we create:

**Equation Declarations:**
```gams
Equations
    stat_x_i1
    stat_x_i2
    stat_x_i3
;
```

**Equation Definitions:**
```gams
stat_x_i1.. x("i1") * 0 + a("i1") * 1 + (1 - 0) * lam_balance("i1") + ... =E= 0;
stat_x_i2.. x("i2") * 0 + a("i2") * 1 + (1 - 0) * lam_balance("i2") + ... =E= 0;
stat_x_i3.. x("i3") * 0 + a("i3") * 1 + (1 - 0) * lam_balance("i3") + ... =E= 0;
```

**Model MCP Declaration:**
```gams
Model mcp_model /
    stat_x_i1.x,
    stat_x_i2.x,
    stat_x_i3.x,
    ...
/;
```

### Why This Fails

GAMS reports the following errors:
```
****   2  Identifier expected
**** 140  Unknown symbol
**** 924  Equation and variable list in model statement expect | as separator
****  39  Colon ':' expected
**** 142  No suffix allowed here - suffix ignored
```

The root cause: **`x` is declared as `x(i)` (an indexed variable), but we're trying to pair it with scalar equations `stat_x_i1`, `stat_x_i2`, etc.**

GAMS Model MCP syntax requires:
- For scalar equation + scalar variable: `equation.variable` ✓
- For indexed equation + indexed variable: `equation(i).variable(i)` ✓
- For element-specific scalar equation + indexed variable: **INVALID** ✗

Our attempt `stat_x_i1.x` is invalid because:
1. `stat_x_i1` is a scalar equation (no domain)
2. `x` is an indexed variable (domain `i`)
3. GAMS has no way to understand which instance of `x` to pair with `stat_x_i1`

## Required Solution

We need to generate **indexed stationarity equations with domains**, not element-specific equations.

### Target Output

**Equation Declarations:**
```gams
Equations
    stat_x(i)
;
```

**Equation Definition:**
```gams
stat_x(i).. <gradient_expr(i)> + <jacobian_terms(i)> - piL_x(i) + piU_x(i) =E= 0;
```

**Model MCP Declaration:**
```gams
Model mcp_model /
    stat_x(i).x(i),
    ...
/;
```

### Key Challenges

The difficulty lies in building the stationarity expression with the correct set index instead of element labels.

**Current approach** (per-element):
```
For element i1:
  grad_x_i1 + J[0,0] * lam_bal_i1 + J[1,0] * lam_bal_i2 + J[2,0] * lam_bal_i3 = 0
```

**Required approach** (indexed):
```
For set index i:
  grad_x(i) + sum(j, J(j,i) * lam_bal(j)) = 0
```

This requires:
1. Detecting when multiple element-specific equations can be collapsed into one indexed equation
2. Determining the parent set for element labels (e.g., `i1` → set `i`)
3. Rebuilding expressions to use set indices instead of element labels
4. Converting explicit sums over elements to GAMS `sum()` operators
5. Handling Jacobian transpose terms with proper index matching

## Technical Details

### Current Code Flow

1. **Index Mapping** (`src/ad/index_mapping.py`):
   - Maps variable instances to column IDs: `(x, (i1,))` → col 0, `(x, (i2,))` → col 1, etc.
   - Stores element labels like `("i1",)` as tuples

2. **Stationarity Building** (`src/kkt/stationarity.py:build_stationarity_equations()`):
   ```python
   for col_id in range(kkt.gradient.num_cols):
       var_name, var_indices = index_mapping.col_to_var[col_id]
       # var_indices = ("i1",) for first instance
       
       stat_expr = _build_stationarity_expr(kkt, col_id, var_name, var_indices, ...)
       stat_name = _create_stationarity_name(var_name, var_indices)  # "stat_x_i1"
       
       stationarity[stat_name] = EquationDef(
           name=stat_name,
           domain=(),  # Empty domain - this is the problem!
           relation=Rel.EQ,
           lhs_rhs=(stat_expr, Const(0.0))
       )
   ```

3. **Expression Building** (`_build_stationarity_expr()`):
   - Creates expressions with explicit element labels
   - Example: `lam_balance("i1")`, `x("i2")`
   - All Jacobian terms are explicitly enumerated

4. **Model MCP Emission** (`src/emit/model.py`):
   - Tries to pair `stat_x_i1.x` but this is invalid GAMS syntax

### Proposed Refactoring

#### Phase 1: Detect Indexable Stationarity Equations

Group element-specific equations that can be collapsed:
```python
def _group_stationarity_by_variable(kkt: KKTSystem) -> dict[str, list[tuple[int, tuple[str, ...]]]]:
    """Group variable instances by base variable name.
    
    Returns:
        {var_name: [(col_id, indices), ...]}
        
    Example:
        {"x": [(0, ("i1",)), (1, ("i2",)), (2, ("i3",))],
         "y": [(3, ())]}  # y is scalar
    """
```

#### Phase 2: Determine Parent Sets

Map element labels to their parent sets:
```python
def _get_parent_set(var_name: str, model_ir: ModelIR) -> tuple[str, ...]:
    """Get the domain sets for a variable.
    
    For variable x(i), returns ("i",)
    For variable z(i,j), returns ("i", "j")
    For scalar y, returns ()
    """
    var_def = model_ir.variables[var_name]
    return var_def.domain
```

#### Phase 3: Build Indexed Expressions

Convert element-specific expressions to indexed:
```python
def _build_indexed_stationarity_expr(
    kkt: KKTSystem,
    var_name: str,
    set_indices: tuple[str, ...],  # ("i",) not ("i1",)
    col_ids: list[int]
) -> Expr:
    """Build stationarity expression using set indices.
    
    Key difference: Use set index 'i' instead of element labels 'i1', 'i2', etc.
    
    Challenges:
    - Gradient component: Need ∂f/∂x(i) with symbolic index i
    - Jacobian terms: Need J(j,i) with proper index matching
    - Bound multipliers: Need π^L(i), π^U(i)
    """
```

This requires fundamental changes to how we represent and manipulate derivatives.

#### Phase 4: Handle Jacobian Transpose with Indices

Convert explicit Jacobian sums to GAMS `sum()` operators:
```python
# Current (element-specific):
# J[0,0] * lam(i1) + J[1,0] * lam(i2) + J[2,0] * lam(i3)

# Required (indexed):
# sum(j, J_partial(j,i) * lam(j))
```

This is particularly challenging because:
1. We need to detect when a sum over elements can become a set sum
2. Jacobian entries are stored per-element, not symbolically
3. GAMS `sum()` syntax requires proper index variable names

## Impact Assessment

### What Works Now

- **Scalar variables** (no indices): `stat_x.x` ✓
- **Variables with bounds** (scalar or indexed): Bound equations work ✓
- **Inequality/equality complementarities** (indexed): `comp_balance(i).lam_balance(i)` ✓

### What Doesn't Work

- **Indexed variables without bounds**: Stationarity equations invalid ✗
- **Any model with `x(i)` where `i` has multiple elements**: Invalid Model MCP syntax ✗

### Workarounds (None Viable)

1. ❌ **Declare multiple scalar variables** (`x_i1`, `x_i2`, ...): Changes user's model structure
2. ❌ **Use subset syntax**: GAMS doesn't support element-specific subsets in this context
3. ❌ **Skip stationarity for indexed variables**: Violates KKT conditions

## Files Requiring Changes

1. **`src/kkt/stationarity.py`**:
   - `build_stationarity_equations()`: Main refactoring needed
   - `_build_stationarity_expr()`: Must use set indices
   - `_add_jacobian_transpose_terms()`: Generate `sum()` expressions
   - New helper functions for grouping and index detection

2. **`src/emit/model.py`**:
   - `emit_model_mcp()`: Simplified - indexed equations naturally work
   - Remove element-specific handling code

3. **`src/ad/index_mapping.py`**:
   - May need extensions to track set-to-elements mappings
   - Currently only stores element labels, not parent sets

4. **`src/ir/ast.py`**:
   - May need new AST nodes for `sum()` aggregation over sets
   - Currently `Sum` node only handles specific expressions

5. **`src/emit/expr_to_gams.py`**:
   - Handle emission of indexed expressions with set variables
   - Remove element label quoting logic (no longer needed for this case)

## Testing Strategy

### Phase 1: Scalar Variables (Baseline)

Ensure existing scalar variable tests still pass:
- `scalar_nlp_mcp.gms` ✓ (already passing)
- `bounds_nlp_mcp.gms` ✓ (already passing)

### Phase 2: Simple Indexed Variables

Fix the failing tests:
- `simple_nlp_mcp.gms`: Single indexed variable `x(i)`
- Target: `stat_x(i).x(i)` in Model MCP

### Phase 3: Complex Indexed Models

Extend to more complex cases:
- `indexed_balance_mcp.gms`: Multiple indexed variables
- Models with 2D indices: `z(i,j)`
- Mixed scalar and indexed variables

### Phase 4: Edge Cases

- Empty sets (no elements)
- Single-element sets (could use scalar syntax)
- Alias sets
- Multiple variables sharing the same domain

## Estimated Effort

**Complexity**: High  
**Estimated Time**: 2-3 days of focused work  
**Risk**: Medium (requires careful handling of symbolic vs. concrete indices)

**Breakdown**:
- Phase 1 (Grouping & Detection): 4 hours
- Phase 2 (Parent Set Mapping): 2 hours
- Phase 3 (Indexed Expression Building): 8-12 hours (most complex)
- Phase 4 (Jacobian Sum Generation): 6-8 hours
- Testing & Debugging: 6-8 hours
- Documentation: 2 hours

**Total**: 28-36 hours

## Alternative Approaches

### Option 1: Symbolic Derivatives with Index Variables (Recommended)

Represent derivatives symbolically with index variables instead of computing them per-element.

**Pros**:
- Cleaner, more maintainable code
- Naturally produces indexed equations
- More efficient for large sets

**Cons**:
- Requires significant refactoring of AD system
- Current AD system assumes concrete element evaluation

### Option 2: Post-Processing Consolidation

Generate element-specific equations as now, then consolidate them into indexed equations as a post-processing step.

**Pros**:
- Minimal changes to existing AD system
- Can detect patterns in generated code

**Cons**:
- Complex pattern matching required
- Fragile - relies on recognizing code patterns
- May not handle all edge cases

### Option 3: Hybrid Approach (Recommended)

Keep element-based AD for derivatives, but generate indexed equations for emission:

1. Compute gradients/Jacobians per-element (current approach)
2. Group element-specific results by parent variable
3. Generate indexed equations using pattern matching on Jacobian structure
4. Emit GAMS code with proper `sum()` operators

**Pros**:
- Balances implementation complexity with maintainability
- Reuses existing AD infrastructure
- Focused changes in emission layer

**Cons**:
- Still requires careful pattern matching
- May be inefficient for very large sets

## Recommended Path Forward

**Approach**: Hybrid (Option 3)

**Implementation Plan**:

1. **Week 1**: Detection and grouping
   - Implement `_group_stationarity_by_variable()`
   - Map element labels to parent sets
   - Write unit tests for grouping logic

2. **Week 2**: Expression generation
   - Implement `_build_indexed_stationarity_expr()`
   - Generate Jacobian sum expressions
   - Handle gradient indexing

3. **Week 3**: Integration and testing
   - Update Model MCP emission
   - Fix golden files
   - Comprehensive testing

## References

- **GAMS Documentation**: [Model Classification](https://www.gams.com/latest/docs/UG_ModelSolve.html#UG_ModelSolve_ModelClassificationOfModels)
- **GAMS MCP**: [PATH Solver Documentation](https://www.gams.com/latest/docs/S_PATH.html)
- **Current Issue**: GitHub #46 - GAMS Code Generator Syntax Errors
- **Related Code**: `src/kkt/stationarity.py`, `src/emit/model.py`

## Appendix: Example Comparison

### Current Output (Invalid)

```gams
Sets
    i /i1, i2, i3/ ;

Variables
    x(i) ;

Equations
    stat_x_i1
    stat_x_i2
    stat_x_i3 ;

stat_x_i1.. x("i1") + lam("i1") =E= 0;
stat_x_i2.. x("i2") + lam("i2") =E= 0;
stat_x_i3.. x("i3") + lam("i3") =E= 0;

Model mcp_model /
    stat_x_i1.x,      ← INVALID: x is indexed, stat_x_i1 is scalar
    stat_x_i2.x,      ← INVALID
    stat_x_i3.x       ← INVALID
/;
```

### Required Output (Valid)

```gams
Sets
    i /i1, i2, i3/ ;

Variables
    x(i) ;

Equations
    stat_x(i) ;

stat_x(i).. x(i) + lam(i) =E= 0;

Model mcp_model /
    stat_x(i).x(i)    ← VALID: Both indexed with matching domain
/;
```

## Questions for Discussion

1. Should we support mixed approaches (indexed + element-specific in same model)?
2. How do we handle models with very large sets (memory/performance)?
3. Should element-specific equations be available as an option for debugging?
4. What's the best way to represent symbolic indices in the AST?

---

**Document Version**: 1.0  
**Last Updated**: 2025-10-30  
**Author**: Claude (via nlp2mcp development)
