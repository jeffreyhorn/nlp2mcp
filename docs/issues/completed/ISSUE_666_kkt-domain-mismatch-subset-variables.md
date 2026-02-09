# Issue #666: KKT generation domain mismatch when variable domain differs from equation domain

**GitHub Issue:** [#666](https://github.com/jeffreyhorn/nlp2mcp/issues/666)
**Status:** Fixed
**Priority:** High
**Category:** KKT Generation Bug

## Summary

The KKT generator produces stationarity equations with incorrect variable indices when a variable is declared over a subset but appears in equations indexed over a superset. This causes GAMS compilation errors due to domain mismatch.

## Reproduction

**Model:** `data/gamslib/raw/chenery.gms`

### Original variable declarations

```gams
Set
   i    'sectors'    / light-ind, food+agr, heavy-ind, services /
   t(i) 'tradables'  / light-ind, food+agr, heavy-ind /;  * t is subset of i

Variable
   e(i)    'quantity of exports'        * defined over all sectors
   m(i)    'quantity of imports'        * defined over all sectors
   g(t)    'foreign exchange cost of imports'   * defined only over tradables
   h(t)    'foreign exchange value of exports'  * defined only over tradables
```

### Key equation (trade balance)

```gams
tb..  sum(t, g(t)*m(t) - h(t)*e(t)) =l= dbar;
```

Note: In this equation, `e(t)` and `m(t)` use the subset index `t`, not the full domain `i`.

### Generated stationarity equation (incorrect - before fix)

```gams
* stat_e(i) is the stationarity equation for variable e, indexed over i
stat_e(i).. ... + ((-1) * h(i)) * lam_tb + ... =E= 0;
stat_m(i).. ... + g(i) * lam_tb + ... =E= 0;
```

**Problem:** `h(i)` and `g(i)` are invalid because `h` and `g` are only declared over `t`, not `i`.

### Expected stationarity equation (after fix)

```gams
stat_e(i).. ... + ((-1) * h(t)) * lam_tb + ... =E= 0;
stat_m(i).. ... + g(t) * lam_tb + ... =E= 0;
```

The variable's subset index `t` is preserved rather than being replaced with the superset index `i`.

## GAMS Error (before fix)

When compiling the generated MCP:
```
*** Error 170: Domain violation for element "services" in variable g(i)
*** Error 170: Domain violation for element "services" in variable h(i)
```

## Fix Details

**Fixed in:** [PR #667](https://github.com/jeffreyhorn/nlp2mcp/pull/667)
**Fix date:** 2026-02-09

### Root Cause

The `_replace_indices_in_expr()` function in `src/kkt/stationarity.py` was replacing element-specific indices (like `"light-ind"`) with the stationarity equation's domain indices (like `i`) without checking if the variable's declared domain was a subset of that equation domain.

### Solution

Added a new helper function `_preserve_subset_var_indices()` that:

1. Checks if the variable is defined over a subset of the stationarity equation's domain
2. If the variable's domain set is declared as a subset (via `SetDef.domain`), preserves the subset index
3. For example, `h(t)` where `t(i)` remains `h(t)` in `stat_e(i)`, not `h(i)`

### Files Modified

1. **`src/kkt/stationarity.py`**:
   - Added `_preserve_subset_var_indices()` helper function (lines 567-612)
   - Modified `_replace_indices_in_expr()` VarRef case to call the new helper before index substitution (lines 479-488)

2. **`tests/integration/kkt/test_stationarity.py`**:
   - Added `TestStationaritySubsetVariableDomain` test class with:
     - `test_subset_variable_preserved_in_stationarity()` - verifies h(t) stays h(t) in stat_e(i)
     - `test_superset_variable_uses_equation_domain()` - verifies normal case still works

### Verification

```python
# Before fix:
stat_e LHS: Binary(+, Const(1.0), Binary(*, VarRef(h(i)), MultiplierRef(lam_tb)))
# ERROR: h(i) causes GAMS Error 170

# After fix:
stat_e LHS: Binary(+, Const(1.0), Binary(*, VarRef(h(t)), MultiplierRef(lam_tb)))
# CORRECT: h(t) uses the subset index
```

## Related

- Discovered during PR #664 review (comments 2781520079, 2781520112)
- May affect other gamslib models with subset-indexed variables
- Similar to Issue #620 (superset index substitution for parameters)
