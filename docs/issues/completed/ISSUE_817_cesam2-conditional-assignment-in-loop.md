# cesam2: Conditional Assignment Inside Loop Body Not Supported

**GitHub Issue:** [#817](https://github.com/jeffreyhorn/nlp2mcp/issues/817)
**Model:** `cesam2` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 324/494, 66%)
**Severity:** Medium — blocks full parse of cesam2
**Date:** 2026-02-21
**Status:** FIXED

---

## Problem Summary

The grammar does not support conditional indexed assignments (`name(indices)$condition = expr`) inside a `loop` body. The parser fails when it encounters a conditional assignment as a statement within a loop block.

---

## Root Cause (Actual)

Investigation revealed the original diagnosis was incorrect. The grammar already had `lvalue condition ASSIGN expr SEMI -> conditional_assign_general` which handles conditional assignments in loop bodies.

The **real** root causes were:

1. **Indexed dollar condition on loop domain**: `loop((ii,jj)$NONZERO(ii,jj), ...)` — the `loop_stmt_paren_filtered` rule only supported `$ID`, `$(expr)`, `$[expr]` forms but NOT `$ID(id_list)` (an indexed function/parameter call as the filter condition).

2. **Square bracket delimiters for aggregation**: `sum[i, expr]` — the `sum_expr`, `prod_expr`, `smax_expr`, `smin_expr` rules only supported `()` and `{}` delimiters, not `[]`.

---

## Fix Applied

### Grammar (`src/gams/gams_grammar.lark`)

1. Added `loop_stmt_paren_filtered` alternative for indexed dollar condition:
   ```
   | LOOP_K "(" "(" id_list ")" DOLLAR ID "(" id_list ")" "," loop_body ")" SEMI -> loop_stmt_paren_filtered
   ```

2. Added `[` bracket support for all aggregation functions:
   ```
   sum_expr: SUM_K "[" sum_domain "," expr "]" -> sum
   prod_expr: PROD_K "[" sum_domain "," expr "]" -> prod
   smax_expr: SMAX_K "[" sum_domain "," expr "]" -> smax
   smin_expr: SMIN_K "[" sum_domain "," expr "]" -> smin
   ```

### Tests

- `tests/unit/test_issues_816_817.py::TestLoopIndexedCondition` — loop with indexed dollar condition
- `tests/unit/test_issues_816_817.py::TestSquareBracketAggregation` — sum/prod with square brackets

### Verification

cesam2 now fully parses:
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/cesam2.gms'); print('OK')"
```

---

## Impact

- Unblocks: cesam2 full parse
- Related: Any model using indexed conditions on loop domains or square bracket aggregation
