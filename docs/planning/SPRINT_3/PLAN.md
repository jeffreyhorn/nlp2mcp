# Sprint 3: KKT Synthesis + GAMS MCP Code Generation

**Duration:** 2 weeks (10 working days)  
**Start Date:** TBD  
**Goal:** Transform NLP models to runnable GAMS MCP files via KKT conditions

**Revision History:**
- PLAN_ORIGINAL.md: Initial comprehensive plan
- PLAN_REVISED.md: Addressed 4 gaps from PLAN_REVIEW.md (data emission, duplicate bounds, infinite bounds, objective variable)
- PLAN.md (this): Final plan addressing findings from PLAN_REVIEW_FINAL.md

**Final Review Adjustments:**
1. Duplicate bounds now excluded from inequality list (not just warned)
2. Indexed bounds support via lo_map/up_map/fx_map iteration
3. Original symbol emission aligned with actual IR dataclasses
4. Variable kind preservation (Positive/Binary/Integer/etc.)

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
        - Original Sets, Aliases, Parameters (re-emitted from IR)
        - Primal variables with correct kinds (Positive/Binary/etc.)
        - Multiplier variables (λ, ν, π^L, π^U)
        - Stationarity equations
        - Complementarity conditions
        - Model MCP declaration
```

### Key Components

1. **`src/kkt/assemble.py`** - KKT system assembler
   - Partition constraints (equalities h, inequalities g) **with duplicate exclusion**
   - Filter infinite bounds **for both scalar and indexed variables** (skip π^L/π^U for ±INF)
   - Create multiplier variables for each constraint row
   - Handle objective variable specially
   - Build stationarity: ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0
   - Build complementarity: F_λ ⊥ λ, F_ν = h(x), F_π^L ⊥ π^L, F_π^U ⊥ π^U

2. **`src/emit/emit_gams.py`** - GAMS code generator  
   - Emit original Sets, Aliases, Parameters **using actual IR fields** (SetDef.members, ParameterDef.values, etc.)
   - Emit Sets for multiplier indexing
   - Emit Variables blocks **preserving VariableDef.kind** (Positive, Binary, Integer, etc.)
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
- ✅ **NEW**: Duplicate bounds excluded from inequalities (no duplicate complementarity)
- ✅ **NEW**: Indexed bounds handled correctly (lo_map/up_map/fx_map)
- ✅ Infinite bounds are skipped correctly (both scalar and indexed)
- ✅ Objective variable handled correctly
- ✅ **NEW**: Variable kinds preserved (Positive/Binary/Integer/etc.)
- ✅ Golden tests pass (generated output matches expected)
- ✅ CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`

**Code Quality:**
- ✅ All unit tests pass (expect ~70 new tests, up from 60)
- ✅ All integration tests pass (expect ~22 new tests, up from 18)
- ✅ All e2e/golden tests pass (5 tests)
- ✅ Type checking passes (`mypy src/`)
- ✅ Linting passes (`ruff check`)
- ✅ Code formatted (`ruff format`)

**Documentation:**
- ✅ KKT assembly documented with mathematical notation
- ✅ Bounds handling strategy documented (scalar + indexed)
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

**Goal:** Define KKT system data structures and partition constraints with duplicate exclusion

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
         
         # Multipliers (filtered for infinite bounds, including indexed)
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
         skipped_infinite_bounds: list[tuple[str, tuple, str]]  # (var_name, indices, 'lo'/'up')
         duplicate_bounds_excluded: list[str]  # Inequality names excluded (not just warned)
     
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

