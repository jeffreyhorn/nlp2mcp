# Parser Enhancement: Inline Descriptions in Set Element Declarations

**GitHub Issue**: #385 - https://github.com/jeffreyhorn/nlp2mcp/issues/385  
**Status**: Open  
**Priority**: High  
**Component**: Parser (src/ir/parser.py, src/gams/gams_grammar.lark)  
**Effort**: 3h  
**Impact**: Unlocks 3 Tier 2 models (chem, water, gastrans) - 30% parse rate improvement

## Summary

GAMS allows inline text descriptions for set elements using quoted strings. The parser currently does not support this syntax, blocking 3 Tier 2 models from parsing.

## Current Behavior

When parsing GAMS files with inline descriptions in set declarations, the parser fails with:

**Example from chem.gms (line 16):**
```
Error: Parse error at line 16, column 19: Unexpected character: '''
  i 'atoms'     / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
                    ^
```

**Example from water.gms (line 22):**
```
Error: Parse error at line 22, column 21: Unexpected character: '''
  n      'nodes' / nw 'north west reservoir', e 'east reservoir'
                      ^
```

**Example from gastrans.gms (line 25):**
```
Error: Parse error at line 25, column 1: Unexpected character: 'B'
  Brugge,    Dudzele,   Gent,    Liege,     Loenhout
  ^
```
(Note: gastrans has multi-line set declarations with continuation)

## Expected Behavior

The parser should accept inline descriptions in set element declarations and either:
1. Store them as metadata on the set element AST nodes, OR
2. Parse and ignore them (like comments)

## GAMS Syntax Reference

**Set Declaration with Descriptions:**
```gams
Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
```

**Set Element with Description:**
```gams
element_name 'descriptive text'
```

**Multi-line Set Declaration:**
```gams
Set n 'nodes' / 
    nw 'north west reservoir'
    e  'east reservoir'
    ne 'north east reservoir'
    s  'south reservoir' 
/;
```

From GAMS User's Guide, Section 2.4 "Set Declarations":
- Set elements can have optional quoted string descriptions
- Descriptions are for documentation purposes only
- Single or double quotes are accepted

## Reproduction

### Test Case 1: Single-line with descriptions (chem.gms)
```gams
Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
```

**Current Result:** Parse error at `'hydrogen'`  
**Expected Result:** Parse successfully

### Test Case 2: Multi-line with descriptions (water.gms)
```gams
Set n 'nodes' / 
    nw 'north west reservoir'
    e  'east reservoir'
    ne 'north east reservoir'
    s  'south reservoir' 
/;
```

**Current Result:** Parse error at `'north west reservoir'`  
**Expected Result:** Parse successfully

### Test Case 3: Multi-line continuation (gastrans.gms)
```gams
Set node 'nodes' /
    Brugge,    Dudzele,   Gent,    Liege,     Loenhout,
    Namur,     Mons,      Anderlues, Voeren
/;
```

**Current Result:** Parse error at `Brugge`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 3h

**Breakdown:**
- Grammar extension (1h): Modify set element parsing to accept optional quoted strings
- AST changes (0.5h): Add `description` field to set element nodes (or parse and discard)
- Multi-line handling (0.5h): Ensure continuation across newlines works correctly
- Testing (1h): 15 test cases covering:
  - Single-line declarations with descriptions
  - Multi-line declarations with descriptions
  - Mixed (some elements with descriptions, some without)
  - Nested sets with descriptions
  - Edge cases (empty descriptions, quoted descriptions with special chars)

### Parser Changes Checklist

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Verify STRING terminal captures single and double quotes
- [ ] Update set element rule: `set_element: ID (STRING)?`
- [ ] Ensure multi-line set declarations handle newlines correctly

**AST (if storing descriptions):**
- [ ] Add `description: Optional[str]` field to SetElement node
- [ ] Update transformer to extract description strings

**Parser Semantic Handler:**
- [ ] Handle optional description in set element parsing
- [ ] Store or discard description as appropriate
- [ ] Validate multi-line continuation logic

**Testing:**
- [ ] Unit tests for single-line set declarations with descriptions
- [ ] Unit tests for multi-line set declarations with descriptions
- [ ] Integration tests with chem.gms, water.gms, gastrans.gms
- [ ] Edge case tests (empty descriptions, special characters, mixed)

## Affected Models

**Tier 2 Models (Sprint 12 Selected):**
- ✅ chem.gms (40 lines, NLP) - Chemical Equilibrium Problem
- ✅ water.gms (88 lines, DNLP) - Water Distribution Network Design
- ✅ gastrans.gms (180 lines, NLP) - Gas Transmission Problem - Belgium

**Impact:** Unlocking these 3 models improves Tier 2 parse rate from 30% → 60% (3/10 → 6/10)

## Related Issues

- Issue #137: Hyphens in equation descriptions (SOLVED - PR #384)
- Inline descriptions are a common GAMS documentation pattern
- Similar to variable/parameter/equation descriptions but for set elements

## Technical Notes

### Current Grammar Pattern
```lark
set_block: "Set"i set_decl+ SEMI
set_decl: ID STRING? "/" set_elements "/"
set_elements: set_element ("," set_element)*
set_element: ID                    # Currently only supports ID
```

### Proposed Grammar Pattern
```lark
set_element: ID (STRING)?          # Add optional description
```

### Multi-line Handling

GAMS allows set declarations to span multiple lines:
```gams
Set i / 
    element1 'description 1'
    element2 'description 2'
    element3
/;
```

The parser must handle:
1. Newlines between elements (already supported)
2. Optional descriptions after element IDs
3. Commas are optional in multi-line declarations

### Description Storage Options

**Option 1: Store in AST (preferred)**
- Add `description: Optional[str]` to SetElement node
- Preserves documentation for downstream tools
- Minimal overhead (descriptions are short)

**Option 2: Parse and discard**
- Simpler implementation
- Loses documentation metadata
- Still allows models to parse successfully

**Recommendation:** Option 1 for completeness

## Success Criteria

- [ ] chem.gms parses successfully
- [ ] water.gms parses successfully  
- [ ] gastrans.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] 15+ new test cases added
- [ ] Parse rate for selected 10 Tier 2 models ≥ 60%

## References

- **GAMS Documentation:** User's Guide Section 2.4 "Set Declarations"
- **Sprint 12 Planning:** docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md
- **Model Selection:** docs/planning/EPIC_2/SPRINT_12/TIER_2_MODEL_SELECTION.md
- **Blocker Priority:** HIGH (Score: 27) - 3 models affected, medium complexity

## Example Test Cases

### Test 1: Basic inline description
```gams
Set i 'atoms' / H 'hydrogen', N 'nitrogen', O 'oxygen' /;
```

### Test 2: Mixed with and without descriptions
```gams
Set i / a 'first', b, c 'third' /;
```

### Test 3: Multi-line with descriptions
```gams
Set i /
    a 'first element'
    b 'second element'
    c
/;
```

### Test 4: Description with special characters
```gams
Set i / a 'element with "quotes" and symbols: @#$%' /;
```

### Test 5: Empty description
```gams
Set i / a '' /;
```
