# Multi-Solve Models Produce Incomparable NLP Reference Objectives

**GitHub Issue:** [#1080](https://github.com/jeffreyhorn/nlp2mcp/issues/1080)
**Status:** RESOLVED
**Severity:** Medium — Caused false "mismatch" classification for 4 models
**Date:** 2026-03-14
**Resolved:** 2026-03-16 (Sprint 22 Day 12)
**Affected Models:** senstran, apl1p, apl1pca, aircraft (sparta is also multi-solve but has
an additional KKT infeasibility bug tracked separately in #1081)

---

## Problem Summary

4 Category A (verified_convex mismatch) models have mismatches caused by the pipeline
comparing the MCP objective against an NLP reference from a different solve iteration or
solver mode. These are not KKT formulation bugs — the MCP formulation is correct for the
deterministic/first-solve case, but the NLP reference captures a different problem.

---

## Resolution

Added `multi_solve` classification to the pipeline:

1. **New comparison category**: `COMPARE_MULTI_SOLVE_SKIP` in `scripts/gamslib/error_taxonomy.py`
2. **Model flag**: `multi_solve: true` added to 4 models in `data/gamslib/gamslib_status.json`
3. **Early-exit in comparison**: `compare_solutions()` in `scripts/gamslib/test_solve.py` checks for `model.get("multi_solve")` and returns `comparison_status: "skipped"` with `comparison_result: "compare_multi_solve_skip"`
4. **Schema update**: `multi_solve` boolean property added to model_entry in `data/gamslib/schema.json`; `compare_multi_solve_skip` added to `comparison_result_category` enum
5. **Test updates**: Category count tests updated in `tests/gamslib/test_error_taxonomy.py` (17→18 solve categories, 49→50 total)

Multi-solve models are now counted in `compare_skipped` instead of `compare_mismatch`, correctly excluding them from the match rate denominator.

### Files Changed

| File | Change |
|------|--------|
| `scripts/gamslib/error_taxonomy.py` | Added `COMPARE_MULTI_SOLVE_SKIP` constant |
| `scripts/gamslib/test_solve.py` | Added early-exit check in `compare_solutions()` |
| `data/gamslib/gamslib_status.json` | Added `multi_solve: true` to 4 models |
| `data/gamslib/schema.json` | Added `multi_solve` property and enum value |
| `tests/gamslib/test_error_taxonomy.py` | Updated category count assertions |
