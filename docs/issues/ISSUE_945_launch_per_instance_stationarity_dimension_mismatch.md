# launch: Per-Instance Stationarity Equations Cause Dimension Mismatch in MCP Pairing

**GitHub Issue:** [#945](https://github.com/jeffreyhorn/nlp2mcp/issues/945)
**Status:** OPEN
**Models:** launch (GAMSlib)
**Error category:** `gams_compilation_error` (Error 70, Error 256)
**Compilation error:** `The dimensions of the equ.var pair do not conform`

## Description

The launch model generates per-instance (scalar) stationarity equations for indexed variables. For example, `stat_length_stage_1`, `stat_length_stage_2`, `stat_length_stage_3` are three separate scalar equations for the variable `length(s)` where `s = /stage-1, stage-2, stage-3/`. The MCP model block pairs these scalar equations with the indexed variable `length`, causing a dimension mismatch (scalar equation vs. 1D variable).

## Reproduction

```bash
# Translate and solve:
python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms
/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams /tmp/launch_mcp.gms lo=2

# Expected errors:
# **** 70  The dimensions of the equ.var pair do not conform
# **** The following MCP errors were detected in model mcp_model:
# ****  70 length dimensions are different
# ****  70 ms dimensions are different
# ****  70 t2w dimensions are different
# ****  70 vfac dimensions are different
```

## Root Cause

The stationarity builder generates per-instance equations when it expands indexed variables:

```gams
* Variable length(s) with s = /stage-1, stage-2, stage-3/
* Instead of one indexed equation:
*   stat_length(s).. <gradient terms for length(s)> =E= 0;
* The builder generates three scalar equations:
stat_length_stage_1.. <gradient for length("stage-1")> =E= 0;
stat_length_stage_2.. <gradient for length("stage-2")> =E= 0;
stat_length_stage_3.. <gradient for length("stage-3")> =E= 0;
```

The MCP model block then pairs each scalar equation with the full indexed variable:

```gams
Model mcp_model /
    stat_length_stage_1.length,    ← scalar equation paired with length(s) → Error 70
    stat_length_stage_2.length,    ← scalar equation paired with length(s) → Error 70
    stat_length_stage_3.length,    ← scalar equation paired with length(s) → Error 70
    ...
/;
```

GAMS requires that equation and variable dimensions match in MCP pairings. A scalar equation can only pair with a scalar variable.

### Affected Variables

| Variable | Dimension | Per-Instance Equations | Bound Variables |
|----------|-----------|----------------------|-----------------|
| length(s) | 1D (3 elements) | stat_length_stage_1/2/3 | piL_length_stage_1/2/3, piU_length_stage_1/2/3 |
| ms(s) | 1D (3 elements) | stat_ms_stage_1/2/3 | piL_ms_stage_1/2/3, piU_ms_stage_1/2/3 |
| t2w(s) | 1D (3 elements) | stat_t2w_stage_1/2/3 | piL_t2w_stage_1/2/3, piU_t2w_stage_1/2/3 |
| vfac(s) | 1D (3 elements) | stat_vfac_stage_1/2/3 | piL_vfac_stage_1/2/3, piU_vfac_stage_1/2/3 |

## Fix Approach

**Option A: Consolidate per-instance stationarity into indexed equations.** Instead of generating `stat_length_stage_1`, `stat_length_stage_2`, `stat_length_stage_3`, generate a single indexed equation:
```gams
stat_length(s).. <gradient for length(s)> =E= 0;
```

This requires the stationarity builder to recognize when it's generating per-instance equations for an indexed variable and merge them into a single indexed equation. The gradient terms would use the set index `s` instead of literal element names.

**Option B: Pair per-instance equations with per-instance variables.** Create scalar "alias" variables for each instance:
```gams
Variable length_stage_1, length_stage_2, length_stage_3;
length_stage_1.l = length.l("stage-1");
* ... and link them back after solve
```

This is complex and fragile.

**Option C: Use scalar MCP pairing.** GAMS supports per-element MCP pairing but requires matching scalar equations with scalar variables. This would mean declaring the bound multipliers as scalars too (which they already are: `piL_length_stage_1`, etc.).

However, the core variable `length(s)` is still indexed, so Option C only works if we also split the variable into scalars, which is Option B.

**Recommended: Option A** — Consolidate per-instance stationarity equations into properly indexed equations. This is the most natural GAMS pattern and avoids the dimension mismatch entirely.

**Estimated effort:** 3-5h (significant stationarity builder changes to merge per-instance into indexed)

## Related Issues

- #904: power() non-integer exponent (primary blocker now fixed; this is the secondary blocker)
- The per-instance stationarity pattern may affect other models with indexed variables where the stationarity builder can't generate indexed equations directly
