# mlgamma: loggamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#937](https://github.com/jeffreyhorn/nlp2mcp/issues/937)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (missing function derivative)
**Date:** 2026-02-26
**Affected Models:** mlgamma
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `mlgamma.gms` model (GAMSlib SEQ=222, "Maximum Likelihood estimation of parameters of the gamma distribution") parses successfully but fails during KKT translation because the model uses `loggamma()` in its equations. Differentiation of `loggamma()` requires the digamma (psi) function, which is not available as a built-in GAMS function.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 222 |
| Solve Type | NLP |
| Convexity | likely_convex |
| Reference Objective | -155.3468 |
| Parse Status | success |
| Translate Status | failure — `internal_error` |

---

## Error Message

```
Error: Invalid model - Differentiation of 'loggamma' requires the digamma/psi function,
which is not available in GAMS. Models using loggamma() in the objective or constraints
cannot be converted to MCP.
```

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/mlgamma.gms -o /tmp/mlgamma_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model mlgamma --only-translate --verbose
```

---

## Root Cause

Same as mingamma and mlbeta. The gamma distribution MLE uses `loggamma()`:
```
log L(a,b) = (a-1)*sum(log(x)) - n*a*log(b) - n*loggamma(a) - sum(x)/b
```

The derivative `d/dx[loggamma(x)] = psi(x)` cannot be expressed in GAMS.

Code location: `src/ad/derivative_rules.py:589-600`.

---

## Possible Fixes

Same as mingamma — implement digamma approximation, use external functions, or mark as unsupported.

---

## Related Issues

- mingamma: Same `loggamma` differentiation blocker
- mlbeta: Same `loggamma` differentiation blocker
- robustlp: `gamma()` differentiation blocker (same underlying digamma issue)
