# Sprint 3: KKT Synthesis + GAMS MCP Code Generation

**Duration:** 2 weeks (10 working days)  
**Start Date:** TBD  
**Goal:** Transform NLP models to runnable GAMS MCP files via KKT conditions

---

## Overview

Sprint 3 completes the end-to-end NLP → MCP transformation by:

1. **KKT System Assembly** - Convert derivatives into KKT equations (stationarity + complementarity)
2. **GAMS Code Generation** - Emit valid GAMS MCP syntax from KKT system
3. **CLI Integration** - Create `nlp2mcp` command-line tool
4. **Golden Test Suite** - Text-based golden tests for all example models
5. **Optional GAMS Validation** - Verify generated MCP compiles/solves (if GAMS available)

### What We're Building

```
Input:  examples/simple_nlp.gms (GAMS NLP model)
        ↓
Output: simple_nlp_mcp.gms (GAMS MCP model with KKT conditions)
        - Multiplier variables (λ, ν, π^L, π^U)
        - Stationarity equations
        - Complementarity conditions
        - Model MCP declaration
```

### Key Components

1. **`src/kkt/assemble.py`** - KKT system assembler
   - Partition constraints (equalities h, inequalities g)
   - Create multiplier variables for each constraint row
   - Build stationarity: ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0
   - Build complementarity: F_λ ⊥ λ, F_ν = h(x), F_π^L ⊥ π^L, F_π^U ⊥ π^U

2. **`src/emit/emit_gams.py`** - GAMS code generator  
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
- ✅ Golden tests pass (generated output matches expected)
- ✅ CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`

**Code Quality:**
- ✅ All unit tests pass (expect ~50 new tests)
- ✅ All integration tests pass (expect ~15 new tests)
- ✅ All e2e/golden tests pass (5 tests)
- ✅ Type checking passes (`mypy src/`)
- ✅ Linting passes (`ruff check`)
- ✅ Code formatted (`ruff format`)

**Documentation:**
- ✅ KKT assembly documented with mathematical notation
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

**Goal:** Define KKT system data structures and partition constraints

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
         
         # Multipliers
         multipliers_eq: dict[str, MultiplierDef]  # ν for equalities
         multipliers_ineq: dict[str, MultiplierDef]  # λ for inequalities  
         multipliers_bounds_lo: dict[str, MultiplierDef]  # π^L
         multipliers_bounds_up: dict[str, MultiplierDef]  # π^U
         
         # KKT equations
         stationarity: dict[str, EquationDef]  # One per variable instance
         complementarity_ineq: dict[str, ComplementarityPair]
         complementarity_bounds_lo: dict[str, ComplementarityPair]
         complementarity_bounds_up: dict[str, ComplementarityPair]
     
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

2. **Implement Constraint Partitioning** (2 hours)
   - File: `src/kkt/partition.py`
   - Function: `partition_constraints(model_ir: ModelIR) -> tuple`
   - Returns: `(equalities, inequalities, bounds_lo, bounds_up)`
   - Logic:
     ```python
     # Equalities: equations with Rel.EQ
     equalities = [name for name in model_ir.equalities]
     
     # Inequalities: equations with Rel.LE (normalized to ≤ 0)
     inequalities = [name for name in model_ir.inequalities 
                     if name not in model_ir.normalized_bounds]
     
     # Bounds: from normalized_bounds dict
     bounds_lo = {k: v for k, v in model_ir.normalized_bounds.items() 
                  if k.endswith('_lo')}
     bounds_up = {k: v for k, v in model_ir.normalized_bounds.items() 
                  if k.endswith('_up')}
     ```

3. **Create Multiplier Naming Convention** (1 hour)
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

4. **Write Unit Tests** (2 hours)
   - File: `tests/unit/kkt/test_partition.py`
   - Test `partition_constraints()` on simple_nlp, bounds_nlp
   - File: `tests/unit/kkt/test_naming.py`
   - Test naming functions, collision handling

**Deliverables:**
- `src/kkt/kkt_system.py` - Data structures
- `src/kkt/partition.py` - Constraint partitioning
- `src/kkt/naming.py` - Multiplier naming
- `tests/unit/kkt/` - Unit tests (expect ~15 tests)

**Acceptance Criteria:**
- [ ] All data structures defined with complete type hints
- [ ] Partition correctly separates equalities, inequalities, bounds
- [ ] Naming convention handles all test cases
- [ ] Unit tests pass (15/15)
- [ ] Type checking passes
- [ ] Code formatted and linted

---

### Day 2: KKT Assembler - Stationarity

**Goal:** Build stationarity equations ∇f + J_g^T λ + J_h^T ν - π^L + π^U = 0

**Tasks:**

1. **Implement Stationarity Builder** (3 hours)
   - File: `src/kkt/stationarity.py`
   - Function: `build_stationarity_equations(kkt: KKTSystem) -> dict[str, EquationDef]`
   - For each variable instance `x(i1)`:
     ```python
     # Start with gradient component
     F_x = ∂f/∂x(i1)  # From gradient.entries
     
     # Add J_eq^T ν
     for each equality constraint row r:
         if J_eq[r, col_x(i1)] != 0:
             F_x += J_eq[r, col_x(i1)] * ν_r
     
     # Add J_ineq^T λ  
     for each inequality constraint row r:
         if J_ineq[r, col_x(i1)] != 0:
             F_x += J_ineq[r, col_x(i1)] * λ_r
     
     # Subtract π^L (if bound exists)
     if x(i1) has lower bound:
         F_x -= π^L_x(i1)
     
     # Add π^U (if bound exists)
     if x(i1) has upper bound:
         F_x += π^U_x(i1)
     
     # Create equation: F_x = 0
     stationarity[f"stat_x_{i1}"] = EquationDef(..., F_x, Rel.EQ, 0)
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

