# Sprint 35 — camcge Dual-Consistent Walras Design (Epic 5) + rocket PATH-Consultation Submission Plan (Priority 5)

**Prep Task:** 9 (Medium) · **Date:** 2026-07-24 · **Owner:** Sprint 35 prep (CGE/MCP + consultation)
**Day-0 code anchor:** `78ceaead` (S34 close) · **Measurement tree:** `8d15a8dd` (`main` at the S35 prep Task-8 merge) — docs-only ahead of the anchor, `src/`/`scripts/` byte-identical
**Scope:** docs/design only — specifies the camcge dual-consistent Walras redefinition as an Epic-5 `/tmp` MS-1 gate + the per-model-numéraire fallback, re-confirms the detector scope + rocket Case-c live, and produces the **Sprint-36** consultation-submission plan (bundling rocket + the mine [Task 6] and fawley [Task 8] hand-offs). **No `src/` change.**

> **Disposition: camcge Epic-5-deferred (0 in-sprint bucket, MS-1 a-priori hard); rocket a Sprint-36 hand-off (conditional +Solve). P5 is the sprint's explicitly non-KPI priority.** This task's added value beyond the banked S33/S34 designs: (1) the **renumbering correction** — the FINALIZED rocket input references "**Sprint 33**" (its S32 authoring number, *doubly* stale after S33→S35→S36), not "Sprint 35" as assumed; both it and the S34 plan retarget to **Sprint 36**; (2) the **Sprint-36 bundle** — mine (Task 6, the primal-degenerate-LP question) and fawley (Task 8, the H-b `--force` survey) join rocket, so Sprint 36 receives one coherent consultation/forcing package, not three loose ends; (3) live re-confirmation of the detector scope and rocket Case-c on the current tree.

---

## Executive summary

