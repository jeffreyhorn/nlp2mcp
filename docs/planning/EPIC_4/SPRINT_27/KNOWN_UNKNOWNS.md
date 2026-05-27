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

**Critical** — If 1+ models have self-recovered between Sprint 26 Day 14 and Sprint 27 Day 0 (e.g., a Sprint 26 fix has a delayed effect on dependent models), Priority 1's scope shrinks. Conversely, if Day 0 retest surfaces additional affected models, Priority 1's scope expands. Either case forces a re-budget of Priority 1's 10–14h allocation before Day 1.

### Assumption

All 15 models identified in the Sprint 26 Day 13 #1398 sweep (qdemo7, egypt, ferts, shale, sambal, qsambal, harker, tfordy, dinam, ganges, gangesx, fawley, srpchase, sroute, turkpow) remain in non-compare_match buckets at Sprint 27 Day 0 baseline, and no additional non-target models exhibit the same gate-overreach pattern.

### Research Questions

1. Does Sprint 27 Day 0 pipeline retest reproduce the exact 15-model bucket set from Sprint 26 Day 14?
2. Are there models outside the 15 that exhibit the same gate-overreach pattern (e.g., models that translate but produce wrong-but-compiling emit with similar Phase A consolidated-multiplier shapes)?
3. Has any Sprint 26 post-Day-13 fix (PR #1399 review-driven changes, etc.) silently shifted any of the 15 models' bucket?
4. Does the bucket-provenance baseline (Task 3 of PREP_PLAN.md) capture the Sprint 26 Day 14 → Sprint 27 Day 0 transitions cleanly for all 15 models?

### How to Verify

1. Run `.venv/bin/python scripts/gamslib/run_full_test.py` at Sprint 27 Day 0.
2. Diff resulting `gamslib_status.json` against Sprint 26 Day 14 commit version.
3. For each of the 15 models, confirm bucket has not changed; flag any drift.
4. Grep `data/gamslib/mcp/*_mcp.gms` for the Phase A consolidated-multiplier pattern (e.g., `sum(j$(domain_filter), imat(j,i) * nu_<eq>(j))` style) across all 142 in-scope models; cross-reference against the 15 to identify any non-flagged models.

### Risk if Wrong

- **Scope shrinkage (1+ self-recovered):** Priority 1 budget overestimated; potential reallocation of 1–2h to other priorities.
- **Scope expansion (additional affected models):** Priority 1 budget underestimated; potential 2–4h additional verification effort.
- **Drift in Sprint 26 Day 14 → Sprint 27 Day 0 baseline:** Bucket-provenance baseline becomes unreliable, affecting Sprint 27 progress measurement.

### Estimated Research Time

2–3 hours (pipeline retest + bucket-provenance diff + corpus grep)

### Owner

Sprint planning + AD/KKT engineer

### Verification Results

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

---

# Category 8: Pipeline Absolute-Path Leak Fix (#1400)

Priority 8 workstream — `scripts/gamslib/run_full_test.py:899` sets the `mcp_file_used` field (`model["mcp_solve"]["mcp_file_used"] = str(presolve_path)`) which serializes an absolute path (since `presolve_path` is `mcp_path.with_name(...)` where `mcp_path` is anchored at `PROJECT_ROOT / "data" / "gamslib" / "mcp" / ...`). This is the only CONFIRMED leak source. **The original Sprint 26 CHANGELOG / PROJECT_PLAN.md attribution of a second leak source to `run_full_test.py:warnings.formatwarning` is INCORRECT** — `grep -lE "warnings\." scripts/gamslib/*.py` returns nothing; no warning-capture logic exists in `scripts/gamslib/`. **The PR22 speculation that GAMS subprocess stderr from `test_solve.py:982-988` might be persisted into the status dict is ALSO WRONG** — `solve_mcp()` at `scripts/gamslib/test_solve.py:911` uses `subprocess.run(..., capture_output=True)` but discards stdout/stderr (no `result = ...` capture); the error stored in `model["mcp_solve"]["error"]["message"]` is synthesized from parsed `.lst` content via `parse_gams_listing(...)`, not from subprocess stderr. The Priority 8 workstream must identify any additional leak fields by direct AUDIT of `gamslib_status.json` for absolute-path substrings (e.g., `grep -E "\"[^\"]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json`) rather than speculate (NOTE: Priority 8 has no dedicated prep task in this PREP_PLAN — Task 8 is unrelated, covering #1387/#1388 fix-surface analysis). Note: there is no `scripts/gamslib/solve_mcp.py` file in the repo; `solve_mcp` is a function in `test_solve.py`. Fix to repo-relative paths.

## Unknown 8.1: Beyond `run_full_test.py:899 mcp_file_used`, what is the actual second absolute-path leak source (the Sprint 26 attribution to `warnings.formatwarning` is wrong)?

### Priority

**Medium** — Sprint 26 Day 13 surfaced the `mcp_file_used` leak at `run_full_test.py:899` and attributed a second source to `warnings.formatwarning`, but the latter attribution is incorrect (no `warnings` module usage in `scripts/gamslib/`). A subsequent PR22 speculation pointed at captured subprocess stderr in `scripts/gamslib/test_solve.py:982-988`, but that is also wrong — `solve_mcp()` discards stdout/stderr (`subprocess.run(..., capture_output=True)` without storing the result) and the error string in `model["mcp_solve"]["error"]["message"]` is synthesized from parsed `.lst` content, not from subprocess stderr. The Priority 8 workstream / #1400 implementation must audit `gamslib_status.json` directly to identify any actual second source (NOTE: Priority 8 has no dedicated prep task — Task 8 in this PREP_PLAN is unrelated, covering #1387/#1388). It may turn out that `mcp_file_used` is the only leak; if so, Sprint 27 Priority 8 effort is at the low end of the 2–4h budget. If additional sources are surfaced via the audit, effort may grow; if not caught, `gamslib_status.json` will not be byte-identical across machines post-fix.

### Assumption

Only 1 leak source is currently CONFIRMED: `scripts/gamslib/run_full_test.py:899` mcp_file_used assignment (where `presolve_path` is anchored at `PROJECT_ROOT / "data" / "gamslib" / "mcp" / ...`). The original Sprint 26 CHANGELOG / PROJECT_PLAN.md attribution to `warnings.formatwarning` is wrong (no `warnings` usage in `scripts/gamslib/`), and the subsequent PR22 speculation about captured subprocess stderr is also wrong (`solve_mcp()` discards stdout/stderr and synthesizes the error string from parsed `.lst` content via `parse_gams_listing(...)`). The Priority 8 workstream needs to audit `gamslib_status.json` directly (e.g., `grep -oE "\"[a-z_]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json | sort -u`) to determine whether `mcp_file_used` is the only leak or whether additional fields also leak. (CHANGELOG.md Sprint 26 Summary + PROJECT_PLAN.md §Sprint 27 Priority 8 are corrected as part of Sprint 27 PR #1402 to remove the wrong `warnings.formatwarning` attribution.)

### Research Questions

1. Beyond the confirmed `run_full_test.py:899 mcp_file_used` leak, does any other field in `gamslib_status.json` contain absolute paths? (Direct-audit approach: grep the JSON for absolute-path substrings — that identifies the real leak fields without speculation.)
2. Does grep across `scripts/gamslib/*.py` for absolute-path constructions (e.g., `Path.cwd()`, `os.path.abspath`, `__file__` without basename, `str(<absolute_path>)` style assignments) find additional source code that produces leaks?
3. Does the `gamslib_status.json` JSON schema documentation list any path fields that should be repo-relative?
4. Will the path-relativization break any downstream consumer of `gamslib_status.json` (e.g., the bucket-provenance baseline scripts from Task 3)?

### How to Verify

1. Run pipeline against 1–2 models (e.g., `chenery` + `abel`) to regenerate `gamslib_status.json`, then audit directly for absolute-path substrings: `grep -oE "\"[a-z_]+\": \"/[^\"]+\"" data/gamslib/gamslib_status.json | sort -u` — each match identifies a real leak field by JSON key name.
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

🔍 **Status:** INCOMPLETE

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

🔍 **Status:** INCOMPLETE

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

1. Corpus sweep: `grep -lE "(var)\.l\(([^)]+)\) = [^;]+;.*(var)\.l\(([^)]+)\) = " data/gamslib/mcp/*_mcp.gms` (approximate pattern; tune to find per-element duplicates).
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
