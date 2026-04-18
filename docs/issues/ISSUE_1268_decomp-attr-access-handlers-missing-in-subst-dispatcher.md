# decomp: `attr_access` Handlers Missing in `_loop_tree_to_gams_subst_dispatch`

**GitHub Issue:** [#1268](https://github.com/jeffreyhorn/nlp2mcp/issues/1268)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Medium — Silently emits invalid GAMS (`Error 140`) for any single-model multi-solve script that reads `eq.m` or `var.l` inside a loop body
**Date:** 2026-04-18
**Last Updated:** 2026-04-18
**Affected Models:** any single-model multi-solve script that passes the `multi_solve_driver_out_of_scope` gate and has `.m` / `.l` attribute reads inside a loop (none currently in the in-scope corpus; surfaced by `decomp` investigation)
**Labels:** `sprint-25`

---

## Problem Summary

`src/emit/original_symbols.py` has two loop-body dispatchers:

- `_loop_tree_to_gams` — no token substitution (canonical path)
- `_loop_tree_to_gams_subst_dispatch` — applies a token-substitution map during emission (used for pre-solve parameter assignments inside loops)

The **substituting** dispatcher is missing rule handlers for `attr_access` and `attr_access_indexed` nodes. These nodes are the parse-tree shape for `eq.m` / `var.l` / `x.fx` attribute reads. When they fall through to the generic space-joining fallback, the grammar's silent `.` token is lost and the emitter produces output like:

```gams
ctank = - tbal m ;
```

instead of

```gams
ctank = -tbal.m;
```

GAMS rejects the first form with `Error 140: Unknown symbol`.

---

## Why This Was Deferred

The two models in the GAMSlib corpus that triggered this bug — `decomp` and `danwolfe` — are **multi-solve Dantzig–Wolfe driver scripts**. They were categorically excluded from the nlp2mcp pipeline in Sprint 24 (PR #1265) because no single KKT snapshot can reproduce their converged iterative objective. Fixing the emitter bug would not recover either model's catalog reference value, so the emitter fix was deprioritized in favor of the gate.

However, the bug is **real and silent** for any future single-model multi-solve pattern (e.g., warm-start / rolling-horizon styles that read `var.l` between solves of the same model). These patterns are **not** caught by the multi-solve-driver gate, so they would hit this bug unannounced. Fixing the emitter now prevents a class of future silent corruption.

Full deferral rationale: `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md` §"Why Not Fix The Emission Bugs" #1.

---

## Reproduction

Tooling: the existing `decomp` source at `data/gamslib/raw/decomp.gms` triggers the bug under `--allow-multi-solve` (the dev escape hatch added in PR #1265):

```bash
.venv/bin/python -m src.cli data/gamslib/raw/decomp.gms \
    --allow-multi-solve -o /tmp/decomp_mcp.gms
gams /tmp/decomp_mcp.gms lo=0
# → Error 140 on line containing `ctank = - tbal m ;`
```

Inspect the offending output:

```bash
grep -n "tbal m\|tbal\.m" /tmp/decomp_mcp.gms | head -5
```

Expected after fix: `ctank = -tbal.m;` (single token, dot preserved).

---

## Root Cause (Code-Level)

- `src/emit/original_symbols.py::_loop_tree_to_gams` (canonical) handles `attr_access` / `attr_access_indexed` at approximately lines 3109–3115, emitting `<symbol>.<attr>` with no surrounding spaces.
- `src/emit/original_symbols.py::_loop_tree_to_gams_subst_dispatch` (substituting variant) lacks these handlers; unmatched tree nodes fall through to a generic `" ".join(children)` path that drops silent tokens like `.`.

The fix is a direct port of the canonical-path logic.

---

## Suggested Fix

1. Copy the `attr_access` / `attr_access_indexed` branch from `_loop_tree_to_gams` into `_loop_tree_to_gams_subst_dispatch`.
2. Confirm the symbol / attr tokens go through the same substitution map (substitution must NOT apply to the attr keyword itself).
3. Add a unit test for the substituting dispatcher that exercises a `<var>.l` read inside a loop body, asserting the rendered string contains `<var>.l` (no whitespace before `.`).

**Do not** do this as part of the larger dispatcher refactor — those are tracked separately (see #1271) to keep the diffs independently reviewable.

---

## Out of Scope (Do NOT Reopen)

- Decomposition semantics for `decomp`/`danwolfe`: covered by the multi-solve-driver gate (PR #1265, issue #1222). These models stay excluded.
- Dispatcher unification: tracked as #1271.
- KKT gradient dropping under multi-model `_solve_objectives`: tracked as #1269.

---

## Estimated Effort

1–2 hours (direct port + small regression test).

---

## References

- `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_DECOMP.md` §"Why Not Fix The Emission Bugs" #1
- `docs/issues/completed/ISSUE_1222_decomp-multi-solve-benders-unsupported.md` — the parent exclusion doc
- PR #1265 (merged) — multi-solve-driver gate
- Sibling issues: #1269 (KKT assembly), #1270 (gate extension), #1271 (dispatcher refactor)

---

## Files Involved

- `src/emit/original_symbols.py` (lines 3045–3137 — both dispatchers)
- `tests/unit/emit/` (new test file, or addition to an existing `test_loop_emit_*.py`)
