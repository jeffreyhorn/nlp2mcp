# Sprint 16 Baseline Metrics

**Established:** January 28, 2026  
**nlp2mcp Version:** 0.7.0  
**GAMS Version:** 51.3.0  
**PATH Solver Version:** 5.2.01  
**Total Models:** 160 (GAMSLIB verified_convex + likely_convex)

---

## Executive Summary

| Stage | Attempted | Success | Rate | Bottleneck |
|-------|-----------|---------|------|------------|
| Parse | 160 | 48 | 30.0% | lexer_invalid_char (86.6% of failures) |
| Translate | 48 | 21 | 43.8% | model_domain_mismatch, diff_unsupported_func |
| Solve | 21 | 11 | 52.4% | path_syntax_error (80% of failures) |
| Compare | 11 | 5 match | 45.5% | 2 objective mismatches, 4 skipped |

**Full Pipeline Success:** 5/160 (3.1%) - Models: himmel11, hs62, mathopt1, mathopt2, rbrock

---

## Comparison with Sprint 15

| Stage | Sprint 15 | Sprint 16 | Delta | Growth |
|-------|-----------|-----------|-------|--------|
| Parse | 34/160 (21.2%) | 48/160 (30.0%) | +14 | +41% |
| Translate | 17/34 (50.0%) | 21/48 (43.8%) | +4 | +24% |
| Solve | 3/17 (17.6%) | 11/21 (52.4%) | +8 | +267% |
| Full Pipeline | 1/160 (0.6%) | 5/160 (3.1%) | +4 | +400% |

**New Full Pipeline Successes:** himmel11, mathopt1, mathopt2, rbrock

**Note:** Translate rate dropped (50% → 43.8%) but absolute count improved. This is because we now parse 14 additional harder models that also tend to fail translation. The rate drop is a statistical artifact, not a regression.

---

## Parse Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Total Attempted | 160 |
| Success | 48 (30.0%) |
| Failure | 112 (70.0%) |

### Timing Statistics (Successful Models)

| Metric | Value |
|--------|-------|
| Mean | 560.0 ms |
| Median | 310.0 ms |
| Stddev | 350.0 ms |
| Min | 100.0 ms |
| Max | 2000.0 ms |
| P90 | 1230.0 ms |
| P99 | 2000.0 ms |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 94 | 28 | 29.8% |
| LP | 57 | 16 | 28.1% |
| QCP | 9 | 4 | 44.4% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| lexer_invalid_char | 97 | 86.6% |
| internal_error | 14 | 12.5% |
| semantic_undefined_symbol | 1 | 0.9% |

**Analysis:** The dominant parse blocker remains `lexer_invalid_char` (97/112 failures, down from 109 in Sprint 15). Sprint 16 grammar improvements fixed 12 models previously blocked by lexer issues. The `internal_error` category dropped from 17 to 14.

**Sprint 16 Improvements:**
- FREE_K keyword support (+1 model: jobt)
- Abort statement with display list (+1 model: cclinpts)
- Tuple expansion syntax for parameter data
- Extended range expressions for hyphenated identifiers
- Multi-line equation continuation support

---

## Translate Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Attempted | 48 |
| Success | 21 (43.8%) |
| Failure | 27 (56.2%) |
| Cascade Skip | 112 |

### Timing Statistics (Successful Models)

| Metric | Value |
|--------|-------|
| Mean | 1670.0 ms |
| Median | 1240.0 ms |
| Stddev | 800.0 ms |
| Min | 500.0 ms |
| Max | 3500.0 ms |
| P90 | 2260.0 ms |
| P99 | 3500.0 ms |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 28 | 14 | 50.0% |
| LP | 16 | 6 | 37.5% |
| QCP | 4 | 1 | 25.0% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| model_domain_mismatch | 6 | 22.2% |
| diff_unsupported_func | 6 | 22.2% |
| model_no_objective_def | 5 | 18.5% |
| unsup_index_offset | 4 | 14.8% |
| internal_error | 3 | 11.1% |
| codegen_numerical_error | 3 | 11.1% |

**Analysis:** Translation failures are distributed across categories. Top issues remain:
- `model_domain_mismatch` (6): Incompatible index domains in expressions
- `diff_unsupported_func` (6): Differentiation of unsupported functions
- `model_no_objective_def` (5): Models without a defined objective function

---

## Solve Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Attempted | 21 |
| Success | 11 (52.4%) |
| Failure | 10 (47.6%) |
| Cascade Skip | 139 |

### Timing Statistics (Successful Models)

| Metric | Value |
|--------|-------|
| Mean | 290.0 ms |
| Median | 300.0 ms |
| Stddev | 50.0 ms |
| Min | 200.0 ms |
| Max | 400.0 ms |
| P90 | 350.0 ms |
| P99 | 400.0 ms |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 14 | 7 | 50.0% |
| LP | 6 | 3 | 50.0% |
| QCP | 1 | 1 | 100.0% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| path_syntax_error | 8 | 80.0% |
| model_infeasible | 1 | 10.0% |
| path_solve_terminated | 1 | 10.0% |

**Analysis:** Solve failures dropped significantly (14 → 10). The dominant issue remains `path_syntax_error` (8 failures, down from 14). 

**Sprint 16 Improvements:**
- Unary minus formatting: `-(expr)` → `((-1) * (expr))`
- Negative constant handling: `y * -1` → `y * (-1)`
- Set element quoting consistency
- Scalar declaration edge case fix

---

## Comparison Stage

### Results

| Metric | Value |
|--------|-------|
| Attempted | 11 |
| Match | 5 (45.5%) |
| Mismatch | 2 (18.2%) |
| Skipped | 4 (36.4%) |
| Cascade Skip | 149 |

