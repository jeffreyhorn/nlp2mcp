# Sprint 22 Preparation Task Prompts

**Purpose:** Day-by-day execution prompts for Sprint 22 prep tasks (Tasks 2-10)
**Usage:** Copy the relevant task prompt into a new Claude Code session to execute it
**Created:** 2026-03-05

---

## Task 2: Catalog path_syntax_error Remaining Subcategories

On branch `planning/sprint22-task2`, created from the current `main` branch, execute Prep Task 2 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

### Objective

Update the Sprint 21 path_syntax_error catalog with current status and prepare a prioritized fix plan for Sprint 22.

### Context

- path_syntax_error is the single largest solve failure category (41 models at Sprint 21 close)
- Sprint 22 targets reducing this to ≤30 (−11 models)
- Sprint 21 `PATH_SYNTAX_ERROR_CATALOG.md` classified 45 models into subcategories A-J
- Sprint 21 WS4 fixed subcategories E (set quoting), D (negative exponents), and parts of A (emission ordering)
- 3 new models (dinam, ferts, tricp) entered this category and are unsubcategorized
- Deferred subcategories for Sprint 22: C (9, uncontrolled sets), B (5, domain violations), G (2, set index reuse), F (1), I (1), J (1)

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 2 full description (lines 135-219)
- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — Sprint 21 subcategory A-J classification
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-01, KU-03, KU-16, KU-17, KU-18, KU-19

### What to Do

1. **Create branch** `planning/sprint22-task2` from `main`
2. **Run latest pipeline** to get current path_syntax_error model list:
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | grep path_syntax_error
   ```
3. **Diff against Sprint 21 catalog** — identify models that moved OUT, moved IN, or stayed
4. **Reclassify unsubcategorized models** (dinam, ferts, tricp, and any new entries) by running GAMS on their MCP files and examining error codes
5. **Update subcategory counts** and prioritize by leverage (models × effort ratio)
6. **Create** `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` with:
   - Updated subcategory breakdown table
   - All current path_syntax_error models classified
   - Prioritized fix order for Sprint 22
   - Effort estimates per subcategory
   - Sprint 22 target subcategories identified (enough for −11 models)

### Known Unknowns to Verify

For each unknown below, update `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` Appendix C (Verification Status Tracking) with your findings. Set "Verified?" to "Yes", fill in the Date, Result, and Action Taken columns.

- **KU-01** (Subcategory C same root cause): Examine GAMS `.lst` error output for 3 representative Subcategory C models (dyncge, glider, harker). Do they all share the same $149 uncontrolled-set pattern, or are there distinct sub-patterns?
- **KU-03** (Subcategory B common emitter bug): Examine emitted parameter data for 2-3 Subcategory B models. Is the $170 domain violation pattern consistent?
- **KU-16** (Subcategory F reserved-word isolated): Search for `gamma`, `psi`, and other GAMS built-in names across model IR outputs. Are other models affected?
- **KU-17** (Subcategory I straightforward): Check why `xb` and `y` are in nemhaus's MCP model statement. Are they missing stationarity equations?
- **KU-18** (Subcategory J pairing logic): Examine pdi's MCP model statement dimension mismatch.
- **KU-19** (3 unsubcategorized models fit existing subcategories): Classify dinam, ferts, tricp — do they match existing subcategories A-J or need a new one?

For each unknown, write the verification result directly in the unknown's "Verification Results" field AND update Appendix C.

### Update PREP_PLAN.md

In `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`:
1. Change Task 2 status from `:large_blue_circle: NOT STARTED` to `:white_check_mark: COMPLETE`
2. Fill in the **Changes** section with what was done
3. Fill in the **Result** section with key findings
4. Check off all acceptance criteria that were met (change `- [ ]` to `- [x]`)

### Update CHANGELOG.md

Add an entry under `## [Unreleased]` (above the Task 1 entry) following this format:
```
### Sprint 22 Prep Task 2: path_syntax_error Catalog Update - YYYY-MM-DD

**Branch:** `planning/sprint22-task2`

#### Added
- Updated path_syntax_error catalog (`docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md`)
  - [describe key findings]

#### Changed
- Updated PREP_PLAN.md: Task 2 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-01, KU-03, KU-16, KU-17, KU-18, KU-19
```

### Quality Gate

This is a research/documentation task — no code changes expected. If any code changes are needed, run:
```bash
make typecheck && make lint && make format && make test
```

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 2: path_syntax_error catalog update"
git push -u origin planning/sprint22-task2
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

