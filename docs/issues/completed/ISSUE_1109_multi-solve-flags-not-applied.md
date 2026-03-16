# Multi-Solve Database Flags Not Applied to Models

**GitHub Issue:** [#1109](https://github.com/jeffreyhorn/nlp2mcp/issues/1109)
**Status:** RESOLVED
**Resolved:** 2026-03-16
**Affected Models:** senstran, apl1p, apl1pca, aircraft, ps10_s_mn, ps5_s_mn
**Error category:** `pipeline_classification`

## Description

Issue #1080 established the `multi_solve` classification infrastructure (schema field, comparison skip logic in `test_solve.py`, `COMPARE_MULTI_SOLVE_SKIP` taxonomy constant) but the `multi_solve: true` flag was never actually set on any models in `data/gamslib/gamslib_status.json`. Zero models in the database had `multi_solve=true`.

This caused multi-solve models to be incorrectly counted as mismatches in the pipeline, inflating the mismatch count and deflating the match rate.

## Affected Models

| Model | Solve Count | Expected Classification |
|-------|------------|------------------------|
| senstran | 4 solves | `compare_multi_solve_skip` |
| apl1p | 2 solves | `compare_multi_solve_skip` |
| apl1pca | 2 solves | `compare_multi_solve_skip` |
| aircraft | 2 solves | `compare_multi_solve_skip` |
| ps10_s_mn | 2000 solves (loop) | `compare_multi_solve_skip` |
| ps5_s_mn | 2000 solves (loop) | `compare_multi_solve_skip` |

## Resolution

Set `multi_solve: true` in `data/gamslib/gamslib_status.json` for all 6 models. Verified with pipeline retest that comparison now returns `compare_multi_solve_skip` for these models (confirmed with senstran).

**File changed:** `data/gamslib/gamslib_status.json` — added `"multi_solve": true` to 6 model entries at indices: aircraft(2), apl1p(10), apl1pca(11), ps10_s_mn(142), ps5_s_mn(153), senstran(180).

## Verification

```bash
# Before fix:
python -c "..."  # 0 models with multi_solve=true

# After fix:
python scripts/gamslib/run_full_test.py --model senstran --verbose 2>&1 | grep COMPARE
# [COMPARE] SKIPPED: Multi-solve model: NLP reference captures a different solve iteration...
```

## Related Issues

- #1080: Multi-solve classification infrastructure (RESOLVED — code existed but flags not set)
- #1107 (ps10_s_mn), #1108 (ps5_s_mn): Individual model mismatches resolved by this fix
- #963, #964: ps-family multi-solve mismatches
