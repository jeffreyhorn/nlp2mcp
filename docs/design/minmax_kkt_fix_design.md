# Min/Max in Objective-Defining Equations: KKT Assembly Fix Design

**Status:** 🔧 Implementation Ready  
**Priority:** Critical (Sprint 5 Day 1-2)  
**Date:** November 6, 2025  
**Related Research:** `docs/research/minmax_objective_reformulation.md`

---

## Executive Summary

This design document specifies the fix for min/max reformulation in objective-defining equations. The current implementation creates **mathematically infeasible KKT systems** when min/max defines the objective variable. This document outlines **Strategy 1 (Auxiliary Variable with Proper KKT Assembly)** as the required solution.

**Key Finding:** Strategy 2 (Direct Constraints) has been mathematically proven infeasible. We MUST use Strategy 1.

---

## Problem Statement

### Current Behavior (Broken)

When min/max appears in an equation that defines the objective variable, the current reformulation creates an infeasible system:

```gams
Variables x, y, z, obj;
Equations objective, min_constraint;

objective.. obj =e= z;
min_constraint.. z =e= min(x, y);

x.lo = 1; y.lo = 2;
Solve model using NLP minimizing obj;
```

**Current Reformulation:**
```
minimize z
s.t. z = aux_min
     aux_min ≤ x
     aux_min ≤ y
```

**KKT Stationarity (INFEASIBLE):**
```
∂L/∂z = 1 + ν = 0           → ν = -1
∂L/∂aux = -ν + λ_x + λ_y = 0  → λ_x + λ_y = -1  (IMPOSSIBLE!)
```

Since λ_x, λ_y ≥ 0, the equation λ_x + λ_y = -1 is **mathematically infeasible**.

### Root Cause

The issue occurs in **KKT assembly** (`src/kkt/assemble.py`):

1. The min/max reformulation creates auxiliary constraints (e.g., `aux ≤ x`)
2. These constraints have associated **equality constraint multipliers** when they connect to the objective variable
3. **The current KKT assembly EXCLUDES these auxiliary constraint multipliers** from the stationarity equations
4. This creates an incomplete Lagrangian, leading to infeasibility

**Critical Insight:** The reformulation in `src/kkt/reformulation.py` is actually CORRECT. The bug is in `src/kkt/assemble.py` which doesn't include ALL equality constraint multipliers in the stationarity equations.

---

## Solution Approach: Strategy 1 (Proper KKT Assembly)

### Mathematical Formulation

**Strategy 1 Reformulation:**
```
Original:
    minimize obj
    s.t. obj = z
         z = min(x, y)

Reformulated:
    minimize obj
    s.t. obj = z
         z = aux          (equality constraint with multiplier ν_z)
         aux ≤ x          (inequality with multiplier λ_x ≥ 0)
         aux ≤ y          (inequality with multiplier λ_y ≥ 0)
```

**Complete KKT System:**
```
Variables: x, y, z, aux, obj

Multipliers:
    ν_obj  (for obj = z, free)
    ν_z    (for z = aux, free)
    λ_x    (for aux ≤ x, ≥ 0)
    λ_y    (for aux ≤ y, ≥ 0)

Stationarity Equations:
    ∂L/∂obj = ν_obj = 0                     (obj is free)
    ∂L/∂z = -ν_obj + ν_z = 0                (z couples obj and aux)
    ∂L/∂aux = -ν_z - λ_x - λ_y = 0          (aux balances equality and inequalities)
    ∂L/∂x = ... + λ_x = 0                   (x's other terms)
    ∂L/∂y = ... + λ_y = 0                   (y's other terms)

Equality Equations:
    obj - z = 0
    z - aux = 0

Complementarity Pairs:
    (x - aux) ⊥ λ_x
    (y - aux) ⊥ λ_y
```

