# imsl parse failure: _process_index_list missing expr_fn in parameter conditional assign path

**GitHub Issue:** [#1031](https://github.com/jeffreyhorn/nlp2mcp/issues/1031)
**Status:** OPEN
**Severity:** Medium — prevents imsl from parsing
**Date:** 2026-03-09
**Affected Models:** imsl (SEQ=59)

---

## Problem Summary

The `imsl` model fails to parse via `parse_model_file` with:

```
ParserSemanticError: offset_func requires an expr_fn argument
```

The failure occurs in `_handle_conditional_assign_general` at the parameter conditional assignment path. When processing `w(m+1,n)$w(m,n) = 1 - w(m,n)`, the `_process_index_list` call does not pass `expr_fn`, so the `m+1` offset expression cannot be evaluated.

---

## Reproduction

```python
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
ir = parse_model_file('data/gamslib/raw/imsl.gms')
# Raises: ParserSemanticError: offset_func requires an expr_fn argument
```

Full traceback points to `src/ir/parser.py` line 4562 in `_handle_conditional_assign_general`.

---

## Root Cause

In `src/ir/parser.py`, the parameter conditional assign path in `_handle_conditional_assign_general` calls:

```python
raw_indices = _process_index_list(target.children[1])
```

without passing `expr_fn`. When the target has index offsets like `m+1`, `_process_index_list` tries to call `offset_func` which requires `expr_fn` to evaluate the offset expression.

The set assignment path (lines ~4509-4539) was already fixed to pass `expr_fn` in PR #1029, but the parameter path was not.

---

## Triggering GAMS Code

From `imsl.gms` line 40-41:

```gams
w(m+floor((ord(n)-1)/k),n)$(ord(m) = 1) = 1 - mod(ord(n)-1,k)/k;
w(m+1,n)$w(m,n) = 1 - w(m,n);
```

The `m+1` offset in `w(m+1,n)` requires `expr_fn` to process.

---

## Proposed Fix

Catch `ParserSemanticError` in the except clause alongside `AttributeError`, `IndexError`, `TypeError` and set `has_offset = True` so the assignment falls through to `_handle_assign`, which handles offsets correctly:

```python
except (AttributeError, IndexError, TypeError, ParserSemanticError):
    has_offset = True  # Assume offset; fall through to _handle_assign
    has_subset_index = False
```

---

## Affected Files

- `src/ir/parser.py` — `_handle_conditional_assign_general` parameter path (line ~4562)
- `data/gamslib/raw/imsl.gms` — lines 40-41

---

## Context

- Pre-existing issue (fails on `main` too)
- Same class of bug as the srpchase regression fixed in PR #1029
- Discovered during PR #1029 review
- Related to Issue #1030 (dual parse entry points masking failures)
