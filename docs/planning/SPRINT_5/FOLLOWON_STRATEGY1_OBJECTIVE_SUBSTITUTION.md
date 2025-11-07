# Follow-On Task: Strategy 1 - Direct Objective Substitution for Min/Max in Objective-Defining Equations

**Created:** November 6, 2025  
**Priority:** High  
**Estimated Effort:** 6-8 hours  
**Dependencies:** Sprint 5 Day 2 completion  
**Complexity:** Medium-High  

## Executive Summary

Implement Strategy 1 (Direct Objective Substitution) to handle min/max functions that appear in objective-defining equation chains. This resolves the mathematical infeasibility that occurs when the standard epigraph reformulation is applied to such cases.

**Current Status:** The reformulation infrastructure creates correct auxiliary variables and constraints, but generates mathematically infeasible KKT systems when min/max defines the objective variable through an equation chain.

**Goal:** Transform models like `minimize obj` where `obj = z` and `z = min(x,y)` into solvable MCP systems by substituting the objective variable with the auxiliary variable directly.

## Background

### The Problem

When min/max appears in an equation that defines the objective variable (rather than directly in the objective or a regular constraint), the standard KKT reformulation creates an over-constrained system:

**Example:**
```gams
minimize obj
obj = z          * Objective-defining equation
z = min(x, y)    * Min/max in the chain
```

**Current Reformulation Produces:**
```
Variables: obj, z, aux_min, nu_objdef, nu_minconstraint, lam_x, lam_y

Equations:
  obj = z                           * Original objective definition
  z = aux_min                       * Transformed min equation
  aux_min <= x, aux_min <= y        * Min inequalities

Stationarity:
  ∂L/∂obj = 1 + nu_objdef = 0           →  nu_objdef = -1
  ∂L/∂z = -nu_objdef + nu_minconstraint = 0  →  nu_minconstraint = -1
  ∂L/∂aux = -nu_minconstraint - lam_x - lam_y = 0  →  1 = lam_x + lam_y
```

**Problem:** The constant `1` from the objective gradient cannot be balanced by non-negative multipliers. System is **mathematically infeasible**.

### What is Strategy 1?

Strategy 1 (Direct Objective Substitution) resolves this by:

1. **Detecting** when min/max appears in the objective-defining equation chain
2. **Substituting** the objective variable with the auxiliary variable
3. **Eliminating** the intermediate variable from the objective path
4. **Updating** the objective function to use the auxiliary variable directly

**Transformation:**
```
BEFORE (Infeasible):
  minimize obj
  obj = z
  z = min(x, y)  →  z = aux_min with aux_min <= x, aux_min <= y

AFTER (Feasible):
  minimize aux_min           * Direct substitution
  obj = aux_min              * Updated equality
  aux_min <= x, aux_min <= y * Reformulation constraints
```

**Result:** The auxiliary variable becomes the objective directly, eliminating the stationarity conflict.

## Implementation Strategy

### Phase 1: Detection (2-3 hours)

Implement logic to detect when min/max appears in an objective-defining equation chain.

#### Step 1.1: Define Objective-Defining Chain
**File:** `src/ir/minmax_detection.py`

Add function to trace the dependency chain from objective variable:

```python
def trace_objective_chain(model_ir: ModelIR) -> set[str]:
    """
    Trace all variables involved in defining the objective.
    
    Returns set of variable names that are part of the objective-defining chain.
    
    Example:
        minimize obj where obj = z and z = x + y
        Returns: {'obj', 'z'}
    """
    if not model_ir.objective:
        return set()
    
    obj_var = model_ir.objective.objvar
    chain = {obj_var}
    
    # Build reverse dependency map: var -> equations that define it
    definitions = build_variable_definitions(model_ir)
    
    # BFS to find all variables in the chain
    to_visit = [obj_var]
    visited = set()
    
    while to_visit:
        var = to_visit.pop(0)
        if var in visited:
            continue
        visited.add(var)
        
        # Find equation that defines this variable
        if var in definitions:
            defining_eq = definitions[var]
            # Extract all variables from the RHS
            rhs_vars = extract_variables(defining_eq.rhs)
            for rhs_var in rhs_vars:
                if rhs_var not in visited:
                    chain.add(rhs_var)
                    to_visit.append(rhs_var)
    
    return chain
```

