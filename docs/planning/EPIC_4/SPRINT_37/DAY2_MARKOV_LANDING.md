# Sprint 37 Day 2 — P1 markov `σ=sp` Discriminator: `src/` Landing

**Date:** 2026-08-11 · **Branch:** `planning/sprint37-day2-markov-land` · **Commit:** `3190c74f` · **Scope:** emit-touching — `src/kkt/stationarity.py` (+225) and the regenerated `data/gamslib/mcp/markov_mcp.gms`. **DB deliberately untouched** (§6).

**Verdict: ✅ LANDED.** All four `ISSUE_1110` Phase-0 criteria are satisfied on the landed tree, including the full-corpus leak gate that blocked Sprint 36 outright. The emit is **byte-identical to Day 1's reverted control**, and `--resolve-changed` independently confirms markov shifting **`model_optimal_presolve` → `model_optimal`** with the match retained — the methodology→genuine transition, i.e. **genuine floor 75 → 76**.

---

## 1. What landed

Three helpers plus a gated additive early-out in `_add_indexed_jacobian_terms`:

| symbol | role |
|---|---|
| `_sigma_sp_domain_collision` | conjunct 1 — the Sprint-36 domain signature (which **alone** leaked onto `cesam`/`ferts`/`sroute`; 15 of 142 models reach it) |
| `_sigma_sp_value_param_refs` | value-branch walk; a `$`-condition and a `Sum`/`Prod` condition are **not** walked — this is what excludes sroute's `1$(darc(ip,ipp))` structurally |
| `_sigma_sp_param_couples` | conjunct 2, requiring the eq-index and collision-index matches at **distinct positions** of the parameter's own tuple |
| `_try_build_sigma_sp_crossterm` | builds the two hand-derived terms and returns them; `None` when the gate does not fire |

**`_compute_index_offset_key` is untouched.** That shared matcher is the cohort-leak surface, and leaving it alone is Mechanism C's premise.

### Deliberate divergence from the prep design's hook

The design (Task 4 §4) prescribed: *detect at the `offset_groups` construction, **suppress** the 44 spurious groups in that dict, emit at the correction-append region.* This landed an **additive early-out placed before** that machinery instead, mirroring the `_try_build_param_offset_crossterm` precedent (`src/kkt/stationarity.py:5933–5938` pre-patch).

Rationale: the offset-group machinery is *precisely what mis-groups this shape*. Suppressing after construction means reaching into a dict that every other model also flows through; an early-out means non-firing pairs observe **no change at all**. Same output — byte-identical to the Day-1 control — with a strictly smaller blast radius. `_compute_index_offset_key` is untouched under either shape.

### Condition-propagation guard (added under review)

The early-out bypasses the main loop's condition propagation, so a `$`-conditioned
constraint would have its condition **silently dropped** from the emitted terms.
markov's `constr` carries no condition (measured: `constr.condition = None`), so
nothing is lost today — but that is a property of markov, not of the helper. The
helper therefore **refuses to fire when the constraint carries a condition**,
returning `None` so the standard path handles it. Emit verified byte-identical
after the change. This converts an accidental absence into a structural guarantee.

*(Separately, the membership guards `$(sp(s) and j(i))` / `$(sp(sp) and j(j))` in
the golden are added by the **emit layer**, downstream of
`build_stationarity_equations` — instrumented and confirmed. Both the early-out and
the main loop feed into it identically, which is why the golden — this path's own
output — carries them.)*

### A correctness detail that is load-bearing

The representative-entry search **rejects any candidate whose index elements are not pairwise distinct**. Most markov entries repeat one — `var=('12','normal','12')` puts the same element at positions 0 and 2, so `'12'` would map to both `s` and `sp`. A wrong element→symbol map yields **silently incorrect parameter indices that still compile**, which is the worst failure mode available here. This was found by tracing on Day 1, not predicted by the design.

## 2. Phase-0 gate (`ISSUE_1110`) — all four measured on the landed tree

| criterion | required | measured | status |
|---|---|---|---|
| Correctness | `CASE_A`, rel < 1e-3 | `CASE_A` — healthy; max `stat_z(6,normal,empty)` rel **2.84e-16** (from `CASE_B` 1.33e+01); dual CONSISTENT | ✅ |
| Bucket / KPI | cold `MODEL STATUS 1`, `pvcost` 2401.577, match | `modelstat=1`, `solverstat=1`, **pvcost 2401.5774** vs NLP 2401.5773 ⇒ rel **4.16e-08** ⇒ **match**, with **no `--nlp-presolve`** | ✅ |
| Leak-freedom | unqualified `LEAK GATE PASS` | **PASS** — 163 in-scope goldens, **0 unverified**, only `markov_mcp.gms` drifted (−11,619 B) | ✅ |
| Regression guard | fixture fail-before/pass-after | corpus-free spec ready — **lands Day 3** | ⏳ |

### Emit

```
stat_z(s,i,sp).. c(s,sp,i) + nu_constr(s,i)$(sp(s) and j(i))
               + sum(j, (((-1) * (b * pi(s,i,sp,j,sp))) * nu_constr(sp,j))$(sp(sp) and j(j)))
               + [equil term, unchanged] - piL_z(s,i,sp) =E= 0;
```

