# Solution Comparison Research

**Task:** Sprint 15 Prep Task 3  
**Date:** January 9, 2026  
**Purpose:** Research strategies for comparing NLP solutions with MCP solutions to validate nlp2mcp KKT reformulation

---

## Executive Summary

This document researches strategies for comparing original NLP solutions with MCP solutions from nlp2mcp's KKT reformulation. The comparison validates that the reformulation produces mathematically equivalent results.

**Key Recommendations:**
1. **Tolerance values:** rtol=1e-6, atol=1e-8 (aligned with solver defaults)
2. **Comparison scope:** Objective value only for Sprint 15 (sufficient for validation)
3. **Status handling:** Decision tree for optimal/infeasible/mismatch scenarios
4. **Multiple optima:** Accept matching objective values regardless of primal variable differences

**Implementation Approach:** Parse .lst files for objective values and status codes using existing patterns from `verify_convexity.py`.

---

## Section 1: Theoretical Foundation

### 1.1 KKT Optimality Conditions

From `docs/concepts/IDEA.md`, the nlp2mcp transformation converts an NLP to an MCP by:

1. **Starting with NLP:**
   - Minimize f(x) subject to g(x) ≤ 0, h(x) = 0, ℓ ≤ x ≤ u

2. **Forming KKT conditions:**
   - **Stationarity:** ∇f(x) + Jg(x)ᵀλ + Jh(x)ᵀν - πL + πU = 0
   - **Primal feasibility:** g(x) ≤ 0, h(x) = 0, ℓ ≤ x ≤ u
   - **Dual feasibility:** λ ≥ 0, πL ≥ 0, πU ≥ 0
   - **Complementarity:** λ ⊥ g(x), πL ⊥ (x-ℓ), πU ⊥ (u-x)

3. **Encoding as MCP:**
   - Variables z := (x, λ, ν, πL, πU)
   - Functions F(z) with bounds producing complementarity behavior

### 1.2 When NLP and MCP Solutions Should Match

**Theorem (Convex Case):** For convex NLPs (convex f, convex g, affine h), the KKT conditions are both necessary and sufficient for global optimality. Therefore:
- If NLP has a unique global optimum x*, the MCP solution will have x = x*
- Objective values will match exactly (within numerical precision)

**Non-Convex Case:** The MCP encodes KKT stationary points. For non-convex NLPs:
- MCP may find local optima or saddle points
- Not guaranteed to find the same local optimum as NLP solver

**Sprint 15 Context:** GAMSLIB models are filtered for `verified_convex` or `likely_convex` status, so solutions should match.

### 1.3 Sources of Numerical Differences

Even for convex problems, numerical differences arise from:

1. **Solver tolerances:** NLP solver (CONOPT/IPOPT) and MCP solver (PATH) use different internal tolerances
2. **Starting points:** Different initial values may lead to different convergence paths
3. **Numerical precision:** IEEE 754 double precision (~15-17 significant digits)
4. **Problem scaling:** Poorly scaled problems amplify numerical errors
5. **Constraint qualification:** Near-degenerate cases may have numerical sensitivity

---

## Section 2: Tolerance Selection

### 2.1 Solver Default Tolerances

| Solver | Tolerance Parameter | Default Value | Description |
|--------|---------------------|---------------|-------------|
| CONOPT | RTREDG | 1e-7 | Reduced gradient tolerance |
| IPOPT | tol | 1e-8 | Overall convergence tolerance |
| PATH | convergence_tolerance | 1e-6 | Complementarity residual tolerance |
| CPLEX | optimality_tolerance | 1e-6 | Optimality tolerance for LP/QP |
| GUROBI | OptimalityTol | 1e-6 | Optimality tolerance |

**Observation:** Most solvers use tolerances in the 1e-6 to 1e-8 range.

### 2.2 Existing nlp2mcp Tolerances

From `tests/validation/test_path_solver.py`:
```python
def _check_kkt_residuals(lst_content: str, tolerance: float = 1e-6) -> tuple[bool, str]:
    """Check if KKT conditions are satisfied based on solution residuals."""
```

The existing codebase uses **1e-6** for KKT residual checking.

### 2.3 Tolerance Comparison Approaches

**Absolute Tolerance (atol):**
```python
|a - b| <= atol
```
- Good for values near zero
- Fails for large values (1000.0 vs 1000.001 may fail with atol=1e-4)

**Relative Tolerance (rtol):**
```python
|a - b| / |b| <= rtol
```
- Good for large values
- Fails for values near zero (division by ~0)

