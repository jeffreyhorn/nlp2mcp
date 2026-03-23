# PS-Family: Alias-Aware Gradient Mismatch in Stochastic Programming Models

**GitHub Issue:** [#1140](https://github.com/jeffreyhorn/nlp2mcp/issues/1140)
**Status:** OPEN
**Severity:** Medium-High — objective mismatch (0.5%–27.4%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s

---

## Problem Summary

Seven stochastic programming models from the "Progressive Hedging" family share a
common alias pattern with `Alias(i,j)` used in scenario-coupling constraints.
All models solve successfully as MCP but produce objective mismatches ranging from
0.5% to 27.4%.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| ps2_f_s | 0.865 | 0.861 | 0.5% |
| ps2_s | 0.865 | 0.861 | 0.5% |
| ps3_s | 1.162 | 1.056 | 9.1% |
| ps3_s_gic | 1.162 | 1.056 | 9.1% |
| ps3_s_mn | 1.052 | 1.029 | 2.2% |
| ps3_s_scp | -0.607 | -0.617 | 1.6% |
| ps10_s | 0.533 | 0.387 | 27.4% |

The larger models (ps10_s with 10 scenarios) show larger mismatches, suggesting
the error compounds with the number of aliased-index terms.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps2_s.gms -o /tmp/ps2_s_mcp.gms
gams /tmp/ps2_s_mcp.gms lo=2
# Objective: 0.861, expected: 0.865

python -m src.cli data/gamslib/raw/ps10_s.gms -o /tmp/ps10_s_mcp.gms
gams /tmp/ps10_s_mcp.gms lo=2
# Objective: 0.387, expected: 0.533
```

---

## Root Cause Analysis

The PS-family models use aliases for scenario coupling, e.g.:

```gams
Alias(i, j);
Set bundle(i,j) "scenario bundles";
```

Equations use `sum(j$bundle(i,j), ...)` patterns where `j` is an alias of `i`.
The AD engine's `_partial_collapse_sum` and `_diff_varref` may produce incorrect
gradients when aliased indices appear in cross-scenario coupling terms.

### Potential Issues

1. **Index order mismatch in `_partial_collapse_sum`**: The fallback matching
   builds `symbolic_wrt` in sum-index-set order rather than wrt-indices order
   (same root cause as qabel — see #1089).

2. **Alias resolution in `_diff_varref`**: When VarRef indices use an alias
   (e.g., `x(j)` where `Alias(i,j)`), the exact tuple comparison
   `expr.indices == wrt_indices` fails because `('j',) != ('i',)`.

3. **Cross-scenario terms**: The coupling constraints link variables across
   scenarios using aliased index pairs, producing bilinear-like gradient terms
   that require the multi-matching enumeration from PR #1136.

### Investigation Steps

1. Generate MCP for ps2_s (smallest model) and compare `stat_x(i)` with
   hand-derived KKT conditions
2. Check if fixing the qabel index-order bug (#1089) also reduces PS mismatches
3. Verify whether the multi-matching fix from PR #1136 helps
4. Test ps10_s to see if the error scales with model size

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/ps2_s.gms` — Simplest PS variant (2 scenarios)
- `data/gamslib/raw/ps10_s.gms` — Largest PS variant (10 scenarios)
