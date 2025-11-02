# Sprint 4 Plan: Feature Expansion + Robustness (FINAL)

**Sprint Duration:** 10 days (Days 1-10)
**Sprint Goal:** Broaden language coverage, improve numerics, and add quality-of-life features
**Status:** 📋 READY TO START
**Created:** 2025-11-01
**Final Version:** 2025-11-01

---

## Revision History

**FINAL Version (2025-11-01):**
This final plan addresses ALL 4 findings from PLAN_REVIEW_FINAL.md:
1. ✅ Added PREP_PLAN Task 3 (PATH setup) as explicit Follow-On Item on Day 7
2. ✅ Rebalanced ALL days to ≤8 hours including checkpoints
3. ✅ Added concise unknown summaries for EVERY referenced unknown
4. ✅ Trimmed Day 8 scope by moving documentation task to Day 9

**Previous Revisions:**
- PLAN_REVISED.md: Addressed initial review feedback (removed COMPLETE details, added ergonomics, expanded scaling)
- Original PLAN.md: Initial draft

---

## Overview

Sprint 4 builds on the solid foundation of Sprints 1-3 to add critical GAMS features and improve model robustness. This sprint focuses on:

1. **Language Features:** `$include` support, `Table` data blocks, fixed variables (`x.fx`)
2. **Non-smooth Functions:** `min/max` reformulation, `abs(x)` handling
3. **Numerics:** Scaling heuristics with byvar support for better solver performance
4. **Diagnostics:** Model statistics and Jacobian pattern dumps
5. **Developer Ergonomics:** Enhanced error messages, configuration options, logging

**Key Process Improvements from Sprint 3:**
- Proactive Known Unknowns list (10/23 already COMPLETE)
- Formal checkpoints on Days 3, 6, 8 (catch issues early)
- PATH solver validation environment (test with actual solver starting Day 8)
- Edge case testing matrix (comprehensive coverage)

---

## Success Metrics

### Functional Goals
- [ ] `$include` directive works (nested, circular detection, relative paths)
- [ ] `Table` data blocks parse correctly (2D, sparse, with descriptive text)
- [ ] Fixed variables (`x.fx`) handled in KKT and MCP emission
- [ ] `min/max` reformulated to valid MCP with auxiliary variables
- [ ] `abs(x)` either rejected or smoothed (user choice via flag)
- [ ] Scaling applied with configurable algorithm: `--scale none|auto|byvar`
- [ ] Diagnostics: model stats (rows/cols/nonzeros) and Jacobian dumps
- [ ] Enhanced error messages with source locations and suggestions
- [ ] Configuration via `pyproject.toml` and CLI flags
- [ ] Logging with verbosity control

### Quality Metrics
- [ ] All existing tests pass (602+ tests, no regressions)
- [ ] New test coverage >= 85% for Sprint 4 code
- [ ] All Known Unknowns resolved by Day 8 (PATH-dependent ones on Day 8)
- [ ] GAMS syntax validation passes for all test cases
- [ ] PATH solver successfully solves reformulated MCPs
- [ ] 10 mid-size example models created and validated

### Integration Metrics
- [ ] No Sprint 1/2/3 API breakage
- [ ] Generated MCP files compile in GAMS
- [ ] Golden files updated and passing
- [ ] CLI supports new features with appropriate flags

---

## Day-by-Day Plan

### Day 1: `$include` and Preprocessing (8h total)

#### Goals
- Implement `$include` directive support
- Handle nested includes and circular detection
- Integrate preprocessor into parse pipeline

#### Main Tasks

**Task 1: Implement `preprocess_includes()` function with recursion** (Est: 2.5h)
- Create preprocessor.py module with include resolution
- Handle relative/absolute paths
- Build include dependency graph

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.1 ($include syntax)**: GAMS uses simple string substitution without macro expansion. Preprocessor runs before parser, maintains include stack. ✅ COMPLETE
- **Unknown 1.4 (Nested includes)**: Arbitrary nesting allowed, tested 10 levels. Use depth tracking with default 100 limit, circular detection works. ✅ COMPLETE
- **Unknown 1.5 (Relative paths)**: Paths resolved relative to containing file, not CWD. Parent directory (..) works correctly. ✅ COMPLETE

**Task 2: Add circular include detection with clear error messages** (Est: 1.5h)
- Implement include stack tracking
- Detect cycles and report full chain
- Provide helpful error messages with source locations

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.4 (Nested includes)**: Circular detection implemented using include_stack. Raises CircularIncludeError with full chain shown. ✅ COMPLETE

**Task 3: Integrate preprocessor into `parse_model_file()`** (Est: 1h)
- Add preprocessing step before parsing
- Ensure transparent to downstream code
- Add debug comments for include boundaries

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 6.1 ($include vs ModelIR)**: Preprocessing happens before parsing, ModelIR sees flat expanded source. No special tracking needed. ✅ COMPLETE

**Task 4: Add relative path resolution** (Est: 1h)
- Resolve paths relative to file containing $include
- Handle parent directory (..) references
- Support absolute paths

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.5 (Relative paths)**: Use file_path.parent / included_filename. Resolves relative to containing file. ✅ COMPLETE

**Task 5: Write comprehensive tests** (Est: 2h)
- Test simple, nested, circular, missing files
- Test relative vs absolute paths
- Test error message quality

#### Deliverables
- `src/ir/preprocessor.py` with `preprocess_includes()` function
- Integration into parser (transparent to downstream code)
- 15+ tests covering all edge cases
- Documentation in docstrings

#### Acceptance Criteria
- [x] Simple `$include` works (file inserted at directive location)
- [x] Nested includes work (3+ levels deep)
- [x] Circular includes detected with full chain shown in error
- [x] Missing files produce clear error with source location
- [x] Relative paths resolve correctly (to containing file, not CWD)
- [x] All tests pass (including existing 602 tests) - **700 tests now passing**

#### Integration Risks
- **Risk 1:** Parser grammar may need updates if `$include` has special syntax
  - *Mitigation:* Preprocess before parsing (text substitution)
