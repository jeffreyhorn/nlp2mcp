# Issue: Chenery Special Characters Regression

**GitHub Issue:** [#366](https://github.com/jeffreyhorn/nlp2mcp/issues/366)  
**Status:** Open  
**Priority:** MEDIUM  
**Complexity:** LOW (1-2h)  
**Impact:** 1 Tier 2 model (chenery)  
**Sprint:** Sprint 13+

---

## Problem Description

The `chenery.gms` model uses special characters (hyphens and plus signs) in set member identifiers like `light-ind`, `food+agr`, and `heavy-ind`. Despite implementing `normalize_special_identifiers()` in PR #358, this model is still failing to parse.

**Expected Behavior:**
The preprocessor should quote these identifiers automatically:
```gams
Set i / light-ind, food+agr, heavy-ind, services /;
```
Should become:
```gams
Set i / 'light-ind', 'food+agr', 'heavy-ind', services /;
```

**Actual Behavior:**
Parse error at the first special character identifier.

---

## Affected Model

### chenery.gms (line 17)

**GAMS Syntax:**
```gams
Set
   i    'sectors'               / light-ind, food+agr, heavy-ind, services /
   t(i) 'tradables'             / light-ind, food+agr, heavy-ind /
   lmh  'possible elasticities' / low, medium, high /
   sde  'other parameters'      / subst, distr, effic /;

Alias (i,j);

Table aio(i,i) 'input coefficients'
               light-ind  food+agr  heavy-ind  services
   food+agr           .1
   heavy-ind          .2        .1
   services           .2        .3         .1          ;
```

**Error:**
```
Error: Parse error at line 17, column 37: Unexpected character: '-'
  i    'sectors'               / light-ind, food+agr, heavy-ind, services /
                                      ^
```

**Blocker:** Special character identifiers in both set declarations and table headers are not being quoted by the preprocessor.

---

## Root Cause Analysis

### Hypothesis 1: Multi-line Set Declaration
The Set declaration spans multiple lines:
```gams
Set
   i    'sectors'  / light-ind, ... /
   t(i) 'tradables' / light-ind, ... /
   ...
```

The `normalize_special_identifiers()` function may not be detecting these as data blocks because:
1. The keyword `Set` is on a different line from the `/.../ ` data
2. The function checks for `Set/Parameter/Scalar/Alias` at the start of each line
3. Lines starting with identifiers (like `i 'sectors'`) don't match the pattern

### Hypothesis 2: Context Detection Regex
The current regex in `normalize_special_identifiers()`:
```python
is_declaration = re.match(r"^\s*(Set|Parameter|Scalar|Alias)\b", line, re.IGNORECASE)
```

This only matches lines that START with the keyword. In chenery.gms:
- Line 1: `Set` ✓ (matches)
- Line 2: `   i    'sectors'  / light-ind, ...` ✗ (doesn't match, starts with whitespace + identifier)

### Hypothesis 3: Table Headers Not Processed
Table headers with special chars:
```gams
Table aio(i,i) 'input coefficients'
               light-ind  food+agr  heavy-ind  services
```

The table header line (`light-ind food+agr ...`) should be processed, but the function may not be recognizing it as part of a table.

---

## Solution Design

### Option 1: Track Multi-line Declaration Context (RECOMMENDED)

Modify `normalize_special_identifiers()` to maintain state across lines when inside a Set/Parameter/Scalar/Alias declaration:

```python
def normalize_special_identifiers(source: str) -> str:
    lines = source.split("\n")
    result = []
    in_data_block = False
    in_table = False
    in_multi_line_declaration = False  # NEW: track multi-line Set/Parameter
    
    for line in lines:
        stripped = line.strip()
        
        # Check if starting a multi-line declaration
        if re.match(r"^\s*(Set|Parameter|Scalar|Alias)\b", stripped, re.IGNORECASE):
            in_multi_line_declaration = True
        
        # Check if we're in a declaration and hit a data block
        if in_multi_line_declaration and "/" in line:
            # Process this line as data block
            processed = _quote_special_in_line(line)
            result.append(processed)
            
            # Check if declaration ends
            if ";" in line:
                in_multi_line_declaration = False
            continue
        
        # End declaration if we hit a semicolon
        if in_multi_line_declaration and ";" in line:
            in_multi_line_declaration = False
        
        # ... rest of existing logic
```

### Option 2: More Flexible Line Matching

Instead of requiring the keyword at the start of the line, look back to see if we're inside a declaration:

```python
# Track if previous lines started a Set/Parameter declaration
# that hasn't been closed yet
if "/" in line and not in_data_block:
    # Look back to find if we're in a declaration
    # Check recent lines for Set/Parameter without closing ;
```

This is more complex and error-prone.

---

## Implementation Plan

### Phase 1: Debug Current Behavior (30min)
1. Add debug logging to `normalize_special_identifiers()`
2. Run chenery.gms through preprocessor
3. Identify which lines are/aren't being processed
4. Confirm hypothesis about multi-line declarations

### Phase 2: Fix Multi-line Declaration Tracking (1h)
1. Add `in_multi_line_declaration` state tracking
2. Detect Set/Parameter/Scalar/Alias keywords
3. Process all lines until closing `;`
4. Special handling for `/.../ ` within declarations

### Phase 3: Testing (30min)
1. Unit test for multi-line Set declaration:
   ```python
   def test_multi_line_set_with_special_chars():
       source = """
       Set
          i 'sectors' / light-ind, food+agr /
          j 'regions' / north-east, south-west /;
       """
       result = normalize_special_identifiers(source)
       assert "'light-ind'" in result
       assert "'food+agr'" in result
   ```

2. Test chenery.gms parsing
3. Verify table headers are processed correctly
4. Regression test existing models

---

## Testing Strategy

### Unit Tests
```python
class TestMultiLineDeclarations:
    def test_multi_line_set_special_chars(self):
        source = """
        Set
           i 'sectors' / light-ind, food+agr, heavy-ind /;
        """
        result = normalize_special_identifiers(source)
        assert "'light-ind'" in result
        assert "'food+agr'" in result
        assert "'heavy-ind'" in result
    
    def test_table_headers_special_chars(self):
        source = """
        Table aio(i,i)
                   light-ind  food+agr  heavy-ind
           food+agr      .1
           heavy-ind     .2      .1     ;
        """
        result = normalize_special_identifiers(source)
        # Table headers and row labels should be quoted
        assert "'light-ind'" in result
        assert "'food+agr'" in result
```

### Integration Test
- Parse `chenery.gms` successfully
- Verify Set `i` has members: `'light-ind'`, `'food+agr'`, `'heavy-ind'`, `services`
- Verify table headers are processed

---

## Edge Cases

1. **Mixed inline and multi-line:**
   ```gams
   Set i / a, b /, j / x-1, y-2 /;
   ```

2. **Nested special chars in descriptions:**
   ```gams
   Set i / light-ind "light industry - manufacturing" /;
   ```

3. **Special chars in table row/column labels:**
   ```gams
   Table data(i,j)
          col-1  col-2
      row-1  1     2
      row-2  3     4;
   ```

---

## Success Criteria

- [ ] chenery.gms parses successfully
- [ ] Set members with special chars are properly quoted
- [ ] Table headers with special chars are properly quoted  
- [ ] Unit tests for multi-line declarations pass
- [ ] No regressions in existing test suite
- [ ] Tier 2 parse rate increases from 28% to 33% (5/18 → 6/18)

---

## Related Issues

- PR #358 - Implemented `normalize_special_identifiers()` but doesn't handle multi-line declarations
- Issue #357 - Original special chars implementation
- Similar pattern needed as multi-line set continuations issue

---

## References

- Implementation: `src/ir/preprocessor.py::normalize_special_identifiers()`
- Tests: `tests/unit/test_special_identifiers.py`
- Model: `tests/fixtures/tier2_candidates/chenery.gms`
