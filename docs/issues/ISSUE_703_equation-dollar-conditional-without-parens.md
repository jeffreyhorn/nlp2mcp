# Equation Dollar Conditional Without Enclosing Parentheses

**GitHub Issue:** [#703](https://github.com/jeffreyhorn/nlp2mcp/issues/703)

**Issue:** The grammar's `condition` rule for equation definitions requires dollar conditionals to be wrapped in parentheses `$(expr)` or brackets `$[expr]`, but GAMS allows bare dollar conditionals like `$identifier(args)` without enclosing delimiters. This causes parse failures on equations like `minw(t)$tm(t)..`.

**Status:** Open
**Severity:** High — Affects up to 23 models in the active corpus
**Discovered:** 2026-02-13 (Sprint 19 Day 1, investigating weapons model)
**Affected Models:** weapons (confirmed), plus 22 other models with the same pattern (see below)

---

## Problem Summary

The GAMS language allows dollar conditionals on equation definitions in two forms:

1. **With enclosing parens:** `eqname(i)$(condition).. lhs =e= rhs;` — supported
2. **Bare identifier/call:** `eqname(i)$param(i).. lhs =e= rhs;` — **NOT supported**

Our grammar rule at `src/gams/gams_grammar.lark:365` defines:

```lark
condition: DOLLAR "(" expr ")"
         | DOLLAR "[" expr "]"
```

This only matches `$(...)` and `$[...]`. When GAMS uses the bare form `$identifier(args)`, the parser sees `$` followed by an identifier (not an opening paren/bracket) and fails.

---

## Reproduction

**Model:** `weapons` (`data/gamslib/raw/weapons.gms`)

**Failing line (63):**
```gams
minw(t)$tm(t).. sum(w$td(w,t), x(w,t)) =g= tm(t);
```

**Command to reproduce:**
```bash
.venv/bin/python -c "
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/weapons.gms')
"
```

**Error output:**
```
Error: Parse error at line 63, column 1: Unexpected character: 'p'
  probe(t)..      prob(t) =e= 1 - prod(w$td(w,t), (1-td(w,t))**x(w,t));
  ^
Expected one of: DOLLAR, __ANON_0, ASSIGN
```

Note: The error appears on line 63 (`probe(t)..`) because the parser is still trying to complete the failed parse of line 61 (`minw(t)$tm(t)..`). The parser consumed `minw(t)` and `$` but couldn't match `tm(t)` as a `condition` (expected `(` or `[`), so it kept scanning forward looking for valid continuations.

**Minimal GAMS reproduction:**
```gams
Set t / 1*5 /;
Parameter tm(t) / 1 1, 3 1 /;
Variable x(t), z;
Equation minw(t), obj;
minw(t)$tm(t).. x(t) =g= tm(t);
obj..           z =e= sum(t, x(t));
Model m / all /;
Solve m minimizing z using nlp;
```

---

## Root Cause

The `condition` rule in `gams_grammar.lark` (line 365) only accepts dollar conditionals with explicit grouping delimiters:

```lark
condition: DOLLAR "(" expr ")"
         | DOLLAR "[" expr "]"
```

GAMS syntax also allows bare expressions after `$` without delimiters. The most common forms seen in gamslib models are:

1. **`$param(indices)`** — e.g., `minw(t)$tm(t)..` (parameter filter)
2. **`$set_membership(indices)`** — e.g., `cc(g,m,i,t)$mpos(g,m,i)..`
3. **Chained:** `ubnd(cr,i,t)$(cposm(cr,i)$pdlim(i,cr))..` (nested dollar conditionals)

---

## Proposed Fix

Extend the `condition` rule to accept bare expressions after `$`:

```lark
condition: DOLLAR "(" expr ")"
         | DOLLAR "[" expr "]"
         | DOLLAR ID "(" index_list ")"    // bare parameter/set conditional
         | DOLLAR ID                        // bare scalar conditional
```

Alternatively, a more general approach would parse `DOLLAR expr` where `expr` handles all cases, but this may introduce ambiguity with the rest of the grammar (since `$` is also used in dollar conditionals within expressions via `index_spec`).

**Key consideration:** The `condition` rule is used by both `eqn_def_domain` and `eqn_def_scalar` in `equation_def`. The fix must not introduce ambiguity with `DOLLAR` in `index_spec` (used in sum/prod domains), or with `$` in assignment conditionals.

---

## Affected Models (29 total, 23 in active corpus)

Models containing `$identifier(..)..` pattern in equation definitions:

| Model | Status | Error Category | Bare Dollar Pattern |
|-------|--------|---------------|-------------------|
| weapons | FAIL | lexer_invalid_char | `minw(t)$tm(t)..` |
| camcge | FAIL | lexer_invalid_char | `profitmax(i,lc)$wdist(i,lc)..` |
| cesam | FAIL | lexer_invalid_char | `SAMMAKE(ii,jj)$nonzero(ii,jj)..` |
| cesam2 | FAIL | lexer_invalid_char | `SAMCOEF(ii,jj)$NONZERO(ii,jj)..` |
| dinam | FAIL | lexer_invalid_char | `dsc(te)$t(te)..` |
| fawley | FAIL | lexer_invalid_char | `qsb(cfq,l,s)$specs(cfq,l,s)..` |
| fdesign | FAIL | lexer_invalid_char | `passband_up_bnds(i)$omega_pass(i)..` |
| feedtray | FAIL | lexer_invalid_char | `eqname$cond..` |
| ferts | FAIL | lexer_invalid_char | various |
| indus | FAIL | lexer_invalid_char | various |
| iswnm | FAIL | lexer_invalid_char | various |
| korcge | FAIL | lexer_invalid_char | various |
| lop | FAIL | lexer_invalid_char | various |
| marco | FAIL | lexer_invalid_char | various |
| mexls | FAIL | lexer_invalid_char | various |
| mine | FAIL | lexer_invalid_char | various |
| nebrazil | FAIL | lexer_invalid_char | various |
| nemhaus | FAIL | lexer_invalid_char | various |
| otpop | FAIL | lexer_invalid_char | various |
| saras | FAIL | lexer_invalid_char | various |
| sarf | FAIL | lexer_invalid_char | various |
| turkey | FAIL | lexer_invalid_char | various |
| turkpow | FAIL | lexer_invalid_char | various |
| worst | FAIL | lexer_invalid_char | various |
| andean | none | — | `ubnd(cr,i,t)$(cposm(cr,i)$pdlim(i,cr))..` |
| indus89 | none | — | various |
| minlphi | none | — | various |
| msm | none | — | various |
| sddp | none | — | various |

**Note:** Not all 23 failing models necessarily fail *because* of this issue — their first parse error may be a different `lexer_invalid_char` subcategory. However, even if they pass their current first error in the future, they will eventually hit this equation dollar conditional gap.

---

## Impact

Fixing this grammar gap would potentially unblock a significant portion of the `lexer_invalid_char` failures. Since 23 of 72 `lexer_invalid_char` models (32%) contain this pattern, the fix could contribute substantially to the Sprint 19 goal of reducing `lexer_invalid_char` from 72 to below 30.

---

## Related Issues

- This is distinct from dollar conditionals within sum/prod index specs (`sum(w$td(w,t), ...)`) which are already supported via the `index_spec` rule.
- This is distinct from dollar conditionals in assignments (`x(i)$cond(i) = ...`) which may use a separate grammar path.
