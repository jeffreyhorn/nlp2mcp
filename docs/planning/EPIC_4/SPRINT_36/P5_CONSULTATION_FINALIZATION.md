# Sprint 36 — P5 Consultation Bundle Finalization + camcge Epic-5 Gate Scoping (Prep Task 8)

**Date:** 2026-08-07 · **Owner:** Sprint 36 execution team · **Branch:** `planning/sprint36-task8` · **Scope:** docs/analysis-only (readiness read-through + DB/size probes; no `src/` change).

**Outcome: P5 is a bounded submission/scoping day, not open research.** The rocket PATH-consultation input is submission-ready (all four components present, renumbered S33→S36 ×11, FINALIZED, reproducer live on `main`); the mine primal-degenerate-LP question is precisely framed with the S34 value-invariance proof + the `x.up=inf` BAN; the camcge S1∧S2∧S3 detector still fires only on camcge (DB-confirmed, byte-unchanged); and — correcting a stale `DAY8` claim — the camcge Walras `/tmp` MS-1 gate is **locally reachable on the demo** (the generated MCP measures **641 rows < the 1000-row limit** and solves to MS-4), so the Epic-5 gate needs no licensed testbed. **P5 ships no `src/`** — it submits rocket, poses the mine question, scopes the camcge Epic-5 gate, and cross-references the fawley `--force` survey — feeding the Sprint-37 consultation. Verifies Unknowns 5.1, 5.2, 5.3, 5.4.

Reference: `CONSULTATION_BUNDLE.md` (the umbrella bundle), `../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md`, `../SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md`, `../SPRINT_35/DAY8_P5_CAMCGE_SPRINT36.md`, `../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`, `FAWLEY_DISCRIMINATOR_DESIGN.md` (Task 4).

---

## 1. rocket — PATH-consultation input submission-ready (Unknown 5.1)

