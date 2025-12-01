# Issue: Newline as Implicit Separator in Set and Parameter Declarations

**GitHub Issue:** [#353](https://github.com/jeffreyhorn/nlp2mcp/issues/353)  
**Status:** Open  
**Priority:** HIGH  
**Complexity:** HIGH (4-6h)  
**Impact:** 3 Tier 2 models (chem, water, gastrans)  
**Sprint:** Sprint 13

---

## Problem Description

GAMS allows implicit line continuation in set member lists and parameter data without requiring trailing commas. Our parser currently requires explicit commas between all list elements, causing parse failures when GAMS code spans multiple lines without trailing commas.

---

## Examples

### Set Member Lists (water.gms, gastrans.gms)

**Current GAMS Syntax:**
```gams
Set n 'nodes' / nw 'north west reservoir', e 'east reservoir'
                cc 'central city', w 'west'
                sw 'south west', s 'south'
                se 'south east', n 'north' /;
```

**Issue:** Line 1 ends with `'east reservoir'` (no comma), line 2 starts with `cc 'central city'`.

**Error:**
```
Error: Parse error at line 2, column 1: Unexpected character: 'c'
Expected one of: SLASH, COMMA
```

### Parameter Data Lists (chem.gms)

**Current GAMS Syntax:**
```gams
Parameter
   gibbs(c) 'gibbs free energy'
            / H  -10.021, H2  -21.096, H2O -37.986, N -9.846, N2 -28.653
              NH -18.918, NO -28.032, O  -14.640, o2 -30.594, OH -26.11 /;
```

**Issue:** Line 1 ends with `N2 -28.653` (no comma), line 2 starts with `NH -18.918`.

**Error:**
```
Error: Parse error at line 2, column 1: Unexpected character: 'N'
```

---

## Root Cause Analysis

### Grammar Ambiguity

Attempted fix (making commas optional):
```lark
set_members: set_member (","? set_member)*
```

**Problem:** This creates ambiguity with the `ID STRING` pattern for inline descriptions:
- `H 'hydrogen'` should match as ONE element with description
- With optional commas, parser matches as TWO elements: `H` (ID) + `'hydrogen'` (STRING)

### Test Failure Example

```python
# Expected: ['H', 'N', 'O']
# Actual:   ['H', "'hydrogen'", 'N', "'nitrogen'", 'O', "'oxygen'"]
```

The parser treats each STRING as a separate set element instead of part of the preceding ID.

---

## Attempted Solutions

### ❌ Attempt 1: Optional Commas
- Grammar: `(","? set_member)*`
- Result: FAILED - breaks inline description parsing
- Test failures: 6 tests in test_inline_descriptions.py

### ❌ Attempt 2: Reordered Grammar Rules
- Tried prioritizing `ID STRING` before `ID` and `STRING`
- Result: FAILED - Lark's greedy matching still splits them

---

## Proposed Solutions

### Option A: Preprocessor Normalization (RECOMMENDED)

**Approach:** Add preprocessing step to normalize multi-line continuations before parsing.

**Algorithm:**
```python
def normalize_continuations(source: str) -> str:
    """
    Within / ... / blocks (sets/parameters):
    - Detect continuation lines (leading whitespace, no /; at start)
    - Insert commas at end of previous line if missing
    """
    # Track state: inside data block?
    # If line starts with whitespace and previous line didn't end with comma/slash
    # Insert comma at end of previous line
```

**Pros:**
- No grammar changes needed
- Preserves inline description logic
- Deterministic behavior

**Cons:**
- Adds preprocessing complexity
- May need to handle edge cases (comments, strings)

**Effort:** 4-5h

---

### Option B: Context-Sensitive Lexer

**Approach:** Make lexer track context (inside `/.../ block`) and emit special "implicit separator" tokens.

**Implementation:**
- Custom lexer callback to detect data block boundaries
- Emit COMMA token when newline detected inside block without trailing comma
- Grammar remains unchanged

**Pros:**
- No source modification
- Grammar stays clean

**Cons:**
- Complex lexer state management
- Lark callback mechanisms may be limited

**Effort:** 5-6h

---

### Option C: Grammar Restructuring

**Approach:** Separate grammar rules for single-line vs multi-line declarations.

**Example:**
```lark
set_members: set_member_line+
set_member_line: set_member ("," set_member)* ","?  // Allow trailing comma
```

**Pros:**
- Explicit multi-line handling

**Cons:**
- Still ambiguous with ID STRING
- Likely won't solve the core issue

**Effort:** 3-4h (with unknown success rate)

---

## Recommendation

**Implement Option A (Preprocessor Normalization)** in Sprint 13.

**Rationale:**
- Highest success probability
- Preserves existing grammar and parser logic
- Similar to how we handle `$ontext/$offtext` comments

**Implementation Plan:**
1. Add `normalize_multi_line_continuations()` to preprocessor.py
2. Detect `/.../ block` boundaries (sets, parameters, scalars)
3. Insert commas at line ends where missing (before newline + leading whitespace)
4. Unit test with water.gms, chem.gms, gastrans.gms patterns
5. Integration test: parse all 3 models successfully

---

## Affected Models

| Model | Lines | Error Location | Status |
|-------|-------|----------------|--------|
| chem | 58 | line 28 | Blocked |
| water | 114 | line 23 | Blocked (also needs tuple_notation fix) |
| gastrans | 242 | line 25 | Blocked |

**Parse Rate Impact:** +30% Tier 2 (3/10 models → 5/10 or 6/10 models)

---

## Testing Requirements

1. Unit tests for preprocessor normalization
2. Regression tests: ensure inline descriptions still work
3. Integration tests: chem.gms, water.gms, gastrans.gms parse successfully
4. Edge cases:
   - Comments within data blocks
   - Strings containing newlines (rare)
   - Nested structures

---

## References

- Failing models: `tests/fixtures/tier2_candidates/{chem,water,gastrans}.gms`
- Grammar: `src/gams/gams_grammar.lark` (lines 130-135)
- Parser: `src/ir/parser.py` (lines 614-657)
- Blocker analysis: `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`
