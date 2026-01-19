# Lexer Error Analysis: lexer_invalid_char

**Created:** January 18, 2026  
**Purpose:** Deep analysis of lexer_invalid_char errors to identify root causes and fix strategies  
**Related Task:** Sprint 16 Prep Task 6 - Analyze Top Parse Blockers

---

## Executive Summary

This document provides a comprehensive analysis of the 153 models (70% of 219) that fail with `lexer_invalid_char` errors. The analysis reveals that the errors are **NOT primarily caused by dollar control directives** (which are already handled), but by **advanced GAMS data syntax** that the grammar doesn't fully support.

**Key Finding:** The grammar's `$ontext/$offtext` handling works correctly. The lexer errors occur in regular GAMS syntax that uses features like:
- Hyphenated identifiers in set elements (`1964-i`, `route-1`)
- Inline descriptions in set data (`cotton-h 'cotton description'`)
- Tuple expansion syntax (`(a,b).c`)
- Mixed alphanumeric set elements

**Recommendation:** Focus on extending the grammar's set element and data handling rather than dollar control improvements.

---

## Analysis Summary

### Overall Results (219 Models)

| Category | Count | Percentage |
|----------|-------|------------|
| **Parse Success** | 59 | 27% |
| **Lexer Errors** | 153 | 70% |
| **Internal Errors** | 7 | 3% |

### Lexer Error Subcategories

| Subcategory | Count | % of Lexer Errors | Fixability | Effort |
|-------------|-------|-------------------|------------|--------|
| **Other/Complex Set Data** | 91 | 59% | Partial | High |
| Tuple syntax `(a,b).c` | 12 | 8% | Yes | Medium |
| Numeric-context issues | 11 | 7% | Yes | Medium |
| Keyword case (`Model` vs `model`) | 9 | 6% | Yes | Low |
| Operator context | 9 | 6% | Partial | Medium |
| Quoted set descriptions | 7 | 5% | Yes | Medium |
| Dot notation issues | 5 | 3% | Partial | Medium |
| Hyphenated set elements | 3 | 2% | Yes | Low |
| Abort statement syntax | 3 | 2% | Yes | Low |
| Slash/division syntax | 2 | 1% | Yes | Low |
| Hyphenated identifiers | 1 | 1% | Yes | Low |

### Internal Error Subcategories

| Subcategory | Count | Models |
|-------------|-------|--------|
| Invalid range syntax | 2 | blend, ibm1 |
| Undefined symbol | 2 | circpack, popdynm |
| Other | 3 | gqapsdp, harker, kqkpsdp |

---

## Detailed Subcategory Analysis

### 1. Complex Set Data Syntax (91 models, 59%)

**Root Cause:** GAMS allows rich data syntax in set/parameter definitions that the grammar partially supports but has edge cases.

**Patterns Found:**
- Parameter inline data with hyphenated keys: `/ hardware 8, software 9, show-biz 12 /`
- Set elements with inline descriptions: `/ cotton-h 'cotton-herbaceo' /`
- Numeric values in set context: `/ route-1 250 /`
- Compile-time variable expansion: `/ n1*n%new% /`

**Example Errors:**
```gams
* airsp2: char '2' at line 51
  / route-1 250

* alan: char '1' at line 28  
  / hardware 8, software 9, show-biz 12, t-bills 7 /;

* emfl: char '%' at line 36
  n  'total number of new facilities'    / n1*n%new%  /
```

**Fix Strategy:** 
- Extend `SET_ELEMENT_ID` terminal to better handle hyphenated identifiers with numbers
- Improve parameter data parsing for mixed alphanumeric keys
- **Effort:** High (requires grammar restructuring)
- **Sprint 16 Target:** Defer most; target ~10 models with simple patterns

---

### 2. Tuple Expansion Syntax (12 models, 8%)

**Root Cause:** GAMS supports tuple expansion in set data like `(a,b).c` which expands to `a.c, b.c`.

**Affected Models:** aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey

**Example Errors:**
```gams
* aircraft: char '(' at line 54
  k(j) 'revenue lost' / (route-1,route-2) 13, (route-3,route-4) 8 /

* clearlak: char '(' at line 42
  tw(t,w) 'relates months to weather' / (jan,feb).wet, (mar,apr,may).dry /
```

**Fix Strategy:**
- Add grammar rule for tuple expansion: `"(" id_list ")" ("." ID)?`
- **Effort:** Medium (localized grammar change)
- **Sprint 16 Target:** Yes - 12 models, well-defined syntax

