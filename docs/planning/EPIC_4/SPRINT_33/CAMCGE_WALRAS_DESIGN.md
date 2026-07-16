# camcge #1330 — Dual-Consistent Walras Numéraire + Degeneracy-Detector Scope: Design

**Prep Task:** 6 (Priority 4 / Epic 5) · **Date:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/CGE specialist)
**Status:** design complete — **Epic-5-deferred.** Step 1 (the scalar-`fx` `nu_mps_fx` transfer) landed on main (S32, PR #1553). Step 2 (the dual-consistent Walras numéraire) is genuinely deeper MCP research: the banked Sprint-32 Day-5 control showed **step-1-first + numéraire reaches omega 191.7346 (correct primal) but MS-4** — camcge stays `model_infeasible` in Sprint 33; the numéraire falls to the per-model-declaration Epic-5 fallback.

> **PR24 discipline:** validated read-only (harness/DB re-confirm + the banked `/tmp` numéraire prototype); no `src/` change. The dual-consistent redefinition's `/tmp`-to-MS-1 prototype is the **Epic-5** gate.

---

## 1. Day-0 re-confirm

- **Base camcge state (step 1 landed).** camcge is `model_infeasible` (**MS-4 Infeasible at iteration 0** — the singular-Jacobian / inherent-Walras signature; `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` §1). Step 1 (PR #1553) converted the `stat_mps` CASE_B residual to Case-a (a general emit fix); the residual MS-4 is the Walras rank-deficiency, independent of `stat_mps`. (The `kkt_residual.py camcge.gms` cold-MCP re-run exceeds a 2-min cap — camcge is a large CGE model; the MS-4 base is the well-banked state.)
- **The banked numéraire prototype (Sprint-32 Day-5, `CAMCGE_WALRAS_REPLAN.md`).** step 1 + the consumption-weighted numéraire (`numeraire.. sum(i$cles(i), cles(i)·(p(i)−pd0(i))) =E= 0` + the `cles(i)·nu_numeraire` cross-term in `stat_p`, every market-clearing row kept) → **omega 191.7346 (the correct allocation ✅) but MCP MS-4 ❌**, with residual INFES on the accounting identities `gdp` (131.96), `depreq` (131.96), `hhsaveq` (97.26), `gruse` (43.97) — the **primal-correct / basis-singular** signature. Byte-identical GAMSlib model + emit; stands.
- **S1∧S2∧S3 detector cohort (re-confirmed on the current DB).** cold/final MCP MS across the CGE cohort:

  | Model | outcome | MS | S1∧S2 (structural) | **S3** (cold MCP singular @ iter 0) | detector |
  |---|---|---|---|---|---|
  | **camcge** | model_infeasible | **4** | ✓ | ✓ **fires** | **FLAGS** |
  | irscge | model_optimal_presolve | 1 | ✓ | ✗ (cold MS-1, Day-7) | pass-through |
  | lrgcge | model_optimal_presolve | 1 | ✓ | ✗ | pass-through |
  | moncge | model_optimal_presolve | 1 | ✓ | ✗ | pass-through |
  | stdcge | model_optimal_presolve | 1 | ✓ | ✗ | pass-through |

  The detector flags **only camcge** (Unknown 4.2). The Sprint-31 Day-7 cold-MCP test (banked, `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §4) established the *cold* MS status directly: irscge/lrgcge/moncge/stdcge all cold **MS-1**, camcge cold **MS-4**; the DB re-confirms camcge MS-4 vs the four siblings MS-1.

## 2. The dual-consistent Walras numéraire — design (Unknown 4.1)

**Why the numéraire alone is insufficient.** The numéraire removes the price-scaling nullspace (CGE conditions are homogeneous of degree 0 in prices — equilibria form a ray `{λ·p*}`), delivering the right primal (191.7346). But the **residual Walras rank-deficiency remains**: the goods-clearing rows `equil(i)` + the labor-clearing `lmequil(lc)` are linearly dependent given household budget balance (Walras' law: `∑_i p_i·equil_i + w·lmequil ≡ B`), so one market-clearing row is redundant → a 1-D nullspace in the KKT Jacobian → MS-4 even at the correct primal.

**The dual-consistent redefinition** (`CAMCGE_STAT_MPS_WALRAS_DESIGN.md` §3):
1. **Keep every market-clearing row** (no orphaned dual — the naïve "drop one row" is primal-correct but *breaks the MCP dual*: the dropped market's multiplier vanishes from the stationarity, the S30 finding).
2. **Fix the consumption-weighted numéraire** (`sum(i$cles(i), cles(i)·p(i)) = sum(i$cles(i), cles(i)·pd0(i))`, since camcge has no `cpi`) — the automatic rule (reproduces the NLP optimum's `p=pd0`, a *selection* not a perturbation).
3. **Redefine the redundant market's dual via Walras' law** — express the redundant market-clearing row's multiplier as the Walras-law combination of the others, so the **reduced system is full-rank while the redundant market's multiplier stays available in the stationarity**. This is the piece the numéraire-only prototype lacks (it removed the price nullspace but not the row-redundancy nullspace).

**Check the dual side, not just the primal** (the Day-11 lesson): the redefinition must be verified against the KKT *dual* (the redundant market's multiplier must equal its economically-correct value, not just leave the primal at 191.7346).

## 3. The degeneracy-detector scope (Unknown 4.2)

The detector must flag **only** camcge — nlp2mcp must not silently redefine a dual on a well-posed model. **S1 ∧ S2 ∧ S3**:
- **S1** — a market-clearing block (goods `equil(i)` + factor `lmequil(lc)`) linearly dependent via budget balance.
- **S2** — no price numéraire fixed (price homogeneity of degree 0).
- **S3** (the false-positive guard) — **the cold MCP is singular at iteration 0 (MS-4)**. A well-posed CGE with a determined closure passes S1∧S2 structurally but has a nonsingular Jacobian → fails S3 → pass-through.

**Cohort precision (§1 table):** camcge fires (cold MS-4); irscge/lrgcge/moncge/stdcge pass-through (cold MS-1). **Pass-through default** = the identity transform (faithful KKT emission); the redefinition applies to the flagged model only.

## 4. The `/tmp` gate + disposition (Unknowns 4.3, 4.4)

**Epic-5 `/tmp` prototype gate:** the FULL dual-consistent redefinition (step 1 + the consumption-weighted numéraire + the Walras-law dual redefinition) → **MS-1 at omega 191.7346** (`modelstat` asserted), with the S1∧S2∧S3 detector flagging only camcge across the five CGE models. **Not run in this docs-only prep** — and the banked evidence is discouraging: the *price-pin* variant (numéraire without the dual redefinition) stayed MS-4, and 3+ sprints of prep (price-pin MS-4, single-dual-pin MS-4, drop-row corrupt @ 299) all failed to reach MS-1. The dual redefinition is "genuinely deeper Epic-5 MCP research, not a same-day hand-transform."

**Disposition (Unknown 4.3): Epic-5-deferred.** camcge stays `model_infeasible` in Sprint 33; the dual-consistent Walras redefinition + the per-model-numéraire declaration are the Epic-5 deliverable (`EPIC_5/CGE_DEGENERACY_SCOPING.md` §3–§5). The +1 Solve defers to Epic 5. The de-risked Epic-5 hand-off: the working numéraire recipe (omega 191.7346), the exact residual-singularity characterization (INFES on `gdp`/`depreq`/`hhsaveq`/`gruse`), the S1∧S2∧S3 detector (flags only camcge), and the confirmation that step-1-first does not change the MS-4 outcome.

**Step-1 stability (Unknown 4.4):** the numéraire adds the `numeraire` equation + the `cles(i)·nu_numeraire` cross-term in `stat_p` — it does **not** touch `stat_mps` (step 1). The banked step-1 + numéraire prototype kept omega 191.7346 (step 1 stable under the numéraire change); the landed `nu_mps_fx = mps.m` transfer stays Case-a.

## 5. Sizing + REPLAN exit

**10–16 h** (Epic-5-domain CGE work, if pursued in an Epic-5 sprint):
- `/tmp` prototype of the full dual-consistent redefinition (keep-every-row + numéraire + Walras-law dual redefinition) + the MS-1/MS-4 discrimination + the dual-side check (~5–8 h) — the Epic-5 Phase-0 gate.
- The CGE-aware preprocessing layer (detect via S1∧S2∧S3, apply the per-model-numéraire declaration + the dual redefinition) — Epic-5 `src/` (~4–6 h) — **only if the `/tmp` prototype reaches MS-1**.
- Detector cohort re-verification (no false-flag on irscge/lrgcge/moncge/stdcge) + determinism (~1–2 h).

**Epic-5-deferral REPLAN exit (the realized outcome):** if the full `/tmp` prototype stays MS-4 (the Walras rank-deficiency is deeper than the dual redefinition too), camcge lands only step 1 (already on main) and the numéraire is the documented per-model-declaration Epic-5 fallback — **no Sprint-33 `src/`**. Given the banked evidence (price-pin MS-4, 3+ sprints of MS-4 variants), this is the **expected disposition**; the design's value is the Epic-5-ready recipe + detector + gate.

## 6. Outcome for the Known Unknowns

| Unknown | Verdict | Finding |
|---|---|---|
| **4.1** | ✅ VERIFIED (design-level) | The per-model-numéraire + dual-consistent Walras redefinition is designed (keep every row + consumption-weighted numéraire + Walras-law dual redefinition, dual side checked). Whether it reaches **MS-1 at 191.7346** is **unproven** — the `/tmp` prototype is the Epic-5 gate; the banked price-pin variant stayed MS-4, so MS-1 is genuinely hard (Epic-5-deep, not a prep or same-day landing). |
| **4.2** | ✅ VERIFIED | The S1∧S2∧S3 detector flags **only camcge**: S3 (cold MCP MS-4 at iter 0) is the false-positive guard; the DB + the banked Day-7 cold-MCP test confirm camcge MS-4 vs irscge/lrgcge/moncge/stdcge cold MS-1 (pass-through). |
| **4.3** | ✅ VERIFIED — **Epic-5-deferred** | The dual-consistent redefinition is deeper MCP research; the banked step-1+numéraire prototype reaches omega 191.7346 but MS-4. camcge stays `model_infeasible` in Sprint 33; the +1 Solve + the per-model-numéraire declaration are Epic-5. |
| **4.4** | ✅ VERIFIED | The numéraire adds the `numeraire` equation + the `cles(i)·nu_numeraire` cross-term in `stat_p`; it does not touch `stat_mps` (step 1). The banked step-1+numéraire prototype kept omega 191.7346 — step 1 (`nu_mps_fx = mps.m`, Case-a) stays correct under the numéraire change. |

---
**Document Created:** 2026-07-16 · **Owner:** Sprint 33 prep (KKT/CGE specialist)
