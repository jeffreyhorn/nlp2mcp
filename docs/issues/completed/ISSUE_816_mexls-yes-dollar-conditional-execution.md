# mexls: `yes$(...)` Conditional Execution Not Supported

**GitHub Issue:** [#816](https://github.com/jeffreyhorn/nlp2mcp/issues/816)
**Model:** `mexls` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 957/1088, 88%)
**Severity:** Medium — blocks full parse of mexls
**Date:** 2026-02-21
**Status:** FIXED

---

## Problem Summary

The grammar does not support `yes$(condition)` as a standalone statement or assignment value. GAMS uses `yes` as a special domain membership value, and `yes$(cond)` conditionally assigns domain membership. The parser fails when encountering `yes` as the start of a statement.

---

## Root Cause

Multiple grammar and preprocessor gaps:

1. `yes`/`no` not recognized as valid expression atoms (like `inf`, `eps`, `na`)
2. `yes$(condition)` / `no$(condition)` not supported as conditional expressions
3. `$sum(...)` not supported in dollar conditions — `sum` is a keyword (`SUM_K`), not an `ID`, so `DOLLAR ref_indexed` didn't match
4. Multi-line assignments where line ends with `=` weren't being joined by the preprocessor
5. Wildcard `*` not supported in set and variable domain declarations (e.g., `Set xpos(i,j,*)`, `Variable xm(i,j,*)`)

---

## Fix Applied

### Grammar (`src/gams/gams_grammar.lark`)

1. Added `YES_K` and `NO_K` terminals:
   ```
   YES_K: /(?i:yes)\b/
   NO_K: /(?i:no)\b/
   ```

2. Added yes/no as atom alternatives in expression rules:
   ```
   | YES_K condition -> yes_cond
   | YES_K           -> yes_value
   | NO_K condition  -> no_cond
   | NO_K            -> no_value
   ```

3. Added aggregate functions and func_call to `condition` rule for `$sum(...)`, `$prod(...)`, etc.:
   ```
   | DOLLAR sum_expr
   | DOLLAR prod_expr
   | DOLLAR smax_expr
   | DOLLAR smin_expr
   | DOLLAR func_call
   ```

4. Changed set and variable domain lists from `id_list` to `id_or_wildcard_list` to support `*` in domains.

### Parser (`src/ir/parser.py`)

- Added `yes_value`/`no_value` handlers returning `Const(1.0)`/`Const(0.0)`
- Added `yes_cond`/`no_cond` handlers returning `Const(1.0)`/`Const(0.0)` (condition captured but simplified)
- Updated set_domain/set_domain_with_members to use `_id_or_wildcard_list`
- Updated all var_item_indexed domain extraction to use `_id_or_wildcard_list`

### Preprocessor (`src/ir/preprocessor.py`)

- Extended `join_multiline_assignments` to detect trailing `=` (but not `==`) as a continuation trigger, joining `expr =\n value;` into a single line.

### Tests

- `tests/unit/test_issues_816_817.py::TestYesNoValues` — yes/no as boolean values
- `tests/unit/test_issues_816_817.py::TestYesNoCondition` — yes$/no$ conditional expressions
- `tests/unit/test_issues_816_817.py::TestDollarSumCondition` — $sum as condition
- `tests/unit/test_issues_816_817.py::TestWildcardDomain` — wildcard in set/variable domains

### Verification

mexls now fully parses:
```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/mexls.gms'); print('OK')"
```

---

## Impact

- Unblocks: mexls full parse
- Related: Any GAMSlib model using `yes$()`/`no$()`, `$sum(...)` conditions, or wildcard domains
