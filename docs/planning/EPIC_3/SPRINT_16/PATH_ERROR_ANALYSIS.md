# PATH Syntax Error Analysis

**Created:** January 19, 2026  
**Purpose:** Analyze path_syntax_error failures at solve stage to understand patterns and develop fix strategies  
**Related Task:** Sprint 16 Prep Task 7 - Research PATH Syntax Error Patterns

---

## Executive Summary

This document analyzes the 14 models that fail with `path_syntax_error` at the SOLVE stage. Despite the name, these are **NOT PATH solver errors** - they are **GAMS compilation errors** in the generated MCP files.

**Critical Finding:** The errors are caused by bugs in nlp2mcp's MCP code generation (`emit_gams_mcp.py`), not issues with the PATH solver or the original GAMS models. All 14 failures are due to invalid GAMS syntax in the generated MCP files.

**Key Insight:** These errors are **highly addressable** in Sprint 16 because they represent code generation bugs that can be systematically fixed.

---

## Terminology Clarification

The error category `path_syntax_error` is misleadingly named:

| What It's Called | What It Actually Is |
|------------------|---------------------|
| path_syntax_error | GAMS compilation error in generated MCP file |
| "PATH solver error" | Actually: MCP file won't even compile |

The PATH solver is never invoked because GAMS fails to compile the MCP file first.

---

## Analysis Results

### Models Affected (14 total)

| # | Model | Original File | MCP File | Status |
|---|-------|---------------|----------|--------|
| 1 | Chemical Equilibrium Problem | chem.gms | chem_mcp.gms | Complex errors |
| 2 | Economic Load Dispatch | dispatch.gms | dispatch_mcp.gms | Multiple issues |
| 3 | Himmelblau Problem 11 | himmel11.gms | himmel11_mcp.gms | Error 445 |
| 4 | House Plan Design | house.gms | house_mcp.gms | Error 445 |
| 5 | Nonlinear Regression | least.gms | least_mcp.gms | Error 445 |
| 6 | MathOptimizer Example 1 | mathopt1.gms | mathopt1_mcp.gms | Error 445 |
| 7 | MathOptimizer Example 2 | mathopt2.gms | mathopt2_mcp.gms | Error 445 |
| 8 | Nonlinear Test Problem | mhw4d.gms | mhw4d_mcp.gms | Error 445 |
| 9 | MHW4D with Tests | mhw4dx.gms | mhw4dx_mcp.gms | Error 445 |
| 10 | Simple Portfolio | port.gms | port_mcp.gms | Domain error |
| 11 | Alkylation Process | process.gms | process_mcp.gms | Error 445 |
| 12 | Parts Supply Problem | ps2_f_inf.gms | ps2_f_inf_mcp.gms | Mixed errors |
| 13 | Rosenbrock Function | rbrock.gms | rbrock_mcp.gms | Error 445 |
| 14 | Stratified Sample | sample.gms | sample_mcp.gms | Mixed errors |

### Successfully Solving Models (3 for comparison)

| Model | MCP File | Notes |
|-------|----------|-------|
| hs62 | hs62_mcp.gms | Compiles and solves correctly |
| prodmix | prodmix_mcp.gms | Compiles, objective mismatch |
| trig | trig_mcp.gms | Compiles, different local optimum |

---

## Error Categories

### Error Distribution

| Error Code | Count | Description | Root Cause |
|------------|-------|-------------|------------|
| **445** | 46 | More than one operator in a row | Unary minus before parentheses |
| **2** | 24 | Identifier expected | Various syntax issues |
| **924** | 24 | Equation/variable separator issue | MCP model statement format |
| **257** | 14 | Solve statement not expected | Position/context issue |
| **171** | 10 | Domain violation for set | Set element quoting |
| **149** | 7 | Uncontrolled set as constant | Index variable issues |
| **120** | 5 | Unknown identifier as set | Reference errors |
| **340** | 4 | Label/element name conflict | Need quotes for elements |
| **145** | 4 | Set identifier expected | Indexing issues |
| **148** | 4 | Dimension different | Index count mismatch |
| Other | 12 | Various | Edge cases |