**Test Cases:**
- Simple chain: `obj = z`, `z = min(x,y)` → Returns `{obj, z}`
- No chain: `obj = min(x,y)` directly → Returns `{obj}`
- Multiple hops: `obj = a`, `a = b`, `b = min(x,y)` → Returns `{obj, a, b}`

#### Step 1.2: Detect Min/Max in Objective Chain
**File:** `src/ir/minmax_detection.py`

```python
def detect_minmax_in_objective_chain(model_ir: ModelIR) -> list[tuple[str, str, str]]:
    """
    Detect min/max calls in objective-defining equations.
    
    Returns list of (equation_name, var_name, func_type) tuples where:
    - equation_name: The equation containing min/max
    - var_name: The objective-chain variable being defined
    - func_type: 'min' or 'max'
    
    Example:
        minimize obj where obj = z and z = min(x, y)
        Returns: [('eq_z', 'z', 'min')]
    """
    obj_chain = trace_objective_chain(model_ir)
    results = []
    
    for eq_name, eq_def in model_ir.equations.items():
        # Check if LHS is a simple variable in the objective chain
        if isinstance(eq_def.lhs, VarRef) and eq_def.lhs.name in obj_chain:
            # Check if RHS contains min/max
            if contains_minmax(eq_def.rhs):
                minmax_calls = find_minmax_calls(eq_def.rhs, context=eq_name)
                for call in minmax_calls:
                    results.append((eq_name, eq_def.lhs.name, call.func_type))
    
    return results
```

**Test Cases:**
- Direct: `obj = min(x,y)` → Returns `[('objdef', 'obj', 'min')]`
- Chain: `z = min(x,y)` where z in obj chain → Returns `[('eq_z', 'z', 'min')]`
- No match: `z = min(x,y)` where z NOT in obj chain → Returns `[]`

#### Step 1.3: Add Detection to Pipeline
**File:** `src/cli.py`

Add detection before reformulation:

```python
# After normalize, before reformulate
if verbose >= 2:
    click.echo("Checking for min/max in objective-defining equations...")

minmax_in_obj_chain = detect_minmax_in_objective_chain(model)

if minmax_in_obj_chain:
    if verbose >= 2:
        for eq_name, var_name, func_type in minmax_in_obj_chain:
            click.echo(f"  Found {func_type}() defining objective variable '{var_name}' in equation '{eq_name}'")
```

### Phase 2: Objective Substitution (3-4 hours)

Implement the actual substitution logic.

#### Step 2.1: Extend Reformulation Result
**File:** `src/kkt/reformulation.py`

Update the reformulation result structure to include auxiliary variable mapping:

```python
@dataclass
class MinMaxReformulationResult:
    """Result of reformulating a single min/max call."""
    replacement_expr: Expr  # The aux variable reference
    aux_var_name: str       # Name of auxiliary variable
    inequality_constraints: list[tuple[str, EquationDef]]  # (name, equation) pairs
    func_type: str          # 'min' or 'max'
    context: str            # Equation name where this appeared
    original_lhs_var: str | None = None  # If this defined a variable, which one?
```

#### Step 2.2: Implement Objective Substitution
**File:** `src/kkt/reformulation.py`

Add new function for Strategy 1:

