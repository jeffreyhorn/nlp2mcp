# Springchain: Square Bracket Expression in Scalar Data Not Supported

**GitHub Issue:** [#837](https://github.com/jeffreyhorn/nlp2mcp/issues/837)
**Status:** OPEN — Grammar does not support `[expr]` in scalar data context
**Severity:** Medium — Model fails to parse entirely
**Date:** 2026-02-22
**Affected Models:** springchain

---

## Problem Summary

The springchain model (`data/gamslib/raw/springchain.gms`) fails to parse because it uses
square bracket expressions in scalar data definitions, which the grammar does not support in
that context.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/springchain.gms

# Error: Parse error at line 31, column 43: Unexpected character: '['
#   L0    "rest length of each spring"     /  [2*sqrt(sqr(a_x-b_x) + sqr(a_y-b_y))/10]/
#                                              ^
```

---

## Root Cause

GAMS supports square bracket expressions `[expr]` as compile-time evaluation (similar to
`$eval`). In the springchain model, a scalar parameter's data block uses this syntax:

```gams
Scalar
  L0    "rest length of each spring"     /  [2*sqrt(sqr(a_x-b_x) + sqr(a_y-b_y))/10]/
```

The `[2*sqrt(...)/10]` is evaluated at compile time to produce a numeric value. The grammar's
`bracket_expr` rule exists for expressions in equation contexts but is not reachable from the
scalar data context (inside `/` delimiters).

---

## Suggested Fix

**Option A (preprocessor):** Evaluate `[expr]` in scalar data contexts at preprocessing time,
replacing them with their numeric values. This mirrors `$eval` semantics.

**Option B (grammar):** Extend the grammar to allow `bracket_expr` in scalar data positions
(inside `/` delimiters for Scalar/Parameter declarations).

Option A is likely cleaner since it avoids grammar complexity and aligns with GAMS semantics
where `[expr]` is compile-time evaluation.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/gams/gams_grammar.lark` | `scalar_data` / `data_record` rules — add bracket expr support |
| `src/ir/preprocessor.py` | Potential `$eval`-style preprocessing for `[expr]` |
| `data/gamslib/raw/springchain.gms` | Original model with bracket expressions in data |

---

## Classification

Lexer error catalog: Subcategory J (Bracket/Brace)

---

## Estimated Effort

~1-2h — either preprocessor `$eval` support or grammar extension for bracket expressions in
data blocks
