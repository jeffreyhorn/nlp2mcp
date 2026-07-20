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

**Deferred-unknown lineage (from Sprint 33):** Sprint 34's Categories 1–5 are the direct continuation of the Sprint-33 REPLAN'd/deferred tracks (`SPRINT_33/SPRINT_RETROSPECTIVE.md` §4 + `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`). The Sprint-33 Known Unknowns for these tracks were resolved as *control-confirmed characterizations with un-built (and, for P1/P3, harder-than-anticipated) fixes*; Sprint 34 carries forward the *implementation-shape* unknowns (the dual-reconciliation architecture, the symbolic emit mode, the constraint-index-diagonal correction, the NEW sign-robust bound transfer), not the diagnosis. Category 4 is a **newly-surfaced** track (the max-convention bound-transfer-sign gap, discovered Sprint-33 Day 4).

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
Re-run the Sprint-33 Day-1/Day-2 `/tmp` mine control from the repo root (the emit `$include` is repo-relative; assert `modelstat`; `x.up=inf` BANNED). Reproduce the residual decomposition (`SPRINT_33/DAY1_PROGRESS_NOTES.md` §5) row-for-row; confirm `d_N = d_Nh1` (value-invariance) and the 22-row `c`-boundary confinement. Cross-check `SPRINT_33/DAY2_MINE_REPLAN.md`.

### Risk if Wrong
- **H1 not value-invariant (a keying change closes it):** P1 is far cheaper than scoped — but Sprint-33's control makes this unlikely; over-scoping wastes budget (recoverable).
- **The dual-architecture gap is not the residual driver:** the reconciliation design (Unknown 1.2) is aimed at the wrong mechanism → mid-sprint REPLAN, no +1 Solve.

### Estimated Research Time
2 hours (re-run the control, reproduce the decomposition, confirm value-invariance)

