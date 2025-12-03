# Parser Enhancement: Multi-line Set/Parameter Declarations

**GitHub Issue**: #388 - https://github.com/jeffreyhorn/nlp2mcp/issues/388  
**Status**: Open  
**Priority**: High  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 5h  
**Impact**: Unlocks 4 Tier 2 models - 22.2% parse rate improvement

## Summary

GAMS allows set element lists and parameter data to span multiple lines without explicit continuation characters. The parser currently fails when encountering newlines within these declarations, blocking 4 Tier 2 models from parsing.

## Current Behavior

When parsing GAMS files with multi-line declarations, the parser fails:

**Example from gastrans.gms (line 25):**
```
Error: Parse error at line 25, column 1: Unexpected character: 'B'
Set node 'nodes' /
  Brugge,    Dudzele,   Gent,    Liege,     Loenhout
  ^
```

**Example from water.gms (line 23):**
```
Error: Parse error at line 23, column 1: Unexpected character: 'c'
Set n 'nodes' / nw 'north west reservoir', e 'east reservoir',
  cc 'central city',         w 'west'
  ^
```

**Example from chem.gms (line 28):**
```
Error: Parse error at line 28, column 1: Unexpected character: 'N'
Parameter gibbs(c) 'gibbs free energy' / H -10.021, H2 -21.096
  NH -18.918, NO -28.032
  ^
```

**Example from pool.gms (line 69):**
```
Error: Parse error at line 69, column 1: Unexpected character: 'h'
Table cost 'blending costs' /
  haverly1         -400
  haverly2         -600
  ^
```

## Expected Behavior

The parser should accept multi-line declarations where:
- Set element lists continue across lines
- Parameter value lists continue across lines
- Table data rows continue across lines
- No explicit continuation character is required

## GAMS Syntax Reference

**Multi-line Set Declaration:**
```gams
Set node 'nodes' /
    Brugge,    Dudzele,   Gent,    Liege,     Loenhout,
    Namur,     Mons,      Anderlues, Voeren
/;
```

**Multi-line Parameter Declaration:**
```gams
Parameter gibbs(c) 'gibbs free energy' /
    H   -10.021
    H2  -21.096
    H2O -37.986
    NH  -18.918
/;
```

**Multi-line Table Declaration:**
```gams
Table cost 'blending costs' /
    haverly1  -400
    haverly2  -600
    haverly3  -800
/;
```

From GAMS User's Guide, Section 2.4 "Set Declarations":
- Elements within `/.../ ` can span multiple lines
- Commas between elements are optional when on separate lines
- Whitespace (including newlines) is generally ignored

## Reproduction

### Test Case 1: Multi-line set elements (gastrans.gms)
```gams
Set node 'nodes' /
    Brugge,    Dudzele,   Gent,    Liege,     Loenhout,
    Namur,     Mons,      Anderlues, Voeren
/;
```

**Current Result:** Parse error at `Brugge`  
**Expected Result:** Parse successfully with 9 elements

### Test Case 2: Multi-line set with descriptions (water.gms)
```gams
Set n 'nodes' /
    nw 'north west reservoir',
    e  'east reservoir',
    cc 'central city',
    w  'west'
/;
```

**Current Result:** Parse error at `cc`  
**Expected Result:** Parse successfully with 4 elements

### Test Case 3: Multi-line parameter data (chem.gms)
```gams
Parameter gibbs(c) /
    H   -10.021
    H2  -21.096
    NH  -18.918
/;
```

**Current Result:** Parse error at `NH`  
**Expected Result:** Parse successfully with 3 values

### Test Case 4: Multi-line table (pool.gms)
```gams
Table cost /
    haverly1  -400
    haverly2  -600
/;
```

**Current Result:** Parse error at `haverly2`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 5h

**Breakdown:**
- Grammar update (2h): Modify set/parameter/table rules to handle newlines
- Parser semantic handler (1.5h): Update element/value collection logic
- Multi-line handling (1h): Ensure proper newline treatment in various contexts
- Testing (1.5h): 25+ test cases covering:
  - Multi-line sets (with/without descriptions)
  - Multi-line parameters (1D, 2D, multi-dimensional)
  - Multi-line tables
  - Mixed single/multi-line in same file
  - Edge cases (trailing commas, blank lines)

### Implementation Checklist

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Update set_elements rule to allow newlines between elements
- [ ] Update parameter_values rule to allow newlines between values
- [ ] Update table_data rule to allow newlines between rows
- [ ] Ensure comma is optional when elements are on separate lines
- [ ] Handle optional trailing commas

