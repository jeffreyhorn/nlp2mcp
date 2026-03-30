# kand: Alias-Aware Gradient Mismatch — Tree Structure with Alias(n,nn)

**GitHub Issue:** [#1141](https://github.com/jeffreyhorn/nlp2mcp/issues/1141)
**Status:** OPEN
**Severity:** High — objective mismatch (92.5%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** kand

---

## Problem Summary

The kand model (Kandler's Structural Optimization) uses a tree structure with
aliased node indices:

```gams
Alias(n, nn);
```

The model has a 92.5% objective mismatch — among the largest in the alias
mismatch group — suggesting that the gradient computation is severely broken
for this model's alias pattern.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| kand | 2613 | 195 | 92.5% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/kand.gms -o /tmp/kand_mcp.gms
gams /tmp/kand_mcp.gms lo=2
# Objective: ~195, expected: ~2613
```

---

## Root Cause Analysis

The kand model uses `Alias(n, nn)` with tree-structured constraints that
reference both `n` and `nn` in equations like:

```gams
balance(n).. sum(nn$arc(n,nn), flow(n,nn)) =e= demand(n);
```

The alias `nn` iterates over the same set as `n` but represents a different
role (child/neighbor node in the tree). The AD engine likely fails to:

1. **Correctly differentiate `flow(n,nn)` w.r.t. `flow`**: The multi-dimensional
   variable with aliased indices at different positions requires position-aware
   index matching.

2. **Preserve alias semantics in `_replace_indices_in_expr`**: When the same
   concrete element (e.g., 'node1') maps to both `n` and `nn`, the flat
   `element_to_set` mapping cannot disambiguate which domain position is
   intended.

3. **Handle arc-set restrictions**: The `$arc(n,nn)` condition on the sum uses
   a 2D set membership test with aliased indices.

### Investigation Steps

1. Generate the MCP and inspect stationarity equations for `stat_flow`
2. Check if the `SetMembershipTest` condition `arc(n,nn)` is correctly
   translated after sum collapse
3. Compare with hand-derived KKT for the tree balance constraints
4. Test if the harker model's similar bug (arc(n,np) → arc(n,n)) also
   affects kand

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`, `_build_element_to_set_mapping`
- `data/gamslib/raw/kand.gms` — Source model

## Current Status (2026-03-30)

Translates and solves to Optimal but objective does not match the NLP reference. Same alias differentiation root cause as qabel/abel (#1137): `_alias_match` in `derivative_rules.py` incorrectly handles alias-bound indices in sum contexts.
