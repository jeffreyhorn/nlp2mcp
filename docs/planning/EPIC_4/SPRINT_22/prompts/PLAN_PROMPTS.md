# Sprint 22 Day-by-Day Prompts

This file contains comprehensive prompts for each day of Sprint 22 (Days 0–14). Each prompt is designed to be used when starting work on that specific day.

**Sprint Duration:** 15 days (Day 0 – Day 14)
**Estimated Effort:** ~24–30 hours (~1.6–2.0h/day effective capacity)
**Baseline:** parse 154/157 (98.1%), translate 136/154 (88.3%), solve 65/136 (47.8%), match 30/65 (46.2%), tests 3,957

---

## Day 0 Prompt: Baseline Confirm + Sprint Kickoff

**Branch:** Create a new branch named `sprint22-day0-kickoff` from `main`

**Objective:** Verify clean baseline, internalize the plan, confirm all tests pass, initialize sprint log.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (lines 1–50) — sprint overview, targets, and workstream summaries
- Read `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md` — exact baseline numbers at commit `53ac5979`
- Read `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — note KU-24 (model_infeasible influx risk) and any items flagged as open risks

**Tasks to Complete (~1 hour):**

1. **Verify baseline** (0.25h)
   - Run `make test` — must show 3,957 passed
   - Run `git log --oneline -5` — confirm you are on a clean commit from `main`

2. **Initialize SPRINT_LOG.md** (0.25h)
   - Open `docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md` (template already created)
   - Fill in baseline metrics from BASELINE_METRICS.md
   - Record the baseline commit: `53ac5979`

3. **Run baseline pipeline** (0.25h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --only-parse --quiet`
   - Confirm parse 154/157, translate 136/154, solve 65/136, match 30/65

4. **Map open issues to workstreams** (0.25h)
   - Review GitHub issues: `gh issue list --state open`
   - Note which issues correspond to WS1–WS6
   - Record in SPRINT_LOG.md

**Deliverables:**
- `make test` passing (3,957 tests)
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md` filled with baseline metrics
- Pipeline baseline confirmed

**Quality Checks:**
ALWAYS run these commands before any commit or push that includes changes to code files:
1. `make typecheck` - Must pass
2. `make lint` - Must pass
3. `make format` - Apply formatting
4. `make test` - All tests must pass

You do NOT need to do this if all changes you are committing or pushing are documentation files (e.g. .md, .txt files).

**Completion Criteria:**
- [ ] `make test` passes (3,957 tests)
- [ ] SPRINT_LOG.md filled with baseline metrics
- [ ] Pipeline baseline confirmed
- [ ] Mark Day 0 as complete in PLAN.md
- [ ] Log progress to CHANGELOG.md

**Pull Request & Review:**
After committing and pushing all changes:
1. Create a pull request:
   ```bash
   gh pr create --title "Sprint 22 Day 0: Baseline Confirm + Sprint Kickoff" \
                --body "Completes Day 0 tasks: baseline verified, SPRINT_LOG.md initialized."
   ```
2. Request a review from Copilot: `gh pr edit --add-reviewer copilot`
3. Address all review comments, reply directly to each, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (Day 0 section)
- `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md`
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md`

---

## Day 1 Prompt: WS5 Timeout Quick Win + WS1 Subcategory C (Part 1)

**Branch:** Create a new branch named `sprint22-day1-timeout-subcat-c` from `main`

**Objective:** Increase subprocess timeout to recover 3 translation timeouts; begin subcategory C uncontrolled set fixes in stationarity.py.

**Prerequisites:**
- Read `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md` — timeout models and root causes
- Read `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md` — subcategory C fix design (~110 LOC in stationarity.py)
- Read `src/kkt/stationarity.py` — understand `_collect_free_indices()` and domain conditioning logic
- Read `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` — list of 10 subcategory C models

**Tasks to Complete (~2–3 hours):**

1. **WS5: Increase subprocess timeout** (0.25h)
   - In `scripts/gamslib/run_full_test.py`, change subprocess timeout from 60s to 150s
   - Verify egypt, ferts, dinam now translate (may need to rerun pipeline for these 3)

2. **WS1/C: Analyze uncontrolled set root cause** (0.5h)
   - Pick the simplest subcategory C model (from PATH_SYNTAX_ERROR_STATUS.md)
   - Trace through `_collect_free_indices()` to understand why sets are uncontrolled
   - Document the pattern: which sets should be conditioned and how