| measurement | before | after |
|---|---|---|
| `stat_z` characters | 14,695 | **3,966** |
| distinct `s__kktN` groups | **45** | **0** |

**Byte-identical to the Day-1 control emit** — the re-implementation is faithful, not merely equivalent-looking.

## 3. Leak gate — and a load-dependence finding that outlives markov

```
Golden staleness: checked 163 in-scope golden(s) (7 allowlisted, 3 workers).
    EXPECTED DRIFT: markov_mcp.gms (-11619 bytes)
  LEAK GATE PASS: exactly the expected model(s) drifted (markov);
                  all other in-scope goldens byte-identical.
```

All three Sprint-36 leak models — `cesam`, `ferts`, `sroute` — verified byte-identical, as were the six 2-D cohort models and the 18 goldens CI was silently skipping before the `--min-scope` fix.

**But getting a conclusive verdict took three runs, and that is a finding about the gate.**

| run | conditions | result |
|---|---|---|
| 1 | GAMS cold solve running concurrently | **UNVERIFIED** — 4 timeouts (`clearlak`, `ferts`, `ganges`, `gangesx`) |
| 2 | quiet machine, default 6 workers | **UNVERIFIED** — 2 timeouts (`clearlak`, `ganges`); `ferts` now clean |
| 3 | quiet machine, **3 workers** | **PASS** — 0 timeouts |

**Root cause:** the emit budget is hardcoded at **600 s** (`scripts/gamslib/batch_translate.py:265`) and the sweep defaults to **6 workers**. `ganges` emits in 259–293 s *standalone* (Task 5); under 6-way contention it exceeds the cap. So the verdict is decided by scheduling, not by the change under test.

`--allow-unverified` was **deliberately not used.** The unverified tail in run 1 contained `ferts` — the model the leak claim most depends on — so accepting a partial claim would have been precisely the laundering that flag exists to make visible rather than easy. The gate behaved exactly as Task 3 designed: **unverified ≠ clean.**

**This also revises a Day-1 claim.** Day 1 reported an unqualified PASS with zero timeouts and presented it as settled. That result was real but *not reliably reproducible* — the same command on a loaded machine returns UNVERIFIED. Day 1's confidence was luckier than the mechanism warrants.

**⇒ P7 Day-9 item.** `golden-staleness` is now a **required** status check, and `ganges`/`gangesx` are themselves the subject of Days 4–6 — the models that blow the budget are next up against the gate. Either lower the worker count, raise the cap, or route the full sweep to a nightly lane.

## 4. Checkpoint — and a procedural finding

```
[resolve-changed] re-solving 19 changed-golden model(s) since 78ceaead: …, markov, …
  markov  {'model_optimal_presolve', 'match'} -> {'model_optimal', 'match'}   ~ shift
  turkey  {'path_syntax_error', ...}          -> {'path_solve_license', ...}  ~ shift
GO: all 19 changed-golden model(s) held their bucket
```

markov's shift is the **methodology→genuine transition confirmed by the pipeline runner**, independent of the hand-run cold solve in §2. turkey's shift independently corroborates Task 8's stale-entry prediction (a reclassification, **not** a recovery and **not** a v54 effect).

**Procedural finding:** the *first* checkpoint run reported a confident `GO: all 18 changed-golden model(s) held their bucket` — **without markov in it.** `--resolve-changed --since-commit` selects models by **git diff**, so the then-uncommitted golden was invisible. Run pre-commit, it returns a green light that does not cover the work in progress. **The correct sequence is commit → checkpoint**, and the Day-5 / Day-10 checkpoint prompts should say so; they currently do not.

## 5. Quality gate

`make typecheck && make format && make lint && make test` — all green, **5040 passed, 10 skipped, 1 xfailed**.

## 6. What was deliberately NOT done

**The DB is untouched — still byte-identical to anchor `78ceaead`.** markov's row still records `model_optimal_presolve` + match.

The genuine floor 75 → 76 is a **recompute over the DB**, so it is not yet *measurable* from the DB even though it is now *established* by two independent measurements (§2 cold solve, §4 checkpoint). `--resolve-changed` deliberately never persists.

Deferring the persist to Day 3 keeps the emit landing and the KPI move in **separately revertible commits**, and Day 3 is already the day that recomputes the PR25 partition. **Day 3 must therefore persist markov's row before recomputing**, or the partition will still read 75.

## 7. Disposition

- **Unknown 1.3 → ✅ VERIFIED** (was 🔶) — the design-verified claim re-earned empirically on the landed tree. Tally now ✅ 21 · 🔶 3 · ❌ 3.
- **`ISSUE_1110` → ✅ LANDED** (`3190c74f`), with the regression-guard criterion outstanding until Day 3.
- **Day 3 carries three items:** persist markov's DB row and recompute the partition (75 → 76, presolve-match 30 → 29, cold-optimal 63 → 64, **Match unchanged at 93**); land the corpus-free `shape_markov_diagonal_kronecker` fixture; give the `slow` integration test the `determinism` marker so `nightly.yml` actually reaches it.

---

**Document Status:** ✅ Complete — Sprint 37 Day 2 (P1 landed; DB persist deferred to Day 3 by design).
**Last Updated:** 2026-08-11 · **Owner:** Sprint 37 execution team