- **Risk 2:** Line numbers in error messages may be incorrect after include expansion
  - *Mitigation:* Add source mapping comments (future enhancement, not Sprint 4)

---

### Day 2: `Table` Data Blocks (8h total)

#### Goals
- Parse `Table` syntax for 2D parameter data
- Handle sparse tables (empty cells → 0)
- Integrate into parameter data structures

#### Main Tasks

**Task 1: Extend grammar with `table_block` rule** (Est: 2h)
- Add table_block grammar rule
- Separate from params_block
- Handle table row and value tokens

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.2 (Table syntax)**: Table uses 2D layout with row/col headers. First row = column indices, subsequent rows = row index + values. Grammar uses token metadata (line/column) to reconstruct rows despite %ignore NEWLINE. ✅ COMPLETE

**Task 2: Implement `_handle_table_block()` in parser** (Est: 2.5h)
- Parse table structure using token metadata
- Extract row and column headers
- Build parameter values dictionary

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.2 (Table syntax)**: Token metadata approach verified. Use .line and .column attributes to group tokens by row, match values to columns by position (±6 char tolerance). ✅ COMPLETE

**Task 3: Handle sparse cells and multi-dimensional keys** (Est: 1.5h)
- Zero-fill empty cells
- Format multi-dimensional keys as tuples
- Handle alignment variations

**Task 4: Write tests for dense, sparse, and edge cases** (Est: 2h)
- Test simple 2D tables
- Test sparse tables with missing values
- Test tables with descriptive text
- Test tables in included files

#### Deliverables
- Grammar extension in `src/gams/gams_grammer.lark`
- Parser handler in `src/ir/parser.py`
- 20+ tests covering table variations
- Integration with existing `ParameterDef` structure

#### Acceptance Criteria
- [x] Simple 2D table parses correctly (row/col headers → dict keys)
- [x] Sparse tables fill missing cells with 0.0
- [x] Descriptive text after table name handled
- [x] Multi-dimensional keys formatted correctly: `("i1", "j2")`
- [x] Table integrated with existing parameter emission code
- [x] All tests pass (including Sprint 1-3 tests) - **721 tests now passing**

#### Integration Risks
- **Risk 1:** Grammar `%ignore NEWLINE` may conflict with table row parsing
  - *Mitigation:* Use token metadata (line/column) to reconstruct rows (verified approach)
- **Risk 2:** Table data may conflict with later parameter assignments
  - *Mitigation:* Document precedence rules (later assignment wins)

---

### Day 3: `min/max` Reformulation - Part 1 (Infrastructure) (7h tasks + 1h checkpoint = 8h total)

#### Goals
- Design auxiliary variable reformulation for `min/max`
- Implement detection in AST traversal
- Create auxiliary variable generation framework

#### Main Tasks

**Task 1: Design epigraph reformulation** (Est: 2h)
- Document epigraph reformulation approach
- Design constraint structure
- Plan complementarity pairing

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.1 (min reformulation)**: Use epigraph form: z = min(x,y) becomes z ≤ x, z ≤ y with complementarity (z-x) ⊥ λ_x, (z-y) ⊥ λ_y. Stationarity: ∂f/∂z - λ_x - λ_y = 0. Scales linearly: n args → n+1 vars/eqs. ✅ COMPLETE
- **Unknown 2.2 (max reformulation)**: Dual of min, reverse inequalities: z ≥ x, z ≥ y. Same structure with opposite direction. Direct implementation preferred over -min(-x,-y) for efficiency. ✅ COMPLETE

**Task 2: Add AST traversal to detect `min/max` calls** (Est: 1.5h)
- Traverse equation ASTs to find function calls
- Identify min/max calls
- Extract arguments for reformulation

**Task 3: Implement auxiliary variable name generation** (Est: 1.5h)
- Create AuxiliaryVariableManager class
- Generate unique names based on context
- Detect and avoid collisions with user variables

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
- [x] `min(x, y)` calls detected in equation ASTs
- [x] Auxiliary variable names generated without collisions
- [x] Multi-argument `min(x, y, z)` supported (design level)
- [x] Nested `min(min(x, y), z)` flattened to `min(x, y, z)`
- [x] All existing tests pass (no regressions) - **754 tests now passing**

#### Integration Risks
- **Risk 1:** KKT assembly may need refactoring to add auxiliary constraints
  - *Mitigation:* Add new constraint type, keep existing code paths unchanged
- **Risk 2:** Variable ordering in Jacobian may break with new auxiliary vars
  - *Mitigation:* Extend IndexMapping to handle auxiliary variables

#### Follow-On Research Items
*Note: These are INCOMPLETE unknowns to be resolved during implementation:*

- **Unknown 4.2 (Auxiliary variable naming)**: ✅ **COMPLETE** (Verified on Day 3)
  - **Implementation**: Context-based naming with counter for duplicates in `src/kkt/reformulation.py`
  - **Naming scheme**: `aux_{min|max}_{context}_{index}` (e.g., `aux_min_objdef_0`)
  - **Features**: Collision detection, separate counters per (func_type, context), GAMS-compliant names
  - **Testing**: 8 dedicated tests in `test_reformulation.py`, all passing
  - **Result**: Robust, readable, debuggable auxiliary variable names
  - See KNOWN_UNKNOWNS.md Unknown 4.2 for full verification details
  
- **Unknown 6.4 (Auxiliary vars and IndexMapping)**: ✅ **COMPLETE** (Verified 2025-11-02)
  - **Finding**: Current architecture is CORRECT BY DESIGN - IndexMapping created fresh during derivative computation
  - **Integration Point**: Reformulations must be inserted at Step 2.5 (between normalize and derivatives)
  - **Pipeline**: Parse → Normalize → **[Reformulation]** → Derivatives (creates IndexMapping) → KKT → Emit
  - **Key Insight**: `build_index_mapping()` called inside `compute_objective_gradient()` and `compute_constraint_jacobian()`, ensuring auxiliary variables are included
  - **Action Required**: Add reformulation calls in cli.py BEFORE compute_objective_gradient()
  - **Verification**: Gradient/Jacobian alignment guaranteed by shared build_index_mapping() function
  - **Benefits**: No special handling needed, deterministic ordering, scalable to any number of aux vars
  - See KNOWN_UNKNOWNS.md Unknown 6.4 for complete analysis and integration code example

