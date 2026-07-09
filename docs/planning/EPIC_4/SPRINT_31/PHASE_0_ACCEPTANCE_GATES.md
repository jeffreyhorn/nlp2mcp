# Sprint 31 Phase-0 Acceptance Gates (PR20 + PR24 + PR27)

**Task:** Sprint 31 Prep Task 6
**Date:** 2026-07-09
**Owner:** Sprint planning
**Scope:** docs-only — consolidates the per-track PROCEED/REPLAN gates for the six emit-touching Sprint-31 priorities. The authoritative per-issue gate lives in each `docs/issues/ISSUE_<N>_*.md` `## Phase 0: Acceptance Gate` section (refreshed to the Sprint-31 disposition by this task); this document is the single-page index + the control-experiment discipline for the sprint.

---

## 0. The standing discipline (why these gates exist)

Sprint 30 **refuted five banked diagnoses** via control experiments *before* any high-blast-radius `src/` change (the obj-grad sign flip 3×, the Class-B `stat_pz` "coefficient bug" which was really case-normalization, and the camcge Walras drop-row which broke the dual). The Phase-0 gate is the single most load-bearing discipline the sprint carries. Two rules bind every gate below:

- **PR24 — the banked fix surface is a Day-0-re-confirm hypothesis, not fact.** Each gate frames its fix surface as a hypothesis and requires a Day-0 trace + a `Traced Fix-Surface (Day-0)` `file:line` before any `src/` commit (CONTRIBUTING.md §"Phase 0 Acceptance Gates").
- **PR24/PR27 — control-experiment-before-implement.** For every emit-touching track, the fix must be shown to reach the target (MS-1 / the NLP optimum / a byte-stable golden) in a `/tmp` control experiment *before* the `src/` change. The `kkt_residual.py` Case-(a/b/c) verdict is the standard instrument (Case-b ⇒ emit fix; Case-c ⇒ warm-start/forcing, not an emit fix).

**Check the dual side** (the Sprint-30 camcge lesson): any structural transform that drops/adds rows must be verified against the KKT *dual*, not just the primal solution set.

---

## 1. Per-track gates (P1–P6)

### P1 — mine head-offset IR plumbing + shared 3-site helper (#1443)

- **Disposition:** PROCEED (foundational IR change + the shared 3-site helper).
- **PROCEED precondition (Phase 1 gate):** the **round-trip unit reproduction** (`tests/fixtures/head_offset_ir_roundtrip.gms`, asserting `head_domain_offsets[1] == IndexOffset('l', Const(1.0), False)`) must be **green before any emit change** — the IR plumbing is a field addition on `EquationDef` (mirroring `declaration_domain`), verified in isolation first.
- **PROCEED precondition (Phase 2 gate):** the **cold-INFES-by-direction histogram** driven to zero — `kkt_residual.py` residual → 0 warm, then cold **MS-1** with `x ≤ x.up = 1` (no `x → 4e10`) across **all four** k-directions (nw/ne/se/sw; baseline ~4.07e10). mine is a convex LP ⇒ no Case-c escape.
- **REPLAN exit:** a **4th site** (bound-complementarity `comp_lo_x`/`comp_up_x` persisting after the `comp_pr` fix) → a Sprint-32 head-offset-Phase-3 workstream; the IR plumbing + helper still land as reusable foundation.
- **Verify:** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/mine.gms`
- **Design + unknowns:** `HEAD_OFFSET_IR_PLUMBING_DESIGN.md`; Unknowns 1.1/1.2/1.3/1.4. Fix surface: `_add_indexed_jacobian_terms`/`stat_x` (`stationarity.py:5767`) + `_emit_nlp_presolve` (`emit_gams.py:1354`) + the `comp_pr` head-var (`equations.py`/`emit_gams.py`).

### P2 — offset-alias general-alias core #1111/#1112 (polygon, #1143)

- **Disposition:** PROCEED (coupled objective-successor + distance-Jacobian second-index, tightly gated).
- **PROCEED precondition:** the **4-term recipe re-confirmed** on the current tree (✅ done, Task 4 — harness byte-identical to the Day-0 fingerprint: CASE_B, `stat_theta(i12)` rel 0.492, dual-transfer CONSISTENT) **+ #1110 orthogonality** (the multi-pattern correction is a single scalar diagonal-vs-off-diagonal delta keyed on *pattern* multiplicity, vs the second-index *whole sum* keyed on *constraint-index-position* multiplicity). Land the objective half (`_build_indexed_gradient_term`, `stationarity.py:2864`) **and** the distance second-index half (`_add_indexed_jacobian_terms`, `stationarity.py:5767`) **together** — neither alone matches (objective-alone regresses polygon to MS-5).
- **Completion gate:** `shape8_offset_alias_successor` drops its `strict=True` xfail **+** polygon warm-matches 0.780 **+** the CGE multi-pattern GO list is byte-stable (`--resolve-changed`).
- **REPLAN exit:** the var-at-two-indices gate **leaks** into the CGE multi-pattern cohort → the full #1111/#1112 alias-aware-differentiation AD-engine core = a **Sprint-32 filing**; polygon's genuine-floor +1 becomes conditional.
- **Verify:** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/polygon.gms`
- **Design + unknowns:** `OFFSET_ALIAS_JACOBIAN_DESIGN.md`; Unknowns 2.1/2.2/2.3/2.4. himmel16 is a **non-convex scope guard** (sign-fix refuted, `ISSUE_1146`) — not a P2 target.

