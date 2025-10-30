# GAMS Code Generator Syntax Errors

**Status**: Partially Fixed (2 of 4 test cases now passing)  
**Priority**: High  
**Component**: Code Generator (KKT Assembly / GAMS Emission)  
**Discovered**: Sprint 3 Day 9 (GAMS Validation)  
**GitHub Issue**: #46  
**Related Issues**: #47 (Indexed Stationarity Equations - remaining work)

> **Note**: Problem 2 (Double Operators) has been fixed. Problem 1 (Domain Violations) 
> requires more extensive refactoring and is tracked separately in GitHub issue #47.

## Summary

The GAMS MCP code generator produces syntactically invalid GAMS code in 4 out of 5 test cases. These errors prevent the generated files from being compiled by GAMS, even though they are used as "golden" reference files in our test suite.

With the improvements to GAMS validation in Sprint 3 Day 9, we can now accurately detect these syntax errors. The affected files have been marked with `@pytest.mark.xfail` in the test suite pending fixes to the code generator.

## Problem 1: Domain Violations with Indexed Sets

**Affected files:**
- `tests/golden/simple_nlp_mcp.gms`
- `tests/golden/indexed_balance_mcp.gms`

**GAMS Error Codes:**
- Error 120: Unknown identifier entered as set
- Error 149: Uncontrolled set entered as constant
- Error 171: Domain violation for set
- Error 340: A label/element with the same name exists

### Root Cause

The generator treats individual set elements (e.g., `i1`, `i2`, `i3`) as if they were separate sets/indices, rather than as elements of a parent set `i`.

### Example from `simple_nlp_mcp.gms`

**Current (incorrect) output:**

```gams
Sets
    i /i1, i2, i3/
;

Variables
    x(i)
;

Equations
    stat_x_i1    ! ❌ WRONG: Declares equation without domain
    stat_x_i2
    stat_x_i3
;

stat_x_i1(i1).. x(i1) * 0 + ... + lam_balance(i1) + ... + lam_balance(i2) + ... =E= 0;
          ^^                      ^^             ^^               ^^             ^^
          Uses i1, i2, i3 as if they were sets, but they're elements of set i
```

### Proposed Solution

The generator should either:

**Option A: Use the parent set as the domain**

```gams
Equations
    stat_x(i)    ! ✅ CORRECT: Use parent set as domain
;

stat_x(i).. x(i) * 0 + ... + sum(j, jacobian(i,j) * lam_balance(j)) =E= 0;
```

**Option B: Use element-specific equations with proper quoting**

```gams
Alias(i, i1_alias, i2_alias, i3_alias);

Equations
    stat_x_i1
    stat_x_i2  
    stat_x_i3
;

stat_x_i1.. x('i1') * 0 + ... =E= 0;  ! Quote element names
```

**Recommendation**: Option A is preferred as it's more general and scalable.

---

## Problem 2: Double Operators (Unparenthesized Negative Terms)

**Affected files:**
- `tests/golden/bounds_nlp_mcp.gms`
- `tests/golden/nonlinear_mix_mcp.gms`

**GAMS Error Code:**
- Error 445: More than one operator in a row. You need to use parenthesis

### Root Cause

When emitting derivative terms with negative coefficients, the generator produces expressions like `+ -sin(y)` which GAMS interprets as two consecutive operators.

### Example from `bounds_nlp_mcp.gms` line 66

**Current (incorrect) output:**

```gams
stat_x.. 1 + 0 + (cos(x) * 1 + -sin(y) * 0 - 0) * nu_nonlinear - piL_x + piU_x =E= 0;
                                ^^^^^^^
                                ❌ WRONG: "+ -sin(y)" is invalid
```

### Proposed Solution

**Option A: Parenthesize negative terms**

```gams
stat_x.. 1 + 0 + (cos(x) * 1 + (-sin(y)) * 0 - 0) * nu_nonlinear - piL_x + piU_x =E= 0;
                                ^^^^^^^^^^
                                ✅ CORRECT: Parenthesize negative function calls
```

**Option B: Combine operators algebraically**

```gams
stat_x.. 1 + 0 + (cos(x) * 1 - sin(y) * 0 - 0) * nu_nonlinear - piL_x + piU_x =E= 0;
                              ^
                              ✅ CORRECT: Combine + and - into single -
```

**Recommendation**: Option B is preferred when possible (cleaner output), with Option A as fallback.

---

## Impact

- **Severity**: High - Generated GAMS files cannot be compiled
- **Affected Components**: 
  - `src/kkt/assembly.py` (likely the Jacobian/derivative handling)
  - `src/emit/gams.py` (GAMS code emission)
- **Test Status**: 4 out of 8 validation tests marked as `xfail`

## Expected Behavior

All generated GAMS MCP files should:

