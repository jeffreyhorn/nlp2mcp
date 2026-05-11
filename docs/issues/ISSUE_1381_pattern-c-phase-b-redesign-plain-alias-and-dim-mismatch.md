# Pattern C Phase B Redesign — Plain-Alias + Dim-Mismatch Consolidation (camcge #1354 + cesam2 #1355)

**GitHub Issue:** [#1381](https://github.com/jeffreyhorn/nlp2mcp/issues/1381)
**Status:** OPEN (filed Sprint 26 Day 3, 2026-05-11)
**Severity:** Medium — affects ≥ 11 GAMSlib models in `path_syntax_error` bucket (camcge, cesam2, quocge, prolog, paklive, blend, chem, demo1, fdesign, ibm1, pollut, prodmix, trussm — full corpus impact larger pending Phase B-1 / B-2 / B-3 implementation).
**Date:** 2026-05-11
**Last Updated:** 2026-05-11
**Affected Models:** camcge (#1354), cesam2 (#1355), plus byte-shifted plain-alias canaries observed Day 3
**Target Sprint:** Sprint 27 (10–16h across three sub-phases)
**Cross-references:**
- Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" — original Phase A specification (launch-only)
- Sprint 26 Task 3 [PATTERN_C_HYPOTHESIS_VALIDATION.md](../planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md) §3 — REPLAN to 2 targets
- Sprint 26 Day 1 PR #1379 — Phase A launch fix landed
- Sprint 26 Day 2 PR #1380 — Phase A validation + (incomplete) Phase B scoping
- Sprint 26 Day 3 PR #1382 — this issue filed; Phase B reclassified
- Sprint 27 #1378 — separate carryforward for launch PATH-numerics on Phase A's correct KKT

---

## Problem Summary

Sprint 26 Day 1 Phase A landed the consolidated zero-offset Pattern C builder for launch (per Sprint 25 SPRINT_LOG.md Day 11 follow-up). The fix uses a **post-hoc alias↔eq-domain swap** on the auto Sum-wrapped term — works correctly for launch because the source body `sum(ss$ge(ss,s), iweight(ss) + ...)` has the alias `ss` and eq-domain `s` as **textually distinct** symbols.

Sprint 26 Task 3 REPLAN extended scope to camcge + cesam2 (plain-alias / `sameas`-decomposed Pattern C variants). Day 2 scoping concluded the Phase B fix was a simple gate-predicate relaxation (drop `expr.condition is not None`). Day 3 implemented this (~15 LOC) and verified empirically that **the swap-based approach doesn't generalize.**

---

## Symptom — Wrong consolidated emit on plain-alias bodies

Day 3 ran the gate-predicate relaxation across the 54-model golden corpus. 11 canaries byte-shifted, all producing mathematically wrong consolidated emits:

| Model | Equation | Correct consolidated form (hand-derived) | Day 3 produced |
|---|---|---|---|
| camcge | `stat_dk` | `sum(j, (-imat(j,i)) * nu_ieq(j))` | `((-1) * imat(j,j)) * nu_ieq(j)` — `j` free unbound; coords wrong |
| camcge | `stat_xd` | `sum(j, (-io(j,i)) * nu_inteq(j))` | `((-1) * io(j,j)) * nu_inteq(j)` — same shape failure |
| camcge | `stat_p` | mix of `nu_actp`, `nu_pkdef`, `nu_prodinv` consolidations | partial (4/5 multipliers consolidated wrong; `nu_prodinv` not consolidated at all) |
| quocge | `stat_pq` | `sum(j, (-ax(j,i)) * nu_eqpzs(j))` | `((-1) * ax(j,j)) * nu_eqpzs(j)` |
| prolog | `stat_q` | `sum(j, (-a(j,i)) * lam_cb(j))` (with `t` guard) | `a(i+1,i) * lam_cb(i) - lam_cb(i) + sum(k, d(i,k,t) * lam_rc(k))` — mangled, retains an IndexOffset, missing terms |

camcge and quocge fail with identical shape errors. prolog fails differently (more aggressive corruption — the auto Sum-wrap appears to have collapsed entirely with element substitution).

---

## Root Cause

The Phase A swap-based approach fails on plain-alias for two compounding reasons:

### 1. Element-to-set substitution collapses alias and eq-domain names

For camcge's `ieq(i)..  id(i) =e= sum(j, imat(i,j)*dk(j));`:

- `j` is an alias of canonical set `i` (declared `Alias (i,j);`).
- Variable `dk` has domain `(i,)`; equation `ieq` has domain `(i,)`.
- The body's coefficient `imat(i,j)` has `i` (eq-domain index) and `j` (alias) as **distinct symbols** in the source AST.

The `_add_indexed_jacobian_terms` builder runs `_replace_indices_in_expr` (element-to-set substitution) BEFORE the auto Sum-wrap. Element-to-set maps `j` to canonical `i` (since `j` aliases `i`), so `imat(i,j)` becomes `imat(i,i)` in the indexed derivative. The position information distinguishing the eq-domain coordinate from the alias coordinate is **erased**.

The Day 3 swap `i ↔ j` then transforms `imat(i,i)` to `imat(j,j)` — both coordinates wrong (correct form would have one coordinate as `j` and the other as `i`).

For launch, the same logic ran but the symbols `ss` and `s` weren't aliases of the same canonical set — they were textually distinct strings in the body, so element-to-set didn't merge them, and the swap worked.

### 2. Auto Sum-wrap doesn't fire on plain-alias post-collapse

Phase A's transform relies on the auto Sum-wrap (in `_add_indexed_jacobian_terms` around line 5269) wrapping the term in `Sum((alias,), term)` when the indexed derivative has uncontrolled free indices. The wrap binds the alias `ss` for launch because `ss` was free in the post-element-to-set body (`ge(ss,s)` still has free `ss`).

For plain-alias bodies, post-element-to-set there is **no free index** — the alias `j` has been mapped to canonical `i`, and `i` is the controlled eq/var index. So no auto Sum-wrap fires. The Day 3 swap then introduces `j` into the body (via the rename), but no Sum binds it — `j` becomes a dangling unbound reference.

---

## Why Phase A's swap works only on launch

Phase A's swap-based approach implicitly assumes:

1. The source body has the alias and eq-domain indices as textually distinct symbols (`ss` vs `s`, not `j` vs `i` where `j` aliases `i`).
2. After element-to-set substitution, the alias remains free in the indexed derivative — auto Sum-wrap fires.
3. The swap can rewrite both names independently in the post-element-to-set AST.

These hold for launch's `ge(ss,s)` condition but not for plain-alias bodies where the alias's canonical resolution is the same as the eq-domain's canonical.

---

## Proposed Fix Approach — Phase B Builder Redesign

Phase B requires intercepting BEFORE element-to-set substitution and building the consolidated term explicitly from the source Sum's body structure. Three sub-phases:

### Phase B-1 (~3–5h): Source-body-driven builder for simple plain-alias

Target: camcge's 4-of-5 simple variants (`actp`, `pkdef`, `inteq`, `ieq`). All share the shape `sum(<alias>, <coeff>(<eq_idx>, <alias>) * <var>(<alias>))`.

When the Pattern C gate fires (after the predicate relaxation that Day 3 already implemented), instead of running through the standard derivative-and-swap path:

1. Read the source `Sum` node from `pattern_c_info` (already captured by `_find_pattern_c_alias_sum`).
2. Identify the alias name (e.g. `j`) and eq-domain index (e.g. `i`) from the source body's structure, with positions preserved (NOT through element-to-set).
3. Extract the coefficient AST from the Sum's body, swapping `i ↔ j` positions while preserving the SYMBOL distinction (the coefficient was `imat(i,j)` in source — after swap it's `imat(j,i)`, with `j` as the alias-bound iteration var and `i` as the free var-domain index).
4. Build `MultiplierRef(mult_base_name, (<alias>,) * len(mult_domain))` — multiplier indexed by alias.
5. Build the gated body: `Binary("*", coeff_swapped, mult_reindexed)` (no `DollarConditional` needed since there's no source `$cond`).
6. Wrap in `Sum((alias,), gated_body)` — alias-bound.
7. Replace the standard term-building path's output with this constructed term.

This skips the standard offset-groups loop entirely for this (eq, var) pair, since the consolidation is built directly.

### Phase B-2 (~3–5h): Eq-domain factor OUTSIDE the inner Sum (camcge prodinv)

Target: camcge's 5th variant. Source: `prodinv(i)..  pk(i)*dk(i) =e= kio(i)*savings - kio(i)*sum(j, dst(j)*p(j));`

The eq-domain index `i` appears in `kio(i)` OUTSIDE the inner Sum. The correct consolidated form is:

```gams
stat_p(i)..  ... + dst(i) * sum(j, kio(j) * nu_prodinv(j)) + ... =e= 0
```

- `dst(i)` (var-side factor) stays outside the new Sum.
- `kio(i)` (eq-side factor) moves INSIDE the new Sum, reindexed to `kio(j)`.
- The multiplier reindex `nu_prodinv(i) → nu_prodinv(j)` is the same as Phase B-1.

This requires the Phase B-1 builder to ALSO inspect the source equation body OUTSIDE the alias Sum, identifying:

- Factors that reference the eq-domain index → eq-side factors (move inside new Sum, reindex to alias)
- Factors that reference only the var-domain index → var-side factors (leave outside)
- Factors that reference NEITHER eq-domain nor var-domain → constants (treat as eq-side or var-side based on multiplication position; default to var-side)

Conceptually: separate the equation body's algebraic structure into `<var-side-factors> * <eq-side-factors> * sum(alias, ...)` (or equivalent algebraic factoring) BEFORE applying the consolidation.

### Phase B-3 (~4–6h): Dim-mismatch + sameas-block element-to-set (cesam2)

Target: cesam2 (#1355). Source: `COLSUM(jj)..   sum(ii, TSAM(ii,jj)) =e= Y(jj);`

- Equation domain: `(jj,)` (1D, canonical `(i,)`)
- Variable domain (TSAM): `(i, j)` (2D, canonical `(i, i)`)
- The alias-Sum's iter `ii` binds to the variable's FIRST index position
- The equation's domain `jj` binds to the variable's SECOND index position

Correct consolidated form: `stat_tsam(i,j)..  ... + nu_COLSUM(j)$(jj(j)) + ... =e= 0` (single zero-offset term, NO outer Sum — the alias is already bound by the stat-eq's variable-domain index).

The Phase B-3 builder must:

1. Detect dim-mismatch: `len(var_domain) != len(eq_domain)`.
2. Determine which var-domain position the eq-domain index binds to (positional inference from the source body's variable reference, e.g. in `TSAM(ii,jj)`: `ii` is position 0, `jj` is position 1; the eq-domain index `jj` is the BINDING for var position 1).
3. Build `MultiplierRef(mult_base_name, (var_dom[binding_position],))` — multiplier indexed by the var-domain index at the binding position (cesam2: `nu_COLSUM(j)` with `j = var_dom[1]`).
4. Apply subset-membership guard if needed (cesam2: `$(jj(j))` since `jj ⊆ i`).
5. NO outer Sum wrap (the alias is already controlled by the stat-eq's domain).

This sub-phase also needs to suppress the spurious `sameas`-block guards (`sameas(i, 'ACT') and sameas(j, 'COM') or ...`) that the current element-to-set machinery produces under dim-mismatch — those are emit-formatting artifacts that disappear once the consolidation is structurally correct.

---

## Tests to Add

### Phase B-1

`tests/unit/kkt/test_pattern_c_alias_offset_gate.py`:

- New test mirroring camcge's `ieq(i)..  id(i) =e= sum(j, imat(i,j)*dk(j));` synthetic shape. Assert:
  - No phantom-offset `nu_ieq(i±N)` terms.
  - Consolidated form `sum(j, (-imat(j,i)) * nu_ieq(j))` present (verify `imat(j,i)` substring — coefficient swap correct).
  - Multiplier `nu_ieq(j)` present (alias-indexed).
  - No `nu_ieq(i)` standalone (would mean swap didn't fire).

### Phase B-2

`tests/unit/kkt/test_pattern_c_alias_offset_gate.py`:

- New test mirroring camcge's prodinv shape: `prodinv(i).. ... = ... - kio(i)*sum(j, dst(j)*p(j));`. Assert:
  - Consolidated form `dst(i) * sum(j, kio(j) * nu_prodinv(j))` present.
  - `kio(j)` (eq-side reindexed) inside the Sum.
  - `dst(i)` (var-side) outside the Sum.

### Phase B-3

`tests/unit/kkt/test_pattern_c_alias_offset_gate.py`:

- New test mirroring cesam2's `COLSUM(jj)..  sum(ii, TSAM(ii,jj))` shape. Assert:
  - Consolidated form `nu_COLSUM(j)$(jj(j))` present (NO outer Sum).
  - No phantom-offset `nu_COLSUM(i±N)` terms.
  - No spurious `sameas` blocks.

### Integration tests

`tests/integration/emit/test_camcge_consolidation.py` (new file):

- Translate camcge fresh; assert 0 phantom-offset terms; GAMS `action=c` compile-clean.

`tests/integration/emit/test_cesam2_consolidation.py` (new file):

- Translate cesam2 fresh; assert 0 phantom-offset `nu_COLSUM(i±N)` terms; GAMS `action=c` compile-clean.

Pipeline regression: 54-model Tier 0/1/2 golden-file check; expect byte-shifts on plain-alias canaries (quocge, prolog, paklive, blend, chem, demo1, fdesign, ibm1, pollut, prodmix, trussm) plus camcge + cesam2 (formerly path_syntax_error → now should solve). Golden files for byte-shifted canaries regenerate as part of Phase B-1 / B-3 PRs per PR14 obligation; each regeneration verified mathematically correct against the hand-derived Lagrangian gradient.

---

## Files Involved

- `src/kkt/stationarity.py`:
  - `_find_pattern_c_alias_sum` (Day 3 left predicate launch-shape-only; relaxation will be re-applied as part of Phase B-1)
  - `_apply_pattern_c_swap_to_term` (Phase A logic; keep for launch case)
  - `_add_indexed_jacobian_terms` (gate site at line 4476+; standard term-building loop at line 5269+; auto Sum-wrap; element-to-set call ordering)
  - NEW: `_build_pattern_c_consolidated_term` (Phase B-1 builder driven from source body)
  - NEW: `_classify_eq_body_factors` (Phase B-2 helper for separating eq-side / var-side / inner-Sum factors)
  - NEW: `_build_pattern_c_dim_mismatch_term` (Phase B-3 builder for dim-mismatch case)

- `tests/unit/kkt/test_pattern_c_alias_offset_gate.py` (per-phase tests)
- `tests/integration/emit/test_camcge_consolidation.py` (NEW)
- `tests/integration/emit/test_cesam2_consolidation.py` (NEW)

- `data/gamslib/mcp/*_mcp.gms` (regenerate golden files for byte-shifted canaries per PR14; verify each new emit mathematically correct):
  - camcge_mcp.gms (new — formerly path_syntax_error)
  - cesam2_mcp.gms (new — formerly path_syntax_error)
  - quocge_mcp.gms (regenerate — phantom-offset enumeration consolidates)
  - prolog_mcp.gms (regenerate — phantom-offset enumeration consolidates)
  - paklive_mcp.gms (regenerate — verify Pattern C scope doesn't accidentally hit lead/lag `xtransf(n,t--1)` body)
  - plus 7 others observed Day 3

---

## Estimated Effort

| Sub-phase | Scope | Effort |
|---|---|---|
| Phase B-1 | Source-body-driven builder for simple plain-alias (4 camcge variants + quocge / prolog / etc.) | 3–5h |
| Phase B-2 | Eq-domain factor outside the inner Sum (camcge prodinv) | 3–5h |
| Phase B-3 | Dim-mismatch + sameas-block element-to-set artifacts (cesam2) | 4–6h |
| **Total** | | **10–16h** |

Plus per-phase test coverage (unit + integration) and 54-model golden-file regression with reviewer verification of each regenerated emit's mathematical correctness.

---

## Scope and Sprint Routing

**Target: Sprint 27.** Day 3 reclassification (Sprint 26 Day 3 PR #1382) documents this deferral and adjusts Sprint 26 Targets accordingly:

- Sprint 26 Solve target relaxed: ≥ 108 → maintain ≥ 104 (no Phase A/B Solve gain this sprint)
- Sprint 26 Match target relaxed: ≥ 64 → maintain ≥ 60
- Sprint 26 path_syntax_error target relaxed: ≤ 6 → maintain ≤ 9 (camcge + cesam2 stay in path_syntax_error)
- Sprint 26 Translate target slightly relaxed: ≥ 135 → ≥ 132 (Priority 4 short-circuit still in scope for +2)

Day 5 Checkpoint 1 criteria updated to reflect Phase B reclassification — only Phase A landing + Tier 0/1/2 canary rows count toward GO routing.

---

## Related

- **Sprint 25 #1351** — original launch rollback that created the need for Phase A
- **Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)"** — Phase A specification (launch-only)
- **Sprint 26 Task 3 PATTERN_C_HYPOTHESIS_VALIDATION.md** — REPLAN to 2 targets (camcge + cesam2) hypothesis
- **Sprint 26 Day 1 PR #1379** — Phase A landed
- **Sprint 26 Day 2 PR #1380** — Phase A validation + Phase B scoping (the scoping that turned out to be incomplete)
- **Sprint 26 Day 3 PR #1382** — Phase B reclassified to Sprint 27 #1381 (this issue)
- **Sprint 27 #1378** — launch PATH-numerics on Phase A's correct KKT (separate carryforward)
- **#1354 (camcge)** — will be closed when Phase B-1 + B-2 land
- **#1355 (cesam2)** — will be closed when Phase B-3 lands
