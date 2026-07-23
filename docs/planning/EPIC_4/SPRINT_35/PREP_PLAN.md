# Sprint 35 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 35 begins
**Timeline:** Complete before Sprint 35 Day 1
**Goal:** Set up Sprint 35 for success — land the Sprint 34 REPLAN'd/deferred/banked carryforwards, each of which arrives as a **control-confirmed, precisely-pinned specification** rather than an open question (`docs/planning/EPIC_4/SPRINT_34/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`). Sprint 34 closed **full modal-flat — 0 bucket moves** (Solve 108 / Match 93 / genuine floor 75 all held), *exactly* the Task-9 honest projection: every deep emit track REPLAN'd or deferred after a `/tmp`/harness/compile control refuted or de-risked its premise **before any bad ship** (zero broken code across 8 execution PRs), and the sole `src/` landing (P4 sense-aware bound-transfer) was a general warm-start-correctness fix with no +Solve. Sprint 35 inherits four deep emit tracks — the **mine head-offset dual subsystem** (#1443 — S34 Day 1's cold-MS-1 control refuted H_dual: the boundary is **`x.m=0`-degenerate**, needing a dual-architecture rethink, not a keying tweak); the **sarf symbolic-emit subsystem** (#1385 — the 369,024-column `task` materialization needs a from-scratch symbolic/parametric emit *mode*, a corpus-wide re-architecture of the foundational `enumerate_variable_instances`); the **fawley constraint-index-diagonal correction** (#1111/#1112 — the qsb/pbal `sameas` gap is genuine [473 → 18.468 control-proven] in the ~1430-line `_add_indexed_jacobian_terms`, but fawley's +Solve is **H-b** [non-emit MS-5 divergence → forcing]); and the **NEW ganges/gangesx multi-root recovery** (S34 Day 11 *corrected* the prep's single-root hypothesis into **three independent roots**: the verified-and-banked `$141` `.l`-calibration NaN-cleanup fix, the `$145` universal-set gap, and the deep **`$149` CES/LES `prod()` product-rule stationarity AD bug** that gates six models) — plus the **camcge dual-consistent Walras** (#1330 → Epic 5) and the **rocket PATH-consultation submission** (#1462 → the now-Sprint-36 consultation). Targets: Solve maintain **108** (+1–4 firm via mine [P1] / fawley-forcing [P3] / ganges·gangesx [P4] / camcge [P5-Epic5]; stretch ≥ 112); Match maintain ≥ **93** as-measured / genuine floor **75 → ≥ 76**; Translate maintain ≥ **135** (+1 → 136 via #1385 sarf); model_infeasible ≤ **7**; path_syntax_error ≤ **7** (−2 → 5 via the ganges pair).

**Key Insight from Sprint 34:** Sprint 35 is **specification-bound, not diagnosis-bound** — with two sharper lessons than Sprint 34 carried. (1) **The prep fix-surface hypotheses were optimistic *again*.** Sprint 34's prep asserted "ganges/gangesx share a single `$141/$145/$149` root; one fix recovers both"; Day 11 found **three independent roots** and **no model recovering from `$141` alone**. That is the standing lesson (prep `file:line`/root hypotheses are wrong ~half the time) firing for the fourth consecutive sprint — so Sprint 35 prep must treat the P4 root structure as **verified-per-model, not asserted**, and must budget an *analysis* task for the `$149` product-rule AD bug ahead of the P4 recovery design. (2) **"No bucket → no `src/`" cost a real, verified fix.** The `$141` fix was written, empirically verified (removes all 15 `$141`), and then **reverted** — because it recovered 0 bucket alone *and* its slow-emit CGE goldens are un-regenerable in the CI budget (`make regen-goldens` soft-timed-out on ganges/gangesx/clearlak/turkpow, refreshing 0 goldens). Sprint 35's P4 is the effort that must ship all three roots *together* and can afford the slow regen — so the **golden-regeneration budget is itself a prep deliverable**, not a Day-11 discovery. Alongside these: keep the PR24/PR27 control-experiment-before-implement gate as the standing discipline on P1–P5 (it prevented every bad ship in S32/S33/S34), and keep the honest **modal-flat-KPI** projection binding — three consecutive sprints have shown the deep AD/emit tracks (mine, sarf, fawley) move no bucket, while the **failure-cohort track is the genuine bucket source** (S33 sample +1; S34's P6 got closest). P4 is therefore Sprint 35's designated best shot, and it is scheduled and resourced as such.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

> **Note on location.** Sprint 35 is defined in `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35 (Weeks 35–36)" (lines ~1696–1767). This prep plan is filed under `EPIC_4/SPRINT_35/` alongside the Sprint-31/32/33/34 prep plans it mirrors, and follows the prep-plan format established in `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md` and `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md`.

---

## Executive Summary

Sprint 35 inherits the six Sprint-34 REPLAN'd/deferred/banked carryforwards (Priorities 1–5 in `PROJECT_PLAN.md` §"Sprint 35"): the mine head-offset dual subsystem (#1443); the sarf symbolic-emit subsystem (#1385); the fawley #1111/#1112 constraint-index-diagonal correction + forcing; the **NEW** ganges/gangesx multi-root recovery (`$141` + `$145` + `$149`, plus turkey's `$161`); and the camcge #1330 dual-consistent Walras numéraire (Epic 5) + the rocket #1462 PATH-consultation submission to the now-Sprint-36 consultation. Priority 6 pulls the residual `path_syntax_error` cohort (dinam/indus `$140`+`$149`; turkpow/clearlak `$149`+`$171`; turkey `$161`) + the banked Case-c follow-ons; Priority 7 (infrastructure) adds the property fixtures for the tracks that land (**shape12** head-offset once P1 lands, **shape13** sarf once P2 lands, a **fawley 2-D second-index** fixture once P3 lands, a **ganges recovery** raw-emit fixture once P4 lands — all following the S33 `test_sample_pruned_var_l_init.py` skip-if-absent pattern and the S34 `test_p4_maximize_bound_transfer_sense_aware` pattern), recomputes the PR25 genuine-floor tracking against the anchor (**75**), refreshes the `--resolve-changed` checkpoint targets, and continues the Epic-4 `SUMMARY.md` groundwork (row 35).

Sprint 35 resembles Sprint 34 structurally — **Sprint 34 diagnosed, control-confirmed, and precisely characterized these tracks; Sprint 35 implements them against a de-risked specification** — but the shape of the work has shifted in one decisive way. Three consecutive sprints (S32, S33, S34) have front-loaded the same three deep AD/emit tracks (mine, sarf, fawley) and all three have REPLAN'd or deferred every time, moving **zero** buckets; meanwhile the *failure-cohort* track produced the only genuine bucket move in that window (S33 P6 sample). Sprint 34's Day-11 re-triage then handed Sprint 35 the most concrete recovery specification the corpus has seen: two models (ganges, gangesx) whose three blocking roots are each individually characterized, one of which (`$141`) is **already written and empirically verified**. So this prep plan deliberately **promotes the ganges/gangesx recovery to first-class critical-path status** (a dedicated root-analysis task *and* a dedicated recovery-design task), while keeping the three deep tracks fully designed and Phase-0-gated — and it adds a prep task that removes the specific operational blocker that forced S34 to bank a working fix (the slow-emit CGE golden-regeneration budget).

The hardest track (P1 mine) needs a genuine **head-offset dual-architecture design** — H_dual is refuted, so the design must answer how head-placed constraint duals reconcile into `stat_x` when `x.m = 0` makes the boundary degenerate, or else name the deeper-architecture REPLAN exit up front. The second (P2 sarf) needs the **symbolic/parametric emit-mode re-architecture design** that stops enumerating `task`'s 369K columns at all three sites (S1 `acost3` body-diff, S2 `enumerate_variable_instances`, S3 per-column `stat_task`) atomically, in a foundational function all 142 models traverse. P3 (fawley) needs the **constraint-index-diagonal design** plus the explicit forcing hand-off for its H-b +Solve. P4 (ganges/gangesx) needs the **`$149` uncontrolled-index product-rule root analysis** first (a hand-derived `stat_pc` cross-term for a CES/LES `prod()`) and then the multi-root recovery design that sequences `$141` → `$145` → `$149` with a per-root `--resolve-changed` gate. The Sprint-28–34 diagnostic tooling (KKT-residual harness incl. `case_c_objdef`, presolve-divergence detector, golden-staleness gate, `--resolve-changed` checkpoint re-solve, the `--force` scaffold, the S33 `.l`-init fixture pattern, the S34 bound-transfer fixture pattern) is **reused rather than rebuilt** throughout.

This prep plan focuses on:

1. **Risk identification** — a Sprint 35 Known Unknowns List covering the six carryforward tracks (each a Sprint-34 control-confirmed characterization that nonetheless remains a Day-0-re-confirm hypothesis, PR24), the three thrice/twice-carried deep tracks (P1 mine, P2 sarf, P3 fawley), the NEW P4 multi-root recovery (including the depth of the `$149` AD-core bug), and the P6/P7 scope.
2. **Day-0 baseline + genuine-floor re-baseline (PR15 + PR17 + PR25)** — Sprint 34 final → Sprint 35 Day-0 per-model bucket provenance, confirming Day 0 = Sprint 34 close (Solve 108, Match 93, genuine floor 75, model_infeasible 7, path_syntax_error 7, Translate 135, all-219 Match 96) and pinning the Day-0 code anchor to the **S34-close SHA `78ceaead`** (the DB has been byte-unchanged since `750803b2`, but `src/` changed at S34 Day 4 — P4 — so the checkpoint anchor must advance).
3. **Reusable-tooling readiness audit + the slow-emit CGE golden-regeneration budget + the P7 fixture catalog** — confirm the S28–34 tools cover the new Sprint-35 classes, and *resolve the operational blocker that forced S34 to bank the verified `$141` fix* by measuring and budgeting the ganges/gangesx/clearlak/turkpow golden regeneration ahead of Day 1.
4. **`$149` CES/LES `prod()` product-rule stationarity AD root analysis + the uncontrolled-index cohort catalog (P4 + P6 foundation)** — hand-derive the correct `stat_pc` cross-term, localize the free-index defect in the AD/stationarity emit, and catalog every cohort member the fix does and does not unblock.
5. **ganges/gangesx multi-root recovery design (Priority 4)** — sequence the three roots (`$141` re-apply → `$145` universal-set skip → `$149` product-rule fix) plus turkey's `$161`, each with its own `--resolve-changed` gate and per-model verification (the multi-root discipline S34 Day 11 established).
6. **mine head-offset dual-architecture design (Priority 1 foundation)** — turn the S34 Day-1 refutation (H_dual value-invariant; `x.m = 0`-degenerate boundary) into a concrete dual-architecture design or an explicitly-named REPLAN exit, sizing the deepest carryforward BEFORE the schedule is set.
7. **sarf symbolic/parametric emit-mode re-architecture design (Priority 2 foundation)** — design the symbolic emit mode across S1/S2/S3 atomically with a full-corpus regression harness, since `enumerate_variable_instances` is foundational for all 142 models.
8. **fawley constraint-index-diagonal correction + forcing design (Priority 3 foundation)** — design the genuine `sameas` cross-term correction (guarded by a 2-D-cohort regression harness) + the forcing hand-off for the H-b +Solve.
9. **camcge dual-consistent Walras design (Epic 5) + rocket PATH-consultation submission plan (Priority 5)** — the Walras-law dual redefinition to MS-1 as the Epic-5 `/tmp` gate + the rocket input submission to the **Sprint-36** consultation.
10. **Phase 0 acceptance gates (PR20 + PR24 + PR27)** — author the gates for the Sprint-35 tracks (P1 cold-MS-1 with `modelstat` asserted, P2 O(active = 398) emit budget, P3 `max|stat_bq| → 0` + the H-b forcing branch, P4 per-root `--resolve-changed` + the hand-derived `$149` control, P5 the Walras `/tmp` MS-1 gate).
11. **Diagnosis-heavy / REPLAN-prone track risk assessment (PR16)** — REPLAN priors + refutation evidence per track, pinned exits, freed-budget reallocation, the front-load ordering, and the honest KPI projection naming P4 as the designated best shot.
12. **Sprint planning** — the detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day per the `PROJECT_PLAN.md` Sprint 35 entry (92–134h work-items under the 168h cap).

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 35 Known Unknowns List | Critical | 3–4h | None | All priorities — risk identification |
| 2 | Sprint 34 → Sprint 35 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25) | Critical | 3–4h | None | All priorities — baseline metrics + genuine-floor anchor |
| 3 | Reusable-Tooling Readiness Audit + Slow-Emit CGE Golden-Regeneration Budget + P7 Fixture Catalog | High | 4–5h | Tasks 1, 2 | Priorities 4, 7 — unblocks the S34 ship-blocker; tooling reuse |
| 4 | `$149` CES/LES `prod()` Product-Rule Stationarity AD Root Analysis + Uncontrolled-Index Cohort Catalog | Critical | 5–7h | Tasks 1, 2 | Priorities 4, 6 — the deep blocker gating six models |
| 5 | ganges/gangesx Multi-Root Recovery Design (Priority 4 foundation) | Critical | 5–7h | Tasks 3, 4 | Priority 4 — the designated best-shot bucket mover |
| 6 | mine Head-Offset Dual-Architecture Design (Priority 1 foundation) | Critical | 6–8h | Tasks 1, 2 | Priority 1 — mine (Solve) deepest track |
| 7 | sarf Symbolic/Parametric Emit-Mode Re-Architecture Design (Priority 2 foundation) | High | 5–7h | Tasks 1, 2 | Priority 2 — sarf (Translate) 369K elimination |
| 8 | fawley Constraint-Index-Diagonal Correction + Forcing Hand-Off Design (Priority 3 foundation) | High | 4–6h | Tasks 1, 2 | Priority 3 — fawley (floor) + the H-b forcing tail |
| 9 | camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5) | Medium | 3–4h | Task 1 | Priority 5 — Epic-5 camcge + the Sprint-36 rocket hand-off |
| 10 | Author Phase 0 Acceptance Gates for the Sprint-35 Tracks (PR20 + PR24 + PR27) | Critical | 4–6h | Tasks 4, 5, 6, 7, 8, 9 | Priorities 1–5 — primary scope-correctness gate |
| 11 | Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment + Honest KPI Projection (PR16) | High | 4–6h | Tasks 5, 6, 7, 8, 10 | Priorities 1–4 — REPLAN-prone tracks + front-load ordering |
| 12 | Plan Sprint 35 Detailed Schedule | Critical | 3–4h | Tasks 1–11 | All priorities — sprint planning |

**Total Estimated Time:** 49–68 hours (~6–9 working days)

**Critical Path:** Task 1 → Task 4 → Task 5 → Task 10 → Task 11 → Task 12 — the **P4 ganges/gangesx chain**, which is Sprint 35's designated best-shot bucket mover: the `$149` root analysis (Task 4) sizes the deep half of P4 and feeds the recovery design (Task 5), which feeds the Phase-0 gates (Task 10), the REPLAN assessment (Task 11), and the schedule (Task 12). A secondary near-critical chain runs Task 1 → Task 6 (mine dual architecture) → Task 10 → Task 11 → Task 12, because P1 is the largest single budget line (18–24h) and its REPLAN prior is the highest. Tasks 3, 7, 8, 9 are parallelizable after Tasks 1/2; Task 3 must land before Task 5 (the golden-regeneration budget is a P4 design input).

---

## Task 1: Create Sprint 35 Known Unknowns List

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create a proactive `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` cataloguing every assumption and open question across the seven categories (the six carryforward tracks P1–P5 — with the NEW ganges/gangesx multi-root recovery as its own category — plus the P6 residual cohort + P7 infrastructure), so no Sprint-34-style late correction (the Day-11 single-root refutation) survives undiscovered to Day 5.

### Why This Matters

The standing PR24/PR27 lesson, reaffirmed on every Sprint-34 track: **a banked, control-confirmed characterization is still a Day-0-re-confirm hypothesis.** Sprint 34's own prep asserted a single shared ganges/gangesx root and was substantially wrong — three independent roots, no model recovering from `$141` alone. A Known Unknowns list turns each carryforward's residual assumptions into an explicit, verifiable pre-Day-1 checklist, forces the multi-root discipline into the open for P4/P6, and puts the honest modal-flat-KPI projection on the table before the schedule is drawn.

### Background

Sprint 35's carryforwards each arrive with a Sprint-34 control-confirmed diagnosis but an *un-built* fix (see `PROJECT_PLAN.md` §"Sprint 35" + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`). Three (P1 head-offset dual, P2 symbolic-emit mode, P3 constraint-index diagonal) are from-scratch AD/emit workstreams whose *implementation shape* remains genuinely open and which have now REPLAN'd/deferred in three consecutive sprints. The NEW P4 is the most concretely specified (one root already written + verified) but the least *architecturally* understood at its deep end (`$149` is an AD-core product-rule defect). Mirror the Sprint-34 Known Unknowns structure (`SPRINT_34/KNOWN_UNKNOWNS.md`, 27 unknowns / 7 categories).

### What Needs to Be Done

1. **Review the Sprint 35 scope** from `PROJECT_PLAN.md` §"Sprint 35" (Priorities 1–7) + `SPRINT_34/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` + the per-track S34 control docs (`DAY1_`, `DAY5_`, `DAY6_`, `DAY10_`, `DAY11_PROGRESS_NOTES.md`).
2. **Enumerate unknowns per category** (assumption · how-to-verify · priority · risk-if-wrong · verification deadline):
   - **Category 1 — mine head-offset dual subsystem (#1443):** Given H_dual is refuted and the boundary is `x.m = 0`-degenerate, does *any* emit-side dual architecture reach **cold MS-1 @ 17500**, or is the LP's warm KKT point genuinely not MCP-reconcilable (→ the PATH-consultation track)? Does the S31 `head_domain_offsets` IR carry what a reconciliation would need? Is the 22-row breadth still exact at Day 0? Is `x.up=inf` still **BANNED** (assert `modelstat`)?
   - **Category 2 — sarf symbolic/parametric emit mode (#1385):** Can `enumerate_variable_instances` gain a symbolic-column concept without perturbing the other 141 models' `col_to_var` ordering? Are all three sites (S1/S2/S3) covered, or is there a 4th? Is the banked 7-term `stat_task` derivation complete? Does the re-emit land at **O(active = 398)** (seconds), not O(369K) (>75s)?
   - **Category 3 — fawley constraint-index-diagonal correction (#1111/#1112):** Does the diagonal `sameas` extension drive `max|stat_bq| → 0` (not 96%) without changing any mbal term or regressing the 1-D polygon/ps2 core? Is the H-b finding still exact (MS-5 @ 4399.557 with the warm residual closed)? Does the genuine correction lift the floor if fawley cold-matches even under H-b?
   - **Category 4 — ganges/gangesx multi-root recovery (NEW):** Is the banked `$141` fix still clean-applying at the S35 tree, and does it still remove all 15 `$141`? Is `$145` genuinely a separate universal-set (`*`-domain) NaN-cleanup gap? Is the `$149` free-`j` defect in the stationarity emit or in the AD core, and what is the correct hand-derived `stat_pc` cross-term? **After all three roots, do ganges/gangesx actually compile and solve** (the S34 lesson: no model recovered from one root alone — verify per-model, assume nothing shared)? Can the slow-emit goldens be regenerated inside the sprint budget?
   - **Category 5 — camcge Walras (#1330 / Epic 5) + rocket PATH:** Does the full dual-consistent redefinition reach MS-1 at omega 191.7346 in a `/tmp` prototype (the Epic-5 gate)? Does the S1∧S2∧S3 detector still fire only on camcge? Is the FINALIZED rocket input complete for **Sprint-36** submission (note the renumbering — the consultation sprint is now 36)?
   - **Category 6 — P6 residual failure-cohort:** Which cohort members does the `$149` fix actually unblock (dinam/indus also carry `$140`; turkpow/clearlak also carry `$171`)? Is turkey's `$161` dotted-tuple set-declaration root independent of everything else? Does the Case-c family stay documented-non-convex (sign flip **BANNED**)?
   - **Category 7 — P7 infrastructure:** Do shape12/shape13/fawley-2-D/ganges fixtures fail-before/pass-after only once their tracks land? Is the PR25 genuine-floor anchor still **75** and the Day-0 code anchor the **S34-close SHA**? What does Epic-4 `SUMMARY.md` row 35 need?
3. **Prioritize** by risk (Critical / High / Medium / Low).
4. **Assign a verification method + deadline** (Day 0 / Day 1 / Day N) to every Critical/High unknown.
5. **Write** `KNOWN_UNKNOWNS.md` with the update template + priority definitions + a Task-to-Unknown mapping appendix (which prep Task 2–11 verifies which unknowns).

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md && echo "file exists"
# >= 25 unknowns — headings are '## Unknown N.M:'
grep -cE '^## Unknown [0-9]+\.[0-9]+:' docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md
# all 7 categories present — headings are '# Category N:'
grep -cE '^# Category [0-9]:' docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md
# every unknown carries a Verification Results section (N + 1 template)
grep -cE '^### Verification Results$' docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md
# the multi-root discipline and the renumbered consultation sprint are represented
grep -icE 'multi-root|per-model|Sprint 36|Sprint-36' docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/KNOWN_UNKNOWNS.md` with ≥ 25 unknowns across 7 categories (one per carryforward track — the NEW ganges/gangesx multi-root recovery its own category — plus P6 + P7)
- Each unknown: assumption · verification method · priority · risk-if-wrong · estimated research time · owner
- Update template + priority definitions + the Task-to-Unknown mapping appendix

### Acceptance Criteria

- [ ] Document created with ≥ 25 unknowns across the 7 categories
- [ ] All unknowns have assumption, verification method, priority, risk-if-wrong
- [ ] All Critical/High unknowns have a verification method + research time + a Day-0/Day-N deadline
- [ ] The Sprint-34 lessons are represented as explicit unknowns: the multi-root discipline (P4/P6), the `x.m = 0` degeneracy (P1), the H-b +Solve (P3), the modal-flat-KPI reality
- [ ] The Sprint-36 renumbering of the PATH consultation is captured in Category 5
- [ ] Update template + priority definitions + Task-to-Unknown mapping included
- [ ] Cross-referenced to `PROJECT_PLAN.md` §"Sprint 35" and the Sprint-34 control docs

---

## Task 2: Sprint 34 → Sprint 35 Day-0 Baseline + Genuine-Floor Re-Baseline (PR15 + PR17 + PR25)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** None

### Objective

Establish and document the Sprint 35 Day-0 baseline — per-model bucket provenance for the 142-model convex-candidate corpus — confirm it equals the Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / Parse 142 / all-219 Match 96), and **advance the `--resolve-changed` code anchor to the S34-close SHA `78ceaead`**.

### Why This Matters

Every Sprint-35 KPI delta is measured against this baseline, and every emit-touching PR is gated by `--resolve-changed --since-commit <anchor>`. Getting the anchor wrong silently invalidates the whole sprint's no-regression evidence. Sprint 35 has a *specific* anchor subtlety: the DB has been byte-unchanged since the S33 close `750803b2`, but `src/` did change during Sprint 34 (the Day-4 P4 sense-aware bound-transfer + 11 regenerated presolve goldens), so the checkpoint anchor must advance to the **S34 close** even though the DB did not move. The PR25 genuine-vs-methodology split is likewise the KPI that actually gates the sprint's headline claim (genuine floor 75 → ≥ 76), and it must be recomputed, not inherited by assertion.

### Background

`SPRINT_34/BASELINE_METRICS.md` is the template (it pinned the S33-close SHA `750803b2` and floor 75). The Sprint-34 close is commit `78ceaead` (PR #1602, "Sprint 34 Day 13: Final retest + CLOSE"); `main` has since advanced only by the docs-only PROJECT_PLAN cascade (PR #1603, `cf34a80c`), so `git diff 78ceaead..HEAD -- src/ scripts/` is expected clean. Corpus scope, the genuine-vs-methodology definition, and the 142-vs-219 distinction are in `docs/planning/EPIC_4/SPRINT_28/` + the Match/Solve KPI corpus-scope reference. The DB is `data/gamslib/gamslib_status.json` (schema 2.2.1).

### What Needs to Be Done

1. **Derive the Day-0 code anchor portably** and record it:
   ```bash
   S34=$(git log --first-parent main --grep='SPRINT 34 CLOSED' --format=%H -n 1)
   ```
   Confirm it resolves to the S34-close merge; record the full SHA + the DB md5.
2. **Confirm zero `src/`/`scripts/` drift** since the anchor (`git diff --quiet 78ceaead..HEAD -- src/ scripts/`), so the committed DB can be reused byte-for-byte without a fresh full retest.
3. **Recompute the KPI table from the committed DB** (142 convex-candidate corpus): Parse / Translate / Solve (cold + presolve split) / Match as-measured / genuine floor / model_infeasible / path_syntax_error / all-219 Match tally.
4. **Recompute the PR25 genuine-vs-methodology split** and confirm the anchor is **75** (63 cold + 12 genuine-presolve; methodology 21; all-219 Match 96 = 63 cold + 33 presolve).
5. **Record per-model provenance for every Sprint-35 target model** — mine, sarf, fawley, ganges, gangesx, camcge, rocket, turkey, dinam, indus, turkpow, clearlak, agreste — with its current bucket, failure code, and the priority that owns it.
6. **Run the `--resolve-changed --since-commit <anchor> --dry-run` GO check** and record the result as the Day-0 gate.
7. **Note the anchor advance explicitly** — DB byte-unchanged since `750803b2` but the code anchor is now the S34 close — so no day of the sprint re-uses the stale anchor.
8. **Write** `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md && echo "baseline doc exists"
# the Day-0 code anchor is the S34 close, and it is recorded in the doc
S34=$(git log --first-parent main --grep='SPRINT 34 CLOSED' --format=%H -n 1); echo "anchor: $S34"
grep -c "${S34:0:8}" docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md
# no src/ or scripts/ drift since the anchor (baseline is reusable byte-for-byte)
git diff --quiet "$S34"..HEAD -- src/ scripts/ && echo "no drift"
# the headline KPI numbers + the genuine-floor anchor are present
grep -icE '108|93|75|135|142|genuine floor' docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md
# the DB md5 is recorded
md5 -q data/gamslib/gamslib_status.json 2>/dev/null || md5sum data/gamslib/gamslib_status.json
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` with the Day-0 KPI table (142 corpus) + the Sprint-35 target column
- The Day-0 code anchor (S34-close SHA) + the DB md5 + the portable anchor-derivation snippet
- The PR25 genuine-vs-methodology recompute confirming the anchor **75**
- Per-model provenance rows for all 13 Sprint-35 target models
- The `--resolve-changed --dry-run` Day-0 GO record + the explicit anchor-advance note

### Acceptance Criteria

- [ ] Day-0 baseline confirmed = Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / Translate 135 / Parse 142 / mi 7 / pse 7 / all-219 96)
- [ ] Day-0 code anchor pinned to the S34-close SHA, with the portable derivation recorded
- [ ] Zero `src/`/`scripts/` drift verified since the anchor (baseline reused byte-for-byte, no fresh retest)
- [ ] PR25 genuine-floor anchor recomputed and confirmed at **75**
- [ ] Per-model provenance recorded for mine, sarf, fawley, ganges, gangesx, camcge, rocket, turkey, dinam, indus, turkpow, clearlak, agreste
- [ ] `--resolve-changed --since-commit <anchor> --dry-run` = GO recorded
- [ ] The anchor-advance caveat (DB unchanged since `750803b2`, code anchor now S34-close) called out explicitly
- [ ] Cross-referenced to `SPRINT_34/BASELINE_METRICS.md` + the corpus-scope reference

---

## Task 3: Reusable-Tooling Readiness Audit + Slow-Emit CGE Golden-Regeneration Budget + P7 Fixture Catalog

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–5 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2

### Objective

Confirm the Sprint-28–34 diagnostic tooling covers the new Sprint-35 emit classes without new tool code; **measure and budget the slow-emit CGE golden regeneration** (ganges, gangesx, clearlak, turkpow) that blocked Sprint 34 from shipping its verified `$141` fix; and catalog the P7 property fixtures each landing track will need.

### Why This Matters

This task removes the single operational blocker that turned a *working, verified* Sprint-34 fix into a banked one. S34 Day 11 shipped no `src/` for the `$141` fix specifically because `make regen-goldens` soft-timed-out on ganges/gangesx/clearlak/turkpow, refreshing **0** goldens — so shipping would have left stale goldens. Sprint 35's P4 is *defined* as the effort that "can afford the slow ganges/gangesx golden regen", but affording it requires knowing, before Day 1, how long it actually takes, whether it can run out-of-band (nightly/background), and what the determinism-×3 cost is on top. Discovering that on Day 11 again would repeat the exact failure. The tooling audit and fixture catalog are the standing (cheap) half of the task: they keep Sprint 35 at **zero new diagnostic-tool code** and give P7 a plan instead of a cold survey.

### Background

Reused tooling: `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`), `scripts/diagnostics/check_presolve_divergence.py`, `scripts/sprint_audit/check_golden_staleness.py`, `scripts/gamslib/run_full_test.py --resolve-changed --since-commit`, the `--force` scaffold in `src/cli.py`, the AD cross-term catalog (`tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/`), the S33 `test_sample_pruned_var_l_init.py` skip-if-absent pattern, and the S34 `test_p4_maximize_bound_transfer_sense_aware` fixture (`tests/fixtures/crossterm_shapes/shape_p4_max_bound_transfer.gms`). The regen target is `Makefile:72` (`regen-goldens`). Precedent: `SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md`.

### What Needs to Be Done

1. **Audit the reused tooling against the new Sprint-35 classes** — the head-offset dual residual test (P1), the sarf symbolic-emit path + a full-corpus regression harness (P2), the 2-D-cohort `sameas` regression harness (P3), the raw-emit compile check for the ganges roots (P4), the Case-c documentation path (P6). Record reuse vs gap; the target is **zero new diagnostic-tool code**.
2. **Measure the slow-emit golden regeneration** — time a single-model emit for ganges, gangesx, clearlak, turkpow (`data/gamslib/raw/` present locally; these tests `pytest.skip` in CI). Record wall-clock per model, whether `make regen-goldens` completes when scoped to just those models, and the peak time under `sys.setrecursionlimit(50000)`.
3. **Budget the regeneration into the sprint** — propose a concrete plan: scoped/per-model regen invocation, an out-of-band (nightly/background) run window, the determinism-×3 (`PYTHONHASHSEED` {0,1,42}) multiplier, and the `--resolve-changed` re-solve cost afterwards. State explicitly whether P4 can ship inside a normal ≤ 12h day or needs a dedicated overnight slot.
4. **Catalog the P7 property fixtures**, each gated on its own track's landing and each fail-before/pass-after: **shape12** (head-offset dual → P1), **shape13** (sarf symbolic → P2), **fawley 2-D second-index** (→ P3), **ganges recovery raw-emit** (→ P4, following the `test_sample_pruned_var_l_init.py` skip-if-absent pattern since `data/gamslib/raw/` is absent in CI). Note the genuine-floor recompute (anchor 75) + the Epic-4 `SUMMARY.md` row-35 continuation.
5. **Re-run the Day-0 gate** — `--resolve-changed --since-commit <S34-close> --dry-run` = GO.
6. **Write** `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md && echo "analysis doc exists"
# the reused tools are all referenced (reuse, not rebuild)
grep -icE 'kkt_residual|case_c_objdef|check_presolve_divergence|check_golden_staleness|resolve-changed|--force' docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md
# the golden-regeneration budget is quantified for all four slow-emit models
grep -icE 'ganges|gangesx|clearlak|turkpow|regen-goldens|wall.?clock|PYTHONHASHSEED' docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md
# the P7 fixture catalog names all four fixtures + their gating tracks
grep -icE 'shape12|shape13|second-index|ganges recovery|fail-before|skip-if-absent' docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md
# the tools themselves still exist where the audit says they do
test -f scripts/diagnostics/kkt_residual.py && test -f scripts/sprint_audit/check_golden_staleness.py && echo "tools present"
grep -n '^regen-goldens:' Makefile
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` with the tooling-readiness audit (reuse vs gap)
- A **measured** slow-emit golden-regeneration budget for ganges / gangesx / clearlak / turkpow (per-model wall-clock, scoped-regen feasibility, determinism-×3 multiplier, out-of-band run plan)
- An explicit statement of whether the P4 golden regen fits a ≤ 12h day or requires a dedicated overnight slot
- The P7 fixture catalog (shape12 → P1, shape13 → P2, fawley 2-D → P3, ganges recovery → P4), each fail-before/pass-after and landing-gated
- The genuine-floor recompute note (anchor 75) + the Epic-4 `SUMMARY.md` row-35 continuation scope
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 4 regen unknown + the Category 7 unknowns

### Acceptance Criteria

- [ ] The S28–34 tooling audited against the new Sprint-35 classes; reuse confirmed with any gap named (target: zero new diagnostic-tool code)
- [ ] Golden-regeneration wall-clock **measured** (not estimated) for ganges, gangesx, clearlak, turkpow
- [ ] A concrete regen plan proposed (scoped invocation + run window + determinism-×3 cost + the follow-on `--resolve-changed` cost)
- [ ] The "fits a normal day / needs an overnight slot" verdict stated explicitly for P4
- [ ] The four P7 fixtures catalogued with their gating tracks and the skip-if-absent pattern for raw-dependent fixtures
- [ ] `--resolve-changed --since-commit <S34-close> --dry-run` = GO recorded
- [ ] Cross-referenced to `SPRINT_34/TOOLING_AND_BACKLOG_ANALYSIS.md` + `SPRINT_34/DAY11_PROGRESS_NOTES.md` (the banked-fix rationale) + `SPRINT_34/DAY12_P7_INFRA.md`
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 4: `$149` CES/LES `prod()` Product-Rule Stationarity AD Root Analysis + Uncontrolled-Index Cohort Catalog

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2

### Objective

Localize the `$149` "uncontrolled index" defect to a specific emit/AD surface, hand-derive the correct `stat_pc` cross-term for ganges's CES/LES `prod(j, (pc(j)/pc00(j))**ac(j,r))` term, and catalog exactly which `path_syntax_error` cohort members the fix unblocks — and which carry additional independent roots it does not touch.

### Why This Matters

`$149` is the deepest blocker Sprint 35 owns and the one that gates the most models: **ganges, gangesx, dinam, indus, turkpow, clearlak** all carry it. It is also the one root whose *fix shape* is unknown — S34 Day 11 characterized the symptom (the derivative of a `prod(j, …)` w.r.t. `pc(i)` leaves a free `j` in the emitted `stat_pc`, which GAMS rejects as an uncontrolled index) but did not localize the defect or derive the correction. Doing that analysis inside the sprint would consume the P4 budget and risk a Day-11-style late correction; doing it in prep means P4 Day 1 starts against a derived answer. Equally important is the *cohort catalog*: Sprint 34's fatal prep error was assuming a shared root, and the honest projection for Sprint 35 (P4 delivers +2 Solve, P6 delivers the rest) depends entirely on knowing per-model which roots remain after `$149` is fixed.

### Background

The GAMS `$149` error is "Uncontrolled set entered as constant" — an index appears on the right-hand side of an assignment/equation without being controlled by the equation domain or an enclosing `sum`/`prod`. Product-rule differentiation of `prod(j, f(j))` w.r.t. one element `f(i)` yields `prod(j, f(j)) / f(i) * f'(i)` (or the equivalent `exp(sum(j, log …))` form) — the emitted expression must either bind `j` under a `sum`/`prod` or collapse it; leaving it free is the bug. The standing cross-sprint finding is that these defects live in `src/kkt/stationarity.py` (the stationarity emit) rather than the AD layer proper — `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`) is the general indexed cross-term path — but that must be *verified*, not assumed, per the recurring "prep fix-surfaces are hypotheses" lesson. Cohort roots per `SPRINT_34/DAY11_PROGRESS_NOTES.md`: ganges/gangesx `$141`×15 + `$145`×3 + `$149`×9; dinam/indus `$140` + `$149`; turkpow/clearlak `$149` + `$171`; turkey `$161` (dotted-tuple set declaration; its `$141`/`$257` are cascades).

### What Needs to Be Done

1. **Reproduce `$149` live** — emit ganges (`data/gamslib/raw/ganges.gms`, recursion limit 50000) and compile the golden, capturing the exact offending `stat_pc` line(s) and the free index. Record the emitted text verbatim.
2. **Hand-derive the correct cross-term** — for the CES/LES term `prod(j, (pc(j)/pc00(j))**ac(j,r))`, derive ∂/∂`pc(i)` symbolically (product rule; watch the `**` exponent and the `ac(j,r)` coefficient), and write the *correct* GAMS-emittable form with every index bound. Note both candidate emit forms (explicit `prod` ratio vs `exp(sum(log …))`) and pick one with a rationale.
3. **Localize the defect** — trace the emit path from the `prod()` node through the stationarity builder to the emitted string; identify the `file:line` where the free index is introduced (start at `src/kkt/stationarity.py`, `_add_indexed_jacobian_terms` and the product/power handling; confirm or refute that the AD layer is *not* the surface). Record the finding as a **hypothesis with the evidence that supports it**, per the standing lesson.
4. **Build the cohort catalog** — for each of ganges, gangesx, dinam, indus, turkpow, clearlak, turkey: compile the committed golden, tabulate every distinct `$NNN` error code with its count, and mark which are `$149`-caused vs independent. Explicitly answer: *after a correct `$149` fix, which models still fail and on what?*
5. **Estimate the blast radius** — which other corpus models emit `prod()`/`**` stationarity terms and would therefore traverse the changed path (candidates: the CGE cluster, cesam2, camcge). List them as the regression set the P4 gate must cover.
6. **Write** `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md && echo "analysis doc exists"
# the hand-derived cross-term + the localized fix surface are recorded
grep -icE 'prod\(|product rule|stat_pc|uncontrolled|free index|\$149' docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md
# the fix surface names a concrete file:line hypothesis
grep -icE 'stationarity\.py|_add_indexed_jacobian_terms|index_mapping\.py' docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md
# the cohort catalog covers all seven models and marks residual roots
grep -icE 'ganges|gangesx|dinam|indus|turkpow|clearlak|turkey|\$140|\$141|\$145|\$161|\$171' docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md
# the claimed fix surface exists in the tree
grep -n 'def _add_indexed_jacobian_terms' src/kkt/stationarity.py
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md`
- The verbatim offending `stat_pc` emit line(s) + the identified free index
- The hand-derived correct ∂/∂`pc(i)` cross-term for the CES/LES `prod()` term, in GAMS-emittable form, with the emit-form choice justified
- A `file:line` fix-surface hypothesis with its supporting evidence (explicitly labelled a hypothesis, per the standing lesson)
- The per-model cohort catalog (7 models × distinct `$NNN` codes × counts) answering "what still fails after `$149`"
- The blast-radius regression set (other `prod()`/`**` stationarity models)
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 4 `$149` unknowns + the Category 6 cohort unknowns

### Acceptance Criteria

- [ ] `$149` reproduced live on ganges with the offending emit line captured verbatim
- [ ] The correct cross-term hand-derived and written in a GAMS-emittable, fully-index-bound form
- [ ] The fix surface localized to a `file:line` and labelled explicitly as a hypothesis with its evidence
- [ ] All seven cohort models compiled and catalogued by distinct error code with counts
- [ ] "Which models still fail after `$149`, and on what" answered per model (the multi-root discipline)
- [ ] The blast-radius regression set enumerated for the P4 acceptance gate
- [ ] Cross-referenced to `SPRINT_34/DAY11_PROGRESS_NOTES.md` + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` §4
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 5: ganges/gangesx Multi-Root Recovery Design (Priority 4 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 3, 4

### Objective

Design the Priority-4 recovery as an ordered, individually-gated sequence of three independent root fixes (`$141` re-apply → `$145` universal-set skip → `$149` product-rule correction) plus turkey's separate `$161`, with a per-model verification protocol and a golden-regeneration plan that lets the fixes actually ship.

### Why This Matters

P4 is Sprint 35's **designated best-shot bucket mover**: +2 Solve / +2 Match / −2 path_syntax_error (and +2 genuine floor if ganges/gangesx cold-match), against three deep tracks whose priors are all "no bucket". It is also the track with the most specific inheritance — one root already written and verified, one narrowly characterized, one derived in Task 4. What it lacks is a *sequencing and shipping* plan: S34 proved that fixing one root recovers nothing (so partial landings show no bucket movement and can look like failure), and that the goldens are the binding operational constraint. The design must therefore state up front what "progress" looks like after each root, and how the three land as a coherent unit.

### Background

Per `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` §4 and `DAY11_PROGRESS_NOTES.md`:
- **`$141`** (×15 on ganges) — the Issue-#1322 NaN-cleanup pass emits a self-referential guard `param(i)$(NOT(param(i) > -inf …)) = 0` over `.l`-referencing calibration params (`adst(i) = dst.l(i)/…`) whose assignment is presolve-gated (`src/emit/emit_gams.py:2730`), so in the cold MCP they are declared-but-unassigned. **Fix written + verified + reverted:** skip `.l`-attribute-referencing params in `emit_post_assignment_na_cleanup` (`src/emit/original_symbols.py:152`) via a `_param_assignment_references_varref_attr` helper mirroring `_param_assignment_has_division` (`:137`).
- **`$145`** (×3) — a separate NaN-cleanup gap over a universal-set (`*`) domain param (`series(*,years)`).
- **`$149`** (×9) — the deep product-rule stationarity defect analysed in Task 4.
- **turkey `$161`** — a dotted-tuple set-declaration emit root; its `$141`/`$257` are cascades of it.

### What Needs to Be Done

1. **Re-validate the banked `$141` fix against the current tree** — confirm the helper still applies cleanly at `src/emit/original_symbols.py` (the `_param_assignment_has_division` sibling is still at `:137`, `emit_post_assignment_na_cleanup` at `:152`), and re-verify it removes all 15 `$141` from the ganges emit. Record any drift since S34 Day 11.
2. **Design the `$145` universal-set skip** — specify how the cleanup pass should treat a `*`-domain parameter (skip vs guard-with-domain), where in `emit_post_assignment_na_cleanup` the branch belongs, and what the minimal reproducing shape is.
3. **Specify the `$149` correction** from Task 4's derivation — the concrete emit change at the localized `file:line`, the index-binding it introduces, and the hand-derived cross-term it must reproduce.
4. **Order the landings and gate each one** — `$141` → `$145` → `$149` (cheapest-and-verified first, deepest last), each with its own `--resolve-changed --since-commit <S34-close>` run and its own golden refresh. State the expected *bucket* outcome after each step (explicitly: **no bucket movement is expected until all three land** — the S34 finding), so a mid-sequence flat KPI is not misread as failure.
5. **Define the per-model verification protocol** — for ganges and gangesx independently (never inferred from one another): emit → compile → count residual `$NNN` → solve → bucket → match. The multi-root discipline is the deliverable, not a note.
6. **Fold in the golden-regeneration plan from Task 3** — which models regenerate, in what window, with determinism ×3, and the `--resolve-changed` re-solve afterwards.
7. **Scope turkey's `$161`** as a separate, smaller item with its own gate (and its own decision on whether it belongs in P4 or P6).
8. **Name the REPLAN exit** — what evidence would say the `$149` correction is out of reach in-sprint (e.g. the derivation implies a general AD-core restructure), and where the budget goes if so (→ P6/P7).
9. **Write** `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md && echo "design doc exists"
# all three roots + turkey are sequenced and individually gated
grep -icE '\$141|\$145|\$149|\$161|resolve-changed|per-model|multi-root' docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md
# the banked-fix surfaces still exist where the design says they do
grep -n 'def emit_post_assignment_na_cleanup\|def _param_assignment_has_division' src/emit/original_symbols.py
# the golden-regeneration plan is carried over from Task 3
grep -icE 'regen|golden|PYTHONHASHSEED|determinism' docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md
# the REPLAN exit is explicit
grep -icE 'REPLAN|exit|reallocat' docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md`
- The re-validated `$141` fix (clean-apply confirmation + the 15-error removal re-verified against the current tree)
- The `$145` universal-set skip design + its minimal reproducing shape
- The `$149` correction specification derived from Task 4 (concrete emit change at the localized `file:line`)
- The ordered, individually-`--resolve-changed`-gated landing sequence with the expected per-step bucket outcome (explicitly: no movement until all three land)
- The per-model (ganges *and* gangesx, independently) verification protocol
- The golden-regeneration plan folded in from Task 3
- turkey `$161` scoped as a separate item with its own gate and P4/P6 placement decision
- The named REPLAN exit + budget reallocation target
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 4 unknowns

### Acceptance Criteria

- [ ] The banked `$141` fix re-validated against the current tree (clean apply + 15 `$141` removed)
- [ ] The `$145` universal-set skip designed with a concrete branch location
- [ ] The `$149` correction specified from Task 4's hand-derived cross-term
- [ ] The three roots ordered with a per-root `--resolve-changed` gate and per-step expected bucket outcome
- [ ] "No bucket movement until all three land" stated explicitly so a mid-sequence flat KPI is not misread
- [ ] The per-model verification protocol defined for ganges and gangesx independently (multi-root discipline)
- [ ] The golden-regeneration plan (window, determinism ×3, follow-on re-solve) folded in from Task 3
- [ ] turkey `$161` scoped separately with a P4/P6 placement decision
- [ ] An explicit REPLAN exit + budget reallocation target named
- [ ] Cross-referenced to `SPRINT_34/DAY11_PROGRESS_NOTES.md` + Task 4's analysis + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md` §4
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 6: mine Head-Offset Dual-Architecture Design (Priority 1 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 6–8 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2

### Objective

Turn the Sprint-34 Day-1 refutation (H_dual is value-invariant; the head-offset dual boundary is **`x.m = 0`-degenerate**) into either a concrete head-offset dual-architecture design that can reach **cold MS-1 @ 17500**, or an explicitly-argued conclusion that no emit-side architecture can — in which case the track's disposition (deeper architecture vs the PATH-consultation hand-off) is decided in prep rather than on Day 3.

### Why This Matters

P1 is Sprint 35's largest single budget line (18–24h) and its highest REPLAN prior: mine is **four-times-carried** (S32 → S33 → S34 → S35) and each sprint has refuted the then-current hypothesis with a control before shipping anything. S33 proved H1 head-label re-keying is value-invariant (22 → 22 nonzero rows); S34 proved the same of H_dual on the *cold* solve (both MS-5, profit 16747.0723, 51 INFES) and established that closing the residual needs a contribution neither a keying change (sign flip **BANNED**) nor a bound multiplier (`x.m = 0`) can supply. Spending 18–24h of sprint budget on a fifth hypothesis without first asking, in prep, whether the boundary is reachable at all would be the least defensible allocation in the plan. The honest outcome of this task may be "REPLAN before Day 1" — and that is a *successful* result, freeing budget to P4.

### Background

`SPRINT_34/DAY1_PROGRESS_NOTES.md` (the H_dual cold-MS-1 control), `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` §§3.2/4/5 (the boundary needs +16000, unreachable without the banned sign flip or an unavailable bound multiplier), `SPRINT_33/MINE_CROSSTERM_DESIGN.md` + `DAY2_MINE_REPLAN.md` (H1 value-invariance), `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`. The IR foundation is `EquationDef.head_domain_offsets` (S31): a per-position `IndexOffset|None` tuple aligned to the declaration domain, with `has_head_domain_offset` derived in `__post_init__`. The physical situation: the NLP stores `pr.m` at the *shifted* head label `(k,l+1,i,j)` while `lam_pr` pairs at the base `(k,l,i,j)`. The LP primal is feasible/optimal at 17500 (mine NLP MS-1), so the MCP failure is a genuine dual degeneracy. Standing BANs: the objective-gradient sign flip; `x.up=inf` as a measurement device (always assert `modelstat`).

### What Needs to Be Done

1. **Re-state the refutation precisely** — what S33 and S34 each proved, and what specifically remains unrefuted. Distinguish "this keying is value-invariant" from "no emit change can move the boundary".
2. **Characterize the degeneracy formally** — at the bound-active `stat_x` rows, write the stationarity identity with every available multiplier (`piU_x`, `piL_x`, `lam_pr`, the precedence duals) and show which terms are structurally zero when `x.m = 0`. Quantify the gap (the design's +16000) against what each candidate contribution could supply.
3. **Enumerate the candidate architectures** — for each, state the emit change, the IR support it needs from `head_domain_offsets`, and the mechanism by which it supplies the missing contribution. Candidates to consider at minimum: (a) an explicit head-offset dual variable paired at the shifted label; (b) a reformulation of the precedence constraint so its dual lands at the base label; (c) an augmented complementarity pairing that keeps both labels' multipliers live; (d) an LP-side reformulation upstream of emit.
4. **Score each candidate against the reachability question** — can it, in principle, supply the +16000 without the banned sign flip? Reject the ones that cannot, on the record.
5. **Design the surviving candidate (if any) to `file:line`** — the emit change in `src/kkt/stationarity.py`, the IR reads from `head_domain_offsets`, and the interior-row invariance argument (unchanged 0 at interior rows).
6. **Specify the pre-`src/` `/tmp` control** — the reformulation must drive the warm residual → 0 at **all** bound-active rows AND leave interior rows at 0, **then** cold/presolve MS-1 @ 17500, with `modelstat` asserted every time. This is the Phase-0 gate Task 10 will formalize.
7. **If no candidate survives, write the REPLAN recommendation** — the disposition (deeper architecture in a later sprint vs the Sprint-36 PATH-consultation track as "an LP whose warm KKT point is not MCP-reconcilable"), and the freed-budget target (→ P4/P6/P7).
8. **Write** `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md && echo "design doc exists"
# the refutation history + the degeneracy characterization are present
grep -icE 'H1|H_dual|value-invariant|x\.m *= *0|degener|17500|16747' docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md
# candidate architectures are enumerated and scored
grep -icE 'candidate|reachab|piU_x|piL_x|lam_pr|head_domain_offsets' docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md
# the standing BANs are restated
grep -icE 'BANNED|sign flip|x\.up=inf|modelstat' docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md
# the IR foundation still exists as described
grep -rn 'head_domain_offsets' src/ir/*.py | head -3
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`
- A precise restatement of what S33/S34 refuted vs what remains open
- The formal degeneracy characterization at the bound-active `stat_x` rows, with the quantified gap
- The enumerated candidate architectures, each scored on reachability, with rejections recorded
- Either a `file:line` design for the surviving candidate (emit change + IR reads + interior-row invariance) **or** a written REPLAN recommendation with its disposition and freed-budget target
- The pre-`src/` `/tmp` control specification (all-bound-active residual → 0, interior rows unchanged, then cold MS-1 @ 17500, `modelstat` asserted)
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 1 unknowns

### Acceptance Criteria

- [ ] The S33/S34 refutations restated precisely, separating "this keying is invariant" from "no emit change suffices"
- [ ] The `x.m = 0` degeneracy characterized formally with the quantified boundary gap
- [ ] ≥ 4 candidate architectures enumerated and each scored on whether it can supply the missing contribution
- [ ] A `file:line` design for the surviving candidate **or** an explicit, argued REPLAN recommendation (either is an acceptable outcome)
- [ ] The pre-`src/` `/tmp` control specified with `modelstat` asserted and the interior-row invariance requirement
- [ ] The standing BANs restated (objective-gradient sign flip; `x.up=inf` measurement)
- [ ] Cross-referenced to `SPRINT_34/DAY1_PROGRESS_NOTES.md`, `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md`, `SPRINT_33/MINE_CROSSTERM_DESIGN.md`, `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 7: sarf Symbolic/Parametric Emit-Mode Re-Architecture Design (Priority 2 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 5–7 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2

### Objective

Design the symbolic/parametric emit mode that stops materializing sarf's 369,024 `task(g,t,mn,mn)` columns at all three sites atomically — including the corpus-wide safety argument for changing `enumerate_variable_instances`, which every one of the 142 models traverses — and the full-corpus regression harness that makes the change shippable.

### Why This Matters

P2 is the second-largest budget line (20–28h) for the **lowest-leverage** bucket (+1 Translate — it moves neither Solve nor Match). It has been deferred in three consecutive sprints on exactly that risk/reward basis, and S34 Day 6 sharpened *why*: `enumerate_variable_instances` (`src/ad/index_mapping.py:327`) builds the `col_to_var` index that the whole Jacobian → gradient → stationarity flow iterates for **all 142 models**, so this is not a gated add-on but a coordinated re-architecture with corpus-wide blast radius. There is no safe partial landing (gated constraints emit zero per-instance Jacobian entries, so the cross-terms must come from a new parametric path that does not exist today). A prep design that cannot articulate the corpus-safety argument and the regression harness is a design that should not be implemented — and saying so before Day 1 is worth more than discovering it on Day 7 for the fourth time.

### Background

`SPRINT_34/DAY6_PROGRESS_NOTES.md` (the three-site re-confirmation + the foundational finding), `SPRINT_34/SARF_EMIT_MODE_DESIGN.md`, `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` (the 7-term `stat_task` derivation), `SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` + `SARF_TRANSLATE_REPLAN.md`. The three sites: **S1** `acost3` scalar body-diff in `compute_constraint_jacobian`; **S2** `enumerate_variable_instances` materializing the 369,024 columns (called per-variable from `build_index_mapping`); **S3** the per-column `stat_task` stationarity. The active subset (`taskposs ∧ tech` = 398) is **not statically enumerable** (`taskposs` is runtime-computed), so the target emit is one guarded `stat_task(g,t,m,n)$taskposs` + `task.fx(...)$(not (...)) = 0`, letting GAMS instantiate the live rows. Only an **equation**-level blow-up gate exists today (`_is_blowup_dynamic_subset_equation`); there is no variable-level gate. Reference: `docs/research/multidimensional_indexing.md`.

### What Needs to Be Done

1. **Re-confirm the three sites at Day 0 scope** — verify S1/S2/S3 are still the complete set (S34 Day 6 found no fourth, but this is a re-confirm hypothesis) and that the 369,024 = 16·24·31·31 Cartesian and the 398 active count still hold.
2. **Design the symbolic-column concept** — how a variable can present as a *symbolic* column (a domain expression + a guard) rather than an enumerated instance list, and what `col_to_var` becomes for such variables.
3. **Make the corpus-safety argument explicit** — how the other 141 models' `col_to_var` construction and ordering stay byte-identical (determinism is a hard requirement, PR12), and which code paths must branch on symbolic-vs-enumerated.
4. **Design the parametric cross-term path** — the new path that produces `stat_task`'s cross-terms without per-instance Jacobian entries, checked against the banked 7-term derivation, with every index bound and no set-name-literal indices.
5. **Specify the guarded emit** — `stat_task(g,t,m,n)$taskposs` + the `task.fx$(not active) = 0` companion + the MCP matching, and argue it yields exactly the 398 live rows.
6. **Specify the tractability gate** — the re-emit must be **O(active = 398), not O(369K)**: time `sarf_mcp.gms` emission (target: seconds; the current failure is > 75s), with the measurement method pinned.
7. **Specify the full-corpus regression harness** — the atomic-landing requirement, the byte-stable golden expectation for all 141 other models, determinism ×3 (`PYTHONHASHSEED` {0,1,42}), and the `--resolve-changed` full-corpus run.
8. **Name the REPLAN exit** — a fourth enumeration site, a determinism break, any non-byte-stable golden on an unrelated model, or a re-triggered timeout → re-scope and hand off, with the freed budget going to P4/P6.
9. **Write** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md && echo "design doc exists"
# all three sites + the counts are covered
grep -icE 'S1|S2|S3|acost3|enumerate_variable_instances|stat_task|369,?024|398|taskposs' docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md
# the corpus-safety + regression-harness arguments are present
grep -icE 'col_to_var|142|141|byte-stable|determinism|PYTHONHASHSEED|resolve-changed|atomic' docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md
# the tractability gate is quantified
grep -icE 'O\(active|75s|seconds|timing|tractab' docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md
# the foundational function still exists where the design says it does
grep -n 'def enumerate_variable_instances' src/ad/index_mapping.py
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md`
- The S1/S2/S3 re-confirmation (or a corrected site list) with the 369,024 / 398 counts re-verified
- The symbolic-column design + what `col_to_var` becomes for symbolic variables
- The corpus-safety argument (141 other models byte-identical; determinism preserved) with the branching code paths named
- The parametric cross-term path checked against the banked 7-term `stat_task` derivation
- The guarded emit specification (`$taskposs` + `task.fx` companion + MCP matching → exactly 398 live rows)
- The quantified tractability gate (O(active) vs the > 75s failure) with its measurement method
- The full-corpus regression harness specification (atomic landing, byte-stable goldens, determinism ×3, `--resolve-changed`)
- The named REPLAN exit + freed-budget target
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 2 unknowns

### Acceptance Criteria

- [ ] The three sites re-confirmed (or corrected) with the Cartesian and active counts re-verified
- [ ] The symbolic-column concept designed, including the `col_to_var` representation
- [ ] The corpus-safety argument made explicitly for the other 141 models, with determinism preserved
- [ ] The parametric cross-term path designed and checked against the banked 7-term derivation
- [ ] The guarded emit specified and argued to produce exactly the 398 live rows
- [ ] The tractability gate quantified (seconds, not > 75s) with a pinned measurement method
- [ ] The full-corpus regression harness specified (atomic, byte-stable, determinism ×3, `--resolve-changed`)
- [ ] A REPLAN exit named (4th site / determinism break / golden churn / re-triggered timeout) with the freed-budget target
- [ ] Cross-referenced to `SPRINT_34/DAY6_PROGRESS_NOTES.md`, `SPRINT_34/SARF_EMIT_MODE_DESIGN.md`, `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`, `docs/research/multidimensional_indexing.md`
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 8: fawley Constraint-Index-Diagonal Correction + Forcing Hand-Off Design (Priority 3 foundation)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Tasks 1, 2

### Objective

Design the genuine constraint-index-diagonal `sameas` cross-term correction inside `_add_indexed_jacobian_terms` — leak-free against the shared 2-D cohort (mbal, cesam2, camcge, ps2) and the 1-D core (polygon, ps2/ps3) — together with the explicit forcing hand-off for fawley's H-b +Solve, so the correctness win and the (non-emit) solve win are not conflated.

### Why This Matters

P3 is the clearest example in the sprint of a **genuine correctness fix whose bucket value is contingent**. S34 Day 5 re-confirmed the gap is real (adding `$(sameas(cfq__,cf))` takes `max|stat_bq|` from 473 to 18.468) *and* that fawley is **H-b**: with the sameas correction plus all bound transfers, the warm residual goes to ~0 but the MCP still solves **MS-5 @ 4399.557** against an LP optimum of 2899.25. So the +Solve is a forcing problem, not an emit problem. The design must therefore deliver two separable things — a shippable, regression-safe cross-term correction (which can lift the genuine floor if fawley cold-matches) and a forcing hand-off — and the prep must make the separation explicit so the sprint does not spend P3 budget chasing a solve that P3 cannot produce. The fix surface itself is the risk: a ~1430-line general emit function with a dozen issue-specific `sameas` paths, shared with models that currently pass.

### Background

`SPRINT_34/DAY5_PROGRESS_NOTES.md` (the H-b finding + the fix-surface examination), `SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` §6 (the gate-leak REPLAN exit), `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` + `DAY4_FAWLEY_CONTROL.md` / `DAY5_FAWLEY_CLOSE.md`. The gap: mbal carries `$(sameas(cfq__,cf))` while qsb/pbal over-sum (`data/gamslib/mcp/fawley_mcp.gms:238`). The fix surface is `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`), which also carries the #1104/#1111 offset-group / fresh-alias machinery. The constraint-index diagonal is a genuinely new pattern: the existing #1049 guard fires only when the variable has *more* dimensions than the constraint; qsb is the opposite orientation. The `--force {homotopy,multistart,optfile}` scaffold (`src/cli.py`) is the forcing lever; the survey precedent is `SPRINT_30/NONCONVEX_FORCING_SURVEY.md`.

### What Needs to Be Done

1. **Re-confirm the gap and the H-b finding at Day 0 scope** — `max|stat_bq|` 473 → 18.468 with the sameas guard; MS-5 @ 4399.557 persisting with the residual closed; LP optimum 2899.25.
2. **Characterize the constraint-index diagonal precisely** — the index orientation (constraint dimension ≥ variable dimension) that distinguishes it from the #1049 guard, expressed as a predicate over the emit-time index structures.
3. **Design the guard** — where in `_add_indexed_jacobian_terms` the diagonal predicate belongs relative to the existing dozen `sameas` paths, and the precedence argument against each of them (which is the leak risk).
4. **Define the leak-free requirement operationally** — **no mbal term may change**, and the 1-D core (polygon, ps2, ps3) must be byte-identical; enumerate the 2-D cohort (mbal, cesam2, camcge, ps2) as the regression set and specify the harness.
5. **Specify the pre-`src/` `/tmp` control** — the generalization must drive `max|stat_bq| → 0` (not 96%, i.e. not merely 473 → 18.468), with `modelstat` asserted, before any `src/` change.
6. **Design the fawley 2-D second-index property fixture** — fail-before/pass-after, landing with the correction (the P7 catalog entry from Task 3).
7. **Specify the forcing hand-off** — which `--force` levers to survey for fawley's MS-5, what evidence would make the +Solve reachable, and the explicit statement that the +Solve is **not** an in-sprint P3 deliverable (it is a forcing tail; the floor +1 is contingent on a cold match).
8. **Name the REPLAN exit** — a gate leak (any mbal/1-D change), or `max|stat_bq|` not reaching 0 → defer again with the fix surface further characterized, budget to P4/P6.
9. **Write** `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md && echo "design doc exists"
# the H-b separation of correctness vs +Solve is explicit
grep -icE 'H-b|forcing|4399|2899|18\.468|473|MS-5' docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md
# the leak-free requirement names the shared cohort
grep -icE 'mbal|cesam2|camcge|ps2|ps3|polygon|byte-identical|#1049' docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md
# the fix surface still exists where the design says it does
grep -n 'def _add_indexed_jacobian_terms' src/kkt/stationarity.py
# the fawley golden line the gap was localized at
grep -n 'sameas' data/gamslib/mcp/fawley_mcp.gms | head -5
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`
- The Day-0 re-confirmation of the gap (473 → 18.468) and the H-b finding (MS-5 @ 4399.557 with the residual closed)
- The constraint-index-diagonal predicate, distinguished explicitly from the #1049 guard orientation
- The guard design with its placement + precedence argument against the existing `sameas` paths
- The operational leak-free requirement (no mbal term change; 1-D core byte-identical) + the 2-D-cohort regression harness
- The pre-`src/` `/tmp` control specification (`max|stat_bq| → 0`, `modelstat` asserted)
- The fawley 2-D second-index property fixture design (fail-before/pass-after)
- The forcing hand-off specification, with the +Solve explicitly excluded from P3's in-sprint deliverables
- The named REPLAN exit + budget reallocation target
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 3 unknowns

### Acceptance Criteria

- [ ] The gap and the H-b finding re-confirmed with their exact figures
- [ ] The constraint-index diagonal characterized as a predicate and distinguished from #1049
- [ ] The guard placement designed with a precedence argument against each existing `sameas` path
- [ ] The leak-free requirement stated operationally (no mbal change; 1-D core byte-identical) with the regression cohort enumerated
- [ ] The pre-`src/` `/tmp` control specified (`max|stat_bq| → 0`, not 96%; `modelstat` asserted)
- [ ] The fawley 2-D fixture designed as fail-before/pass-after
- [ ] The forcing hand-off specified and the +Solve explicitly excluded from P3's in-sprint scope (H-b)
- [ ] A REPLAN exit named (gate leak / residual not reaching 0) with the freed-budget target
- [ ] Cross-referenced to `SPRINT_34/DAY5_PROGRESS_NOTES.md`, `SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` §6, `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 9: camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Development team
**Dependencies:** Task 1

### Objective

Specify the camcge dual-consistent Walras redefinition as an Epic-5 `/tmp` prototype with an MS-1 gate, and produce the submission plan that delivers the FINALIZED rocket PATH-consultation input to the **Sprint-36** consultation (note the renumbering — the consultation sprint moved from 35 to 36 in the Sprint-35 insertion).

### Why This Matters

P5 is the sprint's explicitly *non-KPI* priority: camcge is Epic-5-scoped (its +Solve is not an in-sprint commitment) and rocket is a hand-off (no emit fix — the Case-c sign flip is **BANNED**, control-refuted four times). Its prep value is in preventing two specific failure modes. First, camcge has consumed prep and execution budget in three sprints on a target (MS-1) that the banked price-pin variant demonstrably does not reach — so the design must state the Epic-5 gate crisply and the per-model-numéraire fallback that counts as a successful finding. Second, the rocket submission has a **renumbering hazard**: the input was authored for "the Sprint-35 consultation" and the consultation is now Sprint 36; a submission plan that carries the stale reference will confuse the hand-off.

### Background

`SPRINT_34/DAY10_PROGRESS_NOTES.md` (the S1∧S2∧S3 detector cohort confirmed live: camcge cold **MS-4** at NLP objective / omega **191.7346**; the four CGE siblings irscge/lrgcge/moncge/stdcge cold **MS-1** — so the detector's cold-singular false-positive guard holds), `SPRINT_34/CAMCGE_ROCKET_PLAN.md`, `SPRINT_33/CAMCGE_WALRAS_DESIGN.md`, `SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` + `CAMCGE_WALRAS_REPLAN.md`, `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`. Step 1 (the scalar-`fx` `nu_mps_fx` marginal transfer → `stat_mps` Case-a) landed in S32. The banked price-pin numéraire variant reaches the correct primal (omega 191.7346) but stays MS-4 (INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`). For rocket: `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` is FINALIZED (the concrete question + the ruled-out-lever survey + the two-command reproducer + the `--force` scaffold); `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` and `SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 hold the survey. rocket's Case-c signature: CASE_C_OBJDEF, boundary `stat_ht(h0)` 1.00 / `stat_step` 0.497 / `stat_ht(h50)` 0.438, dual CONSISTENT 1.53e-10.

### What Needs to Be Done

1. **Specify the full dual-consistent Walras redefinition** — keep every market-clearing row, add the consumption-weighted numéraire, and redefine the redundant market's dual via Walras' law so the reduced system is full-rank while the multiplier stays available.
2. **Define the Epic-5 `/tmp` gate** — the prototype must reach **MS-1** (not merely the correct primal at omega 191.7346, which the price-pin variant already achieves at MS-4), with `modelstat` asserted and the INFES rows (`gdp`, `depreq`, `hhsaveq`, `gruse`) tracked.
3. **Define the acceptable fallback finding** — the per-model-numéraire Epic-5 result, so a non-MS-1 outcome is a documented deliverable rather than a failure.
4. **Re-confirm the degeneracy-detector scope** — S1∧S2∧S3 fires only on camcge; the four CGE siblings stay cold MS-1 (the false-positive guard).
5. **Write the rocket submission plan** — the recipient(s), the artifact bundle (the FINALIZED input + the reproducible case + the `--force` scaffold + the ruled-out-lever survey), the tracking mechanism for the response, and — explicitly — that the destination is the **Sprint-36** "PATH Author Consultation & Solution Forcing" sprint. Note any stale "Sprint 35" references in the banked input that must be updated at submission time.
6. **Restate the standing BAN** — the rocket Case-c objective-gradient sign flip stays BANNED; no re-litigation.
7. **Write** `docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md && echo "plan doc exists"
# the Epic-5 MS-1 gate + the fallback finding are both specified
grep -icE 'MS-1|MS-4|191\.7346|Walras|numéraire|numeraire|Epic 5|fallback' docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md
# the rocket submission targets Sprint 36 (not the stale 35) and restates the BAN
grep -icE 'Sprint 36|Sprint-36' docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md
grep -icE 'BANNED|sign flip|CASE_C_OBJDEF' docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md
# the banked rocket input exists to be submitted
test -f docs/planning/EPIC_4/SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md && echo "rocket input present"
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/CAMCGE_ROCKET_PLAN.md`
- The full dual-consistent Walras redefinition specification (market rows + consumption-weighted numéraire + the Walras-law dual redefinition)
- The Epic-5 `/tmp` MS-1 gate with `modelstat` asserted and the INFES rows tracked
- The per-model-numéraire fallback defined as an acceptable Epic-5 finding
- The degeneracy-detector scope re-confirmation (fires only camcge; siblings cold MS-1)
- The rocket submission plan (recipients, artifact bundle, response tracking) targeting the **Sprint-36** consultation, with any stale "Sprint 35" references in the banked input flagged for update
- The restated Case-c sign-flip BAN
- Updated `KNOWN_UNKNOWNS.md` with verification results for the Category 5 unknowns

### Acceptance Criteria

- [ ] The Walras redefinition specified in full (rows kept, numéraire, dual redefinition)
- [ ] The Epic-5 gate stated as **MS-1** (explicitly distinguished from the price-pin variant's correct-primal-at-MS-4 result), with `modelstat` asserted
- [ ] The per-model-numéraire fallback defined as a successful Epic-5 outcome
- [ ] The detector scope re-confirmed (camcge only; four siblings cold MS-1)
- [ ] The rocket submission plan complete, targeting **Sprint 36**, with stale "Sprint 35" references in the banked input flagged
- [ ] The Case-c sign-flip BAN restated with no re-litigation path
- [ ] camcge explicitly excluded from the in-sprint Solve commitment (Epic-5-scoped)
- [ ] Cross-referenced to `SPRINT_34/DAY10_PROGRESS_NOTES.md`, `SPRINT_33/CAMCGE_WALRAS_DESIGN.md`, `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 10: Author Phase 0 Acceptance Gates for the Sprint-35 Tracks (PR20 + PR24 + PR27)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 4, 5, 6, 7, 8, 9

### Objective

Consolidate the per-track `/tmp` controls from Tasks 4–9 into a single `PHASE_0_ACCEPTANCE_GATES.md` — one gate per track, each with a measurable PROCEED/REPLAN criterion evaluated **before** any `src/` change, and each asserting `modelstat` wherever a solve result is read.

### Why This Matters

This is the discipline that has produced Sprint 32/33/34's defining outcome: **zero broken code shipped across three sprints of deep architectural work**, because every premise was refuted or confirmed by a control experiment first. It is also the guard against the specific measurement error that has bitten before — reading an objective off a solve without asserting `modelstat` (the S31 Day-2 `x.up=inf` error, which read the embedded LP instead of the MCP and produced 34 spurious unmatched-var errors). Sprint 35's tracks each have a distinct gate shape (P1 a cold-MS-1 boundary; P2 a *timing* budget; P3 a residual-magnitude threshold with a leak check; P4 a per-root compile-and-bucket sequence; P5 an Epic-5 MS-1 prototype), so a single consolidated document is what makes them uniformly enforceable on the day.

### Background

`SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` is the template; `SPRINT_33/PHASE_0_ACCEPTANCE_GATES.md` and `SPRINT_32/PHASE_0_ACCEPTANCE_GATES.md` are the precedents. The standing rules: PR20 (a tractability/emit-budget gate where performance is the failure mode), PR24 (control experiment before high-blast-radius `src/`), PR27 (the single-point KKT-residual harness is systematically misleading for non-convex / objective-defining-intermediate-variable shapes — pair it with a solve-status assertion). The harness is `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`); the no-regression gate is `run_full_test.py --resolve-changed --since-commit <S34-close>`.

### What Needs to Be Done

1. **P1 (mine) gate** — the reformulation must drive the warm residual → 0 at **all** bound-active `stat_x` rows AND leave interior rows unchanged at 0 in a `/tmp` control, **then** reach cold/presolve **MS-1 @ 17500**; `modelstat` asserted at every read; `x.up=inf` **BANNED**. PROCEED/REPLAN stated. (If Task 6 returned a REPLAN recommendation, record the gate as pre-refuted and the exit as taken.)
2. **P2 (sarf) gate** — the re-emit must be **O(active = 398), not O(369K)**: timed `sarf_mcp.gms` emission in seconds (current failure > 75s); `stat_task` verified against the banked 7-term derivation; atomic landing; byte-stable goldens for the other 141 models; determinism ×3; full-corpus `--resolve-changed`.
3. **P3 (fawley) gate** — the generalization must drive `max|stat_bq| → 0` (not 96% / not merely 473 → 18.468) in a `/tmp` control; `--resolve-changed --since-commit <S34-close>` GO with **no mbal-term change** and no 1-D polygon/ps2/ps3 regression; the +Solve explicitly out of scope (H-b → forcing).
4. **P4 (ganges/gangesx) gate** — per-root: each of `$141`/`$145`/`$149` individually `--resolve-changed`-gated; the `$149` correction verified against the Task-4 hand-derived `stat_pc` cross-term in a `/tmp` control **before** `src/`; the slow-emit CGE goldens regenerated per the Task-3 budget + determinism ×3; per-model (ganges and gangesx independently) compile → residual-code count → solve → bucket → match.
5. **P5 (camcge) gate** — the Walras `/tmp` prototype at **MS-1** with `modelstat` asserted (the Epic-5 gate), plus the per-model-numéraire fallback as the documented alternative outcome; rocket's submission has no solve gate (it is a hand-off).
6. **Add the cross-cutting gates** — determinism ×3 (`PYTHONHASHSEED` {0,1,42}, PR12); the golden-staleness check (PR26); the presolve-divergence detector; the "no bucket → no `src/`" shipping rule, with the S34 P4 exception criteria (fast, regenerable goldens + `--resolve-changed` GO) written out, since P4 is *expected* to invoke it.
7. **Write** `docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md && echo "gates doc exists"
# one gate per track, each with PROCEED/REPLAN
grep -cE '^#+ .*(P1|P2|P3|P4|P5)' docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
grep -icE 'PROCEED|REPLAN' docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
# modelstat is asserted wherever a solve is read, and the BANs are restated
grep -icE 'modelstat|BANNED|x\.up=inf|sign flip' docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
# the cross-cutting gates are present
grep -icE 'PYTHONHASHSEED|determinism|golden-staleness|presolve-divergence|resolve-changed|no bucket' docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/PHASE_0_ACCEPTANCE_GATES.md` with one gate per track (P1–P5)
- Each gate: the control to run, the measurable threshold, the PROCEED/REPLAN criterion, and the `modelstat` assertion requirement
- The P2 timing gate (O(active = 398), seconds not > 75s) and the P4 per-root gate sequence stated as first-class, distinct gate shapes
- The cross-cutting gates: determinism ×3 (PR12), golden-staleness (PR26), presolve-divergence, `--resolve-changed` (anchor = S34 close)
- The "no bucket → no `src/`" rule with the S34-P4 exception criteria written out for P4's expected use
- Updated `KNOWN_UNKNOWNS.md` with verification results for the gate-related unknowns

### Acceptance Criteria

- [ ] A gate authored for each of P1, P2, P3, P4, P5 with a measurable PROCEED/REPLAN criterion
- [ ] Every gate that reads a solve result requires `modelstat` to be asserted
- [ ] The standing BANs restated (mine `x.up=inf`; Case-c sign flip)
- [ ] The P2 gate is a **timing** budget (O(active)) and the P4 gate is a **per-root** sequence — not generic residual gates
- [ ] The P3 gate excludes the +Solve (H-b) and requires no mbal/1-D change
- [ ] Cross-cutting gates included: determinism ×3, golden-staleness, presolve-divergence, `--resolve-changed` against the S34-close anchor
- [ ] The "no bucket → no `src/`" rule and its exception criteria written out for P4
- [ ] Cross-referenced to `SPRINT_34/PHASE_0_ACCEPTANCE_GATES.md` and Tasks 4–9's design docs
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 11: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment + Honest KPI Projection (PR16)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 4–6 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 5, 6, 7, 8, 10

### Objective

Apply the PR16 hypothesis-validation methodology to the four deep/new tracks — P1 (mine dual architecture), P2 (sarf re-architecture), P3 (fawley gate-leak / H-b), P4 (ganges `$149` depth) — pinning per-track REPLAN priors with their refuting evidence, the freed-budget reallocation, the front-load ordering, and the honest projection of which KPI buckets can actually move.

### Why This Matters

This projection has been accurate to the bucket for two consecutive sprints, and naming the modal outcome up front is what has kept those sprints focused on de-risking and banking rather than forcing a bad ship. Sprint 35 needs it more than either predecessor, because the historical record is now unambiguous: mine, sarf, and fawley have between them consumed roughly half of three sprints' budget and moved **zero** buckets, while the failure-cohort track produced the only genuine move in that window. An honest assessment likely concludes that **P4 is the sprint's designated best shot** and should be scheduled accordingly — which is a scheduling decision, and therefore has to be made here, before Task 12 lays out the days.

### Background

`SPRINT_34/REPLAN_RISK_ASSESSMENT.md` is the template (its modal-flat projection was borne out exactly — 0 bucket moves); `SPRINT_33/REPLAN_RISK_ASSESSMENT.md` and `SPRINT_34/SPRINT_RETROSPECTIVE.md` §§1/3 hold the outcome record. `PROJECT_PLAN.md` §"Sprint 35" Risk Level is **HIGH**, and enumerates the REPLAN exits per priority. Historical priors: P1 mine High (now four-times-carried, three hypotheses refuted); P2 sarf Medium-High (a failed-architecture rebuild, lowest-leverage bucket); P3 fawley Medium correctness / +Solve is a forcing hand-off (H-b confirmed); P4 is new-to-first-class but carries one already-verified root and one AD-core unknown.

### What Needs to Be Done

1. **Assess each of P1/P2/P3/P4 for REPLAN probability**, naming the specific evidence that would refute it and the earliest day that evidence surfaces (Day-5 checkpoint measurability is the requirement). Weigh the carry count explicitly (mine ×4, sarf ×3, fawley ×3).
2. **Assess P5** (camcge Epic-5 deferral; rocket Sprint-36 submission) — both a-priori non-movers in-sprint.
3. **Pin the REPLAN exits and the freed-budget reallocation** — for each track, where its budget goes when it exits (→ P4 first, then P6/P7).
4. **Author the honest KPI projection** — the in-sprint Solve movers ({P4 ganges·gangesx firm-ish, P1 mine conditional}; **P3's +Solve is a forcing hand-off, not in-sprint**; camcge is Epic-5); Translate +1 via P2; the genuine floor (75 → ≥ 76 needs a *cold-emit* mover — P4 or P1 or P3-cold-match, not a warm-start fix); path_syntax_error −2 via P4; the stretch (Solve ≥ 112); and the modal outcome.
5. **Recommend the front-load ordering** — which tracks run early so their REPLANs surface by the Day-5 checkpoint. Given the record, argue explicitly for where P4 sits relative to P1/P2 rather than inheriting the previous sprints' ordering by default.
6. **State the budget arithmetic** — the per-priority sizings (P1 18–24h, P2 20–28h, P3 12–18h, P4 14–20h, P5 10–16h, P6 8–14h, P7 6–10h, retest 4h = 92–134h) against the 168h cap, and what the reallocation looks like under early REPLANs.
7. **Write** `docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md && echo "assessment doc exists"
# per-track priors + exits + reallocation
grep -icE 'P1|P2|P3|P4|P5|REPLAN|prior|freed budget|reallocat' docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md
# the honest projection + front-load ordering + the stretch target
grep -icE 'modal|flat.?KPI|front.?load|projection|112|genuine floor|76' docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md
# the budget arithmetic is present
grep -icE '92|134|168|12h|per-priority' docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/REPLAN_RISK_ASSESSMENT.md`
- A per-track REPLAN prior (P1/P2/P3/P4) with the refuting evidence and its earliest surfacing day, weighing the carry counts
- The P5 disposition assessment (camcge Epic-5; rocket Sprint-36)
- The pinned REPLAN exits + freed-budget reallocation chain (→ P4, then P6/P7)
- The honest KPI projection: firm vs conditional movers, the genuine-floor conditionality (cold-emit movers only), the stretch (Solve ≥ 112), and the modal outcome
- The front-load ordering recommendation, argued from the three-sprint record rather than inherited
- The budget arithmetic (92–134h work-items vs the 168h cap) including the early-REPLAN reallocation case
- Updated `KNOWN_UNKNOWNS.md` with verification results for the REPLAN-prior unknowns

### Acceptance Criteria

- [ ] P1/P2/P3/P4 each assigned a REPLAN prior with its refuting evidence and earliest surfacing day
- [ ] The carry counts (mine ×4, sarf ×3, fawley ×3) weighed explicitly in the priors
- [ ] P5 assessed as an a-priori non-mover (Epic-5 / Sprint-36 hand-off)
- [ ] REPLAN exits + the freed-budget reallocation chain pinned
- [ ] The honest KPI projection authored, including the genuine-floor conditionality (a warm-start fix yields 0 floor by definition)
- [ ] The front-load ordering recommended and **argued**, with P4's position relative to P1/P2 justified from the three-sprint record
- [ ] The budget arithmetic stated (92–134h vs 168h) with the early-REPLAN reallocation case
- [ ] Cross-referenced to `SPRINT_34/REPLAN_RISK_ASSESSMENT.md` + `SPRINT_34/SPRINT_RETROSPECTIVE.md` §§1/3 + `PROJECT_PLAN.md` §"Sprint 35" Risk Level
- [ ] The relevant Known Unknowns verified and updated in `KNOWN_UNKNOWNS.md`

---

## Task 12: Plan Sprint 35 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 35 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–11

### Objective

Produce the detailed 14-day Sprint 35 schedule (Day 0 setup + Days 1–13 execution) with pasteable day-by-day prompts, front-loading per Task 11's recommendation so every deep-track REPLAN surfaces by the Day-5 checkpoint, at ≤ 12 hours/day within the 168-hour budget (92–134h work-items).

### Why This Matters

The schedule is the synthesis of all prior prep: the four track designs (Tasks 5–8), the `$149` analysis (Task 4), the golden-regeneration budget (Task 3), the Phase-0 gates (Task 10), and the REPLAN assessment (Task 11). Two scheduling decisions carry most of the sprint's expected value: **where P4 sits** (Task 11's projection says it is the designated best shot, which argues for an early slot rather than the traditional back-half failure-cohort placement), and **where the slow-emit golden regeneration runs** (Task 3's measurement determines whether it fits a normal day or needs a dedicated overnight window — getting this wrong is precisely what banked S34's verified fix).

### Background

Sprint 34's schedule + prompts are in `SPRINT_34/PLAN.md` and `SPRINT_34/prompts/PLAN_PROMPTS.md`. The per-day workflow: branch → work → quality gate ONLY if `*.py` changed → commit → push → PR → user merges → "checkout main and pull"; docs/DB/golden-only PRs skip the gate. Branch naming: `planning/sprintNN-dayN-<slug>`. Checkpoints at Day 5 + Day 10; final retest Day 13 under ≥ 3 `PYTHONHASHSEED`. The `PROJECT_PLAN.md` §"Sprint 35" Estimated Effort (92–134h, heaviest day ~11h) constrains the layout.

### What Needs to Be Done

1. **Lay out Day 0** — baseline confirmation (Task 2) + the per-track control re-confirms (mine boundary, sarf O(active) timing probe, fawley residual, the ganges per-model compile, camcge detector) + the GO/NO-GO for Day 1.
2. **Place the tracks per Task 11's front-load recommendation** — with P4's slot justified explicitly (early if it is the designated best shot) and the deep tracks positioned so their REPLANs surface by the Day-5 checkpoint.
3. **Schedule the slow-emit golden regeneration** per Task 3's measured budget — as an in-day step or a dedicated window, with the determinism-×3 and follow-on `--resolve-changed` costs accounted.
4. **Place the checkpoints** — Day 5 (PROCEED/REPLAN + freed-budget reallocation) and Day 10; the Day-13 final retest under ≥ 3 `PYTHONHASHSEED` + closeout.
5. **Write the day-by-day prompts** — one per day, pasteable verbatim, each referencing its Phase-0 gate, its design doc, and its REPLAN exit.
6. **Verify the budget** — ≤ 12h/day, ≤ 168h total, heaviest ~11h; confirm the per-priority sizings sum to 92–134h.
7. **Confirm all Known Unknowns are resolved** — any Critical/High unknown still `🔍 INCOMPLETE` is either flagged as a Day-0 blocker or explicitly labelled DESIGN-SPECIFIED (an in-sprint execution gate by design).
8. **Write** `docs/planning/EPIC_4/SPRINT_35/PLAN.md` + `docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md`.

### Changes

_To be completed_

### Result

_To be completed_

### Verification

```bash
cd "$(git rev-parse --show-toplevel)"
test -f docs/planning/EPIC_4/SPRINT_35/PLAN.md && echo "plan exists"
test -f docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md && echo "prompts exist"
# Day 0 + Days 1-13 all present as prompt headers (expect 14)
grep -cE '^## Day ([0-9]|1[0-3]) Prompt' docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md
# checkpoints, front-load, determinism, and the golden-regen window are laid out
grep -icE 'Day 5|Day 10|checkpoint|front.?load|PYTHONHASHSEED|regen' docs/planning/EPIC_4/SPRINT_35/PLAN.md
# the budget verification section is present
grep -icE '12h|168|92|134|heaviest' docs/planning/EPIC_4/SPRINT_35/PLAN.md
# no Critical/High unknown left unresolved without a label
grep -icE 'INCOMPLETE|DESIGN-SPECIFIED|Day-0 blocker' docs/planning/EPIC_4/SPRINT_35/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_35/PLAN.md` — the 14-day schedule (Day 0 + Days 1–13) with the front-load, the checkpoints, the golden-regeneration window, and the budget verification
- `docs/planning/EPIC_4/SPRINT_35/prompts/PLAN_PROMPTS.md` — one pasteable prompt per day, each referencing its Phase-0 gate + design doc + REPLAN exit
- The explicit justification for P4's scheduled position (per Task 11's projection)
- The budget confirmation (≤ 12h/day, ≤ 168h total, 92–134h work-items, heaviest ~11h)
- The Known-Unknowns resolution status (all Critical/High resolved, or flagged as Day-0 blockers / labelled DESIGN-SPECIFIED)

### Acceptance Criteria

- [ ] The 14-day schedule laid out (Day 0 + Days 1–13) with the front-load following Task 11's recommendation
- [ ] P4's scheduled position explicitly justified rather than inherited from prior sprints
- [ ] The slow-emit golden-regeneration window scheduled per Task 3's measured budget
- [ ] Checkpoints placed (Day 5 PROCEED/REPLAN + reallocation, Day 10, final retest Day 13 under ≥ 3 `PYTHONHASHSEED`)
- [ ] A pasteable prompt authored for every day, each referencing its gate + design doc + REPLAN exit
- [ ] The budget verified (≤ 12h/day, ≤ 168h, 92–134h work-items, heaviest ~11h)
- [ ] All Critical/High unknowns confirmed resolved, flagged as Day-0 blockers, or labelled DESIGN-SPECIFIED
- [ ] Cross-referenced to all prior prep tasks (Tasks 1–11) and `SPRINT_34/PLAN.md`

---

## Summary: Prep Task Execution Order

**Recommended sequence** (respecting dependencies + the critical path):

1. **Tasks 1 + 2 (parallel, Critical)** — Known Unknowns + the Day-0 baseline (anchor advanced to the S34 close; genuine-floor anchor 75). The foundation every later task re-confirms against.
2. **Tasks 3 + 4 (parallel after 1/2)** — the tooling/golden-regen survey and the `$149` product-rule root analysis. Both are *information-producing* tasks the P4 design consumes; Task 4 is on the critical path.
3. **Task 5 (Critical, after 3/4)** — the ganges/gangesx multi-root recovery design: the sprint's designated best-shot bucket mover, built on Task 4's derivation and Task 3's regen budget.
4. **Tasks 6 + 7 + 8 + 9 (parallel after 1/2)** — the deep-track designs (mine dual architecture, sarf symbolic emit, fawley diagonal + forcing) and the camcge/rocket plan. Task 6 is near-critical (largest budget line, highest REPLAN prior) and may legitimately return a REPLAN recommendation.
5. **Task 10 (Critical, after 4/5/6/7/8/9)** — consolidate the per-track `/tmp` controls into the Phase-0 gates.
6. **Task 11 (High, after 5/6/7/8/10)** — the REPLAN-prone risk assessment, the honest KPI projection, and the front-load ordering.
7. **Task 12 (Critical, after 1–11)** — the detailed 14-day schedule + day-by-day prompts.

### Success Criteria for Sprint 35 Prep

- [ ] All 12 prep tasks complete (or explicitly deferred with rationale)
- [ ] The Known Unknowns list identifies ≥ 25 unknowns with verification plans across 7 categories (Task 1)
- [ ] Day-0 baseline confirmed = Sprint 34 close (Solve 108 / Match 93 / genuine floor 75 / Translate 135), with the code anchor advanced to the **S34-close SHA** (Task 2)
- [ ] The slow-emit CGE golden-regeneration budget is **measured** and a shipping window is proposed — the S34 ship-blocker is resolved before Day 1 (Task 3)
- [ ] The `$149` product-rule defect is localized to a `file:line` hypothesis with a hand-derived correct cross-term, and the cohort catalog answers "what still fails after `$149`" per model (Task 4)
- [ ] P4 has an ordered, individually-gated, per-model-verified recovery design (Task 5)
- [ ] Each deep track (P1 mine, P2 sarf, P3 fawley) has either a `file:line` design with a pre-`src/` `/tmp` control **or** an explicit, argued REPLAN recommendation (Tasks 6, 7, 8)
- [ ] camcge's Epic-5 MS-1 gate + fallback and rocket's **Sprint-36** submission plan are specified (Task 9)
- [ ] A Phase-0 acceptance gate is authored per track P1–P5, each with `modelstat` asserted and a PROCEED/REPLAN criterion (Task 10)
- [ ] The REPLAN assessment pins the exits, the reallocation chain, and the honest modal-KPI projection — and argues P4's scheduling position from the three-sprint record (Task 11)
- [ ] The 14-day schedule + day-by-day prompts front-load per that recommendation, with Day-5/10 checkpoints and the golden-regen window placed (Task 12)
- [ ] Every design carries an explicit REPLAN exit (the modal outcome remains de-risking plus, at best, the P4 failure-cohort recovery — not a guaranteed deep-track bucket move)

---

## Appendix: Document Cross-References

- **Sprint 35 scope:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35 (Weeks 35–36)" (lines ~1696–1767)
- **Epic 4 goals:** `docs/planning/EPIC_4/GOALS.md` (Goal 5 translation blockers · Goal 6 `emit_gams.py` solve blockers · Goal 7 PATH convergence and solution matching) · `docs/planning/EPIC_4/SUMMARY.md` (row 35 is a P7 deliverable)
- **Sprint 34 close (the source of the carryforwards):** `SPRINT_34/SPRINT_LOG.md` · `SPRINT_34/SPRINT_RETROSPECTIVE.md` §4 · `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`
- **Per-track Sprint-34 control docs:** `SPRINT_34/DAY1_PROGRESS_NOTES.md` + `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` (P1) · `SPRINT_34/DAY6_PROGRESS_NOTES.md` + `SPRINT_34/SARF_EMIT_MODE_DESIGN.md` (P2) · `SPRINT_34/DAY5_PROGRESS_NOTES.md` + `SPRINT_34/FAWLEY_CORRECTION_FORCING_DESIGN.md` (P3) · `SPRINT_34/DAY11_PROGRESS_NOTES.md` (P4/P6) · `SPRINT_34/DAY10_PROGRESS_NOTES.md` + `SPRINT_34/CAMCGE_ROCKET_PLAN.md` (P5) · `SPRINT_34/DAY4_PROGRESS_NOTES.md` + `SPRINT_34/BOUND_TRANSFER_SIGN_DESIGN.md` (the shipped S34 P4) · `SPRINT_34/DAY12_P7_INFRA.md` (P7 patterns)
- **Earlier per-track lineage:** `SPRINT_33/MINE_CROSSTERM_DESIGN.md` · `SPRINT_33/DAY2_MINE_REPLAN.md` · `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md` (mine) · `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` · `SPRINT_32/SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` (sarf) · `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md` · `SPRINT_33/DAY4_FAWLEY_CONTROL.md` · `SPRINT_33/DAY5_FAWLEY_CLOSE.md` (fawley) · `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` · `SPRINT_32/CAMCGE_STAT_MPS_WALRAS_DESIGN.md` (camcge) · `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` · `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` · `SPRINT_30/NONCONVEX_FORCING_SURVEY.md` (rocket)
- **Prior-sprint prep precedents:** `SPRINT_34/PREP_PLAN.md` (the direct analog) · `SPRINT_33/PREP_PLAN.md` · `SPRINT_32/PREP_PLAN.md`
- **Prep-format templates:** `docs/planning/EPIC_1/SPRINT_4/PREP_PLAN.md` · `docs/planning/EPIC_1/SPRINT_5/PREP_PLAN.md`
- **Follow-on / backlog analyses:** `SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` · `SPRINT_30/BACKLOG_FIX_SURFACE_ANALYSIS.md` · `SPRINT_32/P6_BACKLOG_RETRIAGE.md` · `SPRINT_32/P7_INFRASTRUCTURE.md` · `docs/planning/EPIC_1/SPRINT_5/follow-ons/`
- **Epic 5:** `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the camcge Walras hand-off)
- **Reused tooling:** `scripts/diagnostics/kkt_residual.py` (Case-a/b/c + `case_c_objdef`) · `scripts/gamslib/run_full_test.py` (`--resolve-changed --since-commit`) · `scripts/diagnostics/check_presolve_divergence.py` · `scripts/sprint_audit/check_golden_staleness.py` · `Makefile` (`regen-goldens`) · `src/cli.py` (`--force`)
- **Fix surfaces referenced by the designs:** `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms`) · `src/ad/index_mapping.py` (`enumerate_variable_instances`) · `src/emit/original_symbols.py` (`emit_post_assignment_na_cleanup`, `_param_assignment_has_division`) · `src/emit/emit_gams.py` (`_emit_nlp_presolve`, the presolve-gated param assignment)
- **Property-fixture patterns:** `tests/integration/emit/test_ad_crossterm_shapes.py` + `tests/fixtures/crossterm_shapes/` (incl. `shape_p4_max_bound_transfer.gms`) · the S33 `test_sample_pruned_var_l_init.py` skip-if-absent pattern
- **Research:** `docs/research/multidimensional_indexing.md` (sarf enumeration) · `docs/research/convexity_detection.md` (Case-c family) · `docs/research/gamslib_kpi_definitions.md` (KPI definitions) · `docs/research/gamslib_parse_errors.md`

---

**Document Created:** 2026-07-23
**Owner:** Sprint 35 Planning Team
**Status:** 🔵 Prep NOT STARTED — execute Tasks 1–12 before Sprint 35 Day 1
