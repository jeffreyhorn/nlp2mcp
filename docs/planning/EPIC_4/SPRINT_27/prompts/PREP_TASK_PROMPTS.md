# Sprint 27 Prep Task Execution Prompts

Self-contained prompts for Sprint 27 Prep Tasks 2–11. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch, does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 27 Known Unknowns List) is already complete — no prompt needed.

Tasks 2–11 are dispatchable in the following order per the dependency graph in `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md`:

- **Parallel kickoff (no dependencies beyond Task 1):** Tasks 2, 3, 6, 9, 10
- **After Task 2:** Tasks 7, 8 (need Phase 0 sections authored before fix-surface analysis)
- **After Task 3:** Task 4 (anchor audit cross-references baseline)
- **After Task 4:** Task 5 (PR19 widening depends on anchor mapping)
- **After all (final integration):** Task 11

---

## Task 2 Prompt: Author Missing Phase 0 Acceptance Gates (PR20)

**Branch:** Create a new branch named `planning/sprint27-task2` from `main`

**Priority:** Critical (4–6 hours) — **THE central new prep activity for Sprint 27**

**Objective:** Author missing Phase 0 acceptance-gate sections on four `docs/issues/ISSUE_*.md` carryforward documents (#1356 fawley, #1357 otpop, #1387 cclinpts, #1388 camshape) — each must include hand-derived KKT shape for the target equation(s) + verification methodology against regenerated `*_mcp.gms`. Additionally codify the Phase 0 methodology in CONTRIBUTING.md as a hard rule for any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/`. This is the codified instance of Sprint 26 retrospective process recommendation **PR20**.

**Unknowns Verified:** 7.1, 7.2, 9.1

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 7.1, §Unknown 7.2, §Unknown 9.1
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" PR20 codification rationale
- Existing Phase 0 reference content (Note: no issue doc currently has a formal `## Phase 0: Acceptance Gate` section header — that's literally what this task establishes as a template. The following 4 issue docs mention Phase 0 in their content for guidance on what to include in each subsection). Locate the reference passages via grep — line numbers will drift as the docs evolve:
  - `docs/issues/ISSUE_1390_kand-tree-predicate-aliased-sum-architecture-redesign.md` — most comprehensive; has the stable section heading `## Investigation pointers (Phase 0 / Sprint 27 prep work)` (find via `grep -n "Investigation pointers (Phase 0" docs/issues/ISSUE_1390_*.md`) plus additional Phase 0 mentions (find via `grep -n "Phase 0" docs/issues/ISSUE_1390_*.md`).
  - `docs/issues/ISSUE_1393_ad-scalar-eq-sum-collapse-symbolic-superset.md` — Phase 0 mentioned inline within the design discussion (find via `grep -n "Phase 0" docs/issues/ISSUE_1393_*.md`).
  - `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` — Phase 0 mentioned inline (find via `grep -n "Phase 0" docs/issues/ISSUE_1385_*.md`).
  - `docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md` — Phase 0 mentioned in the Estimated effort paragraph (find via `grep -n "Phase 0" docs/issues/ISSUE_1335_*.md`).

  After Task 2 lands, these 4 issues should also be updated with formal `## Phase 0: Acceptance Gate` sections in a follow-on (Sprint 27 Day 0).
- The 4 target issue documents (current state):
  - `docs/issues/ISSUE_1356_*.md` (fawley comp_up — no formal Phase 0)
  - `docs/issues/ISSUE_1357_*.md` (otpop comp_up — no formal Phase 0)
  - `docs/issues/ISSUE_1387_*.md` (cclinpts — investigation pointer, no formal Phase 0)
  - `docs/issues/ISSUE_1388_*.md` (camshape — investigation pointer, no formal Phase 0)

**Tasks to Complete:**

1. **For each of the 4 target issues, locate the existing `docs/issues/ISSUE_<N>_*.md` file(s)** and identify the target equation(s) requiring hand-derived KKT:
   - #1356/#1357: `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` shape — derive expected complementarity condition with subset/superset domain widening
   - #1387 cclinpts: identify which stationarity equation produces the ~70% rel_diff; hand-derive expected vs current emit
   - #1388 camshape: identify which equation(s) drive the Locally Infeasible outcome; hand-derive KKT and compare against current MCP emit
2. **Author Phase 0 sections** — each issue file gets a new `## Phase 0: Acceptance Gate` section with subsections:
   - **Hand-Derived KKT Shape** — formal Lagrangian + stationarity / primal-feasibility / complementarity equations for the target
   - **Expected Emit Pattern** — what `*_mcp.gms` should contain, by equation name + index pattern
   - **Verification Methodology** — explicit byte-comparison or pattern-match command(s) to run against regenerated `<model>_mcp.gms`
   - **PROCEED/REPLAN Signal** — binary criteria for whether Phase 1 src/ work can begin
3. **Codify Phase 0 methodology in CONTRIBUTING.md** — add new §"Phase 0 Acceptance Gates" section that:
   - States the hard rule: any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` MUST have a Phase 0 section in its `docs/issues/ISSUE_*.md` file before any src/ commit
   - References the canonical template (the 4 subsections from step 2)
   - Lists the 2 incident citations (Sprint 26 PR #1379 and PR #1394) for rationale
   - Defines the exception scope: scripts/ + docs/ + tests/ + CI changes do NOT require Phase 0
   - Links to the Sprint 26 retrospective for full context

**Deliverables:**

- Phase 0 acceptance-gate section authored in `docs/issues/ISSUE_1356_*.md`
- Phase 0 acceptance-gate section authored in `docs/issues/ISSUE_1357_*.md`
- Phase 0 acceptance-gate section authored in `docs/issues/ISSUE_1387_*.md`
- Phase 0 acceptance-gate section authored in `docs/issues/ISSUE_1388_*.md`
- New §"Phase 0 Acceptance Gates" section in `CONTRIBUTING.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 9.1
- CHANGELOG.md updated with Task 2 completion entry

**Known Unknowns Updates:**

For each of Unknowns 7.1, 7.2, 9.1 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 2 (Author Missing Phase 0 Acceptance Gates PR20)
- Date: today's date (YYYY-MM-DD)
- Findings: per-issue Phase 0 derivation results + CONTRIBUTING.md exception-scope decision
- Evidence: links to authored Phase 0 sections + grep results showing methodology adoption
- Decision: PROCEED criteria for each issue; whether Priority 5 / 7 implementation may begin

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 2:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section with a summary of what was done
- Fill in the "Result" section with the per-issue PROCEED/REPLAN outcomes + CONTRIBUTING.md addition
- Check off all items in "Acceptance Criteria" (change `- [ ]` → `- [x]`)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Authored Phase 0 acceptance-gate sections on 4 carryforward issues (#1356 fawley comp_up, #1357 otpop comp_up, #1387 cclinpts condition-guard/sign, #1388 camshape Locally Infeasible) per PR20 codification. Each Phase 0 section includes Hand-Derived KKT Shape + Expected Emit Pattern + Verification Methodology + PROCEED/REPLAN Signal. Codified Phase 0 methodology in CONTRIBUTING.md as hard rule for any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` (with scripts/ + tests/ + docs/ + CI exception). Per-issue PROCEED status: <#1356 result>, <#1357 result>, <#1387 result>, <#1388 result>. Verified Unknowns 7.1, 7.2, 9.1.
```

**Quality Gate:**

Task 2 is research/docs only — no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 2: Author Missing Phase 0 Acceptance Gates (PR20)

Codifies Sprint 26 retrospective PR20 — Phase 0 acceptance-gate hard
rule + 4 carryforward issues' Phase 0 sections authored to enable
Sprint 27 Priorities 5 + 7 src/ implementation start.

## Phase 0 sections authored

- #1356 fawley comp_up — PROCEED criteria: <one-line>
- #1357 otpop comp_up + $171 — PROCEED criteria: <one-line>
- #1387 cclinpts ~70% rel_diff — PROCEED criteria: <one-line>
- #1388 camshape Locally Infeasible — PROCEED criteria: <one-line>

## CONTRIBUTING.md codification

- New §"Phase 0 Acceptance Gates" section with hard rule
- Scope: src/ad/, src/kkt/, src/emit/ Phase 1 changes
- Exceptions: scripts/, tests/, docs/, CI changes
- 2 incident citations: Sprint 26 PR #1379 + PR #1394

## Deliverables

- Updated docs/issues/ISSUE_{1356,1357,1387,1388}_*.md with Phase 0 sections
- Updated CONTRIBUTING.md with §"Phase 0 Acceptance Gates"
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknowns 7.1, 7.2, 9.1 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 2 status → COMPLETE
- Updated CHANGELOG.md with Task 2 completion entry
```

**Pull Request:**

After committing, push the branch and open a PR:

```bash
git push -u origin planning/sprint27-task2
gh pr create --title "Complete Sprint 27 Prep Task 2: Author Missing Phase 0 Acceptance Gates (PR20)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] All 4 ISSUE_*.md files contain `## Phase 0: Acceptance Gate` section with 4 required subsections
- [x] CONTRIBUTING.md §"Phase 0 Acceptance Gates" exists with hard rule + exception scope + Sprint 26 incident citations
- [x] Unknowns 7.1, 7.2, 9.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Sprint 26 → Sprint 27 Bucket-Provenance Baseline + Scope Freeze (PR15 + PR17)

**Branch:** Create a new branch named `planning/sprint27-task3` from `main`

**Priority:** Critical (4–5 hours)

**Objective:** Run a full pipeline retest at Sprint 27 Day 0 (`scripts/gamslib/run_full_test.py`), produce `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` documenting the per-bucket baseline + per-failing-model bucket provenance with Sprint 26 final → Sprint 27 Day 0 bucket transitions. Freeze the in-scope model set at 142 (matching Sprint 26 Day 14 final per the Sprint 26 abel reclassification). Reaffirms Sprint 26 retrospective process recommendations **PR15** (scope freeze) and **PR17** (bucket-provenance baseline) for Sprint 27.

**Unknowns Verified:** 1.1

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 3
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.1
- `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` (Sprint 26 baseline pattern with §5 scope-freeze + §6 bucket-provenance)
- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 + §5.1 (abel reclassification + scope-freeze policy)
- Current state: `data/gamslib/gamslib_status.json` (Sprint 26 Day 14 final — Match 59, Solve 103, path_syntax_error 17)
- Sprint 27 PROJECT_PLAN.md §Sprint 27 (target metrics)

**Tasks to Complete:**

1. **Run full pipeline retest** — `.venv/bin/python scripts/gamslib/run_full_test.py` (full pipeline; runtime varies with machine load: Sprint 26 Day 0 took ~3h33m / 12779s, Sprint 26 Day 13 retest took ~1h26m / 5165.8s on a faster runner — budget ~1–3.5h). Capture stdout/stderr.
2. **Diff updated `gamslib_status.json` against Sprint 26 Day 14 commit** — `git diff data/gamslib/gamslib_status.json` to surface bucket transitions; investigate any unexpected drift before freezing baseline.
3. **Author `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md`** with the standard sections (modeled on `SPRINT_26/BASELINE_METRICS.md`):
   - §1: Sprint 27 Goals (from PROJECT_PLAN.md)
   - §2: Per-Bucket Baseline (Match, Solve, path_syntax_error, path_solve_terminated, model_infeasible, translate, parse counts)
   - §3: Tests Baseline
   - §4: Determinism Baseline (PYTHONHASHSEED guard reaffirmation)
   - §5: Scope Freeze (continue 142 in-scope per Sprint 25 abel policy)
   - §6: Per-Failing-Model Bucket Provenance (Sprint 26 final → Sprint 27 Day 0 transitions for the ~83 failing models)
   - §7: Sprint 27 Target Metrics (with delta-from-baseline columns)
4. **Per-failing-model bucket provenance** — for each model in a non-compare_match bucket: current Day 0 bucket + Sprint 26 final bucket + Sprint 26 Day 0 bucket (if shifted during Sprint 26) + triggering Sprint 26 fix (if applicable) + Sprint 27 priority that targets this model (if any).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` with §1–§7 sections
- Updated `data/gamslib/gamslib_status.json` from Day 0 retest (or confirmation no drift from Sprint 26 Day 14)
- Per-failing-model bucket-provenance entries for all ~83 failing models
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 1.1
- CHANGELOG.md updated with Task 3 completion entry

**Known Unknowns Updates:**

For Unknown 1.1 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 3 (Sprint 26 → Sprint 27 Bucket-Provenance Baseline + Scope Freeze)
- Date: today's date (YYYY-MM-DD)
- Findings: count of the 15 #1398-affected models present at non-compare_match buckets; any drift or self-recovery surfaced
- Evidence: BASELINE_METRICS.md §6 references; gamslib_status.json diff output
- Decision: Priority 1 scope confirmed at 15 models (or adjusted to N models with rationale)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 3:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section with a summary of what was done
- Fill in the "Result" section with Day 0 metrics + bucket-provenance summary + scope-freeze confirmation
- Check off all items in "Acceptance Criteria" (change `- [ ]` → `- [x]`)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Sprint 26 → Sprint 27 bucket-provenance baseline + scope freeze (PR15 + PR17 reaffirmation). Sprint 27 Day 0 baseline: Parse 142/142, Translate <N>/142, Solve <N>, Match <N>, path_syntax_error <N>, path_solve_terminated <N>, model_infeasible <N>. <Drift summary: any bucket transitions Sprint 26 Day 14 → Sprint 27 Day 0 + root-cause attribution>. Scope frozen at 142 in-scope (continues Sprint 25 abel runtime-filter policy). Validation document at `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md`. Verified Unknown 1.1.
```

**Quality Gate:**

Task 3 runs the pipeline (which exercises Python code) and updates `data/gamslib/gamslib_status.json` + the BASELINE_METRICS.md doc; no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For data/docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 3: Sprint 26 → Sprint 27 Bucket-Provenance Baseline + Scope Freeze (PR15 + PR17)

Reaffirms Sprint 26 retrospective PR15 (scope freeze) + PR17
(bucket-provenance baseline) for Sprint 27. Establishes the Day 0
reference point for all Sprint 27 progress metrics.

## Sprint 27 Day 0 Baseline

- Parse: 142/142 (100%)
- Translate: <N>/142
- Solve: <N>
- Match: <N>
- path_syntax_error: <N>
- path_solve_terminated: <N>
- model_infeasible: <N>
- Tests: <N>

## Scope Freeze

- 142 in-scope (continues Sprint 25 abel runtime-filter policy)

## Sprint 26 Day 14 → Sprint 27 Day 0 Drift

- <Summary of any bucket transitions + root-cause attribution>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md with §1–§7
- Updated data/gamslib/gamslib_status.json (Sprint 27 Day 0)
- Per-failing-model bucket-provenance for ~83 failing models
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknown 1.1 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 3 status → COMPLETE
- Updated CHANGELOG.md with Task 3 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task3
gh pr create --title "Complete Sprint 27 Prep Task 3: Bucket-Provenance Baseline + Scope Freeze (PR15 + PR17)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Pipeline retest completed (`scripts/gamslib/run_full_test.py` exit 0)
- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] BASELINE_METRICS.md contains all 7 sections (§1–§7)
- [x] Scope frozen at 142 (matches Sprint 26 Day 14)
- [x] Per-failing-model bucket-provenance entries present for ~83 failing models
- [x] Unknown 1.1 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: #1398 Widened-Scope Verification + Anchor Model Audit

**Branch:** Create a new branch named `planning/sprint27-task4` from `main`

**Priority:** High (2–3 hours)

**Objective:** Verify that all 15 models identified in the Sprint 26 Day 13 #1398 sweep are reflected in the Sprint 27 Day 0 baseline as path_syntax_error / wrong-but-compiling-emit / mismatch buckets. Confirm the 8 Phase 0 anchor models (launch, qdemo7, ferts, sambal, ganges, sroute, turkpow, dinam) each represent a distinct emit shape requiring separate hand-derived KKT verification.

**Unknowns Verified:** 1.1 (cross-reference with Task 3), 1.2, 4.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 4
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.1, §Unknown 1.2, §Unknown 4.2
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` (Task 3 output — must complete first)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 27 §"Priority 1: Phase A Gate Predicate Tightening (#1398)" anchor-model list
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 13 entry (#1398 sweep notes)
- The 15 #1398-affected models: qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow

**Tasks to Complete:**

1. **Cross-reference 15 #1398-affected models against Sprint 27 Day 0 baseline (from Task 3)** — confirm each is in a non-compare_match bucket; flag any that have self-recovered or shifted bucket.
2. **For each non-anchor model (egypt, shale, qsambal, harker, tfordy, gangesx, srpchase), identify the presumed-matching anchor:** Inspect regenerated `data/gamslib/mcp/<model>_mcp.gms` for the stationarity equation pattern; compare against the 8 anchors' patterns; document presumed match.
3. **Sanity-check the 8 anchor models' shape distinctness** — inspect regenerated `<model>_mcp.gms` for each anchor; document distinguishing emit pattern (which stationarity equation, what cross-term structure, what alias-conditional pattern). If 2 anchors look similar, flag for Day 1/2 hand-derived KKT escalation.
4. **Author `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md`** with:
   - Per-anchor section documenting distinguishing emit pattern + non-anchor models that map to it
   - Per-non-anchor justification for anchor-model assignment
   - "Open questions" subsection for any ambiguous mappings (escalates to Day 1 hand-derived KKT)
   - Any model from the original 15 that has self-recovered or shifted bucket flagged with scope-impact note

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` with per-anchor sections + per-non-anchor justifications
- Confirmation that all 15 models present in Sprint 27 Day 0 baseline at non-compare_match buckets
- "Open questions" subsection for any ambiguous mappings
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1 (cross-reference), 1.2, 4.2
- CHANGELOG.md updated with Task 4 completion entry

**Known Unknowns Updates:**

For Unknowns 1.1 (cross-reference), 1.2, 4.2 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 4 (#1398 Widened-Scope Verification + Anchor Model Audit)
- Date: today's date (YYYY-MM-DD)
- Findings: distinct-shape count (target: 8); any anchor collapse or 9th-shape discovery; launch byte-stability impact from any Priority 4 fix
- Evidence: PRIORITY_1_ANCHOR_MAPPING.md per-anchor + per-non-anchor entries; emit-pattern grep results
- Decision: Priority 1 anchor set confirmed at 8 (or adjusted to N); launch byte-stability anchor confirmed (or shifted)

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 4:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with anchor-distinctness verdict + non-anchor mapping summary
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 4 COMPLETE (YYYY-MM-DD):** #1398 widened-scope verification + anchor model audit. Confirmed <N>/15 #1398-affected models present at non-compare_match buckets in Sprint 27 Day 0 baseline. Anchor distinctness: <N>/8 confirmed distinct shapes (<list any collapses>); <N> non-anchor models mapped to anchors (<list>). <Any ambiguous mappings escalated to Day 1/2 hand-derived KKT>. Verified Unknowns 1.1 (cross-reference), 1.2, 4.2. Validation document at `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md`.
```

**Quality Gate:**

Task 4 is research/docs only — no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 4: #1398 Widened-Scope Verification + Anchor Model Audit

Verifies Sprint 27 Priority 1 (#1398 Phase A gate tightening) scope:
all 15 affected models present at non-compare_match buckets in Day 0
baseline, 8 anchor models cover N distinct emit shapes.

## Anchor Distinctness Verdict

- 8/8 anchors confirmed distinct shapes (or N/8 with M collapse(s))
- launch byte-stability anchor preserved (or shifted to <new anchor>)
- 7/7 non-anchor models mapped: egypt → <anchor>, shale → <anchor>,
  qsambal → <anchor>, harker → <anchor>, tfordy → <anchor>,
  gangesx → <anchor>, srpchase → <anchor>

## Sprint 27 Day 0 Scope Confirmation

- 15/15 #1398-affected models present in baseline (or N with M
  self-recoveries flagged)
- Open questions: <any ambiguous mappings>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknowns 1.1 (xref), 1.2, 4.2 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 4 status → COMPLETE
- Updated CHANGELOG.md with Task 4 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task4
gh pr create --title "Complete Sprint 27 Prep Task 4: #1398 Widened-Scope Verification + Anchor Model Audit" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] PRIORITY_1_ANCHOR_MAPPING.md exists; all 15 #1398-affected models referenced
- [x] All 8 anchor models have dedicated sections with distinguishing emit patterns
- [x] All 7 non-anchor models assigned to anchors with justification
- [x] Unknowns 1.1 (xref), 1.2, 4.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: PR19 Target-List Widening Design

**Branch:** Create a new branch named `planning/sprint27-task5` from `main`

**Priority:** High (2–3 hours) — **prevents Sprint 26's #1398 gate-overreach incident from recurring**

**Objective:** Plan the PR19 CI target-list widening to cover all 15 #1398-affected models + launch, with quantified CI runtime impact estimate and integration plan with the existing `.github/path-solve-ci-targets.txt` infrastructure landed in Sprint 26 PR #1396.

**Unknowns Verified:** 1.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 5
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.4
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` (Task 4 output — must complete first)
- `.github/path-solve-ci-targets.txt` (current PR19 target list — from Sprint 26 PR #1396)
- `.github/workflows/pr19-emit-solve-validation.yml` (CI workflow)
- Sprint 26 PR #1396 CI logs (per-model PATH-solve runtime) — `gh run list -w "PR19 Pre-Merge Solve-Time Validation"` to discover
- Sprint 27 PROJECT_PLAN.md §"Priority 1" + §"PR19 target-list widening" rationale

**Tasks to Complete:**

1. **Inventory current PR19 target list** — read `.github/path-solve-ci-targets.txt`; document current models + per-model PATH-solve runtime (from CI logs). Note that the current list (15 models: 11 Tier 0/1 canaries hard-fail + 4 Pattern C target models soft-fail) already includes `fawley` (Pattern C tier), which is one of the 15 #1398-affected models — so the candidate cohort of 16 (15 #1398-affected + launch) overlaps the current list by 1 model.
2. **Calculate CI runtime impact of widening:** Compute net additions = 16 candidates − 1 (`fawley` already present) = 15 net new models. Final widened union = current 15 + 15 net new = 30 unique models. Project runtime = 30 models × avg per-model time (or refine using per-model medians from CI logs). Threshold check against GitHub Actions per-job runtime limit.
3. **Design widening strategy — evaluate 3 options:**
   - **Option A (full widening):** Add 15 net new models (the 16-candidate cohort minus `fawley` already present) — final union 30 unique models, max coverage, max runtime cost
   - **Option B (anchor-only widening):** Add only the 8 Phase 0 anchor models (none currently in PR19 list — 8 net new); final union 23 unique models; partial coverage (7 non-anchor #1398-affected models still uncovered), lower runtime cost
   - **Option C (tiered widening):** Same final union as Option A (30 unique) but split into 2 parallel CI jobs — full coverage, runtime cost amortized
   - Recommend one option with explicit reasoning (Option A or C preferred per KU-37 mitigation rationale)
4. **Author `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md`** with:
   - Current state inventory
   - Runtime impact calculation
   - 3 options + recommendation
   - Implementation steps (file edits, CI workflow changes if any)
   - Validation plan (dummy PR to confirm CI behavior)

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` with state inventory + runtime calc + 3 options + recommendation + implementation steps
- Explicit recommendation among Options A/B/C
- Estimated CI runtime delta for the recommended option
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 1.4
- CHANGELOG.md updated with Task 5 completion entry

**Known Unknowns Updates:**

For Unknown 1.4 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 5 (PR19 Target-List Widening Design)
- Date: today's date (YYYY-MM-DD)
- Findings: projected total CI runtime under each option; selected option; whether 5 min threshold exceeded
- Evidence: CI log timing data; runtime projection math in PR19_WIDENING_DESIGN.md
- Decision: Option A / B / C selected with rationale

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 5:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with selected option + estimated runtime delta
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 5 COMPLETE (YYYY-MM-DD):** PR19 target-list widening design. Current PR19 list: 15 models (11 Tier 0/1 hard-fail + 4 Pattern C soft-fail including `fawley`), baseline runtime <T min>. 16-candidate widening cohort (15 #1398-affected + launch) overlaps current list by 1 (`fawley`), so net additions = 15; final widened union = 30 unique models. Selected Option <A/B/C> (<one-line rationale>). Projected CI runtime: <T' min> (<delta>). Implementation lands in Sprint 27 Day 0 (per Task 11 schedule). Validation document at `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md`. Verified Unknown 1.4.
```

**Quality Gate:**

Task 5 is design/docs only — no Python source code or CI workflow YAML is expected to change (implementation lands at Sprint 27 Day 0). Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 5: PR19 Target-List Widening Design

Designs Sprint 27 Day 0 widening of PR19 CI target list to cover
all 15 #1398-affected models + launch — the structural mitigation
against Sprint 26's PR #1379 gate-overreach incident (KU-37).

## Recommendation: Option <A/B/C>

- Coverage: <N>/16 candidate models (15 net new — `fawley` already
  present); final widened union <30 / 23> unique models
- Projected CI runtime: <T> min (current: <T0>, delta <ΔT>)
- Implementation steps: edit `.github/path-solve-ci-targets.txt`
  with <15 / 8> net new entries; <any workflow YAML changes>

## Runtime Projection

- Current per-model PATH-solve median: <Ts>
- Current PR19 list: 15 models (11 Tier 0/1 + 4 Pattern C inc. fawley)
- Net additions after deduping fawley: 15 (Option A/C) or 8 (Option B)
- Final widened union: 30 (Option A/C) or 23 (Option B) unique models
- Projected total: <final-union> × <Ts> = <Tw>
- Per-job budget: <Tw> vs GitHub Actions limit <budget>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknown 1.4 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 5 status → COMPLETE
- Updated CHANGELOG.md with Task 5 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task5
gh pr create --title "Complete Sprint 27 Prep Task 5: PR19 Target-List Widening Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] PR19_WIDENING_DESIGN.md exists with all 4 required sections
- [x] All 16 candidate model names appear in document (15 #1398-affected + launch; `fawley` overlap with current PR19 list called out)
- [x] Runtime calc documents net additions (15 after deduping `fawley`) and final widened union (30 unique for Options A/C, 23 for Option B)
- [x] Recommended option includes estimated CI runtime delta
- [x] Implementation steps include exact `.github/path-solve-ci-targets.txt` edits (only the 15 net new entries, not `fawley`)
- [x] Unknown 1.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: AD Architectural Redesigns Risk Assessment (PR16 Application)

**Branch:** Create a new branch named `planning/sprint27-task6` from `main`

**Priority:** High (4–6 hours) — **the hypothesis-validation safeguard for the 30–48h Priority 3 budget**

**Objective:** Apply the Sprint 25 Day 5 hypothesis-validation methodology (codified as Sprint 25 retrospective PR16) to each of the three Sprint 27 Priority 3 AD architectural redesigns — #1390 (kand per-instance enumeration), #1385 (Option 1 short-circuit), #1393 + #1335 (scalar-eq Sum-collapse) — BEFORE committing the 30-48h Priority 3 budget. For each redesign, identify the central architectural hypothesis, sketch a minimal validation experiment (~30-90 min each), and produce a PROCEED / REPLAN signal.

**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4, 3.5

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 6
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Category 3 (Unknowns 3.1–3.5)
- `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` (Day 5 methodology canonical reference)
- `docs/issues/ISSUE_1390_*.md` (kand per-instance enumeration)
- `docs/issues/ISSUE_1385_*.md` (Option 1 short-circuit)
- `docs/issues/ISSUE_1393_*.md` + `docs/issues/ISSUE_1335_*.md` (scalar-eq Sum-collapse + 3 competing approaches)
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 9 entry (3-approach enumeration for #1335)
- Source code: `src/ad/constraint_jacobian.py:903,1027`; `src/ad/derivative_rules.py:2556,2607`; `_build_symbolic_instance_placeholder` in emit pipeline

**Tasks to Complete:**

1. **For each of the 3 Priority 3 redesigns, identify the central architectural hypothesis** (see PREP_PLAN.md §Task 6 step 1 for explicit hypothesis statements).
2. **For each hypothesis, run a ~30-90 min validation experiment:**
   - **#1390:** Patch `constraint_jacobian.py` with model-name-guarded predicate-guarded-Sum shim for kand; regenerate `kand_mcp.gms`; byte-compare cross-term against hand-derived KKT.
   - **#1385:** Pick alternative short-circuit shape; patch `_build_symbolic_instance_placeholder` for srpchase; regenerate `srpchase_mcp.gms` + compile-check + multiplier-reference resolution.
   - **#1393 + #1335:** Pick one of 3 documented approaches (recommend hybrid post-AD collapse); patch `_sum_should_collapse` for otpop; regenerate `otpop_mcp.gms`; check shape matches hand-derived KKT; if matches, run PATH-solve to check `pi ≈ 4217.80`.
3. **Evaluate coordinated design (KU-38):** for each pair of Priority 3 redesigns, assess shared design constraints. Document whether coordinated design is recommended.
4. **Author `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md`** with:
   - Per-redesign hypothesis statement
   - Per-redesign validation experiment design (~30-90 min each) + execution result
   - Per-redesign PROCEED / REPLAN criteria + verdict
   - Coordinated design analysis
   - Mark each experiment "executed in prep with result: PROCEED/REPLAN" or "scheduled for Day 0"
5. **If validation experiments require src/ changes:** keep them as prototypes (model-name guarded) — do NOT land them as fixes. Revert before committing.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` with per-redesign hypothesis + validation experiment + PROCEED/REPLAN verdict + coordinated design analysis
- Explicit selection of one of the 3 #1335 approaches (KU-39 resolution)
- Coordinated-design recommendation (KU-38 resolution)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4, 3.5
- CHANGELOG.md updated with Task 6 completion entry

**Known Unknowns Updates:**

For Unknowns 3.1, 3.2, 3.3, 3.4, 3.5 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction) — per sub-priority verdict
- Verified by: Task 6 (AD Architectural Redesigns Risk Assessment PR16)
- Date: today's date (YYYY-MM-DD)
- Findings: per-hypothesis PROCEED/REPLAN signal; #1335 approach selected (1 of 3); coordinated-design recommendation
- Evidence: experiment regeneration results; byte-comparison output; PATH-solve result on otpop
- Decision: which of #1390 / #1385 / #1393+#1335 may proceed in Sprint 27; whether Priority 3 budget needs reallocation

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 6:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with per-sub-priority PROCEED/REPLAN + #1335 approach selection + coordinated-design recommendation
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 6 COMPLETE (YYYY-MM-DD):** PR16 hypothesis validation for 3 Priority 3 AD architectural redesigns. **#1390 (kand):** <PROCEED/REPLAN> — <one-line evidence>. **#1385 (Option 1 short-circuit):** <PROCEED/REPLAN> — <one-line evidence>. **#1393 + #1335 (scalar-eq Sum-collapse):** <PROCEED/REPLAN>, approach <1/2/3> selected (KU-39 resolution) — <one-line evidence>. **Coordinated design (KU-38):** <serial/coordinated> recommended for <which pair(s)>. Validation document at `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md`. Verified Unknowns 3.1, 3.2, 3.3, 3.4, 3.5.
```

**Quality Gate:**

Task 6's validation experiments touch `src/` as throwaway prototypes (model-name-guarded). All `src/` changes MUST be reverted before committing the prep task — only docs are committed. **Preferred outcome:** zero `src/` diff in the commit; only docs. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless (whether or not `src/` changes remain):

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass.

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 6: AD Architectural Redesigns Risk Assessment (PR16 Application)

Applies Sprint 25 PR16 hypothesis-validation methodology to 3 Priority 3
AD architectural redesigns before committing the 30-48h Sprint 27
budget. Resolves KU-38 (coordinated-design) + KU-39 (#1335 approach
selection).

## Per-Sub-Priority Verdicts

- #1390 (kand per-instance enumeration): <PROCEED/REPLAN>
  - <one-line evidence>
- #1385 (Option 1 short-circuit): <PROCEED/REPLAN>
  - <one-line evidence>
- #1393 + #1335 (scalar-eq Sum-collapse): <PROCEED/REPLAN>
  - Approach <1/2/3> selected: <one-line rationale>
  - <one-line evidence>

## Coordinated Design Recommendation

- <serial/coordinated> for <which pair(s)>; <one-line rationale>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknowns 3.1–3.5 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 6 status → COMPLETE
- Updated CHANGELOG.md with Task 6 completion entry
- All experiment prototype patches reverted (zero `src/` diff)
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task6
gh pr create --title "Complete Sprint 27 Prep Task 6: AD Architectural Redesigns Risk Assessment (PR16)" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] All experiment prototype `src/` patches reverted before commit (zero `src/` diff confirmed)
- [x] PRIORITY_3_RISK_ASSESSMENT.md exists with hypothesis + experiment + PROCEED/REPLAN for #1390, #1385, #1393+#1335
- [x] #1335 approach selected (1 of 3) with rationale
- [x] Coordinated-design analysis covers each pair (#1390+#1385, #1385+#1393, #1390+#1393)
- [x] Unknowns 3.1–3.5 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: comp_up Subset/Superset Fix-Surface Analysis

**Branch:** Create a new branch named `planning/sprint27-task7` from `main`

**Priority:** High (3–4 hours)

**Objective:** Identify the exact `src/kkt/complementarity.py` + `src/emit/emit_gams.py` patch sites required for the comp_up subset/superset domain widening that fixes both #1356 (fawley) and #1357 (otpop). Confirm whether the fix is a single-file change or requires coordinated changes across both files. Confirm whether fawley and otpop are the only two affected models.

**Unknowns Verified:** 5.1, 5.2, 5.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 7
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 5.1, §Unknown 5.2, §Unknown 5.3
- `docs/issues/ISSUE_1356_*.md` (fawley) with new Phase 0 section (Task 2 output — must complete first)
- `docs/issues/ISSUE_1357_*.md` (otpop) with new Phase 0 section (Task 2 output — must complete first)
- `src/kkt/complementarity.py` (comp_up_X equation generation)
- `src/emit/emit_gams.py` (`.fx` substitution + domain-condition emission)
- Sprint 25 #1349 fix in `src/emit/emit_gams.py` (potentially-related code path)

**Tasks to Complete:**

1. **Read the Phase 0 sections** authored in Task 2 for #1356 and #1357 — note target equation shape + verification methodology.
2. **Identify source code producing current (incorrect) shape:**
   - In `src/kkt/complementarity.py`: locate function(s) generating `comp_up_x(tt)$(...)` equations
   - In `src/emit/emit_gams.py`: locate function(s) emitting `$(t(tt) and xb(tt) < inf)` domain condition + `piU_x.fx(tt)$(...)` initialization
3. **Diagnose the subset/superset domain mismatch:** Compare current emit against Phase 0 target shape; identify which part of domain condition needs widening; document proposed patch as unified diff sketch.
4. **Confirm fawley + otpop are the only affected models:** `grep -lE "comp_up_x\(.*\)\$\(.*<[[:space:]]*inf\)" data/gamslib/mcp/*_mcp.gms` for corpus sweep (note: `[[:space:]]*` instead of `\s*` — `\s` is not valid in POSIX ERE; use `grep -P` if you prefer PCRE `\s`); document any additional models found.
5. **Estimate implementation effort** vs Priority 5's 8-12h budget.
6. **Author `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md`** with: Phase 0 target shape cross-reference; source code patch site identification (file:line); unified diff sketch (~50-100 lines); affected-model corpus sweep results; implementation effort estimate; Day 1 readiness assessment.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` with target shape + patch sites + diff sketch + corpus sweep + effort estimate
- Confirmation of single-file or coordinated patch shape
- List of all models exhibiting the comp_up subset/superset shape
- Day 1 readiness assessment
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3
- CHANGELOG.md updated with Task 7 completion entry

**Known Unknowns Updates:**

For Unknowns 5.1, 5.2, 5.3 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 7 (comp_up Subset/Superset Fix-Surface Analysis)
- Date: today's date (YYYY-MM-DD)
- Findings: patch shape (single-file vs coordinated); affected-model count (target: 2); clearlak regression risk
- Evidence: file:line patch sites; corpus grep results; clearlak verification
- Decision: Priority 5 PROCEED with <single-file/coordinated> patch; <N> models in scope; <regression risk handling plan>

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 7:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with patch shape verdict + affected-model count + readiness
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 7 COMPLETE (YYYY-MM-DD):** comp_up subset/superset fix-surface analysis for Sprint 27 Priority 5 (#1356 fawley + #1357 otpop). Patch shape: <single-file `src/kkt/complementarity.py`-only / coordinated `complementarity.py` + `src/emit/emit_gams.py`>. Affected models corpus sweep: <2 (fawley + otpop) / N>. Implementation effort: <T h> within Priority 5's 8-12h budget. Clearlak (Sprint 25 #1349 canary) regression risk: <none / mitigated by N>. Validation document at `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md`. Verified Unknowns 5.1, 5.2, 5.3.
```

**Quality Gate:**

Task 7 is research/docs only — proposed patch shipped as a diff sketch in the design doc, NOT applied; no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 7: comp_up Subset/Superset Fix-Surface Analysis

Maps Sprint 27 Priority 5 (#1356 fawley + #1357 otpop) to specific
patch sites in src/kkt/complementarity.py + src/emit/emit_gams.py
ahead of Day 1 implementation.

## Fix-Surface Verdict

- Patch shape: <single-file/coordinated>
- Patch sites: <file:line list>
- Affected-model count: <N> (corpus sweep)
- Implementation effort estimate: <T h> (Priority 5 budget: 8-12h)

## Regression Risk Assessment

- Clearlak (#1349 canary): <none/mitigated>
- 11 Tier 0/1 canaries: <byte-stable/at-risk>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknowns 5.1, 5.2, 5.3 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 7 status → COMPLETE
- Updated CHANGELOG.md with Task 7 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task7
gh pr create --title "Complete Sprint 27 Prep Task 7: comp_up Subset/Superset Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] PRIORITY_5_FIX_SURFACE.md exists with all 6 required sections
- [x] Patch sites identified with `file:line` precision
- [x] Unified diff sketch covers all required changes
- [x] Affected-model sweep ran against `data/gamslib/mcp/*_mcp.gms` corpus
- [x] Implementation effort estimate fits within Priority 5's 8-12h budget (or REPLAN flagged)
- [x] Unknowns 5.1, 5.2, 5.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: #1387 cclinpts + #1388 camshape Fix-Surface Analysis

**Branch:** Create a new branch named `planning/sprint27-task8` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** For each of #1387 (cclinpts ~70% rel_diff) and #1388 (camshape Locally Infeasible), assess whether the Sprint 27 6-12h Priority 7 budget is sufficient for implementation, or whether formal Sprint 28 carryforward filing is warranted. Document the fix-surface analysis (or carryforward rationale) for each issue.

**Unknowns Verified:** 7.1, 7.2, 7.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 8
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 7.1, §Unknown 7.2, §Unknown 7.3
- `docs/issues/ISSUE_1387_*.md` (cclinpts) with new Phase 0 section (Task 2 output — must complete first)
- `docs/issues/ISSUE_1388_*.md` (camshape) with new Phase 0 section (Task 2 output — must complete first)
- `data/gamslib/mcp/cclinpts_mcp.gms` (current emit)
- `data/gamslib/mcp/camshape_mcp.gms` (current emit)
- Sprint 26 retrospective §"Sprint 27 Recommendations" §"Priority 7"

**Tasks to Complete:**

1. **For #1387 cclinpts:**
   - Read the Phase 0 section from Task 2 — note target stationarity equation shape
   - Compare current `cclinpts_mcp.gms` emit against the target
   - Identify the bug class: condition-guard, sign, or both
   - Locate source-code site(s) producing the bug (likely in `src/kkt/stationarity.py` or `src/ad/`)
   - Estimate fix-surface effort
   - Verdict: Sprint 27 fix OR Sprint 28 carryforward filing
2. **For #1388 camshape:**
   - Read the Phase 0 section from Task 2 — note target KKT shape
   - Compare current `camshape_mcp.gms` emit against the target
   - Determine whether Locally Infeasible is an emit bug (fixable) or fundamental model property (not fixable in Sprint 27)
   - If emit bug, locate source-code site(s)
   - Estimate fix-surface effort
   - Verdict: Sprint 27 fix OR Sprint 28 carryforward filing
3. **Author `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md`** with per-issue subsection: target shape cross-reference, current emit, bug class, source-code patch sites, effort estimate, verdict; Sprint 28 carryforward filing template (if deferred).
4. **If either issue is deferred:** File Sprint 28 carryforward in `docs/issues/ISSUE_<N>_*.md`; label GitHub issue with `sprint-28` (remove `sprint-27` label if applicable); document the carryforward.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` with per-issue analysis + verdict
- Per-issue fix-surface estimate
- If deferred: Sprint 28 carryforward filing for each deferred issue + GitHub label updates
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.1, 7.2, 7.3
- CHANGELOG.md updated with Task 8 completion entry

**Known Unknowns Updates:**

For Unknowns 7.1, 7.2, 7.3 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 8 (#1387 cclinpts + #1388 camshape Fix-Surface Analysis)
- Date: today's date (YYYY-MM-DD)
- Findings: #1387 bug class (condition-guard/sign/both); #1388 emit-bug vs fundamental-property; combined-budget fit
- Evidence: file:line patch sites; hand-derived KKT vs current emit comparisons
- Decision: per-issue Sprint 27 / Sprint 28 verdict + budget impact

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 8:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with per-issue verdict + combined-budget fit
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 8 COMPLETE (YYYY-MM-DD):** #1387 cclinpts + #1388 camshape fix-surface analysis. **#1387:** bug class <condition-guard / sign / both>, effort ~<T h>, verdict <Sprint 27 fix / Sprint 28 carryforward>. **#1388:** classification <emit bug / fundamental property>, effort ~<T h>, verdict <Sprint 27 fix / Sprint 28 carryforward>. Combined Priority 7 effort: <T1 + T2 h> vs 6-12h budget. <Any Sprint 28 carryforward filings>. Validation document at `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md`. Verified Unknowns 7.1, 7.2, 7.3.
```

**Quality Gate:**

Task 8 is research/docs only — no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 8: #1387 cclinpts + #1388 camshape Fix-Surface Analysis

Maps Sprint 27 Priority 7 (Day 6 close-and-refile carryforwards) to
specific patch sites or Sprint 28 carryforward filings ahead of
Day 1 implementation.

## Per-Issue Verdicts

- #1387 cclinpts: bug class <...>, effort ~<T h>, verdict <S27/S28>
- #1388 camshape: <emit bug/fundamental property>, effort ~<T h>,
  verdict <S27/S28>

## Combined-Budget Fit

- Total Sprint 27 effort: <T1 + T2 h>
- Priority 7 budget: 6-12h
- Fit: <within / exceeds>

## Sprint 28 Carryforward Filings (if any)

- <list of issues moved to sprint-28>

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknowns 7.1, 7.2, 7.3 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 8 status → COMPLETE
- Updated CHANGELOG.md with Task 8 completion entry
- <Optional: docs/issues/ISSUE_<N>_*.md carryforward filing>
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task8
gh pr create --title "Complete Sprint 27 Prep Task 8: #1387 cclinpts + #1388 camshape Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] PRIORITY_7_FIX_SURFACE.md exists with per-issue subsections for #1387 + #1388
- [x] Each issue has a documented verdict (Sprint 27 fix OR Sprint 28 carryforward)
- [x] If Sprint 27 fix verdict: source-code patch sites identified + effort estimate
- [x] If Sprint 28 carryforward verdict: GitHub issue labeled `sprint-28` + rationale documented
- [x] Combined Sprint 27 effort fits within Priority 7's 6-12h budget
- [x] Unknowns 7.1, 7.2, 7.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: PR22 Mid-Sprint Audit Script Design

**Branch:** Create a new branch named `planning/sprint27-task9` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Design and implement `scripts/sprint_audit/changed_emit_artifacts.py` that scans git history (via `git log --since <date>` or `git log <commit>..HEAD` — selected by CLI flag) for emit-affecting `data/gamslib/mcp/*.gms` changes (broad glob covering `*_mcp.gms` + `*_mcp_presolve.gms`) and auto-generates the PR14 review list + retest comparison surface. This is the codified instance of Sprint 26 retrospective process recommendation **PR22**.

**Unknowns Verified:** 9.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 9
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 9.3
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" §"PR22"
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 12 entry (PLAN_PROMPTS.md staleness incident)
- Existing pattern: `scripts/gamslib/run_full_test.py` for pipeline retest style
- Sprint 26 PR14 reaffirmation rule (CONTRIBUTING.md)

**Tasks to Complete:**

1. **Design the script interface:**
   - Command-line args: mutually exclusive `--since-date <date>` (passed to `git log --since <date>` — date-based; subject to same-day commit-boundary ambiguity) and `--since-commit <sha>` (implemented via `git log <sha>..HEAD` — commit-based, unambiguous). Exactly one must be specified.
   - Note: `git log --since` is date-based and does NOT accept commit SHAs, so a single overloaded `--since <date|commit>` would be misleading. Two distinct flags is the correct design.
   - Recommended `--since-commit` value for mid-sprint retests: the Sprint 27 Day 0 commit SHA (to be recorded in PLAN.md Day 0 entry by Task 11).
   - Output format: structured list (JSON or markdown table) of changed `data/gamslib/mcp/*.gms` files + triggering commits
   - Subcommands or flags for "PR14 review list" mode (per-PR scope) vs "mid-sprint retest" mode (since-sprint-start scope)
   - Handles cross-sprint timestamp ambiguity from KU Unknown 9.3 via `--since-commit` (commit boundaries are unambiguous)
2. **Implement the script** at `scripts/sprint_audit/changed_emit_artifacts.py`:
   - Use `subprocess.run(argv_list, ...)` to scan commits — argv elements are passed verbatim without shell parsing, so do NOT include shell-style quotes around `--pretty=format:` values or pathspecs. The argv form differs by mode:
     - For `--since-date`: `subprocess.run(['git', 'log', '--name-only', '--pretty=format:COMMIT:%H', '--since', date_str, '--', 'data/gamslib/mcp/*_mcp.gms', 'data/gamslib/mcp/*_mcp_presolve.gms'], ...)`
     - For `--since-commit`: same argv structure with `f'{sha}..HEAD'` replacing `'--since', date_str`
   - **IMPORTANT:** `--name-only` (or `--name-status`) is REQUIRED — without it, `git log` won't include changed file paths in output and the script can't build the commit-to-files mapping. The custom `--pretty=format:COMMIT:%H` (note: `%H` only, NO `%n%s` — including the subject line `%s` would emit a second non-path line per commit that the parser would incorrectly treat as a file path). If commit subjects are needed for display, fetch them in a separate `git log` pass keyed by SHA rather than mixing them with the `--name-only` output.
   - Validate the `--since-commit` SHA via `git rev-parse` before constructing the revision range
   - Parse output by walking lines: each `COMMIT:<sha>` line starts a new group; subsequent non-blank lines until the next `COMMIT:` are the changed file paths for that commit (already filtered by the `-- <pathspec>` to mcp artifacts)
   - Group changes by triggering commit
   - Output structured format suitable for mid-sprint retest reports
3. **Integration with PR14 review process** — document in CONTRIBUTING.md §"Emit-PR `.gms` Diff Workflow" (or similar) how to invoke the script.
4. **Test the script:**
   - Dry-run against Sprint 26 history; verify the output MUST INCLUDE AT LEAST the following artifacts (exact count varies because the script scans both `*_mcp.gms` and `*_mcp_presolve.gms` and which presolve variants were regenerated depends on Sprint 26 commit history): launch artifacts (`launch_mcp.gms` and/or `launch_mcp_presolve.gms` — Phase A target, regenerated Day 1 PR #1379; launch is the separate Phase A fix target, NOT one of the 15 #1398-affected) AND artifacts for all 15 #1398-affected models (Day 13 regenerated: qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow — each contributing `<model>_mcp.gms` and possibly `<model>_mcp_presolve.gms`). NOTE: #1400 is a `scripts/gamslib/*` path-relativization change (not an emit artifact) and will NOT appear in the script's output by design — do not expect to see it
   - Document expected output in `--help` or accompanying notes
5. **Author `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md`** with: design decisions (CLI, output format, integration); implementation summary (file:line locations); validation results (Sprint 26 dry-run output); CONTRIBUTING.md integration plan.

**Deliverables:**

- `scripts/sprint_audit/changed_emit_artifacts.py` (executable Python script)
- `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md` with design + implementation + validation
- CONTRIBUTING.md updated with §"Emit-PR `.gms` Diff Workflow" referencing the script
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 9.3
- CHANGELOG.md updated with Task 9 completion entry

**Known Unknowns Updates:**

For Unknown 9.3 in `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md`, update Verification Results:

- Status: ✅ VERIFIED (or ❌ WRONG with correction)
- Verified by: Task 9 (PR22 Mid-Sprint Audit Script Design)
- Date: today's date (YYYY-MM-DD)
- Findings: CLI implements two mutually exclusive flags `--since-date <date>` + `--since-commit <sha>` (resolving Unknown 9.3's two-flag design question); both dry-runs on Sprint 26 surface the #1398 Day 13 regenerated `*_mcp.gms` artifacts (15 affected models + presolve variants); cross-sprint timestamp ambiguity handled via `--since-commit`. NOTE: #1400 does NOT appear in the script output by design — it's a `scripts/gamslib/*` path-relativization change, not an emit artifact.
- Evidence: dry-run output; CLI design notes
- Decision: script ready for Sprint 27 mid-sprint use; CONTRIBUTING.md workflow integration complete

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 9:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with script implementation summary + dry-run validation
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 9 COMPLETE (YYYY-MM-DD):** PR22 mid-sprint audit script designed + implemented. New `scripts/sprint_audit/changed_emit_artifacts.py` scans git history for emit-affecting `data/gamslib/mcp/*.gms` changes (broad glob covers `*_mcp.gms` + `*_mcp_presolve.gms`) and auto-generates PR14 review list + retest comparison surface. CLI exposes two mutually exclusive flags: `--since-date <date>` (date-based; uses `git log --since`) and `--since-commit <sha>` (commit-based; uses `git log <sha>..HEAD`). The two-flag design resolves the cross-sprint timestamp ambiguity from Unknown 9.3 — `git log --since` is date-only and won't accept commit SHAs, so a single overloaded `--since` would be misleading. Sprint 26 history dry-runs (both modes) include AT LEAST the launch artifacts (`launch_mcp.gms` / `launch_mcp_presolve.gms` — Phase A target, Day 1; launch is the separate Phase A fix target, NOT one of the 15 #1398-affected) PLUS all 15 #1398-affected models' artifacts (Day 13 regenerated — exact count varies because the script scans both `*_mcp.gms` and `*_mcp_presolve.gms` and not every model regenerates both variants). #1400 (`scripts/gamslib/*` path-relativization) is intentionally NOT in scope for this script and does not appear in output. CONTRIBUTING.md updated with §"Emit-PR `.gms` Diff Workflow" referencing the script. Validation document at `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md`. Verified Unknown 9.3.
```

**Quality Gate:**

Task 9 creates new Python code (`scripts/sprint_audit/changed_emit_artifacts.py`). Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. If any check fails, fix the issue and re-run; do not bypass.

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 9: PR22 Mid-Sprint Audit Script Design

Codifies Sprint 26 retrospective PR22 — auto-generates PR14 review
list + mid-sprint retest comparison surface from git log instead of
frozen PLAN_PROMPTS.md (Sprint 26 Day 12 staleness incident).

## Script

- Path: scripts/sprint_audit/changed_emit_artifacts.py
- CLI: mutually exclusive `--since-date <date>` (uses `git log --since`)
  + `--since-commit <sha>` (uses `git log <sha>..HEAD`); subcommands or
  flags for PR14 vs retest modes
- Output: structured list of changed `data/gamslib/mcp/*.gms` files
  grouped by triggering commit
- Filter: `*_mcp.gms` + `*_mcp_presolve.gms` (broad glob)

## Validation

- Sprint 26 dry-runs (both `--since-date` and `--since-commit` modes):
  output must include AT LEAST (a) launch artifacts
  (`launch_mcp.gms` / `launch_mcp_presolve.gms` — Phase A target,
  Day 1; launch is the separate Phase A fix target, NOT one of the
  15 #1398-affected models) AND (b) artifacts for all 15
  #1398-affected models (Day 13 regenerated: qdemo7, egypt, ferts,
  shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx,
  fawley, srpchase, sroute, turkpow). Exact artifact count varies
  because the script scans both `*_mcp.gms` and `*_mcp_presolve.gms`
  and not every model regenerates both variants.
- #1400 (`scripts/gamslib/*` path-relativization) is intentionally
  out of scope for this script and does not appear in output
- Cross-sprint timestamp ambiguity: handled via `--since-commit` form
  (commit boundaries are unambiguous unlike `--since` date semantics)

## Quality Gate

- make typecheck: PASS
- make lint: PASS
- make format: PASS
- make test: PASS (<N> passed / <N> skipped)

## Deliverables

- New scripts/sprint_audit/changed_emit_artifacts.py (executable)
- New docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md
- Updated CONTRIBUTING.md: §"Emit-PR `.gms` Diff Workflow"
- Updated docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md: Unknown 9.3 verified
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 9 status → COMPLETE
- Updated CHANGELOG.md with Task 9 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task9
gh pr create --title "Complete Sprint 27 Prep Task 9: PR22 Mid-Sprint Audit Script Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] make typecheck PASS
- [x] make lint PASS
- [x] make format PASS
- [x] make test PASS
- [x] Script exists at `scripts/sprint_audit/changed_emit_artifacts.py` with executable bit
- [x] CLI accepts mutually exclusive `--since-date <date>` (uses `git log --since`) and `--since-commit <sha>` (uses `git log <sha>..HEAD`) arguments
- [x] Sprint 26 history dry-runs (both `--since-date` and `--since-commit`) include AT LEAST: launch artifacts (`launch_mcp.gms` / `launch_mcp_presolve.gms` — Phase A target, Day 1; launch is NOT one of the 15 #1398-affected models, it's a separate Phase A target) PLUS all 15 #1398-affected models' `*_mcp.gms` (Day 13). Exact count varies because the script scans both `*_mcp.gms` and `*_mcp_presolve.gms` and not every model regenerates both variants. #1400 (`scripts/gamslib/*` path-relativization) intentionally NOT in scope for this script
- [x] CONTRIBUTING.md updated with script invocation workflow
- [x] Unknown 9.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: PR23 CI-Workflow PR Self-Review Checklist Authoring

**Branch:** Create a new branch named `planning/sprint27-task10` from `main`

**Priority:** Medium (2–3 hours)

**Objective:** Author the CONTRIBUTING.md §"CI Workflow PR Checklist" content based on Sprint 26 PR #1396's 11-round Copilot review surface. This is the codified instance of Sprint 26 retrospective process recommendation **PR23**.

**Unknowns Verified:** (no specific unknown; design-only — checklist content derived from Sprint 26 PR #1396 review history)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 10
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" §"PR23"
- Sprint 26 PR #1396 review history: `gh api repos/jeffreyhorn/nlp2mcp/pulls/1396/comments` to pull 11 rounds of Copilot review comments
- Existing CONTRIBUTING.md (current structure + PR14 reaffirmation rule for reference)
- 7 recurring review categories from Sprint 26 retrospective: input validation, pagination, fork tolerance, schema validation, error handling, marker uniqueness, logging visibility

**Tasks to Complete:**

1. **Review Sprint 26 PR #1396 history** — pull the 11 rounds of Copilot review comments and categorize across the 7 recurring categories.
2. **For each of the 7 categories, draft 3-5 self-review checklist items:**
   - Input validation: env-var presence, path validation, value sanitization
   - Pagination: API response pagination, page-size limits
   - Fork tolerance: secrets unavailability, permission degradation
   - Schema validation: JSON/YAML input schema checks
   - Error handling: per-step failure handling, exit code propagation
   - Marker uniqueness: file names, IDs, cache keys across concurrent runs
   - Logging visibility: entry/exit/result logs, debug flag, secret redaction
3. **Author the CONTRIBUTING.md §"CI Workflow PR Checklist"** with: brief rationale (1 paragraph referencing PR #1396 incident); scope (`.github/workflows/*.yml` + `scripts/ci/*`); 7-category checklist with 3-5 items each (~25-35 items total); PR author runs checklist before requesting review.
4. **Author `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md`** with: Sprint 26 PR #1396 review-comment categorization (raw input); per-category item rationale; sample PR self-review (apply to hypothetical PR).

**Deliverables:**

- New §"CI Workflow PR Checklist" section in `CONTRIBUTING.md`
- `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` with categorization + rationale + sample
- All 7 categories covered with 3-5 checklist items each
- CHANGELOG.md updated with Task 10 completion entry

**Known Unknowns Updates:**

Task 10 has no specific unknown assigned (design-only — checklist derived from concrete PR #1396 review surface). No KNOWN_UNKNOWNS.md updates required for this task.

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 10:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with checklist item count + category coverage
- Check off all items in "Acceptance Criteria"

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 10 COMPLETE (YYYY-MM-DD):** PR23 CI-workflow PR self-review checklist authored. New CONTRIBUTING.md §"CI Workflow PR Checklist" with rationale + scope (`.github/workflows/*.yml` + `scripts/ci/*`) + 7-category checklist (<N items total>): input validation, pagination, fork tolerance, schema validation, error handling, marker uniqueness, logging visibility. Each category has 3-5 specific items drawn from Sprint 26 PR #1396's 11-round Copilot review. Design document at `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md`.
```

**Quality Gate:**

Task 10 is research/docs only — no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 10: PR23 CI-Workflow PR Self-Review Checklist Authoring

Codifies Sprint 26 retrospective PR23 — structured self-review
checklist to compress CI-workflow PR review iteration count (Sprint 26
PR #1396 required 11 rounds of Copilot review).

## CI Workflow PR Checklist (CONTRIBUTING.md)

- Scope: .github/workflows/*.yml + scripts/ci/*
- 7 categories, <N> items total:
  - Input validation: <K1> items
  - Pagination: <K2> items
  - Fork tolerance: <K3> items
  - Schema validation: <K4> items
  - Error handling: <K5> items
  - Marker uniqueness: <K6> items
  - Logging visibility: <K7> items

## Derived From

- Sprint 26 PR #1396 11-round Copilot review (categorized in design doc)

## Deliverables

- Updated CONTRIBUTING.md: new §"CI Workflow PR Checklist"
- New docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 10 status → COMPLETE
- Updated CHANGELOG.md with Task 10 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task10
gh pr create --title "Complete Sprint 27 Prep Task 10: PR23 CI-Workflow PR Self-Review Checklist" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] CONTRIBUTING.md §"CI Workflow PR Checklist" exists with rationale + scope + 7-category checklist
- [x] Each of 7 categories has 3-5 specific items
- [x] Total checklist contains ≥ 25 items
- [x] Scope clearly defines applicability (`.github/workflows/*.yml` + `scripts/ci/*`)
- [x] PR23_CHECKLIST_DESIGN.md contains Sprint 26 PR #1396 categorization
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 11 Prompt: Plan Sprint 27 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint27-task11` from `main`

**Priority:** Critical (3–4 hours) — **integrates Tasks 1-10 outputs into the 14-day execution plan**

**Objective:** Create the detailed 14-day Sprint 27 schedule (Day 0 setup + Days 1-13 execution) with day-by-day prompts. Budget each day at ≤ 12 hours per the PROJECT_PLAN.md Sprint 27 entry (168-hour total budget). Sequence priorities to respect dependencies (Phase 0 gates before src/ commits per PR20; PR19 widening before Priority 1 to prevent re-regression; Priority 6 #1224 can bundle with Priority 3 #1385).

**Unknowns Verified:** (integrates all)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 11
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 27 (canonical priorities + Acceptance Criteria + Estimated Effort)
- All Sprint 27 Tasks 2-10 deliverable docs:
  - `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` (Task 3)
  - `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` (Task 4)
  - `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` (Task 5)
  - `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` (Task 6)
  - `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` (Task 7)
  - `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` (Task 8)
  - `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md` (Task 9)
  - `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` (Task 10)
- `docs/planning/EPIC_4/SPRINT_26/PLAN.md` (Sprint 26 schedule reference pattern)
- `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` (Sprint 26 day-by-day prompts reference pattern)

**Tasks to Complete:**

1. **Synthesize all prep task outputs** — read Tasks 1-10 deliverables and integrate findings into the schedule.
2. **Author `docs/planning/EPIC_4/SPRINT_27/PLAN.md`** with:
   - Sprint 27 goal restatement (from PROJECT_PLAN.md)
   - Day-by-day schedule (Day 0 + Days 1-13)
   - Per-day: focus, hours budgeted (≤ 12), tasks, deliverables, success criteria
   - Checkpoint days (Day 5, Day 10) with pipeline retest + bucket-provenance update
   - Day 13: final retest + SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md authoring
3. **Author `docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md`** with:
   - Per-day execution prompt (suitable for direct invocation)
   - Each prompt references PROJECT_PLAN.md priority + prep-task outputs
   - Each prompt includes PR14 reaffirmation rule (regenerated `.gms` diff)
   - Each prompt includes PR22 audit-script invocation at mid-sprint retests
4. **Author `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` skeleton** — empty per-day sections for Days 0-13 + standard Sprint Log header.
5. **Validate schedule against budget:** total ≤ 168h; heaviest day ≤ 12h; no priority precedes its prep-task output; parallelization opportunities used.

**Sequencing constraints (per PREP_PLAN.md §Task 11):**

- Day 0: Task 2's PR20 codification + per-issue Phase 0 sections + Task 5's PR19 widening
- Days 1-3: Priority 1 (#1398 tightening) — highest leverage; +1 firm Solve
- Day 0 or Day 4: Task 6's AD architectural redesign validation experiments (PROCEED/REPLAN signal before Priority 3 commits)
- Days 4-9: Priority 3 (AD redesigns) — largest budget; depends on Task 6 PROCEED signal
- Days 5-11: Priorities 5, 7, 8, 9 in parallel (smaller priorities; can overlap with Priority 3)
- Day 5, Day 10, Day 13: pipeline retest (per PR6) + bucket-provenance update
- Day 13: buffer for unexpected scope adjustments + final retrospective

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` with day-by-day schedule (Day 0 + Days 1-13)
- `docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md` with day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` skeleton with empty per-day sections
- CHANGELOG.md updated with Task 11 completion entry

**Known Unknowns Updates:**

Task 11 integrates all verified Unknowns from Tasks 2-10. The integration is recorded in PLAN.md schedule choices. No additional KNOWN_UNKNOWNS.md updates required — but verify that all Critical/High Unknowns from Tasks 2-10 are now marked ✅ VERIFIED before authoring PLAN.md (if any remain 🔍 INCOMPLETE, escalate to the relevant task owner).

**PREP_PLAN.md Updates:**

In `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 11:

- Change `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`
- Add line: `**Completed:** YYYY-MM-DD`
- Fill in the "Changes" section
- Fill in the "Result" section with PLAN.md totals + heaviest-day check + final-prep-task-status summary
- Check off all items in "Acceptance Criteria"
- **Add a "Final Prep-Task Status" table** at the bottom of the PREP_PLAN.md showing all 11 tasks ✅ COMPLETE + total prep effort (~31-44h actual) + KU coverage (28/28 verified)

**CHANGELOG.md Update:**

Under `[Unreleased]` → `### Sprint 27 Preparation`, prepend a new bullet:

```markdown
- **Prep Task 11 COMPLETE (YYYY-MM-DD):** Integrated Tasks 1-10 outputs into a 14-day Sprint 27 execution schedule (`docs/planning/EPIC_4/SPRINT_27/PLAN.md`) + per-day execution prompts (`docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md`) + SPRINT_LOG.md skeleton. **Schedule honors:** Day 0 PR19 widening (Task 5) + Phase 0 codification application (Task 2); Days 1-3 Priority 1 (#1398 tightening); Day 0/4 Task 6 AD architectural validation experiments before Priority 3 commit; Days 4-9 Priority 3 (AD redesigns); Days 5-11 Priorities 5/7/8/9 parallel; Day 5/10/13 pipeline retest + PR22 audit script invocation. **Per-day budget verified ≤ 12h**; heaviest day = Day <N> (~<T h>); total estimated 97-157h within 168h cap. **Sprint 27 Targets vs Day 0 baseline:** Solve ≥ 111 (Day 0: 103; +8 firm + conditional), Match ≥ 66 (Day 0: 59; +7), path_syntax_error ≤ 6 (Day 0: 17; -11), Tests ≥ 4,750. **PREP_PLAN.md Final Prep-Task Status table added** — all 11 prep tasks ✅ COMPLETE. **All 28 Sprint 27 Known Unknowns (KUs 1.1-9.4) ✅ VERIFIED. Sprint 27 ready to kick off Day 0.**
```

**Quality Gate:**

Task 11 is docs/scheduling only — no Python source code is expected to change. Per CONTRIBUTING.md §"Before Every Commit" and `docs/development/AGENTS.md` §"Before submitting", run the full Python quality gate before committing regardless:

```bash
make typecheck && make format && make lint && make test
```

Do NOT proceed to commit until all pass. (For docs-only diffs the suite runs against the unchanged main state and should pass quickly; failures here indicate you touched something unintended.)

**Commit Message Format:**

```
Complete Sprint 27 Prep Task 11: Plan Sprint 27 Detailed Schedule

Integrates Tasks 1-10 outputs into the 14-day Sprint 27 execution
plan + per-day prompts + SPRINT_LOG.md skeleton. Sprint 27 is ready
to kick off Day 0.

## Schedule Summary

- Day 0: PR19 widening (Task 5) + Phase 0 codification application
  (Task 2)
- Days 1-3: Priority 1 (#1398 Phase A tightening) — +1 firm Solve
- Day 0 or Day 4: AD architectural validation experiments (Task 6
  PROCEED signal before Priority 3 commit)
- Days 4-9: Priority 3 (AD redesigns)
- Days 5-11: Priorities 5 / 7 / 8 / 9 in parallel
- Day 5 / Day 10 / Day 13: pipeline retest + PR22 audit script
- Day 13: final retest + SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md

## Budget Verification

- Total: <T_total> h within 168h cap
- Heaviest day: Day <N> at ~<T_max> h (≤ 12h)
- Parallelization: <list of parallel-priority days>

## Sprint 27 Targets (Day 0 → Day 13)

- Solve: 103 → ≥ 111 (+8)
- Match: 59 → ≥ 66 (+7)
- path_syntax_error: 17 → ≤ 6 (-11)
- Tests: ≥ 4,750

## Final Prep-Task Status

- All 11 prep tasks ✅ COMPLETE
- All 28 Known Unknowns ✅ VERIFIED
- Total prep effort: ~<T h> (within 31-44h budget)

## Deliverables

- New docs/planning/EPIC_4/SPRINT_27/PLAN.md (Day 0 + Days 1-13)
- New docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md
- New docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md (skeleton)
- Updated docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md: Task 11 → COMPLETE
  + Final Prep-Task Status table appended
- Updated CHANGELOG.md with Task 11 completion entry
```

**Pull Request:**

```bash
git push -u origin planning/sprint27-task11
gh pr create --title "Complete Sprint 27 Prep Task 11: Plan Sprint 27 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] Full Python quality gate run before commit per CONTRIBUTING.md §"Before Every Commit" (`make format`, `make lint`, `make test`) + `docs/development/AGENTS.md` §"Before submitting" (adds `make typecheck`): `make typecheck && make format && make lint && make test` all PASS
- [x] PLAN.md covers all 14 days (Day 0 + Days 1-13)
- [x] PLAN_PROMPTS.md covers all 14 days
- [x] SPRINT_LOG.md skeleton covers all 14 days
- [x] Total scheduled hours ≤ 168
- [x] No single day exceeds 12 hours
- [x] All 9 Sprint 27 priorities scheduled with explicit day(s) + hour budget
- [x] All 4 process recommendations (PR20-PR23) scheduled or marked completed in prep
- [x] Pipeline retest scheduled at Day 5, Day 10, Day 13
- [x] Phase 0 acceptance-gate verification (per PR20) precedes every Priority 1/2/3/5/7 src/ commit day
- [x] PR19 widening (per Task 5) scheduled on Day 0 (before Priority 1)
- [x] PR22 audit script (per Task 9) invoked at each mid-sprint retest
- [x] All 28 Known Unknowns verified in KNOWN_UNKNOWNS.md
- [x] Task 11 Acceptance Criteria all checked in PREP_PLAN.md
- [x] Final Prep-Task Status table appended to PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

**End of Sprint 27 Prep Task Execution Prompts.**

After Tasks 2-11 are all merged, Sprint 27 is ready to kick off Day 0 per the schedule in `docs/planning/EPIC_4/SPRINT_27/PLAN.md`.
