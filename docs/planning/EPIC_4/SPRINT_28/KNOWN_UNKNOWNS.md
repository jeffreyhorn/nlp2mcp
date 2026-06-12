# Sprint 28 Known Unknowns

**Created:** 2026-06-09
**Status:** Active — Pre-Sprint 28
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 28 — Sprint 27 Carryforward (KKT Cross-Term Correctness, AD Architectural Fixes & Diagnostic/CI Tooling). Codifies Sprint 27 retrospective process recommendations PR24 (Day-0 traced fix-surface) and PR25 (projection discipline), extends the Sprint 26 recommendations PR20–PR23 (Phase 0 acceptance gate, prep-task emit verification, mid-sprint audit script, CI-workflow PR checklist), and introduces three diagnostic/CI tooling tracks (PR26 golden-staleness check, PR27 KKT-residual harness, embedded-NLP-divergence detector + AD cross-term property tests).

---

## Overview

This document identifies all assumptions and unknowns for Sprint 28 features **before** implementation begins. Sprint 28 is the **sixth consecutive sprint** touching alias-aware differentiation / KKT cross-term correctness (after S24's launch attempt, S25's narrow-gate Pattern C fix, S26's Phase A consolidated builder + Pattern C Phase B reclassification, and S27's Phase A gate tightening + Pattern C Phase B landing). It is the first sprint to deliberately pair the carryforward bug-fixes with **diagnostic + CI tooling** so the bug classes that recurred across Sprints 24–27 are caught systematically rather than re-diagnosed by hand each sprint.

**The central new prep activity is the codification of PR24** (the prep-doc fix surface is a Day-0-trace hypothesis, never trusted as fact) **before any Phase 0 gate is authored** — because Sprint 27 proved the prep-doc `file:line` surfaces were wrong 4× (Days 0/6/11/12), and a Known Unknowns List that frames those surfaces as established fact would re-introduce exactly that mis-scope. Accordingly, every carryforward fix-surface unknown below is framed as an *unverified hypothesis* whose verification method is a Day-0 trace + a KKT-residual check, not an assertion to be implemented.

**Sprint 28 Scope** (per `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 entry, Weeks 21–22, 14-day sprint at ≤ 12h/day):

1. **Priority 1: #1224 mine — Parameter-Valued-Offset KKT Cross-Term Inversion** — `stat_x` must invert the parameter-valued offset (`sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` - the `l-1` term)
2. **Priority 2: #1388 camshape — Case-(b) `stat_r` Stationarity-Emit Divergence** — per-term hand-derivation vs the emit; #1424 subset co-bug already landed (Sprint 27)
3. **Priority 3: #1393 + #1335 otpop — Scalar-Eq Sum-Collapse + `card(t)-ord(t)` Offset Evaluator** — two confirmed-distinct fixes (Approach C proven inert)
4. **Priority 4: #1387 cclinpts — Three Coupled AD Changes** — offset-enumeration + re-symbolization anchor + non-convex warm-start; "sign-flip" is a misdiagnosis
5. **Priority 5: #1390 kand — Re-Diagnose the True Mismatch Source** — phantom-term collapse proven inert; the 195-vs-2613 gap is elsewhere
6. **Priority 6: camcge — Singular-Jacobian CGE Degeneracy** — distinct from Pattern C; may be inherent (Epic 5)
7. **Priority 7: Sprint 27 Lower-Priority Cleanups** — #1374 `.l` dedup (robot), #1400 `message`-field path leak, #1385 runtime-guard cross-terms
8. **Priority 8 (Infrastructure): Golden-Staleness Sweep + CI Check** — regenerate-diff-report check + CI gate + `make regen-goldens`
9. **Priority 9 (Infrastructure): KKT-Residual Verification Harness** — formalize the GDX warm-from-good-optimum Case-(a/b/c) discriminator
10. **Priority 10 (Infrastructure): Embedded-NLP-Divergence Detector + AD Cross-Term Property Tests** — catch the `$onMultiR` re-run bug class + the cross-term defect class

**Process Recommendations:** PR24 (Day-0 traced fix-surface), PR25 (projection discipline) — extending PR20–PR23 (in force from Sprint 26).

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 28 entry (Goal, Components, Deliverables, Acceptance Criteria, Estimated Effort 98–144h, Risk Level HIGH) and `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md` (10 prep tasks). No `PRELIMINARY_PLAN.md` exists for Sprint 28 — the `PROJECT_PLAN.md` Sprint 28 section + the `PREP_PLAN.md` are the authoritative scope docs.

**Lessons from Previous Sprints:**

- Sprint 22: 28 unknowns; early preprocessing research saved 20+ hours.
- Sprint 23: 32 unknowns; KU-27 (subset-superset domain) led to a high-impact fix.
- Sprint 24: 26 prep + 6 end-of-sprint KUs; Lark disambiguation unblocked CI.
- Sprint 25: 27 prep + 4 end-of-sprint KUs; KU-33 drove Sprint 26 Priority 1.
- Sprint 26: 26 prep + 3 end-of-sprint KUs (KU-37..KU-39); each drove a Sprint 27 priority.
- Sprint 27: 28 prep unknowns, **all resolved Days 0–13** (see `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"KU Coverage Summary"). The Sprint 27 carryforward is a *set of fixes*, not open KUs — so Sprint 28's unknowns are net-new, organized around the six carryforward fixes + four tooling tracks.

**Sprint 27 Key Learnings** (from `docs/planning/EPIC_4/SPRINT_27/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" + §"What Went Well"):

- **(PR24) Prep-doc fix surfaces were wrong 4×** (Days 0/6/11/12). The real surfaces were `src/kkt/stationarity.py`, `src/ir/ast.py`, and the emit restore pass — NOT the AD `_try_eval_offset` / `constraint_jacobian` sites the prep named. **Every carryforward fix-surface in this document is a hypothesis pending a Day-0 trace.**
- **(PR25) The Day-0 "+6 firm Match" projection over-counted** because it conflated `path_syntax_error → model_infeasible` bucket-forward moves (fawley/otpop/camcge) with genuine Solve/Match gains. The realized Match was +3 (the genuine bucket-to-success transitions). **Every projection must label deltas genuine-gain vs bucket-forward.**
- **(PR27) The GDX warm-from-good-optimum experiment** (does the NLP KKT point satisfy the emitted stationarity?) was the most-reused diagnostic of Sprint 27 — it classified camshape Case (b), proved kand's phantom-collapse inert, and proved launch's 2257.80 a valid KKT point. Sprint 28 formalizes it as the KKT-residual harness (Priority 9).
- **The "embedded NLP pre-solve diverges from standalone" bug class** (`$include` re-running source under `$onMultiR`) drove two Sprint 27 wins (#1378 launch, #1424 camshape). Sprint 28 builds a detector (Priority 10).
- **Golden staleness accumulated silently** (cesam/fawley/korcge/dinam) and surfaced as noise in unrelated PRs. Sprint 28 builds a CI staleness check (Priority 8).

---

## How to Use This Document

### Before Sprint 28 Day 1

1. Research and verify all **Critical** and **High** priority unknowns during prep tasks (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases / Day-0 traces for validation where needed (especially for the carryforward fix-surface hypotheses — these MUST be traced, not asserted, per PR24).
3. Document findings in the "Verification Results" subsection of each unknown.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 28

1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly-discovered unknowns in the "Newly Discovered" section (migrate into categories post-sprint).
3. Update with implementation findings as work progresses.
4. Flag any assumption that turns out wrong — don't quietly re-scope around it. Per PR24, if a Day-0 trace contradicts a prep-doc fix surface, file the correction in the issue doc and the Phase-0 gate before committing src/ effort.

### Priority Definitions

- **Critical:** Wrong assumption will break a sprint priority or require major re-planning (>8 hours of rework). For Sprint 28, this includes any unknown whose disconfirmation would force a carryforward fix to be REPLAN'd to Sprint 29 mid-execution.
- **High:** Wrong assumption will cause significant rework (4–8 hours).
- **Medium:** Wrong assumption will cause minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 29

**By Priority:**

- Critical: 7 (24%)
- High: 12 (41%)
- Medium: 8 (28%)
- Low: 2 (7%)

**By Category:**

- Category 1 (#1224 mine — Parameter-Valued-Offset KKT Cross-Term Inversion): 3 unknowns
- Category 2 (#1388 camshape — Case-(b) `stat_r` Divergence): 3 unknowns
- Category 3 (#1393 + #1335 otpop — Scalar-Eq Sum-Collapse + Offset Evaluator): 3 unknowns
- Category 4 (#1387 cclinpts — Three Coupled AD Changes): 3 unknowns
- Category 5 (#1390 kand — Re-Diagnose the Mismatch): 3 unknowns
- Category 6 (camcge — Singular-Jacobian CGE Degeneracy): 2 unknowns
- Category 7 (Sprint 27 Lower-Priority Cleanups): 3 unknowns
- Category 8 (Infrastructure — Golden-Staleness Sweep + CI Check): 3 unknowns
- Category 9 (Infrastructure — KKT-Residual Verification Harness): 3 unknowns
- Category 10 (Infrastructure — Divergence Detector + AD Cross-Term Property Tests): 3 unknowns

**Estimated Research Time:** 28–36 hours (work-item estimates; the per-unknown numbers below sum to ~36h, but many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping". The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_28/PREP_PLAN.md`: 32–44h across Tasks 1–10.)

---

## Table of Contents

