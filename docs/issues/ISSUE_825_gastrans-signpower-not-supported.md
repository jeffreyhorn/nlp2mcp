# Gastrans MCP: Translation Fails — `signpower` Function Not Supported in AD

**GitHub Issue:** [#825](https://github.com/jeffreyhorn/nlp2mcp/issues/825)
**Status:** OPEN
**Severity:** Medium — Model cannot be translated to MCP (pipeline fails at differentiation)
**Date:** 2026-02-22
**Affected Models:** gastrans

---

## Problem Summary

The gastrans model (`data/gamslib/raw/gastrans.gms`) fails during NLP→MCP translation because
the `signpower` function is not supported by the automatic differentiation (AD) module:

```
Error: Invalid model - Differentiation not yet implemented for function 'signpower'.
Supported functions: power, exp, log, log10, log2, sqrt, sin, cos, tan, abs, sqr,
errorf, smin, smax, sameas, card, ord.
Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

Previously this model failed with `codegen_numerical_error` due to `-Inf` parameter values
in the `Ndata` table. The Inf handling fix (Sprint 20 Day 10) resolved that blocker, revealing
this deeper issue.

---

## Original Model Structure

The gastrans model uses `signpower` in the Weymouth pipe flow equation:

```gams
weymouthp(aij(ap,i,j)).. signpower(f(aij),2) =e= c2(aij)*(pi(i) - pi(j));
```

`signpower(x, n)` is defined as `sign(x) * |x|^n` — it preserves the sign of `x` while
raising the absolute value to the power `n`. This is used for gas flow equations where flow
direction matters.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/gastrans.gms -o /tmp/gastrans_mcp.gms
# Error: Invalid model - Differentiation not yet implemented for function 'signpower'.
```

---

## Root Cause

The AD module (`src/ad/`) does not have differentiation rules for `signpower(x, n)`.

The derivative of `signpower(x, n)` w.r.t. `x` is:
- `d/dx signpower(x, n) = n * |x|^(n-1)` (for `n > 1`)

This can be implemented using existing AD primitives (`abs`, `power`).

---

## Suggested Fix

Add `signpower` to the supported function list in the AD module:

1. **`src/ad/differentiate.py`** (or similar): Add differentiation rule for `signpower(x, n)`:
   - `d/dx signpower(x, n) = n * abs(x)^(n-1)` (requires `n > 1` for differentiability at 0)
   - May need the `--smooth-abs` flag since `abs()` is non-differentiable at `x=0`

2. **`src/ad/simplify.py`**: Ensure `signpower` expressions simplify correctly

3. **Unit tests**: Add tests for `signpower` differentiation

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ad/differentiate.py` | Where function differentiation rules are defined |
| `src/ad/supported_functions.py` | List of supported functions for AD |
| `data/gamslib/raw/gastrans.gms` | Original model with `signpower` usage |
