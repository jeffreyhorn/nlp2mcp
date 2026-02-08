# Parser: Variable Bounds with Subset Indexing Not Supported

**GitHub Issue:** [#455](https://github.com/jeffreyhorn/nlp2mcp/issues/455)
**Status:** Open  
**Priority:** Medium  
**Blocking Model:** gastrans.gms (tier 2)

---

## Problem Summary

The parser does not correctly handle variable bounds when using subset indexing. When a variable is defined with multiple indices (e.g., `f(a,i,j)`) but bounds are set using a subset that maps to those indices (e.g., `f.lo(aij(as,i,j))`), the parser incorrectly reports an index count mismatch.

---

## Reproduction

### Test Case

```gams
Set i / 1*3 /, j / 1*3 /;
Set a / a1, a2 /;
Set aij(a,i,j) "arc subset";
Set as(a) / a1 /;

Variable f(a,i,j);

* This should work - aij(as,i,j) expands to the 3 indices (a,i,j)
f.lo(aij(as,i,j)) = 0;
```

### Error Message

```
Variable 'f' bounds expect 3 indices but received 1 [context: expression] (line 145, column 1)
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gastrans.gms`  
**Line:** 145

```gams
f.lo(aij(as,i,j)) = 0;
```

The variable `f` is defined with domain `(a,i,j)` and `aij` is a subset over `(a,i,j)`. The syntax `f.lo(aij(as,i,j))` sets the lower bound for all elements of `f` where the indices are in the subset `aij` and the first index is in `as`.

---

## Technical Analysis

### GAMS Subset Indexing Semantics

In GAMS, when you write `f.lo(aij(as,i,j))`, this means:
- `aij` is a subset defined over domain `(a,i,j)`
- The expression `aij(as,i,j)` filters to only those tuples where `a` is in `as`
- The result is a valid 3-dimensional index into variable `f`

### Current Behavior

The parser sees `aij(as,i,j)` as a single reference and counts it as 1 index, when it should recognize that:
1. `aij` is a subset over `(a,i,j)` 
2. The expression expands to provide all 3 indices needed for `f`

### Root Cause

The variable bounds assignment handler doesn't properly expand subset references to determine the actual index count. It's counting the number of top-level tokens rather than understanding the dimensional semantics of subset indexing.

---

## Suggested Fix

Modify the bounds assignment handler in `src/ir/parser.py` to:

1. When encountering a reference like `aij(as,i,j)` in a bounds context
2. Look up the definition of `aij` to determine its domain dimensions
3. Use the subset's domain dimension count rather than the syntactic argument count

Alternatively, for a mock/skip approach:
- Recognize this pattern and skip validation of index counts for bounds assignments involving subset indexing
- Log a warning that the bounds assignment is being accepted without full validation

---

## Testing Requirements

1. **Unit test:** Verify bounds with subset indexing parse correctly
2. **Integration test:** Verify `gastrans.gms` parses completely after fix

### Example Test Cases

```python
def test_bounds_with_subset_indexing():
    code = '''
    Set i / 1*3 /, j / 1*3 /;
    Set a / a1, a2 /;
    Set aij(a,i,j);
    Set as(a) / a1 /;
    Variable f(a,i,j);
    f.lo(aij(as,i,j)) = 0;
    '''
    model = parse_model_text(code)
    assert model is not None

def test_bounds_with_simple_subset():
    code = '''
    Set i / 1*3 /, j / 1*3 /;
    Set aij(i,j);
    Variable f(i,j);
    f.lo(aij) = 0;
    '''
    model = parse_model_text(code)
    assert model is not None
```

---

## Impact

- **Severity:** Medium - Blocks one tier 2 model
- **Workaround:** None practical - the bounds are semantically important
- **Scope:** Any GAMS code using subset-indexed variable bounds

---

## Related Issues

- This is a semantic/validation issue, not a grammar issue
- The grammar correctly parses the syntax; the issue is in index count validation
