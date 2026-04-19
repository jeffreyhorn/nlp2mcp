# decomp: `bound_scalar` / `bound_indexed` Handlers Missing in `_loop_tree_to_gams_subst_dispatch`

**GitHub Issue:** [#1268](https://github.com/jeffreyhorn/nlp2mcp/issues/1268)
**Status:** OPEN — Deferred to Sprint 25
**Severity:** Medium — Silently emits invalid GAMS (`Error 140`) for any single-model multi-solve script that reads `eq.m` / `var.l` / `x.up` / `x.lo` / `x.fx` inside a loop body
**Date:** 2026-04-18
**Last Updated:** 2026-04-19
**Affected Models:** any single-model multi-solve script that passes the `multi_solve_driver_out_of_scope` gate and has bound-attribute reads inside a loop (none currently in the in-scope corpus; surfaced by `decomp` investigation)
**Labels:** `sprint-25`

---

## Problem Summary

`src/emit/original_symbols.py` has two loop-body dispatchers:

- `_loop_tree_to_gams` — no token substitution (canonical path)
- `_loop_tree_to_gams_subst_dispatch` — applies a token-substitution map during emission (used for pre-solve parameter assignments inside loops)

The **substituting** dispatcher is missing rule handlers for `bound_scalar` and `bound_indexed` nodes. The GAMS grammar (`src/gams/gams_grammar.lark`) tokenizes the bound-attribute keywords `.l`, `.m`, `.lo`, `.up`, `.fx` as the `BOUND_K` terminal, so reads like `tbal.m` / `util.l` / `x.up` parse to `bound_scalar` / `bound_indexed` nodes — **not** `attr_access` / `attr_access_indexed`, which the grammar reserves for non-bound attributes like `.val` / `.stage` / `.scaleOpt` (and which the substituting dispatcher already handles at lines 3109–3115).

When `bound_scalar` / `bound_indexed` nodes fall through to the generic space-joining fallback at the bottom of the substituting dispatcher, the grammar's silent `.` token is lost and the emitter produces output like:

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

- `src/emit/original_symbols.py::_loop_tree_to_gams` (canonical, defined at ~line 2556) handles `bound_indexed` at ~line 2632 and `bound_scalar` at ~line 2639, emitting `<symbol>.<attr>` (and the indexed variant with parentheses) with no surrounding spaces. The `attr_access` / `attr_access_indexed` branches in the canonical dispatcher are at ~lines 2645 / 2649 and handle the **non-bound** attribute rules (`.val`, `.stage`, etc.).
- `src/emit/original_symbols.py::_loop_tree_to_gams_subst_dispatch` (substituting variant, defined at ~line 3047) **does** handle `attr_access` / `attr_access_indexed` (lines 3109–3115) but **lacks** `bound_scalar` / `bound_indexed` handlers entirely. Unmatched tree nodes fall through to the generic `" ".join(children)` fallback at line 3165, which drops silent tokens like `.`.

The fix is a direct port of the `bound_scalar` / `bound_indexed` branches from the canonical dispatcher.

---

## Suggested Fix

1. Copy the `bound_scalar` / `bound_indexed` branches from `_loop_tree_to_gams` (~lines 2632–2644) into `_loop_tree_to_gams_subst_dispatch`, routing child recursion through `_tree_to_gams_subst` instead of `_loop_tree_to_gams` so the substitution map applies to the symbol name.
2. The attribute keyword itself (`l`, `m`, `lo`, `up`, `fx`) is a `BOUND_K` token — do NOT apply substitution to it.
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

- `src/emit/original_symbols.py` — canonical dispatcher `_loop_tree_to_gams` (~line 2556 onward, with `bound_*` branches at ~2632–2644) and substituting dispatcher `_loop_tree_to_gams_subst_dispatch` (~line 3047 onward)
- `src/gams/gams_grammar.lark` (`BOUND_K` terminal at ~line 375; `ref_bound` / `cond_bound` rules at ~365–370 and ~451–453)
- `tests/unit/emit/` (new test file, or addition to an existing `test_loop_emit_*.py`)
