# nonsharp: `abort.noerror` with double-quoted string

**GitHub Issue:** [#891](https://github.com/jeffreyhorn/nlp2mcp/issues/891)
**Model:** nonsharp (GAMSlib SEQ=233, "Synthesis of General Distillation Sequences")
**Error category:** `lexer_invalid_char`
**Error message:** `Unexpected character: '"'` at line 442, column 37
**Status:** RESOLVED

## Description

The lexer fails on `abort.noerror$(not relax.marginals) "solver did not provide marginals, cannot continue"`. Two issues: (1) `abort.noerror` is a GAMS `abort` suffix form, and (2) the error message uses double quotes `"..."` instead of single quotes.

## Resolution

Fixed by adding `abort.noerror` → `abort` normalization in the preprocessor pipeline
(`src/ir/preprocessor.py`, step 10b). Since abort is already mock/skipped by the parser,
stripping the `.noerror` suffix is semantically neutral.

The double-quoted string issue turned out to be a non-issue: the grammar's `STRING` terminal
already supports double quotes (`/"[^"]*"|'[^']*'/`). The actual error was caused by
`abort.noerror` not being recognized as a valid abort variant, causing the parser to fail
before reaching the string.

After the fix, nonsharp parses successfully (15 variables, 18 equations).

## Files Modified

| File | Changes |
|------|---------|
| `src/ir/preprocessor.py` | Added `re.sub(r"\babort\.noerror\b", "abort", ...)` normalization |
