# Min/Max in Objective-Defining Equations: Research and Reformulation Strategies

**Status:** Open Research Question  
**Priority:** Medium  
**Date:** 2025-11-03  
**Related Issue:** Min/max reformulation creates infeasible KKT system

---

## Problem Statement

The current min/max reformulation creates a mathematically infeasible system when min/max appears in an equation that *defines* the objective variable.

### Example Test Case

```gams
Variables x, y, z, obj;
Equations objective, min_constraint;

objective.. obj =e= z;
min_constraint.. z =e= min(x, y);

x.lo = 1;
y.lo = 2;

Solve model using NLP minimizing obj;
```

**Expected solution:** z* = 1 (minimum of x=1 and y=2)

### Current Reformulation (Infeasible)

The epigraph reformulation generates:

**Variables:**
- Primal: x, y, z, obj, aux_min
- Multipliers: ν_min, λ₀, λ₁

**Constraints:**
- Equality: z = aux_min
- Inequalities: aux_min ≤ x, aux_min ≤ y
- Bounds: x ≥ 1, y ≥ 2

**KKT Stationarity Conditions:**
```
∂L/∂z = 1 + ν = 0                    →  ν = -1
∂L/∂aux = -ν + λ₀ + λ₁ = 0           →  λ₀ + λ₁ = -1
```

**Problem:** Since λ₀, λ₁ ≥ 0, the equation λ₀ + λ₁ = -1 is infeasible.

### Why This Occurs

The negative multiplier ν = -1 indicates that the equality constraint z = aux is "pulling in the wrong direction" for a minimization problem. This happens because:

1. The objective is **minimize z** (pushing z DOWN)
2. The constraint z = aux tries to enforce equality
3. The constraints aux ≤ x, aux ≤ y bound aux from above
4. The KKT system detects this as impossible to satisfy

---

## Root Cause Analysis

### Key Distinction

Min/max reformulation works correctly for:
- ✅ **Constraints containing min/max:** `g(x) ≤ min(a, b)`
- ✅ **Direct objective minimization:** `minimize min(a, b)` (no intermediate variable)

But fails for:
- ❌ **Objective variable defined by min/max:** `minimize z` where `z = min(a, b)`

### Mathematical Insight

When min/max DEFINES the objective variable rather than appearing directly in the objective or constraints, the standard epigraph reformulation creates a conflict:

- The objective function gradient ∇f = [0, 0, 1, ...]ᵀ has non-zero entry for z
- The equality constraint z = aux has multiplier ν
- For minimization, ∇f and ν must have opposite signs
- But the min reformulation forces them to have the same sign
- Result: infeasibility

---

## Proposed Reformulation Strategies

### Strategy 1: Direct Objective Substitution (RECOMMENDED)

**Approach:** Replace the objective variable with the auxiliary variable directly.

**Transformation:**
```
Original:
    minimize obj
    s.t. obj = z
         z = min(x, y)

Reformulated:
    minimize aux
    s.t. obj = aux
         z = aux
         aux ≤ x
         aux ≤ y
```

**KKT Conditions:**
```
∂L/∂aux = 1 + ν_obj + ν_z + λ₀ + λ₁ = 0
```

**Analysis:**
- ν_obj and ν_z are free (can be negative)
- λ₀, λ₁ ≥ 0
- The system can balance: 1 = -(ν_obj + ν_z + λ₀ + λ₁)
- At optimum: aux = 1, one of λ₀ or λ₁ is active

**Pros:**
- Mathematically sound
- Follows standard epigraph reformulation
- Single auxiliary variable for the entire min/max chain

**Cons:**
- Requires modifying the objective formulation
- Changes the objective variable identity
- More complex implementation

### Strategy 2: Eliminate Intermediate Variable

**Approach:** Replace `z = min(x, y)` with direct constraints on z.

**Transformation:**
```
Original:
    minimize obj
    s.t. obj = z
         z = min(x, y)

Reformulated:
    minimize obj
    s.t. obj = z
         z ≤ x
         z ≤ y
```

