# Sprint 7 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 7 (Days 0-10). Each prompt is designed to be used when starting work on that specific day.

---

## Day 0 Prompt: Pre-Sprint Setup & Kickoff

**Branch:** Create a new branch named `sprint7-day0-setup` from `main`

**Objective:** Complete prep work verification and sprint kickoff

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` - All 9 prep tasks should be complete
- Read `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` - All 25 unknowns verified
- Review these design documents:
  - `docs/research/preprocessor_directives.md`
  - `docs/research/multidimensional_indexing.md`
  - `docs/research/line_number_tracking.md`
  - `docs/research/gamslib_regression_tracking.md`
  - `docs/testing/PARSER_FIXTURE_STRATEGY.md`

**Tasks to Complete (6-8 hours):**

1. **Verify all prep tasks (1-9) complete**
   - Review PREP_PLAN.md and confirm all tasks marked complete
   - Verify all Known Unknowns have been verified

2. **Set up development environment** (2 hours)
   - Verify Python dependencies are up to date: `pip list`
   - Install pytest-xdist but don't enable yet: `pip install pytest-xdist`
   - Verify CI access and permissions
   - Validate GAMSLib data available in `data/gamslib/`

3. **Create fixture directory structure** (2 hours)
   - Create `tests/fixtures/preprocessor/` directory
   - Create `tests/fixtures/sets/` directory
   - Create `tests/fixtures/multidim/` directory
   - Create `tests/fixtures/statements/` directory
   - Create template `expected_results.yaml` files in each directory
   - Create template `README.md` files in each directory

4. **Sprint planning and kickoff** (2-3 hours)
   - Review daily goals from PLAN.md
   - Review all 4 sprint goals and 5 checkpoints
   - Review risk register and mitigation plans

**Deliverables:**
- All prep tasks verified complete
- Development environment ready
- Sprint 7 branch created
- All 4 fixture directories created with templates
- Sprint kickoff complete

**Quality Checks:**
- N/A for Day 0 (setup only, no code changes)

**Completion Criteria:**
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off all Checkpoint 0 criteria in PLAN.md
- [ ] Check off Day 0 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 0: Pre-Sprint Setup & Kickoff" \
                --body "Completes Day 0 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 198-244)
- `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md`
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md`

---

## Day 1 Prompt: Preprocessor Directives (Part 1)

**Branch:** Create a new branch named `sprint7-day1-preprocessor-part1` from `main`

**Objective:** Implement preprocessor directive mock handling (50%)

**Prerequisites:**
- Read `docs/research/preprocessor_directives.md` - Complete design for preprocessor handling
- Review `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` - Unknowns 1.1, 1.2, 1.3 (preprocessor blocking models)
- Ensure GAMSLib models circle.gms and maxmin.gms are available in `data/gamslib/`

**Tasks to Complete (6-8 hours):**

1. **Implement Core Functions** (3-4 hours)
   - Implement `extract_conditional_sets()` in `src/ir/preprocessor.py` (1.5h)
     - Extract defaults from `$if not set` directives
     - Handle `$if not set i $set i "default"`
   - Implement `expand_macros()` in `src/ir/preprocessor.py` (2h)
     - Expand `%macro%` references
     - Support user-defined and system macros
   - Implement `strip_conditional_directives()` in `src/ir/preprocessor.py` (0.5h)
     - Replace directives with comments
     - Preserve line numbers

2. **Write Unit Tests** (2-2.5 hours)
   - Test `extract_conditional_sets()` with various patterns (5 tests)
   - Test `expand_macros()` with user-defined and system macros (5 tests)
   - Test `strip_conditional_directives()` edge cases (3 tests)
   - Test error handling (missing macros, invalid syntax)
   - Place tests in `tests/unit/ir/test_preprocessor.py`

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

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `extract_conditional_sets()` extracts defaults correctly
  - [ ] `expand_macros()` expands user-defined and system macros
  - [ ] circle.gms preprocesses without errors
  - [ ] maxmin.gms preprocesses without errors
  - [ ] All 13+ unit tests pass
  - [ ] Code reviewed and documented
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 1 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 1: Preprocessor Directives (Part 1)" \
                --body "Completes Day 1 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 247-290)
- `docs/research/preprocessor_directives.md`
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (Unknowns 1.1, 1.2, 1.3)

