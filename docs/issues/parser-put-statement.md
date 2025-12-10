# Parser: Put Statement Not Supported

**GitHub Issue:** [#447](https://github.com/jeffreyhorn/nlp2mcp/issues/447)
**Status:** Open  
**Priority:** Medium  
**Blocking Model:** inscribedsquare.gms (tier 2)

---

## Problem Summary

The GAMS parser does not support `put` statements. The `put` statement is used for writing output to files in GAMS, and is commonly used for generating reports, data exports, and interoperability with other programs (like gnuplot).

---

## Reproduction

### Test Case

```gams
file f / 'output.txt' /;
put f;
put 'Hello World' /;
```

### Error Message

```
Error: Parse error at line 91, column 5: Unexpected character: 'f'
  put f;
      ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/inscribedsquare.gms`  
**Lines:** 91-100

```gams
file f / '%gams.scrdir%gnuplot.in' /;
if( %gnuplot% and
 (m.modelstat = %modelStat.optimal% or
  m.modelstat = %modelStat.locallyOptimal% or
  m.modelstat = %modelStat.feasibleSolution%),
  f.nd=6;
  f.nw=0;
  put f;
  put 'set size ratio -1' /;
  put 'set samples 1000' /;
  ...
);
```

The model uses `put` statements to generate a gnuplot input file for visualization.

---

## Technical Analysis

### GAMS Put Statement Syntax

The `put` statement has several forms:

1. **Set current file:** `put f;` (where `f` is a file handle)
2. **Write literal:** `put 'text' /;` (slash means newline)
3. **Write expression:** `put x.l;` (write variable level value)
4. **Write multiple items:** `put 'x = ' x.l /;`
5. **Format control:** `put x.l:10:4;` (width:decimals)
6. **Cursor positioning:** `put @col #row 'text';`

### Related Constructs

- `file` declaration: Declares a file handle (already supported per Issue #434)
- `putclose`: Close the file after writing
- `put_utility`: Advanced file operations

### Root Cause

The grammar does not include rules for `put` statements. This is a significant omission since `put` is a core GAMS I/O feature.

---

## Suggested Fix

Add `put_stmt` rules to `src/gams/gams_grammar.lark`:

```lark
put_stmt: "put"i put_item* SEMI
        | "put"i put_item* "/" SEMI           -> put_stmt_newline

put_item: ID                                   -> put_file
        | STRING                               -> put_string
        | expr                                 -> put_expr
        | expr ":" NUMBER                      -> put_formatted
        | expr ":" NUMBER ":" NUMBER           -> put_formatted_full
        | "@" expr                             -> put_column
        | "#" expr                             -> put_row
        | "/"                                  -> put_newline

putclose_stmt: "putclose"i ID? SEMI
```

Note: The `put` statement syntax is complex due to:
- Multiple items per statement
- Inline format specifications
- Cursor positioning
- The `/` newline character can appear mid-statement or at end

---

## Testing Requirements

1. **Unit test:** Verify basic `put` statements parse correctly
2. **Integration test:** Verify `inscribedsquare.gms` parses completely after fix
3. **Edge cases:**
   - File selection: `put f;`
   - Simple string: `put 'text';`
   - With newline: `put 'text' /;`
   - Expression: `put x.l;`
   - Multiple items: `put 'x = ' x.l ' y = ' y.l /;`
   - Formatted: `put x.l:10:4;`
   - Cursor control: `put @10 'text';`

### Example Test Cases

```python
def test_put_file_selection():
    code = "file f / 'test.txt' /; put f;"
    tree = parse_text(code)
    assert tree is not None

def test_put_string():
    code = "file f / 'test.txt' /; put f; put 'Hello World' /;"
    tree = parse_text(code)
    assert tree is not None

def test_put_expression():
    code = "Scalar x / 5 /; file f / 'test.txt' /; put f; put x /;"
    tree = parse_text(code)
    assert tree is not None

def test_put_multiple_items():
    code = "Scalar x / 5 /; file f / 'test.txt' /; put f; put 'x = ' x /;"
    tree = parse_text(code)
    assert tree is not None
```

---

## Impact

- **Severity:** Medium - Blocks one tier 2 model
- **Workaround:** Remove or comment out `put` statements (loses file output functionality but model may still solve)
- **Scope:** Any GAMS code using file output operations

---

## Related Issues

- Issue #434 (parser-file-statement.md): `file` declaration support (already implemented)
- May need `putclose` statement support as well
- Consider `display` statement (different but related output mechanism)

---

## GAMS Reference

From GAMS documentation, the `put` writing facility provides:

1. **File handling:** Define files with `file` statement, select with `put filename;`
2. **Output items:** Strings, expressions, variable/equation attributes
3. **Formatting:** Field width, decimal places, alignment
4. **Cursor control:** Position cursor with `@col` and `#row`
5. **Newlines:** Use `/` for carriage return

The `put` facility is essential for:
- Custom report generation
- Data export to other formats
- Integration with external tools (gnuplot, visualization)
- Logging and debugging output
