# harker: Regression — SetMembershipTest Substitution Exposes Index Mapping Bug

**GitHub Issue:** [#1086](https://github.com/jeffreyhorn/nlp2mcp/issues/1086)
**Status:** OPEN
**Severity:** High — model_optimal regressed to path_solve_terminated
**Date:** 2026-03-14
**Affected Models:** harker
**Regressing PR:** #1083 (Sprint 22 Day 9)

---

## Problem Summary

The harker model (GAMSlib SEQ=108, "Spatial Price Equilibrium") regressed from
model_optimal to path_solve_terminated after PR #1083 added `_apply_index_substitution`
handling for `SetMembershipTest` nodes.

Before PR #1083, `arc(n,np)` conditions were preserved as symbolic after sum collapse.
After the change, `SetMembershipTest` indices get substituted to concrete values (e.g.,
`arc(five,five)`), then `_replace_indices_in_expr` maps both `five` → `n` using the flat
`element_to_set` mapping, producing `arc(n,n)` instead of the correct `arc(n,np)`.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/harker.gms -o /tmp/harker_mcp.gms
gams /tmp/harker_mcp.gms lo=2
# PATH solver reports system failure / solve terminated
```

---

## Root Cause

### Model Structure

harker has a transportation network with:
- `Set n /one*five/` (5 nodes), `alias(n, np)`
- `Set arc(n,np)` — sparse 2D set defining valid arcs between nodes
- Equations use conditions like `$arc(n,np)` to restrict to valid arcs

### The Bug

When the stationarity builder processes constraint Jacobian entries, it substitutes
concrete element values back to symbolic set names. The `element_to_set` mapping is flat:
```python
{"five": "n", "four": "n", ...}
```

Before PR #1083, `SetMembershipTest` was not touched by `_apply_index_substitution`, so
`arc(n,np)` remained symbolic after sum collapse. The `_replace_indices_in_expr` function
then correctly preserved it.

After PR #1083, `_apply_index_substitution` substitutes `SetMembershipTest` indices:
- `arc(n, np)` with substitution `{np: "five"}` → `arc(n, five)`
- `_replace_indices_in_expr` then maps `five` → `n` (from flat mapping)
- Result: `arc(n, n)` — **wrong** (should be `arc(n, np)`)

This means the condition `arc(n,n)` only allows diagonal arcs (a node to itself), which
doesn't match any arc in the model. The stationarity equations become structurally wrong,
and PATH cannot solve the system.

### Additional Issue

The `nbal` equation now appears in the MCP (previously absent), likely also related to the
stationarity builder changes. This further distorts the system structure.

---

## Suggested Fix

**Option A (Recommended):** In `_replace_indices_in_expr`, when a multi-index expression
like `SetMembershipTest("arc", ("five", "five"))` is encountered, use positional domain
information to distinguish which occurrence maps to which set alias. The `arc` set has
domain `(n, np)`, so position 0 maps to `n` and position 1 maps to `np`.

**Option B:** Don't substitute `SetMembershipTest` indices in `_apply_index_substitution`
when the substitution would collapse distinct alias indices to the same concrete value.
Detect when multiple positions in the set's domain are aliases of the same underlying set
and preserve the symbolic names.

**Option C:** Revert `SetMembershipTest` handling in `_apply_index_substitution` to the
pre-PR-#1083 behavior (don't substitute), and find an alternative way to handle the uimp
case that motivated the change.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py:2114-2121` | Fix SetMembershipTest index substitution |
| `src/kkt/stationarity.py` | Use positional domain info in `_replace_indices_in_expr` |
