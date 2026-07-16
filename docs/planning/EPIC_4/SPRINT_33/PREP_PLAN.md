# Sprint 33 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 33 begins
**Timeline:** Complete before Sprint 33 Day 1
**Goal:** Set up Sprint 33 for success — land the Sprint 32 Solve/Match/Translate carryforwards the Day-13 closeout REPLAN'd, each of which now carries a **control-confirmed, precisely-pinned root cause** rather than an open question (`docs/planning/EPIC_4/SPRINT_32/SPRINT_RETROSPECTIVE.md` §4). The three deepest carryforwards are now **from-scratch AD/emit workstreams** that Sprint 32 de-risked to a specification: the **mine head-offset bound-active cross-term architecture** (#1443 — Sprint 32 Day 1 confirmed the bound-multiplier `N`-derivation closes `stat_x` *by construction* but yields a wrong-sign residual at **6 bound-active rows**, so the emitted `stat_x` head-offset cross-term is inconsistent at bound-active rows, not a warm-start value); the **sarf symbolic parametric `stat_task` emit subsystem** (#1385 — Sprint 32 Day 6 profiled the timeout to `compute_constraint_jacobian` and confirmed the 2-D constraint gate is *necessary but insufficient*: the **369,024** `task(g,t,mn,mn)` columns enumerate via the scalar `acost3` + the variable path, so the fix must eliminate the 369K-column materialization *everywhere*); and the **#1111/#1112 second-index generalization** (fawley — Sprint 32 Day 11 control-confirmed that `stat_bq`'s qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` second-index restriction the mbal term has; the `/tmp` patch closes `max|stat_bq|` **473 → 18 [96%]** but a residual + the MS-5 LP-convergence remain). Alongside them: the **camcge dual-consistent Walras numéraire** (#1330 → Epic 5 — step 1 landed S32; step 2's numéraire reaches omega 191.7346 but MS-4) and the **rocket + hhfair/CGE Case-c PATH forcing** (#1462/#1236 — the finalized PATH-consultation input is packaged; the Case-c family is documented, forcing-only). Targets: Solve 107 → ≥ 108 (stretch ≥ 110); Match maintain ≥ 92 / genuine floor 74 → ≥ 75; model_infeasible maintain ≤ 7; Translate maintain ≥ 135 (+1 via #1385 sarf → 136); Tests 5,085 → ≥ 5,085+.

**Key Insight from Sprint 32:** Sprint 33 is **specification-bound, not diagnosis-bound** — every carryforward inherits a Sprint-32 *control-confirmed* root cause (not just a pinned location, but a confirmed sign and sufficiency: mine's 6-bound-active-row wrong-sign `N`; sarf's `acost3`-plus-variable-path enumeration; fawley's qsb/pbal `sameas` gap 473→18; camcge's omega-191.7346-but-MS-4 numéraire; rocket's exhausted-lever survey). But two structural lessons from Sprint 32 dominate the prep. (1) **A banked "design" is still a hypothesis that must survive a `/tmp` control before any high-blast-radius `src/` change** — Sprint 32 *REPLAN'd all five* deep tracks after a control refuted the original design premise, with **zero broken code shipped**, and two designs were materially wrong on their *sign/sufficiency*, not just their location (camcge's `nu_mps_fx.l = -mps.m` was a sign error the control corrected to `= mps.m`; mine's `N`-derivation was proven insufficient — an infeasible negative bound multiplier at 6 rows). So the prep-doc `file:line`/sign/sufficiency is a **Day-0-re-confirm hypothesis**, the standing PR24/PR27 lesson. (2) **When every KPI mover is REPLAN-prone and the sprint is "implement against a banked root cause," a flat-KPI outcome is the modal result** — Sprint 32 moved no headline bucket (the Task-9 honest projection borne out exactly); the value was the de-risking, so Sprint 33 prep MUST (a) turn each control-confirmed root cause into a **design the implementation follows** — most critically the P1 mine **bound-active cross-term re-derivation** and the P2 sarf **O(active=398) symbolic emit subsystem**; (b) front-load the **tractability/depth probes** that would re-allocate budget earlier (the P1 cross-term re-derivation depth; the P2 369K→active elimination budget; the P3 second-index gate-leak risk); and (c) keep the PR24/PR27 control-experiment-before-implement gate as the standing discipline on P1/P2/P3/P4/P5.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

> **Note on location.** Sprint 33 is defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33 (Weeks 31–32)". This prep plan is filed under `EPIC_4/SPRINT_33/` alongside the Sprint-30/31/32 prep plans it mirrors.

---

## Executive Summary

Sprint 33 inherits the five Sprint-32 REPLAN'd carryforwards (Priorities 1–5 in `PROJECT_PLAN.md` §"Sprint 33"): the mine head-offset bound-active cross-term architecture (#1443); the sarf symbolic parametric `stat_task` emit subsystem (#1385); the fawley #1111/#1112 second-index generalization; the camcge #1330 dual-consistent Walras numéraire (Epic 5); and the rocket #1462 PATH-consultation submission + hhfair/CGE #1236 Case-c forcing. Priority 6 pulls the residual failure-cohort re-triage (agreste double-`solve` scope, cesam/lnts Case-c) + adjacent emit backlog; Priority 7 (infrastructure) adds the AD cross-term property fixtures the Sprint-32 P1/P2 REPLANs deferred (shape12 head-offset bound-active, shape13 sarf symbolic, fawley second-index), recomputes the PR25 genuine-floor tracking against the re-baselined anchor (74), refreshes the `--resolve-changed` checkpoint targets, and continues the Epic-4 `SUMMARY.md` groundwork.

Sprint 33 resembles Sprint 32 in one structural way: **Sprint 32 diagnosed, control-confirmed, and precisely pinned these tracks; Sprint 33 implements them against a de-risked specification.** Because the root causes are already control-confirmed (the Sprint 32 SPRINT_LOG per-day entries + the per-track banked write-ups — `MINE_5TH_COUPLING_REPLAN.md`, `SARF_TRANSLATE_REPLAN.md`, `P6_BACKLOG_RETRIAGE.md`, `CAMCGE_WALRAS_REPLAN.md`, `ROCKET_PATH_CONSULTATION_INPUT.md`, and `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`), Sprint 33 prep is lighter on *survey* and heavier on **design-before-implement + depth-probe**: the hardest track (P1 mine) needs a concrete **bound-active cross-term re-derivation design** (how the head-offset `stat_x` cross-term `sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)` vanishes consistently at bound-active rows) before any emit change; the second-hardest (P2 sarf) needs the **O(active-instances) symbolic `stat_task` emit-subsystem design** that eliminates the 369K-column materialization in the constraint Jacobian, the variable enumeration, AND the variable stationarity together; and P3 (fawley) needs the **second-index gate-generalization design** (extending the landed #1111/#1112 core from the variable's-first-index shape to the variable's-second-index-summed shape). The Sprint-28–32 diagnostic tooling (KKT-residual harness incl. the new `case_c_objdef` classifier, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` solution-forcing scaffold) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — Sprint 33 Known Unknowns List covering the five carryforward tracks (each a Sprint-32 control-confirmed root cause that remains a Day-0-re-confirm hypothesis, PR24), the three deepest REPLAN-prone from-scratch tracks (P1 mine cross-term architecture, P2 sarf symbolic-emit subsystem, P3 fawley second-index generalization), the cross-term-re-derivation and second-index-gate assumptions, and the camcge Epic-5 numéraire + degeneracy-detector false-positive scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 32 final → Sprint 33 Day 0 per-model bucket provenance, confirming Day-0 = Sprint 32 close (Solve 107, Match 92, genuine floor 74, model_infeasible 7, Translate 135, Tests 5,085, all-219 Match 95) with the committed DB byte-unchanged since the S31 close `4cbf8bff`, and that the PR25 genuine-vs-methodology re-baseline anchor is 74.
3. **mine head-offset bound-active cross-term re-derivation design (Priority 1 foundation)** — turn the Sprint-32 Day-1 control (the wrong-sign `N` at 6 bound-active rows) into a concrete stationarity-consistent cross-term re-derivation, sizing the deepest carryforward BEFORE the schedule is set.
4. **sarf symbolic parametric `stat_task` emit-subsystem design (Priority 2 foundation)** — design the O(active=398) symbolic emit that eliminates the 369K-column materialization everywhere (constraint Jacobian via `acost3`, variable enumeration, variable stationarity) with parametric cross-terms.
5. **fawley #1111/#1112 second-index generalization design (Priority 3 foundation)** — design the second-index gate extension from the variable's-first-index shape (mbal) to the variable's-second-index-summed shape (qsb/pbal), closing the residual + the LP convergence.
6. **camcge dual-consistent Walras numéraire design + degeneracy-detector scope (Priority 4 / Epic 5)** — design the per-model-numéraire declaration + Walras redefinition (omega 191.7346 at MS-1), plus the S1∧S2∧S3 detector scope that must NOT false-flag irscge/lrgcge/moncge/stdcge.
7. **rocket PATH-consultation submission package + hhfair/CGE Case-c forcing plan (Priority 5)** — finalize the submission of the packaged PATH-consultation input to the Sprint-34 consultation + plan the `--force` (homotopy/multistart/optfile) lever survey for the Case-c family.
8. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — refresh/author the gates for the Sprint-33 dispositions (P1 bound-active-row warm→cold residual gate, P2 O(active) emit budget, P3 second-index `/tmp` residual→0 gate, P4 Walras `/tmp` prototype at MS-1, P5 Case-c re-confirm before forcing).
9. **Diagnosis-heavy / REPLAN-prone track risk assessment (PR16)** — apply hypothesis-validation to P1 (deeper cross-term coupling risk), P2 (timeout re-trigger), and P3 (second-index gate-leak); pin explicit Sprint 34/Epic-5 REPLAN exits + budget reallocation.
10. **Reusable-tooling readiness audit + backlog fix-surface analysis (Priorities 6 + 7)** — confirm the Sprint-28–32 tools cover the new Sprint-33 classes (the bound-active cross-term residual test, the sarf symbolic emit path, the second-index property fixture), and analyze the P6 backlog fix-surfaces (agreste/cesam/lnts re-triage; the srpchase/sarf symbolic-emit family) + the P7 property-catalog (shape12/shape13/fawley) + Epic-4-SUMMARY groundwork.
11. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 33 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 33 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 32 → Sprint 33 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine floor |
| 3 | mine Head-Offset Bound-Active Cross-Term: Localization + Re-Derivation Design (Priority 1 foundation) | Critical | 6–8h | Tasks 1, 2 | Priority 1 — mine (Solve) deepest track |
| 4 | sarf Symbolic Parametric `stat_task` Emit-Subsystem Design (Priority 2 foundation) | High | 5–7h | Tasks 1, 2 | Priority 2 — sarf (Translate) 369K elimination |
| 5 | fawley #1111/#1112 Second-Index Cross-Term Generalization Design (Priority 3 foundation) | High | 4–6h | Tasks 1, 2 | Priority 3 — fawley (Solve) second-index gate |
| 6 | camcge Dual-Consistent Walras Numéraire Design + Degeneracy-Detector Scope (Priority 4 / Epic 5) | High | 4–5h | Task 1 | Priority 4 — Epic 5 camcge (Solve) |
| 7 | rocket PATH-Consultation Submission Package + hhfair/CGE Case-c Forcing Plan (Priority 5) | Medium | 2–3h | Task 1 | Priority 5 — rocket hand-off + Case-c forcing |
| 8 | Refresh + Author Phase 0 Acceptance Gates for the Sprint-33 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 1, 3, 4, 5, 6, 7 | Priorities 1–5 — primary scope-correctness gate |
| 9 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 cross-term, P2 sarf timeout, P3 fawley gate-leak; PR16) | High | 3–5h | Tasks 3, 4, 5, 8 | Priorities 1, 2, 3 — REPLAN-prone tracks |
| 10 | Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7) | Medium | 3–4h | Tasks 1, 8 | Priorities 6, 7 — tooling reuse + backlog fix-surfaces |
| 11 | Plan Sprint 33 Detailed Schedule | Critical | 3–4h | Tasks 1–10 | All priorities — sprint planning |

