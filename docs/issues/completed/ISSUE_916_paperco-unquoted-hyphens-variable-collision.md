# paperco: Unquoted Hyphenated Elements + Variable Name Collision

**GitHub Issue:** [#916](https://github.com/jeffreyhorn/nlp2mcp/issues/916)
**Model:** paperco (GAMSlib)
**Sprint:** 21 Day 8
**Error Category:** Compilation — $120/$171/$340 (unquoted elements), $195/$318 (variable redefinition), $322 (wrong MCP pair)
**Status:** RESOLVED

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
- Variable `pulp(p)` -- a legitimate variable name

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

## Fix

Fixed in `_quote_assignment_index()` in `src/emit/original_symbols.py`:

1. Added `_needs_quoting()` check to detect elements containing operators (`-`, `+`)
   or other special characters that GAMS would interpret as arithmetic.

2. Added `domain_lower` parameter to distinguish domain variables from literal
   element values. Non-domain elements are quoted as literals.

3. In `emit_subset_value_assignments()`, mixed-key entries (some set names, some
   not) use the parameter's domain to determine quoting.

After fix: `psdat('scenario-2','pulp-1',p) = 5;` -- all 18 errors eliminated.
Only 2 remaining errors ($66 symbol `pp` not defined, $256 cascading) are
unrelated to quoting.

## Impact

18 -> 2 compilation errors (all remaining are unrelated to quoting).
