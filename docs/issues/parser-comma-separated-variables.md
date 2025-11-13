# Issue #195: Parser does not support comma-separated variable declarations

**Issue URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/195  
**Issue Number:** #195  
**Status:** Open  
**Priority:** Medium  
**Labels:** bug, enhancement  
**Created:** 2025-11-13  
**Milestone:** Sprint 7 (proposed)

## Problem Description

The GAMS parser currently does not support comma-separated variable declarations in the standard GAMS syntax `Variables x, y, z;`. The parser only accepts one variable per declaration statement or indexed variables with parentheses.

This limitation affects many GAMS models, including 10 out of 13 convexity test fixtures, which use the common comma-separated syntax for declaring multiple variables on a single line.

## Error Observed

When attempting to parse a GAMS file with comma-separated variables, the parser fails with:

```
lark.exceptions.UnexpectedCharacters: No terminal matches ',' in the current parser context, at line 7 col 12

Variables x, y, obj;
           ^
Expected one of:
	* INTEGER_K
	* SEMI
	* BINARY_K
	* ID
	* POSITIVE_K
	* LPAR
	* NEGATIVE_K
```

## Impact

**Severity:** Medium  
**Scope:** Parser/Frontend

### Current Impact
- **Test Coverage:** 10 out of 13 convexity test fixtures cannot be parsed
  - Blocked fixtures use `Variables x, y, obj;` syntax
  - Only 3 fixtures work (use different variable declaration patterns)
- **User Experience:** Users must manually rewrite variable declarations to use one per line
- **GAMS Compatibility:** Standard GAMS syntax not supported, reducing tool usability
- **Real-world Models:** Many production GAMS models use comma-separated declarations

### Affected Files

**Test Fixtures (10 blocked):**
1. `tests/fixtures/convexity/convex_qp.gms`
2. `tests/fixtures/convexity/convex_exponential.gms`
3. `tests/fixtures/convexity/convex_log_barrier.gms`
4. `tests/fixtures/convexity/convex_inequality.gms`
5. `tests/fixtures/convexity/nonconvex_circle.gms`
6. `tests/fixtures/convexity/nonconvex_bilinear.gms`
7. `tests/fixtures/convexity/nonconvex_quotient.gms`
8. `tests/fixtures/convexity/nonconvex_odd_power.gms`
9. `tests/fixtures/convexity/mixed_convex_nonconvex.gms`
10. `tests/fixtures/convexity/convex_with_trig_ineq.gms`

## Example GAMS Files Affected

### Current Syntax (Not Supported)
```gams
Variables x, y, z, obj;
Positive Variables a, b, c;
Equations eq1, eq2, eq3;
```

### Required Workaround (Currently)
```gams
Variables x;
Variables y;
Variables z;
Variables obj;

Positive Variables a;
Positive Variables b;
Positive Variables c;

Equations eq1;
Equations eq2;
Equations eq3;
```

### Example from Blocked Fixture
```gams
$title Convex Quadratic Program - Convex

Variables x, y, obj;  # <-- Parser fails here
Equations objdef, linear_constr;

objdef.. obj =e= sqr(x) + sqr(y);
linear_constr.. x + 2*y =l= 5;

Model m /all/;
Solve m using nlp minimizing obj;
```

## GAMS Language Specification

According to GAMS documentation:
- **Syntax:** `Variables id1, id2, ..., idn;`
- **Purpose:** Declare multiple variables in a single statement
- **Scope:** Standard GAMS syntax supported in all GAMS versions
- **Common Usage:** Very common in GAMS models for brevity
- **Also Applies To:** 
  - `Equations eq1, eq2, eq3;`
  - `Parameters p1, p2, p3;`
  - `Sets s1, s2, s3;`
  - All variable kinds: `Positive Variables`, `Binary Variables`, etc.

## Proposed Solution

### Option 1: Grammar Extension (Recommended)

Update the Lark grammar to support comma-separated identifiers in declarations:

**Current Grammar Pattern:**
```lark
variable_decl: "Variables" ID ("(" id_list ")")? ";"
```

**Proposed Grammar Pattern:**
```lark
variable_decl: "Variables" id_list ";"
id_list: ID ("," ID)*
```

**Changes Required:**
1. Update `src/ir/gams.lark` grammar file
2. Update parser transformer to handle comma-separated IDs
3. Expand each comma-separated declaration into individual variable definitions in ModelIR

**Implementation Approach:**
```python
def transform_variable_decl(self, items):
    """Transform comma-separated variable declaration.
    
    Input:  Variables x, y, z;
    Output: [VariableDef('x'), VariableDef('y'), VariableDef('z')]
    """
    var_kind = items[0]  # 'Variables', 'Positive Variables', etc.
    id_list = items[1]   # ['x', 'y', 'z']
    
    # Create individual VariableDef for each identifier
    return [VariableDef(name=id, kind=var_kind) for id in id_list]
```

**Pros:**
- Proper language support
- Matches GAMS specification exactly
- Clean implementation
- No preprocessing hacks

**Cons:**
- Requires grammar changes (moderate effort)
- Need to test all declaration types (Variables, Equations, Parameters, Sets)

### Option 2: Preprocessor Transformation

Add preprocessing step to expand comma-separated declarations:

