# Min/Max PATH Validation Findings
**Date:** November 6, 2025  
**Sprint:** 5, Day 2, Task 2.3  
**Status:** 🔴 CRITICAL ISSUE IDENTIFIED

## Executive Summary

PATH validation revealed that the current min/max reformulation generates **mathematically infeasible** MCP systems when min/max appears in objective-defining equations. This matches the prediction in `minmax_objective_reformulation.md` research document.

## Test Results

### Test 1: minimize min(x,y)
**File:** `tests/fixtures/minmax_research/test1_minimize_min.gms`

**Model Structure:**
```gams
minimize obj
obj = z
z = min(x, y)
```

**Generated MCP:** ✅ Structurally correct auxiliary variables and constraints created  
**PATH Result:** ❌ INFEASIBLE  
**PATH Output:**
```
ThrRowEqnTwoInfeasible
     stat_aux_min_minconstraint_0
     minconstraint
     stat_z

 *** EXIT - infeasible.
```

### Root Cause Analysis

The infeasibility arises from over-constrained stationarity conditions:

**Generated Equations:**
1. `stat_z.. 1 + 1 * nu_minconstraint = 0`  
   (Stationarity for z with objective gradient = 1)

2. `stat_aux_min_minconstraint_0.. -nu_minconstraint + lam_arg0 + lam_arg1 = 0`  
   (Stationarity for auxiliary variable)

3. `minconstraint.. z = aux_min_minconstraint_0`  
   (Auxiliary equality constraint)

**Mathematical Impossibility:**
- From eq. 1: `nu_minconstraint = -1`
- From eq. 2: `nu_minconstraint = lam_arg0 + lam_arg1`
- Therefore: `-1 = lam_arg0 + lam_arg1` where both lambdas ≥ 0

This system has no solution!

## Why This Happens

When min/max appears in an **objective-defining equation** (not directly in the objective or a regular constraint), the KKT stationarity equation for the intermediate variable (z) includes:

1. The objective gradient term: `∂f/∂z = 1` (for minimize)
2. The equality constraint multiplier: `ν_minconstraint`

These create a conflict because:
- The objective gradient is a fixed constant (1 or -1)
- The multiplier must balance the auxiliary variable's stationarity
- The system becomes over-constrained

## What Works vs. What Doesn't

### ✅ WORKS: Direct objective min/max
```gams
minimize min(x, y)  * Min/max directly in objective
```
→ No intermediate variable z, no conflict

### ✅ WORKS: Min/max in regular constraints  
```gams
minimize obj
obj = z
c1.. z >= min(x, y) + 0.5  * Min/max in constraint, not defining obj
```
→ No objective gradient for the constraint expression

### ❌ FAILS: Min/max defining objective variable
```gams
minimize obj
obj = z          * Objective-defining equation
z = min(x, y)    * Min/max in objective-defining chain
```
→ Creates infeasible KKT system (our test cases!)

## Solution: Strategy 1 (Direct Objective Substitution)

The research document `minmax_objective_reformulation.md` identified this exact issue and proposed **Strategy 1** as the solution:

**Transformation:**
```
Original:
  minimize obj
  obj = z
  z = min(x, y)

Strategy 1:
  minimize aux_min    * Substitute objective variable
  obj = aux_min       * Update equality
  aux_min <= x        * Reformulation constraints
  aux_min <= y
```

**Key Insight:** By making the auxiliary variable the objective directly, we eliminate the intermediate variable z and avoid the stationarity conflict.

## Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Detection (Day 1) | ✅ Complete | Can identify min/max in equations |
| Basic reformulation | ✅ Complete | Creates aux variables and constraints |
| Objective substitution (Strategy 1) | ❌ NOT IMPLEMENTED | Required for objective-defining cases |
| KKT assembly | ✅ Complete | Architecture is correct |

## Impact on Sprint 5 Goals

### Day 2 Acceptance Criteria
- ✅ Reformulation in pipeline
- ✅ Debug logging enabled  
- ✅ Tests pass (structural checks)
- ❌ **PATH validation FAILS** ← BLOCKER

### Required Next Steps

1. **Implement Strategy 1** (Direct Objective Substitution)
   - Detect when min/max is in objective-defining equation chain
   - Replace objective variable with auxiliary variable
   - Update objective-defining equations

2. **Update Test Expectations**
   - Current tests only check structural reformulation
   - Need PATH solvability tests

3. **Alternative: Redefine Test Cases**
   - Use min/max in regular constraints (not objective-defining)
   - Focus on cases that work with current implementation
   - Document objective-defining case as known limitation

## Recommendations

### Option A: Implement Strategy 1 (Full Fix)
**Effort:** 4-6 hours  
**Risk:** Medium (complex objective variable substitution)  
**Benefit:** Solves the problem completely

**Tasks:**
- Implement objective variable detection and chain tracing
- Add objective substitution logic to reformulation
- Update derivative computation for new objective
- Verify PATH solvability

### Option B: Document Limitation (Pragmatic)
**Effort:** 1-2 hours  
**Risk:** Low  
**Benefit:** Unblocks Day 2, defers complex work

**Tasks:**
- Update tests to use min/max in regular constraints
- Document objective-defining case as unsupported
- Add validation error with helpful message
- Create follow-on task for Strategy 1

## References

- Research: `docs/research/minmax_objective_reformulation.md`
- Design: `docs/design/minmax_kkt_fix_design.md`  
- Implementation: `src/kkt/reformulation.py`
- Tests: `tests/unit/kkt/test_minmax_fix.py`

## Conclusion

The reformulation infrastructure is working correctly, but the current approach generates infeasible MCPs for the specific case of min/max in objective-defining equations. This was predicted in the research phase and requires implementing Strategy 1 (Direct Objective Substitution) to resolve.

**Status:** Day 2 cannot be marked complete until either:
1. Strategy 1 is implemented and PATH validation passes, OR
2. Scope is adjusted to exclude objective-defining cases with clear documentation
