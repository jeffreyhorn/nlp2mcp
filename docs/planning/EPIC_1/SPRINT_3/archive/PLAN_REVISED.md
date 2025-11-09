# Sprint 3: KKT Synthesis + GAMS MCP Code Generation (REVISED)

**Duration:** 2 weeks (10 working days)  
**Start Date:** TBD  
**Goal:** Transform NLP models to runnable GAMS MCP files via KKT conditions

**Revision Note:** This plan addresses gaps identified in PLAN_REVIEW.md:
1. Added original data/alias emission tasks
2. Added bounds vs. explicit constraints detection
3. Added infinite bounds handling
4. Added objective variable/equation flow handling

---

## Overview

Sprint 3 completes the end-to-end NLP → MCP transformation by:

1. **KKT System Assembly** - Convert derivatives into KKT equations (stationarity + complementarity)
2. **GAMS Code Generation** - Emit valid GAMS MCP syntax from KKT system including original model symbols
3. **CLI Integration** - Create `nlp2mcp` command-line tool
4. **Golden Test Suite** - Text-based golden tests for all example models
5. **Optional GAMS Validation** - Verify generated MCP compiles/solves (if GAMS available)

### What We're Building

```
Input:  examples/simple_nlp.gms (GAMS NLP model)
        ↓
Output: simple_nlp_mcp.gms (GAMS MCP model with KKT conditions)
        - Original Sets, Aliases, Parameters (re-emitted)
        - Multiplier variables (λ, ν, π^L, π^U)
        - Stationarity equations
        - Complementarity conditions
        - Model MCP declaration
```

### Key Components

1. **`src/kkt/assemble.py`** - KKT system assembler
   - Partition constraints (equalities h, inequalities g) with duplicate detection
   - Filter infinite bounds (skip π^L/π^U for ±INF)
   - Create multiplier variables for each constraint row
   - Handle objective variable specially
   - Build stationarity: ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0
   - Build complementarity: F_λ ⊥ λ, F_ν = h(x), F_π^L ⊥ π^L, F_π^U ⊥ π^U

2. **`src/emit/emit_gams.py`** - GAMS code generator  
   - Emit original Sets, Aliases, Parameters (from ModelIR)
   - Emit Sets for multiplier indexing
   - Emit Variables blocks (primal + multipliers)
   - Emit Equations blocks with index expansion
   - Generate Model MCP with complementarity pairs
   - Handle sign conventions correctly

3. **`src/cli.py`** - Command-line interface
   - `nlp2mcp input.gms -o output.gms`
   - Options for comments, validation, verbosity

4. **Golden Test Suite** - End-to-end validation
   - Input `.gms` → Output `.gms` string comparison
   - 5 reference models with hand-verified outputs
   - Optional: Run GAMS compiler validation

---

## Success Metrics

### Primary Metrics

