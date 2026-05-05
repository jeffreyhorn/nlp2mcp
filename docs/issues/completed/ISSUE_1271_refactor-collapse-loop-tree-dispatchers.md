# Refactor: Collapse `_loop_tree_to_gams` and `_loop_tree_to_gams_subst_dispatch` Into One Dispatcher

**GitHub Issue:** [#1271](https://github.com/jeffreyhorn/nlp2mcp/issues/1271)
**Status:** RESOLVED — Sprint 25 Day 12 (PR #1353)
**Severity:** Medium — Pure maintenance debt; actively causes bugs when new grammar-rule handlers are added
**Date:** 2026-04-18
**Last Updated:** 2026-05-05
**Affected Area:** `src/emit/original_symbols.py` loop-body emission paths
**Labels:** `sprint-25`

---

## Problem Summary

`src/emit/original_symbols.py` has two near-duplicate dispatcher functions that walk the same parse-tree shape and emit GAMS source:

- **`_loop_tree_to_gams`** — canonical path, no token substitution.
- **`_loop_tree_to_gams_subst_dispatch`** — same walker, but applies a token-substitution map during emission (used for pre-solve parameter assignments inside loops that must rewrite loop indices).

Every time a new grammar rule needs emitter support, a handler must be added in **both** functions. This has repeatedly caused silent-correctness bugs where the substituting path falls behind the canonical path:

- **Sprint 24 partssupply (PR #1264):** missing `dollar_cond` / `dollar_cond_paren` / `bracket_expr` / `brace_expr` / `yes_cond` / `no_cond` handlers. Fixed by copy-pasting from the canonical path.
- **Sprint 25 decomp (#1268):** missing `bound_scalar` / `bound_indexed` handlers (the grammar's forms for `.l` / `.m` / `.lo` / `.up` / `.fx` reads, tokenized as `BOUND_K` — NOT `attr_access`, which the substituting dispatcher already handles). Same class of bug.

Each occurrence takes 1–2 hours to diagnose and fix. They will keep recurring as the grammar grows.

---

## Why This Was Deferred

The copy-paste approach was the correct short-term call during Sprint 24 because:

1. Sprint 24's primary objective was alias differentiation, not emitter cleanup.
2. The unified dispatcher requires a full regression test (diff every translated MCP before/after) to be safe — that's ~1 hour of verification work alone.
3. Unifying during a sprint focused on correctness fixes risked conflating two unrelated diff lines.

Deferral note: `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_PARTSSUPPLY.md` §"Refactor opportunity".

---

## Proposal

Single parameterized dispatcher with an optional substitution map:

```python
def _loop_tree_to_gams(
    tree: Tree,
    *,
    token_subst: Mapping[str, str] | None = None,
) -> str:
    """Walk a loop-body subtree and emit GAMS source.

    When ``token_subst`` is None (default), behavior is identical to the
    pre-refactor ``_loop_tree_to_gams``. When provided, ID tokens are
    rewritten through the map during emission, matching the behavior
    previously in ``_loop_tree_to_gams_subst_dispatch``.
    """
```

The `_loop_tree_to_gams_subst_dispatch` name is removed (or kept as a thin wrapper during a deprecation period if external code imports it).

---

## Scope of Work

1. **Unify the two dispatchers.** Preserve every existing handler path exactly. The substitution point is a single `if token_subst is not None: name = token_subst.get(name, name)` inside each ID-emission branch.
2. **Update callers.** Every site that called `_loop_tree_to_gams_subst_dispatch(tree, subst_map)` now calls `_loop_tree_to_gams(tree, token_subst=subst_map)`.
3. **Regression test: full-corpus MCP diff.** Before/after, translate every currently-solving GAMSlib model (roughly 60 models) and byte-diff the generated `.gms` output. Any non-zero diff must be investigated. Commit the pre-refactor output to a tmpdir, not to the repo.
4. **Unit coverage.** Add tests under `tests/unit/emit/` that exercise both call shapes (with and without `token_subst`) across the handler classes — plain IDs, indexed refs, `attr_access`, `dollar_cond`, `sum` expressions, function calls. These pin the parity guarantee.
5. **Changelog.** Document the rename in `CHANGELOG.md` under `[Unreleased]`.

---

## Explicitly Out of Scope

- **Do not** take the opportunity to fix emission bugs in this PR. Bugs in the current emitter remain as bugs after the refactor; they are fixed in separate PRs (#1268, #1269). Mixing a mechanical refactor with behavior changes defeats the regression diff.
- **Do not** change the name of handler methods inside the unified dispatcher. Keep patches small and obviously equivalent.

---

## Regression Guards

- Full fast test suite (`make test`) — zero new failures.
- `scripts/gamslib/run_full_test.py --only-parse --quiet` — no new parse failures.
- Byte-diff of MCP outputs for all currently-solving models — zero diffs.

---

## Estimated Effort

- Mechanical unification: 2–3 hours.
- Full-corpus MCP diff regression: 1–2 hours (depending on corpus size on the developer machine).
- Unit test additions: 1 hour.
- **Total: 4–6 hours.**

---

## References

- `docs/planning/EPIC_4/SPRINT_24/PLAN_FIX_PARTSSUPPLY.md` §"Refactor opportunity"
- PR #1264 (merged) — latest change hitting both dispatchers
- Sibling issue: #1268 (the next emitter bug that will cost 1–2 hours under the current duplication)

---

## Files Involved

- `src/emit/original_symbols.py` — both dispatcher functions
- Any caller of `_loop_tree_to_gams_subst_dispatch` (grep for references)
- `tests/unit/emit/` — new parity tests
- `CHANGELOG.md` — `[Unreleased]` entry

---

## Resolution (Sprint 25 Day 12, PR #1353)

The two dispatchers were collapsed into a single parameterized function:

```python
def _loop_tree_to_gams(
    node,
    *,
    token_subst: Mapping[str, str] | None = None,
) -> str:
```

- The nested `_tree_to_gams_subst` / `_loop_tree_to_gams_subst_dispatch` functions (~140 LOC) were deleted from `src/emit/original_symbols.py`.
- Every handler branch that emits an identifier now applies `token_subst.get(name, name)` when the map is non-None; behavior is byte-identical to the pre-refactor canonical path when `token_subst is None`.
- Two call sites in `emit_pre_solve_param_assignments` were updated from positional dispatch (`_loop_tree_to_gams_subst_dispatch(stmt, p_sub)`) to keyword form (`_loop_tree_to_gams(stmt, token_subst=p_sub)` / `_loop_tree_to_gams(stmt, token_subst=l_sub)`).
- Defensive paren-wrap for compound-LHS in `dollar_cond` is gated on `token_subst is not None` so the no-substitution path remains byte-stable.

### Regression Verification

- Full-corpus MCP byte-diff: pre-refactor outputs snapshotted under `/tmp/sprint25-disp-pre/`, post-refactor outputs under `/tmp/sprint25-disp-post/`, both with `PYTHONHASHSEED=0`. Byte-diff across all 141 currently-translating gamslib models: **zero diffs**.
- `make test`: zero new failures.
- `scripts/gamslib/run_full_test.py --only-parse --quiet`: no new parse failures.

### Tests

`tests/unit/emit/test_original_symbols.py`:
- New `TestLoopTreeToGamsTokenSubst` class with three parity tests covering the no-subst canonical path, the subst path with ID rewriting, and a mixed handler-class scenario.
- Pre-existing `test_dollar_cond_handler` and `test_dollar_cond_paren_handler` updated to match the real parser's `[lhs_tree, DOLLAR_token, rhs_tree]` shape with `symbol_plain`-wrapped IDs.

### PR review hardening (PR #1353)

- Latent indexing bug fixed in `dollar_cond` / `dollar_cond_paren` branches: pre-refactor code read RHS from `children[1]`, which is the DOLLAR `Token` slot — the correct RHS lives at the second `Tree` child. The unified branch now filters to `tree_children` (skipping tokens) and uses `tree_children[1]` for RHS. Verified safe: pre-fix byte-diff snapshot shows no `$$` artifacts in any translated model (`grep -c '\$\$' /tmp/sprint25-disp-pre/*.gms` → all zero), so the bug had not yet been observed in the corpus but would have surfaced on any future `dollar_cond` whose pre-DOLLAR LHS was a `Tree` rather than a `Token`.
- Test fixtures aligned with the real parse-tree shape (3-element children including the DOLLAR token, IDs wrapped in `symbol_plain`), preventing future fixture drift.
