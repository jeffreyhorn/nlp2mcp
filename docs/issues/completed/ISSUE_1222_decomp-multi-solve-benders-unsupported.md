# decomp: Multi-Solve Benders Decomposition Unsupported

**GitHub Issue:** [#1222](https://github.com/jeffreyhorn/nlp2mcp/issues/1222)
**Status:** RESOLVED — Excluded from pipeline as `multi_solve_driver_out_of_scope`
**Severity:** Medium — Model requires iterative solve loop, incompatible with single MCP
**Date:** 2026-04-07
**Resolved:** 2026-04-18 (Sprint 24, PLAN_FIX_DECOMP)
**Affected Models:** decomp (and danwolfe, resolved in the same change)

---

## Problem Summary

The decomp model (GAMSlib SEQ=164, "Decomposition Principle - Animated") uses
Benders decomposition with multiple iterative `solve` statements in a loop. The
nlp2mcp tool reformulates a single NLP solve into an MCP, but decomp has 4+
solve statements and references equation marginals (`.m` attribute) between
iterations. The emitter produces invalid GAMS like `ctank = - tbal m ;` instead
of `ctank = -tbal.m;` because the equation marginal attribute is not properly
handled.

---

## Root Cause

1. **Multi-solve structure**: decomp solves `sub` (LP) and `master` (LP)
   iteratively in a loop, using marginal values from one solve to update
   parameters for the next.

2. **Equation marginal references**: Lines like `ctank = -tbal.m;` and
   `rep(ss,'t-pi') = -tbal.m;` reference the marginal (dual value) of
   equation `tbal` from the most recent solve. The emitter doesn't handle
   `.m` attribute access on equations.

3. **Fundamental incompatibility**: The MCP reformulation replaces the
   original model's equations with KKT stationarity conditions. The
   original equations (`tbal`, `convex`) don't exist in the MCP, so their
   marginals (`.m`) are undefined.

---

## Reproduction

```bash
# Translate
.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms -o /tmp/decomp_mcp.gms --quiet

# Compile — Error 140 (Unknown symbol) on "tbal m"
gams /tmp/decomp_mcp.gms lo=0

# Error output:
# ctank = - tbal m ;
#                $140,409
# **** 140  Unknown symbol
```

---

## GAMS Errors

- **Error 140**: Unknown symbol — `tbal` is emitted as a bare identifier, not
  recognized as an equation name
- **Error 409**: Unrecognizable item — the `m` after `tbal` is not parsed as
  an attribute accessor

---

## Potential Fix Approaches

1. **Detect and skip multi-solve models**: If a model has multiple `solve`
   statements, warn and skip MCP reformulation. This is the simplest approach.

2. **Support equation marginal emission**: Emit `.m` references properly
   as `equation_name.m`. However, in the MCP context, the original equation
   doesn't exist, so the marginal is the multiplier variable instead. Would
   need to map `tbal.m` → `nu_tbal.l` in post-solve assignments.

3. **Support iterative solve loops**: Full support for Benders-style
   decomposition. Very complex — requires loop unrolling or multi-stage
   reformulation. Not recommended for near-term.

---

## Files Involved

- `src/emit/emit_gams.py` — Pre-solve assignment emission
- `src/ir/parser.py` — Loop/solve statement handling
- `data/gamslib/raw/decomp.gms` — Original model (138 lines)

---

## Resolution

Resolved by exclusion in Sprint 24 (PR #1265, `sprint24-plan-fix-decomp`). The
underlying mismatch is not fixable by patching the emitter: decomp's catalog
objective `mobj = 60` is the **converged fixed point** of the Dantzig–Wolfe /
Benders iteration, not any single NLP's answer. Even a bug-free emitter would
only produce one snapshot of the loop, which cannot be expected to match the
algorithm's final value.

The `decomp` model is now rejected up-front by the pre-translation gate added
in `src/validation/driver.py` (three-condition conjunction: ≥2 declared models
AND ≥2 distinct solve targets AND ≥1 `eq.m` read inside a solve-containing
loop). `decomp` satisfies all three via `master` / `sub` and the
`tbal.m` / `convex.m` reads inside the iteration loop.

### Changes

| File | Change |
|------|--------|
| `src/validation/driver.py` | New `validate_single_optimization()` / `scan_multi_solve_driver()` — raises `MultiSolveDriverError` on driver scripts |
| `src/cli.py` | Wires the gate in; exit code `4` (`EXIT_MULTI_SOLVE_OUT_OF_SCOPE`); `--allow-multi-solve` dev escape hatch |
| `data/gamslib/schema.json` | Schema v2.2.0 → v2.2.1; new exclusion-reason keyword `multi_solve_driver_out_of_scope` |
| `scripts/gamslib/migrate_schema_v2.2.1.py` | Migration script that flips `decomp` and `danwolfe` to `pipeline_status: skipped` and strips the stale translate/solve blocks |
| `data/gamslib/gamslib_status.json` | Migrated in-place |
| `tests/unit/validation/test_driver.py` | 10 unit tests |
| `tests/integration/test_decomp_skipped.py` | 3 integration tests — end-to-end exit code 4, regression guard for `ibm1` and `partssupply` which must continue to translate |

### Verification

- Direct CLI on `decomp.gms` → exits 4 with `MultiSolveDriverError` message
- `--allow-multi-solve` → succeeds with a yellow stderr warning (dev only)
- `ibm1` (1 model, 5 solves on it) and `partssupply` (2 models, 2 targets, no
  `eq.m` feedback) continue to translate as before — regression-guarded

### Fix-path alternatives, and why they were rejected

- **Emit `.m` as multiplier levels** (`tbal.m` → `nu_tbal.l`): would suppress the
  GAMS compile error but still cannot reproduce `mobj = 60` — a single KKT
  snapshot does not equal the DW converged value. Rejected.
- **Loop unrolling / multi-stage reformulation**: out of scope for nlp2mcp's
  single-NLP-to-MCP mandate. Rejected.

Fully documented under `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md`
(§ "Why Not Fix The Emission Bugs").
