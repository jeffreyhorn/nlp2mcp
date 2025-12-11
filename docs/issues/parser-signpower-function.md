# Parser: signpower Function Not Supported

**GitHub Issue:** [#453](https://github.com/jeffreyhorn/nlp2mcp/issues/453)
**Status:** Open  
**Priority:** Medium  
**Blocking Model:** gastrans.gms (tier 2)

---

## Problem Summary

The GAMS parser does not support the `signpower` function. This function computes a signed power operation and is used in some GAMS models for handling directional flow calculations.

---

## Reproduction

### Test Case

```gams
Variable x;
Equation eq;
eq.. signpower(x, 2) =e= 0;
```

### Error Message

```
Error: Parse error at line 134, column 43: Unexpected character: '2'
  weymouthp(aij(ap,i,j)).. signpower(f(aij),2) =e= c2(aij)*(pi(i) - pi(j));
                                            ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gastrans.gms`  
**Line:** 134

```gams
weymouthp(aij(ap,i,j)).. signpower(f(aij),2) =e= c2(aij)*(pi(i) - pi(j));
```

---

## Technical Analysis

### GAMS signpower Function

The `signpower(x, y)` function computes `sign(x) * |x|^y`. This is useful for:
- Flow equations where direction matters
- Avoiding discontinuities at zero
- Gas pipeline network models (like gastrans.gms)

Mathematical definition:
```
signpower(x, y) = sign(x) * abs(x)^y
                = x * abs(x)^(y-1)  when x != 0
```

### Current Grammar

The `FUNCNAME` terminal in `src/gams/gams_grammar.lark` does not include `signpower`:

```lark
FUNCNAME: /(?i:abs|exp|log10|log2|log|sqrt|sin|cos|tan|min|max|smin|smax|power|sqr|ord|card|uniform|normal|gamma|loggamma|round|mod|ceil|floor)\b/
```

### Root Cause

The `signpower` function is missing from the list of recognized function names in the grammar.

---

## Suggested Fix

Add `signpower` to the `FUNCNAME` terminal in `src/gams/gams_grammar.lark`:

```lark
FUNCNAME: /(?i:abs|exp|log10|log2|log|sqrt|sin|cos|tan|min|max|smin|smax|power|signpower|sqr|ord|card|uniform|normal|gamma|loggamma|round|mod|ceil|floor)\b/
```

---

## Testing Requirements

1. **Unit test:** Verify `signpower` function parses correctly
2. **Integration test:** Verify `gastrans.gms` parses further after fix
3. **Edge cases:**
   - `signpower(x, 2)` - basic usage
   - `signpower(x+y, 2)` - expression as first argument
   - `signpower(x, n)` - variable exponent
   - Nested: `signpower(signpower(x, 2), 0.5)`

### Example Test Cases

```python
def test_signpower_basic():
    code = "Variable x; Equation eq; eq.. signpower(x, 2) =e= 0;"
    model = parse_model_text(code)
    assert model is not None

def test_signpower_in_expression():
    code = "Variable x, y; Equation eq; eq.. signpower(x, 2) + y =e= 0;"
    model = parse_model_text(code)
    assert model is not None
```

---

## Impact

- **Severity:** Medium - Blocks one tier 2 model
- **Workaround:** None - the function is semantically important for the model
- **Scope:** Any GAMS code using `signpower` function

---

## Related Issues

- Similar to issue #445 (floor function) - adding missing function to FUNCNAME

---

## GAMS Reference

From GAMS documentation:

> `signpower(x, y)` returns `sign(x) * abs(x)^y`

This function is particularly useful in optimization models where the sign of a variable matters, such as:
- Gas pipeline flow models
- Electrical network models
- Any model with bidirectional flow
