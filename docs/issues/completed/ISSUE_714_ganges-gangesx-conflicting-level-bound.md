# Parser: Conflicting Level Bound Error on Repeated .l Assignments (ganges, gangesx)

**GitHub Issue:** [#714](https://github.com/jeffreyhorn/nlp2mcp/issues/714)
**Status:** Fixed
**Severity:** Medium — Blocks parsing of models that use multiple conditional .l assignments
**Discovered:** 2026-02-13 (Sprint 19, after Issues #710 fix advanced ganges/gangesx past model_ref_list)
**Fixed:** 2026-02-13 (Sprint 19)
**Affected Models:** ganges (line 704), gangesx (line 887)

---

## Problem Summary

The parser raises a `ParserSemanticError: Conflicting level bound` when a variable's `.l` (level) attribute is assigned multiple times with different conditions. GAMS allows this — later assignments overwrite earlier ones, and conditional assignments only apply to matching elements. The parser is too strict and rejects valid GAMS code.

---

## Root Cause

The GAMS source uses multiple conditional assignments to the same variable's `.l` attribute:

```gams
tw.l(sa) = 0;                       -- line 703 (ganges)
tw.l(i)$(not sa(i)) = 0.045;        -- line 704 (ganges)
```

The `_set_bound_value` method in `src/ir/parser.py` detected that `tw.l('agricult')` already had a value and raised a "Conflicting level bound" error. In GAMS, multiple assignments to the same bound attribute are valid with last-write-wins semantics.

---

## Fix

Three changes in `src/ir/parser.py`:

1. **`_set_bound_value` (line ~4665):** Removed the conflicting value check. Both keyed (indexed) and scalar bound assignments now silently overwrite previous values, matching GAMS last-write-wins semantics. Removed unused `label_map` and `index_hint` variables that were only used by the deleted error message.

2. **`_handle_model_with_list` (line ~2732):** Fixed a follow-up bug exposed once ganges parsed past the level bound error. The method assumed `node.children[1]` was the `model_ref_list` Tree, but ganges has a STRING description token between the model name and the ref list (`Model track 'ganges with tracking option' /infalloc, wdet, .../`). Changed to dynamically find the `model_ref_list` Tree child using `next(c for c in node.children if isinstance(c, Tree) and c.data == "model_ref_list")`.

Updated tests:
- `tests/unit/gams/test_parser.py`: Renamed `test_conflicting_bounds_raise_error` to `test_repeated_bounds_last_write_wins` — now verifies last value is stored instead of expecting an error.
- `tests/edge_cases/test_edge_cases.py`: Updated `test_duplicate_bounds` to verify last-write-wins semantics (lo=1, up=5) instead of expecting `ParserSemanticError`.

---

## Verification

- ganges: Parses successfully. `declared_model=ganges`, 67 model equations.
- gangesx: Parses successfully. `declared_model=ganges`, 67 model equations.
- Both models now advance to a circular dependency detection stage (separate issue, not related to #714).
- Quality gate: 3312 tests pass, typecheck/lint/format all clean.
