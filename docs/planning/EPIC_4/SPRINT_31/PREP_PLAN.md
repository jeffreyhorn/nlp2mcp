# Sprint 31 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 31 begins
**Timeline:** Complete before Sprint 31 Day 1
**Goal:** Set up Sprint 31 for success — land the Sprint 30 Solve/Match carryforwards the Day-13 closeout REPLAN'd, each of which now carries a *de-risked, control-verified* recipe rather than an open question (`docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §4). The core is the **mine head-domain-offset architecture** (#1443), which Sprint 30 Day 6 found needs a **foundational IR change first** — the head-offset position+amount is not stored today (only a `has_head_domain_offset` bool), so Sprint 31 plumbs the head-offset detail through parse → normalize → KKT and *then* builds the shared 3-site index-map helper. Alongside it: the **offset-alias general-alias core #1111/#1112** (polygon — Sprint 30 Day 7 control-verified the exact 4-term fix at warm-match 0.780, Day 8 implemented+verified the objective-successor half; the remaining **distance-Jacobian second-index** cross-term is the general-alias core that must land coupled); the **camcge #1330 dual-consistent Walras transform** (Sprint 30 Day 11 found the design's drop-row is primal-correct but breaks the MCP *dual* — the price-pin gives the correct omega 191.735, so the fix is a dual-consistent multiplier redefinition, not the naive row-drop); the **#1385 sarf symbolic-emit workstream** (the atomic runtime-guard cross-term emit is the Sprint-26-failed architecture, rebuilt as a dedicated builder-pipeline-aware path with the banked `stat_task` derivation); the **cold-convex obj-grad residue** (hhfair `stat_u` / CGE `stat_xp` — the objective-defining-intermediate-variable family whose sign-flip fix was *control-refuted* three times in Sprint 30, so it needs a non-sign-flip treatment); and **rocket #1462 non-convex forcing** advancing to the PATH-consultation input (the `--force` scaffold landed Sprint 30; the concrete PATH question is banked). Targets: Solve 107 → ≥ 109; Match maintain ≥ 92 / genuine floor 70 → ≥ 73; model_infeasible 7 → ≤ 5; Translate maintain ≥ 135 (stretch +1 via #1385); Tests 4,997 → ≥ 5,000.

