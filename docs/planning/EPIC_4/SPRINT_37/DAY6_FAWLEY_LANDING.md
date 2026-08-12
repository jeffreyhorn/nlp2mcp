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

---

# Sprint 37 Day 7 (same branch) — P5 sarf: Profile → **DEFER, on measured grounds**

**Date:** 2026-08-12 · **Scope:** analysis-only — a scratch memoization was applied for measurement and **REVERTED**; `src/` carries only the Day-6 fawley landing.

**Verdict: 🔶 DEFER (sixth consecutive) — but for the first time on a *measured* basis rather than a budget one.** The profile locates the blow-up precisely, and a cheap constant-factor fix was tried and **measured insufficient**, which converts the design's central premise from an assumption into a result.

## 1. Where the time actually goes (new — the design did not have this)

Capped at 180 s on current `main`; `compute_constraint_jacobian` accounts for **137 s**:

| function | calls | cum |
|---|---|---|
| `differentiate_expr` | 6,189,439 (761,897 primitive) | 121.6 s |
| `_diff_sum` | 1,154,628 | 104.5 s |
| `_is_concrete_instance_of` | 5,796,109 | 59.0 s |
| `simplify` | 10,486,266 | 49.7 s |
| `resolve_set_members` | 4,618,097 | 29.0 s |
| `CaseInsensitiveDict.__contains__` | 16,210,454 | 26.8 s |

**The blow-up is per-column differentiation, not the column enumeration itself.** ~762 K top-level differentiations in 180 s, against **398** columns that matter. The banked design said "369K columns"; the profile says the columns are cheap and *differentiating each one* is not.

## 2. The cheap fix was tried and does not work — measured, then reverted

`_is_concrete_instance_of` calls `resolve_set_members` on **every** one of its 5.8 M invocations, rebuilding the member list and linearly scanning it. That is textbook-memoizable, and it looked like it might make the re-architecture unnecessary.

| | baseline | memoized |
|---|---|---|
| `resolve_set_members` | 4.6 M calls, 29.0 s | **out of the top-14** |
| `_is_concrete_instance_of` | 59.0 s | 39.7 s |
| `CaseInsensitiveDict.__contains__` | 16.2 M, 26.8 s | 7.5 M, 14.8 s |
| **top-level differentiations in 180 s** | **761,897** | **802,108** |

**~5 % more throughput.** The memoization worked exactly as intended locally and the bottleneck simply moved to `simplify` and `_diff_sum`.

sarf needs `>330 s → single-digit seconds` ≈ **66×**. A 5 % win cannot close that. The **927×** ratio between declared columns (369,024) and active ones (398) is where the headroom is.

**⇒ The design's premise is now empirical: only the O(active) re-architecture can work.** Recorded in `ISSUE_1385` so the cheap optimization is not re-attempted as a shortcut by a future effort.

## 3. Phase-0 authored — the track never had one

`docs/issues/ISSUE_1385_sarf-symbolic-emit-o-active.md`, four canonical subsections + traced surfaces. P5 had **no** Phase-0 gate, so it was not implementable under CONTRIBUTING §392–447 regardless of budget — the same gap Day 5 found on `$66`/#1289.

It carries three things a future effort would otherwise re-derive:

- **The three materialization sites re-located on current `main`** (S1 `constraint_jacobian.py:78`, S2 `index_mapping.py:634`, S3 `stationarity.py`), plus the **six** corpus-safety call sites that must be provably unperturbed.
- **The inverted gate.** sarf has no golden, so `make leak-check MODEL=sarf` reports `NO-OP` and fails for a non-correctness reason. The gate is `make check-goldens` — zero drift across 163 — **plus** sarf newly producing a golden (163 → 164).
- **A fixture constraint:** sarf cannot be its own fixture model, because at 369,024 columns the *fail-before* state does not terminate.

**One Task-7 precondition is now stale:** it recorded all three materialization-site files as byte-unchanged since the anchor. `stationarity.py` is now **+304** (markov Day 2, fawley Day 6). The sites themselves are intact and all six call sites remain at the recorded line numbers.

## 4. Disposition

**DEFER — the sixth consecutive.** The prior five were risk/reward judgements ("everything needed exists; the case against is budget"). This one adds evidence: the only viable lever is the 20–28 h atomic re-architecture, and a partial landing is explicitly a REPLAN rather than progress, because the change must land as one unit (2-D constraint gate + S1/S2/S3 short-circuit + parametric `stat_task` + `task.fx`) or the MCP is inconsistent — multipliers with no stationarity coupling.

Attempting it with the session's remaining capacity would have produced exactly the half-finished atomic change the design forbids. **Sprint 37 keeps its zero-broken-code record.**

**What Sprint 37 leaves for a dedicated effort that did not exist before:** a Phase-0 gate, a profile identifying the real hot path, and a measured refutation of the cheap alternative.

---

**Day 7 Status:** ✅ Complete — P5 profiled, Phase-0 authored, DEFER on measured grounds.
