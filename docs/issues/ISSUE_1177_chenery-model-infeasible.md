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

## Investigation (2026-03-30)

`.fx` statements correctly zero out multipliers for out-of-subset instances (e.g., `nu_dg.fx(i)$(not (t(i))) = 0;`). The infeasibility is structural — the KKT conditions are mathematically wrong.

Specific finding: `stat_y(i)` equations have `=E= 1` on the RHS but LHS is 0 at the initial point, with INFES=1. The `1` appears to be from the objective gradient coefficient for `y`. The `comp_mb` equations also show large infeasibilities (50-110).

This suggests the stationarity equations themselves are incorrectly constructed — possibly the objective gradient term or the constraint Jacobian entries for `y` are wrong. The domain widening may have introduced zero entries where non-zero coefficients should exist.

## Fix Approach

1. Compare the generated KKT equations against manually-derived KKT for chenery
2. Check if the objective gradient for `y` is correct (should it be 1?)
3. Verify Jacobian entries for `comp_mb` constraint w.r.t. `y` variables
4. The infeasibility may require fixing the stationarity builder's handling of the objective function in models with subset-domain variables
