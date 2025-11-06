# Sprint 5 Plan: Hardening, Packaging, and Documentation

**Sprint Duration:** 10 days  
**Sprint Goal:** Ship a production-ready, packaged tool with comprehensive documentation  
**Status:** 📋 PLANNED  
**Created:** November 6, 2025

---

## Overview

### What Sprint 5 Accomplishes

Sprint 5 transforms nlp2mcp from a research tool to a production-ready system available on PyPI with comprehensive documentation. This sprint addresses all Sprint 4 Retrospective recommendations while adding the final polish needed for public release.

**Primary Deliverables:**
1. **Bug-Free Core** - Fix min/max reformulation bug blocking PATH validation
2. **Solver Validation** - Complete PATH solver testing with all reformulations
3. **Production Quality** - Large model testing, error recovery, memory optimization  
4. **Easy Installation** - PyPI package with automated releases
5. **User Documentation** - Tutorial, FAQ, troubleshooting guides

**Foundation:**
- Sprint 4 delivered 972 passing tests, 85%+ coverage
- All Sprint 5 prep tasks completed (Tasks 1-9)
- Large model test fixtures ready (250, 500, 1K variables)
- Known Unknowns researched (22 unknowns documented, 1 critical finding)

**Alignment with Sprint 4 Retrospective:**
- Priority 1-5 structure directly from Sprint 4 recommendations
- Checkpoint 0 completed (Task 9 - dependency verification)
- Process improvements integrated (research first, quality over quantity)
- External dependencies verified (GAMS/PATH licensing)

---

## Success Metrics

### Functional Goals (8 targets)

1. ✅ Min/max reformulation bug fixed
   - All 5 test cases from research doc pass
   - PATH solver solves reformulated MCPs
   - No "spurious variables" errors

2. ✅ PATH validation complete
   - All golden files solve (or documented failures)
   - Min/max, abs, fixed vars validated
   - Solver options documented

3. ✅ Large models tested
   - 250, 500, 1K variable models convert successfully
   - Performance within targets (see benchmarks)
   - Memory usage acceptable (<500MB peak)

4. ✅ Error recovery implemented
   - Graceful NaN/Inf handling
   - Better error messages for user mistakes
   - Model validation before processing

5. ✅ PyPI package published
   - `pip install nlp2mcp` works
   - CLI entry point functional
   - Tested on Python 3.10, 3.11, 3.12

6. ✅ Tutorial created
   - Step-by-step beginner guide
   - Examples with explanations
   - Integration with USER_GUIDE.md

7. ✅ FAQ documented
   - Common issues addressed
   - Troubleshooting steps
   - PATH solver help

8. ✅ Release automation
   - GitHub Actions for PyPI
   - Version bumping automated
   - Changelog generation

### Quality Metrics (6 targets)

1. ✅ All existing tests pass (972+ tests, 0 regressions)
2. ✅ Test coverage ≥ 85% for new Sprint 5 code
3. ✅ All Known Unknowns resolved or deferred with justification
4. ✅ mypy: 0 errors, ruff: 0 errors, black: 100% formatted
5. ✅ PATH validation: 90%+ success rate on golden files
6. ✅ PyPI package: Clean install on fresh virtual environment

### Integration Metrics (4 targets)

1. ✅ No API breakage from Sprints 1-4
2. ✅ Generated MCPs compile in GAMS
3. ✅ PATH solver solves generated MCPs
4. ✅ Large model fixtures pass all quality tests

---

## Day-by-Day Plan

### DAY 1: Min/Max Bug Fix - Research & Design

**Priority:** 1 (Critical Bug Fix)  
**Duration:** 8 hours  
**Dependencies:** Sprint 4 code, Unknown 1.1 DISPROVEN finding

#### Goals
- Understand min/max reformulation failure root cause
- Design fix based on Unknown 1.1 findings (Strategy 2 INFEASIBLE, need alternative)
- Create comprehensive test plan
- Begin implementation of KKT assembly fix

#### Tasks

**Task 1.1: Review Unknown 1.1 DISPROVEN Analysis** (1 hour)
- **Related Unknown:** Unknown 1.1 (DISPROVEN)
  - **Finding:** Strategy 2 (Direct Constraints) is INFEASIBLE
  - **Summary:** Converting `obj = min(x,y)` to constraints `obj ≤ x, obj ≤ y` fails because these are inequalities, creating slack variables that don't match KKT structure
  - **Key Architecture:** Must use auxiliary variable approach (Strategy 1) with proper KKT assembly
  - **Status:** ✅ COMPLETE
- Read `docs/research/minmax_objective_reformulation.md` full analysis
- Understand why Strategy 2 fails (inequality → slack → KKT mismatch)
- Confirm Strategy 1 (Auxiliary Variables) is correct approach
- Acceptance: Clear understanding of correct reformulation strategy

**Task 1.2: Design KKT Assembly Fix** (2 hours)
- **Related Unknowns:**
  - Unknown 1.2: How to detect if min/max defines objective variable?
    - **Finding:** Need to analyze ModelIR.objective_equ to find which equation defines objvar
    - **Key Architecture:** Parser already identifies objective_equ, check if it contains min/max operations
    - **Status:** 🔍 INCOMPLETE
  - Unknown 1.4: What KKT assembly changes needed?
    - **Finding:** Stationarity equations must include multipliers for ALL equality constraints, including auxiliary ones
    - **Key Architecture:** Loop over all normalized equations (not just original), add Jacobian terms to stationarity
    - **Status:** 🔍 INCOMPLETE
- Review current KKT assembly in `src/kkt/assemble.py`
- Identify where auxiliary constraint multipliers are missing
- Design fix to include all equality constraint multipliers
- Create architecture diagram for fix
- Acceptance: Written design doc with code locations and changes

**Task 1.3: Create Test Cases** (1 hour)
- Implement 5 test cases from research doc:
  - Test 1: Simple min in objective (currently failing)
  - Test 2: Direct min objective
  - Test 3: Min in constraint (should work)
  - Test 4: Nested min/max
  - Test 5: Max in maximization
- Write test files in `tests/unit/kkt/test_minmax_fix.py`
- Mark as xfail with issue reference
- Acceptance: 5 xfailing tests committed

**Task 1.4: Implement Detection Logic** (2 hours)
- **Related Unknown:** Unknown 1.2 (detection algorithm)
- Implement function to detect if min/max defines objective
- Check if ModelIR.objective_equ contains min/max AST nodes
- Handle chains (obj=z, z=min(x,y))
- Add unit tests for detection
- Acceptance: Detection logic tested, all unit tests pass

