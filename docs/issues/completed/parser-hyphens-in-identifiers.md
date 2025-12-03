# Parser Enhancement: Hyphens in Identifiers

**GitHub Issue**: #390 - https://github.com/jeffreyhorn/nlp2mcp/issues/390  
**Status**: Open  
**Priority**: Medium  
**Component**: Lexer (src/gams/gams_grammar.lark)  
**Effort**: 2h  
**Impact**: Unlocks 1 Tier 2 model - 5.6% parse rate improvement

## Summary

GAMS allows hyphens (`-`) and plus signs (`+`) within identifiers (set elements, variable names, etc.) in certain contexts. The parser currently treats hyphens as operators, causing parse errors when they appear in identifiers. This blocks 1 Tier 2 model from parsing.

## Current Behavior

When parsing GAMS files with hyphens in identifiers, the parser fails with:

**Example from chenery.gms (line 17):**
```
Error: Parse error at line 17, column 37: Unexpected character: '-'
i 'sectors' / light-ind, food+agr, heavy-ind, services /
                                    ^
```

## Expected Behavior

The parser should accept hyphens and plus signs in identifiers when used in set element declarations and other identifier contexts:
- `light-ind` as a single identifier
- `food+agr` as a single identifier
- `heavy-ind` as a single identifier

## GAMS Syntax Reference

**Set Declaration with Hyphenated Identifiers:**
```gams
Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;
```

**Table with Hyphenated Row/Column Labels:**
```gams
Table aio(i,i) 'input coefficients'
           light-ind  food+agr  heavy-ind  services
light-ind     0.1       0.2       0.3        0.4
food+agr      0.5       0.1       0.2        0.3
heavy-ind     0.2       0.3       0.1        0.2
services      0.1       0.1       0.1        0.1;
```

From GAMS User's Guide, Section 2.2 "Identifiers":
- Identifiers can contain letters, digits, and certain special characters
- Hyphens and plus signs are allowed in quoted identifiers or in specific contexts
- In set declarations, GAMS is lenient about identifier characters

## Important Distinction

This issue is **different** from Issue #137 (hyphens in descriptions):
- **Issue #137:** Hyphens in quoted descriptions (e.g., `eq 'mass-balance'`) ✅ SOLVED
- **This issue:** Hyphens in unquoted identifiers (e.g., `i / light-ind /`)

## Reproduction

### Test Case 1: Hyphens in set elements (chenery.gms)
```gams
Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;
```

**Current Result:** Parse error at `-` in `light-ind`  
**Expected Result:** Parse successfully with 4 elements

### Test Case 2: Hyphens in table labels
```gams
Table aio(i,i) 'input coefficients'
           light-ind  food+agr
light-ind     0.1       0.2
food+agr      0.5       0.1;
```

**Current Result:** Parse error at `-` in `light-ind`  
**Expected Result:** Parse successfully

## Implementation Plan

### Complexity Estimate: 2h

**Breakdown:**
- Lexer/Grammar update (1h): Modify identifier token to accept hyphens/plus signs
- Context sensitivity (0.5h): Ensure hyphens are operators in expressions but allowed in identifiers
- Testing (0.5h): 12+ test cases covering:
  - Hyphens in set elements
  - Plus signs in set elements
  - Mixed hyphen/plus/underscore identifiers
  - Hyphens in table labels
  - Disambiguation from operators
  - Edge cases

### Implementation Checklist

**Grammar (src/gams/gams_grammar.lark):**
- [ ] Review current identifier token (ID terminal)
- [ ] Create specialized token for set elements that allows hyphens
- [ ] Ensure hyphen is still treated as operator in expressions
- [ ] Handle context-sensitive parsing (identifiers vs expressions)

**Current Grammar Pattern:**
```lark
ID: /[a-zA-Z][a-zA-Z0-9_]*/
set_element: ID STRING?
```

**Proposed Grammar Pattern (Option 1 - Context-sensitive):**
```lark
ID: /[a-zA-Z][a-zA-Z0-9_]*/
SET_ELEMENT_ID: /[a-zA-Z][a-zA-Z0-9_+\-]*/
set_element: SET_ELEMENT_ID STRING?
```

**Proposed Grammar Pattern (Option 2 - Quoted identifiers):**
```lark
# Allow quoted identifiers anywhere
identifier: ID | QUOTED_ID
QUOTED_ID: /'[^']+'/
set_element: identifier STRING?
```

