# Sprint 25 Detailed Plan

**Created:** 2026-04-22
**Sprint Duration:** 15 days (Day 0 – Day 14)
**Effort:** ~57.5–77.5 hours (Priority 1 19–26h + Priority 2 23–33h + Priorities 3–4 7.5–9.5h + Day 1 PR12 landing 2–3h + retest/close ~6h); Budget ~4–5.5h/day effective capacity
**Risk Level:** MEDIUM-HIGH (alias-AD workstream has history of regressions; mitigated by 4-phase rollout + 4 quantitative gates + 5 stop-the-sprint triggers from `DESIGN_ALIAS_AD_ROLLOUT.md`)
**Baseline:** `main @ fc038801` — Parse 143/143 (100%), Translate 135/143 (94.4%), Solve 99, Match 54, Tests 4,522 (Sprint 24 Day 14 final). Scope LOCKED at 143 per Sprint 24 retrospective PR15 and `BASELINE_METRICS.md` §5.

---

## Executive Summary

Sprint 25 executes Sprint 24's 11 alias-AD carryforward issues + 7 emitter backlog issues + 4 recovered-translate bugs, with a parallel determinism-invariant test infrastructure landing Day 1. The sprint is scheduled in 4 phases (Task 6 rollout) with 2 checkpoints (Day 6, Day 10). The alias-AD architecture is already live (Sprint 23 base layer + Sprint 24 additions — see `AUDIT_ALIAS_AD_CARRYFORWARD.md`); Sprint 25's work is **extending `_partial_collapse_sum` multi-index concrete→symbolic recovery** (Pattern A root cause) and **extending `_alias_match` for `IndexOffset.base`** (Pattern C).

- **WS1: Alias-AD (Priority 1, Days 2–12)** — 4 phases with Gates 1–4; cumulative Match ladder ≥+3/+5/+6 at each gate.
- **WS2: Emitter backlog (Priority 2, Days 2–10 parallel)** — 3 batches for #1275–#1281 + 4 new issues #1289–#1292; `#1289 ganges` is Day 4 focus (highest single-fix leverage).
- **WS3: Determinism infrastructure (Day 1)** — Option D grammar fix (Task 3) + PR12 test harness (Task 10); must land before any metric-affecting PR.
- **WS4: Small priorities (Days 11)** — #1270 multi-solve gate extension + #1271 dispatcher refactor.
- **WS5: Pipeline retest & close (Days 13–14)** — full pipeline + retrospective.

**Process requirements (carried forward from Sprint 23/24 retrospectives):**
- **PR6:** Full pipeline for all definitive metrics (`scripts/gamslib/run_full_test.py --quiet`).
- **PR7:** Track model_infeasible gross fixes and gross influx.
- **PR8:** Absolute counts and percentages.
- **PR9:** Targets against 143-model pipeline scope (LOCKED per PR15).
- **PR10 (re-calibrated via Unknown 6.3):** Budget **30%** error influx for alias-AD recoveries (not the 100% PR13 figure — PR13 applies only to previously-timeout-excluded models; alias-AD bugs produce valid-but-wrong MCPs, a fundamentally different failure mode). Budget **80–100%** influx for Priority 2 emitter recoveries (they come from the same "latent emitter bug" category PR13 describes).
- **PR11:** Highest-leverage fix (alias-AD Phase 1) in Days 2–4.
- **PR12:** Determinism regression test — lands Day 1 (per `DESIGN_DETERMINISM_TESTS.md`).
- **PR13:** Unchanged — 100% influx budget applies to timeout recoveries.
- **PR14:** Known unknowns captured in `KNOWN_UNKNOWNS.md` before sprint start (done).
- **PR15:** Scope frozen at 143 pre-Day-0 (done per `BASELINE_METRICS.md`).

---

## Sprint 25 Targets

