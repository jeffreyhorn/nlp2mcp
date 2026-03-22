# fawley: Table Column Alignment Bug — Section-Based Path Missing Continuation Offsets

**GitHub Issue:** [#1130](https://github.com/jeffreyhorn/nlp2mcp/issues/1130)
**Status:** FIXED
**Severity:** High — model generates MCP but GAMS aborts with EXECERROR=1 (UNDF propagation)
**Date:** 2026-03-22
**Fixed:** 2026-03-22
**Affected Models:** fawley (and potentially any model with continuation tables + secondary headers)

---

## Problem Summary

The fawley model (`data/gamslib/raw/fawley.gms`) generates an MCP file, but the `ap(c,p)`
parameter table has incorrect column assignments. Specifically, `brega.'d-brega' = -1` in
the original is emitted as `brega.'d-arab-h' = -1` — the value is assigned to the wrong
column. This causes a division-by-zero cascade:

1. `bp(k,p)$(kuse(k,p)) = 1 / sum(c$(ap(c,p) < 0), ...)` — the `sum` evaluates to 0
   for `(pipestill, d-brega)` because no crude has `ap(c, d-brega) < 0` (the brega entry
   was misplaced to `d-arab-h`)
2. `bp(pipestill, d-brega)` becomes UNDF
3. UNDF propagates into `kbal(pipestill)` and `stat_z(d-brega)` equations
4. GAMS aborts the SOLVE with `EXECERROR = 1`

---

## Root Cause

### The Original Table

In fawley.gms, the `ap(c,p)` table uses continuation lines (the `+` character):

```gams
Table ap(c,p)  'process yields  (proportion weight of crude feed)'
               d-arab-l  d-arab-h  d-brega   reform   ho-low-s   ...

   arabian-l     -1.0
   arabian-h               -1.0
   brega                            -1.0
   ...

+              ho-high-s  vd-low-s  vd-high-s
   ...
```

The `brega` row has `-1.0` positioned under the third column `d-brega`.

### The Bug: Three Issues in the Section-Based Path

The table has both a continuation (`+`) and secondary column headers, triggering the
**section-based processing path** in `_handle_table_block()`. Three bugs were found:

**1. Continuation tokens leaked into section 0 headers**

When the preprocessor removes `+` continuation markers and merges continuation line tokens
into the first header line, section 0 sees ALL column headers (including those from
continuation sections). This gives section 0 eight column headers instead of three,
distorting the gap-midpoint column ranges.

**2. `continuation_col_offsets` not passed to `_merge_dotted_col_headers()`**

The section-based path did not pass `continuation_col_offsets` to `_merge_dotted_col_headers()`,
unlike the non-section path which did.

**3. `continuation_col_offsets` not applied to data value positions**

Data value tokens from continuation lines were not having their column offsets adjusted
in the section-based path, unlike the non-section path.

### Consequence

The `-1.0` value in the `brega` row at column 37 fell into the gap-midpoint range of
`d-arab-h` instead of `d-brega` because the extra continuation tokens distorted the
column boundary calculations. Additionally, the token center matching approach was needed
in the section-based path to correctly match right-aligned values near column boundaries.

---

## Fix Applied

Three changes to `src/ir/parser.py` in the section-based path of `_handle_table_block()`:

1. **Filter continuation tokens from section 0 headers** (~line 2548-2554):
   When processing section 0, exclude any tokens whose `id()` appears in
   `continuation_col_offsets` — these belong to later continuation sections.

2. **Pass `continuation_col_offsets` to `_merge_dotted_col_headers()`** (~line 2558):
   Added the missing `continuation_col_offsets=continuation_col_offsets` parameter.

3. **Apply continuation offsets + token center matching in section-based data rows**
   (~line 2600-2607):
   - Apply `continuation_col_offsets` to data value positions (same as non-section path).
   - Use token center (`val_col += len(str(val_tok)) / 2`) for gap-midpoint matching
     so that right-aligned values (e.g., `-1.0` spanning cols 37-40 under a header
     at col 39) are correctly matched.
   - Use exclusive right boundary (`<` instead of `<=`) to break ties in favor of
     the right column.

Note: The token center and exclusive right boundary changes were applied ONLY to the
section-based path, not the non-section path, to avoid regressions with closely-spaced
columns in simpler tables.

---

## Verification

```bash
python -m src.cli data/gamslib/raw/fawley.gms -o /tmp/fawley_mcp.gms
grep "brega\.'d-" /tmp/fawley_mcp.gms
# Output: brega.'d-brega' -1  ← CORRECT
```

Full test suite: 4,222 passed, 10 skipped, 1 xfailed.

---

## Files Modified

| File | Line | Change |
|------|------|--------|
| `src/ir/parser.py` | ~2548-2554 | Filter continuation tokens from section 0 headers |
| `src/ir/parser.py` | ~2558 | Pass `continuation_col_offsets` to `_merge_dotted_col_headers` |
| `src/ir/parser.py` | ~2600-2628 | Apply continuation offsets + token center + exclusive right boundary in section-based data matching |
