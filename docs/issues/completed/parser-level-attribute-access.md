# Parser: Level Attribute `.l` Access Not Supported

## GitHub Issue
- **Issue #:** 432
- **URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/432

## Summary
The parser does not support accessing variable level attributes (`.l`) for reading solution values in assignment statements.

## Affected Model
- **chenery.gms** (Tier 2) - Substitution and Structural Change

## Error
```
Error: Parse error at line 199, column 1: Unexpected character: 'l'
  l.l(i) = (((del(i)/vv.l(i) + (1 - del(i)))**(1/rho(i)))$(sig(i) <> 0)
  ^
```

## Root Cause
The grammar supports `.lo`, `.up`, `.fx`, `.l`, `.m` as bound/attribute setters on the left-hand side of assignments (via `BOUND_K`), but does not support reading `.l` (level) values on the right-hand side of expressions.

## GAMS Code Pattern
```gams
h.l(t) = gam(t) - alp(t)*e.l(t);
pd.l   = 0.3;
p.l(i) = 3;
pk.l   = 3.5;
pi.l   = pk.l/plab;

vv.l(i)$sig(i) = (pi.l*(1 - del(i))/del(i))**(-rho(i)/(1 + rho(i)));

l.l(i) = (((del(i)/vv.l(i) + (1 - del(i)))**(1/rho(i)))$(sig(i) <> 0)
         + 1$(sig(i) = 0))/efy(i);
```

The `.l` suffix is used both:
1. On the LHS to set initial level values
2. On the RHS to read current level values (e.g., `vv.l(i)` in the expression)

## Suggested Fix
Extend `ref_bound` or add a new rule to allow `.l` attribute access in expressions:

1. Current `ref_bound` handles LHS: `ID "." BOUND_K "(" index_list ")"`
2. Need to allow `ID "." BOUND_K` in `atom` rule for RHS expressions

## Complexity
Medium - grammar already has `BOUND_K` pattern, need to allow it in expression context.

## Test Case
```gams
Variable x;
x.l = 5;
Parameter p;
p = x.l * 2;
```

Expected: `p = 10`