1. [Category 1: #1224 mine — Parameter-Valued-Offset KKT Cross-Term Inversion](#category-1-1224-mine--parameter-valued-offset-kkt-cross-term-inversion)
2. [Category 2: #1388 camshape — Case-(b) `stat_r` Stationarity-Emit Divergence](#category-2-1388-camshape--case-b-stat_r-stationarity-emit-divergence)
3. [Category 3: #1393 + #1335 otpop — Scalar-Eq Sum-Collapse + `card(t)-ord(t)` Offset Evaluator](#category-3-1393--1335-otpop--scalar-eq-sum-collapse--cardt-ordt-offset-evaluator)
4. [Category 4: #1387 cclinpts — Three Coupled AD Changes](#category-4-1387-cclinpts--three-coupled-ad-changes)
5. [Category 5: #1390 kand — Re-Diagnose the True Mismatch Source](#category-5-1390-kand--re-diagnose-the-true-mismatch-source)
6. [Category 6: camcge — Singular-Jacobian CGE Degeneracy](#category-6-camcge--singular-jacobian-cge-degeneracy)
7. [Category 7: Sprint 27 Lower-Priority Cleanups (#1374, #1400, #1385)](#category-7-sprint-27-lower-priority-cleanups-1374-1400-1385)
8. [Category 8: Infrastructure — Golden-Staleness Sweep + CI Check (#PR26)](#category-8-infrastructure--golden-staleness-sweep--ci-check-pr26)
9. [Category 9: Infrastructure — KKT-Residual Verification Harness (PR27)](#category-9-infrastructure--kkt-residual-verification-harness-pr27)
10. [Category 10: Infrastructure — Embedded-NLP-Divergence Detector + AD Cross-Term Property Tests](#category-10-infrastructure--embedded-nlp-divergence-detector--ad-cross-term-property-tests)
11. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: #1224 mine — Parameter-Valued-Offset KKT Cross-Term Inversion

Priority 1 workstream — the highest-leverage Solve carryforward. mine translates (Sprint 27 #1224, `src/ir/ast.py` emit render) but is `model_infeasible` because the `stat_x` cross-term from the `pr` constraint does not invert the parameter-valued offset. Hand-derived target shape recorded in `PROJECT_PLAN.md` Priority 1 + `ISSUE_1224_*.md`.

## Unknown 1.1: Is the AD/Jacobian inversion the correct fix surface, or does a Day-0 trace localize it elsewhere?

### Priority

**Critical** — If the prep-doc surface (`src/ad/constraint_jacobian.py` / `src/ad/derivative_rules.py:2793`) is wrong (as 4 prep surfaces were in Sprint 27), committing src/ effort there wastes the Priority-1 budget and risks a revert. The actual surface might be the same `src/ir/ast.py` emit-render layer the Sprint 27 translate fix touched, or `src/kkt/stationarity.py` (where cross-terms are assembled).

### Assumption

The `stat_x` cross-term inversion is implemented in the AD/Jacobian layer (`constraint_jacobian.py` cross-term construction), producing `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` minus the `l-1` term — **but this is a hypothesis to be confirmed by a Day-0 trace, not an established surface (PR24).**

### Research Questions

1. Where does the current emit produce the non-inverted `sum(k, lam_pr(k,l,i,j))` — in the Jacobian cross-term construction, the stationarity assembly, or the AST emit render?
2. Does a Day-0 trace (instrument the cross-term build for the `pr` constraint) confirm the AD/Jacobian surface, or redirect to `stationarity.py` / `src/ir/ast.py`?
3. Is the offset inversion a general transformation (`x(i+off) → multiplier at i-off`) or specific to parameter-valued offsets?
4. Does the existing alias-offset inversion machinery (used for constant offsets) already exist and just not fire for `ParamRef` offsets?

### How to Verify

1. Run a Day-0 trace: emit `mine_mcp.gms`, locate the `stat_x` row, and instrument the code path that builds its `lam_pr` term (add a temporary log at the candidate surfaces).
2. Cross-check against the constant-offset inversion path — does it produce the inverted multiplier for a synthetic constant-offset analog of `pr`?
3. Apply the KKT-residual harness (Category 9 / Task 4) to confirm whether the NLP KKT point satisfies the *corrected* hand-derived `stat_x` (residual ≈ 0).

### Risk if Wrong

- **Wrong surface committed:** wasted implementation + revert (the Sprint 27 Day-6 cclinpts pattern); 4–6h lost.
- **Inversion is more general than assumed:** broader blast radius (other models with offset cross-terms) → byte-stability re-verification needed.

### Estimated Research Time

1.5 hours (Day-0 trace + constant-offset analog check)

### Owner

AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** mine is `model_infeasible` at Sprint 28 Day 0 (S27 Day-0 `translate_internal_error` → +1 Translate via #1224 `IndexOffset(ParamRef)` render, Day 12 → `model_infeasible`). The projected #1224 Solve delta is a **genuine** bucket-to-success gain (model_infeasible → solve, +1 firm); the follow-on Match is conditional on solving first.
**Evidence:** committed Day-13 `gamslib_status.json` (`mine.mcp_solve.outcome_category = model_infeasible`); BASELINE_METRICS.md §2 provenance row + §3 projection row P1.
**Decision:** +1 Solve tallied toward the ≥110 stretch; mine Match held conditional (not tallied). Fix-surface (AD/Jacobian vs `stationarity.py` vs `ast.py`) remains a Day-0 hypothesis for Tasks 5/6.


**— Task 3 (PR24/PR25 codification — fix-surface-as-hypothesis framing):**

- **Task 3 outcome:** ✅ VERIFIED (framing aspect)
- **Verified by:** Task 3 (Codify PR24 + PR25)
- **Date:** 2026-06-11
- **Findings:** This fix surface (the AD/Jacobian layer vs `src/kkt/stationarity.py` vs the `src/ir/ast.py` emit render) is now governed by the codified **PR24** rule — the prep-doc/issue-doc `### Expected Emit Pattern` is a *hypothesis*; the actual `file:line` is established by a Day-0 trace, and a Phase-0 PROCEED must cite the *traced* surface (never the prep-doc guess).
- **Evidence:** CONTRIBUTING.md §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" + the amended Phase-0 4-subsection template (`### Expected Emit Pattern` hypothesis note; `### PROCEED/REPLAN Signal` `Traced Fix-Surface (Day-0)` line).
- **Decision:** Phase-0 PROCEED for this unknown now requires the traced surface; Task 5 applies PR24 when authoring the gate.


**— Task 5 (Phase-0 acceptance gate authored):**

- **Task 5 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- **Date:** 2026-06-11
- **Findings:** ISSUE_1224 gained a Phase-0 **Solve** gate (the prior gate covered the Sprint 27 translate fix): the inverted `stat_x` hand-derived shape, the harness Verification Methodology (target mine MS 1), and a `Traced Fix-Surface (Day-0)` PROCEED naming AD/Jacobian vs `stationarity.py` vs `ast.py` as the hypothesis (PR24).
- **Evidence:** `docs/issues/ISSUE_1224_*.md` §"Phase 0 Refresh (Sprint 28 … Solve fix)".
- **Decision:** The fix surface stays a Day-0-trace hypothesis; the gate's residual confirmation is the PROCEED gate.

---

## Unknown 1.2: Does the inverse-offset `lam_pr` term need the `l-1` companion term emitted in the same pass?

### Priority

**High** — If the two terms (`sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` and `-sum(k, lam_pr(k,l-1,i,j))`) are assembled in different passes, a partial fix emits an inconsistent `stat_x` (one term present, one missing) → still infeasible, and the Phase 0 residual check fails ambiguously.

### Assumption

Both the inverse-offset term and the `l-1` companion term are produced by the same cross-term-assembly pass for the `pr` constraint, so a single fix emits both atomically.

### Research Questions

1. Are the `i,j` spatial-offset cross-term and the `l` temporal-offset cross-term built by the same code path, or separately?
2. Does the `l-1` term arise from a different constraint instance (the lead/lag duality) that must be enumerated independently?
3. Would emitting only the inverse-offset term (without `-sum(k, lam_pr(k,l-1,i,j))`) leave mine infeasible in a way the harness residual can distinguish?

### How to Verify

1. Hand-derive `stat_x(l,i,j)` for mine and identify which constraint instances contribute each term (Phase 0, Task 5).
2. Trace the cross-term assembly to confirm both terms flow through one pass.
3. KKT-residual harness: emit a both-terms version and an inverse-only version; confirm only the both-terms version gives residual ≈ 0.

### Risk if Wrong

- **Terms separable:** the fix is two coordinated changes, not one → +2–3h and a higher revert risk if only one lands.

### Estimated Research Time

1 hour (hand-derivation cross-check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the Phase-0 gate + hand-derived shape are authored; the fix surface is a Day-0-trace hypothesis (PR24) and the residual confirmation is in-sprint.

**Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
**Date:** 2026-06-11
**Findings:** The ISSUE_1224 Phase-0 Refresh hand-derives `stat_x(l,i,j)` with BOTH the inverse-offset `sum(k, lam_pr(k,l,i-li(k),j-lj(k)))` AND its `- sum(k, lam_pr(k,l-1,i,j))` companion lag term. Whether the two are emitted in one AD pass or two is a Day-0-trace question; the gate's PROCEED requires the harness residual → 0 with **both** present, so a one-term-only emit fails the gate.
**Evidence:** `docs/issues/ISSUE_1224_*.md` §"Phase 0 Refresh" (hand-derived shape + harness Verification Methodology).
**Decision:** Both terms are in the acceptance shape; the emit pass-structure is established by the Day-0 trace, not assumed.

---

## Unknown 1.3: Will the parameter-valued offset `i-li(k)` render correctly at all domain boundaries?

### Priority

**High** — GAMS lead/lag with a parameter offset may clip (drop out-of-range elements) or wrap; if the emitted `lam_pr(k,l,i-li(k),j-lj(k))` references out-of-domain cells, PATH errors or silently zeroes terms, leaving mine infeasible for a reason unrelated to the cross-term math.

### Assumption

GAMS natively handles `lam_pr(k,l,i-li(k),j-lj(k))` lead/lag with parameter-valued offsets by clipping out-of-range references to zero (the standard GAMS lag semantics), matching the NLP's `pr` constraint domain behavior.

### Research Questions

1. Does GAMS clip or wrap a parameter-valued lag like `i-li(k)` when `li(k)` pushes the index out of `i`'s domain?
2. Does the NLP's original `pr.. x(l, i+li(k), j+lj(k))` constraint use the same clip/wrap semantics, so the dual inversion is consistent?
3. Are there `(l,i,j,k)` combinations in mine where the offset lands out of domain, and do they matter for the solution?

### How to Verify

1. Write a minimal GAMS probe with a parameter-valued lag and inspect the generated index set (clip vs wrap).
2. Cross-check mine's `li`/`lj` parameter values against the `i`/`j` domain cardinalities.
3. KKT-residual harness: confirm the emitted `stat_x` residual is ≈ 0 at boundary cells, not just interior cells.

### How to Verify (additional)

- Compare against the `src/ir/ast.py` Sprint 27 render that already emits the forward `i+li(k)` form — confirm the inverse `i-li(k)` renders symmetrically.

### Risk if Wrong

- **Clip/wrap mismatch:** mine stays infeasible at boundary cells; the fix needs an explicit domain guard `$(...)` on the `lam_pr` term → +2h.

### Estimated Research Time

1 hour (GAMS lead/lag probe + boundary-cell check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the harness is *designed* to detect boundary-cell residuals, but the GAMS clip-vs-wrap semantics probe remains a Day-0 task; the unknown's core question is not empirically answered here.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** The harness is *designed* as the residual instrument for the boundary question: the mine sketch (DESIGN §6) would check the emitted `stat_x` residual ≈ 0 at *boundary* cells, not just interior cells — distinguishing a genuine cross-term inversion from an offset-out-of-domain clip that would need an explicit `$(...)` domain guard. (The GAMS clip-vs-wrap probe itself remains a Day-0 task; the harness would report whether the residual vanishes at the boundary once built.)
**Evidence:** DESIGN §6 (mine invocation sketch — boundary-cell residual check) + the concrete forward-render artifact `IndexOffset.to_gams_string()` (`src/ir/ast.py:470`), specifically the `Call`/`ParamRef` offset branch (`src/ir/ast.py:572`, the Sprint 27 #1224 fix) that renders `base+li(k)` directly — the inverse `i-li(k)` form renders symmetrically through that same branch with a negated offset.
**Decision:** The harness verdict for mine explicitly inspects boundary-cell residuals, so Unknown 1.3's clip/wrap risk surfaces as a Case-b-at-boundary signal rather than a silent infeasibility.


**— Task 5 (Phase-0 acceptance gate authored):**

- **Task 5 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- **Date:** 2026-06-11
- **Findings:** The ISSUE_1224 gate's Verification Methodology folds in the boundary-cell residual check (the Task-4 instrument): a residual non-zero *only* at offset-out-of-domain cells ⇒ a domain-guard need, not the inversion. The GAMS clip/wrap probe itself stays a Day-0 task.
- **Evidence:** `docs/issues/ISSUE_1224_*.md` §"Phase 0 Refresh" (boundary-cell check).
- **Decision:** Boundary behaviour is checked by the gate's harness step; the clip/wrap probe is Day-0.

---

# Category 2: #1388 camshape — Case-(b) `stat_r` Stationarity-Emit Divergence

Priority 2 workstream — the second firm Solve carryforward. Sprint 27 Day 11 §4.6 discriminator classified camshape Case (b) (non-inert emit bug, NOT non-convexity): from a verified-complete NLP-KKT warm-start the MCP returns MODEL STATUS 5 with `stat_r(i1)` INFES ≈ 396. The subset-corruption co-bug (#1424) already landed in Sprint 27, making the warm-start valid.

## Unknown 2.1: Is the missing/mis-signed term in the interior `stat_r(i)` or the edge `lam_convex_edge*` cross-terms?

### Priority

**Critical** — The Sprint 27 §4.6 discriminator pinned `stat_r(i1)` INFES ≈ 396 but did not isolate the specific term. If the defect is in the edge cross-terms (boundary `i1`), the fix differs structurally from an interior-term fix, and the prep-doc surface (`stationarity.py:1835`) may be wrong (PR24).

### Assumption

The divergence is a single missing or mis-signed balancing term in the `stat_r(i)` assembly at `src/kkt/stationarity.py:1835` (`_build_indexed_stationarity_expr`), most likely an edge `lam_convex_edge*` cross-term at the `i1` boundary — **a hypothesis pending the Day-0 trace + per-term residual.**

### Research Questions

1. Which `stat_r` term is missing/mis-signed — an interior `lam_convexity` cross-term or an edge `lam_convex_edge1/3/4` cross-term?
2. Why is the INFES concentrated at `i1` (the boundary element)? Does that implicate the edge cross-terms specifically?
3. Does the Day-0 trace confirm `stationarity.py:1835` as the surface, or redirect to `constraint_jacobian.py`?
4. Is the defect the same bug-class as the Sprint 27 cesam2 fixes (which had a cesam/shale/ganges/gangesx blast radius)?

### How to Verify

1. KKT-residual harness (Category 9): warm-start from the NLP optimum (area ≈ 4.2841) and read the per-row residual table — the max-residual row is the prime-suspect term.
2. Hand-derive `stat_r(i)` interior + edge terms (Phase 0, Task 5) and diff against the emit term-by-term.
3. Day-0 trace at the candidate surfaces to confirm where the term is dropped/mis-signed.

### Risk if Wrong

- **Edge vs interior misattribution:** the fix targets the wrong term → camshape stays MS5; +3–4h re-diagnosis.
- **Shared bug-class:** a blast radius beyond camshape (cf. cesam2) → full byte-stability re-verification.

### Estimated Research Time

2 hours (harness residual + per-term hand-derivation diff)

### Owner

AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** camshape is `model_infeasible` at Sprint 28 Day 0 (unchanged across Sprint 27; #1424 subset-corruption landed Day 11 but the MCP stays MS5). The projected #1388 Solve delta is a **genuine** bucket-to-success gain (model_infeasible → solve, +1 firm); Match is conditional on solving first.
**Evidence:** committed Day-13 `gamslib_status.json` (`camshape.mcp_solve.outcome_category = model_infeasible`); BASELINE_METRICS.md §2 row + §3 row P2.
**Decision:** +1 Solve tallied toward the ≥110 stretch; camshape Match held conditional. The interior-`stat_r` vs edge-`lam_convex_edge` term localization is a Task-5/6 fix-surface question.


**— Task 3 (PR24/PR25 codification — fix-surface-as-hypothesis framing):**

- **Task 3 outcome:** ✅ VERIFIED (framing aspect)
- **Verified by:** Task 3 (Codify PR24 + PR25)
- **Date:** 2026-06-11
- **Findings:** This fix surface (the interior `stat_r(i)` vs edge `lam_convex_edge*` cross-terms (prep names `stationarity.py:1835`)) is now governed by the codified **PR24** rule — the prep-doc/issue-doc `### Expected Emit Pattern` is a *hypothesis*; the actual `file:line` is established by a Day-0 trace, and a Phase-0 PROCEED must cite the *traced* surface (never the prep-doc guess).
- **Evidence:** CONTRIBUTING.md §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" + the amended Phase-0 4-subsection template (`### Expected Emit Pattern` hypothesis note; `### PROCEED/REPLAN Signal` `Traced Fix-Surface (Day-0)` line).
- **Decision:** Phase-0 PROCEED for this unknown now requires the traced surface; Task 5 applies PR24 when authoring the gate.


**— Task 5 (Phase-0 acceptance gate authored):**

- **Task 5 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- **Date:** 2026-06-11
- **Findings:** ISSUE_1388's gate (refreshed) hand-derives the interior `stat_r(i)` cross-terms + the canonical `middle(i±1)` guards (vs the looser emitted guards) and the edge `convex_edge*` terms; surface `stationarity.py:1835` is named as the hypothesis (PR24).
- **Evidence:** `docs/issues/ISSUE_1388_*.md` §"Hand-Derived KKT Shape" + §"Phase 0 Refresh".
- **Decision:** Whether the missing/mis-signed term is interior or edge is pinned by the harness max-residual row at Day 0.

---

## Unknown 2.2: Does fixing `stat_r` risk the same multi-model blast radius as the Sprint 27 cesam2 bug-class fixes?

### Priority

**High** — Sprint 27's `stationarity.py` cross-term fixes for cesam2 had a cesam/shale/ganges/gangesx blast radius (all same bug-class, all improvements, but requiring golden regen + re-solve). If the camshape `stat_r` fix touches a shared code path, the same multi-model verification is required and must be budgeted.

### Assumption

The camshape `stat_r` fix is camshape-specific (gated to the convex-combination shape), with no blast radius beyond camshape — verifiable via a full-corpus byte scan.

### Research Questions

1. Does the candidate fix surface (`stationarity.py:1835`) serve other models' stationarity assembly, or only the camshape convex-combination shape?
2. Which other corpus models use the `lam_convex_edge*` / convex-combination construct?
3. Would the fix change any currently-matching model's emit (a regression risk)?

### How to Verify

1. Grep the corpus for the convex-combination / `lam_convex_edge` construct.
2. Phase 0 hand-derivation: confirm the fix is gated to the specific shape.
3. After a prototype fix, run the golden-staleness check (Category 8 / Task 7) to enumerate the byte-diff blast radius.

### Risk if Wrong

- **Wide blast radius:** golden regen + re-solve for N models → +2–4h verification; potential regression on a matching model.

### Estimated Research Time

1.5 hours (corpus grep + gating analysis)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the harness is *designed to* pin the fix target, but the blast-radius *enumeration* is owned by Task 7's golden-staleness check (run after a prototype fix); not answered here.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** The harness is *designed to* pin camshape's Case-b max-residual row (`stat_r('i1')`≈396, DESIGN §6) as the fix target; the blast-radius enumeration itself is the **golden-staleness check (Task 7 / Category 8)**, run after a prototype fix — the harness and the staleness check are complementary (residual = correctness target, staleness = blast radius).
**Evidence:** DESIGN §6 (camshape sketch) + the Task 7 golden-staleness cross-reference.
**Decision:** The harness confirms *what* to fix (the max-residual `stat_r` term); Task 7 measures *how wide* the fix's byte-diff reaches — the 2.2 blast-radius concern is owned by Task 7, instrumented by this harness.


**— Task 5 (Phase-0 acceptance gate authored):**

- **Task 5 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- **Date:** 2026-06-11
- **Findings:** The ISSUE_1388 gate is *designed to* pin `stat_r('i1')`≈396 as the fix target; the blast-radius enumeration is explicitly deferred to the Task 7 golden-staleness check (run after a prototype fix), not asserted in the gate.
- **Evidence:** `docs/issues/ISSUE_1388_*.md` §"Phase 0 Refresh" (blast-radius → Task 7).
- **Decision:** Gate pins the fix target; Task 7 measures blast radius — complementary, not duplicated.

---

## Unknown 2.3: Does the #1424 subset-default fix (Sprint 27) fully validate the camshape warm-start, or are residual warm-start gaps possible?

### Priority

**Medium** — The §4.6 discriminator relied on a verified-complete warm-start (all 3 primals + 7 multipliers loaded). If the #1424 fix left any warm-start symbol incompletely initialized, a MODEL STATUS 5 could be a warm-start artifact rather than the `stat_r` emit bug, invalidating the Case-(b) classification.

### Assumption

With #1424 landed, the `--nlp-presolve` emit warm-starts all 10 camshape symbols (3 primals + 7 multipliers) correctly, so the MS5 is attributable to the `stat_r` emit bug alone.

### Research Questions

1. Does the current `camshape_mcp_presolve.gms` load all 10 warm-start symbols at non-zero where expected?
2. Could any multiplier still start at zero (independently driving PATH to MS5)?
3. Does the harness's dual-transfer (Category 9) reproduce the §4.6 warm-start exactly?

### How to Verify

1. Regenerate `camshape_mcp_presolve.gms` on current main; display-block pre-check all 10 symbols (per the Sprint 27 §4.6 10-symbol check).
2. KKT-residual harness: confirm the warm-start it loads matches the §4.6 state.

### Risk if Wrong

- **Incomplete warm-start:** the Case-(b) classification is in doubt → re-run the discriminator (+1–2h) before fixing.

### Estimated Research Time

1 hour (regen + 10-symbol display check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the Phase-0 gate + hand-derived shape are authored; the fix surface is a Day-0-trace hypothesis (PR24) and the residual confirmation is in-sprint.

**Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
**Date:** 2026-06-11
**Findings:** The ISSUE_1388 Phase-0 Refresh records the Sprint 27 Day-11 §4.6 verdict: post-#1424 the 10-symbol warm-start IS valid (embedded NLP reaches MS2 area=4.2841), yet the MCP stays MS5 with `stat_r(i1)` INFES≈396 — a **non-inert per-term emit divergence**, not a warm-start gap. So #1424 validated the warm-start; the residual gap is the remaining `stat_r` fix the gate targets.
**Evidence:** `docs/issues/ISSUE_1388_*.md` §"Phase 0 Refresh" + §4.6 discriminator; BASELINE_METRICS §2 camshape row.
**Decision:** The warm-start is sound (Case b, not a gap); the in-sprint fix is the per-term `stat_r` guard/coefficient, confirmed by the harness residual.

---

# Category 3: #1393 + #1335 otpop — Scalar-Eq Sum-Collapse + `card(t)-ord(t)` Offset Evaluator

Priority 3 workstream — confirmed two distinct fixes (Sprint 27 Day 0 proved #1393's Approach C inert). #1393: the over-counted `sum(t__, …·nu_kdef)` cross-term must collapse via the `stationarity.py` symbolic-collapse path. #1335: the missing `nu_zdef` cross-term needs a `_try_eval_offset` extension resolving `card(t)-ord(t)` arithmetic without Sum expansion (Approach B).

## Unknown 3.1: Which `stationarity.py` code path does the `t→t__` aliasing actually flow through (#1393)?

### Priority

**Critical** — Sprint 27 Day 0 proved Approach C (`_is_concrete_instance_of`) is inert (otpop_mcp.gms byte-identical, no src diff). If the Day-0 trace does not localize the actual collapse path, #1393 cannot be fixed and otpop stays `model_infeasible`. This is the canonical PR24 case: the prep-doc surface was already disproven once.

### Assumption

The over-counted `sum(t__, del(t__)…·nu_kdef)` cross-term collapse happens in the `stationarity.py` symbolic-collapse path (where `t→t__` aliasing occurs), NOT in `_is_concrete_instance_of` — **but the exact function/line is a Day-0-trace hypothesis (Approach C already disproven).**

### Research Questions

1. Where in `stationarity.py` is the `t__` alias Sum constructed for `stat_x(tt)` / `stat_p(tt)`?
2. What predicate currently fails to collapse the over-counted terms to one?
3. Does a Day-0 env-guarded prototype (zero src diff) confirm the collapse point produces the correct `stat_x('tt-elem')`?
4. Is #1393's collapse independent of #1335's offset evaluator, or coupled (sequencing)?

### How to Verify

1. Day-0 trace: instrument the `stationarity.py` alias-Sum construction for otpop's `stat_x`/`stat_p`; identify the over-counting site.
2. Env-guarded prototype (per the Sprint 27 PR16 methodology): collapse the terms, verify `otpop_mcp.gms` regenerates with the correct shape, zero unrelated diff.
3. KKT-residual harness: confirm the collapsed `stat_x` residual ≈ 0 at the NLP optimum (cost ≈ 4217.80).

### Risk if Wrong

- **Collapse path not localized:** #1393 REPLANs again → otpop deferred to Sprint 29; the Match target loses +1.

### Estimated Research Time

2 hours (Day-0 trace + env-guarded prototype)

### Owner

AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** otpop is `model_infeasible` at Sprint 28 Day 0 — a **bucket-forward** move already banked in Sprint 27 (S27 Day-0 `path_syntax_error` → P5 #1356/#1357 cleared `$171` → Locally Infeasible). The projected #1393+#1335 delta is a **genuine** Solve +1 firm AND Match +1 firm.
**Evidence:** committed Day-13 `gamslib_status.json` (`otpop.mcp_solve.outcome_category = model_infeasible`); BASELINE_METRICS.md §2 row + §3 row P3.
**Decision:** +1 Solve and +1 Match tallied (firm). The prior `path_syntax_error → model_infeasible` move is NOT re-counted (PR25). Which `stationarity.py` collapse path the `t→t__` aliasing flows through stays a Task-5/6 question.


**— Task 3 (PR24/PR25 codification — fix-surface-as-hypothesis framing):**

- **Task 3 outcome:** ✅ VERIFIED (framing aspect)
- **Verified by:** Task 3 (Codify PR24 + PR25)
- **Date:** 2026-06-11
- **Findings:** This fix surface (which `stationarity.py` symbolic-collapse path the `t→t__` aliasing flows through) is now governed by the codified **PR24** rule — the prep-doc/issue-doc `### Expected Emit Pattern` is a *hypothesis*; the actual `file:line` is established by a Day-0 trace, and a Phase-0 PROCEED must cite the *traced* surface (never the prep-doc guess).
- **Evidence:** CONTRIBUTING.md §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" + the amended Phase-0 4-subsection template (`### Expected Emit Pattern` hypothesis note; `### PROCEED/REPLAN Signal` `Traced Fix-Surface (Day-0)` line).
- **Decision:** Phase-0 PROCEED for this unknown now requires the traced surface; Task 5 applies PR24 when authoring the gate.


**— Task 5 (Phase-0 acceptance gate authored):**

- **Task 5 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
- **Date:** 2026-06-11
- **Findings:** ISSUE_1393 gained a Phase-0 gate recording the `t→t__` aliasing redirect onto the `stationarity.py` symbolic-collapse path (the AD `_is_concrete_instance_of` surface was proven inert in Sprint 27); the single-guarded `stat_x`/`stat_p` shape is hand-derived, surface a Day-0 hypothesis (PR24).
- **Evidence:** `docs/issues/ISSUE_1393_*.md` §"Phase 0: Acceptance Gate".
- **Decision:** Which `stationarity.py` code path the aliasing flows through is established by the Day-0 trace, not the prep doc.

---

## Unknown 3.2: Does the `_try_eval_offset` `card(t)-ord(t)` extension (#1335, Approach B) interact with the #1393 collapse?

### Priority

**High** — If the missing `nu_zdef` cross-term (#1335) and the over-counted `nu_kdef` collapse (#1393) touch the same `stat_x` row, the two fixes must be sequenced/coordinated; landing one without the other could leave otpop infeasible in a way that masks the second fix's correctness.

### Assumption

#1335 (add the `nu_zdef` cross-term via a symbolic `card(t)-ord(t)` offset evaluator, no Sum expansion) and #1393 (collapse the `nu_kdef` over-count) are independent fixes that can land in either order, each verifiable by the harness residual on its own row.

### Research Questions

1. Do the `nu_zdef` and `nu_kdef` terms appear in the same `stat_x(tt)` row or different rows?
2. Does Approach B's `card(t)-ord(t)` evaluator require the #1393 collapse to be in place first (or vice versa)?
3. Is Approach B (symbolic resolution) confirmed superior to the other two #1335 approaches Sprint 26 Day 9 enumerated?

### How to Verify

1. Hand-derive otpop's full `stat_x(tt)` (Phase 0, Task 5); identify which rows each term lands in.
2. Prototype each fix independently behind an env guard; check the harness residual after each.

### Risk if Wrong

- **Coupled fixes:** sequencing constraint → +1–2h coordination; risk of a partial-fix infeasibility masking progress.

### Estimated Research Time

1.5 hours (hand-derivation + independence check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the Phase-0 gate + hand-derived shape are authored; the fix surface is a Day-0-trace hypothesis (PR24) and the residual confirmation is in-sprint.

**Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
**Date:** 2026-06-11
**Findings:** The ISSUE_1335 and ISSUE_1393 gates record that otpop's +1 Solve/+1 Match needs **both** fixes — #1393 (the scalar `kdef` Sum-collapse in `stat_x`/`stat_p`) and #1335 (the missing `zdef` `nu_zdef` cross-term via the `card(t)-ord(t)` evaluator). They are sequenced and co-gated by the same harness run + the `cost ≈ 4217.80` target; the `_try_eval_offset` extension is independent of the #1393 collapse path but both must land.
**Evidence:** `docs/issues/ISSUE_1393_*.md` + `docs/issues/ISSUE_1335_*.md` §"Phase 0: Acceptance Gate" (companion cross-links).
**Decision:** otpop is gated on both #1393 and #1335; the Day-0 trace confirms whether they are independent edits or must be sequenced.

---

## Unknown 3.3: Will the `_try_eval_offset` `card(t)-ord(t)` extension regress any currently-translating model?

### Priority

**Medium** — Extending the offset evaluator to resolve symbolic-base `IndexOffset`s with `card(t)-ord(t)` arithmetic could change emit for other time-indexed models that use end-of-horizon offsets.

### Assumption

The `card(t)-ord(t)` extension is gated to the symbolic-base offset shape and does not change emit for models whose offsets already resolve to constants.

### Research Questions

1. Which corpus models use `card(t)-ord(t)`-style or end-of-horizon offsets?
2. Does the extension fire only when the offset would otherwise be left unresolved (the current `nu_zdef`-drop case)?
3. Does the golden-staleness check (Category 8) show any unexpected byte-diffs after the extension?

### How to Verify

1. Grep the corpus for `card(`/`ord(` offset patterns.
2. After the prototype, run the golden-staleness check to enumerate the blast radius.

### Risk if Wrong

- **Unexpected emit change:** golden regen + re-solve for affected models → +1–2h.

### Estimated Research Time

1 hour (corpus grep + gating check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the Phase-0 gate + hand-derived shape are authored; the fix surface is a Day-0-trace hypothesis (PR24) and the residual confirmation is in-sprint.

**Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
**Date:** 2026-06-11
**Findings:** The ISSUE_1335 gate's PROCEED requires the symbolic `card(t)-ord(t)` extension to restore `nu_zdef` **without** regressing other models' offset handling. Whether it regresses is an implementation-time check (the Task 7 golden-staleness enumeration over the corpus), gated here as a PROCEED precondition rather than asserted now.
**Evidence:** `docs/issues/ISSUE_1335_*.md` §"PROCEED/REPLAN Signal" (no-regression precondition); Task 7 golden-staleness check.
**Decision:** The no-regression requirement is a gate precondition verified at implementation, not by this docs-only task.

---

# Category 4: #1387 cclinpts — Three Coupled AD Changes

Priority 4 workstream — REPLAN-prone (diagnosis-heavy). Per the Sprint 27 Day-6 binding diagnosis, cclinpts needs three coupled changes: (1) AD objective-gradient offset-enumeration in `_diff_sum`; (2) a gradient→stationarity re-symbolization anchor fix; (3) a non-convex warm-start. The "sign-flip" framing is a misdiagnosis (the `(-1)` is the standard maximize negation — do NOT touch sign logic).

## Unknown 4.1: Is the gradient→stationarity re-symbolization anchor fix architectural or local?

### Priority

**Critical** — This is the explicit REPLAN pivot for Priority 4. Sprint 27 Day 6 implemented the offset-enumeration but reverted because the re-symbolization anchored a pure-offset term on the wrong element. If the anchor fix touches all re-symbolization callers (architectural), Priority 4 REPLANs to Sprint 29; if it can be gated to the offset case (local), it lands in Sprint 28.

### Assumption

The re-symbolization anchor fix can be made local — gated so a pure-offset term anchors on the differentiated variable's own column index rather than an arbitrary element — without changing the re-symbolization behavior for non-offset terms.

### Research Questions

1. How many callers of the re-symbolization path would a correct anchor change affect?
2. Can the anchor be selected from the differentiated variable's column index in a gated branch, or is the anchor chosen upstream of any per-term context?
3. Does the Sprint 27 Day-6 revert reproduce on current main (re-confirm the blocker still exists)?
4. Do all three coupled changes still need to land together, or has Sprint 27's later work changed the dependency?

### How to Verify

1. Re-run the Sprint 27 Day-6 prototype on current main; confirm the anchor blocker.
2. Trace the re-symbolization callers; classify the anchor fix architectural vs local (Task 6 hypothesis-validation).
3. KKT-residual harness: eliminated-KKT residual check at the NLP optimum (`objgrad_b(j) + b(j)^(-γ)·objgrad_fb(j) = 0`, max|r| ≤ 1e-6) on a single-model prototype.

### Risk if Wrong

- **Architectural:** Priority 4 REPLANs to Sprint 29 → the +1 Match is deferred; budget reallocates.
- **Local but mis-gated:** the Day-6 wrong-anchor revert recurs → cclinpts worse, not better.

### Estimated Research Time

1.5 hours (re-run prototype + caller trace)

### Owner

AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** cclinpts is `model_optimal` / mismatch at Sprint 28 Day 0 (already solves; obj -9.975 vs NLP -3.0011, rel 0.70). The projected #1387 delta is a **genuine** solve→match gain (Match +1) — it is **NOT** a Solve gain.
**Evidence:** committed Day-13 `gamslib_status.json` (`cclinpts` model_optimal, `solution_comparison.comparison_result = compare_objective_mismatch`); BASELINE_METRICS.md §2 row + §3 row P4.
**Decision:** +1 Match tallied (firm); 0 Solve credit. Whether the re-symbolization-anchor fix is architectural (→ Sprint 29 REPLAN) is the Task-6 hypothesis-validation, not a Task-2 baseline question.


**— Task 3 (PR24/PR25 codification — fix-surface-as-hypothesis framing):**

- **Task 3 outcome:** ✅ VERIFIED (framing aspect)
- **Verified by:** Task 3 (Codify PR24 + PR25)
- **Date:** 2026-06-11
- **Findings:** This fix surface (whether the gradient→stationarity re-symbolization anchor fix is architectural or local) is now governed by the codified **PR24** rule — the prep-doc/issue-doc `### Expected Emit Pattern` is a *hypothesis*; the actual `file:line` is established by a Day-0 trace, and a Phase-0 PROCEED must cite the *traced* surface (never the prep-doc guess).
- **Evidence:** CONTRIBUTING.md §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" + the amended Phase-0 4-subsection template (`### Expected Emit Pattern` hypothesis note; `### PROCEED/REPLAN Signal` `Traced Fix-Surface (Day-0)` line).
- **Decision:** Phase-0 PROCEED for this unknown now requires the traced surface; Task 5 applies PR24 when authoring the gate.


**— Task 6 (REPLAN risk assessment — PR16):**

- **Task 6 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- **Date:** 2026-06-11
- **Findings:** Track A makes the **architectural-vs-local anchor** question the explicit Priority-4 decision pivot. Validation design: (A1) re-run the Day-6 `_diff_sum` prototype on current main to re-confirm the anchor blocker; (A2) **trace the re-symbolization callers** to classify the anchor fix local (gateable to the differentiated variable's column index) vs architectural (chosen upstream / all callers); (A3) harness eliminated-KKT residual (5e-8) re-check. Sign-flip stays a misdiagnosis.
- **Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track A.
- **Decision:** **PROCEED** if A2 shows local; **REPLAN to Sprint 29** if architectural. All three coupled changes land together. Budget at risk ~12–18h.

---

## Unknown 4.2: Are the AD offset-enumeration cross-terms (change 1) correct as residual-verified in Sprint 27?

### Priority

**High** — Sprint 27 residual-verified the per-instance offset-enumeration math to 5e-8 at the NLP optimum, but it was reverted as part of the coupled bundle. If that verification still holds on current main, change 1 is de-risked and only changes 2–3 carry uncertainty.

### Assumption

The Sprint 27 `_diff_sum` offset-enumeration (the missing j+1 cross-terms) is mathematically correct as residual-verified (5e-8); re-applying it on current main reproduces the same per-instance correctness.

### Research Questions

1. Does the Sprint 27 offset-enumeration prototype still apply cleanly to current main?
2. Does the eliminated-KKT residual still verify to ≤ 1e-6 at the NLP optimum?
3. Is the enumeration gated tightly enough to avoid the cclinpts diagonal-cancellation the Day-6 note described?

### How to Verify

1. Re-apply the Sprint 27 `_try_diff_sum_offset_crossterms` prototype; run the eliminated-KKT residual check.
2. Confirm the per-instance math matches the hand-derived offset cross-terms (Phase 0, Task 5).

### Risk if Wrong

- **Math no longer verifies:** change 1 needs re-derivation → +2h; the three-change bundle grows.

### Estimated Research Time

1.5 hours (re-apply prototype + residual check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the Phase-0 gate + hand-derived shape are authored; the fix surface is a Day-0-trace hypothesis (PR24) and the residual confirmation is in-sprint.

**Verified by:** Task 5 (Author/Refresh Phase 0 Acceptance Gates)
**Date:** 2026-06-11
**Findings:** The ISSUE_1387 Phase-0 Refresh records that change-1 (the AD `_diff_sum` `j+1`-offset cross-terms) was **residual-verified in Sprint 27** — eliminated-KKT max|r| = 5e-8 at the NLP optimum — so the gate REUSES that verification rather than re-deriving. The open risk is changes 2 (re-symbolization anchor) and 3 (non-convex warm-start), assessed in Task 6; all three must land together.
**Evidence:** `docs/issues/ISSUE_1387_*.md` §"Phase 0 Refresh" (5e-8 residual reuse) + Hand-Derived KKT Shape.
**Decision:** Change-1 cross-terms are accepted as Sprint-27-verified; the Match gain is contingent on changes 2/3, which carry the REPLAN risk (Task 6).

---

## Unknown 4.3: Is the cclinpts non-convex warm-start (change 3) cclinpts-specific or generalizable?

### Priority

**Medium** — cclinpts cold-converges to a spurious degenerate KKT point (`b ≈ const`); change 3 is a warm-start. If the warm-start mechanism generalizes, it benefits other non-convex models; if cclinpts-specific, it's a one-off and must not regress the cold-start path for convex models.

### Assumption

The cclinpts warm-start is a model-specific initial point (or `--nlp-presolve` warm-start) that does not change the default cold-start emit for any other model.

### Research Questions

1. Can the warm-start be delivered via `--nlp-presolve` (reusing the existing machinery), or does it need a bespoke initial point?
2. Does a warm-started cclinpts reach MODEL STATUS 1 with `rel_diff < 1%`?
3. Does the warm-start interact with changes 1–2 (i.e., is it only effective once the emit is correct)?

### How to Verify

1. Once changes 1–2 prototype is in place, run cclinpts with a warm-start (presolve or manual) and check MODEL STATUS + rel_diff.
2. Confirm the warm-start path leaves other models' emit byte-identical.

### Risk if Wrong

- **Warm-start ineffective / leaks to other models:** cclinpts stays mismatch or a regression appears → +1–2h.

### Estimated Research Time

1 hour (warm-start experiment, gated on changes 1–2)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the single-model validation + PROCEED/REPLAN recommendation are designed; the binding verdict comes from the in-sprint Day-0 run.

**Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
**Date:** 2026-06-11
**Findings:** The cclinpts non-convex warm-start (change 3) is assessed as **model-specific** — Track A's validation design delivers it via the existing `--nlp-presolve` machinery (a per-model initial point, not a default-cold-start change), so it does not alter any other model's emit. It is only effective once changes 1–2 (AD enumeration + anchor) are correct, so it is gated on them.
**Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track A (A3 + the three-coupled-change dependency).
**Decision:** Warm-start is cclinpts-specific via presolve; a byte-stability check on other models' emit is part of the in-sprint validation (no leak).

---

# Category 5: #1390 kand — Re-Diagnose the True Mismatch Source

Priority 5 workstream — REPLAN-prone (diagnosis-heavy). Sprint 27 proved the phantom-term collapse is inert (MCP stays `cost = 195.0` ≠ NLP `2613.0`). The real defect is elsewhere; re-diagnosis surfaces are the `bal(j,t,n)`/`x` stationarity, the `t-1`↔`t+1` lag duality, or the LP first-stage/recourse coupling.

## Unknown 5.1: Where is the 195.0-vs-2613.0 gap — a localizable stationarity/complementarity row, or LP-recourse-coupling architecture?

### Priority

**Critical** — This determines whether #1390 is a Sprint 28 fix or a Sprint 29 re-scope. The phantom-term re-symbolization is proven inert (explicitly out of scope), so a fresh Day-0 trace via the KKT-residual harness is the ONLY verification path. If the gap is LP-recourse-coupling architecture, #1390 REPLANs.

### Assumption

The 195-vs-2613 gap localizes to a specific stationarity or complementarity row (most likely `bal(j,t,n)`/`x` stationarity or the `t-1`↔`t+1` lag duality) that the KKT-residual harness can pinpoint — **not the (proven-inert) phantom-term collapse.**

### Research Questions

1. Does the NLP KKT point (cost 2613.0) satisfy the emitted kand stationarity (Case b) or not (Case c)?
2. Which row has the maximum residual — `bal`/`x` stationarity, a lag-duality row, or an LP-recourse coupling row?
3. Is the gap an emit bug (fixable) or a structural LP first-stage/recourse coupling issue (architectural → Sprint 29)?
4. Does the harness's dual-transfer correctly handle kand's tree-conditioned aliased Sum multipliers?

### How to Verify

1. KKT-residual harness (Category 9 / Task 4): warm-start kand from the NLP optimum; read the per-row residual; classify Case (a/b/c).
2. Day-0 trace at the max-residual row to localize the surface.
3. Task 6 hypothesis-validation: decide PROCEED (localizable row) vs REPLAN (LP-recourse architecture).

### Risk if Wrong

- **Architectural gap:** #1390 REPLANs to Sprint 29 → the +1 Match is deferred.
- **Harness can't localize:** re-diagnosis stalls → Match target at risk.

### Estimated Research Time

2 hours (harness residual + Day-0 trace + classification)

### Owner

AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** kand is `model_optimal` / mismatch at Sprint 28 Day 0 (already solves; obj 195.0 vs NLP 2613.0, rel 0.93). The projected #1390 delta is a **genuine** solve→match gain (Match +1) — **NOT** a Solve gain.
**Evidence:** committed Day-13 `gamslib_status.json` (`kand` model_optimal, `solution_comparison.comparison_result = compare_objective_mismatch`); BASELINE_METRICS.md §2 row + §3 row P5.
**Decision:** +1 Match tallied (firm); 0 Solve credit. Whether the 195-vs-2613 gap is a localizable row vs LP-recourse-coupling architecture (→ Sprint 29 REPLAN) is the Task-6 question.


**— Task 3 (PR24/PR25 codification — fix-surface-as-hypothesis framing):**

- **Task 3 outcome:** ✅ VERIFIED (framing aspect)
- **Verified by:** Task 3 (Codify PR24 + PR25)
- **Date:** 2026-06-11
- **Findings:** This fix surface (a localizable stationarity/complementarity row vs LP first-stage/recourse-coupling architecture) is now governed by the codified **PR24** rule — the prep-doc/issue-doc `### Expected Emit Pattern` is a *hypothesis*; the actual `file:line` is established by a Day-0 trace, and a Phase-0 PROCEED must cite the *traced* surface (never the prep-doc guess).
- **Evidence:** CONTRIBUTING.md §"Day-0 Traced Fix-Surface (PR24) + Projection Discipline (PR25)" + the amended Phase-0 4-subsection template (`### Expected Emit Pattern` hypothesis note; `### PROCEED/REPLAN Signal` `Traced Fix-Surface (Day-0)` line).
- **Decision:** Phase-0 PROCEED for this unknown now requires the traced surface; Task 5 applies PR24 when authoring the gate.


**— Task 4 (KKT-residual harness as the verification instrument):**

- **Task 4 outcome:** 🟡 PARTIALLY VERIFIED (design scope) — the harness is *designed* as the Case-(b/c) instrument; the empirical verdict comes from the in-sprint run.
- **Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
- **Date:** 2026-06-11
- **Findings:** The harness is *designed to* provide the Case-(b/c) split that would drive the kand REPLAN decision: dual transfer consistent + `max|r|≤tol` ⇒ **Case c** (the 195-vs-2613 gap is non-convexity / LP first-stage-recourse coupling → Sprint 29 REPLAN); a `stat` row `> tol` ⇒ **Case b** (a localizable emit row, in-sprint fix). The actual gap localization is the Day-0 trace (Tasks 5/6) *using* this harness once built.
- **Evidence:** `PRIORITY_9_KKT_RESIDUAL_HARNESS_DESIGN.md` §6 (kand sketch) + §3 (verdict logic).
- **Decision:** The kand Phase-0 gate (Task 5) runs the harness first; its Case-b-vs-Case-c verdict is the binding input to the #1390 PROCEED/REPLAN signal.


**— Task 6 (REPLAN risk assessment — PR16):**

- **Task 6 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- **Date:** 2026-06-11
- **Findings:** Track B's Day-0 trace plan uses the KKT-residual harness to localize the 195-vs-2613 gap: dual-transfer self-check (B1) first, then Case-(b/c) (B2). **Case b** (a `bal`/`x` stationarity or lag-duality row > tol) ⇒ localizable → PROCEED; **Case c** (residuals clean, cold PATH at 195) ⇒ LP-recourse coupling → REPLAN. Phantom-term collapse stays out of scope (inert).
- **Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track B.
- **Decision:** Harness Case-(b/c) verdict is the binding signal; lean REPLAN-aware (first hypothesis already inert). Budget at risk ~8–14h.

---

## Unknown 5.2: Does the KKT-residual harness correctly transfer kand's tree-predicate-conditioned aliased-Sum duals?

### Priority

**High** — kand's multipliers are tree-conditioned aliased Sums (`tree(nn,n)`-conditioned). If the harness can't transfer these duals from the NLP solution, the residual it reports is unreliable and the Case-(a/b/c) verdict for Unknown 5.1 is invalid.

### Assumption

The harness dual-transfer (Category 9) handles tree-conditioned aliased-Sum multipliers by loading the NLP constraint marginals into the corresponding MCP multiplier variables, preserving the tree-predicate condition.

### Research Questions

1. How are kand's `lam_dembalx` (tree-conditioned) multipliers represented in the emitted MCP?
2. Can the harness map the NLP `dembalx` marginals onto them, respecting the `tree(nn,n)` condition (the argument order the emitted `kand_mcp.gms` uses)?
3. Does an incorrect dual transfer produce a false Case-(b) residual?

### How to Verify

1. Inspect kand's emitted multiplier declarations; design the dual-transfer mapping (feeds Category 9 / Task 4).
2. Sanity-check: transfer the duals, then verify the *constraint* rows (not stationarity) have residual ≈ 0 (the duals are consistent with the NLP).

### Risk if Wrong

- **Bad dual transfer:** the harness verdict for 5.1 is unreliable → the whole kand diagnosis is in doubt; +2h.

### Estimated Research Time

1.5 hours (multiplier-mapping design + consistency check)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the dual-transfer for the tree-conditioned duals + the consistency self-check are *designed*; correctness is observed only when the harness is built and run on kand in-sprint.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** kand's `lam_dembalx` multipliers are `tree(nn,n)`-conditioned aliased Sums; the harness is *designed* to load the NLP `dembalx` marginals into them respecting the tree predicate, with the **constraint-row consistency self-check as the gating step** (DESIGN §2 + §6 kand): the *constraint* rows must be ≈ 0 before any stationarity verdict is trusted. By design a bad transfer would report `dual_transfer_inconsistent` rather than a false Case-b, so the 5.1 verdict cannot be corrupted by a mis-transferred tree-conditioned dual once the harness is built and run.
**Evidence:** DESIGN §2 (consistency self-check) + §6 (kand invocation sketch) — design, not a run result.
**Decision:** kand's Case-(a/b/c) verdict (Unknown 5.1) is to be consumed only after the dual-transfer self-check passes — the tree-conditioned transfer will be confirmed by constraint-row residual ≈ 0 when the harness runs in-sprint.


**— Task 6 (REPLAN risk assessment — PR16):**

- **Task 6 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- **Date:** 2026-06-11
- **Findings:** Track B step B1 makes the dual-transfer consistency self-check the **gating precondition** for the kand verdict: the `tree(nn,n)`-conditioned `lam_dembalx` marginals must transfer so the *constraint* rows ≈ 0 before any Case-(b/c) verdict is trusted; a bad transfer reports `dual_transfer_inconsistent`, not a false Case-b.
- **Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track B (B1); harness design §2 self-check.
- **Decision:** The 5.1 verdict is consumed only after B1 passes; designed, confirmed in-sprint.

---

## Unknown 5.3: Is kand's NLP reference optimum (2613.0) itself reliable as the warm-start target?

### Priority

**Low** — The re-diagnosis assumes 2613.0 is the correct NLP optimum to warm-start from. If the NLP reference is itself questionable (e.g., a local optimum), the residual comparison is against the wrong target.

### Assumption

kand's NLP optimum is reliably 2613.0 (the standalone GAMS NLP solve value), and it is the correct warm-start target for the harness.

### Research Questions

1. Does a standalone kand NLP solve reproduce 2613.0 deterministically?
2. Is 2613.0 a global or local optimum (does the model have multiple optima)?

### How to Verify

1. Run the standalone kand NLP solve; confirm 2613.0.
2. Check the `_NLP_REFERENCES` entry (if present) for kand.

### Risk if Wrong

- **Unreliable reference:** the harness target is wrong → minor; re-establish the reference (<1h).

### Estimated Research Time

0.5 hours (standalone NLP solve)

### Owner

AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the single-model validation + PROCEED/REPLAN recommendation are designed; the binding verdict comes from the in-sprint Day-0 run.

**Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
**Date:** 2026-06-11
**Findings:** kand's NLP reference 2613.0 is the harness warm-start target; Track B step B0 designs the reliability check — a standalone deterministic NLP solve + a global-vs-local check (multiple optima?). If 2613.0 proves a local optimum, the residual comparison target is re-established before the Case-(b/c) verdict.
**Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track B (B0); harness design §6 (kand target 2613.0).
**Decision:** The NLP-reference check is a Day-0 precondition of the kand verdict; designed, run in-sprint.

---

# Category 6: camcge — Singular-Jacobian CGE Degeneracy

Priority 6 workstream — REPLAN-prone. camcge translates `action=c`-clean (Pattern C Phase B emit correct) but the MCP is `model_infeasible` from a singular-Jacobian CGE degeneracy, distinct from Pattern C. May be inherent (formulation change → Epic 5).

## Unknown 6.1: Is the singularity a redundant market-clearing row, a missing numéraire fix, or a PATH option — i.e., is it fixable in-sprint?

### Priority

**Critical** — This determines whether camcge is a Sprint 28 +1 Solve or a documented "inherent CGE degeneracy → Epic 5" finding. CGE models are classically singular at the Walras-law row; the fix (numéraire fix / redundant-row drop) must preserve the economic solution, or it's not a fix.

### Assumption

The singularity is a standard CGE Walras-law redundancy (one market-clearing row is linearly dependent), fixable by a price-numéraire normalization or a redundant-row drop that preserves the economic solution — **not an inherent formulation defect.**

### Research Questions

1. Which row(s) does the PATH listing's basis-singularity report flag?
2. Does a Jacobian rank check at the NLP point confirm a single redundant row (Walras' law)?
3. Does fixing a price numéraire (or dropping the redundant row) yield MODEL STATUS 1 with the correct economic solution?
4. Is this a general CGE issue affecting korcge/quocge too, or camcge-specific?

### How to Verify

1. Read the camcge PATH listing's basis-singularity / dependency report.
2. Compute the Jacobian rank at the NLP point; identify the dependent row.
3. Prototype a numéraire fix; check MODEL STATUS + economic-solution match.

### Risk if Wrong

- **Inherent degeneracy:** camcge cannot solve as-is → documented Epic-5 finding; the +1 Solve is lost.
- **Numéraire fix changes the solution:** not a valid fix → re-scope.

### Estimated Research Time

1.5 hours (PATH listing + Jacobian rank check)

### Owner

AD/KKT engineer + CGE-modeling reference

### Verification Results

✅ **Status:** VERIFIED (baseline / bucket-provenance aspect only — the fix-surface aspect is owned by Tasks 5/6)

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** camcge is `model_infeasible` at Sprint 28 Day 0 — a **bucket-forward** move banked in Sprint 27 (S27 Day-0 `path_syntax_error` → #1381 Pattern C Phase B cleared the syntax error → Locally Infeasible / singular Jacobian). The projected Priority-6 Solve delta is **conditional** (may be inherent CGE degeneracy).
**Evidence:** committed Day-13 `gamslib_status.json` (`camcge.mcp_solve.outcome_category = model_infeasible`); `docs/issues/ISSUE_1330` round-3 singular-Jacobian diagnosis; BASELINE_METRICS.md §2 row + §3 row P6.
**Decision:** camcge Solve carried as **conditional** (not tallied as firm); if it stays infeasible it is bucket-forward progress, not target credit. Whether the singularity is fixable in-sprint is the Task-6 hypothesis-validation.


**— Task 6 (REPLAN risk assessment — PR16):**

- **Task 6 outcome:** 🟡 PARTIALLY VERIFIED (design scope)
- **Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- **Date:** 2026-06-11
- **Findings:** Track C designs the singular-row identification: (C1) PATH listing basis-singularity report; (C2) Jacobian rank check at the NLP point (single redundant Walras row vs higher-dimensional degeneracy); (C3) prototype a price-numéraire / redundant-row fix and check MS 1 **+ economic-solution preservation**; (C4) generality on korcge/quocge. Sprint 27 already found the KKT structurally correct (residual ≈ 0) and the failure PATH-side.
- **Evidence:** PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track C; ISSUE_1330 round-3.
- **Decision:** **PROCEED** if a single redundant row + a solution-preserving numéraire fix; **REPLAN to an Epic 5 observation** otherwise. camcge +1 Solve conditional. Budget at risk ~8–14h.

---

## Unknown 6.2: Is camcge still `model_infeasible` at Sprint 28 Day 0 (not self-recovered or re-bucketed)?

### Priority

**Medium** — The baseline (Task 2) must confirm camcge's Day-0 bucket. If a Sprint 27 late fix shifted it, the Priority-6 scope changes.

### Assumption

camcge remains `model_infeasible` at Sprint 28 Day 0, matching the Sprint 27 Day-10/Day-13 retest buckets.

### Research Questions

1. Does the Day-0 baseline retest reproduce camcge `model_infeasible`?
2. Has any Sprint 27 closeout change shifted camcge's emit or bucket?

### How to Verify

1. Day-0 baseline run (Task 2); confirm camcge bucket.
2. Diff `camcge_mcp.gms` against the committed Sprint 27 golden.

### Risk if Wrong

- **Re-bucketed:** Priority-6 scope changes → re-plan camcge before Day 1.

### Estimated Research Time

0.5 hours (baseline confirmation, folded into Task 2)

### Owner

Sprint planning

### Verification Results

✅ **Status:** VERIFIED — camcge Day-0 bucket confirmed

**Verified by:** Task 2 (Bucket-Provenance Baseline + Projection Discipline)
**Date:** 2026-06-10
**Findings:** Confirmed: camcge is `model_infeasible` at Sprint 28 Day 0, matching the Sprint 27 Day-10/Day-13 retest buckets — no self-recovery or re-bucketing. No Sprint 27 closeout change shifted its emit (no `src/`/`scripts/` diff since the Day-13 close `68be9cca`).
**Evidence:** committed Day-13 `gamslib_status.json` (`camcge.mcp_solve.outcome_category = model_infeasible`); `git diff 68be9cca..HEAD -- src/ scripts/` empty; BASELINE_METRICS.md §2 row.
**Decision:** Priority-6 scope is unchanged — camcge stays the Priority-6 target. Fully resolved by Task 2 (pure baseline question).


**— Task 6 (REPLAN risk assessment — PR16):**

- **Task 6 outcome:** ✅ VERIFIED
- **Verified by:** Task 6 (Diagnosis-Heavy Track REPLAN Risk Assessment)
- **Date:** 2026-06-11
- **Findings:** Re-confirmed for the assessment: camcge is `model_infeasible` at Sprint 28 Day 0 (Task 2 baseline holds; no `src/`/`scripts/` change since the Day-13 close). Priority-6 scope is unchanged; the *fixability* (not the bucket) is the open 6.1 question that Track C decides.
- **Evidence:** Task 2 baseline (committed DB) + PRIORITY_4_5_6_REPLAN_RISK_ASSESSMENT.md Track C.
- **Decision:** Day-0 bucket confirmed (the empirical part); the PROCEED/REPLAN fork is owned by 6.1/Track C.

---

# Category 7: Sprint 27 Lower-Priority Cleanups (#1374, #1400, #1385)

Priority 7 workstream — small, well-understood cleanups, each with a coupling risk to scope before implementation.

## Unknown 7.1: Is the #1374 robot `.l` second-shape dedup isolatable from the Sprint 27 dominant-`.fx`-shape fix?

### Priority

**High** — Sprint 27 fixed the dominant `.fx`-restore duplicate-init shape; robot's `.l` denominator/override second shape was deferred. If the `.l` dedup shares the `fx_to_l_override` path with the landed fix, a naive change could regress the dominant shape.

### Assumption

The robot `.l` second shape (`rho.l('h0') = 4.5;` emitted by both the denominator-init block and the `fx_to_l_override`) is dedup-able at emit time, isolated from the Sprint 27 `.fx`-restore fix.

### Research Questions

1. Where is robot's `rho.l('h0')` emitted twice — which two passes?
2. Does the dedup share code with the Sprint 27 dominant-shape fix (`emit_gams.py` Variable Bounds + suppressed-fx restore)?
3. Does a robot-only gate avoid touching the `.fx`-restore path?

### How to Verify

1. Day-0 trace: locate both robot `rho.l` emission sites.
2. Confirm the dedup gate is independent of the Sprint 27 fix; regenerate `robot_mcp.gms`.

### Risk if Wrong

- **Coupled paths:** the dedup regresses the `.fx`-restore fix → +1–2h + re-verify the Sprint 27 models (otpop/dinam).

### Estimated Research Time

1 hour (Day-0 trace of both emission sites)

### Owner

Emit engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 7.2: Where is the #1400 second path leak (the `message`-field captured-warning text)?

### Priority

**Medium** — Sprint 27 fixed `mcp_file_used` (`_repo_relative_path`); the second leak is absolute paths embedded in captured WARNING text in the `message` field (e.g., mine's `pr` warning). The relativization must target the warning-capture path, distinct from the already-fixed field.

### Assumption

The second leak is in the warning-capture path that writes `…/src/…py:NNN` (and possibly source-file absolute paths) into `gamslib_status.json`'s `message` field; it can be relativized by reusing `_repo_relative_path` (or an equivalent) at the capture site.

### Research Questions

1. Which code path captures the warning text into the `message` field?
2. Are the absolute paths source-file paths, src-module paths, or both?
3. Does a single relativization at the capture site cover all `message`-field leaks (audit `gamslib_status.json`)?

### How to Verify

1. Audit `gamslib_status.json` for absolute-path substrings in `message` fields.
2. Trace the warning-capture path; identify the relativization site.

### Risk if Wrong

- **Multiple leak sources:** more than one site to relativize → +0.5–1h.

### Estimated Research Time

0.75 hours (DB audit + capture-path trace)

### Owner

Pipeline/scripts engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 7.3: Must the #1385 runtime-guard equation-body re-emit and the `J_gᵀ·lam` cross-terms land atomically?

### Priority

**Medium** — Sprint 27 deferred the srpchase runtime-guard eq-body re-emit + the `J_gᵀ·lam` cross-terms together (re-emit without cross-terms = inconsistent MCP). If they're genuinely atomic, a partial landing must be avoided.

### Assumption

The runtime-guard equation-body re-emit (`src/kkt/stationarity.py`) and the `J_gᵀ·lam` cross-terms are one atomic unit — landing the re-emit without the cross-terms produces an inconsistent MCP, so they ship together.

### Research Questions

1. Does the re-emit change the equation body in a way that *requires* the cross-terms to stay consistent?
2. Is the cross-term work scoped (srpchase-only) or broader?
3. Can the combined change be verified with the KKT-residual harness on srpchase?

### How to Verify

1. Hand-derive srpchase's runtime-guarded stationarity; confirm the re-emit ⟺ cross-term coupling.
2. Estimate the combined change size; flag if the cross-terms prove larger than a cleanup (→ re-scope).

### Risk if Wrong

- **Larger than a cleanup:** #1385 exceeds the Priority-7 budget → re-scope to a dedicated track.

### Estimated Research Time

0.75 hours (hand-derivation + coupling confirmation)

### Owner

AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 8: Infrastructure — Golden-Staleness Sweep + CI Check (#PR26)

Priority 8 workstream — build a check that regenerates every translating model's golden and fails if it differs from the committed artifact (modulo an allowlist). Addresses Sprint 27 retro §"What We'd Do Differently #3".

## Unknown 8.1: How large is the current golden drift, and how big is the known-failing/non-deterministic allowlist?

### Priority

**High** — The one-time corpus-refresh commit scope and the check's allowlist depend on the actual drift inventory. If drift is widespread (beyond cesam/fawley/korcge/dinam), the refresh commit is larger and the CI check needs careful allowlisting to avoid false failures.

### Assumption

Golden drift is limited to a small set (cesam/fawley/korcge/dinam + a few presolve goldens), and the allowlist (non-translating + non-deterministic models) is small and enumerable.

### Research Questions

1. How many of the 135 translating models' goldens differ from current emit when regenerated?
2. Which models must be allowlisted (non-translating, license-gated, or non-deterministic)?
3. Is the drift purely from known Sprint 27 staleness, or are there surprises?

### How to Verify

1. Regenerate every translating model's golden; diff against the committed artifact; tabulate drift.
2. Enumerate the allowlist from the failure buckets (path_solve_license, translate-fails, etc.).

### Risk if Wrong

- **Widespread drift:** the refresh commit + allowlist grow → +1–2h; the check needs more allowlist maintenance.

### Estimated Research Time

1.5 hours (corpus regen + diff tabulation)

### Owner

Pipeline/CI engineer

### Verification Results

✅ **Status:** VERIFIED

**Verified by:** Task 7 (Golden-Staleness Drift Audit + CI-Check Design)
**Date:** 2026-06-11
**Findings:** Drift audit run over all 164 committed goldens (regenerate via the pipeline emit `python -m src.cli <raw> -o <out> --quiet` [+`--nlp-presolve`], byte-diff). **Result: 154 CLEAN, 4 DRIFTED, 6 allowlist.** The 4 drifted are **all presolve variants** — `camshape`/`cesam`/`fawley`/`korcge` `_mcp_presolve.gms` (Sprint 27 deliberately didn't sweep them); the 153 plain `*_mcp.gms` goldens are 100% clean/allowlisted. The allowlist is 6 out-of-scope models (3 multi-solve drivers danwolfe/decomp/saras + 3 discrete MIP nemhaus/nonsharp/trnspwl).
**Evidence:** PRIORITY_8_GOLDEN_STALENESS_DESIGN.md §1 (drift inventory) + §2 (allowlist).
**Decision:** One-time refresh commit = the 4 drifted presolve goldens only (small, bounded); allowlist seeded with the 6 out-of-scope models.

---

## Unknown 8.2: On which PR trigger paths should the CI golden-staleness check run, and what is its runtime budget?

### Priority

**Medium** — Running the full-corpus regen on every PR is too slow; the check should trigger only on `src/{ad,kkt,emit,ir}/` changes. The runtime budget must not add unacceptable PR friction (Sprint 27 KU flagged > 5 min/PR as friction).

### Assumption

The check triggers on PRs touching `src/{ad,kkt,emit,ir}/`, regenerates only the affected/translating goldens, and completes within an acceptable CI budget (target < 5 min, or a sampled/incremental mode).

### Research Questions

1. How long does a full-corpus golden regen take in CI (vs the ~4h local full pipeline)?
2. Can the check regen only the models a diff could affect, or must it run the full corpus?
3. What trigger-path filter avoids running on docs-only / test-only PRs?

### How to Verify

1. Time a corpus golden regen (emit-only, no solve) in the CI environment.
2. Design the trigger-path filter + an incremental/sampled mode if full regen is too slow.

### Risk if Wrong

- **Too slow:** the check becomes PR friction → needs an incremental/sampled redesign; +1h.

### Estimated Research Time

1 hour (CI timing + trigger design)

### Owner

Pipeline/CI engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope)

**Verified by:** Task 7 (Golden-Staleness Drift Audit + CI-Check Design)
**Date:** 2026-06-11
**Findings:** CI trigger paths designed (`src/{ad,kkt,emit,ir}/**` + the check/allowlist/workflow files), modeled on `pr19-emit-solve-validation.yml`. Runtime: the local audit found **8 slow-emit models** (clearlak/dinam/ferts/ganges/gangesx/indus/tabora/turkpow, >240 s each; ganges/gangesx ~minutes) that dominate a full-corpus regen — serially this exceeds the 5-min friction threshold. Mitigation designed: parallel regen (≈6 workers, wall-clock ≈ slowest single model) + a changed-emit-subset fallback on PRs with a nightly full sweep. The CI-environment timing itself is an in-sprint measurement.
**Evidence:** PRIORITY_8_GOLDEN_STALENESS_DESIGN.md §4 (interface) + §5 (CI integration); §1 slow-emit list.
**Decision:** CI runs report-mode in parallel on `src/{ad,kkt,emit,ir}/` PRs; fall back to the changed-emit subset + nightly sweep if the parallel full regen nears 5 min (confirm timing in-sprint).

---

## Unknown 8.3: Is the golden regeneration determinism-clean under the PR12 guard?

### Priority

**Low** — The check's regenerate-diff logic depends on emit being byte-identical across runs. Sprint 27 confirmed determinism (3× PYTHONHASHSEED byte-identical), so the risk is low, but the check must not flap on non-determinism.

### Assumption

Golden regeneration is byte-identical across runs (PR12 determinism holds), so the check produces stable diffs with no false positives from non-determinism.

### Research Questions

1. Does a back-to-back golden regen produce byte-identical output for every translating model?
2. Are there any models with residual non-determinism that must be allowlisted?

### How to Verify

1. Regenerate the corpus twice (different PYTHONHASHSEED); diff the two regens.
2. Flag any non-byte-identical model for the allowlist.

### Risk if Wrong

- **Non-determinism:** the check flaps → allowlist the model + file a determinism bug; minor.

### Estimated Research Time

0.5 hours (double-regen diff, reuses Task 8.1 output)

### Owner

Pipeline/CI engineer

### Verification Results

✅ **Status:** VERIFIED

**Verified by:** Task 7 (Golden-Staleness Drift Audit + CI-Check Design)
**Date:** 2026-06-11
**Findings:** Regeneration is determinism-clean. Spot-check: 8 representative models (abel, trnsport, launch, qdemo7, cesam2, korcge, mine, camshape) regenerated under `PYTHONHASHSEED=0` vs `42` → **byte-identical for all 8**, matching the Sprint 27 Day-13 full-pipeline PR12 result (byte-identical ×3 seeds).
**Evidence:** PRIORITY_8_GOLDEN_STALENESS_DESIGN.md §3 (determinism).
**Decision:** The check treats any regen≠committed diff as genuine drift, not seed noise; `--fix` re-emits twice and asserts byte-identity before overwriting.

---

# Category 9: Infrastructure — KKT-Residual Verification Harness (PR27)

Priority 9 workstream — formalize the GDX warm-from-good-optimum experiment as `scripts/diagnostics/kkt_residual.py`. Front-loaded (Days 1–3) so it accelerates the carryforward diagnoses (P1/P2/P5).

## Unknown 9.1: What is the dual-transfer mechanism for inequality multipliers that became `comp_*` equations?

### Priority

**Critical** — The harness's whole value is reporting whether the NLP KKT point satisfies the emitted stationarity, which requires transferring the NLP's duals into the MCP multipliers. Inequality multipliers become `comp_*` equations (not plain variables), and bounds multipliers (piL/piU) are recovered from `.m`. If the transfer is wrong, every harness verdict (used by P1/P2/P5) is unreliable — this is foundational tooling.

### Assumption

The harness can transfer NLP constraint/bound marginals into the MCP multiplier variables by generalizing the Sprint 27 Day-9 pattern (load `.m` marginals into parameters, then into the `comp_*`/multiplier variables), covering nu_* (equalities), lam_* (inequalities → `comp_*`), and piL_*/piU_* (bounds).

### Research Questions

1. How does the emit name and structure each multiplier class (nu/lam/piL/piU), and how do inequalities map to `comp_*` equations?
2. Can the harness reuse the emit's multiplier↔equation correspondence (`src/kkt/`, `src/emit/emit_gams.py`) to drive the transfer automatically?
3. How are piL/piU recovered from `.m` at the solution (sign conventions)?
4. Does the `--nlp-presolve` machinery already transfer most duals (so the harness can reuse it)?

### How to Verify

1. On a known-good case (e.g., launch, where 2257.80 was proven a valid KKT point in Sprint 27), build the transfer and confirm the *constraint* rows have residual ≈ 0 (duals consistent).
2. Cross-check against the Sprint 27 Day-9 `pwl_m`/`pwu_m` manual workaround — the harness must generalize it.
3. Validate on camshape (where the §4.6 10-symbol warm-start is documented).

### Risk if Wrong

- **Bad dual transfer:** the harness gives false Case-(b) residuals → every carryforward diagnosis built on it (P1/P2/P5) is compromised; this is the highest-leverage tooling risk.

### Estimated Research Time

2 hours (multiplier-mapping design + known-good validation)

### Owner

AD/KKT + diagnostics engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the dual-transfer mechanism is fully *designed*; empirical validation on launch/camshape runs when the harness is built in-sprint.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** Designed the dual transfer (DESIGN §2): `nu_<eq>` ← NLP `eq.m` (free); `lam_<eq>` ← `eq.m` sign-normalized to the emitted `=g=`/`=l=` orientation (paired with `comp_ineq`); `piL_<v>`/`piU_<v>` ← `v.m` at active bounds (`v.l≈v.lo`/`v.l≈v.up`). The inequality→`comp_*` case generalizes the Sprint 27 Day-9 `pwl_m`/`pwu_m` parameter-load by driving it from `build_complementarity_pairs` (`comp_ineq` keyed by eq, `comp_bounds_lo`/`_up` keyed by `(var,indices)`). A constraint-row consistency self-check is designed to run first — a non-zero *constraint* residual would report `dual_transfer_inconsistent`, never a false Case-b.
**Evidence:** DESIGN §2 (Dual-Transfer Mechanism) + the reuse of `src/kkt/naming.py` + `src/kkt/complementarity.py` + the `_emit_nlp_presolve` primal warm-start.
**Decision:** The harness drives the transfer from the emitter's own multiplier↔equation map; a validation-against-known-cases *plan* (launch Case a + camshape Case b, DESIGN §7) runs when the harness is built.

---

## Unknown 9.2: What is the Case-(a/b/c) verdict logic and its residual thresholds?

### Priority

**High** — The harness must mechanically classify Case a (match), Case b (emit bug — residual ≠ 0 at the NLP KKT point), Case c (non-convexity — residual ≈ 0 but PATH diverges). Wrong thresholds → misclassification → a carryforward gets the wrong fix path (emit-fix vs warm-start).

### Assumption

A per-row stationarity/complementarity residual with a tolerance (~1e-6, tunable) cleanly separates Case b (some row exceeds tol) from Case c (all rows within tol but cold PATH diverges), with the max-residual row reported as the prime suspect.

### Research Questions

1. What residual tolerance distinguishes a genuine emit bug from numerical noise at the NLP optimum?
2. How does the harness detect Case c (residual clean but PATH diverges from cold start) — does it need a cold-solve comparison?
3. What does the output report (per-row table, verdict, max-residual row)?

### How to Verify

1. Calibrate the tolerance on Sprint 27 known cases: camshape (Case b, INFES ≈ 396 → clearly > tol), launch (Case a, residual ≈ 0), a known non-convex model (Case c).
2. Confirm the verdict logic reproduces the Sprint 27 manual classifications.

### Risk if Wrong

- **Misclassification:** a Case-b emit bug treated as Case-c non-convexity (or vice versa) → wrong fix path; +2–4h per affected carryforward.

### Estimated Research Time

1 hour (threshold calibration on known cases)

### Owner

AD/KKT + diagnostics engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the verdict logic + `tol=1e-6` are *designed*; threshold calibration on the Sprint 27 cases runs when the harness is built in-sprint.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** Verdict logic (DESIGN §3): **Case a** = `max|r|≤tol` AND cold PATH reaches the NLP optimum; **Case b** = `max|r|>tol` (emit bug; the max-residual row is the prime-suspect term); **Case c** = `max|r|≤tol` but cold PATH diverges (non-convexity → warm-start, not an emit fix). Default `tol=1e-6`, `--tol`-tunable, with calibration *targets* from Sprint 27 ground truth (to be reproduced when the harness runs): camshape `stat_r('i1')`≈396 ≫ tol (b) vs cclinpts max|r|=5e-8 (c). Case-c detection needs the cold-start comparison.
**Evidence:** DESIGN §3 (verdict table + threshold calibration) + §7 (launch a / camshape b / cclinpts c validation plan).
**Decision:** Output is a per-row residual table + verdict + max-residual row; `tol=1e-6` cleanly separates the camshape-b from the cclinpts-c calibration points.

---

## Unknown 9.3: Can the harness solve the NLP (or load a provided GDX) and warm-start the MCP within a reasonable runtime per model?

### Priority

**Medium** — The harness is a per-model diagnostic; if it's too slow (e.g., re-solving a slow NLP like ganges at ~8min), it's impractical as a Phase-0 tool. A `--gdx` option to load a pre-solved solution mitigates this.

### Assumption

The harness runs in a practical per-model time by accepting a pre-solved GDX (`--gdx`) to skip the NLP solve, falling back to solving the NLP only when no GDX is provided.

### Research Questions

1. What is the runtime for the harness on a fast model (mine/camshape) vs a slow one (kand/ganges)?
2. Does the `--gdx` load path correctly transfer primals + duals from an existing solution?
3. Is `iterlim=0` (or a residual-only evaluation) sufficient to get the residual without a full MCP solve?

### How to Verify

1. Prototype the harness on mine + camshape; time it.
2. Confirm the `--gdx` path reproduces the same residual as the solve-NLP path.

### Risk if Wrong

- **Too slow:** the harness is impractical for slow models → must require `--gdx` for those; minor design adjustment.

### Estimated Research Time

1 hour (runtime prototype on 2 models)

### Owner

AD/KKT + diagnostics engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope) — the `--gdx` design answers the runtime concern, but the runtime + residual-parity *measurements* are an in-sprint acceptance check, not performed here.

**Verified by:** Task 4 (Design the KKT-Residual Verification Harness)
**Date:** 2026-06-11
**Findings:** `--gdx <solution.gdx>` loads a pre-solved NLP solution (primals + marginals) to skip the NLP solve — essential for slow NLPs (kand/ganges ~8 min); the no-`--gdx` path solves the NLP first and suits fast models (mine/camshape, seconds–low minutes). The residual evaluation itself is `iterlim=0` (PATH evaluates the start point without iterating), near-instant. The `--gdx` and solve-NLP paths must produce the *same* residual on a fast model (the acceptance check; a mismatch means the GDX load drops primals/duals).
**Evidence:** DESIGN §1 (CLI / pipeline) + §8 (runtime / `--gdx` mitigation).
**Decision:** `--gdx` is the practical path for slow models; the solve-NLP path for fast ones — the harness stays practical as a per-model Phase-0 tool.

---

# Category 10: Infrastructure — Embedded-NLP-Divergence Detector + AD Cross-Term Property Tests

Priority 10 workstream — a detector for the `$onMultiR` re-run bug class + property tests guarding the cross-term defect class. Addresses Sprint 27 retro §"What Went Well #2".

## Unknown 10.1: Can the divergence detector reliably compare the embedded-NLP objective to the standalone-NLP objective, and would it have caught #1378 + #1424?

### Priority

**High** — The detector's value is catching the "embedded NLP diverges from standalone" bug class at translate time. If it can't reliably extract both objectives (or has too many false positives from legitimate differences), it's not trustworthy as a CI gate.

### Assumption

For each `--nlp-presolve` model, the detector can extract the embedded-NLP objective (from the `$include`d pre-solve) and the standalone-NLP objective, flag divergence beyond tolerance, and would have flagged #1378 (launch double-apply) and #1424 (camshape subset corruption) at translate time.

### Research Questions

1. How does the detector extract the embedded-NLP objective from the presolve emit vs the standalone NLP solve?
2. What tolerance separates a real divergence from numerical noise?
3. Are there models where embedded ≠ standalone for a *legitimate* reason (the false-positive allowlist)?
4. Replaying #1378 + #1424 pre-fix: does the detector flag them?

### How to Verify

1. Prototype the detector; run it on the corpus presolve models.
2. Replay the #1378 + #1424 pre-fix states; confirm the detector flags both.
3. Enumerate any legitimate-divergence models for the allowlist.

### Risk if Wrong

- **Unreliable / false-positive-heavy:** the detector can't be a CI gate → demote to an advisory script; reduced leverage.

### Estimated Research Time

1.5 hours (detector prototype + #1378/#1424 replay)

### Owner

Diagnostics/CI engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope)

**Verified by:** Task 8 (Divergence Detector + AD Cross-Term Property-Test Catalog Design)
**Date:** 2026-06-11
**Findings:** Detector designed: it extracts the **embedded** NLP objective via a probe `Display <objvar>.l` inserted right after the `$offMulti` that closes the `$include` block (post-include, pre-dual-transfer, pre-MCP-Solve), and the **standalone** NLP objective from a direct `gams <raw>.gms` solve; flags when the relative objective gap > `tol` (default 1e-4) or the embedded model status is worse (infeasible). Validated *by design* against the past wins: #1378 launch (embedded 2604.01 vs standalone 2257.80 ≈ 13% → FLAG) and #1424 camshape (embedded infeasible/area 5.009 vs standalone 4.2841 MS 1 → model-status FLAG). The pre-fix-replay confirmation is the in-sprint acceptance test.
**Evidence:** PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md Part 1 (interface + extraction + validation table).
**Decision:** Detector + allowlist + CI gate on the presolve emit path designed; the #1378/#1424 replay is the in-sprint acceptance run.

---

## Unknown 10.2: Which recurring AD cross-term shapes must the property-test catalog cover, and can each be expressed as a small hand-checkable synthetic model?

### Priority

**High** — The property tests' value is systematically guarding the #1224/#1388/#1390 cross-term defect class. If the catalog misses a recurring shape, the defect class stays under-guarded; if a shape can't be reduced to a small synthetic model with a hand-derived KKT, the test isn't trustworthy.

### Assumption

The recurring cross-term shapes (single-axis offset Sum, self-alias Sum, cross-set alias Sum, parameter-valued offset, interior+edge convex-combination, tree-predicate-conditioned aliased Sum) can each be expressed as a small synthetic GAMS model with a hand-derived stationarity cross-term the emit must match.

### Research Questions

1. Is the catalog of ≥ 6 shapes complete for the #1224/#1388/#1390 defect class (and the Sprint 24–27 history)?
2. Can each shape be reduced to a minimal hand-checkable model?
3. What does each property test assert (emit cross-term == hand-derived shape)?
4. Where do the tests live and how do they wire into CI (`@pytest.mark.unit`)?

### How to Verify

1. Enumerate the shapes from the carryforward issue docs + `docs/research/multidimensional_indexing.md` + `nested_subset_indexing_research.md`.
2. Draft one minimal synthetic model per shape + its hand-derived cross-term.

### Risk if Wrong

- **Incomplete catalog:** the defect class stays under-guarded → a future cross-term bug slips; the property tests under-deliver.

### Estimated Research Time

1.5 hours (shape enumeration + synthetic-model sketches)

### Owner

AD/KKT + diagnostics engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (design scope)

**Verified by:** Task 8 (Divergence Detector + AD Cross-Term Property-Test Catalog Design)
**Date:** 2026-06-11
**Findings:** Cataloged **6 cross-term shapes**, each with a minimal synthetic model + hand-derived `stat_*` cross-term: (1) single-axis offset Sum, (2) self-alias Sum, (3) cross-set alias Sum (#1398), (4) parameter-valued offset (#1224), (5) interior+edge convex-combination (#1388), (6) tree-predicate-conditioned aliased Sum (#1390). Shapes 4/5/6 are the literal #1224/#1388/#1390 defect shapes; 1/2/3 are the foundational offset/alias/cross-set recurrences. Shape 1 was prototyped — the emit produced the hand-derived inverted-offset form exactly.
**Evidence:** PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md Part 2 (catalog table) + the shape-1 prototype.
**Decision:** The catalog covers the #1224/#1388/#1390 defect class; additional shapes (e.g. #1335 `card(t)-ord(t)`) appendable in-sprint.

---

## Unknown 10.3: Will the AD cross-term property tests be byte-stable and fast enough to run in CI on every PR?

### Priority

**High** — Property tests that are slow or flaky won't survive as a CI gate. The synthetic models must emit deterministically and quickly so the suite runs on every PR (unlike the full-corpus golden check, which is path-gated).

### Assumption

The synthetic property-test models are tiny (a handful of variables/equations), emit deterministically, and run in well under a second each, so the full property-test suite adds negligible CI time and runs on every PR.

### Research Questions

1. How fast does the emit pipeline run on a minimal synthetic model?
2. Are the synthetic-model emits byte-stable across runs (PR12)?
3. Does the assertion compare against a hand-derived string, an AST shape, or a golden snippet?

### How to Verify

1. Prototype one property test; time it; double-run for byte-stability.
2. Confirm the assertion form is robust to incidental formatting.

### Risk if Wrong

- **Slow/flaky:** the suite can't run on every PR → demote to a nightly/path-gated job; reduced leverage.

### Estimated Research Time

1 hour (prototype one test + timing/stability check)

### Owner

AD/KKT + diagnostics engineer

### Verification Results

✅ **Status:** VERIFIED

**Verified by:** Task 8 (Divergence Detector + AD Cross-Term Property-Test Catalog Design)
**Date:** 2026-06-11
**Findings:** Property tests are byte-stable and fast. Prototyped shape 1 (a tiny synthetic offset-Sum model): emit is **byte-identical on re-emit** (PR12-clean), and the per-model emit is sub-second in-process (the 4.38 s measured for a `python -m src.cli` subprocess is interpreter+import startup, which the in-process emit API the test suite already uses avoids). The 6-test suite adds negligible CI time and runs inside the existing `make test` on every PR; committed fixtures run in `--fast` CI too.
**Evidence:** PRIORITY_10_DIVERGENCE_PROPERTY_TESTS_DESIGN.md Part 2 (property-test spec) + the shape-1 timing/byte-stability prototype.
**Decision:** Property tests live in `tests/integration/emit/` with committed synthetic fixtures, use in-process emit + pattern-match assertions, and wire into `make test` (no separate workflow).

---

## Newly Discovered Unknowns (During Sprint 28)

(Populate during sprint execution; migrate into categories post-sprint.)

---

## Confirmed Knowledge (From Sprint 27 and Earlier)

### Carryforward Diagnoses Already Established (Sprint 27)

- ✅ #1224 mine translates after the `src/ir/ast.py` emit-render fix (parameter lead/lag renders natively); the remaining defect is the `stat_x` cross-term inversion (model_infeasible).
- ✅ #1388 camshape is Case (b) (non-inert emit bug, NOT non-convexity) — the §4.6 discriminator from a verified-complete warm-start returned MS5 with `stat_r(i1)` INFES ≈ 396. The #1424 subset co-bug is fixed.
- ✅ #1393 Approach C (`_is_concrete_instance_of`) is **inert** (otpop_mcp.gms byte-identical, no src diff) — the collapse must be at the `stationarity.py` symbolic-collapse path. #1393 and #1335 are confirmed **distinct** fixes.
- ✅ #1387 cclinpts needs **three coupled changes**; the "sign-flip" is a **misdiagnosis** (the `(-1)` is the standard maximize negation `gradient.py:265`). The per-instance offset-enumeration math was residual-verified to 5e-8.
- ✅ #1390 kand's phantom-term collapse is **inert** (MCP stays 195.0 ≠ NLP 2613.0) — the real defect is elsewhere (bal/x stationarity, lag duality, or LP recourse).
- ✅ #1424 (dynamic-subset blanket corruption) landed in Sprint 27 — `_emit_dynamic_subset_defaults` skips model-assigned subsets.

### Diagnostic Tooling Precedent (Sprint 27)

- ✅ The GDX warm-from-good-optimum experiment is the reliable Case-(a/b/c) discriminator (launch, camshape, kand). The Day-9 dual-transfer used parameters `pwl_m`/`pwu_m` for inequality multipliers → `comp_*` — the harness must generalize this.
- ✅ The "embedded NLP diverges from standalone" bug class (`$include` under `$onMultiR`) is real and recurred twice (#1378, #1424).
- ✅ Determinism holds end-to-end (3× PYTHONHASHSEED byte-identical) — the golden-staleness check and property tests can rely on byte-stable emit.

### Process (Sprint 26–27)

- ✅ PR20 Phase 0 acceptance gate is the primary mitigation against alias-AD drift (caught 4 mis-scopes in Sprint 27).
- ✅ PR24: prep-doc fix surfaces are wrong more often than right — treat as Day-0-trace hypotheses.
- ✅ PR25: distinguish bucket-forward moves from genuine Solve/Match gains in projections.
- ✅ PR22 mid-sprint audit script (`changed_emit_artifacts.py`) generates the PR14 review surface from git history.

---

## Template for New Unknowns

When adding unknowns during Sprint 28:

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority

**[Critical/High/Medium/Low]** — [One-line impact]

### Assumption

[State the assumption being made]

### Research Questions

1. [Question 1]
2. [Question 2]
...

### How to Verify

[Test cases, experiments, analysis to validate assumption]

### Risk if Wrong

[Impact if assumption is incorrect]

### Estimated Research Time

[Hours] ([brief description of research activities])

### Owner

[Team/Person responsible]

### Verification Results

🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Before Sprint 28 Day 1:**

1. Review all Critical and High priority unknowns (19 total: 7 Critical + 12 High).
2. Execute verification tests for top unknowns via prep Tasks 2–10 (see Appendix below).
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG).
4. Adjust Sprint 28 scope (PROJECT_PLAN.md or PLAN.md) if major assumptions are wrong — specifically, any of Unknowns 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 9.1 returning WRONG triggers a Priority re-plan / REPLAN-to-Sprint-29 decision during prep.
5. Share findings with the team during sprint planning (Task 10).

**During Sprint 28:**

1. Reference this document daily (especially Critical / High unknowns).
2. Add newly discovered unknowns in the "Newly Discovered" section above.
3. Update verification results as features are implemented.
4. Move resolved items to "Confirmed Knowledge" post-sprint.

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 28 prep tasks verify which unknowns. Prep Task 10 (Plan Sprint 28 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Bucket-Provenance Baseline + Projection Discipline (PR15 + PR17 + PR25) | 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2 | Day-0 baseline confirms each carryforward target's bucket (the "still infeasible/mismatch at Day 0?" research question in each Critical unknown) + the PR25 genuine-gain-vs-bucket-forward classification of each projected delta |
| Task 3: Codify PR24 (Day-0 Traced Fix-Surface) + PR25 | 1.1, 2.1, 3.1, 4.1, 5.1 | Codifies the rule that makes every carryforward fix-surface a Day-0-trace hypothesis (the framing of each Critical fix-surface unknown); PR25 codification governs the Task-2 projection labeling |
| Task 4: Design the KKT-Residual Verification Harness (PR27 / P9) | 9.1, 9.2, 9.3, 1.3, 2.2, 5.1, 5.2 | The harness's own design unknowns (9.1 dual-transfer, 9.2 verdict logic, 9.3 runtime) + the harness as verification instrument for the mine boundary residual (1.3), camshape blast radius (2.2), and the kand localization + dual-transfer (5.1, 5.2) |
| Task 5: Author / Refresh Phase 0 Gates for the Six Carryforwards (PR20 + PR24) | 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 4.2 | Hand-derived KKT shapes + traced-surface + harness-based verification methodology for #1224 (1.1–1.3), #1388 (2.1–2.3), otpop (3.1–3.3), and cclinpts change-1 residual (4.2) |
| Task 6: Diagnosis-Heavy Track REPLAN Risk Assessment (#1387, #1390, camcge; PR16) | 4.1, 4.3, 5.1, 5.2, 5.3, 6.1, 6.2 | Single-model hypothesis-validation + PROCEED/REPLAN for cclinpts anchor (4.1) + warm-start (4.3); kand localization (5.1), dual transfer (5.2), NLP reference (5.3); camcge singular row (6.1) + Day-0 bucket (6.2) |
| Task 7: Golden-Staleness Drift Audit + CI-Check Design (PR26 / P8) | 8.1, 8.2, 8.3 | Drift inventory + allowlist sizing (8.1), CI trigger-path + runtime budget (8.2), determinism-clean confirmation (8.3) |
| Task 8: Divergence Detector + AD Cross-Term Property-Test Catalog Design (P10) | 10.1, 10.2, 10.3 | Detector reliability + #1378/#1424 replay (10.1), cross-term shape catalog (10.2), property-test CI speed/stability (10.3) |
| Task 9: Lower-Priority Cleanups Fix-Surface Analysis (#1374, #1400, #1385) | 7.1, 7.2, 7.3 | robot `.l` dedup isolation (7.1), #1400 second-leak location (7.2), #1385 atomic-landing requirement (7.3) |
| Task 10: Plan Sprint 28 Detailed Schedule | (integrates all) | Sprint 28 14-day schedule + day-by-day prompts; absorbs the PROCEED/REPLAN decisions from Tasks 5/6 and the infra designs from Tasks 4/7/8 |

**Cross-cutting unknowns** (verified across multiple prep tasks):

- **Unknown 1.1** (mine fix surface) — Task 5 authors the Phase-0 gate (hand-derived shape + traced surface), Task 3 codifies the PR24 rule that makes the surface a hypothesis, and Task 2 confirms mine is still `model_infeasible` at Day 0.
- **Unknowns 2.1 / 3.1 / 4.1 / 5.1 / 6.1** (the carryforward fix surfaces) — each is cross-verified by Task 2 (Day-0 bucket), Task 3 (PR24 hypothesis framing), and its primary fix/REPLAN task (Task 5 for 2.1/3.1; Task 6 for 4.1/5.1/6.1).
- **Unknown 5.1** (kand localization) — Task 4 designs the harness that performs the localization, Task 6 makes the PROCEED/REPLAN decision from its output.
- **Unknown 9.1** (harness dual-transfer) — primarily Task 4 (design); its correctness is foundational for the Task-5/Task-6 verification methodologies that consume the harness (so it is validated against the Sprint 27 known-good launch/camshape cases).

**Coverage:** All 29 Sprint 28 prep-time unknowns are assigned to at least one prep task. Most Critical and High-priority unknowns are assigned to the task that will act on the findings (e.g., Task 6 verifies the diagnosis-heavy Category 4/5/6 unknowns AND its findings drive Task 10's schedule allocation + the Sprint 29 REPLAN exits).

**Carryforward from Sprint 27** (now informing Sprint 28 prep):

- All 28 Sprint 27 prep unknowns were resolved (see `SPRINT_27/SPRINT_RETROSPECTIVE.md` §"KU Coverage Summary"). The Sprint 28 unknowns are net-new, derived from the §"Sprint 28 Recommendations" + the diagnostic/CI tooling tracks.

---

**Document Created:** 2026-06-09
**Last Updated:** 2026-06-09
**Total Unknowns:** 29
**Owner:** Sprint 28 Planning Team
**Review Frequency:** Daily during Sprint 28