4. **Early Integration Smoke Test** (1 hour)
   - File: `tests/e2e/test_smoke.py` (from PREP_PLAN Task 5)
   - Implement first 3 smoke tests:
     - `test_minimal_scalar_nlp_pipeline()` - Parse → Normalize → Grad → Jac
     - `test_indexed_nlp_pipeline()` - With indexed variables
     - `test_bounds_handling_pipeline()` - Issue #24 regression
   - Add skeleton for `test_kkt_assembler_smoke()` (implement today)

**Deliverables:**
- `src/kkt/stationarity.py` - Stationarity builder
- `src/ir/ast.py` - Add `MultiplierRef` node
- `tests/integration/kkt/test_stationarity.py` - Integration tests (~10 tests)
- `tests/e2e/test_smoke.py` - Early smoke tests (4 tests implemented)

**Acceptance Criteria:**
- [ ] Stationarity equations generated for all variable instances
- [ ] Multiplier references correctly indexed
- [ ] Integration tests pass (10/10)
- [ ] Early smoke tests pass (4/4)
- [ ] Manual inspection: stationarity for simple_nlp matches hand calculation
- [ ] No Sprint 1/2 test regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 5: Early Integration Smoke Test** - ✅ Completed as part of Day 2
- Smoke tests implemented and passing
- `test_kkt_assembler_smoke()` added and verified

---

### Day 3: KKT Assembler - Complementarity

**Goal:** Build complementarity equations and complete KKT system

**Tasks:**