`../SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (Status: ✅ **FINALIZED**, Sprint 32 Day 9) contains all four submission components:

| component | location | status |
|---|---|---|
| concrete PATH question | §3 — "Which PATH option set / regularization schedule / model reformulation forces convergence for this discretized optimal-control MCP?" | ✅ present |
| ruled-out-lever survey | §2 (7-row table, all MS-5) + §4 (remaining-lever sweep) | ✅ present |
| reproducible case | §3 — a runnable `python -m src.cli data/gamslib/raw/rocket.gms … --nlp-presolve` block | ✅ present |
| `--force` scaffold reference | §3 + §5 item 1 ("`--force {homotopy, multistart, optfile}` scaffold, landed Sprint 30") | ✅ present |

- **Renumbering S33→S36 ×11 confirmed:** the banner records "the target-consultation labels were retargeted Sprint 33 → Sprint 36 (11 refs)"; the forward-target labels are all S36 (title "(Sprint-36 Hand-Off)", §3 "(feeds Sprint 36)", §5 "Sprint-36 hand-off note", §6 "PROCEED to the Sprint-36 hand-off"). The residual S32/S33/S35 mentions are **intentional provenance/history** (authoring metadata "Sprint 32 Day 9", the "S33→S34→S35 all deferred it" slip chain, the "NOT a Sprint-32 gain" caveat) — not missed renumbers.
- **Reproducer live on `main`:** the `--force` scaffold is present in `src/cli.py:207` (`homotopy`/`multistart`/`optfile` modes; `--nlp-presolve --force homotopy` → `proximal_perturbation` μ-continuation + `mcp_model.optfile = 1`). The banked Case-c signature (`stat_ht(h0)` rel 1.00 / `stat_step` 0.497 / dual transfer CONSISTENT 1.53e-10) is byte-stable (`src/` unchanged over the relevant paths since the anchor).

**Verdict:** submission-ready. **Sprint-36 P5 action = submit** (not re-author). ✅

## 2. mine — primal-degenerate-LP question finalized (Unknown 5.2)

`../SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` (Status: ✅ Complete, Sprint 35 Prep Task 6 REPLAN) frames the question precisely and carries both required guards:

- **Primal-degenerate-LP framing (explicit):** "mine is a **primal-degenerate LP whose warm KKT point is not MCP-reconcilable by any emit reformulation**"; the pointed consultation form (§6): "**how should a square MCP represent a primal-degenerate LP boundary?**" — *"the shadow price lives entirely in a constraint dual with no complementary bound."*
- **S34 value-invariance proof cited:** "re-anchoring the precedence dual's complementarity — `comp_pr` + `lam_pr` + `stat_x` *together* — to any label produces the identical scalar MCP … any candidate that only moves where the dual lives is value-invariant by construction"; "**No relabeling of the dual can create the missing +16000**, because the scalar system is invariant under relabeling (S34)."
- **`x.up=inf` BAN restated (twice):** "`modelstat` asserted; `x.up=inf` BANNED (the S31 measurement-error lesson)"; "(Standing BANs) `x.up=inf` as a measurement device is **BANNED** (the S31 error)."

**Verdict:** precise, guarded, actionable. **Sprint-36 P5 action = pose the LP-degeneracy question** (the only non-invariant lever is an LP-side reformulation, out of emit scope). **0 in-sprint bucket.** ✅

## 3. camcge — Epic-5 `/tmp` Walras MS-1 gate scope (Unknowns 5.3, 5.4)

### 3.1 The detector still fires only on camcge (Unknown 5.4)

Re-confirmed from the committed DB (`gamslib_status.json`, **byte-unchanged since the anchor `78ceaead`** — no re-solve could have shifted the cohort):

| model | solve bucket | modelstat | S1∧S2∧S3 |
|---|---|---|---|
| **camcge** | `model_infeasible` | **MS 4** (Walras rank-deficiency @ omega **191.7346**) | **FIRES** |
| irscge / lrgcge / moncge / stdcge | `model_optimal_presolve` (match) | MS 1 | pass-through |

Only camcge shows the cold MS-4 signature; the four CGE siblings cold-solve MS-1 and match. The S3 false-positive guard (cold-MCP-singular-at-iter-0) holds. ✅ fires only on camcge.

### 3.2 The `/tmp` Walras MS-1 gate is LOCALLY reachable on the demo (Unknown 5.3) — correcting `DAY8`

**Measured this task:** the committed camcge MCP golden generates **BLOCKS OF EQUATIONS 85 / SINGLE EQUATIONS 641** and **SINGLE VARIABLES 641** under GAMS 54.2.1 demo, and PATH runs to **SOLVER STATUS 1 (Normal Completion) / MODEL STATUS 4 (Infeasible)** — the exact cold MS-4 signature — with "*This solver runs with a demo license.*" **641 rows < the 1000-row demo limit.**

→ **This supersedes the `DAY8` claim that "camcge's MCP exceeds the local GAMS-demo 1000-row solve limit."** camcge has a small *symbolic* count (34 eqns) but — unlike turkey (3,866 generated rows) — its *generated* MCP stays at 641 rows, comfortably demo-solvable. So the camcge Walras `/tmp` MS-1 gate control is **runnable locally on the demo** — it is **NOT** a licensed-testbed step (contrast turkey/Task 7). (`DAY8`'s separate note that `kkt_residual.py camcge.gms` exceeds the 2-min harness cap may still hold — that is the AD/emit *analysis* harness, not the solve — but the solve-size blocker it cited is stale.)

### 3.3 The Epic-5 gate + fallback

- **The gate (locally attemptable):** the full three-part dual-consistent Walras redefinition — keep every market-clearing row + the consumption-weighted numéraire (`sum(i$cles(i), cles(i)*(p(i)-pd0(i)))=0`) + redefine the redundant market's dual via Walras' law — targeting **MS-1 @ 191.7346 on the dual side** with `modelstat` asserted and the four INFES rows (gdp/depreq/hhsaveq/gruse) cleared. Now a **demo `/tmp` control** (641 rows), not a testbed gate.
- **Two nullspaces:** the price-scaling ray (fixed by the numéraire) and the row-redundancy nullspace (redundant by Walras' law → MS-4 even at the correct primal; a numéraire alone does not fix it — this is why the banked price-pin variant reaches the correct primal but stays MS-4).
- **Fallback (if MS-1 unreachable):** the **per-model-numéraire Epic-5 declaration** (`../../EPIC_5/CGE_DEGENERACY_SCOPING.md` §3–§5) + the residual-singularity characterization + the detector (§3.1) + the S32 step-1 stability. Reaching the correct primal at MS-4 with the fallback declaration is "not a failure" — it is the Epic-5 deliverable.

**Verdict:** the Epic-5 gate is scoped and **locally reachable to attempt** (5.3 assumption holds — reachability of MS-1 itself remains the open Epic-5 experiment, now demo-runnable rather than testbed-gated). ✅

## 4. fawley — `--force` survey cross-reference (bundle §3 / Task 4)

fawley (#1111/#1112) is the third bundled track: `model_infeasible`, **H-b**, emit-correct (`CASE_B` / `stat_bq` rel 0.973, the `stat_trans(tr-2)` residual the emit-correct non-emit divergence; MCP stays MS-5 @ 4399.557 vs the LP optimum 2899.25). Its +Solve needs a **`--force`/continuation survey**, not a `stat_bq` fix. The banked design is `../SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md`; **Task 4's `FAWLEY_DISCRIMINATOR_DESIGN.md`** additionally proved the fawley constraint-index-diagonal correction is **disjoint from markov** (fires only when the summed constraint index is absent from the derivative coefficient), so a fawley correctness landing cannot leak onto the markov cohort. The `--force` survey (homotopy / multistart / optfile against fawley) is the P5 fawley action — **cross-referenced here, owned by the bundle §3**, shared with the markov emit-fix effort's `--force` scaffold.

## 5. P5 is a submission/scoping day — feeding the Sprint-37 consultation

All three consultation tracks are **control-confirmed not-an-emit-defect** and hand a self-contained question to a solver/reformulation authority — **none ships `src/` in Sprint 36:**

- [ ] **rocket** — submit the FINALIZED input (§1) to the PATH authors; +1 Solve conditional on the consultation reply → **Sprint 37**.
- [ ] **mine** — pose the primal-degenerate-LP question (§2); 0 in-sprint bucket; the candidate lever is an LP-side reformulation (out of emit scope).
- [ ] **camcge** — run the Walras `/tmp` MS-1 gate as a demo control (§3.2); if MS-1, an Epic-5 `src/` CGE-aware preprocessing follow-up; else the per-model-numéraire declaration (§3.3).
- [ ] **fawley** — run the `--force` survey (§4); the genuine-floor +1 is contingent on a forced cold match H-b precludes unforced.

**P5's product is submissions + a scoping decision, not an emit fix.** The rocket reply + the camcge gate result feed the **Sprint-37 consultation** cycle; the markov emit-fix (the only bucket-relevant lever, `../SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md` + Task 3's `MARKOV_OFFDIAGONAL_DESIGN.md`) is a **separate** emit-fix effort, not part of this consultation bundle.

## 6. Go / No-Go

**GO — P5 is bounded.** rocket submission-ready (5.1 ✅); mine question precise + guarded (5.2 ✅); camcge detector fires only camcge (5.4 ✅) and the Walras gate is locally demo-reachable (5.3 ✅, correcting the stale `DAY8` demo-limit claim). No `src/` in P5; no external blocker except the rocket PATH reply (Sprint 37) and the camcge MS-1 experiment (Epic-5, now demo-runnable).

**REPLAN triggers:** the camcge Walras `/tmp` control stays MS-4 (→ the per-model-numéraire fallback, §3.3, the expected outcome after 3+ sprints of MS-4 variants); the fawley `--force` survey finds no forcing schedule that closes the H-b divergence (→ fawley stays `model_infeasible`, 0 bucket); the rocket PATH reply recommends no emittable option-set (→ rocket stays Case-c). None blocks the sprint — each is a conditional +Solve, honestly contingent.

---

**Document Status:** ✅ Complete — Sprint 36 Prep Task 8 (P5 consultation finalization + camcge Epic-5 gate scoping; GO, P5 bounded)
**Last Updated:** 2026-08-07
**Owner:** Sprint 36 Execution Team
