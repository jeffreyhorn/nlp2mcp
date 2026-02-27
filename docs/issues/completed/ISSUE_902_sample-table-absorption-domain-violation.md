# sample: Table Data Absorption Bug Produces Domain Violation

**GitHub Issue:** [#902](https://github.com/jeffreyhorn/nlp2mcp/issues/902)
**Model:** sample (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$170` — Domain violation for element
**Subcategory:** B (Domain violation in emitted parameter data)
**Status:** RESOLVED

## Description

The `sample` model defines a table `data(h,*)` with numeric row labels (`1`, `2`, `3`, `4`) and data values starting before the first column header position. The Issue #863 absorption logic in the parser incorrectly treats the first data value (`400000`) as a split-off row label segment, producing the corrupted row label `1.400000` instead of `1`. When emitted, `'1.400000'` is not a member of set `h = /'1', '2', '3', '4'/`, triggering 4 instances of `$170`.

## Resolution

Fixed by adding a column-gap guard to the absorption logic in `src/ir/parser.py`.
Before absorbing a NUMBER token as a dotted-label segment, the code now checks that
the token is immediately adjacent to the preceding row label token (within 1 column).
Data values separated by whitespace (like `400000` at column 7 vs row label `1` ending
at column 4) are no longer absorbed.

After the fix, table keys are correctly parsed:
- Before: `('1.400000', 'pop'): 25.0` (corrupted)
- After: `('1', 'pop'): 400000.0` (correct)

## Files Modified

| File | Changes |
|------|---------|
| `src/ir/parser.py` | Added `row_label_end_col` tracking and adjacency check in absorption loop |

## Related Issues

- Issue #863 introduced the absorption logic that causes this bug
- [#827](https://github.com/jeffreyhorn/nlp2mcp/issues/827) — gtm: domain violation from zero-fill (related pattern)
