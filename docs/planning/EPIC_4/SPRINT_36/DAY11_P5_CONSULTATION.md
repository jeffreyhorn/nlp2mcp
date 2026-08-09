# Sprint 36 — Day 11: P5 consultation submission/scoping day (rocket + mine + camcge + fawley)

**Date:** 2026-08-09 · **Branch:** `planning/sprint36-day11-p5` · **Scope:** docs-only (2 submissions + 2 `/tmp`/scaffold experiments; no `src/`, no golden change).

**Outcome: P5 is a bounded submission/scoping day — 0 `src/`, 0 bucket, as designed. Both consultation submissions are confirmed ready (rocket → PATH authors; mine → the primal-degenerate-LP question), and both experiments ran with the honest expected results: the fawley `--force` survey is NEGATIVE (all of homotopy/multistart/optfile leave fawley MS-5 Locally Infeasible — no forcing closes the H-b divergence), and the camcge Walras `/tmp` control confirms MS-4 (the numéraire alone fixes the price-scaling ray but not the row-redundancy nullspace — the two-nullspaces diagnosis, empirically confirmed). All four feed the Sprint-37 consultation / Epic-5; none is an in-sprint bucket.** Verifies the P5 dispositions (Unknowns 5.1–5.4 executed).

Reference: `P5_CONSULTATION_FINALIZATION.md` (Task 8) §1 rocket, §2 mine, §3 camcge, §4 fawley; `CONSULTATION_BUNDLE.md`; `../../../EPIC_5/CGE_DEGENERACY_SCOPING.md` (the camcge fallback).

---

## 1. rocket — PATH-consultation input (submit)

