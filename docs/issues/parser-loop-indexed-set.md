# Parser: Loop Over Indexed/Mapped Set Not Supported

**GitHub Issue:** [#450](https://github.com/jeffreyhorn/nlp2mcp/issues/450)
**Status:** Open  
**Priority:** Medium  
**Blocking Model:** gasoil.gms (tier 2)

---

## Problem Summary

The GAMS parser does not support looping over indexed (mapped) sets. GAMS allows `loop(setname(i,j), ...)` syntax to iterate over a subset defined by a multi-dimensional set, but the parser fails when encountering this pattern.

---

## Reproduction

### Test Case

```gams
Set nm / nm1*nm3 /;
Set i / i1*i5 /;
Set mapitau(nm,i);
loop(mapitau(nm,i), display nm);
```

### Error Message

```
Error: Parse error at line 4, column 29: Unexpected character: 'n'
  loop(mapitau(nm,i), display nm);
                              ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gasoil.gms` (via `copspart.inc`)  
**Line:** ~141 (line 63 of copspart.inc)

```gams
loop(mapitau(nm,i),
  v.l[nh,s]$(ord(nh) > itau(nm-1)+1) = z[nm,s];
);
```

The model uses `mapitau(nm,i)` to define a mapping between measurement points and partition intervals for collocation.

---

## Technical Analysis

### GAMS Loop Domain Syntax

The `loop` statement supports multiple domain specifications:

1. **Simple index:** `loop(i, ...)` - iterate over all elements of set i
2. **Multi-index tuple:** `loop((i,j), ...)` - iterate over cartesian product
3. **Filtered index:** `loop(i$(cond), ...)` - iterate with condition
4. **Indexed set:** `loop(setname(i,j), ...)` - iterate over elements where setname(i,j) is true

The indexed set form (4) is used to iterate over sparse subsets defined by multi-dimensional sets.

### Current Grammar

The current `loop_stmt` rules support forms 1-3 but not form 4:

```lark
loop_stmt: LOOP_K "(" id_list "," loop_body ")" SEMI
         | LOOP_K "(" "(" id_list ")" "," loop_body ")" SEMI
         | LOOP_K "(" ID DOLLAR "(" expr ")" "," loop_body ")" SEMI
         | LOOP_K "(" "(" id_list ")" DOLLAR "(" expr ")" "," loop_body ")" SEMI
```

### Root Cause

The grammar lacks a rule for `ID "(" id_list ")"` as a loop domain, which would match `setname(i,j)`.

---

## Suggested Fix

Add loop domain rules for indexed set iteration:

```lark
loop_stmt: LOOP_K "(" loop_domain "," loop_body ")" SEMI

loop_domain: id_list                                          -> loop_simple
           | "(" id_list ")"                                   -> loop_tuple
           | ID DOLLAR "(" expr ")"                            -> loop_filtered
           | "(" id_list ")" DOLLAR "(" expr ")"               -> loop_tuple_filtered
           | ID "(" id_list ")"                                -> loop_indexed_set
           | ID "(" id_list ")" DOLLAR "(" expr ")"            -> loop_indexed_set_filtered
```

The `loop_indexed_set` form matches `setname(i,j)` where `setname` is a multi-dimensional set and `i,j` are the index variables bound during iteration.

---

## Testing Requirements

1. **Unit test:** Verify loop over indexed set parses correctly
2. **Integration test:** Verify `gasoil.gms` parses completely after fix
3. **Edge cases:**
   - 2D indexed set: `loop(map(i,j), ...)`
   - 3D indexed set: `loop(map(i,j,k), ...)`
   - Indexed set with filter: `loop(map(i,j)$(cond), ...)`
   - Indexed set with body: `loop(map(i,j), x(i,j) = 1);`

### Example Test Cases

```python
def test_loop_indexed_set_2d():
    code = """
Set i / i1*i3 /;
Set j / j1*j3 /;
Set map(i,j);
Parameter x(i,j);
loop(map(i,j), x(i,j) = 1);
"""
    tree = parse_text(code)
    assert tree is not None

def test_loop_indexed_set_with_body():
    code = """
Set nm / nm1*nm3 /;
Set i / i1*i5 /;
Set mapitau(nm,i);
Variable v(i);
loop(mapitau(nm,i), v.l(i) = nm.val);
"""
    tree = parse_text(code)
    assert tree is not None
```

---

## Impact

- **Severity:** Medium - Blocks tier 2 model after prior fixes
- **Workaround:** Restructure loop to use explicit conditionals or nested loops
- **Scope:** Any GAMS code using mapped/indexed sets in loop domains

---

## Related Issues

- Issue #449: Loop conditional filter (resolved)
- This pattern combines set iteration with index binding

---

## GAMS Reference

From GAMS documentation, the indexed set loop form:

```
loop(setname(indices), statements);
```

This iterates over all combinations of indices where `setname(indices)` evaluates to true (i.e., the element is in the set). This is commonly used for:
- Sparse iteration patterns
- Mapping between different index domains
- Conditional iteration without explicit `$` conditions
