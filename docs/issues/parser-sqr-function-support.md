# Issue: Parser does not support GAMS sqr() function

**Issue URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/196  
**Issue Number:** #196  
**Status:** Open  
**Priority:** Medium  
**Labels:** bug, parser, enhancement  
**Created:** 2025-11-13  
**Milestone:** Sprint 7 (proposed)

## Problem Description

The GAMS parser currently does not recognize the `sqr()` function, which is a standard GAMS intrinsic function for computing the square of an expression. This prevents parsing of many GAMS models that use `sqr(x)` instead of `x**2`.

The parser treats `sqr` as an undefined symbol/parameter, causing semantic errors during parsing even though it's valid GAMS syntax.

## Error Observed

When attempting to parse a GAMS file using `sqr()`, the parser fails with:

```
ParserSemanticError: Undefined symbol 'sqr' with indices ('x',) referenced [context: equation 'objdef']
```

## Impact

**Severity:** Medium  
**Scope:** Parser/Function Support

### Current Impact
- **Test Coverage:** 6 out of 16 convexity test fixtures cannot be parsed
  - Blocked fixtures: `convex_qp.gms`, `convex_inequality.gms`, `mixed_convex_nonconvex.gms`, `nearly_affine.gms`, `nonconvex_circle.gms`, `nonconvex_trig_eq.gms`
- **User Experience:** Users must manually rewrite `sqr(x)` as `x**2` or `power(x, 2)`
- **GAMS Compatibility:** Standard GAMS intrinsic function not supported
- **Real-world Models:** Many GAMS models use `sqr()` for readability and performance

### After Fixing Issues #194 and #195
- Total fixtures: 16
- Successfully parsing: 9 (56.25%)
- Blocked by `sqr()`: 6 (37.5%)
- Blocked by other issues: 1 (6.25%)

## Example GAMS Files Affected

### Current Syntax (Not Supported)
```gams
Variables x, y, obj;
Equations objdef, constraint;

objdef.. obj =e= sqr(x) + sqr(y);
constraint.. sqr(x) + sqr(y) =l= 25;

Model m /all/;
Solve m using nlp minimizing obj;
```

### Required Workaround (Currently)
```gams
Variables x, y, obj;
Equations objdef, constraint;

objdef.. obj =e= x**2 + y**2;
constraint.. x**2 + y**2 =l= 25;

Model m /all/;
Solve m using nlp minimizing obj;
```

### Example from Blocked Fixture (convex_qp.gms)
```gams
$title Convex Quadratic Program - Convex

Variables x, y, obj;
Equations objdef, linear_constr;

objdef.. obj =e= sqr(x) + sqr(y);  # <-- Parser fails here
linear_constr.. x + 2*y =l= 5;

x.lo = -10; x.up = 10;
y.lo = -10; y.up = 10;

Model m /all/;
Solve m using nlp minimizing obj;
```

## GAMS Function Specification

According to GAMS documentation:
- **Function:** `sqr(x)`
- **Definition:** Returns x² (x squared)
- **Equivalent:** `x**2` or `power(x, 2)`
- **Domain:** All real numbers
- **Purpose:** More readable than `x**2`, potentially optimized by GAMS
- **Common Usage:** Very common in GAMS models for quadratic terms

**Related Functions:**
- `sqrt(x)` - Square root (already supported)
- `power(x, n)` - General power function (already supported)
- `sqr(x)` - Square (NOT supported)

## Proposed Solution

### Option 1: Add as Built-in Function (Recommended)

Add `sqr` to the list of recognized built-in functions in the parser:

**Changes Required:**
1. Add `sqr` to `_FUNCTION_NAMES` set in `src/ir/parser.py`
2. Add transformation rule in expression builder to convert `sqr(x)` → `Binary("**", x, Const(2))`
3. Update automatic differentiation to handle `sqr` efficiently

