# Sprint 30 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 30 begins
**Timeline:** Complete before Sprint 30 Day 1
**Goal:** Set up Sprint 30 for success — land the Sprint 29 Solve/Match carryforwards the Day-13 retest REPLAN'd: the **head-domain-offset emit architecture** (the coordinated `comp_pr`/`lam_pr`/`stat_x` + bound index-map re-derivation that converts **mine** [+1 Solve] *and* **robert** [genuine-floor], with robert as the minimal pure-constant-offset reproduction and mine the full `l+1 × li(k)/lj(k)` multi-site case), the **rocket #1462 non-convex forcing** (trust-region / homotopy / multi-start — the `_fx_` warm-start already landed Sprint 29), the **hhfair #1236 widened-VARIABLE presolve fix** (the `$184` #1449 conflict for a live nonlinear-stationarity variable), the **#1385 symbolic runtime-guard cross-term emit** (sarf; cross-terms already hand-derived + banked Sprint 29), the **offset-alias cross-terms #1111/#1112** (polygon + himmel16), the **camcge #1330 → Epic 5** Walras drop-row + fix-numéraire transformation, and the adjacent **Class-B CGE `stat_pz`** general-emit backlog (confirmed NOT Walras). Targets: Solve 107 → ≥ 109; Match maintain ≥ 92 / genuine floor 69 → ≥ 72; model_infeasible 7 → ≤ 5; Translate maintain ≥ 135 (stretch +1 via #1385); Tests 4,971 → ≥ 4,990.

**Key Insight from Sprint 29:** Sprint 30 is **implementation-bound, not diagnosis-bound** — the inverse of Sprint 29. Every core carryforward was already *diagnosed* in Sprint 29 and then REPLAN'd precisely because the diagnosis proved the fix was multi-site, architectural, or intrinsic: #1443 mine was traced to a coordinated **3-site head-offset index-map re-derivation** (Day 6–7), and Sprint 29 Day 12 found **robert** is a second, *simpler* instance of the same class (pure constant offset, no parameter offset) — so robert is the **minimal reproduction that de-risks the whole track**; #1462 rocket's residual was confirmed **intrinsic non-convergence** (the `_fx_` warm-start landed, MS-5 persists — Day 2), so it needs a **solution-forcing** strategy, not an emit fix; #1236 hhfair's blocker was traced to the **`$184` widened-VARIABLE** #1449 conflict (Day 8), not the Day-0-attributed `$141`; #1385's cross-terms were **hand-derived + banked** (Day 9), ready to materialize; the offset-alias fix was **reverted** (Day 5) as coupled with the distance-Jacobian; and camcge's Walras transformation is **paper-verified** in `EPIC_5/CGE_DEGENERACY_SCOPING.md`. Sprint 30 prep MUST therefore (a) turn each banked diagnosis into a **design** the implementation follows (the head-offset index-map, the forcing lever set, the widened-VARIABLE emit path, the Walras detection+numéraire selection), (b) **refresh the existing Phase-0 gates** with the Sprint-30 dispositions (mine+robert, rocket-forcing, hhfair-`$184`) rather than author from scratch, and (c) keep the PR16/PR24/PR25 discipline: the banked fix surfaces are still **Day-0-trace hypotheses** (Sprint 29 proved the Day-0 `$141` attribution wrong for hhfair), the deep tracks (P1 multi-site, P2 forcing, P6 Epic-5) still get explicit REPLAN exits, and the re-baseline stays honest (genuine floor 69, not the methodology-inflated 92).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 30 inherits the six Sprint-29 REPLAN'd carryforwards (Priorities 1–6 in `PROJECT_PLAN.md` §"Sprint 30"): the head-domain-offset emit architecture (#1443 mine + robert); rocket #1462 non-convex forcing; hhfair #1236 widened-VARIABLE presolve fix; #1385 symbolic runtime-guard cross-term emit (sarf); offset-alias cross-terms #1111/#1112 (polygon + himmel16); and camcge #1330 → Epic 5 Walras drop-row + fix-numéraire transformation. Two additional priorities (7–8) pull the adjacent general-emit backlog (the Class-B CGE `stat_pz` coefficient discrepancy — confirmed **NOT** Walras — plus the cold-convex Case-c residue) and the Sprint-29-retrospective infrastructure (property-test catalog extension for the new head-offset/offset-alias cross-term shapes, the Rolling-KPIs Match re-baseline for S31–S33, and a solution-forcing harness scaffold that feeds the renumbered Sprint 31 PATH-consultation work).