**Combined Tolerance (recommended):**
```python
|a - b| <= atol + rtol * |b|
```
- Handles both edge cases
- Used by NumPy `allclose()`, SciPy, and most numerical libraries

### 2.4 Recommended Tolerance Values

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **rtol** | 1e-6 | Matches PATH/CPLEX defaults; 0.0001% relative difference |
| **atol** | 1e-8 | Matches IPOPT default; handles objectives near zero |

**Comparison Algorithm:**
```python
def objectives_match(nlp_obj: float, mcp_obj: float, rtol: float = 1e-6, atol: float = 1e-8) -> bool:
    """Check if NLP and MCP objectives match within tolerance."""
    return abs(nlp_obj - mcp_obj) <= atol + rtol * abs(nlp_obj)
```

### 2.5 Edge Cases

| Scenario | Handling |
|----------|----------|
| Objective = 0 exactly | Use absolute tolerance only |
| Very large objective (> 1e9) | Relative tolerance dominates |
| Very small objective (< 1e-6) | Absolute tolerance dominates |
| NaN or Inf | Report as comparison failure |

### 2.6 Configuration Approach

For Sprint 15, make tolerances configurable via:

**Command-line arguments:**
```bash
python test_solve.py --rtol=1e-6 --atol=1e-8
```

**Environment variables (optional):**
```bash
export NLP2MCP_RTOL=1e-6
export NLP2MCP_ATOL=1e-8
```

---

## Section 3: Status Comparison Decision Tree

### 3.1 GAMS Status Codes

**Solver Status (from GAMS):**
| Code | Meaning |
|------|---------|
| 1 | Normal Completion |
| 2 | Iteration Interrupt |
| 3 | Resource Interrupt |
| 4 | Terminated by Solver |
| 5 | Evaluation Error Limit |
| 6 | Capability Problems |
| 7 | Licensing Problems |

**Model Status (from GAMS):**
| Code | Meaning |
|------|---------|
| 1 | Optimal |
| 2 | Locally Optimal |
| 3 | Unbounded |
| 4 | Infeasible |
| 5 | Locally Infeasible |
| 6 | Intermediate Infeasible |
| 7 | Intermediate Nonoptimal |

### 3.2 Decision Tree

```
START
  │
  ├── NLP solve failed (solver_status != 1)?
  │     └── YES → comparison_result = "nlp_solve_failed"
  │               (Cannot compare without NLP baseline)
  │
  ├── MCP solve failed (solver_status != 1)?
  │     └── YES → comparison_result = "mcp_solve_failed"
  │               (Possible nlp2mcp bug or model issue)
  │
  ├── Both optimal (model_status == 1 or 2)?
  │     └── YES → Compare objectives
  │               ├── Match within tolerance → "objective_match"
  │               └── Mismatch → "objective_mismatch" (INVESTIGATE!)
  │
  ├── Both infeasible (model_status == 4 or 5)?
  │     └── YES → comparison_result = "both_infeasible"
  │               (Agree on infeasibility - OK)
  │
  ├── NLP optimal, MCP infeasible?
  │     └── YES → comparison_result = "status_mismatch_nlp_optimal"
  │               (Likely nlp2mcp bug - INVESTIGATE!)
  │
  ├── NLP infeasible, MCP optimal?
  │     └── YES → comparison_result = "status_mismatch_mcp_optimal"
  │               (Likely nlp2mcp bug - INVESTIGATE!)
  │
  └── Other status combinations
        └── comparison_result = "status_unknown"
            (Log for manual review)
```

### 3.3 Comparison Result Enum

```python
class ComparisonResult(str, Enum):
    OBJECTIVE_MATCH = "objective_match"           # Objectives match within tolerance
    OBJECTIVE_MISMATCH = "objective_mismatch"     # Objectives differ beyond tolerance
    BOTH_INFEASIBLE = "both_infeasible"           # Both agree model is infeasible
    STATUS_MISMATCH_NLP_OPTIMAL = "status_mismatch_nlp_optimal"  # NLP optimal, MCP not
    STATUS_MISMATCH_MCP_OPTIMAL = "status_mismatch_mcp_optimal"  # MCP optimal, NLP not
    NLP_SOLVE_FAILED = "nlp_solve_failed"         # Could not solve original NLP
    MCP_SOLVE_FAILED = "mcp_solve_failed"         # Could not solve generated MCP
    COMPARISON_ERROR = "comparison_error"         # Error during comparison
```

### 3.4 Priority of Investigation

