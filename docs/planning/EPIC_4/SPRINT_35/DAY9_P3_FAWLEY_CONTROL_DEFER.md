# Sprint 35 — Day 9 (P3): fawley constraint-index-diagonal — control VERIFIED, src/ landing ATTEMPTED, LEAKS onto markov → DEFERRED

**Day:** 9 (Priority 3 — fawley constraint-index-diagonal correction, optional/correctness-only) · **Date:** 2026-08-03 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day9-p3-fawley` · **Scope:** docs-only (src/ attempt reverted). **0 in-sprint bucket, 0 floor (fawley H-b), no `src/` shipped.**
**Outcome: the `/tmp` control PROCEEDED and the `src/` landing was ATTEMPTED (per direction) — the fix is verified correct (max\|stat_bq\| 473.4 → 1.14e-13) but a general constraint-index-diagonal predicate in the shared `_add_indexed_jacobian_terms` LEAKS onto the `#1110` multi-pattern cohort (markov), which triggers the design's REPLAN exit → REVERTED + DEFERRED to a dedicated effort with a 2-D-cohort / multi-pattern harness.**

---

## 1. The `/tmp` control — PROCEEDS (verified live, GAMS 54.2.1)

Per `FAWLEY_DIAGONAL_DESIGN.md` §5, applied the constraint-index-diagonal `$(sameas(cfq__,cf))` guard to fawley's emitted `stat_bq` **by hand** (the two unguarded terms — `qsb` and `pbal` — in the committed `fawley_mcp_presolve.gms`), then measured the warm-start residual (`mcp_model.iterlim = 0`, `limrow` high; `modelstat` = the warm point):

| | `max\|stat_bq\|` (36 rows) |
|---|---|
| **baseline** (committed golden, unguarded qsb/pbal) | **473.4** (= the Day-0 / S34 figure exactly) |
| **fixed** (qsb + pbal + `$(sameas(cfq__,cf))`) | **1.137e-13** (machine zero) |

