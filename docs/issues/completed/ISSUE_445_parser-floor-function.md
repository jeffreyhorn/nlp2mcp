# Parser: Missing `floor()` Function

**GitHub Issue:** [#445](https://github.com/jeffreyhorn/nlp2mcp/issues/445)
**Status:** Open  
**Priority:** Medium  
**Blocking Model:** gasoil.gms (tier 2)

---

## Problem Summary

The GAMS parser does not recognize the `floor()` function. The `FUNCNAME` terminal in the grammar includes `ceil` but not `floor`, causing parsing to fail when `floor()` is encountered.

---

## Reproduction

### Test Case

```gams
Scalar x;
x = floor(5/2);
```

### Error Message

```
Error: Parse error at line 2, column 5: Unexpected character: '5'
  x = floor(5/2);
            ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gasoil.gms`  
**Line:** 106

```gams
itau(nm) = min(50,floor(tau[nm]/h)+1);
```

The parser fails at the `/` character after `tau[nm]` because `floor` is not recognized as a function name, causing the expression to be misparsed.

---

## Technical Analysis

### Current Grammar

In `src/gams/gams_grammar.lark`, the `FUNCNAME` terminal is defined as:

```lark
FUNCNAME: /(?i:abs|exp|log10|log2|log|sqrt|sin|cos|tan|min|max|smin|smax|power|sqr|ord|card|uniform|normal|gamma|loggamma|round|mod|ceil)\b/
```

The terminal includes `ceil` but is missing `floor`.

### Root Cause

When `floor` is not recognized as a function name, the parser cannot match `floor(...)` as a `func_call` rule. This causes subsequent parsing to fail when it encounters the parenthesized expression.

---

## Suggested Fix

Add `floor` to the `FUNCNAME` terminal in `src/gams/gams_grammar.lark`:

```lark
FUNCNAME: /(?i:abs|exp|log10|log2|log|sqrt|sin|cos|tan|min|max|smin|smax|power|sqr|ord|card|uniform|normal|gamma|loggamma|round|mod|ceil|floor)\b/
```

---

## Testing Requirements

1. **Unit test:** Verify `floor()` function parses correctly
2. **Integration test:** Verify `gasoil.gms` parses completely after fix
3. **Edge cases:**
   - `floor(x)`
   - `floor(x/y)`
   - `floor(expr) + other_expr`
   - Nested: `min(floor(x), y)`

### Example Test Cases

```python
def test_floor_function_basic():
    code = "Scalar x; x = floor(5.7);"
    tree = parse_text(code)
    assert tree is not None

def test_floor_function_with_division():
    code = "Parameter tau / 0.5 /; Scalar h / 0.1 /; Scalar result; result = floor(tau/h);"
    tree = parse_text(code)
    assert tree is not None

def test_floor_in_min():
    code = "Scalar x; x = min(50, floor(3.7) + 1);"
    tree = parse_text(code)
    assert tree is not None
```

---

## Impact

- **Severity:** Medium - Blocks one tier 2 model
- **Workaround:** None - cannot parse models using `floor()`
- **Scope:** Any GAMS code using the `floor()` function

---

## Related Issues

- Similar to potential missing functions in `FUNCNAME`
- Consider auditing GAMS documentation for other missing math functions

---

## GAMS Reference

From GAMS documentation, `floor(x)` returns the largest integer less than or equal to x. It is a standard mathematical function commonly used in:
- Discretization calculations
- Index computations
- Rounding operations