3. **WS1/C: Implement domain conditioning** (1–1.5h)
   - Enhance `_collect_free_indices()` to propagate domain conditioning from equation definitions
   - Implement the fix per PATH_SYNTAX_ERROR_FIX_DESIGN.md Section C
   - Target: first 3–5 of 10 subcategory C models fixed

4. **Unit tests** (0.5h)
   - Add ≥ 3 unit tests for the domain conditioning logic
   - Cover: simple uncontrolled set, nested domain, multi-index equation

**Deliverables:**
- Timeout increased to 150s (egypt, ferts, dinam now translate)
- `src/kkt/stationarity.py` enhanced with domain conditioning
- ≥ 3 subcategory C models no longer have $149 error
- ≥ 3 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] Timeout increased; egypt/ferts/dinam translate
- [ ] ≥ 3 subcategory C models fixed
- [ ] ≥ 3 unit tests pass
- [ ] All existing tests pass
- [ ] Mark Day 1 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 1: WS5 timeout + WS1 subcategory C (Part 1)" \
             --body "Increases subprocess timeout 60s→150s. Begins subcategory C uncontrolled set fixes."
```
Request review from Copilot, address comments, merge when approved.

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (Day 1 section)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md` (Section C)
- `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`
- `src/kkt/stationarity.py`

---

## Day 2 Prompt: WS1 Subcategory C (Part 2)

**Branch:** Create a new branch named `sprint22-day2-subcat-c-complete` from `main`

**Objective:** Complete subcategory C fixes for all 10 models; regression test all solving models.

**Prerequisites:**
- Day 1 PR must be merged
- Read Day 1 results in SPRINT_LOG.md — which subcategory C models were fixed, which remain
- Read `src/kkt/stationarity.py` — understand Day 1 changes

**Tasks to Complete (~2–3 hours):**

1. **Complete remaining subcategory C models** (1–1.5h)
   - Fix any subcategory C models not addressed in Day 1
   - Handle edge cases: nested domains, multi-index conditioning

2. **Regression testing** (0.5h)
   - Run full pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Verify all 65 previously-solving models still solve
   - Document any regressions or unexpected category shifts

3. **Assess model_infeasible influx** (0.5h)
   - Check if any models shifted from path_syntax_error to model_infeasible (KU-24)
   - If influx > 5: document and adjust WS3 priorities

**Deliverables:**
- All 10 subcategory C models addressed
- Regression test: 0 regressions in 65 solving models
- model_infeasible influx assessed and documented

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] All 10 subcategory C models no longer have $149 error
- [ ] 0 regressions in solving models
- [ ] model_infeasible influx documented
- [ ] Mark Day 2 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 2: WS1 subcategory C complete" \
             --body "Completes subcategory C uncontrolled set fixes for all 10 models."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (Day 2 section)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` (KU-24)

---

## Day 3 Prompt: WS1 Subcategories G + B

**Branch:** Create a new branch named `sprint22-day3-subcat-g-b` from `main`

**Objective:** Fix subcategory G (set index reuse, 4 models) and subcategory B (domain violation, 2 models); reach path_syntax_error ≤ 30 target.

**Prerequisites:**
- Day 2 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md` — Sections G and B
- Read `src/emit/expr_to_gams.py` — understand current index renaming logic (for G)
- Read `src/emit/original_symbols.py` — understand domain filtering (for B)

**Tasks to Complete (~2–3 hours):**

1. **WS1/G: Fix set index reuse conflicts** (1–1.5h)
   - In `src/emit/expr_to_gams.py`, implement nested bound index tracking
   - Add case-insensitive collision detection (~100 LOC per design doc)
   - Target: 4 subcategory G models fixed

2. **WS1/B: Fix domain violation in emitted data** (0.5–1h)
   - In `src/emit/original_symbols.py`, add `_is_in_domain()` filter (~70 LOC per design doc)
   - Target: 2 subcategory B models fixed

3. **Unit tests** (0.5h)
   - Add ≥ 4 unit tests covering G and B fixes
   - G: test index collision detection, case-insensitive matching
   - B: test domain filtering, out-of-domain element exclusion

4. **Full pipeline retest** (0.25h)
   - Verify path_syntax_error ≤ 30
   - Check for regressions

**Deliverables:**
- 4 subcategory G models fixed
- 2 subcategory B models fixed
- path_syntax_error ≤ 30 target met
- ≥ 4 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] path_syntax_error ≤ 30
- [ ] 6 models fixed (4 G + 2 B)
- [ ] ≥ 4 unit tests pass
- [ ] 0 regressions
- [ ] Mark Day 3 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 3: WS1 subcategories G + B" \
             --body "Fixes subcategory G (index reuse, 4 models) and B (domain violation, 2 models). path_syntax_error target ≤30 met."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (Day 3 section)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md` (Sections G, B)