Use `gh` to create a PR targeting `main`:
```bash
gh pr create --title "Sprint 22 Prep Task 2: path_syntax_error catalog update" --body "$(cat <<'EOF'
## Summary
- Updated path_syntax_error subcategory catalog for Sprint 22 baseline
- Classified all current path_syntax_error models including 3 unsubcategorized (dinam, ferts, tricp)
- Verified 6 Known Unknowns (KU-01, KU-03, KU-16, KU-17, KU-18, KU-19)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md`
- Updated `PREP_PLAN.md` Task 2 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] PATH_SYNTAX_ERROR_STATUS.md has all current path_syntax_error models classified
- [ ] Subcategory counts match pipeline output
- [ ] Sprint 22 target subcategories identified (enough for −11 models)
- [ ] KNOWN_UNKNOWNS.md Appendix C updated for KU-01, KU-03, KU-16, KU-17, KU-18, KU-19
EOF
)"
```

Then wait for reviewer comments. When the reviewer posts comments, use the standard review workflow:
1. Fetch comments: `gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pulls/PRNUMBER/comments"`
2. Fix issues in code/docs
3. Commit: `git commit -m "Address PR #PRNUMBER review comments"`
4. Push
5. Reply to each comment: `gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pulls/PRNUMBER/comments/$id/replies" -X POST -f body="..."`

---

## Task 3: Classify path_solve_terminated Root Causes

On branch `planning/sprint22-task3`, created from the current `main` branch, execute Prep Task 3 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

### Objective

Map the 12 remaining path_solve_terminated models to actionable fix categories using Sprint 21 PATH_CONVERGENCE_ANALYSIS.md findings.

### Context

- Sprint 22 targets path_solve_terminated ≤ 5 (from 12, −7 models)
- Sprint 21 Day 12 analysis classified all 29 original models into categories A-F
- 14 now solve (Category A), 15 remain: B (5 execution errors), C (4 MCP pairing), D (2 compilation), E (2 timeout), F (2 locally infeasible)
- Key finding: 13 of 15 fail BEFORE PATH runs — pre-solver errors fixable in translator/emitter
- Issue documents exist: #983 (elec), #984 (etamac), #986 (lands)

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 3 full description (lines 222-303)
- `docs/planning/EPIC_4/SPRINT_21/PATH_CONVERGENCE_ANALYSIS.md` — Category A-F classification
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-05, KU-06, KU-09, KU-10, KU-25
- `docs/issues/ISSUE_983_elec-mcp-division-by-zero-distance.md`
- `docs/issues/ISSUE_984_etamac-mcp-division-by-zero-log-singular.md`
- `docs/issues/ISSUE_986_lands-mcp-rhs-na-equation.md`

### What to Do

1. **Create branch** `planning/sprint22-task3` from `main`
2. **Get current path_solve_terminated model list** from latest pipeline output
3. **Map each model** to Sprint 21 Category (B/C/D/E/F) using PATH_CONVERGENCE_ANALYSIS.md
4. **For each model, identify the specific error:**
   - Category B: What domain error? (`.l = 0`, rPower, division by zero?)
   - Category C: What MCP pairing mismatch? (variable count, equation count?)
   - Category D: What data is missing?
   - Category F: Is this genuinely infeasible or a KKT formulation bug?
5. **Cross-reference with issue documents** in `docs/issues/`
6. **Estimate fix effort per model** and group into Sprint 22 fix batches
7. **Create** `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` with:
   - Each of 12 models mapped to fix category with specific error details
   - Cross-references to existing issue documents
   - Fix effort estimates and Sprint 22 batch plan
   - Genuine infeasibility cases identified and excluded from fix targets

### Known Unknowns to Verify

Update `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` for each:

- **KU-05** (Category B execution errors `.l`-fixable): For each of the 5 Category B models, determine if the error is caused by default `.l = 0` values vs other causes. Can `option domlim = 100;` unblock any?
- **KU-06** (`option domlim` sufficiency): Add `option domlim = 100;` to one Category B model's MCP file (e.g., etamac) and run GAMS directly. Does PATH run?
- **KU-09** (Category F genuine): Check chain and rocket model convexity. Would warm-starting from NLP `.l` values change the outcome?
- **KU-10** (Category C MCP pairing bugs): For fdesign, compare IR variable count to emitted MCP variable count. Are stationarity equations being dropped?
- **KU-25** (elec self-pair exclusion): Examine elec's original GAMS file for self-pair exclusion conditions (`$(ord(i) <> ord(j))`).

