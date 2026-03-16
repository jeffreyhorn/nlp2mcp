# harker: Regression — SetMembershipTest Substitution Exposes Index Mapping Bug

**GitHub Issue:** [#1086](https://github.com/jeffreyhorn/nlp2mcp/issues/1086)
**Status:** FIXED
**Severity:** High — model_optimal regressed to path_solve_terminated
**Date:** 2026-03-14
**Last Updated:** 2026-03-15
**Affected Models:** harker (SEQ=108, "Spatial Price Equilibrium")
**Regressing PR:** #1083 (Sprint 22 Day 9)

---

## Problem Summary

The harker model regressed from model_optimal to path_solve_terminated due to two bugs:

1. **Bug 2 (stat_t condition)**: `SetMembershipTest` index substitution in
   `_replace_indices_in_expr` mapped concrete element values using positional domain
   resolution, producing `arc(n,n)` instead of `arc(n,np)`. Previously fixed.

2. **Bug 3 (nbal parser)**: `_extract_domain_indices` in `src/ir/parser.py` discarded
   the parent set name `arc` from `sum(arc(np,n), ...)`, producing `Sum(('np','n'), body)`
   without the `arc` set restriction. This caused nbal equations to sum over ALL
   transport flows instead of only those connected to the node.

---

## Fix Applied

### Parser Fix: Preserve index_subset set restriction (Bug 3)

**File:** `src/ir/parser.py` — `_handle_aggregation()`

Added detection of `index_subset` patterns in sum domains. When the parser encounters
`sum(arc(np,n), body)`:

1. `_extract_domain_indices` still extracts `["np", "n"]` as iteration indices
2. New code scans `index_list_node` for `index_subset` children, collecting
   `(set_name="arc", child_indices=["np", "n"])`
3. After index expansion, maps the child indices to positions in `expanded_indices`
   and adds to `multidim_set_conditions`
4. The existing `SetMembershipTest` condition generation (Issue #1002) creates
   `Sum(("np", "n"), body, condition=SetMembershipTest("arc", (SymbolRef("np"), SymbolRef("n"))))`

**Result:**
```gams
* Before (wrong — no arc restriction):
nbal(n).. s(n)$(l(n)) + sum((np,n__), t(np,n__)) =E= d(n)$(l(n)) + sum((n__,np), t(n__,np));

* After (correct — arc restriction present):
nbal(n).. s(n)$(l(n)) + sum((np,n__)$(arc(np,n__)), t(np,n__)) =E= d(n)$(l(n)) + sum((n__,np)$(arc(n__,np)), t(n__,np));
```

### Stationarity Fix: Equation-domain-aware positional resolution

**File:** `src/kkt/stationarity.py` — `_replace_indices_in_expr()`

The `SetMembershipTest` positional resolution was blindly using `smt_domain[pos]`
for concrete element values. When a condition like `arc(np, "one")` appeared (where
`"one"` represents the equation domain index `n`), positional resolution mapped
`"one"` → `smt_domain[1]` = `"np"`, producing the incorrect `arc(np, np)`.

**Fix:** Before applying positional resolution, check if the element maps via
`element_to_set` to a set name that is in the `equation_domain`. If so, use that
mapping (which preserves the equation domain binding) instead of the positional
domain resolution.

### Emitter Fix: SymbolRef alias substitution

**File:** `src/emit/expr_to_gams.py` — `resolve_index_conflicts()`

`SymbolRef` nodes inside `SetMembershipTest` conditions were not subject to alias
substitution. When `n` conflicted with the equation domain and was aliased to `n__`
in the sum's index_sets, the condition still had `SymbolRef("n")` instead of
`SymbolRef("n__")`. Added a `SymbolRef` case to `_resolve()` that applies
`active_aliases` substitution.

---

## Verification

- GAMS: MODEL STATUS 1 (Optimal), SOLVER STATUS 1 (Normal), obj = 718.750
- No regressions: dispatch (obj 7.955, matching NLP 7.9546), all 4,206 tests pass
- `stat_t(n,np)` correctly includes `nu_nbal(n)` Jacobian term with `arc(np,n)` condition
- `nbal(n)` correctly restricts sums to valid arcs via `$(arc(...))` conditions

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/parser.py:~4764-4890` | Detect `index_subset` in sum domains, add `SetMembershipTest` |
| `src/kkt/stationarity.py:~1402-1437` | Equation-domain-aware positional resolution for `SetMembershipTest` |
| `src/emit/expr_to_gams.py:~922` | `SymbolRef` alias substitution in `resolve_index_conflicts()` |
