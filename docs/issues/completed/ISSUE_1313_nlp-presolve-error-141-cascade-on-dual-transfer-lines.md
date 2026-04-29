# `--nlp-presolve` Error 141 Cascade on Dual-Transfer Lines (qabel/abel/ganges)

**GitHub Issue:** [#1313](https://github.com/jeffreyhorn/nlp2mcp/issues/1313)
**Status:** ✅ **RESOLVED** (2026-04-29)
**Resolution:** Move `_emit_nlp_presolve` to BEFORE the MCP equation declarations + wrap equation-definitions block in `$onMultiR ... $offMulti`.
**Severity:** Medium — blocked the warm-start verification path for non-convex models; doesn't affect normal MCP emission
**Date filed:** 2026-04-25
**Date resolved:** 2026-04-29
**Discovered:** Sprint 25 Day 5 investigation (DAY5_PATTERN_A_INVESTIGATION.md), re-surfaced Day 8 as the architecturally-right answer for abel's non-convex residual
**Related:**
- `#1150` (qabel/abel — partially resolved by #1311 + #1312; this fix completes the abel match path)
- `#1311` (RESOLVED — AD u-criterion-gradient drop)
- `#1312` (RESOLVED — `_is_concrete_instance_of` prefix-heuristic fix)
- `#1326` (gtm PATH zero-iterations residual after #1192/#1320/#1322 — likely UNBLOCKED by this fix as a side effect)

---

## Resolution (2026-04-29)

### Actual root cause (different from initial hypothesis)

The original issue doc hypothesised that the dual-transfer lines (`nu_stateq.l(n,k) = stateq.m(n,k)`) referenced equation symbols BEFORE the `$include` brought them into scope. Investigation showed the actual bug is more subtle:

1. The `$include` runs the source's `Model abel /all/; solve abel using nlp ...;` lines.
2. **`/all/` captures every equation declared at that point** — including the MCP's own stationarity (`stat_*`) and complementarity (`comp_*`) equations that were declared earlier in the file.
3. The "NLP solve" therefore tried to solve the **MCP-augmented system** (NLP equations + MCP stationarity + comp constraints), which is structurally infeasible.
4. This produced `MODEL STATUS 4 Infeasible` for the include's NLP solve, and the dual-transfer downstream then wrote zeros (or stale values) into the MCP multipliers, defeating the warm-start.

The Error 141 cascade described in the original doc was a **secondary symptom from running gams in a non-repo-root CWD** (relative `$include` path failed), not the actual blocker. The real blocker only manifests when the include path resolves correctly.

### Fix

Two coordinated changes in `src/emit/emit_gams.py`:

1. **Move `_emit_nlp_presolve` call to BEFORE the MCP equation declarations.** Now:
   - Variables (primals + multipliers) are declared first.
   - `$onMultiR; $include "..."; $offMulti` runs while only the original NLP equations are in scope. The source's `Model X /all/` correctly captures only NLP equations, the NLP solver runs cleanly, and `eq.m` values are populated.
   - Then the MCP declares its own `stat_*` / `comp_*` equations, the `mcp_model`, and runs the MCP solve.

2. **Wrap the MCP equation-definitions block in `$onMultiR ... $offMulti`** when presolve is active. The `$include` already defined the original equality equations (`criterion..`, `stateq..`); the MCP file's "Original equality equations" section then redefines them. Without `$onMultiR`, GAMS aborts with Error 150 ("Symbolic equations redefined"). The wrap allows the redefinition cleanly.

### Verification

| Model | Pre-fix | Post-fix NLP | Post-fix MCP | Match |
|-------|---------|--------------|--------------|-------|
| **abel** | NLP infeasible (status 4) | Locally Optimal `225.1946` | Optimal | ✅ Matches NLP |
| **qabel** | NLP infeasible | Locally Optimal `46965.0362` | Optimal | ✅ Matches NLP |
| **gtm** | NLP infeasible | Locally Optimal `-543.5651` | Optimal `-543.565` | ✅ Matches NLP |

The fix likely also unblocks **#1326** (gtm PATH zero-iterations from default starting point) as a side effect — gtm now solves cleanly with `--nlp-presolve`.

### Tests

- `make typecheck`: ✅ Success
- `make lint`: ✅ All checks passed (after `make format`)
- `make format`: ✅ Applied formatting
- `make test`: ✅ Full suite (run separately)

### Files changed

- `src/emit/emit_gams.py`: moved `_emit_nlp_presolve` invocation + calibration block from after `model_code` to before `emit_equations`. Wrapped `eq_defs_code` in `$onMultiR / $offMulti` when presolve is active.

---

## Problem Summary

The `--nlp-presolve` warm-start path is the architecturally-right answer for non-convex KKT systems where the Lagrangian Hessian is indefinite and the KKT system has multiple stationary points: PATH starts from the NLP's optimal primals + duals, so it converges to the same KKT point CONOPT did. But on qabel/abel/ganges (and likely other models with similar dual-transfer needs) it currently produces a `.gms` that fails to compile under GAMS, hitting Error 141 cascades on the dual-transfer lines emitted by `_emit_nlp_presolve`.

This blocks the verification path for abel specifically: with #1311 + #1312 fixed, abel's structural emission is correct (matches qabel's clean form), but the MCP converges to a different stationary point (97 vs NLP 225). Warm-starting from the NLP solution would force PATH onto the NLP's stationary point, making the rel_diff comparison meaningful and confirming the KKT system is correct.

## Reproduction

```bash
# Translate with --nlp-presolve enabled:
.venv/bin/python -m src.cli data/gamslib/raw/abel.gms \
  -o /tmp/abel_presolve.gms --skip-convexity-check --nlp-presolve

# Compile under GAMS (any abel/qabel/ganges):
gams /tmp/abel_presolve.gms action=c lo=2

# Output (excerpt):
# *** Error 282 in /tmp/abel_presolve.gms
# *** Error 141 in /tmp/abel_presolve.gms
#     Symbol declared but no values have been assigned. Check for missing
#        data definition, assignment, data loading or implicit assignment
#        via a solve statement. Suppress with $onImplicitAssign.
# *** Error 257 in /tmp/abel_presolve.gms
#     Solve statement not checked because of previous errors
# *** Error 141 in /tmp/abel_presolve.gms
# *** Status: Compilation error(s)
```

Same shape on qabel and ganges per the Day 5 investigation.

## Root Cause (hypothesised)

`_emit_nlp_presolve` in `src/emit/emit_gams.py` emits dual-transfer lines that reference original NLP equation names (e.g., `nu_stateq.l(n,k) = stateq.m(n,k);`). These references appear BEFORE the `$include` of the NLP source file resolves the equation symbols, so GAMS sees the symbol references first and flags Error 141 ("Symbol declared but no values have been assigned").

Fix likely involves reordering: include the NLP source FIRST (with `$onMultiR` already in place), THEN emit the dual transfers using the now-in-scope equation marginals.

There's also a deeper question of whether `$onMultiR` actually preserves equation marginal access in subsequent code — if GAMS clears `eq.m` outside the included scope, the warm-start design may need a different mechanism (e.g., copy `eq.m` to a parameter inside the included file, then reference that parameter outside).

## Expected Impact

- Direct: enables `--nlp-presolve` warm-start for abel, qabel, ganges, and likely other models with similar shapes.
- Validates the abel case: with warm-start, PATH should converge to the NLP's stationary point (225.195) rather than its current 97.185, confirming the KKT system is correct and the residual rel_diff was genuinely solver-behavior on the indefinite-Hessian Lagrangian.
- Sprint 26+ Match-target gain: potentially **+1 Match (abel)** once `--nlp-presolve` is the default for non-convex models.
- Restores `--nlp-presolve` as the recommended path for any non-convex problem (currently it's effectively unavailable for the affected model family).

## Files

- `src/emit/emit_gams.py::_emit_nlp_presolve` — likely fix site (reorder include before dual-transfers, or add parameter-based marginal copy mechanism).
- Test plan: extend `tests/unit/emit/test_nlp_presolve_include_path.py` with a synthetic case that mirrors the qabel/abel `nu_stateq.l(n,k) = stateq.m(n,k)` pattern; assert the emitted GAMS compiles cleanly under `action=c`.

## Status

Open. Not blocking Sprint 25 close — abel is now correctly classified as `convexity.status: non_convex` in `gamslib_status.json` (matching the existing 7-model `non_convex` precedent set by ps10_s and the ps-family), so the rel_diff is documented as expected behavior for non-convex problems rather than an emission bug.