**Functional Completeness:**
- ✅ All 5 v1 example models convert successfully
- ✅ Generated MCP files compile in GAMS (syntax valid)
- ✅ Generated MCP includes all original model symbols
- ✅ No duplicate complementarity pairs for user-authored bounds
- ✅ Infinite bounds are skipped correctly
- ✅ Objective variable handled correctly
- ✅ Golden tests pass (generated output matches expected)
- ✅ CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`

**Code Quality:**
- ✅ All unit tests pass (expect ~60 new tests, up from 50)
- ✅ All integration tests pass (expect ~18 new tests, up from 15)
- ✅ All e2e/golden tests pass (5 tests)
- ✅ Type checking passes (`mypy src/`)
- ✅ Linting passes (`ruff check`)
- ✅ Code formatted (`ruff format`)

**Documentation:**
- ✅ KKT assembly documented with mathematical notation
- ✅ Bounds handling strategy documented
- ✅ Objective variable handling documented
- ✅ GAMS emission documented with template examples
- ✅ CLI usage documented in README
- ✅ All public functions have docstrings

### Sprint Health Metrics

**Velocity:**
- Complete 1 day's goals per day (no slippage beyond Day 7 checkpoint)
- No more than 2 days behind schedule by mid-sprint checkpoint

**Quality:**
- No more than 3 bugs per day found in previous days' work
- API contract tests still pass throughout sprint
- No regression in Sprint 1/2 tests

**Integration:**
- Integration issues caught within 1 day (not on Day 9 like Sprint 2)
- Early smoke test passing by Day 2
- Mid-sprint checkpoint shows all components integrating

### Optional Stretch Goals

- 🎯 Generated MCP solves successfully in GAMS/PATH (if GAMS available)
- 🎯 10 total example models (5 additional beyond v1 set)
- 🎯 Performance: Convert models in < 1 second
- 🎯 Error messages with source locations and suggestions

---

## Day-by-Day Plan

### Day 1: Foundation & Data Structures

**Goal:** Define KKT system data structures and partition constraints with duplicate detection

**Tasks:**

1. **Create KKT Data Structures** (2 hours)
   - File: `src/kkt/kkt_system.py`
   - Define `KKTSystem` dataclass:
     ```python
     @dataclass
     class KKTSystem:
         # Primal problem
         model_ir: ModelIR
         
         # Derivatives
         gradient: GradientVector
         J_eq: JacobianStructure
         J_ineq: JacobianStructure
         
         # Multipliers (filtered for infinite bounds)
         multipliers_eq: dict[str, MultiplierDef]  # ν for equalities
         multipliers_ineq: dict[str, MultiplierDef]  # λ for inequalities  
         multipliers_bounds_lo: dict[str, MultiplierDef]  # π^L (finite only)
         multipliers_bounds_up: dict[str, MultiplierDef]  # π^U (finite only)
         
         # KKT equations
         stationarity: dict[str, EquationDef]  # One per variable instance
         complementarity_ineq: dict[str, ComplementarityPair]
         complementarity_bounds_lo: dict[str, ComplementarityPair]
         complementarity_bounds_up: dict[str, ComplementarityPair]
         
         # Metadata
         skipped_infinite_bounds: list[tuple[str, str]]  # (var_name, bound_type)
         duplicate_bounds_warnings: list[str]  # Warnings for user-authored bounds
     
     @dataclass
     class MultiplierDef:
         name: str
         domain: tuple[str, ...]  # Index sets
         kind: Literal['eq', 'ineq', 'bound_lo', 'bound_up']
         associated_constraint: str  # Which constraint this is for
     
     @dataclass
     class ComplementarityPair:
         equation: EquationDef  # F(x, λ, ...)
         variable: str  # Variable name (e.g., "lam_g1")
         variable_indices: tuple[str, ...]
     ```

2. **Implement Enhanced Constraint Partitioning** (3 hours)
   - File: `src/kkt/partition.py`
   - Function: `partition_constraints(model_ir: ModelIR) -> PartitionResult`
   - **NEW:** Detect duplicate bounds (Review Adjustment #2)
     ```python
     @dataclass
     class PartitionResult:
         equalities: list[str]
         inequalities: list[str]
         bounds_lo: dict[str, BoundDef]  # Only finite bounds
         bounds_up: dict[str, BoundDef]  # Only finite bounds
         skipped_infinite: list[tuple[str, str]]  # (var, 'lo'/'up')
         duplicate_warnings: list[str]  # User-authored bounds to skip
     
     def partition_constraints(model_ir: ModelIR) -> PartitionResult:
         # Equalities: equations with Rel.EQ
         equalities = [name for name in model_ir.equalities]
         
         # Inequalities: equations with Rel.LE (normalized to ≤ 0)
         # BUT: skip if they duplicate normalized_bounds
         inequalities = []
         duplicate_warnings = []
         
         for name in model_ir.inequalities:
             if name in model_ir.normalized_bounds:
                 continue  # Skip auto-generated bound equations
             
             # Check if this inequality duplicates a bound
             if _is_user_authored_bound(model_ir.inequalities[name]):
                 # e.g., user wrote "x(i) =L= 10" and we also have x.up = 10
                 if _duplicates_variable_bound(model_ir, name):
                     duplicate_warnings.append(
                         f"Equation {name} appears to be a bound constraint "
                         f"that duplicates variable bounds. Treating as inequality."
                     )
             
             inequalities.append(name)
         
         # Bounds: filter infinite bounds (Review Adjustment #3)
         bounds_lo = {}
         bounds_up = {}
         skipped_infinite = []
         
         for var_name, var_def in model_ir.variables.items():
             # Lower bounds
             if var_def.lo is not None:
                 if var_def.lo == float('-inf'):
                     skipped_infinite.append((var_name, 'lo'))
                 else:
                     bounds_lo[var_name] = BoundDef('lo', var_def.lo, var_def.domain)
             
             # Upper bounds
             if var_def.up is not None:
                 if var_def.up == float('inf'):
                     skipped_infinite.append((var_name, 'up'))
                 else:
                     bounds_up[var_name] = BoundDef('up', var_def.up, var_def.domain)
         
         return PartitionResult(
             equalities, inequalities, 
             bounds_lo, bounds_up,
             skipped_infinite, duplicate_warnings
         )
     ```

3. **Implement Objective Variable Detection** (1.5 hours)
   - File: `src/kkt/objective.py`
   - **NEW:** Handle objective variable special case (Review Adjustment #4)
   - Function: `extract_objective_info(model_ir: ModelIR) -> ObjectiveInfo`
     ```python
     @dataclass
     class ObjectiveInfo:
         objvar: str  # Name of objective variable
         objvar_indices: tuple[str, ...]  # Usually empty for scalar
         defining_equation: str  # Name of equation that defines objvar
         needs_stationarity: bool  # Whether to create stat equation for objvar
     
     def extract_objective_info(model_ir: ModelIR) -> ObjectiveInfo:
         """
         Extract objective variable and its defining equation.
         
         The objective variable appears in the objective function but is
         defined by an equation (e.g., obj =E= f(x)). We need to:
         1. Include the defining equation in the MCP
         2. Decide whether to create a stationarity row for objvar
         """
         obj = model_ir.objective
         objvar = obj.objvar
         
         # Find defining equation (usually named like "defobjective" or "objdef")
         defining_eq = None
         for eq_name, eq_def in model_ir.equations.items():
             # Check if LHS is just objvar and RHS is the expression
             if _is_objective_defining_equation(eq_def, objvar):
                 defining_eq = eq_name
                 break
         
         if defining_eq is None:
             raise ValueError(f"Could not find defining equation for objective variable {objvar}")
         
         # For standard NLP → MCP: objvar is free, no stationarity needed
         # (The gradient is w.r.t. the actual decision variables, not objvar)
         needs_stationarity = False
         
         return ObjectiveInfo(objvar, (), defining_eq, needs_stationarity)
     ```

4. **Create Multiplier Naming Convention** (1 hour)
   - File: `src/kkt/naming.py`
   - Functions:
     ```python
     def create_eq_multiplier_name(eq_name: str, indices: tuple) -> str:
         """nu_eqname(i,j) for equation eqname(i,j)"""
         
     def create_ineq_multiplier_name(eq_name: str, indices: tuple) -> str:
         """lam_eqname(i,j) for inequality eqname(i,j)"""
         
     def create_bound_lo_multiplier_name(var_name: str, indices: tuple) -> str:
         """piL_varname(i,j) for lower bound on varname(i,j)"""
         
     def create_bound_up_multiplier_name(var_name: str, indices: tuple) -> str:
         """piU_varname(i,j) for upper bound on varname(i,j)"""
     ```
   - Collision detection and prefix generation

5. **Write Unit Tests** (2.5 hours)
   - File: `tests/unit/kkt/test_partition.py`
   - Test `partition_constraints()` on simple_nlp, bounds_nlp
   - **NEW:** Test infinite bound filtering
   - **NEW:** Test duplicate bound detection
   - File: `tests/unit/kkt/test_objective.py`
   - **NEW:** Test objective variable extraction
   - File: `tests/unit/kkt/test_naming.py`
   - Test naming functions, collision handling

**Deliverables:**
- `src/kkt/kkt_system.py` - Data structures with new fields
- `src/kkt/partition.py` - Enhanced constraint partitioning
- `src/kkt/objective.py` - **NEW** Objective variable handling
- `src/kkt/naming.py` - Multiplier naming
- `tests/unit/kkt/` - Unit tests (expect ~18 tests, up from 15)

**Acceptance Criteria:**
- [ ] All data structures defined with complete type hints
- [ ] Partition correctly separates equalities, inequalities, bounds
- [ ] **NEW:** Infinite bounds are filtered out (±INF skipped)
- [ ] **NEW:** Duplicate user-authored bounds detected and warned
- [ ] **NEW:** Objective variable and defining equation extracted
- [ ] Naming convention handles all test cases
- [ ] Unit tests pass (18/18)
- [ ] Type checking passes
- [ ] Code formatted and linted

---

### Day 2: KKT Assembler - Stationarity

**Goal:** Build stationarity equations ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0

**Tasks:**

1. **Implement Stationarity Builder** (3.5 hours)
   - File: `src/kkt/stationarity.py`
   - Function: `build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]`
   - **MODIFIED:** Skip objective variable if needs_stationarity=False
   - For each variable instance `x(i1)`:
     ```python
     def build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]:
         """Build stationarity: ∇f + J^T λ - π^L + π^U = 0 for each var."""
         
         stationarity = {}
         obj_info = extract_objective_info(kkt.model_ir)
         
         # Iterate over all variable instances
         for col_id in range(kkt.gradient.num_cols):
             var_name, var_indices = kkt.gradient.index_mapping.col_to_var[col_id]
             
             # Skip objective variable (Review Adjustment #4)
             if var_name == obj_info.objvar:
                 continue
             
             # Start with gradient component
             F_x = kkt.gradient.get_derivative(col_id) or Const(0.0)
             
             # Add J_eq^T ν
             for eq_name in kkt.model_ir.equalities:
                 if eq_name == obj_info.defining_equation:
                     continue  # Skip objective defining equation in stationarity
                 
                 for row_id, entries in kkt.J_eq.entries.items():
                     if col_id in entries:
                         nu_name = create_eq_multiplier_name(eq_name, ...)
                         F_x = Binary("+", F_x, 
                                     Binary("*", entries[col_id], 
                                           MultiplierRef(nu_name, ...)))
             
             # Add J_ineq^T λ  
             for row_id, entries in kkt.J_ineq.entries.items():
                 if col_id in entries:
                     lam_name = create_ineq_multiplier_name(...)
                     F_x = Binary("+", F_x, 
                                 Binary("*", entries[col_id], 
                                       MultiplierRef(lam_name, ...)))
             
             # Subtract π^L (if finite bound exists)
             if var_name in kkt.multipliers_bounds_lo:
                 piL_name = create_bound_lo_multiplier_name(var_name, var_indices)
                 F_x = Binary("-", F_x, MultiplierRef(piL_name, var_indices))
             
             # Add π^U (if finite bound exists)
             if var_name in kkt.multipliers_bounds_up:
                 piU_name = create_bound_up_multiplier_name(var_name, var_indices)
                 F_x = Binary("+", F_x, MultiplierRef(piU_name, var_indices))
             
             # Create equation: F_x = 0
             stat_name = f"stat_{var_name}"
             if var_indices:
                 stat_name += f"_{'_'.join(var_indices)}"
             
             stationarity[stat_name] = EquationDef(
                 name=stat_name,
                 domain=var_indices,
                 lhs=F_x,
                 relation=Rel.EQ,
                 rhs=Const(0.0)
             )
         
         return stationarity
     ```

2. **Handle Multiplier References** (2 hours)
   - Create AST nodes for multiplier references:
     ```python
     @dataclass
     class MultiplierRef(Expr):
         name: str
         indices: tuple[str, ...]
     ```
   - Update gradient/Jacobian access to use correct indices

3. **Test Stationarity on Examples** (2 hours)
   - File: `tests/integration/kkt/test_stationarity.py`
   - Test cases:
     - Scalar NLP: verify ∂f/∂x + λ·∂g/∂x = 0 structure
     - Indexed NLP: verify index matching (stat_x_i1 uses ∂f/∂x(i1))
     - Bounds NLP: verify π^L and π^U terms
     - **NEW:** Infinite bounds: verify no π terms for ±INF bounds
     - **NEW:** Objective variable: verify no stationarity row for objvar

4. **Early Integration Smoke Test** (1.5 hours)
   - File: `tests/e2e/test_smoke.py` (from PREP_PLAN Task 5)
   - Implement first 4 smoke tests:
     - `test_minimal_scalar_nlp_pipeline()` - Parse → Normalize → Grad → Jac
     - `test_indexed_nlp_pipeline()` - With indexed variables
     - `test_bounds_handling_pipeline()` - Issue #24 regression
     - `test_kkt_assembler_smoke()` - Basic KKT assembly
   - **NEW:** Add test for infinite bounds handling
   - **NEW:** Add test for objective variable handling

**Deliverables:**
- `src/kkt/stationarity.py` - Stationarity builder (with objective skipping)
- `src/ir/ast.py` - Add `MultiplierRef` node
- `tests/integration/kkt/test_stationarity.py` - Integration tests (~12 tests, up from 10)
- `tests/e2e/test_smoke.py` - Early smoke tests (6 tests, up from 4)

**Acceptance Criteria:**
- [ ] Stationarity equations generated for all variable instances except objvar
- [ ] **NEW:** Objective variable skipped in stationarity
- [ ] **NEW:** No π terms for infinite bounds
- [ ] Multiplier references correctly indexed
- [ ] Integration tests pass (12/12)
- [ ] Early smoke tests pass (6/6)
- [ ] Manual inspection: stationarity for simple_nlp matches hand calculation
- [ ] No Sprint 1/2 test regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 5: Early Integration Smoke Test** - ✅ Completed as part of Day 2
- Smoke tests implemented and passing
- `test_kkt_assembler_smoke()` added and verified
- Infinite bounds and objective variable tests included

---

### Day 3: KKT Assembler - Complementarity

**Goal:** Build complementarity equations and complete KKT system

**Tasks:**

1. **Implement Complementarity Builder** (3.5 hours)
   - File: `src/kkt/complementarity.py`
   - Function: `build_complementarity_pairs(kkt: KKTSystem) -> dict`
   - **MODIFIED:** Include objective defining equation
   - For inequalities g(x) ≤ 0:
     ```python
     def build_complementarity_pairs(kkt: KKTSystem) -> tuple[dict, dict, dict]:
         """Build complementarity pairs for inequalities and bounds."""
         
         comp_ineq = {}
         comp_bounds_lo = {}
         comp_bounds_up = {}
         equality_eqs = {}
         
         obj_info = extract_objective_info(kkt.model_ir)
         
         # Inequalities: F_λ = -g(x) ⊥ λ ≥ 0
         for eq_name in kkt.model_ir.inequalities:
             if eq_name in kkt.model_ir.normalized_bounds:
                 continue  # Skip auto-generated bounds
             
             g_expr = kkt.model_ir.inequalities[eq_name].lhs
             F_lam = Unary("-", g_expr)  # -g(x)
             
             lam_name = create_ineq_multiplier_name(eq_name, ...)
             comp_ineq[eq_name] = ComplementarityPair(
                 equation=EquationDef(..., F_lam, Rel.GE, Const(0.0)),
                 variable=lam_name,
                 variable_indices=...
             )
         
         # Equalities: F_ν = h(x) = 0 with ν free
         # IMPORTANT: Include objective defining equation (Review Adjustment #4)
         for eq_name in kkt.model_ir.equalities:
             h_expr = kkt.model_ir.equalities[eq_name].lhs
             
             nu_name = create_eq_multiplier_name(eq_name, ...)
             equality_eqs[eq_name] = EquationDef(
                 name=f"eq_{eq_name}",
                 domain=...,
                 lhs=h_expr,
                 relation=Rel.EQ,
                 rhs=Const(0.0)
             )
             # Note: ν is a free variable (no .LO or .UP)
         
         # Bounds: Only for finite bounds (infinite bounds already filtered)
         # Lower bounds: F_π^L = x - lo ⊥ π^L ≥ 0
         for var_name in kkt.multipliers_bounds_lo:
             bound_def = kkt.multipliers_bounds_lo[var_name]
             F_piL = Binary("-", 
                           VarRef(var_name, bound_def.domain),
                           Const(bound_def.value))
             
             piL_name = create_bound_lo_multiplier_name(var_name, bound_def.domain)
             comp_bounds_lo[var_name] = ComplementarityPair(
                 equation=EquationDef(..., F_piL, Rel.GE, Const(0.0)),
                 variable=piL_name,
                 variable_indices=bound_def.domain
             )
         
         # Upper bounds: F_π^U = up - x ⊥ π^U ≥ 0
         for var_name in kkt.multipliers_bounds_up:
             bound_def = kkt.multipliers_bounds_up[var_name]
             F_piU = Binary("-",
                           Const(bound_def.value),
                           VarRef(var_name, bound_def.domain))
             
             piU_name = create_bound_up_multiplier_name(var_name, bound_def.domain)
             comp_bounds_up[var_name] = ComplementarityPair(
                 equation=EquationDef(..., F_piU, Rel.GE, Const(0.0)),
                 variable=piU_name,
                 variable_indices=bound_def.domain
             )
         
         return comp_ineq, comp_bounds_lo, comp_bounds_up, equality_eqs
     ```

2. **Main KKT Assembler** (2 hours)
   - File: `src/kkt/assemble.py`
   - Function: `assemble_kkt_system(model_ir, gradient, J_eq, J_ineq) -> KKTSystem`
   - Orchestrates all builders:
     ```python
     def assemble_kkt_system(model_ir, gradient, J_eq, J_ineq):
         # Step 1: Enhanced partition with duplicate/infinite detection
         partition = partition_constraints(model_ir)
         
         # Log warnings
         for warning in partition.duplicate_warnings:
             logger.warning(warning)
         for var, bound_type in partition.skipped_infinite:
             logger.info(f"Skipping infinite {bound_type} bound on {var}")
         
         # Step 2: Extract objective info
         obj_info = extract_objective_info(model_ir)
         
         # Step 3: Create multiplier definitions (only finite bounds)
         multipliers_eq = create_eq_multipliers(partition.equalities)
         multipliers_ineq = create_ineq_multipliers(partition.inequalities)
         multipliers_bounds_lo = create_bound_multipliers(partition.bounds_lo)
         multipliers_bounds_up = create_bound_multipliers(partition.bounds_up)
         
         # Step 4: Build KKT system
         kkt = KKTSystem(...)
         
         # Step 5: Build stationarity (skips objvar)
         kkt.stationarity = build_stationarity_equations(kkt)
         
         # Step 6: Build complementarity (includes obj defining eq)
         kkt.complementarity_ineq, kkt.complementarity_bounds_lo, \
         kkt.complementarity_bounds_up, kkt.equality_eqs = \
             build_complementarity_pairs(kkt)
         
         return kkt
     ```

3. **End-to-End KKT Test** (2.5 hours)
   - File: `tests/integration/kkt/test_kkt_full.py`
   - Test full assembly on all 5 examples:
     - simple_nlp.gms
     - bounds_nlp.gms (test infinite bounds)
     - indexed_balance.gms
     - nonlinear_mix.gms
     - scalar_nlp.gms
   - Verify:
     - Correct number of stationarity equations (num_vars - 1 for objvar)
     - Correct number of multipliers
     - Correct complementarity pairs
     - **NEW:** Objective defining equation included
     - **NEW:** No multipliers for infinite bounds
     - Hand-check one example (simple_nlp) completely

4. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Verify `test_kkt_assembler_smoke()` passes with new logic
   - Add assertions for objective variable handling

**Deliverables:**
- `src/kkt/complementarity.py` - Complementarity builder
- `src/kkt/assemble.py` - Main KKT assembler
- `tests/integration/kkt/test_kkt_full.py` - Full integration tests (~15 tests, up from 12)
- `tests/e2e/test_smoke.py` - Updated smoke tests (6 tests total)

**Acceptance Criteria:**
- [ ] KKT system assembled for all 5 examples
- [ ] Stationarity + complementarity equations count matches theory
- [ ] **NEW:** Objective defining equation included in equality_eqs
- [ ] **NEW:** Objective variable has no stationarity equation
- [ ] **NEW:** Infinite bounds produce no complementarity pairs
- [ ] Integration tests pass (15/15)
- [ ] Smoke tests pass (6/6)
- [ ] Manual verification: simple_nlp KKT matches hand calculation
- [ ] No regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 7: Add Integration Risk Sections** - Complete this evening (2 hours)
- Review Days 4-10 plan
- Add "Integration Risks" section to each remaining day
- Document Sprint 1/2 dependencies
- Add mitigation strategies (diagnostics, early tests)
- Update PLAN_REVISED.md with risk sections

---

### Day 4: GAMS Emitter - Original Symbols & Structure

**Goal:** Emit original model symbols (Sets/Aliases/Parameters) and create GAMS code generation templates

**Integration Risks:**

**Sprint 1 Dependencies:**
- Assumption: ModelIR.sets, ModelIR.aliases, ModelIR.params contain all original declarations
- Risk: Symbol information incomplete or incorrect
- Mitigation: Add diagnostic on Day 4 morning to verify all symbols have complete data

**Sprint 2 Dependencies:**  
- Assumption: GradientVector.index_mapping provides correct variable instance enumeration
- Risk: Index mapping doesn't match KKT system expectations
- Mitigation: Add assertion `len(kkt.stationarity) == gradient.num_cols - 1` (accounting for objvar)

**Within-Sprint Dependencies:**
- Assumption: Day 3 KKT system has all required fields populated
- Risk: Missing multipliers or equations
- Mitigation: Run smoke test before starting Day 4 work

**Tasks:**

1. **Design GAMS Template Structure** (1.5 hours)
   - File: `src/emit/templates.py`
   - Template functions:
     ```python
     def emit_original_sets(model_ir: ModelIR) -> str:
         """Emit original Sets block from ModelIR.sets."""
         
     def emit_original_aliases(model_ir: ModelIR) -> str:
         """Emit original Alias declarations from ModelIR.aliases."""
         
     def emit_original_parameters(model_ir: ModelIR) -> str:
         """Emit original Parameters and their data from ModelIR.params."""
         
     def emit_kkt_sets(kkt: KKTSystem) -> str:
         """Emit Sets block for multiplier indexing."""
         
     def emit_variables(kkt: KKTSystem) -> str:
         """Emit Variables and Positive Variables blocks."""
         
     def emit_equations(kkt: KKTSystem) -> str:
         """Emit Equations block declarations."""
         
     def emit_equation_definitions(kkt: KKTSystem) -> str:
         """Emit equation definitions (eq_name.. lhs =E= rhs;)"""
         
     def emit_model(kkt: KKTSystem) -> str:
         """Emit Model MCP block with complementarity pairs."""
         
     def emit_solve(kkt: KKTSystem) -> str:
         """Emit Solve statement."""
     ```

2. **Implement Original Symbols Emission** (3 hours)
   - File: `src/emit/original_symbols.py`
   - **NEW:** Emit original model symbols (Review Adjustment #1)
   - Functions:
     ```python
     def emit_original_sets(model_ir: ModelIR) -> str:
         """
         Emit Sets block from original model.
         
         Example output:
         Sets
             i /i1*i10/
             j /j1*j5/
         ;
         """
         if not model_ir.sets:
             return ""
         
         lines = ["Sets"]
         for set_name, set_def in model_ir.sets.items():
             elements = ', '.join(set_def.elements)
             lines.append(f"    {set_name} /{elements}/")
         lines.append(";")
         return '\n'.join(lines)
     
     def emit_original_aliases(model_ir: ModelIR) -> str:
         """
         Emit Alias declarations.
         
         Example output:
         Alias(i, ip);
         Alias(j, jp);
         """
         if not model_ir.aliases:
             return ""
         
         lines = []
         for alias_name, original_set in model_ir.aliases.items():
             lines.append(f"Alias({original_set}, {alias_name});")
         return '\n'.join(lines)
     
     def emit_original_parameters(model_ir: ModelIR) -> str:
         """
         Emit Parameters and their data.
         
         Example output:
         Parameters
             c(i) /i1 2.5, i2 3.0, i3 1.8/
             demand(j) /j1 100, j2 150/
         ;
         
         Scalars
             discount /0.95/
         ;
         """
         if not model_ir.params:
             return ""
         
         # Separate scalars and parameters
         scalars = {}
         parameters = {}
         
         for param_name, param_def in model_ir.params.items():
             if param_def.is_scalar:
                 scalars[param_name] = param_def
             else:
                 parameters[param_name] = param_def
         
         lines = []
         
         # Emit Parameters
         if parameters:
             lines.append("Parameters")
             for param_name, param_def in parameters.items():
                 # Format data: /key1 val1, key2 val2/
                 data_str = ', '.join(
                     f"{k} {v}" for k, v in param_def.data.items()
                 )
                 lines.append(f"    {param_name}({','.join(param_def.domain)}) /{data_str}/")
             lines.append(";")
         
         # Emit Scalars
         if scalars:
             lines.append("Scalars")
             for scalar_name, scalar_def in scalars.items():
                 lines.append(f"    {scalar_name} /{scalar_def.value}/")
             lines.append(";")
         
         return '\n'.join(lines)
     ```

3. **Implement KKT Sets Emission** (1.5 hours)
   - Extract unique index sets from:
     - Multiplier domains
     - Equation domains
   - Example output:
     ```gams
     Sets
         eq_rows /eq1, eq2/
         ineq_rows /g1, g2, g3/
     ;
     ```

4. **Implement Variables Emission** (1.5 hours)
   - Primal variables (from original model)
   - Multiplier variables:
     ```gams
     Variables
         x(i)          "Primal variable"
         obj           "Objective variable"
         nu_balance(i) "Multiplier for balance equation"
     ;
     
     Positive Variables
         lam_g1(i)     "Multiplier for inequality g1"
         piL_x(i)      "Multiplier for lower bound on x"
         piU_x(i)      "Multiplier for upper bound on x"
     ;
     ```

5. **Test Template Generation** (2.5 hours)
   - File: `tests/unit/emit/test_templates.py`
   - Test each template function separately
   - **NEW:** Test original symbols emission
   - Verify GAMS syntax correctness
   - Test with simple_nlp and bounds_nlp

**Deliverables:**
- `src/emit/templates.py` - Template functions
- `src/emit/original_symbols.py` - **NEW** Original symbols emission
- `tests/unit/emit/test_templates.py` - Unit tests (~20 tests, up from 15)
- `tests/unit/emit/test_original_symbols.py` - **NEW** Tests for original symbols (~8 tests)

**Acceptance Criteria:**
- [ ] All template functions implemented
- [ ] **NEW:** Original Sets/Aliases/Parameters emitted correctly
- [ ] Generated Sets/Variables blocks syntactically correct
- [ ] Unit tests pass (28/28)
- [ ] Output for simple_nlp inspected and verified
- [ ] Type checking passes

---

### Day 5: GAMS Emitter - Equation Emission

**Goal:** Emit equation definitions with correct syntax and index expansion

**Integration Risks:**

**Sprint 2 Dependencies:**
- Assumption: AST expressions can be converted to GAMS syntax
- Risk: Some AST nodes don't have GAMS equivalents
- Mitigation: Add comprehensive AST → GAMS tests before equation emission

**Within-Sprint Dependencies:**
- Assumption: Day 3 stationarity equations use correct operator precedence
- Risk: Generated GAMS has wrong precedence (e.g., missing parentheses)
- Mitigation: Add expression rendering tests with nested operators

**Tasks:**

1. **Implement AST → GAMS Converter** (3 hours)
   - File: `src/emit/expr_to_gams.py`
   - Function: `expr_to_gams(expr: Expr) -> str`
   - Handle all AST node types including **NEW** `MultiplierRef`:
     ```python
     def expr_to_gams(expr: Expr) -> str:
         match expr:
             case Const(value):
                 return str(value)
             case VarRef(name, indices):
                 if indices:
                     return f"{name}({','.join(indices)})"
                 return name
             case ParamRef(name, indices):
                 if indices:
                     return f"{name}({','.join(indices)})"
                 return name
             case MultiplierRef(name, indices):  # NEW
                 if indices:
                     return f"{name}({','.join(indices)})"
                 return name
             case Binary(op, left, right):
                 l = expr_to_gams(left)
                 r = expr_to_gams(right)
                 # Handle precedence with parentheses
                 return f"({l} {op} {r})"
             case Unary(op, child):
                 c = expr_to_gams(child)
                 return f"{op}{c}"
             case Call(func, args):
                 args_str = ', '.join(expr_to_gams(a) for a in args)
                 return f"{func}({args_str})"
             case Sum(index_sets, body):
                 # GAMS: sum(i, body)
                 body_str = expr_to_gams(body)
                 return f"sum({','.join(index_sets)}, {body_str})"
     ```

2. **Implement Equation Definition Emission** (2 hours)
   - File: `src/emit/equations.py`
   - For each equation in KKT system:
     ```python
     def emit_equation_def(eq_name: str, eq_def: EquationDef) -> str:
         # eq_name(i,j).. lhs =E= rhs;
         
         # Convert LHS and RHS to GAMS
         lhs_gams = expr_to_gams(eq_def.lhs)
         rhs_gams = expr_to_gams(eq_def.rhs)
         
         # Determine relation
         rel_map = {Rel.EQ: '=E=', Rel.LE: '=L=', Rel.GE: '=G='}
         rel_gams = rel_map[eq_def.relation]
         
         # Build equation string
         if eq_def.domain:
             indices_str = ','.join(eq_def.domain)
             return f"{eq_name}({indices_str}).. {lhs_gams} {rel_gams} {rhs_gams};"
         else:
             return f"{eq_name}.. {lhs_gams} {rel_gams} {rhs_gams};"
     ```

3. **Test Expression Conversion** (2 hours)
   - File: `tests/unit/emit/test_expr_to_gams.py`
   - Test all AST node types
   - **NEW:** Test MultiplierRef conversion
   - Test operator precedence
   - Test nested expressions
   - Verify power operator (Issue #25 check)

**Deliverables:**
- `src/emit/expr_to_gams.py` - AST → GAMS converter (with MultiplierRef)
- `src/emit/equations.py` - Equation emission
- `tests/unit/emit/test_expr_to_gams.py` - Expression tests (~22 tests, up from 20)
- `tests/unit/emit/test_equations.py` - Equation tests (~10 tests)

**Acceptance Criteria:**
- [ ] All AST nodes convert to valid GAMS syntax
- [ ] **NEW:** MultiplierRef converts correctly
- [ ] Operator precedence correct (tested with complex expressions)
- [ ] Equation definitions emit correctly
- [ ] Unit tests pass (32/32)
- [ ] Power operator converts correctly (x^2 → x ** 2 or power(x, 2))

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 6: Test Pyramid Visualization** - Complete this evening (3 hours)
- Implement `scripts/test_pyramid.py`
- Generate `docs/testing/TEST_PYRAMID.md`
- Add to CI workflow
- Update README with link to pyramid

---

### Day 6: GAMS Emitter - Model & Solve

**Goal:** Complete GAMS emitter with Model MCP and Solve statements

**Integration Risks:**

**Within-Sprint Dependencies:**
- Assumption: Day 5 equation emission produces valid GAMS equations
- Risk: Equations have syntax errors that don't appear until Model declaration
- Mitigation: Run GAMS syntax check on Day 6 morning before proceeding

**Tasks:**

1. **Implement Model MCP Emission** (3.5 hours)
   - File: `src/emit/model.py`
   - Function: `emit_model_mcp(kkt: KKTSystem) -> str`
   - **MODIFIED:** Handle objective defining equation pairing
   - Model MCP syntax:
     ```gams
     Model mcp_model /
         * Stationarity conditions (primal variables, except objvar)
         stat_x.x
         stat_y.y
         
         * Inequality complementarities
         comp_g1.lam_g1
         comp_g2.lam_g2
         
         * Equality constraints (free multipliers)
         eq_h1.nu_h1
         eq_objdef.obj  * Objective defining equation paired with objvar
         
         * Bound complementarities (finite bounds only)
         bound_lo_x.piL_x
         bound_up_x.piU_x
     /;
     ```
   - Pairing rules:
     - Stationarity equations paired with primal variables (except objvar)
     - Complementarity equations paired with multipliers
     - Equality equations paired with free multipliers
     - **NEW:** Objective defining equation paired with objvar (not a multiplier)

2. **Implement Solve Statement** (1 hour)
   - Function: `emit_solve(kkt: KKTSystem) -> str`
   - Output:
     ```gams
     Solve mcp_model using MCP;
     ```
   - Optional: Add display statements for debugging

3. **Main Emitter Orchestration** (2.5 hours)
   - File: `src/emit/emit_gams.py`
   - Function: `emit_gams_mcp(kkt: KKTSystem) -> str`
   - **MODIFIED:** Include original symbols first (Review Adjustment #1)
   - Combine all pieces:
     ```python
     def emit_gams_mcp(kkt: KKTSystem, options: dict = None) -> str:
         sections = []
         
         # Header comment
         sections.append("* Generated by nlp2mcp")
         sections.append("* KKT conditions for MCP")
         sections.append("")
         
         # Original model symbols (NEW - Review Adjustment #1)
         sections.append("* Original model declarations")
         sections.append(emit_original_sets(kkt.model_ir))
         sections.append("")
         sections.append(emit_original_aliases(kkt.model_ir))
         sections.append("")
         sections.append(emit_original_parameters(kkt.model_ir))
         sections.append("")
         
         # KKT-specific Sets
         sections.append("* KKT system sets")
         sections.append(emit_kkt_sets(kkt))
         sections.append("")
         
         # Variables
         sections.append("* Variables (primal + multipliers)")
         sections.append(emit_variables(kkt))
         sections.append("")
         
         # Equations declaration
         sections.append("* Equations")
         sections.append(emit_equations(kkt))
         sections.append("")
         
         # Equation definitions
         sections.append("* Equation definitions")
         sections.append(emit_equation_definitions(kkt))
         sections.append("")
         
         # Model
         sections.append("* Model MCP")
         sections.append(emit_model_mcp(kkt))
         sections.append("")
         
         # Solve
         sections.append("* Solve")
         sections.append(emit_solve(kkt))
         
         return '\n'.join(sections)
     ```

4. **Integration Test** (1.5 hours)
   - File: `tests/integration/emit/test_emit_full.py`
   - Test full emission on simple_nlp
   - **NEW:** Verify original symbols appear in output
   - **NEW:** Verify objective equation pairing
   - Verify generated GAMS is syntactically valid
   - Manually inspect output

5. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Implement `test_gams_emitter_smoke()` (remove @skip)
   - Verify full pipeline doesn't crash
   - **NEW:** Verify output contains original symbols

**Deliverables:**
- `src/emit/model.py` - Model MCP emission (with objective handling)
- `src/emit/emit_gams.py` - Main emitter (with original symbols)
- `tests/integration/emit/test_emit_full.py` - Integration tests (~10 tests, up from 8)
- `tests/e2e/test_smoke.py` - Updated smoke tests (7 tests total, up from 6)

**Acceptance Criteria:**
- [ ] Model MCP emitted with correct complementarity pairs
- [ ] **NEW:** Objective defining equation paired with objvar
- [ ] **NEW:** Original Sets/Aliases/Parameters appear in output
- [ ] Full GAMS code generated for simple_nlp
- [ ] Generated code is syntactically valid (manual inspection)
- [ ] Integration tests pass (10/10)
- [ ] Smoke tests pass (7/7)
- [ ] No regressions

---

### Day 7: Mid-Sprint Checkpoint & CLI

**Goal:** Review progress, address integration issues, implement CLI

**Mid-Sprint Checkpoint Activities:**

1. **Status Review** (1 hour)
   - Run all tests (unit, integration, e2e, smoke)
   - Review completed vs. planned work
   - Identify blockers and risks
   - Update plan for Days 8-10 if needed

2. **Integration Health Check** (1 hour)
   - Run API contract tests (should still pass)
   - Run Sprint 1/2 tests (should still pass)
   - Test all 5 example models through full pipeline
   - **NEW:** Verify generated GAMS includes original symbols
   - **NEW:** Verify no infinite bound multipliers created
   - **NEW:** Verify objective variable handling correct
   - Document any issues found

**Tasks:**

3. **Implement CLI** (3 hours)
   - File: `src/cli.py`
   - Command: `nlp2mcp input.gms -o output.gms`
   - Options:
     ```python
     @click.command()
     @click.argument('input_file', type=click.Path(exists=True))
     @click.option('-o', '--output', type=click.Path(), help='Output file')
     @click.option('--verbose', '-v', count=True, help='Verbosity level')
     @click.option('--validate', is_flag=True, help='Validate with GAMS if available')
     @click.option('--comments', is_flag=True, default=True, help='Add explanatory comments')
     @click.option('--warn-duplicates', is_flag=True, default=True, 
                   help='Warn about potential duplicate bound constraints')
     def main(input_file, output, verbose, validate, comments, warn_duplicates):
         # Load and parse
         model = parse_model_file(input_file)
         normalize_model(model)
         
         # Compute derivatives
         gradient = compute_objective_gradient(model)
         J_eq, J_ineq = compute_constraint_jacobian(model)
         
         # Assemble KKT
         kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
         
         # Log warnings from assembly
         if warn_duplicates:
             for warning in kkt.duplicate_bounds_warnings:
                 click.echo(f"Warning: {warning}", err=True)
         
         if verbose:
             click.echo(f"Skipped {len(kkt.skipped_infinite_bounds)} infinite bounds")
             click.echo(f"Created {len(kkt.stationarity)} stationarity equations")
             click.echo(f"Created {len(kkt.complementarity_ineq)} inequality multipliers")
         
         # Emit GAMS
         gams_code = emit_gams_mcp(kkt, options={'comments': comments})
         
         # Write output
         if output:
             Path(output).write_text(gams_code)
             click.echo(f"Generated MCP: {output}")
         else:
             print(gams_code)
         
         # Optional validation
         if validate:
             validate_gams_syntax(output)
     ```

4. **Error Handling** (2 hours)
   - Add try/except blocks for each pipeline stage
   - Provide clear error messages
   - Test error paths (malformed GAMS, unsupported features)

5. **CLI Testing** (1 hour)
   - File: `tests/integration/test_cli.py`
   - Test CLI on all 5 examples
   - Test error cases
   - Test options (--verbose, --comments, --warn-duplicates)

**Deliverables:**
- `src/cli.py` - Command-line interface (with new warnings)
- `tests/integration/test_cli.py` - CLI tests (~12 tests, up from 10)
- Mid-sprint checkpoint report (in PR comment or doc)

**Acceptance Criteria:**
- [ ] Mid-sprint checkpoint completed
- [ ] All tests passing (expect ~175 total, up from ~150)
- [ ] CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`
- [ ] **NEW:** CLI shows warnings for duplicate bounds
- [ ] **NEW:** CLI reports skipped infinite bounds in verbose mode
- [ ] Generated output file is valid GAMS
- [ ] Error messages are clear and helpful
- [ ] No critical blockers identified

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 8: Mid-Sprint Checkpoint Process** - ✅ Completed as part of Day 7
- Checkpoint conducted
- Integration health verified
- Plan updated if needed

