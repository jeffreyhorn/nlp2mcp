# Sprint 32 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 32 begins
**Timeline:** Complete before Sprint 32 Day 1
**Goal:** Set up Sprint 32 for success — land the Sprint 31 Solve/Match carryforwards the Day-13 closeout REPLAN'd, each of which now carries a *precisely-pinned root cause* rather than an open question (`docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` §4). The core is the **mine head-offset 4th bound-complementarity site** (#1443), which Sprint 31 REPLAN'd on Day 3 after the head-offset IR foundation (`EquationDef.head_domain_offsets` + the Site-2 dual transfer) landed but a residual 4th site remained — the LP bound-duals warm-started into `piU_x` don't satisfy the emitted `stat_x` at bound-active rows. Alongside it: the **sarf 4-D `task`-variable stationarity sparsification** (#1385 — Sprint 31 Day 8 found the 2-D constraint gate fires but sarf still times out on the **369,024-instance** 4-D `task(g,t,mn,mn)` `stat_task` enumeration, not the 1,152 constraints); the **camcge dual-consistent Walras / CASE_B `stat_mps`** (#1330 → Epic 5 — Sprint 31 Days 6–7 re-diagnosed camcge as CASE_B, the `nu_mps_fx` fixing-multiplier defect, NOT the clean Walras singular-Jacobian case); the **rocket PATH-consultation forcing input** (#1462 — Sprint 31 Day 11 exhausted the division-by-variable reformulation; the intrinsic non-convergence is now a *ruled-out-lever* question for the renumbered Sprint 33 consultation); and the **hhfair + CGE-cluster Case-c documentation** (#1236 — Sprint 31 Day 10 control-refuted the ν_objective reduction, documenting the objective-defining-intermediate-variable family as genuine non-convex Case-c). Targets: Solve 107 → ≥ 109; Match maintain ≥ 92 / genuine floor 74 → ≥ 75; model_infeasible 7 → ≤ 5; Translate maintain ≥ 135 (stretch +1 via #1385 sarf); Tests 5,074 → ≥ 5,080.

**Key Insight from Sprint 31:** Sprint 32 is **specification-bound, not diagnosis-bound** — every carryforward inherits a Sprint-31 *precisely-pinned* root cause (mine's bound-complementarity localization; sarf's 369K finding; camcge's `stat_mps` CASE_B verdict; rocket's exhausted-lever survey; the CGE-cluster Case-c control), so Sprint 32 implements against specifications rather than re-diagnosing. But two structural lessons from Sprint 31 dominate the prep: (1) **the banked root cause is still a hypothesis that must survive a control experiment before any high-blast-radius `src/` change** — Sprint 31 *REPLAN'd all five* deep tracks after a control or harness re-diagnosis refuted the original design premise (the mine "MS-1 17500" measurement error; the camcge CASE_B-not-Walras verdict; the sarf 369K-not-1,152 finding; the P5 inert-reduction control; the rocket exhausted-lever survey); the single-point harness residual and the banked fix-surface are systematically misleading for non-convex / objective-defining-intermediate-variable shapes. (2) **Always assert `modelstat` before reading an objective off a solve** (the Sprint-31 Day-2 measurement error: relaxing `x.up=inf` produced 34 unmatched-variable errors, so the "MS-1 17500" was the embedded LP, not the MCP). Sprint 32 prep MUST therefore (a) turn each pinned root cause into a **design the implementation follows** — most critically the P1 mine **bound-multiplier derivation** design (the 4th site is the deepest track and gates the +1 Solve) and the P2 sarf **O(active-instances) `stat_task` sparsification** design; (b) front-load the **tractability probes** the Sprint-30/31 retros said would have re-allocated budget earlier (the P1 bound-dual reconciliation depth; the P2 369K→active sparsification budget; the P3 Epic-5 `stat_mps`-before-Walras ordering); and (c) keep the PR24/PR27 control-experiment-before-implement gate as the standing discipline on P1/P2/P3/P4/P5.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

> **Note on location.** Sprint 32 is defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32 (Weeks 29–30)". This prep plan is filed under `EPIC_4/SPRINT_32/` alongside the Sprint-30/31 prep plans it mirrors (the request's `EPIC_11` path does not exist; `EPIC_4` is where the Sprint 32 entry and all sibling sprint artifacts live).

---

## Executive Summary

Sprint 32 inherits the five Sprint-31 REPLAN'd carryforwards (Priorities 1–5 in `PROJECT_PLAN.md` §"Sprint 32"): the mine head-offset 4th bound-complementarity site (#1443); the sarf 4-D `task`-variable stationarity sparsification (#1385); the camcge #1330 dual-consistent Walras / CASE_B `stat_mps` (Epic 5); the rocket #1462 PATH-consultation forcing input; and the hhfair + CGE-cluster Case-c formalization (#1236). Priority 6 pulls the adjacent offset-alias / symbolic-emit backlog + a residual failure-cohort re-triage; Priority 7 (infrastructure) extends the AD cross-term property catalog with the new head-offset 4th-site + sarf 4-D shapes, recomputes the PR25 genuine-floor tracking, refreshes the `--resolve-changed` checkpoint targets, and begins the Epic-4 `SUMMARY.md` groundwork.

Sprint 32 resembles Sprint 31 in one structural way: **Sprint 31 diagnosed and precisely pinned these tracks; Sprint 32 implements them against a banked root cause.** Because the root causes are already pinned (the Sprint 31 SPRINT_LOG per-day entries, the per-track ISSUE docs, `BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 for rocket, `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` for camcge, and the AD cross-term property catalog), Sprint 32 prep is lighter on *survey* and heavier on **design-before-implement + tractability-probe**: the hardest track (P1 mine 4th site) needs a concrete **stationarity-consistent bound-multiplier design** (how the bound-active `stat_x` reconciles the LP reduced costs `x.m` warm-started into `piU_x`) before any emit change; the second-hardest (P2 sarf) needs the **O(active-instances) symbolic `stat_task` emit design** over the `$taskposs`-active subset that couples with the 2-D constraint gate; and P3 (camcge Epic-5) needs the **`stat_mps`-first-then-dual-consistent-Walras** ordering design that the Sprint-31 CASE_B verdict established. The Sprint-28–31 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — Sprint 32 Known Unknowns List covering the five carryforward tracks (each a Sprint-31 pinned root cause that is still a Day-0-re-confirm hypothesis, PR24), the three deepest REPLAN-prone tracks (P1 mine 4th-site bound-dual, P2 sarf 369K sparsification, P3 camcge Epic-5), the bound-multiplier-derivation assumption, and the camcge `stat_mps`-before-Walras ordering + degeneracy-detector false-positive scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 31 final → Sprint 32 Day 0 per-model bucket provenance, confirming Day-0 = Sprint 31 final (Solve 107, Match 92, genuine floor 74, model_infeasible 7, Translate 135, Tests 5,074, all-219 Match 95) and that the PR25 genuine-vs-methodology re-baseline is the standing discipline.
3. **mine 4th-site localization + bound-multiplier design (Priority 1 foundation)** — turn the Sprint-31 Day-3 REPLAN (the residual 4th bound-complementarity site at bound-active `stat_x` rows) into a concrete stationarity-consistent bound-multiplier design, sizing the deepest carryforward BEFORE the schedule is set.
4. **sarf 4-D `task`-variable sparsification design (Priority 2 foundation)** — design the O(active-instances) symbolic `stat_task` emit over the `$taskposs`-active subset (369K → active) that couples with the 2-D constraint gate.
5. **camcge `stat_mps` + dual-consistent Walras design + degeneracy-detector scope (Priority 3 / Epic 5)** — design the `stat_mps`/`nu_mps_fx` CASE_B fix first, then the dual-consistent numéraire (price-pin omega 191.735), plus the degeneracy-detector scope that must NOT false-flag irscge/lrgcge/moncge/stdcge.
6. **rocket PATH-consultation input packaging (Priority 4)** — package the finalized PATH-consultation question (the reformulation now a ruled-out candidate) for the Sprint 33 consultation, plus a last remaining-lever sweep.
7. **hhfair + CGE-cluster Case-c formalization design (Priority 5)** — design the `kkt_residual.py` Case-c auto-classifier extension for the objective-defining-intermediate-variable family + the ISSUE-closure criteria.
8. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — refresh/author the gates for the Sprint-32 dispositions (P1 bound-multiplier warm→cold residual gate, P2 O(constraints)/O(active) emit budget, P3 `stat_mps`-then-Walras `/tmp` prototype, P4 Case-c re-confirm before forcing, P5 control-before-implement).
9. **Diagnosis-heavy / REPLAN-prone track risk assessment (PR16)** — apply hypothesis-validation to P1 (deeper IR / 5th-coupling risk), P2 (timeout re-trigger), and P3 (Epic-5 deferral); pin explicit Sprint 33 REPLAN exits + budget reallocation.
10. **Reusable-tooling readiness audit + backlog fix-surface analysis (Priorities 6 + 7)** — confirm the Sprint-28–31 tools cover the new Sprint-32 classes (the bound-multiplier residual test, the sarf 4-D sparsification path, the Case-c classifier), and analyze the P6 backlog fix-surfaces (the #1111/#1112 offset-alias generalization beyond polygon/ps2; the residual `model_infeasible` cohort re-triage) + the P7 property-catalog + Epic-4-SUMMARY groundwork.
11. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 32 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 32 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 31 → Sprint 32 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine floor |
| 3 | mine 4th Bound-Complementarity Site: Localization + Bound-Multiplier Design (Priority 1 foundation) | Critical | 5–7h | Tasks 1, 2 | Priority 1 — mine (Solve) deepest track |
| 4 | sarf 4-D `task`-Variable Stationarity Sparsification Design (Priority 2 foundation) | High | 4–6h | Tasks 1, 2 | Priority 2 — sarf (Translate) 369K sparsification |
| 5 | camcge `stat_mps` CASE_B + Dual-Consistent Walras Design + Degeneracy-Detector Scope (Priority 3 / Epic 5) | High | 4–5h | Task 1 | Priority 3 — Epic 5 camcge (Solve) |
| 6 | rocket PATH-Consultation Input Packaging + Remaining-Lever Sweep (Priority 4) | Medium | 2–3h | Task 1 | Priority 4 — rocket PATH hand-off |
| 7 | hhfair + CGE Cluster Case-c Formalization + Harness Classifier Design (Priority 5) | Medium | 2–3h | Task 1 | Priority 5 — Case-c documentation |
| 8 | Refresh + Author Phase 0 Acceptance Gates for the Sprint-32 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 1, 3, 4, 5 | Priorities 1–5 — primary scope-correctness gate |
| 9 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 4th site, P2 sarf timeout, P3 Epic-5 camcge; PR16) | High | 3–5h | Tasks 3, 4, 5, 8 | Priorities 1, 2, 3 — REPLAN-prone tracks |
| 10 | Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7) | Medium | 3–4h | Tasks 1, 8 | Priorities 6, 7 — tooling reuse + backlog fix-surfaces |
| 11 | Plan Sprint 32 Detailed Schedule | Critical | 3–4h | Tasks 1–10 | All priorities — sprint planning |

**Total Estimated Time:** 36–51 hours (~4.5–6.5 working days)

**Critical Path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11 (the deep-track chain — the mine 4th-site bound-multiplier design (Task 3) sizes Priority 1 and feeds the Phase-0 gate refresh (Task 8), which feeds the REPLAN assessment (Task 9) and the schedule).
**Secondary Path:** Task 1 → Task 4 → Task 8 → Task 9 → Task 11 (the sarf 4-D sparsification design feeds the P2 gate + the timeout-re-trigger REPLAN assessment → schedule).
**Tertiary Path:** Task 1 → Task 5 → Task 8 → Task 9 → Task 11 (the camcge `stat_mps`-then-Walras design feeds the P3 gate + the Epic-5 REPLAN assessment → schedule).
**Quaternary Path:** Task 1 → Task 10 → Task 11 (tooling readiness + backlog fix-surface analysis → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 3 + 4 + 5 + 6 + 7 (independent after Tasks 1/2); Task 10 follows Task 8; Tasks 3/4/5 gate the Phase-0 refresh (Task 8).

---

## Task 1: Create Sprint 32 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~3.5h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive list of assumptions and unknowns for Sprint 32 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform every other prep task — particularly the mine 4th-site bound-multiplier design (Task 3), the sarf 4-D sparsification design (Task 4), the camcge `stat_mps`/Walras design (Task 5), the rocket packaging (Task 6), the hhfair Case-c formalization (Task 7), the Phase-0 gate refresh (Task 8), the REPLAN assessment (Task 9), and the tooling/backlog analysis (Task 10). It also carries forward the end-of-sprint unknowns from Sprint 31 (the carryforwards in `docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` §4 plus any open items in `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 32's central risk is that its carryforwards are the tracks Sprint 31 REPLAN'd *precisely because they proved deeper than projected* — mine needs a 4th bound-complementarity site after the IR foundation landed; sarf's blow-up is the 369K-instance 4-D `task` variable, not the 1,152 constraints; camcge is a CASE_B `nu_mps_fx` defect, not clean Walras; and rocket/hhfair are intrinsic non-convexity. Each carries a pinned root cause, but PR24 still holds: **the pinned root cause is a Day-0-re-confirm hypothesis, not fact** — Sprint 31 REPLAN'd all five deep tracks after a control or harness re-diagnosis, and the Day-2 mine "MS-1 17500" was an outright measurement error. The Known Unknowns List must therefore (a) frame each pinned root cause as a re-verifiable hypothesis, (b) flag the **bound-multiplier-derivation** assumption as a Critical unknown (if the bound-active `stat_x` cannot be reconciled with a stationarity-consistent multiplier, the P1 +1 Solve does not land and REPLANs deeper), (c) flag the three deepest REPLAN-prone tracks (P1 mine 4th site, P2 sarf 4-D sparsification, P3 camcge Epic-5) with a single-model or control-experiment validation as their verification (PR16), and (d) surface the camcge **`stat_mps`-before-Walras ordering** risk (fixing the Walras dual on top of an unresolved fixing-multiplier defect would mis-attribute the residual) *plus* the **degeneracy-detector false-positive** risk (silently redefining a dual on a well-posed CGE would corrupt it — the Sprint-30 "check the dual side" lesson).

### Background

- Sprint 31 Retrospective: `docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` (§4 "Sprint-32 carryforwards" — the five carryforward tracks; §2 "What landed (firm)" — the P2 offset-alias core + the head-offset IR foundation that already landed; §1 metrics table; §3 the control-first + assert-`modelstat` lessons)
- Sprint 31 Known Unknowns: `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` (the 7 Sprint-31 categories — review for open/end-of-sprint items; especially the Category-1 head-offset, Category-3 camcge, Category-4 sarf, Category-5 obj-grad, and Category-6 rocket unknowns whose Sprint-32 dispositions are now known)
- Sprint 32 scope: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32 (Weeks 29–30)" (Priorities 1–7 + Acceptance Criteria + Estimated Effort + Risk Level)
- Carryforward + backlog issues: `docs/issues/ISSUE_{1443,1385,1330,1462,1236}_*.md` (local) + GitHub #1462 rocket, #1111, #1112 (the P6 offset-alias generalization) + the cold-convex CGE cluster (irscge/lrgcge/moncge). **Note:** `ISSUE_1443` records the head-offset 4th-site Day-3 REPLAN block; `ISSUE_1385` records the 369K-instance finding; `ISSUE_1330` records the CASE_B `stat_mps` verdict + the price-pin recipe (omega 191.735); `ISSUE_1462` records the exhausted-lever survey; `ISSUE_1236` records the Case-c control-refutation — these are the Day-0-re-confirm starting points.
- Sprint-30/31 diagnostic + design docs that Sprint 32 consumes: `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` (§3 the rocket PATH-consultation question), `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (§4 the PATH hand-off draft), `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the camcge Epic-5 scoping), the head-offset architecture design + the AD cross-term property catalog

