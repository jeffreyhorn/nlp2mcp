# ps10_s_mn: Objective Mismatch — 10-Type Principal-Agent Monte Carlo, Multi-Solve

**GitHub Issue:** [#1107](https://github.com/jeffreyhorn/nlp2mcp/issues/1107)
**Status:** OPEN
**Model:** ps10_s_mn (GAMSlib SEQ=375)
**Error category:** `objective_mismatch`
**MCP objective:** 1.505
**NLP objective:** 0.4035
**Absolute difference:** 1.10
**Relative difference:** 73.2%

## Description

ps10_s_mn (Parts Supply Problem with 10 Types, Monotone Non-Decreasing) is a Monte Carlo simulation harness that solves an inner NLP 2000 times (1000 iterations x 2 models). The generated MCP solves to Optimal but at a completely different KKT point due to two compounding factors: multi-solve data incompatibility and non-convex KKT divergence.

## Root Cause

### 1. Multi-Solve Monte Carlo Incompatibility (Dominant)

The model generates 1000 random probability vectors and solves two NLP variants per iteration:

```gams
loop(t,
   p(i) = pt(i,t);                           -- different data each iteration
   solve SB_lic maximizing Util using nlp;    -- without monotonicity
   Util_lic(t) = util.l;
   solve SB_lic2 maximizing Util using nlp;   -- with monotonicity
   Util_lic2(t) = util.l;
);
```

The NLP reference captures the LAST solve objective (t=1000, SB_lic2 with monotonicity). The MCP uses `p(i) = pt(i,'1')` (first iteration) and transforms SB_lic (without monotonicity). The comparison is fundamentally invalid — different data AND different model.

### 2. Non-Convex KKT Point Divergence (Secondary)

Even comparing MCP to NLP first-iteration values shows 187% mismatch (MCP=1.505 vs NLP SB_lic(t=1)=0.525). The principal-agent model with `b(i) = x(i)**0.5` has many KKT points, and PATH converges to a completely different one from default initialization. The mismatch grows with the number of types (worse for 10-type than 3-type or 5-type).

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps10_s_mn.gms -o /tmp/ps10_s_mn_mcp.gms
gams /tmp/ps10_s_mn_mcp.gms lo=2
# MCP obj = 1.505

gams data/gamslib/raw/ps10_s_mn.gms lo=2
# NLP obj = 0.4035 (last of 2000 solves)
```

## Recommended Fix

1. **Short-term**: Set `multi_solve: true` in `gamslib_status.json` to skip comparison (reclassify as incomparable)
2. **Long-term**: Multi-solve warm-start infrastructure — solve original NLP first, use solution to initialize MCP

## Related Issues

- #963 (ps3_s_mn): 3-type variant, same pattern (2.2% mismatch)
- #964 (ps10_s): 10-type single-solve variant (27.4% mismatch)
- #944 (ps5_s_mn): Multi-solve pattern incompatibility
- #1080: Multi-solve classification infrastructure (resolved, but flags not applied)
- #917, #1101: Previous compilation errors (RESOLVED)

## Estimated Effort

Short-term (database flag): 15 minutes. Long-term (warm-start): 6h+ architectural change.