**Task 1.5: Begin KKT Assembly Changes** (2 hours)
- **Related Unknown:** Unknown 1.4 (KKT assembly changes)
- Modify `src/kkt/assemble.py` stationarity equation generation
- Include auxiliary constraint multipliers
- Add debug logging to trace which constraints are included
- Acceptance: Initial implementation compiles, ready for Day 2 testing

#### Deliverables
- [ ] Design document for KKT assembly fix
- [ ] 5 test cases (xfailing) committed
- [ ] Detection logic implemented and tested
- [ ] KKT assembly changes scaffolded

#### Acceptance Criteria
- [ ] All 5 test cases written (xfailing is OK)
- [ ] Detection logic has 100% unit test coverage
- [ ] KKT assembly changes compile without errors
- [ ] Design doc reviewed and approved
- [ ] No regressions in existing tests

#### Integration Risks
- **Risk:** Changes to KKT assembly could break existing reformulations
- **Mitigation:** Run full test suite after each change
- **Risk:** Detection logic might miss edge cases
- **Mitigation:** Comprehensive test cases from research doc

---

### DAY 2: Min/Max Bug Fix - Implementation & Testing

**Priority:** 1 (Critical Bug Fix)  
**Duration:** 8 hours  
**Dependencies:** Day 1 design and scaffolding

#### Goals
- Complete KKT assembly fix implementation
- Make all 5 test cases pass
- Validate with PATH solver
- Remove xfail markers

#### Tasks

**Task 2.1: Complete KKT Assembly Implementation** (3 hours)
- **Related Unknown:** Unknown 1.4 (KKT assembly)
- Finish stationarity equation generation
- Ensure all normalized equations included (original + auxiliary)
- Handle indexed equations properly
- Add comprehensive inline documentation
- Acceptance: KKT assembly generates correct equations for min/max cases

**Task 2.2: Debug Test Failures** (2 hours)
- Run 5 test cases from Day 1
- Debug failures one by one
- Fix issues in reformulation or KKT assembly
- Verify generated MCP syntax is correct
- Acceptance: All 5 test cases generate valid GAMS MCP code

**Task 2.3: PATH Solver Validation** (2 hours)
- **Related Unknown:** Unknown 1.5: PATH solver options tuning?
  - **Finding:** PATH has many options (presolve, crash, lemke_start, etc.)
  - **Summary:** Default options usually sufficient, may need `lemke_start=advanced` for difficult problems
  - **Status:** 🔍 INCOMPLETE - Test during validation
- Run generated MCPs through GAMS PATH solver
- Check Model Status: 1 (Optimal) or 2 (Locally Optimal) acceptable
- Investigate any failures
- Tune PATH options if needed
- Acceptance: All 5 test cases solve successfully with PATH

**Task 2.4: Remove xfail Markers** (0.5 hours)
- Remove xfail from passing tests
- Update test documentation
- Add comments explaining what was fixed
- Acceptance: All tests pass without xfail

**Task 2.5: Regression Testing** (0.5 hours)
- Run full test suite
- Check for any regressions
- Fix any broken tests
- Acceptance: 972+ tests passing, 0 regressions

#### Deliverables
- [ ] KKT assembly fix complete
- [ ] All 5 min/max test cases passing
- [ ] PATH solver validation successful
- [ ] xfail markers removed
- [ ] Full test suite passing

#### Acceptance Criteria
- [ ] All 5 test cases pass
- [ ] PATH solver solves all 5 reformulated MCPs
- [ ] No spurious variable errors in GAMS
- [ ] Full test suite passes (972+ tests)
- [ ] Code coverage ≥ 85% for new code
- [ ] mypy 0 errors, ruff 0 errors

#### Integration Risks
- **Risk:** KKT changes might break non-min/max models
- **Mitigation:** Full regression test suite
- **Risk:** PATH solver might not converge
- **Mitigation:** Research Unknown 1.5 findings, tune options

---

### DAY 3: PATH Validation + Checkpoint 1

**Priority:** 2 (PATH Validation)  
**Duration:** 7 hours work + 1 hour checkpoint  
**Dependencies:** Day 2 min/max fix complete

#### Goals
- Execute PATH validation test suite
- Investigate and resolve failures
- Document PATH solver usage
- **Checkpoint 1:** Formal mid-sprint review

#### Tasks

**Task 3.1: Execute PATH Validation Suite** (2 hours)
- **Related Unknowns:**
  - Unknown 2.1: Why do bounds_nlp and nonlinear_mix fail with Model Status 5?
    - **Finding:** Locally infeasible = KKT system has no solution at starting point
    - **Summary:** May indicate modeling issues, needs investigation
    - **Status:** 🔍 INCOMPLETE - Test after Priority 1 implementation
  - Unknown 2.2: PATH solver options to document?
    - **Finding:** Key options: `presolve`, `crash`, `lemke_start`, `convergence_tolerance`
    - **Status:** 🔍 INCOMPLETE - Document during Priority 2
- Run `tests/validation/test_path_solver.py`
- Run `tests/validation/test_path_solver_minmax.py` (should pass after Day 2 fix)
- Collect results: Model Status, Solve Status, residuals
- Identify failures (Model Status 4, 5)
- Acceptance: Complete results documented

**Task 3.2: Investigate Failures** (2 hours)
- **Related Unknown:** Unknown 2.1 (Model Status 5 failures)
- For each failure, analyze:
  - MCP formulation (check syntax)
  - KKT system (check for inconsistencies)
  - Starting point (check bounds)
  - PATH options (try different settings)
- Document root causes
- Determine if failure is expected (infeasible model) or bug
- Acceptance: All failures explained

**Task 3.3: Document PATH Solver** (2 hours)
- **Related Unknowns:**
  - Unknown 2.2 (PATH options)
  - Unknown 2.3: How to interpret PATH solution quality?
    - **Finding:** Model Status 1=optimal, 2=locally optimal (both good), 4=infeasible, 5=locally infeasible
    - **Summary:** Residual < 1e-6 is excellent, < 1e-4 is good
    - **Status:** 🔍 INCOMPLETE - Can do during Priority 2
- Create `docs/PATH_SOLVER.md` with:
  - Installation instructions (GAMS setup)
  - How to run PATH on generated MCPs
  - Solver options and when to use them
  - Interpreting results (Model/Solve Status)
  - Troubleshooting common issues
- Add PATH section to USER_GUIDE.md
- Acceptance: PATH documentation complete and reviewed

**Task 3.4: Update Test Suite** (1 hour)
- Mark expected failures with proper skip/xfail reasons
- Add solver options to difficult test cases
- Document why certain models are expected to fail
- Acceptance: Test suite stable and documented

#### Checkpoint 1: Day 3 Formal Review (1 hour)

**Following:** `docs/process/CHECKPOINT_TEMPLATES.md` - Checkpoint 1

