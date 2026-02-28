# ps10_s: Objective Mismatch — Non-Convex 10-Type Principal-Agent Model

**GitHub Issue:** [#964](https://github.com/jeffreyhorn/nlp2mcp/issues/964)
**Status:** OPEN
**Model:** ps10_s (GAMSlib SEQ=380)
**Error category:** `objective_mismatch`
**MCP objective:** 0.387
**NLP objective:** 0.533
**Relative difference:** 27.4%

## Description

ps10_s (Parts Supply Problem with 10 Types, Second-Best) is a non-convex NLP (maximization) modeling adverse selection with 10 supplier types. The generated MCP solves to Optimal but converges to a significantly different KKT point, with the largest mismatch (27.4%) in the principal-agent model family.

The mismatch grows with the number of types: ps2 (0.5%), ps3 (2-9%), ps10 (27.4%). This is expected — the IC constraint space grows quadratically (10×10 = 100 constraints) creating exponentially more local optima.

## Root Cause

### Non-Convexity with Many KKT Points

Same fundamental cause as ps2_s/ps3_s but amplified by scale:
- Set `i / 0*9 /` (10 types)
- `ic(i,j)` creates 10×10 = 100 IC constraints (90 off-diagonal)
- `licd(i)`, `licu(i)` add 9+9 lead/lag constraints
- Revenue function `b(i) =E= x(i)**0.5` is non-convex

Single solve statement — no warm-start:
```gams
solve SB_lic maximizing Util using nlp;
```

The combinatorial explosion of binding constraint patterns makes it very unlikely that the MCP solver will find the same KKT point as the NLP solver from default initialization.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps10_s.gms -o /tmp/ps10_s_mcp.gms
gams /tmp/ps10_s_mcp.gms lo=2
# MCP obj = 0.387

gams data/gamslib/raw/ps10_s.gms lo=2
# NLP obj = 0.533

# 27.4% mismatch
```

## Recommended Fix

Same as the ps2/ps3 family — improved initialization or multi-start. However, for 10-type models, multi-start may be expensive. Better initialization heuristics (e.g., bounds-based or analytic starting points for mechanism design problems) may be more practical.

## Related Issues

- ps2_s, ps2_f_s: 2-type variants (0.5% mismatch)
- ps3_s, ps3_s_gic, ps3_s_scp, ps3_s_mn: 3-type variants (2-9% mismatch)
- #942, #943: Previously blocking .fx emission issues (RESOLVED)

## Estimated Effort

See ps2_s — same fix applies, though 10-type models may need more sophisticated initialization.
