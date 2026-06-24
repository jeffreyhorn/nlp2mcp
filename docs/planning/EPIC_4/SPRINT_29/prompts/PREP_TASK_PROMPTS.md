# Sprint 29 Prep Task Execution Prompts

Self-contained prompts for Sprint 29 Prep Tasks 2–10. Each prompt can be copy-pasted into a new conversation to execute one prep task end-to-end, including the Known Unknowns updates, PREP_PLAN.md / CHANGELOG.md updates, quality gate, commit, and PR.

**Usage:**

1. Pick a task prompt below.
2. Paste it into a new conversation.
3. The agent creates the branch (`planning/sprint29-task<N>`), does the work, runs the quality gate, commits, pushes, and opens a PR.
4. Wait for reviewer comments on the PR.

Task 1 (Create Sprint 29 Known Unknowns List) is already ✅ COMPLETE — no prompt needed.

Tasks 2–10 are dispatchable in the following order per the dependency graph in `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` (Task 1 is done, so its direct dependents are immediately dispatchable):

- **Immediately dispatchable:** Task 2 (no dependencies), Tasks 6 + 7 (need only the completed Task 1)
- **After Task 2:** Task 3 (cold-convex survey reuses the Day-0 baseline) and Task 8 (with Task 6)
- **After Task 3:** Task 4 (Phase 0 gates need the cold-convex Case-b leads) and Task 9 (with Task 6)
- **After Task 4:** Task 5 (REPLAN assessment consumes the Phase 0 gates)
- **After all (final integration):** Task 10

**Critical path:** Task 1 → Task 3 → Task 4 → Task 5 → Task 10.

**Cross-cutting conventions for every prompt below:**

- Branch from `main`; PR targets `main`.
- User preferences (enforce in every commit/PR): **NO `Co-Authored-By` lines** in commit messages; **NO "Generated with Claude Code"** in PR descriptions.
- Replace `YYYY-MM-DD` with the actual date at execution time.
- These are **docs/design/analysis-only** prep tasks — no Python source changes are expected (the scripts they design are *built in-sprint*, not in prep; the harness/detector/gate already exist on `main`). Run the full quality gate before committing regardless; if you did touch Python, it must pass.
- Every Known-Unknowns update uses the verification block: **Status** (✅ VERIFIED / ❌ WRONG), **Verified by**, **Date**, **Findings**, **Evidence**, **Decision**.

---

## Task 2 Prompt: Sprint 28 → Sprint 29 Bucket-Provenance Baseline + Re-Baseline Discipline (PR15 + PR17 + PR25)

**Branch:** Create a new branch named `planning/sprint29-task2` from `main`

**Priority:** Critical (4–5 hours)

**Objective:** Establish the authoritative Sprint 29 Day-0 baseline from the Sprint 28 Day-13 retest, with a per-failing-model bucket provenance table, and — critically for Sprint 29 — split the Match baseline into its **genuine** (≈68, the cross-term fixes) and **methodology** (≈24, the Day-9 presolve-retry-on-cold-mismatch broadening) components so every Sprint 29 projected delta is labeled genuine vs methodology-inflated.

**Unknowns Verified:** 8.2, 8.3 (and contributes the Day-0-bucket confirmation to 1.1, 2.1, 4.1, 6.1)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 2
- `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` §Unknowns 8.2 (re-baseline representation), 8.3 (Day-0 = Sprint 28 final)
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` header + §"What We'd Do Differently #5" (the methodology-lift / re-baseline lesson) + §"Day 13" Match decomposition
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" (the +7 genuine / ~+24 methodology / −1 rocket split; the ~24 presolve-recovered model list) + `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (the bucket-provenance template)
- `data/gamslib/gamslib_status.json` (fresh Day-13 retest DB: Solve 107 / Match 92 / model_infeasible 7) + `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp` (the methodology source)

**Tasks to Complete:**

1. Confirm Day-0 = Sprint 28 final: `git diff <S28-close-SHA>..HEAD -- src/ scripts/` empty → reuse the committed DB (no fresh retest); confirm the DB recomputes to Solve 107 / Match 92 / model_infeasible 7 and has 0 absolute-path leaks (#1400).
2. Headline counts table (142-model scope) with the Sprint 29 target column + gap.
3. Genuine-vs-methodology Match partition: list the +24 methodology-recovered models (`model_optimal_presolve` + match, cold golden byte-identical to a pre-Day-9 baseline) vs the +7 genuine cross-term matches; record the genuine baseline (≈68).
4. Per-failing-model bucket provenance table for the Sprint 29 targets (mine, rocket, the cold-convex cohort, the objective-mismatch cohort, the offset-alias mismatches) — Sprint 28 final bucket + gating issue.
5. PR25 projection table: per Sprint 29 priority, label each projected Solve/Match delta genuine vs methodology/bucket-forward; tally only genuine transitions toward Solve ≥ 109 / Match ≥ 96-stretch.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` — §1 headline counts, §2 carryforward bucket provenance, §3 PR25 projection table
- The Match baseline split genuine (≈68) vs methodology (≈24) with model lists
- Day-0 = Sprint 28 final confirmation (no fresh retest)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.2, 8.3
- CHANGELOG.md updated with the Task 2 completion entry

**Known Unknowns Updates:** For Unknowns 8.2, 8.3 in `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md`, set the "Verification Results" subsection: Status ✅ VERIFIED (or ❌ WRONG + correction), Verified by Task 2, Date, Findings (the genuine-vs-methodology split + the Day-0 baseline confirmation), Evidence (DB recompute + git diff), Decision (the attributable targets + any scope adjustment). Also record the Day-0-bucket aspect of 1.1/2.1/4.1/6.1 (their fix-surface aspect is verified by Tasks 3/4/5).

**PREP_PLAN.md Updates:** In §Task 2: `**Status:** 🔵 NOT STARTED` → `**Status:** ✅ COMPLETE`; add `**Completed:** YYYY-MM-DD`; fill "Changes" (what was measured/authored) + "Result" (the genuine-vs-methodology baseline); check off all Acceptance Criteria (`- [ ]` → `- [x]`).

**CHANGELOG.md Update:** Under `[Unreleased]` → `### Sprint 29 Prep`, prepend:
```markdown
- **Prep Task 2 COMPLETE (YYYY-MM-DD):** Sprint 29 Day-0 baseline = Sprint 28 final (Solve 107 / Match 92 / model_infeasible 7; no fresh retest). Match baseline split genuine (≈68) vs methodology (≈24, the Day-9 presolve-retry broadening). PR25 projection labels each Sprint 29 delta genuine vs methodology/bucket-forward. Verified Unknowns 8.2, 8.3.
```

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only task — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 2: Bucket-Provenance Baseline + Re-Baseline Discipline

Day-0 = Sprint 28 final (Solve 107 / Match 92 / model_infeasible 7; no retest).
Match baseline split genuine (~68) vs methodology (~24, the Day-9 presolve-retry
broadening). PR25 projection labels each Sprint 29 delta genuine vs
methodology/bucket-forward; only genuine transitions count toward targets.

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md
- KNOWN_UNKNOWNS.md: Unknowns 8.2, 8.3 verified
- PREP_PLAN.md: Task 2 -> COMPLETE
- CHANGELOG.md: Task 2 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task2
gh pr create --title "Complete Sprint 29 Prep Task 2: Bucket-Provenance Baseline + Re-Baseline Discipline" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] BASELINE_METRICS.md records Day-0 counts + per-failing-model buckets + the genuine-vs-methodology Match split
- [x] Day-0 = Sprint 28 final confirmed (git diff empty, 0 path leaks)
- [x] Unknowns 8.2, 8.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 2 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 3 Prompt: Cold-Convex Cohort Survey + Case-(b/c) Partition (Priority 4 Foundation)

