# KKT Stationarity: Cross-Domain Summation in Constraints

**Status:** Open  
**Priority:** Medium  
**Affects:** trussm.gms, potentially other models with constraints summing over variables with different index domains  
**GitHub Issue:** [#594](https://github.com/jeffreyhorn/nlp2mcp/issues/594)

---

## Summary

The KKT stationarity equation builder fails when a constraint's domain partially overlaps with a variable's domain through a shared index, but also includes indices not in the variable domain. This occurs when a constraint sums over a variable using a different index set.

## Symptoms

- **Model:** trussm.gms (GAMSLIB SEQ=432)
- **Parse:** SUCCESS
- **Translate:** FAILS

```
Error: Invalid model - Incompatible domains for summation: variable domain ('i', 'k'), 
multiplier domain ('j', 'k'). Multiplier domain must be either a subset of variable 
domain or completely disjoint.
```

## Root Cause

The error is raised in `src/kkt/stationarity.py` at line 623. The stationarity equation builder has logic that requires multiplier domains to be either:
1. A subset of the variable domain, OR
2. Completely disjoint from the variable domain

However, the `trussm` model has a valid constraint pattern where the constraint sums over the variable using a different index:

**Variable:** `s(i,k)` - stress on bar `i` under load scenario `k`  
**Constraint:** `stiffness(j,k).. sum(i, s(i,k)*b(j,i)) =E= f(j,k)`

Here:
- Variable domain: `('i', 'k')`
- Constraint/multiplier domain: `('j', 'k')`
- Shared index: `k`
- Non-shared indices: `i` (in variable), `j` (in constraint)

The constraint sums over `i` (the bars), so when computing stationarity for `s(i,k)`, the derivative with respect to each `s(i,k)` should be multiplied by the appropriate `lambda_stiffness(j,k)` for all `j`, then summed over `j`.

**Location:** `src/kkt/stationarity.py` lines 614-627

```python
if mult_domain != var_domain and len(mult_domain) > 0:
    # Check domain compatibility: mult_domain should be subset of var_domain
    # or they should be disjoint (independent indexing)
    mult_domain_set = set(mult_domain)
    var_domain_set = set(var_domain)
    if not mult_domain_set.issubset(
        var_domain_set
    ) and mult_domain_set.intersection(var_domain_set):
        # Domains overlap but aren't compatible for summation
        raise ValueError(
            f"Incompatible domains for summation: variable domain {var_domain}, "
            f"multiplier domain {mult_domain}. Multiplier domain must be either "
            f"a subset of variable domain or completely disjoint."
        )
```

## Model Structure

From `trussm.gms`:

```gams
Set i  "bars"           /i1*i5/
    j  "nodes"          /j1*j4/
    k  "load scenarios" /k1*k3/;

Variables
    s(i,k)     "stress on bar i under load scenario k";

Equations
    stiffness(j,k) "stiffness requirement for bar j under load k";

stiffness(j,k).. sum(i, s(i,k)*b(j,i)) =E= f(j,k);
```

The stiffness constraint indexed by `(j,k)` contains a sum over `i` of variable `s(i,k)`.

## Mathematical Analysis

For the Lagrangian:
```
L = tau + sum(j,k, lambda_stiffness(j,k) * (sum(i, s(i,k)*b(j,i)) - f(j,k))) + ...
```

The stationarity condition for `s(i,k)` is:
```
dL/ds(i,k) = sum(j, lambda_stiffness(j,k) * b(j,i)) + ... = 0
```

Note that:
- The derivative is with respect to `s(i,k)` (specific `i`, specific `k`)
- The sum is over `j` (all nodes)
- The `k` index is shared (same load scenario)
- The result should be indexed by `(i,k)` - same as the variable

This is a valid mathematical operation that the current code rejects.

## Proposed Solution

Enhance the domain compatibility check in `_build_stationarity_expr_for_indexed_var()` to handle the case where:
1. Domains partially overlap (share some indices)
2. The constraint contains a sum over the variable that eliminates the non-shared variable indices

The key insight is:
- Variable domain: `(i, k)` 
- Multiplier domain: `(j, k)`
- Shared: `k`
- The constraint sums over `i`, so the derivative w.r.t. `s(i,k)` is valid
- Result: sum over `j` of `(derivative * lambda(j,k))`, indexed by `(i,k)`

**Implementation approach:**
1. Detect when constraint contains `sum(idx, ...)` over the variable
2. Extract which indices are summed over in the constraint body
3. If the summed indices match the "extra" variable indices (not in multiplier domain), allow the partial overlap
4. Build the stationarity term as: `sum(j, derivative * lambda(j,k))`

## Reproduction Steps

```bash
cd /Users/jeff/experiments/nlp2mcp
.venv/bin/python -m src.cli data/gamslib/raw/trussm.gms -o /tmp/trussm_mcp.gms
```

**Expected:** Successful translation to MCP format  
**Actual:** Error about incompatible domains

## Minimal Reproduction

```python
from src.ir.parser import parse_model_file

model_ir = parse_model_file('data/gamslib/raw/trussm.gms')
print('Parse: SUCCESS')

# Verify structure
print('Variable s domain:', model_ir.variables['s'].domain)  # ('i', 'k')
print('Equation stiffness domain:', model_ir.equations['stiffness'].domain)  # ('j', 'k')

# This will fail
from src.kkt import build_kkt_system
kkt = build_kkt_system(model_ir)  # Raises ValueError
```

## Impact

- **Translation Rate:** Currently 25/48 (52.1%) - could increase with this fix
- **Models Affected:** trussm.gms (confirmed), likely other models with similar constraint patterns
- **Problem Types:** Structural optimization, network flow, transportation problems where constraints aggregate variables across different index sets

## Testing Requirements

1. Unit test for domain overlap detection in `src/kkt/stationarity.py`
2. Unit test for correct stationarity expression when constraint sums over variable
3. Integration test: trussm.gms translates successfully
4. Integration test: generated MCP compiles with GAMS
5. Validation test: MCP solution matches NLP solution
6. Regression test: existing models still work

## Related Issues

- Part of Sprint 17 Translation Quick Wins analysis
- Listed in `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md` as `model_domain_mismatch` category

## References

- **Source File:** `src/kkt/stationarity.py` lines 614-627
- **Test Model:** `data/gamslib/raw/trussm.gms` (GAMSLIB SEQ=432)
- **Sprint Context:** Sprint 17 Day 1 - discovered while fixing objective extraction

---

**Created:** 2025-01-31  
**Sprint:** Sprint 17 Day 1
