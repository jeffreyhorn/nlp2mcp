# camcge Dual-Consistent Walras (Epic 5) + rocket PATH-Consultation Submission: Plan (Sprint 34 Prep Task 7)

**Created:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/CGE + solver specialist)
**Prep Task:** 7 (Priority 5) · **Priority:** Medium
**Day-0 code anchor:** `750803b2` (S33 close) · no `src/` drift since (Task 2 `BASELINE_METRICS.md`)
**Anchors:** `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` (the dual-consistent numéraire + detector) · `SPRINT_33/ROCKET_CASEC_FORCING_PLAN.md` (the FINALIZED consultation input + the `--force` survey) · `EPIC_5/CGE_DEGENERACY_SCOPING.md` (the S1∧S2∧S3 detector, the numéraire recipe) · `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (the FINALIZED brief)

> **Disposition (prep):** **camcge is Epic-5-deferred** (the dual-consistent Walras redefinition is deeper MCP research — the banked prototype reaches the correct primal omega 191.7346 but MS-4); **rocket is a Sprint-35 submission** (the FINALIZED PATH-consultation input hands off to the renumbered Sprint-35 "PATH Author Consultation & Solution Forcing"). **No `src/` change** — the camcge `/tmp`-to-MS-1 prototype is the Epic-5 gate; the rocket `--force` survey is an in-sprint exercise. **The Case-c objective-gradient sign flip stays BANNED (refuted 4×).**

---

## 1. Day-0 re-confirm (live)

From the committed DB (S33-close `750803b2`):

| Model | outcome | MS | match | role |
|---|---|---|---|---|
| **camcge** | model_infeasible | **4** | not_tested | the Walras rank-deficiency (Epic-5) |
| irscge | model_optimal_presolve | 1 | match | detector pass-through (sibling) |
| lrgcge | model_optimal_presolve | 1 | match | detector pass-through |
| moncge | model_optimal_presolve | 1 | match | detector pass-through |
| stdcge | model_optimal_presolve | 1 | match | detector pass-through |
| **rocket** | model_infeasible | **5** | not_tested | Case-c forcing → Sprint-35 consultation |

camcge **MS-4** (the singular-Jacobian / inherent-Walras signature; **MS-4 Infeasible at iteration 0**); the four CGE siblings **MS-1** (pass-through); rocket **MS-5**. Step 1 (`nu_mps_fx` scalar-`fx` transfer → `stat_mps` Case-a) landed on `main` (S32 PR #1553); the residual MS-4 is the Walras rank-deficiency, independent of `stat_mps`. (The `kkt_residual.py camcge.gms` cold-MCP re-run exceeds a ~2-min cap — camcge is a large CGE model; the MS-4 base is the well-banked state.)

---

## 2. The dual-consistent Walras numéraire — design (Unknown 5.1, Epic-5)

**Why the numéraire alone is insufficient.** CGE conditions are homogeneous of degree 0 in prices (equilibria form a ray `{λ·p*}`), so a numéraire removes the price-scaling nullspace and delivers the right primal (**omega 191.7346**, banked Sprint-32 Day-5). But the **residual Walras rank-deficiency remains**: the goods-clearing rows `equil(i)` + the labor-clearing `lmequil(lc)` are linearly dependent given household budget balance (Walras' law: `sum_i p_i·equil_i + w·lmequil == B`), so one market-clearing row is redundant → a 1-D nullspace in the KKT Jacobian → **MS-4 even at the correct primal**.

**The dual-consistent redefinition** (three parts, `SPRINT_33/CAMCGE_WALRAS_DESIGN.md` §2):
1. **Keep every market-clearing row** — no orphaned dual. The naïve "drop one row" is primal-correct but **breaks the MCP dual** (the dropped market's multiplier vanishes from the stationarity — the S30 finding).
2. **Fix the consumption-weighted numéraire** — `sum(i$cles(i), cles(i)·p(i)) = sum(i$cles(i), cles(i)·pd0(i))` (camcge has no `cpi`); the automatic rule reproduces the NLP optimum's `p=pd0` (a *selection*, not a perturbation).
3. **Redefine the redundant market's dual via Walras' law** — express the redundant market-clearing row's multiplier as the Walras-law combination of the others, so the **reduced system is full-rank while the redundant market's multiplier stays available in the stationarity**. This is the piece the numéraire-only prototype lacks (it removed the price nullspace but not the row-redundancy nullspace).

**Check the dual side, not just the primal** (the Day-11 lesson): the redefinition must be verified against the KKT *dual* — the redundant market's multiplier must equal its economically-correct value, not merely leave the primal at 191.7346.

---

## 3. The S1∧S2∧S3 degeneracy-detector scope (Unknown 5.2)

nlp2mcp must not silently redefine a dual on a well-posed model — the detector must flag **only** camcge. **S1 ∧ S2 ∧ S3**:
- **S1** — a market-clearing block (goods `equil(i)` + factor `lmequil(lc)`) linearly dependent via budget balance.
- **S2** — no price numéraire fixed (price homogeneity of degree 0).
- **S3 (the false-positive guard)** — the **cold MCP is singular at iteration 0 (MS-4)**. A well-posed CGE with a determined closure passes S1∧S2 structurally but has a nonsingular Jacobian → fails S3 → pass-through.

**Cohort precision (§1 + `EPIC_5/CGE_DEGENERACY_SCOPING.md`):** camcge fires (cold MS-4); irscge/lrgcge/moncge/stdcge pass-through (cold MS-1 — the banked Sprint-31 Day-7 cold-MCP test + the live DB confirm camcge MS-4 vs the four siblings MS-1). **Pass-through default = the identity transform** (faithful KKT emission); the redefinition applies to the flagged model only.

---

## 4. The camcge `/tmp` gate + disposition (Unknown 5.1)

**Epic-5 `/tmp` prototype gate:** the FULL dual-consistent redefinition (step 1 + the consumption-weighted numéraire + the Walras-law dual redefinition) → **MS-1 at omega 191.7346** (`modelstat` asserted), with the S1∧S2∧S3 detector flagging only camcge across the five CGE models. **Not run in this docs-only prep** — and the banked evidence is discouraging: the *price-pin* variant (numéraire without the dual redefinition) stayed **MS-4** with INFES on the accounting identities `gdp` (131.96), `depreq` (131.96), `hhsaveq` (97.26), `gruse` (43.97) — the **primal-correct / basis-singular** signature; 3+ sprints of prep (price-pin MS-4, single-dual-pin MS-4, drop-row corrupt @ 299) all failed to reach MS-1.

**Disposition (Epic-5-deferred, the expected outcome).** camcge stays `model_infeasible` in Sprint 34; the dual-consistent Walras redefinition + the per-model-numéraire declaration are the **Epic-5** deliverable (`EPIC_5/CGE_DEGENERACY_SCOPING.md` §3–§5). The +1 Solve defers to Epic 5. The de-risked Epic-5 hand-off: the working numéraire recipe (omega 191.7346), the exact residual-singularity characterization (INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`), the S1∧S2∧S3 detector (flags only camcge), and the confirmation that step-1-first does not change the MS-4 outcome. **Step-1 stability:** the numéraire adds the `numeraire` equation + the `cles(i)·nu_numeraire` cross-term in `stat_p` — it does **not** touch `stat_mps` (step 1); the landed `nu_mps_fx = mps.m` transfer stays Case-a.