**PROCEED:** the `sameas` fix drives `max|stat_bq| → 0` — **scoped to `stat_bq`** (the harness's global max retains the emit-correct `stat_trans(tr-2)` non-emit residual, §Task-8 finding, which the fix correctly does not touch). This **confirms the design's post-P4 refinement**: on the current tree the fix reaches **0**, not the 18.468 partial — the S34 P4 sense-aware bound-transfer already handles the cc-dist cell (`FAWLEY_DIAGONAL_DESIGN.md` §1.3). The hypothesis (the qsb/pbal over-sum is the emit gap; the `mbal` term's diagonal guard is the template) is **verified**.

### The exact fix (for the dedicated effort / Sprint-36)

In the emitted `stat_bq(c,cf)`, the `mbal` term already carries `$(sameas(cfq__,cf))`; the `qsb` and `pbal` terms sum over `cfq__` without it. Add the guard to both:
- **qsb:** `sum((cfq__,l,s), (…$(cfq(cfq__)))$(specs(cfq__,l,s)))` → `sum((cfq__,l,s), ((…$(cfq(cfq__)))$(specs(cfq__,l,s)))$(sameas(cfq__,cf)))`
- **pbal:** `sum((cfq__,m), (…$(cfq(cfq__)))$(cfm(cfq__,m)))` → `sum((cfq__,m), ((…$(cfq(cfq__)))$(cfm(cfq__,m)))$(sameas(cfq__,cf)))`

## 2. The `src/` landing — ATTEMPTED (per direction) → LEAKS onto markov → REVERTED

The control verified the fix is **correct**, so the `src/` landing was attempted. Implementation:
- **`_constraint_index_diagonal_guards`** helper (added after `_dual_binding_map`): a general constraint-index-diagonal predicate — fire the `sameas` guard only when the *summed* multiplier index is a **constraint-domain** index occupying the *variable's* stat position (disjoint from the #1049 variable-heavier reduction and the #1110/#1111 *variable*-index diagonal). Bails (`return []`) on offset indices, inconsistent bindings, or when a summed index shares a canonical set with a bound one (the aliased-reduction gate).
- Guard application in **both** emit paths `stat_bq` traverses: the disjoint-else `Sum(mult_domain, term)` branch **and** the #1104 fresh-alias path (guard inserted *before* the `cfq→cfq__` rename so it propagates into the `sameas`).

**Result on fawley: exactly reproduces the control** — `stat_bq(c,cf)` emits all three `sameas` guards; `max|stat_bq| → 1.137e-13`. The predicate + placement are correct for fawley.

**Result on the cohort: LEAKS onto markov (#1110 multi-pattern).** The KKT integration suite flagged `test_markov_multi_pattern::test_markov_stationarity_has_correction_term`: my predicate **over-fired on markov**, adding a wrong `$(sameas(j,i))` diagonal guard to markov's `constr` term. markov shares the *surface* pattern (a constraint index sitting in the variable's stat position) but its derivative is **genuinely off-diagonal** (that is the whole point of the #1110 multi-pattern correction) — so the guard is semantically wrong there. A general surface-pattern predicate **cannot distinguish** fawley's true constraint-index-diagonal from markov's off-diagonal multi-pattern.

This is exactly the **high-blast-radius shared-function leak** the design predicted (`_add_indexed_jacobian_terms`, `src/kkt/stationarity.py:5861`, ~1430 lines, a dozen existing `sameas` paths; leak-freedom must be proven against the 2-D cohort **and** the #1110 diagonal). It trips the design's **REPLAN exit** verbatim: *"any mbal/cohort/1-D-core change → DEFER again (a dedicated effort + the 2-D-cohort harness)."* → **src/ reverted** (`git checkout src/kkt/stationarity.py`; helper count 0, `git diff main -- src/` empty).

## 3. Why DEFER is the right call (not merely the leak)

Even absent the leak, the deferral is proportionate:
- **0 bucket, 0 floor.** fawley is **H-b** (re-confirmed live Day 0: `CASE_B`, `stat_bq` 0.973, `stat_trans(tr-2)` rel 1.00 the *emit-correct* harness max — the divergence is non-emit). The MCP solves **MS-5 @ 4399.557** (LP opt 2899.25) even with `stat_bq` closed → fawley stays `model_infeasible`, does **not** cold-match, so the correctness fix yields **no Solve and no genuine-floor move**.
- **The leak makes it a dedicated effort, not a day-fix.** Distinguishing fawley's constraint-index-diagonal from the #1110 multi-pattern off-diagonal requires a **derivative-structure** discriminator (not a surface-pattern predicate) plus a 2-D-cohort + multi-pattern regression harness. That is the banked scope, not a bounded P3 day.
- **Flat sprint.** P3 is the explicitly optional/low-priority track; the design + prompt both sanction the docs-only DEFER.

## 4. Separate finding — markov `slow` test fails on clean main (pre-existing, NOT this work)

While running the KKT suite I confirmed `test_markov_multi_pattern::test_markov_stationarity_has_correction_term` **fails on clean main** (src/ reverted, helper absent): the assertion is `'1 -' not in <emitted stat>`, but the current markov emit contains `(1 - b * pi(s,i,s,i,s__kkt1)) * nu_constr(s,i)`. The test is marked `pytest.mark.slow` (module line 17), so `make test` (`-m "not slow"`) **excludes** it — which is why Day-6's full `make test` was green (5040/0) and this went unseen. It is **pre-existing and unrelated to the fawley work** (fails with the helper reverted; my fix separately *added* a `sameas(j,i)`, but the `'1 -'` the test checks is present either way). Flagged as a follow-up: either the markov emit regressed vs. this assertion at some earlier point, or the assertion is stale. → recorded in `FOLLOWUPS_GAMS54_TRANSITION.md` for Day-13 triage; **not a Day-9 deliverable.**

## 5. Hand-off

- **The +Solve** is already in the **Sprint-36 consultation bundle** (`SPRINT_36/CONSULTATION_BUNDLE.md`, Day 8) — the fawley H-b `--force` survey. It is *not* a P3 deliverable.
- **The correctness fix** hands to a **dedicated fawley effort** (Sprint-36 or later): the verified control (473 → 1.14e-13) + the exact guard spec (§1) + **the leak requirement made concrete (§2): the discriminator must be derivative-structure-based, not surface-pattern, to separate fawley's constraint-index-diagonal from the #1110 multi-pattern off-diagonal (markov)** + the fawley 2-D-second-index property fixture (`FAWLEY_DIAGONAL_DESIGN.md` §6, `shape_fawley_2d_second_index`, lands *with* the fix) + a #1110 multi-pattern guard test. The fix surface (`_add_indexed_jacobian_terms:5861`) is re-confirmed as the correct layer; the general *predicate* is what needs the redesign.

## Outcome

**0 in-sprint bucket / 0 floor, as expected** (P3 optional, fawley H-b). The `src/` attempt was made per direction and **reverted** (leaks onto markov #1110); no `src/` shipped, no `--resolve-changed` impact. The firm product is the **verified control** (the qsb/pbal `sameas` fix reaches machine zero on the post-P4 tree, refining the S34 18.468→0) + the exact guard spec + **the now-concrete leak boundary** (surface-pattern predicate over-fires on the #1110 cohort — the dedicated effort needs a derivative-structure discriminator), de-risking the dedicated fawley correctness effort and the Sprint-36 forcing survey. Plus a **separate pre-existing flag** (§4: markov `slow` test failing on main, excluded from `make test`).

**Next (Day 10):** P7 infrastructure (fixtures for landed tracks — only the turkey-recovery raw-emit fixture applies, P4/P3 not landed; PR25 floor tracking; SUMMARY row 35) + Checkpoint 2.

---

**Document Status:** ✅ Complete — Sprint 35 Day 9 (P3 control VERIFIED; src/ ATTEMPTED per direction, leaks onto markov #1110 → REVERTED + DEFERRED)
**Last Updated:** 2026-08-03
**Owner:** Sprint 35 Execution Team
