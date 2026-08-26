# Sprint 36 — Consultation / Forcing Bundle (rocket + mine + fawley)

**Assembled:** Sprint 35 Day 8 (2026-08-03) · **Owner:** Sprint 35 execution (P5 slot) → Sprint 36
**Scope:** docs-only hand-off. Three de-risked, banked non-convex/degenerate tracks that share a common shape — **the emit is correct at the reference point; the blocker is a solver/forcing/reformulation question, not an emit bug** — bundled into one coherent Sprint-36 package instead of three loose ends (Task 9's recommendation). None ships `src/` in Sprint 35; each is a conditional +Solve deferred to Sprint 36.

---

## Why bundle these three

Each was control-confirmed across multiple sprints as **not an emit defect** (the fix-the-emit-first path is ruled out), and each hands a *specific, self-contained question* to Sprint 36:

| Track | Issue | Bucket now | The Sprint-36 question | Banked source |
|---|---|---|---|---|
| **rocket** | #1462 | `model_infeasible` (Case-c) | a **PATH consultation** — a recommended option-set/schedule for a non-convex objective-defining-intermediate-variable model whose every emittable lever (PATH options, μ-continuation, multistart, division-by-var reformulation) stays MS-5 | `SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` (renumbered → Sprint 36) |
| **mine** | #1443 | `model_infeasible` (`x.m=0`-degenerate) | a **primal-degenerate-LP question** — the warm KKT point is not MCP-reconcilable by *any* emit-side dual architecture (the whole keying/pairing space is value-invariant, S34 proved H_dual value-invariant); the only non-invariant lever is an LP-side reformulation, out of emit scope | `SPRINT_35/MINE_DUAL_ARCHITECTURE_DESIGN.md` (Task 6) |
| **fawley** | #1111/#1112 | `model_infeasible` (H-b) | a **`--force` survey** — the emit-correct `stat_bq` residual is closable, but the MCP stays MS-5 @ 4399.557 vs the LP optimum 2899.25 (the `stat_trans(tr-2)` residual is the emit-correct non-emit divergence); the +Solve needs a forcing/continuation survey, not a `stat_bq` fix | `SPRINT_35/FAWLEY_DIAGONAL_DESIGN.md` (Task 8) |

**Common discipline carried in:** `modelstat` asserted before every objective read; **the Case-c objective-gradient sign flip stays BANNED** (control-refuted 4×, S30–S31); `x.up=inf` BANNED (mine, the S31 measurement error). Each track's residual/signature is re-confirmable via `kkt_residual.py` (PR27).

## 1. rocket (#1462) — PATH consultation

**Disposition:** `model_infeasible`, **CASE_C_OBJDEF** — a *forcing* problem, re-confirmed live (Task 9: `stat_ht(h0)` rel 1.00 / `stat_step` 0.497 / `stat_ht(h50)` 0.438, dual transfer CONSISTENT closure 1.53e-10 — byte-for-byte the banked signature). Clean at the NLP point ⇒ not a latent emit bug.

**Sprint-36 action:** submit the FINALIZED, renumbered input (`SPRINT_32/ROCKET_PATH_CONSULTATION_INPUT.md` §3 — the concrete question + the ruled-out-lever survey §2 + a reproducible case) to the PATH authors; the recommended option-set plugs into the existing `--force homotopy` scaffold (`--nlp-presolve --force homotopy` → `proximal_perturbation` μ-continuation + `mcp_model.optfile = 1`). +1 Solve is **conditional on the consultation**.

## 2. mine (#1443) — primal-degenerate-LP question

**Disposition:** `model_infeasible`, `x.m=0`-degenerate boundary — **REPLAN'd in prep** (Task 6). No emit-side dual architecture can supply the +16000 the degenerate boundary requires; the whole keying/pairing candidate space is value-invariant (S34 proved H_dual value-invariant on the cold solve; the cross-term is algebraically correct S33; the `N`-derivation refuted S32 — mine is **four-times-carried**).

**Sprint-36 action:** pose the primal-degenerate-LP question — *how does a warm KKT point of a primal-degenerate LP reconcile into an MCP when the degenerate boundary is not emit-reachable?* The S31 head-offset IR foundation (`EquationDef.head_domain_offsets`) + the value-invariance findings hand off cleanly. No emit lever remains; the candidate is an LP-side reformulation (out of emit scope). **0 in-sprint bucket.**

## 3. fawley (#1111/#1112) — `--force` survey

**Disposition:** `model_infeasible`, **H-b** (Task 8, re-confirmed + strengthened live: `CASE_B` / `stat_bq` rel 0.973 with `stat_trans(tr-2)` rel 1.00 the harness max — the emit-correct non-emit residual dominates). The constraint-index-diagonal correction (a *correctness-only* landing, 0 bucket) is optional (Sprint-35 Day 9); its +Solve is **out of scope** and lives here.

**Sprint-36 action:** a `--force`/continuation survey for the H-b divergence — the MCP stays MS-5 @ 4399.557 while the LP optimum is 2899.25, and the divergence is non-emit (the `stat_trans(tr-2)` residual). The genuine-floor +1 is contingent on a cold match that H-b precludes without forcing. Survey the `--force` strategies (homotopy / multistart / optfile) against fawley.

---

## Hand-off checklist (all banked; no Sprint-35 `src/`)

- [x] rocket input renumbered → Sprint 36 (11 target-labels; authoring metadata preserved)
- [x] mine primal-degenerate-LP question specified (Task 6 design + the value-invariance findings)
- [x] fawley H-b `--force` survey scoped (Task 8 design + the live re-measurement)
- [x] The Case-c sign flip + `x.up=inf` BANs restated
- [x] **fawley `--force` survey — DONE (Sprint 36).** Result: **NEGATIVE** (homotopy/multistart/optfile all leave MS-5).
- [x] **Submit rocket to the PATH authors — SENT 2026-08-26** (Sprint 38 Day 12). Email to `ferris@cs.wisc.edu`, `steve@gams.com`, `sdirkse@gams.com`. Sent package: **`docs/planning/EPIC_4/SPRINT_38/ROCKET_CONSULTATION_EXTERNAL.md`** + **`data/gamslib/mcp/rocket_mcp_presolve.gms`** — *not* the prepared §5 package; the internal input doc was replaced by an externally-scoped extract and the NLP source by the generated MCP. Recorded on **#1462**. Follow-up due **2026-09-09**.
- [x] **Pose the mine LP-degeneracy question — POSED 2026-08-26**, riding along with the rocket send as planned. Reframed around the signature `mine` **shares with `agreste`** (both verified-convex LPs; MCPs MS-5 Locally Infeasible after 10,662 / 9,734 iterations) rather than posed per-model. Recorded on **#1443**.

> **Split 2026-08-18 (Sprint 38 Prep Task 7).** This was one checkbox covering three actions, **one of which was already complete** — part of why it went un-ticked across S33–S37.

---

## Related Sprint-36 banked work (NOT a consultation — an emit fix)

A fourth track was surfaced Sprint-35 Day 11 but is **categorically different** from the three above (whose emit is correct and whose blocker is a solver/forcing question): **markov is a genuine cold-emit bug** with a concrete +1 payoff, so it belongs to a Sprint-36 *emit-fix* effort, not this consultation bundle.

- **markov** — `stat_z` diagonal-Kronecker emit bug (the `#1110` multi-pattern split was never emitted). KKT-residual control = `CASE_B`, `max|stat_z|` rel 13.3; markov is a *methodology* match today, and a correct cold emit ⇒ `CASE_A` ⇒ cold `model_optimal` ⇒ **genuine floor 75→76 (+1)**. Deep repair of the shared `_add_indexed_jacobian_terms` / `_multi_pattern_correction` machinery, high-blast-radius across the matching 2-D cohort (fawley Day-9 leak precedent) → dedicated effort. Full diagnosis + implementer-ready hand-off: `SPRINT_35/DAY11_MARKOV_DIAGONAL_LEVER.md`. This is the **only bucket-relevant lever found in Sprint 35** (all deep tracks refuted/banked as non-emit).

---

**Document Status:** ✅ Assembled — Sprint 35 Day 8 (P5 slot); markov emit-fix cross-ref added Day 11 · handed to Sprint 36
**Last Updated:** 2026-08-04
**Owner:** Sprint 35 Execution Team → Sprint 36