**Why This Works:**
- The stationarity for aux includes **both** the equality multiplier ν_z **and** the inequality multipliers λ_x, λ_y
- At optimum: aux = 1 (min of x=1, y=2)
- ν_z can be any value needed to balance the equation
- λ_x > 0 (active), λ_y = 0 (slack)
- System is feasible!

### Key Architecture Insight

The fix is NOT in the reformulation logic (`src/kkt/reformulation.py`). That code is correct.

The fix is in **KKT assembly** (`src/kkt/assemble.py`):
- Currently, it only creates multipliers for "original" equality constraints
- It must ALSO create multipliers for auxiliary equality constraints introduced by min/max reformulation
- These auxiliary multipliers must appear in stationarity equations

---

## Implementation Plan

### Phase 1: Detection (Task 1.4)

**Goal:** Detect when min/max defines the objective variable.

**Location:** `src/ir/analysis.py` or new `src/ir/minmax_detection.py`

**Function Signature:**
```python
def detects_objective_minmax(model_ir: ModelIR) -> bool:
    """
    Detect if min/max appears in equations that define the objective variable.
    
    Detection algorithm:
    1. Get objective variable from model_ir.objective.objvar
    2. Find the equation that defines it (e.g., obj = z)
    3. Trace dependency chain: if z is defined by an equation containing min/max
    4. Handle chains: obj = z, z = w, w = min(x,y)
    
    Returns:
        True if min/max defines objective (directly or through chain)
    """
```

**Implementation:**
```python
def detects_objective_minmax(model_ir: ModelIR) -> bool:
    if model_ir.objective is None:
        return False
    
    objvar = model_ir.objective.objvar
    
    # Build dependency graph: var -> equation that defines it
    definitions = _build_variable_definitions(model_ir)
    
    # Trace from objvar through defining equations
    visited = set()
    to_check = [objvar]
    
    while to_check:
        var = to_check.pop()
        if var in visited:
            continue
        visited.add(var)
        
        # Find equation defining this variable
        if var not in definitions:
            continue
            
        eq_name = definitions[var]
        eq_def = model_ir.equations[eq_name]
        
        # Check if equation contains min/max
        if _contains_minmax(eq_def):
            return True
        
        # Find variables on RHS to continue tracing
        rhs_vars = _extract_variables(eq_def.lhs_rhs[1])
        to_check.extend(rhs_vars)
    
    return False

def _build_variable_definitions(model_ir: ModelIR) -> dict[str, str]:
    """Map each variable to the equation that defines it (if any)."""
    definitions = {}
    for eq_name, eq_def in model_ir.equations.items():
        lhs, rhs = eq_def.lhs_rhs
        # If LHS is simple variable reference, this equation defines it
        if isinstance(lhs, VarRef):
            definitions[lhs.name] = eq_name
    return definitions

def _contains_minmax(eq_def: EquationDef) -> bool:
    """Check if equation contains min() or max() calls."""
    from src.kkt.reformulation import detect_min_max_calls
    
    lhs, rhs = eq_def.lhs_rhs
    for expr in [lhs, rhs]:
        calls = detect_min_max_calls(expr, eq_def.name)
        if calls:
            return True
    return False

def _extract_variables(expr: Expr) -> list[str]:
    """Extract all variable names from an expression."""
    vars = []
    
    def traverse(node: Expr):
        if isinstance(node, VarRef):
            vars.append(node.name)
        elif hasattr(node, '__dict__'):
            for value in node.__dict__.values():
                if isinstance(value, Expr):
                    traverse(value)
                elif isinstance(value, (list, tuple)):
                    for item in value:
                        if isinstance(item, Expr):
                            traverse(item)
    
    traverse(expr)
    return vars
```

**Test Coverage:** 100% required
- Simple case: obj = min(x,y)
- Chain case: obj = z, z = min(x,y)
- Multi-hop chain: obj = z, z = w, w = min(x,y)
- Nested min/max: obj = z, z = max(min(x,y), w)
- No min/max: obj = x + y
- Min/max in constraint (not objective): should return False

