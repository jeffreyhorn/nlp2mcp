# Bug: Jacobian Computation Fails for Equality-Type Bounds (`.fx`)

**GitHub Issue:** [#63](https://github.com/jeffreyhorn/nlp2mcp/issues/63)  
**Status:** Open  
**Created:** 2025-11-01

## Summary

The constraint jacobian computation fails with a `KeyError` when processing fixed variables (`.fx` bounds) because `_compute_equality_jacobian()` only searches `model.equations` dictionary, missing equality-type bounds stored in `model.normalized_bounds`.

## Severity

**Critical** - Blocks end-to-end usage of fixed variables (`.fx`), a common GAMS modeling pattern.

## Affected Component

`src/ad/constraint_jacobian.py`, specifically:
- Function: `_compute_equality_jacobian()`
- Line: 199

## Steps to Reproduce

1. Create a GAMS model with a fixed variable:
   ```gams
   Variables x, obj;
   x.fx = 10.0;
   
   Equations objdef;
   objdef.. obj =e= x;
   
   Model test /all/;
   Solve test using NLP minimizing obj;
   ```

2. Parse and normalize the model:
   ```python
   from src.ir.parser import parse_model_file
   from src.ir.normalize import normalize_model
   
   model = parse_model_file("test.gms")
   normalize_model(model)
   ```

3. Attempt to compute derivatives:
   ```python
   from src.ad.api import compute_derivatives
   compute_derivatives(model)  # Fails here
   ```

## Error Message

```
KeyError: 'x_fx'
```

## Root Cause

When a variable has `.fx` set, the normalization phase correctly:
1. Creates an equality constraint `x - fx_value = 0` with `Rel.EQ`
2. Stores it in `model.normalized_bounds["x_fx"]`
3. Adds `"x_fx"` to the `model.equalities` list

However, `_compute_equality_jacobian()` assumes ALL equalities are in `model.equations`:

```python
def _compute_equality_jacobian(model_ir: ModelIR, index_mapping, J_h: JacobianStructure) -> None:
    """Compute Jacobian for equality constraints."""
    from .index_mapping import enumerate_equation_instances

    for eq_name in model_ir.equalities:
        eq_def = model_ir.equations[eq_name]  # <-- KeyError: 'x_fx' not here!
        # ...
```

The issue is that equality-type bounds (`.fx`) are stored in `normalized_bounds`, not `equations`.

## Expected Behavior

The function should check both dictionaries:
1. First check if the equality is in `model.equations` (user-defined constraints)
2. If not found, check if it's in `model.normalized_bounds` (bound-derived constraints)
3. Process accordingly

## Proposed Fix

```python
def _compute_equality_jacobian(model_ir: ModelIR, index_mapping, J_h: JacobianStructure) -> None:
    """Compute Jacobian for equality constraints."""
    from .index_mapping import enumerate_equation_instances

    for eq_name in model_ir.equalities:
        # Check both equations dict and normalized_bounds dict
        if eq_name in model_ir.equations:
            eq_def = model_ir.equations[eq_name]
        elif eq_name in model_ir.normalized_bounds:
            eq_def = model_ir.normalized_bounds[eq_name]
        else:
            # Skip if not found in either location (shouldn't happen)
            continue
        
        # ... rest of the function proceeds as before
        
        # Get all instances of this equation (handles indexed constraints)
        eq_instances = enumerate_equation_instances(eq_name, eq_def.domain, model_ir)
        
        # ... (existing code)
```

## Additional Considerations

### Similar Issue in `_compute_inequality_jacobian`?

The function `_compute_inequality_jacobian()` (line ~246) has the same pattern. However, it processes only items from `model.inequalities` list, and currently all inequality bounds go through `_compute_bound_jacobian()` which correctly accesses `normalized_bounds`.

**But:** If in the future we have inequality-type bounds that get added to the `inequalities` list, this function would have the same bug.

**Recommendation:** Apply the same fix pattern to `_compute_inequality_jacobian()` for consistency and future-proofing.

### Separation of Concerns

A deeper architectural question: Should equality-type bounds be:
- **Option A**: Treated as equalities in J_h (current approach, requires the fix above)
- **Option B**: Handled separately in a dedicated bounds jacobian function
- **Option C**: Never added to the `equalities` list in the first place

Current code seems to assume **Option A**, which makes sense (fixed variables are equality constraints). The fix above maintains this design.

## Impact

**Current Status:**
- Parser: ✅ Works (extracts `.fx` correctly)
- Normalization: ✅ Works (creates equality constraints)
- Partition: ✅ Works (identifies fixed variables)
- Jacobian: ❌ **BROKEN** (this bug)
- KKT Assembly: ❌ **BLOCKED** (depends on jacobian)
- MCP Emission: ❌ **BLOCKED** (depends on KKT)

**Once Fixed:**
- Will unlock full support for fixed variables (`.fx`)
- Will allow testing of KKT treatment and MCP emission strategies
- Will enable end-to-end models with fixed parameters

## Test Case

Test case that demonstrates the bug:
- `tests/research/fixed_variable_verification/test_kkt.py`
- Expected to fail until bug is fixed
- Once fixed, this test should pass and validate the entire pipeline

## Related Research

- See `RESEARCH_SUMMARY_FIXED_VARIABLES.md` for complete analysis
- See `docs/planning/EPIC_1/SPRINT_4/KNOWN_UNKNOWNS.md` Unknown 1.3 for verification results
- Test files in `tests/research/fixed_variable_verification/`

## Workaround

None currently. Fixed variables (`.fx`) cannot be used in models until this bug is fixed.

## References

- Issue discovered during: Unknown 1.3 research (Sprint 4 pre-planning)
- Branch: `research-unknown-1-3-fixed-variables`
- Related to: GAMS `.fx` attribute (fix variable value)
