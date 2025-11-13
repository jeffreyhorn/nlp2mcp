# Issue: Parser does not support odd power syntax (x³, x**3)

**Issue URL:** https://github.com/jeffreyhorn/nlp2mcp/issues/197  
**Issue Number:** #197  
**Status:** ✅ Closed - Completed  
**Resolved:** 2025-11-13  
**Resolution:** Fixed in commit 5af7556  
**Priority:** Low  
**Labels:** bug, parser, enhancement  
**Created:** 2025-11-13  
**Milestone:** Sprint 6 Day 3 (completed same day as Issues #194, #195, #196)

## Problem Description

The GAMS parser currently does not support certain odd power expressions, specifically syntax like `x**3` for cubic terms. This prevents parsing of GAMS models that use odd polynomial powers.

The parser fails with an unexpected character error when encountering the exponent in odd power expressions.

## Error Observed

When attempting to parse a GAMS file with odd powers, the parser fails with:

```
UnexpectedCharacters: No terminal matches '3' in the current parser context, at line 11 col 31

objdef.. obj =e= x**3 + y**3;
                              ^
```

## Impact

**Severity:** Low  
**Scope:** Parser/Expression Handling

### Current Impact
- **Test Coverage:** 1 out of 16 convexity test fixtures cannot be parsed
  - Blocked fixture: `nonconvex_odd_power.gms`
- **User Experience:** Users cannot use odd power syntax for non-convex terms
- **GAMS Compatibility:** Standard GAMS power operator `**` not fully supported
- **Mathematical Modeling:** Limits ability to model certain non-convex functions

### After Fixing Issues #194, #195, and sqr()
- Total fixtures: 16
- Successfully parsing: 9 (currently) → 15 (after sqr fix)
- Blocked by odd powers: 1 (6.25%)
- **This is the last remaining blocker**

## Example GAMS Files Affected

### Current Syntax (Not Supported)
```gams
Variables x, y, obj;
Equations objdef;

objdef.. obj =e= x**3 + y**3;

Model m /all/;
Solve m using nlp minimizing obj;
```

### Workaround (power function)
```gams
Variables x, y, obj;
Equations objdef;

objdef.. obj =e= power(x, 3) + power(y, 3);

Model m /all/;
Solve m using nlp minimizing obj;
```

### Example from Blocked Fixture (nonconvex_odd_power.gms)
```gams
$title Non-Convex Problem - Odd Powers

Variables x, y, obj;
Equations objdef, linear_constr;

objdef.. obj =e= x**3 + y**3;  # <-- Parser fails here
linear_constr.. x + y =e= 2;

x.lo = -5; x.up = 5;
y.lo = -5; y.up = 5;

Model m /all/;
Solve m using nlp minimizing obj;
```

## GAMS Power Operator Specification

According to GAMS documentation:
- **Operator:** `x ** n` or `x ^ n`
- **Definition:** Raises x to the power n
- **Domain:** x (any real), n (any real)
- **Examples:**
  - `x**2` - Square (currently works)
  - `x**3` - Cube (NOT working)
  - `x**0.5` - Square root (needs testing)
  - `x**(-1)` - Reciprocal (needs testing)

**Alternative Syntax:**
- `power(x, n)` - Function form (currently works)
- `x ** n` - Operator form (partially works)
- `x ^ n` - Alternative operator (needs testing)

## Root Cause Analysis

Based on the error location and grammar, the issue appears to be in how the parser handles the power operator's right-hand side (the exponent).

**Possible causes:**
1. Grammar expects specific token types for exponents (not general expressions)
2. Precedence/associativity issue with `**` operator
3. Lexer tokenization issue with `**3` sequence
4. Context-dependent parsing where `**` handling differs based on exponent

**Need to investigate:**
- Current grammar rule for `power` operation
- How `x**2` works but `x**3` doesn't
- Whether it's specific to odd numbers or all integers > 2

## Proposed Solution

### Option 1: Fix Grammar Power Expression (Recommended)

Update the grammar to properly handle arbitrary integer exponents:

**Investigation needed:**
```python
# Check current grammar in src/gams/gams_grammar.lark
# Look for power operator rules
# Identify why x**2 works but x**3 doesn't
```

**Likely fix:**
```lark
# Current (hypothetical issue):
power: atom ("**" | "^") (NUMBER | atom)  # May be too restrictive

# Fixed:
power: atom ("**" | "^") expr  # Allow any expression as exponent
```

**Pros:**
- Proper solution
- Supports all power expressions
- Matches GAMS specification

**Cons:**
- Need to identify exact grammar issue first
- May affect precedence/associativity

### Option 2: Normalize to power() Function

Transform `x**n` to `power(x, n)` during parsing:

**Pros:**
- Consistent internal representation
- power() already works

**Cons:**
- Doesn't fix root cause
- May mask underlying grammar issue

## Recommended Approach

**Option 1 (Fix Grammar)** is recommended because:
1. **Root Cause Fix:** Addresses the underlying parsing issue
2. **Complete Support:** Will work for all power expressions
3. **GAMS Compliant:** Matches GAMS specification exactly
4. **Maintainable:** Proper grammar fix vs workaround

**However**, need to first investigate why `x**2` works but `x**3` doesn't.

## Investigation Steps

1. **Examine current grammar:**
   ```bash
   grep -A 5 "power\|**" src/gams/gams_grammar.lark
   ```

2. **Test various exponents:**
   ```python
   test_cases = [
       "x**1",   # Linear - should work
       "x**2",   # Quadratic - known to work
       "x**3",   # Cubic - known to fail
       "x**4",   # Quartic - unknown
       "x**(-1)", # Reciprocal - unknown
       "x**0.5",  # Fractional - unknown
   ]
   ```

3. **Check tokenization:**
   - Is `**3` being tokenized as single token or two?
   - Is `3` being recognized as NUMBER token?

4. **Review power expression AST:**
   - How is `x**2` represented in parse tree?
   - What's different about `x**3`?

## Implementation Checklist

- [ ] Investigate current power operator grammar
- [ ] Identify why `x**2` works but `x**3` fails
- [ ] Test various power expressions (1, 2, 3, 4, -1, 0.5, etc.)
- [ ] Fix grammar to support all power expressions
- [ ] Add unit tests for power operator:
  - [ ] Integer powers: x**1, x**2, x**3, x**4, x**5
  - [ ] Negative powers: x**(-1), x**(-2)
  - [ ] Fractional powers: x**0.5, x**1.5
  - [ ] Zero power: x**0
  - [ ] Variable exponent: x**y
- [ ] Test with `nonconvex_odd_power.gms` fixture
- [ ] Update documentation with supported power syntax

## Test Cases

```python
def test_power_operator_integers():
    """Test ** operator with integer exponents."""
    for n in [1, 2, 3, 4, 5]:
        source = f"""
        Variables x, obj;
        Equations eq;
        eq.. obj =e= x**{n};
        Model m /all/;
        Solve m using nlp minimizing obj;
        """
        model_ir = parse_model_text(source)
        assert "eq" in model_ir.equations

def test_power_operator_negative():
    """Test ** operator with negative exponents."""
    source = """
    Variables x, obj;
    Equations eq;
    eq.. obj =e= x**(-1);
    """
    model_ir = parse_model_text(source)
    assert "eq" in model_ir.equations

def test_power_operator_fractional():
    """Test ** operator with fractional exponents."""
    source = """
    Variables x, obj;
    Equations eq;
    eq.. obj =e= x**0.5;
    """
    model_ir = parse_model_text(source)
    assert "eq" in model_ir.equations

def test_cubic_nonconvex():
    """Test cubic expression (from fixture)."""
    source = """
    Variables x, y, obj;
    Equations objdef;
    objdef.. obj =e= x**3 + y**3;
    """
    model_ir = parse_model_text(source)
    assert "objdef" in model_ir.equations
```

## Acceptance Criteria

1. Parser successfully handles `x**n` for any integer n
2. Parser handles negative exponents: `x**(-1)`
3. Parser handles fractional exponents: `x**0.5`
4. Parser handles variable exponents: `x**y`
5. `nonconvex_odd_power.gms` fixture parses successfully
6. Zero regressions in existing power expression tests
7. Documentation updated with supported power syntax

## Related Issues

- **Issue #194:** Parser `$title` directive support (✅ Resolved in f21396e)
- **Issue #195:** Comma-separated variable declarations (✅ Resolved in bc50094)
- **Issue #196:** Parser `sqr()` function support (proposed)
- **After #194 + #195:** 9/16 fixtures parse (56.25%)
- **After #196 (sqr):** Expected 15/16 fixtures parse (93.75%)
- **After this fix:** Expected 16/16 fixtures parse (100% ✅)

## Priority Justification

**Low Priority** because:
- **Minimal Blocking:** Only 1/16 convexity fixtures affected (6.25%)
- **Workaround Available:** Can use `power(x, 3)` function form
- **Edge Case:** Odd powers are less common than quadratics
- **Lower Impact:** After sqr() fix, this is the only remaining blocker

**Should Address In:**
- Sprint 7 (after sqr() function support)
- Can be bundled with other grammar improvements
- Part of "complete GAMS syntax support" initiative

## Estimated Effort

**2-4 hours total:**
- 1-2 hours: Investigate grammar issue and root cause
- 1 hour: Fix grammar to support all power expressions
- 30 min: Add comprehensive power operator tests
- 30 min: Test with fixture and verify

**Unknown factor:** May be quick fix if issue is obvious, or complex if it involves precedence/associativity issues.

## Notes

- Discovered during Sprint 6 Day 3 after fixing Issues #194 and #195
- Currently the LAST remaining blocker for convexity fixtures
- Interesting that `x**2` works but `x**3` doesn't - suggests specific handling of quadratics?
- Need investigation before implementation
- Low priority due to workaround and small impact (1 fixture)
- Would achieve 100% fixture parsing rate if fixed

## Discovery Context

After successfully fixing Issue #194 ($title), Issue #195 (comma-separated variables), and identifying sqr() issue:

**Test Results:**
```
Testing 16 convexity fixtures...

✅ 9 fixtures: Parse successfully
❌ 6 fixtures: Blocked by sqr() function (Issue #196)
❌ 1 fixture (nonconvex_odd_power.gms): Blocked by this issue

Error:
UnexpectedCharacters: No terminal matches '3' in the current parser context, at line 11 col 31

objdef.. obj =e= x**3 + y**3;
                              ^
```

**Interesting observation:** The error points to position after `y**3`, suggesting the parser handled `x**3` but failed on `y**3`. This might be a context-sensitive issue or error recovery artifact.

## Path to 100% Fixture Support

1. ✅ **Issue #194**: $title directive support → +0 fixtures
2. ✅ **Issue #195**: Comma-separated declarations → +6 fixtures (3→9)
3. ⏳ **Issue #196**: sqr() function support → +6 fixtures (9→15)
4. ⏳ **This issue**: Odd power syntax → +1 fixture (15→16)
5. 🎉 **Result**: 16/16 fixtures parse (100%)
