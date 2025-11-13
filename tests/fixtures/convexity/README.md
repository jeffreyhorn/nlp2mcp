# Convexity Test Fixtures

**Purpose:** Test fixtures for convexity detection heuristics in Sprint 6  
**Created:** 2025-11-12  
**Total Models:** 13 (5 convex, 5 non-convex, 3 edge cases)

## Overview

This directory contains minimal GAMS NLP models designed to test convexity detection algorithms. Each model is carefully constructed to represent a specific convexity pattern or edge case.

## Test Model Catalog

### Convex Models (Should NOT Warn)

| Model | Description | Key Feature | Expected Result |
|-------|-------------|-------------|-----------------|
| `linear_program.gms` | Simple LP | Linear objective & constraints | CONVEX, no warning |
| `convex_qp.gms` | Quadratic program | Minimize x² + y² | CONVEX, no warning |
| `convex_exponential.gms` | Exponential objective | Minimize exp(x) + exp(y) | CONVEX, no warning |
| `convex_log_barrier.gms` | Log barrier function | Minimize -log(x) - log(y) | CONVEX, no warning |
| `convex_inequality.gms` | Convex constraints | Linear obj, x² + y² ≤ 25 | CONVEX, no warning |

**Rationale:** These models represent standard convex optimization patterns. Any convexity detector should recognize these as convex and NOT issue warnings.

### Non-Convex Models (Should Warn)

| Model | Description | Key Feature | Expected Result |
|-------|-------------|-------------|-----------------|
| `nonconvex_circle.gms` | Circle equality | x² + y² = 4 (equality) | NON-CONVEX, warn |
| `nonconvex_trig_eq.gms` | Trig equality | sin(x) + cos(y) = 0 | NON-CONVEX, warn |
| `nonconvex_bilinear.gms` | Bilinear term | Minimize x*y | NON-CONVEX, warn |
| `nonconvex_quotient.gms` | Division | Minimize x/y | NON-CONVEX, warn |
| `nonconvex_odd_power.gms` | Cubic term | Minimize x³ + y² | NON-CONVEX, warn |

**Rationale:** These models contain known non-convex features. Convexity detector should issue warnings recommending NLP solver instead of PATH.

### Edge Cases (Ambiguous or Borderline)

| Model | Description | Key Feature | Expected Result |
|-------|-------------|-------------|-----------------|
| `mixed_convex_nonconvex.gms` | Mixed problem | Convex obj, x*y = 1 (eq) | NON-CONVEX, warn (due to equality) |
| `convex_with_trig_ineq.gms` | Trig inequality | sin(x) ≤ 0.5 | AMBIGUOUS (depends on strictness) |
| `nearly_affine.gms` | Almost linear | Linear obj, x² = 4 (eq) | NON-CONVEX, warn (nonlinear eq) |

**Rationale:** These test boundary conditions and heuristic behavior. Conservative detectors may warn, permissive ones may not.

## Expected Warning Messages

Based on convexity research (Task 2), expected warning format:

```
Warning: Non-convex problem detected (line X, column Y)

Nonlinear equality constraint may cause PATH solver to fail.
The problem contains: [bilinear term / trigonometric equality / ...]

Action: Consider using NLP solver instead of PATH for MCP reformulation.
See: docs/CONVEXITY.md
```

## Model Structure

All models follow this minimal structure (< 20 lines):
1. Comment header with expected classification
2. Variable declarations
3. Equation declarations
4. Equation definitions
5. Variable bounds
6. Model and solve statements

## Usage

### Testing Convexity Detection

```python
from nlp2mcp.convexity import detect_convexity

# Test convex model (should not warn)
result = detect_convexity("tests/fixtures/convexity/linear_program.gms")
assert result.is_convex == True
assert len(result.warnings) == 0

# Test non-convex model (should warn)
result = detect_convexity("tests/fixtures/convexity/nonconvex_circle.gms")
assert result.is_convex == False
assert len(result.warnings) > 0
assert "equality" in result.warnings[0].lower()
```

### Batch Testing

```bash
# Run convexity detector on all fixtures
for model in tests/fixtures/convexity/*.gms; do
    python -m nlp2mcp.convexity "$model"
done
```

### Integration with Parser

```python
from nlp2mcp import parse_gams_file
from nlp2mcp.convexity import analyze_model_ir

# Parse model
ir = parse_gams_file("tests/fixtures/convexity/nonconvex_circle.gms")

# Analyze convexity
analysis = analyze_model_ir(ir)
print(f"Convex: {analysis.is_convex}")
print(f"Warnings: {analysis.warnings}")
```

## Validation

All models have been verified to:
- ✅ Parse successfully with current nlp2mcp parser
- ✅ Contain < 20 lines (minimal examples)
- ✅ Include expected classification in comments
- ✅ Represent distinct convexity patterns

## Convexity Detection Criteria

Based on Task 2 research, key non-convex indicators:

1. **Nonlinear Equalities** - Any nonlinear equality constraint
   - Examples: x² + y² = 4, sin(x) = 0, x*y = 1
   
2. **Non-Convex Functions in Objective**
   - Bilinear: x*y
   - Division: x/y  
   - Odd powers: x³, x⁵
   - Some trig: cos(x) when minimizing
   
3. **Non-Convex Constraint Sets**
   - Concave functions in ≤ constraints
   - Convex functions in ≥ constraints (when not flipped)

## Sprint 6 Testing Goals

1. **Baseline Accuracy**: Detect all 5 non-convex models (100% recall on obvious cases)
2. **Precision**: Don't warn on 5 convex models (0% false positive rate)
3. **Edge Case Handling**: Consistent behavior on ambiguous cases
4. **Performance**: Analyze all 13 models in <1 second

## File Manifest

```
tests/fixtures/convexity/
├── README.md                      # This file
├── linear_program.gms             # Convex: LP
├── convex_qp.gms                  # Convex: QP with x² + y²
├── convex_exponential.gms         # Convex: exp functions
├── convex_log_barrier.gms         # Convex: -log barrier
├── convex_inequality.gms          # Convex: convex inequalities
├── nonconvex_circle.gms           # Non-convex: circle equality
├── nonconvex_trig_eq.gms          # Non-convex: trig equality
├── nonconvex_bilinear.gms         # Non-convex: x*y term
├── nonconvex_quotient.gms         # Non-convex: x/y term
├── nonconvex_odd_power.gms        # Non-convex: x³ term
├── mixed_convex_nonconvex.gms     # Edge: mixed
├── convex_with_trig_ineq.gms      # Edge: trig in inequality
└── nearly_affine.gms              # Edge: almost linear
```

## Notes

- Models are intentionally minimal to isolate specific features
- All models are solvable (have feasible solutions)
- Expected classifications are documented in each .gms file header
- These fixtures complement GAMSLib models (Task 7) which are more complex

## References

- Task 2: Convexity Detection Research
- `docs/planning/EPIC_2/SPRINT_6/CONVEXITY_RESEARCH.md`
- Sprint 6 PREP_PLAN.md (Task 8)

## Version History

- **2025-11-12**: Initial fixture set (13 models)
  - 5 convex models
  - 5 non-convex models
  - 3 edge cases