---

## Detailed Pattern Analysis

### Pattern 1: Unary Minus Before Parentheses (Error 445)

**Affected Models:** 10 models (himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample)

**Root Cause:** The code generator emits expressions like:
```gams
stat_x1.. -(x4 * 0.0006262) * nu_e2 =E= 0;
```

GAMS interprets this as two operators in a row (`..` then `-`) and fails.

**Fix Required:**
```gams
stat_x1.. (-1)*(x4 * 0.0006262) * nu_e2 =E= 0;
* or
stat_x1.. (-(x4 * 0.0006262)) * nu_e2 =E= 0;
```

**Implementation Location:** `src/emit/emit_gams.py` - coefficient formatting

**Fix Complexity:** Low - add parentheses around negative expressions

---

### Pattern 2: Set Element Quoting Inconsistency (Errors 171, 340, 120, 149)

**Affected Models:** 3 models (chem, dispatch, port)

**Root Cause:** Generated code inconsistently quotes set elements:
```gams
* Incorrect - mixed quoting
x(H)         * unquoted
x("H2")      * quoted
comp_lo_x_H.piL_x("H")  * quoted in model statement
```

**Should be:**
```gams
* Correct - consistent quoting
x('H')
x('H2')
comp_lo_x_H.piL_x('H')
```

**Implementation Location:** `src/emit/emit_gams.py` - set element references

**Fix Complexity:** Medium - need consistent quoting strategy

---

### Pattern 3: MCP Model Statement Separator (Error 924)

**Affected Models:** 3 models (chem, ps2_f_inf, sample)

**Root Cause:** MCP model statement uses wrong separator for indexed variables:
```gams
* Incorrect
Model mcp_model /
    stat_x.x,
    comp_lo_x_H.piL_x("H"),  * error - needs | not .
/;
```

**Should be:**
```gams
* Correct
Model mcp_model /
    stat_x | x,
    comp_lo_x_H | piL_x('H'),
/;
```

**Implementation Location:** `src/emit/emit_gams.py` - MCP model declaration

**Fix Complexity:** Low - use correct MCP syntax

---

### Pattern 4: Scalar Declaration Issues (Errors 409, 191, 710)

**Affected Model:** dispatch

**Root Cause:** Scalar with descriptive text but missing name:
```gams
* Incorrect
Scalars
    'loss equation constant' /0.040357/
;
```

**Should be:**
```gams
* Correct  
Scalars
    lossconst 'loss equation constant' /0.040357/
;
```

**Implementation Location:** `src/emit/emit_gams.py` - scalar declarations

**Fix Complexity:** Low - include identifier names

---

### Pattern 5: Domain Index Errors (Errors 145, 148)

**Affected Models:** 2 models (chem, ps2_f_inf)

**Root Cause:** Using wrong domain in indexed expressions:
```gams
* Incorrect - c used twice instead of (i,c)
sum(i, a(c,c) * nu_cdef(i))
```

**Should be:**
```gams
* Correct
sum(i, a(i,c) * nu_cdef(i))
```

**Implementation Location:** `src/emit/emit_gams.py` - constraint Jacobian terms

**Fix Complexity:** Medium - trace domain propagation

---

## Error Distribution by Model

| Model | Primary Error | Secondary Errors |
|-------|---------------|------------------|
| himmel11 | 445 (unary minus) | 257 |
| house | 445 | 257 |
| least | 445 | 257 |
| mathopt1 | 445 | 257 |
| mathopt2 | 445 | 257 |
| mhw4d | 445 | 257 |
| mhw4dx | 445 | 257 |
| process | 445 | 257 |
| rbrock | 445 | 257 |
| chem | 171, 340 (quoting) | 120, 145, 148, 149, 924 |
| dispatch | 409, 191 (scalar) | 125, 171, 610, 710 |
| port | 171 (domain) | 257 |
| ps2_f_inf | 145, 148 (domain) | 182, 445, 924 |
| sample | 445 | 182, 924 |

