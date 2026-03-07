# paklive: Scalar-Unrolled Stationarity Equations Paired with Indexed Variable

**GitHub Issue:** [#1008](https://github.com/jeffreyhorn/nlp2mcp/issues/1008)
**Model:** paklive (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform

## Description

The `paklive` model has an indexed variable `xcrop(c)` with 10 elements (wheat, basrice, irrrice, maize, oilseed, gram, cotton, sugar, berseem, kharfodder). The variable has a single per-element upper bound: `xcrop.up("sugar") = 2`.

The MCP emitter creates 10 scalar stationarity equations (`stat_xcrop_wheat`, `stat_xcrop_basrice`, ...) instead of one indexed equation `stat_xcrop(c)`. Each scalar equation is then paired with the indexed variable `xcrop(c)` in the MCP model statement, producing 9 instances of GAMS Error $70 (dimension mismatch).

This is the same root cause as issue #903 (launch model).

## Reproduction

```bash
# Translate and compile:
.venv/bin/python -m src.cli data/gamslib/raw/paklive.gms -o /tmp/paklive_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams \
    /tmp/paklive_mcp.gms lo=3 o=/tmp/paklive_mcp.lst

# Check errors:
grep '\$70' /tmp/paklive_mcp.lst
```

Output:
```
****                           $70,256
 70 xcrop dimensions are different  (× 9)
```

## Emitted MCP Pairing (paklive_mcp.gms)

```gams
* Variable declaration:
Positive Variables
    xcrop(c)    'cropping activities (acres)'

* 10 scalar stationarity equations (lines 141-150):
Equations
    stat_xcrop_basrice
    stat_xcrop_berseem
    stat_xcrop_cotton
    ...

* MCP pairings (lines 258-267):
Model mcp_model /
    stat_xcrop_basrice.xcrop,    * 0-dim eq paired with 1-dim var → $70
    stat_xcrop_berseem.xcrop,
    ...
/;
```

## Expected Output

```gams
* Single indexed stationarity equation:
Equations
    stat_xcrop(c)

* Single indexed MCP pairing:
Model mcp_model /
    stat_xcrop.xcrop,    * both 1-dim → OK
    ...
/;
```

## Root Cause

Same as #903: the MCP emitter unrolls stationarity equations to per-element scalars when any per-element bound exists (here `xcrop.up("sugar") = 2`), but pairs them with the original indexed variable. Fix approach: keep the stationarity equation indexed and encode per-element bounds via indexed parameters.

## Related Issues

- #903 — Same root cause (launch model: scalar-indexed MCP pairing mismatch)