**Rationale:**
When minimizing z, the constraint z = min(x,y) is equivalent to z ≤ x AND z ≤ y, because the objective will naturally push z down to the minimum value satisfying both constraints.

**KKT Conditions:**
```
∂L/∂z = 1 + ν_obj - λ_x - λ_y = 0
```

where λ_x is the multiplier for z ≤ x and λ_y for z ≤ y.

**Analysis:**
- At optimum: 1 + ν_obj = λ_x + λ_y
- For x = 1, y = 2: z* = 1, λ_x > 0, λ_y = 0
- This is feasible!

**Pros:**
- Simple transformation
- No auxiliary variable needed for min in objective
- Direct constraint representation

**Cons:**
- Only works for min (for max, need z ≥ x AND z ≥ y with maximization)
- Special case logic needed
- Doesn't extend to max(min(a,b), c) nested cases

### Strategy 3: Reformulate at Parse Time

**Approach:** Detect min/max in objective-defining equations during parsing and reformulate before KKT assembly.

**Transformation:**
```
Original model IR:
    equations: {
        "objective": obj = z,
        "min_constraint": z = min(x, y)
    }
    solve: minimize obj

Reformulated model IR:
    equations: {
        "objective": obj = aux,
        "constraint_0": aux ≤ x,
        "constraint_1": aux ≤ y
    }
    solve: minimize obj
```

**Implementation:**
1. Detect that z appears in objective equation
2. Find equations defining z
3. If definition contains min/max, reformulate at that level
4. Remove original z = min(...) equation
5. Replace z with aux in all uses

**Pros:**
- Clean separation of concerns
- Reformulation happens before KKT
- Can handle complex cases

**Cons:**
- Complex control flow
- Requires dependency analysis (which variables define which)
- May not handle all edge cases

### Strategy 4: Two-Phase Reformulation

**Approach:** First reformulate min/max, then detect and fix objective variable issues.

**Phase 1:** Standard min/max reformulation (current implementation)
```
z = min(x, y)  →  z = aux, aux ≤ x, aux ≤ y
```

**Phase 2:** Detect if aux appears in objective-defining chain and adjust
```
If minimize obj AND obj = z AND z = aux:
    Replace obj equation with: obj = aux
    Remove z = aux equation
    Remove z variable from system
```

**Pros:**
- Modular approach
- Can be added as post-processing step
- Handles nested cases naturally

**Cons:**
- Multiple passes over model
- Variable elimination is complex
- May miss some patterns

---

## Implementation Recommendations

### Short-Term: Detect and Error (Minimal Change)

Add validation after min/max reformulation:

```python
def validate_minmax_in_objective(model_ir: ModelIR) -> None:
    """Check if auxiliary variables appear in objective-defining equations."""
    obj_info = extract_objective_info(model_ir)
    
    if obj_info.defining_equation:
        obj_eq = model_ir.equations[obj_info.defining_equation]
        # Check if any aux variables appear in objective equation
        for aux_var_name in get_auxiliary_variable_names(model_ir):
            if appears_in_expression(aux_var_name, obj_eq.lhs_rhs):
                # Follow the dependency chain
                if creates_infeasible_system(model_ir, aux_var_name):
                    raise UnsupportedFeatureError(
                        f"Min/max in objective-defining equations not yet supported.\n"
                        f"Found: {obj_info.objvar} = ... = {aux_var_name}\n"
                        f"Workaround: Reformulate as 'minimize aux' with 'aux <= x, aux <= y'"
                    )
```

**Timeline:** 1-2 hours  
**Benefit:** Prevents incorrect results, provides helpful error message

### Medium-Term: Implement Strategy 2 (Direct Constraints)

For simple cases where min/max defines objective variable:

