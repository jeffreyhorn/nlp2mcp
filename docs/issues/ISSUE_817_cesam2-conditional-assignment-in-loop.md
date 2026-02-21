# cesam2: Conditional Assignment Inside Loop Body Not Supported

**GitHub Issue:** [#817](https://github.com/jeffreyhorn/nlp2mcp/issues/817)
**Model:** `cesam2` (GAMSlib)
**Blocking Stage:** Parse (lexer_invalid_char at line 324/494, 66%)
**Severity:** Medium — blocks full parse of cesam2
**Date:** 2026-02-21

---

## Problem Summary

The grammar does not support conditional indexed assignments (`name(indices)$condition = expr`) inside a `loop` body. The parser fails when it encounters a conditional assignment as a statement within a loop block.

---

## Reproduction

### Failing GAMS Pattern (cesam2.gms, lines 321–331)

```gams
loop((ii,jj)$NONZERO(ii,jj),
*  Set standard deviation for errors on cell values or coefficients
*  Additive errors
   sigmay3(ii,jj)$ival(ii,jj)   = stderr3*ABS(sam0(ii,jj));
*  Multiplicative errors
   sigmay3(ii,jj)$icoeff(ii,jj) = stderr3;
   vbar3(ii,jj,"1") = -3*sigmay3(ii,jj);
   vbar3(ii,jj,"2") =  0;
   vbar3(ii,jj,"3") =  3*sigmay3(ii,jj);
   wbar3(ii,jj,"1") =  1/18;
```

### Error Output

```
Error: Parse error at line 324, column 1: Unexpected character: 's'
  sigmay3(ii,jj)$ival(ii,jj)   = stderr3*ABS(sam0(ii,jj));
  ^
```

### Smoke Test Command

```bash
python -c "import sys; sys.setrecursionlimit(50000); from src.ir.parser import parse_file; parse_file('data/gamslib/raw/cesam2.gms')"
```

---

## Root Cause

The `exec_stmt` rule (used in loop bodies) does not support the `name(indices)$condition = expr` pattern. The `$` (dollar) conditional on the LHS of an assignment is a common GAMS pattern for conditional data manipulation inside loops, but the grammar's `assignment_stmt` or `exec_stmt` rules don't include this form.

Key patterns needed:
- `name(i,j)$cond(i,j) = expr;` — conditional indexed assignment
- `name(i,j)$scalar_cond = expr;` — conditional with scalar condition
- The `$` condition can reference indexed parameters or set membership tests

---

## Suggested Fix

1. Extend `assignment_stmt` (or `exec_stmt`) to allow `$condition` between the LHS index and `=`
2. Pattern: `ID "(" id_list ")" condition? ASSIGN expr SEMI`
3. The `condition` rule already exists in the grammar for equation definitions; reuse it

### Files to Modify

- `src/gams/gams_grammar.lark` — extend assignment rules with optional `$condition`
- `src/ir/parser.py` — handle conditional assignments in loop body processing

---

## Impact

- Blocks: cesam2 full parse
- Related: Any model using conditional assignments inside loop bodies (common GAMS pattern)
- Note: cesam2 also uses inline scalar data `/ .05 /` which was fixed in Sprint 20 Day 8
