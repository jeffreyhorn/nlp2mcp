# Loop Statement: Tuple Domain with Dollar Condition Not Supported

**GitHub Issue:** [#808](https://github.com/jeffreyhorn/nlp2mcp/issues/808)

## Issue Type
Parser Error

## Affected Models
- senstran (GAMSlib model)

## Description
GAMS allows loop statements with tuple domains and dollar conditions in the form:

```gams
loop((i,j)$condition, statements);
```

The current grammar supports:
- `loop((i,j), statements)` - tuple domain without condition
- `loop(i$condition, statements)` - single index with condition

But does NOT support the combination of tuple domain with dollar condition.

## Error Details

### senstran
```
Error: Parse error at line 90, column 1: Unexpected character: 'c'
  c(ip,jp) = c(ip,jp)*(1-sens);
  ^
```

The error occurs after this loop statement (line 89):
```gams
loop((ip,jp)$counter, counter = counter - 1;
   c(ip,jp) = c(ip,jp)*(1-sens);
```

## Root Cause
The `loop_stmt` grammar rule in `src/gams/gams_grammar.lark` has these variants:

```lark
loop_stmt: LOOP_K "(" id_list "," loop_body ")" SEMI
         | LOOP_K "(" "(" id_list ")" "," loop_body ")" SEMI  -> loop_stmt_paren
         | LOOP_K "(" ID DOLLAR "(" expr ")" "," loop_body ")" SEMI  -> loop_stmt_filtered
         | LOOP_K "(" ID DOLLAR "[" expr "]" "," loop_body ")" SEMI  -> loop_stmt_filtered
         | LOOP_K "(" "(" id_list ")" DOLLAR "(" expr ")" "," loop_body ")" SEMI  -> loop_stmt_paren_filtered
         | LOOP_K "(" "(" id_list ")" DOLLAR "[" expr "]" "," loop_body ")" SEMI  -> loop_stmt_paren_filtered
```

The `loop_stmt_paren_filtered` variants expect the comma AFTER the dollar condition:
```
"(" id_list ")" DOLLAR "(" expr ")" ","
```

But in senstran, the syntax is:
```
"(" id_list ")" DOLLAR expr ","
```

The condition is a bare expression (`counter`), not wrapped in parentheses or brackets.

## Reproduction
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/senstran.gms')"
```

Minimal reproduction:
```gams
Scalar counter / 5 /;
Parameter c(i,j);
loop((i,j)$counter,
   c(i,j) = 0;
);
```

## Expected Behavior
The parser should accept loop statements with tuple domains and bare dollar conditions (without parentheses or brackets).

## Proposed Fix
Extend `loop_stmt` in `src/gams/gams_grammar.lark` to support bare dollar conditions for tuple domains:

```lark
loop_stmt: LOOP_K "(" id_list "," loop_body ")" SEMI
         | LOOP_K "(" "(" id_list ")" "," loop_body ")" SEMI  -> loop_stmt_paren
         | LOOP_K "(" ID DOLLAR "(" expr ")" "," loop_body ")" SEMI  -> loop_stmt_filtered
         | LOOP_K "(" ID DOLLAR "[" expr "]" "," loop_body ")" SEMI  -> loop_stmt_filtered
         | LOOP_K "(" ID DOLLAR expr "," loop_body ")" SEMI  -> loop_stmt_filtered
         | LOOP_K "(" "(" id_list ")" DOLLAR "(" expr ")" "," loop_body ")" SEMI  -> loop_stmt_paren_filtered
         | LOOP_K "(" "(" id_list ")" DOLLAR "[" expr "]" "," loop_body ")" SEMI  -> loop_stmt_paren_filtered
         | LOOP_K "(" "(" id_list ")" DOLLAR expr "," loop_body ")" SEMI  -> loop_stmt_paren_filtered
```

The new variants allow `DOLLAR expr` without wrapping parentheses/brackets.

**Note:** This may require careful ordering to avoid ambiguity with the comma separator in the id_list.

## Related
- Similar to existing support for bare dollar conditions in single-index loops: `loop(i$condition, ...)`
- Related to equation conditional support (Sprint 19 Issue #703) which added bare dollar conditionals

## Files to Modify
- `src/gams/gams_grammar.lark` (loop_stmt rule)
- `tests/unit/gams/test_parser.py` (add test for tuple loop with bare dollar condition)

## Test Case
```gams
Sets i, j;
Scalar flag / 1 /;
Parameter c(i,j);

loop((i,j)$flag,
   c(i,j) = 0;
);
```

## Priority
Medium - affects 1 GAMSlib model (senstran). File declaration now parses correctly after Sprint 20 Day 4.

## Sprint Context
Discovered during Sprint 20 Day 4 (WS3 Lexer Phase 1) after fixing Subcat M File declaration. The File declaration now parses successfully, but the model fails later at the loop statement.

## Resolution

**Status:** FIXED

### Changes
1. **`src/gams/gams_grammar.lark`**: Added two new `loop_stmt` variants with bare `DOLLAR ID` conditions:
   - `LOOP_K "(" ID DOLLAR ID "," loop_body ")" SEMI -> loop_stmt_filtered` (single index)
   - `LOOP_K "(" "(" id_list ")" DOLLAR ID "," loop_body ")" SEMI -> loop_stmt_paren_filtered` (tuple domain)
2. **`tests/unit/test_issue_fixes_807_808_809.py`**: Added 3 unit tests covering tuple loop with bare dollar, single-index bare dollar, and tuple loop with parenthesized dollar (regression).

### Verification
- The minimal reproduction case `loop((i,j)$counter, ...)` now parses successfully.
- Note: senstran.gms now parses past the loop statement but hits a separate error at line 109 (if/else + put statement) which is a different issue.
- 3,622 tests pass, 10 skipped, 2 xfailed.
