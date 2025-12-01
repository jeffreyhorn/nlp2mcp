# Issue: Curly Braces in Sum/Aggregation Functions

**GitHub Issue:** [#355](https://github.com/jeffreyhorn/nlp2mcp/issues/355)  
**Status:** Open  
**Priority:** MEDIUM  
**Complexity:** SIMPLE-MEDIUM (1-2h)  
**Impact:** 1 Tier 2 model (jbearing)  
**Sprint:** Sprint 13

---

## Problem Description

GAMS allows curly braces `{}` as an alternative to parentheses `()` for sum and other aggregation functions. Our parser currently only supports parentheses, causing parse failures when encountering the curly brace syntax.

---

## Example

### jbearing.gms (line 62)

**GAMS Syntax:**
```gams
obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                                           *(wq[j] + 2*wq[j+1])};
```

**Standard Syntax (currently supported):**
```gams
obj =e= (hx*hy/12)*sum((nx(i+1),ny(j+1)), (wq[i] + 2*wq[i+1])
                                           *(wq[j] + 2*wq[j+1]));
```

**Error:**
```
Error: Parse error at line 62, column 23: Unexpected character: '{'
  obj =e= (hx*hy/12)*sum{(nx(i+1),ny(j+1)), ...
                        ^
```

---

## GAMS Semantics

Both syntaxes are equivalent in GAMS:
- `sum{(i,j), expr}` ≡ `sum((i,j), expr)`
- `prod{i, expr}` ≡ `prod(i, expr)`
- `smin{i, expr}` ≡ `smin(i, expr)`
- `smax{i, expr}` ≡ `smax(i, expr)`

**Usage:** Curly braces are stylistic and have no semantic difference. Some users prefer `{}` for aggregations to distinguish them from function calls or indexing.

---

## Implementation

### 1. Grammar Extension

**Current Rule:**
```lark
aggr_expr: aggr_func "(" index_list "," expr ")"    -> aggr_indexed
         | aggr_func "(" expr ")"                   -> aggr_simple

aggr_func: /(?i:sum|prod|smin|smax)\b/
```

**Proposed Rule:**
```lark
aggr_expr: aggr_func aggr_delim_open index_list "," expr aggr_delim_close    -> aggr_indexed
         | aggr_func aggr_delim_open expr aggr_delim_close                   -> aggr_simple

aggr_func: /(?i:sum|prod|smin|smax)\b/
aggr_delim_open: "(" | "{"
aggr_delim_close: ")" | "}"
```

**Alternative (simpler):**
```lark
aggr_expr: aggr_func ("(" | "{") index_list "," expr (")" | "}")    -> aggr_indexed
         | aggr_func ("(" | "{") expr (")" | "}")                   -> aggr_simple
```

**Effort:** 15-30 minutes

---

### 2. Validation (Optional)

**Balanced Brackets Check:**
Ensure opening `{` matches closing `}` (and same for `()`).

```python
def _parse_aggr_expr(self, node: Tree) -> Expr:
    # Extract opening and closing delimiters
    opening = node.children[1].value  # "(" or "{"
    closing = node.children[-1].value  # ")" or "}"
    
    # Validate balance
    if (opening == "(" and closing != ")") or (opening == "{" and closing != "}"):
        raise self._error(f"Mismatched brackets: '{opening}' ... '{closing}'", node)
    
    # Continue with normal parsing...
```

**Effort:** 15 minutes

---

### 3. Testing

**Unit Tests:**
```python
def test_sum_with_curly_braces():
    """Test sum{i, expr} syntax"""
    source = """
    Variable x(i);
    Equation eq;
    eq.. sum{i, x(i)} =e= 10;
    """
    model = parse_model_text(source)
    # Verify equation parses correctly
    
def test_sum_indexed_with_curly_braces():
    """Test sum{(i,j), expr} syntax"""
    source = """
    Variable x(i,j);
    Equation eq;
    eq.. sum{(i,j), x(i,j)} =e= 100;
    """
    model = parse_model_text(source)
    
def test_nested_aggr_mixed_brackets():
    """Test sum{i, prod(j, x(i,j))} - mixed brackets"""
    source = """
    Variable x(i,j);
    Equation eq;
    eq.. sum{i, prod(j, x(i,j))} =e= 50;
    """
    model = parse_model_text(source)
    
def test_mismatched_brackets_error():
    """Test sum{i, expr) raises error"""
    source = """
    Variable x(i);
    Equation eq;
    eq.. sum{i, x(i)) =e= 10;
    """
    with pytest.raises(ParseError, match="Mismatched brackets"):
        parse_model_text(source)
```

**Integration Test:**
```python
def test_jbearing_parses():
    """Test jbearing.gms with curly braces"""
    model = parse_model_file('tests/fixtures/tier2_candidates/jbearing.gms')
    # Should parse successfully
```

**Effort:** 30 minutes

---

## Total Effort Estimate

| Task | Effort |
|------|--------|
| Grammar extension | 0.5h |
| Validation logic (optional) | 0.25h |
| Testing | 0.5h |
| **TOTAL** | **1.25h** |

---

## Risks and Challenges

### Risk 1: Bracket Mismatch Edge Cases
User writes `sum{i, x(i))` (mismatched brackets).

**Mitigation:** Add validation check in parser. Clear error message.

---

### Risk 2: Nested Aggregations
Complex nesting like `sum{i, smax{j, prod(k, x(i,j,k))}}`.

**Mitigation:** Grammar should handle recursively. Test with nested cases.

---

## Affected Models

| Model | Lines | Error Location | Additional Blockers | Status |
|-------|-------|----------------|---------------------|--------|
| jbearing | 55 | line 62, col 23 | multiple_alias_declaration (FIXED Day 4) | Partially blocked |

**Parse Rate Impact:** +10% Tier 2 (2/10 models → 3/10 models)

**Note:** jbearing.gms was partially unlocked on Day 4 when `multiple_alias_declaration` was fixed. Curly braces are the remaining blocker.

---

## Recommendation

**Implement in Sprint 13** as quick win after higher-priority blockers.

**Rationale:**
- Low effort (1-2h)
- Clean implementation (straightforward grammar change)
- Unlocks 1 model

**Sprint 13 Sequencing:**
1. Day 1-2: newline_as_separator (HIGH priority, 3 models)
2. Day 3: curly_braces_sum (MEDIUM priority, 1 model) ← Quick win
3. Day 4+: tuple_notation or table_wildcard (STRETCH)

---

## Alternative: User Workaround

If implementation is deferred, users can manually convert curly braces to parentheses:

**Before:**
```gams
obj =e= sum{(i,j), x(i,j)};
```

**After:**
```gams
obj =e= sum((i,j), x(i,j));
```

This is a simple find-replace operation and maintains semantic equivalence.

---

## References

- Failing model: `tests/fixtures/tier2_candidates/jbearing.gms`
- Grammar: `src/gams/gams_grammar.lark` (aggregation expression rules)
- Parser: `src/ir/parser.py` (aggregation parsing section)
- Blocker analysis: `docs/planning/EPIC_2/SPRINT_12/TIER_2_BLOCKER_ANALYSIS.md`
- GAMS Documentation: Aggregation functions (sum, prod, smin, smax)

---

## Implementation Update (2025-12-01)

### Status: PARTIALLY IMPLEMENTED

**Commit:** 95452a4

**What Works:**
- ✅ Basic curly braces: `sum{i, expr}`
- ✅ Nested sums: `sum{i, sum{j, expr}}`
- ✅ Complex expressions: `sum{i, x(i)*2 + y(i)/3}`
- ✅ Mixed brackets: `sum{i, sum(j, expr)}`
- ✅ Backward compatibility: all `sum(i, expr)` syntax still works

**What Doesn't Work:**
- ❌ Subset indexing with arithmetic: `sum{(nx(i+1),ny(j+1)), expr}`

### Additional Blocker Discovered

**jbearing.gms** requires a separate feature beyond curly braces:

**Pattern:** `sum{(nx(i+1), ny(j+1)), expr}`

**Issue:** This uses **arithmetic expressions inside subset filters**, not just curly braces.
- `nx(i+1)` means "filter set nx where index is i+1"
- Requires extending `index_expr` to support arithmetic expressions
- Current grammar only supports: `ID "(" id_list ")"` for subset indexing

**New Blocker:** Subset Indexing with Arithmetic Expressions
- Effort: 2-3h
- Pattern: `set_name(arithmetic_expr)` in sum indices
- Example: `nx(i+1)`, `ny(j+1)`, `low(n*2)`
- Affects: jbearing.gms

**Recommendation:** Create new GitHub issue for this separate blocker.

### Impact

**Parse Rate:** Still 20% (2/10 models: fct, process)
- jbearing.gms NOT unlocked (needs arithmetic subset indexing)
- Curly braces implementation correct but insufficient for jbearing

**Value:** Curly braces support is still useful for:
- Future models using curly brace syntax
- User preference/style
- GAMS compatibility

### Next Steps

1. **Option A:** Defer jbearing to Sprint 14+
   - Create issue for subset indexing with arithmetic
   - Focus on higher-impact blockers (#353, #354)
   
2. **Option B:** Implement arithmetic subset indexing now
   - Adds 2-3h to current work
   - Would unlock jbearing (+10% Tier 2)
   - May discover additional blockers in jbearing

**Recommended:** Option A - defer to Sprint 14+, focus on #353 next
