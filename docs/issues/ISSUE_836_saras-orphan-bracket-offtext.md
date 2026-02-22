# Saras: Parse Error from Orphan `]` After `$offText` Stripping

**GitHub Issue:** [#836](https://github.com/jeffreyhorn/nlp2mcp/issues/836)
**Status:** OPEN — Preprocessor stripping marker leaves orphan bracket
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Affected Models:** saras

---

## Problem Summary

The saras model (`data/gamslib/raw/saras.gms`) fails to parse because the preprocessor's
`$offText` stripping leaves a `[Stripped: $offText]` marker. The trailing `]` bracket is
interpreted as syntax by the parser, causing a lexer error.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/saras.gms

# Error: Parse error at line 1631, column 22: Unexpected character: ']'
#   * [Stripped: $offText]
#                        ^
```

---

## Root Cause

The `strip_unsupported_directives()` function in `src/ir/preprocessor.py` handles
`$onText`/`$offText` blocks by replacing their content with comment lines. However, the
stripping markers use square brackets (`[Stripped: $offText]`), and the trailing `]` is
not inside a comment prefix, so the lexer/parser encounters it as unexpected syntax.

The stripping format:
```
* [Stripped: $offText]
```

While the `*` at the start makes this a GAMS comment line, the issue arises when the
marker format is slightly different or the `*` is missing.

---

## Suggested Fix

**Option A (preferred):** Change the stripping marker format to avoid brackets entirely:

```python
# Instead of:  "* [Stripped: $offText]"
# Use:         "* Stripped: $offText"
```

**Option B:** Ensure all stripping markers are proper GAMS comment lines (prefixed with `*`
in column 1).

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/preprocessor.py` | `strip_unsupported_directives()` — marker format |
| `data/gamslib/raw/saras.gms` | Original model with `$onText`/`$offText` blocks |

---

## Classification

Lexer error catalog: Subcategory J (Bracket/Brace)

---

## Estimated Effort

~30min — preprocessor fix to handle the stripping marker format
