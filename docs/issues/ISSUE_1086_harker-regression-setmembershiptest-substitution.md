# harker: Regression — SetMembershipTest Substitution Exposes Index Mapping Bug

**GitHub Issue:** [#1086](https://github.com/jeffreyhorn/nlp2mcp/issues/1086)
**Status:** PARTIALLY FIXED
**Severity:** High — model_optimal regressed to path_solve_terminated
**Progress:** Bug 2 (stat_t arc(n,n) → arc(n,np)) fixed via two changes: (1) sum conditions kept symbolic in `derivative_rules.py`, (2) positional domain resolution for `SetMembershipTest` in `_replace_indices_in_expr`. Bug 3 (nbal parser) remains: `_extract_domain_indices` drops parent set name from `sum(arc(np,n), ...)`, producing `Sum(('np','n'), body)` without `arc` restriction. Model still path_solve_terminated due to nbal empty equations.
**Date:** 2026-03-14
**Affected Models:** harker (SEQ=85, "Spatial Competition")
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
# **** MCP pair nbal.nu_nbal has empty equation but associated variable is NOT fixed
#      nu_nbal(four), nu_nbal(five), nu_nbal(six)
# **** SOLVE from line 178 ABORTED, EXECERROR = 3
```

---

## Root Cause

### Model Structure

harker has a transportation network with 6 nodes:
- `Set n /one*six/` (6 nodes), `alias(n, np)`
- `Set l(n) /one, two, three/` — supply/demand regions
- `Set arc(n,np)` — sparse 2D set defining 14 valid transport arcs
- Equations use conditions like `$arc(n,np)` to restrict to valid arcs
- Two models: `hark` (competitive equilibrium) and `harkoli` (Cournot-Nash oligopoly)

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

### Bug 2: `stat_t` condition `arc(n,n)` instead of `arc(n,np)`

The generated stationarity equation:
```gams
stat_t(n,np).. (...) * 1$(arc(n,n)) - piL_t(n,np) =E= 0;
```

`arc(n,n)` is always FALSE (no self-arcs), so the entire gradient term vanishes, forcing
`piL_t = 0` and removing ALL nonlinear terms (`NON LINEAR N-Z = 0` in model statistics).

### Bug 3: `nbal` equation missing `arc` set restriction in sums

**Generated:**
```gams
nbal(n).. s(n)$(l(n)) + sum((np,n__), t(np,n__)) =E= d(n)$(l(n)) + sum((n__,np), t(n__,np));
```

**Original GAMS:**
```gams
nbal(n).. s(n)$l(n) + sum(arc(np,n), t(arc)) =e= d(n)$l(n) + sum(arc(n,np), t(arc));
```

The parser (`_extract_domain_indices` at line 581 of `parser.py`) discards the parent set
name `arc` when extracting indices from `sum(arc(np,n), ...)`, creating
`Sum(('np', 'n'), body, condition=None)` without the `arc` set restriction. This is a
latent parser bug that was masked because `nbal` wasn't included in the MCP before.

The `nbal` equation generates empty equations for non-region nodes (`four`, `five`, `six`)
where the paired `nu_nbal` variables are not fixed, triggering `EXECERROR = 3`.

---

## Suggested Fix

**Fix 1 (Critical — stat_t condition):** In `_replace_indices_in_expr` in
`src/kkt/stationarity.py`, add position-aware handling for `SetMembershipTest` when the
flat `element_to_set` mapping is ambiguous. Use the set's declared domain (`arc` has domain
`(n, np)`) to correctly resolve position 0 → `n`, position 1 → `np`.

**Fix 2 (Parser — nbal sum domain):** In `_extract_domain_indices` in `src/ir/parser.py`,
when processing `sum(arc(np,n), ...)`, preserve the parent set name and generate a
`SetMembershipTest` condition: `Sum(('np',), body, condition=SetMembershipTest('arc', (...)))`.
Recognize that when a sum index matches an equation domain variable (e.g., `n` in `nbal(n)`),
it's a filter, not a new iteration variable.

**Fix 3 (nbal multiplier):** If `nu_nbal` instances for non-region nodes remain empty after
Fix 2, add `.fx = 0` statements for `nu_nbal(n)$(not l(n))`.

**Alternative:** Revert `SetMembershipTest` handling in `_apply_index_substitution` to
pre-PR-#1083 behavior and find an alternative way to handle the uimp case.

---

## Files to Modify

| File | Change |
|------|--------|
| `src/ad/derivative_rules.py:2114-2121` | Fix SetMembershipTest index substitution |
| `src/kkt/stationarity.py` | Use positional domain info in `_replace_indices_in_expr` |
| `src/ir/parser.py:581` | Preserve parent set in `_extract_domain_indices` for sum domains |
