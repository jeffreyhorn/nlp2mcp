# Parser: Inline End-of-Line Comments and Lead Operator `l()` (lop)

**GitHub Issue:** [#722](https://github.com/jeffreyhorn/nlp2mcp/issues/722)
**Status:** Fixed
**Severity:** High — Blocks parsing of lop model from line 344 onward
**Discovered:** 2026-02-13 (Sprint 19, after Issues #715 and #718 advanced lop past abort and tuple-domain fixes)
**Fixed:** 2026-02-14
**Affected Models:** lop (and any model using `$eolCom`)

---

## Problem Summary

The lop model fails to parse at preprocessed line 344 (`Model evaldt / dtllimit, sumbound, defobjdtlop /;`) because the preprocessor does not strip end-of-line comments defined by the `$eolCom //` directive. When multiline equations are joined into a single line, the `//` comment text gets embedded in the middle of the expression, causing parse failures.

---

## Fix

### 1. `$eolCom` comment stripping (`src/ir/preprocessor.py`)

Added `strip_eol_comments()` function that:
- Detects the `$eolCom` directive and extracts the comment marker (e.g., `//`)
- Strips everything from the comment marker to end-of-line on subsequent lines
- Respects quoted strings — comment markers inside single or double quotes are preserved
- Runs as Step 9b in the preprocessing pipeline, BEFORE `strip_unsupported_directives` (which strips the `$eolCom` directive itself) and BEFORE `join_multiline_equations` (which would embed comment text into joined lines)

### 2. `sameas` function support (`src/gams/gams_grammar.lark`)

Added `sameas` to the `FUNCNAME` terminal pattern so it is recognized as a built-in GAMS function. `sameas(s1,s2)` returns 1 if two set elements are identical, 0 otherwise. This was encountered during lop model testing after the comment fix advanced the pipeline.

### 3. Findings on the other reported issues

- **`l()` in equation domain**: `l` is actually a user-defined 4D set `l(s,s1,s2,s3)` declared at line 166 of lop.gms, not the GAMS lead operator. `dtllimit(l(sol,s,s1))..` is a subset-driven equation domain — the grammar already supports this via the `domain_element: ID ("(" index_list ")")` rule.
- **`min()`/`max()` in conditions**: Already supported — `min` and `max` are in the `FUNCNAME` terminal, and function calls work inside dollar conditions.

### Remaining blocker (separate issue)

After these fixes, the lop model advances to a new error at line 222:
```
Parameter 'rp' expects 3 indices, got 2 [context: expression]
  rp(ll,s)   = sum(r$lr(ll,s,r), ord(r));
```
This is a separate issue: `rp(s,s,s)` has 3 dimensions but `rp(ll,s)` uses the 2D set `ll` as a compact notation for 2 indices (GAMS set-mapping notation). This is a pre-existing limitation unrelated to Issue #722.

### Results

- `//` end-of-line comments are properly stripped before multiline joining
- `sameas()` is recognized as a built-in function
- The `Model evaldt`, `Solve`, and `Display` statements at lines 344-353 are now parseable
- All quality gates pass (typecheck, lint, format, 3315 tests)