---

### 3. Numeric Context Issues (11 models, 7%)

**Root Cause:** Set elements that are pure numbers or start with numbers in contexts where identifiers are expected.

**Affected Models:** decomp, kand, lands, nonsharp, pak, prodsp, prodsp2, prolog, rotdk, sam2act, tsp1

**Example Errors:**
```gams
* decomp: char '9' at line 33
  a(i) 'availability' / plant-1 9, plant-2 8 /

* kand: char '2' at line 25
  Parameter c(i) 'present cost' / raw-1 2, raw-2 3 /;
```

**Fix Strategy:**
- Improve number vs identifier disambiguation in parameter data context
- Allow numeric values after hyphenated identifiers
- **Effort:** Medium
- **Sprint 16 Target:** Yes - 11 models

---

### 4. Keyword Case Issues (9 models, 6%)

**Root Cause:** GAMS is case-insensitive, but some keywords use capital letters that conflict with identifier patterns.

**Affected Models:** ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst

**Example Errors:**
```gams
* ampl: char 'M' at line 58
  Model ampl 'maximum revenue production problem' / all /;

* apl1p: char 'V' at line 43
  Free Variable tcost 'total cost';
```

**Fix Strategy:**
- Grammar already uses case-insensitive keywords (`"Model"i`)
- Issue is context: `Free Variable` parsed as `Free` then fails on `Variable`
- Need to add `"Free"i "Variable"i` as combined keyword
- **Effort:** Low
- **Sprint 16 Target:** Yes - 9 models, simple fix

---

### 5. Operator Context Issues (9 models, 6%)

**Root Cause:** Operators (`*`, `=`) appearing in unexpected contexts, often in embedded data or special syntax.

**Affected Models:** dyncge, hhfair, hhmax, lmp1, lmp2, lmp3, phosdis, pool, splcge

**Example:** Models with embedded matrix data or specialized equation syntax.

**Fix Strategy:**
- Analyze specific patterns case-by-case
- **Effort:** Medium
- **Sprint 16 Target:** Partial - investigate top 3

---

### 6. Quoted Set Descriptions (7 models, 5%)

**Root Cause:** Set elements with inline quoted descriptions after hyphenated identifiers.

**Affected Models:** agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm

**Example Errors:**
```gams
* agreste: char ''' at line 17
  c 'crops' / cotton-h 'cotton-herbaceo', corn-g 'corn grain' /

* camcge: char ''' at line 18
  i 'sectors' / ag-subsist 'food crops', ag-export 'export crops' /
```

**Fix Strategy:**
- Extend `set_member` rule to allow `SET_ELEMENT_ID STRING`
- Already partially supported but hyphen in element breaks it
- **Effort:** Medium (combines with hyphenated element fix)
- **Sprint 16 Target:** Yes - 7 models

---

### 7. Dot Notation Issues (5 models, 3%)

**Root Cause:** Advanced dot notation in expressions or data contexts.

**Affected Models:** epscm, launch, minlphi, spatequ, srkandw

**Fix Strategy:** Case-by-case analysis needed.
**Sprint 16 Target:** Defer

---

### 8. Hyphenated Set Elements (3 models, 2%)

**Root Cause:** Set elements with hyphens like `1964-i`, `89-07`.

**Affected Models:** abel, ajax, immun

**Example:**
```gams
* abel: char '-' at line 18
  k 'horizon' / 1964-i, 1964-ii, 1964-iii, 1964-iv /
```

**Fix Strategy:**
- `SET_ELEMENT_ID` already allows hyphens: `/[a-zA-Z_][a-zA-Z0-9_+\-]*/`
- Issue: element starts with number (`1964-i`)
- Need to extend pattern to allow number-hyphen-letter
- **Effort:** Low
- **Sprint 16 Target:** Yes - 3 models

---

### 9. Abort Statement Syntax (3 models, 2%)

**Root Cause:** Complex abort statement with dollar conditions.

**Affected Models:** cclinpts, imsl, trigx

**Example:**
```gams
* cclinpts: char ',' at line 39
  abort$(b0 < 0) 'b0 should be positive', b0;
```

**Fix Strategy:**
- Extend `abort_stmt` to handle message followed by display list
- **Effort:** Low
- **Sprint 16 Target:** Yes - 3 models

---

### 10. Other Categories (< 2% each)

- **Slash/division syntax (2):** netgen, saras - edge cases
- **Hyphenated identifiers outside sets (1):** feedtray - equation with lag syntax

