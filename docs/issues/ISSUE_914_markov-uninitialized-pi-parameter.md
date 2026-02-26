# markov: Uninitialized Parameter `pi` ($66)

**GitHub Issue:** [#914](https://github.com/jeffreyhorn/nlp2mcp/issues/914)
**Model:** markov (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $66 Symbol has no values assigned, $256 Solve error

## Problem

The generated MCP file declares parameter `pi(s,i,sp,j,spp)` but never assigns it values. The stationarity equation `stat_z` references `pi`, causing GAMS error $66:

```
**** 66  Use of a symbol that has not been defined or assigned
****  66 equation stat_z.. symbol "pi" has no values assigned
```

## Error Output

```
**** 66  Use of a symbol that has not been defined or assigned
**** 256  Error(s) in analyzing solve statement
```

2 compilation errors.

## Root Cause

In the original markov.gms, `pi` is a **computed parameter** assigned via:

```gams
pi(s,i,sp,j,sp) = pr(i,j);
```

This assignment populates `pi` from the transition probability matrix `pr(i,j)`. However, the MCP emitter fails to include this assignment in the generated file. The parameter is declared but the computed assignment is missing.

Possible reasons:
1. The assignment has overlapping index names (`sp` appears twice: as 3rd and 5th index), which may confuse the parser or expression storage
2. The assignment may be dropped during the computed parameter emission pass

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/markov.gms -o /tmp/markov_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/markov_mcp.gms o=/tmp/markov_mcp.lst
grep '^\*\*\*\*' /tmp/markov_mcp.lst
```

## Suggested Fix

1. Investigate why the `pi(s,i,sp,j,sp) = pr(i,j)` assignment is not captured or emitted
2. Check if the repeated index name `sp` in positions 3 and 5 causes the parser to drop the assignment
3. Ensure computed parameter assignments with repeated index names are correctly stored and emitted

## Impact

2 compilation errors. Model cannot compile. The `pi` parameter is essential for the Markov chain transition structure.