`../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (Status ✅ FINALIZED, renumbered S33→S36 ×11; Task 8 §1 re-confirmed submission-ready). **Action:** the finalized package — the concrete question ("Which PATH option set / regularization schedule / model reformulation forces convergence for this discretized optimal-control MCP?") + the ruled-out-lever survey (§2, 7 MS-5 levers) + the reproducible case + the `--force {homotopy,multistart,optfile}` scaffold reference — is **ready to submit to the PATH authors**. The +1 Solve is contingent on the reply → **Sprint 37** (a consultation-cycle input, not an in-sprint deliverable).

## 2. mine — primal-degenerate-LP question (pose)

`../SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` (Task 8 §2). **Action:** pose the question — *"how should a square MCP represent a primal-degenerate LP boundary, when the warm KKT point is not MCP-reconcilable by any emit reformulation because the shadow price lives entirely in a constraint dual with no complementary bound?"* Carries the S34 value-invariance proof ("no relabeling of the dual can create the missing +16000 — the scalar system is invariant under relabeling") and the standing `x.up=inf` BAN. The only non-invariant lever is an LP-side reformulation (out of emit scope) → **0 in-sprint bucket**; the question feeds the Sprint-37 consultation.

## 3. camcge — Walras `/tmp` MS-1 control → MS-4 (Epic-5, per-model-numéraire fallback)

**Ran (demo, 641 rows — Task 8 §3.2 confirmed demo-reachable):**
- **Baseline (cold MCP):** MODEL STATUS **4 Infeasible**, with a **uniform Walras residual** `INFES = 0.20224` across every `stat_cd` row (the S1∧S2∧S3 rank-deficiency signature — the redundant market's dual is unpinned).
- **Numéraire control** (pin `p("ag-subsist") = 1`, the price-scaling ray): **STILL MODEL STATUS 4 Infeasible.**

⇒ **The numéraire alone does NOT reach MS-1** — empirically confirming the S35 DAY8 **two-nullspaces** diagnosis: the numéraire fixes the *price-scaling ray*, but the **row-redundancy nullspace** (redundant by Walras' law → MS-4 even at the correct primal) is untouched. The full three-part dual-consistent Walras redefinition (keep every market-clearing row + the consumption-weighted numéraire `sum(i$cles(i), cles(i)·(p(i)−pd0(i)))=0` + **redefine the redundant market's dual via Walras' law**) — the row-redundancy dual redefinition being the hard part — is the **Epic-5 gate**, expected MS-4 (3+ sprints of variants all stayed MS-4). **Fallback (the deliverable):** the per-model-numéraire Epic-5 declaration (`../../../EPIC_5/CGE_DEGENERACY_SCOPING.md`) + the detector + the residual-singularity characterization. **0 in-sprint bucket** (camcge → Epic 5).

## 4. fawley — `--force` survey → NEGATIVE (H-b not forceable)

**Ran** (`--nlp-presolve --force <mode>`, GAMS 54.2.1):

| `--force` | MODEL STATUS | obj | reaches LP opt 2899.25? |
|---|---|---|---|
| none | 5 Locally Infeasible | 6862.02 | no |
| homotopy | 5 Locally Infeasible | 5277.11 | no |
| multistart | 5 Locally Infeasible | 6001.39 | no |
| optfile | 5 Locally Infeasible | 5112.68 | no |

⇒ **No forcing strategy closes the H-b divergence** — every mode stays **MS-5 Locally Infeasible**, none reaching the LP optimum 2899.25. **On the objective numbers:** at a *locally-infeasible* (MS-5) termination the objective is just where PATH gave up, not a stable quantity — so these Day-11 runs' values (5113–6862) differ from the **S35-documented H-b baseline of 4399.557** (`CONSULTATION_BUNDLE.md` §3, a separate prior measurement); they are not the same run. **The invariant across all of them is MS-5** (locally infeasible, not the LP optimum) — which is the result that matters here. This confirms fawley's H-b diagnosis (Task 4 §5): the `stat_trans(tr-2)` residual is the **emit-correct non-emit divergence** — the MCP is correctly emitted but PATH cannot reach the LP optimum from the warm start, and the current `--force` scaffold (μ-continuation / perturbed-restart / proximal-optfile) does not force it. **0 in-sprint bucket**; the +Solve hands to a Sprint-37 consultation (a stronger continuation / a reformulation), NOT a `stat_bq` emit fix.

## 5. P5 is a submission/scoping day

All four tracks are **control-confirmed not-an-in-sprint-bucket** and ship **no `src/`**:
- [x] **rocket** — finalized input ready to submit to the PATH authors (→ Sprint 37).
- [x] **mine** — the primal-degenerate-LP question posed (0 bucket; LP-side reformulation out of emit scope).
- [x] **camcge** — Walras `/tmp` control ran → MS-4; numéraire-alone insufficient (two-nullspaces confirmed); the full Walras redefinition = Epic-5; per-model-numéraire fallback.
- [x] **fawley** — `--force` survey ran → NEGATIVE (no force closes H-b); +Solve → Sprint 37.

**P5's product is submissions + scoping decisions, not code.** The rocket reply + the camcge Epic-5 gate + the fawley forcing question feed the **Sprint-37 consultation** cycle.

## 6. Go / No-Go

**Done — clean.** 0 `src/`, 0 golden change, 0 bucket (all four are consultation/Epic-5, as designed). `src/` byte-identical to `main`; DB byte-unchanged; genuine floor **75** / Solve 108 / Match 93 / Translate 135 unchanged. The two experiments produced their honest expected results (fawley un-forceable; camcge MS-4 with numéraire-alone insufficient), sharpening the Sprint-37 hand-offs. `modelstat`-assert / `x.up=inf`-BAN / Case-c-BAN disciplines held.

---

**Document Status:** ✅ Complete — Sprint 36 Day 11 (P5 consultation submission/scoping; 0 src / 0 bucket; rocket+mine ready, camcge MS-4, fawley un-forceable → Sprint 37 / Epic 5)
**Last Updated:** 2026-08-09 · **Owner:** Sprint 36 Execution Team
