# egypt: Translate regression — variable `up_expr_map` key mismatch + multi-pattern Jacobian warning

**GitHub Issue:** [#1343](https://github.com/jeffreyhorn/nlp2mcp/issues/1343)
**Status:** RESOLVED (2026-05-03)
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (translate stage)
**Date:** 2026-05-03
**Affected Models:** egypt (SEQ=94, LP, Egypt Agricultural Model)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`egypt` translated successfully at the Sprint 25 Day 0 baseline (and historically failed *only* at the solve stage with `path_solve_license` because the MCP exceeds the demo license — see #927). On the current branch the translate stage now fails:

```
Variable 'xcrop' up_expr_map key ('r', 'cup') does not match domain ('r', 'c'). Skipping.
Variable 'xcrop' up_expr_map key ('r', 'cup') does not match domain ('r', 'c'). Skipping.
/Users/jeff/experiments/nlp2mcp/src/kkt/stationarity.py:1662: UserWarning: Multi-pattern Jacobian: detected 2 derivative patterns for gfodb/fodder but could not pair a minority entry with a majority entry sharing the same column. Correction term skipped; minority entries may be inaccurate.
```

Translation now exits with `unsup_expression_type` instead of producing the historically-license-rejected MCP.

---

## Reproduce

```bash
.venv/bin/python -m src.cli translate data/gamslib/raw/egypt.gms -o /tmp/egypt_mcp.gms
```

Expected: `data/gamslib/mcp/egypt_mcp.gms` written (license-blocked at solve, but translate clean).
Actual: warnings + non-zero exit.

---

## Source Context

`egypt.gms` declares `xcrop` on `(r, c)` and assigns `xcrop.up(r, cup) = ...` where `cup` is a subset of `c`. The translator stores the assignment under key `(r, cup)` but the validator compares against the declared domain `(r, c)` and rejects the key, dropping the bound.

The `gfodb`/`fodder` multi-pattern Jacobian warning is a separate consequence: with `xcrop.up` dropped, the AD/stationarity assembly sees a different effective constraint set and finds two derivative patterns it can't pair.

---

## Comparison to Day 0 Baseline

| Stage | Day 0 baseline | Day 11 (this branch) |
|---|---|---|
| parse | success | success |
| translate | success | **failure (`unsup_expression_type`)** |
| solve | failure (`path_solve_license`) | not_tested |

---

## Suspected Cause

Same `up_expr_map` validator regression as `shale`. The key compare should normalize subset names to declared-domain names (or accept subset aliases), not drop the bound.

The Jacobian "multi-pattern" warning at `src/kkt/stationarity.py:1662` may have been added during Sprint 25 to detect a real bug, but is fired here because the upstream bound-storage regression masked the input — fix the upstream regression first, re-evaluate the warning.

---

## Acceptance Criteria

- `egypt` translate exits clean (no `up_expr_map` mismatch on `xcrop`).
- The `gfodb/fodder` multi-pattern Jacobian warning either disappears (preferred — was a downstream symptom) or is investigated as a separate finding.
- Solve stage produces the historical `path_solve_license` outcome (license-limit) — translate must not regress beyond Day 0.

---

## Related

- #927 (open) — egypt MCP exceeds demo license; the *historical* egypt issue.
- `shale` regression (sister issue) — same `up_expr_map` mismatch family.
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
