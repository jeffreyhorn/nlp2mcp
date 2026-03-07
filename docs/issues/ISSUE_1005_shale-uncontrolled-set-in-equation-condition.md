# shale: Uncontrolled set index in stationarity equation condition and .fx statements ($149)

**GitHub Issue:** [#1005](https://github.com/jeffreyhorn/nlp2mcp/issues/1005)
**Model:** shale (GAMSlib SEQ=46)
**Status:** OPEN
**Error category:** `path_syntax_error` (Subcategory C — $149)
**Severity:** Medium — model parses and translates but GAMS compilation fails (3 $149 errors)

---

## Problem Summary

After the Sprint 22 Day 1 stationarity Sum-wrapping fix, shale's stationarity equation bodies no longer have uncontrolled indices. However, the **dollar condition** on the stationarity equation `stat_h(m,tf)$(ts(t,tf))` and the corresponding `.fx` statements still reference set `t` which is not in the equation domain `(m,tf)`. The `t` in the condition `$(ts(t,tf))` is uncontrolled.

---

## Error Details

### Line 318 — $149 in stat_h equation condition

```
 318  stat_h(m,tf)$(ts(t,tf)).. sum(t, ...) + sum(t, ...) - piL_h(m,tf) =E= 0;
****                    $149
**** 149  Uncontrolled set entered as constant
```

The equation body correctly wraps `t` in `sum(t, ...)` (the Day 1 fix works). But the dollar condition `$(ts(t,tf))` on the equation definition itself contains bare `t` which is not controlled by the equation domain `(m,tf)`.

### Lines 374-375 — $149 in .fx statements

```
 374  h.fx(m,tf)$(not (ts(t,tf))) = 0;
****                       $149
 375  piL_h.fx(m,tf)$(not (ts(t,tf))) = 0;
****                           $149
```

The `.fx` statements use the same `$(not (ts(t,tf)))` condition with uncontrolled `t`.

### Original GAMS Context

```gams
Set tf      / 1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010 /
    t(tf)   'active time periods' / 1975, 1980, 1985, 1990, 1995, 2000 /
    ts(t,tf) 'time steps' ;

ts(t,tf) = yes$(ord(tf) = ord(t) + 1) ;
```

Here `t` is a subset of `tf`, and `ts(t,tf)` is a 2-dimensional set mapping time steps. The stationarity equation for variable `h(m,tf)` should only be active for periods where `ts(t,tf)` holds — but `t` is not in the equation domain `(m,tf)`.

---

## Root Cause

**Primary file:** `src/kkt/stationarity.py`
**Key functions:**
- `_find_variable_access_condition()` — detects dollar conditions for stationarity equations
- `_find_variable_subset_condition()` — detects subset-based conditions
- Equation condition propagation in `build_stationarity_equations()`

The condition `$(ts(t,tf))` is propagated from the original equation's access pattern into the stationarity equation condition. However, `t` is a set index that appears in the condition but is NOT in the stationarity equation's domain `(m,tf)`.

The condition should either:
1. Be wrapped in an existential quantifier: `$(sum(t, ts(t,tf)))` or `$(sum(t$ts(t,tf), 1))` — "does there exist a `t` such that `ts(t,tf)`?"
2. Or use `t(tf)` instead — since `t` is a subset of `tf`, the condition `$(t(tf))` checks if element `tf` is in subset `t`, which is equivalent and doesn't introduce uncontrolled indices.

The same fix applies to the `.fx` statements which use `$(not (ts(t,tf)))`.

### Expected Fix

When a stationarity equation condition contains set indices not in the equation domain, either:
- Replace `$(ts(t,tf))` with the equivalent `$(t(tf))` (subset membership test)
- Or wrap in an existential check: `$(sum(t$ts(t,tf), 1))`

The `.fx` statement generation should apply the same transformation.

---

## Reproduction Steps

```bash
.venv/bin/python -m src.cli data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms --quiet
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/shale_mcp.gms lo=2 o=/tmp/shale_mcp.lst
grep '$149' /tmp/shale_mcp.lst
```

---

## Affected Equations/Statements

| Location | Domain | Uncontrolled Index | Pattern |
|----------|--------|-------------------|---------|
| stat_h(m,tf) | (m,tf) | t | `$(ts(t,tf))` in equation condition |
| h.fx(m,tf) | (m,tf) | t | `$(not (ts(t,tf)))` in .fx statement |
| piL_h.fx(m,tf) | (m,tf) | t | `$(not (ts(t,tf)))` in .fx statement |

---

## Notes

- The stationarity equation BODY is correctly handled by the Sprint 22 Day 1 Sum-wrapping fix — `sum(t, ...)` properly controls `t` inside the equation body.
- The issue is specifically in the equation CONDITION (dollar condition on the equation definition) and the corresponding `.fx` statements.
- Other shale errors ($170 domain violation) are separate issues unrelated to this $149 pattern.
- The `stat_phik(tf)$(t(tf))` equation on line 320 does NOT have this issue because it uses `$(t(tf))` directly (subset membership), not `$(ts(t,tf))`.
