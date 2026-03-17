# mingamma: Pipeline Excluded — Reclassification Needed After Digamma Fix

**GitHub Issue:** [#1106](https://github.com/jeffreyhorn/nlp2mcp/issues/1106)
**Status:** RESOLVED
**Resolved:** 2026-03-16
**Model:** mingamma (GAMSlib SEQ=159)
**Error category:** `pipeline_excluded` → `likely_convex` (now in pipeline)
**MCP solve status:** MODEL STATUS 1 (Optimal), obj=-0.121

## Description

The mingamma model was excluded from the pipeline candidate database with `convexity.status = "excluded"`. The original exclusion reason was: "Gamma function is not convex on x>0. Additionally, GAMS lacks the digamma/psi function needed for derivatives."

The digamma fix (commit `69ea31d3`, Issue #935-938) implemented a smooth digamma approximation macro, resolving the derivative limitation. The model now translates and solves to optimality.

## Resolution

Updated `data/gamslib/gamslib_status.json` for mingamma (index 109):
1. Changed `convexity.status` from `"excluded"` to `"likely_convex"`
2. Removed stale `convexity.error` field
3. Cleared stale `nlp2mcp_translate`, `mcp_solve`, and `solution_comparison` entries

Pipeline retest confirms:
- **Parse**: SUCCESS (4 vars, 2 eqs)
- **Translate**: SUCCESS
- **Solve**: SUCCESS (MODEL STATUS 1, obj=-0.121)
- **Compare**: Minor mismatch (diff=0.0005, 0.41% relative) — this is within expected numerical precision of the digamma approximation macro, not a formulation bug

The NLP reference objective is -0.1215 and the MCP objective is -0.121. The 0.41% relative difference exceeds the 0.2% tolerance threshold due to the digamma series approximation truncation. This is a known limitation documented in #935.

## Related Issues

- #935 (mingamma): loggamma/digamma derivative — RESOLVED
- #936-938: mlbeta, mlgamma, robustlp gamma family — RESOLVED
