# Day 1 Prompt: Test Infrastructure - Part 1

**Branch:** Create a new branch named `sprint9-day1-test-infrastructure-part1` from `sprint9-advanced-features`

**Objective:** Document mhw4dx secondary blockers (defer to Sprint 10), implement automated test fixture generation framework, and begin performance optimization by identifying slow tests.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 169-285) - Day 1 detailed plan
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 2) - mhw4dx research findings
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 6) - Automated fixture design
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.3.1, 9.3.5) - Fixture framework and secondary blocker unknowns
- Verify Day 0 baseline complete (parse rate: 40%, fast tests: 52.39s)

**Tasks to Complete (5-7 hours):**

1. **Analyze mhw4dx secondary blockers** (2-3 hours)
   - Review Task 2 findings from PREP_PLAN.md
   - Parse mhw4dx.gms and capture ALL parse errors (not just first)
   - For each blocker, estimate implementation effort:
     - Grammar changes required
     - Semantic handler complexity
     - IR representation needs
     - Test coverage requirements
   - Sum total effort for all mhw4dx blockers
   - Expected finding: 12-17h total effort (too large for Sprint 9)
   - Decision framework from PLAN.md (lines 207-218):
     - If effort <8h: Consider including in Sprint 9
     - If effort 8-12h: Defer to Sprint 10, document as "next priority"
     - If effort >12h: Defer to Sprint 10, mark as "complex feature requiring dedicated sprint"

2. **Document blocker findings in BLOCKERS.md** (30 minutes)
   - Create `docs/blockers/mhw4dx_analysis.md` with structure:
     ```markdown
     # mhw4dx.gms Secondary Blocker Analysis
     
     **Date:** 2025-XX-XX
     **Status:** DEFERRED to Sprint 10
     **Reason:** Total effort 12-17h exceeds Sprint 9 budget
     
     ## Primary Blocker (from Sprint 8)
     [Primary blocker that was addressed]
     
     ## Secondary Blockers Identified
     
     ### Blocker 1: [Feature Name]
     - **Error:** [Parse error message]
     - **Location:** Line XXX in mhw4dx.gms
     - **Required Work:**
       - Grammar: [description] (Xh)
       - Semantic: [description] (Xh)
       - IR: [description] (Xh)
       - Tests: [description] (Xh)
     - **Total Effort:** X-Yh
     
     [Repeat for each blocker]
     
     ## Total Effort Estimate
     - Conservative: XXh
     - Realistic: XXh
     - Upper bound: XXh
     
     ## Decision
     **DEFER to Sprint 10** - Effort exceeds Sprint 9 budget
     
     ## Recommendation for Sprint 10
     [Priority order for addressing blockers]
     ```
   - Reference this file from GAMSLIB_FEATURE_MATRIX.md

3. **Implement fixture generation framework** (1-2 hours)
   - Create `tests/fixtures/generate_fixtures.py` based on Task 6 design
   - Implement key functions:
     ```python
     def create_variable_fixture(name: str, type: str, bounds: tuple) -> VariableDeclaration:
         """Generate IR VariableDeclaration node."""
         pass
     
     def create_parameter_fixture(name: str, value: float) -> ParameterDeclaration:
         """Generate IR ParameterDeclaration node."""
         pass
     
     def create_equation_fixture(name: str, expr: str) -> EquationDeclaration:
         """Generate IR EquationDeclaration node."""
         pass
     
     def create_model_fixture(variables: list, parameters: list, equations: list) -> ModelIR:
         """Generate complete IR tree for a model."""
         pass
     ```
   - Use template-based generation for common patterns
   - Support parameterization (e.g., number of variables, equation complexity)
   - Example usage reduces fixture code from 50 lines to 5-10 lines
   - Validation happens at generation time (fail fast on invalid fixtures)
   - Generated fixtures are deterministic (same inputs → same IR)

