# GAMSLIB Failure Analysis Report

**Generated:** 2026-01-28 08:18:00 UTC
**nlp2mcp Version:** 0.7.0
**Data Source:** baseline_metrics.json

---

## Executive Summary

- **Total Models:** 160
- **Total Failures:** 149 (93.1%)
- **Unique Error Types:** 11
- **Dominant Blocker:** `lexer_invalid_char` (parse stage)

---

## Error Distribution by Stage

| Stage     |   Failures | % of Total Models   | Top Error               |
|-----------|------------|---------------------|-------------------------|
| Parse     |        112 | 70.0%               | `lexer_invalid_char`    |
| Translate |         27 | 16.9%               | `model_domain_mismatch` |
| Solve     |         10 | 6.2%                | `path_syntax_error`     |

---

## Parse Failures

**Total:** 112 failures (70.0% of attempted)

### Error Breakdown

| Category                    |   Count | % of Failures   | Fixable   |   Priority |
|-----------------------------|---------|-----------------|-----------|------------|
| `lexer_invalid_char`        |      97 | 86.6%           | Yes       |      12.12 |
| `internal_error`            |      14 | 12.5%           | Yes       |       1.17 |
| `semantic_undefined_symbol` |       1 | 0.9%            | Yes       |       0.25 |

### lexer_invalid_char

| Metric | Value |
|--------|-------|
| Count | 97 |
| % of parse failures | 86.6% |
| % of all models | 60.6% |
| Fixable | Yes |
| Effort | 8.0h |
| Priority Score | 12.12 |

---

### internal_error

| Metric | Value |
|--------|-------|
| Count | 14 |
| % of parse failures | 12.5% |
| % of all models | 8.8% |
| Fixable | Yes |
| Effort | 12.0h |
| Priority Score | 1.17 |

---

### semantic_undefined_symbol

| Metric | Value |
|--------|-------|
| Count | 1 |
| % of parse failures | 0.9% |
| % of all models | 0.6% |
| Fixable | Yes |
| Effort | 4.0h |
| Priority Score | 0.25 |

---


## Translation Failures

**Total:** 27 failures (56.2% of attempted)

### Error Breakdown

| Category                  |   Count | % of Failures   | Fixable   |   Priority |
|---------------------------|---------|-----------------|-----------|------------|
| `model_domain_mismatch`   |       6 | 22.2%           | Yes       |       1    |
| `diff_unsupported_func`   |       6 | 22.2%           | Yes       |       1    |
| `model_no_objective_def`  |       5 | 18.5%           | Yes       |       5    |
| `unsup_index_offset`      |       4 | 14.8%           | Yes       |       0.5  |
| `internal_error`          |       3 | 11.1%           | Yes       |       0.25 |
| `codegen_numerical_error` |       3 | 11.1%           | Yes       |       0.75 |

### model_domain_mismatch

| Metric | Value |
|--------|-------|
| Count | 6 |
| % of translate failures | 22.2% |
| % of all models | 3.8% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 1.00 |

---

### diff_unsupported_func

| Metric | Value |
|--------|-------|
| Count | 6 |
| % of translate failures | 22.2% |
| % of all models | 3.8% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 1.00 |

---

### model_no_objective_def

| Metric | Value |
|--------|-------|
| Count | 5 |
| % of translate failures | 18.5% |
| % of all models | 3.1% |
| Fixable | Yes |
| Effort | 1.0h |
| Priority Score | 5.00 |

---

### unsup_index_offset

| Metric | Value |
|--------|-------|
| Count | 4 |
| % of translate failures | 14.8% |
| % of all models | 2.5% |
| Fixable | Yes |
| Effort | 8.0h |
| Priority Score | 0.50 |

---

### internal_error

| Metric | Value |
|--------|-------|
| Count | 3 |
| % of translate failures | 11.1% |
| % of all models | 1.9% |
| Fixable | Yes |
| Effort | 12.0h |
| Priority Score | 0.25 |

---

### codegen_numerical_error

| Metric | Value |
|--------|-------|
| Count | 3 |
| % of translate failures | 11.1% |
| % of all models | 1.9% |
| Fixable | Yes |
| Effort | 4.0h |
| Priority Score | 0.75 |

---


## Solve Failures

**Total:** 10 failures (47.6% of attempted)

### Error Breakdown

| Category                |   Count | % of Failures   | Fixable   |   Priority |
|-------------------------|---------|-----------------|-----------|------------|
| `path_syntax_error`     |       8 | 80.0%           | Yes       |       1.33 |
| `model_infeasible`      |       1 | 10.0%           | Yes       |       0.25 |
| `path_solve_terminated` |       1 | 10.0%           | Yes       |       0.25 |

### path_syntax_error

| Metric | Value |
|--------|-------|
| Count | 8 |
| % of solve failures | 80.0% |
| % of all models | 5.0% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 1.33 |

---

### model_infeasible

| Metric | Value |
|--------|-------|
| Count | 1 |
| % of solve failures | 10.0% |
| % of all models | 0.6% |
| Fixable | Yes |
| Effort | 4.0h |
| Priority Score | 0.25 |

---

### path_solve_terminated

| Metric | Value |
|--------|-------|
| Count | 1 |
| % of solve failures | 10.0% |
| % of all models | 0.6% |
| Fixable | Yes |
| Effort | 4.0h |
| Priority Score | 0.25 |

---


## Improvement Roadmap

Based on impact analysis (Priority Score = Models / Effort), prioritized fixes:

|   Priority | Error Category              | Stage     |   Models | Effort   |   Score |
|------------|-----------------------------|-----------|----------|----------|---------|
|          1 | `lexer_invalid_char`        | parse     |       97 | 8.0h     |   12.12 |
|          2 | `model_no_objective_def`    | translate |        5 | 1.0h     |    5    |
|          3 | `path_syntax_error`         | solve     |        8 | 6.0h     |    1.33 |
|          4 | `internal_error`            | parse     |       14 | 12.0h    |    1.17 |
|          5 | `model_domain_mismatch`     | translate |        6 | 6.0h     |    1    |
|          6 | `diff_unsupported_func`     | translate |        6 | 6.0h     |    1    |
|          7 | `codegen_numerical_error`   | translate |        3 | 4.0h     |    0.75 |
|          8 | `unsup_index_offset`        | translate |        4 | 8.0h     |    0.5  |
|          9 | `semantic_undefined_symbol` | parse     |        1 | 4.0h     |    0.25 |
|         10 | `internal_error`            | translate |        3 | 12.0h    |    0.25 |


---

*Report generated by `generate_report.py`*