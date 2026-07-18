# Sprint 34 Known Unknowns

**Created:** 2026-07-18
**Status:** Active — Pre-Sprint 34
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 34 — the Sprint 33 carryforward sprint landing the mine head-offset dual subsystem (#1443), the sarf symbolic/parametric `stat_task` emit subsystem (#1385), the fawley #1111/#1112 second-index correction + forcing, the NEW max-convention bound-transfer-sign track, the camcge dual-consistent Walras numéraire (#1330 → Epic 5), and the rocket #1462 PATH-consultation submission

---

## Overview

This document identifies every assumption and unknown for Sprint 34's carryforwards **before** implementation begins, continuing the methodology that has prevented late-stage surprises since Sprint 4. Sprint 34 is **specification-bound, not diagnosis-bound**: every carryforward inherits a Sprint-33 *control-confirmed* characterization. The role of this list is therefore not to re-diagnose but to keep each control-confirmed characterization — including its *sufficiency* and its *achievable KPI bucket* — an explicit, verifiable Day-0-re-confirm hypothesis (the standing PR24/PR27 lesson).

**Sprint 34 Scope** (see `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 34 (Weeks 33–34)", Priorities 1–7):
1. **P1 — mine #1443:** head-offset dual subsystem (the deepest from-scratch AD/emit track, H1 refuted; +1 Solve lever)
2. **P2 — sarf #1385:** symbolic/parametric `stat_task` emit subsystem (369K-column elimination; +1 Translate lever)
3. **P3 — fawley #1111/#1112:** second-index correction + forcing (+1 genuine-floor lever; +Solve is H-b → forcing)
4. **P4 — max-convention bound-transfer-sign track (NEW):** the fresh general warm-start-transfer +Solve lever
5. **P5 — camcge #1330 (Epic 5) + rocket #1462:** dual-consistent Walras numéraire + PATH-consultation submission
6. **P6 — banked failure-cohort re-triage:** ganges/gangesx `$141/$145/$149` + agreste scope-verify
7. **P7 — infrastructure:** property fixtures + genuine-floor tracking + Epic-4-SUMMARY continuation

**Reference:** `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 34" (Deliverables / Acceptance Criteria / Estimated Effort / Risk Level); the per-track Sprint-33 control docs under `docs/planning/EPIC_4/SPRINT_33/` (`DAY2_MINE_REPLAN.md`, `MINE_CROSSTERM_DESIGN.md`, `DAY6_SARF_ASSESSMENT.md`, `SARF_EMIT_SUBSYSTEM_DESIGN.md`, `DAY4_FAWLEY_CONTROL.md`, `DAY5_FAWLEY_CLOSE.md`, `FAWLEY_SECOND_INDEX_DESIGN.md`, `CAMCGE_WALRAS_DESIGN.md`, `ROCKET_CASEC_FORCING_PLAN.md`, `SPRINT_34_CARRYFORWARDS.md`); and `docs/planning/EPIC_4/SPRINT_34/PREP_PLAN.md`. (No `PRELIMINARY_PLAN.md` exists for Sprint 34; the PROJECT_PLAN.md Sprint 34 section is the authoritative scope.)

**Lessons from Previous Sprints:** The Known Unknowns process has run every sprint since Sprint 4 (Sprint 4: 23 unknowns / Sprint 5: 22 / Sprint 33: 27). Three Sprint-33 lessons dominate this list:
- **A banked characterization is still a hypothesis — including its sufficiency and its achievable bucket.** Sprint 33 *refuted the banked fix hypothesis on every deep track* before any bad ship: mine's H1 re-keying was proven **value-invariant** by a `/tmp` control; fawley reached **H-b** (the MCP diverges MS-5 even with the warm residual fully closed); sarf was Option-B-deferred as a from-scratch rebuild. Unknowns 1.1/1.2 (mine dual-architecture sufficiency), 3.2 (fawley H-b), 2.1/2.2 (sarf atomicity/timeout) encode this.
- **When every deep KPI mover is REPLAN-prone, a flat-KPI outcome is the modal result — but the designated failure-cohort fallback can still deliver.** Sprint 33's three deep tracks moved no bucket (the honest projection borne out), *but P6 (sample) delivered the +1 Solve / +1 Match / +1 floor*. Unknowns 1.5, 2.2, 3.2, 4.2 track the REPLAN-probability of each mover; Category 6 tracks the failure-cohort fallback.
- **The failure cohort is multi-root — verify per-model, do not assume a shared root.** Sprint 33's `path_syntax_error` cohort was not a single root: sample (`$140`, pruned-var `.l`-init) recovered; ganges/gangesx (`$141/$145/$149`, referenced vars declared) are a *different* root. Unknowns 6.1/6.3 encode this.

**Deferred-unknown lineage (from Sprint 33):** Sprint 34's Categories 1–5 are the direct continuation of the Sprint-33 REPLAN'd/deferred tracks (`SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_34_CARRYFORWARDS.md`). The Sprint-33 Known Unknowns for these tracks were resolved as *control-confirmed characterizations with un-built (and, for P1/P3, harder-than-anticipated) fixes*; Sprint 34 carries forward the *implementation-shape* unknowns (the dual-reconciliation architecture, the symbolic emit mode, the constraint-index-diagonal correction, the NEW sign-robust bound transfer), not the diagnosis. Category 4 is a **newly-surfaced** track (the max-convention bound-transfer-sign gap, discovered Sprint-33 Day 4).

---

## How to Use This Document

### Before Sprint 34 Day 1
1. Research and verify all **Critical** and **High** priority unknowns (via prep Tasks 2–10; see the Task-to-Unknown mapping appendix)
2. Run the `/tmp` control experiment for each track (the PR24/PR27 gate) BEFORE any `src/` change
3. Document findings in the "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 34
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
- Critical: 7 (26% — the from-scratch AD/emit tracks whose sufficiency gates the +Solve/+Translate movers, plus the baseline-anchor correctness)
- High: 11 (41% — upfront design + no-regression + REPLAN-probability + cohort-scope questions)
- Medium: 7 (26% — disposition, byte-stability, fixture, and detector-scope questions)
- Low: 2 (7% — nice-to-know, low impact)

**By Category:**
- Category 1 (mine head-offset dual subsystem): 5 unknowns
- Category 2 (sarf symbolic-emit subsystem): 5 unknowns
- Category 3 (fawley second-index correction + forcing): 4 unknowns
- Category 4 (max-convention bound-transfer-sign track): 4 unknowns
- Category 5 (camcge Walras + rocket PATH submission): 3 unknowns
- Category 6 (banked failure-cohort re-triage): 3 unknowns
- Category 7 (infrastructure): 3 unknowns

**Estimated Research Time:** ~34 hours (within the 28–36 hour target; spread across prep Tasks 2–10)

---

## Table of Contents

1. [Category 1: mine #1443 — Head-Offset Dual Subsystem](#category-1-mine-1443--head-offset-dual-subsystem)
2. [Category 2: sarf #1385 — Symbolic-Emit Subsystem](#category-2-sarf-1385--symbolic-emit-subsystem)
3. [Category 3: fawley #1111/#1112 — Second-Index Correction + Forcing](#category-3-fawley-11111112--second-index-correction--forcing)
4. [Category 4: Max-Convention Bound-Transfer-Sign Track](#category-4-max-convention-bound-transfer-sign-track)
5. [Category 5: camcge Walras (Epic 5) + rocket PATH Submission](#category-5-camcge-walras-epic-5--rocket-path-submission)
6. [Category 6: Banked Failure-Cohort Re-Triage](#category-6-banked-failure-cohort-re-triage)
7. [Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking + Checkpoint](#category-7-infrastructure--property-fixtures--genuine-floor-tracking--checkpoint)

---

# Category 1: mine #1443 — Head-Offset Dual Subsystem

## Unknown 1.1: Is H1 (head-label multiplier re-keying) truly value-invariant, and is the residual a deeper dual-architecture gap?

### Priority
**Critical** — Gates the entire P1 fix; if H1 is *not* value-invariant a keying change might close it, but Sprint-33's control proved it is — so P1 requires a from-scratch dual-reconciliation, not a keying tweak (the twice-refuted premise)

### Assumption
The Sprint-33 Day-2 control result holds: re-keying the `l+1`-shifted head-label transfer (`lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j))`) is **value-invariant** (the shifted transfer already stores the head-label value at the body label → 22→22 nonzero residual rows, `d_N = d_Nh1` row-for-row), so the residual is a deeper head-offset dual-architecture mismatch (the head-placed precedence dual not mapping into `stat_x` at the `c`-boundary), not a keying error.

### Research Questions
1. Does the Day-2 `/tmp` control reproduce the value-invariance (22→22 rows, `d_N = d_Nh1`) on the live tree?
2. At the max row `stat_x(3,1,1)`, is `x` bound-active with NLP reduced cost `x.m = 0`, and is the cross-term structurally correct (−16000)?
3. Is the +16000 needed to close supplied by *no* emittable term (neither a keying change — banned sign flip — nor a bound multiplier at `x.m = 0`)?
4. Is the residual confined to the `c`-boundary (`ord(l)+ord(i) = card` / `= card+1`), 0 at interior rows?
5. Is the 22-row breadth genuinely broader than the banked 6, and are all 22 on the boundary?

### How to Verify
Re-run the Sprint-33 Day-1/Day-2 `/tmp` mine control from the repo root (the emit `$include` is repo-relative; assert `modelstat`; `x.up=inf` BANNED). Reproduce the residual decomposition (`DAY1_PROGRESS_NOTES.md` §5) row-for-row; confirm `d_N = d_Nh1` (value-invariance) and the 22-row `c`-boundary confinement. Cross-check `DAY2_MINE_REPLAN.md`.

### Risk if Wrong
- **H1 not value-invariant (a keying change closes it):** P1 is far cheaper than scoped — but Sprint-33's control makes this unlikely; over-scoping wastes budget (recoverable).
- **The dual-architecture gap is not the residual driver:** the reconciliation design (Unknown 1.2) is aimed at the wrong mechanism → mid-sprint REPLAN, no +1 Solve.

### Estimated Research Time
2 hours (re-run the control, reproduce the decomposition, confirm value-invariance)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.2: Does a head-offset dual-reconciliation drive `N→0` at all bound-active rows without perturbing interior rows?

### Priority
**Critical** — This is the P1 fix hypothesis; if the reconciliation cannot close `N→0` at all 22 boundary rows without moving interior rows, P1 REPLANs

### Assumption
An emit reconciliation that maps the head-placed precedence dual `pr.m(k,l+1,i,j)` into the `stat_x` boundary stationarity (a boundary-row dual-transfer term keyed on the S31 `head_domain_offsets` IR) drives the warm residual `N → 0` at **all** bound-active `c`-boundary rows AND leaves interior rows unchanged (0), then reaches presolve MS-1 @ 17500.

### Research Questions
1. What is the precise reconciliation term (which head-placed dual, at which shifted label, mapped into which `stat_x` row)?
2. Does it close `N → 0` at *all 22* boundary rows, not just the max row?
3. Does it leave every interior row at 0 (no new nonzero introduced)?
4. Does the closed warm residual then reach presolve MS-1 @ 17500 (the NLP optimum)?
5. Does it regress srpchase or any other head-offset model that shares the emit path?

### How to Verify
Prototype the reconciliation in a `/tmp` emit (no `src/` change); assert `modelstat`; measure the per-row residual before/after (all 22 boundary rows → 0, interior unchanged); then the presolve solve → MS-1 @ 17500. Compare against `MINE_CROSSTERM_DESIGN.md` §2/§3.

### Risk if Wrong
- **Cannot close all 22 without perturbing interior rows:** the reconciliation is the wrong mechanism → P1 REPLAN (H3, a further-deferred head-offset dual architecture); mine stays `model_infeasible`.
- **Closes the warm residual but MS-5 persists:** P1 is H-b (like fawley) — a genuine correction with no in-sprint Solve bucket.

### Estimated Research Time
3 hours (design + `/tmp` prototype + per-row residual + presolve solve)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.3: Is the 22-row breadth (not the banked 6) fully characterized, and does closing all 22 reach MS-1?

### Priority
**High** — If the breadth is wider than the reconciliation design accounts for, the fix is incomplete (partial residual → MS-5 persists)

### Assumption
The wrong-sign residual is exactly the 22 `c`-boundary rows characterized in `DAY2_MINE_REPLAN.md` (broader than the banked 6 from Sprint 32), and closing all 22 (not merely the max row) is both necessary and sufficient to reach MS-1 @ 17500.

### Research Questions
1. Are all 22 nonzero rows on the `c`-boundary (`ord(l)+ord(i) = card` / `= card+1`)?
2. Do the 22 rows share a single sign pattern, or do lo-active and up-active rows differ?
3. Is closing all 22 sufficient for MS-1, or does a residual elsewhere (a non-boundary term) remain?
4. Does the boundary classification generalize across the mine index structure (all `(k,l,i,j)` boundary instances)?

### How to Verify
Enumerate the 22 nonzero residual rows from the Day-1 decomposition; classify each by boundary condition + active bound; confirm the reconciliation (Unknown 1.2) targets all 22; verify the post-fix solve reaches MS-1 (not a reduced-but-nonzero residual).

### Risk if Wrong
- **Wider breadth / mixed residual:** the reconciliation closes some rows but not all → MS-5 persists, no +1 Solve, partial-fix REPLAN.

### Estimated Research Time
2 hours (row enumeration + boundary classification + sufficiency check)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.4: Does the S31 `head_domain_offsets` IR carry the shifted-label pairing the reconciliation needs?

### Priority
**High** — If the IR foundation cannot express the head-shifted precedence pairing, P1 needs IR/plumbing work beyond the emit change (scope expansion)

### Assumption
The S31 `EquationDef.head_domain_offsets` IR (per-position `IndexOffset|None` tuple, `has_head_domain_offset` derived) already carries the shifted-head-label pairing (`pr.m` stored at `(k,l+1,i,j)` while `lam_pr` pairs at base `(k,l,i,j)`) that the boundary dual-reconciliation needs, so no new IR plumbing is required.

### Research Questions
1. Does `head_domain_offsets` expose the `l+1` head shift for the mine precedence equation?
2. Can the emit read the shifted head label + the base body label from the existing IR fields?
3. Is any additional plumbing needed (a new IR field, or a change to `_try_build_param_offset_crossterm`)?
4. Does `lam_pr.fx` correctly zero the out-of-range `l=4` / `l−1=0` instances (as Sprint-33 confirmed)?

### How to Verify
Probe the mine `ModelIR` (`head_domain_offsets` for the precedence equation); trace `_try_build_param_offset_crossterm` (`src/kkt/stationarity.py`); confirm the shifted/base labels are readable; note any missing IR field.

### Risk if Wrong
- **IR gap:** P1 expands to include IR plumbing (mirroring the S31 `head_domain_offsets` landing) → scope beyond the 18–24h budget.

### Estimated Research Time
1.5 hours (IR probe + emit-path trace)

### Owner
Development team (KKT/IR specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 1.5: Is the P1 sizing (18–24h) realistic given the H3 REPLAN prior (banked premise twice-refuted)?

### Priority
**High** — P1 is the highest-REPLAN-prior track (refuted in both S32 and S33); an unrealistic sizing mis-allocates the whole sprint

### Assumption
The 18–24h P1 sizing (design + `/tmp` control + emit/IR plumbing + regression fixture + determinism) is realistic, and the Day-5 checkpoint surfaces an H3 REPLAN early enough to reallocate freed budget to P4/P6.

### Research Questions
1. Given the dual-architecture depth, is 18–24h enough for the design + `/tmp` control + emit change + fixture?
2. Does the Day-5 checkpoint surface the PROCEED/REPLAN decision before more than ~8h is sunk?
3. If H3 (REPLAN), where does the freed budget flow (P4 bound-transfer / P6 ganges)?
4. Is P1 the correct front-load position (Days 1–5) given its twice-refuted prior?

### How to Verify
Break the P1 work into sub-items with hour estimates (`MINE_DUAL_SUBSYSTEM_DESIGN.md`); confirm the `/tmp` control decision lands by Day 5; pin the H3 REPLAN exit + the freed-budget flow in `REPLAN_RISK_ASSESSMENT.md`.

### Risk if Wrong
- **Under-sized:** P1 overruns, squeezing P4/P6 (the fresh + fallback levers) → a flat-KPI sprint with no fallback win.

### Estimated Research Time
1 hour (sizing breakdown + checkpoint placement)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 2: sarf #1385 — Symbolic-Emit Subsystem

## Unknown 2.1: Does the symbolic emit mode require changing all three sites (S1/S2/S3) atomically?

### Priority
**Critical** — A partial change (one or two sites) yields an inconsistent MCP; the atomicity gates the whole P2 approach

### Assumption
Eliminating the 369,024-column `task(g,t,mn,mn)` materialization requires changing all three enumeration sites atomically — S1 (`acost3` scalar body-diff, `src/ad/constraint_jacobian.py`), S2 (`enumerate_variable_instances`, `src/ad/index_mapping.py:369`), S3 (variable stationarity, `src/kkt/stationarity.py`) — in one change; a partial change leaves `task` enumerated at the untouched site (an inconsistent MCP).

### Research Questions
1. Does each of S1/S2/S3 independently enumerate `task`'s 369K columns?
2. Is there any safe partial (change S3 only, keep S1/S2)?
3. Does the symbolic mode at S1 (parametric `acost3` body-diff) compose with the S2 short-circuit and the S3 guarded emit?
4. What is the interface between the three sites (a shared "symbolic variable" flag on `task`)?

### How to Verify
Trace each site's `task`-column enumeration (bounded translate probe); confirm the three-site atomicity from `DAY6_SARF_ASSESSMENT.md` + `SARF_EMIT_SUBSYSTEM_DESIGN.md`; sketch the shared interface.

### Risk if Wrong
- **A safe partial exists:** P2 is cheaper (good news). **The three sites don't compose:** P2 needs a deeper AD-core refactor → beyond the 20–28h budget, REPLAN.

### Estimated Research Time
2 hours (three-site trace + interface sketch)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: Will the parametric symbolic emit stay O(active = 398) and not re-trigger the timeout?

### Priority
**Critical** — The whole point of P2 is to stop the 369K-column blow-up; if the symbolic emit re-triggers the timeout (a 4th enumeration site), P2 fails

### Assumption
The symbolic/parametric emit stays O(active = 398): GAMS instantiates only the 398 live rows (`taskposs ∧ tech`) from one guarded `stat_task(g,t,m,n)$taskposs(g,t)` + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`, so translate drops to seconds (srpchase ~2.9s reference), not >75s.

### Research Questions
1. Does the parametric emit avoid materializing any `task` column at translate time (no hidden 4th enumeration site)?
2. Does the guarded `stat_task$taskposs` + `task.fx` let GAMS resolve the 398 at solve, not the translator at emit?
3. Is the translate time O(active = 398), i.e. seconds not >75s?
4. Does the `taskposs` runtime-computed set block any static enumeration the emit might attempt?

### How to Verify
Prototype the symbolic emit (`/tmp` or a bounded probe); measure translate time; confirm no >75s blow-up; verify no site materializes the 369K columns. Cross-check the O(active) budget gate in `SARF_EMIT_SUBSYSTEM_DESIGN.md`.

### Risk if Wrong
- **A 4th enumeration site re-triggers the timeout:** P2 REPLAN, +1 Translate deferred again (the 5th failed attempt on this track).

### Estimated Research Time
2 hours (symbolic-emit prototype + translate-time measurement)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Is the banked 7-term `stat_task` derivation complete and free of set-name-literal multiplier indices?

### Priority
**High** — If the derivation is incomplete or carries a set-name-literal index, the emitted `stat_task` is wrong (a silent emit bug, not a timeout)

### Assumption
The banked 7-term `stat_task` derivation (from the constraint bodies that reference `task`) is complete term-for-term, and none of the multiplier indices is a set-name literal (all are proper domain indices), so the symbolic `stat_task$taskposs` is correct.

### Research Questions
1. Do the 7 terms account for every constraint that references `task` (acost3 + the others)?
2. Is each term's multiplier index a proper domain index (no set-name literal)?
3. Does the `$taskposs` guard correctly restrict the emitted row to the active `(g,t)`?
4. Do the cross-terms stay parametric (no per-column expansion)?

### How to Verify
Re-derive `stat_task` term-for-term against the sarf constraint bodies; compare against the banked 7-term derivation; check each multiplier index; confirm the `$taskposs` guard placement. Cross-check `SARF_EMIT_SUBSYSTEM_DESIGN.md`.

### Risk if Wrong
- **Incomplete/wrong derivation:** the symbolic `stat_task` emits an incorrect stationarity → a silent Match/Solve failure even if translate succeeds.

### Estimated Research Time
2 hours (term-for-term re-derivation + index audit)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Does `task.fx` + the head guard + MCP matching yield exactly the 398 live rows?

### Priority
**Medium** — If the 398-active computation is off, the MCP is under- or over-determined (a Match failure)

### Assumption
The 398 live rows come from the head guard (`$taskposs`) + `task.fx` (fixing the inactive `task` to 0) + MCP variable/equation matching — not from the head guard alone (which gives ~124K rows) — so the emitted MCP is square at exactly 398.

### Research Questions
1. Does `$taskposs` alone give ~124K rows (not 398), confirming the guard is insufficient by itself?
2. Does `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` fix exactly the inactive complement?
3. Does MCP matching pair the 398 `stat_task` rows with the 398 free `task` columns?
4. Is the resulting MCP square (no unmatched var/eqn errors)?

### How to Verify
Compute the row counts (`$taskposs` alone vs `+ task.fx + matching`); confirm 398; verify MCP squareness (no unmatched errors) in the prototype.

### Risk if Wrong
- **Wrong active count:** the MCP is non-square → unmatched-var errors or a wrong Match.

### Estimated Research Time
1 hour (row-count computation + squareness check)

### Owner
Development team (AD/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Is the symbolic-emit golden byte-stable and deterministic (×3), with `--resolve-changed` GO?

### Priority
**Medium** — A non-deterministic or non-byte-stable emit fails the CI gates even if functionally correct

### Assumption
The symbolic `stat_task` emit produces a byte-stable golden, is deterministic across ≥ 3 `PYTHONHASHSEED` values, and passes `--resolve-changed --since-commit <S33-close>` with no regression to the other 134 translating models.

### Research Questions
1. Is the emitted `sarf_mcp.gms` byte-identical across ≥ 3 `PYTHONHASHSEED` runs?
2. Does the new emit mode leave the other 134 translating models byte-unchanged?
3. Does `--resolve-changed --since-commit <S33-close>` come back GO?
4. Does the golden-staleness gate pass?

### How to Verify
Emit sarf under 3 seeds (`{0,1,42}`); diff the goldens; run `--resolve-changed`; confirm the blast radius is sarf-only.

### Risk if Wrong
- **Non-determinism / collateral golden change:** the emit fails CI or regresses another model → rework.

### Estimated Research Time
1 hour (determinism ×3 + resolve-changed)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 3: fawley #1111/#1112 — Second-Index Correction + Forcing

## Unknown 3.1: Does the constraint-index-diagonal `sameas` extension close `max|stat_bq|` → 0 without regressing mbal / the 1-D polygon core?

### Priority
**Critical** — This is the P3 genuine-correction fix; if the extension leaks onto mbal or the 1-D core, P3 regresses already-passing models

### Assumption
Extending `_add_indexed_jacobian_terms` to recognize the *variable's-second-index = the constraint's-own-index* diagonal (qsb/pbal) and emit `$(sameas(cfq__,cf))` — symmetrically with the mbal first-index shape — closes `max|stat_bq|` from 18.468 to ~0 (once combined with the bound transfer, Category 4) WITHOUT changing the mbal term or regressing the 1-D polygon/ps2 core (a different emit path).

### Research Questions
1. Does the constraint-index-diagonal recognition fire on qsb/pbal but NOT on mbal (already correct)?
2. Does the extension leave the 1-D polygon/ps2 second-index core byte-unchanged (a different path)?
3. Does `max|stat_bq|` reach ~0 with sameas + the bound transfer (Category 4), or does a residual remain?
4. Does the extended gate over-fire on any other indexed model in the corpus?

### How to Verify
Prototype the constraint-index-diagonal `sameas` in a `/tmp` emit; measure `max|stat_bq|` (473 → 18.468 with sameas; → ~0 with + the bound transfer); confirm mbal + polygon/ps2 byte-unchanged; run `--resolve-changed`. Cross-check `FAWLEY_SECOND_INDEX_DESIGN.md`.

### Risk if Wrong
- **Gate leak onto mbal / 1-D core:** P3 regresses passing models → REPLAN; the ~1400-line general emit function makes this a real blast-radius risk.

### Estimated Research Time
2 hours (`/tmp` prototype + residual measurement + regression check)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Is fawley's +Solve genuinely H-b (MS-5 persists even with the warm residual fully closed)?

### Priority
**High** — Determines whether P3 yields a +1 Solve (if H-a) or only a genuine-floor lever + a forcing hand-off (if H-b, as Sprint-33 found)

### Assumption
The Sprint-33 Day-4/5 finding holds: fawley is **H-b** — sameas + all bound-transfers-fixed drives the warm residual to ~0 but the MCP still solves MS-5 @ 4399.557 (LP opt 2899.25), a non-emit divergence at fawley's scale, so P3's +Solve is a forcing hand-off (to P5's `--force` survey), not a warm-residual fix.

### Research Questions
1. With sameas + the bound transfer applied (warm residual ~0), does the MCP still solve MS-5 @ 4399.557?
2. Is the LP optimum 2899.25 (the reference)?
3. Is the divergence non-emit (structural, at fawley's scale) rather than a remaining warm-start residual?
4. Does any `--force` lever (homotopy/multistart/optfile) cross for fawley?

### How to Verify
Re-run the Sprint-33 fawley control (sameas + bound transfer, warm residual ~0); assert `modelstat`; confirm MS-5 @ 4399.557 persists (H-b). Cross-check `DAY4_FAWLEY_CONTROL.md` + `DAY5_FAWLEY_CLOSE.md`.

### Risk if Wrong
- **Actually H-a:** P3 yields a +1 Solve (better than projected). **Confirmed H-b:** P3 is a genuine-floor lever only; the +Solve hands to forcing (as scoped).

### Estimated Research Time
1.5 hours (re-run the control + `modelstat` confirm + `--force` probe)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Does the genuine cross-term correction lift the genuine floor (fawley cold-match) even under H-b?

### Priority
**High** — The genuine-floor +1 is P3's in-sprint KPI bucket; if the correction does not make fawley cold-match, P3 yields zero KPI even shipping the correct fix

### Assumption
The constraint-index-diagonal `sameas` correction changes fawley's cold emit such that the cold MCP matches the NLP (a genuine cold-emit correction), lifting the genuine floor by +1 — even though the +Solve is H-b (forcing).

### Research Questions
1. Does the sameas correction change fawley's cold emit (a genuine cold-emit change, not a warm-start-only fix)?
2. Under H-b (MS-5), does fawley "match" in the genuine-floor sense (cold emit byte-correct), or does the floor only credit a solved model?
3. Is the genuine-floor definition satisfied by a corrected cold emit that still needs forcing to converge?
4. Does the correction lift the floor 75 → 76, or is the floor credit contingent on the solve?

### How to Verify
Apply the genuine-vs-methodology floor definition (`reference_match_kpi_corpus_scope`) to fawley post-correction; confirm whether a corrected-but-forcing cold emit counts toward the floor; cross-check the PR25 partition (Task 2).

### Risk if Wrong
- **Floor credit contingent on solve:** P3 yields zero in-sprint KPI (the correction is genuine but uncredited under H-b) → the correction is worth shipping for correctness but moves no bucket.

### Estimated Research Time
1 hour (floor-definition application + PR25 partition cross-check)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 3.4: Is the fawley 2-D second-index fixture fail-before/pass-after, gated on the correction landing?

### Priority
**Medium** — The P7 fixture only lands once P3 lands; if P3 REPLANs, the fixture is deferred (as Sprint-33's shape12/13/fawley fixtures were)

### Assumption
A fawley 2-D second-index property fixture (following the Sprint-33 `test_sample_pruned_var_l_init.py` pattern: raw-file emit + skip-if-absent) fails before the correction and passes after, and it lands only once the P3 correction lands.

### Research Questions
1. What is the minimal assertion (e.g. the `$(sameas(cfq__,cf))` guard present on qsb/pbal in the emit)?
2. Does it fail before the correction (the over-sum) and pass after?
3. Does it skip cleanly when `data/gamslib/raw/fawley.gms` is absent (CI)?
4. Is it correctly deferred if P3 REPLANs?

### How to Verify
Sketch the fixture (raw-file emit + the sameas-guard assertion + skip-if-absent); confirm fail-before/pass-after against the `/tmp` correction; note the P3-landing gate.

### Risk if Wrong
- **Fixture lands without the fix:** a false-passing test (low impact — the gate is the P3 landing).

### Estimated Research Time
0.5 hours (fixture sketch + gate note)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 4: Max-Convention Bound-Transfer-Sign Track

## Unknown 4.1: Is the sign-robust `= abs(.m)` transfer correct at active bounds without over-transferring on presolve-match models?

### Priority
**Critical** — This is the P4 fix; if the sign-robust transfer over-transfers (fires at interior/inactive bounds), it regresses the presolve-match cohort

### Assumption
Replacing the min-convention sign gate (`.m > 0` / `.m < 0`) with a sign-robust `= abs(.m)` transfer at the *active* bound is correct for both MINIMIZE and MAXIMIZE solves, and — because it fires only at active bounds — it does not over-transfer on the presolve-match cohort (interior/inactive bounds contribute 0).

### Research Questions
1. Does `= abs(.m)` at the active bound reproduce the correct multiplier sign for both MINIMIZE and MAXIMIZE?
2. Does the transfer fire only at active bounds (no contribution at interior/inactive)?
3. Does it leave the presolve-match cohort's warm-start values unchanged (no over-transfer)?
4. Does it close the fawley residual-18.468 cell + the mine upper-bound cells (the two discovery cases)?
5. Is the active-bound gating correct (does the emit know which bound is active at warm-start)?

### How to Verify
Locate the min-convention gates in `src/emit/emit_gams.py`; prototype `= abs(.m)` in a `/tmp` emit; confirm it closes the fawley + mine cells; confirm the presolve-match cohort's warm values are unchanged; assert `modelstat`. Cross-check `DAY4_FAWLEY_CONTROL.md` §5.

### Risk if Wrong
- **Over-transfer:** the sign-robust transfer regresses presolve-match models → `--resolve-changed` NO-GO, REPLAN.

### Estimated Research Time
1.5 hours (`/tmp` prototype + fawley/mine cell check + presolve-cohort check)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Which MAXIMIZE-cohort models' MCP divergence is warm-residual-driven (a +Solve lever) vs structural (H-b)?

### Priority
**High** — Determines P4's +Solve yield; if every MAXIMIZE `model_infeasible` model is structural (H-b like fawley), P4 recovers no bucket

### Assumption
Some MAXIMIZE `model_infeasible` model in the corpus has a divergence that is *warm-residual-driven* (the sign-robust transfer closes the residual AND reaches MS-1), i.e. P4 is a genuine +Solve lever on a model *other* than fawley (which is structurally H-b).

### Research Questions
1. Which corpus models `solve ... maximizing ...` (the MAXIMIZE cohort)?
2. Of those, which are `model_infeasible` / presolve-recovered (the +Solve candidates) vs already-solving (the regression-risk set)?
3. For each candidate, does the sign-robust transfer close the warm residual AND reach MS-1 (warm-residual-driven) vs stay MS-5 (structural)?
4. Is any candidate a clean +1 Solve (not H-b)?

### How to Verify
Enumerate the MAXIMIZE cohort (grep the raw sources / DB for `maximizing`); classify each `model_infeasible` MAXIMIZE model; for each, apply the sign-robust transfer in a `/tmp` control and assert `modelstat` (warm-residual-driven vs structural). Cross-check `BOUND_TRANSFER_SIGN_DESIGN.md`.

### Risk if Wrong
- **All structural (H-b):** P4 recovers no Solve bucket (a documented general-correctness finding, like fawley) → no +Solve, the fresh lever yields nothing.

### Estimated Research Time
2 hours (cohort enumeration + per-candidate `/tmp` control)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Does the sign-robust transfer keep `--resolve-changed` GO (no presolve-cohort regression)?

### Priority
**High** — The sign-robust transfer touches a general emit path; a presolve-cohort regression is the primary blast-radius risk

### Assumption
The sign-robust transfer, gated to fire only at active bounds, leaves the 44 presolve-recovered + the 64 cold-match Solve models byte-unchanged where it should, so `--resolve-changed --since-commit <S33-close>` comes back GO.

### Research Questions
1. Does the transfer change any presolve-match model's warm-start block?
2. Does it change any cold-match model's emit?
3. Does `--resolve-changed --since-commit <S33-close>` come back GO?
4. Is the blast radius confined to the MAXIMIZE `model_infeasible` candidates?

### How to Verify
Run `--resolve-changed --since-commit <S33-close>` after the `/tmp`-validated change; confirm GO; enumerate the changed goldens (should be only the MAXIMIZE candidates).

### Risk if Wrong
- **Presolve-cohort regression:** `--resolve-changed` NO-GO → the transfer over-fires, REPLAN.

### Estimated Research Time
1 hour (`--resolve-changed` + blast-radius enumeration)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 4.4: Is the min-convention gate correctly localized in `emit_gams.py` (the fix surface)?

### Priority
**High** — A mislocated fix surface is the classic prep-doc `file:line` hypothesis error (wrong ~4× in S27); locating the gate wrong sinks the P4 effort

### Assumption
The min-convention sign gates (`.m > 0` / `.m < 0`) that produce the `piL_*/piU_*` warm-start transfers are localized in `src/emit/emit_gams.py` (the presolve bound-transfer emit lines), and that is the sole fix surface for P4.

### Research Questions
1. Where exactly are the `piL_*/piU_*` transfer lines emitted (`emit_gams.py` line range)?
2. Is the min-convention sign gate there, or in a shared AD/KKT helper?
3. Is there a single fix surface, or are the lo/up transfers emitted separately?
4. Does any other emit path (the indexed `l`-transfers) share the same gate?

### How to Verify
Grep `src/emit/emit_gams.py` for the `piL`/`piU` transfer + the `.m > 0`/`.m < 0` gate; confirm the line range; check whether the indexed `l`-transfers share the gate. (The prep-doc `file:line` is a Day-0-re-confirm hypothesis, PR24.)

### Risk if Wrong
- **Mislocated surface:** P4 edits the wrong path → no effect / collateral change; the classic S27 hypothesis-error failure mode.

### Estimated Research Time
1 hour (grep + line-range confirm)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 5: camcge Walras (Epic 5) + rocket PATH Submission

## Unknown 5.1: Does the full dual-consistent Walras redefinition reach MS-1 at omega 191.7346 in a `/tmp` prototype?

### Priority
**High** — The Epic-5 gate for camcge; if the dual-consistent redefinition still lands MS-4, camcge stays Epic-5-deferred (the expected disposition)

### Assumption
The full dual-consistent Walras redefinition (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law) reaches MS-1 at omega 191.7346 in a `/tmp` prototype — checking the *dual* side, not just the primal (the Sprint-32/33 MS-4 was a dual rank-deficiency, not a primal error).

### Research Questions
1. Does the dual-consistent redefinition (dual side, not a dropped row) reach MS-1 (not MS-4)?
2. Is omega 191.7346 (the correct numéraire value) preserved at MS-1?
3. Is the MS-4 Walras rank-deficiency (gdp/depreq/hhsaveq/gruse) resolved by the dual redefinition?
4. Is this in-scope for Sprint 34 or confirmed Epic-5-deferred?

### How to Verify
Prototype the dual-consistent redefinition in a `/tmp` emit; assert `modelstat`; check MS-1 + omega 191.7346 + the dual side. Cross-check `CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Risk if Wrong
- **Still MS-4:** camcge stays Epic-5-deferred (expected — 3+ sprints of MS-4 variants); the design is the Epic-5-ready recipe, not an in-sprint fix.

### Estimated Research Time
1.5 hours (`/tmp` prototype + dual-side check)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Does the S1∧S2∧S3 degeneracy detector false-flag irscge/lrgcge/moncge/stdcge?

### Priority
**Medium** — A false-positive detector would mis-classify the four solving CGE siblings (a correctness regression on models that already solve)

### Assumption
The S1∧S2∧S3 degeneracy detector (S3 = cold-MCP-singular-at-iter-0, the false-positive guard) flags only camcge and passes through irscge/lrgcge/moncge/stdcge (which already solve), so it does not mis-classify the solving siblings.

### Research Questions
1. Do all three signals (S1∧S2∧S3) fire on camcge?
2. Does at least one signal fail to fire on each of irscge/lrgcge/moncge/stdcge (the pass-through)?
3. Is S3 (cold-MCP-singular-at-iter-0) the discriminating false-positive guard?
4. Does the detector touch any Solve/Match bucket (it should be diagnostic-only)?

### How to Verify
Run the detector against camcge + the four siblings; confirm camcge fires + the siblings pass; confirm diagnostic-only (no bucket change). Cross-check `EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Risk if Wrong
- **False-positive on a sibling:** a solving CGE model is mis-flagged (a correctness/reporting regression) → detector re-scope.

### Estimated Research Time
1 hour (detector run + sibling pass-through check)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Is the rocket PATH-consultation input complete for the Sprint-35 submission, and is the Case-c sign flip still BANNED?

### Priority
**Medium** — A missing input element delays the Sprint-35 PATH-author consultation; the sign-flip BAN is a standing correctness guard

### Assumption
The FINALIZED rocket PATH-consultation input (concrete question + ruled-out-lever survey + reproducible case + `--force` scaffold) is complete for submission to the Sprint-35 PATH-author consultation, and the Case-c objective-gradient sign flip remains BANNED (refuted 4× — hhfair/irscge/lrgcge/moncge + camcge `stat_tm` guard).

### Research Questions
1. Is the rocket input complete (question + lever survey + reproducer + scaffold)?
2. Is the reproducible case runnable (a clean `--force` scaffold emit)?
3. Is the Case-c family (hhfair/irscge/lrgcge/moncge + cesam/lnts) documented as `case_c_objdef`?
4. Is the sign flip still BANNED for every Case-c model?

### How to Verify
Review the rocket input package (`ROCKET_CASEC_FORCING_PLAN.md` + `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`); confirm completeness + the reproducer; confirm the Case-c documentation + the sign-flip BAN.

### Risk if Wrong
- **Incomplete input:** the Sprint-35 consultation slips. **Sign flip un-banned:** a refuted-4× correctness regression on Case-c models.

### Estimated Research Time
0.5 hours (input review + BAN confirm)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 6: Banked Failure-Cohort Re-Triage

## Unknown 6.1: Do ganges/gangesx share a single `$141/$145/$149` translate-syntax root, distinct from sample's `$140`?

### Priority
**High** — The failure-cohort is the Sprint-33-proven bucket source; if ganges/gangesx share one root, a single fix may recover both (+1 or +2 Solve)

### Assumption
ganges and gangesx share a single `path_syntax_error` translate-syntax root (`$141/$145/$149` on bound-clamp `x$(not(...))=0` + parameter-assignment lines) that is *distinct* from sample's `$140` (pruned-var `.l`-init), and their `.l`-init referenced vars are *declared* (so the P6 sample fix does not touch them) — so a single new fix may recover both.

### Research Questions
1. Do ganges + gangesx emit + compile to the same `$141/$145/$149` error class?
2. Is the root a bound-clamp `x$(not(...))=0` / parameter-assignment translate-syntax issue?
3. Are their `.l`-init referenced vars declared (confirming the P6 sample fix does not apply)?
4. Does a single fix recover both, or are they two roots that merely share an error code?

### How to Verify
Emit + compile ganges + gangesx (`data/gamslib/raw/`, skip-if-absent); capture the `$141/$145/$149` lines; confirm the shared vs distinct root; confirm the referenced vars are declared. Cross-check `SPRINT_34_CARRYFORWARDS.md` (banked P6).

### Risk if Wrong
- **Two distinct roots:** a single fix recovers only one (+1 not +2); the "shared root" hypothesis was only partially right (the Sprint-33 lesson).

### Estimated Research Time
1.5 hours (emit + compile both + error-line diagnosis)

### Owner
Development team (emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: Is agreste genuinely CASE_B or a double-`solve` scenario-driver artifact?

### Priority
**Medium** — If agreste's CASE_B is a scenario-driver artifact (not an emit bug), chasing it wastes budget

### Assumption
agreste's CASE_B `stat_sales` rel 2.0 needs harness scope-verify: it is a single-model-solved-twice scenario driver, so the factor-of-2 may be a driver artifact (the model solved twice, doubling a gradient) rather than a genuine dropped-gradient emit bug.

### Research Questions
1. Does agreste solve the same model twice (a scenario driver)?
2. Is the `stat_sales` rel 2.0 a genuine dropped-gradient (factor-of-2) emit bug or a driver-doubling artifact?
3. Does the harness scope the residual to a single solve, or does it conflate the two?
4. Is agreste a genuine CASE_B candidate or a false-positive?

### How to Verify
Inspect agreste's source (the two `solve` statements); run the harness with single-solve scoping; determine whether the factor-of-2 is genuine or a driver artifact. Cross-check `SPRINT_34_CARRYFORWARDS.md`.

### Risk if Wrong
- **Driver artifact:** agreste is a false CASE_B → chasing it wastes budget (the right call is to document + defer).

### Estimated Research Time
1 hour (source inspection + single-solve harness scope)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Is the failure-cohort multi-root (verify per-model), not a single shared root?

### Priority
**Low** — A meta-assumption; low direct impact but frames the P6 approach (verify per-model, do not batch)

### Assumption
The `path_syntax_error` failure-cohort is multi-root (the Sprint-33 lesson: sample `$140`, ganges/gangesx `$141/$145/$149` are *different* roots), so P6 must verify per-model and not assume a single fix recovers the cohort.

### Research Questions
1. How many distinct roots does the residual `path_syntax_error` cohort carry?
2. Is each root model-specific, or do subsets share a root?
3. Does the per-model-verify discipline (not batch) hold?

### How to Verify
Enumerate the residual `path_syntax_error` models; note the distinct error classes; confirm the per-model-verify approach. Cross-check `SPRINT_33/SPRINT_RETROSPECTIVE.md` §3 lesson 5.

### Risk if Wrong
- **Assumed single root:** a batch fix misses the per-model roots (low impact — the discipline is already the Sprint-33 lesson).

### Estimated Research Time
0.5 hours (cohort enumeration + root-class note)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

# Category 7: Infrastructure — Property Fixtures + Genuine-Floor Tracking + Checkpoint

## Unknown 7.1: Do the shape12/shape13/fawley property fixtures fail-before/pass-after only once P1/P2/P3 land?

### Priority
**Medium** — The property fixtures are gated on the track landings (as Sprint-33's were deferred); scoping them early lets P7 start against a plan

### Assumption
The shape12 (head-offset dual), shape13 (sarf symbolic), and fawley (second-index) property fixtures — following the Sprint-33 `test_sample_pruned_var_l_init.py` pattern (raw-file emit + skip-if-absent) — fail before their respective fix and pass after, and each lands *only once* its track (P1/P2/P3) lands.

### Research Questions
1. What is each fixture's minimal fail-before/pass-after assertion (the emitted term the fix introduces)?
2. Does each skip cleanly when the raw source is absent (CI)?
3. Is each correctly deferred if its track (P1/P2/P3) REPLANs (the Sprint-33 precedent)?
4. Do the fixtures follow the established `test_sample_pruned_var_l_init.py` pattern?

### How to Verify
Sketch each fixture (assertion + skip-if-absent + the landing gate); confirm the pattern matches `test_sample_pruned_var_l_init.py`; note the per-track deferral. Cross-check `SPRINT_33/DAY12_P7_INFRA.md`.

### Risk if Wrong
- **Fixtures land without the fix:** false-passing tests (low impact — the gate is the track landing).

### Estimated Research Time
1 hour (three fixture sketches + gate notes)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Is the PR25 genuine-floor anchor 75 (not 74), and is the Day-0 code anchor the S33-close SHA (not `4cbf8bff`)?

### Priority
**Critical** — A wrong baseline anchor makes every KPI delta + the `--resolve-changed` no-regression gate meaningless (breaks all measurement)

### Assumption
The Sprint-34 Day-0 baseline = Sprint-33 close (Solve 108 / Match 93 / genuine floor 75 / model_infeasible 7 / path_syntax_error 7 / Translate 135 / all-219 Match 96); the PR25 genuine-floor re-baseline anchor is **75** (not the Sprint-33 Day-0 74); and — unlike Sprint 33 — the Day-0 code anchor for `--resolve-changed` is the **S33-close SHA**, because the S33 P6 sample fix changed `sample_mcp.gms` + the DB (so `4cbf8bff` is now historical, no longer byte-unchanged).

### Research Questions
1. Does the committed DB recompute to Solve 108 / Match 93 / floor 75 / mi 7 / Translate 135 / all-219 96?
2. Is the PR25 genuine-floor anchor 75 (the S33 close), not 74?
3. Is the Day-0 code anchor the S33-close SHA (is `git diff <S33-close>..HEAD -- src/ scripts/` empty)?
4. Is `4cbf8bff` confirmed superseded (the S33 sample DB change)?

### How to Verify
Recompute the 142-corpus buckets from the committed DB (Task 2); confirm the anchor is the S33-close SHA (`git log` for the S33 close merge); confirm the diff is empty; confirm the PR25 partition = 75. Cross-check `SPRINT_33/SPRINT_LOG.md` + `BASELINE_METRICS.md`.

### Risk if Wrong
- **Wrong anchor:** every KPI delta + the no-regression gate is measured against the wrong baseline → every Sprint-34 KPI claim is unverifiable.

### Estimated Research Time
0.5 hours (DB recompute + anchor confirm)

### Owner
Development team

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Unknown 7.3: What does the Epic-4 `SUMMARY.md` row-34 need, and is it a Day-12 continuation?

### Priority
**Low** — A mis-formatted summary row breaks the Epic-4 rollup (low impact, easily fixed)

### Assumption
The Epic-4 `SUMMARY.md` row 34 needs the {Theme / Headline KPIs (Solve/Match/floor at close) / Firm landing(s) / REPLAN'd → carryforward} cells in the rows-28–33 format, and the continuation is a Day-12 close task (as Sprints 32/33 were).

### Research Questions
1. Which cells does the Sprint-34 row need (Theme / Headline KPIs / Firm landing(s) / REPLAN'd → carryforward)?
2. What is the backfill format (consistent with rows 28–33)?
3. Is the Sprint-34 theme cell correct (the Sprint-33 carryforwards), not mislabeled?
4. Is the continuation a Day-12 task (as Sprint 33's was)?

### How to Verify
Review `SUMMARY.md` row 34 (currently "(planned)"); confirm the cell format vs rows 28–33; schedule the continuation in the Task-11 plan.

### Risk if Wrong
- **Inconsistent summary:** a mis-formatted row breaks the Epic-4-close rollup (low impact, easily fixed).

### Estimated Research Time
0.5 hours (SUMMARY.md review)

### Owner
Sprint planning

### Verification Results
🔍 **Status:** INCOMPLETE

---

## Confirmed Knowledge (From Sprint 33 and Earlier)

These items were control-confirmed in Sprint 33 and are treated as knowledge (not unknowns) for Sprint 34:

### mine (P1)
- H1 head-label multiplier re-keying is **value-invariant** — the `l+1`-shifted transfer already stores the head-label value at the body label (warm residual unchanged 22→22 rows, `d_N = d_Nh1` row-for-row). At the max row `stat_x(3,1,1)`, `x` is bound-active with `x.m = 0`, the cross-term is structurally correct (−16000), and closing needs +16000 that no keying change (banned sign flip) or bound multiplier (`x.m = 0`) supplies. The residual is a deeper head-offset dual-architecture gap (22-row `c`-boundary breadth). (`DAY2_MINE_REPLAN.md`)

### sarf (P2)
- The blow-up is per-column differentiation of `task`'s 369,024 columns at three sites (S1 `acost3`, S2 `enumerate_variable_instances`, S3 stationarity); the active `taskposs ∧ tech` = 398 is **not statically enumerable** (`taskposs` is runtime-computed) → a from-scratch symbolic/parametric emit mode is required (atomic, no safe partial). (`DAY6_SARF_ASSESSMENT.md`)

### fawley (P3)
- The qsb/pbal cross-terms miss the `$(sameas(cfq__,cf))` the mbal term has (control-proven: `max|stat_bq|` 473 → 18.468); the fix surface is a constraint-index diagonal in `_add_indexed_jacobian_terms` (~1400 lines). fawley's +Solve is **H-b** — sameas + all bound-transfers-fixed → warm residual ~0 but the MCP still solves MS-5 @ 4399.557 (LP opt 2899.25), a non-emit divergence. (`DAY4_FAWLEY_CONTROL.md`, `DAY5_FAWLEY_CLOSE.md`)

### The max-convention bound-transfer-sign gap (P4, NEW)
- The `piL_*/piU_*` warm-start transfers are gated on min-convention `.m > 0` / `.m < 0`; for a MAXIMIZE solve they skip correctly-signed bound multipliers — surfaced in both fawley (`bq.m < 0` at a lower bound) and mine (upper-bound multipliers). A sign-robust `= abs(.m)` transfer at the active bound is the candidate general fix. (`DAY4_FAWLEY_CONTROL.md` §5)

### camcge (P5) / rocket
- Step 1 (`nu_mps_fx` scalar-`fx` transfer, `= mps.m` direct) landed → `stat_mps` Case-a (S32). Step 2's numéraire reaches omega 191.7346 but MS-4 (Walras rank-deficiency). rocket's non-convergence is intrinsic (Case-c); the PATH-consultation input is FINALIZED. hhfair + the CGE cluster + cesam/lnts are documented `case_c_objdef`; the sign flip is BANNED (refuted 4×). (`CAMCGE_WALRAS_DESIGN.md`, `ROCKET_CASEC_FORCING_PLAN.md`)

### Process
- **Always assert `modelstat` before reading an objective off a solve** (the Sprint-31 `x.up=inf` measurement error, BANNED for mine). The single-point harness residual is systematically misleading for non-convex / objective-defining-intermediate-variable shapes. Run the `/tmp` control BEFORE any high-blast-radius `src/` change (PR24/PR27). The failure cohort is **multi-root** — verify per-model.

---

## Template for New Unknowns

When adding unknowns during Sprint 34:

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

**Before Sprint 34 Day 1:**
1. Review all Critical and High priority unknowns (18 total) via prep Tasks 2–10 (see the Task-to-Unknown mapping appendix)
2. Run the `/tmp` control experiment for each track BEFORE any `src/` change (the PR24/PR27 gate)
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED / ❌ WRONG)
4. Adjust the Sprint 34 scope + schedule (Task 11) if any Critical assumption is wrong
5. Share findings with the team during sprint planning

**During Sprint 34:**
1. Reference this document daily
2. Add newly discovered unknowns (use the template)
3. Update verification results as each track is implemented
4. Move resolved items to "Confirmed Knowledge"

---

## Appendix: Task-to-Unknown Mapping

This table shows which prep tasks (from `PREP_PLAN.md`) verify which unknowns. Each prep task's "Unknowns Verified" metadata mirrors this table.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Sprint 33 → 34 Day-0 Baseline + Genuine-Floor Re-Baseline | 1.1, 3.1, 7.2 | Re-confirms the Day-0 mine/fawley buckets (contributes to 1.1, 3.1) and the PR25 genuine-floor anchor 75 + the S33-close code anchor (7.2, primary) |
| Task 3: mine Head-Offset Dual Subsystem — Design | 1.1, 1.2, 1.3, 1.4, 1.5 | The full Category-1 design: value-invariance/dual-architecture (1.1), reconciliation (1.2), 22-row breadth (1.3), IR pairing (1.4), sizing (1.5) |
| Task 4: sarf Symbolic/Parametric `stat_task` Emit-Mode Design | 2.1, 2.2, 2.3, 2.4, 2.5 | The full Category-2 design: three-site atomicity (2.1), O(active) budget (2.2), 7-term derivation (2.3), `task.fx`/398 (2.4), determinism (2.5) |
| Task 5: fawley Second-Index Correction + Forcing Design | 3.1, 3.2, 3.3, 3.4 | The full Category-3 design: constraint-index-diagonal correction (3.1), H-b (3.2), floor lift (3.3), fixture (3.4) |
| Task 6: Max-Convention Bound-Transfer-Sign Track Design | 4.1, 4.2, 4.3, 4.4 | The full Category-4 design: sign-robust transfer (4.1), MAXIMIZE-cohort +Solve survey (4.2), no-regression (4.3), fix-surface (4.4) |
| Task 7: camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan | 5.1, 5.2, 5.3 | The full Category-5 plan: Walras MS-1 prototype (5.1), detector scope (5.2), rocket submission + sign-flip BAN (5.3) |
| Task 8: Author Phase 0 Acceptance Gates for the Sprint-34 Tracks | 1.2, 2.2, 3.1, 4.1, 5.1 | The per-track `/tmp` control/gate feasibility for each of P1–P5 (contributes to the correctness unknowns via the Phase-0 gate design) |
| Task 9: Diagnosis-Heavy / REPLAN-Prone Track Risk Assessment | 1.5, 2.2, 3.2, 4.2 | The REPLAN-probability unknowns: mine sizing/depth (1.5), sarf timeout re-trigger (2.2), fawley H-b (3.2), bound-transfer structural-vs-warm (4.2) |
| Task 10: Reusable-Tooling Readiness Audit + Backlog Fix-Surface Analysis | 6.1, 6.2, 6.3, 7.1, 7.3 | The full Category-6 (ganges/gangesx 6.1, agreste 6.2, multi-root discipline 6.3) + the Category-7 infrastructure (property fixtures 7.1, SUMMARY continuation 7.3) |

**Note:** Task 11 (Plan Sprint 34 Detailed Schedule) integrates all verified unknowns into the day-by-day schedule (it does not verify unknowns directly). Task 1 (this document) authors the unknowns. Some unknowns are verified by more than one task (e.g., 1.1 by Tasks 2/3; 2.2 by Tasks 4/8/9; 3.1 by Tasks 2/5/8; 4.1 by Tasks 6/8) — the primary owner is the per-track design task (Tasks 3–7); Tasks 2/8/9 *contribute* via the baseline, the Phase-0 gate, and the REPLAN assessment respectively.

---

**Document Status:** 🔵 Active — Pre-Sprint 34
**Last Updated:** 2026-07-18
**Owner:** Sprint 34 Planning Team
**Review Frequency:** Daily during Sprint 34
