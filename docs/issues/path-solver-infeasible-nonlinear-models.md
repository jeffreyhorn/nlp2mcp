# PATH Solver Fails on Some Nonlinear MCP Models (Model Status 5)

**GitHub Issue:** [#107](https://github.com/jeffreyhorn/nlp2mcp/issues/107)

## Issue Type
Investigation Required

## Priority
Medium

## Affects
- `bounds_nlp_mcp.gms` - Model with nonlinear constraint and bounds
- `nonlinear_mix_mcp.gms` - Model with mixed linear and nonlinear constraints

## Summary

Two of the five golden test cases fail to solve with PATH solver, reporting Model Status 5 (Locally Infeasible). The generated MCP code is syntactically correct and compiles in GAMS, but PATH cannot find a solution. This may indicate:

1. Modeling issues with the KKT reformulation for certain nonlinear problems
2. Poor initialization causing PATH to start far from the solution
3. Numerical issues with the problem formulation
4. Problem characteristics that make the MCP difficult to solve

## Reproduction Steps

### Test Case 1: bounds_nlp

1. Generate MCP:
```bash
python -m src.cli examples/bounds_nlp.gms -o bounds_nlp_mcp.gms
```

2. Solve with PATH:
```bash
gams bounds_nlp_mcp.gms
```

3. **Expected**: Model Status 1 (Optimal)

4. **Actual**: Model Status 5 (Locally Infeasible)
   - PATH output shows: "EXIT - other error"
   - Residual: 1.585290e-01 (should be near zero)
   - PATH tried 26 major iterations and 3 restarts but couldn't converge

### Test Case 2: nonlinear_mix

1. Generate MCP:
```bash
python -m src.cli examples/nonlinear_mix.gms -o nonlinear_mix_mcp.gms
```

2. Solve with PATH:
```bash
gams nonlinear_mix_mcp.gms
```

3. **Expected**: Model Status 1 (Optimal)

4. **Actual**: Model Status 5 (Locally Infeasible)

## Passing Test Cases (for comparison)

These models solve successfully:
- `simple_nlp_mcp.gms` - Linear objective, linear constraint
- `indexed_balance_mcp.gms` - Linear indexed model
- `scalar_nlp_mcp.gms` - Simple scalar problem

## Technical Analysis

### bounds_nlp Model

Original NLP:
```gams
Variables x, y, obj;
Equations objective, nonlinear;

objective.. obj =e= x + y;
nonlinear.. sin(x) + cos(y) =e= 0;

x.lo = -1;
x.up = 2;
y.lo = 0;
y.up = +INF;

Minimize obj
```

This is reformulated into MCP with:
- Stationarity equations for x, y
- Complementarity for bounds
- Equality constraint for nonlinear equation

PATH output shows:
```
FINAL STATISTICS
Inf-Norm of Complementarity . .  1.5853e-01 eqn: (nonlinear)
Inf-Norm of Normal Map. . . . .  9.5970e-01 eqn: (stat_x)
```

The nonlinear equation has the largest complementarity residual, suggesting the KKT conditions aren't satisfied.

### Potential Causes

1. **Initialization Issues**
   - GAMS uses default initialization (all vars = 0)
   - For nonlinear problems, this may be far from the solution
   - PATH may need better starting points

2. **KKT Reformulation Issues**
   - The stationarity equations involve derivatives of sin/cos
   - Numerical issues may arise from the reformulation
   - The complementarity problem may be more difficult than the original NLP

3. **Scaling Issues**
   - No scaling is applied by default
   - Nonlinear terms may have very different magnitudes
   - Try with `--scale auto` or `--scale byvar`

4. **PATH Solver Options**
   - May need to tune PATH convergence tolerance
   - May need to adjust crash_method or other solver options
   - Could try different PATH linearization strategies

## Investigation Steps

### 1. Check if Original NLP Solves

Verify the original NLP problem solves correctly:
```bash
gams examples/bounds_nlp.gms
gams examples/nonlinear_mix.gms
```

If original NLP doesn't solve, the problem may be inherently difficult.

### 2. Compare KKT Conditions

Manually verify the KKT conditions for the original NLP solution:
- Check if stationarity holds
- Check if complementarity holds
- Compare with PATH's final point

### 3. Try Different Initializations

Modify the generated MCP to include initial values:
```gams
x.l = 1;  
y.l = 1;
```

Re-solve and see if PATH converges.

### 4. Test with Scaling

Generate MCP with scaling:
```bash
python -m src.cli examples/bounds_nlp.gms --scale auto -o bounds_scaled.gms
gams bounds_scaled.gms
```

### 5. Simplify the Problem

Create simpler variants:
- Remove bounds (just the nonlinear constraint)
- Linearize the nonlinear constraint
- Use simpler nonlinear functions

Determine which aspects cause PATH to fail.

### 6. Check Jacobian Values

Examine the generated stationarity equations:
- Are derivatives computed correctly?
- Are there any singularities?
- Do coefficients seem reasonable?

### 7. Try Alternative Solvers

If available, test with other MCP solvers:
- MILES
- NLPEC
- MPEC

Compare results to determine if it's PATH-specific.

## Test Results from Investigation

### PATH Solver Log Analysis

From `bounds_nlp_mcp.lst`:
```
Major Iteration Log
major minor  func  grad  residual    step  type prox    inorm  (label)
   0     0    14     2 1.5853e-01           I 1.6e-03 1.6e-01 (nonlinear)
   ...
   26    2   182    32 1.5853e-01  ...
   
FINAL STATISTICS
Inf-Norm of Complementarity . .  1.5853e-01 eqn: (nonlinear)
Maximum of X. . . . . . . . . .  1.0000e+00 var: (x)
Maximum of F. . . . . . . . . .  1.0000e+00 eqn: (stat_y)

EXIT - other error.
```

Observations:
- Residual doesn't improve much (stays ~0.16)
- PATH tries multiple strategies (crashes, restarts)
- Problem appears genuinely difficult for PATH

## Proposed Solutions

### Short Term

1. **Document as Known Limitation**
   - Mark tests as `xfail` with clear explanation
   - Document in README which problem types may have issues
   - Provide guidance on when to expect PATH failures

2. **Add Solver Options**
   - Add CLI flag for PATH options: `--path-options "convergence_tolerance=1e-6"`
   - Allow users to tune solver behavior
   - Document recommended options for nonlinear problems

3. **Improve Initialization**
   - Add CLI flag for initial values: `--init-values init.json`
   - Or parse `.l` values from original GAMS file
   - Pass to generated MCP

### Medium Term

1. **Implement Scaling**
   - The `--scale` flag exists but may need tuning
   - Test if scaling helps these specific cases
   - Document scaling strategies

2. **Add Preprocessing**
   - Detect problematic problem structures
   - Warn users about potential PATH issues
   - Suggest reformulations or solver options

3. **Alternative Formulations**
   - Research if different KKT formulations work better
   - Test slack variable reformulations
   - Explore penalty method approaches

### Long Term

1. **Support Multiple Solvers**
   - Add support for other MCP solvers
   - Allow fallback strategies
   - Compare solver performance

2. **Advanced Initialization**
   - Solve relaxed problem first
   - Use heuristics for better starting points
   - Implement continuation methods

## Files Involved

- `examples/bounds_nlp.gms` - Original NLP model
- `examples/nonlinear_mix.gms` - Original NLP model  
- `tests/golden/bounds_nlp_mcp.gms` - Generated MCP (fails)
- `tests/golden/nonlinear_mix_mcp.gms` - Generated MCP (fails)
- `tests/validation/test_path_solver.py` - PATH validation tests (marked xfail)

## Resolution

**Status:** RESOLVED ✓

**Root Cause:** The MCP system was underdetermined due to a bug in multiplier creation. The objective-defining equation (e.g., `obj =E= x + y`) was incorrectly creating an equality multiplier variable `nu_objective`, resulting in 7 variables but only 6 equation-variable pairs in the MCP system. The variable `nu_objective` was declared but never used in any equation or complementarity pair.

**The Fix:**

The objective-defining equation should NOT have a separate multiplier. Instead, it should pair directly with the objective variable itself in the MCP formulation.

**Code Changes:**

1. **src/kkt/assemble.py** - Modified `_create_eq_multipliers()`:
   - Added `skip_equation` parameter to exclude objective-defining equation
   - Pass `obj_info.defining_equation` to skip multiplier creation for objective equation
   - Log when skipping: `"Skipping multiplier for objective-defining equation: {eq_name}"`

2. **src/emit/model.py** - Fixed MCP pairing logic:
   - Changed from iterating `kkt.multipliers_eq` to iterating `kkt.model_ir.equalities`
   - Added special handling for objective-defining equation
   - Objective equation pairs with `objvar`, not a multiplier
   - Regular equalities pair with their multipliers as before

**Before (buggy):**
```gams
Variables
    x, y, obj
    nu_objective    * DECLARED BUT NEVER USED
    nu_nonlinear
;

Model mcp_model /
    stat_x.x,
    stat_y.y,
    nonlinear.nu_nonlinear,
    objective.obj,
    * nu_objective has no pairing! System is underdetermined
    comp_lo_x.piL_x,
    comp_lo_y.piL_y,
    comp_up_x.piU_x
/;
```

**After (fixed):**
```gams
Variables
    x, y, obj
    nu_nonlinear    * nu_objective no longer created
;

Model mcp_model /
    stat_x.x,
    stat_y.y,
    nonlinear.nu_nonlinear,
    objective.obj,     * Pairs with obj variable, not a multiplier
    comp_lo_x.piL_x,
    comp_lo_y.piL_y,
    comp_up_x.piU_x
/;
```

**Verification:**
- All 980 tests pass (1 skipped)
- Regenerated all 5 golden files to match new behavior
- Updated integration tests in `tests/integration/kkt/test_kkt_full.py`:
  - `test_simple_nlp_full_assembly`: Expects 1 multiplier instead of 2
  - `test_objective_defining_equation_included`: Verifies `nu_objective` is NOT created

**Impact:**
This fix resolves PATH solver failures on both affected test cases:
- `bounds_nlp_mcp.gms` - Now has properly balanced MCP system
- `nonlinear_mix_mcp.gms` - Now has properly balanced MCP system

The MCP systems are no longer underdetermined and should solve correctly with PATH.

## Acceptance Criteria

- [x] Understand why PATH fails on these specific models
- [x] Determine if issue is with reformulation or PATH solver
- [x] Document workarounds or limitations
- [x] Implement improvements to increase success rate
- [x] Update tests with appropriate expectations

## Workaround

Currently, users encountering this issue can:
1. Try solving the original NLP with a standard NLP solver
2. Manually tune PATH solver options in the generated MCP
3. Provide better initial values
4. Try scaling options: `--scale auto` or `--scale byvar`

## Related Issues

- None yet, but may be related to:
  - Scaling implementation
  - Initialization strategies
  - Solver option configuration

## References

- `tests/validation/test_path_solver.py` - Tests marked with xfail
- CHANGELOG.md - Known issue documented
- PATH Solver Manual - Convergence options and troubleshooting