```python
def apply_strategy1_objective_substitution(
    model_ir: ModelIR,
    reformulation_results: list[MinMaxReformulationResult]
) -> None:
    """
    Apply Strategy 1: Direct Objective Substitution.
    
    For min/max calls that define variables in the objective chain,
    substitute the objective variable with the auxiliary variable.
    
    Transformation:
        minimize obj where obj = z and z = aux_min
        →
        minimize aux_min where obj = aux_min
    
    Args:
        model_ir: The model to modify
        reformulation_results: Results from min/max reformulation
    """
    if not model_ir.objective:
        return
    
    # Detect objective chain
    obj_chain = trace_objective_chain(model_ir)
    
    # Find reformulation results for variables in objective chain
    for result in reformulation_results:
        if result.original_lhs_var and result.original_lhs_var in obj_chain:
            # This aux variable should become the objective
            old_objvar = model_ir.objective.objvar
            new_objvar = result.aux_var_name
            
            # Step 1: Update objective variable
            model_ir.objective = ObjectiveInfo(
                sense=model_ir.objective.sense,
                objvar=new_objvar,
                expr=VarRef(new_objvar)  # Simple variable reference
            )
            
            # Step 2: Find and update objective-defining equations
            # Replace old_objvar = intermediate with old_objvar = new_objvar
            for eq_name, eq_def in model_ir.equations.items():
                if isinstance(eq_def.lhs, VarRef) and eq_def.lhs.name == old_objvar:
                    # Update RHS to reference new objective variable
                    model_ir.equations[eq_name] = EquationDef(
                        name=eq_def.name,
                        domain=eq_def.domain,
                        relation=eq_def.relation,
                        lhs_rhs=(eq_def.lhs, VarRef(new_objvar))
                    )
            
            # Step 3: Remove intermediate variable from chain if no longer needed
            # (Optional - may want to keep for solution interpretation)
```

#### Step 2.3: Integrate Strategy 1 into Reformulation Pipeline
**File:** `src/kkt/reformulation.py`

Update `reformulate_model()` to track and apply Strategy 1:

```python
def reformulate_model(model_ir: ModelIR) -> None:
    """
    Reformulate min/max functions using epigraph approach.
    
    Applies Strategy 1 (Direct Objective Substitution) when min/max
    appears in objective-defining equations.
    """
    # Existing detection logic
    minmax_calls = collect_all_minmax_calls(model_ir)
    
    if not minmax_calls:
        return
    
    # Track reformulation results for Strategy 1
    all_results: list[MinMaxReformulationResult] = []
    
    # Apply standard reformulation
    for eq_name in list(model_ir.equations.keys()):
        eq_def = model_ir.equations[eq_name]
        
        # ... existing reformulation logic ...
        
        # When creating result, track which variable was defined
        result = MinMaxReformulationResult(
            replacement_expr=VarRef(aux_var_name),
            aux_var_name=aux_var_name,
            inequality_constraints=constraints,
            func_type=min_max_call.func_type,
            context=eq_name,
            original_lhs_var=eq_def.lhs.name if isinstance(eq_def.lhs, VarRef) else None
        )
        all_results.append(result)
    
    # Apply Strategy 1 for objective-defining cases
    apply_strategy1_objective_substitution(model_ir, all_results)
```

### Phase 3: Derivative Updates (1-2 hours)

Update derivative computation to handle the new objective structure.

#### Step 3.1: Update Objective Gradient
**File:** `src/ad/objective_gradient.py`

The objective gradient computation should already handle simple variable objectives like `minimize aux_min`. Verify this works correctly:

```python
def compute_objective_gradient(model_ir: ModelIR) -> dict[str, Expr]:
    """Compute ∇f for objective function."""
    
    if not model_ir.objective:
        return {}
    
    obj_expr = model_ir.objective.expr
    
    # Should already handle VarRef(aux_min) case
    # Gradient is: ∂(aux_min)/∂var = 1 if var == aux_min, else 0
    
    # ... existing implementation should work ...
```

**Test:** Verify that `minimize aux_min` produces correct gradient `[..., 0, 1, 0, ...]` with 1 at aux_min position.

#### Step 3.2: Test Derivative Computation
**File:** `tests/unit/ad/test_strategy1_derivatives.py` (new)

```python
def test_objective_gradient_for_aux_variable():
    """Test that objective gradient is correct when objective is aux variable."""
    # Create model: minimize aux_min where aux_min is from min() reformulation
    model = create_test_model(
        objective_expr=VarRef("aux_min_eq1_0"),
        variables=["x", "y", "aux_min_eq1_0"]
    )
    
    gradient = compute_objective_gradient(model)
    
    # Should have ∂(aux_min)/∂aux_min = 1
    assert "aux_min_eq1_0" in gradient
    assert is_constant_one(gradient["aux_min_eq1_0"])
    
    # Should have ∂(aux_min)/∂x = 0, ∂(aux_min)/∂y = 0
    assert "x" in gradient and is_constant_zero(gradient["x"])
    assert "y" in gradient and is_constant_zero(gradient["y"])
```

