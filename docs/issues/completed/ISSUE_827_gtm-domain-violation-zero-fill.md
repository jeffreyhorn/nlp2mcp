# GTM MCP: GAMS Error 170 — Domain Violations from Zero-Filled Parameter Data

**GitHub Issue:** [#827](https://github.com/jeffreyhorn/nlp2mcp/issues/827)
**Status:** OPEN — Cannot fix; requires parser + emitter infrastructure changes
**Severity:** High — MCP generates but GAMS reports 28 compile errors (domain violations)
**Date:** 2026-02-22
**Affected Models:** gtm

---

## Problem Summary

The gtm model (`data/gamslib/raw/gtm.gms`) generates an MCP file, but GAMS reports
28 compile errors including domain violations (Error 170) and unassigned symbols (Error 141):

```
**** 170  Domain violation for element
**** 300  Remaining errors not printed for this line
**** 141  Symbol declared but no values have been assigned.
```

The errors occur because the parser zero-fills parameter table data for all combinations of
domain indices, including `(i,j)` pairs where the first index is not in set `i` (e.g.,
`central` which is only in set `j`), and the emitter emits these entries without domain
validation.

Previously this model failed with `codegen_numerical_error` due to `+Inf` parameter value
in the `sdat` table. The Inf handling fix (Sprint 20 Day 10) resolved that blocker, revealing
these deeper issues.

---

## Specific Errors

### Error 170: Domain Violations in `utc(i,j)` and `pc(i,j)`

Parameters `utc(i,j)` and `pc(i,j)` have domain `(i,j)` where:
- `i = {mexico, alberta-bc, atlantic, appalacia, us-gulf, mid-cont, permian-b, rockies, pacific, alaska}`
- `j = {mexico, west-can, ont-quebec, atlantic, new-engl, ny-nj, mid-atl, south-atl, midwest, south-west, central, n-central, west, n-west}`

The emitter zero-fills entries like `central.west-can 0.0` and `central.ont-quebec 0.0`
where `central` is in set `j` but NOT in set `i`. GAMS correctly rejects these as domain
violations.

### Error 141: Unassigned Symbols (`supa`, `supb`, `dema`, `demb`)

Parameters `supa(i)`, `supb(i)`, `dema(j)`, `demb(j)` are declared but assigned values
via computed expressions that reference other parameters. The emitter emits the assignment
statements (`supa(i) = ...`) but these assignments reference `supb` and `supc` which are
declared without data, causing a cascade of Error 141 warnings.

This is likely because the emitter emits parameter assignments in declaration order rather
than dependency order — `supa` is assigned before `supb` gets its value.

---

## Reproduction

```bash
# Generate MCP
python -m src.cli data/gamslib/raw/gtm.gms -o /tmp/gtm_mcp.gms

# Run GAMS
gams /tmp/gtm_mcp.gms lo=2

# Expected output:
# **** 170  Domain violation for element (on utc and pc parameters)
# **** 141  Symbol declared but no values have been assigned (supa, supb, dema, demb)
# **** 28 ERROR(S)   0 WARNING(S)
```

---

## Root Cause

### Domain Violations (Error 170)

The parser's zero-fill logic in `_handle_table_block()` generates entries for all
combinations of the Cartesian product of row and column headers. For `utc(i,j)`, this
produces entries for `central.west-can`, `n-central.mexico`, etc. where the first index
(`central`) is not in set `i`. The emitter then emits these entries without domain
validation, and GAMS enforces domain checking and rejects them.

The zero-fill should only generate entries for valid domain combinations, respecting the actual
domain sets of each parameter dimension.

### Unassigned Symbols (Error 141)

Parameters `supa`, `supb`, `dema`, `demb` are computed from other parameters via assignment
statements. The emitter needs to ensure these assignments are emitted in topologically-sorted
(dependency) order so that referenced parameters have values before they are used.

---

## Suggested Fix

**For Error 170:**
- In `emit_original_parameters()` (or zero-fill logic), only generate entries for valid
  domain combinations. Check each index against its declared domain set before emitting.
- Alternatively, skip zero-filling for parameters with multi-dimensional domains and let
  GAMS use its default value (0) for unspecified entries.

**For Error 141:**
- Topologically sort parameter assignment statements by their dependencies before emitting.
- Alternatively, use `$onImplicitAssign` to suppress the warnings for parameters that are
  computed later.

---

## Files to Investigate

| File | Relevance |
|------|-----------|
| `src/emit/original_symbols.py` | `emit_original_parameters()` — zero-fill logic |
| `src/emit/emit_gams.py` | Parameter assignment ordering |
| `data/gamslib/raw/gtm.gms` | Original model with multi-domain parameters |

---

## Investigation Findings (2026-02-22)

### Problem 1: Zero-Fill Creates Invalid Domain Combinations

**Root cause location**: `src/ir/parser.py`, lines 2462-2483 (`_handle_table_block()`)

The zero-fill logic in the parser's table handler collects all row headers and all column
headers, then fills missing cells with 0.0 for every `(row, col)` combination:

```python
for row_header in all_row_headers:
    for col_name in col_names:
        key = (row_header, col_name)
        if key not in values:
            values[key] = 0.0
```

This creates a blind Cartesian product without validating that each index belongs to the
parameter's declared domain set. For `utc(i,j)` in the gtm model:
- Row headers include elements from set `i` (10 supply regions)
- Column headers include elements from set `j` (14 demand regions)
- The zero-fill generates all 140 combinations, but some row headers (like `central`) are
  only in set `j`, not in set `i`. GAMS correctly rejects these as Error 170.

**Why the emitter doesn't catch this**: `emit_original_parameters()` in
`src/emit/original_symbols.py` (lines 706-740) iterates over `param_def.values.items()`
and emits all entries without domain validation. The domain set membership information
exists in `model_ir.sets` but is never consulted during parameter emission.

### Problem 2: Parameter Assignment Ordering

**Root cause location**: `src/emit/original_symbols.py`, line 946

The emitter has two passes for parameter assignments:
- **First pass** (`varref_filter="no_varref_attr"`): Parameters without `.l` references,
  emitted BEFORE Variables. Uses declaration order: `param_order = list(model_ir.params.keys())`
- **Second pass** (`varref_filter="only_varref_attr"`): Calibration parameters with `.l`
  references. Uses topological sort via Kahn's algorithm (lines 909-944).

The gtm model's computed parameters (`supa`, `supb`, `supc`, `dema`, `demb`) have no `.l`
references, so they go through the first pass with no dependency ordering. If `supa` is
declared before `supb` but depends on it, GAMS reports Error 141 (unassigned symbol).

The topological sort infrastructure already exists in the codebase (Kahn's algorithm,
`_collect_param_refs()`, `param_deps` tracking) but is only applied to the calibration
parameter pass.

### Why This Cannot Be Simply Fixed

**Error 170 (domain violations)**:
- The zero-fill happens at parse time in `_handle_table_block()`, which has no access to
  domain set membership (sets may not be fully resolved yet)
- Fixing at emit time would require domain validation against `model_ir.sets`, but the
  emitter currently has no such logic
- A simpler approach: **skip zero-fill entirely** for multi-dimensional parameters and let
  GAMS use its default value (0) for unspecified entries. However, this would change behavior
  for models that rely on explicit zero entries.

**Error 141 (parameter ordering)**:
- Extending topological sort to the first pass is feasible but requires careful handling:
  the existing Kahn's algorithm only operates on `eligible` parameters (filtered to include
  only calibration parameters). Broadening this to all computed parameters needs testing
  across the full model suite.

