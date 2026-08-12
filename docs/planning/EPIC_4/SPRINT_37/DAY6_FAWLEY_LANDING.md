# Sprint 37 Day 6 — P4 fawley: Conjunct-2 Narrowing → **LANDED**

**Date:** 2026-08-12 · **Branch:** `planning/sprint37-day6-fawley-narrow` · **Scope:** emit-touching — `src/kkt/stationarity.py`, the two fawley goldens, and a new corpus-free fixture. **DB untouched.** Pulled forward from Days 7–8 using P2's freed budget (Day 5 disposition).

**Verdict: ✅ LANDED.** The conjunct-2 narrowing works on the first attempt after two failures, and **`make leak-check MODEL=fawley` returns the unqualified `LEAK GATE PASS`** — the gate that has blocked this fix since Sprint 35. `dinam`, `shale` and `prolog` are byte-identical. **0 bucket by construction**: Solve 108 / Match 93 / floor 76 unchanged, exactly as `ISSUE_1111` requires.

---

## 1. What the narrowing changed

Both previous predicates only ever **subtracted**:

| attempt | predicate | result |
|---|---|---|
| 1 (Task 6) | conjunct 1 alone — a mult-domain index is a declared subset of a var-domain index | `LEAK: dinam, prolog, shale` |
| 2 (Task 6) | + "the coefficient omits the summed index" (`_collect_free_indices` absence) | `LEAK: dinam, shale` |
| **3 (here)** | + **the coefficient must REFERENCE the subset's parent index**, compared **suffix-stripped**; skip when the term carries an offset | **`LEAK GATE PASS`** |

The decisive addition is a **positive** requirement rather than another negative one. "The coefficient omits the summed index" is satisfied by any term that simply doesn't mention it — including terms where the pair is genuinely disjoint. Requiring the coefficient to *reference the parent* asserts the thing the fix actually depends on: **the derivative really is diagonal in this pair**, because the collapsed per-cell derivative left the parent index behind.

Two smaller guards matter:

- **Suffix-stripped comparison.** The AD layer re-symbolises subset indices with a `__` suffix (`cfq` → `cfq__`). Attempt 2 compared raw names, so a reference through the re-symbolised form was invisible — the specific reason it under-fired on `dinam`/`shale`.
- **Offset skip.** The binding is meaningless when the term already carries a lead/lag offset, so the predicate declines there rather than stacking guards.

**Implementation reuses `_subset_alias_superset_index`** (Issue #1393, `:7708`) rather than adding a parallel walker — it already performs the subset-parent lookup *and* the `__`-stripping, and its own docstring names fawley's `pcr(cr)`. The emitted guard mirrors the `mbal` term that was already correct in the golden: a `sameas` condition on a retained `Sum`, not an index rewrite.

## 2. Phase-0 gate (`ISSUE_1111`) — all four criteria

| criterion | required | measured | status |
|---|---|---|---|
| Correctness | no `stat_bq` row in the residuals | **absent** (was rel 9.73e-01); max is the emit-correct `stat_trans(tr-2)` rel 1.00 | ✅ |
| | `sameas` count in `stat_bq` 1 → 3 | **3** | ✅ |
| **Leak-freedom** | unqualified `LEAK GATE PASS` | **PASS** — 163 goldens, 0 unverified, fawley only (+44 B each) | ✅ |
| Bucket / KPI | **unchanged** 108/93/76 | **unchanged**; fawley still `model_infeasible`; DB untouched | ✅ |
| Regression guard | fail-before/pass-after fixture | **3 tests**, corpus-free, fail-before verified against pre-landing `main` | ✅ |

The `CASE_B` verdict is retained and expected — the harness max remains `stat_trans(tr-2)`, the H-b divergence outside this issue's scope.

## 3. The fixture caught a real gap in its own synthetic

`tests/unit/kkt/test_shape_fawley_2d_second_index.py` — corpus-free, `pytest.mark.unit`, no skip guard, 0.8 s.

**The first synthetic did not reproduce the shape.** Its coefficient was `(-1) * char(c,m)`, which references `c` and `m` but never the parent `cf` — so conjunct 2 correctly declined to fire, and the test failed *against the landed fix*. Real fawley's constraint is

```gams
pbal(cfq,m)$cfm(cfq,m).. q(cfq,m) =e= sum(c$bposs(cfq,c), char(c,m)*bq(c,cfq));
```

and it is the **`$bposs(cfq,c)` guard** — re-symbolised to `1$(bposs(cf,c))` during differentiation — that supplies the parent reference. Adding that condition to the synthetic made all three tests pass.

Without writing the fixture, this landing would have shipped with a synthetic that silently exercised nothing. Same class of gap as the `Call` branch on Day 3 — caught this time **by construction rather than by review**.

**Three tests:**

| test | asserts |
|---|---|
| `test_subset_constraint_index_binds_to_its_parent` | the `sameas(cfq…, cf)` binding is emitted |
| `test_multiplier_is_still_summed_not_rewritten` | the multiplier keeps its subset index and the `Sum` survives — a guard, not an index rewrite |
| `test_binding_does_not_fire_without_the_subset_relation` | **negative control** — with `cfq` declared independent (not `cfq(cf)`), the binding does **not** fire |

The negative control is the discriminating half: conjunct 1 alone is exactly what leaked onto three models in Task 6, so a fixture that only proved the positive case would not distinguish this predicate from the one that failed.

**Fail-before verified against real code**, not asserted: against pre-landing `main`, `test_subset_constraint_index_binds_to_its_parent` fails while the other two pass — correct, since pre-landing the multiplier *is* still summed and unrewritten, and the negative control *should* stay silent.

## 4. Bucket — 0, by construction

fawley is **H-b**: with `stat_bq` fully corrected the harness max is still the emit-correct `stat_trans(tr-2)` rel 1.00, the MCP stays MS-5 (LP optimum 2899.25), and Sprint 36's `--force` survey was NEGATIVE. So:

- **Solve 108 · Match 93 (64 cold + 29 presolve) · genuine floor 76 — unchanged.**
- fawley remains `model_infeasible` / `not_tested`.
- **The DB is untouched.**

Claiming a bucket gain here would be wrong; the +Solve is a Sprint-38 PATH-consultation question.

## 5. Disposition

- **`ISSUE_1111` → ✅ LANDED**, with the historical leak status retained and marked as design-time rather than deleted.
- **P4 is closed for Sprint 37** — the correctness fix ships, the +Solve hands off to Sprint 38.
- **Two of the sprint's four deep tracks have now landed** (P1 markov, P4 fawley); P2 ganges is REPLAN'd with two Phase-0 gates banked.
- **Days 7–8 are now free**, having been spent here. The schedule's next unclaimed work is P5 sarf (Days 11–12, 20–28 h) — pulling it forward is the natural use, and it is the sprint's last remaining bucket lever (+1 Translate).

---

**Document Status:** ✅ Complete — Sprint 37 Day 6 (P4 fawley landed, 0 bucket, leak-free).
**Last Updated:** 2026-08-12 · **Owner:** Sprint 37 execution team