**Review Questions:**
1. **Feature Completeness**
   - Is min/max fix complete and tested?
   - Is PATH validation framework functional?
   - Are any features not yet started for Days 4-10?

2. **Known Unknowns Status**
   - Have any new unknowns been discovered?
   - Are Unknowns 1.1-1.5, 2.1-2.3 resolved or on track?
   - Any blockers for Days 4-10?

3. **Test Coverage**
   - Are all new functions tested?
   - Is coverage ≥ 85% for Days 1-3 code?
   - Any untestable code?

4. **Code Quality**
   - mypy passing?
   - ruff passing?
   - black formatted?
   - Any tech debt accumulating?

**Artifacts to Review:**
- Test output (pytest)
- Type checking (mypy)
- Linting (ruff)
- Coverage report (pytest --cov)
- PATH validation results
- Git commits Days 1-3

**Decision Point:**
- **GO:** Days 1-3 goals met, proceed to production hardening (Days 4-6)
- **NO-GO:** Critical issues found, create recovery plan

#### Deliverables
- [ ] PATH validation results documented
- [ ] PATH solver guide created
- [ ] Test suite updated with proper skips/xfails
- [ ] Checkpoint 1 report completed

#### Acceptance Criteria
- [ ] PATH validation suite runs successfully (90%+ pass rate)
- [ ] All failures explained and documented
- [ ] PATH_SOLVER.md created and reviewed
- [ ] Checkpoint 1 PASS (all criteria met)
- [ ] No blockers for Days 4-6

#### Integration Risks
- **Risk:** PATH solver might require options we don't support
- **Mitigation:** Document limitations, add to Known Unknowns
- **Risk:** Some models might be fundamentally infeasible
- **Mitigation:** Document expected failures, mark tests appropriately

#### Follow-On Research Items
- **Unknown 2.4:** Should PATH validation be in CI/CD?
  - **Priority:** Low
  - **Status:** 🔍 INCOMPLETE - Process decision
  - **Research Needed:** Evaluate GitHub Actions with GAMS licensing
  - **Deadline:** Before Sprint 6 planning

---

### DAY 4: Production Hardening - Error Recovery

**Priority:** 3.1 (Error Recovery)  
**Duration:** 8 hours  
**Dependencies:** None (independent work)

#### Goals
- Implement graceful handling of numerical issues
- Improve error messages for user mistakes
- Add model validation before KKT assembly
- Create comprehensive error recovery tests

#### Tasks

**Task 4.1: Numerical Issue Handling** (2 hours)
- **Related Unknown:** Unknown 3.4: How to handle NaN, Inf?
  - **Finding:** Should detect in evaluator, provide clear error with source location
  - **Summary:** Check after each operation in AD, raise NumericalError with context
  - **Status:** 🔍 INCOMPLETE - Medium priority
- Detect NaN, Inf in expression evaluator
- Add try/except around numerical operations
- Provide clear error messages with source context
- Add recovery suggestions
- Acceptance: NaN/Inf detected and reported clearly

**Task 4.2: User Error Detection** (2 hours)
- **Related Unknown:** Unknown 3.5: Should we add model validation pass?
  - **Finding:** Yes, catch common errors early (undefined vars, circular deps, type mismatches)
  - **Summary:** Add validation pass before KKT assembly
  - **Status:** 🔍 INCOMPLETE - Important for production
- Common mistakes to detect:
  - Undefined variables referenced
  - Circular dependencies
  - Type mismatches (scalar vs indexed)
  - Missing objective equation
  - Unbounded variables in nonlinear terms
- Create validation pass in `src/ir/validate.py`
- Acceptance: Common errors caught before KKT assembly

**Task 4.3: Better Error Messages** (2 hours)
- Enhance error messages with:
  - Source file location (line, column)
  - Context (surrounding code)
  - Suggestions for fixes
  - Links to documentation
- Update error classes in `src/utils/errors.py`
- Add examples to error messages
- Acceptance: Error messages are helpful and actionable

**Task 4.4: Error Recovery Tests** (2 hours)
- Create test suite for error conditions
- Test each error class
- Verify error messages are clear
- Test recovery suggestions actually work
- Create `tests/integration/test_error_recovery.py`
- Acceptance: 20+ error recovery tests passing

#### Deliverables
- [ ] NaN/Inf detection implemented
- [ ] Model validation pass created
- [ ] Error messages enhanced
- [ ] Error recovery test suite (20+ tests)

#### Acceptance Criteria
- [ ] All numerical issues detected and reported
- [ ] Model validation catches common errors
- [ ] Error messages include source location and suggestions
- [ ] 20+ error recovery tests passing
- [ ] No regressions in existing tests
- [ ] Code coverage ≥ 85%

#### Integration Risks
- **Risk:** Validation might reject valid models
- **Mitigation:** Conservative validation, allow opt-out flag
- **Risk:** Error detection might slow down conversion
- **Mitigation:** Performance profiling, optimize hot paths

---

### DAY 5: Production Hardening - Large Models & Memory

**Priority:** 3.2, 3.3 (Large Models, Memory)  
**Duration:** 8 hours  
**Dependencies:** Task 8 large model fixtures (250, 500, 1K vars)

#### Goals
- Test nlp2mcp with large models (250, 500, 1K variables)
- Profile memory usage and optimize
- Establish performance baselines
- Create performance benchmarks

#### Tasks

**Task 5.1: Large Model Testing** (2 hours)
- **Related Unknown:** Unknown 3.1: Performance targets?
  - **Finding:** 1K vars in <90s (measured: 45.9s ✅), 5K vars in <5min
  - **Summary:** O(n²) scaling expected (Jacobian computation), track throughput
  - **Status:** ✅ COMPLETE (from Task 8)
- Run nlp2mcp on Task 8 fixtures:
  - resource_allocation_250.gms (250 vars)
  - resource_allocation_500.gms (500 vars)
  - resource_allocation_1k.gms (1000 vars)
- Verify conversion succeeds
- Measure conversion time
- Check output correctness (GAMS compilation)
- Acceptance: All 3 models convert successfully

**Task 5.2: Performance Profiling** (2 hours)
- Profile each large model conversion
- Identify hotspots (cProfile, line_profiler)
- Measure time by phase:
  - Parsing
  - Normalization
  - Derivative computation
  - KKT assembly
  - Emission
- Document bottlenecks
- Acceptance: Performance profile documented

**Task 5.3: Memory Profiling** (2 hours)
- **Related Unknown:** Unknown 3.3: Memory optimization techniques?
  - **Finding:** Use sparse matrices (scipy.sparse), avoid full Jacobian materialization, stream emission
  - **Summary:** Current approach uses sparse AD, should be memory-efficient
  - **Status:** 🔍 INCOMPLETE - Can refine during Priority 3