---

### Day 8: Golden Test Suite

**Goal:** Create end-to-end golden tests with reference outputs

**Integration Risks:**

**All Sprint Dependencies:**
- Assumption: Full pipeline (Parse → KKT → Emit) produces deterministic output
- Risk: Non-deterministic ordering in emitted code (dict iteration order)
- Mitigation: Add sorted() calls in emission code for deterministic output

**Tasks:**

1. **Generate Golden Reference Files** (2.5 hours)
   - For each of 5 example models, manually:
     - Run pipeline: `nlp2mcp examples/simple_nlp.gms -o golden/simple_nlp_mcp.gms`
     - Manually review and verify correctness
     - Hand-check KKT equations match theory
     - **NEW:** Verify original symbols present
     - **NEW:** Verify no infinite bound multipliers
     - **NEW:** Verify objective variable handling
     - Mark as golden reference
   - Files:
     - `tests/golden/simple_nlp_mcp.gms`
     - `tests/golden/bounds_nlp_mcp.gms` (test infinite bounds)
     - `tests/golden/indexed_balance_mcp.gms`
     - `tests/golden/nonlinear_mix_mcp.gms`
     - `tests/golden/scalar_nlp_mcp.gms`

2. **Implement Golden Test Framework** (2 hours)
   - File: `tests/e2e/test_golden.py`
   - Function: `test_golden_match(example_name: str)`
   - For each example:
     ```python
     @pytest.mark.e2e
     def test_simple_nlp_golden():
         # Run pipeline
         output = run_pipeline('examples/simple_nlp.gms')
         
         # Load golden reference
         golden = Path('tests/golden/simple_nlp_mcp.gms').read_text()
         
         # Compare (after normalizing whitespace)
         assert normalize(output) == normalize(golden), \
             "Generated output doesn't match golden reference"
     ```

