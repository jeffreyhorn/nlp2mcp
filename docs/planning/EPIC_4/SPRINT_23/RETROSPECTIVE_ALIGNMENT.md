# Sprint 22 Retrospective Alignment for Sprint 23

**Created:** 2026-03-20
**Source:** `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md`
**Cross-reference:** `docs/planning/EPIC_4/SPRINT_23/PREP_PLAN.md`, `docs/planning/EPIC_4/SPRINT_23/KNOWN_UNKNOWNS.md`

---

## 1. "What Could Be Improved" Items

### WCI-1: path_solve_terminated Target Was Too Aggressive

**Retrospective finding:** Target ≤ 5 (from 12) assumed most models had pre-solver fixes. Many have genuine solver convergence issues. Achieved 10 (missed by 5). Future targets should be calibrated against actual root cause distribution.

**Sprint 23 action:** Prep Task 2 (TRIAGE_PATH_SOLVE_TERMINATED.md) completed root cause classification for all 10 models. Finding: 6 execution errors (B), 2 MCP pairing errors (A), 1 already solved, 1 PATH convergence (C). Sprint 23 targets 7 models (Tiers 1+2), aiming for 10 → 3. The target is calibrated against actual root causes, not assumptions.

**Status:** ADDRESSED — triage-first approach directly implements this recommendation.

### WCI-2: WS1 Days 2-3 Were Skipped (G+B Subcategories)

**Retrospective finding:** Subcategories G (set index reuse) and B (domain violations) were planned for Days 2-3 but redirected to WS2/WS3. 6 subcategory G+B models left unaddressed. Should be carried into Sprint 23.

**Sprint 23 action:** Prep Task 6 (TRIAGE_PATH_SYNTAX_ERROR_GB.md) completed triage. Revised count: 1 G + 4 B = 5 models (not 6). Sprint 23 Priority 4 targets these; note that the G+B model counts in PROJECT_PLAN.md §Priority 4 are outdated (still showing the earlier 7-model subset), and the authoritative updated count is TRIAGE_PATH_SYNTAX_ERROR_GB.md (1 G + 4 B = 5).

**Status:** ADDRESSED — carried forward as Priority 4 with full triage.

### WCI-3: Full Pipeline vs Partial Pipeline Numbers Diverged

**Retrospective finding:** Day 11 partial pipeline showed solve 80/match 41; Day 13 full pipeline showed solve 89/match 47. Partial metrics were misleading. Recommendation: always use full pipeline for definitive metrics.

**Sprint 23 action:** This became Process Recommendation PR6. Task 8 established baseline using full pipeline. PROJECT_PLAN.md §Pipeline Retest mandates "full pipeline run at each checkpoint and final (per PR6)." BASELINE_METRICS.md was created with full pipeline.

**Status:** ADDRESSED — PR6 integrated into Sprint 23 process. See §3 below.

### WCI-4: model_infeasible Net Change Was Zero Despite Significant Work

**Retrospective finding:** WS3 fixed several models but new models entered infeasible from other stages. "Net zero" masks real progress. Recommendation: track both gross fixes and gross influx separately.

**Sprint 23 action:** This became Process Recommendation PR7. PROJECT_PLAN.md §Priority 2 states "track gross fixes and gross influx per PR7." Prep Task 3 (TRIAGE_MODEL_INFEASIBLE.md) established the baseline of 12 in-scope models. KU-08 specifically tracks whether 4+ gross fixes are achievable.

**Status:** ADDRESSED — PR7 integrated into Sprint 23 process. See §3 below.

### WCI-5: Parse Success Percentage Declined Due to Corpus Growth

**Retrospective finding:** Parse went 154/157 → 156/160. Gained 2 models but denominator grew, lowering percentage. Recommendation: use absolute counts alongside percentages.

**Sprint 23 action:** This became Process Recommendation PR8. BASELINE_METRICS.md reports both absolute counts and percentages. PROJECT_PLAN.md acceptance criteria uses both formats (e.g., "≥ 156/160 (maintain 97.5%)").

