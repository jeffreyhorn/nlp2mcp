# Sprint 24 Prep Task Prompts

Step-by-step execution prompts for Sprint 24 preparation tasks 2-9.

**Usage:** Copy the relevant task prompt into the conversation to execute that prep task.

---

## Task 2 Prompt: Analyze Alias Differentiation Root Causes (#1111 Family)

on a new branch `planning/sprint24-task2`,

**Objective:** Classify all 12 alias-differentiation issues (#1137-#1147, #1150) by root cause pattern. Determine whether a single architectural fix addresses most/all, or if multiple distinct fixes are needed. This analysis directly informs the architecture design in Task 3.

**Unknowns to Verify:** KU-01, KU-02, KU-03, KU-04, KU-07, KU-08

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 2 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-01 through KU-08
- Read `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` — prior design
- Key source files: `src/ad/derivative_rules.py`, `src/kkt/stationarity.py`

**What to Do:**

1. For each of the 12 issues, reproduce the gradient mismatch:
   - Translate the model: `python -m src.cli data/gamslib/raw/{model}.gms -o /tmp/{model}_mcp.gms --skip-convexity-check`
   - Compare generated stationarity equations against expected KKT conditions
   - Classify the root cause pattern (summation-context, alias-mapping, offset-alias, condition-scope, etc.)

2. Identify common root cause patterns:
   - Pattern A: Summation index not tracked through derivative chain
   - Pattern B: Alias-to-root-set mapping fails in Jacobian construction
   - Pattern C: Offset + alias interaction
   - Pattern D: Condition-scope shadowing in dollar conditionals
   - Other patterns as discovered

3. Create classification table mapping each issue to its pattern(s)
4. Estimate fix effort per pattern
5. Assess regression risk — which of the 49 matching models use aliases?
6. Create `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md`

**After completing the analysis:**

7. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For each of KU-01, KU-02, KU-03, KU-04, KU-07, KU-08:
     - Change status from `:mag: Status: INCOMPLETE` to `:white_check_mark: Status: VERIFIED` or `:x: Status: WRONG`
     - Add findings, evidence, and decisions under each unknown

8. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 2 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections with summary of findings
   - Check off all acceptance criteria

9. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 2: Analyze alias differentiation root causes — N patterns identified across 12 issues"

**Quality Gate:** Run `make typecheck && make lint && make format && make test` if any Python code was modified.

**Commit:** `Complete Sprint 24 Prep Task 2: Analyze alias differentiation root causes`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task2
gh pr create --title "Sprint 24 Prep Task 2: Analyze alias differentiation root causes" \
  --body "Classifies 12 alias-differentiation issues by root cause pattern. Verifies KU-01, KU-02, KU-03, KU-04, KU-07, KU-08."
```

Then wait for reviewer comments.

---

## Task 3 Prompt: Design Alias Differentiation Architecture

on a new branch `planning/sprint24-task3`,

**Objective:** Design the architectural changes to `_diff_varref`, `_partial_collapse_sum`, and related AD functions needed to fix alias-aware differentiation. Produce a design document with file-level change specifications, regression test plan, and rollout strategy.

**Unknowns to Verify:** KU-03, KU-05, KU-06, KU-26

**Prerequisites:**
- Task 2 must be merged (root cause analysis informs architecture)
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 3 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-03, KU-05, KU-06, KU-26
- Read `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md` — Task 2 output
- Read `docs/planning/EPIC_4/SPRINT_23/DESIGN_ALIAS_DIFFERENTIATION.md` — Sprint 23 design
- Key source files: `src/ad/derivative_rules.py`, `src/kkt/stationarity.py`

**What to Do:**

1. Review Sprint 23 design document — what was implemented, what was deferred
2. For each root cause pattern from Task 2:
   - Design the minimal code change needed
   - Identify which functions are affected
   - Design regression guards
3. Design summation-context threading:
   - How `_diff_varref` receives and uses summation context
   - How `_partial_collapse_sum` preserves or transforms context
   - How the context flows through the full derivative chain
4. Design regression test strategy:
   - Golden-file comparison for all 49 matching models
   - Per-issue regression tests for each of the 12 fixes
   - Canary models that exercise alias paths
5. Document rollout strategy: incremental vs. big-bang
6. Create `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md`

**After completing the design:**

7. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For each of KU-03, KU-05, KU-06, KU-26:
     - Change status to VERIFIED or WRONG
     - Add findings, evidence, and decisions

8. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 3 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

9. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 3: Design alias differentiation architecture v2"

**Quality Gate:** Run `make typecheck && make lint && make format && make test` if any Python code was modified.

**Commit:** `Complete Sprint 24 Prep Task 3: Design alias differentiation architecture`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task3
gh pr create --title "Sprint 24 Prep Task 3: Design alias differentiation architecture" \
  --body "Alias differentiation v2 design with summation-context threading. Verifies KU-03, KU-05, KU-06, KU-26."
```

Then wait for reviewer comments.

---

## Task 4 Prompt: Triage path_syntax_error Models (23)

on a new branch `planning/sprint24-task4`,

**Objective:** Classify all 23 path_syntax_error models by error subcategory and estimate fix effort. Identify which models are highest-leverage and which overlap with alias differentiation.

**Unknowns to Verify:** KU-09, KU-10, KU-11, KU-12, KU-13, KU-22, KU-23

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 4 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-09 through KU-13, KU-22, KU-23
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_PATH_SYNTAX_ERROR_GB.md` — prior triage
- Models available in `data/gamslib/raw/`

**What to Do:**

1. Get the current list of path_syntax_error models from `gamslib_status.json`
2. Run pipeline on each model to capture current error messages:
   ```bash
   for model in <list>; do
     python -m src.cli data/gamslib/raw/${model}.gms -o /tmp/${model}_mcp.gms --skip-convexity-check
     (cd /tmp && gams ${model}_mcp.gms lo=2 2>&1) | grep -F '$' | head -5
   done
   ```
3. Classify each model by error subcategory (A/B/C/G/new)
4. Identify influx models from Sprint 23 translate recovery
5. Estimate fix effort per subcategory and per model
6. Identify models that alias differentiation may fix automatically
7. Prioritize: which 8+ models to fix for the ≤ 15 target
8. Create `docs/planning/EPIC_4/SPRINT_24/TRIAGE_PATH_SYNTAX_ERROR.md`

**After completing the triage:**

9. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For each of KU-09, KU-10, KU-11, KU-12, KU-13, KU-22, KU-23:
     - Change status to VERIFIED or WRONG
     - Add findings, evidence, and decisions

10. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
    - Change Task 4 status to `:white_check_mark: COMPLETE`
    - Fill in Changes and Result sections
    - Check off all acceptance criteria

11. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 4: Triage path_syntax_error models — N models classified across M subcategories"

**Quality Gate:** Run `make typecheck && make lint && make format && make test` if any Python code was modified.

**Commit:** `Complete Sprint 24 Prep Task 4: Triage path_syntax_error models`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task4
gh pr create --title "Sprint 24 Prep Task 4: Triage path_syntax_error models" \
  --body "Classifies 23 path_syntax_error models by subcategory. Verifies KU-09–KU-13, KU-22, KU-23."
```

Then wait for reviewer comments.

---

## Task 5 Prompt: Triage model_infeasible Models (11)

on a new branch `planning/sprint24-task5`,

**Objective:** Update the model_infeasible classification, incorporating Sprint 23 discoveries. Identify fixable models and overlap with alias differentiation.

**Unknowns to Verify:** KU-14, KU-15, KU-16, KU-17, KU-18

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 5 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-14 through KU-18
- Read `docs/planning/EPIC_4/SPRINT_23/TRIAGE_MODEL_INFEASIBLE.md` — prior triage
- New issues: #1199 (bearing), #1177 (chenery), #1195 (sambal), #1192 (gtm)

**What to Do:**

1. Confirm current model_infeasible model list from `gamslib_status.json`
2. For each model, classify root cause:
   - KKT formulation bug (fixable)
   - Jacobian accuracy (may overlap with alias differentiation)
   - Inherent MCP incompatibility (not fixable)
   - Missing feature (deferred)
3. For new issues (#1177, #1192, #1195, #1199), perform root cause analysis
4. Identify overlap with alias differentiation
5. Prioritize: which 3+ models to target for ≤ 8 goal
6. Track gross fixes/influx budget per PR7
7. Create `docs/planning/EPIC_4/SPRINT_24/TRIAGE_MODEL_INFEASIBLE.md`

**After completing the triage:**

8. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For each of KU-14, KU-15, KU-16, KU-17, KU-18:
     - Change status to VERIFIED or WRONG
     - Add findings, evidence, and decisions

9. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 5 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

10. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 5: Triage model_infeasible models — N models classified, M fixable targets identified"

**Quality Gate:** Run `make typecheck && make lint && make format && make test` if any Python code was modified.

**Commit:** `Complete Sprint 24 Prep Task 5: Triage model_infeasible models`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task5
gh pr create --title "Sprint 24 Prep Task 5: Triage model_infeasible models" \
  --body "Updates model_infeasible classification with Sprint 23 discoveries. Verifies KU-14–KU-18."
```

Then wait for reviewer comments.

---

## Task 6 Prompt: Investigate Translation Timeouts (6 models)

on a new branch `planning/sprint24-task6`,

**Objective:** Analyze the 6 remaining translation timeout models to determine fixability within Sprint 24. Also triage the 1 internal_error model.

**Unknowns to Verify:** KU-19, KU-20, KU-21

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 6 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-19, KU-20, KU-21
- Sprint 23 LP fast path: PR #1172
- Known timeout models: lop (#1169), mexls (#1185)

**What to Do:**

1. List all timeout and internal_error models from `gamslib_status.json`
2. For each timeout model, profile the translation:
   - Model size (equations, variables, constraints)
   - Time to parse vs. time to translate
   - Where the bottleneck is (stationarity builder, emitter, AD)
3. Classify by bottleneck pattern:
   - Large model (too many Jacobian entries)
   - Deep recursion (nested expressions)
   - Specific grammar pattern (multi-solve, large tables)
4. Estimate feasibility of optimization per model
5. Investigate the internal_error model — root cause and potential fix
6. Create `docs/planning/EPIC_4/SPRINT_24/INVESTIGATION_TRANSLATE_TIMEOUTS.md`

**After completing the investigation:**

7. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For each of KU-19, KU-20, KU-21:
     - Change status to VERIFIED or WRONG
     - Add findings, evidence, and decisions

8. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 6 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

9. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 6: Investigate translation timeouts — N models profiled, M potentially fixable"

**Quality Gate:** Run `make typecheck && make lint && make format && make test` if any Python code was modified.

**Commit:** `Complete Sprint 24 Prep Task 6: Investigate translation timeouts`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task6
gh pr create --title "Sprint 24 Prep Task 6: Investigate translation timeouts" \
  --body "Profiles 6 timeout models and 1 internal_error. Verifies KU-19, KU-20, KU-21."
```

Then wait for reviewer comments.

---

## Task 7 Prompt: Run Full Pipeline Baseline (per PR6)

on a new branch `planning/sprint24-task7`,

**Objective:** Run the full pipeline to establish definitive Sprint 24 baseline metrics, following Sprint 23 process recommendation PR6.

**Unknowns to Verify:** KU-25

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 7 section
- Read `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md` — KU-25
- Sprint 23 final: parse 147/147, translate 140/147, solve 86/140, match 49/147

**What to Do:**

1. Run full pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
2. Record ALL metrics with absolute counts AND percentages (per PR8):
   - Parse, Translate, Solve, Match
   - Error categories: path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license
   - Translate errors: timeout, internal_error
3. Compare to Sprint 23 final — identify any changes
4. Calculate Sprint 23 actual error influx rate (for KU-25 verification)
5. Create `docs/planning/EPIC_4/SPRINT_24/BASELINE_METRICS.md` with metrics table
6. Commit updated `data/gamslib/gamslib_status.json`

**After completing the baseline:**

7. Update `docs/planning/EPIC_4/SPRINT_24/KNOWN_UNKNOWNS.md`:
   - For KU-25: Change status to VERIFIED or WRONG; add actual influx rate finding

8. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 7 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

9. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 7: Full pipeline baseline — parse N/N, translate N/N, solve N/N, match N/N"

**Quality Gate:** No Python code changes expected; skip quality gate unless code was modified.

**Commit:** `Complete Sprint 24 Prep Task 7: Full pipeline baseline`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task7
gh pr create --title "Sprint 24 Prep Task 7: Full pipeline baseline" \
  --body "Establishes Sprint 24 baseline metrics. Verifies KU-25 (error influx budget)."
```

Then wait for reviewer comments.

---

## Task 8 Prompt: Review Sprint 23 Retrospective Action Items

on a new branch `planning/sprint24-task8`,

**Objective:** Verify that all Sprint 23 retrospective action items, process recommendations (PR9-PR11), and deferred items are addressed in the Sprint 24 prep plan.

**Unknowns to Verify:** (cross-cutting PR9/PR10/PR11 compliance)

**Prerequisites:**
- Tasks 1-7 should be merged (review after all research is complete)
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 8 section
- Read `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` — action items
- Read `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md` — deferred KUs (KU-28, KU-29, KU-32)

**What to Do:**

1. Review each "What Could Be Improved" item (5 items) — verify addressed in Sprint 24
2. Review each "What We'd Do Differently" item (4 items) — verify changes incorporated
3. Verify PR9 compliance — targets set against 147-model pipeline scope
4. Verify PR10 compliance — error influx budget calculated (use Task 7 findings)
5. Verify PR11 compliance — alias differentiation is Days 1-5 priority in schedule
6. Check all deferred items from Sprint 23 KNOWN_UNKNOWNS (KU-28→KU-22, KU-29→KU-23, KU-32→KU-24)
7. Document any gaps and propose adjustments
8. Create `docs/planning/EPIC_4/SPRINT_24/RETROSPECTIVE_ALIGNMENT.md`

**After completing the review:**

9. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 8 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

10. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 8: Review Sprint 23 retrospective — N/N items addressed, PR9/PR10/PR11 compliance verified"

**Quality Gate:** No Python code changes expected; skip quality gate unless code was modified.

**Commit:** `Complete Sprint 24 Prep Task 8: Review Sprint 23 retrospective action items`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task8
gh pr create --title "Sprint 24 Prep Task 8: Review Sprint 23 retrospective" \
  --body "Verifies all retrospective action items and PR9/PR10/PR11 compliance."
```

Then wait for reviewer comments.

---

## Task 9 Prompt: Plan Sprint 24 Detailed Schedule

on a new branch `planning/sprint24-task9`,

**Objective:** Create the Sprint 24 detailed schedule (Day 0-14) with daily task assignments, checkpoints, contingency plans, and day-by-day execution prompts. Integrate all prep task findings.

**Unknowns to Verify:** (integrates all verified unknowns into schedule)

**Prerequisites:**
- ALL Tasks 1-8 must be merged
- Read `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md` — Task 9 section
- Read all Task 2-8 deliverables:
  - `ANALYSIS_ALIAS_DIFFERENTIATION.md` (Task 2)
  - `DESIGN_ALIAS_DIFFERENTIATION_V2.md` (Task 3)
  - `TRIAGE_PATH_SYNTAX_ERROR.md` (Task 4)
  - `TRIAGE_MODEL_INFEASIBLE.md` (Task 5)
  - `INVESTIGATION_TRANSLATE_TIMEOUTS.md` (Task 6)
  - `BASELINE_METRICS.md` (Task 7)
  - `RETROSPECTIVE_ALIGNMENT.md` (Task 8)
- Read `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 24 section (lines 744-829)
- Read `docs/planning/EPIC_4/SPRINT_23/PLAN.md` — template for schedule format
- Read `docs/planning/EPIC_4/SPRINT_23/prompts/PLAN_PROMPTS.md` — template for prompts

**What to Do:**

1. Define workstreams based on prep task findings:
   - WS1: Alias differentiation (Priority 1, Days 1-7)
   - WS2: path_syntax_error fixes (Priority 2, Days 5-9)
   - WS3: model_infeasible fixes (Priority 3, Days 7-10)
   - WS4: Translation timeout (Priority 4, Days 8-10)
   - WS5: Pipeline retest and sprint close (Days 11-14)
2. Assign daily tasks for all 15 days (Day 0-14)
3. Define 2 checkpoints with GO/NO-GO criteria:
   - Checkpoint 1 (Day 5): Alias differentiation progress + regression check
   - Checkpoint 2 (Day 10): Error category progress + GO/NO-GO for close
4. Create contingency plans for top 3 risks
5. Budget error influx per PR10 (~40% of newly-translating models → solve errors)
6. Create day-by-day execution prompts
7. Initialize SPRINT_LOG.md with targets and baseline

Create these files:
- `docs/planning/EPIC_4/SPRINT_24/PLAN.md` — 15-day detailed schedule
- `docs/planning/EPIC_4/SPRINT_24/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` — initialized sprint log

**After completing the schedule:**

8. Update `docs/planning/EPIC_4/SPRINT_24/PREP_PLAN.md`:
   - Change Task 9 status to `:white_check_mark: COMPLETE`
   - Fill in Changes and Result sections
   - Check off all acceptance criteria

9. Update `CHANGELOG.md` with entry: "Complete Sprint 24 Prep Task 9: Plan Sprint 24 detailed schedule — 15-day plan with 5 workstreams, 2 checkpoints, day-by-day prompts"

**Quality Gate:** No Python code changes expected; skip quality gate unless code was modified.

**Commit:** `Complete Sprint 24 Prep Task 9: Plan Sprint 24 detailed schedule`

**Push and create PR:**
```bash
git push -u origin planning/sprint24-task9
gh pr create --title "Sprint 24 Prep Task 9: Plan Sprint 24 detailed schedule" \
  --body "15-day Sprint 24 schedule with 5 workstreams, 2 checkpoints, day-by-day prompts, and initialized sprint log."
```

Then wait for reviewer comments.