### Phase 4: KKT Assembly Updates (0.5 hours)

Verify KKT assembly handles auxiliary objective variables correctly.

#### Step 4.1: Check Stationarity Equation Generation
**File:** `src/kkt/assemble.py`

The stationarity equation for the new objective variable (aux_min) should be:

```
∂L/∂aux_min = ∂f/∂aux_min - ν_eq + Σ λ_inequalities = 0
```

Where:
- `∂f/∂aux_min = 1` (from minimize aux_min)
- `ν_eq` is the multiplier for the equation that defined aux_min (e.g., `z = aux_min`)
- `λ_inequalities` are the multipliers for min/max constraints (aux_min ≤ x, aux_min ≤ y)

**This should already work** with the existing KKT assembly logic. Verify with a test.

#### Step 4.2: Test KKT Assembly
**File:** `tests/unit/kkt/test_strategy1_assembly.py` (new)

```python
def test_kkt_assembly_with_strategy1():
    """Test that KKT assembly produces correct stationarity for aux objective."""
    # Build model after Strategy 1 transformation
    model = create_model_after_strategy1()
    
    gradient = compute_objective_gradient(model)
    J_eq, J_ineq = compute_constraint_jacobians(model)
    
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
    
    # Check stationarity equation for aux_min
    assert "stat_aux_min_eq1_0" in kkt.equations
    
    # Should include:
    # - Objective gradient term (1)
    # - Equality constraint multiplier (-ν_eq)
    # - Inequality multipliers (+λ_x, +λ_y)
    # Result: 1 - ν_eq + λ_x + λ_y = 0
```

### Phase 5: Validation and Error Handling (1 hour)

Add validation to detect unsupported patterns and provide helpful error messages.

#### Step 5.1: Add Validation
**File:** `src/kkt/reformulation.py`

```python
def validate_minmax_reformulation(model_ir: ModelIR) -> None:
    """
    Validate that min/max reformulation can be applied.
    
    Raises:
        ValueError: If min/max appears in unsupported context
    """
    # Check for deeply nested min/max in objective chains
    minmax_in_chain = detect_minmax_in_objective_chain(model_ir)
    
    for eq_name, var_name, func_type in minmax_in_chain:
        eq = model_ir.equations[eq_name]
        
        # Check for nested min/max (e.g., max(min(x,y), z))
        # This requires recursive Strategy 1 application
        minmax_calls = find_minmax_calls(eq.rhs, context=eq_name)
        
        if len(minmax_calls) > 1:
            # Multiple min/max in same objective-defining equation
            # This needs special handling
            raise ValueError(
                f"Multiple min/max functions in objective-defining equation '{eq_name}' "
                f"are not yet supported. Found {len(minmax_calls)} calls.\n"
                f"Suggested workaround: Reformulate manually using auxiliary variables."
            )
        
        # Check for min/max nested inside other functions
        # e.g., obj = exp(min(x, y))
        if not is_simple_minmax_equation(eq):
            raise ValueError(
                f"Min/max inside complex expressions in objective-defining equation '{eq_name}' "
                f"is not yet supported.\n"
                f"Found: {eq.rhs}\n"
                f"Suggested workaround: Introduce intermediate variable."
            )
```

#### Step 5.2: Add Helpful Error Messages
**File:** `src/kkt/reformulation.py`

When Strategy 1 cannot be applied, provide guidance:

```python
class MinMaxReformulationError(Exception):
    """Error during min/max reformulation."""
    
    def __init__(self, message: str, equation_name: str, suggestion: str):
        self.equation_name = equation_name
        self.suggestion = suggestion
        super().__init__(
            f"{message}\n"
            f"In equation: {equation_name}\n"
            f"Suggestion: {suggestion}"
        )
```

