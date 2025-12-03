# Parser Enhancement: Multi-line Table Continuation with Plus Sign

**GitHub Issue**: #392 - https://github.com/jeffreyhorn/nlp2mcp/issues/392  
**Status**: Open  
**Priority**: Low  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 2h  
**Impact**: Unlocks 1 Tier 2 model - 5.6% parse rate improvement

## Summary

GAMS allows table data to continue across multiple lines using a plus sign (`+`) as an explicit continuation character. This is used for tables with many columns that don't fit on a single line. The parser currently does not support this continuation syntax, blocking 1 Tier 2 model from parsing.

## Current Behavior

When parsing GAMS files with plus-sign table continuation, the parser fails with:

**Example from like.gms (line 24):**
```
Error: Parse error at line 24, column 1: Unexpected character: '+'
Table p(i,*) 'frequency of pressure'
                 1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
   pressure     95 105 110 115 120 125 130 135 140 145 150 155 160 165 170
   frequency     1   1   4   4  15  15  15  13  21  12  17   4  20   8  17

   +            16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31
   ^
```

## Expected Behavior

The parser should accept plus-sign continuation in table declarations:
- A line starting with `+` continues the previous table row
- The `+` is followed by additional column headers or data values
- This allows tables with many columns to be split across multiple lines

## GAMS Syntax Reference

**Table with Plus-Sign Continuation:**
```gams
Table p(i,*) 'frequency of pressure'
                 1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
   pressure     95 105 110 115 120 125 130 135 140 145 150 155 160 165 170
   frequency     1   1   4   4  15  15  15  13  21  12  17   4  20   8  17
   +            16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31
   pressure    175 180 185 190 195 200 205 210 215 220 225 230 235 240 245 260
   frequency     8   6   6   7   4   3   3   8   1   6   0   5   1   7   1   2;
```

This is equivalent to having all column headers on one line and all data values on one line (if they fit).

From GAMS User's Guide, Section 4.2 "Table Statements":
- Tables can span multiple lines
- A line starting with `+` continues the previous row
- The `+` acts as a row continuation marker
- Used primarily for wide tables with many columns

## Reproduction

### Test Case 1: Table continuation (like.gms)
```gams
Table p(i,*) 'frequency of pressure'
                 1   2   3   4   5
   pressure     95 105 110 115 120
   frequency     1   1   4   4  15
   +             6   7   8   9  10
   pressure    125 130 135 140 145
   frequency    15  15  13  21  12;
```

**Current Result:** Parse error at `+`  
**Expected Result:** Parse successfully

### Test Case 2: Multiple continuations
```gams
Table data(i,j)
       col1  col2  col3
   +   col4  col5  col6
   +   col7  col8  col9
   
row1   1     2     3
   +   4     5     6
   +   7     8     9;
```

**Current Result:** Parse error at first `+`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 2h

**Breakdown:**
- Grammar update (0.5h): Add continuation line handling to table syntax
- Parser semantic handler (1h): Merge continuation lines with previous row
- Testing (0.5h): 10+ test cases covering:
  - Basic table continuation
  - Multiple continuation lines
  - Continuation in headers vs data
  - Mixed continuation and regular rows
  - Edge cases

### Implementation Checklist

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Add continuation_line rule for `+` followed by values
- [ ] Update table_row to optionally include continuation lines
- [ ] Handle whitespace before `+`

**Current Grammar Pattern:**
```lark
table_stmt: "Table"i ID indices? STRING? table_data SEMI
table_data: table_header table_rows
table_header: ID+
table_rows: table_row+
table_row: ID NUMBER+
```

**Proposed Grammar Pattern:**
```lark
table_stmt: "Table"i ID indices? STRING? table_data SEMI
table_data: table_header table_rows
table_header: header_segment continuation_segment*
header_segment: ID+
continuation_segment: "+" ID+
table_rows: table_row+
table_row: row_segment continuation_segment*
row_segment: ID NUMBER+
continuation_segment: "+" NUMBER+
```

**Parser Semantic Handler:**
- [ ] Merge continuation segments into the base row
- [ ] Concatenate column headers with continuations
- [ ] Concatenate data values with continuations
- [ ] Validate continuation lines have correct structure

**Testing:**
- [ ] Unit tests for basic table continuation
- [ ] Unit tests for multiple continuation lines
- [ ] Unit tests for header continuation
- [ ] Unit tests for data continuation
- [ ] Integration test with like.gms
- [ ] Edge case tests (empty continuation, extra whitespace)

