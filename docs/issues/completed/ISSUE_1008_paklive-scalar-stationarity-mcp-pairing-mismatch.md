# paklive: Scalar-Unrolled Stationarity Equations Paired with Indexed Variable

**GitHub Issue:** [#1008](https://github.com/jeffreyhorn/nlp2mcp/issues/1008)
**Status:** FIXED
**Model:** paklive (GAMSlib)
**Error category:** `path_syntax_error`
**GAMS error:** `$70` — The dimensions of the equ.var pair do not conform

## Description

The `paklive` model has an indexed variable `xcrop(c)` with 10 elements (wheat, basrice, irrrice, maize, oilseed, gram, cotton, sugar, berseem, kharfodder). The variable has a single per-element upper bound: `xcrop.up("sugar") = 2`.

The MCP emitter creates 10 scalar stationarity equations (`stat_xcrop_wheat`, `stat_xcrop_basrice`, ...) instead of one indexed equation `stat_xcrop(c)`. Each scalar equation is then paired with the indexed variable `xcrop(c)` in the MCP model statement, producing 9 instances of GAMS Error $70 (dimension mismatch).

This is the same root cause as issue #903 (launch model).

## Fix Applied

Eliminated per-instance scalar unrolling for non-uniform bounds. All stationarity, complementarity, and bound multiplier equations now remain indexed, with per-element bound values encoded via indexed GAMS parameters.

### Changes

1. **`src/kkt/assemble.py`** — `_create_bound_lo_multipliers()` / `_create_bound_up_multipliers()`: Always create a single indexed multiplier at key `(var_name, ())` regardless of whether bounds are uniform or non-uniform. Removed per-instance scalar multiplier creation and `enumerate_variable_instances` import.

2. **`src/kkt/complementarity.py`** — `build_complementarity_pairs()`: For non-uniform bounds on indexed variables, create a single indexed complementarity equation using an indexed `ParamRef` for bound values, and store parameter data on `kkt.bound_params`.

3. **`src/kkt/stationarity.py`** — `build_stationarity_equations()`: Removed `_has_nonuniform_bounds()` function and per-instance branching. Always uses the indexed path for indexed variables.

4. **`src/emit/emit_gams.py`** — Added bound parameter emission section: declares `Parameter x_up_param(c);` and assigns per-element values before equations.

5. **`src/kkt/kkt_system.py`** — Added `bound_params` field to `KKTSystem` for indexed bound parameter storage.

### Verification

- All 3961 tests pass
- Quality gate: typecheck, lint, format all pass

## Related Issues

- #903 — Same root cause (launch model: scalar-indexed MCP pairing mismatch)
- #1009 — Same root cause (tabora model)