**Branch:** Create a new branch named `planning/sprint29-task3` from `main`

**Priority:** High (5–7 hours)

**Objective:** Survey the ~24 non-convex models that match ONLY via the `--nlp-presolve` warm-start (the cold-convex cohort), and partition them into Case-b (a genuine cold-emit bug that the warm-start masks → fixable in Sprint 29) and Case-c (inherent non-convexity → cold infeasibility expected → Sprint 30 forcing strategies), using the Sprint-28 KKT-residual harness. This is a survey/catalog task that must precede the Phase-0 gates (Task 4) and the schedule (Task 10) because the Case-b count determines how much of Priority 4 is achievable.

**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 3; `KNOWN_UNKNOWNS.md` §Category 4 (Unknowns 4.1–4.4)
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" (the ~24 methodology-recovered model list)
- GitHub #1447 maxmin (`stat_mindist` cold-emit Case-b lead; harness-localized in Sprint 28) — there is a local `docs/issues/ISSUE_1447_*.md`
- `scripts/diagnostics/kkt_residual.py` (Case-(a/b/c) verdict + dual-transfer self-check) and `scripts/diagnostics/check_presolve_divergence.py`
- `data/gamslib/gamslib_status.json` `convexity.classification` (heuristic cross-check) + `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp`

**Tasks to Complete:**

1. Enumerate the cohort from the Day-13 DB (`outcome_category = model_optimal_presolve` + `comparison_status = match`, where the cold solve failed/mismatched).
2. Run `kkt_residual.py` on each at its NLP KKT point; record the Case-(a/b/c) verdict, the max-residual row, and the dual-transfer self-check.
3. Cross-check convexity: a *verified_convex* model that cold-fails is a strong Case-b signal; a *non-convex* cold-fail is expected Case-c. Use the harness verdict as the tie-breaker when it disagrees with the DB classification.
4. Partition + size: the Case-b list (Sprint-29-fixable, ranked by residual-localizability) and the Case-c list (Sprint-30 hand-off); confirm #1447 maxmin as the lead Case-b + ≥1 more.
5. Confirm `check_presolve_divergence.py` soft-classifies the cohort (no false hard-fails). Feed the partition size to Task 4 (gates) and Task 10 (P4 budget).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` enumerating the cohort with a per-model harness verdict
- The Case-b vs Case-c partition with counts + a Sprint-29-fixable ranked list
- #1447 maxmin confirmed as the lead Case-b + ≥1 additional Case-b candidate
- The partition size fed to Tasks 4 and 10
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4
- CHANGELOG.md updated with the Task 3 completion entry

**Known Unknowns Updates:** For Unknowns 4.1, 4.2, 4.3, 4.4: Status ✅ VERIFIED (or ❌ WRONG), Verified by Task 3, Date, Findings (the partition counts + the maxmin shared-shape determination + the convexity-seed audit + the detector soft-classification), Evidence (the per-model harness verdicts), Decision (the Sprint-29-fixable Case-b list + the Priority-4 budget implication, including any freed budget to pre-allocate to Priorities 6/7).

**PREP_PLAN.md Updates:** §Task 3 → COMPLETE + Completed date; fill Changes + Result (the partition counts); check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 3 COMPLETE (YYYY-MM-DD):** Cold-convex cohort survey — <N> models partitioned into <b> Case-b (Sprint-29-fixable, #1447 maxmin lead) / <c> Case-c (Sprint-30 hand-off). Verified Unknowns 4.1–4.4.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Analysis-only — no Python expected. (The harness/detector runs are read-only.) Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 3: Cold-Convex Cohort Survey + Case-(b/c) Partition

Surveyed the ~24 warm-start-only non-convex cohort with kkt_residual.py and
partitioned Case-b (cold-emit bug, Sprint-29-fixable; #1447 maxmin lead) from
Case-c (inherent non-convexity, Sprint-30 forcing). Sizes Priority 4 and feeds
the Phase-0 gates (Task 4) + schedule (Task 10).

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md
- KNOWN_UNKNOWNS.md: Unknowns 4.1, 4.2, 4.3, 4.4 verified
- PREP_PLAN.md: Task 3 -> COMPLETE
- CHANGELOG.md: Task 3 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task3
gh pr create --title "Complete Sprint 29 Prep Task 3: Cold-Convex Cohort Survey + Case-(b/c) Partition" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (analysis-only)
- [x] COLD_CONVEX_COHORT_SURVEY.md enumerates the cohort + per-model harness verdict
- [x] Case-b/Case-c partition produced with counts; #1447 maxmin + ≥1 more confirmed Case-b
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 3 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 4 Prompt: Author Phase 0 Acceptance Gates for the Carryforward + Backlog Tracks (PR20 + PR24 + PR27)

**Branch:** Create a new branch named `planning/sprint29-task4` from `main`

**Priority:** Critical (5–7 hours) — **depends on Task 3 (the cold-convex Case-b leads feed the Priority-4 gates)**

**Objective:** Author or refresh a Phase 0 acceptance gate in each target issue doc — a hand-derived KKT shape (where applicable), a *traced* fix-surface framed as a Day-0 hypothesis (PR24), and a `kkt_residual.py`-based verification method (PR27) — for the Sprint 29 implementation tracks: #1443 mine, #1462 rocket, #1385, the cold-convex Case-b leads (#1447 + the Task-3 list), the objective-mismatch cohort (#1332/#1247/#1239/#1236), and the offset-alias gradient pair (#1146/#1143).

**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 4; `KNOWN_UNKNOWNS.md` §Unknowns 1.1–1.3, 2.1–2.3, 3.1–3.3, 4.2, 6.1, 7.1, 7.2; `COLD_CONVEX_COHORT_SURVEY.md` (Task 3 output — the Case-b leads)
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (PR20 + PR24 template); `scripts/diagnostics/kkt_residual.py` + `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`
- Target issue docs: `docs/issues/ISSUE_{1443,1385,1447,1332,1247,1239,1236,1146,1143}_*.md` (local) + GitHub #1462 (no local doc — root cause localized in `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13"); for #1462 author the Phase 0 gate in the GitHub issue or create a local `docs/issues/ISSUE_1462_*.md`
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 4" (mine cold MS-5), §"Day 13" (rocket warm-start 1.137 → 1.016)

