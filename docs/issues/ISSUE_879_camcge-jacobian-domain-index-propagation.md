# camcge: Jacobian Domain Index Not Remapped in Stationarity Sums

**GitHub Issue:** [#879](https://github.com/jeffreyhorn/nlp2mcp/issues/879)
**Status:** OPEN
**Severity:** High — Model compiles but solver aborts with 1 execution error (division by zero)
**Date:** 2026-02-25
**Affected Models:** camcge

---

## Problem Summary

After the partial fix for Issue #871 (DollarConditional subset conditioning), camcge has
1 remaining execution error: `stat_pd(services)` division by zero. The root cause is that
Jacobian derivative expressions from subset-restricted equations use the **outer stationarity
domain index** instead of the **inner sum index** for certain parameter references.

---

## Error Details

```
**** Exec Error at line 456: division by zero (0)
**** Evaluation error(s) in equation "stat_pd(services)"
       Problem in Jacobian evaluation of "nu_costmin(ag-subsist)"
       Problem in Jacobian evaluation of "nu_costmin(ag-exp+ind)"
       Problem in Jacobian evaluation of "nu_costmin(sylvicult)"
       Problem in Jacobian evaluation of "nu_costmin(ind-alim)"
```

---

## Root Cause: Domain Index Not Remapped

The original equation `costmin(it)` uses parameters indexed by `it` (the traded sectors
subset). When the Jacobian `d(costmin)/d(pd)` is computed and wrapped in a stationarity
sum `sum(it, deriv * nu_costmin(it))`, some parameter indices are incorrectly emitted with
the outer domain `i` instead of the inner sum index `it`.

### Emitted (WRONG):

```gams
stat_pd(i).. ... + sum(it,
    ((-1) * ((pd(it) / pm(it) * delta(i) / (1 - delta(i))) ** (1 / (1 + rhoc(i))) * ...
    )) * nu_costmin(it)) + ...
```

Note: `pd(it)`, `pm(it)` correctly use the sum index, but `delta(i)`, `rhoc(i)` use the
outer stationarity domain `i`.

### Should Be (CORRECT):

```gams
stat_pd(i).. ... + sum(it,
    ((-1) * ((pd(it) / pm(it) * delta(it) / (1 - delta(it))) ** (1 / (1 + rhoc(it))) * ...
    )) * nu_costmin(it)) + ...
```

All parameter references that were `delta(it)`, `rhoc(it)` in the original `costmin(it)`
equation should remain `delta(it)`, `rhoc(it)` inside the stationarity sum.

### Why This Causes Division by Zero

- `services` is NOT in the `it` subset (it's a non-traded sector)
- `delta('services') = 0` (calibrated only for traded sectors)
- When evaluating `stat_pd('services')`, the `sum(it, ...)` iterates over traded sectors
- But `delta(i)` evaluates to `delta('services') = 0`
- Expressions like `delta(i) / (1 - delta(i))` and `(...)^(1/(1+rhoc(i)))` produce
  division by zero or 0^(negative) = Inf

### Same Pattern in Other Equations

The same `rhot(i)` vs `rhot(it)` bug appears in the esupply Jacobian terms:

```gams
sum(it, ((-1) * ((pe(it) / pd(it) * (1 - gamma(it)) / gamma(it)) ** (1 / (rhot(i) - 1))
    * ...)) * nu_esupply(it))
```

Here `rhot(i)` should be `rhot(it)`. This doesn't cause errors for `stat_pd(services)`
only because the other violations happen first, but it would cause errors for other
non-traded sectors.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/camcge.gms -o /tmp/camcge_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/camcge_mcp.gms o=/tmp/camcge_mcp.lst

# Check for execution errors:
grep 'Exec Error\|Evaluation error' /tmp/camcge_mcp.lst

# Verify incorrect indices in stationarity equation:
grep 'stat_pd' /tmp/camcge_mcp.gms | grep '\.\.'
# Look for delta(i), rhoc(i), rhot(i) inside sum(it, ...) — these should be delta(it) etc.
```

---

## Suggested Fix

The issue is in `_add_indexed_jacobian_terms()` in `src/kkt/stationarity.py` (around
line 1483). When building a stationarity term from an equation defined over a subset
domain (e.g., `costmin(it)` where `it ⊂ i`), the derivative expression is computed using
the equation's original indices. When this expression is wrapped in `sum(it, ...)` for the
stationarity equation, parameter references like `delta(it)` must retain `it` as their index.

Currently, the `_replace_indices_in_expr()` function (line ~996) remaps indices using the
`element_to_set` and `constraint_element_to_set` mappings. The bug is likely in how
`_build_constraint_element_mapping()` (line ~952) constructs the mapping when the
equation domain (`it`) differs from the variable domain (`i`).

### Specific Fix Approach

In `_add_indexed_jacobian_terms()`, when the constraint domain (`it`) differs from the
variable domain (`i`), the derivative expression should preserve the constraint's domain
index for parameter references. The `constraint_element_to_set` mapping should map
equation domain elements to the equation's domain set name (`it`), not the variable's
domain set name (`i`).

**Effort estimate:** ~4-6h (requires careful handling of index remapping edge cases)

---

## Files Likely Affected

| File | Change |
|------|--------|
| `src/kkt/stationarity.py` | Fix `_build_constraint_element_mapping()` or `_replace_indices_in_expr()` to preserve equation domain indices |

---

## Related Issues

- **Issue #871** (partial): camcge stationarity subset conditioning — the DollarConditional
  detection fix reduces errors from 5 to 1; this issue addresses the remaining error
- **Issue #862** (sambal): Related domain conditioning issues in stationarity builder
