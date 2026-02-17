# Emitter: Per-Instance Bound Multipliers Not Index-Guarded in Stationarity Equations

**GitHub Issue:** [#767](https://github.com/jeffreyhorn/nlp2mcp/issues/767)
**Status:** OPEN
**Severity:** Medium — MCP is syntactically valid and may solve, but stationarity equations are mathematically wrong (multipliers active for wrong index values)
**Date:** 2026-02-17
**Affected Models:** cclinpts, maxmin, hydro

---

## Problem Summary

When a set-indexed variable has `.fx` bounds at specific element values (e.g., `b.fx('s1') = 0`),
the emitter creates a scalar multiplier `nu_b_fx_s1` for each fixed instance. These multipliers
should only appear in the stationarity row corresponding to their fixed index value. Instead,
they appear unconditionally in every row of the stationarity equation, producing mathematically
incorrect KKT conditions.

---

## Examples

### cclinpts — `stat_b(j)`

`b(j)` is fixed at two specific values (`s1`, `s30`). The generated stationarity equation is:

```gams
stat_b(j).. 1 + nu_b_fx_s1 + nu_b_fx_s30 =e= 0;
```

Both multipliers appear for **every** `j`, meaning the equation is wrong for all `j ∉ {s1, s30}`.
The correct form is:

```gams
stat_b(j).. 1 + nu_b_fx_s1$(sameas(j,'s1')) + nu_b_fx_s30$(sameas(j,'s30')) =e= 0;
```

### maxmin — `stat_point(n,d)`

`point(n,d)` is fixed at specific instances (e.g., `('p1','x')`, `('p1','y')`). Generated:

```gams
stat_point(n,d).. ... + nu_point_fx_p1_x + nu_point_fx_p1_y =e= 0;
```

Both multipliers appear for every `(n,d)` pair. Correct form requires
`$(sameas(n,'p1') and sameas(d,'x'))` and `$(sameas(n,'p1') and sameas(d,'y'))` guards.

### hydro — `stat_v(tt)`

`v(tt)` is fixed at several specific time periods (`0` through `6`). Generated:

```gams
stat_v(tt).. ... + nu_v_fx_0 + nu_v_fx_1 + ... + nu_v_fx_6 =e= 0;
```

All 7 multipliers appear for every `tt`.

---

## Root Cause

In `emit_gams.py`, when building the stationarity equation terms for a variable with
fixed-bound instances, the per-instance scalar multipliers (`nu_var_fx_val`) are added
as plain terms without any index restriction. The emitter does not check whether the
current stationarity equation row corresponds to the fixed index value.

The affected code path handles variables where `.fx` was set at specific element values
(scalar bounds on indexed variables), creating one scalar multiplier per fixed element.

---

## Reproduction

```bash
# Generate MCP for any affected model
python -m src.cli data/gamslib/raw/cclinpts.gms -o /tmp/cclinpts_mcp.gms

# Inspect stationarity equations:
grep -A5 "stat_b(j)" /tmp/cclinpts_mcp.gms
# Observe: nu_b_fx_s1 and nu_b_fx_s30 appear unconditionally
```

---

## Generated MCP (Relevant Sections)

### cclinpts — current (wrong)
```gams
* Scalar multipliers for fixed instances:
Positive Variables nu_b_fx_s1, nu_b_fx_s30;

* Stationarity (wrong — multipliers active for all j):
stat_b(j).. 1 + nu_b_fx_s1 + nu_b_fx_s30 =e= 0;
```

### cclinpts — correct
```gams
stat_b(j).. 1 + nu_b_fx_s1$(sameas(j,'s1')) + nu_b_fx_s30$(sameas(j,'s30')) =e= 0;
```

---

## Suggested Fix

When emitting a per-instance bound multiplier term `nu_var_fx_val` into a stationarity
equation `stat_var(i1, i2, ...)`, wrap it with a `$(sameas(...))` guard matching the
fixed element:

- Single-index variable `b(j)` fixed at `'s1'`: emit `nu_b_fx_s1$(sameas(j,'s1'))`
- Multi-index variable `point(n,d)` fixed at `('p1','x')`: emit
  `nu_point_fx_p1_x$(sameas(n,'p1') and sameas(d,'x'))`

The emitter already knows the fixed element values (they come from the `.fx` assignment
records), so the guard expression can be constructed from the element key.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/emit/emit_gams.py` | Stationarity equation emission — where per-instance multiplier terms are added |
| `data/gamslib/mcp/cclinpts_mcp.gms` | Generated — shows the bug (do not edit directly) |
| `data/gamslib/mcp/maxmin_mcp.gms` | Generated — shows the bug (do not edit directly) |
| `data/gamslib/mcp/hydro_mcp.gms` | Generated — shows the bug (do not edit directly) |

---

## Related Issues

- **ISSUE_768**: Scalar parameter emitted once per equation pass (triplication) — separate emitter bug identified in same PR review
- Identified during PR #762 review
