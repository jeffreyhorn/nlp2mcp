# paperco: Loop Body Parameter Assignment `pp(p)` Not Emitted

**GitHub Issue:** [#953](https://github.com/jeffreyhorn/nlp2mcp/issues/953)
**Status:** OPEN
**Severity:** High — 2 compilation errors block solve
**Date:** 2026-02-27
**Affected Models:** paperco

---

## Problem Summary

The paperco MCP output declares parameter `pp(p)` (price of pulp) without values. In the original model, `pp(p)` is assigned inside a `loop(scenario, ...)` statement that the IR parser does not process. The stationarity equations `stat_purchase` and `stat_sales` reference `pp(p)`, causing GAMS error $66 ("symbol pp has no values assigned").

---

## Error Details

```
 209  Solve mcp_model using MCP;
****                           $66,256
****  66  Use of a symbol that has not been defined or assigned
**** 256  Error(s) in analyzing solve statement.
**** The following MCP errors were detected in model mcp_model:
****  66 equation stat_purchase.. symbol "pp" has no values assigned
```

Total: **2 errors** ($66 + $256 cascading)

---

## Root Cause: Parameter Assignment Inside Loop Body

In `paperco.gms` (lines 111-117), `pp(p)` is assigned inside a loop:

```gams
loop(scenario,
   purchase.up(p) = psdat(scenario,p,'p');
   sales.up(p)    = psdat(scenario,p,'s');
   pp(p)          = ppdat(scenario,p);         * <-- Assignment here
   solve wood maximizing profit using lp;
   option limCol = 0, limRow = 0;
);
```

The parameter declaration (line 54) has no initial values:

```gams
Parameter
   pq(q) 'sales price'   / kraft 265, newsprint 275, printing 310 /
   pp(p) 'price of pulp'                    * <-- NO initial values
   pc(w) 'price of wood products' / ground 18, chips 16 /;
```

The IR parser's `_handle_loop_stmt()` stores the loop body as raw AST in `model_ir.loop_statements` but does not process individual statements. The assignment `pp(p) = ppdat(scenario,p)` is never added to `ParameterDef.expressions`, so the emitter outputs `pp(p)` with no data.

The stationarity equations use `pp(p)`:
- `stat_purchase(p).. pp(p) - nu_pbal(p) - piL_purchase(p) =E= 0;`
- `stat_sales(p).. ((-1) * pp(p)) + nu_pbal(p) - piL_sales(p) =E= 0;`
- `obj.. profit =E= sum(p, pp(p) * sales(p)) + ... - sum(p, pp(p) * purchase(p));`

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/paperco.gms -o /tmp/paperco_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/paperco_mcp.gms lo=2
```

---

## Proposed Fix

### Option A: Extract Loop Body Parameter Assignments (Preferred)

Same approach as lmp2 (#TBD): enhance `_handle_loop_stmt()` in `src/ir/parser.py` to walk the loop body and extract parameter assignment statements into `ParameterDef.expressions`.

For paperco specifically, the assignment `pp(p) = ppdat(scenario,p)` references the loop variable `scenario`. To emit a valid MCP, one approach is:
1. Use the **last iteration's value**: `pp(p) = ppdat('scenario-3', p);`
2. Or pick a representative scenario (e.g., scenario-1)

Since `ppdat` has known values:
```
ppdat('scenario-1','pulp-1') = 120
ppdat('scenario-1','pulp-2') = 140
ppdat('scenario-2','pulp-1') = 120
ppdat('scenario-2','pulp-2') = 140
ppdat('scenario-3','pulp-1') = 120
ppdat('scenario-3','pulp-2') = 150
```

The MCP transformation is for a single solve snapshot, so any scenario's values would work.

### Option B: Emit `ppdat` Direct Assignment as Fallback

If loop body extraction is too complex, detect that `pp(p)` is used in equations but has no values, and emit a placeholder assignment like:
```gams
pp(p) = 0;
```
This allows compilation but may produce incorrect MCP solutions.

---

## Relationship to Other Issues

This issue shares the same root cause as the lmp2 dynamic subset issue (#952): the IR parser does not process statements inside `loop()` bodies. A unified fix for loop body extraction would resolve both models.

---

## Files to Modify

| File | Changes |
|------|---------|
| `src/ir/parser.py` | Walk loop body statements in `_handle_loop_stmt()` |
| `src/emit/original_symbols.py` | Emit parameter assignments extracted from loop bodies |

---

## Notes

- The original paperco model solves multiple scenarios in a loop. For MCP transformation, we need a single representative set of parameter values.
- Variable bounds (`purchase.up`, `sales.up`) are also set inside the loop body — the emitter also does not emit these. However, since these are `up` bounds (not used in the current stationarity equations for positive variables), they don't cause compilation errors.
- The `psdat` reassignment statements (lines 43-48 in the MCP output) use `p` as a loop index to reassign values — these ARE emitted correctly because they're top-level assignments, not inside a loop.
