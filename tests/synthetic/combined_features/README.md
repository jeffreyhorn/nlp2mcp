# Combined Features Test Directory

**Purpose:** Synthetic GAMS models testing feature interactions  
**Sprint:** 11 Prep Task 11  
**Date:** 2025-11-26

---

## Overview

This directory contains synthetic GAMS models that combine multiple features to test for interaction bugs. Each model focuses on a specific feature pair identified as high or medium risk.

## Risk-Based Testing Strategy

### HIGH Risk (P0 - Critical)
- **functions_with_nested_indexing.gms:** Function calls + nested index expressions (✅ created)
- **bounds_with_nested_indexing.gms:** Variable bounds + nested index extraction (planned)

### MEDIUM Risk (P1 - Important)
- **functions_with_simplification.gms:** Function calls + expression simplification (planned, Sprint 11)
- **comma_separated_complex.gms:** Comma-separated declarations + complex inline expressions (planned)

### File Naming Convention

Format: `{feature1}_with_{feature2}.gms`
- Descriptive names showing feature combination
- Alphabetically sorted feature names for consistency
- Example: `functions_with_nested_indexing.gms` not `nested_indexing_with_functions.gms`

## Model Structure

Each synthetic model follows this structure:

```gams
$ontext
Feature Interaction Test: {Feature A} + {Feature B}

Purpose: {Specific interaction being tested}
Risk Level: {HIGH|MEDIUM|LOW}
Expected Behavior: {What should happen}

Sprint: 11 Prep
Date: 2025-11-26
$offtext

* Model content testing the interaction
```

## Testing Workflow

1. **Synthetic model** defines the interaction scenario
2. **Integration test** (`tests/integration/test_feature_interactions.py`) validates behavior
3. **CI pipeline** runs interaction tests on every commit
4. **PR review** verifies interaction tests for new features

## Current Test Coverage

| Feature Pair | Risk | File | Status | Test Class |
|--------------|------|------|--------|------------|
| Function Calls + Nested Indexing | HIGH | functions_with_nested_indexing.gms | ✅ Created | TestFunctionCallsWithNestedIndexing |
| Variable Bounds + Nested Indexing | HIGH | (planned) | Planned | TestVariableBoundsWithNestedIndexing |
| Function Calls + Simplification | MEDIUM | (planned) | Planned | TestFunctionCallsWithSimplification |
| Comma-Separated + Complex Expr | MEDIUM | (planned) | Planned | TestCommaSeparatedWithComplexExprs |

**Coverage:** 1/2 HIGH-risk files (50%), 0/2 MEDIUM-risk files (0%)

**Note:** Integration tests exist for all feature pairs, but only one synthetic GAMS model file is currently created. Additional synthetic models can be added as needed during Sprint 11 execution.

## Adding New Interaction Tests

See `docs/planning/EPIC_2/SPRINT_11/feature_interaction_testing_guide.md` for detailed instructions.

**Quick steps:**
1. Create `{feature1}_with_{feature2}.gms` in this directory
2. Add `$ontext` header documenting purpose and risk
3. Write model combining the features
4. Create integration test in `test_feature_interactions.py`
5. Run `make test` to verify

## References

- Testing Guide: `docs/planning/EPIC_2/SPRINT_11/feature_interaction_testing_guide.md`
- Integration Tests: `tests/integration/test_feature_interactions.py`
- Sprint 10 Retrospective: Feature interaction testing action item
- KNOWN_UNKNOWNS.md: Unknown 5.3
