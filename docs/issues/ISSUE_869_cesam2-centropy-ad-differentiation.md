# Cesam2: `centropy()` AD Differentiation Not Implemented

**GitHub Issue:** [#869](https://github.com/jeffreyhorn/nlp2mcp/issues/869)
**Status:** OPEN
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model parses successfully and alias domain resolution now works (Issue #858),
but translation fails with `diff_unsupported_func` because the AD module has no derivative
rule for the `centropy()` function.

---

## Error Details

```
Category: diff_unsupported_func
Message: Differentiation not yet implemented for function 'centropy'.
```

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from pathlib import Path
from scripts.gamslib.batch_translate import translate_single_model
result = translate_single_model(
    Path('data/gamslib/raw/cesam2.gms'),
    Path('/Users/jeff/experiments/nlp2mcp/data/gamslib/mcp/cesam2_mcp.gms')
)
print(result['status'], result.get('error', {}).get('category', ''))
"
```

---

## Root Cause

The model uses `CENTROPY()` in its objective equation (lines 431-434):

```gams
ENTROPY.. DENTROPY =e= sum[(ii,jj,jwt3)$nonzero(ii,jj), CENTROPY(W3(ii,jj,jwt3),wbar3(ii,jj,jwt3))]
                    +  sum[(ii,jwt1),    CENTROPY(W1(ii,jwt1),wbar1(ii,jwt1))]
                    +  sum[(macro,jwt2), CENTROPY(W2(macro,jwt2),wbar2(macro,jwt2))];
```

`centropy(x, y)` is the GAMS cross-entropy function, defined as:

```
centropy(x, y) = x * ln((x + delta) / (y + delta))
```

where `delta` is a small regularization constant (default ~1e-20) to avoid `ln(0)`.

The AD dispatch table in `src/ad/derivative_rules.py` does not include `centropy`.
The derivative with respect to `x` is:

```
d/dx centropy(x, y) = ln((x + delta) / (y + delta)) + x / (x + delta)
                     = ln(x + delta) - ln(y + delta) + x / (x + delta)
```

And with respect to `y`:

```
d/dy centropy(x, y) = -x / (y + delta)
```

### Complication: GAMS `delta` constant

The regularization constant `delta` in GAMS's `centropy` implementation is internal
and not directly accessible. For practical purposes in MCP reformulation, we can either:

1. Use a hardcoded small constant (e.g., `1e-20`) matching GAMS default
2. Use the simplified form `x * ln(x/y)` and rely on GAMS's own `centropy` in the
   emitted code (i.e., emit `centropy(x, y)` directly in the stationarity equations
   rather than expanding the derivative)
3. Implement the derivative symbolically and emit using `log()` and arithmetic

### Key Code Location

`src/ad/derivative_rules.py`, function dispatch in `_diff_call()` (around line 619):
the `else` branch raises `ValueError` for unsupported functions.

---

## Suggested Fix

Add a `_diff_centropy()` function to `src/ad/derivative_rules.py` following the pattern
of existing derivative rules (e.g., `_diff_exp`, `_diff_betareg`).

Since GAMS uses `delta ≈ 1e-20`, use the simplified derivative:

```python
# d/dx centropy(x, y) ≈ ln(x/y) + 1  (when delta ≈ 0 and x > 0)
# d/dy centropy(x, y) ≈ -x/y          (when delta ≈ 0 and y > 0)
```

Apply chain rule for both arguments since both may contain decision variables.

**Effort estimate:** ~2h

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Add `_diff_centropy()` and register in dispatch table |

---

## Related Issues

- **Issue #858** (completed): Previous cesam2 blocker (alias domain resolution)
- **Issue #817** (completed): Earlier cesam2 blocker (conditional assignment in loop)
- **Issue #859** (completed): Similar fix for `betareg()` AD differentiation (procmean)
