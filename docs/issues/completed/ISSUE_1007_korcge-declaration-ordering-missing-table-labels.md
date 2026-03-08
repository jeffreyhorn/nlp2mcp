# korcge: Variable `.l` Used Before Declaration + Missing Table Labels

**GitHub Issue:** [#1007](https://github.com/jeffreyhorn/nlp2mcp/issues/1007)
**Status:** FIXED
**Model:** korcge (GAMSlib)
**Error category:** `gams_compilation_error`
**GAMS errors:** `$318` (domain list redefined), `$140` (unknown symbol), `$116` (label is unknown)

## Description

The `korcge` MCP translation has two independent emitter bugs that produce 9 compilation errors:

### Bug 1: Variable `.l` initialization emitted before variable declaration ($318, $140)

The emitter places the assignment `it(i) = yes$(e.l(i) or m.l(i))` at line 59 of the MCP file, **before** the Variables section begins at line 91. GAMS sees `e.l(i)` before `e(i)` is declared as a variable, creating an implicit domain-less symbol. When the explicit `Variable e(i)` declaration appears later at line 105, GAMS raises `$318` (domain list redefined).

In the original `korcge.gms`, variable declarations (lines 123–176) precede `.l` initializations (lines 251–252), and the `it(i)` set definition using `.l` values appears at line 260 — well after both.

### Bug 2: Zero-valued table rows dropped from parameter initialization ($116)

The `zz(*,i)` table in the original model has rows for `depr`, `dstr`, and `te` where all values are `0.0`. The `sectres(*,i)` table has a row for `dst` where all values are `0.0`. The emitter omits these all-zero rows during parameter initialization, but the model later references them:

```gams
depr(i) = zz("depr",i);   * $116 — "depr" label not in zz
dstr(i) = zz("dstr",i);   * $116 — "dstr" label not in zz
te(i)   = zz("te",i);     * $116 — "te" label not in zz
dst.l(i) = sectres("dst",i);  * $116 — "dst" label not in sectres
```

## Fix Applied

### Bug 1: Defer `.l`-referencing set assignments after variable declarations

Added `varref_filter` parameter to `emit_set_assignments()` (same pattern as `emit_computed_parameter_assignments()`). Set assignments that reference `.l` values — either directly (e.g., `it(i) = yes$(e.l(i))`) or transitively through set dependencies (e.g., `in(i) = not it(i)`) — are deferred until after the Variables declaration and `.l` initialization sections.

The transitive dependency computation identifies deferred sets by:
1. Finding set assignments whose expressions contain attributed VarRef nodes
2. Propagating deferral to set assignments that reference deferred sets via `SetMembershipTest`

Files modified:
- `src/emit/original_symbols.py`: Added `varref_filter` parameter and `_collect_set_membership_names()` helper for transitive dependency computation
- `src/emit/emit_gams.py`: Split `emit_set_assignments()` call into two passes — `no_varref_attr` before Variables, `only_varref_attr` after `.l` initialization

### Bug 2: Preserve label registration for all-zero table rows

Instead of re-inserting explicit zero entries (which would break Issue #967's sparse evaluation fix), we collect first-dimension labels for multi-dimensional `*`-domain parameters that would be entirely dropped by zero-filtering via `collect_missing_param_labels()`, and emit them into a synthetic UEL registry `Set`. This ensures GAMS sees the full set of string-indexable labels (e.g., `"depr"`, `"dstr"`, `"te"`, `"dst"`) without reintroducing all-zero rows, preserving sparse evaluation semantics while keeping labels available for string-indexed lookups.

Files modified:
- `src/emit/original_symbols.py`: Added `collect_missing_param_labels()` to track labels lost to zero-filtering
- `src/emit/emit_gams.py`: Emit synthetic UEL registry `Set` to register missing parameter labels with GAMS

### Verification

- All 3970 tests pass
- Quality gate: typecheck, lint, format all pass
- korcge model compiles with zero errors and solves to completion

## Related Issues

- Cascading errors: $257 (solve not checked) and $141 (omega.l unassigned) were consequences of the primary errors above — resolved by fixing both bugs