### Phase 2: KKT Assembly Fix (Task 1.5 + Day 2)

**Goal:** Include auxiliary constraint multipliers in stationarity equations.

**Location:** `src/kkt/assemble.py`

**Current Code (Lines 107-138):**
```python
def _create_eq_multipliers(
    equalities: list[str], model_ir: ModelIR, skip_equation: str | None = None
) -> dict[str, MultiplierDef]:
    """Create multiplier definitions for equality constraints."""
    multipliers = {}
    for eq_name in equalities:
        # Skip objective-defining equation if specified
        if skip_equation and eq_name == skip_equation:
            logger.info(f"Skipping multiplier for objective-defining equation: {eq_name}")
            continue

        # Check both equations dict and normalized_bounds dict
        if eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
            domain = eq_def.domain
        elif eq_name in model_ir.normalized_bounds:
            norm_eq = model_ir.normalized_bounds[eq_name]
            domain = norm_eq.domain_sets
        else:
            continue

        mult_name = create_eq_multiplier_name(eq_name)
        multipliers[mult_name] = MultiplierDef(...)
    return multipliers
```

**Problem:** This function processes `equalities` list from partition, which may not include auxiliary constraints created by min/max reformulation.

**Fix Strategy:**

1. **After min/max reformulation** (in `src/cli.py` or wherever reformulation is called), auxiliary equality constraints are added to `model_ir.equations`

2. **In `assemble_kkt_system`**, we need to ensure auxiliary constraints are included in the partition

3. **Modify `_create_eq_multipliers`** to handle auxiliary constraints:

```python
def _create_eq_multipliers(
    equalities: list[str], 
    model_ir: ModelIR, 
    skip_equation: str | None = None
) -> dict[str, MultiplierDef]:
    """Create multiplier definitions for equality constraints.
    
    Handles both user-defined equations and auxiliary constraints from min/max.
    
    CRITICAL: After min/max reformulation, some auxiliary variables may be
    defined by equality constraints (e.g., z = aux_min). These constraints
    MUST have multipliers created for proper KKT assembly.
    """
    multipliers = {}
    
    # TODO (Sprint 5 Day 2): Verify auxiliary constraints from min/max reformulation
    # are included in equalities list. If not, add them explicitly:
    # auxiliary_equalities = _find_auxiliary_equalities(model_ir)
    # all_equalities = equalities + auxiliary_equalities
    
    for eq_name in equalities:
        # Skip objective-defining equation if specified
        if skip_equation and eq_name == skip_equation:
            logger.info(f"Skipping multiplier for objective-defining equation: {eq_name}")
            continue

        # Check both equations dict and normalized_bounds dict
        if eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
            domain = eq_def.domain
        elif eq_name in model_ir.normalized_bounds:
            norm_eq = model_ir.normalized_bounds[eq_name]
            domain = norm_eq.domain_sets
        else:
            continue

        mult_name = create_eq_multiplier_name(eq_name)
        
        # TODO (Sprint 5 Day 2): Add debug logging to trace auxiliary multipliers
        logger.debug(f"Creating equality multiplier: {mult_name} for constraint: {eq_name}")
        if eq_name.startswith("aux_eq_"):
            logger.info(f"  -> Auxiliary constraint from min/max reformulation")
        
        multipliers[mult_name] = MultiplierDef(
            name=mult_name,
            domain=domain,
            kind="eq",
            associated_constraint=eq_name,
        )
    
    return multipliers
```

4. **Ensure auxiliary constraints appear in partition:**

Check `src/kkt/partition.py` to ensure auxiliary constraints created during min/max reformulation are properly categorized:

```python
# In partition_constraints():
# After min/max reformulation, model_ir.equations contains both:
# - Original user equations
# - Auxiliary equality constraints (e.g., aux_eq_min_*)
# - Auxiliary inequality constraints (e.g., minmax_min_*_arg0)

# The partition logic should classify these correctly based on their Rel type
```

