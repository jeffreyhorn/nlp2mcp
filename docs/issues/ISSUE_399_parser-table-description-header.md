# Parser Bug: Table Descriptions Parsed as Column Headers

**GitHub Issue:** [#399](https://github.com/jeffreyhorn/nlp2mcp/issues/399)  
**Status:** Open  
**Priority:** Medium  
**Component:** Parser (Table Parsing)  
**Discovered:** 2025-12-03 (during Issue #392 testing)  
**Updated:** 2026-02-11 (Sprint 18 Day 8-9 findings)

## Problem Description

When a GAMS table includes a description string, the parser incorrectly treats the description as a column header instead of ignoring it or storing it separately as metadata.

## Sprint 18 Day 8 Findings (2026-02-11)

During domain violation investigation, we confirmed this issue blocks the `robert` model:

**Symptom:** GAMS Error 170 "Domain violation for element" on parameter `c(p,t)`

**Root Cause Analysis:**
- The `robert.gms` model has a table with description:
  ```gams
  Table c(p,t) 'expected profits'
            1    2    3
  low      25   20   10
  medium   30   27   20
  high     40   36   28;
  ```
- The parser treats `'expected profits'` as a column header
- Only 4 values are captured instead of 9 (3 rows × 3 columns)
- This causes 55% data loss

**Generated MCP file shows:**
```gams
Parameters
    c(p,t) /'1'.'expected profits' 2.0, low.'expected profits' 25.0, medium.'expected profits' 50.0, high.'expected profits' 75.0/
```

Instead of:
```gams
Parameters
    c(p,t) /low.1 25, low.2 20, low.3 10, medium.1 30, medium.2 27, medium.3 20, high.1 40, high.2 36, high.3 28/
```

**Classification:** ARCHITECTURAL - Parser semantic handler bug in `_handle_table_block` (grammar already supports optional descriptions).

**Note:** The `robert` model also has ISSUE_670 (cross-indexed sums) which would block it even after this fix.

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

## Affected Models

| Model | Impact | Other Blockers |
|-------|--------|----------------|
| robert | E170 domain violation | Also has ISSUE_670 (cross-indexed sums) |
| like | May contribute to issues | Primary blocker is ISSUE_392 |

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

## Implementation Location

- `src/ir/parser.py` - `_handle_table_block` method (around line 950-1200)

### Estimated Effort

**Medium** (1-2 hours):
- Grammar is already correct
- Need to update semantic handler to skip description token
- Add test cases for tables with descriptions

## Impact

- **Severity**: Medium - affects tables with descriptions
- **Workaround**: Remove description strings from table declarations
- **Related Issues**: ISSUE_392 (table continuation syntax)

## Acceptance Criteria

- [ ] Tables with STRING descriptions parse correctly
- [ ] Tables with DESCRIPTION descriptions parse correctly
- [ ] Column headers are extracted correctly (numeric and alphanumeric)
- [ ] All values map to correct row/column combinations
- [ ] An enabled unit test covers large GAMS-style tables with description headers and passes
- [ ] Existing table tests continue to pass
- [ ] robert.gms table `c(p,t)` parses all 9 values correctly

## References

- Sprint 18 Days 7-8 analysis in SPRINT_LOG.md
- GAMS Table Syntax Documentation