**Implementation:**
```python
# In src/ir/parser.py
_FUNCTION_NAMES = {"abs", "exp", "log", "sqrt", "sin", "cos", "tan", "sqr"}

# In expression transformation
def _transform_sqr(self, args):
    """Transform sqr(x) to x**2 for internal representation."""
    if len(args) != 1:
        raise self._error("sqr() requires exactly 1 argument")
    return Binary("**", args[0], Const(2))

# In AD rules (src/ad/derivative_rules.py)
def differentiate_sqr(expr: Call, wrt_var: str) -> Expr:
    """d/dx[sqr(x)] = 2*x"""
    arg = expr.args[0]
    d_arg = differentiate_expr(arg, wrt_var)
    return Binary("*", Binary("*", Const(2), arg), d_arg)
```

**Pros:**
- Clean implementation
- Efficient differentiation (can optimize `2*x` vs general power rule)
- Matches GAMS semantics exactly
- Easy to add other GAMS functions (e.g., `sign`, `mod`, etc.)

**Cons:**
- Need to add to multiple places (parser, AD, possibly simplifier)

### Option 2: Preprocessing Transformation

Convert `sqr(x)` to `x**2` during preprocessing:

```python
def expand_sqr_function(source: str) -> str:
    """Replace sqr(expr) with (expr)**2 before parsing."""
    # Use regex to find and replace sqr() calls
    import re
    pattern = r'sqr\(([^)]+)\)'
    return re.sub(pattern, r'(\1)**2', source)
```

**Pros:**
- Simple implementation
- No changes to grammar or AD system
- Works immediately

**Cons:**
- Loses `sqr` in source representation
- Complex nested expressions hard to handle with regex
- Doesn't preserve original intent
- Can't provide optimized differentiation

### Option 3: Add to Grammar as Special Syntax

Extend grammar to recognize `sqr` as a special case:

```lark
atom: sqr_expr
    | power_expr
    | ...

sqr_expr: "sqr" "(" expr ")"
```

**Pros:**
- Most explicit
- Could provide special handling

**Cons:**
- Grammar bloat
- Still need transformation and AD rules
- Overly complex for a simple function

## Recommended Approach

**Option 1 (Built-in Function)** is recommended because:
1. **Clean Architecture:** Fits existing function handling pattern
2. **Extensible:** Easy to add more GAMS functions later
3. **Optimizable:** Can provide efficient differentiation rules
4. **Maintainable:** All function logic in one place
5. **GAMS Compatible:** Matches GAMS's treatment of `sqr` as intrinsic

## Implementation Checklist

- [ ] Add `sqr` to `_FUNCTION_NAMES` in `src/ir/parser.py`
- [ ] Add `sqr` handling in expression builder
- [ ] Add differentiation rule for `sqr` in `src/ad/derivative_rules.py`
- [ ] Add unit tests for `sqr()` parsing
- [ ] Add unit tests for `sqr()` differentiation
- [ ] Test with all 6 blocked convexity fixtures
- [ ] Consider adding other common GAMS functions:
  - [ ] `sign(x)` - Sign function
  - [ ] `mod(x, y)` - Modulo
  - [ ] `div(x, y)` - Integer division
  - [ ] `max(x, y)` - Already supported
  - [ ] `min(x, y)` - Already supported
- [ ] Update documentation with supported functions list

## Test Cases

```python
def test_sqr_function_basic():
    source = """
    Variables x, obj;
    Equations eq;
    eq.. obj =e= sqr(x);
    Model m /all/;
    Solve m using nlp minimizing obj;
    """
    model_ir = parse_model_text(source)
    # Should parse successfully
    assert "eq" in model_ir.equations

def test_sqr_function_differentiation():
    from src.ad.ad_core import differentiate
    expr = Call("sqr", [VarRef("x")])
    derivative = differentiate(expr, "x")
    # d/dx[sqr(x)] = 2*x
    assert isinstance(derivative, Binary)
    assert derivative.op == "*"

def test_sqr_with_complex_argument():
    source = """
    Variables x, y;
    Equations eq;
    eq.. sqr(x + y) =e= 4;
    """
    model_ir = parse_model_text(source)
    assert "eq" in model_ir.equations

def test_nested_sqr():
    source = """
    Variables x;
    Equations eq;
    eq.. sqr(sqr(x)) =e= 16;
    """
    model_ir = parse_model_text(source)
    # sqr(sqr(x)) = (x²)² = x⁴
    assert "eq" in model_ir.equations
```