### Phase 3: Integration Point

**Where to call reformulation:**

Current pipeline (from `src/cli.py`):
```
1. parse_gams_model()
2. normalize_model()
3. compute_objective_gradient()
4. compute_constraint_jacobians()
5. assemble_kkt_system()
```

**Required change:**
```
1. parse_gams_model()
2. normalize_model()
3. reformulate_model()        # NEW: Add min/max reformulation HERE
4. compute_objective_gradient()
5. compute_constraint_jacobians()
6. assemble_kkt_system()
```

**Rationale:**
- After `normalize_model()`: All equations are in standard form
- Before `compute_*_gradient()`: Auxiliary variables are added to model before derivatives computed
- `assemble_kkt_system()` sees complete model with all multipliers

---

## Code Locations to Modify

### Files to Create/Modify

1. **`src/ir/minmax_detection.py`** (NEW)
   - `detects_objective_minmax()` - Main detection function
   - `_build_variable_definitions()` - Dependency graph builder
   - `_contains_minmax()` - AST checker
   - `_extract_variables()` - Variable extractor

2. **`src/kkt/assemble.py`** (MODIFY)
   - `_create_eq_multipliers()` - Add TODO comments + logging for Day 2
   - `assemble_kkt_system()` - Add debug logging to trace auxiliary constraints

3. **`src/kkt/partition.py`** (VERIFY)
   - Ensure auxiliary constraints are correctly partitioned
   - No changes expected if reformulation adds constraints properly

4. **`src/cli.py`** or main pipeline (MODIFY on Day 2)
   - Add `reformulate_model()` call after `normalize_model()`
   - Import from `src.kkt.reformulation`

5. **`tests/unit/kkt/test_minmax_fix.py`** (NEW)
   - 5 regression tests from research (xfail initially)

6. **`tests/unit/ir/test_minmax_detection.py`** (NEW)
   - 100% coverage of detection logic

7. **`docs/design/minmax_kkt_fix_design.md`** (THIS FILE)
   - Design documentation

---

## Test Strategy

### Unit Tests

#### 1. Detection Logic (`tests/unit/ir/test_minmax_detection.py`)

```python
def test_detects_simple_objective_minmax():
    """obj = min(x, y) should be detected."""
    
def test_detects_chained_objective_minmax():
    """obj = z, z = min(x, y) should be detected."""
    
def test_detects_multihop_chain():
    """obj = z, z = w, w = min(x, y) should be detected."""
    
def test_detects_nested_minmax():
    """obj = z, z = max(min(x, y), w) should be detected."""
    
def test_no_detection_for_constraint_minmax():
    """min/max in constraint (not objective) should NOT be detected."""
    
def test_no_detection_without_minmax():
    """obj = x + y should NOT be detected."""
```

#### 2. KKT Assembly (`tests/unit/kkt/test_minmax_fix.py`)

Port from `tests/fixtures/minmax_research/`:

```python
@pytest.mark.xfail(reason="Min/max in objective not yet implemented")
def test_minimize_min_xy():
    """Test Case 1: minimize z where z = min(x, y)
    
    Expected solution: z* = 1, x* = 1, y* = 2
    
    This is the critical test case that proves Strategy 2 is infeasible.
    Strategy 1 should generate proper KKT system with auxiliary multipliers.
    """
    gams_file = "tests/fixtures/minmax_research/test1_minimize_min.gms"
    # Parse, normalize, reformulate, assemble KKT
    # Assert MCP is generated without errors
    # Assert auxiliary constraints and multipliers are present

@pytest.mark.xfail(reason="Min/max in objective not yet implemented")
def test_maximize_max_xy():
    """Test Case 2: maximize z where z = max(x, y)
    
    Symmetric case to Test 1.
    """

@pytest.mark.xfail(reason="Min/max in objective not yet implemented")
def test_minimize_max_xy():
    """Test Case 3: minimize z where z = max(x, y)
    
    Opposite sense combination.
    """

@pytest.mark.xfail(reason="Min/max in objective not yet implemented")
def test_maximize_min_xy():
    """Test Case 4: maximize z where z = min(x, y)
    
    Opposite sense combination.
    """

@pytest.mark.xfail(reason="Min/max in objective not yet implemented")
def test_nested_minmax():
    """Test Case 5: minimize z where z = max(min(x, y), w)
    
    Nested min/max handling.
    """
```

