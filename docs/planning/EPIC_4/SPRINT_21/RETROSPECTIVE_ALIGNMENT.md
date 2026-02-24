# Sprint 20 Retrospective → Sprint 21 Alignment

**Date:** 2026-02-24
**Source:** `docs/planning/EPIC_4/SPRINT_20/SPRINT_RETROSPECTIVE.md`
**Purpose:** Verify all Sprint 20 retrospective action items are addressed in Sprint 21 planning

---

## 1. Process Recommendations (5 items)

### PR1: Standardize pipeline denominator to 160

**Source:** Retrospective lines 353
**Action:** Use 160 (parse-attempted) as canonical reference, not 158 (convexity-filtered).

**Status:** ADDRESSED
**Where:** `BASELINE_METRICS.md` uses 160 consistently throughout all sections. `PREP_PLAN.md` executive summary uses 160. Sprint 21 targets in `PROJECT_PLAN.md` use /160 denominator.
**Verification:** Confirmed in Task 8 — all baseline metrics use 160 denominator.

---

### PR2: Record PR numbers immediately after merge

**Source:** Retrospective lines 355
**Action:** Avoid leaving "PR: TBD" in sprint logs; record PR number in same commit as day's work.

**Status:** PLANNED (Task 10; addressed in plan, not yet encoded)
**Where:** Sprint 21 execution prompts should include "update SPRINT_LOG.md with PR number" as a post-merge step. This is a process discipline item for Task 10 (detailed schedule) to encode into day-by-day prompts.
**Action for Task 10:** Include explicit "record PR number in SPRINT_LOG.md" instruction in each day's execution prompt.

---

### PR3: Verify parse claims end-to-end with pipeline parse stage

**Source:** Retrospective lines 357
**Action:** Do not use `parse_file()` (grammar-only) as proof that a model "parses". End-to-end verification must use the full pipeline parse stage (`parse_model_file()` + `validate_model_structure()`), i.e., the pipeline retest as ground truth.

**Status:** ADDRESSED
**Where:** Sprint 21 Prep Task 8 (Baseline Metrics) ran the full pipeline retest (`parse_model_file()` + `validate_model_structure()`) as ground truth. Sprint 21 execution should use this pipeline retest at checkpoints, not ad-hoc grammar checks or `parse_file()` alone.
**Action for Task 10:** Include full pipeline parse-stage retest (`parse_model_file()` + `validate_model_structure()`) at checkpoint gates (not just end-of-sprint) when asserting that models "parse".

---

### PR4: Run targeted solve on newly-parsing models

**Source:** Retrospective lines 359
**Action:** Don't wait for checkpoints to discover solve issues. Run `--only-solve` after each parse-improvement PR.

**Status:** ADDRESSED
**Where:** Sprint 21 prep identified this gap — Sprint 20 had no new solve successes in Phase 3 (Days 12-14) despite +2 parse successes. The Task 4 path_syntax_error catalog and Task 6 solve-match gap analysis provide solve-readiness data for newly-parsing models.
**Action for Task 10:** Include "test newly-parsing models through full pipeline" after each parse-improvement day. Define solve-improvement checkpoint gates alongside parse checkpoints.

---

### PR5: Track error category migration

**Source:** Retrospective lines 361
**Action:** As lexer errors decrease, models shift to later-stage failures. Track transitions to prevent surprise backlogs.

**Status:** ADDRESSED
**Where:** Sprint 21 Prep Tasks 3 (internal_error catalog), 4 (path_syntax_error catalog), and 7 (semantic error audit) all document current error populations. `BASELINE_METRICS.md` Section 3 breaks down all 28 parse failures by category. `KNOWN_UNKNOWNS.md` Unknown 7.1 explicitly tracks the "waterfall" effect for newly-parsing models.
**Action for Task 10:** Include error category counts at each checkpoint gate, not just parse/solve/match totals.

---

## 2. "What Could Be Improved" Lessons (5 items)

### WCI1: Day 8 parse count claims were overstated

