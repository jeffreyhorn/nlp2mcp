# Sprint 16 Baseline Analysis

**Created:** January 16, 2026  
**Sprint 15 Baseline Date:** January 15, 2026  
**Purpose:** Deep-dive analysis of Sprint 15 baseline metrics to inform Sprint 16 improvement priorities

---

## Executive Summary

Sprint 15 established comprehensive baseline metrics for the nlp2mcp pipeline on GAMSLIB. This analysis identifies key blockers, quantifies improvement potential, and provides actionable recommendations for Sprint 16.

**Key Findings:**
- **Parse stage** is the primary bottleneck: 126/160 models (78.8%) fail to parse
- **Single error category dominates:** `lexer_invalid_char` accounts for 86.5% of parse failures (109/126)
- **Solve stage has 100% single-cause failure:** All 14 solve failures are `path_syntax_error`
- **Translation failures are diverse:** 6 different error types, suggesting multiple improvement vectors
- **Full pipeline success:** Only 1 model (hs62) achieves complete success (0.6%)

**Sprint 16 Improvement Potential:**
- Fixing `lexer_invalid_char` could theoretically raise parse rate from 21.3% to 89.4%
- Realistic Sprint 16 target: +20-30% parse rate improvement (to ~40-50%)
- Focus should be on dollar control handling within `lexer_invalid_char`

---

## Baseline Metrics Summary

### Environment
- **nlp2mcp Version:** 0.1.0
- **Python:** 3.12.8
- **GAMS:** 51.3.0
- **PATH Solver:** 5.2.01
- **Platform:** Darwin 24.6.0

### Model Corpus
- **Total Models:** 160
- **Model Types:**
  - NLP: 94 (58.8%)
  - LP: 57 (35.6%)
  - QCP: 9 (5.6%)

### Pipeline Stage Success Rates

| Stage | Attempted | Success | Failure | Success Rate |
|-------|-----------|---------|---------|--------------|
| Parse | 160 | 34 | 126 | 21.3% |
| Translate | 34 | 17 | 17 | 50.0% |
| Solve | 17 | 3 | 14 | 17.6% |
| Full Pipeline | 160 | 1 | 159 | 0.6% |

### Success by Model Type

| Type | Parse Rate | Translate Rate | Solve Rate |
|------|------------|----------------|------------|
| NLP | 27.7% (26/94) | 53.9% (14/26) | 14.3% (2/14) |
| LP | 8.8% (5/57) | 40.0% (2/5) | 50.0% (1/2) |
| QCP | 33.3% (3/9) | 33.3% (1/3) | 0.0% (0/1) |

**Observation:** LP models have the lowest parse rate (8.8%), suggesting they may use more complex GAMS features or dollar control options.

---

## Parse Failure Analysis

### Error Distribution

| Error Category | Count | % of Failures | % of Total |
|----------------|-------|---------------|------------|
| `lexer_invalid_char` | 109 | 86.5% | 68.1% |
| `internal_error` | 17 | 13.5% | 10.6% |
| **Total Failures** | 126 | 100% | 78.8% |

### Analysis: lexer_invalid_char (109 models)

This is the **dominant parse blocker** and the primary target for Sprint 16 improvements.

**Assumed Subcategories (to be verified in Task 6):**
1. **Dollar control options** ($ontext, $offtext, $include, $if, $setglobal)
   - Estimated: 80-90% of lexer_invalid_char errors
   - Fix complexity: Medium (lexer mode for region skipping)
   
2. **Special characters** (non-ASCII, extended encoding)
   - Estimated: 5-10% of lexer_invalid_char errors
   - Fix complexity: Low (extend character class)
   
3. **Embedded execution commands** ($call, $execute)
   - Estimated: 5-10% of lexer_invalid_char errors
   - Fix complexity: N/A (intentional exclusion - requires GAMS runtime)

**Maximum Improvement Potential:**
- If all `lexer_invalid_char` fixed: 34 + 109 = 143 models parsing (89.4%)
- Realistic (dollar control only): 34 + 87 = 121 models (75.6%) assuming 80% are dollar control

### Analysis: internal_error (17 models)

**Characteristics:**
- These are unexpected exceptions in the parser
- May indicate grammar ambiguity or edge cases
- Lower priority than `lexer_invalid_char` due to smaller count

