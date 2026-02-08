# Parser Bug: Wildcard Tuple Domains Not Supported

**GitHub Issue:** [#400](https://github.com/jeffreyhorn/nlp2mcp/issues/400)  
**Status:** ✅ Fixed  
**Priority:** Low  
**Component:** Parser (Table Parsing)  
**Discovered:** 2025-12-03 (during Issue #392 testing)  
**Fixed:** 2025-12-03 (as side effect of PR #401 for Issue #399)

## Problem Description

The parser does not correctly handle table declarations with wildcard tuple domains like `(*,*)`. When a table is declared with this domain syntax, the parser produces no values in the resulting parameter definition.

## Example

```gams
Table data(*,*)
       col1  col2
row1   1     2;
```

**Expected behavior:**
- Table should be parsed with wildcard tuple domain
- Values should be stored: `(row1, col1) -> 1`, `(row1, col2) -> 2`

**Actual behavior:**
- Table parses without error
- Parameter `data` is created
- No values are stored: `model.params["data"].values == {}`

## Test Case

The following test case (from `tests/unit/gams/test_parser.py::TestTableContinuation::test_continuation_with_wildcard_domain`) demonstrates the issue:

```python
def test_continuation_with_wildcard_domain(self):
    """Test table continuation with wildcard tuple domain."""
    text = dedent("""
        Table data(*,*)
               col1  col2
           +   col3  col4
        row1   1     2     3     4;
    """)
    model = parser.parse_model_text(text)
    assert "data" in model.params
    # This assertion fails because no values are parsed
    assert model.params["data"].values[("row1", "col1")] == 1
```

## Current Grammar

The grammar defines table domains as:

```lark
table_domain_list: table_domain ("," table_domain)*
table_domain: ID                      -> explicit_domain
            | "*"                     -> wildcard_domain
            | "(" wildcard_tuple ")"  -> wildcard_tuple_domain
```

The grammar correctly recognizes `(*,*)` as a `wildcard_tuple_domain`, but the parser may not be handling this case properly.

## Root Cause

The issue likely stems from how `_handle_table_block` in `src/ir/parser.py` processes the domain. The method may be:
1. Not correctly extracting/parsing `wildcard_tuple_domain` nodes
2. Creating an invalid domain tuple that causes table value parsing to fail
3. Having logic that only works for simple wildcard `*` or explicit domain `ID` cases

## Investigation Needed

1. Check if `wildcard_tuple_domain` is handled in `_handle_table_domain_list`
2. Verify what domain tuple is created for `(*,*)` syntax
3. Determine if the issue is in domain parsing or in subsequent value assignment
4. Test if this affects only tables or also other constructs with wildcard tuple domains

## Workaround

Use single wildcard domain `(*)` instead of tuple wildcards when possible, or declare explicit domain sets.

## Impact

- **Severity**: Low - wildcard tuple syntax is less commonly used than single wildcards
- **Workaround**: Use explicit domains or single wildcard
- **Related Issues**: None currently

## Files Affected

- `src/ir/parser.py` - `_handle_table_block` method (domain extraction logic)
- `src/ir/parser.py` - `_handle_table_domain_list` or related domain parsing methods

## Acceptance Criteria

- [x] Tables with `(*,*)` domain parse correctly
- [x] Tables with `(*,*,*)` and higher-dimension tuple wildcards work
- [x] Column headers are extracted correctly
- [x] All values map to correct row/column combinations  
- [x] Test case `test_continuation_with_wildcard_domain` passes
- [x] Existing table and domain tests continue to pass

## Resolution

**Fixed in:** PR #401 (commit 1643d98)  
**Related Issue:** #399 (Table descriptions parsed as column headers)

The issue was inadvertently fixed as a side effect of the table continuation parsing improvements in PR #401. The root cause was in how the first line of table content was being processed when merging continuation lines.

### What Was Fixed

The changes to `_handle_table_block` in `src/ir/parser.py` for issue #399 corrected the continuation line merging logic, which had the side effect of fixing wildcard tuple domain parsing. Specifically:

1. The continuation line merging logic was updated to properly distinguish between column header continuations and data continuations
2. The first line token handling was improved to correctly extract column headers regardless of the domain syntax
3. The domain tuple processing now works correctly for wildcard tuple domains like `(*,*)`, `(*,*,*)`, etc.

### Verification

The test `test_continuation_with_wildcard_domain` now passes, confirming that:
- Tables with wildcard tuple domains `(*,*)` parse correctly
- Column headers are extracted properly
- All values map to the correct (row, column) combinations
- The fix works with table continuations as well

All 2183 tests pass, including existing table and domain tests.

## Additional Notes

This was a broader issue affecting wildcard tuple domains in table constructs. The fix in PR #401 resolved it comprehensively without requiring specific changes for wildcard tuple domain handling.
