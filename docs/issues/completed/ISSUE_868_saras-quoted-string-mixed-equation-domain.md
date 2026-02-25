# Saras: Quoted String in Mixed Equation Domain Rejected as Unknown Set

**GitHub Issue:** [#868](https://github.com/jeffreyhorn/nlp2mcp/issues/868)
**Status:** FIXED
**Severity:** Medium — Model fails to parse (blocks translate/solve)
**Date:** 2026-02-24
**Fixed:** 2026-02-25
**Affected Models:** saras

---

## Problem Summary

The saras model fails during IR building because equation definitions use mixed domains
containing both set references and quoted string literals (e.g., `Rcon1(r,"aland")..`).
The parser only handles the case where ALL domain elements are quoted strings (Issue #774),
not the mixed case where some are sets and some are literal element selectors.

---

## Fix Applied

Three changes to `src/ir/parser.py`:

1. **`_handle_eqn_def_domain()`**: Changed from `all(...)` check to `any(...)`. When any
   domain token is a quoted string literal, filter those out before calling `_ensure_sets()`.
   Only non-literal domain elements are validated as sets. The stored equation domain uses
   the filtered (sets-only) list.

2. **`_make_symbol()` variable index validation**: Added `len(expected) > 0` guard so that
   variables declared without a domain (like `cx` in saras) can still be used with indices.
   This matches the existing behavior for parameters.

3. **`_apply_variable_bound()`**: Added early return when a domain-less variable receives
   indexed bounds, preventing the "scalar variable with indexed bounds" error.

**Result:** saras parses successfully — 40 equations, 21 variables.

---

## Files Changed

| File | Change |
|------|--------|
| `src/ir/parser.py` | `_handle_eqn_def_domain()`: mixed quoted/set domain filtering |
| `src/ir/parser.py` | `_make_symbol()`: domain-less variable index guard |
| `src/ir/parser.py` | `_apply_variable_bound()`: domain-less variable indexed bounds |

---

## Related Issues

- **Issue #774**: Original fix for all-literal equation domains (singleton instantiation)
- **Issue #857** (completed): Previous saras blocker (attribute access validation)
- **Issue #840** (completed): Earlier saras blocker (`%system.nlp%` macro)
