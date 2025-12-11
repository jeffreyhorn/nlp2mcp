# Parser: Option Statement Colon Syntax Not Supported

**GitHub Issue:** [#446](https://github.com/jeffreyhorn/nlp2mcp/issues/446)
**Status:** Completed  
**Priority:** Medium  
**Blocking Model:** gastrans.gms (tier 2) - now progresses to line 134

---

## Problem Summary

The GAMS parser does not support the colon-separated format specification syntax in `option` statements. GAMS allows options like `option arep:6:3:1;` to control display formatting, but the parser fails when encountering the colon characters.

---

## Reproduction

### Test Case

```gams
Parameter arep(i,j);
option arep:6:3:1;
```

### Error Message

```
Error: Parse error at line 117, column 13: Unexpected character: ':'
  option  arep:6:3:1;
              ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/gastrans.gms`  
**Line:** 117

```gams
option  arep:6:3:1;
```

---

## Technical Analysis

### GAMS Option Syntax

The GAMS `option` statement supports multiple formats:

1. **Simple assignment:** `option optname = value;`
2. **Display format:** `option identifier:decimals;`
3. **Extended format:** `option identifier:decimals:rowlabels:columnlabels;`

The colon-separated format controls how parameters/variables are displayed:
- First number: decimal places
- Second number: row label width
- Third number: column label width

### Current Grammar

The current grammar likely only supports the simple assignment form of `option` statements and does not handle the colon-separated format specification.

### Root Cause

The option statement grammar rule does not include a pattern for `IDENTIFIER COLON NUMBER (COLON NUMBER)*` syntax.

---

## Suggested Fix

Extend the `option_stmt` rule in `src/gams/gams_grammar.lark` to support colon-separated format:

```lark
option_stmt: "option"i option_item ("," option_item)* SEMI

option_item: ID "=" expr                           -> option_assign
           | ID ":" NUMBER (":" NUMBER)*           -> option_format
           | ID ":" ID (":" ID)*                   -> option_format_id
```

Alternatively, a more specific rule:

```lark
option_format: ID ":" NUMBER                       -> option_decimals
             | ID ":" NUMBER ":" NUMBER            -> option_row_format  
             | ID ":" NUMBER ":" NUMBER ":" NUMBER -> option_full_format
```

---

## Testing Requirements

1. **Unit test:** Verify option format syntax parses correctly
2. **Integration test:** Verify `gastrans.gms` parses completely after fix
3. **Edge cases:**
   - Single colon: `option x:6;`
   - Two colons: `option x:6:3;`
   - Three colons: `option x:6:3:1;`
   - Combined with other options: `option x:6, limrow=0;`

### Example Test Cases

```python
def test_option_format_decimals():
    code = "Parameter x; option x:6;"
    tree = parse_text(code)
    assert tree is not None

def test_option_format_row():
    code = "Parameter x(i); option x:6:3;"
    tree = parse_text(code)
    assert tree is not None

def test_option_format_full():
    code = "Parameter arep(i,j); option arep:6:3:1;"
    tree = parse_text(code)
    assert tree is not None
```

---

## Impact

- **Severity:** Medium - Blocks one tier 2 model
- **Workaround:** Remove or comment out the option statement (may affect output formatting but not model semantics)
- **Scope:** Any GAMS code using colon format in option statements

---

## Related Issues

- May need to audit other `option` statement variations
- GAMS has many option types with different syntax patterns

---

## GAMS Reference

From GAMS documentation, the `option` statement with colon syntax controls the display format:

```
option identifier:d           Display d decimals
option identifier:d:r         Display d decimals, r characters for row labels
option identifier:d:r:c       Display d decimals, r for rows, c for columns
```

This is commonly used before `display` statements to control output formatting in listing files.
