# Issue #666: KKT generation domain mismatch when variable domain differs from equation domain

**GitHub Issue:** [#666](https://github.com/jeffreyhorn/nlp2mcp/issues/666)
**Status:** Open
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

### Generated stationarity equation (incorrect)

```gams
* stat_e(i) is the stationarity equation for variable e, indexed over i
stat_e(i).. ... + ((-1) * h(i)) * lam_tb + ... =E= 0;
stat_m(i).. ... + g(i) * lam_tb + ... =E= 0;
```

**Problem:** `h(i)` and `g(i)` are invalid because `h` and `g` are only declared over `t`, not `i`.

### Expected stationarity equation

Option 1 - Using conditional:
```gams
stat_e(i).. ... + ((-1) * h(t))$t(i) * lam_tb + ... =E= 0;
stat_m(i).. ... + g(t)$t(i) * lam_tb + ... =E= 0;
```

Option 2 - Using sum with sameas:
```gams
stat_e(i).. ... + sum(t$sameas(t,i), (-1) * h(t)) * lam_tb + ... =E= 0;
```

Option 3 - Zero for non-subset elements:
```gams
stat_e(i).. ... + (((-1) * h(i))$t(i) + 0$(not t(i))) * lam_tb + ... =E= 0;
```

## Problem Analysis

1. Variable `h` is declared over `t` (tradables subset: light-ind, food+agr, heavy-ind)
2. Variable `e` is declared over `i` (all sectors: light-ind, food+agr, heavy-ind, services)
3. In equation `tb`, `h(t)*e(t)` appears - both indexed by `t`
4. The stationarity equation for `e` is indexed by `i` (the variable's declared domain)
5. When computing ∂tb/∂e(i), the derivative of `sum(t, h(t)*e(t))` w.r.t. `e(i)` should be:
   - `h(t)` when `i ∈ t` (i.e., when `t(i)` is true)
   - `0` otherwise (for `i = services`)
6. **Bug:** The current code emits `h(i)` which is invalid since `h` is not defined for `i = services`

## GAMS Error

When compiling the generated MCP:
```
*** Error 170: Domain violation for element "services" in variable g(i)
*** Error 170: Domain violation for element "services" in variable h(i)
```

## Impact

- GAMS compilation error: domain mismatch
- The chenery model cannot be solved as MCP
- Any model with variables defined over subsets used in constraints will have this issue

## Root Cause Location

The issue is in the KKT stationarity equation generation code:

### Files to investigate

1. `src/kkt/assemble.py` - Main KKT assembly logic
2. `src/kkt/stationarity.py` - Stationarity equation construction (if exists)
3. `src/ad/jacobian.py` - Jacobian computation that feeds into stationarity
4. `src/emit/emit_gams.py` - Equation emission (may need domain-aware index mapping)

### Specific issue

When computing the Jacobian entry for `∂constraint/∂variable`:
- The constraint index (from the sum over `t`)
- The variable index (from `e`'s domain `i`)
- The reference to another variable (`h(t)`)

The code needs to:
1. Track that the derivative term includes `h(t)` where `t` is the constraint's index
2. When emitting the stationarity equation (indexed by `i`), recognize that `h` cannot be indexed by `i`
3. Either preserve the original index or add appropriate conditionals

## Fix Approach

### Option A: Domain-aware index substitution

When substituting the stationarity equation index into derivative terms:
1. Check if any referenced variable has a subset domain
2. If the stationarity index is outside that subset, emit 0
3. If inside, use the correct index with conditional

### Option B: Preserve original indices with conditionals

Keep the original `h(t)` reference but add `$t(i)` conditionals:
```gams
stat_e(i).. ... + ((-1) * h(t))$t(i) * lam_tb + ... =E= 0;
```

This requires:
1. Detecting when the sum index differs from the stationarity equation index
2. Adding appropriate domain conditionals
3. Possibly introducing alias indices to avoid conflicts

### Option C: Expand to element-wise equations

For subset-indexed variables, generate separate stationarity equations:
- `stat_e_tradables(t)` for the tradables
- `stat_e_nontradables(i)$(not t(i))` for non-tradables (with zero derivative terms)

## Test Case

```python
def test_stationarity_subset_variable_domain():
    """Verify stationarity equations handle subset-indexed variables correctly."""
    gams_code = '''
    Set i /a, b, c/;
    Set t(i) /a, b/;
    Variable x(i), y(t);
    Equation e;
    e.. sum(t, y(t) * x(t)) =l= 10;
    '''
    ir = parse_gams_string(gams_code)
    kkt = assemble_kkt_system(ir)
    
    # stat_x(i) should reference y(t) with $t(i) conditional, not y(i)
    stat_x = get_equation(kkt, 'stat_x')
    assert 'y(i)' not in stat_x  # Invalid: y not defined for all i
    assert 'y(t)' in stat_x or '$t(i)' in stat_x  # Valid alternatives
```

## Related

- Discovered during PR #664 review (comments 2781520079, 2781520112)
- May affect other gamslib models with subset-indexed variables
- Similar to index aliasing issues in equation emission