1. **Implement Complementarity Builder** (3 hours)
   - File: `src/kkt/complementarity.py`
   - Function: `build_complementarity_pairs(kkt: KKTSystem) -> dict`
   - For inequalities g(x) ≤ 0:
     ```python
     # Complementarity: F_λ = -g(x) ⊥ λ ≥ 0
     # In GAMS MCP: -g(x) =G= 0 paired with λ.LO = 0
     F_lam = negate(g(x))  # -g(x)
     comp_pairs[f"comp_{eq_name}"] = ComplementarityPair(
         equation=EquationDef(..., F_lam, Rel.GE, 0),
         variable=f"lam_{eq_name}",
         variable_indices=eq_indices
     )
     ```
   - For equalities h(x) = 0:
     ```python
     # Free multiplier: F_ν = h(x) = 0 with ν free
     # In GAMS: h(x) =E= 0 (no complementarity, ν is free variable)
     F_nu = h(x)
     equality_eqs[f"eq_{eq_name}"] = EquationDef(..., F_nu, Rel.EQ, 0)
     ```
   - For bounds x ≥ lo:
     ```python
     # Complementarity: F_π^L = x - lo ⊥ π^L ≥ 0
     # In GAMS MCP: x - lo =G= 0 paired with piL.LO = 0
     F_piL = Binary("-", VarRef(x), Const(lo))
     comp_pairs[f"bound_lo_{var_name}"] = ComplementarityPair(
         equation=EquationDef(..., F_piL, Rel.GE, 0),
         variable=f"piL_{var_name}",
         variable_indices=var_indices
     )
     ```

2. **Main KKT Assembler** (2 hours)
   - File: `src/kkt/assemble.py`
   - Function: `assemble_kkt_system(model_ir, gradient, J_eq, J_ineq) -> KKTSystem`
   - Orchestrates all builders:
     ```python
     def assemble_kkt_system(model_ir, gradient, J_eq, J_ineq):
         # Step 1: Partition constraints
         eq, ineq, bounds_lo, bounds_up = partition_constraints(model_ir)
         
         # Step 2: Create multiplier definitions
         multipliers_eq = create_eq_multipliers(eq)
         multipliers_ineq = create_ineq_multipliers(ineq)
         multipliers_bounds = create_bound_multipliers(bounds_lo, bounds_up)
         
         # Step 3: Build KKT system
         kkt = KKTSystem(...)
         
         # Step 4: Build stationarity
         kkt.stationarity = build_stationarity_equations(kkt)
         
         # Step 5: Build complementarity
         kkt.complementarity_ineq, kkt.complementarity_bounds = \
             build_complementarity_pairs(kkt)
         
         return kkt
     ```

3. **End-to-End KKT Test** (2 hours)
   - File: `tests/integration/kkt/test_kkt_full.py`
   - Test full assembly on all 5 examples:
     - simple_nlp.gms
     - bounds_nlp.gms
     - indexed_balance.gms
     - nonlinear_mix.gms
     - scalar_nlp.gms
   - Verify:
     - Correct number of stationarity equations
     - Correct number of multipliers
     - Correct complementarity pairs
     - Hand-check one example (simple_nlp) completely

4. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Implement `test_kkt_assembler_smoke()` (remove @skip)
   - Verify basic KKT assembly doesn't crash

**Deliverables:**
- `src/kkt/complementarity.py` - Complementarity builder
- `src/kkt/assemble.py` - Main KKT assembler
- `tests/integration/kkt/test_kkt_full.py` - Full integration tests (~12 tests)
- `tests/e2e/test_smoke.py` - Updated smoke tests (5 tests total)

**Acceptance Criteria:**
- [ ] KKT system assembled for all 5 examples
- [ ] Stationarity + complementarity equations count matches theory
- [ ] Integration tests pass (12/12)
- [ ] Smoke tests pass (5/5)
- [ ] Manual verification: simple_nlp KKT matches hand calculation
- [ ] No regressions