### Owner
Development team (KKT/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (Task 2 Day-0-bucket + Task 3 primary — value-invariance/dual-architecture)
**Verified by:** Task 2 (Day-0 bucket) + Task 3 (primary: value-invariance + dual-architecture)
**Date:** 2026-07-18

**Findings (Task 2 — Day-0 bucket):**
- At Day 0, mine is `model_infeasible` (MS 5), a `verified_convex` candidate — the P1 bucket the head-offset dual subsystem targets (infeasible → MODEL STATUS 1 if the reconciliation cold-matches). Confirmed from the committed DB.

**Evidence:** `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` §3 (model_infeasible members) + §5 (mine provenance MS 5).

**Decision:** the Day-0 mine bucket is confirmed; the value-invariance + dual-architecture + reconciliation-hypothesis aspects of this unknown are the primary work of Task 3 (mine dual-subsystem design).

**Task-3 (primary) — ✅ VERIFIED (2026-07-18):** H1 head-label re-keying is **value-invariant** (S33 Day-2 control: 22→22 rows, `d_N=d_Nh1` row-for-row); the live harness re-confirms the CASE_B fingerprint (`stat_x(3,1,1)` rel 2.37 raw −32000, dual scale 1.35e4, dual transfer CONSISTENT). The residual is a **head-offset dual-architecture mismatch** — the head-placed precedence dual `pr.m(k,l+1,i,j)` enters `stat_x` with opposite orientation at the boundary, with `x.m=0` degeneracy — **not** a keying or cross-term error (the cross-term is algebraically correct, S33 §3). Evidence: `MINE_DUAL_SUBSYSTEM_DESIGN.md` §1–§3; live `kkt_residual.py mine.gms`.

---

## Unknown 1.2: Does a head-offset dual-reconciliation drive the cold MCP to MS-1 @ 17500 without perturbing interior rows?

### Priority
**Critical** — This is the P1 fix hypothesis; if the reconciliation cannot drive the **cold** MCP to MS-1 @ 17500 (all 22 boundary rows closing in the cold solution, interior rows unperturbed), P1 REPLANs

### Assumption
An emit reconciliation that anchors the head-placed precedence dual `pr.m(k,l+1,i,j)`'s *complementarity* to the head-side variable (keyed on the S31 `head_domain_offsets` IR) drives the **cold** MCP to **MS-1 @ 17500** — with the 22 boundary rows closing in the cold solution and interior rows unperturbed. **NB (gate reframed — see Verification Results):** the gate is the **cold** solve, **not** the warm residual `N → 0`. Because keying is value-invariant (Unknown 1.1), a keying/pairing change leaves the warm-point term VALUES unchanged, so `N → 0` is un-hittable by this class of fix and is the wrong diagnostic; the *structural* pairing change is what the cold solve reflects.

### Research Questions
1. What is the precise reconciliation term (which head-placed dual, at which shifted label, mapped into which `stat_x` row)?
2. Does it close all 22 boundary rows **in the cold solution** (not just the max row)?
3. Does it leave every interior row consistent (no new nonzero introduced)?
4. Does the cold MCP then reach MS-1 @ 17500 (the NLP/LP optimum), `modelstat` asserted?
5. Does it regress srpchase or any other head-offset model that shares the emit path?

### How to Verify
Prototype the reconciliation in a `/tmp` emit (no `src/` change); assert `modelstat`; **gate on the cold MCP reaching MS-1 @ 17500** (the 22 boundary rows closing in the cold solution, interior rows unperturbed) — not on the warm residual `N → 0`, which is keying-invariant. Compare against `SPRINT_33/MINE_CROSSTERM_DESIGN.md` §2/§3 + `MINE_DUAL_SUBSYSTEM_DESIGN.md` §5.

### Risk if Wrong
- **Cannot drive the cold MCP to MS-1 without perturbing interior rows or regressing srpchase:** the reconciliation is the wrong mechanism → P1 REPLAN (H3′, a further-deferred head-offset dual architecture); mine stays `model_infeasible`.
- **The boundary is a genuine dual-degeneracy the emit cannot deterministically reconcile:** no emit-consistent change reaches cold MS-1 → REPLAN / a PATH-consultation question (an LP whose warm KKT point is not MCP-reconcilable).

### Estimated Research Time
3 hours (design + `/tmp` prototype + per-row residual + presolve solve)

### Owner
Development team (KKT/emit specialist)

### Verification Results
🔍 **Status:** INCOMPLETE — DESIGN-SPECIFIED (the reconciliation design + the cold-MS-1 `/tmp` control are fully specified, but the control is the Sprint-34 **Day-1** executed gate and has **not** been run in this docs-only prep — the empirical question "does H_dual reach cold MS-1?" remains open)
**Design by:** Task 3 (prep) · **Control (pending):** Sprint-34 Day 1
**Date:** 2026-07-18

**Findings:**
- The reconciliation hypothesis **H_dual** is stated: anchor the head-placed precedence dual's *complementarity* to the head-side variable `x(l+1,i,j)` (a structural pairing change), not merely re-label the multiplier (the refuted H1).
- **Key correction to the S33 gate:** because keying is value-invariant (Unknown 1.1), the warm residual `N` is the **wrong diagnostic** — no keying/pairing change moves the warm-point term VALUES. The gate is reframed to the **cold** MCP reaching **MS-1 @ 17500** (`modelstat` asserted), which the structural pairing change *can* affect. This is why S33's `N→0` gate could not be passed.
- Fix surface (a Day-0-re-confirm hypothesis, PR24): `head_domain_offsets` IR carrier (`src/ir/parser.py`) + `_try_build_param_offset_crossterm` (`src/kkt/stationarity.py:5712`) + the `_emit_nlp_presolve` transfer (`src/emit/emit_gams.py`).

**Evidence:** `MINE_DUAL_SUBSYSTEM_DESIGN.md` §4–§5.

**Decision:** PROCEED spec = the `/tmp` H_dual prototype drives the **cold** MCP to MS-1 @ 17500 (interior unperturbed, srpchase no-regression, `--resolve-changed` GO); else REPLAN (H3′). Executed on Sprint-34 Day 1 (not in this docs-only prep).

**Task-8 gate-feasibility note (2026-07-19):** the P1 Phase-0 gate is authored with a clean PROCEED (cold MCP MS-1 @ 17500, `modelstat` asserted, `x.up=inf` BANNED, `/tmp` scratch copy run from the repo root) / REPLAN (H3′) decision — `PHASE_0_ACCEPTANCE_GATES.md` §1 P1. The keying-invariance reframe (cold-MS-1, not warm `N→0`) is encoded at the gate layer.

---

## Unknown 1.3: Is the 22-row breadth (not the banked 6) fully characterized, and does closing all 22 reach MS-1?

### Priority
**High** — If the breadth is wider than the reconciliation design accounts for, the fix is incomplete (partial residual → MS-5 persists)

### Assumption
The wrong-sign residual is exactly the 22 `c`-boundary rows characterized in `SPRINT_33/DAY2_MINE_REPLAN.md` (broader than the banked 6 from Sprint 32), and closing all 22 (not merely the max row) is both necessary and sufficient to reach MS-1 @ 17500.

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
✅ **Status:** VERIFIED
**Verified by:** Task 3
**Date:** 2026-07-18

**Findings:**
- The residual is exactly the pit's top edge — the **`c`-boundary** (`ord(l)+ord(i)=card` or `ord(l)+ord(j)=card`, `card(l)=4`) plus the **`d\c` ring** (`=card+1`, where `x` is a real variable in `d` but no precedence constraint originates). Interior rows have `N=0`.
- The full nonzero set is **22 rows** (the S33 Day-2 control count), materially broader than the banked "6 bound-active rows."
- Closing all 22 in the **cold** solution = MS-1 @ 17500 is the sufficiency gate (a partial close leaves MS-5).

**Evidence:** `MINE_DUAL_SUBSYSTEM_DESIGN.md` §3.1 (boundary strata) + §3.2 (max-row decomposition); `SPRINT_33/MINE_CROSSTERM_DESIGN.md` §2.

**Decision:** the 22-row breadth + boundary classification is confirmed; H_dual must close all 22 (cold), not just the max row.

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
✅ **Status:** VERIFIED
**Verified by:** Task 3
**Date:** 2026-07-18

**Findings:**
- `EquationDef.head_domain_offsets` **exists** in the IR (`src/ir/parser.py`, defined line ~1019, populated ~3958) — the S31 foundation that describes, per domain position, the head offset (`l+1`) distinguishing the head label from the body label.
- It is **already consumed in the emit/KKT layer** (`src/emit/emit_gams.py::head_offset_marginal_index_map`; `src/kkt/complementarity.py`; `src/kkt/sqr_reformulation.py`) but is **NOT referenced anywhere in `src/kkt/stationarity.py`** (live `grep` → 0 hits): mine's cross-term flows through `_try_build_param_offset_crossterm` (the #1224 param-offset path), which re-inverts the body-keyed offset instead of consuming the head-offset IR.
- H_dual needs a **head-label-indexed multiplier**; `head_domain_offsets` is its natural carrier, and H_dual would be its **first consumer in the stationarity cross-term path** (`src/kkt/stationarity.py`) — so the new work is **wiring the existing IR into `_try_build_param_offset_crossterm`** (not an IR capability from scratch, but new stationarity-emit plumbing). This is a scope factor for the 1.5 sizing.

**Evidence:** `MINE_DUAL_SUBSYSTEM_DESIGN.md` §1 (live grep) + §4.2 (fix surface).

**Decision:** the IR foundation exists but is unused by this path; the H_dual fix must wire `head_domain_offsets` into `_try_build_param_offset_crossterm` + `_emit_nlp_presolve` (new plumbing).

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
✅ **Status:** VERIFIED
**Verified by:** Task 3
**Date:** 2026-07-18

**Findings:**
- **18–24 h, upper half (~22–24 h)**: `/tmp` re-decomposition + H_dual structural prototype + the cold-MS-1 gate (~5–7 h); head-anchored complementarity + cross-term emit + `head_domain_offsets` plumbing (~10–14 h); determinism ×3 + golden-staleness + `--resolve-changed` + the `shape12` fixture (~3–4 h).
- Front-loaded **Days 1–5** so the PROCEED/REPLAN decision lands by the **Day-5 checkpoint** — P1 is the sprint's **highest-REPLAN-prior** track (banked premise twice-refuted). An early REPLAN frees ~14–18 h → P6/P7 (exactly as S33 realized on Day 2).
- The H3′ REPLAN exit is pinned (if the cold MCP cannot reach MS-1 without perturbing interior rows or regressing srpchase).

**Evidence:** `MINE_DUAL_SUBSYSTEM_DESIGN.md` §6.

**Decision:** 18–24 h (upper ~22–24 h) is realistic; front-load Days 1–5; H3′ REPLAN exit pinned. (Task 9 will assess the P1 REPLAN probability.)

**Task-9 REPLAN-probability contribution (2026-07-19):** P1's prior is **High — higher than Sprint 33 carried.** The banked premise is now **twice-refuted** (S32 `N`-derivation + S33 H1 value-invariance), and mine enters on a **third** hypothesis (H_dual) against a **reframed cold-MS-1 gate** that is a harder bar than a warm-residual check on a degenerate LP (`x.m=0` at the boundary). ~14–18h at risk → P6/P7 on H3′ REPLAN. `REPLAN_RISK_ASSESSMENT.md` Track P1.

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
✅ **Status:** VERIFIED
**Verified by:** Task 4
**Date:** 2026-07-19

**Findings:**
- Eliminating the 369,024-column materialization requires **all three sites atomically**: S1 `acost3` body-differentiation (`constraint_jacobian.py`, `compute_constraint_jacobian` `:679`), S2 variable-column enumeration (`index_mapping.py` `enumerate_variable_instances`, def `:327`/call `:634`), S3 variable stationarity (`stationarity.py`). Fixing only the constraint gate is insufficient — the live blow-up persists (bounded probe: > 116 s still in `compute_constraint_jacobian` at `constraint_jacobian.py:1247`, `enumerate_equation_instances` for `tbal`).
- No safe partial: the short-circuited constraints enumerate zero Jacobian entries, so every `stat_*` cross-term must come from the parametric path (Unknown 2.2).

**Evidence:** `SARF_EMIT_MODE_DESIGN.md` §1–§3; live grep (2-D gate 0 matches, 1-D base gate `index_mapping.py:402`); the bounded translate probe.

**Decision:** the three-site atomic elimination is confirmed as the required shape; S1 parametric ∂, S2 guarded-symbolic, S3 one symbolic `stat_task`.

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
✅ **Status:** VERIFIED (architecture verdict; the executed O(active) translate gate is the Sprint-34 in-sprint gate)
**Verified by:** Task 4
**Date:** 2026-07-19

**Findings:**
- **Architecture (verified now):** the parametric emit avoids materializing `task`'s columns at all three sites — S1 differentiates the `acost3` body once (→ `+oc(g,m,n)*nu_acost3`), S2 fixes the vacuous columns + treats `task` as a guarded symbol, S3 emits one guarded `stat_task(g,t,m,n)$taskposs(g,t)`. `taskposs` is runtime-computed (`sarf.gms:371`), so no static enumeration is attempted; GAMS resolves the 398 live rows at solve.
- **Empirical (deferred to the in-sprint gate):** whether the parametric emit **translates in seconds** (no hidden 4th enumeration site re-triggering the timeout) is the O(active) translate-budget gate — run **in-sprint** (Task 8 Phase-0 / Days 1–7) before the golden ships, **not** in this docs-only prep. srpchase (~2.9 s) is the reference; the current failure is > 116 s.

**Evidence:** `SARF_EMIT_MODE_DESIGN.md` §3, §5 (the O(active) gate); the live bounded blow-up probe.

**Decision:** the architecture is sound; the timeout-re-trigger risk is the primary REPLAN exit, gated on the in-sprint translate-time measurement.

**Task-8 gate-feasibility note (2026-07-19):** the P2 Phase-0 gate is authored with a clean PROCEED (translate seconds not >116s, one symbolic `stat_task$taskposs` + `task.fx`, no set-name literals, atomic, byte-stable, det ×3, `--resolve-changed` GO) / REPLAN (timeout re-trigger) decision — `PHASE_0_ACCEPTANCE_GATES.md` §1 P2. The O(active=398) translate-budget probe is the load-bearing gate item.

**Task-9 REPLAN-probability contribution (2026-07-19):** P2's prior is **Medium-High** — a failed-architecture rebuild (the 4×-failed Sprint-26 path); the "necessary but insufficient" finding proved the blow-up hides at multiple sites, so "eliminate it everywhere" carries genuine miss-a-site risk. The V1 O(active) timing probe resolves the dominant risk **Day-0**, capping the prior below High. +Translate is the lowest-leverage KPI; ~9–20h → P6/P7 on REPLAN. `REPLAN_RISK_ASSESSMENT.md` Track P2.

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
✅ **Status:** VERIFIED
**Verified by:** Task 4
**Date:** 2026-07-19

**Findings:**
- The 7-term `stat_task` is complete and re-verified **term-for-term against the live sarf bodies**: [1]+[2] tbal (`:427` + the `tadj`/harvest-c adjustment `:375`/`:379`), [3] labor `lam_labor(t)` (`labor(t)..` body), [4] equipb1$equipposs (`:443`), [5] equipb2$equipposs (`:446`), [6] acost3 `nu_acost3` (`:454`, S1), [7] `task.lo` `−piL_task` (`:402`).
- **No set-name-literal multiplier indices** — every multiplier is over the stat domain (`nu_tbal(g,t)`, `lam_equipb1(m,t)`, `nu_acost3`, …). The compile-clean anti-pattern grep (`grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` → nothing) is the in-sprint structural guard against the reverted Sprint-26 `243fe578` `nu_slack("srn")` anti-pattern.

**Evidence:** `SARF_EMIT_MODE_DESIGN.md` §4 (the term-by-term table against the live source).

**Decision:** the derivation is complete + literal-free; the anti-pattern grep is a Phase-0 gate item.

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
✅ **Status:** VERIFIED (design reasoning; the emitted-MCP squareness is confirmed in-sprint by the golden)
**Verified by:** Task 4
**Date:** 2026-07-19

**Findings:**
- The **398 live rows come from the combination**, not the head guard alone: `$taskposs(g,t)` alone still expands across all `(m,n)` per active `(g,t)` (~124K rows); `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0` fixes the 368,626 vacuous columns, and under MCP matching the fixed columns — and their paired `stat_task` rows — drop, leaving the **398** `taskposs ∧ tech` rows.
- The `$(not active)` guard exactly complements the `$taskposs∧$tech`-active 398 (the mine non-`d` precedent); PATH accepts the fixing.
- The actual MCP squareness (no unmatched var/eqn) is confirmed in-sprint against the emitted golden (part of the O(active) gate).

**Evidence:** `SARF_EMIT_MODE_DESIGN.md` §3 + §4 (Unknown 2.4 row); the banked GAMS data probe (taskposs 129, active 398).

**Decision:** the 398 = head guard + `task.fx` + MCP matching (not the head alone); the emit is square by construction.

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
✅ **Status:** VERIFIED (gate specified; the determinism ×3 + `--resolve-changed` runs are the in-sprint gate)
**Verified by:** Task 4
**Date:** 2026-07-19

**Findings:**
- **Gate specified (now):** the O(active) budget gate (§5) enforces byte-stability + determinism ×3 `PYTHONHASHSEED` + `--resolve-changed --since-commit 750803b2` GO (sarf the only changed golden) + the anti-pattern grep. The track is sized **20–28 h** with the timeout-re-trigger REPLAN exit.
- **Empirical (deferred):** the determinism ×3 run + the `--resolve-changed` GO execute **in-sprint** against the emitted golden (which does not exist in this docs-only prep) — a Task-8 Phase-0 / in-sprint gate.

**Evidence:** `SARF_EMIT_MODE_DESIGN.md` §5 (the O(active) budget gate) + §6 (sizing + REPLAN exit).

**Decision:** the byte-stability/determinism gate is specified as a Phase-0 acceptance item; the executed runs are in-sprint (Task 8 authors the gate).

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
✅ **Status:** VERIFIED (Task 2 Day-0-bucket + Task 5 primary — the constraint-index-diagonal correction)
**Verified by:** Task 2 (Day-0 bucket) + Task 5 (primary: the constraint-index-diagonal `sameas` correction)
**Date:** 2026-07-19 (Task 5 primary; Task 2 Day-0-bucket 2026-07-18)

**Findings (Task 2 — Day-0 bucket):**
- At Day 0, fawley is `model_infeasible` (MS 5; LP opt 2899.25), a `verified_convex` candidate — the P3 bucket the constraint-index-diagonal `sameas` correction targets. Confirmed from the committed DB. (fawley's +Solve is **H-b** per the S33 control, so there is **no in-sprint bucket**: the correction ships for correctness, and the +1 genuine floor is **contingent on the P5 forcing solve**, not an in-sprint P3 gain — see Task 5 / Unknown 3.3.)

**Evidence:** `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` §3 (model_infeasible members) + §5 (fawley provenance MS 5) + §4 (the ≥ 76 conversion map, fawley H-b note).

**Decision:** the Day-0 fawley bucket is confirmed; the `sameas`-correction / no-regression / H-b / floor-credit aspects are the primary work of Task 5 (fawley correction + forcing design).

**Task-5 (primary) — ✅ VERIFIED (2026-07-19):** the qsb/pbal `sameas` gap is a **constraint-index diagonal** (the summed constraint index `cfq` = `bq`'s 2nd index = the stat index `cf`), distinct from mbal's variable-index diagonal (the Day-5 refinement). Fix surface = the general `sameas`-guard path (`_build_sameas_guard` `src/kkt/stationarity.py:4623` / `_get_or_create_fresh_alias` `src/kkt/stationarity.py:4496` in `_add_indexed_jacobian_terms` `src/kkt/stationarity.py:5861`, ~1430 lines), **not** the 1-D core `_var_at_two_indices_complement` (`src/kkt/stationarity.py:7291`; never fires for 2-D `bq`). The correction gives `max|stat_bq|` **473 → 18.468** (control-proven); reaching **→ 0** also needs the P4 bound-transfer fix on the cc-dist cell. No-regression is structurally favorable (mbal + the 1-D core are different paths). Live fingerprint re-confirmed (CASE_B `stat_bq(res-arab-l,fuel-oil)` 0.973 raw 473, dual CONSISTENT). Evidence: `FAWLEY_CORRECTION_FORCING_DESIGN.md` §2/§4; `data/gamslib/mcp/fawley_mcp.gms:238`.

**Task-8 gate-feasibility note (2026-07-19):** the P3 Phase-0 gate is authored with a clean PROCEED (the constraint-index-diagonal correction 473→18.468, no mbal / 1-D-core move, `--resolve-changed` GO) / REPLAN (gate-leak) decision — `PHASE_0_ACCEPTANCE_GATES.md` §1 P3. **H-b is confirmed** at the gate layer: the +Solve is a P5 forcing hand-off, the correction ships for correctness, and the +1 genuine floor is contingent on forcing (`max|stat_bq|→0` also needs P4).

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
✅ **Status:** VERIFIED (H-b confirmed by the Sprint-33 Day-4 control)
**Verified by:** Task 5
**Date:** 2026-07-19

**Findings:**
- **H-b confirmed** (Day-4, `modelstat` asserted): sameas + all bound-transfer signs → warm `max|stat_bq| ~0`, but the MCP still solves **MS-5 @ 4399.557** (LP opt 2899.25), and the objective is **identical** with/without the bound-transfer fix. The divergence is **non-emit** — an LP-convergence/structural issue at fawley's scale (a large degenerate blending LP), separable from the `stat_bq` emit.
- Therefore fawley's +Solve is **not** an emit fix → it hands to the **P5 `--force` survey** (homotopy/multistart/optfile) + the PATH consultation.

**Evidence:** `SPRINT_33/DAY4_FAWLEY_CONTROL.md` §4 (the H-a/H-b table) + `FAWLEY_CORRECTION_FORCING_DESIGN.md` §3.

**Decision:** the +Solve is a P5 forcing hand-off (H-b); the emit correction ships for correctness only (moves no in-sprint bucket).

**Task-9 REPLAN-probability contribution (2026-07-19):** P3's **correctness-REPLAN prior is Medium** (the no-regression is structurally favorable — polygon/ps2 use the different 1-D core; the only real risk is perturbing the same-path mbal). But **the +Solve is a P5 forcing hand-off (H-b confirmed), a priori unpromising — not an in-sprint mover**, and the genuine-floor +1 is **contingent on forcing** (fawley doesn't cold-match unaided). So P3 lands a firm correctness fix but its bucket contribution is effectively deferred to forcing. `REPLAN_RISK_ASSESSMENT.md` Track P3.

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
✅ **Status:** VERIFIED (floor-credit determined: NO in-sprint gain under H-b)
**Verified by:** Task 5
**Date:** 2026-07-19

**Findings:**
- The correction **changes the cold emit** (adds the constraint-index-diagonal `sameas` to qsb/pbal) → a **genuine** cross-term fix (not methodology, per the PR25 definition).
- **But under H-b fawley does not cold-match** (the cold MCP stays MS-5 without a forcing lever), and the PR25 genuine floor credits a **matched** model — so there is **no in-sprint genuine-floor gain**. The +1 genuine floor is **contingent on forcing landing the solve** (P5).
- This corrects the Day-5-prompt premise that the H-b branch yields "+genuine floor" — it does **not** for fawley, because it doesn't cold-match (`SPRINT_33/DAY5_FAWLEY_CLOSE.md` §1).

**Evidence:** `FAWLEY_CORRECTION_FORCING_DESIGN.md` §4.D; the PR25 partition (`SPRINT_34/BASELINE_METRICS.md` §4).

**Decision:** the correction ships for correctness; the +1 genuine floor is contingent on the P5 forcing solve (not an in-sprint P3 gain).

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
✅ **Status:** VERIFIED
**Verified by:** Task 5
**Date:** 2026-07-19

**Findings:**
- The fawley 2-D second-index property fixture follows the S33 `tests/integration/emit/test_sample_pruned_var_l_init.py` pattern (raw-file emit + skip-if-absent): it asserts the `$(sameas(cfq__,cf))` guard is present on the **qsb/pbal** terms of the emitted `stat_bq` (absent before the correction → fails; present after → passes).
- It lands **only once** the P3 correction lands (correctly deferred if P3 REPLANs — the S33 precedent for shape12/shape13/fawley).
- Sized within the 12–18 h track (~3–4 h for no-regression + determinism ×3 + the fixture).

**Evidence:** `FAWLEY_CORRECTION_FORCING_DESIGN.md` §6; the S33 `test_sample_pruned_var_l_init.py` pattern.

**Decision:** the fixture is scoped (fail-before/pass-after, gated on the correction landing); the track is sized 12–18 h with the gate-leak REPLAN exit.

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
✅ **Status:** VERIFIED
**Verified by:** Task 6
**Date:** 2026-07-19

**Findings:**
- The bound multiplier at an active bound is `|reduced cost|`, so `= abs(var.m)` is correct for **both** senses; the current sign gates (`var.m > 0` for `piL`, `var.m < 0` for `piU`) encode the MINIMIZE convention and skip the correctly-signed multiplier for MAXIMIZE (fawley `bq.m = -18.468`, Day-4 proven → `= abs(bq.m)` closes the residual; mine's symmetric 3 upper-bound `x.m > 0` rows).
- The **position** gate (`abs(var.l - var.bound) < 1e-6`) confines the transfer to active bounds — **no over-transfer** at interior/inactive bounds (`abs(var.m) ≈ 0` there anyway), and MINIMIZE is value-identical (`abs(var.m) = var.m` when `var.m ≥ 0`).
- Two implementation options: **A** universal `abs` (all ~44 presolve goldens byte-change; MINIMIZE value-identical) vs **B** sense-aware (`ObjSense.MAX`-conditioned; MINIMIZE byte-identical, only MAXIMIZE goldens change) — **Option B recommended** (surgical, minimal churn).

**Evidence:** `BOUND_TRANSFER_SIGN_DESIGN.md` §1–§2; `SPRINT_33/DAY4_FAWLEY_CONTROL.md` §3; the live gate lines `src/emit/emit_gams.py:1590`/`:1603`.

**Decision:** the sign-robust transfer is correct + no over-transfer; recommend the sense-aware Option B to minimize blast radius.

**Task-8 gate-feasibility note (2026-07-19):** the P4 Phase-0 gate is authored with a clean PROCEED (sign-robust `= abs(var.m)` closes the fawley cc-dist + mine 3-row cells, active-bound gating, `--resolve-changed` GO over the MAXIMIZE presolve cohort) / documented-general-correctness-finding (no candidate warm-residual-driven → no +Solve) / re-scope (over-transfer) decision — `PHASE_0_ACCEPTANCE_GATES.md` §1 P4. The +Solve survey (primarily agreste) is the contingent lever.

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
✅ **Status:** VERIFIED (design-level; the per-candidate +Solve survey is the in-sprint gate)
**Verified by:** Task 6
**Date:** 2026-07-19

**Findings:**
- The MAXIMIZE `model_infeasible` cohort (the +Solve targets) = **{fawley, mine, camcge, rocket, agreste}** (from the committed DB + `solve … maximizing` scan; ~85 MAXIMIZE candidates total).
- **Four are already attributed to other tracks:** fawley **H-b** (Task 5, structural), mine **P1** (head-offset dual; `x.m=0` at the `c`-boundary — nothing to transfer; P4 closes only the 3 upper-bound `x.m>0` warm-residual rows, not the solve), camcge **Epic-5** (Walras rank-deficiency), rocket **Case-c** (non-convex). So the realistic +Solve target reduces to **agreste** — the one open candidate, but **P6-entangled** (its CASE_B may be a double-`solve` scenario-driver artifact).
- **Honest finding:** the +Solve is **contingent and a-priori uncertain**; P4's firm value is the **general warm-start-correctness fix** (it closes the harness CASE_B warm residual for the MAXIMIZE cohort). The per-candidate solve (warm-residual-driven vs structural) is the **in-sprint** survey.

**Evidence:** `BOUND_TRANSFER_SIGN_DESIGN.md` §3.1 (the attribution table) + §3.2 (the survey).

**Decision:** front-load the survey (Days 1–5); the REPLAN/documented-finding exit is a general-correctness fix with no +Solve if no candidate is warm-residual-driven.

**Task-9 REPLAN-probability contribution (2026-07-19):** P4's **correctness prior is Low** (the sign-robust fix lands regardless), but **the +Solve miss is Medium-High** — "the freshest, least-refuted lever" is not "most-likely-to-move-a-bucket": the MAXIMIZE `model_infeasible` cohort is otherwise-attributed (fawley H-b, mine P1, camcge Epic-5, rocket Case-c), so the realistic +Solve target is **agreste alone (P6-entangled)**. The a-priori outcome is a general-correctness fix with **no +Solve** (the documented finding *is* the deliverable). `REPLAN_RISK_ASSESSMENT.md` Track P4.

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
✅ **Status:** VERIFIED (gate specified; the `--resolve-changed` run is the in-sprint gate)
**Verified by:** Task 6
**Date:** 2026-07-19

**Findings:**
- The sign-robust change byte-alters the transfer line; under **Option B** (sense-aware) only the **MAXIMIZE** goldens change (the MINIMIZE cohort stays byte-identical), confining the re-solve/regression surface to the MAXIMIZE cohort.
- The regression-risk set = the ~20 MAXIMIZE **presolve-match** models (camshape, cclinpts, cpack, etamac, harker, himmel16, irscge, like, lrgcge, marco, moncge, paperco, polygon, robert, stdcge, tforss, weapons, worst, ps10_s_mn, ps5_s_mn) — their warm-start changes, so they must not regress.
- **No-regression gate:** `--resolve-changed --since-commit 750803b2` **GO** (every changed golden re-solves to the same bucket). The executed run is **in-sprint**.

**Evidence:** `BOUND_TRANSFER_SIGN_DESIGN.md` §3.3 + §2 (Option B); the committed DB (MAXIMIZE presolve-match enumeration).

**Decision:** Option B confines the blast radius to the MAXIMIZE cohort; the `--resolve-changed` GO over the presolve-match set is the in-sprint no-regression gate.

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
✅ **Status:** VERIFIED
**Verified by:** Task 6
**Date:** 2026-07-19

**Findings:**
- The min-convention gate is localized (live) to `src/emit/emit_gams.py:1590` (`piL`: `…$(abs(var.l - var.lo) < 1e-6 and var.m > 0) = var.m`) + `:1603` (`piU`: `…$(abs(var.l - var.up) < 1e-6 and var.m < 0) = -(var.m)`), both inside `_emit_nlp_presolve` — the **sole** fix surface.
- The **inequality**-multiplier warm-start transfer already uses `abs()` (`src/emit/emit_gams.py:1574`), so it is unaffected; the objective sense for Option B is available via `model_ir.objective.sense == ObjSense.MAX` (the `ObjSense` enum `src/ir/symbols.py:42`, parsed at `src/ir/parser.py:4104`; existing branch precedent at `src/ad/gradient.py:300` — `if sense == ObjSense.MAX:`).

**Evidence:** `BOUND_TRANSFER_SIGN_DESIGN.md` §1–§2; live grep of `src/emit/emit_gams.py`.

**Decision:** the two gate lines are the sole fix surface; the objective sense is available for the sense-aware Option B.

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
Prototype the dual-consistent redefinition in a `/tmp` emit; assert `modelstat`; check MS-1 + omega 191.7346 + the dual side. Cross-check `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` + `EPIC_5/CGE_DEGENERACY_SCOPING.md`.

### Risk if Wrong
- **Still MS-4:** camcge stays Epic-5-deferred (expected — 3+ sprints of MS-4 variants); the design is the Epic-5-ready recipe, not an in-sprint fix.

### Estimated Research Time
1.5 hours (`/tmp` prototype + dual-side check)

### Owner
Development team (KKT/CGE specialist)

### Verification Results
✅ **Status:** VERIFIED (design-level; MS-1 is the Epic-5 gate, not an in-sprint result)
**Verified by:** Task 7
**Date:** 2026-07-19

**Findings:**
- camcge is `model_infeasible` **MS-4** (live DB) — the Walras rank-deficiency (a redundant market-clearing row given budget balance → a 1-D KKT-Jacobian nullspace, MS-4 even at the correct primal). Step 1 (`nu_mps_fx`) landed S32; the MS-4 is independent of `stat_mps`.
- The full dual-consistent redefinition is designed: **keep every market-clearing row** (no orphaned dual) + the **consumption-weighted numéraire** (removes the price nullspace → omega 191.7346, banked) + **redefine the redundant market's dual via Walras' law** (full-rank while the multiplier stays available) — with the **dual side checked** (the Day-11 lesson).
- Whether it reaches **MS-1 at 191.7346** is **unproven**: the banked price-pin variant stayed MS-4 (INFES on gdp/depreq/hhsaveq/gruse); the `/tmp`-to-MS-1 prototype is the **Epic-5** gate (not runnable in this docs-only prep). **Epic-5-deferred** — camcge stays `model_infeasible` in Sprint 34.

**Evidence:** `CAMCGE_ROCKET_PLAN.md` §2/§4; `SPRINT_33/CAMCGE_WALRAS_DESIGN.md`; `EPIC_5/CGE_DEGENERACY_SCOPING.md`; the live DB (camcge MS-4).

**Decision:** Epic-5-deferred; the design (recipe + dual-side check) is the Epic-5 deliverable; MS-1 is the Epic-5 `/tmp` gate.

**Task-8 gate-feasibility note (2026-07-19):** the P5-camcge Phase-0 gate is authored with the `/tmp` full dual-consistent redefinition → MS-1 @ 191.7346 (dual side checked) + the S1∧S2∧S3 detector (flags only camcge) as the PROCEED precondition, and the **Epic-5-deferral as the expected REPLAN exit** (the banked price-pin variant stayed MS-4) — `PHASE_0_ACCEPTANCE_GATES.md` §1 P5. rocket's residual-clean-before-forcing + the sign-flip BAN are encoded at the gate layer.

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
✅ **Status:** VERIFIED
**Verified by:** Task 7
**Date:** 2026-07-19

**Findings:**
- The S1∧S2∧S3 degeneracy detector flags **only camcge** (no false-flag on the siblings): S1 = market-clearing block linearly dependent via budget balance; S2 = no price numéraire fixed; **S3 (the false-positive guard) = the cold MCP is singular at iteration 0 (MS-4)**.
- Live DB confirms the cohort: camcge **MS-4** (fires); irscge/lrgcge/moncge/stdcge **MS-1** (pass-through — a determined closure → nonsingular Jacobian → fails S3). The pass-through default is the **identity transform** (faithful KKT emission).

**Evidence:** `CAMCGE_ROCKET_PLAN.md` §3; the live DB (camcge MS-4 vs the four siblings MS-1); the banked Sprint-31 Day-7 cold-MCP test.

**Decision:** the detector is correctly scoped (flags only camcge); the redefinition applies to the flagged model only — no false-flag on the four solving CGE siblings.

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
✅ **Status:** VERIFIED
**Verified by:** Task 7
**Date:** 2026-07-19

**Findings:**
- The rocket PATH-consultation input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, FINALIZED S32) is submission-ready: the concrete question + the ruled-out-lever survey (PATH options / μ-continuation / multistart / division-by-variable, all MS-5) + the two-command reproducer + the `--force` scaffold. rocket is `model_infeasible` MS-5 (live DB), a Case-c **forcing** problem (boundary rows move with the warm-start; dual-transfer CONSISTENT), not an emit bug.
- **Sprint-35 hand-off:** Sprint 34 submits the self-contained brief; **Sprint 35** ("PATH Author Consultation & Solution Forcing", renumbered from the pre-insertion Sprint 34) conducts the author consultation (Ferris/Dirkse). +1 Solve is conditional on the consultation (the `--force` survey is exhausted).
- **The Case-c objective-gradient sign flip stays BANNED** (control-refuted 4×: hhfair 72.147 → 22.144 worse; the CGE-cluster `nu_objective` reduction inert since `nu_obj=±1`). No re-litigation.

**Evidence:** `CAMCGE_ROCKET_PLAN.md` §5; `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md`; `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`; the live DB (rocket MS-5).

**Decision:** the rocket input is complete + submission-ready for the Sprint-35 consultation; the sign-flip BAN is re-affirmed.

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
Emit + compile ganges + gangesx (`data/gamslib/raw/`, skip-if-absent); capture the `$141/$145/$149` lines; confirm the shared vs distinct root; confirm the referenced vars are declared. Cross-check `SPRINT_33/SPRINT_34_CARRYFORWARDS.md` (banked P6).

### Risk if Wrong
- **Two distinct roots:** a single fix recovers only one (+1 not +2); the "shared root" hypothesis was only partially right (the Sprint-33 lesson).

### Estimated Research Time
1.5 hours (emit + compile both + error-line diagnosis)

### Owner
Development team (emit specialist)

### Verification Results
✅ **Status:** VERIFIED (live-diagnosed)
**Verified by:** Task 10
**Date:** 2026-07-19

**Findings:**
- Compiled the committed goldens (`data/gamslib/mcp/{ganges,gangesx}_mcp.gms`) from the repo root: **both have the identical error profile `$141` ×15 / `$145` ×3 / `$149` ×9** → a **single shared root**.
- The root: the NaN-sanitization emit pass emits `param(i)$(NOT (param(i) > -inf and param(i) < inf)) = 0;` — a self-referential guard that *reads* `param(i)` — over parameters (`adst`, `aex`, `aid`, `an`, `as`, `az`, `cg`, `deltan`, …) whose source value-assignment is `= dst.l(i)/sum(j, dst.l(j))` (depends on a **variable level**, pruned/mis-ordered in the MCP) → `$141` "Symbol declared but no values assigned" (+ `$145` "Set identifier expected" / `$149` "Uncontrolled set as constant" on the same construct).
- **A single fix may recover both.** **Distinct from sample's `$140`** (pruned-var `.l`-init) — the S33 P6 fix (skip an `.l`-init whose refs aren't a subset of the declared MCP vars) is a **no-op** here (ganges/gangesx's root is *parameter* sanitization, and their `.l`-init refs are declared).
- **NB — the Assumption's `bound-clamp x$(not(...))=0` hypothesis was refined, not confirmed:** the root is the same guard *shape* (`sym$(NOT(...))=0`) but on a **parameter** (`param(i)$(NOT(...))=0`), **not** a variable bound-clamp — the parameter's value-assignment depends on a variable level (`dst.l`), so it is declared-but-unassigned in the MCP context. The "parameter-assignment lines" half of the Assumption was on the right track; the "variable bound-clamp" half was not the root.

**Evidence:** `TOOLING_AND_BACKLOG_ANALYSIS.md` §2 (the live compile diagnosis); the GAMS listing (`$141` = declared-but-unassigned on `adst(i)$(NOT(...))=0`).

**Decision:** the fix surface is the NaN-sanitization pass (`src/emit/emit_gams.py`, a hypothesis) — skip params whose value depends on a variable level, or emit the assignment before the guard; `--resolve-changed`-gated; a single fix recovers the ganges/gangesx pair.

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
Inspect agreste's source (the two `solve` statements); run the harness with single-solve scoping; determine whether the factor-of-2 is genuine or a driver artifact. Cross-check `SPRINT_33/SPRINT_34_CARRYFORWARDS.md`.

### Risk if Wrong
- **Driver artifact:** agreste is a false CASE_B → chasing it wastes budget (the right call is to document + defer).

### Estimated Research Time
1 hour (source inspection + single-solve harness scope)

### Owner
Development team (KKT/emit specialist)

### Verification Results
✅ **Status:** VERIFIED (live-confirmed)
**Verified by:** Task 10
**Date:** 2026-07-19

**Findings:**
- agreste is `model_infeasible` MS-5 with a banked CASE_B `stat_sales` rel 2.0. **Confirmed live: two `solve agreste maximizing yfarm using lp;` statements (`data/gamslib/raw/agreste.gms:294` + `:298`)** — a single-model-solved-twice **scenario driver**.
- So the factor-of-2 in `stat_sales` is likely a **driver-doubling artifact** (the harness's single-solve scoping conflating the two solves), **not** a genuine dropped-gradient emit bug.

**Evidence:** `TOOLING_AND_BACKLOG_ANALYSIS.md` §2; `data/gamslib/raw/agreste.gms:294`/`:298`.

**Decision:** **scope-verify the single-solve harness scoping BEFORE treating the CASE_B `stat_sales` as an emit bug** — the right call may be to document + defer (a false CASE_B, not a P6 recovery target).

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
✅ **Status:** VERIFIED
**Verified by:** Task 10
**Date:** 2026-07-19

**Findings:**
- The `path_syntax_error` cohort is **multi-root** — sample (`$140`, pruned-var `.l`-init, recovered S33) ≠ ganges/gangesx (`$141/$145/$149`, parameter-sanitization). Two distinct roots already confirmed.
- The S33 lesson holds: **verify per-model; do not assume a single shared root** (the earlier "one fix recovers the cohort" was only partially right — one fix recovers the ganges/gangesx *pair*, but not sample's distinct `$140`). The residual cohort (clearlak/dinam/indus/turkey/turkpow) each needs its own compile-diagnosis before treatment.

**Evidence:** `TOOLING_AND_BACKLOG_ANALYSIS.md` §2 (the sample-vs-ganges/gangesx root split).

**Decision:** the per-model-verify discipline is confirmed; P6 treats each model on its own compile-diagnosis (ganges/gangesx as a pair; the rest individually).

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
✅ **Status:** VERIFIED
**Verified by:** Task 10
**Date:** 2026-07-19

**Findings:**
- The AD cross-term property catalog is at **shapes 1–11** (`tests/integration/emit/test_ad_crossterm_shapes.py`); shape12/shape13/fawley are **not yet added** (correctly deferred, the S33 precedent).
- The three fixtures follow the S33 `test_sample_pruned_var_l_init.py` pattern (raw-file emit + skip-if-absent), each fail-before/pass-after, landing **only once** its track lands: shape12 (P1 head-offset dual — the head-anchored reconciliation), shape13 (P2 sarf — one guarded `stat_task$taskposs`, no set-name literals), fawley 2-D second-index (P3 — the `$(sameas(cfq__,cf))` on qsb/pbal). A P4 MAXIMIZE bound-transfer fixture is added if P4's correctness fix lands. Each is correctly deferred if its track REPLANs.

**Evidence:** `TOOLING_AND_BACKLOG_ANALYSIS.md` §3; the catalog (shapes 1–11 present); the S33 fixture pattern.

**Decision:** the fixtures are scoped (fail-before/pass-after, each gated on **its own** track's landing — shape12→P1, shape13→P2, fawley→P3 — deferred on that track's REPLAN).

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
✅ **Status:** VERIFIED
**Verified by:** Task 2
**Date:** 2026-07-18

**Findings:**
- The Day-0 baseline = the Sprint 33 close, recomputed from the committed DB: Parse 142 / Translate 135 / Solve 108 (64 cold + 44 presolve) / Match 93 / model_infeasible 7 / path_syntax_error 7 / all-219 Match 96.
- The PR25 genuine-floor anchor is **75** (not the S33 Day-0 74) — the S33 P6 sample fix added +1 genuine (a cold-emit correction). Partition: genuine floor 75 / methodology 21 / all-219 Match 96, corroborated by the cold/presolve split (63 cold + 33 presolve; 63 + 12 genuine-presolve = 75, 21 methodology).
- The Day-0 **code anchor** is the S33-close SHA **`750803b2`** (Merge #1581). `4cbf8bff` (S31 close) is **superseded** — the DB's last modifying commit is `1568a531` (S33 Day-11 sample), so the DB is no longer byte-unchanged since `4cbf8bff`. No `src/`/`scripts/` drift since `750803b2`.

**Evidence:** `docs/planning/EPIC_4/SPRINT_34/BASELINE_METRICS.md` §1–§4; `git diff --quiet 750803b2..HEAD -- src/ scripts/` clean; `run_full_test.py --resolve-changed --since-commit 750803b2 --dry-run` → GO (0 changed); DB md5 `6166acab90dcaff8789255f8ada83c54`; determinism ✅ ×3 `{0,1,42}` (mine/fawley/sample byte-identical).

**Decision:** Sprint-34 Day-0 baseline pinned; the ≥ 76 conversion map (mine [P1] / fawley [P3] cold-match) recorded; the code anchor for all `--resolve-changed` checkpoints is `750803b2` (not `4cbf8bff`).

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
✅ **Status:** VERIFIED
**Verified by:** Task 10
**Date:** 2026-07-19

**Findings:**
- `SUMMARY.md` row 33 is filled (the S33 close). **Row 34 currently reads `| 34 | 33–34 | Quality, performance & PATH-feedback integration | (planned) | … |`** — but that theme is the **pre-insertion** Sprint 34, now **Sprint 35** (the Sprint-34 insertion renumbered it).
- The row-34 continuation is a **Day-12 close task** (mirroring S33's): **(1) reconcile the theme** — row 34 = "S33 carryforward — mine head-offset dual / sarf symbolic-emit / fawley 2nd-index + forcing / max-convention bound-transfer / camcge Walras [Epic 5] + rocket PATH [Sprint 35]"; **(2) fill the cells** in the rows-28–33 format (Theme / Headline KPIs at close / Firm landing(s) / REPLAN'd → carryforward); **(3) add a row 35** for the renumbered Quality/PATH theme. Genuine-floor recompute maintains **anchor 75**.

**Evidence:** `TOOLING_AND_BACKLOG_ANALYSIS.md` §3; `docs/planning/EPIC_4/SUMMARY.md` row 34 (the current `(planned)` / pre-insertion theme).

**Decision:** a Day-12 close continuation (not this docs-only prep) — reconcile the theme + backfill the cells + add row 35; the anchor-75 recompute holds.

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

**Pre-Day-1 status (Task 11, 2026-07-20):** all 27 unknowns are resolved via prep Tasks 2–10 — **no Critical/High unknown is an unresolved Day-0 blocker**. The **sole `🔍 INCOMPLETE`** is **Unknown 1.2** (mine H_dual → cold MS-1), and it is **intentionally DESIGN-SPECIFIED**: the reconciliation design + the cold-MS-1 `/tmp` control are fully specified, but the control is the Sprint-34 **Day-1 executed gate** (it cannot run in a docs-only prep) — its resolution is an **in-sprint execution gate, not a prep blocker**. The remaining in-sprint gates are the *execution* of each track's PROCEED/REPLAN gate (Days 2/4/5/7), not open prep questions. Sprint 34 is **GO for Day 0** (`PLAN.md` §17).

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

**Document Status:** 🔵 Active — Pre-Sprint 34 (all 27 resolved; GO for Day 0 — Task 11)
**Last Updated:** 2026-07-20
**Owner:** Sprint 34 Planning Team
**Review Frequency:** Daily during Sprint 34
