# Saras: Parse Error from Orphan `]` After `$offText` Stripping

**GitHub Issue:** [#836](https://github.com/jeffreyhorn/nlp2mcp/issues/836)
**Status:** RESOLVED
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Resolved:** 2026-02-22
**Affected Models:** saras

---

## Problem Summary

The saras model (`data/gamslib/raw/saras.gms`) fails to parse because the preprocessor's
`$offText` stripping leaves a `[Stripped: $offText]` marker. The trailing `]` bracket is
interpreted as syntax by the parser, causing a lexer error.

---

## Fix Applied

Removed square brackets from all stripping marker comments across the entire preprocessor.
Changed format from `* [Stripped: ...]` to `* Stripped: ...` and `* [EchoContent: ...]` to
`* EchoContent: ...`.

Locations fixed in `src/ir/preprocessor.py`:
- `strip_unsupported_directives()`: $onEchoV/$offEcho, $onEps/$offEps, $onText/$offText,
  $title, $eolCom markers
- `preprocess_includes()`: $batInclude file not found marker
- `strip_conditional_sets()`: $if not set markers
- `strip_set_directives()`: $set markers
- `strip_macro_directives()`: $macro markers
- `_strip_remaining_includes()`: $include markers

Updated all corresponding test assertions in:
- `tests/unit/ir/test_preprocessor.py`
- `tests/unit/test_dollar_set_directives.py`
- `tests/unit/test_dollar_macro.py`

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/preprocessor.py` | Removed brackets from all stripping markers |
| `tests/unit/ir/test_preprocessor.py` | Updated assertions to match new format |
| `tests/unit/test_dollar_set_directives.py` | Updated assertions to match new format |
| `tests/unit/test_dollar_macro.py` | Updated assertions to match new format |