---

## Day 2 Prompt: Preprocessor Directives (Part 2) + Set Range Syntax (Part 1)

**Branch:** Create a new branch named `sprint7-day2-preprocessor-part2-ranges-part1` from `main`

**Objective:** Complete preprocessor implementation and start set range syntax

**Prerequisites:**
- Day 1 must be complete (preprocessor core functions implemented)
- Read `docs/research/preprocessor_directives.md` - Full preprocessor design
- Review `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` - Unknown 1.5 (set range syntax)
- Review `src/gams/grammar.lark` - Current grammar structure

**Tasks to Complete (6-8 hours):**

1. **Complete Preprocessor Integration** (3-4 hours)
   - Integrate preprocessor functions into `preprocess_gams_file()` pipeline (0.5h)
   - Write comprehensive unit tests (15+ tests) (2h)
   - Handle `$eolCom` directive for end-of-line comments (1h)
   - Add integration tests with preprocessor pipeline (0.5h)

2. **Start Set Range Syntax** (2-2.5 hours)
   - Update `src/gams/grammar.lark` with range syntax rules (1h)
     - Support `Set i / 1*6 /` syntax
     - Support `Set j / s1*s10 /` syntax
   - Implement range expansion logic for numeric ranges (1h)
     - Expand `1*6` to `1, 2, 3, 4, 5, 6`
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

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 15+ preprocessor unit tests pass
  - [ ] Preprocessor integrated into main pipeline
  - [ ] Grammar accepts `Set i / 1*6 /` syntax
  - [ ] Numeric range expansion generates correct elements
  - [ ] Error handling comprehensive
  - [ ] Documentation complete
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 2 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 2: Preprocessor (Part 2) + Set Range Syntax (Part 1)" \
                --body "Completes Day 2 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 292-329)
- `docs/research/preprocessor_directives.md`
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (Unknown 1.5)

---

## Day 3 Prompt: Set Range Syntax (Part 2)

**Branch:** Create a new branch named `sprint7-day3-set-ranges-part2` from `main`

**Objective:** Complete set range syntax implementation

**Prerequisites:**
- Day 2 must be complete (numeric ranges working)
- Review `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` - Unknown 1.5 (set range patterns)
- Ensure himmel16.gms is available in `data/gamslib/`

**Tasks to Complete (6.5-8 hours):**

1. **Complete Range Expansion** (3-3.5 hours)
   - Implement alpha ranges: `s1*s10` → `s1, s2, ..., s10` (1h)
   - Implement prefix ranges: `p1*p100` → `p1, p2, ..., p100` (1h)
   - Implement ranges with macros: `1*%n%` (0.5h)
   - Integration with preprocessor (macro expansion in ranges) (1h)

2. **Comprehensive Unit Tests** (2-2.5 hours)
   - Test all 4 range types: numeric, alpha, prefix, macro (8 tests)
   - Test edge cases: single element, large ranges, empty ranges (5 tests)
   - Test macro integration (3 tests)
   - Test error handling: invalid ranges (2 tests)
   - Total: 18+ tests

3. **Integration Tests and Documentation** (1.5-2 hours)
   - Create integration test suite for set ranges
   - Test himmel16.gms end-to-end (uses set ranges)
   - Document range syntax with examples
   - Add grammar documentation

**Deliverables:**
- Set range syntax fully implemented
- All range types working
- 18+ unit tests passing
- Integration tests complete
- Documentation updated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All 4 range types expand correctly
  - [ ] himmel16.gms parses successfully
  - [ ] Unit tests cover all range patterns
  - [ ] Integration with preprocessor working
  - [ ] All 18+ tests passing
  - [ ] Documentation complete
- [ ] Mark Day 3 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 3 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 3: Set Range Syntax (Part 2)" \
                --body "Completes Day 3 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 332-371)
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (Unknown 1.5)

---

## Day 4 Prompt: Parser Integration & Testing + Quick Wins

**Branch:** Create a new branch named `sprint7-day4-integration-quick-wins` from `main`

**Objective:** Integrate parser enhancements, test on GAMSLib, and implement quick wins for 40-50% parse rate

**Prerequisites:**
- Days 1-3 must be complete (preprocessor and set ranges fully implemented)
- Review `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` - Unknowns 1.1-1.5
- Ensure all 10 GAMSLib models available in `data/gamslib/`
- Read prep analysis: circle.gms, maxmin.gms, himmel16.gms, trig.gms, mathopt1.gms

