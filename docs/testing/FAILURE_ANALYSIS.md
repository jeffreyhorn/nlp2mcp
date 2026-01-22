# GAMSLIB Failure Analysis Report

**Generated:** 2026-01-22
**nlp2mcp Version:** 0.1.0
**Data Source:** baseline_metrics.json
**Sprint:** 16 Day 4 - Detailed Gap Analysis

---

## Executive Summary

- **Total Models:** 160
- **Total Failures:** 157 (98.1%)
- **Unique Error Types:** 9 (high-level categories)
- **Dominant Blocker:** `lexer_invalid_char` (parse stage) - 109 models (68.1%)
- **Key Finding:** Lexer errors are NOT caused by dollar control (already handled), but by GAMS data syntax features

---

## Error Distribution by Stage

| Stage     | Failures | % of Total | Top Error                | Root Cause |
|-----------|----------|------------|--------------------------|------------|
| Parse     | 126      | 78.8%      | `lexer_invalid_char`     | Grammar gaps for GAMS data syntax |
| Translate | 17       | 10.6%      | `model_no_objective_def` | Missing features, complex constructs |
| Solve     | 14       | 8.8%       | `path_syntax_error`      | MCP code generation bugs |

---

## Parse Failures (Detailed Analysis)

**Total:** 126 failures (78.8% of attempted)

### High-Level Error Breakdown

| Category             | Count | % of Failures | Fixable | Priority Score |
|----------------------|-------|---------------|---------|----------------|
| `lexer_invalid_char` | 109   | 86.5%         | Yes     | 13.62          |
| `internal_error`     | 17    | 13.5%         | Yes     | 1.42           |

### lexer_invalid_char Subcategory Analysis

**Critical Finding:** The grammar's `$ontext/$offtext` handling already works correctly. These 109 errors occur in **regular GAMS syntax** that uses features the grammar doesn't fully support.

**Note:** A single model can appear in multiple subcategories when it exhibits multiple distinct syntax issues. Subcategory counts and percentages therefore reflect the distribution of error types, and their totals can exceed the number of unique models with `lexer_invalid_char` errors (109).

| Subcategory | Count | % of Lexer Errors | Fixability | Effort | Fix Strategy |
|-------------|-------|-------------------|------------|--------|--------------|
| Complex Set Data (hyphenated+numeric) | 91 | 59% | Partial | High | Extend SET_ELEMENT_ID |
| Tuple expansion `(a,b).c` | 12 | 8% | Yes | Medium | Add tuple_expansion rule |
| Numeric context issues | 11 | 7% | Yes | Medium | Improve num/id disambiguation |
| Keyword case (`Free Variable`) | 9 | 6% | Yes | Low | Add combined keywords |
| Operator context | 9 | 6% | Partial | Medium | Case-by-case analysis |
| Quoted set descriptions | 7 | 5% | Yes | Medium | Extend set_member rule |
| Dot notation issues | 5 | 3% | Partial | Medium | Case-by-case |
| Hyphenated set elements (number-start) | 3 | 2% | Yes | Low | Extend SET_ELEMENT_ID pattern |
| Abort statement syntax | 3 | 2% | Yes | Low | Extend abort_stmt rule |
| Slash/division syntax | 2 | 1% | Yes | Low | Edge case fixes |
| Hyphenated identifiers | 1 | 1% | Yes | Low | Minor grammar fix |

#### Character Analysis

Characters causing lexer errors:

| Character | Count | Primary Cause |
|-----------|-------|---------------|
| `'` (quote) | 25 | Inline descriptions in set data |
| `,` (comma) | 20 | Abort syntax, tuple data |
| `1`-`9` (digits) | 25+ | Numeric values in set context |
| `(` (paren) | 14 | Tuple expansion syntax |
| `/` (slash) | 7 | Data delimiters |
| `*` (asterisk) | 6 | Operator/range context |
| `V`, `F` (letters) | 10 | `Variable`, `Free` keyword case |
| `.` (dot) | 5 | Dot notation |
| `-` (hyphen) | 4 | Hyphenated identifiers |

**Note:** NO encoding issues found - all errors are standard ASCII characters in valid GAMS syntax contexts.

#### Example Errors by Subcategory

**Tuple Expansion (12 models):** aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey
```gams
* aircraft: char '(' at line 54
k(j) 'revenue lost' / (route-1,route-2) 13, (route-3,route-4) 8 /
```

**Keyword Case (9 models):** ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst
```gams
* ampl: char 'M' at line 58
Model ampl 'maximum revenue production problem' / all /;
* apl1p: char 'V' at line 43
Free Variable tcost 'total cost';
```

