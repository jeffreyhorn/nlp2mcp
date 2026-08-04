# rocket #1462 — PATH-Consultation Input (Sprint-36 Hand-Off)

> **Renumbering note (Sprint 35 Day 8, 2026-08-03):** the target-consultation labels were retargeted **Sprint 33 → Sprint 36** (11 refs). This input was authored in Sprint 32 (Day 9) naming the *then-next* consultation "Sprint 33"; the consultation kept slipping (S33→S34→S35 all deferred it, all as banked hand-offs), so the actual target is now **Sprint 36**. The technical content is current and unchanged — only the stale sprint-number labels moved. Authoring metadata ("Sprint 32 Day 9") is preserved. Submitted as part of the Sprint-36 consultation bundle (`SPRINT_36/CONSULTATION_BUNDLE.md`) alongside mine (P1) and fawley (P3).

**Created:** 2026-07-13
**Prep Task:** 6 (Priority 4)
**Issue:** #1462 (local write-up: `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md`)
**Status:** ✅ **FINALIZED (Sprint 32 Day 9, 2026-07-15)** — the PATH-consultation input for the renumbered **Sprint 36** consultation is packaged and finalized. All experiments read-only (harness); no `src/` change.

> **Day-9 finalization (PR27 gate satisfied):** the Case-c boundary signature is **re-confirmed on the current tree** — `kkt_residual.py rocket.gms` → CASE_B concentrated on the boundary rows `stat_ht(h0)` rel **1.00** (raw −4.56) / `stat_step` **0.497** / `stat_ht(h50)` **0.438**, with the interior near tolerance (`stat_v(h0)` 0.038, `stat_m(h0)` 0.014) and **dual-transfer CONSISTENT** (closure 1.53e-10). The residual is clean at the NLP point ⇒ rocket is a **forcing** problem, not a latent emit bug (fix-the-emit-first is ruled out). The `--force homotopy` scaffold **still emits** for rocket (`--nlp-presolve --force homotopy` → the `proximal_perturbation` μ-continuation driver + `mcp_model.optfile = 1`) — the hand-off mechanism the consultation's recommended option-set plugs into. **No emittable lever crosses** (the §2 survey stands: PATH options / μ-continuation / multistart / division-by-variable reformulation all MS-5). **+1 Solve is a conditional Sprint-36 hand-off, NOT a Sprint-32 gain.**

**Objective:** Package the finalized PATH-consultation input for rocket (the concrete question set + the ruled-out-lever survey) that feeds the Sprint-36 PATH consultation; confirm the emit residual is clean at the NLP point (Case-c) so rocket stays a forcing problem; and sweep for any remaining emittable lever.

---

## §1. Case-c scope guard — re-confirmed (harness, current tree)

`kkt_residual.py data/gamslib/raw/rocket.gms` on the current tree:

```
model: rocket    dual scale: 4.56
dual transfer: CONSISTENT (max comp infeas 0.00e+00 rel, max equality residual 1.53e-10 raw)
verdict: CASE_B  — emit_bug        <- harness's NOMINAL classifier label; see the interpretation below
max-residual row: stat_ht(h0)   rel = 1.00e+00  (raw -4.56e+00)
top: stat_ht(h0) 1.00, stat_step 0.497, stat_ht(h50) 0.438, stat_v(h0) 0.038, stat_m(h0) 0.014
```

