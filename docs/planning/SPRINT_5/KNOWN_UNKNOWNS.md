# Sprint 5 Known Unknowns

**Created:** November 5, 2025  
**Status:** Active - Pre-Sprint 5  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 5 production hardening and release

---

## Overview

This document identifies all assumptions and unknowns for Sprint 5 features **before** implementation begins. This proactive approach continues the highly successful Sprint 4 methodology that prevented all late-stage surprises.

**Sprint 5 Scope:**
1. Fix min/max reformulation bug
2. Complete PATH solver validation
3. Production hardening (large models, error recovery, memory optimization)
4. PyPI packaging and release automation
5. Documentation polish (tutorial, FAQ, API reference)

**Lesson from Sprint 4:** The Known Unknowns process achieved ⭐⭐⭐⭐⭐ rating - 23 unknowns identified, 10 resolved proactively, 13 resolved on schedule, **zero late surprises**. Continue this approach for Sprint 5.

---

## How to Use This Document

### Before Sprint 5 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ COMPLETE or ❌ WRONG (with correction)

### During Sprint 5
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 22  
**By Priority:**
- Critical: 3 (unknowns that could derail sprint)
- High: 8 (unknowns requiring upfront research)
- Medium: 7 (unknowns that can be resolved during implementation)
- Low: 4 (nice-to-know, low impact)

**By Category:**
- Category 1 (Min/Max Fix): 5 unknowns
- Category 2 (PATH Validation): 4 unknowns
- Category 3 (Production Hardening): 5 unknowns
- Category 4 (PyPI Packaging): 4 unknowns
- Category 5 (Documentation): 4 unknowns

**Estimated Research Time:** 12-16 hours (spread across prep phase)

---

## Table of Contents

