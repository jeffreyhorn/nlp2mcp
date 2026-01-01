# GAMSLIB Model Types Survey

**Date:** December 30, 2025 (Updated: January 1, 2026)  
**Sprint 13 Prep Task 4:** Survey GAMSLIB Model Types  
**Purpose:** Establish inclusion/exclusion criteria for Sprint 13 model catalog

---

## Executive Summary

GAMSLIB contains 437 models across 15 model type categories. For Sprint 13 convexity verification:

- **Discovered:** 219 models (86 LP + 120 NLP + 13 QCP)
- **Successfully Classified:** 164 models (57 verified_convex + 103 likely_convex + 4 excluded)
- **Errors:** 55 models (license limits, compilation errors, special workflows)

This significantly exceeds the 50+ model target for corpus creation.

### Sprint 13 Results Summary

| Classification | Count | Percentage |
|---------------|-------|------------|
| Verified Convex (LP) | 57 | 26.0% |
| Likely Convex (NLP/QCP) | 103 | 47.0% |
| Excluded (Infeasible) | 4 | 1.8% |
| Errors | 55 | 25.1% |
| **Total** | **219** | **100%** |

---

## 1. GAMS Model Type Definitions

### 1.1 Continuous Optimization (Candidates for Inclusion)

| Type | Full Name | Description | Convexity |
|------|-----------|-------------|-----------|
| **LP** | Linear Programming | Linear objective and constraints, continuous variables | **Always convex** |
| **NLP** | Nonlinear Programming | Smooth nonlinear functions, continuous variables | **May be convex or non-convex** |
| **QCP** | Quadratically Constrained Program | Quadratic objective/constraints, continuous variables | **Convex if Q ⪰ 0** |

### 1.2 Integer/Discrete Optimization (Excluded)

| Type | Full Name | Description | Exclusion Reason |
|------|-----------|-------------|------------------|
| **MIP** | Mixed Integer Programming | Linear with integer/binary variables | Non-convex by definition |
| **MINLP** | Mixed Integer Nonlinear Programming | Nonlinear with integer/binary variables | Non-convex by definition |
| **MIQCP** | Mixed Integer QCP | Quadratic with integer/binary variables | Non-convex by definition |
| **RMIQCP** | Relaxed MIQCP | MIQCP with relaxed integrality | Designed for integer problems |

**Note:** RMIP and RMINLP are valid GAMS model types but have 0 models in GAMSLIB.

### 1.3 Complementarity/Equilibrium (Excluded)

| Type | Full Name | Description | Exclusion Reason |
|------|-----------|-------------|------------------|
| **MCP** | Mixed Complementarity Problem | No objective, complementarity conditions | No optimization objective |
| **MPEC** | Math Program with Equilibrium Constraints | Optimization with complementarity | Non-convex constraints |
| **CNS** | Constrained Nonlinear System | Square system of equations | No optimization objective |

### 1.4 Special Types (Excluded)

| Type | Full Name | Description | Exclusion Reason |
|------|-----------|-------------|------------------|
| **DNLP** | Discontinuous NLP | Non-smooth functions (abs, min, max) | Non-differentiable, non-convex |
| **EMP** | Extended Mathematical Programming | Meta-modeling framework | Not standard optimization |
| **MPSGE** | Mathematical Programming System for General Equilibrium | CGE models | Specialized equilibrium |
| **GAMS** | GAMS Utility | Data manipulation, no optimization | No solve statement |
| **DECIS** | Stochastic Programming | Multi-stage stochastic models | Specialized framework |

---

## 2. GAMSLIB Type Distribution

### 2.1 Model Counts by Type

| Type | Count | Percentage | Inclusion Status |
|------|-------|------------|------------------|
| MIP | 72 | 16.5% | ❌ Excluded |
| LP | 57 | 13.0% | ✅ **Included** |
| NLP | 51 | 11.7% | ✅ **Included** |
| MINLP | 24 | 5.5% | ❌ Excluded |
| GAMS | 23 | 5.3% | ❌ Excluded |
| MPSGE | 21 | 4.8% | ❌ Excluded |
| MCP | 16 | 3.7% | ❌ Excluded |
| QCP | 11 | 2.5% | ✅ **Included** |
| DNLP | 7 | 1.6% | ❌ Excluded |
| DECIS | 5 | 1.1% | ❌ Excluded |
| MIQCP | 4 | 0.9% | ❌ Excluded |
| CNS | 4 | 0.9% | ❌ Excluded |
| EMP | 4 | 0.9% | ❌ Excluded |
| RMIQCP | 2 | 0.5% | ❌ Excluded |
| MPEC | 1 | 0.2% | ❌ Excluded |
| **Total** | **437** | 100% | |

### 2.2 Actual Corpus (Sprint 13 Results)