**Status:** ADDRESSED — PR8 integrated into Sprint 23 process. See §3 below.

---

## 2. "What We'd Do Differently" Items

### WDD-1: Execute WS1 Subcategories G+B Before Moving to WS2

**Retrospective finding:** Completing all WS1 subcategories first would have provided a cleaner path_syntax_error baseline for Checkpoint 1.

**Sprint 23 action:** Prep Task 6 triaged all G+B models. Sprint 23 Priority 4 is explicitly scheduled. The detailed schedule (Task 10) should consider sequencing G+B fixes early to avoid repeating the skip pattern.

**Status:** ADDRESSED — triage complete; scheduling recommendation for Task 10.

### WDD-2: Run Full Pipeline at Every Checkpoint

**Retrospective finding:** Checkpoints 1 and 2 used `--only-solve` for speed, but partial numbers were misleading.

**Sprint 23 action:** PROJECT_PLAN.md §Pipeline Retest: "Full pipeline run at each checkpoint and final (per PR6)." Task 8 demonstrated this with the baseline run (~76 min). The additional ~1h cost per checkpoint is explicitly accepted.

**Status:** ADDRESSED — mandated in Sprint 23 process.

### WDD-3: Plan for model_infeasible Influx Explicitly

**Retrospective finding:** KU-24 (path_syntax_error → model_infeasible cascade) was correctly identified but underestimated. Recommendation: budget 50% more model_infeasible capacity when targeting path_syntax_error reductions.

**Sprint 23 action:** KU-05 (cascade risk from PST fixes) and KU-08 (gross fix budget) directly address this. Task 3 triage estimates Tier 1 delivers 5 gross fixes, budgeting headroom for influx. The 12 → ≤ 8 target requires net -4, but the plan budgets for 5+ gross fixes (Tier 1) plus 2 more (Tier 2), anticipating 1-3 models of influx.

**Status:** ADDRESSED — influx budgeting embedded in triage and KU tracking.

---

## 3. Process Recommendations Integration

### PR6: Full Pipeline for All Definitive Metrics

| Integration Point | Evidence |
|-------------------|----------|
| Task 8 baseline | Full pipeline run, 147 candidates, ~76 min (BASELINE_METRICS.md) |
| PROJECT_PLAN.md | §Pipeline Retest: "Full pipeline run at each checkpoint and final (per PR6)" |
| Acceptance criteria | All metrics in PROJECT_PLAN.md reference full pipeline denominators |
| Sprint 23 checkpoints | Task 10 should mandate full pipeline at Checkpoint 1 (Day 5) and Checkpoint 2 (Day 10) |

**Status:** INTEGRATED

### PR7: Gross Fixes/Influx Tracking for model_infeasible

| Integration Point | Evidence |
|-------------------|----------|
| Task 3 triage | TRIAGE_MODEL_INFEASIBLE.md classifies all 12 models, estimates gross fixes per tier |
| KU-08 | Tracks "4+ gross fixes needed for ≤ 8 target" |
| KU-05 | Tracks cascade risk (influx from PST fixes) |
| PROJECT_PLAN.md | §Priority 2: "track gross fixes and gross influx per PR7" |
| BASELINE_METRICS.md §5 | model_infeasible broken down into 12 in-scope + 3 permanently excluded |

**Status:** INTEGRATED

### PR8: Absolute Counts for Parse Success

| Integration Point | Evidence |
|-------------------|----------|
| BASELINE_METRICS.md | Reports "156/160 (97.5%)" — both absolute and percentage |
| PROJECT_PLAN.md | Acceptance criteria: "≥ 156/160 (maintain 97.5%)" |
| PREP_PLAN.md targets | Uses absolute counts for all metrics |

**Status:** INTEGRATED

---

## 4. Sprint 22 Suggested Targets vs Sprint 23 Planning

The retrospective §Sprint 23 Recommendations suggested targets. Here is the alignment:

