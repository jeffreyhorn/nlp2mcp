# AD: scalar-constraint stationarity Sum body doesn't fully collapse when wrt-index is symbolic eq-domain superset of inner Sum's iteration subset

**GitHub Issue:** [#1393](https://github.com/jeffreyhorn/nlp2mcp/issues/1393)
**Status:** OPEN (filed Sprint 26 Day 9, 2026-05-12)
**Severity:** Medium — produces an over-counted KKT Jacobian cross-term (off by factor |subset| = 17× for otpop). Differs from the NLP optimum.
**Date:** 2026-05-12
**Last Updated:** 2026-05-12
**Affected Models:** otpop (confirmed; the `kdef` scalar equation with `sum(t, del(t)*p(t)*x(t))`). Likely affects other models with scalar-aggregation constraints over subset domains referenced by indexed stationarity equations.
**Target Sprint:** Sprint 27 (10–16h across architectural change + integration tests + Tier 0/1 byte-stable regression).
**Cross-references:**
- Predecessor: #1334. Closure history: originally CLOSED on GitHub 2026-05-05 (unintentional auto-closure via PR #1359 — a docs-only PR whose body explicitly listed #1334 as supposed-to-stay-OPEN); REOPENED Sprint 26 Day 4 (PR #1384) during Priority 5 #1334 investigation; close-and-refiled to this Sprint 27 #1393 on Sprint 26 Day 9 (the Day 9 GitHub closure + ISSUE_1334 doc move to `docs/issues/completed/` reflects the carryforward, not a new fix landing). See [docs/issues/completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md](completed/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md) for the original 2026-05-02 framing.
- Companion: #1335 — Day 9 fix attempt rolled back per PR #1394 review (math-correctness regression in the resulting cross-term shape); reopened in-place as a Sprint 27 carryforward (6–10h estimate, narrower scope than this issue's 10–16h architectural redesign). Same target model otpop; see `[docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md](ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md)` for the corrected fix-surface diagnosis with three competing Sprint 27 approaches.
- Sister Sprint 27 carryforwards (AD-architecture-level reclassifications):
  - #1381 (Pattern C Phase B redesign — Sprint 26 Day 3).
  - #1385 (Option 1 short-circuit redesign — Sprint 26 Day 4).
  - #1390 (kand tree-predicate-aliased Sum redesign — Sprint 26 Day 7).

## Problem Summary

otpop's `kdef.. k =e= sum(t, del(t) * (0.365 * (1 - c) * p(t) * x(t) - rd(t)))` (where `t ⊂ tt`) produces an over-counted Jacobian cross-term in `stat_x(tt)` and `stat_p(tt)`:

- **Expected `stat_x(tt)` cross-term** (hand-derived from KKT, see `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 4 §"Approach 1 sketch"):
  ```
  (del(tt) * 0.365 * (1 - c) * p(tt))$(t(tt)) * nu_kdef
  ```
  — single guarded term (`x(t)` matches `x(tt)` only when `t(tt)` holds).

- **Observed `stat_x(tt)` cross-term** (current main; Day 9 #1335 fix attempt rolled back so this is the pre-Day-9 baseline shape — see `[docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md](ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md)` §"Sprint 26 Day 9 Update — Fix Attempt Rolled Back" for the narrative):
  ```
  sum(t__, ((-1) * (del(t__) * 0.365 * (1 - c) * p(tt))) * nu_kdef)$(t(tt))
  ```
  — Sum over all `t__` elements of subset `t`, over-counting `del` by `|t|` = 17×.

Same shape in `stat_p(tt)` (the `p(t)` cross-term).

Sprint 26 Day 9 attempted the ISSUE_1334.md §Approach 1 fix (`_replace_indices_in_expr` ParamRef branch in `src/kkt/stationarity.py:2534+`) and discovered the framing was insufficient — closing #1334 + filing this Sprint 27 successor with the corrected diagnosis (mirroring the Day 4 #1385 + Day 7 #1390 reclassification methodology).

## Reproduction

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
  -o /tmp/otpop_mcp.gms --skip-convexity-check --quiet

grep -cE "sum\(t__, .* \* nu_kdef" /tmp/otpop_mcp.gms
# Returns: 2 (one in stat_p, one in stat_x). Must be 0 post-fix.
```

## Root cause (from Sprint 26 Day 9 trace analysis)

When `_diff_sum(Sum(('t',), del(t)*p(t)*x(t)), wrt_var='x', wrt_indices=('tt',), ...)` is called (`src/ad/derivative_rules.py:1847`):

1. `_sum_should_collapse(('t',), ('tt',), config)` is invoked at line 1909.
2. It checks `_is_concrete_instance_of('tt', 't', config)` at line 2601 — is `'tt'` a concrete element of set `t`?
3. `'tt'` is **not** a concrete element — it's the SYMBOLIC eq-domain index of the indexed stationarity equation `stat_x(tt)`.
4. `_sum_should_collapse` returns False → no collapse.
5. AD falls through to the symbolic-Sum-preservation path at line 2086, returning `Sum(('t',), body_derivative, condition)`.
6. The `body_derivative` inside has `x(t) → x(tt)` substituted (via the indexed-stationarity rewrite at `_replace_indices_in_expr`), but the Sum-over-`t` wrapper remains. `del(t)` and `p(t)` keep symbolic `t` (rewriting them would be wrong — they ARE iterated over the Sum).
7. Downstream cross-term assembly in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:4432+`) renames `t → t__` (alias-renamed dummy) for the emit and adds the `$(t(tt))` guard — producing the over-counted `sum(t__, del(t__)*p(tt))$(t(tt))` shape.

## The correct architecture

When differentiating `sum(<subset_iter>, body)` w.r.t. `<some_var>(<symbolic_superset>)` where `<subset_iter> ⊂ <symbolic_superset>`, the sum should collapse to a single guarded term:

```
body[<subset_iter> → <symbolic_superset>] $ (<subset_iter>(<symbolic_superset>))
```

For otpop's `(stat_x(tt), kdef)`:

```
(del(tt) * 0.365 * (1 - c) * p(tt)) $ (t(tt)) * nu_kdef
```

This requires `_is_concrete_instance_of` (or a new sibling check) to recognize SYMBOLIC superset names as "concrete" w.r.t. subset iteration variables — a substantial AD-architecture-level change.

## Original #1334 Approach 1 framing — insufficient

The original ISSUE_1334.md §Approach 1 framing (Sprint 26 Days 0–8) proposed a fix in `_replace_indices_in_expr` ParamRef branch (`src/kkt/stationarity.py:2534+` def / `:2652+` `case ParamRef`). That framing is too narrow:

- The bug isn't in stationarity-time index substitution; it's in AD-time Sum-collapse logic.
- `_replace_indices_in_expr` runs AFTER `_diff_sum`. By then, the `Sum(('t',), body_with_t__)` is already in the AST. No amount of post-AD index substitution can collapse a structurally-preserved Sum.

## Proposed Fix Approach — Three Sub-Phases

(Phase decomposition added Sprint 26 Day 9 per established Sprint 27 carryforward methodology; mirrors the Phase 1/2/3 structure used in #1381 / #1385 / #1390.)

### Phase 1 (~3–4h): Inventory + design choice

**Deliverable:** decision between three competing architecture options.

- **Option A — Extend `_is_concrete_instance_of`:** treat symbolic superset names as "concrete instances" of their subsets when a `model_ir` subset relationship is established. Pros: smallest change. Cons: changes semantics of a fundamental check; may regress other AD paths that relied on the strict concrete-only check.
- **Option B — New `_sum_should_collapse_with_subset_guard`:** parallel check that fires for `(subset_iter ⊂ symbolic_superset)` cases and returns a guard expression alongside the collapse decision. The `_diff_sum` code path uses the guard to wrap the collapsed body in `body$(<subset_iter>(<symbolic_superset>))`.
- **Option C — Defer to emit-time guard reconstruction:** let `_diff_sum` produce the over-counted Sum-wrap, then post-process in `_add_indexed_jacobian_terms` to detect the pattern and collapse. Most conservative (doesn't touch AD core) but adds emit-time complexity.

Phase 1 must include the **Phase 0 acceptance gate** (per Sprint 26 Days 3 + 4 + 7 reclassification methodology): translate otpop with a Phase-1 prototype + verify GAMS compile-clean + hand-derive `stat_x('1990')` KKT instance against the emit BEFORE committing the Phase 2 implementation budget.

### Phase 2 (~4–6h): Implementation

Implement the chosen option from Phase 1. Reuse existing infrastructure:

- `_diff_sum` (`src/ad/derivative_rules.py:1847`) — entry point for Sum differentiation.
- `_sum_should_collapse` (`:2556`) — current collapse-decision logic.
- `_is_concrete_instance_of` (`:2607`) — current concrete-check logic.
- `_substitute_sum_indices` (sibling of `_substitute_single_index`) — used for index substitution in the collapsed result.
- `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:4432+`) — cross-term assembly site; may need awareness of the new subset-guard wrapper.

### Phase 3 (~3–6h): Integration test coverage + Tier 0/1/2 byte-stable regression

Integration tests verifying EMIT CORRECTNESS (hand-derived KKT shape + GAMS compile-clean), not just "Sum collapsed":

- 1 unit test in `tests/unit/ad/`: synthetic 3-element subset `t ⊂ tt`, scalar equation `eq.. y = sum(t, p(t)*x(t))`, stationarity domain `tt`. Assert `(stat_x(tt), nu_eq)` cross-term has no Sum wrapper and uses the `$(t(tt))` guard.
- 1 integration test in `tests/integration/ad/test_otpop_kdef_collapse.py`:
  - Translate otpop from `data/gamslib/raw/otpop.gms`.
  - Assert `grep -cE "sum\(t__, .* \* nu_kdef" data/gamslib/mcp/otpop_mcp.gms` returns 0.
  - Assert `(del(tt) * ... * p(tt))$(t(tt)) * nu_kdef` shape appears in `stat_x(tt)` body.
  - Run `gams data/gamslib/mcp/otpop_mcp.gms lo=2` and assert `nu_kdef` appears in the listing.
- Tier 0/1 byte-stable canary check (11 models, mirror Sprint 26 Day 5 retest list).

## Tests to Add (Sprint 27)

### Phase 1 deliverable

- 1 hand-derived KKT shape verification document — pins the expected `stat_x('1990')` and `stat_p('1990')` cross-term shapes for otpop. Stored at `docs/issues/ISSUE_1393_otpop_phase_0_handderived_kkt.md` or inline in the Phase 1 PR description.

### Phase 2 (unit tests)

- `tests/unit/ad/test_diff_sum_subset_iter_collapse.py`:
  - Synthetic Sum collapse w/ subset iter + symbolic superset wrt — assert collapsed body has subset-guard wrapper.
  - Negative case: Sum collapse w/ concrete wrt (existing behavior preserved).

### Phase 3 (integration)

- `tests/integration/ad/test_otpop_kdef_collapse.py` — full end-to-end otpop translate + grep assertions per the Phase 3 plan above.

## Files Involved

- `src/ad/derivative_rules.py` (`_diff_sum:1847`, `_sum_should_collapse:2556`, `_is_concrete_instance_of:2607`).
- `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms:4432+` — observes the bug downstream; Option C lands here).
- `data/gamslib/raw/otpop.gms` (source — kept as the target reproducer; do NOT use any other model for Phase 0 acceptance gate).
- `data/gamslib/mcp/otpop_mcp.gms` (current emit with 2× `sum(t__, ...)` wraps; will regenerate post-fix).

## Effort estimate

10–16h across three sub-phases (Phase 1: 3–4h design + Phase 0 acceptance gate; Phase 2: 4–6h implementation; Phase 3: 3–6h integration tests + Tier 0/1 byte-stable regression). Mirrors the Sprint 27 #1381 / #1385 / #1390 effort profiles.

## Related

- **#1334** — superseded by this Sprint 27 #1393 via Sprint 26 Day 9 close-and-refile (see the Predecessor cross-reference above for the full closure history: originally closed on GitHub 2026-05-05 via PR #1359 unintentional auto-closure; reopened Day 4 via PR #1384; re-closed Day 9 with carryforward comment to #1393, ISSUE_1334 doc moved to `docs/issues/completed/`). Original Approach 1 framing in stationarity.py was insufficient; corrected diagnosis localizes fix to AD `_diff_sum` / `_sum_should_collapse`.
- **#1335** — narrow AD scalar-equation gate relaxation; Day 9 fix attempt rolled back per PR #1394 review (math-correctness regression in the resulting cross-term shape); reopened in-place as a Sprint 27 carryforward (6–10h estimate). Independent of #1334's wider architectural scope.
- **#1381** (Sprint 27): Pattern C Phase B redesign — similar AD-architecture-level reclassification (Day 3).
- **#1385** (Sprint 27): Option 1 short-circuit redesign — closest sibling pattern, AD-vs-emit symbolic/concrete handling (Day 4).
- **#1390** (Sprint 27): kand tree-predicate Sum redesign — AD-Sum-architecture-level (Day 7).
- **Sprint 26 has produced 4 architectural reclassifications** in this same root-cause class (prep-task design validation at patch-site level + downstream-handling assumption that doesn't hold empirically). Sprint 27 prep should add a Phase 0 sub-task to each for empirical end-to-end correctness verification.
