# Sprint 4 Plan: Feature Expansion + Robustness

**Sprint Duration:** 10 days (Days 1-10)
**Sprint Goal:** Broaden language coverage, improve numerics, and add quality-of-life features
**Status:** 🔄 IN PROGRESS
**Created:** 2025-11-01

---

## Overview

Sprint 4 builds on the solid foundation of Sprints 1-3 to add critical GAMS features and improve model robustness. This sprint focuses on:

1. **Language Features:** `$include` support, `Table` data blocks, fixed variables (`x.fx`)
2. **Non-smooth Functions:** `min/max` reformulation, `abs(x)` handling
3. **Numerics:** Scaling heuristics for better solver performance
4. **Diagnostics:** Model statistics and Jacobian pattern dumps

**Key Process Improvements from Sprint 3:**
- Proactive Known Unknowns list (prevent Issue #47-style late discoveries)
- Formal checkpoints on Days 3, 6, 8 (catch issues early)
- PATH solver validation environment (test with actual solver)
- Edge case testing matrix (comprehensive coverage)

---

## Success Metrics

### Functional Goals
- [ ] `$include` directive works (nested, circular detection, relative paths)
- [ ] `Table` data blocks parse correctly (2D, sparse, with descriptive text)
- [ ] Fixed variables (`x.fx`) handled in KKT and MCP emission
- [ ] `min/max` reformulated to valid MCP with auxiliary variables
- [ ] `abs(x)` either rejected or smoothed (user choice via flag)
- [ ] Scaling applied with configurable algorithm (Curtis-Reid default)
- [ ] Diagnostics: model stats (rows/cols/nonzeros) and Jacobian dumps

### Quality Metrics
- [ ] All existing tests pass (602+ tests, no regressions)
- [ ] New test coverage >= 85% for Sprint 4 code
- [ ] All Known Unknowns resolved by Day 6
- [ ] GAMS syntax validation passes for all test cases
- [ ] PATH solver successfully solves reformulated MCPs

### Integration Metrics
- [ ] No Sprint 1/2/3 API breakage
- [ ] Generated MCP files compile in GAMS
- [ ] Golden files updated and passing
- [ ] CLI supports new features with appropriate flags

---

## Day-by-Day Plan

### Day 1: `$include` and Preprocessing

#### Goals
- Implement `$include` directive support
- Handle nested includes and circular detection
- Integrate preprocessor into parse pipeline

#### Main Tasks

**Task 1: Implement `preprocess_includes()` function with recursion** (Est: 3h)
- Create preprocessor.py module with include resolution
- Handle relative/absolute paths
- Build include dependency graph

**Required Unknowns:**
- **Unknown 1.1: `$include` syntax and semantics** - COMPLETE
  - **Findings:** GAMS `$include` uses simple string substitution without macro expansion. Supports relative and absolute paths with syntax `$include filename.inc` or `$include "filename with spaces.inc"`.
  - **Key Architecture:** Preprocessor runs before parser, maintains include stack for error reporting, detects circular includes.
  - **Summary:** Simple textual file insertion confirmed via GAMS documentation and test examples.

**Task 2: Add circular include detection with clear error messages** (Est: 1.5h)
- Implement include stack tracking
- Detect cycles and report full chain
- Provide helpful error messages

**Required Unknowns:**
- **Unknown 1.4: Nested `$include` handling** - COMPLETE
  - **Findings:** GAMS allows arbitrary nesting depth (limited only by system resources). Best practice is 3-5 levels max. Tested 10-level nesting successfully.
  - **Key Architecture:** Track include depth, configurable limit with default of 10, clear error messages for circular includes with full chain shown.
  - **Summary:** Use depth tracking with configurable limit (default 100 levels), circular detection works correctly.

**Task 3: Integrate preprocessor into `parse_model_file()`** (Est: 1h)
- Add preprocessing step before parsing
- Ensure transparent to downstream code
- Add debug comments for include boundaries

**Required Unknowns:**
- **Unknown 6.1: $include vs ModelIR preprocessing** - COMPLETE
  - **Findings:** Preprocessing happens before parsing. ModelIR sees flat expanded source with no include-related attributes. Debug comments mark include boundaries.
  - **Key Architecture:** Clean separation: preprocess → parse → build ModelIR. No source mapping needed for current use cases.
  - **Summary:** ModelIR structure unaffected - sees expanded source as if in one file.

**Task 4: Add relative path resolution (relative to containing file)** (Est: 1.5h)
- Resolve paths relative to file containing $include
- Handle parent directory (..) references
- Support absolute paths

**Required Unknowns:**
- **Unknown 1.5: Relative path resolution** - COMPLETE
  - **Findings:** Paths resolved relative to directory of file containing $include (NOT current working directory). Parent directory (..) navigation works correctly.
  - **Key Architecture:** Uses `file_path.parent / included_filename` pattern. Absolute paths supported.
  - **Summary:** Path resolution matches GAMS behavior - relative to containing file, not CWD.

**Task 5: Write comprehensive tests (nested, circular, missing files)** (Est: 2h)
- Test simple includes
- Test nested includes (3+ levels)
- Test circular detection
- Test missing file errors
- Test relative vs absolute paths

#### Deliverables
- `src/ir/preprocessor.py` with `preprocess_includes()` function
- Integration into parser (transparent to downstream code)
- 15+ tests covering all edge cases
- Documentation in docstrings

#### Acceptance Criteria
- [ ] Simple `$include` works (file inserted at directive location)
- [ ] Nested includes work (3+ levels deep)
- [ ] Circular includes detected with full chain shown in error
- [ ] Missing files produce clear error with source location
- [ ] Relative paths resolve correctly (to containing file, not CWD)
- [ ] All tests pass (including existing 602 tests)

#### Integration Risks
- **Risk 1:** Parser grammar may need updates if `$include` has special syntax
  - *Mitigation:* Preprocess before parsing (text substitution)
- **Risk 2:** Line numbers in error messages may be incorrect after include expansion
  - *Mitigation:* Add source mapping comments (future enhancement, not Sprint 4)

---

### Day 2: `Table` Data Blocks

#### Goals
- Parse `Table` syntax for 2D parameter data
- Handle sparse tables (empty cells → 0)
- Integrate into parameter data structures

#### Main Tasks

**Task 1: Extend grammar with `table_block` rule** (Est: 2h)
- Add table_block grammar rule
- Separate from params_block
- Handle table row and value tokens

**Required Unknowns:**
- **Unknown 1.2: `Table` block syntax** - COMPLETE
  - **Findings:** `Table` uses multi-line format with row/column headers. First row after declaration contains column headers. Subsequent rows have row header followed by data values. Empty cells default to zero. Strictly 2D (one row index, one column index).
  - **Key Architecture:** Uses token line/column metadata to reconstruct rows (grammar's `%ignore NEWLINE` strips newlines). Groups tokens by line number, matches values to columns by position with ±6 char tolerance.
  - **Summary:** Token metadata approach handles sparse tables without grammar changes.

**Task 2: Implement `_handle_table_block()` in parser** (Est: 3h)
- Parse table structure using token metadata
- Extract row and column headers
- Build parameter values dictionary

**Task 3: Handle sparse cells and multi-dimensional keys** (Est: 2h)
- Zero-fill empty cells
- Format multi-dimensional keys as tuples
- Handle alignment variations

**Task 4: Write tests for dense, sparse, and edge cases** (Est: 2h)
- Test simple 2D tables
- Test sparse tables with missing values
- Test tables with descriptive text
- Test table in included files

**Required Unknowns:**
- **Unknown 6.1: $include vs ModelIR preprocessing** - COMPLETE (see Day 1)
  - Tables in included files work correctly since preprocessing happens before parsing.

#### Deliverables
- Grammar extension in `src/gams/gams_grammar.lark`
- Parser handler in `src/ir/parser.py`
- 20+ tests covering table variations
- Integration with existing `ParameterDef` structure

#### Acceptance Criteria
- [ ] Simple 2D table parses correctly (row/col headers → dict keys)
- [ ] Sparse tables fill missing cells with 0.0
- [ ] Descriptive text after table name handled
- [ ] Multi-dimensional keys formatted correctly: `("i1", "j2")`
- [ ] Table integrated with existing parameter emission code
- [ ] All tests pass (including Sprint 1-3 tests)

#### Integration Risks
- **Risk 1:** Grammar `%ignore NEWLINE` may conflict with table row parsing
  - *Mitigation:* Use token metadata (line/column) to reconstruct rows
- **Risk 2:** Table data may conflict with later parameter assignments
  - *Mitigation:* Document precedence rules (later assignment wins)

**Checkpoint** (Day 3):
- Checkpoint 1 review (Est: 1h) - Use template from docs/process/CHECKPOINT_TEMPLATES.md
  - All features scaffolded (✓)
  - Known Unknowns 1.1, 1.2, 1.4, 1.5, 6.1 all COMPLETE (✓)
  - Test coverage >= 70% (✓)
  - All existing tests pass (✓)

---

### Day 3: `min/max` Reformulation - Part 1 (Infrastructure)

#### Goals
- Design auxiliary variable reformulation for `min/max`
- Implement detection in AST traversal
- Create auxiliary variable generation framework

#### Main Tasks

**Task 1: Design epigraph reformulation (z = min(x,y) → z≤x, z≤y with λ)** (Est: 2h)
- Document epigraph reformulation approach
- Design constraint structure
- Plan complementarity pairing

**Required Unknowns:**
- **Unknown 2.1: min() reformulation** - COMPLETE
  - **Findings:** Epigraph reformulation using complementarity is standard: `min(x,y)` becomes `x - z >= 0 ⊥ λ_x >= 0` and `y - z >= 0 ⊥ λ_y >= 0`. Stationarity for z: `∂obj/∂z - λ_x - λ_y = 0`.
  - **Key Architecture:** Multi-argument min scales linearly (n args → n+1 vars, n+1 equations). Nested min should be flattened before reformulation for efficiency.
  - **Summary:** Epigraph form confirmed as correct, standard approach in complementarity literature.

- **Unknown 2.2: max() reformulation** - COMPLETE
  - **Findings:** Dual of min using reversed inequality direction: `max(x,y)` becomes `x - z <= 0 ⊥ λ_x >= 0` and `y - z <= 0 ⊥ λ_y >= 0`. Use `=l=` constraints in GAMS (opposite of min's `=g=`).
  - **Key Architecture:** Direct implementation recommended over `-min(-x,-y)` for efficiency (fewer variables/operations). Symmetric to min implementation.
  - **Summary:** Direct epigraph reformulation with opposite constraint direction.

**Task 2: Add AST traversal to detect `min/max` calls** (Est: 2h)
- Traverse equation ASTs to find function calls
- Identify min/max calls
- Extract arguments for reformulation

**Task 3: Implement auxiliary variable name generation (collision-free)** (Est: 2h)
- Create AuxiliaryVariableManager class
- Generate unique names based on context
- Detect and avoid collisions with user variables

**Required Unknowns:**
- **Unknown 4.2: Auxiliary variable naming** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 3
  - **Planned approach:** Context-based naming (`aux_min_<equation_name>`) with counter for duplicates
  - **Need to verify:** Collision detection works, indexed equation handling, GAMS name validity

**Task 4: Create test framework for reformulation** (Est: 2h)
- Write detection tests
- Write naming tests
- Write flattening tests for nested min/max

#### Deliverables
- Design document for `min/max` reformulation (inline in code)
- `src/kkt/reformulation.py` module (infrastructure only)
- Auxiliary variable naming scheme: `aux_min_<context>_<N>`
- 10+ tests for detection and naming

#### Acceptance Criteria
- [ ] `min(x, y)` calls detected in equation ASTs
- [ ] Auxiliary variable names generated without collisions
- [ ] Multi-argument `min(x, y, z)` supported (design level)
- [ ] Nested `min(min(x, y), z)` flattened to `min(x, y, z)`
- [ ] All existing tests pass (no regressions)

#### Integration Risks
- **Risk 1:** KKT assembly may need refactoring to add auxiliary constraints
  - *Mitigation:* Add new constraint type, keep existing code paths unchanged
- **Risk 2:** Variable ordering in Jacobian may break with new auxiliary vars
  - *Mitigation:* Extend IndexMapping to handle auxiliary variables

**Checkpoint** (Day 3 - End of Day):
- Checkpoint 1 review (Est: 1h)
  - Review all Day 1-3 deliverables
  - Verify Known Unknowns 1.1, 1.2, 1.4, 1.5, 2.1, 2.2, 6.1 COMPLETE
  - Note Unknown 4.2 needs verification during implementation
  - Check test coverage >= 70%
  - Confirm no regressions

---

### Day 4: `min/max` Reformulation - Part 2 (Implementation)

#### Goals
- Implement full `min/max` reformulation in KKT assembly
- Generate complementarity pairs for auxiliary constraints
- Integrate with stationarity equations

#### Main Tasks

**Task 1: Implement `reformulate_min()` function** (Est: 3h)
- Create auxiliary variable and multipliers
- Generate complementarity constraints
- Handle multi-argument case
- Flatten nested min calls

**Task 2: Implement `reformulate_max()` function** (Est: 2h)
- Implement symmetric to min with reversed inequalities
- Reuse auxiliary variable infrastructure
- Handle multi-argument case

**Task 3: Add auxiliary constraints to KKT system** (Est: 2h)
- Extend KKT data structures for auxiliary constraints
- Add complementarity pairs
- Maintain equation-variable count balance

**Required Unknowns:**
- **Unknown 4.3: Auxiliary constraints in Model declaration** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 4
  - **Planned approach:** Add auxiliary constraints to Model MCP declaration like regular constraints
  - **Need to verify:** GAMS compilation works, equation-variable pairing correct, no special handling needed

- **Unknown 6.4: Auxiliary vars and IndexMapping** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 4
  - **Critical:** IndexMapping must be created AFTER reformulations to include auxiliary variables
  - **Need to verify:** Gradient/Jacobian columns align correctly, no index misalignment errors

**Task 4: Update stationarity to include auxiliary multipliers** (Est: 2h)
- Add multiplier terms to stationarity equations
- Verify sign conventions
- Test complementarity conditions

#### Deliverables
- Complete `src/kkt/reformulation.py` module
- Integration with `assemble_kkt_system()`
- 25+ tests for reformulation correctness
- Example: `min(x, y)` → KKT with `z_min`, `λ_x`, `λ_y`

#### Acceptance Criteria
- [ ] `min(x, y)` generates 2 auxiliary constraints with multipliers
- [ ] `max(x, y)` generates 2 auxiliary constraints (opposite direction)
- [ ] Multi-argument `min(a, b, c)` generates 3 constraints
- [ ] Stationarity includes `∂f/∂z_min - λ_x - λ_y = 0`
- [ ] Complementarity pairs: `(x - z_min) ⊥ λ_x`, `(y - z_min) ⊥ λ_y`
- [ ] All tests pass (including reformulation-specific tests)

#### Integration Risks
- **Risk 1:** Jacobian computation may not handle auxiliary variables
  - *Mitigation:* Auxiliary constraints are simple (linear in aux var)
- **Risk 2:** GAMS emission may not declare auxiliary variables/equations
  - *Mitigation:* Extend emission templates to include auxiliary vars

---

### Day 5: `abs(x)` Handling and Fixed Variables (`x.fx`)

#### Goals
- Implement `abs(x)` handling (reject by default, smooth optional)
- Add fixed variable support (`x.fx = c`)
- Integrate both into KKT system

#### Main Tasks

**Task 1: Implement `abs(x)` detection and rejection** (Est: 1.5h)
- Detect abs() calls during differentiation
- Raise clear error by default
- Suggest --smooth-abs flag

**Required Unknowns:**
- **Unknown 2.3: abs() smoothing strategy** - COMPLETE
  - **Findings:** Reject by default with optional smoothing via `--smooth-abs` flag. Soft-abs approximation `sqrt(x^2 + ε)` with default ε=1e-6 provides excellent accuracy (max error 0.001 at x=0, <0.0001% for |x|≥1).
  - **Key Architecture:** Derivative is `x / sqrt(x^2 + ε)` (continuous everywhere). Auto-convert conceptually to `max(x, -x)` for consistency. Do NOT implement MPEC approach (too complex, poor solver compatibility).
  - **Summary:** Soft-abs approximation recommended with ε=1e-6 default.

**Task 2: Add `--smooth-abs` flag with soft-abs approximation** (Est: 2.5h)
- Implement CLI flags --smooth-abs and --smooth-abs-epsilon
- Add differentiation rule for smooth abs
- Test accuracy and numerical stability

**Task 3: Parse `x.fx` syntax and create equality constraints** (Est: 2h)
- Extend parser to recognize .fx attribute
- Create equality constraints for fixed variables
- Handle both scalar and indexed variables

**Required Unknowns:**
- **Unknown 1.3: Fixed variable semantics** - COMPLETE
  - **Findings:** `.fx` attribute sets both `.lo` and `.up` to same value, effectively fixing variable. In MCP context, treated as equality constraint paired with free multiplier (not bound multipliers).
  - **Key Architecture:** Treat .fx equalities like any other equality constraint. Normalization creates `x - fx_value = 0` with `Rel.EQ`. Stores in `normalized_bounds` dictionary and adds to `equalities` list.
  - **Summary:** Option A implemented - treat as equality constraints paired with free multipliers (e.g., x_fx.nu_x_fx).

**Task 4: Integrate fixed vars into KKT assembly (no piL/piU)** (Est: 2h)
- Skip stationarity equations for fixed variables
- Add fixing constraints to KKT system
- Pair with variable (not multiplier) in MCP

**Required Unknowns:**
- **Unknown 4.4: Emit fixed variables in MCP** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 5
  - **Approach:** Based on Unknown 1.3 findings, use equality constraint approach
  - **Need to verify:** MCP emission works, GAMS compilation succeeds, PATH solver handles correctly

- **Unknown 6.2: Fixed vars in KKT assembly** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 5
  - **Approach:** No stationarity equation for fixed vars, add fixing constraint instead
  - **Need to verify:** KKT dimension correct (equations = variables), no piL/piU multipliers created

**Task 5: Write tests for both features** (Est: 2h)
- Test abs() rejection and smoothing
- Test .fx parsing and normalization
- Test KKT integration
- Test MCP emission

#### Deliverables
- `abs(x)` handling in differentiation engine
- CLI flag: `--smooth-abs` with `--smooth-abs-epsilon` (default 1e-6)
- Fixed variable parsing in `src/ir/parser.py`
- KKT integration: `x.fx = c` → equality constraint `x - c = 0`
- 20+ tests (10 for abs, 10 for fixed vars)

#### Acceptance Criteria
- [ ] `abs(x)` without flag raises clear error with suggestion
- [ ] `abs(x)` with `--smooth-abs` uses `sqrt(x^2 + ε)` approximation
- [ ] Derivative of smooth abs is `x / sqrt(x^2 + ε)`
- [ ] `x.fx = 10` parsed into `BoundsDef(fx=10.0)`
- [ ] Fixed vars create equality constraint (no bound multipliers)
- [ ] MCP emission pairs fixed var equality with free multiplier
- [ ] All tests pass

#### Integration Risks
- **Risk 1:** Smooth abs may cause numerical issues near x=0
  - *Mitigation:* Document limitations, allow user to tune epsilon
- **Risk 2:** Fixed vars may conflict with user-defined equality constraints
  - *Mitigation:* Use unique naming: `eq_fix_<varname>`

---

### Day 6: Scaling Implementation

#### Goals
- Implement Curtis-Reid scaling algorithm
- Add CLI flags for scaling control
- Apply scaling to Jacobian before KKT assembly

#### Main Tasks

**Task 1: Implement Curtis-Reid row/column scaling** (Est: 3h)
- Implement iterative row/column norm balancing
- Compute scaling factors from Jacobian
- Handle sparse matrices efficiently

**Required Unknowns:**
- **Unknown 3.1: Scaling algorithm selection** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 6
  - **Planned approach:** Curtis-Reid geometric mean scaling (iterative row/col norm balancing)
  - **Need to verify:** Algorithm implementation correct, converges properly, improves conditioning

- **Unknown 3.2: Scaling application point** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 6
  - **Decision needed:** Scale original NLP vs. scale KKT system
  - **Need to verify:** Which approach gives better PATH solver performance

**Task 2: Add `--scale` flag (none/auto, default: none)** (Est: 1.5h)
- Add CLI flag for scaling control
- Default to no scaling (opt-in)
- Document scaling behavior

**Required Unknowns:**
- **Unknown 6.3: Scaling impact on tests** - INCOMPLETE
  - **Status:** TO BE VERIFIED before Day 6
  - **Critical:** Existing tests must pass without --scale flag
  - **Need to verify:** Scaled and unscaled give equivalent solutions, no test breakage

**Task 3: Compute scaling factors from Jacobian** (Est: 2h)
- Extract Jacobian structure
- Apply Curtis-Reid algorithm
- Store scaling factors

**Task 4: Apply scaling to equations and variables** (Est: 1.5h)
- Scale equations by row factors
- Scale variables by column factors
- Maintain mathematical equivalence

**Task 5: Write tests and verify no semantic changes** (Est: 2h)
- Test scaling is deterministic
- Test scaled vs unscaled solutions match
- Test existing tests still pass

#### Deliverables
- `src/kkt/scaling.py` module with Curtis-Reid algorithm
- CLI flags: `--scale none|auto`
- Scaling factors stored in KKT system
- 15+ tests for scaling correctness
- Verification that scaling doesn't change KKT semantics

#### Acceptance Criteria
- [ ] Curtis-Reid scaling implemented (iterative row/col norm balancing)
- [ ] Scaling factors computed from symbolic Jacobian
- [ ] Scaled Jacobian has row/col norms ≈ 1
- [ ] Scaling applied transparently (no user intervention needed with auto)
- [ ] `--scale none` skips scaling (default)
- [ ] `--scale auto` applies Curtis-Reid
- [ ] Existing tests pass with `--scale none`
- [ ] Tests with scaling verify semantic preservation

#### Integration Risks
- **Risk 1:** Scaling may expose bugs in Jacobian computation
  - *Mitigation:* Verify Jacobian correctness before scaling
- **Risk 2:** Scaled vs unscaled solutions may differ numerically
  - *Mitigation:* Document that scaling is for solver robustness, not semantics

**Checkpoint** (Day 6 - End of Day):
- Checkpoint 2 review (Est: 1h)
  - All features >= 80% implemented (✓)
  - Known Unknowns 1.1-1.3, 2.1-2.3, 6.1 COMPLETE (✓)
  - Known Unknowns 3.1, 3.2, 4.2-4.4, 6.2-6.4 verified during Days 3-6 (✓)
  - Test coverage >= 85% (✓)
  - No critical bugs (✓)

---

### Day 7: Diagnostics and Model Statistics

#### Goals
- Add model statistics reporting (rows/cols/nonzeros)
- Implement Jacobian pattern dump (Matrix Market format)
- Add verbosity controls for diagnostics

#### Main Tasks

**Task 1: Compute model statistics from KKT system** (Est: 2h)
- Count equations, variables, nonzeros
- Break down by type (stationarity, complementarity, bounds)
- Format for display

**Task 2: Implement Matrix Market Jacobian export** (Est: 3h)
- Export Jacobian in Matrix Market format
- Handle sparse structure
- Validate format (SciPy/MATLAB compatible)

**Task 3: Add CLI flags for diagnostics (--stats, --dump-jacobian)** (Est: 1.5h)
- Add --stats flag for statistics output
- Add --dump-jacobian <file> flag
- Integrate into main workflow

**Task 4: Write tests for diagnostic output** (Est: 1.5h)
- Test statistics computation
- Test Matrix Market export
- Verify diagnostics don't affect MCP generation

#### Deliverables
- `src/diagnostics/` module with stats and export functions
- CLI flags: `--stats`, `--dump-jacobian <file>`
- Matrix Market format Jacobian export
- 10+ tests for diagnostic features

#### Acceptance Criteria
- [ ] `--stats` prints: # equations, # variables, # nonzeros
- [ ] Stats include breakdown: stationarity, complementarity, bounds
- [ ] `--dump-jacobian jac.mtx` exports Jacobian in Matrix Market format
- [ ] Matrix Market file valid (can be loaded by SciPy/MATLAB)
- [ ] Diagnostics don't affect MCP generation
- [ ] All tests pass

#### Integration Risks
- **Risk 1:** Matrix Market export may be slow for large models
  - *Mitigation:* Document as debug feature, not production
- **Risk 2:** Statistics may be incorrect for reformulated models
  - *Mitigation:* Count after reformulation (auxiliary vars included)

#### Follow-On Items
**PREP PLAN Task 3** (PATH solver validation - available now):
- Validate generated MCPs with PATH solver
- Test reformulated `min/max` and `abs` with PATH
- Verify solver convergence and solution quality
- Document any PATH-specific issues or required options

**Known Unknown Research:**
- Unknown 2.4: PATH compatibility for non-smooth reformulations
- Unknown 5.1: PATH behavior on nonlinear MCPs

---

### Day 8: PATH Solver Validation and Testing

#### Goals
- Validate all generated MCPs with PATH solver
- Test reformulated features (`min/max`, `abs`, fixed vars)
- Identify and document any PATH-specific issues

#### Main Tasks

**Task 1: Set up PATH solver test harness** (Est: 2h)
- Create PATH validation framework
- Set up test infrastructure
- Configure solver options

**Required Unknowns:**
- **Unknown 5.2: Recommend PATH options** - INCOMPLETE
  - **Status:** TO BE VERIFIED during Day 8
  - **Planned approach:** Document default options, test problem-specific tuning
  - **Need to verify:** Which options improve convergence, recommended defaults for nlp2mcp

**Task 2: Run all golden files through PATH** (Est: 2h)
- Validate existing golden files
- Verify no regressions
- Document solve status

**Task 3: Test `min/max` reformulations with PATH** (Est: 2h)
- Test simple 2-argument min/max
- Test multi-argument cases
- Test nested cases (flattened)

**Required Unknowns:**
- **Unknown 2.4: PATH compatibility for non-smooth reformulations** - INCOMPLETE
  - **Status:** TO BE VERIFIED during Day 8
  - **Critical:** Verify PATH can handle min/max reformulations
  - **Need to verify:** Convergence characteristics, initial point sensitivity, solver robustness

- **Unknown 5.1: PATH behavior on nonlinear MCPs** - INCOMPLETE
  - **Status:** TO BE VERIFIED during Day 8
  - **Need to verify:** How PATH handles highly nonlinear KKT systems, when to apply scaling, when convergence fails

**Task 4: Test smooth `abs` with PATH** (Est: 1.5h)
- Test abs() with smoothing enabled
- Verify numerical stability
- Check solution accuracy

**Task 5: Document PATH solver requirements and options** (Est: 1.5h)
- Document setup instructions
- Document recommended options
- Create troubleshooting guide

**Required Unknowns:**
- **Unknown 5.3: PATH failure reporting** - INCOMPLETE
  - **Status:** TO BE VERIFIED during Day 8
  - **Need to verify:** How to parse PATH status codes, error messages, listing file output

- **Unknown 5.4: PATH initial point guidance** - INCOMPLETE
  - **Status:** TO BE VERIFIED during Day 8 (low priority)
  - **Need to verify:** Whether PATH default initialization sufficient, when user initial points needed

#### Deliverables
- PATH validation tests in `tests/validation/test_path.py`
- Documentation of PATH solver setup and usage
- List of known PATH issues/limitations
- 10+ PATH-specific tests

#### Acceptance Criteria
- [ ] All golden files solve successfully with PATH
- [ ] Reformulated `min/max` problems solve correctly
- [ ] Smooth `abs` problems solve correctly
- [ ] Fixed variable problems solve correctly
- [ ] PATH solver options documented (if needed)
- [ ] All tests pass (including PATH validation tests)

#### Integration Risks
- **Risk 1:** PATH may not be available on all systems
  - *Mitigation:* Make PATH tests conditional (skip if not found)
- **Risk 2:** PATH may fail on some reformulations
  - *Mitigation:* Document limitations, provide alternative formulations

**Checkpoint** (Day 8 - End of Day):
- Checkpoint 3 review (Est: 1h)
  - All features 100% implemented (✓)
  - All Known Unknowns resolved (✓)
  - All tests passing (✓)
  - PATH validation complete (✓)
  - Documentation complete (✓)

---

### Day 9: Integration Testing and Documentation

#### Goals
- Run comprehensive integration tests
- Update all documentation
- Regenerate golden files
- Verify all acceptance criteria

#### Main Tasks

**Task 1: Run full test suite with all features enabled** (Est: 2h)
- Run all 650+ tests
- Verify no regressions
- Check test coverage >= 85%

**Task 2: Update README.md with Sprint 4 features** (Est: 1.5h)
- Document $include support
- Document Table support
- Document min/max reformulation
- Document abs() handling
- Document fixed variables
- Document scaling and diagnostics

**Task 3: Update technical documentation** (Est: 2h)
- Update KKT_ASSEMBLY.md with reformulation details
- Update GAMS_EMISSION.md with auxiliary variable handling
- Document scaling algorithm
- Add troubleshooting guide

**Task 4: Regenerate all golden files with new features** (Est: 1.5h)
- Update golden files with new capabilities
- Add new golden files for Sprint 4 features
- Validate all golden files with GAMS

**Task 5: Write Sprint 4 summary document** (Est: 2h)
- Document what was accomplished
- Document lessons learned
- Document known limitations
- Plan Sprint 5 scope

#### Deliverables
- All 650+ tests passing
- Updated README.md with feature list
- Updated technical docs (KKT_ASSEMBLY.md, GAMS_EMISSION.md)
- New golden files with reformulations
- Sprint 4 summary document

#### Acceptance Criteria
- [ ] All tests pass (no xfail markers)
- [ ] Test coverage >= 85% for Sprint 4 code
- [ ] README.md accurate and complete
- [ ] Technical docs reflect all new features
- [ ] Golden files validate with GAMS
- [ ] All acceptance criteria from Days 1-8 met

#### Integration Risks
- **Risk 1:** Documentation may be out of sync with code
  - *Mitigation:* Review docs against actual implementation
- **Risk 2:** Golden file regeneration may reveal hidden bugs
  - *Mitigation:* Fix any issues found, retest

#### Follow-On Items
**Known Unknown Research:**
- **Unknown 4.1: Line breaking for GAMS emission** - COMPLETE
  - **Findings:** GAMS has no practical line length limit. Current nlp2mcp output (max ~158 chars) is acceptable. Line breaking is cosmetic, not functional.
  - **Summary:** No changes needed - current behavior is appropriate.

---

### Day 10: Polish, Buffer, and Sprint Wrap-Up

#### Goals
- Final quality pass (typecheck, lint, format)
- Address any remaining issues
- Create Sprint 4 retrospective
- Plan Sprint 5

#### Main Tasks
- Task: Run all quality checks (mypy, ruff, black) (Est: 1.5h)
- Task: Fix any remaining issues or technical debt (Est: 3h)
- Task: Create Sprint 4 retrospective document (Est: 2h)
- Task: Update CHANGELOG.md with Sprint 4 release (Est: 1h)
- Task: Plan Sprint 5 scope (preliminary) (Est: 1.5h)
- Task: Buffer time for unexpected issues (Est: 1h)

#### Deliverables
- All quality checks passing
- Sprint 4 retrospective (RETROSPECTIVE.md)
- Updated CHANGELOG.md
- Preliminary Sprint 5 plan
- Clean codebase ready for Sprint 5

#### Acceptance Criteria
- [ ] All 650+ tests passing
- [ ] Mypy: 0 errors
- [ ] Ruff: 0 errors
- [ ] Black: 100% formatted
- [ ] Test coverage >= 85%
- [ ] All Sprint 4 success metrics achieved
- [ ] Retrospective complete
- [ ] CHANGELOG.md updated

#### Integration Risks
- **Risk 1:** Last-minute bug discoveries
  - *Mitigation:* Buffer time allocated, can extend to Day 11 if needed
- **Risk 2:** Sprint 5 scope unclear
  - *Mitigation:* Preliminary plan only, detailed planning in Sprint 5 prep

#### Follow-On Items
**Sprint 5 Planning**:
- Review Sprint 4 lessons learned
- Identify remaining PROJECT_PLAN.md items
- Create Sprint 5 prep plan
- Schedule Sprint 5 kickoff

---

## Risk Management

### High-Priority Risks

**Risk 1: PATH Solver Not Available Until Late**
- **Impact:** Cannot validate reformulations until Day 7-8
- **Mitigation:** 
  - Test reformulation logic independently (unit tests)
  - Verify mathematical correctness via literature
  - Schedule PATH-dependent work on Days 7-8
- **Contingency:** If PATH unavailable, document limitations and defer to Sprint 5

**Risk 2: `min/max` Reformulation More Complex Than Expected**
- **Impact:** Days 3-4 may overrun
- **Mitigation:**
  - Research Known Unknowns 2.1-2.2 **COMPLETE** ✅
  - Implement simple 2-arg case first, extend to N-arg later
  - Checkpoint 1 on Day 3 will catch delays early
- **Contingency:** Descope multi-arg or nested min/max to Sprint 5

**Risk 3: Scaling Breaks Existing Tests**
- **Impact:** Day 6 may require debugging Sprint 1-3 code
- **Mitigation:**
  - Default to `--scale none` (opt-in, not default)
  - Test scaling on new examples first
  - Checkpoint 2 on Day 6 will identify issues
- **Contingency:** Make scaling experimental (behind flag) if unstable

**Risk 4: Integration Issues with Auxiliary Variables**
- **Impact:** Days 4-5 may require refactoring KKT/emit code
- **Mitigation:**
  - Design auxiliary var integration on Day 3
  - Use existing VarDef/EquationDef structures
  - Test integration incrementally
- **Contingency:** Descope nested `min/max` or limit to simple cases

### Medium-Priority Risks

**Risk 5: `Table` Parsing Grammar Conflicts**
- **Impact:** Day 2 may require grammar debugging
- **Mitigation:** Unknown 1.2 **COMPLETE** ✅ - token metadata approach verified
- **Contingency:** Support only simple tables, defer complex cases to Sprint 5

**Risk 6: Documentation Lag**
- **Impact:** Day 9 documentation may be rushed
- **Mitigation:** Document as you go, use docstrings extensively
- **Contingency:** Extend Day 10 to complete docs if needed

### Low-Priority Risks

**Risk 7: Performance Issues with Large Models**
- **Impact:** Scaling/diagnostics may be slow
- **Mitigation:** Profile if issues arise
- **Contingency:** Document as known limitation, optimize in Sprint 5

**Risk 8: Unknown Unknowns Discovered Mid-Sprint**
- **Impact:** Schedule delays
- **Mitigation:** Proactive Known Unknowns list (10/23 already COMPLETE), checkpoints on Days 3, 6, 8
- **Contingency:** Use Day 10 buffer time or extend sprint

---

## Checkpoint Schedule

### Checkpoint 1 (Day 3)
- **Focus:** Early features scaffolded, Known Unknowns verified
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/NO-GO for Days 4-6
- **Time:** 1 hour

### Checkpoint 2 (Day 6)
- **Focus:** All features >= 80% complete, integration healthy
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/NO-GO for Days 7-10, descoping if needed
- **Time:** 1 hour

### Checkpoint 3 (Day 8)
- **Focus:** Feature completeness, PATH validation, final push
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/EXTEND/NO-GO for completion
- **Time:** 1 hour

---

## Known Unknowns Schedule

Sprint 4 Known Unknowns are documented in:
- `/Users/jeff/experiments/nlp2mcp/docs/planning/EPIC_1/SPRINT_4/KNOWN_UNKNOWNS.md`
- `/Users/jeff/experiments/nlp2mcp/docs/planning/EPIC_1/SPRINT_4/KNOWN_UNKNOWNS/SCHEDULE.md`

**Verification Status (as of 2025-11-01):**

**COMPLETE (10/23):**
- ✅ Unknown 1.1: `$include` syntax and semantics
- ✅ Unknown 1.2: `Table` block syntax
- ✅ Unknown 1.3: Fixed variable semantics
- ✅ Unknown 1.4: Nested `$include` handling
- ✅ Unknown 1.5: Relative path resolution
- ✅ Unknown 2.1: min() reformulation
- ✅ Unknown 2.2: max() reformulation
- ✅ Unknown 2.3: abs() handling
- ✅ Unknown 4.1: Line breaking for GAMS emission
- ✅ Unknown 6.1: $include vs ModelIR preprocessing

**INCOMPLETE - TO BE VERIFIED (13/23):**
- 🔍 Unknown 2.4: PATH compatibility (Day 8)
- 🔍 Unknown 3.1: Scaling algorithm (Day 6)
- 🔍 Unknown 3.2: Scaling application point (Day 6)
- 🔍 Unknown 4.2: Auxiliary variable naming (Day 3-4)
- 🔍 Unknown 4.3: Auxiliary constraints in Model (Day 4)
- 🔍 Unknown 4.4: Emit fixed variables in MCP (Day 5)
- 🔍 Unknown 5.1: PATH nonlinearity handling (Day 8)
- 🔍 Unknown 5.2: PATH options (Day 8)
- 🔍 Unknown 5.3: PATH failure reporting (Day 8)
- 🔍 Unknown 5.4: PATH initial points (Day 8, low priority)
- 🔍 Unknown 6.2: Fixed vars in KKT (Day 5)
- 🔍 Unknown 6.3: Scaling impact on tests (Day 6)
- 🔍 Unknown 6.4: Auxiliary vars and IndexMapping (Day 4)

**All unknowns must be resolved or documented by Day 8.**

---

## Dependencies on Prior Sprints

### Sprint 1 Dependencies
- Parser and ModelIR structure (extended for `$include`, `Table`, `x.fx`)
- Grammar (extended for new syntax)
- AST nodes (extended for auxiliary vars)

### Sprint 2 Dependencies
- AD engine (extended for smooth `abs` derivatives)
- Jacobian computation (extended for auxiliary vars)
- Symbolic differentiation (used for scaling computation)

### Sprint 3 Dependencies
- KKT assembly (extended for reformulations, fixed vars)
- GAMS emission (extended for auxiliary vars, scaling)
- CLI (extended for new flags)
- Validation framework (extended for PATH testing)

**No breaking changes to Sprint 1-3 APIs.** All extensions are additive.

---

## Lessons Applied from Sprint 3

1. **Proactive Known Unknowns:** Created before sprint start (10/23 already COMPLETE) ✅
2. **Early Validation:** PATH setup on Day 7 (not deferred)
3. **Formal Checkpoints:** Days 3, 6, 8 with templates and decision points
4. **Test-Driven Development:** Write tests before/during implementation
5. **Incremental Integration:** Test each feature independently before combining
6. **Documentation as You Go:** Update docs daily, not just Day 9

---

## Success Criteria Summary

**Sprint 4 is successful if:**
- [ ] All 7 priority-1 features implemented (`$include`, `Table`, `min/max`, `abs`, `x.fx`, scaling, diagnostics)
- [ ] All existing tests pass (602+ with no regressions)
- [ ] New test coverage >= 85%
- [ ] All Known Unknowns resolved
- [ ] PATH validation complete (all golden files solve)
- [ ] Documentation complete and accurate
- [ ] GAMS syntax validation passes
- [ ] Checkpoints all show GO status
- [ ] No critical bugs or technical debt
- [ ] Sprint 5 ready to start

**Minimum Viable Sprint 4:**
- [ ] `$include`, `Table`, `min/max`, `abs`, `x.fx` working
- [ ] Scaling and diagnostics may be descoped if time-constrained
- [ ] PATH validation on representative examples (not all cases)

---

## Next Steps

1. **Before Day 1:** Complete all prep tasks (Task 1-9 from PREP_PLAN.md) - **10/23 unknowns already COMPLETE** ✅
2. **Day 1 Morning:** Review this plan, set up environment, verify tooling
3. **Day 1 Start:** Begin `$include` implementation per Day 1 plan above
4. **Daily:** Update progress, run tests, document findings
5. **Checkpoints:** Use templates, make GO/NO-GO decisions
6. **Day 10 End:** Sprint 4 retrospective, plan Sprint 5
