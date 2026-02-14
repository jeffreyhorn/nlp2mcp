# Parser: Inline End-of-Line Comments and Lead Operator `l()` (lop)

**GitHub Issue:** [#722](https://github.com/jeffreyhorn/nlp2mcp/issues/722)
**Status:** Open
**Severity:** High — Blocks parsing of lop model from line 344 onward
**Discovered:** 2026-02-13 (Sprint 19, after Issues #715 and #718 advanced lop past abort and tuple-domain fixes)
**Affected Models:** lop

---

## Problem Summary

The lop model fails to parse at preprocessed line 344 (`Model evaldt / dtllimit, sumbound, defobjdtlop /;`) because the parser cannot handle the equation definition on line 340. That equation uses three unsupported GAMS features:

1. **`l()` lead operator in equation domain** — `dtllimit(l(sol,s,s1))..` uses the GAMS `l()` (lead) set operator to iterate over consecutive elements of a dynamic set
2. **Inline `//` end-of-line comments** — GAMS supports `//` as end-of-line comments, but the preprocessor does not strip them
3. **`min()` and `max()` as comparison functions** — Used inside dollar conditions with relational operators (e.g., `min(rp(sol,s),rp(sol,s1)) >= rp(sol,s2)`)

The parse failure on line 340 prevents the parser from recovering to parse the `Model` statement on line 344, the `Solve` on line 350, and subsequent `Display` statements.

---

## Reproduction

**Model:** `lop` (`data/gamslib/raw/lop.gms`)

**Command:**
```bash
python -m src.cli data/gamslib/raw/lop.gms --diagnostics
```

**Error:**
```
Error: Parse error at line 344, column 1: Unexpected character: 'M'
  Model evaldt / dtllimit, sumbound, defobjdtlop /;
  ^

Suggestion: This character is not valid in this context
```

**Raw GAMS source (lines 350-358 of `data/gamslib/raw/lop.gms`):**
```gams
dtllimit(l(sol,s,s1))..
   sum((s2,s3)$(od(s2,s3) and rp(sol,s2) and rp(sol,s3) and
       (min(rp(sol,s),rp(sol,s1)) >= rp(sol,s2) and // s and s1 must be
        max(rp(sol,s),rp(sol,s1)) <= rp(sol,s3)  or // between the nodes of the
        min(rp(sol,s),rp(sol,s1)) >= rp(sol,s3) and // origin destination pair
        max(rp(sol,s),rp(sol,s1)) <= rp(sol,s2))),  // s2-s3 in order to
   dtr(sol,s2,s3)) =l= cap(sol);                    // occupy capacity of s s1
```

**Preprocessed output (line 340):**
The preprocessor joins the multiline equation into a single line but does NOT strip the `//` comments, producing:
```
dtllimit(l(sol,s,s1)).. sum((s2,s3)$(od(s2,s3) and rp(sol,s2) and rp(sol,s3) and (min(rp(sol,s),rp(sol,s1)) >= rp(sol,s2) and // s and s1 must be max(rp(sol,s),rp(sol,s1)) <= rp(sol,s3)  or // between the nodes of the ...
```

---

## Root Causes

### 1. Inline `//` end-of-line comments not stripped by preprocessor

**File:** `src/ir/preprocessor.py`

GAMS supports `//` as end-of-line comments (similar to C++). The preprocessor strips `*` comments (column 1) and handles `$onText`/`$offText` blocks, but does not strip inline `//` comments. When multiline equations are joined into a single line, the `//` comment text becomes part of the expression, causing parse failures.

**Fix approach:** Add a preprocessing pass to strip `//` end-of-line comments. Care must be taken to avoid stripping `//` inside quoted strings.

### 2. `l()` lead operator not supported in equation domains

**File:** `src/parser/gams.lark` (grammar), `src/ir/parser.py` (AST builder)

The grammar rule for `equation_def` is:
```lark
equation_def: IDENT (func_args)? DOTDOT expression (COMMA expression)* SEMICOLON
```

The `func_args` rule matches `(sol,s,s1)` but NOT `(l(sol,s,s1))` — the `l()` is a GAMS lead operator that iterates over ordered set elements. The grammar has no rule for this operator.

**Fix approach:** Add grammar support for the `l()` (lead), `lag()`, `ord()`, and related GAMS set operators when used in equation domain specifications. In the IR, this could be represented as a filtered domain with an ordering constraint.

### 3. `min()`/`max()` as comparison functions in dollar conditions

The `min()` and `max()` calls are used as part of boolean expressions inside the dollar condition: `min(rp(sol,s),rp(sol,s1)) >= rp(sol,s2)`. These are standard GAMS intrinsic functions. If the grammar already supports `min`/`max` as function calls in expressions, this may work once issues 1 and 2 are fixed. If not, function call support in boolean expressions within dollar conditions needs to be added.

---

## Impact

- Lines 344-353 of the preprocessed lop model are unparsed (Model, Solve, Display statements)
- The lop model has two sub-models: `lop` (the LP) and `evaldt` (the direct traveler evaluation). The `lop` sub-model parses and solves correctly. The `evaldt` sub-model is blocked.
- This is the second model definition in the file; the first (`Model lop / all /`) was already parsed successfully in prior preprocessed output (line 346 in earlier testing before issue #718 was fixed moved line numbers)

---

## Suggested Fix Priority

1. **`//` comments** — Highest priority, simplest fix, affects any model using inline comments
2. **`l()` lead operator** — Medium priority, needed for lop and potentially other GAMSLib models
3. **`min()`/`max()` in conditions** — Likely already works once comments are stripped; verify after fix 1