### Detailed Comparison Results

| Model | NLP Objective | MCP Objective | Result | Notes |
|-------|---------------|---------------|--------|-------|
| himmel11 | -30665.5 | -30665.5 | Match | Within tolerance |
| hs62 | -26272.52 | -26272.51 | Match | diff=2.30e-03, within tolerance |
| mathopt1 | 1.0 | 1.0 | Match | Exact match |
| mathopt2 | 0.0 | 0.0 | Match | Exact match |
| rbrock | ~0 | ~0 | Match | Rosenbrock function minimum |
| prodmix | 18666.67 | 0.0 | Mismatch | MCP returns 0 (objective bug) |
| trig | 0.0 | -2.479 | Mismatch | Different local optima |
| apl1p, blend, mhw4d, mhw4dx | N/A | N/A | Skipped | MCP objective not available |

---

## Full Pipeline Success

**5 models** completed the full pipeline successfully:

| Model | Type | Parse | Translate | Solve | Compare |
|-------|------|-------|-----------|-------|---------|
| himmel11 | NLP | Success | Success | Success | Match |
| hs62 | NLP | Success | Success | Success | Match |
| mathopt1 | NLP | Success | Success | Success | Match |
| mathopt2 | NLP | Success | Success | Success | Match |
| rbrock | NLP | Success | Success | Success | Match |

---

## Key Improvements in Sprint 16

### Grammar Improvements (Parse Stage)

| Fix | Change | Models Impacted |
|-----|--------|-----------------|
| FREE_K keyword | Added to var_kind rule | jobt |
| Abort with display list | Extended abort_base | cclinpts |
| Tuple expansion | Added param_data_tuple_expansion | pollut |
| Hyphenated range bounds | Extended range_bound | (enables other fixes) |
| Quoted set descriptions | STRING STRING in set_member | (agreste, etc.) |

### Code Generation Improvements (Solve Stage)

| Fix | Error | Change | Impact |
|-----|-------|--------|--------|
| S-1 | 445 | `-(expr)` → `((-1) * (expr))` | ~10 models |
| S-1b | 445 | `y * -1` → `y * (-1)` | Additional patterns |
| S-2 | 171, 340 | Consistent element quoting | 3 models |
| S-3 | 409 | Filter invalid scalar names | 1 model |

### Error Category Improvements

| Category | Sprint 15 | Sprint 16 | Change |
|----------|-----------|-----------|--------|
| lexer_invalid_char | 109 | 97 | -12 |
| internal_error (parse) | 17 | 14 | -3 |
| path_syntax_error | 14 | 8 | -6 |

---

## Remaining Blockers (Priority Order)

### Parse (112 failures)

| Category | Count | % | Priority |
|----------|-------|---|----------|
| lexer_invalid_char | 97 | 86.6% | High |
| internal_error | 14 | 12.5% | Medium |
| semantic_undefined_symbol | 1 | 0.9% | Low |

### Translate (27 failures)

| Category | Count | % | Priority |
|----------|-------|---|----------|
| model_domain_mismatch | 6 | 22.2% | Medium |
| diff_unsupported_func | 6 | 22.2% | Medium |
| model_no_objective_def | 5 | 18.5% | Medium |
| unsup_index_offset | 4 | 14.8% | Low |
| internal_error | 3 | 11.1% | Low |
| codegen_numerical_error | 3 | 11.1% | Low |

### Solve (10 failures)

| Category | Count | % | Priority |
|----------|-------|---|----------|
| path_syntax_error | 8 | 80.0% | High |
| model_infeasible | 1 | 10.0% | N/A |
| path_solve_terminated | 1 | 10.0% | Medium |

---

## Recommendations for Sprint 17

1. **Priority 1: Continue addressing lexer_invalid_char**
   - Still 97 models blocked
   - Focus on complex set data syntax patterns

2. **Priority 2: Fix remaining path_syntax_error issues**
   - 8 models blocked
   - Investigate remaining MCP syntax generation bugs

3. **Priority 3: Address translation blockers**
   - model_domain_mismatch: 6 models
   - diff_unsupported_func: 6 models

---

## Environment Details

| Component | Version |
|-----------|---------|
| nlp2mcp | 0.7.0 |
| Python | 3.12.8 |
| GAMS | 51.3.0 |
| PATH Solver | 5.2.01 (libpath52.dylib) |
| Platform | macOS Darwin 24.6.0 |

---

## Appendix: Successful Models

### Parse Success (48 models)

abel, aircraft, ajax, alkyl, apl1p, bearing, blend, cclinpts, chem, chenery, circle, cpack, decomp, dispatch, gastrans, himmel11, himmel16, house, hs62, hydro, ibm1, jobt, least, like, markov, mathopt1, mathopt2, maxmin, mexss, mhw4d, mhw4dx, mingamma, orani, pak, pollut, port, process, prodmix, ps2_f_inf, qabel, ramsey, rbrock, robert, sample, trig, trnsport, trussm, whouse

### Translate Success (21 models)

ajax, apl1p, blend, chem, dispatch, himmel11, house, hs62, least, mathopt1, mathopt2, mhw4d, mhw4dx, port, process, prodmix, ps2_f_inf, rbrock, sample, trig, trnsport

### Solve Success (11 models)

apl1p, blend, himmel11, hs62, mathopt1, mathopt2, mhw4d, mhw4dx, prodmix, rbrock, trig

### Full Pipeline Success (5 models)

himmel11, hs62, mathopt1, mathopt2, rbrock