4. **Write tests for fixture generator** (30 minutes)
   - Create `tests/test_fixture_generator.py`
   - Test cases:
     - `test_create_variable_fixture_positive()` - positive variable with bounds
     - `test_create_variable_fixture_free()` - free variable (no bounds)
     - `test_create_parameter_fixture()` - parameter with scalar value
     - `test_create_equation_fixture()` - equation with simple expression
     - `test_create_model_fixture()` - complete model with variables, parameters, equations
     - `test_fixture_validation()` - invalid inputs raise errors
   - Verify generated fixtures are valid IR (can be serialized/deserialized)
   - Test coverage ≥80% for fixture generator

5. **Identify slow tests (pytest --durations=20)** (30 minutes)
   - Run `pytest --durations=20` to identify slowest tests
   - Expected findings from Task 9:
     - Full GAMSLib ingest: ~15-20s per model (currently marked slow ✅)
     - Complex IR validation tests: ~2-3s each
     - Dashboard generation tests: ~1-2s each
   - Create "slow test candidates" list in `docs/performance/slow_tests_day1.md`:
     ```markdown
     # Slow Test Candidates (Day 1)
     
     ## Tests >3 seconds
     1. test_file_name::test_name - 5.23s - Candidate for @pytest.mark.slow
     2. test_file_name::test_name - 3.45s - Candidate for @pytest.mark.slow
     
     ## Tests 1-3 seconds
     1. test_file_name::test_name - 2.1s - Review on Day 2
     2. test_file_name::test_name - 1.8s - Review on Day 2
     
     ## Target
     Identify ≥10 tests >1s for slow markers on Day 2
     ```
   - Target: Identify ≥10 tests >1s that can be marked slow

**Deliverables:**
- `docs/blockers/mhw4dx_analysis.md` - Secondary blocker documentation with effort estimates and defer decision
- `tests/fixtures/generate_fixtures.py` - Automated fixture generation framework
- `tests/test_fixture_generator.py` - Fixture generator tests (≥80% coverage)
- `docs/performance/slow_tests_day1.md` - Slow test candidates list

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] mhw4dx blockers documented with effort estimate (expected: 12-17h)
  - [ ] Decision documented: DEFER mhw4dx to Sprint 10
  - [ ] Fixture generator creates valid IR for ≥3 fixture types (variables, parameters, equations)
  - [ ] Fixture generator tests pass with ≥80% coverage
  - [ ] Slow test list identified (≥10 tests >1s each)
  - [ ] All quality checks pass: `make typecheck && make lint && make format && make test`
- [ ] Mark Day 1 as complete in `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (line 287)
- [ ] Check off Day 1 in README.md
- [ ] Log Day 1 completion to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 9 Day 1: Test Infrastructure - Part 1" \
                --body "Completes Day 1 tasks from Sprint 9 PLAN.md

   - Analyzed mhw4dx secondary blockers (12-17h effort)
   - Documented defer decision in docs/blockers/mhw4dx_analysis.md
   - Implemented automated fixture generation framework
   - Fixture generator creates valid IR for variables, parameters, equations
   - All fixture tests pass (≥80% coverage)
   - Identified XX slow tests for Day 2 markers
   
   Ready to proceed with Day 2 (Fixture validation + performance optimization)." \
                --base sprint9-advanced-features
   ```
2. Request a review from Copilot:
   ```bash
   gh pr edit --add-reviewer copilot
   ```
3. Wait for Copilot's review to be completed
4. Address all review comments
5. Once approved, merge the PR

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 169-285) - Day 1 detailed plan with implementation details
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 2, Task 6) - mhw4dx research and fixture design
- `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknowns 9.3.1, 9.3.5) - Fixture and blocker unknowns
- `docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md` (lines 362-412) - Sprint 8 lessons (fixture issues, performance)

**Notes:**
- Effort: 5-7h (2-3h analysis + 0.5h docs + 1-2h implementation + 0.5h tests + 0.5h profiling)
- mhw4dx defer decision is expected outcome (12-17h > Sprint 9 budget)
- Fixture generator uses Python AST to create type-safe IR nodes
- Generated fixtures are deterministic and validated at generation time
- Slow test identification prepares for Day 2 marker application
