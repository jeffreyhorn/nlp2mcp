# maxmin: Unquoted Element Labels in .fx Equations (GAMS $120/$340)

**GitHub Issue:** [#939](https://github.com/jeffreyhorn/nlp2mcp/issues/939)
**Status:** PARTIALLY FIXED
**Severity:** Medium — Model translates but compilation errors prevented solve
**Date:** 2026-02-26
**Last Updated:** 2026-03-17
**Affected Models:** maxmin

---

## Problem Summary

The original issue described an `smin()` arity mismatch error. However, the solved model
(`maxmin1a`) does not use `smin` — only the unused `maxmin2a` model does. The `smin` arity
issue remains for models that use multi-index `smin(domain(i,j), expr)`, but it does not
block this model.

The actual blocking issue was GAMS compilation errors $120/$340 on the `.fx` equations:
```gams
point_fx_p1_x.. point("p1",x) - 0 =E= 0;
```

The set element `x` (from set `d / x, y /`) was emitted without quotes, causing GAMS to
interpret it as a set/alias reference rather than a literal element label.

---

## Fix Applied (2026-03-17)

Added `_quote_literal_indices()` in `src/ir/normalize.py` to pre-quote per-element bound
indices (from `fx_map`/`lo_map`/`up_map`) before they are stored in the VarRef expression.
This ensures `expr_to_gams` treats them as UELs, not domain variables.

**Before:** `point("p1",x)` — `x` unquoted, GAMS error $120/$340
**After:** `point("p1","x")` — `x` quoted, compiles correctly

---

## Remaining Issue: PATH Convergence

After the compilation fix, the MCP compiles but PATH fails with execution errors (division
by zero in stationarity equations). This is caused by the `low(n,nn)` set filtering — the
stationarity equation has `1/sqrt(distance)` terms where `distance = 0` for electron pairs
not in the lower-triangular filter. The `$(low(n,nn))` condition should prevent evaluation
but the stationarity builder expands the Jacobian into per-offset terms that may not carry
the condition properly.

This is the same class of issue as ISSUE_983 (elec) and ISSUE_862 (sambal) — domain
conditions from set-filtered sums not fully propagated through the stationarity pipeline.

---

## smin() Arity Note

The original issue about `smin(low(n,nn), expr)` creating 3 arguments instead of 2 is a
real parser issue, but does not affect the solved model `maxmin1a`. The smin multi-index
domain handling would need to be fixed for models that actually solve using smin-based
equations:
- Parser's `_handle_smin_smax()` (line 5040) expands multi-index domains into separate
  `SymbolRef` args
- `_diff_smin` (line 1407) expects exactly 2 arguments
- Fix: bundle multi-index domain as a tuple first argument, or use a dedicated SminExpr node

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/normalize.py` | Added `_quote_literal_indices()`, applied to lo_map/up_map/fx_map |

## Files to Investigate (Remaining Issues)

| File | Relevance |
|------|-----------|
| `src/ir/parser.py:5040` | smin multi-index domain expansion |
| `src/ad/derivative_rules.py:1407` | smin arity check |
| `src/kkt/stationarity.py` | Domain condition propagation for set-filtered sums |
