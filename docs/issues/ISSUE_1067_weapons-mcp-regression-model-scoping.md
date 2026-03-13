# weapons: MCP Regression — Locally Infeasible After Model Equation Scoping

**GitHub Issue:** [#1067](https://github.com/jeffreyhorn/nlp2mcp/issues/1067)
**Model:** weapons (SEQ=18) — Weapons Assignment
**Type:** NLP
**Category:** Regression (was model_optimal, now model_infeasible)

---

## Summary

The weapons model regressed from model_optimal (model_status=1) to locally infeasible (model_status=5, 22662 iterations) during Sprint 22. The root cause is PR #1037's model equation scoping fix, which correctly restricts equations to the solved model `war` but removes intermediate variable `prob(t)` and its chain-rule multipliers that were essential for PATH solver convergence.

## Reproduction

```bash
# Current MCP (infeasible)
cd /tmp && gams /path/to/data/gamslib/mcp/weapons_mcp.gms lo=2 o=weapons.lst
# Expected: MODEL STATUS 5 (Locally Infeasible), 22662 iterations

# Baseline MCP (working, commit 53ac5979)
git show 53ac5979:data/gamslib/mcp/weapons_mcp.gms > /tmp/weapons_baseline.gms
cd /tmp && gams weapons_baseline.gms lo=2 o=weapons_baseline.lst
# Expected: MODEL STATUS 1 (Optimal), obj=1361.557
```

## Model Structure

The original GAMS model defines two formulations:
```gams
Model war  'traditional'  / maxw, minw, etd         /;
Model warp 'extended'     / maxw, minw, probe, etdp /;
solve war maximizing tetd using nlp;
```

- `war` uses `etd`: `tetd =E= sum(t, mv(t)*(1 - prod(w$td(w,t), (1-td(w,t))^x(w,t))))`
- `warp` uses `probe(t)` as an intermediate: `prob(t) =E= 1 - prod(w$td(w,t), ...)` and `tetd =E= sum(t, mv(t)*prob(t))`

The solve uses model `war` (3 equations: maxw, minw, etd).

## Root Cause

**PR #1037** (model equation scoping, commit `2da2827a`) correctly restricts KKT generation to the `war` model's equations only. This excludes `probe(t)` and `etdp` from model `warp`, which removes:

- `prob(t)` as a primal variable
- `nu_probe(t)` free multiplier (chain-rule term)
- `nu_etd` free multiplier
- `stat_prob(t)` stationarity equation

### Structural Difference

| Element | Baseline (working) | Current (broken) |
|---------|-------------------|------------------|
| `prob(t)` variable | Present | Removed |
| `nu_probe(t)` multiplier | Present | Removed |
| `stat_x` gradient | Chain through `nu_probe(t)` | Direct product differentiation |
| MCP size | 6 equation types, 6 variable types | 5 equation types, 5 variable types |

### Stationarity Equation Change

**Baseline** (chain through `prob`):
```gams
stat_x(w,t)$(td(w,t))..
    prod(...) * sum(...log...) * nu_probe(t)
  + (-1)*(mv(t)*(-1)*prod(...)*sum(...log...)) * nu_etd
  + td(w,t)*lam_maxw(w) + ... =E= 0;
```

**Current** (direct differentiation):
```gams
stat_x(w,t)$(td(w,t))..
    (-1)*(mv(t)*(-1)*(prod(...)*sum(...log...)))
  + td(w,t)*lam_maxw(w) + ... - piL_x(w,t) =E= 0;
```

The decomposed gradient through `prob(t)` was numerically better-conditioned for PATH than the monolithic product-of-sums derivative.

## PATH Solver Output

```
FINAL POINT STATISTICS
Maximum of X. . . . . . . . . .  1.7290e+03 var: (tetd)
Maximum of F. . . . . . . . . .  3.9627e+01 eqn: (comp_minw('20'))
```

Maximum residual: 39.627, indicating PATH could not converge. NLP reference obj = 1735.57; MCP reached obj = 1728.97 (close but infeasible).

## Potential Fixes

1. **Automatic intermediate variable introduction**: When differentiating complex nested expressions (product of sums with exponentials), detect when introducing an auxiliary variable would decompose the gradient chain and improve conditioning.
2. **Prefer extended model formulation**: When the source has an equivalent model with decomposed intermediates, prefer it for KKT derivation.
3. **NLP warm-start**: Initialize MCP variables from the NLP solution to give PATH a better starting point.
4. **Accept as known limitation**: Note that even the baseline obj (1361) was far from the NLP reference (1735), suggesting PATH had convergence difficulties even with the decomposed form.

## Files

- `data/gamslib/raw/weapons.gms` — original NLP
- `data/gamslib/mcp/weapons_mcp.gms` — current (broken) MCP
- Baseline MCP: `git show 53ac5979:data/gamslib/mcp/weapons_mcp.gms`
