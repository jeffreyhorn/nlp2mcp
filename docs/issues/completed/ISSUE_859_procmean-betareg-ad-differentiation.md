# Procmean: `betareg()` Automatic Differentiation Not Implemented

**GitHub Issue:** [#859](https://github.com/jeffreyhorn/nlp2mcp/issues/859)
**Status:** FIXED
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Affected Models:** procmean

---

## Problem Summary

The procmean model parses successfully but fails during translation with
`diff_unsupported_func` because the AD module had no derivative rule for `betareg()`.

---

## Root Cause

The AD dispatch table in `src/ad/derivative_rules.py` did not include `betareg`.

---

## Fix Applied

Added `_diff_betareg()` to `src/ad/derivative_rules.py` implementing the derivative
of the regularized incomplete Beta function:

```
d/dx betareg(x, a, b) = x^(a-1) * (1-x)^(b-1) / Beta(a, b)
```

where `Beta(a, b) = gamma(a) * gamma(b) / gamma(a+b)`.

Shape parameters `a` and `b` are treated as constant w.r.t. decision variables.
Chain rule is applied for the first argument.

**Result:** procmean now translates AND solves successfully.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Added `_diff_betareg()` and registered in dispatch table |