### Phase 6: Testing (1-2 hours)

Comprehensive testing of Strategy 1 implementation.

#### Step 6.1: Update Existing Test Fixtures
**Files:** `tests/fixtures/minmax_research/test*.gms`

These files already use min/max in objective-defining equations, so they're perfect test cases for Strategy 1. No changes needed.

#### Step 6.2: Add Strategy 1 Unit Tests
**File:** `tests/unit/kkt/test_strategy1_reformulation.py` (new)

```python
class TestStrategy1Detection:
    """Test detection of min/max in objective-defining equations."""
    
    def test_detects_simple_chain(self):
        """Test: minimize obj where obj = z and z = min(x,y)"""
        model = create_simple_chain_model()
        results = detect_minmax_in_objective_chain(model)
        assert len(results) == 1
        assert results[0] == ('eq_z', 'z', 'min')
    
    def test_detects_direct_objective(self):
        """Test: minimize obj where obj = min(x,y)"""
        model = create_direct_objective_model()
        results = detect_minmax_in_objective_chain(model)
        assert len(results) == 1
        assert results[0] == ('objdef', 'obj', 'min')
    
    def test_no_detection_for_constraint(self):
        """Test: min/max in regular constraint should not be detected"""
        model = create_constraint_minmax_model()
        results = detect_minmax_in_objective_chain(model)
        assert len(results) == 0


class TestStrategy1Substitution:
    """Test objective variable substitution."""
    
    def test_substitutes_objective_variable(self):
        """Test that objective variable is replaced with aux variable."""
        model = create_simple_chain_model()  # obj = z, z = min(x,y)
        reformulate_model(model)
        
        # After Strategy 1, objective should be aux_min
        assert model.objective.objvar.startswith("aux_min_")
        assert isinstance(model.objective.expr, VarRef)
    
    def test_updates_objective_defining_equation(self):
        """Test that obj = z becomes obj = aux_min."""
        model = create_simple_chain_model()
        reformulate_model(model)
        
        objdef = model.equations['objdef']
        assert isinstance(objdef.rhs, VarRef)
        assert objdef.rhs.name.startswith("aux_min_")
    
    def test_preserves_inequality_constraints(self):
        """Test that min/max inequality constraints are still created."""
        model = create_simple_chain_model()
        reformulate_model(model)
        
        # Should have aux_min <= x and aux_min <= y
        ineqs = [eq for eq in model.equations.keys() if eq.startswith("minmax_min_")]
        assert len(ineqs) == 2


class TestStrategy1Integration:
    """Integration tests for full pipeline with Strategy 1."""
    
    def test_full_pipeline_test1(self):
        """Test full pipeline on test1_minimize_min.gms"""
        model = parse_model_file("tests/fixtures/minmax_research/test1_minimize_min.gms")
        normalize_model(model)
        reformulate_model(model)
        
        gradient = compute_objective_gradient(model)
        J_eq, J_ineq = compute_constraint_jacobians(model)
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
        
        # KKT system should be well-formed
        assert len(kkt.stationarity_equations) > 0
        assert len(kkt.complementarity_pairs) > 0
    
    def test_generates_solvable_mcp(self):
        """Test that generated MCP is solvable by PATH."""
        # This is the critical test - PATH should NOT report infeasible
        model = parse_model_file("tests/fixtures/minmax_research/test1_minimize_min.gms")
        
        # Run through full pipeline
        from src.cli import convert_nlp_to_mcp
        output_file = "/tmp/test_strategy1.gms"
        convert_nlp_to_mcp(model, output_file)
        
        # Run through GAMS/PATH
        result = subprocess.run(
            ["gams", output_file],
            capture_output=True,
            text=True
        )
        
        # PATH should NOT report infeasible
        assert "infeasible" not in result.stdout.lower()
        assert "Normal completion" in result.stdout
```

#### Step 6.3: Update Integration Tests
**File:** `tests/unit/kkt/test_minmax_fix.py`

Update the existing tests to expect Strategy 1 behavior:

