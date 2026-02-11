# Parser Bug: Table Descriptions Parsed as Column Headers

**GitHub Issue:** [#399](https://github.com/jeffreyhorn/nlp2mcp/issues/399)  
**Status:** Open  
**Priority:** Medium  
**Component:** Parser (Table Parsing)  
**Discovered:** 2025-12-03 (during Issue #392 testing)

## Problem Description

When a GAMS table includes a description string, the parser incorrectly treats the description as a column header instead of ignoring it or storing it separately as metadata.

## Example

```gams
Set i;
Table p(i,*) 'frequency of pressure'
                 1   2   3
   pressure     95 105 110;
```

**Expected behavior:**
- Description `'frequency of pressure'` should be stored as table metadata or ignored
- Column headers should be: `1`, `2`, `3`
- Values should map correctly: `pressure,1 -> 95`, `pressure,2 -> 105`, `pressure,3 -> 110`

**Actual behavior:**
- Description `'frequency of pressure'` is treated as a column header
- Only one column `'frequency of pressure'` is recognized
- Only last value in row is stored: `pressure,'frequency of pressure' -> 105`

## Test Case

The following test case (from `tests/unit/gams/test_parser.py::TestTableContinuation::test_large_table_like_gms_pattern`) demonstrates the issue:

```python
def test_large_table_like_gms_pattern(self):
    """Test pattern from like.gms with many columns."""
    text = dedent("""
        Set i;
        Table p(i,*) 'frequency of pressure'
                         1   2   3   4   5
           pressure     95 105 110 115 120
           frequency     1   1   4   4  15
           +             6   7   8   9  10
           pressure    125 130 135 140 145
           frequency    15  15  13  21  12;
    """)
    model = parser.parse_model_text(text)
    assert "p" in model.params
    # This assertion fails because description is treated as column
    assert ("pressure", "1") in model.params["p"].values
```

## Current Grammar

The current grammar defines tables as:

```lark
table_block: "Table"i ID "(" table_domain_list ")" (STRING | DESCRIPTION)? table_content+ SEMI
```

The `(STRING | DESCRIPTION)?` correctly allows for an optional description, but the parser's `_handle_table_block` method doesn't properly handle or skip this token when collecting column headers.

## Root Cause

In `src/ir/parser.py`, the `_handle_table_block` method collects all tokens from table rows and continuation lines, but doesn't filter out or separately handle STRING/DESCRIPTION tokens that appear immediately after the table header. These tokens get grouped with the first line's tokens and are mistakenly treated as column headers.

## Proposed Solution

1. In `_handle_table_block`, extract any STRING/DESCRIPTION child directly from the `table_block` node before processing rows
2. Store the description in the `ParameterDef` or discard it (depending on whether we want to preserve metadata)
3. Ensure the description token is not included in `all_tokens` collection that feeds into column header parsing

## Impact

- **Severity**: Medium - affects tables with descriptions
- **Workaround**: Remove description strings from table declarations
- **Related Issues**: None currently

## Files Affected

- `src/ir/parser.py` - `_handle_table_block` method (around line 950-1200)

## Acceptance Criteria

- [ ] Tables with STRING descriptions parse correctly
- [ ] Tables with DESCRIPTION descriptions parse correctly
- [ ] Column headers are extracted correctly (numeric and alphanumeric)
- [ ] All values map to correct row/column combinations
- [ ] Test case `test_large_table_like_gms_pattern` passes
- [ ] Existing table tests continue to pass