**Tasks to Complete (6-8 hours):**

1. **Integration Testing** (2-3 hours)
   - Test circle.gms end-to-end (preprocessor)
   - Test maxmin.gms end-to-end (preprocessor)
   - Test himmel16.gms end-to-end (set ranges)
   - Fix any integration issues
   - Create integration test suite

2. **Quick Win: Multiple Scalar Declarations** (2-3 hours) - REQUIRED
   - Update `src/gams/grammar.lark` to support `Scalars a, b, c;` syntax
   - Implement parser support for multiple scalars in one statement
   - Write unit tests (5+ tests)
   - Test on trig.gms
   - This unlocks trig.gms → +10% parse rate

3. **Quick Win: Models Keyword** (1-2 hours) - REQUIRED
   - Add `Models` (plural) keyword support to grammar
   - Implement parser handling for multiple model declarations
   - Write unit tests (3+ tests)
   - Test on mathopt1.gms
   - This unlocks mathopt1.gms → +10% parse rate

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

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] circle.gms parses (preprocessor working)
  - [ ] maxmin.gms parses (preprocessor working)
  - [ ] himmel16.gms parses (set range working)
  - [ ] trig.gms parses (multiple scalars - REQUIRED)
  - [ ] mathopt1.gms parses (models keyword - REQUIRED)
  - [ ] Parse rate = 50% (5/10 models)
  - [ ] All integration tests pass
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 4 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 4: Parser Integration & Testing + Quick Wins" \
                --body "Completes Day 4 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 374-423)
- `docs/planning/EPIC_2/SPRINT_7/KNOWN_UNKNOWNS.md` (Unknowns 1.1-1.5)

---

## Day 5 Prompt: GAMSLib Retest & Checkpoint 1

**Branch:** Create a new branch named `sprint7-day5-gamslib-checkpoint1` from `main`

**Objective:** Verify 30%+ parse rate achieved (Checkpoint 1)

**Prerequisites:**
- Day 4 must be complete (5 models parsing at 50% rate)
- Review `docs/testing/PARSER_FIXTURE_STRATEGY.md` - Fixture creation guidelines
- Ensure fixture directories created in Day 0

**Tasks to Complete (6-8 hours):**

1. **GAMSLib Full Retest** (1 hour)
   - Run `make ingest-gamslib`
   - Update dashboard with new parse rate
   - Verify ≥3 models parsing (30% minimum)
   - Target: 5 models parsing (50%)

2. **Parser Fixture Creation** (4-5 hours)
   - Create 9 preprocessor fixtures in `tests/fixtures/preprocessor/`
     - Cover `$if not set`, `%macro%`, `$eolCom`
   - Create 8 set range fixtures in `tests/fixtures/sets/`
     - Cover numeric, alpha, prefix, macro ranges
   - Create `expected_results.yaml` files for each fixture
   - Create `README.md` files documenting each fixture category
   - Document fixture patterns and edge cases

3. **Checkpoint 1 Review** (1-2 hours)
   - Review acceptance criteria
   - Document any issues or risks
   - Plan Week 2 work (Days 6-7: test performance)
   - Update project documentation

**Deliverables:**
- GAMSLib parse rate ≥30% (Checkpoint 1)
- 17 parser fixtures created (9 preprocessor + 8 set range)
- Dashboard updated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All Checkpoint 1 acceptance criteria met:
  - [ ] GAMSLib parse rate ≥30% (3/10 models minimum)
  - [ ] circle.gms, maxmin.gms, himmel16.gms parsing
  - [ ] Dashboard updated with new parse rate
  - [ ] ≥17 parser fixtures created with expected results
  - [ ] All parser unit tests passing
- [ ] Mark Day 5 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off all Checkpoint 1 criteria in PLAN.md
- [ ] Check off Day 5 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 5: GAMSLib Retest & Checkpoint 1" \
                --body "Completes Day 5 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 426-462)
- `docs/testing/PARSER_FIXTURE_STRATEGY.md`

---

## Day 6 Prompt: Test Performance (Part 1) - pytest-xdist

**Branch:** Create a new branch named `sprint7-day6-pytest-xdist` from `main`