**Follow-On Items (After Day's Tasks):**

**PREP_PLAN Task 7: Add Integration Risk Sections** - Complete this evening (2 hours)
- Review Days 4-10 plan
- Add "Integration Risks" section to each remaining day
- Document Sprint 1/2 dependencies
- Add mitigation strategies (diagnostics, early tests)
- Update PLAN_ORIGINAL.md with risk sections

---

### Day 4: GAMS Emitter - Templates & Structure

**Goal:** Create GAMS code generation templates and emit basic structure

**Integration Risks:**

**Sprint 1 Dependencies:**
- Assumption: ModelIR.variables contains all variable definitions with correct domains
- Risk: Variable domain information incomplete or incorrect
- Mitigation: Add diagnostic on Day 4 morning to verify all variables have domains

**Sprint 2 Dependencies:**  
- Assumption: GradientVector.index_mapping provides correct variable instance enumeration
- Risk: Index mapping doesn't match KKT system expectations
- Mitigation: Add assertion `len(kkt.stationarity) == gradient.num_cols`

**Within-Sprint Dependencies:**
- Assumption: Day 3 KKT system has all required fields populated
- Risk: Missing multipliers or equations
- Mitigation: Run smoke test before starting Day 4 work

**Tasks:**

1. **Design GAMS Template Structure** (2 hours)
   - File: `src/emit/templates.py`
   - Template functions:
     ```python
     def emit_sets(kkt: KKTSystem) -> str:
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

2. **Implement Sets Emission** (1.5 hours)
   - Extract unique index sets from:
     - Original model sets
     - Multiplier domains
     - Equation domains
   - Example output:
     ```gams
     Sets
         i /i1, i2, i3/
         eq_rows /eq1, eq2/
         ineq_rows /g1, g2, g3/
     ;
     ```

3. **Implement Variables Emission** (1.5 hours)
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

4. **Test Template Generation** (2 hours)
   - File: `tests/unit/emit/test_templates.py`
   - Test each template function separately
   - Verify GAMS syntax correctness
   - Test with simple_nlp and bounds_nlp

**Deliverables:**
- `src/emit/templates.py` - Template functions
- `tests/unit/emit/test_templates.py` - Unit tests (~15 tests)

**Acceptance Criteria:**
- [ ] All template functions implemented
- [ ] Generated Sets/Variables blocks syntactically correct
- [ ] Unit tests pass (15/15)
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
   - Handle all AST node types:
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
   - Test operator precedence
   - Test nested expressions
   - Verify power operator (Issue #25 check)

**Deliverables:**
- `src/emit/expr_to_gams.py` - AST → GAMS converter
- `src/emit/equations.py` - Equation emission
- `tests/unit/emit/test_expr_to_gams.py` - Expression tests (~20 tests)
- `tests/unit/emit/test_equations.py` - Equation tests (~10 tests)

**Acceptance Criteria:**
- [ ] All AST nodes convert to valid GAMS syntax
- [ ] Operator precedence correct (tested with complex expressions)
- [ ] Equation definitions emit correctly
- [ ] Unit tests pass (30/30)
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

1. **Implement Model MCP Emission** (3 hours)
   - File: `src/emit/model.py`
   - Function: `emit_model_mcp(kkt: KKTSystem) -> str`
   - Model MCP syntax:
     ```gams
     Model mcp_model /
         stat_x.x
         stat_y.y
         comp_g1.lam_g1
         comp_g2.lam_g2
         eq_h1.nu_h1
         bound_lo_x.piL_x
         bound_up_x.piU_x
     /;
     ```
   - Pairing rules:
     - Stationarity equations paired with primal variables
     - Complementarity equations paired with multipliers
     - Equality equations paired with free multipliers (no .LO)

2. **Implement Solve Statement** (1 hour)
   - Function: `emit_solve(kkt: KKTSystem) -> str`
   - Output:
     ```gams
     Solve mcp_model using MCP;
     ```
   - Optional: Add display statements for debugging

3. **Main Emitter Orchestration** (2 hours)
   - File: `src/emit/emit_gams.py`
   - Function: `emit_gams_mcp(kkt: KKTSystem) -> str`
   - Combine all pieces:
     ```python
     def emit_gams_mcp(kkt: KKTSystem, options: dict = None) -> str:
         sections = []
         
         # Header comment
         sections.append("* Generated by nlp2mcp")
         sections.append("* KKT conditions for MCP")
         sections.append("")
         
         # Sets
         sections.append(emit_sets(kkt))
         sections.append("")
         
         # Variables
         sections.append(emit_variables(kkt))
         sections.append("")
         
         # Equations declaration
         sections.append(emit_equations(kkt))
         sections.append("")
         
         # Equation definitions
         sections.append(emit_equation_definitions(kkt))
         sections.append("")
         
         # Model
         sections.append(emit_model_mcp(kkt))
         sections.append("")
         
         # Solve
         sections.append(emit_solve(kkt))
         
         return '\n'.join(sections)
     ```

4. **Integration Test** (1 hour)
   - File: `tests/integration/emit/test_emit_full.py`
   - Test full emission on simple_nlp
   - Verify generated GAMS is syntactically valid
   - Manually inspect output

5. **Update Smoke Test** (30 min)
   - File: `tests/e2e/test_smoke.py`
   - Implement `test_gams_emitter_smoke()` (remove @skip)
   - Verify full pipeline doesn't crash

**Deliverables:**
- `src/emit/model.py` - Model MCP emission
- `src/emit/emit_gams.py` - Main emitter
- `tests/integration/emit/test_emit_full.py` - Integration tests (~8 tests)
- `tests/e2e/test_smoke.py` - Updated smoke tests (6 tests total)

**Acceptance Criteria:**
- [ ] Model MCP emitted with correct complementarity pairs
- [ ] Full GAMS code generated for simple_nlp
- [ ] Generated code is syntactically valid (manual inspection)
- [ ] Integration tests pass (8/8)
- [ ] Smoke tests pass (6/6)
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
     def main(input_file, output, verbose, validate, comments):
         # Load and parse
         model = parse_model_file(input_file)
         normalize_model(model)
         
         # Compute derivatives
         gradient = compute_objective_gradient(model)
         J_eq, J_ineq = compute_constraint_jacobian(model)
         
         # Assemble KKT
         kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
         
         # Emit GAMS
         gams_code = emit_gams_mcp(kkt, options={'comments': comments})
         
         # Write output
         if output:
             Path(output).write_text(gams_code)
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
   - Test options (--verbose, --comments)

**Deliverables:**
- `src/cli.py` - Command-line interface
- `tests/integration/test_cli.py` - CLI tests (~10 tests)
- Mid-sprint checkpoint report (in PR comment or doc)

**Acceptance Criteria:**
- [ ] Mid-sprint checkpoint completed
- [ ] All tests passing (expect ~150 total)
- [ ] CLI works: `nlp2mcp examples/simple_nlp.gms -o out.gms`
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

1. **Generate Golden Reference Files** (2 hours)
   - For each of 5 example models, manually:
     - Run pipeline: `nlp2mcp examples/simple_nlp.gms -o golden/simple_nlp_mcp.gms`
     - Manually review and verify correctness
     - Hand-check KKT equations match theory
     - Mark as golden reference
   - Files:
     - `tests/golden/simple_nlp_mcp.gms`
     - `tests/golden/bounds_nlp_mcp.gms`
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

4. **Determinism Check** (1 hour)
   - Run each example 5 times
   - Verify output is identical each time
   - Fix any non-determinism (sort dict keys, etc.)

**Deliverables:**
- `tests/golden/` - Golden reference files (5 files)
- `tests/e2e/test_golden.py` - Golden tests (5 tests)

**Acceptance Criteria:**
- [ ] All 5 golden reference files generated and verified
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

2. **Document KKT Assembly** (2 hours)
   - File: `docs/kkt/KKT_ASSEMBLY.md`
   - Mathematical notation for KKT conditions
   - Explain stationarity construction
   - Explain complementarity conditions
   - Document multiplier naming conventions

3. **Document GAMS Emission** (2 hours)
   - File: `docs/emit/GAMS_EMISSION.md`
   - Template examples
   - AST → GAMS conversion rules
   - Model MCP pairing rules
   - Sign conventions

4. **Update README** (1 hour)
   - Add usage examples
   - Document CLI options
   - Show before/after example
   - Link to documentation

**Deliverables:**
- `src/validation/gams_check.py` - Optional GAMS validation
- `docs/kkt/KKT_ASSEMBLY.md` - KKT documentation
- `docs/emit/GAMS_EMISSION.md` - Emission documentation
- Updated `README.md`

**Acceptance Criteria:**
- [ ] GAMS validation implemented (optional feature)
- [ ] KKT assembly fully documented with math notation
- [ ] GAMS emission fully documented with examples
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

1. **Comprehensive Testing** (2 hours)
   - Run full test suite
   - Run all 5 examples through CLI
   - Test edge cases:
     - Models with only equalities
     - Models with only inequalities
     - Models with no bounds
     - Scalar models (no indexing)
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

3. **Integration Test Coverage** (2 hours)
   - Review test coverage:
     ```bash
     pytest --cov=src tests/
     ```
   - Add tests for uncovered code paths
   - Target: >90% coverage for new Sprint 3 code

4. **Final Validation** (1 hour)
   - Verify all success metrics achieved
   - Run smoke tests one final time
   - Verify API contract tests still pass
   - Verify no Sprint 1/2 regressions

5. **Sprint Wrap-Up** (1 hour)
   - Create Sprint 3 summary document
   - Document lessons learned
   - Identify items for Sprint 4
   - Celebrate! 🎉

**Deliverables:**
- All tests passing
- Code coverage >90% for Sprint 3 code
- Sprint 3 summary document
- Clean, polished codebase

**Acceptance Criteria:**
- [ ] All 403+ tests pass
- [ ] All 5 examples convert successfully
- [ ] Generated MCP files compile in GAMS (if GAMS available)
- [ ] Golden tests pass (5/5)
- [ ] CLI works correctly
- [ ] Code quality checks pass
- [ ] Documentation complete
- [ ] Sprint 3 success metrics achieved

---

## Sprint 3 Success Criteria Summary

### Functional Requirements ✅

- [ ] **KKT Assembler**: Converts derivatives to KKT system
  - Stationarity equations for all variables
  - Complementarity conditions for inequalities
  - Multiplier variables created correctly
  - Bounds handled properly

- [ ] **GAMS Emitter**: Generates valid GAMS MCP code
  - Sets, Variables, Equations blocks
  - Equation definitions with correct syntax
  - Model MCP with complementarity pairs
  - Solve statement

- [ ] **CLI**: `nlp2mcp` command works
  - Converts all 5 example models
  - Options (--output, --verbose, --validate) work
  - Error messages are clear

- [ ] **Golden Tests**: Reference outputs validated
  - 5 golden reference files
  - All golden tests pass
  - Deterministic output

### Quality Requirements ✅

- [ ] **Test Coverage**:
  - Unit tests: ~150 total (50 new)
  - Integration tests: ~50 total (15 new)
  - E2E tests: ~20 total (5 new)
  - Total: 220+ tests passing

- [ ] **Code Quality**:
  - Type checking passes (`mypy src/`)
  - Linting passes (`ruff check`)
  - Formatting passes (`ruff format`)
  - Coverage >90% for Sprint 3 code

- [ ] **Documentation**:
  - KKT assembly documented
  - GAMS emission documented
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

---

## Risk Management

### High-Priority Risks

**Risk 1: GAMS Syntax Correctness**
- **Impact:** Generated code doesn't compile in GAMS
- **Likelihood:** Medium
- **Mitigation:**
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
- **Contingency:** Reject unsupported expressions with clear error

**Risk 6: Sprint Scope Creep**
- **Impact:** Don't finish core features by Day 10
- **Likelihood:** Low
- **Mitigation:**
  - Strict focus on 5 example models only
  - Mid-sprint checkpoint on Day 7
  - Optional features clearly marked
- **Contingency:** Move optional features to Sprint 4

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
2. **bounds_nlp.gms** - Variable bounds handling (Issue #24 regression test)
3. **indexed_balance.gms** - Balance equations with indexing
4. **nonlinear_mix.gms** - Mixed nonlinear functions, power operator
5. **scalar_nlp.gms** - Simple scalar optimization (no indexing)

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
