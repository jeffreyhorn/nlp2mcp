# ps3_s_scp: Objective Mismatch — 3-Type Principal-Agent with SCP, Multi-Solve

**GitHub Issue:** [#962](https://github.com/jeffreyhorn/nlp2mcp/issues/962)
**Status:** OPEN
**Model:** ps3_s_scp (GAMSlib SEQ=374)
**Error category:** `objective_mismatch`
**MCP objective:** -0.621
**NLP objective:** -0.607
**Relative difference:** 2.3%

## Description

ps3_s_scp (Parts Supply Problem with 3 Types, Single Crossing Property) is a non-convex NLP (maximization, but with negative objective) variant with SCP constraints. The model uses two sequential solves for warm-starting. The generated MCP solves to Optimal but converges to a different KKT point, with a 2.3% objective mismatch.

## Root Cause

Two contributing factors:

### 1. Multi-Solve Warm-Start

The model defines two sub-models solved sequentially:
```gams
solve SB_gic_wo_SCP maximizing Util using nlp;
solve SB_lic_wo_SCP maximizing Util using nlp;
```

The first solve initializes variable levels for the second. Our pipeline only captures the last model/solve and emits MCP from default initialization.

### 2. Non-Convexity

Same fundamental cause as the ps2/ps3 family: non-convex revenue function with multiple KKT points.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps3_s_scp.gms -o /tmp/ps3_s_scp_mcp.gms
gams /tmp/ps3_s_scp_mcp.gms lo=2
# MCP obj = -0.621

gams data/gamslib/raw/ps3_s_scp.gms lo=2
# NLP obj = -0.607

# 2.3% mismatch
```

## Recommended Fix

Same as ps2_f_s — multi-solve support for warm-starting, plus improved initialization.

## Related Issues

- ps2_f_s: 2-type variant with multi-solve (0.5% mismatch)
- ps3_s, ps3_s_gic: 3-type variants without multi-solve (9.1% mismatch)
- ps3_s_mn, ps10_s: Other variants in the same family
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

See ps2_s — same fix applies across all models in this family.
