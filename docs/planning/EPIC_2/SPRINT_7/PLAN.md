# Sprint 7 Detailed Plan

**Sprint:** Epic 2 - Sprint 7 (Parser Enhancements & GAMSLib Expansion)  
**Duration:** 11 days (Days 0-10)  
**Start Date:** TBD  
**End Date:** TBD  
**Version:** v0.7.0

---

## Executive Summary

Sprint 7 focuses on **parser enhancements** and **test suite optimization** to achieve 30%+ GAMSLib parse rate and <60s test execution time. Building on comprehensive prep work (Tasks 1-9), this sprint implements high-ROI features with well-defined effort estimates and low-risk execution.

**Key Achievements from Prep Phase:**
- 25 Known Unknowns identified and verified (100% verification rate)
- 9 GAMSLib failures analyzed with feature priorities ranked by ROI
- Complete designs for all major features (preprocessor, test performance, CI/CD)
- 34-45 hour total effort estimated across 4 feature areas
- Zero blocking dependencies identified

**Sprint 7 Goals:**

| # | Goal | Baseline | Target | Measurement |
|---|------|----------|--------|-------------|
| 1 | **GAMSLib Parse Rate** | 10% (1/10) | 30% (3/10) minimum, 40% (4/10) stretch | `make ingest-gamslib` |
| 2 | **Fast Test Suite** | 208s | <60s target, 72s conservative | `time pytest tests/` |
| 3 | **Convexity UX** | No line numbers | 100% warnings show source location | Manual inspection |
| 4 | **CI Automation** | Manual dashboard | Automated regression detection | CI workflow active |

**Risk Level:** LOW ✅  
**Confidence:** HIGH ✅  
**Recommended Approach:** Focus Week 1 on parser (critical path), Week 2 on tests (high ROI), Week 3 on polish

> **Note on PREP_PLAN Acceptance Criteria:**  
> The Task 10 acceptance checklist in `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` (lines 2095-2102) should be checked **only after** this final plan receives approval. The checkboxes must reflect the final state of the approved plan, not any intermediate versions.

---

## Table of Contents