**Objective:** Enable pytest-xdist parallelization

**Prerequisites:**
- Review `docs/research/test_performance_optimization.md` (if exists)
- pytest-xdist should be installed from Day 0
- Baseline: Current test suite runs in ~208 seconds

**Tasks to Complete (6-8 hours):**

1. **Install and Configure** (1 hour)
   - Ensure pytest-xdist is installed: `pip install pytest-xdist`
   - Update `pyproject.toml` configuration for pytest-xdist
   - Document usage in README

2. **Baseline Testing** (1.5-2 hours)
   - Run `pytest -n 4` baseline test
   - Identify any flaky tests
   - Fix test isolation issues
   - Verify all 1,217 tests pass in parallel

3. **Stress Testing** (3.5-5 hours)
   - Run 10 iterations: `for i in {1..10}; do pytest -n 4; done`
   - Each iteration will take ~60-70s = 10-12 minutes minimum
   - Document any intermittent failures
   - Fix race conditions and shared state issues
   - Debug and resolve flaky tests
   - Additional buffer for unexpected isolation issues

**Deliverables:**
- pytest-xdist enabled
- All tests passing in parallel with no flakiness
- Stability verified across 10 consecutive runs
- All isolation issues resolved

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass (including `pytest -n 4`)

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] `pytest -n 4` runs successfully
  - [ ] All 1,217 tests pass in parallel
  - [ ] Zero flaky tests detected across 10 runs
  - [ ] All race conditions and shared state issues fixed
- [ ] Mark Day 6 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 6 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 6: Test Performance (Part 1) - pytest-xdist" \
                --body "Completes Day 6 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 465-502)

---

## Day 7 Prompt: Test Performance (Part 2) & Checkpoint 2

**Branch:** Create a new branch named `sprint7-day7-test-optimization-checkpoint2` from `main`

**Objective:** Achieve fast test suite <60s, full test suite <120s (Checkpoint 2)

**Prerequisites:**
- Day 6 must be complete (pytest-xdist enabled, all tests passing)
- Review `docs/research/test_performance_optimization.md` (if exists)

**Tasks to Complete (6-8 hours):**

1. **Benchmark Worker Counts** (1.5-2 hours)
   - Test with 2, 4, 8, 16 workers
   - Plot speedup curve
   - Measure overhead (expect 15-25%)
   - Document optimal worker count

2. **Optimize Worker Count** (0.5-1 hour)
   - Analyze benchmark results
   - Select optimal worker count (likely 4-8)
   - Configure as default in pyproject.toml

3. **Mark Slow Tests** (1.5-2 hours)
   - Identify 5-10 slowest tests
   - Add `@pytest.mark.slow` decorator
   - Create fast test suite config
   - Verify fast suite <60s and full suite <120s

4. **CI Configuration** (2-3 hours)
   - Enable pip/pytest caching in `.github/workflows/`
   - Configure pytest-xdist in CI: `pytest -n auto`
   - Set timeout to 15 minutes
   - Test CI workflow on PR

5. **Checkpoint 2 Review** (0.5-1 hour)
   - Verify fast <60s, full <120s achieved
   - Document speedup results
   - Plan Week 3 work (Days 8-10)

**Deliverables:**
- Worker count benchmarks complete (Checkpoint 2)
- Fast test suite <60s, Full test suite <120s (Checkpoint 2)
- CI optimized with parallelization
- Slow tests marked for fast test suite

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass
5. Verify: `time pytest -m "not slow" -n 4 tests/` → <60s
6. Verify: `time pytest -n 4 tests/` → <120s

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All Checkpoint 2 acceptance criteria met:
  - [ ] Fast test suite <60s (verified with `pytest -m "not slow" -n 4`)
  - [ ] Full test suite <120s (verified with `pytest -n 4`)
  - [ ] CI test time <5 minutes
  - [ ] All tests passing with parallelization
  - [ ] Zero regressions from Sprint 6
- [ ] Mark Day 7 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off all Checkpoint 2 criteria in PLAN.md
- [ ] Check off Day 7 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 7: Test Performance (Part 2) & Checkpoint 2" \
                --body "Completes Day 7 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 505-551)

---

## Day 8 Prompt: Convexity UX + Multi-Dim Fixtures

**Branch:** Create a new branch named `sprint7-day8-line-numbers-multidim` from `main`