Sprint 30 differs from Sprint 29 in one structural way: **Sprint 29 diagnosed these tracks; Sprint 30 implements them.** Because the diagnosis is already banked (the Sprint 29 SPRINT_LOG per-day entries, the REPLAN_RISK_ASSESSMENT, the COLD_CONVEX_COHORT_SURVEY, the BACKLOG_FIX_SURFACE_ANALYSIS, and the EPIC_5 scoping doc), Sprint 30 prep is lighter on *survey* and heavier on *design-before-implement*: the hardest track (P1 head-offset architecture) needs a concrete index-map design with **robert as the minimal reproduction**; the second-hardest (P2 rocket forcing) needs a **forcing-strategy survey** so the implementation picks a lever rather than improvising; and P6 (camcge Epic-5) needs the detection-heuristic + per-model numéraire-selection design that the paper-verified transformation left open. The Sprint-29 diagnostic tooling (KKT-residual harness, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — Sprint 30 Known Unknowns List covering the six carryforward tracks (each a banked Sprint-29 diagnosis that is still a Day-0-trace hypothesis, PR24), the three diagnosis-heavy REPLAN-prone tracks (#1443 multi-site head-offset, #1462 non-convex forcing, #1111/#1112 AD-engine redesign), the robert-generalizes-to-mine assumption, and the camcge Walras detection-heuristic scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 29 final → Sprint 30 Day 0 per-model bucket provenance, confirming Day-0 = Sprint 29 final (Solve 107, Match 92, genuine floor 69, model_infeasible 7, Translate 135, Tests 4,971) and that the Sprint-29-built re-baseline tooling is the standing discipline.
3. **Head-domain-offset emit-architecture design + robert minimal reproduction (Priority 1 foundation)** — turn the Sprint-29 Day-6/7 3-site trace into a concrete index-map design; establish robert (pure-constant-offset) as the minimal reproduction so a correct robert fix generalizes to mine, sizing P1 BEFORE the schedule is set.
4. **Non-convex forcing strategy survey (Priority 2 foundation)** — survey trust-region / homotopy / multi-start forcing levers for rocket #1462 and the cold-convex Case-c residue, so P2 implements a chosen lever and P8's forcing scaffold has a tested entry point.
5. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — refresh the existing gates for the Sprint-30 dispositions (mine+robert head-offset, rocket forcing, hhfair `$184`) and add the new robert and Class-B `stat_pz` gates.
6. **Diagnosis-heavy track REPLAN assessment (PR16)** — apply hypothesis-validation to P1 (multi-site head-offset), P2 (non-convex forcing beyond the warm-start), and P6 (Epic-5 transformation); pin explicit Sprint 31 REPLAN exits + budget reallocation.
7. **camcge → Epic 5 Walras transformation design (Priority 6)** — design the degeneracy-detection heuristic + per-model numéraire selection + the non-degenerate-model guard that the paper-verified transformation left as open questions.
8. **Reusable-tooling readiness audit** — confirm the Sprint-29 tools cover the new Sprint-30 classes (head-offset property-test shape, the forcing-harness scaffold, the widened-VARIABLE emit path) and identify any minimal extension.
9. **Backlog fix-surface analysis (Priorities 4 + 5 + 7)** — the #1385 sarf banked cross-terms, the offset-alias #1111/#1112 patch site, and the Class-B CGE `stat_pz` coefficient discrepancy patch-site hypotheses + property-test fixtures.
10. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 30 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 30 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 29 → Sprint 30 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine floor |
| 3 | Head-Domain-Offset Emit-Architecture Design + robert Minimal Reproduction (Priority 1 foundation) | Critical | 5–7h | Tasks 1, 2 | Priority 1 — mine (Solve) + robert (genuine-floor) |
| 4 | Non-Convex Forcing Strategy Survey (rocket #1462 + cold-convex Case-c residue) (Priority 2 foundation) | High | 4–6h | Task 1 | Priorities 2, 7, 8 — forcing levers; feeds P8 scaffold |
| 5 | Refresh + Author Phase 0 Acceptance Gates for the Sprint-30 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 1, 3 | Priorities 1–7 — primary scope-correctness gate |
| 6 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443 multi-site, #1462 forcing, #1330 Epic-5; PR16) | High | 3–5h | Tasks 3, 4, 5 | Priorities 1, 2, 6 — REPLAN-prone tracks |
| 7 | camcge → Epic 5 Walras Transformation Design (Priority 6) | Medium | 3–4h | Task 1 | Priority 6 — Epic 5 implementation design |
| 8 | Reusable-Tooling Readiness Audit for the Sprint-30 Model Classes | Medium | 3–4h | Task 1 | All priorities — tooling reuse; feeds P8/P9 |
| 9 | Backlog Fix-Surface Analysis (#1385 sarf; #1146/#1143/#1112/#1111; Class-B CGE `stat_pz`) | Medium | 3–4h | Tasks 1, 8 | Priorities 4, 5, 7 — fix-surface hypotheses |
| 10 | Plan Sprint 30 Detailed Schedule | Critical | 3–4h | Tasks 1–9 | All priorities — sprint planning |

**Total Estimated Time:** 34–48 hours (~4.5–6 working days)

**Critical Path:** Task 1 → Task 3 → Task 5 → Task 6 → Task 10 (the deep-track chain — the head-offset architecture design (Task 3) sizes Priority 1 and feeds the Phase-0 gate refresh (Task 5), which feeds the REPLAN assessment (Task 6) and the schedule).
**Secondary Path:** Task 1 → Task 4 → Task 6 → Task 10 (the forcing survey feeds the rocket REPLAN assessment + the P8 scaffold → schedule).
**Tertiary Path:** Task 1 → Task 8 → Task 9 → Task 10 (tooling readiness → backlog fix-surface analysis → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 4 + 7 + 8 (independent after Task 1); Task 9 follows Task 8; Task 3 gates the critical path.

---

## Task 1: Create Sprint 30 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~3.5h)
**Completed:** 2026-07-04
**Deadline:** Before Sprint 30 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive list of assumptions and unknowns for Sprint 30 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform every other prep task — particularly the head-offset architecture design (Task 3), the forcing survey (Task 4), the Phase-0 gate refresh (Task 5), the REPLAN assessment (Task 6), and the tooling audit (Task 8). It also carries forward the end-of-sprint unknowns from Sprint 29 (the §"KU Coverage Summary" / carryforwards in `docs/planning/EPIC_4/SPRINT_29/SPRINT_RETROSPECTIVE.md` plus any open items in `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 30's central risk is inverted from Sprint 29's: it is **implementation-bound on tracks that were REPLAN'd *because* they proved hard** — the head-offset architecture is a multi-site re-derivation, rocket needs intrinsic-non-convergence forcing, and camcge needs a domain-specific transformation. Each carried a banked Sprint-29 diagnosis, but PR24 still holds: **the banked fix surface is a Day-0-trace hypothesis, not fact** (Sprint 29 proved the Day-0 `$141` attribution wrong for hhfair — the real blocker was `$184`). The Known Unknowns List must therefore (a) frame each banked diagnosis as a re-verifiable hypothesis, (b) flag the **robert-generalizes-to-mine** assumption as a Critical unknown (if robert is *not* representative, P1's minimal-reproduction de-risking evaporates), (c) flag the three REPLAN-prone tracks (P1 multi-site, P2 forcing, P6 Epic-5) with a single-model hypothesis-validation as their verification (PR16), and (d) surface the camcge Walras **detection-heuristic false-positive** risk (silently transforming a well-posed model would corrupt it).

### Background

- Sprint 29 Retrospective: `docs/planning/EPIC_4/SPRINT_29/SPRINT_RETROSPECTIVE.md` (§"Sprint-30 carryforwards" [lines 54–61] — the six carryforward tracks; §"Firm deliverables" — the `_fx_` warm-start / maxmin fix / `--resolve-changed` gate that already landed; the metrics table)
- Sprint 29 Known Unknowns: `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` (Cat 1–8 — review for open/end-of-sprint items; especially the Category-1 head-offset, Category-2 rocket, Category-5 camcge, and Category-7 offset-alias unknowns whose Sprint-30 dispositions are now known)
- Sprint 30 scope: `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30 (Weeks 25–26)" (Priorities 1–8 + Acceptance Criteria + Estimated Effort + Risk Level)
- Carryforward + backlog issues: `docs/issues/ISSUE_{1443,1236,1385,1146,1143,1330}_*.md` (local) + GitHub #1462, #1111, #1112 (the Sprint-30 tracks) + the Class-B CGE cohort (irscge/lrgcge/moncge/stdcge/marco). **Note:** #1443's ISSUE doc already records the robert second-instance finding + the 3-site trace; #1236 already records the `$184` blocker; #1385 already records the banked cross-terms — these are the Day-0-hypothesis starting points.
- Sprint-29 diagnostic + design docs that Sprint 30 consumes: `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` (the Track-A/B/C dispositions), `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (the Case-b/c partition + the Class-B CGE cluster), `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md`, `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the paper-verified Walras transformation + its §5 open questions)

### What Needs to Be Done

1. **Review Sprint 29 carryforward / end-of-sprint KUs.** Migrate any open items from `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` and the retro carryforwards into Sprint 30 numbering with full text and forward-links to the Sprint 30 categories they drive.

2. **For each Priority area, brainstorm unknowns** (assumption / how-to-verify / priority / risk-if-wrong), organized by category aligned to the PROJECT_PLAN priorities:

   **Category 1 (P1 head-domain-offset emit architecture — #1443 mine + robert):**
   - Does a correct head-offset cross-term + dual-transfer index-map that fixes **robert** (pure constant offset) generalize to **mine** (adds `li(k)`/`lj(k)` parameter offsets)? **(Critical — PR16; robert is the minimal reproduction that de-risks P1; if it does not generalize, mine is a separate multi-site fix.)**
   - Is the coordinated re-derivation across the **three** emit sites (`comp_pr` emission, the `--nlp-presolve` dual transfer `_emit_nlp_presolve`, the `stat_x` cross-term) an ≤ 14–20h fix, or does each fixed site expose the next (deeper architectural)?
   - Does the head-offset fix leave the cold LCP feasible (mine's `x → 4e10` blowup resolved), or is there a residual bound-complementarity coupling?

   **Category 2 (P2 rocket #1462 non-convex forcing):**
   - Which forcing lever (trust-region damping / homotopy-continuation / multi-start from perturbed warm-starts) moves rocket's MS-5 toward MS 1/2 at 1.0128, given the `_fx_` warm-start already landed and the residual is intrinsic? **(Critical — PR16 single-lever validation.)**
   - Is a forcing lever expressible inside nlp2mcp's emitted GAMS (e.g., a continuation parameter / bound relaxation schedule), or does it require a PATH solver option (a clean Sprint-31 PATH-consultation hand-off)?
   - Does the same forcing lever recover any of the cold-convex Case-c residue from the Sprint-29 cohort survey (shared payoff)?

   **Category 3 (P3 hhfair #1236 widened-VARIABLE presolve fix):**
   - Does generalizing the #1449 widened-symbol handling from the *parameter* case to the *variable* case clear the `$184`, given `n` is a live nonlinear-stationarity coefficient (`n(t)` widened to `n(tl)`)? **(Critical — the residual MCP must compile before the CES verdict is readable.)**
   - After the `$184` clears, is hhfair's CES/product mismatch a localizable Case-b `stat_*` row, or an inherent non-convexity (Case-c → Sprint 31)?

   **Category 4 (P4 #1385 symbolic runtime-guard cross-term emit):**
   - Do the Sprint-29-banked hand-derived `J_gᵀ·lam` cross-terms materialize atomically with the runtime-guarded equation-body re-emit for **sarf** (the reference target), with no quoted-set-name multiplier indices?
   - Is sarf's skipped-constraint instance count tractable at emit time, or does the symbolic re-emit re-introduce the translate-timeout blow-up Option-1 short-circuited?

   **Category 5 (P5 offset-alias cross-terms #1111/#1112 — polygon + himmel16):**
   - Was the Sprint-29 Day-5 revert caused by the offset-image cross-term being *coupled* with the distance-Jacobian (so both must land together), and does a coordinated fix avoid the regression?
   - Does the localized polygon/himmel16 fix stay gateable to the cyclic/successor-offset shape, or does it require the #1111 alias-aware-differentiation / #1112 dollar-condition-propagation core (→ Sprint 31 architectural filing)?

   **Category 6 (P6 camcge #1330 → Epic 5 Walras transformation):**
   - Does the paper-verified drop-`lmequil` + fix-`cpi=1` transformation actually reach MODEL STATUS 1 at 191.7346 in GAMS (empirical confirmation of `CGE_DEGENERACY_SCOPING.md` §3)? **(Critical — the transformation is proven on paper only.)**
   - Is there a robust degeneracy-detection heuristic that does **NOT** false-flag a well-posed model (silently dropping a user row / fixing a price would corrupt a non-degenerate problem)?
   - Is the redundant-row + numéraire selection a single automatic rule, or a per-model declaration?

   **Category 7 (P7 Class-B CGE `stat_pz` + cold-convex residue):**
   - Is the Class-B CGE `stat_pz` residual (irscge/lrgcge/moncge/stdcge/marco) a single general-emit coefficient discrepancy the harness localizes (confirmed NOT Walras, Sprint 29 Day 12), and does one fix convert several models?
   - What is the disposition of the remaining cold-convex Case-c residue — Sprint-31 forcing, or documented inherent non-convexity?

   **Category 8 (P8 infrastructure — property tests, re-baseline, forcing scaffold):**
   - Does the head-domain-offset cross-term shape need a new `test_ad_crossterm_shapes.py` fixture (the offset-alias-successor shape already exists as `shape8`, currently xfail; `shape7` is the cyclic variant), and does landing the offset-alias fix let the existing `shape7`/`shape8` xfail be enabled?
   - Does the solution-forcing harness scaffold (from P2) provide a stable entry point the renumbered Sprint 31 PATH-consultation + forcing sprint can inherit?

3. **Assign priority + verification** to each unknown; write the Task-to-Unknown mapping appendix (which prep task resolves which unknown). Aim for **24–32 unknowns across 8 categories**.

4. **Update this PREP_PLAN** with the "Unknowns Verified" metadata per downstream task, and add a CHANGELOG entry.

### Changes

Created `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` (25 unknowns across the 8 Sprint-30 priority categories) + the Task-to-Unknown mapping appendix; updated the "Unknowns Verified" metadata + Deliverables/Acceptance-Criteria lines on Tasks 2–10 below; CHANGELOG entry.

### Result

**COMPLETE (2026-07-04).** `KNOWN_UNKNOWNS.md` authored with **25 unknowns** (target 24–32) across **8 categories** aligned to the PROJECT_PLAN Sprint-30 priorities. Priority distribution: **6 Critical / 10 High / 7 Medium / 2 Low** (24% / 40% / 28% / 8%). Per-unknown research estimates sum to ~36h; the authoritative scheduling budget is the per-task 34–48h in this PREP_PLAN. Every unknown starts 🔍 INCOMPLETE and is assigned to a downstream prep task (2–10) in the mapping appendix. The three REPLAN-prone Criticals (1.1/1.2 head-offset multi-site, 2.1 rocket forcing, 6.1/6.2 camcge Epic-5) and the robert→mine generalization (1.1) + the camcge detection-heuristic false-positive (6.2) are captured as required.

### Verification

```bash
# Document exists
test -f docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md && echo "KU list present"

# 8 categories aligned to the PROJECT_PLAN Sprint-30 priorities (expect 8)
grep -cE "^# Category [0-9]+:" docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md

# Every numbered unknown carries a "How to Verify" section
u=$(grep -cE "^## Unknown [0-9]+\.[0-9]+:" docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md)
v=$(grep -cE "^### How to Verify" docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md)
echo "unknowns=$u how-to-verify=$v (should match)"

# The robert-generalizes-to-mine Critical unknown is present
grep -iq "robert" docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md && echo "robert generalization unknown present"

# Carryforward + backlog issues referenced
grep -oE "#(1443|1462|1236|1385|1146|1143|1330|1111|1112)" docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md | sort -u
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` — 24–32 unknowns across 8 categories aligned to the Sprint-30 priorities, each with Priority / Assumption / Research Questions / How to Verify / Risk if Wrong / Estimated Research Time / Owner / Verification Results (🔍 INCOMPLETE)
- A Task-to-Unknown mapping appendix
- Updated `PREP_PLAN.md` "Unknowns Verified" metadata on Tasks 2–10
- CHANGELOG entry

### Acceptance Criteria

- [x] KNOWN_UNKNOWNS.md created with 8 categories aligned to the Sprint-30 priorities
- [x] 24–32 unknowns (25), each with Priority / Assumption / How to Verify / Risk if Wrong / Owner
- [x] The three REPLAN-prone tracks (P1 multi-site, P2 forcing, P6 Epic-5) flagged Critical with a single-model validation
- [x] The robert-generalizes-to-mine Critical unknown is present (P1 de-risking hinges on it — Unknown 1.1)
- [x] The camcge Walras detection-heuristic false-positive risk is captured (P6 — Unknown 6.2)
- [x] Sprint-29 open/carryforward KUs migrated with forward-links (the three INVERTED Sprint-29 unknowns → Categories 1/2/6-7)
- [x] Task-to-Unknown mapping appendix present
- [x] CHANGELOG updated

---

## Task 2: Sprint 29 → Sprint 30 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 3–4 hours (actual: ~2h)
**Completed:** 2026-07-05
**Deadline:** Before Sprint 30 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 8.2 (contributes the per-target Day-0 bucket to 1.1 / 2.1 / 3.1 / 6.1)

### Objective

Establish the Sprint 30 Day-0 baseline as the Sprint 29 final state, with per-model bucket provenance for the Sprint-30 target models and the genuine-vs-methodology Match split carried forward, so Sprint 30's targets land on genuine transitions. This is lighter than the Sprint-29 baseline task because the **re-baseline tooling and discipline already exist** (Sprint 29 Priority 8 built `--resolve-changed` + the PR25 re-baseline step) — this task *applies* them to the Day-0 DB, it does not build them.

### Why This Matters

Sprint 29 closed with the headline Match at 92 but a **genuine floor of 69** (the +23 gap is the Sprint-28 methodology lift the Sprint-29 retrospective kept flagged). Sprint 30's Match target is "maintain ≥ 92 as-measured; **genuine floor 69 → ≥ 72**" — so the baseline must carry the genuine/methodology split forward, or the +3 genuine-floor goal is unmeasurable. Equally, the Solve target (≥ 109) depends on **both** mine (P1) and rocket (P2) recovering from `model_infeasible`, so the Day-0 bucket for each Sprint-30 target model must be pinned (mine `model_infeasible`, rocket `model_infeasible`, hhfair `model_optimal`-mismatch, robert `model_optimal_presolve`-match, camcge `model_infeasible`).

### Background

- `data/gamslib/gamslib_status.json` — the Sprint 29 final retest DB (Solve 107 / Match 92 / model_infeasible 7 / Translate 135)
- `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` (the bucket-provenance + genuine-vs-methodology template)
- `docs/planning/EPIC_4/SPRINT_29/SPRINT_LOG.md` §"Day 13" (the final PR25 tally: genuine floor 69; the Sprint-30-carryforward buckets)
- `scripts/gamslib/run_full_test.py` `_cold_objective_mismatches_nlp` (the methodology source) + `scripts/sprint_audit/changed_emit_artifacts.py` (the changed-golden diff, now the checkpoint at-risk-list source)

### What Needs to Be Done

1. **Assert Day-0 = Sprint 29 final** — confirm `git diff <S29-close-SHA>..HEAD -- src/ scripts/` is empty (no `src/` drift since the Sprint 29 close) so the Day-0 metrics equal the Sprint 29 final without a fresh 4h retest.
2. **Recompute the canonical bucket tally** from the committed DB (`get_candidate_models`, canonical 142): Solve 107, Match 92, model_infeasible 7 — matching the Sprint 29 close.
3. **Carry the genuine-vs-methodology split forward** — the genuine floor is 69; document which Sprint-30 tracks convert methodology/warm matches into genuine cold matches (robert P1, hhfair P3, polygon/himmel16 P5, Class-B CGE P7) so the "genuine floor → ≥ 72" target is attributable.
4. **Pin the per-Sprint-30-target Day-0 bucket + projected delta** (mine, rocket, hhfair, robert, sarf, polygon, himmel16, camcge, the Class-B CGE cluster), each labeled genuine bucket-to-success vs already-banked, mirroring `BASELINE_METRICS.md §3`.

### Changes

Authored `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` (§0 Day-0 assertion + latent-snippet finding, §1 headline counts, §2 genuine/methodology split, §3 per-target bucket provenance + PR25 tally, §4 scope freeze). Recomputed the canonical tally from the committed DB via `get_candidate_models`. Updated `KNOWN_UNKNOWNS.md` Unknown 8.2 → ✅ VERIFIED. CHANGELOG entry.

### Result

**COMPLETE (2026-07-05).** Day-0 = Sprint 29 final, **no fresh retest**: `git diff 68b5b4a7..HEAD -- src/ scripts/` empty (every post-close commit docs-only). Canonical recompute (142 scope) = **Parse 142 · Translate 135 · Solve 107 · Match 92 · Mismatch 9 · model_infeasible 7** — reproduces the Sprint 29 final headline exactly. Genuine floor **69** carried forward (methodology ~23); genuine-floor → ≥ 72 conversion map documented (robert P1 / polygon-himmel16 P5 / Class-B CGE P7 / hhfair P3). Per-target Day-0 buckets pinned: mine/rocket/camcge `model_infeasible`; hhfair `model_optimal`+mismatch (72.147 vs 87.159); robert/polygon/himmel16 + Class-B cluster `model_optimal_presolve`+match; sarf `translate_failure`. **Two findings:** (a) the committed DB is byte-unchanged since the *Sprint 28* close because Sprint 29 netted no bucket change (all headline movers REPLAN'd); (b) the `git log --grep='SPRINT 29 CLOSED' -1` auto-derive snippet is now ambiguous (resolves to a docs-only PR-#1490 commit, not the true close) — drift result identical, but the schedule (Task 10) / tooling audit (Task 8) should use the pinned SHA or `git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1`.

### Verification

```bash
# Baseline doc exists
test -f docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md && echo "baseline present"

# No src/scripts drift since Sprint 29 close (Day-0 == S29 final)
# Use the OLDEST match (| tail -1) — later prep commits quote "SPRINT 29 CLOSED" in their bodies,
# so `-1` (newest) would resolve to a docs-only review-fix commit, not the true close.
S29=$(git log --grep='SPRINT 29 CLOSED' --format=%H | tail -1)
git diff --quiet "$S29"..HEAD -- src/ scripts/ && echo "no src/ drift — Day-0 == S29 final" || git diff --stat "$S29"..HEAD -- src/ scripts/

# DB headline counts recomputed (canonical scope) — expect Solve 107 / Match 92 / infeasible 7
grep -E "Solve 107|Match 92|model_infeasible 7|genuine floor 69" docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md

# Genuine-vs-methodology partition + per-target bucket table present
grep -qi "genuine" docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md && grep -qiE "robert|rocket|hhfair|camcge" docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md && echo "partition + targets present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` — Day-0 = Sprint 29 final; canonical bucket tally; genuine-floor-69 carry-forward; per-Sprint-30-target bucket provenance with PR25 projection labels
- Confirmation that no fresh retest is needed (no `src/` drift since the S29 close)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 8.2 (Day-0 baseline + genuine floor)

### Acceptance Criteria

- [x] BASELINE_METRICS.md created; Day-0 asserted = Sprint 29 final (no `src/` drift)
- [x] Canonical bucket tally recomputed (Solve 107 / Match 92 / model_infeasible 7)
- [x] Genuine floor 69 carried forward with the genuine-floor → ≥ 72 conversion map
- [x] Per-Sprint-30-target Day-0 bucket + projected-delta table (mine/rocket/hhfair/robert/sarf/polygon/himmel16/camcge/Class-B CGE)
- [x] Each projected delta labeled genuine vs already-banked (PR25)
- [x] Unknown 8.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Head-Domain-Offset Emit-Architecture Design + robert Minimal Reproduction (Priority 1 Foundation)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 5–7 hours (actual: ~5h)
**Completed:** 2026-07-05
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (AD/KKT specialist)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4

### Objective

Turn the Sprint-29 Day-6/7 3-site head-offset trace into a concrete **index-map design** the Sprint-30 implementation follows, and establish **robert** as the minimal reproduction that de-risks the whole Priority-1 track. This is the hardest and highest-leverage prep task: Priority 1 is the deepest carryforward (a multi-site emit-architecture re-derivation), and its achievable scope is unknown until the index-map is designed and robert's generalization to mine is validated on paper.

### Why This Matters

Sprint 29 Day-7 REPLAN'd #1443 mine precisely because the fix is **not** a single-site emit bug: the head-domain-offset constraint `pr(k,l+1,i,j)` requires a coordinated re-derivation of the `l+1` head-offset index map across three emit sites — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve`), and (3) the (landed) `stat_x` cross-term — plus the cold-start LCP consistency (mine's `x → 4e10` blowup). Sprint 29 Day-12 then found **robert** is a second instance of the *same class* but the **pure-constant-offset sub-case** (`sb(r,tt+1)` with a constant `+1`, no `li(k)`/`lj(k)` parameter offset): `x(p,tt)`'s cross-term must be `sum(r, a(r,p)*nu_sb(r,tt+1))` but the emit produces `nu_sb(r,tt)`. Because robert is *strictly simpler*, a correct head-offset cross-term emit that fixes robert **should** generalize to mine — so robert is the ideal minimal reproduction. But that generalization is an **assumption** (Unknown 1.1): this task validates it on paper before the schedule commits the P1 budget, so the sprint knows whether P1 is "one fix, two models" or "robert first, then a separate mine multi-site fix."

### Background

- `docs/issues/ISSUE_1443_*.md` (the Status line records the Sprint-29 Day-7 REPLAN + the Day-12 robert second-instance finding; the "Day-4 root-cause probe" + "Pushed-further check" sections record the 3-site trace + the 22/30 systemic `stat_x` cells)
- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` Track A (the head-offset budget/architecture pivot + the reallocation plan)
- `src/emit/emit_gams.py` `_emit_nlp_presolve` (~line 1281 — the `lam_<eq>.l = abs(<eq>.m)` dual transfer; ~1297/1310 the `piL/piU` bound-complementarity inits), `src/kkt/stationarity.py` `_try_build_param_offset_crossterm` (the landed `stat_x` cross-term), and the `comp_pr` emission path
- `scripts/diagnostics/kkt_residual.py` (the residual → 0 confirmation on robert, then mine)
- `data/gamslib/raw/robert.gms` (the minimal reproduction) + `data/gamslib/raw/mine.gms` (the full case)

### What Needs to Be Done

1. **Hand-derive robert's head-offset cross-term + dual-transfer index map** — for `sb(r,tt+1)`, derive the correct `x(p,tt)` stationarity cross-term `sum(r, a(r,p)*nu_sb(r,tt+1))` and the `--nlp-presolve` dual transfer that reads `sb.m` at the `tt+1` head-offset position; verify the eliminated-KKT residual → 0 at robert's NLP optimum via `kkt_residual.py`.
2. **Design the three-site index-map coordination** — write the concrete design (which function at each of the three emit sites inverts the head offset onto the multiplier index, and how the constant-offset case (robert) and the parameter-offset case (mine, `li(k)`/`lj(k)`) share one code path vs branch). Identify the gate that fires only on `has_head_domain_offset`.
3. **Validate the robert → mine generalization on paper** — show that mine's `l+1 × li(k)/lj(k)` case is the constant-offset design with the parameter offset composed in (the `sum(k, lam_pr(k,l,i-li(k),j-lj(k)) - lam_pr(k,l-1,i,j))` shape the landed `stat_x` already uses), so a correct robert fix generalizes. If it does NOT generalize (Unknown 1.1 = WRONG), document mine as a separate multi-site fix and re-size P1.
4. **Confirm the cold-LCP-consistency question** — whether the head-offset fix alone resolves mine's `x → 4e10` blowup, or a residual bound-complementarity coupling remains (feeds the Task-5 gate + Task-6 REPLAN assessment).

### Changes

Authored `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (robert re-derivation + the two cold-solve control experiments; mine's firm `comp_pr` bug; the 3-site table; the generalization verdict; the P1 re-scope). Updated `KNOWN_UNKNOWNS.md` Unknowns 1.1 (❌ WRONG), 1.2 (mine-only), 1.3 (robert ✅), 1.4 (❌ WRONG). CHANGELOG entry. No `src/`/golden change (all probes were `/tmp` copies, reverted).

### Result

**COMPLETE (2026-07-05) — a PR24 correction that re-scopes Priority 1.** Empirical re-derivation **refuted the banked robert diagnosis**: cold-solve control experiments on `robert_mcp.gms` show patching **only** `stat_x` to `nu_sb(r,tt+1)` (the banked "fix") leaves robert at the spurious **6741.67**, while patching **only** `stat_s`'s objective gradient (drop-in `−res-value(r)` boundary term at `tt=4` + guard `storage-c(r)` to `t(tt)`) makes robert cold-solve to **11025.0 = NLP optimum (MATCH)**. So robert's real bug is an **objective-gradient boundary-term drop** (same class as #1447 maxmin), NOT the head-offset cross-term — and it is a **different class** from mine's firm `comp_pr` `l+1`-head × `li(k)`/`lj(k)`-parameter-offset coupling. **Unknown 1.1 = ❌ does NOT generalize.** Favourable: **P1 splits into two independent tracks** — robert (genuine-floor +1, LOW-risk standalone objective-gradient fix ~2–4 h, decoupled) and mine (+1 Solve, HIGH-risk multi-site `comp_pr` re-derivation ~10–16 h, REPLAN-prone). robert's cold LCP is confirmed feasible (11025, no warm-start); the 3-site coordination is mine-only. Fed to Task 5 (record robert as objective-gradient / head-offset architecture as mine-only), Task 6 (REPLAN mine only), Task 10 (schedule robert early + standalone).

### Verification

```bash
# Design doc exists
test -f docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md && echo "design present"

# robert minimal-reproduction residual check recorded (harness)
grep -qi "robert" docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md && grep -qiE "residual|kkt_residual|nu_sb" docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md && echo "robert repro + residual present"

# The three emit sites named + the robert→mine generalization verdict recorded
grep -qE "comp_pr|_emit_nlp_presolve|stat_x" docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md && grep -qiE "generaliz" docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md && echo "3-site + generalization verdict present"

# harness runs on robert + mine
for m in robert mine; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "verdict|dual transfer"; done
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` — robert's hand-derived head-offset cross-term + dual-transfer index map (with the `kkt_residual.py` residual → 0 confirmation); the three-site index-map coordination design; the robert → mine generalization verdict; the cold-LCP-consistency finding
- robert established as the P1 minimal reproduction; mine as the full multi-site case
- The P1 budget sized (one shared fix vs robert-then-mine) feeding Task 5 + Task 10
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4

### Acceptance Criteria

- [x] HEAD_OFFSET_ARCHITECTURE_DESIGN.md created
- [x] robert re-derived; residual → 0 / cold-match 11025 at the NLP optimum achieved — but via the **`stat_s` objective-gradient fix**, not the head-offset cross-term (the banked `nu_sb(r,tt+1)` was refuted; `nu_sb(r,tt)` is already correct)
- [x] The three emit sites (`comp_pr` / `_emit_nlp_presolve` / `stat_x`) designed — **mine-only**; robert needs no site coordination
- [x] The robert → mine generalization verdict recorded (Unknown 1.1: **❌ does NOT generalize** — different bug classes)
- [x] The cold-LCP-consistency question resolved (robert ✅ confirmed cold-feasible at 11025; mine hypothesis: the `comp_pr` fix must clear `x → 4e10`)
- [x] The P1 budget re-sized on the generalization verdict (**two independent tracks**: robert ~2–4 h objective-gradient, mine ~10–16 h `comp_pr`); fed to Tasks 5 + 10
- [x] Unknowns 1.1, 1.2, 1.3, 1.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Non-Convex Forcing Strategy Survey (rocket #1462 + Cold-Convex Case-c Residue) (Priority 2 Foundation)

**Status:** ✅ COMPLETE
**Priority:** High
**Estimated Time:** 4–6 hours (actual: ~4h)
**Completed:** 2026-07-05
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (numerics / solver-interface)
**Dependencies:** Task 1
**Unknowns Verified:** 2.1, 2.2, 2.3, 7.2

### Objective

Survey the candidate **solution-forcing** strategies for rocket #1462's intrinsic non-convergence — trust-region damping, homotopy/continuation, and multi-start from perturbed warm-starts — and determine which is expressible inside nlp2mcp's emitted GAMS vs which needs a PATH solver option, so Priority 2 implements a chosen lever and Priority 8's forcing-harness scaffold has a tested entry point. This is a research-before-design task: it precedes the P2 implementation and feeds the P8 scaffold + the Task-6 REPLAN assessment.

### Why This Matters

Sprint 29 Day-2 confirmed rocket's residual MS-5 is **intrinsic non-convex convergence**, not an emit/warm-start defect (the `_fx_` warm-start landed and moved the objective 1.137 → 1.016, but MS-5 persists). So Priority 2 is fundamentally a **numerics** problem, not an emit problem — and the sprint should not improvise a forcing strategy mid-implementation. A survey up front (a) picks the lever most likely to move rocket, (b) determines the nlp2mcp/PATH boundary (a lever needing a PATH option is a clean Sprint-31 PATH-consultation hand-off, not a dead end), and (c) checks whether the same lever recovers any cold-convex Case-c residue from the Sprint-29 cohort survey (shared payoff). Without the survey, P2 risks the "improvise, partially work, defer" churn the sprint methodology is built to avoid.

### Background

- `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (the `_fx_` warm-start landed Sprint 29 Day 1; the Day-2 intrinsic-non-convergence finding; the §"Verification Methodology" forcing-probe hints)
- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` Track B (the rocket conditional-PROCEED + the "feeds Sprint-31 PATH consultation" hand-off)
- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (the Case-c residue that shares the forcing need)
- `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` (non-convexity context)
- PATH solver documentation (trust-region / merit-function / crash options) — literature fallback for the PATH-option boundary

### What Needs to Be Done

1. **Enumerate the forcing levers** — for each of trust-region damping, homotopy/continuation (from a relaxed/convexified problem back to the original), and multi-start (perturbed warm-starts), record: the mechanism, whether it is expressible as emitted GAMS (a continuation parameter loop / bound-relaxation schedule / `.l` perturbation) or requires a PATH option, and the expected effect on rocket's MS-5.
2. **Prototype-probe one lever on rocket** (env-guarded, zero `src/` diff) — apply the most promising lever to rocket's presolve MCP and measure the MODEL STATUS progression toward MS 1/2 at 1.0128; record the result (or "needs a PATH option").
3. **Check shared payoff on the cold-convex Case-c residue** — does the chosen lever move any Case-c cohort model (from the Sprint-29 survey) toward a solve?
4. **Define the nlp2mcp/PATH boundary** — which levers stay in the Sprint-30 emit/scaffold vs which become the Sprint-31 PATH-consultation question.

### Changes

Authored `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (lever enumeration + boundary table, the rocket PATH-option probes, the Case-c shared-payoff check, the P8 scaffold + Sprint-31 hand-off). Updated `KNOWN_UNKNOWNS.md` 2.1/2.2/2.3/7.2. CHANGELOG entry. No `src/`/golden change (all probes were `/tmp` copies + a transient `path.opt`, reverted).

### Result

**COMPLETE (2026-07-05).** rocket prototype-probe: emitted the presolve MCP, confirmed baseline MS 5 / 477 INFES, then applied the tunable PATH levers (env-guarded `path.opt`): `proximal_perturbation` {1e-2,1e-1,1.0,1e2}, `crash_method pnewton`, `merit_function normal`, combined — **all stay MS 5**; best (`merit_function normal` + `proximal_perturbation 1e-2`) reduces INFES 477 → **382** but never converges. **No PATH-option configuration (via optfile) forces rocket** → intrinsic non-convergence confirmed. The effective levers (proximal_perturbation/crash/merit) are **PATH options** → the tuning is the **Sprint-31 PATH-consultation** hand-off; the emittable-GAMS levers (homotopy/multi-start) are the **Sprint-30 P8 forcing scaffold** + entry point. **No Case-c shared payoff:** the 4 Case-c cohort models (bearing/launch/mathopt3/robustlp) are emit-correct + already warm-match; rocket is the sole non-converging model. **Decision:** P2 Sprint-30 = the forcing scaffold (firm) + the PATH hand-off; **rocket's +1 Solve is NOT firm for Sprint 30** (conditional on Sprint-31). Fed to Task 6 (rocket PROCEED-to-scaffold, +1 Solve deferred) + Task 10 (schedule the scaffold, not a rocket-solve milestone).

### Verification

```bash
# Survey doc exists
test -f docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md && echo "forcing survey present"

# The three lever families enumerated + a chosen lever recorded
grep -qiE "trust.region|homotopy|continuation|multi.start" docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md && echo "levers enumerated"

# The nlp2mcp-vs-PATH boundary recorded (feeds the Sprint-31 hand-off)
grep -qiE "PATH option|PATH consultation|nlp2mcp boundary|emitted GAMS" docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md && echo "boundary present"

# rocket forcing probe result recorded
grep -qi "rocket" docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md && grep -qiE "MODEL STATUS|MS 1|MS-5|1.0128" docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md && echo "probe result present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` — the forcing-lever enumeration (trust-region / homotopy / multi-start), the rocket prototype-probe result, the cold-convex Case-c shared-payoff check, and the nlp2mcp/PATH boundary
- The chosen P2 forcing lever + the P8 forcing-scaffold entry point
- The Sprint-31 PATH-consultation hand-off scope (the levers needing a PATH option)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 7.2

### Acceptance Criteria

- [x] NONCONVEX_FORCING_SURVEY.md created
- [x] The forcing-lever families enumerated with the nlp2mcp-emittable (homotopy/multi-start) vs PATH-option (proximal_perturbation/crash/merit) boundary per lever
- [x] Levers prototype-probed on rocket (env-guarded, zero `src/`); MODEL STATUS + INFES progression recorded (all MS 5; best 477→382 INFES)
- [x] The cold-convex Case-c shared-payoff checked (**none** — the 4 Case-c models already warm-match)
- [x] The chosen P2 lever (emitted-GAMS forcing scaffold) + the P8 scaffold entry point identified; the Sprint-31 PATH hand-off scoped
- [x] Unknowns 2.1, 2.2, 2.3, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Refresh + Author Phase 0 Acceptance Gates for the Sprint-30 Tracks (PR20 + PR24 + PR27)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 4–6 hours (actual: ~4h)
**Completed:** 2026-07-05
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (AD/KKT specialist)
**Dependencies:** Tasks 1, 3
**Unknowns Verified:** 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3

### Objective

Refresh the existing Phase 0 acceptance gates (authored in Sprint 29 Prep Task 4) with the Sprint-30 dispositions, and author the two new gates the Sprint-30 tracks need. Most Sprint-30 target issue docs (`ISSUE_{1443,1462,1236,1385,1146,1143,1330}`) already carry a `## Phase 0: Acceptance Gate` from Sprint 29 — this task updates them to reflect what Sprint 29 *learned* (mine+robert head-offset, rocket forcing, hhfair `$184`, the offset-alias Day-5 revert), and adds a **robert** gate (the P1 minimal reproduction) and a **Class-B CGE `stat_pz`** gate (the P7 general-emit backlog).

### Why This Matters

The Phase-0 gate is the scope-correctness mechanism (PR20/PR24): hand-derived KKT shape + traced fix-surface + harness verification method BEFORE any `src/` change. Sprint 29 already authored these gates, but their content is now **stale for Sprint 30** — e.g., the mine gate says "conditional, lean REPLAN-aware" (the Sprint-29 disposition), but Sprint 30's disposition is "PROCEED via the head-offset architecture (Task 3 design), robert as the minimal reproduction." The hhfair gate says the blocker is `$141`; Sprint 29 proved it is `$184` (widened-VARIABLE). Refreshing the gates keeps the Day-0 hypothesis honest (PR24) and gives the Sprint-30 implementation a correct starting point rather than the Sprint-29 REPLAN framing. The two new gates (robert, Class-B `stat_pz`) cover the tracks Sprint 29 discovered but did not gate.

### Background

- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (the PR20 4-subsection template + PR24 traced-fix-surface + PR27 harness verification)
- The existing Sprint-29 gates in `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md`
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (Task 3 — the mine+robert gate content)
- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` (the offset-alias + Class-B fix-surface hypotheses)
- `scripts/diagnostics/kkt_residual.py` (the verification method in every gate)

### What Needs to Be Done

1. **Refresh the seven existing gates** to the Sprint-30 disposition: #1443 mine (PROCEED via head-offset architecture per Task 3; robert minimal reproduction); #1462 rocket (PROCEED to a forcing lever per Task 4; the Case-c → Sprint-31 PATH exit); #1236 hhfair (the `$184` widened-VARIABLE blocker, not `$141`; CES verdict after the compile clears); #1385 (the banked cross-terms + sarf reference target); #1146/#1143 (the Day-5 revert coupling + the coordinated fix); #1330 camcge (the Walras transformation + the detection-heuristic gate per Task 7).
2. **Author a robert gate** — either in `ISSUE_1443` (shared with mine) or a new local `docs/issues/ISSUE_robert_*.md`: the hand-derived `sum(r, a(r,p)*nu_sb(r,tt+1))` cross-term, the expected emit, the `kkt_residual.py` PROCEED verdict, the traced `file:line` (Day-0).
3. **Author a Class-B CGE `stat_pz` gate** (the P7 general-emit backlog): the hand-derived `stat_pz` coefficient the harness localizes (confirmed NOT Walras), the expected emit, the per-model verdict PROCEED condition.
4. **Verify every gate** cites `kkt_residual.py` as its verification method and has an explicit Sprint-31 REPLAN exit where applicable (P1 architectural, P2 non-convex, P5 #1111/#1112 core, P6 non-degenerate).

### Changes

Added a dated 🔄 Sprint-30 refresh note to the `## Phase 0: Acceptance Gate` of `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md`; authored two new gates — `docs/issues/ISSUE_robert_objgrad_boundary_term.md` and `docs/issues/ISSUE_classB_cge_stat_pz.md` (each 4 subsections). Updated `KNOWN_UNKNOWNS.md` Unknowns 1.2/1.3/2.2 (Task-5 refresh note) + 3.1/3.2/4.1/5.2/6.1/7.1/7.3 (VERIFIED). CHANGELOG entry.

### Result

**COMPLETE (2026-07-05).** Refreshed the 7 existing gates to the Sprint-30 dispositions and authored the 2 new gates. Key refreshes: **#1443** now mine-**only** and flags the Day-12 robert note as **REFUTED** (robert → the new objective-gradient gate; P1 splits into two tracks); **#1462** records "no PATH-option configuration forces rocket → P8 scaffold + Sprint-31 PATH consultation, +1 Solve deferred"; **#1236** corrected to the `$184` widened-VARIABLE blocker (not `$141`); **#1385** to the atomic sarf runtime-guard re-emit; **#1146/#1143** to the coordinated offset-alias fix + the #1111/#1112 architectural-REPLAN boundary; **#1330** to the Epic-5 Walras transformation. New gates: **robert** (objective-gradient boundary-term, PROCEED, decoupled) and **Class-B CGE `stat_pz`** (general-emit coefficient discrepancy, PROCEED-conditional, NOT Walras). All 9 gates cite `kkt_residual.py`; REPLAN-prone gates (P1/P2/P5/P6) carry an explicit Sprint-31 exit. 10 Unknowns VERIFIED.

### Verification

```bash
# Phase 0 gate present in each Sprint-30 target issue doc
for f in 1443 1462 1236 1385 1146 1143 1330; do grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md 2>/dev/null || echo "MISSING: $f"; done

# The robert gate + the Class-B stat_pz gate exist (in ISSUE_1443 or a new doc, and a CGE doc)
grep -rliE "robert" docs/issues/ISSUE_1443_*.md docs/issues/ISSUE_robert_*.md 2>/dev/null && echo "robert gate present"
grep -rli "stat_pz" docs/issues/ 2>/dev/null | head -1 && echo "Class-B stat_pz gate present"

# The stale Sprint-29 framing is refreshed (hhfair says $184, not $141-only; mine says head-offset architecture)
grep -qi '\$184' docs/issues/ISSUE_1236_*.md && echo "hhfair refreshed to \$184"
grep -qiE "head-offset architecture|robert" docs/issues/ISSUE_1443_*.md && echo "mine refreshed to Sprint-30 disposition"

# Each gate cites the harness
for f in 1443 1462 1236 1385 1146 1143 1330; do grep -lE 'kkt_residual\.py' docs/issues/ISSUE_${f}_*.md 2>/dev/null || echo "no harness ref: $f"; done
```

### Deliverables

- Refreshed `## Phase 0: Acceptance Gate` in `docs/issues/ISSUE_{1443,1462,1236,1385,1146,1143,1330}_*.md` to the Sprint-30 dispositions
- A robert Phase-0 gate (in ISSUE_1443 or a new local doc)
- A Class-B CGE `stat_pz` Phase-0 gate
- Every gate cites `kkt_residual.py`; REPLAN-prone gates have an explicit Sprint-31 exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3

### Acceptance Criteria

- [x] The seven existing gates refreshed to the Sprint-30 dispositions (mine [robert refuted], rocket-forcing, hhfair-`$184`, #1385-banked, offset-alias-coupled, camcge-Walras)
- [x] A robert gate authored (`ISSUE_robert_objgrad_boundary_term.md` — the objective-gradient bug, not the head-offset; a separate track)
- [x] A Class-B CGE `stat_pz` gate authored (`ISSUE_classB_cge_stat_pz.md` — the P7 general-emit backlog)
- [x] hhfair gate corrected to the `$184` widened-VARIABLE blocker (not `$141`-only)
- [x] Every gate frames its fix-surface as a Day-0 hypothesis (PR24) + cites `kkt_residual.py` (PR27)
- [x] REPLAN-prone gates (P1/P2/P5/P6) have an explicit Sprint-31 exit
- [x] Unknowns 1.2, 1.3, 2.2, 3.1, 3.2, 4.1, 5.2, 6.1, 7.1, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (#1443 multi-site, #1462 forcing, #1330 Epic-5; PR16)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-06
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (AD/KKT specialist)
**Dependencies:** Tasks 3, 4, 5
**Unknowns Verified:** 1.1, 1.2, 2.1, 2.2, 6.1, 6.2

### Why this is separate from Task 5

Task 5 authors the gate (the verification *mechanism*); Task 6 assesses the *risk* (the probability and cost of REPLAN, and the budget reallocation if it fires) so the schedule (Task 10) can pre-allocate slack and a fallback ordering. Sprint 30's three deepest tracks were all REPLAN'd out of Sprint 29 *because* they proved multi-site / intrinsic / domain-specific — so the risk that they slip *again* (to Sprint 31) is the single largest schedule unknown.

### Objective

Apply the PR16 hypothesis-validation methodology to the three Sprint-30 tracks most likely to prove deeper than budgeted — #1443 (the multi-site head-offset architecture: does the robert-minimal fix generalize to mine, or is mine a separate multi-site slip?), #1462 (non-convex forcing: does a lever move rocket, or is it a PATH-option Sprint-31 hand-off?), and #1330 camcge (the Epic-5 transformation: does the paper-verified drop-row + fix-numéraire reach MS 1 empirically, or does the detection heuristic prove unreliable?) — and pin an explicit PROCEED/REPLAN signal + Sprint-31 exit + budget reallocation for each.

### Why This Matters

The Sprint-30 Solve target (≥ 109) depends on **both** mine (P1) and rocket (P2) landing. Both are REPLAN-prone: mine's generalization from robert is an assumption (Task 3), and rocket's forcing may need a PATH option (Task 4). If either slips, the Solve target misses — so the schedule must know the REPLAN probability and the reallocation (the freed budget goes to the genuine-floor Class-B CGE + offset-alias work) BEFORE Day 0, exactly as the Sprint-29 REPLAN assessment did for its three tracks.

### Background

- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` (the structural template — per-track decision pivot, single-model validation design, PROCEED/REPLAN signals, Sprint-30 exit, budget reallocation)
- `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` (Task 3 — the robert → mine generalization verdict)
- `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (Task 4 — the rocket forcing-lever result + the PATH boundary)
- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §5 (the camcge open questions — detection heuristic, per-model numéraire, empirical confirmation)
- `scripts/diagnostics/kkt_residual.py` (the Case-c verdict = the REPLAN trigger)

### What Needs to Be Done

1. **For each of the three tracks:** state the architectural hypothesis, the single-model validation experiment (the Task-3/Task-4/Task-7 result + any prototype-then-revert probe), the PROCEED signal, the REPLAN signal, and the Sprint-31 exit scope.
2. **#1443:** PROCEED if robert's fix generalizes to mine (Task 3 verdict) and the 3-site re-derivation fits ~14–20h; REPLAN mine (not robert) to a Sprint-31 head-offset-architecture workstream if it does not generalize or the cold-LCP coupling persists — robert (genuine-floor) still lands.
3. **#1462:** PROCEED if a Task-4 forcing lever moves rocket to MS 1/2; REPLAN to the Sprint-31 PATH consultation if the lever needs a PATH option — the forcing scaffold (P8) still lands.
4. **#1330 camcge:** PROCEED if the Walras transformation empirically reaches MS 1 at 191.7346 and the detection heuristic is reliable; REPLAN to a per-model-numéraire-declaration Epic-5 item if the heuristic false-flags or the numéraire selection proves per-model.
5. **Budget-reallocation plan per REPLAN:** which lower-risk priority absorbs the freed budget (mine slip → more Class-B CGE / offset-alias genuine-floor; rocket slip → the scaffold + hhfair; camcge slip → the Class-B general-emit fix).

### Changes

**COMPLETE (2026-07-06).** Authored `docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md` (modeled on the Sprint-29 template) with per-track hypothesis + single-model validation design + PROCEED/REPLAN signal + Sprint-31 exit + budget reallocation for the three REPLAN-prone tracks, plus a Budget-at-Risk tally that feeds the Task-10 schedule. Appended a "Task 6 — risk/decision layer" note to the Verification Results of Unknowns 1.1, 1.2, 2.1, 2.2, 6.1 and filled the previously-INCOMPLETE Unknown 6.2 with the RISK-ASSESSED (Task 6) decision. CHANGELOG Task-6 entry added.

### Result

- **Track A (#1443):** the Task-3 verdict (Unknown 1.1 = ❌ does NOT generalize) splits P1 → **robert = firm PROCEED** (genuine-floor +1, ~2–4 h, cold-confirmed 11025, no REPLAN branch) and **mine = PROCEED-conditional / REPLAN-prone** (the coordinated 3-site `comp_pr` head-offset re-derivation; REPLAN mine — not robert — to a Sprint-31 head-offset-architecture workstream if a 4th site surfaces or the Day-7 `ne`/`se`/`sw` cascade persists). Prior of REPLAN Medium-High.
- **Track B (#1462):** **PROCEED-to-scaffold** (the P8 forcing scaffold is firm) + **rocket's +1 Solve REPLANs to the Sprint-31 PATH consultation** (no PATH-option config converges even from the NLP optimum; prior of REPLAN High). One low-prior PROCEED-flip: a scaffold homotopy/multi-start strategy reaching MS 1/2 at 1.0128.
- **Track C (#1330 camcge):** **PROCEED-conditional** on the empirical MS-1 gate (C1: drop-`lmequil` + fix-`cpi=1` → MS 1 at 191.7346) + the detection-heuristic false-positive gate (C3); **REPLAN to a per-model-numéraire-declaration Epic-5 item (opt-in)** if the auto-heuristic false-flags or the numéraire proves per-model. The declaration fallback still lands camcge's +1 Solve (camcge is the sole inherent Walras case). Prior of REPLAN-to-declaration Medium.
- **Budget reallocation:** mine slip → Class-B CGE `stat_pz` (P7) + offset-alias (P5) genuine-floor; rocket slip → scaffold hardening + hhfair (P3); camcge slip → the Class-B general-emit fix (P7). **Solve ≥ 109 is the most REPLAN-sensitive KPI** (needs both mine + rocket); the firm parts (robert / scaffold / Class-B fix / camcge declaration-fallback) land regardless, so the genuine-floor lift is robust even under a triple-REPLAN.

### Verification

```bash
# Risk assessment doc exists
test -f docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && echo "risk assessment present"

# Each of the three tracks has PROCEED + REPLAN signals
grep -cE "PROCEED|REPLAN" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md
grep -qiE "#1443|mine|robert" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && grep -qiE "#1462|rocket" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && grep -qiE "#1330|camcge" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && echo "3 tracks present"

# Sprint 31 exits + budget-reallocation plan present
grep -qiE "Sprint 31|Sprint-31" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && grep -qiE "realloc|freed budget|budget-at-risk" docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md && echo "exits + reallocation present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md` with per-track hypothesis, validation experiment, PROCEED/REPLAN signals, Sprint-31 exit
- A budget-reallocation plan for each possible REPLAN
- The three REPLAN-prone unknowns resolved into scheduled decisions (feeds Task 10's slack allocation + fallback ordering)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2

### Acceptance Criteria

- [x] Risk assessment created covering #1443 (multi-site), #1462 (forcing), #1330 (Epic-5)
- [x] Each track has an architectural hypothesis + single-model validation experiment
- [x] Each track has explicit PROCEED and REPLAN signals tied to the Task-3/4/7 result
- [x] Each track has a Sprint-31 exit scope + the firm part that lands regardless (robert / scaffold / Class-B fix)
- [x] Budget-reallocation plan specified per REPLAN
- [x] Feeds the Task-10 schedule's slack allocation and fallback ordering
- [x] Unknowns 1.1, 1.2, 2.1, 2.2, 6.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: camcge → Epic 5 Walras Transformation Design (Priority 6)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-06
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (CGE / Epic-5)
**Dependencies:** Task 1
**Unknowns Verified:** 6.1, 6.2, 6.3

### Objective

Turn the paper-verified Walras transformation in `EPIC_5/CGE_DEGENERACY_SCOPING.md` into an implementation design: the **degeneracy-detection heuristic** (how the preprocessing layer recognises a Walras-degenerate model without false-flagging a well-posed one), the **per-model numéraire + redundant-row selection** rule, and the **non-degenerate-model guard**, so the in-sprint Priority-6 implementation follows a design rather than re-deriving the open questions.

### Why This Matters

The Sprint-29 Epic-5 scoping doc proved the transformation (drop one redundant market-clearing row + fix a price numéraire) is **solution-preserving on paper** and reproduces camcge's NLP optimum 191.7346 — but it left three open questions (`CGE_DEGENERACY_SCOPING.md` §5) that block implementation: (Q1) the numéraire-selection rule, (Q2) the degeneracy-detection heuristic that must NOT false-positive a well-posed model, and (Q3) the empirical confirmation. Priority 6 is medium-risk *because* of these open questions — silently transforming a non-degenerate model would corrupt it. This task designs the answers so P6 is an implementation, not a research spike, and so the Task-6 REPLAN assessment can judge whether the heuristic is reliable enough to PROCEED.

### Background

- `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the paper-verified transformation §3; the scope boundary §4; the open questions §5)
- `docs/issues/ISSUE_1330_*.md` (the camcge structural-singularity diagnosis; the MS-4-at-iteration-0 signature; the `equil`/`lmequil` linear dependence)
- The CGE cohort sources (`data/gamslib/raw/camcge.gms` + `irscge/lrgcge/moncge/stdcge` for the generality check)
- `scripts/diagnostics/kkt_residual.py` + the PATH basis-singularity report (the detection-heuristic evidence)

### What Needs to Be Done

1. **Design the degeneracy-detection heuristic** — a rank check on the market-clearing block, or the PATH basis-singularity report, or a model-structure signature; specify the false-positive guard (a well-posed model must be left untouched) and how the layer decides to transform vs pass through.
2. **Design the redundant-row + numéraire selection** — the rule for choosing which market-clearing row to drop and which price to fix (a SAM-largest-sector rule, a CPI aggregate, or a per-model declaration); verify it reproduces camcge's 191.7346 on paper.
3. **Scope the empirical-confirmation experiment** — the Day-0 GAMS run (drop-`lmequil` + fix the concrete consumption-weighted numéraire `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` — "`cpi=1`" is generic shorthand; camcge has no literal `cpi` — → MS 1 at 191.7346) that Priority 6 runs first, and the cohort-generality check (does any *other* corpus model need the transformation, or is camcge the sole inherent case?).
4. **Record the nlp2mcp/Epic-5 boundary** — the transformation is CGE-domain preprocessing (Epic 5), invoked only for detected-degenerate models; the general-emit fixes (Class-B `stat_pz`, empty-equation multipliers) stay in nlp2mcp (P7).

### Changes

**COMPLETE (2026-07-06).** Authored `docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` — grounded in a read of `data/gamslib/raw/camcge.gms` (equation/variable structure) + the `ISSUE_1330` diagnosis + the Epic-5 scoping paper argument. Resolves the three `CGE_DEGENERACY_SCOPING.md` §5 open questions into a design: the S1∧S2∧S3 detection heuristic with a pass-through false-positive guard (§2), the drop-`lmequil` + consumption-weighted-numéraire selection rule reproducing 191.7346 on paper (§3), the P6 Day-0 empirical experiment + cohort-generality check (§4), and the nlp2mcp/Epic-5 boundary (§5). Updated KNOWN_UNKNOWNS Unknowns 6.1/6.2/6.3 to VERIFIED (Task-7 layer) + CHANGELOG Task-7 entry.

### Result

- **Grounding refinement (the key finding):** camcge has **no `cpi` variable** and `er` is a fixed `Scalar` (=.21) that anchors only *traded* prices — so the scoping-doc canonical "fix-`cpi=1`" is instantiated concretely as a **base-consumption-weighted composite-price index** on the existing `p(i)`/`pd0(i)`: `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` (a CPI=1 normalization). This is the exact numéraire the P6 Day-0 run needs.
- **Detection heuristic (6.2):** transform only if **S1** (market-clearing-block rank deficiency) ∧ **S2** (MS-4-at-iter-0 + residual-clean + PATH basis-singular) ∧ **S3** (CGE structure, no existing numéraire); **default = pass through untouched** (the correctness guard — a well-posed CGE with a full-rank block is never touched). The residual-clean sub-check separates structural singularity from an emit bug (`CASE_B`).
- **Selection rule (6.3):** drop **one** redundant row instance `lmequil(lc_drop)` (Walras' law ⇒ rank deficiency exactly 1 — a single labor category, **not** the whole `lc` family; the other `lmequil` instances and all `equil(i)` stay enforced) + the consumption-weighted numéraire; by homogeneity quantities are invariant along the price ray, so the numéraire is a base-year normalization (λ=1 only if the unscaled equilibrium already satisfies it), a *selection* not a *perturbation* ⇒ omega **191.7346** on paper. Per-model (closure/SAM dependent) → ships with a **per-model declaration fallback (opt-in)**, acceptable because camcge is the sole inherent Walras case.
- **Empirical experiment (6.1):** drop-`lmequil` + fix-the-numéraire → **MS 1 at 191.7346**, non-singular basis (P6 Day-0 gate); the §4.2 cohort sweep (camcge + irscge/lrgcge/moncge/stdcge) is the false-positive validation — expected only camcge flagged.
- **Boundary:** the Walras transform is Epic-5 CGE-domain preprocessing (invoked only for detected-degenerate models); the Class-B `stat_pz` general-emit fix (confirmed NOT Walras) stays in nlp2mcp (P7). Feeds the Task-6 REPLAN reliability judgment (the auto-heuristic is PROCEED-conditional with the declaration fallback).

### Verification

```bash
# Design doc exists (extends the Epic-5 scoping doc or a new Sprint-30 design)
test -f docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "camcge design present"

# The three open questions answered: detection heuristic + numéraire rule + empirical experiment
grep -qiE "detect|rank|basis-singular|false.positive|false.flag" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "detection heuristic designed"
grep -qiE "numéraire|numeraire|redundant.row|drop.*row" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "selection rule designed"
grep -qE "191.7346" docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md && echo "empirical target recorded"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` — the degeneracy-detection heuristic + false-positive guard; the redundant-row + numéraire-selection rule (reproducing 191.7346 on paper); the empirical-confirmation experiment scope; the cohort-generality check plan
- The three `CGE_DEGENERACY_SCOPING.md` §5 open questions resolved into a design
- The nlp2mcp/Epic-5 boundary (Class-B general-emit fixes stay in nlp2mcp)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3

### Acceptance Criteria

- [x] CAMCGE_WALRAS_TRANSFORM_DESIGN.md created
- [x] The degeneracy-detection heuristic designed with an explicit non-degenerate-model false-positive guard
- [x] The redundant-row + numéraire-selection rule designed; reproduces 191.7346 on paper
- [x] The empirical-confirmation experiment (drop-`lmequil` + fix the concrete consumption-weighted numéraire `sum(i$cles(i), cles(i)*p(i)) =e= sum(i$cles(i), cles(i)*pd0(i))` — camcge has no `cpi` — → MS 1) scoped for Priority 6 Day-0
- [x] The cohort-generality check plan present (is camcge the sole inherent case?)
- [x] The nlp2mcp/Epic-5 boundary recorded (Class-B general-emit stays in nlp2mcp)
- [x] Unknowns 6.1, 6.2, 6.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Reusable-Tooling Readiness Audit for the Sprint-30 Model Classes

**Status:** ✅ COMPLETE
**Completed:** 2026-07-06
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (Tooling)
**Dependencies:** Task 1
**Unknowns Verified:** 1.4, 8.1, 8.3, 8.4

### Objective

Audit the Sprint-29 diagnostic/CI tools — `kkt_residual.py`, `check_presolve_divergence.py`, `check_golden_staleness.py`, `changed_emit_artifacts.py`, and the `--resolve-changed` checkpoint re-solve — against the new Sprint-30 model classes (head-domain-offset multipliers `lam_pr`/`nu_sb`, the widened-VARIABLE presolve emit, the forcing-harness scaffold, the offset-alias-successor cross-term shape), and identify any *minimal* extension needed before Day 1 so the in-sprint work runs on tooling that already covers the cases.

### Why This Matters

Sprint 30 reuses the Sprint-28/29 tooling rather than rebuilding it — but the new model classes stress paths the tooling has not yet been audited against: the harness dual-transfer must handle the head-offset `lam_pr`/`nu_sb` multipliers (Task 3 relies on the residual → 0 confirmation being trustworthy), the `--resolve-changed` gate must cover the widened-VARIABLE presolve regens, and the AD property-test catalog must be extensible to the new head-offset shape — the offset-alias `shape7`/`shape8` fixtures already exist (`shape8` xfail, to be enabled when the fix lands) (P8). A readiness audit confirms this up front so the in-sprint diagnosis runs on tooling that already covers the cases, not one that silently mis-classifies them (the Sprint-29 hhfair `$141`→`$184` lesson: trust the tool's actual output, not the assumed one).

### Background

- `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` (the Sprint-29 audit template + the "gap list = none" verdict)
- `scripts/diagnostics/kkt_residual.py` (dual-transfer self-check — audit on robert + mine head-offset multipliers), `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/changed_emit_artifacts.py`, and the `--resolve-changed` mode (Sprint 29 Priority 8)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (the property-test catalog — extensibility for head-offset + offset-alias shapes)
- `scripts/sprint_audit/golden_staleness_allowlist.txt` + `scripts/diagnostics/presolve_divergence_allowlist.txt` (allowlist currency)

### What Needs to Be Done

1. **KKT-residual harness:** run it on robert + mine (head-offset `lam_pr`/`nu_sb` multipliers) and confirm the dual-transfer self-check reports CONSISTENT; if it mis-transfers the head-offset multiplier, scope the minimal one-line index-mapping extension as a Day-0 task.
2. **`--resolve-changed` checkpoint re-solve:** confirm it covers the widened-VARIABLE presolve regens (hhfair P3) and the head-offset goldens (mine/robert P1) — i.e., the changed-golden diff surfaces them as at-risk.
3. **Property-test catalog:** confirm `test_ad_crossterm_shapes.py` is extensible to the head-domain-offset shape (the one new fixture P8 adds) and that the existing `shape8_offset_alias_successor` (currently xfail) + `shape7_offset_alias_cyclic` can be enabled once the offset-alias fix lands; no structural blocker.
4. **Allowlists + detector:** confirm the golden-staleness + divergence allowlists are current at Sprint 30 Day 0 (no new models need allowlisting/removing); confirm the divergence detector soft-classifies the Class-B CGE + cold-convex residue (no false hard-fails).
5. **Produce a gap list** (each Day-0 extension ≤ 1h) or "no extensions needed".

### Changes

**COMPLETE (2026-07-06).** Authored `docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md` — per-tool readiness verdict for the Sprint-30 classes, from **actual read-only tool runs** (the harness on robert + mine, the crossterm-shapes pytest, the detector logic + allowlist review, the `--resolve-changed` surface). Updated KNOWN_UNKNOWNS Unknowns 1.4 (Task-8 tooling layer)/8.1/8.3/8.4 to VERIFIED + CHANGELOG Task-8 entry.

### Result

- **Harness (`kkt_residual.py`):** ran on robert + mine — **dual transfer CONSISTENT on both** (robert CASE_B `stat_x(high,3)` rel 7.20; mine CASE_B `stat_x(4,1,1)` rel 1.33). The harness handles the head-offset `nu_sb`/`lam_pr` multipliers with no mis-transfer. **Caveat (the Task-8 nuance):** the top per-row residual on base-normalized head-offset equations is a **same-index-transfer artifact** (robert's `stat_x` is the artifact; the operative bug is `stat_s`), so per-row *localization* is corroborated with the cold-solve control (Task 3's proven method). → **one OPTIONAL non-blocking ≤ 1 h extension** (head-label multiplier warm-start); not required.
- **Divergence detector:** hard-fails on one of three embedded-NLP triggers — abort (`execerror`, korcge #1439), infeasible/non-optimal embedded NLP (camshape #1424), or no parseable objective (`emb_obj is None`) — and gates on the embedded NLP, never the MCP. So the **Class-B CGE `stat_pz`** (embedded optimal + objective present; MCP coefficient discrepancy) and the **cold-convex residue** (incl. rocket's MS-5 MCP) both **soft-classify** — no false hard-fail, no new allowlist entry.
- **`--resolve-changed`:** present on `main`; `_GOLDEN_SUFFIXES = ("_mcp_presolve.gms", "_mcp.gms")` → covers **both** the widened-VARIABLE presolve regen (hhfair P3) **and** the head-offset cold golden (mine/robert P1). Allowlists current (golden-staleness 7, divergence 1 = korcge; **#1439 + #1461 both OPEN** → keep).
- **Property catalog:** `pytest tests/integration/emit/test_ad_crossterm_shapes.py` = **7 passed, 1 xfailed** (shape8 xfail-strict #1143; shape7 passing). The head-domain-offset shape is the one genuinely-missing fixture (a clean one-file add for P8); shape8 flips to passing by dropping its xfail when the offset-alias fix lands.
- **Gap list = one OPTIONAL ≤ 1 h harness extension (non-blocking); otherwise NONE.** Proceed to Day 1 on the existing tooling.

### Verification

```bash
# Readiness audit doc exists
test -f docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md && echo "audit present"

# The tools are present on main (including the Sprint-29 --resolve-changed mode)
for t in scripts/diagnostics/kkt_residual.py scripts/diagnostics/check_presolve_divergence.py scripts/sprint_audit/check_golden_staleness.py scripts/sprint_audit/changed_emit_artifacts.py; do test -f "$t" && echo "✓ $t" || echo "✗ $t"; done

# Harness runs on robert + mine (head-offset dual-transfer self-check)
for m in robert mine; do .venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/$m.gms 2>&1 | grep -iE "dual transfer"; done

# Gap list present (extensions or "none needed")
grep -qiE "gap list|no extensions needed|Day-0 extension" docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md && echo "gap list present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md` — per-tool readiness verdict for the Sprint-30 classes (head-offset dual-transfer, widened-VARIABLE re-solve coverage, property-catalog extensibility, allowlist currency)
- A scoped gap list (Day-0 extensions ≤ 1h each) or "no extensions needed"
- Confirmation the `--resolve-changed` checkpoint covers the Sprint-30 changed-golden set
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.4, 8.1, 8.3, 8.4

### Acceptance Criteria

- [x] TOOLING_READINESS_AUDIT.md created covering the four tools + `--resolve-changed`
- [x] KKT-residual harness dual-transfer validated on robert + mine (head-offset multipliers) — CONSISTENT on both + a scoped OPTIONAL ≤1h extension for per-row localization
- [x] `--resolve-changed` confirmed to cover the widened-VARIABLE + head-offset goldens (`_GOLDEN_SUFFIXES` = both suffixes)
- [x] Property-test catalog confirmed extensible to the new head-offset shape (existing `shape7`/`shape8` offset-alias fixtures noted; `shape8` xfail-strict; run = 7 passed, 1 xfailed)
- [x] Allowlists confirmed current (7 + 1, #1439/#1461 open); divergence detector soft-classifies the Class-B/cold-convex residue
- [x] Gap list produced (one OPTIONAL ≤1h harness extension, non-blocking; otherwise none)
- [x] Unknowns 1.4, 8.1, 8.3, 8.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Backlog Fix-Surface Analysis (#1385 sarf; #1146/#1143/#1112/#1111; Class-B CGE `stat_pz`)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-06
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 30 Day 1
**Owner:** Development team (AD/emit specialist)
**Dependencies:** Tasks 1, 8
**Unknowns Verified:** 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1

### Objective

Produce the Day-0 patch-site hypotheses (PR24) + property-test fixture plan for the Sprint-30 tracks whose diagnosis is *banked but not yet implemented*: the #1385 sarf runtime-guard cross-terms (hand-derived Sprint 29), the offset-alias #1146/#1143 + #1111/#1112 fix (reverted Sprint 29 Day 5), and the Class-B CGE `stat_pz` coefficient discrepancy (harness-localized Sprint 29 Day 12). This is analogous to the Sprint-29 backlog fix-surface task but for the Sprint-30 "banked" set.

### Why This Matters

These three tracks share a property: Sprint 29 *diagnosed* them but did not *implement* them, so their fix surfaces are the highest-value Day-0 hypotheses to re-verify (PR24). The offset-alias fix was reverted (so the coupling with the distance-Jacobian must be understood before re-attempting); the #1385 cross-terms were hand-derived (so the sarf emit site must be pinned); the Class-B `stat_pz` was localized to a coefficient row (so the general-emit patch site must be traced). Getting these patch-site hypotheses + the property-test fixtures right at Day-0 keeps the in-sprint work from re-discovering the Sprint-29 findings.

### Background

- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` (the Sprint-29 template + the offset-alias + objective-mismatch fix-surface hypotheses)
- `docs/issues/ISSUE_1385_*.md` (the banked runtime-guard cross-terms + the sarf target), `docs/issues/ISSUE_{1146,1143}_*.md` (the offset-alias gates + the Day-5 revert), GitHub #1111/#1112 (the AD-engine architecture)
- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` §"Class B" (the `stat_pz` cluster: irscge/lrgcge/moncge/stdcge/marco, confirmed NOT Walras)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (the property-test catalog for the new fixtures)

### What Needs to Be Done

1. **#1385 sarf** — pin the emit site where the runtime-guard equation-body re-emit + the banked `J_gᵀ·lam` cross-terms materialize (`src/kkt/stationarity.py` + `src/ad/index_mapping.py`); record the smallest-target verification (no quoted-set-name multiplier indices; byte-stable golden).
2. **Offset-alias #1146/#1143 + #1111/#1112** — record the Day-5 revert root cause (the offset-image cross-term coupled with the distance-Jacobian), the coordinated-fix hypothesis, and the property-test fixture (the cyclic `i++1` / successor `ord(j)=ord(i)+1` shape); flag the #1111/#1112 architectural-REPLAN boundary.
3. **Class-B CGE `stat_pz`** — trace the general-emit coefficient-discrepancy patch site (the harness-localized `stat_pz` row, confirmed NOT Walras); record whether one fix converts several models (irscge/lrgcge/moncge/stdcge/marco).
4. **Property-test fixture plan** — the new head-domain-offset fixture (from Task 3) that P8 adds to `test_ad_crossterm_shapes.py`, plus enabling the existing `shape8_offset_alias_successor` xfail (and `shape7_offset_alias_cyclic`) once the offset-alias fix lands.

### Changes

**COMPLETE (2026-07-06).** Authored `docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md` — Day-0 patch-site hypotheses (PR24) for the five banked surfaces, grounded in the banked ISSUE docs + fresh Day-0 `kkt_residual.py` runs on the Class-B cluster + the #1449 blast-radius enumeration + the Task-8 property catalog. Updated KNOWN_UNKNOWNS Unknowns 3.3/4.2/5.1/5.3 (INCOMPLETE → verified) + 4.1/5.2/7.1 (Task-9 layer appended) + CHANGELOG Task-9 entry.

### Result

- **#1385 sarf (Part A):** two coupled sites — `src/ad/index_mapping.py` (extend the short-circuit gate from srpchase's **1-D** to sarf's **2-D** dynamic-subset shape) + `src/kkt/stationarity.py` (a **new symbolic runtime-guard cross-term emit** differentiating each body parametrically in `(g,t,m,n)` — the equations enumerate zero instances). Atomic; the banked 6-guarded-term `stat_task` derivation is the target. Instance counts **384 + 648 + 120 = 1,152** → the emit must be **O(constraints), not O(instances)** (the Day-0 tractability gate; REPLAN S31 if it re-triggers the timeout).
- **Offset-alias (Part B):** the Day-5 revert was **polygon** — the objective-gradient cross-term is **coupled** with the `distance(i,j)` **constraint-Jacobian symmetry** (the dropped second-index `r(j)` term); neither alone matches (the fix landed the gradient → regressed to a spurious 0.0). Coordinated fix = the successor-offset cross-term (`derivative_rules.py`) **+** the distance-Jacobian symmetry (`constraint_jacobian.py`). **himmel16 is distinct** (cyclic cross-term *present*; a numeric/objvar-gradient-**sign** defect). The **#1111/#1112** architectural boundary is flagged for Task 6 (REPLAN S31 only if a shape-gate can't make it correct).
- **Class-B `stat_pz` (Part C):** fresh harness — irscge/lrgcge/moncge all `stat_pz` rel **1.00**, CONSISTENT, CASE_B (**not** Walras) → **one general-emit coefficient fix converts all three** (the missing-unit-coefficient fingerprint). Surface = the `pz`-cross-term Jacobian-transpose coefficient in `src/kkt/stationarity.py` / `src/ad/constraint_jacobian.py`. Genuine-floor.
- **hhfair widened-VAR (Part D):** the #1449 widened-**parameter** presolve cohort = **4 models** (cclinpts/chain/otpop/rocket); the widened-**VARIABLE** fix (companion variable + value-coupling for the live nonlinear-stat coefficient `n`) is a **disjoint additive path** → blast-radius-safe (the 4 goldens stay byte-identical; only hhfair changes).
- **Property fixtures (Part E):** the head-domain-offset fixture is the one missing shape (a clean one-file add for P8); `shape8` flips from xfail-strict to passing when the polygon coordinated fix lands; `shape7` (himmel16 structural) gains a numeric assertion when the objvar-sign fix lands.

### Verification

```bash
# Backlog fix-surface analysis doc exists
test -f docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "analysis present"

# The three banked tracks referenced
grep -qiE "#1385|sarf" docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && grep -qiE "#1146|#1143|offset-alias" docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && grep -qi "stat_pz" docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "3 tracks present"

# Property-test fixture plan + the Day-5 revert coupling recorded
grep -qiE "property.test|fixture|test_ad_crossterm_shapes" docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && grep -qiE "distance-Jacobian|revert|coupl" docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md && echo "fixture plan + coupling present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md` — the #1385 sarf emit site, the offset-alias coordinated-fix hypothesis + Day-5 revert root cause, the Class-B CGE `stat_pz` patch site, and the property-test fixture plan
- The #1111/#1112 architectural-REPLAN boundary flagged for the Task-6 assessment
- The new head-offset property-test fixture scoped for P8, plus the plan to enable the existing `shape7`/`shape8` offset-alias xfail
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1

### Acceptance Criteria

- [x] BACKLOG_FIX_SURFACE_ANALYSIS.md created
- [x] All three banked tracks referenced (#1385 sarf, #1146/#1143/#1112/#1111 offset-alias, Class-B `stat_pz`)
- [x] Each patch-site framed as a Day-0 hypothesis (PR24), not fact
- [x] The offset-alias Day-5 revert coupling (distance-Jacobian) recorded + the coordinated-fix hypothesis
- [x] Property-test fixture plan present (new head-offset fixture + enabling the existing `shape7`/`shape8` offset-alias fixtures)
- [x] The #1111/#1112 architectural-REPLAN boundary flagged
- [x] Unknowns 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 7.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 30 Detailed Schedule

**Status:** ✅ COMPLETE
**Completed:** 2026-07-06
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 30 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–9

### Objective

Produce the detailed 14-day Sprint 30 schedule (Day 0 setup + Days 1–13 execution) with day-by-day execution prompts, consuming all prep outputs (the Known Unknowns, the baseline, the head-offset design, the forcing survey, the Phase-0 gates, the REPLAN assessment, the camcge design, the tooling audit, the backlog analysis), and respecting the ≤ 12 hours/day budget from the PROJECT_PLAN.md Sprint 30 entry.

### Why This Matters

This is the terminal task — the schedule is only trustworthy once the deep-track designs (Task 3 head-offset, Task 4 forcing, Task 7 camcge) and the REPLAN assessment (Task 6) are done, because they size the REPLAN-prone priorities and set the fallback ordering. The schedule must front-load P1 — **but per the Task-3 correction (Unknown 1.1 returned ❌ WRONG: robert does NOT generalize to mine), P1 splits into two independent tracks**: **P1a robert**, a *decoupled* objective-gradient boundary-term genuine-floor fix (early, standalone, no REPLAN branch), and **P1b mine**, the REPLAN-prone head-offset architecture (mid-sprint). It must also embed the Day-5/Day-10 checkpoint re-solve (the Sprint-29 `--resolve-changed` gate), and place the REPLAN decision points (mine head-offset architecture, rocket forcing, camcge empirical) where the Task-6 assessment says.

### Background

- `docs/planning/EPIC_4/SPRINT_29/PLAN.md` + `docs/planning/EPIC_4/SPRINT_29/prompts/PLAN_PROMPTS.md` (the day-by-day schedule + prompt template)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30" (the 8 priorities + the ≤12h/day budget + the heaviest-day note)
- All Task 1–9 prep outputs (the schedule consumes them)

### What Needs to Be Done

1. **Sequence the 8 priorities across Days 1–13** — front-load P1 per the **Task-3 split** (Unknown 1.1 refuted — robert does NOT generalize to mine): **P1a robert** (a decoupled objective-gradient genuine-floor fix) first, then **P1b mine** (the head-offset architecture) mid-sprint; interleave P2 (rocket forcing) and P3 (hhfair `$184`) early (both feed the Solve target), place P4/P5/P7 (banked cross-terms) mid-sprint, P6 (camcge Epic-5) and P8 (infrastructure) as they fit; respect ≤ 12h/day.
2. **Embed the checkpoint re-solve** at Day 5 + Day 10 using the Sprint-29 `--resolve-changed` gate (so a broken solve surfaces mid-sprint) + the PR25 re-baseline recompute.
3. **Place the REPLAN decision points** (mine head-offset architecture Day ~6–7, rocket-forcing Day ~2–3, camcge-empirical Day ~11) per the Task-6 assessment, each with the fallback the assessment specifies.
4. **Write the day-by-day execution prompts** (`prompts/PLAN_PROMPTS.md`) — one per day, each self-contained with objectives / branch / Phase-0 gate / quality gate / PR + wait-for-review.

### Changes

**COMPLETE (2026-07-06).** Authored `docs/planning/EPIC_4/SPRINT_30/PLAN.md` (Day 0 + Days 1–13 schedule, §1–§19) + `docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md` (14 self-contained day prompts). Updated KNOWN_UNKNOWNS §"Next Steps" → prep phase COMPLETE + GO for Day 0; updated the §Summary Prep-Task→Deliverable Map statuses to ✅ + added the prep-phase-COMPLETE line; CHANGELOG Task-10 entry + Sprint-30-prep-COMPLETE note.

### Result

- **Schedule** (`PLAN.md`): Day 0 traces → **Day 1 P1a robert** (the decoupled, firm objective-gradient genuine-floor +1) → **Days 2–3 P2 rocket** forcing scaffold + REPLAN decision → **Day 4 P3 hhfair** `$184` → **Day 5 Checkpoint 1 + P7 Class-B** start → **Days 6–7 P1b mine** head-offset architecture (REPLAN-gated) → **Day 8 P5 offset-alias** → **Days 9–10 P4 #1385 sarf** + Checkpoint 2 → **Day 11 P6 camcge** Walras (REPLAN-gated) → **Day 12 P7/P8** + REPLAN-slack → **Day 13** final retest + closeout. **~110 h** mid-estimate, **no day > 12 h** (heaviest ~7 h/day in the Days 6–7 mine block); fits the 168 h cap with ≥ 58 h slack.
- **Absorbs the Task-3 P1 split (INVERTED Unknown 1.1):** robert is scheduled Day 1 as a *decoupled* objective-gradient fix (not the head-offset cross-term); the head-offset architecture is mine-only (Days 6–7).
- **Three REPLAN decision points** placed per the Task-6 assessment, each with its firm part + Sprint-31 exit: rocket (Day ~2–3, +1 Solve → Sprint-31 PATH consultation, scaffold firm), mine (Day ~6–7, → Sprint-31 head-offset architecture, robert firm), camcge (Day ~11, → per-model-numéraire declaration, Class-B firm).
- **Checkpoints** at Day 5 + Day 10 (`--resolve-changed` + PR25 re-baseline); Day 13 full 3× `PYTHONHASHSEED` retest.
- **Honest projection:** Solve ≥ 109 (mine + rocket) is the most REPLAN-sensitive KPI; the genuine-floor lift (≥ 72) is robust even under a triple-REPLAN.

### Verification

```bash
# Schedule + prompts exist
test -f docs/planning/EPIC_4/SPRINT_30/PLAN.md && echo "PLAN present"
test -f docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md && echo "PLAN_PROMPTS present"

# Day 0–13 covered
grep -cE "Day [0-9]+" docs/planning/EPIC_4/SPRINT_30/PLAN.md

# Checkpoint re-solve embedded at Day 5 / Day 10
grep -qiE "Day 5.*(checkpoint|resolve-changed)|Checkpoint 1" docs/planning/EPIC_4/SPRINT_30/PLAN.md && grep -qiE "Day 10.*(checkpoint|resolve-changed)|Checkpoint 2" docs/planning/EPIC_4/SPRINT_30/PLAN.md && echo "checkpoints present"

# ≤12h/day budget respected (no day exceeds 12h)
grep -iE "12h|≤ 12|hours/day" docs/planning/EPIC_4/SPRINT_30/PLAN.md | head
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_30/PLAN.md` — the Day 0–13 schedule with per-day objectives, the front-loaded P1 (robert → mine), the embedded checkpoint re-solves, the REPLAN decision points
- `docs/planning/EPIC_4/SPRINT_30/prompts/PLAN_PROMPTS.md` — the day-by-day execution prompts
- Confirmation the schedule fits ≤ 12h/day (< 168h total)

### Acceptance Criteria

- [x] PLAN.md created covering Day 0 + Days 1–13
- [x] The 8 priorities sequenced with P1 front-loaded (robert Day 1 — the decoupled objective-gradient genuine-floor half of the Task-3 split)
- [x] The Day-5/Day-10 checkpoint re-solve (`--resolve-changed`) + PR25 re-baseline embedded
- [x] The three REPLAN decision points placed per the Task-6 assessment with fallbacks
- [x] PLAN_PROMPTS.md created with one self-contained prompt per day (14: Day 0–13)
- [x] ≤ 12h/day budget respected (no day exceeds 12h; ~110 h total < 168 h)

---

## Summary

### Prep Task → Deliverable Map

| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| — | PROJECT_PLAN Sprint 30 insertion | `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30" | ✅ (PR #1489) |
| 1 | Known Unknowns List | `docs/planning/EPIC_4/SPRINT_30/KNOWN_UNKNOWNS.md` | ✅ |
| 2 | Day-0 Baseline + Genuine-Floor Re-Baseline | `docs/planning/EPIC_4/SPRINT_30/BASELINE_METRICS.md` | ✅ |
| 3 | Head-Offset Architecture Design (mine) + robert (found decoupled — objective-gradient, NOT a minimal reproduction of mine) | `docs/planning/EPIC_4/SPRINT_30/HEAD_OFFSET_ARCHITECTURE_DESIGN.md` | ✅ |
| 4 | Non-Convex Forcing Strategy Survey | `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` | ✅ |
| 5 | Refresh + Author Phase 0 Acceptance Gates | `docs/issues/ISSUE_*.md` Phase-0 sections (refreshed) + robert + Class-B gates | ✅ |
| 6 | REPLAN Risk Assessment | `docs/planning/EPIC_4/SPRINT_30/REPLAN_RISK_ASSESSMENT.md` | ✅ |
| 7 | camcge → Epic 5 Walras Transformation Design | `docs/planning/EPIC_4/SPRINT_30/CAMCGE_WALRAS_TRANSFORM_DESIGN.md` | ✅ |
| 8 | Reusable-Tooling Readiness Audit | `docs/planning/EPIC_4/SPRINT_30/TOOLING_READINESS_AUDIT.md` | ✅ |
| 9 | Backlog Fix-Surface Analysis | `docs/planning/EPIC_4/SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md` | ✅ |
| 10 | Sprint 30 Detailed Schedule | `docs/planning/EPIC_4/SPRINT_30/PLAN.md` + `prompts/PLAN_PROMPTS.md` | ✅ |

**Total prep effort ≈ 34–48 h** (~4.5–6 working days).

**✅ Sprint 30 prep phase COMPLETE (Tasks 1–10, 2026-07-06).** All 10 prep tasks landed; all 25 Known Unknowns VERIFIED (3 INVERTED/WRONG, absorbed by the schedule); the 14-day PLAN + day-by-day prompts are authored. **Sprint 30 is GO for Day 0.**

### Verification

```bash
# All prep artifacts present
ls docs/planning/EPIC_4/SPRINT_30/

# Phase-0 gates refreshed on the Sprint 30 tracks
for f in 1443 1462 1236 1385 1146 1143 1330; do grep -l "Phase 0" docs/issues/ISSUE_${f}_*.md 2>/dev/null || echo "MISSING: $f"; done

# Head-offset design + forcing survey + camcge design present (the three deep-track designs)
for d in HEAD_OFFSET_ARCHITECTURE_DESIGN NONCONVEX_FORCING_SURVEY CAMCGE_WALRAS_TRANSFORM_DESIGN; do test -f docs/planning/EPIC_4/SPRINT_30/$d.md && echo "$d ✓"; done

# Schedule fits the budget
grep -Ei 'Day [0-9]' docs/planning/EPIC_4/SPRINT_30/PLAN.md | head -20
```

**✅ All critical items checked — Sprint 30 is ready to begin (GO for Day 0).**

### Success Criteria

This prep plan succeeds if Sprint 30 starts with:

1. **No banked diagnosis taken as fact** — every carryforward fix surface is re-framed as a Day-0 `kkt_residual.py` hypothesis (PR24), so the Sprint-29 hhfair `$141`→`$184` correction cannot recur silently.
2. **A de-risked, correctly-scoped hardest track** — Task 3 established that **P1 splits** (Unknown 1.1 returned WRONG: robert does NOT generalize to mine): **robert** is a *decoupled* objective-gradient boundary-term genuine-floor fix, and **mine** is the head-offset architecture (a concrete 3-site index-map design). The split is known up front, not a mid-sprint discovery.
3. **A chosen forcing lever, not an improvisation** — the non-convex forcing survey (Task 4) picks rocket's lever and sets the nlp2mcp/PATH boundary before implementation.
4. **Planned REPLANs, not surprises** — the three diagnosis-heavy tracks (#1443 multi-site, #1462 forcing, #1330 Epic-5) have explicit PROCEED/REPLAN signals + Sprint 31 exits + budget reallocation (Task 6), with the firm parts (robert / scaffold / Class-B fix) landing regardless.
5. **An implementable Epic-5 transformation** — the camcge Walras design (Task 7) answers the three `CGE_DEGENERACY_SCOPING.md` §5 open questions (detection heuristic, numéraire selection, empirical confirmation) so P6 is an implementation, not a spike.
6. **An honest, re-baselined target** — the genuine floor (69) is carried forward (Task 2), so Sprint 30's Match goal (genuine floor → ≥ 72) is measured on real cold-match transitions, not the methodology-inflated 92.
7. **Reused, not rebuilt, tooling** — the Sprint-29 KKT-residual harness, divergence detector, golden-staleness gate, and `--resolve-changed` checkpoint re-solve are audited ready for the new model classes (Task 8).

**Estimated prep investment:** 4.5–6 days
**Expected benefit:** correctly scopes the multi-site head-offset architecture (the deepest carryforward — mine-only after the Task-3 P1 split, with robert decoupled as a standalone objective-gradient genuine-floor fix), picks a forcing lever for rocket before implementation, turns the paper-verified Walras transformation into an implementable design, and keeps the headline Match honestly attributable — so Sprint 30 spends its budget landing the Sprint-29 REPLAN'd carryforwards rather than re-diagnosing them.

---

## Appendix: Document Cross-References

### Sprint 30 Scope + Goals
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 30 (Weeks 25–26): Sprint 29 Carryforward — Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD" (Priorities 1–8 + pipeline retest + Acceptance Criteria + Estimated Effort + Risk Level)
- `docs/planning/EPIC_4/GOALS.md` (Epic 4: Full GAMSLIB LP/NLP/QCP coverage; Solve Completion + Solution Matching themes)

### Sprint 29 Source Material
- `docs/planning/EPIC_4/SPRINT_29/SPRINT_RETROSPECTIVE.md` (§"Sprint-30 carryforwards" [lines 54–61] — the six carryforward tracks; §"Firm deliverables" — the `_fx_` warm-start / maxmin fix / `--resolve-changed` gate that already landed; the metrics table)
- `docs/planning/EPIC_4/SPRINT_29/SPRINT_LOG.md` (per-day entries; §"Day 2" rocket intrinsic-non-convergence; §"Day 6–7" mine head-offset 3-site trace + REPLAN; §"Day 8" hhfair `$184`; §"Day 9" #1385 banked cross-terms; §"Day 12" robert second-instance + Class-B CGE `stat_pz`; §"Day 13" final PR25 tally + genuine floor 69)
- `docs/planning/EPIC_4/SPRINT_29/REPLAN_RISK_ASSESSMENT.md` (the Track-A/B/C dispositions — the structural template for Task 6)
- `docs/planning/EPIC_4/SPRINT_29/COLD_CONVEX_COHORT_SURVEY.md` (§"Class B" the `stat_pz` cluster; the Case-c residue for Task 4)
- `docs/planning/EPIC_4/SPRINT_29/BASELINE_METRICS.md` (bucket-provenance + genuine-vs-methodology template for Task 2)
- `docs/planning/EPIC_4/SPRINT_29/BACKLOG_FIX_SURFACE_ANALYSIS.md` (the fix-surface template for Task 9)
- `docs/planning/EPIC_4/SPRINT_29/TOOLING_READINESS_AUDIT.md` (the readiness-audit template for Task 8)
- `docs/planning/EPIC_4/SPRINT_29/KNOWN_UNKNOWNS.md` (open-item migration source for Task 1)
- `docs/planning/EPIC_4/SPRINT_29/PREP_PLAN.md` + `PLAN.md` + `prompts/PLAN_PROMPTS.md` (structural templates for Tasks 1–10)
- `docs/planning/EPIC_4/SPRINT_29/PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` (the `--resolve-changed` design reused at the Task-10 checkpoints)

### Carryforward + Backlog Issues (Phase-0 gate targets)
- `docs/issues/ISSUE_1443_*.md` (P1 — mine head-domain-offset MCP infeasibility; records the robert second-instance + the 3-site trace)
- `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (P2 — rocket non-convex forcing; the `_fx_` warm-start landed Sprint 29)
- `docs/issues/ISSUE_1236_*.md` (P3 — hhfair widened-VARIABLE `$184` presolve fix; the Sprint-29 Day-8 blocker correction)
- `docs/issues/ISSUE_1385_*.md` (P4 — translation-timeout Option-1 runtime-guard cross-terms; sarf target; banked hand-derivation)
- `docs/issues/ISSUE_{1146,1143}_*.md` + GitHub #1112 / #1111 (P5 — offset-alias gradient + dollar-condition / alias-aware AD architecture; the Day-5 revert coupling)
- `docs/issues/ISSUE_1330_*.md` + `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (P6 — camcge → Epic 5 Walras drop-row + fix-numéraire transformation)
- The Class-B CGE cohort (irscge / lrgcge / moncge / stdcge / marco) — the P7 `stat_pz` general-emit backlog (confirmed NOT Walras, Sprint 29 Day 12)
- GitHub #1461 (indus cross-platform emit determinism — no local doc; golden-staleness allowlist context for Task 8)

### Related Research / Tooling
- `scripts/diagnostics/kkt_residual.py` (KKT-residual Case-(a/b/c) harness — Tasks 3, 5, 6, 8)
- `scripts/diagnostics/check_presolve_divergence.py` (embedded-NLP-divergence detector — Task 8)
- `scripts/sprint_audit/check_golden_staleness.py` + `scripts/sprint_audit/changed_emit_artifacts.py` + the `--resolve-changed` mode (golden-staleness gate + changed-artifact diff + checkpoint re-solve — Tasks 8, 10)
- `src/emit/emit_gams.py` `_emit_nlp_presolve` + `src/kkt/stationarity.py` (the head-offset emit sites — Task 3) and the widened-symbol #1449 handling (hhfair — Task 5)
- `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (AD cross-term property-test catalog — Tasks 8, 9)
- `docs/research/convexity_detection.md`, `docs/research/CONVEXITY_VERIFICATION_DESIGN.md` (Case-c non-convexity context for the forcing survey — Task 4)

### Process / Tooling
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gate" (PR20 template + PR24/PR25 amendments)
- `data/gamslib/gamslib_status.json` (Sprint 29 final retest DB — Solve 107 / Match 92 / model_infeasible 7; Task 2 baseline source)
- `data/gamslib/mcp/*_mcp.gms`, `*_mcp_presolve.gms` (golden artifacts for the Task-8 / Task-10 checkpoint checks)
