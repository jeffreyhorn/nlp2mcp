# Indexed Assignments Research

**Sprint:** Epic 2 - Sprint 8 Prep  
**Created:** 2025-11-17  
**Purpose:** Deep dive research on indexed assignments feature for Sprint 8 implementation

---

## Executive Summary

Indexed assignments enable assigning values to multi-dimensional parameters and variable attributes using explicit indices. This feature unlocks **2 GAMSLib models** (mathopt1.gms, trig.gms) with **+20% parse rate increase** (3/10 → 5/10 models).

**Key Findings:**
- **Feature Selection:** Indexed assignments confirmed as Sprint 8's second high-ROI feature (after option statements)
- **Unlock Rate:** +20% (2 models: mathopt1.gms + trig.gms)
- **Combined Sprint 8 Impact:** Option statements (+10%) + Indexed assignments (+20%) = **50% parse rate** (optimistic), **30% conservative**
- **Effort Estimate:** 6-8 hours (validated, Medium complexity)
- **Risk Assessment:** Medium risk (grammar changes + semantic validation, no hidden complexity found)
- **Grammar Design:** Minimal changes to existing lvalue rule (already partially supports indexing)
- **Implementation Scope:** Well-defined, 4 GAMS syntax patterns identified

---

## Table of Contents

1. [Task 2 Feature Recommendation Review](#task-2-feature-recommendation-review)
2. [GAMS Syntax Survey](#gams-syntax-survey)
3. [Grammar Design](#grammar-design)
4. [Implementation Plan](#implementation-plan)
5. [Test Fixture Design](#test-fixture-design)
6. [Risk Assessment](#risk-assessment)
7. [Models Unlocked](#models-unlocked)

---

## Task 2 Feature Recommendation Review

### Recommendation from GAMSLIB_FEATURE_MATRIX.md

**Feature Selected:** Indexed Assignments  
**Alternative Considered:** Function Calls  
**Decision Rationale:** Higher ROI (2 models vs 1 model unlock)

From GAMSLIB_FEATURE_MATRIX.md (lines 341-373):

> **Recommended: Indexed Assignments**
>
> **Unlocks:** mathopt1.gms, trig.gms  
> **Unlock Rate:** +20% (2/10 → 4/10 models)  
> **Effort:** 6-8 hours  
> **Complexity:** Medium  
> **Risk:** Medium  
>
> **Rationale:**
> - ✅ **High ROI:** Unlocks 2 models (mathopt1 + trig) vs 1 model for other features
> - ✅ **Clear scope:** Both models have explicit "Indexed assignments are not supported yet" errors
> - ✅ **Medium complexity:** Grammar + semantic changes, but well-defined scope
> - ✅ **Foundation for future:** Indexed assignments are common GAMS pattern
> - ✅ **Meets Sprint 8 target:** Combined with option statements → 50% parse rate

### Validation of Recommendation

**Evidence from GAMSLib Analysis:**

1. **mathopt1.gms (line 45):**
   - Error: `ParserSemanticError: Indexed assignments are not supported yet [context: expression]`
   - Code: `report('x1','global') = 1;`
   - Pattern: 2D parameter indexed assignment

2. **trig.gms (line 32):**
   - Error: `ParserSemanticError: Unsupported expression type: bound_scalar`
   - Code: `xdiff = 2.66695657 - x1.l;`
   - Pattern: Variable attribute access in expression (related to indexed assignment handling)

**Confirmation:** Indexed assignments is the correct choice for Sprint 8's second feature.

---

## GAMS Syntax Survey

### Overview of GAMS Indexed Assignment Syntax

From official GAMS documentation (https://www.gams.com/latest/docs/UG_Parameters.html):

> "An indexed assignment uses controlling indices (or controlling sets), which are the index set(s) on the left hand side of the assignment."
>
> "The number of controlling indices on the left of the = sign should be at least as large as the number of indices on the right."

**Key Characteristics:**
- **Parallel Processing:** All tuples execute simultaneously (not sequentially)
- **Copy Before Assign:** Right-hand side is copied before assignment (prevents self-reference)
- **Domain Restrictions:** Supports explicit labels, subsets, conditionals, tuples

### Pattern 1: Simple Indexed Parameter Assignment (1D)

**GAMS Syntax:**
```gams
Parameter p(i) / i1 10, i2 20 /;
p('i1') = 15;  // Explicit label assignment
```

**Frequency in GAMSLib:** Low (most models use inline data initialization)

**Sprint 8 Priority:** Medium (foundation for 2D/3D assignments)

**Example from GAMSLib:**
- Not found in failing models (all use 2D patterns)

---

### Pattern 2: Multi-Dimensional Parameter Assignment (2D, 3D)

**GAMS Syntax:**
```gams
Parameter report(scenario, metric);
report('x1','global') = 1;           // 2D assignment
report('x2','solver') = x2.l;         // 2D with variable attribute on right
```

**Frequency in GAMSLib:** **High** (mathopt1.gms uses this pattern extensively)

**Sprint 8 Priority:** **Critical** (unlocks mathopt1.gms)

**Example from mathopt1.gms (lines 45-50):**
```gams
Parameter report 'solution summary report';
report('x1','global') = 1;
report('x2','global') = 1;
report('x1','solver') = x1.l;
report('x2','solver') = x2.l;
report('x1','diff')   = report('x1','global') - report('x1','solver');
report('x2','diff')   = report('x2','global') - report('x2','solver');
```

**Pattern Characteristics:**
- Left-hand side: `parameter_name(index1, index2, ...)`
- Right-hand side: Constant, expression, or variable attribute
- Indices: String literals (quoted identifiers)
- Complexity: Medium (requires index parsing + validation)

---

### Pattern 3: Variable Attribute Access in Assignments

**GAMS Syntax:**
```gams
Scalar xdiff;
xdiff = 2.66695657 - x1.l;  // .l = level attribute
```

**Variable Attributes:**
- `.l` - Level (solution value)
- `.lo` - Lower bound
- `.up` - Upper bound
- `.m` - Marginal (dual value)
- `.scale` - Scaling factor

**Frequency in GAMSLib:** **High** (trig.gms, mathopt1.gms both use `.l` attribute)

**Sprint 8 Priority:** **Critical** (unlocks trig.gms)

**Example from trig.gms (line 32):**
```gams
Scalar xdiff, fdiff;
xdiff =  2.66695657 - x1.l;  // Variable level attribute
fdiff = -3.76250149 - obj.l;
```

**Example from mathopt1.gms (line 47):**
```gams
report('x1','solver') = x1.l;  // Variable attribute in 2D indexed assignment
```

**Pattern Characteristics:**
- Variable attributes appear on **right-hand side** of assignments
- Attributes access solution values (post-solve)
- Complexity: Low (grammar already supports `ref_bound` rule for `.lo`, `.up`, `.fx`)
- Extension needed: Add `.l` and `.m` to BOUND_K token

---

### Pattern 4: Indexed Assignment with Expressions

**GAMS Syntax:**
```gams
report('x1','diff') = report('x1','global') - report('x1','solver');
```

**Frequency in GAMSLib:** High (mathopt1.gms uses this pattern)

**Sprint 8 Priority:** Critical (required for mathopt1.gms)

**Pattern Characteristics:**
- Right-hand side: Complex expression with indexed parameter references
- Requires: Indexed parameters in expressions (already supported in grammar via `ref_indexed`)
- Complexity: Low (expression evaluation already handles indexed references)

---

### GAMS Syntax Patterns Summary

| Pattern | GAMS Example | GAMSLib Usage | Sprint 8? | Complexity |
|---------|-------------|---------------|-----------|------------|
| 1. Simple 1D indexed assignment | `p('i1') = 15;` | Low | ✅ YES | Low |
| 2. Multi-dimensional (2D/3D) | `report('x1','global') = 1;` | **High** | ✅ YES | Medium |
| 3. Variable attribute access | `xdiff = x1.l;` | **High** | ✅ YES | Low |
| 4. Indexed expressions on RHS | `p('i') = q('i') + 10;` | High | ✅ YES | Low |

**Total Patterns:** 4 (all within Sprint 8 scope)

**Patterns Deferred:** None (all patterns needed for mathopt1/trig unlock)

---

## Grammar Design

### Current Grammar Analysis

From `src/gams/gams_grammar.lark` (lines 99-107):

```lark
assignment_stmt: lvalue ASSIGN expr SEMI                    -> assign

// lvalue supports: x.lo(i), x.up(i), x.fx(i), parameter(i), scalar
lvalue: ref_bound | ref_indexed | ID

ref_bound: ID "." BOUND_K "(" id_list ")"   -> bound_indexed
         | ID "." BOUND_K                      -> bound_scalar

BOUND_K: /(lo|up|fx|l)/i

ref_indexed.2: ID "(" id_list ")"             -> symbol_indexed
```

**Current Status:**
- ✅ Grammar **already supports** indexed assignments via `ref_indexed` in lvalue
- ✅ Grammar **already supports** variable attributes via `ref_bound` (`.lo`, `.up`, `.fx`, `.l`)
- ❌ Parser **raises error** for `symbol_indexed` in `src/ir/parser.py:876`

**Key Finding:** Grammar changes are **minimal** - only need to extend `.l` and `.m` attribute support, which is **already in grammar**!

---

### Required Grammar Changes

#### Change 1: Extend BOUND_K Token (ALREADY DONE)

**Current Grammar (line 107):**
```lark
BOUND_K: /(lo|up|fx|l)/i
```

**Status:** ✅ **Already includes `.l` attribute!**

**Needed Addition:** Add `.m` (marginal) attribute
```lark
BOUND_K: /(lo|up|fx|l|m)/i
```

**Effort:** 5 minutes (single line change)

**Rationale:** Enables variable marginal attribute access (e.g., `x.m` for dual values)

---

#### Change 2: Enable symbol_indexed in Expressions (ALREADY DONE)

**Current Grammar (lines 105-106):**
```lark
lvalue: ref_bound | ref_indexed | ID
ref_indexed.2: ID "(" id_list ")"             -> symbol_indexed
```

**Status:** ✅ **Grammar already supports indexed parameters in lvalue!**

**Example:** `report('x1','global')` parses as `ref_indexed` → `symbol_indexed`

**No grammar changes needed** - only parser semantic handling required.

---

### Grammar Design Summary

**Total Grammar Changes:** 1 line (add `.m` to BOUND_K)

**Estimated Effort:** 15 minutes

**Complexity:** **Very Low** (grammar already 95% supports indexed assignments)

**Hidden Complexity Found:** ❌ **None** - grammar design is straightforward

---

## Implementation Plan

### Phase 1: Grammar Extension (15 minutes)

**Task 1.1: Extend BOUND_K token for marginal attribute**
- File: `src/gams/gams_grammar.lark`
- Change: Line 107 - Add `.m` to BOUND_K regex
- Before: `BOUND_K: /(lo|up|fx|l)/i`
- After: `BOUND_K: /(lo|up|fx|l|m)/i`
- Effort: 5 minutes

**Task 1.2: Verify grammar parses test cases**
- Run: `pytest tests/unit/gams/test_parser.py -k "indexed"` (currently fails as expected)
- Verify: Grammar accepts `report('x1','global') = 1;`
- Verify: Grammar accepts `xdiff = x1.l;`
- Effort: 10 minutes

**Phase 1 Total:** 15 minutes

---

### Phase 2: Semantic Handler Implementation (4-5 hours)

**Task 2.1: Implement indexed parameter assignment handler**
- File: `src/ir/parser.py`
- Location: Line 876 (currently raises "Indexed assignments are not supported yet")
- Replace error with implementation
- Effort: 2 hours

**Implementation Pseudocode:**
```python
if target.data == "symbol_indexed":
    # Extract parameter name and indices
    param_name = _token_text(target.children[0])
    indices = _id_list(target.children[1]) if len(target.children) > 1 else ()
    
    # Validate parameter exists
    if param_name not in self.model.params:
        raise self._error(f"Parameter '{param_name}' not declared", target)
    
    param = self.model.params[param_name]
    
    # Validate index count matches domain
    if len(indices) != len(param.domain):
        raise self._error(
            f"Parameter '{param_name}' expects {len(param.domain)} indices, got {len(indices)}",
            target
        )
    
    # Store indexed value (value already extracted via _extract_constant)
    param.values[tuple(indices)] = value
    return
```

**Validation Requirements:**
1. Parameter must be declared
2. Index count must match parameter domain
3. Value must be numeric constant (for Sprint 8 scope)

**Effort Breakdown:**
- Core implementation: 1 hour
- Error handling: 30 minutes
- Edge case handling: 30 minutes

---

**Task 2.2: Extend variable attribute handling for `.l` and `.m`**
- File: `src/ir/parser.py`
- Location: `_apply_variable_bound` method (around line 820)
- Current: Handles `.lo`, `.up`, `.fx` assignments
- Extend: Handle `.l` (level) and `.m` (marginal) attributes
- Effort: 1 hour

**Implementation Pseudocode:**
```python
def _apply_variable_bound(self, var_name, bound_token, indices, value, tree):
    if var_name not in self.model.variables:
        raise self._error(f"Variable '{var_name}' not declared", tree)
    
    var = self.model.variables[var_name]
    bound_attr = _token_text(bound_token).lower()
    
    # Existing handling for .lo, .up, .fx
    if bound_attr == "lo":
        var.lo = value
    elif bound_attr == "up":
        var.up = value
    elif bound_attr == "fx":
        var.fx = value
    # NEW: Handle .l (level) and .m (marginal)
    elif bound_attr == "l":
        # Store level value (for initial point or post-solve validation)
        var.level = value
    elif bound_attr == "m":
        # Store marginal value (for post-solve validation)
        var.marginal = value
    else:
        raise self._error(f"Unknown variable attribute: .{bound_attr}", tree)
```

**Validation Requirements:**
1. Variable must be declared
2. Attribute must be valid (`.lo`, `.up`, `.fx`, `.l`, `.m`)
3. Value must be numeric constant

**Effort Breakdown:**
- Extend _apply_variable_bound: 30 minutes
- Add .level and .marginal fields to Variable IR node: 30 minutes

---

**Task 2.3: Enable variable attribute access in expressions**
- File: `src/ir/parser.py`
- Location: `_expr` method (handles `ref_bound` nodes in expressions)
- Current: Variable attributes used in assignments (left-hand side)
- Extend: Variable attributes used in expressions (right-hand side)
- Effort: 1.5 hours

**Implementation Pseudocode:**
```python
def _expr(self, node: Tree | Token, free_domain: tuple[str, ...]) -> Expr:
    # ... existing cases ...
    
    if isinstance(node, Tree) and node.data == "bound_scalar":
        # Handle: x1.l, x1.lo, x1.up, x1.m
        var_name = _token_text(node.children[0])
        bound_token = node.children[1]
        
        if var_name not in self.model.variables:
            raise self._error(f"Variable '{var_name}' not declared", node)
        
        var = self.model.variables[var_name]
        bound_attr = _token_text(bound_token).lower()
        
        # Return variable attribute as expression
        return VarAttr(var_name, bound_attr, domain=free_domain)
```

**New IR Node Required:**
```python
@dataclass
class VarAttr(Expr):
    """Variable attribute access: x.l, x.lo, x.up, x.m"""
    var_name: str
    attr: str  # "l", "lo", "up", "m"
```

**Validation Requirements:**
1. Variable must be declared
2. Attribute must be valid
3. No semantic validation needed (solver populates at runtime)

**Effort Breakdown:**
- Implement VarAttr IR node: 30 minutes
- Extend _expr method: 30 minutes
- Handle indexed variable attributes (`x.l(i)`): 30 minutes

---

**Task 2.4: Update ModelIR to store indexed parameter values**
- File: `src/ir/model.py`
- Location: `Parameter` dataclass
- Current: `values: dict[tuple, float]` (already supports indexed storage!)
- Change: ✅ **No changes needed** - existing structure supports indexed assignments
- Effort: 0 minutes (already implemented)

**Verification:**
- Current `Parameter.values` uses `dict[tuple, float]` for storage
- Example: `report('x1','global') = 1` → `param.values[('x1', 'global')] = 1.0`
- ✅ Existing data structure is compatible

---

**Phase 2 Total:** 4.5 hours

---

### Phase 3: Testing (1.5 hours)

**Task 3.1: Unit tests for indexed assignments**
- File: `tests/unit/gams/test_parser.py`
- Tests: 5 test cases (see Test Fixture Design section)
- Effort: 1 hour

**Task 3.2: Integration test with mathopt1.gms and trig.gms**
- File: `tests/integration/test_gamslib.py`
- Verify: mathopt1.gms parses successfully
- Verify: trig.gms parses successfully
- Verify: Parse rate increases to 40% (4/10 models)
- Effort: 30 minutes

**Phase 3 Total:** 1.5 hours

---

### Phase 4: Documentation (30 minutes)

**Task 4.1: Update CHANGELOG.md**
- Document: Indexed assignments feature implementation
- Document: Models unlocked (mathopt1, trig)
- Effort: 15 minutes

**Task 4.2: Update parser documentation**
- File: `docs/parser/FEATURES.md` (if exists) or README
- Document: Indexed assignment syntax support
- Effort: 15 minutes

**Phase 4 Total:** 30 minutes

---

### Implementation Plan Summary

| Phase | Task | Effort | Complexity |
|-------|------|--------|------------|
| 1. Grammar Extension | Extend BOUND_K token | 15 min | Very Low |
| 2. Semantic Handlers | Indexed parameter assignments | 2h | Medium |
| 2. Semantic Handlers | Variable attribute handling | 1h | Low |
| 2. Semantic Handlers | Attribute access in expressions | 1.5h | Medium |
| 2. Semantic Handlers | ModelIR updates | 0 min | N/A |
| 3. Testing | Unit tests (5 fixtures) | 1h | Low |
| 3. Testing | Integration tests | 30 min | Low |
| 4. Documentation | CHANGELOG + docs | 30 min | Low |
| **TOTAL** | | **6.5 hours** | **Medium** |

**Effort Estimate Validation:**
- Original estimate: 6-8 hours
- Detailed breakdown: 6.5 hours
- ✅ **Estimate confirmed** (within range)

**Risk Buffer:**
- +1.5 hours for unexpected issues (edge cases, debugging)
- Total with buffer: **8 hours** (upper bound of estimate)

---

## Test Fixture Design

### Fixture 1: Simple 1D Indexed Assignment

**File:** `tests/fixtures/indexed_assign/01_simple_1d.gms`

**GAMS Code:**
```gams
Set i / i1, i2, i3 /;
Parameter p(i);
p('i1') = 10;
p('i2') = 20;
p('i3') = 30;
```

**Test Coverage:**
- Basic 1D indexed assignment
- String literal indices
- Multiple sequential assignments

**Expected Result:** ✅ PASS - Parse successfully, store values in `param.values`

**Validation:**
- `param.values[('i1',)] == 10.0`
- `param.values[('i2',)] == 20.0`
- `param.values[('i3',)] == 30.0`

---

### Fixture 2: Multi-Dimensional Indexed Assignment (2D)

**File:** `tests/fixtures/indexed_assign/02_multi_dim_2d.gms`

**GAMS Code:**
```gams
Set scenario / global, solver /;
Set metric / x1, x2 /;
Parameter report(scenario, metric);
report('global','x1') = 1.0;
report('global','x2') = 1.0;
report('solver','x1') = 0.95;
report('solver','x2') = 1.02;
```

**Test Coverage:**
- 2D indexed assignments
- Multiple index dimensions
- Realistic use case from mathopt1.gms

**Expected Result:** ✅ PASS

**Validation:**
- `param.values[('global', 'x1')] == 1.0`
- `param.values[('solver', 'x2')] == 1.02`

---

### Fixture 3: Variable Attribute Access in Assignments

**File:** `tests/fixtures/indexed_assign/03_variable_attributes.gms`

**GAMS Code:**
```gams
Variable x1, x2;
Scalar diff1, diff2;

x1.l = 2.5;
x2.l = 3.7;

diff1 = 10.0 - x1.l;
diff2 = 5.0 - x2.l;
```

**Test Coverage:**
- Variable `.l` attribute assignment (left-hand side)
- Variable `.l` attribute access in expressions (right-hand side)
- Realistic use case from trig.gms

**Expected Result:** ✅ PASS

**Validation:**
- `var.level == 2.5` for x1
- `diff1` expression includes `VarAttr('x1', 'l')`

---

### Fixture 4: Indexed Assignment with Expressions

**File:** `tests/fixtures/indexed_assign/04_indexed_expressions.gms`

**GAMS Code:**
```gams
Set metric / global, solver, diff /;
Parameter data(metric);
data('global') = 1.0;
data('solver') = 0.95;
data('diff') = data('global') - data('solver');
```

**Test Coverage:**
- Indexed parameters in expressions (right-hand side)
- Expression evaluation with indexed references
- Realistic use case from mathopt1.gms

**Expected Result:** ✅ PASS

**Validation:**
- `param.values[('diff',)]` contains expression: `Sub(ParameterRef('data', ('global',)), ParameterRef('data', ('solver',)))`

---

### Fixture 5: Error Handling - Index Count Mismatch

**File:** `tests/fixtures/indexed_assign/05_error_index_mismatch.gms`

**GAMS Code:**
```gams
Set i / i1, i2 /;
Set j / j1, j2 /;
Parameter p(i, j);
p('i1') = 10;  // ERROR: Parameter expects 2 indices, got 1
```

**Test Coverage:**
- Error handling for incorrect index count
- Validation logic

**Expected Result:** ❌ FAIL - ParserSemanticError

**Expected Error Message:**
```
Parameter 'p' expects 2 indices, got 1
```

---

### Test Fixture Summary

| Fixture | Description | Coverage | Expected |
|---------|-------------|----------|----------|
| 1. Simple 1D | Basic indexed assignment | 1D indexing | ✅ PASS |
| 2. Multi-dim 2D | 2D indexed assignment | Multi-dimensional | ✅ PASS |
| 3. Variable attributes | `.l` attribute access | Var attributes | ✅ PASS |
| 4. Indexed expressions | Indexed params in RHS | Expression eval | ✅ PASS |
| 5. Error handling | Index count mismatch | Validation | ❌ FAIL |

**Total Fixtures:** 5

**Coverage:**
- ✅ All 4 GAMS syntax patterns covered
- ✅ Error handling covered
- ✅ Realistic GAMSLib use cases (mathopt1, trig patterns)

---

## Risk Assessment

### Risk 1: Variable Attribute Semantics

**Description:** Variable attributes (`.l`, `.m`) are populated by solver at runtime, but parser must handle them in pre-solve assignments.

**Likelihood:** Medium

**Impact:** Low (does not block parsing, only affects semantic accuracy)

**Mitigation:**
- Store `.l` and `.m` values in Variable IR node as "initial level" and "initial marginal"
- Document that these are pre-solve values (initial guesses or validation data)
- Post-solve values would be populated by solver (out of scope for Sprint 8)

**Residual Risk:** Low

---

### Risk 2: Expression Evaluation with Indexed Parameters

**Description:** Right-hand side expressions may reference indexed parameters (e.g., `data('diff') = data('global') - data('solver')`), requiring indexed parameter access in expression context.

**Likelihood:** High (mathopt1.gms uses this pattern)

**Impact:** Medium (requires additional expression handling)

**Mitigation:**
- Grammar already supports `ref_indexed` in expressions (via atom rule)
- Parser `_expr` method needs to handle `symbol_indexed` nodes
- Create `ParameterRef` IR node with index tuple
- Estimated effort: Already included in Phase 2 (1.5 hours for expression handling)

**Residual Risk:** Low

---

### Risk 3: Index Validation Complexity

**Description:** Validating that indices match parameter domain may be complex if domains are dynamic or conditional.

**Likelihood:** Low (GAMSLib models use simple static domains)

**Impact:** Low (can defer complex validation to Sprint 8b)

**Mitigation:**
- Sprint 8 scope: Validate index **count** only (simple check)
- Defer index **domain membership** validation to Sprint 8b (e.g., verify 'i1' ∈ set i)
- Document limitation in CHANGELOG

**Residual Risk:** Very Low

---

### Risk 4: Grammar Ambiguity Between Function Calls and Indexed References

**Description:** Grammar uses `ref_indexed` for both function calls (e.g., `sum(i, expr)`) and indexed parameters (e.g., `p(i)`). Potential ambiguity?

**Likelihood:** Low

**Impact:** Low

**Mitigation:**
- Grammar already disambiguates via context:
  - Function calls: `func_call.3: FUNCNAME "(" arg_list? ")"` (higher priority)
  - Indexed references: `ref_indexed.2: ID "(" id_list ")"` (lower priority)
- FUNCNAME is explicit token list, ID is fallback
- ✅ No ambiguity found in existing grammar

**Residual Risk:** Very Low

---

### Risk Assessment Summary

| Risk | Likelihood | Impact | Mitigation | Residual |
|------|------------|--------|------------|----------|
| 1. Variable attribute semantics | Medium | Low | Store as initial values | Low |
| 2. Indexed params in expressions | High | Medium | ParameterRef IR node | Low |
| 3. Index validation complexity | Low | Low | Defer domain checks | Very Low |
| 4. Grammar ambiguity | Low | Low | Priority rules | Very Low |

**Overall Risk:** **Medium** (acceptable for Sprint 8 scope)

**Risk Summary:**
- ✅ No hidden complexity found in GAMS syntax
- ✅ Grammar changes are minimal (1 line)
- ✅ Implementation is well-scoped (6.5 hours)
- ⚠️ Expression handling requires care (1.5 hours allocated)

**Recommendation:** Proceed with Sprint 8 implementation.

---

## Models Unlocked

### Model 1: mathopt1.gms

**Primary Blocker:** Indexed assignments  
**Error Location:** Line 45  
**Error Message:** `ParserSemanticError: Indexed assignments are not supported yet [context: expression]`

**Blocking Code:**
```gams
Parameter report 'solution summary report';
report('x1','global') = 1;
report('x2','global') = 1;
report('x1','solver') = x1.l;
report('x2','solver') = x2.l;
report('x1','diff')   = report('x1','global') - report('x1','solver');
report('x2','diff')   = report('x2','global') - report('x2','solver');
```

**Patterns Used:**
- ✅ Pattern 2: Multi-dimensional (2D) indexed assignment
- ✅ Pattern 3: Variable attribute access (`.l`)
- ✅ Pattern 4: Indexed expressions on RHS

**Unlock Confidence:** **Very High (95%)**

**Rationale:**
- All blocking patterns are within Sprint 8 scope
- No secondary errors identified in manual review (from GAMSLIB_FEATURE_MATRIX.md)
- Error message explicitly states feature is "not supported yet" (implementation in progress)

**Parse Rate Impact:** +10% (3/10 → 4/10 models)

---

### Model 2: trig.gms

**Primary Blocker:** Variable attribute access in expressions  
**Error Location:** Line 32  
**Error Message:** `ParserSemanticError: Unsupported expression type: bound_scalar`

**Blocking Code:**
```gams
Scalar xdiff, fdiff;
xdiff =  2.66695657 - x1.l;
fdiff = -3.76250149 - obj.l;
```

**Patterns Used:**
- ✅ Pattern 3: Variable attribute access (`.l`)

**Unlock Confidence:** **High (85%)**

**Rationale:**
- Primary blocker is Pattern 3 (variable attributes in expressions)
- Pattern 3 is within Sprint 8 scope (1.5 hours allocated)
- Possible secondary issue: `bound_scalar` error suggests expression handling needs extension
- Risk: May need additional debugging beyond 1.5 hour estimate

**Parse Rate Impact:** +10% (4/10 → 5/10 models)

**Note:** Conservative estimate assumes trig.gms unlock may require Sprint 8b debugging if unexpected issues arise.

---

### Combined Sprint 8 Impact

**Baseline:** 20% parse rate (2/10 models: mhw4d, rbrock)

**After Option Statements (Task 6):**
- Unlocks: mhw4dx.gms
- Parse rate: 30% (3/10 models)

**After Indexed Assignments (Task 7):**
- Unlocks: mathopt1.gms (95% confidence) + trig.gms (85% confidence)
- Optimistic: 50% parse rate (5/10 models)
- Conservative: 40% parse rate (4/10 models, if trig.gms has secondary issues)

**Sprint 8 Target Comparison:**
- PROJECT_PLAN.md Target: 25-30% parse rate
- Projected: **30-50% parse rate**
- ✅ **EXCEEDS TARGET** in both scenarios

---

## Appendix: Cross-References

### Task 2 (GAMSLIB_FEATURE_MATRIX.md)

- Lines 341-373: Indexed Assignments recommendation
- Lines 176-207: mathopt1.gms analysis (confirms indexed assignments as only blocker)
- Lines 466-489: trig.gms analysis (confirms variable attributes as only blocker)

### KNOWN_UNKNOWNS.md

**Unknown 3.1:** Is indexed assignments OR function calls the right choice?
- ✅ VERIFIED by this document: Indexed assignments confirmed

**Unknown 3.2:** Are there hidden complexities in indexed assignments?
- ✅ VERIFIED by this document: No hidden complexity found

**Unknown 3.3:** What test fixtures are needed for indexed assignments?
- ✅ VERIFIED by this document: 5 fixtures identified

### PROJECT_PLAN.md

- Lines 84-148: Sprint 8 goals (25-30% parse rate target)
- Lines 105-110: Indexed assignments listed as "one additional feature" candidate

---

**Document Status:** ✅ Complete  
**Analysis Date:** 2025-11-17  
**Next Steps:**
1. Verify unknowns 3.1, 3.2, 3.3 in KNOWN_UNKNOWNS.md
2. Update PREP_PLAN.md Task 7 to COMPLETE
3. Update CHANGELOG.md with findings
4. Execute Sprint 8 implementation (6-8 hours)