- Profile memory usage (memory_profiler)
- Check for memory leaks
- Identify large data structures
- Optimize if needed:
  - Use generators for large iterations
  - Release memory after each phase
  - Sparse matrix operations
- Acceptance: Memory usage < 500MB for 1K var model

**Task 5.4: Performance Benchmarks** (2 hours)
- Create benchmark suite in `tests/benchmarks/test_large_models.py`
- Benchmark each phase separately
- Set performance targets (from Unknown 3.1):
  - 250 vars: < 10s
  - 500 vars: < 30s
  - 1K vars: < 90s
- Add to CI/CD as optional slow tests
- Acceptance: Benchmarks created and passing

#### Deliverables
- [ ] Large model test results documented
- [ ] Performance profile analysis
- [ ] Memory profile analysis
- [ ] Performance benchmark suite

#### Acceptance Criteria
- [ ] All 3 large models (250, 500, 1K) convert successfully
- [ ] Conversion times within targets
- [ ] Memory usage < 500MB peak for 1K model
- [ ] Performance benchmarks created and passing
- [ ] No performance regressions vs Sprint 4

#### Integration Risks
- **Risk:** Large models might expose parser bugs
- **Mitigation:** Progressive testing (250 → 500 → 1K)
- **Risk:** Memory usage might exceed limits
- **Mitigation:** Profiling and optimization, sparse matrices

---

### DAY 6: Production Hardening - Edge Cases + Checkpoint 2

**Priority:** 3 (Edge Cases)  
**Duration:** 7 hours work + 1 hour checkpoint  
**Dependencies:** Days 4-5 hardening work

#### Goals
- Implement comprehensive edge case testing
- Validate robustness with unusual inputs
- Document limitations and known issues
- **Checkpoint 2:** Mid-sprint progress review

#### Tasks

**Task 6.1: Edge Case Test Suite** (3 hours)
- **Related Unknown:** Unknown 3.2: Which edge cases are most critical?
  - **Finding:** Extreme bounds, degenerate constraints, all-zero Jacobians, circular references, empty sets
  - **Summary:** 5 critical categories, 4+ tests each = 20+ edge case tests
  - **Status:** ✅ COMPLETE (research done in prep phase)
- Implement edge cases from Unknown 3.2:
  - **Extreme bounds:** x.lo = -1e20, x.up = 1e20
  - **Degenerate constraints:** 0 = 0, x = x
  - **All-zero Jacobians:** constant equations
  - **Circular references:** x = y, y = x
  - **Empty sets:** i = {} (empty set)
- Create `tests/edge_cases/test_production_edge_cases.py`
- Each edge case should either:
  - Convert successfully (robustness), or
  - Fail with clear error message (validation)
- Acceptance: 20+ edge case tests implemented

**Task 6.2: Boundary Condition Testing** (2 hours)
- Test limits of each component:
  - Maximum variables (10K+)
  - Maximum constraints (10K+)
  - Maximum nonzeros in Jacobian
  - Deeply nested expressions (20+ levels)
  - Long variable/equation names (100+ chars)
- Document limits in USER_GUIDE.md
- Acceptance: Boundary conditions tested and documented

**Task 6.3: Error Message Validation** (1 hour)
- Review all error messages from edge case tests
- Ensure they're clear and actionable
- Add missing error handling
- Update error message catalog
- Acceptance: All error messages reviewed and improved

**Task 6.4: Limitations Documentation** (1 hour)
- Create `docs/LIMITATIONS.md` with:
  - Known issues (from edge case testing)
  - Parser limitations (from GAMS subset)
  - Solver limitations (PATH requirements)
  - Performance limits (model size)
  - Unsupported features
- Link from README.md and USER_GUIDE.md
- Acceptance: Limitations clearly documented

#### Checkpoint 2: Day 6 Formal Review (1 hour)

**Following:** `docs/process/CHECKPOINT_TEMPLATES.md` - Checkpoint 2

**Review Questions:**
1. **Progress vs Plan**
   - Days 1-2: Min/max fix complete? ✅/❌
   - Day 3: PATH validation complete? ✅/❌
   - Days 4-6: Hardening complete? ✅/❌
   - Are we on track for Days 7-10?

2. **Quality Metrics**
   - Test count: 972+ ?
   - Coverage: ≥ 85% ?
   - Tech debt: Any accumulating?
   - Performance: Targets met?

3. **Scope Adjustments Needed?**
   - Any features to descope?
   - Any features to add?
   - Timeline adjustments needed?

4. **Days 7-10 Readiness**
   - PyPI packaging blockers?
   - Documentation blockers?
   - Any unknowns discovered?

**Artifacts to Review:**
- Test results (pytest)
- Coverage report
- Performance benchmarks
- Edge case test results
- Git commits Days 4-6

**Decision Point:**
- **GO:** Production hardening complete, proceed to packaging (Days 7-8)
- **NO-GO:** Critical gaps, create recovery plan

#### Deliverables
- [ ] Edge case test suite (20+ tests)
- [ ] Boundary conditions tested
- [ ] LIMITATIONS.md created
- [ ] Checkpoint 2 report completed

#### Acceptance Criteria
- [ ] 20+ edge case tests passing (or failing gracefully)
- [ ] Boundary conditions documented
- [ ] All error messages clear and actionable
- [ ] LIMITATIONS.md complete
- [ ] Checkpoint 2 PASS
- [ ] No blockers for Days 7-8

#### Integration Risks
- **Risk:** Edge cases might expose fundamental issues
- **Mitigation:** Systematic testing, clear error messages
- **Risk:** Limitations might be too restrictive
- **Mitigation:** Document, plan for future sprints

#### Follow-On Research Items
- **Unknown 3.3:** Memory optimization techniques
  - **Priority:** Medium
  - **Status:** 🔍 INCOMPLETE
  - **Research Needed:** If Day 5 profiling shows issues
  - **Deadline:** Before Day 7 (if memory exceeds limits)

---

### DAY 7: PyPI Packaging - Configuration & Build

**Priority:** 4 (PyPI Packaging)  
**Duration:** 8 hours  
**Dependencies:** None (independent work)

#### Goals
- Configure PyPI package metadata
- Set up build system
- Create installable wheel
- Test local installation

#### Tasks

**Task 7.1: Choose Build System** (1 hour)
- **Related Unknown:** Unknown 4.1: setuptools vs hatch vs flit?
  - **Finding:** Use `hatch` - modern, PEP 517 compliant, good dev workflow
  - **Summary:** Hatch recommended for new projects, cleaner than setuptools
  - **Status:** 🔍 INCOMPLETE - Need to decide before Priority 4
- Evaluate options:
  - setuptools: Traditional, widely used
  - hatch: Modern, recommended for new projects
  - flit: Simpler, less features