---

## Day 4 Prompt: WS2 path_solve_terminated — `_fx_` Suppression

**Branch:** Create a new branch named `sprint22-day4-fx-suppression` from `main`

**Objective:** Implement `_fx_` equation suppression for fixed variables, fixing 5 path_solve_terminated models.

**Prerequisites:**
- Day 3 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` — understand the 5 `_fx_` models and their error pattern
- Read `src/kkt/stationarity.py` — understand how stationarity equations are generated for fixed variables
- Read `src/emit/emit_gams.py` — understand equation emission

**Tasks to Complete (~2–3 hours):**

1. **Analyze `_fx_` equation pattern** (0.5h)
   - Pick the simplest `_fx_` model from PATH_SOLVE_TERMINATED_STATUS.md
   - Trace through the MCP output to understand why `_fx_` equations cause PATH errors
   - Document: which equations need suppression, under what conditions

2. **Implement `_fx_` equation suppression** (1–1.5h)
   - In the KKT builder or emitter, suppress stationarity equations for variables that are fully fixed (`.fx` set)
   - Ensure complementarity is still preserved for the fixed variable bound

3. **Unit tests** (0.5h)
   - Add ≥ 3 unit tests for `_fx_` suppression
   - Cover: fully fixed scalar variable, indexed variable with partial fixing, interaction with bounds

4. **Regression test** (0.25h)
   - Run pipeline on the 5 `_fx_` models — all should advance past MCP pairing error
   - Run pipeline on all 65 solving models — 0 regressions

**Deliverables:**
- `_fx_` equation suppression implemented
- 5 models no longer have MCP pairing errors
- ≥ 3 unit tests
- 0 regressions

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] 5 `_fx_` models solve or advance to next error category
- [ ] ≥ 3 unit tests pass
- [ ] 0 regressions
- [ ] Mark Day 4 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 4: WS2 _fx_ equation suppression" \
             --body "Implements _fx_ equation suppression for 5 path_solve_terminated models."
```

**Reference Documents:**
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` (Day 4 section)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md`

---

## Day 5 Prompt: Checkpoint 1 + WS2 Part 2

**Branch:** Create a new branch named `sprint22-day5-checkpoint1-ws2` from `main`

**Objective:** Evaluate Checkpoint 1 GO/NO-GO; fix remaining path_solve_terminated MCP pairing errors (unmatched free variables, `$` condition preservation).

**Prerequisites:**
- Day 4 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/PLAN.md` — Checkpoint 1 criteria
- Read `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` — remaining models after `_fx_` fix

**Tasks to Complete (~2–3 hours):**

1. **Checkpoint 1 evaluation** (0.5h)
   - Run full pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Evaluate against Checkpoint 1 criteria:
     - path_syntax_error ≤ 32? (GO threshold)
     - Solve success ≥ 70? (GO threshold)
     - All tests pass?
   - Record decision in SPRINT_LOG.md

2. **WS2: Fix unmatched free variable pairing** (1h)
   - 2 models have unmatched free variables in MCP model statement
   - Fix pairing logic in KKT builder

3. **WS2: Fix `$` condition preservation** (0.5–1h)
   - 1 model loses `$` conditions during KKT transformation
   - Preserve conditional guards in emitted equations

4. **Pipeline retest for affected models** (0.25h)

**Deliverables:**
- Checkpoint 1 GO/NO-GO decision documented
- 3 additional path_solve_terminated models fixed
- path_solve_terminated ≤ 7

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] Checkpoint 1 evaluated and documented
- [ ] path_solve_terminated ≤ 7
- [ ] All tests pass
- [ ] Mark Day 5 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 5: Checkpoint 1 + WS2 free variable pairing" \
             --body "Checkpoint 1 GO/NO-GO. Fixes unmatched free variables and condition preservation."
```

---

## Day 6 Prompt: WS2 Part 3 + Pipeline Retest

**Branch:** Create a new branch named `sprint22-day6-ws2-complete` from `main`

**Objective:** Complete path_solve_terminated fixes; full pipeline retest; assess model_infeasible influx.

**Prerequisites:**
- Day 5 PR must be merged; Checkpoint 1 must be GO
- Read SPRINT_LOG.md Day 5 results