## Affected Models

**Tier 2 Models (1 blocked by this issue):**
- ✅ like.gms (85 lines, NLP) - Likelihood Function Fitting

**Impact:** Unlocking this model improves Tier 2 parse rate from 27.8% → 33.3% (5/18 → 6/18)

## Related Issues

- Related to general table parsing
- May interact with multi-line declaration handling
- Independent of other blockers

## Technical Notes

### Continuation Semantics

**Conceptual model:**
```gams
# With continuation
Table data(i,j)
       a  b  c
   +   d  e  f
row1   1  2  3
   +   4  5  6;

# Equivalent without continuation
Table data(i,j)
       a  b  c  d  e  f
row1   1  2  3  4  5  6;
```

The `+` line simply extends the previous line.

### AST Representation

Tables are represented as:
```python
@dataclass
class TableData:
    """Table data declaration."""
    name: str
    indices: list[str]
    headers: list[str]       # Column headers (merged with continuations)
    rows: dict[str, list]    # Row name -> values (merged with continuations)
    location: SourceLocation
```

Continuation lines are merged during parsing, so the AST doesn't need special continuation representation.

### Parsing Strategy

1. Parse base header line
2. Parse continuation lines (starting with `+`)
3. Merge all segments into single header list
4. Repeat for each data row

### Example Parsing

**Input:**
```gams
Table p(i,*) 'data'
         1   2   3
   +     4   5
row1    10  20  30
   +    40  50;
```

**Parsing steps:**
1. Header base: `["1", "2", "3"]`
2. Header continuation: `["4", "5"]`
3. Merged header: `["1", "2", "3", "4", "5"]`
4. Row "row1" base: `[10, 20, 30]`
5. Row "row1" continuation: `[40, 50]`
6. Merged row: `{"row1": [10, 20, 30, 40, 50]}`

### Edge Cases

**Empty continuation:**
```gams
Table data
       a  b
   +
row1   1  2;
```
**Behavior:** Should treat as empty continuation (no additional columns)

**Multiple consecutive continuations:**
```gams
Table data
       a  b
   +   c  d
   +   e  f
row1   1  2
   +   3  4
   +   5  6;
```
**Behavior:** Merge all continuations in order

**Whitespace before plus:**
```gams
Table data
       a  b
    +  c  d    # Indented
row1   1  2;
```
**Behavior:** Should handle leading whitespace

## Success Criteria

- [ ] like.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] Continuation lines are properly merged in AST
- [ ] 10+ new test cases added for table continuation
- [ ] Parse rate for Tier 2 models ≥ 33%

## References

- **GAMS Documentation:** User's Guide Section 4.2 "Table Statements"
- **GAMS Table Syntax:** https://www.gams.com/latest/docs/UG_DataEntry.html#UG_DataEntry_Table
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Basic header continuation
```gams
Table data(i,j)
       a  b
   +   c  d
row1   1  2  3  4;
```

### Test 2: Basic data continuation
```gams
Table data(i,j)
       a  b  c  d
row1   1  2
   +   3  4;
```

### Test 3: Both header and data continuation
```gams
Table data(i,j)
       a  b
   +   c  d
row1   1  2
   +   3  4;
```

### Test 4: Multiple rows with continuation
```gams
Table data(i,j)
       a  b
   +   c  d
row1   1  2
   +   3  4
row2   5  6
   +   7  8;
```

### Test 5: Multiple continuation lines
```gams
Table data(i,j)
       a  b
   +   c  d
   +   e  f
row1   1  2  3  4  5  6;
```

### Test 6: Large table (like.gms pattern)
```gams
Table p(i,*) 'data'
                 1   2   3   4   5
   pressure     95 105 110 115 120
   frequency     1   1   4   4  15
   +             6   7   8   9  10
   pressure    125 130 135 140 145
   frequency    15  15  13  21  12;
```

### Test 7: No continuation (baseline)
```gams
Table data(i,j)
       a  b  c
row1   1  2  3;
```

### Test 8: Only header continuation
```gams
Table data(i,j)
       a  b
   +   c  d
row1   1  2  3  4;
```

### Test 9: Only data continuation
```gams
Table data(i,j)
       a  b  c  d
row1   1  2
   +   3  4;
```

### Test 10: Sparse continuation
```gams
Table data(i,j)
       a  b  c  d  e  f
row1   1  2
   +   3  4
   +   5  6;
```
