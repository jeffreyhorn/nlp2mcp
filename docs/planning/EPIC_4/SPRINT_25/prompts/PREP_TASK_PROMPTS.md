# Sprint 25 Prep Task Execution Prompts

Self-contained prompts for Sprint 25 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**
1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch, does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 25 Known Unknowns List) is already complete — no prompt needed.

Tasks 2–11 are dispatchable in the following order per the dependency graph in `PREP_PLAN.md`:

- **Parallel kickoff (no dependencies beyond Task 1):** Tasks 2, 3, 4, 7, 8, 9
- **After Task 4:** Task 5
- **After Task 3:** Task 10
- **After Task 2:** Task 6
- **After all:** Task 11 (final integration)

---

## Task 2 Prompt: Audit Alias-AD Carryforward State

**Branch:** Create a new branch named `planning/sprint25-task2` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Survey exactly what landed in Sprint 24's partial alias-AD work, classify the 11 remaining open issues by Pattern (A/B/C/D/E), and produce a state-of-play document that Task 6 (rollout design) can build on.

**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8

**Prerequisites (read before starting):**
- `docs/planning/EPIC_4/SPRINT_25/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` §Category 1 (Unknowns 1.1–1.8)
- `docs/planning/EPIC_4/SPRINT_24/SPRINT_LOG.md` — Day 1–5 alias-AD entries
- `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md` — pattern classification
- `docs/planning/EPIC_4/SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` — current design state
- GitHub issues: #1138, #1139, #1140, #1141, #1142, #1143, #1144, #1145, #1146, #1147, #1150

**Tasks to Complete:**

1. **Inventory Sprint 24 landed work:** grep `src/ad/` and `src/kkt/` for summation-context / alias-match helpers; cross-reference with PRs merged during Sprint 24 touching alias-AD.
2. **Re-run reproduction for each of the 11 open issues:** translate + solve each model, record current failure signature, compare against Sprint 24 Day 13 Addendum `gamslib_status.json`.
3. **Classify each issue by Pattern** (A = summation index; B = bound-index guard; C = offset-alias; D = condition-scope; E = non-differentiation).
4. **Map Pattern → architectural fix site** (`src/ad/*` paths, dependencies between issues, subsume-opportunities).
5. **Identify regression risks** among the 54 currently-matching models; produce a canary-test ladder beyond `dispatch`.

**Deliverables (produce these files):**
- `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` — state-of-play document
- Pattern classification table for all 11 open issues (in the doc)
- Landed-vs-stubbed inventory for `src/ad/` and `src/kkt/` helpers (in the doc)
- Canary-test priority list (in the doc)

**Known Unknowns Updates:**

For each of Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 in `SPRINT_25/KNOWN_UNKNOWNS.md`, add to the "Verification Results" subsection:

- Status: ✅ VERIFIED or ❌ WRONG (replace the initial 🔍 INCOMPLETE)
- Verified by: Task 2 (Alias-AD Carryforward Audit)
- Date: today's date (YYYY-MM-DD)
- Findings: bullet list of what the audit found
- Evidence: specific file paths, commit SHAs, or issue numbers referenced
- Decision: "Proceed with assumption as-stated" / "Revised assumption: …" / "Blocked pending …"

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_25/PREP_PLAN.md` §Task 2:
- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Fill in the "Changes" section with a summary of what was done
- Fill in the "Result" section with the key findings (Pattern distribution, regression-risk summary)
- Check off all items in "Acceptance Criteria" (change `- [ ]` → `- [x]`)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 25 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Audited Sprint 24 alias-AD carryforward state. Classified all 11 open alias issues (#1138–#1147, #1150) by Pattern: [fill in distribution]. Inventory of landed-vs-stubbed helpers in `src/ad/`. Regression-risk canary list beyond `dispatch`: [fill in]. Verified Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8.
```

**Quality Gate:**

Task 2 is research/docs only. No Python source code is modified. **Skip the Python quality gate.** If you touched any `.py` file unexpectedly, run:

```bash
make typecheck && make lint && make format && make test
```

Do NOT proceed to commit until all pass.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 2: Audit Alias-AD Carryforward State

