# paperco: Unquoted Hyphenated Elements + Variable Name Collision

**GitHub Issue:** [#916](https://github.com/jeffreyhorn/nlp2mcp/issues/916)
**Model:** paperco (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $120/$171/$340 (unquoted elements), $195/$318 (variable redefinition), $322 (wrong MCP pair)

## Problem

The generated MCP file has multiple compilation errors from two distinct root causes:

### Issue 1: Unquoted hyphenated set element references

Parameter assignments emit bare hyphenated identifiers:

```gams
psdat(scenario-2,pulp-1,p) = 5;
```

GAMS interprets `scenario-2` as `scenario` minus `2` (subtraction), not as the set element `'scenario-2'`. The original uses quoted references: `psdat('scenario-2','pulp-1',p)`.

### Issue 2: Variable name collision with `pulp`

The original model has both:
- Set `p` with elements including `pulp-1`, `pulp-2`
- Variable `pulp(p)` — a legitimate variable name

The MCP generation creates `piL_pulp(p)` (lower bound multiplier) and pairs `comp_lo_pulp.piL_pulp`, which may conflict with the set element naming.

## Error Output

```
**** 120  Unknown identifier entered as set
**** 171  Domain violation for set
**** 340  A label/element with the same name exist
**** 195  Symbol redefined with a different type
**** 318  Domain list redefined
**** 322  Wrong complementarity pair
```

18 total compilation errors.

## Root Cause

1. **Unquoted hyphens**: The `_quote_assignment_index()` function in `src/emit/original_symbols.py` does not detect that hyphenated elements like `scenario-2` or `pulp-1` must be quoted. Without quotes, GAMS parses `scenario-2` as the expression `scenario - 2`.

2. **Variable redefinition**: The emitter may be re-declaring `pulp` in a way that conflicts with its original declaration, or the KKT multiplier naming collides with existing symbol names.

## Original GAMS

```gams
Set p 'pulp types'     / pulp-1, pulp-2 /
    scenario            / 'scenario-1', 'scenario-2', 'scenario-3' /;

Positive Variable pulp(p);

psdat('scenario-2','pulp-1',p) = 5;
```

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/paperco.gms -o /tmp/paperco_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/paperco_mcp.gms o=/tmp/paperco_mcp.lst
grep '^\*\*\*\*' /tmp/paperco_mcp.lst | head -10
```

## Suggested Fix

1. **Quote hyphenated elements**: Extend `_quote_assignment_index()` to detect and quote any element containing `-` that isn't a set name reference
2. **Preserve original quoting**: When the parser encounters quoted set elements in data/assignments, maintain the quotes through to emission
3. **Investigate variable collision**: Check if `pulp` variable redeclaration in the MCP file conflicts with an existing symbol

## Impact

18 compilation errors. Model cannot compile.
