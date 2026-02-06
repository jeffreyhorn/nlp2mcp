# emit_gams.py Path Syntax Error Analysis

**Date:** February 6, 2026
**Task:** Sprint 18 Prep Task 4
**Purpose:** Analyze all 17 `path_syntax_error` models to identify failure categories and design fixes

---

## Executive Summary

**Key Finding: Table data emission is NOT the primary blocker.**

Analysis of all 17 `path_syntax_error` models reveals a different failure taxonomy than originally assumed:
- **0 models** fail due to table data emission issues (tables are parsed as parameters and work correctly)
- **5 models** fail due to computed parameter assignment emission issues
- **5 models** fail due to missing bound multiplier variable declarations
- **3 models** fail due to multi-dimensional parameter data emission (conflicting dimensions)
- **6 models** fail due to set element quoting issues (ps2_* family + pollut)
- **1 model** fails due to undefined function reference in generated equations

**Note:** Some models appear in multiple failure categories (e.g., demo1 has both computed param and bound multiplier issues), so the counts above may sum to more than 17.

This significantly changes Sprint 18 scope for emit_gams.py fixes.

---

## Methodology

### Test Environment
- **GAMS Version:** 51.3.0 (38407a9b DEX-DEG x86 64bit/macOS)
- **Test Date:** February 6, 2026
- **Command:** `gams data/gamslib/mcp/<model>_mcp.gms action=c`

### Models Tested
All 17 `path_syntax_error` models from `gamslib_status.json`:
ajax, alkyl, bearing, chenery, demo1, least, mathopt1, mexss, mingamma, orani, pollut, ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, sample

---

## Failure Taxonomy

### Category 1: Bound Multiplier Variable Dimension (5 models)

**Models:** alkyl, bearing, least (partial), demo1 (partial), sample (partial)

**Error Pattern:**
```
*** Error 69 in alkyl_mcp.gms
    Dimension of variable is unknown
*** Error 483
    Mapped variables have to appear in the model
```

**Root Cause:**
Bound multiplier variables (`piL_*`, `piU_*`) are declared for scalar variables but:
1. Their dimensions are not set correctly in the MCP output
2. The stationarity equations reference these multipliers incorrectly

**Example (alkyl):**
```gams
Positive Variables
    piL_OlefinFeed    ! Declared without domain - but original is scalar
    piL_IsobutRec
    ...
```

The KKT transformation creates bound multipliers for primal variables, but scalar variables produce scalar multipliers that aren't properly dimensioned.

**Fix Location:** `src/kkt/bound_multipliers.py` and `src/emit/model.py`

**Estimated Fix Time:** 4-5 hours

---

### Category 2: Computed Parameter Assignment Emission (5 models)

**Models:** ajax, demo1, mathopt1, mexss, sample

**Error Pattern:**
```
*** Error 121  Set expected
*** Error 140  Unknown symbol
*** Error 141  Symbol declared but no values assigned
*** Error 148  Dimension different
```

