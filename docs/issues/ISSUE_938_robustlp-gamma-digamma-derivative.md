# robustlp: gamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#938](https://github.com/jeffreyhorn/nlp2mcp/issues/938)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (missing function derivative)
**Date:** 2026-02-26
**Affected Models:** robustlp
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `robustlp.gms` model (GAMSlib SEQ=318, "Robust linear programming as an SOCP") parses successfully but fails during KKT translation because the model uses the `gamma()` function in its equations. Differentiation of `gamma()` requires the digamma (psi) function, which is not available as a built-in GAMS function.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 318 |
| Solve Type | LP |
| Convexity | verified_convex |
| Reference Objective | -2.3296 |
| Parse Status | success |
| Translate Status | failure — `internal_error` |

---

## Error Message

```
Error: Invalid model - Differentiation of 'gamma' requires the digamma/psi function,
which is not available in GAMS. Models using gamma() in the objective or constraints
cannot be converted to MCP.
```

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/robustlp.gms -o /tmp/robustlp_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model robustlp --only-translate --verbose
```

---

## Root Cause

The derivative of `gamma(x)` is `gamma(x) * psi(x)`, where `psi(x)` is the digamma function. GAMS does not have a built-in `digamma()` or `psi()` function, so the symbolic differentiation engine raises a `ValueError`.

Code location: `src/ad/derivative_rules.py:589-600`:
```python
elif func in ("gamma", "loggamma"):
    raise ValueError(
        f"Differentiation of '{func}' requires the digamma/psi function, ..."
    )
```

Note: Despite being classified as an LP model, robustlp uses `gamma()` in parameter initialization expressions that appear in the model equations, triggering the derivative computation.

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Implement digamma via series expansion or rational approximation | High — unblocks all 4 gamma/loggamma models | Medium-High |
| Check if gamma() appears only in parameters (not in variable expressions) — if so, evaluate numerically before differentiation | High for this specific model | Medium |
| Mark as unsupported (fundamental GAMS limitation) | N/A | Trivial |

---

## Related Issues

- mingamma, mlbeta, mlgamma: Same family — `loggamma` differentiation blocker