**Objective:** Implement line number tracking and create multi-dim fixtures

**Prerequisites:**
- Review `docs/research/line_number_tracking.md` - Design for line number tracking
- Review `docs/research/multidimensional_indexing.md` - Multi-dim patterns (already work, need fixtures)
- Review `docs/testing/PARSER_FIXTURE_STRATEGY.md` - Fixture guidelines

**Tasks to Complete (6-8 hours):**

1. **Line Number Tracking** (3.5-5 hours)
   - Phase 1: IR Structure (1h)
     - Add `SourceLocation` dataclass to IR
     - Add line/column fields to AST nodes
   - Phase 2: Parser Integration (1-1.5h)
     - Extract Lark metadata (line, column)
     - Populate SourceLocation in parser
   - Phase 3: Normalization Preservation (0.5-1h)
     - Preserve line numbers through normalization
   - Phase 4: Convexity Integration (0.5-1h)
     - Update convexity warnings to include line numbers
     - Format: `"W301 in equation 'eq' (file.gms:15:8)"`
   - Phase 5: Testing (0.5-1h)
     - Write 7+ unit tests for line number tracking
     - Create 1 E2E test
   - Phase 6: Documentation and edge cases (0.5h)
     - Document line number tracking
     - Handle edge cases gracefully

2. **Multi-Dim Fixtures** (2.5-3 hours)
   - Create 8 multidimensional fixtures in `tests/fixtures/multidim/`
   - Create `expected_results.yaml` for each
   - Create `README.md` documenting multidimensional patterns
   - Document multidimensional patterns

**Deliverables:**
- Line numbers in all convexity warnings
- 8 multidim fixtures created

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] 100% of convexity warnings show line numbers
  - [ ] Warning format: `"W301 in equation 'eq' (file.gms:15:8)"`
  - [ ] All edge cases handled gracefully
  - [ ] 8 multidim fixtures created
- [ ] Mark Day 8 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off Day 8 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 8: Convexity UX + Multi-Dim Fixtures" \
                --body "Completes Day 8 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 554-584)
- `docs/research/line_number_tracking.md`
- `docs/research/multidimensional_indexing.md`
- `docs/testing/PARSER_FIXTURE_STRATEGY.md`

---

## Day 9 Prompt: CI Automation + Statement Fixtures & Checkpoint 3

**Branch:** Create a new branch named `sprint7-day9-ci-automation-checkpoint3` from `main`

**Objective:** Complete CI automation and all fixtures (Checkpoint 3)

**Prerequisites:**
- Review `docs/research/gamslib_regression_tracking.md` - CI automation design
- Review `docs/testing/PARSER_FIXTURE_STRATEGY.md` - Statement fixture guidelines

**Tasks to Complete (6-8 hours):**

1. **GAMSLib Regression CI** (3.5-5 hours)
   - Implement `scripts/check_parse_rate_regression.py` (2h)
     - Read baseline parse rate from file
     - Run GAMSLib ingestion
     - Compare new vs baseline
     - Fail if regression >10% relative
   - Create `.github/workflows/gamslib-regression.yml` (1.5-3h)
     - Hybrid trigger: path filter + weekly cron
     - Run on GAMSLib changes or weekly
     - Store results as artifacts
   - Test workflow on PR
   - Verify regression detection

2. **Statement Fixtures** (2-2.5 hours)
   - Create 9 statement fixtures in `tests/fixtures/statements/`
   - Create `expected_results.yaml` for each
   - Create `README.md` documenting statement patterns

3. **Checkpoint 3 Review** (0.5-1 hour)
   - Verify all features integrated
   - Verify CI working
   - Plan Day 10 release

**Deliverables:**
- CI automation complete (Checkpoint 3)
- 34 total fixtures created (9 preprocessor + 8 set range + 8 multidim + 9 statement)
- All features integrated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All Checkpoint 3 acceptance criteria met:
  - [ ] GAMSLib regression CI workflow active
  - [ ] All 34 fixtures created (9+8+8+9)
  - [ ] Line number tracking working
  - [ ] Test suite <60s
  - [ ] Parse rate ≥30%
  - [ ] Zero failing tests
