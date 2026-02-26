# qdemo7: Empty MCP Equations for Conditionally-Absent Variables

**GitHub Issue:** [#918](https://github.com/jeffreyhorn/nlp2mcp/issues/918)
**Model:** qdemo7 (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Execution — MCP pair empty equation, variable NOT fixed

## Problem

The generated MCP file creates stationarity equations for `exports(c)` and `imports(c)` that are empty (`0 =E= 0`) because these variables only appear in constraints conditionally (via `$ce(c)` and `$cm(c)`). For indices where `ce(c)` or `cm(c)` is false, the variables have no gradient terms, yet are not fixed:

```gams
stat_exports(c).. 0 =E= 0;
stat_imports(c).. 0 =E= 0;
```

GAMS runtime error: "MCP pair stat_exports.exports has empty equation but associated variable is NOT fixed."

## Error Output

```
**** MCP pair stat_exports.exports has empty equation but associated variable is NOT fixed
**** MCP pair stat_imports.imports has empty equation but associated variable is NOT fixed
```

15 execution errors (7 for exports + 7 for imports + 1 SOLVE aborted). 0 compilation errors.

## Root Cause

The original qdemo7.gms uses conditional references in the demand balance equation:

```gams
dem(cn).. natcon(cn) =e= natprod(cn) + imports(cn)$cm(cn) - exports(cn)$ce(cn);
```

For crops where `ce(c) = 0` (not an export crop), `exports(c)` doesn't appear in any constraint. The KKT stationarity equation for `exports(c)` is therefore `0 =E= 0` — but the variable is still free (not fixed), violating MCP requirements.

The fix already exists for `natcon` (line 222 in qdemo7_mcp.gms):
```gams
natcon.fx(c)$(not (cn(c))) = 0;
```

But equivalent fixes for `exports` and `imports` are missing.

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/qdemo7.gms -o /tmp/qdemo7_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/qdemo7_mcp.gms o=/tmp/qdemo7_mcp.lst
grep 'MCP pair' /tmp/qdemo7_mcp.lst | head -5
```

## Suggested Fix

When a variable's stationarity equation is empty (all gradient terms are zero due to dollar conditions), the KKT generator should fix the variable for those inactive indices:

```gams
exports.fx(c)$(not ce(c)) = 0;
imports.fx(c)$(not cm(c)) = 0;
```

This requires the KKT generator to:
1. Detect when stationarity equations resolve to `0 =E= 0` for specific index subsets
2. Identify the conditioning sets (e.g., `ce`, `cm`) that make the variable inactive
3. Emit `.fx` statements fixing the variable for the complementary subset

## Impact

15 execution errors. Model compiles cleanly but SOLVE aborts.
