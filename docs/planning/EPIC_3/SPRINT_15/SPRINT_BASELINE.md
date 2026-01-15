# Sprint 15 Baseline Metrics

**Established:** January 15, 2026  
**nlp2mcp Version:** 0.1.0  
**GAMS Version:** 51.3.0  
**PATH Solver Version:** 5.2.01  
**Total Models:** 160 (GAMSLIB verified_convex + likely_convex)

---

## Executive Summary

| Stage | Attempted | Success | Rate | Bottleneck |
|-------|-----------|---------|------|------------|
| Parse | 160 | 34 | 21.3% | lexer_invalid_char (86.5% of failures) |
| Translate | 34 | 17 | 50.0% | model_no_objective_def, diff_unsupported_func |
| Solve | 17 | 3 | 17.6% | path_syntax_error (100% of failures) |
| Compare | 3 | 1 match | 33.3% | 2 objective mismatches |

**Full Pipeline Success:** 1/160 (0.6%) - Model: hs62

---

## Parse Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Total Attempted | 160 |
| Success | 34 (21.3%) |
| Failure | 126 (78.8%) |

### Timing Statistics

| Metric | Value |
|--------|-------|
| Mean | 0.26s |
| Median | 0.15s |
| Stddev | 0.34s |
| Min | 0.02s |
| Max | 2.03s |
| P90 | 0.57s |
| P99 | 1.73s |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 94 | 26 | 27.7% |
| LP | 57 | 5 | 8.8% |
| QCP | 9 | 3 | 33.3% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| lexer_invalid_char | 109 | 86.5% |
| internal_error | 17 | 13.5% |

**Analysis:** The dominant parse blocker is `lexer_invalid_char` (109/126 failures). This indicates the lexer does not support certain GAMS syntax characters used in GAMSLIB models. The `internal_error` category (17 failures) represents parser bugs or unhandled edge cases.

---

## Translate Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Attempted | 34 |
| Success | 17 (50.0%) |
| Failure | 17 (50.0%) |
| Cascade Skip | 126 |

### Timing Statistics

| Metric | Value |
|--------|-------|
| Mean | 1.20s |
| Median | 1.01s |
| Stddev | 0.56s |
| Min | 0.78s |
| Max | 3.59s |
| P90 | 1.84s |
| P99 | 3.19s |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 26 | 14 | 53.8% |
| LP | 5 | 2 | 40.0% |
| QCP | 3 | 1 | 33.3% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| model_no_objective_def | 5 | 29.4% |
| diff_unsupported_func | 5 | 29.4% |
| unsup_index_offset | 3 | 17.6% |
| model_domain_mismatch | 2 | 11.8% |
| unsup_dollar_cond | 1 | 5.9% |
| codegen_numerical_error | 1 | 5.9% |

**Analysis:** Translation failures are more distributed across categories. Top issues:
- `model_no_objective_def` (5): Models without a defined objective function
- `diff_unsupported_func` (5): Differentiation of unsupported functions (e.g., log, exp with complex args)
- `unsup_index_offset` (3): Index expressions with +/- offsets (e.g., `x(i+1)`)

---

## Solve Stage

### Success Rate

| Metric | Value |
|--------|-------|
| Attempted | 17 |
| Success | 3 (17.6%) |
| Failure | 14 (82.4%) |
| Cascade Skip | 143 |

### Timing Statistics

| Metric | Value |
|--------|-------|
| Mean | 0.19s |
| Median | 0.16s |
| Stddev | 0.06s |
| Min | 0.15s |
| Max | 0.35s |
| P90 | 0.30s |
| P99 | 0.34s |

### Success by Model Type

| Type | Attempted | Success | Rate |
|------|-----------|---------|------|
| NLP | 14 | 2 | 14.3% |
| LP | 2 | 1 | 50.0% |
| QCP | 1 | 0 | 0.0% |

### Error Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| path_syntax_error | 14 | 100% |

**Analysis:** All 14 solve failures are due to `path_syntax_error`. This indicates the generated MCP files have GAMS syntax errors that prevent compilation. Root cause: improper element quoting in sets (e.g., `'MN''OX'` should be `'MN''''OX'`).

---

## Comparison Stage

### Results

| Metric | Value |
|--------|-------|
| Attempted | 3 |
| Match | 1 (33.3%) |
| Mismatch | 2 (66.7%) |
| Skipped | 0 |
| Cascade Skip | 157 |

### Detailed Comparison Results

| Model | NLP Objective | MCP Objective | Result | Notes |
|-------|---------------|---------------|--------|-------|
| hs62 | -26272.52 | -26272.51 | Match | diff=2.30e-03, within tolerance |
| prodmix | 18666.67 | 0.0 | Mismatch | MCP returns 0 (objective bug) |
| trig | 0.0 | -2.479 | Mismatch | Different local optima |

**Analysis:** 
- **hs62**: Full pipeline success. NLP and MCP objectives match within tolerance.
- **prodmix**: The MCP objective is incorrectly computed as 0.0 due to a bug in MCP code generation.
- **trig**: NLP found a locally optimal solution at 0.0, while MCP found the global optimum at -2.479. This is expected behavior for non-convex problems.

---

## Full Pipeline Success

Only **1 model** (hs62) completed the full pipeline successfully:

| Model | Type | Parse | Translate | Solve | Compare |
|-------|------|-------|-----------|-------|---------|
| hs62 | NLP | Success | Success | Success | Match |

**hs62 Details:**
- 4 variables, 3 equations
- NLP objective: -26272.5168
- MCP objective: -26272.5145
- Difference: 2.30e-03 (within tolerance)

---

## Key Findings

### Blockers by Impact

1. **Parse: lexer_invalid_char (109 models)**
   - GAMS syntax characters not supported by lexer
   - Highest impact blocker

2. **Solve: path_syntax_error (14 models)**
   - MCP files have GAMS compilation errors
   - Affects all models that reach solve stage

3. **Translate: model_no_objective_def (5 models)**
   - Models without explicit objective function
   - Needs handling for MCP reformulation

### Recommendations for Sprint 16+

1. **Priority 1: Fix lexer to handle more GAMS syntax**
   - Investigate the 109 `lexer_invalid_char` failures
   - Focus on the specific characters causing failures

2. **Priority 2: Fix MCP code generation for proper element quoting**
   - Address the `path_syntax_error` issue
   - Would immediately improve solve success rate

3. **Priority 3: Handle models without objective functions**
   - Decide on approach for `model_no_objective_def` cases
   - Consider using feasibility formulation

---

## Environment Details

| Component | Version |
|-----------|---------|
| nlp2mcp | 0.1.0 |
| Python | 3.12.8 |
| GAMS | 51.3.0 |
| PATH Solver | 5.2.01 (libpath52.dylib) |
| Platform | macOS Darwin 24.6.0 |

---

## Appendix: Successful Models

### Parse Success (34 models)

alkyl, bearing, chem, chenery, circle, cpack, dispatch, etamac, gastrans, himmel11, himmel16, house, hs62, hydro, least, like, markov, mathopt1, mathopt2, maxmin, mhw4d, mhw4dx, mingamma, orani, procsel, prodmix, ps10_s_ins, ps2_f_inf, rbrock, rostein, sample, topo, trig, turkey

### Translate Success (17 models)

chem, dispatch, himmel11, house, hs62, least, mathopt1, mathopt2, mhw4d, mhw4dx, port, process, prodmix, ps2_f_inf, rbrock, sample, trig

### Solve Success (3 models)

hs62, prodmix, trig

### Full Pipeline Success (1 model)

hs62
