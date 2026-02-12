# Cross-Indexed Sums Produce Uncontrolled Set Error 149

**GitHub Issue:** [#670](https://github.com/jeffreyhorn/nlp2mcp/issues/670)

**Issue:** Models with cross-indexed sums in constraints produce stationarity equations with uncontrolled set indices, causing GAMS Error 149.

**Status:** Open - Architectural Issue  
**Severity:** High - Affects 6 models  
**Affected Models:** abel, qabel, chenery, mexss, orani, robert (partial)  
**Date:** 2026-02-10  
**Updated:** 2026-02-11 (Sprint 18 Day 9)

---

## Problem Summary

When a constraint contains a sum over an index that also appears in a different position of a referenced symbol (cross-indexed sum), the derivative computation produces expressions where that index is "uncontrolled" - it appears in the equation body but not in the equation's domain.

GAMS Error 149: "Uncontrolled set entered as constant"

---

## Sprint 18 Day 7-8 Analysis

During Sprint 18 Days 7-8 domain investigation, we identified that **6 models** are blocked by this architectural issue. After the Day 7 wildcard fix (PR #680), the E170/E171 domain violations were resolved for mexss and orani upon regeneration, but E149 errors remain due to cross-indexed sums.

### Complete Model Analysis

| Model | Original Errors | After Day 7 Fix | Root E149 Cause |
|-------|-----------------|-----------------|-----------------|
| abel | E149 | E149 | `ku` subset in sum over `(m__,mp)` |
| qabel | E149 | E149 | Same as abel (quadratic version) |
| chenery | E149 | E149 | Cross-indexed sums in CES functions |
| mexss | E170/E171 | E149 | `a(c,p)` where `c` not in equation domain |
| orani | E170/E171 | E149 | Cross-indexed sums in stationarity equations |
| robert | E170 | E170/E149 | E170 from table parsing (ISSUE_399); also has E149 |

---

## Per-Model Root Cause Analysis

### 1. abel and qabel

**Constraint Pattern:**
```gams
* Original constraint uses cross-indexed sum with dynamic subset ku
stateq(n,k).. x(n,k+1) =e= sum(np, a(n,np)*x(np,k)) + sum(m, b(n,m)*u(m,k))
```

**Generated Stationarity Issue (from abel_mcp.gms):**
```gams
stat_x(n,k).. 0.5 * sum(np, 0) + 0.5 * sum((ku,m,mp), 0) + ((-1) * (a(n,np) + sum(m, 0))) * nu_stateq(n,k) =E= 0;
```

The equation `stat_x(n,k)` references `a(n,np)` where `np` is not a controlled index in the equation domain. The cross-indexed sum in the original constraint produces derivative terms with uncontrolled indices.

**Classification:** ARCHITECTURAL - Requires KKT stationarity builder changes to wrap uncontrolled indices in sums.

### 2. chenery

**Constraint Pattern:**
```gams
* CES production function with cross-indexed coefficients
ces(s).. sum(j, a(s,j) * x(j)^rho)^(1/rho) =e= output(s)
```

**Generated Stationarity Issue:**
The derivative of CES functions produces terms with indices from the sum that are not in the stationarity equation's domain.

**Classification:** ARCHITECTURAL - Same root cause as abel/qabel.

### 3. mexss

**Constraint Pattern:**
```gams
* Demand-supply balance with cross-region coefficients
supply(p).. sum(i, a(c,p) * z(p,i)) =e= demand(p)
```

**Generated Stationarity Issue:**
```gams
stat_z(p,i).. ... + a(c,p) * nu_supply(p) + ...
```

The equation `stat_z(p,i)` references `a(c,p)` where `c` is not a controlled index.

**Day 7 Impact:** The wildcard fix resolved E170/E171 errors (regenerated file uses `rd(*,*)` correctly), but E149 remains.

**Classification:** ARCHITECTURAL - Cross-indexed parameter reference.

### 4. orani

**Constraint Pattern:**
```gams
* Multi-sector economic model with input-output matrices
balance(c,s).. sum(i, amc(c,s,i) * x(i)) =e= total(c,s)
```

**Generated Stationarity Issue:**
Cross-indexed sums in the stationarity equations produce uncontrolled indices.

**Day 7 Impact:** The wildcard fix resolved E170/E171 errors (preserves `amc(c,s,*)` for dynamic domain extension). E149 remains from cross-indexed sums.

**Classification:** ARCHITECTURAL - Same root cause.

### 5. robert (Partial)

**Primary Issue:** E170 from table parsing (ISSUE_399 - table description parsed as header).

**Secondary Issue:** Also has E149 from cross-indexed sums in stationarity equations:
```gams
stat_s(r,tt).. ... + c(p,t) * nu_constraint + ...
```

Where `c(p,t)` references `t` but equation is indexed over `tt`.

**Classification:** Requires both ISSUE_399 (parser) and ISSUE_670 (KKT) fixes.

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

### Option 1: Wrap in Appropriate Sum (Preferred)

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

### Estimated Effort

**High** - This is a fundamental change to how stationarity equations handle cross-domain references. Requires:
- Index analysis infrastructure to detect uncontrolled indices
- Sum wrapping logic in stationarity builder
- Extensive testing across all affected models
- Potential changes to multiplier variable domain inference

---

## Workaround

Currently none. These models cannot be translated to valid MCP format until this architectural issue is addressed.

---

## Models Affected Summary

| Model | Description | Cross-Index Pattern | Sprint 18 Status |
|-------|-------------|---------------------|------------------|
| abel | Linear Quadratic Control | `a(n,np)*x(np,k)` | ARCHITECTURAL |
| qabel | Quadratic version of abel | Same pattern | ARCHITECTURAL |
| chenery | Economic model | CES production functions | ARCHITECTURAL |
| mexss | Multi-region supply | `a(c,p)*z(p,i)` | ARCHITECTURAL |
| orani | Input-output model | Multi-sector matrices | ARCHITECTURAL |
| robert | Resource allocation | Cross-time references | ARCHITECTURAL (also ISSUE_399) |

---

## Related Issues

- ISSUE_392: Table continuation syntax (affects `like`)
- ISSUE_399: Table description as header (affects `robert`)
- ISSUE_671: orani dynamic domain extension (resolved by Day 7 fix)
- ISSUE_674: mexss/sample wildcard domain (resolved by Day 7 fix)

---

## References

- GAMS Error 149 Documentation: Uncontrolled set entered as constant
- Sprint 18 Days 5, 7-8 analysis in SPRINT_LOG.md
- PR #680: Wildcard domain preservation fix
