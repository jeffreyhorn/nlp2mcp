# Mingamma: Digamma Function Not Available in GAMS

**GitHub Issue:** [#676](https://github.com/jeffreyhorn/nlp2mcp/issues/676)

**Issue:** The derivative rules for `gamma(x)` and `loggamma(x)` produce expressions using `psi(x)` (digamma function), but GAMS does NOT have a built-in `psi` or `digamma` function.

**Status:** ✅ RESOLVED (Option 2 implemented)  
**Severity:** High - Model fails to compile  
**Affected Models:** mingamma, any model using gamma/loggamma derivatives  
**Date:** 2026-02-10  
**Investigated:** 2026-02-11  
**Resolved:** 2026-02-11

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

## Resolution (2026-02-11)

**Option 2 was implemented:** Models using `gamma(x)` or `loggamma(x)` in expressions that require differentiation now raise a clear error message.

### Changes Made

1. **`src/ad/derivative_rules.py`**:
   - Removed `_diff_gamma()` and `_diff_loggamma()` functions
   - Added clear error when attempting to differentiate gamma/loggamma:
     ```python
     elif func in ("gamma", "loggamma"):
         raise ValueError(
             f"Differentiation of '{func}' requires the digamma/psi function, "
             f"which is not available in GAMS. Models using {func}() in the "
             f"objective or constraints cannot be converted to MCP."
         )
     ```

2. **`data/gamslib/gamslib_status.json`**:
   - Set `mingamma` model's `convexity.status` to `"excluded"`
   - Added error message: "Gamma function is not convex on x>0. Additionally, GAMS lacks the digamma/psi function needed for derivatives."

3. **`tests/unit/ad/test_transcendental.py`**:
   - Updated gamma/loggamma tests to expect the new error message
   - Reduced from 10 tests to 6 tests (3 for gamma, 3 for loggamma)

### Rationale

- The gamma function is not convex on x > 0, so mingamma is not a valid candidate for NLP-to-MCP conversion anyway
- Very few GAMS models use gamma functions in optimization objectives
- A clear error message is better than silently generating invalid GAMS code

---

## References

- [Digamma function - Wikipedia](https://en.wikipedia.org/wiki/Digamma_function)
- GAMS Built-in Functions (no psi/digamma available)
