# Sprint 4 Plan: Feature Expansion + Robustness (REVISED)

**Sprint Duration:** 10 days (Days 1-10)
**Sprint Goal:** Broaden language coverage, improve numerics, and add quality-of-life features
**Status:** 🔄 IN PROGRESS
**Created:** 2025-11-01
**Revised:** 2025-11-01

---

## Revision Notes

This revised plan addresses feedback from PLAN_REVIEW.md:
1. ✅ Removed COMPLETE unknown details from main task lists (brief notes only)
2. ✅ Added developer ergonomics tasks (error messages, pyproject config, logging)
3. ✅ Expanded scaling to support `--scale none|auto|byvar`
4. ✅ Added explicit task for 10 mid-size example models (Day 9)
5. ✅ Fixed Success Metrics to acknowledge PATH unknowns complete Day 8
6. ✅ Moved INCOMPLETE unknowns to "Follow-On Research Items" sections
7. ✅ Re-scoped Day 8 to 8 hours (moved docs/config tasks to Days 7 and 9)

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
- PATH solver validation environment (test with actual solver starting Day 7)
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
- *Prerequisites: Unknowns 1.1, 1.4, 1.5, 6.1 COMPLETE ✅*

**Task 2: Add circular include detection with clear error messages** (Est: 1.5h)
- Implement include stack tracking
- Detect cycles and report full chain
- Provide helpful error messages with source locations
- *Prerequisites: Unknown 1.4 COMPLETE ✅*

**Task 3: Integrate preprocessor into `parse_model_file()`** (Est: 1h)
- Add preprocessing step before parsing
- Ensure transparent to downstream code
- Add debug comments for include boundaries
- *Prerequisites: Unknown 6.1 COMPLETE ✅*

**Task 4: Add relative path resolution** (Est: 1.5h)
- Resolve paths relative to file containing $include
- Handle parent directory (..) references
- Support absolute paths
- *Prerequisites: Unknown 1.5 COMPLETE ✅*

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
- *Prerequisites: Unknown 1.2 COMPLETE ✅*

**Task 2: Implement `_handle_table_block()` in parser** (Est: 3h)
- Parse table structure using token metadata
- Extract row and column headers
- Build parameter values dictionary
- *Prerequisites: Unknown 1.2 COMPLETE ✅ (token metadata approach)*

**Task 3: Handle sparse cells and multi-dimensional keys** (Est: 2h)
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

---

### Day 3: `min/max` Reformulation - Part 1 (Infrastructure)

#### Goals
- Design auxiliary variable reformulation for `min/max`
- Implement detection in AST traversal
- Create auxiliary variable generation framework

#### Main Tasks

**Task 1: Design epigraph reformulation** (Est: 2h)
- Document epigraph reformulation approach
- Design constraint structure
- Plan complementarity pairing
- *Prerequisites: Unknowns 2.1, 2.2 COMPLETE ✅*

**Task 2: Add AST traversal to detect `min/max` calls** (Est: 2h)
- Traverse equation ASTs to find function calls
- Identify min/max calls
- Extract arguments for reformulation

**Task 3: Implement auxiliary variable name generation** (Est: 2h)
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

#### Follow-On Research Items
- **Unknown 4.2: Auxiliary variable naming** (INCOMPLETE - verify during implementation)
  - Planned approach: Context-based naming with counter for duplicates
  - Need to verify: Collision detection, indexed equation handling, GAMS name validity

**Checkpoint 1** (Day 3 - End of Day):
- Review all Day 1-3 deliverables (Est: 1h)
- Verify preprocessing and table features working
- Check test coverage >= 70%
- Confirm no regressions
- **Decision:** GO/NO-GO for Days 4-6

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

#### Follow-On Research Items
- **Unknown 4.3: Auxiliary constraints in Model declaration** (INCOMPLETE)
  - Planned approach: Add auxiliary constraints to Model MCP declaration
  - Need to verify: GAMS compilation works, equation-variable pairing correct

- **Unknown 6.4: Auxiliary vars and IndexMapping** (INCOMPLETE - CRITICAL)
  - IndexMapping must be created AFTER reformulations to include auxiliary variables
  - Need to verify: Gradient/Jacobian columns align correctly, no index misalignment

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
- *Prerequisites: Unknown 2.3 COMPLETE ✅*