| Result | Priority | Action |
|--------|----------|--------|
| `objective_mismatch` | Critical | Investigate nlp2mcp formulation |
| `status_mismatch_*` | Critical | Investigate nlp2mcp formulation |
| `mcp_solve_failed` | High | Check generated MCP syntax, PATH config |
| `nlp_solve_failed` | Medium | Model may be genuinely problematic |
| `both_infeasible` | Low | Expected for infeasible models |
| `objective_match` | None | Success! |

---

## Section 4: Multiple Optima Handling

### 4.1 When Multiple Optima Occur

Multiple optima (non-unique solutions) occur when:
1. **Linear programs:** Degenerate vertices, edge solutions
2. **Flat objective regions:** Objective constant along a set
3. **Symmetric problems:** Multiple equivalent solutions

### 4.2 Impact on Comparison

For problems with multiple optima:
- **Primal variables (x):** May differ between NLP and MCP solutions
- **Objective value (f(x)):** Should be identical at all optima
- **Dual multipliers (λ, ν):** May differ

### 4.3 Sprint 15 Strategy

**Recommendation:** Compare objective values only, not primal variables.

**Rationale:**
1. If objectives match, both solvers found an optimal solution
2. Different primal values at same objective are valid multiple optima
3. Primal comparison requires variable name mapping (complex)
4. Objective comparison is sufficient to detect nlp2mcp bugs

**Future Enhancement (Sprint 16+):**
- Add optional primal variable comparison for debugging
- Implement variable name mapping between NLP and MCP
- Compare dual multipliers for theoretical validation

### 4.4 Detection of Multiple Optima

For Sprint 15, we won't explicitly detect multiple optima. If objectives match, we accept the solution regardless of primal variable differences.

Future enhancement: Flag models where primal variables differ significantly despite matching objectives (suggests multiple optima).

---

## Section 5: Comparison Scope Decision

### 5.1 What Could Be Compared

| Component | Availability | Complexity | Value |
|-----------|--------------|------------|-------|
| Objective value | Easy (.lst parsing) | Low | High |
| Primal variables (x) | Medium (.lst parsing) | Medium | Medium |
| Dual multipliers (λ, ν) | Hard (MCP-specific) | High | Low |
| KKT residuals | Medium (.lst parsing) | Low | Medium |

### 5.2 Sprint 15 Scope: Objective Only

**Decision:** Compare objective values only for Sprint 15.

**Justification:**
1. **Sufficient for bug detection:** Wrong KKT formulation will produce wrong objective
2. **Simple implementation:** Reuse existing .lst parsing from `verify_convexity.py`
3. **Handles multiple optima:** Objective matches even when primal differs
4. **Low overhead:** Single floating-point comparison per model

### 5.3 What This Catches

Objective-only comparison will catch:
- Sign errors in stationarity equations
- Missing or incorrect gradient terms
- Wrong constraint handling
- Incorrect bound transformations

### 5.4 What This Might Miss

Objective-only comparison might miss:
- Bugs that don't affect objective (rare in practice)
- Subtle dual variable issues (not relevant for Sprint 15)
- Constraint satisfaction issues (caught by solver status)

---

## Section 6: Implementation Approach

### 6.1 .lst File Parsing (Recommended)

**Existing Pattern from `verify_convexity.py`:**
```python
objective_pattern = re.compile(
    r"\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
    re.MULTILINE,
)

objective_matches = list(objective_pattern.finditer(lst_content))
if objective_matches:
    match = objective_matches[-1]
    objective_value = float(match.group(1))
```

**Advantages:**
- Already implemented and tested
- Works with any GAMS version
- No additional dependencies

### 6.2 Status Extraction

**Existing Pattern from `verify_convexity.py`:**
```python
solver_pattern = re.compile(
    r"\*\*\*\* SOLVER STATUS\s+(\d+)\s+(\w+.*?)$",
    re.MULTILINE,
)
model_pattern = re.compile(
    r"\*\*\*\* MODEL STATUS\s+(\d+)\s+(\w+.*?)$",
    re.MULTILINE,
)
```

### 6.3 Code Reuse Opportunities

**From `scripts/gamslib/verify_convexity.py`:**
- `parse_gams_output()` - Extract status codes and objective
- `classify_result()` - Classify based on status codes

**From `tests/validation/test_path_solver.py`:**
- `_check_kkt_residuals()` - Validate KKT satisfaction
- `_solve_gams()` - Execute GAMS and collect output

### 6.4 Proposed Implementation

