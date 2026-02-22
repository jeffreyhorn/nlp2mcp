# Gastrans MCP: Translation Fails — `signpower` Function Not Supported in AD

**GitHub Issue:** [#825](https://github.com/jeffreyhorn/nlp2mcp/issues/825)
**Status:** RESOLVED
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

## Resolution

### Changes Made

1. **`src/ad/derivative_rules.py`**: Added `_diff_signpower()` function implementing:
   - `d/dx signpower(x, n) = n * abs(x)^(n-1) * dx/dx` (chain rule)
   - Requires `--smooth-abs` flag (since derivative uses `abs()`)
   - Only supports constant exponents (variable exponents raise `ValueError`)
   - Added `elif func == "signpower"` dispatch in `_diff_call()`
   - Updated supported functions list in error message

2. **`src/ad/evaluator.py`**: Added `signpower` evaluation handler:
   - `signpower(x, n) = copysign(|x|^n, x)` using `math.copysign`

3. **`tests/unit/ad/test_transcendental.py`**: Added 11 unit tests:
   - `TestSignpowerDifferentiation` (6 tests): constant exponent, smooth-abs requirement,
     constant exponent requirement, wrong arity, chain rule, other variable
   - `TestSignpowerEvaluation` (5 tests): positive base, negative base, zero base,
     fractional exponent, variable input

### Remaining Blocker

The signpower AD issue is fully resolved. However, gastrans still cannot complete the full
pipeline due to a **separate pre-existing issue**: the Jacobian computation times out because
the dynamic subset `aij(a,i,i)` has 0 static members, causing fallback to parent sets
`a` (24) x `i` (20) x `i` (20) = 9,600 tuple combinations per equation/variable pair.
This is a Jacobian infrastructure issue, not a signpower problem.

---

## Files Modified

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Added `_diff_signpower()` + dispatch + error message update |
| `src/ad/evaluator.py` | Added `signpower` evaluation handler |
| `tests/unit/ad/test_transcendental.py` | Added 11 unit tests (6 differentiation, 5 evaluation) |
