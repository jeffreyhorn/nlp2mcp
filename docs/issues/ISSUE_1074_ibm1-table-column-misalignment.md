# ibm1: Objective Mismatch — Table Column Misalignment in Sparse Rows

**GitHub Issue:** [#1074](https://github.com/jeffreyhorn/nlp2mcp/issues/1074)
**Model:** ibm1 (SEQ=155) — Aluminum Alloy Smelter Sample Problem
**Type:** LP
**Category:** Parser bug (table column alignment)

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

**Parsed result (in MCP file):**
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

**Lines 2758-2764** — Non-section table parsing fallback:
```python
# Fallback: if no range match (e.g., value is left of first header),
# assign to the next unused column sequentially to avoid data loss
if best_match is None:
    for col_name, _ in col_headers:
        if col_name not in used_columns:
            best_match = col_name
            break
```

When a value token doesn't fall within any column's position range (which happens when middle columns are blank and the value is at the position of a later column), the fallback assigns it to the **next unused column sequentially** rather than the **closest column by position**.

## Why It Fails

The range-based matching (lines 2732-2756) defines column ranges as `[col_pos - tolerance, next_col_pos)`. For the aluminum row:
- `inventory` range: roughly [16, 26)
- `min-use` range: roughly [26, 36)
- `cost` range: roughly [36, ∞)

The value `0.21` at column position ~36 should match `cost` (range [36, ∞)). However, the exact boundary condition `36 < 36` evaluates false (strict inequality), so the range check fails and falls through to the sequential fallback, which picks `min-use` (first unused column).

## Correct Pattern Already Exists

The **section-based path** (lines 2582-2597) for tables with continuation blocks (`+`) already has the correct distance-based fallback:

```python
if best_col_label is None and sec_col_headers:
    best_distance = math.inf
    best_idx: int | None = None
    for fidx, (col_label, col_pos) in enumerate(sec_col_headers):
        if col_label in used_sec_columns:
            continue
        distance = abs((col_pos or 0) - val_col)
        if (
            best_idx is None
            or distance < best_distance
            or (distance == best_distance and fidx < best_idx)
        ):
            best_distance = distance
            best_idx = fidx
    if best_idx is not None:
        best_col_label = sec_col_headers[best_idx][0]
```

This picks the **closest unused column by position**, which correctly maps `.21` at position 36 to the `cost` column header at position 36.

## Fix

Replace the sequential fallback (lines 2760-2764) in the non-section path with the distance-based fallback from the section-based path:

**Before:**
```python
if best_match is None:
    for col_name, _ in col_headers:
        if col_name not in used_columns:
            best_match = col_name
            break
```

**After:**
```python
if best_match is None and col_headers:
    best_distance = math.inf
    best_idx: int | None = None
    for fidx, (col_name, col_pos) in enumerate(col_headers):
        if col_name in used_columns:
            continue
        distance = abs((col_pos or 0) - token_col)
        if (
            best_idx is None
            or distance < best_distance
            or (distance == best_distance and fidx < best_idx)
        ):
            best_distance = distance
            best_idx = fidx
    if best_idx is not None:
        best_match = col_headers[best_idx][0]
```

## Impact

This bug affects any GAMS table with:
- 3+ columns
- Sparse rows where middle columns are blank
- Values that land exactly at or near the boundary between column ranges

Beyond ibm1, other models with sparse tables may have silent data corruption from this bug.

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ibm1.gms -o /tmp/ibm1_mcp.gms

# Check parsed sup parameter — look for aluminum.cost and silicon.cost
grep -E "aluminum|silicon" /tmp/ibm1_mcp.gms

# Run GAMS (if available)
cd /tmp && gams ibm1_mcp.gms lo=2
# MODEL STATUS 1 (Optimal), obj = 80.0 (should be 287.1357)
```

## Solution Comparison

| Metric | Value |
|--------|-------|
| NLP reference objective | 287.1357 |
| MCP objective | 80.0 |
| Absolute difference | 207.14 |
| Relative difference | 72.1% |
| MODEL STATUS | 1 (Optimal) |
| SOLVER STATUS | 1 (Normal Completion) |

## Files

- `data/gamslib/raw/ibm1.gms` — original LP model
- `data/gamslib/mcp/ibm1_mcp.gms` — generated MCP (with wrong `sup` values)
- `src/ir/parser.py` — `_handle_table_block()`, lines 2758-2764 (bug), lines 2582-2597 (correct pattern)
