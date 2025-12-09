# Parser: Unquoted Parameter Descriptions Not Supported

## GitHub Issue
- **Issue #:** 433
- **URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/433

## Summary
The parser does not support unquoted text descriptions after parameter declarations.

## Affected Model
- **gasoil.gms** (Tier 2) - Catalytic Cracking of Gas Oil (via `copspart.inc` include file)

## Error
```
Error: Parse error at line 96, column 1: Unexpected character: 'r'
  rho(nc) roots of k-th degree Legendre polynomial
  ^
```

## Root Cause
The grammar expects parameter descriptions to be quoted strings, but GAMS allows unquoted descriptions after the parameter name/domain declaration.

## GAMS Code Pattern (from copspart.inc)
```gams
Parameter t(nh)   partition
          rho(nc) roots of k-th degree Legendre polynomial
          itau(nm) "itau[i] is the largest integer k with t[k] <= tau[i]";
```

Here:
- `partition` is an unquoted description for `t(nh)`
- `roots of k-th degree Legendre polynomial` is an unquoted description for `rho(nc)`
- The third parameter uses a quoted description (which works)

## Current Grammar
```lark
param_single_item: ID "(" id_or_wildcard_list ")" (STRING | desc_text)? ...
```

The `desc_text` pattern may not be matching multi-word unquoted descriptions correctly in parameter context.

## Suggested Fix
Ensure `desc_text` or a similar pattern captures unquoted multi-word descriptions in parameter declarations, similar to how it works for variables and sets.

## Complexity
Low - grammar already has `desc_text` pattern for other declarations, may need adjustment for parameter context.

## Test Case
```gams
Parameter
   x(i)   cost coefficient
   y(j)   demand level;
```

Expected: Both parameters parsed with their unquoted descriptions.
