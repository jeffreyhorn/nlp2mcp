# Parser: Loop Statement Conditional Filter Not Supported

**GitHub Issue:** [#449](https://github.com/jeffreyhorn/nlp2mcp/issues/449)
**Status:** Completed  
**Priority:** Medium  
**Blocking Model:** gasoil.gms (tier 2)

---

## Problem Summary

The GAMS parser does not support conditional filters on set indices within `loop` statements. GAMS allows filtering the iteration domain using the `$` operator directly on the set index, such as `loop(nc$(ord(nc)>1), ...)`, but the parser fails when encountering this syntax.

---

## Reproduction

### Test Case

```gams
Set nc / nc1*nc4 /;
Parameter fact(nc);
fact('nc1') = 1;
loop(nc$(ord(nc)>1), fact(nc) = fact(nc-1)*ord(nc));
```

### Error Message

```
Error: Parse error at line 111, column 25: Unexpected character: '$'
  fact('nc1') = 1; loop(nc$(ord(nc)>1), fact(nc) = fact(nc-1)*ord(nc));
                          ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gasoil.gms`  
**Line:** 111

```gams
fact('nc1') = 1; loop(nc$(ord(nc)>1), fact(nc) = fact(nc-1)*ord(nc));
```

This computes factorials by iterating over `nc` starting from the second element (where `ord(nc) > 1`).

---

## Technical Analysis

### GAMS Loop Conditional Syntax

The `loop` statement supports conditional filtering on the iteration domain:

1. **Simple loop:** `loop(i, statement);`
2. **Filtered loop:** `loop(i$(condition), statement);`
3. **Multi-index loop:** `loop((i,j), statement);`
4. **Multi-index filtered:** `loop((i,j)$(condition), statement);`

The `$` conditional filter restricts which elements of the set are iterated over. Only elements where the condition evaluates to true are processed.

### Current Grammar

The current `loop_stmt` rule likely only supports simple set references without the conditional filter syntax.

### Root Cause

The grammar rule for `loop` does not include a pattern for `ID DOLLAR "(" expr ")"` as the iteration domain.

---

## Suggested Fix

Extend the `loop_stmt` rule in `src/gams/gams_grammar.lark` to support conditional filters:

```lark
loop_stmt: LOOP_K "(" loop_domain "," stmt_list ")" SEMI

loop_domain: ID                                    -> loop_simple
           | ID DOLLAR "(" expr ")"                -> loop_filtered
           | "(" id_list ")"                       -> loop_multi
           | "(" id_list ")" DOLLAR "(" expr ")"   -> loop_multi_filtered
```

Alternatively, reuse existing conditional syntax patterns if available.

---

## Testing Requirements

1. **Unit test:** Verify loop with conditional filter parses correctly
2. **Integration test:** Verify `gasoil.gms` parses completely after fix
3. **Edge cases:**
   - Simple filtered loop: `loop(i$(ord(i)>1), x(i) = 1);`
   - Complex condition: `loop(i$(ord(i)>1 and ord(i)<5), ...);`
   - Multi-index filtered: `loop((i,j)$(ord(i)=ord(j)), ...);`
   - Nested conditions with parameters: `loop(i$(a(i)>0), ...);`

### Example Test Cases

```python
def test_loop_with_conditional_filter():
    code = """
Set i / i1*i5 /;
Parameter x(i);
loop(i$(ord(i)>1), x(i) = ord(i));
"""
    tree = parse_text(code)
    assert tree is not None

def test_loop_factorial_pattern():
    code = """
Set nc / nc1*nc4 /;
Parameter fact(nc);
fact('nc1') = 1;
loop(nc$(ord(nc)>1), fact(nc) = fact(nc-1)*ord(nc));
"""
    tree = parse_text(code)
    assert tree is not None

def test_loop_multi_index_filtered():
    code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Parameter x(i,j);
loop((i,j)$(ord(i)=ord(j)), x(i,j) = 1);
"""
    tree = parse_text(code)
    assert tree is not None
```

---

## Impact

- **Severity:** Medium - Blocks tier 2 model after floor() fix
- **Workaround:** Rewrite loop with explicit if-statement inside:
  ```gams
  loop(nc, if(ord(nc)>1, fact(nc) = fact(nc-1)*ord(nc)));
  ```
- **Scope:** Any GAMS code using filtered loops

---

## Related Issues

- Similar to conditional assignment syntax (`lvalue$condition = expr;`)
- May share patterns with sum/prod conditional filters if those exist

---

## GAMS Reference

From GAMS documentation, the `loop` statement with conditional filtering:

```
loop(index$(condition), statements);
```

The conditional filter `$(condition)` restricts the iteration to only those index values where the condition is true. This is commonly used for:
- Skipping boundary elements in recursive calculations
- Iterating over subsets dynamically
- Conditional initialization patterns

This is a core GAMS feature for efficient iteration control.