1. [Sprint 7 Goals](#sprint-7-goals)
2. [Day-by-Day Breakdown](#day-by-day-breakdown)
3. [Checkpoint Definitions](#checkpoint-definitions)
4. [Effort Estimates](#effort-estimates)
5. [Success Criteria](#success-criteria)
6. [Risk Register](#risk-register)
7. [Deliverables](#deliverables)
8. [Cross-References](#cross-references)

---

## 1. Sprint 7 Goals

### Goal 1: GAMSLib Parse Rate (PRIMARY)

**Objective:** Increase GAMSLib parse rate from 10% (1/10 models) to 30%+ (3/10 models)

**Rationale:** Sprint 6 established 10% baseline but revealed parser gaps. Task 2 (GAMSLib Failure Analysis) identified 2 critical features that unlock 3 models with 9-12 hours effort.

**Implementation:**
1. **Preprocessor Directives** (6-8 hours) - Mock/skip approach
   - `$if not set` with default values
   - `%macro%` expansion (user-defined + system constants)
   - `$eolCom` comment delimiter
   - **Unlocks:** circle.gms, maxmin.gms (+20% parse rate)
   - **ROI:** 2.9% per hour

2. **Set Range Syntax** (3-4 hours) - Grammar extension
   - Numeric ranges: `Set i / 1*6 /`
   - Alpha ranges: `Set s / s1*s10 /`
   - Prefix ranges: `Set p / p1*p100 /`
   - With macros: `Set i / 1*%n% /`
   - **Unlocks:** himmel16.gms (+10% parse rate)
   - **ROI:** 2.5% per hour

**Success Metrics:**
- ✅ Minimum: 30% parse rate (3/10 models) - Conservative
- 🎯 Target: 40% parse rate (4/10 models) - Likely (with quick wins)
- 🚀 Stretch: 50% parse rate (5/10 models) - If time permits

**Dependencies:**
- Task 2: GAMSLIB_FAILURE_ANALYSIS.md (feature priorities)
- Task 3: preprocessor_directives.md (implementation design)
- Task 9: PARSER_FIXTURE_STRATEGY.md (test fixtures)

---

### Goal 2: Fast Test Suite (PRIMARY)

**Objective:** Reduce test suite execution time from 208s to <60s (target) or <72s (conservative)

**Rationale:** Current 208s test suite (1,217 tests) slows development feedback loop. Task 5 (Test Performance Baseline) found Pareto distribution (1.3% of tests = 66.7% of time) and confirmed 95%+ tests are parallelizable.

**Implementation:**
1. **Enable pytest-xdist** (4-6 hours)
   - Install and configure pytest-xdist
   - Run baseline test with 4 workers
   - Identify and fix flaky tests
   - **Expected:** 3.0x-3.4x speedup

2. **Optimize Worker Count** (2-3 hours)
   - Benchmark 2, 4, 8, 16 workers
   - Plot speedup curve
   - Configure CI with optimal settings
   - **Expected:** Identify optimal worker count (likely 4-8)

3. **Mark Slow Tests** (2-3 hours) - OPTIONAL
   - Add `@pytest.mark.slow` to 4 production + 6 benchmark tests
   - Create fast test suite: `pytest -m "not slow" -n 4`
   - **Expected:** <30s fast test suite for local development

4. **CI Optimization** (3-4 hours)
   - Enable pip/pytest caching
   - Configure pytest-xdist in CI
   - Set CI timeout: 15 minutes
   - **Expected:** <5 minutes total CI test time

**Success Metrics:**
- ✅ Minimum: <72s with 4 workers (2.9x speedup) - Conservative
- 🎯 Target: <60s with 4-6 workers (3.5x speedup) - Likely
- 🚀 Stretch: <45s with 8 workers (4.6x speedup) - Aggressive

**Dependencies:**
- Task 5: TEST_PERFORMANCE_BASELINE.md (profiling data, 4-phase plan)

---

### Goal 3: Convexity UX Improvements (SECONDARY)

**Objective:** Add line numbers to convexity warnings for improved developer experience

**Rationale:** Current warnings don't cite line numbers, making it hard to locate problematic equations. Task 7 (Line Number Tracking Design) confirmed Lark metadata support with negligible performance overhead.

**Implementation:**
1. **IR Metadata Structure** (1 hour)
   - Add `SourceLocation` dataclass
   - Update `EquationDef`, `VariableDef`, `ParameterDef` with `loc` field

2. **Parser Integration** (1-1.5 hours)
   - Extract metadata from Lark `tree.meta`
   - New `_extract_location()` helper method
   - Pass `source_file` parameter

3. **Normalization Preservation** (0.5 hour)
   - Preserve `equation.loc` through transformations
   - Allow `loc=None` for generated nodes

4. **Convexity Integration** (0.5 hour)
   - Update warnings to include line numbers
   - Update formatter: `"W301 in equation 'circle_eq' (file.gms:15:8)"`

5. **Testing & Documentation** (0.5 hour)
   - 7 unit tests + 1 E2E test
   - Update warning documentation

**Success Metrics:**
- ✅ 100% of convexity warnings show source location (line:column)
- ✅ Graceful handling of generated nodes (loc=None)
- ✅ All edge cases covered (multi-line, includes, macros)

**Dependencies:**
- Task 7: line_number_tracking.md (complete design)

---

### Goal 4: CI Automation (SECONDARY)

**Objective:** Automate GAMSLib parse rate regression detection in CI

**Rationale:** Manual dashboard updates are error-prone. Task 8 (CI Regression Tracking Design) provides complete implementation plan with security considerations.

**Implementation:**
1. **Regression Detection Script** (2 hours)
   - Implement `scripts/check_parse_rate_regression.py`
   - 10% relative threshold
   - Detailed regression reports

2. **CI Workflow** (2-3 hours)
   - Create `.github/workflows/gamslib-regression.yml`
   - Hybrid trigger (path filter + weekly schedule)
   - Minimal permissions (contents: read)
   - 10-minute timeout

**Success Metrics:**
- ✅ CI workflow active on PR (parser file changes)
- ✅ Weekly scheduled run (Sunday 00:00 UTC)
- ✅ Zero false positives on non-regression PRs
- ✅ Fails CI if dashboard not committed

**Dependencies:**
- Task 8: gamslib_regression_tracking.md (complete design, workflow YAML)

---

## 2. Day-by-Day Breakdown

### Day 0: Pre-Sprint Setup & Kickoff

**Objective:** Complete prep work verification and sprint kickoff

**Tasks:**
1. ✅ Verify all prep tasks (1-9) complete
2. ✅ Review KNOWN_UNKNOWNS.md (25 unknowns, all verified)
3. ✅ Confirm all designs ready:
   - preprocessor_directives.md
   - multidimensional_indexing.md
   - line_number_tracking.md
   - gamslib_regression_tracking.md
   - PARSER_FIXTURE_STRATEGY.md
4. **Set up development environment** (2 hours)
   - Verify Python dependencies up to date
   - Configure pytest-xdist (install but don't enable yet)
   - Set up development branch and verify CI access
   - Validate GAMSLib data available in data/gamslib/
5. **Create fixture directory structure** (2 hours)
   - Create tests/fixtures/preprocessor/ directory
   - Create tests/fixtures/sets/ directory
   - Create tests/fixtures/multidim/ directory
   - Create tests/fixtures/statements/ directory
   - Create template expected_results.yaml files
   - Create template README.md files
6. **Sprint planning and kickoff** (2-3 hours)
   - Sprint kickoff meeting
   - Review daily goals and checkpoints
   - Assign responsibilities (if team sprint)
   - Set up daily standup schedule
   - Review risk register and mitigation plans

**Deliverables:**
- ✅ All prep tasks verified complete
- ✅ Development environment ready (Python 3.12.8, pytest-xdist installed)
- ✅ Sprint 7 branch created (sprint7-day0-setup)
- ✅ All 4 fixture directories created with templates
- ✅ Sprint kickoff complete (SPRINT_KICKOFF.md created)

**Effort:** 6-8 hours (verification + setup + templates + kickoff)

**Status:** ✅ COMPLETE (November 15, 2025)

**Checkpoint 0 Criteria:**
- [x] All 9 prep tasks complete
- [x] All 25 Known Unknowns verified
- [x] All designs reviewed and approved
- [x] Development environment ready

---

### Day 1: Preprocessor Directives (Part 1)

**Objective:** Implement preprocessor directive mock handling (50%)

**Tasks:**
1. **Implement Core Functions** (3-4 hours)
   - `extract_conditional_sets()` - Extract defaults from `$if not set` (1.5h)
   - `expand_macros()` - Expand `%macro%` references (2h)
   - `strip_conditional_directives()` - Replace directives with comments (0.5h)

2. **Write Unit Tests** (2-2.5 hours)
   - Test `extract_conditional_sets()` with various patterns (5 tests)
   - Test `expand_macros()` with user-defined and system macros (5 tests)
   - Test `strip_conditional_directives()` edge cases (3 tests)
   - Test error handling (missing macros, invalid syntax)

3. **Test on GAMSLib Models** (0.5 hour)
   - Test circle.gms (preprocessor blocking)
   - Test maxmin.gms (preprocessor blocking)
   - Document preprocessing flow

4. **Code Review and Refactoring** (1-1.5 hours)
   - Review code for edge cases
   - Add error handling and validation
   - Optimize performance
   - Add docstrings and comments

**Deliverables:**
- `src/ir/preprocessor.py` updated with 3 new functions
- 13+ unit tests for preprocessor functions
- circle.gms and maxmin.gms preprocessing working
- Code reviewed and documented

**Effort:** 6-8 hours

**Success Criteria:**
- ✅ `extract_conditional_sets()` extracts defaults correctly
- ✅ `expand_macros()` expands user-defined and system macros
- ✅ circle.gms preprocesses without errors
- ✅ maxmin.gms preprocesses without errors
- ✅ All 26 unit tests pass (exceeds 13+ requirement)
- ✅ Code reviewed and documented

**Status:** ✅ COMPLETE (PR #TBD)

---

### Day 2: Preprocessor Directives (Part 2) + Set Range Syntax (Part 1)

**Objective:** Complete preprocessor implementation and start set range syntax

**Tasks:**
1. **Complete Preprocessor Integration** (3-4 hours)
   - Integrate into `preprocess_gams_file()` pipeline (0.5h)
   - Write comprehensive unit tests (15+ tests) (2h)
   - Handle `$eolCom` directive (1h)
   - Add integration tests with preprocessor pipeline (0.5h)

2. **Start Set Range Syntax** (2-2.5 hours)
   - Update grammar.lark with range syntax rules (1h)
   - Implement range expansion logic (numeric ranges) (1h)
   - Write initial unit tests for numeric ranges (0.5h)

3. **Documentation and Error Handling** (1-1.5 hours)
   - Document preprocessor functions with examples
   - Add comprehensive error messages
   - Update user documentation if needed

**Deliverables:**
- Preprocessor fully integrated and tested
- Grammar updated with range syntax
- Numeric range expansion working
- 15+ preprocessor unit tests complete
- Documentation updated

**Effort:** 6-8 hours

**Success Criteria:**
- ✅ All 15+ preprocessor unit tests pass
- ✅ Preprocessor integrated into main pipeline
- ✅ Grammar accepts `Set i / 1*6 /` syntax
- ✅ Numeric range expansion generates correct elements
- ✅ Error handling comprehensive
- ✅ Documentation complete

---

### Day 3: Set Range Syntax (Part 2)

**Status:** ✅ COMPLETE (2025-11-15)

**Objective:** Complete set range syntax implementation

**Actual Completion:**
- ✅ All 4 range types verified working from Day 2
- ✅ 18 unit tests from Day 2 confirmed passing
- ✅ Added grammar enhancements for real GAMS models:
  - `Set` (singular) keyword support
  - Optional set descriptions
  - `Alias` (singular) keyword support
  - `Alias (i,j)` parentheses syntax
- ✅ Added 9 integration tests
- ✅ Added 10 unit tests for new grammar features
- ✅ Updated documentation (CHANGELOG, issue #136)
- ✅ All quality checks pass

**Key Discovery:**
Range implementation was already complete from Day 2. Day 3 focused on grammar enhancements to support real GAMSLib model syntax like himmel16.gms.

**Tasks:**
1. **Complete Range Expansion** (3-3.5 hours)
   - ✅ Alpha ranges: `s1*s10` (already done Day 2)
   - ✅ Prefix ranges: `p1*p100` (already done Day 2)
   - ✅ With macros: `1*%n%` (already done Day 2)
   - ✅ Integration with preprocessor (already done Day 2)

2. **Comprehensive Unit Tests** (2-2.5 hours)
   - ✅ Test all 4 range types (8 tests) - confirmed from Day 2
   - ✅ Test edge cases (5 tests) - confirmed from Day 2
   - ✅ Test macro integration (3 tests) - confirmed from Day 2
   - ✅ Test error handling (2 tests) - confirmed from Day 2

3. **Integration Tests and Documentation** (1.5-2 hours)
   - ✅ Create integration test suite (9 tests added)
   - ✅ Test himmel16.gms patterns (discovered grammar needs)
   - ✅ Document range syntax (CHANGELOG, issue doc updated)
   - ✅ Add grammar documentation (CHANGELOG has details)

**Deliverables:**
- ✅ Set range syntax fully implemented
- ✅ All range types working
- ✅ 37 total tests passing (18 unit + 9 integration + 10 grammar)
- ✅ Integration tests complete
- ✅ Documentation updated

**Effort:** ~4 hours (less than estimated due to Day 2 completion)

**Success Criteria:**
- ✅ All 4 range types expand correctly
- ✅ himmel16.gms parses successfully
- ✅ Unit tests cover all range patterns
- ✅ Integration with preprocessor working
- ✅ All 18+ tests passing
- ✅ Documentation complete

---

### Day 4: Parser Integration & Testing + Quick Wins

**Objective:** Integrate parser enhancements, test on GAMSLib, and implement quick wins for 40-50% parse rate

**Tasks:**
1. **Integration Testing** (2-3 hours)
   - Test circle.gms end-to-end
   - Test maxmin.gms end-to-end
   - Test himmel16.gms end-to-end
   - Fix any integration issues
   - Create integration test suite

2. **Quick Win: Multiple Scalar Declarations** (2-3 hours) - REQUIRED
   - Update grammar to support `Scalars a, b, c;` syntax
   - Implement parser support for multiple scalars in one statement
   - Write unit tests (5+ tests)
   - Test on trig.gms
   - **Unlocks trig.gms → +10% parse rate**

3. **Quick Win: Models Keyword** (1-2 hours) - REQUIRED
   - Add `Models` (plural) keyword support to grammar
   - Implement parser handling for multiple model declarations
   - Write unit tests (3+ tests)
   - Test on mathopt1.gms
   - **Unlocks mathopt1.gms → +10% parse rate**

4. **Validation and Documentation** (1 hour)
   - Run full parser test suite
   - Document new features
   - Update CHANGELOG

**Deliverables:**
- 3 models parsing (circle, maxmin, himmel16) - MINIMUM (30%)
- 5 models parsing (+ trig, mathopt1) - TARGET (50%)
- Integration test suite complete
- Multiple scalar syntax supported
- Models keyword supported
- Documentation updated

**Effort:** 6-8 hours (all tasks required)

**Success Criteria:**
- ✅ circle.gms parses (preprocessor working)
- ✅ maxmin.gms parses (preprocessor working)
- ✅ himmel16.gms parses (set range working)
- ✅ trig.gms parses (multiple scalars - REQUIRED)
- ✅ mathopt1.gms parses (models keyword - REQUIRED)
- ✅ Parse rate = 50% (5/10 models)
- ✅ All integration tests pass

---

### Day 5: GAMSLib Retest & Checkpoint 1

**Objective:** Verify 30%+ parse rate achieved (Checkpoint 1)

**Tasks:**
1. **GAMSLib Full Retest** (1 hour)
   - Run `make ingest-gamslib`
   - Update dashboard with new parse rate
   - Verify ≥3 models parsing (30%)

2. **Parser Fixture Creation** (4-5 hours)
   - Create 9 preprocessor fixtures
   - Create 8 set range fixtures
   - Create expected_results.yaml files
   - Create README.md files
   - Document fixture patterns and edge cases

3. **Checkpoint 1 Review** (1-2 hours)
   - Review acceptance criteria
   - Document any issues or risks
   - Plan Week 2 work
   - Update project documentation

**Deliverables:**
- GAMSLib parse rate ≥30% (Checkpoint 1)
- 17 parser fixtures created
- Dashboard updated

**Effort:** 6-8 hours

**Checkpoint 1 Criteria:**
- [ ] GAMSLib parse rate ≥30% (3/10 models minimum)
- [ ] circle.gms, maxmin.gms, himmel16.gms parsing
- [ ] Dashboard updated with new parse rate
- [ ] ≥17 parser fixtures created with expected results
- [ ] All parser unit tests passing

---

### Day 6: Test Performance (Part 1) - pytest-xdist

**Objective:** Enable pytest-xdist parallelization

**Tasks:**
1. **Install and Configure** (1 hour)
   - Install pytest-xdist
   - Update pyproject.toml configuration
   - Document usage in README

2. **Baseline Testing** (1.5-2 hours)
   - Run `pytest -n 4` baseline test
   - Identify flaky tests (if any)
   - Fix test isolation issues
   - Verify all 1,217 tests pass

3. **Stress Testing** (3.5-5 hours)
   - Run 10 iterations: `for i in {1..10}; do pytest -n 4; done`
   - Each iteration ~60-70s = 10-12 minutes minimum
   - Document any intermittent failures
   - Fix race conditions and shared state issues
   - Debug and resolve flaky tests
   - Additional buffer for unexpected isolation issues

**Deliverables:**
- pytest-xdist enabled
- All tests passing in parallel with no flakiness
- Stability verified across 10 consecutive runs
- All isolation issues resolved

**Effort:** 6-8 hours

**Success Criteria:**
- ✅ `pytest -n 4` runs successfully
- ✅ All 1,217 tests pass in parallel
- ✅ Zero flaky tests detected across 10 runs
- ✅ All race conditions and shared state issues fixed

---

### Day 7: Test Performance (Part 2) & Checkpoint 2

**Objective:** Achieve <60s test suite (Checkpoint 2)

**Tasks:**
1. **Benchmark Worker Counts** (1.5-2 hours)
   - Test 2, 4, 8, 16 workers
   - Plot speedup curve
   - Measure overhead (15-25% expected)
   - Document optimal worker count

2. **Optimize Worker Count** (0.5-1 hour)
   - Analyze benchmark results
   - Select optimal worker count (likely 4-8)
   - Configure as default

3. **Mark Slow Tests** (1.5-2 hours)
   - Add `@pytest.mark.slow` to 5-10 slowest tests
   - Create fast test suite config
   - Verify fast suite <60s and full suite <120s

4. **CI Configuration** (2-3 hours)
   - Enable pip/pytest caching
   - Configure pytest-xdist in CI (`pytest -n auto`)
   - Set timeout to 15 minutes
   - Test CI workflow

5. **Checkpoint 2 Review** (0.5-1 hour)
   - Verify fast <60s, full <120s achieved
   - Document speedup results
   - Plan Week 3 work

**Deliverables:**
- Worker count benchmarks complete (Checkpoint 2)
- Fast test suite <60s, Full test suite <120s (Checkpoint 2)
- CI optimized with parallelization
- Slow tests marked for fast test suite

**Effort:** 6-8 hours

**Checkpoint 2 Criteria:**
- [ ] Fast test suite <60s (verified with `pytest -m "not slow" -n 4`)
- [ ] Full test suite <120s (verified with `pytest -n 4`)
- [ ] CI test time <5 minutes
- [ ] All tests passing with parallelization
- [ ] Zero regressions from Sprint 6

---

### Day 8: Convexity UX + Multi-Dim Fixtures

**Objective:** Implement line number tracking and create multi-dim fixtures

**Tasks:**
1. **Line Number Tracking** (3.5-5 hours)
   - Phase 1: IR Structure (1h)
   - Phase 2: Parser Integration (1-1.5h)
   - Phase 3: Normalization Preservation (0.5-1h)
   - Phase 4: Convexity Integration (0.5-1h)
   - Phase 5: Testing (0.5-1h)
   - Phase 6: Documentation and edge cases (0.5h)

2. **Multi-Dim Fixtures** (2.5-3 hours)
   - Create 8 multidim fixtures
   - Create expected_results.yaml
   - Create README.md
   - Document multidimensional patterns

**Deliverables:**
- Line numbers in all convexity warnings
- 8 multidim fixtures created

**Effort:** 6-8 hours

**Success Criteria:**
- ✅ 100% of convexity warnings show line numbers
- ✅ Warning format: `"W301 in equation 'eq' (file.gms:15:8)"`
- ✅ All edge cases handled gracefully
- ✅ 8 multidim fixtures created

---

### Day 9: CI Automation + Statement Fixtures & Checkpoint 3

**Objective:** Complete CI automation and all fixtures (Checkpoint 3)

**Tasks:**
1. **GAMSLib Regression CI** (3.5-5 hours)
   - Implement `scripts/check_parse_rate_regression.py` (2h)
   - Create `.github/workflows/gamslib-regression.yml` (1.5-3h)
   - Test workflow on PR
   - Verify regression detection

2. **Statement Fixtures** (2-2.5 hours)
   - Create 9 statement fixtures
   - Create expected_results.yaml
   - Create README.md

3. **Checkpoint 3 Review** (0.5-1 hour)
   - Verify all features integrated
   - Verify CI working
   - Plan Day 10 release

**Deliverables:**
- CI automation complete (Checkpoint 3)
- 34 total fixtures created
- All features integrated

**Effort:** 6-8 hours

**Checkpoint 3 Criteria:**
- [ ] GAMSLib regression CI workflow active
- [ ] All 34 fixtures created (9+8+8+9)
- [ ] Line number tracking working
- [ ] Test suite <60s
- [ ] Parse rate ≥30%
- [ ] Zero failing tests

---

### Day 10: Sprint Review, Release & Checkpoint 4

**Objective:** Complete Sprint 7, release v0.7.0 (Checkpoint 4)

**Tasks:**
1. **Final QA** (2-2.5 hours)
   - Run full test suite: `pytest tests/`
   - Run quality checks: `make typecheck lint format`
   - Test GAMSLib ingestion
   - Verify all 4 sprint goals met

2. **Documentation** (2-2.5 hours)
   - Update CHANGELOG.md
   - Update PROJECT_PLAN.md Sprint 7 status
   - Create Sprint 7 retrospective (RETROSPECTIVE.md)
   - Update version to 0.7.0

3. **Release** (1-1.5 hours)
   - Tag v0.7.0 release
   - Create GitHub release notes
   - Update README if needed

4. **Sprint Review** (1-2 hours)
   - Demo new features
   - Review metrics vs goals
   - Identify lessons learned
   - Plan Sprint 8 prep

**Deliverables:**
- v0.7.0 released (Checkpoint 4)
- Sprint retrospective complete
- All documentation updated

**Effort:** 6-8 hours

**Checkpoint 4 Criteria:**
- [ ] All 4 sprint goals achieved
- [ ] v0.7.0 tagged and released
- [ ] CHANGELOG.md updated
- [ ] Retrospective complete
- [ ] All quality checks passing
- [ ] Sprint review conducted

---

## 3. Checkpoint Definitions

### Checkpoint 0: Prep Complete (Day 0)

**Objective:** All preparation work verified complete before Sprint 7 begins

**Acceptance Criteria:**
- [x] All 9 prep tasks complete (Tasks 1-9)
- [x] All 25 Known Unknowns verified
- [x] All implementation designs reviewed:
  - [x] preprocessor_directives.md
  - [x] multidimensional_indexing.md
  - [x] line_number_tracking.md
  - [x] gamslib_regression_tracking.md
  - [x] PARSER_FIXTURE_STRATEGY.md
- [x] Development environment ready
- [x] Sprint 7 PLAN.md created and approved

**Measurement:** Manual verification checklist

**Status:** ✅ COMPLETE

---

### Checkpoint 1: Parser Enhancements Complete (Day 5)

**Objective:** GAMSLib parse rate ≥30% achieved

**Acceptance Criteria:**
- [ ] Preprocessor directives implemented (6-8h)
  - [ ] `$if not set` with default extraction
  - [ ] `%macro%` expansion (user-defined + system)
  - [ ] `$eolCom` comment handling
  - [ ] All 15+ unit tests passing
- [ ] Set range syntax implemented (3-4h)
  - [ ] Numeric ranges: `1*6`
  - [ ] Alpha ranges: `s1*s10`
  - [ ] Prefix ranges: `p1*p100`
  - [ ] With macros: `1*%n%`
  - [ ] All unit tests passing
- [ ] GAMSLib models parsing:
  - [ ] circle.gms ✅ (preprocessor)
  - [ ] maxmin.gms ✅ (preprocessor)
  - [ ] himmel16.gms ✅ (set range)
  - [ ] Parse rate ≥30% (3/10 models minimum)
- [ ] Parser fixtures created:
  - [ ] 9 preprocessor fixtures
  - [ ] 8 set range fixtures
  - [ ] expected_results.yaml files
  - [ ] README.md files
- [ ] Dashboard updated with new parse rate

**Measurement:** 
- `make ingest-gamslib` → parse rate in dashboard
- `pytest tests/unit/parser/` → all parser tests pass

**Success Metrics:**
- ✅ Minimum: 30% parse rate (3/10 models)
- 🎯 Target: 40% parse rate (4/10 models with quick wins)
- 🚀 Stretch: 50% parse rate (5/10 models)

**Estimated Effort:** 9-12 hours (Days 1-5)

**Risk Mitigation:**
- If <30%: Debug individual models, add targeted fixes
- If quick wins take >3h: Defer to Sprint 8
- If tests fail: Prioritize fixing over adding features

---

### Checkpoint 2: Test Performance Optimized (Day 7)

**Objective:** Fast test suite <60s, Full test suite <120s

**Acceptance Criteria:**
- [ ] pytest-xdist enabled and configured (Day 6)
  - [ ] `pytest -n 4` runs successfully
  - [ ] All 1,217 tests pass in parallel
  - [ ] Zero flaky tests across 10 consecutive runs
  - [ ] All isolation issues resolved
- [ ] Worker count benchmarked and optimized (Day 7)
  - [ ] Benchmarks run: 2, 4, 8, 16 workers
  - [ ] Speedup curve plotted
  - [ ] Optimal worker count selected
  - [ ] Overhead measured (15-25% expected)
- [ ] **Test suite performance targets met** (REQUIRED)
  - [ ] **Fast test suite <60s** (verified with `time pytest -m "not slow" -n 4 tests/`)
  - [ ] **Full test suite <120s** (verified with `time pytest -n 4 tests/`)
  - [ ] Slow tests marked with `@pytest.mark.slow` (5-10 tests)
  - [ ] Fast suite excludes slow tests
- [ ] CI optimized
  - [ ] pip/pytest caching enabled
  - [ ] pytest-xdist configured (`-n auto`)
  - [ ] Timeout set to 15 minutes
  - [ ] CI test time <5 minutes
- [ ] Zero regressions from Sprint 6
  - [ ] All existing tests still pass
  - [ ] Code coverage ≥88%

**Measurement:**
- `time pytest -m "not slow" -n 4 tests/` → <60s (fast suite)
- `time pytest -n 4 tests/` → <120s (full suite)
- CI job duration → <5 minutes

**Success Metrics:**
- ✅ Minimum (REQUIRED): Fast <60s, Full <120s
- 🎯 Target: Fast <45s, Full <90s (2x faster)
- 🚀 Stretch: Fast <30s, Full <60s (3.5x faster)

**Estimated Effort:** 11-16 hours (Days 6-7)

**Risk Mitigation:**
- If flaky tests: Isolate with fixtures, fix shared state
- If speedup <2.9x: Investigate overhead, reduce worker count
- If CI timeout: Increase timeout, split test suites

---

### Checkpoint 3: All Features Integrated (Day 9)

**Objective:** All Sprint 7 features complete and integrated

**Acceptance Criteria:**
- [ ] Line number tracking implemented
  - [ ] `SourceLocation` dataclass added
  - [ ] Parser extracts Lark metadata
  - [ ] Normalization preserves locations
  - [ ] Convexity warnings show line numbers
  - [ ] Warning format: `"W301 ... (file.gms:15:8)"`
  - [ ] All 7 unit tests + 1 E2E test passing
  - [ ] 100% of warnings show source location
- [ ] GAMSLib regression CI automated
  - [ ] `scripts/check_parse_rate_regression.py` implemented
  - [ ] `.github/workflows/gamslib-regression.yml` created
  - [ ] Hybrid trigger configured (path filter + weekly)
  - [ ] 10% relative threshold set
  - [ ] Workflow tested on PR
  - [ ] Zero false positives detected
- [ ] All parser fixtures created
  - [ ] 9 preprocessor fixtures ✅
  - [ ] 8 set range fixtures ✅
  - [ ] 8 multidim fixtures
  - [ ] 9 statement fixtures
  - [ ] All expected_results.yaml files
  - [ ] All README.md files
  - [ ] 34 total fixtures (100% coverage)
- [ ] All quality checks passing
  - [ ] `make typecheck` → Success
  - [ ] `make lint` → All checks passed
  - [ ] `make format` → No changes
  - [ ] `pytest tests/` → 1,217+ tests pass

**Measurement:**
- Manual verification of all features
- CI workflow active
- All tests passing

**Estimated Effort:** 34-45 hours (Days 0-9)

**Risk Mitigation:**
- If line numbers fail: Simplify to start line only
- If CI workflow issues: Manual testing, staged rollout
- If fixtures incomplete: Prioritize critical fixtures

---

### Checkpoint 4: Sprint Complete & Released (Day 10)

**Objective:** Sprint 7 complete, v0.7.0 released, all goals achieved

**Acceptance Criteria:**
- [ ] **Goal 1: GAMSLib Parse Rate** ✅
  - [ ] Parse rate ≥30% (3/10 models minimum)
  - [ ] Dashboard updated
  - [ ] Preprocessor + set range working
- [ ] **Goal 2: Fast Test Suite** ✅
  - [ ] Fast test suite <60s (verified with `pytest -m "not slow" -n 4`)
  - [ ] Full test suite <120s (verified with `pytest -n 4`)
  - [ ] CI test time <5 minutes
  - [ ] pytest-xdist configured
- [ ] **Goal 3: Convexity UX** ✅
  - [ ] 100% warnings show line numbers
  - [ ] Warning format enhanced
- [ ] **Goal 4: CI Automation** ✅
  - [ ] GAMSLib regression CI active
  - [ ] Weekly scheduled runs
  - [ ] Manual commit required
- [ ] **Quality Assurance:**
  - [ ] All 1,217+ tests passing
  - [ ] Code coverage ≥88%
  - [ ] All quality checks passing
  - [ ] Zero regressions from Sprint 6
- [ ] **Documentation:**
  - [ ] CHANGELOG.md updated
  - [ ] PROJECT_PLAN.md Sprint 7 marked complete
  - [ ] RETROSPECTIVE.md created
  - [ ] Version bumped to 0.7.0
- [ ] **Release:**
  - [ ] v0.7.0 tagged
  - [ ] GitHub release created
  - [ ] Release notes published

**Measurement:**
- All acceptance criteria verified
- Sprint review conducted
- Release published

**Success Metrics:**
- ✅ All 4 sprint goals achieved
- ✅ 34-45 hours total effort (within estimate)
- ✅ Zero blocking issues
- ✅ High-quality release

**Risk Mitigation:**
- If goal unmet: Document reason, plan remediation for Sprint 7.1
- If release blocked: Identify blocker, plan hotfix
- If retrospective delayed: Schedule post-sprint

---

## 4. Effort Estimates

### 4.1 Summary by Feature Area

| Feature Area | Estimated Effort | Actual Effort | Variance |
|--------------|------------------|---------------|----------|
| **Parser Enhancements** | 9-12 hours | TBD | TBD |
| - Preprocessor directives | 6-8 hours | TBD | TBD |
| - Set range syntax | 3-4 hours | TBD | TBD |
| **Test Performance** | 12-16 hours | TBD | TBD |
| - Enable pytest-xdist | 6-8 hours | TBD | TBD |
| - Optimize worker count | 1-2 hours | TBD | TBD |
| - Mark slow tests (optional) | 1-2 hours | TBD | TBD |
| - CI optimization | 2-3 hours | TBD | TBD |
| **Convexity UX** | 3-4 hours | TBD | TBD |
| - Line number tracking | 3-4 hours | TBD | TBD |
| **CI Automation** | 4-5 hours | TBD | TBD |
| - Regression detection | 4-5 hours | TBD | TBD |
| **Test Fixtures** | 7-8 hours | TBD | TBD |
| - 34 fixtures + YAML + READMEs | 7-8 hours | TBD | TBD |
| **TOTAL** | **35-45 hours** | **TBD** | **TBD** |

### 4.2 Effort by Day

| Day | Focus | Estimated Effort | Cumulative |
|-----|-------|------------------|------------|
| Day 0 | Pre-sprint setup | 6-8 hours | 6-8h |
| Day 1 | Preprocessor (Part 1) | 6-8 hours | 12-16h |
| Day 2 | Preprocessor (Part 2) + Set Range (Part 1) | 6-8 hours | 18-24h |
| Day 3 | Set Range (Part 2) | 6.5-8 hours | 24.5-32h |
| Day 4 | Parser integration + quick wins | 6-8 hours | 30.5-40h |
| Day 5 | GAMSLib retest + fixtures | 6-8 hours | 36.5-48h |
| Day 6 | pytest-xdist | 6-8 hours | 42.5-56h |
| Day 7 | Test optimization | 6-8 hours | 48.5-64h |
| Day 8 | Line numbers + multidim fixtures | 6-8 hours | 54.5-72h |
| Day 9 | CI automation + statement fixtures | 6-8 hours | 60.5-80h |
| Day 10 | Sprint review + release | 6-8 hours | 66.5-88h |

**Target:** 60.5-80 hours (Days 0-9) + 6-8 hours (Day 10) = 66.5-88 hours total

**Budget:** 11 days × 6-8 hours/day = 66-88 hours available

**Margin:** 0-21.5 hours buffer (0-24% contingency)

### 4.3 Critical Path

**Critical Path (Must Complete):**
1. Preprocessor directives (6-8h) → **Day 1-2**
2. Set range syntax (3-4h) → **Day 2-3**
3. GAMSLib retest (1h) → **Day 5**
4. pytest-xdist (4-6h) → **Day 6**

**Total Critical Path:** 14-19 hours (Days 1-6)

**Parallel Work (Can be done anytime):**
- Line number tracking (3-4h) → **Day 8**
- CI automation (4-5h) → **Day 9**
- Test fixtures (7-8h) → **Days 5, 8, 9**

**Flexible Items (Can be deferred):**
- Quick wins (2-3h) → **Day 4** (optional)
- Slow test marking (2-3h) → **Day 7** (optional)
- Worker count optimization (2-3h) → **Day 7** (can use default 4)

---

## 5. Success Criteria

### 5.1 Sprint Goals Success Metrics

**Goal 1: GAMSLib Parse Rate**
- ✅ **PASS:** ≥30% parse rate (3/10 models)
- 🎯 **TARGET:** 40% parse rate (4/10 models)
- 🚀 **EXCEED:** 50% parse rate (5/10 models)

**Goal 2: Fast Test Suite**
- ✅ **PASS:** Fast <60s, Full <120s (Checkpoint 2 requirement)
- 🎯 **TARGET:** Fast <45s, Full <90s (2x faster)
- 🚀 **EXCEED:** Fast <30s, Full <60s (3.5x faster)

**Goal 3: Convexity UX**
- ✅ **PASS:** 100% warnings show line numbers
- 🎯 **TARGET:** All edge cases handled
- 🚀 **EXCEED:** Column numbers + source range highlighting

**Goal 4: CI Automation**
- ✅ **PASS:** CI workflow active, zero false positives
- 🎯 **TARGET:** Hybrid trigger working (path filter + weekly)
- 🚀 **EXCEED:** Historical trend tracking

### 5.2 Quality Metrics

**Test Coverage:**
- ✅ All 1,217+ tests passing
- ✅ Code coverage ≥88%
- ✅ Zero failing tests
- 🎯 Code coverage ≥90%

**Performance:**
- ✅ Test suite <60s (or <72s conservative)
- ✅ CI test time <5 minutes
- 🎯 Fast test suite <30s (optional)

**Documentation:**
- ✅ CHANGELOG.md updated
- ✅ All prep tasks documented
- ✅ Retrospective complete
- 🎯 User guide updated

**Code Quality:**
- ✅ `make typecheck` passing
- ✅ `make lint` passing
- ✅ `make format` no changes
- ✅ Zero new warnings

### 5.3 Deliverables Checklist

**Sprint 7 Deliverables:**
- [ ] Preprocessor directive handling (mock/skip approach)
- [ ] Set range syntax support
- [ ] pytest-xdist parallelization
- [ ] Line number tracking in warnings
- [ ] GAMSLib regression CI automation
- [ ] 34 parser test fixtures
- [ ] CHANGELOG.md updated
- [ ] RETROSPECTIVE.md created
- [ ] v0.7.0 release

**All Deliverables Complete:** ✅ / ❌

---

## 6. Risk Register

### Risk 1: Preprocessor Complexity Underestimated

**Description:** Preprocessor directive handling may be more complex than estimated, requiring additional features or edge case handling.

**Probability:** Low (20%)  
**Impact:** Medium (could add 4-6 hours)  
**Risk Score:** LOW

**Mitigation:**
- Mock/skip approach is well-researched (Task 3)
- Only 3 directive types needed (`$if not set`, `%macro%`, `$eolCom`)
- Complete directive survey found no advanced features in GAMSLib
- Fallback: Defer edge cases to Sprint 8

**Contingency:**
- Budget +4 hours for edge cases
- Defer advanced conditionals (`$ifThen`, `$else`) to Sprint 8
- Focus on minimal viable implementation

**Owner:** Parser specialist

---

### Risk 2: pytest-xdist Flaky Tests

**Description:** Parallelization may expose test isolation issues, causing flaky tests that fail intermittently.

**Probability:** Medium (40%)  
**Impact:** High (could block parallelization, 11-16h wasted)  
**Risk Score:** MEDIUM

**Mitigation:**
- Task 5 analysis: 95%+ tests are parallelizable (no shared state detected)
- Most tests use fixtures (already isolated)
- Run stress test (10 iterations) to identify flaky tests early (Day 6)
- Fix isolation issues immediately when detected

**Contingency:**
- Budget +2-4 hours for fixing flaky tests
- Use pytest-xdist `--dist loadfile` to reduce race conditions
- Isolate problematic tests with `@pytest.mark.serial` if needed
- Fallback: Reduce worker count to 2 if issues persist

**Owner:** Testing specialist

---

### Risk 3: Parse Rate Goal Unmet (30%)

**Description:** Parser enhancements may not unlock expected models, resulting in <30% parse rate.

**Probability:** Very Low (5%)  
**Impact:** High (Sprint 7 goal failure)  
**Risk Score:** LOW

**Mitigation:**
- Task 2 analysis confirms 30% achievable with just 2 features
- Preprocessor unlocks circle.gms, maxmin.gms (+20%)
- Set range unlocks himmel16.gms (+10%)
- Quick wins available (multiple scalars, models keyword) for 40-50%

**Contingency:**
- Debug individual models to identify additional blockers
- Add targeted fixes for specific syntax patterns
- Defer to Sprint 7.1 if fundamental parser limitation discovered
- Document lessons learned for Sprint 8

**Owner:** Parser specialist

---

### Risk 4: Test Performance Goal Unmet (<60s)

**Description:** Parallelization speedup may be less than expected due to overhead or test distribution.

**Probability:** Very Low (10%)  
**Impact:** Medium (goal unmet but <72s acceptable)  
**Risk Score:** LOW

**Mitigation:**
- Conservative 2.9x speedup estimate (208s → 72s)
- Pareto analysis shows 66.7% of time in top 4 tests (highly parallelizable)
- Benchmarks will identify optimal worker count
- pytest-xdist overhead estimated 15-25% (reasonable)

**Contingency:**
- Accept <72s if <60s not achievable (still 65% reduction)
- Investigate overhead sources (test collection, fixture setup)
- Consider sharding tests across multiple CI jobs
- Defer further optimization to Sprint 8

**Owner:** Testing specialist

---

### Risk 5: Scope Creep

**Description:** Additional features or "nice-to-have" items may be added during sprint, causing timeline slip.

**Probability:** Medium (30%)  
**Impact:** Medium (delays release, reduces buffer)  
**Risk Score:** MEDIUM

**Mitigation:**
- Strict prioritization: Critical → High → Medium → Low
- Clear critical path defined (14-19 hours)
- Optional items identified (quick wins, slow test marking)
- 11-33 hours buffer available (20-37% contingency)

**Contingency:**
- Defer optional items to Sprint 8 if timeline tight
- Focus on 4 primary goals only
- Document deferred items in retrospective
- Plan Sprint 7.1 for missed items if needed

**Owner:** Sprint lead

---

### Risk 6: CI Workflow Issues

**Description:** GAMSLib regression CI may have permission issues, timeout problems, or false positives.

**Probability:** Low (20%)  
**Impact:** Low (doesn't block development, manual fallback)  
**Risk Score:** LOW

**Mitigation:**
- Complete design in Task 8 (gamslib_regression_tracking.md)
- Minimal permissions (contents: read) - secure
- 10-minute timeout (2x expected time)
- Manual commit required (no auto-commit security risk)

**Contingency:**
- Test workflow on PR before merging
- Debug with `act` (local GitHub Actions runner) if issues
- Fallback to manual dashboard updates if workflow fails
- Plan hotfix for CI issues post-sprint

**Owner:** CI/CD specialist

---

### Risk 7: Line Number Tracking Edge Cases

**Description:** Line number tracking may fail on edge cases (multi-line equations, includes, macros, generated nodes).

**Probability:** Low (15%)  
**Impact:** Low (doesn't block sprint, warnings still useful without line numbers)  
**Risk Score:** LOW

**Mitigation:**
- Complete design in Task 7 (line_number_tracking.md)
- Lark metadata support confirmed (negligible overhead)
- Graceful handling designed (`loc=None` for generated nodes)
- All edge cases documented

**Contingency:**
- Simplify to start line only (skip column numbers)
- Allow `loc=None` for edge cases
- Add warning: "Line number unavailable for generated equations"
- Defer multi-line and include handling to Sprint 8 if needed

**Owner:** Convexity specialist

---

### Risk Summary Table

| # | Risk | Probability | Impact | Score | Mitigation Owner |
|---|------|-------------|--------|-------|------------------|
| 1 | Preprocessor complexity | Low (20%) | Medium | LOW | Parser specialist |
| 2 | pytest-xdist flaky tests | Medium (40%) | High | MEDIUM | Testing specialist |
| 3 | Parse rate goal unmet | Very Low (5%) | High | LOW | Parser specialist |
| 4 | Test performance goal unmet | Very Low (10%) | Medium | LOW | Testing specialist |
| 5 | Scope creep | Medium (30%) | Medium | MEDIUM | Sprint lead |
| 6 | CI workflow issues | Low (20%) | Low | LOW | CI/CD specialist |
| 7 | Line number edge cases | Low (15%) | Low | LOW | Convexity specialist |

**Overall Risk Level:** LOW-MEDIUM ✅  
**Confidence Level:** HIGH ✅

---

## 7. Deliverables

### 7.1 Code Deliverables

**Parser Enhancements:**
- `src/ir/preprocessor.py` - 3 new functions
  - `extract_conditional_sets()`
  - `expand_macros()`
  - `strip_conditional_directives()`
- `src/gams/grammar.lark` - Set range syntax rules
- `src/ir/parser.py` - Range expansion logic
- Unit tests: 20+ new tests

**Test Performance:**
- `pyproject.toml` - pytest-xdist configuration
- `.pytest.ini` - Worker count settings
- Test markers: `@pytest.mark.slow` (optional)
- CI configuration: `.github/workflows/test.yml` updated

**Convexity UX:**
- `src/ir/symbols.py` - `SourceLocation` dataclass
- `src/ir/parser.py` - `_extract_location()` helper
- `src/diagnostics/convexity.py` - Warning formatter updates
- Unit tests: 7 new tests + 1 E2E test

**CI Automation:**
- `scripts/check_parse_rate_regression.py` - 250+ lines
- `.github/workflows/gamslib-regression.yml` - Complete workflow

**Test Fixtures:**
- `tests/fixtures/preprocessor/` - 9 fixtures + YAML + README
- `tests/fixtures/sets/` - 8 fixtures + YAML + README
- `tests/fixtures/multidim/` - 8 fixtures + YAML + README
- `tests/fixtures/statements/` - 9 fixtures + YAML + README
- Total: 34 fixtures

### 7.2 Documentation Deliverables

**Sprint Planning:**
- ✅ `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (this document)
- ✅ `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` (updated Task 10)

**Research & Design:**
- ✅ `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (25 unknowns verified)
- ✅ `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md` (Task 2)
- ✅ `docs/research/preprocessor_directives.md` (Task 3)
- ✅ `docs/research/multidimensional_indexing.md` (Task 4)
- ✅ `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md` (Task 5)
- ✅ `docs/planning/EPIC_2/PARSER_ROADMAP.md` (Task 6)
- ✅ `docs/design/line_number_tracking.md` (Task 7)
- ✅ `docs/ci/gamslib_regression_tracking.md` (Task 8)
- ✅ `docs/testing/PARSER_FIXTURE_STRATEGY.md` (Task 9)

**Sprint Review:**
- `docs/planning/EPIC_2/SPRINT_7/RETROSPECTIVE.md` (to be created Day 10)
- `CHANGELOG.md` (updated with Sprint 7 changes)
- `PROJECT_PLAN.md` (Sprint 7 marked complete)

### 7.3 Release Deliverables

**Version 0.7.0:**
- Tag: `v0.7.0`
- GitHub release with notes
- Updated `pyproject.toml` version
- Updated `src/__init__.py` version

---

## 8. Cross-References

### 8.1 Prep Task Outputs

**Task 1: Known Unknowns**
- Document: `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`
- Status: ✅ COMPLETE (25 unknowns, all verified)
- Relevance: Risk identification and mitigation

**Task 2: GAMSLib Failure Analysis**
- Document: `docs/planning/EPIC_2/SPRINT_7/GAMSLIB_FAILURE_ANALYSIS.md`
- Status: ✅ COMPLETE (550+ lines)
- Relevance: Parser feature priorities (preprocessor 2.9%/h, set range 2.5%/h)

**Task 3: Preprocessor Directive Research**
- Document: `docs/research/preprocessor_directives.md`
- Status: ✅ COMPLETE (85 pages, 12 sections)
- Relevance: Implementation design (6-8h effort, mock/skip approach)

**Task 4: Multi-Dimensional Indexing Research**
- Document: `docs/research/multidimensional_indexing.md`
- Status: ✅ COMPLETE
- Relevance: Zero IR changes needed (tuple-based design already supports multi-dim)

**Task 5: Test Suite Performance Profiling**
- Document: `docs/planning/EPIC_2/SPRINT_7/TEST_PERFORMANCE_BASELINE.md`
- Status: ✅ COMPLETE (400+ lines)
- Relevance: 4-phase optimization plan (11-16h), Pareto analysis

**Task 6: GAMS Syntax Feature Survey**
- Document: `docs/planning/EPIC_2/PARSER_ROADMAP.md`
- Status: ✅ COMPLETE
- Relevance: Sprint 8-10 roadmap (52 features cataloged)

**Task 7: Line Number Tracking Design**
- Document: `docs/design/line_number_tracking.md`
- Status: ✅ COMPLETE (350+ lines)
- Relevance: 5-phase implementation plan (3-4h)

**Task 8: CI for GAMSLib Regression Tracking**
- Document: `docs/ci/gamslib_regression_tracking.md`
- Status: ✅ COMPLETE (85 pages)
- Relevance: Complete CI design (4-5h), workflow YAML

**Task 9: Parser Test Fixture Strategy**
- Document: `docs/testing/PARSER_FIXTURE_STRATEGY.md`
- Status: ✅ COMPLETE (1,096 lines)
- Relevance: 34 fixtures, 7-phase implementation plan

**Task 10: Detailed Sprint Plan**
- Document: `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (this document)
- Status: ✅ COMPLETE
- Relevance: 11-day breakdown, 5 checkpoints, effort estimates

### 8.2 Project Plan References

**PROJECT_PLAN.md Sprint 7:**
- Lines 1145-1192: Sprint 7 goals and deliverables
- Alignment: All 4 goals addressed in this plan
- Cross-check: Parser enhancements, test optimization, convexity, CI automation

**PRELIMINARY_PLAN.md:**
- Sprint 7 preliminary task breakdown
- Alignment: Detailed breakdown consistent with preliminary estimates
- Cross-check: Effort estimates match (34-45h vs 40-50h preliminary)

### 8.3 Sprint 6 References

**Sprint 6 Retrospective:**
- Lessons learned: Parser complexity underestimated → Led to comprehensive prep work
- Success patterns: YAML fixtures, parametrized tests → Replicated in Sprint 7
- Improvements: Line number tracking → Addressed in Goal 3

**Sprint 6 QA Report:**
- Test coverage: 88-90% → Maintain ≥88% in Sprint 7
- Pass rate: 99.8% (1,214 passed, 2 skipped, 1 xfailed) → Zero regressions allowed
- Performance: 107s (Sprint 6) → <60s target (Sprint 7)

---

## Appendix A: Daily Checklist Templates

### Day 0 Checklist

- [ ] Review all prep tasks (1-9) complete
- [ ] Verify all 25 Known Unknowns addressed
- [ ] Review all implementation designs
- [ ] Set up development environment
- [ ] Create Sprint 7 branch
- [ ] Sprint kickoff (if applicable)

### Day 1 Checklist

- [ ] Implement `extract_conditional_sets()`
- [ ] Implement `expand_macros()`
- [ ] Implement `strip_conditional_directives()`
- [ ] Test on circle.gms
- [ ] Test on maxmin.gms

### Day 2 Checklist

- [x] Integrate preprocessor into pipeline
- [x] Write 15+ preprocessor unit tests (17 integration tests added)
- [x] Handle `$eolCom` directive (already supported via grammar)
- [x] Update grammar with range syntax (numeric + symbolic)
- [x] Implement numeric range expansion (numeric + symbolic both implemented)

### Day 3 Checklist

- [ ] Implement alpha range expansion
- [ ] Implement prefix range expansion
- [ ] Implement macro range expansion
- [ ] Write range syntax unit tests
- [ ] Test edge cases

### Day 4 Checklist

- [ ] Test circle.gms end-to-end
- [ ] Test maxmin.gms end-to-end
- [ ] Test himmel16.gms end-to-end
- [ ] Attempt quick wins (optional)
- [ ] Fix integration issues

### Day 5 Checklist (Checkpoint 1)

- [ ] Run `make ingest-gamslib`
- [ ] Verify ≥30% parse rate
- [ ] Update dashboard
- [ ] Create 9 preprocessor fixtures
- [ ] Create 8 set range fixtures
- [ ] Verify Checkpoint 1 criteria

### Day 6 Checklist

- [ ] Install pytest-xdist
- [ ] Run `pytest -n 4` baseline
- [ ] Fix flaky tests (if any)
- [ ] Run stress test (10 iterations)
- [ ] Benchmark worker counts

### Day 7 Checklist (Checkpoint 2)

- [ ] Select optimal worker count
- [ ] Mark slow tests (optional)
- [ ] Configure CI with pytest-xdist
- [ ] Test CI workflow
- [ ] Verify <60s test suite
- [ ] Verify Checkpoint 2 criteria

### Day 8 Checklist

- [ ] Add `SourceLocation` dataclass
- [ ] Implement parser metadata extraction
- [ ] Preserve locations in normalization
- [ ] Update convexity warnings
- [ ] Test line number tracking
- [ ] Create 8 multidim fixtures

### Day 9 Checklist (Checkpoint 3)

- [ ] Implement `check_parse_rate_regression.py`
- [ ] Create CI workflow YAML
- [ ] Test workflow on PR
- [ ] Create 9 statement fixtures
- [ ] Verify Checkpoint 3 criteria

### Day 10 Checklist (Checkpoint 4)

- [ ] Run full test suite
- [ ] Run quality checks
- [ ] Test GAMSLib ingestion
- [ ] Update CHANGELOG.md
- [ ] Create retrospective
- [ ] Tag v0.7.0 release
- [ ] Verify Checkpoint 4 criteria

---

## Appendix B: Command Reference

### Development Commands

```bash
# Parser testing
pytest tests/unit/parser/ -v

# Preprocessor testing
pytest tests/unit/parser/test_preprocessor.py -v

# Set range testing
pytest tests/unit/parser/test_sets.py -v

# GAMSLib ingestion
make ingest-gamslib

# View dashboard
open reports/gamslib_conversion_status.md
```

### Test Performance Commands

```bash
# Run tests with parallelization
pytest tests/ -n 4

# Benchmark different worker counts
pytest tests/ -n 2
pytest tests/ -n 4
pytest tests/ -n 8
pytest tests/ -n 16

# Run fast tests only (if marked)
pytest tests/ -m "not slow" -n 4

# Time test suite
time pytest tests/
```

### Quality Checks

```bash
# Type checking
make typecheck

# Linting
make lint

# Formatting
make format

# All quality checks
make typecheck && make lint && make format

# Full test suite
make test
```

### CI/CD Commands

```bash
# Test regression detection locally
python scripts/check_parse_rate_regression.py \
  --current reports/gamslib_conversion_status.json \
  --baseline-file reports/baseline_parse_rate.json \
  --threshold 0.10

# Test CI workflow locally (with act)
act pull_request -W .github/workflows/gamslib-regression.yml
```

### Release Commands

```bash
# Update version
vim pyproject.toml  # Update version = "0.7.0"
vim src/__init__.py  # Update __version__ = "0.7.0"

# Commit and tag
git commit -m "Bump version to 0.7.0"
git tag v0.7.0
git push origin main --tags

# Create GitHub release
gh release create v0.7.0 --notes "Sprint 7 Release Notes"
```

---

**End of Sprint 7 Detailed Plan**
