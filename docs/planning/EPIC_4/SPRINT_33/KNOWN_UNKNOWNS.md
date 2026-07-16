# Sprint 33 Known Unknowns

**Created:** 2026-07-15
**Status:** Active — Pre-Sprint 33
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 33 — the Sprint 32 carryforward sprint landing the mine head-offset bound-active cross-term architecture (#1443), the sarf symbolic parametric `stat_task` emit subsystem (#1385), the fawley #1111/#1112 second-index generalization, the camcge dual-consistent Walras numéraire (#1330 → Epic 5), and the rocket/hhfair/CGE Case-c PATH forcing (#1462/#1236)

---

## Overview

This document identifies every assumption and unknown for Sprint 33's carryforwards **before** implementation begins, continuing the methodology that has prevented late-stage surprises since Sprint 4. Sprint 33 is **specification-bound, not diagnosis-bound**: every carryforward inherits a Sprint-32 *control-confirmed* root cause. The role of this list is therefore not to re-diagnose but to keep each control-confirmed diagnosis — including its *sign* and *sufficiency* — an explicit, verifiable Day-0-re-confirm hypothesis (the standing PR24/PR27 lesson).

**Sprint 33 Scope** (see `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33 (Weeks 31–32)", Priorities 1–7):
1. **P1 — mine #1443:** head-offset bound-active cross-term architecture (the deepest from-scratch AD/emit track; +1 Solve lever)
2. **P2 — sarf #1385:** symbolic parametric `stat_task` emit subsystem (369K-column elimination; +1 Translate lever)
3. **P3 — fawley #1111/#1112:** second-index cross-term generalization (+1 Solve / +1 genuine-floor lever)
4. **P4 — camcge #1330:** dual-consistent Walras numéraire (Epic-5-domain CGE work)
5. **P5 — rocket #1462 + hhfair/CGE #1236:** PATH-consultation submission + Case-c forcing
6. **P6 — failure-cohort re-triage:** agreste / cesam / lnts + adjacent backlog
7. **P7 — infrastructure:** property fixtures + genuine-floor tracking + Epic-4-SUMMARY continuation

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 33" (Deliverables / Acceptance Criteria / Estimated Effort / Risk Level); the per-track banked write-ups under `docs/planning/EPIC_4/SPRINT_32/` (`MINE_5TH_COUPLING_REPLAN.md`, `SARF_TRANSLATE_REPLAN.md`, `P6_BACKLOG_RETRIAGE.md`, `CAMCGE_WALRAS_REPLAN.md`, `ROCKET_PATH_CONSULTATION_INPUT.md`); and `docs/planning/EPIC_4/SPRINT_33/PREP_PLAN.md`. (No `PRELIMINARY_PLAN.md` exists for Sprint 33; the PROJECT_PLAN.md Sprint 33 section is the authoritative scope.)

**Lessons from Previous Sprints:** The Known Unknowns process has run every sprint since Sprint 4 (Sprint 4: 23 unknowns / Sprint 5: 22 / Sprint 32: the five carryforward tracks). Two Sprint-32 lessons dominate this list:
- **A banked "design" is still a hypothesis — including its sign and sufficiency.** Sprint 32 REPLAN'd all five deep tracks after a `/tmp` control refuted the original premise, and corrected two materially-wrong designs (camcge's `nu_mps_fx.l = -mps.m` → `= mps.m`; mine's `N`-derivation, proven insufficient at 6 bound-active rows). Unknowns 1.1/1.2 (mine sufficiency), 2.3 (sarf completeness), 3.1 (fawley generalization) encode this.
- **When every KPI mover is REPLAN-prone, a flat-KPI outcome is the modal result.** The value is the de-risking. Unknowns 1.5, 2.2, 3.2, 4.3 track the REPLAN-probability of each mover.

**Deferred-unknown lineage (from Sprint 32):** Sprint 33's Categories 1–5 are the direct continuation of the Sprint-32 REPLAN'd tracks (`SPRINT_32/SPRINT_RETROSPECTIVE.md` §4). The Sprint-32 Known Unknowns for these tracks were resolved as *control-confirmed diagnoses with un-built fixes*; Sprint 33 carries forward the *implementation-shape* unknowns (the cross-term re-derivation, the O(active) emit subsystem, the second-index gate generalization), not the diagnosis.

---

## How to Use This Document

### Before Sprint 33 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (via prep Tasks 2–10; see the Task-to-Unknown mapping appendix)
2. Run the `/tmp` control experiment for each track (the PR24/PR27 gate) BEFORE any `src/` change
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 33
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

**Total Unknowns:** 27
**By Priority:**
- Critical: 7 (26% — the from-scratch AD/emit tracks whose sufficiency gates the +Solve/+Translate movers)
- High: 11 (41% — upfront design + no-regression + detector-scope questions)
- Medium: 7 (26% — sizing, disposition, byte-stability, and infrastructure scope)
- Low: 2 (7% — nice-to-know, low impact)

**By Category:**
- Category 1 (mine head-offset cross-term): 5 unknowns
- Category 2 (sarf symbolic emit subsystem): 5 unknowns
- Category 3 (fawley second-index generalization): 4 unknowns
- Category 4 (camcge Walras numéraire): 4 unknowns
- Category 5 (rocket / Case-c forcing): 3 unknowns
- Category 6 (failure-cohort re-triage): 3 unknowns
- Category 7 (infrastructure): 3 unknowns

**Estimated Research Time:** ~34 hours (within the 28–36 hour target; spread across prep Tasks 2–10)

---

## Table of Contents

1. [Category 1: mine #1443 — Head-Offset Bound-Active Cross-Term Architecture](#category-1-mine-1443--head-offset-bound-active-cross-term-architecture)
2. [Category 2: sarf #1385 — Symbolic Parametric stat_task Emit Subsystem](#category-2-sarf-1385--symbolic-parametric-stat_task-emit-subsystem)
3. [Category 3: fawley #1111/#1112 — Second-Index Cross-Term Generalization](#category-3-fawley-11111112--second-index-cross-term-generalization)
4. [Category 4: camcge #1330 — Dual-Consistent Walras Numéraire](#category-4-camcge-1330--dual-consistent-walras-numéraire)
5. [Category 5: rocket #1462 + hhfair/CGE #1236 — PATH-Consultation Submission & Case-c Forcing](#category-5-rocket-1462--hhfaircge-1236--path-consultation-submission--case-c-forcing)
6. [Category 6: Failure-Cohort Re-Triage + Adjacent Backlog](#category-6-failure-cohort-re-triage--adjacent-backlog)
7. [Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking + Checkpoint](#category-7-infrastructure--property-fixtures--genuine-floor-tracking--checkpoint)

---

# Category 1: mine #1443 — Head-Offset Bound-Active Cross-Term Architecture

## Unknown 1.1: Is the wrong-sign `N` fully explained by the head-offset `stat_x` cross-term (vs a deeper coupling)?

### Priority
**Critical** — Gates the entire P1 fix; if a deeper coupling is involved, re-deriving one cross-term is insufficient (the Sprint-32 REPLAN failure mode)

### Assumption
The wrong-sign residual `N` at the 6 bound-active rows (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`) is produced entirely by the emitted head-offset cross-term `sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)`, so re-deriving that one cross-term closes it.

### Research Questions
1. Does `N = 0` hold at every interior row and fail *only* at the 6 bound-active rows?
2. Is the residual sign at each of the 6 rows exactly the *opposite* bound's sign (as the Sprint-32 Day-1 control found)?
3. Does any *other* stationarity term (a bound multiplier `piL_x`/`piU_x`, or a second cross-term) contribute at bound-active rows?
4. Is a deeper (5th) coupling involved — i.e., does the head-offset cross-term interact with a second head-offset equation?
5. Does the residual depend on which bound (lo vs up) is active at each row?

### How to Verify
Re-run the Sprint-32 `/tmp` mine control (assert `modelstat`; the `x.up=inf` experiment is BANNED). Inspect the per-row residual: confirm `N=0` interior, wrong-sign at the 6 bound-active rows. Hand-derive the correct bound-active-row stationarity and compare term-by-term against the emitted cross-term to isolate the offending term(s). Cross-check against `SPRINT_32/MINE_5TH_COUPLING_REPLAN.md`.

### Risk if Wrong
- **Deeper coupling:** the cross-term re-derivation is insufficient → mid-sprint REPLAN (repeating the Sprint-32 outcome), no +1 Solve.
- **Multiple contributing terms:** the fix must touch more than the one cross-term, expanding scope beyond the 18–24h budget.

### Estimated Research Time
2 hours (re-run the control, per-row residual inspection, hand-derivation cross-check)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Does the re-derived cross-term vanish at all 6 bound-active rows without perturbing interior rows?

### Priority
**Critical** — The correctness criterion for the P1 fix and the primary REPLAN-probability driver

### Assumption
A sign/guard correction on the shifted-label term (`lam_pr(k,l,i−li,j−lj)$c`) makes `N → 0` at all 6 bound-active rows while every interior row stays at 0.

### Research Questions
1. Which term in the cross-term carries the opposite bound's sign at a bound-active row?
2. Does the correction over-correct any interior row (introduce a new nonzero residual)?
3. Does the fix depend on the `head_domain_offsets` shifted-label pairing `(k,l+1,i,j) ↔ (k,l,i,j)` being present?
4. Does the correction generalize beyond the 6 specific rows to any bound-active row of the same shape?
5. Is the correction a sign flip, a `$`-guard addition, or a structural re-derivation?

### How to Verify
Prototype the corrected cross-term in a `/tmp` control (BEFORE any `src/` change, PR24/PR27). Assert the warm residual → 0 at all 6 bound-active rows AND unchanged (0) at interior rows; then presolve to MS-1 at the NLP optimum 17500 (assert `modelstat`).

### Risk if Wrong
- **Interior perturbation:** a naive sign flip fixes the 6 rows but breaks interior rows → net regression.
- **Row-specific correction:** if the fix is specific to the 6 rows (not the shape), it is not a general emit fix and cannot ship.

### Estimated Research Time
2 hours (prototype the corrected cross-term, verify at all rows, presolve)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: Does the S31 IR foundation (`EquationDef.head_domain_offsets`) carry the shifted-label pairing the re-derivation needs?

### Priority
**High** — If the IR pairing is missing/incomplete, the fix needs new IR plumbing (larger scope)

### Assumption
The landed `EquationDef.head_domain_offsets` (per-position `IndexOffset|None` tuple, with `has_head_domain_offset` derived in `__post_init__`) provides the `(k,l+1,i,j) ↔ (k,l,i,j)` base/shifted pairing without new IR plumbing.

### Research Questions
1. Is the shifted head label stored correctly for mine's `stat_x` equation in the IR?
2. Does the base/shifted pairing survive from the IR through to the stationarity emit in `src/kkt/stationarity.py`?
3. Is any offset position missing or mis-aligned relative to `declaration_domain`?
4. Does the pairing carry the `$c` condition needed at bound-active rows?

### How to Verify
Inspect the parsed `ModelIR` for mine (`head_domain_offsets`, `has_head_domain_offset`); trace the pairing through the stationarity emit path; confirm the shifted-label term is available where the cross-term is built.

### Risk if Wrong
- **Missing IR plumbing:** the fix expands to include IR changes (as Sprint 31 discovered for the head-offset foundation), pushing scope beyond P1's budget.

### Estimated Research Time
1.5 hours (IR inspection + emit-path trace)

### Owner
Development team (IR/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Is the `x.up=inf` measurement BANNED and is `modelstat` asserted before reading any objective?

### Priority
**High** — A repeat of the Sprint-31 measurement error would produce a misleading "MS-1" and mis-size the track

### Assumption
The banked lesson holds: relaxing `x.up=inf` produces unmatched-variable errors and a misleading "MS-1 17500" (the embedded LP, not the MCP); every mine measurement must assert `modelstat` before reading an objective.

### Research Questions
1. Does every mine control/measurement script assert `modelstat` before reading the objective?
2. Is the `x.up=inf` experiment explicitly excluded from all P1 controls?
3. Could any measurement read the embedded LP optimum instead of the MCP status?

### How to Verify
Audit the P1 `/tmp` control scripts for a `modelstat` assertion; grep for any `x.up` relaxation; confirm the objective is read only after an MS confirmation.

### Risk if Wrong
- **Measurement error:** a false "MS-1" leads to shipping a broken emit or mis-sizing the track (the Sprint-31 Day-2 error).

### Estimated Research Time
0.5 hours (script audit)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: Is the mine track sizing (18–24h) realistic given the from-scratch cross-term re-derivation?

### Priority
**Medium** — Affects the schedule front-load and the Day-5 checkpoint REPLAN decision

### Assumption
18–24h covers the hand-derivation + the `stat_x` cross-term emit change + the `/tmp` control + the presolve verification, with the REPLAN surfacing (if any) by the Day-5 checkpoint.

### Research Questions
1. How deep is the re-derivation — a bounded sign/guard change, or an AD-core change?
2. Does the fix touch only `src/kkt/stationarity.py`, or also the AD layer?
3. Does the schedule front-load surface a REPLAN by Day 5 (as Sprint 32's did for mine Day 1)?

### How to Verify
The Task-3 design doc (`MINE_CROSSTERM_DESIGN.md`) sizing + the REPLAN assessment (Task 9); confirm the fix-surface is in `stationarity.py` (where most emit bugs live), not the AD layer.

### Risk if Wrong
- **Under-sizing:** the track overruns and squeezes P2/P3; freed-budget reallocation is delayed.

### Estimated Research Time
1 hour (design-doc sizing review)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: sarf #1385 — Symbolic Parametric stat_task Emit Subsystem

## Unknown 2.1: Does eliminating the 369K-column materialization require changing all three enumeration sites atomically?

### Priority
**Critical** — A partial fix re-triggers the >120s timeout (the Sprint-32 "necessary but insufficient" finding)

### Assumption
The 369,024 `task(g,t,mn,mn)` columns enumerate at three sites — the constraint Jacobian (via the scalar `acost3`), the variable enumeration, and the variable stationarity — so a fix touching only `compute_constraint_jacobian` is insufficient; all three must land atomically.

### Research Questions
1. Which sites materialize the 369K columns (confirm the constraint Jacobian via `acost3`, the variable enumeration, and the variable stationarity)?
2. Does fixing only `compute_constraint_jacobian` still time out (the Sprint-32 Day-6 result)?
3. Do the variable-enumeration and variable-stationarity paths also need the `$taskposs`-active subset?
4. Is there any fourth enumeration site not yet profiled?

### How to Verify
Re-profile the timeout (Day-0 re-confirm); instrument each candidate site to confirm the 369K materialization; cross-check against `SPRINT_32/SARF_TRANSLATE_REPLAN.md` and `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md`.

### Risk if Wrong
- **Missed site:** the parametric emit re-triggers the timeout mid-sprint → P2 REPLAN, no +1 Translate.

### Estimated Research Time
2 hours (re-profile + site instrumentation)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Will the parametric symbolic emit stay O(active = 398) and not re-trigger the timeout?

### Priority
**Critical** — The tractability criterion for sarf recovering to translate (+1 Translate)

### Assumption
Emitting one guarded `stat_task(g,t,m,n)$taskposs(g,t)` over the 398 active instances (not 369K), with cross-terms differentiated once parametrically, keeps translate within budget (srpchase's 1-D analogue translates in 6.56s).

### Research Questions
1. Is the active subset (`$taskposs(g,t)`) exactly 398 instances?
2. Do the `J_gᵀ·lam` cross-terms differentiate *once parametrically*, not per-instance?
3. Does any residual per-instance path remain after the three-site fix?
4. Is the translate time within the budget vs srpchase's 6.56s reference?

### How to Verify
After the design lands in a `/tmp` prototype, time `sarf_mcp.gms` against the translate budget; compare against srpchase's 1-D analogue; confirm the active-instance count is 398.

### Risk if Wrong
- **Still O(369K):** if a per-instance path remains, translate still times out → P2 REPLAN.

### Estimated Research Time
2 hours (prototype timing + active-subset count)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Is the banked 7-term `stat_task` derivation complete and free of set-name-literal multiplier indices?

### Priority
**Critical** — An incomplete derivation ships a wrong `stat_task`; set-name literals break the parametric emit

### Assumption
The 7-term `stat_task` derivation in `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` captures every cross-term, and the emit uses no set-name-literal multiplier indices.

### Research Questions
1. Are all 7 terms of the derivation present and correct?
2. Is any `J_gᵀ·lam` cross-term missing (e.g., from `acost3` or a coupled constraint)?
3. Does a grep-scan of the emitted golden find any set-name-literal multiplier index?
4. Does the derivation match a hand-derivation of `stat_task` from the sarf source?

### How to Verify
Hand-derive `stat_task` from the sarf source and compare against the banked 7-term derivation; grep-scan the emitted golden for set-name literals in multiplier indices.

### Risk if Wrong
- **Missing term:** the emitted `stat_task` is wrong → sarf translates but produces a broken MCP.
- **Set-name literals:** the emit is not parametric → the timeout re-triggers.

### Estimated Research Time
1.5 hours (hand-derivation + grep-scan)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Does `task.fx$(not active) = 0` correctly handle the inactive `task` columns?

### Priority
**High** — Incorrect fixing breaks complementarity or leaves inactive columns in the MCP

### Assumption
Fixing the inactive `task` columns to 0 via `task.fx$(not active)=0` removes them from the MCP without breaking complementarity, mirroring the `$taskposs(g,t)` guard.

### Research Questions
1. Does the `$(not active)` guard exactly complement `$taskposs(g,t)`?
2. Does PATH accept the fixing without a pairing error against `stat_task`?
3. Does fixing interact with the presolve warm-start?

### How to Verify
Emit the `task.fx` in a `/tmp` prototype; solve with PATH; confirm no unmatched-variable / complementarity-pairing error and that inactive columns are fixed at 0.

### Risk if Wrong
- **Pairing error:** the MCP has unmatched variables → translate/solve failure.

### Estimated Research Time
1 hour (emit + PATH solve)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Is the new sarf golden byte-stable and deterministic under ≥ 3 `PYTHONHASHSEED` values?

### Priority
**Medium** — A non-deterministic golden fails the determinism gate (PR12) and the golden-staleness check (PR26)

### Assumption
The re-emit produces a byte-identical golden under ≥ 3 `PYTHONHASHSEED` values {0,1,42}, with the active-subset enumeration deterministic.

### Research Questions
1. Is there any set-ordering nondeterminism in the active-subset enumeration?
2. Does the parametric cross-term emit order deterministically?
3. Does the golden match across the three seeds (md5)?

### How to Verify
Emit the sarf golden under `PYTHONHASHSEED` {0,1,42}; compare with `md5 -q` (macOS) / `md5sum` (Linux); confirm byte-identical.

### Risk if Wrong
- **Nondeterminism:** the determinism gate fails → the emit cannot ship until the ordering is fixed.

### Estimated Research Time
0.5 hours (emit ×3 seeds + md5)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: fawley #1111/#1112 — Second-Index Cross-Term Generalization

## Unknown 3.1: Does the second-index gate generalize cleanly from the variable's-first-index (mbal) to the variable's-second-index-summed (qsb/pbal) shape?

### Priority
**Critical** — The core correctness question for the P3 fix; a leaky generalization is the confirmed "#1111/#1112 gate leaks" risk

### Assumption
Extending the landed `_var_at_two_indices_complement` / `_build_complement_index_sum` gate from the variable's-first-index = equation-index shape (mbal) to the variable's-second-index-summed shape covers qsb/pbal, so `max|stat_bq| → 0`.

### Research Questions
1. Is the qsb/pbal shape truly the *variable's-second-index-summed* transpose (vs a distinct shape)?
2. Does the gate's detection logic generalize to the second-index case without a new AST shape?
3. Does the `$(sameas(cfq__,cf))` restriction apply identically to qsb/pbal as to mbal?
4. Does the generalized gate correctly handle both qsb and pbal (or do they differ)?

### How to Verify
Hand-derive `stat_bq` for qsb/pbal from the fawley source; prototype the generalized gate in a `/tmp` control; confirm `max|stat_bq| → 0` (beyond the 96% the sameas patch reached). Cross-check `SPRINT_32/P6_BACKLOG_RETRIAGE.md` §3.

### Risk if Wrong
- **Gate leaks:** the generalization covers only part of the qsb/pbal shape → residual remains, fawley still diverges (P3 REPLAN).

### Estimated Research Time
2 hours (hand-derivation + `/tmp` gate prototype)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Does closing the residual 18.47 also fix the MS-5 LP-convergence?

### Priority
**High** — Determines whether the emit fix alone reaches MS-1 at the LP optimum 2899.25

### Assumption
The residual `max|stat_bq|` 18.47 (after the 96% sameas patch) is the last emit defect; closing it reaches MS-1 at the LP optimum 2899.25.

### Research Questions
1. Is the residual 18.47 a *second* over-sum (a further gate-leak) or a *distinct* qsb/pbal term the sameas restriction doesn't reach?
2. Is the MS-5 LP-convergence gated on closing the residual, or is there a non-emit cause?
3. Does the `/tmp` control reach MS-1 at 2899.25 once the residual is 0?

### How to Verify
Localize the residual-18.47 term; prototype the full fix in a `/tmp` control; assert `max|stat_bq| → 0` AND MS-1 at 2899.25 (assert `modelstat`).

### Risk if Wrong
- **Non-emit divergence:** if the LP-convergence has a separate cause, the emit fix reaches Case-a but the model still diverges → conditional +Solve only.

### Estimated Research Time
1.5 hours (residual localization + `/tmp` presolve)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Does the extended gate regress polygon/ps2/mbal (already covered by the landed core)?

### Priority
**High** — A regression on the already-covered models would be a net-negative ship

### Assumption
The second-index generalization is additive — it fires on qsb/pbal without changing the emit for polygon/ps2/mbal (which the landed core already covers).

### Research Questions
1. Does the broadened detection accidentally fire on polygon/ps2/mbal?
2. Does `--resolve-changed --since-commit 4cbf8bff` return GO (no bucket moves for the covered models)?
3. Is the generalization gated so it fires only on the second-index-summed shape?

### How to Verify
Run `--resolve-changed --since-commit 4cbf8bff` after the `/tmp` prototype; confirm GO (no polygon/ps2/mbal regression); inspect the emitted diff for those models (should be unchanged).

### Risk if Wrong
- **Regression:** the generalization breaks a covered model → the fix cannot ship as-is.

### Estimated Research Time
1 hour (`--resolve-changed` GO + emit-diff inspection)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Is the fawley sizing (12–18h) realistic, and does the fix cold-match (genuine floor +1)?

### Priority
**High** — Determines whether P3 delivers a *genuine* floor gain (not methodology) and fits the budget

### Assumption
12–18h covers the residual diagnosis + the gate generalization + the control + the presolve; and fawley *cold-matches* after the fix (a genuine floor +1, not a warm-start-only methodology match).

### Research Questions
1. Does the cold emit change (a genuine fix) vs matching only via presolve warm-start (methodology)?
2. Does fawley cold-match at the LP optimum after the fix?
3. Is the 12–18h budget realistic for the generalization + no-regression verification?

### How to Verify
After the fix, diff the cold emit vs the Day-0 emit (must change → genuine); run the PR25 genuine-vs-methodology check; confirm the cold match.

### Risk if Wrong
- **Methodology-only:** fawley matches only via presolve → no genuine floor gain (the S30/S31 conditionality lesson).

### Estimated Research Time
1 hour (cold-emit diff + PR25 genuine check)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: camcge #1330 — Dual-Consistent Walras Numéraire

## Unknown 4.1: Does the per-model-numéraire + dual-consistent Walras redefinition reach MS-1 at omega 191.7346 in a `/tmp` prototype?

### Priority
**Critical** — The correctness criterion for camcge; step 2 currently reaches omega 191.7346 but MS-4

### Assumption
Keeping every market-clearing row and redefining the redundant market's dual via Walras' law makes the reduced system full-rank while keeping the dual available, reaching MS-1 at omega 191.7346.

### Research Questions
1. Does the redefinition remove the rank-deficiency on the accounting identities (`gdp`/`depreq`/`hhsaveq`/`gruse`)?
2. Does the redundant market's dual stay available (not dropped, unlike the primal-correct-but-dual-breaking drop-row)?
3. Does the `/tmp` prototype reach MS-1 (not MS-4) at omega 191.7346?
4. How is the numéraire declared per-model (vs a global assumption)?

### How to Verify
Prototype the per-model-numéraire + Walras redefinition in a `/tmp` model; assert `modelstat` = 1 at omega 191.7346; cross-check `SPRINT_32/CAMCGE_WALRAS_REPLAN.md` and `EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Risk if Wrong
- **Still MS-4:** the redefinition doesn't resolve the rank-deficiency → camcge stays `model_infeasible`, Epic-5-deferred (the per-model-numéraire fallback becomes the documented finding).

### Estimated Research Time
2 hours (`/tmp` prototype + MS assertion)

### Owner
Development team (CGE/Epic-5 specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Does the S1∧S2∧S3 degeneracy detector flag only camcge (not irscge/lrgcge/moncge/stdcge)?

### Priority
**High** — A false positive on the sibling CGE models would mis-apply the Walras redefinition and break them

### Assumption
The three detector conditions (S1∧S2∧S3) isolate camcge; none of irscge/lrgcge/moncge/stdcge satisfies all three, so the redefinition applies only to camcge.

### Research Questions
1. What are the three conditions S1/S2/S3 (from `CGE_DEGENERACY_SCOPING.md`)?
2. Do any of the four sibling CGE models satisfy all three (a false positive)?
3. Is the detector scope narrow enough to be safe as a general `src/` gate?

### How to Verify
Run the S1∧S2∧S3 detector on all five CGE models (camcge + irscge/lrgcge/moncge/stdcge); confirm it flags only camcge.

### Risk if Wrong
- **False positive:** the redefinition fires on a sibling CGE model that doesn't need it → breaks a currently-working model.

### Estimated Research Time
1.5 hours (detector run on the five models)

### Owner
Development team (CGE/Epic-5 specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Is camcge in-scope for Sprint 33 or Epic-5-deferred?

### Priority
**Medium** — Determines whether P4 is a Sprint-33 deliverable or a documented Epic-5 finding

### Assumption
If the `/tmp` prototype lands MS-1, camcge is in-scope for Sprint 33; otherwise the per-model-numéraire fallback is the documented Epic-5 finding.

### Research Questions
1. Does the prototype land MS-1 (Unknown 4.1)?
2. Is the redefinition general or camcge-specific (affecting whether it belongs in Epic 5)?
3. What is the clean hand-off if deferred?

### How to Verify
The Task-6 disposition (`CAMCGE_WALRAS_DESIGN.md`) + the Unknown-4.1 prototype result.

### Risk if Wrong
- **Scope thrash:** an ambiguous disposition churns budget between Sprint 33 and Epic 5.

### Estimated Research Time
1 hour (disposition review)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: Does the scalar-`fx` step-1 fix (Sprint 32) remain correct under the numéraire change?

### Priority
**Low** — The step-1 fix landed and is stable; the numéraire change is unlikely to perturb it, but worth confirming

### Assumption
The landed `nu_mps_fx` transfer (`= mps.m` direct, the control-corrected sign) stays correct after the numéraire redefinition.

### Research Questions
1. Does the numéraire change perturb `stat_mps` (which step 1 moved to Case-a)?
2. Is there any sign interaction between the `nu_mps_fx` transfer and the redefined dual?

### How to Verify
Re-run the Sprint-32 step-1 `stat_mps` control after applying the numéraire redefinition; confirm `stat_mps` stays Case-a.

### Risk if Wrong
- **Regression:** the numéraire change re-breaks `stat_mps` → step 1 must be re-derived alongside step 2.

### Estimated Research Time
0.5 hours (re-run the step-1 control)

### Owner
Development team (CGE/Epic-5 specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: rocket #1462 + hhfair/CGE #1236 — PATH-Consultation Submission & Case-c Forcing

## Unknown 5.1: Is the packaged rocket PATH-consultation input complete for Sprint-34 submission?

### Priority
**High** — The clean hand-off gates the Sprint-34 PATH-author consultation

### Assumption
`ROCKET_PATH_CONSULTATION_INPUT.md` (Status: FINALIZED) contains the concrete question set + the ruled-out-lever survey + the `--force` scaffold outputs, ready for submission to the Sprint-34 consultation.

### Research Questions
1. What is the Sprint-34 submission mechanism (what is handed off, to whom)?
2. Is anything missing from the finalized package (a question, a lever, a data artifact)?
3. Does the Case-c boundary (residual clean at the NLP point) still hold on re-confirm?

### How to Verify
Review `ROCKET_PATH_CONSULTATION_INPUT.md`; define the hand-off mechanism in the Task-7 plan; re-confirm the Case-c boundary via the harness.

### Risk if Wrong
- **Incomplete package:** the Sprint-34 consultation stalls waiting for missing input.

### Estimated Research Time
1 hour (package review + hand-off definition)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does any `--force` lever (homotopy/multistart/optfile) cross for rocket or the hhfair/CGE family?

### Priority
**Medium** — Any recovery is a *conditional* (not firm) +Solve; the survey feeds the consultation regardless

### Assumption
Some `--force` lever may recover a +Solve on rocket or a hhfair/CGE Case-c model, but the recovery is conditional (non-convex, forcing-dependent), not a firm KPI gain.

### Research Questions
1. Which levers (homotopy / multistart / optfile) are worth surveying per model?
2. What does "a lever crosses" mean operationally (a recovered +Solve at MS-1)?
3. Does any model converge under forcing, or is the survey banked for the consultation?

### How to Verify
Run the `--force` survey on rocket + hhfair/irscge/lrgcge/moncge; record which levers cross (if any) vs banked for the PATH consultation.

### Risk if Wrong
- **Over-promising:** counting a conditional forcing recovery as a firm KPI gain (the methodology-vs-genuine lesson).

### Estimated Research Time
1.5 hours (`--force` survey across the family)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Is the sign flip still BANNED for the Case-c family, and is each residual clean at the NLP point?

### Priority
**Low** — Re-affirms a settled decision (the sign flip is control-refuted); low risk but worth a Day-0 re-confirm

### Assumption
The Case-c family (hhfair/irscge/lrgcge/moncge, auto-classified `case_c_objdef`) has clean residuals at the NLP point (forcing problems, not emit bugs), and the sign flip stays BANNED.

### Research Questions
1. Is each Case-c model's residual clean at the NLP point (Case-c, not a latent emit bug)?
2. Is the sign flip re-litigated anywhere in the P5 plan (it must not be)?

### How to Verify
Re-run the harness on the Case-c family; confirm the `case_c_objdef` classification and a clean NLP-point residual; confirm the sign flip is not re-introduced.

### Risk if Wrong
- **Mis-classification:** a latent emit bug hidden behind the Case-c label goes unfixed (unlikely — control-refuted in S32).

### Estimated Research Time
0.5 hours (harness re-run)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Failure-Cohort Re-Triage + Adjacent Backlog

## Unknown 6.1: Is agreste genuinely CASE_B or a double-`solve` scope artifact?

### Priority
**High** — A double-`solve` artifact is not a fixable emit bug; treating it as CASE_B wastes budget

### Assumption
agreste's Sprint-32 CASE_B (`stat_sales` rel 2.0) may be a scenario-driver double-`solve` artifact rather than a genuine emit bug; the scope must be verified before any fix.

### Research Questions
1. Is agreste a multi-`solve` scenario driver (like decomp/danwolfe)?
2. Does the harness CASE_B verdict hold under correct single-solve scope?
3. If genuine, is it fixable within Sprint 33, or banked?

### How to Verify
Inspect the agreste source for multiple `solve` statements; re-run the harness under the correct scope; gate any fix on a `--resolve-changed` GO.

### Risk if Wrong
- **Wasted budget:** chasing a scope artifact as an emit bug (the multi-solve-gate lesson).

### Estimated Research Time
1.5 hours (source scope inspection + harness re-run)

### Owner
Development team (diagnostics)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Are cesam and lnts confirmed Case-c (non-convex, forcing-only)?

### Priority
**High** — Confirms whether they belong in the forcing/PATH cohort (not the emit-fix cohort)

### Assumption
cesam (bilinear SAM) and lnts (bilinear-`step` optimal control) are genuine non-convex Case-c, not latent emit bugs.

### Research Questions
1. Does each classify as Case-c under the harness (clean NLP-point residual)?
2. Is any emit defect masquerading as non-convexity?
3. Do they join the rocket/hhfair Case-c forcing cohort?

### How to Verify
Run the KKT-residual harness + a convexity check on cesam and lnts; confirm Case-c; cross-check `docs/research/convexity_detection.md`.

### Risk if Wrong
- **Missed emit bug:** a real defect labeled Case-c goes unfixed.

### Estimated Research Time
1 hour (harness + convexity check)

### Owner
Development team (diagnostics)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Do the P1/P2/P3 fixes unlock adjacent backlog (the srpchase/sarf symbolic-emit family)?

### Priority
**Medium** — Any unlocked follow-on is bonus scope for the sprint's back half

### Assumption
The sarf symbolic-emit subsystem (P2) generalizes to srpchase-family follow-ons sharing the same active-subset shape.

### Research Questions
1. Which models share the sarf `$taskposs`-active symbolic-emit shape?
2. Does the P2 subsystem apply to them without further work?
3. Does each candidate return a `--resolve-changed` GO?

### How to Verify
After P2 lands, scan the failure cohort for the same shape; run `--resolve-changed` per candidate.

### Risk if Wrong
- **No unlock:** the follow-ons need separate work (not a Sprint-33 gain) — acceptable, just re-scoped.

### Estimated Research Time
1 hour (shape scan + `--resolve-changed`)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking + Checkpoint

## Unknown 7.1: Do the shape12/shape13/fawley property fixtures fail-before/pass-after only once P1/P2/P3 land?

### Priority
**High** — The property fixtures are the permanent guard on the new emit paths; they must fail on the old emit and pass on the new

### Assumption
The AD cross-term property fixtures — shape12 (head-offset bound-active), shape13 (sarf symbolic `stat_task`), and a fawley second-index fixture — can be authored to fail on the Day-0 emit and pass only after P1/P2/P3 land, and are property-based (shape-level), not model-specific.

### Research Questions
1. Can each fixture be authored *before* the fix so it fails-before (guarding against regression)?
2. Does each pass after the corresponding fix lands?
3. Are the fixtures property-based (the cross-term shape), not tied to the specific model?
4. Do they extend `test_ad_crossterm_shapes.py` cleanly?

### How to Verify
Author the fixtures against the Day-0 emit (confirm fail-before); after each fix lands, confirm pass-after; confirm they extend the existing property catalog.

### Risk if Wrong
- **No fail-before:** a fixture that passes on the old emit isn't guarding anything (the Sprint-28 property-catalog lesson).

### Estimated Research Time
1.5 hours (fixture authoring + fail-before check)

### Owner
Development team (test infrastructure)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is the genuine-floor anchor correctly 74, and which levers move it?

### Priority
**Medium** — The genuine-floor ramp (S33 anchor 74, footnote ⁸) is the real progress metric; a wrong anchor mis-measures the sprint

### Assumption
The PR25 genuine-floor anchor is 74 (cold-emit-correct genuine matches, excluding presolve-recovered methodology), and mine [P1] / fawley [P3] cold-matches are the levers that move it to ≥ 75.

### Research Questions
1. Is the anchor correctly 74 at Sprint-33 Day 0?
2. Which models are cold-genuine vs presolve-methodology at the baseline?
3. Do the P1/P3 fixes convert their models to cold-genuine matches (+1 each)?

### How to Verify
Recompute the PR25 genuine-vs-methodology split at Day 0 (Task 2 baseline); confirm the anchor 74; identify the mover levers.

### Risk if Wrong
- **Wrong anchor:** the genuine-floor delta is mis-measured, over/under-crediting the sprint.

### Estimated Research Time
1 hour (PR25 recompute)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.3: What is the Epic-4 `SUMMARY.md` row-33 continuation scope?

### Priority
**Medium** — The Epic-4 summary groundwork (begun Sprint 32 Day 12) needs the Sprint-33 row filled at close

### Assumption
The `SUMMARY.md` skeleton (one row per Sprint 18–36) needs the Sprint-33 row populated with the KPIs + firm landings + REPLAN'd carryforwards at Sprint-33 close.

### Research Questions
1. Which cells does the Sprint-33 row need (Theme / Headline KPIs / Firm landing(s) / REPLAN'd → carryforward)?
2. What is the backfill format (consistent with rows 28–32)?
3. Is the continuation a Day-12 task (as Sprint 32's was)?

### How to Verify
Review `SUMMARY.md` row 33 (currently "(planned)"); confirm the cell format vs rows 28–32; schedule the continuation in the Task-11 plan.

### Risk if Wrong
- **Inconsistent summary:** a mis-formatted row breaks the Epic-4-close rollup (low impact, easily fixed).

### Estimated Research Time
0.5 hours (SUMMARY.md review)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Confirmed Knowledge (From Sprint 32 and Earlier)

These items were control-confirmed in Sprint 32 and are treated as knowledge (not unknowns) for Sprint 33:

### mine (P1)
- The bound-multiplier `N`-derivation closes `stat_x` *by construction* but is **insufficient** — it yields a wrong-sign residual at 6 bound-active rows (MS-5 @ 22058, not the NLP optimum 17500). The defect is in the emitted head-offset cross-term, not a warm-start value. (`MINE_5TH_COUPLING_REPLAN.md`)

### sarf (P2)
- The 2-D constraint gate (`_is_blowup_2d_condition_equation`, fires sarf-only) is **necessary but insufficient** — the 369K columns enumerate via `acost3` + the variable path, untouched by the constraint gate. (`SARF_TRANSLATE_REPLAN.md`)

### fawley (P3)
- `stat_bq` applies `$(sameas(cfq__,cf))` to the mbal cross-term but **not** the qsb/pbal terms (over-sum); the `/tmp` sameas patch closes `max|stat_bq|` 473 → 18 (96%). (`P6_BACKLOG_RETRIAGE.md` §3)

### camcge (P4)
- Step 1 (scalar-`fx` `nu_mps_fx` transfer, `= mps.m` direct) landed → `stat_mps` Case-a. Step 2's numéraire reaches omega 191.7346 but MS-4 (Walras rank-deficiency on gdp/depreq/hhsaveq/gruse). The drop-row is primal-correct but breaks the MCP dual. (`CAMCGE_WALRAS_REPLAN.md`)

### rocket / Case-c (P5)
- rocket's non-convergence is intrinsic (Case-c); every emittable lever is ruled out; the PATH-consultation input is FINALIZED. hhfair + the CGE cluster are auto-classified `case_c_objdef` (ISSUE_1236 CLOSED); the sign flip is BANNED. (`ROCKET_PATH_CONSULTATION_INPUT.md`, `CASE_C_CLASSIFIER_DESIGN.md`)

### Process
- **Always assert `modelstat` before reading an objective off a solve** (the Sprint-31 `x.up=inf` measurement error). The single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes. Run the `/tmp` control BEFORE any high-blast-radius `src/` change (PR24/PR27).

---

## Template for New Unknowns

When adding unknowns during Sprint 33:

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

**Before Sprint 33 Day 1:**
1. Review all Critical and High priority unknowns (18 total) via prep Tasks 2–10 (see the Task-to-Unknown mapping appendix)
2. Run the `/tmp` control experiment for each track BEFORE any `src/` change (the PR24/PR27 gate)
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED / ❌ WRONG)
4. Adjust the Sprint 33 scope + schedule (Task 11) if any Critical assumption is wrong
5. Share findings with the team during sprint planning

**During Sprint 33:**
1. Reference this document daily
2. Add newly discovered unknowns (use the template)
3. Update verification results as each track is implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Sprint 32 → 33 Day-0 Baseline + Genuine-Floor Re-Baseline | 1.1, 3.1, 7.2 | Re-confirms the Day-0 mine/fawley buckets (contributes to 1.1, 3.1) and the PR25 genuine-floor anchor 74 (7.2) |
| Task 3: mine Head-Offset Bound-Active Cross-Term — Localization + Re-Derivation Design | 1.1, 1.2, 1.3, 1.4, 1.5 | The full Category-1 design: sufficiency (1.1), correctness (1.2), IR pairing (1.3), measurement ban (1.4), sizing (1.5) |
| Task 4: sarf Symbolic Parametric `stat_task` Emit-Subsystem Design | 2.1, 2.2, 2.3, 2.4, 2.5 | The full Category-2 design: three-site elimination (2.1), O(active) budget (2.2), 7-term derivation (2.3), `task.fx` (2.4), determinism (2.5) |
| Task 5: fawley #1111/#1112 Second-Index Cross-Term Generalization Design | 3.1, 3.2, 3.3, 3.4 | The full Category-3 design: gate generalization (3.1), residual/LP-convergence (3.2), no-regression (3.3), sizing/cold-match (3.4) |
| Task 6: camcge Dual-Consistent Walras Numéraire Design + Degeneracy-Detector Scope | 4.1, 4.2, 4.3, 4.4 | The full Category-4 design: MS-1 prototype (4.1), detector scope (4.2), disposition (4.3), step-1 stability (4.4) |
| Task 7: rocket PATH-Consultation Submission Package + hhfair/CGE Case-c Forcing Plan | 5.1, 5.2, 5.3 | The full Category-5 plan: submission completeness (5.1), `--force` survey (5.2), Case-c/sign-flip re-confirm (5.3) |
| Task 8: Refresh + Author Phase 0 Acceptance Gates for the Sprint-33 Tracks | 1.1, 2.1, 3.1, 4.1, 5.1 | The per-track `/tmp` control/gate feasibility for each of P1–P5 (contributes to the correctness unknowns via the Phase-0 gate design) |
| Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment | 1.2, 2.3, 3.3 | The REPLAN-probability unknowns: mine cross-term correctness (1.2), sarf derivation completeness (2.3), fawley no-regression/gate-leak (3.3) |
| Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis | 6.1, 6.2, 6.3, 7.1, 7.3 | The full Category-6 (agreste 6.1, cesam/lnts 6.2, adjacent backlog 6.3) + the Category-7 infrastructure (property fixtures 7.1, SUMMARY continuation 7.3) |

**Note:** Task 11 (Plan Sprint 33 Detailed Schedule) integrates all verified unknowns into the day-by-day schedule (it does not verify unknowns directly). Task 1 (this document) authors the unknowns. Some unknowns are verified by more than one task (e.g., 1.1 by Tasks 2/3/8; 3.1 by Tasks 2/5; 7.2 by Task 2) — the primary owner is the per-track design task (Tasks 3–7); Tasks 2/8/9 *contribute* via the baseline, the Phase-0 gate, and the REPLAN assessment respectively.

---

**Document Status:** 🔵 Active — Pre-Sprint 33
**Last Updated:** 2026-07-15
**Owner:** Sprint 33 Planning Team
**Review Frequency:** Daily during Sprint 33
