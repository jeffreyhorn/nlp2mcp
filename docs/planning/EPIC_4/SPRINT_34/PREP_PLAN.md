# Sprint 34 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 34 begins
**Timeline:** Complete before Sprint 34 Day 1
**Goal:** Set up Sprint 34 for success — land the Sprint 33 REPLAN'd/deferred carryforwards, each of which now carries a **control-confirmed, precisely-characterized diagnosis** rather than an open question (`docs/planning/EPIC_4/SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`). The three deepest are **from-scratch AD/emit workstreams** Sprint 33 de-risked to a specification: the **mine head-offset dual subsystem** (#1443 — Sprint 33 Day 2 *proved* the banked H1 head-label re-keying is **value-invariant** [22→22 nonzero residual rows], so the residual is a deeper head-offset dual-architecture mismatch — the head-placed precedence dual not mapping to `stat_x` at the `c`-boundary, `x.m=0` degeneracy); the **sarf symbolic-emit subsystem** (#1385 — the 369,024-column `task(g,t,mn,mn)` materialization needs a from-scratch symbolic/parametric emit *mode*, since the active 398 = `taskposs∧tech` is not statically enumerable); and the **fawley second-index correction** (#1111/#1112 — the qsb/pbal `sameas` gap is genuine [473→18.468 control-proven] but the fix surface is a constraint-index diagonal in the ~1400-line general emit function, and fawley's +Solve is **H-b** [non-emit MS-5 divergence → forcing]). Alongside them: the **NEW max-convention bound-transfer-sign track** (the `piL_*/piU_*` warm-start transfers skip correctly-signed multipliers for MAXIMIZE solves — surfaced in both fawley and mine); the **camcge dual-consistent Walras numéraire** (#1330 → Epic 5); and the **rocket PATH-consultation submission** (#1462 → the Sprint-35 consultation). Targets: Solve maintain **108** (stretch ≥ 110 via mine/fawley-forcing/bound-transfer/camcge/ganges); Match maintain ≥ **93** / genuine floor **75 → ≥ 76**; model_infeasible maintain ≤ 7; path_syntax_error maintain ≤ 7; Translate maintain ≥ 135 (+1 via #1385 sarf → 136).

**Key Insight from Sprint 33:** Sprint 34 is **specification-bound, not diagnosis-bound** — but with one sharper lesson than Sprint 33 carried. Sprint 33's control-first discipline (PR24/PR27) *refuted the banked premise on every deep track before any bad ship*: P1 mine's H1 was proven **value-invariant** by a `/tmp` control (not merely "deeper"); P3 fawley reached **H-b** (the MCP diverges MS-5 even with the warm residual fully closed); P2 sarf was Option-B-deferred as a 20–28h from-scratch rebuild. **Zero broken code shipped across 8 execution PRs, and the one genuine bucket move (P6 sample) came from the failure-cohort — the designated best-remaining-shot.** So Sprint 34 prep must (a) turn each Sprint-33 control-confirmed characterization into a **design the implementation follows** — most critically the P1 mine **head-offset dual subsystem** (the reconciliation of head-placed constraint duals into `stat_x` at the boundary) and the P2 sarf **symbolic/parametric emit-mode** subsystem; (b) give the **NEW P4 bound-transfer-sign track** a first-class design (it is the most promising *fresh* +Solve lever — a general gap, not a twice-refuted deep track); and (c) keep the PR24/PR27 control-experiment-before-implement gate as the standing discipline on P1/P2/P3/P4/P5, with the honest **modal-flat-KPI** projection binding (three of Sprint 33's deep tracks moved no bucket).

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

> **Note on location.** Sprint 34 is defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 34 (Weeks 33–34)". This prep plan is filed under `EPIC_4/SPRINT_34/` alongside the Sprint-31/32/33 prep plans it mirrors.

---

## Executive Summary

Sprint 34 inherits the six Sprint-33 REPLAN'd/deferred carryforwards (Priorities 1–5 in `PROJECT_PLAN.md` §"Sprint 34"): the mine head-offset dual subsystem (#1443); the sarf symbolic-emit subsystem (#1385); the fawley #1111/#1112 second-index correction + forcing; the NEW max-convention bound-transfer-sign track; the camcge #1330 dual-consistent Walras numéraire (Epic 5) + the rocket #1462 PATH-consultation submission. Priority 6 pulls the banked failure-cohort (ganges/gangesx `$141/$145/$149`, agreste scope-verify); Priority 7 (infrastructure) adds the property fixtures for the tracks that land (shape12 head-offset, shape13 sarf, fawley second-index — following the Sprint-33 P6 `test_sample_pruned_var_l_init.py` pattern), recomputes the PR25 genuine-floor tracking against the re-baselined anchor (**75**), refreshes the `--resolve-changed` checkpoint targets, and continues the Epic-4 `SUMMARY.md` groundwork (row 34).

Sprint 34 resembles Sprint 33 in one structural way: **Sprint 33 diagnosed, control-confirmed, and precisely characterized these tracks; Sprint 34 implements them against a de-risked specification.** But Sprint 33 went further than a "pinned location" — it *refuted the banked fix hypothesis* on every deep track (mine H1 value-invariant; fawley H-b; sarf a from-scratch rebuild), so Sprint 34 prep is heavier on **design-before-implement** (the fix *shape* is genuinely new work, not a bounded change) and on the **honest KPI projection** (three of Sprint 33's deep tracks moved no bucket — the modal-flat-KPI reality). The hardest track (P1 mine) needs a concrete **head-offset dual-subsystem design** (how head-placed constraint duals reconcile into `stat_x` at the boundary, the 22-row breadth) before any emit change; the second-hardest (P2 sarf) needs the **symbolic/parametric emit-mode design** that stops enumerating `task`'s 369K columns everywhere (constraint Jacobian S1, variable enumeration S2, variable stationarity S3) atomically; P3 (fawley) needs the **constraint-index-diagonal design** + the forcing hand-off (its +Solve is H-b); and the NEW P4 needs the **sign-robust bound-transfer design** + a cohort-wide +Solve survey. The Sprint-28–33 diagnostic tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` scaffold, + the S33 P6 `.l`-init fixture pattern) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — Sprint 34 Known Unknowns List covering the six carryforward tracks (each a Sprint-33 control-confirmed characterization that remains a Day-0-re-confirm hypothesis, PR24), the three deepest REPLAN-prone from-scratch tracks (P1 mine dual subsystem, P2 sarf symbolic-emit, P3 fawley + forcing), the NEW bound-transfer-sign track's cohort scope, and the camcge Epic-5 numéraire + degeneracy-detector false-positive scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 33 final → Sprint 34 Day 0 per-model bucket provenance, confirming Day-0 = Sprint 33 close (Solve 108, Match 93, genuine floor 75, model_infeasible 7, path_syntax_error 7, Translate 135, all-219 Match 96) and that the PR25 genuine-vs-methodology re-baseline anchor is **75**. NB: the DB is no longer byte-unchanged since `4cbf8bff` — the S33 P6 sample fix changed `sample_mcp.gms` + the DB; the Day-0 code anchor is the **S33-close SHA**.
3. **mine head-offset dual subsystem design (Priority 1 foundation)** — turn the Sprint-33 Day-2 control (H1 value-invariant; the 22-row `c`-boundary dual-architecture mismatch) into a concrete head-offset dual-reconciliation design, sizing the deepest carryforward BEFORE the schedule is set.
4. **sarf symbolic/parametric emit-mode design (Priority 2 foundation)** — design the symbolic emit mode that stops enumerating `task`'s 369K columns at all three sites (S1 `acost3` body-diff, S2 variable enumeration, S3 variable stationarity) atomically, letting GAMS instantiate the 398 live rows.
5. **fawley second-index correction + forcing design (Priority 3 foundation)** — design the constraint-index-diagonal `sameas` extension (the genuine cross-term correction) + the forcing hand-off for the H-b +Solve.
6. **max-convention bound-transfer-sign track design (Priority 4 — NEW)** — design the sign-robust `piL_*/piU_*` transfer + the MAXIMIZE-cohort +Solve survey (which max models' divergence is warm-residual-driven vs structural).
7. **camcge dual-consistent Walras numéraire design (Epic 5) + rocket PATH-consultation submission plan (Priority 5)** — the per-model-numéraire + Walras redefinition to MS-1 (the Epic-5 `/tmp` gate) + the rocket input submission to the Sprint-35 consultation.
8. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — author the gates for the Sprint-34 dispositions (P1 dual-subsystem warm-residual→0, P2 O(active) emit budget, P3 `max|stat_bq|→0` + the H-b forcing branch, P4 sign-robust warm-residual→0, P5 Walras `/tmp` at MS-1).
9. **Diagnosis-heavy / REPLAN-prone track risk assessment (PR16)** — apply hypothesis-validation to P1 (deeper dual-architecture risk), P2 (timeout re-trigger), P3 (gate-leak / H-b) + the NEW P4; pin explicit Sprint 35/Epic-5 REPLAN exits + budget reallocation + the honest modal-flat-KPI projection.
10. **Reusable-tooling readiness audit + backlog fix-surface analysis (Priorities 6 + 7)** — confirm the Sprint-28–33 tools cover the new Sprint-34 classes, and analyze the P6 backlog fix-surfaces (ganges/gangesx `$141/$145/$149`, agreste scope-verify) + the P7 property-catalog + Epic-4-SUMMARY groundwork.
11. **Sprint planning** — detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the PROJECT_PLAN.md Sprint 34 entry.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 34 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 33 → Sprint 34 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine floor |
| 3 | mine Head-Offset Dual Subsystem: Design (Priority 1 foundation) | Critical | 6–8h | Tasks 1, 2 | Priority 1 — mine (Solve) deepest track |
| 4 | sarf Symbolic/Parametric `stat_task` Emit-Mode Design (Priority 2 foundation) | High | 5–7h | Tasks 1, 2 | Priority 2 — sarf (Translate) 369K elimination |
| 5 | fawley Second-Index Correction + Forcing Design (Priority 3 foundation) | High | 4–6h | Tasks 1, 2 | Priority 3 — fawley (Solve/floor) + forcing |
| 6 | Max-Convention Bound-Transfer-Sign Track Design (Priority 4 — NEW) | High | 4–6h | Tasks 1, 2 | Priority 4 — the fresh +Solve lever |
| 7 | camcge Dual-Consistent Walras Numéraire Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5) | Medium | 3–4h | Task 1 | Priority 5 — Epic-5 camcge + rocket hand-off |
| 8 | Author Phase 0 Acceptance Gates for the Sprint-34 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 1, 3, 4, 5, 6, 7 | Priorities 1–5 — primary scope-correctness gate |
| 9 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 dual, P2 sarf timeout, P3 fawley gate-leak/H-b, P4 bound-transfer; PR16) | High | 3–5h | Tasks 3, 4, 5, 6, 8 | Priorities 1–4 — REPLAN-prone tracks |
| 10 | Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7) | Medium | 3–4h | Tasks 1, 8 | Priorities 6, 7 — tooling reuse + backlog fix-surfaces |
| 11 | Plan Sprint 34 Detailed Schedule | Critical | 3–4h | Tasks 1–10 | All priorities — sprint planning |

**Total Estimated Time:** 41–57 hours (~5–7 working days)

**Critical Path:** Task 1 → Task 3 → Task 8 → Task 9 → Task 11 (the deep-track chain — the mine head-offset dual-subsystem design (Task 3) sizes Priority 1 and feeds the Phase-0 gates (Task 8), which feed the REPLAN assessment (Task 9) and the schedule (Task 11)). Tasks 4/5/6/7 are parallelizable after Tasks 1/2.

---

## Task 1: Create Sprint 34 Known Unknowns List

**Status:** ✅ COMPLETE
**Completed:** 2026-07-18
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` cataloguing every assumption and open question across the seven categories (the six carryforward tracks P1–P5 — with the NEW bound-transfer track as its own category — plus the P6 backlog + P7 infrastructure), so no Sprint-33-style late surprise (or refuted banked hypothesis) survives to Day 5.

### Why This Matters

The standing PR24/PR27 lesson, reaffirmed on every Sprint-33 deep track: **a banked, control-confirmed characterization is still a Day-0-re-confirm hypothesis.** Sprint 33 *refuted* its banked fix hypotheses before any bad ship — mine's H1 re-keying was proven value-invariant, fawley reached H-b, sarf was deferred as a rebuild. A Known Unknowns list turns each carryforward's residual assumptions into an explicit, verifiable pre-Day-1 checklist and forces the honest modal-flat-KPI projection into the open early.

### Background

Sprint 34's carryforwards each arrive with a Sprint-33 control-confirmed diagnosis but an *un-built* (and, for P1/P3, a *harder-than-a-keying-tweak*) fix (see `PROJECT_PLAN.md` §"Sprint 34" + `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`). The deepest three (P1 head-offset dual, P2 symbolic-emit mode, P3 second-index correction) are from-scratch AD/emit workstreams whose *implementation shape* is genuinely open; the NEW P4 bound-transfer track is the freshest and least-scoped. Mirror the Sprint-33 Known Unknowns structure (`SPRINT_33/KNOWN_UNKNOWNS.md`).

### What Needs to Be Done

1. **Review the Sprint 34 scope** from `PROJECT_PLAN.md` §"Sprint 34" (Priorities 1–7) + `SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34_CARRYFORWARDS.md`.
2. **Enumerate unknowns per category** (assumption · how-to-verify · priority · risk-if-wrong · verification deadline):
   - **Category 1 — mine head-offset dual subsystem (#1443):** Given H1 is value-invariant, what reconciliation of head-placed constraint duals into `stat_x` at the `c`-boundary drives `N→0` at all bound-active rows without perturbing interior rows? Does the S31 `head_domain_offsets` IR carry what the reconciliation needs? Is the 22-row breadth (not 6) fully characterized? Is `x.up=inf` BANNED (assert `modelstat`)?
   - **Category 2 — sarf symbolic/parametric emit mode (#1385):** Can the emit switch `task` to a symbolic mode at all three sites (S1 `acost3` body-diff, S2 enumeration, S3 stationarity) atomically? Is the banked 7-term `stat_task` derivation complete + free of set-name-literal indices? Does the `task.fx$(not active)` + MCP matching yield exactly the 398 live rows? Does the translate drop to seconds (O(active)) not >75s?
   - **Category 3 — fawley second-index correction + forcing (#1111/#1112):** Does the constraint-index-diagonal `sameas` extension close `max|stat_bq|→0` without regressing mbal / the 1-D polygon core? Is the +Solve genuinely H-b (MS-5 persists even with the warm residual closed)? Does the genuine cross-term correction lift the floor (fawley cold-match) even under H-b?
   - **Category 4 — max-convention bound-transfer-sign track (NEW):** Is the sign-robust `= abs(.m)` transfer correct across the MAXIMIZE cohort (no over-transfer on presolve-match models)? Which max models' MCP divergence is warm-residual-driven (a +Solve lever) vs structural (like fawley's H-b)? Does `--resolve-changed` stay GO?
   - **Category 5 — camcge Walras (#1330 / Epic 5) + rocket PATH:** Does the full dual-consistent redefinition reach MS-1 at omega 191.7346 in a `/tmp` prototype (the Epic-5 gate)? Does the S1∧S2∧S3 detector false-flag irscge/lrgcge/moncge/stdcge? Is the rocket PATH-consultation input complete for Sprint-35 submission?
   - **Category 6 — P6 banked failure-cohort:** Do ganges/gangesx share a single `$141/$145/$149` translate-syntax root (distinct from sample's `$140`)? Is agreste genuinely CASE_B or a double-`solve` scope artifact? Is the cohort multi-root (verify per-model)?
   - **Category 7 — P7 infrastructure:** Do the shape12/shape13/fawley property fixtures fail-before/pass-after only once P1/P2/P3 land? Is the PR25 genuine-floor anchor 75 + the Day-0 code anchor the S33-close SHA? What does the Epic-4 `SUMMARY.md` row-34 need?
3. **Prioritize** by risk (Critical / High / Medium / Low).
4. **Assign a verification method + deadline** (Day 0 / Day 1 / Day N) to every Critical/High unknown.
5. **Write** `KNOWN_UNKNOWNS.md` with the update template + priority definitions + a Task-to-Unknown mapping appendix (which prep Task 2–10 verifies which unknowns).

### Changes

Created `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` with 27 unknowns across the 7 categories (Category 1 mine dual subsystem ×5, Category 2 sarf symbolic emit ×5, Category 3 fawley correction + forcing ×4, Category 4 max-convention bound-transfer ×4, Category 5 camcge + rocket ×3, Category 6 failure-cohort ×3, Category 7 infrastructure ×3), each with priority, assumption, research questions, how-to-verify, risk-if-wrong, estimated research time, owner, and a `🔍 Status: INCOMPLETE` verification stub; plus the Confirmed Knowledge section, the update template + priority definitions, the Next Steps section, and the Task-to-Unknown mapping appendix. Added the "Unknowns Verified" metadata to Tasks 2–10 below.

### Result

27 unknowns (Critical 7 / High 11 / Medium 7 / Low 2 — 26/41/26/7%; ~34h research, within the 28–36h target) covering the six carryforward tracks (P1–P5, with the NEW bound-transfer track as Category 4) + the P6 failure-cohort (Category 6) + P7 infrastructure (Category 7). Every prep Task 2–10 is mapped to the specific unknowns it verifies.

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md && echo "file exists"
# 27 unknowns (>= 25 target) — headings are '## Unknown N.M:'
grep -cE '^## Unknown [0-9]+\.[0-9]+:' docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md
# all 7 categories present — headings are '# Category N:'
grep -cE '^# Category [0-9]:' docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md
# every unknown carries a Verification Results section (27 + 1 template = 28; the Status value fills in ✅/🟡 as prep Tasks 2–10 verify — do not assume all INCOMPLETE)
grep -cE '^### Verification Results$' docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/KNOWN_UNKNOWNS.md` with 27 unknowns across 7 categories (one per carryforward track — the NEW bound-transfer track its own category — + P6 + P7)
- Each unknown: assumption · verification method · priority · risk-if-wrong · estimated research time · owner
- Update template + priority definitions + the Task-to-Unknown mapping appendix

### Acceptance Criteria

- [x] Document created with 27 unknowns across the 7 categories
- [x] All unknowns have assumption, verification method, priority, risk-if-wrong
- [x] All Critical/High unknowns have a verification method + research time (planned for verification via prep Tasks 2–10, which are NOT STARTED)
- [x] The Sprint-33 lessons (H1 value-invariant; fawley H-b; the modal-flat-KPI reality) are represented as explicit unknowns for P1/P3
- [x] Update template + priority definitions + Task-to-Unknown mapping included
- [x] Cross-referenced to `PROJECT_PLAN.md` §"Sprint 34" and the Sprint-33 control docs

---

## Task 2: Sprint 33 → Sprint 34 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team
**Dependencies:** None
**Unknowns Verified:** 1.1, 3.1, 7.2

### Objective

Establish the Sprint 34 Day-0 baseline from the committed DB, confirm the per-model bucket provenance, pin the Day-0 **code anchor** (the S33-close SHA) for `--resolve-changed`, and re-confirm the PR25 genuine-vs-methodology partition (genuine floor **75**).

### Why This Matters

Every carryforward's Deliverable is measured as a delta from Day-0. A wrong baseline (or a stale anchor) makes the `--resolve-changed` no-regression gate meaningless and the KPI claims unverifiable. **Unlike Sprint 33, the DB is no longer byte-unchanged since `4cbf8bff`** — the S33 P6 sample fix changed `sample_mcp.gms` + the DB, so the Day-0 anchor must be re-pinned to the S33-close commit.

### Background

Sprint 33 closed at Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / all-219 Match 96 (`SPRINT_33/SPRINT_LOG.md`). The genuine floor advanced 74→75 via the P6 sample genuine cold-emit fix (`BASELINE_METRICS.md` §4 partition, re-anchored to 75). The Day-0 code anchor is the S33-close SHA (the `--resolve-changed` baseline); the DB byte-anchor `4cbf8bff` is now historical (superseded by the S33 sample DB change).

### What Needs to Be Done

1. **Confirm Day-0 = Sprint 33 close** — recompute the 142-candidate buckets from the committed `data/gamslib/gamslib_status.json`: Parse 142, Translate 135, Solve 108 (64 cold + 44 presolve), Match 93, model_infeasible 7, path_syntax_error 7, all-219 Match 96.
2. **Pin the Day-0 code anchor** — record the S33-close SHA (`git log` for the SPRINT_33 close merge); confirm `git diff <S33-close>..HEAD -- src/ scripts/` is empty at prep time (no drift).
3. **Enumerate the bucket members** — the 7 model_infeasible (agreste, camcge, cesam, fawley, lnts, mine, rocket), the 7 path_syntax_error (clearlak, dinam, ganges, gangesx, indus, turkey, turkpow — the S33 8-member cohort minus sample, which recovered to Solve at the S33 close), and the genuine-floor / methodology partition members.
4. **Re-confirm the PR25 partition** — genuine floor **75** / methodology **21** / all-219 Match 96 (per PR25 definition); the genuine-floor → ≥ 76 conversion map (mine [P1] / fawley [P3] cold-match).
5. **Determinism baseline** — confirm the S33 close is deterministic ×3 `PYTHONHASHSEED` (or note the blast radius).
6. **Write** `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md && echo "baseline doc exists"
# the headline numbers appear
grep -icE 'Solve.*108|Match.*93|genuine floor.*75|model_infeasible.*7|Translate.*135|all-219.*96' docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md
# the Day-0 code anchor (S33-close SHA) is recorded
grep -icE 'S33.close|anchor|--resolve-changed' docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` with the 142-corpus Day-0 tally + bucket members
- The Day-0 code anchor (S33-close SHA) for `--resolve-changed`
- The PR25 genuine-vs-methodology partition (genuine floor 75) + the → ≥ 76 conversion map
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 3.1, 7.2

### Acceptance Criteria

- [ ] Day-0 = Sprint 33 close confirmed from the committed DB (Solve 108 / Match 93 / floor 75 / mi 7 / Translate 135 / all-219 96)
- [ ] The Day-0 code anchor (S33-close SHA) recorded; `git diff <anchor>..HEAD -- src/ scripts/` empty at prep time
- [ ] The 7 model_infeasible + the residual path_syntax_error members enumerated
- [ ] The PR25 genuine-floor partition (75) + the → ≥ 76 conversion map recorded
- [ ] Cross-referenced to `SPRINT_33/SPRINT_LOG.md` + `SPRINT_33/BASELINE_METRICS.md`
- [ ] Unknowns 1.1, 3.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: mine Head-Offset Dual Subsystem: Design (Priority 1 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 6–8 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team (KKT/emit specialist)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 1.1, 1.2, 1.3, 1.4, 1.5

### Objective

Turn the Sprint-33 Day-2 control (H1 head-label re-keying is **value-invariant**; the residual is a deeper head-offset dual-architecture mismatch, 22-row breadth) into a concrete **head-offset dual-subsystem design** — how head-placed constraint duals reconcile into `stat_x` at the `c`-boundary so `N→0` at all bound-active rows — with a pre-`src/` `/tmp` control gate and a sizing.

### Why This Matters

P1 mine is the sprint's deepest and highest-REPLAN-prior track — its banked premise was **twice-refuted** (S32 `N`-derivation + S33 H1 value-invariance). Sizing and de-risking the dual-subsystem design BEFORE the schedule is set is what prevents a Day-11 REPLAN; the design is the specification the implementation follows (or REPLANs against, cleanly).

### Background

`kkt_residual.py data/gamslib/raw/mine.gms` → CASE_B `stat_x(3,1,1)` rel 2.37, dual-transfer CONSISTENT. Sprint 33 Day 1 built a validated residual decomposition (`SPRINT_33/DAY1_PROGRESS_NOTES.md`) that reproduces the harness residuals row-for-row; Day 2 proved H1 re-keying is value-invariant (the `l+1`-shifted transfer `lam_pr.l(k,l,i,j)=abs(pr.m(k,l+1,i,j))` already stores the head-label value at the body label, so re-keying reads the same value — 22→22 nonzero rows, `SPRINT_33/DAY2_MINE_REPLAN.md`). At the max row, `x` is bound-active with NLP reduced cost `x.m=0`, the cross-term is structurally correct (−16000), and closing needs +16000 that neither a keying change (banned sign flip) nor a bound multiplier (`x.m=0`) can supply.

### What Needs to Be Done

1. **Re-confirm the Day-0 fingerprint** — `kkt_residual.py mine.gms` (CASE_B, `stat_x(3,1,1)` 2.37, dual CONSISTENT) + re-run the Day-1 residual decomposition (repo-root presolve substrate) to reproduce the 22-row `dbg_N`.
2. **Characterize the dual-architecture mismatch** — from the residual decomposition, precisely state how the head-placed precedence dual `pr.m(k,l+1,i,j)` fails to map into `stat_x` at the `c`-boundary (the +16000-needed vs −16000-supplied gap; the `x.m=0` degeneracy at bound-active rows).
3. **Design the reconciliation hypothesis (H_dual)** — the emit reformulation that makes head-placed constraint duals enter `stat_x` consistently at the boundary (candidate: a boundary-row dual-transfer term keyed on the S31 `head_domain_offsets` IR; or a `stat_x` reformulation that accounts for the head-shifted precedence structure). State the fix surface (`src/kkt/stationarity.py` `_try_build_param_offset_crossterm` + the S31 IR; any `src/ad/…` plumbing) as a **hypothesis**.
4. **Specify the pre-`src/` `/tmp` control** — the reconciliation prototype must drive the warm residual `N→0` at **all** bound-active rows AND unchanged (0) at interior rows (`modelstat` asserted; `x.up=inf` BANNED); then presolve MS-1 @ 17500.
5. **Pin the REPLAN exit (H3)** — if the reconciliation can't close `N→0` without perturbing interior rows or regressing srpchase → a further-deferred head-offset dual architecture; mine stays `model_infeasible`; freed budget → P6/P7.
6. **Size it** (design + `/tmp` control + emit/IR plumbing + regression fixture + determinism).
7. **Write** `docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md && echo "design doc exists"
# the value-invariance + the dual-architecture + the /tmp gate + the REPLAN exit are covered
grep -icE 'value-invariant|dual-architecture|22.row|head_domain_offsets|/tmp|modelstat|REPLAN' docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` with the dual-architecture characterization + the reconciliation hypothesis + the `/tmp` control gate
- The fix surface (as a Day-0-re-confirm hypothesis) + the sizing + the H3 REPLAN exit
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5

### Acceptance Criteria

- [ ] The Day-0 fingerprint re-confirmed + the 22-row residual decomposition reproduced
- [ ] The head-offset dual-architecture mismatch characterized (the +16000/−16000 boundary gap, `x.m=0`)
- [ ] The reconciliation hypothesis (H_dual) stated with a `file:line` fix surface (a hypothesis, PR24)
- [ ] The pre-`src/` `/tmp` control specified (`N→0` at all bound-active rows → MS-1 @ 17500; `modelstat` asserted; `x.up=inf` BANNED)
- [ ] The H3 REPLAN exit pinned; the track sized
- [ ] Cross-referenced to `SPRINT_33/DAY2_MINE_REPLAN.md` + `DAY1_PROGRESS_NOTES.md` + `MINE_CROSSTERM_DESIGN.md`
- [ ] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: sarf Symbolic/Parametric `stat_task` Emit-Mode Design (Priority 2 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team (AD/emit specialist)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 2.1, 2.2, 2.3, 2.4, 2.5

### Objective

Design the symbolic/parametric emit **mode** for `task(g,t,mn,mn)` that stops enumerating its 369,024 columns at all three sites (S1 `acost3` body-diff, S2 variable enumeration, S3 variable stationarity) atomically, emitting one guarded `stat_task$taskposs` + `task.fx` and letting GAMS instantiate the 398 live rows — with the O(active) translate-budget gate.

### Why This Matters

P2 sarf is the +Translate lever (lowest-leverage KPI) but the highest-effort/highest-risk track (the 4×-failed Sprint-26 path). The Sprint-33 Day-6 assessment established there is **no cheap gate** (the active 398 is not statically enumerable); the fix is a from-scratch emit mode. Designing the atomic three-site change + the O(active) gate BEFORE implementation is what avoids the timeout-re-trigger REPLAN.

### Background

`SPRINT_33/DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md`: the blow-up is per-column differentiation of `task`'s 369,024 columns at S1 (`acost3` scalar body-diff, `src/ad/constraint_jacobian.py`), S2 (`enumerate_variable_instances`, `src/ad/index_mapping.py:369`), S3 (variable stationarity, `src/kkt/stationarity.py`). `taskposs` is runtime-computed, so the 398 active is not statically enumerable → emit `stat_task(g,t,m,n)$taskposs(g,t)` (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` and let GAMS instantiate the 398 (head guard + `task.fx` + MCP matching). Atomic (no safe partial).

### What Needs to Be Done

1. **Re-confirm the blow-up** — bounded translate probe (`> 75s` in `compute_constraint_jacobian`); confirm the 2-D gate is absent from `src/`.
2. **Design the symbolic emit mode per site** — S1 the `acost3` parametric body-diff (`+ oc(g,m,n)*nu_acost3` as the guarded term, not 369K entries); S2 the `task` column short-circuit (emit symbolic, not enumerate); S3 the one symbolic guarded `stat_task$taskposs`.
3. **Verify the 7-term `stat_task` derivation** term-for-term against the constraint bodies; confirm no set-name-literal multiplier indices.
4. **Specify the atomicity** — the three sites + the `task.fx` fixing land in one change (a partial = an inconsistent MCP).
5. **Specify the O(active) budget gate** — translate in seconds (srpchase ~2.9s reference); byte-stable golden; determinism ×3; `--resolve-changed` GO.
6. **Pin the REPLAN exit** — the parametric emit re-triggers the timeout (a 4th enumeration site) → re-scope; +Translate deferred.
7. **Write** `docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md && echo "design doc exists"
grep -icE 'S1|S2|S3|acost3|taskposs|task.fx|O\(active|398|atomic|REPLAN' docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/SARF_EMIT_MODE_DESIGN.md` with the three-site symbolic emit mode + the 7-term `stat_task` + the O(active) budget gate + atomicity spec
- The REPLAN exit + the sizing
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4, 2.5

### Acceptance Criteria

- [ ] The blow-up re-confirmed (> 75s in `compute_constraint_jacobian`; 2-D gate absent)
- [ ] The symbolic emit mode designed per site (S1 `acost3` parametric ∂, S2 enumeration short-circuit, S3 one guarded `stat_task$taskposs`)
- [ ] The 7-term derivation verified term-for-term; no set-name-literal indices
- [ ] The atomicity + the O(active) budget gate (translate seconds, byte-stable, det ×3, `--resolve-changed` GO) specified
- [ ] The timeout-re-trigger REPLAN exit pinned; the track sized
- [ ] Cross-referenced to `SPRINT_33/DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md`
- [ ] Unknowns 2.1, 2.2, 2.3, 2.4, 2.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: fawley Second-Index Correction + Forcing Design (Priority 3 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team (KKT/emit specialist)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 3.1, 3.2, 3.3, 3.4

### Objective

Design the constraint-index-diagonal `sameas` extension (the genuine qsb/pbal cross-term correction) in `_add_indexed_jacobian_terms` + the forcing hand-off for the H-b +Solve — with the no-regression gate (no mbal / 1-D-core move).

### Why This Matters

P3 fawley is a **split outcome**: the sameas correction is a genuine emit-correctness fix (control-proven 473→18.468) that lifts the genuine floor if fawley cold-matches, but its +Solve is **H-b** (the MCP diverges MS-5 even with the warm residual closed). Designing both the correction (a high-blast-radius change to the ~1400-line general emit function) and the forcing hand-off BEFORE implementation is what keeps the correctness fix safe and the +Solve honestly scoped.

### Background

`SPRINT_33/DAY4_FAWLEY_CONTROL.md` + `DAY5_FAWLEY_CLOSE.md` + `FAWLEY_SECOND_INDEX_DESIGN.md`: the qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` the mbal term has (control-proven 473→18.468); the fix surface is a constraint-index diagonal in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py`, ~1400 lines, a dozen `sameas` paths), distinct from the 1-D polygon core. sameas + all bound-transfer signs fixed → warm residual → 0 but the MCP still solves MS-5 @ 4399.557 (LP opt 2899.25) → H-b (non-emit divergence).

### What Needs to Be Done

1. **Re-confirm the control** — `max|stat_bq|` 473 → 18.468 with the sameas patch; localize the residual + the H-a/H-b discriminator (Day-4 finding: H-b).
2. **Design the constraint-index-diagonal `sameas`** — how `_add_indexed_jacobian_terms` recognizes the *variable's-second-index = the constraint's-own-index* diagonal (qsb/pbal) and emits `$(sameas(cfq__,cf))`, symmetrically with the mbal first-index shape. State the fix surface.
3. **Specify the no-regression gate** — no mbal-term change; no 1-D polygon/ps2 regression (different path); `--resolve-changed --since-commit <S33-close>` GO.
4. **Design the forcing hand-off** — since the +Solve is H-b, the genuine correction ships (a floor lever if fawley cold-matches) and the +Solve hands to the P5 `--force` survey; specify the boundary between the two.
5. **Pin the REPLAN exit** — the generalization leaks onto mbal / regresses the 1-D core → REPLAN.
6. **Size it** (design + `/tmp` control + the emit change + the fawley second-index fixture + the forcing hand-off).
7. **Write** `docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md && echo "design doc exists"
grep -icE 'sameas|constraint-index|_add_indexed_jacobian_terms|H-b|forcing|no.regression|REPLAN' docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` with the constraint-index-diagonal `sameas` design + the no-regression gate + the forcing hand-off
- The REPLAN exit + the sizing (+ the fawley second-index fixture plan)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3, 3.4

### Acceptance Criteria

- [ ] The control re-confirmed (473 → 18.468; the H-b discriminator)
- [ ] The constraint-index-diagonal `sameas` design stated with a fix surface (a hypothesis, PR24)
- [ ] The no-regression gate specified (no mbal / 1-D-core move; `--resolve-changed` GO)
- [ ] The forcing hand-off for the H-b +Solve designed
- [ ] The gate-leak REPLAN exit pinned; the track sized
- [ ] Cross-referenced to `SPRINT_33/DAY4_FAWLEY_CONTROL.md` + `DAY5_FAWLEY_CLOSE.md`
- [ ] Unknowns 3.1, 3.2, 3.3, 3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Max-Convention Bound-Transfer-Sign Track Design (Priority 4 — NEW)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team (emit specialist)
**Dependencies:** Tasks 1, 2
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Design the sign-robust `piL_*/piU_*` warm-start transfer (the general max-convention fix) + the MAXIMIZE-cohort +Solve survey — determining which max models' MCP divergence is warm-residual-driven (a +Solve lever) vs structural (like fawley's H-b).

### Why This Matters

P4 is the **freshest, least-refuted** lever — a *new* general gap discovered in Sprint 33 (Day 4), not a twice-refuted deep track. It is the most promising candidate for another genuine +Solve because it is a general warm-start-transfer correctness fix that may unlock *any* MAXIMIZE model whose divergence is warm-residual-driven. Scoping the cohort + the regression risk BEFORE implementation is what turns it into an early win (or a documented finding).

### Background

`SPRINT_33/DAY4_FAWLEY_CONTROL.md` §5: the `piL_*/piU_*` warm-start transfers are gated on min-convention `.m > 0` / `.m < 0`; for a **MAXIMIZE** solve they skip the correctly-signed bound multipliers — surfaced in both fawley (`bq.m < 0` at a lower bound → the residual-18.468 cell) and mine (`x.m > 0` upper-bound multipliers). A sign-robust transfer (`= abs(.m)` at the active bound) closes the warm residual (control-proven on fawley).

### What Needs to Be Done

1. **Re-confirm the gap** — locate the min-convention `.m > 0` / `.m < 0` gates in the presolve emit (`src/emit/emit_gams.py` bound-transfer lines); confirm the sign-robust `= abs(.m)` closes the warm residual on fawley + mine (`/tmp` control).
2. **Enumerate the MAXIMIZE cohort** — which corpus models `solve … maximizing …`; of those, which are `model_infeasible` / presolve-recovered (the +Solve candidates) vs already-solving (the regression-risk set).
3. **Design the sign-robust transfer** — the general emit change (drop the min-convention sign gate; `= abs(.m)` at the active bound), gated so it fires only at active bounds (no over-transfer on interior/presolve-match models).
4. **Specify the +Solve survey** — for each MAXIMIZE `model_infeasible` candidate, does the sign-robust transfer close the warm residual AND reach MS-1 (a +Solve, warm-residual-driven) vs stay MS-5 (structural, like fawley's H-b)?
5. **Specify the no-regression gate** — `--resolve-changed --since-commit <S33-close>` GO (no presolve-match cohort regression — the transfer only fires at active bounds).
6. **Pin the REPLAN exit** — the sign-robust transfer over-transfers / regresses the presolve cohort → re-scope; or it recovers no bucket → a documented general-correctness finding.
7. **Write** `docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md && echo "design doc exists"
grep -icE 'max.convention|piL|piU|abs\(|maximize|MAXIMIZE|cohort|warm-residual|structural|REPLAN' docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md` with the sign-robust transfer design + the MAXIMIZE-cohort +Solve survey + the no-regression gate
- The REPLAN exit + the sizing
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [ ] The gap re-confirmed (min-convention gate; `= abs(.m)` closes the warm residual on fawley + mine)
- [ ] The MAXIMIZE cohort enumerated (the +Solve candidates vs the regression-risk set)
- [ ] The sign-robust transfer design stated with a fix surface (a hypothesis, PR24) + the active-bound gating
- [ ] The +Solve survey (warm-residual-driven vs structural) specified
- [ ] The no-regression gate + the REPLAN exit pinned; the track sized
- [ ] Cross-referenced to `SPRINT_33/DAY4_FAWLEY_CONTROL.md` §5
- [ ] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: camcge Dual-Consistent Walras Numéraire Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team (KKT/CGE specialist)
**Dependencies:** Task 1
**Unknowns Verified:** 5.1, 5.2, 5.3

### Objective

Design the camcge per-model-numéraire + dual-consistent Walras redefinition (the Epic-5 `/tmp` gate to MS-1 at omega 191.7346) with the S1∧S2∧S3 degeneracy-detector scope, and plan the rocket PATH-consultation input submission to the Sprint-35 consultation.

### Why This Matters

camcge is Epic-5-deferred (the expected disposition — 3+ sprints of MS-4 variants); the design's value is the Epic-5-ready recipe + the detector that must NOT false-flag the four solving CGE siblings. rocket's input is FINALIZED; the plan defines the clean Sprint-35 hand-off.

### Background

`SPRINT_33/CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`: step 1 (`nu_mps_fx`) landed S32; step 2's numéraire reaches omega 191.7346 but MS-4 (residual Walras rank-deficiency). `ROCKET_CASEC_FORCING_PLAN.md`: the FINALIZED PATH-consultation input (concrete question + ruled-out-lever survey + reproducible case + `--force` scaffold) is submission-ready.

### What Needs to Be Done

1. **Re-confirm camcge MS-4** (DB) + the S1∧S2∧S3 detector cohort (camcge fires; irscge/lrgcge/moncge/stdcge pass-through).
2. **Design the full dual-consistent redefinition** — keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law; the `/tmp`-to-MS-1 prototype is the Epic-5 gate (check the dual side, not just the primal).
3. **Scope the degeneracy detector** — S1∧S2∧S3 flags only camcge (S3 = cold-MCP-singular-at-iter-0, the false-positive guard).
4. **Plan the rocket submission** — package the FINALIZED input + the reproducer + the scaffold as the Sprint-35 consultation brief; define the hand-off mechanism.
5. **Pin the disposition** — camcge Epic-5-deferred (expected); rocket = a Sprint-35 submission.
6. **Write** `docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md && echo "plan doc exists"
grep -icE 'Walras|numéraire|omega 191|MS-4|S1∧S2∧S3|Epic 5|rocket|Sprint-35|consultation' docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/CAMCGE_ROCKET_PLAN.md` with the dual-consistent Walras design (Epic-5 gate) + the detector scope + the rocket submission plan
- The Epic-5-deferral disposition + the Sprint-35 rocket hand-off
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3

### Acceptance Criteria

- [ ] camcge MS-4 re-confirmed + the S1∧S2∧S3 detector cohort (flags only camcge)
- [ ] The full dual-consistent redefinition designed with the `/tmp`-to-MS-1 Epic-5 gate (dual side checked)
- [ ] The rocket PATH-consultation input submission to Sprint 35 planned
- [ ] The Epic-5-deferral disposition pinned
- [ ] Cross-referenced to `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` + `ROCKET_CASEC_FORCING_PLAN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`
- [ ] Unknowns 5.1, 5.2, 5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Author Phase 0 Acceptance Gates for the Sprint-34 Tracks (PR20 + PR24 + PR27)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 3, 4, 5, 6, 7
**Unknowns Verified:** 1.2, 2.2, 3.1, 4.1, 5.1

### Objective

Consolidate the per-track `/tmp` control specs from the Task-3–7 designs into one `PHASE_0_ACCEPTANCE_GATES.md` — one hand-derived gate per track (P1–P5) with the exact control, the pass criterion, the `modelstat` assertion, and the PROCEED/REPLAN decision.

### Why This Matters

The Phase-0 gates are the control-first discipline for the whole sprint — the single most load-bearing prep artifact (Sprint 33 refuted every deep-track premise at these gates *before* any bad ship). One consolidated gate index makes the control-before-`src/` rule easy to reference per track.

### Background

Mirror `SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md`. Each Sprint-34 emit-touching track (P1 mine dual, P2 sarf, P3 fawley, P4 bound-transfer) has a `/tmp`/harness control that must pass before any `src/` change; P5 camcge is an Epic-5 `/tmp` gate (confirm the MS-4 deferral); rocket is a docs submission.

### What Needs to Be Done

1. **Author one gate per track (P1–P5)** — the exact `/tmp` control + the pass criterion + the `modelstat` assertion + the PROCEED/REPLAN decision, carrying each design's disposition (P1 the dual-reconciliation warm-residual→0; P2 the O(active=398) probe; P3 the `max|stat_bq|→0` + the H-b forcing branch; P4 the sign-robust warm-residual→0 + the +Solve survey; P5 the Walras `/tmp` at MS-1 [Epic-5-deferral]).
2. **Encode the standing BANs** — mine `x.up=inf` BANNED; the Case-c objective-gradient sign flip BANNED.
3. **Encode the emit-touching CI gates** — golden-staleness (PR26), presolve-divergence detector, `--resolve-changed --since-commit <S33-close>` checkpoint.
4. **Append Task-8 gate-feasibility notes** to the mapped Known Unknowns (without overwriting the Task-3–7 primary blocks).
5. **Write** `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md && echo "gates doc exists"
# one gate per track P1-P5 + the BANs + the CI gates
grep -icE 'P1|P2|P3|P4|P5|PROCEED|REPLAN|modelstat|x.up=inf|BANNED|--resolve-changed' docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` — one PROCEED/REPLAN gate per track P1–P5 with the `/tmp` control + the pass criterion + the CI gates
- The standing BANs + the Task-8 gate-feasibility notes on the mapped unknowns
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.2, 2.2, 3.1, 4.1, 5.1

### Acceptance Criteria

- [ ] One hand-derived gate per track P1–P5 (control + pass criterion + `modelstat` + PROCEED/REPLAN)
- [ ] The standing BANs encoded (mine `x.up=inf`; the Case-c sign flip)
- [ ] The emit-touching CI gates encoded (golden-staleness, presolve-divergence, `--resolve-changed --since-commit <S33-close>`)
- [ ] Task-8 gate-feasibility notes appended to the mapped unknowns (primary blocks preserved)
- [ ] Cross-referenced to the Task-3–7 design docs + `SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md`
- [ ] Unknowns 1.2, 2.2, 3.1, 4.1, 5.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment (P1 dual, P2 sarf timeout, P3 fawley gate-leak/H-b, P4 bound-transfer; PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–5 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 3, 4, 5, 6, 8
**Unknowns Verified:** 1.5, 2.2, 3.2, 4.2

### Objective

Apply the PR16 hypothesis-validation methodology to the four from-scratch/new tracks — P1 (deeper dual-architecture), P2 (timeout re-trigger), P3 (gate-leak / H-b), P4 (over-transfer / structural) — pinning explicit REPLAN exits, the freed-budget reallocation, and the honest projection of which KPI buckets can actually move.

### Why This Matters

Sprint 33's Task-9 honest projection was borne out exactly (three deep tracks moved no bucket) — but P6 delivered the +1. Sprint 34's movers are the same class, plus the fresh P4 lever. A frank pre-sprint assessment of the REPLAN probability per track + the freed-budget flow + the modal (flat-KPI-plus-maybe-one) outcome prevents over-promising and front-loads the deep tracks so REPLANs surface by Day 5.

### Background

`SPRINT_33/REPLAN_RISK_ASSESSMENT.md` is the template; `SPRINT_33/SPRINT_RETROSPECTIVE.md` §3 the modal-flat-KPI lesson (borne out for the deep tracks, beaten by P6). `PROJECT_PLAN.md` §"Sprint 34" Risk Level (HIGH) enumerates the P1/P2 from-scratch risks + the REPLAN exits.

### What Needs to Be Done

1. **For each of P1/P2/P3/P4, assess the REPLAN probability** — the control/harness evidence that would refute the design (P1 the reconciliation can't close `N→0`; P2 a 4th enumeration site; P3 a gate-leak / the H-b +Solve; P4 over-transfer / all-structural cohort), and how early the Day-5 checkpoint surfaces it. NB: P1 is **High** (banked premise twice-refuted); P4 is the freshest/least-refuted (the best +Solve odds).
2. **Assess P5** (camcge Epic-5 deferral; rocket Sprint-35 submission).
3. **Pin the REPLAN exits + budget reallocation** (→ P6 failure-cohort + P7 fixtures).
4. **Author the honest KPI projection** — the in-sprint Solve movers ({P1 mine, P3-forcing, P4 bound-transfer, P6 ganges/gangesx}); Translate +1 via P2; genuine floor +1 via P1/P3 cold-match; the stretch (Solve ≥ 110); and the modal outcome (Sprint 33 showed the failure-cohort P6 is a genuine bucket source).
5. **Recommend the front-load ordering** (P1, P2 front-loaded; P4 early as the fresh lever).
6. **Write** `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md && echo "assessment doc exists"
grep -icE 'P1|P2|P3|P4|REPLAN|freed budget|reallocat|flat.?KPI|modal|front.?load|Solve.*110' docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/REPLAN_RISK_ASSESSMENT.md` with a per-track REPLAN-probability + refutation-evidence assessment (P1/P2/P3/P4)
- The pinned REPLAN exits + freed-budget reallocation (→ P6/P7)
- The honest KPI projection (firm/conditional movers, stretch, modal outcome) + the front-load ordering
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.5, 2.2, 3.2, 4.2

### Acceptance Criteria

- [ ] P1/P2/P3/P4 each assessed for REPLAN probability + the refuting control/harness evidence
- [ ] P5 (Epic-5 / Sprint-35) disposition assessed
- [ ] REPLAN exits + freed-budget reallocation pinned (→ P6/P7)
- [ ] The honest KPI projection authored (movers, stretch ≥ 110, modal outcome incl. the P6 failure-cohort lever)
- [ ] The front-load ordering recommended (deep tracks + P4 by Day 5)
- [ ] Cross-referenced to `SPRINT_33/REPLAN_RISK_ASSESSMENT.md` + `SPRINT_RETROSPECTIVE.md` §3
- [ ] Unknowns 1.5, 2.2, 3.2, 4.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis (Priorities 6 + 7)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 8
**Unknowns Verified:** 6.1, 6.2, 6.3, 7.1, 7.3

### Objective

Confirm the Sprint-28–33 diagnostic tooling covers the new Sprint-34 emit classes, and analyze the P6 failure-cohort fix-surfaces (ganges/gangesx `$141/$145/$149`, agreste scope-verify) + the P7 infrastructure scope (shape12/shape13/fawley property fixtures, genuine-floor tracking, Epic-4-SUMMARY continuation).

### Why This Matters

Priorities 6 and 7 fill the 14-day budget and absorb freed budget when a deep track REPLANs — and Sprint 33 proved the P6 failure-cohort is a genuine bucket source (sample +1). Pre-analyzing the ganges/gangesx `$141/$145/$149` root + the property-fixture scope means Day-6+ P6 work starts against a plan, not a cold survey.

### Background

The reused tooling: the KKT-residual harness (incl. `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, the `--force` scaffold, + the S33 P6 `test_sample_pruned_var_l_init.py` fixture pattern. P6: ganges/gangesx (`$141/$145/$149` translate-syntax, a different root than sample's `$140`), agreste (CASE_B `stat_sales` rel 2.0 — a scenario driver, verify scope). P7: shape12 (head-offset, once P1 lands), shape13 (sarf, once P2 lands), fawley second-index (once P3 lands); genuine-floor tracking anchor 75; Epic-4-SUMMARY row 34.

### What Needs to Be Done

1. **Audit the reused tooling** — confirm the harness (Case-a/b/c + `case_c_objdef`), the presolve-divergence detector, the golden-staleness gate, the `--resolve-changed` checkpoint, and the `--force` scaffold cover the new Sprint-34 classes (the head-offset dual residual test; the sarf symbolic emit path; the bound-transfer warm-residual test; the second-index fixture). Note any gap.
2. **Analyze the P6 fix-surfaces** — ganges/gangesx (emit + compile one; find the shared `$141/$145/$149` translate-syntax root; a single fix may recover both); agreste (verify the double-`solve` scope before treating CASE_B as an emit bug). Each `--resolve-changed`-gated.
3. **Scope the P7 property fixtures** — shape12 (head-offset dual), shape13 (sarf symbolic), fawley second-index — each fail-before/pass-after, landing *only once* P1/P2/P3 land (the S33 `test_sample_pruned_var_l_init.py` pattern); plus the genuine-floor recompute (anchor 75) + the Epic-4-`SUMMARY.md` row-34 continuation.
4. **Write** `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "analysis doc exists"
grep -icE 'kkt_residual|case_c_objdef|golden-staleness|resolve-changed|--force' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md
grep -icE 'ganges|gangesx|agreste|shape12|shape13|second-index|genuine-floor|SUMMARY' docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap) + the P6 fix-surface + P7 fixture scope
- The ganges/gangesx `$141/$145/$149` root diagnosis + the agreste scope caveat
- The shape12/shape13/fawley fixture plan (gated on P1/P2/P3) + the genuine-floor recompute (anchor 75) + Epic-4-SUMMARY continuation
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2, 6.3, 7.1, 7.3

### Acceptance Criteria

- [ ] The Sprint-28–33 tooling audited against the new Sprint-34 classes (reuse confirmed, any gap noted)
- [ ] The P6 cohort analyzed (ganges/gangesx `$141/$145/$149` root, agreste scope caveat) — each `--resolve-changed`-gated
- [ ] The P7 property fixtures scoped (shape12/shape13/fawley, fail-before/pass-after, gated on landings)
- [ ] The genuine-floor recompute (anchor 75) + Epic-4-SUMMARY row-34 continuation noted
- [ ] Cross-referenced to `SPRINT_33/TOOLING_AND_BACKLOG_ANALYSIS.md` + the S33 P6 fixture pattern
- [ ] Unknowns 6.1, 6.2, 6.3, 7.1, 7.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 34 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 34 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–10

### Objective

Produce the detailed 14-day Sprint 34 schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts, front-loading the deep tracks (P1, P2) + the fresh P4 lever so REPLANs surface by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget (88–130h work-items).

### Why This Matters

The schedule is the synthesis of all prior prep: the deep-track designs (Tasks 3–6), the Phase-0 gates (Task 8), and the REPLAN assessment (Task 9). Front-loading the movers so their REPLANs surface early — as Sprint 33's front-load correctly did (mine Day 2, fawley Day 4/5, sarf Day 6) — plus scheduling the fresh P4 lever and the P6 failure-cohort (the Sprint-33 bucket source) is the single most impactful scheduling decision.

### Background

Sprint 33's schedule + prompts are in `SPRINT_33/PLAN.md` and `SPRINT_33/prompts/`. The per-day workflow: branch → work → quality gate ONLY if `*.py` changed → commit → push → PR → user merges → "checkout main and pull". Checkpoints at Day 5 + Day 10; final retest under ≥ 3 `PYTHONHASHSEED`. The `PROJECT_PLAN.md` §"Sprint 34" Estimated Effort (88–130h) + the ~11h heaviest-day budget constrain the layout.

### What Needs to Be Done

1. **Lay out Day 0** — baseline confirmation (Task 2) + the per-track control re-confirms (mine, sarf, fawley, bound-transfer, camcge) + GO/NO-GO for Day 1.
2. **Front-load the deep + fresh tracks** — P1 (mine dual) + P2 (sarf) + P4 (bound-transfer, the fresh +Solve lever) across Days 1–7 so their REPLANs surface by the Day-5 checkpoint; P3 (fawley) + P5 (camcge/rocket) mid-sprint; P6 (failure-cohort — the Sprint-33 bucket source) + P7 in the back half.
3. **Place the checkpoints** — Day 5 (deep-track PROCEED/REPLAN + freed-budget reallocation) + Day 10; final retest Day 13 (≥ 3 `PYTHONHASHSEED`).
4. **Write the day-by-day prompts** — one per day, pasteable verbatim, each referencing its Phase-0 gate + design doc + REPLAN exit.
5. **Verify the budget** — ≤ 12h/day, ≤ 168h total, heaviest day ~11h; confirm the per-priority sizings sum to 88–130h.
6. **Confirm all Known Unknowns resolved** — if any Critical/High unknown is still `🔍 INCOMPLETE`, flag it as a Day-0 blocker.
7. **Write** `docs/planning/EPIC_4/SPRINT_34/PLAN.md` + `docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md`.

### Changes

*To be completed*

### Result

*To be completed*

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_34/PLAN.md && echo "plan exists"
test -f docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md && echo "prompts exist"
# Day 0 + Days 1-13 all present as prompt headers
grep -cE '^## Day ([0-9]|1[0-3]) Prompt' docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md
# the checkpoints + the deep-track front-load are present
grep -icE 'Day 5|Day 10|checkpoint|front.?load|PYTHONHASHSEED' docs/planning/EPIC_4/SPRINT_34/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_34/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the deep + P4 front-load, checkpoints, and budget verification
- `docs/planning/EPIC_4/SPRINT_34/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The budget confirmation (≤ 12h/day, ≤ 168h total, 88–130h work-items)

### Acceptance Criteria

- [ ] The 14-day schedule laid out (Day 0 + Days 1–13) with the deep tracks (P1, P2) + P4 front-loaded
- [ ] Checkpoints placed (Day 5 PROCEED/REPLAN + freed-budget reallocation, Day 10, final retest Day 13)
- [ ] A pasteable day-by-day prompt authored for every day, each referencing its gate + design doc + REPLAN exit
- [ ] The budget verified (≤ 12h/day, ≤ 168h, 88–130h work-items, heaviest ~11h)
- [ ] All 6 categories' Critical/High unknowns confirmed resolved (or flagged as Day-0 blockers)
- [ ] Cross-referenced to all prior prep tasks (Tasks 1–10)

---

## Summary: Prep Task Execution Order

**Recommended sequence** (respecting dependencies + the critical path):

1. **Tasks 1 + 2 (parallel, Critical)** — Known Unknowns + Day-0 baseline (anchor 75). The foundation everything else re-confirms against.
2. **Tasks 3 + 4 + 5 + 6 + 7 (parallel after 1/2)** — the per-track design docs (mine dual subsystem, sarf emit mode, fawley correction + forcing, the NEW bound-transfer track, camcge/rocket). Tasks 3/4 are the deep-track designs on the critical path; Task 6 is the fresh +Solve lever.
3. **Task 8 (Critical, after 1/3/4/5/6/7)** — consolidate the per-track `/tmp` controls into the Phase-0 gates.
4. **Task 9 (High, after 3/4/5/6/8)** — the REPLAN-prone risk assessment + the honest KPI projection.
5. **Task 10 (Medium, after 1/8)** — the tooling-readiness audit + P6/P7 backlog analysis.
6. **Task 11 (Critical, after 1–10)** — the detailed 14-day schedule + prompts.

### Success Criteria for Sprint 34 Prep

- [ ] All 11 prep tasks complete (or explicitly deferred with rationale)
- [ ] Known Unknowns list identifies ≥ 25 unknowns with verification plans (Task 1)
- [ ] Day-0 baseline confirmed = Sprint 33 close (Solve 108 / Match 93 / genuine floor 75), Day-0 code anchor = S33-close SHA (Task 2)
- [ ] Each deep track (P1 mine dual, P2 sarf, P3 fawley) + the NEW P4 has a `file:line` design + a pre-`src/` `/tmp` control (Tasks 3, 4, 5, 6)
- [ ] camcge Walras (Epic 5) + rocket PATH submission designed (Task 7)
- [ ] A Phase-0 acceptance gate authored per track P1–P5 with `modelstat` + PROCEED/REPLAN (Task 8)
- [ ] The REPLAN-prone risk assessment pins exits + the honest modal-KPI projection (Task 9)
- [ ] The tooling reuse is confirmed + the P6/P7 fix-surfaces analyzed (Task 10)
- [ ] The 14-day schedule + day-by-day prompts front-load the deep tracks + P4 with Day-5/10 checkpoints (Task 11)
- [ ] Every design carries an explicit REPLAN exit (the modal outcome is de-risking + maybe the P6 failure-cohort, not a guaranteed deep-track bucket move)

---

## Appendix: Document Cross-References

- **Sprint 34 scope:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 34 (Weeks 33–34)" (lines ~1623–1692)
- **Epic 4 goals:** `docs/planning/EPIC_4/GOALS.md`
- **Sprint 33 close (the source of the carryforwards):** `SPRINT_33/SPRINT_LOG.md` · `SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 · `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`
- **Per-track Sprint-33 control docs:** `SPRINT_33/DAY2_MINE_REPLAN.md` · `SPRINT_33/DAY1_PROGRESS_NOTES.md` · `SPRINT_33/MINE_CROSSTERM_DESIGN.md` (P1) · `SPRINT_33/DAY6_SARF_ASSESSMENT.md` · `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` (P2) · `SPRINT_33/DAY4_FAWLEY_CONTROL.md` · `SPRINT_33/DAY5_FAWLEY_CLOSE.md` · `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` (P3) · `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` · `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` (P5)
- **Prep-format templates:** `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md` · `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md` · `SPRINT_33/PREP_PLAN.md` (the direct analog)
- **Epic 5:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (camcge Walras)
- **Reused tooling:** `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`) · `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit`) · `scripts/diagnostics/check_presolve_divergence.py` · `scripts/sprint_audit/check_golden_staleness.py` · `src/cli.py` (`--force`)
- **Research:** `docs/research/multidimensional_indexing.md` (sarf) · `docs/research/convexity_detection.md` (Case-c)

---

**Document Created:** 2026-07-18
**Owner:** Sprint 34 Planning Team
**Status:** 🔵 Prep NOT STARTED — execute Tasks 1–11 before Sprint 34 Day 1
