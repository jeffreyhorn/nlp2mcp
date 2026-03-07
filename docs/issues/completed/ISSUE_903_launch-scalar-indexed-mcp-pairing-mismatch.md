# launch: Scalar-Unrolled Stationarity Equations Paired with Indexed Variables

**GitHub Issue:** [#903](https://github.com/jeffreyhorn/nlp2mcp/issues/903)
**Status:** FIXED
**Model:** launch (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform
**Subcategory:** J (MCP pairing dimension mismatch)

## Description

The `launch` model has 4 indexed variables (`length(s)`, `ms(s)`, `t2w(s)`, `vfac(s)`) with per-element bounds that differ by element. The translator previously unrolled the stationarity equations into per-element scalar equations (e.g., `stat_length_stage_1`, `stat_length_stage_2`, `stat_length_stage_3`), but paired each scalar equation with the original indexed variable `length(s)` in the MCP model declaration. GAMS requires both sides of an MCP pairing to have the same dimensionality, producing 12 instances of `$70`.

## Fix Applied (Option A)

Eliminated per-instance scalar unrolling for non-uniform bounds. Stationarity, complementarity, and bound multiplier equations now remain indexed, with per-element bound values encoded via indexed GAMS parameters.

### Changes

1. **`src/kkt/assemble.py`** — `_create_bound_lo_multipliers()` / `_create_bound_up_multipliers()`: Always create a single indexed multiplier at key `(var_name, ())` regardless of whether bounds are uniform or non-uniform.

2. **`src/kkt/complementarity.py`** — `build_complementarity_pairs()`: For non-uniform bounds on indexed variables, create a single indexed complementarity equation using an indexed `ParamRef` for bound values, and store parameter data on `kkt.bound_params`.

3. **`src/kkt/stationarity.py`** — `build_stationarity_equations()`: Removed `_has_nonuniform_bounds()` and per-instance branching. Always uses the indexed path for indexed variables.

4. **`src/emit/emit_gams.py`** — Added bound parameter emission section (e.g., `Parameter length_lo_param(s); length_lo_param('stage-1') = 125;`).

5. **`src/kkt/kkt_system.py`** — Added `bound_params` field for indexed bound parameter storage.

### Emitted MCP (after fix)

```gams
Parameter length_lo_param(s);
length_lo_param('stage-1') = 125;
length_lo_param('stage-2') = 75;
length_lo_param('stage-3') = 50;

stat_length(s).. ... - piL_length(s) + piU_length(s) =E= 0;
comp_lo_length(s).. length(s) - length_lo_param(s) =G= 0;

Model mcp_model /
    stat_length.length,    * both 1-dim → OK
    ...
/;
```

### Verification

- launch: Compiles and solves **OPTIMAL** (Solver Status 1, Model Status 1). Zero `$70` errors.
- paklive (#1008): Compiles and solves OPTIMAL
- tabora (#1009): Compiles without `$70` errors (cannot solve due to demo license size limit)
- All 3961 tests pass

## Related Issues

- #1008 — Same root cause (paklive model)
- #1009 — Same root cause (tabora model)
