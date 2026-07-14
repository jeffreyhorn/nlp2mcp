# Sprint 32 Phase-0 Acceptance Gates (PR20 + PR24 + PR27)

**Created:** 2026-07-13
**Prep Task:** 8 (the primary scope-correctness gate)
**Scope:** docs-only — consolidates the per-track PROCEED/REPLAN gates for the five Sprint-32 priorities (P1 mine, P2 sarf, P3 camcge, P4 rocket, P5 hhfair/CGE). The authoritative per-track detail lives in each Task-3–7 design doc (`MINE_BOUND_MULTIPLIER_DESIGN.md`, `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md`, `CAMCGE_STAT_MPS_WALRAS_DESIGN.md`, `ROCKET_PATH_CONSULTATION_INPUT.md`, `CASE_C_CLASSIFIER_DESIGN.md`) + each `docs/issues/ISSUE_<N>_*.md`; this document is the single-page index + the control-experiment discipline for the sprint.

---

## 0. The standing discipline (why these gates exist)

- **PR20 — hand-derived KKT before `src/`.** Each emit-touching change starts from a hand-derived / harness-verified target shape, not a guess.
- **PR24 — the banked fix surface is a Day-0-re-confirm hypothesis, not fact.** Sprint 31 REPLAN'd all five deep tracks after a control or harness re-diagnosis refuted the original premise (the mine "MS-1 17500" measurement error; the camcge CASE_B-not-Walras verdict; the sarf 369K-not-1,152 finding; the P5 inert reduction; the rocket exhausted survey). Each gate frames its fix surface as a hypothesis re-confirmed at Day 0 in the Task-3–7 designs.
- **PR27 — control-experiment before implement.** Every high-blast-radius change is gated on a `kkt_residual.py` verdict and/or a `/tmp` control that must pass *before* the `src/` commit. The harness Case-(a/b/c) verdict is the standard instrument.
- **Assert `modelstat` before reading an objective** (the Sprint-31 Day-2 measurement-error lesson): every warm/cold solve step asserts `mcp_model.modelstat` before any objective read; `x.up=inf` is a structurally invalid experiment (BANNED).

Every emit-touching PR must also pass the **golden-staleness check (PR26)** + the **`--resolve-changed` checkpoint re-solve** (no changed golden moves backward vs the Day-0 anchor `4cbf8bff`).

---

## 1. Per-track gates (P1–P5)

### P1 — mine 4th Bound-Complementarity Site (#1443)

- **Disposition:** PROCEED (the stationarity-consistent bound-multiplier derivation; a single local presolve-transfer fix).
- **PROCEED precondition (PR27 warm→cold, `modelstat` asserted):** replace the `--nlp-presolve` bound-multiplier transfer (`src/emit/emit_gams.py:1548–1577`, currently `piL_x/piU_x = ±x.m`) with the **stationarity-residual derivation** `piL_x = max(N, 0)`, `piU_x = max(−N, 0)` (where `N` = the non-bound part of `stat_x` after the `lam_pr` transfer). Then re-run `kkt_residual.py data/gamslib/raw/mine.gms` → **warm residual → 0 (Case-a)** → presolve **MS-1** (the +1 Solve) → cold MS-1 (stretch). The generic `x.m`-transfer block must be gated to the head-offset-coupled case (or `--resolve-changed`-verified) so the non-mine presolve cohort stays byte-stable; the head-offset IR foundation (Site-2 helper + `EquationDef.head_domain_offsets`) is untouched (16 guard tests green).
- **REPLAN exit:** the `N`-derivation does **not** close the warm residual (a fresh residual persists at the NLP optimum, or the sign of `N` contradicts the bound-active status) = a genuine **5th coupling** → a Sprint-33 deeper head-offset architecture; the head-offset IR foundation + this bound-multiplier design remain the banked hand-off; budget → P6/P7 (Task 9).
- **Cross-links:** KNOWN_UNKNOWNS Category 1 (Unknowns 1.1–1.4) · `MINE_BOUND_MULTIPLIER_DESIGN.md` · `docs/issues/ISSUE_1443_mine-head-domain-offset-mcp-infeasible.md`.

### P2 — sarf 4-D `task` Stationarity Sparsification (#1385)