**Total Estimated Time:** 40–56 hours (~5–7 working days)

**Critical Path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11 (the deep-track chain — the mine bound-active cross-term re-derivation design (Task 3) sizes Priority 1 and feeds the Phase-0 gate refresh (Task 8), which feeds the REPLAN assessment (Task 9) and the schedule).
**Secondary Path:** Task 1 → Task 4 → Task 8 → Task 9 → Task 11 (the sarf symbolic-emit subsystem design feeds the P2 gate + the timeout-re-trigger REPLAN assessment → schedule).
**Tertiary Path:** Task 1 → Task 5 → Task 8 → Task 9 → Task 11 (the fawley second-index generalization design feeds the P3 gate + the gate-leak REPLAN assessment → schedule).
**Quaternary Path:** Task 1 → Task 10 → Task 11 (tooling readiness + backlog fix-surface analysis → schedule).
**Parallelizable:** Tasks 1 + 2 (independent); Tasks 3 + 4 + 5 + 6 + 7 (independent after Tasks 1/2); Task 10 follows Task 8; Tasks 3/4/5/6/7 gate the Phase-0 refresh (Task 8).

---

## Task 1: Create Sprint 33 Known Unknowns List

**Status:** ✅ COMPLETE
**Completed:** 2026-07-15
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` cataloguing every assumption and open question across the five carryforward tracks (P1–P5) plus the P6/P7 backlog + infrastructure, so no Sprint-32-style late surprise (or wrong-sign banked design) survives to Day 5.

### Why This Matters

The standing PR24/PR27 lesson, reaffirmed five times in Sprint 32: **a banked, control-confirmed root cause is still a Day-0-re-confirm hypothesis** — including its *sign* and *sufficiency*, not just its location. Sprint 32 REPLAN'd all five deep tracks on control evidence and corrected two materially-wrong banked designs (camcge's `-mps.m` sign; mine's `N`-derivation sufficiency). A Known Unknowns list turns each carryforward's residual assumptions into an explicit, verifiable pre-Day-1 checklist.

### Background

Sprint 33's carryforwards each arrive with a control-confirmed diagnosis but an *un-built* fix (see `PROJECT_PLAN.md` §"Sprint 33" + `SPRINT_32/SPRINT_RETROSPECTIVE.md` §4). The deepest three (P1 cross-term architecture, P2 symbolic-emit subsystem, P3 second-index generalization) are from-scratch AD/emit workstreams whose *implementation shape* is still open even though the *defect* is pinned. Mirror the Sprint-32 Known Unknowns structure (`SPRINT_32/KNOWN_UNKNOWNS.md`).

### What Needs to Be Done

1. **Review the Sprint 33 scope** from `PROJECT_PLAN.md` §"Sprint 33" (Priorities 1–7) + `SPRINT_32/SPRINT_RETROSPECTIVE.md` §4 carryforwards.
2. **Enumerate unknowns per category** (assumption · how-to-verify · priority · risk-if-wrong · verification deadline):
   - **Category 1 — mine head-offset bound-active cross-term (#1443):** Is the wrong-sign `N` fully explained by the head-offset cross-term (vs a deeper coupling)? Does the re-derived cross-term vanish at *all 6* bound-active rows without perturbing interior rows? Does the S31 IR foundation (`EquationDef.head_domain_offsets`) carry the shifted-label pairing needed? Is the `x.up=inf` measurement BANNED (assert `modelstat`)?
   - **Category 2 — sarf symbolic `stat_task` (#1385):** Does eliminating the 369K-column materialization in `compute_constraint_jacobian` alone suffice, or must the variable-enumeration + variable-stationarity paths change atomically? Is the banked 7-term `stat_task` derivation complete? Will the parametric cross-terms stay O(active=398)? Any set-name-literal multiplier indices left?
   - **Category 3 — fawley second-index (#1111/#1112):** Does the second-index gate generalize cleanly from the variable's-first-index (mbal) to the variable's-second-index-summed (qsb/pbal) shape? Does the `/tmp` `$(sameas(cfq__,cf))` patch close the residual 18.47 (beyond 96%)? Does the extended gate regress polygon/ps2 (already covered)?
   - **Category 4 — camcge Walras numéraire (#1330 / Epic 5):** Does the per-model-numéraire + dual-consistent Walras redefinition reach MS-1 at omega 191.7346 in a `/tmp` prototype? Does the S1∧S2∧S3 detector false-flag irscge/lrgcge/moncge/stdcge? Is this in-scope for Sprint 33 or Epic-5-deferred?
   - **Category 5 — rocket / Case-c forcing (#1462/#1236):** Is the packaged PATH-consultation input complete for Sprint-34 submission? Does any `--force` lever (homotopy/multistart/optfile) cross for rocket or the hhfair/CGE family? Is the sign flip still BANNED for Case-c?
   - **Category 6 — P6 failure-cohort + P7 infrastructure:** Is agreste genuinely CASE_B or a double-`solve` scope artifact? Are cesam/lnts confirmed Case-c? Do the shape12/shape13/fawley property fixtures fail-before/pass-after only once P1/P2/P3 land?
3. **Prioritize** by risk (Critical: wrong assumption breaks the fix; High: significant rework; Medium/Low: minor).
4. **Assign a verification method + deadline** (Day 0 / Day 1 / Day N) to every Critical/High unknown.
5. **Write** `KNOWN_UNKNOWNS.md` with the update template + priority definitions.

### Changes

Created `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` with 27 unknowns across the 7 carryforward/backlog/infrastructure categories, each with priority, assumption, research questions, verification method, risk-if-wrong, research-time, owner, and a `🔍 Status: INCOMPLETE` verification stub; plus the Task-to-Unknown mapping appendix and the "Unknowns Verified" metadata on Tasks 2–10 below.

### Result

27 unknowns (Critical 7 / High 11 / Medium 7 / Low 2; ~34h research) covering the five carryforward tracks (P1–P5) + the P6 failure-cohort + P7 infrastructure. Every prep Task 2–10 is mapped to the specific unknowns it verifies.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md && echo "file exists"
# 27 unknowns (>= 25 target) — headings are '## Unknown N.M:'
grep -cE '^## Unknown [0-9]+\.[0-9]+:' docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md
# all 7 categories present — headings are '# Category N:'
grep -cE '^# Category [0-9]:' docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md
# every unknown carries a Verification Results section (27 + 1 template = 28; the Status value fills in ✅/🟡 as prep Tasks 2–10 verify — do not assume all INCOMPLETE)
grep -cE '^### Verification Results$' docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/KNOWN_UNKNOWNS.md` with 27 unknowns across 7 categories (one per carryforward track + P6 + P7)
- Each unknown: assumption · verification method · priority · risk-if-wrong · verification deadline
- Update template + priority definitions + a "newly discovered" section

