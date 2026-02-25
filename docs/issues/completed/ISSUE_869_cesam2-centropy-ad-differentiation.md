# Cesam2: `centropy()` AD Differentiation Not Implemented

**GitHub Issue:** [#869](https://github.com/jeffreyhorn/nlp2mcp/issues/869)
**Status:** FIXED
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Fixed:** 2026-02-25
**Affected Models:** cesam2

---

## Problem Summary

The cesam2 model parses successfully but translation fails with `diff_unsupported_func`
because the AD module has no derivative rule for the `centropy()` function.

---

## Fix Applied

Added `_diff_centropy()` to `src/ad/derivative_rules.py` and registered it in the
`_diff_call()` dispatch table.

**Derivative formulas** (simplified, delta ≈ 0):
- `d/dx centropy(x, y) = ln(x/y) + 1`
- `d/dy centropy(x, y) = -x/y`

Both arguments may depend on the differentiation variable, so the implementation applies
the chain rule to both and sums the contributions (same pattern as `_diff_betareg`).

**Tests added:** 9 unit tests in `tests/unit/ad/test_centropy.py` covering:
- Derivative w.r.t. first arg, second arg, unrelated variable
- Both args depending on wrt variable (centropy(x,x) → derivative = 0)
- Numerical verification at specific values
- Wrong arity error handling
- Chain rule with composed first argument

**Result:** cesam2 translates successfully.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Added `_diff_centropy()` + dispatch table entry |
| `tests/unit/ad/test_centropy.py` | 9 unit tests for centropy differentiation |

---

## Related Issues

- **Issue #858** (completed): Previous cesam2 blocker (alias domain resolution)
- **Issue #817** (completed): Earlier cesam2 blocker (conditional assignment in loop)
- **Issue #859** (completed): Similar fix for `betareg()` AD differentiation (procmean)