3. **Add Golden Test for All 5 Examples** (2 hours)
   - One test per example
   - Detailed diff output on failure
   - Document any known differences (e.g., comment formatting)

4. **Determinism Check** (1.5 hours)
   - Run each example 5 times
   - Verify output is identical each time
   - Fix any non-determinism (sort dict keys, etc.)
   - **NEW:** Verify infinite bounds consistently skipped
   - **NEW:** Verify duplicate warnings deterministic

**Deliverables:**
- `tests/golden/` - Golden reference files (5 files)
- `tests/e2e/test_golden.py` - Golden tests (5 tests)

**Acceptance Criteria:**
- [ ] All 5 golden reference files generated and verified
- [ ] **NEW:** Golden files include original model symbols
- [ ] **NEW:** Golden files show correct infinite bound handling
- [ ] **NEW:** Golden files show correct objective variable treatment
- [ ] Golden tests pass (5/5)
- [ ] Output is deterministic (tested with 5 runs each)
- [ ] Diff output is clear when tests fail
- [ ] Golden files committed to git

---

### Day 9: GAMS Validation (Optional) & Documentation

**Goal:** Add optional GAMS validation and complete documentation

**Tasks:**

1. **Optional GAMS Syntax Validation** (2 hours)
   - File: `src/validation/gams_check.py`
   - If GAMS available:
     ```python
     def validate_gams_syntax(gams_file: str) -> bool:
         """Run GAMS in compile-only mode to check syntax."""
         result = subprocess.run(
             ['gams', gams_file, 'action=c'],
             capture_output=True
         )
         return result.returncode == 0
     ```
   - Skip if GAMS not available (not required for Sprint 3)