```python
def expand_comma_declarations(source: str) -> str:
    """Expand comma-separated declarations to one per line."""
    # Variables x, y, z; → Variables x; Variables y; Variables z;
    # Similar to how we handle $title directive
```

**Pros:**
- No grammar changes needed
- Preserves line numbers (with careful implementation)
- Quick to implement

**Cons:**
- Hacky solution
- Harder to preserve source locations for error messages
- Duplicates declaration keywords unnecessarily

## Recommended Approach

**Option 1 (Grammar Extension)** is recommended because:
1. **Proper Solution:** Matches GAMS language specification
2. **Clean Architecture:** No preprocessing hacks
3. **Better Errors:** Can provide better error messages with correct source locations
4. **Extensible:** Easy to add support for other comma-separated constructs
5. **Maintainable:** Grammar-based approach is clearer and easier to maintain

## Implementation Checklist

- [ ] Update grammar in `src/ir/gams.lark`
  - [ ] Add comma-separated support to `variable_decl`
  - [ ] Add comma-separated support to `equation_decl`
  - [ ] Add comma-separated support to `parameter_decl`
  - [ ] Add comma-separated support to `set_decl`
- [ ] Update parser transformer in `src/ir/parser.py`
  - [ ] Handle comma-separated IDs in `_visit_variable_decl()`
  - [ ] Handle comma-separated IDs in `_visit_equation_decl()`
  - [ ] Handle comma-separated IDs in other declaration types
- [ ] Add unit tests
  - [ ] Test comma-separated variables
  - [ ] Test comma-separated equations
  - [ ] Test comma-separated with variable kinds (Positive, Binary, etc.)
  - [ ] Test mixed single and comma-separated declarations
  - [ ] Test edge cases (single variable, trailing comma, etc.)
- [ ] Test with all 13 convexity fixtures
- [ ] Update documentation

## Test Cases

```python
def test_comma_separated_variables():
    source = """
    Variables x, y, z;
    Equations eq1, eq2;
    """
    model_ir = parse_model_text(source)
    assert 'x' in model_ir.variables
    assert 'y' in model_ir.variables
    assert 'z' in model_ir.variables
    assert 'eq1' in model_ir.equations
    assert 'eq2' in model_ir.equations

def test_comma_separated_with_kind():
    source = "Positive Variables x, y, z;"
    model_ir = parse_model_text(source)
    assert all(model_ir.variables[v].kind == VarKind.POSITIVE 
               for v in ['x', 'y', 'z'])

def test_mixed_declarations():
    source = """
    Variables x;
    Variables y, z;
    Variables w;
    """
    model_ir = parse_model_text(source)
    assert len(model_ir.variables) == 4

def test_single_variable_no_comma():
    source = "Variables x;"
    model_ir = parse_model_text(source)
    assert 'x' in model_ir.variables
```

## Acceptance Criteria

1. Parser successfully handles comma-separated variable declarations
2. Parser successfully handles comma-separated equation declarations
3. Parser successfully handles comma-separated parameter declarations
4. Parser successfully handles comma-separated set declarations
5. All 13 convexity test fixtures parse without errors
6. Variable kinds (Positive, Binary, etc.) work with comma-separated syntax
7. Line numbers and error reporting remain accurate
8. Zero regressions in existing tests
9. Documentation updated with supported syntax

## Related Issues

- **Issue #194:** Parser `$title` directive support (✅ Resolved in f21396e)
  - Fixed in Sprint 6 Day 3 ahead of schedule
- **Sprint 6 Day 3:** Only 3/13 convexity fixtures testable due to this issue
- **Future:** GAMSLib integration will require comma-separated support for most models

## Priority Justification

**Medium Priority** because:
- **Blocking Test Coverage:** Limits convexity heuristic testing to 3/13 fixtures
- **Common Syntax:** Very common in real GAMS models (high user impact)
- **Workaround Exists:** Users can manually rewrite declarations (annoying but possible)
- **Not Urgent:** Core functionality works with workaround

**Should Address In:**
- Sprint 7 (next sprint)
- Before GAMSLib benchmark work (many models use this syntax)
- As part of parser completeness improvements

## Estimated Effort

**4-6 hours total:**
- 2-3 hours: Update grammar and parser transformer
- 1-2 hours: Add comprehensive tests (variables, equations, parameters, sets)
- 1 hour: Test with all 13 convexity fixtures and verify
- 30 min: Update documentation

## Notes

- Discovered during Sprint 6 Day 3 when implementing convexity heuristics
- After fixing Issue #194 ($title support), this is now the primary blocker
- Grammar-based solution is cleaner than preprocessing approach
- Should handle all declaration types uniformly (not just variables)
- Consider adding support for inline comments: `Variables x, y, z; * three vars`

## Discovery Context

While fixing Issue #194 ($title directive support) in commit f21396e, testing revealed this separate parser limitation. After successfully implementing directive stripping:

**Test Results:**
```
Testing 16 convexity fixtures...

✅ convex_lp.gms: Parsed successfully
✅ convex_with_nonlinear_ineq.gms: Parsed successfully
✅ nonconvex_trig.gms: Parsed successfully
❌ convex_qp.gms: UnexpectedCharacters at 'Variables x, y, obj;'
❌ [10 more fixtures with same error]

Results: 3/16 passed, 13 failed
```

All 13 failures are due to comma-separated variable declarations, not $title directives.
