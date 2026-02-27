# lmp2: Unquoted Set Element Indices in Parameter Assignments ($120/$340)

**GitHub Issue:** [#912](https://github.com/jeffreyhorn/nlp2mcp/issues/912)
**Model:** lmp2 (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $120 Unknown identifier, $340 Label/element name conflict, $171 Domain violation, $352 Set not initialized
**Status:** RESOLVED

## Problem

The generated MCP file emits parameter assignments with bare (unquoted) set element names that clash with declared set identifiers:

```gams
cases(c1,m) = 10;
cases(c1,n) = 20;
cases(c2,m) = 20;
```

GAMS interprets `c1` as an unquoted identifier that could be a set reference, but `c1` is actually a **set element** of set `c`. Similarly, `m` is both a set element label AND a declared set `m(mm)`, causing $340 (name clash) and $120 (unknown identifier as set) errors.

## Error Output

```
**** 120  Unknown identifier entered as set
**** 340  A label/element with the same name exist. You may have forgotten
****         to quote a label/element reference.
**** 171  Domain violation for set
**** 352  Set has not been initialized
```

34 compilation errors across 10 assignment lines.

## Root Cause

The original lmp2.gms declares:

```gams
Set mm / m1*m200 /
    nn / n1*n200 /
    m(mm) 'constraints'
    n(nn) 'variables'
    c / c1*c5 /;
```

Then assigns:
```gams
cases('c1','m') = 10;
cases('c1','n') = 20;
```

The original uses **quoted** element references `'c1'` and `'m'` to disambiguate from the set names `c` and `m`. The emitter strips these quotes, causing GAMS to misinterpret the bare identifiers.

## Fix

Fixed in `_quote_assignment_index()` in `src/emit/original_symbols.py`:

1. Added `domain_lower` parameter: the parameter's declared domain set names.
   Only indices matching domain sets are treated as domain variables; all others
   are quoted as literal elements.

2. In `emit_subset_value_assignments()`, when a key has mixed set/non-set flags,
   the parameter's domain is used to distinguish domain variables from literal
   elements that collide with set names.

3. In `emit_computed_parameter_assignments()`, `param_domain_lower` is passed
   to ensure non-domain indices are properly quoted.

After fix: `cases('c1','m') = 10;` — all 34 $120/$340/$171/$352 errors eliminated.
3 remaining errors ($141/$257) are unrelated MCP emission issues.

## Impact

34 → 3 compilation errors (all remaining are unrelated to quoting).