- Decision criteria:
  - PEP 517/518 compliance
  - Development workflow
  - Documentation quality
- Make decision and document rationale
- Acceptance: Build system chosen and justified

**Task 7.2: Configure pyproject.toml** (2 hours)
- **Related Unknown:** Unknown 4.2: Required PyPI metadata?
  - **Finding:** name, version, description, authors, license, classifiers, dependencies
  - **Summary:** Follow PEP 621, add keywords for discoverability
  - **Status:** 🔍 INCOMPLETE - Easy to add during Priority 4
- Add package metadata:
  - Name: nlp2mcp
  - Version: 0.4.0 (semantic versioning)
  - Description
  - Authors, license
  - Keywords: GAMS, NLP, MCP, optimization, KKT
  - Classifiers (see Unknown 4.2)
  - URLs (homepage, repository, bug tracker)
- Add dependencies:
  - scipy, sympy, lark, numpy
  - Version constraints
- Add optional dependencies (dev, docs, test)
- Acceptance: pyproject.toml complete and valid

**Task 7.3: Configure Entry Points** (1 hour)
- Set up CLI entry point:
  - Command: `nlp2mcp`
  - Module: `src.cli:main`
- Test entry point configuration
- Verify help text and version
- Acceptance: Entry point configured correctly

**Task 7.4: Build Wheel** (1 hour)
- Install build tools: `pip install build`
- Build wheel: `python -m build`
- Inspect wheel contents
- Verify all files included
- Check wheel size (should be < 1MB)
- Acceptance: Wheel builds successfully

**Task 7.5: Test Local Installation** (2 hours)
- Create fresh virtual environment
- Install from wheel: `pip install dist/*.whl`
- Test CLI: `nlp2mcp --help`
- Test conversion: Run on example models
- Verify all dependencies install
- Test uninstall: `pip uninstall nlp2mcp`
- Acceptance: Package installs and works correctly

**Task 7.6: Multi-Platform Testing** (1 hour)
- **Related Unknown:** Unknown 4.3: How to test multi-platform?
  - **Finding:** Use `tox` with different Python versions locally, GitHub Actions for OS matrix
  - **Summary:** Test Python 3.10, 3.11, 3.12 locally, defer full CI matrix to Day 8
  - **Status:** 🔍 INCOMPLETE - Practical decision
- Test on available platforms:
  - macOS (local)
  - Python 3.10, 3.11, 3.12
- Document platform-specific issues
- Acceptance: Package works on tested platforms

#### Deliverables
- [ ] pyproject.toml configured
- [ ] Wheel built successfully
- [ ] Local installation tested
- [ ] Multi-platform test results

#### Acceptance Criteria
- [ ] Build system chosen and configured
- [ ] Wheel builds without errors
- [ ] Package installs from wheel
- [ ] CLI works after installation
- [ ] All dependencies install correctly
- [ ] Tested on Python 3.10, 3.11, 3.12

#### Integration Risks
- **Risk:** Missing dependencies in package
- **Mitigation:** Fresh venv testing
- **Risk:** Entry point might not work
- **Mitigation:** Test immediately after build

---

### DAY 8: PyPI Packaging - Release Automation + Checkpoint 3

**Priority:** 4 (Release Automation)  
**Duration:** 7 hours work + 1 hour checkpoint  
**Dependencies:** Day 7 package build

#### Goals
- Create GitHub Actions workflow for PyPI
- Publish to TestPyPI
- Test installation from TestPyPI
- **Checkpoint 3:** Pre-completion review

#### Tasks

**Task 8.1: Version Numbering** (0.5 hours)
- **Related Unknown:** Unknown 4.4: Version numbering for 1.0.0 release?
  - **Finding:** Start at 0.4.0 (Sprint 5), increment to 1.0.0 when production-ready
  - **Summary:** Semantic versioning: 0.4.0 → 0.5.0 → ... → 1.0.0
  - **Status:** 🔍 INCOMPLETE - Practical decision
- Decide version for Sprint 5 release: 0.4.0
- Plan path to 1.0.0:
  - 0.4.0: Sprint 5 (packaging + docs)
  - 0.5.0: Bug fixes and polish
  - 1.0.0: Stable release
- Document versioning scheme
- Acceptance: Version numbering decided

**Task 8.2: GitHub Actions Workflow** (2 hours)
- Create `.github/workflows/publish-pypi.yml`
- Trigger on: git tags (v*)
- Steps:
  - Checkout code
  - Set up Python
  - Install build tools
  - Run tests
  - Build wheel
  - Publish to PyPI (using PYPI_TOKEN secret)
- Test workflow on branch (without publish)
- Acceptance: Workflow configured and tested

**Task 8.3: Publish to TestPyPI** (1 hour)
- Create TestPyPI account if needed
- Configure API token
- Publish package: `twine upload --repository testpypi dist/*`
- Verify package appears on TestPyPI
- Acceptance: Package on TestPyPI

**Task 8.4: Test Installation from TestPyPI** (1 hour)
- Fresh virtual environment
- Install from TestPyPI:
  ```bash
  pip install --index-url https://test.pypi.org/simple/ nlp2mcp
  ```
- Test CLI and library
- Verify dependencies install
- Document any issues
- Acceptance: Package installs from TestPyPI

**Task 8.5: Release Documentation** (1 hour)
- Create `RELEASING.md` with:
  - How to create a release
  - Version bumping process
  - Changelog update process
  - GitHub Actions workflow
  - Testing checklist
- Add release checklist template
- Acceptance: Release process documented

**Task 8.6: Update README Installation** (0.5 hours)
- Add PyPI installation instructions
- Update quick start with pip install
- Add badge for PyPI version
- Test instructions work
- Acceptance: README updated

#### Checkpoint 3: Day 8 Formal Review (1 hour)

**Following:** `docs/process/CHECKPOINT_TEMPLATES.md` - Checkpoint 3

**Review Questions:**
1. **Days 1-8 Completeness**
   - All priorities 1-4 complete? ✅/❌
   - Any deferred work?
   - Quality metrics met?

2. **Days 9-10 Readiness**
   - Blockers for documentation?
   - All features to document ready?
   - Tutorial topics clear?

3. **Release Readiness**
   - PyPI package functional?
   - All tests passing?
   - Documentation ready for polish?

4. **Sprint 5 Success Metrics**
   - 8/8 functional goals met?
   - 6/6 quality metrics met?
   - 4/4 integration metrics met?

**Artifacts to Review:**
- PyPI package (TestPyPI)
- GitHub Actions workflow
- Full test suite results
- Coverage report
- All deliverables Days 1-8

