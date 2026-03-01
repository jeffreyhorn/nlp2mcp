# twocge: Table `+` Continuation Sections Overwrite Earlier Data

**GitHub Issue:** [#968](https://github.com/jeffreyhorn/nlp2mcp/issues/968)
**Status:** RESOLVED
**Model:** twocge (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 28)
**GAMS errors:** `division by zero` (26 instances), `rPower: FUNC DOMAIN: x**y, x=0,y<0` (2 instances)

## Description

The `twocge` model defines a 3-dimensional table `SAM(u,v,r)` with 4 `+` continuation
sections covering two regions (JPN and USA):

```gams
Table SAM(u,v,r) 'social accounting matrix'
         BRD.JPN MLK.JPN CAP.JPN LAB.JPN IDT.JPN
   BRD        21      8
   MLK        17      9
   ...

   +     TRF.JPN HOH.JPN GOV.JPN INV.JPN EXT.JPN
   BRD                20      19      16       8
   ...

   +     BRD.USA MLK.USA CAP.USA LAB.USA IDT.USA
   BRD        40       1
   MLK        17      29
   ...

   +     TRF.USA HOH.USA GOV.USA INV.USA EXT.USA
   BRD                30      20      20      13
   ...
```

The table parser only recognized the first section's column headers, causing USA data
to be stored under JPN keys and overwriting JPN values.

## Root Cause

The preprocessor's `normalize_table_continuations()` replaces `+` with a space, so the
grammar never produces `table_continuation` nodes. Continuation header lines with dotted
ID tokens (like `BRD.USA MLK.USA CAP.USA`) were treated as regular data rows.

The secondary header detection in `_handle_table_block()` (lines ~2358-2369) only detected
all-NUMBER lines as secondary headers. All-ID lines (like dotted column headers) were not
recognized, causing all data to be matched against the first section's JPN column headers.

## Fix Applied

In `src/ir/parser.py`, extended the secondary header detection in `_handle_table_block()`
to also detect all-ID/STRING lines positioned at or right of the primary column header
start position. Three changes:

1. **Extended secondary header detection**: Added an `elif` branch for all-ID/STRING lines
   with `len(line_tokens) >= 2` and `first_tok_col >= first_header_col`. Uses strict
   position check (no left tolerance) to avoid misclassifying data rows with ID-type
   values (e.g., `-inf`) as headers.

2. **False row label cleanup**: Added the same false-label cleanup logic from the
   non-section path (Issue #863) to the section-based path. This removes `row_label_map`
   entries for tokens positioned in the column header area, preventing data values
   from being treated as row labels.

3. **Range-based column matching**: Changed the section-based processing path from
   proximity-based to range-based column matching (consistent with the non-section path).
   Each column owns the range from its position to the next column's position, correctly
   handling right-aligned numbers under dotted headers.

**Result**: SAM table now correctly produces 60 entries (30 JPN + 30 USA) with correct
values: `BRD.BRD.JPN = 21`, `BRD.BRD.USA = 40`. All 28 EXECERROR errors are resolved
(0 exec errors after fix). The MCP now solves (SOLVER STATUS 1) but reports MODEL
STATUS 5 (Locally Infeasible) — see #970 for the remaining infeasibility issue.

## Related Issues

- [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901) — twocge dotted table column headers (RESOLVED)
- [#967](https://github.com/jeffreyhorn/nlp2mcp/issues/967) — twocge explicit zeros (RESOLVED — zero-filtering applied)
- [#970](https://github.com/jeffreyhorn/nlp2mcp/issues/970) — twocge MCP locally infeasible (OPEN)
