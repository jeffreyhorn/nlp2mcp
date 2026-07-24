# Sprint 35 Known Unknowns

**Created:** 2026-07-23
**Status:** Active — Pre-Sprint 35
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 35 — the Sprint 34 carryforward sprint landing the mine head-offset dual subsystem (#1443), the sarf symbolic-emit subsystem (#1385), the fawley #1111/#1112 constraint-index-diagonal correction + forcing, the **NEW** ganges/gangesx multi-root recovery (`$141`/`$145`/`$149`), the camcge dual-consistent Walras numéraire (#1330 → Epic 5), and the rocket #1462 PATH-consultation submission to the **Sprint-36** consultation

---

## Executive Summary

This document identifies every assumption and unknown for Sprint 35's carryforwards **before** implementation begins, continuing the methodology that has prevented late-stage surprises since Sprint 4. Sprint 35 is **specification-bound, not diagnosis-bound**: every carryforward inherits a Sprint-34 *control-confirmed* characterization. The role of this list is therefore not to re-diagnose but to keep each characterization — including its *sufficiency*, its *root structure*, and its *achievable KPI bucket* — an explicit, verifiable Day-0-re-confirm hypothesis (the standing PR24/PR27 lesson).

Sprint 34 closed **full modal-flat — 0 bucket moves** (Solve 108 / Match 93 / genuine floor 75 all held), exactly the honest Task-9 projection. Every deep emit track REPLAN'd or deferred after a `/tmp`/harness/compile control refuted its premise **before any bad ship** (zero broken code across 8 execution PRs); the one `src/` landing (P4 sense-aware bound-transfer) was a general warm-start-correctness fix with no +Solve. Two Sprint-34 findings shape this list more than any other:

1. **The prep root hypothesis was substantially wrong — again.** Sprint 34's prep asserted "ganges/gangesx share a single `$141/$145/$149` root; one fix recovers both." Day 11 found **three independent roots** and **no model recovering from `$141` alone**. Category 4 is written to make the multi-root structure verifiable per model rather than asserted, and Unknown 4.3 pulls the deepest root (`$149`) into prep as its own analysis.
2. **"No bucket → no `src/`" cost a real, verified fix.** The `$141` fix was written, empirically verified (removes all 15 `$141`), and then **reverted** — because it moved no bucket alone *and* its slow-emit CGE goldens are un-regenerable in the CI budget (`make regen-goldens` soft-timed-out on ganges/gangesx/clearlak/turkpow, refreshing 0 goldens). Unknown 4.5 makes that operational constraint a measured, pre-Day-1 question rather than a Day-11 discovery.

**Sprint 35 Scope** (see `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35 (Weeks 35–36)", lines ~1696–1767, Priorities 1–7):
1. **P1 — mine #1443:** head-offset dual subsystem (~18–24h; the deepest from-scratch AD/emit track, H_dual refuted, `x.m = 0`-degenerate boundary; +1 Solve lever)
2. **P2 — sarf #1385:** symbolic/parametric `stat_task` emit subsystem (~20–28h; 369K-column elimination via a corpus-wide re-architecture; +1 Translate lever)
3. **P3 — fawley #1111/#1112:** constraint-index-diagonal correction + forcing (~12–18h; +1 genuine-floor lever; the +Solve is **H-b** → forcing)
4. **P4 — ganges/gangesx multi-root recovery (NEW):** `$141` + `$145` + `$149` + turkey `$161` (~14–20h; +2 Solve/Match, −2 path_syntax_error — the designated best-shot bucket mover)
5. **P5 — camcge #1330 (Epic 5) + rocket #1462:** dual-consistent Walras numéraire + the PATH-consultation submission to **Sprint 36** (~10–16h)
6. **P6 — residual failure-cohort + banked follow-ons:** dinam/indus `$140`+`$149`; turkpow/clearlak `$149`+`$171`; turkey `$161`; the Case-c family (~8–14h)
7. **P7 — infrastructure:** property fixtures + genuine-floor tracking (anchor 75) + checkpoint refresh + Epic-4-SUMMARY row 35 (~6–10h)

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 35" (Deliverables / Acceptance Criteria / Estimated Effort / Risk Level = **HIGH**); the per-track Sprint-34 control docs under `docs/planning/EPIC_4/SPRINT_34/` (`DAY1_PROGRESS_NOTES.md`, `MINE_DUAL_SUBSYSTEM_DESIGN.md`, `DAY6_PROGRESS_NOTES.md`, `SARF_EMIT_MODE_DESIGN.md`, `DAY5_PROGRESS_NOTES.md`, `FAWLEY_CORRECTION_FORCING_DESIGN.md`, `DAY11_PROGRESS_NOTES.md`, `DAY10_PROGRESS_NOTES.md`, `CAMCGE_ROCKET_PLAN.md`, `SPRINT_35_CARRYFORWARDS.md`); and `docs/planning/EPIC_4/SPRINT_35/PREP_PLAN.md`. (No `PRELIMINARY_PLAN.md` exists for Sprint 35; the `PROJECT_PLAN.md` Sprint 35 section is the authoritative scope.)

**Lessons from Previous Sprints:** The Known Unknowns process has run every sprint since Sprint 4 (Sprint 4: 23 unknowns / Sprint 5: 22 / Sprint 33: 27 / Sprint 34: 27). Four lessons dominate this list:
- **A banked characterization is still a hypothesis — including its root structure.** Sprint 34 refuted or corrected the banked premise on *every* track it touched: mine's H_dual proved value-invariant on the cold solve too; fawley's +Solve proved **H-b**; sarf proved a foundational re-architecture; and P6's single-root hypothesis proved **three-root**. Unknowns 1.1/1.2, 2.1/2.3, 3.1/3.3, 4.3/4.4 encode this.
- **The failure cohort is multi-root — verify per model, never infer one model from another.** Unknowns 4.4, 6.1, 6.2 encode the discipline explicitly.
- **When every deep KPI mover is REPLAN-prone, a flat-KPI close is the modal outcome — but the failure-cohort track can still deliver.** S33's P6 (sample) produced the only genuine bucket move in a three-sprint window; S34's P6 got closest. Unknowns 1.5, 2.2, 3.2, 4.5 track the REPLAN-probability of each mover; Category 4 is the designated fallback-turned-primary.
- **The genuine-floor ramp is conditional, not a sequence of independent +1s** (Sprint-30 §3, borne out in S32/S33/S34). Only a *cold-emit* mover lifts the floor; a warm-start fix yields 0 by definition. Unknowns 3.4 and 7.2 encode this.

**Deferred-unknown lineage (from Sprint 34):** Sprint 35's Categories 1, 2, 3 and 5 are the direct continuation of the Sprint-34 REPLAN'd/deferred tracks (`SPRINT_34/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34/SPRINT_35_CARRYFORWARDS.md`). Specific carried-forward unknowns:
- **S34 Unknown 1.2** (mine H_dual → cold MS-1) closed **❌ WRONG** on S34 Day 1 — the control refuted H_dual. Its successor here is **Unknown 1.2** (does *any* emit-side dual architecture reach cold MS-1?), preceded by the new reachability question **Unknown 1.1**.
- **S34 Unknowns 2.1–2.5** (sarf) resolved as "the design is sound; the scope is a corpus-wide re-architecture." They carry forward here as **2.1–2.5** with the new corpus-safety question **2.3** promoted to Critical.
- **S34 Unknown 3.2** (fawley H-b) closed ✅ VERIFIED as H-b; it carries forward as **3.3** (is the H-b finding still exact) with the +Solve explicitly removed from P3's scope.
- **S34 Unknowns 6.1/6.3** (the ganges/gangesx cohort root) closed **❌ WRONG** (single-root refuted). They are the direct ancestors of the whole of **Category 4** and of **6.1/6.2**.
- **S34 Unknown 7.2** (genuine-floor anchor + code anchor) carries forward as **7.2**, with the code anchor now required to *advance* to the S34-close SHA.
Category 4 is a **newly-promoted** first-class track (it was S34's Priority 6 backlog item).

---

## How to Use This Document

### Before Sprint 35 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (via prep Tasks 2–11; see the Task-to-Unknown mapping appendix)
2. Run the `/tmp` control experiment for each track (the PR24/PR27 gate) BEFORE any `src/` change
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 35
1. Review daily during standup
2. Add newly discovered unknowns (use the template at the end)
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption breaks the fix or forces a mid-sprint REPLAN (>8 hours rework)
- **High:** Wrong assumption causes significant rework (4–8 hours)
- **Medium:** Wrong assumption causes minor issues (2–4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 29

**By Priority:**
- Critical: 7 (24% — the reachability/sufficiency questions that gate the +Solve / +Translate / floor movers, plus the `$149` AD-core root and the per-model recovery verdict)
- High: 12 (41% — design, no-regression, REPLAN-probability, cohort-scope, and operational-budget questions)
- Medium: 7 (24% — IR support, byte-stability, floor-lift, detector-scope, fixture, and submission questions)
- Low: 3 (10% — nice-to-know, low impact)

**By Category:**
- Category 1 (mine head-offset dual subsystem): 5 unknowns
- Category 2 (sarf symbolic-emit subsystem): 5 unknowns
- Category 3 (fawley constraint-index-diagonal correction + forcing): 4 unknowns
- Category 4 (ganges/gangesx multi-root recovery): 6 unknowns
- Category 5 (camcge Walras + rocket PATH submission): 3 unknowns
- Category 6 (residual failure-cohort + banked follow-ons): 3 unknowns
- Category 7 (infrastructure): 3 unknowns

**Estimated Research Time:** ~35.5 hours (within the 28–36 hour target; spread across prep Tasks 2–11)

---

## Table of Contents

1. [Category 1: mine #1443 — Head-Offset Dual Subsystem](#category-1-mine-1443--head-offset-dual-subsystem)
2. [Category 2: sarf #1385 — Symbolic-Emit Subsystem](#category-2-sarf-1385--symbolic-emit-subsystem)
3. [Category 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction + Forcing](#category-3-fawley-11111112--constraint-index-diagonal-correction--forcing)
4. [Category 4: ganges/gangesx Multi-Root Recovery](#category-4-gangesgangesx-multi-root-recovery)
5. [Category 5: camcge Walras (Epic 5) + rocket PATH Submission](#category-5-camcge-walras-epic-5--rocket-path-submission)
6. [Category 6: Residual Failure-Cohort + Banked Follow-Ons](#category-6-residual-failure-cohort--banked-follow-ons)
7. [Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking](#category-7-infrastructure--property-fixtures--genuine-floor-tracking)

---

# Category 1: mine #1443 — Head-Offset Dual Subsystem

## Unknown 1.1: Is the `x.m = 0`-degenerate boundary reachable by ANY emit-side dual architecture?

### Priority
**Critical** — This is the *prior* question to the whole of P1 (18–24h, the sprint's largest single budget line). If no emit-side architecture can supply the missing boundary contribution, P1 should REPLAN in prep, not on Day 3 of a fourth consecutive carry.

### Assumption
The Sprint-34 Day-1 result holds and generalizes: mine's head-offset dual boundary is **`x.m = 0`-degenerate** — at the bound-active `stat_x` rows the cross-term is structurally correct, and closing the residual needs a contribution (+16000 per `MINE_DUAL_SUBSYSTEM_DESIGN.md` §3.2) that neither a keying change (the objective-gradient sign flip is **BANNED**) nor a bound multiplier (`x.m = 0`, so `piU_x`/`piL_x` are structurally zero) can supply. The *open* part is whether a genuinely different dual architecture — an explicit head-offset dual variable, a precedence-constraint reformulation, an augmented complementarity pairing, or an LP-side reformulation upstream of emit — can supply it.

### Research Questions
1. Writing the bound-active `stat_x` stationarity identity with every available multiplier (`piU_x`, `piL_x`, `lam_pr`, the precedence duals), which terms are structurally zero when `x.m = 0`, and what is the exact size of the unfilled gap?
2. Can an explicit head-offset dual variable paired at the shifted label `(k,l+1,i,j)` supply it, and does that variable have a legitimate complementarity partner?
3. Can a reformulation of the precedence constraint place its dual at the base label `(k,l,i,j)` instead, and does that change the MCP's square structure?
4. Is there any candidate that supplies the contribution **without** the banned sign flip and without an LP-side change (which would be out of emit scope)?
5. If every candidate fails the reachability test, is the correct disposition a deeper-architecture carry or a hand-off to the Sprint-36 PATH consultation as "an LP whose warm KKT point is not MCP-reconcilable"?

### How to Verify
Symbolic analysis against the banked decomposition, then a re-run of the S34 Day-1 `/tmp` mine control from the repo root (the emit `$include` is repo-relative; **assert `modelstat`**; `x.up=inf` is **BANNED** as a measurement device). Reproduce the residual decomposition row-for-row (`SPRINT_34/DAY1_PROGRESS_NOTES.md`), confirm the cold MS-5 / profit 16747.0723 / 51 INFES signature, and score each candidate architecture on whether it can, in principle, contribute at the degenerate rows. Cross-check `SPRINT_34/MINE_DUAL_SUBSYSTEM_DESIGN.md` §§3.2/4/5 and `SPRINT_33/DAY2_MINE_REPLAN.md`.

### Risk if Wrong
- **If the boundary IS reachable and we conclude it is not:** P1 REPLANs unnecessarily and mine stays `model_infeasible` for a fifth sprint (a missed +1 Solve / +1 floor). Recoverable in a later sprint but expensive in credibility.
- **If the boundary is NOT reachable and we proceed anyway:** 18–24h — the largest budget line — is spent on a fifth refuted hypothesis, and the freed-budget reallocation to P4/P6 (the sprint's actual bucket movers) happens too late to matter.

### Estimated Research Time
2 hours (symbolic identity analysis + the `/tmp` control re-run + candidate scoring)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Does a head-offset dual reconciliation drive the cold MCP to MS-1 @ 17500 without perturbing interior rows?

### Priority
**Critical** — This is the P1 fix hypothesis and its Phase-0 gate. If the surviving architecture cannot drive the **cold** MCP to MS-1 @ 17500 with interior rows unperturbed, P1 REPLANs.

### Assumption
The surviving candidate from Unknown 1.1 — an emit reconciliation keyed on the S31 `EquationDef.head_domain_offsets` IR that anchors the head-placed precedence dual's complementarity correctly — drives the **cold** MCP to **MS-1 @ 17500** (the NLP/LP optimum), closing all bound-active boundary rows while leaving interior rows unchanged at 0.

**NB (the gate is the cold solve, not the warm residual).** Sprint 33 proved H1 re-keying value-invariant and Sprint 34 proved the same of H_dual: because keying/pairing changes leave the warm-point term *values* unchanged, a warm residual `N → 0` check is un-hittable by this class of fix and is the **wrong** diagnostic. The structural pairing change is what the cold solve reflects.

### Research Questions
1. What is the precise reconciliation term — which head-placed dual, at which shifted label, mapped into which `stat_x` row?
2. Does it close **all** bound-active boundary rows in the cold solution, not merely the max row?
3. Does it leave every interior row consistent (no new nonzero introduced)?
4. Does the cold MCP then reach MS-1 @ 17500, with `modelstat` asserted at every read?
5. Does it regress any other head-offset model that shares the emit path (srpchase and the S31 offset-alias cohort)?

### How to Verify
A pre-`src/` `/tmp` control (PR24/PR27): emit the reconciled MCP, confirm the warm residual is 0 at **all** bound-active rows AND unchanged (0) at interior rows, **then** solve cold and presolve, asserting `modelstat` each time and requiring MS-1 @ 17500. Then re-run the head-offset cohort for regressions. This is the P1 Phase-0 gate (Task 10).

### Risk if Wrong
- Mid-sprint REPLAN after the design phase is already spent: the 18–24h budget produces documentation rather than a bucket move, and the Solve/genuine-floor targets lose their largest single lever (Solve stays 108, floor stays 75).
- If the reconciliation *partially* closes (some boundary rows but not all), the temptation to ship a partial correctness change with no bucket must be resisted under the "no bucket → no `src/`" rule — the S34 P6 precedent.

### Estimated Research Time
2 hours (design the reconciliation term + specify the `/tmp` control; the control itself executes in-sprint on Day 1)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: Is the 22-row boundary breadth and the +16000 gap still exact at Day 0?

### Priority
**High** — The design is sized against these figures; if the live tree has drifted (the S34 P4 bound-transfer change touched the presolve warm-start path), the design targets the wrong rows.

### Assumption
The banked characterization still holds exactly on the live tree: 22 nonzero residual rows, all confined to the `c`-boundary (`ord(l)+ord(i) = card` / `= card+1`), 0 at interior rows; the max row is `stat_x(3,1,1)` with CASE_B fingerprint (rel 2.37, raw −32000, dual scale 1.35e4, dual transfer CONSISTENT); and the gap to close is +16000. mine's Day-0 bucket is `model_infeasible` (MS 5).

### Research Questions
1. Does `kkt_residual.py mine.gms` reproduce the CASE_B fingerprint exactly (rel 2.37, raw −32000, dual CONSISTENT)?
2. Are there still exactly 22 nonzero rows, and are all of them on the `c`-boundary?
3. Did the S34 P4 sense-aware bound-transfer change (MINIMIZE byte-identical, but mine's warm path touches `piU_x`) perturb any figure?
4. Is mine still `model_infeasible` (MS 5) and a `verified_convex` candidate in the Day-0 DB?
5. Is the LP primal still feasible/optimal at 17500 (mine NLP MS-1), confirming the failure is a genuine dual degeneracy rather than a primal problem?

### How to Verify
Run `scripts/diagnostics/kkt_residual.py` on mine from the repo root and diff the fingerprint against `SPRINT_34/DAY1_PROGRESS_NOTES.md` and `SPRINT_34/BASELINE_METRICS.md` §5. Read mine's Day-0 bucket from the committed `data/gamslib/gamslib_status.json`. Confirm the NLP solves MS-1 @ 17500 with `modelstat` asserted.

### Risk if Wrong
- A drifted row count or gap size means the reconciliation design (Unknown 1.2) targets rows that no longer exist or under/over-supplies the contribution → the `/tmp` control fails for a reason unrelated to the architecture, burning Day-1 budget on re-diagnosis.
- If the S34 P4 change perturbed mine's warm path, the banked decomposition must be re-derived before the design is trusted.

### Estimated Research Time
1.5 hours (harness run + fingerprint diff + DB provenance read)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED (Day-0-bucket aspect; the fingerprint aspect is Task 6's)
**Verified by:** Task 2 (Day-0 bucket + emit stability) — Task 6 owns the residual decomposition
**Date:** 2026-07-23

**Findings (Task 2 — Day-0 bucket + emit stability):**
- mine is `model_infeasible` (`model_status = 5`) at Day 0, a `verified_convex` candidate — the P1 bucket the head-offset dual subsystem targets (infeasible → MODEL STATUS 1 if the reconciliation cold-matches). Recomputed from the committed DB.
- **mine's emit is byte-identical to the Sprint-34 Day-0 record**: md5 `a394cbc3dee15015aa099d7a84e0fa30`, reproduced under `PYTHONHASHSEED` ∈ {0,1,42}. This is the same md5 `SPRINT_34/BASELINE_METRICS.md` §2 recorded, so **the S34 P4 sense-aware bound-transfer did not perturb mine's cold emit** (P4 was MINIMIZE-byte-identical and mine's presolve golden was not among the 11 regenerated).
- The 22-row breadth, the CASE_B `stat_x(3,1,1)` fingerprint (rel 2.37 / raw −32000 / dual CONSISTENT) and the +16000 gap are **not** re-measured here — they need the `kkt_residual.py` run and the residual decomposition, which are Task 6's primary work.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` §3 (model_infeasible members), §2.4 (determinism ×3 + the md5 match vs S34 Day 0), §5 (mine provenance row).

**Decision:** the Day-0 mine bucket and emit stability are confirmed, and the S34 P4 change is ruled out as a perturbation source; the fingerprint / 22-row / +16000 re-confirmation remains Task 6's (mine dual-architecture design).

---

## Unknown 1.4: Does `EquationDef.head_domain_offsets` carry everything the reconciliation needs?

### Priority
**Medium** — If the IR is short of what the design needs, an IR extension lands first (a bounded, well-understood change — S31 built this foundation), adding hours but not changing the track's shape.

### Assumption
The S31 IR foundation is sufficient: `EquationDef.head_domain_offsets` is a per-position `IndexOffset|None` tuple aligned to the declaration domain (mirroring `declaration_domain`), with `has_head_domain_offset` derived in `__post_init__`, and it carries enough structure for the emit to identify the shifted head label `(k,l+1,i,j)` where `pr.m` lives versus the base label `(k,l,i,j)` where `lam_pr` pairs — without new IR fields.

### Research Questions
1. Does `head_domain_offsets` expose the offset *direction and magnitude* per position, or only its presence?
2. Can the emit reconstruct both the shifted and the base label from the IR alone, for every position in mine's domain?
3. Does the parser populate `head_domain_offsets` for every mine equation the reconciliation touches (not just `pr`)?
4. If an extension is needed, is it additive (a new derived property) or does it change existing field semantics — i.e. what is the blast radius across the 142 models?
5. Does any other consumer of `head_domain_offsets` (the S31 Site-2 dual transfer) constrain what can be added?

### How to Verify
Read `src/ir/parser.py` around the `head_domain_offsets` construction (`_domain_list_head_offsets`) and the `EquationDef` definition; trace mine's equations through the parser with a small script and print the populated tuples. Cross-check `SPRINT_31`'s head-offset IR plumbing notes and the S31 Site-2 dual-transfer consumer.

### Risk if Wrong
- An IR extension is needed mid-design: +2–4h and a wider blast radius (the IR is read by the general emit path for all models), plus a determinism re-verification.

### Estimated Research Time
1 hour (IR read + a trace of mine's equations)

### Owner
Development team (IR specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: What is P1's REPLAN probability, and is a fourth carry the right allocation?

### Priority
**High** — Determines the front-load ordering and the freed-budget reallocation. mine is **four-times-carried** (S32 → S33 → S34 → S35) with a refuted hypothesis each time; 18–24h is the sprint's largest single line.

### Assumption
P1's REPLAN prior is **High** — higher than Sprint 34's, because the hypothesis space has narrowed with each refutation (S32: the 5th-coupling; S33: H1 keying, proven value-invariant; S34: H_dual, proven value-invariant on the cold solve too) and the remaining candidates all require supplying a contribution at a structurally degenerate row. If Unknown 1.1's reachability analysis is negative, the correct in-prep disposition is a REPLAN with the budget reallocated to P4 (the designated best shot) and P6/P7.

### Research Questions
1. What specific control evidence would refute the surviving architecture, and how early can it surface (Day-5 checkpoint measurability is the requirement)?
2. Given three consecutive refutations, what is the honest prior that a fourth hypothesis succeeds?
3. If P1 REPLANs on Day 1 (as it did in S34), where does the 18–24h go — P4 first, then P6/P7?
4. Is the mine +1 Solve / +1 floor still counted as "firm" or "conditional" in the sprint's acceptance criteria?
5. Does the alternative disposition (hand mine to the Sprint-36 PATH consultation alongside rocket) have more expected value than a fifth emit attempt?

### How to Verify
Apply the PR16 hypothesis-validation methodology (`SPRINT_34/REPLAN_RISK_ASSESSMENT.md` template): per-track prior, refuting evidence, earliest surfacing day, freed-budget target. Weigh the carry count explicitly against the S32/S33/S34 outcome record (`SPRINT_34/SPRINT_RETROSPECTIVE.md` §§1/3).

### Risk if Wrong
- **Prior too low:** the schedule front-loads 18–24h that produces no bucket, and P4 (the actual mover) is squeezed into the back half where its slow golden regeneration cannot fit.
- **Prior too high:** a reachable architecture is abandoned prematurely.

### Estimated Research Time
1 hour (REPLAN assessment for this track)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: sarf #1385 — Symbolic-Emit Subsystem

## Unknown 2.1: Are S1/S2/S3 the complete set of enumeration sites?

### Priority
**Critical** — The landing must be **atomic** (the gated constraints emit zero per-instance Jacobian entries, so the cross-terms must come from the new parametric path). A missed fourth site means a partial landing that is worse than no landing: broken cross-terms with no timeout relief.

### Assumption
Sprint 34 Day 6's three-site characterization is complete: **S1** the `acost3` scalar body-diff in `compute_constraint_jacobian`; **S2** `enumerate_variable_instances` (`src/ad/index_mapping.py:327`) materializing the 369,024 `task(g,t,mn,mn)` columns, called per-variable from `build_index_mapping`; **S3** the per-column `stat_task` stationarity. No fourth site materializes `task`'s columns.

### Research Questions
1. Does a live trace of a sarf emit attempt confirm all three sites and no others?
2. Is 369,024 = 16·24·31·31 still the exact Cartesian, and is the active `taskposs ∧ tech` subset still 398?
3. Are there indirect consumers of the enumerated column list (golden emit, presolve companion emission, the `.fx` init pass) that would also need a symbolic path?
4. Does the existing **equation**-level gate `_is_blowup_dynamic_subset_equation` interact with any of the three sites?
5. Is there any site that enumerates lazily today and would become eager under the symbolic change?

### How to Verify
Instrument a sarf emit attempt (recursion limit 50000) with counters at each candidate enumeration point; confirm the three sites fire and that the aggregate column count matches 369,024. Cross-check `SPRINT_34/DAY6_PROGRESS_NOTES.md` and `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`.

### Risk if Wrong
- A fourth site turns an atomic landing into a partial one: the emit still times out (no +1 Translate) while the changed cross-term path risks the other 141 models → the worst outcome available on this track.

### Estimated Research Time
1.5 hours (instrumented emit trace + count confirmation)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Does the symbolic re-emit land at O(active = 398) rather than O(369K)?

### Priority
**High** — This is P2's Phase-0 tractability gate (PR20) and its sole KPI justification (+1 Translate). If the parametric emit re-triggers the timeout, the whole 20–28h track REPLANs.

### Assumption
Emitting one guarded `stat_task(g,t,m,n)$taskposs` plus a `task.fx(...)$(not (...)) = 0` companion — letting GAMS instantiate the live rows — reduces the emit from O(369,024) to O(active = 398), taking **seconds** rather than the current >75s failure.

### Research Questions
1. What is the current, measured emit wall-clock for sarf (the >75s failure), and by what method is it measured reproducibly?
2. What is the projected symbolic-mode cost, and what is the pass threshold (single-digit seconds? under 30s?)
3. Does the parametric cross-term path introduce a *new* cost that scales with something other than the active set?
4. Does GAMS itself handle the guarded `$taskposs` instantiation efficiently, or does the cost simply move from Python to GAMS compile time?
5. Would a partial improvement (e.g. 75s → 40s, still failing) count as progress or as a REPLAN?

### How to Verify
Pin the measurement method first (a timed emit of `sarf_mcp.gms` from a clean tree). Run it as a Day-0 probe to establish the baseline. Post-change, re-time under the same method and require the O(active) threshold. This is the P2 Phase-0 gate (Task 10) and a REPLAN-prior input (Task 11).

### Risk if Wrong
- 20–28h — the second-largest budget line — spent for the lowest-leverage bucket with no result; sarf stays `translate_failure` and Translate stays 135.
- A partial improvement that does not cross the threshold is the likeliest failure mode and must be pre-classified as a REPLAN, not as progress.

### Estimated Research Time
1.5 hours (pin the measurement method + run the Day-0 baseline probe)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Can `enumerate_variable_instances` gain a symbolic-column concept without perturbing the other 141 models?

### Priority
**Critical** — `enumerate_variable_instances` builds the `col_to_var` index that the entire Jacobian → gradient → stationarity flow iterates **for all 142 models**. Any ordering or content change there is a corpus-wide regression risk, and determinism is a hard requirement (PR12).

### Assumption
A symbolic-column concept can be added as a *branch* — variables flagged symbolic present as a domain expression plus a guard; all other variables enumerate exactly as today — leaving the other 141 models' `col_to_var` construction and ordering **byte-identical**, their goldens unchanged, and determinism intact under `PYTHONHASHSEED` {0,1,42}.

### Research Questions
1. What exactly does `col_to_var` become for a symbolic variable, and which downstream consumers must branch on symbolic-vs-enumerated?
2. Can the branch be made structurally impossible to reach for non-symbolic variables (so the other 141 models traverse literally unchanged code paths)?
3. Which models besides sarf would be flagged symbolic under the proposed criterion — is the flag sarf-only by construction, or data-driven (and therefore able to catch a model unexpectedly)?
4. Does the change alter any dictionary iteration order or set-derived ordering that determinism depends on?
5. What is the regression harness that proves corpus-safety — full-corpus golden byte-comparison plus `--resolve-changed`, or is a narrower set defensible?

### How to Verify
Read `src/ad/index_mapping.py` (`enumerate_variable_instances`, `build_index_mapping`) and enumerate its call sites; design the branch and identify every consumer. Specify the full-corpus regression harness: all 141 non-sarf goldens byte-identical, determinism ×3, `--resolve-changed --since-commit <S34-close>` GO.

### Risk if Wrong
- A corpus-wide regression on currently-passing models — the highest-blast-radius failure available in the sprint (135 translating, 108 solving, 93 matching models all traverse this code).
- A determinism break would invalidate the sprint's PR12 acceptance criterion regardless of any other result.

### Estimated Research Time
2 hours (code read + call-site enumeration + harness specification)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Is the banked 7-term `stat_task` derivation complete and fully index-bound?

### Priority
**High** — The parametric cross-term path must reproduce this derivation exactly; a missing or set-name-literal term produces a silently wrong `stat_task` that no timeout measurement would catch.

### Assumption
The banked 7-term `stat_task` derivation (`SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md`) is complete — every constraint contributing a `task` cross-term is represented — and each term is expressible with all indices bound by the equation domain or an enclosing `sum`, with no set-name-literal indices that would break under the guarded parametric emit.

### Research Questions
1. Do all 7 terms survive re-derivation from the sarf source, or has a term been missed/duplicated?
2. Is every index in every term bound by the `stat_task(g,t,m,n)` domain or an explicit `sum`?
3. Do any terms rely on the per-instance Jacobian entries that the guarded constraints will no longer emit?
4. How is the parametric emit verified term-by-term — against a hand-check on a reduced sarf instance, or against the (unobtainable) full enumeration?
5. Does the `acost3` body-diff (S1) contribute a term that only exists in scalar form today?

### How to Verify
Re-derive the `stat_task` cross-terms from `data/gamslib/raw/sarf.gms` by hand and diff against the banked 7-term list. Check each term's index binding. Where full verification is impossible (369K columns), specify a reduced-instance hand-check as the acceptance evidence.

### Risk if Wrong
- A silently wrong `stat_task`: sarf translates (+1 Translate achieved) but emits an incorrect MCP — the worst kind of "success", since the KPI moves while correctness regresses and no gate catches it.

### Estimated Research Time
1.5 hours (hand re-derivation + index-binding check)

### Owner
Development team (AD specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Does the guarded emit plus the `task.fx` companion yield exactly the 398 live rows?

### Priority
**Medium** — A mismatch here produces either an under-determined MCP (missing rows) or spurious fixed variables; both are detectable at compile/solve time, so the cost is rework rather than a silent defect.

### Assumption
Emitting `stat_task(g,t,m,n)$taskposs` together with `task.fx(...)$(not (taskposs ∧ tech)) = 0` and the corresponding MCP matching yields exactly the **398** live rows — the same set the (intractable) full enumeration would produce — with the inactive columns fixed out rather than absent.

### Research Questions
1. Is the guard predicate in the emitted GAMS exactly `taskposs ∧ tech`, matching the runtime-computed active set?
2. Does the MCP `Model` matching statement pair `stat_task` with `task` correctly under the guard, given the square-system requirement?
3. Does fixing the inactive columns to 0 change the solution versus simply omitting them?
4. Does GAMS report exactly 398 `stat_task` rows at compile time, and how is that counted?
5. Are there `taskposs` elements that are runtime-true but structurally excluded by `tech` (or vice versa) — i.e. is the conjunction correct?

### How to Verify
After the symbolic emit exists, compile `sarf_mcp.gms` and read the GAMS row/column counts; assert exactly 398 `stat_task` rows and that the MCP is square. Compare against `SPRINT_34/DAY0_TRACE_NOTES.md`'s 398 active-column figure.

### Risk if Wrong
- Rework of the guard/matching (2–4h) and a re-run of the tractability gate; recoverable, but it consumes the P2 buffer.

### Estimated Research Time
1 hour (guard/matching specification + the counting method)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: fawley #1111/#1112 — Constraint-Index-Diagonal Correction + Forcing

## Unknown 3.1: Does the constraint-index-diagonal guard drive `max|stat_bq|` to 0, not merely to 18.468?

### Priority
**Critical** — This is P3's Phase-0 gate. The control-proven 473 → 18.468 is a 96% reduction, **not** a closure; a correction that stops at 18.468 has not fixed the cross-term and must not ship.

### Assumption
Adding the constraint-index-diagonal `sameas` guard to the qsb/pbal cross-terms in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`) — the guard mbal already carries — drives `max|stat_bq|` to **0** (machine zero), not to the 18.468 residue the partial S34 Day-5 control reached.

### Research Questions
1. What accounts for the residual 18.468 after the `$(sameas(cfq__,cf))` guard is added — a second missing guard, a different term, or a bound-transfer artifact?
2. Is the constraint-index diagonal a *single* predicate, or does qsb need a different orientation than pbal?
3. Does the S34 P4 sense-aware bound-transfer (`abs(var.m)`, which now transfers fawley's `bq(cc-dist)` cell) account for part of the 18.468, changing the target?
4. What is the pass threshold — machine zero, or a tolerance consistent with the harness's other Case-a determinations?
5. Can the closure be demonstrated in a `/tmp` control before any `src/` change (the PR24 requirement)?

### How to Verify
A pre-`src/` `/tmp` control: apply the diagonal guard to fawley's emitted MCP by hand, re-run `kkt_residual.py`, and require `max|stat_bq| → 0` with `modelstat` asserted. Cross-check `SPRINT_34/DAY5_PROGRESS_NOTES.md` and `SPRINT_33/FAWLEY_SECOND_INDEX_DESIGN.md`.

### Risk if Wrong
- Shipping a partial correction into a ~1430-line shared emit function for a residual that does not close: all the blast radius, none of the correctness win, and no floor lift.
- If the 18.468 has a *different* root, P3's design is aimed at only part of the defect and the genuine-floor lever evaporates.

### Estimated Research Time
1.5 hours (residual decomposition + `/tmp` control specification)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Is the guard leak-free against mbal, the 1-D core, and the 2-D cohort?

### Priority
**High** — `_add_indexed_jacobian_terms` is ~1430 lines with a dozen issue-specific `sameas` paths, shared with mbal, cesam2, camcge and ps2. A leak regresses currently-passing models — the standing gate-leak REPLAN exit (`FAWLEY_CORRECTION_FORCING_DESIGN.md` §6).

### Assumption
The diagonal predicate can be placed so that **no mbal term changes** and the 1-D core (polygon, ps2, ps3) stays byte-identical, because the predicate is orientation-specific (constraint dimension ≥ variable dimension) and therefore disjoint from the existing #1049 guard (which fires only when the variable has *more* dimensions than the constraint).

### Research Questions
1. Where exactly in the function does the predicate belong relative to the dozen existing `sameas` paths, and what is the precedence argument against each?
2. Is the orientation distinction (#1049's variable-heavier case vs qsb's constraint-heavier case) genuinely disjoint, or do they overlap for some shape?
3. Which models constitute the 2-D regression cohort (mbal, cesam2, camcge, ps2) and which the 1-D core (polygon, ps2, ps3)?
4. What does the regression harness assert — byte-identical goldens for the cohort, or bucket-stability via `--resolve-changed`?
5. Does the S31 offset-alias machinery (#1104/#1111) in the same function interact with the new predicate?

### How to Verify
Read `_add_indexed_jacobian_terms` and map every `sameas` path; construct the precedence argument. Specify the regression harness: the 2-D cohort byte-compared, the 1-D core byte-identical, and `--resolve-changed --since-commit <S34-close>` GO with no mbal-term change.

### Risk if Wrong
- A regression on mbal/cesam2/camcge/ps2 — models that currently pass — which is a strictly negative sprint outcome and would force a revert plus a golden re-regeneration cycle.

### Estimated Research Time
1.5 hours (function read + `sameas`-path map + harness specification)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Is fawley's H-b finding still exact — MS-5 @ 4399.557 with the warm residual closed?

### Priority
**High** — H-b is what removes the +Solve from P3's in-sprint scope. If it has changed (e.g. the S34 P4 bound-transfer moved the warm point), P3's KPI claim changes with it.

### Assumption
The Sprint-34 Day-5 H-b finding still holds: with the `sameas` correction **plus** all bound transfers applied, fawley's warm residual goes to ~0 yet the MCP still solves **MS-5 @ 4399.557** against an LP optimum of **2899.25** — a non-emit divergence. Therefore fawley's +Solve is a forcing hand-off, not a P3 deliverable, and P3's only KPI lever is the genuine floor (contingent on a cold match, Unknown 3.4).

### Research Questions
1. Does the live tree reproduce MS-5 @ 4399.557 for fawley with the S34 P4 bound-transfer now shipped?
2. Is the LP optimum still 2899.25?
3. Did the P4 sense-aware transfer (which now moves fawley's `bq(cc-dist)` cell) change the warm point enough to alter the divergence?
4. Is fawley still `model_infeasible` at Day 0?
5. Does any `--force` lever (homotopy / multistart / optfile) show movement that would make the +Solve reachable after all?

### How to Verify
Re-run fawley through the harness and a cold/presolve solve on the live tree with `modelstat` asserted; compare against `SPRINT_34/DAY5_PROGRESS_NOTES.md`. Read fawley's Day-0 bucket from the committed DB. Survey the `--force` scaffold for any lever that crosses.

### Risk if Wrong
- **If H-b no longer holds (the +Solve is reachable):** P3 is under-claimed and a Solve is left on the table.
- **If H-b holds but the sprint claims a +Solve anyway:** the acceptance criteria over-promise, repeating the pattern the honest projection exists to prevent.

### Estimated Research Time
1 hour (harness + solve re-run + DB read)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED (Day-0-bucket aspect; the H-b aspect is Task 8's)
**Verified by:** Task 2 (Day-0 bucket + emit stability) — Task 8 owns the H-b re-confirm
**Date:** 2026-07-23

**Findings (Task 2 — Day-0 bucket + emit stability):**
- fawley is `model_infeasible` (`model_status = 5`) at Day 0, a `verified_convex` candidate — unchanged from the S34 close.
- fawley's **cold** emit is byte-identical to the Sprint-34 Day-0 record: md5 `d2eb48f11bdd2b6743151490ca993e6f` under `PYTHONHASHSEED` ∈ {0,1,42}, matching the md5 in `SPRINT_34/BASELINE_METRICS.md` §2.
- ⚠️ **But fawley's *warm* path did move.** `data/gamslib/mcp/fawley_mcp_presolve.gms` is one of the **11 presolve goldens regenerated** by the S34 Day-4 P4 commit `b71da11a` (the sense-aware `abs(var.m)` transfer, which now transfers fawley's `bq(cc-dist)` cell). So the MS-5 @ 4399.557 figure was measured **before** that change reached the warm start, and Task 8 must re-measure rather than inherit it.
- The MS-5 @ 4399.557 / LP-opt 2899.25 / `max|stat_bq|` 473 → 18.468 figures are **not** re-measured here — they need the harness + solve runs that are Task 8's primary work.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` §3 (model_infeasible members), §2.4 (determinism + md5 match), §5 (fawley provenance row), §1 (the 11 P4-regenerated goldens, incl. `fawley_mcp_presolve.gms`); `git diff --name-only 750803b2..78ceaead -- data/gamslib/mcp/`.

**Decision:** the Day-0 fawley bucket and cold-emit stability are confirmed; **Task 8 must re-confirm the H-b figures against the post-P4 warm start**, not carry them forward from `SPRINT_34/DAY5_PROGRESS_NOTES.md` unchecked. This is a sharpened requirement Task 2 surfaced.

---

## Unknown 3.4: Does the correction lift the genuine floor — i.e. does fawley cold-match?

### Priority
**Medium** — This is P3's only KPI claim, and it is conditional. Getting it wrong costs a target, not the work.

### Assumption
The genuine `sameas` correction changes fawley's **cold** emit (not merely its warm-start behaviour), so if fawley cold-matches after the correction it counts as a genuine floor +1 (75 → 76) under the PR25 definition. Because fawley remains MS-5 (H-b), the more likely outcome is a genuine correctness fix with **0** floor movement.

### Research Questions
1. Does the correction change the cold emit bytes, or only the warm-start path (the S34 P4 distinction — a warm-start-only fix yields 0 floor by definition)?
2. Given fawley stays MS-5, can it match at all without a forcing lever?
3. What is the PR25 classification of a cold-emit change on a model that does not solve — does it contribute to the floor?
4. If the floor does not move, is the correction still shippable under "no bucket → no `src/`"?
5. Which other 2-D models could cold-match as a side effect of the same correction?

### How to Verify
Byte-compare fawley's cold emit before and after the correction in the `/tmp` control; apply the PR25 genuine-vs-methodology definition (`SPRINT_34/BASELINE_METRICS.md` + the corpus-scope reference) to classify the result.

### Risk if Wrong
- The genuine-floor target (75 → ≥ 76) loses a claimed contributor and must rest entirely on P4/P1 — a scope-honesty issue rather than a technical one.
- The "no bucket → no `src/`" rule may block shipping a genuine correctness fix; the P3 design must pre-decide how that is handled (the S34 P4 exception criteria).

### Estimated Research Time
0.5 hours (classification against the PR25 definition)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: ganges/gangesx Multi-Root Recovery

## Unknown 4.1: Does the banked `$141` fix still apply cleanly and still remove all 15 `$141`?

### Priority
**High** — This is the one root that is already written and empirically verified. If it has drifted against the current tree, P4's cheapest step becomes a re-implementation.

### Assumption
The banked `$141` fix applies cleanly to the current tree and still removes all 15 `$141` errors from the ganges emit: skip `.l`-attribute-referencing (calibration) params in `emit_post_assignment_na_cleanup` (`src/emit/original_symbols.py:152`) via a `_param_assignment_references_varref_attr` helper mirroring the existing `_param_assignment_has_division` (`:137`). The root: the Issue-#1322 NaN-cleanup emits a self-referential guard `param(i)$(NOT(param(i) > -inf …)) = 0` over params like `adst(i) = dst.l(i)/…` whose assignment is presolve-gated (`src/emit/emit_gams.py`), leaving them declared-but-unassigned in the cold MCP.

### Research Questions
1. Do `emit_post_assignment_na_cleanup` and `_param_assignment_has_division` still sit where S34 Day 11 recorded them, with the same signatures?
2. Does the helper as banked handle every `.l`-attribute reference form (direct `dst.l(i)`, nested in an expression, inside a division)?
3. Re-applied to the current tree, does the ganges emit still show exactly 0 `$141`?
4. Does the fix change any *other* model's emit (does any passing model have `.l`-referencing params that currently get the cleanup guard)?
5. Does the same fix remove gangesx's `$141` count, or does gangesx differ?

### How to Verify
Re-apply the banked helper in a scratch tree, emit ganges and gangesx (recursion limit 50000), compile both goldens, and count `$141` occurrences before and after. Run `--resolve-changed --since-commit <S34-close> --dry-run` to check for collateral bucket movement. Cross-check `SPRINT_34/DAY11_PROGRESS_NOTES.md`.

### Risk if Wrong
- P4's cheapest, most certain step becomes uncertain, and the 14–20h budget loses its de-risked anchor.
- Collateral emit changes on passing models would require golden regeneration well beyond the four slow CGE models already budgeted.

### Estimated Research Time
1 hour (re-apply + re-emit + count + collateral check)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Is `$145` genuinely an independent universal-set (`*`-domain) root?

### Priority
**Medium** — A separate small fix if independent; if it is a facet of `$141`, the sequence shortens. Either way the cost is bounded.

### Assumption
`$145` (×3 on ganges) is an **independent** root: the same NaN-cleanup pass emitting a guard over a parameter whose domain includes the universal set (`series(*,years)`), which the cleanup pass cannot express a valid guard for. It is not fixed by the `$141` helper (which keys on `.l`-attribute references, a different criterion).

### Research Questions
1. Which exact parameters trigger `$145`, and do they also reference `.l` attributes (i.e. would the `$141` helper incidentally cover them)?
2. Is the correct treatment to skip `*`-domain params entirely, or to emit a domain-restricted guard?
3. Does skipping them re-introduce the NaN condition Issue-#1322 was written to prevent, for these params?
4. What is the minimal reproducing shape (a fixture-sized GAMS snippet with a `*`-domain param)?
5. Do any other corpus models declare `*`-domain params that currently receive the cleanup guard?

### How to Verify
Compile the ganges golden and isolate the three `$145` lines; inspect the offending parameter declarations in `data/gamslib/raw/ganges.gms`. Test whether the `$141` helper alone removes them. Grep the corpus for `*`-domain parameter declarations to size the blast radius.

### Risk if Wrong
- If `$145` is *not* independent, the design over-scopes by a small step (cheap).
- If skipping `*`-domain params re-introduces a NaN condition elsewhere, a passing model could regress — caught by `--resolve-changed`, but it costs a cycle.

### Estimated Research Time
1 hour (golden compile + declaration inspection + corpus grep)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Where does the `$149` free index originate, and what is the correct hand-derived `stat_pc` cross-term?

### Priority
**Critical** — `$149` is the deep blocker gating **six** models (ganges, gangesx, dinam, indus, turkpow, clearlak). It is the only root whose *fix shape* is unknown, and it is an AD-core/stationarity-emit defect rather than a cleanup-pass gap.

### Assumption
The `$149` "uncontrolled set entered as constant" arises in the stationarity emit: differentiating ganges's CES/LES term `prod(j, (pc(j)/pc00(j))**ac(j,r))` with respect to `pc(i)` leaves the product index `j` free in the emitted `stat_pc`. The correct emission binds `j` — either as an explicit `prod` ratio form (`prod(j, f(j)) / f(i) * f'(i)`) or an `exp(sum(j, log …))` form — and the defect lives in `src/kkt/stationarity.py` (the general indexed cross-term path `_add_indexed_jacobian_terms`, `:5861`) rather than in the AD layer proper. **This localization is a hypothesis**, per the standing lesson that prep `file:line` fix-surfaces are wrong roughly half the time.

### Research Questions
1. What is the verbatim offending `stat_pc` line, and which index is free in it?
2. What is the correct ∂/∂`pc(i)` of `prod(j, (pc(j)/pc00(j))**ac(j,r))`, accounting for the `**` exponent and the `ac(j,r)` coefficient — and which of the two candidate emit forms is preferable (numerical safety at `pc(i) → 0` argues against the naive ratio form)?
3. Is the free index introduced in the stationarity emit, in the AD differentiation of the `prod` node, or in the index-mapping layer?
4. Does the defect reproduce on a minimal fixture (a small model with `prod(j, x(j)**a(j))` in a constraint), or does it need ganges's full structure?
5. Which other corpus models emit `prod()`/`**` stationarity terms and would traverse the changed path (the blast-radius set)?

### How to Verify
Emit ganges live and capture the offending line verbatim. Hand-derive the correct cross-term symbolically and write it in fully index-bound GAMS. Trace the emit path from the `prod()` AST node to the emitted string, instrumenting `src/kkt/stationarity.py` (and, if refuted there, the AD layer) to find where `j` escapes binding. Build the minimal reproducing fixture. Grep the corpus for `prod(`/`**` in constraint bodies to enumerate the blast radius. This is prep Task 4's primary deliverable (`GANGES_149_PRODUCT_RULE_ANALYSIS.md`).

### Risk if Wrong
- **Wrong localization:** P4's deepest step starts against the wrong file, and the 14–20h budget is consumed re-diagnosing mid-sprint — precisely the S34 Day-11 failure mode this prep task exists to prevent.
- **Wrong derivation:** a fix that binds `j` but computes the wrong derivative produces a silently incorrect `stat_pc` — ganges may compile and even solve while emitting a wrong MCP.
- **Deeper than expected:** if the defect requires a general AD-core restructure of `prod` differentiation, P4's deep half is out of reach in-sprint and must REPLAN with `$141`/`$145` landing alone (which, per S34, move no bucket).

### Estimated Research Time
3 hours (live emit + symbolic derivation + emit-path trace + fixture + blast-radius grep)

### Owner
Development team (AD/KKT specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: After all three roots, do ganges AND gangesx each actually compile, solve, and match?

### Priority
**Critical** — This is P4's entire KPI claim (+2 Solve, +2 Match, −2 path_syntax_error, and +2 genuine floor if they cold-match). Sprint 34 proved that fixing one root recovers **nothing**; the assumption that fixing all three recovers **both models** is the successor hypothesis and is equally unverified.

### Assumption
`$141` + `$145` + `$149`, landed together, are **sufficient** for both ganges and gangesx: each compiles with zero `$NNN` errors, translates, solves to `model_optimal` (cold or presolve), and matches the NLP solution. Both models are `verified_convex` candidates currently in the `path_syntax_error` bucket with identical NLP objectives (6395.5444).

### Research Questions
1. After all three roots, does the ganges golden compile with **zero** errors — or does a fourth code surface (the S34 pattern)?
2. Does gangesx behave identically, or does it carry an additional independent root (verify per model — never infer one from the other)?
3. Do they solve, and to what `modelstat` — cold, or only under `--nlp-presolve`?
4. If they solve, do they match, and is the match cold (genuine floor) or presolve-only (methodology)?
5. What are their Day-0 buckets and failure codes in the committed DB, so the delta is measured rather than assumed?

### How to Verify
Per model, independently: emit → compile → count residual `$NNN` by code → translate → solve (cold and presolve, `modelstat` asserted) → bucket → match classification. Read the Day-0 provenance from the committed DB first. This protocol *is* the P4 Phase-0 gate (Task 10); Day-0 provenance comes from Task 2.

### Risk if Wrong
- The sprint's designated best-shot mover produces **0 bucket** — and since P1/P2/P3 are all a-priori non-movers or conditional, the modal outcome becomes a second consecutive full modal-flat close.
- A fourth root discovered at execution time repeats the S34 Day-11 correction, but with 14–20h already committed.
- If only ganges recovers, the −2 path_syntax_error target halves and the stretch (Solve ≥ 112) becomes unreachable.

### Estimated Research Time
1.5 hours (Day-0 provenance read + the per-model verification protocol specification)

### Owner
Development team

### Verification Results
🔍 **Status:** PARTIALLY VERIFIED — Day-0 provenance confirmed (Task 2); **the recovery verdict remains OPEN** (Task 5)
**Verified by:** Task 2 (Day-0 provenance only)
**Date:** 2026-07-23

**Findings (Task 2 — Day-0 provenance):**
- ganges and gangesx are **both** `path_syntax_error` at Day 0, both `likely_convex` candidates, both with `mcp_solve.model_status = None` (neither ever reached a solve). Both translate successfully — the failure is at the GAMS compile of the emitted MCP, not at translation.
- Both are members of the 7-model `path_syntax_error` bucket (`clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `turkey`, `turkpow`), unchanged from the S34 close.
- Their identical NLP objective (6395.5444) and apparently identical root sets are **recorded but NOT treated as evidence of a shared fate** — that inference is exactly what Sprint 34's prep got wrong.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` §3 (path_syntax_error members), §5 (ganges/gangesx provenance rows).

**Decision:** the Day-0 provenance is confirmed, but **the substantive question — whether `$141` + `$145` + `$149` together are *sufficient* for each model, verified independently — is unanswerable from the DB and stays OPEN for Task 5** (design) and the in-sprint P4 execution (the per-model emit → compile → solve → bucket → match protocol). Marked PARTIALLY VERIFIED rather than ✅ deliberately: this is the assumption S34 got wrong, and a Day-0 bucket read is not evidence for it.

---

## Unknown 4.5: Can the slow-emit CGE goldens be regenerated within the sprint budget?

### Priority
**High** — This is the operational constraint that forced Sprint 34 to **bank a verified working fix**. If it is not resolved before Day 1, P4 can produce correct code that still cannot ship.

### Assumption
The ganges / gangesx / clearlak / turkpow golden regeneration — which soft-timed-out under `make regen-goldens` in Sprint 34, refreshing **0** goldens — can be completed within Sprint 35 by scoping the regeneration per model and/or running it out-of-band (a nightly/background window), including the determinism ×3 (`PYTHONHASHSEED` {0,1,42}) multiplier and the follow-on `--resolve-changed` re-solve.

### Research Questions
1. What is the **measured** per-model emit wall-clock for ganges, gangesx, clearlak, turkpow (not an estimate)?
2. Does a per-model-scoped regeneration invocation complete where the full `make regen-goldens` soft-timed-out?
3. What is the total cost including determinism ×3 and the follow-on `--resolve-changed` re-solve?
4. Does the work fit inside a normal ≤ 12h sprint day, or does it need a dedicated overnight window (which the schedule must then reserve)?
5. Is there a soft-timeout setting or a scoping flag in the regen path that can be adjusted safely, rather than working around it?

### How to Verify
Time a single-model emit for each of the four models locally (`data/gamslib/raw/` is present locally; these paths `pytest.skip` in CI). Attempt a scoped `regen-goldens` for just those models and record the outcome. Compute the ×3 determinism and re-solve costs. This is prep Task 3's primary measurement; the verdict feeds the Task 12 schedule.

### Risk if Wrong
- **Exact repeat of the S34 outcome:** a correct, verified P4 fix that cannot ship because its goldens would be left stale — turning the sprint's best shot into another banked hand-off and a second consecutive flat close.
- If the regeneration needs an overnight window and the schedule did not reserve one, P4 lands too late for the Day-13 final retest.

### Estimated Research Time
1.5 hours (four timed emits + a scoped regen attempt + the cost arithmetic)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.6: Is turkey's `$161` independent, and does it belong in P4 or P6?

### Priority
**Low** — A small, self-contained item either way; its placement affects sequencing, not sprint outcome.

### Assumption
turkey's `$161` is a **distinct** root — a dotted-tuple set-declaration emit defect — and its `$141`/`$257` errors are downstream cascades of it, not independent roots. It shares no fix surface with the ganges `$141`/`$145`/`$149` trio.

### Research Questions
1. What is the offending set declaration, and what does the emit produce versus what GAMS expects for a dotted-tuple set?
2. Do turkey's `$141`/`$257` disappear once `$161` is fixed (confirming they are cascades)?
3. Is the fix surface in the set-declaration emit path, disjoint from `emit_post_assignment_na_cleanup`?
4. Would fixing `$161` alone recover turkey to translate/solve, or does turkey carry further roots?
5. Is turkey better placed in P4 (with the other emit-syntax roots) or P6 (the residual cohort)?

### How to Verify
Compile the turkey golden, isolate the `$161` line and the declaration it comes from, and check whether the `$141`/`$257` occurrences are downstream of it. Locate the set-declaration emit path. Cross-check `SPRINT_34/DAY11_PROGRESS_NOTES.md`.

### Risk if Wrong
- Minor mis-sequencing: turkey work lands in the wrong priority block. If `$141`/`$257` are *not* cascades, turkey is multi-root too and should be scoped as its own item rather than a small add-on.

### Estimated Research Time
0.5 hours (golden compile + declaration inspection)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: camcge Walras (Epic 5) + rocket PATH Submission

## Unknown 5.1: Does the full dual-consistent Walras redefinition reach MS-1 in a `/tmp` prototype?

### Priority
**High** — This is the Epic-5 gate. camcge has consumed prep and execution budget across three sprints against a target the banked price-pin variant demonstrably does not reach; the gate must be crisp and the fallback must be a legitimate deliverable.

### Assumption
The full dual-consistent Walras redefinition — keep every market-clearing row, add the consumption-weighted numéraire, and redefine the redundant market's dual via Walras' law so the reduced system is full-rank while the multiplier stays available — reaches **MS-1** in a `/tmp` prototype. The banked price-pin variant reaches the correct primal (omega **191.7346**, matching the NLP objective) but stays **MS-4** with INFES on `gdp`, `depreq`, `hhsaveq`, `gruse`, so MS-1 is genuinely hard and the per-model-numéraire fallback is the documented alternative outcome.

### Research Questions
1. What exactly does the Walras-law dual redefinition look like as emittable GAMS, and does it keep the MCP square?
2. Does it clear the four INFES rows the price-pin variant leaves (`gdp`, `depreq`, `hhsaveq`, `gruse`)?
3. Does it preserve the correct primal (omega 191.7346) while changing the dual system's rank?
4. What distinguishes an acceptable Epic-5 "finding" from a failure — is the per-model-numéraire characterization a deliverable in its own right?
5. Is camcge correctly excluded from the in-sprint Solve commitment (Epic-5-scoped), so a non-MS-1 outcome does not read as a missed target?

### How to Verify
Build the `/tmp` prototype and solve, asserting `modelstat` and requiring MS-1 (explicitly distinguished from the price-pin variant's correct-primal-at-MS-4 result); track the four INFES rows. Cross-check `SPRINT_34/DAY10_PROGRESS_NOTES.md`, `SPRINT_33/CAMCGE_WALRAS_DESIGN.md`, and `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Risk if Wrong
- A fourth sprint of camcge effort with no MS-1 and no clearly-framed Epic-5 finding — budget spent with nothing bankable.
- If camcge is *not* clearly excluded from the in-sprint Solve commitment, the sprint's Solve target is inflated by a model that was never going to move.

### Estimated Research Time
1.5 hours (redefinition specification + gate/fallback definition)

### Owner
Development team (CGE/MCP specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does the S1∧S2∧S3 degeneracy detector still fire only on camcge?

### Priority
**Medium** — A false positive on a passing CGE sibling would mean the detector cannot be used as a general diagnostic; the cost is a scoped diagnostic rather than a general one.

### Assumption
The S1∧S2∧S3 degeneracy detector's cold-singular false-positive guard still holds: it fires **only** on camcge (cold MS-4 @ omega 191.7346) and not on the four CGE siblings irscge, lrgcge, moncge, stdcge (all cold MS-1, `model_optimal_presolve` + match).

### Research Questions
1. Does the detector reproduce the S34 Day-10 cohort result on the live tree?
2. Do the four siblings still solve cold MS-1 at Day 0?
3. Did the S34 P4 sense-aware bound-transfer change any sibling's warm path enough to alter the detector's inputs?
4. Is the S3 cold-singular guard the component doing the discrimination, and is it robust?
5. Should the detector be promoted to a general diagnostic, or does it stay camcge-scoped?

### How to Verify
Run the detector across camcge + the four siblings on the live tree, asserting `modelstat`; compare against `SPRINT_34/DAY10_PROGRESS_NOTES.md`. Read the five models' Day-0 buckets from the committed DB.

### Risk if Wrong
- A false positive would mis-flag a passing model as degenerate, potentially triggering unnecessary Walras work on a model that does not need it (2–4h).

### Estimated Research Time
0.5 hours (detector run across the five-model cohort)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Is the FINALIZED rocket input complete, and is it correctly retargeted to the Sprint-36 consultation?

### Priority
**Medium** — A hand-off, not a fix. The specific hazard is the renumbering: the input was authored for "the Sprint-35 consultation" and the consultation sprint is now **Sprint 36**.

### Assumption
`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` is complete and submission-ready (the concrete question, the ruled-out-lever survey, the two-command reproducer, and the `--force` scaffold), and the only change needed is retargeting its stale "Sprint 35" references to **Sprint 36** at submission time. rocket's Case-c signature (CASE_C_OBJDEF; boundary `stat_ht(h0)` 1.00 / `stat_step` 0.497 / `stat_ht(h50)` 0.438; dual CONSISTENT 1.53e-10) is unchanged, and the objective-gradient sign flip remains **BANNED** (control-refuted 4×).

### Research Questions
1. Does the banked input contain stale "Sprint 35" references, and where?
2. Are all four components present and current (question, ruled-out levers, reproducer, scaffold)?
3. Does the reproducer still work on the live tree (the two-command sequence)?
4. Who are the recipients and what is the response-tracking mechanism?
5. Does rocket's Case-c signature still reproduce, confirming this is a forcing problem rather than an emit bug?

### How to Verify
Read `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` end-to-end and grep it for "Sprint 35". Re-run the reproducer and the harness Case-c classification on the live tree. Cross-check `SPRINT_34/DAY10_PROGRESS_NOTES.md` and `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md`.

### Risk if Wrong
- A hand-off carrying a stale sprint reference confuses the Sprint-36 consultation (the sprint the input actually feeds), or an incomplete bundle delays the author response — the External-Dependency risk the PROJECT_PLAN already flags.
- Re-litigating the banned sign flip would waste budget on a four-times-refuted hypothesis.

### Estimated Research Time
0.5 hours (document read + grep + reproducer check)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Residual Failure-Cohort + Banked Follow-Ons

## Unknown 6.1: Which cohort members does the `$149` fix actually unblock?

### Priority
**High** — P6's scope and the sprint's `path_syntax_error` target both depend on this. Sprint 34's fatal prep error was exactly this class of assumption.

### Assumption
The `$149` product-rule fix unblocks the `$149` **half** of dinam, indus, turkpow and clearlak — but **none of them recovers from it alone**, because dinam/indus additionally carry `$140` (the pruned-var `.l`-init shape the S33 sample fix addressed) and turkpow/clearlak additionally carry `$171`. Only ganges and gangesx have all their roots covered by P4.

### Research Questions
1. Per model (dinam, indus, turkpow, clearlak), what is the full set of distinct `$NNN` codes with counts, from a live golden compile?
2. Is dinam/indus's `$140` the same shape as the S33 sample pruned-var `.l`-init root (i.e. is the S33 fix applicable, or is it a different `$140` instance)?
3. What is `$171` on turkpow/clearlak, and is it a single shared root or two?
4. After a correct `$149` fix, exactly which models still fail and on what?
5. Does any of these four become recoverable within the sprint's remaining budget, or do they all hand forward?

### How to Verify
Compile each committed golden and tabulate error codes with counts; classify each code as `$149`-caused or independent. Compare `$140` against the S33 sample fix (`src/emit/emit_gams.py` var-init pass; the `_declared_mcp_vars` subset check). This is prep Task 4's cohort-catalog deliverable.

### Risk if Wrong
- Repeating Sprint 34's error at a larger scale: a P6 plan built on "the `$149` fix recovers the cohort" would over-promise `path_syntax_error` ≤ 5 and under-deliver.
- If a member *is* fully unblocked by `$149`, an extra recovery is left unclaimed.

### Estimated Research Time
1.5 hours (four golden compiles + code tabulation + `$140` comparison)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Does the multi-root discipline hold — is any per-model root genuinely shared?

### Priority
**High** — This is the methodological unknown that Sprint 34 got wrong. It governs how every P4/P6 claim in the sprint is verified.

### Assumption
The `path_syntax_error` cohort is **multi-root throughout**: no two models may be assumed to share a root, and no model's recovery may be inferred from another's. Every claim ("model X recovers") requires a per-model emit → compile → solve → bucket verification. Even ganges and gangesx — which share an NLP objective (6395.5444) and appear to share all three roots — must be verified independently.

### Research Questions
1. Do ganges and gangesx genuinely have identical root sets, or does one carry an extra?
2. Is there any pair in the cohort whose roots are demonstrably identical (same code, same count, same offending construct)?
3. What is the minimum verification evidence for a "recovered" claim — compile-clean, or compile-clean + solve + bucket + match?
4. How should partial recoveries (compiles but does not solve) be classified in the KPI table?
5. Does the discipline need to be encoded in the Phase-0 gate so it cannot be skipped under time pressure?

### How to Verify
Compile every cohort golden and build the per-model code×count table; look for genuinely identical root signatures. Write the per-model verification protocol into the P4 Phase-0 gate (Task 10) so it is enforced rather than remembered. Cross-check `SPRINT_34/SPRINT_RETROSPECTIVE.md` §3 (the multi-root lesson).

### Risk if Wrong
- Assuming a shared root again → a mid-sprint correction identical to S34 Day 11, with the budget already committed.
- Over-applying the discipline costs a little redundant verification time; that is the acceptable direction of error.

### Estimated Research Time
1 hour (cohort table construction + protocol specification)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Does the Case-c family stay documented non-convex, with the sign flip BANNED?

### Priority
**Low** — Settled knowledge, restated to prevent re-litigation. The sign flip has been control-refuted four times.

### Assumption
The Case-c family (cesam, lnts, hhfair, and the CGE cluster) remains **documented non-convex**, classified by the `case_c_objdef` classifier (`nu_obj = ±1`, no free multiplier). Their residuals are clean at the NLP point — a forcing problem, not an emit bug — and the objective-gradient sign flip stays **BANNED**. No emit fix is expected or attempted in Sprint 35.

### Research Questions
1. Does `kkt_residual.py`'s `case_c_objdef` classifier still flag the family on the live tree?
2. Are the residuals still clean at the NLP point for each member?
3. Did the S34 P4 bound-transfer change alter any member's classification?
4. Is the sign-flip BAN documented where a future sprint will see it before re-attempting?
5. Do any of these models belong in the Sprint-36 forcing/consultation work rather than in P6?

### How to Verify
Run the harness across the Case-c family and confirm the `case_c_objdef` classification and clean NLP-point residuals. Confirm the BAN is recorded in the Phase-0 gates and the carryforwards. Cross-check `SPRINT_32/CASE_C_CLASSIFIER_DESIGN.md` and `docs/research/convexity_detection.md`.

### Risk if Wrong
- Re-litigating a four-times-refuted hypothesis wastes budget; a reclassification would (harmlessly) reopen a documented finding.

### Estimated Research Time
0.5 hours (harness run across the family)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking

## Unknown 7.1: Are the four P7 fixtures each properly gated on their track's landing, fail-before/pass-after?

### Priority
**Medium** — Fixtures for tracks that do not land cannot be written; the scope is contingent by construction. Getting the gating wrong costs rework, not correctness.

### Assumption
The four P7 property fixtures are each gated on their own track's landing and each demonstrates fail-before/pass-after: **shape12** (head-offset dual → P1), **shape13** (sarf symbolic → P2), a **fawley 2-D second-index** fixture (→ P3), and a **ganges recovery** raw-emit fixture (→ P4). The ganges fixture must follow the `test_sample_pruned_var_l_init.py` skip-if-absent pattern, since `data/gamslib/raw/` is absent in CI.

### Research Questions
1. For each fixture, what is the minimal GAMS shape that isolates the corrected behaviour?
2. Which fixtures can be written from the design alone versus which need the landed code?
3. Does the ganges fixture need raw sources (→ skip-if-absent) or can it be expressed as a synthetic shape in `tests/fixtures/crossterm_shapes/`?
4. Does the existing catalog (`test_ad_crossterm_shapes.py`, shapes 1–11 plus `shape_p4_max_bound_transfer`) accommodate the new shapes without restructuring?
5. If a track REPLANs, is the corresponding fixture simply not written (the S34 precedent — three fixtures correctly deferred)?

### How to Verify
Read `tests/integration/emit/test_ad_crossterm_shapes.py` and `tests/fixtures/crossterm_shapes/`; confirm the `_emit` helper's flags support the new shapes. Review the S33 `test_sample_pruned_var_l_init.py` and the S34 `test_p4_maximize_bound_transfer_sense_aware` as the two patterns. This is prep Task 3's fixture-catalog deliverable.

### Risk if Wrong
- Fixtures written for tracks that REPLAN are wasted work (the S34 precedent handled this correctly by deferring); fixtures *not* written for tracks that do land leave a landed emit path unguarded.

### Estimated Research Time
0.5 hours (catalog read + fixture scoping)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is the PR25 genuine-floor anchor still 75, and must the code anchor advance to the S34-close SHA?

### Priority
**High** — Every no-regression claim in the sprint is gated by `--resolve-changed --since-commit <anchor>`. A stale anchor silently invalidates the sprint's regression evidence, and the floor anchor is the headline KPI's baseline.

### Assumption
The PR25 genuine-vs-methodology anchor is **75** (63 cold + 12 genuine-presolve; methodology 21; all-219 Match 96 = 63 cold + 33 presolve), and the Day-0 code anchor must **advance** to the **S34-close SHA `78ceaead`**. This differs from Sprint 34's situation: the DB has been byte-unchanged since `750803b2` (the S33 close), but `src/` changed during Sprint 34 (the Day-4 P4 sense-aware bound-transfer plus 11 regenerated presolve goldens), so reusing `750803b2` as the checkpoint anchor would not reflect the shipped P4 change.

### Research Questions
1. Does the committed DB still yield genuine floor 75 on recompute?
2. Does the anchor derivation resolve to the expected close merge `78ceaead`? **Note:** Sprint 34's `--grep='SPRINT 33 CLOSED'` pattern does *not* carry over with the number bumped — the S34 close merge body does not contain "SPRINT 34 CLOSED", so match the branch slug / closeout text case-insensitively (`-i -E --grep='sprint34-day13-close|Sprint 34 Day 13.*CLOSE'`) and guard for a non-empty result, since an empty rev makes `git diff --quiet "$S34"..HEAD` vacuously pass.
3. Is `git diff --quiet 78ceaead..HEAD -- src/ scripts/` clean, so the Day-0 baseline can be reused byte-for-byte without a fresh retest?
4. Does `--resolve-changed --since-commit 78ceaead --dry-run` return GO?
5. Which sprint artifacts still reference `750803b2` and must be updated to avoid an accidental stale-anchor run?

### How to Verify
Recompute the PR25 split from the committed `data/gamslib/gamslib_status.json`; derive the anchor portably via the `git log --grep` snippet and record the full SHA plus the DB md5; run the `--resolve-changed --dry-run` GO check. This is prep Task 2's primary deliverable (`BASELINE_METRICS.md`).

### Risk if Wrong
- A stale anchor means every emit-touching PR's no-regression evidence is measured against the wrong baseline — the P4 goldens shipped in S34 would be re-flagged or, worse, real regressions would be masked.
- A wrong floor anchor makes the headline claim (75 → ≥ 76) unverifiable.

### Estimated Research Time
1 hour (PR25 recompute + anchor derivation + GO check)

### Owner
Development team

### Verification Results
✅ **Status:** VERIFIED
**Verified by:** Task 2 (primary)
**Date:** 2026-07-23

**Findings:**
- **PR25 genuine-floor anchor = 75**, reproduced from the committed DB rather than asserted. The all-219 Match 96 splits **63 cold** (`model_optimal`) + **33 presolve** (`model_optimal_presolve`); the 21 methodology members are all presolve matches, so 33 − 21 = **12 genuine-presolve**, and 63 + 12 = **75**. ✓ Both sets are enumerated in `BASELINE_METRICS.md` §4.1 (methodology 21: cpack/etamac/harker/himmel16/irscge/like/lrgcge/marco/markov/mathopt1/mathopt3/mathopt4/mingamma/moncge/paperco/qsambal/sambal/stdcge/tforss/weapons/worst; genuine-presolve 12: bearing/camshape/catmix/cclinpts/launch/maxmin/polygon/ps2_f_s/ps2_s/ps3_s_gic/robert/robustlp). The 21-member set matches the S31/S32/S33 enumeration exactly (their named list plus `mathopt3`, covered there as "+ residue").
- **The Day-0 code anchor MUST advance to the S34-close SHA `78ceaead`** — confirmed with the mechanism, not just the claim. Between `750803b2` and `78ceaead` there is exactly **one `src/` commit** (`b71da11a`, "Sprint 34 Day 4 (P4): sense-aware bound-transfer sign (Option B)") plus **11 regenerated presolve goldens** (agreste, camshape, cclinpts, fawley, korcge, otpop, polygon, ps2_f_s, ps2_s, ps3_s_gic, rocket), while `git diff --quiet 750803b2..HEAD -- data/gamslib/gamslib_status.json` is **clean** (the DB's last modifying commit is still `1568a531`, the S33 Day-11 sample fix). So the DB may be reused byte-for-byte, but re-using `750803b2` as the checkpoint anchor would re-flag those 11 P4 goldens on every checkpoint.
- **The anchor-derivation pattern itself needed correcting.** The S33 close merge body ended with the literal `SPRINT 33 CLOSED`; the S34 close merge does **not** contain "SPRINT 34 CLOSED" (subject `Merge pull request #1602 from jeffreyhorn/planning/sprint34-day13-close`, body "Sprint 34 Day 13: Final retest + CLOSE — …"). The bumped-number pattern returns **empty**, and an empty rev makes `git diff --quiet "$S34"..HEAD` degenerate to `HEAD..HEAD` and pass **vacuously**. The corrected derivation matches the branch slug or closeout text case-insensitively with a non-empty guard (`BASELINE_METRICS.md` §2.1) and resolves `78ceaead`.
- **Day-0 gate GO:** `run_full_test.py --resolve-changed --since-commit 78ceaead --dry-run` → "GO: no emit goldens changed since 78ceaead" (0 changed). `git diff --quiet 78ceaead..HEAD -- src/ scripts/` clean → the committed DB is reused with no fresh retest. DB md5 `6166acab90dcaff8789255f8ada83c54`.
- **Determinism ✅ ×3** `{0,1,42}` on mine / fawley / sample, every md5 **also matching the S34 Day-0 record** — independent confirmation of zero emit drift across the whole of Sprint 34 for those models.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/BASELINE_METRICS.md` §§1, 2.1–2.4, 3, 4.1–4.2; `git log --first-parent 750803b2..78ceaead -- src/`; `git diff --name-only 750803b2..78ceaead -- data/gamslib/mcp/`; the `--dry-run` GO output.

**Decision:** Sprint-35 Day 0 = the Sprint-34 close (Solve 108 / Match 93 / genuine floor 75 / mi 7 / pse 7 / Translate 135 / Parse 142 / all-219 96), with the code anchor pinned at **`78ceaead`** and `750803b2` explicitly retired as historical. The → ≥ 76 conversion map (§4.2) names **P4 ganges/gangesx as the firmest cold-emit contributor**, with P1 mine conditional and P3 fawley contingent under H-b; camcge is excluded as Epic-5-scoped.

---

## Unknown 7.3: What does the Epic-4 `SUMMARY.md` row 35 need?

### Priority
**Low** — A documentation continuation with a well-established format; a Day-12/13 close task.

### Assumption
`SUMMARY.md` row 34 was filled at the Sprint-34 close and a row 35 was added for the (then-renumbered) Quality/PATH theme. After the Sprint-35 insertion in `PROJECT_PLAN.md`, **row 35 must be reconciled** to the Sprint-34-carryforward theme (mine dual / sarf symbolic / fawley diagonal / ganges multi-root / camcge Epic-5 / rocket → Sprint 36), and a **row 36** added for the PATH-consultation theme — mirroring the reconcile-and-append pattern the previous two sprint closes used.

### Research Questions
1. What does `SUMMARY.md` row 35 currently say, and does it carry the pre-insertion theme?
2. What is the established cell format (Theme / Headline KPIs at close / Firm landing(s) / REPLAN'd → carryforward)?
3. Does a row 36 need to be added for the renumbered PATH-consultation sprint?
4. Is the genuine-floor recompute (anchor 75) reflected in the row-34 cells?
5. Is this a Day-12 or a Day-13 close task in the schedule?

### How to Verify
Read `docs/planning/EPIC_4/SUMMARY.md` rows 33–35 and compare against the `PROJECT_PLAN.md` Sprint 35/36 themes post-insertion. Cross-check the S34 Day-12 continuation notes (`SPRINT_34/DAY12_P7_INFRA.md`).

### Risk if Wrong
- A stale theme row in the Epic summary — a documentation inconsistency, no technical impact.

### Estimated Research Time
0.5 hours (SUMMARY.md review)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Confirmed Knowledge (From Sprint 34 and Earlier)

These items were control-confirmed in Sprint 34 (or earlier) and are treated as knowledge, not unknowns, for Sprint 35:

### mine (P1)
- H1 head-label multiplier re-keying is **value-invariant** (S33 Day 2: 22 → 22 nonzero rows, `d_N = d_Nh1` row-for-row), and **H_dual is value-invariant on the cold solve too** (S34 Day 1: the head-anchored prototype compiled with 0 errors but is scalar-identical to baseline — both cold MS-5, profit 16747.0723, 51 INFES). Each `(inequality ⊥ dual)` pair is the same physical pair relabelled `l ↔ l+1`, so GAMS generates the identical scalar MCP. The LP primal is feasible/optimal at 17500, so the MCP failure is a genuine **dual degeneracy**. (`SPRINT_34/DAY1_PROGRESS_NOTES.md`, `SPRINT_33/DAY2_MINE_REPLAN.md`)

### sarf (P2)
- The blow-up is per-column differentiation of `task`'s 369,024 columns at three sites (S1 `acost3` body-diff, S2 `enumerate_variable_instances`, S3 stationarity); the active `taskposs ∧ tech` = 398 is **not statically enumerable** (`taskposs` is runtime-computed). `enumerate_variable_instances` is **foundational** — it builds the `col_to_var` index the whole Jacobian → gradient → stationarity flow iterates for all 142 models — so the change is a coordinated corpus-wide re-architecture, atomic (no safe partial: the gated constraints emit zero per-instance Jacobian entries). Only an equation-level blow-up gate exists today. (`SPRINT_34/DAY6_PROGRESS_NOTES.md`)

### fawley (P3)
- The qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` guard the mbal term carries (control-proven: `max|stat_bq|` 473 → 18.468). The fix surface is a **constraint-index diagonal** in `_add_indexed_jacobian_terms` (~1430 lines, a dozen `sameas` paths, shared with mbal/cesam2/camcge/ps2), and it is a genuinely new pattern: the #1049 guard fires only when the variable has *more* dimensions than the constraint; qsb is the opposite orientation. fawley's +Solve is **H-b** — sameas + all bound transfers → warm residual ~0 but the MCP still solves MS-5 @ 4399.557 (LP opt 2899.25), a non-emit divergence. (`SPRINT_34/DAY5_PROGRESS_NOTES.md`)

### ganges/gangesx (P4)
- The cohort is **three-root, not single-root** (the S34 prep hypothesis was refuted): `$141` (×15, the NaN-cleanup self-referential guard over `.l`-calibration params whose assignment is presolve-gated — **fix written, empirically verified, then reverted/banked**), `$145` (×3, a universal-set `*`-domain cleanup gap), `$149` (×9, an uncontrolled index in the stationarity emit from a CES/LES `prod()` derivative). **No model recovers from `$141` alone.** The `$141` fix was banked rather than shipped because it moved 0 bucket and its slow-emit CGE goldens were un-regenerable in the CI budget. turkey's `$161` (dotted-tuple set declaration) is a distinct root whose `$141`/`$257` are cascades. (`SPRINT_34/DAY11_PROGRESS_NOTES.md`)

### camcge (P5) / rocket
- Step 1 (the `nu_mps_fx` scalar-`fx` transfer, `= mps.m` direct) landed in S32 → `stat_mps` Case-a. The S1∧S2∧S3 degeneracy detector fires **only** on camcge (cold MS-4 @ omega 191.7346; the four CGE siblings cold MS-1). The banked price-pin numéraire variant reaches the correct primal but stays MS-4 (INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`); 3+ sprints of prep failed to reach MS-1 → Epic-5-deferred. rocket is CASE_C_OBJDEF with dual CONSISTENT (1.53e-10) — a forcing problem, not an emit bug; the `--force` survey is exhausted (all MS-5); the FINALIZED PATH-consultation input is submission-ready. (`SPRINT_34/DAY10_PROGRESS_NOTES.md`)

### The shipped S34 P4 (not a carryforward)
- The `--nlp-presolve` bound-multiplier warm-start transfer is now objective-sense-aware: for MAXIMIZE it drops the min-convention sign gate, keeps the active-bound position gate, and transfers `= abs(var.m)`; MINIMIZE emit is byte-identical. A general warm-start-correctness fix with **no +Solve** (agreste's divergence is structural). Guarded by `test_p4_maximize_bound_transfer_sense_aware`. (`SPRINT_34/DAY4_PROGRESS_NOTES.md`)

### Process
- **Always assert `modelstat` before reading an objective off a solve** (the S31 `x.up=inf` measurement error; BANNED for mine). The single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes (PR27). Run the `/tmp` control BEFORE any high-blast-radius `src/` change (PR24). **The failure cohort is multi-root — verify per model.** **Prep `file:line` and root hypotheses are wrong roughly half the time** — verify at Day 0, do not implement against an unverified prep claim. **"No bucket → no `src/`"**, with the S34 P4 exception (fast, regenerable goldens + `--resolve-changed` GO). The genuine-floor ramp is **conditional**: only a cold-emit change lifts it; a warm-start fix yields 0 by definition.

---

## Template for New Unknowns

When adding unknowns during Sprint 35:

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority
**[Critical/High/Medium/Low]** - [One-line impact]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, /tmp controls, experiments, analysis to validate the assumption]

### Risk if Wrong
[Impact if the assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Pre-Day-1 status (Task 1, 2026-07-23):** all 29 unknowns are authored and 🔍 INCOMPLETE. They are scheduled for verification via prep Tasks 2–11 (see the Task-to-Unknown mapping appendix). Sprint 35 is **not yet GO for Day 0** — the GO/NO-GO determination is made in prep Task 12 (Plan Sprint 35 Detailed Schedule), after Tasks 2–11 have resolved the Critical and High unknowns.

**Before Sprint 35 Day 1:**
1. Review all Critical and High priority unknowns (19 total: 7 Critical + 12 High) via prep Tasks 2–11 (see the mapping appendix)
2. Run the `/tmp` control experiment for each track BEFORE any `src/` change (the PR24/PR27 gate)
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED / ❌ WRONG)
4. Adjust the Sprint 35 scope + schedule (Task 12) if any Critical assumption is wrong — in particular, a negative Unknown 1.1 (mine boundary unreachable) should trigger an in-prep P1 REPLAN and a budget reallocation to P4
5. Share findings with the team during sprint planning

**During Sprint 35:**
1. Reference this document daily
2. Add newly discovered unknowns (use the template)
3. Update verification results as each track is implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Sprint 34 → Sprint 35 Day-0 Baseline + Genuine-Floor Re-Baseline | 1.3, 3.3, 4.4, 7.2 | Primary for 7.2 (the PR25 floor anchor 75 + the code-anchor advance to the S34-close SHA); contributes the Day-0 bucket provenance for mine (1.3), fawley (3.3), and ganges/gangesx (4.4) |
| Task 3: Reusable-Tooling Readiness Audit + Slow-Emit CGE Golden-Regeneration Budget + P7 Fixture Catalog | 4.5, 7.1, 7.3 | Primary for the measured golden-regeneration budget (4.5 — the S34 ship-blocker), the P7 fixture catalog (7.1), and the Epic-4 SUMMARY row-35 continuation (7.3) |
| Task 4: `$149` Product-Rule AD Root Analysis + Uncontrolled-Index Cohort Catalog | 4.3, 6.1, 6.2 | Primary for the `$149` localization + hand-derived cross-term (4.3) and the whole cohort catalog: which members `$149` unblocks (6.1) and the multi-root discipline (6.2) |
| Task 5: ganges/gangesx Multi-Root Recovery Design | 4.1, 4.2, 4.3, 4.4, 4.6 | The full Category-4 design: `$141` re-validation (4.1), `$145` universal-set skip (4.2), the `$149` correction spec from Task 4's derivation (4.3, contributes), the per-model recovery verdict + protocol (4.4), turkey `$161` (4.6) |
| Task 6: mine Head-Offset Dual-Architecture Design | 1.1, 1.2, 1.3, 1.4, 1.5 | The full Category-1 design: boundary reachability (1.1), the reconciliation + cold-MS-1 gate (1.2), the 22-row/+16000 re-confirm (1.3), IR sufficiency (1.4), REPLAN prior + disposition (1.5) |
| Task 7: sarf Symbolic/Parametric Emit-Mode Re-Architecture Design | 2.1, 2.2, 2.3, 2.4, 2.5 | The full Category-2 design: three-site completeness (2.1), the O(active) tractability gate (2.2), corpus-safety for the other 141 models (2.3), the 7-term derivation (2.4), the guarded emit / 398 live rows (2.5) |
| Task 8: fawley Constraint-Index-Diagonal Correction + Forcing Hand-Off Design | 3.1, 3.2, 3.3, 3.4 | The full Category-3 design: `max|stat_bq| → 0` (3.1), leak-freedom against mbal/1-D/2-D cohort (3.2), the H-b re-confirm (3.3), the conditional floor lift (3.4) |
| Task 9: camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan | 5.1, 5.2, 5.3, 6.3 | The full Category-5 plan: the Walras MS-1 `/tmp` gate + fallback (5.1), detector scope (5.2), the rocket submission retargeted to Sprint 36 (5.3); also restates the Case-c documented-non-convex status + the sign-flip BAN (6.3) |
| Task 10: Author Phase 0 Acceptance Gates for the Sprint-35 Tracks | 1.2, 2.2, 3.1, 4.3, 5.1 | The per-track `/tmp` control/gate feasibility for P1–P5 (contributes to each track's correctness unknown via the Phase-0 gate design; also encodes the per-model multi-root protocol into the P4 gate) |
| Task 11: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment + Honest KPI Projection | 1.5, 2.2, 3.2, 4.5 | The REPLAN-probability unknowns: mine's fourth-carry disposition (1.5), sarf's timeout re-trigger (2.2), fawley's gate-leak risk (3.2), and whether the golden-regen budget makes P4 shippable in-sprint (4.5) |

**Note:** Task 12 (Plan Sprint 35 Detailed Schedule) integrates all verified unknowns into the day-by-day schedule and makes the GO/NO-GO determination; it does not verify unknowns directly. Task 1 (this document) authors the unknowns. Some unknowns are verified by more than one task (e.g. 1.3 by Tasks 2/6; 2.2 by Tasks 7/10/11; 3.1 by Tasks 8/10; 4.3 by Tasks 4/5/10; 4.4 by Tasks 2/5; 4.5 by Tasks 3/11; 5.1 by Tasks 9/10) — the primary owner is the per-track design task (Tasks 4–9); Tasks 2/3/10/11 *contribute* via the baseline, the tooling/budget survey, the Phase-0 gate, and the REPLAN assessment respectively.

> **Numbering note.** The Sprint-35 `PREP_PLAN.md` has **12** tasks (Tasks 2–11 verify unknowns; Task 12 is the schedule), one more than Sprint 34's 11. The extra task is Task 4 (the `$149` root analysis), promoted into prep because Sprint 34's equivalent question was answered — incorrectly — only at Day 11.

---

**Document Status:** 🔵 Active — Pre-Sprint 35 (29 authored, 0 resolved; verification via prep Tasks 2–11)
**Last Updated:** 2026-07-23
**Owner:** Sprint 35 Planning Team
**Review Frequency:** Daily during Sprint 35
