# Issue: Tuple Notation in Set Declarations

**GitHub Issue:** [#356](https://github.com/jeffreyhorn/nlp2mcp/issues/356)  
**Status:** Completed  
**Priority:** MEDIUM  
**Complexity:** MEDIUM (2-3h)  
**Impact:** 1 Tier 2 model (water - secondary blocker)  
**Sprint:** Sprint 13+

---

## Problem Description

GAMS allows tuple notation `ID.(id1,id2,...)` as shorthand for Cartesian product expansion in multi-dimensional set declarations. Our parser currently does not support this syntax, causing parse failures when encountering tuple notation.

---

## Example

### water.gms (line 26)

**GAMS Syntax:**
```gams
Set
   n 'nodes' / nw, e, cc, w, sw, s, se /
   a(n,n) 'arcs (arbitrarily directed)' / nw.(w,cc,n), e.(n,cc,s,se),
                                           cc.(w,sw,s,n), s.se, s.sw, sw.w /;
```

**Meaning:**
- `nw.(w,cc,n)` expands to: `(nw,w), (nw,cc), (nw,n)`
- `e.(n,cc,s,se)` expands to: `(e,n), (e,cc), (e,s), (e,se)`
- `s.se` is standard tuple notation: `(s,se)`
- `s.sw` is standard tuple notation: `(s,sw)`
- `sw.w` is standard tuple notation: `(sw,w)`

**Error:**
```
Error: Parse error at line 26, column 43: Unexpected character: '.'
  a(n,n) 'arcs' / nw.(w,cc,n), e.(n,cc,s,se), ...
                                            ^
```

---

## GAMS Semantics

### Standard Tuple Notation (currently supported):
```gams
Set a(n,n) / s.se, s.sw, sw.w /;
// Equivalent to: (s,se), (s,sw), (sw,w)
```

### Cartesian Product Notation (NOT supported):
```gams
Set a(n,n) / nw.(w,cc,n) /;
// Expands to: (nw,w), (nw,cc), (nw,n)
// Equivalent to: nw.w, nw.cc, nw.n
```

**Usage:** Shorthand for defining multiple tuples with a common prefix element.

---

## Implementation

### 1. Grammar Extension

**Current Rule:**
```lark
?set_member: range_expr              -> set_range
           | ID STRING               -> set_element_with_desc
           | ID                      -> set_element
           | STRING                  -> set_element
```

**Proposed Rule:**
```lark
?set_member: range_expr                                    -> set_range
           | ID "." "(" id_list ")"                        -> set_tuple_expansion
           | ID "." ID                                     -> set_tuple
           | ID STRING                                     -> set_element_with_desc
           | ID                                            -> set_element
           | STRING                                        -> set_element

// Note: ID "." "(" must come before ID "." ID to avoid ambiguity
```

**Effort:** 30 minutes

---

### 2. Parser Expansion Logic

**Expand Cartesian Product:**
```python
def _expand_tuple_notation(self, node: Tree) -> list[str]:
    """
    Expand ID.(id1,id2,...) into tuples.
    
    Example: nw.(w,cc,n) → ["nw.w", "nw.cc", "nw.n"]
    """
    prefix = _token_text(node.children[0])  # "nw"
    id_list_node = node.children[1]  # id_list containing (w,cc,n)
    
    # Extract suffix IDs
    suffixes = []
    for child in id_list_node.children:
        if isinstance(child, Token) and child.type == "ID":
            suffixes.append(_token_text(child))
    
    # Generate expanded tuples
    tuples = [f"{prefix}.{suffix}" for suffix in suffixes]
    return tuples
```

**Integration into `_extract_set_members`:**
```python
def _extract_set_members(self, node: Tree) -> list[str]:
    result = []
    for child in node.children:
        if isinstance(child, Tree):
            if child.data == "set_tuple_expansion":
                # Expand ID.(id1,id2,...) → [ID.id1, ID.id2, ...]
                result.extend(self._expand_tuple_notation(child))
            elif child.data == "set_tuple":
                # Standard tuple: ID.ID → "ID.ID"
                prefix = _token_text(child.children[0])
                suffix = _token_text(child.children[1])
                result.append(f"{prefix}.{suffix}")
            elif child.data == "set_element_with_desc":
                result.append(_token_text(child.children[0]))
            # ... other cases
    return result
```

**Effort:** 1 hour

---

### 3. Testing

**Unit Tests:**
```python
def test_tuple_expansion_single():
    """Test nw.(w,cc,n) → nw.w, nw.cc, nw.n"""
    source = """
    Set n / nw, w, cc /
        a(n,n) / nw.(w,cc) /;
    """
    model = parse_model_text(source)
    assert "a" in model.sets
    assert model.sets["a"].members == ["nw.w", "nw.cc"]
    
def test_tuple_expansion_multiple():
    """Test multiple expansions: nw.(w,cc), e.(n,s)"""
    source = """
    Set n / nw, e, w, cc, s /
        a(n,n) / nw.(w,cc), e.(n,s) /;
    """
    model = parse_model_text(source)
    assert model.sets["a"].members == ["nw.w", "nw.cc", "e.n", "e.s"]
    
def test_tuple_expansion_mixed():
    """Test expansion mixed with standard tuples"""
    source = """
    Set n / nw, e, w, cc, s, se, sw /
        a(n,n) / nw.(w,cc), s.se, s.sw /;
    """
    model = parse_model_text(source)
    assert model.sets["a"].members == ["nw.w", "nw.cc", "s.se", "s.sw"]
    
def test_water_exact_pattern():
    """Test exact pattern from water.gms"""
    source = """
    Set n / nw, e, cc, w, sw, s, se /
        a(n,n) / nw.(w,cc,n), e.(n,cc,s,se), cc.(w,sw,s,n), s.se, s.sw, sw.w /;
    """
    model = parse_model_text(source)
    # Should have 4 + 4 + 4 + 1 + 1 + 1 = 15 tuples
    assert len(model.sets["a"].members) == 15
```

**Integration Test:**
```python
def test_water_parses_with_tuple_notation():
    """Test water.gms (requires both tuple_notation AND newline_as_separator fixes)"""
    model = parse_model_file('tests/fixtures/tier2_candidates/water.gms')
    # Should parse successfully
```

**Effort:** 45 minutes

---

### 4. Edge Cases

**Edge Case 1: Single element expansion**
```gams
Set a(n,n) / nw.(w) /;  // Should expand to: nw.w
```

**Edge Case 2: Nested expansions (NOT supported by GAMS)**
```gams
Set a(n,n) / nw.(w.(x,y)) /;  // Invalid GAMS syntax
```

**Edge Case 3: Empty expansion (syntax error)**
```gams
Set a(n,n) / nw.() /;  // Should raise parse error
```

**Effort:** Handled by tests above

---

## Total Effort Estimate

| Task | Effort |
|------|--------|
| Grammar extension | 0.5h |
| Expansion logic | 1h |
| Testing | 0.75h |
| Documentation | 0.25h |
| **TOTAL** | **2.5h** |

---

## Risks and Challenges

### Risk 1: Grammar Ambiguity
`ID "." ID` vs `ID "." "(" ... ")"` may cause parsing conflicts.

**Mitigation:** Order grammar rules with expansion before standard tuple. Lark's greedy matching should prioritize longer match.

---

### Risk 2: Multi-dimensional Tuples
GAMS may support tuple expansion in >2D sets.

**Example:**
```gams
Set a(i,j,k) / x.(y.(z1,z2)) /;
```

**Mitigation:** Start with 2D support (all current models are 2D). Document limitation. Extend if needed.

---

## Dependencies

**Blocker:** water.gms also requires **newline_as_separator** fix (#353).

**Impact:** Even with tuple notation implemented, water.gms won't parse until newline_as_separator is fixed.

**Recommendation:** Implement newline_as_separator FIRST, then tuple notation.

---

## Affected Models

| Model | Lines | Primary Blocker | Secondary Blocker | Status |
|-------|-------|-----------------|-------------------|--------|
| water | 114 | newline_as_separator (#353) | tuple_notation (#356) | Blocked |

**Parse Rate Impact:** +0% initially (depends on #353 being fixed first)

**Combined Impact:** Once #353 is fixed, implementing #356 may unlock water.gms → +10% Tier 2

---

## Recommendation

**Defer to Sprint 13+** after newline_as_separator (#353) is implemented.

**Rationale:**
- Depends on higher-priority blocker (#353)
- Only affects 1 model (water.gms)
- Medium complexity (2-3h)
- Not critical path for MCP functionality

**Sprint 13 Sequencing:**
1. Day 1-2: Fix newline_as_separator (#353) - unlocks chem, gastrans
2. Day 3: Fix curly_braces_sum (#355) - unlocks jbearing  
3. Day 4: Fix tuple_notation (#356) - unlocks water
4. Result: 6/10 Tier 2 models (60% parse rate)

---

## Alternative: User Workaround

If implementation is deferred, users can manually expand tuple notation:

**Before:**
```gams
Set a(n,n) / nw.(w,cc,n) /;
```

**After:**
```gams
Set a(n,n) / nw.w, nw.cc, nw.n /;
```

This is tedious for large expansions but maintains semantic equivalence.

---

## References

- Failing model: `tests/fixtures/tier2_candidates/water.gms` (line 26)
- Grammar: `src/gams/gams_grammar.lark` (set member rules)
- Parser: `src/ir/parser.py` (`_extract_set_members` method)
- Related issue: #353 (newline_as_separator - prerequisite)
- GAMS Documentation: Set declarations with tuple notation