```python
def compare_solutions(
    nlp_objective: float,
    mcp_objective: float,
    nlp_model_status: int,
    mcp_model_status: int,
    rtol: float = 1e-6,
    atol: float = 1e-8,
) -> ComparisonResult:
    """Compare NLP and MCP solutions.
    
    Args:
        nlp_objective: Objective value from original NLP solve
        mcp_objective: Objective value from MCP solve
        nlp_model_status: GAMS model status from NLP
        mcp_model_status: GAMS model status from MCP
        rtol: Relative tolerance
        atol: Absolute tolerance
        
    Returns:
        ComparisonResult enum value
    """
    # Check if both optimal
    if nlp_model_status in (1, 2) and mcp_model_status in (1, 2):
        if abs(nlp_objective - mcp_objective) <= atol + rtol * abs(nlp_objective):
            return ComparisonResult.OBJECTIVE_MATCH
        else:
            return ComparisonResult.OBJECTIVE_MISMATCH
    
    # Check if both infeasible
    if nlp_model_status in (4, 5) and mcp_model_status in (4, 5):
        return ComparisonResult.BOTH_INFEASIBLE
    
    # Status mismatch
    if nlp_model_status in (1, 2) and mcp_model_status not in (1, 2):
        return ComparisonResult.STATUS_MISMATCH_NLP_OPTIMAL
    
    if mcp_model_status in (1, 2) and nlp_model_status not in (1, 2):
        return ComparisonResult.STATUS_MISMATCH_MCP_OPTIMAL
    
    return ComparisonResult.COMPARISON_ERROR
```

---

## Section 7: Sprint 15 Recommendations

### 7.1 Implementation Checklist

1. **Create `compare_solutions()` function** in test_solve.py
   - Accept NLP and MCP objectives/statuses
   - Return ComparisonResult enum
   - Use rtol=1e-6, atol=1e-8 defaults

2. **Extend database schema** (Task 6)
   - Add `solution_comparison` object
   - Store comparison_result, objectives, tolerances

3. **Add reporting**
   - Summary: match/mismatch/infeasible counts
   - Detail: per-model comparison results
   - Flag: models requiring investigation

### 7.2 Testing Strategy

1. **Known-good models:** Verify objective_match
2. **Infeasible models:** Verify both_infeasible
3. **Synthetic bugs:** Verify objective_mismatch detection

### 7.3 Configuration Defaults

| Parameter | Default | Override |
|-----------|---------|----------|
| rtol | 1e-6 | --rtol=VALUE |
| atol | 1e-8 | --atol=VALUE |

### 7.4 Error Handling

1. **NaN/Inf objectives:** Report as comparison_error
2. **Parse failures:** Report as comparison_error with details
3. **Timeout:** Report as mcp_solve_failed or nlp_solve_failed

---

## Appendix A: Verification of Known Unknowns

### Unknown 3.1: What tolerance values are appropriate for solution comparison?

**Status:** ✅ VERIFIED

**Finding:** Default tolerances of rtol=1e-6 and atol=1e-8 are appropriate:
- Aligned with PATH, CPLEX, IPOPT defaults (1e-6 to 1e-8 range)
- Consistent with existing nlp2mcp validation (1e-6 for KKT residuals)
- Combined tolerance formula handles edge cases (near-zero, very large)

### Unknown 3.2: How to handle infeasibility and status mismatches?

**Status:** ✅ VERIFIED

**Finding:** Use decision tree approach:
- Both optimal → compare objectives
- Both infeasible → accept as agreement
- Status mismatch (one optimal, one not) → flag for investigation as likely nlp2mcp bug
- Solve failures → report appropriately

### Unknown 3.3: How to handle multiple optima (non-unique solutions)?

**Status:** ✅ VERIFIED

**Finding:** Compare objective values only, not primal variables:
- Objective should be identical at all optima
- Primal variables may legitimately differ
- Variable comparison adds complexity without value for Sprint 15

### Unknown 3.4: Should solution comparison include primal variables or just objectives?

**Status:** ✅ VERIFIED

**Finding:** Objective comparison only for Sprint 15:
- Sufficient to detect nlp2mcp bugs (wrong gradients, sign errors)
- Handles multiple optima gracefully
- Simple implementation with existing code reuse
- Primal comparison can be added in Sprint 16+ if needed

---

## Appendix B: References

1. **IDEA.md:** KKT transformation theory
2. **NLP2MCP_HIGH_LEVEL.md:** Implementation approach
3. **verify_convexity.py:** Existing .lst parsing patterns
4. **test_path_solver.py:** KKT residual checking
5. **GAMS Documentation:** Status codes and solver options

---

*Document created: January 9, 2026*  
*Sprint 15 Prep Task 3*
