# Sprint 30 — Progress Log

Head-Domain-Offset Emit Architecture, Non-Convex Forcing & Offset-Alias AD (Sprint 29 carryforward). Schedule: `PLAN.md`; prompts: `prompts/PLAN_PROMPTS.md`.

| Day | Priority / Work | Metric delta | Status |
|---|---|---|---|
| 0 | Kickoff + Day-0 traces (PR24) | — (baseline confirmed) | ✅ DONE (docs/trace-only) |
| 1 | P1a robert objective-gradient fix (decoupled, firm) | genuine floor 69 → **70** (robert cold-match) | ✅ DONE |
| 2 | P2 rocket forcing scaffold (firm P8) | — (scaffold lands; rocket +1 Solve → Sprint-31) | ✅ DONE |
| 3 | P2 rocket forcing REPLAN decision | — (no lever converges; rocket +1 Solve → Sprint-31 PATH consult) | ✅ DONE (REPLAN) |

---

## Day 0 — Kickoff + Day-0 Traces (2026-07-06)

**Branch:** `planning/sprint30-day0-kickoff`. Docs/trace-only — no `src/` change.

### Baseline confirmed = Sprint 29 final (no drift)

- **`git diff 68b5b4a7..HEAD -- src/ scripts/` is EMPTY** (S29 close = `68b5b4a7`, "SPRINT 29 CLOSED") → Day-0 = Sprint 29 final without a retest (Unknown 8.2). Every commit since the close is docs-only (the Sprint-30 PROJECT_PLAN insertion + the Tasks 1–10 prep PRs).
- **DB recompute (canonical 142-model scope, `convexity.status ∈ {verified_convex, likely_convex}`)** reproduces the Sprint 29 final headline exactly:

  | Metric | Day-0 | Target (S30) |
  |---|---|---|
  | Translate | **135** | ≥ 135 (stretch +1) |
  | Solve | **107** | ≥ 109 (mine + rocket, REPLAN-prone) |
  | Match | **92** | maintain ≥ 92; genuine floor 69 → ≥ 72 |
  | model_infeasible | **7** | ≤ 5 |
  | path_syntax_error | **8** | ≤ 8 |
  | path_solve_terminated | **4** | ≤ 5 |
  | path_solve_license | 9 | — |

- **PR25 tally:** genuine floor **69** / methodology ~23. Firm path (genuine floor → ≥ 72) = robert (P1a) + Class-B `stat_pz` (P7) + offset-alias polygon/himmel16 (P5) + hhfair-if-Case-b (P3). The +2 Solve (mine + rocket) is REPLAN-gated (§`REPLAN_RISK_ASSESSMENT.md`).

### Day-0 traces (PR24) — every banked surface re-confirmed at Sprint-30 HEAD