**Tasks to Complete (~2–3 hours):**

1. **WS2: Fix stationarity domain conditioning** (1h)
   - 1 model with domain conditioning issue in stationarity equations
   - Fix domain propagation in KKT builder

2. **WS2: Address execution error models** (1h, if time)
   - 4 models have execution errors (domain guards, parameter resolution)
   - Address the simplest 1–2 as bonus

3. **Full pipeline retest** (0.5h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record updated metrics: path_syntax_error, path_solve_terminated, model_infeasible, solve, match

4. **Assess KU-24 influx** (0.25h)
   - Compare model_infeasible count before and after WS1/WS2 fixes
   - Document any models that shifted categories

**Deliverables:**
- path_solve_terminated ≤ 5
- Full pipeline metrics updated
- model_infeasible influx assessed

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] path_solve_terminated ≤ 5
- [ ] Pipeline metrics updated in SPRINT_LOG.md
- [ ] model_infeasible influx documented
- [ ] Mark Day 6 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 6: WS2 complete + pipeline retest" \
             --body "Completes path_solve_terminated fixes. Full pipeline retest with updated metrics."
```

---

## Day 7 Prompt: WS3 model_infeasible Fixes (Part 1)

**Branch:** Create a new branch named `sprint22-day7-model-infeasible` from `main`

**Objective:** Exclude 4 permanently incompatible models; fix whouse and ibm1 KKT bugs.

**Prerequisites:**
- Day 6 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` — Category A fixes and permanent exclusions
- Read `src/kkt/stationarity.py` — understand lag reference and mixed-bounds patterns
- Check SPRINT_LOG.md Day 6 for model_infeasible influx count

**Tasks to Complete (~2–3 hours):**

1. **Permanently exclude 4 models** (0.25h)
   - Add feasopt1, iobalance, meanvar, orani to pipeline exclusion list
   - Document reason for each exclusion

2. **Fix whouse lag reference conditioning** (1–1.5h)
   - In `src/kkt/stationarity.py`, fix handling of lagged variable references in stationarity
   - Add conditioning to prevent infeasible complementarity from lag terms

3. **Fix ibm1 mixed-bounds multipliers** (1–1.5h)
   - Fix multiplier generation for variables with both `.lo` and `.up` bounds
   - Ensure correct complementarity conditions

4. **Unit tests** (0.25h)
   - Add ≥ 2 unit tests for lag conditioning and mixed-bounds

**Deliverables:**
- 4 models permanently excluded with documentation
- whouse, ibm1 no longer infeasible
- ≥ 2 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] 4 models excluded; whouse and ibm1 solve
- [ ] ≥ 2 unit tests pass
- [ ] Mark Day 7 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 7: WS3 model_infeasible fixes (Part 1)" \
             --body "Excludes 4 incompatible models. Fixes whouse lag conditioning and ibm1 mixed-bounds."
```

---

## Day 8 Prompt: WS3 Part 2 + WS6 mexss

**Branch:** Create a new branch named `sprint22-day8-uimp-mexss` from `main`

**Objective:** Fix uimp multi-solve objective; fix mexss `sameas` guard (deferred issue #764).

**Prerequisites:**
- Day 7 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` — uimp fix description
- Read `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` — full issue details
- Read `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md` — #764 scope decision

**Tasks to Complete (~2–3 hours):**

1. **Fix uimp multi-solve objective** (1h)
   - uimp has multiple solve statements; MCP objective linked to wrong solve
   - Fix objective variable linkage in parser or emitter