### P3 — camcge dual-consistent Walras transform (#1330 → Epic 5)

- **Disposition:** PROCEED-conditional (the dual-consistent redefinition; **PR24 control-experiment gate**).
- **PROCEED precondition (check the dual side):** the **dual-consistent multiplier redefinition** — keep every market-clearing row (no orphaned dual) + a consumption-weighted numéraire (on `cles(i)`/`pd0(i)`) + redefine the redundant market's dual via Walras' law — must reach **MS-1 at omega 191.7346** in a hand-edited `/tmp` MCP **before** the `src/` change. (The Day-11 price-pin alone reaches 191.735 but stays **MS-4**; the naive drop-row orphans a needed dual → omega 299. The `/tmp` prototype proves the *dual* is repaired, not just the primal.)
- **Detector precision:** the **S1∧S2∧S3** degeneracy detector must flag **only camcge** across irscge/lrgcge/moncge/stdcge — **S3 (cold-MCP-singular-at-iter-0) is the false-positive guard** (a well-posed model with S1∧S2 but a determined closure fails S3). The transform is detected, never silently applied.
- **REPLAN exit:** the `/tmp` prototype **cannot** reach MS-1 (the dual redundancy is deeper than a single Walras relation) → a **per-model-numéraire-declaration Epic-5 item**; camcge stays `model_infeasible`.
- **Verify:** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/camcge.gms`
- **Design + unknowns:** `CAMCGE_DUAL_CONSISTENT_DESIGN.md`; Unknowns 3.1/3.2/3.3/3.4. Emit-correct at the NLP optimum (Case-c structural singularity, not an emit bug — the transform is a CGE-aware preprocessing layer, `CGE_DEGENERACY_SCOPING.md` §4).

### P4 — sarf symbolic runtime-guard cross-term emit (#1385)

- **Disposition:** PROCEED (the dedicated builder-pipeline-aware symbolic-emit workstream).
- **PROCEED precondition (tractability gate):** the symbolic re-emit must be **O(constraints), not O(instances)** — sarf has **1,152** Cartesian instances (`tbal(g,t)$taskposs`, `equipb1/equipb2`), and the whole point of the Option-1 short-circuit was to avoid enumerating them. Time `sarf_mcp.gms` against the translate budget (must stay well under the >180s Option-1 timeout); the re-emitted `stat_task` must match the **banked 6-guarded-term hand-derivation** with **no set-name-literal multiplier indices** (the Sprint-26-Day-4 `nu_slack("srn")` failure mode); the re-emit + `J_gᵀ·lam` cross-terms land **atomically** (a re-emit without cross-terms = an inconsistent MCP); the regenerated golden is byte-stable.
- **REPLAN exit:** the parametric re-emit **re-triggers the translate timeout** (O(instances) after all) → re-scope the parametric emit (documented re-scoping); +Translate deferred.
- **Verify:** `time .venv/bin/python -m src.cli data/gamslib/raw/sarf.gms --emit-mcp -o /tmp/sarf_mcp.gms` (O(constraints) `stat_task` row count, sub-timeout).
- **Unknowns:** 4.1 (the 2-D `_is_blowup_dynamic_subset_equation` extension + the parametric `stat_task` builder, no set-name literals), 4.2 (O(constraints) budget), 4.3 (atomicity). **Fix surface pinned by Task 9** (`src/ad/index_mapping.py` + `src/kkt/stationarity.py`, Day-0 hypothesis).

### P5 — cold-convex obj-grad residue (hhfair `stat_u` / CGE `stat_xp`, #1236)

- **Disposition:** PROCEED-conditional (the **ν_objective reduction**; **PR24/PR27 control-experiment gate**).
- **PROCEED precondition (control-before-implement):** the objective-gradient reduction **through the objective-defining-equation multiplier (ν_objective)** must reach the **NLP optimum on hhfair** (the cleanest instance, `stat_u` rel 2.0) in a `/tmp` control experiment **before** the (high-blast-radius) objective-gradient `src/` change. **THE SIGN FLIP IS BANNED** — it was control-refuted **three times** in Sprint 30 (hhfair 72.147 → 22.144, *worse*, away from the NLP ref 87.159). Then confirm the same reduction converts the CGE cluster (irscge/lrgcge/moncge `stat_xp` rel ~0.06 after the Day-5 case-normalization fix) to Case-a.
- **REPLAN exit:** the ν_objective reduction does **not** reach the NLP optimum → hhfair is **genuine Case-c non-convexity** → a documented non-convexity finding for the objective-defining-intermediate-variable family; no `src/` change.
- **Verify:** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/hhfair.gms`
- **Unknowns:** 5.1 (ν_objective reduction reaches the NLP optimum, sign flip banned), 5.2 (CGE-cluster generalization → Case-a), 5.3/5.4. **Fix surface pinned by Task 9** (the ν_objective reduction in `src/kkt/stationarity.py` / `src/ad/gradient.py`, NOT the sign flip).

