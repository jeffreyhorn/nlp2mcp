# Nested Min/Max Support Requirements

**Date:** 2025-11-07  
**Status:** 🔴 NOT YET IMPLEMENTED  
**Priority:** Low (edge case, but should be supported for completeness)  
**Difficulty:** Medium

## Problem Summary

The current min/max reformulation does not support nested min/max expressions like `min(x, min(y, z))` or `max(min(x, y), z)`. When encountered, the compiler throws an error.

## Current Behavior

**Test Case:** test5_nested_minmax.gms

```gams
Variables x, y, z, w, obj;
x.lo = 1; x.up = 10;
y.lo = 2; y.up = 10;
z.lo = 3; z.up = 10;

Equations objdef, nestedconstraint;
objdef.. obj =e= w;
nestedconstraint.. w =e= min(x, min(y, z));

Model test /all/;
Solve test using NLP minimizing obj;
```

**Current Error:**
```
Error: Invalid model - Differentiation not yet implemented for function 'min'. 
Supported functions: power, exp, log, sqrt, sin, cos, tan, abs. 
Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

**What Happens:**
1. Outer `min(x, min(y, z))` is detected and reformulated
2. The inner `min(y, z)` becomes an argument expression
3. When computing Jacobian derivatives, the system tries to differentiate the inner `min()` call
4. Differentiation fails because `min()` is not in the list of differentiable functions

## Why This Matters

Nested min/max is mathematically valid and occurs in real optimization problems:

**Example Use Cases:**
- `min(cost1, min(cost2, cost3))` - selecting minimum cost from multiple options
- `max(profit1, max(profit2, profit3))` - maximizing profit across alternatives
- `min(x, max(y, z))` - mixed nested operations
- Supply chain: `min(supplier1_cost, min(supplier2_cost, supplier3_cost))`
- Resource allocation: `max(machine1_output, max(machine2_output, machine3_output))`

## Mathematical Background

Nested min/max can be flattened:
```
min(x, min(y, z)) = min(x, y, z)
max(x, max(y, z)) = max(x, y, z)
min(x, max(y, z)) ≠ simplified form (must remain nested)
```

**Key Insight:** 
- Same-operation nesting (min inside min, max inside max) can be flattened
- Mixed-operation nesting (min inside max or vice versa) must be handled hierarchically

## Proposed Solution: Multi-Pass Reformulation

### Strategy: Bottom-Up Reformulation

Process nested min/max in multiple passes, starting from innermost:

**Pass 1: Detect and mark all min/max calls**
```python
# In min/max detection phase
nestedconstraint: w = min(x, min(y, z))
  ↓
Detect: 
  - Outer: min(x, min(y, z))
  - Inner: min(y, z)
Mark inner as "needs reformulation first"
```

**Pass 2: Reformulate innermost calls first**
```python
# Reformulate min(y, z) first
aux_inner = min(y, z)
  ↓ becomes ↓
aux_inner - y <= 0  (with multiplier lam_y)
aux_inner - z <= 0  (with multiplier lam_z)
```

**Pass 3: Substitute auxiliary variables**
```python
# Original: w = min(x, min(y, z))
# After inner reformulation: w = min(x, aux_inner)
  ↓
aux_outer - x <= 0  (with multiplier lam_x)
aux_outer - aux_inner <= 0  (with multiplier lam_inner)
```

**Final Result:**
```gams
Variables:
  x, y, z, w, obj
  aux_inner      # Replaces min(y, z)
  aux_outer      # Replaces min(x, min(y, z))

Equations:
  objdef.. obj =e= w
  link_w.. w =e= aux_outer
  
Complementarity Constraints:
  aux_inner - y <= 0  ⊥ lam_y
  aux_inner - z <= 0  ⊥ lam_z
  aux_outer - x <= 0  ⊥ lam_x
  aux_outer - aux_inner <= 0  ⊥ lam_inner