```python
def reformulate_minmax_in_objective(model_ir: ModelIR, min_call: MinMaxCall) -> None:
    """
    Special handling for min/max that defines the objective variable.
    
    Converts: minimize z where z = min(x, y)
    To: minimize z with z <= x, z <= y
    """
    obj_info = extract_objective_info(model_ir)
    
    # Check if this min defines the objective variable
    if is_objective_defining_minmax(model_ir, min_call):
        if min_call.func_type == "min" and obj_info.sense == ObjSense.MIN:
            # Create inequality constraints: z <= each argument
            for arg in min_call.args:
                constraint = create_inequality(
                    lhs=obj_info.objvar,  # z
                    rhs=arg,              # x or y
                    relation=Rel.LE       # z <= arg
                )
                model_ir.add_equation(constraint)
            
            # Remove the original z = min(x,y) equation
            del model_ir.equations[min_call.context]
            
        elif min_call.func_type == "max" and obj_info.sense == ObjSense.MAX:
            # Symmetric case for maximization
            ...
        else:
            raise UnsupportedFeatureError(
                "Minimizing max or maximizing min requires auxiliary variable"
            )
    else:
        # Use standard epigraph reformulation
        standard_minmax_reformulation(model_ir, min_call)
```

**Timeline:** 2-3 days  
**Benefit:** Handles common case correctly  
**Limitation:** Only works for simple min/max in objective definition

### Long-Term: Implement Strategy 1 (Full Substitution)

Comprehensive solution that handles all cases:

```python
def reformulate_minmax_comprehensive(model_ir: ModelIR) -> None:
    """
    Full min/max reformulation with objective substitution.
    
    Handles:
    - Min/max in constraints (standard epigraph)
    - Min/max in objective definition (objective substitution)
    - Nested min/max
    - Chains of definitions
    """
    # 1. Build dependency graph
    dep_graph = build_variable_dependency_graph(model_ir)
    
    # 2. Find all min/max calls
    minmax_calls = find_all_minmax_calls(model_ir)
    
    # 3. Classify each call
    for call in minmax_calls:
        if affects_objective(call, dep_graph):
            # Use objective substitution strategy
            reformulate_with_objective_substitution(model_ir, call, dep_graph)
        else:
            # Use standard epigraph reformulation
            reformulate_standard_epigraph(model_ir, call)
    
    # 4. Clean up unused variables
    eliminate_unused_variables(model_ir, dep_graph)
```

**Timeline:** 1-2 weeks  
**Benefit:** Complete solution for all cases  
**Complexity:** High - requires dependency analysis, variable elimination

---

## Research Questions

### Question 1: Is there existing literature on this?

**Investigation needed:**
- Search MCP literature for "non-smooth objectives"
- Check AMPL, GAMS, Pyomo documentation on min/max in objectives
- Review PATH solver documentation on reformulation techniques
- Look for papers on "complementarity formulations of non-smooth optimization"

**Relevant areas:**
- Non-smooth optimization → MCP conversion
- Epigraph reformulation variants
- Objective function smoothing techniques

### Question 2: How do commercial solvers handle this?

**Test with:**
- GAMS: Can it solve `minimize z` where `z = min(x,y)` directly?
- AMPL: What transformations does it apply?
- JuMP/Convex.jl: How do they reformulate min/max?

**Questions:**
- Do they reformulate automatically?
- Do they require manual reformulation?
- What error messages do they provide?

### Question 3: What about nested cases?

**Example:**
```gams
z = max(min(x, y), w)
obj = z
minimize obj
```

**Questions:**
- Does Strategy 2 (direct constraints) still work?
- Can we flatten nested min/max first?
- What's the correct MCP formulation?

### Question 4: Maximization cases

**Example:**
```gams
z = max(x, y)
obj = z
maximize obj
```

**Analysis:**
- For maximization, max in objective should work (symmetric to min in minimization)
- But min in maximization is problematic (like max in minimization)
- Need to verify both cases

---

## Testing Strategy

### Test Case 1: Simple Min in Objective (Current Failure)

```gams
Variables x, y, z, obj;
x.lo = 1; y.lo = 2;

objective.. obj =e= z;
min_constraint.. z =e= min(x, y);

Solve model using NLP minimizing obj;
```

**Expected:** z* = 1, x* = 1, y* = 2

### Test Case 2: Direct Min Objective (Should Work)

```gams
Variables x, y, obj;
x.lo = 1; y.lo = 2;

objective.. obj =e= min(x, y);

Solve model using NLP minimizing obj;
```

