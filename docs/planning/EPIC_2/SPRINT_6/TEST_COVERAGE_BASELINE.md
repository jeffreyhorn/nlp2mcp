# Test Coverage Baseline (Pre-Sprint 6)

**Date:** 2025-11-12  
**Purpose:** Establish baseline test coverage metrics before Sprint 6  
**Coverage Tool:** pytest-cov 7.11.0  

## Executive Summary

- **Total Tests:** 1098 (up from 1078 in Epic 1)
- **Overall Coverage:** 87%
- **Total Statements:** 4423
- **Covered Statements:** 3846
- **Missing Statements:** 577
- **Sprint 6 Target:** ≥90%

## Overall Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Total Tests | 1098 | +20 tests since Epic 1 |
| Coverage | 87% | Baseline for Sprint 6 |
| Statements | 4423 | Total executable lines |
| Covered | 3846 | Lines executed by tests |
| Missing | 577 | Lines not covered |
| Excluded | 44 | Lines marked for exclusion |

## Module Coverage Analysis

### Critical Gaps (< 70% coverage)

| Module | Coverage | Statements | Missing | Priority | Notes |
|--------|----------|------------|---------|----------|-------|
| `src/config_loader.py` | **0%** | 25 | 25 | **CRITICAL** | Completely untested |
| `src/diagnostics/matrix_market.py` | **40%** | 109 | 65 | **HIGH** | Matrix Market export feature |
| `src/logging_config.py` | **66%** | 44 | 15 | **MEDIUM** | Logging configuration |
| `src/validation/gams_check.py` | **68%** | 72 | 23 | **MEDIUM** | GAMS validation utilities |
| `src/cli.py` | **69%** | 162 | 50 | **HIGH** | CLI entry point |

### Moderate Gaps (70-85% coverage)

| Module | Coverage | Statements | Missing | Priority | Notes |
|--------|----------|------------|---------|----------|-------|
| `src/validation/numerical.py` | 70% | 64 | 19 | MEDIUM | Numerical validation |
| `src/ir/minmax_detection.py` | 77% | 120 | 28 | MEDIUM | Min/max detection |
| `src/kkt/stationarity.py` | 81% | 177 | 34 | MEDIUM | Stationarity conditions |
| `src/ir/parser.py` | 82% | 758 | 133 | HIGH | Core parser (large module) |
| `src/emit/equations.py` | 83% | 59 | 10 | LOW | Equation emission |
| `src/ad/evaluator.py` | 84% | 139 | 22 | MEDIUM | Expression evaluator |
| `src/ad/validation.py` | 84% | 70 | 11 | LOW | AD validation |

### Good Coverage (85-90% coverage)

| Module | Coverage | Statements | Missing | Priority | Notes |
|--------|----------|------------|---------|----------|-------|
| `src/emit/emit_gams.py` | 87% | 112 | 15 | LOW | GAMS emission |
| `src/validation/model.py` | 88% | 73 | 9 | LOW | Model validation |

### Excellent Coverage (>90% coverage)

Most modules have >90% coverage including:
- `src/ad/ad_core.py` - 95%
- `src/ad/api.py` - 100%
- `src/ir/__init__.py` - 100%
- And many more...

## Critical Gaps Analysis

### 1. config_loader.py (0% coverage) - CRITICAL

**Status:** Completely untested  
**Impact:** Configuration loading is a core feature  
**Statements:** 25 missing out of 25

**Recommendation:**
- **Sprint 6 Action:** Add basic config loading tests (10+ tests)
- **Target:** 80% coverage minimum
- **Tests Needed:**
  - Valid config file loading
  - Invalid config handling
  - Default config fallback
  - Config validation

### 2. diagnostics/matrix_market.py (40% coverage) - HIGH

**Status:** 65 of 109 statements uncovered  
**Impact:** Matrix export functionality for debugging

**Recommendation:**
- **Sprint 6 Action:** Add matrix market export tests
- **Target:** 70% coverage
- **Tests Needed:**
  - Export to Matrix Market format
  - Sparse matrix handling
  - Edge cases (empty matrices, single element)

### 3. cli.py (69% coverage) - HIGH

**Status:** 50 of 162 statements uncovered  
**Impact:** Command-line interface is user-facing

**Recommendation:**
- **Sprint 6 Action:** Add CLI integration tests
- **Target:** 80% coverage
- **Tests Needed:**
  - Command-line argument parsing
  - Error message formatting
  - Help text generation
  - Output file handling

### 4. ir/parser.py (82% coverage) - HIGH PRIORITY

**Status:** 133 of 758 statements uncovered (largest module)  
**Impact:** Core parser is critical for all functionality

**Recommendation:**
- **Sprint 6 Action:** Focus on parser edge cases
- **Target:** 90% coverage
- **Tests Needed:**
  - Complex indexing patterns
  - Nested structures
  - Error recovery paths
  - Table parsing edge cases