**Decision Point:**
- **GO:** Days 1-8 complete, proceed to documentation (Days 9-10)
- **NO-GO:** Critical issues, adjust Day 10 scope

#### Deliverables
- [ ] GitHub Actions workflow for PyPI
- [ ] Package on TestPyPI
- [ ] Installation tested from TestPyPI
- [ ] RELEASING.md created
- [ ] README updated
- [ ] Checkpoint 3 report completed

#### Acceptance Criteria
- [ ] Workflow runs successfully
- [ ] Package installs from TestPyPI
- [ ] All installation instructions tested
- [ ] RELEASING.md complete
- [ ] Checkpoint 3 PASS
- [ ] No blockers for Days 9-10

#### Integration Risks
- **Risk:** PyPI upload might fail
- **Mitigation:** Test with TestPyPI first
- **Risk:** Workflow might have permission issues
- **Mitigation:** Test with dummy package first

---

### DAY 9: Documentation - Tutorial & FAQ

**Priority:** 5 (Documentation)  
**Duration:** 8 hours  
**Dependencies:** All features complete (Days 1-8)

#### Goals
- Create comprehensive beginner tutorial
- Build FAQ from common issues
- Enhance troubleshooting guide
- Integrate with existing USER_GUIDE.md

#### Tasks

**Task 9.1: Tutorial Planning** (1 hour)
- **Related Unknown:** Unknown 5.2: Most critical tutorial topics?
  - **Finding:** Installation, first example, PATH validation, troubleshooting, advanced features
  - **Summary:** Step-by-step guide with complete examples
  - **Status:** 🔍 INCOMPLETE - Need to decide before Priority 5
- Outline tutorial sections:
  1. Installation (pip install)
  2. First MCP (simple example)
  3. Understanding output
  4. PATH solver integration
  5. Common issues
  6. Advanced features
- Identify examples to include
- Plan diagrams/visualizations
- Acceptance: Tutorial outline complete

**Task 9.2: Write Tutorial** (4 hours)
- Create `docs/TUTORIAL.md`
- Write each section step-by-step
- Include complete runnable examples
- Add screenshots/diagrams
- Explain concepts clearly
- Link to USER_GUIDE.md for details
- Test all examples work
- Acceptance: Tutorial complete and tested

**Task 9.3: Build FAQ** (2 hours)
- Collect common questions from:
  - Sprint 4 testing experience
  - Edge case testing (Day 6)
  - GitHub issues
  - User guide feedback
- Organize by category:
  - Installation issues
  - Conversion errors
  - PATH solver issues
  - Performance questions
  - Feature requests
- Write clear Q&A format
- Link to relevant docs
- Create `docs/FAQ.md`
- Acceptance: FAQ created with 20+ Q&As

**Task 9.4: Troubleshooting Guide** (1 hour)
- **Related Unknown:** Unknown 5.3: Troubleshooting guide detail level?
  - **Finding:** Problem → Diagnosis → Solution format, include error message examples
  - **Summary:** Cover common errors, PATH issues, performance problems
  - **Status:** 🔍 INCOMPLETE - Can refine during Priority 5
- Enhance `docs/TROUBLESHOOTING.md`
- Add problem → solution sections
- Include error message examples
- Add diagnostic steps
- Link to FAQ and USER_GUIDE
- Acceptance: Troubleshooting guide comprehensive

#### Deliverables
- [ ] TUTORIAL.md created
- [ ] FAQ.md created (20+ Q&As)
- [ ] TROUBLESHOOTING.md enhanced
- [ ] All examples tested

#### Acceptance Criteria
- [ ] Tutorial complete with tested examples
- [ ] FAQ has 20+ questions answered
- [ ] Troubleshooting guide covers common issues
- [ ] All documentation cross-linked
- [ ] No broken links
- [ ] Examples run successfully

#### Integration Risks
- **Risk:** Tutorial examples might not work
- **Mitigation:** Test every example before committing
- **Risk:** FAQ might miss important questions
- **Mitigation:** Review all error messages from Days 1-8

#### Follow-On Research Items
- **Unknown 5.1:** Sphinx vs MkDocs for API documentation?
  - **Priority:** Low
  - **Status:** 🔍 INCOMPLETE
  - **Research Needed:** For future API reference site
  - **Deadline:** Sprint 6 planning

- **Unknown 5.4:** API reference detail level?
  - **Priority:** Low
  - **Status:** 🔍 INCOMPLETE
  - **Research Needed:** Public API only vs full internals
  - **Deadline:** Sprint 6 planning

---

### DAY 10: Polish & Buffer

**Priority:** Buffer (Contingency)  
**Duration:** 8 hours  
**Dependencies:** Days 1-9 complete

#### Goals
- Address any incomplete items from Days 1-9
- Final quality pass on all deliverables
- Prepare Sprint 5 retrospective
- Close out sprint cleanly

#### Tasks

**Task 10.1: Incomplete Work from Days 1-9** (4 hours)
- Review all acceptance criteria from Days 1-9
- Complete any incomplete items
- Fix any failing tests
- Address any documentation gaps
- Priority order:
  1. Critical: Min/max fix, PATH validation
  2. High: PyPI package, tutorial
  3. Medium: Edge cases, FAQ
  4. Low: Nice-to-have polish
- Acceptance: All critical/high items complete

**Task 10.2: Final Quality Pass** (2 hours)
- Run full test suite one final time
- Check code coverage (target: ≥ 85%)
- Run mypy, ruff, black
- Review all error messages
- Check documentation for typos
- Verify all links work
- Test package installation
- Acceptance: All quality checks pass

**Task 10.3: Sprint 5 Retrospective Prep** (1 hour)
- Collect metrics:
  - Test count (target: 1000+)
  - Coverage percentage
  - Performance benchmarks
  - PyPI package stats
- Document what went well
- Document what could improve
- Identify action items for Sprint 6
- Draft retrospective document
- Acceptance: Retrospective prep complete

**Task 10.4: Final Deliverables Review** (1 hour)
- Check all deliverables from PLAN_ORIGINAL.md:
  - Min/max fix ✅
  - PATH validation ✅
  - Production hardening ✅
  - PyPI package ✅
  - Documentation ✅
- Verify all acceptance criteria met
- Create completion checklist
- Acceptance: All deliverables verified

#### Deliverables
- [ ] All Days 1-9 work complete
- [ ] Quality checks passing
- [ ] Retrospective prep done
- [ ] Sprint 5 complete

#### Acceptance Criteria
- [ ] All critical and high priority items complete
- [ ] All tests passing (1000+ tests)
- [ ] Code coverage ≥ 85%
- [ ] mypy 0 errors, ruff 0 errors
- [ ] PyPI package functional
- [ ] Documentation complete
- [ ] Ready for Sprint 5 retrospective

