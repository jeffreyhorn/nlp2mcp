# Sprint 32 — Retrospective

**Sprint:** 32 (Weeks 29–30) — Sprint 31 Carryforward: mine Head-Offset 4th Site, sarf 4-D Stationarity, camcge Dual-Consistent Walras (Epic 5), rocket PATH-Consultation & Case-c Documentation
**Closed:** 2026-07-15 (Day 13)
**Day-0 anchor:** `4cbf8bff` (Sprint 31 close)

---

## 1. Outcome vs targets

| Target (`PROJECT_PLAN.md` §"Sprint 32") | Result | Status |
|---|---|---|
| Solve ≥ 109 | **107** | ✗ |
| Match maintain ≥ 92 (142-corpus) | **92** | ✅ |
| genuine floor ≥ 75 | **74** | ✗ |
| model_infeasible ≤ 5 | **7** | ✗ |
| Translate +1 → 136 (via sarf) | **135** | ✗ |
| Tests ≥ 5,080 | **5,085** | ✅ |
| Determinism ✅ ×3 `PYTHONHASHSEED` | ✅ {0,1,42} | ✅ |
| Parse 142 | **142** | ✅ |

**No headline KPI bucket moved.** Final 142-corpus: Parse 142 · Translate 135 · Solve 107 · Match 92 · genuine floor 74 · model_infeasible 7. The committed DB is **byte-unchanged since the S31 close `4cbf8bff`** (no bucket moved → nothing to persist).

## 2. What landed (firm)

Two genuine landings — both correct and valuable, neither moving a headline bucket:

1. **camcge P3 step-1 — the scalar-`fx` marginal warm-start transfer (a general nlp2mcp emit-correctness fix, `src/emit/emit_gams.py`).** `_emit_presolve_fx_warmstart` + `_emit_presolve_fx_unfix` now cover **scalar** `.fx` fixings (camcge `mps.fx`) as well as per-element `fx_map` fixings — the scalar case lived in `var_def.fx` (empty index tuple) and was skipped, leaving `nu_mps_fx` at 0. Result: camcge `stat_mps` CASE_B (rel 1.05) → **Case-a**. Any scalar-`.fx`-in-stationarity model benefits. **The `/tmp` control corrected the design's sign** (`= var.m` direct, not `-mps.m`).
2. **P5 — the objective-defining-intermediate-variable Case-c auto-classifier (`scripts/diagnostics/kkt_residual.py`).** `reclassify_objdef_case_c` reclassifies a CASE_B → `case_c_objdef` on D1 (the max-residual `stat_<var>` is the objective-defining intermediate variable, `nu_obj=±1`) ∧ D3 (cold-start reaches a spurious optimum — an *objective comparison*, since the cold MCP reaches MS-1 at a wrong local optimum). All four family members auto-flag (hhfair/irscge/lrgcge/moncge); the camcge guard holds. **ISSUE_1236 CLOSED**; the sign flip stays BANNED.

## 3. What we'd do differently / key lessons

1. **The Task-9 honest projection was borne out exactly.** Solve ≥ 109 needed BOTH mine [P1] AND camcge [P3]; both REPLAN'd → Solve held at 107. The genuine-floor ramp ≥ 75 was conditional on an emit-changing cold-match; every mover REPLAN'd/re-triaged → floor held at 74. Translate +1 rested solely on sarf [P2]; it REPLAN'd. **When every KPI mover is REPLAN-prone and the sprint is "implement against a banked root cause," a flat-KPI outcome is the modal result** — the value is the *de-risking*, not the bucket.
2. **The control-first discipline (PR24/PR27) paid off on every deep track — and repeatedly caught a *wrong banked premise before any bad ship*.** Five deep tracks REPLAN'd on control/probe evidence with **zero broken code shipped**: mine (the `N`-derivation closes `stat_x` by construction but yields MS-5 — wrong-sign `N` at 6 bound-active rows); camcge Walras (step-1-first + numéraire still MS-4); sarf (the 2-D gate fires but the 369K `task` columns enumerate elsewhere); fawley (the qsb/pbal `sameas` patch closes 96% of the residual but the MCP still diverges). Each `/tmp`/harness control ran **before** the `src/` change. **This is the sprint's real product: five precisely-pinned, control-confirmed root causes.**
3. **A banked "design" is still a hypothesis — two designs were materially wrong, caught by the control.** camcge's design proposed `nu_mps_fx.l = -mps.m`; the `/tmp` control showed the emitted `stat_mps` body is **+209.86**, so the DIRECT `= mps.m` is correct (`-mps.m` made it *worse*). mine's design proposed the `N`-derivation as sufficient; the control showed it produces an *infeasible negative bound multiplier* at 6 rows. **The prep-doc `file:line`/sign is a Day-0-re-confirm hypothesis (the standing PR24 lesson), now including the fix's *sign* and *sufficiency*, not just its location.**
4. **Front-loading the +Solve movers worked as designed** — mine (Day 1) and camcge (Day 5) both REPLAN'd by the Day-5 checkpoint, not Day 11, so the freed budget flowed to P6/P7 with the whole back-half of the sprint remaining. The schedule's front-load correctly surfaced the REPLANs early.
5. **P6 confirmed the "#1111/#1112 gate leaks" risk empirically.** The offset-alias structural candidates (cpack et al.) were false leads (already solve / emit-correct, CASE_A). fawley's genuine second-index bug (qsb/pbal missing the `sameas(cfq__,cf)` the mbal term has) is a *variable's-second-index-summed* shape the landed core doesn't cover — and even the 96%-closing patch leaves the MCP diverging. **Structural-shape audits over-generate candidates; the harness verdict (CASE_B vs CASE_A) is the real filter.**

