# CGE Models: Alias-Aware Gradient Mismatch (irscge, lrgcge, moncge, stdcge)

**GitHub Issue:** [#1138](https://github.com/jeffreyhorn/nlp2mcp/issues/1138)
**Status:** OPEN
**Severity:** Medium — objective mismatch (1.0%–2.2%)
**Date:** 2026-03-23
**Parent Issue:** #1111 (Alias-Aware Differentiation)
**Affected Models:** irscge, lrgcge, moncge, stdcge

---

## Problem Summary

Four CGE (Computable General Equilibrium) models share the same alias pattern
and exhibit similar small objective mismatches. All use three alias pairs:

```gams
Alias(u, v);
Alias(i, j);
Alias(h, k);
```

These aliases appear throughout the models in SAM (Social Accounting Matrix)
expressions like `sum(k, SAM(k,j))` and `sum(j, F0(k,j))`, where aliased
indices iterate over the same underlying sets.

| Model | NLP Objective | MCP Objective | Rel Diff |
|-------|--------------|--------------|----------|
| irscge | 26.0914 | 25.5080 | 2.2% |
| lrgcge | 25.7679 | 25.5080 | 1.0% |
| moncge | 25.9819 | 25.5080 | 1.8% |
| stdcge | 26.0926 | 25.5080 | 2.2% |

Note: All four converge to the same MCP objective (25.508), suggesting a
systematic gradient error in the shared CGE equation structure.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/irscge.gms -o /tmp/irscge_mcp.gms
gams /tmp/irscge_mcp.gms lo=2
# Objective: 25.508, expected: 26.091

# Same pattern for lrgcge, moncge, stdcge
```

---

## Root Cause Analysis

CGE models have complex equation structures with:

1. **Multi-level nesting**: `sum(j, sum(k, ...))` with aliases at different levels
2. **Conditional sums**: `sum(j$(not gov(j)), ...)` where conditions use aliased sets
3. **CES/Cobb-Douglas functions**: Power functions with aliased index parameters
4. **SAM balance equations**: Bilinear terms like `SAM(i,j)` iterated with aliases

The alias-aware multi-matching fix from Day 3 handles the simple bilinear
case (`sum((i,j), x(i)*A(i,j)*x(j))`), but CGE models use aliases in more
complex patterns:

- `sum(k, F0(k,j))` where `k` aliases `h` — the sum variable is an alias, not
  the matched index
- Nested sums where both the outer and inner variables are aliases
- Dollar-conditioned sums with alias-dependent conditions

### Investigation Steps

1. Generate the MCP for irscge and compare `stat_` equations with hand-derived KKT
2. Identify which specific equation(s) have incorrect gradient terms
3. Check if the gradient error is in the objective gradient or constraint Jacobian
4. Test if fixing one model (irscge) automatically fixes the other three

---

## Files

- `src/ad/derivative_rules.py` — `_partial_collapse_sum`, `_diff_varref`
- `src/kkt/stationarity.py` — `_replace_indices_in_expr`
- `data/gamslib/raw/irscge.gms` — Simplest CGE variant
- `data/gamslib/raw/stdcge.gms` — Standard CGE template

## Current Status (2026-03-30)

- **splcge**: SOLVED — full pipeline success, objective matches reference.
- **camcge**: Compiles but fails $141 — zero-valued param `te(i) = 0` is dropped.
- **cesam2**: Compiles but fails $140 — undeclared loop-scoped params (`sigmay3`, `vbar3`, `wbar3`).

The camcge and cesam2 failures are not alias-related.