1. Compile without syntax errors when run with `gams <file> action=c`
2. Use proper GAMS domain declarations for indexed equations
3. Parenthesize or simplify negative function calls (e.g., `(-sin(y))` or `- sin(y)`, not `+ -sin(y)`)

## Files to Fix

Based on the error patterns, the fixes likely belong in:

### For Domain Violations

- `src/kkt/assembly.py` - How stationarity equations are indexed
- `src/emit/gams.py` - How equation declarations and model statements are emitted

### For Double Operators

- `src/emit/gams.py` - Expression emission, specifically around unary minus operators
- May need to improve AST-to-GAMS conversion to detect and parenthesize/simplify negative terms

## Test Files Status

| File | Status | Issue |
|------|--------|-------|
| `tests/golden/scalar_nlp_mcp.gms` | ✅ Pass | No indexed variables |
| `tests/golden/simple_nlp_mcp.gms` | ❌ xfail | Domain violations |
| `tests/golden/bounds_nlp_mcp.gms` | ❌ xfail | Double operators |
| `tests/golden/indexed_balance_mcp.gms` | ❌ xfail | Domain violations |
| `tests/golden/nonlinear_mix_mcp.gms` | ❌ xfail | Double operators |

## Related Work

This issue was discovered during Sprint 3 Day 9 when GAMS validation was improved to accurately detect compilation errors. The validation improvements included:

- Better error marker detection (ignoring false positives from section headers)
- Proper identification of GAMS error codes in `.lst` files
- Numeric version sorting for GAMS executable detection

## Acceptance Criteria

- [ ] All 5 golden files compile successfully with GAMS
- [ ] Remove `@pytest.mark.xfail` from 4 validation tests in `tests/validation/test_gams_check.py`
- [ ] Verify fixes don't break existing non-indexed test cases
- [ ] Update golden files if needed after fixing the generator
- [ ] Add regression tests to prevent reintroduction of these errors

## Detailed Error Output

### simple_nlp_mcp.gms Error Summary

```
**** 120  Unknown identifier entered as set
**** 149  Uncontrolled set entered as constant
**** 171  Domain violation for set
**** 300  Remaining errors not printed for this line
**** 340  A label/element with the same name exist
```

Problematic lines (68-70):
```gams
stat_x_i1(i1).. x(i1) * 0 + a(i1) * 1 + (1 - 0) * lam_balance(i1) + (0 - 0) * lam_balance(i2) + (0 - 0) * lam_balance(i3) =E= 0;
stat_x_i2(i2).. x(i2) * 0 + a(i2) * 1 + (0 - 0) * lam_balance(i1) + (1 - 0) * lam_balance(i2) + (0 - 0) * lam_balance(i3) =E= 0;
stat_x_i3(i3).. x(i3) * 0 + a(i3) * 1 + (0 - 0) * lam_balance(i1) + (0 - 0) * lam_balance(i2) + (1 - 0) * lam_balance(i3) =E= 0;
```

### bounds_nlp_mcp.gms Error Summary

```
**** 445  More than one operator in a row. You need to use parenthesis
```

Problematic lines (66-67):
```gams
stat_x.. 1 + 0 + (cos(x) * 1 + -sin(y) * 0 - 0) * nu_nonlinear - piL_x + piU_x =E= 0;
stat_y.. 0 + 1 + (cos(x) * 0 + -sin(y) * 1 - 0) * nu_nonlinear - piL_y =E= 0;
                              ^^^^^^^
                              Problem: + -sin(y)
```

### indexed_balance_mcp.gms Error Summary

```
**** 120  Unknown identifier entered as set
**** 149  Uncontrolled set entered as constant
**** 171  Domain violation for set
**** 340  A label/element with the same name exist
****  39  Colon ':' expected
```

Similar domain violation pattern to `simple_nlp_mcp.gms`.

### nonlinear_mix_mcp.gms Error Summary

```
**** 445  More than one operator in a row. You need to use parenthesis
```

Problematic lines (70-71):
```gams
stat_x.. 1 + 0 + (2 * power(x, 1) * 1 + 2 * power(y, 1) * 0 - 0) * nu_poly_balance + (cos(x) * 1 + -sin(y) * 0 - 0) * nu_nonlinear - piL_x + piU_x =E= 0;
stat_y.. 0 + 1 + (2 * power(x, 1) * 0 + 2 * power(y, 1) * 1 - 0) * nu_poly_balance + (cos(x) * 0 + -sin(y) * 1 - 0) * nu_nonlinear - piL_y =E= 0;
```

## Next Steps

1. Investigate `src/kkt/assembly.py` for how indexed stationarity equations are generated
2. Investigate `src/emit/gams.py` for expression emission logic
3. Implement fixes for both issues
4. Regenerate golden files with corrected code
5. Remove `xfail` markers from tests
6. Verify all validation tests pass
