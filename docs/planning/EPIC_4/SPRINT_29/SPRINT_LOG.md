# Sprint 29 Log

**Sprint:** 29 (Sprint 28 carryforwards + cold-convex robustness + AD/KKT backlog + Epic-5 scoping)
**Plan:** `PLAN.md` · **Prompts:** `prompts/PLAN_PROMPTS.md` · **Baseline:** `BASELINE_METRICS.md`
**Day-0 baseline (= Sprint 28 final):** Parse 142 · Translate 135 · Solve 107 · Match 92 · model_infeasible 7 · Tests ~4,935.
**Targets:** Solve ≥ 109 (mine + rocket, both REPLAN-gated) · Match maintain ≥ 92 / stretch ≥ 96 (genuine floor 68 → up) · model_infeasible ≤ 5 · Translate ≥ 135 · Tests ≥ 4,960 · determinism ×3 seeds.

## Cumulative Metrics Tracker

| Metric | Day 0 | Day 5 (CP1) | Day 10 (CP2) | Day 13 (final) | Target |
|---|---|---|---|---|---|
| Solve | 107 | — | — | — | ≥ 109 |
| Match (as-measured) | 92 | — | — | — | ≥ 92 / stretch 96 |
| Match (genuine floor) | 68 | — | — | — | 68 → up (cold-robustness) |
| model_infeasible | 7 | — | — | — | ≤ 5 |
| Translate | 135 | — | — | — | ≥ 135 |
| Tests | ~4,935 | — | — | — | ≥ 4,960 |

---

## Day 3 — Priority 4/7: cold-convex Class-A — maxmin objvar multi-model scoping fix (#1447) (2026-06-29)

