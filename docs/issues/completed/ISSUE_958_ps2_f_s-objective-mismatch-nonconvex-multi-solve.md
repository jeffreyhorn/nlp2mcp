# ps2_f_s: Objective Mismatch — Non-Convex Principal-Agent Model with Multi-Solve Warm-Start

**GitHub Issue:** [#958](https://github.com/jeffreyhorn/nlp2mcp/issues/958)
**Status:** WON'T FIX — Expected behavior for non-convex models (multiple KKT points)
**Model:** ps2_f_s (GAMSlib SEQ=358)
**Error category:** `objective_mismatch`
**MCP objective:** 0.861
**NLP objective:** 0.865
**Relative difference:** 0.5%

## Description

ps2_f_s (Parts Supply Problem with 2 Types, First-Best and Second-Best) is a non-convex NLP (maximization) that models adverse selection in contract theory. The generated MCP solves to Optimal but finds a different KKT point than the NLP solver, producing a 0.5% objective mismatch.

## Root Cause

Two contributing factors:

### 1. Multi-Solve Warm-Start (Primary)

The original model defines two sub-models solved sequentially:
```gams
Model
   FB1 / obj, rev, pc     /
   SB1 / obj, rev, pc, ic /;

solve FB1 maximizing Util using nlp;
solve SB1 maximizing Util using nlp;
```

The first solve (FB1, first-best without incentive compatibility constraints) initializes variable levels that warm-start the second solve (SB1, second-best with IC). Our pipeline only captures the last model/solve (SB1) and emits MCP from default initialization, missing the warm-start that guides the NLP solver to the correct local optimum.

### 2. Non-Convexity (Fundamental)

The model contains non-convex terms (`x(i)**0.5` in the revenue function). Multiple KKT points exist. Without warm-starting, the MCP solver (PATH) converges to a valid but suboptimal stationary point.

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/ps2_f_s.gms -o /tmp/ps2_f_s_mcp.gms

# Solve MCP (finds obj = 0.861)
gams /tmp/ps2_f_s_mcp.gms lo=2

# Solve original NLP (finds obj = 0.865)
gams data/gamslib/raw/ps2_f_s.gms lo=2

# Compare: MCP 0.861 vs NLP 0.865 (0.5% mismatch)
```

## Key Differences (MCP vs NLP)

| Variable | MCP | NLP |
|----------|-----|-----|
| x(inf) | 2.778 | 2.367 |
| w(inf) | 0.833 | 0.710 |
| b(inf) | 1.667 | 1.538 |
| Util | 0.861 | 0.865 |

## Recommended Fix

1. **Multi-solve support:** Implement sequential solve handling — when multiple `solve` statements exist, either:
   - Solve the first model (NLP/LP) to initialize variables, then emit MCP for the last solve
   - Capture `.l` values from earlier solves as initial points in the MCP
2. **Better initialization heuristic:** For non-convex models, use mid-point initialization or multiple start points

## Related Issues

- ps2_s: Same model family, single solve (no warm-start), same 0.5% mismatch
- ps3_s, ps3_s_gic, ps3_s_scp, ps3_s_mn, ps10_s: Same principal-agent model family with varying types and constraints
- #942: Empty diagonal complementarity (RESOLVED — was a secondary blocker for these models)
- #943: Dollar-conditioned complementarity (RESOLVED — was a secondary blocker for these models)

## Estimated Effort

Multi-solve support: ~6-8h (requires parser changes to track multiple model/solve pairs, plus a mini-NLP solver or sequential emit strategy)