### Update PREP_PLAN.md

1. Change Task 3 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 3: path_solve_terminated Classification - YYYY-MM-DD

**Branch:** `planning/sprint22-task3`

#### Added
- path_solve_terminated classification (`docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md`)

#### Changed
- Updated PREP_PLAN.md: Task 3 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-05, KU-06, KU-09, KU-10, KU-25
```

### Quality Gate

Research/documentation task. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 3: path_solve_terminated classification"
git push -u origin planning/sprint22-task3
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 3: path_solve_terminated classification" --body "$(cat <<'EOF'
## Summary
- Classified all 12 remaining path_solve_terminated models with specific error details
- Mapped each to Sprint 21 Category (B/C/D/E/F) with fix approach
- Verified 5 Known Unknowns (KU-05, KU-06, KU-09, KU-10, KU-25)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md`
- Updated `PREP_PLAN.md` Task 3 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] All 12 models classified with specific errors
- [ ] Fix effort estimates per model
- [ ] Sprint 22 fix batches defined (enough for −7 models)
- [ ] KNOWN_UNKNOWNS.md updated for KU-05, KU-06, KU-09, KU-10, KU-25
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 4: Triage model_infeasible Models

On branch `planning/sprint22-task4`, created from the current `main` branch, execute Prep Task 4 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

### Objective

Classify the 15 model_infeasible models into KKT formulation bugs (fixable) vs genuine MCP incompatibility (not fixable).

### Context

- Sprint 22 targets model_infeasible ≤ 12 (−3 models)
- 15 models haven't been classified
- Known patterns: #765 (orani, CGE incompatible), #970 (twocge, MCP locally infeasible), #828 (ibm1, stationarity issue)
- model_infeasible grew from 12 to 15 during Sprint 21 as more models reached solve stage

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 4 full description (lines 306-379)
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-23, KU-24
- `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`
- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`
- `docs/planning/EPIC_4/SPRINT_21/SPRINT_RETROSPECTIVE.md` (lines 110-111)

### What to Do

1. **Create branch** `planning/sprint22-task4` from `main`
2. **Get current model_infeasible list** from pipeline output or `data/gamslib/gamslib_status.json`
3. **For each model, examine the GAMS .lst file** — PATH solver status, model status, stationarity/complementarity errors
4. **Classify each model:** KKT bug / starting point / model type incompatible / genuine infeasibility
5. **Cross-reference with issue documents**
6. **Identify 3+ models** with likely KKT bugs as Sprint 22 fix candidates
7. **Create** `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md`

### Known Unknowns to Verify

- **KU-23** (#765 orani fundamentally unfixable): Review model_infeasible list for other CGE-like models with >50% fixed variables. Confirm orani is genuinely incompatible.
- **KU-24** (path_syntax_error fixes may shift models to model_infeasible): Review model types in path_syntax_error subcategories. Estimate how many may shift to model_infeasible when syntax errors are fixed.

### Update PREP_PLAN.md

1. Change Task 4 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 4: model_infeasible Triage - YYYY-MM-DD

**Branch:** `planning/sprint22-task4`

#### Added
- model_infeasible triage (`docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md`)

#### Changed
- Updated PREP_PLAN.md: Task 4 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-23, KU-24
```

### Quality Gate

