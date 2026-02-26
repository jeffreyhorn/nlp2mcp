# marco: Duplicate Element in Parameter Data ($172)

**GitHub Issue:** [#913](https://github.com/jeffreyhorn/nlp2mcp/issues/913)
**Model:** marco (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $172 Element is redefined

## Problem

The generated MCP file declares parameter `qs(lim,cf,q)` with a duplicate entry for `upper.'fuel-oil'.sulfur`:

```gams
qs(lim,cf,q) /
    lower.premium.octane 90, ...,
    upper.'fuel-oil'.sulfur 3.5,
    ...,
    upper.'fuel-oil'.sulfur 3.4
/
```

GAMS error $172: "Element is redefined" — the same key `(upper, fuel-oil, sulfur)` appears twice with different values (3.5 and 3.4).

## Error Output

```
**** 172  Element is redefined
```

4 compilation errors (1 primary $172 + downstream $257, $141 errors).

## Root Cause

The original marco.gms defines `qs` as a TABLE:

```gams
Table qs(lim,cf,q) 'specs of crude quality'
              octane  vapor-pres  sulfur
lower.premium    90      .        .
...
upper.'fuel-oil'  .      .       3.5 ;
```

The table has a single value for `upper.'fuel-oil'.sulfur` = 3.5. However, the emitter is producing two entries, likely because:
1. The table data is parsed with value 3.5
2. A computed assignment or second parsing pass adds the value 3.4
3. Both get emitted as static data

The parser or emitter may be merging values from different sources (table data + inline data) without deduplication.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/marco.gms -o /tmp/marco_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/marco_mcp.gms o=/tmp/marco_mcp.lst
grep '172' /tmp/marco_mcp.lst
```

## Suggested Fix

1. Investigate where the duplicate value originates — check if `qs` gets both table values AND inline/computed values
2. Add deduplication in `emit_original_parameters()` or the table data merging logic to prevent emitting the same key twice
3. If both values exist in the IR, last-write-wins should apply (matching GAMS semantics)

## Impact

4 compilation errors. Model cannot compile.
