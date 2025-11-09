# KKT Assembly Bug: Equality Multipliers Missing from Stationarity Equations

**GitHub Issue:** [#106](https://github.com/jeffreyhorn/nlp2mcp/issues/106)

**Status:** ✅ FIXED in PR [#110](https://github.com/jeffreyhorn/nlp2mcp/pull/110)

## Issue Type
Bug - Critical

## Priority
High (RESOLVED)

## Affects
- Min/max reformulation (auxiliary variables)
- Fixed variables (`.fx` syntax)
- Any feature that adds equality constraints after initial model construction

## Summary

When auxiliary variables or fixed variables participate in equality constraints, their stationarity equations do not include the equality constraint multiplier terms. This causes GAMS to reject the generated MCP model with error "no ref to var in equ.var".

## Reproduction Steps

### Example 1: Min/Max Reformulation

1. Create a test file `min_test.gms`:
```gams
Variables x, y, z, obj ;
Equations objective, min_constraint ;

objective.. obj =e= z;
min_constraint.. z =e= min(x, y);

x.lo = 1;
y.lo = 2;

Model min_nlp / objective, min_constraint / ;
Solve min_nlp using NLP minimizing obj ;
```

2. Run nlp2mcp:
```bash
python -m src.cli min_test.gms -o min_mcp.gms
```

3. Try to solve with GAMS:
```bash
gams min_mcp.gms
```

4. **Expected**: MCP model solves successfully

5. **Actual**: GAMS errors:
```
*** Error 69: Dimension of variable is unknown
*** Error 483: Mapped variables have to appear in the model
*** nu_min_constraint no ref to var in equ.var
```

### Example 2: Fixed Variables

1. Create test file `fixed_test.gms`:
```gams
Variables x, y, obj ;
Equations objective ;

objective.. obj =e= x + y;
y.fx = 3;

Model fixed_nlp / objective / ;
Solve fixed_nlp using NLP minimizing obj ;
```

2. Run nlp2mcp:
```bash
python -m src.cli fixed_test.gms -o fixed_mcp.gms
```

3. Try to solve with GAMS:
```bash
gams fixed_mcp.gms
```

4. **Expected**: MCP model solves successfully

5. **Actual**: GAMS errors:
```
*** Error 69: Dimension of variable is unknown  
*** Error 483: Mapped variables have to appear in the model
*** nu_y_fx no ref to var in equ.var
```

## Technical Analysis

### What Should Happen

For min/max reformulation, when we have:
- Original equation: `z = min(x, y)`
- Reformulated to: `z = aux_min` with complementarity constraints
- Equality constraint: `min_constraint: z = aux_min` with multiplier `nu_min_constraint`

The stationarity equation for `aux_min` should be:
```
stat_aux_min.. ∂f/∂aux_min + nu_min_constraint + λ₁ + λ₂ = 0
```

Where:
- `∂f/∂aux_min` = gradient of objective w.r.t. aux_min (usually 0)
- `nu_min_constraint` = multiplier for the equality constraint `z = aux_min`
- `λ₁, λ₂` = multipliers for complementarity constraints

### What Actually Happens

The generated stationarity equation is:
```gams
stat_aux_min.. 0 + 1 * lam_comp_arg0 + 1 * lam_comp_arg1 =E= 0;
```

**Missing**: The `nu_min_constraint` term is completely absent.

### Root Cause

The issue is in how stationarity equations are assembled. The gradient computation
appears to:

1. Compute ∇f (objective gradient)
2. Add terms from inequality Jacobian (J_ineq^T λ)
3. Add terms from equality Jacobian (J_eq^T ν)

However, when auxiliary or fixed variables are added:
- They are added to `model.variables`
- New equality constraints are added to `model.equations`
- But the gradient computation doesn't recognize that these new variables participate in the new equality constraints

The stationarity computation likely happens in `src/kkt/stationarity.py` and uses:
- `src/ad/gradient.py` - compute_objective_gradient()
- `src/ad/constraint_jacobian.py` - compute_constraint_jacobian()

The Jacobian should include derivatives of the new equality constraints w.r.t. the auxiliary variables, but these derivatives either:
1. Aren't being computed, OR
2. Are computed but not included in the stationarity assembly

## Files Involved

- `src/kkt/stationarity.py` - Assembles stationarity equations
- `src/ad/gradient.py` - Computes objective gradient
- `src/ad/constraint_jacobian.py` - Computes constraint Jacobians
- `src/kkt/assemble.py` - Main KKT assembly orchestration
- `src/kkt/reformulation.py` - Min/max reformulation (adds auxiliary variables)
- `src/ir/normalize.py` - Fixed variable handling

## Proposed Solution

### Investigation Steps

1. **Trace Jacobian computation for auxiliary variables**
   - Set breakpoint in `compute_constraint_jacobian()`
   - Check if `min_constraint` equation appears in equality Jacobian
   - Check if derivative of `min_constraint` w.r.t. `aux_min` is computed
   - Verify Jacobian entry: `J_eq[min_constraint, aux_min]` should = 1

2. **Trace stationarity assembly**
   - Set breakpoint in stationarity equation assembly
   - Check if equality Jacobian terms are being added for auxiliary variables
   - Verify that `nu_min_constraint` multiplier is being referenced

3. **Check IndexMapping**
   - Verify auxiliary variables are properly indexed
   - Check that equality constraints include auxiliary variables in their domains

### Potential Fix Locations

#### Option 1: Ensure Jacobian Includes New Constraints

In `src/ad/constraint_jacobian.py`:
```python
def compute_constraint_jacobian(model_ir, normalized_eqs, config):
    # Current: May not include dynamically added equality constraints
    # Fix: Ensure ALL equations in model_ir.equalities are processed
    
    # Check that auxiliary variables appear in IndexMapping
    # Check that new equality constraints are in normalized_eqs
```

#### Option 2: Special Handling in Stationarity Assembly

In `src/kkt/stationarity.py`:
```python
def assemble_stationarity_equations(...):
    # After adding objective gradient and Jacobian terms
    # Add special handling for auxiliary variables
    
    for var_name in auxiliary_variables:
        # Find equality constraints where this variable appears
        # Add corresponding multiplier terms explicitly
```

#### Option 3: Update Reformulation to Mark Variables

In `src/kkt/reformulation.py`:
```python
def reformulate_model(model):
    # After creating auxiliary variables
    # Mark them with metadata indicating which equality they participate in
    aux_var.metadata['equality_constraint'] = 'min_constraint'
    aux_var.metadata['multiplier'] = 'nu_min_constraint'
```

## Test Cases

Create tests that verify:
1. Min reformulation generates valid MCP (test currently fails)
2. Max reformulation generates valid MCP
3. Fixed variables generate valid MCP (test currently fails)
4. Multiple min/max in same model
5. Nested min/max (flattened to single level)

## Acceptance Criteria

- [ ] Min/max reformulated models solve successfully with PATH
- [ ] Fixed variable models solve successfully with PATH  
- [ ] Stationarity equations include all relevant multiplier terms
- [ ] GAMS does not report "no ref to var in equ.var" errors
- [ ] All new test cases pass

## Related Files

- `examples/min_max_test.gms` - Test case that exhibits the bug
- `examples/fixed_var_test.gms` - Test case that exhibits the bug
- `tests/unit/kkt/test_reformulation.py` - Unit tests for reformulation
- `docs/planning/EPIC_1/SPRINT_4/PLAN.md` - Sprint 4 planning (Days 3-4 cover min/max)

## Solution

**Fixed in commit 5c7198d on branch feature/fix-kkt-equality-multipliers**

### Root Causes Identified

1. **Missing inequality list update**: `reformulate_model()` added complementarity constraints to `model.equations` but not to `model.inequalities`, excluding them from J_ineq

2. **Shared index mapping with global row numbering**: J_eq and J_ineq used same index mapping with global row IDs, causing mismatches when Jacobians had separate row counts

3. **Bound double-counting**: Bounds in both `model.inequalities` and `model.normalized_bounds` were counted twice when allocating J_ineq rows

### Changes Made

1. **src/kkt/reformulation.py** (line 707-710):
   ```python
   for constraint_name, constraint_def in result.constraints:
       model.add_equation(constraint_def)
       # NEW: Add to inequalities list so compute_constraint_jacobian includes them in J_ineq
       model.inequalities.append(constraint_name)
   ```

2. **src/ad/constraint_jacobian.py**:
   - Created `_build_equality_index_mapping()` - separate mapping for J_eq with rows 0..num_equalities-1
   - Updated `_build_inequality_index_mapping()` - separate mapping for J_ineq with rows 0..num_inequalities-1
   - Fixed `_count_equation_instances()` - check both `model.equations` and `model.normalized_bounds`
   - Removed bound double-counting - they're already in `model.inequalities`
   - Removed separate `_compute_bound_jacobian()` call - now handled in `_compute_inequality_jacobian()`

3. **Test updates**:
   - Updated `test_mapping_consistency()` to reflect separate index mappings
   - Removed `xfail` from auxiliary constraints research test
   - Regenerated golden files

### Verification

```bash
# Min/max reformulation now works
python -m src.cli examples/min_max_test.gms -o min_mcp.gms
grep "stat_aux_min" min_mcp.gms
# Output: stat_aux_min.. 0 + (-1) * nu_min_constraint + ...

# Fixed variables now work
python -m src.cli examples/fixed_var_test.gms -o fixed_mcp.gms
grep "stat_y" fixed_mcp.gms
# Output: stat_y.. 1 + 1 * nu_y_fx =E= 0;
```

### Test Results
- ✅ All e2e and unit tests pass (127 tests)
- ✅ Auxiliary constraints research test passes (was xfail)
- ✅ Type checking passes
- ✅ Min/max reformulation test cases pass
- ✅ Fixed variable test cases pass

## Workaround

~~None currently available. The features are non-functional until this bug is fixed.~~

**FIXED** - Upgrade to version with commit 5c7198d or later.

## References

- PR: https://github.com/jeffreyhorn/nlp2mcp/pull/110
- Commit: 5c7198d
- SPRINT_4/PLAN.md - Day 3-4: Min/max reformulation
- SPRINT_4/KNOWN_UNKNOWNS.md - Unknown 2.1, 2.2 (min/max reformulation approach)
- CHANGELOG.md - Documents this issue under "Known Issues - Min/Max and Fixed Variables"