2. **Implement Enhanced Constraint Partitioning** (3.5 hours)
   - File: `src/kkt/partition.py`
   - Function: `partition_constraints(model_ir: ModelIR) -> PartitionResult`
   - **CRITICAL FIX (Finding #1)**: Exclude duplicate bounds from inequality list
     ```python
     @dataclass
     class PartitionResult:
         equalities: list[str]
         inequalities: list[str]  # EXCLUDES duplicate bounds
         bounds_lo: dict[tuple[str, tuple], BoundDef]  # (var_name, indices) → BoundDef
         bounds_up: dict[tuple[str, tuple], BoundDef]
         bounds_fx: dict[tuple[str, tuple], BoundDef]
         skipped_infinite: list[tuple[str, tuple, str]]  # (var, indices, 'lo'/'up'/'fx')
         duplicate_excluded: list[str]  # Inequality names excluded
     
     def partition_constraints(model_ir: ModelIR) -> PartitionResult:
         # Equalities: equations with Rel.EQ
         equalities = [name for name in model_ir.equalities]
         
         # Inequalities: equations with Rel.LE (normalized to ≤ 0)
         # BUT: EXCLUDE if they duplicate normalized_bounds (Finding #1 fix)
         inequalities = []
         duplicate_excluded = []
         
         for name in model_ir.inequalities:
             if name in model_ir.normalized_bounds:
                 continue  # Skip auto-generated bound equations
             
             # Check if this inequality duplicates a bound
             if _is_user_authored_bound(model_ir.inequalities[name]):
                 if _duplicates_variable_bound(model_ir, name):
                     duplicate_excluded.append(name)
                     # CRITICAL: Do NOT append to inequalities list
                     continue
             
             inequalities.append(name)
         
         # Bounds: iterate over ALL bound maps (Finding #2 fix)
         bounds_lo = {}
         bounds_up = {}
         bounds_fx = {}
         skipped_infinite = []
         
         for var_name, var_def in model_ir.variables.items():
             # Scalar bounds (if any)
             if var_def.lo is not None:
                 if var_def.lo == float('-inf'):
                     skipped_infinite.append((var_name, (), 'lo'))
                 else:
                     bounds_lo[(var_name, ())] = BoundDef('lo', var_def.lo, var_def.domain)
             
             if var_def.up is not None:
                 if var_def.up == float('inf'):
                     skipped_infinite.append((var_name, (), 'up'))
                 else:
                     bounds_up[(var_name, ())] = BoundDef('up', var_def.up, var_def.domain)
             
             if var_def.fx is not None:
                 bounds_fx[(var_name, ())] = BoundDef('fx', var_def.fx, var_def.domain)
             
             # Indexed bounds (Finding #2 fix)
             for indices, lo_val in var_def.lo_map.items():
                 if lo_val == float('-inf'):
                     skipped_infinite.append((var_name, indices, 'lo'))
                 else:
                     bounds_lo[(var_name, indices)] = BoundDef('lo', lo_val, var_def.domain)
             
             for indices, up_val in var_def.up_map.items():
                 if up_val == float('inf'):
                     skipped_infinite.append((var_name, indices, 'up'))
                 else:
                     bounds_up[(var_name, indices)] = BoundDef('up', up_val, var_def.domain)
             
             for indices, fx_val in var_def.fx_map.items():
                 bounds_fx[(var_name, indices)] = BoundDef('fx', fx_val, var_def.domain)
         
         return PartitionResult(
             equalities, inequalities, 
             bounds_lo, bounds_up, bounds_fx,
             skipped_infinite, duplicate_excluded
         )
     ```

3. **Implement Objective Variable Detection** (1.5 hours)
   - File: `src/kkt/objective.py`
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

5. **Write Unit Tests** (3 hours)
   - File: `tests/unit/kkt/test_partition.py`
   - Test `partition_constraints()` on simple_nlp, bounds_nlp
   - **NEW**: Test duplicate bounds are EXCLUDED (not just warned)
   - **NEW**: Test indexed bounds (lo_map/up_map/fx_map)
   - **NEW**: Test infinite bounds for both scalar and indexed
   - File: `tests/unit/kkt/test_objective.py`
   - Test objective variable extraction
   - File: `tests/unit/kkt/test_naming.py`
   - Test naming functions, collision handling

**Deliverables:**
- `src/kkt/kkt_system.py` - Data structures with updated fields
- `src/kkt/partition.py` - Enhanced constraint partitioning (duplicate exclusion + indexed bounds)
- `src/kkt/objective.py` - Objective variable handling
- `src/kkt/naming.py` - Multiplier naming
- `tests/unit/kkt/` - Unit tests (expect ~22 tests, up from 18)

**Acceptance Criteria:**
- [ ] All data structures defined with complete type hints
- [ ] Partition correctly separates equalities, inequalities, bounds
- [ ] **CRITICAL**: Duplicate bounds EXCLUDED from inequality list (Finding #1 fixed)
- [ ] **CRITICAL**: Indexed bounds processed via lo_map/up_map/fx_map (Finding #2 fixed)
- [ ] Infinite bounds filtered for both scalar and indexed variables
- [ ] Objective variable and defining equation extracted
- [ ] Naming convention handles all test cases
- [ ] Unit tests pass (22/22)
- [ ] Type checking passes
- [ ] Code formatted and linted

---

### Day 2: KKT Assembler - Stationarity

**Goal:** Build stationarity equations ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0

**Tasks:**

1. **Implement Stationarity Builder** (3.5 hours)
   - File: `src/kkt/stationarity.py`
   - Function: `build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]`
   - Skip objective variable (from Day 1)
   - Handle indexed bounds correctly
   - For each variable instance `x(i1)`:
     ```python
     def build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]:
         """Build stationarity: ∇f + J^T λ - π^L + π^U = 0 for each var."""
         
         stationarity = {}
         obj_info = extract_objective_info(kkt.model_ir)
         
         # Iterate over all variable instances
         for col_id in range(kkt.gradient.num_cols):
             var_name, var_indices = kkt.gradient.index_mapping.col_to_var[col_id]
             
             # Skip objective variable
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
             
             # Subtract π^L (if finite bound exists for this instance)
             if (var_name, var_indices) in kkt.multipliers_bounds_lo:
                 piL_name = create_bound_lo_multiplier_name(var_name, var_indices)
                 F_x = Binary("-", F_x, MultiplierRef(piL_name, var_indices))
             
             # Add π^U (if finite bound exists for this instance)
             if (var_name, var_indices) in kkt.multipliers_bounds_up:
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

3. **Test Stationarity on Examples** (2.5 hours)
   - File: `tests/integration/kkt/test_stationarity.py`
   - Test cases:
     - Scalar NLP: verify ∂f/∂x + λ·∂g/∂x = 0 structure
     - Indexed NLP: verify index matching (stat_x_i1 uses ∂f/∂x(i1))
     - Bounds NLP: verify π^L and π^U terms
     - **NEW**: Indexed bounds: verify correct π terms per instance
     - Infinite bounds: verify no π terms for ±INF bounds
     - Objective variable: verify no stationarity row for objvar

4. **Early Integration Smoke Test** (1 hour)
   - File: `tests/e2e/test_smoke.py` (from PREP_PLAN Task 5)
   - Implement first 4 smoke tests:
     - `test_minimal_scalar_nlp_pipeline()` - Parse → Normalize → Grad → Jac
     - `test_indexed_nlp_pipeline()` - With indexed variables
     - `test_bounds_handling_pipeline()` - Issue #24 regression
     - `test_kkt_assembler_smoke()` - Basic KKT assembly
   - Add test for indexed bounds handling
   - Add test for objective variable handling

**Deliverables:**
- `src/kkt/stationarity.py` - Stationarity builder (with objective skipping, indexed bounds)
- `src/ir/ast.py` - Add `MultiplierRef` node
- `tests/integration/kkt/test_stationarity.py` - Integration tests (~14 tests, up from 12)
- `tests/e2e/test_smoke.py` - Early smoke tests (6 tests)

**Acceptance Criteria:**
- [ ] Stationarity equations generated for all variable instances except objvar
- [ ] Objective variable skipped in stationarity
- [ ] **CRITICAL**: Indexed bounds handled correctly (π terms per instance)
- [ ] No π terms for infinite bounds (both scalar and indexed)
- [ ] Multiplier references correctly indexed
- [ ] Integration tests pass (14/14)
- [ ] Early smoke tests pass (6/6)
- [ ] Manual inspection: stationarity for simple_nlp matches hand calculation
- [ ] No Sprint 1/2 test regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 5: Early Integration Smoke Test** - ✅ Completed as part of Day 2
- Smoke tests implemented and passing
- `test_kkt_assembler_smoke()` added and verified
- Indexed bounds and objective variable tests included

---

### Day 3: KKT Assembler - Complementarity

**Goal:** Build complementarity equations and complete KKT system

**Tasks:**

1. **Implement Complementarity Builder** (4 hours)
   - File: `src/kkt/complementarity.py`
   - Function: `build_complementarity_pairs(kkt: KKTSystem) -> dict`
   - Include objective defining equation
   - Handle indexed bounds correctly
   - For inequalities g(x) ≤ 0:
     ```python
     def build_complementarity_pairs(kkt: KKTSystem) -> tuple[dict, dict, dict, dict]:
         """Build complementarity pairs for inequalities and bounds."""
         
         comp_ineq = {}
         comp_bounds_lo = {}
         comp_bounds_up = {}
         equality_eqs = {}
         
         obj_info = extract_objective_info(kkt.model_ir)
         
         # Inequalities: F_λ = -g(x) ⊥ λ ≥ 0
         # Note: Duplicate bounds already excluded by partition (Finding #1)
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
         # IMPORTANT: Include objective defining equation
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
         
         # Bounds: Only for finite bounds, including indexed (Finding #2)
         # Lower bounds: F_π^L = x(i) - lo(i) ⊥ π^L ≥ 0
         for (var_name, indices), bound_def in kkt.partition_result.bounds_lo.items():
             F_piL = Binary("-", 
                           VarRef(var_name, indices),
                           Const(bound_def.value))
             
             piL_name = create_bound_lo_multiplier_name(var_name, indices)
             comp_bounds_lo[(var_name, indices)] = ComplementarityPair(
                 equation=EquationDef(..., F_piL, Rel.GE, Const(0.0)),
                 variable=piL_name,
                 variable_indices=indices
             )
         
         # Upper bounds: F_π^U = up(i) - x(i) ⊥ π^U ≥ 0
         for (var_name, indices), bound_def in kkt.partition_result.bounds_up.items():
             F_piU = Binary("-",
                           Const(bound_def.value),
                           VarRef(var_name, indices))
             
             piU_name = create_bound_up_multiplier_name(var_name, indices)
             comp_bounds_up[(var_name, indices)] = ComplementarityPair(
                 equation=EquationDef(..., F_piU, Rel.GE, Const(0.0)),
                 variable=piU_name,
                 variable_indices=indices
             )
         
         return comp_ineq, comp_bounds_lo, comp_bounds_up, equality_eqs
     ```

2. **Main KKT Assembler** (2 hours)
   - File: `src/kkt/assemble.py`
   - Function: `assemble_kkt_system(model_ir, gradient, J_eq, J_ineq) -> KKTSystem`
   - Orchestrates all builders:
     ```python
     def assemble_kkt_system(model_ir, gradient, J_eq, J_ineq):
         # Step 1: Enhanced partition with duplicate exclusion and indexed bounds
         partition = partition_constraints(model_ir)
         
         # Log excluded duplicates (Finding #1)
         for eq_name in partition.duplicate_excluded:
             logger.warning(f"Excluding duplicate bound: {eq_name}")
         
         # Log skipped infinite bounds (including indexed)
         for var, indices, bound_type in partition.skipped_infinite:
             idx_str = f"({','.join(indices)})" if indices else ""
             logger.info(f"Skipping infinite {bound_type} bound on {var}{idx_str}")
         
         # Step 2: Extract objective info
         obj_info = extract_objective_info(model_ir)
         
         # Step 3: Create multiplier definitions (only finite bounds, including indexed)
         multipliers_eq = create_eq_multipliers(partition.equalities)
         multipliers_ineq = create_ineq_multipliers(partition.inequalities)
         multipliers_bounds_lo = create_bound_multipliers(partition.bounds_lo)
         multipliers_bounds_up = create_bound_multipliers(partition.bounds_up)
         
         # Step 4: Build KKT system
         kkt = KKTSystem(...)
         
         # Step 5: Build stationarity (skips objvar, handles indexed bounds)
         kkt.stationarity = build_stationarity_equations(kkt)
         
         # Step 6: Build complementarity (includes obj defining eq, indexed bounds)
         kkt.complementarity_ineq, kkt.complementarity_bounds_lo, \
         kkt.complementarity_bounds_up, kkt.equality_eqs = \
             build_complementarity_pairs(kkt)
         
         return kkt
     ```

3. **End-to-End KKT Test** (2.5 hours)
   - File: `tests/integration/kkt/test_kkt_full.py`
   - Test full assembly on all 5 examples:
     - simple_nlp.gms
     - bounds_nlp.gms (test infinite and indexed bounds)
     - indexed_balance.gms
     - nonlinear_mix.gms
     - scalar_nlp.gms
   - Verify:
     - Correct number of stationarity equations (num_vars - 1 for objvar)
     - Correct number of multipliers
     - Correct complementarity pairs
     - Objective defining equation included
     - No multipliers for infinite bounds
     - **NEW**: Indexed bounds produce correct number of multipliers
     - **NEW**: Duplicate bounds excluded from inequalities
     - Hand-check one example (simple_nlp) completely

4. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Verify `test_kkt_assembler_smoke()` passes with new logic
   - Add assertions for objective variable handling
   - Add assertions for indexed bounds

**Deliverables:**
- `src/kkt/complementarity.py` - Complementarity builder (indexed bounds)
- `src/kkt/assemble.py` - Main KKT assembler
- `tests/integration/kkt/test_kkt_full.py` - Full integration tests (~18 tests, up from 15)
- `tests/e2e/test_smoke.py` - Updated smoke tests (6 tests total)

**Acceptance Criteria:**
- [ ] KKT system assembled for all 5 examples
- [ ] Stationarity + complementarity equations count matches theory
- [ ] Objective defining equation included in equality_eqs
- [ ] Objective variable has no stationarity equation
- [ ] **CRITICAL**: Duplicate bounds excluded from complementarity (Finding #1 verified)
- [ ] **CRITICAL**: Indexed bounds produce correct complementarity pairs (Finding #2 verified)
- [ ] Infinite bounds produce no complementarity pairs (scalar + indexed)
- [ ] Integration tests pass (18/18)
- [ ] Smoke tests pass (6/6)
- [ ] Manual verification: simple_nlp KKT matches hand calculation
- [ ] No regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 7: Add Integration Risk Sections** - Complete this evening (2 hours)
- Review Days 4-10 plan
- Add "Integration Risks" section to each remaining day
- Document Sprint 1/2 dependencies
- Add mitigation strategies (diagnostics, early tests)
- Update PLAN.md with risk sections

---

### Day 4: GAMS Emitter - Original Symbols & Structure

**Goal:** Emit original model symbols (Sets/Aliases/Parameters) using actual IR fields and create GAMS code generation templates

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
         """Emit Variables blocks by kind (Positive/Binary/Integer/etc.)"""
         
     def emit_equations(kkt: KKTSystem) -> str:
         """Emit Equations block declarations."""
         
     def emit_equation_definitions(kkt: KKTSystem) -> str:
         """Emit equation definitions (eq_name.. lhs =E= rhs;)"""
         
     def emit_model(kkt: KKTSystem) -> str:
         """Emit Model MCP block with complementarity pairs."""
         
     def emit_solve(kkt: KKTSystem) -> str:
         """Emit Solve statement."""
     ```

2. **Implement Original Symbols Emission** (4 hours)
   - File: `src/emit/original_symbols.py`
   - **CRITICAL (Finding #3)**: Use actual IR fields, not invented ones
   - Functions:
     ```python
     def emit_original_sets(model_ir: ModelIR) -> str:
         """
         Emit Sets block from original model.
         Uses SetDef.members (not .elements).
         
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
             # Use SetDef.members (Finding #3)
             members = ', '.join(set_def.members)
             lines.append(f"    {set_name} /{members}/")
         lines.append(";")
         return '\n'.join(lines)
     
     def emit_original_aliases(model_ir: ModelIR) -> str:
         """
         Emit Alias declarations.
         Uses AliasDef.target and .universe.
         
         Example output:
         Alias(i, ip);
         Alias(j, jp);
         """
         if not model_ir.aliases:
             return ""
         
         lines = []
         for alias_name, alias_def in model_ir.aliases.items():
             # Use AliasDef.target (Finding #3)
             if alias_def.universe:
                 # Alias with universe constraint
                 lines.append(f"Alias({alias_def.target}, {alias_name});")
             else:
                 lines.append(f"Alias({alias_def.target}, {alias_name});")
         return '\n'.join(lines)
     
     def emit_original_parameters(model_ir: ModelIR) -> str:
         """
         Emit Parameters and their data.
         Uses ParameterDef.values (dict[tuple[str,...], float]).
         Scalars have empty tuple key: values[()] = value.
         
         Example output:
         Parameters
             c(i,j) /i1.j1 2.5, i1.j2 3.0, i2.j1 1.8/
             demand(j) /j1 100, j2 150/
         ;
         
         Scalars
             discount /0.95/
         ;
         """
         if not model_ir.params:
             return ""
         
         # Separate scalars (empty domain) from parameters
         scalars = {}
         parameters = {}
         
         for param_name, param_def in model_ir.params.items():
             # Use ParameterDef.domain to detect scalars (Finding #3)
             if len(param_def.domain) == 0:
                 scalars[param_name] = param_def
             else:
                 parameters[param_name] = param_def
         
         lines = []
         
         # Emit Parameters
         if parameters:
             lines.append("Parameters")
             for param_name, param_def in parameters.items():
                 # Use ParameterDef.values (Finding #3)
                 # Format tuple keys as GAMS syntax: (i1, j2) → "i1.j2"
                 data_parts = []
                 for key_tuple, value in param_def.values.items():
                     # Convert tuple to GAMS index syntax (Finding #3)
                     key_str = '.'.join(key_tuple)
                     data_parts.append(f"{key_str} {value}")
                 
                 data_str = ', '.join(data_parts)
                 domain_str = ','.join(param_def.domain)
                 lines.append(f"    {param_name}({domain_str}) /{data_str}/")
             lines.append(";")
         
         # Emit Scalars
         if scalars:
             lines.append("Scalars")
             for scalar_name, scalar_def in scalars.items():
                 # Scalars have values[()] = value (Finding #3)
                 value = scalar_def.values.get((), 0.0)
                 lines.append(f"    {scalar_name} /{value}/")
             lines.append(";")
         
         return '\n'.join(lines)
     ```

3. **Implement KKT Sets Emission** (1 hour)
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

4. **Implement Variables Emission with Kind Preservation** (2.5 hours)
   - **CRITICAL (Finding #4)**: Use VariableDef.kind to emit correct blocks
   - Primal variables grouped by kind
   - Multiplier variables
     ```python
     def emit_variables(kkt: KKTSystem) -> str:
         """
         Emit Variables blocks grouped by VariableDef.kind.
         
         Example output:
         Variables
             obj           "Objective variable"
             nu_balance(i) "Multiplier for balance equation"
         ;
         
         Positive Variables
             x(i)          "Primal variable (POSITIVE)"
             lam_g1(i)     "Multiplier for inequality g1"
             piL_x(i)      "Multiplier for lower bound on x"
             piU_x(i)      "Multiplier for upper bound on x"
         ;
         
         Binary Variables
             y(i)          "Binary decision variable"
         ;
         
         Integer Variables
             z(i)          "Integer variable"
         ;
         """
         # Group variables by kind (Finding #4)
         var_groups = {
             VarKind.CONTINUOUS: [],
             VarKind.POSITIVE: [],
             VarKind.NEGATIVE: [],
             VarKind.BINARY: [],
             VarKind.INTEGER: []
         }
         
         # Group primal variables by kind
         for var_name, var_def in kkt.model_ir.variables.items():
             var_groups[var_def.kind].append((var_name, var_def.domain))
         
         # Add multipliers to appropriate groups
         # Free multipliers (ν for equalities) → CONTINUOUS
         for mult_name, mult_def in kkt.multipliers_eq.items():
             var_groups[VarKind.CONTINUOUS].append((mult_name, mult_def.domain))
         
         # Positive multipliers (λ, π^L, π^U) → POSITIVE
         for mult_name, mult_def in kkt.multipliers_ineq.items():
             var_groups[VarKind.POSITIVE].append((mult_name, mult_def.domain))
         for mult_name, mult_def in kkt.multipliers_bounds_lo.items():
             var_groups[VarKind.POSITIVE].append((mult_name, mult_def.domain))
         for mult_name, mult_def in kkt.multipliers_bounds_up.items():
             var_groups[VarKind.POSITIVE].append((mult_name, mult_def.domain))
         
         # Emit blocks
         lines = []
         
         kind_to_block = {
             VarKind.CONTINUOUS: "Variables",
             VarKind.POSITIVE: "Positive Variables",
             VarKind.NEGATIVE: "Negative Variables",
             VarKind.BINARY: "Binary Variables",
             VarKind.INTEGER: "Integer Variables"
         }
         
         for kind, block_name in kind_to_block.items():
             if var_groups[kind]:
                 lines.append(block_name)
                 for var_name, domain in var_groups[kind]:
                     if domain:
                         lines.append(f"    {var_name}({','.join(domain)})")
                     else:
                         lines.append(f"    {var_name}")
                 lines.append(";")
         
         return '\n'.join(lines)
     ```

5. **Test Template Generation** (3 hours)
   - File: `tests/unit/emit/test_templates.py`
   - Test each template function separately
   - File: `tests/unit/emit/test_original_symbols.py`
   - **CRITICAL**: Test with actual IR structures
   - Test scalars (empty domain, values[()])
   - Test multi-dimensional parameters (tuple keys → "i1.j2" format)
   - Test alias universes
   - File: `tests/unit/emit/test_variable_kinds.py`
   - **NEW**: Test variable kind preservation (Finding #4)
   - Verify GAMS syntax correctness
   - Test with simple_nlp and bounds_nlp

**Deliverables:**
- `src/emit/templates.py` - Template functions
- `src/emit/original_symbols.py` - Original symbols emission (using actual IR fields)
- `tests/unit/emit/test_templates.py` - Unit tests (~20 tests)
- `tests/unit/emit/test_original_symbols.py` - Tests for original symbols (~12 tests)
- `tests/unit/emit/test_variable_kinds.py` - **NEW** Tests for variable kinds (~8 tests)

**Acceptance Criteria:**
- [ ] All template functions implemented
- [ ] **CRITICAL**: Original symbols use actual IR fields (SetDef.members, ParameterDef.values, etc.) (Finding #3 fixed)
- [ ] **CRITICAL**: Variable kinds preserved in emission (Finding #4 fixed)
- [ ] Scalars handled correctly (empty domain, values[()])
- [ ] Multi-dimensional parameter keys formatted as GAMS syntax ("i1.j2")
- [ ] Alias universes handled correctly
- [ ] Generated Sets/Variables blocks syntactically correct
- [ ] Unit tests pass (40/40)
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
   - Handle all AST node types including `MultiplierRef`:
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
             case MultiplierRef(name, indices):
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
   - Test MultiplierRef conversion
   - Test operator precedence
   - Test nested expressions
   - Verify power operator (Issue #25 check)

**Deliverables:**
- `src/emit/expr_to_gams.py` - AST → GAMS converter (with MultiplierRef)
- `src/emit/equations.py` - Equation emission
- `tests/unit/emit/test_expr_to_gams.py` - Expression tests (~22 tests)
- `tests/unit/emit/test_equations.py` - Equation tests (~10 tests)

**Acceptance Criteria:**
- [ ] All AST nodes convert to valid GAMS syntax
- [ ] MultiplierRef converts correctly
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
   - Handle objective defining equation pairing
   - Model MCP syntax:
     ```gams
     Model mcp_model /
         * Stationarity conditions (primal variables, except objvar)
         stat_x.x
         stat_y.y
         
         * Inequality complementarities (duplicates already excluded)
         comp_g1.lam_g1
         comp_g2.lam_g2
         
         * Equality constraints (free multipliers)
         eq_h1.nu_h1
         eq_objdef.obj  * Objective defining equation paired with objvar
         
         * Bound complementarities (finite bounds only, including indexed)
         bound_lo_x_i1.piL_x_i1
         bound_lo_x_i2.piL_x_i2
         bound_up_x_i1.piU_x_i1
     /;
     ```
   - Pairing rules:
     - Stationarity equations paired with primal variables (except objvar)
     - Complementarity equations paired with multipliers
     - Equality equations paired with free multipliers
     - Objective defining equation paired with objvar (not a multiplier)

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
   - Include original symbols first
   - Combine all pieces:
     ```python
     def emit_gams_mcp(kkt: KKTSystem, options: dict = None) -> str:
         sections = []
         
         # Header comment
         sections.append("* Generated by nlp2mcp")
         sections.append("* KKT conditions for MCP")
         sections.append("")
         
         # Original model symbols (Finding #3 compliant)
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
         
         # Variables (Finding #4 compliant - preserves kinds)
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
   - Verify original symbols appear in output
   - Verify objective equation pairing
   - Verify variable kinds preserved
   - Verify generated GAMS is syntactically valid
   - Manually inspect output

5. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Implement `test_gams_emitter_smoke()` (remove @skip)
   - Verify full pipeline doesn't crash
   - Verify output contains original symbols
   - Verify output preserves variable kinds

**Deliverables:**
- `src/emit/model.py` - Model MCP emission (with objective handling)
- `src/emit/emit_gams.py` - Main emitter (with original symbols, variable kinds)
- `tests/integration/emit/test_emit_full.py` - Integration tests (~12 tests, up from 10)
- `tests/e2e/test_smoke.py` - Updated smoke tests (7 tests total)

**Acceptance Criteria:**
- [ ] Model MCP emitted with correct complementarity pairs
- [ ] Objective defining equation paired with objvar
- [ ] Original Sets/Aliases/Parameters appear in output (using actual IR fields)
- [ ] **CRITICAL**: Variable kinds preserved in output (Finding #4 verified)
- [ ] Full GAMS code generated for simple_nlp
- [ ] Generated code is syntactically valid (manual inspection)
- [ ] Integration tests pass (12/12)
- [ ] Smoke tests pass (7/7)
- [ ] No regressions

---

### Day 7: Mid-Sprint Checkpoint & CLI

**Goal:** Review progress, address integration issues, implement CLI

**Integration Risks:**

**Sprint 1 Dependencies:**
- Assumption: Parser captures all original symbols needed for emission
- Risk: Some symbols (aliases, parameters) missing or incomplete
- Mitigation: Integration health check validates symbols present in generated output

**Sprint 2 Dependencies:**
- Assumption: All derivative computations from Days 1-6 are correct
- Risk: Accumulated errors from previous sprints
- Mitigation: Run full Sprint 1/2 test suites as part of checkpoint

**Days 4-6 Dependencies:**
- Assumption: GAMS emission from Days 4-6 is syntactically correct
- Risk: Generated GAMS files don't compile or have syntax errors
- Mitigation: Test all 5 examples through full pipeline; validate syntax if GAMS available

**Cross-Sprint Integration:**
- Assumption: Full pipeline (Parse → Normalize → AD → KKT → Emit) works end-to-end
- Risk: Integration issues between sprint boundaries
- Mitigation: Mid-sprint checkpoint explicitly tests cross-sprint integration points

**CLI Integration:**
- Assumption: CLI can orchestrate all pipeline stages correctly
- Risk: Pipeline stages have incompatible interfaces
- Mitigation: API contract tests should catch interface mismatches early

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
   - Verify generated GAMS includes original symbols
   - Verify no infinite bound multipliers created
   - Verify objective variable handling correct
   - **NEW**: Verify duplicate bounds excluded (Finding #1)
   - **NEW**: Verify indexed bounds handled (Finding #2)
   - **NEW**: Verify variable kinds preserved (Finding #4)
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
     @click.option('--show-excluded', is_flag=True, default=True, 
                   help='Show duplicate bounds excluded from inequalities')
     def main(input_file, output, verbose, validate, comments, show_excluded):
         # Load and parse
         model = parse_model_file(input_file)
         normalize_model(model)
         
         # Compute derivatives
         gradient = compute_objective_gradient(model)
         J_eq, J_ineq = compute_constraint_jacobian(model)
         
         # Assemble KKT
         kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
         
         # Log excluded duplicates (Finding #1)
         if show_excluded:
             for eq_name in kkt.duplicate_bounds_excluded:
                 click.echo(f"Excluded duplicate bound: {eq_name}", err=True)
         
         if verbose:
             # Log skipped infinite bounds (including indexed)
             click.echo(f"Skipped {len(kkt.skipped_infinite_bounds)} infinite bounds")
             for var, indices, bound_type in kkt.skipped_infinite_bounds:
                 idx_str = f"({','.join(indices)})" if indices else ""
                 click.echo(f"  {var}{idx_str}.{bound_type} = ±INF")
             
             click.echo(f"Created {len(kkt.stationarity)} stationarity equations")
             click.echo(f"Created {len(kkt.complementarity_ineq)} inequality multipliers")
             click.echo(f"Created {len(kkt.multipliers_bounds_lo)} lower bound multipliers")
             click.echo(f"Created {len(kkt.multipliers_bounds_up)} upper bound multipliers")
         
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
   - Test options (--verbose, --comments, --show-excluded)

**Deliverables:**
- `src/cli.py` - Command-line interface (with exclusion reporting)
- `tests/integration/test_cli.py` - CLI tests (~14 tests, up from 12)
- Mid-sprint checkpoint report (in PR comment or doc)

**Acceptance Criteria:**
- [ ] Mid-sprint checkpoint completed
- [ ] All tests passing (expect ~200 total, up from ~175)
- [ ] CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`
- [ ] CLI shows excluded duplicate bounds
- [ ] CLI reports skipped infinite bounds in verbose mode (including indexed)
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

1. **Generate Golden Reference Files** (3 hours)
   - For each of 5 example models, manually:
     - Run pipeline: `nlp2mcp examples/simple_nlp.gms -o golden/simple_nlp_mcp.gms`
     - Manually review and verify correctness
     - Hand-check KKT equations match theory
     - Verify original symbols present (using actual IR fields)
     - Verify no infinite bound multipliers
     - Verify objective variable handling
     - **NEW**: Verify duplicate bounds excluded (Finding #1)
     - **NEW**: Verify indexed bounds handled (Finding #2)
     - **NEW**: Verify variable kinds preserved (Finding #4)
     - Mark as golden reference
   - Files:
     - `tests/golden/simple_nlp_mcp.gms`
     - `tests/golden/bounds_nlp_mcp.gms` (test infinite and indexed bounds)
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
   - **NOTE FROM MID-SPRINT CHECKPOINT**: Pay special attention to:
     - Dict iteration order in `emit_model_mcp()` (use `sorted()`)
     - Multiplier ordering in complementarity pairs
     - Variable/equation ordering in template generation
   - Verify infinite bounds consistently skipped
   - Verify duplicate exclusions deterministic
   - Verify indexed bounds deterministic

**Deliverables:**
- `tests/golden/` - Golden reference files (5 files)
- `tests/e2e/test_golden.py` - Golden tests (5 tests)

**Acceptance Criteria:**
- [ ] All 5 golden reference files generated and verified
- [ ] Golden files include original model symbols (actual IR fields)
- [ ] Golden files show correct infinite bound handling (scalar + indexed)
- [ ] Golden files show correct objective variable treatment
- [ ] **NEW**: Golden files show duplicate bounds excluded (Finding #1)
- [ ] **NEW**: Golden files show indexed bounds correctly (Finding #2)
- [ ] **NEW**: Golden files preserve variable kinds (Finding #4)
- [ ] Golden tests pass (5/5)
- [ ] Output is deterministic (tested with 5 runs each)
- [ ] Diff output is clear when tests fail
- [ ] Golden files committed to git

---

### Day 9: GAMS Validation (Optional) & Documentation

**Goal:** Add optional GAMS validation and complete documentation

**Integration Risks:**

**Sprint 1 Dependencies:**
- Assumption: All original model constructs are documented correctly
- Risk: Documentation doesn't match actual parser/IR behavior
- Mitigation: Review documentation against actual code; test examples validate docs

**Sprint 2 Dependencies:**
- Assumption: Derivative computation is well-understood for documentation
- Risk: Documentation oversimplifies or misrepresents AD behavior
- Mitigation: Include concrete examples from test suite in documentation

**Days 1-8 Dependencies:**
- Assumption: All features implemented Days 1-8 are stable and ready to document
- Risk: Documentation written before features fully stabilized
- Mitigation: Document after Day 8 golden tests pass; update docs if bugs found Day 10

**GAMS Availability:**
- Assumption: GAMS validation is optional and not required for success
- Risk: Can't validate syntax without GAMS installation
- Mitigation: Make validation feature optional; use golden test comparisons as alternative

**Documentation Completeness:**
- Assumption: All 4 critical findings (duplicate exclusion, indexed bounds, IR fields, variable kinds) are documented
- Risk: Missing documentation for critical features
- Mitigation: Checklist of all findings to ensure documentation coverage

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

2. **Document KKT Assembly** (3 hours)
   - File: `docs/kkt/KKT_ASSEMBLY.md`
   - Mathematical notation for KKT conditions
   - Explain stationarity construction
   - Explain complementarity conditions
   - Document multiplier naming conventions
   - Document infinite bounds handling (scalar + indexed) (Finding #2)
   - Document objective variable handling
   - **NEW**: Document duplicate bounds exclusion (Finding #1)

3. **Document GAMS Emission** (3 hours)
   - File: `docs/emit/GAMS_EMISSION.md`
   - Document original symbols emission
   - **NEW**: Emphasize use of actual IR fields (Finding #3)
   - **NEW**: Document variable kind preservation (Finding #4)
   - Template examples
   - AST → GAMS conversion rules
   - Model MCP pairing rules
   - Sign conventions
   - Show example with objective defining equation pairing
   - **NEW**: Show example with indexed bounds
   - **NEW**: Show example with multiple variable kinds

4. **Update README** (1 hour)
   - Add usage examples
   - Document CLI options (including --show-excluded)
   - Show before/after example
   - Link to documentation
   - Mention bounds handling features
   - **NEW**: Mention variable kind preservation

**Deliverables:**
- `src/validation/gams_check.py` - Optional GAMS validation
- `docs/kkt/KKT_ASSEMBLY.md` - KKT documentation (with new sections)
- `docs/emit/GAMS_EMISSION.md` - Emission documentation (with Finding #3, #4 sections)
- Updated `README.md`

**Acceptance Criteria:**
- [ ] GAMS validation implemented (optional feature)
- [ ] KKT assembly fully documented with math notation
- [ ] Infinite bounds handling documented (scalar + indexed)
- [ ] Objective variable handling documented
- [ ] **NEW**: Duplicate bounds exclusion documented (Finding #1)
- [ ] GAMS emission fully documented with examples
- [ ] Original symbols emission documented (using actual IR fields) (Finding #3)
- [ ] **NEW**: Variable kind preservation documented (Finding #4)
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

**Integration Risks:**

**Full Pipeline Integration:**
- Assumption: All pipeline stages work together correctly
- Risk: Edge cases expose integration bugs between stages
- Mitigation: Comprehensive edge case testing (listed below); fix bugs immediately

**Sprint 1/2 Regression:**
- Assumption: Sprint 3 changes don't break Sprint 1/2 functionality
- Risk: Subtle regressions in parser or AD engine
- Mitigation: Run full Sprint 1/2 test suites; all must still pass

**Test Coverage:**
- Assumption: >90% coverage means code is well-tested
- Risk: High coverage but critical paths untested
- Mitigation: Focus on testing all 4 critical findings explicitly

**Critical Findings Verification:**
- Assumption: All 4 findings from final review are fixed and tested
- Risk: Fixes incomplete or not validated end-to-end
- Mitigation: Explicit test cases for each finding:
  - Finding #1: Test duplicate bounds exclusion with CLI output
  - Finding #2: Test indexed bounds in golden tests
  - Finding #3: Test actual IR fields in emission tests  
  - Finding #4: Test variable kinds in generated GAMS

**Time Risk:**
- Assumption: 10 hours is enough for polish and wrap-up
- Risk: Bug fixes take longer than expected
- Mitigation: Prioritize critical bugs; defer nice-to-have fixes to Sprint 4

**Tasks:**

1. **Comprehensive Testing** (3 hours)
   - Run full test suite
   - Run all 5 examples through CLI
   - Test edge cases:
     - Models with only equalities
     - Models with only inequalities
     - Models with no bounds
     - Models with all infinite bounds
     - Scalar models (no indexing)
     - Models with potential duplicate bounds
     - Models where objective variable has different name
     - **NEW**: Models with indexed bounds only
     - **NEW**: Models with mixed variable kinds (Positive/Binary/Integer)
     - **NEW**: Models with multi-dimensional parameters
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
   - Document all warnings generated by system

3. **Integration Test Coverage** (2.5 hours)
   - Review test coverage:
     ```bash
     pytest --cov=src tests/
     ```
   - Add tests for uncovered code paths
   - Add tests for all new features:
     - Duplicate exclusion (Finding #1)
     - Indexed bounds (Finding #2)
     - Actual IR field usage (Finding #3)
     - Variable kind preservation (Finding #4)
   - Target: >90% coverage for new Sprint 3 code

4. **Final Validation** (1 hour)
   - Verify all success metrics achieved
   - Run smoke tests one final time
   - Verify API contract tests still pass
   - Verify no Sprint 1/2 regressions
   - Verify all 4 review findings addressed

5. **Sprint Wrap-Up** (1.5 hours)
   - Create Sprint 3 summary document
   - Document review feedback and how it was addressed (both rounds)
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
- [ ] All 480+ tests pass (up from 440+)
- [ ] All 5 examples convert successfully
- [ ] Generated MCP files include original symbols
- [ ] Infinite bounds handled correctly (scalar + indexed)
- [ ] Objective variable handled correctly
- [ ] **CRITICAL**: Duplicate bounds excluded from inequalities (Finding #1 verified)
- [ ] **CRITICAL**: Indexed bounds handled correctly (Finding #2 verified)
- [ ] **CRITICAL**: Original symbols use actual IR fields (Finding #3 verified)
- [ ] **CRITICAL**: Variable kinds preserved (Finding #4 verified)
- [ ] Generated MCP files compile in GAMS (if GAMS available)
- [ ] Golden tests pass (5/5)
- [ ] CLI works correctly with all options
- [ ] Code quality checks pass
- [ ] Documentation complete
- [ ] Sprint 3 success metrics achieved
- [ ] All 4 final review findings verified fixed

---

## Sprint 3 Success Criteria Summary

### Functional Requirements ✅

- [ ] **KKT Assembler**: Converts derivatives to KKT system
  - Stationarity equations for all variables (except objvar)
  - Complementarity conditions for inequalities
  - Multiplier variables created correctly
  - **FIXED (Finding #1)**: Duplicate bounds excluded from inequalities
  - **FIXED (Finding #2)**: Indexed bounds handled via lo_map/up_map/fx_map
  - Infinite bounds filtered (no π for ±INF, scalar + indexed)
  - Objective variable handled specially

- [ ] **GAMS Emitter**: Generates valid GAMS MCP code
  - **FIXED (Finding #3)**: Original Sets/Aliases/Parameters use actual IR fields
  - Sets, Variables, Equations blocks
  - Equation definitions with correct syntax
  - Model MCP with complementarity pairs
  - **FIXED (Finding #4)**: Variable kinds preserved (Positive/Binary/Integer/etc.)
  - Objective defining equation paired with objvar
  - Solve statement

- [ ] **CLI**: `nlp2mcp` command works
  - Converts all 5 example models
  - Options (--output, --verbose, --validate, --show-excluded) work
  - Shows excluded duplicate bounds
  - Reports skipped infinite bounds (including indexed)
  - Error messages are clear

- [ ] **Golden Tests**: Reference outputs validated
  - 5 golden reference files
  - All golden tests pass
  - Deterministic output

### Quality Requirements ✅

- [ ] **Test Coverage**:
  - Unit tests: ~210 total (70 new, up from 60)
  - Integration tests: ~72 total (22 new, up from 18)
  - E2E tests: ~22 total (7 new)
  - Total: 300+ tests passing (up from 260+)

- [ ] **Code Quality**:
  - Type checking passes (`mypy src/`)
  - Linting passes (`ruff check`)
  - Formatting passes (`ruff format`)
  - Coverage >90% for Sprint 3 code

- [ ] **Documentation**:
  - KKT assembly documented (with Finding #1 addressed)
  - GAMS emission documented (with Findings #3, #4 addressed)
  - Bounds handling documented (Finding #2 addressed)
  - Objective variable handling documented
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

### Final Review Findings Verified ✅

- [ ] **Finding #1**: Duplicate bounds excluded from inequality list
  - `partition_constraints()` excludes (not just warns)
  - No duplicate complementarity pairs generated
  - CLI reports excluded bounds with --show-excluded

- [ ] **Finding #2**: Indexed bounds handled correctly
  - lo_map/up_map/fx_map iteration in partition logic
  - Finite/infinite filtering per instance
  - Correct number of π multipliers

- [ ] **Finding #3**: Original symbols use actual IR fields
  - SetDef.members (not .elements)
  - ParameterDef.values (not .data or .is_scalar)
  - Scalars: empty domain, values[()] = value
  - Multi-dim keys: tuple → "i1.j2" GAMS syntax

- [ ] **Finding #4**: Variable kinds preserved
  - VariableDef.kind consulted during emission
  - Correct GAMS blocks (Positive/Binary/Integer/etc.)
  - Primal variable semantics match source model

---

## Risk Management

### High-Priority Risks

**Risk 1: GAMS Syntax Correctness**
- **Impact:** Generated code doesn't compile in GAMS
- **Likelihood:** Low (reduced with actual IR fields + variable kind preservation)
- **Mitigation:**
  - Use actual IR fields for all emissions (Finding #3)
  - Preserve variable kinds (Finding #4)
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
  - Indexed bounds add complexity (Finding #2)
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
- **Likelihood:** Low-Medium (review adjustments added work)
- **Mitigation:**
  - Strict focus on 5 example models only
  - Mid-sprint checkpoint on Day 7
  - Optional features clearly marked
  - Final review adjustments add ~2 days of work but are critical
- **Contingency:** Move optional features to Sprint 4

### New Risks from Final Review Adjustments

**Risk 7: Indexed Bounds Complexity**
- **Impact:** lo_map/up_map/fx_map iteration logic has bugs
- **Likelihood:** Medium
- **Mitigation:**
  - Comprehensive unit tests for indexed bounds
  - Test all 5 examples (at least one has indexed bounds)
  - Early smoke tests on Day 2
- **Contingency:** Fall back to scalar bounds only for v1

**Risk 8: Variable Kind Emission Edge Cases**
- **Impact:** Some variable kinds don't emit correctly
- **Likelihood:** Low
- **Mitigation:**
  - Test all VarKind enum values
  - Verify with examples that have mixed kinds
  - Unit tests for variable grouping logic
- **Contingency:** Emit all as Variables with .lo/.up attributes

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
2. **bounds_nlp.gms** - Variable bounds handling (Issue #24 regression test, test infinite and indexed bounds)
3. **indexed_balance.gms** - Balance equations with indexing
4. **nonlinear_mix.gms** - Mixed nonlinear functions, power operator
5. **scalar_nlp.gms** - Simple scalar optimization (no indexing)

### Changes from PLAN_REVISED.md

**Critical Fixes (from PLAN_REVIEW_FINAL.md):**
1. **Finding #1**: Duplicate bounds now EXCLUDED (not just warned)
   - Changed partition logic to not append to inequalities list
   - Added `duplicate_bounds_excluded` field (not `duplicate_bounds_warnings`)
2. **Finding #2**: Indexed bounds support added
   - Iterate over lo_map/up_map/fx_map (not just scalar .lo/.up/.fx)
   - Bounds dict keys now (var_name, indices) tuples
   - Skipped infinite bounds track indices too
3. **Finding #3**: Original symbol emission uses actual IR fields
   - SetDef.members (not .elements)
   - ParameterDef.values (not .data or .is_scalar)
   - Scalar detection via empty domain
   - Tuple keys → "i1.j2" GAMS syntax
4. **Finding #4**: Variable kind preservation added
   - emit_variables() groups by VariableDef.kind
   - Separate blocks for Positive/Binary/Integer/etc.
   - New test file for variable kinds

**Impact on Plan:**
- Day 1: +1 hour (indexed bounds, duplicate exclusion logic)
- Day 2: +0.5 hours (indexed bounds in stationarity)
- Day 3: +1 hour (indexed bounds in complementarity)
- Day 4: +2 hours (actual IR fields, variable kinds)
- Day 5-6: No change
- Day 7: +0.5 hours (CLI exclusion reporting)
- Day 8: +0.5 hours (verify all findings in golden tests)
- Day 9: +1 hour (document all findings)
- Day 10: +0.5 hours (test all findings)
- **Total:** ~7 hours added across sprint (manageable within buffer)

**Test Count Changes:**
- Unit tests: 210 (was 180, +30)
- Integration tests: 72 (was 60, +12)
- E2E tests: 22 (was 20, +2)
- Total: 300+ (was 260+, +40)

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

### First Review (PLAN_REVIEW.md)

#### Gap #1: Missing data/alias emission
**Status:** ✅ Addressed
**Implementation:**
- Added `emit_original_sets()`, `emit_original_aliases()`, `emit_original_parameters()` to Day 4
- Modified main emitter to include original symbols before KKT blocks
- Added unit tests for original symbol emission
- Updated documentation

#### Gap #2: Bounds vs. explicit constraints not addressed
**Status:** ✅ Addressed
**Implementation:**
- Enhanced `partition_constraints()` to detect user-authored bounds
- Added `duplicate_bounds_warnings` to KKTSystem
- Added `--warn-duplicates` CLI option
- Added tests for duplicate detection

#### Gap #3: Infinite bounds handling absent
**Status:** ✅ Addressed
**Implementation:**
- Modified partition logic to filter ±INF bounds
- Added `skipped_infinite_bounds` to KKTSystem
- Modified stationarity builder to skip π terms for infinite bounds
- Modified complementarity builder to skip infinite bound pairs
- Added tests for infinite bounds
- Documented in KKT_ASSEMBLY.md

#### Gap #4: Objective variable/equation flow undefined
**Status:** ✅ Addressed
**Implementation:**
- Created `src/kkt/objective.py` with `extract_objective_info()`
- Modified stationarity builder to skip objective variable
- Modified complementarity builder to include objective defining equation
- Modified Model MCP emission to pair objective equation with objvar
- Added tests for objective variable handling
- Documented in KKT_ASSEMBLY.md and GAMS_EMISSION.md

### Final Review (PLAN_REVIEW_FINAL.md)

#### Finding #1: Duplicate bounds only warned, not excluded
**Status:** ✅ Addressed
**Implementation:**
- Changed partition logic to EXCLUDE duplicates from inequality list (not just warn)
- Changed field name from `duplicate_bounds_warnings` to `duplicate_bounds_excluded`
- Modified CLI to report exclusions with `--show-excluded` option
- No duplicate complementarity pairs will be generated

#### Finding #2: Indexed bounds ignored
**Status:** ✅ Addressed
**Implementation:**
- Extended bounds processing to iterate over lo_map/up_map/fx_map
- Changed bounds dict keys to (var_name, indices) tuples
- Applied finite/infinite filtering per indexed instance
- Updated stationarity and complementarity builders
- Indexed bounds now correctly produce π multipliers

#### Finding #3: Original symbol emission uses non-existent fields
**Status:** ✅ Addressed
**Implementation:**
- Changed to use SetDef.members (not .elements)
- Changed to use ParameterDef.values (not .data or .is_scalar)
- Scalars detected via empty domain, accessed via values[()]
- Multi-dim parameter keys formatted as GAMS syntax ("i1.j2")
- Added comprehensive tests for actual IR structures

#### Finding #4: Variable kinds not preserved
**Status:** ✅ Addressed
**Implementation:**
- Modified emit_variables() to group by VariableDef.kind
- Emit separate blocks for Positive/Binary/Integer/Negative/Continuous
- Multipliers added to appropriate kind groups
- Added test file for variable kind preservation
- Ensures primal variable semantics match source model