**Task 2: Add `--smooth-abs` flag with soft-abs approximation** (Est: 2.5h)
- Implement CLI flags --smooth-abs and --smooth-abs-epsilon
- Add differentiation rule for smooth abs: `sqrt(x^2 + ε)`
- Test accuracy and numerical stability (ε=1e-6 default)
- *Prerequisites: Unknown 2.3 COMPLETE ✅*

**Task 3: Parse `x.fx` syntax and create equality constraints** (Est: 2h)
- Extend parser to recognize .fx attribute
- Create equality constraints for fixed variables
- Handle both scalar and indexed variables
- *Prerequisites: Unknown 1.3 COMPLETE ✅*

**Task 4: Integrate fixed vars into KKT assembly** (Est: 2h)
- Skip stationarity equations for fixed variables
- Add fixing constraints to KKT system
- Pair with variable (not multiplier) in MCP

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

#### Follow-On Research Items
- **Unknown 4.4: Emit fixed variables in MCP** (INCOMPLETE)
  - Approach: Use equality constraint approach per Unknown 1.3 findings
  - Need to verify: MCP emission works, GAMS compilation succeeds, PATH handles correctly

- **Unknown 6.2: Fixed vars in KKT assembly** (INCOMPLETE)
  - Approach: No stationarity equation for fixed vars, add fixing constraint
  - Need to verify: KKT dimension correct (equations = variables), no piL/piU created

---

### Day 6: Scaling Implementation + Developer Ergonomics (Part 1)

#### Goals
- Implement Curtis-Reid scaling algorithm with byvar support
- Add CLI flags for scaling control
- Apply scaling to Jacobian before KKT assembly
- Begin developer ergonomics improvements (error messages)

#### Main Tasks

**Task 1: Implement Curtis-Reid row/column scaling** (Est: 2.5h)
- Implement iterative row/column norm balancing
- Compute scaling factors from Jacobian
- Handle sparse matrices efficiently

**Task 2: Implement byvar scaling mode** (Est: 1.5h)
- Add per-variable scaling option
- Scale each variable's column independently
- Document when to use byvar vs auto

**Task 3: Add `--scale` flag (none/auto/byvar, default: none)** (Est: 1h)
- Add CLI flag for scaling control
- Support none|auto|byvar options
- Default to no scaling (opt-in)
- Document scaling behavior

**Task 4: Compute and apply scaling factors** (Est: 1.5h)
- Extract Jacobian structure
- Apply Curtis-Reid algorithm
- Store and apply scaling factors

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
- **Unknown 3.1: Scaling algorithm selection** (INCOMPLETE)
  - Planned approach: Curtis-Reid geometric mean scaling
  - Need to verify: Algorithm implementation, convergence, conditioning improvement

- **Unknown 3.2: Scaling application point** (INCOMPLETE)
  - Decision needed: Scale original NLP vs. scale KKT system
  - Need to verify: Which approach gives better PATH solver performance

- **Unknown 6.3: Scaling impact on tests** (INCOMPLETE - CRITICAL)
  - Existing tests must pass without --scale flag
  - Need to verify: Scaled and unscaled give equivalent solutions, no test breakage

**Checkpoint 2** (Day 6 - End of Day):
- Review all Day 4-6 deliverables (Est: 1h)
- Verify all features >= 80% implemented
- Verify Unknowns 3.1, 3.2, 4.2-4.4, 6.2-6.4 status
- Check test coverage >= 85%
- Confirm no critical bugs
- **Decision:** GO/NO-GO for Days 7-10, descoping if needed

---

### Day 7: Diagnostics + Developer Ergonomics (Part 2)

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

**Task 2: Implement Matrix Market Jacobian export** (Est: 2h)
- Export Jacobian in Matrix Market format
- Handle sparse structure
- Validate format (SciPy/MATLAB compatible)

**Task 3: Add CLI flags for diagnostics** (Est: 1h)
- Add --stats flag for statistics output
- Add --dump-jacobian <file> flag
- Integrate into main workflow

**Task 4: Configuration via pyproject.toml** (Est: 1.5h)
- Add pyproject.toml support for default options
- Support all CLI flags in config file
- Document configuration options

**Task 5: Structured logging with verbosity control** (Est: 1.5h)
- Add logging framework with levels
- Add --verbose and --quiet flags
- Log key transformation steps