**Recommended Action:** Investigate after `lexer_invalid_char` is addressed to see if any are resolved as side effects.

---

## Translation Failure Analysis

### Error Distribution

| Error Category | Count | % of Failures | Description |
|----------------|-------|---------------|-------------|
| `model_no_objective_def` | 5 | 29.4% | Model has no objective function |
| `diff_unsupported_func` | 5 | 29.4% | Unsupported differentiation function |
| `unsup_index_offset` | 3 | 17.6% | Unsupported index offset syntax |
| `model_domain_mismatch` | 2 | 11.8% | Domain mismatch in model |
| `unsup_dollar_cond` | 1 | 5.9% | Unsupported dollar conditional |
| `codegen_numerical_error` | 1 | 5.9% | Numerical error in code generation |
| **Total Failures** | 17 | 100% | |

### Analysis by Category

**1. model_no_objective_def (5 models, 29.4%)**
- These models may be feasibility problems or have implicit objectives
- Sprint 16 action: Document as intentional limitation or investigate structure

**2. diff_unsupported_func (5 models, 29.4%)**
- Missing support for functions like gamma, erf, or special mathematical functions
- Sprint 16 action: Defer to Sprint 17 (Translation Improvements focus)
- Sprint 17 effort estimate: 4-6 hours per function family

**3. unsup_index_offset (3 models, 17.6%)**
- GAMS allows index arithmetic (e.g., `x(i+1)`) which requires domain analysis
- Sprint 16 action: Defer to Sprint 17
- Complexity: High (requires control flow analysis)

**4. model_domain_mismatch (2 models, 11.8%)**
- IR construction or domain inference issues
- Sprint 16 action: Investigate as potential parser-level fix

**5. unsup_dollar_cond (1 model, 5.9%)**
- Dollar conditional syntax not fully supported
- Sprint 16 action: May resolve with dollar control improvements

**6. codegen_numerical_error (1 model, 5.9%)**
- Numerical precision issue during MCP generation
- Sprint 16 action: Low priority, investigate if time permits

---

## Solve Failure Analysis

### Error Distribution

| Error Category | Count | % of Failures | Description |
|----------------|-------|---------------|-------------|
| `path_syntax_error` | 14 | 100% | PATH solver syntax error |
| **Total Failures** | 14 | 100% | |

### Analysis: path_syntax_error (14 models, 100%)

**This is notable:** All solve failures have the same root cause.

**Possible Causes:**
1. Generated MCP file has syntax errors
2. Variable/equation naming issues
3. Bounds specification problems
4. Complementarity condition formatting

**Sprint 16 Action:** Task 7 will investigate PATH syntax error patterns to determine if these are:
- nlp2mcp translation bugs (fixable)
- PATH solver limitations (document as known limitation)
- Model characteristics (convexity violations, etc.)

**Note:** The 3 successful solves (hs62 and 2 others) demonstrate that the translation-to-solve pipeline can work correctly.

---

## Comparison Stage Analysis

| Metric | Value |
|--------|-------|
| Attempted | 3 |
| Match | 1 |
| Mismatch | 2 |
| Match Rate | 33.3% |

**Observation:** Of the 3 models that solved, only 1 (hs62) matched the GAMS reference solution. The 2 mismatches may indicate:
- Numerical tolerance differences
- Different solution paths (local vs. global optima)
- Translation correctness issues

---

## Impact Ranking for Sprint 16

### Priority Matrix

| Rank | Error Category | Models | Impact | Fix Complexity | Sprint 16 Priority |
|------|----------------|--------|--------|----------------|-------------------|
| 1 | `lexer_invalid_char` (dollar control) | ~87 | Very High | Medium | **HIGH** |
| 2 | `lexer_invalid_char` (other) | ~22 | High | Low-Medium | **MEDIUM** |
| 3 | `internal_error` | 17 | Medium | Unknown | LOW |
| 4 | `path_syntax_error` | 14 | Medium | Unknown | **MEDIUM** (investigate) |
| 5 | `model_no_objective_def` | 5 | Low | N/A (model) | Skip |
| 6 | `diff_unsupported_func` | 5 | Low | High | Defer to Sprint 17 |

### Recommended Sprint 16 Targets

**Minimum Success Criteria:**
- +10% parse rate improvement (from 21.3% to 31.3%)
- 16+ additional models parsing

