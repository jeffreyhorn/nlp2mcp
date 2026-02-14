# Grammar: Model Equation List Allows Whitespace Separation (No Commas Between Lines)

**GitHub Issue:** [#710](https://github.com/jeffreyhorn/nlp2mcp/issues/710)

**Issue:** The `model_ref_list` grammar rule requires commas between all equation names, but GAMS allows whitespace (including newlines) as separators in model equation lists. Multi-line lists without trailing commas at line ends fail to parse.

**Status:** Completed
**Severity:** Medium — Affects models with large equation lists spanning multiple lines
**Discovered:** 2026-02-13 (Sprint 19, after Issues #704/#705 fixes advanced ganges/gangesx past their original errors)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** ganges (confirmed, line 1082), gangesx (confirmed, line 1368)

---

## Problem Summary

GAMS model statements list equation names inside `/ ... /` delimiters. These lists can use commas, whitespace, or both as separators. Our grammar required commas:

```lark
model_ref_list: ID ("," ID)*
```

But GAMS source files commonly use multi-line lists where the last identifier on a line is NOT followed by a comma, relying on newline + whitespace to separate from the next line's identifiers.

---

## Fix Applied

Changed the `model_ref_list` rule in `src/gams/gams_grammar.lark` to make commas optional:

```lark
model_ref_list: ID (","? ID)*
```

The parser handler (`_handle_model_multi` in `src/ir/parser.py`) already filters children by `tok.type == "ID"`, so it correctly ignores comma tokens and required no changes.

**Verification:**
- ganges and gangesx both parse past the model statement (lines 1082 and 1368 respectively)
- Both models now hit a different, unrelated error (conflicting level bound semantic error at earlier lines during IR building), confirming the model_ref_list grammar fix resolved the original issue

**Quality gate:** All 3299 tests pass. Typecheck, lint, and format all clean.