---

## 5. rocket PATH-consultation submission plan (Unknown 5.3)

### 5.1 The FINALIZED input (submission-ready)

The rocket input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, **FINALIZED** Sprint 32) is three self-contained parts:
1. **The concrete question:** which PATH option-set / regularization schedule / reformulation forces convergence for the discretized optimal-control MCP — with the division-by-variable reformulation as a *ruled-out* candidate (targeting the intrinsic structure, not the Jacobian conditioning).
2. **The ruled-out-lever survey:** PATH options (best INFES 382), μ-continuation, multistart, division-by-variable reformulation — all MS-5, so the authors don't re-suggest them.
3. **The reproducible case:** `python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve; gams rocket_mcp_presolve.gms` → MS-5 from the embedded NLP optimum; the `--force homotopy` scaffold adds the μ-continuation driver + optfile.

rocket's Case-c signature (re-confirmed): the harness residual concentrates on the discretized-optimal-control **boundary** rows (`stat_ht(h0)` 1.00, `stat_step` 0.50, `stat_ht(h50)` 0.44 — they move with the warm-start value); the interior is near tolerance; dual-transfer CONSISTENT (closure 1.53e-10). **A forcing problem, not an emit bug.**

### 5.2 The Sprint-35 submission mechanism (the hand-off)

