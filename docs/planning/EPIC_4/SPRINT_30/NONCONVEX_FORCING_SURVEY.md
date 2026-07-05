# Non-Convex Forcing Strategy Survey (rocket #1462 + Cold-Convex Case-c Residue)

**Task:** Sprint 30 Prep Task 4 (Priority 2 foundation — research-before-design)
**Date:** 2026-07-05
**Owner:** Development team (numerics / solver-interface)
**Scope:** research/design only — no `src/` change (all probes were `/tmp` copies + a transient `path.opt`, reverted; the committed goldens are untouched).

---

## 0. Executive summary

rocket (#1462) is the Goddard rocket optimal-control problem (COPS): highly non-convex — `sqr(v)`, `exp(...)`, `sqr(h_0/ht)` (**division-by-variable** + square), the `/m(h)` terms in `v_eqn` (division-by-variable), and bilinear `step·(v+v_prev)`. Its MCP's **initial Jacobian carries `1/ht²` and `1/m²` entries** that are ill-conditioned at the start point. Sprint-29 confirmed: with the complete `_fx_` warm-start (landed Day 1), the **embedded NLP reaches MS 2 (1.00412 ≈ ref 1.0128) but the MCP stays MS 5 Locally Infeasible**, PATH `EXIT — other error` at the initial Jacobian — **intrinsic non-convergence**, not an emit/warm-start defect.

**This survey's empirical findings (Task-4 probes, this branch):**

1. **The effective forcing levers are PATH solver options, not emittable GAMS.** Trust-region damping = PATH `proximal_perturbation` (Levenberg-Marquardt Jacobian regularization); the other tunable levers (`crash_method`, `merit_function`, iteration limits) are also PATH options.
2. **No in-GAMS PATH-option lever forces rocket to MS 1/2.** Across `proximal_perturbation` 1e-1…1e2, `crash pnewton`, `merit_function normal`, and combined strong configs, rocket **stays MS 5**; the best config (`merit_function normal` + `proximal_perturbation 1e-2`) reduces the infeasible-row count **477 → 382** but never converges. → the residual convergence is a **PATH-solver-internals question → Sprint-31 PATH-author consultation.**
3. **No cold-convex Case-c shared payoff.** The 4 Case-c cohort models (bearing / launch / mathopt3 / robustlp, `COLD_CONVEX_COHORT_SURVEY.md` §3) are emit-correct and **already warm-match** (`model_optimal_presolve` + `compare_objective_match`, residual ≤ 8e-6) — they need **no forcing**. rocket is the **sole** genuinely-non-converging model. So a rocket forcing lever has no additional cohort to lift.
4. **Chosen P2 lever + decision.** Sprint-30 P2 = build the **emitted-GAMS forcing-harness scaffold** (homotopy/continuation + multi-start driver + optional PATH-optfile emission) as the P8 entry point — **NOT** a firm rocket +1 Solve. rocket's +1 Solve is **conditional and likely defers to Sprint-31** (the PATH-option tuning that moves INFES 477 → 382 but doesn't converge is the concrete PATH-consultation hand-off). This is the honest outcome: the scaffold lands; rocket's solve does not, on the evidence.

---

## 1. Forcing-lever enumeration (Unknown 2.1) + the nlp2mcp/PATH boundary (Unknown 2.2)

| Lever family | Mechanism | Emittable GAMS? / PATH option? | rocket probe result |
|---|---|---|---|
| **Trust-region damping** | PATH `proximal_perturbation` — adds a Levenberg-Marquardt regularization term to the Jacobian (the MCP analogue of a trust region), stabilizing the ill-conditioned `1/ht²`,`1/m²` initial Jacobian | **PATH option** (optfile) | pp ∈ {1e-1, 1.0, 1e2}: **MS 5**; INFES 477 → 456–482 (no monotone gain) |
| **Crash / restart** | PATH `crash_method pnewton` + `crash_perturb` — a projected-Newton crash to a better initial basis | **PATH option** | **MS 5**, INFES 477 (unchanged) |
| **Merit function** | PATH `merit_function normal` + `gradient_step_limit` — the non-monotone merit steering | **PATH option** | **MS 5**; INFES → **382** (the best of all configs), still no convergence |
| **Combined strong** | merit + pp 1e-1 + crash + 20k major / 500k minor iters | **PATH option** | **MS 5**, INFES 458 |
| **Homotopy / continuation** | Emitted-GAMS loop: solve a relaxed/convexified/scaled problem, then step a continuation parameter `μ: relaxed → original`, re-solving from each prior point | **Emittable GAMS** (a P2/P8 scaffold — a driver loop around the `Solve mcp_model using MCP;`) | design-level (a scaffold, not a one-line probe) — **not demonstrated to crack rocket** |
| **Multi-start** | Emitted-GAMS `.l`-perturbation loop: re-solve from several perturbed initial points, keep the first MS-1/2 | **Emittable GAMS** | probe not cleanly executed (the injected `.l` perturbation broke the emit) — **inconclusive**; superseded by the PATH-option result (warm-starting from the *NLP optimum itself* already fails, so random restarts are a priori unpromising) |

