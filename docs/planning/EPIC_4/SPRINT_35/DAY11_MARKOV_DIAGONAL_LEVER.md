# Sprint 35 — Day 11 (slack): markov `stat_z` diagonal-Kronecker emit bug — a de-risked **+1 genuine-floor lever**, banked to Sprint 36

**Day:** 11 (REPLAN-slack + P6/P7 continuation) · **Date:** 2026-08-04 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day11-slack` · **Scope:** docs-only (no `src/`). **0 in-sprint bucket; a confirmed +1-floor lever discovered, diagnosed, and banked.**
**Outcome: the Day-10 markov `slow`-test finding (Follow-up 3) resolves to a genuine cold-emit stationarity bug (`CASE_B`, `max|stat_z|` rel 13.3). markov is currently a *methodology* match (presolve-rescued); a correct cold emit would flip it methodology→genuine = genuine floor 75→76. The fix is a deep change to the shared multi-pattern (#1110) machinery that never emitted the correct form — high-blast-radius across the matching 2-D cohort — so it is BANKED to a dedicated Sprint-36 effort, not landed on a slack day.**

---

## 1. Why this is a real lever (not a stale test)

- **markov is `verified_convex` and currently `model_optimal_presolve` + `match`** — i.e. it is in the **Methodology (21)** partition (`SPRINT_35/BASELINE_METRICS.md:134`), *not* counted in the genuine floor. Its cold MCP does **not** reach optimal; presolve rescues it.
- **The KKT-residual control (PR27, `kkt_residual.py data/gamslib/raw/markov.gms`) returns `CASE_B — emit_bug`:** `max|stat_z|` rel **13.3** (raw −4.79e+04) on `stat_z(empty,disrupted,*)`, dual_scale 3.6e+03, **dual transfer CONSISTENT** (comp-infeas 0, equality residual 6e-16). So the cold emit is *mathematically wrong* (not a non-convexity / not a warm-start artifact), and the divergence is entirely in `stat_z`.
- **Therefore a correct cold emit ⇒ `CASE_A` ⇒ cold `model_optimal` ⇒ genuine match.** markov moves methodology→genuine: **genuine floor 75 → 76 (+1)**, high-confidence contingent on the fix landing and a cold re-solve confirming `model_optimal` (markov is tiny — 2 vars / 3 eqns / 212-line MCP — so the re-solve is fully local, no testbed gate).

This is the **first bucket-relevant lever surfaced this sprint** — every deep track (P1 mine, P2 sarf, P3 fawley, P4 ganges, P5 camcge/rocket) was refuted or banked as *not* an emit defect. markov is the opposite: a control-confirmed emit defect on a convex model with a concrete, local +1 payoff.

## 2. The bug — the Kronecker `1` is summed over the enumeration dummy

markov is an LP: `constr(sp,j).. sum(spp, z(sp,j,spp)) - b*sum((s,i,spp), pi(s,i,sp,j,spp)*z(s,i,spp)) =e= beta`.

Hand-deriving stationarity for `z(s,i,sp)`:
```
∂constr(σ,τ)/∂z(s,i,sp) = [σ=s][τ=i]  −  b·pi(s,i,σ,τ,sp)
```
- the **Kronecker `[σ=s][τ=i]`** (from the direct `sum(spp, z(sp,j,spp))` reference) ⇒ a **single, direct** `+ nu_constr(s,i)` diagonal term;
- the **`−b·pi`** (from the summed reference) ⇒ the **off-diagonal sum** `Σ_(σ,τ) −b·pi(s,i,σ,τ,sp)·nu_constr(σ,τ)`, with `nu` indexed by the **summed** pair.

So the correct first term is `nu_constr(s,i) + sum((s__kkt1,j), (−b·pi(s,i,s,i,s__kkt1))·nu_constr(s__kkt1,j)$(…))` — a direct Kronecker term split out of the sum. This is exactly the `test_markov_stationarity_has_correction_term` docstring's intended "after the fix" form.

**The current emit's term 1 (`markov_mcp.gms:162`, and the fresh CLI emit):**
```
sum((s__kkt1,j), ((1 - b * pi(s,i,s,i,s__kkt1)) * nu_constr(s,i))$(sp(s) and j(i)))
```
fuses the Kronecker `1` with `−b·pi` **inside** the sum over the enumeration dummy `(s__kkt1,j)`. Since neither `1` nor `nu_constr(s,i)` depends on `s__kkt1`, the Kronecker `1` is **summed `card(s)=8` times** (only the `pi` factor collapses to `s__kkt1=s`) ⇒ the diagonal is inflated ~8× ⇒ the rel-13 residual. (It also mis-indexes `nu` as the outer `(s,i)` rather than the summed `(s__kkt1,j)`.) Terms 2–45 (the `s__kkt2..45` offset patterns) are **already correct** off-diagonal form — **only term 1 is buggy.**

## 3. Archaeology — the correct split was NEVER emitted (test red from birth, hidden by `slow`)

| golden SHA | date | `stat_z` first-term form |
|---|---|---|
| 2bd8ff5f | 03-16 | `(1 − b·pi(s,i,s__kkt1,j,sp)) · nu_constr(s__kkt1,j)` |
| **db385a43 / 839095c1** | 03-24 | `(1 − b·pi(s,i,s,i,s__kkt1)) · nu_constr(s__kkt1,j)` — #1110 "fix" (pi-index only) |
| **717bb971** (PR #1198) | 04-02 | `(1 − b·pi(s,i,s,i,s__kkt1)) · nu_constr(s,i)` + 44 `s__kkt2..45` offset sums |
| 2bfb2a6d | 06-05 | current form (+`$(sp(s) and j(i))` guard) |

- **`db385a43`** (2026-03-24, "Fix multi-pattern Jacobian for markov (#1110)") introduced `_multi_pattern_correction` + `_derivative_structure_key` but only fixed the `pi` index; the Kronecker `1` stayed **inside** the sum.
- The test (`c5958aee`, PR #1151, 2026-03-25) asserts the *split* form. **It has never passed** — assertion 1 (`nu_constr(s,i) in stat_z`) failed at birth; after PR #1198's `(s__kkt1,j)→(s,i)` mutation, assertions 2/3 fail instead. Hidden the whole time by `pytest.mark.slow` (excluded from `make test`).

**Verdict: never-emitted deep bug**, not a regression to restore. (This resolves the Day-10 Follow-up 3 open question "regression vs stale assertion": neither — the assertion is *correct* and the emit has *always* been wrong.)

## 4. The fix surface + why it is a dedicated effort (not a slack-day landing)

The live #1110 machinery in `_add_indexed_jacobian_terms` (`src/kkt/stationarity.py:5861`):
- **:6263–6293** — multi-pattern detection: groups Jacobian entries by `_derivative_structure_key`, builds `_multi_pattern_correction` only when `_has_second_pattern` **and** `len(_sg) > 1`.
- **:7187–7190** — appends the correction as a separate `+` term.
- **:570–575** — a single-pattern guard that *avoids* the #1110 path.

For markov's `stat_z` first group the detection does **not** fire (`_multi_pattern_correction` is `None`): the diagonal derivative `(1 − b·pi(…))` is emitted verbatim as `derivative·mult` with `mult = nu_constr(s,i)`, summed. The fix must make the detection recognize markov's diagonal-vs-off-diagonal split and pull the Kronecker `1` out to a direct term — i.e. genuinely repair the machinery that `db385a43` only partially fixed.

**This is high-blast-radius.** `_add_indexed_jacobian_terms` / `_multi_pattern_correction` is the shared path for the whole 2-D cohort — **cesam2 (`model_optimal` + match), camcge, ps2_f_s, ps2_s, ps3_s_gic, polygon (match)** — plus every `sameas`/#1104/#1049/#670/#1110 model. Leak-freedom (golden-staleness: only markov drifts; cohort byte-identical) is mandatory and non-trivial. **The direct precedent is Sprint-35 Day 9**, where a *simpler* shared-function change (the fawley constraint-index-diagonal predicate) **leaked onto markov** and forced a revert. A deep repair of the multi-pattern detection is not a safe slack-day change; it needs a dedicated effort with the full 2-D-cohort + multi-pattern regression harness.

## 5. Sprint-36 hand-off (implementer-ready)

- **Payoff:** methodology→genuine, **floor 75→76 (+1)**; contingent on the fix + a cold re-solve showing `model_optimal` (local, tiny model).
- **Control (done):** `kkt_residual.py data/gamslib/raw/markov.gms` = `CASE_B`, `max|stat_z|` rel 13.3 → after the fix must reach `CASE_A` (rel < tol). The tiny model makes each iteration cheap.
- **Target form (term 1):** `nu_constr(s,i)` (direct) `+ sum((s__kkt1,j), ((-1)*(b*pi(s,i,s,i,s__kkt1)))*nu_constr(s__kkt1,j)$(…))` — split the Kronecker out; index the off-diagonal `nu` by the summed dummy (matching terms 2–45 and the test docstring).
- **Fix surface:** the multi-pattern detection at `:6263–6293` (make it fire for markov's constr diagonal group) + the correction append at `:7187`; do **not** hand-special-case markov.
- **Gates:** golden-staleness (only markov drifts; the 2-D cohort byte-identical), `--resolve-changed --since <SHA>` GO, determinism ×3, and the existing `test_markov_stationarity_has_correction_term` flips red→green (decide its `slow`/`xfail` disposition *with* the fix — the assertion is correct as-is).

## Outcome

**0 in-sprint bucket** (docs-only, no `src/`), but the slack day converted a silently-red `slow` test into a **fully-diagnosed, control-confirmed +1 genuine-floor lever** — the sprint's only such lever. Banked to a dedicated Sprint-36 markov effort (deep multi-pattern-machinery repair, cohort-leak-proofed). P4 (ganges/gangesx ≥5-blocker cascade) and P6 residuals (turkpow/clearlak/dinam/indus, heavily multi-root) dispositions are unchanged — the slack was best spent discovering and de-risking this lever rather than re-litigating refuted tracks.

**Next (Day 12):** slack / carryforwards. **Day 13:** retest (GAMS-version axis; turkey +1 testbed re-solve). The markov lever + this note feed the Sprint-36 planning (a fourth banked track alongside the [FOLLOWUPS_GAMS54_TRANSITION.md](FOLLOWUPS_GAMS54_TRANSITION.md) items and the [CONSULTATION_BUNDLE](../SPRINT_36/CONSULTATION_BUNDLE.md)).

---

**Document Status:** ✅ Complete — Sprint 35 Day 11 (markov +1-floor lever discovered, diagnosed, banked)
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team
