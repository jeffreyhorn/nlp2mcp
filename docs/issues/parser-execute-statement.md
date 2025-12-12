# Parser: Execute Statement Not Supported

**GitHub Issue:** [#456](https://github.com/jeffreyhorn/nlp2mcp/issues/456)
**Status:** Open  
**Priority:** Low  
**Blocking Model:** inscribedsquare.gms (tier 2)

---

## Problem Summary

The GAMS parser does not support the `execute` statement. The `execute` statement is used to run external programs or shell commands from within a GAMS model. This is commonly used for post-processing, visualization, or integration with other tools.

---

## Reproduction

### Test Case

```gams
execute 'gnuplot input.txt';
execute 'rm tempfile.txt';
```

### Error Message

```
Error: Parse error at line 105, column 9: Unexpected character: '''
  execute 'gnuplot %gams.scrdir%gnuplot.in'
          ^

Suggestion: This character is not valid in this context
```

### Affected Model

**File:** `tests/fixtures/tier2_candidates/inscribedsquare.gms`  
**Lines:** 105-106

```gams
  execute 'gnuplot %gams.scrdir%gnuplot.in'
  execute 'rm %gams.scrdir%gnuplot.in'
```

The model uses `execute` statements to run gnuplot for visualization and to clean up temporary files.

---

## Technical Analysis

### GAMS Execute Statement Syntax

The `execute` statement has several forms:

1. **Basic execute:** `execute 'command';`
2. **Execute with return code:** `execute.checkaliashell 'command';`
3. **Execute with options:** `execute.async 'command';`

### Related Constructs

- `execute_load`: Load data from GDX files
- `execute_unload`: Save data to GDX files
- `execute_loadpoint`: Load solution point

### Root Cause

The grammar does not include a rule for the `execute` statement. Since `execute` runs external programs, it's not directly relevant to NLP model extraction, but it needs to be parsed (and skipped) to allow the model to load.

---

## Suggested Fix

Add `execute_stmt` rule to `src/gams/gams_grammar.lark`:

```lark
// Execute statement (Sprint 12 - mock/skip for external program execution)
// Syntax: execute 'command';
// We parse but don't process since external execution is not relevant for NLP model extraction
execute_stmt: "execute"i ("." ID)? STRING SEMI?
```

Note: The semicolon may be optional in some GAMS contexts (especially inside if blocks).

Also add to the `stmt` rule and `exec_stmt` rule for use inside if/loop blocks.

---

## Testing Requirements

1. **Unit test:** Verify execute statements parse correctly
2. **Integration test:** Verify `inscribedsquare.gms` parses completely after fix
3. **Edge cases:**
   - Basic: `execute 'command';`
   - With modifier: `execute.async 'command';`
   - Without semicolon (in if block context)
   - With compile-time variables: `execute '%gams.scrdir%script.sh';`

### Example Test Cases

```python
def test_execute_basic():
    code = "execute 'echo hello';"
    model = parse_model_text(code)
    assert model is not None

def test_execute_with_modifier():
    code = "execute.async 'long_running_script.sh';"
    model = parse_model_text(code)
    assert model is not None

def test_execute_in_if_block():
    code = '''
    Scalar x / 1 /;
    if(x > 0, execute 'script.sh');
    '''
    model = parse_model_text(code)
    assert model is not None
```

---

## Impact

- **Severity:** Low - The execute statement doesn't affect the mathematical model
- **Workaround:** Comment out or remove execute statements (model will still solve correctly)
- **Scope:** Any GAMS code using external program execution

---

## Related Issues

- Issue #447: put statement support (already implemented)
- The execute statement is often used alongside put statements for visualization pipelines

---

## GAMS Reference

From GAMS documentation:

> The execute statement allows calling external programs. The string argument is passed to the operating system's command processor.

Common uses:
- Running visualization tools (gnuplot, matplotlib scripts)
- Post-processing results with external programs
- File management (copy, move, delete)
- Integration with other modeling tools
