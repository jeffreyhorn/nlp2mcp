# Sprint 27 Known Unknowns

**Created:** 2026-05-26
**Status:** Active — Pre-Sprint 27
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 27 — Sprint 26 Carryforward (Pattern C Phase B + Phase A Gate Tightening + AD Architectural Redesigns + comp_up Subset/Superset + launch PATH-numerics + #1224 mine + Day 6 close-and-refile + #1400 pipeline path leak + #1374 emit duplicate-init). Codifies Sprint 26 retrospective process recommendations PR20 (Phase 0 acceptance gate), PR21 (prep-task end-to-end emit verification), PR22 (mid-sprint audit script), PR23 (CI-workflow PR self-review checklist).

---

## Overview

This document identifies all assumptions and unknowns for Sprint 27 features **before** implementation begins. Sprint 27 is the **fourth consecutive sprint** targeting alias-aware differentiation correctness (after S24's launch attempt, S25's narrow-gate Pattern C fix, and S26's Phase A consolidated builder + Pattern C Phase B reclassification). The central new prep activity is **Phase 0 acceptance-gate codification pre-Day-0** (Task 2 of `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md`, codifying Sprint 26 retrospective PR20). Sprint 27 inherits 14 issues labeled `sprint-27` (2 net-new from Sprint 26 Day 13 — #1398 Phase A gate side-effect on 15 models, #1400 pipeline absolute-path leak — plus 7 net-new from Sprint 26 reclassifications + close-and-refile across Days 1–9, 1 reopened in-place on Day 13, and 4 pre-existing carryforward).

**Sprint 27 Scope** (per `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 27 entry, Weeks 19–20, 14-day sprint at ≤ 12h/day):

1. **Priority 1: Phase A Gate Predicate Tightening (#1398)** — Tighten Phase A's `_find_pattern_c_alias_sum` gate predicate that fires too broadly on 15 affected models (qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow)
2. **Priority 2: Pattern C Phase B Redesign (#1381)** — Build consolidated multiplier term from source Sum body structure, intercepting before element-to-set substitution
3. **Priority 3: AD Architectural Redesigns (#1390, #1385, #1393 + #1335)** — Three architectural redesigns targeting different AD pipeline subsystems
4. **Priority 4: launch PATH-Numerics Investigation (#1378)** — Numerical-conditioning problem on Phase A's mathematically-correct emit
5. **Priority 5: comp_up Subset/Superset Workstream (#1356 fawley + #1357 otpop)** — Domain-widening fix in `src/kkt/complementarity.py` + `src/emit/emit_gams.py`
6. **Priority 6: #1224 mine ParamRef IndexOffset** — `src/ad/index_mapping.py` UserWarning fix
7. **Priority 7: Day 6 Close-and-Refile Carryforwards (#1387 cclinpts + #1388 camshape)** — Fix-surface analysis + implementation OR Sprint 28 carryforward filing
8. **Priority 8: Pipeline Absolute-Path Leak Fix (#1400)** — `scripts/gamslib/run_full_test.py:899` `mcp_file_used` assignment serializes an absolute path (the only CONFIRMED leak source). The original Sprint 26 CHANGELOG / PROJECT_PLAN.md attribution of a second leak source to `warnings.formatwarning` is INCORRECT (`grep -lE "warnings\." scripts/gamslib/*.py` returns nothing). The Priority 8 workstream / #1400 implementation must run a direct AUDIT of `gamslib_status.json` for absolute-path substrings (e.g., `grep -E "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json`) to identify any additional leak fields rather than speculate about candidate sources. (Priority 8 has no dedicated prep task — Task 8 in this PREP_PLAN is the #1387/#1388 fix-surface analysis, unrelated to #1400.) Note: `solve_mcp()` in `scripts/gamslib/test_solve.py:911` calls `subprocess.run(..., capture_output=True)` but discards stdout/stderr; the error stored in `model["mcp_solve"]["error"]["message"]` is synthesized from parsed `.lst` content, so subprocess stderr is NOT a leak channel.
9. **Priority 9: Emit Duplicate-Init Bugs (#1374)** — Observation-style sweep of regenerated `*_mcp.gms` artifacts
10. **Process Recommendations:** PR20 (Phase 0 acceptance gate codification), PR21 (prep-task end-to-end emit verification template), PR22 (mid-sprint `scripts/sprint_audit/changed_emit_artifacts.py`), PR23 (CI-workflow PR self-review checklist)

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 27 entry (Goal, Components, Deliverables, Acceptance Criteria, Estimated Effort 97–157h, Risk Level HIGH).

**Lessons from Previous Sprints:**

- Sprint 22: 28 unknowns; early preprocessing research saved 20+ hours.
- Sprint 23: 32 unknowns; KU-27 (subset-superset domain) led to a high-impact fix.
- Sprint 24: 26 prep + 6 end-of-sprint KUs (KU-27..KU-32); Lark disambiguation unblocked CI.
- Sprint 25: 27 prep + 4 end-of-sprint KUs (KU-33..KU-36); KU-33 drove Sprint 26 Priority 1 (Pattern C generalization), which itself surfaced the architectural drift now driving Sprint 27 priorities.
- Sprint 26: 26 prep + 3 end-of-sprint KUs (KU-37..KU-39); KU-37 directly drives Sprint 27 Priority 1 (#1398); KU-38 drives Task 6 coordinated-design analysis for Priority 3; KU-39 drives the #1335 approach selection.

**Sprint 26 Key Learning** (from `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" PR20): Sprint 26 Day 1 PR #1379 ("Phase A consolidated zero-offset builder") shipped GREEN through all quality gates (unit + integration + byte-stability) and the 15-model regression surface was only discovered by PR #1399 reviewer-driven retest. The inverse incident (Day 9 PR #1394 #1335 in-place fix) shipped GREEN and was rolled back during PR review when a hand-derived KKT comparison caught a regression. **Both incidents prove unit/integration/byte-stability gates are insufficient to catch alias-AD pipeline architectural-drift regressions; only hand-derived KKT comparison reliably surfaces them.** Sprint 27's PR20 codifies the Phase 0 acceptance gate as a hard rule for any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/`. This is the single highest-value prep activity for Sprint 27.

**Sprint 26 Carryforward KUs** (from `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` §End-of-Sprint Discoveries):

- **KU-37** (Phase A gate overreach surface ≥ 15 models — PR19 widening is the structural mitigation) → directly drives Category 1 (Phase A Gate Tightening) and Category 9 (process — PR19 widening prerequisite)
- **KU-38** (4 close-and-refile share architectural class — coordinated design may be preferable) → drives Category 3 (AD Architectural Redesigns) coordinated-design analysis
- **KU-39** (#1335 has 3 competing approaches, requires selection) → drives Category 3 #1335 approach-selection unknown

---

## How to Use This Document

### Before Sprint 27 Day 1

1. Research and verify all **Critical** and **High** priority unknowns during prep tasks (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases for validation where needed (especially for Phase 0 acceptance-gate derivations).
3. Document findings in the "Verification Results" subsection of each unknown.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 27

1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly-discovered unknowns in the "Newly Discovered" section (migrate into categories post-sprint).
3. Update with implementation findings as work progresses.
4. Flag any assumption that turns out wrong — don't quietly re-scope around it. (Per Sprint 26 retrospective, the Phase A gate-overreach surface was an undeclared scope expansion; Sprint 27 should explicitly file new sprint-27 issues for any surface expansion.)

### Priority Definitions

- **Critical:** Wrong assumption will break a sprint priority or require major re-planning (>8 hours of rework). For Sprint 27, this includes any unknown whose disconfirmation would force one of the 4 architectural redesigns (Priorities 1, 2, 3) to be replanned during execution.
- **High:** Wrong assumption will cause significant rework (4–8 hours).
- **Medium:** Wrong assumption will cause minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 28

**By Priority:**

- Critical: 6 (21%)
- High: 11 (39%)
- Medium: 8 (29%)
- Low: 3 (11%)

**By Category:**

- Category 1 (Phase A Gate Predicate Tightening — #1398): 4 unknowns
- Category 2 (Pattern C Phase B Redesign — #1381): 3 unknowns
- Category 3 (AD Architectural Redesigns — #1390 / #1385 / #1393 + #1335): 5 unknowns
- Category 4 (launch PATH-Numerics Investigation — #1378): 2 unknowns
- Category 5 (comp_up Subset/Superset — #1356 fawley + #1357 otpop): 3 unknowns
- Category 6 (#1224 mine ParamRef IndexOffset): 2 unknowns
- Category 7 (Day 6 Close-and-Refile — #1387 cclinpts + #1388 camshape): 3 unknowns
- Category 8 (Pipeline Absolute-Path Leak Fix — #1400): 2 unknowns
- Category 9 (Process Recommendations — PR20/PR21/PR22/PR23 + #1374 observation): 4 unknowns

**Estimated Research Time:** 28–36 hours (work-item estimates; per-unknown numbers sum higher than the prep-task budget because many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping" for which task verifies which unknowns. The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md`: 31–44h across Tasks 1–11.)

---

## Table of Contents

1. [Category 1: Phase A Gate Predicate Tightening (#1398)](#category-1-phase-a-gate-predicate-tightening-1398)
2. [Category 2: Pattern C Phase B Redesign (#1381)](#category-2-pattern-c-phase-b-redesign-1381)
3. [Category 3: AD Architectural Redesigns (#1390, #1385, #1393 + #1335)](#category-3-ad-architectural-redesigns-1390-1385-1393--1335)
4. [Category 4: launch PATH-Numerics Investigation (#1378)](#category-4-launch-path-numerics-investigation-1378)
5. [Category 5: comp_up Subset/Superset Workstream (#1356 fawley + #1357 otpop)](#category-5-comp_up-subsetsuperset-workstream-1356-fawley--1357-otpop)
6. [Category 6: #1224 mine ParamRef IndexOffset](#category-6-1224-mine-paramref-indexoffset)
7. [Category 7: Day 6 Close-and-Refile Carryforwards (#1387 cclinpts + #1388 camshape)](#category-7-day-6-close-and-refile-carryforwards-1387-cclinpts--1388-camshape)
8. [Category 8: Pipeline Absolute-Path Leak Fix (#1400)](#category-8-pipeline-absolute-path-leak-fix-1400)
9. [Category 9: Process Recommendations (PR20/PR21/PR22/PR23) + Emit Duplicate-Init Bugs (#1374)](#category-9-process-recommendations-pr20pr21pr22pr23--emit-duplicate-init-bugs-1374)
10. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Phase A Gate Predicate Tightening (#1398)

Priority 1 workstream — Sprint 27 highest-leverage priority. Tightens the Phase A `_find_pattern_c_alias_sum` gate predicate that PR #1379 inadvertently broadened in Sprint 26 Day 1, regressing 15 non-target models. Drives KU-37 from Sprint 26 §End-of-Sprint Discoveries.

## Unknown 1.1: Are all 15 #1398-affected models still in non-compare_match buckets at Sprint 27 Day 0?

### Priority

**Critical** — If 1+ models have self-recovered between Sprint 26 Day 13 (final) and Sprint 27 Day 0 (e.g., a Sprint 26 fix has a delayed effect on dependent models), Priority 1's scope shrinks. Conversely, if Day 0 retest surfaces additional affected models, Priority 1's scope expands. Either case forces a re-budget of Priority 1's 10–14h allocation before Day 1.

### Assumption

All 15 models identified in the Sprint 26 Day 13 #1398 sweep (qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow) remain in non-compare_match buckets at Sprint 27 Day 0 baseline, and no additional non-target models exhibit the same gate-overreach pattern.

### Research Questions

1. Does Sprint 27 Day 0 pipeline retest reproduce the exact 15-model bucket set from Sprint 26 Day 13 (final)?
2. Are there models outside the 15 that exhibit the same gate-overreach pattern (e.g., models that translate but produce wrong-but-compiling emit with similar Phase A consolidated-multiplier shapes)?
3. Has any Sprint 26 post-Day-13 fix (PR #1399 review-driven changes, etc.) silently shifted any of the 15 models' bucket?
4. Does the bucket-provenance baseline (Task 3 of PREP_PLAN.md) capture the Sprint 26 Day 13 (final) → Sprint 27 Day 0 transitions cleanly for all 15 models?

### How to Verify

1. Run `.venv/bin/python scripts/gamslib/run_full_test.py` at Sprint 27 Day 0.
2. Diff resulting `gamslib_status.json` against Sprint 26 Day 13 (final) commit version.
3. For each of the 15 models, confirm bucket has not changed; flag any drift.
4. Grep `data/gamslib/mcp/*_mcp.gms` for the Phase A consolidated-multiplier pattern (e.g., `sum(j$(domain_filter), imat(j,i) * nu_<eq>(j))` style) across all 142 in-scope models; cross-reference against the 15 to identify any non-flagged models.

### Risk if Wrong

- **Scope shrinkage (1+ self-recovered):** Priority 1 budget overestimated; potential reallocation of 1–2h to other priorities.
- **Scope expansion (additional affected models):** Priority 1 budget underestimated; potential 2–4h additional verification effort.
- **Drift in Sprint 26 Day 13 (final) → Sprint 27 Day 0 baseline:** Bucket-provenance baseline becomes unreliable, affecting Sprint 27 progress measurement.

### Estimated Research Time

2–3 hours (pipeline retest + bucket-provenance diff + corpus grep)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Sprint 26 → Sprint 27 Bucket-Provenance Baseline + Scope Freeze PR15 + PR17)
**Date:** 2026-05-28

**Findings:** All 15 #1398-affected models present at non-compare_match buckets at Sprint 27 Day 0:

| Model | Sprint 27 Day 0 bucket | Sprint 27 Priority 1 target? |
|---|---|---|
| `qdemo7` | path_syntax_error | ✓ (the +1 firm Solve / +1 firm Match recovery anchor) |
| `egypt` | path_syntax_error | ✓ |
| `ferts` | path_syntax_error | ✓ |
| `shale` | path_syntax_error | ✓ |
| `dinam` | path_syntax_error | ✓ (Phase 0 anchor — 2 distinct shapes) |
| `fawley` | path_syntax_error | ✓ (also Priority 5 #1356) |
| `gangesx` | path_syntax_error | ✓ |
| `turkpow` | path_syntax_error | ✓ |
| `ganges` | translate_timeout | ✓ (machine-variance churn — was path_syntax_error at Sprint 26 Day 13 final, churned forward to translate_timeout at Day 0; also a churn-back vs Sprint 26 Day 0 where it was translate_timeout; still failing) |
| `srpchase` | translate_timeout | ✓ (machine-variance churn — was path_syntax_error at Sprint 26 Day 13 final, churned forward to translate_timeout at Day 0; also a churn-back vs Sprint 26 Day 0 where it was translate_timeout; still failing) |
| `tfordy` | path_solve_license | ✓ (license bucket, not Phase A regression — but in #1398 scope per PR #1399 review surface) |
| `sroute` | path_solve_license | ✓ (same as tfordy) |
| `sambal` | compare_mismatch | ✓ (solve `model_optimal` but `compare_mismatch` — not a Phase A syntax regression) |
| `qsambal` | compare_mismatch | ✓ (same as sambal) |
| `harker` | compare_mismatch | ✓ (same as sambal) |

**Evidence:** Sprint 27 Day 0 baseline retest (BASELINE_METRICS.md §6.2 + §6 tables; raw data in `data/gamslib/gamslib_status.json`).

**Decision:** Priority 1 scope CONFIRMED at 15 models (no self-recoveries, no scope shrinkage). All 15 models remain candidates for the Sprint 27 #1398 Phase A gate-tightening fix per the PROJECT_PLAN.md target. The 2 machine-variance churn models (`ganges`, `srpchase` — Sprint 26 Day 13 final `path_syntax_error` → Sprint 27 Day 0 `translate_timeout`; also churn-backs vs Sprint 26 Day 0 where they were `translate_timeout`) are still failing — just at an earlier pipeline stage — and will return to their Sprint 26 Day 13 final `path_syntax_error` bucket once translate completes on a faster runner; the fix surface remains the same as for the path_syntax_error cohort.

**Bonus finding (not in original Unknown 1.1 scope but surfaced by retest):** Sprint 27 Day 0 also exhibits the same 3-model machine-variance churn pattern as Sprint 26 Day 0 (clearlak/ganges/srpchase vs Sprint 26 Day 0's clearlak/ganges/turkpow; the exact boundary-crosser identity shifts run-to-run based on machine load, but the count is stable at ~3). Sprint 27 Day-N retests should expect this churn and use bucket provenance (per PR17 / BASELINE_METRICS.md §6.3) to distinguish fix-driven from churn-driven transitions.

**Cross-reference (Task 4):** Task 4 (#1398 widened-scope verification + anchor-model audit) re-verified all 15 models against `data/gamslib/mcp/*_mcp.gms` regenerated emit on 2026-05-28 and confirmed no bucket drift since Task 3. Per-model anchor mapping recorded in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §2.

---

## Unknown 1.2: Do the 8 Phase 0 anchor models (launch + qdemo7 + ferts + sambal + ganges + sroute + turkpow + dinam) actually cover 8 distinct emit shapes?

### Priority

**Critical** — Phase 0 acceptance-gate methodology (PR20) requires per-shape hand-derived KKT verification. If 2+ anchors collapse to the same shape under formal analysis, Sprint 27 Day 1/2 verification budget can be reduced. If the 7 non-anchor models exhibit additional shapes not covered by the 8 anchors, Priority 1's Phase 0 inventory is incomplete.

### Assumption

The 8 anchor models selected in Sprint 27 PROJECT_PLAN.md (launch byte-stability anchor + 7 distinct stationarity-equation shapes: qdemo7 `stat_xcrop(c)`, ferts `stat_z(p,i)`, sambal `stat_x(i,j)` cbal-derivative, ganges `stat_pls(r)`, sroute `stat_<network>`, turkpow `stat_zt(m,v,b,t)`, dinam two distinct shapes in `comp_mb(i,t)` + `stat_ka(te)`) cover all distinct emit shapes that the tightened gate predicate must handle. The 7 non-anchor models (egypt, shale, qsambal, harker, tfordy, gangesx, srpchase) each share a shape with one of the 8 anchors.

### Research Questions

1. When the hand-derived KKT analysis is performed on the 8 anchors, do any two collapse to the same shape?
2. For each of the 7 non-anchor models, which anchor's shape best matches? Is the match unambiguous?
3. Do any of the 7 non-anchor models exhibit a 9th distinct shape not covered by the 8 anchors?
4. Does the dinam "2 distinct shapes" justification hold up under formal analysis, or is dinam actually 1 shape with positional variations?

### How to Verify

1. For each of the 8 anchor models, inspect regenerated `data/gamslib/mcp/<model>_mcp.gms` for the stationarity equation pattern (Task 4 of PREP_PLAN.md).
2. Document each anchor's distinguishing emit pattern (which stationarity equation, what cross-term structure, what alias-conditional pattern).
3. Compare across all 8 anchors for distinctness; flag any pair with similar patterns for hand-derived KKT to confirm distinctness in Sprint 27 Day 1/2.
4. Assign each of the 7 non-anchor models to the matching anchor with justification in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md`.

### Risk if Wrong

- **Anchor over-coverage (2+ collapse to same shape):** Sprint 27 Phase 0 verification time reduced by ~1h per collapsed anchor.
- **Anchor under-coverage (9th shape exists):** Sprint 27 Phase 0 verification time increased by 2–3h to add the missing shape; risk of Day 13 surprise if not caught in prep.
- **Ambiguous non-anchor mapping:** Sprint 27 Day 1/2 hand-derived KKT must resolve before Priority 1 implementation can proceed.

### Estimated Research Time

2–3 hours (per-anchor pattern inspection + per-non-anchor matching analysis)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (inspection-based; formal hand-derived KKT confirmation deferred to Sprint 27 Day 1/2 Phase 0)
**Verified by:** Task 4 (#1398 Widened-Scope Verification + Anchor Model Audit)
**Date:** 2026-05-28

**Findings:** Inspection of regenerated `data/gamslib/mcp/<anchor>_mcp.gms` for all 8 anchor models surfaces **8 structurally distinct emit shapes** at the inspection level (no anchor pair collapses to the same shape under emit-artifact comparison):

| Anchor | Distinguishing emit pattern (canonical equation) |
|---|---|
| `launch` | `sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss))` — order-relation alias-indicator (`ge(s,ss)`) |
| `qdemo7` | `sum(s, 1$(sc(c,s)) * lam_plow(c))` — Pattern C alias-sum with `sc(s,c)`-domain (source constraint is `sum(c$(sc(s,c)), xcrop(c))`); suspected bug has 2 compounding errors — (a) indicator argument order swapped to `sc(c,s)` AND (b) multiplier uses eq-index `c` instead of bound-index `s`; expected post-fix `sum(s, 1$(sc(s,c)) * lam_plow(s))` |
| `ferts` | `sum(c, ((-1) * (a(c,i) * 1$(ppos(i,p)))) * lam_mb(c,p))` — multi-bound-index sum with `ppos(i,p)` 2-set membership; multiplier projects bound + eq |
| `sambal` | `sum(i__kkt1, ((-1) * 1$(xb(i,i__kkt1))) * nu_cbal(i))` — `__kkt1` synthetic alias + `xb(i,i__kkt1)` parameter-as-condition + cbal-derivative |
| `ganges` | 4 inner Pattern C alias-sums with `ri(i,r)` 2-set membership + outer set-membership existential guard `$(sum(i, 1$(ri(r,i))))` |
| `sroute` | `(1$(darc(ip,ipp)) * lam_nb(i,ip))$((not sameas(i,ipp)))` — parameter-arc indicator + negation guard; NO outer sum (unwrapped Pattern C) |
| `turkpow` | `vs(t__,t__)` self-loop alias + `bs(bp,b)` separate-var conditional + massive `sameas`-Cartesian inner-sum-of-bs-conditioned-products |
| `dinam` | `stat_ka(te)` row-multiplier-collapse `lam_mb(i,t)` (both bound) + `ts2(te,te)` eq-index self-loop + `IndexOffset(te+7)` inside Pattern C |

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §3 (launch) + §4 (7 in-cohort anchors) — per-anchor distinguishing emit pattern, Phase 0 grep-based verification commands, and recovery-impact note. Inspection commands run on Sprint 27 Day 0 `data/gamslib/mcp/*_mcp.gms` artifacts (`e0be4fb1`-baselined; no `src/` changes since).

**Decision:** Priority 1 Phase 0 anchor set CONFIRMED at 8 anchors covering 8 distinct emit shapes (at inspection granularity). 7 non-anchor models mapped to anchors with justification (`docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §5):

- egypt → qdemo7 (high confidence — 2-region extension)
- shale → ferts (medium-high — multi-bound-index sum family; sameas-Cartesian sub-shape flagged Open Question 2)
- qsambal → sambal (high — structurally identical, quadratic objective only)
- harker → sroute (medium — network-arc parameter family; sameas-aliased inner-sum sub-shape flagged Open Question 3)
- tfordy → sambal (medium — cbal-style multiplier family without `__kkt1` alias; Open Question 3)
- gangesx → ganges (high — eXtended variant, same 4-inner-sum + `ri(i,r)` family)
- srpchase → turkpow (low-medium — `ancestor(srn,srn)` self-loop mirrors turkpow's `vs(t__,t__)`; Open Question 3)

**5 Open Questions escalate to Sprint 27 Day 1/2 Phase 0 hand-derived KKT** (`PRIORITY_1_ANCHOR_MAPPING.md` §6):

1. fawley's #1398 surface vs #1356 fix scope (folded into #1356 per PROJECT_PLAN.md L1032; confirmation needed after Day 1 #1356 fix lands)
2. shale's sameas-Cartesian sub-shape — candidate 9th shape under turkpow's pattern
3. Non-anchor mapping confidence for harker/tfordy/srpchase — possible 9th/10th/11th distinct shapes
4. dinam's "2 distinct shapes" claim (Shape A `stat_ka` + Shape B `comp_mb` differentiate) — may collapse to 1 logical shape with positional variations
5. Anchor-pair collapse risk (launch vs sambal both have synthetic-alias structure; qdemo7 vs ferts both have set-membership indicators) — no inspection-level collapse, but formal hand-derived KKT may reduce verification budget

**Bonus finding:** No 9th-shape candidate identified at inspection that REQUIRES additional anchor (5 of the open questions are confirmation tasks, not gap fixes). Sprint 27 anchor set unchanged at 8 unless Day 1/2 Phase 0 surfaces an unambiguous shape that no anchor covers.

---

## Unknown 1.3: Will the tightened gate predicate fire only on the original launch-shape Pattern C case, or does it need explicit positional information from the source Sum's body?

### Priority

**High** — The Priority 2 Pattern C Phase B redesign builds the consolidated multiplier term explicitly from the source Sum's body structure (positions preserved). If Priority 1's tightening also requires positional information, then Priorities 1 and 2 share infrastructure and must be sequenced — Priority 2's positional-extraction work would precede Priority 1's predicate-tightening work.

### Assumption

Priority 1's tightening can use alias-conditional structure detection alone (similar to Sprint 25's original narrow `_find_pattern_c_alias_sum` gate, restored from the broadening that PR #1379 introduced), without needing the explicit positional information that Priority 2's Phase B redesign requires.

### Research Questions

1. Does the launch-shape Pattern C case (the original PR #1379 target) have a structurally simpler predicate than the camcge / cesam2 plain-alias / `sameas`-decomposed cases that Priority 2 targets?
2. Can Priority 1 be implemented as a "restore the Sprint 25 narrow gate" + "verify byte-stable on launch" without touching the Priority 2 positional-extraction infrastructure?
3. If Priority 1 needs positional information, are Priorities 1 and 2 the same workstream (combine into a single Phase 0 + implementation cycle)?
4. Does the Sprint 26 final emit on launch (post-PR #1379) need to be preserved byte-stable, or only semantically-equivalent under the tightened gate?

### How to Verify

1. Inspect Sprint 25 narrow gate code (pre-PR #1379) — `git log --oneline -- src/kkt/stationarity.py | head -20` to locate the relevant SHA, then `git show <sha>:src/kkt/stationarity.py | grep -A50 _find_pattern_c_alias_sum`.
2. Compare against the PR #1379 broadened gate to identify the exact predicate change.
3. Hand-derive KKT for launch + qdemo7 (smallest pair) and check whether the tightened predicate distinguishes correctly without positional information.
4. Verify whether the Priority 2 positional-extraction infrastructure is reusable for Priority 1 or strictly orthogonal.

### Risk if Wrong

- **Priority 1 needs positional info:** Sprint 27 sequencing changes; combined Priorities 1+2 effort becomes ~20–30h instead of separate budgets, potentially exceeding the 10–14h Priority 1 allocation.
- **Byte-stability on launch breaks:** Sprint 27 Priority 4 (launch PATH-numerics) gets a moving target; either Priority 1 must preserve byte stability or Priority 4 budget must absorb the change.

### Estimated Research Time

1–2 hours (git inspection + hand-derived predicate analysis)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Sprint 27 Day 1, 2026-06-02) — **the gate fires only on the launch-shape self-alias case; NO positional info from the source Sum body is needed.**

**Finding:** an empirical trace of `_find_pattern_c_alias_sum` showed the Sprint 26 Phase A gate over-reached by firing on **cross-set** alias sums (qdemo7: `alias=c[crop]`, `eq_dom=s[season]`) and applying a blanket `alias↔eq_dom` swap that transposed both the condition arg order and the multiplier index. The distinguishing signal between a valid Pattern C (launch's `s`/`ss` — `Alias(s,ss)`, same set) and an over-reach (qdemo7's `s`/`c`, different sets) is purely **`_resolve_alias_target(alias) == _resolve_alias_target(eq_domain_index)`**.

**Fix:** restrict `_find_pattern_c_alias_sum` to return a match only when alias and eq-domain index resolve to the same canonical set; otherwise fall through to the recursive descent (a deeper Sum may still be a genuine self-alias). Verified: launch + sambal + sroute + turkpow + 11 Tier 0/1 canaries byte-identical; qdemo7/ferts/ganges/dinam corrected to source-order shapes (hand-derived in `DAY0_ANCHOR_SCRATCH_NOTES.md`); `make test` 4737 passed + new regression test. No source-Sum positional metadata required — the canonical-set identity is sufficient.

---

## Unknown 1.4: Will PR19 target-list widening to 16 models (15 #1398-affected + launch) produce CI runtime overhead > 5 minutes per PR?

### Priority

**High** — PR19's existing CI extension (per Sprint 26 PR #1396) runs PATH-solve on each target model, the most expensive pipeline stage. The current PR19 list is 15 models; adding the 16-candidate widening cohort (15 #1398-affected + launch) means 15 net new entries after deduping `fawley` (already in Pattern C tier), bringing the final union to 30 unique models. That doubling could push per-PR runtime past developer-friction thresholds. If runtime exceeds 5 min, Sprint 27 must implement Option C (parallelized CI jobs) instead of Option A (full widening).

### Assumption

PR19 widening to add the 16-model cohort (15 #1398-affected + launch) to the existing 15-model PR19 list — `fawley` is already present in the Pattern C tier so net additions = 15, final union = 30 unique models — adds < 5 minutes per PR runtime under Option A, keeping the CI feedback loop within developer-friction thresholds without requiring parallelization (Option C).

### Research Questions

1. What is the current PR19 per-model PATH-solve runtime distribution (min, median, max, per-model timeout cap)?
2. With 15 net new models added (16 candidates − 1 `fawley` already in list), final widened union 30 unique models, what is the projected total CI runtime?
3. Does GitHub Actions' per-job runtime limit (typically 6 hours, but Sprint 26 CI typically completes in < 30 min) constrain Option A?
4. If Option A exceeds 5 min, does Option C (split into 2 parallel CI jobs) keep both jobs under 5 min?
5. Does Option B (anchor-only widening to 8 anchors — 8 net new since no anchor is currently in PR19 list; final union 23 unique models) leave the 7 non-anchor #1398-affected models uncovered in a way that breaks Sprint 27's structural-mitigation rationale (KU-37 → PR19 widening is the structural mitigation)?

### How to Verify

1. Inspect Sprint 26 PR #1396 CI logs for per-model runtime data: `gh run list -w "PR19 Pre-Merge Solve-Time Validation" --json conclusion,createdAt,databaseId | head -20`.
2. Project widened runtime: 30 unique models (final union) × avg per-model time — refine using per-model medians from CI logs.
3. Run a dummy PR with the widened target list to measure actual CI runtime.
4. If Option A exceeds threshold, design Option C split (e.g., 8 anchors in job 1, 7 non-anchors + launch in job 2 — total 15 net new across both jobs) and project per-job runtime.

### Risk if Wrong

- **Option A exceeds threshold:** Switch to Option C (parallelized jobs) adds ~1–2h implementation effort to Task 5 + Sprint 27 Day 0.
- **Option B selected (anchor-only):** 7 non-anchor models uncovered against future gate-overreach; KU-37 mitigation incomplete.
- **GitHub Actions per-job limit exceeded:** Forces immediate Option C; no graceful degradation.

### Estimated Research Time

1–2 hours (CI log inspection + projection + dummy PR if needed)

### Owner

Sprint planning + CI engineer

### Verification Results

✅ **Status:** VERIFIED (projection-based; dummy-PR confirmation deferred to Sprint 27 Day 0 implementation PR)
**Verified by:** Task 5 (PR19 Target-List Widening Design)
**Date:** 2026-05-28

**Findings:**

- **Q1 (current PR19 runtime distribution):** Per `gh run view 25862102598` (Sprint 26 PR #1396 latest run 2026-05-14T13:15:47Z): Tier 0/1 11 models @ 0.02–0.17s each, sum ~0.5s; Pattern C 4 models @ 0.01–0.02s each (all rc=2 compile-fail), sum ~0.06s; setup overhead ~22s (dominated by GAMS install ~14s); whole-workflow wall-clock ~27s. Per-model timeout cap: 60s (reslim=30s + 30s subprocess buffer per `pr19-emit-solve-validation.yml` L21-32).
- **Q2 (projected widened runtime, Option A):** ~36s steady state. Breakdown: 22s setup + ~0.5s Tier 0/1 (11 models @ ~0.04s) + ~10s Pattern C (19 models incl. launch — launch ~0.2s MODEL STATUS 5, 9 compile-fast @ ~0.02s + 2 license-fail @ ~0.5–1s + 3 solve-pass @ ~0.5–2s + buffer) + 3s overhead. Worst case (all 19 Pattern C hit reslim timeout): ~19.5 min — within 20-min hard ceiling but tight (mitigated by observed compile-fast/fail-fast behavior). **(Corrected Day 0: launch is pattern-c, not Tier 0/1 — MODEL STATUS 5 Locally Infeasible.)**
- **Q3 (GitHub Actions per-job limit):** Not a constraint. 6-hour default ceiling; current workflow has `timeout-minutes: 20`. Option A worst case ~19.5 min stays inside this.
- **Q4 (Option C necessity):** NOT NEEDED. Option A projected runtime (~36s) is 8× under the 5-min friction threshold; Option C (parallel split) adds ~1–2h implementation effort + duplicates GAMS install (~22s overhead × 2) without solving a real bottleneck. Reserve Option C for Sprint 28+ if Pattern C cohort grows past ~25 models.
- **Q5 (Option B coverage gap):** Option B (anchor-only — 8 net new, final union 23) defeats the KU-37 mitigation rationale. The 7 non-anchor #1398-affected models (egypt, shale, qsambal, harker, tfordy, gangesx, srpchase) would remain UNCOVERED by PR19. Sprint 26's #1398 incident is exactly this failure mode at the launch level — failing to widen the structural mitigation surface to match the structural-regression surface. The ~5s runtime saving from Option B does not justify losing coverage on 7 non-anchor models.

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` §2 (PR #1396 CI log timing data), §4 (runtime calculation), §5 (3-option comparison), §6 (implementation steps).

**Decision: Option A SELECTED.** Sprint 27 Day 0 widens PR19 to 30 unique models (**11 Tier 0/1 hard-fail + 19 Pattern C soft-fail** — corrected Day 0: launch is pattern-c, MODEL STATUS 5 Locally Infeasible) via 15 net-new appended lines in `.github/path-solve-ci-targets.txt`. NO CI workflow YAML or helper script changes needed. Validation plan: local `parse_pr19_targets.py` dry-run + Sprint 27 Day 0 implementation PR triggers PR19 with the widened list + post-merge regression check on the first follow-up emit-affecting PR.

**Bonus finding — ❌ SUPERSEDED by Day 0 KU 6.1 (no action needed):** The prep-stage `PR19_WIDENING_DESIGN.md` §8.2 open question proposed adding `src/ad/index_mapping.py` to the PR19 `paths:` filter, on the premise that #1224 (`IndexOffset(ParamRef)`) touches that file. **Day 0 KU 6.1 disproved the premise** — `index_mapping.py` contains no `IndexOffset`/`ParamRef` code; #1224's actual surface is `src/ad/constraint_jacobian.py` (`_try_eval_offset:133`) + `src/ad/derivative_rules.py:2793`, **both already in the PR19 `paths:` filter** (`pr19-emit-solve-validation.yml` L10–L11). **No workflow `paths:` edit is needed** — PR19 already fires on #1224's emit-affecting changes. (Adding `index_mapping.py` would be a spurious edit.)

---

# Category 2: Pattern C Phase B Redesign (#1381)

Priority 2 workstream — Build consolidated multiplier term explicitly from source Sum body structure, intercepting before element-to-set substitution. Targets camcge + cesam2 (carryforward from Sprint 26 Day 3 reclassification).

## Unknown 2.1: Does the "build consolidated multiplier term from source Sum body structure" approach generalize cleanly to both camcge and cesam2?

### Priority

**Critical** — Priority 2 budgets 10–16h on the assumption that a single design pattern unblocks both camcge (plain-alias enumeration) and cesam2 (`sameas`-decomposed SAM-block aliasing). If cesam2 requires a separate detection path or distinct emit-construction logic, Priority 2 budget needs to be split or expanded.

### Assumption

A single Pattern C Phase B redesign — building the consolidated multiplier term explicitly from the source Sum's body structure with positions preserved, intercepting before element-to-set substitution — works for both camcge plain-alias bodies and cesam2 `sameas`-decomposed SAM-block aliases.

### Research Questions

1. Does cesam2's `sameas`-decomposed alias structure require an additional resolution step before the Phase B redesign can extract source-body structure?
2. Are camcge's and cesam2's source-Sum body shapes structurally similar (both are SAM-coefficient * variable patterns), or does cesam2 have additional decomposition?
3. Does the Phase B redesign produce byte-identical emit on camcge vs cesam2 for analogous constraints, or does each model need per-model variants?
4. What is the expected `nu_ieq` cross-term shape for camcge that Phase 0 acceptance gate (per #1381 issue body) must verify?

### How to Verify

1. Read Sprint 26 Day 3 reclassification rationale in `docs/issues/ISSUE_1381_*.md` for the camcge + cesam2 distinction.
2. Inspect the current (broken) regenerated `data/gamslib/mcp/{camcge,cesam2}_mcp.gms` for the source-Sum body shapes and compare structurally.
3. Hand-derive `nu_ieq` cross-term for camcge per Phase 0 acceptance gate; cross-check whether the same derivation pattern applies to cesam2.
4. Sketch the Phase B redesign patch and verify it produces the expected shape on both models.

### Risk if Wrong

- **Single design insufficient:** Priority 2 budget split between camcge variant + cesam2 variant; total effort grows to ~16–22h.
- **cesam2 requires upstream decomposition:** New `src/ir/` work needed before Priority 2 can proceed; potential Sprint 28 carryforward.

### Estimated Research Time

2–3 hours (issue inspection + emit comparison + hand-derivation sketch)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (Sprint 27 Day 3 hand-derivation; binding verdict + implementation Day 4) — see `DAY3_P2_PHASE0_NOTES.md`.

**Day 3 finding:** the "build consolidated term from the source Sum body" philosophy generalizes, but camcge and cesam2 need **related-but-distinct builders** (not a single code path):
- **camcge (B-1/B-2):** all 5 variants hand-derived. Consolidation rule = `sum(j, COEFF'·nu_eq(j))` where `COEFF'` keeps the source coefficient's argument *positions* but rewrites the sum-index slot → stat index `i` and the eq-index slot → alias `j` (e.g. ieq `imat(i,j)→imat(j,i)`; actp `io(j,i)→io(i,j)`). prodinv (B-2) additionally factors a var-side `dst(i)` outside + an eq-side `kio(i)→kio(j)` inside the new Sum. The Phase A swap fails here because element-to-set collapses `imat(i,j)→imat(i,i)` (positions erased) → so Phase B must intercept BEFORE element-to-set.
- **cesam2 (B-3):** dim-mismatch (1-D eq `COLSUM(jj)` vs 2-D var `TSAM(i,i)`) needs a **separate** builder — multiplier indexed by the var-domain position the eq-domain binds to, **no outer Sum**, + a `$(jj(j))` subset guard. Distinct detection (`len(var_domain) != len(eq_domain)`).

**Binding answer (provisional):** YES, generalizes — under one source-body-driven design with **three sub-builders** (`_build_pattern_c_consolidated_term` B-1, `_classify_eq_body_factors` B-2, `_build_pattern_c_dim_mismatch_term` B-3) per ISSUE_1381 §Files Involved. Budget split across B-1/B-2/B-3 is sound. **Day 4: finalize cesam2 derivation + implement + byte-verify → moves to ✅ VERIFIED.**

---

## Unknown 2.2: Does the Phase B redesign interact with the tightened Phase A gate from Priority 1, requiring sequenced implementation?

### Priority

**High** — Priorities 1 and 2 both modify the Pattern C gate-handling code in `src/kkt/stationarity.py`. If they share infrastructure (both rely on alias-conditional detection or both touch `_apply_pattern_c_swap_to_term`), one must precede the other. Parallelization without sequencing risks merge conflicts and behavioral coupling.

### Assumption

Priority 1 (Phase A gate tightening) and Priority 2 (Phase C Phase B redesign) are independent enough to be implemented in parallel across Sprint 27 Days 1–4, sharing only the test-target overlap on launch (Priority 1 byte-stability anchor) and Pattern C target models (Priority 2 implementation targets).

### Research Questions

1. Do Priorities 1 and 2 modify overlapping functions in `src/kkt/stationarity.py`?
2. Does Phase B's "intercept before element-to-set substitution" infrastructure share code with Phase A's gate predicate?
3. Can Priorities 1 and 2 share a single Phase 0 acceptance-gate sequence, or do they need separate gates?
4. If sequenced, which goes first — Priority 1 (smaller, lower risk) or Priority 2 (larger, higher leverage)?

### How to Verify

1. `grep -n "_find_pattern_c_alias_sum\|_apply_pattern_c_swap_to_term\|element_to_set_substitution" src/kkt/stationarity.py` to identify shared functions.
2. Read Sprint 26 Day 1 PR #1379 + Day 3 reclassification diffs to understand the current Phase A + B code layout.
3. Compare the planned Priority 1 patch sites (from Task 4) against the planned Priority 2 patch sites (from #1381 issue body + Phase 0 work) for overlap.
4. If overlap exists, propose sequencing order with justification.

### Risk if Wrong

- **Sequential dependency:** Sprint 27 schedule (Task 11) must respect ordering; parallel days lost.
- **Merge conflict mid-sprint:** Day 4–5 churn on `stationarity.py` if both priorities ship simultaneously.

### Estimated Research Time

1–2 hours (code inspection + Sprint 26 PR diff review)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: What is the byte-stability surface on the 11 Tier 0/1 canary models when Phase B lands?

### Priority

**High** — Phase B intercepts before element-to-set substitution, which is upstream of many emit paths. If the redesign affects the 11 Tier 0/1 canaries (dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive), regression risk is high and Phase 0 acceptance gate must include all 11 canaries in the verification set.

### Assumption

Phase B redesign is selective enough that only the 2 target models (camcge, cesam2) have emit changes; the 11 Tier 0/1 canaries remain byte-identical post-Phase-B.

### Research Questions

1. Does Phase B's interception trigger condition fire on any Tier 0/1 canary's Sum expressions?
2. If canaries trigger the new code path, does the consolidated multiplier construction produce the same emit as the pre-Phase-B element-to-set-substitution path?
3. Does the Phase 0 acceptance gate need to extend to canary byte-stability checks, or only target-model correctness?
4. Does PR19 widening (from Category 1.4) already cover canary byte-stability, or does Phase B need its own canary regression test?

### How to Verify

1. Grep all 11 canary `data/gamslib/mcp/<canary>_mcp.gms` files for the Pattern C / Phase B trigger pattern (alias-conditional Sum bodies).
2. For any canary matching, prototype the Phase B redesign with a model-name guard and verify byte-identical emit.
3. Extend Phase 0 acceptance gate to include canary byte-stability if any canary triggers Phase B.

### Risk if Wrong

- **Canary regressions:** Phase B redesign requires expanded scope to cover canary protection; budget +2–4h.
- **Phase 0 gate too narrow:** Day 13 retrospective surfaces canary regression; Sprint 28 carryforward.

### Estimated Research Time

1–2 hours (canary corpus grep + prototype check)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 3: AD Architectural Redesigns (#1390, #1385, #1393 + #1335)

Priority 3 workstream — Three architectural redesigns targeting different AD pipeline subsystems. Sprint 27 budgets 30–48h combined (10–16h per sub-priority). All three require Phase 0 acceptance gates per PR20. Drives KU-38 (4 close-and-refile share architectural class — coordinated design analysis) and KU-39 (#1335 has 3 competing approaches, requires selection) from Sprint 26 §End-of-Sprint Discoveries.

## Unknown 3.1: Can #1390's per-instance enumeration redesign be implemented as an opt-in via static predicate, or does it require modifying `_compute_equality_jacobian` / `_compute_inequality_jacobian` signatures?

### Priority

**Critical** — Signature changes to `_compute_equality_jacobian` / `_compute_inequality_jacobian` ripple through all callers in the AD pipeline. If #1390 requires signature changes, the patch surface expands well beyond `src/ad/constraint_jacobian.py:903`/`:1027` and likely exceeds the 10–16h sub-priority budget.

### Assumption

#1390's per-instance enumeration redesign for tree-predicate-aliased Sums (kand `stat_y(j,t,n)` cross-term) can be implemented as a per-equation opt-in via a static predicate (e.g., `_is_tree_predicate_aliased_sum(eq)`) without modifying the signatures of `_compute_equality_jacobian` / `_compute_inequality_jacobian`.

### Research Questions

1. Does the current enumeration step in `_compute_equality_jacobian:903` / `_compute_inequality_jacobian:1027` accept per-element callbacks that could be replaced with a predicate-guarded Sum builder?
2. Does the kand-specific shape (22 phantom-offset `lam_dembalx(j,t+1,n+k)` terms) generalize to a tree-predicate detection pattern, or is it kand-specific?
3. Are there other models exhibiting the same tree-predicate-aliased Sum shape that would benefit from #1390's redesign, or is kand isolated?
4. What is the hand-derived expected KKT shape for `stat_y(j,t,n)` cross-term (predicate-guarded Sum vs 22-element enumeration)?

### How to Verify

1. Read `src/ad/constraint_jacobian.py` `_compute_equality_jacobian` / `_compute_inequality_jacobian` signatures and identify caller surface.
2. Patch with model-name-guarded predicate-guarded Sum shim for kand only; regenerate `kand_mcp.gms`; byte-compare cross-term against hand-derived KKT.
3. Grep corpus for the tree-predicate-aliased Sum shape across all 134 translating models.
4. Document PROCEED / REPLAN signal per Phase 0 acceptance gate.

### Risk if Wrong

- **Signature changes needed:** #1390 sub-priority budget grows to 16–24h; risk of Sprint 28 carryforward.
- **kand isolated (no other models):** Sub-priority value lower than projected; consider deferring to Sprint 28 in favor of higher-leverage work.

### Estimated Research Time

2–3 hours (signature inspection + shim prototype + corpus grep + hand-derivation)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Sprint 27 Day 0 execution) — **binding signal: 🔴 REPLAN.** The §3.3 patch site (`constraint_jacobian.py:903/1027`) is **misattributed**: a full-translate trace shows the 22 phantom-offset terms are produced by `stationarity.py::_apply_offset_substitution` (fires exactly 22×), while `_compute_inequality_jacobian` only stores concrete per-(row,col) partials. RQ1's "callback dispatch insertion" premise does not address the bug. Redirected surface = stationarity lead/lag-offset re-symbolization. See `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 + §8.5 binding table.
**Verified by:** Task 6 design + Sprint 27 Day 0 prototype execution (PR16)
**Date:** 2026-05-28 (prep) / 2026-06-01 Sprint 27 Day 0 (binding)

**Findings (architectural analysis):**

- **Research Q1 (signatures vs callbacks):** `_compute_equality_jacobian` (`src/ad/constraint_jacobian.py:903`) and `_compute_inequality_jacobian` (`:1027`) accept a per-equation differentiation strategy via callback (the per-element enumeration is one of several differentiation paths). Inserting a predicate-guarded path at the same dispatch site is well-localized — **no signature changes needed.**
- **Research Q2 (kand-specific vs general):** `tree(n,n)` 2-set membership predicate has a clear AST shape (`SetMembershipTest` on a 2-set parameter); detection via static analysis is feasible. The detection generalizes to any model with a 2-set-membership-bound Sum body — not kand-specific.
- **Research Q3 (corpus prevalence):** Corpus grep deferred to Sprint 27 Day 0 execution; expected to surface 0–3 additional models with the same shape (low-prevalence shape).
- **Research Q4 (hand-derived KKT shape):** The expected `stat_y(j,t,n)` cross-term is `sum(n_inner$tree(n,n_inner), eps * lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner))` — single guarded Sum, 1 element. Pre-fix emit produces 22 phantom-offset terms instead.

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3 (Redesign A — #1390 kand) — hypothesis statement, validation experiment design with explicit patch site (`_compute_equality_jacobian:903` + `_compute_inequality_jacobian:1027`), prototype guard illustration, regen + grep verification commands, hand-derived KKT for `stat_y('p-1','time-2','n-4')` instance.

**Tentative verdict:** 🟢 PROCEED projected. Predicate detection is feasible; cross-term builder is well-defined; model-name guard limits regression risk to zero by construction.

**Decision (binding pending Day 0):** **Opt-in via static predicate (no signature changes).** Day 0 engineer executes §3.3 experiment (~45 min); records binding PROCEED/REPLAN signal in PRIORITY_3_RISK_ASSESSMENT.md §3.5 + updates this Unknown to ✅ VERIFIED.

---

## Unknown 3.2: Does #1385's alternative short-circuit shape need to preserve concrete-index semantics throughout the AD/emit pipeline, or only at the AD → emit boundary?

### Priority

**Critical** — The Sprint 26 Day 4 #1385 attempt produced syntactically-correct emit + GREEN quality gates but broken multiplier references downstream because `_build_symbolic_instance_placeholder` returned the set name as the index. The fix scope depends on whether concrete-index semantics must hold throughout (large patch surface) or only at the AD → emit boundary (smaller, contained patch).

### Assumption

#1385's alternative short-circuit shape can preserve concrete-index semantics at the AD → emit boundary only (final emit stage), with symbolic placeholders allowed throughout earlier AD pipeline stages, by enhancing `_build_symbolic_instance_placeholder` and its consumers in the emit path rather than refactoring upstream AD stages.

### Research Questions

1. Where in the AD pipeline does `_build_symbolic_instance_placeholder` get called, and which downstream consumers depend on its return shape?
2. Does the emit path's multiplier-reference resolution require concrete indices, or can it accept symbolic placeholders with late-stage resolution?
3. Can a "preserve concrete-index semantics at emit boundary only" patch be prototyped on srpchase (Priority 3's #1385 unblock target) without regressing the 11 Tier 0/1 canaries?
4. Does the alternative short-circuit shape conflict with existing `_build_symbolic_instance_placeholder` callers (e.g., the Sprint 26 Day 4 attempt's broken multiplier references)?

### How to Verify

1. Grep all callers of `_build_symbolic_instance_placeholder` in `src/ad/` and `src/emit/`.
2. Read Sprint 26 Day 4 SPRINT_LOG entry for #1385 details on the broken-multiplier-reference root cause.
3. Patch the emit boundary with a concrete-index-preserving variant guarded on srpchase only; regenerate `srpchase_mcp.gms`; compile-check + multiplier-reference resolution check.
4. Document PROCEED / REPLAN signal per Phase 0 acceptance gate.

### Risk if Wrong

- **Throughout-pipeline preservation needed:** #1385 sub-priority budget grows to 18–28h; high Sprint 28 carryforward risk.
- **Breaks Tier 0/1 canaries:** Sub-priority budget grows with regression-fix work.

### Estimated Research Time

2–3 hours (caller grep + Sprint 26 Day 4 log review + prototype + regression check)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Sprint 27 Day 0 execution) — **binding signal: 🟡 SCOPED-PROCEED (translate-time only).** The AD→emit-boundary short-circuit (skip `slack`/`demand` enumeration at `index_mapping.py:377`) brings translate **>180s → 6.0s** with clean GAMS compile and no quoted-literal indices (crit 1–3 ✓). But it preserves concrete-index semantics only by **dropping** the equations — cross-term coverage (crit 4) is NOT preserved; the runtime-guard *emit* half (the answer to this KU — "only at the AD→emit boundary") was not authored and is an emit-layer problem. Sprint 27 may land translate-time only and defer cross-terms to Sprint 28. See `PRIORITY_3_RISK_ASSESSMENT.md` §4.5 + §8.5.
**Verified by:** Task 6 design + Sprint 27 Day 0 prototype execution (PR16)
**Date:** 2026-05-28 (prep) / 2026-06-01 Sprint 27 Day 0 (binding)

**Findings (architectural analysis):**

- **Research Q1 (callers of `_build_symbolic_instance_placeholder`):** The function does NOT currently exist in `src/ad/index_mapping.py` (verified via grep on current main). Sprint 26 Day 4 attempted but the patch was rolled back. The hypothetical Sprint 27 implementation would create the function as part of #1385 — caller surface is therefore a Sprint 27 design decision, not a constraint inherited from existing code.
- **Research Q2 (emit-boundary vs throughout-pipeline):** The Sprint 26 Day 4 attempt tried Option A (throughout-pipeline symbolic-instance handling) and failed at the emit boundary — `_diff_varref` requires exact concrete-index matches; symbolic placeholders produced `nu_slack("srn")` literal-string indices that PATH rejects at compile. **Option B (runtime-guard emission at the AD → emit boundary only) is the recommended alternative** — preserves the existing AD-layer Cartesian-enumeration contract, emits the predicate as a GAMS runtime guard `sum(<bound>$(<predicate>), <body>)`.
- **Research Q3 (Option B prototype on srpchase):** Day 0 prototype execution per §4.3 of PRIORITY_3_RISK_ASSESSMENT.md will surface whether Option B's runtime-guard emission preserves cross-term coverage. Architectural analysis projects ⚠️ caveat: the empty `enumerate_equation_instances` return means the AD layer doesn't enumerate any instances, so cross-terms from `J_g^T·lam_demand` must be emitted structurally at the emit boundary (not via AD enumeration).
- **Research Q4 (conflict with Sprint 26 Day 4 callers):** No callers exist on main (Day 4 rolled back); no conflict.

**Evidence:** PRIORITY_3_RISK_ASSESSMENT.md §4 (Redesign B — #1385 srpchase) — hypothesis statement, validation experiment design with explicit patch sites (`src/ad/index_mapping.py:377` + `src/kkt/stationarity.py`), regen + GAMS compile-check verification commands, partial-PROCEED escalation rule for cross-term coverage.

**Tentative verdict:** 🟡 PROCEED-with-caveat projected. Translate-time fix (5.7s achievable) is high-confidence; cross-term coverage is the residual risk surface.

**Decision (binding pending Day 0):** **Option B (runtime-guard emission at emit boundary).** If Day 0 execution surfaces the cross-term coverage gap, escalate to scoped-PROCEED (§7 of PRIORITY_3_RISK_ASSESSMENT.md) — Sprint 27 implements translate-time short-circuit only, defers cross-term handling to Sprint 28.

---

## Unknown 3.3: Which of the 3 competing approaches for #1335 (extend `_expand_sums_with_unresolved_offsets` + fix downstream re-symbolization; resolve `card-ord` symbolically without expansion; hybrid post-AD collapse to symbolic-Sum) is empirically best for otpop?

### Priority

**Critical** — KU-39 codifies that Sprint 26 Day 9 SPRINT_LOG enumerated 3 approaches but didn't select. Sprint 27 must select before implementation; selection is a Sprint 27 prep deliverable (Task 6). Each approach has different patch-surface and risk profiles.

### Assumption

The "hybrid post-AD collapse to symbolic-Sum" approach (Approach 3, the lightest) is the empirically best choice for otpop because it minimizes upstream AD churn and confines the change to a single post-AD collapse step in `_sum_should_collapse` (`src/ad/derivative_rules.py:2556`) + `_is_concrete_instance_of` (`:2607`).

### Research Questions

1. For each of the 3 approaches, what is the patch surface (files + lines)?
2. For each approach, what is the regression risk to the 8 currently-passing scalar-eq models?
3. Does Approach 3 produce the expected `stat_x(tt)` / `stat_p(tt)` shape on otpop matching hand-derived KKT?
4. Does Approach 3 also subsume #1393 (scalar-eq Sum-collapse), or does #1393 need its own design?
5. Does Approach 1 (extend `_expand_sums_with_unresolved_offsets`) introduce regressions in the existing IndexOffset / SetMembershipTest handling from Sprint 25?

### How to Verify

1. Read Sprint 26 Day 9 SPRINT_LOG entry for the 3-approach enumeration + rationale.
2. For Approach 3, patch `_sum_should_collapse` with a model-name-guarded prototype for otpop; regenerate `otpop_mcp.gms`; check `stat_x(tt)` / `stat_p(tt)` shape against hand-derived KKT.
3. If Approach 3 shape matches, run PATH-solve on otpop and check `pi ≈ 4217.80` per Phase 0 acceptance gate.
4. Document selection rationale + PROCEED / REPLAN signal in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md`.

### Risk if Wrong

- **Approach 3 disconfirmed:** Fall back to Approach 2 (resolve `card-ord` symbolically); patch surface in `src/ir/condition_eval.py` instead of `derivative_rules.py`; effort +3–5h.
- **All 3 approaches fail Phase 0:** #1335 + #1393 deferred to Sprint 28; Sprint 27 Solve target impacted (otpop loss = −1 Solve).
- **Approach 3 doesn't subsume #1393:** Need separate Phase 0 + implementation for #1393; sub-priority budget split.

### Estimated Research Time

2–3 hours (Day 9 SPRINT_LOG review + Approach 3 prototype + Phase 0 verification on otpop)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Sprint 27 Day 0 execution) — **Approach C selected at prep, but DISPROVEN on Day 0 → 🔴 REPLAN.** The §5.3 premise (the collapse routes through `_is_concrete_instance_of('tt','t')`) is empirically false — that call never happens; the otpop-guarded Approach-C prototype produced **byte-identical** emit (#1393 over-count + #1335 missing `nu_zdef` both persist). Per the §5.5 fallback rule, the empirical answer to "which approach is best" becomes **Approach B** (symbolic offset evaluation of `card(t)-ord(t)`), which is ALSO required independently for #1335 — Approach C does not subsume it. #1393 and #1335 are now distinct fixes. See `PRIORITY_3_RISK_ASSESSMENT.md` §5.6 + §8.5.
**Verified by:** Task 6 design + Sprint 27 Day 0 prototype execution (PR16)
**Date:** 2026-05-28 (prep) / 2026-06-01 Sprint 27 Day 0 (binding)

**Findings (architectural analysis + Sprint 26 Day 9 SPRINT_LOG review):**

- **Research Q1 (per-approach patch surface):** Approach A = `src/ad/derivative_rules.py:1847+` + `src/kkt/stationarity.py` re-symbolization helpers (multi-module, high risk). Approach B = `src/ir/condition_eval.py` (or `src/ad/index_eval.py`) — requires new symbolic-offset-evaluation infrastructure not currently in the codebase (medium risk). Approach C = `src/ad/derivative_rules.py:2607` `_is_concrete_instance_of` only (~30-line addition, low risk).
- **Research Q2 (per-approach regression risk):** A = high (touches multiple AD subsystems; risks regressing existing IndexOffset / SetMembershipTest handling from Sprint 25). B = medium (narrower than A but new infrastructure). C = low (contained single-function change; reuses existing collapse-logic infrastructure).
- **Research Q3 (Approach C shape match):** Architectural analysis projects 🟢 high-confidence shape match for `stat_x(tt)` (#1393). Approach C extends `_is_concrete_instance_of` to recognize SYMBOLIC supersets via the model_ir subset declaration — `_sum_should_collapse` then fires correctly. Hand-derived KKT is unambiguous (single guarded term).
- **Research Q4 (Approach C subsumes #1335?):** 🟡 PROCEED-with-caveat — Approach C may NOT fully subsume #1335's missing time-reversal cross-term, because `_try_eval_offset` (`constraint_jacobian.py:133–260`) may still fail to resolve `card(t) - ord(t)` to `'1990'` during AD enumeration of the `zdef` sum body. Day 0 prototype execution will resolve. Fallback rule: if Approach C alone doesn't fix #1335, escalate to Approach B (symbolic offset evaluation, ~3–5h additional effort).
- **Research Q5 (Approach A regression risk):** Confirmed high — Sprint 25 IndexOffset / SetMembershipTest handling was developed iteratively across multiple PRs; extending `_expand_sums_with_unresolved_offsets` AND fixing downstream re-symbolization risks regressing those Sprint 25 surfaces.

**Evidence:** PRIORITY_3_RISK_ASSESSMENT.md §5.3 (#1335 approach selection table with per-approach patch surface + risk profile) + §5.4 (Approach C validation experiment design with explicit `_is_concrete_instance_of` 3rd-strategy patch + regen + grep verification + PATH-solve verification for `pi ≈ 4217.80`) + §5.5 (PROCEED/REPLAN criteria) + Sprint 26 Day 9 SPRINT_LOG note that Approach C is "the lightest."

**Decision (KU-39 resolution, binding):** **Approach C SELECTED.** Fallback rule: C → B → A per §5.5 if Day 0 execution REPLAN. If all 3 REPLAN, defer #1393 + #1335 to Sprint 28 and reallocate Priority 3 budget to higher-leverage work (#1378 deep-dive or #1387/#1388 implementation).

---

## Unknown 3.4: Do any of the 3 AD architectural redesigns share design constraints that make coordinated design preferable to serial implementation?

### Priority

**High** — KU-38 codifies that the 4 close-and-refile reclassifications (#1381 in Priority 2 + #1385 / #1390 / #1393 in Priority 3) share an architectural class (AD pipeline subsystem boundary leak between symbolic and concrete index handling). Coordinated design could reduce total effort vs serial implementation but risks late-binding all three sub-priorities to a single design decision.

### Assumption

The 3 Priority 3 redesigns can be implemented serially (one after another across Sprint 27 Days 4–9) without significant duplicate design work, because each targets a distinct AD pipeline subsystem (#1390 = `constraint_jacobian.py` enumeration; #1385 = `_build_symbolic_instance_placeholder` emit boundary; #1393 + #1335 = `derivative_rules.py` collapse logic).

### Research Questions

1. Do #1390 + #1385 share the symbolic-vs-concrete index handling concern at the AD layer?
2. Do #1385 + #1393 share the emit-pipeline boundary concern?
3. Do #1390 + #1393 share the predicate-guarded vs enumerated Sum-handling concern?
4. Would a coordinated design reduce duplicate refactoring effort by ≥ 4h vs serial implementation, or are the subsystems independent enough that coordination is overhead?
5. If coordinated, which sub-priority becomes the design anchor (likely #1385 as the boundary point, or #1390 as the largest surface)?

### How to Verify

1. Pair-wise architectural-overlap analysis for (#1390, #1385), (#1385, #1393), (#1390, #1393) — Task 6 step 3.
2. Estimate duplicate-refactoring effort for serial vs coordinated implementation.
3. Recommend serial vs coordinated in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §"Coordinated Design".

### Risk if Wrong

- **Coordinated needed but serial chosen:** ~4–8h duplicate refactoring effort in Sprint 27.
- **Serial needed but coordinated chosen:** All 3 sub-priorities late-bound to single design decision; if design wrong, all 3 slip to Sprint 28.

### Estimated Research Time

1–2 hours (pair-wise analysis + effort estimation)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED — coordinated-design analysis complete; serial implementation recommended (binding). **Day 0 update:** serial execution confirmed correct — running C → A → B independently let each REPLAN be diagnosed in isolation (the §6.4 cascading rule fired: 2 of 3 REPLAN). See `PRIORITY_3_RISK_ASSESSMENT.md` §8.5 binding table + budget-reallocation recommendation.
**Verified by:** Task 6 (PR16) + Sprint 27 Day 0 execution
**Date:** 2026-05-28 (prep) / Sprint 27 Day 0 (binding)

**Findings (architectural analysis):**

- **Research Q1 (#1390 + #1385 shared symbolic-vs-concrete concern):** Distinct fix surfaces — #1390 = `src/ad/constraint_jacobian.py` cross-term enumeration; #1385 = `src/ad/index_mapping.py` instance enumeration. Adjacent modules but distinct functions. No code reuse.
- **Research Q2 (#1385 + #1393+#1335 shared emit-pipeline boundary concern):** Distinct AD subsystems — #1385 = `index_mapping.py` (AD → emit boundary); #1393+#1335 = `derivative_rules.py` (collapse logic). Option B (#1385's runtime-guard emission, the recommended choice) is orthogonal to Approach C (#1393+#1335's collapse extension). If Option A were selected for #1385 (rejected here), there would be moderate coordinated-design interaction — but Option B has none.
- **Research Q3 (#1390 + #1393+#1335 shared Sum-handling concern):** Complementary but orthogonal — #1390 preserves predicate-structure upstream (cross-term emission); #1393+#1335 collapses Sum cross-terms downstream. No code reuse.
- **Research Q4 (coordinated design effort savings):** Coordinated design would NOT reduce total effort because the 3 fix surfaces are orthogonal (different modules, different functions, different architectural layers). Coordinated design's overhead (joint design meetings, shared interface discussions) would likely add ~2–4h without commensurate savings.
- **Research Q5 (design-anchor if coordinated):** N/A — coordinated design rejected.

**Shared methodology (NOT implementation):** All 3 redesigns share the same Phase 0 acceptance-gate methodology (PR16), the same regression-check surface (11 Tier 0/1 byte-stable canaries), and the same documentation pattern (Phase 0 sections in each issue doc per CONTRIBUTING.md §"Phase 0 Acceptance Gates"). Reuse methodology + tests; don't coordinate implementation.

**Evidence:** PRIORITY_3_RISK_ASSESSMENT.md §6 (Coordinated Design Analysis) — pair-wise architectural-overlap table; serial-implementation recommendation with lowest-risk-first sequencing (#1393+#1335 Approach C → #1390 → #1385 Option B); cascading-REPLAN rule (no architectural dependency means individual REPLANs do not cascade).

**Decision (KU-38 resolution, binding):** **Serial implementation recommended.** Sequence: (1) #1393+#1335 Approach C (~6–10h, lowest risk), (2) #1390 predicate-guarded Sum (~10–16h, medium risk), (3) #1385 Option B runtime-guard (~6–10h or ~12–18h if cross-term coverage caveat materializes, highest risk). Total: 22–44h within the 30–48h Priority 3 budget. **Cascading REPLAN rule:** if any 1 sub-priority REPLANs, the other 2 PROCEED independently (no architectural dependency). If 2+ REPLAN, Sprint 27 retrospective decision on budget reallocation.

---

## Unknown 3.5: Does the Phase 0 acceptance-gate methodology produce a binary PROCEED / REPLAN signal for each of #1390, #1385, #1393, or could results be ambiguous?

### Priority

**High** — Sprint 25 retrospective PR16 codified that the hypothesis-validation methodology produces binary signals (clearly proceed or clearly replan). If Sprint 27's Phase 0 validation for Priority 3 produces ambiguous results (e.g., "the patch produces the expected shape on the target equation but breaks an unrelated equation"), Sprint 27 has no decision rule.

### Assumption

Per-sub-priority Phase 0 validation experiments (Task 6) produce binary PROCEED / REPLAN signals — the prototype patch either produces the hand-derived expected shape on the target equation AND passes basic regression check, or it doesn't.

### Research Questions

1. What are the explicit PROCEED criteria for each of #1390, #1385, #1393 + #1335?
2. What constitutes an "ambiguous" result, and how should Sprint 27 prep treat it (PROCEED with caveat? REPLAN?)?
3. Does each validation experiment include a regression-check step on at least one Tier 0/1 canary?
4. If 1 of the 3 sub-priorities returns REPLAN, can the other 2 proceed independently, or does REPLAN cascade across coordinated-design dependencies (KU-38)?

### How to Verify

1. Define explicit PROCEED criteria in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` per sub-priority.
2. Run each validation experiment per Task 6; document signal.
3. Define cascading-REPLAN rule if applicable.

### Risk if Wrong

- **Ambiguous results:** Sprint 27 starts without clear PROCEED on Priority 3; mid-sprint pivot risk.
- **REPLAN cascade:** All 3 sub-priorities deferred to Sprint 28; Priority 3's 30–48h budget reallocated to other priorities (likely #1378 deep-dive + #1387/#1388 implementation).

### Estimated Research Time

1–2 hours (criteria definition + experiment execution)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED — binary-signal criteria defined per experiment; partial-PROCEED rules codified (binding). **Day 0 update:** the methodology produced unambiguous signals for all 3 (C → 🔴 REPLAN, A → 🔴 REPLAN, B → 🟡 SCOPED-PROCEED per the §7 partial-PROCEED escalation). PR16 caught a failure class unit/byte gates could not: all 3 prep patch sites were mis-scoped to the AD layer when the bugs live in the KKT stationarity/emit layer. See `PRIORITY_3_RISK_ASSESSMENT.md` §8.5.
**Verified by:** Task 6 (PR16) + Sprint 27 Day 0 execution
**Date:** 2026-05-28 (prep) / Sprint 27 Day 0 (binding)

**Findings:**

- **Research Q1 (explicit PROCEED criteria):** Defined for each of #1390, #1385, #1393+#1335 in PRIORITY_3_RISK_ASSESSMENT.md §3.4, §4.4, §5.5 respectively. Each PROCEED criteria list is conjunctive — ALL items must hold for PROCEED. Each REPLAN criteria list is disjunctive — ANY item triggers REPLAN.
- **Research Q2 (ambiguous-result handling):** Binary by construction — if ANY PROCEED criterion fails, signal is REPLAN regardless of partial successes. Special handling for **partial-PROCEED** (codified in PRIORITY_3_RISK_ASSESSMENT.md §7):
  - **#1385 partial-PROCEED:** if translate-time fix works (5.7s achievable) but cross-term coverage issue surfaces, escalate to **scoped-PROCEED** — Sprint 27 implements translate-time short-circuit only, defers cross-term handling to Sprint 28.
  - **#1390 partial-PROCEED:** not anticipated (predicate detection is binary by construction).
  - **#1393+#1335 partial-PROCEED:** if #1393 fixes but #1335 cross-term still missing, escalate to **Approach B fallback** per §5.5 fallback rule.
- **Research Q3 (regression-check step):** Yes — each validation experiment includes a regression check on at least the 11 Tier 0/1 byte-stable canaries (§3.3 step 6, §4.3 step 7, §5.4 step 9).
- **Research Q4 (cascading REPLAN):** No cascading — the 3 redesigns are architecturally orthogonal per §6.1 pair-wise overlap analysis. If 1 of 3 REPLAN, the other 2 PROCEED independently. If 2+ REPLAN, Sprint 27 retrospective decision on budget reallocation per §6.4.

**Evidence:** PRIORITY_3_RISK_ASSESSMENT.md §3.4, §4.4, §5.5 (per-experiment binary criteria) + §6.4 (cascading-REPLAN rule) + §7 (Phase 0 binary-signal criteria + partial-PROCEED resolution rules).

**Decision (KU 3.5 resolution, binding):** **Binary PROCEED / REPLAN signals confirmed per experiment.** Partial-PROCEED ambiguity resolved via either (a) scoped-PROCEED escalation (#1385) or (b) approach-fallback rule (#1393+#1335). Sprint 27 Day 0 Priority 3 entry gate has a clear decision rule for each experiment outcome.

---

# Category 4: launch PATH-Numerics Investigation (#1378)

Priority 4 workstream — Phase A's mathematically-correct KKT diverges PATH residuals vs Day 0's over-counted-but-tractable form. Numerical-conditioning problem, not a correctness regression.

## Unknown 4.1: Is the launch PATH-numerics issue fixable via solver-tuning (initial point, presolve, NLP-warm-start), or does it require an in-place sign/scaling refinement in `_apply_pattern_c_swap_to_term`?

### Priority

**High** — Sprint 27 Priority 4 budgets 6–12h. Solver-tuning-only fix is the small end of that range; in-place sign/scaling refinement is the large end. Knowing which class of fix applies before Day 1 lets Task 11 schedule Priority 4 appropriately.

### Assumption

launch's PATH-numerics divergence (MODEL STATUS 5 Locally Infeasible, 6194 iterations, `defvt` residual ~3.2e+04) is fixable via solver-tuning (NLP-warm-start using the NLP solution as MCP starting point, plus `--nlp-presolve` and initial-point tuning), without requiring in-place sign/scaling changes to `_apply_pattern_c_swap_to_term`.

### Research Questions

1. Does NLP-warm-start applied to launch reduce PATH iterations below 6194 with MODEL STATUS 1?
2. Does `--nlp-presolve` (or equivalent preprocessing) recover launch to MODEL STATUS 1 without warm-start?
3. If solver-tuning insufficient, what is the sign/scaling refinement needed in `_apply_pattern_c_swap_to_term`?
4. Does the fix transfer to other Pattern C models (cesam2, camcge) once Priority 2 lands, or is it launch-specific?

### How to Verify

1. Run launch with NLP-warm-start: solve launch as NLP (CONOPT), feed solution as initial point to PATH MCP; check MODEL STATUS + iteration count + `defvt` residual.
2. If warm-start works, document Priority 4 effort as small (~6h).
3. If warm-start fails, inspect `_apply_pattern_c_swap_to_term` for sign/scaling issues; document required changes.

### Risk if Wrong

- **Solver-tuning insufficient:** Priority 4 effort grows to upper bound (12h+); risk of Sprint 28 carryforward.
- **Fix doesn't transfer to cesam2/camcge:** Each model needs separate Priority 4 effort; Sprint 27 Solve / Match targets impacted.

### Estimated Research Time

2–3 hours (warm-start experiment + presolve test + sign/scaling inspection if needed)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: Will the launch byte-stability anchor (Priority 1 anchor model) constrain the Priority 4 fix shape?

### Priority

**Medium** — Priority 1 (#1398) selects launch as the byte-stability anchor — the Phase A tightening must preserve launch's regenerated `*_mcp.gms` byte-identical to Sprint 26 final. If Priority 4 (#1378) changes launch's emit (e.g., sign/scaling refinement in `_apply_pattern_c_swap_to_term`), Priority 1's byte-stability anchor moves.

### Assumption

Priority 4 fix is either (a) solver-tuning only (no emit change, byte-stability preserved) or (b) an in-place change to `_apply_pattern_c_swap_to_term` that produces semantically-equivalent emit (different multiplier system, same primal/dual) compatible with Priority 1's byte-stability anchor target.

### Research Questions

1. If Priority 4 requires sign/scaling refinement, does that change launch's emitted `.gms` artifact?
2. If yes, does Priority 1's byte-stability anchor need to shift (e.g., to a different anchor model) or be relaxed (e.g., to semantic-stability instead of byte-stability)?
3. Can Priorities 1 and 4 share a single PROCEED criterion on launch (both must produce valid emit AND launch must solve), or are they orthogonal?

### How to Verify

1. From Unknown 4.1, identify whether Priority 4 fix changes emit.
2. If emit changes, update Task 4's anchor-model mapping to reflect new byte-stability target.
3. Document combined Priority 1 + Priority 4 success criteria.

### Risk if Wrong

- **Byte-stability anchor shift needed:** Task 4 anchor mapping updated; ~1h prep effort + risk of cascading anchor changes.
- **Combined criteria conflict:** Priorities 1 and 4 produce conflicting requirements on launch; one must accept partial compromise.

### Estimated Research Time

1 hour (Priority 4 emit-impact analysis + anchor mapping update)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🟡 **Status:** PARTIALLY VERIFIED (anchor identified; Priority 4 emit-impact analysis deferred to Unknown 4.1)
**Verified by:** Task 4 (#1398 Widened-Scope Verification + Anchor Model Audit)
**Date:** 2026-05-28

**Findings:** Task 4 inspection of `data/gamslib/mcp/launch_mcp.gms` confirms the launch byte-stability anchor is the **Pattern C consolidated zero-offset with `ge(s,ss)` order-relation indicator** shape (`stat_iweight(s)` + `stat_pweight(s)` — 2 stationarity equations, identical Pattern C shape per `PRIORITY_1_ANCHOR_MAPPING.md` §3). This is the canonical Sprint 26 PR #1379 target shape.

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §3 with per-term emit + grep-based Phase 0 verification command.

**Constraint inputs identified (escalates to Unknown 4.1 emit-impact analysis):**

- If Priority 4 (#1378) is **solver-tuning only** (no `src/` change touching `_apply_pattern_c_swap_to_term` or related emit helpers) → launch byte-stability anchor preserved, no anchor mapping update needed.
- If Priority 4 is an **in-place sign/scaling refinement of `_apply_pattern_c_swap_to_term`** producing semantically-equivalent emit → launch byte-stability anchor MUST shift to a new reference (likely qdemo7 post-fix, since qdemo7's recovery from path_syntax_error → compare_match is itself a byte-stability signal). Anchor mapping document (§3) would be updated to reflect the new byte-stability anchor.
- If Priority 4 changes launch's emit AND launch fails to solve under new emit → joint Priority 1 + Priority 4 conflict; one workstream must accept partial compromise.

**Decision (Sprint 27 Day 0 prep):** Anchor mapping document records launch as the **provisional** byte-stability anchor pending Unknown 4.1 (Priority 4 emit-impact analysis on `_apply_pattern_c_swap_to_term`). Task 4 does NOT itself resolve Unknown 4.1; the anchor-shift decision is deferred to Sprint 27 Day 0/1 #1378 Phase 0 work.

**Cross-reference:** `PRIORITY_1_ANCHOR_MAPPING.md` §3 explicitly notes "Unknown 4.2 (will Priority 4 #1378 break launch byte-stability?) feeds into this anchor" — when Priority 4 Phase 0 resolves the emit-impact question, this Unknown's status updates from PARTIALLY VERIFIED to ✅ VERIFIED (anchor preserved) or ⚠️ ANCHOR SHIFTED (anchor mapping document updated with new byte-stability reference).

---

# Category 5: comp_up Subset/Superset Workstream (#1356 fawley + #1357 otpop)

Priority 5 workstream — Both fawley (#1356) and otpop (#1357) exhibit `$171` domain violations in `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` and `piU_x.fx(tt)$(...)`. Fix is in `src/kkt/complementarity.py` + `src/emit/emit_gams.py`.

## Unknown 5.1: Is the comp_up subset/superset fix a single-file change (complementarity.py only) or coordinated (complementarity.py + emit_gams.py)?

### Priority

**High** — Single-file effort is ~2–3h; coordinated effort is ~4–6h. Knowing scope before Day 1 lets Task 11 schedule Priority 5 appropriately within the 8–12h budget. Additional models (if Unknown 5.2 surfaces them) would expand effort further.

### Assumption

The fix is a coordinated change across `src/kkt/complementarity.py` (subset/superset domain logic) and `src/emit/emit_gams.py` (domain-condition emission for `comp_up_x` + `piU_x.fx`), because the subset/superset shape originates in `complementarity.py` and is rendered by `emit_gams.py`.

### Research Questions

1. Which function(s) in `src/kkt/complementarity.py` generate `comp_up_x(tt)$(...)` equations?
2. Which function(s) in `src/emit/emit_gams.py` emit the `$(t(tt) and xb(tt) < inf)` domain condition?
3. Does the domain-condition mismatch originate in `complementarity.py` (incorrect domain calculation) or in `emit_gams.py` (incorrect rendering of correct domain)?
4. Does the Sprint 25 #1349 `.fx → .l` side-effect fix in `emit_gams.py` interact with the proposed Priority 5 fix?

### How to Verify

1. `grep -n "comp_up\|comp_up_x" src/kkt/complementarity.py src/emit/emit_gams.py` to identify patch sites.
2. Inspect current `data/gamslib/mcp/{fawley,otpop}_mcp.gms` for the broken `comp_up_x` emit pattern.
3. Trace the emit through `complementarity.py` → `emit_gams.py` to identify the bug origin.
4. Sketch unified diff in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` covering both files if needed.

### Risk if Wrong

- **Single-file sufficient:** Priority 5 effort at lower end of 8–12h budget; slack absorbs other priorities.
- **Coordinated requires upstream IR changes:** Effort grows to 10–14h+; Sprint 28 carryforward risk.

### Estimated Research Time

1–2 hours (code inspection + emit tracing + diff sketch)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED — patch shape decision binding; implementation lands Sprint 27 Day 1
**Verified by:** Task 7 (comp_up Subset/Superset Fix-Surface Analysis)
**Date:** 2026-05-28

**Findings:**

- **Research Q1 (functions in `complementarity.py` generating `comp_up_x(tt)$(...)`):** `build_complementarity_pairs()` at `src/kkt/complementarity.py:465-513` — Patch site A at L473-483 (`up_guard` assembly via `Binary("and", condition, rhs_guard)` flat-conjunction), Patch site B at L485-494 (equation definition with `domain=var_domain` superset).
- **Research Q2 (functions in `emit_gams.py` emitting `$(t(tt) and xb(tt) < inf)` domain condition):** The `up_guard` Expr structure from `complementarity.py` Patch site A is rendered as `cond_gams` string by the standard EquationDef emit path; the matched-pair `piU_x.fx(tt)$(not (cond_gams)) = 0;` is emitted at `src/emit/emit_gams.py:2230-2243` (Patch site C, consumer of `cond_gams`).
- **Research Q3 (domain mismatch origin):** Originates in `complementarity.py` Patch site A — the flat-conjunction `Binary("and", subset_predicate, rhs<inf)` is GAMS-not-short-circuited; GAMS evaluates `param(c,...) < inf` for ALL `c ∈ var_domain`, triggering `$171` at non-subset elements. The `emit_gams.py` rendering at Patch site C inherits the bug. Fix MUST land in `complementarity.py`; `emit_gams.py` is consumer-only.
- **Research Q4 (#1349 interaction):** Different code regions — Sprint 25 #1349 at `emit_gams.py:1518-1698 + :1897-1906` (`.fx → .l` accumulator); Priority 5 at `emit_gams.py:2230-2243` (piU_x.fx matched-pair fixup). NO direct overlap. Code-path overlap matrix in `PRIORITY_5_FIX_SURFACE.md` §7.1.

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §3 (Source-Code Patch Sites) — exact `file:line` for Patch sites A/B/C + §4 (Unified Diff Sketch) with helper-function signatures + §6.1 (effort breakdown) + §6.2 (patch shape verdict) + §7 (#1349 regression analysis).

**Decision (Unknown 5.1 resolution, binding):** **Single-file `src/kkt/complementarity.py`-only patch recommended.** Equation-domain-narrowing approach (Option a in §2.1 / §3.1 Patch B) restructures `up_guard` to use the subset directly when detected; `emit_gams.py` Patch site C inherits the corrected `cond_gams` rendering automatically (no `emit_gams.py` change needed). **Coordinated `complementarity.py + emit_gams.py` patch is a defensive fallback** if Day 1 surfaces downstream issues with equation-domain narrowing. Estimated effort: ~7.5–8h within Priority 5's 8–12h budget.

---

## Unknown 5.2: Are fawley and otpop the only two models exhibiting the comp_up subset/superset shape, or do additional models exhibit the same `$171` pattern?

### Priority

**High** — Sprint 26 Day 13 surfaced fawley as needing the same fix as otpop, but the retest may not have covered the full corpus. If 1+ additional models exhibit the shape, Priority 5 budget needs additional verification effort per model (~1h each).

### Assumption

fawley + otpop are the only two models in the 142 in-scope corpus that exhibit the `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` + `piU_x.fx(tt)$(...)` shape. No additional models will surface during Sprint 27 Day 0 baseline retest.

### Research Questions

1. Does a corpus-wide grep of `data/gamslib/mcp/*_mcp.gms` for the `comp_up_x.*\$(.*< inf)` pattern find only fawley + otpop?
2. Do any other GAMS error code `$171` occurrences in the regenerated emit corpus suggest related (but distinct) subset/superset issues?
3. Does the Sprint 27 Day 0 baseline retest produce any new models in path_syntax_error bucket with this shape?

### How to Verify

1. `grep -lE "comp_up_x\(.*\)\$\(.*<[[:space:]]*inf\)" data/gamslib/mcp/*_mcp.gms` for corpus sweep (note: `[[:space:]]*` instead of `\s*` — `\s` is not valid in POSIX ERE; use `grep -P` if you prefer PCRE `\s`).
2. Cross-reference with `gamslib_status.json` path_syntax_error bucket entries.
3. Document any additional model in `PRIORITY_5_FIX_SURFACE.md`.

### Risk if Wrong

- **Additional models found:** Priority 5 budget grows by ~1h per model; Sprint 27 Solve count benefits.
- **Pattern broader than expected:** Coordinated fix needed across multiple shapes; effort 12h+; Sprint 28 risk.

### Estimated Research Time

1 hour (corpus grep + cross-reference)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED — corpus sweep complete; binding (no additional models discovered)
**Verified by:** Task 7 (comp_up Subset/Superset Fix-Surface Analysis)
**Date:** 2026-05-28

**Findings:**

- **Research Q1 (corpus-wide grep for `comp_up_x.*\$(.*< inf)` pattern):** Per `grep -lE 'comp_up_x\(.*\)\$\(.*<[[:space:]]*inf\)' data/gamslib/mcp/*_mcp.gms`: 4 matches (gtm, ibm1, otpop, tricp). Broader sweep `comp_up_[a-z]+` returns 28 matches (including fawley's `comp_up_u` shape). The regex match is **necessary but not sufficient** for the bug.
- **Research Q2 (other `$171` occurrences):** Per `gamslib_status.json` Sprint 27 Day 0 baseline: only fawley + otpop are in `path_syntax_error` bucket AND exhibit `$171` errors traceable to subset/superset bound-parameter declarations. The other 26 broader-sweep matches either solve cleanly (gtm, ibm1, agreste, cesam, indus, etc. in compare_match or model_infeasible buckets) or fail at unrelated stages (tricp at path_solve_terminated — NOT a syntax error).
- **Research Q3 (Sprint 27 Day 0 baseline retest):** Per Task 3 baseline `BASELINE_METRICS.md` §6.2 path_syntax_error table: no new models with the comp_up subset/superset shape surfaced. fawley + otpop are at path_syntax_error; gtm/ibm1 at compare_match; tricp at path_solve_terminated.

**Per-model classification table:**

| Model | Day 0 bucket | Affected? |
|---|---|---|
| `fawley` | path_syntax_error | ✅ YES — #1356 target (subset `cr(c)` + param `crdat(c,"supply")`) |
| `otpop` | path_syntax_error | ✅ YES — #1357 target (subset `t(tt)` + param `xb(tt)`) |
| `gtm` | compare_match | ❌ NO — `pc(i,j)` declared over `(i,j)` (full eq-domain); no subset/superset mismatch |
| `ibm1` | compare_match | ❌ NO — `sup(s,"inventory")` declared over `(s,*)` (full eq-domain); no mismatch |
| `tricp` | path_solve_terminated | ❌ NO — bound expr is `myScale * smax((i,kp), fx(i,kp))` (no subset-restricted parameter); failure is unrelated bug class |

**The bug requires BOTH:** (a) the flat-conjunction guard shape `$(subset(x) and param(x) < inf)` AND (b) the bound parameter is declared over a STRICT SUBSET of the equation domain. Only fawley + otpop satisfy both conditions.

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §5 (Affected-Model Corpus Sweep) — both narrow + broader regex sweeps, per-model classification table with Day 0 buckets, false-positive root-cause analysis.

**Decision (Unknown 5.2 resolution, binding):** **Priority 5 scope CONFIRMED at 2 models (fawley + otpop).** No additional models discovered. No effort growth needed. Sprint 27 Day 0 baseline retest did not surface any new models in the same shape.

---

## Unknown 5.3: Will the comp_up fix interact with the existing `.fx → .l` substitution logic from Sprint 25 #1349?

### Priority

**Medium** — Sprint 25 #1349 fixed a `.fx → .l` clobbering bug in `src/emit/emit_gams.py`. The Priority 5 fix also touches `emit_gams.py` (per Unknown 5.1). If they share code paths, regression risk to #1349 is non-trivial.

### Assumption

Priority 5's comp_up fix in `emit_gams.py` is structurally orthogonal to Sprint 25 #1349's `.fx → .l` substitution logic — they touch different functions / different emit-rendering paths.

### Research Questions

1. Does the function that emits `piU_x.fx(tt)$(...)` share code with the function that handles `.fx → .l` substitution from #1349?
2. Does the Priority 5 fix preserve the #1349 behavior on clearlak (the #1349 canary)?
3. If shared code paths, can a regression test on clearlak gate Priority 5 PR review?

### How to Verify

1. Grep `src/emit/emit_gams.py` for `.fx` handling + comp_up handling; identify any shared callers.
2. Apply Priority 5 fix prototype + verify clearlak emit byte-identical to Sprint 26 final.
3. Add clearlak regression check to Priority 5 acceptance criteria if shared code paths confirmed.

### Risk if Wrong

- **Shared code paths discovered late:** Priority 5 PR review surfaces #1349 regression; revert + retry; ~2h effort.
- **Clearlak regression in production:** Sprint 27 mid-sprint discovery; Sprint 28 carryforward + rollback.

### Estimated Research Time

1 hour (code inspection + clearlak verification)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED — LOW regression risk; clearlak byte-stability check codified as Priority 5 PR gate
**Verified by:** Task 7 (comp_up Subset/Superset Fix-Surface Analysis)
**Date:** 2026-05-28

**Findings:**

- **Research Q1 (shared callers):** No direct code-path overlap. Sprint 25 #1349 operates at `src/emit/emit_gams.py:1518-1531` (`fx_to_l_overrides_by_var` accumulator), `:1668-1698` (`eq_paired_in_mcp` / `.fx → .l` substitution), `:1897-1906` (merge `.fx → .l` per-instance overrides). Priority 5 operates at `src/kkt/complementarity.py:465-513` (Patch sites A + B) + `src/emit/emit_gams.py:2230-2243` (Patch site C, piU_x.fx matched-pair fixup — optional defensive). Distinct functions, distinct accumulators, no shared callers.
- **Research Q2 (clearlak preservation):** clearlak's bound parameters are declared over their respective equation domains (no subset/superset mismatch); Priority 5's subset-detection helpers (`_extract_subset_predicate` / `_bound_expr_subset_dependency`) return None for clearlak's bound expressions; the new code path is INACTIVE for clearlak. Expected outcome: byte-stable.
- **Research Q3 (regression gate):** Codified as Priority 5 PR pre-merge verification — regenerate `clearlak_mcp.gms`, diff against current main artifact, expect zero diff. If non-zero, root-cause; if Sprint 25 #1349 `.l`-side-effect behavior changed, rollback Priority 5 changes affecting the `.l` accumulator.

**Code-path overlap matrix (verified):**

| Code region | Sprint 25 #1349 site | Priority 5 site | Overlap? |
|---|---|---|---|
| `emit_gams.py:1518-1531` (fx_to_l accumulator) | YES | NO | None |
| `emit_gams.py:1668-1698` (eq_paired_in_mcp) | YES | NO | None |
| `emit_gams.py:1897-1906` (merge .l overrides) | YES | NO | None |
| `emit_gams.py:2230-2243` (piU_x.fx fixup) | NO | YES (Patch site C, optional) | None — different function |
| `complementarity.py:465-513` (comp_up generation) | NO | YES (Patch sites A + B) | None |

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §7 (Sprint 25 #1349 Regression Risk Assessment) — code-path overlap matrix + indirect-risk analysis on `.fx` emission semantics + verification check command for clearlak byte-stability.

**Decision (Unknown 5.3 resolution, binding):** **Regression risk LOW.** Code paths are distinct. Priority 5 changes are inactive for clearlak (no subset/superset bound parameters). **Mitigation codified** as Priority 5 PR pre-merge gate: regenerate `clearlak_mcp.gms` + diff vs current main; expect zero diff. If diff non-zero, root-cause before merge. 11 Tier 0/1 canary byte-stability: also expected (none have subset/superset bound parameters); verified by PR19 widening's CI on Sprint 27 Day 0 (per Task 5 PR19_WIDENING_DESIGN.md).

---

# Category 6: #1224 mine ParamRef IndexOffset

Priority 6 workstream — `src/ad/index_mapping.py` UserWarning on `IndexOffset(ParamRef)`. Can address standalone or bundle with Priority 3 #1385 work.

## Unknown 6.1: Should #1224 be bundled with Priority 3 #1385 (both touch `src/ad/index_mapping.py`), or kept standalone?

### Priority

**Medium** — Bundling could reduce duplicate context-loading / testing effort. Keeping standalone reduces blast radius if Priority 3 #1385 hits REPLAN signal.

### Assumption

#1224 (mine ParamRef IndexOffset) and Priority 3 #1385 (Option 1 short-circuit) share enough infrastructure in `src/ad/index_mapping.py` that bundling them into a single PR reduces total effort vs serial implementation.

### Research Questions

1. Do #1224 and #1385 modify overlapping functions in `src/ad/index_mapping.py`?
2. If bundled, what is the combined effort vs serial (~6–10h + 10–16h)?
3. If #1385 returns Phase 0 REPLAN, can #1224 still be implemented standalone in Sprint 27?
4. Does #1224's fix interact with Priority 3 #1385's redesigned short-circuit logic?

### How to Verify

1. Grep `src/ad/index_mapping.py` for `IndexOffset\|ParamRef\|short_circuit\|symbolic_instance` to identify shared infrastructure.
2. Read `docs/issues/ISSUE_1224_*.md` for the IndexOffset(ParamRef) UserWarning fix shape.
3. If bundled, document combined PR scope in Task 11 schedule.

### Risk if Wrong

- **Bundling adds risk:** If #1385 REPLAN, #1224 also slips; Sprint 27 Solve / Translate target impacted.
- **Serial is correct but bundled chosen:** Duplicate test/regression effort across 2 PRs.

### Estimated Research Time

1 hour (code inspection + issue review)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Sprint 27 Day 0 inspection) — **Decision: STANDALONE (do NOT bundle #1224 with #1385).**

**Day 0 code inspection (`src/ad/index_mapping.py` @ anchor `148662a5`):**

1. **No overlap.** `src/ad/index_mapping.py` contains **zero** `IndexOffset` or `ParamRef` references (grep returns nothing). The #1385 patch site is `enumerate_equation_instances` (`index_mapping.py:377`), which does set-membership **condition filtering** on equation instances — it has no offset-arithmetic code path. (RQ1: the two do not modify overlapping functions.)
2. **The #1224 `IndexOffset(ParamRef)` surface is in a different module.** Offset resolution lives in `src/ad/constraint_jacobian.py` — `_try_eval_offset` (`:133`), the `IndexOffset` index-resolution helpers (`:93`, `:274`, `:1283`), and `src/ad/derivative_rules.py:2793` ("Substitute indices in ParamRef, including IndexOffset bases"). None of these are touched by #1385. (The PR19_WIDENING_DESIGN §8.2 / KNOWN_UNKNOWNS premise that #1224 "touches `src/ad/index_mapping.py`" is imprecise — the actual `IndexOffset(ParamRef)` evaluation code is in `constraint_jacobian.py`/`derivative_rules.py`.)
3. **Blast-radius argument confirms standalone.** Because there is no shared function or even shared module on the critical path, bundling would yield no context/test reuse savings (RQ2) while coupling #1224's fate to #1385's Phase 0 outcome. If #1385 REPLANs, #1224 proceeds unaffected (RQ3 = yes). No interaction between #1224's offset fix and #1385's short-circuit logic (RQ4 = none).

**Schedule impact:** #1224 is **standalone** — NOT bundled with #1385. Per the Option 1 re-plan it **starts Day 11 (PLAN.md §11) and closes Day 12 (§12)** on its own `constraint_jacobian.py`/`derivative_rules.py` surface (the move to Day 11 is the re-plan's slack-driven pull-forward, NOT a bundle with #1385). PLAN.md §3 sequencing constraint 4 ("Priority 6 #1224 may bundle with Priority 3 #1385") resolves to **no bundle**.

---

## Unknown 6.2: After fixing #1224's UserWarning, what is the next failure mode for mine (path_syntax_error, model_infeasible, compare_match, or other)?

### Priority

**Medium** — Sprint 27 PROJECT_PLAN.md explicitly notes "Solve gain is conditional per Sprint 26 retrospective Solve target rationale" for #1224. Knowing the next failure mode before Day 1 lets Sprint 27 plan whether #1224 is a Solve gain (compare_match) or only a Translate gain (downstream failure).

### Assumption

After #1224's UserWarning fix, mine progresses from translate_internal_error to translate_success but hits a downstream failure (likely path_syntax_error or model_infeasible). Sprint 27's Translate target benefits (+1) but Solve target benefit is conditional.

### Research Questions

1. After patching the IndexOffset(ParamRef) UserWarning, does mine translate cleanly?
2. If yes, what does the regenerated `mine_mcp.gms` solve to in PATH (compare_match? path_syntax_error? model_infeasible?)?
3. If a downstream failure, is it a known pattern (e.g., comp_up subset/superset like #1356/#1357, or AD residual like #1334) that Sprint 27 can address as a follow-on?

### How to Verify

1. Patch the UserWarning fix as a prototype (model-name guarded on mine if necessary).
2. Run pipeline on mine: translate + solve.
3. Document the downstream outcome in `docs/issues/ISSUE_1224_*.md` and decide Sprint 27 vs Sprint 28 follow-on.

### Risk if Wrong

- **mine reaches compare_match:** Sprint 27 Solve target +1 (firm); upgrade conditional to firm.
- **mine hits a new failure mode requiring Sprint 28 work:** Translate target +1; Solve target unchanged; carryforward filing needed.

### Estimated Research Time

1 hour (prototype + pipeline run + outcome documentation)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 7: Day 6 Close-and-Refile Carryforwards (#1387 cclinpts + #1388 camshape)

Priority 7 workstream — Both issues marked close-and-refile in Sprint 26 Day 6 with limited investigation depth. Sprint 27 Priority 7 budgets 6–12h; either fix or formal Sprint 28 carryforward filing.

## Unknown 7.1: Is #1387's cclinpts ~70% rel_diff a condition-guard bug, a sign bug, or both?

### Priority

**High** — Fix-surface effort varies significantly: a single condition-guard fix is ~2h; a sign-bug fix is ~3h; both combined is ~5h. Knowing which class of bug is present before Day 1 lets Task 11 schedule Priority 7 within the 6–12h combined budget.

### Assumption

cclinpts's ~70% rel_diff is caused by a condition-guard bug (the wrong domain condition fires during stationarity equation construction) rather than a sign bug (the multiplier sign is inverted). The fix is a single localized change in `src/kkt/stationarity.py` or `src/ad/`.

### Research Questions

1. Does hand-derived KKT for cclinpts's stationarity equation show a sign inversion vs current emit?
2. Does the current emit fire on a wrong domain condition (e.g., missing $cond filter or wrong subset)?
3. Is the ~70% rel_diff explained by a single equation or distributed across multiple equations?
4. Does the fix interact with Priority 1 / Priority 2 work (since cclinpts post-Pattern-A reclassification per Sprint 26 Day 6)?

### How to Verify

1. Phase 0 acceptance gate (Task 2 deliverable): hand-derive KKT for cclinpts's largest-rel-diff stationarity equation.
2. Compare against current `data/gamslib/mcp/cclinpts_mcp.gms` emit.
3. Classify bug: condition-guard, sign, both, or other.
4. Document fix-surface in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md`.

### Risk if Wrong

- **Both condition-guard + sign:** Priority 7's #1387 effort grows to ~5h; Sprint 27 budget still fits, but combined with #1388 may exceed 12h.
- **Other bug class (e.g., AD pipeline issue):** #1387 requires larger redesign; Sprint 28 carryforward.

### Estimated Research Time

1–2 hours (hand-derivation + emit comparison + bug classification)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 2 (Author Missing Phase 0 Acceptance Gates PR20)
**Date:** 2026-05-27

**Findings:** #1387's bug class is **BOTH a sign-flip AND a term-omission** (not pure condition-guard):

- The current `stat_b(j)` emit shows `((-1) * (((-1) * ((fb(j) - fb(j-1)) * 1$((not last(j))))))` — a double-negation that flattens to positive, which is suspected to be a sign bug at the Lagrangian-sign conversion step (Term 1's `-b(j)` factor in source should yield `-(fb(j) - fb(j-1))` after Lagrangian flip, not `+(fb(j) - fb(j-1))`).
- The current `stat_fb(j)` emit shows ONLY the Term-2-at-j contribution `((-1) * (0.5 * (b(j) - b(j-1)) * 1$((not first(j)))))`; it is **MISSING 3 of the 4 expected contributions** (Term 1 at j, Term 1 at j+1, Term 2 at j+1 — all involve `b(j)` or `b(j+1)` factors and the offset-indexed `(fb(j+1) - fb(j))` cross-term).

**Evidence:** Hand-derivation in Phase 0 §"Hand-Derived KKT Shape" of `docs/issues/ISSUE_1387_cclinpts-stat-b-stat-fb-condition-guard-or-sign-bug.md` walks through `∂ObjV/∂b(j)` and `∂ObjV/∂fb(j)` term-by-term and identifies the 3 missing `stat_fb` terms + the suspected double-negation in `stat_b`.

**Decision (REVISED 2026-05-29 per PR #1409 review):** Sprint 27 Priority 7 PROCEED criteria are documented in #1387 Phase 0 §"PROCEED/REPLAN Signal". The bug class is now actionable (sign-flip + term-omission, both fixable in `src/kkt/stationarity.py` or upstream in `src/ad/`). **Effort estimate refined to ~7h** (per Task 8 supplementary below + the §3.5 sub-task arithmetic in `PRIORITY_7_FIX_SURFACE.md` — was misreported as 3–6h in earlier revision); root cause is likely shared with a broader AD-pipeline issue around indexed-sum partial derivatives w.r.t. an index-bound variable — flag for Sprint 27 Day 1 to evaluate whether to bundle with Priority 3 AD redesigns.

**Task 8 supplementary finding (2026-05-28, REVISED 2026-05-29):** Mapped #1387 to specific source-code patch sites at `file:line` precision: **Primary (Bug 2 term-omission)** `src/ad/derivative_rules.py:1847` (`_diff_sum`) + `:577` (`_diff_binary` product-rule). **Secondary (Bug 1 sign-flip)** `src/kkt/stationarity.py:1352` (`build_stationarity_equations`) or `:1835` (`_build_indexed_stationarity_expr`). **Tertiary fallback** `src/ad/constraint_jacobian.py:903` (`_compute_equality_jacobian`). Effort estimate refined to ~7h within Priority 7 budget (per the §3.5 sub-task arithmetic in PRIORITY_7_FIX_SURFACE.md — was misreported as ~6h in the earlier revision). Verified Day 0 baseline: `cclinpts` at `solve=model_optimal, compare=mismatch, rel_diff=1.0` (1.0/100% — drifted from the originally-filed ~70%; emit may have changed in Sprint 25/26 but Phase 0 KKT-derivation analysis is unchanged). **Task 8 verdict: SPRINT 27 FIX binding** (high confidence). Conditional escalation to Sprint 28 ONLY IF Day 1 diagnosis reveals broader AD-architecture issue with `_diff_sum`'s offset-substitution enumeration — in that case, bundle with Priority 3 #1335 Approach C workstream. Evidence in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §3.

---

## Unknown 7.2: Is #1388's camshape Locally Infeasible status an emit bug (fixable) or a fundamental model property (not fixable in Sprint 27)?

### Priority

**High** — Like Sprint 25's abel case (`likely_convex` → `non_convex` reclassification), camshape's Locally Infeasible may be a model property rather than an emit bug. If so, Priority 7's #1388 effort becomes a Sprint 28 carryforward filing rather than a Sprint 27 implementation.

### Assumption

camshape's MODEL STATUS 5 Locally Infeasible is caused by an emit bug (incorrect KKT shape) rather than a fundamental model property (non-convex MCP). Hand-derived KKT comparison will reveal the emit bug, and a Sprint 27 fix exists.

### Research Questions

1. Does hand-derived KKT for camshape match the current `data/gamslib/mcp/camshape_mcp.gms` emit (suggesting fundamental property) or diverge (suggesting emit bug)?
2. Does NLP-warm-start applied to camshape (similar to abel investigation) produce a feasible MCP solution?
3. Is the camshape model itself convex (`gamslib_status.json` convexity status), or is it a known non-convex case?
4. Does the Pattern E reclassification context (Sprint 26 Day 6) suggest the AD residual pattern (like #1334) rather than an emit bug?

### How to Verify

1. Phase 0 acceptance gate (Task 2 deliverable): hand-derive KKT for camshape; compare against current emit.
2. If emit matches hand-derived shape, attempt NLP-warm-start; if still Locally Infeasible, flag as fundamental property.
3. If emit diverges from hand-derived shape, classify as emit bug + document fix-surface.
4. Cross-reference with `gamslib_status.json` convexity status for camshape.

### Risk if Wrong

- **Fundamental property:** Priority 7's #1388 becomes Sprint 28 carryforward filing (~1h prep effort, no Sprint 27 implementation); Sprint 27 Solve / Match targets impacted (no +1 from camshape).
- **Emit bug + complex fix:** Effort 6h+; combined Priority 7 (#1387 + #1388) may exceed 12h budget; either deprioritize one or accept Sprint 28 carryforward.

### Estimated Research Time

1–2 hours (hand-derivation + warm-start experiment + convexity check)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

✅ **Status:** VERIFIED (Phase 0 derivation complete; runtime classification deferred to Sprint 27 Day 0/1 NLP-warm-start experiment per Phase 0 §"PROCEED/REPLAN Signal")
**Verified by:** Task 2 (Author Missing Phase 0 Acceptance Gates PR20)
**Date:** 2026-05-27

**Findings:** Phase 0 hand-derivation for `stat_r(i)` (middle index) identifies **5 specific per-term presence-and-sign checks** (executed via grep against the emit) that distinguish emit bug (case a/b — fixable in Sprint 27) from fundamental model property (case c — Sprint 28 carryforward):

1. Constant `(pi * R_v / n)` objective gradient term presence + sign (Lagrangian-flipped)
2. `lam_convexity(i-1)` cross-term presence with canonical `middle(i-1)` guard (NOT the looser `ord(i) > 1` currently in the emit — `middle(i-1)` implies `ord(i)>2 and ord(i)<=card(i)`; the emit's looser form over-fires at `i=2` where `convexity(1)=convexity(first(i))` doesn't exist, which is itself a suspected bug surface)
3. `lam_convexity(i+1)` cross-term presence with canonical `middle(i+1)` guard (NOT the looser `ord(i) <= card(i) - 1` currently in the emit; same over-fire risk at the `i=card(i)-1` boundary)
4. `nu_eqrdiff(i-1)` (+1) and `nu_eqrdiff(i)` (-1) presence with correct signs
5. The bound-fixup `$(r.up(i) - r.lo(i) > 1e-10)` outer wrap correctness

The Phase 0 §"PROCEED/REPLAN Signal" specifies that the canonical fundamental-property test is the **NLP-warm-started PATH solve**: if PATH converges to MODEL STATUS 1 with `obj ≈ 4.2841` from the NLP starting point but fails to do so from the default starting point, then camshape is starting-point sensitive (case c variant) and Sprint 28 carryforward applies. If even the NLP-warm-started solve fails AND all 5 per-term grep checks above pass (no emit bug), then this is case (c) — fundamental property; Sprint 28 carryforward. If any of the 5 grep checks fails, this is case (a) — fix-and-ship in Sprint 27.

**Evidence:** Hand-derivation in Phase 0 §"Hand-Derived KKT Shape" of `docs/issues/ISSUE_1388_camshape-mcp-locally-infeasible-post-pattern-e-reclassification.md` walks through `∂L/∂r(i)` term-by-term for middle indices. The Phase 0 verification methodology is grep/pattern-based per-term presence-and-sign checks (NOT a literal byte-diff or canonicalized normalization step — the emit may reorder or differently-parenthesize terms vs the canonical hand-derived form), plus the NLP-warm-started PATH solve test.

**Decision (REVISED 2026-05-29 per PR #1409 review):** Sprint 27 Priority 7 prep is at PROCEED-with-condition state — the binding Sprint 27-fix-vs-Sprint-28-carryforward decision requires the FULL §4.6 3-way discriminator (runtime warm-start MODEL STATUS + per-term Phase 0 grep checks for non-inert shape divergence), NOT the runtime warm-start experiment alone. The runtime test by itself only distinguishes Case (a) (MS 1 → Sprint 27 fix) from Cases (b)/(c) (MS 5 → further classification needed). **Revised effort estimates per Task 8 supplementary finding below:** ~4.5h Case (a), ~5.5h Case (b), ~1.25h Case (c) Sprint 28 carryforward filing. **Case (c) requires BOTH conditions:** (i) NLP-warm-start MS 5 AND (ii) per-term Phase 0 grep checks reveal NO non-inert shape divergence (excluding the inert boundary-guard form-mismatch — see Task 8 supplementary below).

**Task 8 supplementary finding (2026-05-28, REVISED 2026-05-29 per PR #1409 review; REVISED again 2026-05-30 per PR #1409 review to account for MCP multiplier warm-start surface):** Verified the current emit shape at `data/gamslib/mcp/camshape_mcp.gms:428` against Phase 0 hand-derivation. The `lam_convexity(i-1)` guard is `$(ord(i) > 1)$(middle(i))` (current) vs `$(middle(i-1))` (canonical) — at i=2 the current guard over-fires; same form mismatch on `lam_convexity(i+1)` guard at i=card(i)-1. **HOWEVER, this guard form-mismatch is NUMERICALLY INERT** (downgraded from "strong suspicion of emit bug" per reviewer): the emit at L464 + L467 fixes `lam_convexity(<non-middle i>) = 0` via `lam_convexity.fx(i)$(not (middle(i))) = 0;` and `lam_convexity.fx(i)$(not ((ord(i) <= card(i) - 1) and (ord(i) > 1))) = 0;`. The over-fired contributions are mathematically `<coefficient> * 0 = 0` and cannot drive PATH to MODEL STATUS 5. The boundary guard form-mismatch is a Phase 0 form-correctness cleanup item but NOT a demonstrated root cause of Locally Infeasible. **Actual cause of Locally Infeasible: UNKNOWN at Day 0 prep stage.** Day 0/1 engineer inspects the default-start failing-solve listing's infeasibility-row report to identify which residual is non-zero and traces back to the originating Python helper. Patch site candidates remain: **Candidate A** `src/kkt/stationarity.py:1835` (`_build_indexed_stationarity_expr`) OR **Candidate B** `src/ad/constraint_jacobian.py:903 + :1027`. Effort refined to **~4.5h Case (a) emit bug + NLP-warm-start solves** (1h diagnosis + 1.5h fix + 0.5h optional guard cleanup + tests/verification), **~5.5h Case (b)** emit bug + warm-start guidance, **~1.25h Case (c)** fundamental property → Sprint 28 carryforward filing. **Task 8 verdict: SPRINT 27 CONDITIONAL** (binding pending Day 0/1 NLP-warm-start runtime test). Day 0/1 engineer warm-starts via a mechanism that initializes BOTH all 3 primals (`r`, `rdiff`, `area`) AND all 7 multipliers (`lam_convexity`, `lam_convex_edge1/3/4`, `nu_eqrdiff`, `piL_r`, `piU_r`) declared at `camshape_mcp.gms:69-78`: (Approach A — RECOMMENDED) regenerate the presolve emit via `.venv/bin/python -m src.cli ... --nlp-presolve -o /tmp/camshape_mcp_presolve.gms` and run that file directly — the emit auto-includes an NLP solve via `$onMultiR $include "camshape.gms"` AND the multiplier-transfer block at `camshape_mcp_presolve.gms:301-309` (`lam_*.l = abs(*.m)`, `nu_eqrdiff.l = eqrdiff.m`, conditional `piL_r.l`/`piU_r.l` at active bounds); or (Approach B — manual fallback) explicit per-instance overrides on the non-presolve emit for ALL 10 warm-startable symbols, matching the L301-309 transfer formulas (especially `abs(...)` wrapping on `lam_*` and conditional bound-marginal guards on `piL_r`/`piU_r`). **A raw `execute_loadpoint '<nlp.gdx>';` of an NLP GDX is INSUFFICIENT** because NLP variables (`convexity`, `convex_edge1/3/4`, `eqrdiff`) have different symbol names from MCP multipliers (`lam_convexity`, `lam_convex_edge1/3/4`, `nu_eqrdiff`), so multipliers stay at zero — driving MS 5 from an incomplete start regardless of any emit bug. **A generic `--starting-point=<file>` GAMS double-dash parameter is ALSO NOT a warm-start mechanism** — the generated `camshape_mcp.gms` does not consume any such user parameter, so PATH would still run from the default `r.l(i) = (R_min + R_max) / 2;` levels at `camshape_mcp.gms:300+`. Full Approach A (presolve emit) + B (manual full-symbol override) workflows + a 10-symbol display-block pre-check are documented in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §4.6. Result interpretation (3-way discriminator per §4.6, only valid AFTER confirming ALL 10 warm-startable symbols — 3 primals (`r.l`, `rdiff.l`, `area.l`) AND 7 multipliers (`lam_convexity.l`, `lam_convex_edge1/3/4.l`, `nu_eqrdiff.l`, `piL_r.l`, `piU_r.l`) — were loaded from NLP solution / NLP marginals): MODEL STATUS 1 with obj≈4.2841 → **Case (a)** Sprint 27 fix; MODEL STATUS 5 AND per-term Phase 0 grep checks reveal a non-inert shape divergence (i.e., other than the inert boundary-guard form-mismatch documented above) → **Case (b)** Sprint 27 fix (emit bug exists; needs warm-start guidance); MODEL STATUS 5 AND no non-inert shape divergence visible → **Case (c)** Sprint 28 carryforward. **A verified-warm-start MODEL STATUS 5 is NOT automatically Case (c)** — the shape-divergence check distinguishes Case (b) (Sprint 27 fix path) from Case (c) (fundamental property); the Day 0/1 engineer MUST perform the per-term grep checks before classifying as carryforward. Evidence in `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §4.

---

## Unknown 7.3: Can both #1387 and #1388 be fixed within Priority 7's combined 6–12h budget, or should one (or both) defer to Sprint 28?

### Priority

**Medium** — Decision driven by Unknowns 7.1 + 7.2. If both fixes are simple (~2–3h each), both fit. If either is complex (~5–8h), one must defer. If both are complex or one is a fundamental property, formal Sprint 28 carryforward filing is needed.

### Assumption

Both #1387 (cclinpts condition-guard) and #1388 (camshape emit bug) are tractable within Priority 7's 6–12h combined budget, with #1387 ~3–4h and #1388 ~3–6h.

### Research Questions

1. From Unknowns 7.1 + 7.2, what is the combined effort estimate for #1387 + #1388?
2. If combined effort > 12h, which has higher Sprint 27 impact (Solve / Match contribution)?
3. If one must defer, what does the formal Sprint 28 carryforward filing look like (Phase 0 + investigation-depth recap + Sprint 28 budget estimate)?
4. Does Sprint 28 PROJECT_PLAN.md already have budget allocated for these carryforwards, or does the deferral push other Sprint 28 work?

### How to Verify

1. Sum effort estimates from Unknowns 7.1 + 7.2 (Task 8 deliverable).
2. If > 12h, prioritize by Sprint 27 Solve / Match impact.
3. File Sprint 28 carryforward in `docs/issues/ISSUE_<N>_*.md` if deferring; label GitHub issue `sprint-28`.

### Risk if Wrong

- **Both fit:** Sprint 27 Solve target +2 (camshape +1, cclinpts +1); good outcome.
- **One deferred:** Sprint 27 Solve target +1; Sprint 28 carryforward filed.
- **Both deferred:** Sprint 27 Solve target unchanged; both carried to Sprint 28; suggests under-investment in Day 6 close-and-refile during Sprint 26.

### Estimated Research Time

1 hour (effort summation + prioritization + carryforward filing if needed)

### Owner

Sprint planning

### Verification Results

✅ **Status:** VERIFIED — combined-budget fit analysis complete (binding for most-likely path)
**Verified by:** Task 8 (#1387 cclinpts + #1388 camshape Fix-Surface Analysis)
**Date:** 2026-05-28

**Findings:**

- **Research Q1 (combined effort estimate):** Per Task 8's per-issue effort breakdown:
  - #1387 cclinpts ~7h (sign-flip diagnosis 1h + sign-flip fix 1h + term-omission diagnosis 1.5h + term-omission fix 1.5h + Tier 0/1 regression 0.5h + PATH solve verification 1h + review buffer 0.5h = 7h total — was misreported as ~6h in earlier revision). Within Priority 7 budget. Risk factor: if Day 1 diagnosis reveals broader AD-architecture issue with `_diff_sum`'s offset-substitution enumeration, escalates to Sprint 28.
  - #1388 camshape ~4.5h Case (a) emit bug + NLP-warm-start solves (incl. 1h Day 0/1 diagnostic step), ~5.5h Case (b) emit bug + warm-start guidance, ~1.25h Case (c) fundamental property + Sprint 28 carryforward filing. **Binding case selected by the FULL §4.6 3-way discriminator** — i.e., the Day 0/1 NLP-warm-start runtime MODEL STATUS (with ALL 10 warm-startable symbols — 3 primals `r.l`, `rdiff.l`, `area.l` AND 7 multipliers `lam_convexity.l`, `lam_convex_edge1/3/4.l`, `nu_eqrdiff.l`, `piL_r.l`, `piU_r.l` — verified loaded per §4.6 10-symbol display-block pre-check) PLUS, when MS = 5, the per-term Phase 0 grep checks for non-inert shape divergence. The runtime test ALONE is INSUFFICIENT to select Case (a/b/c): MS 1 → Case (a); MS 5 + non-inert shape divergence visible → Case (b); MS 5 + NO non-inert shape divergence → Case (c). MS 5 alone never selects Case (c) without the shape-divergence check. **A primals-only warm-start verification is ALSO INSUFFICIENT** — incomplete multiplier starts can independently drive PATH to MS 5 regardless of any emit bug, so the gate must cover all 10 symbols (REVISED 2026-05-29 per PR #1409 review — boundary-guard mechanism downgraded to UNPROVEN; REVISED 2026-05-30 per PR #1409 review — warm-start gate expanded from 3 primals to all 10 warm-startable symbols per KU 7.2 supplementary finding).
- **Research Q2 (priority if exceeds budget):** Both #1387 and #1388 are independently valuable (+1 Match and +1 Solve respectively). If only one fits, **#1388 has higher leverage** (+1 Solve = direct headline metric improvement) but requires the FULL §4.6 3-way discriminator at Day 0/1 to confirm Case (a/b) — i.e., the NLP-warm-start runtime MODEL STATUS (with ALL 10 warm-startable symbols — 3 primals AND 7 multipliers — verified loaded via the §4.6 display-block pre-check) PLUS, when MS = 5, the per-term Phase 0 shape-divergence check; both the runtime test alone AND a primals-only warm-start verification are insufficient. **#1387 has lower leverage** (+1 Match only — solver-side improvement, not headline) but higher fix confidence (binding SPRINT 27 FIX verdict).
- **Research Q3 (carryforward filing template):** Documented in `PRIORITY_7_FIX_SURFACE.md` §6 — formal template includes Sprint 27 Day 0/1 verdict, Phase 0 cross-reference, effort estimate, Sprint 28 priority placement, discriminating evidence, recommended approach. GitHub label updates: `gh issue edit <NNNN> --remove-label sprint-27 --add-label sprint-28`. PROJECT_PLAN.md Sprint 28 §Priority update required.
- **Research Q4 (Sprint 28 budget allocation):** Sprint 28's allocation is undefined at this prep stage; carryforward of either #1387 or #1388 would consume Sprint 28 capacity that's currently unspecified — would need to be reflected in Sprint 28 prep planning if deferred.

**Budget fit table** (per `PRIORITY_7_FIX_SURFACE.md` §5):

| Path | #1387 effort | #1388 effort | Combined | Within 6-12h budget? | Sprint 27 gain |
|---|---|---|---|---|---|
| **Most-likely** (both Sprint 27 fix) | ~7h | ~4.5–5.5h | **~11.5–12.5h** | ⚠️ AT-OR-JUST-ABOVE (upper end edges 0.5h past 12h ceiling; mitigated per PRIORITY_7_FIX_SURFACE.md §5.1 escalation note) | +1 Match + +1 Solve |
| **Mixed** (#1387 fix, #1388 carryforward Case c) | ~7h | ~1.25h | ~8.25h | ✅ YES | +1 Match |
| **Worst** (#1387 AD-architecture escalation + #1388 Sprint 27 fix) | ~1h filing | ~4.5–5.5h | ~5.5–6.5h | ✅ YES (lower end) | +1 Solve |
| **Worst-worst** (both deferred) | ~1h | ~1.25h | ~2.25h | ✅ YES (severely under-utilized) | 0 |

**Note (REVISED 2026-05-29 per PR #1409 review):** #1388 effort estimates REVISED to include a Day 0/1 diagnostic step (~1h) since the boundary-guard hypothesis was disproved (over-fired terms are zeroed by L464+L467 fixups, so they cannot cause Locally Infeasible — the actual root cause is unknown pre-Day 0).

**Evidence:** `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §3 (#1387 patch sites + effort), §4 (#1388 candidate patch sites + 3 cases + UNPROVEN boundary-guard hypothesis), §5 (combined-budget fit table), §6 (Sprint 28 carryforward template).

**Decision (Unknown 7.3, binding for most-likely path):** **Combined Priority 7 effort fits within 6–12h budget for the Mixed / Worst / Worst-worst scenarios; the Most-likely path (~11.5–12.5h) sees its upper end edge ~0.5h past the 12h ceiling on the high estimate.** REVISED 2026-05-29 per PR #1409 review (#1387 corrected to ~7h per §3.5 sub-task arithmetic + #1388 revised to ~4.5–5.5h with the Day 0/1 diagnostic step). Mitigation per PRIORITY_7_FIX_SURFACE.md §5.1 escalation note: trim the 0.5h #1388 optional guard cleanup, OR draw from the Day 13 buffer. Most-likely path: both Sprint 27 fix (+1 Match + +1 Solve). #1387 verdict binding (SPRINT 27 FIX). #1388 verdict conditional (SPRINT 27 CONDITIONAL pending the full §4.6 3-way discriminator: NLP-warm-start runtime test PLUS per-term Phase 0 grep checks for non-inert shape divergence — NOT the runtime test alone). No Sprint 28 carryforward filings needed at this prep stage; carryforward would only trigger conditionally on BOTH (a) NLP-warm-start runtime MS 5 AND (b) per-term Phase 0 grep checks revealing NO non-inert shape divergence (excluding the inert boundary-guard form-mismatch). MS 5 with a non-inert shape divergence is Case (b) — STILL a Sprint 27 fix path. This aligns with Unknown 7.2's Case (b)/(c) split. Case (c) probability is now non-negligible (was "low") since the boundary-guard mechanism for #1388 was disproved.

---

# Category 8: Pipeline Absolute-Path Leak Fix (#1400)

Priority 8 workstream — `scripts/gamslib/run_full_test.py:899` sets the `mcp_file_used` field (`model["mcp_solve"]["mcp_file_used"] = str(presolve_path)`) which serializes an absolute path (since `presolve_path` is `mcp_path.with_name(...)` where `mcp_path` is anchored at `PROJECT_ROOT / "data" / "gamslib" / "mcp" / ...`). This is the only CONFIRMED leak source. **The original Sprint 26 CHANGELOG / PROJECT_PLAN.md attribution of a second leak source to `run_full_test.py:warnings.formatwarning` is INCORRECT** — `grep -lE "warnings\." scripts/gamslib/*.py` returns nothing; no warning-capture logic exists in `scripts/gamslib/`. **The PR22 speculation that GAMS subprocess stderr from `test_solve.py:982-988` might be persisted into the status dict is ALSO WRONG** — `solve_mcp()` at `scripts/gamslib/test_solve.py:911` uses `subprocess.run(..., capture_output=True)` but discards stdout/stderr (no `result = ...` capture); the error stored in `model["mcp_solve"]["error"]["message"]` is synthesized from parsed `.lst` content via `parse_gams_listing(...)`, not from subprocess stderr. The Priority 8 workstream must identify any additional leak fields by direct AUDIT of `gamslib_status.json` for absolute-path substrings (e.g., `grep -E "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json`) rather than speculate (NOTE: Priority 8 has no dedicated prep task in this PREP_PLAN — Task 8 is unrelated, covering #1387/#1388 fix-surface analysis). Note: there is no `scripts/gamslib/solve_mcp.py` file in the repo; `solve_mcp` is a function in `test_solve.py`. Fix to repo-relative paths.

## Unknown 8.1: Beyond `run_full_test.py:899 mcp_file_used`, what is the actual second absolute-path leak source (the Sprint 26 attribution to `warnings.formatwarning` is wrong)?

### Priority

**Medium** — Sprint 26 Day 13 surfaced the `mcp_file_used` leak at `run_full_test.py:899` and attributed a second source to `warnings.formatwarning`, but the latter attribution is incorrect (no `warnings` module usage in `scripts/gamslib/`). A subsequent PR22 speculation pointed at captured subprocess stderr in `scripts/gamslib/test_solve.py:982-988`, but that is also wrong — `solve_mcp()` discards stdout/stderr (`subprocess.run(..., capture_output=True)` without storing the result) and the error string in `model["mcp_solve"]["error"]["message"]` is synthesized from parsed `.lst` content, not from subprocess stderr. The Priority 8 workstream / #1400 implementation must audit `gamslib_status.json` directly to identify any actual second source (NOTE: Priority 8 has no dedicated prep task — Task 8 in this PREP_PLAN is unrelated, covering #1387/#1388). It may turn out that `mcp_file_used` is the only leak; if so, Sprint 27 Priority 8 effort is at the low end of the 2–4h budget. If additional sources are surfaced via the audit, effort may grow; if not caught, `gamslib_status.json` will not be byte-identical across machines post-fix.

### Assumption

Only 1 leak source is currently CONFIRMED: `scripts/gamslib/run_full_test.py:899` mcp_file_used assignment (where `presolve_path` is anchored at `PROJECT_ROOT / "data" / "gamslib" / "mcp" / ...`). The original Sprint 26 CHANGELOG / PROJECT_PLAN.md attribution to `warnings.formatwarning` is wrong (no `warnings` usage in `scripts/gamslib/`), and the subsequent PR22 speculation about captured subprocess stderr is also wrong (`solve_mcp()` discards stdout/stderr and synthesizes the error string from parsed `.lst` content via `parse_gams_listing(...)`). The Priority 8 workstream needs to audit `gamslib_status.json` directly (e.g., `grep -oE "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json | sort -u` — note: the key match must use `"[^"]+"` rather than `"[a-z_]+"` because the JSON contains keys with digits like `_migration_summary_v2_2_1`; a narrower regex could silently under-report) to determine whether `mcp_file_used` is the only leak or whether additional fields also leak. (CHANGELOG.md Sprint 26 Summary + PROJECT_PLAN.md §Sprint 27 Priority 8 are corrected as part of Sprint 27 PR #1402 to remove the wrong `warnings.formatwarning` attribution.)

### Research Questions

1. Beyond the confirmed `run_full_test.py:899 mcp_file_used` leak, does any other field in `gamslib_status.json` contain absolute paths? (Direct-audit approach: grep the JSON for absolute-path substrings — that identifies the real leak fields without speculation.)
2. Does grep across `scripts/gamslib/*.py` for absolute-path constructions (e.g., `Path.cwd()`, `os.path.abspath`, `__file__` without basename, `str(<absolute_path>)` style assignments) find additional source code that produces leaks?
3. Does the `gamslib_status.json` JSON schema documentation list any path fields that should be repo-relative?
4. Will the path-relativization break any downstream consumer of `gamslib_status.json` (e.g., the bucket-provenance baseline scripts from Task 3)?

### How to Verify

1. Run pipeline against 1–2 models (e.g., `chenery` + `abel`) to regenerate `gamslib_status.json`, then audit directly for absolute-path substrings: `grep -oE "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json | sort -u` — each match identifies a real leak field by JSON key name. (Note: the key match uses `"[^"]+"` rather than `"[a-z_]+"` because the JSON contains keys with digits like `_migration_summary_v2_2_1`; a narrower regex could silently miss leak fields whose key names include digits or other characters.)
2. For each leak field found, trace back to the source-code assignment in `scripts/gamslib/*.py` (use `grep -n "<key_name>" scripts/gamslib/*.py`).
3. `grep -rnE "abspath|os.path.realpath|str\(Path.cwd|str\(presolve_path\)|str\(mcp_path\)" scripts/gamslib/` to surface other potential absolute-path construction sites that may not yet be in the status dict but could leak in future schema changes.
4. Test path-relativization against downstream consumers in Task 3's bucket-provenance scripts.

### Risk if Wrong

- **Additional sources discovered:** Priority 8 effort grows by ~1h per source; still within 2–4h budget.
- **Downstream consumer breaks:** Sprint 27 mid-sprint discovery of broken bucket-provenance reports; revert + retry.

### Estimated Research Time

1 hour (corpus grep + JSON schema audit + downstream test)

### Owner

Sprint planning + tooling engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 8.2: Does the path-relativization use `PROJECT_ROOT` (absolute then converted) or basename-only (always `data/gamslib/mcp/<model>_mcp_presolve.gms`)?

### Priority

**Low** — Both approaches achieve cross-machine byte-identical JSON; choice is stylistic / robustness preference. PROJECT_ROOT approach is more general; basename-only is simpler.

### Assumption

Basename-only relativization is sufficient because the mcp file is always at `data/gamslib/mcp/<model>_mcp_presolve.gms` per Sprint 25 #1345/#1346/#1347 cwd convention. PROJECT_ROOT approach is overkill for this single file.

### Research Questions

1. Is the mcp file always at the fixed relative path per the cwd convention, or could it vary (e.g., user-configurable output directory)?
2. Does `PROJECT_ROOT` exist as a constant in the codebase already (yes — see `scripts/gamslib/test_solve.py:987` `cwd=str(PROJECT_ROOT)`), or would Priority 8 need to introduce additional helpers?
3. For any additional leak field identified by Unknown 8.1's direct audit of `gamslib_status.json`, does the field need full PROJECT_ROOT-based relativization (paths may originate from variable locations) or a basename-only approach (since the field references a fixed pipeline output path like `mcp_file_used`)?

### How to Verify

1. Confirm cwd convention in `scripts/gamslib/run_full_test.py` (per #1345/#1346/#1347 — `mcp_file_used` is assigned at line 899 to `str(presolve_path)` where `presolve_path` is constructed at line 701 as `mcp_path.with_name(f"{model_id}_mcp_presolve.gms")`). Also audit `scripts/gamslib/test_solve.py:911 solve_mcp` for cwd / abspath dependency (it uses `cwd=str(PROJECT_ROOT)` per line 987, which is the right pattern).
2. Decide per-leak-source identified by Unknown 8.1's direct JSON audit: basename for fixed-path fields like `mcp_file_used`; PROJECT_ROOT-relative (via `presolve_path.relative_to(PROJECT_ROOT)` or equivalent) for any variable-path fields surfaced by the audit.
3. Document chosen approach in `docs/issues/ISSUE_1400_*.md`.

### Risk if Wrong

- **PROJECT_ROOT approach selected unnecessarily:** Minor over-engineering; no functional impact.
- **Basename approach for variable paths breaks:** Captured subprocess stderr paths become uninformative; minor logging / debuggability loss.

### Estimated Research Time

0.5 hour (cwd convention check + decision)

### Owner

Sprint planning + tooling engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 9: Process Recommendations (PR20/PR21/PR22/PR23) + Emit Duplicate-Init Bugs (#1374)

Cross-cutting process recommendations from Sprint 26 retrospective + Priority 9 (#1374) observation-style sweep.

## Unknown 9.1: Will PR20's hard rule for Phase 0 acceptance gates produce friction on small/tactical PRs (e.g., #1400 pipeline absolute-path leak, #1374 sweep)?

### Priority

**Medium** — PR20 codifies that any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` requires a Phase 0 acceptance-gate section. Sprint 27 has small/tactical PRs (e.g., #1400 in scripts/-only; #1374 emit sweep) where Phase 0 may be overkill. Friction could deter compliance.

### Assumption

PR20's hard rule explicitly scopes Phase 0 to PRs touching `src/ad/`, `src/kkt/`, or `src/emit/` — scripts/ + tests/ + docs/ + CI changes are exempt. #1400 (scripts-only) is exempt; #1374 (touches `src/emit/`) requires Phase 0 but may be reduced-scope (observation-style sweep section rather than full hand-derived KKT).

### Research Questions

1. Does CONTRIBUTING.md §"Phase 0 Acceptance Gates" §"Exception scope" cover scripts/ + tests/ + docs/ + CI?
2. For Priority 9 (#1374) observation-style sweep, is a reduced-scope Phase 0 (e.g., "sweep findings documented + targeted fix patches verified against the affected models") sufficient, or does each fix patch need formal Phase 0?
3. Does the PR20 rule allow PR authors to mark a PR "Phase 0 exempt — scripts only" in the PR description?

### How to Verify

1. Define explicit exception scope in CONTRIBUTING.md (Task 2 deliverable).
2. Apply rule to #1400 (should be exempt) and #1374 (should require reduced-scope Phase 0).
3. Document edge cases in `docs/planning/EPIC_4/SPRINT_27/PR20_CODIFICATION.md` (or inline in CONTRIBUTING.md).

### Risk if Wrong

- **Friction too high:** PR authors bypass rule via "this is a small fix" reasoning; Sprint 28 surfaces new architectural-drift regression.
- **Friction too low:** Phase 0 becomes performative; Sprint 27 mid-sprint regression occurs despite formal compliance.

### Estimated Research Time

1 hour (CONTRIBUTING.md exception drafting + rule application to Sprint 27 PRs)

### Owner

Sprint planning

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 2 (Author Missing Phase 0 Acceptance Gates PR20)
**Date:** 2026-05-27

**Findings:** PR20 codified in CONTRIBUTING.md §"Phase 0 Acceptance Gates" with explicit exception scope covering `scripts/**`, `tests/**`, `docs/**`, `.github/**`, and `data/**`. Friction-management decisions:

- **#1400 (Priority 8 — pipeline absolute-path leak):** EXEMPT per the scripts/-only scope; the actual leak source is `scripts/gamslib/run_full_test.py:899` (verified via Sprint 27 PR #1402 audit), entirely within the exempted `scripts/**` path. No Phase 0 required.
- **#1374 (Priority 9 — emit duplicate-init bugs):** Touches `src/emit/` so requires Phase 0. Reduced-scope: the Phase 0 §"Hand-Derived KKT Shape" subsection becomes "duplicate-init shape catalog" (the per-element-override-after-parameterized-init pattern observed on ganges + corpus-sweep results) rather than a full per-equation Lagrangian derivation. The 4 standard Phase 0 subsections still apply with content adapted to the observation-style nature of the work.
- **PR author "Phase 0 exempt" marker:** Codified — PRs touching ONLY exempted paths note this in PR description (no separate label required; reviewer enforces via PR checklist).
- **Mixed-touch PRs:** A PR that touches BOTH `src/{ad,kkt,emit}/` AND exempted paths still requires Phase 0 for the `src/` portion (explicitly stated in CONTRIBUTING.md §"Exception scope").

**Evidence:** CONTRIBUTING.md §"Phase 0 Acceptance Gates" sections: "The hard rule" (mandatory rule statement), "Why this exists" (2 incident citations: PR #1379 + PR #1394), "Exception scope" (scripts/**, tests/**, docs/**, .github/**, data/**), "Workflow" (5-step author guidance), "Reviewer expectations" (3-bullet reviewer checklist).

**Decision:** Friction risk mitigated by explicit exception scope + the Phase 0 template makes authoring fast (~30-60min per Phase 0 section vs uncapped speculative debugging time post-merge). Sprint 27 PROCEED on all Priority workstreams: Priority 5 (#1356, #1357) + Priority 7 (#1387, #1388) Phase 0 sections authored as part of this Task 2; Priority 8 (#1400) exempt; Priority 9 (#1374) reduced-scope Phase 0 deferred to its issue-doc authoring step.

---

## Unknown 9.2: Will PR21's prep-task end-to-end emit verification template be reusable beyond Sprint 27?

### Priority

**Low** — PR21 codifies an end-to-end emit verification template for prep tasks (translate one concrete target model with a prototype patch + verify GAMS compile-clean + KKT body shape against hand-derived Lagrangian). If the template is Sprint-27-specific, it provides no compounding benefit for Sprint 28+ prep work.

### Assumption

The PR21 template is general — applicable to any future sprint's architectural-redesign prep tasks, not specific to Sprint 27's Priority 3 sub-priorities.

### Research Questions

1. Does the PR21 template depend on Sprint 27-specific tooling (e.g., the specific anchor models, the specific issue numbers)?
2. Can the template be parameterized over model + issue + patch site for reuse?
3. Does Sprint 28 PROJECT_PLAN.md have prep tasks that would benefit from the PR21 template?

### How to Verify

1. Draft the template (Task 6 deliverable or separate PR21 codification document).
2. Apply the template to a Sprint 27 sub-priority (e.g., #1390 validation experiment).
3. Trial-apply the template to a hypothetical Sprint 28 prep task to verify generality.

### Risk if Wrong

- **Sprint-27-specific:** Template provides no compounding benefit; minor documentation overhead.
- **General + reusable:** Compounding benefit across Sprints 28, 29, 30; supports the Epic 4 carryforward closeout.

### Estimated Research Time

0.5 hour (template generality assessment)

### Owner

Sprint planning

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 9.3: Does PR22's audit script handle the cross-sprint timestamp ambiguity from Sprint 26's late carryforward landings (e.g., #1396 PR19 CI, #1398 emit changes)?

### Priority

**Medium** — Sprint 26 Day 12-13 landed multiple late-sprint changes including #1398 (Phase A gate side-effect — the emit-affecting change that produced 15 regenerated `*_mcp.gms` artifacts on Day 13 for the 15 #1398-affected models per CHANGELOG), #1396 (PR19 CI workflow YAML change, not emit), and #1400 (`scripts/gamslib/*` / `gamslib_status.json` path-relativization, not emit). launch's emit was regenerated separately on Day 1 (Phase A landing per PR #1379), not as part of the #1398 sweep — so a full-Sprint-26 dry-run should surface both. Only #1398 + launch produce `data/gamslib/mcp/*.gms` diffs that the PR22 audit script scans for; the script's dry-run validation should target `launch_mcp.gms` (Day 1 Phase A target, separate) + all 15 #1398-affected models' `*_mcp.gms` (Day 13 regenerated — qdemo7 / egypt / ferts / shale / sambal / qsambal / harker / tfordy / dinam / ganges / gangesx / fawley / srpchase / sroute / turkpow), and NOT expect #1400 to appear. The PR22 audit script's git-history query must handle the case where Sprint 27 Day 0 is on a date with mid-day commit boundaries between Sprint 26 and Sprint 27. Note: `git log --since` is date-based and does NOT accept commit SHAs — to use a commit boundary the script must build the query as `git log <sha>..HEAD` instead.

### Assumption

The PR22 audit script accepts two mutually exclusive flags — `--since-date <date>` (date-based, passed to `git log --since`) and `--since-commit <sha>` (commit-based, implemented via `git log <sha>..HEAD`). The Sprint 27 Day 0 commit SHA is the recommended `--since-commit` value for mid-sprint retests, avoiding cross-sprint timestamp ambiguity entirely.

### Research Questions

1. Does the script implement two distinct flags (`--since-date` and `--since-commit`) rather than a single overloaded `--since <date|commit>` (which would be misleading since `git log --since` itself is date-only)?
2. For `--since-date`: what is the timestamp resolution (UTC midnight? local time? second-resolution?) and does it handle the same-day commit boundary?
3. For `--since-commit`: is the input SHA validated against `git rev-parse` before constructing the `<sha>..HEAD` revision range?
4. Should the Sprint 27 Day 0 commit SHA be recorded in `docs/planning/EPIC_4/SPRINT_27/PLAN.md` Day 0 entry for use as the canonical `--since-commit` anchor?

### How to Verify

1. Design the script's CLI to accept `--since-date` + `--since-commit` as mutually exclusive flags (Task 9 deliverable).
2. Document the Sprint 27 Day 0 anchor commit SHA in PLAN.md Day 0.
3. Dry-run the script with both `--since-date "2026-04-22"` and `--since-commit <sprint-26-day-0-sha>` against Sprint 26 history to verify both modes surface the `data/gamslib/mcp/*.gms` artifacts regenerated during Sprint 26. Output MUST INCLUDE AT LEAST: (a) launch artifacts (`launch_mcp.gms` and/or `launch_mcp_presolve.gms` — Phase A target, Day 1 PR #1379; launch is the separate Phase A fix target, NOT one of the 15 #1398-affected models) AND (b) artifacts for all 15 #1398-affected models (Day 13 regenerated: qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow — each contributing `<model>_mcp.gms` and possibly `<model>_mcp_presolve.gms`). Exact artifact count varies because the script scans both `*_mcp.gms` and `*_mcp_presolve.gms` and not every model regenerates both variants in every commit. #1400 is a `scripts/gamslib/*` path-relativization change and will NOT appear in the script's output by design (the script only scans `data/gamslib/mcp/*.gms`).

### Risk if Wrong

- **Ambiguity unhandled:** PR22 script may include or exclude Sprint 26 late-carryforward commits inconsistently; mid-sprint retest review surface incomplete or polluted.
- **Workaround needed:** Sprint 27 mid-sprint prompts must manually specify commit boundaries; defeats the audit-script automation purpose.

### Estimated Research Time

0.5 hour (CLI design + dry-run validation)

### Owner

Sprint planning + tooling engineer

### Verification Results

✅ **Status:** VERIFIED — script implemented + Sprint 26 dry-runs surface the expected #1398 + launch artifacts
**Verified by:** Task 9 (PR22 Mid-Sprint Audit Script Design)
**Date:** 2026-05-30

**Findings:**

- **Research Q1 (two distinct flags?):** YES. CLI exposes `--since-date <DATE>` (date-based; uses `git log --since`) and `--since-commit <SHA>` (commit-based; uses `git log <SHA>..HEAD`) as a mutually exclusive group; exactly one is required. A single overloaded `--since` was rejected because `git log --since` is date-only and an overloaded flag would have to internally dispatch on "looks like a SHA?" heuristics.
- **Research Q2 (`--since-date` timestamp resolution):** Delegated to `git log --since` semantics — accepts ISO-8601 dates, full timestamps, or relative expressions like `"2 days ago"`. Same-day commit-boundary ambiguity is the known limitation; `--since-commit` is the recommended structural mitigation.
- **Research Q3 (`--since-commit` validation):** YES. SHA is validated via `git rev-parse --verify <sha>^{commit}` before constructing the revision range (`scripts/sprint_audit/changed_emit_artifacts.py:96-112`). Invalid SHA produces a clear stderr message + exit code 2.
- **Research Q4 (record Day 0 SHA in PLAN.md?):** YES — this is the canonical mid-sprint workflow. Task 11 will record `Sprint 27 Day 0 anchor SHA: <sha>` in `PLAN.md` Day 0 entry; mid-sprint retests then pass that SHA to `--since-commit`.

**Evidence:** Sprint 26 dry-runs (both `--since-date "2026-04-22"` and `--since-commit 0d8446d2...` — Sprint 26 Day 0 resolved via `git rev-list -1 --before="2026-04-23" main`) surface 19 commits / 209 emit changes / 103 unique paths, INCLUDING:

- **`e0be4fb16e8b`** (Sprint 26 Day 13 final retest): 16 files — all 15 #1398-affected models' `*_mcp.gms` (qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow) PLUS `launch_mcp_presolve.gms`.
- **`8d4cc4acc59c`** (Sprint 26 Day 1 Phase A): 1 file — `launch_mcp.gms` (separate Phase A target, NOT one of the 15 #1398-affected).

**#1400 (`scripts/gamslib/*` path-relativization) intentionally absent** from output — it's not an emit artifact and falls outside `data/gamslib/mcp/`. Confirmed by-design.

**Decision:** Script ready for Sprint 27 mid-sprint use. CONTRIBUTING.md §"Emit-PR `.gms` Diff Workflow (PR22, Sprint 27 Prep Task 9)" documents per-PR + mid-sprint workflows. Validation document at `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md`. KU 9.3 cross-sprint timestamp-ambiguity question is structurally mitigated by the `--since-commit` design.

---

## Unknown 9.4: How widespread is the #1374 emit duplicate-init bug across the 134 translating models?

### Priority

**Low** — #1374 is classified as observation-style in Sprint 27 (Priority 9, 2–4h investigation). If the pattern is widespread (e.g., > 20 models), the targeted fix in `src/emit/` becomes a Sprint 27 Solve-target booster. If isolated (~2–5 models), it remains observation-style with selective fixes.

### Assumption

The #1374 emit duplicate-init bug (e.g., ganges `taum.l('cap-good')` after `taum.l(i)` init) is isolated to a small number of models (< 10) sharing the same emit pattern (per-element override after parameterized init). The targeted fix in `src/emit/` is small (~2h) and benefits Sprint 27 Solve gain by ~1–2.

### Research Questions

1. Does the corpus sweep find < 10 models with the duplicate-init pattern, or is it more widespread?
2. Is the bug a single shape (per-element override after parameterized init) or multiple shapes?
3. Does the Sprint 25 #1349 clearlak fix already address some shapes, or are these distinct from the Sprint 25 fix?
4. Does the targeted fix produce Sprint 27 Solve gain (i.e., do the affected models reach compare_match), or only emit cleanup?

### How to Verify

1. Corpus sweep — find files with two `.l(...)` assignments to the same variable on the same line. Two approaches:

   - **PCRE one-shot (preferred; requires GNU grep with PCRE):** uses `\1` backreference to match the same variable twice without enumerating candidates:

     ```bash
     grep -lP '(\w+)\.l\([^)]+\) = [^;]+;.*\1\.l\([^)]+\) = ' data/gamslib/mcp/*_mcp.gms
     ```

   - **POSIX two-step (portable; works in BSD grep):** first enumerate candidate variables via `.l(...)` assignments, then per-variable grep for duplicates. (POSIX ERE doesn't support backreferences, so a one-shot is not possible; BRE `\1` works but is awkward to write portably.) Example one-liner:

     ```bash
     for f in data/gamslib/mcp/*_mcp.gms; do
       awk -F'.l(' '/\.l\(.*\) = / {n[$1]++} END {for (v in n) if (n[v] > 1) print FILENAME ": " v}' "$f"
     done
     ```

   Both approaches identify files with multiple per-element `.l(idx) = val` assignments to the same variable. Tune as needed to filter for the specific per-element-override-after-parameterized-init shape observed on ganges (`taum.l(i)` parameterized init followed by `taum.l('cap-good') = ...` per-element override).
2. Classify pattern shape per affected model.
3. Estimate Solve gain from the targeted fix.

### Risk if Wrong

- **Widespread (≥ 20 models):** Priority 9 effort grows; Sprint 27 Solve gain potentially +3–5; consider promoting Priority 9 above observation-style.
- **Isolated and no Solve gain:** Priority 9 deferrable to Sprint 28 with minimal cost.

### Estimated Research Time

1 hour (corpus sweep + pattern classification + gain estimation)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Newly Discovered Unknowns (During Sprint 27)

(Populate during sprint execution; migrate into categories post-sprint.)

---

## Confirmed Knowledge (From Sprint 26 and Earlier)

### Pattern C Gate Mechanics (Sprint 26)

- ✅ Phase A consolidated zero-offset builder rewrite (PR #1379) correctly handles launch-shape Pattern C — verified byte-stable on launch
- ✅ Pattern C Phase B reclassification (Day 3): camcge / cesam2 require source-Sum body structure preservation, not Phase A swap-based approach
- ✅ PR19 CI extension (PR #1396) provides PATH-solve regression testing for emit-affecting PRs — the structural mitigation against alias-AD drift

### Phase 0 Acceptance Gate Lessons (Sprint 26)

- ✅ Unit + integration + byte-stability gates are insufficient to catch alias-AD pipeline architectural-drift regressions (PR #1379 + PR #1394 incidents)
- ✅ Hand-derived KKT comparison reliably surfaces architectural-drift regressions that GREEN quality gates miss
- ✅ PR20 codification scope: any issue whose Phase 1 design touches `src/ad/`, `src/kkt/`, or `src/emit/` requires Phase 0 acceptance gate

### AD Pipeline Architecture (Sprints 24–26)

- ✅ Symbolic-vs-concrete index handling is the underlying class of issue for #1381, #1385, #1390, #1393 (KU-38)
- ✅ Element-to-set substitution is upstream of many emit paths and can collapse alias names before downstream handling
- ✅ `_apply_pattern_c_swap_to_term` is launch-shape-specific (Phase A approach); does not generalize to plain-alias bodies

### Scope-Freeze Policy (Sprint 25 → Sprint 26)

- ✅ 142 in-scope models (post-abel reclassification per Sprint 25); convexity reclassifications treated as runtime filters not scope edits
- ✅ Bucket-provenance per-failing-model annotations enable mid-sprint retest analysis (PR17 carryforward into Sprint 27 baseline)

### Pipeline Infrastructure (Sprints 25–26)

- ✅ `scripts/gamslib/run_full_test.py` is reliable for pipeline retests; runtime varies with machine load — Sprint 26 Day 0 was ~3h33m (12779s); Sprint 26 Day 13 retest was ~1h26m (5165.8s) on a faster runner. Budget ~1–3.5h for full-pipeline runs.
- ✅ Pre-Sprint-0 baselining (PR15 scope freeze) prevents mid-sprint scope-shift confusion
- ✅ PR12 byte-stability guard: full pipeline produces byte-identical output under ≥ 3 different `PYTHONHASHSEED` values

---

## Template for New Unknowns

When adding unknowns during Sprint 27:

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

**Before Sprint 27 Day 1:**

1. Review all Critical and High priority unknowns (17 total: 6 Critical + 11 High)
2. Execute verification tests for top unknowns via prep Tasks 2–10 (see Appendix below)
3. Update this document with findings (🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG)
4. Adjust Sprint 27 scope (PROJECT_PLAN.md or PLAN.md) if major assumptions are wrong — specifically, any of Unknowns 1.1, 1.2, 2.1, 3.1, 3.2, 3.3 returning WRONG triggers Sprint 27 replanning during prep
5. Share findings with team during sprint planning (Task 11)

**During Sprint 27:**

1. Reference this document daily (especially Critical / High unknowns)
2. Add newly discovered unknowns in the "Newly Discovered" section above
3. Update verification results as features are implemented
4. Move resolved items to "Confirmed Knowledge" post-sprint

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 27 prep tasks verify which unknowns. Prep Task 11 (Plan Sprint 27 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Author Missing Phase 0 Acceptance Gates (PR20) | 7.1, 7.2, 9.1 | Phase 0 sections for #1356, #1357, #1387 (drives 7.1 hand-derivation), #1388 (drives 7.2 hand-derivation); CONTRIBUTING.md exception scope (drives 9.1) |
| Task 3: Sprint 26 → Sprint 27 Bucket-Provenance Baseline + Scope Freeze (PR15 + PR17) | 1.1 | Day 0 pipeline retest + bucket-provenance diff verifies all 15 #1398-affected models present at expected buckets |
| Task 4: #1398 Widened-Scope Verification + Anchor Model Audit | 1.1 (cross-reference), 1.2, 4.2 | Anchor mapping verifies 8 distinct shapes; cross-references baseline; surfaces any Priority 4 emit-impact on launch anchor |
| Task 5: PR19 Target-List Widening Design | 1.4 | CI runtime projection + Option A/B/C selection |
| Task 6: AD Architectural Redesigns Risk Assessment (PR16 application) | 3.1, 3.2, 3.3, 3.4, 3.5 | Per-sub-priority hypothesis + validation experiment + PROCEED/REPLAN signal; coordinated-design analysis; #1335 approach selection |
| Task 7: comp_up Subset/Superset Fix-Surface Analysis | 5.1, 5.2, 5.3 | Patch site identification; corpus sweep for additional models; clearlak regression risk assessment |
| Task 8: #1387 cclinpts + #1388 camshape Fix-Surface Analysis | 7.1, 7.2, 7.3 | Bug classification; emit-bug-vs-fundamental-property analysis; combined-budget fit decision |
| Task 9: PR22 Mid-Sprint Audit Script Design | 9.3 | CLI design — mutually exclusive `--since-date` (uses `git log --since`) + `--since-commit` (uses `git log <sha>..HEAD`); cross-sprint timestamp handling |
| Task 10: PR23 CI-Workflow PR Self-Review Checklist Authoring | (no specific unknown; design-only) | Drafts checklist based on Sprint 26 PR #1396 review surface |
| Task 11: Plan Sprint 27 Detailed Schedule | (integrates all) | Sprint 27 14-day schedule + day-by-day prompts; absorbs decisions from all prior tasks |

**Cross-cutting unknowns** (not assigned to a single task — verified across multiple prep tasks):

- **Unknown 1.3** (positional information for Priority 1 vs Priority 2) — verified in both Task 4 (anchor-shape analysis) and Task 6 (architectural-overlap analysis between Priority 2 and Priority 3 sub-priorities)
- **Unknown 2.1** (Phase B generalization across camcge / cesam2) — primarily verified through #1381 Phase 0 acceptance-gate work; if Task 2's PR20 codification extends to authoring a Phase 0 section on #1381 (currently not in Task 2's scope but flagged for consideration), this would be Task 2; otherwise verified as part of Sprint 27 Day 0 Phase 0 work for #1381
- **Unknown 2.2** (Priority 1 / 2 sequencing) — verified in Task 4 (cross-references anchor mapping with Priority 2 patch sites) and Task 11 (schedule integration)
- **Unknown 2.3** (Phase B canary byte-stability) — verified in Task 5 (PR19 widening includes canary protection) and during Sprint 27 Day 0 Phase 0 work
- **Unknown 4.1** (launch PATH-numerics fix class) — primarily verified during Sprint 27 Day 0 / Day 1 (NLP-warm-start experiment); Task 4 cross-references for byte-stability impact (Unknown 4.2)
- **Unknown 6.1** (mine + #1385 bundling) — verified in Task 6 (architectural-overlap analysis covers #1385 ↔ #1224 in `src/ad/index_mapping.py`) and Task 11 (schedule integration)
- **Unknown 6.2** (mine downstream failure mode) — verified during Sprint 27 prep prototype (lightweight; part of Task 6 or run as a standalone prep mini-experiment)
- **Unknown 8.1** (additional path-leak sources) — verified in Task 3 (during baseline retest) and Sprint 27 Day 0
- **Unknown 8.2** (PROJECT_ROOT vs basename) — design decision in #1400 implementation; minor; can be made during PR review
- **Unknown 9.2** (PR21 template generality) — primarily verified during Task 6 application + future Sprint 28 prep planning
- **Unknown 9.4** (#1374 sweep widespread) — verified during Sprint 27 Day 8–9 implementation (Task 11 schedule); pre-Sprint sweep can be deferred since Priority 9 is observation-style

**Coverage:** All 28 Sprint 27 prep-time unknowns are assigned to at least one prep task or to early Sprint 27 Day 0 / Day 1 work. Most Critical and High-priority unknowns are assigned to the same task that will act on the findings (e.g., Task 6 verifies all 5 Category 3 unknowns AND its findings drive Task 11's Day 4–9 schedule allocation for Priority 3).

**Carryforward from Sprint 26** (now informing Sprint 27 prep):

- **KU-37** (Phase A gate overreach surface ≥ 15 models) → directly drives Category 1 — see Unknowns 1.1, 1.2, 1.4
- **KU-38** (4 close-and-refile share architectural class) → drives Category 3 coordinated-design analysis — see Unknown 3.4
- **KU-39** (#1335 has 3 competing approaches, requires selection) → drives Category 3 approach selection — see Unknown 3.3

---

**Document Created:** 2026-05-26
**Last Updated:** 2026-05-26
**Total Unknowns:** 28
**Owner:** Sprint 27 Planning Team
**Review Frequency:** Daily during Sprint 27