- [ ] Mark Day 9 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off all Checkpoint 3 criteria in PLAN.md
- [ ] Check off Day 9 in `README.md`
- [ ] Log progress to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 9: CI Automation + Statement Fixtures & Checkpoint 3" \
                --body "Completes Day 9 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 587-622)
- `docs/research/gamslib_regression_tracking.md`
- `docs/testing/PARSER_FIXTURE_STRATEGY.md`

---

## Day 10 Prompt: Sprint Review, Release & Checkpoint 4

**Branch:** Create a new branch named `sprint7-day10-release-checkpoint4` from `main`

**Objective:** Complete Sprint 7, release v0.7.0 (Checkpoint 4)

**Prerequisites:**
- All Days 0-9 must be complete
- All 4 sprint goals should be achieved
- All quality checks passing

**Tasks to Complete (6-8 hours):**

1. **Final QA** (2-2.5 hours)
   - Run full test suite: `pytest tests/`
   - Run quality checks: `make typecheck lint format`
   - Test GAMSLib ingestion: `make ingest-gamslib`
   - Verify all 4 sprint goals met:
     - Goal 1: Parse rate ≥30% (target 40-50%)
     - Goal 2: Fast <60s, Full <120s
     - Goal 3: 100% warnings show line numbers
     - Goal 4: CI automation active

2. **Documentation** (2-2.5 hours)
   - Update `CHANGELOG.md` with Sprint 7 changes
   - Update `docs/planning/EPIC_2/PROJECT_PLAN.md` - Mark Sprint 7 complete
   - Create `docs/planning/EPIC_2/SPRINT_7/RETROSPECTIVE.md`
     - What went well
     - What could be improved
     - Lessons learned
     - Metrics vs goals
   - Update version to 0.7.0 in `pyproject.toml`

3. **Release** (1-1.5 hours)
   - Tag v0.7.0 release: `git tag -a v0.7.0 -m "Sprint 7: Parser enhancements, test performance, convexity UX, CI automation"`
   - Create GitHub release notes
   - Update README if needed

4. **Sprint Review** (1-2 hours)
   - Demo new features:
     - Preprocessor directives
     - Set range syntax
     - Line number tracking
     - GAMSLib regression CI
   - Review metrics vs goals
   - Identify lessons learned
   - Plan Sprint 8 prep

**Deliverables:**
- v0.7.0 released (Checkpoint 4)
- Sprint retrospective complete
- All documentation updated

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All Checkpoint 4 acceptance criteria met:
  - [ ] All 4 sprint goals achieved
  - [ ] v0.7.0 tagged and released
  - [ ] CHANGELOG.md updated
  - [ ] Retrospective complete
  - [ ] All quality checks passing
  - [ ] Sprint review conducted
- [ ] Mark Day 10 as complete in `docs/planning/EPIC_2/SPRINT_7/PLAN.md`
- [ ] Check off all Checkpoint 4 criteria in PLAN.md
- [ ] Check off Day 10 in `README.md`
- [ ] Log final Sprint 7 summary to `CHANGELOG.md`

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 7 Day 10: Sprint Review, Release & Checkpoint 4" \
                --body "Completes Day 10 tasks from Sprint 7 PLAN.md" \
                --base main
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments:
   - Read each comment carefully
   - Make necessary fixes
   - Commit and push fixes
   - Reply to comments indicating fixes made
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_7/PLAN.md` (lines 625-663)
- `docs/planning/EPIC_2/PROJECT_PLAN.md`

---

## Usage Instructions

**For each day:**

1. **Start of day:**
   - Read the full prompt for that day
   - Review all prerequisite documents
   - Create the specified branch
   - Review tasks and time estimates

2. **During the day:**
   - Complete tasks in order
   - Run quality checks after each significant change
   - Track progress against time estimates

3. **End of day:**
   - Verify all deliverables complete
   - Run final quality checks
   - Check off completion criteria
   - Update PLAN.md, README.md, and CHANGELOG.md
   - Commit and push changes

4. **Quality checks reminder:**
   - ALWAYS run `make typecheck`, `make lint`, `make format`, `make test` before committing code changes
   - Skip quality checks only for documentation-only commits

---

## Notes

- Each prompt is designed to be self-contained
- Prerequisites ensure you have necessary context
- Quality checks ensure code quality throughout
- Completion criteria provide clear definition of "done"
- All prompts reference specific line numbers in PLAN.md for detailed task descriptions
