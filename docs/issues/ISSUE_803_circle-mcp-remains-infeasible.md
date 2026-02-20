# ISSUE #803: Circle MCP Remains Infeasible Despite .l Initialization

**GitHub Issue**: https://github.com/jeffreyhorn/nlp2mcp/issues/803  
**Status**: Open  
**Created**: 2026-02-20  
**Epic**: Epic 4 - GAMSlib Catalog Expansion  
**Priority**: Medium

## Problem

After implementing expression-based `.l` initialization emission (Sprint 20 Days 1-2), circle.gms still fails to solve with PATH solver returning model_status=5 (Locally Infeasible). The `.l` initialization expressions are correctly captured in the IR and emitted in the MCP output, but this does not resolve the infeasibility.

## Verification

Circle's `.l` expressions are correctly emitted in the MCP file:
```gams
a.l = (xmin + xmax) / 2;
b.l = (ymin + ymax) / 2;
r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));
```

PATH solver output:
```
**** SOLVER STATUS     1 Normal Completion
**** MODEL STATUS      5 Locally Infeasible
 RESOURCE USAGE, LIMIT          0.249 10000000000.000
 ITERATION COUNT, LIMIT       487    2147483647
```

## Analysis

The infeasibility persists despite providing PATH with a warm start (the centroid of the data points, which should be close to the optimal solution). This suggests:

1. **Not an initialization problem**: The warm start values are reasonable and close to the solution
2. **Likely an MCP formulation issue**: The KKT equations generated for circle may have structural problems
3. **Possible causes**:
   - Incorrect stationarity equations
   - Missing or incorrect complementarity conditions
   - Issues with bound handling in the KKT system
   - Problems with how the original GAMS model translates to MCP

## Context

- Original GAMS circle.gms solves successfully
- Sprint 19 PR #750 fixed determinism (random data is now stable)
- Sprint 20 Days 1-2 added `.l` expression emission
- Issue #753 tracked this as a `.l` initialization problem, but the root cause is deeper

## Investigation Results (2026-02-19)

### Attempted Fix: Multiplier Initialization

**Hypothesis:** PATH solver needs initialized dual variables (multipliers) to provide a feasible warm start for the KKT system.

**Implementation Attempted:**
- Added multiplier initialization in `src/emit/emit_gams.py`
- Initialized all inequality multipliers (`lam_e(i)`) to 0.1
- Initialized all bound multipliers (`piL_r`) to 0.1

**Result:** FAILED - Model still returns status 5 (Locally Infeasible)

PATH output showed:
```
FINAL STATISTICS
Inf-Norm of Complementarity . .  4.0707e+00 eqn: (stat_r)
Inf-Norm of Fischer Function. .  8.7897e-01 eqn: (stat_r)

** EXIT - other error.
Residual. . . . . . . . 8.789771e-01
```

### Root Cause Analysis

After comprehensive investigation, the multiplier initialization approach did NOT solve the problem because:

1. **The mathematical formulation is correct but confusing:**
   - The generated stationarity equations have double negations: `(-1) * sum(i, ... * (-1) * lam_e(i))`
   - These simplify to the correct KKT conditions mathematically
   - However, PATH solver may struggle with the numerical representation

2. **Uniform multiplier initialization is inconsistent:**
   - Setting all `lam_e(i) = 0.1` implies ALL constraints are active
   - The primal initialization (centroid of bounding box) suggests most constraints should be INACTIVE
   - This creates an inconsistent starting point for PATH

3. **The stationarity equation for `r` is violated at startup:**
   - With all multipliers at 0.1: `1 = 2*r*sum(lam_e) + piL_r`
   - This requires `sum(lam_e) ≈ 1/(2*r)` for consistency
   - Uniform 0.1 initialization doesn't satisfy this relationship

4. **Deeper KKT formulation issues:**
   - The double negation pattern suggests the inequality constraint derivative handling may need review
   - Original constraint: `sqr(x(i) - a) + sqr(y(i) - b) <= sqr(r)`
   - Converted to: `g_i = sqr(x(i) - a) + sqr(y(i) - b) - sqr(r) <= 0`
   - The `-1` factors in stationarity may be coming from how `<=` constraints are normalized

### What Would Be Required for a Fix

1. **Simplify stationarity equations during generation:**
   - Eliminate double negations in the Jacobian/stationarity assembly
   - Emit cleaner GAMS code: `sum(i, 2*(a - x(i)) * lam_e(i)) = 0`

2. **Smart multiplier initialization:**
   - Evaluate constraints at primal initial point
   - Identify which constraints are active/inactive
   - Set multipliers accordingly (active: positive, inactive: 0)
   - Solve reduced KKT system to determine consistent multiplier values

3. **Review inequality constraint conversion:**
   - Check `src/ad/jacobian.py` for how LE/GE constraints are differentiated
   - Verify sign conventions are consistent throughout the pipeline
   - Consider normalizing `g(x) <= 0` to `g(x) = 0` form during derivative computation

## Conclusion

**This issue CANNOT be fixed with simple multiplier initialization.** The problem requires:
- Deeper investigation of the KKT transformation pipeline (AD, Jacobian, stationarity assembly)
- Potential refactoring of how inequality constraints are normalized and differentiated
- More sophisticated warm-start computation that ensures KKT system consistency

This is beyond the scope of Sprint 20 and should be deferred to a dedicated debugging sprint.

## Recommendation

This requires deep debugging of the MCP formulation:
1. Review and simplify inequality constraint derivative computation in `src/ad/jacobian.py`
2. Eliminate double negations in stationarity equation assembly
3. Implement smart multiplier initialization based on active set estimation
4. Add validation that emitted KKT equations match hand-derived first-order conditions
5. Consider adding a KKT consistency checker to validate the generated system

## Related Issues

- Closes #753 (original issue, which focused on `.l` initialization)
- Sprint 20 Day 2 PR #802 (completed `.l` emission feature)
- Deferred to future sprint: KKT transformation refinement