```python
def test_minimize_min_xy(self):
    """Test Case 1: minimize z where z = min(x, y)"""
    gams_file = "tests/fixtures/minmax_research/test1_minimize_min.gms"
    
    model_ir = parse_model_file(gams_file)
    normalize_model(model_ir)
    reformulate_model(model_ir)
    
    # After Strategy 1, objective should be the auxiliary variable
    assert model_ir.objective.objvar.startswith("aux_min_")
    
    # Original equation structure still exists
    aux_vars = [v for v in model_ir.variables.keys() if v.startswith("aux_min_")]
    assert len(aux_vars) >= 1
    
    minmax_ineqs = [eq for eq in model_ir.equations.keys() if eq.startswith("minmax_min_")]
    assert len(minmax_ineqs) >= 2
    
    # NEW: Test PATH solvability
    output_file = "/tmp/test1_after_strategy1.gms"
    generate_mcp(model_ir, output_file)
    
    result = run_gams_path(output_file)
    assert result.solvable, "MCP should be solvable after Strategy 1"
```

### Phase 7: Documentation (0.5 hours)

Update documentation to reflect Strategy 1 implementation.

#### Step 7.1: Update Design Document
**File:** `docs/design/minmax_kkt_fix_design.md`

Add section:

```markdown
## Strategy 1 Implementation (Completed)

Strategy 1 (Direct Objective Substitution) has been implemented to handle min/max
functions in objective-defining equations.

### Detection Algorithm
[Copy from implementation]

### Transformation Process
[Copy from implementation]

### Supported Cases
- Simple chains: `minimize obj` where `obj = z`, `z = min(x,y)`
- Direct objectives: `minimize obj` where `obj = min(x,y)`
- Multiple hops: `minimize obj` where `obj = a`, `a = b`, `b = min(x,y)`

### Unsupported Cases (Future Work)
- Nested min/max in objective chain: `obj = max(min(x,y), z)`
- Min/max in complex expressions: `obj = exp(min(x,y))`
```

#### Step 7.2: Update Research Document
**File:** `docs/research/minmax_objective_reformulation.md`

Add implementation status:

```markdown
## Implementation Status

### Strategy 1: Direct Objective Substitution
**Status:** ✅ IMPLEMENTED (Sprint 5 Follow-On)

**Files:**
- Detection: `src/ir/minmax_detection.py`
- Substitution: `src/kkt/reformulation.py`
- Tests: `tests/unit/kkt/test_strategy1_*.py`

**Verification:** All 6 min/max research test cases now generate PATH-solvable MCPs.
```

## Implementation Checklist

### Phase 1: Detection
- [ ] Implement `trace_objective_chain()` function
- [ ] Implement `detect_minmax_in_objective_chain()` function  
- [ ] Add detection to CLI pipeline with verbose logging
- [ ] Write unit tests for detection logic
- [ ] Test on all 6 research fixtures

### Phase 2: Objective Substitution
- [ ] Extend `MinMaxReformulationResult` dataclass
- [ ] Implement `apply_strategy1_objective_substitution()` function
- [ ] Integrate Strategy 1 into `reformulate_model()`
- [ ] Write unit tests for substitution logic
- [ ] Verify objective variable is correctly updated

### Phase 3: Derivative Updates
- [ ] Verify objective gradient handles aux variables
- [ ] Add tests for gradient computation with Strategy 1
- [ ] Ensure no regressions in existing gradient tests

### Phase 4: KKT Assembly
- [ ] Verify stationarity equations are correct
- [ ] Add tests for KKT assembly with Strategy 1
- [ ] Check that multipliers are properly connected

### Phase 5: Validation
- [ ] Add validation for unsupported patterns
- [ ] Implement helpful error messages
- [ ] Test error messages with invalid inputs

### Phase 6: Testing
- [ ] Create `test_strategy1_reformulation.py`
- [ ] Create `test_strategy1_derivatives.py`
- [ ] Create `test_strategy1_assembly.py`
- [ ] Update existing tests in `test_minmax_fix.py`
- [ ] Add PATH solvability tests
- [ ] Run full regression suite

### Phase 7: Documentation
- [ ] Update design document
- [ ] Update research document
- [ ] Update CHANGELOG.md
- [ ] Add code comments and docstrings

