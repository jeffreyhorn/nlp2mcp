# tfordy: Unmatched Bound Multiplier MCP Pairs (piL_r, piL_x)

**GitHub Issue:** [#966](https://github.com/jeffreyhorn/nlp2mcp/issues/966)
**Model:** tfordy (GAMSlib)
**Error category:** `gams_error` (EXECERROR = 66)
**GAMS error:** `MCP pair comp_lo_r.piL_r has unmatched equation` (36 instances), `MCP pair comp_lo_x.piL_x has unmatched equation` (27 instances), `Unmatched variable not free or fixed` (3 instances)

## Description

The tfordy MCP generates lower-bound complementarity equations `comp_lo_r(c,te)` and
`comp_lo_x(c,t)` over the full domain of variables `r` and `x`. However, the
stationarity equations `stat_r(c,te)` and `stat_x(c,t)` are conditioned on subsets
`cl(c)` and `cf(c)` respectively. The emitter correctly fixes the primal variables
for inactive instances:

```gams
r.fx(c,te)$(not (cl(c))) = 0;
x.fx(c,t)$(not (cf(c))) = 0;
```

But it does **not** fix the corresponding lower-bound multipliers `piL_r` and `piL_x`
for those same inactive instances. Since `comp_lo_r` and `comp_lo_x` have no dollar
condition, GAMS sees active MCP equation instances paired with unfixed variables that
have no meaningful role in the KKT system.

## Root Cause

When a primal variable `r(c,te)` is fixed to 0 for non-`cl(c)` instances, its
lower-bound multiplier `piL_r(c,te)` should also be fixed to 0 for those instances.
The KKT pipeline generates the `.fx` for the primal variable (from the stationarity
equation's dollar condition) but does not propagate this fix to the bound multiplier.

**Error counts:**
- 36 = 3 non-cl commodities (residuals, pulp, sawnwood) × 12 periods (te)
- 27 = 3 non-cf commodities (pulplogs, sawlogs, residuals) × 9 periods (t)
- 3 = "Unmatched variable not free or fixed" for specific `r(c,te)` instances

## Reproduction

```bash
python -m src.cli data/gamslib/raw/tfordy.gms -o /tmp/tfordy_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/tfordy_mcp.gms lo=3
# Check LST file for errors:
grep "^\*\*\*\*" /tmp/tfordy_mcp.lst | sort | uniq -c | sort -rn
```

## Fix Approach

When a primal variable has a `.fx` emission with a condition `$(not (cond))`, the
emitter should also emit `.fx = 0` for the corresponding bound multipliers (`piL_*`
and/or `piU_*`) with the same condition. This ensures that when the primal variable
is inactive, its bound multipliers are also removed from the active MCP matching.

The fix should be in `src/emit/emit_gams.py` in the `.fx` emission section. After
emitting `r.fx(c,te)$(not (cl(c))) = 0`, also emit:
```gams
piL_r.fx(c,te)$(not (cl(c))) = 0;
```

**Files to modify:**
- `src/emit/emit_gams.py` — `.fx` emission section
- Possibly `src/kkt/assemble.py` or `src/kkt/partition.py` if the condition information needs to be propagated

**Estimated effort:** 2–3h

## Related Issues

- [#886](https://github.com/jeffreyhorn/nlp2mcp/issues/886) — tfordy compound table headers (RESOLVED)
- Similar pattern to #942/#943 where multiplier `.fx` was missing for inactive instances
- May affect other models where stationarity equations have dollar conditions that restrict the primal variable domain