### Integration Tests

After Day 2 implementation, remove `@pytest.mark.xfail` and verify:
- MCP generates successfully
- Auxiliary variables appear in output
- Multipliers are correctly named
- Stationarity equations include all terms
- PATH solver converges (Day 3 validation)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         NLP Model                                │
│  minimize obj                                                    │
│  s.t. obj = z                                                    │
│       z = min(x, y)                                              │
│       x ≥ 1, y ≥ 2                                               │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Min/Max Reformulation                               │
│  (src/kkt/reformulation.py::reformulate_model)                  │
│                                                                  │
│  Creates:                                                        │
│  - Auxiliary variable: aux_min_minconstraint_0                   │
│  - Auxiliary equality: z = aux_min_minconstraint_0               │
│  - Inequality constraints: aux ≤ x, aux ≤ y                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              Constraint Partition                                │
│  (src/kkt/partition.py::partition_constraints)                  │
│                                                                  │
│  Equalities:                                                     │
│    - objective: obj = z                                          │
│    - aux_eq_min_*: z = aux_min_minconstraint_0  ← MUST INCLUDE! │
│                                                                  │
│  Inequalities:                                                   │
│    - minmax_min_*_arg0: aux ≤ x                                  │
│    - minmax_min_*_arg1: aux ≤ y                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│              KKT Assembly (THE FIX!)                             │
│  (src/kkt/assemble.py::assemble_kkt_system)                     │
│                                                                  │
│  Multipliers Created:                                            │
│    ν_objective  (for obj = z, free)                              │
│    ν_aux_eq     (for z = aux, free)  ← CRITICAL: Must create!   │
│    λ_arg0       (for aux ≤ x, ≥ 0)                               │
│    λ_arg1       (for aux ≤ y, ≥ 0)                               │
│                                                                  │
│  Stationarity Equations:                                         │
│    ∂L/∂obj = ν_objective = 0                                     │
│    ∂L/∂z = -ν_objective + ν_aux_eq = 0                           │
│    ∂L/∂aux = -ν_aux_eq - λ_arg0 - λ_arg1 = 0  ← Now feasible!   │
│    ∂L/∂x = ... + λ_arg0 = 0                                      │
│    ∂L/∂y = ... + λ_arg1 = 0                                      │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MCP System                                  │
│                                                                  │
│  Variables: obj, z, aux, x, y                                    │
│  Multipliers: ν_objective, ν_aux_eq, λ_arg0, λ_arg1              │
│                                                                  │
│  Equations: stationarity(obj), stationarity(z),                  │
│             stationarity(aux), stationarity(x), stationarity(y)  │
│                                                                  │
│  Equality Equations: obj - z = 0, z - aux = 0                    │
│                                                                  │
│  Complementarity: (x - aux) ⊥ λ_arg0, (y - aux) ⊥ λ_arg1         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

### Day 1 (Design & Scaffolding)

- [x] Design document created (`docs/design/minmax_kkt_fix_design.md`)
- [ ] Detection module created (`src/ir/minmax_detection.py`)
- [ ] Detection tests created with 100% coverage (`tests/unit/ir/test_minmax_detection.py`)
- [ ] Regression test suite created with xfail markers (`tests/unit/kkt/test_minmax_fix.py`)
- [ ] KKT assembly scaffolded with TODO comments and logging (`src/kkt/assemble.py`)
- [ ] All tests pass (xfail tests are expected failures)
- [ ] Build succeeds: `make typecheck && make lint && make format && make test`

