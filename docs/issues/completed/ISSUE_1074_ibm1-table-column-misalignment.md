# ibm1: Objective Mismatch — Table Column Misalignment in Sparse Rows

**GitHub Issue:** [#1074](https://github.com/jeffreyhorn/nlp2mcp/issues/1074)
**Model:** ibm1 (SEQ=155) — Aluminum Alloy Smelter Sample Problem
**Type:** LP
**Category:** Parser bug (table column alignment)
**Status:** FIXED

---

## Summary

The ibm1 model solves successfully (model_status=1) but has a large objective mismatch: MCP obj=80.0 vs NLP ref=287.1357 (72.1% relative error). The root cause is a table parsing bug where sparse rows with missing middle columns have values assigned to the wrong columns.

## Root Cause

The GAMS `Table sup(s,*)` has three columns (`inventory`, `min-use`, `cost`). For rows where the middle column `min-use` is blank, the parser assigns the `cost` value to `min-use` instead:

**Original GAMS table:**
```gams
Table sup(s,*) 'supply and cost data'
                inventory  min-use   cost
   bin-1              200             .03
   bin-2              750             .08
   ...
   aluminum           inf             .21
   silicon            inf             .38;
```

**Parsed result (in MCP file) — before fix:**
```gams
sup(s,*) /..., aluminum.inventory inf, aluminum.'min-use' 0.21,
               silicon.inventory inf, silicon.'min-use' 0.38/
```

**Expected:**
- `aluminum`: inventory=inf, min-use=0 (blank), cost=0.21
- `silicon`: inventory=inf, min-use=0 (blank), cost=0.38

**Actual (buggy):**
- `aluminum`: inventory=inf, min-use=0.21, cost=0 (missing)
- `silicon`: inventory=inf, min-use=0.38, cost=0 (missing)

Since the objective is `cost = sum(s, sup(s,"cost")*x(s))`, the missing cost coefficients for aluminum and silicon cause a completely wrong objective value.

## Bug Location

**File:** `src/ir/parser.py`, function `_handle_table_block()`

The range-based column matching defined column boundaries as `[col_pos - tolerance, next_col_pos)` where `next_col_pos` is the start position of the next column header. This boundary is too far right: a value right-aligned near the next column header's start position gets incorrectly assigned to the current column.

For example, with headers `inventory`(col 17), `min-use`(col 28), `cost`(col 40):
- `min-use` range was `[25, 40)` — extending right up to `cost`'s start
- `.21` at col 39 fell in `min-use`'s range (39 < 40), not `cost`'s

## Fix

Replaced the range-based column matching (both section-based and non-section paths) with **gap-midpoint range matching**. Each column now owns from the midpoint of the gap to its left (between the previous header's right edge and this header's left edge) to the midpoint of the gap to its right.

For headers `inventory`(17, len=9), `min-use`(28, len=7), `cost`(40, len=4):
- `inventory` right edge = 26, gap midpoint to `min-use` = (26+28)/2 = 27
- `min-use` right edge = 35, gap midpoint to `cost` = (35+40)/2 = 37.5
- Ranges: `inventory` [14, 27), `min-use` [27, 37.5), `cost` [37.5, ∞)

Now `.21` at col 39 correctly falls in `cost`'s range [37.5, ∞).

A distance-based fallback is retained for values outside all ranges (e.g., far left of the first header).

## Verification

After fix:
- ibm1 table `sup` parsed correctly: `aluminum.cost=0.21`, `silicon.cost=0.38`
- MODEL STATUS: 1 (Optimal)
- MCP objective: 287.105 (vs NLP ref 287.1357, 0.01% difference — solver tolerance)
- All 4170 tests pass, no regressions

## Files Modified

- `src/ir/parser.py` — `_handle_table_block()`: replaced range-based matching with gap-midpoint matching in both section-based and non-section paths