### Prerequisites Before Attempting Fix

1. **Error 170 — Domain-aware zero-fill** (three options):
   - **Option A (parser-side)**: In `_handle_table_block()`, validate each `(row, col)` pair
     against the parameter's domain sets before adding the zero entry. Requires resolving
     domain sets before table parsing completes.
   - **Option B (emitter-side)**: In `emit_original_parameters()`, filter out entries where
     indices violate domain sets by checking against `model_ir.sets[domain_set].members`.
   - **Option C (simplest)**: Skip zero-fill for table parameters entirely — GAMS defaults
     unspecified entries to 0.

2. **Error 141 — Topological sort for all computed parameters**:
   - Extend the existing Kahn's algorithm in `emit_computed_parameter_assignments()` to also
     apply when `varref_filter="no_varref_attr"`.
   - The dependency collection (`_collect_param_refs()`) and sorting infrastructure already
     exist — this is primarily a matter of removing the calibration-only guard.

### Key Code Locations

| Function | File:Line | Issue |
|----------|-----------|-------|
| `_handle_table_block()` | `parser.py:2462-2483` | Blind Cartesian zero-fill |
| `emit_original_parameters()` | `original_symbols.py:706-740` | No domain validation on emit |
| `emit_computed_parameter_assignments()` | `original_symbols.py:839-946` | Topological sort only for calibration params |
| `_collect_param_refs()` | `original_symbols.py:825-836` | Dependency collection (works for all params) |

---

## Progress (2026-04-01)

**Compilation errors: FIXED.** All 28 compilation errors ($170 domain violations, $141 unassigned symbols) have been resolved by accumulated fixes across prior PRs. The model now compiles cleanly.

**New blocker: Runtime errors.** EXECERROR=3 at solve time:
- Division by zero in `stat_s(mexico)`, `stat_s(alberta-bc)`, `stat_s(atlantic)` — likely from supply function derivatives evaluated at zero
- Infeasibilities in `stat_d` and `stat_x` equations — KKT conditions may be structurally incorrect

These are separate issues from the original $170/$141 problems.
