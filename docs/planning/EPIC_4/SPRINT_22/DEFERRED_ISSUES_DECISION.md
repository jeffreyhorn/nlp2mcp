# Sprint 22 Deferred Issues Decision

**Date:** 2026-03-06
**Sprint:** 22 (Prep Task 6)
**Prerequisites:** Tasks 2 (PATH_SYNTAX_ERROR_STATUS), 3 (PATH_SOLVE_TERMINATED_STATUS), 4 (MODEL_INFEASIBLE_TRIAGE)

---

## Executive Summary

Three of the four deferred Sprint 21 issues (#765, #827, #830) are **recommended to DEFER to Sprint 23**; #764 (mexss) is **recommended to be included in Sprint 22** as part of the model_infeasible Category A workstream, since Task 4 re-estimated its effort at 3-4h (down from the original 8-12h) and it directly addresses a Sprint 22 target.

The deferred issues have leverage ratios of 0.1-0.3 models/hour — an order of magnitude below Sprint 22's primary workstreams (Subcategory A: 2.5-3.75 models/h, Subcategory C: 2.0-3.33 models/h). Including all 4 deferred issues (22-30h) would consume the entire Sprint 22 budget (~24-30h) with minimal model count improvement.

---

## Leverage Comparison

### Sprint 22 Primary Workstreams (for reference)

| Workstream | Models Fixed | Effort | Leverage (models/h) |
|-----------|-------------|--------|---------------------|
| Subcategory A (missing data) | 15 | 4-6h | **2.5-3.75** |
| Subcategory C (uncontrolled sets) | 10 | 3-5h | **2.0-3.33** |
| Subcategory G (set index reuse) | 4 | 1-2h | **2.0-4.0** |
| Category A KKT bugs (model_infeasible) | 4 | 8-12h | **0.33-0.50** |
| Category C MCP pairing (path_solve_terminated) | 8 | 4-5h | **1.6-2.0** |

### Deferred Issues

| Issue | Model | Effort | Models Fixed | Leverage (models/h) | vs Best Sprint 22 |
|-------|-------|--------|-------------|---------------------|-------------------|
| #764 | mexss | 3-4h* | 1 | **0.25-0.33** | 10× lower |
| #765 | orani | N/A | 0 | **0** | N/A (unfixable) |
| #827 | gtm | 6-8h | 1 | **0.13-0.17** | 18× lower |
| #830 | gastrans | 8-10h | 1 | **0.10-0.13** | 25× lower |

*#764 effort re-estimated by Task 4 as 3-4h (model_infeasible Category A fix), down from original 8-12h estimate.

---

## Individual Issue Assessments

### Issue #764: mexss — Accounting Variable Stationarity

**Original Estimate:** 8-12h (architectural refactor of `sameas` guard)
**Revised Estimate:** 3-4h (Task 4 scoped as model_infeasible Category A fix)
**Model Status:** model_infeasible (Category A — KKT bug)

**Root Cause:** The `_add_indexed_jacobian_terms()` function in `src/kkt/stationarity.py` (lines 1785-1812) uses an incorrect `sameas` guard when a scalar constraint has multiple nonzero Jacobian entries for different instances of an indexed variable. The guard restricts multiplier terms to only the first entry (`entries[0]`), leaving other instances without proper contributions.

**Overlap with Subcategory C (KU-20):**
- **MINIMAL OVERLAP.** Subcategory C fixes uncontrolled free indices in stationarity expressions (Issue #670 logic, lines 1748-1759 of `stationarity.py`). #764 is about the Issue #767 `sameas` guard logic (lines 1785-1812). These are independent code paths within the same file.
- Fixing Subcategory C would NOT change mexss's behavior because mexss's stationarity equations already handle domain wrapping correctly — the bug is in the guard that restricts which instances receive multiplier terms.
- However, both fixes operate on `src/kkt/stationarity.py`, so a developer working on Subcategory C would already have context on the stationarity builder, potentially reducing ramp-up time for #764.

**Decision:** **INCLUDE in Sprint 22** — as part of model_infeasible Category A workstream (whouse, ibm1, uimp, mexss). Rationale:
1. Task 4 re-estimated effort at 3-4h, making it budget-feasible
2. mexss is one of 4 Category A KKT bug fixes needed to meet the model_infeasible ≤12 target
3. KU-24 confirmed 7-14 path_syntax_error models may shift to model_infeasible — fixing Category A early builds buffer
4. Developer working on Subcategory C will already have stationarity.py context

**Budget Impact:** 3-4h (already accounted for in Category A workstream total of 8-12h)

---

### Issue #765: orani — CGE Model Type Incompatible

**Original Estimate:** Detection only (no fix possible)
**Model Status:** model_infeasible (Category C — model type incompatible)

**Root Cause:** orani is a linearized percentage-change CGE model with exogenously fixed variables. This is structurally incompatible with NLP→MCP conversion: stationarity equations for fixed variables reduce to constants ≠ 0, and non-fixed variable stationarity equations create cascading infeasibility.

**Overlap with Sprint 22:** None. KU-23 CONFIRMED this is fundamentally unfixable.

**Decision:** **WON'T FIX** — model class mismatch. Rationale:
1. Issue #765 investigation was thorough: excluding fixed variables creates count mismatch; even with count fix, cascading infeasibility remains
2. Variables represent percentage changes, not level values — a fundamentally different problem class
3. No other model_infeasible model has comparable characteristics (orani has 54 `_fx_` references, highest in corpus)
4. Correct approach: add model class detection heuristic (>30% fixed variables + all linear equations → warning)

**Sprint 22 Action:** Exclude orani from model_infeasible metrics. Consider adding a detection warning as a low-priority enhancement if time permits.

**Budget Impact:** 0h (no implementation work)

---

### Issue #827: gtm — Domain Violations from Zero-Fill

**Original Estimate:** 6-8h (parser + emitter changes)
**Model Status:** path_syntax_error (reclassified to "new pattern" — $120/$340 unquoted hyphenated labels)

**Root Cause (dual issue):**
1. **Error $170 (domain violations):** Parser's `_handle_table_block()` generates blind Cartesian product entries without domain validation; emitter doesn't filter them
2. **Error $141 (unassigned symbols):** Computed parameters lack topological sort for dependency ordering

**Overlap with Subcategory B (KU-21):**
- **PARTIAL but INDIRECT.** Current Subcategory B contains only cesam and cesam2 (2 models with $170 errors). gtm was reclassified out of Subcategory B in Task 2 — its primary errors are now $120/$340 (unquoted hyphenated labels), not $170.
- Even if Subcategory B's emitter domain filtering fix were applied, gtm would still fail with $120/$340 errors (the hyphenated label issue is independent and upstream).
- The $170 domain violation errors from #827 are a **secondary** issue for gtm — they would only surface after fixing the $120/$340 primary errors.
- An emitter domain filtering fix for Subcategory B (cesam/cesam2) might also prevent gtm's $170 errors, but gtm needs the $120/$340 fix first.

**Decision:** **DEFER to Sprint 23.** Rationale:
1. gtm's primary error ($120/$340 hyphenated labels) is independent of #827's domain violation issue
2. The $170 domain violation is secondary — only surfaces after $120/$340 is fixed
3. The full fix chain (hyphenated labels → domain filtering → topological sort) is 3+ separate issues totaling 3-4h minimum
4. gtm is listed in Task 2's "new patterns" section with a 1h estimate for the $120/$340 fix alone
5. Leverage: 1 model / 6-8h = 0.13-0.17 models/h (vs 2.0+ for Subcategory A/C)

**Budget Impact:** 0h saved by deferring. If the $120/$340 fix is included as a Sprint 22 quick fix (1h from Task 2's new patterns), the domain violation may surface as a follow-on issue.

---

### Issue #830: gastrans — Jacobian Timeout from Dynamic Subsets

**Original Estimate:** 8-10h (dynamic subset preservation + Jacobian sparsity)
**Model Status:** timeout (translate subprocess timeout at 60s)

**Root Cause:** Dynamic subsets (`ap`, `as`, `aij`) have 0 static members in IR because range notation (`a01*a19`) isn't expanded during parsing. The Jacobian computation falls back to iterating over parent sets, creating a combinatorial explosion (24 arcs × 20 nodes × 20 nodes × 7 equations × 7 variables = hundreds of thousands of Jacobian entries).

**Overlap with Sprint 22 (KU-22):**
- **NO OVERLAP.** The Jacobian timeout occurs in `src/ad/index_mapping.py` (dynamic subset fallback logic, lines 163-167) and `src/ad/constraint_jacobian.py`. Sprint 22's primary workstreams (Subcategory C domain conditioning in `src/kkt/stationarity.py`, Category A KKT fixes, Category C MCP pairing) do not touch these code paths.
- Subcategory C fixes stationarity equation generation; #830 is a Jacobian instantiation performance issue. Different layers of the pipeline.
- Translation timeout profiling (Task 5) confirmed gastrans is in the "intractable" tier — architectural changes needed.

**Decision:** **DEFER to Sprint 23.** Rationale:
1. No overlap with any Sprint 22 workstream (KU-22 confirmed independent)
2. 8-10h effort for 1 model = 0.10-0.13 models/h leverage (lowest of all deferred issues)
3. Task 5 profiling confirmed Jacobian-bottlenecked models need architectural changes (sparsity-aware Jacobian or LP fast-path) — not Sprint 22 scope
4. gastrans is one of 11 translation timeout models; a Sprint 23 Jacobian optimization workstream could address multiple timeout models simultaneously

**Budget Impact:** 0h saved by deferring. Potential Sprint 23 synergy with other Jacobian-bottlenecked timeout models.

---

## Decision Summary

| Issue | Model | Decision | Sprint 22 Effort | Rationale |
|-------|-------|----------|------------------|-----------|
| **#764** | mexss | **INCLUDE** | 3-4h | Part of Category A KKT fixes; meets model_infeasible target |
| **#765** | orani | **WON'T FIX** | 0h | Structurally incompatible; detection warning only |
| **#827** | gtm | **DEFER** | 0h | Primary error ($120/$340) is independent; low leverage |
| **#830** | gastrans | **DEFER** | 0h | No overlap; architectural change needed; low leverage |

**Total Sprint 22 budget impact from deferred issues:** 3-4h (only #764, already accounted for in Category A workstream)

---

## Known Unknowns Verification

### KU-20: #764 Overlaps with Subcategory C

**Status:** VERIFIED — MINIMAL OVERLAP
**Finding:** #764 (`sameas` guard in `_add_indexed_jacobian_terms()`, stationarity.py:1785-1812) and Subcategory C (uncontrolled free indices, stationarity.py:1748-1759) are independent code paths within the same file. Fixing Subcategory C does not change mexss's behavior. However, both fixes operate on `stationarity.py`, providing developer context overlap (not code overlap).

### KU-21: #827 Overlaps with Subcategory B

**Status:** VERIFIED — PARTIAL BUT INDIRECT
**Finding:** gtm was reclassified out of Subcategory B in Task 2. Its primary errors are now $120/$340 (unquoted hyphenated labels), not the $170 domain violations from #827. Current Subcategory B (cesam/cesam2) shares the $170 error code but has different root causes (newly-translating models vs parser zero-fill). An emitter domain filtering fix for cesam/cesam2 might prevent gtm's secondary $170 errors, but gtm's primary $120/$340 errors must be fixed first.

### KU-22: #830 Is Independent of Sprint 22 Work

**Status:** VERIFIED — CONFIRMED INDEPENDENT
**Finding:** #830's Jacobian timeout occurs in `src/ad/index_mapping.py` (dynamic subset fallback) and `src/ad/constraint_jacobian.py`. No Sprint 22 workstream touches these code paths. Subcategory C fixes operate on stationarity equation generation (`src/kkt/stationarity.py`), a different pipeline layer.

---

## Budget Analysis

### Without Deferred Issues (Sprint 22 primary workstreams only)

| Workstream | Effort | Models Fixed |
|-----------|--------|-------------|
| Subcategory A (missing data) | 4-6h | 15 |
| Subcategory C (uncontrolled sets) | 3-5h | 10 |
| Subcategory B (domain violations) | 1-2h | 2 |
| Subcategory G (set index reuse) | 1-2h | 4 |
| Category A KKT (incl. #764) | 8-12h | 4 |
| Category C MCP pairing | 4-5h | 7-8 |
| **Total** | **21-32h** | **42-44** |

### If All Deferred Issues Were Included

| Additional Work | Effort | Models Fixed |
|----------------|--------|-------------|
| #764 (already included above) | 0h | 0 |
| #827 (gtm full fix) | 6-8h | 1 |
| #830 (gastrans) | 8-10h | 1 |
| **Additional Total** | **14-18h** | **2** |

Including #827 and #830 would push the budget to 35-50h (exceeding the 24-30h Sprint 22 budget) for only 2 additional models. This would require cutting primary workstreams that have 10-20× higher leverage.

---

## Appendix: Source Documents

- `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md`
- `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md`
- `docs/issues/ISSUE_827_gtm-domain-violation-zero-fill.md`
- `docs/issues/ISSUE_830_gastrans-jacobian-dynamic-subset-timeout.md`
- `docs/planning/EPIC_4/SPRINT_21/DEFERRED_ISSUES_TRIAGE.md`
- `docs/planning/EPIC_4/SPRINT_22/PATH_SYNTAX_ERROR_STATUS.md` (Task 2)
- `docs/planning/EPIC_4/SPRINT_22/PATH_SOLVE_TERMINATED_STATUS.md` (Task 3)
- `docs/planning/EPIC_4/SPRINT_22/MODEL_INFEASIBLE_TRIAGE.md` (Task 4)
- `docs/planning/EPIC_4/SPRINT_22/TRANSLATION_TIMEOUT_PROFILE.md` (Task 5)