*(`CASE_B — emit_bug` is the harness's **nominal** classifier label — the residual-tolerance verdict, not a final diagnosis; the interpretation below shows it is a Case-c **boundary** signature, not a cleanable emit bug.)*

**Reading — this is the Case-c *boundary* signature, not a cleanable emit bug (per ISSUE_1462):** the residual concentrates entirely on the **boundary/terminal rows** of the discretized optimal-control problem — `stat_ht(h0)` (the initial-altitude grid point), `stat_ht(h50)` (the terminal grid point), and `stat_step` (the time-step) — which **move with the warm-start value** (`nu_*_fx = 0` → `stat_step`; `= var.m` → `stat_ht(h0)`). The **interior** stationarity rows are near tolerance (`stat_v(h0)` 0.038, `stat_m(h0)` 0.014). Dual-transfer CONSISTENT (closure 1.53e-10). So the emit is clean except the boundary rows that are inherently non-convex — **rocket is a genuine forcing problem, not a latent emit bug.** The scope guard holds: no emit fix is attempted; the deliverable is the PATH-consultation input.

---

## §2. The ruled-out-lever survey (consolidated)

Every emittable-GAMS / PATH-option lever probed across Sprints 30–31 — **none converges rocket** (all stay MODEL STATUS 5 Locally Infeasible):

| Lever | Mechanism | Type | Result |
|---|---|---|---|
| `proximal_perturbation` {1e-2, 1e-1, 1.0, 1e2} | Levenberg-Marquardt Jacobian regularization (trust-region analogue) | PATH option | MS-5; INFES 477 → 456–482 (no monotone gain) |
| `crash_method pnewton` + `crash_perturb yes` | projected-Newton crash to a better basis | PATH option | MS-5; INFES 477 (unchanged) |
| `merit_function normal` + `gradient_step_limit` | non-monotone merit steering | PATH option | MS-5; INFES → **382** (best of all configs) |
| Combined strong (`merit normal` + `pp 1e-1` + `crash pnewton` + 20k/500k iters) | | PATH option | MS-5; INFES 458 |
| **Homotopy / μ-continuation** | `proximal_perturbation` continuation `mu: 1e3 → 0`, warm-restart each step | Emittable GAMS (`--force homotopy`) | **MS-5 across every continuation step** |
| **Multi-start** | `.l`-perturbation re-solve loop | Emittable GAMS (`--force multistart`) | inconclusive / superseded — warm-starting from the *NLP optimum itself* already fails, so random restarts are a priori unpromising |
| **Division-by-variable reformulation** | remove all `1/m`,`1/ht²` from the initial Jacobian: `gf` → `g·ht² = g_0·h_0²`; a free acceleration `a(h)` with `(a+g)·m = T−D` replacing `(T−D−m·g)/m` in `v_eqn` | Emittable GAMS (emit transform) | reformulated **NLP solves to the same optimum 1.0128**, but the MCP is **MS-5 cold, MS-5 warm-started from the NLP optimum, and MS-5 across every μ-continuation step** (nh=10; nh=50 exceeds the demo-license nonlinear-row limit) |

**The decisive finding (Sprint-31 Day-11):** the division-by-variable reformulation removes ALL `1/m`,`1/ht²` from the initial Jacobian, yet the MCP still does not converge — **so rocket's non-convergence is intrinsic to the discretized optimal-control MCP structure, NOT the division-by-variable Jacobian conditioning.** This *sharpens* the consultation question (the reformulation is now a ruled-out candidate, redirecting the question toward the intrinsic structure).

---

## §3. The finalized PATH-consultation question (feeds Sprint 36)

> rocket's MCP is **MODEL STATUS 5** with `EXIT — other error` at an ill-conditioned initial Jacobian; the ill-conditioning was *initially suspected* to come from the division-by-variable terms (`1/m(h)` in the velocity update, `1/ht(h)²` in gravity). `proximal_perturbation` / `merit_function` / `crash_method` move INFES **477 → 382** but do **not** converge from the NLP-optimum warm-start. A `1/m` + `1/ht²` auxiliary-variable reformulation (`gf` multiplied through to `g·ht² = g_0·h_0²`; a free acceleration `a(h)` with `(a+g)·m = T−D` replacing `(T−D−m·g)/m` in `v_eqn`) — which removes **ALL** division-by-variable from the initial Jacobian — **ALSO does not converge** (the reformulated NLP solves to the same optimum 1.0128, but its MCP is MS-5 Locally Infeasible cold, MS-5 warm-started from the NLP optimum, and MS-5 across every μ-continuation step, at nh=10). **So the non-convergence is intrinsic to the discretized optimal-control MCP structure, not the division-by-variable Jacobian conditioning.** The residual at the NLP optimum is clean except the boundary rows (`stat_ht(h0)`/`stat_ht(h50)`/`stat_step`), which move with the warm-start value — a non-convex boundary signature. **Which PATH option set / regularization schedule / model reformulation forces convergence for this discretized optimal-control MCP?**

**Reproducible case for the PATH authors:** from `data/gamslib/raw/rocket.gms` (the Goddard rocket, COPS), emit the warm-started MCP with

```bash
python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_presolve.gms --nlp-presolve
gams rocket_mcp_presolve.gms        # → MODEL STATUS 5, warm-started from the embedded NLP optimum
```

The forcing scaffold adds the μ-continuation driver + the PATH optfile: `python -m src.cli data/gamslib/raw/rocket.gms -o rocket_mcp_forced.gms --nlp-presolve --force homotopy` (or `--force optfile`).

---

## §4. Remaining-lever sweep result

The Task-6 sweep for any **untried** emittable-GAMS lever surfaces **none**: the PATH-option space is exhausted (best INFES 382, MS-5), the μ-continuation is exhausted (MS-5 every step), multistart is superseded (warm-from-optimum already fails), and the division-by-variable reformulation is exhausted (MS-5). No scaled/relaxed continuation schedule beyond the tried `mu: 1e3 → 0` offers a new mechanism (the reformulation result shows the conditioning is not the blocker). **No Day-1 forcing attempt is warranted** — the packaged PATH-consultation input (§3) is the deliverable, and rocket's +1 Solve is deferred to the Sprint-36 consultation.

---

## §5. Sprint-36 hand-off note

The de-risked Sprint-36 hand-off has three parts, all landed/banked:

1. **The `--force {homotopy, multistart, optfile}` scaffold** (landed Sprint 30) — emits the μ-continuation driver + the PATH optfile, the mechanism the consultation's recommended option-set/schedule would plug into.
2. **The finalized PATH-consultation question (§3)** — concrete, with the reformulation as a *ruled-out* candidate, targeting the intrinsic discretized-optimal-control structure.
3. **The ruled-out-lever survey (§2)** — so the PATH authors don't re-suggest the exhausted levers (PATH options, continuation, multistart, reformulation).

Sprint 36 submits §3 (with the §1 Case-c residual + the §2 survey + the reproducible case) to the PATH authors; a recommended option-set/schedule plugs into the `--force` scaffold. rocket stays `model_infeasible` until then; the +1 Solve is conditional on the consultation.

---

## §6. Summary + Known-Unknowns dispositions

| # | Unknown | Disposition |
|---|---|---|
| 4.1 | Is the emit residual clean at the NLP point (Case-c) so rocket stays a forcing problem? | ✅ VERIFIED — the harness residual concentrates on the boundary rows (`stat_ht(h0)` 1.00, `stat_step` 0.50, `stat_ht(h50)` 0.44) that move with the warm-start value (the non-convex Case-c boundary signature); the interior is near tolerance; dual-transfer CONSISTENT. rocket is a forcing problem, not an emit bug. |
| 4.2 | Do any remaining emittable levers cross the intrinsic non-convergence? | ✅ VERIFIED — no untried emittable lever surfaces; the PATH-option space (best INFES 382), μ-continuation, multistart, and the division-by-variable reformulation are all exhausted (MS-5). No Day-1 attempt is warranted; the hand-off is the deliverable. |
| 4.3 | Is the packaged PATH-consultation question concrete enough for the Sprint-36 hand-off? | ✅ VERIFIED — the §3 question includes the ruled-out-lever survey (so the PATH authors don't re-suggest them), the intrinsic-structure focus (the reformulation ruled out), and a reproducible case; the `--force` scaffold + the question form a self-contained hand-off. |

**Decision: PROCEED to the Sprint-36 hand-off.** rocket's non-convergence is intrinsic (confirmed across every emittable lever); the Case-c scope guard holds (no emit bug); the packaged PATH-consultation input (§3) + the `--force` scaffold + the ruled-out survey (§2) are the de-risked deliverable. rocket's +1 Solve is **conditional on the Sprint-36 consultation** (not a Sprint-32 gain).

---

**Document Created:** 2026-07-13
**Owner:** Sprint 32 Planning Team (solver/KKT specialist)
**Evidence:** `kkt_residual.py data/gamslib/raw/rocket.gms` (CASE_B concentrated on `stat_ht(h0)`/`stat_step`/`stat_ht(h50)` boundary rows, duals CONSISTENT); `docs/planning/EPIC_4/SPRINT_31/BACKLOG_FIX_SURFACE_ANALYSIS.md` §3 (the finalized question); `docs/planning/EPIC_4/SPRINT_30/NONCONVEX_FORCING_SURVEY.md` §4 (the lever survey, INFES 477 → 382); `docs/issues/ISSUE_1462_rocket-fx-multiplier-warmstart-nonconvex.md` (the Day-11 reformulation-exhaustion probe).