### Verification
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] PATH solves all 6 research test cases
- [ ] No regressions in existing functionality
- [ ] Type checking (mypy) clean
- [ ] Linting (ruff) clean
- [ ] Coverage ≥85%

## Success Criteria

1. ✅ All 6 min/max research test cases generate PATH-solvable MCPs
2. ✅ PATH reports "Normal completion" (not "infeasible")
3. ✅ Tests verify correct objective variable substitution
4. ✅ Generated MCP structure matches Strategy 1 design
5. ✅ No regressions in existing min/max or KKT tests
6. ✅ Documentation updated and complete

## Testing Strategy

### Unit Tests
- Detection logic for objective chains
- Objective variable substitution
- Gradient computation for aux objectives
- KKT assembly with substituted objectives

### Integration Tests
- Full pipeline on all 6 research fixtures
- PATH solvability verification
- Comparison with manually reformulated models

### Regression Tests
- Existing min/max in constraint tests still pass
- Existing KKT assembly tests unchanged
- All other model types unaffected

## Known Limitations (Post-Implementation)

After implementing Strategy 1, the following cases will still be unsupported:

1. **Nested min/max in objective chain:**
   ```gams
   minimize obj
   obj = z
   z = max(min(x, y), w)  * Nested min inside max
   ```
   **Future Work:** Recursive Strategy 1 application

2. **Min/max in complex expressions:**
   ```gams
   minimize obj  
   obj = exp(min(x, y)) + z^2
   ```
   **Future Work:** Expression decomposition before Strategy 1

3. **Multiple min/max calls in same equation:**
   ```gams
   minimize obj
   obj = min(x, y) + max(w, z)
   ```
   **Future Work:** Multi-call Strategy 1 coordination

These limitations should be clearly documented with helpful error messages.

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaks existing reformulation | Low | High | Comprehensive regression tests |
| Edge cases not handled | Medium | Medium | Extensive unit test coverage |
| PATH still fails | Low | High | Verify with manual reformulation first |
| Performance degradation | Low | Low | Profile detection algorithm |
| Complex code, hard to maintain | Medium | Medium | Thorough documentation and comments |

## Dependencies

### Code Dependencies
- `src/ir/minmax_detection.py` - Existing detection functions
- `src/kkt/reformulation.py` - Existing reformulation infrastructure
- `src/ad/objective_gradient.py` - Gradient computation
- `src/kkt/assemble.py` - KKT assembly

### Test Dependencies
- `tests/fixtures/minmax_research/` - Research test cases
- GAMS/PATH installation for solvability testing

### Documentation Dependencies
- `docs/research/minmax_objective_reformulation.md`
- `docs/design/minmax_kkt_fix_design.md`

## Timeline Estimate

| Phase | Task | Hours | Running Total |
|-------|------|-------|---------------|
| 1 | Detection logic | 2-3h | 2-3h |
| 2 | Objective substitution | 3-4h | 5-7h |
| 3 | Derivative updates | 1-2h | 6-9h |
| 4 | KKT assembly verification | 0.5h | 6.5-9.5h |
| 5 | Validation & errors | 1h | 7.5-10.5h |
| 6 | Testing | 1-2h | 8.5-12.5h |
| 7 | Documentation | 0.5h | 9-13h |

**Estimate: 9-13 hours total**  
**Recommended allocation: 2 full work days**

## References

- Original research: `docs/research/minmax_objective_reformulation.md`
- PATH validation findings: `docs/research/minmax_path_validation_findings.md`
- Day 2 status: `docs/planning/SPRINT_5/DAY_2_STATUS.md`
- KKT assembly: `src/kkt/assemble.py`
- Existing reformulation: `src/kkt/reformulation.py`

## Notes

This task implements the solution that was identified during the research phase and validated during Day 2 PATH testing. The infrastructure is already in place; this task adds the missing piece to make min/max in objective-defining equations work correctly.

The implementation should be straightforward since the research already worked out the mathematics and the existing reformulation infrastructure provides all the necessary hooks.
