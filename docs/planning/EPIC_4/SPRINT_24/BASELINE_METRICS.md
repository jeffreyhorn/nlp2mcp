# Sprint 24 Baseline Metrics

**Date:** 2026-04-04
**Pipeline:** `scripts/gamslib/run_full_test.py --quiet`
**Duration:** 4641s (~77 min)
**Models:** 147/147

---

## Pipeline Results

| Stage | Count | Rate | Notes |
|---|---|---|---|
| Parse | 147/147 | 100.0% | No failures |
| Translate | 140/147 | 95.2% | 6 timeout, 1 internal_error |
| Solve | 86/140 | 61.4% | Of translated models |
| Match | 49/147 | 33.3% | Of all models |

## Error Categories

| Category | Count | Models |
|---|---|---|
| path_syntax_error | 23 | (see TRIAGE_PATH_SYNTAX_ERROR.md) |
| path_solve_terminated | 12 | |
| model_infeasible | 11 | (see TRIAGE_MODEL_INFEASIBLE.md — note: pipeline counts 11, triage doc counts 14 due to different classification) |
| path_solve_license | 8 | |
| translate timeout | 6 | (see INVESTIGATION_TRANSLATE_TIMEOUTS.md) |
| translate internal_error | 1 | mine |

## Comparison to Sprint 23 Final (Day 13)

| Metric | Sprint 23 Final | Sprint 24 Baseline | Delta |
|---|---|---|---|
| Parse | 147/147 (100.0%) | 147/147 (100.0%) | 0 |
| Translate | 140/147 (95.2%) | 140/147 (95.2%) | 0 |
| Solve | 86/140 (61.4%) | 86/140 (61.4%) | 0 |
| Match | 49/147 (33.3%) | 49/147 (33.3%) | 0 |
| path_syntax_error | 23 | 23 | 0 |
| path_solve_terminated | 12 | 12 | 0 |
| model_infeasible | 11 | 11 | 0 |
| path_solve_license | 8 | 8 | 0 |

**No changes from Sprint 23 final.** Baseline is identical — no code changes between Sprint 23 close and Sprint 24 prep.

## Sprint 24 Targets (from PROJECT_PLAN.md)

| Metric | Baseline | Target | Gap |
|---|---|---|---|
| Parse | 147/147 (100%) | ≥ 147/147 (100%) | 0 (maintain) |
| Translate | 140/147 (95.2%) | ≥ 143/147 (97%) | +3 needed |
| Solve | 86 | ≥ 95 | +9 needed |
| Match | 49 | ≥ 55 | +6 needed |
| path_syntax_error | 23 | ≤ 15 | -8 needed |
| path_solve_terminated | 12 | ≤ 10 | -2 needed |
| model_infeasible | 11 | ≤ 8 | -3 needed |
| Tests | 4,364 | ≥ 4,400 | +36 needed |

## Error Influx Rate Analysis (KU-25)

Sprint 23 actual influx:
- **Translate recovery:** +12 models (128 → 140)
- **New solve errors from recovered models:** +7 (path_syntax_error +5, path_solve_terminated +2)
- **Actual influx rate:** 7/12 = 58.3%

Sprint 23 process recommendation PR10 estimated ~40%. **Actual was 58% — PR10 underestimates influx.** Sprint 24 should budget for ~50-60% of newly-translating models entering solve error categories.
