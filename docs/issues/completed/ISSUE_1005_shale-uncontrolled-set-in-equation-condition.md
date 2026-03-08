# shale: Uncontrolled set index in stationarity equation condition and .fx statements ($149)

**GitHub Issue:** [#1005](https://github.com/jeffreyhorn/nlp2mcp/issues/1005)
**Model:** shale (GAMSlib SEQ=46)
**Status:** FIXED
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

### Lines 374-375 — $149 in .fx statements

```
 374  h.fx(m,tf)$(not (ts(t,tf))) = 0;
****                       $149
 375  piL_h.fx(m,tf)$(not (ts(t,tf))) = 0;
****                           $149
```

---

## Root Cause

**Primary file:** `src/kkt/stationarity.py`
**Function:** `_find_variable_access_condition()`

The condition `ts(t,tf)` was detected by `_collect_access_conditions()` as the common dollar condition guarding access to variable `h(m,tf)`. However, the validation step used `_collect_symbolref_names()` to detect uncontrolled indices. This function only finds `SymbolRef` AST nodes via `expr.children()`, but `ParamRef` stores its indices as plain strings (not `SymbolRef` children). Since the parser represents `ts(t,tf)` as `ParamRef('ts', ('t', 'tf'))`, the function returned an empty set — missing the uncontrolled `t` index entirely. The condition passed through unchanged, producing bare `t` in the equation condition and `.fx` statements.

---

## Fix Applied

Replaced `_collect_symbolref_names()` with `_collect_free_indices()` in `_find_variable_access_condition()`. The `_collect_free_indices()` function properly handles string indices in `ParamRef`/`VarRef` nodes and correctly identifies `t` as a free (uncontrolled) index not in the variable domain `(m, tf)`.

When extra indices are found, instead of rejecting the condition outright (the old Issue #730 behavior), the fix lifts them into an existential check: `sum(extra_indices, 1$cond)`. This mirrors the existing lifting logic in `_extract_all_conditioned_guard()`.

**Result:**
- `$(ts(t,tf))` → `$(sum(t, 1$ts(t,tf)))` — equation condition
- `$(not (ts(t,tf)))` → `$(not (sum(t, 1$ts(t,tf))))` — .fx statements

Files modified:
- `src/kkt/stationarity.py`: Replaced `_collect_symbolref_names()` with `_collect_free_indices()` in `_find_variable_access_condition()` and added existential lifting for uncontrolled indices

### Verification

- All 3970 tests pass
- Quality gate: typecheck, lint, format all pass
- All 3 $149 errors eliminated from shale MCP output
- Remaining shale errors ($170 domain violation) are separate issues

---

## Notes

- The stationarity equation BODY was already correctly handled by the Sprint 22 Day 1 Sum-wrapping fix
- The `.fx` statements automatically use the lifted condition because they read from `kkt.stationarity_conditions`, which stores the same lifted `Expr`
- The `stat_phik(tf)$(t(tf))` equation was unaffected because `$(t(tf))` uses a `SetMembershipTest` with `SymbolRef` children, which `_collect_symbolref_names()` could detect
