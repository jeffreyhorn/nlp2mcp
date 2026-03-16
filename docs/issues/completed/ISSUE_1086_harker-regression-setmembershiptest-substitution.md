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

The harker model regressed from model_optimal to path_solve_terminated due to multiple interacting bugs in the parser, AD, stationarity builder, and emitter:

1. **Bug 2 (stat_t condition)**: `SetMembershipTest` index substitution in
   `_replace_indices_in_expr` mapped concrete element values using positional domain
   resolution, producing `arc(n,n)` instead of `arc(n,np)`. Previously fixed.

2. **Bug 3 (nbal parser)**: `_extract_domain_indices` in `src/ir/parser.py` discarded
   the parent set name `arc` from `sum(arc(np,n), ...)`, producing `Sum(('np','n'), body)`
   without the `arc` set restriction.

3. **Bug 4 (AD single-index sum)**: For `Sum(("np",), body, arc(np,n))` with single
   iteration index, the AD's `_partial_index_match` greedy matching always tried
   position 0 first, missing non-zero derivatives when the sum variable matched at
   a later position in the body VarRef.

4. **Bug 5 (dimension-mismatch Jacobian)**: When a 1D equation `nbal(n)` contributes
   to a 2D variable `t(n,np)`, the stationarity builder had three sub-bugs:
   - `_compute_index_offset_key` collapsed all entries into one group `(0,0)`,
     losing distinct contribution patterns
   - `_add_indexed_jacobian_terms` used a single representative per group
   - `MultiplierRef` always used equation domain `("n",)`, never `("np",)` for
     the entry where the equation index aligned with variable position 1

5. **Bug 6 (condition substitution for dim-mismatch)**: The constraint element mapping
   mapped equation indices to equation domain names (e.g., `five→n`), not to the
   correct variable domain name at the matched position (`five→np` for position 1).
   Also, sum iteration aliases (e.g., `np`) passed through unchanged instead of being
   remapped to the appropriate variable domain name.

---

## Fixes Applied

### Parser Fix: Preserve index_subset set restriction + filter equation-domain indices

**File:** `src/ir/parser.py` — `_handle_aggregation()`

Added detection of `index_subset` patterns in sum domains. When the parser encounters
`sum(arc(np,n), body)`:

1. Scans `index_list_node` for `index_subset` children, collecting
   `(set_name="arc", child_indices=["np", "n"])`
2. Generates `SetMembershipTest("arc", ...)` conditions
3. Filters equation-domain indices from Sum's index_sets so only the free
   iteration variable is in the Sum (e.g., `Sum(("np",), body, arc(np,n))`)

### AD Fix: Try all candidate positions for single-index sums

**File:** `src/ad/derivative_rules.py` — Sum differentiation

For single-index sums where `wrt_indices` has more dimensions than `index_sets`,
instead of greedy first-match, try ALL candidate positions and return the first
non-zero derivative. This handles cases like `sum(np, t(np,n))` w.r.t. `t("three","four")`
where `np` (alias of `n`) could match at either position.

### Stationarity Fix: Dimension-mismatch Jacobian grouping and multiplier construction

**File:** `src/kkt/stationarity.py`

1. **`_compute_index_offset_key`**: For dimension-mismatch cases (eq dims < var dims),
   use sentinel value 999 at unmatched variable positions. This creates separate groups
   for entries where the equation index maps to different variable positions.

2. **`_add_indexed_jacobian_terms`**: For dimension-mismatch groups:
   - Prefer representative entries with distinct variable indices (avoid `t(five,five)`
     where both positions have the same value, causing key collisions in override dict)
   - Build constraint element mapping from variable indices (not equation domain),
     mapping concrete elements to the correct variable domain names
   - Remap sum iteration aliases (e.g., `np`) to the variable domain name at the
     unmatched position
   - Build `MultiplierRef` with variable domain names at matched positions

3. **`_replace_indices_in_expr`**: Equation-domain-aware positional resolution for
   `SetMembershipTest` indices — if an element maps to a set in the equation domain,
   use that mapping instead of positional resolution.

### Emitter Fix: SymbolRef alias substitution

**File:** `src/emit/expr_to_gams.py` — `resolve_index_conflicts()`

Added `SymbolRef` case to `_resolve()` that applies `active_aliases` substitution,
so conditions use the correct aliased index names.

---

## Verification

- GAMS: MODEL STATUS 1 (Optimal), SOLVER STATUS 1 (Normal)
- KKT conditions verified manually: stationarity, complementarity, and primal
  feasibility all satisfied at the MCP solution point
- The MCP and NLP may converge to different KKT points (expected for nonconvex models)
- No regressions: dispatch (obj 7.955), all 4,206 tests pass
- `stat_t(n,np)` correctly includes BOTH `nu_nbal(n)` and `nu_nbal(np)` Jacobian
  terms with correct `arc(n,np)` conditions
- `nbal(n)` correctly restricts sums to valid arcs via `$(arc(...))` conditions

---

## Files Modified

| File | Change |
|------|--------|
| `src/ir/parser.py:~4764-4890` | Detect `index_subset` in sum domains, filter eq-domain indices from Sum |
| `src/ad/derivative_rules.py:~1635-1662` | Try all candidate positions for single-index sum differentiation |
| `src/kkt/stationarity.py:~2267-2283` | Sentinel-based offset key for dimension-mismatch grouping |
| `src/kkt/stationarity.py:~2501-2552` | Dimension-mismatch element mapping and alias remapping |
| `src/kkt/stationarity.py:~2585-2600` | Dimension-mismatch multiplier with variable domain names |
| `src/kkt/stationarity.py:~1402-1437` | Equation-domain-aware positional resolution for SetMembershipTest |
| `src/emit/expr_to_gams.py:~922` | `SymbolRef` alias substitution in `resolve_index_conflicts()` |
