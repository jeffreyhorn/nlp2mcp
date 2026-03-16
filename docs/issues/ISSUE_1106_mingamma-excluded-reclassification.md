# mingamma: Pipeline Excluded — Reclassification Needed After Digamma Fix

**GitHub Issue:** [#1106](https://github.com/jeffreyhorn/nlp2mcp/issues/1106)
**Status:** OPEN
**Model:** mingamma (GAMSlib SEQ=159)
**Error category:** `pipeline_excluded`
**MCP solve status:** MODEL STATUS 1 (Optimal), obj=-0.121

## Description

The mingamma model is excluded from the pipeline candidate database with `convexity.status = "excluded"`. The original exclusion reason was: "Gamma function is not convex on x>0. Additionally, GAMS lacks the digamma/psi function needed for derivatives."

The digamma fix (commit `69ea31d3`, Issue #935-938) implemented a smooth digamma approximation macro, resolving the derivative limitation. The model now translates and solves to optimality (MODEL STATUS 1, obj=-0.121), matching the NLP reference.

## Root Cause

The database entry in `data/gamslib/gamslib_status.json` still has:
- `convexity.status = "excluded"`
- `nlp2mcp_translate.status = "failure"` (stale from 2026-02-22)

The pipeline's `run_full_test.py` only processes models with `convexity.status` equal to `"verified_convex"` or `"likely_convex"`, so mingamma is never tested.

## Reproduction

```bash
# Translates successfully:
python -m src.cli data/gamslib/raw/mingamma.gms -o /tmp/mingamma_mcp.gms
# MCP includes digamma__ macro

# Solves to optimality:
gams /tmp/mingamma_mcp.gms lo=2
# MODEL STATUS 1, SOLVER STATUS 1, obj=-0.121

# But pipeline skips it:
.venv/bin/python scripts/gamslib/run_full_test.py --model mingamma --verbose
# "Model not found or not a candidate"
```

## Recommended Fix

Update `data/gamslib/gamslib_status.json`:
1. Change `convexity.status` from `"excluded"` to `"likely_convex"`
2. Re-run pipeline to update `nlp2mcp_translate` and `mcp_solve` entries

## Related Issues

- #935 (mingamma): loggamma/digamma derivative — RESOLVED
- #936-938: mlbeta, mlgamma, robustlp gamma family — RESOLVED

## Estimated Effort

15 minutes — database field update + pipeline retest.
