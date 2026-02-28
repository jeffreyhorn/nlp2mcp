# ps3_s_gic: Objective Mismatch — 3-Type Principal-Agent with Generalized IC

**GitHub Issue:** [#961](https://github.com/jeffreyhorn/nlp2mcp/issues/961)
**Status:** OPEN
**Model:** ps3_s_gic (GAMSlib SEQ=371)
**Error category:** `objective_mismatch`
**MCP objective:** 1.056
**NLP objective:** 1.162
**Relative difference:** 9.1%

## Description

ps3_s_gic (Parts Supply Problem with 3 Types, Second-Best with Generalized Incentive Compatibility) is a non-convex NLP (maximization) variant of ps3_s. It uses generalized IC constraints that pair all types against all others. The generated MCP solves to Optimal but converges to a different KKT point, with a 9.1% objective mismatch — identical to ps3_s.

## Root Cause

Same as ps3_s: non-convex revenue function `b(i) =E= x(i)**0.5` with a 3×3 IC constraint space creates multiple KKT points. The MCP solver converges to a suboptimal stationary point from default initialization.

Single solve statement — no warm-start:
```gams
solve SB_gic maximizing Util using nlp;
```

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps3_s_gic.gms -o /tmp/ps3_s_gic_mcp.gms
gams /tmp/ps3_s_gic_mcp.gms lo=2
# MCP obj = 1.056

gams data/gamslib/raw/ps3_s_gic.gms lo=2
# NLP obj = 1.162

# 9.1% mismatch
```

## Recommended Fix

Same as ps2_s/ps3_s — improved initialization or multi-start MCP solving.

## Related Issues

- ps3_s: Same 3-type model without generalized IC (same 9.1% mismatch)
- ps2_s, ps2_f_s, ps3_s_scp, ps3_s_mn, ps10_s: Same model family
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

See ps2_s — same fix applies across all models in this family.
