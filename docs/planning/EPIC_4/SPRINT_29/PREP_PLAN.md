# Sprint 29 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 29 begins
**Timeline:** Complete before Sprint 29 Day 1
**Goal:** Set up Sprint 29 for success — land the Sprint 28 Solve/Match carryforwards the Day-13 retest and Task-6 gates deferred (#1443 mine head-domain-offset, #1462 rocket presolve `_fx_`-multiplier warm-start, #1385 translation-timeout cross-terms), attack the **cold-convex robustness** gap (the ~24 non-convex models that match only warm-started), produce the camcge → Epic 5 scoping observation (#1330), and clear the highest-leverage AD/KKT cross-term backlog beyond the retrospective (#1447 maxmin, the objective-mismatch cohort #1332/#1247/#1239/#1236, the offset-alias gradient architecture #1146/#1143/#1112/#1111). Targets: Solve 107 → ≥ 109; Match maintain ≥ 92 / stretch ≥ 96; model_infeasible 7 → ≤ 5; Translate maintain ≥ 135; Tests ~4,935 → ≥ 4,960.

**Key Insight from Sprint 28:** Two Day-13-retest lessons reshape Sprint 29's prep (Sprint 28 retro §"What We'd Do Differently" #4 + #5). First, **golden-stability does not catch a broken solve** — the rocket #1462 regression hid behind passing golden-staleness byte-checks until the final re-solve, because the per-PR check only re-emits, it never re-solves. Second, the **headline Match jumped 62 → 92 mostly from a pipeline-*methodology* change** (the Day-9 presolve-retry-on-cold-mismatch broadening lifted +24 of the +30), not from cross-term fixes (genuine contribution +7), so the as-measured baseline silently drifted away from "genuine gains." Sprint 29 prep MUST therefore (a) re-baseline the Day-0 metrics with an explicit genuine-vs-methodology partition (PR25), (b) plan a mid-sprint **re-solve of the changed-golden set** at the Day-5/Day-10 checkpoints so a broken solve surfaces early, and (c) lean on the Sprint-28 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate) which Sprint 29 **reuses rather than rebuilds** — the diagnosis cost is therefore lower than Sprint 28's, provided a readiness audit confirms the tooling covers the new model classes (presolve warm-start `_fx_` multipliers, the cold-convex cohort, offset-alias gradients). A third carried-forward rule remains in force: **PR24** — prep records the *symptom + reproducer* only; the fix surface is a Day-0-trace hypothesis, never trusted from the prep doc (Sprint 27 proved prep surfaces wrong 4×; Sprint 28's Phase-0 gates caught the rest).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 29 inherits the Sprint 28 carryforward backlog of **five retrospective carryforwards** (Priorities 1–5 in `PROJECT_PLAN.md`): #1443 mine head-domain-offset MCP infeasibility; #1462 rocket presolve `_fx_`-multiplier warm-start + non-convex convergence (root cause already localized at the Sprint 28 Day-13 retest); #1385 translation-timeout Option-1 runtime-guard re-emit + `J_gᵀ·lam` cross-terms; the **cold-convex robustness** track (the ~24 non-convex models — otpop/cclinpts/camshape + the methodology-recovered cohort — that match only via the `--nlp-presolve` warm-start, whose cold MCP is non-convex-infeasible); and camcge #1330 → Epic 5 CGE Walras-law-degeneracy scoping. Three additional priorities (6–8) pull open backlog beyond the retrospective to fill the 14-day budget: the objective-mismatch cohort (#1332/#1247/#1239/#1236), the offset-alias gradient + dollar-condition AD architecture (#1146/#1143/#1112/#1111), and the checkpoint re-solve + re-baseline infrastructure.

Sprint 29 differs from Sprint 28 in one structural way: **Sprint 28 built the diagnostic tooling; Sprint 29 consumes it.** The KKT-residual Case-(a/b/c) discriminator (`scripts/diagnostics/kkt_residual.py`), the embedded-NLP-divergence detector (`scripts/diagnostics/check_presolve_divergence.py`), and the golden-staleness gate (`scripts/sprint_audit/check_golden_staleness.py`) are all on `main` and are the standard verification method in every Sprint 29 Phase-0 gate. The single new infrastructure deliverable (P8) closes the two gaps the tooling itself revealed at the Day-13 retest — a checkpoint re-solve so a broken solve can't hide behind a passing golden check, and a post-methodology re-baseline so the headline delta stays attributable.

This prep plan focuses on:

1. **Risk identification** — Sprint 29 Known Unknowns List covering the five carryforward fix-surfaces (PR24: hypotheses to re-trace at Day 0), the diagnosis-heavy REPLAN-prone tracks (#1443 cold-coupling, #1462 non-convex convergence, P7 AD-engine #1111/#1112), the cold-convex cohort's unknown Case-b/Case-c partition, and the camcge Epic-5 scope boundary.
2. **Day-0 baseline + re-baseline discipline (PR15 + PR17 + PR25 + the methodology re-baseline)** — Sprint 28 final → Sprint 29 Day 0 per-model bucket provenance, with every projected delta labeled genuine vs methodology-inflated and the Match baseline split into genuine (≈68) vs methodology (≈24) so Sprint 29 targets land on real transitions.
3. **Cold-convex cohort survey (Priority 4 foundation)** — run the KKT-residual harness across the ~24 warm-start-only models to partition Case-b (cold emit bug → fixable in Sprint 29) from Case-c (inherent non-convexity → Sprint 30 forcing strategies) BEFORE the schedule is set, because the partition size determines how much of P4 is achievable.
4. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — author the hand-derived KKT shape + traced fix-surface + harness-based verification method for #1443, #1462, #1385, #1447, the cohort, and #1146/#1143.
5. **Diagnosis-heavy track REPLAN assessment (PR16)** — apply hypothesis-validation to #1443 (deeper cold-coupling), #1462 (non-convex convergence beyond the warm-start), and the P7 AD-engine tracks; pin explicit Sprint 30 REPLAN exits.
6. **Reusable-tooling readiness audit** — confirm the three Sprint-28 diagnostic tools cover the new model classes and identify any minimal extension (e.g., the harness dual-transfer for `_fx_` multipliers, the property-test catalog's offset-alias shape).
7. **camcge → Epic 5 scoping pre-work (Priority 5)** — gather the Walras-degeneracy evidence and the CGE cohort, and stub the Epic 5 scoping doc, so the in-sprint task is write-up only (no `src/`).
8. **Checkpoint re-solve + re-baseline tooling design (Priority 8)** — design the `--resolve-changed` checkpoint mode and the PR25 re-baseline step that the two Day-13 lessons require.
9. **Backlog fix-surface analysis (Priorities 6 + 7)** — #1332/#1247/#1239/#1236 and #1146/#1143/#1112/#1111 patch-site hypotheses + property-test fixtures.
10. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 29 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 29 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 28 → Sprint 29 Bucket-Provenance Baseline + Re-Baseline Discipline (PR15 + PR17 + PR25) | Critical | 4–5h | None | All priorities — baseline metrics + methodology partition |
| 3 | Cold-Convex Cohort Survey + Case-(b/c) Partition (Priority 4 foundation) | High | 5–7h | Tasks 1, 2 | Priority 4 — cold-convex robustness; feeds P6/P7 |
| 4 | Author Phase 0 Acceptance Gates for the Carryforward + Backlog Tracks (PR20 + PR24 + PR27) | Critical | 5–7h | Tasks 1, 3 | Priorities 1–4, 6, 7 — primary scope-correctness gate |
| 5 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443, #1462, #1111/#1112; PR16) | High | 3–5h | Task 4 | Priorities 1, 2, 7 — REPLAN-prone tracks |
| 6 | Reusable-Tooling Readiness Audit (KKT-residual harness, divergence detector, golden-staleness gate) | High | 3–4h | Task 1 | All priorities — tooling reuse; feeds P8/P9 |
| 7 | camcge → Epic 5 Scoping Pre-Work (Priority 5) | Medium | 3–4h | Task 1 | Priority 5 — Epic 5 hand-off |
| 8 | Checkpoint Re-Solve + Post-Methodology Re-Baseline Tooling Design (Priority 8) | Medium | 3–4h | Tasks 2, 6 | Priority 8 — process recs #4 + #5 |
| 9 | Backlog Fix-Surface Analysis (#1332/#1247/#1239/#1236; #1146/#1143/#1112/#1111) | Medium | 3–4h | Tasks 1, 3, 6 | Priorities 6, 7 — fix-surface hypotheses |
| 10 | Plan Sprint 29 Detailed Schedule | Critical | 3–4h | Tasks 1–9 | All priorities — sprint planning |

**Total Estimated Time:** 35–48 hours (~4.5–6 working days)

**Critical Path:** Task 1 → Task 3 → Task 4 → Task 5 → Task 10 (the diagnosis chain — the cold-convex Case-b/Case-c partition (Task 3) sizes Priority 4 and informs the Phase-0 gates (Task 4), which feed the REPLAN assessment (Task 5) and the schedule).
**Secondary Path:** Task 2 → Task 8 → Task 10 (baseline + methodology partition → checkpoint re-solve + re-baseline design → schedule).
**Tertiary Path:** Task 1 → Task 6 → Task 9 → Task 10 (tooling readiness → backlog fix-surface analysis → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 6 + 7 (independent after Task 1); Task 9 follows Tasks 3 + 6; Task 8 follows Tasks 2 + 6.

---

## Task 1: Create Sprint 29 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~3.5h)
**Completed:** 2026-06-23
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive list of assumptions and unknowns for Sprint 29 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform every other prep task — particularly the cold-convex cohort survey (Task 3), the Phase-0 gates (Task 4), the REPLAN assessment (Task 5), and the reusable-tooling readiness audit (Task 6). It also carries forward the end-of-sprint unknowns from Sprint 28 (the §"KU Coverage Summary" in `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` plus any open items in `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 29's central risk is that it is **diagnosis-bound, not implementation-bound** — five of the eight priorities have a non-trivial "is this a fixable emit bug or an inherent non-convexity?" question that must be answered with the KKT-residual harness before any `src/` change. The Known Unknowns List must therefore frame every fix surface as a Case-(a/b/c)-classifiable hypothesis (PR24), and flag the three REPLAN-prone tracks (#1443 deeper cold-infeasible coupling, #1462 non-convex convergence beyond the `_fx_` warm-start, P7 AD-engine #1111/#1112) as Critical unknowns with a single-model hypothesis-validation as their verification (PR16), so the REPLAN decision (Task 5) is made on evidence.

The largest single unknown is the **cold-convex cohort partition size** (Unknown 4.x): Priority 4's achievable scope depends entirely on how many of the ~24 warm-start-only models are Case-b (fixable cold-emit bugs) vs Case-c (inherent non-convexity → Sprint 30). If the partition is mostly Case-c, Priority 4 collapses to a documentation/hand-off task and the freed budget should pre-allocate to Priorities 6/7. Surfacing this now (and resolving it in Task 3) prevents a mid-sprint scope surprise.

### Background

- Sprint 28 Retrospective: `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` (§"Sprint 29 Recommendations / Carryforwards" Priorities 1–5; §"What We'd Do Differently" #1–#5 → PR24/PR25 + the re-solve and re-baseline lessons; §"What Went Well" #1–#6; §"KU Coverage Summary")
- Sprint 28 Known Unknowns: `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` (Cat 1–10 — review for any open/end-of-sprint items)
- Sprint 29 scope: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29 (Weeks 23–24)" (Priorities 1–8 + Acceptance Criteria + Estimated Effort + Risk Level)
- Carryforward + backlog issues: `docs/issues/ISSUE_{1443,1385,1330}_*.md` (local) + GitHub #1462 (no local doc) — the five retrospective carryforwards — and the open backlog #1447, #1332, #1247, #1239, #1236, #1146, #1143, #1112, #1111. **Note:** #1462's root cause is already localized (the `nu_*_fx_h0` `_fx_`-multipliers are not warm-started) — its unknown is whether the warm-start is *sufficient* (Day-13 showed it is necessary-but-not-sufficient: objective 1.137 → 1.016, MS 5 persists).
- Sprint-28 diagnostic tooling that Sprint 29 reuses: `scripts/diagnostics/kkt_residual.py`, `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py`

### What Needs to Be Done

1. **Review Sprint 28 carryforward / end-of-sprint KUs.** Migrate any open items from `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` and the retro KU-coverage summary into Sprint 29 numbering with full text and forward-links to the Sprint 29 categories they drive.

2. **For each Priority area, brainstorm unknowns** (assumption / how-to-verify / priority / risk-if-wrong), organized by category aligned to the PROJECT_PLAN priorities:

   **Category 1 (#1443 mine — head-domain-offset MCP infeasibility):**
   - Is the cold MS-5 failure dominated by the `pr(k,l+1,i,j)` head-domain-offset dual-transfer (`pr.m` read at the wrong lead index — Case b), or by a deeper cold-infeasible complementarity/bound coupling (Case c)? **(Critical — PR16 hypothesis-validation; the Day-0 `kkt_residual.py` verdict decides PROCEED vs Sprint-30 REPLAN.)**
   - Does mine, a convex LP, have a *unique* KKT point so that a correct emit must cold-solve (no warm-start escape), unlike the non-convex cold-convex cohort?

   **Category 2 (#1462 rocket — `_fx_`-multiplier warm-start + non-convex convergence):**
   - Is the general `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` warm-start *sufficient* for rocket, or does the residual MS 5 require additionally suppressing the `piL/piU` bound-complementarity activation at `h0` introduced by the #1449 Layer-4 unfix? **(Critical — the warm-start is known-necessary-but-insufficient; the remaining gap is the unknown.)**
   - Does the general `_fx_`-multiplier warm-start regress any of the 13 presolve models that currently use the Layer-4 unfix (catmix/himmel16/polygon/… — verify byte-stability + solve-stability)?

   **Category 3 (#1385 — translation-timeout Option-1 cross-terms):**
   - Do the runtime-guard equation-body re-emit and the `J_gᵀ·lam` cross-terms have to land atomically (a re-emit without cross-terms = an inconsistent MCP)?
   - Which `translate_timeout` model (#1228 iswnm, #1185 mexls, #932 nebrazil, sarf) is the smallest viable Phase-0 target whose hand-derived cross-terms are tractable?

   **Category 4 (cold-convex robustness — the ~24 warm-start-only cohort):**
   - **What is the Case-b (fixable cold-emit bug) vs Case-c (inherent non-convexity) partition of the cohort?** **(Critical — sizes all of Priority 4; resolved by Task 3's harness survey.)**
   - Is #1447 maxmin's `stat_mindist` objective-variable cross-term defect representative of a shared Case-b shape across the cohort, or model-specific?
   - Which cohort members are convex (cold *should* solve → genuine emit bug) vs genuinely non-convex (cold infeasibility is expected → Sprint 30)? (The convexity DB `status` field is heuristic — cross-check with the harness verdict.)

   **Category 5 (camcge — Epic 5 CGE-degeneracy scoping):**
   - Is the camcge Walras-law singularity shared verbatim by the rest of the CGE cohort (#1354/#1355/#1317/#1331/#1251), or do they have distinct degeneracies? **(Determines whether the Epic-5 scoping doc covers one transformation or several.)**
   - Does the proposed numéraire-fix + redundant-row-drop transformation preserve the economic solution for at least one cohort model on paper (no `src/` — paper analysis only)?

   **Category 6 (objective-mismatch cohort #1332/#1247/#1239/#1236):**
   - For each, is the mismatch a Case-b emit bug (localizable stationarity/complementarity row) or a Case-c spurious-local-optimum / non-convexity? **(The harness verdict per model gates PROCEED.)**
   - Do any of the four share a root cause with a cold-convex cohort member (Task 3 overlap) or with the offset-alias gradient class (Category 7)?

   **Category 7 (offset-alias gradient + dollar-condition AD #1146/#1143/#1112/#1111):**
   - Is the himmel16/polygon offset-alias gradient defect fixable as a localized AD cross-term correction, or does it require the deeper AD-engine redesign (#1111 alias-aware differentiation / #1112 dollar-condition propagation) — i.e., the Sprint-30 architectural REPLAN? **(Critical — PR16 hypothesis-validation.)**
   - Does the Sprint-28 `test_ad_crossterm_shapes.py` property-test catalog already cover the offset-alias shape, or does it need a new fixture (Task 9)?

   **Category 8 (infrastructure P8 — checkpoint re-solve + re-baseline):**
   - What is the wall-clock cost of re-solving only the changed-golden set at a checkpoint (the `changed_emit_artifacts.py` diff sizes it), and does it fit the Day-5/Day-10 budget?
   - How should the re-baseline step represent the genuine-vs-methodology split so the headline Match delta stays attributable (PR25 extension)?

   **Category 9 (tooling readiness — reuse risk):**
   - Does `kkt_residual.py`'s dual-transfer mechanism handle the presolve `_fx_` multipliers (rocket) and the head-domain-offset multipliers (mine), or does it need a minimal extension (Task 6)?
   - Does `check_presolve_divergence.py`'s DB-reference + hard-fail/soft-`obj_gap` logic correctly classify the cold-convex cohort (they are *expected* to diverge cold), avoiding false hard-fails?

3. **Categorize, prioritize by risk, define a testable verification method and a verification deadline (Day 0 / Day N)** for each unknown — Critical/High unknowns get a Day-0 `kkt_residual.py` trace or single-model hypothesis-validation.

4. **Write the document** with all categories, the priority-definition legend, and the update/resolution template (matching the `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` structure).

### Changes

- Created `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` (28 unknowns across 8 categories aligned to the Sprint 29 priorities).
- Added the `## Appendix: Task-to-Unknown Mapping` table assigning every unknown to its verifying prep task (Tasks 2–10).

### Result

- **28 unknowns** authored: 7 Critical / 11 High / 6 Medium / 4 Low (~34h research time, parallelized across Tasks 2–10).
- Every carryforward/backlog fix-surface framed as a Day-0 `kkt_residual.py` hypothesis (PR24); the three REPLAN-prone Criticals (1.1 mine, 2.2 rocket residual, 7.2 offset-alias) and the cold-convex partition (4.1) flagged.
- The Task-to-Unknown mapping is the source for the "Unknowns Verified" metadata now added to Tasks 2–10 below.

### Verification

```bash
# Document exists
test -f docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md && echo "KU file present"

# 8 categories aligned to the PROJECT_PLAN priorities (expect 8)
grep -c '^# Category ' docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md

# Every numbered unknown carries a "How to Verify" section
n_unknowns=$(grep -cE '^## Unknown [0-9]' docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md)
n_verify=$(awk '/^## Template for New Unknowns/{exit} /^### How to Verify/{c++} END{print c+0}' docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md)
[ "$n_verify" -ge "$n_unknowns" ] && echo "all $n_unknowns unknowns have a verification method"

# Carryforward + backlog issues are referenced
grep -oE '#1(443|462|385|330|447|332|247|239|236|146|143|112|111)' docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md | sort -u | wc -l
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` with 25+ unknowns across 8+ categories
- Every carryforward/backlog fix-surface treated as a Day-0-traceable, harness-classifiable hypothesis (PR24 alignment)
- The three REPLAN-prone tracks (#1443, #1462-residual, #1111/#1112) flagged Critical with hypothesis-validation verification
- The cold-convex cohort partition flagged as the single largest scope unknown (Unknown 4.1), with Task 3 as its resolution
- Forward-links from each unknown to the Sprint 29 priority it drives

### Acceptance Criteria

- [x] Document created with 25+ unknowns across 8+ categories (28 unknowns across 8 categories)
- [x] All unknowns have assumption, verification method, priority, risk-if-wrong (all 8 fields per unknown)
- [x] All Critical/High unknowns have a Day-0 `kkt_residual.py` trace or single-model hypothesis-validation as their verification
- [x] Carryforward/backlog fix-surfaces framed as hypotheses per PR24 (not as established fact)
- [x] #1443 (1.1), #1462-residual (2.2), #1111/#1112 (7.2) flagged Critical (REPLAN-prone)
- [x] Cold-convex cohort partition flagged as the largest scope unknown (Unknown 4.1), routed to Task 3
- [x] Update/resolution template defined (§"Template for New Unknowns")

---

## Task 2: Sprint 28 → Sprint 29 Bucket-Provenance Baseline + Re-Baseline Discipline (PR15 + PR17 + PR25)

**Status:** ✅ COMPLETE
**Completed:** 2026-06-24
**Priority:** Critical
**Estimated Time:** 4–5 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 8.2, 8.3 (contributes to 1.1, 2.1, 4.1, 6.1 bucket confirmation)

### Objective

Establish the authoritative Sprint 29 Day-0 baseline from the Sprint 28 Day-13 retest, with a per-failing-model bucket provenance table, and — critically for Sprint 29 — split the Match baseline into its **genuine** (≈68, the cross-term fixes) and **methodology** (≈24, the Day-9 presolve-retry-on-cold-mismatch broadening) components so every Sprint 29 projected delta is labeled genuine vs methodology-inflated.

### Why This Matters

Sprint 28's headline Match jumped 62 → 92 (+30), but only +7 of that was genuine cross-term correctness; ~+24 was a one-time pipeline-methodology lift (the broadened presolve-retry now warm-start-validating already-correct non-convex emits), and −1 was the rocket stale-baseline correction. If Sprint 29 sets its target against the as-measured 92 without the partition, it will either (a) over-promise (treating the methodology lift as a repeatable trend) or (b) under-count its own genuine gains. The Sprint 28 retro §"What We'd Do Differently" #5 made this explicit: *re-baseline immediately after any pipeline-methodology change so the headline delta stays attributable.* This task is that re-baseline.

The committed DB is already fresh — the Sprint 28 Day-13 retest committed `gamslib_status.json` with Solve 107 / Match 92 / model_infeasible 7 — so unlike Sprint 28's Day-0 (which discovered a *stale* DB), Sprint 29 Day-0 = Sprint 28 final with no fresh retest required, provided `git diff <S28-close-SHA>..HEAD -- src/ scripts/` is empty.

### Background

- Sprint 28 final metrics + the genuine-vs-methodology decomposition: `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" (Match 62→92 = +7 genuine + ~24 methodology − 1 rocket; Solve 105→107) + `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` header + §"What We'd Do Differently" #5
- The committed pipeline DB: `data/gamslib/gamslib_status.json` (Solve 107, Match 92, model_infeasible 7 — fresh from the Day-13 retest)
- Bucket-provenance template: `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (the Sprint 28 §1 headline + §2 carryforward provenance table + §3 PR25 projection table)
- The methodology source: `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp` (the Day-9 #1387 PR broadening — the +24 driver)
- PR25 projection discipline: `CONTRIBUTING.md` §"Projection Discipline" (Sprint 28 Task 3)

### What Needs to Be Done

1. **Confirm Day-0 = Sprint 28 final.** `git diff <S28-close-SHA>..HEAD -- src/ scripts/` empty → reuse the committed DB; no fresh ~4h retest.
2. **Headline counts table** (142-model scope): Parse 142, Translate 135, Solve 107, Match 92, model_infeasible 7, path_syntax_error, path_solve_terminated, Tests ~4,935 — with the Sprint 29 target column and gap.
3. **Genuine-vs-methodology Match partition:** list the +24 methodology-recovered models (`model_optimal_presolve` + match where the cold golden is byte-identical to a pre-Day-9 baseline) vs the +7 genuine cross-term matches; record the "genuine baseline" (≈68) used for PR25 projection.
4. **Per-failing-model bucket provenance table** for the Sprint 29 target models: mine (model_infeasible), rocket (model_infeasible, NEW from the Day-13 stale-baseline correction), the cold-convex cohort (mismatch → warm-start-match), the objective-mismatch cohort, the offset-alias mismatches — Sprint 28 final bucket + gating issue.
5. **PR25 projection table:** for each Sprint 29 priority, label each projected Solve/Match delta as a genuine bucket-to-success transition vs a methodology/bucket-forward move; only genuine transitions count toward the target.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` (§1 headline counts, §2 genuine-vs-methodology Match split, §3 per-failing-model bucket provenance + PR25 projection, §4 scope freeze).
- Updated `KNOWN_UNKNOWNS.md` Unknowns 8.2 + 8.3 → ✅ VERIFIED and recorded the Day-0-bucket aspect of 1.1, 2.1, 4.1, 6.1.

### Result

- **Day-0 = Sprint 28 final confirmed:** `git diff 803a259a..HEAD -- src/ scripts/` empty; DB recomputes to **Solve 107 / Match 92 / model_infeasible 7** (canonical 142 scope); 0 absolute-path leaks. No fresh retest.
- **Re-baseline (Sprint-28 §5):** Match 92 = **genuine 68** + **~24 methodology** (the Day-9 presolve-retry-on-cold-mismatch broadening). Sprint 29 genuine floor = 68; as-measured maintain target = 92.
- **Major PR25 scope finding:** the objective-mismatch cohort (P6) has **largely already resolved** — quocge / prolog / sambal / qsambal all match on the Day-0 DB (the PROJECT_PLAN used stale pre-Sprint-28 objective values); only **hhfair (#1236)** still mismatches, so P6's live target is ≤ +1 Match. Priorities 4/7 (maxmin, himmel16, polygon) already match via warm-start — their fixes are **cold-robustness** (raise the genuine floor), not headline +Match. The only headline-moving genuine transitions are mine (#1443) + rocket (#1462), both `model_infeasible` (→ Solve ≥ 109, REPLAN-gated).

### Verification

```bash
# Baseline doc exists
test -f docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md && echo "baseline present"

# Day-0 = Sprint 28 final assertion (src/scripts unchanged since the S28 close)
git diff --stat <S28-close-SHA>..HEAD -- src/ scripts/ | tail -1   # <S28-close-SHA> = the Sprint 28 closeout merge SHA

# DB headline counts recomputed (canonical scope)
.venv/bin/python - <<'PY'
import json; db=json.load(open("data/gamslib/gamslib_status.json"))
items=list(db["models"].values()) if isinstance(db.get("models"),dict) else db["models"]
opt=sum(1 for m in items if (m.get("mcp_solve") or {}).get("outcome_category") in ("model_optimal","model_optimal_presolve"))
mat=sum(1 for m in items if (m.get("solution_comparison") or {}).get("comparison_status")=="match")
print("optimal(raw)=%d match(raw)=%d"%(opt,mat))
PY

# Genuine-vs-methodology partition present
grep -iE 'methodology|genuine' docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` with §1 headline counts, §2 carryforward bucket provenance, §3 PR25 projection table
- The Match baseline split into genuine (≈68) vs methodology (≈24) with the model lists
- Day-0 = Sprint 28 final confirmation (no fresh retest required)
- Per-priority projection labeling each delta genuine vs methodology/bucket-forward
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.2, 8.3

### Acceptance Criteria

- [x] Baseline doc created with headline counts, bucket provenance, and PR25 projection
- [x] Match baseline split genuine vs methodology with explicit model lists (genuine 68 / methodology ~24)
- [x] Day-0 = Sprint 28 final confirmed (git diff empty, no retest)
- [x] Every Sprint 29 projected Solve/Match delta labeled genuine vs methodology/bucket-forward
- [x] Sprint 29 targets (Solve ≥ 109 / Match ≥ 92 maintain, ≥ 96 stretch / model_infeasible ≤ 5) traced to specific model transitions
- [x] Unknowns 8.2, 8.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Cold-Convex Cohort Survey + Case-(b/c) Partition (Priority 4 Foundation)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 5–7 hours
**Completed:** 2026-06-24
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Survey the 30-model warm-start-only cohort — the models that match ONLY via the `--nlp-presolve` warm-start (their cold MCP fails/mismatches, so they *behave* non-convexly, though the DB convexity status labels all 30 convex) — and partition them into Case-b (a genuine cold-emit bug that the warm-start masks → fixable in Sprint 29) and Case-c (inherent non-convexity → cold infeasibility expected → Sprint 30 forcing strategies), using the Sprint-28 KKT-residual harness. This is a **survey/catalog task that must precede the Phase-0 gates (Task 4) and the schedule (Task 10)** because the Case-b count determines how much of Priority 4 is achievable.

### Why This Matters

Priority 4 (cold-convex robustness, 12–18h) is the single largest *NEW* Sprint 29 workstream, and its achievable scope is unknown until the cohort is partitioned. If most of the cohort is Case-c (genuinely non-convex — cold infeasibility is correct, not a bug), Priority 4 collapses to a documentation + Sprint-30 hand-off and ~10h of budget frees up for Priorities 6/7. If a meaningful subset is Case-b (the cold emit is *wrong*, like #1447 maxmin's missing `stat_mindist` cross-term, and the warm-start merely hides it), those are genuine emit-correctness fixes. **(Result update — see below: the survey found these Case-b models *already match warm*, so the fixes are Match-neutral cold-robustness that lift the genuine floor, NOT headline +Match/+Solve; the "+Match/+Solve" framing in this paragraph was the pre-survey expectation and is superseded by the Result.)** Resolving this in prep — rather than discovering it on Day 6 — is exactly the "survey before committing the schedule" discipline.

The cohort is also where the Sprint 28 Match number is most fragile: these are the +24 methodology-recovered models. A Case-b fix here is a *genuine* gain that survives any future methodology change, so partitioning them sharpens the PR25 genuine-vs-methodology accounting (Task 2).

### Background

- The cohort source: `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" (the ~24 methodology-recovered models: catmix, himmel16, weapons, harker, polygon, sambal, markov, worst, irscge, lrgcge, moncge, stdcge, like, robert, mathopt1/4, mingamma, paperco, qsambal, marco, etamac, cpack, maxmin, tforss + the genuine presolve fixes cclinpts/camshape). **Note:** `otpop` is *not* in the presolve-only cohort — Task 3 confirmed it matches **cold** (`model_optimal`), so it is excluded from the 30-model survey (per the acceptance criteria below).
- #1447 maxmin (the first concrete Case-b target): `docs/issues/ISSUE_1447_*.md` (`stat_mindist` missing the objective-variable cross-term — Case b, harness-localized in Sprint 28)
- The harness: `scripts/diagnostics/kkt_residual.py` (Case-(a/b/c) verdict + dual-transfer self-check)
- The convexity DB status (heuristic cross-check): `data/gamslib/gamslib_status.json` `convexity.status` (Task 3 verified the field is `convexity.status`, not `convexity.classification`)
- The presolve-retry mechanism that recovers them: `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp`

### What Needs to Be Done

1. **Enumerate the cohort** from the Day-13 retest DB: models with `outcome_category = model_optimal_presolve` + `comparison_status = match` whose **cold** solve failed/mismatched (the warm-start was required).
2. **Run `kkt_residual.py` on each** at its NLP KKT point; record the Case-(a/b/c) verdict, the max-residual row, and the dual-transfer self-check result.
3. **Cross-check convexity:** for each model, compare the harness verdict to the DB `convexity.status` and the cold model status — a *convex* model that cold-fails is a strong Case-b signal (the cold MCP should solve), while a *non-convex* model cold-failing is expected Case-c. (Task 3 found the field is `convexity.status`, not `convexity.classification`, and that it labels all 30 cohort members convex — so the harness verdict, not the DB status, is authoritative.)
4. **Partition + size:** produce the Case-b list (Sprint-29-fixable, ranked by residual-localizability) and the Case-c list (Sprint-30 forcing-strategy hand-off), with #1447 maxmin confirmed as the lead Case-b target.
5. **Feed forward:** flag any Case-b shapes shared with the objective-mismatch cohort (Task 9) or the offset-alias gradient class (P7), and record the partition size for the Task-10 schedule (P4 budget allocation).

### Changes

- Authored `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` — the 30-model cohort enumeration, per-model `kkt_residual.py` verdict + max-residual table, the Case-(b/c) partition, the three-fix-class shared-shape analysis, the Sprint-29-fixable ranked list, the convexity-seed audit, the detector soft-classification, and the Task-4/Task-10 budget implication.
- Filled KNOWN_UNKNOWNS.md Unknowns 4.1/4.2/4.3/4.4 Verification Results (all ✅ VERIFIED).

### Result

**The partition INVERTS the assumption: 21 Case b / 4 Case c / 3 Case a / 2 inconclusive** (of 30). Priority 4 is target-rich, not collapsing — the "mostly Case-c → free budget" path is refuted. **But all 21 Case-b already match warm**, so the fixes are Match-neutral cold-robustness (genuine floor 68 → up to ~89), not headline +Match. #1447 maxmin confirmed as the lead Case-b (`stat_mindist` rel = 1.0); the maxmin shape recurs (integer-residual objective/defining cross-term) across himmel16/like/catmix/polygon + the CGE `stat_pz` cluster → one shared `stationarity.py` Class-A fix plausibly lands ~6–8. The 5 CGE-family Class-B models (irscge/lrgcge/moncge/stdcge/marco) are gated to Task 4 (likely camcge #1330 / Epic 5). DB convexity is a non-signal (all 30 labeled convex); harness verdict authoritative. Detector soft-classifies the cohort (no false hard-fails).

### Verification

```bash
# Survey doc exists
test -f docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md && echo "survey present"

# The ~24 cohort enumerated from the DB (model_optimal_presolve + match)
.venv/bin/python - <<'PY'
import json; db=json.load(open("data/gamslib/gamslib_status.json"))
items=list(db["models"].values()) if isinstance(db.get("models"),dict) else db["models"]
coh=[m["model_id"] for m in items
     if (m.get("mcp_solve") or {}).get("outcome_category")=="model_optimal_presolve"
     and (m.get("solution_comparison") or {}).get("comparison_status")=="match"]
print("presolve-recovered matches:", len(coh)); print(sorted(coh))
PY

# Case-b vs Case-c partition recorded
grep -cE 'Case[- ]?b' docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md
grep -cE 'Case[- ]?c' docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md

# #1447 maxmin confirmed as a Case-b lead
grep -i 'maxmin' docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` enumerating the cohort with a per-model harness verdict
- The Case-b (Sprint-29-fixable) vs Case-c (Sprint-30 hand-off) partition with counts
- #1447 maxmin confirmed as the lead Case-b target + ≥1 additional Case-b candidate identified
- The partition size fed to Task 4 (gates) and Task 10 (P4 budget allocation)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [x] Cohort enumerated from the Day-13 DB: **30 models** with `model_optimal_presolve` + match. cclinpts and camshape **are** in this cohort; otpop is **excluded** (it matches **cold** as `model_optimal`, not via presolve).
- [x] `kkt_residual.py` run on each; Case-(a/b/c) verdict + max-residual row recorded
- [x] Convexity cross-check applied (DB convexity found to be a non-signal — all 30 labeled convex; harness authoritative)
- [x] Case-b / Case-c partition produced with counts (21/4/3/2) and a Sprint-29-fixable ranked list
- [x] #1447 maxmin + ≥1 more Case-b candidate confirmed (himmel16/like/catmix/polygon + 16 more)
- [x] Partition size handed to Tasks 4 and 10 (budget implication §8)
- [x] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Author Phase 0 Acceptance Gates for the Carryforward + Backlog Tracks (PR20 + PR24 + PR27)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 5–7 hours
**Completed:** 2026-06-25
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 3
**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2

### Objective

Author or refresh a Phase 0 acceptance gate in each target issue doc — a hand-derived KKT shape (where applicable), a *traced* fix-surface framed as a Day-0 hypothesis (PR24), and a `kkt_residual.py`-based verification method (PR27) — for the Sprint 29 implementation tracks: #1443 mine, #1462 rocket, #1385, the cold-convex Case-b leads (#1447 + the Task-3 list), the objective-mismatch cohort (#1332/#1247/#1239/#1236), and the offset-alias gradient pair (#1146/#1143).

### Why This Matters

The Phase 0 acceptance gate (PR20) is the primary mitigation against the Sprint 24–28 failure mode: a deep AD/non-convex fix that *looks* one-bug-deep but proves multi-bug mid-implementation. Sprint 28 proved every gated track either landed cleanly or REPLAN'd cheaply because the gate caught the mis-scope *before* `src/` effort. Sprint 29 is even more gate-dependent because five of eight priorities have a Case-b/Case-c question that *only* the harness can answer — so each gate must specify the exact `kkt_residual.py` command, the expected verdict for PROCEED, and the explicit Case-c REPLAN exit to Sprint 30.

For #1462 specifically, the gate is unusual: the fix is *already known* (the `nu_*_fx_h0` warm-start) but proven necessary-but-not-sufficient (Sprint 28 Day-13: 1.137 → 1.016, MS 5 persists). Its Phase 0 gate must therefore frame the *remaining* question (the `piL/piU`-at-`h0` activation) as the hypothesis, not the warm-start itself.

### Background

- The Phase-0 gate template (PR20 + PR24 amendments): `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (authored in Sprint 28 prep)
- The harness as verification (PR27): `scripts/diagnostics/kkt_residual.py` + its `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`
- Target issue docs: `docs/issues/ISSUE_{1443,1385,1447,1332,1247,1239,1236,1146,1143}_*.md` (local) + `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (created by Task 4 — rocket previously had no local doc)
- The cold-convex partition (Task 3 output) — supplies the Case-b lead list for the cohort gates
- Sprint 28 Day-13 rocket diagnosis (already-localized root cause): `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" + issue #1462

### What Needs to Be Done

1. **For each track, author/refresh `## Phase 0: Acceptance Gate`** with four `###` subsections: (a) hand-derived KKT shape or expected fix shape; (b) the *traced* fix-surface as a Day-0 hypothesis (PR24 — symptom + reproducer + a candidate surface explicitly labeled "to be confirmed by the Day-0 trace"); (c) the verification methodology — the exact `kkt_residual.py <model>` command + the PROCEED verdict + the Case-c REPLAN exit; (d) the acceptance criterion (MODEL STATUS / objective / residual threshold).
2. **#1443 mine:** gate on the `kkt_residual.py data/gamslib/raw/mine.gms` max-residual row deciding head-offset dual-transfer (Case b → PROCEED) vs cold non-convex coupling (Case c → Sprint-30 REPLAN).
3. **#1462 rocket:** gate the *residual* question — warm-start `nu_*_fx_h0` lands first (known), then the harness localizes whether the `piL/piU`-at-`h0` activation is the remaining MS-5 driver; include the 13-presolve-model byte/solve regression check.
4. **#1385:** gate on the hand-derived runtime-guard `stat_*` cross-terms for the smallest timeout target; atomic-landing note (re-emit + cross-terms together).
5. **Cohort gates (#1447 + Task-3 Case-b list; #1332/#1247/#1239/#1236; #1146/#1143):** each gets a per-model harness verdict as the PROCEED condition; #1146/#1143 additionally get a property-test fixture requirement (Task 9 / Sprint-28 `test_ad_crossterm_shapes.py`).

### Changes

- Authored `## Phase 0: Acceptance Gate` (4 `###` subsections + a `Traced Fix-Surface (Day-0)` line) in all 10 tracks: `docs/issues/ISSUE_{1443,1385,1447,1332,1247,1239,1146,1143,1236}_*.md` (9 existing) + a **new** `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (rocket had no local doc).
- Ran `kkt_residual.py` on the tracks lacking a Day-0 verdict (mine, rocket, hhfair, quocge, prolog) to anchor each gate's PROCEED condition.
- Verified KNOWN_UNKNOWNS Unknowns 1.1/1.2/1.3, 2.1/2.2/2.3, 3.1/3.2/3.3, 6.1, 7.1, 7.2 (4.2 was verified by Task 3).

### Result

**Day-0 harness verdicts:** mine **Case b** `stat_x` 1.33 (convex LP → no Case-c escape → genuine +1 Solve); rocket **Case b** `stat_step` 0.497 (`_fx_` warm-start necessary-but-insufficient, 1.137→1.016, MS5 persists → conditional, Task-5 decision); maxmin **Case b** `stat_mindist` 1.0, himmel16 `stat_area` 2.0, polygon `stat_theta` 0.49 (cold-robustness, Match-neutral). **Cohort sharpened:** quocge **Case b** `stat_pz` 1.0 *but matches cold* (CGE numéraire → Epic 5), prolog **Case a** (healthy, matches), sambal/qsambal **Case b** `stat_x` 0.78 (match warm), **hhfair harness-ERROR** (`$141`/`$257` — residual MCP won't compile; the **only** live +1 Match, verdict gated on the compile fix). #1385 gate is structural (atomic re-emit + cross-terms; no Day-0 harness target). Each gate frames its `file:line` fix-surface as a Day-0 hypothesis (PR24) with an explicit Case-c Sprint-30 REPLAN exit.

### Verification

```bash
# Phase 0 gate present in each local target issue doc (Task 4 created the local
# ISSUE_1462 doc, so #1462 is now included in the local loop)
for f in 1443 1462 1385 1447 1332 1247 1239 1236 1146 1143; do
  grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md 2>/dev/null || echo "MISSING: $f"
done

# Each gate cites the kkt_residual harness as its verification method, across ALL
# 10 Task-4 targets (#1385 names it as the post-fix verifier — structural gate)
for f in 1443 1462 1385 1447 1332 1247 1239 1236 1146 1143; do
  grep -lE 'kkt_residual\.py' docs/issues/ISSUE_${f}_*.md 2>/dev/null || echo "MISSING harness ref: $f"
done

# Each REPLAN-PRONE gate has an explicit Case-c / Sprint-30 REPLAN exit
# (the NO-OP / Case-a gates — quocge/prolog/sambal/qsambal — have no REPLAN branch by design)
grep -liE 'REPLAN|Sprint 30|Case[- ]?c' docs/issues/ISSUE_{1443,1462,1146,1143}_*.md 2>/dev/null
```

### Deliverables

- `## Phase 0: Acceptance Gate` authored/refreshed in #1443, #1462, #1385, #1447, #1332, #1247, #1239, #1236, #1146, #1143
- Each gate cites the exact `kkt_residual.py` command + PROCEED verdict + Case-c REPLAN exit
- #1462's gate frames the residual `piL/piU`-at-`h0` question as the hypothesis (warm-start known)
- The cold-convex Case-b leads (from Task 3) gated for Priority 4
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2

### Acceptance Criteria

- [x] Phase 0 gate present in all ten target issue docs (9 existing + new ISSUE_1462)
- [x] Each gate's fix-surface framed as a Day-0 hypothesis (PR24), not established fact
- [x] Each gate cites `kkt_residual.py` as the verification method (PR27) — except #1385 (structural; no Day-0 MCP to warm-start), which names the harness as the post-fix verifier
- [x] Each REPLAN-prone gate (#1443, #1462-residual, #1146/#1143) has an explicit Sprint-30 exit
- [x] #1462's gate distinguishes the known warm-start from the residual non-convex question
- [x] Cohort gates pull the Case-b leads from the Task-3 partition
- [x] Unknowns 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2, 6.1, 7.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443, #1462, #1111/#1112; PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 4
**Unknowns Verified:** 1.1, 2.2, 7.2, 7.4

### Objective

Apply the PR16 hypothesis-validation methodology to the three Sprint 29 tracks most likely to prove multi-bug or architectural — #1443 mine (deeper cold-infeasible complementarity/bound coupling beyond the head-offset dual-transfer), #1462 rocket (residual non-convex convergence beyond the `_fx_` warm-start), and Priority 7's AD-engine #1111/#1112 (offset-alias gradient possibly requiring an alias-aware-differentiation redesign) — and pin an explicit PROCEED/REPLAN signal and Sprint 30 exit for each.

### Why This Matters

Sprint 28's lower-effort bound assumed the diagnosis-heavy tracks partially slip; that assumption held (camcge REPLAN'd cleanly, but only because its REPLAN was pre-planned). Sprint 29 carries three tracks with the same shape, and the cost of an *unplanned* REPLAN mid-sprint is high (sunk implementation effort + schedule churn). A pre-sprint risk assessment that defines, per track, "what evidence at Day 0 means PROCEED vs REPLAN" converts those from surprises into scheduled decisions — exactly the Sprint 26/27/28 pattern where the gate caught the architectural ones cheaply.

### Why this is separate from Task 4: Task 4 authors the gate (the verification *mechanism*); Task 5 assesses the *risk* (the probability and cost of REPLAN, and the budget reallocation if it fires) so the schedule (Task 10) can pre-allocate slack and a fallback ordering.

### Background

- PR16 hypothesis-validation: `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (the Sprint 28 analog — #1387/#1390/camcge) as the structural template
- #1443 deeper coupling evidence: `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 4 — #1224" (mine cold MS-5, `x → 4e10`, 49 INFES) + issue #1443
- #1462 residual non-convexity: `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13" (warm-start 1.137 → 1.016, MS 5 persists) + issue #1462
- #1111/#1112 AD-engine architecture: GitHub #1111 / #1112 (no local doc) + `docs/issues/ISSUE_1146_*.md`, `ISSUE_1143_*.md`
- The harness Case-c verdict as the REPLAN trigger: `scripts/diagnostics/kkt_residual.py`

### What Needs to Be Done

1. **For each of the three tracks**, state the architectural hypothesis, the single-model validation experiment (the Day-0 `kkt_residual.py` trace + any quick prototype-then-revert probe), the PROCEED signal, the REPLAN signal, and the Sprint 30 exit scope.
2. **#1443:** PROCEED if the max-residual row is the head-offset dual-transfer (localizable, Case b); REPLAN to Sprint 30 if the residual is distributed across `comp_*`/bound rows (deeper coupling, Case c) — file the re-scoped diagnosis.
3. **#1462:** PROCEED if, after the `nu_*_fx_h0` warm-start, the residual MS-5 is the localizable `piL/piU`-at-`h0` activation; REPLAN if the non-convex convergence is intrinsic (warm-start lands near-optimal but PATH still diverges) — hand to Sprint 30 forcing strategies.
4. **#1111/#1112 (P7):** PROCEED if himmel16/polygon offset-alias gradients are a localized AD cross-term correction (property-test-guardable); REPLAN if the fix requires the alias-aware-differentiation / dollar-condition-propagation redesign (architectural) — file the Sprint-30 AD-engine track.
5. **Budget reallocation plan:** for each REPLAN, specify which lower-risk priority absorbs the freed budget (e.g., #1443 REPLAN → more cold-convex Case-b fixes; P7 REPLAN → objective-mismatch cohort depth).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Risk assessment doc exists
test -f docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md && echo "risk assessment present"

# Each of the three tracks has PROCEED + REPLAN signals
for t in 1443 1462 '111[12]'; do
  grep -iE "$t" docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md >/dev/null && echo "track $t covered"
done
grep -c -iE 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md

# Sprint 30 exits + budget-reallocation plan present
grep -iE 'Sprint 30|budget reallocat|absorb' docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` with per-track hypothesis, validation experiment, PROCEED/REPLAN signals, Sprint 30 exit
- A budget-reallocation plan for each possible REPLAN (which priority absorbs the freed hours)
- The three Critical REPLAN-prone unknowns (Task 1) resolved into scheduled decisions
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.2, 7.2, 7.4

### Acceptance Criteria

- [ ] Risk assessment created covering #1443, #1462, #1111/#1112
- [ ] Each track has an architectural hypothesis + single-model validation experiment
- [ ] Each track has explicit PROCEED and REPLAN signals tied to the harness verdict
- [ ] Each track has a Sprint 30 exit scope (the re-scoped filing)
- [ ] Budget-reallocation plan specified per REPLAN
- [ ] Feeds the Task-10 schedule's slack allocation and fallback ordering
- [ ] Unknowns 1.1, 2.2, 7.2, 7.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Reusable-Tooling Readiness Audit (KKT-Residual Harness, Divergence Detector, Golden-Staleness Gate)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 1.2, 2.4, 4.4, 8.4

### Objective

Audit the three diagnostic/CI tools Sprint 28 built and Sprint 29 reuses — `kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py` — against the new Sprint 29 model classes (presolve `_fx_`-multiplier warm-starts, head-domain-offset multipliers, the cold-convex cohort, offset-alias gradients), and identify any *minimal* extension needed before Day 1 so the in-sprint diagnosis runs on tooling that already covers the cases.

### Why This Matters

Sprint 29's effort estimate (96–134h, lower than Sprint 28's because the tooling exists) is only valid if the tooling actually handles the new cases. The KKT-residual harness's dual-transfer self-check, for example, was validated on the Sprint 28 carryforwards but not on the presolve `_fx_` multipliers (rocket) or the head-domain-offset multipliers (mine) — if its dual transfer mis-handles those, the Day-0 verdicts are unreliable and every dependent gate is undermined. Similarly, the presolve-divergence detector's hard-fail/soft-`obj_gap` logic must classify the cold-convex cohort as *expected* divergences (soft), not hard-fails, or it will flood the Day-5/Day-10 checkpoints with false alarms. Catching a tooling gap now (a small extension) is far cheaper than discovering it on Day 2 and blocking the whole diagnosis chain.

### Background

- KKT-residual harness: `scripts/diagnostics/kkt_residual.py` + `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` (Case-(a/b/c) verdict, dual-transfer self-check)
- Presolve-divergence detector: `scripts/diagnostics/check_presolve_divergence.py` (DB-reference comparison, hard-fail on abort/infeasible, soft `obj_gap` for non-convex local optima) + `.github/workflows/presolve-divergence.yml`
- Golden-staleness gate: `scripts/sprint_audit/check_golden_staleness.py` + the allowlist (6 out-of-scope + indus #1461) + `.github/workflows/golden-staleness.yml`
- The new model classes: rocket `_fx_` multipliers (#1462), mine head-domain-offset (#1443), the cold-convex cohort (Task 3), offset-alias gradients (#1146/#1143)

### What Needs to Be Done

1. **KKT-residual harness:** run it on rocket (`_fx_` multipliers) and mine (head-domain-offset) and confirm the dual-transfer self-check reports CONSISTENT; if it mis-transfers, scope the minimal fix (a one-line index-mapping extension, not a rewrite) as a Day-0 task.
2. **Presolve-divergence detector:** confirm the cold-convex cohort classifies as soft `obj_gap` (expected) not hard-fail; confirm rocket #1462 (the known abort/infeasible) is allowlisted or correctly hard-flagged; verify no false hard-fails on the cohort.
3. **Golden-staleness gate:** confirm the allowlist is current (indus #1461 still listed; korcge #1439 in the divergence allowlist); confirm the changed-golden-set diff (`changed_emit_artifacts.py`) is the right input for the Task-8 checkpoint re-solve.
4. **Gap list:** produce a short list of any required Day-0 tooling extensions (each scoped ≤ 1h), or confirm "no extensions needed — tooling covers all Sprint 29 classes."

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Readiness audit doc exists
test -f docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md && echo "audit present"

# The three tools are present on main
for t in scripts/diagnostics/kkt_residual.py scripts/diagnostics/check_presolve_divergence.py scripts/sprint_audit/check_golden_staleness.py; do
  test -f "$t" && echo "present: $t" || echo "MISSING: $t"
done

# Harness runs on rocket + mine (dual-transfer self-check)
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms 2>&1 | grep -iE 'case|residual|consistent' | head
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms   2>&1 | grep -iE 'case|residual|consistent' | head

# Gap list present (extensions or "none needed")
grep -iE 'extension|no extensions|gap' docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` with a per-tool readiness verdict for the new model classes
- A scoped gap list (Day-0 extensions ≤ 1h each) or a "no extensions needed" confirmation
- Confirmation the changed-golden-set diff is the right Task-8 checkpoint re-solve input
- Confirmation the divergence detector won't false-hard-fail the cold-convex cohort
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.4, 4.4, 8.4

### Acceptance Criteria

- [ ] Audit created covering all three Sprint-28 tools
- [ ] KKT-residual harness validated on rocket (`_fx_`) + mine (head-offset) dual transfer
- [ ] Presolve-divergence detector confirmed to soft-classify the cold-convex cohort (no false hard-fails)
- [ ] Golden-staleness allowlist confirmed current; changed-golden-set diff confirmed as Task-8 input
- [ ] Gap list produced (each extension ≤ 1h) or "no extensions needed"
- [ ] Feeds Tasks 8 (checkpoint re-solve) and 9 (property-test reuse)
- [ ] Unknowns 1.2, 2.4, 4.4, 8.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: camcge → Epic 5 Scoping Pre-Work (Priority 5)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Gather the evidence and structure for the camcge → Epic 5 scoping observation so the in-sprint Priority 5 task is a write-up only (no `src/`): assemble the Sprint-28 Day-11 Walras-degeneracy diagnosis, survey the CGE cohort (#1354/#1355/#1317/#1331/#1251 + #1330) for shared vs distinct degeneracies, and stub `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Why This Matters

Priority 5 is explicitly a *no-`src/`* Epic-5 hand-off — the Sprint 28 Day-11 Task-6 gate already proved camcge's MCP is structurally singular (CGE Walras-law redundancy, no price numéraire) with no general nlp2mcp emit fix. The risk is that the in-sprint task balloons into a CGE-formulation rabbit hole if the cohort's degeneracies aren't pre-surveyed. Pre-assembling the evidence (the harness CASE_C verdict, the Jacobian-rank finding, the affected cohort) and stubbing the scoping doc keeps Priority 5 to its 6–10h write-up budget and ensures the Epic 5 hand-off is actionable (a named transformation + a cohort list), not a vague "CGE is hard" note.

### Background

- The camcge Walras-degeneracy diagnosis: `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 11" (CASE_B `stat_mps` = fix-multiplier-transfer artifact; cold MCP MS-4 singular at iteration 0; `equil(i)` + `lmequil(lc)` linearly dependent given budget balance, no numéraire) + `docs/issues/ISSUE_1330_*.md` (REPLAN → Epic 5)
- The CGE cohort: `docs/issues/ISSUE_{1354,1355,1317,1331,1251}_*.md` (camcge/cesam2/twocge family) + `ISSUE_1070_*.md` (prolog CES singular Jacobian)
- The Task-6 gate methodology: `docs/planning/EPIC_4/SPRINT_28/PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md`
- Epic 5 destination: `docs/planning/EPIC_5/` (create the dir + scoping doc skeleton)

### What Needs to Be Done

1. **Assemble the diagnosis:** the harness CASE_C verdict + the basis-singularity report + the Jacobian-rank finding at the NLP point, with the precise linearly-dependent rows (`equil`/`lmequil`) and the missing numéraire.
2. **Survey the CGE cohort:** for #1354/#1355/#1317/#1331/#1251, record whether each shares the camcge Walras redundancy or has a distinct degeneracy (e.g., empty trade equations when `r=rr`, CES demand singular Jacobian) — paper analysis only, no `src/`.
3. **Name the transformation:** the proposed CGE-domain structural fix (single redundant-row drop + price-numéraire selection) and a paper argument that it preserves the economic solution for ≥1 cohort model.
4. **Stub the scoping doc:** create `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` with the diagnosis, cohort, proposed transformation, and open questions — so Priority 5's in-sprint work is filling it in, not researching from scratch.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Epic 5 scoping doc stub exists
test -f docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md && echo "Epic 5 scoping stub present"

# The CGE cohort is enumerated
grep -oE '#1(354|355|317|331|251|330)' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | sort -u

# The Walras-degeneracy diagnosis + the named transformation are recorded
grep -iE 'walras|numéraire|numeraire|redundant.*row|singular' docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md | head
```

### Deliverables

- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (stub) with the camcge diagnosis, CGE cohort survey, and named transformation
- A shared-vs-distinct degeneracy classification across #1354/#1355/#1317/#1331/#1251
- A paper argument that the proposed numéraire-fix transformation preserves the economic solution
- Priority 5 reduced to a write-up-only in-sprint task (no `src/`)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [ ] Epic 5 scoping doc stub created with the camcge Walras-degeneracy diagnosis
- [ ] CGE cohort surveyed (shared vs distinct degeneracies)
- [ ] Proposed transformation named with a solution-preservation argument
- [ ] #1330 confirmed moved to Epic 5 (no Sprint-29 `src/`)
- [ ] In-sprint Priority 5 scoped to write-up only
- [ ] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Checkpoint Re-Solve + Post-Methodology Re-Baseline Tooling Design (Priority 8)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 2, 6
**Unknowns Verified:** 8.1, 8.2

### Objective

Design the two Priority-8 infrastructure deliverables that the Sprint 28 Day-13 lessons require: a checkpoint **re-solve of the changed-golden set** (so a broken solve surfaces at Day 5/Day 10, not Day 13), and a **post-methodology re-baseline** step in the PR25 projection-discipline template (so the headline delta stays attributable after any pipeline-methodology change).

### Why This Matters

The rocket #1462 stale baseline cost Sprint 28 a full sprint of an undetected broken solve — its golden was byte-stable (passing the golden-staleness gate) while its *solve* silently regressed, only caught by the Day-13 full retest. The fix is cheap (re-solve only the models whose golden changed, using the `changed_emit_artifacts.py` diff as the at-risk list) but must be designed before Day 1 so it can be wired into the Day-5/Day-10 checkpoint flow. The re-baseline step is the codification of Task 2's genuine-vs-methodology partition into a repeatable process, so the next methodology change (whenever it comes) doesn't silently inflate the headline again.

### Background

- The Sprint 28 lessons: `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #4 (golden-stability ≠ correct solving — re-solve the changed-golden set) + #5 (re-baseline after a methodology change)
- The changed-golden-set diff: `scripts/sprint_audit/changed_emit_artifacts.py` (PR22; the at-risk list input)
- The checkpoint flow: `docs/planning/EPIC_4/SPRINT_28/PLAN.md` §"Pipeline Retest Cadence" (Day 5 / Day 10 / Day 13)
- The PR25 projection template: `CONTRIBUTING.md` §"Projection Discipline"
- The re-solve mechanism: `scripts/gamslib/run_full_test.py` (per-model `--model` re-solve)

### What Needs to Be Done

1. **Design the `--resolve-changed` checkpoint mode:** given the `changed_emit_artifacts.py` golden diff, re-solve only those models and diff their solve/compare buckets against the committed DB — flagging any model that regressed (was matching/optimal, now not). Specify the interface, the at-risk-list source, and the wall-clock budget (Task 6 confirmed the diff is the right input).
2. **Design the re-baseline step:** a PR25 template addition that, after any pipeline-methodology change (a retry-trigger or comparison-logic change), recomputes the genuine-vs-methodology split (Task 2) and records the new attributable baseline.
3. **Wire into the cadence:** specify where in the Day-5 / Day-10 checkpoint the re-solve runs, and the GO/NO-GO criterion (any changed-golden model that regressed = investigate before proceeding).
4. **Document** the design in a Priority-8 design doc (mirroring the Sprint-28 priority-design-doc convention).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Priority 8 design doc exists
test -f docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md && echo "P8 design present"

# The changed-golden-set diff tool exists (the at-risk-list source)
test -f scripts/sprint_audit/changed_emit_artifacts.py && echo "changed-artifacts tool present"

# Design covers both the re-solve and the re-baseline
grep -iE 'resolve-changed|re-solve|changed.golden' docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md | head
grep -iE 're-baseline|methodology' docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` with the `--resolve-changed` interface + the re-baseline step
- The at-risk-list source confirmed (`changed_emit_artifacts.py` diff) + the checkpoint wall-clock budget
- The GO/NO-GO criterion (any changed-golden model regressed → investigate)
- The PR25 re-baseline template addition specified
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.1, 8.2

### Acceptance Criteria

- [ ] Priority 8 design doc created
- [ ] `--resolve-changed` checkpoint mode specified (interface, at-risk-list source, budget)
- [ ] Re-baseline step specified as a PR25 template addition
- [ ] Wired into the Day-5 / Day-10 checkpoint cadence with a GO/NO-GO criterion
- [ ] Implements both Sprint-28 Day-13 lessons (#4 re-solve, #5 re-baseline)
- [ ] Unknowns 8.1, 8.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Backlog Fix-Surface Analysis (#1332/#1247/#1239/#1236; #1146/#1143/#1112/#1111)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 3, 6
**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3, 7.4

### Objective

Pre-analyze the Priority-6 (objective-mismatch cohort #1332/#1247/#1239/#1236) and Priority-7 (offset-alias gradient + dollar-condition AD #1146/#1143/#1112/#1111) fix surfaces as Day-0 hypotheses (PR24), identify any shared root causes with the cold-convex cohort (Task 3) or each other, and plan the property-test fixtures (extending the Sprint-28 `test_ad_crossterm_shapes.py` catalog) that guard the P7 AD changes.

### Why This Matters

Priorities 6 and 7 are the "fill the 14-day budget" backlog beyond the retrospective carryforwards, so they are the most likely to be skipped if the carryforwards over-run — which means their prep must be *cheap to pick up*: a Day-0 hypothesis + a property-test fixture plan, ready to execute if the budget allows. Pre-analysis also surfaces consolidation: if #1146 himmel16 and #1143 polygon share the offset-alias gradient root cause (likely), one fix lands two models; if any objective-mismatch cohort member overlaps a cold-convex Case-b shape (Task 3), the fix is already scoped. This consolidation is exactly what keeps Sprint 29's backlog tractable within the budget.

### Background

- Objective-mismatch cohort: `docs/issues/ISSUE_{1332,1247,1239,1236}_*.md` (quocge 25.683 vs 25.5085; prolog −73.5 vs −0.0; sambal/qsambal 1028 vs 3.97; hhfair 54.9 vs 87.2)
- Offset-alias gradient: `docs/issues/ISSUE_{1146,1143}_*.md` (himmel16 cyclic 43%; polygon 100%) + the AD-engine GitHub #1112 / #1111 (no local doc; dollar-condition propagation; alias-aware differentiation)
- The Sprint-28 property-test catalog: `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/shape{1..6}_*.gms` (extend with the offset-alias shape)
- The harness for per-model verdicts: `scripts/diagnostics/kkt_residual.py`
- The cold-convex partition (Task 3) — cross-check for shared root causes

### What Needs to Be Done

1. **Objective-mismatch cohort:** for each of #1332/#1247/#1239/#1236, record the harness Case-(a/b/c) verdict (from Task 3's runs where overlapping, else fresh), the candidate fix-surface as a Day-0 hypothesis (PR24), and whether it shares a root cause with a cold-convex Case-b model.
2. **Offset-alias gradient:** determine whether #1146 himmel16 and #1143 polygon share the offset-alias gradient root cause (likely one fix → two models); frame the fix-surface as a localized AD cross-term correction hypothesis vs the #1111/#1112 architectural redesign (the Task-5 REPLAN trigger).
3. **Property-test fixture plan:** specify the new `tests/fixtures/crossterm_shapes/shape7_offset_alias_*.gms` fixture (and any others) that reproduces the himmel16/polygon shape and would guard the P7 fix, extending the Sprint-28 catalog.
4. **Consolidation map:** record which fixes land multiple models (himmel16+polygon; any cohort+cold-convex overlap) so Task 10 can order them for maximum coverage per fix.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Backlog fix-surface analysis doc exists
test -f docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "backlog analysis present"

# All eight backlog issues referenced
grep -oE '#1(332|247|239|236|146|143|112|111)' docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md | sort -u | wc -l

# Property-test fixture plan + consolidation map present
grep -iE 'shape7|offset.alias|fixture' docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md | head
grep -iE 'consolidat|one fix|two models|shared root' docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` with per-issue Day-0 fix-surface hypotheses (PR24)
- The himmel16/polygon shared-root-cause determination + the localized-vs-architectural split (Task-5 trigger)
- A property-test fixture plan extending `test_ad_crossterm_shapes.py`
- A consolidation map (which fixes land multiple models)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4

### Acceptance Criteria

- [ ] Analysis doc created covering all eight backlog issues
- [ ] Each fix-surface framed as a Day-0 hypothesis (PR24), not established fact
- [ ] himmel16/polygon shared-root-cause determined; localized-vs-architectural split recorded
- [ ] Property-test fixture plan specified (shape7+ offset-alias)
- [ ] Consolidation map produced (multi-model fixes identified)
- [ ] Shared root causes with the cold-convex cohort (Task 3) cross-checked
- [ ] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3, 7.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 29 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 29 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–9
**Unknowns Verified:** (integrates all 28 — see §"Appendix: Task-to-Unknown Mapping" in KNOWN_UNKNOWNS.md)

### Objective

Produce the detailed 14-day Sprint 29 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, sequencing the eight priorities + pipeline retest within the ≤ 12 hours/day budget, front-loading the cold-convex survey resolution and the REPLAN-gated tracks, and embedding the Day-5/Day-10 checkpoint re-solve.

### Why This Matters

The schedule is the synthesis of every prior prep task: the Known Unknowns (Task 1) set the Day-0 trace agenda, the baseline (Task 2) sets the targets, the cold-convex partition (Task 3) sizes Priority 4, the Phase-0 gates (Task 4) and REPLAN assessment (Task 5) order the diagnosis-heavy tracks with their exits, the tooling audit (Task 6) confirms no Day-0 tooling build is needed, and the checkpoint re-solve design (Task 8) embeds the Day-13-lesson safeguard. A schedule that respects the dependency order — survey before fix, gate before implement, re-solve at checkpoints — is what converts the prep investment into an executable sprint.

### Background

- Sprint 29 scope + effort: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29 (Weeks 23–24)" (Priorities 1–8 + pipeline retest; 96–134h; ≤ 12h/day; Risk HIGH)
- Structural template: `docs/planning/EPIC_4/SPRINT_28/PLAN.md` + `docs/planning/EPIC_4/SPRINT_28/prompts/PLAN_PROMPTS.md` (the day-by-day schedule + prompts format)
- The prep outputs (Tasks 1–9): KNOWN_UNKNOWNS, BASELINE_METRICS, COLD_CONVEX_COHORT_SURVEY, the Phase-0 gates, REPLAN_RISK_ASSESSMENT, TOOLING_READINESS_AUDIT, the Epic-5 stub, the P8 design, the backlog analysis
- The checkpoint cadence: Day 5 (Checkpoint 1) + Day 10 (Checkpoint 2) + Day 13 (final retest) with the new Task-8 changed-golden re-solve

### What Needs to Be Done

1. **Day 0:** baseline confirmation + Day-0 `kkt_residual.py` traces for the Critical unknowns (mine #1443, rocket #1462-residual, the cold-convex Case-b leads, #1146/#1143) — establishing the traced fix-surfaces (PR24) before any `src/`.
2. **Days 1–13:** sequence the eight priorities — front-load #1462 rocket (root cause known, highest-confidence +1 Solve/+1 Match) and the cold-convex Case-b leads (Task-3 sized); schedule #1443 mine and the P7 AD-engine tracks with their REPLAN gates (Task 5); place the camcge Epic-5 write-up (Task 7, no `src/`) and the P8 infra (Task 8) in lower-contention slots; the objective-mismatch cohort + offset-alias fixes (Tasks 9) as budget allows.
3. **Checkpoints:** Day 5 (Checkpoint 1) + Day 10 (Checkpoint 2) each run the Task-8 changed-golden re-solve + golden-staleness + PR25 tally; Day 13 the full 3× `PYTHONHASHSEED` retest + closeout.
4. **Budget + slack:** keep every day ≤ 12h; allocate the REPLAN slack per Task 5; record the fallback ordering if a diagnosis-heavy track REPLANs early.
5. **Write `PLAN.md` + `prompts/PLAN_PROMPTS.md`** in the Sprint-28 format; record this prep plan's task→PR mapping in the summary table.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Schedule + prompts exist
test -f docs/planning/EPIC_4/SPRINT_29/PLAN.md && echo "PLAN present"
test -f docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md && echo "PROMPTS present"

# Day 0–13 covered
grep -cE '^#+ .*Day [0-9]' docs/planning/EPIC_4/SPRINT_29/PLAN.md

# Checkpoint re-solve embedded at Day 5 / Day 10
grep -iE 'changed.golden|re-solve|Checkpoint' docs/planning/EPIC_4/SPRINT_29/PLAN.md | head

# ≤12h/day budget respected (no day exceeds 12h)
grep -iE 'Day [0-9].*1[3-9]h|~1[3-9] ?h' docs/planning/EPIC_4/SPRINT_29/PLAN.md || echo "no day exceeds 12h"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_29/PLAN.md` — 14-day schedule (Day 0 + Days 1–13), ≤ 12h/day
- `docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts
- The Day-5/Day-10 checkpoint re-solve embedded (Task 8)
- The REPLAN slack + fallback ordering (Task 5) reflected in the schedule
- The prep-task → PR mapping summary table
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns (all 28 — see the Task-to-Unknown Mapping)

### Acceptance Criteria

- [ ] `PLAN.md` covers Day 0 + Days 1–13 with per-day budgets ≤ 12h
- [ ] `prompts/PLAN_PROMPTS.md` has a prompt per execution day
- [ ] Day-0 traces scheduled for all Critical unknowns before any `src/`
- [ ] Diagnosis-heavy tracks (#1443, #1462-residual, P7) scheduled with their REPLAN gates + exits
- [ ] Day-5/Day-10 checkpoints run the changed-golden re-solve + golden-staleness + PR25 tally
- [ ] Day-13 full 3× `PYTHONHASHSEED` retest + closeout scheduled
- [ ] Prep-task → PR mapping table included
- [ ] Unknowns (all 28 — see the Task-to-Unknown Mapping) verified and updated in KNOWN_UNKNOWNS.md

---

## Summary

### Prep Task → Deliverable Map

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 1 | Known Unknowns List | `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` | ✅ |
| 2 | Bucket-Provenance Baseline + Re-Baseline | `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` | 🔵 |
| 3 | Cold-Convex Cohort Survey + Partition | `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` | 🔵 |
| 4 | Phase 0 Acceptance Gates (10 tracks) | `docs/issues/ISSUE_*.md` Phase-0 sections | 🔵 |
| 5 | REPLAN Risk Assessment | `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` | 🔵 |
| 6 | Reusable-Tooling Readiness Audit | `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` | 🔵 |
| 7 | camcge → Epic 5 Scoping Pre-Work | `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (stub) | 🔵 |
| 8 | Checkpoint Re-Solve + Re-Baseline Design | `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` | 🔵 |
| 9 | Backlog Fix-Surface Analysis | `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` | 🔵 |
| 10 | Sprint 29 Detailed Schedule | `docs/planning/EPIC_4/SPRINT_29/PLAN.md` + `prompts/PLAN_PROMPTS.md` | 🔵 |

**Total prep effort ≈ 35–48 h** (~4.5–6 working days).

### Verification

```bash
# All prep artifacts present
ls docs/planning/EPIC_4/SPRINT_29/

# Phase-0 gates on the Sprint 29 tracks
for f in 1443 1385 1447 1332 1247 1239 1236 1146 1143; do grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md 2>/dev/null; done  # #1462 GitHub-only

# Epic 5 hand-off stub
test -f docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md && echo "Epic 5 stub present"

# Schedule fits the budget
grep -Ei 'Day [0-9]' docs/planning/EPIC_4/SPRINT_29/PLAN.md | head -20
```

**When all critical items checked: Sprint 29 ready to begin.**

### Success Criteria

This prep plan succeeds if Sprint 29 starts with:

1. **No unverified fix-surfaces taken as fact** — every carryforward/backlog surface is a Day-0 `kkt_residual.py` hypothesis (PR24), so the Sprint 24–27 mis-scope cannot recur silently.
2. **An attributable, re-baselined target** — the Match baseline is split genuine (≈68) vs methodology (≈24), so Sprint 29's Solve ≥ 109 / Match ≥ 96-stretch is set on genuine transitions (PR25), not on the one-time presolve-retry lift.
3. **A sized cold-convex workstream** — the Case-b/Case-c partition (Task 3) is known before the schedule, so Priority 4's achievable scope (and the freed budget if it's mostly Case-c) is planned, not discovered.
4. **Planned REPLANs, not surprises** — the three diagnosis-heavy tracks (#1443, #1462-residual, #1111/#1112) have explicit PROCEED/REPLAN signals + Sprint 30 exits + budget reallocation (Task 5).
5. **A broken-solve safeguard** — the Day-5/Day-10 checkpoint re-solve of the changed-golden set (Task 8) ensures a rocket-style stale baseline cannot hide behind a passing golden check until Day 13.
6. **Reused, not rebuilt, tooling** — the Sprint-28 KKT-residual harness, divergence detector, and golden-staleness gate are audited ready (Task 6), so Sprint 29 spends its budget on fixes, not infrastructure.

**Estimated prep investment:** 4.5–6 days
**Expected benefit:** avoids the cold-convex scope surprise + the diagnosis-heavy REPLAN churn on three tracks, keeps the headline Match honestly attributable after the Sprint-28 methodology lift, and closes the broken-solve detection gap that cost Sprint 28 the undetected rocket regression.

---

## Appendix: Document Cross-References

### Sprint 29 Scope + Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 29 (Weeks 23–24): Sprint 28 Carryforward — Presolve/Warm-Start Robustness, Cold-Convex MCP Convergence & AD Cross-Term Cleanup" (Priorities 1–8 + pipeline retest + Acceptance Criteria + Estimated Effort + Risk Level + footnote ⁸ re-baseline note)
- `docs/planning/EPIC_4/GOALS.md` (Epic 4: Full GAMSLIB LP/NLP/QCP coverage; Solve Completion + Solution Matching themes)

### Sprint 28 Source Material
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_RETROSPECTIVE.md` (§"Sprint 29 Recommendations / Carryforwards" Priorities 1–5; §"What We'd Do Differently" #1–#5 → PR24/PR25 + the re-solve (#4) and re-baseline (#5) lessons; §"What Went Well" #1–#6; §"KU Coverage Summary")
- `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` (per-day entries; §"Day 13" the genuine-vs-methodology Match decomposition + the rocket #1462 stale-baseline + the cold-convex cohort list; §"Day 11" camcge Walras-degeneracy; §"Day 4" mine cold MS-5)
- `docs/planning/EPIC_4/SPRINT_28/BASELINE_METRICS.md` (bucket-provenance template for Task 2)
- `docs/planning/EPIC_4/SPRINT_28/KNOWN_UNKNOWNS.md` (open-item migration source for Task 1)
- `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` + `PLAN.md` + `prompts/PLAN_PROMPTS.md` (structural templates for Tasks 1–10)
- `docs/planning/EPIC_4/SPRINT_28/PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md`, `PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md`, `PRIORITY_8_GOLDEN_STALENESS_DESIGN.md`, `PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md` (tooling + REPLAN templates)

### Carryforward + Backlog Issues (Phase-0 gate targets)
- `docs/issues/ISSUE_1443_*.md` (P1 — mine head-domain-offset MCP infeasibility)
- #1462 (P2 — rocket presolve `_fx_`-multiplier warm-start + non-convex convergence; local doc `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` created by Task 4 — root cause localized in `docs/planning/EPIC_4/SPRINT_28/SPRINT_LOG.md` §"Day 13")
- `docs/issues/ISSUE_1385_*.md` (P3 — translation-timeout Option-1 runtime-guard cross-terms)
- `docs/issues/ISSUE_1447_*.md` (P4 — maxmin `stat_mindist` cold-emit Case-b lead)
- `docs/issues/ISSUE_1330_*.md` (P5 — camcge → Epic 5 CGE Walras degeneracy)
- `docs/issues/ISSUE_{1332,1247,1239,1236}_*.md` (P6 — objective-mismatch cohort: quocge / prolog / sambal-qsambal / hhfair)
- `docs/issues/ISSUE_{1146,1143}_*.md` + GitHub #1112 / #1111 (P7 — offset-alias gradient + dollar-condition / alias-aware AD architecture)
- `docs/issues/ISSUE_{1354,1355,1317,1331,1251,1070}_*.md` (CGE cohort context for Task 7)
- GitHub #1461 (indus cross-platform emit determinism — no local doc; tracked in `scripts/sprint_audit/golden_staleness_allowlist.txt`; golden-staleness allowlist context for Task 6)

### Related Research / Tooling
- `scripts/diagnostics/kkt_residual.py` (KKT-residual Case-(a/b/c) harness — Tasks 3, 4, 5, 6)
- `scripts/diagnostics/check_presolve_divergence.py` (embedded-NLP-divergence detector — Task 6)
- `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/changed_emit_artifacts.py` (golden-staleness gate + changed-artifact diff — Tasks 6, 8)
- `scripts/gamslib/run_full_test.py` (`_cold_objective_mismatches_nlp` — the methodology source for Task 2; per-model re-solve for Task 8)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (AD cross-term property-test catalog — Task 9)
- `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` (Case-c non-convexity context for the cold-convex partition)

### Process / Tooling
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (PR20 template + PR24/PR25 amendments; extended by Task 8 with the re-baseline step)
- `data/gamslib/gamslib_status.json` (fresh Day-13 retest DB — Solve 107 / Match 92 / model_infeasible 7; Task 2 baseline source)
- `data/gamslib/mcp/*_mcp.gms`, `*_mcp_presolve.gms` (golden artifacts for the Task-6/Task-8 checks)