**Current Grammar Pattern:**
```lark
set_block: "Set"i set_decl+ SEMI
set_decl: ID STRING? "/" set_elements "/"
set_elements: set_element ("," set_element)*
set_element: ID STRING?
```

**Proposed Grammar Pattern:**
```lark
set_block: "Set"i set_decl+ SEMI
set_decl: ID STRING? "/" set_elements "/"
set_elements: set_element (","? NEWLINE? set_element)*
set_element: ID STRING?
```

**Parser Semantic Handler:**
- [ ] Update set element collection to skip newlines
- [ ] Update parameter value collection to skip newlines
- [ ] Update table row collection to skip newlines
- [ ] Validate that commas and newlines are handled consistently

**Testing:**
- [ ] Unit tests for multi-line set declarations
- [ ] Unit tests for multi-line parameter declarations
- [ ] Unit tests for multi-line table declarations
- [ ] Integration tests with gastrans.gms, water.gms, chem.gms, pool.gms
- [ ] Edge case tests (blank lines, multiple newlines, trailing commas)

## Affected Models

**Tier 2 Models (4 blocked by this issue):**
- ✅ gastrans.gms (180 lines, NLP) - Gas Transmission Problem - Belgium
- ✅ water.gms (88 lines, DNLP) - Water Distribution Network Design
- ✅ chem.gms (40 lines, NLP) - Chemical Equilibrium Problem
- ✅ pool.gms (140 lines, NLP) - Pooling Problem

**Impact:** Unlocking these 4 models improves Tier 2 parse rate from 27.8% → 50.0% (5/18 → 9/18)

## Related Issues

- Related to general whitespace handling in declarations
- May overlap with table data parsing issues
- Independent of dynamic set ranges and attribute assignments

## Technical Notes

### Current Newline Handling

The grammar currently treats newlines as whitespace in most contexts, but within `/.../ ` blocks for sets and parameters, the parser expects continuous token sequences.

### Key Insight

GAMS allows flexible formatting:
```gams
# Single line
Set i / a, b, c /;

# Multi-line with commas
Set i /
    a, b, c
/;

# Multi-line without commas
Set i /
    a
    b
    c
/;

# Mixed
Set i /
    a, b
    c, d
/;
```

All four forms should parse identically.

### Grammar Changes

**Before:**
```lark
set_elements: set_element ("," set_element)*
```

**After:**
```lark
set_elements: set_element (","? NEWLINE* set_element)*
```

This allows:
- Optional comma between elements
- Multiple newlines between elements
- Commas at end of lines or on separate lines

### Edge Cases

**Trailing Comma:**
```gams
Set i / a, b, c, /;
```
**Behavior:** Should parse (trailing comma is optional in GAMS)

**Blank Lines:**
```gams
Set i /
    a
    
    b
/;
```
**Behavior:** Should parse (blank lines treated as whitespace)

**Mixed Formats:**
```gams
Set i / a, b
        c, d /;
```
**Behavior:** Should parse

## Success Criteria

- [ ] gastrans.gms parses successfully
- [ ] water.gms parses successfully
- [ ] chem.gms parses successfully
- [ ] pool.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] 25+ new test cases added for multi-line declarations
- [ ] Parse rate for Tier 2 models ≥ 50%

## References

- **GAMS Documentation:** User's Guide Section 2.4 "Set Declarations"
- **GAMS Documentation:** User's Guide Section 3.3 "Parameter Declarations"
- **GAMS Documentation:** User's Guide Section 4.2 "Table Statements"
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Multi-line set with commas
```gams
Set i /
    a, b, c,
    d, e, f
/;
```

### Test 2: Multi-line set without commas
```gams
Set i /
    a
    b
    c
/;
```

### Test 3: Multi-line set with descriptions
```gams
Set i /
    a 'first element'
    b 'second element'
    c 'third element'
/;
```

### Test 4: Multi-line parameter 1D
```gams
Parameter p(i) /
    a  1.5
    b  2.7
    c  3.9
/;
```

### Test 5: Multi-line parameter 2D
```gams
Parameter cost(i,j) /
    a.x  10
    a.y  20
    b.x  30
/;
```

### Test 6: Multi-line table
```gams
Table data(i,j)
       x    y    z
    a  1    2    3
    b  4    5    6
    c  7    8    9;
```

### Test 7: Mixed single/multi-line
```gams
Set i / a, b /;
Set j /
    x
    y
    z
/;
```

### Test 8: Trailing comma
```gams
Set i /
    a,
    b,
    c,
/;
```