| Metric | Baseline (143-scope) | Target | Stretch | Rationale |
|---|---|---|---|---|
| Parse | 143/143 (100%) | ≥ 143/143 | — | Invariant. |
| Translate | 135/143 (94.4%) | ≥ 135/143 | ≥ 137/143 | 5 timeouts + `mine` deferred to Sprint 26 per Task 8 (srpchase + iswnm recoverable if Option 1 fix lands Day 11 overflow). |
| Solve | 99 | ≥ 102 | ≥ 105 | +3 via alias-AD (qabel/abel mismatched-value recoveries + 1 Pattern C); +1 via Priority 2 #1289 ganges unblock. |
| Match | 54 | ≥ 60 | ≥ 62 | +6 via Task 6 Match ladder; Gate 4 threshold. |
| path_syntax_error | 11 | ≤ 6 | ≤ 4 | Task 4 Batch 1 removes ~2 (#1275, #1280); Batch 2 removes ~2 (#1276, #1281); Batch 3 removes ~1 (#1291 clearlak statement ordering, landed Day 9); alias-AD influx ~1 budgeted. |
| path_solve_terminated | 10 | ≤ 9 | ≤ 8 | Pattern C (#1277 twocge offsets) removes 1; Priority 5 timeout work deferred. |
| model_infeasible | 8 | ≤ 6 | ≤ 4 | Pattern A fixes may recover chenery (#1177) + partial CGE; Category B (cesam, fawley, korcge) remains hard. |
| Tests | 4,522 | ≥ 4,560 | — | PR12 test harness adds 6 new tests + per-fix unit tests (~40 new). |

**Error influx budgets (Unknown 6.3 calibration — §Influx Calibration below).**

---

## Workstreams

### WS1: Alias-AD (Priority 1)

**Effort:** ~19–26h across 4 phases (per `DESIGN_ALIAS_AD_ROLLOUT.md`).
**Target:** Cumulative Match ladder +3/+5/+6/+6 at each gate; final Match ≥60; stretch ≥62.
**Source:** [`AUDIT_ALIAS_AD_CARRYFORWARD.md`](./AUDIT_ALIAS_AD_CARRYFORWARD.md), [`DESIGN_ALIAS_AD_ROLLOUT.md`](./DESIGN_ALIAS_AD_ROLLOUT.md).

| Phase | Focus | Issues | Days | Gate |
|---|---|---|---|---|
| 1 | Pattern A single-index validation + `_partial_collapse_sum` multi-index prototype (qabel, abel, launch) | — (architecture) | 2–4 | — |
| 2 | Pattern A across all 6 issues | #1138, #1139, #1140, #1142, #1145, #1150 | 5–6 | Gate 2 = Checkpoint 1 (Day 6) |
| 3 | Pattern C IndexOffset.base extraction + #1277 re-validation | #1143, #1146 (+ #1277) | 7–9 | Gate 3 (Day 9) |
| 4 | Final sweep + Pattern E routing + Checkpoint 2 | #1141, #1144, #1147 | 10–12 | Gate 4 = Checkpoint 2 (Day 10) |

**Regression canaries (per `AUDIT_ALIAS_AD_CARRYFORWARD.md` tier list):**
- **Tier 0 (non-negotiable):** `dispatch`.
- **Tier 1 (alias-using matching):** `quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge`, plus defensive `paklive` (non-alias).
- **Tier 2:** all 44 non-alias matching models — golden-file diff expected identical.

**Touched files:** `src/ad/derivative_rules.py` (`_partial_collapse_sum`, `_alias_match`), `src/kkt/stationarity.py` (`_apply_alias_offset_to_deriv`).

### WS2: Emitter Backlog (Priority 2)

**Effort:** ~23–33h across 3 batches + Task 5 recovered-translate fixes.
**Target:** 5+ path_syntax_error reductions; at least 1 Match gain (#1289 ganges).
**Source:** [`CATALOG_EMITTER_BACKLOG.md`](./CATALOG_EMITTER_BACKLOG.md), [`ANALYSIS_RECOVERED_TRANSLATES.md`](./ANALYSIS_RECOVERED_TRANSLATES.md).

| Batch | Focus | Issues | Effort | Days |
|---|---|---|---|---|
| 1 | presolve paths + UEL quoting | #1275, #1280 | 3–5h | 2–3 (parallel with WS1 Phase 1) |
| 2 | IR-normalize + emitter idempotency + turkpow line wrap | #1279, #1276, #1281, #1292 | 7–11h | 4–6 (parallel with WS1 Phase 2) |
| 2.5 | Ganges calibration stripping (highest-leverage single fix — unblocks ganges + gangesx, 2 of 5 Task 5 models) | #1289 | 4–6h | 4 |
| 3 | AD / stationarity (post-Pattern-C) + ferts identifier length + clearlak statement ordering | #1277, #1278, #1290, #1291 | 8–12h | 7–10 (parallel with WS1 Phase 3–4) |

**Touched files:** `src/emit/emit_gams.py` (#1275, #1280, #1281, #1292), `src/ir/normalize.py` (#1279), `src/kkt/stationarity.py` (#1277, #1278), new `_DeclaredSymbolTracker` helper.

### WS3: Determinism Infrastructure (Day 1)

**Effort:** ~4–6h (Option D fix 2–3h + PR12 test harness 2–3h).
**Target:** #1283 fix lands + byte-stability regression test CI-enforced.
**Source:** [`INVESTIGATION_PARSER_NON_DETERMINISM.md`](./INVESTIGATION_PARSER_NON_DETERMINISM.md), [`DESIGN_DETERMINISM_TESTS.md`](./DESIGN_DETERMINISM_TESTS.md).

- **Option D fix:** Extend `_resolve_ambiguities()` in `src/ir/parser.py:166–225` with a greediest-value `table_row` heuristic. Expected regression surface: LOW.
- **PR12 test harness:** 5 fixtures (chenery, indus89, abel, partssupply, ps2_f) × 5 seeds [0, 1, 42, 12345, 99999]; new `determinism` pytest marker; `tests/integration/test_pipeline_determinism.py`; new `.github/workflows/nightly.yml` for full-corpus nightly sweep.
- **Ordering constraint:** Option D MUST land before PR12 test enables (else CI stays red on chenery).

### WS4: Small Priorities (Day 11)

**Effort:** ~7.5–9.5h combined (per `DESIGN_SMALL_PRIORITIES.md`).
**Target:** saras-style model flagged by extended multi-solve gate; dispatcher refactor with zero byte-diff regression.

- **#1270 gate extension (3.5–4.5h):** Approach A cross-reference — flag `eq.m` reads whose receiving parameter later appears in another declared model's constraint body. Code site `src/validation/driver.py:151–225`. 4-fixture test matrix with explicit expected outcomes: **only saras-style feedback cases flag**; post-solve reporting MUST NOT flag; multi-stage display MUST NOT flag; partssupply `var.l` MUST NOT flag. Canaries: `gussrisk, sparta` (MUST NOT flag — currently matching); `saras` (MUST flag).
- **#1271 dispatcher refactor (4–5h):** Unified signature `_loop_tree_to_gams(node, *, token_subst=None)`. Byte-diff regression test: snapshot 135 currently-translating models pre-refactor (PYTHONHASHSEED=0), regenerate post, `diff -r` must be empty.

### WS5: Pipeline Retest and Close (Days 13–14)

**Effort:** ~6h.

| Day | Task |
|---|---|
| 13 | Full pipeline retest (per PR6); acceptance-criteria evaluation against §Sprint 25 Targets; error-influx accounting (per PR7, PR10 re-calibrated). |
| 14 | Sprint retrospective; CHANGELOG updates; PROJECT_PLAN KPIs; Sprint 26 carryforward issue filing. |

---

## Influx Calibration (Unknown 6.3)

**Finding:** The Sprint 24 retrospective's PR13 "100% influx" finding was specific to **previously-timeout-excluded models** (5 models: ganges, gangesx, ferts, clearlak, turkpow went 5/5 to `path_syntax_error` after translate recovery). This category is dominated by latent emitter bugs that also slow translation — their failure mode is "valid emission is broken."

Alias-AD recoveries are a **different failure mode**: the MCP structure is syntactically valid; only the derivative values are wrong. When an alias-AD fix lands, the recovered model produces valid GAMS that typically compiles and either solves correctly (best case → Match gain) or hits a PATH solver-convergence issue (`path_solve_terminated`). It rarely produces new `path_syntax_error` unless the fix itself introduces an emission bug (Sprint 24 Day 5 `a(n+1,n)` → `a(np+1,n)` episode, caught in-sprint).

**Calibrated Sprint 25 influx budgets:**

| Recovery source | Influx rate | Rationale |
|---|---|---|
| Alias-AD (Priority 1) | **30%** | 1 per ~3 recoveries. Worst-case absorbs one accidental emitter regression like the Sprint 24 Day 5 Error 125 episode. Well below PR13's 100% because the failure mode is different. |
| Priority 2 emitter (recovered-translates #1289–#1292) | **80–100%** | These are PR13's category — latent emitter bugs that also previously caused failure. Same dynamics expected. |
| Priority 2 emitter (existing matching models — #1275, #1276, #1280, #1281, #1279) | **10–20%** | These fix bugs in currently-matching models; influx limited to accidental regression. |
| Priority 3 multi-solve gate | **0%** (by construction) | Gate only excludes; cannot introduce new errors on kept models. |

**Verification Status:** Unknown 6.3 — ✅ VERIFIED via `../SPRINT_24/SPRINT_RETROSPECTIVE.md` §2 and `../SPRINT_24/SPRINT_LOG.md` Days 3–5; PR10 split into two sub-budgets (alias-AD 30% vs emitter-recovered 80–100%).

---

## Daily Schedule

### Day 0 — Setup & Kickoff
- Verify baseline metrics match `BASELINE_METRICS.md` (Parse 143, Translate 135, Solve 99, Match 54).
- Generate Tier 1 + Tier 2 golden files for WS1 canary work (`dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive`, plus the 44 Tier 2 non-alias matching set).
- Initialize `SPRINT_LOG.md` Day 0 entry.

### Day 1 — WS3 Determinism Landing
- Implement Option D fix in `src/ir/parser.py::_resolve_ambiguities` (greediest-value `table_row` heuristic).
- Re-run the 20-seed sweep on chenery — expect 20/20 byte-identical.
- Land PR12 test harness: register `determinism` marker, create `tests/integration/test_pipeline_determinism.py`, create `.github/workflows/nightly.yml`.
- Verify fast suite cost delta ≈ +60s; stays under 5-minute CI budget.

### Day 2 — WS1 Phase 1 Start + WS2 Batch 1 Start (parallel)
- **WS1:** Add debug logging to `_diff_varref` and `_partial_collapse_sum`. Translate qabel; trace derivative computation for the specific Pattern A cross-term. Identify the multi-index `_partial_collapse_sum` concrete→symbolic gap.
- **WS2 Batch 1 (fresh contributor or tail-end of Day 2):** Fix #1275 (presolve absolute paths) in `src/emit/emit_gams.py:889` `_emit_nlp_presolve`.

### Day 3 — WS1 Phase 1 Prototype + WS2 Batch 1 Complete
- **WS1:** Prototype `_partial_collapse_sum` multi-index extension. Validate on qabel (stationarity output changes). Run dispatch canary — MUST match.
- **WS2:** Fix #1280 (unquoted UEL dots). Run golden-file regression for all 54 matching models.

### Day 4 — WS1 Phase 1 Complete + WS2 Batch 2.5 (#1289)
- **WS1:** Validate on abel, launch. Run Tier 1 canary. Run `make test`. Quality gate.
- **WS2:** **High-leverage day** — fix #1289 (ganges/gangesx calibration-from-`.l` stripping). Per Task 5, this unblocks 2 of 5 recovered-translate models. Validate compile + solve + Match.

### Day 5 — WS1 Phase 2 Start + WS2 Batch 2 Start
- **WS1:** Apply Pattern A fix across #1138, #1139, #1140, #1142, #1145, #1150 candidate models. Measure Match/Solve delta per model.
- **WS2:** Fix #1279 (robustlp `defobj(i)` scalar-equation widening) in `src/ir/normalize.py`.

### Day 6 — Checkpoint 1 + WS2 Batch 2 Continue
- **Checkpoint 1 evaluation (end of Day 6):**

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Tier 0 canary (dispatch) | Identical | Identical | Any diff |
| Tier 1 canary regressions | 0 | ≤ 1 | > 1 |
| Pattern A improvement (Match/Solve on #1138/1139/1140/1142/1145/1150) | ≥ 3 of 6 improved ≥50% | ≥ 1 improved | 0 improved |
| Cumulative Match delta | ≥ +3 | ≥ +1 | < 0 (regression) |
| Tests | All pass | All pass | Any failure |
| path_syntax_error | ≤ 10 | ≤ 11 | > 11 |

- **GO:** proceed to WS1 Phase 3 + WS2 Batch 2 completion.
- **CONDITIONAL GO:** extend Phase 2 into Day 7; slip Phase 3 start to Day 8.
- **NO-GO:** revert Phase 2 PRs; Day 7 is root-cause investigation; Phase 3 slips to Day 9.

- **WS2 Batch 2 continues:** #1276 (fawley duplicate `.fx`) + #1281 (lmp2 duplicate Parameter) using new `_DeclaredSymbolTracker` helper.

### Day 7 — WS1 Phase 3 Start + WS2 Batch 3 Setup
- **WS1 Phase 3:** Extend `_alias_match()` at `src/ad/derivative_rules.py:304–307` to handle `IndexOffset` with `_same_root_set(expr_idx.base, wrt_idx, aliases)`. Target models: polygon, himmel16 (#1143, #1146).
- **WS2:** Fix #1292 (turkpow `stat_zt` line wrap) — short emitter fix.

### Day 8 — WS1 Phase 3 Continue + WS2 Batch 3 Core
- **WS1:** Re-validate #1277 (twocge `stat_tz` mixed offsets) now that Pattern C infrastructure is live — per Task 4 this is partially subsumed by Pattern C.
- **WS2:** Fix #1278 (twocge `ord(r) <> ord(r)` tautology) in `src/kkt/stationarity.py`.

### Day 9 — Gate 3 + WS2 Batch 3 Completion
- **Gate 3 (end of Day 9):** Pattern C target (polygon, himmel16) improves ≥50% OR Pattern A not regressed AND #1277 resolved → GO to Phase 4.
- **WS2:** Fix #1290 (ferts identifier length) + #1291 (clearlak statement ordering).

### Day 10 — Checkpoint 2 + WS1 Phase 4 Start
- **Checkpoint 2 evaluation (end of Day 10):**

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Match | ≥ 60 | ≥ 58 | < 55 (regression) |
| Solve | ≥ 102 | ≥ 100 | < 99 (regression) |
| path_syntax_error | ≤ 7 | ≤ 9 | > 11 (regression) |
| model_infeasible | ≤ 7 | ≤ 8 | > 8 (regression) |
| Tier 0 + Tier 1 canaries | All match | ≤ 1 regression | > 1 regression |
| Tests | All pass | All pass | Any failure |

- **GO:** lock main; WS1 Phase 4 is cleanup + Pattern E routing (#1141, #1144, #1147) + optional stretch targets.
- **CONDITIONAL GO:** Phase 4 limited to cleanup; no new architectural changes.
- **NO-GO:** main locked; Day 11 revert offending PRs; Phase 4 cancelled.

### Day 11 — WS4 Small Priorities
- **#1270 gate extension (3.5–4.5h):** Implement + test matrix (saras flag + post-solve reporting + multi-stage display + partssupply `var.l` non-flag). Verify gussrisk/sparta remain un-flagged; verify saras is flagged.
- **#1271 dispatcher refactor (4–5h):** Snapshot 135 models → refactor → regen → `diff -r /tmp/pre /tmp/post` must be empty.

### Day 12 — Buffer / Overflow / Sprint-Close Prep
- Buffer for any Phase 4 / Priority 2 Batch 3 slippage.
- **Stretch (Priority 5 contingency):** per Task 8, srpchase + iswnm Option 1 fix (short-circuit empty-subset fallback in `src/ad/index_mapping.py::enumerate_equation_instances`, 4–6h effort; 0–2 Solve delta expected). Land ONLY if schedule has slack.
- File deferred-to-Sprint-26 issues (label `sprint-26`). Update `KNOWN_UNKNOWNS.md` with end-of-sprint discoveries.

### Day 13 — Final Pipeline Retest
- `scripts/gamslib/run_full_test.py --quiet` (~2h15m under doubled timeouts).
- Record definitive final metrics (per PR6). Cross-check against §Sprint 25 Targets.
- Error-influx accounting: categorize any new path_syntax_error / path_solve_terminated / model_infeasible against PR10 re-calibrated budgets.

### Day 14 — Sprint Close + Retrospective
- Write Sprint 25 Retrospective using Sprint 24 template.
- Update `CHANGELOG.md` with Sprint 25 Summary.
- Update `PROJECT_PLAN.md` Rolling KPIs.
- File Sprint 26 recommendations.

---

## Contingency Plans

### Risk 1: Alias-AD Regression on Tier 0/1 Canary (most likely)
**Trigger:** dispatch or any Tier 1 canary regresses post-WS1 PR.
**Action:** Immediate revert per `DESIGN_ALIAS_AD_ROLLOUT.md` stop-trigger #2; isolate root cause via alias-match vs offset-alias logging; narrow-scope re-land.
**Fallback:** If the pattern repeatedly regresses, defer that specific pattern to Sprint 26; focus on patterns that are safe.

### Risk 2: Priority 2 Batch 3 Post-Pattern-C Dependency Not Ready
**Trigger:** Pattern C (#1143, #1146) NOT landed by Day 9, so #1277 re-validation blocked.
**Action:** Drop #1277 Day 10 re-validation to Day 11 buffer; do not slip Sprint close.
**Fallback:** Defer #1277 to Sprint 26; note reason in retrospective.

### Risk 3: Checkpoint 1 NO-GO
**Trigger:** Day 6 Gate 2 NO-GO (see Checkpoint 1 table).
**Action:** Revert Phase 2 PRs; Day 7 is root-cause investigation day; Phase 3 slips to Day 9; Phase 4 effectively compressed into Day 10 only (Pattern E routing may be deferred to Sprint 26).
**Fallback:** Sprint pivots to Priority 2-only work; Match target lowered to ≥57.

### Risk 4: PR12 Catches a New #1283-Class Bug Mid-Sprint
**Trigger:** PR12 nightly sweep flags a non-chenery corruption on Day 2+.
**Action:** File new issue `multi_row_label_ambiguity_<model>`; extend Option D pattern to cover it; re-run nightly.
**Fallback:** If Option D doesn't generalize, skip the test for that model via temporary skipif, file Sprint-26 issue.

### Risk 5: Error Influx Above Budget
**Trigger:** Day 13 retest shows alias-AD influx >30% OR Priority 2 emitter-recovered influx >100%.
**Action:** Classify new errors; file Sprint 26 issues. If influx destroys Match gain (e.g., Match net-zero), document in retrospective as PR10 recalibration item for Sprint 26.

---

## Workstream to Issue Mapping

### WS1: Alias-AD
- **Pattern A (Phase 2):** #1138, #1139, #1140, #1142, #1145, #1150 — 6 issues, ~16 comparison-scope models.
- **Pattern C (Phase 3):** #1143, #1146 — offset-alias extension.
- **Pattern E (Phase 4 routing):** #1141 (B→E), #1144, #1147 — multi-solve driver route or stationarity-level.

### WS2: Emitter Backlog
- **Batch 1:** #1275 (presolve paths), #1280 (unquoted UEL dots).
- **Batch 2:** #1279 (robustlp scalar-widening), #1276 (fawley duplicate `.fx`), #1281 (lmp2 duplicate Parameter), #1292 (turkpow line wrap).
- **Batch 2.5:** #1289 (ganges calibration stripping) — Day 4 focus.
- **Batch 3:** #1277 (twocge mixed offsets), #1278 (tautology), #1290 (ferts identifier length), #1291 (clearlak statement ordering).

### WS3: Determinism
- #1283 (parser non-determinism): Option D fix + PR12 test harness.

### WS4: Small Priorities
- #1270 (multi-solve gate extension).
- #1271 (dispatcher refactor).

### WS5 (deferred to Sprint 26):
- Translation timeouts (#1169, #1185, #1192 family + #1228 + Task 8's 5 models): DEFER per Task 8 Priority 5 recommendation.
- `mine` (`internal_error` / `SetMembershipTest`): DEFER — same architectural fix.

---

## Unknown 6.3 Verification Summary

**Status:** ✅ VERIFIED via `../SPRINT_24/SPRINT_RETROSPECTIVE.md` §2 + `../SPRINT_24/SPRINT_LOG.md` Days 3–5.

- Sprint 23 `_alias_match` / `_same_root_set` / `_partial_collapse_sum` base layer + Sprint 24 Day 3–5 single-index-sum-collapse fix landed qabel and abel from mismatch/IOerror → `model_optimal` + mismatch-value (eventually Match via subsequent fixes). **No new `path_syntax_error` observed** after the Sprint 24 Day 5 Error 125 `a(n+1,n)` episode was resolved in-PR via alias-substitution.
- Final Sprint 24 Match delta: +5 (49 → 54); the 11 open alias-AD issues (#1138–#1147, #1150) are this sprint's highest-leverage remaining work.
- PR13 "100% influx" applies specifically to previously-timeout-excluded models (5/5 went to path_syntax_error); NOT representative of alias-AD dynamics.

**Sprint 25 decision:** PR10 split into two sub-budgets — alias-AD 30%, emitter-recovered 80–100%. Match target +6 calibrated against the 30% figure with one-model reserve.

---

## Related Documents

- Prep task deliverables (all merged to main): `AUDIT_ALIAS_AD_CARRYFORWARD.md`, `INVESTIGATION_PARSER_NON_DETERMINISM.md`, `CATALOG_EMITTER_BACKLOG.md`, `ANALYSIS_RECOVERED_TRANSLATES.md`, `DESIGN_ALIAS_AD_ROLLOUT.md`, `DESIGN_SMALL_PRIORITIES.md`, `PROFILE_HARD_TIMEOUTS.md`, `BASELINE_METRICS.md`, `DESIGN_DETERMINISM_TESTS.md`.
- Day-by-day execution prompts: `prompts/PLAN_PROMPTS.md`.
- Known unknowns + calibrated influx budgets: `KNOWN_UNKNOWNS.md`.
- Sprint 24 templates: `../SPRINT_24/PLAN.md`, `../SPRINT_24/prompts/PLAN_PROMPTS.md`.
