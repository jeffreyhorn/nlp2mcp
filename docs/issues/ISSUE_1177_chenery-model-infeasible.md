# chenery: MCP Locally Infeasible (MODEL STATUS 5)

**GitHub Issue:** [#1177](https://github.com/jeffreyhorn/nlp2mcp/issues/1177)
**Model:** chenery (GAMSlib SEQ=28)
**Error category:** `model_infeasible`
**Previous blocker:** $171 domain violation (fixed in PR #1176 via domain widening)

## Description

The chenery model now compiles cleanly after the $171/$445 fixes, but PATH solver returns MODEL STATUS 5 (Locally Infeasible). The KKT conditions may be structurally incorrect due to the domain widening — widening parameter domains from subset `t` to superset `i` changes the semantics (zero-fills for out-of-subset elements, which may create infeasible constraints).

## Reproduction

```bash
python -m src.cli data/gamslib/raw/chenery.gms -o /tmp/chenery_mcp.gms --skip-convexity-check
(cd /tmp && gams chenery_mcp.gms lo=2)
# MODEL STATUS 5 Locally Infeasible
```

## Root Cause

The stationarity equations iterate over `i = {light-ind, food+agr, heavy-ind, services}` but parameters `alp(t)` and `xsi(t)` are only meaningful for `t = {light-ind, food+agr, heavy-ind}`. Domain widening declares them over `i`, so the `services` element gets zero values. This may create contradictory KKT conditions for the `services` instance.

## Fix Approach

Investigate whether the stationarity equations for `services` (the superset-only element) need special handling:
1. Check if `.fx` statements correctly zero out multipliers for out-of-subset instances
2. Verify that the dollar conditions on stationarity terms properly exclude out-of-subset elements
3. May need to add explicit `.fx` for primal variables or multipliers at `services`
