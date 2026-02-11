# Cross-Indexed Sums Produce Uncontrolled Set Error 149

**GitHub Issue:** [#670](https://github.com/jeffreyhorn/nlp2mcp/issues/670)

**Issue:** Models with cross-indexed sums in constraints produce stationarity equations with uncontrolled set indices, causing GAMS Error 149.

**Status:** Open - Architectural Issue  
**Severity:** High - Affects 4 models  
**Affected Models:** abel, qabel, robert, chenery  
**Date:** 2026-02-10

---

## Problem Summary

When a constraint contains a sum over an index that also appears in a different position of a referenced symbol (cross-indexed sum), the derivative computation produces expressions where that index is "uncontrolled" - it appears in the equation body but not in the equation's domain.

GAMS Error 149: "Uncontrolled set entered as constant"

---

## Reproduction

### Test Case: abel.gms

```bash
# Translate the model
nlp2mcp data/gamslib/raw/abel.gms -o data/gamslib/mcp/abel_mcp.gms

# Run GAMS
cd data/gamslib/mcp && gams abel_mcp.gms lo=2

# Check errors
grep "149" abel_mcp.lst
```

**Error Output:**
```
**** 149  Uncontrolled set entered as constant
```

### Root Cause Analysis

In abel.gms, the constraint structure includes cross-indexed sums like:
```gams
sum(np, a(n,np)*x(np,k))
```

Where `np` is the summation index but `a(n,np)` references both `n` (equation domain) and `np` (sum index).

When computing the stationarity equation for a scalar variable, the derivative of this term produces:
```gams
stat_scalar.. ... + a(n,np) * nu_constraint(n) + ...
```

Here `n` and `np` are both uncontrolled because:
- The stationarity equation is for a scalar variable (no domain)
- But the expression contains `a(n,np)` which requires both indices

### Affected Equations in Generated MCP

From abel_mcp.lst:
```gams
stat_e(i).. ... + ((-1) * h(t)) * lam_tb + ...
```

The equation `stat_e(i)` is indexed by `i`, but references `h(t)` where `t` is not in the equation domain.

---

## Technical Details

### Why This Happens

1. **Constraint Definition**: `eq(n).. expr =e= sum(np, a(n,np)*x(np,k))`
2. **KKT Stationarity**: For variable `x(p,k)`, we need `∂L/∂x(p,k) = 0`
3. **Chain Rule**: `∂/∂x(p,k)[sum(np, a(n,np)*x(np,k))] = a(n,p)` when `np = p`
4. **Problem**: The derivative contains `a(n,p)` but the stationarity equation for `x` may not have `n` in its domain

### Current Behavior

The stationarity builder produces:
```gams
stat_x(p,k).. ... + sum(n, a(n,p) * nu_eq(n)) + ...
```

But when the original model structure doesn't properly propagate index mappings, we get:
```gams
stat_x(p,k).. ... + a(n,p) * nu_eq(n) + ...  * WRONG: n is uncontrolled
```

---

## Proposed Solution

### Option 1: Wrap in Appropriate Sum

When emitting terms with indices not in the equation domain, wrap them in a sum:
```gams
stat_x(p,k).. ... + sum(n, a(n,p) * nu_eq(n)) + ...
```

This requires:
1. Tracking which indices are "free" in each derivative term
2. Identifying which of those are not in the target equation's domain
3. Wrapping uncontrolled indices in appropriate sum aggregations

### Option 2: Index Mapping Propagation

Ensure the index_mapping module properly propagates all cross-referenced indices when building stationarity equations.

### Implementation Location

- `src/kkt/stationarity.py`: Stationarity equation builder
- `src/ad/index_mapping.py`: Index mapping for derivatives
- `src/emit/equations.py`: Equation emission

---

## Workaround

Currently none. These models cannot be translated to valid MCP format.

---

## Models Affected

| Model | Description | Cross-Index Pattern |
|-------|-------------|---------------------|
| abel | Linear Quadratic Control | `a(n,np)*x(np,k)` |
| qabel | Quadratic version of abel | Same pattern |
| robert | Resource allocation | Similar cross-indexing |
| chenery | Economic model | CES production functions |

---

## Related Issues

- Error 149 is also caused by other issues (e.g., quoted lag/lead references), but those have been fixed
- This specific cross-indexed sum pattern requires architectural changes

---

## References

- GAMS Error 149 Documentation: Uncontrolled set entered as constant
- Sprint 18 Day 5 analysis in SPRINT_LOG.md
