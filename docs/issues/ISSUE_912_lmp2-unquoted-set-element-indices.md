# lmp2: Unquoted Set Element Indices in Parameter Assignments ($120/$340)

**GitHub Issue:** [#912](https://github.com/jeffreyhorn/nlp2mcp/issues/912)
**Model:** lmp2 (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $120 Unknown identifier, $340 Label/element name conflict, $171 Domain violation, $352 Set not initialized

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

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/lmp2.gms -o /tmp/lmp2_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/lmp2_mcp.gms o=/tmp/lmp2_mcp.lst
grep '^\*\*\*\*' /tmp/lmp2_mcp.lst | head -10
```

## Suggested Fix

The `_quote_assignment_index()` function in `src/emit/original_symbols.py` should preserve quotes for literal set element values in parameter assignments, especially when the element name matches a declared set name. If an element like `m` is also a declared set, it MUST be quoted as `'m'` in the assignment context.

## Impact

34 compilation errors. Model cannot compile.
