# qabel/abel: Alias-Aware Gradient Still Incomplete for Quadratic Forms

**GitHub Issue:** [#1137](https://github.com/jeffreyhorn/nlp2mcp/issues/1137)
**Status:** OPEN
**Severity:** High — objective mismatch (qabel: 8.9%, abel: 29.8%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** qabel, abel

---

## Problem Summary

The qabel and abel models use aliased indices in quadratic forms:

```gams
Alias(n, np);
Alias(m, mp);
Variable x(n,k);
obj.. z =e= 0.5 * sum((k,n,np), (x(n,k)-xtilde(n,k))*w(n,np,k)*(x(np,k)-xtilde(np,k)))
           + 0.5 * sum((ku,m,mp), (u(m,ku)-utilde(m,ku))*lambda(m,mp)*(u(mp,ku)-utilde(mp,ku)));
```

Sprint 23 Day 3 (PR #1136) implemented multi-matching enumeration in
`_partial_collapse_sum` which correctly produces both collapse paths for the
bilinear cross-term. However, the models still mismatch, suggesting the fix
is necessary but not sufficient.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| qabel | 46,965.04 | 51,133.49 | 8.9% |
| abel | 225.19 | 158.15 | 29.8% |

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/qabel.gms -o /tmp/qabel_mcp.gms
gams /tmp/qabel_mcp.gms lo=2
# MCP solves but objective = 51133.49, expected NLP = 46965.04

python -m src.cli data/gamslib/raw/abel.gms -o /tmp/abel_mcp.gms
gams /tmp/abel_mcp.gms lo=2
# MCP solves but objective = 158.15, expected NLP = 225.19
```

---

## Root Cause Analysis

### What Was Fixed (Day 3)

The multi-matching enumeration in `_partial_collapse_sum` correctly handles the
inner quadratic sum `sum((k,n,np), ...)`. For `d/d(x(consumpt,q1))`, both
matchings (n→consumpt and np→consumpt) are enumerated and their derivatives
summed, producing the correct `(W + W^T)x` gradient structure.

### What Remains Broken

The residual mismatch likely comes from one or more of:

1. **Stationarity equation condition propagation**: The `stateq` equation has
   condition `$(ord(k) <= card(k) - 1)` and uses `x(n,k+1)`. The lead/lag
   domain restrictions may not propagate correctly when aliased indices are
   involved in the gradient terms.

2. **Cross-equation gradient terms**: The `stat_x(n,k)` equation combines
   gradients from multiple constraints. The `nu_stateq` multiplier terms use
   lead/lag (`k+1`, `k-1`) with aliased indices — the interaction between
   alias renaming and index offset substitution may produce incorrect terms.

3. **`_replace_indices_in_expr` edge cases**: The Day 3 fix protects Sum
   index variables, but other expression nodes containing renamed indices
   (e.g., DollarConditional, IndexOffset) may still be incorrectly processed.

### Investigation Steps

1. Compare the full `stat_x` equation output with the hand-derived KKT conditions
2. Check if `nu_stateq(n+1,k)` and `nu_stateq(n-1,k)` terms are correctly generated
3. Verify the `stateq` equality equation is correctly emitted with alias handling
4. Run finite difference validation on the MCP gradient for specific variable instances

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_enumerate_matchings`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`, `_replace_matching_indices`
- `src/emit/equations.py` — `_collect_ad_generated_aliases`
- `data/gamslib/raw/qabel.gms` — Source model
- `data/gamslib/raw/abel.gms` — Source model (variant of qabel)

## Current Status (2026-03-30)

Both abel and qabel translate and solve to MODEL STATUS 1 Optimal, but objective values do not match the NLP reference. The alias differentiation in quadratic forms produces incorrect KKT conditions. Root cause identified: `_alias_match` in `derivative_rules.py` incorrectly handles alias-bound indices in sum contexts.