**Task 6: Enhanced error messages - Phase 2** (Est: 1.5h)
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

---

### Day 8: PATH Solver Validation and Testing

#### Goals
- Validate all generated MCPs with PATH solver
- Test reformulated features (`min/max`, `abs`, fixed vars)
- Identify and document any PATH-specific issues
- Complete all Known Unknown verification

#### Main Tasks

**Task 1: Set up PATH solver test harness** (Est: 1.5h)
- Create PATH validation framework
- Set up test infrastructure
- Configure solver options

**Task 2: Run all golden files through PATH** (Est: 1.5h)
- Validate existing golden files
- Verify no regressions
- Document solve status

**Task 3: Test `min/max` reformulations with PATH** (Est: 2h)
- Test simple 2-argument min/max
- Test multi-argument cases
- Test nested cases (flattened)

**Task 4: Test smooth `abs` and fixed vars with PATH** (Est: 1.5h)
- Test abs() with smoothing enabled
- Test fixed variable problems
- Verify numerical stability and solution accuracy

**Task 5: Document PATH solver requirements and options** (Est: 1.5h)
- Document setup instructions
- Document recommended options
- Create troubleshooting guide

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
- **Unknown 2.4: PATH compatibility for non-smooth reformulations** (INCOMPLETE)
  - Verify PATH can handle min/max reformulations
  - Need to verify: Convergence characteristics, initial point sensitivity, solver robustness

- **Unknown 5.1: PATH behavior on nonlinear MCPs** (INCOMPLETE)
  - Need to verify: How PATH handles highly nonlinear KKT systems
  - Need to verify: When to apply scaling, when convergence fails

- **Unknown 5.2: Recommend PATH options** (INCOMPLETE)
  - Document default options, test problem-specific tuning
  - Need to verify: Which options improve convergence, recommended defaults for nlp2mcp

- **Unknown 5.3: PATH failure reporting** (INCOMPLETE)
  - Need to verify: How to parse PATH status codes, error messages, listing file output

- **Unknown 5.4: PATH initial point guidance** (INCOMPLETE - low priority)
  - Need to verify: Whether PATH default initialization sufficient, when user initial points needed

**Checkpoint 3** (Day 8 - End of Day):
- Review all deliverables (Est: 1h)
- Verify all features 100% implemented
- Verify all Known Unknowns resolved
- Verify all tests passing
- Verify PATH validation complete
- **Decision:** GO/EXTEND for final integration

---

### Day 9: Integration Testing, Documentation, and Examples

#### Goals
- Run comprehensive integration tests
- Update all documentation
- Regenerate golden files
- Create 10 mid-size example models
- Verify all acceptance criteria

#### Main Tasks

**Task 1: Run full test suite with all features enabled** (Est: 1.5h)
- Run all 650+ tests
- Verify no regressions
- Check test coverage >= 85%

**Task 2: Create 10 mid-size example models** (Est: 3h)
- Curate or create transport-style models
- Include indexed constraints and nonlinear costs
- Cover all Sprint 4 features ($include, Table, min/max, abs, x.fx, scaling)
- Validate all examples with GAMS and PATH

**Task 3: Update README.md with Sprint 4 features** (Est: 1.5h)
- Document $include support
- Document Table support
- Document min/max reformulation
- Document abs() handling
- Document fixed variables
- Document scaling (including byvar mode)
- Document diagnostics and developer ergonomics

**Task 4: Update technical documentation** (Est: 2h)
- Update KKT_ASSEMBLY.md with reformulation details
- Update GAMS_EMISSION.md with auxiliary variable handling
- Document scaling algorithm (all modes)
- Add troubleshooting guide
- Document configuration options

**Task 5: Regenerate all golden files with new features** (Est: 1h)
- Update golden files with new capabilities
- Add new golden files for Sprint 4 features
- Validate all golden files with GAMS

#### Deliverables
- All 650+ tests passing
- 10 mid-size example models with documentation
- Updated README.md with complete feature list
- Updated technical docs (KKT_ASSEMBLY.md, GAMS_EMISSION.md)
- New golden files with reformulations
- Configuration and logging documentation