**The nlp2mcp/PATH boundary (Unknown 2.2):** the three *tunable* levers (trust-region/proximal_perturbation, crash, merit) are **PATH options** delivered via an `optfile` — nlp2mcp can *emit* the optfile (a P8 capability), but the tuning that would actually force convergence is PATH-internal and, on the evidence, **not reachable by the documented options** → **Sprint-31 PATH-author consultation.** The two *structural* levers (homotopy/continuation, multi-start) are **emittable GAMS** and are the Sprint-30 P8 scaffold — but the probe gives no evidence they crack rocket.

---

## 2. rocket prototype-probe (Unknown 2.1) — method + result

- **Emit:** `nlp2mcp data/gamslib/raw/rocket.gms --nlp-presolve -o /tmp/rocket_ps.gms` (the presolve emit already carries the Day-1 `_fx_` warm-start). Run GAMS from the repo root (the emit's `$include "data/gamslib/raw/rocket.gms"` is repo-relative).
- **Baseline:** embedded NLP → MS 2; MCP `mcp_model` → **MS 5 Locally Infeasible, 477 INFES, 0 evaluation errors** (matches ISSUE_1462 Day-2).
- **Lever injection:** `mcp_model.optfile = 1;` before the `Solve mcp_model using MCP;` + a `path.opt` per config (env-guarded, transient — removed after each run; **zero `src/` diff**).
- **Result:** every PATH-option config stayed **MS 5**. Best = `merit_function normal` + `proximal_perturbation 1e-2` → INFES 477 → **382** (a ~20% reduction, but PATH stalls, does not converge). Larger `proximal_perturbation` (1e2) and crash did **not** improve on the baseline. **No config reached MS 1/2 or the NLP objective 1.0128.**

**Verdict (Unknown 2.1):** confirms the Sprint-29 Day-2 finding — rocket's MS-5 is **intrinsic non-convergence**, not defeated by PATH-option forcing. The INFES reduction (477 → 382) shows the regularization *helps* but is insufficient; a PATH-author may know a config/strategy that crosses, hence the Sprint-31 consultation.

---

## 3. Cold-convex Case-c shared-payoff check (Unknown 2.3) + residue disposition (Unknown 7.2)

The Sprint-29 cohort survey (`COLD_CONVEX_COHORT_SURVEY.md` §3) partitioned the ~30 cold-convex models: **4 are Case-c** (emit correct, inherent non-convex) — **bearing, launch, mathopt3, robustlp** — with residuals ≤ 8e-6 (numerically at the KKT point).

| Case-c model | Day-0 bucket | Comparison | Needs forcing? |
|---|---|---|---|
| bearing | `model_optimal_presolve` | `compare_objective_match` | **No — already matches (warm)** |
| launch | `model_optimal_presolve` | `compare_objective_match` | **No — already matches** |
| mathopt3 | `model_optimal_presolve` | `compare_objective_match` | **No — already matches** |
| robustlp | `model_optimal_presolve` | `compare_objective_match` | **No — already matches** |
| **rocket** | **`model_infeasible`** | — | **Yes — the sole non-converging model** |

**Shared payoff (2.3): NONE.** The 4 Case-c cohort models are emit-correct and warm-match already — a forcing lever has nothing to recover there. rocket is the only genuinely-non-converging non-convex model (its NLP-optimum warm-start does not make the MCP converge — the distinguishing "intrinsic non-convergence" signature the 4 Case-c models do **not** share).

**Case-c residue disposition (7.2):** the residue = {bearing, launch, mathopt3, robustlp} already matching (no action, documented cold-robust) **+ rocket** (the sole forcing target, which resists PATH tuning → Sprint-31). There is **no Sprint-30 forcing-sprint cohort** — it is rocket-alone, and rocket's forcing is a PATH-consultation question. Document the 4 as inherent-non-convexity-that-warm-matches; rocket as the Sprint-31 PATH-consultation target.

---

## 4. Chosen P2 lever + P8 scaffold entry point + Sprint-31 hand-off

**Chosen Sprint-30 P2 lever:** the **emitted-GAMS forcing-harness scaffold** — a `--force <strategy>` emit mode (or a driver template) that wraps `Solve mcp_model using MCP;` in one of:
1. a **homotopy/continuation** loop over a continuation parameter (relaxed/scaled → original), re-solving from each prior point;
2. a **multi-start** `.l`-perturbation loop (re-solve from N perturbed points, keep the first MS-1/2);
3. an emitted **PATH `optfile`** (a `proximal_perturbation` schedule + `merit_function normal`) — the tunable levers §1.

**P8 forcing-scaffold entry point (feeds Unknown 8.3 / Task 8):** the stable interface Sprint-31 inherits = a lever-injection hook around the MCP solve + a MODEL-STATUS reporter (the scaffold emits the driver; the strategy is a parameter). Sprint-30 P8 builds this scaffold and validates its plumbing on rocket (it *runs* the levers) — but, per §2, it is **not** expected to make rocket converge.

**Sprint-31 PATH-consultation hand-off scope:** "rocket's MCP is MS 5 with `EXIT — other error` at an ill-conditioned initial Jacobian (`1/ht²`,`1/m²`); `proximal_perturbation`/`merit_function`/`crash` move INFES 477 → 382 but do not converge from the NLP-optimum warm-start. Which PATH option set / regularization schedule / reformulation forces convergence for this division-by-variable optimal-control MCP?"

**Decision (feeds Task 6 REPLAN + Task 10 schedule):** P2 Sprint-30 deliverable = **the forcing scaffold** (firm) + **the PATH-consultation hand-off** (Sprint-31). rocket's **+1 Solve is NOT firm for Sprint 30** — it is conditional on the Sprint-31 PATH consultation (or a reformulation). Task 6 should record rocket as PROCEED-to-scaffold with the +1 Solve deferred; Task 10 should schedule the scaffold build, not a rocket-solve milestone.

---

## 5. Unknowns resolved

- **2.1 (which forcing lever moves rocket): ⚠️ none of the tunable in-GAMS PATH options do** — best (merit+proximal_perturbation) reduces INFES 477 → 382 but stays MS 5. Intrinsic non-convergence confirmed.
- **2.2 (nlp2mcp/PATH boundary): the effective levers are PATH options** (proximal_perturbation/crash/merit), and even the strongest don't converge → PATH-internals → **Sprint-31 PATH consultation**; the emittable-GAMS levers (homotopy/multi-start) are the P8 scaffold.
- **2.3 (Case-c shared payoff): NONE** — the 4 Case-c cohort models already warm-match (emit-correct); rocket is the sole non-converging model.
- **7.2 (Case-c residue disposition): rocket-alone.** The 4 Case-c models are documented inherent-non-convexity-that-warm-matches (no action); rocket is the Sprint-31 PATH-consultation target. No Sprint-30 forcing cohort.

---

## Appendix — evidence

- Emit: `.venv/bin/python -m src.cli data/gamslib/raw/rocket.gms --nlp-presolve -o /tmp/rocket_ps.gms`.
- Baseline: GAMS from repo root → embedded NLP MS 2; MCP MS 5, 477 INFES, 0 eval errors.
- PATH-option probes (transient `path.opt`, `mcp_model.optfile=1`): pp{1e-1,1.0,1e2}, crash pnewton, merit_function normal, combined — all **MS 5**; best INFES 382 (merit + pp 1e-2).
- Case-c cohort buckets (§3): DB `data/gamslib/gamslib_status.json` — bearing/launch/mathopt3/robustlp all `model_optimal_presolve` + `compare_objective_match`; rocket `model_infeasible`.
- Prior: `docs/issues/ISSUE_1462_*.md` Day-2 (complete `_fx_` warm-start → NLP MS 2 1.00412 / MCP MS 5; degenerate-bound probe no help; residual not cleanable by warm-start value).
- No `src/` or golden change committed; all probes reverted.