### Day 2 (Implementation)

- [ ] Detection logic fully implemented and tested (100% coverage)
- [ ] KKT assembly modified to include auxiliary constraint multipliers
- [ ] Integration point added in pipeline (reformulation call)
- [ ] All 5 regression tests PASS (xfail removed)
- [ ] Full test suite passes (≥972 tests, no regressions)
- [ ] Coverage maintained at ≥85%
- [ ] Mypy and ruff clean

### Day 3 (PATH Validation)

- [ ] All 5 test cases generate valid MCPs
- [ ] PATH solver converges on all 5 cases
- [ ] Solution values match expected results
- [ ] Documentation updated with findings

---

## Known Risks & Mitigations

### Risk 1: Partition doesn't include auxiliary constraints

**Mitigation:** 
- Verify `partition_constraints()` processes all equations in `model_ir.equations`
- Add explicit check for auxiliary constraints
- Add debug logging to trace partition decisions

### Risk 2: Multiplier naming conflicts

**Mitigation:**
- Use consistent naming scheme: `nu_<equation_name>` for equality multipliers
- Verify no collisions with user-declared variables
- Add collision detection in auxiliary variable manager

### Risk 3: Stationarity equations missing terms

**Mitigation:**
- Add comprehensive logging in `build_stationarity_equations()`
- Verify Jacobian includes auxiliary variables
- Test with known-good hand-derived KKT system

### Risk 4: PATH solver non-convergence

**Mitigation:**
- Start with simple test case (test1)
- Experiment with PATH solver options (Day 3)
- Compare with manual MCP formulation
- Document any required solver tuning

---

## References

1. **Research Document:** `docs/research/minmax_objective_reformulation.md`
   - Strategy 2 infeasibility proof
   - Strategy 1 mathematical derivation

2. **Prep Plan Update:** `docs/planning/SPRINT_5/PREP_PLAN_TASK2_UPDATE.md`
   - Validation results from manual testing
   - Critical findings summary

3. **Test Fixtures:** `tests/fixtures/minmax_research/`
   - Test case GAMS models (test1-test6)
   - Manual MCP reformulations demonstrating infeasibility

4. **Sprint 5 Plan:** `docs/planning/SPRINT_5/PLAN.md`
   - Day 1-2 task breakdown
   - Acceptance criteria

---

## Implementation Notes

### Day 1 Focus: Infrastructure & Design

**DO NOT implement full fix on Day 1.** Focus on:
- Detection logic (complete implementation)
- Test scaffolding (xfail tests ready)
- Design validation (this document)
- Assembly scaffolding (TODOs + logging)

### Day 2 Focus: Implementation & Testing

**Complete the fix:**
- Remove TODOs from assembly code
- Verify auxiliary multipliers created
- Test all 5 regression cases
- Remove xfail markers
- Run full test suite

### Day 3 Focus: Validation

**PATH solver testing:**
- Generate MCPs for all test cases
- Run through PATH
- Verify convergence
- Document any issues

---

## Conclusion

This design provides a clear path to fixing the min/max reformulation bug:

1. **Root Cause Identified:** Missing auxiliary constraint multipliers in KKT assembly
2. **Solution Validated:** Strategy 1 with proper KKT assembly is mathematically sound
3. **Implementation Path Clear:** Detection → Scaffolding → Implementation → Testing
4. **Risk Mitigation:** Comprehensive testing, logging, and incremental approach

The fix is **straightforward** once the root cause is understood: ensure ALL equality constraint multipliers (original + auxiliary) are included in the stationarity equations.

**Estimated Effort:**
- Day 1 (Design & Scaffolding): 8 hours ✅
- Day 2 (Implementation & Testing): 8 hours
- Total: 16 hours

**Confidence Level:** HIGH
- Mathematical foundation solid (Strategy 1 proven feasible)
- Code architecture supports the fix
- Comprehensive test coverage planned
- Incremental approach reduces risk