**Scope:** start the cold-convex Class-A + offset-alias shared fix. Landed the maxmin objvar half; the offset-alias half (himmel16/polygon + maxmin's residual) is Day-4 continuation.

### Root cause refined (a 2nd PR24-style correction)
The Day-0 trace corrected the prep hypothesis (dropped term = objective gradient `-1`, not the constraint sum). Day-3 refined it further: the `-1` is a **multi-model objective-scoping bug**. maxmin declares 4 models sharing objvar `mindist`; the solved model `maxmin1a / mindist1a /` has only the indexed `=l=` constraint, so the objective is the **bare objvar** `mindist` (gradient `-1`). But `find_objective_expression` (`src/ad/gradient.py`) scanned **all** equations and matched `mindist2.. mindist =e= smin(low, dist)` from the *unsolved* `maxmin2`, differentiating `smin(low, dist)` (no `mindist`) → the `-1` vanished.

### Fix — `src/ad/gradient.py` (#1447)
`find_objective_expression`'s Case-2 defining-equation search is now scoped to `model_ir.get_solved_model_equations()` (None → search all, the single-anonymous-model fallback). `stat_mindist` now emits `-1 + sum(low, lam_mindist1a) = 0`; harness `stat_mindist` residual **1.0 → 0**.

### Blast radius — maxmin golden ONLY
Golden-staleness over **159 goldens**: exactly **1 drifted — `maxmin_mcp.gms` (+5 bytes**, the `-1 +`), 0 others, 0 failed. Surgical. maxmin matches warm → **Match-neutral genuine-floor lift**. 2 unit tests (`tests/unit/ad/test_objective_expr_model_scoping.py`: scoped-to-solved-model returns bare objvar; control where the `=e=` def IS in the solved model still uses it).

### Not yet Case a — 2nd residual exposed → Day 4
Clearing `stat_mindist` exposed `stat_point(p6,x)` rel **0.312** — the offset-alias cross-term enumeration over the `low(n,nn)` pair subset (the `_diff_sum`/`_try_diff_sum_offset_crossterms` class shared with himmel16 `stat_area` 2.0 / polygon `stat_theta` 0.49). **himmel16/polygon are unchanged** by today's fix (confirmed) — their bug is purely offset-alias. That fix threads the #1387/#1111/#1112 AD core → **Day-4 work under the Unknown 7.2 REPLAN gate**.

### Decision
Day-3 lands the maxmin objvar-scoping fix (correct, isolated, verified). The offset-alias fix (maxmin `stat_point` + himmel16 + polygon) is the substantive **Day-4** deliverable, where the PROCEED/REPLAN call on threading the alias-AD core is made. **No metric change** (all Class-A models match warm).

---

## Day 2 — Priority 2 #1462: rocket residual → **REPLAN to Sprint 30** (2026-06-29)

**Scope:** resolve the residual MS-5 question (Unknown 2.2) — is the post-warm-start MS 5 a localizable emit/warm-start fix (PROCEED) or intrinsic non-convexity (REPLAN)? **No `src/` change** (the warm-start landed Day 1; the Day-2 probe was a diagnostic that didn't pan out, so nothing new is landed). Docs-only.

### Experiments
- **Complete `_fx_`-at-`h0` warm-start (already in from Day 1 — all ht/v/m):** solving `rocket_mcp_presolve.gms` → embedded NLP **MS 2** (obj **1.00412** ≈ NLP ref 1.0128) but the MCP `mcp_model` → **MS 5 (Locally Infeasible)**, PATH `** EXIT - other error` at the **initial Jacobian** (1307 elements, 903 nonlinear).
- **Degenerate-bound suppression probe (the prescribed Day-2 experiment):** the lone degenerate fix is **v('h0')=0** (fixed value = relaxed lower bound 0; ht/m fix to 1 ≠ bound 0). Suppressing the redundant `v_fx_h0` `_fx_` equation + pinning v('h0')=0 by bound → **still MS 5**, identical `EXIT - other error`, identical NLP obj. **The degeneracy is not the MS-5 driver.**
- **Residual not cleanable by warm-start value:** the harness residual moves with the warm-start value (`nu_*_fx=0` → `stat_step` 0.497; `=var.m` → `stat_ht(h0)` 1.00; negating only flips the sign) — the transferred NLP duals don't make the NLP point an exact MCP KKT point (the **Case-c boundary** for this non-convex model: bilinear + division-by-variable + nonlinear-equality). Converging NLP + non-converging MCP-from-warm-point = **intrinsic non-convergence**.

### Decision — REPLAN to Sprint 30
Both prescribed interventions (complete warm-start + degenerate-bound suppression) leave rocket at **MS 5**; the operational gate (PROCEED iff MS 1) is not met. **REPLAN to Sprint 30 forcing** (trust-region / homotopy / perturbed-restart). The Day-1 `_fx_` warm-start **stays** as firm presolve robustness; rocket's **+1 Solve / +1 Match is DEFERRED to Sprint 30** (`ISSUE_1462` → REPLAN-DEFERRED). **Freed ~4–8 h → Day-8 hhfair (Priority 6).** Unknown 2.2 resolved. **No metric change** (rocket was already `not_tested`/MS 5).

---

## Day 1 — Priority 2 #1462: `_fx_`-multiplier presolve warm-start (2026-06-29)

**Scope:** land the **general** `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` `_fx_`-multiplier warm-start in the presolve dual transfer — sprint-wide presolve robustness, firm regardless of rocket's Day-2 outcome.

### Implementation
`src/emit/emit_gams.py`: new `_emit_presolve_fx_warmstart(kkt, suppressed_fx, add_comments)` helper, called at the end of `_emit_nlp_presolve`'s dual-transfer block. It iterates `var_def.fx_map` and emits `nu_<var>_fx_<idx>.l = <var>.m(<idx>);` for exactly the active `_fx_` multipliers, mirroring `_emit_presolve_fx_unfix`'s `eq_paired_in_mcp` gate (`in equalities` ∧ not suppressed ∧ referenced). The general transfer loop skipped these because the `_fx_` equations are not original NLP equations — the NLP fixes the column via `.fx`, so the fix dual surfaces as the *variable* marginal, not an equation marginal.

### Blast radius — exactly the 4 Layer-4-unfix models, additive-only
`grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms` → **chain / cclinpts / otpop / rocket** (the only presolve goldens with `_fx_` multipliers). Each golden diff is purely additive (the new warm-start block): chain `nu_x_fx_i0/i50`, cclinpts `nu_b_fx_s1/s30`, otpop `nu_x_fx_1974`, rocket `nu_v_fx_h0/nu_ht_fx_h0/nu_m_fx_h0` — **16 inserted lines, nothing else changed.**

### Zero regression — proven
- **Cold MCP files BYTE-IDENTICAL** for all 4 (the change is inside `_emit_nlp_presolve`, presolve-only). The committed DB solves these via the **cold** file (`mcp_file_used=None`: otpop/cclinpts match, chain mismatch, rocket not_tested), so the DB Solve/Match results are unaffected by construction.
- **All 4 presolve goldens compile clean** (`gams action=c`, 0 errors); rocket + otpop also solve via the harness without abort.

### Rocket residual — necessary-but-insufficient (Day-2 question), as the gate predicted
Harness on rocket *with* the warm-start: the max-residual row **moved** from `stat_step` rel 0.497 → `stat_ht(h0)` rel 1.00 (a `_fx_` element row). Negating the transfer only flips the sign of the same magnitude, so this is **not** a sign error — the `_fx_` warm-start alone leaves a residual at the fixed element, exactly the **necessary-but-insufficient** finding from the Sprint-28 Day-13 diagnosis (obj 1.137 → 1.016, MS 5 persists). The residual `piL/piU`-at-`h0` interaction is the **Day-2 PROCEED/REPLAN question** (Unknown 2.2). Day-1 does **not** claim rocket is fixed.

### Tests + gate
3 new unit tests (`tests/unit/emit/test_presolve_fx_warmstart.py`: helper emits the line for a fixed boundary element; empty for a fix-free model; appears in the full `--nlp-presolve` emit). Goldens regen'd; golden-staleness + quality gate green. **No Solve/Match metric change** (firm robustness landed; rocket's +1 is the Day-2 decision).

## Day 0 — Kickoff + Day-0 Traces (2026-06-29)

**Scope:** baseline confirmation + Day-0 `kkt_residual.py` traces (PR24) for the REPLAN-prone + lead tracks; fill each Phase-0 gate's `Traced Fix-Surface (Day-0)` line. **No `src/` change** (per the Day-0 prompt). Docs-only.

### Baseline gate — PASS
`git diff 803a259a..HEAD -- src/ scripts/` is **empty** → `src/` + `scripts/` are byte-identical to the Sprint-28 baseline commit, so the committed `gamslib_status.json` stands as the Day-0 baseline (Solve 107 / Match 92 / model_infeasible 7). No fresh retest (Unknown 8.3 ✅). **Tooling (Task 6):** the KKT-residual harness, divergence detector, and golden-staleness gate are present and audited-ready — no Day-0 extension.

### Day-0 harness verdicts — all 8 RE-CONFIRMED vs the prep-time (Task 4) Day-0 status

| Track | Model | Verdict | max-residual row | rel | Prep | Note |
|---|---|---|---|---|---|---|
| P1 #1443 | mine | Case b | `stat_x(4,1,1)` | 1.33 | 1.333 | ✅ convex LP, dual-transfer CONSISTENT |
| P2 #1462 | rocket | Case b | `stat_step` | 0.497 | 0.497 | ✅ `_fx_`-at-`h0` warm-start absent |
| P4/P7 #1447 | maxmin | Case b | `stat_mindist` | 1.00 | 1.000 | ✅ **hypothesis corrected** (see below) |
| P4/P7 #1146 | himmel16 | Case b | `stat_area(1)` | 2.00 | 2.000 | ✅ cyclic + objvar-gradient sign |
| P4/P7 #1143 | polygon | Case b | `stat_theta(i12)` | 0.492 | 0.492 | ✅ dropped offset-image cross-term |
| P4 (Class-A) | like | Case b | `stat_p(three)` | 2.00 | 2.0 | ✅ folds into the Class-A lead (#1447) |
| P4 (Class-A) | catmix | Case b | `stat_x1(0)` | 0.952 | 0.95 | ✅ folds into the Class-A lead |
| P6 #1236 | hhfair | **ERROR** (blocker) | — | — | `$141`/`$257` | ✅ blocker reproduced + root localized |

Every prep verdict held on current `main` — **no drift**. JSON reports in `/tmp/day0_<model>.json`.

### Traced fix-surfaces (PR24) — filled in each Phase-0 gate
- **mine #1443:** three sites pinned — `stat_x` cross-term (landed #1224) `src/kkt/stationarity.py:5562-5570`; presolve dual transfer `src/emit/emit_gams.py:1281` (`lam_pr.l = abs(pr.m)`, same-index, sign-discarding); `comp_pr` head var `x(l+1,i,j)`. Residual is in the LP row despite consistent dual transfer → the `l+1`/`±li`/`±lj` correspondence is not aligned across the three sites (corroborates Task-5 lean-REPLAN).
- **rocket #1462:** `nu_*_fx_h0` declared + used in `stat_ht/m/v` but the presolve dual-transfer block (`emit_gams.py:1281-1310`) emits **no `nu_*_fx_*` init** → starts at 0 → `stat_step` residual. Layer-4 unfix `_emit_presolve_fx_unfix` at `emit_gams.py:1090`.
- **maxmin #1447 — ⚠️ prep hypothesis CORRECTED (PR24 catch):** the dropped term is the **objective gradient `-1`** (maxmin maximizes `mindist`), not the constraint sum (the `sum((n,nn)$low, lam_mindist1a)` **is** present). Surface: the objvar stationarity assembly in `src/kkt/stationarity.py` (`build_stationarity_equations`:2090 → `_build_indexed_stationarity_expr`:2650 / objective-gradient merge :2222).
- **himmel16 #1146:** two candidate surfaces (root disambiguates Day 3) — (a) cyclic `i++1` decomposed into `i+5`$(ord≤card-5)+`i-1`$(ord>1) in `stat_x`/`stat_y` (`derivative_rules.py` circular branch ~:1866); (b) the `stat_area` `-1` objvar-defining gradient interacting with the signed `nu_areadef` transfer (raw −2.0). Integer 2.0 = 2× maxmin's 1.0.
- **polygon #1143:** clean **dropped predecessor offset-image cross-term** — `stat_theta` has the own-row gradient but not the `+0.5*r(i)*r(i-1)*cos(...)` term from the `i-1` row (where `theta(i+1)` resolves to `theta(i)`). Surface: `derivative_rules.py` non-circular successor branch (~:1989/:2022) over `j(i+1)`.
- **hhfair #1236:** `$141` blocker reproduced (13 errors); root = the dual-transfer block emits multiplier inits over the **widened `tl` domain** (`nu_budget.l(tl) = -(budget.m(tl))`) reading unpopulated `.m('0')` (set split `tl /'0'..'3'/` vs active `t /'1'..'3'/`, propagated by the domain-widened `n(tl)`). Fix surface = restrict the transfer to the active subset (`emit_gams.py:1281-1310`); verdict gated on the Day-8 compile fix.

### PR25 Day-0 tally (genuine vs methodology)
- **As-measured baseline:** Solve 107 · Match 92 (= **genuine 68 + ~24 methodology**).
- **Firm headline path:** mine (#1443) + rocket (#1462), both `model_infeasible`/MS-5 → Solve, **both REPLAN-gated** (Task 5). hhfair (#1236) the lone live +Match (gated on the compile fix).
- **Cold-convex Class-A (maxmin/himmel16/polygon/like/catmix):** all **Case b but already match warm** → **Match-neutral genuine-floor lift** (68 → up), not as-measured Match.
- **No `src/` change today** → metrics unchanged from baseline.

### Deliverables
6 Phase-0 gates updated (`docs/issues/ISSUE_{1443,1462,1447,1146,1143,1236}_*.md`) + this Day-0 SPRINT_LOG entry. Docs-only; no quality-gate-relevant source touched.