### 5. kkt/stationarity.py (81% coverage) - MEDIUM

**Status:** 34 of 177 statements uncovered  
**Impact:** Stationarity conditions for KKT reformulation

**Recommendation:**
- **Sprint 7 Action:** Add stationarity edge case tests
- **Target:** 90% coverage
- **Tests Needed:**
  - Indexed stationarity
  - Bound combinations
  - Objective variable handling

## Sprint 6 Recommendations

### High Priority (Must Do)

1. **config_loader.py** - Add basic tests (0% → 80%)
   - Estimated: 10 tests, 2 hours
   
2. **cli.py** - Add integration tests (69% → 80%)
   - Estimated: 15 tests, 3 hours
   
3. **ir/parser.py** - Add edge case tests (82% → 90%)
   - Estimated: 20 tests, 4 hours

### Medium Priority (Should Do)

4. **diagnostics/matrix_market.py** - Add export tests (40% → 70%)
   - Estimated: 8 tests, 2 hours
   
5. **validation/gams_check.py** - Add validation tests (68% → 80%)
   - Estimated: 5 tests, 1 hour

### Low Priority (Nice to Have)

6. **ir/minmax_detection.py** - Edge cases (77% → 85%)
7. **kkt/stationarity.py** - Edge cases (81% → 90%)

### Estimated Impact

If high priority items completed:
- **New Tests:** ~58 tests
- **Expected Coverage:** 87% → **90%**
- **Time Investment:** ~12 hours

## Coverage Tracking Strategy

### CI/CD Enforcement

Add to `.github/workflows/test.yml`:
```yaml
- name: Check coverage
  run: |
    pytest --cov=src --cov-fail-under=87 tests/
```

This enforces current baseline (87%) to prevent regression.

### Sprint 6 Milestones

- **Week 1:** Add config_loader tests → 88%
- **Week 2:** Add CLI tests → 89%
- **Week 3:** Add parser edge cases → 91%
- **Target:** 90%+ by end of Sprint 6

### Monitoring

Track coverage changes in each PR:
1. Run coverage in CI
2. Compare to baseline (87%)
3. Require coverage not to decrease
4. Aim for incremental improvements

## Test Suite Composition

Current 1098 tests distributed across:
- **Unit Tests:** ~800 tests
- **Integration Tests:** ~250 tests
- **Validation Tests:** ~30 tests
- **Edge Case Tests:** ~18 tests

## Known Testing Gaps

### 1. Config Loading (CRITICAL)
- No tests for configuration file parsing
- No tests for default config handling
- No tests for invalid config detection

### 2. CLI Error Handling
- Limited tests for malformed arguments
- Missing tests for file not found scenarios
- No tests for conflicting options

### 3. Parser Edge Cases
- Complex table structures
- Deeply nested indexing
- Mixed set operations
- Parameter defaults

### 4. Matrix Export
- Sparse matrix formats
- Large matrix handling
- Format validation

### 5. Numerical Validation
- Floating point edge cases
- NaN/Inf handling
- Tolerance thresholds

## Regression Prevention

### High-Risk Modules for Sprint 6

Based on Sprint 6 work (convexity detection, bug fixes):
1. **src/ir/parser.py** - Parser modifications
2. **src/kkt/stationarity.py** - KKT changes
3. **src/validation/*.py** - New validation
4. **src/cli.py** - Error message improvements

**Action:** Ensure these modules maintain/improve coverage during Sprint 6.

### Coverage Goals by Module

| Module | Current | Sprint 6 Goal |
|--------|---------|---------------|
| config_loader.py | 0% | 80% |
| cli.py | 69% | 80% |
| ir/parser.py | 82% | 90% |
| diagnostics/matrix_market.py | 40% | 70% |
| validation/gams_check.py | 68% | 80% |

## Baseline Files

- **HTML Report:** `htmlcov/index.html`
- **Coverage Data:** `.coverage`
- **This Document:** `docs/planning/EPIC_2/SPRINT_6/TEST_COVERAGE_BASELINE.md`

## Next Steps

1. **Week 1:** Add config_loader tests
2. **Week 2:** Add CLI tests
3. **Week 3:** Add parser edge cases
4. **Week 4:** Review coverage, address remaining gaps
5. **Sprint End:** Achieve ≥90% coverage

## Notes

- Coverage measured with `pytest --cov=src tests/`
- HTML report generated on 2025-11-12 18:44
- Total statements have grown from ~4200 to 4423 (+5%)
- Test count increased from 1078 to 1098 (+20 tests)
- Coverage remained stable at 87% despite code growth

## References

- Coverage report: `htmlcov/index.html`
- CI configuration: `.github/workflows/test.yml`
- Sprint 6 Plan: `docs/planning/EPIC_2/SPRINT_6/PREP_PLAN.md`
