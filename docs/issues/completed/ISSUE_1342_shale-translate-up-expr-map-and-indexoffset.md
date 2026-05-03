# shale: Translate regression — variable `up_expr_map` key mismatch + `Unknown expression type: IndexOffset`

**GitHub Issue:** [#1342](https://github.com/jeffreyhorn/nlp2mcp/issues/1342)
**Status:** RESOLVED (2026-05-03)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** shale (SEQ=334, LP, Investment Planning in the Oil Shale Industry)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`shale` translated successfully at the Sprint 25 Day 0 baseline. On the current branch translate emits domain-mismatch warnings on two variables (`uur`, `uug`) and ultimately fails with the `IndexOffset` family error:

```
Variable 'uur' up_expr_map key ('crr', 'i', 't') does not match domain ('c', 'i', 'tf'). Skipping.
Variable 'uug' up_expr_map key ('crg', 'i') does not match domain ('c', 'i'). Skipping.
Variable 'uur' up_expr_map key ('crr', 'i', 't') does not match domain ('c', 'i', 'tf'). Skipping.
Variable 'uug' up_expr_map key ('crg', 'i') does not match domain ('c', 'i'). Skipping.
Error: Invalid model - Unknown expression type: IndexOffset
```

The `up_expr_map` key contains subset names (`crr`, `crg`, `t`) where the variable's declared domain expects the parent set element (`c`, `tf`). The skipped bound expressions then leave the IR in a state where downstream emit hits an unhandled `IndexOffset`.

---

## Reproduce

```bash
.venv/bin/python -m src.cli translate data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms
```

Expected: `data/gamslib/mcp/shale_mcp.gms` written, exit 0.
Actual: warnings above + non-zero exit.

---

## Source Context

`shale.gms` declares `uur` and `uug` upper-bound parameter expressions on subset domains (`crr`, `crg`, `tf`) that are subsets of (`c`, `t`). Look in `shale.gms` for `uur.up(...) =` and `uug.up(...) =` assignments to confirm the index labels used.

The IR's `up_expr_map` stores keys as the *index expression labels* used in the assignment, but the validator compares against the *declared domain* — so when the source uses subset labels in the assignment (as `shale` does idiomatically), the keys don't match and the bound is dropped.

---

## Comparison to Day 0 Baseline

| Stage | Day 0 baseline | Day 11 (this branch) |
|---|---|---|
| parse | success | success |
| translate | success | **failure (`unsup_expression_type`)** |
| solve | success | not_tested |

---

## Suspected Cause

Two-part regression, may have a single root cause:

1. **`up_expr_map` key/domain comparison** — the mismatch warning is in `src/ir/parser.py` or `src/kkt/` where bound expressions are stored. The key should be normalized to the declared domain (or comparison should accept subset-name aliases).
2. **`IndexOffset` dispatcher** — same family as `catmix`/`glider`/`markov`/`tricp`. The two may be linked: dropping the bound may leave a placeholder that downstream code treats as an `IndexOffset`.

Issue #1015 (closed) addressed an alias-index-literal-in-parameter-assignment for shale and may share machinery with the current `up_expr_map` regression.

---

## Acceptance Criteria

- `shale` translates without `up_expr_map` warnings (or the warnings are downgraded to debug-level and the bounds are correctly stored).
- `shale` translate completes with exit 0.
- Solve and comparison stages run.
- Add an integration test that translates `shale.gms` and asserts the warnings are absent and translate exits clean.

---

## Related

- #1005, #1015 (closed) — prior shale issues (alias/uncontrolled set in equation condition).
- IndexOffset sister issues: catmix, glider, markov, tricp.
- `egypt` translate regression has the same `up_expr_map` mismatch pattern (sister issue).
---

## Fix (2026-05-03)

**Status:** RESOLVED — translate now succeeds with no `up_expr_map` warnings; emitted MCP compiles clean and carries the correct subset guard.

### Root cause

`src/kkt/partition.py::_process_expr_map_bound` rejected any `up_expr_map`/`lo_expr_map` key whose index names were not byte-equal (case-insensitive) to the variable's declared domain. GAMS source idiomatically writes:

- egypt: `xcrop.up(r, cup) = upbnds(cup, r);` where `xcrop(r, c)` and `cup(c)` is a subset of `c`.
- shale: `uur.up(crr, i, t) = bbr(crr);` where `uur(c, i, tf)`, `crr(c)` ⊂ `c`, and `t(tf)` ⊂ `tf`.

The validator dropped these bounds with `Variable '...' up_expr_map key (...) does not match domain (...). Skipping.`, silently losing the upper-bound expressions and (for egypt + shale, where they are part of the constraint set) damaging the KKT structure downstream.

### Change

Updated `_process_expr_map_bound` to accept subset / alias key positions:

1. New helper `_is_subset_or_alias_of(candidate, parent, model_ir)` walks `SetDef.domain` parent chains and resolves `AliasDef` to determine whether `candidate` resolves to `parent`.
2. For each (key index, domain index) pair, if they differ but the key is a subset/alias of the domain set, record a rename and (for strict subsets) a `SetMembershipTest` guard.
3. New helper `_substitute_symbol_in_expr` reuses `src/ad/constraint_jacobian._substitute_indices` to rewrite the bound expression's symbol references from subset names to parent names.
4. When subset guards are present, wrap the rewritten expression in `LhsConditionalAssign(rhs=expr, condition=AND(guards))`. The complementarity assembler in `src/kkt/complementarity.py` already routes `LhsConditionalAssign.condition` into the comp pair guard, so the bound becomes `comp_up_xcrop(r, c)$(cup(c) and upbnds(c, r) < inf).. upbnds(c, r) - xcrop(r, c) =G= 0;` for egypt and `comp_up_uur(c, i, tf)$(crr(c) and t(tf) and bbr(c) < inf).. bbr(c) - uur(c, i, tf) =G= 0;` for shale.

Genuine mismatches (key index that is neither equal nor a subset of the domain index) still hit the original "Skipping." warning path — preserved historical behavior.

### Tests

Added three regression cases in `tests/unit/kkt/test_partition.py::TestExpressionBasedBounds`:
- `test_up_expr_map_subset_key_accepted_with_guard` — single-position subset (egypt pattern); asserts `LhsConditionalAssign` wrapping with `SetMembershipTest("cup", (SymbolRef("c"),))` and that the RHS is rewritten to use the parent index.
- `test_up_expr_map_subset_multi_position_combines_guards` — two-position subset (shale pattern); asserts AND of two guards.
- `test_up_expr_map_genuine_mismatch_still_skipped` — preserves the "Skipping." path for unrelated set keys.

### Verification

```
$ .venv/bin/python -m src.cli --skip-convexity-check data/gamslib/raw/shale.gms -o /tmp/shale_mcp.gms
✓ Generated MCP: /tmp/shale_mcp.gms      (no up_expr_map warnings)

$ .venv/bin/python -m src.cli --skip-convexity-check data/gamslib/raw/egypt.gms -o /tmp/egypt_mcp.gms
✓ Generated MCP: /tmp/egypt_mcp.gms      (no up_expr_map warnings)
```

Generated comp pairs:
```gams
# egypt
comp_up_xcrop(r,c)$(cup(c) and upbnds(c,r) < inf).. upbnds(c,r) - xcrop(r,c) =G= 0;
piU_xcrop.fx(r,c)$(not (cup(c) and upbnds(c,r) < inf)) = 0;

# shale
comp_up_uug(c,i)$(crg(c) and bbg(c) < inf).. bbg(c) - uug(c,i) =G= 0;
comp_up_uur(c,i,tf)$(crr(c) and t(tf) and bbr(c) < inf).. bbr(c) - uur(c,i,tf) =G= 0;
```

GAMS compile of both emitted MCPs returns 0 ERROR sections.

### Quality gate

- `make typecheck` → Success: no issues found in 98 source files
- `make lint` → All checks passed!
- `make format` → All checks passed!
- `make test` → 4715 passed, 10 skipped, 1 xfailed (was 4712; +3 new tests)
