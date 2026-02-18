# Parser: Variable Bound Assignment with Multi-Level Compound Index

**Status:** FIXED (2026-02-18)
**Fixed In:** `sprint19-day14-fix-issues-780-784`
**Fix:** Two changes:
1. **Grammar** (`src/gams/gams_grammar.lark`): Added `ref_indexed -> offset_func` alternative to `offset_expr`, allowing indexed parameter references like `li(k)` as index offsets (previously only `func_call` was supported).
2. **Parser** (`src/ir/parser.py`): Updated `offset_func` handler in `_process_index_expr()` to detect whether the inner node is `symbol_indexed` (from `ref_indexed`) and pass it directly to `expr_fn`, vs. a `func_call` node (wrapped in synthetic `funccall` tree). The equation head `pr(k,l+1,i,j)` grammar was already handled by the existing `domain_element: ID lag_lead_suffix` rule — the actual blocker was `x(l,i+li(k),j+lj(k))` using `li(k)` as an offset.
**Verified:** `mine.gms` now parses successfully (2 equations). `ampl.gms` also fixed (equation head `balance(r,tl+1)..` already worked via existing grammar). All 3,579 tests pass.
**Severity:** Medium — blocks parse of mine.gms; same pattern affects any model using `x.up(i,j,k) = val` after equation with `pr(k,l+1,i,j)` compound equation head index
**Date:** 2026-02-18
**Affected Models:** mine.gms
**GitHub Issue:** [#780](https://github.com/jeffreyhorn/nlp2mcp/issues/780)

---

## Problem Summary

`mine.gms` fails to parse at line 64:

```
Error: Parse error at line 64, column 1: Unexpected character: 'x'
  x.up(l,i,j) = 1;
```

The parse error occurs immediately after the equation definition on line 62:

```gams
pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);
```

The equation head uses a **compound index with lead** (`l+1`) and a multi-index domain
(`k,l+1,i,j`). After this equation is processed, the parser state is inconsistent and
rejects the subsequent bound assignment `x.up(l,i,j) = 1;`.

---

## GAMS Code Pattern

```gams
Set l 'identifiers for level row and column labels' / 1*4 /;
Alias (l,i,j);

Set
   k        'location of four neighboring blocks' / nw, "ne", se, sw /
   c(l,i,j) 'neighboring blocks related to extraction feasibility';

Parameter
   li(k)    'lead for i'  / (se,sw)   1 /
   lj(k)    'lead for j'  / ("ne",se) 1 /;

Variable x(l,i,j);

Equation pr(k,l,i,j) 'precedence relationships';

pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);

x.up(l,i,j) = 1;    -- Line 64: parse fails here
```

The equation head `pr(k,l+1,i,j)` has:
1. A compound multi-index domain `(k,l+1,i,j)` — 4 indices
2. A lead offset `l+1` in the **equation domain** (not the variable index)
3. A dollar condition `$c(l,i,j)` after the head

This is distinct from lead/lag in variable references (already supported). Here, the
lead/lag offset appears in the **equation head domain** declaration.

---

## Root Cause

The parser's equation head handler does not support `IndexOffset` in the **equation
domain** position (e.g., `pr(k, l+1, i, j)`). The `eqn_head_mixed_list` grammar rule
(added in Sprint 19 Day 11) handles comma-separated equation domain names with
descriptions, but does not accommodate lead/lag offsets as domain specifiers.

When the parser encounters `pr(k,l+1,i,j)`, it cannot resolve the equation's domain
correctly, leaving the parser in an inconsistent state that causes the next valid
statement (`x.up(l,i,j) = 1;`) to fail.

---

## Expected Behavior

The parser should recognize `pr(k,l+1,i,j)..` as an equation definition with a
shifted domain index. In GAMS, `eq(i+1)..` means the equation is defined for elements
where `i+1` is in range. For NLP-to-MCP purposes, this is equivalent to restricting the
equation domain by one element.

---

## Proposed Fix

Extend the equation head grammar and parser to allow `IndexOffset` expressions in the
equation domain index list. The `eqn_head_mixed_list` / `eqn_head` rules should accept:

```lark
eqn_domain_idx: ID lag_lead_suffix?   -> eqn_domain_index
```

And in the semantic handler, when an `IndexOffset` appears in the equation domain,
store it as a shifted domain with appropriate domain restriction (or treat the shifted
index as defining a sub-range of the original set).

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/gams/gams_grammar.lark` | `eqn_head`, `eqn_head_mixed_list` rules (lines ~200-240) |
| `src/ir/parser.py` | `_handle_eqn_def_domain()`, `_handle_equations_block()` |
| `data/gamslib/raw/mine.gms` | Affected model; lines 57-64 |

---

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/mine.gms')
"
# ParseError: Error: Parse error at line 64, column 1: Unexpected character: 'x'
#   x.up(l,i,j) = 1;
```

---

## Related Issues

- Sprint 19 Day 11 added `eqn_head_mixed_list` for `Equation a(i), b(j)` patterns
- Sprint 19 Day 13 added `offset_paren`/`offset_func` support for IndexOffset in variable references
- The lead/lag offset in equation domain positions is a separate gap from lead/lag in variable index positions