**Source:** Retrospective lines 101-106
**Lesson:** turkey and turkpow were reported as parsing on Day 8 but failed in the Day 14 retest. Claims were based on partial preprocessor output, not full end-to-end parse.

**Status:** ADDRESSED (by PR3)
**Where:** Process Recommendation PR3 (verify parse claims end-to-end via `parse_model_file()` + `validate_model_structure()`, not `parse_file()` alone) directly addresses this. Additionally, the Sprint 21 baseline (Task 8) was established via full pipeline retest, not partial checks.

---

### WCI2: Pipeline denominator inconsistency (158 vs 160)

**Source:** Retrospective lines 107-112
**Lesson:** Sprint 20 plan used /160, but pipeline script filtered to 158 "convex" candidates, causing confusion.

**Status:** ADDRESSED (by PR1)
**Where:** Process Recommendation PR1 standardizes on 160. Task 8 baseline confirms 160 as the denominator. The pipeline script now processes all 160 models (confirmed in Task 8 retest).

---

### WCI3: Some PR numbers not recorded in sprint log

**Source:** Retrospective lines 113-117
**Lesson:** Days 9, 10, 12, 13 had "PR: TBD" initially, backfilled later.

**Status:** ADDRESSED (by PR2)
**Where:** Process Recommendation PR2 requires immediate PR number recording. Sprint 21 prompts should enforce this.

---

### WCI4: internal_error category growth (2 → 7)

**Source:** Retrospective lines 119-123
**Lesson:** Parse-stage internal_error grew from 2 to 7 as models that previously failed at lexer stage progressed further. This is the "waterfall" effect.

**Status:** ADDRESSED
**Where:** Sprint 21 Prep Task 3 created `INTERNAL_ERROR_CATALOG.md` with full root cause analysis of all 7 models. Sprint 21 Priority 2 (6-10h) explicitly targets these 7 models. `KNOWN_UNKNOWNS.md` Category 2 has 3 unknowns covering this population, all verified during prep.

---

### WCI5: No new solve successes in Phase 3 (Days 12-14)

**Source:** Retrospective lines 125-129
**Lesson:** Days 12-14 added 2 parse successes but no solve successes. Earlier identification of solve-blocking issues might have pushed the count higher.

**Status:** ADDRESSED (by PR4)
**Where:** Process Recommendation PR4 (run targeted solve on newly-parsing models) addresses this. Sprint 21 Prep Task 4 (path_syntax_error catalog) and Task 6 (solve-match gap analysis) provide solve-readiness data. Sprint 21 workstreams explicitly include solve quality improvement (Priority 3) and match rate improvement (Priority 5).

---

## 3. Technical Priorities (5 items)

### TP1: `%macro%` expansion in preprocessor

**Source:** Retrospective lines 302-309
**Scope:** saras (`%system.nlp%`), springchain (`$set`/`$eval`/`%N%`/`%NM1%`), 4-8h

**Status:** ADDRESSED
**Where:** Sprint 21 Priority 1 (from `PROJECT_PLAN.md`). Prep Task 2 researches GAMS macro expansion semantics and produces a design document. `KNOWN_UNKNOWNS.md` Category 1 has 4 unknowns (1.1-1.4) covering macro expansion scope, corpus survey, system macros, and preprocessing order. Issues #837 and #840 are tracked.

---

### TP2: internal_error triage (7 models)

**Source:** Retrospective lines 311-317
**Scope:** clearlak, imsl, indus, sarf, senstran, tfordy, turkpow, 6-10h

**Status:** ADDRESSED
**Where:** Sprint 21 Priority 2. Prep Task 3 created `INTERNAL_ERROR_CATALOG.md` with 5 distinct root causes classified, effort estimated per subcategory, and recommended fix order (lead/lag first for 3-model batch fix). `KNOWN_UNKNOWNS.md` Category 2 unknowns all verified.

---

### TP3: Solve quality / path_syntax_error (45 models)

**Source:** Retrospective lines 319-325
**Scope:** Reduce 45 path_syntax_error models, 8-12h

