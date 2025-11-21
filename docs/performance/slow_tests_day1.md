# Slow Test Analysis - Sprint 9 Day 1

**Analysis Date**: 2025-11-20  
**Branch**: `sprint9-day1-test-infrastructure-part1`  
**Command**: `pytest --durations=20 -q --ignore=tests/production/test_large_models.py -m "not slow"`

## Summary

**Total Fast Test Time**: 40.42s (baseline from Day 0: 36.59s)  
**Status**: ⚠️ Slightly above 30s budget (10.42s over)  
**Tests Analyzed**: 1376 passed, 2 skipped, 11 deselected (slow tests)

## Top 20 Slowest Tests

### Tests >1s (Immediate Candidates for @pytest.mark.slow)

1. **1.44s** - `tests/e2e/test_integration.py::TestGAMSLibParsing::test_gamslib_parse_rate`
   - **Category**: GAMSLib parsing (full corpus)
   - **Action**: Mark as slow - parses entire GAMSLib corpus
   - **File**: tests/e2e/test_integration.py:268

2. **1.27s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_odd_power_warnings`
   - **Category**: CLI end-to-end test with file I/O
   - **Action**: Review - CLI tests with subprocess spawning
   - **File**: tests/integration/test_convexity_e2e.py

3. **1.23s** - `tests/integration/test_convexity_e2e.py::test_cli_output_format_with_warnings`
   - **Category**: CLI end-to-end test
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

4. **1.21s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_multiple_warnings`
   - **Category**: CLI end-to-end test
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

5. **1.20s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_does_not_block_conversion`
   - **Category**: CLI end-to-end test
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

6. **1.19s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_quotient_warnings`
   - **Category**: CLI end-to-end test
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

7. **1.14s** - `tests/integration/test_convexity_e2e.py::test_cli_specific_error_codes[nonconvex_odd_power.gms-W305]`
   - **Category**: CLI end-to-end test (parameterized)
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

8. **1.12s** - `tests/integration/test_convexity_e2e.py::test_cli_specific_error_codes[nonconvex_circle.gms-W301]`
   - **Category**: CLI end-to-end test (parameterized)
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

9. **1.10s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_warnings_nonconvex_circle`
   - **Category**: CLI end-to-end test
   - **Action**: Review
   - **File**: tests/integration/test_convexity_e2e.py

10. **1.09s** - `tests/integration/test_convexity_e2e.py::test_cli_specific_error_codes[nonconvex_trig.gms-W302]`
    - **Category**: CLI end-to-end test (parameterized)
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

11. **1.08s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_trig_warnings`
    - **Category**: CLI end-to-end test
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

12. **1.08s** - `tests/integration/test_convexity_e2e.py::test_cli_specific_error_codes[nonconvex_bilinear.gms-W303]`
    - **Category**: CLI end-to-end test (parameterized)
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

13. **1.07s** - `tests/integration/test_convexity_e2e.py::test_cli_skip_convexity_check`
    - **Category**: CLI end-to-end test
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

14. **1.06s** - `tests/integration/test_convexity_e2e.py::test_cli_specific_error_codes[nonconvex_quotient.gms-W304]`
    - **Category**: CLI end-to-end test (parameterized)
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

15. **1.06s** - `tests/integration/test_convexity_e2e.py::test_cli_convexity_bilinear_warnings`
    - **Category**: CLI end-to-end test
    - **Action**: Review
    - **File**: tests/integration/test_convexity_e2e.py

### Tests 0.5s-1s (Review on Day 2)

16. **0.69s** - `tests/research/nested_include_verification/test_nested_includes.py::test_max_depth_exceeded`
    - **Category**: Include directive edge case testing
    - **Action**: Keep for now, monitor

17. **0.54s** - `tests/validation/test_path_solver.py::TestPATHSolverValidation::test_solve_simple_nlp_mcp`
    - **Category**: PATH solver integration (requires external solver)
    - **Action**: Keep for now - validates solver integration

18. **0.53s** - `tests/validation/test_path_solver.py::TestPATHSolverValidation::test_solve_indexed_balance_mcp`
    - **Category**: PATH solver integration
    - **Action**: Keep for now

19. **0.32s** - `tests/validation/test_gams_check.py::TestGAMSValidationErrors::test_validate_with_explicit_gams_path`
    - **Category**: GAMS installation check
    - **Action**: Keep - necessary validation

20. **0.29s** - `tests/validation/test_gams_check.py::TestGAMSValidation::test_validate_simple_nlp_golden`
    - **Category**: GAMS golden file validation
    - **Action**: Keep - necessary validation

## Analysis by Category

### CLI End-to-End Tests (14 tests, ~16s total)
**Pattern**: All `test_convexity_e2e.py` tests are 1.06s-1.27s each  
**Root Cause**: Subprocess spawning + file I/O for each test  
**Recommendation for Day 2**:
- Consider marking entire `test_convexity_e2e.py` module as slow
- Alternative: Refactor to use pytest fixtures with shared CLI instance
- **Estimated savings if marked slow**: ~16s (reduces fast suite to ~24s)

### GAMSLib Corpus Parsing (1 test, 1.44s)
**Test**: `test_gamslib_parse_rate`  
**Root Cause**: Parses all GAMSLib models to compute parse rate metric  
**Recommendation for Day 2**:
- Mark as slow immediately
- **Estimated savings**: 1.44s

### PATH Solver Integration (2 tests, ~1.07s)
**Pattern**: External solver invocation  
**Recommendation**: Keep in fast suite - validates critical solver integration

### GAMS Validation (2 tests, ~0.61s)
**Pattern**: GAMS installation checks  
**Recommendation**: Keep in fast suite - necessary validation

## Recommended Actions for Day 2

### High Priority (Immediate Slow Markers)
1. ✅ Mark `test_gamslib_parse_rate` as slow (saves 1.44s)
2. ✅ Mark all `test_convexity_e2e.py` CLI tests as slow (saves ~16s)
   - **Total estimated savings**: ~17.5s
   - **Projected fast suite time**: 40.42s - 17.5s = **22.9s** ✅ (under 30s budget)

### Medium Priority (Review & Optimize)
3. Consider fixture optimization for CLI tests
4. Review nested include test for optimization opportunities

### Low Priority (Monitor)
5. PATH solver tests - acceptable for integration validation
6. GAMS validation tests - acceptable for installation checks

## Day 2 Implementation Strategy

```python
# In tests/integration/test_convexity_e2e.py - add at module level
pytestmark = pytest.mark.slow

# In tests/e2e/test_integration.py - mark specific test
@pytest.mark.slow
def test_gamslib_parse_rate():
    ...
```

## Fast Test Budget Status

**Current**: 40.42s  
**Baseline (Day 0)**: 36.59s  
**Target**: <30s  
**After Day 2 markers**: ~22.9s (projected) ✅

**Variance from Day 0**: +3.83s (likely due to new fixture generator tests: 27 tests added)

## Notes

- New fixture generator tests added 27 test cases (all fast: <0.1s each)
- Production large model tests were excluded from this run (marked slow in Sprint 8)
- All 14 convexity CLI tests follow same pattern - good candidate for batch slow marking
- Fast suite is currently healthy except for CLI subprocess overhead
