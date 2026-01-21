# GAMSLIB Failure Analysis Report

**Generated:** 2026-01-21 18:16:58 UTC
**nlp2mcp Version:** 0.1.0
**Data Source:** baseline_metrics.json

---

## Executive Summary

- **Total Models:** 160
- **Total Failures:** 157 (98.1%)
- **Unique Error Types:** 9
- **Dominant Blocker:** `lexer_invalid_char` (parse stage)

---

## Error Distribution by Stage

| Stage     |   Failures | % of Total Models   | Top Error                |
|-----------|------------|---------------------|--------------------------|
| Parse     |        126 | 78.8%               | `lexer_invalid_char`     |
| Translate |         17 | 10.6%               | `model_no_objective_def` |
| Solve     |         14 | 8.8%                | `path_syntax_error`      |

---

## Parse Failures

**Total:** 126 failures (78.8% of attempted)

### Error Breakdown

| Category             |   Count | % of Failures   | Fixable   |   Priority |
|----------------------|---------|-----------------|-----------|------------|
| `lexer_invalid_char` |     109 | 86.5%           | Yes       |      13.62 |
| `internal_error`     |      17 | 13.5%           | Yes       |       1.42 |

### lexer_invalid_char

| Metric | Value |
|--------|-------|
| Count | 109 |
| % of parse failures | 86.5% |
| % of all models | 68.1% |
| Fixable | Yes |
| Effort | 8.0h |
| Priority Score | 13.62 |

---

### internal_error

| Metric | Value |
|--------|-------|
| Count | 17 |
| % of parse failures | 13.5% |
| % of all models | 10.6% |
| Fixable | Yes |
| Effort | 12.0h |
| Priority Score | 1.42 |

---


## Translation Failures

**Total:** 17 failures (50.0% of attempted)

### Error Breakdown

| Category                  |   Count | % of Failures   | Fixable   |   Priority |
|---------------------------|---------|-----------------|-----------|------------|
| `model_no_objective_def`  |       5 | 29.4%           | Yes       |       5    |
| `diff_unsupported_func`   |       5 | 29.4%           | Yes       |       0.83 |
| `unsup_index_offset`      |       3 | 17.6%           | Yes       |       0.38 |
| `model_domain_mismatch`   |       2 | 11.8%           | Yes       |       0.33 |
| `unsup_dollar_cond`       |       1 | 5.9%            | Yes       |       0.17 |
| `codegen_numerical_error` |       1 | 5.9%            | Yes       |       0.25 |

### model_no_objective_def

| Metric | Value |
|--------|-------|
| Count | 5 |
| % of translate failures | 29.4% |
| % of all models | 3.1% |
| Fixable | Yes |
| Effort | 1.0h |
| Priority Score | 5.00 |

---

### diff_unsupported_func

| Metric | Value |
|--------|-------|
| Count | 5 |
| % of translate failures | 29.4% |
| % of all models | 3.1% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 0.83 |

---

### unsup_index_offset

| Metric | Value |
|--------|-------|
| Count | 3 |
| % of translate failures | 17.6% |
| % of all models | 1.9% |
| Fixable | Yes |
| Effort | 8.0h |
| Priority Score | 0.38 |

---

### model_domain_mismatch

| Metric | Value |
|--------|-------|
| Count | 2 |
| % of translate failures | 11.8% |
| % of all models | 1.2% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 0.33 |

---

### unsup_dollar_cond

| Metric | Value |
|--------|-------|
| Count | 1 |
| % of translate failures | 5.9% |
| % of all models | 0.6% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 0.17 |

---

### codegen_numerical_error

| Metric | Value |
|--------|-------|
| Count | 1 |
| % of translate failures | 5.9% |
| % of all models | 0.6% |
| Fixable | Yes |
| Effort | 4.0h |
| Priority Score | 0.25 |

---


## Solve Failures

**Total:** 14 failures (82.4% of attempted)

### Error Breakdown

| Category            |   Count | % of Failures   | Fixable   |   Priority |
|---------------------|---------|-----------------|-----------|------------|
| `path_syntax_error` |      14 | 100.0%          | Yes       |       2.33 |

### path_syntax_error

| Metric | Value |
|--------|-------|
| Count | 14 |
| % of solve failures | 100.0% |
| % of all models | 8.8% |
| Fixable | Yes |
| Effort | 6.0h |
| Priority Score | 2.33 |

---


## Improvement Roadmap

Based on impact analysis (Priority Score = Models / Effort), prioritized fixes:

|   Priority | Error Category            | Stage     |   Models | Effort   |   Score |
|------------|---------------------------|-----------|----------|----------|---------|
|          1 | `lexer_invalid_char`      | parse     |      109 | 8.0h     |   13.62 |
|          2 | `model_no_objective_def`  | translate |        5 | 1.0h     |    5    |
|          3 | `path_syntax_error`       | solve     |       14 | 6.0h     |    2.33 |
|          4 | `internal_error`          | parse     |       17 | 12.0h    |    1.42 |
|          5 | `diff_unsupported_func`   | translate |        5 | 6.0h     |    0.83 |
|          6 | `unsup_index_offset`      | translate |        3 | 8.0h     |    0.38 |
|          7 | `model_domain_mismatch`   | translate |        2 | 6.0h     |    0.33 |
|          8 | `codegen_numerical_error` | translate |        1 | 4.0h     |    0.25 |
|          9 | `unsup_dollar_cond`       | translate |        1 | 6.0h     |    0.17 |


---

*Report generated by `generate_report.py`*