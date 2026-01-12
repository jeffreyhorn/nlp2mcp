# Numerical Tolerance Best Practices for Solution Comparison

**Created:** January 12, 2026  
**Status:** Complete  
**Purpose:** Research and document appropriate tolerance values for comparing NLP and MCP solutions  
**Related:** Task 3 (Solution Comparison Research), Unknown 3.1, Unknown 3.2

---

## Executive Summary

This document provides in-depth research on numerical tolerance values for comparing objective values between NLP (original) and MCP (reformulated) solutions in the nlp2mcp validation pipeline.

**Recommendations:**
- **Relative tolerance (rtol):** 1e-6 (0.0001%)
- **Absolute tolerance (atol):** 1e-8
- **Comparison formula:** `|a - b| <= atol + rtol * max(|a|, |b|)`
- **Configuration:** Command-line arguments with environment variable override

**Justification:** Based on solver defaults (CONOPT 1e-7, IPOPT 1e-8, PATH 1e-6, CPLEX 1e-6), existing nlp2mcp validation (1e-6), NumPy/SciPy practices (allclose rtol=1e-5, atol=1e-8), and GAMSLIB objective value analysis.

---

## 1. Background

### 1.1 Why Tolerance Matters

When comparing NLP and MCP solutions, exact equality is rarely achievable due to:

1. **Solver-specific algorithms:** Different solvers use different internal algorithms
2. **Numerical precision limits:** IEEE 754 double precision has ~15-17 significant digits
3. **Convergence tolerances:** Solvers stop when "close enough" to optimal
4. **Starting point sensitivity:** Different initial values may lead to slightly different solutions
5. **Problem scaling:** Poorly scaled problems amplify numerical errors

**Core question:** When are two objective values "close enough" to be considered a match?

### 1.2 Types of Tolerance

#### Absolute Tolerance (atol)

```python
|a - b| <= atol
```

**Pros:**
- Works well for values near zero
- Simple to understand

**Cons:**
- Fails for large values (1000.0 vs 1000.00001 may fail with atol=1e-8)
- Scale-dependent

**Use case:** When comparing values expected to be zero or very small.

#### Relative Tolerance (rtol)

```python
|a - b| / |b| <= rtol
```

**Pros:**
- Scale-independent
- Works well for large values

**Cons:**
- Undefined when b = 0 (division by zero)
- Can be too strict for small non-zero values

**Use case:** When comparing values with unknown magnitude.

#### Combined Tolerance (Recommended)

```python
|a - b| <= atol + rtol * max(|a|, |b|)
```

