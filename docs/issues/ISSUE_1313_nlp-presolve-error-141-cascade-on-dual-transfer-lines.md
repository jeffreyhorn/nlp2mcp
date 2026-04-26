# `--nlp-presolve` Error 141 Cascade on Dual-Transfer Lines (qabel/abel/ganges)

**GitHub Issue:** [#1313](https://github.com/jeffreyhorn/nlp2mcp/issues/1313)
**Status:** OPEN — targeted for Sprint 26
**Severity:** Medium — blocks the warm-start verification path for non-convex models; doesn't affect normal MCP emission
**Date filed:** 2026-04-25
**Discovered:** Sprint 25 Day 5 investigation (DAY5_PATTERN_A_INVESTIGATION.md), re-surfaced Day 8 as the architecturally-right answer for abel's non-convex residual
**Related:**
- `#1150` (qabel/abel — partially resolved by #1311 + #1312; this is the remaining piece for abel)
- `#1311` (RESOLVED — AD u-criterion-gradient drop)
- `#1312` (RESOLVED — `_is_concrete_instance_of` prefix-heuristic fix)
- `gamslib_status.json` abel entry: now flagged `convexity.status: non_convex` to document the indefinite-Hessian classification while this warm-start path remains broken

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
