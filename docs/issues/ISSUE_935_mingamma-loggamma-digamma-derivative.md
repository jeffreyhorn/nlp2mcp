# mingamma: loggamma Differentiation Requires Digamma/Psi Function

**GitHub Issue:** [#935](https://github.com/jeffreyhorn/nlp2mcp/issues/935)
**Status:** OPEN
**Severity:** Medium — Model parses but cannot be translated (missing function derivative)
**Date:** 2026-02-26
**Affected Models:** mingamma
**Sprint:** 21 (Day 11 triage)

---

## Problem Summary

The `mingamma.gms` model (GAMSlib SEQ=217, "Minimal y of GAMMA(x)") parses successfully but fails during KKT translation because the model uses `loggamma()` in its equations, and differentiation of `loggamma()` requires the digamma (psi) function, which is not available as a built-in GAMS function.

---

## Model Details

| Property | Value |
|----------|-------|
| GAMSlib SEQ | 217 |
| Solve Type | NLP |
| Convexity | excluded |
| Reference Objective | -0.1215 |
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
python -m src.cli data/gamslib/raw/mingamma.gms -o /tmp/mingamma_mcp.gms
# Or:
python scripts/gamslib/run_full_test.py --model mingamma --only-translate --verbose
```

---

## Root Cause

The derivative of `loggamma(x)` is the digamma function `psi(x)`, also known as the polygamma function of order 0. GAMS does not have a built-in `digamma()` or `psi()` function, so the symbolic differentiation engine (`src/ad/derivative_rules.py:589-600`) raises a `ValueError` when encountering `loggamma()`.

The mathematical relationship:
- `d/dx[loggamma(x)] = psi(x)` (digamma function)
- `d/dx[gamma(x)] = gamma(x) * psi(x)`

### Code Location

`src/ad/derivative_rules.py` lines 589-600:
```python
elif func in ("gamma", "loggamma"):
    # Gamma derivatives require the digamma/psi function, which GAMS doesn't have.
    # d/dx[gamma(x)] = gamma(x) * psi(x)
    # d/dx[loggamma(x)] = psi(x)
    raise ValueError(
        f"Differentiation of '{func}' requires the digamma/psi function, "
        "which is not available in GAMS. ..."
    )
```

---

## Possible Fixes

| Approach | Impact | Effort |
|----------|--------|--------|
| Implement digamma via series expansion or rational approximation | High — would unblock all 4 gamma/loggamma models | Medium-High |
| Use GAMS external functions to provide digamma | Medium — requires GAMS external library setup | Medium |
| Mark these models as unsupported (fundamental GAMS limitation) | N/A — document limitation | Trivial |

**Note:** A series expansion for digamma is mathematically well-known (Stirling's approximation, recurrence relation), but implementing it as a GAMS expression may produce very long equations. An alternative is to use GAMS's `execSeed` or external function interface.

---

## Related Issues

- mlbeta: Same `loggamma` differentiation blocker
- mlgamma: Same `loggamma` differentiation blocker
- robustlp: `gamma()` differentiation blocker (same underlying digamma issue)
