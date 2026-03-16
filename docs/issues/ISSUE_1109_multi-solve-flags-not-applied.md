# Multi-Solve Database Flags Not Applied to Models

**GitHub Issue:** [#1109](https://github.com/jeffreyhorn/nlp2mcp/issues/1109)
**Status:** OPEN
**Affected Models:** senstran, apl1p, apl1pca, aircraft, ps10_s_mn, ps5_s_mn
**Error category:** `pipeline_classification`

## Description

Issue #1080 established the `multi_solve` classification infrastructure (schema field, comparison skip logic in `test_solve.py`, `COMPARE_MULTI_SOLVE_SKIP` taxonomy constant) but the `multi_solve: true` flag was never actually set on any models in `data/gamslib/gamslib_status.json`. Zero models in the database have `multi_solve=true`.

This means multi-solve models are incorrectly counted as mismatches in the pipeline, inflating the mismatch count and deflating the match rate.

## Affected Models

| Model | Solve Count | Expected Classification |
|-------|------------|------------------------|
| senstran | 4 solves | `compare_multi_solve_skip` |
| apl1p | 2 solves | `compare_multi_solve_skip` |
| apl1pca | 2 solves | `compare_multi_solve_skip` |
| aircraft | 2 solves | `compare_multi_solve_skip` |
| ps10_s_mn | 2000 solves (loop) | `compare_multi_solve_skip` |
| ps5_s_mn | 2000 solves (loop) | `compare_multi_solve_skip` |

## Root Cause

The #1080 fix added the comparison-skip logic in `scripts/gamslib/test_solve.py` (line 809):

```python
if model.get("multi_solve"):
    result["comparison_result"] = COMPARE_MULTI_SOLVE_SKIP
```

But the database entries for these models were never updated with `"multi_solve": true`. The code that sets this flag was either not run or its results were not persisted.

## Reproduction

```bash
python -c "
import json
db = json.load(open('data/gamslib/gamslib_status.json'))
ms_count = sum(1 for v in db.values() if v.get('multi_solve'))
print(f'Models with multi_solve=true: {ms_count}')
"
# Output: 0
```

## Recommended Fix

Set `multi_solve: true` in `data/gamslib/gamslib_status.json` for all 6 models listed above, then re-run the pipeline comparison stage.

```python
import json
db_path = "data/gamslib/gamslib_status.json"
db = json.load(open(db_path))
for model in ["senstran", "apl1p", "apl1pca", "aircraft", "ps10_s_mn", "ps5_s_mn"]:
    if model in db:
        db[model]["multi_solve"] = True
json.dump(db, open(db_path, "w"), indent=2)
```

## Related Issues

- #1080: Multi-solve classification infrastructure (RESOLVED — code exists but flags not set)
- #963, #964: ps-family multi-solve mismatches
- #958-964: ps family objective mismatches

## Estimated Effort

15 minutes — database update + pipeline retest.