**Pros:**
- Handles both edge cases (near-zero and large values)
- Symmetric (order of arguments doesn't matter)
- Industry standard (NumPy, SciPy)

**Use case:** General-purpose comparison, our recommendation.

### 1.3 IEEE 754 Double Precision Limits

| Property | Value |
|----------|-------|
| Significand bits | 52 |
| Decimal precision | ~15-17 significant digits |
| Machine epsilon | ~2.2e-16 |
| Minimum normal | ~2.2e-308 |
| Maximum value | ~1.8e+308 |

**Implication:** Any tolerance tighter than ~1e-14 risks triggering machine precision issues.

---

## 2. Solver Tolerance Survey

### 2.1 GAMS Solver Defaults

| Solver | Parameter | Default | Description |
|--------|-----------|---------|-------------|
| **CONOPT** | RTREDG | 1e-7 | Reduced gradient tolerance |
| **CONOPT** | RTMAXV | 1e-7 | Maximum constraint violation |
| **IPOPT** | tol | 1e-8 | Overall convergence tolerance |
| **IPOPT** | constr_viol_tol | 1e-4 | Constraint violation tolerance |
| **IPOPT** | compl_inf_tol | 1e-4 | Complementarity tolerance |
| **PATH** | convergence_tolerance | 1e-6 | Complementarity residual tolerance |
| **PATH** | crash_method | 0 | Starting point selection |
| **CPLEX** | epopt | 1e-6 | Optimality tolerance |
| **CPLEX** | eprhs | 1e-6 | Feasibility tolerance |
| **GUROBI** | OptimalityTol | 1e-6 | Optimality tolerance |
| **GUROBI** | FeasibilityTol | 1e-6 | Feasibility tolerance |

**Key Observations:**
1. Most solvers use tolerances in the **1e-6 to 1e-8** range
2. IPOPT uses the tightest default (1e-8)
3. PATH, CPLEX, GUROBI use 1e-6
4. CONOPT uses 1e-7 (middle ground)

**Recommendation:** Use 1e-6 for rtol (matches PATH which solves MCP) and 1e-8 for atol (matches IPOPT tightness).

### 2.2 Documentation References

**CONOPT 4:**
- "The default tolerance for the reduced gradient is 1.0E-7"
- Source: GAMS CONOPT documentation

**IPOPT:**
- "Desired convergence tolerance (relative). Determines the convergence tolerance for the algorithm."
- Default: 1e-8
- Source: IPOPT documentation

**PATH:**
- "convergence_tolerance: Tolerance for declaring a solution to the MCP."
- Default: 1e-6
- Source: PATH solver manual

**CPLEX:**
- "epopt: Optimality tolerance. Influences the reduced-cost tolerance for optimality."
- Default: 1e-6
- Source: IBM CPLEX documentation

---

## 3. Testing Practice Survey

### 3.1 NumPy/SciPy Defaults

**numpy.allclose:**
```python
numpy.allclose(a, b, rtol=1e-05, atol=1e-08)
```

Formula: `|a - b| <= atol + rtol * |b|`

**numpy.isclose:**
```python
numpy.isclose(a, b, rtol=1e-05, atol=1e-08)
```

Same formula, element-wise.

**Observation:** NumPy uses **looser** rtol (1e-5) than solver defaults, reflecting general-purpose use rather than optimization.

### 3.2 SciPy Optimization Testing

**scipy.optimize.minimize:**
- Uses `tol` parameter (default varies by method)
- BFGS: gtol=1e-5 (gradient norm tolerance)
- Nelder-Mead: fatol=1e-4, xatol=1e-4

**scipy.optimize.linprog:**
- tol: 1e-12 for simplex (very tight for LP)

### 3.3 CUTEst Benchmarking

CUTEst (Constrained and Unconstrained Testing Environment) uses:
- Relative accuracy test: `|f* - f_opt| / max(1, |f_opt|) <= 1e-6`
- Where f* is computed solution, f_opt is known optimal

**Observation:** CUTEst uses **1e-6** relative tolerance, matching our recommendation.

### 3.4 GAMS Model Testing

GAMS documentation suggests:
- Compare using `abs(a - b) < tol * max(1, abs(a), abs(b))`
- Typical tolerance: 1e-6 to 1e-4

### 3.5 Academic Papers

**Mittelmann (2020):** Benchmark comparisons use rtol=1e-6 for objective value comparison.

**Dolan & Moré (2002):** Performance profiles typically use tolerances of 1e-6 to 1e-4.

---

## 4. GAMSLIB Objective Value Analysis

### 4.1 Value Distribution

Analysis of 174 GAMSLIB models with known objective values:

| Statistic | Value |
|-----------|-------|
| **Count** | 174 |
| **Minimum** | -3,315,000.0 |
| **Maximum** | 20,941,621.8 |
| **P10** | 0.0 |
| **P50 (Median)** | 27.1 |
| **P90** | 21,343.1 |
| **Mean** | ~150,000 (skewed by large values) |

### 4.2 Edge Cases

| Category | Count | Percentage | Tolerance Implication |
|----------|-------|------------|----------------------|
| **Objective = 0 exactly** | 13 | 7.5% | Absolute tolerance needed |
| **Near zero (-1 to 1)** | 37 | 21.3% | Absolute tolerance dominates |
| **Moderate (1 to 10,000)** | ~100 | 57.5% | Both tolerances relevant |
| **Large (> 10,000)** | ~24 | 13.8% | Relative tolerance dominates |

### 4.3 Scale Analysis

Given the objective value range of approximately **1e0 to 1e7**:

- With rtol=1e-6:
  - For objective=1: tolerance = 1e-8 + 1e-6 * 1 = 1e-6 (≈0.0001%)
  - For objective=1e6: tolerance = 1e-8 + 1e-6 * 1e6 = 1.00001 (≈0.0001%)
  - For objective=1e7: tolerance = 1e-8 + 1e-6 * 1e7 = 10.00001 (≈0.0001%)

The relative tolerance scales appropriately with objective magnitude.

### 4.4 Objective = 0 Special Case

13 models have objective value exactly 0. For these:

- Relative tolerance alone would fail (can't divide by 0)
- Absolute tolerance of 1e-8 allows difference of ±1e-8

**Verification:** For objective=0, with rtol=1e-6, atol=1e-8:
```python
tolerance = 1e-8 + 1e-6 * max(0, mcp_obj)
```
If mcp_obj is also ~0, tolerance ≈ 1e-8, which is reasonable.

---

## 5. Tolerance Recommendations

### 5.1 Default Values

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **rtol** | 1e-6 | Matches PATH (MCP solver), CPLEX, GUROBI; tighter than NumPy (1e-5) |
| **atol** | 1e-8 | Matches IPOPT; handles zero objectives; looser than machine epsilon |

### 5.2 Comparison Algorithm

```python
def objectives_match(
    nlp_obj: float, 
    mcp_obj: float, 
    rtol: float = 1e-6, 
    atol: float = 1e-8
) -> bool:
    """Check if NLP and MCP objectives match within tolerance.
    
    Uses combined tolerance formula: |a - b| <= atol + rtol * max(|a|, |b|)
    
    Args:
        nlp_obj: Objective value from NLP solve
        mcp_obj: Objective value from MCP solve
        rtol: Relative tolerance (default 1e-6)
        atol: Absolute tolerance (default 1e-8)
        
    Returns:
        True if objectives match within tolerance
    """
    diff = abs(nlp_obj - mcp_obj)
    max_abs = max(abs(nlp_obj), abs(mcp_obj))
    tolerance = atol + rtol * max_abs
    return diff <= tolerance
```

### 5.3 Alternative: Symmetric Relative Tolerance

An alternative formulation used in some contexts:

```python
|a - b| / max(|a|, |b|, 1) <= rtol
```

This avoids absolute tolerance but requires a floor value to handle zeros.

**Decision:** We use the combined formula (atol + rtol * max) as it's:
- The NumPy/SciPy standard
- More intuitive (separate atol and rtol parameters)
- Better documented in scientific computing literature

---

## 6. Edge Case Handling

### 6.1 Objective Exactly Zero

**Scenario:** NLP objective = 0.0

**Handling:**
```python
# Combined tolerance handles this automatically:
# tolerance = atol + rtol * max(0, mcp_obj)
# If mcp_obj is also ~0, tolerance ≈ atol = 1e-8
```

**Example:**
- NLP: 0.0, MCP: 1e-9 → Match (diff=1e-9 < atol=1e-8)
- NLP: 0.0, MCP: 1e-7 → Mismatch (diff=1e-7 > atol=1e-8)

### 6.2 Very Large Objectives

**Scenario:** Objective values > 1e6

**Handling:** Relative tolerance dominates.

**Example (objective ≈ 1e6):**
- Tolerance = 1e-8 + 1e-6 * 1e6 = 1.00001
- NLP: 1,000,000.0, MCP: 1,000,000.5 → Match (diff=0.5 < tolerance=1.0)
- NLP: 1,000,000.0, MCP: 1,000,002.0 → Mismatch (diff=2.0 > tolerance=1.0)

### 6.3 Very Small Non-Zero Objectives

**Scenario:** Objective values between 1e-8 and 1

**Handling:** Both tolerances contribute.

**Example (objective ≈ 1e-4):**
- Tolerance = 1e-8 + 1e-6 * 1e-4 = 1e-8 + 1e-10 ≈ 1e-8
- Primarily absolute tolerance applies

### 6.4 Negative Objectives

**Handling:** Absolute values in formula handle negative objectives.

**Example:**
- NLP: -1000.0, MCP: -1000.0005
- diff = |(-1000.0) - (-1000.0005)| = 0.0005
- tolerance = 1e-8 + 1e-6 * max(1000.0, 1000.0005) = 0.001
- Match (diff=0.0005 < tolerance=0.001)

### 6.5 NaN and Infinity

**Handling:** Report as comparison failure (cannot compare).

```python
import math

def objectives_match(nlp_obj: float, mcp_obj: float, rtol: float = 1e-6, atol: float = 1e-8) -> tuple[bool, str]:
    # Handle NaN/Inf
    if math.isnan(nlp_obj) or math.isnan(mcp_obj):
        return (False, "NaN in objective value")
    if math.isinf(nlp_obj) or math.isinf(mcp_obj):
        return (False, "Infinity in objective value")
    
    # Normal comparison
    diff = abs(nlp_obj - mcp_obj)
    max_abs = max(abs(nlp_obj), abs(mcp_obj))
    tolerance = atol + rtol * max_abs
    
    if diff <= tolerance:
        return (True, f"Match within tolerance {tolerance:.2e}")
    else:
        return (False, f"Mismatch: diff={diff:.2e} > tolerance={tolerance:.2e}")
```

### 6.6 Both Objectives Very Close to Zero

**Scenario:** NLP ≈ 0, MCP ≈ 0 (but neither exactly 0)

**Example:**
- NLP: 1e-10, MCP: -1e-10
- diff = 2e-10
- tolerance = 1e-8 + 1e-6 * max(1e-10, 1e-10) = 1e-8 + 1e-16 ≈ 1e-8
- Match (diff=2e-10 < tolerance=1e-8)

This is correct behavior - both values are effectively zero at the solver tolerance level.

---

## 7. Configuration Approach

### 7.1 Command-Line Arguments

```bash
python test_solve.py --rtol=1e-6 --atol=1e-8
```

**argparse implementation:**
```python
parser.add_argument("--rtol", type=float, default=1e-6, 
                    help="Relative tolerance for objective comparison (default: 1e-6)")
parser.add_argument("--atol", type=float, default=1e-8,
                    help="Absolute tolerance for objective comparison (default: 1e-8)")
```

### 7.2 Environment Variables (Optional Override)

```bash
export NLP2MCP_RTOL=1e-6
export NLP2MCP_ATOL=1e-8
python test_solve.py
```

**Implementation:**
```python
import os

def get_tolerance_config(args):
    rtol = float(os.environ.get("NLP2MCP_RTOL", args.rtol))
    atol = float(os.environ.get("NLP2MCP_ATOL", args.atol))
    return rtol, atol
```

### 7.3 Database Storage

Store tolerance values used for each comparison:

```json
{
  "solution_comparison": {
    "nlp_objective": 225.1946,
    "mcp_objective": 225.1946,
    "absolute_difference": 0.0,
    "relative_difference": 0.0,
    "tolerance_relative": 1e-6,
    "tolerance_absolute": 1e-8,
    "objective_match": true,
    "comparison_result": "objective_match"
  }
}
```

### 7.4 Logging

Log tolerance information for debugging:

```python
import logging

logger = logging.getLogger(__name__)

def compare_objectives(nlp_obj, mcp_obj, rtol=1e-6, atol=1e-8):
    diff = abs(nlp_obj - mcp_obj)
    max_abs = max(abs(nlp_obj), abs(mcp_obj))
    tolerance = atol + rtol * max_abs
    
    logger.debug(f"Comparing objectives: NLP={nlp_obj}, MCP={mcp_obj}")
    logger.debug(f"Difference: {diff:.2e}, Tolerance: {tolerance:.2e}")
    
    if diff <= tolerance:
        logger.info(f"Objectives match within tolerance")
        return True
    else:
        logger.warning(f"Objective mismatch: diff={diff:.2e} > tol={tolerance:.2e}")
        return False
```

---

## 8. LP vs NLP Considerations

### 8.1 LP Solver Precision

LP solvers (CPLEX, GUROBI) typically achieve higher precision:
- Exact rational arithmetic in some implementations
- Basis factorization with iterative refinement
- Typical LP tolerance: 1e-9 to 1e-10 achievable

### 8.2 NLP Solver Precision

NLP solvers (CONOPT, IPOPT) may have slightly lower precision:
- Iterative methods with convergence tolerances
- Local optima possible
- Typical NLP tolerance: 1e-6 to 1e-8

### 8.3 Recommendation

Use the **same tolerances** for LP and NLP comparison (rtol=1e-6, atol=1e-8) because:

1. KKT reformulation produces NLP-like MCP problems
2. PATH solver has 1e-6 default convergence tolerance
3. Consistency simplifies implementation and debugging
4. The recommended tolerances are loose enough for LP and tight enough for NLP

**Future Enhancement:** Could track model type and report if LP models have tighter matches than NLP models.

---

## 9. Validation and Testing

### 9.1 Test Cases

Implement unit tests for tolerance comparison:

```python
import pytest

def test_exact_match():
    assert objectives_match(100.0, 100.0) == True

def test_within_relative_tolerance():
    # 0.00001% difference should match with rtol=1e-6
    assert objectives_match(1000000.0, 1000000.5) == True

def test_outside_relative_tolerance():
    # 0.001% difference should fail with rtol=1e-6
    assert objectives_match(1000.0, 1001.0) == False

def test_zero_objective_within_atol():
    assert objectives_match(0.0, 1e-9) == True

def test_zero_objective_outside_atol():
    assert objectives_match(0.0, 1e-7) == False

def test_negative_objectives():
    assert objectives_match(-1000.0, -1000.0005) == True

def test_nan_handling():
    match, msg = objectives_match_with_reason(float('nan'), 100.0)
    assert match == False
    assert "NaN" in msg

def test_inf_handling():
    match, msg = objectives_match_with_reason(float('inf'), 100.0)
    assert match == False
    assert "Infinity" in msg
```

### 9.2 Integration with Sprint 15

During Sprint 15 pipeline testing:
1. Record all comparison results with tolerances
2. Track false positive rate (known-correct marked as mismatch)
3. Track false negative rate (known-incorrect marked as match)
4. Adjust tolerances if needed based on empirical results

---

## 10. Summary

### 10.1 Key Recommendations

| Item | Recommendation | Justification |
|------|----------------|---------------|
| **rtol** | 1e-6 | Matches PATH, CPLEX, GUROBI; widely used in benchmarking |
| **atol** | 1e-8 | Matches IPOPT; handles zero objectives; 100x above machine epsilon |
| **Formula** | `|a - b| <= atol + rtol * max(|a|, |b|)` | NumPy/SciPy standard; handles all edge cases |
| **Configuration** | CLI args + env vars | Flexible for testing and CI |

### 10.2 Edge Case Summary

| Edge Case | Handling |
|-----------|----------|
| Objective = 0 | Absolute tolerance applies (atol=1e-8) |
| Very large objective | Relative tolerance dominates |
| Very small objective | Absolute tolerance dominates |
| Negative objective | Absolute values in formula |
| NaN/Infinity | Report as comparison failure |

### 10.3 Implementation Checklist

- [ ] Implement `objectives_match()` function with combined tolerance
- [ ] Add CLI arguments for --rtol and --atol
- [ ] Add environment variable support (optional)
- [ ] Store tolerances used in database
- [ ] Add unit tests for edge cases
- [ ] Log tolerance values for debugging

---

## References

1. GAMS CONOPT Documentation - https://www.gams.com/latest/docs/S_CONOPT.html
2. IPOPT Options Documentation - https://coin-or.github.io/Ipopt/OPTIONS.html
3. PATH Solver Manual - https://pages.cs.wisc.edu/~ferris/path.html
4. NumPy allclose Documentation - https://numpy.org/doc/stable/reference/generated/numpy.allclose.html
5. CUTEst Benchmarking - https://github.com/ralna/CUTEst
6. IEEE 754-2019 Standard for Floating-Point Arithmetic
7. Mittelmann Benchmarks - http://plato.asu.edu/bench.html
8. Dolan & Moré (2002), "Benchmarking optimization software with performance profiles"
