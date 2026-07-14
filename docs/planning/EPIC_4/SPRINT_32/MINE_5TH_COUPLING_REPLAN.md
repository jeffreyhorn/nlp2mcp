# Sprint 32 Day 1 — mine P1 REPLAN: 5th Coupling Confirmed (control-refuted)

**Date:** 2026-07-14
**Day:** 1 (Priority 1 — mine bound-multiplier 4th site, #1443)
**Outcome:** 🔴 **REPLAN → Sprint 33 deeper head-offset architecture.** No `src/` change.
**Discipline:** the PR24/PR27 `/tmp` control ran **before** the emit change and refuted the banked fix.

---

## 1. What was tested (the banked Day-1 fix)

The `MINE_BOUND_MULTIPLIER_DESIGN.md` fix: replace the presolve bound-multiplier transfer (`src/emit/emit_gams.py:1548–1577`, `piL_x/piU_x = ±x.m`) with the **stationarity-residual `N`-derivation** — `piL_x = max(N,0)`, `piU_x = max(−N,0)`, where `N` = the non-bound part of `stat_x` after the `lam_pr` transfer. The `/tmp` control hand-edited `mine_mcp_presolve.gms`'s two transfer lines to this derivation and ran GAMS (GAMS 53; the embedded NLP solves MS-1 @ profit 17500, so the warm point is the true NLP optimum).

## 2. The control results (three GAMS probes)

| Probe | Result | Reading |
|---|---|---|
| **Direct `stat_x` body** (parameter, no solve) | **max\|stat_x\| = 0.000** (max\|N\| = 32000) | The `N`-derivation closes stationarity **exactly by construction** (`N − max(N,0) + max(−N,0) = 0`). The formula is correct. |
| **MCP solve** (warm-started from the `N`-derivation) | **MODEL STATUS 5 — Locally Infeasible**, profit **22058** (≠ NLP 17500) | PATH cannot solve the MCP from the by-construction-stationary warm point — it walks away to an infeasible point (the Sprint-31 Day-2/3 `22058` signature). |
| **Complementarity check** (at the warm point) | **6 violations:** 3× `piL_x > 0` off the lower bound (`x(1,3,{1,2,3})` = 14500/2000/3000), 3× `piU_x > 0` off the upper bound (`x(3,1,2)`=9000, `x(3,2,1)`=4000, `x(4,1,1)`=11000) | The sign-split bound multiplier is nonzero at rows whose `x` is at the **opposite** bound — the complementarity pairing (`piL_x ⊥ x−lo`, `piU_x ⊥ up−x`) is broken. |
| **Interior-residual check** | **0 interior rows with `N ≠ 0`** (max = 0.000) | The interior stationarity emit is **correct**; the residual is **exclusively** at bound-active rows. |

## 3. Diagnosis — the 5th coupling

At the 6 bound-active rows, `x` sits **at** a bound but the emitted stationarity residual `N` has the sign appropriate for the **opposite** bound — i.e. the KKT gradient points "inward," which would require a **negative** bound multiplier to close `stat_x`. Bound multipliers in the MCP must be **≥ 0**, so **no valid multiplier assignment satisfies both stationarity and complementarity** at these rows. Since `N = 0` at every strictly-interior row, this is not an interior-stationarity defect — it is a **wrong-sign residual in the emitted `stat_x` head-offset cross-term** (`sum(k, lam_pr(k,l,i−li,j−lj)$c − lam_pr(k,l−1,i,j)$c)`) at bound-active rows.

**This is exactly the design's own REPLAN trigger** (`MINE_BOUND_MULTIPLIER_DESIGN.md` §4): *"the sign of `N` contradicts the bound-active status at some row (indicating the emitted `stat_x` cross-term itself is still inconsistent, a genuine 5th site)."* The bound-multiplier warm-start value cannot fix it — the fix must change the emitted `stat_x` **cross-term** at head-offset bound-active rows (a high-blast-radius AD/emit change), which is the **deeper head-offset architecture** the REPLAN defers.

## 4. Disposition

- **REPLAN mine [P1] → Sprint 33** (deeper head-offset bound-active cross-term architecture). **No `src/` change** in Sprint 32 (the `/tmp` control refuted the fix before src — PR24/PR27 working as intended, the 6th consecutive control-first REPLAN across S30–S32).
- **The de-risked hand-off** (banked for Sprint 33): the S31 head-offset IR foundation (`EquationDef.head_domain_offsets` + the Site-2 dual transfer) + this precise 5th-coupling characterization (wrong-sign `N` at 6 bound-active rows; the interior emit is correct) + the `N`-derivation design (still the right bound-multiplier *given* a corrected cross-term).
- **mine stays `model_infeasible`.** Solve ≥ 109 now rests on **camcge [P3] alone** among the two firm movers (a miss unless a P6 candidate — cpack/fawley — converts); mine's +1 Solve + conditional +1 genuine floor become a Sprint-33 carry.
- **Budget reallocation (Task 9):** the P1 Days 1–3 budget (~14–20 h) frees to **P6** (the cpack offset-alias generalization + fawley second-index Case-b — the firmest remaining genuine-floor/+Solve levers) + **P7**. The Day-2/Day-3 mine slots pull P6 forward.

## 5. Evidence

GAMS 53 runs on the hand-edited `/tmp` `mine_mcp_presolve.gms` (all 0 compile errors): `mine_direct.gms` (stat_x body = 0), `mine_Nderiv_solve.gms` (MCP MS-5 @ 22058), `mine_compcheck.gms` (6 complementarity violations), `mine_interior.gms` (0 interior N≠0). The embedded NLP `$include mine.gms` solves MS-1 @ 17500 in every run (the warm point is the true NLP optimum). Anchor `4cbf8bff`; `kkt_residual.py mine.gms` = CASE_B `stat_x(3,1,1)` rel 2.37 (Day-0 `DAY0_TRACES.md`).

---

**Document Created:** 2026-07-14
**Owner:** Sprint 32 execution (KKT/emit specialist)