Research/documentation task. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 4: model_infeasible triage"
git push -u origin planning/sprint22-task4
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 4: model_infeasible triage" --body "$(cat <<'EOF'
## Summary
- Classified all 15 model_infeasible models (KKT bug / starting point / model type / genuine)
- Identified Sprint 22 fix candidates with effort estimates
- Verified 2 Known Unknowns (KU-23, KU-24)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md`
- Updated `PREP_PLAN.md` Task 4 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] All 15 models classified with PATH solver output examined
- [ ] Fix candidates identified with rationale
- [ ] Classification informs Sprint 22 target (≤12 achievable?)
- [ ] KNOWN_UNKNOWNS.md updated for KU-23, KU-24
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 5: Profile Translation Timeout Bottlenecks

On branch `planning/sprint22-task5`, created from the current `main` branch, execute Prep Task 5 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

### Objective

Profile the 11 translation timeout models to identify whether bottlenecks are in Lark/Earley parsing, KKT derivation, or GAMS emission.

### Context

- 11 models timeout during translation (120s limit)
- Issue documents exist: #885 (sarf), #926-#933 (dinam, egypt, ferts, ganges, gangesx, iswnm, nebrazil, tricp)
- Some may be near-miss (130s), others intractable (hours)
- Sprint 22 doesn't explicitly target translation improvements but quick wins may exist

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 5 full description (lines 382-463)
- Sprint 21 SPRINT_RETROSPECTIVE.md (lines 104-105)
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — No specific unknowns for this task

### What to Do

1. **Create branch** `planning/sprint22-task5` from `main`
2. **List all 11 timeout models** from latest pipeline output
3. **For 3-5 representative models**, run translation with profiling:
   ```bash
   timeout 180 .venv/bin/python -c "
   import sys, time; sys.setrecursionlimit(50000)
   from src.ir.parser import parse_file
   t0 = time.time()
   ir = parse_file('data/gamslib/raw/MODEL.gms')
   print(f'Parse: {time.time()-t0:.1f}s')
   # Continue with translation timing...
   "
   ```
4. **Identify bottleneck stage** for each: parsing, IR building, KKT derivation, emission
5. **Classify by tractability:** Near-miss (120-200s), Slow (200-600s), Intractable (>600s)
6. **Create** `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`

### Known Unknowns to Verify

No specific unknowns assigned to this task. If you discover relevant findings for other unknowns, update them.

### Update PREP_PLAN.md

1. Change Task 5 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 5: Translation Timeout Profiling - YYYY-MM-DD

**Branch:** `planning/sprint22-task5`

#### Added
- Translation timeout profile (`docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`)

#### Changed
- Updated PREP_PLAN.md: Task 5 marked COMPLETE
```

### Quality Gate

Research/documentation task. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 5: translation timeout profiling"
git push -u origin planning/sprint22-task5
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 5: translation timeout profiling" --body "$(cat <<'EOF'
## Summary
- Profiled 3-5 representative translation timeout models with stage-level timing
- Classified all 11 timeout models by tractability
- Identified quick-win opportunities (if any)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md`
- Updated `PREP_PLAN.md` Task 5 → COMPLETE

## Test plan
- [ ] All 11 timeout models listed
- [ ] 3-5 models profiled with timing data
- [ ] Tractability classification complete
- [ ] Quick-win recommendations documented
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 6: Survey Deferred Issues for Sprint 22 Fit

On branch `planning/sprint22-task6`, created from the current `main` branch, execute Prep Task 6 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

**Prerequisites:** Tasks 2, 3, and 4 should be completed first (need their findings for overlap assessment). Read their deliverables before starting:
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` (Task 2)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` (Task 3)
- `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` (Task 4)

### Objective

Evaluate the 4 deferred Sprint 21 issues (#764, #765, #827, #830) against Sprint 22 goals and decide which (if any) to include.

### Context

- Deferred issues total 22-30h of architectural work; Sprint 22 has ~24-30h total budget
- #764 (mexss, 8-12h): Accounting variable stationarity
- #765 (orani, detection only): CGE model type incompatible
- #827 (gtm, 6-8h): Domain violations from zero-fill
- #830 (gastrans, 8-10h): Jacobian timeout from dynamic subsets

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 6 full description (lines 466-540)
- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md` — Original triage
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-20, KU-21, KU-22
- Issue documents: `docs/issues/ISSUE_764_*.md`, `docs/issues/ISSUE_765_*.md`, `docs/issues/ISSUE_827_*.md`, `docs/issues/ISSUE_830_*.md`

### What to Do

1. **Create branch** `planning/sprint22-task6` from `main`
2. **Review each deferred issue document**
3. **Assess overlap with Sprint 22 workstreams** (using findings from Tasks 2-4):
   - Does #764 overlap with Subcategory C?
   - Does #827 overlap with Subcategory B?
   - Does #830 overlap with translation timeout work?
4. **Calculate leverage ratio:** models_fixed / effort_hours
5. **Compare to path_syntax_error subcategory leverage** (e.g., Subcategory C: 9 models / 3-5h)
6. **Recommend scope decision:** Include / Defer to Sprint 23 / Won't fix
7. **Create** `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`

### Known Unknowns to Verify

- **KU-20** (#764 overlaps with Subcategory C): After reviewing Task 2's catalog, does the `_add_indexed_jacobian_terms()` guard logic overlap with Subcategory C uncontrolled-set code?
- **KU-21** (#827 overlaps with Subcategory B): After reviewing Task 2's catalog, would the emitter domain filtering fix for Subcategory B also fix gtm, or does gtm need additional parser-side work?
- **KU-22** (#830 independent): Review Sprint 22 fix designs for overlap with `src/ad/index_mapping.py`.

### Update PREP_PLAN.md

1. Change Task 6 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 6: Deferred Issues Decision - YYYY-MM-DD

**Branch:** `planning/sprint22-task6`

#### Added
- Deferred issues decision (`docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`)

#### Changed
- Updated PREP_PLAN.md: Task 6 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-20, KU-21, KU-22
```

### Quality Gate

Research/documentation task. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 6: deferred issues decision"
git push -u origin planning/sprint22-task6
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 6: deferred issues decision" --body "$(cat <<'EOF'
## Summary
- Evaluated 4 deferred Sprint 21 issues against Sprint 22 goals
- Made explicit include/defer/won't-fix decisions with leverage rationale
- Verified 3 Known Unknowns (KU-20, KU-21, KU-22)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md`
- Updated `PREP_PLAN.md` Task 6 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] All 4 deferred issues reviewed with overlap assessment
- [ ] Leverage ratios calculated
- [ ] Explicit decisions with budget impact analysis
- [ ] KNOWN_UNKNOWNS.md updated for KU-20, KU-21, KU-22
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 7: Design path_syntax_error Fix Strategy

On branch `planning/sprint22-task7`, created from the current `main` branch, execute Prep Task 7 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

**Prerequisites:** Task 2 must be completed first (need updated subcategory catalog). Read:
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` (Task 2)

### Objective

Design the implementation approach for fixing Sprint 22's target path_syntax_error subcategories (C, B, G and others as identified in Task 2).

### Context

- path_syntax_error fixes are the highest-leverage Sprint 22 work (−11 models target)
- Subcategory C (9 models): Uncontrolled set in stationarity equations
- Subcategory B (5 models): Domain violation in emitted parameter data
- Subcategory G (2 models): Set index reuse conflict in sum

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 7 full description (lines 543-624)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` (Task 2 output)
- `docs/planning/EPIC_4/SPRINT_21/PATH_SYNTAX_ERROR_CATALOG.md` — Original subcategory details
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-02, KU-04

### What to Do

1. **Create branch** `planning/sprint22-task7` from `main`
2. **For Subcategory C (uncontrolled sets):**
   - Examine 2-3 representative models' MCP output
   - Trace uncontrolled set back to KKT assembly code (`src/kkt/stationarity.py` or `src/emit/emit_gams.py`)
   - Design fix: add domain conditioning or explicit domain controls
   - Identify source files to modify
3. **For Subcategory B (domain violations):**
   - Examine 2-3 models' parameter data sections
   - Identify emitter code that produces out-of-domain data
   - Design fix: filter parameter data by valid domain combinations
4. **For Subcategory G (set index reuse):**
   - Examine the 2 affected models
   - Design fix: rename conflicting indices during KKT derivation
5. **Document implementation plan** with files to modify, estimated LOC, test strategy, risk assessment
6. **Create** `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`

### Known Unknowns to Verify

- **KU-02** (Subcategory C fix regression risk): Review the stationarity equation generation code. Does the fix modify the path used by currently-solving models? What regression test coverage exists?
- **KU-04** (Subcategory G aliasing sufficient): Examine the 2 affected models' conflict pattern. Could alias generation collide with existing identifiers?

### Update PREP_PLAN.md

1. Change Task 7 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 7: path_syntax_error Fix Design - YYYY-MM-DD

**Branch:** `planning/sprint22-task7`

#### Added
- path_syntax_error fix design (`docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`)

#### Changed
- Updated PREP_PLAN.md: Task 7 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-02, KU-04
```

### Quality Gate

Research/documentation task with code exploration. No code changes expected. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 7: path_syntax_error fix design"
git push -u origin planning/sprint22-task7
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 7: path_syntax_error fix design" --body "$(cat <<'EOF'
## Summary
- Designed implementation approach for subcategories C, B, G
- Traced root causes to specific source code files
- Documented test strategy and regression risk assessment
- Verified 2 Known Unknowns (KU-02, KU-04)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md`
- Updated `PREP_PLAN.md` Task 7 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] Representative models examined per subcategory
- [ ] Root cause traced to specific source code
- [ ] Fix approach designed with specific code changes
- [ ] Risk assessment: could fix break currently-solving models?
- [ ] KNOWN_UNKNOWNS.md updated for KU-02, KU-04
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 8: Establish Sprint 22 Baseline Metrics

On branch `planning/sprint22-task8`, created from the current `main` branch, execute Prep Task 8 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

### Objective

Run full pipeline and `make test` to establish the exact Sprint 22 starting baseline, confirming Sprint 21 final metrics.

### Context

- Sprint 21 final: Parse 154/157, Translate 137/154, Solve 65/137, Match 30/65, Tests 3,957
- Sprint 22 targets are defined relative to these baselines
- Need to confirm no regressions from Sprint 21 close to Sprint 22 start

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 8 full description (lines 627-700)
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-14, KU-15

### What to Do

1. **Create branch** `planning/sprint22-task8` from `main`
2. **Ensure main is up to date** with Sprint 21 final state
3. **Run full pipeline:**
   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet
   ```
4. **Run test suite:**
   ```bash
   make test
   ```
5. **Record exact metrics** in all error categories (parse, translate, solve, match, with full error breakdown)
6. **Verify no regressions** from Sprint 21 final checkpoint
7. **Create** `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md` with full error category breakdown

### Known Unknowns to Verify

- **KU-14** (3 remaining lexer_invalid_char low-effort): Run the 3 failing models through parser in verbose mode. What specific characters/patterns cause the failures?
- **KU-15** (Parse rate won't regress): Confirm parse rate is 154/157. If different, investigate.

### Update PREP_PLAN.md

1. Change Task 8 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 8: Baseline Metrics - YYYY-MM-DD

**Branch:** `planning/sprint22-task8`

#### Added
- Sprint 22 baseline metrics (`docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md`)

#### Changed
- Updated PREP_PLAN.md: Task 8 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-14, KU-15

#### Metrics
- Parse: [N]/157
- Solve: [N]
- Match: [N]
- Tests: [N] passed
```

### Quality Gate

```bash
make typecheck && make lint && make format && make test
```

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 8: baseline metrics"
git push -u origin planning/sprint22-task8
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 8: baseline metrics" --body "$(cat <<'EOF'
## Summary
- Ran full pipeline and test suite to establish Sprint 22 baseline
- Recorded all error categories with full breakdown
- Confirmed no regressions from Sprint 21 final
- Verified 2 Known Unknowns (KU-14, KU-15)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md`
- Updated `PREP_PLAN.md` Task 8 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] Full pipeline run completed
- [ ] All error categories captured
- [ ] No regressions from Sprint 21 final
- [ ] Test count confirmed
- [ ] KNOWN_UNKNOWNS.md updated for KU-14, KU-15
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 9: Assess Match Rate Improvement Opportunities

On branch `planning/sprint22-task9`, created from the current `main` branch, execute Prep Task 9 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

**Prerequisites:** Task 3 should be completed first (need path_solve_terminated classification for projections). Read:
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` (Task 3)

### Objective

Identify which of the current 35 "solve but don't match" models have the best chance of matching with targeted fixes, to inform Sprint 22's Match ≥ 35 target.

### Context

- Sprint 22 targets Match ≥ 35 (from 30, +5 models)
- Of 65 solving models, 30 match and 35 don't
- Sprint 21 WS6 improved match rate via tolerance relaxation (DEFAULT_RTOL to 2e-3)
- Issue documents #958-#964 cover objective mismatch cases
- Solution comparison framework: `tests/gamslib/test_test_solve.py`

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 9 full description (lines 703-771)
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` — Unknowns KU-11, KU-12, KU-13, KU-26
- `docs/issues/ISSUE_958_ps2_f_s-objective-mismatch-nonconvex-multi-solve.md` (and #959-#964)
- `docs/research/CONVEXITY_VERIFICATION_DESIGN.md`

### What to Do

1. **Create branch** `planning/sprint22-task9` from `main`
2. **Get current match/mismatch list** from pipeline output or `data/gamslib/gamslib_status.json`
3. **For 5-10 near-miss models** (solve but don't match):
   - Compare MCP objective to NLP objective
   - Classify: tolerance issue, multiple optima, non-convex, or formulation bug
4. **Cross-reference with issue documents** (#958-#964)
5. **Identify models likely to start matching** from Sprint 22 solve improvements
6. **Estimate Sprint 22 match rate improvement**
7. **Create** `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md`

### Known Unknowns to Verify

- **KU-11** (35 non-matching models primarily multi-optima): Extract objective values for all 35. Sort by divergence magnitude. What fraction are near-miss vs clearly different optima?
- **KU-12** (Combined tolerance formula appropriate): Review the 5 near-miss models (ps2_f_s, ps2_s, ps3_s_mn, ps3_s_scp, ps3_s). Would slightly relaxed tolerance match them?
- **KU-13** (Newly-solving models will mostly match): Review model types in path_syntax_error subcategories. Are they convex?
- **KU-26** (NLP solution data available): Check for `.lst` files in `data/gamslib/raw/` for representative models.

### Update PREP_PLAN.md

1. Change Task 9 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 9: Match Rate Analysis - YYYY-MM-DD

**Branch:** `planning/sprint22-task9`

#### Added
- Match rate analysis (`docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md`)

#### Changed
- Updated PREP_PLAN.md: Task 9 marked COMPLETE
- Updated KNOWN_UNKNOWNS.md: Verified KU-11, KU-12, KU-13, KU-26
```

### Quality Gate

Research/documentation task. If code changes needed: `make typecheck && make lint && make format && make test`

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 9: match rate analysis"
git push -u origin planning/sprint22-task9
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 9: match rate analysis" --body "$(cat <<'EOF'
## Summary
- Classified 5-10 near-miss models by divergence type
- Projected Sprint 22 match rate from solve improvements
- Verified 4 Known Unknowns (KU-11, KU-12, KU-13, KU-26)

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md`
- Updated `PREP_PLAN.md` Task 9 → COMPLETE
- Updated `KNOWN_UNKNOWNS.md` verification results

## Test plan
- [ ] 5-10 near-miss models classified
- [ ] Projected match improvement estimated
- [ ] Non-convex multi-optima models identified
- [ ] KNOWN_UNKNOWNS.md updated for KU-11, KU-12, KU-13, KU-26
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Task 10: Plan Sprint 22 Detailed Schedule

On branch `planning/sprint22-task10`, created from the current `main` branch, execute Prep Task 10 from `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md`.

**Prerequisites:** ALL tasks 1-9 must be completed. Read all deliverables before starting:
- `docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md` (Task 1)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` (Task 2)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` (Task 3)
- `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` (Task 4)
- `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md` (Task 5)
- `docs/planning/EPIC_4/SPRINT_22/DEFERRED_ISSUES_DECISION.md` (Task 6)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_FIX_DESIGN.md` (Task 7)
- `docs/planning/EPIC_4/SPRINT_22/BASELINE_METRICS.md` (Task 8)
- `docs/planning/EPIC_4/SPRINT_22/MATCH_RATE_ANALYSIS.md` (Task 9)

### Objective

Create detailed Sprint 22 plan with day-by-day schedule, incorporating all prep task findings.

### Context

- Sprint 22 scope from PROJECT_PLAN.md (lines 509-625)
- PATH Solver Tuning component (4-6h) invalidated by Sprint 21 findings → redirect to pre-solver error fixes
- Sprint 21 Retrospective targets: path_syntax_error ≤30, model_infeasible ≤12, Solve ≥75, Match ≥35, Tests ≥4,020
- Sprint 22 budget: 24-30h

### Reference Documents

- `docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md` — Task 10 full description (lines 774-861)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 509-625) — Sprint 22 scope
- `docs/planning/EPIC_4/PROJECT_PLAN.md` (lines 895-915) — Rolling KPIs
- All Task 2-9 deliverables (listed above)
- `docs/planning/EPIC_4/SPRINT_20/PLAN.md` — Example of detailed sprint plan format
- `docs/planning/EPIC_4/SPRINT_20/prompts/PLAN_PROMPTS.md` — Example of day-by-day prompts format

### What to Do

1. **Create branch** `planning/sprint22-task10` from `main`
2. **Synthesize findings** from Tasks 1-9 into Sprint 22 scope
3. **Define workstreams** (revised from PROJECT_PLAN.md based on Sprint 21 findings):
   - WS1: path_syntax_error subcategory fixes (C, B, G) — use Task 7 design
   - WS2: path_solve_terminated pre-solver error fixes — use Task 3 classification
   - WS3: model_infeasible KKT bug fixes — use Task 4 triage
   - WS4: Solution divergence analysis — use Task 9 analysis
   - WS5: Translation timeout investigation (if quick wins found in Task 5)
   - WS6: Deferred issues (per Task 6 decision)
4. **Create 15-day schedule** (Day 0 – Day 14) with:
   - Day-by-day tasks and workstream assignments
   - Checkpoint gates (Day 5, Day 10, Day 14)
   - Acceptance criteria per checkpoint
   - Pipeline retest points
5. **Define acceptance criteria** aligned with Sprint 22 targets
6. **Create** `docs/planning/EPIC_4/SPRINT_22/PLAN.md` — full 15-day schedule
7. **Create** `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
8. **Create** `docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md` — template with day sections

### Known Unknowns to Verify

All remaining unverified unknowns should be addressed by synthesizing findings from Tasks 2-9. Update any unknowns that were discovered to be wrong or need revision.

### Update PREP_PLAN.md

1. Change Task 10 status to `:white_check_mark: COMPLETE`
2. Fill in Changes and Result sections
3. Check off all acceptance criteria
4. Check off remaining Success Criteria checkboxes

### Update CHANGELOG.md

Add entry under `## [Unreleased]`:
```
### Sprint 22 Prep Task 10: Sprint 22 Plan - YYYY-MM-DD

**Branch:** `planning/sprint22-task10`

#### Added
- Sprint 22 detailed plan (`docs/planning/EPIC_4/SPRINT_22/PLAN.md`)
- Sprint 22 day-by-day prompts (`docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md`)
- Sprint 22 log template (`docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md`)

#### Changed
- Updated PREP_PLAN.md: Task 10 marked COMPLETE; all Success Criteria checked
- Updated KNOWN_UNKNOWNS.md: Final verification pass
```

### Quality Gate

```bash
make typecheck && make lint && make format && make test
```

### Commit and Push

```bash
git add docs/planning/EPIC_4/SPRINT_22/PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md \
        docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md \
        docs/planning/EPIC_4/SPRINT_22/PREP_PLAN.md \
        docs/planning/EPIC_4/SPRINT_22/KNOWN_UNKNOWNS.md \
        CHANGELOG.md
git commit -m "Complete Sprint 22 Prep Task 10: detailed sprint plan"
git push -u origin planning/sprint22-task10
```

Do NOT include `Co-Authored-By` lines in commit messages.

### Create Pull Request

```bash
gh pr create --title "Sprint 22 Prep Task 10: detailed sprint plan" --body "$(cat <<'EOF'
## Summary
- Created Sprint 22 detailed plan with 15-day schedule and 6 workstreams
- Created day-by-day execution prompts for all sprint days
- Created sprint log template
- All prep tasks complete; Sprint 22 ready to begin

## Deliverables
- `docs/planning/EPIC_4/SPRINT_22/PLAN.md` — full 15-day schedule with checkpoints
- `docs/planning/EPIC_4/SPRINT_22/prompts/PLAN_PROMPTS.md` — day-by-day prompts
- `docs/planning/EPIC_4/SPRINT_22/SPRINT_LOG.md` — log template
- Updated `PREP_PLAN.md` — all tasks COMPLETE, all Success Criteria checked

## Test plan
- [ ] Plan covers all 15 days with workstream assignments
- [ ] Checkpoint gates at Days 5, 10, 14 with go/no-go criteria
- [ ] Acceptance criteria match Sprint 22 targets
- [ ] Known unknowns referenced in plan
- [ ] Contingency plans for high-risk workstreams
- [ ] Day-by-day prompts created for all days
- [ ] Sprint log template has day sections
EOF
)"
```

Then wait for reviewer comments and handle them using the standard workflow.

---

## Quick Reference: Execution Order

### Phase 1 — Independent Tasks (can run in parallel)
- **Task 2**: path_syntax_error catalog → `planning/sprint22-task2`
- **Task 3**: path_solve_terminated classification → `planning/sprint22-task3`
- **Task 4**: model_infeasible triage → `planning/sprint22-task4`
- **Task 5**: Translation timeout profiling → `planning/sprint22-task5`
- **Task 8**: Baseline metrics → `planning/sprint22-task8`

### Phase 2 — Dependent Tasks (need Phase 1 outputs)
- **Task 6**: Deferred issues survey → `planning/sprint22-task6` (needs Tasks 2, 3, 4)
- **Task 7**: path_syntax_error fix design → `planning/sprint22-task7` (needs Task 2)
- **Task 9**: Match rate analysis → `planning/sprint22-task9` (needs Task 3)

### Phase 3 — Final Planning (needs all above)
- **Task 10**: Detailed schedule → `planning/sprint22-task10` (needs Tasks 1-9)

### Critical Path: Tasks 2 → 7 → 10

### Standard Review Workflow (all tasks)

When the reviewer posts comments on a PR:
1. Fetch: `gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pulls/PRNUMBER/comments"`
2. Find unreplied comments (no `replies` or reply count 0)
3. Fix issues in code/docs
4. Commit: `git commit -m "Address PR #PRNUMBER review comments"`
5. Push: `git push`
6. Reply to EACH comment individually: `gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pulls/PRNUMBER/comments/$id/replies" -X POST -f body="..."`
