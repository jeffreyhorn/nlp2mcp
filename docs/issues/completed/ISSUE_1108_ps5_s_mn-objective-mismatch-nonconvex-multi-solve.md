# ps5_s_mn: Objective Mismatch — 5-Type Principal-Agent Monte Carlo, Multi-Solve

**GitHub Issue:** [#1108](https://github.com/jeffreyhorn/nlp2mcp/issues/1108)
**Status:** RESOLVED (short-term fix applied)
**Resolved:** 2026-03-16
**Model:** ps5_s_mn (GAMSlib SEQ=374)
**Error category:** `objective_mismatch` → `compare_multi_solve_skip`
**MCP objective:** 0.728
**NLP objective:** 0.4254
**Absolute difference:** 0.30
**Relative difference:** 41.6%

## Description

ps5_s_mn (Parts Supply Problem with 5 Types, Monotone Non-Decreasing) is a Monte Carlo simulation harness that solves an inner NLP 2000 times (1000 iterations x 2 models). The generated MCP solves to Optimal but at a different KKT point due to multi-solve data incompatibility and non-convex KKT divergence.

## Root Cause

Same dual root cause as ps10_s_mn:

### 1. Multi-Solve Monte Carlo Incompatibility (Dominant)

The model generates 1000 random probability vectors and solves two NLP variants per iteration:

```gams
loop(t,
   p(i) = pt(i,t);
   solve SB_lic maximizing Util using nlp;
   Util_lic(t) = util.l;
   solve SB_lic2 maximizing Util using nlp;
   Util_lic2(t) = util.l;
);
```

NLP reference is from last iteration (t=1000, different random data). MCP uses first iteration data (t=1) and only transforms SB_lic.

### 2. Non-Convex KKT Point Divergence (Secondary)

MCP=0.728 vs NLP SB_lic(t=1)=0.421 — even with matching data, a 73% mismatch from non-convex KKT multiplicity with the `b(i) = x(i)**0.5` revenue function.

## Resolution

**Short-term fix applied:** Set `multi_solve: true` in `data/gamslib/gamslib_status.json`. The pipeline comparison now skips this model with category `compare_multi_solve_skip`, removing it from the mismatch count.

**Remaining long-term work:** Multi-solve warm-start infrastructure. Deferred — 6h+ architectural change.

## Reproduction

```bash
python -m src.cli data/gamslib/raw/ps5_s_mn.gms -o /tmp/ps5_s_mn_mcp.gms
gams /tmp/ps5_s_mn_mcp.gms lo=2
# MCP obj = 0.728

gams data/gamslib/raw/ps5_s_mn.gms lo=2
# NLP obj = 0.4254
```

## Related Issues

- #963 (ps3_s_mn): 3-type variant, same pattern
- #964 (ps10_s): 10-type single-solve variant
- #944 (ps5_s_mn): Multi-solve pattern incompatibility (broader)
- #1080: Multi-solve classification infrastructure (resolved, but flags not applied)
- #1109: Multi-solve database flags not applied (this fix)
- #917, #1102: Previous compilation errors (RESOLVED)