**Testing:**
- [ ] Unit tests for hyphenated set elements
- [ ] Unit tests for plus-sign identifiers
- [ ] Unit tests for table labels with hyphens
- [ ] Integration test with chenery.gms
- [ ] Disambiguation tests (ensure `-` is still operator in expressions)
- [ ] Edge case tests (multiple hyphens, leading/trailing hyphens)

## Affected Models

**Tier 2 Models (1 blocked by this issue):**
- ✅ chenery.gms (185 lines, NLP) - Substitution and Structural Change

**Impact:** Unlocking this model improves Tier 2 parse rate from 27.78% → 33.33% (5/18 → 6/18)

## Related Issues

- **Issue #137:** Hyphens in equation descriptions - SOLVED via PR #384
- Different from dynamic set ranges
- May interact with expression parsing (need to disambiguate operators)

## Technical Notes

### Challenge: Disambiguation

The main challenge is distinguishing between:
```gams
Set i / light-ind /;        # "light-ind" is a single identifier
x = a - b;                  # "-" is subtraction operator
```

### Solution Approaches

**Approach 1: Context-Sensitive Lexing**
- Use different token types in different contexts
- `SET_ELEMENT_ID` allows hyphens
- Regular `ID` does not
- Requires grammar to specify context

**Approach 2: Quoted Identifiers**
- Require quotes for identifiers with special characters
- `Set i / 'light-ind', 'food+agr' /;`
- More restrictive than GAMS, but unambiguous

**Approach 3: Lookahead/Lexer Modes**
- Use lexer modes to switch behavior inside `/.../ `
- Complex but matches GAMS behavior exactly

**Recommendation:** Approach 1 (context-sensitive tokens) is simplest and matches GAMS behavior.

### Lexer Priority

Need to ensure the more specific token (SET_ELEMENT_ID) has higher priority than operators:
```lark
?start: model

# Terminals (order matters for priority)
SET_ELEMENT_ID.10: /[a-zA-Z][a-zA-Z0-9_+\-]*/  # High priority in set context
ID: /[a-zA-Z][a-zA-Z0-9_]*/                    # Lower priority
```

### Example Disambiguation

**Set context (allow hyphens):**
```gams
Set i / light-ind, food+agr /;
```
Tokens: `SET_ELEMENT_ID("light-ind")`, `SET_ELEMENT_ID("food+agr")`

**Expression context (hyphen is operator):**
```gams
x = light - ind;
```
Tokens: `ID("light")`, `MINUS`, `ID("ind")`

### Alternative: Relaxed Identifier Rules

GAMS actually allows many characters in identifiers in certain contexts. We could adopt a "when in doubt, it's an identifier" approach:
- Inside `/.../ ` for set declarations: very permissive
- Inside expressions: strict (only alphanumeric + underscore)

## Success Criteria

- [ ] chenery.gms parses successfully
- [ ] All existing tests continue to pass (no regressions)
- [ ] Hyphens in expressions still parse as operators
- [ ] Plus signs in expressions still parse as operators
- [ ] 12+ new test cases added for hyphenated identifiers
- [ ] Parse rate for Tier 2 models ≥ 33%

## References

- **GAMS Documentation:** User's Guide Section 2.2 "Identifiers"
- **Issue #137:** Hyphens in equation descriptions (related but different)
- **Sprint 12 Planning:** Tier 2 model blocker analysis

## Example Test Cases

### Test 1: Hyphenated set elements
```gams
Set i / light-ind, heavy-ind /;
```

### Test 2: Plus signs in identifiers
```gams
Set j / food+agr, service+trade /;
```

### Test 3: Mixed special characters
```gams
Set k / a-b, c+d, e_f, g /;
```

### Test 4: Table with hyphenated labels
```gams
Table data(i,j)
           x-1  x-2  x-3
    row-1   1    2    3
    row-2   4    5    6;
```

### Test 5: Disambiguation - hyphen as operator
```gams
x = a - b;    * Minus operator, not identifier "a-b"
```

### Test 6: Disambiguation - plus as operator
```gams
y = c + d;    * Plus operator, not identifier "c+d"
```

### Test 7: Multiple hyphens
```gams
Set i / very-long-identifier-name /;
```

### Test 8: Numbers with hyphens
```gams
Set i / item-1, item-2, item-3 /;
```

### Test 9: Set with descriptions and hyphens
```gams
Set i /
    light-ind  'light industry'
    heavy-ind  'heavy industry'
/;
```

### Test 10: Alias with hyphenated identifiers
```gams
Set i / light-ind, heavy-ind /;
Alias(i, j);
```