#### Integration Risks
- **Risk:** Unexpected issues discovered on Day 10
- **Mitigation:** Buffer day allows time to address
- **Risk:** Some nice-to-haves might not fit in time
- **Mitigation:** Clear prioritization, defer to Sprint 6

---

## Risk Management

### Critical Risks

**Risk 1: Min/Max Fix More Complex Than Expected**
- **Probability:** Medium
- **Impact:** High (blocks PATH validation)
- **Mitigation:**
  - Days 1-2 dedicated to fix
  - Research completed in prep phase (Unknown 1.1 DISPROVEN)
  - Checkpoint 1 early detection
  - Day 10 buffer for overrun
- **Contingency:** Simplify fix to handle common cases only, defer edge cases to Sprint 6

**Risk 2: PATH Solver Licensing Issues**
- **Probability:** Low (verified in Checkpoint 0)
- **Impact:** High (blocks Priority 2)
- **Mitigation:**
  - Licensing verified before sprint (Task 9)
  - Test framework exists from Sprint 4
  - Can validate with manual testing if CI fails
- **Contingency:** Document PATH testing as manual process, skip automated tests

**Risk 3: PyPI Publishing Fails**
- **Probability:** Low
- **Impact:** Medium (delays release)
- **Mitigation:**
  - Test with TestPyPI first (Day 8)
  - Follow PyPI best practices
  - Day 10 buffer for issues
- **Contingency:** Delay PyPI publish to post-sprint, release from GitHub

### Medium Risks

**Risk 4: Performance Targets Not Met**
- **Probability:** Low (Task 8 established baselines)
- **Impact:** Medium
- **Mitigation:**
  - Baselines from Task 8: 1K vars in 45.9s (well under 90s target)
  - Profile and optimize if needed (Day 5)
  - Clear performance targets
- **Contingency:** Document current performance, optimize in Sprint 6

**Risk 5: Documentation Takes Longer Than Expected**
- **Probability:** Medium
- **Impact:** Low (can ship with less doc)
- **Mitigation:**
  - Sprint 4 lesson: Quality > quantity
  - 2 full days allocated (Days 9-10)
  - Tutorial prioritized over API docs
- **Contingency:** Ship minimal docs, enhance in Sprint 6

**Risk 6: Edge Cases Reveal Fundamental Issues**
- **Probability:** Low
- **Impact:** High (if fundamental)
- **Mitigation:**
  - Checkpoint 2 after edge case testing
  - Systematic test approach
  - Day 10 buffer
- **Contingency:** Document limitations, fix in Sprint 6

### Low Risks

**Risk 7: Test Coverage Below Target**
- **Probability:** Low (Sprint 4 achieved 85%+)
- **Impact:** Low
- **Mitigation:**
  - Continuous coverage monitoring
  - Test-driven development
- **Contingency:** Accept slightly lower coverage, improve iteratively

**Risk 8: Cross-Platform Issues**
- **Probability:** Low (pure Python)
- **Impact:** Low
- **Mitigation:**
  - Multi-platform testing (Day 7)
  - GitHub Actions matrix (Day 8)
- **Contingency:** Document platform-specific issues

---

## Dependencies

### Inter-Day Dependencies

```
Day 1 (Min/Max Design)
  ↓
Day 2 (Min/Max Implementation) ← Required for Day 3
  ↓
Day 3 (PATH Validation + Checkpoint 1) ← Validates Days 1-2
  ↓
Day 4-6 (Production Hardening) ← Independent, can start anytime
  ↓
Day 6 (Checkpoint 2) ← Reviews Days 1-6
  ↓
Day 7 (PyPI Config) ← Independent, requires completed features
  ↓
Day 8 (Release Automation + Checkpoint 3) ← Requires Day 7
  ↓
Day 9 (Documentation) ← Requires all features complete
  ↓
Day 10 (Polish & Buffer) ← Final integration
```

### External Dependencies

**GAMS/PATH Licensing:**
- Required for: Days 2-3 (PATH validation)
- Status: ✅ Verified in Checkpoint 0 (Task 9)
- Backup: Manual testing if automated tests fail

**Sprint 4 Deliverables:**
- Required for: All days (foundation)
- Status: ✅ Complete (972 tests, 85%+ coverage)

**Sprint 5 Prep Tasks:**
- Required for: All days (preparation)
- Status: ✅ Complete (Tasks 1-9 done)
- Key outputs:
  - Task 2: Known Unknowns researched
  - Task 7: Documentation audit
  - Task 8: Large model fixtures (250, 500, 1K vars)
  - Task 9: Retrospective alignment

**PyPI Account:**
- Required for: Day 8 (publish to TestPyPI)
- Status: ✅ Can create on Day 8
- Backup: GitHub releases only

---

## Sprint 5 Success Definition

### Minimum Success (B Grade)
- ✅ Min/max bug fixed (Priority 1)
- ✅ PATH validation complete (Priority 2)
- ✅ Large models tested (Priority 3.2)
- ✅ PyPI package built (Priority 4)
- ✅ Tutorial created (Priority 5.1)
- ✅ 1000+ tests passing
- ✅ Code coverage ≥ 80%

### Target Success (A Grade)
- All minimum success criteria ✅
- ✅ Error recovery implemented (Priority 3.1)
- ✅ Memory optimization done (Priority 3.3)
- ✅ Edge cases tested (Priority 3.2)
- ✅ PyPI package published to TestPyPI
- ✅ FAQ created (Priority 5.2)
- ✅ Release automation working
- ✅ Code coverage ≥ 85%
- ✅ All checkpoints PASS

### Exceptional Success (A+ Grade)
- All target success criteria ✅
- ✅ Published to production PyPI
- ✅ API documentation site created
- ✅ Performance exceeds targets
- ✅ Zero deferred critical items
- ✅ All Known Unknowns resolved
- ✅ Sprint completed early (Day 9)

---

## Checkpoint Schedule

### Checkpoint 0: Pre-Sprint (COMPLETE)
- **Date:** November 6, 2025
- **Type:** Task 9 - Retrospective Alignment
- **Status:** ✅ COMPLETE
- **Findings:**
  - All Sprint 4 recommendations mapped
  - External dependencies verified
  - No gaps identified
  - GO for Sprint 5 start

### Checkpoint 1: Day 3
- **Focus:** New features initial implementation
- **Critical Questions:**
  - Min/max fix design complete?
  - PATH validation framework functional?
  - Any blockers for Days 4-10?
- **Artifacts:** Test results, coverage, PATH validation
- **Decision:** GO/NO-GO for production hardening

### Checkpoint 2: Day 6
- **Focus:** Mid-sprint progress review
- **Critical Questions:**
  - Priorities 1-3 complete?
  - On track for Days 7-10?
  - Scope adjustments needed?
