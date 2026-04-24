# launch: Pattern C Bug #1 — Phantom ±N IndexOffsets on Alias-Only Conditional Sums

**GitHub Issue:** [#1306](https://github.com/jeffreyhorn/nlp2mcp/issues/1306)
**Status:** RESOLVED in Sprint 25 Day 6 (PR #1308)
**Severity:** High — KKT stationarity emits terms that don't correspond to any source derivative, producing an incorrect but syntactically valid MCP
**Date filed:** 2026-04-24
**Parent investigation:** `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md`
**Affected Models:** launch (+ anything else with `sum(alias$condition(alias, eq_domain_idx), ...)` body shape)

---

## Problem Summary

When a source equation contains an alias-only conditional sum — alias summed over its base set with a `$` condition that ties the summed alias to the equation's domain — the KKT stationarity emitter produces phantom ±N multiplier offsets in the emission, even though the source body has NO `IndexOffset` on any index.

Concretely, launch's `dweight`:

```gams
dweight(s)..  weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss))
                            + instweight + pl;
```

has no `iweight(ss+1)` / `iweight(ss-1)` — just an unconditionally plain alias binding under a `ge(ss,s)` filter. Pre-fix, the emitter generated a `stat_iweight` whose multiplier terms spanned offsets 0, +1, +2, -1, -2:

```gams
stat_iweight(s)..  ... + iwf(s) * nu_diweight(s)
  + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+1))$(ord(s) <= card(s) - 1))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s+2))$(ord(s) <= card(s) - 2))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-1))$(ord(s) > 1))
  + sum(ss, (((-1) * 1$(ge(ss,s))) * nu_dweight(s-2))$(ord(s) > 2))
  + ... =E= 0;
```

The four `nu_dweight(s±N)` terms are phantom — they don't correspond to any
`IndexOffset` in the source.

---

## Reproduction

```bash
python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms --skip-convexity-check
grep "^stat_iweight" /tmp/launch_mcp.gms
```

Synthetic minimal reproducer lives in
`tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets`.
The test builds a 3-element set + alias + conditional sum mirroring launch's
`dweight` and asserts the emitted `stat_iweight` has no `nu_dweight(s+N)`
or `nu_dweight(s-N)` terms.

---

## Root Cause

`src/kkt/stationarity.py::_compute_index_offset_key` groups Jacobian entries
by **positional difference** between the concrete equation instance and the
concrete variable instance (member position in the underlying set). The
Jacobian entries for launch's `dweight`/`iweight` pair span cross-element
(eq_s, var_s) combinations because `sum(ss$ge(ss,s), iweight(ss))`
iterates the alias over all elements that satisfy the condition — producing
multiple entries per `(s_eq, s_var)` pair where `s_eq != s_var`.

`_compute_index_offset_key` interprets each non-zero positional delta as a
separate offset group. Downstream, `_add_indexed_jacobian_terms` treats each
group as a lead/lag pattern and emits a multiplier with an `IndexOffset`
index — yielding `nu_dweight(s±N)`.

The bug: positional offset in the Jacobian is an artifact of alias
iteration, not a source-level lead/lag. The emitter was conflating the two.

---

## Fix (Sprint 25 Day 6, PR #1308)

Added a source-body gate in `_add_indexed_jacobian_terms` that suppresses
phantom enumeration when the combination of source features matches the
launch shape. Two helpers:

- `_body_has_index_offset_on_sets(expr, target_sets, model_ir)` — True iff
  any `IndexOffset` node in the body has a base index (after alias
  resolution) referring to a set in `target_sets`. Both circular and
  non-circular offsets count (paklive's `xtransf(n,t--1)` is a circular
  case that must NOT be suppressed).
- `_body_has_aliased_conditional_sum_over_sets(expr, target_sets, model_ir, eq_domain)`
  — True iff the body contains a `Sum` whose summed index aliases the
  variable's domain AND whose condition references the equation's own
  domain index. This is the launch-shaped fingerprint.

Gate logic: if BOTH (a) the body has no real `IndexOffset` on the variable's
domain AND (b) the body has a launch-shaped conditional alias sum, all
non-zero / non-SENTINEL offset keys collapse to a single zero-offset key.

Scope deliberately narrow:
- **Fires on** launch's `dweight(s).. ... =e= sum(ss$ge(ss,s), ...)`.
- **Leaves alone** plain alias-iteration sums (quocge's `sum(i, ax(i,j)*pq(i))`,
  prolog's `sum(j, a(i,j)*q(j,t))`) because they lack the
  equation-domain-linked condition.
- **Preserves real lead/lag** (paklive's `xtransf(n,t--1)`, twocge #1277,
  qabel/abel's stateq) because condition (a) fails.

---

## Verification

- Synthetic unit test `test_pattern_c_alias_offset_gate.py`: fails on main, passes post-fix.
- Launch `stat_iweight`: all four phantom `nu_dweight(s±N)` terms gone;
  `iwf(s) * nu_diweight(s)` intact; residual alias-sum term remains (see
  §"Related — Bug #2").
- Tier 0 + Tier 1 canaries (11 models): byte-identical to golden files.
- Full pytest: 4576 passed.

---

## Related — Bug #2

After this fix, the residual `sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))`
term still exhibits a separate defect: the multiplier `nu_dweight(s)` does
NOT depend on the summed index `ss`, so the `sum` degenerates into a
spurious `card(ss-satisfying-ge)` multiplicative factor. This is tracked
as issue [#1307](https://github.com/jeffreyhorn/nlp2mcp/issues/1307) and
was deliberately kept out of scope for Sprint 25 Day 6 so the phantom-offset
fix could land without conflating two independent corrections.

---

## Files

- `src/kkt/stationarity.py` — new helpers
  `_body_has_index_offset_on_sets`, `_body_has_aliased_conditional_sum_over_sets`,
  `_expr_mentions_indices_canonical`; gate wired into `_add_indexed_jacobian_terms`.
- `tests/unit/kkt/test_pattern_c_alias_offset_gate.py` — regression test.
- `data/gamslib/raw/launch.gms` — real-world reproducer.

## Status

Resolved in Sprint 25 Day 6 PR #1308. Full 54-set regression sweep deferred
to Day 7 per the Sprint 25 plan (see
`docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md` §"Day 7 Prompt").