| Category | Discovered | Verified/Likely | Excluded | Errors |
|----------|-----------|-----------------|----------|--------|
| LP | 86 | 57 verified_convex | 0 | 29 |
| NLP | 120 | 97 likely_convex | 4 | 19 |
| QCP | 13 | 6 likely_convex | 0 | 7 |
| **Total** | **219** | **160 (57 verified + 103 likely)** | **4** | **55** |

**Note:** The 55 errors are expected edge cases:
- License limits (11): Models exceed GAMS demo license size limits
- No solve summary (15): Models with special workflows (async, grid, scenario solves)
- Compilation errors (18): Missing include files or external dependencies
- Unexpected status (7): Unusual solver/model status combinations
- Solver errors (4): Solver did not complete normally

---

## 3. Inclusion Criteria

### 3.1 LP Models (57 models) - AUTO-INCLUDE

**Criteria:**
- Solve statement uses `using LP`
- All LP problems are convex by definition
- No further verification needed

**Classification:** `verified_convex`

**Example:**
```gams
solve transport using lp minimizing z;
```

### 3.2 NLP Models (51 models) - INCLUDE FOR VERIFICATION

**Criteria:**
- Solve statement uses `using NLP`
- Smooth, differentiable functions only
- Requires convexity verification via solve status

**Classification Process:**
1. Solve with local NLP solver (CONOPT, IPOPT)
2. Check MODEL STATUS:
   - STATUS 1 (Optimal) → `verified_convex` (solver proved global optimum)
   - STATUS 2 (Locally Optimal) → `needs_verification` (cannot confirm convexity)
3. For STATUS 2 models, may require manual analysis or global solver

**Example:**
```gams
solve m using nlp minimizing r;
```

### 3.3 QCP Models (11 models) - INCLUDE FOR VERIFICATION

**Criteria:**
- Solve statement uses `using QCP`
- Quadratic objective and/or constraints
- Convex if all quadratic forms are positive semidefinite

**Classification Process:**
1. Solve with QCP solver
2. Check MODEL STATUS (same as NLP)
3. Alternatively, check if solver reports convexity

**Example:**
```gams
solve qp7 using qcp minimizing z;
```

**Note:** Some QCP models are solved as NLP in GAMSLIB (e.g., `qp1.gms` uses `using nlp`).

---

## 4. Exclusion Criteria

### 4.1 Integer/Discrete Variables - EXCLUDE

**Types:** MIP, MINLP, MIQCP, RMIQCP

**Rationale:**
- Integer variables create non-convex feasible regions
- Even relaxed formulations of integer problems are designed for discrete decisions
- Convexity concept doesn't apply to discrete optimization

**Count:** 72 + 24 + 4 + 2 = 102 models

### 4.2 Complementarity Problems - EXCLUDE

**Types:** MCP, MPEC

**Rationale:**
- MCP has no objective function (finds equilibrium)
- MPEC has complementarity constraints which are inherently non-convex
- Not standard convex optimization problems

**Count:** 16 + 1 = 17 models

### 4.3 System of Equations - EXCLUDE

**Types:** CNS

**Rationale:**
- No objective function to optimize
- Finds solution to F(x) = 0
- Convexity concept not applicable

**Count:** 4 models

### 4.4 Non-Smooth Functions - EXCLUDE

**Types:** DNLP

**Rationale:**
- Contains non-differentiable functions (abs, min, max, sign)
- Violates smoothness requirement for standard convexity
- Often reformulated as MINLP internally

**Count:** 7 models

### 4.5 Specialized Frameworks - EXCLUDE

**Types:** EMP, MPSGE, GAMS, DECIS

**Rationale:**
- EMP: Meta-programming framework, not standard optimization
- MPSGE: Specialized CGE equilibrium models
- GAMS: Utility models without solve statements
- DECIS: Stochastic programming framework

**Count:** 4 + 21 + 23 + 5 = 53 models

---

## 5. Model Type Detection

### 5.1 How Model Types Are Declared

Model types in GAMS are determined by the `solve` statement syntax:

```gams
solve <model_name> using <model_type> [minimizing|maximizing] <variable>;
```

**Examples:**
```gams
solve transport using lp minimizing z;      -- LP
solve m using nlp minimizing r;             -- NLP  
solve qp7 using qcp minimizing z;           -- QCP
solve hansen using mcp;                     -- MCP (no objective)
solve model1 using cns;                     -- CNS (no objective)
solve absM using mip maximizing y;          -- MIP
```

### 5.2 Parsing Strategy

To identify model type:
1. Search for `solve ... using <type>` pattern
2. Extract the type keyword (lp, nlp, qcp, mip, etc.)
3. Apply inclusion/exclusion rules

