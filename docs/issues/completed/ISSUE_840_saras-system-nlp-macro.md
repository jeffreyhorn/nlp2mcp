# Saras: `%system.nlp%` System Macro Not Expanded

**GitHub Issue:** [#840](https://github.com/jeffreyhorn/nlp2mcp/issues/840)
**Status:** FIXED (Sprint 21 Day 2, PR #865)
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Fixed:** 2026-02-24
**Affected Models:** saras

---

## Problem Summary

The saras model (`data/gamslib/raw/saras.gms`) fails to parse because it uses the GAMS
built-in system macro `%system.nlp%` on line 1488 of the raw file. The preprocessor does
not expand `%system.*%` macros, so the `%` character reaches the lexer and causes a parse
error.

---

## Error Details

```
ParseError: Error: Parse error at line 1439, column 14: Unexpected character: '%'
  option nlp = %system.nlp%;
               ^

Suggestion: This character is not valid in this context
```

The offending line in the raw file (line 1488):
```gams
option nlp = %system.nlp%;
```

This line restores the default NLP solver after temporarily switching to CONOPT. In GAMS,
`%system.nlp%` is a built-in compile-time macro that expands to the name of the currently
active NLP solver (e.g., `CONOPT`, `IPOPT`, `MINOS`).

---

## Reproduction Steps

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_file
ir = parse_file('data/gamslib/raw/saras.gms')
"
```

---

## Root Cause

The preprocessor (`src/ir/preprocessor.py`) does not handle `%system.*%` macros. The
`strip_unsupported_directives()` and `normalize_special_identifiers()` functions process
various compile-time directives but have no support for `%macro%` expansion of any kind.

GAMS system macros include:
- `%system.nlp%` — current NLP solver
- `%system.lp%` — current LP solver
- `%system.mip%` — current MIP solver
- `%system.fp%` — file path
- And many others

---

## Suggested Fix

**Approach: Expand `%system.*%` macros with reasonable defaults**

1. In `src/ir/preprocessor.py`, add a new step (or extend an existing one) that scans
   each line for `%system.<name>%` patterns and replaces them with default values.

2. A mapping of common system macros to default values:
   ```python
   SYSTEM_MACROS = {
       "system.nlp": "CONOPT",
       "system.lp": "CPLEX",
       "system.mip": "CPLEX",
   }
   ```

3. Use `re.sub(r'%system\.(\w+)%', replacement_fn, line, flags=re.IGNORECASE)` to
   expand them during preprocessing.

4. For unknown `%system.*%` macros, either strip the entire statement or emit a warning
   comment.

**Effort estimate:** ~1-2h

**Note:** This is a simpler variant of the full `%macro%` expansion needed for user-defined
macros (`$set`, `$eval`). System macros have fixed/default values and don't require the
expression evaluation infrastructure that `$eval` demands.

---

## Files That Need Changes

| File | Change |
|------|--------|
| `src/ir/preprocessor.py` | Add `%system.*%` macro expansion step |

---

## Related Issues

- Issue #837 (springchain) — also blocked by macro expansion (`$set`/`$eval`/`%N%`/`%NM1%`)
- Both issues share the broader need for `%macro%` expansion in the preprocessor