**Expected:** obj* = 1, x* = 1, y* = 2  
**Note:** May require different reformulation

### Test Case 3: Min in Constraint (Should Work)

```gams
Variables x, y, z, obj;
x.lo = 1; y.lo = 2;

objective.. obj =e= z;
constraint.. z =g= min(x, y) + 0.5;

Solve model using NLP minimizing obj;
```

**Expected:** z* = 1.5, min(x,y) = 1

### Test Case 4: Nested Min/Max

```gams
Variables x, y, w, z, obj;
x.lo = 1; y.lo = 2; w.lo = 1.5;

objective.. obj =e= z;
nested.. z =e= max(min(x, y), w);

Solve model using NLP minimizing obj;
```

**Expected:** z* = 1.5 (max of min(1,2)=1 and w=1.5)

### Test Case 5: Max in Maximization

```gams
Variables x, y, z, obj;
x.up = 10; y.up = 20;

objective.. obj =e= z;
max_constraint.. z =e= max(x, y);

Solve model using NLP maximizing obj;
```

**Expected:** z* = 20, y* = 20 (maximize the maximum)

---

## Success Criteria

### Minimum Viable Solution

- ✅ Detect min/max in objective-defining equations
- ✅ Provide clear error message with workaround
- ✅ All other min/max cases work correctly

### Complete Solution

- ✅ Strategy 2 implemented for simple cases
- ✅ Test cases 1-5 all pass
- ✅ Documentation of reformulation approach
- ✅ Examples in docs/examples/

### Stretch Goals

- ✅ Strategy 1 (full substitution) implemented
- ✅ Automatic detection and selection of strategy
- ✅ Support for nested min/max
- ✅ Performance benchmarks vs manual reformulation

---

## References

### Papers to Review

1. Ferris, M. C., & Pang, J. S. (1997). "Engineering and Economic Applications of Complementarity Problems"
   - Chapter on non-smooth reformulations

2. Fukushima, M., & Pang, J. S. (1999). "Convergence of a Smoothing Continuation Method for Mathematical Programs with Complementarity Constraints"
   - Smoothing approaches

3. Scholtes, S. (2001). "Introduction to Piecewise Differentiable Equations"
   - Theory of piecewise smooth functions in optimization

### Online Resources

- GAMS Documentation: MCP Model Type and Reformulation
- PATH Solver Manual: Handling Non-Smooth Functions
- NEOS Guide: Reformulation Techniques

### Code References

- AMPL min/max handling: Check ampl/mp repository
- JuMP.jl: Convex.jl package reformulations
- Pyomo: GDP (Generalized Disjunctive Programming) transformations

---

## Implementation Plan

### Phase 1: Validation (Week 1)
- [ ] Implement detection of min/max in objective-defining equations
- [ ] Add helpful error message with workaround
- [ ] Update tests to mark this case as expected failure
- [ ] Document limitation in user guide

### Phase 2: Research (Week 2)
- [ ] Literature review on non-smooth objective reformulation
- [ ] Test commercial solvers (GAMS, AMPL) on test cases
- [ ] Document findings and preferred approach
- [ ] Get community feedback on approach

### Phase 3: Simple Implementation (Week 3-4)
- [ ] Implement Strategy 2 (direct constraints) for simple cases
- [ ] Add test cases 1-3
- [ ] Verify PATH solver convergence
- [ ] Update documentation

### Phase 4: Comprehensive Solution (Month 2)
- [ ] Implement Strategy 1 (objective substitution) if needed
- [ ] Handle nested min/max cases
- [ ] Add test cases 4-5
- [ ] Performance testing and optimization

---

## Notes

- This is a fundamental limitation of applying KKT reformulation to non-smooth objectives
- The issue only manifests when min/max DEFINES the objective variable
- Other uses of min/max (in constraints, direct in objective) should work fine
- The mathematical structure is sound - it's the application that needs refinement

**Bottom Line:** This is a solvable problem that requires careful reformulation strategy selection based on where min/max appears in the model.