**Tasks to Complete:**

1. For each track author/refresh `## Phase 0: Acceptance Gate` with four `###` subsections: (a) hand-derived/expected KKT shape; (b) the *traced* fix-surface as a Day-0 hypothesis (PR24 — symptom + reproducer + a candidate surface labeled "to be confirmed by the Day-0 trace"); (c) the verification methodology — the exact `kkt_residual.py <model>` command + the PROCEED verdict + the Case-c REPLAN exit; (d) the acceptance criterion (MODEL STATUS / objective / residual threshold).
2. #1443 mine: gate on the max-residual row → head-offset dual-transfer (Case b → PROCEED) vs cold non-convex coupling (Case c → Sprint-30 REPLAN).
3. #1462 rocket: warm-start `nu_*_fx_h0` lands first (known); gate the *residual* `piL/piU`-at-`h0` question + the 13-presolve-model byte/solve regression check.
4. #1385: gate the hand-derived runtime-guard `stat_*` cross-terms for the smallest timeout target + the atomic-landing note.
5. Cohort gates (#1447 + Task-3 Case-b list; #1332/#1247/#1239/#1236; #1146/#1143): per-model harness verdict as the PROCEED condition; #1146/#1143 add a property-test fixture requirement.

**Deliverables:**

- `## Phase 0: Acceptance Gate` authored/refreshed in #1443, #1462, #1385, #1447, #1332, #1247, #1239, #1236, #1146, #1143
- Each gate cites the exact `kkt_residual.py` command + PROCEED verdict + Case-c REPLAN exit
- #1462's gate frames the residual `piL/piU`-at-`h0` question as the hypothesis (warm-start known)
- The cold-convex Case-b leads (from Task 3) gated for Priority 4
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2
- CHANGELOG.md updated with the Task 4 completion entry

**Known Unknowns Updates:** For each listed unknown: Status ✅ VERIFIED (the fix-surface is framed as a Day-0 hypothesis with a harness verification method) or ❌ WRONG; Verified by Task 4; Date; Findings (the hand-derived shape + the candidate traced surface); Evidence (the issue-doc Phase-0 gate); Decision (the PROCEED verdict + the Case-c REPLAN exit). Note: 1.1/2.2/7.2's PROCEED/REPLAN *decision* is finalized by Task 5; 6.1/7.1 detail by Task 9.

**PREP_PLAN.md Updates:** §Task 4 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 4 COMPLETE (YYYY-MM-DD):** Phase 0 acceptance gates authored for the 10 Sprint 29 tracks (#1443/#1462/#1385/#1447/#1332/#1247/#1239/#1236/#1146/#1143) — each a Day-0 kkt_residual.py hypothesis (PR24) with a PROCEED verdict + Case-c Sprint-30 REPLAN exit. Verified Unknowns 1.1–1.3, 2.1–2.3, 3.1–3.3, 4.2, 6.1, 7.1, 7.2.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 4: Author Phase 0 Acceptance Gates

Authored/refreshed Phase 0 gates for the 10 Sprint 29 implementation tracks,
each framing its fix-surface as a Day-0 kkt_residual.py hypothesis (PR24) with a
PROCEED verdict + an explicit Case-c Sprint-30 REPLAN exit. #1462's gate frames
the residual piL/piU-at-h0 question (warm-start known).

## Deliverables
- docs/issues/ISSUE_*.md Phase-0 sections (#1443/#1462/#1385/#1447/#1332/#1247/#1239/#1236/#1146/#1143)
- KNOWN_UNKNOWNS.md: Unknowns 1.1-1.3, 2.1-2.3, 3.1-3.3, 4.2, 6.1, 7.1, 7.2 verified
- PREP_PLAN.md: Task 4 -> COMPLETE
- CHANGELOG.md: Task 4 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task4
gh pr create --title "Complete Sprint 29 Prep Task 4: Author Phase 0 Acceptance Gates" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] Phase 0 gate present in all 10 target issue docs
- [x] Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites kkt_residual.py + has a Case-c REPLAN exit
- [x] Unknowns 1.1-1.3, 2.1-2.3, 3.1-3.3, 4.2, 6.1, 7.1, 7.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 4 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 5 Prompt: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443, #1462, #1111/#1112; PR16)

**Branch:** Create a new branch named `planning/sprint29-task5` from `main`

**Priority:** High (3–5 hours) — **depends on Task 4 (consumes the Phase 0 gates)**

**Objective:** Apply the PR16 hypothesis-validation methodology to the three Sprint 29 tracks most likely to prove multi-bug or architectural — #1443 mine (deeper cold-infeasible complementarity/bound coupling beyond the head-offset dual-transfer), #1462 rocket (residual non-convex convergence beyond the `_fx_` warm-start), and Priority 7's AD-engine #1111/#1112 (offset-alias gradient possibly requiring an alias-aware-differentiation redesign) — and pin an explicit PROCEED/REPLAN signal and Sprint 30 exit for each.

**Unknowns Verified:** 1.1, 2.2, 7.2, 7.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 5; `KNOWN_UNKNOWNS.md` §Unknowns 1.1, 2.2, 7.2, 7.4; the Phase 0 gates from Task 4
- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (the Sprint 28 analog — structural template)
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 4" (mine cold MS-5) + §"Day 13" (rocket warm-start residual); GitHub #1111 / #1112 (AD-engine architecture, no local doc) + `docs/issues/ISSUE_{1146,1143}_*.md`
- `scripts/diagnostics/kkt_residual.py` (the Case-c verdict = the REPLAN trigger)

**Tasks to Complete:**

1. For each of the three tracks: state the architectural hypothesis, the single-model validation experiment (the Day-0 `kkt_residual.py` trace + any quick prototype-then-revert probe), the PROCEED signal, the REPLAN signal, and the Sprint 30 exit scope.
2. #1443: PROCEED if the max-residual row is the head-offset dual-transfer (Case b); REPLAN if distributed across `comp_*`/bound rows (Case c).
3. #1462: PROCEED if the residual MS-5 is the localizable `piL/piU`-at-`h0` activation; REPLAN if non-convex convergence is intrinsic.
4. #1111/#1112: PROCEED if himmel16/polygon is a localized AD cross-term correction; REPLAN if it requires the alias-aware-differentiation / dollar-condition-propagation redesign.
5. Budget-reallocation plan per REPLAN (which lower-risk priority absorbs the freed budget).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` with per-track hypothesis, validation experiment, PROCEED/REPLAN signals, Sprint 30 exit
- A budget-reallocation plan for each possible REPLAN
- The three Critical REPLAN-prone unknowns resolved into scheduled decisions
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.2, 7.2, 7.4
- CHANGELOG.md updated with the Task 5 completion entry

**Known Unknowns Updates:** For Unknowns 1.1, 2.2, 7.2, 7.4: Status ✅ VERIFIED (the REPLAN decision criterion is pinned) or ❌ WRONG; Verified by Task 5; Date; Findings (the hypothesis + validation experiment per track); Evidence (the harness verdict + any prototype-then-revert result); Decision (the PROCEED/REPLAN signal + Sprint-30 exit + budget reallocation).

**PREP_PLAN.md Updates:** §Task 5 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 5 COMPLETE (YYYY-MM-DD):** REPLAN risk assessment for the three diagnosis-heavy tracks (#1443 cold-coupling, #1462 residual non-convergence, #1111/#1112 AD-engine) — each with a PROCEED/REPLAN signal, Sprint-30 exit, and budget-reallocation plan. Verified Unknowns 1.1, 2.2, 7.2, 7.4.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 5: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment

PR16 hypothesis-validation for #1443 (cold-infeasible coupling), #1462 (residual
non-convex convergence), and #1111/#1112 (offset-alias AD-engine). Each track
gets a PROCEED/REPLAN signal tied to the harness verdict, a Sprint-30 exit, and a
budget-reallocation plan.

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.1, 2.2, 7.2, 7.4 verified
- PREP_PLAN.md: Task 5 -> COMPLETE
- CHANGELOG.md: Task 5 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task5
gh pr create --title "Complete Sprint 29 Prep Task 5: REPLAN-Prone Track Risk Assessment" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] REPLAN_RISK_ASSESSMENT.md covers #1443, #1462, #1111/#1112 with PROCEED/REPLAN signals + Sprint-30 exits + budget reallocation
- [x] Unknowns 1.1, 2.2, 7.2, 7.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 5 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 6 Prompt: Reusable-Tooling Readiness Audit (KKT-Residual Harness, Divergence Detector, Golden-Staleness Gate)

**Branch:** Create a new branch named `planning/sprint29-task6` from `main`

**Priority:** High (3–4 hours)

**Objective:** Audit the three diagnostic/CI tools Sprint 28 built and Sprint 29 reuses — `kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py` — against the new Sprint 29 model classes (presolve `_fx_`-multiplier warm-starts, head-domain-offset multipliers, the cold-convex cohort, offset-alias gradients), and identify any *minimal* extension needed before Day 1 so the in-sprint diagnosis runs on tooling that already covers the cases.

**Unknowns Verified:** 1.2, 2.4, 4.4, 8.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 6; `KNOWN_UNKNOWNS.md` §Unknowns 1.2, 2.4, 4.4, 8.4
- `scripts/diagnostics/kkt_residual.py` + `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`; `scripts/diagnostics/check_presolve_divergence.py` + `.github/workflows/presolve-divergence.yml`; `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/golden_staleness_allowlist.txt` + `scripts/sprint_audit/changed_emit_artifacts.py`
- `scripts/diagnostics/presolve_divergence_allowlist.txt` (korcge #1439) + GitHub #1461 (indus cross-platform determinism)

**Tasks to Complete:**

1. KKT-residual harness: run it on rocket (`_fx_` multipliers) and mine (head-domain-offset); confirm the dual-transfer self-check reports CONSISTENT. If it mis-transfers, scope the minimal one-line index-mapping extension as a Day-0 task.
2. Presolve-divergence detector: confirm the cold-convex cohort classifies as soft `obj_gap` (not hard-fail); confirm rocket #1462 is allowlisted or correctly flagged; verify no false hard-fails.
3. Golden-staleness gate: confirm the allowlist is current (indus #1461; korcge #1439 in the divergence allowlist); confirm the changed-golden-set diff (`changed_emit_artifacts.py`) is the right Task-8 checkpoint re-solve input.
4. Produce a gap list (each Day-0 extension ≤ 1h) or "no extensions needed".

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` with a per-tool readiness verdict
- A scoped gap list (Day-0 extensions ≤ 1h each) or a "no extensions needed" confirmation
- Confirmation the changed-golden-set diff is the right Task-8 input
- Confirmation the divergence detector won't false-hard-fail the cold-convex cohort
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.4, 4.4, 8.4
- CHANGELOG.md updated with the Task 6 completion entry

**Known Unknowns Updates:** For Unknowns 1.2, 2.4, 4.4, 8.4: Status ✅ VERIFIED or ❌ WRONG; Verified by Task 6; Date; Findings (the per-tool readiness verdict); Evidence (the harness self-check output on rocket/mine + the detector run on a cohort sample + the allowlist contents); Decision (gap list or "no extensions needed").

**PREP_PLAN.md Updates:** §Task 6 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 6 COMPLETE (YYYY-MM-DD):** Reusable-tooling readiness audit — kkt_residual.py dual-transfer validated on rocket (_fx_) + mine (head-offset); presolve-divergence detector soft-classifies the cold-convex cohort; golden-staleness allowlist current. Gap list: <none / N Day-0 extensions>. Verified Unknowns 1.2, 2.4, 4.4, 8.4.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Audit-only — no Python expected (only read-only tool runs). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 6: Reusable-Tooling Readiness Audit

Audited the three Sprint-28 diagnostic tools against the new Sprint 29 model
classes: kkt_residual.py dual-transfer on rocket (_fx_) + mine (head-offset);
presolve-divergence detector soft-classifies the cold-convex cohort (no false
hard-fails); golden-staleness allowlist current. Gap list scoped (each <=1h) or
none.

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md
- KNOWN_UNKNOWNS.md: Unknowns 1.2, 2.4, 4.4, 8.4 verified
- PREP_PLAN.md: Task 6 -> COMPLETE
- CHANGELOG.md: Task 6 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task6
gh pr create --title "Complete Sprint 29 Prep Task 6: Reusable-Tooling Readiness Audit" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (audit-only)
- [x] TOOLING_READINESS_AUDIT.md covers all three Sprint-28 tools
- [x] Harness dual-transfer validated on rocket + mine; detector soft-classifies the cohort; allowlists current
- [x] Unknowns 1.2, 2.4, 4.4, 8.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 6 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 7 Prompt: camcge → Epic 5 Scoping Pre-Work (Priority 5)

**Branch:** Create a new branch named `planning/sprint29-task7` from `main`

**Priority:** Medium (3–4 hours)

**Objective:** Gather the evidence and structure for the camcge → Epic 5 scoping observation so the in-sprint Priority 5 task is a write-up only (no `src/`): assemble the Sprint-28 Day-11 Walras-degeneracy diagnosis, survey the CGE cohort (#1354/#1355/#1317/#1331/#1251 + #1330) for shared vs distinct degeneracies, and stub `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`.

**Unknowns Verified:** 5.1, 5.2, 5.3

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 7; `KNOWN_UNKNOWNS.md` §Category 5 (Unknowns 5.1, 5.2, 5.3)
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 11" (the camcge Walras-degeneracy diagnosis) + `docs/issues/ISSUE_1330_*.md` (REPLAN → Epic 5)
- `docs/issues/ISSUE_{1354,1355,1317,1331,1251,1070}_*.md` (the CGE cohort)
- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (the Task-6-gate methodology)

**Tasks to Complete:**

1. Assemble the diagnosis: the harness CASE_C verdict + the basis-singularity report + the Jacobian-rank finding at the NLP point, with the precise linearly-dependent rows (`equil`/`lmequil`) and the missing numéraire.
2. Survey the CGE cohort: record whether each of #1354/#1355/#1317/#1331/#1251 shares the camcge Walras redundancy or has a distinct degeneracy (paper analysis, no `src/`).
3. Name the transformation: the single redundant-row drop + price-numéraire selection, and a paper argument it preserves the economic solution for ≥1 cohort model.
4. Stub `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (create the dir + the doc) with the diagnosis, cohort, proposed transformation, and open questions.

**Deliverables:**

- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (stub) with the camcge diagnosis, CGE cohort survey, and named transformation
- A shared-vs-distinct degeneracy classification across #1354/#1355/#1317/#1331/#1251
- A paper argument that the proposed numéraire-fix transformation preserves the economic solution
- Priority 5 reduced to a write-up-only in-sprint task (no `src/`)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3
- CHANGELOG.md updated with the Task 7 completion entry

**Known Unknowns Updates:** For Unknowns 5.1, 5.2, 5.3: Status ✅ VERIFIED or ❌ WRONG; Verified by Task 7; Date; Findings (the shared-vs-distinct classification + the solution-preservation argument + the scope boundary); Evidence (the per-model singularity reports); Decision (the Epic-5 scope + #1330 moved to Epic 5).

**PREP_PLAN.md Updates:** §Task 7 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 7 COMPLETE (YYYY-MM-DD):** camcge → Epic 5 scoping pre-work — EPIC_5/CGE_DEGENERACY_SCOPING.md stub with the Walras-degeneracy diagnosis, CGE cohort (#1354/#1355/#1317/#1331/#1251) shared-vs-distinct classification, and the numéraire-fix transformation. #1330 → Epic 5 (no Sprint-29 src/). Verified Unknowns 5.1, 5.2, 5.3.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 7: camcge -> Epic 5 Scoping Pre-Work

Stubbed EPIC_5/CGE_DEGENERACY_SCOPING.md with the Sprint-28 Day-11 Walras-law
degeneracy diagnosis, the CGE cohort (#1354/#1355/#1317/#1331/#1251)
shared-vs-distinct classification, and the named numeraire-fix + redundant-row
transformation. #1330 confirmed Epic 5 (no Sprint-29 src/); Priority 5 reduced to
an in-sprint write-up.

## Deliverables
- docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md
- KNOWN_UNKNOWNS.md: Unknowns 5.1, 5.2, 5.3 verified
- PREP_PLAN.md: Task 7 -> COMPLETE
- CHANGELOG.md: Task 7 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task7
gh pr create --title "Complete Sprint 29 Prep Task 7: camcge -> Epic 5 Scoping Pre-Work" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] EPIC_5/CGE_DEGENERACY_SCOPING.md stub created with the diagnosis + cohort survey + named transformation
- [x] #1330 moved to Epic 5; Priority 5 scoped to write-up only
- [x] Unknowns 5.1, 5.2, 5.3 verified in KNOWN_UNKNOWNS.md
- [x] Task 7 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 8 Prompt: Checkpoint Re-Solve + Post-Methodology Re-Baseline Tooling Design (Priority 8)

**Branch:** Create a new branch named `planning/sprint29-task8` from `main`

**Priority:** Medium (3–4 hours) — **depends on Tasks 2 (baseline) + 6 (tooling audit)**

**Objective:** Design the two Priority-8 infrastructure deliverables that the Sprint 28 Day-13 lessons require: a checkpoint **re-solve of the changed-golden set** (so a broken solve surfaces at Day 5/Day 10, not Day 13), and a **post-methodology re-baseline** step in the PR25 projection-discipline template (so the headline delta stays attributable after any pipeline-methodology change).

**Unknowns Verified:** 8.1, 8.2

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 8; `KNOWN_UNKNOWNS.md` §Unknowns 8.1, 8.2; `BASELINE_METRICS.md` (Task 2) + `TOOLING_READINESS_AUDIT.md` (Task 6)
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #4 (re-solve the changed-golden set) + #5 (re-baseline)
- `scripts/sprint_audit/changed_emit_artifacts.py` (the at-risk-list input) + `scripts/gamslib/run_full_test.py` (`--model` per-model re-solve)
- `docs/planning/EPIC_4/SPRINT_28/PLAN.md` §"Pipeline Retest Cadence" (Day 5 / Day 10 / Day 13) + `CONTRIBUTING.md` §"Projection Discipline" (PR25)

**Tasks to Complete:**

1. Design the `--resolve-changed` checkpoint mode: given the `changed_emit_artifacts.py` golden diff, re-solve only those models and diff their solve/compare buckets against the committed DB — flag any model that regressed. Specify the interface, the at-risk-list source, and the wall-clock budget.
2. Design the re-baseline step: a PR25 template addition that, after any pipeline-methodology change, recomputes the genuine-vs-methodology split (Task 2) and records the new attributable baseline.
3. Wire into the cadence: where in the Day-5/Day-10 checkpoint the re-solve runs + the GO/NO-GO criterion (any changed-golden model regressed → investigate).
4. Document the design in `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md`.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` with the `--resolve-changed` interface + the re-baseline step
- The at-risk-list source confirmed (`changed_emit_artifacts.py` diff) + the checkpoint wall-clock budget
- The GO/NO-GO criterion (any changed-golden model regressed → investigate)
- The PR25 re-baseline template addition specified
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2
- CHANGELOG.md updated with the Task 8 completion entry

**Known Unknowns Updates:** For Unknowns 8.1, 8.2: Status ✅ VERIFIED or ❌ WRONG; Verified by Task 8; Date; Findings (the re-solve wall-clock budget + the re-baseline representation); Evidence (the at-risk-list sizing + per-model solve-time estimate); Decision (the `--resolve-changed` design + the GO/NO-GO criterion).

**PREP_PLAN.md Updates:** §Task 8 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 8 COMPLETE (YYYY-MM-DD):** Priority-8 design — the checkpoint --resolve-changed re-solve (so a broken solve surfaces Day 5/10, not Day 13) + the PR25 post-methodology re-baseline step. Implements the Sprint-28 Day-13 lessons #4 + #5. Verified Unknowns 8.1, 8.2.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Design-only — no Python expected (the tool is built in-sprint). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 8: Checkpoint Re-Solve + Re-Baseline Design

Designed the Priority-8 infrastructure: a checkpoint --resolve-changed mode that
re-solves only the changed-golden set (so a rocket-style broken solve surfaces at
Day 5/10, not Day 13) + a PR25 post-methodology re-baseline step (so the headline
Match stays attributable). Implements the Sprint-28 Day-13 lessons #4 + #5.

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md
- KNOWN_UNKNOWNS.md: Unknowns 8.1, 8.2 verified
- PREP_PLAN.md: Task 8 -> COMPLETE
- CHANGELOG.md: Task 8 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task8
gh pr create --title "Complete Sprint 29 Prep Task 8: Checkpoint Re-Solve + Re-Baseline Design" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (design-only)
- [x] PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md specifies --resolve-changed + the re-baseline step
- [x] At-risk-list source + checkpoint budget + GO/NO-GO criterion specified
- [x] Unknowns 8.1, 8.2 verified in KNOWN_UNKNOWNS.md
- [x] Task 8 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 9 Prompt: Backlog Fix-Surface Analysis (#1332/#1247/#1239/#1236; #1146/#1143/#1112/#1111)

**Branch:** Create a new branch named `planning/sprint29-task9` from `main`

**Priority:** Medium (3–4 hours) — **depends on Tasks 3 (cold-convex partition) + 6 (tooling audit)**

**Objective:** Pre-analyze the Priority-6 (objective-mismatch cohort #1332/#1247/#1239/#1236) and Priority-7 (offset-alias gradient + dollar-condition AD #1146/#1143/#1112/#1111) fix surfaces as Day-0 hypotheses (PR24), identify any shared root causes with the cold-convex cohort (Task 3) or each other, and plan the property-test fixtures (extending the Sprint-28 `test_ad_crossterm_shapes.py` catalog) that guard the P7 AD changes.

**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3, 7.4

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` §Task 9; `KNOWN_UNKNOWNS.md` §Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4; `COLD_CONVEX_COHORT_SURVEY.md` (Task 3) + `TOOLING_READINESS_AUDIT.md` (Task 6)
- `docs/issues/ISSUE_{1332,1247,1239,1236,1146,1143}_*.md` (local) + GitHub #1112 / #1111 (no local doc)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/shape{1..6}_*.gms` (the property-test catalog to extend) + `scripts/diagnostics/kkt_residual.py`

**Tasks to Complete:**

1. Objective-mismatch cohort: for #1332/#1247/#1239/#1236 record the harness Case-(a/b/c) verdict, the candidate fix-surface as a Day-0 hypothesis (PR24), and any shared root cause with a cold-convex Case-b model; verify prolog's NLP −0.0 reference is a valid target (vs a CGE-degenerate #1070).
2. Offset-alias gradient: determine whether #1146 himmel16 and #1143 polygon share the root cause (one fix → two models); frame the fix-surface as localized-vs-architectural (#1111/#1112 — the Task-5 REPLAN trigger).
3. Property-test fixture plan: specify the new `tests/fixtures/crossterm_shapes/shape7_offset_alias_*.gms` fixture (and any others) that guards the P7 fix.
4. Consolidation map: which fixes land multiple models (himmel16+polygon; any cohort+cold-convex overlap).

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` with per-issue Day-0 fix-surface hypotheses (PR24)
- The himmel16/polygon shared-root-cause determination + the localized-vs-architectural split (Task-5 trigger)
- A property-test fixture plan extending `test_ad_crossterm_shapes.py`
- A consolidation map (which fixes land multiple models)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4
- CHANGELOG.md updated with the Task 9 completion entry

**Known Unknowns Updates:** For Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4: Status ✅ VERIFIED or ❌ WRONG; Verified by Task 9; Date; Findings (the per-model verdicts + the shared-root-cause + the fixture plan); Evidence (the harness traces + the catalog review); Decision (the consolidation map + the localized-vs-architectural split feeding Task 5).

**PREP_PLAN.md Updates:** §Task 9 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 9 COMPLETE (YYYY-MM-DD):** Backlog fix-surface analysis — objective-mismatch cohort (#1332/#1247/#1239/#1236) per-model Case verdicts + offset-alias (#1146 himmel16 / #1143 polygon) shared-root-cause + localized-vs-architectural split + the shape7 property-test fixture plan + a consolidation map. Verified Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Analysis-only — no Python expected (the fixtures are added in-sprint). Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 9: Backlog Fix-Surface Analysis

Pre-analyzed the objective-mismatch cohort (#1332/#1247/#1239/#1236) and the
offset-alias gradient pair (#1146 himmel16 / #1143 polygon) as Day-0 hypotheses
(PR24): per-model harness verdicts, the himmel16/polygon shared root cause,
localized-vs-architectural (#1111/#1112) split, a shape7 property-test fixture
plan, and a consolidation map (which fixes land multiple models).

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md
- KNOWN_UNKNOWNS.md: Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4 verified
- PREP_PLAN.md: Task 9 -> COMPLETE
- CHANGELOG.md: Task 9 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task9
gh pr create --title "Complete Sprint 29 Prep Task 9: Backlog Fix-Surface Analysis" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (analysis-only)
- [x] BACKLOG_FIX_SURFACE_ANALYSIS.md covers all 8 backlog issues with Day-0 hypotheses
- [x] himmel16/polygon shared-root-cause + localized-vs-architectural split recorded; shape7 fixture planned; consolidation map produced
- [x] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4 verified in KNOWN_UNKNOWNS.md
- [x] Task 9 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Task 10 Prompt: Plan Sprint 29 Detailed Schedule

**Branch:** Create a new branch named `planning/sprint29-task10` from `main`

**Priority:** Critical (3–4 hours) — **FINAL task; depends on Tasks 1–9**

**Objective:** Produce the detailed 14-day Sprint 29 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, sequencing the eight priorities + pipeline retest within the ≤ 12 hours/day budget, front-loading the cold-convex survey resolution and the REPLAN-gated tracks, and embedding the Day-5/Day-10 checkpoint re-solve.

**Unknowns Verified:** (integrates all 28 — see §"Appendix: Task-to-Unknown Mapping" in KNOWN_UNKNOWNS.md)

**Prerequisites (read before starting):**

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29 (Weeks 23–24)" (Priorities 1–8 + pipeline retest; 96–134h; ≤ 12h/day; Risk HIGH)
- `docs/planning/EPIC_4/SPRINT_28/PLAN.md` + `docs/planning/EPIC_4/SPRINT_28/prompts/PLAN_PROMPTS.md` (the day-by-day schedule + prompts format/template)
- All Task 2–9 outputs: `BASELINE_METRICS.md`, `COLD_CONVEX_COHORT_SURVEY.md`, the Phase-0 gates, `REPLAN_RISK_ASSESSMENT.md`, `TOOLING_READINESS_AUDIT.md`, `EPIC_5/CGE_DEGENERACY_SCOPING.md`, `PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md`, `BACKLOG_FIX_SURFACE_ANALYSIS.md`
- `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` (all 28 + the Task-to-Unknown mapping)

**Tasks to Complete:**

1. Day 0: baseline confirmation + Day-0 `kkt_residual.py` traces for the Critical unknowns (mine #1443, rocket #1462-residual, the cold-convex Case-b leads, #1146/#1143) — establishing the traced fix-surfaces (PR24) before any `src/`.
2. Days 1–13: sequence the eight priorities — front-load #1462 rocket (root cause known) + the cold-convex Case-b leads (Task-3 sized); schedule #1443 mine + the P7 AD-engine tracks with their REPLAN gates (Task 5); place the camcge Epic-5 write-up (Task 7, no `src/`) + the P8 infra (Task 8) in lower-contention slots; the objective-mismatch + offset-alias fixes (Task 9) as budget allows.
3. Checkpoints: Day 5 + Day 10 each run the Task-8 changed-golden re-solve + golden-staleness + PR25 tally; Day 13 the full 3× `PYTHONHASHSEED` retest + closeout.
4. Budget + slack: every day ≤ 12h; allocate the REPLAN slack per Task 5; record the fallback ordering.
5. Write `PLAN.md` + `prompts/PLAN_PROMPTS.md` in the Sprint-28 format; record the prep-task → PR mapping summary table.

**Deliverables:**

- `docs/planning/EPIC_4/SPRINT_29/PLAN.md` — 14-day schedule (Day 0 + Days 1–13), ≤ 12h/day
- `docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- The Day-5/Day-10 checkpoint re-solve embedded (Task 8)
- The REPLAN slack + fallback ordering (Task 5) reflected in the schedule
- The prep-task → PR mapping summary table
- Updated KNOWN_UNKNOWNS.md confirming all 28 unknowns are integrated into the schedule
- CHANGELOG.md updated with the Task 10 completion entry

**Known Unknowns Updates:** Confirm every unknown's verification status is reflected in the schedule (any ❌ WRONG drove a scope adjustment). Add a closing note to the KNOWN_UNKNOWNS §"Next Steps" that the prep phase is complete and the schedule integrates all 28.

**PREP_PLAN.md Updates:** §Task 10 → COMPLETE + Completed date; fill Changes + Result; check all Acceptance Criteria. Add the prep-task → PR summary table to the PREP_PLAN §Summary.

**CHANGELOG.md Update:** Under `### Sprint 29 Prep`, prepend a `- **Prep Task 10 COMPLETE (YYYY-MM-DD):** Sprint 29 14-day schedule (Day 0 + Days 1–13, ≤12h/day) + day-by-day prompts; front-loads the cold-convex Case-b leads + #1462 rocket, schedules the REPLAN-gated tracks with their exits, embeds the Day-5/Day-10 checkpoint re-solve. Sprint 29 is GO for Day 0. Integrates all 28 prep unknowns.` entry.

**Quality Gate:**
```bash
make typecheck && make lint && make format && make test
```
Docs-only — no Python expected. Run the gate regardless; do NOT commit until all pass.

**Commit Message Format:**
```
Complete Sprint 29 Prep Task 10: Plan Sprint 29 Detailed Schedule

Authored the 14-day Sprint 29 schedule (Day 0 + Days 1-13, <=12h/day) + day-by-day
prompts: front-loads the cold-convex Case-b leads + #1462 rocket, schedules the
REPLAN-gated tracks (#1443, #1462-residual, P7) with their Sprint-30 exits, and
embeds the Day-5/Day-10 checkpoint re-solve. Integrates all 28 prep unknowns.
Sprint 29 is GO for Day 0.

## Deliverables
- docs/planning/EPIC_4/SPRINT_29/PLAN.md
- docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md
- KNOWN_UNKNOWNS.md: all 28 integrated; prep phase complete
- PREP_PLAN.md: Task 10 -> COMPLETE + prep-task -> PR summary table
- CHANGELOG.md: Task 10 entry
```

**Pull Request:**
```bash
git push -u origin planning/sprint29-task10
gh pr create --title "Complete Sprint 29 Prep Task 10: Plan Sprint 29 Detailed Schedule" --body "$(cat <<'EOF'
## Summary

[Paste the commit message body here]

## Test plan

- [x] `make typecheck && make lint && make format && make test` all PASS (docs-only)
- [x] PLAN.md covers Day 0 + Days 1-13 with per-day budgets <=12h
- [x] PLAN_PROMPTS.md has a prompt per execution day; Day-5/Day-10 checkpoint re-solve embedded
- [x] All 28 prep unknowns integrated; prep-task -> PR mapping table included
- [x] Task 10 Acceptance Criteria all checked in PREP_PLAN.md
EOF
)"
```

**Then wait for reviewer comments.**

---

## Prep-Task → Branch → PR Summary

| Prep Task | Branch | Unknowns Verified | Depends On |
|-----------|--------|-------------------|------------|
| Task 2: Bucket-Provenance Baseline + Re-Baseline | `planning/sprint29-task2` | 8.2, 8.3 | None |
| Task 3: Cold-Convex Cohort Survey + Partition | `planning/sprint29-task3` | 4.1, 4.2, 4.3, 4.4 | Tasks 1, 2 |
| Task 4: Author Phase 0 Acceptance Gates | `planning/sprint29-task4` | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2 | Tasks 1, 3 |
| Task 5: REPLAN-Prone Track Risk Assessment | `planning/sprint29-task5` | 1.1, 2.2, 7.2, 7.4 | Task 4 |
| Task 6: Reusable-Tooling Readiness Audit | `planning/sprint29-task6` | 1.2, 2.4, 4.4, 8.4 | Task 1 |
| Task 7: camcge → Epic 5 Scoping Pre-Work | `planning/sprint29-task7` | 5.1, 5.2, 5.3 | Task 1 |
| Task 8: Checkpoint Re-Solve + Re-Baseline Design | `planning/sprint29-task8` | 8.1, 8.2 | Tasks 2, 6 |
| Task 9: Backlog Fix-Surface Analysis | `planning/sprint29-task9` | 6.1, 6.2, 6.3, 7.1, 7.3, 7.4 | Tasks 1, 3, 6 |
| Task 10: Plan Sprint 29 Detailed Schedule | `planning/sprint29-task10` | (all 28) | Tasks 1–9 |