### What Needs to Be Done

1. **Review Sprint 31 carryforward / end-of-sprint KUs.** Migrate any open items from `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` and the retro §4 carryforwards into Sprint 32 numbering with full text and forward-links to the Sprint 32 categories they drive.
2. **For each Priority area, brainstorm unknowns** (assumption / how-to-verify / priority / risk-if-wrong), organized by category aligned to the PROJECT_PLAN priorities:
   - **Category 1 (P1 mine 4th bound-complementarity site — #1443):** Can the bound-active `stat_x` be reconciled with a **stationarity-consistent bound-multiplier** derivation (rather than the `x.m` transfer), so mine reaches MS 1? **(Critical — PR16; the deepest track.)** Is the residual a single 4th site, or does a 5th coupling surface (→ deeper-IR REPLAN)? Does the fix preserve the head-offset IR foundation + Site-2 dual transfer already on `main` (zero regression to the 5 head-offset models)?
   - **Category 2 (P2 sarf 4-D `task`-variable sparsification — #1385):** Does the symbolic `stat_task` emit over the `$taskposs`-active subset make sarf **O(active-instances), not O(369K Cartesian)**, staying inside the translate budget? **(Critical — PR16; the failed-Sprint-26-architecture rebuild + the 369K finding.)** Does the 4-D sparsification couple correctly with the 2-D constraint gate (built + reverted S31), with no set-name-literal multiplier indices?
   - **Category 3 (P3 camcge `stat_mps` + dual-consistent Walras → Epic 5 — #1330):** Does resolving the `stat_mps`/`nu_mps_fx` CASE_B residual **first** (before the dual-consistent numéraire) reach the correct stationarity balance? Does the dual-consistent multiplier redefinition then reach MS 1 at omega 191.735? Does the degeneracy detector flag **only** camcge across irscge/lrgcge/moncge/stdcge? **(Critical — the Sprint-31 CASE_B verdict + the "check the dual side" lesson.)**
   - **Category 4 (P4 rocket PATH-consultation input — #1462):** Is the emit residual clean at the NLP point (Case-c) so rocket stays a forcing problem? Do any remaining emittable levers cross the intrinsic non-convergence, or is the packaged PATH-consultation input the deliverable?
   - **Category 5 (P5 hhfair + CGE-cluster Case-c — #1236):** Does the `kkt_residual.py` Case-c auto-classifier correctly flag the objective-defining-intermediate-variable family (hhfair `stat_u` / CGE `stat_xp`) without false-positives on genuine Case-b? Is the sign flip re-confirmed BANNED (control-refuted 4× S30–S31)?
   - **Category 6 (P6 adjacent backlog):** Does the #1111/#1112 offset-alias second-index-transpose core generalize beyond polygon/ps2 to other 2-index-transpose models (audit for cold-emit corrections)? Do any residual `model_infeasible` cohort members (agreste/cesam/fawley/lnts) re-triage to a fixable Case-b via the harness?
   - **Category 7 (P7 infrastructure):** Do the new head-offset-4th-site + sarf-4-D property fixtures guard P1/P2 once they land? Does the PR25 genuine-floor tracking recompute against the S32–S35 re-baselined Match KPIs (footnote ⁸ ramp S32 ≥75)?
3. **Assign priority + verification** to each unknown; write the Task-to-Unknown mapping appendix (which prep task resolves which unknown). Aim for **22–30 unknowns across 7 categories**.
4. **Update this PREP_PLAN** with the "Unknowns Verified" metadata per downstream task, and add a CHANGELOG entry.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` (25 unknowns across the 7 Sprint-32 priority categories) + the Task-to-Unknown mapping appendix; added the "Unknowns Verified" metadata + Deliverables/Acceptance-Criteria lines on Tasks 2–11 below; CHANGELOG entry.

### Result

**COMPLETE (2026-07-13).** `KNOWN_UNKNOWNS.md` authored with **25 unknowns** (target 22–30) across **7 categories** aligned to the PROJECT_PLAN Sprint-32 priorities. Priority distribution: **6 Critical / 10 High / 6 Medium / 3 Low** (24% / 40% / 24% / 12%). Per-unknown research estimates sum to ~36h; the authoritative scheduling budget is the per-task 36–51h in this PREP_PLAN. Every unknown starts 🔍 INCOMPLETE and is assigned to a downstream prep task (2–11) in the mapping appendix. The six REPLAN-prone Criticals (1.1/1.2 mine bound-multiplier + 5th-coupling, 2.1 sarf O(active) sparsification, 3.1/3.2 camcge `stat_mps`-first + dual-consistent Walras, 3.3 detector false-positive) are captured, and the two dominant Sprint-31 lessons (control-experiment-first hypothesis; assert `modelstat` before an objective read) thread through the Category-1/3 unknowns. Docs-only (no `src/`).

### Verification

```bash
# Document exists
test -f docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md && echo "KU list present"

# 7 categories aligned to the PROJECT_PLAN Sprint-32 priorities (expect 7)
grep -cE "^# Category [0-9]+:" docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md

# Every numbered unknown carries a "How to Verify" section.
# Strip the "Template for New Unknowns" section first — its code block also
# contains a "### How to Verify" heading (and the other field headings), which
# would otherwise inflate the count to 26 vs 25.
body=$(sed '/^## Template for New Unknowns/,$d' docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md)
u=$(printf '%s\n' "$body" | grep -cE "^## Unknown [0-9]+\.[0-9]+:")
v=$(printf '%s\n' "$body" | grep -cE "^### How to Verify")
echo "unknowns=$u how-to-verify=$v (should match — both 25)"

# The bound-multiplier-derivation Critical unknown is present
grep -iqE "bound.multiplier|bound-active|4th site" docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md && echo "P1 4th-site unknown present"

# The camcge stat_mps-before-Walras ordering unknown is present
grep -iq "stat_mps" docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md && echo "stat_mps ordering unknown present"

# Carryforward + backlog issues referenced
grep -oE "#(1443|1385|1330|1462|1236|1111|1112)" docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/KNOWN_UNKNOWNS.md` — 22–30 unknowns across 7 categories aligned to the Sprint-32 priorities, each with Priority / Assumption / Research Questions / How to Verify / Risk if Wrong / Estimated Research Time / Owner / Verification Results (🔍 INCOMPLETE)
- A Task-to-Unknown mapping appendix
- Updated `PREP_PLAN.md` "Unknowns Verified" metadata on Tasks 2–11
- CHANGELOG entry

### Acceptance Criteria

- [x] KNOWN_UNKNOWNS.md created with 7 categories aligned to the Sprint-32 priorities
- [x] 22–30 unknowns (25), each with Priority / Assumption / How to Verify / Risk if Wrong / Owner
- [x] The three deepest REPLAN-prone tracks (P1 mine 4th site, P2 sarf 4-D sparsification, P3 camcge Epic-5) flagged Critical/High with a single-model or control-experiment validation
- [x] The bound-multiplier-derivation Critical unknown is present (P1's +1 Solve hinges on it — Category 1, Unknown 1.1)
- [x] The camcge `stat_mps`-before-Walras ordering AND the degeneracy-detector false-positive risks are both captured (P3 — Unknowns 3.1, 3.3)
- [x] Sprint-31 open/carryforward KUs migrated with forward-links (Sprint-31 Unknowns 1.2/4.2/3.1/3.2/5.1/5.2/6.1/6.3 → Sprint-32 Categories 1/2/3/4/5)
- [x] Task-to-Unknown mapping appendix present
- [x] CHANGELOG updated

---

## Task 2: Sprint 31 → Sprint 32 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~2h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Sprint planning
**Dependencies:** None (parallelizable with Task 1)
**Unknowns Verified:** 7.2

### Objective

Establish the authoritative Sprint 32 Day-0 baseline — the per-model bucket provenance (Parse / Translate / Solve / Match / model_infeasible / path_*) carried forward from the Sprint 31 final retest — and re-run the PR25 genuine-vs-methodology re-baseline so the genuine-floor ramp (74 → ≥ 75) is measured against a clean starting line, not the methodology-inflated Match figure. Crucially, this task records the **142-corpus vs all-219** distinction the Sprint-31 closeout pinned (headline Match 92 is over the 142 convex candidates; the +3 ps2/ps3 gains land on non-candidate `non_convex` models → all-219 tally 95).

### Why This Matters

Every Sprint-32 KPI target is relative to Day 0 (Solve 107 → ≥ 109; genuine floor 74 → ≥ 75; model_infeasible 7 → ≤ 5). The Sprint-31 retro (§1) warns that the two Solve-side targets missed by exactly the REPLAN'd deep tracks (mine, camcge, rocket), and that the genuine-floor ramp is carried by whichever track's fix genuinely changes the emit. A precise per-model Day-0 baseline is what makes the mid-sprint checkpoints (Day 5 / Day 10) able to distinguish a **genuine cold-match gain** from a **methodology reclassification** (the PR25 discipline), and what lets the Task-9 REPLAN assessment reallocate budget from a stalled track to a firm one *without* silently losing a bucket. This task also confirms the `--resolve-changed --since-commit <SHA>` checkpoint re-solve anchors to the correct **Sprint-31-final commit** (the DB changed at S31 Day 13 — the first DB change since the Sprint 28 close, when the +3 ps2/ps3 matches were persisted).

### Background

- Sprint 31 final metrics (from `SPRINT_31/SPRINT_RETROSPECTIVE.md` §1): Parse 142 · Translate 135 · **Solve 107** · **Match 92** (142-corpus; genuine floor **74**) · model_infeasible 7 (agreste/camcge/cesam/fawley/lnts/mine/rocket) · determinism ✅ ×3 `{0,1,42}` · Tests 5,074 · **all-219 Match tally 95** (+3 non-candidate ps2_f_s/ps2_s/ps3_s_gic, persisted Day 13).
- Sprint 31 final retest DB: `data/gamslib/gamslib_status.json` (the per-model bucket source — machine-portable relative `mcp_file_used` paths per PR #1400; changed at S31 Day 13 with the ps2/ps3 persist + 3 new `*_mcp_presolve.gms` goldens).
- The 142-corpus definition: `get_candidate_models` in `scripts/gamslib/run_full_test.py` = `convexity.status ∈ {verified_convex, likely_convex}`; the +3 ps2/ps3 are `non_convex` non-candidates (`SPRINT_31/BASELINE_METRICS.md` §5 Day-13 recompute).
- The PR25 genuine-vs-methodology template: `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` (bucket-provenance + genuine-floor derivation + the operational definition: methodology = cold emit byte-identical to pre-fix, matches only via warm-start).
- The checkpoint re-solve design: the `--resolve-changed` mode of `scripts/gamslib/run_full_test.py` (`--since-commit <Sprint-31-final-SHA>`).

### What Needs to Be Done

1. **Record the Sprint 31 → Sprint 32 Day-0 baseline** — copy the per-model bucket table from the Sprint-31 final DB into `SPRINT_32/BASELINE_METRICS.md`, confirming Day-0 = Sprint 31 final (Solve 107, Match 92, genuine floor 74, model_infeasible 7, Translate 135, Tests 5,074, all-219 Match 95). Enumerate the 7 model_infeasible + the path_syntax_error / path_solve_terminated / path_solve_license members by name.
2. **Re-run the PR25 genuine-vs-methodology partition** — reproduce the genuine floor 74 from first principles (S30 70 + P2's +4: polygon + ps2×3), and identify the specific Sprint-32 targets that would convert to genuine (mine [P1] + camcge [P3] cold-matches).
3. **Confirm the checkpoint anchor** — pin the Sprint-31-final SHA and verify `--resolve-changed --since-commit <SHA>` selects the expected changed-emit set (0 at Day 0 = clean baseline), so Days 5/10 checkpoints re-solve only the touched models.
4. **Record the per-priority Day-0 target model list** — mine, sarf, camcge, rocket, hhfair+CGE cluster — with their current bucket, so each track's success is a single-model bucket transition; note the 142-corpus vs all-219 scope for each.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md` (§1 Day-0 KPI table; §2 canonical 142-candidate bucket recompute + failure-bucket enumeration; §3 the PR25 genuine-vs-methodology partition — genuine floor 74; §4 the 142-corpus vs all-219 scope; §5 per-Sprint-32-target Day-0 bucket provenance + PR25 projection labels; §6 the `--resolve-changed` checkpoint anchor). Set `KNOWN_UNKNOWNS.md` Unknown 7.2 → ✅ VERIFIED (+ the Day-0-bucket aspect of 1.1/2.1/3.1). CHANGELOG entry.

### Result

**COMPLETE (2026-07-13).** Day-0 = Sprint 31 final, reused unchanged — no `src/`/`scripts/` drift since the S31 close (`4cbf8bff`), so no fresh ~4 h retest. The canonical-scope recompute (`get_candidate_models`, 142) reproduces the Sprint 31 final headline exactly: **Parse 142 · Translate 135 · Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) **· Match 92 · model_infeasible 7 · path_syntax_error 8 · path_solve_terminated 4 · path_solve_license 9 · Tests 5,074.** The PR25 partition reproduces the **genuine floor 74** (methodology 21; all-219 Match 95 = 74 genuine + 21 methodology) from first principles (S30 70 + P2's +4: polygon + ps2_f_s/ps2_s/ps3_s_gic), and the footnote-⁸ ramp aligns (S30 70 → S31 74 → **S32 ≥ 75** → S33 maintain ≥ 75 → S34 ≥ 77 → S35 ≥ 78). The **142-corpus vs all-219** distinction is recorded (headline Match 92 over the 142 convex candidates; the +3 non-candidate `non_convex` ps2/ps3 lift the all-219 tally to 95 + the genuine floor, not the headline KPI). Per-Sprint-32-target Day-0 buckets pinned: **mine / camcge / rocket `model_infeasible`** (all candidates), **sarf translate-failure** (candidate), **hhfair `model_optimal` + mismatch 72.147 vs 87.159**, **irscge/lrgcge/moncge `model_optimal_presolve` + match** (documented Case-c). The `--resolve-changed --since-commit 4cbf8bff` checkpoint anchor selects **0 models at Day 0** (clean baseline; GO). Solve ≥ 109 rests on mine [P1] + camcge [P3] (both candidates → lift the 142-corpus Match, unlike the S31 ps2/ps3 gains). Docs-only (no `src/`).

### Verification

```bash
# Baseline doc exists and records the Day-0 metrics
test -f docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md && echo "baseline present"
grep -qE "Solve[^0-9]*107" docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md && echo "Solve 107 recorded"
grep -qE "genuine floor[^0-9]*74|floor[^0-9]*74" docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md && echo "genuine floor 74 recorded"

# The 142-corpus vs all-219 distinction is recorded
grep -qiE "142.corpus|all.219|non.candidate" docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md && echo "corpus-scope distinction recorded"

# Canonical recompute reproduces the headline (142 candidates)
.venv/bin/python -c "import json; db=json.load(open('data/gamslib/gamslib_status.json')); \
m=[e for e in db['models'] if e.get('convexity',{}).get('status') in ('verified_convex','likely_convex')]; \
print('candidates=',len(m),'match=',sum((e.get('solution_comparison') or {}).get('comparison_status')=='match' for e in m))"

# The per-priority Day-0 target models are enumerated
grep -oiE "mine|sarf|camcge|rocket|hhfair" docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md` — Day-0 per-model bucket table + the genuine-vs-methodology partition (genuine floor 74) + the 142-corpus vs all-219 scope note + the per-priority target-model list with current buckets
- The pinned Sprint-31-final SHA + confirmation that the `--resolve-changed` checkpoint anchor selects the correct changed-emit set (0 at Day 0)
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 7.2

### Acceptance Criteria

- [x] BASELINE_METRICS.md created with the Day-0 metrics (Solve 107, Match 92, genuine floor 74, model_infeasible 7, Translate 135, Tests 5,074, all-219 Match 95)
- [x] The PR25 genuine floor 74 reproduced from first principles (polygon + ps2×3 over S30 70)
- [x] The 142-corpus vs all-219 distinction explicitly recorded (per the Sprint-31 closeout finding)
- [x] The Sprint-31-final SHA pinned (`4cbf8bff`); the `--resolve-changed` anchor selects 0 models at Day 0 (GO)
- [x] The per-priority Day-0 target-model list (mine/sarf/camcge/rocket/hhfair+CGE) recorded with buckets
- [x] CHANGELOG updated
- [x] Unknowns 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: mine 4th Bound-Complementarity Site — Localization + Bound-Multiplier Design (Priority 1 foundation)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 5–7 hours (actual: ~4h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

### Objective

Turn the Sprint-31 Day-3 REPLAN — the residual **4th bound-complementarity site** at bound-active `stat_x` rows — into a concrete **stationarity-consistent bound-multiplier design** that the Sprint-32 P1 implementation follows. Localize the 4th site with the KKT-residual harness on the current tree, and design the derivation that reconciles the LP reduced costs (`x.m` warm-started into `piU_x`) with the emitted `stat_x`, so mine reaches MODEL STATUS 1 (+1 Solve).

### Why This Matters

mine (P1) is the deepest Sprint-32 track and one of the two firm +Solve movers (with camcge). Sprint 31 landed the head-offset IR foundation (`EquationDef.head_domain_offsets` + the Site-2 dual transfer, both on `main`) — so the first three sites are handled — but Day 3 found mine still `model_infeasible` because the emitted `stat_x` does not balance at bound-active rows: the degenerate-LP bound-duals warm-started via `x.m` into `piU_x` are not the multipliers the head-offset-coupled `stat_x` needs. Sizing this design BEFORE the schedule is set is what the Sprint-30/31 retros (front-load tractability probes) demand: if the 4th site turns out to need a deeper IR change (a 5th coupling), that must drive an early REPLAN exit, not a Day-9 surprise. The Day-2 measurement-error lesson also binds: any warm-start experiment must assert `mcp_model.modelstat` before reading an objective.

### Background

- `ISSUE_1443_mine-head-domain-offset-mcp-infeasible.md` — the Day-3 REPLAN block: the residual 4th bound-complementarity / `stat_x` reconciliation; the head-offset IR foundation + Site-2 dual transfer that landed Days 1–2; the cold-INFES-by-direction characterization.
- The KKT-residual harness: `scripts/diagnostics/kkt_residual.py` (Case-a/b/c verdict + dual-transfer consistency) — the localization tool.
- The head-offset architecture: the Sprint-30/31 head-offset design docs + `src/ir/symbols.py` (`EquationDef.head_domain_offsets`) + the Site-2 `head_offset_marginal_index_map` in `src/emit/emit_gams.py`.
- The Sprint-31 measurement-error correction (`SPRINT_31/SPRINT_LOG.md` Day 2/3): assert `modelstat` before reading an objective; `x.up=inf` is a structurally invalid experiment (34 unmatched-variable errors).

### What Needs to Be Done

1. **Reproduce + localize the 4th site on the current tree.** Run `kkt_residual.py data/gamslib/raw/mine.gms`; confirm the CASE_B `stat_x` residual localizes to the bound-active rows (per the Day-3 record), with the head-offset IR foundation + Site-2 transfer intact.
2. **Characterize the bound-dual mismatch.** For the bound-active `x` elements, tabulate the LP reduced cost (`x.m`), the emitted `piU_x`/`piL_x`, and the head-offset-coupled `stat_x` residual — showing why the `x.m` transfer does not satisfy `stat_x`.
3. **Design the stationarity-consistent bound-multiplier derivation.** Specify how `piU_x`/`piL_x` should be derived (from the stationarity balance, not the LP reduced cost) at bound-active rows, coupled with the head-offset cross-term; identify the emit site(s) in `src/emit/`/`src/kkt/`.
4. **Define the warm→cold residual gate.** The design must reduce the warm-start residual to ≈ 0, THEN reach cold MS 1 — with `modelstat` asserted at each step (the Day-2 lesson). Flag the 5th-coupling REPLAN exit if the bound-dual reconciliation surfaces a deeper IR need.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md` (§1 harness localization; §2 bound-dual mismatch characterization; §3 the stationarity-consistent bound-multiplier derivation + emit site; §4 warm→cold gate + 5th-coupling REPLAN exit; §5 KU dispositions). Set `KNOWN_UNKNOWNS.md` Unknowns 1.1/1.2/1.3/1.4 → ✅ VERIFIED. CHANGELOG entry. All experiments read-only (harness + `/tmp` emits); no `src/` change.

### Result

**COMPLETE (2026-07-13).** The harness reproduces the Day-3 fingerprint **exactly** on the current tree: **CASE_B**, `stat_x(3,1,1)` rel **2.37** / raw −3.2e4, **dual-transfer CONSISTENT** (comp/equality residual 0), dual scale 1.35e4 — the residual localizes entirely to `stat_x` rows, so `lam_pr`/`pr.m` (head-shifted via Site-2) are correct and the **4th site is the warm-start bound-multiplier transfer**. Emit-site pinned: `src/emit/emit_gams.py:1548–1577` ("Transfer variable marginals to bound multipliers") sets `piL_x/piU_x = ±x.m` (the LP reduced cost), but at mine's degenerate LP vertex `x.m ≠ N` (the non-bound part of `stat_x`), so `stat_x = N − (±x.m) ≠ 0`. **Fix (design):** derive `piL_x = max(N,0)`, `piU_x = max(−N,0)` from the stationarity residual `N` after the `lam_pr` transfer — closes `stat_x = N − piL_x + piU_x` by construction, with the sign matching the bound-active status. The change is **presolve-only, local, and independent of the head-offset foundation** (the Site-2 `head_offset_marginal_index_map` + `EquationDef.head_domain_offsets` are untouched; the 16 head-offset guard tests pass; cold `mine_mcp.gms` byte-unchanged). **Warm→cold gate:** warm residual → 0 (harness Case-a, `modelstat` asserted) → presolve MS-1 (+1 Solve) → cold MS-1 (stretch); the `x.up=inf` experiment is BANNED. **5th-coupling REPLAN exit:** REPLAN to a Sprint-33 deeper head-offset architecture iff the `N`-derivation does not close the warm residual or the sign of `N` contradicts the bound (budget → P6/P7 per Task 9). **Decision: PROCEED** to the in-sprint P1 implementation behind the Task-8 gate. Docs/design-only (no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md && echo "design present"

# Harness reproduces the CASE_B stat_x localization on the current tree
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms 2>&1 | grep -iE "CASE_B|stat_x" | head

# The head-offset IR foundation is intact (regression guard)
.venv/bin/python -m pytest tests/unit/ir/test_head_domain_offsets.py -q 2>&1 | tail -2

# The design names the emit site + the warm→cold residual gate + the 5th-coupling REPLAN exit
grep -iqE "bound.active|piU_x|stationarity-consistent" docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md && echo "bound-multiplier design present"
grep -iqE "REPLAN|5th|deeper" docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md && echo "REPLAN exit present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/MINE_BOUND_MULTIPLIER_DESIGN.md` — the 4th-site localization (harness output), the bound-dual mismatch characterization, the stationarity-consistent bound-multiplier derivation design + emit site(s), the warm→cold residual gate, and the explicit 5th-coupling REPLAN exit
- Updated `KNOWN_UNKNOWNS.md` Category-1 unknowns with the localization findings
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 1.3, 1.4

### Acceptance Criteria

- [x] The 4th site is reproduced + localized on the current tree via `kkt_residual.py` (CASE_B `stat_x(3,1,1)` rel 2.37, duals CONSISTENT)
- [x] The bound-dual mismatch is characterized (`x.m` vs `piU_x`/`piL_x` vs the `stat_x` non-bound residual `N`; the `src/emit/emit_gams.py:1548–1577` `±x.m` transfer)
- [x] A stationarity-consistent bound-multiplier derivation is designed (`piL_x = max(N,0)`, `piU_x = max(−N,0)`), with the emit site named (`src/emit/emit_gams.py:1548–1577`, presolve)
- [x] The warm→cold residual gate is defined, with `modelstat` asserted at each step (Day-2 lesson; `x.up=inf` BANNED)
- [x] The 5th-coupling / deeper-IR REPLAN exit is explicit
- [x] The head-offset IR foundation regression guard passes (16 tests green; cold `mine_mcp.gms` byte-stable)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: sarf 4-D `task`-Variable Stationarity Sparsification Design (Priority 2 foundation)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 4–6 hours (actual: ~3.5h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Design the **O(active-instances) symbolic `stat_task` emit** over the `$taskposs`-active subset that makes sarf translate — sparsifying the 369,024-instance 4-D `task(g,t,mn,mn)` variable's stationarity to the active entries (not the full Cartesian product) — coupled with the 2-D dynamic-subset constraint gate (built + reverted in Sprint 31).

### Why This Matters

sarf (P2) is the sprint's +1 Translate stretch. Sprint 31 Day 8 built the 2-D constraint gate (`_is_blowup_2d_condition_equation`) and confirmed it fires on `tbal`/`equipb1`/`equipb2`, but sarf STILL times out because the dominant blow-up is the **369,024-instance** 4-D `task` variable's `stat_task` enumeration (16·24·31·31), not the 1,152 constraint instances — the gate was necessary but insufficient. This is the failed-Sprint-26-architecture (`nu_slack("srn")` set-name-literal bug) rebuilt: the parametric `stat_task` emit must differentiate each short-circuited body **once**, sparsified to `$taskposs`, with no set-name-literal multiplier indices. Designing the O(active) budget BEFORE implementation is what prevents a Day-8-style "gate fires but still times out" re-trigger.

### Background

- `ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` — the Day-8 REPLAN block: the 369,024-instance 4-D `task` finding; the 2-D gate is necessary-but-insufficient; the banked `stat_task` hand-derivation; the atomicity constraint (re-emit + cross-terms land together).
- `src/ad/index_mapping.py` — `_is_blowup_2d_condition_equation` (the 2-D gate, built + reverted S31) + `enumerate_equation_instances`.
- `src/kkt/stationarity.py` — the `stat_task` emit site (the parametric cross-term path).
- The Sprint-26-failed architecture: commit `243fe578` (reverted — the `nu_slack("srn")` set-name-literal indices + dropped `J_gᵀ·lam` cross-terms) — the anti-pattern to avoid.

### What Needs to Be Done

1. **Confirm the 369K figure + the active-subset size.** Enumerate `task(g,t,mn,mn)` Cartesian instances (16·24·31·31 = 369,024) vs the `$taskposs`-active subset; establish the target O(active) instance count.
2. **Design the sparsified `stat_task` emit.** Specify how the parametric `stat_task` differentiates each short-circuited body once, restricted to the `$taskposs`-active entries, with symbolic (not set-name-literal) multiplier indices; identify the `src/kkt/stationarity.py` + `src/ad/index_mapping.py` sites.
3. **Design the 2-D-gate coupling.** Specify how the re-landed 2-D constraint gate + the 4-D `task` sparsification land **atomically** (re-emit + cross-terms together — the ISSUE_1385 atomicity constraint).
4. **Define the O(active) translate-budget gate.** Time `sarf_mcp.gms` against the translate budget; the design must stay O(active), not re-trigger the Option-1 timeout. Flag the re-scoping REPLAN exit if the parametric emit re-triggers.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` (§1 sizing probe; §2 model structure; §3 sparsified `stat_task` emit + sites; §4 2-D-gate atomicity coupling; §5 anti-pattern guard; §6 O(active) translate-budget gate + REPLAN exit; §7 KU dispositions). Set `KNOWN_UNKNOWNS.md` Unknowns 2.1/2.2/2.3/2.4 → ✅ VERIFIED. CHANGELOG entry. All experiments read-only (GAMS data probe + code reads); no `src/` change.

### Result

**COMPLETE (2026-07-13).** A GAMS data probe pins the sizing decisively: `task(g,t,mn,mn)` Cartesian = 16·24·31·31 = **369,024**; `card(taskposs)` = 129 active `(g,t)`; and the active `task(g,t,m,n)` subset (`taskposs(g,t)` ∧ `tech(g,m,n)`) = **398** — a **927× reduction**. `task` is declared over the full 369K but appears only conditioned on `$taskposs(g,t)` ∧ `$tech(g,m,n)`, so the 368,626 inactive columns are vacuous (→ `task.fx = 0`, the mine non-`d` precedent). **Fix (design):** emit **one symbolic guarded equation** `stat_task(g,t,m,n)$taskposs(g,t)..` (the banked 7-term ISSUE_1385 derivation) — translate-time O(1 symbolic equation), not O(369K) — plus `task.fx$(not active)=0`. Sites: `src/ad/index_mapping.py` (variable-stationarity short-circuit, extending the 1-D `_is_blowup_dynamic_subset_equation` to the 2-D shape — the 2-D gate is confirmed **absent from main**, reverted Day 8) + `src/kkt/stationarity.py` (the new symbolic parametric cross-term path, since the short-circuited constraints enumerate zero per-instance Jacobian entries). **Atomicity:** the 2-D constraint gate + the 4-D sparsification + the cross-terms + `task.fx` assemble at a single point (re-emit-without-cross-terms = inconsistent MCP). **Anti-pattern guard:** the banked `stat_task` is symbolic (`nu_tbal(g,t)`, `lam_equipb1(m,t)`, …); the `grep 'nu_*("' / 'lam_*("'` compile-clean scan gates against the Sprint-26 `nu_slack("srn")` bug (commit `243fe578`). **O(active) translate-budget gate + re-scoping REPLAN exit** defined. **Decision: PROCEED** to the in-sprint P2 implementation behind the Task-8 gate (high-risk architectural rebuild; the O(active) budget gate + atomicity/anti-pattern checks are load-bearing). Docs/design-only (no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md && echo "design present"

# The 369K figure + active-subset target are recorded
grep -qE "369,?024|369K" docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md && echo "369K figure recorded"
grep -iqE "taskposs|active.subset|O\(active" docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md && echo "active-subset design present"

# The atomicity coupling + the anti-pattern guard are named
grep -iqE "atomic|couple" docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md && echo "atomicity coupling present"
grep -iqE "set-name|nu_slack|243fe578" docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md && echo "anti-pattern guard present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` — the 369K vs `$taskposs`-active sizing, the sparsified `stat_task` emit design + sites, the 2-D-gate atomicity coupling, the O(active) translate-budget gate, and the re-scoping REPLAN exit
- Updated `KNOWN_UNKNOWNS.md` Category-2 unknowns with the active-subset sizing
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [x] The 369,024 Cartesian figure + the `$taskposs`-active target instance count (398) are recorded
- [x] The sparsified O(active) `stat_task` emit is designed, with symbolic (not set-name-literal) multiplier indices + named sites (`src/ad/index_mapping.py` + `src/kkt/stationarity.py`)
- [x] The 2-D-gate + 4-D-sparsification atomicity coupling is designed (ISSUE_1385 atomicity — single assembly point)
- [x] The O(active) translate-budget gate is defined; the timeout-re-trigger REPLAN exit is explicit
- [x] The Sprint-26 `nu_slack("srn")` anti-pattern (commit `243fe578`) is named as the guard (+ the `grep 'nu_*("'` compile-clean scan)
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: camcge `stat_mps` CASE_B + Dual-Consistent Walras Design + Degeneracy-Detector Scope (Priority 3 / Epic 5)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 4–5 hours (actual: ~4h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Design the two-step camcge fix the Sprint-31 CASE_B verdict established — **first** resolve the `stat_mps`/`nu_mps_fx` fixing-multiplier defect, **then** the dual-consistent Walras numéraire (price-pin omega 191.735) — plus the degeneracy-detector scope that must flag only camcge across the CGE cohort. This is an Epic-5-domain design.

### Why This Matters

camcge (P3) is the second firm +Solve mover. Sprint 31 Days 6–7 re-diagnosed it as **CASE_B** (harness `stat_mps` rel 1.05 / raw −210, dual-transfer CONSISTENT) — a `nu_mps_fx` fixing-multiplier transfer/stationarity defect (`mps` is a fixed variable), a *different bug class* than the Walras singular-Jacobian the Epic-5 transform targets. The Sprint-30 "check the dual side" lesson binds: layering the dual-consistent Walras transform on top of an unresolved `stat_mps` residual would mis-attribute the failure. The ordering (`stat_mps` first, then Walras) must be designed before implementation, and the degeneracy detector must not silently redefine a dual on a well-posed CGE (irscge/lrgcge/moncge/stdcge all solve today).

### Background

- `ISSUE_1330_camcge-model-infeasible-after-1245.md` — the Sprint-31 CASE_B verdict (`stat_mps` rel 1.05, `nu_mps_fx` fixing-multiplier defect); the price-pin recipe (fix `p('services')=pd0` → omega 191.735, MS-4); the naive drop-row corrupts (omega 299); the dual-consistent multiplier redefinition is the target.
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` — the camcge Epic-5 scoping (Walras-law singular Jacobian + no numéraire; a CGE-domain transformation).
- The KKT-residual harness: `scripts/diagnostics/kkt_residual.py` (the CASE_B `stat_mps` localization + the cohort false-positive check).

### What Needs to Be Done

1. **Re-confirm the CASE_B `stat_mps` verdict on the current tree.** Run `kkt_residual.py data/gamslib/raw/camcge.gms`; confirm the `stat_mps`/`nu_mps_fx` residual (rel ~1.05) with dual-transfer CONSISTENT.
2. **Design the `stat_mps` fixing-multiplier fix.** Specify how `nu_mps_fx` (the multiplier for the `mps.fx` fixing) should be transferred/emitted so `stat_mps` balances; identify the emit site.
3. **Design the dual-consistent Walras numéraire (Epic 5).** Specify the multiplier redefinition (express the dropped market's dual via Walras' law so it stays available in the stationarity) that reaches MS 1 at omega 191.735, gated on the `stat_mps` fix landing first.
4. **Scope the degeneracy detector.** Specify the S1∧S2∧S3 (or equivalent) detector that flags **only** camcge across irscge/lrgcge/moncge/stdcge (no false-positive on a well-posed CGE); define the pass-through default + the per-model-numéraire fallback.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` (§1 CASE_B re-confirm; §2 the `stat_mps`/`nu_mps_fx` fix — a general emit fix; §3 the dual-consistent Walras numéraire; §4 the S1∧S2∧S3 detector; §5 the numéraire rule; §6 KU dispositions). Set `KNOWN_UNKNOWNS.md` Unknowns 3.1/3.2/3.3/3.4 → ✅ VERIFIED. CHANGELOG entry. All experiments read-only (harness + NLP marginal probe + `/tmp` emit); no `src/` change.

### Result

**COMPLETE (2026-07-13).** The harness re-confirms **CASE_B `stat_mps` rel 1.05 / raw −210** (duals CONSISTENT, closure 4.83e-10) on the current tree. **Step 1 (general emit fix — precisely localized + empirically confirmed):** the emitted `stat_mps` is structurally correct; the defect is that the `--nlp-presolve` "Transfer fixed-variable marginals to `_fx_` multipliers (#1462)" block emits transfers **only** for the two `$include`-fixed `l(i,lc)` elements (the #1449-widened case), with **no `nu_mps_fx.l = …` line** for the general `mps.fx=.09305` scalar fixing → `nu_mps_fx = 0` → `stat_mps = gradient = −210`. The NLP marginal probe gives **`mps.m = −209.861`**, matching the −210 residual, so `nu_mps_fx` = the fixed variable's reduced cost. The fix (extend the #1462 block to transfer `nu_<var>_fx.l = ±<var>.m` — the sign per the multiplier's role in its stationarity row — for every scalar `var.fx` fixing; for camcge's `stat_mps`, which enters `+ nu_mps_fx`, that instance is `nu_mps_fx.l = -mps.m`) is a **general nlp2mcp emit-correctness fix** in `src/emit/emit_gams.py`, landable in Sprint 32 — it closes `stat_mps` (harness → Case-a). **Step 2 (Epic-5 CGE transformation, gated on step 1):** the residual Walras singularity is independent of `stat_mps`; the design keeps every market-clearing row (no orphaned dual — the Day-11 lesson) + the consumption-weighted numéraire + a Walras-consistent dual redefinition. The Day-11 price-pin reaches omega 191.735 but MS-4 **without** the `stat_mps` fix; the combined `/tmp`-to-MS-1 prototype (step 1 + step 2) is the in-sprint gate, with an Epic-5-deferral fallback if MS-4 persists. **Step 3 (detector):** S1∧S2∧**S3 (cold-MCP-singular-at-iter-0, the false-positive guard)** flags only camcge — the Day-7 cohort test confirms irscge/lrgcge/moncge/stdcge all cold MS-1 (pass-through), only camcge MS-4. **Decision: PROCEED — split the track** (step 1 = general emit fix in Sprint 32; step 2 = Epic-5, +1 Solve conditional on the MS-1 prototype). Docs/design-only (no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md && echo "design present"

# Harness re-confirms the CASE_B stat_mps verdict
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms 2>&1 | grep -iE "CASE_B|stat_mps" | head

# The stat_mps-first-then-Walras ordering + omega 191.735 + detector scope are designed
grep -iqE "stat_mps|nu_mps_fx" docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md && echo "stat_mps fix designed"
grep -qE "191.735" docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md && echo "price-pin target recorded"
grep -oiE "irscge|lrgcge|moncge|stdcge" docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` — the CASE_B `stat_mps` re-confirmation, the `nu_mps_fx` fixing-multiplier fix design, the dual-consistent Walras numéraire design (omega 191.735, gated on `stat_mps` first), and the degeneracy-detector scope (flags only camcge; pass-through default; per-model-numéraire fallback)
- Updated `KNOWN_UNKNOWNS.md` Category-3 unknowns + `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` cross-link
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [x] The CASE_B `stat_mps` verdict is re-confirmed on the current tree (rel 1.05 / raw −210, duals CONSISTENT)
- [x] The `nu_mps_fx` fixing-multiplier fix is designed, with the emit site named (the #1462 transfer block in `src/emit/emit_gams.py`; `nu_mps_fx.l = -mps.m`, confirmed `mps.m = −209.861`)
- [x] The dual-consistent Walras numéraire is designed (omega 191.735), gated on the `stat_mps` fix landing first; the `/tmp`-to-MS-1 prototype is the in-sprint gate
- [x] The degeneracy detector is scoped to flag ONLY camcge across irscge/lrgcge/moncge/stdcge (S3 cold-singular guard; Day-7 cohort test)
- [x] The pass-through default + per-model-numéraire fallback are specified
- [x] The Epic-5 cross-link is recorded (`docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`)
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: rocket PATH-Consultation Input Packaging + Remaining-Lever Sweep (Priority 4)

**Status:** ✅ COMPLETE
**Priority:** Medium
**Estimated Time:** 2–3 hours (actual: ~2h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 4.1, 4.2, 4.3

### Objective

Package the finalized **PATH-consultation input** for rocket (the concrete question set + the ruled-out-lever survey) that feeds the renumbered **Sprint 33** PATH consultation, and sweep for any remaining emittable lever the packaging surfaces. Confirm the emit residual is clean at the NLP point (Case-c) so rocket stays a forcing problem, not a latent emit bug.

### Why This Matters

rocket (P4) is a deferred +1 Solve — Sprint 31 Day 11 exhausted the last emittable lever (the division-by-variable reformulation: MS-5 cold/warm/continuation), establishing that rocket's non-convergence is intrinsic to the discretized optimal-control MCP structure. The Sprint-32 deliverable is the *packaged* PATH-consultation input, not a rocket solve — so the prep must confirm the question is concrete (the reformulation now a ruled-out candidate, sharpening the question toward the intrinsic structure) and the Case-c scope guard holds before any Day-1 forcing attempt.

### Background

- `ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` — the Day-11 exhausted-lever survey (division-by-variable reformulation MS-5 cold/warm/continuation; intrinsic non-convergence); the `--force` scaffold (landed Sprint 30); the Case-c residual-clean-at-NLP-point gate.
- `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 — the PATH-consultation question (the reformulation ruled-out candidate).
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 — the PATH hand-off draft + the exhausted PATH-option survey (INFES 477 → 382).
- The `--force {homotopy,multistart,optfile}` scaffold in the emit pipeline.

### What Needs to Be Done

1. **Re-confirm the Case-c scope guard.** Run `kkt_residual.py data/gamslib/raw/rocket.gms`; confirm the residual is clean at the NLP point (the Case-c boundary signature per ISSUE_1462), so rocket stays a forcing problem.
2. **Assemble the packaged PATH-consultation input.** Consolidate the ruled-out-lever survey (PATH-option INFES 477→382; continuation/multistart MS-5; the division-by-variable reformulation) into a single concrete question set targeting the intrinsic discretized-optimal-control structure.
3. **Sweep for any remaining emittable lever.** Enumerate any lever the packaging surfaces (scaled/relaxed continuation schedules not yet tried); note whether a Day-1 attempt is warranted or the hand-off is the deliverable.
4. **Draft the Sprint-33 hand-off note.** The finalized question + the `--force` scaffold + the ruled-out-lever survey as the de-risked hand-off.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (§1 Case-c scope-guard re-confirmation; §2 the consolidated ruled-out-lever survey; §3 the finalized PATH-consultation question + reproducible case; §4 the remaining-lever sweep result; §5 the Sprint-33 hand-off note; §6 KU dispositions). Set `KNOWN_UNKNOWNS.md` Unknowns 4.1/4.2/4.3 → ✅ VERIFIED. CHANGELOG entry. All experiments read-only (harness); no `src/` change.

### Result

**COMPLETE (2026-07-13).** **Case-c scope guard re-confirmed:** the harness (`kkt_residual.py rocket.gms`) reports a nominal CASE_B verdict, but the residual concentrates entirely on the **boundary rows** — `stat_ht(h0)` rel 1.00 / raw −4.56, `stat_step` 0.50, `stat_ht(h50)` 0.44 (the initial/terminal/time-step conditions of the discretized optimal-control problem) — which move with the warm-start value (the non-convex Case-c boundary signature per ISSUE_1462, NOT a cleanable emit bug); the interior rows are near tolerance (`stat_v(h0)` 0.038, `stat_m(h0)` 0.014); dual-transfer CONSISTENT (closure 1.53e-10). So rocket is a genuine forcing problem. **Remaining-lever sweep: no untried emittable lever** — the PATH-option space (best INFES 477 → 382), μ-continuation, multistart, and the division-by-variable reformulation are all exhausted (MS-5); since the reformulation removes ALL `1/m`,`1/ht²` yet still doesn't converge, the non-convergence is **intrinsic to the discretized optimal-control MCP structure**, so no Day-1 attempt is warranted. **The packaged PATH-consultation input is the deliverable:** the finalized question (with the reformulation as a ruled-out candidate + a reproducible case), the ruled-out-lever survey, and the `--force` scaffold form the de-risked Sprint-33 hand-off. **Decision: PROCEED to the Sprint-33 hand-off;** rocket's +1 Solve is conditional on the consultation. Docs/analysis-only (read-only harness; no `src/`).

### Verification

```bash
# Packaged input doc exists
test -f docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md && echo "packaged input present"

# Case-c scope guard re-confirmed
.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms 2>&1 | grep -iE "CASE_C|Case-c|clean|NLP point" | head

# The ruled-out-lever survey + the concrete question are present
grep -iqE "ruled.out|477|382|division-by-variable" docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md && echo "ruled-out-lever survey present"
grep -iqE "Sprint 33|hand-off|consultation" docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md && echo "Sprint-33 hand-off present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` — the Case-c scope-guard re-confirmation, the packaged PATH-consultation question set, the ruled-out-lever survey, the remaining-lever sweep result, and the Sprint-33 hand-off note
- Updated `KNOWN_UNKNOWNS.md` Category-4 unknowns
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 4.1, 4.2, 4.3

### Acceptance Criteria

- [x] The Case-c scope guard (residual clean except the boundary rows) is re-confirmed on the current tree (`stat_ht(h0)`/`stat_step`/`stat_ht(h50)`, duals CONSISTENT)
- [x] The packaged PATH-consultation question set is concrete (targets the intrinsic structure; the reformulation ruled out; reproducible case)
- [x] The ruled-out-lever survey is consolidated (PATH-option 477→382; continuation/multistart MS-5; reformulation MS-5)
- [x] The remaining-lever sweep result is recorded (no untried lever → the hand-off is the deliverable)
- [x] The Sprint-33 hand-off note is drafted (question + `--force` scaffold + ruled-out survey)
- [x] Unknowns 4.1, 4.2, 4.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: hhfair + CGE Cluster Case-c Formalization + Harness Classifier Design (Priority 5)

**Status:** ✅ COMPLETE
**Priority:** Medium
**Estimated Time:** 2–3 hours (actual: ~2.5h)
**Completed:** 2026-07-13
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

### Objective

Design the `kkt_residual.py` **Case-c auto-classifier extension** for the objective-defining-intermediate-variable family (hhfair `stat_u` / CGE `stat_xp`) and the ISSUE-closure criteria, so Sprint 32 can formally close hhfair + the CGE cluster as documented genuine non-convex Case-c (no emit fix expected).

### Why This Matters

hhfair + the CGE cluster (P5) delivered **0 genuine floor** in Sprint 31 — the P5 ν_objective reduction was control-refuted (inert; the sign flip stayed BANNED, refuted 4× across S30–S31). The Sprint-32 deliverable is *formalization*, not a fix: an auto-classifier that flags the family so future sprints don't re-attempt the refuted reduction, plus a clean ISSUE closure. Designing the classifier's discriminator (the objective-defining-intermediate-variable shape: a variable appearing only in `obj =e= prod(x**a)` and also market-cleared, whose cold solve sits at a spurious local KKT point) before implementation keeps it from producing false positives on genuine Case-b rows.

### Background

- `ISSUE_1236_hhfair-objective-mismatch.md` — the Sprint-31 Day-10 Case-c control-refutation (the ν_objective reduction is inert; the CGE cluster cold `UU=25.5085` for both sign choices; the sign flip BANNED); the objective-defining-intermediate-variable family definition.
- `scripts/diagnostics/kkt_residual.py` — the Case-a/b/c verdict logic (the classifier to extend).
- The Sprint-30/31 control-refutation record: hhfair 72→22 (worse) on sign flip; irscge/lrgcge/moncge `stat_xp` inert.

### What Needs to Be Done

1. **Specify the Case-c discriminator.** Define the objective-defining-intermediate-variable shape precisely (variable appears only in the objective defining equation `obj =e= f(x)` AND is market-cleared; cold solve reaches a spurious local KKT point; presolve warm-start reaches the match).
2. **Design the `kkt_residual.py` classifier extension.** Specify how the harness auto-flags the family as Case-c (non-convex, presolve-required) vs a fixable Case-b, without false-positives.
3. **Define the ISSUE-closure criteria.** Specify what "documented Case-c" means for closure (hhfair + irscge/lrgcge/moncge): the classifier flags them, the sign flip is recorded BANNED, and they are handed to the Sprint-33 forcing/PATH work.
4. **Re-confirm the sign-flip ban.** Note the control-refutation history (4× S30–S31) so no Day-1 sign-flip attempt is made.

### Changes

Created `docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` (§1 the Case-c discriminator D1–D4; §2 the current-tree re-confirmation; §3 the `kkt_residual.py` classifier-extension design; §4 the sign-flip ban; §5 the ISSUE-closure criteria; §6 KU dispositions). Set `KNOWN_UNKNOWNS.md` Unknowns 5.1/5.2/5.3/5.4 → ✅ VERIFIED. CHANGELOG entry. All experiments read-only (harness); no `src/` change.

### Result

**COMPLETE (2026-07-13).** **Discriminator (D1∧D2∧D3):** a `stat_<var>` residual is genuine objective-defining-intermediate-variable Case-c when **D1** — `<var>` appears in the objective defining equation `obj =e= f(<var>)` (so `nu_obj=±1`, no free multiplier) and is pinned by its own defining equation; **D2** — dual-transfer CONSISTENT; **D3** — the cold-start MCP reaches a spurious KKT point (cold ≠ match). **Re-confirmed on the current tree:** hhfair `stat_u(1)` rel 2.00, irscge `stat_xp(BRD)` rel 0.064 — both concentrated on the objective-defining intermediate variable (`u` in `objective.. obj =e= prod(u**ufact)`; `Xp` in `obj.. UU =e= prod(Xp**alpha)`), interiors near tolerance, duals CONSISTENT. The Day-10 cohort control (banked) confirms all four Case-c: irscge/lrgcge/moncge cold `UU=25.5085` vs match `26.09` (sign flip inert), hhfair cold `72.147` vs `87.159`. **Classifier extension:** a post-verdict reclassification pass in `kkt_residual.py` — if CASE_B + D1 + D3 (**D2 is implied by the CASE_B verdict** — the harness only returns CASE_B when dual-transfer is CONSISTENT), emit `case_c (objective-defining-intermediate-variable non-convexity)`; the tight D1 structural gate prevents false-positives on real Case-b bugs; D4 (sign-flip-inert) is the manual control for new candidates. **Sign flip BANNED** (refuted 4×: hhfair S30 Days 4/6 [72→22 worse], himmel16 S30 Day 7, the reduction inert S31 Day 10). **ISSUE-closure:** classifier auto-flag + BANNED sign flip + Sprint-33 forcing/PATH hand-off + `ISSUE_1236` closed as documented-non-convex (methodology, not genuine floor; P5 delivers 0 floor). **Decision: PROCEED** to the in-sprint classifier extension + ISSUE closure; no emit fix. Docs/design-only (no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md && echo "design present"

# The discriminator + classifier extension + closure criteria are present
grep -iqE "objective-defining|intermediate-variable|stat_u|stat_xp" docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md && echo "discriminator present"
grep -iqE "sign flip|BANNED|refuted" docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md && echo "sign-flip ban recorded"
grep -oiE "hhfair|irscge|lrgcge|moncge" docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` — the Case-c discriminator spec, the `kkt_residual.py` classifier-extension design, the ISSUE-closure criteria, and the sign-flip-ban re-confirmation
- Updated `KNOWN_UNKNOWNS.md` Category-5 unknowns
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

### Acceptance Criteria

- [x] The objective-defining-intermediate-variable Case-c discriminator is specified precisely (D1 structural: `<var>` in `obj =e= f(<var>)`, `nu_obj=±1`; D2 dual-consistent; D3 cold-spurious; D4 sign-flip-inert)
- [x] The `kkt_residual.py` classifier extension is designed (a D1∧D2∧D3 post-verdict reclassification pass; the D1 gate prevents false-positives on Case-b)
- [x] The ISSUE-closure criteria for hhfair + irscge/lrgcge/moncge are defined (auto-flag + BANNED sign flip + Sprint-33 hand-off + documented-non-convex closure)
- [x] The sign-flip ban is re-confirmed with the control-refutation history (4× S30–S31)
- [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Refresh + Author Phase 0 Acceptance Gates for the Sprint-32 Tracks (PR20 + PR24 + PR27)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 32 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 3, 4, 5
**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1

### Objective

Author/refresh the Phase 0 acceptance gates (PR20 hand-derived-KKT-before-src; PR24 Day-0-traced fix-surface; PR27 control-experiment-before-implement) for each Sprint-32 track, so every emit-touching implementation starts behind a PROCEED/REPLAN gate. This is the primary scope-correctness gate.

### Why This Matters

Sprint 31 REPLAN'd all five deep tracks after a control or harness re-diagnosis refuted the original premise — the strongest evidence that the Phase-0 gate is load-bearing. Sprint 32's tracks each carry a pinned root cause (Tasks 3/4/5), but PR24/PR27 hold: each must survive a control experiment before the high-blast-radius `src/` change. The gate for P1 (mine) is the warm→cold residual reduction; for P2 (sarf) the O(active) translate-budget; for P3 (camcge) the `stat_mps`-then-Walras `/tmp` prototype to MS 1; for P4 (rocket) the Case-c re-confirm before forcing; for P5 (hhfair) the control-before-implement (sign flip BANNED).

### Background

- The Sprint-31 Phase-0 gate doc (`SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md`) — the template to refresh for the Sprint-32 dispositions.
- The design outputs of Tasks 3 (mine bound-multiplier), 4 (sarf sparsification), 5 (camcge `stat_mps`/Walras).
- The PR-discipline definitions: PR20 (Phase-0 hand-derived KKT), PR24 (Day-0-traced fix-surface = hypothesis), PR27 (control-experiment-before-implement).

### What Needs to Be Done

1. **Author the P1 gate:** the `kkt_residual.py` 4th-site localization + the warm-start residual → 0 (with `modelstat` asserted) → cold MS 1, before the bound-multiplier emit change; the 5th-coupling REPLAN exit.
2. **Author the P2 gate:** the O(active-instances) translate-budget probe (time `sarf_mcp.gms`) + the `stat_task` verification against the banked hand-derivation + golden byte-stable, before the emit lands; the timeout-re-trigger REPLAN exit.
3. **Author the P3 gate:** the `/tmp` prototype of the `stat_mps` fix + the dual-consistent Walras to MS 1 (omega 191.735) + the detector-flags-only-camcge check, before any `src/` change; the Epic-5-deferral REPLAN exit.
4. **Author the P4/P5 gates:** P4 = Case-c residual-clean-at-NLP-point re-confirm before any forcing; P5 = control-experiment-before-implement (the sign flip is BANNED; default to the documented Case-c finding).
5. **Cross-link each gate to its KNOWN_UNKNOWNS category + its design doc.**

### Changes

- Authored `docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` (the Sprint-32 refresh of the SPRINT_31 template): §0 the standing discipline (PR20/PR24/PR27 + the `modelstat`-before-objective / `x.up=inf`-BANNED lesson); §1 the five per-track gates (P1 mine, P2 sarf, P3 camcge, P4 rocket, P5 hhfair/CGE), each with Disposition + PROCEED precondition (control-before-src) + REPLAN exit + cross-links to its KNOWN_UNKNOWNS category + Task-3–7 design doc; §2 the gate summary table; §3 the gate-layer Known-Unknowns dispositions (1.1/2.1/3.1/4.1/5.1). Every emit-touching gate (P1/P2/P3) cites the golden-staleness check (PR26) + `--resolve-changed --since-commit 4cbf8bff`.
- Fixed this task's verification grep to the template-consistent `### P` heading style (the SPRINT_31 template + this doc use `### P1 — …` under `## 1. Per-track gates`, not `## P1`).
- Set KNOWN_UNKNOWNS Unknowns 1.1/2.1/3.1/4.1/5.1 gate-layer disposition (each already VERIFIED by Tasks 3–7; Task 8 adds the PROCEED/REPLAN gate-framing).

### Result

- **P1 (mine) PROCEED** behind the warm-residual→0 gate: replace `piL_x/piU_x = ±x.m` (`src/emit/emit_gams.py:1548–1577`) with the stationarity-residual `N`-derivation, re-run `kkt_residual.py` → Case-a (`modelstat` asserted) → presolve MS-1; 5th-coupling REPLAN exit → Sprint-33.
- **P2 (sarf) PROCEED** behind the O(active=398)-not-O(369K) translate-budget probe + atomic emit (symbolic `stat_task$taskposs` + `task.fx`, no set-name-literal indices, golden byte-stable); timeout-re-trigger REPLAN exit → re-scope.
- **P3 (camcge) PROCEED (split):** step 1 (`nu_mps_fx.l = -mps.m`, `mps.m=−209.861`) → `stat_mps` Case-a is a general emit fix that lands regardless; step 2 (dual-consistent Walras) gated on the `/tmp` prototype → MS-1 @ 191.7346 + the S1∧S2∧S3 detector flagging camcge only; Epic-5-deferral REPLAN exit.
- **P4 (rocket) PROCEED-conditional:** residual-clean-at-NLP-point (Case-c boundary signature) re-confirm before any forcing; intrinsic-non-convergence REPLAN exit → the packaged Sprint-33 PATH-consultation input.
- **P5 (hhfair/CGE) PROCEED:** the only `src/` change is the `kkt_residual.py` Case-c classifier extension (no emit fix; the sign flip is BANNED, refuted 4×); all four re-confirmed Case-c → `ISSUE_1236` documented-non-convex.

### Verification

```bash
# Gate doc exists with a gate per track
test -f docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md && echo "gates present"
grep -cE "^### (P1|P2|P3|P4|P5)" docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md   # expect >=5

# Each gate has a PROCEED/REPLAN decision + a control/probe step
grep -ciE "PROCEED|REPLAN" docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md
grep -iqE "control experiment|/tmp prototype|residual → 0|O\(active" docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md && echo "control/probe steps present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` — one PROCEED/REPLAN gate per track (P1–P5), each with its control/probe step, its REPLAN exit, and a cross-link to its KNOWN_UNKNOWNS category + design doc
- Updated `KNOWN_UNKNOWNS.md` cross-references
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1

### Acceptance Criteria

- [x] A Phase-0 gate exists for each of P1–P5, each with a PROCEED/REPLAN decision
- [x] The P1 gate is the warm→cold residual reduction (with `modelstat` asserted); the 5th-coupling REPLAN exit is explicit
- [x] The P2 gate is the O(active) translate-budget probe; the timeout-re-trigger REPLAN exit is explicit
- [x] The P3 gate is the `/tmp` `stat_mps`-then-Walras prototype to MS 1 + the detector-scope check; the Epic-5-deferral exit is explicit
- [x] The P4 gate (Case-c re-confirm) + the P5 gate (control-before-implement, sign flip BANNED) are authored
- [x] Each gate cross-links its KNOWN_UNKNOWNS category + design doc
- [x] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-14
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 32 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 3, 4, 5, 8
**Unknowns Verified:** 1.1, 1.2, 2.1, 3.1, 3.2

### Objective

Apply the PR16 hypothesis-validation methodology to the three deepest REPLAN-prone Sprint-32 tracks — P1 (mine 4th-site bound-dual, deeper-IR risk), P2 (sarf 4-D sparsification, timeout-re-trigger risk), and P3 (camcge Epic-5, dual-consistency risk) — and pin explicit **Sprint 33 REPLAN exits + budget reallocation** for each, so a stalled track hands off cleanly rather than over-running.

### Why This Matters

Sprint 31's honest projection was borne out exactly: the two Solve-side targets missed by the REPLAN'd deep tracks. Sprint 32's Solve ≥ 109 rests on mine [P1] + camcge [P3], both REPLAN-prone; the +1 Translate rests on sarf [P2], a failed-architecture rebuild. The Sprint-30 retro §3 lesson (treat the ramp as conditional, not independent +1s) binds. This task turns each track's Phase-0 gate (Task 8) into a **budget-reallocation decision**: which task's freed hours flow to which firm track (or to P6/P7) if it REPLANs, so the Task-11 schedule has explicit slip valves.

### Background

- The Task-3/4/5 design docs + the Task-8 Phase-0 gates (the PROCEED/REPLAN criteria per track).
- The Sprint-31 REPLAN record (`SPRINT_31/SPRINT_RETROSPECTIVE.md` §3) — all five deep tracks REPLAN'd; the reallocation order (P5 → P7 → +Translate/forcing tails).
- The PR16 hypothesis-validation methodology + the Sprint-30 retro §3 conditionality lesson.

### What Needs to Be Done

1. **For each of P1/P2/P3, state the hypothesis + the single-model validation** (mine → MS 1; sarf → translate; camcge → MS 1) + the PROCEED/REPLAN threshold from Task 8.
2. **Pin the Sprint-33 REPLAN exit per track** (P1 → deeper-IR head-offset architecture; P2 → symbolic-emit re-scoping; P3 → Epic-5 per-model-numéraire fallback), each with the de-risked hand-off it produces.
3. **Define the budget-reallocation order** — which freed hours flow where (e.g., P1 slip → P6 offset-alias generalization + P7 property catalog), mirroring the Sprint-31 Task-7 reallocation.
4. **Record the honest KPI projection** — Solve ≥ 109 is conditional on ≥ 2 of {mine, camcge}; genuine floor ≥ 75 is conditional on those cold-matching; Translate +1 is conditional on sarf.

### Changes

- Authored `docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md` (the SPRINT_31 template refreshed): Executive summary + a per-track section for the three deepest REPLAN-prone tracks — **P1 mine** (4th-site bound-dual, deeper-IR risk), **P2 sarf** (4-D sparsification, timeout-re-trigger risk), **P3 camcge** (Epic-5, dual-consistency risk) — each with a pinned bug class, a PR16 single-model validation (V1/V2 table), a Sprint-33 REPLAN exit + de-risked hand-off, a budget-reallocation target, and a REPLAN prior; plus a Budget-at-Risk tally + the Honest KPI projection. P4 rocket + P5 hhfair/CGE (a 0-floor documented-Case-c) appear in the KPI projection, not as deep tracks.
- Added a Task-9 risk-layer note to KNOWN_UNKNOWNS Unknowns 1.1/1.2/2.1/3.1/3.2 (Verified by / Date / Findings — the prior + single-model validation + Sprint-33 exit + reallocation / Decision).
- Fixed this task's verification grep to the template-consistent `## Track P` heading style (the SPRINT_31 template + this doc use `## Track P1 — …`, not `## P1`).

### Result

- **P1 mine** (Prior **Medium**): the `N`-derivation transfer → warm residual → 0 (Case-a, `modelstat`) → presolve MS-1 by Day 5; 5th-coupling REPLAN → Sprint-33 deeper head-offset architecture; ~8–14h → P6 + P7. mine's +1 Solve is one of the two firm Solve movers.
- **P2 sarf** (Prior **Medium-High**, a failed-architecture rebuild): the Day-0 O(active=398)-not-O(369K) timing probe caps the dominant risk early; timeout-re-trigger REPLAN → documented re-scoping; ~8–16h → P6 + P7. Translate +1 conditional on this track (lowest-leverage KPI).
- **P3 camcge** (Prior **Medium**, step-2-only): step 1 (`nu_mps_fx.l=-mps.m`, `mps.m=−209.861`) is a near-certain general emit fix that lands regardless (partly de-risking P3); step 2 gated on the `/tmp`-to-MS-1 (191.7346) prototype before any Walras `src/` change; Epic-5-deferral REPLAN → camcge stays `model_infeasible` in S32, +1 Solve at risk; ~6–12h → P6 + P7.
- **Honest KPI projection:** Solve ≥ 109 needs BOTH mine [P1] AND camcge [P3] (the 2-element mover set; rocket [P4] a conditional third) — the most REPLAN-sensitive KPI; genuine floor 74 → ≥ 75 conditional on mine/camcge **cold-matching** or a P6 emit change, NOT presolve-methodology (P5 delivers 0 floor); Translate +1 conditional on sarf. Reallocation order on any REPLAN: P6 → P7 → the rocket [P4] forcing tail.

### Verification

```bash
# Risk-assessment doc exists
test -f docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md && echo "risk assessment present"

# Each deep track has a hypothesis + REPLAN exit + reallocation target
grep -cE "^## Track P[123]" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md
grep -ciE "REPLAN exit|reallocat|slip valve" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md

# The honest KPI projection is present
grep -iqE "conditional|Solve ≥ ?109|genuine floor" docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md && echo "honest projection present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md` — per-track (P1/P2/P3) hypothesis + single-model validation + PROCEED/REPLAN threshold + Sprint-33 REPLAN exit + budget-reallocation order + the honest KPI projection
- Updated `KNOWN_UNKNOWNS.md` REPLAN-prone unknowns with the assessment
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 1.1, 1.2, 2.1, 3.1, 3.2

### Acceptance Criteria

- [x] P1/P2/P3 each have a hypothesis + single-model validation + PROCEED/REPLAN threshold
- [x] Each has a pinned Sprint-33 REPLAN exit with its de-risked hand-off
- [x] The budget-reallocation order (freed hours → firm tracks / P6 / P7) is defined
- [x] The honest KPI projection (Solve ≥ 109 / genuine floor ≥ 75 / Translate +1, each conditional) is recorded
- [x] Unknowns 1.1, 1.2, 2.1, 3.1, 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-14
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 32 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 8
**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

### Objective

Confirm the Sprint-28–31 diagnostic tooling covers the new Sprint-32 model classes (the mine bound-multiplier residual test, the sarf 4-D sparsification path, the Case-c classifier), and analyze the Priority-6 backlog fix-surfaces (the #1111/#1112 offset-alias generalization beyond polygon/ps2; the residual `model_infeasible` cohort re-triage) plus the Priority-7 property-catalog + genuine-floor-tracking + Epic-4-`SUMMARY` groundwork.

### Why This Matters

Sprint 32's tools are **reused, not rebuilt** — but the audit must confirm they cover the new classes before Day 1, and identify any minimal extension (e.g., the Case-c classifier is a `kkt_residual.py` extension, designed in Task 7). Priority 6 is the "fill the 14-day budget + absorb REPLAN slack" track: the offset-alias generalization (does the #1111/#1112 second-index-transpose core correct other 2-index-transpose models' cold emits?) and the failure-cohort re-triage (do agreste/cesam/fawley/lnts re-triage to a fixable Case-b?) are the candidate additional gains. Analyzing these fix-surfaces before the sprint keeps Day-1 P6 work from being an open-ended search.

### Background

- The Sprint-28–31 tooling: `scripts/diagnostics/kkt_residual.py`, the golden-staleness gate, the presolve-divergence detector, the `--resolve-changed` checkpoint re-solve, the `--force` scaffold, the AD cross-term property catalog (`tests/integration/emit/test_ad_crossterm_shapes.py`).
- The P6 backlog: #1111/#1112 (offset-alias general-alias core, landed for polygon/ps2 in Sprint 31); the residual `model_infeasible` cohort (agreste/cesam/fawley/lnts, non-Sprint-32-scoped but re-triageable).
- The P7 infrastructure: the property-catalog extension surface (head-offset 4th-site + sarf 4-D shapes), the PR25 genuine-floor tracking, the `--resolve-changed` checkpoint refresh, the Epic-4 `SUMMARY.md` groundwork (Sprint-30 retro §5 front-loading recommendation).

### What Needs to Be Done

1. **Tooling readiness audit.** For each Sprint-32 track, confirm the reusable tool that guards it (P1 → `kkt_residual.py` + a bound-multiplier residual test; P2 → the translate-budget timer + golden-staleness; P3 → `kkt_residual.py` + the detector; P4 → the `--force` scaffold; P5 → the Case-c classifier extension); identify the minimal extension per track.
2. **P6 offset-alias generalization analysis.** Audit the corpus for other 2-index-transpose models (the #1111/#1112 second-index shape) whose cold emit the general-alias core would correct; list the candidates + the `--resolve-changed` GO gate.
3. **P6 failure-cohort re-triage analysis.** Run `kkt_residual.py` on agreste/cesam/fawley/lnts; record which (if any) re-triage to a fixable Case-b vs genuine Case-c, with banked diagnoses for Sprint 33.
4. **P7 groundwork.** Enumerate the property-catalog fixtures to add (head-offset 4th-site + sarf 4-D), the genuine-floor-tracking recompute surface (S32–S35 footnote ⁸), and the Epic-4 `SUMMARY.md` skeleton (sprint-by-sprint history).

### Changes

- Authored `docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md` from read-only tool runs: §1 the per-track tooling-readiness audit (all 6 tools present + confirmed; minimal extension per track), §2 the P6 offset-alias generalization candidate list + the `--resolve-changed` GO gate, §3 the P6 failure-cohort re-triage (agreste/cesam/fawley/lnts harness sweep), §4 the P7 property-catalog fixtures + genuine-floor recompute + Epic-4-SUMMARY skeleton.
- Set KNOWN_UNKNOWNS Unknowns 6.1/6.2/6.3/7.1/7.3 → ✅ VERIFIED (Verified by / Date / Findings / Evidence / Decision from the sweeps).

### Result

- **Tooling:** no blocking gap. The only tool-code change is the P5 Case-c classifier in the diagnostic harness `scripts/diagnostics/kkt_residual.py` (not `src/`; no emit change); P1/P3/P4 reuse existing tools; the two new coverage adds are P7 fixtures (shape12/shape13). `--resolve-changed --since-commit 4cbf8bff --dry-run` = GO (0 at Day 0).
- **P6 offset-alias (6.1):** the structural audit surfaces **cpack** (circle-packing distance sibling, highest prior) + ps3_s_scp/ps5_s_mn/ps10_s_mn/partssupply; the CGE cluster + himmel16 are excluded (Case-c / non-convex). Per-candidate cold-emit diff is Day-1 P6 work.
- **P6 cohort re-triage (6.2):** **fawley** = clean fixable Case-b (convex LP, uniform `stat_bq(*,fuel-oil)` rel 0.973 — the strongest +Solve candidate, overlapping the second-index family); **agreste** = candidate Case-b, rel 2.0 on a convex LP, but a double-`solve` driver (scope caveat); **cesam** = Case-c (bilinear SAM) / driver; **lnts** = Case-c (bilinear-`step` optimal-control, rocket-family). 2 candidate +Solve + 2 banked Case-c.
- **Checkpoint (6.3/7.3):** the `--resolve-changed` GO gate is ready; the one nuance is sarf's *new* golden (caught by the golden-staleness gate, not `--resolve-changed`). **P7 fixtures (7.1):** shape12 (head-offset 4th-site) + shape13 (sarf 4-D `task`) designed.

### Verification

```bash
# Analysis doc exists
test -f docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "analysis present"

# Reusable tools confirmed present
test -f scripts/diagnostics/kkt_residual.py && echo "kkt_residual harness present"
grep -q "resolve.changed\|resolve_changed" scripts/gamslib/run_full_test.py && echo "--resolve-changed present"

# P6 offset-alias candidates + failure-cohort re-triage recorded
grep -iqE "1111|1112|second-index|transpose" docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "offset-alias analysis present"
grep -oiE "agreste|cesam|fawley|lnts" docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md | sort -u

# P7 property-catalog + Epic-4-SUMMARY groundwork noted
grep -iqE "property|shape|SUMMARY|genuine-floor" docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "P7 groundwork present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md` — the per-track tooling-readiness audit + minimal extensions, the P6 offset-alias generalization candidate list + `--resolve-changed` gate, the P6 failure-cohort re-triage (Case-b vs Case-c per model), and the P7 property-catalog + genuine-floor-tracking + Epic-4-SUMMARY groundwork
- Updated `KNOWN_UNKNOWNS.md` Category-6/7 unknowns
- Updated `KNOWN_UNKNOWNS.md` with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3

### Acceptance Criteria

- [x] The reusable tool guarding each Sprint-32 track is confirmed, with the minimal extension per track identified
- [x] The P6 offset-alias generalization candidate list (other 2-index-transpose models) is recorded with the `--resolve-changed` GO gate
- [x] The P6 failure-cohort (agreste/cesam/fawley/lnts) is re-triaged (Case-b vs Case-c per model) with banked diagnoses
- [x] The P7 property-catalog fixtures + the genuine-floor-tracking recompute surface + the Epic-4-SUMMARY skeleton are enumerated
- [x] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 32 Detailed Schedule

**Status:** ✅ COMPLETE
**Completed:** 2026-07-14
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 32 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–10
**Unknowns Verified:** (integrates all — 1.1–7.3)

### Objective

Create the detailed Sprint 32 day-by-day schedule (Day 0 setup + Days 1–13 execution) with per-day prompts, integration risks, complexity estimates, checkpoint schedule (Days 5 + 10), and contingency/REPLAN slip valves — incorporating every prep-task output. This is the FINAL prep task because it depends on all others.

### Why This Matters

The schedule is where the pinned root causes (Tasks 3/4/5), the Phase-0 gates (Task 8), the REPLAN assessment (Task 9), and the tooling/backlog analysis (Task 10) become an executable plan at ≤ 12 hours/day (the PROJECT_PLAN Sprint 32 budget: 80–120h over 14 days). It sequences the deepest tracks early (P1 mine + P3 camcge — the two firm +Solve movers — front-loaded so a REPLAN surfaces by the Day-5 checkpoint, not Day 11), front-loads the tractability probes, and pins the checkpoint + REPLAN slip valves so a stalled track reallocates cleanly.

### Background

- All prep-task outputs: KNOWN_UNKNOWNS (Task 1), BASELINE_METRICS (Task 2), the three design docs (Tasks 3/4/5), the rocket/hhfair packaging (Tasks 6/7), the Phase-0 gates (Task 8), the REPLAN risk assessment (Task 9), the tooling/backlog analysis (Task 10).
- Sprint 32 scope: `PROJECT_PLAN.md` §"Sprint 32" (Priorities 1–7 + Acceptance Criteria + Estimated Effort 80–120h + Risk Level HIGH).
- The Sprint-31 detailed schedule (`SPRINT_31/PLAN.md` if present) as the format template.

### What Needs to Be Done

1. **Author the day-by-day schedule** (Day 0 + Days 1–13) with per-day objectives, prompts, integration risks, and complexity estimates; front-load P1 (mine) + P3 (camcge) so a REPLAN surfaces by the Day-5 checkpoint.
2. **Place the checkpoints** (Day 5 + Day 10) using the `--resolve-changed` checkpoint re-solve, with GO/NO-GO criteria referencing the Day-0 baseline (Task 2).
3. **Wire the REPLAN slip valves** (Task 9) into the schedule — which day each track's PROCEED/REPLAN gate fires, and where freed budget flows.
4. **Set the day-by-day prompts** (a `prompts/PLAN_PROMPTS.md` companion if the epic convention uses one), ≤ 12 h/day, with the final Day-13 retest + closeout.

### Changes

- Authored `docs/planning/EPIC_4/SPRINT_32/PLAN.md` — the day-by-day schedule (Day 0 + Days 1–13): §1 goal, §2 acceptance criteria, §3 sequencing constraints, §4–§14 the per-day objectives/gates/complexity, §15 the budget summary (~99 h mid, ≤ 12 h/day), §16 Phase-0 coverage, §17 unknowns snapshot, §18 risk register, §19 related docs.
- Authored `docs/planning/EPIC_4/SPRINT_32/prompts/PLAN_PROMPTS.md` — one self-contained execution prompt per day (Day 0 + Days 1–13) with the cross-cutting rules (PR24/PR25/PR27 + `modelstat`-before-objective) + per-day branch/Phase-0-gate/quality-gate/PR steps.
- Authored `docs/planning/EPIC_4/SPRINT_32/SPRINT_LOG.md` skeleton — the 14-row progress table (all 🔵 PENDING) + the targets + the honest KPI projection, to fill per day.
- Set KNOWN_UNKNOWNS §"Next Steps" → ✅ PREP PHASE COMPLETE (all 25 unknowns VERIFIED; the in-sprint-only execution gates noted; **Sprint 32 GO for Day 0**).
- Fixed this task's verification grep to the actual `## N. Day …` heading style (the S31 template + this PLAN use numbered section headings).

### Result

- **Front-loaded the two firm +Solve movers:** P1 mine (Days 1–3, close-or-REPLAN Day 3) + P3 camcge (Days 4–5, close-or-REPLAN + **Checkpoint 1** Day 5) — both PROCEED/REPLAN gates fire by the Day-5 checkpoint. Then P2 sarf (Days 6–8, tractability gate Day 7), P4 rocket (Day 9), P5 Case-c classifier + **Checkpoint 2** (Day 10), P6 adjacent backlog + REPLAN-slack (Day 11), P7 infra + REPLAN-slack (Day 12), retest + closeout (Day 13).
- **Budget ~99 h mid** (80 h if deep tracks REPLAN early, 120 h if all PROCEED) — fits the 168 h cap with ≥ 48 h slack; no day > 12 h.
- **REPLAN slip valves wired** (Task 9): mine 5th-coupling → Sprint-33 architecture; camcge Walras step-2 → Epic-5 numéraire (step 1 lands regardless); sarf timeout → re-scoping — each freeing budget to P6 → P7 → the rocket tail.
- All 25 prep unknowns integrated; **Sprint 32 is GO for Day 0**.

### Verification

```bash
# Schedule doc exists
test -f docs/planning/EPIC_4/SPRINT_32/PLAN.md && echo "schedule present"

# Day 0 + Days 1–13 present (11 day-sections; some cover a range, e.g. "Days 4–5")
grep -cE "^## [0-9]+\. Days? [0-9]" docs/planning/EPIC_4/SPRINT_32/PLAN.md   # expect >=9 sections covering Day 0–13
grep -cE "Day [0-9]+" docs/planning/EPIC_4/SPRINT_32/prompts/PLAN_PROMPTS.md   # 14 per-day prompts (Day 0–13)

# Checkpoints (Day 5 + Day 10) + REPLAN slip valves referenced
grep -ciE "Checkpoint|Day 5|Day 10" docs/planning/EPIC_4/SPRINT_32/PLAN.md
grep -iqE "REPLAN|slip valve|reallocat" docs/planning/EPIC_4/SPRINT_32/PLAN.md && echo "REPLAN slip valves present"

# ≤12h/day budget honored (no day > 12h)
grep -iqE "≤ ?12|12 ?h/day|168" docs/planning/EPIC_4/SPRINT_32/PLAN.md && echo "budget cap referenced"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_32/PLAN.md` — the day-by-day Sprint 32 schedule (Day 0 + Days 1–13) with per-day objectives/prompts/risks/complexity, the Day-5/Day-10 checkpoints, the REPLAN slip valves, and the Day-13 retest + closeout
- (If the epic convention uses one) `docs/planning/EPIC_4/SPRINT_32/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- Updated `KNOWN_UNKNOWNS.md` (any scheduling-surfaced unknowns) + CHANGELOG entry

### Acceptance Criteria

- [x] PLAN.md created with Day 0 + Days 1–13, each with objectives / prompts / integration risks / complexity estimates
- [x] P1 (mine) + P3 (camcge) front-loaded so a REPLAN surfaces by the Day-5 checkpoint
- [x] Day-5 + Day-10 checkpoints placed with GO/NO-GO criteria vs the Day-0 baseline
- [x] REPLAN slip valves (Task 9) wired into the schedule with budget reallocation
- [x] ≤ 12 h/day budget honored (total 80–120h ≤ 168h); Day-13 retest + closeout scheduled
- [x] CHANGELOG updated

---

## Summary: Prep Task Execution Order

**Recommended order** (respecting dependencies; Tasks 1 + 2 first, the design tasks in the middle, the schedule last):

1. **Task 1 — Known Unknowns List** (Critical, no deps) — surfaces the risks that shape every downstream task.
2. **Task 2 — Day-0 Baseline + Genuine-Floor Re-Baseline** (Critical, no deps; parallel with Task 1) — the metric ground truth (Solve 107 / Match 92 / genuine floor 74; 142-corpus vs all-219).
3. **Tasks 3 + 4 + 5 — mine / sarf / camcge design** (Critical/High, after Tasks 1/2; parallelizable) — the three deep-track designs that size the sprint.
4. **Tasks 6 + 7 — rocket packaging / hhfair Case-c** (Medium, after Task 1; parallelizable) — the two documentation/hand-off tracks.
5. **Task 8 — Phase 0 Acceptance Gates** (Critical, after Tasks 1/3/4/5) — the PROCEED/REPLAN gate per track.
6. **Task 9 — REPLAN-Prone Track Risk Assessment** (High, after Tasks 3/4/5/8) — the budget-reallocation slip valves.
7. **Task 10 — Tooling Readiness + Backlog Fix-Surface** (Medium, after Tasks 1/8) — the P6/P7 fill + reuse.
8. **Task 11 — Detailed Schedule** (Critical, after Tasks 1–10) — the executable 14-day plan.

### Success Criteria (all prep tasks complete)

- [x] **KNOWN_UNKNOWNS.md** authored — 25 unknowns across 7 categories, each with priority + verification (all 25 ✅ VERIFIED); the three REPLAN-prone deep tracks + the bound-multiplier + `stat_mps`-ordering Criticals captured (Task 1).
- [x] **BASELINE_METRICS.md** authored — Day-0 = Sprint 31 final (Solve 107 / Match 92 / genuine floor 74 / model_infeasible 7 / Translate 135 / Tests 5,074 / all-219 Match 95); the 142-corpus vs all-219 distinction + the checkpoint anchor recorded (Task 2).
- [x] **Three deep-track design docs** authored — mine bound-multiplier (Task 3), sarf `stat_task` sparsification (Task 4), camcge `stat_mps` + Walras (Task 5) — each with a named emit site + a REPLAN exit.
- [x] **rocket PATH-consultation input** packaged (Task 6) + **hhfair/CGE Case-c classifier** designed (Task 7).
- [x] **PHASE_0_ACCEPTANCE_GATES.md** authored — one PROCEED/REPLAN gate per P1–P5 (Task 8).
- [x] **REPLAN_RISK_ASSESSMENT.md** authored — per-track REPLAN exits + budget reallocation + the honest KPI projection (Task 9).
- [x] **TOOLING_AND_BACKLOG_ANALYSIS.md** authored — tooling readiness + P6 offset-alias/failure-cohort + P7 groundwork (Task 10).
- [x] **PLAN.md** authored — the day-by-day 14-day schedule (+ `prompts/PLAN_PROMPTS.md` + the `SPRINT_LOG.md` skeleton) with checkpoints + REPLAN slip valves at ≤ 12 h/day (Task 11).
- [x] **Total prep effort** tracked; the critical path (Task 1 → 3 → 8 → 9 → 11) completed before Sprint 32 Day 1.

**✅ Sprint 32 is GO for Day 0** (2026-07-14): every prep task above is ✅ COMPLETE, all 25 Known Unknowns are ✅ VERIFIED (none WRONG), each of P1–P5 is behind a PROCEED/REPLAN gate with a pinned Sprint-33 REPLAN exit, and the detailed schedule front-loads the two firm +Solve movers (mine + camcge) so a REPLAN surfaces by the Day-5 checkpoint.

---

## Appendix: Document Cross-References

### Sprint 32 scope + goals

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 32 (Weeks 29–30): Sprint 31 Carryforward …" — the Priorities 1–7, Deliverables, Acceptance Criteria, Estimated Effort (80–120h), Risk Level (HIGH)
- `docs/planning/EPIC_4/GOALS.md` — the Epic 4 strategic themes this sprint advances: **#4 Solve Completion** (mine + camcge), **#5 Solution Matching** (genuine floor 74 → ≥ 75), **#6 Infeasible/Unbounded Handling** (rocket + hhfair/CGE documented Case-c)

### Sprint 31 carryforward provenance

- `docs/planning/EPIC_4/SPRINT_31/SPRINT_RETROSPECTIVE.md` §4 — the five Sprint-32 carryforwards + §3 the control-first / assert-`modelstat` lessons
- `docs/planning/EPIC_4/SPRINT_31/SPRINT_LOG.md` — the Day-by-day REPLAN records (Day 3 mine, Days 6–7 camcge, Day 8 sarf, Day 10 hhfair/CGE, Day 11 rocket) + the Day-13 closeout
- `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` — the PR25 genuine-vs-methodology operational definition + the Day-13 142-corpus vs all-219 recompute
- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` — the Sprint-31 unknowns to migrate

### Per-track ISSUE docs (the pinned root causes)

- `docs/issues/ISSUE_1443_mine-head-domain-offset-mcp-infeasible.md` — the 4th bound-complementarity site (P1)
- `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md` — the 369K-instance 4-D `task` finding (P2)
- `docs/issues/ISSUE_1330_camcge-model-infeasible-after-1245.md` — the CASE_B `stat_mps` verdict + price-pin (P3)
- `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` — the exhausted-lever survey (P4)
- `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md` — the Case-c control-refutation (P5)

### Research / design / follow-on references

- `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 — the rocket PATH-consultation question (P4)
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 — the PATH hand-off draft + the exhausted PATH-option survey
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` — the camcge Epic-5 scoping (P3)
- `docs/research/minmax_path_validation_findings.md` — the PATH validation methodology (reference for the P4 consultation packaging)

### Reusable tooling (reused, not rebuilt)

- `scripts/diagnostics/kkt_residual.py` — the KKT-residual harness (Case-a/b/c verdict) — P1/P3/P5 localization + the Case-c classifier extension
- `scripts/gamslib/run_full_test.py` — the `--resolve-changed --since-commit <SHA>` checkpoint re-solve — the Day-5/Day-10 gates
- The golden-staleness gate + the presolve-divergence detector + the `--force {homotopy,multistart,optfile}` scaffold + the AD cross-term property catalog (`tests/integration/emit/test_ad_crossterm_shapes.py`)

### Prep-plan format precedent

- `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md` + `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md` — the original PREP_PLAN format
- `docs/planning/EPIC_4/SPRINT_31/PREP_PLAN.md` + `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` — the same-epic refined descendants this plan mirrors

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team
**Status:** 🔵 Prep IN PROGRESS — Task 1 ✅ COMPLETE; Tasks 2–11 🔵 NOT STARTED (11 tasks, 36–51h, critical path Task 1 → 3 → 8 → 9 → 11)
