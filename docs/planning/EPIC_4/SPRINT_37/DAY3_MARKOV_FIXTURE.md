# Sprint 37 Day 3 — P1 markov: Fixtures + Floor Verification

**Date:** 2026-08-11 · **Branch:** `planning/sprint37-day3-markov-fixture` · **Scope:** tests + DB. **First persisting DB change since anchor `78ceaead`** (§1). No `src/` change.

**Verdict: ✅ COMPLETE — the genuine floor is 76.** The DB now records markov as cold-optimal, the PR25 partition recompute matches the projection **exactly** on every line, and `ISSUE_1110`'s fourth and final Phase-0 criterion (regression guard) is satisfied. The integration test that had been **red since March** is green and now actually runs in a CI lane.

---

## 1. DB persist — markov's bucket move

Day 2 established the cold match by two independent measurements but deliberately left the DB untouched, so the floor was *established* without being *measurable*. Persisted here via `run_full_test.py --model markov` (DB snapshotted first; md5 `6166acab…`).

**Exactly one row changed:**

| field | before | after |
|---|---|---|
| `mcp_solve.outcome_category` | `model_optimal_presolve` | **`model_optimal`** |
| `mcp_solve.presolve_required` | `True` | **`None`** |
| `solution_comparison.mcp_objective` | 2401.5773 | 2401.577 |

`comparison_status` stays **`match`** — as it must, since markov already counted in Match 93.

## 2. PR25 partition recompute — the projection, met on every line

| KPI | measured | projected | status |
|---|---|---|---|
| Parse | 142 | 142 | ✅ |
| Translate | 135 | 135 | ✅ |
| Solve | 108 | 108 | ✅ |
| **Match** | **93** | 93 (**unchanged**) | ✅ |
|   cold-optimal | **64** | 64 (was 63) | ✅ |
|   presolve (methodology) | **29** | 29 (was 30) | ✅ |
| model_infeasible | 7 | 7 | ✅ |
| path_syntax_error | 7 | 7 | ✅ |
| all-219 Match | 96 | 96 | ✅ |

**⇒ genuine floor 75 → 76.** The first floor advance since Sprint 33, and the first KPI movement of Sprint 37.

**It is a partition transfer, not a Match gain.** markov moved *between* partitions (presolve-match 30 → 29, cold-optimal 63 → 64) while the Match total held at 93. Reporting "+1 Match" would double-count a model that was already in the total — the mis-report this sprint has been guarding against since Task 10.

## 3. `shape_markov_diagonal_kronecker` — corpus-free, three tests

`tests/unit/kkt/test_shape_markov_diagonal_kronecker.py`, `pytest.mark.unit`, **no skip guard**, **1.08 s**.

| test | asserts |
|---|---|
| `test_kronecker_diagonal_is_a_bare_additive_term` | `nu_constr(s,i)` is a bare additive term and is **not** inside a sum over indices it does not depend on |
| `test_off_diagonal_is_a_single_sum_without_the_kronecker_one` | the σ=sp off-diagonal is a single `sum(j, … pi(s,i,sp,j,sp) … nu_constr(sp,j))` with no fused `1 -` |
| `test_call_nodes_survive_symbolization` | a `Call` in the derivative is re-symbolised rather than crashing (§4) |

**Why corpus-free:** the obvious spelling — parse `raw/markov.gms`, `pytest.skip` if absent — would skip on **every** CI run, because `ci.yml` provisions only the five `--fast` fixtures and markov is not among them (Task 10 §1.1). The synthetic runs unconditionally.

**Scale-down is safe** because the assertions are structural. The synthetic is `|s|`=3 against markov's 8, which changes the *number* of spurious groups (15 vs 45) but not the shape — so no test asserts a group count.

### Fail-before verified against real trees, not asserted

| tree | result |
|---|---|
| pre-landing (`4c5e09be`, no discriminator) | **all 3 fail** |
| landing with the review bug (`3190c74f`, `Call(e.name)`) | **only `test_call_nodes_survive_symbolization` fails**, with `AttributeError: 'Call' object has no attribute 'name'` |
| current `main` | **all 3 pass** |