2. **Document KKT Assembly** (2.5 hours)
   - File: `docs/kkt/KKT_ASSEMBLY.md`
   - Mathematical notation for KKT conditions
   - Explain stationarity construction
   - Explain complementarity conditions
   - Document multiplier naming conventions
   - **NEW:** Document infinite bounds handling (Review Adjustment #3)
   - **NEW:** Document objective variable handling (Review Adjustment #4)
   - **NEW:** Document duplicate bounds detection (Review Adjustment #2)

3. **Document GAMS Emission** (2.5 hours)
   - File: `docs/emit/GAMS_EMISSION.md`
   - **NEW:** Document original symbols emission (Review Adjustment #1)
   - Template examples
   - AST → GAMS conversion rules
   - Model MCP pairing rules
   - Sign conventions
   - **NEW:** Show example with objective defining equation pairing

4. **Update README** (1 hour)
   - Add usage examples
   - Document CLI options (including new --warn-duplicates)
   - Show before/after example
   - Link to documentation
   - **NEW:** Mention bounds handling features

**Deliverables:**
- `src/validation/gams_check.py` - Optional GAMS validation
- `docs/kkt/KKT_ASSEMBLY.md` - KKT documentation (with new sections)
- `docs/emit/GAMS_EMISSION.md` - Emission documentation (with new sections)
- Updated `README.md`

**Acceptance Criteria:**
- [ ] GAMS validation implemented (optional feature)
- [ ] KKT assembly fully documented with math notation
- [ ] **NEW:** Infinite bounds handling documented
- [ ] **NEW:** Objective variable handling documented
- [ ] **NEW:** Duplicate bounds detection documented
- [ ] GAMS emission fully documented with examples
- [ ] **NEW:** Original symbols emission documented
- [ ] README updated with Sprint 3 features
- [ ] All documentation reviewed for accuracy

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 9: Add Complexity Estimation** - Complete this evening (2 hours)
- Review Day 10 tasks
- Estimate complexity for each task
- Identify high-risk/complex areas
- Add contingency buffer to plan

**PREP_PLAN Task 10: Known Unknowns List** - Complete with Task 9 (1 hour)
- Document assumptions that might be wrong
- List features we're not sure how to implement
- Identify areas needing research
- Create mitigation strategies

---

### Day 10: Polish, Testing, & Sprint Wrap-Up

**Goal:** Final testing, bug fixes, and Sprint 3 completion

**Tasks:**

1. **Comprehensive Testing** (2.5 hours)
   - Run full test suite
   - Run all 5 examples through CLI
   - Test edge cases:
     - Models with only equalities
     - Models with only inequalities
     - Models with no bounds
     - Models with all infinite bounds
     - Scalar models (no indexing)
     - **NEW:** Models with potential duplicate bounds
     - **NEW:** Models where objective variable has different name
   - Fix any bugs found

2. **Code Quality Pass** (2 hours)
   - Run pre-commit checks:
     ```bash
     mypy src/
     ruff check . --fix
     ruff format .
     ```
   - Add missing docstrings
   - Review code comments
   - Clean up debug print statements
   - **NEW:** Document all warnings generated by system

3. **Integration Test Coverage** (2 hours)
   - Review test coverage:
     ```bash
     pytest --cov=src tests/
     ```
   - Add tests for uncovered code paths
   - **NEW:** Add tests for all new features (bounds handling, objective, etc.)
   - Target: >90% coverage for new Sprint 3 code

4. **Final Validation** (1 hour)
   - Verify all success metrics achieved
   - Run smoke tests one final time
   - Verify API contract tests still pass
   - Verify no Sprint 1/2 regressions
   - **NEW:** Verify all 4 review adjustments implemented

5. **Sprint Wrap-Up** (1.5 hours)
   - Create Sprint 3 summary document
   - **NEW:** Document review feedback and how it was addressed
   - Document lessons learned
   - Identify items for Sprint 4
   - Update CHANGELOG.md
   - Celebrate! 🎉

**Deliverables:**
- All tests passing
- Code coverage >90% for Sprint 3 code
- Sprint 3 summary document
- Clean, polished codebase
- Updated CHANGELOG.md

**Acceptance Criteria:**
- [ ] All 440+ tests pass (up from 403+)
- [ ] All 5 examples convert successfully
- [ ] **NEW:** Generated MCP files include original symbols
- [ ] **NEW:** Infinite bounds handled correctly (no infinite multipliers)
- [ ] **NEW:** Objective variable handled correctly (no stationarity, defines objvar)
- [ ] **NEW:** Duplicate bounds detection works
- [ ] Generated MCP files compile in GAMS (if GAMS available)
- [ ] Golden tests pass (5/5)
- [ ] CLI works correctly with all options
- [ ] Code quality checks pass
- [ ] Documentation complete
- [ ] Sprint 3 success metrics achieved
- [ ] All 4 review adjustments verified implemented

---

## Sprint 3 Success Criteria Summary

### Functional Requirements ✅

- [ ] **KKT Assembler**: Converts derivatives to KKT system
  - Stationarity equations for all variables (except objvar)
  - Complementarity conditions for inequalities
  - Multiplier variables created correctly
  - **NEW:** Infinite bounds filtered (no π for ±INF)
  - **NEW:** Duplicate user bounds detected and warned
  - **NEW:** Objective variable handled specially

- [ ] **GAMS Emitter**: Generates valid GAMS MCP code
  - **NEW:** Original Sets, Aliases, Parameters re-emitted
  - Sets, Variables, Equations blocks
  - Equation definitions with correct syntax
  - Model MCP with complementarity pairs
  - **NEW:** Objective defining equation paired with objvar
  - Solve statement

- [ ] **CLI**: `nlp2mcp` command works
  - Converts all 5 example models
  - Options (--output, --verbose, --validate, --warn-duplicates) work
  - **NEW:** Warnings for duplicate bounds
  - **NEW:** Reports skipped infinite bounds
  - Error messages are clear

- [ ] **Golden Tests**: Reference outputs validated
  - 5 golden reference files
  - All golden tests pass
  - Deterministic output

### Quality Requirements ✅

- [ ] **Test Coverage**:
  - Unit tests: ~180 total (60 new, up from 50)
  - Integration tests: ~60 total (18 new, up from 15)
  - E2E tests: ~20 total (7 new, up from 5)
  - Total: 260+ tests passing (up from 220+)

- [ ] **Code Quality**:
  - Type checking passes (`mypy src/`)
  - Linting passes (`ruff check`)
  - Formatting passes (`ruff format`)
  - Coverage >90% for Sprint 3 code

- [ ] **Documentation**:
  - KKT assembly documented (with new sections)
  - GAMS emission documented (with new sections)
  - **NEW:** Bounds handling documented
  - **NEW:** Objective variable handling documented
  - README updated
  - All public functions have docstrings

### Integration Health ✅

- [ ] **No Regressions**:
  - All Sprint 1/2 tests pass
  - API contract tests pass
  - No issues introduced in previous sprints

- [ ] **Early Detection**:
  - Smoke tests caught issues within 1 day
  - Integration problems identified by Day 2-3
  - Mid-sprint checkpoint showed green status

### Review Adjustments Verified ✅

- [ ] **Adjustment #1**: Original data/alias emission implemented
  - Sets, Aliases, Parameters re-emitted from ModelIR
  - Generated MCP compiles with all symbol references

- [ ] **Adjustment #2**: Bounds vs. explicit constraints addressed
  - Duplicate detection in partition_constraints()
  - Warnings generated for potential duplicates

- [ ] **Adjustment #3**: Infinite bounds handling implemented
  - ±INF bounds filtered during partitioning
  - No π^L/π^U created for infinite bounds
  - Complementarity rows omitted correctly

- [ ] **Adjustment #4**: Objective variable flow defined
  - Objective variable extracted correctly
  - No stationarity equation for objvar
  - Defining equation paired with objvar in Model MCP

---

## Risk Management

### High-Priority Risks

**Risk 1: GAMS Syntax Correctness**
- **Impact:** Generated code doesn't compile in GAMS
- **Likelihood:** Medium → Low (reduced with original symbols emission)
- **Mitigation:**
  - Re-emit original symbols (Review Adjustment #1)
  - Start GAMS validation early (Day 4)
  - Manual review of first emitted example
  - Golden tests with known-good outputs
- **Contingency:** Use text-based validation only if GAMS unavailable

**Risk 2: Multiplier Naming Collisions**
- **Impact:** Generated variables conflict with original model
- **Likelihood:** Low
- **Mitigation:**
  - Use distinctive prefixes (nu_, lam_, piL_, piU_)
  - Collision detection in naming.py
  - Test with models that have similar names
- **Contingency:** Add disambiguation suffixes (_m1, _m2, etc.)

**Risk 3: Sign Convention Errors**
- **Impact:** KKT conditions mathematically incorrect
- **Likelihood:** Medium
- **Mitigation:**
  - Careful hand-checking of simple_nlp
  - Document sign conventions clearly
  - Complementarity tests verify F·λ structure
- **Contingency:** Add --debug mode to show KKT equations before GAMS

**Risk 4: Index Expansion Complexity**
- **Impact:** Indexed equations don't emit correctly
- **Likelihood:** Medium
- **Mitigation:**
  - Test indexed_balance.gms early (Day 5)
  - Separate unit tests for index expansion
  - Manual inspection of emitted code
- **Contingency:** Start with scalar-only support, add indexing later

### Medium-Priority Risks

**Risk 5: AST → GAMS Conversion Edge Cases**
- **Impact:** Some expressions don't convert correctly
- **Likelihood:** Low
- **Mitigation:**
  - Comprehensive unit tests for all AST nodes
  - Test complex nested expressions
  - Power operator special handling (Issue #25)
  - MultiplierRef node support
- **Contingency:** Reject unsupported expressions with clear error

**Risk 6: Sprint Scope Creep**
- **Impact:** Don't finish core features by Day 10
- **Likelihood:** Low
- **Mitigation:**
  - Strict focus on 5 example models only
  - Mid-sprint checkpoint on Day 7
  - Optional features clearly marked
  - Review adjustments add ~1 day of work but are essential
- **Contingency:** Move optional features to Sprint 4

### New Risks from Review Adjustments

**Risk 7: Incomplete Original Symbol Information**
- **Impact:** Can't re-emit Sets/Aliases/Parameters correctly
- **Likelihood:** Low
- **Mitigation:**
  - Sprint 1 ModelIR should have captured everything
  - Add diagnostic on Day 4 to verify completeness
  - Test with all 5 examples
- **Contingency:** Fall back to $include of original file

**Risk 8: Objective Variable Detection Fails**
- **Impact:** Can't identify which equation defines objective
- **Likelihood:** Low
- **Mitigation:**
  - Test with all 5 examples (different naming conventions)
  - Add heuristics (look for "def", "obj", etc. in equation name)
  - Document expected structure in docs
- **Contingency:** Require user to specify objective equation name via CLI option

---

## Notes

### Development Workflow

**Daily Routine:**
1. Morning: Review previous day's work, run all tests
2. Check integration risks for today
3. Work on planned tasks
4. Run pre-commit checks before each commit:
   ```bash
   mypy src/
   ruff check . --fix
   ruff format .
   ```
5. Evening: Update progress, prepare for next day

**Pre-Commit Checklist:**
- [ ] All new tests pass
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Code formatted
- [ ] Docstrings added
- [ ] No debug print statements
- [ ] Commit message descriptive

### Testing Strategy

**Test Organization:**
- `tests/unit/kkt/` - KKT assembly unit tests
- `tests/unit/emit/` - GAMS emission unit tests
- `tests/integration/kkt/` - KKT integration tests
- `tests/integration/emit/` - Emission integration tests
- `tests/e2e/test_golden.py` - Golden reference tests
- `tests/e2e/test_smoke.py` - Smoke tests

**Test Markers:**
- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.skipif(not GAMS_AVAILABLE)` - Optional GAMS tests

### Example Models (v1 Set)

1. **simple_nlp.gms** - Basic indexed NLP with objective and constraints
2. **bounds_nlp.gms** - Variable bounds handling (Issue #24 regression test, test infinite bounds)
3. **indexed_balance.gms** - Balance equations with indexing
4. **nonlinear_mix.gms** - Mixed nonlinear functions, power operator
5. **scalar_nlp.gms** - Simple scalar optimization (no indexing)

### Changes from PLAN_ORIGINAL.md

**New Features (from Review Adjustments):**
1. Original model symbols re-emission (Sets, Aliases, Parameters)
2. Infinite bounds filtering (skip ±INF bounds)
3. Duplicate bounds detection and warnings
4. Objective variable special handling

**Impact on Plan:**
- Day 1: +1 hour (objective handling, enhanced partition logic)
- Day 2: +0.5 hours (skip objvar in stationarity)
- Day 3: +0.5 hours (include objective equation)
- Day 4: +1.5 hours (original symbols emission)
- Day 5: No change
- Day 6: +1 hour (objective equation pairing)
- Day 7: +0.5 hours (new CLI options)
- Day 8: +0.5 hours (verify new features in golden tests)
- Day 9: +1 hour (document new features)
- Day 10: +0.5 hours (test new features, verify adjustments)
- **Total:** ~6 hours added across sprint (manageable within buffer)

**Test Count Changes:**
- Unit tests: 180 (was 150, +30)
- Integration tests: 60 (was 50, +10)
- E2E tests: 20 (was 20, +0 but more assertions)
- Total: 260 (was 220, +40)

---

## Appendix: PREP_PLAN Tasks Integration

The following tasks from `docs/planning/SPRINT_3/PREP_PLAN.md` have been integrated:

- **Task 5** (Early Integration Smoke Test): Day 2
- **Task 6** (Test Pyramid Visualization): Day 5 evening
- **Task 7** (Integration Risk Sections): Day 3 evening
- **Task 8** (Mid-Sprint Checkpoint): Day 7
- **Task 9** (Complexity Estimation): Day 9 evening
- **Task 10** (Known Unknowns List): Day 9 evening

These tasks support the main Sprint 3 work and help prevent the integration issues encountered in Sprint 2.

---

## Appendix: Review Feedback Implementation

### Review Gap #1: Missing data/alias emission
**Status:** ✅ Addressed
**Implementation:**
- Added `emit_original_sets()`, `emit_original_aliases()`, `emit_original_parameters()` to Day 4
- Modified main emitter to include original symbols before KKT blocks
- Added unit tests for original symbol emission
- Updated documentation

### Review Gap #2: Bounds vs. explicit constraints not addressed
**Status:** ✅ Addressed
**Implementation:**
- Enhanced `partition_constraints()` to detect user-authored bounds
- Added `duplicate_bounds_warnings` to KKTSystem
- Added `--warn-duplicates` CLI option
- Added tests for duplicate detection

### Review Gap #3: Infinite bounds handling absent
**Status:** ✅ Addressed
**Implementation:**
- Modified partition logic to filter ±INF bounds
- Added `skipped_infinite_bounds` to KKTSystem
- Modified stationarity builder to skip π terms for infinite bounds
- Modified complementarity builder to skip infinite bound pairs
- Added tests for infinite bounds
- Documented in KKT_ASSEMBLY.md

### Review Gap #4: Objective variable/equation flow undefined
**Status:** ✅ Addressed
**Implementation:**
- Created `src/kkt/objective.py` with `extract_objective_info()`
- Modified stationarity builder to skip objective variable
- Modified complementarity builder to include objective defining equation
- Modified Model MCP emission to pair objective equation with objvar
- Added tests for objective variable handling
- Documented in KKT_ASSEMBLY.md and GAMS_EMISSION.md
