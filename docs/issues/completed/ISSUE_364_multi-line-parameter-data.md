# Issue: Multi-line Parameter Data Declarations

**GitHub Issue:** [#364](https://github.com/jeffreyhorn/nlp2mcp/issues/364)  
**Status:** Open  
**Priority:** MEDIUM  
**Complexity:** MEDIUM (3-5h)  
**Impact:** 1 Tier 2 model (chem) + potentially others  
**Sprint:** Sprint 14+

---

## Problem Description

GAMS allows parameter data to be specified across multiple lines within `/.../ ` blocks, with continuation onto the next line without explicit line-end markers.

**Current Status:** Parser expects parameter data to be on a single line or uses implicit comma insertion (from Issue #353), but fails on certain multi-line patterns.

---

## Affected Models

### chem.gms (line 28)

**GAMS Syntax:**
```gams
Parameter
   mix(i)   'number of elements in mixture' / h 2, n 1, o 1 /
   gibbs(c) 'gibbs free energy at 3500 k and 750 psi'
            / H  -10.021, H2  -21.096, H2O -37.986, N   -9.846, N2 -28.653
              NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /
   gplus(c) 'gibbs energy plus pressure';
```

**Error:**
```
Error: Parse error at line 28, column 1: Unexpected character: 'N'
  NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /
  ^
```

**Issue:** The `gibbs(c)` parameter has data spanning lines 27-28. Parser successfully handles line 27, but fails on continuation line 28.

---

## Root Cause Analysis

### Current Grammar

**Parameter declaration:**
```lark
param_block: "Parameter"i param_decl+ SEMI
           | "Parameters"i param_decl+ SEMI

param_decl: ID domain? STRING? ("/" param_data "/")?
param_data: param_element ("," param_element)*
param_element: ID+ NUMBER
```

**Current Preprocessor:**
- `normalize_multi_line_continuations()` adds commas for set/parameter data blocks
- Only processes lines within `/.../ ` blocks that match declaration patterns
- May not handle continuation lines that don't start with indentation or specific patterns

**Suspected Issue:**
1. Line 27: `/ H  -10.021, H2  -21.096, H2O -37.986, N   -9.846, N2 -28.653`
   - Opens data block with `/`
   - Contains partial data
   - Missing closing `/`

2. Line 28: `  NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /`
   - Continuation of data block
   - Ends with closing `/`
   - Parser may not recognize this as continuation

The preprocessor's `normalize_multi_line_continuations()` should handle this, but something is failing.

---

## Investigation Steps

### 1. Verify Preprocessor Output

Run preprocessor on chem.gms and check if commas are inserted correctly:

```python
from pathlib import Path
from src.ir.preprocessor import preprocess_gams_file

content = preprocess_gams_file(Path('tests/fixtures/tier2_candidates/chem.gms'))
print(content)  # Check lines 27-28
```

### 2. Check Grammar Coverage

Verify the grammar correctly handles multi-line parameter data:
- Does `param_data` allow newlines between elements?
- Does lexer ignore `WS_INLINE` correctly?

### 3. Check Token Stream

Parse up to the error and examine the token stream:
```python
from lark import Lark

parser = Lark.open('src/gams/gams_grammar.lark')
# Try parsing just the parameter block
```

---

## Potential Solutions

### Option A: Fix Preprocessor Logic

**If Issue:** Preprocessor not detecting continuation correctly

**Fix:** Update `normalize_multi_line_continuations()` to better handle:
- Lines that don't have opening `/` but are within a data block
- Indentation patterns for continuation lines
- Parameter vs Set data blocks

**Implementation:**
```python
def normalize_multi_line_continuations(source: str) -> str:
    # Enhanced logic:
    # 1. Track if we're in a Parameter block
    # 2. When / is found, track data block state
    # 3. Process all lines until closing / is found
    # 4. Add commas at appropriate line ends
    ...
```

**Effort:** 2-3h

---

### Option B: Grammar Enhancement

**If Issue:** Grammar doesn't allow multi-line param_data

**Fix:** Ensure grammar permits newlines within `/.../ ` blocks

**Current:**
```lark
param_data: param_element ("," param_element)*
```

**Enhanced:**
```lark
param_data: param_element ("," param_element)* ","?
// Allow optional trailing comma
// WS_INLINE should be ignored automatically
```

**Note:** This may already be working if `WS_INLINE` includes newlines.

**Effort:** 1h

---

### Option C: Combination Approach

**Most Likely:** Both preprocessor and grammar need adjustments

1. Preprocessor: Ensure commas are inserted at line ends within data blocks
2. Grammar: Ensure newlines are allowed between elements
3. Parser: Verify token handling across line boundaries

**Effort:** 3-5h

---

## Recommendation

**Option C: Combination Approach** (3-5h)

**Implementation Plan:**
1. **Investigation** (1h): Run preprocessor, check output, examine token stream
2. **Preprocessor Fix** (1-2h): Update multi-line continuation logic for parameter blocks
3. **Grammar Verification** (30 min): Ensure grammar supports multi-line data
4. **Testing** (1h): Unit tests + chem.gms integration test
5. **Documentation** (30 min): Update preprocessor comments

**Rationale:**
1. **Diagnostic First**: Need to understand exact failure mode
2. **Likely Preprocessor**: Based on similar Issue #353 patterns
3. **Moderate Impact**: Unlocks 1 model immediately, likely helps others
4. **Related Work**: Builds on Issue #353 multi-line continuation work

---

## Testing Requirements

### Unit Tests

**Basic Multi-line Parameter:**
```gams
Parameter p 'test'
  / a 1, b 2
    c 3, d 4 /;
```

**Multi-line with Many Elements:**
```gams
Parameter data(i)
  / elem1 10, elem2 20, elem3 30
    elem4 40, elem5 50
    elem6 60 /;
```

**Mixed Single and Multi-line:**
```gams
Parameter
   p1 / a 1, b 2 /
   p2 'multi'
      / x 10, y 20
        z 30 /
   p3 / c 5 /;
```

**chem.gms Pattern:**
```gams
Parameter
   mix(i) / h 2, n 1, o 1 /
   gibbs(c) 'gibbs free energy'
            / H  -10.021, H2  -21.096, H2O -37.986, N   -9.846, N2 -28.653
              NH -18.918, NO -28.032 , O   -14.640, o2 -30.594, OH -26.11  /;
```

### Integration Tests

- chem.gms: Should parse past line 28 after fix

---

## Expected Impact

**Parse Rate Improvement:**
- Current: 5/18 (27%)
- After fix: 6/18 (33%)
- Improvement: +1 model (chem.gms)

**Additional Benefit:**
- May unlock other models with similar multi-line parameter patterns
- Improves robustness of preprocessor

---

## Related Issues

- **Issue #353**: Newline as Implicit Separator (completed)
  - Implemented `normalize_multi_line_continuations()`
  - Handled sets with multi-line data
  - This issue extends that work to parameter blocks

---

## References

- GAMS Documentation: Parameter Statement
- Failing model: `tests/fixtures/tier2_candidates/chem.gms` (line 28)
- Preprocessor: `src/ir/preprocessor.py` (`normalize_multi_line_continuations`)
- Grammar: `src/gams/gams_grammar.lark` (param_block, param_data rules)
- Related: Issue #353 (completed multi-line set handling)