**camcge (#1330 → Epic 5):** cold **MS-4** (model_infeasible) at the correct primal (omega **191.7346**) — a Walras rank-deficiency, not a `stat_mps` bug (S32 step-1 fixed that). The full dual-consistent redefinition (keep every market-clearing row + consumption-weighted numéraire + Walras-law dual redefinition) is designed and its Epic-5 `/tmp` MS-1 gate specified — but MS-1 is **a-priori hard** (the banked price-pin variant reaches the correct primal but stays MS-4, and 3+ sprints of variants all stayed MS-4), so camcge is **Epic-5-deferred** with the per-model-numéraire declaration as the documented fallback. **0 in-sprint bucket** (expected).

**rocket (#1462 → Sprint 36):** Case-c re-confirmed **live** (`kkt_residual.py rocket.gms` → CASE_C_OBJDEF, `stat_ht(h0)` rel 1.00 / raw −4.56, `stat_step` 0.497, `stat_ht(h50)` 0.438, dual transfer CONSISTENT closure 1.53e-10 — byte-for-byte the banked signature). A **forcing** problem, not an emit bug; the objective-gradient sign flip stays **BANNED** (control-refuted 4×). The FINALIZED input is submission-ready; it submits to the **Sprint-36** consultation.

**Detector scope re-confirmed:** the S1∧S2∧S3 degeneracy detector fires **only** on camcge (cold MS-4); the four CGE siblings irscge/lrgcge/moncge/stdcge stay cold MS-1 (DB-confirmed). The S34 P4 bound-transfer did **not** touch any sibling golden (none among the 11 P4-regenerated goldens), so the detector inputs are unaffected.

---

## §1. camcge — the full dual-consistent Walras redefinition (Unknown 5.1)

### 1.1 The problem (re-confirmed)

camcge is `model_infeasible`, **MS-4 Infeasible at iteration 0** — the singular-Jacobian / inherent-Walras signature (`EPIC_5/CGE_DEGENERACY_SCOPING.md`). Step 1 (the S32 `nu_mps_fx = mps.m` scalar-`fx` transfer, PR #1553, on `main`) already converted the `stat_mps` CASE_B residual to Case-a; the residual MS-4 is the **Walras rank-deficiency**, independent of `stat_mps`. (The `kkt_residual.py camcge.gms` cold run exceeds a 2-min cap — a large CGE model — so the DB MS-4 is the banked base; Day-0 bucket re-confirmed from the committed DB this task: camcge `model_infeasible` MS-4, the four siblings MS-1.)

The **two nullspaces** (`CGE_DEGENERACY_SCOPING.md`):
- **Price-scaling nullspace** — CGE conditions are homogeneous of degree 0 in prices (equilibria form a ray `{λ·p*}`). Removed by a **numéraire**.
- **Row-redundancy nullspace** — the goods-clearing rows `equil(i)` + the labor-clearing `lmequil(lc)` are linearly dependent given household budget balance (Walras' law: `∑_i p_i·equil_i + w·lmequil ≡ B`), so **one market-clearing row is redundant** → a 1-D nullspace in the KKT Jacobian → MS-4 *even at the correct primal*. This is the piece a numéraire alone does **not** fix.

### 1.2 The three-part redefinition (emittable GAMS, MCP square)

1. **Keep every market-clearing row** — do not drop the redundant row (the S32 "drop-row" variant corrupted the primal to 299; a dropped row loses its multiplier from the stationarity).
2. **Add the consumption-weighted numéraire** — `numeraire.. sum(i$cles(i), cles(i)*(p(i) - pd0(i))) =E= 0` (camcge has no `cpi`, so the consumption-weighted rule is the automatic selection that reproduces the NLP optimum's `p = pd0` — a *selection*, not a perturbation), plus the `cles(i)*nu_numeraire` cross-term in `stat_p`. This removes the **price-scaling** nullspace → the correct primal (omega 191.7346).
3. **Redefine the redundant market's dual via Walras' law** — express the redundant market-clearing row's multiplier as the Walras-law combination of the others, so the **reduced system is full-rank while the redundant market's multiplier stays available in the stationarity**. This removes the **row-redundancy** nullspace — the piece the numéraire-only (price-pin) prototype lacks.

**Square-MCP requirement:** the numéraire adds one equation (`numeraire`) and one multiplier (`nu_numeraire`); the dual redefinition re-expresses (does not remove) the redundant multiplier — so the variable/equation counts stay balanced. **Check the dual side, not just the primal** (the S30 camcge lesson): the redefinition must be verified against the KKT *dual* (the redundant market's multiplier must equal its economically-correct value, not merely leave the primal at 191.7346).

### 1.3 The Epic-5 `/tmp` MS-1 gate (DESIGN-SPECIFIED — not built in prep)

**Gate:** the FULL redefinition (step 1 + consumption-weighted numéraire + Walras-law dual redefinition) → **MODEL STATUS 1 at omega 191.7346**, `modelstat` asserted, with the four INFES accounting-identity rows **cleared** (`gdp` 131.96, `depreq` 131.96, `hhsaveq` 97.26, `gruse` 43.97 — the primal-correct / basis-singular signature of the price-pin variant), and the S1∧S2∧S3 detector still flagging only camcge across the five CGE models.

**Why MS-1 is a-priori hard (the banked evidence):** the **price-pin** variant (numéraire *without* the dual redefinition) reaches the correct primal (191.7346) but stays **MS-4** with those four INFES rows; and 3+ sprints of variants — price-pin MS-4, single-dual-pin MS-4, drop-row corrupt @ 299 — all failed to reach MS-1. So the `/tmp` full-redefinition prototype's **expected outcome is MS-4**; an *unexpected* MS-1 would promote to a +Solve, but that is a-priori refuted by the banked evidence. **This is DESIGN-SPECIFIED** — the `/tmp` prototype is the Epic-5 Phase-0 gate, not a prep or same-day landing (the dual redefinition is genuinely deeper MCP research: ~5–8 h prototype + ~4–6 h CGE-aware preprocessing `src/`, Epic-5 only if the prototype reaches MS-1).

### 1.4 The acceptable fallback finding (so non-MS-1 is a deliverable, not a failure)

**Fallback: the per-model-numéraire Epic-5 declaration.** If the `/tmp` prototype stays MS-4 (the row-redundancy nullspace is deeper than the dual redefinition), the deliverable is the **documented per-model-numéraire declaration** (`EPIC_5/CGE_DEGENERACY_SCOPING.md` §3–§5) + the exact residual-singularity characterization (INFES on gdp/depreq/hhsaveq/gruse) + the S1∧S2∧S3 detector + step-1 stability. camcge stays `model_infeasible`; the +1 Solve is an Epic-5 deliverable, **not** an in-sprint commitment. **camcge is explicitly excluded from the Sprint-35 Solve target.**

---

## §2. Degeneracy-detector scope (Unknown 5.2)

The S1∧S2∧S3 detector fires **only** on camcge:
- **S1** — a market-clearing row is redundant (Walras' law).
- **S2** — no price numéraire fixed (price homogeneity of degree 0).
- **S3** — the cold MCP is singular at iteration 0 (**MS-4**) — the false-positive guard.

**Cohort (re-confirmed live from the committed DB, this task):**

| Model | cold MCP | MS | detector |
|---|---|---|---|
| **camcge** | model_infeasible | **4** | **fires** (the Walras rank-deficiency; NLP obj 191.7346) |
| irscge | model_optimal_presolve (match) | 1 | pass-through |
| lrgcge | model_optimal_presolve (match) | 1 | pass-through |
| moncge | model_optimal_presolve (match) | 1 | pass-through |
| stdcge | model_optimal_presolve (match) | 1 | pass-through |

**S3 (the false-positive guard) holds:** camcge is cold-MCP-singular at iter 0 (MS-4) while the four siblings pass through at cold MS-1 — so the detector flags only camcge. **The S34 P4 bound-transfer did NOT alter any sibling's inputs** — none of irscge/lrgcge/moncge/stdcge is among the 11 P4-regenerated goldens (`git diff --name-only 750803b2..78ceaead -- data/gamslib/mcp/` — the four siblings are absent), so the detector scope is unaffected by P4. Pass-through is the identity transform (faithful KKT emission); the redefinition applies to the flagged model only.

**Step-1 stability (banked, re-confirmed):** the numéraire adds the `numeraire` equation + the `cles(i)·nu_numeraire` cross-term in `stat_p` — it does **not** touch `stat_mps` (step 1). The landed `nu_mps_fx = mps.m` transfer stays Case-a.

---

## §3. rocket — Case-c re-confirmed live + the Sprint-36 submission (Unknown 5.3)

### 3.1 Case-c re-confirmed live (this task)

`kkt_residual.py rocket.gms` on the current tree (2026-07-24):

```
verdict: CASE_C_OBJDEF  — objective-defining-intermediate-variable non-convexity (NOT an emit fix — the sign flip is BANNED)
dual transfer: CONSISTENT (max comp infeas 0, max equality residual 1.53e-10 raw)
max-residual row: stat_ht(h0)  rel 1.00 (raw -4.56)
  stat_ht(h0) 1.00 · stat_step 0.497 · stat_ht(h50) 0.438 · stat_v(h0) 0.038
```

**Byte-for-byte the banked signature** (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` §1). The residual concentrates on the **boundary/terminal rows** of the discretized optimal-control problem (`stat_ht(h0)` initial altitude, `stat_ht(h50)` terminal, `stat_step` time-step) — which move with the warm-start value — while the interior rows are near tolerance and the dual transfer is CONSISTENT. **rocket is a genuine forcing problem, not a latent emit bug.**

### 3.2 The submission bundle

The FINALIZED input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) is submission-ready — a self-contained artifact:
- **The concrete question:** which PATH option-set / regularization schedule forces convergence for the discretized optimal-control MCP (the division-by-variable reformulation ruled out — S31 Day 11 showed non-convergence is intrinsic to the structure, not the `1/m`,`1/ht²` Jacobian conditioning).
- **The ruled-out-lever survey:** PATH options (best INFES 382, MS-5), μ-continuation (MS-5 every step), multistart (superseded), division-by-variable reformulation (MS-5) — all exhausted.
- **The two-command reproducer:** `python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve; gams rocket_mcp_presolve.gms` → MS-5.
- **The `--force {homotopy,multistart,optfile}` scaffold** (landed S30) — the mechanism a recommended option-set/schedule plugs into.

**Recipients:** Michael Ferris / Steven Dirkse (the PATH authors; External Dependencies). **Response tracking:** a tracking doc created at submission (question → response → lever tried → outcome), per the Sprint-36 consultation plan (`PROJECT_PLAN.md` §"Sprint 36" — "Submit and Follow Up").

### 3.3 ⚠️ The renumbering hazard — corrected (richer than the task assumed)

The current consultation sprint is **Sprint 36** (`PROJECT_PLAN.md:1769` `# Sprint 36 … PATH Author Consultation & Solution Forcing`). The banked docs carry **two different stale numbers** from the renumbering chain (each sprint-insertion pushed the consultation forward):

| Doc | Stale reference | Why | Retarget to |
|---|---|---|---|
| `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (the FINALIZED input) | **"Sprint 33"** — **11 occurrences** (header "Sprint-33 Hand-Off", "feeds the Sprint-33 consultation", "§5. Sprint-33 hand-off note", …) | authored at S32 for the *then*-Sprint-33 consultation; **doubly stale** (S33 → S35 via the S34 insertion → S36 via the S35 insertion) | **Sprint 36** |
| `SPRINT_34/CAMCGE_ROCKET_PLAN.md` | **"Sprint 35"** (the §5.2 submission mechanism, the KPI notes) | authored at S34, when the consultation was renumbered to Sprint 35 | **Sprint 36** |

> **The task prompt assumed the banked input has stale "Sprint 35" references; it does not — it has "Sprint 33" (older).** At submission time, **all** sprint-destination references in **both** docs must be updated to **Sprint 36**. The technical content of the input (the question, the survey, the reproducer) is current and correct — only the sprint-number labels are stale. This is flagged so the Sprint-36 submission does not carry a confusing "Sprint 33"/"Sprint 35" destination.

### 3.4 The Sprint-36 consultation/forcing bundle (cross-task hand-offs)

rocket does **not** go to Sprint 36 alone. Two other Sprint-35 tracks REPLAN'd/deferred into the same Sprint-36 consultation/forcing sprint, and this plan bundles them so Sprint 36 receives one coherent package:

- **mine (P1, Task 6)** — REPLAN'd in prep as a **primal-degenerate LP whose warm KKT point is not MCP-reconcilable by emit**. It is a **second concrete PATH-consultation question** (distinct from rocket's Case-c forcing): *how should a square MCP represent a primal-degenerate LP boundary whose shadow price lives entirely in a constraint dual with no complementary bound?* Hand-off artifact: `MINE_DUAL_ARCHITECTURE_DESIGN.md` + `SPRINT_34/DAY1_PROGRESS_NOTES.md`.
- **fawley (P3, Task 8)** — its +Solve is **H-b** (non-emit divergence, MS-5 @ 4399.557 vs LP opt 2899.25). It is a **`--force` survey item** for the Sprint-36 solution-forcing work (which `--force` lever, if any, crosses fawley's MS-5). Hand-off artifact: `FAWLEY_DIAGONAL_DESIGN.md` §7.

So Sprint 36 receives: **two consultation questions** (rocket Case-c forcing; mine primal-degenerate LP) + **one forcing-survey item** (fawley H-b) — plus the Case-c family (§4) as documented-non-convex forcing candidates.

---

## §4. Case-c family + the standing BAN (Unknown 6.3)

The **objective-gradient sign flip is BANNED** — control-refuted 4× (S30–S31); no re-litigation. The Case-c family stays **documented non-convex** under the `case_c_objdef` classifier (`scripts/diagnostics/kkt_residual.py:466`, `reclassify_objdef_case_c:621`), with clean residuals at the NLP point (a forcing problem, not an emit bug):

| Model | Day-0 bucket | Case-c note |
|---|---|---|
| rocket | model_infeasible MS-5 | CASE_C_OBJDEF (re-confirmed live, §3.1) — boundary rows, forcing |
| cesam | model_infeasible MS-4 | objective-defining-intermediate-variable non-convexity |
| lnts | model_infeasible MS-4 | same |
| hhfair | model_optimal MS-1 (**mismatch**) | Case-c: solves but mismatches at a spurious local KKT point |
| irscge/lrgcge/moncge/stdcge | model_optimal_presolve (match) | the CGE cluster — methodology-match (presolve warm-start), documented non-convex |

None is an emit fix; all are forcing/consultation candidates for Sprint 36. No emit change is attempted in Sprint 35.

---

## §5. Known Unknowns verified by this task

- **Unknown 5.1** — ✅ **VERIFIED (design); the MS-1 result is DESIGN-SPECIFIED (Epic-5-deferred).** The full dual-consistent Walras redefinition is specified as emittable GAMS with the MCP square (keep every row + consumption-weighted numéraire + Walras-law dual redefinition, dual side checked). The Epic-5 `/tmp` gate is **MS-1 at 191.7346** (distinguished from the price-pin variant's correct-primal-at-**MS-4** result, with the four INFES rows tracked), `modelstat` asserted — **not built in prep** (the `/tmp` prototype is the Epic-5 Phase-0 gate; the banked evidence — price-pin MS-4, 3+ sprints of MS-4 variants — makes MS-1 a-priori hard). The **per-model-numéraire fallback** is defined as an acceptable Epic-5 finding. camcge is **explicitly excluded from the in-sprint Solve commitment**.
- **Unknown 5.2** — ✅ **VERIFIED.** The S1∧S2∧S3 detector fires **only** on camcge (cold MS-4); the four CGE siblings stay cold MS-1 (DB-confirmed live). The S34 P4 bound-transfer did **not** touch any sibling golden (none among the 11 P4-regenerated goldens), so the detector inputs are unaffected. S3 (the cold-singular guard) holds; pass-through is the identity transform.
- **Unknown 5.3** — ✅ **VERIFIED (with the renumbering corrected).** rocket Case-c re-confirmed **live** (CASE_C_OBJDEF, `stat_ht(h0)` 1.00 / `stat_step` 0.497 / dual CONSISTENT 1.53e-10 — byte-identical to the banked signature). The FINALIZED input is submission-ready; the submission plan (recipients, artifact bundle, response tracking) targets **Sprint 36**. **The renumbering hazard is richer than assumed:** the input carries **11 "Sprint 33"** references (doubly stale, S33→S35→S36), and the S34 plan carries "Sprint 35" — both retarget to **Sprint 36** at submission. mine (Task 6) + fawley (Task 8) are bundled into the Sprint-36 consultation/forcing package.
- **Unknown 6.3** — ✅ **VERIFIED.** The Case-c family (rocket/cesam/lnts/hhfair + the CGE cluster) stays documented non-convex under `case_c_objdef`, residuals clean at the NLP point (forcing, not emit). The objective-gradient **sign flip is BANNED** (control-refuted 4×), restated with no re-litigation path.

**Handed to Task 10 (Phase-0 gate):** the camcge Epic-5 `/tmp` MS-1 gate (with the MS-4 fallback documented, `modelstat` asserted); rocket has no solve gate (a hand-off). **Handed to Task 11 (projection):** P5 = **0 in-sprint bucket / 0 genuine floor** (camcge Epic-5-deferred, rocket Sprint-36-conditional). **Handed to Task 12 (schedule):** P5 needs a small in-sprint slot for the camcge `/tmp` Epic-5 gate + the rocket/mine/fawley Sprint-36 submission-bundle packaging (with the renumbering fixes); no bucket expected.

---

**Document Status:** ✅ Complete — Sprint 35 Prep Task 9
**Last Updated:** 2026-07-24
**Owner:** Sprint 35 Planning Team