### Acceptance Criteria

- [x] Document created with 27 unknowns across the 7 categories
- [x] All unknowns have assumption, verification method, priority, risk-if-wrong
- [x] All Critical/High unknowns have a verification deadline (Day 0/1/N)
- [x] The two Sprint-32 wrong-design lessons (sign, sufficiency) are represented as explicit unknowns for P1/P3
- [x] Update template + priority definitions included
- [x] Cross-referenced to `PROJECT_PLAN.md` §"Sprint 33" and the banked REPLAN docs

---

## Task 2: Sprint 32 → Sprint 33 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-16
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Sprint planning
**Dependencies:** None (parallelizable with Task 1)
**Unknowns Verified:** 1.1, 3.1, 7.2

### Objective

Establish the Sprint 33 Day-0 baseline with per-model bucket provenance, confirm it equals the Sprint 32 close, and re-affirm the PR25 genuine-vs-methodology floor anchor (74) that Sprint 33's Match/genuine-floor targets ramp from.

### Why This Matters

Sprint 32's headline result was that **no bucket moved** and the committed DB is byte-unchanged since the S31 close `4cbf8bff`. Sprint 33's acceptance criteria (Solve ≥ 108, genuine floor ≥ 75, Translate +1 → 136) are all *deltas off this exact baseline*; a misremembered Day-0 (or a stale DB) would mis-measure every mover. PR15 (bucket provenance) + PR17 (Day-0 confirmation) + PR25 (genuine-vs-methodology) are the standing baseline disciplines.

### Background

Sprint 32 final (142 corpus): Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine floor 74 · model_infeasible 7 · Tests 5,085 · determinism ✅ ×3 {0,1,42}; all-219 Match 95. The genuine-floor ramp re-baselines to **74** at S33 open (footnote ⁸). See `SPRINT_32/BASELINE_METRICS.md` and `SUMMARY.md` (row 32).

### What Needs to Be Done

1. **Confirm the Day-0 git anchor** — verify `git diff --quiet ee51ed9e..HEAD -- src/ scripts/` is empty (no drift since the S32 close `ee51ed9e`), and that `git diff --quiet 4cbf8bff..HEAD -- data/gamslib/gamslib_status.json` is empty (the committed DB is byte-unchanged since `4cbf8bff` — comparing against the anchor commit, not just hashing the working-tree file; optionally print the current hash with `md5 -q` / `md5sum`).
2. **Re-run the pipeline tally** on the 142 convex-candidate corpus (`--only-parse` fast pass + the full-status DB read) and confirm the buckets: Parse 142 / Translate 135 / Solve 107 / Match 92 / model_infeasible 7 / path_syntax_error 8 / path_solve_license 9 / path_solve_terminated 4 / non-translate 7.
3. **Record per-model bucket provenance** (PR15) for the models each carryforward touches (mine, sarf, fawley, camcge, rocket, hhfair/irscge/lrgcge/moncge, agreste, cesam, lnts) — Day-0 bucket + expected Day-13 bucket.
4. **Re-affirm the PR25 genuine-floor anchor 74** (cold-emit-correct genuine matches vs presolve-recovered methodology) and record the levers that would move it (mine [P1] / fawley [P3] cold-matches).
5. **Confirm determinism** ×3 `PYTHONHASHSEED` {0,1,42} on the Day-0 emit.
6. **Write** `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md`.

### Changes

Confirmed Day-0 = the Sprint 32 close (`ee51ed9e`): no `src/`/`scripts/` drift since (docs-only PR #1561/#1562), DB byte-unchanged since `4cbf8bff` (md5 `a92b040924d20d693699d1861972780c`) → reused the committed DB, no fresh retest. Recomputed the 142-candidate bucket tally, enumerated every bucket's members by name, reproduced the PR25 genuine-vs-methodology partition (74 genuine + 21 methodology = 95), pinned the per-carryforward-model Day-0 provenance, ran the `--resolve-changed --since-commit ee51ed9e --dry-run` checkpoint (GO, 0 changed), and spot-confirmed determinism ×3. Authored `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md`.

### Result

**Day-0 (142 corpus): Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine floor 74 · model_infeasible 7** (agreste/camcge/cesam/fawley/lnts/mine/rocket) · path_syntax_error 8 · path_solve_license 9 · path_solve_terminated 4 · non-translate 7 · all-219 Match 95. Genuine floor 74 = S30 70 + S31 P2's +4; the → ≥ 75 movers are mine [P1] + fawley [P3] (camcge [P4] Epic-5). Determinism ✅ ×3 {0,1,42}; `--resolve-changed` GO. Verified Unknown 7.2 (✅); 1.1/3.1 Day-0 bucket verified (fix-surface → Tasks 3/5).

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md && echo "baseline doc exists"
# DB byte-unchanged since the 4cbf8bff anchor (compares against the commit, not just a hash)
git diff --quiet 4cbf8bff..HEAD -- data/gamslib/gamslib_status.json && echo "DB byte-unchanged since 4cbf8bff"
md5 -q data/gamslib/gamslib_status.json   # optional: print the current hash (macOS; 'md5sum ...' on Linux)
# no src/scripts drift since the Sprint-32 close ee51ed9e (resolved via git log --grep='SPRINT 32 CLOSED' --format=%H | tail -1)
git diff --quiet ee51ed9e..HEAD -- src/ scripts/ && echo "no src/scripts drift since the S32 close"
# the four headline numbers appear in the baseline doc
grep -E 'Solve.*107|Match.*92|genuine floor.*74|Translate.*135' docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/BASELINE_METRICS.md` with the confirmed Day-0 buckets (142 corpus + all-219 Match 95)
- Per-model bucket provenance table for every carryforward-touched model (Day-0 → expected Day-13)
- The PR25 genuine-floor anchor (74) + the mover levers
- Determinism ×3 confirmation + the resolved Day-0 git anchor SHA
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 3.1, 7.2

### Acceptance Criteria

- [x] Day-0 = Sprint 32 close confirmed (Solve 107 / Match 92 / floor 74 / model_infeasible 7 / Translate 135 / Tests 5,085 / all-219 Match 95)
- [x] `gamslib_status.json` byte-unchanged since `4cbf8bff` verified
- [x] No `src/`/`scripts/` drift since the S32-close anchor
- [x] Per-model provenance recorded for the carryforward-touched models
- [x] PR25 genuine-floor anchor 74 re-affirmed with mover levers identified
- [x] Determinism ✅ ×3 `PYTHONHASHSEED` {0,1,42}
- [x] Unknowns 1.1, 3.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: mine Head-Offset Bound-Active Cross-Term — Localization + Re-Derivation Design (Priority 1 foundation)

**Status:** ✅ COMPLETE
**Completed:** 2026-07-16
**Priority:** Critical
**Estimated Time:** 6–8 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5

### Objective

**Validate or refute** the Sprint-32 banked premise (that the wrong-sign residual at the 6 bound-active rows is a `stat_x` cross-term defect closable by re-deriving the cross-term) and produce the concrete P1 fix design — the head-offset reconciliation fix-surface hypotheses + a pre-`src/` `/tmp` control spec — sizing Sprint 33's deepest (+1 Solve) track before the schedule is set.

### Why This Matters

P1 is the deepest from-scratch AD/emit track and the primary +1 Solve lever. Sprint 32 proved the *previous* fix (the `N`-derivation) insufficient via a `/tmp` control (MS-5 @ 22058, six rows needing an infeasible negative bound multiplier). Without a design that pins *why* the emitted cross-term `sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)` carries the opposite bound's sign at bound-active rows — and *how* the re-derivation fixes it — Sprint 33 Day 1 would re-diagnose instead of implement, risking another mid-sprint REPLAN.

### Background

Sprint 31 landed the head-offset IR foundation (`EquationDef.head_domain_offsets`, per-position `IndexOffset|None` aligned to the domain; the head-offset dual transfer stores `pr.m` at the shifted head label `(k,l+1,i,j)` while `lam_pr` pairs at base `(k,l,i,j)`). Sprint 32 Day 1 REPLAN'd mine: `N = 0` at interior rows but carries the opposite bound's sign at the 6 bound-active rows (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`). The banked write-up is `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`. Most stationarity emit bugs live in `src/kkt/stationarity.py`, not the AD layer. Related research: `docs/research/multidimensional_indexing.md`, `docs/research/nested_subset_indexing_research.md`.