- **Artifacts:** All Days 1-6 deliverables
- **Decision:** GO/NO-GO for packaging phase

### Checkpoint 3: Day 8
- **Focus:** Pre-completion review
- **Critical Questions:**
  - Priorities 1-4 complete?
  - Documentation ready for polish?
  - Release readiness?
- **Artifacts:** PyPI package, full test suite
- **Decision:** GO/NO-GO for final documentation

---

## Known Unknowns Integration

### Unknowns Requiring Follow-On Research

These unknowns are INCOMPLETE and require research during Sprint 5:

**Unknown 1.2:** Detection algorithm for min/max in objective
- **Day:** 1
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 1.4

**Unknown 1.4:** KKT assembly changes needed
- **Day:** 1-2
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Tasks 1.5, 2.1

**Unknown 1.5:** PATH solver options tuning
- **Day:** 2
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 2.3

**Unknown 2.1:** Model Status 5 failure causes
- **Day:** 3
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 3.2

**Unknown 2.2:** PATH solver options to document
- **Day:** 3
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 3.3

**Unknown 2.3:** PATH solution quality interpretation
- **Day:** 3
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 3.3

**Unknown 3.4:** NaN/Inf handling approach
- **Day:** 4
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 4.1

**Unknown 3.5:** Model validation pass design
- **Day:** 4
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 4.2

**Unknown 3.3:** Memory optimization techniques
- **Day:** 5
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 5.3 (if needed)

**Unknown 4.1:** Build system choice (setuptools vs hatch)
- **Day:** 7
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 7.1

**Unknown 4.2:** PyPI metadata requirements
- **Day:** 7
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 7.2

**Unknown 4.3:** Multi-platform testing approach
- **Day:** 7
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 7.6

**Unknown 4.4:** Version numbering scheme
- **Day:** 8
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 8.1

**Unknown 5.2:** Critical tutorial topics
- **Day:** 9
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 9.1

**Unknown 5.3:** Troubleshooting guide detail level
- **Day:** 9
- **Status:** 🔍 INCOMPLETE
- **Will be resolved:** During Task 9.4

### Unknowns Deferred to Future Sprints

These unknowns are low priority and deferred:

**Unknown 2.4:** PATH validation in CI/CD
- **Deferred to:** Sprint 6 planning
- **Reason:** Process decision, not critical for Sprint 5

**Unknown 5.1:** Sphinx vs MkDocs
- **Deferred to:** Sprint 6 planning
- **Reason:** API docs not required for initial release

**Unknown 5.4:** API reference detail level
- **Deferred to:** Sprint 6 planning
- **Reason:** Public API docs not required for initial release

### Unknowns Complete from Prep Phase

**Unknown 1.1:** Strategy 2 feasibility
- **Status:** ❌ DISPROVEN
- **Finding:** Direct constraints approach is infeasible
- **Impact:** Must use auxiliary variable approach (Strategy 1)

**Unknown 3.1:** Performance targets
- **Status:** ✅ COMPLETE (from Task 8)
- **Finding:** 1K vars in 45.9s, well under 90s target

**Unknown 3.2:** Critical edge cases
- **Status:** ✅ COMPLETE (research done)
- **Finding:** 5 categories identified, 20+ test cases

---

## Sprint 5 Retrospective Alignment

This plan incorporates all Sprint 4 Retrospective recommendations:

### Process Improvements Integrated

**1. Known Unknowns Process** ⭐⭐⭐⭐⭐
- ✅ 22 unknowns documented before sprint
- ✅ 1 critical finding (Unknown 1.1 DISPROVEN) prevented wrong approach
- ✅ Research completed in prep phase (Tasks 1-9)
- ✅ Unknowns mapped to specific days/tasks

**2. Checkpoint Process** ⭐⭐⭐⭐
- ✅ Checkpoint 0 completed (Task 9 - retrospective alignment)
- ✅ Checkpoint 1 (Day 3), Checkpoint 2 (Day 6), Checkpoint 3 (Day 8) scheduled
- ✅ Each checkpoint has clear GO/NO-GO criteria
- ✅ Recovery plan templates provided

**3. Test-Driven Development** ⭐⭐⭐⭐⭐
- ✅ Test pyramid maintained
- ✅ 1000+ tests target (from 972 Sprint 4 baseline)
- ✅ Coverage target ≥ 85%
- ✅ Tests written before implementation (TDD)

**4. Documentation First** ⭐⭐⭐⭐⭐
- ✅ 2 full days for documentation (Days 9-10)
- ✅ Tutorial prioritized
- ✅ Quality over quantity (Sprint 4 lesson: 5 good examples > 10 rushed)

**5. Research Before Code** ⭐⭐⭐⭐⭐
- ✅ All prep tasks completed (Tasks 1-9)
- ✅ Known Unknowns researched
- ✅ Critical findings documented (Unknown 1.1)
- ✅ No assumptions-driven development

**6. External Dependency Verification** ⭐⭐⭐⭐⭐
- ✅ Checkpoint 0 (Task 9) verified GAMS/PATH licensing
- ✅ Dependencies documented and tested
- ✅ Contingency plans for each dependency

### Technical Debt Resolution

**From Sprint 4 Retrospective:**

1. **Min/Max Reformulation Bug** (Priority 1)
   - ✅ Days 1-2 dedicated
   - ✅ Research complete (Unknown 1.1)
   - ✅ Test cases from research doc

2. **PATH Solver Validation** (Priority 2)
   - ✅ Day 3 dedicated
   - ✅ Test framework exists
   - ✅ Licensing verified

3. **Bound Detection Heuristics** (Low Priority)
   - ✅ Addressed in Day 4 (code quality pass)
   - ✅ Conservative approach documented

4. **GAMS Syntax Validation** (Deferred)
   - ✅ Consciously deferred to Sprint 6
   - ✅ Justification documented in Task 9

### Recommendations Implemented

**1. Fix Min/Max Bug** ✅
- Priority 1, Days 1-2
- Research complete, test plan ready

**2. Complete PATH Validation** ✅
- Priority 2, Day 3
- Dependencies verified

**3. Production Hardening** ✅
- Priority 3, Days 4-6
- Error recovery, large models, edge cases

**4. PyPI Packaging** ✅
- Priority 4, Days 7-8
- Build system, automation, testing

**5. Documentation Polish** ✅
- Priority 5, Days 9-10
- Tutorial, FAQ, troubleshooting

**6. Process Improvements** ✅
- Checkpoint 0, Known Unknowns, TDD
- All integrated into plan

---

**Plan Created:** November 6, 2025  
**Sprint Start:** TBD  
**Sprint End:** TBD (10 days after start)  
**Next Review:** Checkpoint 1 (Day 3)