## 4. Sprint 33 / Epic 5 carryforwards

Every REPLAN hands a **de-risked, control-confirmed** specification:

1. **mine #1443 → Sprint 33 (deeper head-offset bound-complementarity architecture).** The `N`-derivation closes `stat_x` by construction but produces a wrong-sign residual at **6 bound-active rows** (`x(1,3,{1,2,3})`, `x(3,1,2)`, `x(3,2,1)`, `x(4,1,1)`) requiring an infeasible negative bound multiplier → the emitted `stat_x` head-offset **cross-term** is inconsistent at bound-active rows (not a warm-start-value fix). Banked: the S31 IR foundation + `MINE_5TH_COUPLING_REPLAN.md`.
2. **camcge #1330 → Epic 5 (dual-consistent Walras numéraire).** Step 1 (`nu_mps_fx`) landed. Step 2: the consumption-weighted numéraire reaches **omega 191.7346 (correct allocation)** but MS-4 (residual Walras rank-deficiency on the accounting identities `gdp`/`depreq`/`hhsaveq`/`gruse`) — a per-model-numéraire-declaration Epic-5 item. Banked: `CAMCGE_WALRAS_REPLAN.md`.
3. **sarf #1385 → Sprint 33 (symbolic parametric `stat_task` emit subsystem).** The 2-D constraint gate (`_is_blowup_2d_condition_equation`, fires sarf-only) is necessary but insufficient — the 369K `task` columns enumerate via `acost3` + the variable path. The fix must eliminate the 369K-column materialization everywhere + emit one symbolic guarded `stat_task$taskposs` + `task.fx` with parametric cross-terms (a from-scratch subsystem). Banked: `SARF_TRANSLATE_REPLAN.md` + the working 2-D detector.
4. **fawley (P6) → Sprint 33 (#1111/#1112 second-index generalization).** `stat_bq` applies the `$(sameas(cfq__,cf))` second-index restriction to the mbal cross-term but not the qsb/pbal terms (over-sum). The `/tmp` sameas patch closes `max|stat_bq|` **473 → 18 (96%)** but a secondary residual + the MS-5 LP-convergence remain — the core's second-index gate must extend from the variable's-first-index to the variable's-second-index-summed shape. Banked: `P6_BACKLOG_RETRIAGE.md`.
5. **rocket #1462 → Sprint 33 (PATH consultation).** The finalized PATH-consultation input (concrete question + ruled-out-lever survey + `--force` scaffold) is packaged; rocket's +1 Solve is conditional on the consultation. Banked: `ROCKET_PATH_CONSULTATION_INPUT.md` (FINALIZED).
6. **hhfair + CGE cluster #1236 → CLOSED (documented Case-c).** Auto-classified `case_c_objdef`; handed to the Sprint-33 forcing/PATH work like rocket; 0 genuine floor (methodology).

**Also carried:** agreste (candidate Case-b with a double-`solve` driver scope caveat) + cesam/lnts (Case-c) stay banked (Task 10 §3).

## 5. Process notes

- **Genuine-floor ramp re-baselines to 74** at S32 close (footnote ⁸ projected ≥ 75). The S33 target should be **maintain ≥ 74** with the banked emit fixes (fawley qsb/pbal sameas, the #1111/#1112 second-index generalization) as the next levers.
- The Epic-4 `SUMMARY.md` skeleton was begun (Day 12) — one row per Sprint 18–35 — to complete at Epic-4 close.
- **13 PRs merged** (#1551–#1559, Day 0–13); every emit/diagnostic-touching day ran the quality gate; every REPLAN day was docs/control-only (no `src/`). No regression; determinism ✅ ×3.

---

**Document Created:** 2026-07-15
**Owner:** Sprint 32 Planning Team
