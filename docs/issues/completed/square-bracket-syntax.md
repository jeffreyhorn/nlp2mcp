# Issue: Square Bracket Syntax in Expressions

**GitHub Issue:** [#362](https://github.com/jeffreyhorn/nlp2mcp/issues/362)  
**Status:** Open  
**Priority:** LOW  
**Complexity:** LOW (1-2h)  
**Impact:** 1 Tier 2 model (bearing)  
**Sprint:** Sprint 14+

---

## Problem Description

GAMS allows square brackets `[...]` as an alternative to parentheses `(...)` in mathematical expressions. This is purely stylistic and semantically equivalent to parentheses.

**Current Status:** Parser treats `[` and `]` as unexpected characters.

---

## Affected Models

### bearing.gms (line 144)

**GAMS Syntax:**
```gams
friction.. Ef*h =e= sqr(2*pi*N/60)*[(2*pi*mu)]*(r**4 - r0**4)/4;
```

**Error:**
```
Error: Parse error at line 144, column 44: Unexpected character: '['
  friction.. Ef*h =e= sqr(2*pi*N/60)*[(2*pi*mu)]*(r**4 - r0**4)/4;
                                           ^
```

**Blocker:** Square brackets `[(2*pi*mu)]` not recognized as grouping operators.

---

## Root Cause Analysis

### Current Grammar

**Expression grouping:**
```lark
?atom: NUMBER
     | ID
     | "(" expr ")"         -> paren_expr
     | function_call
```

**Issue:** Only `(...)` recognized for grouping, not `[...]`.

---

## Implementation Options

### Option A: Extend Grammar (RECOMMENDED)

**Approach:** Add square brackets as alternative grouping syntax.

**Grammar Change:**
```lark
?atom: NUMBER
     | ID
     | "(" expr ")"         -> paren_expr
     | "[" expr "]"         -> bracket_expr
     | function_call
```

**Parser Change:**
```python
def _handle_bracket_expr(self, node):
    """Handle square bracket grouping [expr]."""
    # Same as paren_expr - just return the inner expression
    return self._transform_expr(node.children[0])
```

**Pros:**
- Clean semantic representation
- Preserves bracket vs paren distinction (if needed)
- Minimal code change

**Cons:**
- None

**Effort:** 1-2h
- Grammar: 10 min
- Parser: 10 min
- Testing: 30 min
- Integration test: 30 min

---

### Option B: Preprocessor Normalization

**Approach:** Replace `[` with `(` and `]` with `)` before parsing.

**Implementation:**
```python
def normalize_square_brackets(source: str) -> str:
    """Replace square brackets with parentheses in expressions."""
    # Simple character replacement
    source = source.replace('[', '(')
    source = source.replace(']', ')')
    return source
```

**Pros:**
- Even simpler implementation
- No grammar changes

**Cons:**
- Loses distinction between brackets and parens
- May interfere with future features (if GAMS uses `[]` for other purposes)

**Effort:** 30 min

---

## Recommendation

**Option A: Extend Grammar** (1-2h)

**Rationale:**
1. **Semantically correct**: Preserves the distinction between `()` and `[]`
2. **Low complexity**: Very simple grammar addition
3. **Future-proof**: If GAMS adds `[]` for other purposes (e.g., indexing), we're ready
4. **Only 1 model affected**: Low urgency, but clean solution worth the small effort

**Implementation:**
1. Add `"[" expr "]" -> bracket_expr` to grammar (10 min)
2. Add handler in parser (returns inner expr) (10 min)
3. Unit tests with square brackets (30 min)
4. Test bearing.gms parsing (30 min)

---

## Testing Requirements

### Unit Tests

**Basic Square Bracket Grouping:**
```gams
Variable x;
Equation eq;
eq.. x =e= [1 + 2] * 3;
```
Expected: `x = (1 + 2) * 3 = 9`

**Nested Square Brackets:**
```gams
eq.. x =e= [[1 + 2] * 3];
```
Expected: `x = ((1 + 2) * 3) = 9`

**Mixed Brackets and Parens:**
```gams
eq.. x =e= (1 + [2 * 3]) * 4;
```
Expected: `x = (1 + (2 * 3)) * 4 = 28`

**bearing.gms Pattern:**
```gams
Equation friction;
Variable Ef, h, N, mu, r, r0;

friction.. Ef*h =e= sqr(2*pi*N/60)*[(2*pi*mu)]*(r**4 - r0**4)/4;
```

### Integration Tests

- bearing.gms: Should parse past line 144 after implementing square brackets

---

## Expected Impact

**Parse Rate Improvement:**
- Current: 5/18 (27%)
- After fix: 6/18 (33%)
- Improvement: +1 model (bearing.gms)

**Note:** bearing.gms may have additional blockers after line 144. This fix addresses the immediate blocker.

---

## References

- GAMS Documentation: Expression Syntax
- Failing model: `tests/fixtures/tier2_candidates/bearing.gms` (line 144)
- Grammar: `src/gams/gams_grammar.lark` (atom rule)
- Parser: `src/ir/parser.py` (expression handling)

---

## Alternative Interpretations

**Could `[]` mean something else in GAMS?**
- Checked GAMS docs: `[]` is purely alternative grouping syntax
- No array indexing syntax in GAMS (uses `()` for indexing)
- Safe to treat as equivalent to `()`