The middle row is the point: the `Call` test isolates *that* defect specifically, rather than merely failing because the whole feature is absent.

## 4. The `Call` branch now has real coverage

PR #1665's third review round found that `symbolize()` rebuilt `Call` nodes with `e.name` while `Call` stores the function name in `func`. It was **unreachable from the corpus** — markov is the only model the gate fires on, and its derivative is `Unary(-, Binary(*, ParamRef, ParamRef))` with no `Call` — so the fix shipped verified only by direct construction.

The synthetic closes that: swapping the coupling to `exp(pi(s,i,sp,j,spp))` produces a derivative containing a `Call` **and** still fires the gate, giving the first end-to-end exercise of that branch.

A detail worth recording: `Call(e.func, …)` was already the established idiom **three times in the same file** (`:2853`, `:5442`, `:5700`). The bug was a lone deviation from a local convention — the kind of thing a reviewer catches and a narrow gate never will.

## 5. The integration test — green, and now in a lane

`tests/integration/kkt/test_markov_multi_pattern.py` had been **red since March**.

**Sharpened to the σ=sp target.** Its old assertions expected `sum(...) * nu_constr(s__kkt1,...)` — the *partially* corrected shape, which still carried one spurious offset group per set element. Post-landing there are zero, so those assertions would have been **asserting on the bug**. Replaced with four: the bare diagonal, the collapsed σ=sp sum, **zero** `s__kktN` groups, and no fused Kronecker `1`. **Now passes.**

**Marker fix — it ran in no CI lane at all.** `ci.yml` selects `-m "not slow and not determinism"`, `nightly.yml` selects `-m "slow and determinism"`. A `[integration, slow]` test is excluded by both. Adding `determinism` routes it into nightly; verified by collection:

```
ci.yml lane      -m "not slow and not determinism"  ->  0 collected (1 deselected)
nightly.yml lane -m "slow and determinism"          ->  1 collected
```

**An honest caveat.** The `determinism` marker is registered as *"Byte-stability regression tests across PYTHONHASHSEED values (PR12)"*, and this test is not one. Using it here is **routing, not semantics** — a pragmatic fix, per Task 10 §1.3. The cleaner alternative is widening nightly's selector to `-m "slow"`, but that pulls in **39** tests where the current selector takes **2**, so it is a scheduling decision rather than a marker edit. **Logged as a P7 Day-9 item** alongside the leak-gate worker/cap question.

## 6. `ISSUE_1110` Phase-0 — complete

| criterion | status |
|---|---|
| Correctness | ✅ `CASE_A`, rel 2.84e-16 |
| Bucket / KPI | ✅ cold `modelstat=1`, 2401.5774, match ⇒ **floor 76** |
| Leak-freedom | ✅ `LEAK GATE PASS`, 163 goldens, 0 unverified |
| **Regression guard** | ✅ **3 fixtures, fail-before verified against two trees** |

**All four criteria met.** The P1 track is closed.

## 7. Quality gate

`make typecheck && make format && make lint && make test` — green, **5043 passed** (5040 + the 3 new fixtures), 10 skipped, 1 xfailed.

## 8. Disposition

- **Genuine floor 76** is now measurable from the DB, not merely established.
- **The DB is no longer byte-identical to `78ceaead`** — one row, deliberately, with a snapshot taken first.
- **Two P7 Day-9 items** now accumulated: the leak gate's worker/cap load-dependence (Day 2) and the `determinism`-marker-as-routing stretch (§5).
- **Day 4 opens P2 ganges** — and inherits Day 2's gate-capacity warning directly, since `ganges` and `gangesx` are the two models that blow the leak sweep's 600 s emit budget.

---

**Document Status:** ✅ Complete — Sprint 37 Day 3 (P1 closed; genuine floor 75 → 76).
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 execution team
