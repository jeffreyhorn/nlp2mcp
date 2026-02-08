# KKT Generation: Set Index Emitted as String Literal (dispatch model)

**GitHub Issue:** #603
**URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/603
**Status:** Open
**Priority:** High
**Affects:** dispatch model (and potentially others using set indices in summations)

## Summary

The KKT stationarity equation generation incorrectly emits set index names as quoted string literals instead of set references. For example, `gendata(i,cg)` becomes `gendata(i,"cg")`, causing GAMS Error 170 (Domain violation for element).

## Reproduction

### Input Model
File: `data/gamslib/raw/dispatch.gms`

```gams
Set
   i           'generators'                / p1*p3 /
   genchar     'generator characteristics' / a, b, c, upplim, lowlim /
   cg(genchar) 'cost categories'           / a, b, c /;

Table gendata(i,genchar) 'generator cost characteristics and limits'
           a       b        c  upplim  lowlim
   p1  213.1  11.669  0.00533     200      50
   ...

Parameter pexp(cg) 'exponent for cost function' / a 0, b 1, c 2 /;

Equation costfn  'total cost calculation';

costfn..  cost =e= sum((i,cg), gendata(i,cg)*power(p(i),pexp(cg)));
```

### Steps to Reproduce

```bash
# Generate MCP file
python -m src.cli data/gamslib/raw/dispatch.gms -o data/gamslib/mcp/dispatch_mcp.gms

# Run GAMS (will fail with compilation errors)
gams data/gamslib/mcp/dispatch_mcp.gms
```

### Expected Output (Stationarity Equation)

```gams
stat_cost.. ... + (1 - sum((i,cg), ...)) * nu_costfn + ... =E= 0;
stat_p(i).. ... + ((-1) * sum((i,cg), ...)) * nu_costfn + ... =E= 0;
costfn.. cost =E= sum((i,cg), gendata(i,cg) * power(p(i), pexp(cg)));
```

### Actual Output

```gams
stat_cost.. 100 * sum(i, 0) / 10000 + 100 * sum((i,j), 0) / 10000 + (1 - sum((i,cg), 0)) * nu_costfn + ...
stat_p(i).. 100 * b0(i) / 10000 + 100 * sum((i,j), 0) / 10000 + ((-1) * sum((i,cg), 0)) * nu_costfn + ...
****                                                $125                            $125
costfn.. cost =E= sum((i,cg), gendata(i,"cg") * power(p(i), pexp("cg")));
****                                             $170                     $170
```

### GAMS Errors

```
**** 125  Set is under control already
**** 170  Domain violation for element
```

## Root Cause Analysis

The bug occurs during KKT stationarity equation generation. When computing partial derivatives of expressions like `sum((i,cg), gendata(i,cg)*...)`:

1. The derivative computation correctly identifies the summation domain `(i,cg)`
2. When emitting the derivative expression, the set index `cg` is being treated as a string literal `"cg"` instead of a set reference

### Likely Location

- `src/kkt/` - KKT system generation
- `src/diff/` - Differentiation code that builds derivative expressions
- `src/emit/expr_to_gams.py` - Expression emission handling of set references

### Investigation Notes

1. Error 125 "Set is under control already" suggests `cg` is being used incorrectly in the summation domain
2. Error 170 "Domain violation for element" confirms `"cg"` is being treated as a literal string element, not a set index
3. The bug may be in how `SymbolRef` or similar AST nodes are constructed during differentiation
4. Compare with working models to see how set indices are preserved through differentiation

## Proposed Fix

1. **Identify where set indices become strings**: Trace how `cg` in `gendata(i,cg)` gets transformed to `"cg"` during KKT generation

2. **Preserve set reference type**: Ensure that when building derivative expressions, set indices remain as `SymbolRef` nodes (or equivalent) rather than being converted to string constants

3. **Check differentiation rules**: The chain rule application for `sum((i,cg), f(i,cg))` needs to preserve that `cg` is a domain variable, not a constant

## Impact

- **dispatch** model fails to compile
- Any model with set-indexed parameters in objective/constraints will be affected
- Common pattern: `sum((i,j), param(i,j) * var(i))` where derivative w.r.t. var involves `param(i,j)`

## Related Files

- `src/kkt/stationarity.py` (or similar) - Stationarity equation generation
- `src/diff/differentiate.py` (or similar) - Differentiation rules
- `src/emit/expr_to_gams.py` - Expression emission
- `src/ir/ast.py` - AST node types (SymbolRef, ParamRef, etc.)
- `data/gamslib/raw/dispatch.gms` - Test case
- `data/gamslib/mcp/dispatch_mcp.gms` - Generated output showing bug

## Test Case

After fixing, verify:
1. `dispatch_mcp.gms` compiles without GAMS errors
2. The stationarity equations correctly reference `gendata(i,cg)` not `gendata(i,"cg")`
3. The MCP solves successfully