2. **Fix mexss `sameas` guard (#764)** (1.5–2h)
   - In `src/kkt/stationarity.py`, fix `_add_indexed_jacobian_terms()` `sameas` guard
   - Guard incorrectly restricts scalar-constraint multiplier terms for accounting variables
   - Ensure fix doesn't break currently-solving models with similar patterns

3. **Unit tests** (0.5h)
   - Add ≥ 2 unit tests for uimp and mexss fixes

4. **Pipeline retest** (0.25h)
   - Verify model_infeasible ≤ 12
   - Check uimp and mexss solve status

**Deliverables:**
- uimp and mexss solve
- model_infeasible ≤ 12
- ≥ 2 unit tests

**Quality Checks:**
Run `make typecheck && make lint && make format && make test` before commit.

**Completion Criteria:**
- [ ] uimp and mexss solve (PATH status 1)
- [ ] model_infeasible ≤ 12
- [ ] ≥ 2 unit tests pass
- [ ] 0 regressions
- [ ] Mark Day 8 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 8: WS3 uimp + WS6 mexss #764" \
             --body "Fixes uimp multi-solve objective and mexss sameas guard (#764). model_infeasible target met."
```

---

## Day 9 Prompt: WS4 Solution Divergence Investigation (Part 1)

**Branch:** Create a new branch named `sprint22-day9-divergence-investigation` from `main`

**Objective:** Investigate root causes for verified_convex mismatch models (Category A from MATCH_RATE_ANALYSIS.md).

**Prerequisites:**
- Day 8 PR must be merged
- Read `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md` — Sections 2.2 (Category A) and 2.5 (Category D)
- Read `data/gamslib/raw/apl1p.gms` (if available) — understand the original NLP model
- Read `data/gamslib/mcp/apl1p_mcp.gms` — compare MCP formulation to expected KKT

**Tasks to Complete (~2–3 hours):**

1. **Analyze apl1p KKT derivation** (1h)
   - Compare MCP output equations to expected KKT conditions
   - Identify which stationarity/complementarity equation is incorrect
   - Document: what the correct equation should be, what the MCP emits instead

2. **Analyze senstran transportation model** (0.5h)
   - senstran is a transportation LP — KKT should be straightforward
   - Check if index/domain handling causes incorrect equation generation

3. **Identify pattern** (0.5h)
   - Do apl1p and senstran share a common root cause?
   - Estimate fix complexity: is it a single code change or model-specific?

4. **Document findings** (0.25h)
   - Add analysis notes to SPRINT_LOG.md
   - File GitHub issue if root cause is clear

**Deliverables:**
- Root cause analysis for apl1p and senstran
- Pattern identified (shared vs. model-specific)
- Fix complexity estimated

**Quality Checks:**
Documentation only — no code changes expected. No quality checks needed.

**Completion Criteria:**
- [ ] Root cause identified for ≥ 1 Category A model
- [ ] Fix strategy documented
- [ ] Mark Day 9 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 9: WS4 solution divergence investigation" \
             --body "Investigates root causes for verified_convex mismatch models (Category A)."
```

---

## Day 10 Prompt: Checkpoint 2 + WS4 Part 2

**Branch:** Create a new branch named `sprint22-day10-checkpoint2` from `main`

**Objective:** Evaluate Checkpoint 2 GO/NO-GO; complete divergence investigation with Category D analysis.

**Prerequisites:**
- Day 9 PR must be merged
- Read SPRINT_LOG.md for current metrics
- Read `docs/planning/EPIC_4/SPRINT_22/PLAN.md` — Checkpoint 2 criteria

**Tasks to Complete (~2–3 hours):**

1. **Checkpoint 2 evaluation** (0.5h)
   - Run full pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Evaluate against Checkpoint 2 criteria:
     - path_syntax_error ≤ 30?
     - path_solve_terminated ≤ 6?
     - model_infeasible ≤ 13?
     - Solve ≥ 73?
     - Match ≥ 33?
   - Record GO/NO-GO decision in SPRINT_LOG.md

2. **WS4: Investigate mathopt1 zero MCP objective** (1h)
   - mathopt1: NLP obj = 1.00, MCP obj = 0.00 → 100% divergence
   - Trace through MCP output to find why objective terms are missing
   - Compare to a working model with similar structure

3. **Document fix strategies** (0.5h)
   - For each Category A/D root cause identified:
     - Estimate fix effort
     - Determine if Sprint 22 or Sprint 23
     - File GitHub issues for Sprint 23 items

**Deliverables:**
- Checkpoint 2 GO/NO-GO decision
- Category D root cause documented
- Sprint 23 backlog items filed

**Quality Checks:**
Documentation only — no quality checks unless code changes made.

**Completion Criteria:**
- [ ] Checkpoint 2 evaluated and documented
- [ ] Category D root cause identified
- [ ] Sprint 23 items filed as GitHub issues
- [ ] Mark Day 10 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 10: Checkpoint 2 + WS4 divergence complete" \
             --body "Checkpoint 2 evaluation. Completes solution divergence investigation."
```

---

## Day 11 Prompt: Buffer / Overflow

**Branch:** Create a new branch named `sprint22-day11-buffer` from `main`

**Objective:** Address any overflow from Days 1–10; comprehensive regression testing.

**Prerequisites:**
- Read SPRINT_LOG.md — identify any unfinished workstream tasks
- Read Checkpoint 2 results — any NO-GO items to address?

**Tasks to Complete (~1–2 hours):**

1. **Complete unfinished tasks** (variable)
   - If any workstream targets not met: focus effort here
   - If all targets met: skip to regression testing

2. **Full pipeline retest** (0.5h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - Record pre-close metrics

3. **Comprehensive regression testing** (0.5h)
   - Run `make test` — all tests pass
   - Verify all 65+ solving models still solve
   - Check for any new issues uncovered

**Deliverables:**
- All workstream targets met or documented as blocked
- Final pre-close pipeline metrics

**Completion Criteria:**
- [ ] All workstream targets met or deferred with documentation
- [ ] Full pipeline retest complete
- [ ] 0 regressions
- [ ] Mark Day 11 as complete in PLAN.md

---

## Day 12 Prompt: Sprint Close Prep

**Branch:** Create a new branch named `sprint22-day12-close-prep` from `main`

**Objective:** File issues for deferred items; update documentation.

**Tasks to Complete (~1–2 hours):**

1. **File GitHub issues** (0.5h)
   - Create issues for all deferred/blocked items with `sprint-23` label
   - Include: root cause, estimated effort, models affected

2. **Update KNOWN_UNKNOWNS.md** (0.25h)
   - Document any new unknowns discovered during Sprint 22
   - Update status of existing unknowns resolved by sprint work

3. **Update SPRINT_LOG.md** (0.25h)
   - Record current metrics for all tracked dimensions
   - Note any deferred items

4. **Run `make test`** (0.1h)
   - Confirm all tests pass

**Deliverables:**
- GitHub issues filed for all deferred items
- KNOWN_UNKNOWNS.md updated
- SPRINT_LOG.md current

**Completion Criteria:**
- [ ] All deferred items have GitHub issues
- [ ] Documentation updated
- [ ] Mark Day 12 as complete in PLAN.md

---

## Day 13 Prompt: Final Pipeline Retest + Metrics

**Branch:** Create a new branch named `sprint22-day13-final-retest` from `main`

**Objective:** Final full pipeline run; record definitive sprint metrics.

**Tasks to Complete (~1–2 hours):**

1. **Final full pipeline retest** (0.5h)
   - Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
   - This is the definitive pipeline run — all Sprint 22 changes must be on `main`

2. **Record final metrics** (0.25h)
   - Update SPRINT_LOG.md with final metrics table
   - Compare each metric against targets and stretch goals

3. **Verify acceptance criteria** (0.25h)
   - Check each sprint-level acceptance criterion
   - Document which criteria met, which missed, and why

**Deliverables:**
- Updated `gamslib_status.json` with final pipeline results
- SPRINT_LOG.md with final metrics vs. targets
- Acceptance criteria evaluation

**Completion Criteria:**
- [ ] Final pipeline retest complete
- [ ] Final metrics recorded
- [ ] All acceptance criteria evaluated
- [ ] Mark Day 13 as complete in PLAN.md

---

## Day 14 Prompt: Sprint Close + Retrospective

**Branch:** Create a new branch named `sprint22-day14-retrospective` from `main`

**Objective:** Write sprint retrospective; update project-level documents; outline Sprint 23.

**Tasks to Complete (~1–2 hours):**

1. **Write Sprint 22 Retrospective** (0.5h)
   - Create `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
   - Include: what went well, what didn't, lessons learned
   - Sprint 23 recommendations

2. **Update CHANGELOG.md** (0.25h)
   - Add Sprint 22 summary entry
   - Include all major changes and metrics

3. **Update PROJECT_PLAN.md Rolling KPIs** (0.25h)
   - Fill in Sprint 22 actual numbers in the KPI table

4. **Sprint 23 scope outline** (0.25h)
   - Based on retrospective, outline Sprint 23 priorities
   - Include deferred items from Sprint 22

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
- Updated CHANGELOG.md
- Updated PROJECT_PLAN.md KPIs
- Sprint 23 scope outline

**Quality Checks:**
Documentation only — no quality checks needed.

**Completion Criteria:**
- [ ] Retrospective written
- [ ] CHANGELOG.md updated
- [ ] PROJECT_PLAN.md KPIs updated
- [ ] Sprint 23 scope outlined
- [ ] Mark Day 14 as complete in PLAN.md

**Pull Request & Review:**
```bash
gh pr create --title "Sprint 22 Day 14: Sprint Close + Retrospective" \
             --body "Sprint 22 retrospective, final metrics, Sprint 23 recommendations."
```