**Numeric Context (11 models):** decomp, kand, lands, nonsharp, pak, prodsp, prodsp2, prolog, rotdk, sam2act, tsp1
```gams
* decomp: char '9' at line 33
a(i) 'availability' / plant-1 9, plant-2 8 /
```

**Quoted Descriptions (7 models):** agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm
```gams
* agreste: char ''' at line 17
c 'crops' / cotton-h 'cotton-herbaceo', corn-g 'corn grain' /
```

**Abort Syntax (3 models):** cclinpts, imsl, trigx
```gams
* cclinpts: char ',' at line 39
abort$(b0 < 0) 'b0 should be positive', b0;
```

### internal_error Analysis

| Subcategory | Count | Models |
|-------------|-------|--------|
| Invalid range syntax | 2 | blend, ibm1 |
| Undefined symbol | 2 | circpack, popdynm |
| Other | 3 | gqapsdp, harker, kqkpsdp |

**Note:** Some internal_error cases may resolve when lexer_invalid_char fixes are applied, as they may be secondary effects.

---

## Translation Failures (Detailed Analysis)

**Total:** 17 failures (50.0% of parsed models)

### Error Breakdown

| Category                  | Count | % of Failures | Fixable | Effort | Priority Score |
|---------------------------|-------|---------------|---------|--------|----------------|
| `model_no_objective_def`  | 5     | 29.4%         | Yes*    | 1.0h   | 5.00           |
| `diff_unsupported_func`   | 5     | 29.4%         | Yes     | 6.0h   | 0.83           |
| `unsup_index_offset`      | 3     | 17.6%         | Yes     | 8.0h   | 0.38           |
| `model_domain_mismatch`   | 2     | 11.8%         | Yes     | 6.0h   | 0.33           |
| `unsup_dollar_cond`       | 1     | 5.9%          | Yes     | 6.0h   | 0.17           |
| `codegen_numerical_error` | 1     | 5.9%          | Yes     | 4.0h   | 0.25           |

*Note: `model_no_objective_def` may represent feasibility problems that intentionally lack objectives.

### Translation Failure Details

#### model_no_objective_def (5 models)
- These models may be feasibility problems or have implicit objectives
- **Sprint 16 action:** Document as known limitation; investigate if feasibility mode can be supported
- **Sprint 17 consideration:** Feasibility problem reformulation

#### diff_unsupported_func (5 models)
- Missing support for functions like `gamma`, `erf`, `betareg`, or special mathematical functions
- **Sprint 16 action:** Defer to Sprint 17 (Translation Improvements focus)
- **Sprint 17 effort estimate:** 4-6 hours per function family

#### unsup_index_offset (3 models)
- GAMS allows index arithmetic (e.g., `x(i+1)`) which requires domain analysis
- **Sprint 16 action:** Defer to Sprint 17
- **Complexity:** High (requires control flow analysis)

#### model_domain_mismatch (2 models)
- IR construction or domain inference issues
- **Sprint 16 action:** Investigate if parse improvements help

#### unsup_dollar_cond (1 model)
- Dollar conditional syntax not fully supported
- **Sprint 16 action:** May resolve with parse improvements

#### codegen_numerical_error (1 model)
- Numerical precision issue during MCP generation
- **Sprint 16 action:** Low priority edge case

### Sprint 17 Deferral Rationale

Translation fixes are deferred to Sprint 17 for the following reasons:

1. **Cascade Effect:** Parse improvements in Sprint 16 will change which models reach translation
2. **ROI:** Parse improvements unblock 109+ models vs. translation fixes affecting 17 models
3. **Dependencies:** Some translation issues may resolve with better parsing
4. **Sprint Scope:** Sprint 16 already has reporting infrastructure + parse improvements
5. **Expected Drop:** As more complex models parse, initial translation success rate may temporarily decrease

---

## Solve Failures (Detailed Analysis)

**Total:** 14 failures (82.4% of translated models)

### Error Breakdown

| Category            | Count | % of Failures | Fixable | Effort | Priority Score |
|---------------------|-------|---------------|---------|--------|----------------|
| `path_syntax_error` | 14    | 100.0%        | Yes     | 6.0h   | 2.33           |

### Critical Finding

**ALL 14 solve failures (100%) are addressable nlp2mcp bugs**, NOT inherent model difficulties or PATH solver limitations.

### path_syntax_error Root Cause Analysis

From PATH_ERROR_ANALYSIS.md, the actual errors are **GAMS compilation errors** in generated MCP files:

| GAMS Error Code | Count | Description | Root Cause |
|-----------------|-------|-------------|------------|
| 445 | 46 instances | Operator sequence | Unary minus before parentheses |
| 924 | 24 instances | MCP separator | Wrong syntax in model statement |
| 171, 340 | 14 instances | Domain/quoting | Inconsistent set element quoting |
| 145, 148 | 8 instances | Index issues | Domain propagation bugs |

