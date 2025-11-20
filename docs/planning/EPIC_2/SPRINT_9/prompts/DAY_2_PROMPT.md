# Day 2 Prompt: Test Infrastructure - Part 2 → CHECKPOINT 1

**Branch:** Create a new branch named `sprint9-day2-test-infrastructure-part2-checkpoint1` from `sprint9-advanced-features`

**Objective:** Implement fixture validation script, establish performance baseline by applying slow test markers, and achieve Checkpoint 1 (Test infrastructure complete).

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 287-338) - Day 2 detailed plan
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 7) - Fixture validation design
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` (Unknown 9.3.2) - Fixture validation unknowns
- Verify Day 1 complete: Fixture generator working, slow test list identified
- Review `docs/performance/slow_tests_day1.md` from Day 1

**Tasks to Complete (1-2 hours):**

1. **Implement fixture validation script** (1 hour)
   - Create `scripts/validate_fixtures.py` based on Task 7 design
   - Validate 5 fixture error types from Sprint 8 lessons:
     1. **Missing expected_results.yaml** - Every fixture directory must have this file
     2. **Incorrect statement counts** - Actual statements don't match expected_results.yaml count
     3. **Incorrect line numbers** - Source line numbers don't match expected_results.yaml
     4. **Invalid YAML syntax** - expected_results.yaml must parse correctly
     5. **Missing source file** - Fixture directory must have .gms or source file
   - Script structure:
     ```python
     def validate_fixtures(fixture_dir: Path) -> list[ValidationError]:
         """Validate all fixtures in directory."""
         errors = []
         for fixture in find_fixtures(fixture_dir):
             errors.extend(validate_fixture_structure(fixture))
             errors.extend(validate_expected_results(fixture))
             errors.extend(validate_statement_counts(fixture))
             errors.extend(validate_line_numbers(fixture))
         return errors
     
     def main():
         errors = validate_fixtures(Path("tests/fixtures"))
         if errors:
             print(f"Found {len(errors)} validation errors:")
             for error in errors:
                 print(f"  - {error}")
             sys.exit(1)
         print("All fixtures valid!")
     ```
   - Exit code 1 if any errors found (for CI integration)
   - Verbose mode shows all checked fixtures

2. **Apply @pytest.mark.slow to identified slow tests** (30 minutes)
   - Review `docs/performance/slow_tests_day1.md` from Day 1
   - Add `@pytest.mark.slow` decorator to ≥10 tests identified as >1s
   - Update test files with slow markers
   - Typical candidates (from Task 9 research):
     - Full GAMSLib ingest tests (already marked ✅)
     - Complex IR validation tests
     - Dashboard generation tests
     - Integration tests with file I/O
   - Update `pyproject.toml` if slow marker not already configured:
     ```toml
     [tool.pytest.ini_options]
     markers = [
         "slow: marks tests as slow (deselect with '-m \"not slow\"')"
     ]
     ```

3. **Re-baseline fast test performance** (15 minutes)
   - Run fast test suite (excluding slow): `pytest -m "not slow"`
   - Record new fast test duration (target: <30s, down from 52.39s baseline)
   - Update `docs/performance/baselines/sprint9_day2.json`:
     ```json
     {
       "date": "2025-XX-XX",
       "sprint": "9",
       "day": "2",
       "fast_test_duration_seconds": XX.XX,
       "fast_test_count": XXX,
       "slow_test_count": XXX,
       "total_test_count": XXX,
       "improvement_from_day0_percent": XX.X,
       "budget_seconds": 30,
       "within_budget": true/false,
       "git_commit": "XXXXXXX"
     }
     ```

4. **Validate <30s fast test budget achieved** (15 minutes)
   - Compare day2 timing vs day0 baseline (52.39s)
   - Expected improvement: ~45-55% reduction (52.39s → ~24-29s)
   - If <30s achieved: **Checkpoint 1 PASS** ✅
   - If ≥30s: Debug which tests still slow
     - Run `pytest -m "not slow" --durations=10`
     - Identify remaining slow tests >1s
     - Apply additional slow markers
     - Re-run fast tests
     - If still ≥30s after additional markers: Document for Day 3 follow-up

**Deliverables:**
- `scripts/validate_fixtures.py` - Fixture validation script (catches 5 error types)
- Updated test files with `@pytest.mark.slow` decorators (≥10 tests marked)
- `docs/performance/baselines/sprint9_day2.json` - Performance baseline after optimization
- Updated `pyproject.toml` with slow test marker configuration (if needed)

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass (fast tests should now be <30s)

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .json files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] Fixture validation script catches all 5 fixture error types
  - [ ] Fast test suite <30s (within budget) after slow markers applied
  - [ ] All quality checks pass: `make typecheck && make lint && make format && make test`
  - [ ] **CHECKPOINT 1 PASSED** (see below)
- [ ] Mark Day 2 as complete in `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (line 340)
- [ ] Check off Day 2 in README.md
- [ ] Log Day 2 completion to CHANGELOG.md
- [ ] **Check off all Checkpoint 1 criteria in PLAN.md** (lines 474-513)

**Checkpoint 1 Criteria:**
- [ ] mhw4dx secondary blockers documented (decision: defer to Sprint 10)
- [ ] Automated fixture generator working (creates valid IR)
- [ ] Fixture validation script working (catches 5 error types)
- [ ] Fast test suite <30s (performance budget achieved)
- [ ] Slow test markers applied to ≥10 tests

**Checkpoint 1 Decision:**
- **GO:** All 5 criteria met → Proceed to Day 3 (i++1 indexing)
- **NO-GO:** Performance budget not achieved → See PLAN.md lines 489-513 for recovery scenarios

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 9 Day 2: Test Infrastructure - Part 2 → CHECKPOINT 1" \
                --body "Completes Day 2 tasks and achieves Checkpoint 1 from Sprint 9 PLAN.md

   ## Test Infrastructure Complete ✅
   - Implemented fixture validation script (catches 5 error types)
   - Applied @pytest.mark.slow to XX tests
   - Fast test suite now XX.XXs (down from 52.39s, XX% improvement)
   - Within 30s budget: [YES/NO]
   
   ## Checkpoint 1 Status: [PASS/NO-GO]
   - [x] mhw4dx blockers documented
   - [x] Fixture generator working
   - [x] Fixture validation working
   - [x] Fast tests <30s
   - [x] Slow markers applied
   
   Ready to proceed with Day 3 (i++1 indexing implementation)." \
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
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 287-338) - Day 2 detailed plan
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 474-513) - Checkpoint 1 definitions and recovery scenarios
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 7) - Fixture validation design
- `docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md` (lines 362-412) - Sprint 8 fixture issues

**Notes:**
- Total effort: 1-2h (tight schedule, focus on essentials)
- Checkpoint 1 is GO/NO-GO decision point for sprint
- If performance budget not achieved, may need to use Day 3 for additional optimization
- Day 10 buffer available if needed
- Fixture validation prevents Sprint 8-style manual fixture bugs