- **Disposition:** PROCEED (the O(active) symbolic `stat_task` emit + the 2-D constraint gate, atomically).
- **PROCEED precondition (PR20 tractability + atomicity):** the emit must be **O(active-instances = 398), not O(369,024 Cartesian)** — emit **one** symbolic guarded `stat_task(g,t,m,n)$taskposs(g,t)` equation (the banked 7-term derivation) + `task.fx(g,t,m,n)$(not (taskposs(g,t) and tech(g,m,n))) = 0`. **Time `sarf` translate** against the budget (must be seconds — srpchase's 1-D analogue is 6.56s; the failure is >180s). The `stat_task` matches the banked derivation with **symbolic** multiplier indices — **no set-name-literal indices** (the Sprint-26 `nu_slack("srn")` failure, commit `243fe578`; verify via `grep -E 'nu_[[:alnum:]_]+\("|lam_[[:alnum:]_]+\("' sarf_mcp.gms` = empty). The re-landed 2-D constraint gate + the 4-D sparsification + the `J_gᵀ·lam` cross-terms + the `task.fx` fixing land **atomically** (a re-emit without cross-terms = an inconsistent MCP); the regenerated golden is byte-stable; `--resolve-changed` GO (sarf is the only changed golden). Sites `src/ad/index_mapping.py` + `src/kkt/stationarity.py`.
- **REPLAN exit:** the parametric emit **re-triggers the translate timeout** (unexpectedly still O(instances)) → re-scope the parametric emit (documented); +Translate deferred; budget → P6/P7.
- **Cross-links:** KNOWN_UNKNOWNS Category 2 (Unknowns 2.1–2.4) · `SARF_STAT_TASK_SPARSIFICATION_DESIGN.md` · `docs/issues/ISSUE_1385_option-1-short-circuit-redesign-symbolic-instance-handling.md`.

### P3 — camcge `stat_mps` + Dual-Consistent Walras (#1330 → Epic 5)

- **Disposition:** PROCEED — **split track**: step 1 (a general nlp2mcp emit fix) lands in Sprint 32; step 2 (the Epic-5 Walras) is PROCEED-conditional.
- **PROCEED precondition — step 1 (general emit fix):** extend the #1462 "Transfer fixed-variable marginals to `_fx_` multipliers" block (`src/emit/emit_gams.py`) to cover the general scalar `var.fx` fixing — emit `nu_<var>_fx.l = ±<var>.m` (sign per the multiplier's stationarity role; for camcge's `stat_mps`, which enters `+ nu_mps_fx`, `nu_mps_fx.l = -mps.m`, confirmed `mps.m = −209.861` ≈ the −210 residual) → `kkt_residual.py camcge.gms` `stat_mps` → **Case-a**. A general emit-correctness fix (any fixed-scalar-variable model benefits).
- **PROCEED precondition — step 2 (PR27 check-the-dual-side, `/tmp` before `src/`):** the `/tmp` prototype of **step 1 + the dual-consistent Walras numéraire** (keep every market-clearing row + the consumption-weighted numéraire + redefine the redundant market's dual via Walras' law) must reach **MS-1 at omega 191.7346** (assert `modelstat`) *before* the Walras `src/` change. The **S1∧S2∧S3 detector** must flag **only** camcge across irscge/lrgcge/moncge/stdcge (S3 = cold-MCP-singular-at-iter-0, the false-positive guard; Day-7 cohort test: the four pass through cold MS-1, only camcge MS-4).
- **REPLAN exit:** the `/tmp` prototype (step 1 + step 2) still stays **MS-4** (the Walras rank-deficiency is deeper than a numéraire selection) → **step 1 lands anyway** (a cleaner CASE_B → Case-a), the numéraire falls to a per-model-numéraire-declaration **Epic-5** item; camcge stays `model_infeasible`; budget → P6/P7.
- **Cross-links:** KNOWN_UNKNOWNS Category 3 (Unknowns 3.1–3.4) · `CAMCGE_STAT_MPS_WALRAS_DESIGN.md` · `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` · `docs/issues/ISSUE_1330_camcge-model-infeasible-after-1245.md`.

### P4 — rocket Case-c-before-forcing → PATH-Consultation Input (#1462)

- **Disposition:** PROCEED-conditional — the deliverable is the packaged PATH-consultation input; rocket's +1 Solve is conditional on the Sprint-33 consultation.
- **PROCEED precondition (PR27 residual-clean-before-forcing):** re-confirm the emit residual is **clean at the NLP point (Case-c)** *before* any forcing attempt — `kkt_residual.py rocket.gms` residual concentrates on the **boundary rows** (`stat_ht(h0)`/`stat_step`/`stat_ht(h50)`, which move with the warm-start value — the non-convex boundary signature) with the interior near tolerance and dual-transfer CONSISTENT. This keeps rocket a *forcing* problem, not a latent emit bug (a Case-b interior residual would mean fix the emit first). Then confirm no untried emittable lever crosses (PATH options best INFES 477 → 382; μ-continuation / multistart / the division-by-variable reformulation all MS-5).
- **REPLAN exit:** no emittable lever crosses (intrinsic non-convergence confirmed) → the deliverable is the **finalized PATH-consultation input** (the concrete question with the reformulation as a *ruled-out* candidate + a reproducible case + the ruled-out-lever survey + the `--force` scaffold) for the renumbered Sprint 33; rocket's +1 Solve is a conditional hand-off.
- **Cross-links:** KNOWN_UNKNOWNS Category 4 (Unknowns 4.1–4.3) · `ROCKET_PATH_CONSULTATION_INPUT.md` · `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 · `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md`.

### P5 — hhfair + CGE Cluster Case-c Formalization (#1236)

- **Disposition:** PROCEED (the harness Case-c auto-classifier extension + the ISSUE closure). **No emit fix; the sign flip is BANNED.**
- **PROCEED precondition (PR27 control-before-implement — the sign flip is BANNED):** **no objective-gradient emit change is attempted** — the sign flip was control-refuted **4× across S30–S31** (hhfair 72.147 → 22.144 *worse*; himmel16; the ν_objective reduction inert, because `nu_obj = ±1`). The only `src/` change is the **`kkt_residual.py` classifier extension** (a diagnostic-tooling change, no emit change): a post-verdict reclassification pass — if CASE_B (which implies D2) + **D1** (the max-residual `stat_<var>`'s `<var>` appears in the objective defining equation `obj =e= f(<var>)`) + **D3** (the cold-start MCP reaches a spurious KKT point) → `case_c (objective-defining-intermediate-variable non-convexity)`. Gated on all four members re-confirmed Case-c (hhfair `stat_u` rel 2.0; irscge `stat_xp` rel 0.06; the Day-10 cohort control: CGE cold `UU=25.5085` vs match 26.09). Any **new** candidate tripping D1 needs the `/tmp` sign-flip-inert control (D4) before being trusted as Case-c.
- **REPLAN exit:** N/A for the emit (no emit fix). If a member proved a fixable Case-b (D3 not cold-spurious), carve it out as a genuine-floor candidate — but all four are re-confirmed genuine Case-c. ISSUE_1236 closes as documented-non-convex (methodology, not genuine floor; P5 delivers 0 floor).
- **Cross-links:** KNOWN_UNKNOWNS Category 5 (Unknowns 5.1–5.4) · `CASE_C_CLASSIFIER_DESIGN.md` · `docs/issues/ISSUE_1236_hhfair-objective-mismatch.md`.

---

## 2. Gate summary table

| Track | Model | Disposition | PROCEED precondition (control-before-src) | REPLAN exit |
|---|---|---|---|---|
| **P1** | mine (#1443) | PROCEED | `piL_x/piU_x` from the stationarity residual `N` (not `x.m`); warm residual → 0 (Case-a, `modelstat`) → presolve MS-1; foundation byte-stable | a 5th coupling (warm residual won't close) → Sprint-33 deeper head-offset architecture |
| **P2** | sarf (#1385) | PROCEED | O(active=398) symbolic `stat_task$taskposs` + `task.fx`; translate seconds not >180s; banked derivation, no set-name literals; atomic; golden byte-stable | parametric emit re-triggers the timeout → re-scope; +Translate deferred |
| **P3** | camcge (#1330) | PROCEED (split) | **step 1:** `nu_mps_fx.l = -mps.m` (#1462 block) → `stat_mps` Case-a; **step 2:** `/tmp` step 1 + dual-consistent Walras → MS-1 @ 191.7346 before src; S1∧S2∧S3 flags camcge only | `/tmp` stays MS-4 → step 1 lands, numéraire → per-model Epic-5 fallback |
| **P4** | rocket (#1462) | PROCEED-conditional | residual clean at NLP point (Case-c boundary signature) before forcing; no emittable lever crosses | intrinsic non-convergence → packaged PATH-consultation input (Sprint-33) |
| **P5** | hhfair/CGE (#1236) | PROCEED | **no emit fix** (sign flip BANNED, refuted 4×); the `kkt_residual.py` classifier extension (CASE_B + D1 + D3 → `case_c`); all four re-confirmed Case-c | a member is fixable Case-b (D3 not spurious) → carve out as genuine-floor candidate (none is) |

**Cross-cutting:** every gate cites `kkt_residual.py` (PR27) as the Case-(a/b/c) verdict engine; every emit-touching PR (P1/P2/P3) must also pass the golden-staleness check (PR26) + the `--resolve-changed --since-commit 4cbf8bff` checkpoint re-solve; P4 is a docs hand-off (no emit); P5's only `src/` change is the diagnostic classifier (no emit change). **`modelstat` is asserted before every objective read; `x.up=inf` is BANNED.**

---

## 3. Known-Unknowns dispositions (gate-layer)

| # | Unknown | Gate-layer disposition |
|---|---|---|
| 1.1 | mine bound-multiplier reconciliation | ✅ (gate) — P1 PROCEED behind the warm-residual→0 gate (`N`-derivation, `modelstat` asserted); 5th-coupling REPLAN exit. |
| 2.1 | sarf O(active) sparsification | ✅ (gate) — P2 PROCEED behind the O(active) translate-budget probe + the atomicity/anti-pattern checks; timeout-re-trigger REPLAN exit. |
| 3.1 | camcge `stat_mps`-first | ✅ (gate) — P3 step-1 (general emit fix) gated on `stat_mps` → Case-a; step-2 gated on the `/tmp`-to-MS-1 prototype; Epic-5-deferral REPLAN exit. |
| 4.1 | rocket Case-c scope guard | ✅ (gate) — P4 residual-clean-at-NLP-point (Case-c) re-confirm before any forcing; hand-off REPLAN exit. |
| 5.1 | hhfair/CGE Case-c classifier | ✅ (gate) — P5 control-before-implement (sign flip BANNED); the classifier extension is the only `src/` change; documented-Case-c closure. |

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team
**Anchor:** `--resolve-changed --since-commit 4cbf8bff` (Sprint-31 close) gates every emit-touching PR.
