# harker: Multi-dimensional set used as sum domain emits uncontrolled indices

**GitHub Issue:** [#1002](https://github.com/jeffreyhorn/nlp2mcp/issues/1002)
**Model:** harker (GAMSlib SEQ=85)
**Status:** OPEN
**Error category:** `path_syntax_error` (Subcategory C — $149)
**Severity:** Medium — model parses and translates but GAMS compilation fails (16 $149 errors)

---

## Problem Summary

The harker MCP output uses `sum(arc, ...)` where `arc(n,np)` is a 2-dimensional set. In the original GAMS, `sum(arc, pairs(arc,"kappa") * t(arc))` implicitly binds both `n` and `np` through the multi-dimensional set `arc`. Our emitter expands the parameter/variable indices to `pairs(n,np,"kappa") * t(n,np)` but keeps `arc` as the single sum index, leaving `n` and `np` as uncontrolled set references.

---

## Error Details

### Lines 155, 159 — $149 in objdef and objoli equations

```
 155  objdef.. obj =E= ... - sum(arc, pairs(n,np,"kappa") * t(n,np) + tm * pairs(n,np,"nu") * power(t(n,np), 3));
****                          $149,149          $149,149           $149,149             $149,149
**** 149  Uncontrolled set entered as constant

 159  objoli.. obj =E= ... - sum(arc, pairs(n,np,"kappa") * t(n,np) + tm * pairs(n,np,"nu") * power(t(n,np), 3));
****                          $149,149          $149,149           $149,149             $149,149
**** 149  Uncontrolled set entered as constant
```

### Original GAMS (lines 90-93, 171-175)

```gams
objdef..  obj =e= sum(l, coefs(l,"rho")*d(l) - pm*coefs(l,"eta")*sqr(d(l)))
               -  sum(l, coefs(l,"alpha")*s(l) + coefs(l,"beta")*sqr(s(l)))
               -  sum(arc, pairs(arc,"kappa")*t(arc)
                         + tm*pairs(arc,"nu")*power(t(arc),3));
```

In the original, `arc` is a 2-dimensional set `arc(n,np)` and GAMS interprets `pairs(arc,...)` as `pairs(n,np,...)` implicitly. Our translator resolves the multi-dim indices but doesn't adjust the sum domain accordingly.

---

## Root Cause

**Primary file:** `src/emit/expr_to_gams.py` or `src/kkt/stationarity.py` (equation emission path)
**Related component:** Sum domain handling for multi-dimensional sets

When emitting `Sum(("arc",), body)` where the body contains `ParamRef("pairs", ("n", "np", ...))` and `VarRef("t", ("n", "np"))`, the emitter:
1. Correctly resolves `arc` references in the body to their constituent indices `(n, np)`
2. But does NOT update the Sum domain from `("arc",)` to `("n", "np")`

This means `n` and `np` appear in the body but are only controlled by `arc` — GAMS doesn't recognize that `arc` implicitly controls `n` and `np` when the sum domain uses the set name `arc` rather than its constituent indices.

### Expected Fix

When a Sum domain contains a multi-dimensional set `arc(n,np)`, and the body references constituent indices `n` and `np`, either:
- Expand the Sum domain to `("n", "np")` instead of `("arc",)`, OR
- Keep body references as `pairs(arc,...)` and `t(arc)` (matching the original GAMS idiom)

---

## Reproduction Steps

```bash
.venv/bin/python -m src.cli data/gamslib/raw/harker.gms -o /tmp/harker_mcp.gms --quiet
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/harker_mcp.gms lo=2 o=/tmp/harker_mcp.lst
grep '$149' /tmp/harker_mcp.lst
```

---

## Affected Equations

| Equation | Domain | Uncontrolled Indices | Source |
|----------|--------|---------------------|--------|
| objdef | scalar | n, np | `sum(arc, pairs(n,np,...) * t(n,np))` |
| objoli | scalar | n, np | `sum(arc, pairs(n,np,...) * t(n,np))` |

---

## Notes

- This is NOT a stationarity equation issue — the $149 errors are in the original model equations (objdef, objoli), not in KKT stationarity equations.
- The stationarity equations for harker may also be affected (they derive from these equations), but the primary fix should be in the equation/expression emission path.
- The `in(l)` equation has a similar pattern: `sum((n,l__), t(n,l__))` — here the sum domain correctly uses the expanded indices `(n,l__)`, showing that the translator CAN handle this pattern but misses it for `sum(arc, ...)`.