### What Needs to Be Done

1. **Re-confirm the Day-1 control** (Day-0 re-confirm, PR24): re-run the `/tmp` mine control, assert `modelstat` (the `x.up=inf` experiment is BANNED), and reproduce the wrong-sign `N` at the 6 bound-active rows.
2. **Localize the emit site** in `src/kkt/stationarity.py`: identify which builder emits the head-offset `stat_x` cross-term `sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)` (the #1224 parameter-offset path or the `head_domain_offsets` path).
3. **Derive the cross-term from scratch** to test whether the emit is correct: compare the hand-derived stationarity term-for-term against the emit; if it matches, localize the residual to the head-offset boundary and diagnose the reconciliation gap (rather than assume a cross-term term error).
4. **Design the fix** (`file:line` fix-surface as a *hypothesis*) from what the derivation shows: a cross-term correction if the derivation surfaces one, else the head-offset **multiplier-keying / boundary reconciliation** it implies — so `N → 0` at all 6 bound-active rows without perturbing interior rows.
5. **Specify the `/tmp` control** that must pass BEFORE any `src/` change (warm residual → 0 at bound-active rows, then presolve MS-1).
6. **Size the track** honestly (18–24h) and pin the REPLAN exit (a documented deeper-coupling finding if the re-derivation surfaces a further cross-term).
7. **Write** `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md`.

### Changes

Re-confirmed the Day-0 harness control (CASE_B `stat_x(3,1,1)` rel 2.37, dual transfer CONSISTENT); classified the 6 wrong-sign rows + the max as **all on the `c`-boundary** (a sharper localization than the banked doc); localized the emit to `_try_build_param_offset_crossterm` (`src/kkt/stationarity.py:5712`) — NOT the `head_domain_offsets` path; and **hand-derived the cross-term from scratch, finding it term-for-term algebraically correct**. Authored `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md` with the re-derivation, the head-label multiplier-keying fix hypotheses (H1/H2) + the REPLAN exit (H3), the pre-`src/` `/tmp` control spec, and the ~22–24h sizing.

### Result

**The banked "cross-term re-derivation" premise is REFUTED** (Unknowns 1.1/1.2 ❌ WRONG): the emitted `stat_x` cross-term is algebraically correct, so re-deriving it closes nothing. P1's fix is **re-scoped** from a cross-term sign/guard tweak to a **head-offset multiplier-keying reconciliation** (H1 head-label `comp_pr`/`lam_pr`/cross-term via `head_domain_offsets`; H2 `d\c`-ring bound reconciliation), gated by a `/tmp` control, with a deeper-coupling REPLAN exit (H3). Sized ~22–24h (upper half). Unknowns 1.1/1.2 ❌ WRONG (corrected direction recorded), 1.3/1.4/1.5 ✅ VERIFIED. A control-first de-risking win — the wrong banked premise was caught by hand-derivation before any `src/`.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md && echo "design doc exists"
# design names the 6 bound-active rows + the cross-term emit site
grep -cE 'x\(1,3|x\(3,1,2\)|x\(3,2,1\)|x\(4,1,1\)|lam_pr' docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md
# design cites the stationarity emit module (not the AD layer)
grep -c 'stationarity.py' docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md
# a /tmp control + a REPLAN exit are both specified
grep -icE 'modelstat|/tmp control|REPLAN exit' docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/MINE_CROSSTERM_DESIGN.md` with the hand-derived bound-active-row stationarity + the cross-term re-derivation
- The `file:line` fix-surface hypothesis in `src/kkt/stationarity.py`
- The pre-`src/` `/tmp` control spec (warm residual → 0 at bound-active rows, then MS-1)
- The honest 18–24h sizing + the explicit deeper-coupling REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5

### Acceptance Criteria

- [x] The Day-1 control re-confirmed (wrong-sign `N` at the 6 bound-active rows, `modelstat` asserted)
- [x] The head-offset `stat_x` cross-term emit site localized in `src/kkt/stationarity.py`
- [x] The correct bound-active-row stationarity derived by hand
- [x] The re-derivation designed as a `file:line` hypothesis (with sign/guard specifics)
- [x] The pre-`src/` `/tmp` control specified (the `x.up=inf` experiment noted BANNED)
- [x] The track sized (18–24h) with a documented deeper-coupling REPLAN exit
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: sarf Symbolic Parametric `stat_task` Emit-Subsystem Design (Priority 2 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4, 2.5

### Objective

Design the O(active = 398) symbolic parametric `stat_task` emit subsystem that eliminates the 369,024-column materialization *everywhere* it enumerates (the constraint Jacobian via `acost3`, the variable enumeration, and the variable stationarity), so sarf recovers to translate (+1 Translate → 136).

### Why This Matters

Sprint 32 Day 6 proved the extended 2-D constraint gate (`_is_blowup_2d_condition_equation`) is *necessary but insufficient*: with it active, `compute_constraint_jacobian` still times out (> 120s) because the 369K `task(g,t,mn,mn)` columns enumerate via the scalar `acost3` (`sum((g,t,m,n)$taskposs(g,t), oc·task)`) + the variable path, both untouched by the constraint gate. A design that pins *all* the enumeration sites and the single symbolic guarded emit that replaces them is required before Day 1, or the timeout re-triggers mid-sprint (the P2 REPLAN risk).

### Background

The 2-D constraint gate exists and fires sarf-only (the "necessary" half). The banked 7-term `stat_task` derivation + the `task.fx$(not active)=0` handling are in `SPRINT_32/SARF_TRANSLATE_REPLAN.md` and `SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md`. srpchase's 1-D analogue translates in 6.56s (the O(active) target reference). The blow-up profiles to `compute_constraint_jacobian`; the fix touches `src/ad/constraint_jacobian.py` + `src/kkt/stationarity.py`. Research: `docs/research/multidimensional_indexing.md`.

### What Needs to Be Done

1. **Re-profile** the timeout (Day-0 re-confirm) and confirm the three enumeration sites: `compute_constraint_jacobian` (via `acost3`), the variable enumeration, and the variable stationarity for `task(g,t,mn,mn)`.
2. **Design the elimination** of the 369K-column materialization at *each* site — how the active subset (`$taskposs(g,t)`, |active| = 398) replaces the full 369K enumeration in the Jacobian, the variable list, and the stationarity.
3. **Specify the single symbolic guarded emit** `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx$(not active)=0`, with the `J_gᵀ·lam` cross-terms differentiated **once parametrically** (not per-instance) and **no set-name-literal multiplier indices**.
4. **Define the atomicity requirement** — the gate + parametric cross-terms + `task.fx` land together (partial landing re-triggers the timeout).
5. **Define the O(active) budget test** — time `sarf_mcp.gms` against the translate budget (target seconds, srpchase 6.56s reference) + a grep-scan clean of set-name literals + a byte-stable new golden.
6. **Size the track** (20–28h) and pin the timeout-re-trigger REPLAN exit.
7. **Write** `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md && echo "design doc exists"
# design names all three enumeration sites + the active-subset count
grep -icE 'compute_constraint_jacobian|variable enumeration|variable stationarity|369,?024|398|taskposs' docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md
# the atomic-landing requirement + O(active) budget test are specified
grep -icE 'atomic|O\(active|budget|srpchase|6.56' docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` with all three enumeration sites + the O(active) elimination per site
- The single symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` emit spec (7-term derivation) + `task.fx` + parametric cross-terms
- The atomic-landing requirement + the O(active) budget/grep/byte-stable acceptance test
- The 20–28h sizing + the timeout-re-trigger REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 2.5

### Acceptance Criteria

- [ ] The timeout re-profiled and all three 369K enumeration sites named
- [ ] The O(active = 398) elimination designed per site (Jacobian, variable list, stationarity)
- [ ] The single symbolic guarded emit specified (7-term derivation, no set-name literals, parametric cross-terms)
- [ ] The atomic-landing requirement stated
- [ ] The O(active) budget test defined (translate time vs srpchase 6.56s, grep-clean, byte-stable golden)
- [ ] The track sized (20–28h) with a documented timeout-re-trigger REPLAN exit
- [ ] Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: fawley #1111/#1112 Second-Index Cross-Term Generalization Design (Priority 3 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Design the extension of the landed #1111/#1112 second-index gate from the variable's-first-index shape (mbal) to the variable's-second-index-summed shape (qsb/pbal), so `max|stat_bq| → 0` (beyond the 96% the `/tmp` patch reached) and fawley reaches MS-1 at the LP optimum 2899.25 (+1 Solve).

### Why This Matters

P3 is the second firm +1 Solve/genuine-floor lever and the empirical test of the Sprint-32 "#1111/#1112 gate leaks" risk. Sprint 32 Day 11 control-confirmed the root cause: `stat_bq` applies `$(sameas(cfq__,cf))` to the mbal cross-term but not the qsb/pbal terms (over-summing over all `cfq__`); the `/tmp` sameas patch closes 473 → 18 (96%) but a residual (18.47) + the MS-5 LP-convergence remain. The design must pin whether the residual is a second gate-leak or a distinct term, or Day 1 risks a partial fix that still diverges.

### Background

`bq(c,cf)` appears in qsb(cfq,l,s)/pbal(cfq,m) as the #1111/#1112 second-index-transpose shape. The landed core (`_var_at_two_indices_complement` + `_build_complement_index_sum` in `src/kkt/stationarity.py`) covers the variable's-first-index = equation-index shape (mbal, polygon, ps2). The banked write-up is `SPRINT_32/P6_BACKLOG_RETRIAGE.md` §3. Research: `docs/research/nested_subset_indexing_research.md`, `docs/research/multidimensional_indexing.md`.

### What Needs to Be Done

1. **Re-confirm the Day-11 control** (Day-0 re-confirm): re-run the `/tmp` fawley `$(sameas(cfq__,cf))` patch, confirm `max|stat_bq|` 473 → 18 (96%), and localize the residual 18.47 term.
2. **Diagnose the residual** — is the remaining 18.47 a second over-sum (a further gate-leak) or a distinct qsb/pbal term the sameas restriction doesn't reach? Determine whether closing it also fixes the MS-5 LP-convergence.
3. **Design the gate generalization** in `src/kkt/stationarity.py`: extend the second-index gate from the variable's-first-index shape to the variable's-second-index-summed shape, covering qsb/pbal, so `max|stat_bq| → 0`.
4. **Specify the no-regression requirement** — the extended gate must NOT regress polygon/ps2/mbal (already covered); pin the `--resolve-changed --since-commit 4cbf8bff` GO test.
5. **Specify the `/tmp` control** — `max|stat_bq| → 0` + MS-1 at 2899.25 BEFORE any `src/` change.
6. **Size the track** (12–18h) and pin the gate-leak REPLAN exit.
7. **Write** `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md && echo "design doc exists"
# design names the qsb/pbal/mbal terms + the sameas restriction + the residual
grep -icE 'qsb|pbal|mbal|sameas|stat_bq|18.47|2899' docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md
# the no-regression (--resolve-changed) + /tmp control are specified
grep -icE 'resolve-changed|polygon|ps2|/tmp control|MS-1' docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` with the residual-18.47 diagnosis + the gate-generalization design
- The `file:line` fix-surface hypothesis in `src/kkt/stationarity.py` (second-index gate extension)
- The no-regression (`--resolve-changed`) + `/tmp` (`max|stat_bq| → 0`, MS-1 at 2899.25) control specs
- The 12–18h sizing + the gate-leak REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [ ] The Day-11 control re-confirmed (473 → 18, 96%) and the residual 18.47 localized
- [ ] The residual diagnosed (second gate-leak vs distinct term; LP-convergence link)
- [ ] The second-index gate generalization designed as a `file:line` hypothesis
- [ ] The no-regression requirement pinned (polygon/ps2/mbal via `--resolve-changed`)
- [ ] The `/tmp` control specified (`max|stat_bq| → 0`, MS-1 at 2899.25)
- [ ] The track sized (12–18h) with a documented gate-leak REPLAN exit
- [ ] Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: camcge Dual-Consistent Walras Numéraire Design + Degeneracy-Detector Scope (Priority 4 / Epic 5)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–5 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Design the per-model-numéraire declaration + dual-consistent Walras redefinition that reaches MS-1 at omega 191.7346 in a `/tmp` prototype, plus the S1∧S2∧S3 degeneracy-detector scope that flags only camcge (not irscge/lrgcge/moncge/stdcge) — resolving #1330 or empirically Epic-5-scoping it.

### Why This Matters

Sprint 32 landed step 1 (the scalar-`fx` `nu_mps_fx` transfer → `stat_mps` Case-a) but Day 5 confirmed step 2's consumption-weighted numéraire reaches the correct allocation (omega 191.7346) yet stays MS-4 — a residual Walras rank-deficiency on the accounting identities (`gdp`/`depreq`/`hhsaveq`/`gruse`), deeper than a numéraire selection. This is Epic-5-domain CGE work; the design must pin whether the dual-consistent redefinition lands in Sprint 33 or is empirically proven to need the per-model-numéraire fallback (Epic 5).

### Background

Step 2's failure is a rank-deficiency: dropping a redundant market-clearing row is primal-correct but breaks the MCP dual (the Sprint-30/31 finding). The dual-consistent approach keeps every market-clearing row and redefines the redundant market's dual via Walras' law so the reduced system is full-rank while the dual stays available. Banked: `SPRINT_32/CAMCGE_WALRAS_REPLAN.md`, `SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md`, and `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`. Research: `docs/research/convexity_detection.md`.

### What Needs to Be Done

1. **Re-confirm step 2** (Day-0 re-confirm): re-run the numéraire `/tmp` prototype, assert `modelstat`, and reproduce omega 191.7346 at MS-4 with the Walras singularity on the four accounting identities.
2. **Design the per-model-numéraire declaration + Walras redefinition** — keep every market-clearing row; redefine the redundant market's dual via Walras' law so the reduced system is full-rank; specify how the numéraire is declared per-model.
3. **Define the S1∧S2∧S3 detector scope** — the detector must flag only camcge across irscge/lrgcge/moncge/stdcge (no false positives); specify the three conditions.
4. **Specify the `/tmp` prototype gate** — MS-1 at omega 191.7346 (`modelstat` asserted) BEFORE any `src/` change.
5. **Decide the Sprint-33-vs-Epic-5 disposition** — in-scope if the prototype lands at MS-1; otherwise the per-model-numéraire fallback is the documented Epic-5 finding.
6. **Size the track** (10–16h) and pin the Epic-5-deferral REPLAN exit.
7. **Write** `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md && echo "design doc exists"
# design names the numéraire target + the accounting identities + the detector scope
grep -icE '191.7346|gdp|depreq|hhsaveq|gruse|Walras|numéraire|numeraire' docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md
# the detector must not false-flag the four sibling CGE models
grep -icE 'irscge|lrgcge|moncge|stdcge|false.?positive|S1.*S2.*S3' docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/CAMCGE_WALRAS_DESIGN.md` with the per-model-numéraire + dual-consistent Walras redefinition
- The S1∧S2∧S3 detector scope (flags only camcge)
- The `/tmp` prototype gate (MS-1 at omega 191.7346, `modelstat` asserted)
- The Sprint-33-vs-Epic-5 disposition + the 10–16h sizing + the Epic-5-deferral REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [ ] Step 2 re-confirmed (omega 191.7346 at MS-4, Walras singularity on the four identities, `modelstat` asserted)
- [ ] The per-model-numéraire + Walras redefinition designed (full-rank, dual available)
- [ ] The S1∧S2∧S3 detector scope defined (no false-flag on irscge/lrgcge/moncge/stdcge)
- [ ] The `/tmp` prototype gate specified (MS-1 at omega 191.7346)
- [ ] The Sprint-33-vs-Epic-5 disposition decided with an explicit deferral exit
- [ ] The track sized (10–16h)
- [ ] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: rocket PATH-Consultation Submission Package + hhfair/CGE Case-c Forcing Plan (Priority 5)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Task 1
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Finalize the submission of the packaged rocket PATH-consultation input to the Sprint-34 consultation, and plan the `--force` (homotopy/multistart/optfile) lever survey for rocket + the hhfair/CGE Case-c family — the presolve-recovered non-convex models whose only remaining avenue is forcing/reformulation.

### Why This Matters

P5 is the lowest-risk carryforward (the diagnosis is complete) but the hand-off must be clean: rocket's finalized consultation input feeds the Sprint-34 PATH-author consultation, and the Case-c forcing survey is the only remaining lever for the documented non-convex family. Planning the `--force` survey pre-Day-1 avoids re-litigating the (BANNED) sign flip.

### Background

Sprint 32 finalized rocket's PATH-consultation input (Case-c boundary re-confirmed; `--force` scaffold emits; every emittable lever ruled out) in `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (Status: FINALIZED). The hhfair + CGE cluster (irscge/lrgcge/moncge) is auto-classified `case_c_objdef` (ISSUE_1236 CLOSED); the sign flip stays BANNED. The `--force {homotopy,multistart,optfile}` scaffold exists (Sprint 30). Research: `docs/research/convexity_detection.md`, `docs/research/minmax_objective_reformulation.md`.

### What Needs to Be Done

1. **Confirm the rocket package is submission-ready** — the concrete question set + the ruled-out-lever survey + the `--force` scaffold outputs in `ROCKET_PATH_CONSULTATION_INPUT.md`; define the Sprint-34 submission mechanism (what gets handed off, to whom).
2. **Plan the `--force` lever survey** — the homotopy/multistart/optfile passes on rocket + hhfair/irscge/lrgcge/moncge; define what "a lever crosses" means (a recovered +Solve) vs "survey banked for the consultation".
3. **Re-affirm the Case-c gate** — each model's residual must be clean at the NLP point (Case-c) before any forcing (keeps them forcing problems, not latent emit bugs); the sign flip stays BANNED.
4. **Size the track** (8–12h) and note the conditional (not-a-firm-KPI) nature of any +Solve.
5. **Write** `docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md && echo "plan doc exists"
# the submission mechanism + the --force levers + the Case-c gate are specified
grep -icE 'submit|Sprint 34|homotopy|multistart|optfile|--force' docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md
grep -icE 'Case-c|case_c_objdef|sign flip|BANNED|hhfair|irscge|lrgcge|moncge' docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` with the Sprint-34 submission mechanism + the `--force` lever survey plan
- The Case-c re-confirm gate (residual clean at the NLP point before forcing) + the BANNED sign-flip note
- The 8–12h sizing + the conditional +Solve note
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [ ] The rocket PATH-consultation package confirmed submission-ready + the Sprint-34 hand-off mechanism defined
- [ ] The `--force` lever survey planned (homotopy/multistart/optfile on rocket + hhfair/CGE)
- [ ] "Lever crosses" (+Solve) vs "survey banked" criteria defined
- [ ] The Case-c re-confirm gate + BANNED sign flip re-affirmed
- [ ] The track sized (8–12h) with the conditional +Solve noted
- [ ] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Refresh + Author Phase 0 Acceptance Gates for the Sprint-33 Tracks (PR20 + PR24 + PR27)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1, 3, 4, 5, 6, 7
**Unknowns Verified:** 1.1, 2.1, 3.1, 4.1, 5.1

### Objective

Author the Phase 0 acceptance gate for each Sprint-33 track (P1–P5) — the control-experiment-before-`src/` disposition that must pass before any high-blast-radius emit change — consolidating the per-track `/tmp` control specs from Tasks 3–7 into one `PHASE_0_ACCEPTANCE_GATES.md`.

### Why This Matters

The PR20/PR24/PR27 control-experiment-before-implement rule is the single discipline that gave Sprint 32 zero broken code shipped despite five REPLANs. Every Sprint-33 track is REPLAN-prone; a consolidated, hand-derived Phase-0 gate per track (with the exact `/tmp` control, the `modelstat` assertion, and the PROCEED/REPLAN criterion) is the primary scope-correctness safeguard.

### Background

Sprint 32's gates are in `SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md`. The KKT-residual harness Case-(a/b/c) verdict is the PROCEED/REPLAN gate. The standing lessons: assert `modelstat` before reading an objective off a solve; the `x.up=inf` measurement is BANNED (mine); the sign flip is BANNED (Case-c). See `PROJECT_PLAN.md` §"Sprint 33" per-priority Phase-0 gate lines.

### What Needs to Be Done

1. **Consolidate** the per-track `/tmp` control specs from Tasks 3 (mine), 4 (sarf), 5 (fawley), 6 (camcge), 7 (rocket/Case-c) into one gate document.
2. **For each track, author the gate**: the exact `/tmp` control, the pass criterion (P1 warm residual → 0 at bound-active rows then MS-1; P2 O(active) translate budget + grep-clean + byte-stable golden; P3 `max|stat_bq| → 0` + MS-1 at 2899.25; P4 MS-1 at omega 191.7346; P5 Case-c residual clean before forcing), the `modelstat` assertion, and the PROCEED/REPLAN decision.
3. **Encode the standing BANs** (mine `x.up=inf`; Case-c sign flip) as explicit gate conditions.
4. **Encode the emit-touching CI gates** — the golden-staleness check (PR26), the presolve-divergence detector, and the `--resolve-changed` checkpoint re-solve for every `src/`-touching PR.
5. **Write** `docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md && echo "gates doc exists"
# a gate section per track P1-P5 + the modelstat assertion + PROCEED/REPLAN
grep -icE 'mine|sarf|fawley|camcge|rocket' docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md
grep -icE 'modelstat|PROCEED|REPLAN|BANNED' docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md
# the emit-touching CI gates are referenced
grep -icE 'golden-staleness|presolve-divergence|resolve-changed' docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md` with one hand-derived gate per track (P1–P5)
- The `modelstat` assertion + the PROCEED/REPLAN criterion per gate
- The standing BANs (mine `x.up=inf`; Case-c sign flip) as explicit conditions
- The emit-touching CI gate references (golden-staleness, presolve-divergence, `--resolve-changed`)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 2.1, 3.1, 4.1, 5.1

### Acceptance Criteria

- [ ] A Phase-0 gate authored for each of P1–P5 with an exact `/tmp` control + pass criterion
- [ ] Every gate asserts `modelstat` and states a PROCEED/REPLAN decision
- [ ] The mine `x.up=inf` and Case-c sign-flip BANs encoded as gate conditions
- [ ] The emit-touching CI gates (PR26 golden-staleness, presolve-divergence, `--resolve-changed`) referenced
- [ ] Cross-referenced to the per-track design docs (Tasks 3–7)
- [ ] Unknowns 1.1, 2.1, 3.1, 4.1, 5.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 cross-term, P2 sarf timeout, P3 fawley gate-leak; PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 3, 4, 5, 8
**Unknowns Verified:** 1.2, 2.3, 3.3

### Objective

Apply the PR16 hypothesis-validation methodology to the three deepest from-scratch tracks — P1 (deeper cross-term coupling), P2 (timeout re-trigger), P3 (second-index gate-leak) — pinning explicit REPLAN exits, the freed-budget reallocation, and the honest projection of which KPI buckets can actually move.

### Why This Matters

Sprint 32's Task-9 honest projection was borne out exactly: every KPI mover REPLAN'd and the sprint closed flat. Sprint 33's movers are the same class (from-scratch AD/emit). A frank pre-sprint assessment of the REPLAN probability per track, the freed-budget flow (to P6/P7), and the modal (flat-KPI) outcome prevents over-promising and front-loads the deep tracks so REPLANs surface by the Day-5 checkpoint, not Day 11.

### Background

Sprint 32's assessment is in `SPRINT_32/REPLAN_RISK_ASSESSMENT.md`. The control-first discipline (PR24/PR27) refuted five S32 hypotheses before any bad ship. The retrospective §3 lesson: "when every KPI mover is REPLAN-prone and the sprint is 'implement against a banked root cause,' a flat-KPI outcome is the modal result — the value is the de-risking, not the bucket." The `PROJECT_PLAN.md` §"Sprint 33" Risk Level (HIGH) enumerates the P1/P2/P3 from-scratch risks + the explicit REPLAN exits.

### What Needs to Be Done

1. **For each of P1/P2/P3, assess the REPLAN probability** — what control/harness evidence would refute the banked design (P1 the re-derivation surfaces a further coupling; P2 the parametric emit re-triggers the timeout; P3 the second-index gate leaks again), and how early the Day-5 checkpoint surfaces it.
2. **Assess P4 (Epic-5 deferral) and P5 (conditional +Solve)** — the disposition each hands forward.
3. **Pin the REPLAN exits + budget reallocation** — where freed budget flows (P6 failure-cohort re-triage + P7 property fixtures) if a deep track REPLANs early.
4. **Author the honest KPI projection** — which buckets can firmly move (Solve +1 via any one of P1/P3/P4; Translate +1 via P2; genuine floor +1 via P1/P3 cold-match), the stretch (Solve ≥ 110), and the modal flat-KPI outcome.
5. **Recommend the front-load ordering** — the deep tracks (P1, P2) front-loaded so REPLANs surface by Day 5.
6. **Write** `docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md && echo "assessment doc exists"
# each deep track + its REPLAN exit + the freed-budget flow
grep -icE 'P1|P2|P3|REPLAN|freed budget|reallocat' docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md
# the honest KPI projection + the modal flat-KPI outcome
grep -icE 'flat.?KPI|modal|Solve.*108|110|genuine floor|front.?load' docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/REPLAN_RISK_ASSESSMENT.md` with a per-track REPLAN-probability + refutation-evidence assessment (P1/P2/P3)
- The pinned REPLAN exits + freed-budget reallocation (→ P6/P7)
- The honest KPI projection (firm movers, stretch, modal flat-KPI outcome)
- The front-load ordering recommendation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.3, 3.3

### Acceptance Criteria

- [ ] P1/P2/P3 each assessed for REPLAN probability + the refuting control/harness evidence
- [ ] P4 (Epic-5) and P5 (conditional) dispositions assessed
- [ ] REPLAN exits + freed-budget reallocation pinned (→ P6/P7)
- [ ] The honest KPI projection authored (firm movers, stretch ≥ 110, modal flat-KPI)
- [ ] The front-load ordering recommended (deep tracks by Day 5)
- [ ] Unknowns 1.2, 2.3, 3.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 8
**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

### Objective

Confirm the Sprint-28–32 diagnostic tooling covers the new Sprint-33 emit classes, and analyze the P6 failure-cohort fix-surfaces (agreste/cesam/lnts + residual `path_syntax_error`) and the P7 infrastructure scope (shape12/shape13/fawley property fixtures, genuine-floor tracking, Epic-4-SUMMARY continuation).

### Why This Matters

Priorities 6 and 7 fill the 14-day budget and absorb freed budget when a deep track REPLANs. Confirming the tooling is reused (not rebuilt) and pre-analyzing the P6 fix-surfaces + the P7 property-fixture scope means Day-6+ work starts against a plan, not a cold survey — the Sprint-30/31 retro recommendation.

### Background

The reused tooling: the KKT-residual harness (incl. the new `case_c_objdef` classifier), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint re-solve, the `--force` scaffold. The AD cross-term property catalog (`test_ad_crossterm_shapes.py`) needs shape12 (head-offset bound-active, once P1 lands), shape13 (sarf symbolic, once P2 lands), and a fawley second-index fixture (once P3 lands). P6: agreste (CASE_B `stat_sales` rel 2.0, but a double-`solve` scope caveat), cesam (bilinear SAM, likely Case-c), lnts (bilinear-`step`, Case-c). Banked: `SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md`, `SPRINT_32/P6_BACKLOG_RETRIAGE.md`, `SPRINT_32/P7_INFRASTRUCTURE.md`.

### What Needs to Be Done

1. **Audit the reused tooling** — confirm the KKT-residual harness (Case-a/b/c + `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, and the `--force` scaffold cover the new Sprint-33 classes (the bound-active cross-term residual test; the sarf symbolic emit path; the second-index property fixture). Note any gap.
2. **Analyze the P6 fix-surfaces** — agreste (verify the double-`solve` scope before treating it as CASE_B); cesam/lnts (Case-c re-confirm); residual `path_syntax_error` members; the srpchase/sarf symbolic-emit family follow-ons unlocked by P2. Each gated by a `--resolve-changed` GO.
3. **Scope the P7 property fixtures** — shape12 (head-offset bound-active), shape13 (sarf symbolic), fawley second-index — each fail-before/pass-after, landing *only once* P1/P2/P3 land; plus the genuine-floor tracking recompute (anchor 74) + the Epic-4-`SUMMARY.md` continuation (row 33).
4. **Write** `docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "analysis doc exists"
# the reused tools + the P6 cohort + the P7 fixtures are covered
grep -icE 'kkt_residual|case_c_objdef|presolve-divergence|golden-staleness|resolve-changed|--force' docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md
grep -icE 'agreste|cesam|lnts|shape12|shape13|second-index|genuine-floor|SUMMARY' docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap) + the P6 fix-surface + P7 fixture scope
- The agreste double-`solve` scope caveat + the cesam/lnts Case-c re-confirm plan
- The shape12/shape13/fawley property-fixture plan (fail-before/pass-after, gated on P1/P2/P3) + the genuine-floor recompute + Epic-4-SUMMARY continuation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3

### Acceptance Criteria

- [ ] The Sprint-28–32 tooling audited against the new Sprint-33 classes (reuse confirmed, any gap noted)
- [ ] The P6 cohort analyzed (agreste scope caveat, cesam/lnts Case-c, residual path_syntax_error, srpchase/sarf follow-ons)
- [ ] The P7 property fixtures scoped (shape12/shape13/fawley, fail-before/pass-after, gated on landings)
- [ ] The genuine-floor recompute (anchor 74) + Epic-4-SUMMARY row-33 continuation noted
- [ ] Each P6 candidate gated by a `--resolve-changed` GO
- [ ] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 33 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 33 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–10

### Objective

Produce the detailed 14-day Sprint 33 schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts, front-loading the deep tracks (P1, P2) so REPLANs surface by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget.

### Why This Matters

The schedule is the synthesis of all prior prep: the deep-track sizings (Tasks 3–6), the Phase-0 gates (Task 8), and the REPLAN assessment (Task 9). Front-loading the +Solve/+Translate movers (mine, sarf, fawley) so their REPLANs surface early — as Sprint 32's front-load correctly did (mine Day 1, camcge Day 5) — is the single most impactful scheduling decision.

### Background

Sprint 32's schedule + prompts are in `SPRINT_32/PLAN.md` and `SPRINT_32/prompts/`. The per-day workflow: branch → work → quality gate ONLY if `*.py` changed → commit → push → PR → user merges → "checkout main and pull". Checkpoints at Day 5 + Day 10; final retest under ≥ 3 `PYTHONHASHSEED` values. The `PROJECT_PLAN.md` §"Sprint 33" Estimated Effort (86–126h) + the heaviest-day budget (~11h) constrain the layout.

### What Needs to Be Done

1. **Lay out Day 0** — baseline confirmation (Task 2) + the four harness/control re-confirms (mine, sarf, fawley, camcge) + GO/NO-GO for Day 1.
2. **Front-load the deep tracks** — P1 (mine, ~18–24h) + P2 (sarf, ~20–28h) across Days 1–7 so their REPLANs surface by the Day-5 checkpoint; P3 (fawley) + P4 (camcge) mid-sprint; P5 (rocket/Case-c) + P6 (failure-cohort) + P7 (infrastructure) in the back half.
3. **Place the checkpoints** — Day 5 (deep-track PROCEED/REPLAN + freed-budget reallocation) + Day 10; final retest Day 13 (≥ 3 `PYTHONHASHSEED`).
4. **Write the day-by-day prompts** — one per day, pasteable verbatim, each referencing its Phase-0 gate + design doc + REPLAN exit.
5. **Verify the budget** — ≤ 12h/day, ≤ 168h total, heaviest day ~11h; confirm the per-priority sizings sum to 86–126h.
6. **Write** `docs/planning/EPIC_4/SPRINT_33/PLAN.md` + `docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_33/PLAN.md && echo "plan exists"
test -f docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md && echo "prompts exist"
# Day 0 + Days 1-13 all present as prompt headers
grep -cE '^## Day ([0-9]|1[0-3]) Prompt' docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md
# the checkpoints + the deep-track front-load are present
grep -icE 'Day 5|Day 10|checkpoint|front.?load|PYTHONHASHSEED' docs/planning/EPIC_4/SPRINT_33/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_33/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the deep-track front-load, checkpoints, and budget verification
- `docs/planning/EPIC_4/SPRINT_33/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The budget confirmation (≤ 12h/day, ≤ 168h total, 86–126h work-items)

### Acceptance Criteria

- [ ] The 14-day schedule laid out (Day 0 + Days 1–13) with the deep tracks (P1, P2) front-loaded
- [ ] Checkpoints placed (Day 5 PROCEED/REPLAN + freed-budget reallocation, Day 10, final retest Day 13)
- [ ] A pasteable day-by-day prompt authored for every day, each referencing its gate + design doc + REPLAN exit
- [ ] The budget verified (≤ 12h/day, ≤ 168h, 86–126h work-items, heaviest ~11h)
- [ ] Cross-referenced to all prior prep tasks (Tasks 1–10)

---

## Summary: Prep Task Execution Order

**Recommended sequence** (respecting dependencies + the four critical paths):

1. **Tasks 1 + 2 (parallel, Critical)** — Known Unknowns + Day-0 baseline. The foundation everything else re-confirms against.
2. **Tasks 3 + 4 + 5 + 6 + 7 (parallel after 1/2)** — the five per-track design/plan docs (mine cross-term, sarf emit subsystem, fawley second-index, camcge Walras, rocket/Case-c forcing). Tasks 3/4/5 are the deep-track designs on the critical paths.
3. **Task 8 (Critical, after 1/3/4/5/6)** — consolidate the per-track `/tmp` controls into the Phase-0 gates.
4. **Task 9 (High, after 3/4/5/8)** — the REPLAN-prone risk assessment + honest KPI projection.
5. **Task 10 (Medium, after 1/8)** — the tooling-readiness audit + P6/P7 backlog fix-surface analysis.
6. **Task 11 (Critical, after all)** — the detailed 14-day schedule + day-by-day prompts.

### Success Criteria for Sprint 33 Prep

- [ ] All 11 prep tasks complete (or explicitly deferred with rationale)
- [ ] Known Unknowns list identifies ≥ 25 unknowns with verification plans (Task 1)
- [ ] Day-0 baseline confirmed = Sprint 32 close, DB byte-unchanged since `4cbf8bff` (Task 2)
- [ ] Each deep track (P1 mine, P2 sarf, P3 fawley) has a `file:line` design + a pre-`src/` `/tmp` control (Tasks 3, 4, 5)
- [ ] camcge Walras + rocket/Case-c dispositions designed (Tasks 6, 7)
- [ ] A Phase-0 acceptance gate authored per track P1–P5 with `modelstat` + PROCEED/REPLAN (Task 8)
- [ ] The REPLAN-prone risk assessment pins exits + the honest flat-KPI-modal projection (Task 9)
- [ ] The tooling reuse is confirmed + the P6/P7 fix-surfaces analyzed (Task 10)
- [ ] The 14-day schedule + day-by-day prompts front-load the deep tracks with Day-5/10 checkpoints (Task 11)
- [ ] Every design carries an explicit REPLAN exit (the modal outcome is de-risking, not a bucket move)

**Total prep effort:** 40–56 hours (~5–7 working days), front-loaded on the deep-track designs (Tasks 3/4/5) that gate the Phase-0 refresh and the schedule.

---

## Appendix: Document Cross-References

### Sprint 33 definition & epic context
- **`docs/planning/EPIC_4/PROJECT_PLAN.md`** §"Sprint 33 (Weeks 31–32)" (lines ~1549–1620) — the authoritative Sprint 33 Goal / Components (Priorities 1–7) / Deliverables / Acceptance Criteria / Estimated Effort / Risk Level
- **`docs/planning/EPIC_4/GOALS.md`** — Epic 4 goals (full GAMSLIB LP/NLP/QCP coverage; v2.0.0 target)
- **`docs/planning/EPIC_4/SUMMARY.md`** — the Epic-4 sprint-by-sprint summary (row 32 = Sprint 32 close; row 33 to be continued in P7)

### Sprint 32 carryforward provenance (the control-confirmed root causes)
- **`docs/planning/EPIC_4/SPRINT_32/SPRINT_RETROSPECTIVE.md`** §4 — the five carryforwards + the agreste/cesam/lnts backlog
- **`docs/planning/EPIC_4/SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`** — P1 mine wrong-sign `N` at 6 bound-active rows (banked)
- **`docs/planning/EPIC_4/SPRINT_32/SARF_TRANSLATE_REPLAN.md`** + **`SARF_STAT_TASK_SPARSIFICATION_DESIGN.md`** — P2 sarf 369K enumeration (banked)
- **`docs/planning/EPIC_4/SPRINT_32/P6_BACKLOG_RETRIAGE.md`** §3 — P3 fawley qsb/pbal `sameas` gap (473→18) (banked)
- **`docs/planning/EPIC_4/SPRINT_32/CAMCGE_WALRAS_REPLAN.md`** + **`CAMCGE_STAT_MPS_WALRAS_DESIGN.md`** — P4 camcge omega 191.7346 but MS-4 (banked)
- **`docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`** (FINALIZED) — P5 rocket consultation input (banked)
- **`docs/planning/EPIC_4/SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md`** — the `case_c_objdef` classifier (hhfair/CGE, ISSUE_1236)

### Sprint 32 prep artifacts (format + methodology templates for this plan)
- **`docs/planning/EPIC_4/SPRINT_32/PREP_PLAN.md`** — the prep-plan format this document mirrors
- **`docs/planning/EPIC_4/SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md`** — the Phase-0 gate template (Task 8)
- **`docs/planning/EPIC_4/SPRINT_32/REPLAN_RISK_ASSESSMENT.md`** — the REPLAN-assessment template (Task 9)
- **`docs/planning/EPIC_4/SPRINT_32/TOOLING_AND_BACKLOG_ANALYSIS.md`** + **`P7_INFRASTRUCTURE.md`** — the tooling/backlog template (Task 10)
- **`docs/planning/EPIC_4/SPRINT_32/BASELINE_METRICS.md`** — the 142-vs-219 corpus scope + baseline format (Task 2)
- **`docs/planning/EPIC_4/SPRINT_32/PLAN.md`** + **`prompts/`** — the schedule + day-prompt format (Task 11)
- **`docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md`**, **`docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md`** — the original prep-plan format lineage

### Epic 5 (camcge) & research
- **`docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`** — the CGE Walras degeneracy scoping (Task 6)
- **`docs/research/multidimensional_indexing.md`** — multi-dim indexing (sarf 4-D `task`, mine head-offset)
- **`docs/research/nested_subset_indexing_research.md`** — nested/subset indexing (fawley second-index, sarf `$taskposs`)
- **`docs/research/convexity_detection.md`** — non-convexity/Case-c (camcge, hhfair/CGE, rocket)
- **`docs/research/minmax_objective_reformulation.md`** — objective-defining reformulation (Case-c family)

### Key source files (fix-surface hypotheses — verify Day 0, PR24)
- **`src/kkt/stationarity.py`** — the stationarity emit (mine cross-term P1, fawley second-index gate P3; most emit bugs live here, not the AD layer)
- **`src/ad/constraint_jacobian.py`** — the constraint Jacobian (sarf 369K elimination P2)
- **`src/emit/emit_gams.py`** — the presolve warm-start emit (camcge step-1 precedent)
- **`scripts/diagnostics/kkt_residual.py`** — the KKT-residual harness (Case-a/b/c + `case_c_objdef`)
- **`scripts/gamslib/run_full_test.py`** — the pipeline runner (`--resolve-changed --since-commit`)

---

**Document Created:** 2026-07-15
**Owner:** Sprint 33 Planning Team
**Status:** 🔵 Prep NOT STARTED — execute Tasks 1–11 before Sprint 33 Day 1
