# tfordy: Unmatched Bound Multiplier MCP Pairs (piL_r, piL_x)

**GitHub Issue:** [#966](https://github.com/jeffreyhorn/nlp2mcp/issues/966)
**Status:** RESOLVED
**Model:** tfordy (GAMSlib)
**Original error category:** `gams_error` (EXECERROR = 66)
**Original GAMS error:** `MCP pair comp_lo_r.piL_r has unmatched equation` (36 instances), `MCP pair comp_lo_x.piL_x has unmatched equation` (27 instances), `Unmatched variable not free or fixed` (3 instances)

## Description

The tfordy MCP generates lower-bound complementarity equations `comp_lo_r(c,te)` and
`comp_lo_x(c,t)` over the full domain of variables `r` and `x`. However, the
stationarity equations `stat_r(c,te)` and `stat_x(c,t)` are conditioned on subsets
`cl(c)` and `cf(c)` respectively. The emitter correctly fixes the primal variables
for inactive instances but did not fix the corresponding bound multipliers.

## Root Cause

When a primal variable `r(c,te)` is fixed to 0 for non-`cl(c)` instances, its
lower-bound multiplier `piL_r(c,te)` must also be fixed to 0 for those instances.
The `.fx` on the multiplier removes the variable column from GAMS's model matrix,
which must match the equation row to form a valid MCP pair.

## Fix (RESOLVED)

Fixed in `src/emit/emit_gams.py` section 1 (`.fx` emission for conditioned
stationarity). When a primal variable has a stationarity condition, the emitter now
also emits `.fx = 0` for the corresponding lower-bound (`piL_*`) and upper-bound
(`piU_*`) multipliers with the same condition.

The emitted GAMS code now includes:
```gams
r.fx(c,te)$(not (cl(c))) = 0;
piL_r.fx(c,te)$(not (cl(c))) = 0;
x.fx(c,t)$(not (cf(c))) = 0;
piL_x.fx(c,t)$(not (cf(c))) = 0;
```

**Verification:**
- 0 compilation errors
- 0 MCP pairing errors
- Model blocked only by GAMS demo license limit (>1000 rows/columns)

## Related Issues

- [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886) — tfordy compound table headers (RESOLVED)
- Similar pattern to #942/#943 where multiplier `.fx` was missing for inactive instances
