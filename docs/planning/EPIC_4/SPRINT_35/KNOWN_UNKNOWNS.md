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
✅ **Status:** VERIFIED (negative — the boundary is NOT reachable by any emit-side architecture)
**Verified by:** Task 6 (primary)
**Date:** 2026-07-24

**Findings:**
- **No emit-side dual architecture can supply the +16000 the `x.m = 0`-degenerate boundary requires.** Screened the four candidate architectures against the reachability test (supply +16000 at `stat_x(3,1,1)` without the banned sign flip, without a bound multiplier since `x.m = 0`, without altering the LP primal): **(a)** an explicit head-offset dual variable is either the H_dual re-anchoring S34 proved value-invariant, or a free dual with no complementary inequality (non-square MCP); **(b)** re-declaring the precedence constraint at the base label is a relabeling → value-invariant; **(c)** keeping both labels' multipliers live double-counts the dual (`−2λ = −32000`, worse) and breaks squareness; **(d)** an LP-side reformulation is the only non-invariant lever but changes the primal → out of emit scope (= the PATH-consultation question). All four rejected.
- **The degeneracy is formalized** (§2): the max row needs +16000, but the lag coefficient is `−1·lam_pr` (`≤ 0`, can't be +16000 without the banned sign flip) and `x.m = 0` ⇒ no bound multiplier. mine is a **primal-degenerate LP** — the shadow price lives entirely in the precedence duals with no complementary bound.
- **Corroborating live evidence:** the harness's **secondary** residual rows shift run-to-run (S34 `stat_x(1,3,1)` 1.07 → now 2.00; `stat_x(4,1,1)` 0.815 → 1.33) while the **max row is invariant** (2.37 / −32000) — the signature of multiple optimal dual solutions of a degenerate LP.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` §§1–3; the live `kkt_residual.py mine.gms` (CASE_B, dual CONSISTENT, `stat_x(3,1,1)` −32000); `SPRINT_34/DAY1_PROGRESS_NOTES.md` (the H_dual cold-MS-1 refutation).

**Decision:** the boundary is unreachable by emit → **REPLAN** (Unknown 1.5); mine hands to the Sprint-36 PATH consultation.

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
❌ **Status:** WRONG / REFUTED → REPLAN
**Verified by:** Task 6 (primary)
**Date:** 2026-07-24

**Findings:**
- The hypothesis — "a head-offset dual reconciliation drives the **cold** MCP to MS-1 @ 17500" — is **refuted for every candidate in the emit-side space** (§3), extending S34 Day-1's H_dual refutation (value-invariant on the cold solve) to the whole keying/pairing space. No candidate reaches the `/tmp` cold-MS-1 gate: the reachability screen (Unknown 1.1) rejects all four *before* any control is warranted.
- **This is NOT DESIGN-SPECIFIED.** There is no surviving candidate whose `/tmp` control is merely deferred to Day 1 — the space is screened to zero. The cold-MS-1 gate was already executed by S34 Day 1 for the strongest candidate (H_dual) and refuted; Task 6 proves no other candidate would do better.
- The `/tmp` control spec is recorded for completeness (§5), with the standing note that **the cold solve is the gate, not the warm residual `N → 0`** (un-hittable by a value-invariant keying/pairing change — which is why H_dual compiled cleanly yet drove nothing).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` §3 (candidate scoring), §5 (the control spec); `SPRINT_34/DAY1_PROGRESS_NOTES.md` (H_dual scalar-identical to baseline).

**Decision:** REPLAN → the Sprint-36 PATH consultation (the primal-degenerate-LP question); no `src/`, 18–24 h freed to P4/P6/P7 (Unknown 1.5).

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
**Task-6 addendum (2026-07-24):** the fingerprint aspect is now re-confirmed live. `kkt_residual.py mine.gms` → CASE_B, dual scale 1.35e4, dual transfer CONSISTENT, max row `stat_x(3,1,1)` rel 2.37 / raw −32000 — byte-for-byte the S33/S34 fingerprint; the 22-row `c`-boundary breadth and the +16000 gap hold (`MINE_DUAL_ARCHITECTURE_DESIGN.md` §§1–2). The **S34 P4 sense-aware bound-transfer did not perturb mine's cold emit** (md5 `a394cbc3…`, unchanged; mine's `x.m = 0` makes P4 a no-op). **New observation:** the *secondary* residual rows shift run-to-run (a degeneracy signature — multiple optimal dual solutions) while the max row is invariant. Fingerprint aspect ✅ VERIFIED (Task 6).

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
✅ **Status:** VERIFIED (moot given the REPLAN)
**Verified by:** Task 6
**Date:** 2026-07-24

**Findings:**
- `EquationDef.head_domain_offsets` exists and is populated in `src/ir/parser.py`; it is **consumed in the emit/KKT layer** (`src/emit/emit_gams.py` — 7 hits incl. `head_offset_marginal_index_map`) but **NOT consumed by the stationarity cross-term path** (`src/kkt/stationarity.py` — **0 hits**, re-confirmed live 2026-07-24; `_try_build_param_offset_crossterm` at `:5712`).
- Had a candidate survived the Unknown 1.1 reachability screen, this IR would be its natural carrier and the work would be *wiring the existing IR into `_try_build_param_offset_crossterm`*, not adding an IR capability. **The IR is sufficient; it is not the blocker** — the blocker is that no reachable architecture exists to carry (Unknown 1.1). So this unknown resolves ✅ but is **moot**: sufficiency doesn't matter when nothing survives to be carried.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` §4; `grep head_domain_offset src/kkt/stationarity.py` → 0; `src/emit/emit_gams.py` → 7.

**Decision:** IR sufficient; irrelevant given the REPLAN.

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
✅ **Status:** VERIFIED
**Verified by:** Task 6 (primary)
**Date:** 2026-07-24

**Findings:**
- **REPLAN recommended in prep (before Day 1).** mine is four-times-carried (S32 5th-coupling / S33 H1 / S34 H_dual — all refuted), and Task 6 screens the *entire* remaining emit-side candidate space to zero (Unknown 1.1). A fifth 18–24 h emit hypothesis on an exhausted lever is the least defensible allocation in the plan; the honest next step is the consultation, not a fifth hypothesis.
- **Disposition:** hand mine to the **Sprint-36 PATH-author consultation** as the canonical **primal-degenerate-LP** question (*how should a square MCP represent a primal-degenerate LP boundary whose shadow price lives entirely in a constraint dual with no complementary bound?*) — alongside rocket's Case-c question. mine stays `model_infeasible`; no `src/` shipped.
- **Budget reallocation:** the P1 18–24 h → **P4** (Task 5's ganges/gangesx three-root recovery — the designated best shot) first, then **P6/P7**. Surfacing the REPLAN in **prep** (vs S34's Day-1) lets P4 plan against the full freed budget from Day 0.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` §6; the four-sprint refutation chain (`SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`, `SPRINT_33/DAY2_MINE_REPLAN.md`, `SPRINT_34/DAY1_PROGRESS_NOTES.md`).

**Decision:** P1 contributes 0 in-sprint Solve / 0 genuine floor; reallocates to P4/P6/P7. Handed to Task 9 (mine joins rocket as a Sprint-36 consultation question), Task 11 (projection), Task 12 (no Day-1–5 slot for P1).

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
✅ **Status:** VERIFIED
**Verified by:** Task 7 (primary)
**Date:** 2026-07-24

**Findings:**
- The three enumeration sites are re-confirmed **live** and are the complete set: **S1** the per-column constraint diff (`src/ad/constraint_jacobian.py:1002–1013`, differentiating `acost3.. cost = sum((g,t,m,n)$taskposs, oc·task)` against each `task` column); **S2** `enumerate_variable_instances` (`src/ad/index_mapping.py:327`), called from `build_index_mapping` (`:634` → `col_to_var`) and `_precompute_variable_instances` (`constraint_jacobian.py:78`); **S3** `stat_task(g,t,m,n)` materialization in `src/kkt/stationarity.py`.
- **No fourth materialization site.** The objective-gradient (`gradient.py:287/453`) and complementarity (`complementarity.py:367/512`) call sites also enumerate `task`, but they *consume* the same column set — they are additional consumers, not new loci (this is why the corpus-safety surface is 6 call sites, Unknown 2.3). The only blow-up gate that exists is the **equation**-level `_is_blowup_dynamic_subset_equation` (`index_mapping.py:402`); there is no variable-level gate.
- **Counts re-verified:** g = 16, t = 24, mn = 31 → `task(g,t,mn,mn)` = **16·24·31·31 = 369,024** declared; active `taskposs∧tech` = **398** (both runtime-computed, not statically enumerable).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §1; the live source loci; `data/gamslib/raw/sarf.gms` (`:394` task decl, `:371` taskposs, `:454` acost3).

**Decision:** three sites, complete; the fix must be atomic across S1/S2/S3 (Unknown 2.2).

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
✅ **Status:** VERIFIED (baseline measured); the post-change timing is DESIGN-SPECIFIED (in-sprint)
**Verified by:** Task 7 (primary)
**Date:** 2026-07-24

**Findings:**
- **Measured the current emit wall-clock: > 303 s and NON-TERMINATING.** `.venv/bin/python -m src.cli data/gamslib/raw/sarf.gms` was killed at a 300 s cap with **no output produced** — the O(369K) cost, stronger than the design's ">75 s" and consistent with the pipeline `translate_failure` (the 600 s harness timeout). The emit log shows the loop walking the full Cartesian with `UserWarning: … taskposs/equipposs cannot be evaluated statically … Including unevaluable instances by default` — the runtime-gated conditions can't prune at compile time.
- **Pass threshold specified:** single-digit seconds (O(active = 398) / O(constraints); the srpchase ~2.9 s reference). Measurement method pinned (`/usr/bin/time -p … -o sarf_mcp.gms`, `real` seconds, clean tree).
- **Partial-improvement pre-classification (PR20):** an improvement that does not cross the threshold (e.g. 303 s → 90 s but still failing) is a **REPLAN, not progress** — no "faster but still failing" partial credit.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §6; the timed emit (killed at 300 s, no output); the emit log's static-unevaluability warnings.

**Decision:** the baseline (> 303 s) is the O(369K) tractability gap; the post-change O(active) figure is an in-sprint executed result (DESIGN-SPECIFIED). The gate is Task 10's Phase-0 item.

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
✅ **Status:** VERIFIED
**Verified by:** Task 7 (primary)
**Date:** 2026-07-24

**Findings:**
- **The symbolic-column concept** is designed: `task` presents as a single guarded domain expression `(domain=(g,t,m,n), guard=taskposs∧tech)` with **one** `col_to_var` entry instead of 369,024, never expanded; its cross-terms come parametrically (Unknown 2.4) and GAMS instantiates the 398 live rows from the emitted guard.
- **The corpus-safety argument is explicit.** All **6** `enumerate_variable_instances` call sites enumerated (the complete surface): `index_mapping.py:634` (build_index_mapping / col_to_var), `constraint_jacobian.py:78` (_precompute_variable_instances / S1), `gradient.py:287` & `:453` (objective gradient), `complementarity.py:367` & `:512` (complementarity). The change is a **branch gated on a runtime-blow-up predicate** (a variable whose declared Cartesian is large *and* whose active subset is a runtime-computed guard the emit can't statically prune) — **sarf-only by construction**, so on the 141 other models the predicate is false for every variable and all 6 sites execute the **unchanged** enumeration path, keeping their `col_to_var` byte-identical and determinism (PR12) preserved.
- **Residual risk:** the predicate must be *provably* false on all 141 models — "at the harness level" is not "byte-proven." That proof is the full-corpus regression harness (141 byte-identical goldens + determinism ×3, §7), which is why the design is **not landable without it**.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §§2–3, §7; the live 6-call-site enumeration (`grep enumerate_variable_instances src/`).

**Decision:** corpus-safe by a sarf-only-by-construction predicate; the 141-byte-identical-golden harness is the shippability gate (Task 10).

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
✅ **Status:** VERIFIED (no term failed re-derivation)
**Verified by:** Task 7 (primary)
**Date:** 2026-07-24

**Findings:**
- The parametric cross-term path is designed against the banked S33 **7-term `stat_task`**, re-verified **term-for-term** against the `sarf.gms` constraint bodies: [1]–[2] `tbal` (`:426`) with the `tadj` harvest-c adjustment (`:424/:428`); [3] labor balance (`:439`); [4]–[5] `equipb1`/`equipb2` (`:412–413`); [6] `acost3` (`:454`, the S1 parametric ∂ → `oc(g,m,n)·nu_acost3`); [7] `task.lo = 0`. **No term failed re-derivation** — the banked form is correct as written.
- **Every multiplier is over the stat equation's own domain** (`nu_tbal(g,t)`, `lam_labor(t)`, `lam_equipb1(m,t)`, `lam_equipb2(n,t)`, `nu_acost3`, `piL_task(g,t,m,n)`) with **no set-name-literal (quoted-set-name) indices** — the guard against the reverted Sprint-26 `243fe578` `nu_slack("srn")` anti-pattern. The compile-clean scan `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` must return nothing.
- A silently-wrong `stat_task` is the worst failure mode on this track (KPI moves while correctness regresses, uncaught by the timing gate), so the 7-term re-derivation is the correctness anchor; the fix surface (S1/S2/S3 short-circuits + the parametric path in `stationarity.py`) is a hypothesis to re-trace at implementation.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §4; `SPRINT_33/SARF_EMIT_SUBSYSTEM_DESIGN.md` §3.1; `data/gamslib/raw/sarf.gms` constraint bodies.

**Decision:** the 7-term derivation is the parametric path's correctness target; the anti-pattern scan is the structural guard (Task 10 gate).

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
✅ **Status:** VERIFIED
**Verified by:** Task 7 (primary)
**Date:** 2026-07-24

**Findings:**
- The guarded emit `stat_task(g,t,m,n)$taskposs(g,t)` (with per-term `$tech`/`$equipposs`/`sameas` guards) + `task.fx(...)$(not (taskposs(g,t) and tech(g,m,n))) = 0` yields exactly the **398** live rows: the `$(not active)` fixing guard **exactly complements** the `$taskposs∧$tech`-active set, so the square-system count is `variables − fixed = active = 398`; the fixed columns' `stat_task` rows drop under MCP matching (the mine non-`d` precedent). Landing check: compile `sarf_mcp.gms`, assert exactly 398 `stat_task` rows + a square MCP.
- The full-corpus regression harness (§7) is specified: atomic landing; 141 byte-identical goldens (`--resolve-changed --since-commit 78ceaead` reporting sarf as the only changed golden); determinism ×3 `{0,1,42}`; the 7-term + anti-pattern scan; a **shape13** property fixture (a synthetic runtime-gated multi-dim variable, fail-before/pass-after — the P7 catalog entry).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/SARF_SYMBOLIC_EMIT_DESIGN.md` §5, §7.

**Decision:** the guarded emit + `task.fx` produce exactly 398 rows; the harness is the shippability gate. In-sprint disposition: **DEFER** (design complete, foundational/atomic/lowest-leverage; budget → P4).

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
✅ **Status:** VERIFIED (baseline); DESIGN-SPECIFIED (the "→ 0" closure)
**Verified by:** Task 8 (primary)
**Date:** 2026-07-24

**Findings:**
- **The `stat_bq` over-sum gap is re-confirmed live.** `kkt_residual.py fawley.gms` → CASE_B, dual scale 486, dual transfer CONSISTENT, `stat_bq(res-arab-l,fuel-oil)` rel **0.973** / raw **473** — identical to the S34 figures. The `qsb`/`pbal` cross-terms in `stat_bq(c,cf)` (`data/gamslib/mcp/fawley_mcp.gms:238`) sum over `cfq__` **without** the diagonal `$(sameas(cfq__,cf))` the `mbal` term carries; since `bq`'s second index `cf` = the constraint's own index `cfq`, `∂qsb(cfq,·)/∂bq(c,cf)` is nonzero only on `cfq=cf` → the over-sum.
- **The `/tmp` control target is `max|stat_bq| → 0`** (machine zero), **not** the 96% partial (473 → 18.468). Post-P4 the 18.468 residue was the cc-dist bound-transfer cell (shipped S34 Day 4), so on the current tree the `sameas` fix alone is expected to reach 0 — the in-sprint `/tmp` control **will** verify this closure (DESIGN-SPECIFIED — **not executed in this prep**; `modelstat` asserted). The gate is scoped to `max|stat_bq|`, **not** the harness's global max residual (which retains the emit-correct `stat_trans` non-emit residual, Unknown 3.3).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §1, §5; the live `kkt_residual.py fawley.gms` (CASE_B, stat_bq 0.973/473); `data/gamslib/mcp/fawley_mcp.gms:238`.

**Decision:** the emit gap is intact and P3-fixable; the `→ 0` closure is the in-sprint `/tmp` gate (Task 10).

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
✅ **Status:** VERIFIED
**Verified by:** Task 8 (primary)
**Date:** 2026-07-24

**Findings:**
- **The constraint-index diagonal is characterized as a predicate:** a Jacobian cross-term where the constraint's **own** (summed) domain index occupies the **variable's non-summed (stat) index position**, requiring `$(sameas(<summed-constraint-index>, <variable-stat-index>))`. For fawley: qsb `nu_qsb(cfq__,l,s)`, variable `bq(c,cf)`, `cfq__` summed while occupying `cf`'s position → guard `$(sameas(cfq__,cf))`.
- **Distinguished from the existing guards:** **#1049** (`src/kkt/stationarity.py:7176`, `len(var_domain) > len(mult_domain)`) fires on the **variable-heavier** orientation — qsb is constraint-heavier (3-D constraint, 2-D var), the **opposite**, so #1049 does not co-fire; **#1110/#1111** (`_get_or_create_fresh_alias:4496`) handle the **variable-index** diagonal (the mbal term, already guarded), not the constraint-index diagonal. The new predicate keys on a **constraint** domain index in the variable's stat position, so it leaves the mbal (variable-summed) term untouched.
- **Guard placement + precedence** designed (in `_add_indexed_jacobian_terms:5861`, after the #1049 check, disjoint from #1110/#1111; #1104's alias machinery preserved) with a precedence argument against each of the dozen `sameas` paths (the leak risk); **leak-free requirement operational** (no mbal term change; 1-D core polygon/ps2_s/ps3_s_gic byte-identical); **2-D-cohort regression harness** = cesam2/camcge/ps2_f_s/ps2_s/ps3_s_gic/polygon byte-identical + `--resolve-changed --since-commit 78ceaead` reporting fawley as the only changed golden + determinism ×3. The fix surface is a labelled hypothesis (PR24).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §§2–4, §6; `src/kkt/stationarity.py:5861` (`_add_indexed_jacobian_terms`), `:7176` (#1049), `:4496` (`_get_or_create_fresh_alias`); the 6 cohort goldens present on the tree.

**Decision:** the predicate + guard + harness are specified; a leak-free landing is the gate (Task 10). Any mbal/cohort change = the gate-leak REPLAN exit (Unknown 3.4 / §8).

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

**Task-8 addendum (2026-07-24) — H-b re-confirmed live and STRENGTHENED (Task 2 required the re-measurement).** Because the S34 P4 change regenerated `fawley_mcp_presolve.gms` and fawley is **MAXIMIZE** (so P4's sense-aware `abs(var.m)` transfer is in its warm path), the H-b figures were re-measured, not inherited. Result: the **stat_bq gap is unchanged** (rel 0.973 / raw 473, dual scale 486, CASE_B, CONSISTENT), but the **max-residual row is now `stat_trans(tr-2)` (rel 1.00 / raw −488)** — a row S34 did not report. `stat_trans(tr).. sum(c, at(c,tr)*nu_mbal(c)) - piL_trans(tr)` is **emit-correct** (a clean `∂mbal/∂trans` cross-term), so its residual is a **genuine non-emit divergence** — which **strengthens H-b** (the warm KKT point fails even emit-correct rows, likely a P4-moved-warm-point effect on a degenerate infeasible solve) and **scopes the P3 gate to `max|stat_bq|`**, not the global max residual. fawley still solves MS-5 @ 4399.557 (LP opt 2899.25) with the residual closed → the +Solve is non-emit → P5 forcing. H-b aspect ✅ VERIFIED (Task 8).

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
✅ **Status:** VERIFIED (negative — no in-sprint floor gain)
**Verified by:** Task 8 (primary)
**Date:** 2026-07-24

**Findings:**
- Under **H-b** (Unknown 3.3, re-confirmed + strengthened) fawley does **not** cold-match, so the +1 genuine floor is **contingent on forcing (P5)**, not an in-sprint P3 deliverable. The `sameas` correction **does** change fawley's cold emit (a genuine cross-term fix, so it *could* count toward the floor under the PR25 definition) — but fawley stays `model_infeasible` with or without it (the MCP diverges MS-5, and now an emit-correct `stat_trans` row is a co-equal residual).
- So P3's correction is a **correctness-only landing with 0 in-sprint bucket**; the floor credit accrues **only if** a `--force` lever later produces a cold match at 2899.25 (classified per the PR25 genuine-vs-methodology definition). The +Solve and the floor gain are both P5-forcing-contingent, not P3.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` §7, §1.3; the live MS-5 @ 4399.557 / LP-opt 2899.25 H-b figures.

**Decision:** P3 delivers 0 in-sprint bucket; the +1 floor is forcing-contingent (P5). The correctness fix is worth landing *if leak-free and cheap*, but it is not a bucket lever and must not displace P4.

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
✅ **Status:** VERIFIED
**Verified by:** Task 5 (primary)
**Date:** 2026-07-24

**Findings:**
- The banked `$141` fix applies **cleanly** to the current tree: `_param_assignment_has_division` (`src/emit/original_symbols.py:137`) and `emit_post_assignment_na_cleanup` (`:152`) are unchanged in location and signature. Reconstructed the helper `_param_assignment_references_varref_attr` (mirroring the division helper; skips params whose assignment contains a `VarRef` with a non-empty `.attribute`, i.e. `.l`/`.m`/…) + the skip in the cleanup loop, exactly per `SPRINT_34/DAY11_PROGRESS_NOTES.md`.
- **Re-verified empirically: `$141` 15 → 0.** Applied the fix in a scratch tree, re-emitted ganges (~200 s), compiled (`gams a=c`): the 15 `$141` markers are gone. **`$145×3` and `$149×9` remain** — ganges still fails to compile (the multi-root proof; Unknown 4.4). Scratch patch **reverted**; `src/` clean (design task).
- **Root:** ganges calibrates from a solved base equilibrium (`adst(i)=dst.l(i)/…`, `cg(i)=dat(…)/pc.l(i)`, `deltax(i)=(z.l/g.l)**…`), so those assignments are presolve-gated and the param is declared-but-unassigned in the cold MCP → the NA-cleanup guard reads an unassigned symbol → `$141`.
- **Collateral:** the fix is general — it drops the cleanup guard for any `.l`-referencing division param. Beyond ganges/gangesx that touches ~9 more `.l`-calibration models (chakra, dinam, gancnsx, prolog, saras, senstran, shale, tfordy, turkey) but **NOT the data-calibrated CGE cluster** (irscge/lrgcge/moncge/stdcge calibrate from data params `Xp0`/`Y0`/`F0`, not `.l` — verified). Golden-byte drift, no bucket change → `--resolve-changed`-safe but must be regenerated at landing.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md` §1; the scratch re-emit + `gams a=c` tally (`$141` 15→0); `src/emit/original_symbols.py:114–214`; `src/ir/ast.py:53` (VarRef `.attribute`).

**Decision:** the `$141` fix is landing-ready and low-risk; it ships as **step 1** of the three-root P4 sequence (not alone — it recovers nothing without `$145`+`$149`). Collateral goldens enumerated via `--resolve-changed` and regenerated (scoped `--models`, Task 3) at landing.

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
✅ **Status:** VERIFIED
**Verified by:** Task 5 (primary)
**Date:** 2026-07-24

**Findings:**
- `$145` is the NaN-cleanup guard emitted over `series(*,years)` — a param whose **first domain is the universal set `*`** (`Table series(*,years)`). Its assignments divide (`series("pim1",years)=series("pim1",years)/series("usdefl",years)`), so the cleanup filter fires and emits `series(*,years)$(NOT (series(*,years) > -inf …)) = 0;`. `*` is valid in a *declaration* but **invalid as an assignment/`$`-guard index** → GAMS `$145` ("Set identifier or quoted element expected"), ×3.
- **Independent of `$141`, two ways:** (a) `series` references **no `.l`** (it divides one `series` element by another), so the `$141` skip does not cover it; (b) `series` **is** assigned unconditionally (source lines 310+), so it is not a declared-unassigned `$141`. The `$141`-only re-emit (Unknown 4.1) leaves the 3 `$145` intact — direct confirmation.
- **Fix designed:** in the same cleanup loop, `if any(d == "*" for d in param_def.domain): continue` — skip universal-set-domain params (their index space is not a named set the guard can iterate; the guard is structurally malformed regardless of NA-ness). Minimal reproducing shape: `Table p(*,s)` with a division assignment → `p(*,s)$(NOT …)` → `$145`.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md` §2; `data/gamslib/raw/ganges.gms:251,310–319` (the `series` table + division assignments); the golden line `series(*,years)$(NOT …)`; the `$141`-only re-emit leaving `$145×3`.

**Decision:** `$145` ships as **step 2** of the P4 sequence (a bounded cleanup-pass skip, low-risk). Blast radius = models with a `*`-domain division-assignment param (rare; enumerate at landing via `--resolve-changed`).

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
✅ **Status:** VERIFIED
**Verified by:** Task 4 (primary)
**Date:** 2026-07-24

**Findings:**
- **Reproduced live:** ganges emit is byte-identical to the committed golden (md5 `72c5d5f268e9dad458f61f58491872c5`); GAMS `a=c` compile gives `$141×15 / $149×9 / $145×3` (+ `$300`/`$257` cascades). **All 9 `$149` are on one equation — `stat_pc(i)`, golden line 1002.**
- **The offending index is `j`.** The product-derivative of `prod(j, (pc(j)/pc00(j))**ac(j,r))` w.r.t. `pc(i)` emits a `(df/dx)/f` factor that references `pc(j)`/`pc00(j)`/`ac(j,·)` **outside the `prod(j,…)` scope** → `j` uncontrolled → `$149`. Two renderings on the same line: **chunk 1** wraps in `sum(j,…)` and renames the prod bound to `j__` (compiles); **chunk 2** is the collapsed `prod(j,…) * (…j…)` form, un-aliased → free `j`.
- **Hand-derived correct cross-term:** `∂/∂pc(i)[prod(j,(pc(j)/pc00(j))**ac(j,r))] = prod(j,(pc(j)/pc00(j))**ac(j,r)) * ac(i,r)/pc(i)` — `i` controlled, no free `j` (numerically cross-checked on a 2-element set). Three emit forms given (simplified `·ac(i,r)/pc(i)` [recommended, safest]; prod-ratio `·f'(i)/f(i)`; exp-sum-log); form 1 recommended.
- **Localized to a two-layer `file:line` hypothesis** (labelled per the standing lesson): `src/ad/derivative_rules.py:_diff_prod` (~3395, the #1330 `symbolic_name_match` collapsed branch returns `expr * (body_deriv/body)` and *delegates* index-safety to the emitter) + `src/emit/expr_to_gams.py:collect_index_aliases` (:757, renames a Prod bound only on domain/enclosing-binder collision, **not** on a sibling-factor reference — the failing link). The **AD layer, not a cleanup pass, is the surface** (contra the general prior). The distinguishing feature isolating ganges/gangesx: the **cross-index** case (prod over `j`, differentiate w.r.t. `pc(i)`, `j ≠ i`), vs the name-match case the 18 working prod-models use.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md` §§1–3, §5; the live emit + `gams a=c` listing; `src/ad/derivative_rules.py:3272–3410`; `src/emit/expr_to_gams.py:723–770`.

**Decision:** the `$149` correction is form 1/2 at the AD layer (`_diff_prod`, option (a)) — Task 5 specifies it, sequenced after `$141`/`$145`, gated against the 18-model prod-in-stationarity regression set (§5.1). Not the `stationarity.py` cleanup surface the prior assumed.

---
**Task-5 contribution (2026-07-24):** the `$149` correction is carried into the P4 recovery design (`GANGES_RECOVERY_DESIGN.md` §3) as the **deepest, REPLAN-bearing step** of the three-root sequence (`$141`→`$145`→`$149`). The AD-layer surface (`_diff_prod`, form 1/2) and the 18-model prod-in-stationarity regression set (lmp2 flagged) are handed to Task 10's Phase-0 gate. Task 4 remains the primary; this task does **not** build the fix.

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
🔍 **Status:** DESIGN-SPECIFIED (the protocol + sequence are designed; the recovery verdict is NOT executed)
**Verified by:** Task 5 (design) — supersedes the Task-2 provenance-only status below; the verdict is an in-sprint P4 execution result
**Date:** 2026-07-24

**Findings:**
- **The multi-root sequence is empirically confirmed** (not asserted): re-emitting ganges with **only** the `$141` fix leaves `$145×3 + $149×9` and still fails to compile. So **no bucket moves until all three roots land** — the S34 finding, re-proven. The landing sequence `$141`→`$145`→`$149` is each `--resolve-changed`-gated with per-step expected bucket outcome (all `path_syntax_error` until step 3).
- **The per-model verification protocol is designed** (§5): for ganges and gangesx **independently** — emit → compile → count residual `$NNN` → translate → solve (cold + presolve, `modelstat` asserted) → bucket → match — with the explicit rule that compile-clean-but-not-solving is *not* a recovery (it is a bucket change, `path_syntax_error → model_infeasible`).
- **But the recovery verdict itself is NOT executed here.** The `$149` AD fix is not built, and `$149`/`$145` were not applied — so whether all three roots together make ganges *and* gangesx compile, solve, and match is **unverified**. Marked **DESIGN-SPECIFIED**, deliberately: this is the exact assumption Sprint 34 got wrong (its "one fix recovers both" prep hypothesis), and a bucket read is not evidence for it. It becomes ✅ only when the in-sprint P4 execution runs §5's protocol per model.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md` §4, §5; the `$141`-only re-emit tally (`$145×3 + $149×9` remain); `SPRINT_35/BASELINE_METRICS.md` §5 (ganges/gangesx Day-0 provenance, Task 2).

**Decision:** the per-model protocol (§5) is encoded into the P4 Phase-0 gate (Task 10). Task 11's projection uses **+2 (ganges, gangesx)** as *contingent*, not firm — the verdict resolves in-sprint.

---

**Prior (Task 2, 2026-07-23) — provenance-only, superseded above:** ganges and gangesx are both `path_syntax_error` `likely_convex` candidates at Day 0 (`model_status = None`, never reached solve). Recorded but explicitly not treated as evidence of a shared fate. See `SPRINT_35/BASELINE_METRICS.md` §5.

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
✅ **Status:** VERIFIED — **and the Sprint-34 premise is REFUTED**
**Verified by:** Task 3 (primary)
**Date:** 2026-07-23

**Findings:**
- **The four slow-emit goldens ARE regenerable in budget.** Measured per-model emit wall-clock, run alone: gangesx **151.00 s** · clearlak **191.84 s** · ganges **202.57 s** · turkpow **442.15 s** (sum 987.56 s / 16.5 min). **Every one clears the 600 s per-emit subprocess timeout** (`scripts/gamslib/batch_translate.py:265`); turkpow is the binding case with ~26 % headroom.
- **The scoped regen completes in 8.2 minutes.** `check_golden_staleness.py --models ganges,gangesx,clearlak,turkpow` → `real 489.63 user 1356.92`, **0 timeouts, all 4 clean**. All four run concurrently under the 6-worker pool (`user`/`real` ≈ 2.8× confirms real parallelism), so wall-clock is set by the slowest model, not the sum — and **turkpow stayed under 600 s even under four-way contention**, so the parallel-contention risk did not materialise.
- **The S34 soft-timeout was full-sweep contention, not model cost.** `make regen-goldens` sweeps **all 170** goldens at `MAX_WORKERS = 6` (`check_golden_staleness.py:36,:132`); the slow four contend with 166 others and hit the 600 s per-emit timeout, which `check_one` records as a **soft** `"timeout"` — explicitly *"couldn't verify in budget", NOT drift* (`:88–93`). The scoping flag that avoids this, **`--models`, already exists** (`:124`) — **no new tooling is needed to unblock P4**.
- **No latent drift:** all four re-emits are **byte-identical** to their committed goldens (ganges md5 `72c5d5f268e9dad458f61f58491872c5` both sides). So when P4's fixes land, the golden diff is wholly attributable to them.
- **Cost model:** a clean golden = 1 emit; a **drifted** golden under `--fix` = **2 emits** (the determinism guard re-emits and requires byte-identity before overwriting, `:105–112`). The four models have **cold goldens only** (no `_presolve` variants) → P4 refreshes **4 goldens, not 8**.
- **Budget:** scoped `--fix` with all four drifting ≈ **16.4 min**; an optional separate determinism ×3 pass ≈ 24.6 min; the follow-on `--resolve-changed` re-solve ≤ 8 min. **Worst case ≈ 50 min; realistic ≈ 25 min.**

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` §§2, 3.1–3.5; the four `/usr/bin/time -p` emit runs; the scoped `check_golden_staleness.py --models …` run; `cmp` against the committed goldens; `SPRINT_34/DAY11_PROGRESS_NOTES.md` §45 (the refuted claim).

**Decision: P4's golden regeneration FITS A NORMAL ≤ 12 h SPRINT DAY — no dedicated overnight slot is required** (Task 12 schedules against this). Prescribed invocation on the P4 landing day: `check_golden_staleness.py --models ganges,gangesx,clearlak,turkpow --fix`, then `run_full_test.py --resolve-changed --since-commit 78ceaead`. **Do NOT run the unscoped `make regen-goldens`** — that is the 170-golden sweep whose contention caused the S34 soft-timeout. **Consequence:** Sprint 34 banked its verified `$141` fix on two grounds — 0 bucket recovered, *and* un-regenerable goldens. **The second ground is removed.** The first still stands (no bucket → no `src/`), but the S34-P4 exception criteria (fast, regenerable goldens + `--resolve-changed` GO) are now **satisfiable** for this cohort. Task 11 should weigh P4 with the golden constraint lifted.

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
✅ **Status:** VERIFIED
**Verified by:** Task 5 (primary)
**Date:** 2026-07-24

**Findings:**
- turkey's `ao` set is declared with dotted-tuple elements (`grains.wheat, grains.corn, …, industrial.tea, fruits.grape, …`) with inconsistent quoting; the emit produces set elements GAMS rejects → `$161`, ×6, on the set declaration (compiled `gams a=c`: `$161×6 / $141×1 / $257×1`). Its `$141`/`$257` are **cascades** of `$161`.
- **Disjoint from the ganges roots:** a **set-declaration emit** surface, unrelated to the NA-cleanup (`$141`/`$145`) or the product-rule (`$149`) — and **turkey has no `$149`** (Task 4). Shares no root, fix surface, or model with the ganges recovery.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_RECOVERY_DESIGN.md` §7; the turkey `gams a=c` compile (`$161` on the `ao` declaration).

**Decision: P6, not P4.** Folding turkey into P4 would conflate two unrelated efforts and dilute the P4 gate. It is a bounded, standalone P6 item (quote dotted-tuple set elements consistently in the set-declaration emit) with its own `--resolve-changed` gate; a recovery would be +1 Solve on the P6 track.

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
✅ **Status:** VERIFIED — **and the S34 impact framing CORRECTED**
**Verified by:** Task 4 (primary)
**Date:** 2026-07-24

**Findings:**
- **`$149` is a GAMS error *code*, not a single *root*.** All seven cohort goldens compiled (`gams a=c`) and catalogued by code × count. **Only ganges and gangesx carry the product-rule `$149`** (on `stat_pc`, from the `prod` derivative). dinam / indus / turkpow / clearlak carry `$149` markers on **entirely different constructs** — a `sameas` alias-sum (`stat_v`), a raw data-assignment power term (`yc … **gammafrt`), a lag-KKT sum (`stat_zt`), and a set/element data assignment (`tmp1 = sum(nn$leaf(nn), snprob(leaf))`) — sharing only the error number.
- **The cohort is more multi-root than S34 recorded:** dinam `$140×5/$8×3/$149×3/$37×2/$171×2/$141×1`; indus `$141×8/$140×5/$130×4/$409×3/$149×3/$148×2/…` (`$141`-dominated); turkpow `$170×6/$171×5/$149×1/$141×1` (`$170/$171`-dominated); clearlak `$352×4/$141×2/$149×1` (`$352`-dominated — **not `$171`**, correcting S34); turkey `$161×6/$141×1` (**no `$149`**). `$257`/`$300` are cascades.
- **"What still fails after a correct `$149` fix":** ganges/gangesx → `$141×15`+`$145×3` remain (need all three roots, no single-root recovery); dinam/indus/turkpow/clearlak → **unchanged in practice** (`$149` is 0–3 unrelated markers each, dominated by other roots); turkey → unaffected.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md` §4; seven `gams a=c` compiles of the committed goldens.

**Decision:** the clean `$149`-product-rule beneficiaries are **ganges + gangesx only** → the honest P4 target is **+2**, not "the `$149` half of six models" (the carryforward framing is refuted). dinam/indus/turkpow/clearlak are **P6 residual**, not P4 `$149` beneficiaries.

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
✅ **Status:** VERIFIED
**Verified by:** Task 4 (primary)
**Date:** 2026-07-24

**Findings:**
- The multi-root discipline is upheld **and extended by live per-model compile**: the `path_syntax_error` cohort is more multi-root than S34's characterization (which said "dinam/indus `$140`+`$149`; turkpow/clearlak `$149`+`$171`; turkey `$161`"). Reality: dinam adds `$8/$37/$171/$141`; indus is `$141`-dominated (×8); turkpow is `$170/$171`-dominated with only `$149×1`; clearlak is `$352`-dominated (**S34's `$171` attribution is wrong**) with `$149×1`; `$257`/`$300` are cascades, not roots.
- **ganges and gangesx were verified independently** (not inferred one from the other): both compile to the identical `$141×15/$149×9/$145×3` profile with the same `stat_pc` product-rule root — confirmed by two separate compiles, not assumed from their shared NLP objective.
- No model recovers from a single root (S34's core finding re-confirmed and generalized to the whole cohort).

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/GANGES_149_PRODUCT_RULE_ANALYSIS.md` §4 (per-model code×count table + cascade annotation); the seven compiles.

**Decision:** every P4/P6 recovery claim is gated on a per-model emit → compile → count → solve → bucket → match check (encoded into the P4 Phase-0 gate, Task 10). The prep root hypotheses in the carryforward are corrected here, once again validating the "verify per model" discipline.

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
✅ **Status:** VERIFIED
**Verified by:** Task 3
**Date:** 2026-07-23

**Findings:**
- **Zero new diagnostic-tool code for Sprint 35** — a pure reuse, as in Sprint 34. All seven reused tools confirmed present on `main` at the Day-0 anchor, three exercised live this task (`--resolve-changed --dry-run` = GO; the scoped `check_golden_staleness.py --models`; four `src.cli` emits): `kkt_residual.py` (with `reclassify_objdef_case_c` at `:621`, the `case_c_objdef` verdict at `:466`), `check_presolve_divergence.py`, `check_golden_staleness.py` (**`--models` at `:124`**), `run_full_test.py --resolve-changed`, `src/cli.py --force` (`:207`), the AD cross-term catalog (shapes 1–11 + `shape_p4_max_bound_transfer`, with the `nlp_presolve`-aware `_emit` helper), and the `test_sample_pruned_var_l_init.py` raw-emit skip-if-absent pattern.
- **The four P7 fixtures are catalogued** with gating track, shape, pattern and home: **shape12** (head-offset dual → P1), **shape13** (sarf symbolic → P2), **fawley 2-D second-index** (→ P3, the #1049-guard's *opposite* index orientation) — all three synthetic and in-process (sub-second, no regen cost) — and the **ganges recovery** fixture (→ P4), which **must be raw-emit + skip-if-absent** because the defect only manifests on the real model's CES/LES structure and `data/gamslib/raw/` is gitignored/absent in CI. It should assert on the emitted text rather than invoking GAMS, exactly as the sample guard does.
- **Each fixture lands only with its own track's fix.** If a track REPLANs, its fixture is simply not written — the correct outcome, per S34's Day-12 deferral of three fixtures (`SPRINT_34/DAY12_P7_INFRA.md` §18).
- **New finding — `indus` cannot serve as a P4/P6 regression signal.** It is in the golden-staleness **allowlist** for cross-environment byte non-determinism (#1461: hash-seed-stable on macOS, ~45 bytes different on ubuntu CI), so its gate is suppressed. Since indus is a **`$149` cohort member** (`$140` + `$149`), Task 4's catalog and Task 5's per-model protocol must verify it by **compile-error count, not golden diff**.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` §§1, 4, 4.4, 4.5; the tool inventory; `scripts/sprint_audit/golden_staleness_allowlist.txt`.

**Decision:** no blocking tool gap; Sprint 35 adds only P7 test fixtures, each landing-gated. The genuine-floor recompute maintains **anchor 75** unless a track lands a genuine cold-emit change that cold-matches (a warm-start-only fix yields 0 floor by definition — the S34 P4 precedent).

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
✅ **Status:** VERIFIED — **with the scope corrected (larger than a row fill)**
**Verified by:** Task 3
**Date:** 2026-07-23

**Findings:**
- `SUMMARY.md` has 19 numbered rows. Rows 33 and 34 are correctly filled (the S33 and S34 closes). **But rows 35 and 36 still carry the *pre-insertion* themes**, and rows 37/38 do not exist:
  - **row 35** currently reads "Quality, performance & PATH-feedback integration (incl. rocket PATH author consultation) — `(planned)`". Post-insertion that theme is **Sprint 37**; row 35 must be reconciled to the **S34-carryforward** theme (mine dual / sarf symbolic / fawley diagonal / **ganges multi-root** / camcge Epic-5 / rocket → S36).
  - **row 36** currently reads "v2.0.0 release & Epic 5 planning" — post-insertion that is **row 38**; row 36 must become **PATH Author Consultation & Solution Forcing**.
  - **rows 37 and 38 must be appended** (Quality/Performance/PATH-feedback; v2.0.0 + Epic 5).
- So the P7 work is a **reconcile-and-append across rows 35→38**, not the single row fill the task brief implies — mirroring the reconcile-and-append the S33 and S34 closes each performed (`SPRINT_34/DAY12_P7_INFRA.md` §35 records the same pattern one sprint earlier).
- Cell format is established by rows 28–34: Theme / Headline KPIs at close / Firm landing(s) / REPLAN'd → carryforward.

**Evidence:** `docs/planning/EPIC_4/SPRINT_35/TOOLING_AND_BACKLOG_ANALYSIS.md` §5; `docs/planning/EPIC_4/SUMMARY.md` rows 33–36; `docs/planning/EPIC_4/PROJECT_PLAN.md` §§"Sprint 35"–"Sprint 38" headers.

**Decision:** a Day-12/13 close continuation with three steps (reconcile row 35 + fill its cells; reconcile row 36; append rows 37/38). No technical impact, but left undone the Epic summary contradicts `PROJECT_PLAN.md` for three consecutive sprints.

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