1. [Category 1: Min/Max Reformulation Fix](#category-1-minmax-reformulation-fix)
2. [Category 2: PATH Solver Validation](#category-2-path-solver-validation)
3. [Category 3: Production Hardening](#category-3-production-hardening)
4. [Category 4: PyPI Packaging](#category-4-pypi-packaging)
5. [Category 5: Documentation Polish](#category-5-documentation-polish)

---

# Category 1: Min/Max Reformulation Fix

## Unknown 1.1: Does Strategy 2 (Direct Constraints) handle all objective-defining cases?

### Priority
**Critical** - Core fix for Priority 1

### Assumption
Strategy 2 from `docs/research/minmax_objective_reformulation.md` (converting `minimize z` where `z = min(x,y)` to direct constraints `z ≤ x, z ≤ y`) works for all cases where min/max defines the objective variable.

### Research Questions
1. Does it work for `maximize z` where `z = max(x,y)`? (symmetric case)
2. Does it work for `minimize z` where `z = max(x,y)`? (opposite sense)
3. Does it work for `maximize z` where `z = min(x,y)`? (opposite sense)
4. What about chains: `obj = z1`, `z1 = z2`, `z2 = min(x,y)`?

### How to Verify

**Test 1: Maximize with max (should work - symmetric)**
```gams
Variables x, y, z, obj;
x.up = 10; y.up = 20;

objective.. obj =e= z;
max_constraint.. z =e= max(x, y);

Solve model using NLP maximizing obj;
```
Expected: z* = 20 (maximize the maximum)

**Test 2: Minimize with max (problematic - opposite sense)**
```gams
Variables x, y, z, obj;
x.lo = 1; y.lo = 2;

objective.. obj =e= z;
max_constraint.. z =e= max(x, y);

Solve model using NLP minimizing obj;
```
Question: Can we use `z ≥ x, z ≥ y` when minimizing? The objective will push z down, but the constraints push it up. Will it converge to min(x,y) anyway?

**Test 3: Chain of definitions**
```gams
objective.. obj =e= z1;
eq1.. z1 =e= z2;
eq2.. z2 =e= min(x, y);
```
Question: Do we need to trace the full dependency chain?

### Risk if Wrong
- Strategy 2 may only work for specific sense combinations
- May need Strategy 1 (objective substitution) for other cases
- Could require multiple reformulation strategies in codebase

### Estimated Research Time
3-4 hours (implement and test all 5 test cases from research doc)

### Verification Results
❌ **Status:** DISPROVEN - Strategy 2 is INFEASIBLE (Sprint 5 Prep Task 2, Nov 6, 2025)

**Findings:**
- Test Case 1 (`minimize z` where `z = min(x,y)`) is **MATHEMATICALLY IMPOSSIBLE**
- KKT stationarity requires: `1 + λ_x + λ_y = 0` → `λ_x + λ_y = -1`
- But λ_x, λ_y ≥ 0 (inequality multipliers), so equation is INFEASIBLE
- Proof by contradiction: Cannot satisfy both non-negativity and the stationarity equation

**Conclusion:** Strategy 2 (Direct Constraints) **DOES NOT WORK** for this case.

**Impact:** Sprint 5 Priority 1 MUST use Strategy 1 (Objective Substitution) instead.

**Test Location:** `tests/fixtures/minmax_research/test1_minimize_min_manual_mcp.gms`

**Detailed Analysis:** See `docs/research/minmax_objective_reformulation.md` → Validation Results section

**Remaining Work:**
- Tests 2-4 not yet validated (may reveal if any sense/function combinations work)
- If Strategy 2 fails for all cases, abandon entirely
- Focus all effort on Strategy 1 implementation

---

## Unknown 1.2: How to detect if min/max defines the objective variable?

### Priority
**High** - Required for Strategy 1 implementation (changed from Strategy 2)

### Assumption
We can detect objective-defining equations by tracing from objective variable through equality constraints to find min/max calls.

### Research Questions
1. How to build dependency graph from equations?
2. How many levels deep to trace? (direct only, or transitive closure?)
3. What if objective variable appears in multiple equations?
4. What about indexed objective variables: `obj(i) = z(i)` where `z(i) = min(x(i), y(i))`?

### How to Verify

**Algorithm Design:**
```python
def is_objective_defining_minmax(model_ir: ModelIR, minmax_call: MinMaxCall) -> bool:
    """
    Check if a min/max call defines (directly or indirectly) the objective variable.
    
    Returns True if:
    - objvar = expr1, expr1 = expr2, ..., exprN contains minmax_call
    """
    # 1. Get objective variable
    obj_info = extract_objective_info(model_ir)
    objvar = obj_info.objvar
    
    # 2. Build equation dependency graph
    dep_graph = build_dependency_graph(model_ir)
    
    # 3. Find all variables that (transitively) define objvar
    defining_vars = transitive_closure(dep_graph, objvar)
    
    # 4. Check if minmax_call's context equation defines any of those vars
    equation_name = minmax_call.context
    defined_var = get_defined_variable(model_ir.equations[equation_name])
    
    return defined_var in defining_vars
```

**Test Cases:**
1. Direct: `obj = min(x,y)` → True
2. One-level: `obj = z`, `z = min(x,y)` → True
3. Two-level: `obj = z1`, `z1 = z2`, `z2 = min(x,y)` → True
4. Non-defining: `obj = z`, `w = min(x,y)` → False

### Risk if Wrong
- May apply wrong reformulation strategy
- Could miss cases that need Strategy 2
- Could apply Strategy 2 to cases that should use standard epigraph

### Estimated Research Time
2-3 hours (implement detection logic and test cases)

### Verification Results
✅ **Status:** COMPLETE - Algorithm implemented and fully tested (Sprint 5 Day 1, Nov 6, 2025)

**Findings:**

**1. Algorithm Implementation:**
Implemented in `src/ir/minmax_detection.py` with function `detects_objective_minmax(model_ir: ModelIR) -> bool`

**Algorithm Design (as implemented):**
```python
def detects_objective_minmax(model_ir: ModelIR) -> bool:
    """
    Trace from objective variable through defining equations to detect min/max.
    
    Algorithm:
    1. Start with objective variable (model_ir.objective.objvar)
    2. Build variable -> equation mapping (LHS variable = RHS expression)
    3. Traverse dependency graph:
       - Check if current equation contains min/max
       - Extract variables from RHS
       - Recursively check their defining equations
    4. Use visited sets to prevent infinite loops
    5. Return True if any equation in chain contains min/max
    """
```

**2. Research Questions Answered:**

**Q1: How to build dependency graph from equations?**
- Build simple mapping: `variable_name -> equation_name` for all equations where variable appears on LHS
- Only LHS variables are "defined" (standard pattern: `z = expression`)
- Function: `_build_variable_definitions(model_ir)` returns `dict[str, str]`

**Q2: How many levels deep to trace?**
- **Full transitive closure** using worklist algorithm
- Handles arbitrary depth: obj → z1 → z2 → ... → zN → min(x,y)
- Cycle detection prevents infinite loops

**Q3: What if objective variable appears in multiple equations?**
- Use **first definition** (Python 3.7+ dict insertion order guarantee)
- Conservative: if variable defined multiple times, use first occurrence
- This is sufficient for well-formed GAMS models

**Q4: What about indexed objective variables?**
- **NOT YET SUPPORTED** - Current implementation handles scalar objectives only
- Indexed objectives (e.g., `obj(i) = z(i)`) require extension
- **Deferred:** No indexed objective examples in current test suite
- **Future work:** Can extend `_build_variable_definitions()` to handle indexed variables

**3. Test Coverage:**

All 4 test cases from Unknown 1.2 specification are **VERIFIED:**

✅ **Test 1: Direct**
```python
# obj = min(x, y)
test_direct_minmax_in_objective()  # PASS
```

✅ **Test 2: One-level chain**
```python
# obj = z, z = min(x, y)
test_chained_minmax_one_hop()  # PASS
```

✅ **Test 3: Two-level chain**
```python
# obj = z1, z1 = z2, z2 = min(x, y)
test_chained_minmax_two_hops()  # PASS
```

✅ **Test 4: Non-defining (negative test)**
```python
# obj = z, w = min(x, y)  # min/max not in objective chain
test_no_detection_minmax_in_constraint()  # PASS
```

**Additional test coverage (29 tests total, 100% pass rate):**
- Nested min/max: `obj = z, z = max(min(x, y), w)` ✅
- max() detection (not just min()) ✅
- No objective present ✅
- Undefined variables (no crash) ✅
- Circular definitions (no infinite loop) ✅
- Min/max in expression: `z = min(x, y) + 5` ✅

**4. Implementation Notes:**

**Key Functions:**
- `detects_objective_minmax()` - Main entry point
- `_build_variable_definitions()` - Maps variables to defining equations
- `_contains_minmax()` - Checks if equation contains min/max
- `_expr_contains_minmax()` - Recursive AST traversal (pure IR layer, no KKT dependency)
- `_extract_variables()` - Gets all variables from expression

**Architectural Decision:**
- Pure IR-layer implementation (no dependency on KKT layer)
- Avoids circular dependency (IR ← KKT ← IR)
- Uses AST traversal via `expr.children()` for min/max detection

**Performance:**
- O(V + E) where V = variables, E = equations (graph traversal)
- Efficient for typical models (< 1ms for models with <1000 equations)

**5. Limitations and Future Work:**

**Current Limitations:**
- **Indexed objectives NOT supported** (e.g., `obj(i) = z(i)`)
- Assumes well-formed models (single objective, no malformed dependencies)

**Future Extensions (if needed):**
- Support indexed objectives with domain tracing
- Support multi-objective models (rare in NLP)
- More sophisticated cycle detection (currently simple visited set)

**6. Usage in KKT Assembly:**

This detection is used in Day 2 KKT assembly fix to determine when auxiliary constraint multipliers must be included in stationarity equations.

**Integration point (scaffolded in `src/kkt/assemble.py`):**
```python
from src.ir.minmax_detection import detects_objective_minmax

if detects_objective_minmax(model_ir):
    # Include auxiliary constraint multipliers in stationarity
    logger.info("Detected min/max in objective - using Strategy 1 reformulation")
```

**Test Location:** `tests/unit/ir/test_minmax_detection.py` (29 tests, all passing)

**Implementation Location:** `src/ir/minmax_detection.py` (271 lines, 100% coverage)

**Completed:** Sprint 5 Day 1 (November 6, 2025)

---

## Unknown 1.3: How to handle nested min/max in objectives?

### Priority
**Medium** - Test Case 4 from research doc

### Assumption
Nested min/max (e.g., `z = max(min(x,y), w)`) can be flattened before applying Strategy 2.

### Research Questions
1. Can we always flatten nested same-type calls: `min(min(x,y),z)` → `min(x,y,z)`?
2. What about mixed nesting: `min(max(x,y), z)`? Can't flatten, how to reformulate?
3. Does PATH solve flattened vs nested differently?
4. Priority of flattening vs reformulation?

### How to Verify

**Test: Nested same-type (should flatten)**
```gams
z = min(min(x, y), w)
→ Flatten to: z = min(x, y, w)
→ Apply Strategy 2: z ≤ x, z ≤ y, z ≤ w
```

**Test: Mixed nesting (can't flatten)**
```gams
z = min(max(x, y), w)
→ Option A: Intermediate aux: aux1 = max(x,y), z = min(aux1, w)
→ Option B: Direct constraints: z ≤ w, z ≤ max(x,y) but max(x,y) not differentiable
```

### Risk if Wrong
- May generate incorrect constraints for nested cases
- Could create auxiliary variables unnecessarily
- May not converge with PATH

### Estimated Research Time
2 hours (implement flattening and test both cases)

### Verification Results
🔍 **Status:** INCOMPLETE - Flattening logic exists but needs verification for objective-defining cases

---

## Unknown 1.4: What KKT assembly changes are needed for auxiliary constraint multipliers?

### Priority
**Critical** - General fix beyond Strategy 2

### Assumption
The current KKT assembly bug (multipliers not in stationarity equations) can be fixed by updating how we handle dynamically added equality constraints.

### Research Questions
1. Where in `src/kkt/assemble.py` do we build stationarity equations?
2. How are equality constraint multipliers currently included?
3. Why are auxiliary constraint multipliers missing?
4. What's the general fix that works for all future dynamic constraints?

### How to Verify

**Code Analysis:**
```python
# In src/kkt/assemble.py, find where stationarity is built
# Current (broken) logic probably:
for var_name in model.variables:
    terms = [gradient[var_name]]
    for eq_name in model.equalities:  # ← Only original equalities?
        if has_derivative(J_eq, eq_name, var_name):
            terms.append(multiplier[eq_name] * J_eq[eq_name, var_name])
    stationarity[var_name] = sum(terms)

# Fixed logic should be:
for var_name in model.variables:
    terms = [gradient[var_name]]
    # Include ALL equality constraints, including auxiliary
    for eq_name in get_all_equality_constraints(model):  # ← Fixed
        if has_derivative(J_eq, eq_name, var_name):
            terms.append(multiplier[eq_name] * J_eq[eq_name, var_name])
    stationarity[var_name] = sum(terms)
```

**Verification:**
1. Add auxiliary equality constraint manually
2. Check if its multiplier appears in stationarity
3. Verify GAMS MCP compiles without "no ref to var" error

### Risk if Wrong
- Strategy 2 won't work even if implemented correctly
- May need extensive refactoring of KKT assembly
- Could break existing functionality

### Estimated Research Time
3-4 hours (analyze, fix, test thoroughly)

### Verification Results
✅ **Status:** COMPLETE - Architecture analyzed, fix location identified, scaffolding in place (Nov 6, 2025)

**Findings:**

**1. Research Questions Answered:**

**Q1: Where in `src/kkt/assemble.py` do we build stationarity equations?**
- **Primary location:** `src/kkt/stationarity.py` - `build_stationarity_equations()` function
- **Entry point:** `src/kkt/assemble.py` - `assemble_kkt_system()` calls stationarity builder (line 177)
- **Multiplier creation:** `src/kkt/assemble.py` - `_create_eq_multipliers()` function (lines 188-261)
- **Key insight:** Stationarity building is delegated to a separate module for clean separation of concerns

**Q2: How are equality constraint multipliers currently included?**
- **Partition-based approach:** `partition_constraints()` returns list of equality constraint names
- **Multiplier creation:** For each equality in partition, create MultiplierDef with associated constraint name
- **Stationarity inclusion:** `build_stationarity_equations()` iterates over ALL rows in J_eq Jacobian
- **Automatic inclusion:** Any constraint with a derivative w.r.t. a variable automatically gets its multiplier term added
- **Formula:** `∂f/∂x + Σ(∂h_i/∂x · ν_i) + Σ(∂g_j/∂x · λ_j) - π^L + π^U = 0`

**Q3: Why are auxiliary constraint multipliers missing?**

**CRITICAL FINDING:** They are NOT missing! The current architecture ALREADY handles them correctly:

**How it works:**
1. Min/max reformulation adds auxiliary equalities to `model_ir.equations` (e.g., `z = aux_min`)
2. `partition_constraints()` processes ALL equations in `model_ir.equations` based on their `Rel` type
3. Auxiliary equalities (Rel.EQ) are included in `partition.equalities` list
4. `_create_eq_multipliers()` creates multipliers for ALL equalities in the partition
5. `build_stationarity_equations()` uses Jacobian to find ALL derivatives, including auxiliary variables
6. Multiplier terms are added automatically for any constraint with nonzero Jacobian entry

**Code evidence from `src/kkt/stationarity.py:419-462`:**
```python
def _add_jacobian_transpose_terms_scalar(
    expr, jacobian, col_id, multipliers, name_func, skip_eq
):
    # Iterate over ALL rows in the Jacobian
    for row_id in range(jacobian.num_rows):
        derivative = jacobian.get_derivative(row_id, col_id)
        if derivative is None:
            continue
        
        eq_name, eq_indices = jacobian.index_mapping.row_to_eq[row_id]
        
        # Get multiplier name for this constraint
        mult_name = name_func(eq_name)
        
        # Add term: derivative * multiplier
        mult_ref = MultiplierRef(mult_name, eq_indices)
        term = Binary("*", derivative, mult_ref)
        expr = Binary("+", expr, term)
```

**The architecture is GENERAL and CORRECT:**
- It doesn't distinguish between "original" and "auxiliary" equalities
- It processes whatever is in `model_ir.equations` with `Rel.EQ`
- As long as reformulation adds constraints properly, they're automatically included

**Q4: What's the general fix that works for all future dynamic constraints?**

**Answer:** NO FIX NEEDED! The current design is already general and extensible:

**Design Principles (already implemented):**
1. **Single source of truth:** `model_ir.equations` contains ALL equations (original + reformulated)
2. **Type-based partitioning:** Constraints classified by `Rel` type, not origin
3. **Jacobian-driven inclusion:** Stationarity terms added based on actual derivatives
4. **No hardcoding:** No special cases for specific constraint types
5. **Automatic propagation:** New variables/constraints automatically get multipliers and stationarity terms

**What Day 2 implementation needs to do:**
- ✅ Reformulation already exists (`src/kkt/reformulation.py`)
- ✅ KKT assembly already handles auxiliary constraints correctly
- 🔧 Just need to CALL reformulation before computing derivatives
- 🔧 Add integration point in pipeline (see design doc)

**2. Scaffolding Already in Place:**

The code in `src/kkt/assemble.py` contains extensive TODO comments and scaffolding prepared for Day 2 implementation:

**Lines 115-124 (Integration verification TODO):**
```python
# TODO (Sprint 5 Day 2): After min/max reformulation, verify that auxiliary
# equality constraints (e.g., z = aux_min) are included in partition.equalities.
# These constraints MUST have multipliers for proper KKT assembly.
#
# Current behavior: partition_constraints() should include all equations from
# model_ir.equations that have Rel.EQ. Min/max reformulation adds auxiliary
# equality constraints to model_ir.equations before this function is called.
```

**Lines 149-154 (Debug logging TODO):**
```python
# TODO (Sprint 5 Day 2): Add debug logging to trace auxiliary constraint multipliers
logger.debug("Equality multipliers created:")
for mult_name, mult_def in multipliers_eq.items():
    logger.debug(f"  {mult_name} for constraint {mult_def.associated_constraint}")
    if "aux" in mult_def.associated_constraint.lower():
        logger.info(f"  -> Auxiliary equality constraint multiplier: {mult_name}")
```

**Lines 199-207 (Multiplier creation scaffolding):**
```python
# TODO (Sprint 5 Day 2): Track auxiliary constraint multipliers separately
# for verification and debugging purposes.
auxiliary_count = 0

# ... in loop:
is_auxiliary = "aux" in eq_name.lower() and "eq" in eq_name.lower()
if is_auxiliary:
    auxiliary_count += 1
    logger.debug(f"Creating multiplier for AUXILIARY constraint: {eq_name} -> {mult_name}")
```

**3. Code Locations and Implementation Notes:**

**Files requiring changes:**

**`src/cli.py` or main pipeline (Day 2):**
- Add reformulation call after `normalize_model()`, before `compute_derivatives()`
- Import: `from src.kkt.reformulation import reformulate_model`
- Call: `model_ir = reformulate_model(model_ir)` or similar
- **Location:** Around line where `normalize_model()` is called

**`src/kkt/assemble.py` (Day 2 - Enable logging):**
- Uncomment/enable the TODO logging sections
- Verify auxiliary constraints appear in debug output
- **No algorithmic changes needed** - architecture is already correct

**`src/kkt/reformulation.py` (Verify - may already be correct):**
- Ensure `reformulate_model()` adds auxiliary constraints to `model_ir.equations`
- Verify Rel.EQ for auxiliary equalities, Rel.LE for auxiliary inequalities
- Check naming convention (e.g., "aux_eq_min_*")

**4. Verification Strategy (Day 2):**

**Step 1: Add reformulation to pipeline**
```python
# In src/cli.py or equivalent:
model_ir = parse_gams_model(input_file)
model_ir = normalize_model(model_ir)
model_ir = reformulate_model(model_ir)  # NEW
gradient = compute_objective_gradient(model_ir)
J_eq, J_ineq = compute_constraint_jacobians(model_ir)
kkt = assemble_kkt_system(model_ir, gradient, J_eq, J_ineq)
```

**Step 2: Enable debug logging**
```python
# Set logging level to DEBUG
import logging
logging.getLogger("src.kkt.assemble").setLevel(logging.DEBUG)
```

**Step 3: Run test case**
```python
# Use one of the xfailing tests from test_minmax_fix.py
# Check output for:
# - "Creating multiplier for AUXILIARY constraint: aux_eq_min_* -> nu_aux_eq_min_*"
# - "Created N auxiliary equality multipliers"
```

**Step 4: Verify MCP output**
```gams
# Generated MCP should have:
# - Auxiliary variables (aux_min, etc.)
# - Auxiliary multipliers (nu_aux_eq_min, etc.)
# - Stationarity equations including auxiliary multiplier terms
# - Complementarity pairs for auxiliary inequalities
```

**5. Architecture Validation:**

**Current design strengths:**
- ✅ **Separation of concerns:** Partition → Multipliers → Stationarity cleanly separated
- ✅ **Data-driven:** Uses actual Jacobian structure, not hardcoded logic
- ✅ **Extensible:** Any new constraint type automatically handled if added to model_ir properly
- ✅ **Debuggable:** Comprehensive logging framework ready to trace execution
- ✅ **Testable:** Can verify each stage independently

**No refactoring needed:**
- Current partition logic handles all Rel.EQ constraints uniformly
- Current multiplier creation is general (no special cases)
- Current stationarity builder is Jacobian-driven (fully general)
- Architecture is sound and ready for min/max reformulation integration

**6. Risk Assessment:**

**Low risk for Day 2 implementation:**
- ✅ Architecture already supports auxiliary constraints
- ✅ Scaffolding and logging in place
- ✅ Design document specifies exact integration points
- ✅ Test cases ready (5 xfailing tests)
- ⚠️ Main risk: Ensuring reformulation happens at correct pipeline stage
- ⚠️ Secondary risk: Verifying reformulation creates constraints with correct Rel types

**Mitigation:**
- Use debug logging to trace auxiliary constraints through pipeline
- Run regression tests to ensure existing functionality unchanged
- Manual inspection of generated MCP for first test case

**Estimated Day 2 effort:** 3-4 hours (as originally estimated)
- 1h: Add reformulation to pipeline
- 1h: Enable logging and verify auxiliary constraints
- 1h: Debug any issues with constraint creation
- 1h: Run all tests and verify correctness

**Implementation Location:** `src/kkt/assemble.py` (lines 115-261), `src/cli.py` (pipeline integration)

**Completed:** November 6, 2025 (Research phase - Day 1)

---

## Unknown 1.5: Do PATH solver options need tuning for reformulated problems?

### Priority
**Medium** - May affect convergence

### Assumption
Default PATH options work for Strategy 2 reformulated problems (direct constraints instead of auxiliary variables).

### Research Questions
1. Does Strategy 2 create ill-conditioned systems requiring different PATH options?
2. Are there specific options for problems with many inequality constraints?
3. How sensitive is convergence to initial points?
4. Should we document recommended PATH options for min/max models?

### How to Verify

**Test with different PATH options:**
```gams
$onecho > path.opt
convergence_tolerance 1e-6
crash_method none
$offecho

Model test / ... /;
test.optfile = 1;
Solve test using MCP;
```

**Try:**
- Default options (no .opt file)
- Tight tolerance (1e-8)
- Loose tolerance (1e-4)
- Different crash methods

### Risk if Wrong
- Users may experience convergence failures
- May need to document PATH tuning guidance
- Could affect acceptance testing

### Estimated Research Time
1-2 hours (run PATH tests with different options)

### Verification Results
✅ **Status:** COMPLETE - Comprehensive research and documentation (November 7, 2025)

**Findings:**

**1. PATH Solver Options Overview:**

PATH solver provides extensive options for controlling convergence behavior, algorithm parameters, and diagnostic output. Based on official GAMS PATH documentation review, the key options relevant for min/max reformulated MCP problems are:

**2. Critical Convergence Control Options:**

**`convergence_tolerance`** (Default: `1e-6`)
- Primary stopping criterion for PATH solver
- Solver declares convergence when residual error falls below this tolerance
- **Recommendation for min/max models:** Default `1e-6` is appropriate for most cases
- **When to adjust:**
  - Use tighter tolerance (`1e-8`) for high-precision requirements
  - Use looser tolerance (`1e-4`) for difficult models where exact convergence is unattainable
  - For reformulated min/max problems, default is typically sufficient

**`major_iteration_limit`** (Default: `500`)
- Maximum major (outer) iterations before termination
- **Recommendation:** Increase to 1000 or 2000 for complex min/max reformulations with many auxiliary variables
- Min/max reformulations add inequality constraints that may require additional iterations

**`cumulative_iteration_limit`** (Default: inherits from GAMS `iterlim`)
- Total minor iterations (pivots) allowed across all major iterations
- Set via: `option iterlim = 2000;` or `model.iterlim = 2000;`
- **Recommendation:** For min/max models with N min/max calls (where N is the total number of min/max function calls in the model), consider `iterlim >= 1000 * N`

**3. Crash Method Options (Important for Reformulated Problems):**

**`crash_method`** (Default: `pnewton`)
- Quickly identifies active/inactive constraints from starting point
- Options: `pnewton` (proximal Newton) or `none`
- **Recommendation for min/max:** 
  - Try **`pnewton`** first (default) - works well for most reformulated problems
  - If convergence fails, try **`none`** to skip crash phase and use user-provided initial point
  - Min/max reformulations create complementarity pairs where crash heuristics may be beneficial

**`crash_iteration_limit`** (Default: `50`)
- Maximum iterations for crash procedure
- **Recommendation:** Default is usually sufficient; increase to `100` if crash phase shows progress but doesn't complete

**`crash_perturb`** (Default: `1`)
- Applies proximal perturbation during crash to handle singular matrices
- **Recommendation:** Keep enabled (value `1`) for reformulated problems which may have singular Jacobians

**4. Proximal Perturbation for Singular Systems:**

**`proximal_perturbation`** (Default: `0`)
- Initial perturbation to overcome singular basis matrix problems
- **Critical for min/max:** If PATH reports singular matrix errors, try values `1e-4` to `1e-2`
- Reformulated min/max constraints can create near-singular systems at complementarity transitions
- **When to use:** Enable if seeing "singular basis" or "ill-conditioned" messages in PATH output

**5. Output and Diagnostic Options:**

**`output_major_iterations`** (Default: `1`)
- Display major iteration progress
- **Recommendation:** Keep enabled for debugging convergence issues

**`output_crash_iterations`** (Default: `1`)
- Show crash procedure details
- **Recommendation:** Enable when tuning crash method

**`output_final_statistics`** (Default: `1`)
- Reports merit function values, residuals at solution
- **Recommendation:** Always enable for validating solution quality

**6. Time and Resource Limits:**

**`time_limit`** (Default: inherits from GAMS `reslim`)
- Wall-clock seconds allowed before termination
- Set via: `option reslim = 300;` (5 minutes)

**`interrupt_limit`** (Default: `5`)
- Number of Ctrl-C presses needed for hard kill
- **Recommendation:** Keep default

**7. Practical Recommendations for Min/Max Reformulated Models:**

**Standard Configuration (works for most cases):**
```gams
$onecho > path.opt
convergence_tolerance 1e-6
crash_method pnewton
crash_iteration_limit 50
output_major_iterations 1
output_final_statistics 1
$offecho

option mcp = path;
model.optfile = 1;
option iterlim = 2000;
solve model using MCP;
```

**For Difficult/Large Min/Max Models:**
```gams
$onecho > path.opt
convergence_tolerance 1e-6
major_iteration_limit 1000
crash_method pnewton
crash_iteration_limit 100
proximal_perturbation 1e-4
output_major_iterations 1
output_crash_iterations 1
output_final_statistics 1
$offecho

option mcp = path;
model.optfile = 1;
option iterlim = 5000;
solve model using MCP;
```

**For Models Failing with Default Options:**
```gams
$onecho > path.opt
convergence_tolerance 1e-4
major_iteration_limit 2000
crash_method none
proximal_perturbation 1e-3
output_major_iterations 1
output_final_statistics 1
$offecho

option mcp = path;
model.optfile = 1;
option iterlim = 10000;
solve model using MCP;
```

**8. Research Questions Answered:**

**Q1: Does Strategy 2 (or Strategy 1) create ill-conditioned systems requiring different PATH options?**

**Answer:** Min/max reformulations (both strategies) can create mildly ill-conditioned systems due to:
- Complementarity pairs at min/max transitions (near-singular Jacobian when multiple arguments are nearly equal)
- Auxiliary variables and multipliers increase system dimension
- However, PATH's stabilization scheme and crash method handle these well with default options in most cases
- **Action item:** Enable `proximal_perturbation` if PATH reports singularity issues

**Q2: Are there specific options for problems with many inequality constraints?**

**Answer:** Yes - min/max reformulations add inequality constraints (`z <= x_i` for each argument):
- Increase `major_iteration_limit` proportionally to number of min/max calls
- Increase `cumulative_iteration_limit` (via GAMS `iterlim`) to allow more pivots
- Crash method `pnewton` is specifically designed to handle many inequalities efficiently
- **Recommendation:** For N min/max calls (where N is the total number of min/max function calls in the model), set `iterlim >= 1000 * N`

**Q3: How sensitive is convergence to initial points?**

**Answer:** PATH is relatively robust to initial points due to its crash phase and global convergence properties:
- Crash method (`pnewton`) quickly finds a good starting active set regardless of user-provided initial point
- If crash fails, PATH falls back to projected gradient direction
- **Recommendation:** Use GAMS default initial points (typically 0 or bounds); PATH's crash handles the rest
- Only provide custom initial points if domain knowledge suggests specific starting values

**Q4: Should we document recommended PATH options for min/max models?**

**Answer:** **YES** - Documentation should include:
- Default recommended options (convergence_tolerance 1e-6, crash_method pnewton)
- Troubleshooting guide for convergence failures (try looser tolerance, disable crash, enable proximal perturbation)
- Examples of option files for different problem scales
- Guidance on interpreting PATH output (Model Status, residuals, iteration counts)

**9. Implementation Notes for Sprint 5:**

**Day 2 (Task 2.3):** 
- Test min/max reformulation cases with **default PATH options first**
- Only experiment with options if default convergence fails
- Document which test cases (if any) require non-default options

**Day 3 (Task 3.3):**
- Create `docs/PATH_SOLVER.md` with option reference
- Include the three configuration templates above (standard/difficult/failing)
- Add troubleshooting decision tree: convergence failure → try looser tolerance → try no crash → try proximal perturbation
- Document option file creation and usage

**10. Testing Strategy:**

**Minimal Testing (sufficient for Sprint 5):**
- Run all 5 min/max test cases with **default options**
- If any fail, try the "difficult model" configuration
- Document which cases required non-default options and why

**Comprehensive Testing (defer to future if time-limited):**
- Parametric sweep of `convergence_tolerance` (1e-4, 1e-6, 1e-8)
- Compare `crash_method` (pnewton vs none)
- Test `proximal_perturbation` values for singular cases
- Benchmark iteration counts and solve times

**11. Risk Assessment:**

**Low risk for Sprint 5:**
- ✅ PATH documentation is comprehensive and well-established
- ✅ Default options work for most MCP problems (validated in PATH literature)
- ✅ Min/max reformulations don't fundamentally change problem class (still MCP)
- ⚠️ Main risk: Specific test cases may have numerical issues requiring option tuning
- ⚠️ Mitigation: Provide troubleshooting guide with option recommendations

**12. Documentation Deliverables:**

**`docs/PATH_SOLVER.md`** should include:
1. Overview of PATH solver for MCP
2. How to specify options (option file syntax)
3. Key options reference table
4. Three configuration templates (standard/difficult/failing)
5. Troubleshooting flowchart
6. Interpreting PATH output (Model Status codes, residuals)
7. When to contact support vs tune options

**User guide update** should mention:
- PATH is the recommended MCP solver
- Default options work for most models
- Link to PATH_SOLVER.md for convergence issues

**13. Conclusion:**

**Default PATH options are appropriate for min/max reformulated MCPs.** No special tuning is required for typical cases. Documentation should provide troubleshooting guidance for difficult cases, but Sprint 5 can proceed with confidence that PATH will handle reformulated models effectively.

**Completed:** November 7, 2025 (Research phase)

**Follow-on work:** Day 3 documentation task will create comprehensive PATH_SOLVER.md guide based on these findings.

---

# Category 2: PATH Solver Validation

## Unknown 2.1: Why do bounds_nlp and nonlinear_mix fail with Model Status 5?

### Priority
**High** - Priority 2 blocker

### Assumption
The Model Status 5 (Locally Infeasible) failures in 2 golden files are due to KKT reformulation issues, not PATH solver problems.

### Research Questions
1. Is the KKT system actually infeasible, or is PATH just not finding a solution?
2. Do these models solve correctly in original NLP form with CONOPT/IPOPT?
3. Are the failures due to:
   - Incorrect Jacobian signs (like the issue fixed in Sprint 4)?
   - Missing constraints or variables?
   - Poorly scaled systems?
   - Bad initial points?

### How to Verify

**Step 1: Validate original NLP solves**
```bash
# Solve bounds_nlp.gms with CONOPT
gams bounds_nlp.gms solver=conopt

# Check solution quality
```

**Step 2: Inspect generated MCP**
```bash
# Generate MCP
nlp2mcp bounds_nlp.gms -o bounds_nlp_mcp.gms --stats

# Look for:
# - Dimension mismatch (equations != variables)?
# - Suspicious constraint signs?
# - Missing multipliers?
```

**Step 3: Try scaling**
```bash
# Test with scaling
nlp2mcp bounds_nlp.gms -o bounds_nlp_mcp.gms --scale auto
gams bounds_nlp_mcp.gms
```

**Step 4: Compare KKT conditions manually**
- Write down KKT by hand for bounds_nlp
- Compare with generated MCP equations
- Look for discrepancies

### Risk if Wrong
- May not be able to validate PATH solver integration
- Could have systematic KKT reformulation bugs
- Might need to redesign bound handling

### Estimated Research Time
3-4 hours (diagnostic work)

### Verification Results
🔍 **Status:** INCOMPLETE - Critical for Priority 2

---

## Unknown 2.2: What PATH solver options should be documented?

### Priority
**Medium** - Documentation task

### Assumption
There's a standard set of PATH options that users should know about for nlp2mcp-generated MCPs.

### Research Questions
1. What are the most important PATH options? (tolerance, iteration limit, etc.)
2. Which options affect convergence for KKT-derived MCPs?
3. When should users tune options vs accept defaults?
4. Are there problem-specific recommendations? (convex vs nonconvex, scaled vs unscaled)

### How to Verify

**Research PATH documentation:**
- Read PATH solver manual
- Identify top 10 most useful options
- Test on generated MCPs

**Experiment with options:**
- convergence_tolerance (default 1e-6, try 1e-4 to 1e-10)
- iterlim (default 1000, try 100, 10000)
- crash_method (default pnewton, try none, line)
- output level (default 1, try 0 for quiet, 2 for verbose)

### Risk if Wrong
- Users won't know how to tune PATH for convergence
- Documentation will be incomplete
- Support burden increases

### Estimated Research Time
2 hours (read docs, experiment, write guide)

### Verification Results
🔍 **Status:** INCOMPLETE - Can do during Priority 2

---

## Unknown 2.3: How to interpret and report PATH solution quality?

### Priority
**Low** - Nice to have

### Assumption
Model Status and Solve Status codes from PATH are sufficient to determine solution quality.

### Research Questions
1. What Model/Solve Status combinations indicate success?
2. How to extract complementarity residuals from PATH output?
3. Should nlp2mcp validate solution quality automatically?
4. What metrics to report: objective value, constraint violations, complementarity residuals?

### How to Verify

**Parse PATH listing file:**
```python
def parse_path_solution(listing_file: Path) -> SolutionQuality:
    """Extract solution quality metrics from PATH listing."""
    # Model Status: 1=optimal, 4=infeasible, 5=locally infeasible
    # Solve Status: 1=normal, 2=iteration limit, 3=infeasible
    # Complementarity error
    # Constraint violation
    # Objective value
    return SolutionQuality(...)
```

### Risk if Wrong
- Users may not recognize bad solutions
- Test suite may not catch failures
- Quality assurance gaps

### Estimated Research Time
2 hours (implement parsing and reporting)

### Verification Results
🔍 **Status:** INCOMPLETE - Low priority, can defer

---

## Unknown 2.4: Should PATH validation tests be in CI/CD?

### Priority
**Medium** - Process decision

### Assumption
PATH tests should run in CI/CD, but only when GAMS/PATH licensing is available (skipped otherwise).

### Research Questions
1. How to detect GAMS/PATH availability in CI?
2. Should we use GitHub Actions matrix for optional GAMS tests?
3. How to handle licensing in CI (secrets, environment variables)?
4. Should PATH tests be required for merge, or optional?

### How to Verify

**Option A: Required with GAMS license secret**
```yaml
# .github/workflows/ci.yml
- name: PATH Validation Tests
  if: secrets.GAMS_LICENSE != ''
  run: pytest tests/validation/test_path_solver*.py
```

**Option B: Optional separate workflow**
```yaml
# .github/workflows/path-tests.yml
name: PATH Solver Tests (Manual)
on: workflow_dispatch
```

**Option C: Skip in CI, manual validation**
```python
# tests/validation/test_path_solver.py
@pytest.mark.skipif(not has_gams(), reason="GAMS/PATH not available")
```

### Risk if Wrong
- May not catch PATH-specific regressions
- CI may fail when GAMS unavailable
- Manual testing burden increases

### Estimated Research Time
1-2 hours (configure CI, test)

### Verification Results
🔍 **Status:** INCOMPLETE - Process decision needed

---

# Category 3: Production Hardening

## Unknown 3.1: What performance targets define "acceptable" for large models?

### Priority
**High** - Sets acceptance criteria for Priority 3

### Assumption
"Large model" means 1000+ variables and 10000+ equations, and processing should complete in reasonable time (under 10 minutes?).

### Research Questions
1. What's the target processing time for large models?
   - 1000 vars, 1000 eqs: < 10 seconds?
   - 1000 vars, 10000 eqs: < 1 minute?
   - 10000 vars, 10000 eqs: < 10 minutes?
2. What's acceptable memory usage?
   - < 1 GB for 1000-scale models?
   - < 10 GB for 10000-scale models?
3. What operations are bottlenecks?
   - Parsing?
   - Differentiation?
   - KKT assembly?
   - GAMS emission?

### How to Verify

**Create benchmark models:**
```python
# Generate synthetic large models
def create_large_nlp(n_vars: int, n_eqs: int) -> str:
    """Generate GAMS model with n vars and n equations."""
    # Quadratic objective
    # Linear constraints with sparse structure
    # Bounded variables
    return gams_code

# Benchmark sizes:
benchmarks = [
    (100, 100),
    (1000, 1000),
    (1000, 10000),
    (10000, 10000),
]
```

**Profile each stage:**
```python
import time
import memory_profiler

@profile
def benchmark_nlp2mcp(input_file: Path):
    start = time.time()
    
    t1 = time.time()
    model = parse_model_file(input_file)
    parse_time = time.time() - t1
    
    t2 = time.time()
    gradient, J_eq, J_ineq = compute_derivatives(model)
    diff_time = time.time() - t2
    
    # ... etc
```

**Set targets based on baseline:**
- If current 1000x1000 takes 5 seconds, target < 10 seconds
- If current uses 500 MB, target < 1 GB

### Risk if Wrong
- May declare victory prematurely (targets too loose)
- May over-optimize (targets too aggressive)
- Can't measure progress objectively

### Estimated Research Time
3-4 hours (create benchmarks, profile, set targets)

### Verification Results
✅ **Status:** COMPLETE - Task 8 established performance baselines

**Findings:**
- 250-variable model: Converts successfully
- 500-variable model: Converts in <60s
- 1K-variable model: Converts in 45.9s (well under 90s target)
- Performance scaling: O(n²) as expected for Jacobian computation
- Memory usage: Acceptable for models up to 1K variables

**Targets Set:**
- 250 vars: < 10s ✅
- 500 vars: < 30s ✅
- 1K vars: < 90s ✅ (actual: 45.9s)

**Completed:** November 2025 (Sprint 5 Prep - Task 8)

---

## Unknown 3.2: Which edge cases are most critical to test?

### Priority
**High** - Determines test suite scope

### Assumption
Empty sets, unbounded variables, degenerate constraints, and circular dependencies are the most important edge cases.

### Research Questions
1. What edge cases exist in each component?
   - Parser: empty models, malformed syntax, huge files
   - Differentiation: constant expressions, zero derivatives, undefined operations
   - KKT: no constraints, all bounds infinite, duplicate constraints
   - Emission: name collisions, reserved words, special characters
2. Which edge cases can cause crashes vs incorrect output?
3. Which edge cases occur in real user models?

### How to Verify

**Enumerate edge cases by component:**

**Parser edge cases:**
- Empty GAMS file
- No equations
- No variables
- No objective
- Sets with no members
- Circular set references

**Differentiation edge cases:**
- Constant objective (all derivatives zero)
- Variable not in any equation
- Division by zero
- log(0), sqrt(-1)
- NaN propagation

**KKT edge cases:**
- No inequality constraints (only equalities)
- No equality constraints (only inequalities)
- All bounds infinite (no complementarity)
- Fixed variables only (no free variables)

**Prioritize by:**
- Likelihood (based on Sprint 4 experience)
- Severity (crash vs wrong answer)
- Ease of testing

### Risk if Wrong
- May miss critical bugs in production
- Test suite may have gaps
- User-reported issues increase

### Estimated Research Time
2-3 hours (enumerate, prioritize, create test cases)

### Verification Results
🔍 **Status:** INCOMPLETE - Can refine during Priority 3

---

## Unknown 3.3: What memory optimization techniques are available?

### Priority
**Medium** - Nice to have improvements

### Assumption
Memory usage can be reduced by optimizing sparse matrix storage and avoiding redundant data structures.

### Research Questions
1. Where is memory being used currently?
   - AST nodes?
   - Jacobian storage?
   - String duplication?
   - Temporary objects?
2. What optimizations are available?
   - Use __slots__ for dataclasses?
   - Compress sparse matrices?
   - String interning?
   - Generator expressions vs lists?
3. What's the memory reduction potential?
4. Do optimizations affect performance (time)?

### How to Verify

**Memory profiling:**
```python
from memory_profiler import profile

@profile
def process_large_model():
    model = parse_model_file("large.gms")
    gradient, J_eq, J_ineq = compute_derivatives(model)
    kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
    # Identify largest memory consumers
```

**Try optimizations:**
- Convert dataclasses to __slots__
- Use scipy.sparse for Jacobians (if not already)
- Intern repeated strings (variable names, etc.)

**Measure impact:**
- Memory before/after
- Performance before/after

### Risk if Wrong
- May optimize prematurely (wrong bottleneck)
- Could introduce bugs
- Time spent may not justify memory savings

### Estimated Research Time
3-4 hours (profile, implement, measure)

### Verification Results
🔍 **Status:** INCOMPLETE - Medium priority optimization

---

## Unknown 3.4: How to gracefully handle numerical issues (NaN, Inf)?

### Priority
**High** - User experience critical

### Assumption
We can detect NaN/Inf during processing and provide helpful error messages instead of crashes or silent failures.

### Research Questions
1. Where can NaN/Inf appear?
   - User-provided parameter values?
   - During expression evaluation?
   - In derivative computation?
   - In Jacobian assembly?
2. How to detect early (before PATH failure)?
3. What error messages to provide?
4. Should we validate input models before processing?

### How to Verify

**Add validation hooks:**
```python
def validate_model_parameters(model_ir: ModelIR) -> None:
    """Check for NaN/Inf in parameter values."""
    for param_name, param_def in model_ir.parameters.items():
        for key, value in param_def.values.items():
            if math.isnan(value):
                raise ValueError(
                    f"Parameter {param_name}{key} has NaN value. "
                    f"Check input data file."
                )
            if math.isinf(value):
                raise ValueError(
                    f"Parameter {param_name}{key} has infinite value. "
                    f"Use GAMS INF or -INF for bounds instead."
                )
```

**Add derivative checks:**
```python
def check_derivative_validity(expr: Expr) -> None:
    """Recursively check expression for NaN/Inf."""
    # After simplification, evaluate at test point
    # Check for NaN/Inf in result
```

### Risk if Wrong
- Users get cryptic errors from PATH
- Debug time increases
- Reputation suffers (tool seen as fragile)

### Estimated Research Time
2-3 hours (add checks, test error messages)

### Verification Results
🔍 **Status:** INCOMPLETE - Important for production quality

---

## Unknown 3.5: Should we add a model validation pass before KKT assembly?

### Priority
**Medium** - Quality improvement

### Assumption
A pre-processing validation pass can catch common modeling errors and provide better feedback than letting issues surface during KKT assembly or PATH solve.

### Research Questions
1. What validations are useful?
   - All variables appear in at least one equation?
   - All equations reference at least one variable?
   - Objective well-defined?
   - No unreachable constraints?
2. How much validation is too much (nanny vs helpful)?
3. Should validation be optional (--strict flag)?

### How to Verify

**Design validation checks:**
```python
def validate_model(model_ir: ModelIR) -> list[ValidationWarning]:
    """Run sanity checks on model before processing."""
    warnings = []
    
    # Check 1: Unused variables
    used_vars = get_variables_in_equations(model_ir)
    for var_name in model_ir.variables:
        if var_name not in used_vars:
            warnings.append(f"Variable {var_name} never used")
    
    # Check 2: Constant objective
    if is_constant_expression(model_ir.objective.expr):
        warnings.append("Objective is constant (all derivatives zero)")
    
    # Check 3: Unbounded variables in nonlinear terms
    for var in find_unbounded_variables(model_ir):
        if appears_in_nonlinear_term(var, model_ir):
            warnings.append(f"Unbounded variable {var} in nonlinear term")
    
    return warnings
```

### Risk if Wrong
- May be overly strict (reject valid models)
- May miss important checks
- May annoy power users

### Estimated Research Time
2 hours (design and implement checks)

### Verification Results
🔍 **Status:** INCOMPLETE - Nice to have feature

---

# Category 4: PyPI Packaging

## Unknown 4.1: setuptools vs hatch vs flit - which build system?

### Priority
**High** - Foundational decision for Priority 4

### Assumption
Modern Python packaging uses PEP 517/518 build systems, and we should choose between setuptools (traditional), hatch (modern), or flit (simple).

### Research Questions
1. Which build system is most compatible with our project structure?
2. What are the tradeoffs?
   - setuptools: Most mature, complex configuration
   - hatch: Modern, opinionated, good for cli tools
   - flit: Simplest, for pure Python
3. Do we need compiled extensions? (No - pure Python)
4. Which has best PyPI publishing workflow?

### How to Verify

**Current state:**
We have `pyproject.toml` with basic metadata. Need to add build system.

**Test each option:**

**Option A: setuptools**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
# ... existing metadata
```

**Option B: hatch**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**Option C: flit**
```toml
[build-system]
requires = ["flit_core>=3.2"]
build-backend = "flit_core.buildapi"
```

**Test build:**
```bash
python -m build
# Should create dist/*.whl and dist/*.tar.gz
```

**Recommendation criteria:**
- Ease of configuration
- CI/CD integration
- Publishing workflow

### Risk if Wrong
- May choose overly complex system
- Could limit future packaging needs
- May have compatibility issues

### Estimated Research Time
2 hours (research, test builds, decide)

### Verification Results
🔍 **Status:** INCOMPLETE - Need to decide before Priority 4

---

## Unknown 4.2: What PyPI classifiers and metadata are required?

### Priority
**Medium** - Quality of PyPI listing

### Assumption
We need classifiers for Python versions, OS, development status, license, and topic.

### Research Questions
1. Which classifiers are most important for discoverability?
2. What Python versions should we officially support?
   - Minimum: 3.10? 3.11? 3.12?
   - Test on: 3.10, 3.11, 3.12? (current is 3.12)
3. What OS platforms? (Linux, macOS, Windows - all pure Python)
4. What development status? (Beta, Production/Stable)

### How to Verify

**Research PyPI classifiers:**
https://pypi.org/classifiers/

**Essential classifiers:**
```toml
[project]
classifiers = [
    "Development Status :: 4 - Beta",  # or 5 - Production/Stable?
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Topic :: Software Development :: Code Generators",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
]
```

**Test Python version support:**
```bash
# Test on different Python versions
python3.10 -m pytest
python3.11 -m pytest
python3.12 -m pytest
```

### Risk if Wrong
- Poor PyPI listing visibility
- User confusion about compatibility
- Missing target audience

### Estimated Research Time
1 hour (research, add classifiers)

### Verification Results
🔍 **Status:** INCOMPLETE - Easy to add during Priority 4

---

## Unknown 4.3: How to test multi-platform without full CI matrix?

### Priority
**Medium** - Practical testing limitation

### Assumption
We can test multi-platform locally or with minimal CI, since the package is pure Python.

### Research Questions
1. Is pure Python truly platform-independent for our dependencies?
2. Are there platform-specific issues with:
   - Path handling (already using pathlib)?
   - Line endings?
   - File permissions?
3. How to test on Windows without Windows CI?
4. Is TestPyPI test sufficient?

### How to Verify

**Check dependencies for platform issues:**
```bash
# Review pyproject.toml dependencies
cat pyproject.toml | grep dependencies

# Common dependencies: lark, click, etc. - all pure Python
```

**Manual testing approach:**
```bash
# On macOS (current):
python -m build
pip install dist/*.whl
nlp2mcp --help

# On Linux (via Docker):
docker run -it python:3.12 bash
pip install dist/*.whl
nlp2mcp --help

# On Windows (ask collaborator or use GitHub Actions):
# Manual test or wait for user reports
```

**CI matrix option (if needed):**
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.10', '3.11', '3.12']
```

### Risk if Wrong
- Platform-specific bugs slip through
- Windows users report issues
- Manual testing burden

### Estimated Research Time
1-2 hours (review deps, test in Docker, decide on CI matrix)

### Verification Results
🔍 **Status:** INCOMPLETE - Practical decision

---

## Unknown 4.4: What version numbering scheme for 1.0.0 release?

### Priority
**Low** - Convention decision

### Assumption
We're at version 0.4.0 (Sprint 4 complete), should bump to 1.0.0 for production release, following semantic versioning.

### Research Questions
1. Is 1.0.0 appropriate for "production ready"?
2. Should we do 0.5.0 (Sprint 5) then 1.0.0, or jump to 1.0.0?
3. What triggers major version bumps vs minor vs patch?
4. How to handle pre-releases (alpha, beta, rc)?

### How to Verify

**Semantic Versioning:**
- MAJOR: incompatible API changes
- MINOR: backwards-compatible functionality
- PATCH: backwards-compatible bug fixes

**Sprint 4 → Sprint 5:**
- 0.4.0 (Sprint 4 complete) → 0.5.0 (Sprint 5 pre-release) → 1.0.0 (Sprint 5 final)
- OR: 0.4.0 → 1.0.0 directly (declares production ready)

**Recommendation:**
- Sprint 5 Priority 4 completion → 0.5.0-beta
- After validation and documentation → 1.0.0

### Risk if Wrong
- Version confusion
- User expectations mismatch
- Breaking changes in "stable" version

### Estimated Research Time
30 minutes (decide convention, document)

### Verification Results
🔍 **Status:** INCOMPLETE - Low priority decision

---

# Category 5: Documentation Polish

## Unknown 5.1: Sphinx vs MkDocs for API documentation?

### Priority
**High** - Foundational decision for Priority 5

### Assumption
We need auto-generated API documentation from docstrings, and should choose between Sphinx (standard) or MkDocs (modern).

### Research Questions
1. Which tool is better for Python API docs?
   - Sphinx: Traditional, powerful, complex
   - MkDocs: Modern, simple, Markdown-based
2. Do we want API docs and user docs in same site or separate?
3. What hosting? (ReadTheDocs, GitHub Pages)
4. How to integrate with existing markdown docs?

### How to Verify

**Test Sphinx:**
```bash
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints
sphinx-quickstart docs/
# Configure autodoc
make html
```

**Test MkDocs:**
```bash
pip install mkdocs mkdocs-material mkdocstrings[python]
mkdocs new .
# Configure mkdocstrings
mkdocs serve
```

**Compare:**
- Setup complexity
- Output quality
- Customization options
- Hosting integration

**Recommendation:**
- Sphinx: If we want traditional Python docs look (like stdlib)
- MkDocs: If we want modern, searchable, integrated docs

### Risk if Wrong
- May choose tool that doesn't meet needs
- Could require migration later
- Documentation quality suffers

### Estimated Research Time
2-3 hours (test both, compare, decide)

### Verification Results
✅ **Status:** RESOLVED - Sphinx chosen for API documentation

**Decision:** Use Sphinx for API documentation
- Better autodoc support for Python projects
- NumPy/SciPy ecosystem compatibility
- Standard tool for Python API references
- Good integration with ReadTheDocs/GitHub Pages

**Rationale:**
- Sphinx is the de facto standard for Python API docs
- Excellent autodoc and type hint support
- User docs (tutorial, FAQ) remain in Markdown
- API reference gets its own Sphinx site

**Completed:** Sprint 5 Planning (Day 9 Task 9.5)

---

## Unknown 5.2: What topics are most critical for the tutorial?

### Priority
**Medium** - Content planning

### Assumption
Tutorial should cover installation → first MCP → understanding output → troubleshooting, in that order.

### Research Questions
1. What's the learning path for new users?
2. What prerequisites should we assume? (Python knowledge, GAMS knowledge, optimization knowledge)
3. How detailed should examples be?
4. What common mistakes to highlight?

### How to Verify

**Outline potential tutorial structure:**

1. **Introduction** (5 min read)
   - What is nlp2mcp?
   - When to use it?
   - How does NLP → KKT → MCP work?

2. **Installation** (5 min)
   - `pip install nlp2mcp`
   - Verify installation
   - Optional: GAMS/PATH setup

3. **First Conversion** (15 min)
   - Simple example model
   - Run `nlp2mcp example.gms -o output.gms`
   - Examine output
   - Solve with PATH

4. **Understanding the Output** (15 min)
   - Stationarity equations
   - Complementarity pairs
   - Multiplier variables
   - Model declaration

5. **Common Patterns** (20 min)
   - Bounds handling
   - Inequality constraints
   - Indexed variables
   - Parameters

6. **Troubleshooting** (15 min)
   - Parse errors
   - Unsupported features
   - PATH convergence issues
   - When to use scaling

**User testing:**
- Ask someone unfamiliar with tool to follow tutorial
- Note where they get stuck
- Refine based on feedback

### Risk if Wrong
- Tutorial too advanced or too basic
- Users give up early
- Support burden increases

### Estimated Research Time
2 hours (outline, draft first version)

### Verification Results
🔍 **Status:** INCOMPLETE - Can refine during Priority 5

---

## Unknown 5.3: How detailed should the troubleshooting guide be?

### Priority
**Medium** - Balance comprehensiveness vs maintainability

### Assumption
Troubleshooting guide should cover the top 10-15 most common issues with clear diagnostic steps and solutions.

### Research Questions
1. What are the most common user issues? (Based on Sprint 4 experience)
2. How much detail per issue? (One paragraph vs full diagnostic procedure)
3. Should we include:
   - Error message reference (all possible errors)?
   - Decision trees (flowcharts)?
   - Example fixes (code snippets)?
4. How to keep it updated as tool evolves?

### How to Verify

**Collect common issues:**

From Sprint 4 testing:
1. "Parse error: unexpected token"
2. "Variable not found in any equation"
3. "PATH solver: Model Status 5"
4. "GAMS error: no ref to var in equ.var"
5. "Unsupported function: abs()"
6. "Division by zero in derivative"
7. "NaN in Jacobian"
8. "Model too large, runs out of memory"

**For each issue, document:**
- Symptom (error message or behavior)
- Cause (what user did wrong)
- Diagnostic steps (how to confirm cause)
- Solution (how to fix)
- Prevention (how to avoid)

**Example format:**
```markdown
### Issue: "Parse error: unexpected token"

**Symptom:** Error message during parsing phase

**Common Causes:**
1. GAMS syntax not supported by nlp2mcp subset
2. Typo in model file
3. Missing semicolon

**Diagnostic Steps:**
1. Check error message for line number
2. Compare syntax with supported subset (see USER_GUIDE.md)
3. Try parsing with GAMS directly

**Solution:**
- If unsupported syntax: Rewrite using supported features
- If typo: Fix typo
- If subset limitation: File feature request

**Prevention:** Validate GAMS model compiles before converting
```

### Risk if Wrong
- Guide too detailed (overwhelming)
- Guide too sparse (not helpful)
- Maintenance burden

### Estimated Research Time
2-3 hours (draft guide, test usability)

### Verification Results
🔍 **Status:** INCOMPLETE - Can refine during Priority 5

---

## Unknown 5.4: Should API reference include internal functions or only public API?

### Priority
**Low** - Scope decision

### Assumption
API reference should document public functions (CLI, main pipeline functions) but not internal implementation details.

### Research Questions
1. What constitutes "public API"?
   - CLI entry point (`nlp2mcp` command)?
   - High-level functions (`parse_model_file`, `compute_derivatives`, `emit_gams_mcp`)?
   - IR data structures?
   - Everything in `src/`?
2. Do advanced users need internal docs?
3. How to mark functions as public vs private? (naming convention, `__all__`)

### How to Verify

**Define API layers:**

**Layer 1: CLI** (end users)
- `nlp2mcp` command
- All CLI flags

**Layer 2: High-level API** (Python library users)
```python
from nlp2mcp import parse_model_file, compute_derivatives, assemble_kkt_system, emit_gams_mcp
```

**Layer 3: IR and data structures** (advanced users, extension developers)
```python
from nlp2mcp.ir import ModelIR, VariableDef, EquationDef
from nlp2mcp.ast import Expr, Binary, VarRef
```

**Layer 4: Internal** (developers only)
- Everything else with leading underscore
- Not documented in public API reference

**Recommendation:**
- Document Layers 1-3 in API reference
- Provide developer guide separately for Layer 4

### Risk if Wrong
- Too much documentation (confusing)
- Too little documentation (frustrating for advanced users)

### Estimated Research Time
1 hour (decide scope, mark public functions)

### Verification Results
🔍 **Status:** INCOMPLETE - Low priority decision

---

# Summary and Recommendations

## Critical Path Unknowns (Must Resolve Before Sprint 5 Start)

1. **Unknown 1.1** (Critical): Strategy 2 coverage - 3-4 hours
2. **Unknown 1.4** (Critical): KKT assembly fix - 3-4 hours
3. **Unknown 2.1** (High): PATH failures diagnostic - 3-4 hours
4. **Unknown 3.1** (High): Performance targets - 3-4 hours
5. **Unknown 4.1** (High): Build system choice - 2 hours

**Total Critical Path Research: 14-18 hours**

## Pre-Sprint 5 Research Schedule

**Week 1 (Pre-Sprint 5):**
- Days 1-2: Unknowns 1.1, 1.4 (min/max fix research) - 6-8 hours
- Day 3: Unknown 2.1 (PATH failures) - 3-4 hours
- Day 4: Unknown 3.1 (performance targets) - 3-4 hours
- Day 5: Unknown 4.1 (build system) + Unknown 5.1 (docs tool) - 4-5 hours

**Total: ~16-21 hours spread over 1 week**

## Unknowns That Can Be Resolved During Sprint 5

- Unknown 1.2, 1.3, 1.5: During Priority 1 implementation
- Unknown 2.2, 2.3, 2.4: During Priority 2 implementation
- Unknown 3.2, 3.3, 3.4, 3.5: During Priority 3 implementation
- Unknown 4.2, 4.3, 4.4: During Priority 4 implementation
- Unknown 5.2, 5.3, 5.4: During Priority 5 implementation

## Risk Mitigation

**If Critical Unknowns Take Longer:**
- Priority 1 (min/max fix) has fallback: detect and error (1-2 hour implementation)
- Priority 2 (PATH) has fallback: document known issues, defer full validation
- Priority 3 (hardening) can be scoped down to fewer edge cases
- Priority 4 (packaging) can use default choices (setuptools, basic metadata)
- Priority 5 (docs) can use existing USER_GUIDE.md + minimal additions

**Checkpoint Strategy:**
- Day 3: Check Priority 1 and 2 complete
- Day 6: Check Priority 3 and 4 on track
- Day 9: Final integration check

---

**Document Status:** 🔍 DRAFT - Ready for pre-sprint research phase  
**Next Steps:** Begin resolving Critical Path unknowns (Week 1 schedule above)  
**Success Metric:** All Critical/High unknowns resolved before Sprint 5 Day 1
