# launch: Pattern C Bug #2 — Mis-scoped `$(ge(ss, s))` Condition Inside `sum(ss, ...)` With Multiplier Not Indexed by `ss`

**GitHub Issue:** [#1307](https://github.com/jeffreyhorn/nlp2mcp/issues/1307)
**Status:** OPEN — targeted for Sprint 25 Day 13 buffer OR Sprint 26 carryforward
**Severity:** Medium — after Bug #1 (#1306) is fixed, this produces an incorrect numerical coefficient (spurious `card` factor) but the MCP still compiles
**Date filed:** 2026-04-24
**Parent investigation:** `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` §"Evidence — launch's `stat_iweight` is malformed" Bug #2
**Sibling issue:** [#1306](https://github.com/jeffreyhorn/nlp2mcp/issues/1306) (Bug #1 — phantom offsets; RESOLVED in Sprint 25 Day 6)
**Affected Models:** launch (+ potentially other models with the same source shape)

---

## Problem Summary

After Bug #1 (#1306) is fixed, launch's `stat_iweight` still emits a term
whose outer `sum(ss, ...)` does NOT iterate meaningfully: the body
multiplies a boolean-gated `1` with a multiplier `nu_dweight(s)` that is
fixed (does not depend on the summed index `ss`). The result is that the
`sum(ss, ...)` reduces to `card(ss-satisfying-ge(ss,s)) * nu_dweight(s) * -1`
— a spurious multiplicative `card` factor rather than a correct gated
single-term contribution.

Post-Bug-#1-fix emission (from launch's `stat_iweight`):

```gams
stat_iweight(s)..  ... + iwf(s) * nu_diweight(s)
  + sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
  + ... =E= 0;
```

Note the `nu_dweight(s)` inside `sum(ss, ...)` — the multiplier argument
is `s` (the equation's own domain index), not `ss` (the summed alias).
The `$(ge(ss, s))` condition gates the summed body by `ss`, so each
`ss` that satisfies `ge(ss, s)` contributes `-1 * nu_dweight(s)` —
they all add to the same value, yielding the `card(...)` factor.

Compare to launch's source body:

```gams
dweight(s)..  weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss))
                            + instweight + pl;
```

A correct stationarity for `iweight` w.r.t. this body should either:
- Have NO outer `sum(ss, ...)` and instead gate a single
  `nu_dweight(s_row)` term by the appropriate condition over the
  equation's domain `s`, OR
- Have the summed index and the multiplier argument aligned (e.g.
  `sum(s, nu_dweight(s) * 1$(ge(s_row, s)))` — summing over the
  equation's domain, with the multiplier indexed by the summed variable).

The current form is neither of those.

---

## Reproduction

After Sprint 25 Day 6 lands (PR #1308):

```bash
python -m src.cli data/gamslib/raw/launch.gms -o /tmp/launch_mcp.gms --skip-convexity-check
grep "^stat_iweight" /tmp/launch_mcp.gms | tr '+' '\n' | grep -E "sum\(ss.*nu_dweight"
```

Expected output (still shows Bug #2):
```
 sum(ss, ((-1) * 1$(ge(ss,s))) * nu_dweight(s))
```

The `sum(ss, ...)` iterates but the body doesn't depend on `ss`. This is
the Bug-#2 fingerprint.

---

## Root Cause

The Pattern C Bug #1 fix in Sprint 25 Day 6 (issue #1306) consolidated
the phantom ±N offset groups into a single zero-offset group, producing
one multiplier reference at the equation's domain index `s`. However,
the outer `sum(ss, ...)` wrapper — inherited from the way the Jacobian
transpose is assembled for alias-bound sums — is preserved verbatim,
condition and all.

Left over from the Bug #1 fix: the outer `sum(ss, ...)` is no longer
a useful structure once the offset consolidation kills the cross-element
variants. It should be removed OR its body should be re-indexed so the
multiplier depends on the summed variable.

The fix likely lives in the same call site in
`src/kkt/stationarity.py::_add_indexed_jacobian_terms` that builds the
Jacobian-transpose sum expression. Two candidate approaches:

1. **Drop the outer `sum(ss, ...)` when the consolidated zero-offset
   group has a body that doesn't depend on `ss`.** Emit a gated single
   term (with the condition rewritten to reference the equation domain
   directly): `nu_dweight(s) * (-1) * <count-or-existence-gate>`.
2. **Re-index the sum body.** Keep the `sum` over `ss` (or better, over
   the equation's domain `s`) but index the multiplier by the summed
   variable so the sum actually discriminates entries.

Approach 1 is closer to what a hand-derived KKT would produce.
Approach 2 is closer to the existing code shape and may reuse more of
the current infrastructure.

---

## Expected Impact

- Fixes launch's rel_diff (0.17 per Day 5 investigation) if the
  stationarity is numerically off because of the `card` factor.
- Should not affect other models unless they share the exact
  `sum(alias$cond(alias, eq_domain), ...)` shape — but in those cases,
  the same Bug #2 almost certainly applies and this fix would help
  them too.

---

## Files (likely touchpoints)

- `src/kkt/stationarity.py::_add_indexed_jacobian_terms` — call site
  that builds the Jacobian-transpose sum. The consolidation branch
  from the Bug #1 fix (which collapses `offset_groups` to a single
  zero-offset key) is the natural place to also drop/rewrite the
  outer `sum(ss, ...)` wrapper.
- `tests/unit/kkt/test_pattern_c_alias_offset_gate.py` — extend the
  existing regression test with a Bug-#2-specific assertion (currently
  intentionally lax per the Day 6 prompt so it doesn't over-specify
  the residual multiplier argument).

---

## Scheduling

Deliberately deferred from Sprint 25 Day 6 so that Bug #1 (#1306) could
land as a narrow, well-scoped fix (Tier 0/1 canary invariant). Target:
Sprint 25 Day 13 buffer if schedule allows, else Sprint 26 carryforward.

Per the Sprint 25 Day 6 prompt task 9:

> File a separate GH issue `pattern_c_mis_scoped_alias_condition` —
> title "Pattern C Bug #2: KKT stationarity mis-scopes `$(ge(ss, s))`
> condition inside `sum(ss, ...)` where the multiplier is not indexed
> by `ss`"; body references `DAY5_PATTERN_A_INVESTIGATION.md` §Bug #2
> and links to the Day 6 PR as the landing point for Bug #1. Target
> Sprint 25 Day 13 buffer or Sprint 26 carryforward depending on
> schedule.
