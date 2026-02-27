# mlbeta: loggamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#936](https://github.com/jeffreyhorn/nlp2mcp/issues/936)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (missing function derivative)
**Date:** 2026-02-26
**Affected Models:** mlbeta
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `mlbeta.gms` model (GAMSlib SEQ=221, "Fitting of beta distribution through maximum likelihood") parses successfully but fails during KKT translation because the model uses `loggamma()` in its equations. Differentiation of `loggamma()` requires the digamma (psi) function, which is not available as a built-in GAMS function.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 221 |
| Solve Type | NLP |
| Convexity | likely_convex |
| Reference Objective | 25.3176 |
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
python -m src.cli data/gamslib/raw/mlbeta.gms -o /tmp/mlbeta_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model mlbeta --only-translate --verbose
```

---

## Root Cause

Same as mingamma. The derivative of `loggamma(x)` is the digamma function `psi(x)`, which GAMS does not have as a built-in function. The symbolic differentiation engine raises a `ValueError` at `src/ad/derivative_rules.py:589-600`.

The beta distribution log-likelihood function uses `loggamma()` extensively:
```
log L(a,b) = n*loggamma(a+b) - n*loggamma(a) - n*loggamma(b) + (a-1)*sum(log(x)) + (b-1)*sum(log(1-x))
```

---

## Possible Fixes

Same as mingamma — implement digamma approximation, use external functions, or mark as unsupported.

---

## Related Issues

- mingamma: Same `loggamma` differentiation blocker
- mlgamma: Same `loggamma` differentiation blocker
- robustlp: `gamma()` differentiation blocker (same underlying digamma issue)
