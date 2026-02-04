# Emit: Stationarity Equation Uses Uncontrolled Index Variable

**Status:** Open  
**Priority:** High  
**Affects:** meanvar.gms, potentially other models with subset indexing  
**GitHub Issue:** [#620](https://github.com/jeffreyhorn/nlp2mcp/issues/620)

---

## Summary

The KKT stationarity equation generator emits equations that reference index variables not controlled by the equation's domain. In `meanvar_mcp.gms`, the equation `stat_x(i)` references `mu(s)` where `s` is the superset, but the equation is only indexed over `i` (a subset of `s`). This causes GAMS Error 149 "Set is not under control".

## Symptoms

- **Model:** meanvar.gms
- **Parse:** SUCCESS
- **Translate:** SUCCESS (generates MCP file)
- **Solve:** FAILS with GAMS compilation error

```
Error 149: Symbol 's' is not under control in this context
```

## Root Cause

In the stationarity equation generation (likely in `src/kkt/stationarity.py` or `src/emit/expr_to_gams.py`), when computing partial derivatives of constraints with respect to variables, the code is not properly substituting the equation's controlled index for parameter references.

**Problem Code in Generated MCP:**
```gams
Sets
    s /cn, fr, gr, jp, sw, uk, us, wr/
    i(s) /cn, fr, gr, jp, sw, uk, us/  * i is a SUBSET of s
;

Parameters
    mu(s) /cn 0.1287, fr 0.1096, .../  * mu is defined over s
;

* BUG: stat_x(i) references mu(s) but s is not controlled - should be mu(i)
stat_x(i).. 0 + ... + ((-1) * mu(s)) * nu_mbal + ... + (mu(s) - r) * nu_riskless + (sf * sum(h, mu(h)) + (1 - sf) * mu(s) + ...) * nu_meanbal + ... =E= 0;
```

**Correct Code Should Be:**
```gams
stat_x(i).. 0 + ... + ((-1) * mu(i)) * nu_mbal + ... + (mu(i) - r) * nu_riskless + (sf * sum(h, mu(h)) + (1 - sf) * mu(i) + ...) * nu_meanbal + ... =E= 0;
```

## Analysis

The original `meanvar.gms` model has:
- Set `s` (superset): cn, fr, gr, jp, sw, uk, us, wr (8 elements)
- Set `i(s)` (subset): cn, fr, gr, jp, sw, uk, us (7 elements, excludes wr)
- Parameter `mu(s)` defined over the superset
- Variable `x(i)` defined over the subset

When generating the stationarity equation for `x(i)`, the gradient terms involving `mu` should use `mu(i)` (the subset index), not `mu(s)` (the superset). The parameter `mu` is valid for all elements of `i` since `i ⊆ s`.

## Proposed Solution

In the stationarity equation generator:
1. When emitting parameter references in gradients, check if the parameter's domain is a superset of the equation's domain
2. If so, substitute the equation's index variable for the parameter's index
3. This may require tracking domain relationships during KKT construction

**Likely Code Locations:**
- `src/kkt/stationarity.py` - Stationarity equation construction
- `src/emit/expr_to_gams.py` - Expression emission
- `src/ir/ast.py` - AST node handling for indexed references

## Reproduction Steps

```bash
# 1. Parse and translate meanvar.gms (from repo root)
python -m src.cli data/gamslib/raw/meanvar.gms -o /tmp/meanvar_mcp.gms

# 2. Attempt to run with GAMS (will fail)
gams /tmp/meanvar_mcp.gms

# 3. Observe Error 149 on the stat_x equation
```

## Impact

- Models with subset/superset relationships in variable/parameter domains
- Affects solve success rate for translated models
- meanvar.gms is a portfolio optimization model from GAMSLIB

## Testing

1. Unit test: Verify index substitution when parameter domain is superset of equation domain
2. Integration test: meanvar.gms compiles successfully after fix
3. Regression test: Other models with simple indexing still work

## References

- `data/gamslib/mcp/meanvar_mcp.gms` - Generated MCP file showing the bug
- `data/gamslib/raw/meanvar.gms` - Original GAMS model
- `src/kkt/stationarity.py` - Stationarity equation generator
- PR #619 review comment identifying this issue

---

**Created:** 2026-02-04  
**Sprint:** Sprint 17 Day 9
