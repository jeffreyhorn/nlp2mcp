# Parser: Parameter Initialization with Tuple Element List (a08,a16,a24) Not Supported

**Status:** OPEN
**Severity:** Low-Medium — blocks parse of tabora.gms; same pattern (Subcategory A) affects other models using grouped parameter data
**Date:** 2026-02-18
**Affected Models:** tabora.gms
**GitHub Issue:** [#782](https://github.com/jeffreyhorn/nlp2mcp/issues/782)

---

## Problem Summary

`tabora.gms` fails to parse during parameter data processing:

```
internal_error: Parameter 'yv' references member 'a08' not present in set 'a'
[context: expression] (line 64, column 58)
```

Line 64:
```gams
   yv(a)    'yield of planted timber     (m3 per ha)' / (a08,a16,a24) 120 /
```

The parameter `yv(a)` is initialized with a **tuple element list** `(a08,a16,a24)` that
maps multiple set members to a single value (`120`). This is valid GAMS syntax for
assigning the same value to several elements at once, but the parser does not recognize
it and reports member `a08` as not in set `a`.

---

## GAMS Code Pattern

```gams
Set a 'age of trees' / a01*a24 /;

Parameter
   yv(a) 'yield of planted timber (m3 per ha)' / (a08,a16,a24) 120 /;
```

This is equivalent to:
```gams
Parameter yv(a);
yv('a08') = 120;
yv('a16') = 120;
yv('a24') = 120;
```

The GAMS syntax `/ (elem1,elem2,elem3) value /` assigns `value` to all listed elements.
It appears in parameter inline data blocks, table row headers, and scalar assignments.

---

## Root Cause

The parameter data parser's inline data handler does not support the `(elem1,elem2,...) value`
tuple grouping pattern. The grammar's `param_data` or `scalar_data` rule expects either:
- `elem value` — single element with value
- `elem1 v1, elem2 v2, ...` — multiple element-value pairs

But not:
- `(elem1,elem2,...) value` — tuple of elements sharing one value

When the parser encounters `(a08,a16,a24)` in the parameter data context, it fails to
resolve `a08` as a member of set `a`.

This is related to **Subcategory A (Tuple/Compound Set Data)** from the LEXER_ERROR_CATALOG,
but specifically for inline parameter data rather than set definitions.

---

## Expected Behavior

The parameter inline data handler should support:
```
/ (elem1, elem2, elem3) value, other_elem other_value /
```

Expanding to individual element-value pairs:
```
elem1 → value
elem2 → value
elem3 → value
```

---

## Proposed Fix

In the grammar, extend the `param_data_item` rule to accept a parenthesized element list
as the key:

```lark
param_data_item: param_key param_value
               | "(" param_key ("," param_key)* ")" param_value  -> param_tuple_key

param_key: ID | STRING | NUMBER
param_value: NUMBER | SPECIAL_VALUE | STRING | MINUS NUMBER
```

In the parser semantic handler, expand `param_tuple_key` into multiple `(key, value)`
pairs, one per element in the tuple list.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/gams/gams_grammar.lark` | `param_data`, `scalar_data`, `data_item` rules |
| `src/ir/parser.py` | `_handle_params_block()`, `_parse_param_data_value()` |
| `src/ir/preprocessor.py` | May need to expand tuple keys before parsing |
| `data/gamslib/raw/tabora.gms` | Affected model; line 64 |

---

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/tabora.gms')
"
# ParserSemanticError: Parameter 'yv' references member 'a08' not present in set 'a'
```

---

## Minimal Reproducer

```gams
Set a / a01*a24 /;
Parameter yv(a) / (a08,a16,a24) 120 /;
```

---

## Related Issues

- Subcategory A (Tuple/Compound Set Data) in LEXER_ERROR_CATALOG covers dotted compound
  set elements; this issue is specifically the `(elem,elem,...) value` form in parameter
  data blocks
- Sprint 19 Day 8-9 fixed compound set data in set definitions and table rows; parameter
  inline data with tuple keys remains unaddressed
