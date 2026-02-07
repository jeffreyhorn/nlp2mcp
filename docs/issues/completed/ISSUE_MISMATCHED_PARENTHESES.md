# Issue: Mismatched Parentheses Detection

**Status:** SUPERSEDED
**Category:** Parser Error Reporting  
**Affected Models:** camcge  
**Priority:** Low  
**GitHub Issue:** N/A

> **NOTE (February 5, 2026):** This issue was based on an incorrect diagnosis. The `camcge` model does NOT have a syntax error — it compiles successfully with GAMS (`gams action=c` returns exit code 0). The expression spans lines 212-213 with balanced parentheses across both lines. The actual issue is that nlp2mcp doesn't handle multi-line statement continuation. See **ISSUE_MULTILINE_CONTINUATION.md** and GitHub Issue #636 for the correct analysis.

## Summary

The model `camcge` has a syntax error with mismatched parentheses. The parser reports "Unexpected character: ';'" which is confusing. Better error detection would help users find the actual issue.

## Reproduction

**Model:** `data/gamslib/raw/camcge.gms`

**Source line 212:**
```gams
at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it));
```

**Error:**
```
Error: Parse error at line 212, column 63: Unexpected character: ';'
  at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it));
                                                                ^
```

## Root Cause Analysis

The line has mismatched parentheses:
- Opening: `(gamma(it)*e0(it)**rhot(it)` - 1 open
- Additional: `(1 - gamma(it)` - 1 open (total 2 unmatched)
- No closing parenthesis before semicolon

This is actually a **bug in the source model**, not a parser limitation. However, the error message could be improved to suggest parenthesis mismatch.

**Correct line should be:**
```gams
at(it) = xd0(it)/(gamma(it)*e0(it)**rhot(it) + (1 - gamma(it)));
```

## Expected Behavior

When parentheses are mismatched, the parser should provide a more helpful error message like:
```
Error: Mismatched parentheses - 2 unclosed '(' before ';'
```

## Proposed Fix

This is an error reporting improvement, not a grammar fix:

1. In the parse error handler, when "Unexpected ';'" is encountered, count parentheses balance
2. If unbalanced, add a suggestion about mismatched parentheses

```python
if unexpected_char == ';':
    open_parens = line[:col].count('(') - line[:col].count(')')
    if open_parens > 0:
        suggestion = f"Check for {open_parens} unclosed parenthesis(es)"
```

## Test Case

Not applicable - this is a source model bug, not a parser feature request.

## Related Files

- `src/ir/parser.py`: Error message generation in `parse_text()`
- `data/gamslib/raw/camcge.gms`: Line 212 (contains source bug)

## Notes

This model has a genuine syntax error that needs to be fixed in the source. The issue is about improving error messages to help diagnose such problems.