**Checkpoint 1** (Day 3 - End of Day): **(Est: 1h)** ✅ **COMPLETED**
- Review all Day 1-3 deliverables
- Verify preprocessing and table features working
- Check test coverage >= 70%
- Confirm no regressions
- **Decision:** ✅ **GO** - All acceptance criteria met, proceed to Days 4-6
- **Report:** See `docs/planning/SPRINT_4/CHECKPOINT1.md`

---

### Day 4: `min/max` Reformulation - Part 2 (Implementation) (8h total)

#### Goals
- Implement full `min/max` reformulation in KKT assembly
- Generate complementarity pairs for auxiliary constraints
- Integrate with stationarity equations

#### Main Tasks

**Task 1: Implement `reformulate_min()` function** (Est: 2.5h)
- Create auxiliary variable and multipliers
- Generate complementarity constraints
- Handle multi-argument case
- Flatten nested min calls

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.1 (min reformulation)**: Epigraph reformulation verified. For min(x₁,...,xₙ): create aux_min and n multipliers λᵢ, constraints xᵢ - aux_min ≥ 0, complementarity (xᵢ - aux_min) ⊥ λᵢ. Flatten nested min before reformulation. ✅ COMPLETE
- **Unknown 4.2 (Auxiliary variable naming)**: ✅ COMPLETE (Day 3) - Use `AuxiliaryVariableManager.generate_name(func_type, context)` to create names like `aux_min_objdef_0`. Collision detection implemented. Ready for use in reformulation.

**Task 2: Implement `reformulate_max()` function** (Est: 2h)
- Implement symmetric to min with reversed inequalities
- Reuse auxiliary variable infrastructure
- Handle multi-argument case

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.2 (max reformulation)**: Use xᵢ - aux_max ≤ 0 (opposite of min). Direct implementation more efficient than via -min(-x,-y). Same structure, different constraint direction. ✅ COMPLETE
- **Unknown 4.2 (Auxiliary variable naming)**: ✅ COMPLETE (Day 3) - Same `AuxiliaryVariableManager` works for both min and max. Separate counters per function type ensure `aux_max_objdef_0` and `aux_min_objdef_0` can coexist.

**Task 3: Add auxiliary constraints to KKT system** (Est: 1.5h)
- Extend KKT data structures for auxiliary constraints
- Add complementarity pairs
- Maintain equation-variable count balance

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
- [x] `min(x, y)` generates 2 auxiliary constraints with multipliers
- [x] `max(x, y)` generates 2 auxiliary constraints (opposite direction)
- [x] Multi-argument `min(a, b, c)` generates 3 constraints
- [x] Stationarity includes `∂f/∂z_min - λ_x - λ_y = 0` (handled by derivative computation)
- [x] Complementarity pairs: `(x - z_min) ⊥ λ_x`, `(y - z_min) ⊥ λ_y`
- [x] All tests pass (including reformulation-specific tests) - 770 tests passing

#### Integration Risks
- **Risk 1:** Jacobian computation may not handle auxiliary variables
  - *Mitigation:* Auxiliary constraints are simple (linear in aux var)
- **Risk 2:** GAMS emission may not declare auxiliary variables/equations
  - *Mitigation:* Extend emission templates to include auxiliary vars

#### Follow-On Research Items
*Note: These are INCOMPLETE unknowns to be resolved during implementation:*

- **Unknown 4.3 (Auxiliary constraints in Model)**: INCOMPLETE
  - Planned approach: Add auxiliary constraints to Model MCP declaration
  - Need to verify: GAMS compilation works, equation-variable pairing correct

- **Unknown 6.4 (Auxiliary vars and IndexMapping)**: ✅ **COMPLETE** (Research complete)
  - **Critical Integration Requirement**: Call reformulation functions in cli.py BEFORE compute_objective_gradient()
  - **Pipeline Position**: Insert at Step 2.5: Parse → Normalize → **[Reformulate]** → Derivatives → KKT → Emit
  - **Why It Works**: IndexMapping created fresh during derivative computation automatically includes auxiliary variables
  - **Implementation Pattern**:
    ```python
    # In cli.py main() function:
    model = parse_model_file(input_file)
    normalize_model(model)
    
    # ← INSERT REFORMULATION HERE (Step 2.5)
    reformulate_min_max(model)  # Modifies model.variables & model.equations
    
    # Derivatives will now include auxiliary variables automatically
    gradient = compute_objective_gradient(model)
    J_eq, J_ineq = compute_constraint_jacobian(model)
    ```
  - **No Special Handling**: Auxiliary variables treated identically to original variables
  - **Verification**: See KNOWN_UNKNOWNS.md Unknown 6.4 for detailed analysis

---

### Day 5: `abs(x)` Handling and Fixed Variables (`x.fx`) (8h total)

#### Goals
- Implement `abs(x)` handling (reject by default, smooth optional)
- Add fixed variable support (`x.fx = c`)
- Integrate both into KKT system

#### Main Tasks

**Task 1: Implement `abs(x)` detection and rejection** (Est: 1.5h)
- Detect abs() calls during differentiation
- Raise clear error by default
- Suggest --smooth-abs flag

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.3 (abs handling)**: Reject by default with clear error. Optional smoothing via --smooth-abs using sqrt(x² + ε). Default ε=1e-6 gives max error 0.001 at x=0, negligible elsewhere. Derivative: x/sqrt(x² + ε). ✅ COMPLETE

**Task 2: Add `--smooth-abs` flag with soft-abs approximation** (Est: 2h)
- Implement CLI flags --smooth-abs and --smooth-abs-epsilon
- Add differentiation rule for smooth abs: `sqrt(x^2 + ε)`
- Test accuracy and numerical stability (ε=1e-6 default)

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.3 (abs handling)**: Soft-abs approximation abs(x) ≈ sqrt(x² + ε) verified. Accuracy excellent for |x| ≥ 0.1 (rel error < 0.1%). Derivative continuous everywhere. ✅ COMPLETE