#### Acceptance Criteria
- [ ] All tests pass (no xfail markers)
- [ ] Test coverage >= 85% for Sprint 4 code
- [ ] 10 mid-size examples created and validated
- [ ] All examples solve with PATH
- [ ] README.md accurate and complete
- [ ] Technical docs reflect all new features
- [ ] Golden files validate with GAMS
- [ ] All acceptance criteria from Days 1-8 met
- [ ] Configuration and logging documented

#### Integration Risks
- **Risk 1:** Documentation may be out of sync with code
  - *Mitigation:* Review docs against actual implementation
- **Risk 2:** Golden file regeneration may reveal hidden bugs
  - *Mitigation:* Fix any issues found, retest
- **Risk 3:** Creating 10 quality examples may take longer than estimated
  - *Mitigation:* Can use Day 10 buffer time if needed

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

**Risk 1: PATH Solver Not Available Until Day 7**
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

### Checkpoint 1 (Day 3)
- **Focus:** Early features scaffolded, preprocessing and tables working
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/NO-GO for Days 4-6
- **Time:** 1 hour

### Checkpoint 2 (Day 6)
- **Focus:** All features >= 80% complete, integration healthy, scaling working
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/NO-GO for Days 7-10, descoping if needed
- **Time:** 1 hour

### Checkpoint 3 (Day 8)
- **Focus:** Feature completeness, PATH validation, all unknowns resolved
- **Review:** Template from `docs/process/CHECKPOINT_TEMPLATES.md`
- **Decision:** GO/EXTEND for completion
- **Time:** 1 hour

---

## Known Unknowns Schedule

Sprint 4 Known Unknowns are documented in:
- `/Users/jeff/experiments/nlp2mcp/docs/planning/SPRINT_4/KNOWN_UNKNOWNS.md`
- `/Users/jeff/experiments/nlp2mcp/docs/planning/SPRINT_4/KNOWN_UNKNOWNS/SCHEDULE.md`

**Verification Status (as of 2025-11-01):**

**COMPLETE (10/23) - Prerequisites satisfied ✅:**
- Unknown 1.1: $include syntax and semantics
- Unknown 1.2: Table block syntax
- Unknown 1.3: Fixed variable semantics
- Unknown 1.4: Nested $include handling
- Unknown 1.5: Relative path resolution
- Unknown 2.1: min() reformulation
- Unknown 2.2: max() reformulation
- Unknown 2.3: abs() handling
- Unknown 4.1: Line breaking for GAMS emission
- Unknown 6.1: $include vs ModelIR preprocessing

**INCOMPLETE - TO BE VERIFIED (13/23):**

**Days 3-6 Verification:**
- Unknown 4.2: Auxiliary variable naming (Day 3-4)
- Unknown 4.3: Auxiliary constraints in Model (Day 4)
- Unknown 6.4: Auxiliary vars and IndexMapping (Day 4)
- Unknown 4.4: Emit fixed variables in MCP (Day 5)
- Unknown 6.2: Fixed vars in KKT (Day 5)
- Unknown 3.1: Scaling algorithm (Day 6)
- Unknown 3.2: Scaling application point (Day 6)
- Unknown 6.3: Scaling impact on tests (Day 6)

**Day 8 PATH Validation:**
- Unknown 2.4: PATH compatibility for reformulations
- Unknown 5.1: PATH nonlinearity handling
- Unknown 5.2: PATH options
- Unknown 5.3: PATH failure reporting
- Unknown 5.4: PATH initial points (low priority)

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
2. **Early Validation:** PATH setup on Day 7-8 (scheduled appropriately)
3. **Formal Checkpoints:** Days 3, 6, 8 with templates and decision points
4. **Test-Driven Development:** Write tests before/during implementation
5. **Incremental Integration:** Test each feature independently before combining
6. **Documentation as You Go:** Update docs daily, not just Day 9
7. **Developer Ergonomics:** Enhanced errors, config, logging throughout sprint

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

## Next Steps

1. **Before Day 1:** Complete all prep tasks (Task 1-9 from PREP_PLAN.md) - **10/23 unknowns already COMPLETE** ✅
2. **Day 1 Morning:** Review this plan, set up environment, verify tooling
3. **Day 1 Start:** Begin `$include` implementation per Day 1 plan above
4. **Daily:** Update progress, run tests, document findings
5. **Checkpoints:** Use templates, make GO/NO-GO decisions
6. **Day 10 End:** Sprint 4 retrospective, plan Sprint 5
