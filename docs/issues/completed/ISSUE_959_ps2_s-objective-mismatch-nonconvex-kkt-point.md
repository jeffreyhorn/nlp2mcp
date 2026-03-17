# ps2_s: Objective Mismatch — Non-Convex Principal-Agent Model, Multiple KKT Points

**GitHub Issue:** [#959](https://github.com/jeffreyhorn/nlp2mcp/issues/959)
**Status:** WON'T FIX — Expected behavior for non-convex models (multiple KKT points)
**Model:** ps2_s (GAMSlib SEQ=362)
**Error category:** `objective_mismatch`
**MCP objective:** 0.861
**NLP objective:** 0.865
**Relative difference:** 0.5%

## Description

ps2_s (Parts Supply Problem with 2 Types, Second-Best only) is a non-convex NLP (maximization) that models adverse selection in contract theory. The generated MCP solves to Optimal but converges to a different KKT point than the NLP solver, producing a 0.5% objective mismatch.

Unlike ps2_f_s, this model has only a single solve statement — no multi-solve warm-start. The mismatch is purely due to non-convexity and the MCP solver finding a different valid stationary point.

## Root Cause

### Non-Convexity with Multiple KKT Points

The revenue function `b(i) =E= x(i)**0.5` introduces non-convexity. The KKT conditions have multiple solutions. The NLP solver (CONOPT/IPOPT) and MCP solver (PATH) use different algorithms and starting points, converging to different local optima.

The model structure:
```gams
obj..     Util =e= sum(i, p(i)*(b(i) - w(i)));
rev(i)..  b(i) =e= x(i)**(0.5);
pc(i)..   w(i) - theta(i)*x(i) =g= ru;
ic(i,j).. w(i) - theta(i)*x(i) =g= w(j) - theta(i)*x(j);
```

The IC constraint `ic(i,j)` with `Alias(i,j)` creates a combinatorial structure where multiple binding patterns satisfy the KKT conditions.

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ps2_s.gms -o /tmp/ps2_s_mcp.gms

# Solve MCP (finds obj = 0.861)
gams /tmp/ps2_s_mcp.gms lo=2

# Solve original NLP (finds obj = 0.865)
gams data/gamslib/raw/ps2_s.gms lo=2

# Compare: MCP 0.861 vs NLP 0.865 (0.5% mismatch)
```

## Key Differences (MCP vs NLP)

| Variable | MCP | NLP |
|----------|-----|-----|
| x(eff) | 6.250 | 6.250 |
| x(inf) | 2.778 | 2.367 |
| w(eff) | 1.528 | 1.487 |
| w(inf) | 0.833 | 0.710 |
| Util | 0.861 | 0.865 |

Both solutions have `lam_ic(eff,inf) = 0.2` (IC for efficient type binding), confirming the same constraint is active but at different primal values.

## Recommended Fix

1. **Improved initialization:** Use midpoint or bounds-based heuristic for starting point
2. **Multi-start MCP solving:** Try multiple initial points and select the best objective
3. **NLP warm-start option:** Allow users to provide `.l` values from a prior NLP solve

## Related Issues

- ps2_f_s: Same model with additional first-best warm-start solve
- ps3_s, ps3_s_gic, ps3_s_scp, ps3_s_mn, ps10_s: Same model family
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

Initialization heuristic: ~2-3h; Multi-start: ~4-6h
