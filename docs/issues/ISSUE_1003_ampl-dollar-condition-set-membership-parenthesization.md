# ampl: Dollar condition set membership test missing parentheses ($119)

**GitHub Issue:** [#1003](https://github.com/jeffreyhorn/nlp2mcp/issues/1003)
**Model:** ampl (GAMSlib SEQ=74)
**Status:** OPEN
**Error category:** `path_syntax_error` (Subcategory C-adjacent — $119)
**Severity:** Medium — model parses and translates but GAMS compilation fails ($119 errors)

---

## Problem Summary

The ampl MCP output emits dollar conditions of the form `expr$t(tl)` where `t(tl)` is a set membership test ("is element `tl` a member of set `t`?"). GAMS requires parentheses around the condition in expression context: `expr$(t(tl))`. Without parentheses, GAMS interprets `$` as expecting a numeric value and raises Error $119 "Number expected".

This affects both the original model equation (`obj`) and the stationarity equation (`stat_s`).

---

## Error Details

### Line 104 — $119 in stat_s stationarity equation

```
 104  stat_s(r,tl).. ((-1) * ((((-1) * d(r)))$t(tl) + f(r)$(ord(tl) == card(tl)))) - nu_balance(r,tl) - piL_s(r,tl) + piU_s(r,tl) =E= 0;
****                                                                 $119
**** 119  Number (primary) expected
```

### Line 119 — $119 in obj equation (original model)

```
 119  obj.. profit =E= sum((p,t), c(p,t) * x(p,t)) + sum((r,tl), ((((-1) * d(r)))$t(tl) + f(r)$(ord(tl) == card(tl))) * s(r,tl));
****                                                                                                     $119
**** 119  Number (primary) expected
```

### Original GAMS (lines 53-55)

```gams
obj..  profit =e= sum((p,t), c(p,t)*x(p,t))
               +  sum((r,tl), (-d(r)$t(tl) + f(r)$tl.last)*s(r,tl));
```

In the original, `-d(r)$t(tl)` works because `$` is directly attached to `d(r)`. Our emitter restructures the expression to `((-1) * d(r)))$t(tl)` where the `$` follows a complex parenthesized expression, and GAMS fails to parse the condition.

---

## Root Cause

**Primary file:** `src/emit/expr_to_gams.py`
**Key function:** Dollar condition emission (DollarConditional handling)

The emitter outputs `value_expr$condition` but when the condition is a function-call-like set membership test `t(tl)`, GAMS needs it parenthesized as `$(t(tl))`. The issue is that:

1. The emitter may be omitting parentheses around the dollar condition when the condition is a `Call`-like or `SetMembershipTest` node.
2. The expression restructuring from `-d(r)` to `((-1) * d(r))` changes the syntactic context of the `$`, making GAMS interpret it differently.

### Expected Fix

Ensure dollar conditions are always parenthesized in the emitted GAMS:
- `expr$t(tl)` should become `expr$(t(tl))`
- This is safe for all cases since `$(...)` is always valid GAMS syntax

---

## Reproduction Steps

```bash
.venv/bin/python -m src.cli data/gamslib/raw/ampl.gms -o /tmp/ampl_mcp.gms --quiet
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/ampl_mcp.gms lo=2 o=/tmp/ampl_mcp.lst
grep '$119' /tmp/ampl_mcp.lst
```

---

## Affected Equations

| Equation | Type | Error | Pattern |
|----------|------|-------|---------|
| stat_s(r,tl) | Stationarity | $119 | `((-1) * d(r)))$t(tl)` |
| obj | Original model | $119 | `((-1) * d(r)))$t(tl)` |

---

## Notes

- The `$t(tl)` pattern appears in the original GAMS source, so it's a valid GAMS idiom. The issue is only triggered when the emitter restructures the surrounding expression.
- The `f(r)$(ord(tl) == card(tl))` in the same equations compiles fine because the condition is already parenthesized.
- This model was classified as Subcategory C ($149) in PATH_SYNTAX_ERROR_STATUS.md, but the Sprint 22 Day 1 stationarity fix resolved the $149 errors. The remaining $119 errors are a distinct dollar condition parenthesization issue.