```

### Algorithm Outline

```python
def reformulate_nested_minmax(model_ir: ModelIR) -> ModelIR:
    """
    Reformulate nested min/max in bottom-up order.
    """
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while iteration < max_iterations:
        # Detect all min/max calls
        minmax_calls = detect_minmax_calls(model_ir)
        
        if not minmax_calls:
            break  # No more min/max to reformulate
            
        # Sort by nesting depth (innermost first)
        sorted_calls = sort_by_depth(minmax_calls)
        
        # Reformulate only the innermost level
        innermost = get_innermost_level(sorted_calls)
        
        for call in innermost:
            # Reformulate this call
            result = reformulate_min_or_max(call)
            
            # Substitute auxiliary variable in parent expressions
            substitute_in_parents(call, result.aux_var_name)
            
        iteration += 1
    
    if iteration >= max_iterations:
        raise ValueError("Nested min/max too deep (>10 levels)")
    
    return model_ir
```

### Key Implementation Details

**1. Depth Tracking**

```python
@dataclass
class MinMaxCall:
    func_type: str  # "min" or "max"
    args: list[Expr]
    context: str
    index: int
    depth: int = 0  # NEW: Track nesting depth

def calculate_depth(expr: Expr) -> int:
    """Recursively calculate nesting depth."""
    match expr:
        case Call("min" | "max", args):
            inner_depths = [calculate_depth(arg) for arg in args]
            return 1 + max(inner_depths, default=0)
        case Binary(_, left, right):
            return max(calculate_depth(left), calculate_depth(right))
        case _:
            return 0
```

**2. Expression Substitution**

After reformulating inner min/max, substitute the auxiliary variable:

```python
def substitute_call_with_var(expr: Expr, call: MinMaxCall, aux_var: str) -> Expr:
    """
    Replace a min/max call with its auxiliary variable.
    
    Example:
      min(x, min(y, z)) where min(y, z) → aux_inner
      becomes: min(x, aux_inner)
    """
    match expr:
        case Call(func, args) if matches_call(expr, call):
            return VarRef(aux_var, ())
        case Call(func, args):
            new_args = [substitute_call_with_var(arg, call, aux_var) 
                       for arg in args]
            return Call(func, new_args)
        case Binary(op, left, right):
            new_left = substitute_call_with_var(left, call, aux_var)
            new_right = substitute_call_with_var(right, call, aux_var)
            return Binary(op, new_left, new_right)
        case _:
            return expr
```

**3. Flattening Optimization (Optional)**

For same-operation nesting, flatten before reformulating:

```python
def flatten_same_operation(call: MinMaxCall) -> MinMaxCall:
    """
    Flatten nested same operations.
    
    min(x, min(y, z)) → min(x, y, z)
    max(a, max(b, c)) → max(a, b, c)
    """
    if call.func_type not in ("min", "max"):
        return call
    
    flattened_args = []
    for arg in call.args:
        if isinstance(arg, Call) and arg.func_name == call.func_type:
            # Same operation: flatten
            flattened_args.extend(arg.args)
        else:
            flattened_args.append(arg)
    
    return MinMaxCall(
        func_type=call.func_type,
        args=flattened_args,
        context=call.context,
        index=call.index,
        depth=0  # Flattened, so depth resets
    )