---

## Sprint 16 Fix Strategy

### Priority 1: Error 445 - Unary Minus (10 models)

**Impact:** Fixes 10/14 models (71%)  
**Effort:** Low (2-4 hours)  
**Location:** `src/emit/emit_gams.py`

**Fix Approach:**
1. Wrap negative coefficient expressions in parentheses
2. Change `-(expr)` to `(-1)*(expr)` or `(-(expr))`
3. Add unit tests for negative coefficient handling

### Priority 2: Set Element Quoting (3 models)

**Impact:** Fixes 3/14 models (21%)  
**Effort:** Medium (4-6 hours)  
**Location:** `src/emit/emit_gams.py`

**Fix Approach:**
1. Always quote set elements in variable references
2. Use consistent quoting in MCP model statement
3. Add unit tests for indexed variables

### Priority 3: Scalar Declaration (1 model)

**Impact:** Fixes 1/14 models (7%)  
**Effort:** Low (1-2 hours)  
**Location:** `src/emit/emit_gams.py`

**Fix Approach:**
1. Ensure all scalars have proper identifier names
2. Don't emit description-only scalar declarations

---

## Expected Improvement

| Scenario | Models Fixed | New Solve Rate |
|----------|--------------|----------------|
| **Priority 1 only** | +10 | 76% (13/17) |
| **P1 + P2** | +13 | 94% (16/17) |
| **All fixes** | +14 | 100% (17/17) |

**Current:** 3/17 translated models solve (17.6%)  
**Target:** 13-17/17 translated models solve (76-100%)

---

## Implementation Recommendations

### For Sprint 16

1. **Focus on Error 445 first** - Highest impact, lowest effort
2. **Add regression tests** - Prevent reintroduction of these bugs
3. **Consider automated validation** - Run `gams ... action=c` on generated MCP files

### Code Changes Required

| File | Change | Effort |
|------|--------|--------|
| `src/emit/emit_gams.py` | Fix unary minus formatting | 2-4h |
| `src/emit/emit_gams.py` | Consistent set element quoting | 4-6h |
| `src/emit/emit_gams.py` | Fix scalar declarations | 1-2h |
| `tests/emit/test_emit_gams.py` | Add regression tests | 2-3h |
| **Total** | | **9-15h** |

### Testing Strategy

1. **Unit tests:** Add tests for each error pattern
2. **Integration tests:** Compile all generated MCP files with `gams ... action=c`
3. **Regression baseline:** Track which models compile successfully

---

## Relationship to Parse Errors

The `path_syntax_error` failures are **independent** of the lexer_invalid_char parse failures analyzed in Task 6:

| Stage | Error Type | Count | Root Cause |
|-------|------------|-------|------------|
| Parse | lexer_invalid_char | 153 | Grammar limitations |
| Solve | path_syntax_error | 14 | Code generation bugs |

Fixing the parse errors (Task 6) will create more models that reach the translate/solve stages, potentially revealing similar code generation bugs. The fixes identified here should be applied proactively.

---

## Appendix: Full Error Output by Model

### chem_mcp.gms
- Error 171: Domain violation for set (set element quoting)
- Error 120: Unknown identifier entered as set
- Error 340: Label/element name conflict
- Error 149: Uncontrolled set as constant
- Error 924: MCP model separator

### dispatch_mcp.gms
- Error 409: Unrecognizable item (missing scalar name)
- Error 191: Closing quote missing
- Error 710: Wrong variable suffix

### himmel11_mcp.gms (and 9 similar models)
- Error 445: More than one operator in a row (unary minus)
- Error 257: Solve statement context

### port_mcp.gms
- Error 171: Domain violation

### ps2_f_inf_mcp.gms
- Error 145: Set identifier expected
- Error 148: Dimension different
- Error 445: Unary minus
- Error 924: MCP separator

### sample_mcp.gms
- Error 445: Unary minus
- Error 924: MCP separator