| Metric | Retro Suggestion | PROJECT_PLAN.md Target | BASELINE_METRICS.md (Baseline → Target) | Aligned? |
|--------|-----------------|----------------------|----------------------------------------|----------|
| Parse | ≥ 156/160 | ≥ 156/160 | 156/160 → ≥ 156/160 | Yes |
| Translate | ≥ 145/156 (93%) | ≥ 145/156 (93%) | 139/156 → ≥ 145/156 | Yes |
| Solve | ≥ 100 | ≥ 100 | 89 → ≥ 100 | Yes |
| Match | ≥ 55 | ≥ 55 | 47 → ≥ 55 | Yes |
| path_syntax_error | ≤ 15 | ≤ 15 | 18 → ≤ 15 | Yes |
| path_solve_terminated | ≤ 5 | ≤ 5 | 10 → ≤ 5 | Yes |
| model_infeasible | ≤ 8 (in-scope) | ≤ 8 (in-scope) | 12 → ≤ 8 | Yes |
| Tests | ≥ 4,300 | ≥ 4,300 | 4,209 → ≥ 4,300 | Yes |

**All suggested targets are aligned between the retrospective, PROJECT_PLAN.md, and BASELINE_METRICS.md.**

---

## 5. Sprint 22 Deferred Items Tracking

