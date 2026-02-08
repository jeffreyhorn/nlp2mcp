# Issue: Multi-line Set Member Continuations

**GitHub Issue:** [#365](https://github.com/jeffreyhorn/nlp2mcp/issues/365)  
**Status:** ✅ RESOLVED (Fixed in PR #368)  
**Priority:** HIGH  
**Complexity:** MEDIUM (4-6h)  
**Impact:** 3 Tier 2 models (chem, gastrans, water)  
**Sprint:** Sprint 12 (Completed)  
**Resolution:** Issue was resolved by PR #368 which implemented `normalize_multi_line_continuations()` function

---

## Resolution Summary

This issue was **already fixed** in PR #368 (Fix #364: Multi-line Parameter Data with Numeric Indices). The `normalize_multi_line_continuations()` function implemented in that PR handles all the cases described in this issue.

**Fixed by:** PR #368 - commit 6855be6  
**Function:** `normalize_multi_line_continuations()` in `src/ir/preprocessor.py`  
**Verification:** All three test cases from this issue now parse successfully

---

## Problem Description

GAMS allows set member lists to span multiple lines within `/.../ ` delimiters without requiring explicit continuation characters or commas at line breaks. The parser currently fails to handle set members that continue across lines.

**Syntax:**
```gams
Set i 'elements' /
  member1, member2, member3
  member4, member5
  member6
/;
```

The newlines between members are treated as implicit separators (similar to commas).

---

## Affected Models

### 1. chem.gms (line 28)

**GAMS Syntax:**
```gams
Parameter
   gibbs(c) 'gibbs free energy at 3500 k and 750 psi'
            / H  -10.021, H2  -21.096, H2O -37.986, N   -9.846, N2 -28.653
              NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /
```

**Error:**
```
Error: Parse error at line 28, column 1: Unexpected character: 'N'
  NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /
  ^
```

**Blocker:** The second line of parameter data (`NH -18.918, ...`) is not recognized as a continuation of the previous line. The parser expects a keyword or statement, not a continuation of set members.

---

### 2. gastrans.gms (line 25)

**GAMS Syntax:**
```gams
Set
   n 'nodes' /
      Brugge,    Dudzele,   Gent,    Liege,     Loenhout
      Namur,     Mons,      Antwerp, Brussels
   /;
```

**Error:**
```
Error: Parse error at line 25, column 1: Unexpected character: 'B'
  Brugge,    Dudzele,   Gent,    Liege,     Loenhout
  ^
```

**Blocker:** Set members spanning multiple lines without commas at line breaks.

---

### 3. water.gms (line 23)

**GAMS Syntax:**
```gams
Set n 'nodes' /
   nw 'north-west', e 'east',        cc 'central city'
   w 'west',        sw 'south-west', s 'south',         se 'south-east'
/;
```

**Error:**
```
Error: Parse error at line 23, column 1: Unexpected character: 'c'
  cc 'central city',         w 'west'
  ^
```

**Blocker:** Continuation of set members on second line not recognized.

---

## Root Cause Analysis

### Preprocessor Issue

The preprocessor needs to detect when we're inside a `/.../ ` data block and normalize multi-line member lists by ensuring proper separation between items.

**Current Behavior:**
- Preprocessor doesn't track data block state across lines
- Newlines inside data blocks are preserved as-is
- Parser expects commas or semicolons to separate statements

**Required Behavior:**
- Detect `/` opening delimiter for data blocks
- Track state across multiple lines until closing `/`
- Ensure each line has proper separators (commas)
- Handle both Set and Parameter data blocks

---

## Solution Design

### Option 1: Preprocessor Normalization (RECOMMENDED)

Add a preprocessing step to normalize multi-line data blocks:

```python
def normalize_multi_line_data_blocks(source: str) -> str:
    """Ensure data block members on separate lines have comma separators.
    
    Example:
        Set i /
          a, b
          c, d
        /;
        
        Becomes:
        Set i /
          a, b,
          c, d
        /;
    """
    lines = source.split('\n')
    result = []
    in_data_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track data block entry
        if '/' in line and not in_data_block:
            if is_data_block_start(line):
                in_data_block = True
        
        # Inside data block: ensure lines end with comma
        if in_data_block:
            if not stripped.endswith(('/;', '/', ',', ';')):
                # Add trailing comma if missing
                line = line.rstrip() + ','
            
            # Check for closing delimiter
            if '/' in stripped and (stripped.endswith('/') or stripped.endswith('/;')):
                in_data_block = False
        
        result.append(line)
    
    return '\n'.join(result)
```

**Integration:**
- Add to `preprocess_gams_file()` pipeline
- Run after `$include` expansion but before parsing
- Similar to existing `normalize_special_identifiers()`

### Option 2: Grammar Enhancement

Modify grammar to handle newlines as implicit separators within data blocks:

```lark
set_members: set_member (_WS_OR_NEWLINE set_member)* ","?

_WS_OR_NEWLINE: /[\s\n]+/
```

**Drawbacks:**
- More complex grammar changes
- Harder to maintain
- Affects lexer/parser performance

---

## Implementation Plan

### Phase 1: Preprocessor Function (2h)
1. Implement `normalize_multi_line_data_blocks()` in `src/ir/preprocessor.py`
2. Detect Set/Parameter declarations with `/.../ ` blocks
3. Add trailing commas to lines within data blocks that don't already have them
4. Handle edge cases:
   - Comments within data blocks
   - String literals containing newlines
   - Nested structures (tables)

### Phase 2: Integration (1h)
1. Add to preprocessing pipeline in `preprocess_gams_file()`
2. Position after `normalize_special_identifiers()` but before parsing
3. Ensure proper interaction with other preprocessors

### Phase 3: Testing (2h)
1. Unit tests for `normalize_multi_line_data_blocks()`
   - Simple set members across lines
   - Parameter data across lines
   - Mixed comma/newline separators
   - Edge cases (comments, strings)
2. Integration tests with affected models:
   - `chem.gms`
   - `gastrans.gms`
   - `water.gms`
3. Regression tests for existing GAMSLib models

### Phase 4: Validation (1h)
1. Verify all 3 affected models parse successfully
2. Run full test suite
3. Update Tier 2 analysis results
4. Document in sprint summary

---

## Testing Strategy

### Unit Tests
```python
class TestMultiLineDataBlocks:
    def test_set_members_multi_line(self):
        source = """
        Set i / a, b
                c, d /;
        """
        expected = """
        Set i / a, b,
                c, d /;
        """
        assert normalize_multi_line_data_blocks(source) == expected
    
    def test_parameter_data_multi_line(self):
        source = """
        Parameter p / x 1, y 2
                      z 3 /;
        """
        expected = """
        Parameter p / x 1, y 2,
                      z 3 /;
        """
        assert normalize_multi_line_data_blocks(source) == expected
    
    def test_already_has_commas(self):
        source = """
        Set i / a, b,
                c, d /;
        """
        # Should be unchanged
        assert normalize_multi_line_data_blocks(source) == source
```

### Integration Tests
- Test parsing of `chem.gms`, `gastrans.gms`, `water.gms`
- Verify data block contents are correctly parsed
- Check that parameter values are preserved

---

## Edge Cases

1. **Comments within data blocks:**
   ```gams
   Set i /
      a, b  * first batch
      c, d  * second batch
   /;
   ```
   
2. **String literals with newlines:**
   ```gams
   Set i /
      a "description
         continued"
      b
   /;
   ```

3. **Inline closing:**
   ```gams
   Set i / a, b, c /;  * already inline
   ```

4. **Table syntax (different structure):**
   ```gams
   Table data(i,j)
         col1  col2
      a    1     2
      b    3     4;
   ```
   Tables have different syntax and should not be affected.

---

## Success Criteria

- [ ] All 3 affected models parse successfully
- [ ] Unit tests for multi-line data block normalization pass
- [ ] No regressions in existing GAMSLib models
- [ ] Tier 2 parse rate increases from 28% to 44% (5/18 → 8/18)
- [ ] Code follows existing preprocessor patterns
- [ ] Documentation updated

---

## Related Issues

- #361 - Lag/Lead Operators (different blocker category)
- Similar to `normalize_special_identifiers()` preprocessing approach

---

## References

- GAMS Documentation: Set Declaration Syntax
- Existing preprocessor: `src/ir/preprocessor.py`
- Test models: `tests/fixtures/tier2_candidates/{chem,gastrans,water}.gms`
