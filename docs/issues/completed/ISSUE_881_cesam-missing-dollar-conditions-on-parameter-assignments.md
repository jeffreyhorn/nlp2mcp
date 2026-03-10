# cesam: Missing Dollar Conditions on Computed Parameter Assignments

**GitHub Issue:** [#881](https://github.com/jeffreyhorn/nlp2mcp/issues/881)
**Status:** FIXED
**Severity:** High — Model compiles but 6 execution errors block solve
**Date:** 2026-02-25
**Affected Models:** cesam
**Fixed:** 2026-03-09

---

## Problem Summary

Several computed parameter assignments in the emitted cesam MCP were missing dollar conditions
that guard against division by zero and log-domain errors. The original GAMS model uses dollar
conditions like `$SAM(ii,jj)` and `$T1(i,j)` to skip assignments where the denominator is
zero, but the emitter dropped these conditions.

Additionally, set assignments with dollar conditions on the LHS (e.g., `red(ii,jj)$(T0(ii,jj)<0) = yes`)
were not preserving the conditions, and the post-solve `.l` assignment (`DENTROPY.l = sum(...)`)
was incorrectly overwriting the pre-solve initialization.

---

## Root Cause Analysis

Three separate issues contributed to the execution errors:

### 1. LHS Dollar Conditions on Parameter Assignments (5 of 6 errors)
**Fixed by Issue #1015** (LhsConditionalAssign): The `LhsConditionalAssign` AST node now
preserves dollar conditions on the LHS of parameter assignments. This fixed the Abar0, percent1,
and other dollar-conditioned assignments.

### 2. Post-Solve `.l` Assignment Overwrite (1 error)
`DENTROPY.l = sum(...)` at line 601 of the original file is a post-solve computation that
should NOT be emitted in the MCP. The parser's last-write-wins semantics picked it up and
emitted `DENTROPY.l = sum((ii,jj)$(nonzero(ii,jj)), ...)` which evaluates to `log(0)` at
initialization time (before `a.l` has been solved).

**Fix:** Added `_solve_seen` flag to the parser. Once a `solve` statement is encountered,
subsequent `.l` assignments are skipped.

### 3. Missing Dollar Conditions on Set Assignments + Emission Ordering
Set assignments like `red(ii,jj)$(T0(ii,jj) < 0) = yes` and `NONZERO(ii,jj)$(Abar1(ii,jj)) = yes`
were either missing conditions or emitted in the wrong order relative to their computed parameter
dependencies.

**Fix:** Two-part solution:
- **DollarConditional embedding:** For conditional set assignments, the LHS condition is embedded
  in the expression as `DollarConditional(yes, T0(ii,jj) < 0)`, producing `set(i) = yes$(cond)`.
  In GAMS this is not, in general, semantically equivalent to `set(i)$cond = yes` (the RHS-dollar
  form clears membership when `cond` is false, while the LHS-dollar form leaves existing membership
  unchanged). The rewrite is safe here because these sets are dynamic subsets that start empty, so
  the two forms coincide for the generated code. The rewrite is guarded to only apply when the
  target set has no declared members.
- **Interleaved emission:** New `emit_interleaved_params_and_sets()` function uses statement-level
  topological sorting to interleave set assignments with computed parameter expressions in the
  correct dependency order. This handles the chain: `SAM → T0 → red → redsam → T1 → Abar1 → nonzero`.

---

## Fix Details

### Files Modified

| File | Change |
|------|--------|
| `src/ir/parser.py` | Added `_solve_seen` flag to skip post-solve `.l` assignments; embed LHS conditions on set assignments as `DollarConditional` in expression |
| `src/emit/original_symbols.py` | New `emit_interleaved_params_and_sets()` for statement-level interleaved emission; added `only_indices` to `emit_set_assignments`; added `exclude_params` to `emit_subset_value_assignments` |
| `src/emit/emit_gams.py` | Use interleaved emitter when set-blocked params detected; fall back to original early-params approach otherwise |

### Key Emission Order (cesam)

```
$onImplicitAssign
sam(i,j) = sam(i,j) / scalesam;
t0(ii,jj) = SAM(ii,jj);
...
red(ii,jj) = yes$(T0(ii,jj) < 0);     * set assignment interleaved with params
redsam(ii,jj)$(red(ii,jj)) = T0(ii,jj);
...
t1(ii,jj) = T0(ii,jj) - redsam(ii,jj);
...
abar1(ii,jj) = T1(ii,jj) / sam("total",jj);
...
nonzero(ii,jj) = yes$(Abar1(ii,jj));   * second set assignment after its deps
$offImplicitAssign
```

---

## Verification

- Model parses and translates successfully
- Solve result: `path_solve_license` (expected — cesam uses PATH solver which requires license)
- All 4039 unit tests pass
- Full pipeline: 152/157 models parse successfully (unchanged)

---

## Related Issues

- **Issue #1015** (fixed): LhsConditionalAssign — preserved 5 of 6 dollar conditions
- **Issue #878** (fixed): cesam parameter assignment ordering — prerequisite
- **Issue #874** (fixed): cesam emitter quoting and table errors