| Deferred Item | Sprint 22 Source | Sprint 23 Action | Status |
|---------------|-----------------|-----------------|--------|
| Subcategory G+B (WS1 Days 2-3) | WCI-2, WDD-1 | Priority 4; Task 6 triage complete | ADDRESSED |
| path_solve_terminated ≤ 5 | Objective 6 (missed) | Priority 1; Task 2 triage complete | ADDRESSED |
| model_infeasible influx budget | WCI-4, WDD-3 | Priority 2 + PR7; Task 3 triage complete | ADDRESSED |
| Alias-aware differentiation (#1111) | KU-27 → KU-12 | Priority 3; Task 4 design complete | ADDRESSED |
| Dollar-condition propagation (#1112) | KU-28 → KU-14 | Priority 3; Task 5 design complete | ADDRESSED |
| Non-convex multi-KKT (#1111 related) | KU-29 → KU-16 | Deferred — irreducible subset; monitor | DEFERRED (intentional) |
| Multi-solve incomparable | KU-30 → KU-26 | Task 8 verified; no action needed | VERIFIED |

---

## 6. Sprint 22 Process Recommendation Continuity

Sprint 22 also reviewed Sprint 20's process recommendations (PR1-PR5). Status for Sprint 23:

| Recommendation | Sprint 22 Assessment | Sprint 23 Status |
|----------------|---------------------|-----------------|
| PR1: Standardize pipeline denominator (160) | Effective | CONTINUE — BASELINE_METRICS.md uses 160 |
| PR2: Record PR numbers immediately | Effective | CONTINUE — SPRINT_LOG.md to be initialized in Task 10 |
| PR3: Full pipeline at checkpoints | Partially followed | UPGRADED to PR6 (full pipeline for all definitive metrics) |
| PR4: Targeted solve on newly-parsing models | Effective | CONTINUE |
| PR5: Full error category breakdown | Effective | CONTINUE — BASELINE_METRICS.md includes full breakdown |

---

## 7. KU Verification Cross-Check (Tasks 2-8)

All 26 KUs have been verified through Tasks 2-8. Appendix C in KNOWN_UNKNOWNS.md is complete.

### Verification Summary

| Status | Count | KUs |
|--------|-------|-----|
| ✅ VERIFIED | 12 | KU-01, KU-02, KU-03, KU-09, KU-10, KU-13, KU-15, KU-19, KU-20, KU-22, KU-23, KU-26 |
| ⚠️ PARTIAL | 11 | KU-04, KU-05, KU-06, KU-07, KU-08, KU-11, KU-12, KU-16, KU-17, KU-18, KU-21 |
| ❌ REFUTED | 3 | KU-14, KU-24, KU-25 |

**Total: 26/26 verified (no INCOMPLETE entries remain)**

### PARTIAL KUs — Risk Assessment

PARTIAL status means the unknown was investigated but the original assumption was only partially correct. These carry residual risk into Sprint 23:

| KU | Risk | Mitigation |
|----|------|-----------|
| KU-04 | CGE models (dyncge/twocge) have high cascade risk | Deferred to Tier 3; tracked |
| KU-05 | 2-3 models may cascade from PST fixes to model_infeasible | Track per PR7 |
| KU-06 | model_infeasible split is 5 KKT / 6 PATH / 1 feature (not "primarily KKT") | Tier 1 targets 5 KKT models |
| KU-07 | pak/spatequ/sparta have independent root causes | Independent investigation per model |
| KU-08 | Need 4+ gross fixes; Tier 1 delivers 5 but influx possible | Track gross vs influx per PR7 |
| KU-11 | CES singularity is structural, not KKT bug | Deferred to Tier 3 |
| KU-12 | Alias differentiation design sound but untested | Implementation + pipeline testing in Sprint 23 |
| KU-16 | ~12 non-convex models; some may be alias bugs | Clearer after alias fix |
| KU-17 | Convex models should match after alias fix | Need formal convexity check |
| KU-18 | Only 1 G model (srkandw), not 2 as estimated | Triage doc has correct count |
| KU-21 | tricp is NOT low-effort (4-6h); defer unless schedule permits | Target gtm instead |

### Task-to-KU Verification Completeness

| Task | KUs Assigned | KUs Verified | Complete? |
|------|-------------|-------------|-----------|
| Task 2 (path_solve_terminated) | KU-01, KU-02, KU-03, KU-04, KU-05 | All 5 | ✅ |
| Task 3 (model_infeasible) | KU-06, KU-07, KU-08, KU-09, KU-10, KU-11 | All 6 | ✅ |
| Task 4 (Alias Differentiation) | KU-12, KU-13, KU-15, KU-16, KU-17 | All 5 | ✅ |
| Task 5 (Dollar-Condition) | KU-14, KU-15 | Both | ✅ |
| Task 6 (path_syntax_error G+B) | KU-18, KU-19, KU-20, KU-21 | All 4 | ✅ |
| Task 7 (Translate Failures) | KU-22, KU-23, KU-24, KU-25 | All 4 | ✅ |
| Task 8 (Full Pipeline Baseline) | KU-26 | 1 | ✅ |

**All 26 KUs verified. No gaps found.**

---

## 8. Gaps Identified

### No Critical Gaps Found

All Sprint 22 retrospective items — 5 "What Could Be Improved," 3 "What We'd Do Differently," 3 new process recommendations (PR6-PR8), 5 continuing process recommendations (PR1-PR5), all suggested targets, and all deferred items — are captured in Sprint 23 planning through PROJECT_PLAN.md, PREP_PLAN.md, and the prep task deliverables.

### Minor Observations (Non-Blocking)

1. **Translate baseline discrepancy:** BASELINE_METRICS.md records 139/156 (89.1%) vs retrospective's 141/156 (90.4%). This is explained by borderline timeout variance (see BASELINE_METRICS.md §4 and PREP_PLAN.md Task 8 Result). The Sprint 23 translate target (≥ 145/156) accounts for this.

2. **path_solve_terminated target calibration:** WCI-1 recommends calibrating against root causes. Task 2 provides this calibration (Tiers 1-3). However, the PROJECT_PLAN.md target (≤ 5) is the same as Sprint 22's missed target. Task 2's recommendation is 10 → 3 (target 7 models), which is more aggressive than ≤ 5 — this is acceptable because the triage now backs the ambition.

3. **Sprint 22 workstream effort estimates vs actuals:** Several WS effort estimates were significantly off (WS2: planned 6-10h, actual ~12h; WS3: planned 4-8h, actual ~10h). Task 10 should factor this into Sprint 23 scheduling. The prep task triage estimates reflect this lesson (Task 2: 11-18h for 7 models; Task 3: 14-19h for Tier 1).

---

**Document Created:** 2026-03-20
**Conclusion:** All Sprint 22 retrospective items are addressed in Sprint 23 planning. No gaps requiring additional prep work. Ready for Task 10 (Detailed Schedule).
