# Day 4 Prompt: Advanced Indexing - Part 2 → CHECKPOINT 2

**Branch:** Create a new branch named `sprint9-day4-i-plusplus-1-part2-checkpoint2` from `sprint9-advanced-features`

**Objective:** Validate i++1 indexing with himmel16.gms, test advanced indexing edge cases, update dashboard with indexing statistics, and achieve Checkpoint 2 (i++1 working, himmel16 parses).

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 465-472) - Day 4 brief summary
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 515-595) - Checkpoint 2 detailed decision tree
- Verify Day 3 complete: Grammar, semantic handler, IR nodes all implemented
- Verify Day 3 tests pass with ≥80% coverage
- Review himmel16.gms location: `data/gamslib/himmel16.gms`

**Tasks to Complete (4-5 hours):**

1. **Parse himmel16.gms (validate i++1 indexing)** (1 hour)
   - Run parser on himmel16.gms: `python -m src.parser data/gamslib/himmel16.gms`
   - Expected: Parse succeeds with i++1 indexing support
   - If parse fails:
     - Capture error message and location
     - Check if error is i++1-related or different blocker
     - If i++1 issue: Debug semantic handler or IR construction
     - If different blocker: Document as secondary blocker
   - Verify IR structure is correct:
     - Check IndexOffset nodes created for i++1 references
     - Spot-check key equations have proper indexing
   - Save parse output for analysis

2. **Debug himmel16.gms parse failures (if any)** (1-2 hours)
   - If himmel16 fails to parse, follow decision tree from PLAN.md (lines 527-577):
     - **Grammar issue:** Test minimal "x(i++1)" case, fix precedence/ambiguity
     - **Semantic/IR issue:** Check if IndexOffset nodes created, validate structure
     - **Secondary blocker:** Document in blockers/ directory
   - Common failure modes from PLAN.md (lines 536-552):
     1. Semantic handler not called (fix: add handler hook)
     2. IR validation error (fix: update node definition)
     3. Expression type mismatch (fix: type conversion)
     4. Indexing in unexpected context (fix: extend grammar)
   - Recovery plan (PLAN.md lines 554-566):
     - If fixed by Day 5 noon: Proceed with model sections Day 5 afternoon
     - If not fixed: Use full Day 5 for debugging, defer model sections to Day 6
   - Test regression: Re-run existing 4 models (mhw4d, rbrock, mathopt1, trig)
   - All 4 must still parse (no regressions allowed)

3. **Write comprehensive indexing tests** (1-1.5 hours)
   - Extend `tests/test_indexing.py` with real-world test cases
   - Test himmel16-specific patterns (extract from actual file)
   - Additional edge case tests:
     - `test_boundary_behavior()` - What happens at set edges?
     - `test_circular_wrap()` - For circular sets, verify wrap-around
     - `test_linear_suppression()` - For linear indexing, verify out-of-bounds = 0
     - `test_nested_indexing()` - Multiple lead/lag in same expression
     - `test_mixed_indexing()` - Circular and linear in same model
   - Integration test:
     ```python
     def test_himmel16_parses():
         """Verify himmel16.gms parses successfully."""
         result = parse_file("data/gamslib/himmel16.gms")
         assert result.success
         assert result.parse_rate == 1.0
     ```
   - Target coverage: ≥80% maintained or improved

4. **Update dashboard with indexing statistics** (1 hour)
   - Open `scripts/dashboard.py`
   - Add indexing metrics:
     ```python
     def count_indexing_features(ir: ModelIR) -> dict:
         """Count indexing feature usage."""
         return {
             "total_index_expressions": count_nodes(ir, IndexOffset),
             "circular_lead_count": count_circular_lead(ir),
             "circular_lag_count": count_circular_lag(ir),
             "linear_lead_count": count_linear_lead(ir),
             "linear_lag_count": count_linear_lag(ir),
             "max_offset_value": find_max_offset(ir)
         }
     ```
   - Add column to dashboard table for indexing features
   - Regenerate dashboard: `python scripts/dashboard.py`
   - Verify himmel16 now shows as "PASS" in dashboard

**Deliverables:**
- himmel16.gms parsing successfully (or detailed blocker analysis if not)
- Comprehensive indexing test suite with ≥80% coverage
- Updated `scripts/dashboard.py` with indexing metrics
- Regenerated dashboard showing updated parse rate

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] himmel16.gms parses successfully (unlocked by i++1)
  - [ ] Parse rate ≥50% (4/10 → 5/10 with himmel16)
  - [ ] Indexing test coverage ≥80%
  - [ ] All quality checks pass
  - [ ] **CHECKPOINT 2 PASSED** (see below)
- [ ] Mark Day 4 as complete in `docs/planning/EPIC_2/SPRINT_9/PLAN.md`
- [ ] Check off Day 4 in README.md
- [ ] Log Day 4 completion to CHANGELOG.md
- [ ] **Check off all Checkpoint 2 criteria in PLAN.md**

**Checkpoint 2 Criteria (PLAN.md lines 597-650):**
- [ ] Grammar supports i++1, i--1 patterns
- [ ] Semantic handler creates IndexOffset nodes correctly
- [ ] IR representation complete and tested
- [ ] himmel16.gms parses successfully (validates i++1)
- [ ] Parse rate ≥50% (5/10 models)
- [ ] Indexing test coverage ≥80%

**Checkpoint 2 Decision:**
- **GO:** All 6 criteria met → Proceed to Day 5 (model sections)
- **NO-GO:** himmel16 fails to parse → See recovery plan in PLAN.md lines 554-566

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 9 Day 4: Advanced Indexing - Part 2 → CHECKPOINT 2" \
                --body "Completes Day 4 tasks and achieves Checkpoint 2 from Sprint 9 PLAN.md

   ## himmel16.gms Status: [PASS/FAIL]
   - Parse result: [SUCCESS/ERROR]
   - Parse rate: XX% (X/10 models)
   
   ## Checkpoint 2 Status: [PASS/NO-GO]
   - [x] Grammar supports i++1, i--1
   - [x] Semantic handler creates IndexOffset
   - [x] IR complete and tested
   - [x] himmel16 parses
   - [x] Parse rate ≥50%
   - [x] Test coverage ≥80%
   
   ## Regression Check
   - Existing 4 models still parse: [YES/NO]
   
   Ready for Day 5 (model sections implementation)." \
                --base sprint9-advanced-features
   ```
2. Request review, address comments, merge when approved

**Reference Documents:**
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 515-650) - Checkpoint 2 decision tree
- `data/gamslib/himmel16.gms` - Target model to unlock
- Task 3 research: i++1 validation findings

**Notes:**
- Effort: 4-5h (1h parse + 1-2h debugging + 1-1.5h tests + 1h dashboard)
- Checkpoint 2 is critical GO/NO-GO decision
- If himmel16 fails: May need Day 5 for debugging (use Day 10 buffer)
- Parse rate should increase from 40% to 50% (4/10 → 5/10)
