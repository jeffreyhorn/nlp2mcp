# GAMSLIB Test Models Manifest

**Created:** December 31, 2025  
**Sprint 13 Prep Task 8**  
**Purpose:** Test model set for validating Sprint 13 GAMSLIB infrastructure

---

## Overview

This directory contains 13 test models from GAMSLIB for validating:
- Download script functionality
- Convexity verification logic
- Type-based exclusion criteria

**Model Distribution:**
- LP models: 5 (verified convex)
- NLP models: 5 (requires convexity verification)
- Excluded types: 3 (MIP, DNLP)

---

## LP Models (5) - Verified Convex

All LP models are convex by definition (linear objective + linear constraints).

| Model | Seq# | Description | Size | Model Status | Convexity |
|-------|------|-------------|------|--------------|-----------|
| trnsport.gms | 1 | A Transportation Problem | 1,751 bytes | 1 (Optimal) | verified_convex |
| blend.gms | 2 | Blending Problem I | 1,699 bytes | 1 (Optimal) | verified_convex |
| diet.gms | 8 | Stigler's Nutrition Model | 3,768 bytes | 1 (Optimal) | verified_convex |
| aircraft.gms | 9 | Aircraft Allocation Problem | 3,696 bytes | 1 (Optimal) | verified_convex |
| prodmix.gms | 3 | Product Mix Problem | varies | 1 (Optimal) | verified_convex |

**Expected Behavior:**
- All solve with MODEL STATUS = 1 (Optimal)
- CPLEX/CBC proves global optimum
- Classification: `verified_convex`

---

## NLP Models (5) - Requires Verification

NLP models require convexity verification via solve status.

| Model | Seq# | Description | Size | Model Status | Convexity |
|-------|------|-------------|------|--------------|-----------|
| circle.gms | 201 | Circle Enclosing Points | 1,297 bytes | 2 (Locally Optimal) | likely_convex |
| rbrock.gms | 83 | Rosenbrock Test Function | 531 bytes | 2 (Locally Optimal) | likely_convex |
| himmel16.gms | 36 | Hexagon Area Optimization | 2,329 bytes | 2 (Locally Optimal) | likely_convex |
| hs62.gms | 264 | Hock-Schittkowski Problem 62 | 1,233 bytes | 2 (Locally Optimal) | likely_convex |
| chem.gms | 16 | Chemical Equilibrium | 1,625 bytes | 2 (Locally Optimal) | likely_convex |

**Expected Behavior:**
- All solve with MODEL STATUS = 2 (Locally Optimal) using local NLP solvers
- CONOPT/IPOPT find local optimum but cannot prove global optimality
- Classification: `likely_convex` (local solver limitation)

**Notes on Convexity:**
- `circle.gms`: Convex problem (minimize radius of enclosing circle)
- `rbrock.gms`: Non-convex (Rosenbrock banana function) but has unique global minimum
- `himmel16.gms`: Convex optimization problem
- `hs62.gms`: Standard test problem, likely convex
- `chem.gms`: Chemical equilibrium, structure suggests convexity

---

## Excluded Type Models (3) - Not Suitable for MCP

These models demonstrate type-based exclusion criteria.

| Model | Seq# | Type | Description | Size | Exclusion Reason |
|-------|------|------|-------------|------|------------------|
| absmip.gms | 77 | MIP | Absolute Value MIP Example | 4,349 bytes | Integer variables |
| magic.gms | 31 | MIP | Magic Square Problem | 3,199 bytes | Integer variables |
| linear.gms | 22 | DNLP | Linear Regression via DNLP | varies | Non-smooth functions |

**Expected Behavior:**
- MIP models: Solve with MODEL STATUS = 1 but excluded due to integer variables
- DNLP models: May have solver issues (STATUS = 7) due to non-differentiable functions
- All should be flagged for exclusion in catalog

**Exclusion Rationale:**
- **MIP (Mixed Integer Program):** Integer variables create non-convex feasible region, incompatible with KKT-based MCP reformulation
- **DNLP (Discontinuous NLP):** Contains non-smooth functions (abs, min, max) that violate differentiability requirements

---

## Verification Commands

### Run All Models
```bash
cd tests/fixtures/gamslib_test_models
for f in *.gms; do
  echo "Testing $f..."
  gams "$f" lo=3 o=/tmp/${f%.gms}.lst
  grep "MODEL STATUS\|SOLVER STATUS" /tmp/${f%.gms}.lst
done
```

### Check Model Types
```bash
cd tests/fixtures/gamslib_test_models
for f in *.gms; do
  type=$(grep -i "solve.*using" "$f" | head -1)
  echo "$f: $type"
done
```

### Validate LP Convexity
```bash
# LP models should all have MODEL STATUS = 1
for f in trnsport.gms blend.gms diet.gms aircraft.gms prodmix.gms; do
  gams "$f" lo=0 o=/tmp/${f%.gms}.lst
  status=$(grep "MODEL STATUS" /tmp/${f%.gms}.lst | head -1 | awk '{print $4}')
  echo "$f: MODEL STATUS = $status (expected: 1)"
done
```

### Validate NLP Behavior
```bash
# NLP models should have MODEL STATUS = 2 with local solvers
for f in circle.gms rbrock.gms himmel16.gms hs62.gms chem.gms; do
  gams "$f" lo=0 o=/tmp/${f%.gms}.lst
  status=$(grep "MODEL STATUS" /tmp/${f%.gms}.lst | head -1 | awk '{print $4}')
  echo "$f: MODEL STATUS = $status (expected: 2)"
done
```

---

## Model Status Reference

| Code | Status | Meaning | Convexity Implication |
|------|--------|---------|----------------------|
| 1 | Optimal | Global optimum found | LP: verified_convex |
| 2 | Locally Optimal | Local optimum found | NLP: likely_convex |
| 3 | Unbounded | No finite optimum | Exclude from corpus |
| 4 | Infeasible | No feasible solution | Exclude from corpus |
| 5 | Locally Infeasible | Locally infeasible | Exclude from corpus |
| 7 | Intermediate Non-Optimal | Solver interrupted | Needs investigation |

---

## File Sizes

```
total 13 models
-rw-r--r--  4,349  absmip.gms
-rw-r--r--  3,696  aircraft.gms
-rw-r--r--  1,699  blend.gms
-rw-r--r--  1,625  chem.gms
-rw-r--r--  1,297  circle.gms
-rw-r--r--  3,768  diet.gms
-rw-r--r--  2,329  himmel16.gms
-rw-r--r--  1,233  hs62.gms
-rw-r--r--  varies linear.gms
-rw-r--r--  3,199  magic.gms
-rw-r--r--  varies prodmix.gms
-rw-r--r--    531  rbrock.gms
-rw-r--r--  1,751  trnsport.gms
```

---

## Usage in Sprint 13

These models support:

1. **Download Script Testing:** Verify gamslib extraction works correctly
2. **Type Detection:** Test parsing of `solve ... using LP/NLP/MIP` statements
3. **Convexity Verification:** Test classification algorithm with known outcomes
4. **Exclusion Logic:** Test filtering of MIP/DNLP models from corpus

---

## Changelog

- **2025-12-31:** Initial test model set created for Sprint 13 Prep Task 8
