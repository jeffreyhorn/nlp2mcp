# lmp2: Dynamic-subset SET assignments inside multi-solve loops are not extracted into MCP pre-solve

**GitHub Issue:** [#1315](https://github.com/jeffreyhorn/nlp2mcp/issues/1315)
**Status:** RESOLVED — fixed alongside #1323 in PR (this branch)
**Severity:** Medium-High — blocked lmp2 compile (Error 66) even after #1281's Parameter-redefinition fix
**Discovered:** Sprint 25 Day 9 (PR #1314, post-#1281 verification)
**Fixed:** Sprint 25 (this branch)
**Affected Models:** lmp2 (observed); other multi-solve models with dynamic-subset assignments inside the solve-loop body would have shared the same shape

---

## Problem Summary

`emit_pre_solve_param_assignments` extracted PARAMETER assignments from the body of solve-containing loops (issue #1101/#1102), but NOT SET assignments — even though dynamic subsets like `m(mm)` were computed inside the same loop body and required for the MCP to compile.

For lmp2, the source has:

```gams
loop(c,
   m(mm)   = ord(mm) <= cases(c,'m');
   n(nn)   = ord(nn) <= cases(c,'n');
   ...
   solve lmp2 minimizing obj using nlp;
);
```

The MCP emitter:
- Auto-populated `n(nn) = yes;` because `n` was referenced in stat_x's domain guard.
- Did NOT populate `m(mm) = ...` — leaving `m` empty at solve time.

Result: GAMS rejected with `Error 66 equation stat_x.. symbol "m" has no values assigned`.

## Resolution Summary

Approach (1) from the issue's recommendation was implemented: extend `emit_pre_solve_param_assignments` to also extract dynamic-subset SET assignments from the solve-loop body. Identical structural fix also addresses #1323.

### Code changes

1. **`src/emit/original_symbols.py::emit_pre_solve_param_assignments`** — split the substitution map into two:
   - `loop_index_subst` (only loop indices → first members)
   - `param_subst` (loop indices + dynamic-subset → parent-set substitution)
   The walker now accepts assignments whose LHS is a parameter OR a dynamic-subset name. Parameter assignments use `param_subst`; set assignments use `loop_index_subst` so the LHS subset name (e.g., `m(mm)`) is preserved instead of being incorrectly rewritten to `mm(mm)`.

2. **`src/emit/original_symbols.py::collect_pre_solve_referenced_params`** — new helper that walks the same statements as `emit_pre_solve_param_assignments` and collects param-name ID tokens from the RHS / dollar-conditions of the extracted assignments. The LHS root is skipped to avoid pulling assigned-to params into model-relevance.

3. **`src/emit/emit_gams.py::_collect_model_relevant_params`** — calls `collect_pre_solve_referenced_params` so params referenced only via the new pre-solve subset assignments (e.g., `cases` in lmp2) become model-relevant and get their Table values emitted.

4. **`src/emit/original_symbols.py::emit_subset_value_assignments`** — fixed the mixed-key emission to force-quote literal element names that collide with declared sets when the position's declared domain is `*` (wildcard) or when the element is not a subset of the position's declared domain. Previously, `cases(c, *)` with literal column header `m` was emitted as `cases('c1', m) = 10`, causing GAMS to iterate over the (empty) set `m` and silently drop the value.

### Tests

- `tests/unit/emit/test_pre_solve_set_assignment.py` — 5 unit cases on a synthetic lmp2-shaped model.
- `tests/integration/emit/test_lmp2_set_extraction.py` — 3 integration cases on the lmp2 corpus.

### Verification

- Pre-fix: `gams lmp2.gms` → `Error 66: equation stat_x.. symbol "m" has no values assigned`.
- Post-fix: lmp2 emits `m(mm) = ord(mm) <= cases('c1','m');` and `n(nn) = ord(nn) <= cases('c1','n');` in the pre-solve section, plus the `cases` Table values force-quoted (`cases('c1','m') = 10;` etc). Error 66 is gone.
- `make typecheck && make lint && make format && make test`: all pass. Test suite: 4,647 passed, 10 skipped, 1 xfailed.

### Residual blocker (out of scope, filed separately)

After the structural Error 66 was fixed, lmp2 surfaces a different compile error:
```
**** 187  Assigned set used as domain
```
on `Positive Variables lam_Constraints(m)` and `Equations comp_Constraints(m)`. The KKT system declares the multiplier and complementarity equation over the dynamic subset `m` instead of its parent `mm`. Filed as issue #1327 for follow-up.

## Related

- `#1281` (resolved Sprint 25 Day 9): redundant `Parameter A/b/cc` declarations
- `#1243` (resolved earlier in this PR's branch): `1/y(p)` stat_y div-by-zero
- `#1323` (resolved jointly with this issue) — the same root cause re-filed during Sprint 25 Day 11
- `#1327` (NEW — filed during this fix) — `lam_Constraints` / `comp_Constraints` declared over dynamic subset, surfaces post-#1315/#1323 as Error 187