```

## Implementation Plan

### Phase 1: Detection Enhancement (1-2 hours)

**File:** `src/ir/minmax_detection.py`

1. Add depth calculation to MinMaxCall dataclass
2. Implement `calculate_depth()` function
3. Sort detected calls by depth
4. Add unit tests for depth calculation

**Test Cases:**
- `min(x, min(y, z))` → depths: inner=1, outer=2
- `max(max(a, b), max(c, d))` → depths: inner=1, inner=1, outer=2
- `min(x, max(y, z))` → depths: inner=1, outer=2

### Phase 2: Multi-Pass Reformulation (2-3 hours)

**File:** `src/kkt/reformulation.py`

1. Modify `apply_minmax_reformulation()` to iterate until no min/max remain
2. Process innermost calls first each iteration
3. Track which calls have been reformulated (avoid double processing)
4. Add iteration limit with error message

**Challenges:**
- Ensuring auxiliary variables don't create name collisions
- Tracking parent-child relationships for substitution
- Handling partially reformulated expressions

### Phase 3: Expression Substitution (2-3 hours)

**File:** `src/kkt/reformulation.py`

1. Implement `substitute_call_with_var()` traversal function
2. After each reformulation, update parent expressions
3. Re-parse/rebuild equation AST with substitutions
4. Validate that substitution doesn't break other parts of AST

**Challenges:**
- Immutable AST requires rebuilding, not in-place modification
- Must update equation definitions in ModelIR
- Preserve indices and domains during substitution

### Phase 4: Jacobian Handling (1-2 hours)

**File:** `src/kkt/jacobian.py`

Currently, Jacobian computation fails on nested min/max because it tries to differentiate `min()` function.

**Fix:**
- After nested reformulation, auxiliary variables replace min/max calls
- Jacobian should only see auxiliary variables, not min/max functions
- Add validation: error if min/max appears in Jacobian computation

### Phase 5: Testing (2-3 hours)

**Test Files:**
1. `tests/fixtures/minmax_research/test5_nested_minmax.gms` (already exists)
2. New: `test7_nested_same_operation.gms` - flattening test
3. New: `test8_nested_mixed_operation.gms` - mixed min/max
4. New: `test9_deeply_nested.gms` - 3+ levels of nesting

**Expected Results:**
- test5: `min(x, min(y, z))` should find x=1, y=2, z=3, w=1
- test7: `min(x, min(y, z))` flattens to `min(x, y, z)`, same result
- test8: `min(x, max(y, z))` should handle mixed operations
- test9: Deep nesting should work (within iteration limit)

## Alternative Approach: Flattening Only

**Simpler but less general:**

Only support same-operation nesting, flatten it immediately:

```python
# In detection phase
if min(x, min(y, z)) detected:
    → Flatten to min(x, y, z)
    → Reformulate as single n-way min
```

**Pros:**
- Simpler implementation
- Fewer auxiliary variables (one instead of nested)
- Cleaner MCP output

**Cons:**
- Doesn't support mixed operations: `min(x, max(y, z))`
- Less general solution

**Recommendation:** Start with flattening for same-operation, add mixed-operation support later if needed.

## Files to Modify

1. **src/ir/minmax_detection.py**
   - Add depth calculation
   - Sort calls by depth
   - Implement flattening for same-operation nesting

2. **src/kkt/reformulation.py**
   - Multi-pass reformulation loop
   - Expression substitution after each pass
   - Iteration limit and error handling

3. **src/kkt/jacobian.py**
   - Validation: min/max should not appear after reformulation
   - Error message if nested min/max reaches Jacobian computation

4. **src/ir/ast.py** (if needed)
   - Helper functions for expression traversal and substitution
   - May need `substitute()` method on Expr types

## Expected Effort

- **Flattening-only approach:** 4-6 hours
  - Simple, handles 80% of use cases
  - Just flatten same-operation nesting

- **Full multi-pass approach:** 10-15 hours
  - Comprehensive solution
  - Handles all nesting patterns
  - More complex implementation and testing

## Success Criteria

✅ test5_nested_minmax.gms generates valid MCP  
✅ PATH solver finds correct solution: x=1, y=2, z=3, w=1  
✅ Nested min/max no longer causes "function not supported" error  
✅ Generated MCP has correct number of auxiliary variables  
✅ Stationarity equations have correct signs (using Option C fix)  
✅ Existing non-nested tests still pass  

## Open Questions

1. **How deep should nesting be allowed?**
   - Suggestion: 10 levels max (iteration limit)
   - Real-world models rarely exceed 3 levels

2. **Should we flatten same-operation nesting?**
   - Yes, for efficiency and cleaner output
   - `min(x, min(y, z))` → `min(x, y, z)` has fewer variables

3. **How to handle variable bounds on auxiliary variables?**
   - Currently auxiliary variables are unbounded
   - For nested min/max: `aux_min >= min(all leaf bounds)`
   - May improve solver performance if bounds are tight

4. **Should mixed operations be supported in first iteration?**
   - Recommendation: Start with flattening-only (same-operation)
   - Add mixed-operation support in follow-up if needed
   - Test demand vs. implementation complexity

## References

- Current min/max implementation: `src/kkt/reformulation.py` lines 450-620
- Detection logic: `src/ir/minmax_detection.py`
- Research on flattening: Standard optimization textbooks (Boyd & Vandenberghe)
- Similar implementations: AMPL preprocessing, GAMS internal reformulation