**Task 3: Parse `x.fx` syntax and create equality constraints** (Est: 2h)
- Extend parser to recognize .fx attribute
- Create equality constraints for fixed variables
- Handle both scalar and indexed variables

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 1.3 (Fixed variable semantics)**: x.fx = c creates equality constraint x - c = 0. Treat as equality constraint approach (Option A) implemented: pair with free multiplier in MCP. No bound multipliers (piL/piU) created. ✅ COMPLETE

**Task 4: Integrate fixed vars into KKT assembly** (Est: 1.5h)
- Skip stationarity equations for fixed variables
- Add fixing constraints to KKT system
- Pair with variable (not multiplier) in MCP

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 6.2 (Fixed vars in KKT)**: No stationarity equation for fixed vars (x determined by fixing constraint). Add equality constraint x - fx_value = 0. KKT dimension correct: equations = variables. ✅ COMPLETE (bug #63 fixed)

**Task 5: Write tests for both features** (Est: 1h)
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

#### Follow-On Research Items
*Note: These are INCOMPLETE unknowns to be resolved during implementation:*

- **Unknown 4.4 (Emit fixed variables in MCP)**: INCOMPLETE
  - Approach: Use equality constraint approach per Unknown 1.3 findings
  - Need to verify: MCP emission works, GAMS compilation succeeds, PATH handles correctly

---

### Day 6: Scaling Implementation + Developer Ergonomics (Part 1) (7h tasks + 1h checkpoint = 8h total)

#### Goals
- Implement Curtis-Reid scaling algorithm with byvar support
- Add CLI flags for scaling control
- Apply scaling to Jacobian before KKT assembly
- Begin developer ergonomics improvements (error messages)

#### Main Tasks

**Task 1: Implement Curtis-Reid row/column scaling** (Est: 2h)
- Implement iterative row/column norm balancing
- Compute scaling factors from Jacobian
- Handle sparse matrices efficiently

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 3.1 (Scaling algorithm)**: INCOMPLETE - Curtis-Reid geometric mean scaling to be implemented. Iterative row/col norm balancing: R_i = 1/√(row_norm_i), C_j = 1/√(col_norm_j). Verify convergence and conditioning improvement.

**Task 2: Implement byvar scaling mode** (Est: 1.5h)
- Add per-variable scaling option
- Scale each variable's column independently
- Document when to use byvar vs auto

**Task 3: Add `--scale` flag (none/auto/byvar, default: none)** (Est: 1h)
- Add CLI flag for scaling control
- Support none|auto|byvar options
- Default to no scaling (opt-in)
- Document scaling behavior

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 6.3 (Scaling impact on tests)**: INCOMPLETE - CRITICAL. Existing tests must pass without --scale flag (default: none). Verify scaled and unscaled give equivalent solutions, no test breakage.

**Task 4: Compute and apply scaling factors** (Est: 1h)
- Extract Jacobian structure
- Apply Curtis-Reid algorithm
- Store and apply scaling factors

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 3.2 (Scaling application point)**: INCOMPLETE - Decide scale NLP vs scale KKT. Need to verify which approach gives better PATH solver performance.

**Task 5: Enhanced error messages - Phase 1** (Est: 1.5h)
- Add source location tracking to all parser errors
- Improve error messages for common mistakes
- Add suggestions to error messages

#### Deliverables
- `src/kkt/scaling.py` module with Curtis-Reid algorithm
- CLI flags: `--scale none|auto|byvar`
- Scaling factors stored in KKT system
- Enhanced error messages for parser
- 15+ tests for scaling correctness

#### Acceptance Criteria
- [ ] Curtis-Reid scaling implemented (iterative row/col norm balancing)
- [ ] `byvar` mode scales each variable column independently
- [ ] Scaling factors computed from symbolic Jacobian
- [ ] Scaled Jacobian has row/col norms ≈ 1
- [ ] `--scale none` skips scaling (default)
- [ ] `--scale auto` applies Curtis-Reid
- [ ] `--scale byvar` applies per-variable scaling
- [ ] Existing tests pass with `--scale none`
- [ ] Tests with scaling verify semantic preservation
- [ ] Parser errors include source locations

#### Integration Risks
- **Risk 1:** Scaling may expose bugs in Jacobian computation
  - *Mitigation:* Verify Jacobian correctness before scaling
- **Risk 2:** Scaled vs unscaled solutions may differ numerically
  - *Mitigation:* Document that scaling is for solver robustness, not semantics

#### Follow-On Research Items
*Note: These are INCOMPLETE unknowns to be verified during implementation:*

- **Unknown 3.1 (Scaling algorithm selection)**: INCOMPLETE - Implement and verify Curtis-Reid convergence and conditioning improvement
- **Unknown 3.2 (Scaling application point)**: INCOMPLETE - Test both approaches, decide based on PATH performance
- **Unknown 6.3 (Scaling impact on tests)**: INCOMPLETE - CRITICAL - Verify no test breakage with default --scale none

**Checkpoint 2** (Day 6 - End of Day): **(Est: 1h)**
- Review all Day 4-6 deliverables
- Verify all features >= 80% implemented
- Verify Unknowns 3.1, 3.2, 4.2-4.4, 6.2-6.4 status
- Check test coverage >= 85%
- Confirm no critical bugs
- **Decision:** GO/NO-GO for Days 7-10, descoping if needed

---

### Day 7: Diagnostics + Developer Ergonomics (Part 2) (6h tasks + 2h follow-on = 8h total)

#### Goals
- Add model statistics reporting (rows/cols/nonzeros)
- Implement Jacobian pattern dump (Matrix Market format)
- Complete developer ergonomics improvements (config, logging)
- Prepare for PATH validation

#### Main Tasks

**Task 1: Compute model statistics from KKT system** (Est: 1.5h)
- Count equations, variables, nonzeros
- Break down by type (stationarity, complementarity, bounds)
- Format for display

**Task 2: Implement Matrix Market Jacobian export** (Est: 1.5h)
- Export Jacobian in Matrix Market format
- Handle sparse structure
- Validate format (SciPy/MATLAB compatible)

**Task 3: Add CLI flags for diagnostics** (Est: 0.75h)
- Add --stats flag for statistics output
- Add --dump-jacobian <file> flag
- Integrate into main workflow

**Task 4: Configuration via pyproject.toml** (Est: 1h)
- Add pyproject.toml support for default options
- Support all CLI flags in config file
- Document configuration options

**Task 5: Structured logging with verbosity control** (Est: 0.75h)
- Add logging framework with levels
- Add --verbose and --quiet flags
- Log key transformation steps

**Task 6: Enhanced error messages - Phase 2** (Est: 0.5h)
- Improve differentiation error messages
- Improve KKT assembly error messages
- Add troubleshooting suggestions

#### Deliverables
- `src/diagnostics/` module with stats and export functions
- CLI flags: `--stats`, `--dump-jacobian <file>`, `--verbose`, `--quiet`
- Matrix Market format Jacobian export
- `pyproject.toml` configuration support
- Structured logging throughout codebase
- 15+ tests for diagnostic and logging features

#### Acceptance Criteria
- [ ] `--stats` prints: # equations, # variables, # nonzeros
- [ ] Stats include breakdown: stationarity, complementarity, bounds
- [ ] `--dump-jacobian jac.mtx` exports Jacobian in Matrix Market format
- [ ] Matrix Market file valid (can be loaded by SciPy/MATLAB)
- [ ] `pyproject.toml` can set default options for all flags
- [ ] `--verbose` shows detailed transformation steps
- [ ] `--quiet` suppresses non-error output
- [ ] Error messages improved with source locations and suggestions
- [ ] Diagnostics don't affect MCP generation
- [ ] All tests pass

#### Integration Risks
- **Risk 1:** Matrix Market export may be slow for large models
  - *Mitigation:* Document as debug feature, not production
- **Risk 2:** Statistics may be incorrect for reformulated models
  - *Mitigation:* Count after reformulation (auxiliary vars included)

#### Follow-On Items

**PREP_PLAN Task 3: Set Up PATH Solver Validation** (Est: 2h - after licensing available)
*Note: This follow-on runs once licensing is available and must finish before Day 8 validation begins.*

- Install PATH solver (requires GAMS license)
- Verify PATH executable availability within GAMS
- Capture environment setup steps for the team (harness work deferred to Day 8)

*Prerequisites (from PREP_PLAN.md):*
- GAMS license must be active (may not be available until late sprint)
- This work happens AFTER core Day 7 tasks complete
- Enables Day 8 PATH validation work

---

### Day 8: PATH Solver Validation and Testing (6.5h tasks + 1h checkpoint = 7.5h total)

#### Goals
- Validate all generated MCPs with PATH solver
- Test reformulated features (`min/max`, `abs`, fixed vars)
- Identify and document any PATH-specific issues
- Complete all Known Unknown verification

#### Main Tasks

**Task 1: Smoke-test PATH environment and finalize validation harness** (Est: 1.5h)
- Reuse the PATH installation from Day 7 follow-on work
- Run sanity checks to confirm solver invocation works end-to-end
- Wire the automation harness and baseline configuration files for validation runs

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 5.2 (PATH options)**: INCOMPLETE - Document default options, test problem-specific tuning. Verify recommended options: convergence_tolerance, iterlim, crash_method, output level.

**Task 2: Run all golden files through PATH** (Est: 1.5h)
- Validate existing golden files
- Verify no regressions
- Document solve status

**Task 3: Test `min/max` reformulations with PATH** (Est: 2h)
- Test simple 2-argument min/max
- Test multi-argument cases
- Test nested cases (flattened)

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 2.4 (PATH non-smooth compatibility)**: INCOMPLETE - Verify PATH handles min/max reformulations. Test convergence, initial point sensitivity, solver robustness.
- **Unknown 5.1 (PATH nonlinearity handling)**: INCOMPLETE - Test PATH on highly nonlinear KKT systems. Verify when to apply scaling, when convergence fails.

**Task 4: Test smooth `abs` and fixed vars with PATH** (Est: 1.5h)
- Test abs() with smoothing enabled
- Test fixed variable problems
- Verify numerical stability and solution accuracy

*Prerequisites (from KNOWN_UNKNOWNS.md):*
- **Unknown 5.3 (PATH failure reporting)**: INCOMPLETE - Parse PATH status codes, error messages, listing file output. Document infeasibility, unboundedness, singular Jacobian messages.
- **Unknown 5.4 (PATH initial points)**: INCOMPLETE - Low priority. Verify whether PATH default initialization sufficient, when user initial points needed.

#### Deliverables
- PATH validation tests in `tests/validation/test_path.py`
- Documentation of PATH solver setup and usage
- List of known PATH issues/limitations
- 10+ PATH-specific tests
- All Unknown verifications complete

#### Acceptance Criteria
- [ ] All golden files solve successfully with PATH
- [ ] Reformulated `min/max` problems solve correctly
- [ ] Smooth `abs` problems solve correctly
- [ ] Fixed variable problems solve correctly
- [ ] PATH solver options documented (if needed)
- [ ] All tests pass (including PATH validation tests)
- [ ] All Known Unknowns resolved or documented

#### Integration Risks
- **Risk 1:** PATH may not be available on all systems
  - *Mitigation:* Make PATH tests conditional (skip if not found)
- **Risk 2:** PATH may fail on some reformulations
  - *Mitigation:* Document limitations, provide alternative formulations

#### Follow-On Research Items (Complete during Day 8)
*Note: These unknowns are INCOMPLETE and must be verified with actual PATH solver:*

- **Unknown 2.4 (PATH non-smooth compatibility)**: INCOMPLETE - Verify PATH can handle min/max reformulations, convergence characteristics, initial point sensitivity, solver robustness

- **Unknown 5.1 (PATH nonlinearity handling)**: INCOMPLETE - Verify how PATH handles highly nonlinear KKT systems, when to apply scaling, when convergence fails

- **Unknown 5.2 (PATH options)**: INCOMPLETE - Document default options, test problem-specific tuning, verify recommended options

- **Unknown 5.3 (PATH failure reporting)**: INCOMPLETE - Verify how to parse PATH status codes, error messages, listing file output

- **Unknown 5.4 (PATH initial points)**: INCOMPLETE - Low priority. Verify whether PATH default initialization sufficient, when user initial points needed

**Checkpoint 3** (Day 8 - End of Day): **(Est: 1h)**
- Review all deliverables
- Verify all features 100% implemented
- Verify all Known Unknowns resolved
- Verify all tests passing
- Verify PATH validation complete
- **Decision:** GO/EXTEND for final integration

---

### Day 9: Integration Testing, Documentation, and Examples (8h total)

#### Goals
- Run comprehensive integration tests
- Update all documentation
- Regenerate golden files
- Create 10 mid-size example models
- Verify all acceptance criteria

#### Main Tasks

**Task 1: Create 10 mid-size example models** (Est: 3.5h)
- Curate or create transport-style models
- Include indexed constraints and nonlinear costs
- Cover all Sprint 4 features ($include, Table, min/max, abs, x.fx, scaling)
- Validate all examples with GAMS and PATH

**Task 2: Update README.md with Sprint 4 features** (Est: 1.5h)
- Document $include support
- Document Table support
- Document min/max reformulation
- Document abs() handling
- Document fixed variables
- Document scaling (including byvar mode)
- Document diagnostics and developer ergonomics

**Task 3: Update technical documentation** (Est: 1h)
- Update KKT_ASSEMBLY.md with reformulation details
- Update GAMS_EMISSION.md with auxiliary variable handling
- Document scaling algorithm (all modes)
- Add troubleshooting guide
- Document configuration options

**Task 4: Document PATH solver requirements and options** (Est: 1h)
*Note: This task moved from Day 8 to reduce high-risk validation day workload*
- Document PATH setup instructions
- Document recommended options for different problem types
- Create troubleshooting guide for PATH failures

**Task 5: Regenerate all golden files with new features** (Est: 1h)
- Update golden files with new capabilities
- Add new golden files for Sprint 4 features
- Validate all golden files with GAMS

#### Deliverables
- 10 mid-size example models with documentation
- Updated README.md with complete feature list
- Updated technical docs (KKT_ASSEMBLY.md, GAMS_EMISSION.md)
- PATH solver documentation (moved from Day 8)
- New golden files with reformulations
- Configuration and logging documentation

#### Acceptance Criteria
- [ ] Examples exercise all Sprint 4 features ($include, Table, min/max, abs, x.fx, scaling)
- [ ] 10 mid-size examples created and validated
- [ ] All examples solve with PATH
- [ ] README.md accurate and complete
- [ ] Technical docs reflect all new features
- [ ] PATH documentation complete (setup, options, troubleshooting)
- [ ] Golden files validate with GAMS
- [ ] All acceptance criteria from Days 1-8 met
- [ ] Configuration and logging documented
- [ ] Regression suite queued for Day 10 full run

#### Integration Risks
- **Risk 1:** Documentation may be out of sync with code
  - *Mitigation:* Review docs against actual implementation
- **Risk 2:** Golden file regeneration may reveal hidden bugs
  - *Mitigation:* Fix any issues found, retest
- **Risk 3:** Creating 10 quality examples may take longer than estimated
  - *Mitigation:* Can use Day 10 buffer time if needed

---

### Day 10: Polish, Buffer, and Sprint Wrap-Up (8h total)

#### Goals
- Final quality pass (typecheck, lint, format)
- Address any remaining issues
- Create Sprint 4 retrospective
- Plan Sprint 5

#### Main Tasks

**Task 1: Run full regression test suite** (Est: 1.5h)
- Execute all 650+ tests with all Sprint 4 features enabled
- Capture coverage metrics (target ≥ 85%)
- Log any failures for immediate triage

**Task 2: Run quality checks (mypy, ruff, black)** (Est: 1.5h)
- Run mypy on all modules
- Run ruff linter
- Run black formatter
- Fix any issues found

**Task 3: Fix any remaining issues or technical debt** (Est: 2h)
- Address bugs discovered during regression or quality checks
- Clean up code comments and TODOs
- Refactor any messy implementations

**Task 4: Create Sprint 4 retrospective document** (Est: 1.5h)
- Document what went well
- Document what could improve
- Analyze Known Unknowns process effectiveness
- Document lessons for Sprint 5

**Task 5: Update CHANGELOG.md with Sprint 4 release** (Est: 1h)
- List all new features
- Document breaking changes (if any)
- Add upgrade notes

**Task 6: Plan Sprint 5 scope (preliminary)** (Est: 0.5h)
- Review PROJECT_PLAN.md for next priorities
- Identify dependencies on Sprint 4 learnings
- Create preliminary Sprint 5 scope document

#### Deliverables
- Full regression test suite results (coverage ≥ 85%)
- All quality checks passing
- Sprint 4 retrospective (docs/planning/SPRINT_4/RETROSPECTIVE.md)
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

**Sprint 5 Planning:**
- Review Sprint 4 lessons learned
- Identify remaining PROJECT_PLAN.md items
- Create Sprint 5 prep plan
- Schedule Sprint 5 kickoff

---

## Risk Management

### High-Priority Risks

**Risk 1: PATH Solver Not Available Until Day 7**
- **Impact:** Cannot validate reformulations until Day 7-8
- **Mitigation:** 
  - Test reformulation logic independently (unit tests)
  - Verify mathematical correctness via literature
  - Schedule PATH setup as explicit Follow-On on Day 7 (after licensing)
  - Schedule PATH-dependent work on Day 8
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
- **Contingency:** Make byvar mode experimental if unstable

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

**Risk 7: Creating 10 Mid-Size Examples Takes Longer Than Expected**
- **Impact:** Day 9 may overrun
- **Mitigation:** Plan realistic examples, reuse existing patterns
- **Contingency:** Can reduce to 7-8 examples or use Day 10 buffer

### Low-Priority Risks

**Risk 8: Performance Issues with Large Models**
- **Impact:** Scaling/diagnostics may be slow
- **Mitigation:** Profile if issues arise
- **Contingency:** Document as known limitation, optimize in Sprint 5

**Risk 9: Unknown Unknowns Discovered Mid-Sprint**
- **Impact:** Schedule delays
- **Mitigation:** Proactive Known Unknowns list (10/23 already COMPLETE), checkpoints on Days 3, 6, 8
- **Contingency:** Use Day 10 buffer time or extend sprint

---

## Checkpoint Schedule

### Checkpoint 1 (Day 3 - End of Day)
- **Focus:** Early features scaffolded, preprocessing and tables working
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Verify:** Test coverage >= 70%, no regressions, preprocessing/tables functional
- **Decision:** GO/NO-GO for Days 4-6
- **Time:** 1 hour

### Checkpoint 2 (Day 6 - End of Day)
- **Focus:** All features >= 80% complete, integration healthy, scaling working
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Verify:** Test coverage >= 85%, Unknowns 3.1-3.2, 4.2-4.4, 6.2-6.4 verified
- **Decision:** GO/NO-GO for Days 7-10, descoping if needed
- **Time:** 1 hour

### Checkpoint 3 (Day 8 - End of Day)
- **Focus:** Feature completeness, PATH validation, all unknowns resolved
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Verify:** All features 100%, all unknowns resolved, PATH validation complete
- **Decision:** GO/EXTEND for completion
- **Time:** 1 hour

---

## Known Unknowns Schedule

Sprint 4 Known Unknowns are documented in:
- `/Users/jeff/experiments/nlp2mcp/docs/planning/SPRINT_4/KNOWN_UNKNOWNS.md`
- `/Users/jeff/experiments/nlp2mcp/docs/planning/SPRINT_4/KNOWN_UNKNOWNS/SCHEDULE.md`

**Verification Status (as of 2025-11-01):**

**COMPLETE (10/23) - Prerequisites satisfied ✅:**

1. **Unknown 1.1 ($include syntax)**: GAMS uses simple string substitution without macro expansion. Preprocessor runs before parser, maintains include stack. ✅ COMPLETE

2. **Unknown 1.2 (Table syntax)**: Table uses 2D layout with row/col headers. Grammar uses token metadata (line/column) to reconstruct rows despite %ignore NEWLINE. ✅ COMPLETE

3. **Unknown 1.3 (Fixed variable semantics)**: x.fx = c creates equality constraint x - c = 0. Treat as equality constraint paired with free multiplier in MCP. No bound multipliers created. ✅ COMPLETE

4. **Unknown 1.4 (Nested includes)**: Arbitrary nesting allowed, tested 10 levels. Use depth tracking with default 100 limit, circular detection works. ✅ COMPLETE

5. **Unknown 1.5 (Relative paths)**: Paths resolved relative to containing file, not CWD. Parent directory (..) works correctly. ✅ COMPLETE

6. **Unknown 2.1 (min reformulation)**: Use epigraph form: z = min(x,y) becomes z ≤ x, z ≤ y with complementarity. Scales linearly: n args → n+1 vars/eqs. Flatten nested min. ✅ COMPLETE

7. **Unknown 2.2 (max reformulation)**: Dual of min, reverse inequalities: z ≥ x, z ≥ y. Same structure with opposite direction. Direct implementation preferred over -min(-x,-y). ✅ COMPLETE

8. **Unknown 2.3 (abs handling)**: Reject by default. Optional smoothing via --smooth-abs using sqrt(x² + ε). Default ε=1e-6 gives max error 0.001 at x=0. Derivative: x/sqrt(x² + ε). ✅ COMPLETE

9. **Unknown 4.1 (Line breaking)**: GAMS has no practical line length limit. Current output (max ~158 chars) acceptable. No line breaking needed. ✅ COMPLETE

10. **Unknown 6.1 ($include vs ModelIR)**: Preprocessing happens before parsing, ModelIR sees flat expanded source. No special tracking needed in ModelIR. ✅ COMPLETE

**INCOMPLETE - TO BE VERIFIED (12/23):**

**Days 3-6 Verification:**

11. **Unknown 4.2 (Auxiliary variable naming)**: ✅ COMPLETE (Day 3) - Context-based naming with collision detection implemented in `AuxiliaryVariableManager`. All 8 tests passing. Supports indexed equations, GAMS-compliant names, debuggable output.

12. **Unknown 4.3 (Auxiliary constraints in Model)**: INCOMPLETE - Verify GAMS compilation works, equation-variable pairing correct during Day 4

13. **Unknown 6.4 (Auxiliary vars and IndexMapping)**: ✅ COMPLETE (Research) - Architecture correct by design. IndexMapping created during derivative computation automatically includes auxiliary variables. Integration point identified: insert reformulation at Step 2.5 in cli.py (between normalize and derivatives). Gradient/Jacobian alignment guaranteed by shared build_index_mapping(). See KNOWN_UNKNOWNS.md for integration code.

14. **Unknown 4.4 (Emit fixed variables in MCP)**: INCOMPLETE - Verify MCP emission works, GAMS compilation succeeds, PATH handles correctly during Day 5

15. **Unknown 6.2 (Fixed vars in KKT)**: INCOMPLETE - Verify no stationarity equation for fixed vars, KKT dimension correct during Day 5 (bug #63 already fixed)

16. **Unknown 3.1 (Scaling algorithm)**: INCOMPLETE - Implement Curtis-Reid, verify convergence and conditioning improvement during Day 6

17. **Unknown 3.2 (Scaling application point)**: INCOMPLETE - Test scale NLP vs scale KKT, decide based on PATH performance during Day 6

18. **Unknown 6.3 (Scaling impact on tests)**: INCOMPLETE - CRITICAL - Verify existing tests pass with default --scale none during Day 6

**Day 8 PATH Validation:**

19. **Unknown 2.4 (PATH non-smooth compatibility)**: INCOMPLETE - Verify PATH handles min/max reformulations, convergence characteristics, initial point sensitivity

20. **Unknown 5.1 (PATH nonlinearity handling)**: INCOMPLETE - Verify PATH handles highly nonlinear KKT systems, when to apply scaling, when convergence fails

21. **Unknown 5.2 (PATH options)**: INCOMPLETE - Document default options, test problem-specific tuning, verify recommended options

22. **Unknown 5.3 (PATH failure reporting)**: INCOMPLETE - Parse PATH status codes, error messages, listing file output

23. **Unknown 5.4 (PATH initial points)**: INCOMPLETE - Low priority. Verify whether PATH default initialization sufficient

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
2. **Early Validation:** PATH setup scheduled explicitly on Day 7 (as Follow-On after licensing)
3. **Formal Checkpoints:** Days 3, 6, 8 with templates and decision points
4. **Test-Driven Development:** Write tests before/during implementation
5. **Incremental Integration:** Test each feature independently before combining
6. **Documentation as You Go:** Update docs daily, not just Day 9
7. **Developer Ergonomics:** Enhanced errors, config, logging throughout sprint
8. **Time Management:** All days rebalanced to ≤8 hours including checkpoints

---

## Success Criteria Summary

**Sprint 4 is successful if:**
- [ ] All 8 priority-1 features implemented (`$include`, `Table`, `min/max`, `abs`, `x.fx`, scaling with byvar, diagnostics, developer ergonomics)
- [ ] All existing tests pass (602+ with no regressions)
- [ ] New test coverage >= 85%
- [ ] All Known Unknowns resolved by Day 8
- [ ] PATH validation complete (all golden files solve)
- [ ] 10 mid-size examples created and validated
- [ ] Documentation complete and accurate
- [ ] Configuration and logging working
- [ ] GAMS syntax validation passes
- [ ] Checkpoints all show GO status
- [ ] No critical bugs or technical debt
- [ ] Sprint 5 ready to start

**Minimum Viable Sprint 4:**
- [ ] `$include`, `Table`, `min/max`, `abs`, `x.fx` working
- [ ] Scaling with none|auto|byvar modes
- [ ] Basic diagnostics (stats)
- [ ] Enhanced error messages
- [ ] PATH validation on representative examples (not all cases)
- [ ] At least 7 mid-size examples

---

## Day-by-Day Hour Allocation Summary

| Day | Tasks | Checkpoint | Total | Status |
|-----|-------|------------|-------|--------|
| Day 1 | 8h | - | 8h | ✅ Within limit |
| Day 2 | 8h | - | 8h | ✅ Within limit |
| Day 3 | 7h | 1h | 8h | ✅ Within limit |
| Day 4 | 8h | - | 8h | ✅ Within limit |
| Day 5 | 8h | - | 8h | ✅ Within limit |
| Day 6 | 7h | 1h | 8h | ✅ Within limit |
| Day 7 | 6h (+2h follow-on) | - | 8h | ✅ Within limit |
| Day 8 | 6.5h | 1h | 7.5h | ✅ Within limit (high-risk day) |
| Day 9 | 8h | - | 8h | ✅ Within limit |
| Day 10 | 8h | - | 8h | ✅ Within limit |

**Total: 79.5 hours over 10 days (avg 7.95h/day)**

All days now balanced to ≤8 hours including checkpoints, addressing Finding 2 from review.

---

## Next Steps

1. **Before Day 1:** Complete all prep tasks (Task 1-9 from PREP_PLAN.md) - **10/23 unknowns already COMPLETE** ✅
2. **Day 1 Morning:** Review this plan, set up environment, verify tooling
3. **Day 1 Start:** Begin `$include` implementation per Day 1 plan above
4. **Daily:** Update progress, run tests, document findings
5. **Checkpoints:** Use templates, make GO/NO-GO decisions
6. **Day 7 Follow-On:** Set up PATH validation (after licensing available)
7. **Day 10 End:** Sprint 4 retrospective, plan Sprint 5

---

## Review Findings Addressed

This FINAL plan addresses ALL 4 findings from PLAN_REVIEW_FINAL.md:

### ✅ Finding 1: Add PREP_PLAN Task 3 as Follow-On Item
- **Status:** ADDRESSED
- **Location:** Day 7 Follow-On Items section
- **Details:** PATH setup explicitly scheduled as 2h follow-on work on Day 7, clearly marked as happening AFTER licensing becomes available and BEFORE Day 8 validation

### ✅ Finding 2: Rebalance to 8 hours per day MAX
- **Status:** ADDRESSED
- **Changes Made:**
  - Day 1: 9h → 8h (reduced task estimates slightly)
  - Day 2: 9h → 8h (reduced task estimates)
  - Day 3: 8h + 1h checkpoint = 9h → 7h + 1h = 8h (reduced task estimates)
  - Day 4: Kept at 8h (already compliant)
  - Day 5: 10h → 8h (reduced task estimates)
  - Day 6: 8h + 1h checkpoint = 9h → 7h + 1h = 8h (reduced task estimates)
  - Day 7: 9.5h → 8h (reduced task estimates, moved PATH setup to Follow-On)
  - Day 8: 8h + 1h checkpoint = 9h → 6.5h + 1h = 7.5h (moved docs task to Day 9)
  - Day 9: 9.5h → 8h (added PATH docs from Day 8, rebalanced)
  - Day 10: 10h → 8h (reduced estimates, more realistic buffer)

### ✅ Finding 3: Reintroduce Unknown Summaries
- **Status:** ADDRESSED
- **Details:** Added concise summaries from KNOWN_UNKNOWNS.md for EVERY referenced unknown (both COMPLETE and INCOMPLETE), showing:
  - Findings (1-2 sentences)
  - Key architecture/approach (1-2 sentences)
  - Status (✅ COMPLETE or INCOMPLETE with verification needs)
- **Format:** Consistent "*Prerequisites (from KNOWN_UNKNOWNS.md):*" sections throughout

### ✅ Finding 4: Trim Day 8 Scope
- **Status:** ADDRESSED
- **Details:** Moved "Document PATH solver requirements and options" (Task 5, 1.5h) from Day 8 to Day 9 (now Task 5)
- **Result:** Day 8 reduced from 8h + 1h checkpoint = 9h to 6.5h + 1h = 7.5h total (under 8h cap for high-risk PATH validation day)

---

**END OF SPRINT 4 PLAN (FINAL)**
