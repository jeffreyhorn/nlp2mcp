# Parser: Multi-Index Sum Dollar Condition Scope (sum((i,j)$cond, ...) — Index Not In Scope

**Status:** OPEN
**Severity:** Medium — blocks parse of sparta.gms; same pattern may affect other models with multi-variable sum dollar conditions
**Date:** 2026-02-18
**Affected Models:** sparta.gms
**GitHub Issue:** [#784](https://github.com/jeffreyhorn/nlp2mcp/issues/784)

---

## Problem Summary

`sparta.gms` fails to parse at line 59, column 60:

```
Error: Parse error at line 59, column 60: Undefined symbol 'l' referenced
[context: equation 'bal2' LHS] [domain: ('t',)]
```

Line 59:
```gams
bal2(t).. sum((tp,l)$(ord(tp) <= ord(t) and (ord(tp) + ord(l)) > ord(t)), x(tp,l)) =g= req(t);
```

The sum `sum((tp,l)$cond, body)` binds both `tp` and `l` as sum index variables. The
dollar condition `$cond` uses both `tp` and `l` (via `ord(tp)` and `ord(l)`). However,
the parser only recognizes `tp` as a bound variable in the sum scope — `l` appears to
fall out of scope during dollar condition evaluation, producing "Undefined symbol 'l'".

---

## GAMS Code Pattern

```gams
Set
   t 'time periods (years)'         / 1*10 /
   l 'length of enlistment (years)' / len-1*len-4 /;

Alias (l,lp), (t,tp);

Variable x(t,l);
Parameter req(t);

Equation bal2(t);
bal2(t).. sum((tp,l)$(ord(tp) <= ord(t) and (ord(tp) + ord(l)) > ord(t)), x(tp,l)) =g= req(t);
```

In GAMS, `sum((i,j)$cond, body)` iterates over the Cartesian product of sets for `i`
and `j`, applying the condition as a filter. Both `i` and `j` are in scope within both
the condition and the body.

The parser handles `sum(i$cond, body)` (single-index sum with dollar) and
`sum((i,j), body)` (multi-index sum without dollar) correctly, but the combination
`sum((i,j)$cond, body)` does not correctly include all indices in the condition's scope.

---

## Root Cause

In the `_handle_aggregation()` method (and its grammar counterpart), the multi-index
sum form `sum((i,j)$cond, body)` uses the grammar rule `sum_domain` which may only
thread the **first** index as a free variable when processing the dollar condition, or
may not thread all tuple indices into the condition's `free_domain`.

The `sum((tp,l)$cond, body)` parse tree structure is:
```
sum
  sum_domain: (tp, l) $ cond
  body: x(tp,l)
```

When processing `cond`, the parser uses `body_domain = ('tp', 'l')` for the body, but
may use only `('tp',)` or `()` for the condition — causing `l` to be unrecognized.

---

## Expected Behavior

All indices in the sum's index tuple `(tp, l)` should be in scope within both:
1. The dollar condition `$(ord(tp) <= ord(t) and (ord(tp) + ord(l)) > ord(t))`
2. The sum body `x(tp,l)`

---

## Proposed Fix

In `_handle_aggregation()`, ensure that the `free_domain` passed to `_expr()` for the
dollar condition includes **all** sum-bound indices, not just a subset.

Locate where `sum_domain` with a `$condition` is processed. The condition should be
evaluated with `body_domain` (all bound indices) rather than a partial domain:

```python
# In _handle_aggregation():
# All sum indices must be in scope for the dollar condition
condition_domain = free_domain + tuple(all_sum_indices)
condition_expr = self._expr(condition_node, condition_domain)
```

The fix is likely a one-line change in the domain threading for the dollar condition
within `_handle_aggregation()`.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/ir/parser.py` | `_handle_aggregation()` — sum domain + condition processing |
| `src/gams/gams_grammar.lark` | `sum_expr`, `sum_domain`, `sum_domain_dollar` rules |
| `data/gamslib/raw/sparta.gms` | Affected model; lines 57-63 |

---

## Reproduction

```bash
python -c "
import sys; sys.setrecursionlimit(50000)
from src.ir.parser import parse_model_file
parse_model_file('data/gamslib/raw/sparta.gms')
"
# ParseError: Undefined symbol 'l' referenced [context: equation 'bal2' LHS] [domain: ('t',)]
```

---

## Minimal Reproducer

```gams
Set t / 1*10 /;
Set l / 1*4 /;
Alias (t,tp);
Variable x(t,l);
Parameter req(t) / 1 5, 2 6, 3 7, 4 6, 5 4, 6 9, 7 8, 8 8, 9 6, 10 4 /;
Equation bal(t);
bal(t).. sum((tp,l)$(ord(tp) <= ord(t) and (ord(tp) + ord(l)) > ord(t)), x(tp,l)) =g= req(t);
```

---

## Related Issues

- Single-index sum dollar conditions `sum(i$cond, body)` work correctly
- Multi-index sum without dollar `sum((i,j), body)` works correctly
- This issue is specifically the combination: multi-index tuple + dollar condition
- sparta.gms also uses `offset_paren` (bal1, bal4) which was fixed in Sprint 19 Day 13;
  the `bal2` scoping issue is the next blocker after that fix
