# Worst: Table Data Not Emitted for `f0` and `pdata` Parameters

**GitHub Issue:** [#863](https://github.com/jeffreyhorn/nlp2mcp/issues/863)
**Status:** RESOLVED
**Severity:** Medium — Model translates but GAMS compilation fails (path_syntax_error)
**Date:** 2026-02-24
**Resolved:** 2026-02-25
**Affected Models:** worst

---

## Problem Summary

The worst model parses and translates to MCP, but the emitted GAMS code fails compilation
with 6 errors. The emitter correctly emits the `tdata` table with inline data, but declares
`f0(i,t)` and `pdata(i,t,j,*)` as empty parameters with no data. Variables initialized from
these empty parameters then trigger GAMS $141 errors.

---

## Resolution

Two distinct bugs in the table parser were fixed:

### Bug 1: Numeric Row Labels Misidentified as Secondary Column Headers (f0)

The `f0` table has numeric row labels (`9000011`, `9020063`). The secondary column-header
detection (ISSUE_392) checked for lines where ALL tokens are NUMBER type, but didn't
distinguish between:
- Numeric data rows starting at the left margin (col 4)
- Secondary column headers aligned with existing column headers (col 18+)

**Fix:** Added column-position check to secondary header detection: only flag all-NUMBER
lines as secondary headers if the first token's column position is >= `first_header_col - 3`
(with small tolerance for `+` replacement shift). Numeric data rows at the left margin
(col 4 << col 18) are correctly excluded.

### Bug 2: Dotted Row Labels Split by Earley Parser (pdata)

The `pdata` table has dotted row labels like `'9000011'.jun.'1'`. The Earley parser splits
these into multiple `table_row` nodes per physical line, causing data values (e.g. `future`,
`-35000`, `96.60`) to be misidentified as row labels. Three sub-issues were fixed:

1. **Grammar**: Added `NUMBER` to the `dotted_label` rule to allow numeric row labels.

2. **Preprocessor**: Added `quote_suffix_numeric` to convert `.1` → `.'1'` in table data
   lines, preventing the lexer from consuming `.1` as a fractional number.

3. **IR builder** (three changes):
   - **Leftmost-wins**: When multiple `table_row` nodes share the same line, keep only the
     leftmost label (the real row label) in `row_label_map`.
   - **False label cleanup**: After column headers are established, remove `row_label_map`
     entries whose first token column >= `min_col_header_col` and un-mark their tokens from
     `row_label_token_ids` so they are treated as values.
   - **Row header fill-in**: Changed the `all_row_headers` collection for zero-fill to use
     `row_label_map` entries instead of raw `line_tokens[0]`, preventing bare `9000011`
     ghost entries.

**Result:** `f0` emits 6 values, `pdata` emits 52 values — all numerically correct.
String-valued columns (`type` = `future`/`call`/`puto`) emit as 0.0, which is a pre-existing
limitation of the float-only parameter storage.

---

## Files Changed

| File | Change |
|------|--------|
| `src/gams/gams_grammar.lark` | Added NUMBER to `dotted_label` rule |
| `src/ir/preprocessor.py` | Added `quote_suffix_numeric` for `.NUM` → `.'NUM'` in table data |
| `src/ir/parser.py` | Leftmost-wins row label, false label cleanup, row header fill-in, secondary header tolerance |

---

## Related Issues

- **Issue #809** (completed): Previous worst parse blocker (equation negative in function arg)
- Sprint 21 SEMANTIC_ERROR_AUDIT section 2.6 documents the acronym handling fix