Pattern classification across the 11 open alias-differentiation issues
(#1138–#1147, #1150) for Sprint 25 Priority 1 planning.

## Key findings

- Pattern A (summation index): [N issues: list]
- Pattern C (offset-alias): [N issues: list]
- Pattern E (non-differentiation): [N issues: list]
- Sprint 24 landed: [summary]
- Sprint 24 stubbed: [summary]
- Regression-risk canary ladder beyond dispatch: [list]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 1.1, 1.2, 1.3, 1.4,
  1.6, 1.7, 1.8 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 2 status → COMPLETE
- Updated CHANGELOG.md with Task 2 completion entry
```

**Pull Request:**

After committing, push the branch and open a PR:

```bash
git push -u origin planning/sprint25-task2
gh pr create --title "Complete Sprint 25 Prep Task 2: Audit Alias-AD Carryforward State" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] No Python source code modified — quality gate skipped per workflow rules
- [x] All 11 open alias issues classified by Pattern
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Investigate Parser Non-Determinism (#1283)

**Branch:** Create a new branch named `planning/sprint25-task3` from `main`

**Priority:** Critical (2–3 hours)

**Objective:** Root-cause the non-deterministic parser behavior on multi-row-label tables like `(low,medium,high).ynot`, or at minimum narrow it to 1–2 candidate code paths.

**Unknowns Verified:** 2.1, 2.2

**Prerequisites (read before starting):**
- `docs/planning/EPIC_4/SPRINT_25/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.1, 2.2)
- `docs/issues/ISSUE_1283_parser-non-deterministic-multi-row-label-table.md`
- GitHub issue: #1283
- Sprint 24 KU-27 (Lark 1.1.9 vs 1.2+ ambiguity — related pattern)

**Tasks to Complete:**

1. **Reliable reproduction:** Run `src.cli chenery.gms` 20× with `PYTHONHASHSEED=0..19`; count correct vs corrupted runs; find the minimum reproducer (smallest table that triggers it).
2. **Narrow root cause:** Add targeted `logger.debug` calls in `src/ir/parser.py` table-parsing paths and `src/gams/gams_grammar.lark` rule handlers; compare IR between correct and corrupted runs.
3. **Document the specific trigger:** What property of the column headers / row labels / column count / row count causes it?
4. **Scope survey:** grep corpus for `(v1,v2,...).col` multi-row-label patterns; identify which other models may be affected.
5. **Propose a fix approach** (don't implement yet): Option A (replace set with list), Option B (regex anchoring), Option C (Lark unambiguous mode); document expected regression surface for each.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md`
- Reproduction recipe with `PYTHONHASHSEED` sweep
- Minimum reproducer
- Narrowed root cause or ranked candidates
- Proposed fix approach with regression-surface analysis
- List of potentially-affected corpus models

**Known Unknowns Updates:**

For Unknowns 2.1 and 2.2 in `SPRINT_25/KNOWN_UNKNOWNS.md`, update Verification Results:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 3 (Parser Non-Determinism Investigation)
- Date: today's date
- Findings: corruption rate, root-cause candidates, affected model count
- Evidence: reproduction output, code paths traced, grep results
- Decision: proposed fix approach selected (A / B / C) with rationale

**PREP_PLAN.md Updates:**

In `SPRINT_25/PREP_PLAN.md` §Task 3:
- Status → ✅ COMPLETE
- Fill "Changes" and "Result" sections
- Check off all Acceptance Criteria

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 25 Preparation`, prepend:

```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Investigated parser non-determinism #1283. Corruption rate on chenery: [N/20]; root cause narrowed to [1–2 code paths]; [N] additional corpus models potentially affected. Proposed fix: Option [A/B/C] — [one-line rationale]. Verified Unknowns 2.1, 2.2.
```

**Quality Gate:**

Research/docs only. Skip Python quality gate unless a `.py` file was touched. If so:
```bash
make typecheck && make lint && make format && make test
```

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 3: Investigate Parser Non-Determinism (#1283)

Root-cause analysis of the multi-row-label table parsing
non-determinism that quietly corrupted chenery_mcp.gms
throughout Sprint 24.

## Key findings

- Corruption rate on chenery (20-seed sweep): [N/20 = X%]
- Minimum reproducer: [description]
- Root cause narrowed to: [1–2 code paths]
- Affected corpus models: [count + list]
- Proposed fix: Option [A/B/C] — [rationale]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 2.1, 2.2 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 3 status → COMPLETE
- Updated CHANGELOG.md with Task 3 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 3: Investigate Parser Non-Determinism (#1283)" --body "<paste commit body>"` then wait for reviewer comments.

---

## Task 4 Prompt: Categorize Emitter Bug Backlog (#1275–#1281)

**Branch:** Create a new branch named `planning/sprint25-task4` from `main`

**Priority:** High (2–3 hours)

**Objective:** Group the 7 emitter / stationarity issues surfaced during Sprint 24 Day 13 review into a fix-order that surfaces shared code paths and identifies parallelizable work.

**Unknowns Verified:** 2.3, 2.4, 2.5

**Prerequisites (read before starting):**
- `docs/planning/EPIC_4/SPRINT_25/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` §Category 2 (Unknowns 2.3, 2.4, 2.5)
- `docs/issues/ISSUE_127{5,6,7,8,9}_*.md`, `docs/issues/ISSUE_1280_*.md`, `docs/issues/ISSUE_1281_*.md`
- GitHub issues: #1275, #1276, #1277, #1278, #1279, #1280, #1281

**Tasks to Complete:**

1. **Re-read each issue's in-tree doc** to understand fix scope.
2. **Classify each issue by code path:** emitter (`src/emit/`), IR normalize (`src/ir/normalize.py`), stationarity/AD (`src/kkt/`, `src/ad/`).
3. **Identify shared code paths** — same emission function? Same dedup helper?
4. **Propose fix order in 3 batches** (Batch 1 for Days 1–2 alongside alias-AD start, Batch 2 for Days 3–4, Batch 3 for Days 5+).
5. **Estimate per-fix effort** so Task 11 can assign to specific days.
6. **Cross-reference with Task 2's alias-AD classification**: which of #1277/#1278 are subsumed by the alias-AD fix?

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md`
- Per-issue classification by code path and fix complexity
- Shared-code-path map identifying subsume-opportunities
- Proposed batch ordering with per-fix effort estimate
- Cross-reference: which of #1277 / #1278 are subsumed by Task 2's alias-AD fix

**Known Unknowns Updates:**

For Unknowns 2.3, 2.4, 2.5 in `SPRINT_25/KNOWN_UNKNOWNS.md`, update Verification Results:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 4 (Emitter Backlog Categorization)
- Date: today
- Findings: code-path classification, subsume-opportunities, effort estimates
- Evidence: file paths, function names, issue-to-code-path mappings
- Decision: fix order + batch assignment

**PREP_PLAN.md Updates:** Task 4 → ✅ COMPLETE; fill Changes/Result; check off all Acceptance Criteria.

**CHANGELOG.md Update:** Prepend `- **Prep Task 4 COMPLETE (YYYY-MM-DD):** ...` entry with classification summary and batch plan. Verified Unknowns 2.3, 2.4, 2.5.

**Quality Gate:** Skip if no `.py` changes; otherwise `make typecheck && make lint && make format && make test`.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 4: Categorize Emitter Bug Backlog (#1275-#1281)

## Key findings

- Emitter (src/emit/): [list issues]
- IR normalize (src/ir/normalize.py): [list issues]
- Stationarity / AD (src/kkt/, src/ad/): [list issues]
- Subsumed by Task 2 alias-AD fix: [list]
- Shared-code-path merges possible: [list]
- Proposed batches: Batch 1 [issues, ~Nh], Batch 2 [...], Batch 3 [...]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/CATALOG_EMITTER_BACKLOG.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 2.3, 2.4, 2.5 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 4 status → COMPLETE
- Updated CHANGELOG.md with Task 4 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 4: Categorize Emitter Bug Backlog (#1275-#1281)" --body "<paste>"` and wait for reviewer comments.

---

## Task 5 Prompt: Analyze Recovered-Translate Models (ganges family)

**Branch:** Create a new branch named `planning/sprint25-task5` from `main`

**Priority:** High (2–3 hours)

**Objective:** Map each of the 5 "recovered-translate → path_syntax_error" models (ganges, gangesx, ferts, clearlak, turkpow) to specific emitter bugs so Task 11 can schedule fixes that actually unblock new solves.

**Unknowns Verified:** 2.6

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 5
- `SPRINT_25/KNOWN_UNKNOWNS.md` Unknown 2.6
- `SPRINT_25/CATALOG_EMITTER_BACKLOG.md` (from Task 4 — must complete first)
- `SPRINT_24/SPRINT_LOG.md` §Day 13 Addendum — "recovered translate" finding
- Current `data/gamslib/gamslib_status.json` for the 5 models

**Tasks to Complete:**

1. For each of the 5 models (`ganges`, `gangesx`, `ferts`, `clearlak`, `turkpow`): run `gams <model>_mcp.gms action=c` to compile-check; record compile errors verbatim.
2. Map each compile error to one of the 8 tracked emitter bugs (#1275–#1281, #1283) OR identify as new untracked bug.
3. Build a leverage matrix: rows = 5 models, columns = 8 bugs; mark which fix each model depends on.
4. File any new emitter-bug tracking issues on GitHub with `sprint-25` label; add matching in-tree `docs/issues/ISSUE_NNNN_*.md` docs.
5. Rank fix priority by model-unblocking leverage (which single fix unblocks the most of the 5?).

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md`
- Per-model compile-error list
- Leverage matrix (5 × ≥8)
- Any new GitHub issues filed (link in doc)
- Ranked fix priority list

**Known Unknowns Updates:**

Update Unknown 2.6 in `SPRINT_25/KNOWN_UNKNOWNS.md`:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 5
- Date: today
- Findings: per-model unblocking analysis, highest-leverage fix identified
- Evidence: compile-check outputs, leverage-matrix cells
- Decision: fix priority order for Sprint 25 Priority 2

**PREP_PLAN.md Updates:** Task 5 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 5 COMPLETE (YYYY-MM-DD):** ...` with leverage findings. Verified Unknown 2.6.

**Quality Gate:** Skip unless `.py` touched; otherwise full gate.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 5: Analyze Recovered-Translate Models

Maps each of the 5 ganges-family recovered translates to the specific
emitter bugs that block their PATH compile.

## Key findings

- Highest-leverage single fix: [#NNNN unblocks N of 5 models]
- Fix-minimal subset unblocking ≥3 of 5: [#NNNN + #MMMM]
- New emitter bugs discovered: [list with new issue numbers]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/ANALYSIS_RECOVERED_TRANSLATES.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknown 2.6 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 5 status → COMPLETE
- Updated CHANGELOG.md with Task 5 completion entry
- [Any new GitHub issues filed]
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 5: Analyze Recovered-Translate Models" --body "<paste>"` and wait for reviewer comments.

---

## Task 6 Prompt: Design Alias-AD Rollout Plan

**Branch:** Create a new branch named `planning/sprint25-task6` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Produce a day-by-day rollout design for the alias-AD carryforward work, with explicit regression-guard strategy, per-pattern validation gates, and defined "stop the sprint" triggers.

**Unknowns Verified:** 1.5, 1.8 (integrates Task 2's findings on 1.1, 1.2, 1.3, 1.4, 1.6, 1.7)

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 6
- `SPRINT_25/KNOWN_UNKNOWNS.md` Unknowns 1.5, 1.8
- `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` (from Task 2 — must complete first)
- `SPRINT_24/DESIGN_ALIAS_DIFFERENTIATION_V2.md` and Sprint 23 DESIGN_ALIAS_DIFFERENTIATION.md
- `SPRINT_24/PLAN.md` §Day 5 Checkpoint 1 procedure (use as template for Sprint 25 Checkpoints)

**Tasks to Complete:**

1. **Define 4 phases** mapped to Days 1–12:
   - Phase 1 (Days 1–3): complete Pattern A fix for clearest-diagnosed models
   - Phase 2 (Days 3–6): validate Pattern A across all models; start Pattern C for polygon/himmel16/cclinpts
   - Phase 3 (Days 7–9): Pattern B/D edge cases (kand, launch)
   - Phase 4 (Days 10–12): #1150 distinct-sum-indices collapse; final regression sweep
2. **Define per-phase gates** (quantitative pass/fail criteria).
3. **Define regression-guard infrastructure:** golden-file set for 54 matching models, canary ladder, per-model verification script.
4. **Define "stop the sprint" triggers** (≥3 explicit conditions).
5. **Allocate parallel work:** map Priority 2 (emitter) batches from Task 4 to days where alias-AD is in phase-transition waits.
6. **Address Unknown 1.5 (sameas guard validation):** propose a regression-test matrix covering numeric, string, hyphenated, plus-signed, and dotted elements.
7. **Address Unknown 1.8 (feature-flag rollout):** decide feature-flag vs all-or-nothing and document rollback procedure.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md`
- 4 phases with day ranges and target-model lists
- Per-phase gate definitions
- "Stop the sprint" trigger list
- Parallel-work allocation
- Regression-guard infrastructure design (golden files, canary list, scripts)
- sameas-guard regression-test matrix
- Rollout-flag decision + rollback procedure

**Known Unknowns Updates:**

Update Unknowns 1.5 and 1.8 in `SPRINT_25/KNOWN_UNKNOWNS.md`:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 6
- Date: today
- Findings: rollout decisions, sameas-guard test matrix, regression-guard infrastructure
- Evidence: design doc references
- Decision: explicit rollout strategy

**PREP_PLAN.md Updates:** Task 6 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 6 COMPLETE (YYYY-MM-DD):** ...` with phase summary. Verified Unknowns 1.5, 1.8.

**Quality Gate:** Skip unless `.py` touched.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 6: Design Alias-AD Rollout Plan

Day-by-day rollout design for the Sprint 25 Priority 1 alias-AD
carryforward work, with explicit phase gates and stop-the-sprint
triggers.

## Key findings

- Phase 1 (Days 1–3): [target models, gate criteria]
- Phase 2 (Days 3–6): [...]
- Phase 3 (Days 7–9): [...]
- Phase 4 (Days 10–12): [...]
- Stop triggers: [list]
- Rollout strategy: [feature-flag / all-or-nothing] — [rationale]
- sameas-guard regression matrix: [N element types × N tests]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 1.5, 1.8 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 6 status → COMPLETE
- Updated CHANGELOG.md with Task 6 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 6: Design Alias-AD Rollout Plan" --body "<paste>"` and wait for reviewer comments.

---

## Task 7 Prompt: Scope Multi-Solve Gate + Dispatcher Refactor

**Branch:** Create a new branch named `planning/sprint25-task7` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Produce lightweight design notes for the two smaller Sprint 25 priorities — #1270 (multi-solve gate extension) and #1271 (dispatcher refactor) — so they can be dispatched as 1-day work items without needing further design during the sprint.

**Unknowns Verified:** 3.1, 3.2, 3.3, 4.1, 4.2, 4.3

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 7
- `SPRINT_25/KNOWN_UNKNOWNS.md` Categories 3 and 4 (Unknowns 3.1–3.3, 4.1–4.3)
- `docs/issues/ISSUE_1270_multi-solve-gate-saras-style-top-level-marginal-reads.md`
- `docs/issues/ISSUE_1271_refactor-collapse-loop-tree-dispatchers.md`
- Sprint 24 KU-29 (saras-style), KU-30 (dispatcher duplication)
- `src/validation/driver.py` current implementation
- `src/emit/original_symbols.py::_loop_tree_to_gams` + `_loop_tree_to_gams_subst_dispatch`

**Tasks to Complete:**

1. **#1270 Multi-Solve Gate:**
   - Commit to Approach A (cross-reference) with rationale
   - Corpus survey: grep for top-level `eq.m` reads; identify candidate models
   - Test-fixture matrix: saras (must-flag), partssupply (must-not-flag), post-solve-reporting fixture, multi-stage display fixture
   - Identify single function in `src/validation/driver.py` that needs extension
2. **#1271 Dispatcher Refactor:**
   - Define unified signature `_loop_tree_to_gams(tree, *, token_subst=None)`
   - List callers of both dispatchers; confirm rename plan
   - Byte-diff regression strategy: pre/post compare across all 99 currently-translating models
   - Document backward-compatibility window (if any)
3. **Combined effort estimate** and day allocation for Sprint 25 schedule.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md`
- #1270 design: approach commit, corpus survey, test-fixture matrix
- #1271 design: unified signature, caller inventory, byte-diff strategy
- Day allocation for both items

**Known Unknowns Updates:**

Update Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 7
- Date: today
- Findings: corpus survey results, design decisions
- Evidence: grep output, caller list
- Decision: design committed per unknown

**PREP_PLAN.md Updates:** Task 7 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 7 COMPLETE (YYYY-MM-DD):** ...` with design decisions for both #1270 and #1271. Verified Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3.

**Quality Gate:** Skip unless `.py` touched.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 7: Scope Multi-Solve Gate + Dispatcher Refactor

Design notes for Sprint 25 Priorities 3 (#1270) and 4 (#1271).

## Key findings

- #1270: Approach A (cross-reference) committed. Corpus survey
  identifies [N] models that the extended gate will flag:
  saras + [list]. partssupply remains NOT-flagged (regression canary).
- #1271: unified signature `_loop_tree_to_gams(tree, *, token_subst=None)`.
  [N] callers updated. Byte-diff regression across 99 models expected
  to show zero diffs; any diff → investigate.
- Combined effort: [Nh] (Priorities 3 + 4 fit into ≤ 7h per PREP_PLAN budget)

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/DESIGN_SMALL_PRIORITIES.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 7 status → COMPLETE
- Updated CHANGELOG.md with Task 7 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 7: Scope Multi-Solve Gate + Dispatcher Refactor" --body "<paste>"` and wait for reviewer comments.

---

## Task 8 Prompt: Profile Hard Translation Timeouts

**Branch:** Create a new branch named `planning/sprint25-task8` from `main`

**Priority:** Low (2–3 hours)

**Objective:** Profile the 5 remaining hard translation timeouts (`iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`) under the 600s budget to identify bottleneck stages and determine whether Priority 5 work is tractable.

**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 8
- `SPRINT_25/KNOWN_UNKNOWNS.md` §Category 5 (Unknowns 5.1–5.4)
- Sprint 24 KU-19 (timeout models fundamentally intractable), KU-20 (sparse Jacobian)
- GitHub issues: #1169 (lop, recovered), #1185 (mexls), #1192 (gtm)

**Tasks to Complete:**

1. **Instrument stage timing** for each of the 5 models: parse / IR build / normalize / AD / KKT emit.
2. **Run each under a 900s budget** (allow some to complete beyond 600s cap) to get full profile.
3. **Classify each model:**
   - Likely tractable (< 30% over budget, clear single-stage bottleneck)
   - Likely intractable at current architecture (> 2× over budget, multi-stage)
   - Unclear
4. **For tractable models:** propose a specific optimization (caching, redundant computation, algorithm swap).
5. **Address Unknown 5.3:** estimate Jacobian non-zero density; evaluate sparse-Jacobian feasibility.
6. **Address Unknown 5.4:** is `srpchase` (tiny 107-line model) a preprocessor / macro-expansion issue rather than AD/KKT?
7. **Priority 5 scope recommendation:** fix N models in Sprint 25 OR defer all to Sprint 26+.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md`
- Per-model stage-timing breakdown
- Per-model tractability classification
- For tractable models: optimization proposals
- Priority 5 scope recommendation

**Known Unknowns Updates:**

Update Unknowns 5.1, 5.2, 5.3, 5.4:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 8
- Date: today
- Findings: per-model stage-timing, tractability, optimization candidates
- Evidence: profiler output, Jacobian density estimates
- Decision: Priority 5 scope for Sprint 25

**PREP_PLAN.md Updates:** Task 8 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 8 COMPLETE (YYYY-MM-DD):** ...` with tractability classifications. Verified Unknowns 5.1, 5.2, 5.3, 5.4.

**Quality Gate:** Skip unless `.py` touched (profile instrumentation may add Python code temporarily — if keeping, run full gate; if deleting after profiling, skip).

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 8: Profile Hard Translation Timeouts

Stage-level profiling of the 5 remaining hard-timeout models under
a 900s budget.

## Key findings

- iswnm: [bottleneck stage] ([time]) — [tractable / intractable / unclear]
- mexls: [...]
- nebrazil: [...]
- sarf: [...]
- srpchase: [...]
- Sparse Jacobian viability: [feasible for N models / not applicable]
- srpchase root cause: [preprocessor / AD / other]
- Priority 5 recommendation: [fix N models in Sprint 25 / defer all]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknowns 5.1, 5.2, 5.3, 5.4 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 8 status → COMPLETE
- Updated CHANGELOG.md with Task 8 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 8: Profile Hard Translation Timeouts" --body "<paste>"` and wait for reviewer comments.

---

## Task 9 Prompt: Run Full Pipeline Baseline + Freeze Scope (PR6 / PR15)

**Branch:** Create a new branch named `planning/sprint25-task9` from `main`

**Priority:** Critical (1–2 hours)

**Objective:** Record Sprint 25's Day 0 baseline via a full pipeline run (per PR6) and freeze the pipeline scope (per PR15) before Sprint 25 starts.

**Unknowns Verified:** 6.1

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 9
- `SPRINT_25/KNOWN_UNKNOWNS.md` Unknown 6.1
- Sprint 24 retrospective §New Recommendations PR6 (full pipeline baseline) and PR15 (freeze scope)
- Current `data/gamslib/gamslib_status.json` (Day 13 Addendum state)
- `scripts/gamslib/run_full_test.py --quiet`

**Tasks to Complete:**

1. Snapshot current `data/gamslib/gamslib_status.json` pre-retest.
2. Run the full pipeline: `scripts/gamslib/run_full_test.py --quiet` (~2h under doubled timeouts).
3. Verify stable results (per Task 10's determinism work — expect chenery corruption until #1283 fixed).
4. Record baseline numbers in `SPRINT_25/BASELINE_METRICS.md`:
   - Parse / Translate / Solve / Match
   - path_syntax_error / path_solve_terminated / model_infeasible / path_solve_license
   - Scope breakdown (143 in-scope, exclusions by reason)
5. Freeze scope (PR15): document current v2.2.1 exclusion set; commit to no exclusion changes during Sprint 25 unless gate-driven.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md`
- Frozen pipeline-scope declaration
- Updated `data/gamslib/gamslib_status.json` (fresh baseline)

**Known Unknowns Updates:**

Update Unknown 6.1:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 9
- Date: today
- Findings: scope frozen at 143 models; policy for mid-sprint gate additions
- Evidence: exclusion-reason breakdown, BASELINE_METRICS values
- Decision: scope-freeze policy

**PREP_PLAN.md Updates:** Task 9 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 9 COMPLETE (YYYY-MM-DD):** ...` with baseline metrics and scope-freeze declaration. Verified Unknown 6.1.

**Quality Gate:** The pipeline run may regenerate MCP artifacts. If any `.py` changed: `make typecheck && make lint && make format && make test`. Regenerated `data/gamslib/mcp/*.gms` do not count as `.py` changes.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 9: Full Pipeline Baseline + Freeze Scope

Sprint 25 Day 0 baseline metrics per PR6; scope freeze per PR15.

## Key findings

- Parse: [N/143] | Translate: [N/143 (X%)]
- Solve: [N] | Match: [N]
- path_syntax_error: [N] | path_solve_terminated: [N]
- model_infeasible: [N] | path_solve_license: [N]
- Scope frozen at 143 models (14 MINLP + 7 legacy + 2 multi-solve exclusions)

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md
- Updated data/gamslib/gamslib_status.json
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknown 6.1 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 9 status → COMPLETE
- Updated CHANGELOG.md with Task 9 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 9: Full Pipeline Baseline + Freeze Scope" --body "<paste>"` and wait for reviewer comments.

---

## Task 10 Prompt: Design Byte-Stability Test Infrastructure (PR12)

**Branch:** Create a new branch named `planning/sprint25-task10` from `main`

**Priority:** High (1–2 hours)

**Objective:** Design the byte-stability regression test infrastructure (PR12) — a test harness that runs the pipeline under multiple `PYTHONHASHSEED` values and asserts byte-identical `.gms` output across runs.

**Unknowns Verified:** 6.2

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 10
- `SPRINT_25/KNOWN_UNKNOWNS.md` Unknown 6.2
- `SPRINT_25/INVESTIGATION_PARSER_NON_DETERMINISM.md` (from Task 3 — must complete first)
- Sprint 24 retrospective §PR12 recommendation
- `.github/workflows/ci.yml` — current CI fast-test-suite configuration

**Tasks to Complete:**

1. **Decide test scope:**
   - Option A (cheap): 5-model per-commit test (~30s)
   - Option B (comprehensive): full-pipeline nightly (~4h)
   - Option C (both)
2. **Define fixture set for Option A:** chenery (known reproducer), 1 multi-row-label table regression guard, 1 simple model (framework sanity), 2 from CGE / alias-heavy families.
3. **Decide seed set:** fixed (0, 1, 42, 12345, 99999) or random sample with logged seeds.
4. **Design the assertion:** byte-identical MCP output; on failure log first-differing seed + diff.
5. **Plan CI integration:** new test file `tests/integration/test_pipeline_determinism.py`, marker `@pytest.mark.determinism`, workflow wiring.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md`
- Scope decision (A / B / C) with rationale
- Fixture model list (5 models)
- Seed set decision with rationale
- CI integration plan (file path, marker, workflow)

**Known Unknowns Updates:**

Update Unknown 6.2:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 10
- Date: today
- Findings: seed sample size, fixture selection, CI budget
- Evidence: statistical analysis, CI wall-clock estimates
- Decision: Option A/B/C chosen

**PREP_PLAN.md Updates:** Task 10 → ✅ COMPLETE.

**CHANGELOG.md Update:** Prepend `- **Prep Task 10 COMPLETE (YYYY-MM-DD):** ...` with scope + fixture + seed-set decisions. Verified Unknown 6.2.

**Quality Gate:** Skip unless `.py` touched.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 10: Design Byte-Stability Test Infrastructure (PR12)

CI-integrated determinism regression test design to catch
#1283-class bugs automatically.

## Key findings

- Test scope: Option [A / B / C] — [rationale]
- Fixture models: chenery + [4 others]
- Seed set: [fixed seeds / random with logging]
- CI wall-clock estimate: [Ns per-commit / Nm nightly]
- Integration: tests/integration/test_pipeline_determinism.py with
  @pytest.mark.determinism marker

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/DESIGN_DETERMINISM_TESTS.md
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknown 6.2 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 10 status → COMPLETE
- Updated CHANGELOG.md with Task 10 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 10: Design Byte-Stability Test Infrastructure (PR12)" --body "<paste>"` and wait for reviewer comments.

---

## Task 11 Prompt: Plan Sprint 25 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint25-task11` from `main`

**Priority:** Critical (3–4 hours)

**Objective:** Integrate the outputs of Tasks 1–10 into a day-by-day Sprint 25 schedule with 2 checkpoints and day-by-day execution prompts.

**Unknowns Verified:** 6.3 (integrates all unknowns from Tasks 2–10)

**Prerequisites:**
- `SPRINT_25/PREP_PLAN.md` §Task 11
- `SPRINT_25/KNOWN_UNKNOWNS.md` Unknown 6.3
- All prior Task 2–10 outputs (must all complete first):
  - `AUDIT_ALIAS_AD_CARRYFORWARD.md` (Task 2)
  - `INVESTIGATION_PARSER_NON_DETERMINISM.md` (Task 3)
  - `CATALOG_EMITTER_BACKLOG.md` (Task 4)
  - `ANALYSIS_RECOVERED_TRANSLATES.md` (Task 5)
  - `DESIGN_ALIAS_AD_ROLLOUT.md` (Task 6)
  - `DESIGN_SMALL_PRIORITIES.md` (Task 7)
  - `PROFILE_HARD_TIMEOUTS.md` (Task 8)
  - `BASELINE_METRICS.md` (Task 9)
  - `DESIGN_DETERMINISM_TESTS.md` (Task 10)
- `SPRINT_24/PLAN.md` and `SPRINT_24/prompts/PLAN_PROMPTS.md` — templates

**Tasks to Complete:**

1. **Draft `docs/planning/EPIC_4/SPRINT_25/PLAN.md`** covering Days 0–14:
   - Day 0: prep-task review, kickoff, baseline snapshot
   - Days 1–12: Priority 1 alias-AD (per Task 6 rollout) + parallel Priority 2 emitter work (per Task 4 catalog)
   - Day 5: Checkpoint 1 (quantitative GO / CONDITIONAL / NO-GO criteria)
   - Day 10: Checkpoint 2
   - Day 13: final pipeline retest
   - Day 14: sprint close + retrospective
2. **Write day-by-day execution prompts** at `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` (mirror Sprint 24 format).
3. **Define checkpoint evaluation criteria** with quantitative pass/fail.
4. **Allocate parallel work:** map Priority 2 emitter batches to specific days.
5. **Calibrate Unknown 6.3:** review Sprint 23/24 alias-AD impact data; decide whether 80–100% translate-recovery influx assumption (PR13) applies to alias-AD recoveries or if a different budget (30–50%) applies.
6. **Update `SPRINT_25/PREP_PLAN.md` summary section** with all prep tasks marked COMPLETE.

**Deliverables:**
- `docs/planning/EPIC_4/SPRINT_25/PLAN.md` — 15-day schedule
- `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` — day-by-day prompts
- 2 checkpoint criteria
- Parallel-work allocation for Priority 2
- Updated PREP_PLAN.md with all tasks COMPLETE

**Known Unknowns Updates:**

Update Unknown 6.3:
- Status: ✅ VERIFIED or ❌ WRONG
- Verified by: Task 11
- Date: today
- Findings: alias-AD influx rate from S23/S24 data
- Evidence: historical metric references
- Decision: Match target tolerance + influx budget

**PREP_PLAN.md Updates:** Task 11 → ✅ COMPLETE. Final summary section updated.

**CHANGELOG.md Update:** Prepend `- **Prep Task 11 COMPLETE (YYYY-MM-DD):** ...` with sprint-schedule summary, checkpoint criteria, calibrated influx budget. Verified Unknown 6.3. All 11 prep tasks complete; Sprint 25 ready to start.

**Quality Gate:** Skip unless `.py` touched.

**Commit Message Format:**

```
Complete Sprint 25 Prep Task 11: Plan Sprint 25 Detailed Schedule

Final prep task — integrates Tasks 1-10 outputs into the 15-day
Sprint 25 execution schedule with 2 checkpoints.

## Key findings

- Day 0: kickoff + baseline verification
- Days 1–12: Priority 1 alias-AD (4 phases per Task 6 rollout)
- Days 3–8 parallel: Priority 2 emitter backlog (3 batches per Task 4)
- Day 5 Checkpoint 1: [GO criteria]
- Day 10 Checkpoint 2: [GO criteria]
- Day 13: final pipeline retest
- Day 14: sprint close
- Unknown 6.3 (alias-AD influx budget): [calibrated value] — [rationale]

## Deliverables

- docs/planning/EPIC_4/SPRINT_25/PLAN.md (15-day schedule)
- docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md (day-by-day prompts)
- Updated SPRINT_25/KNOWN_UNKNOWNS.md: Unknown 6.3 verified
- Updated SPRINT_25/PREP_PLAN.md: Task 11 status → COMPLETE; all 11 tasks complete
- Updated CHANGELOG.md with Task 11 completion entry
```

**Pull Request:** `gh pr create --title "Complete Sprint 25 Prep Task 11: Plan Sprint 25 Detailed Schedule" --body "<paste>"` and wait for reviewer comments. Note Sprint 25 is ready to kick off after this PR merges.

---

## General Instructions (Apply to All Tasks)

### Standard Workflow

1. **Create branch** from `main`: `git checkout main && git pull && git checkout -b planning/sprint25-task<N>`.
2. **Read prerequisites** listed at the top of the task's prompt.
3. **Execute "Tasks to Complete"** and produce the listed "Deliverables".
4. **Update KNOWN_UNKNOWNS.md** — replace 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG with correction) for each assigned unknown, adding Findings / Evidence / Decision.
5. **Update PREP_PLAN.md** — mark the task's Status → ✅ COMPLETE; fill Changes / Result; check off every Acceptance Criterion (`- [ ]` → `- [x]`).
6. **Update CHANGELOG.md** — prepend a Sprint 25 Preparation bullet under `[Unreleased]`.
7. **Run quality gate if any `.py` file changed:** `make typecheck && make lint && make format && make test`. All four must succeed.
8. **Commit** with the commit message format specified in the prompt.
9. **Push** the branch: `git push -u origin planning/sprint25-task<N>`.
10. **Open PR** via `gh pr create` with the specified title + body.
11. **Wait for reviewer comments.** Do not proceed to the next task until this PR is merged.

### Determining "Unknown VERIFIED" vs "WRONG"

- ✅ **VERIFIED** means the assumption stated in the Unknown section was confirmed by the research. Cite specific evidence (file paths, output, test results).
- ❌ **WRONG** means the assumption was contradicted. Document the correct finding and explain the impact on sprint planning. Revise Task 11's schedule if the correction affects effort estimates.

### Verification Section Template

When updating a Verification Results subsection in KNOWN_UNKNOWNS.md:

```markdown
### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task <N> (<Task Name>)
**Date:** YYYY-MM-DD

**Findings:**
- [Finding 1]
- [Finding 2]

**Evidence:**
- [Specific file/line/issue reference]
- [Specific output or test result]

**Decision:**
- [What this means for Sprint 25 plan]
```

### Commit Message Conventions

- Every task's commit message starts with `Complete Sprint 25 Prep Task <N>: <Task Name>`.
- Body includes a `## Key findings` section with bulleted outcomes.
- Body includes a `## Deliverables` section listing every updated file.
- No `Co-Authored-By` lines.
- No "Generated with Claude Code" attribution in commit body OR PR description.

### Quality Gate Pass Criteria

Run these in order and proceed only if all succeed:

```bash
make typecheck    # mypy on src/
make lint         # ruff check src/ tests/
make format       # black check src/ tests/
make test         # full fast suite, pytest -n auto -m "not slow"
```

If the task is docs-only (no `.py` changes), skip the quality gate but note this in the PR description.

### Pull Request Body Template

```markdown
## Summary

[1-3 sentences describing what this PR does and which Sprint 25 prep task it completes]

## Key findings

[Bulleted list from the commit message body]

## Deliverables

- [New file path 1]
- [New file path 2]
- Updated `SPRINT_25/KNOWN_UNKNOWNS.md`: Unknowns X.Y, X.Z verified
- Updated `SPRINT_25/PREP_PLAN.md`: Task <N> status → COMPLETE
- Updated `CHANGELOG.md` with Task <N> completion entry

## Test plan

- [x] [Quality-gate applicability: run all 4 OR docs-only skip]
- [x] Unknowns X.Y, X.Z verified in KNOWN_UNKNOWNS.md
- [x] Task <N> Acceptance Criteria all checked in PREP_PLAN.md
- [x] [Task-specific verification bullets — e.g., "All 11 issues classified by Pattern"]
```

### After PR Merges

When the user confirms the PR has merged:

1. `git checkout main && git pull` to sync local main.
2. Verify the merged commit is in main: `git log --oneline -3`.
3. Ready to pick up the next task prompt.

---

**Document Created:** 2026-04-19
**Prompts Covered:** Task 2 through Task 11 (10 prompts)
**Dependency Ordering:**
- Kickoff-parallel (no deps beyond Task 1): Tasks 2, 3, 4, 7, 8, 9
- Depends on Task 4: Task 5
- Depends on Task 3: Task 10
- Depends on Task 2: Task 6
- Depends on all: Task 11 (final)