**Status:** ADDRESSED
**Where:** Sprint 21 Priority 3. Prep Task 4 created `PATH_SYNTAX_ERROR_CATALOG.md` with 9 subcategories covering all 45 models (now 48 per baseline retest). Top 3 subcategories account for 71% of failures. Estimated effort 15-22h exceeds budget — triage needed during Task 10 scheduling.

---

### TP4: Deferred Sprint 20 issues (13 issues)

**Source:** Retrospective lines 327-343
**Scope:** 13 deferred issues spanning AD, stationarity, domain handling, macro expansion

**Status:** ADDRESSED
**Where:** Sprint 21 Priority 4. Prep Task 5 created `DEFERRED_ISSUES_TRIAGE.md` classifying all 13: 3 already resolved, 2 fully overlap with Priority 1, 4 recommended for Sprint 21, 4 deferred to Sprint 22+. Total recommended Sprint 21 effort: 9-13h.

---

### TP5: Full pipeline match rate improvement (16 → 20+)

**Source:** Retrospective lines 345-349
**Scope:** Investigate initialization, scaling, domain handling, solver settings for 17 non-matching models

**Status:** ADDRESSED
**Where:** Sprint 21 Priority 5. Prep Task 6 created `SOLVE_MATCH_GAP_ANALYSIS.md` analyzing all 17 models. Primary cause is KKT formulation correctness (not initialization as assumed). Only 2 near-matches (port, chakra). Projected improvement: 16 → 18-22 matches. `KNOWN_UNKNOWNS.md` Category 5 unknowns all verified (all WRONG — findings corrected assumptions).

---

## 4. Gap Analysis

### Gaps Found: None

All 15 action items (5 process recommendations + 5 improvement lessons + 5 technical priorities) from the Sprint 20 retrospective are addressed in Sprint 21 planning:

- **Process recommendations (5/5):** All addressed through baseline practices (PR1, PR2, PR3) or Sprint 21 execution prompts (PR4, PR5). Task 10 must encode PR2, PR3, PR4, PR5 into day-by-day execution prompts.
- **Improvement lessons (5/5):** All addressed — each maps to a process recommendation (WCI1→PR3, WCI2→PR1, WCI3→PR2, WCI5→PR4) or to a specific prep task deliverable (WCI4→Task 3 catalog).
- **Technical priorities (5/5):** All addressed as Sprint 21 Priorities 1-5 with corresponding prep task catalogs, design documents, and known unknowns.

### Action Items for Task 10 (Sprint 21 Detailed Schedule)

These items must be encoded into Sprint 21 day-by-day execution prompts:

1. **PR2:** Include "record PR number in SPRINT_LOG.md" in every day's post-merge checklist
2. **PR3:** Use full pipeline parse stage (`parse_model_file()` + `validate_model_structure()`, not `parse_file()` alone) at all checkpoint gates
3. **PR4:** Include "run newly-parsing models through full pipeline" after parse-improvement days
4. **PR5:** Include error category breakdown (not just totals) at checkpoint gates
5. **Budget awareness:** path_syntax_error estimated effort (15-22h) exceeds Sprint 21 Priority 3 budget (8-12h) — Task 10 must prioritize top subcategories within budget

---

## 5. Summary

| Category | Items | Addressed | Gaps |
|----------|-------|-----------|------|
| Process Recommendations | 5 | 5 | 0 |
| Improvement Lessons | 5 | 5 | 0 |
| Technical Priorities | 5 | 5 | 0 |
| **Total** | **15** | **15** | **0** |

All Sprint 20 retrospective action items are fully addressed in Sprint 21 planning. The five process recommendations are either already embedded in Sprint 21 prep deliverables (PR1 in baseline metrics, PR5 in error catalogs) or flagged for Task 10 to encode in execution prompts (PR2, PR3, PR4). All five technical priorities have corresponding Sprint 21 workstreams with prep task catalogs providing data-driven prioritization.

---

**Document Created:** 2026-02-24