### Error Categories by Pattern

**1. Unary Minus Pattern (10 models):** `-(expr)` should be `(-1)*(expr)`
- Models: himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample
- **Fix:** Update `emit_gams.py` to format unary minus correctly
- **Effort:** 2-4 hours

**2. Set Element Quoting (3 models):** Inconsistent quoting of set elements
- Models: chem, dispatch, port
- **Fix:** Ensure consistent quoting in generated code
- **Effort:** 4-6 hours

**3. Scalar Declaration (1 model):** Missing identifier name
- Model: dispatch
- **Fix:** Minor emit_gams.py fix
- **Effort:** 1-2 hours

### Expected Improvement After Fixes

| Metric | Current | After Fixes |
|--------|---------|-------------|
| Solve rate (of translated) | 17.6% (3/17) | 76-100% (13-17/17) |
| Full pipeline success | 0.6% (1/160) | Potentially 5-10% |

---

## Improvement Roadmap Summary

Based on impact analysis (Priority Score = Models Affected / Effort Hours):

### Sprint 16 Priorities (Parse + Solve)

| Priority | Error Category | Stage | Models | Effort | Score | Confidence |
|----------|----------------|-------|--------|--------|-------|------------|
| 1 | Keyword case (`Free Variable`) | Parse | 9 | 0.5d | 18.0 | High |
| 1 | Hyphenated set elements | Parse | 3 | 0.5d | 6.0 | High |
| 1 | Abort statement syntax | Parse | 3 | 0.5d | 6.0 | High |
| 1 | Unary minus formatting | Solve | 10 | 0.5d | 20.0 | High |
| 2 | Tuple expansion syntax | Parse | 12 | 1.5d | 8.0 | Medium |
| 2 | Quoted set descriptions | Parse | 7 | 1d | 7.0 | Medium |
| 3 | Numeric context in param data | Parse | 11 | 1d | 11.0 | Medium |
| 3 | Set element quoting | Solve | 3 | 0.5d | 6.0 | High |
| 3 | Scalar declaration fix | Solve | 1 | 0.25d | 4.0 | High |

### Sprint 17 Deferrals (Translation)

| Error Category | Models | Reason for Deferral |
|----------------|--------|---------------------|
| `model_no_objective_def` | 5 | Requires feasibility reformulation design |
| `diff_unsupported_func` | 5 | Requires new derivative rules (gamma, etc.) |
| `unsup_index_offset` | 3 | Requires domain arithmetic analysis |
| `model_domain_mismatch` | 2 | Requires improved domain propagation |
| `unsup_dollar_cond` | 1 | Requires conditional expression handling |
| `codegen_numerical_error` | 1 | Edge case, low priority |

---

## Success Targets

### Sprint 16 Expected Outcomes

| Level | Parse Rate | Improvement | Solve Rate | Full Pipeline |
|-------|------------|-------------|------------|---------------|
| **Minimum (P1)** | 31% | +16 models | 76% | 5% (8/160) |
| **Target (P1+P2)** | 43% | +34 models | 100% | 8% (13/160) |
| **Stretch** | 47% | +41 models | 100% | 10% (16/160) |

---

## Appendix: Model Lists by Error Category

### Parse: Tuple Syntax Models (12)
aircraft, airsp, clearlak, mine, pdi, pinene, pollut, qsambal, ramsey, srcpm, synheat, turkey

### Parse: Keyword Case Models (9)
ampl, apl1p, apl1pca, jobt, moncge, nemhaus, qfilter, wall, worst

### Parse: Numeric Context Models (11)
decomp, kand, lands, nonsharp, pak, prodsp, prodsp2, prolog, rotdk, sam2act, tsp1

### Parse: Quoted Description Models (7)
agreste, camcge, egypt, fawley, korcge, nebrazil, srcpm

### Parse: Abort Syntax Models (3)
cclinpts, imsl, trigx

### Parse: Hyphenated Elements (3)
abel, ajax, immun

### Solve: Unary Minus Models (10)
himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample

### Solve: Set Element Quoting (3)
chem, dispatch, port

### Parse: Successfully Parsing Models (34)
alkyl, bearing, camshape, catmix, chain, chakra, chem, chenery, circle, crowder, demo2, demo3, demo4, demo5, demo6, dispatch, elec, ex1221, ex1222, ex1223, ex1224, ex1225, ex1226, ex1252, ex1263, ex1264, ex14_1_1, ex14_1_2, ex14_1_3, ex14_1_4, ex14_1_5, ex14_1_6, ex14_1_7, ex14_1_8

---

*Report updated with detailed subcategory analysis from LEXER_ERROR_ANALYSIS.md and PATH_ERROR_ANALYSIS.md*
