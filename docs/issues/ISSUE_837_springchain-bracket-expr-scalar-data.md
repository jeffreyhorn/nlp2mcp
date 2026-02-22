# Springchain: Square Bracket Expression in Scalar Data Not Supported

**GitHub Issue:** [#837](https://github.com/jeffreyhorn/nlp2mcp/issues/837)
**Status:** PARTIALLY FIXED — Grammar extended but model still blocked by `$eval` macro expansion
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Affected Models:** springchain

---

## Problem Summary

The springchain model (`data/gamslib/raw/springchain.gms`) fails to parse because it uses
square bracket expressions in scalar data definitions, which the grammar does not support in
that context.

---

## Partial Fix Applied

**Grammar fix (completed):**
Extended `scalar_data_item` rule in `src/gams/gams_grammar.lark` to accept `"[" expr "]"`
bracket expressions in scalar data blocks. Updated parser in `src/ir/parser.py` to handle
bracket expressions by storing them as computed parameter assignments (expressions) rather
than trying to evaluate them to numeric constants at parse time.

**Remaining blocker: `$eval` macro expansion**

The springchain model uses `$eval` and `$set` compile-time directives:
```gams
$if not set N $set N 10
$eval NM1 %N%-1
Set n "spring index"  /n0*n%N%/;
```

The preprocessor currently **strips** `$set`/`$if not set` directives (turns them into comments)
rather than executing them. This means `%N%` and `%NM1%` are never expanded, causing parse
errors on lines that reference these macros.

The bracket expression `[2*sqrt(sqr(a_x-b_x) + sqr(a_y-b_y))/%N%]` also contains `%N%`
which would need expansion before the expression can be parsed.

---

## What Must Be Done Before Full Fix

1. **`$set` directive execution**: Instead of stripping `$set` directives, the preprocessor
   should evaluate them and store key-value pairs for `%macro%` expansion.
2. **`$eval` directive support**: Add `$eval` handling to the preprocessor — evaluate
   arithmetic expressions and store results for `%macro%` expansion.
3. **`%macro%` expansion**: Replace `%name%` tokens with their values throughout the source.

This is a significant preprocessor enhancement (~4-8h effort) that should be planned as a
dedicated sprint task.

---

## Files Modified

| File | Change |
|------|--------|
| `src/gams/gams_grammar.lark` | Added `"[" expr "]"` alternative to `scalar_data_item` |
| `src/ir/parser.py` | Handle bracket expr in scalar data — store as computed assignment |

---

## Classification

Lexer error catalog: Subcategory J (Bracket/Brace)
