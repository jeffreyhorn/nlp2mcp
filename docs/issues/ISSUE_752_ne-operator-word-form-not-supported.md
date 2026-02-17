# Word-Form Comparison Operator `ne` Not Supported in Grammar

**GitHub Issue:** [#752](https://github.com/jeffreyhorn/nlp2mcp/issues/752)
**Status:** Open
**Severity:** Medium - Blocks 1 GAMSLib model (ferts)
**Date:** 2026-02-13

---

## Problem Summary

The GAMS grammar supports symbolic comparison operators (`<>`, `<=`, `>=`, `<`, `>`) but not their word-form equivalents (`ne`, `le`, `ge`, `lt`, `gt`, `eq`). The ferts model uses `ne` (not-equal) in a dollar-conditional expression, causing a lexer error.

---

## Affected Model

### ferts.gms

**Error:**
```
Error: Parse error at line 306, column 63: Unexpected character: 'n'
  ppos(p,i) = yes$(sum(m$(not mpos(m,i)), b(m,p) ne 0) eq 0);
                                                        ^
```

**Source (lines 305-306):**
```gams
mpos(m,i)                = yes$k(m,i);
ppos(p,i)                = yes$(sum(m$(not mpos(m,i)), b(m,p) ne 0) eq 0);
```

The expression uses both `ne` (not-equal) and `eq` (equal) as word-form comparison operators. The grammar only defines the symbolic forms: `NE: "<>"` and `ASSIGN: "="` (which also serves as equality comparison in GAMS).

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ferts.gms --diagnostics
```

Reports: `Parse error at line 306, column 63: Unexpected character: 'n'`

---

## Root Cause

**File:** `src/gams/gams_grammar.lark`, line 614

The grammar defines comparison operators only in symbolic form:

```lark
comp_op: ASSIGN | LE | GE | LT | GT | NE
```

With terminal definitions (lines 715-719):
```lark
LE: "<="
GE: ">="
NE: "<>"
LT: "<"
GT: ">"
```

GAMS supports both symbolic and word-form comparison operators:

| Symbolic | Word Form | Meaning |
|----------|-----------|---------|
| `<>` | `ne` | Not equal |
| `<=` | `le` | Less than or equal |
| `>=` | `ge` | Greater than or equal |
| `<` | `lt` | Less than |
| `>` | `gt` | Greater than |
| `=` | `eq` | Equal |

The word forms are case-insensitive in GAMS (`NE`, `Ne`, `ne` are all valid).

---

## Suggested Fix

### Grammar Changes

**File:** `src/gams/gams_grammar.lark`

Add word-form terminals alongside existing symbolic ones:

```lark
NE: "<>" | /ne/i
LE: "<=" | /le/i
GE: ">=" | /ge/i
LT: "<" | /lt/i
GT: ">" | /gt/i
```

For `eq`, GAMS uses `=` for both assignment and equality comparison. The word form `eq` only appears in expression contexts (conditionals, dollar conditions). This requires careful handling to avoid conflicts with other uses of `eq` in GAMS (e.g., `=e=` equation type):

```lark
ASSIGN: "=" | /eq/i
```

**Caution:** Adding `/eq/i` to ASSIGN may conflict with equation types like `=e=` or with the `eq` that appears in equation definitions. A safer approach may be to add a separate `EQ_WORD` terminal and include it in `comp_op`:

```lark
comp_op: ASSIGN | LE | GE | LT | GT | NE | EQ_WORD
EQ_WORD: /eq/i
```

### Parser Changes

No parser changes needed if the word-form tokens map to the same terminal names. The parser already handles `NE`, `LE`, etc. in comparison expressions.

### Potential Conflicts

The word forms `ne`, `le`, `ge`, `lt`, `gt`, `eq` must not conflict with:
- Set element names (e.g., a set containing element `"ne"`)
- Parameter names
- Other GAMS keywords

In GAMS, these word-form operators are context-sensitive — they are only recognized as operators in expression contexts. The Lark grammar may need priority rules or contextual lexing to handle this correctly. If full contextual lexing is too complex, a simpler approach is to only add the word forms that are actually needed by models in the corpus.

---

## Scope Assessment

A search of GAMSLib models may reveal how commonly word-form operators are used. If only `ne` and `eq` are needed (as in ferts), the fix can be scoped narrowly.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/gams/gams_grammar.lark` | Add word-form comparison operator terminals |
| `tests/unit/test_word_form_operators.py` | New: tests for `ne`, `eq`, `lt`, `gt`, `le`, `ge` in expressions |

---

## Testing

```gams
* Minimal reproduction
Set i / a, b /;
Parameter x(i) / a 1, b 0 /;
Parameter y(i);
y(i) = 1$(x(i) ne 0);
display y;
```

Expected: `y('a') = 1`, `y('b') = 0`.
