# Sprint 35 — Day 8 (P5): camcge Epic-5 gate + Sprint-36 bundle

**Day:** 8 (Priority 5 — camcge Epic-5 `/tmp` gate + the Sprint-36 hand-off bundle) · **Date:** 2026-08-03 · **Owner:** Sprint 35 execution
**Branch:** `planning/sprint35-day8-p5-epic5-sprint36` · **Scope:** docs-only. **0 in-sprint bucket, no `src/`.** P5 is the sprint's explicitly non-KPI priority.

---

## A. camcge Epic-5 gate — DESIGN-SPECIFIED, expected MS-4 → per-model-numéraire Epic-5 fallback

**Disposition: Epic-5-deferred (0 in-sprint bucket).** camcge (#1330) is `model_infeasible`, **MS-4 at iteration 0** — a **Walras rank-deficiency** at the *correct* primal (omega **191.7346**), not a `stat_mps` bug (the S32 step-1 `nu_mps_fx = mps.m` transfer, PR #1553 on `main`, already made `stat_mps` Case-a). Two nullspaces (`EPIC_5/CGE_DEGENERACY_SCOPING.md`): the **price-scaling** ray (fixed by a numéraire) and the **row-redundancy** nullspace (one market-clearing row is redundant by Walras' law → MS-4 even at the correct primal — the piece a numéraire alone does not fix).

**The Epic-5 `/tmp` MS-1 gate is DESIGN-SPECIFIED, not run this sprint:**
- The full three-part redefinition (keep every market-clearing row + the consumption-weighted numéraire `sum(i$cles(i), cles(i)*(p(i)-pd0(i)))=0` + the Walras-law dual redefinition) is a genuinely deeper MCP-research prototype (~5–8 h `/tmp` + ~4–6 h CGE-aware `src/` preprocessing), gated on reaching **MS-1 @ 191.7346 on the dual side** (`modelstat` asserted; the four INFES rows gdp/depreq/hhsaveq/gruse cleared).
- **Expected outcome MS-4** (a-priori): the price-pin variant reaches the correct primal but stays MS-4, and 3+ sprints of variants (price-pin, single-dual-pin, drop-row @ 299) all stayed MS-4. An unexpected MS-1 would promote to a +Solve — a-priori refuted by the banked evidence.
- **Locally unrunnable regardless:** `kkt_residual.py camcge.gms` exceeds the 2-min cap (large CGE), and camcge's MCP exceeds the local GAMS-demo 1000-row solve limit — so the `/tmp` MS-1 prototype is an Epic-5 licensed-testbed step, not a Day-8 solve.

**Fallback (the deliverable, so non-MS-1 is not a failure): the per-model-numéraire Epic-5 declaration** (`EPIC_5/CGE_DEGENERACY_SCOPING.md` §3–§5) + the residual-singularity characterization (INFES on gdp/depreq/hhsaveq/gruse) + the detector + step-1 stability. **camcge is explicitly excluded from the Sprint-35 Solve target.**

**Detector scope re-confirmed live (from the committed DB — no solve needed):** the S1∧S2∧S3 degeneracy detector fires **only** on camcge:

| Model | outcome | MS | detector |
|---|---|---|---|
| **camcge** | model_infeasible | **4** | **FIRES** (Walras rank-deficiency) |
| irscge / lrgcge / moncge / stdcge | model_optimal_presolve (match) | 1 | pass-through (cold MS-1) |

S3 (the false-positive guard: cold-MCP-singular-at-iter-0) holds — only camcge is MS-4; the four siblings pass through at cold MS-1. The S34 P4 bound-transfer touched no sibling golden (none among the 11 P4-regenerated), so the detector inputs are unaffected. Step-1 (`nu_mps_fx = mps.m`) stays Case-a (the numéraire adds `numeraire` + the `cles(i)·nu_numeraire` cross-term in `stat_p`; it does not touch `stat_mps`).

## B. Sprint-36 hand-off bundle (rocket + mine + fawley)

Assembled `docs/planning/EPIC_4/SPRINT_36/CONSULTATION_BUNDLE.md` — three de-risked non-convex/degenerate tracks that share one shape (**emit correct at the reference point; blocker is a solver/forcing/reformulation question, not an emit bug**), bundled into one coherent Sprint-36 package (Task 9):

- **rocket (#1462):** the PATH consultation. The FINALIZED input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`) was **renumbered this task** — 11 target-consultation labels retargeted **Sprint 33 → Sprint 36** (the consultation kept slipping S33→S34→S35, all banked hand-offs; the technical content is current, only the sprint-number labels were stale; the "Sprint 32 Day 9" authoring metadata is preserved). Case-c re-confirmed live (Task 9). The sign flip stays BANNED.
- **mine (#1443):** the primal-degenerate-LP question (Task 6, REPLAN'd in prep — the whole keying/pairing space is value-invariant; the only lever is an out-of-scope LP reformulation). Four-times-carried.
- **fawley (#1111/#1112):** the H-b `--force` survey (Task 8 — the emit-correct `stat_bq` residual is closable but the MCP stays MS-5 @ 4399.557 vs LP 2899.25; the divergence is the non-emit `stat_trans(tr-2)` residual). The +Solve is out of P3's correctness-only scope.

## Outcome

**0 in-sprint bucket, as expected** (P5 is the non-KPI priority). camcge stays `model_infeasible` (Epic-5-deferred); rocket/mine/fawley stay `model_infeasible` (Sprint-36 hand-offs). No `src/`; no `--resolve-changed` impact. The firm product is the packaged Epic-5 recipe + detector + the coherent Sprint-36 consultation bundle (renumbered rocket + mine + fawley).

**Next (Day 9):** P3 fawley constraint-index-diagonal correction — optional, correctness-only, 0 bucket (H-b), must not displace anything; its +Solve is this bundle's fawley item.

---

**Document Status:** ✅ Complete — Sprint 35 Day 8 (P5: camcge Epic-5-deferred + Sprint-36 bundle)
**Last Updated:** 2026-08-03
**Owner:** Sprint 35 Execution Team