**Regex Pattern:**
```python
model_type_pattern = r'solve\s+\w+\s+using\s+(\w+)'
```

### 5.3 Type Determination Notes

1. **Type is in solve statement, not model definition**
   - `Model m / all /;` does not specify type
   - Type comes from `solve m using nlp`

2. **Same model can be solved as different types**
   - Some problems can be solved as LP or NLP
   - QCP can often be solved as NLP

3. **Multiple solve statements possible**
   - A file may contain multiple solves with different types
   - Use first solve or primary solve for classification

---

## 6. Convex vs Non-Convex NLP Distinction

### 6.1 Key Finding

**Cannot reliably distinguish convex from non-convex NLP by type declaration alone.**

The `NLP` type encompasses both:
- Convex NLP (e.g., minimize x² + y² subject to linear constraints)
- Non-convex NLP (e.g., minimize x·y subject to nonlinear constraints)

### 6.2 Verification Approach

For NLP models, convexity must be verified empirically:

1. **Solve with local NLP solver**
2. **Check MODEL STATUS:**
   - STATUS 1 → Solver proved global optimality → Convex
   - STATUS 2 → Local optimum only → Unknown (may or may not be convex)

3. **For STATUS 2 models, additional options:**
   - Solve with global solver (BARON) if available
   - Multiple random restarts to check for multiple local optima
   - Manual analysis of objective/constraint functions

### 6.3 Classification Strategy for Sprint 13

| MODEL STATUS | LP | NLP | QCP |
|--------------|----|----|-----|
| 1 (Optimal) | verified_convex | verified_convex | verified_convex |
| 2 (Locally Optimal) | N/A | needs_manual_review | needs_manual_review |
| Other | excluded | excluded | excluded |

---

## 7. Special Cases

### 7.1 QCP Handling

QCP models contain quadratic terms. They are convex if:
- Objective: x'Qx + cx where Q ⪰ 0 (positive semidefinite)
- Constraints: x'Rx + ax ≤ b where R ⪰ 0

**Verification:** Same as NLP - check MODEL STATUS after solve.

### 7.2 RMINLP Handling

RMINLP (Relaxed MINLP) models are excluded because:
- They originate from integer programming problems
- The relaxation is typically used for bounds computation
- Not representative of standard convex optimization

**Example:** Some GAMSLIB models categorized as RMINLP actually use `nlp` solve type (e.g., `ramsey.gms`). These should be evaluated based on actual solve type, not library categorization.

### 7.3 Models with Multiple Types

Some models solve multiple sub-problems with different types:
```gams
solve b1 minimizing phi using lp;
solve b2 minimizing phi using lp;
```

**Strategy:** Include if primary/all solves use included types (LP, NLP, QCP).

---

## 8. Summary

### 8.1 Final Inclusion/Exclusion Rules

| Model Type | Decision | Count | Rationale |
|------------|----------|-------|-----------|
| LP | ✅ Include | 57 | Always convex |
| NLP | ✅ Include | 51 | Verify with solver |
| QCP | ✅ Include | 11 | Verify with solver |
| MIP | ❌ Exclude | 72 | Integer variables |
| MINLP | ❌ Exclude | 24 | Integer + nonlinear |
| MIQCP | ❌ Exclude | 4 | Integer + quadratic |
| MCP | ❌ Exclude | 16 | No objective |
| MPEC | ❌ Exclude | 1 | Non-convex constraints |
| CNS | ❌ Exclude | 4 | No objective |
| DNLP | ❌ Exclude | 7 | Non-smooth |
| EMP | ❌ Exclude | 4 | Special framework |
| MPSGE | ❌ Exclude | 21 | CGE models |
| GAMS | ❌ Exclude | 23 | No optimization |
| DECIS | ❌ Exclude | 5 | Stochastic framework |
| RMIQCP | ❌ Exclude | 2 | Relaxed integer |

### 8.2 Expected Corpus Size

| Category | Count | Expected Valid |
|----------|-------|----------------|
| LP | 57 | ~50-55 (some may have issues) |
| NLP | 51 | ~45-50 (some may fail) |
| QCP | 11 | ~9-11 |
| **Total** | **119** | **~104-116** |

The 119 candidate models significantly exceed the 50+ target, providing margin for:
- Models that fail to execute
- Models excluded due to other issues
- Models with STATUS ≠ 1 or 2

---

## References

- GAMS Documentation: [Model Solve](https://www.gams.com/latest/docs/UG_ModelSolve.html)
- GAMSLIB Index: [Model Library](https://www.gams.com/latest/gamslib_ml/libhtml/index.html)
- Sprint 13 Research: `docs/research/GAMSLIB_ACCESS_RESEARCH.md`
- GAMS Environment: `docs/testing/GAMS_ENVIRONMENT_STATUS.md`