**Target:**
- +20% parse rate improvement (from 21.3% to 41.3%)
- 32+ additional models parsing

**Stretch Goal:**
- +30% parse rate improvement (from 21.3% to 51.3%)
- 48+ additional models parsing

---

## Unknown Verification Summary

This analysis verifies the following unknowns from KNOWN_UNKNOWNS.md:

### Unknown 4.1: lexer_invalid_char breakdown
**Status:** ✅ PARTIALLY VERIFIED

**Finding:** baseline_metrics.json shows 109 models with `lexer_invalid_char` and 17 with `internal_error`. Subcategory breakdown (dollar control vs. special chars) requires detailed analysis in Task 6.

**Key Insight:** The 86.5% concentration in a single error category suggests focused improvement is possible.

### Unknown 4.2: path_syntax_error causes  
**Status:** ✅ PARTIALLY VERIFIED

**Finding:** baseline_metrics.json shows 0 models with parse-stage `path_syntax_error` (contrary to earlier assumptions). All 14 `path_syntax_error` occurrences are at the SOLVE stage, not parse stage. This indicates PATH solver communication issues, not GAMS file path issues.

**Correction:** Unknown 4.2 assumption was that path_syntax_error is caused by "file path references in GAMS models ($include, $batinclude)". This is WRONG. The errors are actually from generated MCP files that PATH solver cannot process.

### Unknown 5.1: Translation failure breakdown
**Status:** ✅ VERIFIED

**Finding:** Translation failures are distributed across 6 categories:
- `model_no_objective_def`: 5 (29.4%)
- `diff_unsupported_func`: 5 (29.4%)
- `unsup_index_offset`: 3 (17.6%)
- `model_domain_mismatch`: 2 (11.8%)
- `unsup_dollar_cond`: 1 (5.9%)
- `codegen_numerical_error`: 1 (5.9%)

**Key Insight:** No single dominant failure category - improvements require multiple targeted fixes.

### Unknown 6.1: Solve failure breakdown
**Status:** ✅ VERIFIED

**Finding:** ALL solve failures (14/14, 100%) are `path_syntax_error`. This single-cause pattern suggests a systematic issue in MCP generation rather than diverse model problems.

**Key Insight:** Fixing the root cause could potentially unblock all 14 models simultaneously.

### Unknown 8.1: Parse blocker targets
**Status:** ✅ VERIFIED

**Finding:** Sprint 16 should target:
1. **Primary:** `lexer_invalid_char` - specifically dollar control handling
2. **Secondary:** Investigate `path_syntax_error` at solve stage
3. **Defer:** `internal_error` (may resolve with dollar control fixes)

**Key Insight:** Focused effort on dollar control could yield 50-80 additional parsing models.

---

## Recommendations

### For Sprint 16 Implementation

1. **Parser Improvements (Days 5-8):**
   - Implement $ontext/$offtext comment block skipping
   - Add $include handling (skip or treat as comment)
   - Test other dollar control options incrementally

2. **Solve Investigation (Task 7):**
   - Examine the 14 `path_syntax_error` models
   - Determine if MCP generation has systematic issues
   - Quick wins may exist if pattern is identified

3. **Reporting Infrastructure:**
   - Use this analysis format as template for automated reports
   - Include error distribution charts
   - Track improvement over baseline

### For Sprint 17 Planning

1. **Translation Improvements:**
   - `diff_unsupported_func`: Add gamma, erf, other special functions
   - `unsup_index_offset`: Implement domain analysis for index arithmetic

2. **Further Parse Improvements:**
   - Investigate remaining `internal_error` cases
   - Handle additional dollar control options as needed

---

## Appendix: Timing Analysis

### Parse Timing (34 successful models)
- Mean: 141.5 ms
- Median: 125.8 ms
- P90: 248.9 ms
- P99: 421.4 ms

### Translate Timing (17 successful models)
- Mean: 3.7 ms
- Median: 3.7 ms
- P90: 5.3 ms
- P99: 5.8 ms

### Solve Timing (3 successful models)
- Mean: 172.7 ms
- Median: 170.4 ms
- P90: 182.5 ms
- P99: 184.0 ms

**Observation:** Translation is extremely fast (~3-4ms). Parse and solve are the time-dominant stages. This suggests optimization efforts should focus elsewhere than translation performance.
