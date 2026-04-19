# decomp: KKT Assembly Drops Gradient Terms Under Multi-Model `_solve_objectives`

**GitHub Issue:** [#1269](https://github.com/jeffreyhorn/nlp2mcp/issues/1269)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Medium — Silent correctness bug; affects any source file that declares multiple `Model` blocks with distinct objective variables
**Date:** 2026-04-18
**Last Updated:** 2026-04-18
**Affected Models:** any source file with ≥2 `Model` declarations and ≥2 distinct solve targets (currently `decomp` + `danwolfe` only, both excluded by the multi-solve-driver gate; future single-model multi-solve files would also hit this if the gate is extended)
**Labels:** `sprint-25`

---

## Problem Summary

When a GAMS source declares multiple `Model` blocks with different objective variables — e.g., `Model sub / ... /; Model master / ... /;` with solve statements `solve sub minimizing tank` and `solve master minimizing mobj` — the KKT assembly pipeline silently drops gradient terms for equations that belong to the non-selected model.

Concretely on `decomp`:

- `src/ir/normalize.py::normalize_model` correctly keeps all three equations (`cbal`, `tbal`, `convex`) in `ModelIR.equations`.
- Downstream KKT assembly / emission produces stationarity only for `cbal`'s variables and emits zero gradient contributions from `tbal` / `convex` — as if those equations didn't exist. The resulting MCP is structurally under-constrained.

Root cause suspicion: `_solve_objectives` is a dict keyed by model name (`{sub: ObjectiveIR(objvar=tank), master: ObjectiveIR(objvar=mobj)}`). The objective-extraction step picks one entry (ordering-dependent) and the rest of KKT assembly walks only that objective's gradient closure, quietly skipping equations tied to the other model's constraints.

---

## Why This Was Deferred

Same reason as #1268: `decomp` and `danwolfe` are Dantzig–Wolfe driver scripts whose catalog objectives are iterative fixed points. Fixing KKT assembly would not recover either model's reference value, so the fix was skipped in favor of the gate (PR #1265).

The bug still matters for:

1. **Any future single-model multi-solve** that declares a second placeholder `Model` (e.g., for diagnostic purposes) — silently produces wrong KKT.
2. **Extension of the multi-solve gate** (see #1270) that keeps such files in-scope.
3. **Schema soundness** — the IR currently accepts multi-model declarations without defining the semantics. Declaring semantics one way or the other eliminates ambiguity.

Full deferral rationale: `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md` §"Why Not Fix The Emission Bugs" #2.

---

## Reproduction

Use `--allow-multi-solve` to bypass the gate and inspect the resulting MCP:

```bash
.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms \
    --allow-multi-solve -o /tmp/decomp_mcp.gms
grep -E "stat_|tbal|convex" /tmp/decomp_mcp.gms
```

Expected behavior after fix: stationarity equations reference `tbal` / `convex` terms (or the docs explicitly declare multi-model declarations out of scope and the CLI refuses before KKT assembly).

---

## Root Cause Investigation Needed

The bug originates in the coupling between:

- `ModelIR._solve_objectives` (Sprint 22 addition, Issue #1154): dict storing per-model objective info
- `src/ir/normalize.py::normalize_model` (lines ≈164–192): objective extraction and equation pruning
- `src/ir/model_ir.py::get_solved_model_equations`: selects which equations feed KKT

Questions to answer in Sprint 25:

1. Which entry of `_solve_objectives` does `normalize_model` currently select, and on what basis (first-inserted? last-solved? alphabetical?)?
2. Are the "orphaned" equations (`tbal`, `convex` in `decomp`) filtered by `model_equation_map[selected_model]`, or do they pass through and only lose gradients downstream?
3. Is the intent to emit KKT for a single model (the last `solve` target seems most natural) and drop the rest, or to emit a joint system?

---

## Proposed Semantics (For Discussion)

Recommended: **emit KKT for exactly one solved model (the last `solve` statement's target)** and explicitly refuse multi-model declarations where this heuristic is ambiguous. Enforce the decision in `validate_single_optimization` (alongside the multi-solve-driver gate) rather than in normalize/KKT-assembly, so the error is raised early with a clear message.

---

## Out of Scope (Do NOT Reopen)

- Decomposition semantics: covered by multi-solve-driver gate; `decomp`/`danwolfe` stay excluded regardless of this fix.
- Emitter attr_access bug: tracked as #1268.

---

## Regression Guards

After any fix:

- `ibm1` (single declared model, 5 solves on it) must continue to translate and match. Covered by `tests/integration/test_decomp_skipped.py::test_cli_does_not_flag_ibm1` and the synthetic-fixture companion `test_cli_does_not_flag_synthetic_single_model_multi_solve`, plus the unit-level guard `tests/unit/validation/test_driver.py::test_scan_single_model_multi_solve_is_not_driver`.
- `partssupply` (2 declared models, 2 distinct solve targets, no equation-marginal feedback) must continue to translate and match — this is the canary for the "multi-model without driver loop" pattern. Covered by `tests/unit/validation/test_driver.py::test_scan_partssupply_style_variable_level_is_not_driver`. An integration-level CLI guard for `partssupply` is NOT currently in `tests/integration/test_decomp_skipped.py`; consider adding one as part of this fix so end-to-end parity matches the ibm1 coverage.

---

## Estimated Effort

4–6 hours (root-cause hand-tracing + semantics decision + targeted fix + regression tests).

---

## References

- `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md` §"Why Not Fix The Emission Bugs" #2
- `docs/issues/completed/ISSUE_1222_decomp-multi-solve-benders-unsupported.md`
- PR #1265 (merged) — multi-solve gate
- Sibling issues: #1268 (emitter), #1270 (gate extension), #1271 (dispatcher refactor)

---

## Files Involved

- `src/ir/normalize.py` (lines ≈164–192)
- `src/ir/model_ir.py::get_solved_model_equations`
- `src/validation/driver.py` (possibly extended to refuse ambiguous multi-model declarations)
- `src/kkt/` (stationarity assembly consumers of `_solve_objectives`)