**Key Insight from Sprint 30:** Sprint 31 is **specification-bound, not diagnosis-bound** — every carryforward inherits a Sprint-30 *control-verified* recipe or a *precisely-pinned* root cause, so Sprint 31 implements against specifications rather than re-diagnosing. But two structural lessons from Sprint 30 dominate the prep: (1) **the banked recipe is still a hypothesis that must survive a control experiment before any high-blast-radius `src/` change** — Sprint 30 *refuted five* banked diagnoses this way (the obj-grad sign flip three times, the Class-B `stat_pz` "coefficient bug" which was really case-normalization, and the camcge Walras drop-row which broke the dual); the single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes. (2) **"Solution-preserving on paper" ≠ "correct in the MCP" — always check the dual side** (the camcge lesson). Sprint 31 prep MUST therefore (a) turn each banked recipe into a **design the implementation follows** — most critically the P1 head-offset **IR-plumbing** design, which is a *foundational* change (parse→normalize→KKT) that gates everything downstream on P1; (b) front-load the **tractability probes** the Sprint-30 retro (§3 lesson 5) said would have re-allocated budget earlier (the P1 IR-plumbing blast radius, the P2 #1111/#1112 general-alias boundary, the P4 O(constraints)-not-O(instances) emit budget); and (c) keep the PR24 control-experiment-before-implement gate as the standing discipline on P2/P3/P4/P5/P6.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 31 inherits the six Sprint-30 REPLAN'd carryforwards (Priorities 1–6 in `PROJECT_PLAN.md` §"Sprint 31"): the mine head-offset IR plumbing + shared 3-site helper (#1443); the offset-alias general-alias core #1111/#1112 (polygon); the camcge #1330 dual-consistent Walras transform (Epic 5); the #1385 sarf symbolic runtime-guard cross-term emit workstream; the cold-convex obj-grad residue (hhfair `stat_u` / CGE `stat_xp`); and rocket #1462 non-convex forcing advancing to the PATH-consultation input. Priority 7 (infrastructure) pulls the deferred property-test fixtures (the head-offset + polygon-successor shapes, unblockable once P1/P2 land) and the PR25 genuine-floor KPI tracking recompute.

Sprint 31 differs from Sprint 30 in one structural way: **Sprint 30 diagnosed and control-verified these tracks; Sprint 31 implements them against a banked recipe.** Because the recipes are already banked (the Sprint 30 SPRINT_LOG per-day entries, the per-track ISSUE docs, `CAMCGE_WALRAS_TRANSFORM_DESIGN.md`, `HEAD_OFFSET_ARCHITECTURE_DESIGN.md`, `NONCONVEX_FORCING_SURVEY.md` §4, and the AD cross-term property catalog with its `shape8`/`shape9` fixtures), Sprint 31 prep is lighter on *survey* and heavier on **design-before-implement + tractability-probe**: the hardest track (P1 head-offset) needs a concrete **IR-plumbing design** (where the head-offset δ + param offsets `li(k)`/`lj(k)` are stored on `EquationDef`, and how they round-trip through normalize→KKT) before any emit change; the second-hardest (P2 #1111/#1112) needs the **distance-Jacobian second-index design** that couples with the already-verified objective-successor half; and P3 (camcge Epic-5) needs the **dual-consistent multiplier-redefinition design** that the Day-11 price-pin recipe left open. The Sprint-28–30 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — Sprint 31 Known Unknowns List covering the seven carryforward tracks (each a banked Sprint-30 control-verified recipe that is still a Day-0-re-confirm hypothesis, PR24), the four deepest REPLAN-prone tracks (P1 foundational IR plumbing, P2 #1111/#1112 general-alias core, P4 symbolic-emit failed-architecture rebuild, P5 control-refuted obj-grad), the head-offset-IR-round-trip assumption, and the camcge dual-consistent-redefinition + degeneracy-detector false-positive scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 30 final → Sprint 31 Day 0 per-model bucket provenance, confirming Day-0 = Sprint 30 final (Solve 107, Match 92, genuine floor 70, model_infeasible 7, Translate 135, Tests 4,997) and that the PR25 genuine-vs-methodology re-baseline is the standing discipline.
3. **mine head-offset IR-plumbing design + round-trip reproduction (Priority 1 foundation)** — turn the Sprint-30 Day-6 REPLAN (the head-offset detail is not stored; `pr.has_head_domain_offset` is a bare bool) into a concrete IR-plumbing design: where the head-offset δ + `li(k)`/`lj(k)` live on `EquationDef`, how they survive normalization, and the round-trip unit reproduction that gates Phase 2 — sizing the deepest carryforward BEFORE the schedule is set.
4. **Offset-alias #1111/#1112 recipe re-confirmation + distance-Jacobian second-index design (Priority 2 foundation)** — re-confirm the Sprint-30 Day-7 control-verified 4-term polygon recipe on the current tree, and design the coupled distance-Jacobian second-index cross-term (the general-alias core `_add_indexed_jacobian_terms` drops) that must land with the already-verified objective-successor half.
5. **camcge dual-consistent Walras transform design + degeneracy-detector scope (Priority 3)** — design the dual-consistent multiplier redefinition (express the dropped market's dual via Walras' law) that the Day-11 price-pin recipe (omega 191.735) proves is needed, plus the S1∧S2∧S3 degeneracy detector scope that must NOT false-flag irscge/lrgcge/moncge/stdcge.
6. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — refresh/author the gates for the Sprint-31 dispositions (P1 IR round-trip + cold-INFES histogram, P2 shape8-enable, P3 price-pin→dual-consistent, P4 O(constraints) emit budget, P5 control-before-implement, P6 Case-c re-confirm).
7. **Diagnosis-heavy / REPLAN-prone track risk assessment (PR16)** — apply hypothesis-validation to P1 (foundational IR plumbing / 4th-site risk), P2 (#1111/#1112 general-alias core), P4 (symbolic-emit timeout re-trigger), and P5 (genuine Case-c); pin explicit Sprint 32 REPLAN exits + budget reallocation.
8. **Reusable-tooling readiness audit** — confirm the Sprint-28–30 tools cover the new Sprint-31 classes (the head-offset IR-round-trip test, the `--force` scaffold's forcing-lever entry, the shape8/head-offset property fixtures, the dual-consistent-Walras regression path) and identify any minimal extension.
9. **Backlog fix-surface analysis (Priorities 4 + 5 + 6)** — the #1385 sarf symbolic-emit patch site (the `_is_blowup_dynamic_subset_equation` 2-D extension + the parametric `stat_task` builder), the cold-convex obj-grad reduction site (hhfair `stat_u` via the defining-equation multiplier ν_objective), and the rocket forcing-lever exhaustion + PATH-consultation-input draft.
10. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 31 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 31 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 30 → Sprint 31 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine floor |
| 3 | mine Head-Offset IR-Plumbing Design + Round-Trip Reproduction (Priority 1 foundation) | Critical | 5–7h | Tasks 1, 2 | Priority 1 — mine (Solve) foundational IR change |
| 4 | Offset-Alias #1111/#1112 Recipe Re-Confirmation + Distance-Jacobian Second-Index Design (Priority 2 foundation) | High | 4–6h | Tasks 1, 2 | Priority 2 — polygon (genuine floor); #1110/#1111/#1112 core |
| 5 | camcge Dual-Consistent Walras Transform Design + Degeneracy-Detector Scope (Priority 3) | High | 4–5h | Task 1 | Priority 3 — Epic 5 dual-consistent implementation design |
| 6 | Refresh + Author Phase 0 Acceptance Gates for the Sprint-31 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 1, 3, 4, 5 | Priorities 1–6 — primary scope-correctness gate |
| 7 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 IR plumbing, P2 general-alias core, P4 symbolic emit, P5 obj-grad; PR16) | High | 3–5h | Tasks 3, 4, 5, 6 | Priorities 1, 2, 4, 5 — REPLAN-prone tracks |
| 8 | Reusable-Tooling Readiness Audit for the Sprint-31 Model Classes | Medium | 3–4h | Task 1 | All priorities — tooling reuse; feeds P7 |
| 9 | Backlog Fix-Surface Analysis (#1385 sarf symbolic emit; hhfair/CGE `stat_*` obj-grad; rocket forcing/PATH input) | Medium | 3–4h | Tasks 1, 8 | Priorities 4, 5, 6 — fix-surface hypotheses |
| 10 | Plan Sprint 31 Detailed Schedule | Critical | 3–4h | Tasks 1–9 | All priorities — sprint planning |

**Total Estimated Time:** 35–49 hours (~4.5–6 working days)

**Critical Path:** Task 1 → Task 3 → Task 6 → Task 7 → Task 10 (the deep-track chain — the head-offset IR-plumbing design (Task 3) sizes Priority 1 and feeds the Phase-0 gate refresh (Task 6), which feeds the REPLAN assessment (Task 7) and the schedule).
**Secondary Path:** Task 1 → Task 4 → Task 6 → Task 7 → Task 10 (the #1111/#1112 recipe re-confirmation + distance-Jacobian design feeds the P2 gate + the general-alias-core REPLAN assessment → schedule).
**Tertiary Path:** Task 1 → Task 5 → Task 6 → Task 7 → Task 10 (the camcge dual-consistent design feeds the P3 gate + the Epic-5 REPLAN assessment → schedule).
**Quaternary Path:** Task 1 → Task 8 → Task 9 → Task 10 (tooling readiness → backlog fix-surface analysis → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 3 + 4 + 5 + 8 (independent after Tasks 1/2); Task 9 follows Task 8; Tasks 3/4/5 gate the Phase-0 refresh (Task 6).

---

## Task 1: Create Sprint 31 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~3.5h)
**Completed:** 2026-07-08
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive list of assumptions and unknowns for Sprint 31 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform every other prep task — particularly the head-offset IR-plumbing design (Task 3), the #1111/#1112 recipe re-confirmation + distance-Jacobian design (Task 4), the camcge dual-consistent design (Task 5), the Phase-0 gate refresh (Task 6), the REPLAN assessment (Task 7), and the tooling audit (Task 8). It also carries forward the end-of-sprint unknowns from Sprint 30 (the carryforwards in `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §4 plus any open items in `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 31's central risk is that its carryforwards are the tracks Sprint 30 REPLAN'd *precisely because they proved to need foundational or architectural work* — the head-offset needs an IR change (parse→normalize→KKT), #1111/#1112 needs the general-alias AD core, camcge needs a dual-side transform, #1385 needs a failed-architecture rebuild, and the obj-grad residue's obvious fix was *refuted three times*. Each carries a banked recipe, but PR24 still holds: **the banked recipe is a Day-0-re-confirm hypothesis, not fact** — Sprint 30 refuted five banked diagnoses via control experiments before any bad ship. The Known Unknowns List must therefore (a) frame each banked recipe as a re-verifiable hypothesis, (b) flag the **head-offset-IR-round-trip** assumption as a Critical unknown (if the head-offset δ + `li(k)`/`lj(k)` cannot round-trip normalize→KKT cleanly, the entire P1 foundation shifts), (c) flag the four deepest REPLAN-prone tracks (P1 IR plumbing, P2 #1111/#1112 core, P4 symbolic-emit rebuild, P5 control-refuted obj-grad) with a single-model or control-experiment validation as their verification (PR16), and (d) surface the camcge **degeneracy-detector false-positive** risk (silently transforming a well-posed model would corrupt it) *plus* the new **dual-consistent-redefinition** correctness risk (the Day-11 lesson: the primal-preserving drop-row broke the dual).

### Background

- Sprint 30 Retrospective: `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` (§4 "Sprint-31 carryforwards" — the seven carryforward tracks; §2 "What landed (firm)" — robert obj-grad / hhfair `$184` / Class-B case-normalization / the `--force` scaffold that already landed; §1 metrics table; §3 the five refuted-hypothesis + dual-side lessons)
- Sprint 30 Known Unknowns: `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` (the 8 Sprint-30 categories — review for open/end-of-sprint items; especially the Category-1 head-offset, Category-2 rocket, Category-5 offset-alias, Category-6 camcge, and Category-7 Class-B `stat_pz` / cold-convex unknowns whose Sprint-31 dispositions are now known)
- Sprint 31 scope: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31 (Weeks 27–28)" (Priorities 1–7 + Acceptance Criteria + Estimated Effort + Risk Level)
- Carryforward + backlog issues: `docs/issues/ISSUE_{1443,1143,1146,1330,1385,1236}_*.md` (local) + GitHub #1462 rocket, #1111, #1112 (the Sprint-31 tracks) + the cold-convex CGE cluster (irscge/lrgcge/moncge). **Note:** #1443's ISSUE doc records the head-offset 3-site trace + the "not stored in IR" blocker; #1143 records the control-verified 4-term recipe + the Day-8 objective-half implementation; #1330 records the price-pin recipe (omega 191.735) + the dual-flaw; #1385 records the banked `stat_task` derivation — these are the Day-0-re-confirm starting points.
- Sprint-30 diagnostic + design docs that Sprint 31 consumes: `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (the 3-site architecture), `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (§4 the PATH hand-off draft), `docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` (the Day-11 dual-consistent refinement + price-pin), the `SPRINT_30/COLD_CONVEX_*`/Class-B cohort survey material

### What Needs to Be Done

1. **Review Sprint 30 carryforward / end-of-sprint KUs.** Migrate any open items from `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` and the retro §4 carryforwards into Sprint 31 numbering with full text and forward-links to the Sprint 31 categories they drive.

2. **For each Priority area, brainstorm unknowns** (assumption / how-to-verify / priority / risk-if-wrong), organized by category aligned to the PROJECT_PLAN priorities:

   **Category 1 (P1 mine head-offset IR plumbing + shared 3-site helper — #1443):**
   - Can the head-offset detail (position `l`, amount `+1`) + the param offsets `li(k)`/`lj(k)` be stored on `EquationDef` and **round-trip through normalization** (which today collapses `pr.domain = (k,l,i,j)` and drops the `l+1` head), so the KKT layer sees them? **(Critical — PR16; this is the foundational blocker Day 6 hit; if the round-trip is not clean, the whole P1 timeline shifts.)**
   - Once plumbed, does the single index-map helper parameterized by (head-offset δ, param offsets) correctly drive all three sites (`comp_pr` emission, `--nlp-presolve` dual transfer, the landed `stat_x` cross-term), or does a **4th site** surface (deeper architecture → REPLAN)?
   - Does the fix leave the cold LCP feasible (mine's ~4.07e10 blowup across all four k-directions resolved to MS 1), or is there a residual bound-complementarity coupling?

   **Category 2 (P2 offset-alias general-alias core #1111/#1112 — polygon):**
   - Does the Sprint-30 Day-7 control-verified **4-term recipe** (warm-match 0.780) still reproduce on the current tree, and does the coupled **distance-Jacobian second-index** cross-term (which `_add_indexed_jacobian_terms` drops) land together with the already-verified objective-successor half without regressing the CGE multi-pattern cohort? **(Critical — PR16; the Day-8 objective half was reverted precisely because it can't ship alone.)**
   - Is the second-index cross-term gateable to the var-at-two-indices shape, or does it require the full #1111 alias-aware-differentiation / #1112 dollar-condition-propagation core (→ Sprint 32 architectural filing)?
   - himmel16 is documented non-convex (Day-7 sign-fix refuted) — confirm no emit fix is expected to convert it (scope guard).

   **Category 3 (P3 camcge #1330 dual-consistent Walras transform → Epic 5):**
   - Does the **dual-consistent multiplier redefinition** (express the dropped market's dual via Walras' law so it stays available in the stationarity) reach MODEL STATUS 1 at omega 191.735, where the naive drop-row gave omega 299 / MS-4? **(Critical — the Day-11 price-pin proves the target allocation; the dual-consistent emit is the unproven step.)**
   - Does the S1∧S2∧S3 degeneracy detector flag **only** camcge across irscge/lrgcge/moncge/stdcge (no false-positive on a well-posed CGE)? **(Critical — silently redefining a dual on a non-degenerate model would corrupt it — the "check the dual side" lesson.)**
   - Is the redundant-row + numéraire selection a single automatic rule, or a per-model declaration fallback?

   **Category 4 (P4 #1385 sarf symbolic runtime-guard cross-term emit):**
   - Does extending `_is_blowup_dynamic_subset_equation` from srpchase's 1-D to sarf's **2-D** dynamic-subset shape (`tbal(g,t)$taskposs`), plus a new parametric `stat_task` cross-term emit, materialize the banked 6-guarded-term derivation with **no set-name-literal multiplier indices** (the Sprint-26 `nu_slack("srn")` failure mode)? **(High — PR16; this is a failed-architecture rebuild.)**
   - Is the symbolic re-emit **O(constraints), not O(instances)** (sarf has 1,152 Cartesian instances), so it stays inside the translate budget rather than re-triggering the Option-1 timeout?

   **Category 5 (P5 cold-convex obj-grad residue — hhfair `stat_u` / CGE `stat_xp`):**
   - Does the objective-gradient reduction **through the defining-equation multiplier (ν_objective)** — NOT the control-refuted sign flip — reach the NLP optimum on hhfair (the cleanest instance, `stat_u` rel 2.0)? **(Critical — PR24/PR27 control-experiment-before-implement; the sign flip made hhfair 72→22 worse, refuted three times.)**
   - Does the same reduction convert the CGE cluster (irscge/lrgcge/moncge `stat_xp` rel ~0.06 after the Day-5 case-normalization fix) to Case-a (residual → 0), or is the family genuinely Case-c (documented non-convexity → Sprint 32)?

   **Category 6 (P6 rocket #1462 non-convex forcing → PATH-consultation input):**
   - Do any remaining **emittable-GAMS levers** (reformulating the `1/ht²`,`1/m²` division-by-variable Jacobian; scaled/relaxed continuation schedules) cross rocket's INFES (477 → 382 best but never converges), or is it confirmed intrinsic (→ the PATH-consultation input)?
   - Is the emit residual clean at the NLP point (Case-c) before any forcing attempt (the scope guard that keeps this a forcing problem, not an emit bug)?

   **Category 7 (P7 infrastructure — property tests, genuine-floor tracking):**
   - Does enabling `shape8_offset_alias_successor` (drop the strict-xfail) become the P2 completion gate once the distance-Jacobian half lands, and does the new **head-domain-offset fixture** correctly guard the P1 index-map once the IR plumbing lands?
   - Does the PR25 genuine-floor tracking recompute correctly against the S31–S33 re-baselined Match KPIs (footnote ⁸ ramp S31 ≥73), and do the `--resolve-changed` checkpoint targets cover the newly-touched emit sites (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit)?

3. **Assign priority + verification** to each unknown; write the Task-to-Unknown mapping appendix (which prep task resolves which unknown). Aim for **22–30 unknowns across 7 categories**.

4. **Update this PREP_PLAN** with the "Unknowns Verified" metadata per downstream task, and add a CHANGELOG entry.

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` (25 unknowns across the 7 Sprint-31 priority categories) + the Task-to-Unknown mapping appendix; added the "Unknowns Verified" metadata + Deliverables/Acceptance-Criteria lines on Tasks 2–10 below; CHANGELOG entry.

### Result

**COMPLETE (2026-07-08).** `KNOWN_UNKNOWNS.md` authored with **25 unknowns** (target 22–30) across **7 categories** aligned to the PROJECT_PLAN Sprint-31 priorities. Priority distribution: **6 Critical / 10 High / 6 Medium / 3 Low** (24% / 40% / 24% / 12%). Per-unknown research estimates sum to ~36h; the authoritative scheduling budget is the per-task 35–49h in this PREP_PLAN. Every unknown starts 🔍 INCOMPLETE and is assigned to a downstream prep task (2–10) in the mapping appendix. The six REPLAN-prone Criticals (1.1/1.2 head-offset IR plumbing, 2.2 offset-alias coupled core, 3.1/3.2 camcge dual-consistent + detector, 5.1 obj-grad ν_objective reduction) + the head-offset-IR-round-trip (1.1) + the camcge detection-heuristic false-positive (3.2) are captured as required. The two dominant Sprint-30 lessons (banked recipe = control-experiment-first hypothesis; check the dual side) thread through the Category-3/5 unknowns.

### Verification

```bash
# Document exists
test -f docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md && echo "KU list present"

# 7 categories aligned to the PROJECT_PLAN Sprint-31 priorities (expect 7)
grep -cE "^# Category [0-9]+:" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md

# Every numbered unknown carries a "How to Verify" section
u=$(grep -cE "^## Unknown [0-9]+\.[0-9]+:" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md)
v=$(grep -cE "^### How to Verify" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md)
echo "unknowns=$u how-to-verify=$v (should match)"

# The head-offset-IR-round-trip Critical unknown is present
grep -iqE "round.?trip|IR plumb" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md && echo "IR round-trip unknown present"

# The camcge dual-consistent / detector-false-positive unknowns are present
grep -iq "dual-consistent" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md && echo "dual-consistent unknown present"

# Carryforward + backlog issues referenced
grep -oE "#(1443|1462|1236|1385|1146|1143|1330|1111|1112|1110)" docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/KNOWN_UNKNOWNS.md` — 22–30 unknowns across 7 categories aligned to the Sprint-31 priorities, each with Priority / Assumption / Research Questions / How to Verify / Risk if Wrong / Estimated Research Time / Owner / Verification Results (🔍 INCOMPLETE)
- A Task-to-Unknown mapping appendix
- Updated `PREP_PLAN.md` "Unknowns Verified" metadata on Tasks 2–10
- CHANGELOG entry

### Acceptance Criteria

- [x] KNOWN_UNKNOWNS.md created with 7 categories aligned to the Sprint-31 priorities
- [x] 22–30 unknowns (25), each with Priority / Assumption / How to Verify / Risk if Wrong / Owner
- [x] The four deepest REPLAN-prone tracks (P1 IR plumbing, P2 #1111/#1112 core, P4 symbolic-emit rebuild, P5 control-refuted obj-grad) flagged Critical/High with a single-model or control-experiment validation
- [x] The head-offset-IR-round-trip Critical unknown is present (P1's foundation hinges on it — Category 1, Unknown 1.1)
- [x] The camcge dual-consistent-redefinition correctness AND the degeneracy-detector false-positive risks are both captured (P3 — Unknowns 3.1, 3.2)
- [x] Sprint-30 open/carryforward KUs migrated with forward-links (Sprint-30 Unknowns 1.1/1.2/5.1/6.1/2.2 → Sprint-31 Categories 1/2/3/6)
- [x] Task-to-Unknown mapping appendix present
- [x] CHANGELOG updated

---

## Task 2: Sprint 30 → Sprint 31 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~2h)
**Completed:** 2026-07-08
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** None (parallelizable with Task 1)
**Unknowns Verified:** 7.2

### Objective

Establish the authoritative Sprint 31 Day-0 baseline — the per-model bucket provenance (Parse / Translate / Solve / Match / model_infeasible / path_* ) carried forward from the Sprint 30 final retest — and re-run the PR25 genuine-vs-methodology re-baseline so the genuine-floor ramp (70 → ≥73) is measured against a clean starting line, not the methodology-inflated Match 92.

### Why This Matters

Every Sprint-31 KPI target is relative to Day 0 (Solve 107 → ≥109; genuine floor 70 → ≥73; model_infeasible 7 → ≤5). The Sprint-30 retro (§1) already warns that the genuine-floor lift is the *most* REPLAN-sensitive KPI (three of its four Sprint-30 contributors hit a REPLAN boundary or control-refutation), and that the Solve ≥109 stretch depends on *both* mine and camcge — both High-risk. A precise per-model Day-0 baseline is what makes the mid-sprint checkpoints (Day 5 / Day 10) able to distinguish a **genuine cold-match gain** from a **methodology reclassification** (the PR25 discipline), and what lets the Task-7 REPLAN assessment reallocate budget from a stalled track to a firm one *without* silently losing a bucket. This task also confirms the `--resolve-changed --since-commit <SHA>` checkpoint re-solve (the Sprint-29-built tooling) still anchors to the correct Sprint-30-final commit.

### Background

- Sprint 30 final metrics (from `SPRINT_30/SPRINT_RETROSPECTIVE.md` §1): Parse 142 · Translate 135 · **Solve 107** · **Match 92** (genuine floor **70**) · model_infeasible 7 · determinism ✅ ×3 `{0,1,42}` · Tests 4,997.
- Sprint 30 final retest DB: `data/gamslib/gamslib_status.json` (the per-model bucket source — machine-portable relative `mcp_file_used` paths per PR #1400).
- The PR25 genuine-vs-methodology template: `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` (bucket-provenance + genuine-floor derivation) and the SPRINT_30 SPRINT_LOG Day-13 genuine-floor tally.
- The checkpoint re-solve design: `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` + the `--resolve-changed` mode of `scripts/gamslib/run_full_test.py`.

### What Needs to Be Done

1. **Record the Sprint 30 → Sprint 31 Day-0 baseline** — copy the per-model bucket table from the Sprint-30 final DB into `SPRINT_31/BASELINE_METRICS.md`, confirming Day-0 = Sprint 30 final (Solve 107, Match 92, genuine floor 70, model_infeasible 7, Translate 135, Tests 4,997). Enumerate the 7 model_infeasible + the path_syntax_error / path_solve_terminated / path_solve_license members by name.
2. **Re-run the PR25 genuine-vs-methodology partition** — for each of the 92 Match models, classify genuine-cold-match vs methodology (warm/presolve/broadened-retry) so the genuine floor 70 is reproduced from first principles, and identify the specific Sprint-31 targets that would convert a methodology match to genuine (polygon [P2], hhfair + irscge/lrgcge/moncge [P5]).
3. **Confirm the checkpoint anchor** — verify `--resolve-changed --since-commit <Sprint-30-final-SHA>` selects the expected changed-emit set, so Days 5/10 checkpoints re-solve only the touched models.
4. **Record the per-priority Day-0 target model list** — mine, polygon, camcge, sarf, hhfair+CGE cluster, rocket — with their current bucket, so each track's success is a single-model bucket transition.

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` (Day-0 = Sprint 30 final; canonical bucket recompute; genuine-vs-methodology partition; per-Sprint-31-target bucket provenance + PR25 projection labels; checkpoint anchor). Updated `KNOWN_UNKNOWNS.md` Unknown 7.2 → ✅ VERIFIED (+ the Day-0-bucket aspect of 1.3/2.1/3.1/5.1/6.1). CHANGELOG entry.

### Result

**COMPLETE (2026-07-08).** Day-0 = Sprint 30 final, reused unchanged — no `src/`/`scripts/` drift since the S30 close (`ea4191dc`), so no fresh ~4 h retest. The canonical-scope recompute (`get_candidate_models`, 142 models) reproduces the Sprint 30 final headline exactly: **Parse 142 · Translate 135 · Solve 107** (63 `model_optimal` + 44 `model_optimal_presolve`) **· Match 92 · Mismatch 9 · model_infeasible 7 · path_syntax_error 8 · path_solve_terminated 4 · path_solve_license 9 · Tests 4,997.** The PR25 partition reproduces the **genuine floor 70** (methodology 22) from first principles, and the footnote-⁸ ramp aligns (S30 70 → S31 ≥ 73 → S32 ≥ 73 → S33 ≥ 75 → S34 ≥ 78). **Finding:** the committed DB is byte-unchanged since the *Sprint 28* close (`2717d542`) — both S29 and S30 netted no as-measured bucket change (all headline movers REPLAN'd; the firm wins were genuine-floor/robustness). The genuine-floor → ≥ 73 conversion map (polygon P2 / hhfair+CGE P5 / mine P1) is captured but flagged **conditional** per the Sprint-30 retrospective §3 (not independent +1s). himmel16 recorded as non-convex (not a converter). The `--resolve-changed --since-commit ea4191dc` checkpoint anchor selects **0 models at Day 0** (clean baseline; no changed goldens). Docs-only (no `src/`).

### Verification

```bash
# Baseline doc exists and records the Day-0 metrics
test -f docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md && echo "baseline present"
grep -qE "Solve[^0-9]*107" docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md && echo "Solve 107 recorded"
grep -qE "genuine floor[^0-9]*70|floor[^0-9]*70" docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md && echo "genuine floor 70 recorded"

# The DB is the Sprint-30-final source (relative paths per PR #1400)
python -c "import json,sys; d=json.load(open('data/gamslib/gamslib_status.json')); \
solved=[m for m,v in d.items() if v.get('solve_status')=='solved']; print('solved=',len(solved))"

# The per-priority Day-0 target models are enumerated
grep -oiE "mine|polygon|camcge|sarf|hhfair|rocket" docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/BASELINE_METRICS.md` — Day-0 per-model bucket table + the genuine-vs-methodology partition (genuine floor 70) + the per-priority target-model list with current buckets
- Confirmation that the `--resolve-changed` checkpoint anchor selects the correct changed-emit set
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 7.2
- CHANGELOG entry

### Acceptance Criteria

- [x] BASELINE_METRICS.md records Day-0 = Sprint 30 final (Solve 107 / Match 92 / genuine floor 70 / model_infeasible 7 / Translate 135 / Tests 4,997)
- [x] The genuine-vs-methodology partition reproduces the genuine floor 70 from first principles
- [x] The 7 model_infeasible + path_* members enumerated by name
- [x] Each Sprint-31 priority's Day-0 target model + current bucket listed (mine, polygon, camcge, sarf, hhfair/CGE, rocket)
- [x] The `--resolve-changed` checkpoint anchor confirmed (0 models at Day 0 — clean baseline)
- [x] Unknowns 7.2 verified and updated in KNOWN_UNKNOWNS.md
- [x] CHANGELOG updated

---

## Task 3: mine Head-Offset IR-Plumbing Design + Round-Trip Reproduction (Priority 1 foundation)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 5–7 hours (actual: ~4h)
**Completed:** 2026-07-08
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

### Objective

Turn the Sprint-30 Day-6 REPLAN of #1443 into a concrete **IR-plumbing design**: specify where the head-offset detail (position `l`, amount `+1`) and the parameter offsets `li(k)`/`lj(k)` are stored on `EquationDef`, how they survive normalization (which today collapses `pr.domain = (k,l,i,j)` and loses the `l+1` head), and how the KKT layer reads them — then establish the minimal round-trip unit reproduction that gates the Phase-2 shared 3-site helper. This is the deepest carryforward; sizing it before the schedule is set is the critical-path prerequisite.

### Why This Matters

Sprint 30 Day 6 REPLAN'd #1443 for a *foundational* reason, not a tactical one: `pr.has_head_domain_offset` is a bare `bool`, so the head-offset amount and position are **not recoverable** at the KKT/emit layer — the shared index-map helper the `HEAD_OFFSET_ARCHITECTURE_DESIGN.md` calls for *cannot be built* until the detail is plumbed through parse → normalize → KKT. This is a parse-and-normalize change with a blast radius across the emit core, so it MUST be designed (and its round-trip verified in isolation) before Sprint 31 spends implementation days on it. The Sprint-30 retro (§3 lesson 5) explicitly names this as a front-loadable tractability probe: "the mine IR-plumbing blocker … [was] discoverable Day-0 with a deeper structural read, which would have re-allocated the Days 6–8 budget." Getting the IR-plumbing design + round-trip reproduction done in prep is exactly that front-loading. If the round-trip proves harder than a field-addition (e.g. normalization actively rewrites the head), the whole P1 timeline — and the Solve ≥109 target — shifts, and Task 7 must know that before the schedule.

### Background

- `docs/issues/ISSUE_1443_*.md` — the head-offset 3-site trace + the "not stored in IR" blocker (Sprint 30 Day 6) + the cold-INFES-by-direction characterization (~4.07e10 across all four k-directions).
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` — the 3-site architecture (comp_pr emission / `--nlp-presolve` dual transfer / `stat_x` cross-term) the helper drives.
- The IR + pipeline sites: `src/ir/ast.py` (`EquationDef`, `IndexOffset`, `has_head_domain_offset`), `src/ir/normalize.py` (where the head is collapsed), `src/kkt/stationarity.py` (the landed `stat_x` cross-term), `src/emit/emit_gams.py` `_emit_nlp_presolve` (the dual transfer).
- The mine head-offset shape: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j)` — the `l+1` head offset *plus* the `li(k)`/`lj(k)` parameter offsets in the body.
- The AD cross-term property catalog: `tests/integration/emit/test_ad_crossterm_shapes.py` (`shape4_parameter_valued_offset` is the closest existing guard; the new head-offset fixture is the P7 deliverable this design specifies).

### What Needs to Be Done

1. **Specify the IR storage.** Design the `EquationDef` fields (or an `IndexOffset`-carrying structure) that store the head-offset position (`l`) + amount (`+1`) + the body param offsets `li(k)`/`lj(k)`, replacing the bare `has_head_domain_offset` bool. Enumerate every producer (parser) and consumer (normalize, KKT, emit) touchpoint.
2. **Design the normalize round-trip.** Determine why normalization collapses `pr.domain` to `(k,l,i,j)` and specify the minimal change that preserves the head-offset detail through `normalize_model` without altering the domain semantics other equations rely on (blast-radius guard).
3. **Author the round-trip unit reproduction.** A minimal synthetic fixture (mine-shaped, committed under `tests/fixtures/`) whose parse→normalize output can be asserted to carry the head-offset δ + `li(k)`/`lj(k)` — the Phase-1 gate before any emit change.
4. **Specify the Phase-2 shared 3-site helper signature.** Parameterized by (head-offset δ on `l`, param offsets `li(k)`/`lj(k)`), consumed by `comp_pr` emission, the `--nlp-presolve` dual transfer, and the landed `stat_x` cross-term — with the atomic-application requirement (all three or none).
5. **Define the cold-INFES-by-direction success histogram.** The `kkt_residual.py` residual → 0 warm, then cold MS 1, per k-direction — the Phase-2 completion gate.

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md` (the `EquationDef.head_domain_offsets` storage design, the parse-time-collapse trace, the normalize round-trip + reconstructor copy-through touchpoints, the round-trip fixture spec, the Phase-2 shared 3-site helper signature, the cold-INFES-by-direction histogram + the 4th-site REPLAN exit). Updated `KNOWN_UNKNOWNS.md` Unknowns 1.1–1.4 → ✅ VERIFIED. CHANGELOG entry.

### Result

**COMPLETE (2026-07-08).** Empirical parse of `mine.gms` (read-only) established the decisive finding: **the head offset is discarded at PARSE, not at normalization** — `pr.domain=('k','l','i','j')` + `has_head_domain_offset=True` (a bare bool), the `l+1` gone before normalize runs (culprit `_domain_list_has_offset`, `parser.py:932`); the param offsets `li(k)`/`lj(k)` are already preserved in the body. So the round-trip is a **field addition** on `EquationDef` (`head_domain_offsets`, a per-position `IndexOffset` tuple mirroring the `declaration_domain` #1327 precedent) + copy-through at the ~3 reconstructor sites (`sqr_reformulation.py:88/:108`, `complementarity.py:242`) — **NOT a deep normalize rewrite** (`NormalizedEquation` doesn't carry it; consumers read the original `EquationDef`). This de-risks Phase 1 (**Unknown 1.1 ✅ favorable**; zero emit blast radius until a consumer reads it, **1.4 ✅**). The Phase-2 shared helper (parameterized by head δ + body param offsets) drives Sites 1–3 (`comp_pr`/`_emit_nlp_presolve`/`stat_x`) atomically, gated by the cold-INFES-by-direction histogram (baseline ~4.07e10 across nw/ne/se/sw → all four → 0, cold MS 1) with an explicit 4th-site (bound-complementarity) Sprint-32 REPLAN exit (**1.2 ✅**); mine is a convex LP so no Case-c escape (**1.3 ✅**). The round-trip unit fixture (`tests/fixtures/head_offset_ir_roundtrip.gms`) asserting `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)` is the Phase-1 gate. Docs/design-only (read-only parses; no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md && echo "design present"

# It names the IR storage sites and the normalize collapse
grep -qE "has_head_domain_offset" docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md && echo "bool blocker referenced"
grep -qiE "normalize" docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md && echo "normalize round-trip covered"

# The current bool is confirmed in the IR (the thing being replaced)
grep -rn "has_head_domain_offset" src/ir/ | head

# The three emit sites are enumerated
grep -oiE "comp_pr|nlp-presolve|presolve dual|stat_x" docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/HEAD_OFFSET_IR_PLUMBING_DESIGN.md` — the `EquationDef` head-offset storage design, the normalize round-trip design + blast-radius guard, the round-trip unit-reproduction spec, the Phase-2 shared 3-site helper signature, and the cold-INFES-by-direction success histogram
- The minimal round-trip fixture spec (mine-shaped) for `tests/fixtures/`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4
- CHANGELOG entry

### Acceptance Criteria

- [x] HEAD_OFFSET_IR_PLUMBING_DESIGN.md specifies where the head-offset δ + `li(k)`/`lj(k)` are stored on `EquationDef` (`head_domain_offsets`, mirroring `declaration_domain`), replacing the bare bool
- [x] The normalize round-trip design preserves the head-offset detail with a blast-radius guard (field addition + copy-through; `NormalizedEquation` unaffected; zero emit change until a consumer reads it)
- [x] The round-trip unit reproduction (`tests/fixtures/head_offset_ir_roundtrip.gms`, parse asserting the head-offset survives) is specified as the Phase-1 gate
- [x] The Phase-2 shared 3-site helper signature (parameterized by δ, `li(k)`, `lj(k)`) + the atomic-application requirement are specified
- [x] The cold-INFES-by-direction success histogram is the Phase-2 completion gate
- [x] The 4th-site REPLAN exit is named (bound-complementarity → Sprint 32)
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified and updated in KNOWN_UNKNOWNS.md
- [x] CHANGELOG updated

---

## Task 4: Offset-Alias #1111/#1112 Recipe Re-Confirmation + Distance-Jacobian Second-Index Design (Priority 2 foundation)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 4–6 hours (actual: ~3.5h)
**Completed:** 2026-07-08
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4

### Objective

Re-confirm the Sprint-30 Day-7 control-verified 4-term polygon recipe (warm-match 0.780) on the current tree (PR24 — banked recipe is a hypothesis), and design the coupled **distance-Jacobian second-index cross-term** — the general-alias core `_add_indexed_jacobian_terms` drops — that must land together with the already-verified-but-reverted objective-successor half.

### Why This Matters

Sprint 30 Day 8 *implemented and verified* the objective-successor half of the polygon fix (interior-representative selection in `_build_indexed_gradient_term`) but **reverted it** — it can't ship without the coupled distance-Jacobian second-index cross-term, which is the #1111/#1112 general-alias core (a variable appearing at two index-positions of a 2-index constraint; the Jacobian already computes the second-index entries but `_add_indexed_jacobian_terms` drops them). This is the second-deepest carryforward, and its risk is *architectural*: if the second-index cross-term cannot be gated tightly to the var-at-two-indices shape, it demands the full #1111 alias-aware-differentiation / #1112 dollar-condition-propagation core (a Sprint-32 filing). The design must (a) re-confirm the 4-term recipe still reproduces (the Day-7 control experiment on today's tree), (b) locate the exact drop in `_add_indexed_jacobian_terms` and specify the second-index restoration, and (c) confirm the Issue #1110 multi-pattern correction (diagonal-vs-off-diagonal topology) is *orthogonal* to var-at-two-indices, so the gate does not disturb the CGE multi-pattern cohort. himmel16 stays a documented non-convex scope guard (Day-7 sign-fix refuted).

### Background

- `docs/issues/ISSUE_1143_*.md` — the control-verified 4-term recipe (Day 7, warm-match 0.780 ≈ NLP 0.7797) + the Day-8 objective-half implementation-and-revert record.
- `docs/issues/ISSUE_1146_*.md` — himmel16's circular `i++1` offset-alias (`stat_area` residual 2.0 is a numeric/sign defect in the objvar-defining-gradient interaction, documented non-convex — NOT converted by the #1143 representative-selection fix).
- GitHub #1111 (alias-aware differentiation), #1112 (dollar-condition propagation), #1110 (multi-pattern Jacobian diagonal-vs-off-diagonal topology).
- The AD sites: `src/ad/constraint_jacobian.py` (`_add_indexed_jacobian_terms` — the second-index drop), `src/kkt/stationarity.py` (`_build_indexed_gradient_term` — the reverted objective-successor half).
- The property catalog: `tests/integration/emit/test_ad_crossterm_shapes.py` — `shape8_offset_alias_successor` (strict-xfail, the P2 completion gate; the objective half's assertion passes when applied), `shape7_offset_alias_cyclic` (himmel16 cyclic decomposition guard).

### What Needs to Be Done

1. **Re-confirm the 4-term recipe.** Reproduce the Sprint-30 Day-7 control experiment on the current tree: the 4-term polygon fix reaches warm-match 0.780. Record any drift from the banked recipe (PR24 — if it no longer reproduces, re-diagnose before design).
2. **Locate + specify the second-index restoration.** Pin the exact point in `_add_indexed_jacobian_terms` where the second-index cross-term is dropped, and specify the restoration (the general-alias core) — including the tight gate to the var-at-two-indices shape.
3. **Confirm #1110 orthogonality.** Verify the Issue #1110 multi-pattern (diagonal-vs-off-diagonal) correction is independent of var-at-two-indices, so restoring the second-index term does not regress the CGE multi-pattern cohort (`--resolve-changed` GO list).
4. **Specify the coupled-landing design + gate.** The objective-successor half + the distance-Jacobian second-index half land together; `shape8_offset_alias_successor` drops its strict-xfail as the completion gate.
5. **Define the Sprint-32 REPLAN exit.** If the gate cannot be made tight (the fix leaks into non-polygon models), re-scope to the #1111/#1112 AD-engine filing.

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md` (the 4-term recipe re-confirmation, the `_add_indexed_jacobian_terms` second-index drop-point trace + restoration, the #1110 orthogonality table, the coupled-landing design + gate, the himmel16 non-convex scope guard, the Sprint-32 REPLAN exit). Updated `KNOWN_UNKNOWNS.md` Unknowns 2.1–2.4 → ✅ VERIFIED. CHANGELOG entry.

### Result

**COMPLETE (2026-07-08).** The 4-term recipe **reproduces exactly on the current tree** (Unknown 2.1): the KKT-residual harness on `polygon.gms` is byte-identical to the banked Day-0 fingerprint (CASE_B, `stat_theta(i12)` rel 0.492, dual-transfer CONSISTENT), and the current emit drops precisely the distance **second-index** sum + the objective **predecessor** term. **Two PR24 fix-surface corrections:** the second-index drop is in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5767`), **NOT** `constraint_jacobian.py`; the reverted objective half (`_count_additive_terms`) is confirmed absent on `main` and `shape8` is strict-xfail. The restoration (Unknown 2.2) is a new per-position complementary sum (inverted multiplier order + flipped `ord`); **#1110 is orthogonal** — its multi-pattern correction is a *single scalar* (diagonal-vs-off-diagonal) keyed on pattern multiplicity, vs a *whole sum* keyed on constraint-index-position multiplicity. The coupled fix (objective half `_build_indexed_gradient_term:2864` + distance half `_add_indexed_jacobian_terms:5767`) lands together, tightly gated to var-at-two-indices, with `shape8` enable + polygon warm-match 0.780 + CGE byte-stability as the completion gate (Unknown 2.3), and a Sprint-32 #1111/#1112 AD-engine REPLAN exit if the gate leaks. himmel16 is confirmed non-convex (Unknown 2.4 — scope guard, no fix). Docs/design-only (read-only parses/emits/harness; no `src/`).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md && echo "design present"

# The second-index drop site is named
grep -q "_add_indexed_jacobian_terms" docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md && echo "drop site referenced"
grep -rn "_add_indexed_jacobian_terms" src/ad/constraint_jacobian.py | head

# The shape8 completion gate is currently strict-xfail (the thing to enable)
grep -n "shape8_offset_alias_successor\|strict=True" tests/integration/emit/test_ad_crossterm_shapes.py | head

# #1110 orthogonality + himmel16 non-convex scope guard covered
grep -oiE "#1110|himmel16|non-convex" docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/OFFSET_ALIAS_JACOBIAN_DESIGN.md` — the 4-term recipe re-confirmation result, the `_add_indexed_jacobian_terms` second-index restoration design + tight gate, the #1110 orthogonality confirmation, the coupled-landing design with `shape8` as the completion gate, and the Sprint-32 REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4
- CHANGELOG entry

### Acceptance Criteria

- [x] The Day-7 control-verified 4-term recipe is re-confirmed on the current tree (harness CASE_B / stat_theta(i12) 0.492 CONSISTENT — no drift; 2 PR24 fix-surface corrections recorded)
- [x] The `_add_indexed_jacobian_terms` second-index drop is located (`stationarity.py:5767`, not `constraint_jacobian.py`) and the general-alias-core restoration specified, tightly gated to var-at-two-indices
- [x] #1110 multi-pattern orthogonality confirmed (single-scalar diagonal-vs-off-diagonal vs a whole position-keyed sum; no CGE multi-pattern regression)
- [x] The coupled-landing design names `shape8_offset_alias_successor` (drop strict-xfail) as the completion gate
- [x] himmel16 non-convex scope guard recorded (sign-fix refuted; no emit fix expected)
- [x] The Sprint-32 #1111/#1112 AD-engine REPLAN exit is named
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md
- [x] CHANGELOG updated

---

## Task 5: camcge Dual-Consistent Walras Transform Design + Degeneracy-Detector Scope (Priority 3)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 4–5 hours (actual: ~4h)
**Completed:** 2026-07-08
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Design the **dual-consistent multiplier redefinition** the Sprint-30 Day-11 analysis proved is needed for camcge (#1330 → Epic 5) — express the dropped market-clearing row's dual via Walras' law so it stays available in the stationarity — plus the S1∧S2∧S3 degeneracy-detection heuristic scope that must flag *only* camcge across the CGE cohort.

### Why This Matters

Sprint 30 Day 11 delivered the decisive camcge lesson (retro §3 lesson 2): the Epic-5 Walras transform is **paper-verified for the primal but breaks the MCP dual** — dropping one market-clearing row is primal-correct (the price-pin reaches the correct allocation, omega 191.735) but orphans a needed price/wage multiplier in the stationarity, giving omega 299 / MS-4. So the fix is *not* the naive drop-row: it is a dual-consistent redefinition that keeps the dropped market's dual expressible (via Walras' law) in the stationarity. This is the Epic-5 track, and it carries *two* correctness risks that the design must resolve before implementation: (1) the redefinition itself must reach MS 1 at 191.735 (the unproven step — the price-pin proves the target, not the emit); and (2) the degeneracy detector must **not false-flag** a well-posed CGE (silently redefining a dual on a non-degenerate model would corrupt it — the standing "check the dual side" discipline). The design front-loads both so P3 implements a prototype-on-`/tmp`-first plan, not an open question.

### Background

- `docs/issues/ISSUE_1330_*.md` — the price-pin recipe (fix `p('services')=pd0` → omega 191.735, MS-4) + the pinned dual-flaw (dropping a market-clearing row orphans its multiplier).
- `docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` — the Day-11 refinement (premise `p=pd0` holds; drop-row breaks the dual; the dual-consistent redefinition is the open design) + the original `CGE_DEGENERACY_SCOPING.md` §3/§5 open questions.
- The CGE cohort for the false-positive check: irscge / lrgcge / moncge / stdcge (well-posed — the detector must pass them through).
- The KKT residual harness: `scripts/diagnostics/kkt_residual.py` (Case-a/b/c verdict on the dual-consistent prototype).

### What Needs to Be Done

1. **Design the dual-consistent multiplier redefinition.** Specify how the dropped market's dual is re-expressed via Walras' law (∑ excess-demand·price ≡ 0) so it remains available in the stationarity, replacing the naive row-drop. Include the numéraire/price-ray pin.
2. **Specify the S1∧S2∧S3 degeneracy detector.** Define the three conjunctive conditions (the market-clearing redundancy signature) that flag camcge, and the pass-through default for every other model.
3. **Design the false-positive guard.** The per-model check that irscge/lrgcge/moncge/stdcge are NOT flagged — the detector's precision test.
4. **Specify the prototype-on-`/tmp`-first plan.** Reach MS 1 at omega 191.735 with the dual-consistent redefinition in a hand-edited `/tmp` MCP *before* the `src/` change (the Day-11-style control experiment).
5. **Define the per-model-numéraire-declaration fallback.** If the automatic redundant-row + numéraire selection proves non-robust, the documented fallback (a per-model declaration) and its Epic-5 scoping.

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md` (the dual-consistent multiplier redefinition, the S1∧S2∧S3 detector + false-positive guard, the prototype-on-`/tmp`-first plan + the Walras-identity verification, the automatic-rule + per-model-numéraire fallback). Updated `KNOWN_UNKNOWNS.md` Unknowns 3.1–3.4 → ✅ VERIFIED. CHANGELOG entry.

### Result

**COMPLETE (2026-07-08).** The Day-11 refinement is the crux (checking the dual side, the Sprint-30 lesson): the price-pin reaches the correct **omega 191.735** but stays **MS-4** (the dual market-clearing block is still rank-deficient), and the naive drop-row **orphans a needed dual** (omega 299, broken) — a read-only emit confirms `nu_equil(i)` in 7 goods-price stationarity rows and `nu_lmequil(lc)` in 3 wage rows. **The fix (design):** keep every market-clearing row (no orphaned dual) + add a consumption-weighted numéraire (camcge has no `cpi`, so "fix cpi=1" is instantiated on `cles(i)`/`pd0(i)`) + **redefine the redundant market's dual via Walras' law** so the dual block is full-rank → MS-1 (Unknown 3.1). The **S1∧S2∧S3 detector** flags camcge-only with **S3 (cold-MCP-singular-at-iter-0) as the false-positive guard** — a well-posed model with S1∧S2 but a determined closure fails S3 (Unknown 3.2). Selection is automatic for camcge (consumption-weighted numéraire; redundant row = the numéraire good's market), with a per-model-declaration Epic-5 fallback (Unknown 3.3). Walras' law holds at machine precision at the NLP optimum (`gdp_check ≈ −4.83e-10`) ⇒ the redundant dual is a clean linear combination (exact recovery, Unknown 3.4). The `/tmp` prototype to MS-1 at 191.7346 is the pre-`src/` control gate; REPLAN to the per-model-numéraire fallback if it can't reach MS-1. Docs/design-only (read-only emit + banked Day-11 `/tmp`; no `src/`).

### Verification

```bash
# Design doc exists (or the Epic-5 design is extended)
test -f docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md \
  && echo "design present" \
  || (test -f docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "Epic-5 design extended")

# The dual-consistent redefinition + Walras' law are the core
grep -qiE "dual-consistent|walras" docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md && echo "dual-consistent design present"

# The omega 191.735 target + the MS-4 failure of the naive drop are recorded
grep -qE "191\.735" docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md && echo "price-pin target recorded"

# The detector's cohort false-positive check names the CGE cluster
grep -oiE "irscge|lrgcge|moncge|stdcge" docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/CAMCGE_DUAL_CONSISTENT_DESIGN.md` (or an extension of `EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md`) — the dual-consistent multiplier redefinition, the S1∧S2∧S3 detector + false-positive guard, the prototype-on-`/tmp`-first plan, and the per-model-numéraire fallback
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4
- CHANGELOG entry

### Acceptance Criteria

- [x] The dual-consistent multiplier redefinition (Walras' law) is designed, replacing the naive dual-breaking drop-row
- [x] The omega 191.735 target (price-pin) + the naive-drop omega-299 / MS-4 failure are recorded as the control baseline
- [x] The S1∧S2∧S3 degeneracy detector + the irscge/lrgcge/moncge/stdcge false-positive guard (S3 = cold-MCP-singular) are specified
- [x] The prototype-on-`/tmp`-first plan (reach MS-1 at 191.7346 before the src change) is required
- [x] The per-model-numéraire-declaration fallback + Epic-5 scoping are named
- [x] Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md
- [x] CHANGELOG updated

---

## Task 6: Refresh + Author Phase 0 Acceptance Gates for the Sprint-31 Tracks (PR20 + PR24 + PR27)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 4–6 hours (actual: ~3.5h)
**Completed:** 2026-07-09
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 3, 4, 5
**Unknowns Verified:** 1.2, 2.2, 3.1, 4.1, 5.1, 6.2

### Objective

Refresh the existing Phase-0 acceptance gates for the Sprint-31 dispositions and author the new ones, so every emit-touching priority (P1–P6) has a written PROCEED/REPLAN gate before implementation. The gate is the primary scope-correctness control (PR20) plus the PR24 control-experiment-before-implement rule and the PR27 residual-clean-before-forcing rule.

### Why This Matters

Sprint 30 refuted *five* banked diagnoses via the Phase-0 gate before any high-blast-radius `src/` change (retro §3 lesson 1); the gate is the single most load-bearing discipline the sprint carries. Sprint 31's tracks are exactly the ones where a naive implementation would ship a plausible-but-wrong change: the P1 head-offset IR change touches the emit core; the P2 second-index restoration risks the CGE multi-pattern cohort; the P3 dual-consistent redefinition risks corrupting a well-posed CGE; the P4 symbolic emit risks a timeout re-trigger; the P5 obj-grad reduction is where the sign flip was refuted three times. Each needs a written gate that says *what must be true before src changes* and *what triggers REPLAN*. This task consolidates the per-track gate specs from Tasks 3/4/5 (and the P4/P6 gates from Task 9) into one Phase-0 gate document plus the required per-issue Phase-0 sections (PR20 mandates a `## Phase 0: Acceptance Gate` in the ISSUE doc for any src-touching PR).

### Background

- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (the PR20 template + the PR24/PR25 amendments).
- The Sprint-30 gate document as the structural template (per-track PROCEED/REPLAN criteria).
- The per-track design docs from Tasks 3 (head-offset IR round-trip + cold-INFES histogram), 4 (shape8-enable + #1110 orthogonality), 5 (price-pin → dual-consistent prototype-first).
- The KKT-residual Case-(a/b/c) harness (`scripts/diagnostics/kkt_residual.py`) — the PROCEED/REPLAN verdict engine for P1/P3/P5/P6.

### What Needs to Be Done

1. **P1 gate (head-offset IR plumbing).** PROCEED requires the round-trip unit reproduction (Task 3) green *before* the emit change; then the cold-INFES-by-direction histogram → residual 0 warm, cold MS 1. REPLAN exit: a 4th head-offset site.
2. **P2 gate (offset-alias core).** PROCEED requires the 4-term recipe re-confirmed (Task 4) + #1110 orthogonality; completion = `shape8_offset_alias_successor` enabled with no CGE multi-pattern regression. REPLAN exit: the gate can't be made tight → #1111/#1112 AD-engine filing.
3. **P3 gate (camcge dual-consistent).** PR24 control: the dual-consistent redefinition must reach MS 1 at omega 191.735 on `/tmp` *before* the src change; the detector must flag only camcge. REPLAN exit: per-model-numéraire fallback.
4. **P4 gate (sarf symbolic emit).** The emit must be **O(constraints), not O(instances)** — `sarf_mcp.gms` timed against the translate budget; the re-emitted `stat_task` verified against the banked hand-derivation; regenerated golden byte-stable. REPLAN exit: timeout re-trigger.
5. **P5 gate (cold-convex obj-grad).** PR24/PR27 control: the ν_objective reduction must reach the NLP optimum on hhfair *before* the objective-gradient src change (the sign flip is banned — refuted three times). REPLAN exit: genuine Case-c → documented non-convexity.
6. **P6 gate (rocket forcing).** PR27: re-confirm the emit residual is clean at the NLP point (Case-c) *before* any forcing attempt; the deliverable is a match OR the finalized PATH-consultation input.
7. **Author the per-issue Phase-0 sections.** Add/refresh the `## Phase 0: Acceptance Gate` section in each src-touching ISSUE doc (#1443, #1143, #1330, #1385, hhfair/CGE, #1462).

### Changes

Created `docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md` (the consolidated per-track P1–P6 PROCEED/REPLAN gates + the standing PR24/PR27 control-experiment discipline + the summary table). Added a `> **🔄 Sprint-31 refresh (Prep Task 6)**` block to each of the six src-touching ISSUE docs' `## Phase 0: Acceptance Gate` sections (ISSUE_{1443,1143,1330,1385,1236,1462}). Updated `KNOWN_UNKNOWNS.md` — 4.1/5.1/6.2 → ✅ VERIFIED (gate layer) + gate-layer notes on 1.2/2.2/3.1. CHANGELOG entry.

### Result

**COMPLETE (2026-07-09).** Every emit-touching Sprint-31 priority (P1–P6) has a written PROCEED/REPLAN gate consolidated in `PHASE_0_ACCEPTANCE_GATES.md` + refreshed in its per-issue Phase-0 section (all six keep the 4 required `###` subsections per CONTRIBUTING PR20). Each gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27): **P1** the round-trip fixture green before the emit change → cold-INFES histogram (REPLAN on a 4th site); **P2** the 4-term recipe re-confirmed + #1110 orthogonality (`shape8` = completion gate, REPLAN to the #1111/#1112 filing); **P3** the dual-consistent prototype to MS-1 at omega 191.7346 on `/tmp` **before** src + the S1∧S2∧S3 detector (per-model-numéraire fallback); **P4** the O(constraints) emit timed vs the translate budget (REPLAN on timeout); **P5** the ν_objective control experiment before src with **the sign flip BANNED** (refuted 3×; REPLAN to a Case-c finding); **P6** the residual-clean-at-NLP-point (Case-c) rule before forcing (REPLAN to the PATH-consultation input). The control-experiment-before-implement discipline (which refuted five Sprint-30 hypotheses) + the "check the dual side" lesson are the standing rules. Docs-only (gate doc + ISSUE Phase-0 refreshes; no `src/`).

### Verification

```bash
# Phase-0 gate doc exists and covers all six src-touching priorities
test -f docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md && echo "gate doc present"
grep -cE "^## (Priority|P)[1-6]" docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md

# The PR24 control-before-implement rule + the banned sign-flip are stated for P5
grep -qiE "control experiment|before.*src" docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md && echo "PR24 control rule present"
grep -qiE "sign.?flip.*(refuted|banned|not)" docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md && echo "sign-flip ban present"

# The per-issue Phase-0 sections exist
for i in 1443 1143 1330 1385; do
  grep -lq "Phase 0" docs/issues/ISSUE_${i}_*.md 2>/dev/null && echo "ISSUE_$i has Phase 0"
done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/PHASE_0_ACCEPTANCE_GATES.md` — the per-track (P1–P6) PROCEED/REPLAN gate criteria consolidated from Tasks 3/4/5/9
- Refreshed `## Phase 0: Acceptance Gate` sections in the src-touching ISSUE docs (#1443, #1143, #1330, #1385, hhfair/CGE obj-grad, #1462)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2
- CHANGELOG entry

### Acceptance Criteria

- [x] PHASE_0_ACCEPTANCE_GATES.md has a written PROCEED/REPLAN gate for each of P1–P6
- [x] The P1 gate requires the IR round-trip reproduction green before the emit change
- [x] The P3 gate requires the dual-consistent prototype to reach MS-1 at 191.7346 on `/tmp` before the src change (PR24)
- [x] The P5 gate bans the sign flip and requires the ν_objective control experiment before the src change (PR24/PR27)
- [x] The P4 gate requires O(constraints) emit timed against the translate budget
- [x] Each src-touching ISSUE doc has a refreshed `## Phase 0: Acceptance Gate` section (all 6 keep the 4 required subsections)
- [x] Unknowns 1.2, 2.2, 3.1, 4.1, 5.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md
- [x] CHANGELOG updated

---

## Task 7: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 3, 4, 5, 6
**Unknowns Verified:** 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2

### Objective

Apply the PR16 hypothesis-validation discipline to the four deepest REPLAN-prone Sprint-31 tracks — P1 (foundational IR plumbing / 4th-site risk), P2 (#1111/#1112 general-alias core), P4 (symbolic-emit timeout re-trigger), and P5 (genuine Case-c obj-grad) — pinning each track's single-model / control-experiment validation, its explicit Sprint-32 REPLAN exit, and the budget reallocation if it stalls.

### Why This Matters

The Sprint-30 Task-6 risk assessment *predicted the outcome* (retro §3 lesson 3): mine (High), rocket (High), camcge (Medium) all REPLAN'd, and polygon surfaced a *new* REPLAN boundary (the #1111/#1112 core). The honest projection ("Solve ≥109 is the most REPLAN-sensitive KPI; treat the genuine-floor ramp as conditional on the #1111/#1112 core + the dual-consistent CGE work, not as independent +1s") is the exact framing Sprint 31 must carry forward. This task turns each deep track's "how do we know it's on-track by the Day-5 checkpoint?" into a single measurable validation, and pre-commits the budget reallocation so a stalled track (e.g. P1's IR plumbing hitting a 4th site) hands its remaining days to a firm track rather than burning them. It also sets the honest KPI projection: which of Solve ≥109 / genuine floor ≥73 is achievable if the deepest track REPLANs.

### Background

- `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` §1 + §3 (the accurate REPLAN prediction + the "genuine floor is conditional" lesson).
- The Sprint-30 REPLAN-risk-assessment doc as the structural template (Track-A/B/C dispositions).
- The per-track design docs (Tasks 3/4/5) + the Phase-0 gates (Task 6) — this task consumes their REPLAN exits.
- The PROJECT_PLAN Sprint 31 §"Risk Level: HIGH" + the per-priority REPLAN exits it names (P1 4th site, P4 timeout, P5 Case-c).

### What Needs to Be Done

1. **P1 (head-offset IR plumbing).** Validation = the round-trip reproduction green by Day-1 + no 4th emit site by the Day-5 checkpoint. REPLAN exit: a 4th site → the deeper-architecture Sprint-32 filing; reallocate P1's remaining days to P5/P7 (the firmest floor gains).
2. **P2 (#1111/#1112 general-alias core).** Validation = the second-index cross-term gates tightly (no CGE multi-pattern regression) by the Day-5 checkpoint. REPLAN exit: the gate leaks → the #1111/#1112 AD-engine filing; polygon's genuine-floor +1 becomes conditional.
3. **P4 (sarf symbolic emit).** Validation = the O(constraints) emit stays inside the translate budget on `sarf_mcp.gms`. REPLAN exit: timeout re-trigger → re-scope the parametric emit.
4. **P5 (cold-convex obj-grad).** Validation = the ν_objective control experiment reaches the NLP optimum on hhfair. REPLAN exit: genuine Case-c → documented non-convexity for the family.
5. **Set the honest KPI projection.** State which of Solve ≥109 (needs mine [P1] + camcge [P3]) and genuine floor ≥73 (needs polygon [P2] + hhfair/CGE [P5]) survives each single-track REPLAN, and the budget-reallocation order.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Risk assessment doc exists
test -f docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md && echo "risk assessment present"

# Each deep track has a validation + a REPLAN exit
grep -cE "REPLAN exit|REPLAN Exit" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md

# The four deepest tracks are all covered
grep -oiE "P1|P2|P4|P5|head-offset|general-alias|symbolic|obj-grad" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md | sort -u

# The honest KPI projection ties Solve/genuine-floor to specific tracks
grep -qiE "Solve.*109|genuine floor.*73" docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md && echo "KPI projection present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/REPLAN_RISK_ASSESSMENT.md` — per-track (P1/P2/P4/P5) single-model validation + Sprint-32 REPLAN exit + budget reallocation, plus the honest Solve ≥109 / genuine floor ≥73 KPI projection under each single-track REPLAN
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2
- CHANGELOG entry

### Acceptance Criteria

- [ ] Each of P1/P2/P4/P5 has a single-model or control-experiment validation measurable by the Day-5 checkpoint
- [ ] Each has an explicit Sprint-32 REPLAN exit + a budget-reallocation target
- [ ] The honest KPI projection ties Solve ≥109 to (mine + camcge) and genuine floor ≥73 to (polygon + hhfair/CGE), stating what survives each single-track REPLAN
- [ ] Unknowns 1.1, 1.2, 2.2, 2.3, 4.2, 5.1, 5.2 verified and updated in KNOWN_UNKNOWNS.md
- [ ] CHANGELOG updated

---

## Task 8: Reusable-Tooling Readiness Audit for the Sprint-31 Model Classes

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 4.2, 6.1, 7.1, 7.3

### Objective

Confirm the Sprint-28–30 diagnostic and regression tooling covers the new Sprint-31 model classes — the head-offset IR-round-trip test, the `--force` scaffold's forcing-lever entry point, the head-offset + `shape8` property fixtures, and the dual-consistent-Walras / symbolic-emit regression paths — and identify any minimal extension needed before implementation.

### Why This Matters

The Sprint-31 estimate depends on reusing (not rebuilding) the KKT-residual harness, the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint re-solve, and the `--force` solution-forcing scaffold. If any tool has a gap for a Sprint-31 class — e.g. the KKT-residual harness doesn't handle the head-offset cross-term shape, or the `--force` scaffold's entry point can't take the rocket continuation lever, or the golden-staleness gate doesn't cover the newly-touched emit sites — that gap surfaces mid-sprint as unplanned tooling work. Auditing readiness in prep keeps the diagnosis cost low (retro §5) and feeds the Task-9 fix-surface analysis + the P7 property-fixture deliverables.

### Background

- `scripts/diagnostics/kkt_residual.py` (Case-a/b/c harness — P1/P3/P5/P6).
- `scripts/diagnostics/check_presolve_divergence.py` (embedded-NLP-divergence detector — the presolve dual-transfer touchpoints in P1/P3).
- `scripts/sprint_audit/check_golden_staleness.py` + `changed_emit_artifacts.py` + the `--resolve-changed` mode (P1–P6 all touch emit).
- `src/emit/forcing.py` + `src/config.py` + `src/cli.py` (the `--force {homotopy,multistart,optfile}` scaffold that landed Sprint 30 — the P6 entry point).
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (the property catalog — `shape8` strict-xfail, `shape9` robert; the head-offset fixture is new).

### What Needs to Be Done

1. **KKT-residual harness coverage** — confirm it produces a Case-(a/b/c) verdict for the head-offset cross-term shape (P1), the dual-consistent Walras prototype (P3), and the obj-grad reduction (P5); note any shape it can't score.
2. **`--force` scaffold entry point** — confirm the scaffold can take the rocket continuation/reformulation levers (P6) and that its harness output feeds the PATH-consultation input.
3. **Property-fixture readiness** — confirm `shape8_offset_alias_successor` is the P2 completion gate and scope the new head-offset fixture (from Task 3's round-trip spec) for P7.
4. **Golden-staleness + `--resolve-changed` coverage** — confirm the gate + the checkpoint re-solve cover the newly-touched emit sites (the head-offset core, `_add_indexed_jacobian_terms`, the Walras redefinition, the sarf symbolic emit).
5. **Identify minimal extensions** — list any tool gap that must close before the relevant priority starts (feeds Task 9 + P7).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Readiness audit doc exists
test -f docs/planning/EPIC_4/SPRINT_31/TOOLING_READINESS_AUDIT.md && echo "audit present"

# The reused tools are all present in the tree
test -f scripts/diagnostics/kkt_residual.py && echo "kkt harness present"
test -f src/emit/forcing.py && echo "--force scaffold present"
test -f scripts/sprint_audit/check_golden_staleness.py && echo "staleness gate present"

# The property catalog + shape8/shape9 are present
grep -n "shape8_offset_alias_successor\|shape9_objgrad_subset_boundary" tests/integration/emit/test_ad_crossterm_shapes.py
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/TOOLING_READINESS_AUDIT.md` — per-tool coverage confirmation for the Sprint-31 classes + a minimal-extension list (feeds Task 9 + P7)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.2, 6.1, 7.1, 7.3
- CHANGELOG entry

### Acceptance Criteria

- [ ] The KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` re-solve, and `--force` scaffold are each confirmed for their Sprint-31 touchpoints
- [ ] The `shape8` P2 completion gate + the new head-offset P7 fixture are scoped
- [ ] Any minimal tooling extension is listed with the priority it blocks
- [ ] Unknowns 4.2, 6.1, 7.1, 7.3 verified and updated in KNOWN_UNKNOWNS.md
- [ ] CHANGELOG updated

---

## Task 9: Backlog Fix-Surface Analysis (#1385 sarf; hhfair/CGE obj-grad; rocket forcing/PATH input)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 8
**Unknowns Verified:** 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3

### Objective

Turn the three implementation-lighter carryforwards into concrete fix-surface hypotheses with property-test fixtures: the #1385 sarf symbolic-emit patch site (P4), the cold-convex obj-grad reduction site (P5), and the rocket forcing-lever exhaustion + PATH-consultation-input draft (P6) — each a Day-0-re-confirm hypothesis (PR24), not a fact.

### Why This Matters

P4/P5/P6 are the carryforwards whose *fix surface* is banked but whose *exact patch site* still needs a re-confirm on the current tree before implementation (the hhfair sign-flip refutation is the cautionary tale — the banked surface was wrong three times). This task pins each patch site (the `_is_blowup_dynamic_subset_equation` 2-D extension + the parametric `stat_task` builder for P4; the ν_objective reduction in the objective-gradient path for P5; the emittable-lever set + the PATH-question scope for P6), and specifies the property-test fixture that will guard each — so implementation starts from a re-confirmed hypothesis and a written test, not an open search. It follows Task 8 because the property-fixture readiness feeds the fixture specs here.

### Background

- `docs/issues/ISSUE_1385_*.md` — the banked 6-guarded-term `stat_task` derivation; the Sprint-26 `nu_slack("srn")` set-name-literal failure; sarf's 2-D `tbal(g,t)$taskposs` shape + 1,152 Cartesian instances.
- The sarf emit sites: `src/ad/index_mapping.py` (`_is_blowup_dynamic_subset_equation`, currently srpchase 1-D), `src/kkt/stationarity.py` (the parametric cross-term emit).
- The obj-grad reduction: hhfair `stat_u` rel 2.0 (the cleanest instance); irscge/lrgcge/moncge `stat_xp` rel ~0.06 (after the Day-5 case-normalization fix); the objective-defining-equation multiplier ν_objective in `src/kkt/stationarity.py` / `src/ad/gradient.py`.
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 — the PATH-consultation-input draft scope; rocket's `1/ht²`,`1/m²` division-by-variable Jacobian + INFES 477→382.
- The property catalog: `tests/integration/emit/test_ad_crossterm_shapes.py` — the fixture home for the sarf-shape + obj-grad-reduction guards.

### What Needs to Be Done

1. **P4 sarf fix-surface.** Re-confirm the 2-D `_is_blowup_dynamic_subset_equation` extension surface + the parametric `stat_task` builder site on the current tree; spec the O(constraints) property fixture (a sarf-shaped synthetic guarding the 6-guarded-term derivation with no set-name multiplier indices).
2. **P5 obj-grad fix-surface.** Re-confirm the ν_objective reduction site in the objective-gradient path (NOT the sign flip); spec the control experiment (hhfair → NLP optimum) + a property fixture for the objective-defining-intermediate-variable shape.
3. **P6 rocket lever set + PATH input.** Enumerate the remaining emittable levers (the `1/ht²`/`1/m²` Jacobian reformulation + scaled/relaxed continuation) and draft the concrete PATH-consultation question scope (feeds Sprint 32).
4. **Assemble the fix-surface + fixture summary** — each patch site as a re-confirmable hypothesis + its guarding fixture.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Fix-surface doc exists
test -f docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "fix-surface present"

# The sarf 1-D→2-D extension site is named + confirmed in the tree
grep -q "_is_blowup_dynamic_subset_equation" docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "sarf surface named"
grep -rn "_is_blowup_dynamic_subset_equation" src/ad/index_mapping.py | head

# The obj-grad reduction is the ν_objective path, not the banned sign flip
grep -qiE "objective.*multiplier|nu_objective|defining.equation" docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "obj-grad reduction surface named"

# The rocket PATH-consultation input scope is drafted
grep -qiE "PATH.consultation|PATH question" docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "PATH input drafted"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` — the P4 sarf symbolic-emit patch site + fixture spec, the P5 ν_objective obj-grad reduction site + control-experiment + fixture spec, and the P6 emittable-lever set + PATH-consultation-input draft
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3
- CHANGELOG entry

### Acceptance Criteria

- [ ] The P4 sarf 2-D `_is_blowup_dynamic_subset_equation` extension + parametric `stat_task` builder site are re-confirmed on the current tree with an O(constraints) property fixture spec
- [ ] The P5 obj-grad fix-surface is the ν_objective reduction (the sign flip is explicitly excluded) with a control-experiment + fixture spec
- [ ] The P6 emittable-lever set + the drafted PATH-consultation question scope are recorded
- [ ] Each patch site is framed as a Day-0-re-confirm hypothesis (PR24)
- [ ] Unknowns 4.1, 4.3, 5.1, 5.2, 5.3, 5.4, 6.1, 6.3 verified and updated in KNOWN_UNKNOWNS.md
- [ ] CHANGELOG updated

---

## Task 10: Plan Sprint 31 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 31 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–9
**Unknowns Verified:** all 25 (integrates every verified unknown into the schedule)

### Objective

Produce the detailed 14-day Sprint 31 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, sequencing the seven priorities so the deepest track (P1 head-offset IR plumbing) and its foundational IR change lead, the checkpoints (Day 5 / Day 10) land the `--resolve-changed` re-solve, and no day exceeds 12 hours per the PROJECT_PLAN Sprint 31 entry.

### Why This Matters

This is the final prep task — it consumes every prior task's output (the KU list, the baseline, the three design docs, the Phase-0 gates, the REPLAN assessment, the tooling audit, the fix-surface analysis) and turns them into an executable schedule. The sequencing is load-bearing: P1's IR plumbing is a foundational change that must land its Phase-1 round-trip *before* the Phase-2 helper, so it needs early, contiguous days; the Sprint-30 retro (§3 lesson 5) says front-load the tractability probes, so Day 0 must run the P1 round-trip + the P3 dual-consistent `/tmp` prototype + the P5 hhfair control experiment before committing the mid-sprint budget. The schedule must also bake in the REPLAN reallocation order from Task 7, so a stalled deep track hands its days to a firm one at the Day-5 checkpoint.

### Background

- The PROJECT_PLAN Sprint 31 entry: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31 (Weeks 27–28)" (Priorities 1–7 + the Estimated Effort per-priority budgets: P1 [18–24h], P2 [14–20h], P3 [12–18h], P4 [14–20h], P5 [10–16h], P6 [8–12h], P7 [6–10h] + retest [4h]; ≤ 12h/day; the ~11h heaviest day is the P1 IR-plumbing Phase 1 + Phase 2).
- The Sprint-30 PLAN.md + prompts/PLAN_PROMPTS.md as the day-by-day structural template.
- All Task 1–9 outputs (KU list, baseline, designs, gates, REPLAN assessment, tooling audit, fix-surface).
- The checkpoint re-solve design (`--resolve-changed`) for the Day-5 / Day-10 checkpoints.

### What Needs to Be Done

1. **Sequence the priorities across Days 1–13** — P1 head-offset (early, contiguous: Phase-1 IR plumbing then Phase-2 helper); P2 offset-alias core; P3 camcge dual-consistent; P4 sarf symbolic emit; P5 cold-convex obj-grad; P6 rocket forcing/PATH input; P7 property fixtures + genuine-floor tracking (after P1/P2 land).
2. **Place Day 0 tractability probes** — the P1 round-trip reproduction, the P3 dual-consistent `/tmp` prototype, and the P5 hhfair ν_objective control experiment, so the deepest tracks are validated before the mid-sprint budget commits.
3. **Place the checkpoints** — Day 5 + Day 10 `--resolve-changed` re-solve + the REPLAN-reallocation decision points from Task 7; the final Day-13 retest under ≥ 3 `PYTHONHASHSEED` values + the PR25 genuine-floor recompute.
4. **Write the day-by-day execution prompts** — one per day, each naming its priority, its Phase-0 gate, its deliverable, and its REPLAN exit.
5. **Verify the budget** — ≤ 12h/day, total within the 92–134h work-item envelope; the ~11h heaviest day is the P1 Phase-1+Phase-2 day.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
# Schedule + prompts exist
test -f docs/planning/EPIC_4/SPRINT_31/PLAN.md && echo "PLAN present"
test -f docs/planning/EPIC_4/SPRINT_31/prompts/PLAN_PROMPTS.md && echo "prompts present"

# 14 days covered (Day 0 + Days 1–13)
grep -cE "^#+ Day [0-9]+" docs/planning/EPIC_4/SPRINT_31/PLAN.md

# Checkpoints + final retest are placed
grep -qiE "Day 5|checkpoint" docs/planning/EPIC_4/SPRINT_31/PLAN.md && echo "Day-5 checkpoint placed"
grep -qiE "Day 10|checkpoint" docs/planning/EPIC_4/SPRINT_31/PLAN.md && echo "Day-10 checkpoint placed"
grep -qiE "PYTHONHASHSEED|determinism" docs/planning/EPIC_4/SPRINT_31/PLAN.md && echo "final determinism retest placed"

# No day exceeds 12 hours (manual review of the per-day estimates)
grep -nE "[0-9]+h|hours" docs/planning/EPIC_4/SPRINT_31/PLAN.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_31/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with per-day priority / Phase-0 gate / deliverable / REPLAN exit, the Day-5 / Day-10 checkpoints + the final determinism retest, and the ≤ 12h/day budget verification
- `docs/planning/EPIC_4/SPRINT_31/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- `docs/planning/EPIC_4/SPRINT_31/SPRINT_LOG.md` (skeleton for the sprint)
- Updated KNOWN_UNKNOWNS.md — all 25 unknowns integrated into the 14-day schedule
- CHANGELOG entry

### Acceptance Criteria

- [ ] PLAN.md covers 14 days (Day 0 + Days 1–13), each ≤ 12 hours, total within the 92–134h envelope
- [ ] Day 0 runs the P1 round-trip + P3 `/tmp` prototype + P5 hhfair control experiment tractability probes
- [ ] P1 head-offset leads with contiguous Phase-1 (IR plumbing) then Phase-2 (helper) days
- [ ] The Day-5 / Day-10 `--resolve-changed` checkpoints + the REPLAN-reallocation decision points + the final Day-13 ≥3-seed determinism retest are placed
- [ ] Per-day execution prompts name the priority, Phase-0 gate, deliverable, and REPLAN exit
- [ ] All 25 unknowns from KNOWN_UNKNOWNS.md integrated into the schedule
- [ ] CHANGELOG updated

---

## Summary

### Prep Task → Deliverable Map

| Task | Primary Deliverable | Feeds |
|------|--------------------|-------|
| 1 | `KNOWN_UNKNOWNS.md` (22–30 unknowns, 7 categories) | Tasks 3–10 |
| 2 | `BASELINE_METRICS.md` (Day-0 buckets + genuine floor 70) | Tasks 3, 7, 10 |
| 3 | `HEAD_OFFSET_IR_PLUMBING_DESIGN.md` (P1 foundation) | Tasks 6, 7, 10 |
| 4 | `OFFSET_ALIAS_JACOBIAN_DESIGN.md` (P2 second-index core) | Tasks 6, 7, 10 |
| 5 | `CAMCGE_DUAL_CONSISTENT_DESIGN.md` (P3 Epic-5) | Tasks 6, 7, 10 |
| 6 | `PHASE_0_ACCEPTANCE_GATES.md` + per-issue Phase-0 sections | Tasks 7, 10 |
| 7 | `REPLAN_RISK_ASSESSMENT.md` (P1/P2/P4/P5 exits + KPI projection) | Task 10 |
| 8 | `TOOLING_READINESS_AUDIT.md` | Tasks 9, 10 |
| 9 | `BACKLOG_FIX_SURFACE_ANALYSIS.md` (P4/P5/P6 patch sites) | Task 10 |
| 10 | `PLAN.md` + `prompts/PLAN_PROMPTS.md` + `SPRINT_LOG.md` skeleton | Sprint 31 execution |

### Verification

```bash
# All prep deliverables present
for f in KNOWN_UNKNOWNS.md BASELINE_METRICS.md HEAD_OFFSET_IR_PLUMBING_DESIGN.md \
         OFFSET_ALIAS_JACOBIAN_DESIGN.md CAMCGE_DUAL_CONSISTENT_DESIGN.md \
         PHASE_0_ACCEPTANCE_GATES.md REPLAN_RISK_ASSESSMENT.md \
         TOOLING_READINESS_AUDIT.md BACKLOG_FIX_SURFACE_ANALYSIS.md PLAN.md; do
  test -f "docs/planning/EPIC_4/SPRINT_31/$f" && echo "OK  $f" || echo "MISSING  $f"
done
test -f docs/planning/EPIC_4/SPRINT_31/prompts/PLAN_PROMPTS.md && echo "OK  prompts/PLAN_PROMPTS.md"
```

### Success Criteria

- [ ] All 10 prep tasks complete (Task 1 Known Unknowns first; Task 10 detailed schedule last)
- [ ] The head-offset IR-plumbing design (Task 3) sizes P1 with a round-trip reproduction gate before any emit change
- [ ] The #1111/#1112 recipe re-confirmation + distance-Jacobian design (Task 4) couples the reverted objective half with the second-index core
- [ ] The camcge dual-consistent design (Task 5) replaces the dual-breaking drop-row and scopes the false-positive-safe detector
- [ ] Every src-touching priority (P1–P6) has a written Phase-0 PROCEED/REPLAN gate (Task 6) enforcing PR24 control-before-implement
- [ ] The four deepest tracks (P1/P2/P4/P5) each have a single-model validation + a Sprint-32 REPLAN exit + budget reallocation (Task 7)
- [ ] The 14-day schedule front-loads the Day-0 tractability probes and keeps every day ≤ 12h (Task 10)

**Estimated prep investment:** 4.5–6 days
**Expected benefit:** correctly scopes the deepest carryforward (P1's foundational head-offset IR plumbing) with a round-trip gate before implementation, couples the P2 offset-alias core so it can ship, turns the paper-broken/dual-verified camcge transform into an implementable dual-consistent design, and — carrying the Sprint-30 lesson that the banked recipe is a hypothesis and the dual side must be checked — keeps every emit-touching track behind a control-experiment gate, so Sprint 31 spends its budget *implementing* the Sprint-30 control-verified carryforwards rather than re-diagnosing or mis-shipping them.

---

## Appendix: Document Cross-References

### Sprint 31 Scope + Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 31 (Weeks 27–28): Sprint 30 Carryforward — Head-Offset IR Plumbing, General-Alias AD (#1111/#1112) & Dual-Consistent CGE" (Priorities 1–7 + pipeline retest + Acceptance Criteria + Estimated Effort + Risk Level)
- `docs/planning/EPIC_4/GOALS.md` (Epic 4: Full GAMSLIB LP/NLP/QCP coverage; Solve Completion + Solution Matching themes)

### Sprint 30 Source Material
- `docs/planning/EPIC_4/SPRINT_30/SPRINT_RETROSPECTIVE.md` (§4 "Sprint-31 carryforwards" — the seven tracks; §2 "What landed (firm)" — robert / hhfair `$184` / Class-B case-normalization / the `--force` scaffold; §1 metrics table; §3 the five refuted-hypothesis + "check the dual side" lessons)
- `docs/planning/EPIC_4/SPRINT_30/SPRINT_LOG.md` (per-day entries; Day 6 mine IR-plumbing REPLAN; Day 7 polygon 4-term control-verification + himmel16 non-convex refutation; Day 8 polygon objective-half implement+revert; Day 9 sarf symbolic-emit REPLAN; Day 11 camcge dual-flaw + price-pin omega 191.735; Day 13 final PR25 tally + genuine floor 70)
- `docs/planning/EPIC_4/SPRINT_30/PREP_PLAN.md` (the structural template for this prep plan — Tasks 1–10)
- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` (open-item migration source for Task 1)
- `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` (bucket-provenance + genuine-vs-methodology template for Task 2)
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (the 3-site architecture the P1 helper drives — Task 3)
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (§4 the PATH-consultation hand-off draft — Task 9 P6)
- `docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` (the Day-11 dual-consistent refinement + price-pin — Task 5)
- The Sprint-30 REPLAN-risk-assessment, tooling-readiness-audit, and backlog-fix-surface docs (structural templates for Tasks 7, 8, 9)

### Carryforward + Backlog Issues (Phase-0 gate targets)
- `docs/issues/ISSUE_1443_*.md` (P1 — mine head-domain-offset; records the "not stored in IR" blocker + the 3-site trace + the cold-INFES-by-direction characterization)
- `docs/issues/ISSUE_1143_*.md` (P2 — offset-alias objective cross-term; the control-verified 4-term recipe + the Day-8 objective-half implement-and-revert)
- `docs/issues/ISSUE_1146_*.md` (P2 scope guard — himmel16 circular offset-alias, documented non-convex, sign-fix refuted)
- `docs/issues/ISSUE_1330_*.md` + `docs/planning/EPIC_5/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` (P3 — camcge dual-consistent Walras; the price-pin recipe omega 191.735 + the pinned dual-flaw)
- `docs/issues/ISSUE_1385_*.md` (P4 — sarf symbolic runtime-guard cross-terms; the banked `stat_task` derivation + the Sprint-26 `nu_slack("srn")` failure)
- `docs/issues/ISSUE_1236_*.md` (P5 context — hhfair; the sign-flip refutation history)
- GitHub #1462 rocket (P6 — non-convex forcing; the `--force` scaffold landed Sprint 30), #1111 / #1112 (P2 — general-alias differentiation / dollar-condition propagation core), #1110 (P2 — multi-pattern Jacobian topology)

### Related Research / Tooling
- `scripts/diagnostics/kkt_residual.py` (KKT-residual Case-(a/b/c) harness — Tasks 3, 5, 6, 8)
- `scripts/diagnostics/check_presolve_divergence.py` (embedded-NLP-divergence detector — the presolve dual-transfer in P1/P3 — Task 8)
- `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/changed_emit_artifacts.py` + the `--resolve-changed` mode (golden-staleness gate + changed-artifact diff + checkpoint re-solve — Tasks 2, 8, 10)
- `src/ir/ast.py` (`EquationDef`, `IndexOffset`, `has_head_domain_offset`) + `src/ir/normalize.py` (the head-offset collapse — Task 3)
- `src/kkt/stationarity.py` (the landed `stat_x` cross-term + the parametric `stat_task` builder site) + `src/ad/constraint_jacobian.py` (`_add_indexed_jacobian_terms` second-index drop) + `src/ad/index_mapping.py` (`_is_blowup_dynamic_subset_equation` — Tasks 3, 4, 9)
- `src/emit/forcing.py` + `src/config.py` + `src/cli.py` (the `--force` solution-forcing scaffold — Tasks 8, 9 P6)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (AD cross-term property catalog — `shape8` P2 gate, `shape9` robert, the new head-offset fixture — Tasks 8, 9)
- `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` (Case-c non-convexity context for P5/P6 — Task 9)

### Process / Tooling
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (PR20 template + PR24/PR25 amendments — Task 6)
- `data/gamslib/gamslib_status.json` (Sprint 30 final retest DB — Solve 107 / Match 92 / model_infeasible 7; Task 2 baseline source)
- `data/gamslib/mcp/*_mcp.gms`, `*_mcp_presolve.gms` (golden artifacts for the Task-8 / Task-10 checkpoint checks)
