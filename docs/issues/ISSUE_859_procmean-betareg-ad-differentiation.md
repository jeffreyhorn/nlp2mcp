# Procmean: `betareg()` Automatic Differentiation Not Implemented

**GitHub Issue:** [#859](https://github.com/jeffreyhorn/nlp2mcp/issues/859)
**Status:** OPEN
**Severity:** Medium — Model parses but fails at translate stage
**Date:** 2026-02-24
**Affected Models:** procmean

---

## Problem Summary

The procmean model parses successfully (fixed in Sprint 21 Day 1 by adding `betareg` to
FUNCNAME) but fails during translation with `diff_unsupported_func`. The AD module cannot
differentiate the `betareg()` function because no derivative rule is implemented for it.

---

## Error Details

```
Error: Invalid model - Differentiation not yet implemented for function 'betareg'.
Supported functions: power, signpower, exp, log, log10, log2, sqrt, sin, cos, tan,
abs, sqr, errorf, smin, smax, sameas, card, ord.
Note: abs() requires --smooth-abs flag (non-differentiable at x=0).
```

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
from src.mcp.emitter import emit_mcp
ir = parse_file('data/gamslib/raw/procmean.gms')
mcp_code = emit_mcp(ir)
"
```

---

## Root Cause

The model uses `betareg()` extensively in its objective equation (lines 45-50):

```gams
tcdef.. tc =e= k1*T*betareg(y,alpha,beta)
            -  k1*{(delta + a)*betareg(y,alpha,beta)
                   +(b - a)*betareg(y,alpha + 1,beta)*g3}
            +  k2*{(delta + a)*[1 - betareg(y,alpha,beta)]
                   +(b - a)*[1 - betareg(y,alpha + 1,beta)*g3]}
            -  k2*T*[1 - betareg(y,alpha,beta)];
```

`betareg(x, a, b)` is the regularized incomplete Beta function: `I_x(a, b)`, the CDF of the
Beta distribution. The function appears 5 times in the objective equation.

The AD module (`src/ad/derivative_rules.py`) has no derivative rule for `betareg`. The
derivative with respect to x is:

```
d/dx betareg(x, a, b) = x^(a-1) * (1-x)^(b-1) / Beta(a, b)
```

where `Beta(a, b) = Gamma(a) * Gamma(b) / Gamma(a + b)` is the Beta function.

---

## Suggested Fix

Add a `_diff_betareg()` method to `src/ad/derivative_rules.py` following the pattern of
existing derivative rules. Register it in the function dispatch table (around line 570-600).

The implementation needs:
1. The derivative formula above (Beta PDF divided by Beta function)
2. Handle the case where only `x` is the differentiation variable (not `a` or `b`, which
   are typically parameters, not decision variables)

**Effort estimate:** ~2-3h (mathematical formula + implementation + testing)

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py` | Add `_diff_betareg()` derivative rule and register in dispatch |

---

## Related Issues

- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.5 documents the original parse blocker
- Other functions that may also need AD rules in the future: `centropy`, `mapval`, `sign`
