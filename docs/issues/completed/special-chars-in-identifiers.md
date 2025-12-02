# Issue: Special Characters in Identifiers

**GitHub Issue:** [#357](https://github.com/jeffreyhorn/nlp2mcp/issues/357)  
**Status:** Open (Reverted)  
**Priority:** LOW  
**Complexity:** MEDIUM (1.5h simple, 4-5h robust)  
**Impact:** 1 Tier 2 model (chenery)  
**Trade-off:** Breaks 3 Tier 1 models  
**Sprint:** Sprint 13+ (Low priority)

---

## Problem Description

GAMS allows hyphens `-` and plus signs `+` within identifiers (e.g., `light-ind`, `food+agr`). Our lexer currently treats `-` and `+` as arithmetic operators, causing parse failures when these characters appear in identifiers.

---

## Example

### chenery.gms (line 17)

**GAMS Syntax:**
```gams
Set i 'sectors' / light-ind, food+agr, heavy-ind, services /;
```

**Error:**
```
Error: Parse error at line 17, column 37: Unexpected character: '-'
  i 'sectors' / light-ind, food+agr, heavy-ind, services /
                                      ^
```

---

## Day 4 Implementation and Reversion

### Attempted Fix (Day 4)

**Grammar Change:**
```lark
ID: /[a-zA-Z_][a-zA-Z0-9_\-+]*/  // Allow - and + in identifiers
```

**Result:** Successfully parsed chenery.gms

---

### Reversion Reason

**Breaking Impact:** Caused arithmetic parsing failures in 3 Tier 1 models:
- hs62.gms
- mhw4d.gms  
- mhw4dx.gms

**Example Failure (hs62.gms):**
```gams
Variable x1;
Equation eq;
eq.. x1-1 =e= 0;  // Should parse as: x1 - 1 (subtraction)
                  // Parsed as: identifier "x1-1"
```

**Trade-off Decision:** Breaking 3 working models to fix 1 model is not acceptable. Reverted the change.

---

## Root Cause: Whitespace Sensitivity

GAMS uses **whitespace-sensitive lexing** to distinguish:
- `x1-1` → identifier `x1-1` (no spaces)
- `x1 - 1` → `x1` minus `1` (spaces around operator)
- `x1- 1` → `x1` minus `1` (space after operator)
- `x1 -1` → `x1` minus `1` (space before operator)

**Challenge:** Lark's lexer is not context-aware by default. We need a way to detect whitespace around `-` and `+` to make the correct tokenization decision.

---

## Proposed Solutions

### Option A: Quoted Identifiers (RECOMMENDED)

**Approach:** Users wrap special-character identifiers in quotes.

**GAMS Syntax:**
```gams
Set i 'sectors' / 'light-ind', 'food+agr', 'heavy-ind', services /;
```

**Pros:**
- No parser changes needed
- Already supported by grammar (`STRING` → `set_element`)
- No ambiguity with operators
- GAMS standard syntax for special identifiers

**Cons:**
- Requires user to modify source files
- Manual workaround

**Effort:** 0h (documentation only)

**Recommendation:** Document this as the preferred solution. Add to README/troubleshooting guide.

---

### Option B: Whitespace-Aware Lexer

**Approach:** Implement custom lexer callback to check for whitespace around `-` and `+`.

**Algorithm:**
```python
class WhitespaceAwareLexer(Lark):
    def lex(self, text):
        tokens = super().lex(text)
        for i, tok in enumerate(tokens):
            if tok.type == "ID" and ('-' in tok.value or '+' in tok.value):
                # Check if previous character (before ID) is whitespace
                # Check if next character (after ID) is whitespace
                # If both sides have whitespace → split into ID + OP + ID
                # If no whitespace → keep as single ID
                ...
```

**Pros:**
- Handles both special identifiers and arithmetic correctly
- No user-facing changes needed

**Cons:**
- Complex implementation (Lark callback mechanisms)
- Fragile (edge cases: beginning of line, after comma, etc.)
- Performance overhead (post-processing all tokens)

**Effort:** 4-5h (implementation + extensive testing)

---

### Option C: Preprocessor Normalization

**Approach:** Preprocess source to quote special identifiers.

**Algorithm:**
```python
def normalize_special_identifiers(source: str) -> str:
    """
    Within / ... / blocks (set/parameter data):
    - Detect identifiers with - or + (no surrounding whitespace)
    - Wrap in single quotes if not already quoted
    """
    # Regex: \b([a-zA-Z_][a-zA-Z0-9_]*[-+][a-zA-Z0-9_\-+]*)\b
    # Replace with: '\1'
    ...
```

**Pros:**
- Clean separation (preprocessing vs parsing)
- Preserves existing lexer/grammar

**Cons:**
- Must distinguish identifiers from arithmetic (same whitespace issue)
- May quote too aggressively (false positives)
- Preprocessing complexity

**Effort:** 3-4h

---

## Recommendation

**Option A: Quoted Identifiers** (documentation-only solution)

**Rationale:**
1. **Zero implementation effort** - already supported by grammar
2. **No trade-offs** - doesn't break existing models
3. **GAMS standard** - quoted identifiers are valid GAMS syntax
4. **Low impact** - only 1 model affected (chenery.gms)

**Implementation:**
1. Add troubleshooting section to README:
   ```markdown
   ### Special Characters in Identifiers
   
   If your model uses identifiers with hyphens or plus signs (e.g., `light-ind`, `food+agr`),
   wrap them in quotes:
   
   ```gams
   Set i / 'light-ind', 'food+agr', 'heavy-ind' /;
   ```
   ```

2. Update chenery.gms in test fixtures (optional):
   - Create chenery_quoted.gms variant with quoted identifiers
   - Use as test case for quoted identifier support

**If users demand native support:**
- Revisit Option B (whitespace-aware lexer) in Sprint 14+
- Requires significant effort (4-5h) for 1 model
- Low priority compared to other blockers

---

## Affected Models

| Model | Lines | Error Location | Alternative | Status |
|-------|-------|----------------|-------------|--------|
| chenery | 172 | line 17, col 37 | Use quoted identifiers | Workaround available |

**Parse Rate Impact:** +10% Tier 2 (2/10 → 3/10) if implemented

**Trade-off:** -30% Tier 1 (10/10 → 7/10) if naive implementation used

**Net Impact:** -20% overall (not acceptable)

---

## Testing Requirements (if Option B/C chosen)

### Regression Tests
Ensure these still parse correctly:
```gams
x1-1        // Arithmetic: x1 minus 1
x1 - 1      // Arithmetic: x1 minus 1  
x1- 1       // Arithmetic: x1 minus 1
x1 -1       // Arithmetic: x1 minus 1 (negative number)
```

### Special Identifier Tests
```gams
Set i / light-ind, food+agr /;    // Identifiers with - and +
Set i / x1-x2 /;                  // Identifier (not x1 minus x2)
```

### Edge Cases
```gams
Set i / a-b-c, x+y+z /;           // Multiple special chars
Set i / -inf, +inf /;             // Leading sign (predefined constants)
```

---

## Decision History

- **Day 4:** Implemented naive fix (allow - and + in ID tokens)
- **Day 4:** Discovered breaking impact on hs62, mhw4d, mhw4dx
- **Day 4:** REVERTED change (fc1a2d6)
- **Day 6:** Documented as low-priority issue with quoted identifier workaround

---

## References

- Failing model: `tests/fixtures/tier2_candidates/chenery.gms` (line 17)
- Day 4 commit (reverted): fc1a2d6
- Grammar: `src/gams/gams_grammar.lark` (ID token definition)
- Tier 1 regressions: hs62.gms, mhw4d.gms, mhw4dx.gms
- GAMS Documentation: Quoted identifiers
