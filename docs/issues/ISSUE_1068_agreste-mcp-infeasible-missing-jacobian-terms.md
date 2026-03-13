# agreste: MCP Structurally Infeasible — Missing Jacobian Terms and Alias Handling Bug

**GitHub Issue:** [#1068](https://github.com/jeffreyhorn/nlp2mcp/issues/1068)
**Model:** agreste (SEQ=88) — Agreste Farm Level Model of NE Brazil
**Type:** LP
**Category:** KKT construction bug (Jacobian / alias index handling)

---

## Summary

The agreste model is structurally infeasible (model_status=4, 0 iterations) due to two bugs:
1. Missing `lam_landb(s)` in `stat_xcrop(p,s)` — **FIXED** (DollarConditional sparsity bug)
2. Incorrect alias transposition in `stat_lswitch(s)` — **OPEN** (deep architectural issue)

## Bug 1: DollarConditional Sparsity — FIXED

### Root Cause

`_collect_variables()` in `src/ad/sparsity.py` did not handle `DollarConditional` expressions. When the constraint `landb(s)` contains `sum(p$ps(p,s), a(p)*xcrop(p,s))$sc(s)`, the outer `$sc(s)` wraps the sum in a `DollarConditional` node. The sparsity checker's `else` clause silently skipped this node, so `xcrop` was never detected as participating in `landb(s)`. The Jacobian builder never differentiated the constraint w.r.t. `xcrop`, and `stat_xcrop(p,s)` was missing the `lam_landb(s)` multiplier term entirely.

### Fix

Added a `DollarConditional` case to `_collect_variables()` in `src/ad/sparsity.py` that recurses into both `value_expr` and `condition` to collect all referenced variables.

### Result

`stat_xcrop(p,s)` now correctly includes:
```gams
(a(p) * 1$(ps(p,s)))$(sc(s)) * lam_landb(s)
```

## Bug 2: Alias Transposition in `stat_lswitch(s)` — OPEN

### Root Cause

The `landb(s)` constraint contains `sum(sp, ldp(s,sp)*lswitch(sp))` where `sp` is an alias of `s`. Differentiating w.r.t. `lswitch(s)` should produce `sum(sp, ldp(sp,s) * lam_landb(sp))` (transposed sum), but produces diagonal `ldp(s,s) * lam_landb(s)` with manual neighbor enumeration.

The bug is in `_diff_sum()` in `src/ad/derivative_rules.py`. When the sum index `sp` matches the differentiation target `s` (both aliases of the same set), `_sum_should_collapse()` returns True and the sum is collapsed. The parameter `ldp(s,sp)` has `sp` substituted to `s`, producing diagonal `ldp(s,s)` instead of preserving the transposed sum structure.

### What Would Be Needed

Fixing this requires changes to `_diff_sum()` and `_substitute_sum_indices()` to detect when parameter indices inside a collapsed sum need transposition. This is an architectural change affecting how alias-indexed sums are differentiated and is deferred to a future sprint.

## Files Modified

- `src/ad/sparsity.py` — Added `DollarConditional` case to `_collect_variables()`
- `tests/unit/ad/test_sparsity.py` — Added 4 unit tests for `DollarConditional` sparsity
- `data/gamslib/mcp/agreste_mcp.gms` — Regenerated MCP fixture with corrected Jacobian

## Files

- `data/gamslib/raw/agreste.gms` — original LP model
- `data/gamslib/mcp/agreste_mcp.gms` — generated MCP
- Key MCP equation: `stat_xcrop(p,s)` (Bug 1 fixed), `stat_lswitch(s)` (Bug 2 open)
