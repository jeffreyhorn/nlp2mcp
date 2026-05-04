# china: Solve regression — `path_syntax_error` (`gio('g',item)` domain violation, set name emitted as string literal)

**GitHub Issue:** [#1348](https://github.com/jeffreyhorn/nlp2mcp/issues/1348)
**Status:** RESOLVED
**Severity:** High — Sprint 25 Day 11 Checkpoint 2 NO-GO contributor (solve, +1 path_syntax_error)
**Date:** 2026-05-03
**Affected Models:** china (SEQ=59, LP, Organic Fertilizer Use in Intensive Farming)
**Regression introduced:** between Sprint 25 Day 0 and Day 11

---

## Summary

`china` solved at Sprint 25 Day 0 baseline (model_optimal). On the current branch the GAMS compile of the emitted MCP fails with 6× `$170 Domain violation for element` and the solve never runs.

The emitter is rendering the SET name `g` (a subset of `ca`) as the string literal `'g'` in parameter assignments, instead of expanding the set iteration:

```gams
* Source (china.gms line 150):
gio(g,g) = -1;     ! diagonal of (g x g) submatrix

* Emitted (china_mcp.gms lines 92-97 — pre-fix):
gio('g','barley') = -1;
gio('g','wheat') = -1;
gio('g','e-rice') = -1;
gio('g','m-rice') = -1;
gio('g','l-rice') = -1;
gio('g','l-sc-rice') = -1;
```

`'g'` is not an element of the `ca` parent set — it's a subset name being incorrectly literalised.

---

## Resolution

Two related parser/emit bugs surfaced; both fixed.

### Fix 1: parser does not expand transitive subset indices (gio bug)

`src/ir/parser.py::_handle_assign` only matched the LHS-index expansion when the index name equalled the domain name (or was a direct alias). For china's `gio(g,g) = -1`:

- `gio.domain = ('ca', 'g')`
- `g.domain = ('c',)`, `c.domain = ('ca',)` — so `g ⊂ c ⊂ ca`
- Position 0: idx=`g`, domain=`ca`. `g` ≠ `ca` and `g` is not a direct alias of `ca` → not expanded → stored literally as `'g'`.
- Position 1: idx=`g`, domain=`g`. Direct match → expanded over g's members (correct).

Fix walks `resolved_idx.domain` parent chain and matches by SetDef identity. Now position 0 expands too. The repeated-symbol logic (#1105) ties the two positions to the same element, producing a diagonal pattern (`gio('barley','barley') = -1`, etc.).

The emitted parameter declaration now reads:

```gams
gio(ca,g) /barley.barley -1, wheat.wheat -1, 'e-rice'.'e-rice' -1, 'm-rice'.'m-rice' -1,
            'l-rice'.'l-rice' -1, 'l-sc-rice'.'l-sc-rice' -1, 'g-feed'.barley 1, …/
```

### Fix 2: `_substitute_indices` did not recurse into `LhsConditionalAssign` (purdata bug)

After Fix 1 unmasked compilation, china still failed with `$149 Uncontrolled set entered as constant` in `comp_up_purchase`:

```gams
comp_up_purchase(ca)$(cp(ca) and purdata(cp,"quantity") < inf)..
    purdata(cp,"quantity") - purchase(ca) =G= 0;
```

`purdata(cp,…)` should be `purdata(ca,…)`. The source `purchase.up(cp)$purdata(cp,"quantity") = purdata(cp,"quantity")` produces a `LhsConditionalAssign(rhs=…, condition=…)` in `purchase.up_expr_map[('cp',)]`. `_process_expr_map_bound` correctly identifies `cp` as a subset of `ca` and builds `rename_map = {'cp':'ca'}`, then calls `_substitute_symbol_in_expr` → `_substitute_indices`. But `_substitute_indices` had no `LhsConditionalAssign` case, so the wrapper passed through unchanged and the `cp` references inside the rhs/condition were never renamed.

Fix:
1. `src/ad/constraint_jacobian.py::_substitute_indices` now recurses into `LhsConditionalAssign(rhs, condition)`.
2. `src/kkt/partition.py::_process_expr_map_bound` now folds the subset-guard into the existing `LhsConditionalAssign.condition` (via `Binary("and", …)`) instead of double-wrapping when the expr is already an `LhsConditionalAssign`.

### Verification

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --model china --verbose
…
Translate Results: Success 1 (100.0%)
Solve Results:     Success 1 (100.0%)  ← was: failure / path_syntax_error
```

China now reaches `model_optimal` (objective = 27369.569). The objective doesn't match the NLP reference (40561.57), but this objective mismatch is **pre-existing at Day 0** (Day 0 MCP objective was -447.139, also a mismatch with the NLP reference) and is out of scope for this issue. The acceptance criteria of this issue concern compile-cleanness and `model_optimal` solver status, both of which are now met.

### Acceptance criteria status

- ✅ china translate emits `gio` without quoting the SET name. Diagonal pattern produced as `barley.barley -1, wheat.wheat -1, …`
- ✅ china_mcp.gms compiles with 0 errors.
- ✅ Solver returns `model_optimal`.
- ✅ Integration test added: `test_china_does_not_quote_set_name_in_diagonal_assignment` and `test_china_comp_up_purchase_substitutes_subset_index_in_body`.

---

## Related

- Sister `path_syntax_error` regressions: `pindyck` (#1349 — fixed by separate `.l`-side-effect preservation), `srkandw` (#1350).
- #1015, #1105 — earlier subset/alias-index fixes in `_handle_assign`.
