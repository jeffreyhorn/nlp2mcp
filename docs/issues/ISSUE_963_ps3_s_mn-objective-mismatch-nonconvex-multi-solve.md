# ps3_s_mn: Objective Mismatch — 3-Type Principal-Agent with Monotone Non-Decreasing, Multi-Solve

**GitHub Issue:** [#963](https://github.com/jeffreyhorn/nlp2mcp/issues/963)
**Status:** OPEN
**Model:** ps3_s_mn (GAMSlib SEQ=373)
**Error category:** `objective_mismatch`
**MCP objective:** 1.029
**NLP objective:** 1.052
**Relative difference:** 2.2%

## Description

ps3_s_mn (Parts Supply Problem with 3 Types, Monotone Non-Decreasing) is a non-convex NLP (maximization) variant with additional monotonicity constraints. The model uses three sequential solves for warm-starting. The generated MCP solves to Optimal but converges to a different KKT point, with a 2.2% objective mismatch.

## Root Cause

Two contributing factors:

### 1. Multi-Solve Warm-Start (3 sequential solves)

The model solves the same model three times sequentially:
```gams
solve SB4 maximizing Util using nlp;
solve SB4 maximizing Util using nlp;
solve SB4 maximizing Util using nlp;
```

Each successive solve uses the previous solution as a starting point, progressively refining toward the global optimum. Our pipeline only captures one solve and emits MCP from default initialization.

### 2. Non-Convexity

Same fundamental cause as the ps2/ps3 family: non-convex revenue function with multiple KKT points. The model includes additional monotonicity constraints (`mn(i)`) that add lead/lag expressions.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps3_s_mn.gms -o /tmp/ps3_s_mn_mcp.gms
gams /tmp/ps3_s_mn_mcp.gms lo=2
# MCP obj = 1.029

gams data/gamslib/raw/ps3_s_mn.gms lo=2
# NLP obj = 1.052

# 2.2% mismatch
```

## Recommended Fix

Same as ps2_f_s — multi-solve support for warm-starting, plus improved initialization. The triple-solve pattern in this model highlights the need for iterative refinement.

## Related Issues

- ps2_f_s, ps3_s_scp: Other multi-solve variants in this family
- ps3_s, ps3_s_gic: Single-solve variants (9.1% mismatch)
- ps10_s: 10-type variant (27.4% mismatch)
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

See ps2_s — same fix applies across all models in this family.
