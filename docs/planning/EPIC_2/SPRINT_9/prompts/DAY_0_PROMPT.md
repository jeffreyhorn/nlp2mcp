# Day 0 Prompt: Sprint Planning & Setup

**Branch:** Create a new branch named `sprint9-day0-setup` from `main`

**Objective:** Review all prep tasks and validate readiness for Sprint 9 execution. Create sprint branch, baseline all metrics (parse rate, test performance), establish performance budgets, and verify all unknowns resolved.

**Prerequisites:**
- Read `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` - Complete preparation plan with all 10 tasks
- Read `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` - All 27 unknowns with verification status
- Read `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 1-100) - Sprint overview and goals
- Review Task 9 completion for performance framework design
- Review Task 10 completion for detailed schedule

**Tasks to Complete (2-3 hours):**

1. **Review prep tasks 1-10** (1 hour)
   - Open `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md`
   - Verify all 10 tasks marked as ✅ COMPLETE
   - Verify Task 1: 27 unknowns documented in KNOWN_UNKNOWNS.md
   - Verify Task 2: mhw4dx secondary blocker analysis complete
   - Verify Task 3: i++1 indexing research complete (8-10h effort validated)
   - Verify Task 4: Model sections research complete (4-5h effort validated)
   - Verify Task 5: Conversion pipeline architecture designed
   - Verify Task 6: Automated fixture generation framework designed
   - Verify Task 7: Fixture validation script designed
   - Verify Task 8: Equation attributes research complete
   - Verify Task 9: Performance baseline & budget framework designed
   - Verify Task 10: Sprint 9 detailed schedule created (PLAN.md)
   - Document any incomplete tasks or concerns

2. **Create branch `sprint9-advanced-features`** (15 minutes)
   - Create feature branch from main: `git checkout -b sprint9-advanced-features`
   - Verify clean working directory: `git status`
   - Verify CI passes on main before branching
   - Push branch to remote: `git push -u origin sprint9-advanced-features`

3. **Baseline metrics (parse rate, test performance)** (30 minutes)
   - Run GAMSLib ingest: `make ingest-gamslib`
   - Record current parse rate (expected: 40%, 4/10 models)
   - List passing models: mhw4d, rbrock, mathopt1, trig
   - Run fast test suite: `make test`
   - Record fast test duration (expected: ~52.39s from Sprint 8)
   - Run full test suite: `pytest` (no markers)
   - Record full test duration
   - Save baseline to `docs/performance/baselines/sprint9_day0.json`:
     ```json
     {
       "date": "2025-XX-XX",
       "sprint": "9",
       "day": "0",
       "parse_rate": 0.40,
       "models_passing": 4,
       "models_total": 10,
       "models_list": ["mhw4d", "rbrock", "mathopt1", "trig"],
       "fast_test_duration_seconds": 52.39,
       "full_test_duration_seconds": XXX,
       "test_count": XXX,
       "git_commit": "XXXXXXX"
     }
     ```

4. **Establish performance budgets** (30 minutes)
   - Review Task 9 design: `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` (Task 9 section)
   - Create `docs/performance/baselines/budgets.json`:
     ```json
     {
       "fast_tests": {
         "budget_seconds": 30,
         "current_seconds": 52.39,
         "status": "over_budget",
         "over_by_percent": 74.6,
         "action": "Apply slow test markers on Day 2"
       },
       "full_tests": {
         "budget_seconds": 300,
         "current_seconds": XXX,
         "status": "within_budget or over_budget"
       },
       "per_model_parse": {
         "budget_seconds": 5,
         "action": "Monitor on Day 4 (i++1) and Day 6 (model sections)"
       }
     }
     ```
   - Document budget enforcement strategy in budgets.json
   - Note: Day 2 will apply @pytest.mark.slow to achieve <30s fast tests

5. **Verify KNOWN_UNKNOWNS.md (27 unknowns verified)** (15 minutes)
   - Open `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`
   - Verify all 27 unknowns have status: ✅ VERIFIED
   - Count unknowns by category:
     - Category 1 (Parser Enhancements): 10 unknowns
     - Category 2 (Conversion Pipeline): 9 unknowns
     - Category 3 (Test Infrastructure): 4 unknowns
     - Category 4 (Performance & Metrics): 2 unknowns
     - Category 5 (Sprint Planning): 2 unknowns
   - Verify no unknowns marked 🔍 INCOMPLETE or ❌ WRONG
   - If any incomplete: Escalate before proceeding with sprint

6. **Day 0 standup & planning** (30 minutes)
   - Review Sprint 9 goals from PLAN.md (lines 43-106):
     - Goal 1: Parse rate ≥30% baseline (maintain with complexity)
     - Goal 2: i++1/i--1 indexing working (himmel16.gms unlocked)
     - Goal 3: Model sections working (hs62.gms unlocked)
     - Goal 4: Equation attributes working
     - Goal 5: Conversion pipeline (≥1 model converts)
     - Goal 6: Performance baseline (<30s fast tests)
   - Review effort estimates: Conservative 30h, Realistic 35.5h, Upper 41h
   - Review 4 checkpoints:
     - Checkpoint 1 (Day 2): Test infrastructure complete
     - Checkpoint 2 (Day 4): i++1 working, himmel16 parses
     - Checkpoint 3 (Day 6): All parser features complete
     - Checkpoint 4 (Day 8): 1 model converts
   - Review Day 10 as BUFFER day (absorbs overruns)
   - Discuss any concerns or risks
   - Confirm team capacity for Days 1-10

**Deliverables:**
- Sprint 9 branch `sprint9-advanced-features` created
- `docs/performance/baselines/sprint9_day0.json` (baseline measurements)
- `docs/performance/baselines/budgets.json` (performance budget definitions)
- All prep tasks verified as complete
- All 27 unknowns verified
- Team alignment on Sprint 9 goals and schedule

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .json files).

**Completion Criteria:**
- [ ] All success criteria met:
  - [ ] All prep tasks 1-10 marked complete in PREP_PLAN.md
  - [ ] All 27 unknowns verified in KNOWN_UNKNOWNS.md
  - [ ] Branch created and CI passing
  - [ ] Baseline measurements recorded (parse rate: 40%, fast tests: ~52.39s)
  - [ ] Performance budgets documented in budgets.json
  - [ ] Team aligned on Sprint 9 goals and checkpoints
- [ ] Mark Day 0 as complete in `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (line 108)
- [ ] Check off Day 0 in project README.md
- [ ] Log Day 0 completion to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request using GitHub CLI:
   ```bash
   gh pr create --title "Sprint 9 Day 0: Sprint Planning & Setup" \
                --body "Completes Day 0 tasks from Sprint 9 PLAN.md

   - Reviewed all 10 prep tasks (all complete)
   - Created sprint branch sprint9-advanced-features
   - Baselined metrics: Parse rate 40%, fast tests 52.39s
   - Established performance budgets (fast: 30s, full: 300s)
   - Verified all 27 unknowns resolved
   - Team aligned on goals and schedule
   
   Ready to proceed with Day 1 (Test Infrastructure)." \
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
- `docs/planning/EPIC_2/SPRINT_9/PLAN.md` (lines 108-167) - Day 0 detailed plan
- `docs/planning/EPIC_2/SPRINT_9/PREP_PLAN.md` - All 10 prep tasks
- `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` - All 27 unknowns
- `docs/planning/EPIC_2/SPRINT_8/RETROSPECTIVE.md` (lines 362-412) - Sprint 8 lessons

**Notes:**
- Day 0 is setup only - no code changes expected beyond baseline files
- If baseline parse rate ≠ 40%, investigate before proceeding
- If any prep task incomplete, must resolve before Day 1
- Budget enforcement begins Day 2 (not Day 0)
- Total effort: 2.5-3h
