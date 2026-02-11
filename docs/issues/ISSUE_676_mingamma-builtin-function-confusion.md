# Mingamma: Digamma Function Not Available in GAMS

**GitHub Issue:** [#676](https://github.com/jeffreyhorn/nlp2mcp/issues/676)

**Issue:** The derivative rules for `gamma(x)` and `loggamma(x)` produce expressions using `psi(x)` (digamma function), but GAMS does NOT have a built-in `psi` or `digamma` function.

**Status:** Cannot Fix (Architectural)  
**Severity:** High - Model fails to compile  
**Affected Models:** mingamma, any model using gamma/loggamma derivatives  
**Date:** 2026-02-10  
**Investigated:** 2026-02-11

---

## Problem Summary

When differentiating expressions containing `gamma(x)` or `loggamma(x)`, the mathematically correct derivatives are:
- d/dx[gamma(x)] = gamma(x) * psi(x)
- d/dx[loggamma(x)] = psi(x)

Where `psi(x)` is the digamma function: ψ(x) = Γ'(x)/Γ(x)

**The fundamental problem:** GAMS does NOT have a built-in `psi` or `digamma` function.

---

## Root Cause Analysis

### Derivative Rules

In `src/ad/derivative_rules.py`, the gamma derivative rules are:

```python
def _diff_gamma(expr, wrt_var, wrt_indices, config):
    # d(gamma(a))/dx = gamma(a) * psi(a) * da/dx
    gamma_arg = Call("gamma", (arg,))
    psi_arg = Call("psi", (arg,))  # <-- psi doesn't exist in GAMS!
    return Binary("*", Binary("*", gamma_arg, psi_arg), darg_dx)

def _diff_loggamma(expr, wrt_var, wrt_indices, config):
    # d(loggamma(a))/dx = psi(a) * da/dx
    psi_arg = Call("psi", (arg,))  # <-- psi doesn't exist in GAMS!
    return Binary("*", psi_arg, darg_dx)
```

The comment on line 1155 incorrectly states "GAMS uses 'psi' as the function name (added in GAMS 47.0+)".

### Verification

Tested with GAMS 51.3.0:
```gams
Scalar x /2.5/;
Variable v;
Equation e;
e.. psi(x) =e= 0;  
```

Result:
```
**** 121  Set expected
**** 140  Unknown symbol
```

GAMS documentation confirms: The available gamma-related functions are:
- `gamma(x)` - Gamma function
- `logGamma(x)` - Log of gamma function
- `beta(x,y)` - Beta function
- `logBeta(x,y)` - Log of beta function
- `betaReg(x,y,z)` - Regularized beta function
- `gammaReg(x,a)` - Regularized gamma function

**No `psi`, `digamma`, or `polygamma` function exists.**

---

## Possible Solutions

### Option 1: Polynomial Approximation (Complex)

Implement digamma using a polynomial/series approximation. The asymptotic expansion is:
```
psi(x) ≈ ln(x) - 1/(2x) - 1/(12x^2) + 1/(120x^4) - ...
```

For x > 6, this is accurate. For smaller x, use the recurrence:
```
psi(x+1) = psi(x) + 1/x
```

This would require:
- Creating a macro or inline function
- Handling edge cases (x <= 0, small x)
- Significant complexity

### Option 2: Skip Gamma Derivative Models (Recommended)

Mark models using `gamma(x)` or `loggamma(x)` in nonlinear expressions as unsupported. The original model can still use these functions, but we cannot compute derivatives for the MCP transformation.

### Option 3: Numerical Differentiation

Use finite differences to approximate derivatives involving gamma functions. This would add complexity and numerical error.

---

## Recommendation

**Option 2 is recommended.** The mingamma model and similar models using gamma/loggamma in expressions that require differentiation should be marked as unsupported with a clear error message.

This affects very few models - most GAMS models don't use gamma functions in optimization objectives.

---

## Files Requiring Changes

If implementing Option 2:
- `src/ad/derivative_rules.py`: Raise an error when gamma/loggamma derivative is needed
- Add a clear error message explaining the limitation

If implementing Option 1:
- `src/emit/expr_to_gams.py`: Add digamma approximation function
- `src/ad/derivative_rules.py`: Use the approximation instead of `Call("psi", ...)`

---

## Workaround

None currently. Models using gamma/loggamma derivatives cannot be translated.

---

## References

- [Digamma function - Wikipedia](https://en.wikipedia.org/wiki/Digamma_function)
- GAMS Built-in Functions (no psi/digamma available)