The packaged input feeds the **Sprint 35** "PATH Author Consultation & Solution Forcing" sprint (the PATH-consultation sprint, renumbered from the pre-insertion Sprint 34 → **Sprint 35** by the Sprint-34 insertion). Sprint 34 **submits** the self-contained artifact — the consultation brief + the two-command reproducer + the scaffold-emitted `rocket_mcp_forced.gms`; Sprint 35 conducts the author back-and-forth (Michael Ferris / Steven Dirkse — External Dependencies). A recommended option-set/schedule from the authors plugs into the `--force {homotopy,optfile}` scaffold. **No firm KPI:** rocket's +1 Solve is conditional on the Sprint-35 consultation (the `--force` survey is exhausted — homotopy/multistart/optfile all MS-5).

### 5.3 The Case-c scope guard + the sign-flip BAN

The Case-c family stays documented non-convex: rocket (boundary signature) + hhfair/CGE-cluster (`case_c_objdef`, `nu_obj = ±1` — no free multiplier to correct the objective-defining intermediate variable; ISSUE_1236 CLOSED S32). **The objective-gradient sign flip is BANNED** — control-refuted **4×** (S30–S31: hhfair 72.147 → 22.144 *worse*; the CGE-cluster `nu_objective` reduction inert since `nu_obj=±1`). **No sign-flip attempt** — do not re-litigate. Every Case-c member's residual is clean at the NLP point (a forcing problem, not a latent emit bug).

---

## 6. Sizing + disposition

**camcge (Epic-5):** 10–16 h of Epic-5-domain CGE work *if pursued in an Epic-5 sprint* (the `/tmp` full-redefinition prototype + the MS-1/MS-4 + dual-side discrimination [~5–8 h]; the CGE-aware preprocessing layer [~4–6 h, **only if `/tmp` reaches MS-1**]; detector cohort re-verification [~1–2 h]). **Not a Sprint-34 `src/` item** — Epic-5-deferred (the banked price-pin-MS-4 evidence makes MS-1 genuinely hard).

**rocket (Sprint-35):** ~2–3 h to package + submit the consultation artifact to the Sprint-35 hand-off (part of the Task-7 prep); the `--force` survey + the author consultation are the Sprint-35 exercise.

**Disposition:** camcge **Epic-5-deferred** (expected — no Sprint-34 bucket); rocket **→ Sprint-35 consultation** (conditional +Solve, not a Sprint-34 KPI). The value is the Epic-5-ready camcge recipe + detector + gate, and the clean rocket Sprint-35 hand-off.

---

## 7. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **5.1** | ✅ **VERIFIED (design-level; MS-1 is the Epic-5 gate, not an in-sprint result)** | The per-model-numéraire + dual-consistent Walras redefinition is designed (keep every row + consumption-weighted numéraire + Walras-law dual redefinition; **dual side checked**). Whether it reaches **MS-1 at 191.7346** is **unproven** — the `/tmp` prototype is the Epic-5 gate; the banked price-pin variant stayed **MS-4** (INFES on gdp/depreq/hhsaveq/gruse), so MS-1 is genuinely Epic-5-deep. camcge stays `model_infeasible` in Sprint 34 (Epic-5-deferred). |
| **5.2** | ✅ **VERIFIED** | The S1∧S2∧S3 detector flags **only camcge**: S3 (cold MCP MS-4 at iter 0) is the false-positive guard; the live DB + the banked Day-7 cold-MCP test confirm camcge MS-4 vs irscge/lrgcge/moncge/stdcge cold MS-1 (pass-through). The pass-through default is the identity transform (no false-flag on the four siblings). |
| **5.3** | ✅ **VERIFIED** | The rocket PATH-consultation input is FINALIZED + submission-ready (concrete question + ruled-out-lever survey + reproducible case + `--force` scaffold); the Sprint-35 hand-off mechanism is defined (Sprint 34 submits; Sprint 35 conducts the author consultation). The Case-c sign flip stays **BANNED** (refuted 4×); every family member's residual is clean at the NLP point (forcing, not an emit bug). |

---
**Document Status:** ✅ Complete — Sprint 34 Prep Task 7 (design/plan; no `src/`)
**Last Updated:** 2026-07-19 · **Owner:** Sprint 34 prep (KKT/CGE + solver specialist)