---

## Sprint 16 Implementation Plan

### Priority 1: Low-Effort, High-Impact (26 models)

| Fix | Models | Effort | Days |
|-----|--------|--------|------|
| Keyword case (`Free Variable`) | 9 | Low | 0.5 |
| Hyphenated set elements (number-start) | 3 | Low | 0.5 |
| Abort statement syntax | 3 | Low | 0.5 |
| Numeric context in param data | 11 | Medium | 1 |
| **Subtotal** | **26** | | **2.5 days** |

### Priority 2: Medium-Effort (19 models)

| Fix | Models | Effort | Days |
|-----|--------|--------|------|
| Tuple expansion syntax | 12 | Medium | 1.5 |
| Quoted set descriptions | 7 | Medium | 1 |
| **Subtotal** | **19** | | **2.5 days** |

### Priority 3: Defer to Future Sprints

| Category | Models | Reason |
|----------|--------|--------|
| Complex set data | 91 | Requires significant grammar work |
| Operator context | 9 | Needs case-by-case analysis |
| Dot notation | 5 | Low impact |
| Slash syntax | 2 | Edge cases |

### Expected Improvement

| Scenario | Issue Instances Fixed | New Parse Rate |
|----------|----------------------|----------------|
| **Minimum (Priority 1)** | +26 | 39% (85/219) |
| **Target (P1 + P2)** | +45 | 47% (104/219) |
| **Stretch** | +55 | 52% (114/219) |

_Note: "Issue instances fixed" may include multiple issues from the same model (e.g., srcpm appears in both Tuple Syntax and Quoted Description categories). Actual unique model counts may be slightly lower due to overlaps._

---

## Character Analysis

### Characters Causing Lexer Errors

| Character | Count | Primary Cause |
|-----------|-------|---------------|
| `'` (quote) | 25 | Inline descriptions in set data |
| `,` (comma) | 20 | Abort syntax, tuple data |
| `1` (digit) | 15 | Numeric values in set context |
| `(` (paren) | 14 | Tuple expansion syntax |
| `3` (digit) | 10 | Numeric values |
| `/` (slash) | 7 | Data delimiters |
| `*` (asterisk) | 6 | Operator/range context |
| `V` (letter) | 5 | `Variable` keyword case |
| `.` (dot) | 5 | Dot notation |
| `F` (letter) | 5 | `Free` keyword case |
| `-` (hyphen) | 4 | Hyphenated identifiers |

---

## Recommendations

### For Sprint 16

1. **Start with keyword case fixes** - Quick wins for 9 models
2. **Fix hyphenated elements starting with numbers** - 3 more models
3. **Extend abort statement grammar** - 3 more models
4. **Improve numeric handling in parameter data** - 11 models
5. **Add tuple expansion syntax** - 12 models

### For Future Sprints

1. **Comprehensive set data overhaul** - Address the 91 "complex" models
2. **Compile-time variable support** - Handle `%variable%` syntax
3. **Advanced equation syntax** - Lag/lead variations

### Testing Strategy

1. Create test cases for each subcategory before implementing fixes
2. Run regression tests after each change
3. Track parse rate improvement incrementally

---

## Appendix: Model Lists by Category

### Tuple Syntax Models (12)
aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey

### Keyword Case Models (9)
ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst

### Numeric Context Models (11)
decomp, kand, lands, nonsharp, pak, prodsp, prodsp2, prolog, rotdk, sam2act, tsp1

### Quoted Description Models (7)
agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm

### Successfully Parsing Models (59)
alkyl, bearing, camshape, catmix, chain, chakra, chem, chenery, circle, crowder, demo2, demo3, demo4, demo5, demo6, elec, ex1221, ex1222, ex1223, ex1224, ex1225, ex1226, ex1252, ex1263, ex1264, ex14_1_1, ex14_1_2, ex14_1_3, ex14_1_4, ex14_1_5, ex14_1_6, ex14_1_7, ex14_1_8, ex14_1_9, ex2_1_1, ex2_1_10, ex2_1_2, ex2_1_3, ex2_1_4, ex2_1_5, ex2_1_6, ex2_1_7, ex2_1_8, ex2_1_9, ex3_1_1, ex3_1_2, ex3_1_3, ex3_1_4, ex4_1_1, ex4_1_2, ex4_1_3, ex4_1_4, ex4_1_5, ex4_1_6, ex4_1_7, ex4_1_8, ex4_1_9, ex5_2_2_case1, ex5_2_2_case2