| Track | Trace result (Sprint-30 Day-0) | Verdict |
|---|---|---|
| **robert** (P1a) | `kkt_residual.py` → CASE_B, `stat_x(high,3)` rel **7.20**, dual transfer CONSISTENT — but this top row is the **same-index transfer artifact** (`TOOLING_READINESS_AUDIT.md` Tool 1). The operative surface is the objective-gradient `stat_s` drop, cold-confirmed by the control experiment (`stat_s`-patch → **11025.0**; `stat_x`-patch → unchanged 6741.67). | Confirmed — objective-gradient `stat_s`, NOT the head-offset cross-term (Unknown 1.1 ❌ / 1.4 ❌ absorbed by the P1 split). |
| **mine** (P1b) | `kkt_residual.py` → CASE_B, `stat_x(4,1,1)` rel **1.33**, CONSISTENT. **Cold-INFES histogram** (the 4th-site question): cold MS-5, **51 INFES** dominated by the `comp_pr` precedence complementarity (`pr` rows nw 6 / ne 9 / se 12 / sw 11 = 38) + the coupled **`x → 4.07e10`** blowup + `def` (1). **NO distinct 4th bound-row site** — `comp_lo_x`/`comp_up_x`/`stat_x` are **not** in the INFES set (the #1224 `stat_x` cross-term already landed). The `nw` direction (`li=lj=0`) is least-infeasible (6) vs ne/se/sw (9/11/12) — the parameter-offset directions carry the residual, exactly the Day-7 `l+1 × li(k)/lj(k)` coupling. | Confirmed — the 3-site set appears **complete** (no 4th site); PROCEED-lean on the coordinated `comp_pr` fix; the cold `x → 4e10` is the LCP residual the fix must drive to 0. |
| **rocket** (P2) | Case-c — the emit residual is clean at the NLP point; the cold/presolve MCP is **MS-5** intrinsic non-convergence (Task-4 evidence: 477 INFES; no PATH-option config converges). | Confirmed — forcing-scaffold territory; the +1 Solve is the Days-2–3 REPLAN decision (→ Sprint-31 PATH consultation). |
| **hhfair** (P3) | Emit `--nlp-presolve` + GAMS `action=c`: **first error is `$184` "Domain list redefined"** on the widened-VARIABLE `n` (source `n(t)` at `hhfair.gms:43` under the `$onMultiR $include` vs the MCP-widened `n(tl)`), *then* the `$257`/`$141` cascade. | Confirmed — the `$184` widened-VARIABLE blocker (not the Day-0-attributed `$141`), matching the Sprint-29 Day-8 diagnosis. |
| **Class-B** (P7) | `kkt_residual.py` on the cluster → **irscge** `stat_pz(MLK)` rel **1.00**, **lrgcge** `stat_pz(MLK)` rel **1.00**, **moncge** `stat_pz(BRD)` rel **1.00** — all CASE_B, all dual transfer CONSISTENT. | Confirmed — identical relative residual (missing-unit-coefficient fingerprint) → **one general-emit coefficient fix converts all three**; NOT Walras (full-rank block, distinct from camcge). |
| **polygon** (P5) | `kkt_residual.py` → CASE_B, `stat_theta(i12)` rel **0.492**, CONSISTENT. | Confirmed — the successor-offset objective cross-term (coupled with the distance-Jacobian symmetry, the Day-5-revert coupling). |
| **himmel16** (P5) | `kkt_residual.py` → CASE_B, `stat_area(1)` rel **2.00**, CONSISTENT. | Confirmed — the cyclic `i++1` cross-term is present; the 2.0 is the objvar-gradient-sign defect (distinct from polygon). |
| **camcge** (P6) | Banked: MS-4 Infeasible at iteration 0 (inherent Walras-law singular Jacobian) — the Epic-5 drop-one-`lmequil`-instance + fix-numéraire transformation (`CAMCGE_WALRAS_TRANSFORM_DESIGN.md`). | Confirmed banked (Day-11 empirical gate). |
| **sarf** (P4) | Banked: `translate_failure` (the 2-D dynamic-subset blow-up — `tbal`/`equipb1`/`equipb2` = 1,152 instances — that the srpchase 1-D short-circuit doesn't catch). | Confirmed banked (Day-9 atomic symbolic-emit + tractability gate). |

### Gate Traced-Fix-Surface lines

- **mine / rocket / hhfair** gates already carry a *confirmed* `Traced Fix-Surface (Day-0)` from Sprint-29 Day-0 — still valid (no `src/` drift); the Sprint-30 Day-0 re-confirmation above is recorded here (the mine cold-INFES histogram is the new Sprint-30 finding: no 4th site).
- **robert / Class-B** gates carried a `Day-0 hypothesis` — **upgraded to Sprint-30 Day-0 CONFIRMED** (this log's table + the gate notes).

### Day-0 outcome

Baseline = Sprint 29 final (no drift); all 9 banked surfaces re-confirmed at HEAD; the mine 3-site set is complete (no 4th bound-row site); Sprint 30 proceeds to **Day 1 (P1a robert objective-gradient fix)**. No `src/` change; no metric change. Trace-notes only.

---

## Day 1 — Priority 1a: robert objective-gradient fix (decoupled, firm genuine-floor) (2026-07-06)

**Branch:** `planning/sprint30-day1-robert`. **+1 genuine floor** (robert warm-only-match → genuine **cold** match).

### Root cause (the objective-gradient consolidation bug)

`_build_indexed_gradient_term` (`src/kkt/stationarity.py`) consolidates the per-instance objective gradient into a single indexed `stat_<var>` term using **one representative instance**. For robert, `s(r,tt)` appears in the objective under TWO structurally-different terms — `sum(t, -storage-c*s(r,t))` (`t` a subset of `tt`) and `+res-value*s(r,"4")` (a fixed boundary element) — so `s(r,tt∈t)` has gradient `+storage-c(r)` while `s(r,"4")` has `-res-value(r)`. The single-representative collapse kept only the storage-c term, **dropped its `$(t(tt))` subset guard** (emitting it for all tt), and **dropped the res-value boundary term** — so the cold MCP admitted the spurious 6741.67 KKT point (the #1447 objective-term-scoping family, extended to fixed-literal-element terms).

### Fix

When the non-zero objective-gradient instances fall into MORE THAN ONE distinct generalized-gradient group, emit the **sum of each group's gradient guarded by the condition that selects its instances** (reusing the #1131 subset/sameas guard builder): `misc("storage-c",r)$(t(tt)) - misc("res-value",r)$(sameas(tt,'4'))`. Tightly gated: (a) not the #1387 offset path, (b) genuine **clustering** (`1 < groups ≤ 8` **and** `groups < non-zero instances`) — so per-instance offset residue that doesn't canonicalize (e.g. chain's `nh(i1-1)`, `nh(i2-1)`, … objective cross-terms) does **not** split into a per-element sum, and (c) a `≤ 32`-instance perf cap so the O(N) per-instance generalization never dominates emit time on large-instance variables (cesam's 81-instance `a(ii,jj)` stays on the unchanged single-representative path). `stat_x` is untouched (`nu_sb(r,tt)` was already correct, Unknown 1.4).

### Verification

- **robert cold-solves to MODEL STATUS 1 Optimal at profit 11025.0** (= the NLP optimum) — a genuine cold match, no warm-start (convex LP). The emitted `stat_s(r,tt).. (misc("storage-c",r)$(t(tt)) + (((-1) * misc("res-value",r)))$(sameas(tt,'4')) - nu_sb(r,tt) + nu_sb(r,tt-1)$(ord(tt)>1) - piL_s(r,tt))$(…)` matches the hand-derived KKT.
- **Blast-radius (byte-scan + re-solve):** robert only; chain / cesam byte-identical (reverted by the clustering guard + the perf cap); no emit-time regression (cesam 10.1 s unchanged).
- **Tests:** new property fixture `shape9_objgrad_subset_boundary.gms` + `test_shape9_objgrad_subset_boundary` (asserts both guarded groups); the #1131 gradient-condition unit tests pass (2 groups = 2 instances → no clustering → unchanged).

---

## Day 2 — Priority 2: rocket forcing scaffold (firm P8) (2026-07-06)

**Branch:** `planning/sprint30-day2-rocket-scaffold`. **Firm P8 deliverable** — the solution-forcing scaffold + the Sprint-31 PATH-consultation entry point. rocket's +1 Solve is **not** achieved (intrinsic non-convergence, deferred to Sprint 31, per `REPLAN_RISK_ASSESSMENT.md` Track B).

### Deliverable — the `--force <strategy>` scaffold

A new `--force {none|homotopy|multistart|optfile}` emit mode (`src/config.py` `Config.force_strategy` + `src/cli.py` `--force` + `src/emit/forcing.py`) that wraps the terminal `Solve mcp_model using MCP;` in a forcing driver + a **MODEL-STATUS reporter** — the stable interface (`NONCONVEX_FORCING_SURVEY.md` §4: a lever-injection hook around the MCP solve + a status reporter, strategy as a parameter). The strategy is emitted at the solve site in `src/emit/emit_gams.py`:
- **`optfile`** — emits a PATH `path.opt` (`proximal_perturbation 1e-2` + `merit_function normal`) + `mcp_model.optfile = 1;` + one solve (the tunable levers, survey §1).
- **`multistart`** — a perturbed-`.l` restart loop (re-solve from N starts, stop at the first MS 1/2); a documented model-specific perturbation hook + the loop plumbing.
- **`homotopy`** — a `mu: 1 → 0` continuation loop, warm-restarting from each prior point; a documented relaxation hook + the loop plumbing.

### Validation — the scaffold runs the levers on rocket

Emitted rocket's `--nlp-presolve` MCP with each strategy and ran it in GAMS from the repo root:

| Strategy | Compile errors | MCP solves run | Reporter | Result |
|---|---|---|---|---|
| optfile | 0 | 2 (embedded NLP + forced MCP) | fired | MS 5 (unchanged) |
| multistart | 0 | 5 (embedded + **4 restart solves**) | fired | MS 5 (unchanged) |
| homotopy | 0 | 6 (embedded + **5 continuation solves**) | fired | MS 5 (unchanged) |

So the **plumbing runs the levers** (the loops execute the re-solves; the optfile applies the PATH options) and the reporter captures the status (`nlp2mcp_force_modelstat = 5` = MS-5 Locally Infeasible). As expected (survey §2), rocket stays MS-5 — it is intrinsic non-convergence, the **Sprint-31 PATH-consultation hand-off** ("which PATH option set / regularization schedule / reformulation forces convergence for this division-by-variable optimal-control MCP?").

### Blast radius + verification

- **Opt-in, no golden churn:** `--force none` (the default) emits the plain solve — rocket's presolve golden is byte-identical; no model's default emit changes.
- **Tests:** `tests/unit/emit/test_forcing_scaffold.py` (13 tests: each driver's structure + reporter + the `none` default + validation + the `Config.force_strategy` field). `make typecheck/format/lint` pass (99 source files).

### Day-2 outcome

The firm P8 forcing scaffold lands + is validated (runs the levers on rocket). rocket's +1 Solve is **deferred to Sprint 31** (the PATH consultation). No metric change (Solve 107 / Match 92 hold); the genuine-floor lift is unaffected. Next: **Day 3 — the rocket forcing REPLAN decision** (drive the emittable-GAMS levers; PROCEED if any reaches MS 1/2 at 1.0128, else file the Sprint-31 hand-off).

---

## Day 3 — Priority 2: rocket forcing REPLAN decision (2026-07-07)

**Branch:** `planning/sprint30-day3-rocket-replan`. **Decision: REPLAN rocket's +1 Solve to the Sprint-31 PATH consultation** (the scaffold + hand-off land regardless; prior High, per `REPLAN_RISK_ASSESSMENT.md` Track B).

### Drove the emittable-GAMS levers on rocket (the ones Task 4 left unexhausted)

On rocket's `--nlp-presolve` MCP, warm-started from the NLP optimum:

| Lever (real, not a hook) | Config | Result |
|---|---|---|
| **multistart** (`.l` perturbation) | perturb `v`/`ht`/`m`/`step` ±5 %…±50 % across 6 restarts, keep first MS 1/2 | **all 6 restarts MS 5**, `done=0` — no convergence |
| **homotopy** (proximal continuation) | `proximal_perturbation` `mu: 1e3 → 0` (7 steps), warm-restart from each prior point, fresh `path.opt`/step | **all 7 steps MS 5**, INFES ~458–467 (no monotone drive) |

Neither converges. Combined with Task-4's PATH-option result (INFES 477 → 382 best, no config crosses even from the NLP optimum), rocket's MS-5 is **intrinsic non-convergence** — the ill-conditioned `1/ht²`,`1/m²` initial Jacobian of the Goddard rocket. The survey's a-priori held: warm-starting from the optimum already fails, so perturbed restarts / regularization schedules are unpromising.

### REPLAN + scaffold hardening

- **rocket's +1 Solve REPLANs to the Sprint-31 PATH consultation** (`ISSUE_1462` Day-3 decision block). Scoped hand-off: *which PATH option set / regularization schedule / reformulation converges the division-by-variable optimal-control MCP?* The firm parts (the P8 scaffold + the hand-off) landed Day 2–3.
- **Scaffold hardening (the freed-budget deliverable):** the `--force homotopy` strategy now emits the **model-agnostic `proximal_perturbation` continuation** (`mu: 1e3 → 0` via a runtime-rewritten `path.opt`) — a *working* lever, not the Day-2 placeholder relaxation hook. Validated to run on rocket (compiles clean, executes the 7-step schedule). `src/emit/forcing.py` + the homotopy unit test updated; `make typecheck/format/lint/test` green.

### Day-3 outcome

rocket's +1 Solve deferred to Sprint 31 (no metric change — Solve 107 / Match 92 hold; the +2-Solve target's rocket half is now formally at Sprint 31, as the Task-6 assessment anticipated). The forcing scaffold is hardened (homotopy = a real generic lever). Next: **Day 4 — P3 hhfair widened-VARIABLE `$184` fix** (the last live +Match; the freed rocket budget flows here).