## Acceptance Criteria

1. Parser successfully handles `sqr()` function calls
2. `sqr(x)` correctly transforms to x² in internal representation
3. Differentiation of `sqr(x)` produces correct result: 2*x * dx
4. All 6 blocked convexity fixtures parse successfully
5. Zero regressions in existing tests
6. Documentation updated with supported functions

## Related Issues

- **Issue #194:** Parser `$title` directive support (✅ Resolved in f21396e)
- **Issue #195:** Comma-separated variable declarations (✅ Resolved in bc50094)
- **After #194 + #195:** 9/16 fixtures parse (56.25%)
- **After this fix:** Expected 15/16 fixtures parse (93.75%)
- **Remaining blocker:** Odd power syntax (1 fixture)

## Priority Justification

**Medium Priority** because:
- **Blocking Test Coverage:** 6/16 convexity fixtures blocked (37.5%)
- **Common Function:** `sqr()` is very common in GAMS models
- **Workaround Exists:** Users can rewrite as `x**2` (annoying but possible)
- **High Impact Fix:** Would enable 6 additional fixtures to parse

**Should Address In:**
- Sprint 7 (along with odd power syntax fix)
- Before GAMSLib benchmark work
- As part of GAMS function completeness

## Estimated Effort

**2-3 hours total:**
- 1 hour: Add `sqr` to parser and function handling
- 30 min: Add differentiation rule for `sqr`
- 1 hour: Add comprehensive tests (parsing, differentiation, fixtures)
- 30 min: Test with 6 blocked fixtures and verify

## Notes

- Discovered during Sprint 6 Day 3 after fixing Issues #194 and #195
- Currently the primary blocker for 6 convexity fixtures
- Clean implementation path using existing function infrastructure
- Consider adding batch of common GAMS functions at once:
  - `sqr(x)`, `sign(x)`, `mod(x,y)`, `div(x,y)`, etc.
- May want to create comprehensive GAMS function support in single PR

## Discovery Context

After successfully fixing Issue #194 ($title) and Issue #195 (comma-separated variables):

**Test Results:**
```
Testing 16 convexity fixtures...

✅ convex_exponential.gms: Parsed successfully
❌ convex_inequality.gms: Undefined symbol 'sqr' with indices ('x',)
✅ convex_log_barrier.gms: Parsed successfully
✅ convex_lp.gms: Parsed successfully
❌ convex_qp.gms: Undefined symbol 'sqr' with indices ('x',)
✅ convex_with_nonlinear_ineq.gms: Parsed successfully
✅ convex_with_trig_ineq.gms: Parsed successfully
✅ linear_program.gms: Parsed successfully
❌ mixed_convex_nonconvex.gms: Undefined symbol 'sqr' with indices ('x',)
❌ nearly_affine.gms: Undefined symbol 'sqr' with indices ('x',)
✅ nonconvex_bilinear.gms: Parsed successfully
❌ nonconvex_circle.gms: Undefined symbol 'sqr' with indices ('x',)
❌ nonconvex_odd_power.gms: UnexpectedCharacters [different issue]
✅ nonconvex_quotient.gms: Parsed successfully
✅ nonconvex_trig.gms: Parsed successfully
❌ nonconvex_trig_eq.gms: Undefined symbol 'sqr' with indices ('x',)

Results: 9/16 passed, 7 failed (6 due to sqr, 1 due to odd power syntax)
```
