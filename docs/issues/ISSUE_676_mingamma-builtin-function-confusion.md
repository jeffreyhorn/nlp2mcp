# Mingamma: Built-in Function Confusion

**GitHub Issue:** [#676](https://github.com/jeffreyhorn/nlp2mcp/issues/676)

**Issue:** The mingamma model uses GAMS built-in functions `gamma(x)` and its derivative `psi(x)`. The emitter incorrectly treats these as indexed parameters instead of function calls.

**Status:** Open  
**Severity:** High - Model fails to compile  
**Affected Models:** mingamma  
**Date:** 2026-02-10

---

## Problem Summary

GAMS provides built-in mathematical functions including:
- `gamma(x)` - Gamma function Γ(x)
- `psi(x)` - Digamma function ψ(x) = Γ'(x)/Γ(x) (derivative of log-gamma)

When differentiating `gamma(x1)` with respect to `x1`, the derivative should be `gamma(x1) * psi(x1)`. However, the emitter produces `gamma(x1) * psi(x1)` where `gamma` and `psi` are treated as unknown symbols with `x1` as an index.

GAMS Errors:
- Error 121: Set expected
- Error 140: Unknown symbol

---

## Reproduction

### Test Case: mingamma.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/mingamma.gms -o data/gamslib/mcp/mingamma_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams mingamma_mcp.gms lo=2

# Check errors
grep -E "121|140" mingamma_mcp.lst
```

**Error Output:**
```
**** 121  Set expected
**** 140  Unknown symbol
```

### Original Model

```gams
Variable y1, y2, x1, x2;
y1def.. y1 =e= gamma(x1);
y2def.. y2 =e= loggamma(x2);
```

### Generated Stationarity Equation (Wrong)

```gams
stat_x1.. 0 + ((-1) * (gamma(x1) * psi(x1))) * nu_y1def - piL_x1 =E= 0;
```

GAMS sees `gamma(x1)` as a parameter reference where `gamma` is undefined and `x1` is used as an index (but `x1` is a variable, not a set).

### Expected Stationarity Equation (Correct)

The derivative d/dx[gamma(x)] = gamma(x) * psi(x) should be emitted as function calls:
```gams
stat_x1.. 0 + ((-1) * (gamma(x1.l) * psi(x1.l))) * nu_y1def - piL_x1 =E= 0;
```

Or using the variable directly in functions (GAMS supports this):
```gams
stat_x1.. 0 + ((-1) * (gamma(x1) * psi(x1))) * nu_y1def - piL_x1 =E= 0;
```

---

## Technical Details

### Why Error 121 "Set expected"

GAMS parses `gamma(x1)` as:
- `gamma` - Unknown identifier (Error 140)
- `(x1)` - Expected to be a set index, but `x1` is a variable (Error 121)

### What's Actually Needed

In GAMS, `gamma(x1)` where `x1` is a variable should work because:
- `gamma` is a recognized built-in function
- Function arguments can be variables

The issue is either:
1. The emitter is not recognizing `gamma`/`psi` as function calls
2. Or the expression structure is incorrect

### Derivative Rule for Gamma

The derivative computation appears correct:
```
d/dx[gamma(x)] = gamma(x) * psi(x)
```

But the emission may be formatting it incorrectly.

---

## Investigation Needed

1. **Check AST structure**: Is `gamma(x1)` parsed as a `Call` node or something else?
2. **Check expr_to_gams**: How are function calls with variable arguments emitted?
3. **Test simple case**: Does `gamma(x)` work in a simpler equation?

### Key Files

- `src/ad/derivative_rules.py`: Derivative of gamma function
- `src/emit/expr_to_gams.py`: Function call emission
- `src/ir/parser.py`: Function call parsing

---

## Proposed Solution

1. **Verify function call emission**: Ensure `Call("gamma", [VarRef("x1")])` emits correctly
2. **Check variable in function context**: GAMS allows `gamma(x1)` where `x1` is a variable
3. **Add gamma/psi to known functions**: May need special handling for these built-ins

---

## Workaround

Currently none. The mingamma model cannot be translated correctly.

---

## Related Functions

Other GAMS special functions that may have similar issues:
- `loggamma(x)` - Log of gamma function
- `beta(x,y)` - Beta function
- `binomial(n,k)` - Binomial coefficient

---

## References

- GAMS Built-in Functions Documentation
- Gamma Function: Γ(x) = ∫₀^∞ t^(x-1) * e^(-t) dt
- Digamma Function: ψ(x) = d/dx[ln(Γ(x))] = Γ'(x)/Γ(x)
