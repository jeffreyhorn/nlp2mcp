# Sprint 32 — Day 0 Traces + Tractability Probes (PR24)

**Date:** 2026-07-14
**Day:** 0 (Kickoff — trace-only, no `src/` change)
**Anchor:** `4cbf8bff` (Sprint 31 close).

This is the PR24 Day-0 re-confirmation: each Phase-0 gate's `Traced Fix-Surface` is a *hypothesis* re-verified on the current tree **before** any Sprint-32 `src/` change. All runs read-only (the `kkt_residual.py` harness + a set-cardinality probe).

---

## 1. Baseline confirmation

- **`git diff 4cbf8bff..HEAD -- src/ scripts/` is EMPTY** → no source/pipeline drift since the Sprint-31 close; the Day-0 baseline holds with **no fresh retest** needed.
- **DB recompute:** 219 models; **142 convex candidates**; **107 solved** (the 142-corpus `success` bucket) — reproduces the Sprint-31-final headline: **Parse 142 · Translate 135 · Solve 107 · Match 92 (genuine floor 74) · model_infeasible 7 · Tests 5,074 · all-219 Match 95** (`BASELINE_METRICS.md`).

## 2. Day-0 traces — Phase-0 fix-surface re-confirmation (`kkt_residual.py --tol 0.001`)

All four harness-runnable tracks re-confirmed **exactly** to their banked fingerprints; **dual-transfer CONSISTENT** on every one (so the residual is a genuine stationarity signal, not a transfer defect):

| Track | Verdict | Max-residual row | rel (raw) | Banked fingerprint | ✓ |
|---|---|---|---|---|---|
| **mine** (#1443, P1) | CASE_B | `stat_x(3,1,1)` | **2.37** (−3.20e4) | CASE_B `stat_x(3,1,1)` 2.37 | ✅ |
| **camcge** (#1330, P3) | CASE_B | `stat_mps` | **1.05** (**−2.10e2**) | CASE_B `stat_mps`, `mps.m = −209.861` | ✅ |
| **rocket** (#1462, P4) | CASE_B | `stat_ht(h0)` 1.00 / `stat_step` 0.50 / `stat_ht(h50)` 0.44 | interior `stat_v(h0)` 0.038 / `stat_m(h0)` 0.014 near tol | Case-c **boundary** signature | ✅ |
| **hhfair** (#1236, P5) | CASE_B | `stat_u(1)` | **2.00** (−36.1); `stat_u(2)` 1.89 / `stat_u(3)` 1.78; interior `stat_a` ~0.005 | D1: `stat_u` rel 2.0, `nu_obj=±1` | ✅ |

- **mine:** the bound-active `stat_x` residual localizes with duals CONSISTENT (`lam_pr`/`pr.m` correct) — the mismatch is the `piL_x/piU_x = ±x.m` warm-start transfer (`src/emit/emit_gams.py:1548–1577`), exactly as Task 3 pinned.
- **camcge:** the raw `stat_mps` residual **−210** corroborates the banked `mps.m = −209.861` → `nu_mps_fx.l = -mps.m` (step 1) closes it (`0 = −210 + 209.861 + ε`).
- **rocket:** the residual concentrates on the boundary rows (which move with the warm-start value) with the interior near tolerance — the non-convex Case-c boundary signature (a forcing problem, not a latent emit bug).
- **hhfair:** the residual concentrates on the objective-defining intermediate variable `stat_u` at rel exactly 2.0 (the `nu_obj=±1` sign-choice signature, D1) — genuine Case-c.

## 3. Tractability probes (the Task-9 single-model validations)

- **(P1) mine warm-residual→0 — pre-fix fingerprint re-confirmed.** The harness reports CASE_B `stat_x(3,1,1)` rel 2.37 at the NLP optimum (§2). The Task-3 `N`-derivation (`piL_x = max(N,0)`, `piU_x = max(−N,0)`) closes `stat_x = N − piL_x + piU_x = 0` by construction → Case-a. **The full `/tmp` hand-edit + warm-residual→0 re-run is the Day-1 pre-`src/` control** (assert `modelstat`; `x.up=inf` BANNED).
- **(P3) camcge dual-consistent — step-1 fingerprint re-confirmed.** The harness raw `stat_mps` = −210 confirms `mps.m ≈ −209.861` → step 1 (`nu_mps_fx.l = -mps.m`) → `stat_mps` Case-a. **The step-1 + dual-consistent-Walras `/tmp`-to-MS-1 (omega 191.7346) prototype is the Day-4 pre-`src/` control** (check the dual side; Task 5 established it in prep).
- **(P2) sarf O(active) sizing — re-confirmed.** `task(g,t,mn,mn)` is a 4-D variable; the constraint gate `tbal(g,t)$taskposs` is 2-D (fires but does **not** sparsify the 4-D `task` stationarity). Cardinalities (Day-0 re-confirmed: **`card(g)=16`**, `card(t)=24`; `card(mn)=31` per the Task-4 GAMS data probe — a textual set-parse over-counts the hyphenated machinery names, so the GAMS-evaluated 31 is authoritative) → **Cartesian = 16·24·31·31 = 369,024**; active `taskposs(g,t) ∧ tech(g,m,n)` = **398** → a **927× reduction**. The fix is **one symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)`** (translate-time O(1 equation)) + `task.fx$(not active)=0` — decisively tractable.

## 4. PR25 tally (genuine vs methodology)

- **Genuine floor 74 / methodology 21** (all-219 Match 95 = 74 genuine + 21 methodology) — the Day-0 anchor.
- **The → ≥ 75 conversion map:** mine [P1] cold-match (+1) and/or camcge [P3] cold-match (+1) — a **genuine emit change**, not presolve reclassification; plus any **P6 emit gain** (cpack offset-alias generalization / fawley second-index Case-b). **P5 delivers 0 floor** (documented Case-c). Reaching ≥ 75 needs ≥ 1 of these cold-matches; ≥ 76 needs both mine + camcge (Task 9 / Sprint-31 §3).

## 5. Day-0 disposition

**GO for Day 1.** The baseline holds byte-for-byte (empty `src/`/`scripts/` diff), all four harness fix-surface fingerprints re-confirmed exactly to their banked values (duals CONSISTENT throughout), and the three tractability probes re-verified (mine `N`-derivation pre-fix fingerprint; camcge step-1 `−210`/`mps.m`; sarf 369,024→398 sizing). The Day-1 first step is the mine bound-multiplier emit at `src/emit/emit_gams.py:1548–1577`, gated on the `/tmp` warm-residual→0 control run first (PR24/PR27).

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 execution
**Evidence:** the `kkt_residual.py --tol 0.001` runs on mine/camcge/rocket/hhfair (verdicts + max-residual rows above); `git diff 4cbf8bff..HEAD -- src/ scripts/` (empty); the committed-DB 142-candidate recompute; the sarf set-cardinality probe + the Task-4 GAMS-evaluated 369,024/398. The raw model `.gms` under `data/gamslib/raw/` are fetched via `gamslib <name>` (not checked in).