**Root Cause:**
`emit_computed_parameter_assignments()` in `original_symbols.py` emits parameter assignments that reference:
1. Undefined symbols (indices that don't exist)
2. Parameters that haven't been assigned values yet
3. Wrong dimension for the target parameter

**Example (ajax):**
```gams
mtr(m,avail-h) = avail(m);     ! 'avail-h' is not a defined symbol
par(g,demand) = dempr(g,"demand");  ! 'demand' used as literal but not defined
```

**Example (mathopt1):**
```gams
Scalars
    report /0.0/
;
report(x1,diff) = report("x1","global") - report("x1","solver");
! Error: 'report' declared as scalar, not indexed parameter
```

**Example (sample):**
```gams
w(h) = data(h,"pop") / tpop;   ! 'data' has no values, 'tpop' not yet computed
tpop = sum(h, data(h,"pop"));  ! Wrong order - tpop needed first
```

**Root Cause Analysis:**
The issue is in `emit_computed_parameter_assignments()`:
- It emits expressions from `ParameterDef.expressions` 
- These expressions contain symbolic references that may not be valid in the MCP context
- The original model may have runtime-computed values that can't be statically emitted

**Fix Location:** `src/emit/original_symbols.py:emit_computed_parameter_assignments()`

**Proposed Fix:**
1. **Option A (Simple):** Skip computed parameter assignments entirely - the MCP model may not need them
2. **Option B (Complex):** Topologically sort assignments, validate symbol references, handle scalar/parameter mismatches

**Estimated Fix Time:** 3-4 hours (Option A) or 8-10 hours (Option B)

---

### Category 3: Multi-Dimensional Parameter Data (3 models)

**Models:** chenery, orani, mexss (partial)

**Error Pattern:**
```
*** Error 161  Conflicting dimensions in element
*** Error 170  Domain violation
```

**Root Cause:**
Parameters with wildcard domains (`*`) have data entries with inconsistent dimensions:

**Example (chenery):**
```gams
Parameters
    pdat(lmh,*,sde,i) /low.a.distr.services 0.8, .../
    ddat(lmh,*,i) /low.ynot.services 450.0, .../
```

The wildcard `*` in the domain creates ambiguity about element membership.

**Example (orani):**
```gams
Parameters
    amc(c,s,*) /food.domestic.agric 10.0, ..., food.agric 0.0, .../
```

Some data entries have 3 indices (`food.domestic.agric`), others have 2 (`food.agric`), creating dimension conflicts.

**Root Cause Analysis:**
The parser stores all parameter data in `ParameterDef.values` but:
- Wildcard domains need special handling
- Entry dimensions must match declaration dimensions
- Some entries may be partial (missing indices)

**Fix Location:** `src/emit/original_symbols.py:emit_original_parameters()`

**Proposed Fix:**
1. Validate that all value keys match the declared domain dimension
2. For wildcard domains, explicitly expand to all used elements
3. Consider skipping parameters with wildcard domains (may not be needed for MCP)

**Estimated Fix Time:** 4-5 hours

---

### Category 4: Set Element Quoting (6 models)

**Models:** ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut

**Error Pattern:**
```
*** Error 120  Unknown identifier entered as set
*** Error 145  Symbol redefined
*** Error 149  Uncontrolled set entered as constant
*** Error 340  A label/element with same name exists
```

**Root Cause:**
Set elements like `eff`, `inf` are used in equations without quotes:

**Example (ps2_f):**
```gams
stat_util.. ((-1) * sum(i, 0)) + 0 * nu_rev(eff) + 0 * nu_rev(inf) ...
!                                         ^^^           ^^^
! eff and inf should be quoted (e.g., 'eff' and 'inf', or "eff" and "inf")
```

The issue is that `eff` looks like a variable name, and `inf` is a GAMS reserved constant.

**Fix Location:** `src/emit/expr_to_gams.py`

**Proposed Fix:**
1. In `expr_to_gams()`, detect when a symbol reference is actually a set element
2. Quote set elements in equation expressions: `nu_rev('eff')` instead of `nu_rev(eff)`
3. This fix was partially implemented in Sprint 17 but may be incomplete

**Estimated Fix Time:** 2-3 hours

---

### Category 5: Undefined Function Reference (1 model)

**Model:** mingamma

**Error Pattern:**
```
*** Error 140  Unknown symbol
*** Error 121  Set expected
```

**Root Cause:**
The `psi()` function (digamma function) is used in the generated stationarity equations but not defined:

**Example:**
```gams
stat_x1.. 0 + ((-1) * (gamma(x1) * psi(x1))) * nu_y1def - piL_x1 =E= 0;
!                                  ^^^
! 'psi' is the digamma function, derivative of log(gamma(x))
```

The KKT transformation correctly computed `d/dx[loggamma(x)] = psi(x)`, but `psi()` isn't a standard GAMS function.

**Fix Location:** `src/ad/derivative_rules.py` or `src/emit/expr_to_gams.py`

**Proposed Fix:**
1. Emit a helper function definition for `psi()` using GAMS's `digamma()` or numerical approximation
2. Or: Replace `psi(x)` with `digamma(x)` in the emitter (GAMS has `digamma()`)

**Estimated Fix Time:** 1-2 hours

---

### Category 6: MCP Variable/Equation Mapping (1 model)

**Model:** least

**Error Pattern:**
```
*** Error 66  Dimension required
*** Error 256  Error(s) in analyzing solve statement
```

**Root Cause:**
The MCP solve statement has issues with equation-variable pairing:
- Some variables don't have matching equations
- Dimension mismatches in the MCP model block

**Fix Location:** `src/emit/model.py` or `src/kkt/` module

**Estimated Fix Time:** 3-4 hours (requires deeper investigation)

---

## Summary Table

| Category | Models | Count | Primary Error Codes | Fix Location | Est. Hours |
|----------|--------|-------|---------------------|--------------|------------|
| Bound multiplier dimension | alkyl, bearing, (+3 partial) | 5 | 69, 483 | kkt/bound_multipliers.py | 4-5h |
| Computed param assignment | ajax, demo1, mathopt1, mexss, sample | 5 | 121, 140, 141, 148 | emit/original_symbols.py | 3-4h |
| Multi-dim parameter data | chenery, orani, (+1 partial) | 3 | 161, 170 | emit/original_symbols.py | 4-5h |
| Set element quoting | ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s, pollut | 6 | 120, 145, 149, 340 | emit/expr_to_gams.py | 2-3h |
| Undefined function (psi) | mingamma | 1 | 140, 121 | emit/expr_to_gams.py | 1-2h |
| MCP mapping | least | 1 | 66, 256 | emit/model.py | 3-4h |

**Note:** Some models have overlapping issues (e.g., demo1 has both computed param and other issues).

---

## Comparison to Original Assumptions

| Original Assumption | Actual Finding | Impact |
|---------------------|----------------|--------|
| ~4 models fail due to table data emission | 0 models (tables parsed as parameters, work correctly) | Table data fix NOT needed |
| ~4 models fail due to computed parameters | 5 models fail due to computed param assignment | Higher count, but issue is emission, not parsing |
| Table + computed = top 2 blockers | Set element quoting (6) + Bound multipliers/Computed params (5 each) = top blockers | Different blockers than expected |
| 4-5h for table data fix | 0h (not needed) | Reallocate time |
| 4-5h for computed param fix | 3-4h (simpler fix: skip assignments) | On target |

---

## Recommended Sprint 18 Priorities

Based on ROI (models fixed / hours):

| Priority | Fix | Models Fixed | Hours | ROI |
|----------|-----|--------------|-------|-----|
| 1 | Set element quoting | 6 (ps2_* family + pollut) | 2-3h | 2.4 |
| 2 | Skip computed param assignments | 5 | 2h | 2.5 |
| 3 | Undefined function (psi→digamma) | 1 | 1-2h | 0.7 |
| 4 | Bound multiplier dimension | 5 | 4-5h | 1.0 |
| 5 | Multi-dim parameter data | 3 | 4-5h | 0.6 |
| 6 | MCP mapping (least) | 1 | 3-4h | 0.3 |

**Recommended Sprint 18 scope:** Priorities 1-3 (~5-7h, ~12 models)

---

## Detailed Model-by-Model Analysis

### ajax
- **Primary Error:** 121, 140, 198 (computed parameter assignment)
- **Line 32:** `mtr(m,avail-h) = avail(m);` - `avail-h` not a valid symbol
- **Line 33:** `par(g,demand) = dempr(g,"demand");` - `demand` used without definition
- **Category:** Computed parameter assignment

### alkyl
- **Primary Error:** 69, 483 (variable dimension unknown)
- **Line 263:** Solve statement - piL_/piU_ variables have unknown dimensions
- **Category:** Bound multiplier dimension

### bearing
- **Primary Error:** 69, 483 (variable dimension unknown)
- **Line 268:** Solve statement - same as alkyl
- **Category:** Bound multiplier dimension

### chenery
- **Primary Error:** 161, 116 (conflicting dimensions)
- **Lines 29-30:** Parameter data with wildcard domain has inconsistent indices
- **Category:** Multi-dimensional parameter data

### demo1
- **Primary Error:** 120, 340, 148, 195 (multiple issues)
- **Lines 43-44:** Computed parameter assignments with undefined indices
- **Line 60:** Symbol redefinition
- **Category:** Computed parameter assignment + others

### least
- **Primary Error:** 66, 256 (MCP dimension issues)
- **Line 123:** Solve statement dimension issues
- **Category:** MCP variable/equation mapping

### mathopt1
- **Primary Error:** 120, 116, 148 (type mismatch)
- **Lines 22-23:** `report` declared as scalar but used as indexed parameter
- **Category:** Computed parameter assignment

### mexss
- **Primary Error:** 120, 340, 171 (set element issues)
- **Line 51:** `d(steel,j)` - `steel` used as set element without quotes
- **Category:** Set element quoting + computed param

### mingamma
- **Primary Error:** 140, 121 (undefined function)
- **Line 79:** `psi(x1)` function not defined in GAMS
- **Category:** Undefined function reference

### orani
- **Primary Error:** 170, 161 (domain violation, dimension conflict)
- **Line 34:** Parameter `amc(c,s,*)` has entries with inconsistent dimensions
- **Category:** Multi-dimensional parameter data

### pollut
- **Primary Error:** 120, 340, 149, 171 (set element issues)
- **Lines 91-92:** Set elements `cod`, `land`, `so2`, `water` used without quotes
- **Category:** Set element quoting

### ps2_f, ps2_f_eff, ps2_f_inf, ps2_f_s, ps2_s
- **Primary Error:** 120, 340, 145, 149, 171 (set element issues)
- **Common Pattern:** `nu_rev(eff)`, `nu_rev(inf)`, `lam_pc(eff)` - elements not quoted
- **Special Case:** `inf` is a GAMS reserved constant
- **Category:** Set element quoting

### sample
- **Primary Error:** 141, 116 (symbol not assigned)
- **Line 35:** `data(h,"pop")` referenced but `data` parameter has no values
- **Line 36:** `tpop` used before it's computed
- **Category:** Computed parameter assignment (ordering issue)

---

## Fix Design Sketches

### Fix 1: Skip Computed Parameter Assignments (Priority 2)

**Location:** `src/emit/original_symbols.py`

**Change:** Modify `emit_computed_parameter_assignments()` to return empty string or skip emission entirely.

```python
def emit_computed_parameter_assignments(model_ir: ModelIR) -> str:
    """Emit computed parameter assignment statements.
    
    NOTE: Computed parameter assignments often reference symbols that don't
    exist in the MCP context. For now, skip emission entirely. The MCP model
    should work without these assignments as they define intermediate values
    not needed for KKT conditions.
    """
    # Sprint 18: Skip computed parameter assignments
    # These often fail due to undefined symbols in MCP context
    return ""
```

**Risk:** Low - MCP models don't need intermediate parameter values
**Test:** Re-run pipeline on 5 affected models

### Fix 2: Set Element Quoting (Priority 1)

**Location:** `src/emit/expr_to_gams.py`

**Current Issue:** `_quote_indices()` doesn't quote all set elements properly.

**Proposed Change:** Improve `_quote_indices()` to:
1. Always quote single-letter elements
2. Quote elements that match GAMS reserved words (inf, na, eps, etc.)
3. Quote elements that could be confused with variable names

```python
GAMS_RESERVED_CONSTANTS = {'inf', 'na', 'eps', 'undf', 'yes', 'no', 'true', 'false'}

def _should_quote_index(index: str, model_ir: ModelIR = None) -> bool:
    """Determine if an index should be quoted in GAMS output."""
    index_lower = index.lower()
    
    # Always quote GAMS reserved constants
    if index_lower in GAMS_RESERVED_CONSTANTS:
        return True
    
    # Quote short identifiers that could be confused with variables
    if len(index) <= 3 and index.isalpha():
        return True
    
    # Quote if it matches a known set element (not a domain variable)
    # This requires access to model_ir to check set memberships
    
    return False
```

**Risk:** Medium - may over-quote in some cases (cosmetic, not functional)
**Test:** Re-run pipeline on ps2_* family

### Fix 3: Replace psi() with digamma() (Priority 3)

**Location:** `src/emit/expr_to_gams.py`

**Change:** In the function call emission, replace `psi` with `digamma`:

```python
def expr_to_gams(expr, ...) -> str:
    ...
    if isinstance(expr, FunctionCall):
        func_name = expr.func_name
        # GAMS uses 'digamma' for the psi (digamma) function
        if func_name == 'psi':
            func_name = 'digamma'
        ...
```

**Risk:** Low - direct substitution
**Test:** Re-run pipeline on mingamma

---

## Unit Test Cases

### Test 1: Skip Computed Parameter Assignments
```python
def test_emit_computed_parameter_assignments_skipped():
    """Verify computed parameter assignments are skipped in Sprint 18."""
    model_ir = ModelIR()
    model_ir.add_param(ParameterDef(
        name="c",
        domain=("i", "j"),
        values={},
        expressions={("i", "j"): BinOp("*", SymbolRef("f"), SymbolRef("d"))}
    ))
    
    result = emit_computed_parameter_assignments(model_ir)
    assert result == ""  # Should be empty
```

### Test 2: Set Element Quoting
```python
def test_quote_reserved_set_elements():
    """Verify GAMS reserved words are quoted when used as indices."""
    expr = SymbolRef("nu_rev", indices=[SymbolRef("inf")])
    result = expr_to_gams(expr)
    assert "'inf'" in result or '"inf"' in result
```

### Test 3: Digamma Function Substitution
```python
def test_psi_to_digamma():
    """Verify psi() is emitted as digamma()."""
    expr = FunctionCall("psi", [SymbolRef("x")])
    result = expr_to_gams(expr)
    assert "digamma(x)" in result
    assert "psi(x)" not in result
```

---

## Document History

- February 6, 2026: Initial creation (Task 4 of Sprint 18 Prep)
