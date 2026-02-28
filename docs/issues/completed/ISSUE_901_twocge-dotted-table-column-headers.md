# twocge: 3-Dimensional Table with Dotted Column Headers Loses All Data

**GitHub Issue:** [#901](https://github.com/jeffreyhorn/nlp2mcp/issues/901)
**Status:** RESOLVED
**Model:** twocge (GAMSlib)
**Original error category:** `path_syntax_error`
**Original GAMS error:** `$141` — Symbol declared but no values have been assigned

## Description

The `twocge` model defines a 3-dimensional table `SAM(u,v,r)` where column headers
use dotted notation (e.g., `BRD.JPN`) to encode two dimensions. The parser previously
extracted each dotted segment as a separate column header instead of merging them
into compound headers.

## Root Cause

In `src/ir/parser.py`, `_handle_table_block()` extracted column headers by iterating
individual tokens. The Lark grammar produced separate `ID` tokens for each segment
(`BRD`, `JPN`) with a `DOT` token between them. The column header loop treated each
segment as a separate header instead of recognizing that consecutive tokens connected
by dots form a single compound header.

## Fix (RESOLVED)

Fixed in Sprint 21 Day 7 (commit 7f87431e) by adding `_merge_dotted_col_headers()`
helper in `src/ir/parser.py`. This function detects adjacent tokens separated by
dots in the source text and merges them into compound column headers. Applied to
both the standard column header path and the section-based (`+` continuation) path.

**Verification:**
- SAM now has 50 entries with 2-tuple keys `('BRD', 'BRD.JPN')` which
  `_expand_table_key()` correctly expands to 3-tuples `('BRD', 'BRD', 'JPN')`
  matching domain `(u,v,r)`
- No `$141` compilation errors remain
- Model still has 28 runtime execution errors (division by zero / rPower domain)
  from parameter calculations with zero-valued SAM entries — this is a separate
  issue unrelated to table parsing

**Tests:** `tests/unit/ir/test_table_parsing.py`

## GAMS Source Context (lines 23–50)

```gams
Table SAM(u,v,r) 'social accounting matrix'
         BRD.JPN MLK.JPN CAP.JPN LAB.JPN IDT.JPN
   BRD        21      8
   MLK        17      9
   CAP                        80      45
   LAB                        20      55
   IDT         3      3
   TRF
   HOH                       100     100       6
   GOV                                        15
   INV                                        -2
   EXT         7     11

   +     TRF.JPN HOH.JPN GOV.JPN INV.JPN EXT.JPN
   BRD                20      19      16       8
   MLK                 4       2       7       3
   ...
```

## Related Issues

- [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886) — tfordy: same dotted column header pattern
