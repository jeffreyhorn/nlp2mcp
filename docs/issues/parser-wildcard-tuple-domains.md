# Parser Bug: Wildcard Tuple Domains Not Supported

**GitHub Issue:** [#400](https://github.com/jeffreyhorn/nlp2mcp/issues/400)  
**Status:** Open  
**Priority:** Low  
**Component:** Parser (Table Parsing)  
**Discovered:** 2025-12-03 (during Issue #392 testing)

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

- [ ] Tables with `(*,*)` domain parse correctly
- [ ] Tables with `(*,*,*)` and higher-dimension tuple wildcards work
- [ ] Column headers are extracted correctly
- [ ] All values map to correct row/column combinations  
- [ ] Test case `test_continuation_with_wildcard_domain` passes
- [ ] Existing table and domain tests continue to pass

## Additional Notes

This may be a broader issue affecting wildcard tuple domains in other GAMS constructs (parameters, variables, equations), not just tables. Further investigation is needed to determine scope.