### P6 — rocket non-convex forcing → PATH-consultation input (#1462)

- **Disposition:** PROCEED-conditional (exhaust the emittable levers; author the PATH-consultation input).
- **PROCEED precondition (PR27 residual-clean-before-forcing):** re-confirm the emit residual is **clean at the NLP point (Case-c)** *before* any forcing attempt — this keeps rocket a *forcing* problem, not a latent emit bug (a Case-b residual would mean fix the emit first, not force). Then exhaust the remaining **emittable-GAMS levers** (the `1/ht²`,`1/m²` division-by-variable Jacobian reformulation; scaled/relaxed continuation schedules via the landed `--force` scaffold; INFES 477 → 382 best but never converges).
- **REPLAN exit:** no emittable lever crosses (intrinsic non-convergence confirmed) → the deliverable is the **finalized PATH-consultation input** for the renumbered Sprint 32 (the concrete question: which option set / regularization schedule / reformulation converges this division-by-variable optimal-control MCP); rocket's +1 Solve is a conditional hand-off.
- **Verify:** `.venv/bin/python scripts/diagnostics/kkt_residual.py data/gamslib/raw/rocket.gms` (expect Case-c — clean emit, non-convex).
- **Unknowns:** 6.1 (emittable-lever exhaustion), 6.2 (residual-clean-at-NLP-point Case-c before forcing), 6.3 (Jacobian reformulation). The `--force` scaffold landed Sprint 30; **fix surface / lever set pinned by Task 9** + `NONCONVEX_FORCING_SURVEY.md` §4.

---

## 2. Gate summary table

| Track | Model | Disposition | PROCEED precondition (control-before-src) | REPLAN exit |
|---|---|---|---|---|
| P1 | mine (#1443) | PROCEED | round-trip fixture green → cold-INFES histogram → all 4 dirs → 0, cold MS-1 | 4th bound-complementarity site → Sprint 32 |
| P2 | polygon (#1143) | PROCEED | 4-term recipe re-confirmed (✅) + #1110 orthogonality; obj + distance halves together; `shape8` enable + warm-match 0.780 + CGE byte-stable | gate leaks → #1111/#1112 AD-engine filing, Sprint 32 |
| P3 | camcge (#1330) | PROCEED-conditional | dual-consistent redefinition → MS-1 @ 191.7346 on `/tmp` **before** src; S1∧S2∧S3 flags camcge only | `/tmp` can't reach MS-1 → per-model-numéraire fallback (Epic 5) |
| P4 | sarf (#1385) | PROCEED | O(constraints) emit timed vs translate budget; `stat_task` = banked derivation, no set-name literals; atomic; golden byte-stable | timeout re-trigger → re-scope |
| P5 | hhfair/CGE (#1236) | PROCEED-conditional | ν_objective reduction → NLP optimum on hhfair **before** src; **sign flip BANNED** (refuted 3×) | genuine Case-c → documented non-convexity |
| P6 | rocket (#1462) | PROCEED-conditional | residual clean at NLP point (Case-c) **before** forcing; exhaust emittable levers | intrinsic non-convergence → Sprint-32 PATH-consultation input |

**Cross-cutting:** every gate cites `kkt_residual.py` (PR27) as the Case-(a/b/c) verdict engine; every emit-touching PR must also pass the golden-staleness check (PR26) + the `--resolve-changed` checkpoint re-solve; each per-issue `## Phase 0: Acceptance Gate` section (ISSUE_{1443,1143,1330,1385,1236} + #1462) carries the authoritative 4-subsection gate refreshed to this disposition.
