# Sprint 25 Detailed Plan

**Created:** 2026-04-22
**Revised:** 2026-04-24 (Day 5 evidence-driven pivot — see §Day 5 Pivot below)
**Sprint Duration:** 16 days (Day 0 – Day 15) — extended by 1 day from original Day 14 close to absorb the Pattern C ramp.
**Effort:** ~55–75h (reduced from original ~59.5–80.5h because Phase 2 broader Pattern A rollout is dropped; Pattern C prototype + validation replaces it); Budget ~4.0–5.5h/day effective capacity.
**Risk Level:** MEDIUM (reduced from MEDIUM-HIGH — the risky 4-phase alias-AD rollout is trimmed to Phase 1 validation only + a targeted Pattern C pivot with narrower scope).
**Baseline:** `main @ fc038801` — Parse 143/143 (100%), Translate 135/143 (94.4%), Solve 99, Match 54, Tests 4,522 (Sprint 24 Day 14 final). Scope LOCKED at 143 per Sprint 24 retrospective PR15 and `BASELINE_METRICS.md` §5.

---

## Day 5 Pivot (2026-04-24) — Executive Summary of the Mid-Sprint Revision

The Day 5 investigation (`DAY5_PATTERN_A_INVESTIGATION.md`, PR #1305) examined the three Phase 1 target models — qabel, abel, launch — whose rel_diff mismatches were the originating justification for the Pattern A workstream (WS1).

**Finding:** None of the three models has a Pattern A bug. Their rel_diff is driven by KKT stationarity assembly, not the AD layer.

- **qabel / abel (rel_diff 0.08, 0.30):** AD criterion derivative is byte-correct (symmetric quadratic form verified). The mismatch, if real, lives in the stateq Lagrangian term's sign / offset / domain-condition handling, which uses a specific `nu_stateq(n, k-1)$(ord(k) > 1)` form that may be deliberate given the emitter's shifted-domain convention. Resolution requires a full PATH solve (`action=c` hits pre-existing Error 141 cascades on dual-transfer lines, blocking compile-only verification).
- **launch (rel_diff 0.17):** The `stat_iweight` emission shows phantom `s+1, s+2, s-1, s-2` IndexOffsets on an alias `ss` that has **no offset in the source** (`sum(ss$ge(ss,s), ...)`). This is **Pattern C (alias-of-IndexOffset)** manifesting in the KKT stationarity emitter as an "expand the alias via ±N offsets" strategy. Pattern A fix in `_partial_collapse_sum` doesn't touch this code path.

**Consequences for the sprint:**

- **Phase 2 (broader Pattern A rollout, original Days 5–6): DROPPED.** The Phase 1 hypothesis — "multi-index concrete→symbolic recovery in `_partial_collapse_sum` unblocks #1138/1139/1140/1142/1145/1150" — is orthogonal to the bug surface we actually see.
- **Pattern C moves EARLIER.** Formerly Phase 3 (Days 7–9), the Pattern C work is now Days 6–7, targeting launch's `stat_iweight` phantom-offset enumeration in `src/kkt/stationarity.py`.
- **A "Pattern A cohort sanity sweep" is added (Day 7).** Before declaring Pattern A dead, we re-inspect the other six Pattern A candidate models (#1138, #1139, #1140, #1142, #1145, #1150) to confirm they exhibit the same symptom shape (AD correct, bug elsewhere) and are not genuinely blocked by the `_partial_collapse_sum` gap.
- **qabel/abel resolution moved to Day 8** via full PATH solve (not `action=c`) to separate nonconvex-solver noise from emission bugs.
- **Sprint extended 1 day** (Day 14 → Day 15) to absorb the Pattern C prototype ramp. WS2 (emitter backlog) is otherwise unchanged; WS4 (small priorities) moves from Day 11 → Day 12.

Gate 1 (Phase 2 GO/NO-GO) and Checkpoint 1 (Day 6 Phase 2 evaluation) are therefore **CANCELLED** — the gate criteria assumed Phase 2 was real. Checkpoint 2 (Match/Solve/path_syntax_error evaluation) moves from Day 10 → Day 11 and retains its GO/NO-GO role for Phase E routing.

---

## Executive Summary

Sprint 25 originally scoped 11 alias-AD carryforward issues + 7 emitter backlog issues + 4 recovered-translate bugs, with a parallel determinism-invariant test infrastructure landing Day 1. After the Day 5 pivot, the sprint focuses on:

- **WS1: Alias-AD (Priority 1, Days 2–4 DONE; Days 6–8 Pattern C + cohort sweep)** — Phase 1 validation (DONE, landed `_find_var_indices_in_body` mechanical port without behavioral change); Pattern C pivot targets launch's `stat_iweight`; Pattern A cohort sanity sweep Day 7; qabel/abel PATH-solve Day 8.
- **WS2: Emitter backlog (Priority 2, Days 2–4 DONE; Days 8–11 remainder)** — Batch 1 (#1275, #1280) DONE; Batch 2.5 (#1289 ganges) DONE; Batch 2 remainder (#1279, #1276, #1281, #1292) Days 8–9; Batch 3 (#1277, #1278, #1290, #1291) Days 10–11.
- **WS3: Determinism infrastructure (Day 1 DONE)** — Option D grammar fix + PR12 test harness landed in PR #1301.
- **WS4: Small priorities (Day 12)** — #1270 multi-solve gate extension + #1271 dispatcher refactor.
- **WS5: Pipeline retest & close (Days 14–15)** — full pipeline + retrospective.

**Process requirements (carried forward from Sprint 23/24 retrospectives):**
- **PR6:** Full pipeline for all definitive metrics (`scripts/gamslib/run_full_test.py --quiet`).
- **PR7:** Track model_infeasible gross fixes and gross influx.
- **PR8:** Absolute counts and percentages.
- **PR9:** Targets against 143-model pipeline scope (LOCKED per PR15).
- **PR10 (re-calibrated via Unknown 6.3):** Budget **30%** error influx for alias-AD recoveries (not the 100% PR13 figure — PR13 applies only to previously-timeout-excluded models; alias-AD bugs produce valid-but-wrong MCPs, a fundamentally different failure mode). Budget **80–100%** influx for Priority 2 emitter recoveries (they come from the same "latent emitter bug" category PR13 describes).
- **PR11:** Highest-leverage fix (originally alias-AD Phase 1) in Days 2–4. Post-pivot: #1289 ganges (landed Day 4) is the highest-leverage single fix, and Pattern C is the new Phase 1 equivalent at Days 6–7.
- **PR12:** Determinism regression test — lands Day 1 (per `DESIGN_DETERMINISM_TESTS.md`) — DONE.
- **PR13:** Unchanged — 100% influx budget applies to timeout recoveries.
- **PR14:** Known unknowns captured in `KNOWN_UNKNOWNS.md` before sprint start (done).
- **PR15:** Scope frozen at 143 pre-Day-0 (done per `BASELINE_METRICS.md`).

---

## Sprint 25 Targets (Revised Post-Day-5)

| Metric | Baseline (143-scope) | Target (Revised) | Stretch | Rationale |
|---|---|---|---|---|
| Parse | 143/143 (100%) | ≥ 143/143 | — | Invariant. |
| Translate | 135/143 (94.4%) | ≥ 135/143 | ≥ 137/143 | 5 timeouts + `mine` deferred to Sprint 26. |
| Solve | 99 | ≥ 100 | ≥ 102 | +1 from #1289 (landed Day 4 — ganges/gangesx unblock). Pattern C may add +1 (launch) if the fix passes regression. Pattern A Phase 2 dropped — previously projected +3 removed. |
| Match | 54 | ≥ 56 | ≥ 58 | +2 from Pattern C on launch + qabel (IF Day 8 PATH solve shows emission bug, not nonconvex noise). +2 stretch if cohort sweep finds another Pattern-C-shaped bug. Pattern A Phase 2 dropped — previously projected +5 removed; the +6 Match ladder is no longer the gate. |
| path_syntax_error | 11 | ≤ 7 | ≤ 5 | #1275 + #1280 (DONE Days 2–3) removed ~2; Batch 2 (#1276, #1281) targets ~2 more; Batch 3 (#1290, #1291) ~1 more. |
| path_solve_terminated | 10 | ≤ 9 | ≤ 8 | Pattern C (launch phantom-offset fix) may remove 1. |
| model_infeasible | 8 | ≤ 7 | ≤ 5 | Pattern C fixes on alias-sum emissions may recover one CGE-family infeasible. |
| Tests | 4,522 | ≥ 4,560 | — | PR12 landed 6 determinism tests + Day 3/Day 4/Day 5 added unit tests (#1283, #1289 + phase1 mechanical-port test). |

**Error influx budgets unchanged (Unknown 6.3 calibration — §Influx Calibration below).**

**What was removed from the Sprint 24-era targets:** the Match +6 ladder (Gates 1–4) was premised on Pattern A landing a Phase 2 cohort sweep that Day 5 disproved. The revised Match target uses the smaller, better-calibrated Pattern C + #1289 totals.

---

## Workstreams

### WS1: Alias-AD (Priority 1) — REVISED

**Effort:** ~8–12h (reduced from 19–26h by dropping Phase 2 cohort rollout).
**Target:** Pattern C recovers launch + opportunistically 1–2 Pattern-C-shaped cohort models. Phase 1 mechanical-port landed Days 2–4 with no regressions.
**Source:** [`AUDIT_ALIAS_AD_CARRYFORWARD.md`](./AUDIT_ALIAS_AD_CARRYFORWARD.md), [`DESIGN_ALIAS_AD_ROLLOUT.md`](./DESIGN_ALIAS_AD_ROLLOUT.md), [`DAY5_PATTERN_A_INVESTIGATION.md`](./DAY5_PATTERN_A_INVESTIGATION.md).

| Phase | Focus | Issues | Days | Status |
|---|---|---|---|---|
| 1 | Pattern A single-index validation + `_partial_collapse_sum` multi-index mechanical port | — (architecture) | 2–4 | DONE — PR #1302, #1303 merged; no behavioral change on qabel/abel/launch (they were never Pattern-A-blocked, per Day 5 evidence). |
| 1.5 | Day 5 evidence-driven investigation | — | 5 | DONE — PR #1305; findings disprove Phase 2 hypothesis. |
| 2 | ~~Pattern A across all 6 issues~~ **DROPPED** | ~~#1138, #1139, #1140, #1142, #1145, #1150~~ | — | DROPPED per Day 5 findings. |
| 3 | Pattern C alias-of-IndexOffset handling in KKT stationarity + launch `stat_iweight` fix | New-issue (filed Day 6) + latent #1143, #1146, #1277 | 6–7 | NEW — replaces Phase 2. |
| 3.5 | Pattern A cohort sanity sweep (confirm #1138, #1139, #1140, #1142, #1145, #1150 are not AD-blocked) | Inspection only | 7 | NEW — confirms Phase 2 drop. |
| 4 | qabel/abel PATH-solve reassessment (separate nonconvex-solver noise from emission bug) | #1138, #1139 (if emission bug) | 8 | NEW — replaces original Phase 3. |
| 5 | Pattern E routing — contingent on Checkpoint 2 GO | #1141, #1144, #1147 | 13 (buffer) | OPTIONAL — same scope as original Phase 4 but demoted to buffer-day contingency. |

**Regression canaries (unchanged per `AUDIT_ALIAS_AD_CARRYFORWARD.md` tier list):**
- **Tier 0 (non-negotiable):** `dispatch`.
- **Tier 1 (alias-using matching):** `quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge`, plus defensive `paklive` (non-alias).
- **Tier 2:** all 44 non-alias matching models — golden-file diff expected identical.

**Touched files (revised):** `src/kkt/stationarity.py` (Pattern C — `_compute_lead_lag_conditions`, `_collect_lead_lag_offsets`, and/or the emission site that enumerates alias bindings via ±N offsets); `src/ad/derivative_rules.py` (Phase 1 mechanical port — DONE).

### WS2: Emitter Backlog (Priority 2) — Largely Unchanged

**Effort:** ~18–28h across 3 batches + Task 5 recovered-translate fixes (reduced from 23–33h by deferring #1277 AD-dependent re-validation to Pattern C landing).
**Target:** 4+ path_syntax_error reductions; at least 1 Match gain from #1289 (LANDED Day 4).
**Source:** [`CATALOG_EMITTER_BACKLOG.md`](./CATALOG_EMITTER_BACKLOG.md), [`ANALYSIS_RECOVERED_TRANSLATES.md`](./ANALYSIS_RECOVERED_TRANSLATES.md).

| Batch | Focus | Issues | Effort | Days | Status |
|---|---|---|---|---|---|
| 1 | presolve paths + UEL quoting | #1275, #1280 | 3–5h | 2–3 | DONE — #1275 via PR #1302 (Day 2), #1280 via PR #1303 (Day 3). |
| 2.5 | Ganges calibration stripping (highest-leverage single fix — unblocks ganges + gangesx) | #1289 | 4–6h | 4 | DONE (PR #1304). |
| 2 | IR-normalize + emitter idempotency + turkpow line wrap | #1279, #1276, #1281, #1292 | 7–11h | 8–9 | PENDING — slipped from original Days 4–6 due to Day 5 pivot. |
| 3 | AD / stationarity (post-Pattern-C) + ferts identifier length + clearlak statement ordering | #1277, #1278, #1290, #1291 | 8–12h | 10–11 | PENDING — #1277 gated on Pattern C landing Day 7. |

**Touched files:** `src/emit/emit_gams.py` (#1275 DONE, #1280 DONE, #1281, #1292), `src/ir/normalize.py` (#1279), `src/kkt/stationarity.py` (#1277, #1278; overlap with Pattern C work), new `_DeclaredSymbolTracker` helper.

### WS3: Determinism Infrastructure (Day 1) — DONE

Landed in PR #1301 (merged). Option D grammar fix in `src/ir/parser.py::_resolve_ambiguities` + PR12 test harness (`tests/integration/test_pipeline_determinism.py`, `.github/workflows/nightly.yml`, `determinism` pytest marker).

### WS4: Small Priorities (Day 12 — shifted from Day 11)

**Effort:** ~7.5–9.5h combined (per `DESIGN_SMALL_PRIORITIES.md`).
**Target:** saras-style model flagged by extended multi-solve gate; dispatcher refactor with zero byte-diff regression.

- **#1270 gate extension (3.5–4.5h):** Approach A cross-reference — flag `eq.m` reads whose receiving parameter later appears in another declared model's constraint body. Code site `src/validation/driver.py:151–225`. 4-fixture test matrix with explicit expected outcomes.
- **#1271 dispatcher refactor (4–5h):** Unified signature `_loop_tree_to_gams(node, *, token_subst=None)`. Byte-diff regression test: snapshot 135 currently-translating models pre-refactor (PYTHONHASHSEED=0), regenerate post, `diff -r` must be empty.

### WS5: Pipeline Retest and Close (Days 14–15 — shifted from Days 13–14)

**Effort:** ~6h.

| Day | Task |
|---|---|
| 14 | Full pipeline retest (per PR6); acceptance-criteria evaluation against §Sprint 25 Targets; error-influx accounting (per PR7, PR10 re-calibrated). |
| 15 | Sprint retrospective; CHANGELOG updates; PROJECT_PLAN KPIs; Sprint 26 carryforward issue filing. |

---

## Influx Calibration (Unknown 6.3) — Unchanged

**Finding:** The Sprint 24 retrospective's PR13 "100% influx" finding was specific to **previously-timeout-excluded models** (5 models: ganges, gangesx, ferts, clearlak, turkpow went 5/5 to `path_syntax_error` after translate recovery). This category is dominated by latent emitter bugs that also slow translation — their failure mode is "valid emission is broken."

Alias-AD recoveries are a **different failure mode**: the MCP structure is syntactically valid; only the derivative values are wrong. When an alias-AD fix lands, the recovered model produces valid GAMS that typically compiles and either solves correctly (best case → Match gain) or hits a PATH solver-convergence issue (`path_solve_terminated`). It rarely produces new `path_syntax_error` unless the fix itself introduces an emission bug.

**Calibrated Sprint 25 influx budgets:**

| Recovery source | Influx rate | Rationale |
|---|---|---|
| Alias-AD / Pattern C (Priority 1, revised scope) | **30%** | 1 per ~3 recoveries. Pattern C's surface area is smaller than the original Phase 2 cohort rollout, so absolute influx is expected small; percentage budget kept. |
| Priority 2 emitter (recovered-translates #1289–#1292) | **80–100%** | PR13 category — latent emitter bugs that also previously caused failure. Same dynamics expected. |
| Priority 2 emitter (existing in-scope, non-timeout-recovered — #1275, #1276, #1280, #1281, #1279) | **10–20%** | Fix bugs in models already in scope; accidental regression budget. |
| Priority 3 multi-solve gate | **0%** (by construction) | Gate only excludes; cannot introduce new errors on kept models. |

**Verification Status:** Unknown 6.3 — ✅ VERIFIED via `../SPRINT_24/SPRINT_RETROSPECTIVE.md` §2 and `../SPRINT_24/SPRINT_LOG.md` Days 3–5.

---

## Daily Schedule (Revised Post-Day-5)

### Day 0 — Setup & Kickoff — DONE
- Verified baseline metrics match `BASELINE_METRICS.md`.
- Generated Tier 1 + Tier 2 golden files.
- Initialized `SPRINT_LOG.md`.

### Day 1 — WS3 Determinism Landing — DONE (PR #1301)
- Option D fix in `_resolve_ambiguities` landed.
- PR12 test harness landed.
- 20-seed sweep on chenery: 20/20 byte-identical.

### Day 2 — WS1 Phase 1 Start + WS2 Batch 1 Start — DONE (PR #1302 + #1275)
- Debug instrumentation added to `_diff_varref` and `_partial_collapse_sum` (SPRINT25_DAY2 tag, env-gated).
- #1275 presolve-path portability landed.
- qabel trace captured; Phase 1 findings documented.

### Day 3 — WS1 Phase 1 Prototype + WS2 Batch 1 Complete — DONE (PR #1303)
- `_partial_collapse_sum` multi-index mechanical port landed (structural no-op on qabel/abel/launch — they never hit the gap path).
- #1280 unquoted-UEL-dots fix landed.
- Tier 0 + Tier 1 canary: no regressions.

### Day 4 — WS1 Phase 1 Complete + WS2 Batch 2.5 (#1289) — DONE (PR #1304)
- Phase 1 validation on abel, launch — all three models still hit their original rel_diff (see Day 5 for why: AD was never the bug).
- #1289 ganges/gangesx calibration-from-`.l` stripping landed. +1 Solve / +1 Match from ganges confirmed.
- Gate 1 (Phase 2 GO/NO-GO) deferred to end of Day 5 pending investigation.

### Day 5 — Pattern A Investigation — DONE (PR #1305)
- Evidence-driven investigation of all three Phase 1 targets.
- **Finding:** None exhibit a Pattern A bug. qabel/abel criterion AD is byte-correct; launch's `stat_iweight` has phantom `s±N` offsets from KKT stationarity assembly (Pattern C).
- **Gate 1 outcome:** NO-GO for Phase 2 in original shape. Pivot to Pattern C.
- Deliverable: `DAY5_PATTERN_A_INVESTIGATION.md` (repo-tracked via PR #1305).

### Day 6 — Pattern C Prototype (NEW)

**Branch:** `sprint25-day6-pattern-c-prototype`.

**Objective:** Locate the phantom-offset enumeration code in KKT stationarity, reproduce launch's `stat_iweight` bug minimally, prototype a gate that only enumerates ±N offsets when the source actually has an IndexOffset.

**Tasks:**
1. Locate the emission site. Candidate functions per `DAY5_PATTERN_A_INVESTIGATION.md`: `src/kkt/stationarity.py::_compute_lead_lag_conditions`, `_collect_lead_lag_offsets`. Grep for `card` + `ord` + alias-enumeration patterns.
2. Reproduce minimally. Build a synthetic unit test that mirrors launch's `dweight(s).. weight(s) =e= sum(ss$ge(ss,s), iweight(ss) + pweight(ss))` and asserts the emitted `stat_iweight` has no `s+N`/`s-N` offsets in the alias-only case.
3. Prototype a gate: only enumerate ±N offsets on alias bindings when the equation's source contains at least one actual `IndexOffset` node referring to the alias's base set. This requires inspecting the equation IR, not just the alias table.
4. Verify launch translates correctly post-fix. Check Tier 0 dispatch canary + Tier 1 canary remain identical (most matching models don't exercise the phantom-offset path, so a conservative gate should be safe).
5. File a new Sprint 25 issue `pattern_c_phantom_offset_stat_iweight` referencing `DAY5_PATTERN_A_INVESTIGATION.md`.

**Deliverable:** PR with prototype + launch-specific synthetic test. Tier 0/1 canary must match golden. **Do NOT run full 54-set regression yet** — defer to Day 7 to isolate the prototype failure surface.

### Day 7 — Pattern C Validation + Pattern A Cohort Sanity Sweep (NEW)

**Branch:** `sprint25-day7-pattern-c-validation`.

**Objective:** Validate the Day 6 prototype on the full 54-set golden-file regression. In parallel, do a short evidence-gathering sweep on the other six Pattern A candidate models (#1138, #1139, #1140, #1142, #1145, #1150) to confirm they are not AD-blocked — establishing that dropping Phase 2 was correct.

**Tasks:**
1. Run full 54-set golden-file regression with the Day 6 Pattern C prototype. Document any regressions (expected 0; Pattern C only fires when phantom-offset enumeration was already happening).
2. Translate launch fresh. First run compile-only (`gams /tmp/launch_mcp.gms action=c`) as a syntax/symbol sanity check. Then run a separate full PATH solve on the emitted MCP and measure rel_diff against the baseline NLP solution. If rel_diff improves materially, +1 Match candidate for Day 14 pipeline retest.
3. Pattern A cohort sanity sweep: for each of the 6 models in #1138, #1139, #1140, #1142, #1145, #1150, capture the derivative-emission shape via `SPRINT25_DAY2_DEBUG=1` trace. Classify each as:
   - **Pattern A shape (AD-blocked):** `_partial_collapse_sum` rejects the body-index match → emits `0` for a known-nonzero derivative.
   - **Pattern C shape (phantom offsets):** derivative emission has ±N offsets that don't come from the source.
   - **Other:** nonconvex-solver noise, scalar/domain mismatch, or a latent KKT stationarity bug.
4. If ≥1 Pattern-C-shaped cohort model is found, extend the Day 6 prototype to cover it; re-run 54-set regression. If all 6 models are "Other," document in `DAY7_COHORT_SWEEP.md` and close out the original Pattern A Phase 2 hypothesis formally.
5. Tier 0 + Tier 1 canary.

**Deliverable:** PR for Pattern C validation (Day 6 prototype graduated) + `DAY7_COHORT_SWEEP.md` classifying the 6 models.

### Day 8 — qabel/abel PATH-Solve Reassessment + WS2 Batch 2 Start (#1279)

**Branch:** `sprint25-day8-qabel-abel-reassess-plus-1279`.

**Objective:** Determine whether qabel/abel's rel_diff is a real emission bug or nonconvex-solver noise by running a full PATH solve (not `action=c`). Start WS2 Batch 2 with #1279 robustlp scalar-widening.

**Tasks:**
1. Translate qabel + abel (they should already be unchanged post-Day-7 since neither is Pattern-C-shaped per Day 5). Compile + full PATH solve. Measure rel_diff.
2. If rel_diff still materially off, bisect the `stat_x` emission vs. the expected symbolic form. Specifically: the `nu_stateq(n, k-1)$(ord(k) > 1)` term is the prime suspect per Day 5 — check the emitter's domain-shift handling for `stateq(n, k+1)` → `nu_stateq(n, k)`.
3. If rel_diff acceptable (solver noise on a nonconvex problem), mark #1138/#1139 as "non-bug" in `AUDIT_ALIAS_AD_CARRYFORWARD.md` and close corresponding GH issues with resolution note.
4. #1279: Fix robustlp `defobj(i)` scalar-equation widening in `src/ir/normalize.py`. The emitter currently emits `defobj(i)` as a domain-indexed equation when the AD treats it as scalar — fix the normalize pass.
5. Tier 0 + Tier 1 + 54-set golden-file regression.

**Deliverable:** PR covering qabel/abel classification (document or fix) + #1279 robustlp fix.

### Day 9 — WS2 Batch 2 Continue (#1276, #1281, #1292)

**Branch:** `sprint25-day9-batch2-complete`.

**Objective:** Land Batch 2 remainder.

**Tasks:**
1. Implement shared `_DeclaredSymbolTracker` helper.
2. #1276: fawley duplicate `.fx` — use `_DeclaredSymbolTracker` to detect already-emitted `.fx` assignments and skip duplicates.
3. #1281: lmp2 duplicate Parameter declaration — same helper, different call site.
4. #1292: turkpow `stat_zt` 144k-char single-line emission — add line-wrapping in the emitter for `sameas()` Cartesian-product expansions when line length exceeds ~1000 chars.
5. Tier 0 + Tier 1 + 54-set golden-file regression.

**Deliverable:** PR with Batch 2 complete.

### Day 10 — WS2 Batch 3 Core (#1277 post-Pattern-C, #1278)

**Branch:** `sprint25-day10-batch3-core`.

**Objective:** Re-validate #1277 now that Pattern C is live; fix #1278 tautology.

**Tasks:**
1. Re-translate twocge. #1277 was partially subsumed by Pattern C per the original plan — verify the `stat_tz` offset-alias emission. If still broken, file a narrow follow-up issue and continue.
2. #1278: Fix the `ord(r) <> ord(r)` (always-false) tautology bug in `src/kkt/stationarity.py`. The stationarity emitter should produce `ord(r) <> ord(rp)` (alias-correct form). Identify the substitution site; fix + unit test.
3. Tier 0 + Tier 1 + 54-set golden-file regression.

**Deliverable:** PR with #1277 re-validation + #1278 fix.

### Day 11 — WS2 Batch 3 Finish (#1290, #1291) + Checkpoint 2

**Branch:** `sprint25-day11-batch3-complete-plus-checkpoint2`.

**Objective:** Close Batch 3; evaluate Checkpoint 2.

**Tasks:**
1. #1290: fix ferts multiplier-name 67-char length violation — add a synthetic-hash-shortening pass in the emitter.
2. #1291: fix clearlak statement ordering — hoist `sum(leaf, ...)` AFTER `leaf(n) = yes$(...)` initialization. Deterministic verification via 3-seed run.
3. Full pipeline retest: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m).
4. Evaluate **Checkpoint 2** (see table below). Decide whether to include Phase E routing (optional Day 13 buffer work) or lock main.

**Checkpoint 2 criteria:**

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Match | ≥ 56 | ≥ 55 | < 54 (regression) |
| Solve | ≥ 100 | ≥ 99 | < 99 (regression) |
| path_syntax_error | ≤ 7 | ≤ 9 | > 11 (regression) |
| model_infeasible | ≤ 7 | ≤ 8 | > 8 (regression) |
| Tier 0 + Tier 1 canaries | All match | ≤ 1 regression | > 1 regression |
| Tests | All pass | All pass | Any failure |

- **GO:** Day 13 buffer may include Pattern E routing (#1141, #1144, #1147 — OPTIONAL stretch).
- **CONDITIONAL GO:** Day 13 buffer limited to tail-cleanup; no new architectural changes.
- **NO-GO:** main locked; Day 13 reverts offending PRs; Phase E cancelled.

**Deliverable:** PR with Batch 3 complete + Checkpoint 2 decision documented in `SPRINT_LOG.md`.

### Day 12 — WS4 Small Priorities (#1270, #1271)

**Branch:** `sprint25-day12-small-priorities`.

**Objective:** Land the #1270 multi-solve gate extension and the #1271 dispatcher refactor.

**Tasks:**
1. #1270 (3.5–4.5h): Implement + 4-fixture test matrix (saras must flag; post-solve reporting, multi-stage display, partssupply `var.l` must NOT flag). Verify gussrisk/sparta remain un-flagged; verify saras is flagged.
2. #1271 (4–5h): Unified signature `_loop_tree_to_gams(node, *, token_subst=None)`. Byte-diff regression test on all 135 currently-translating models (`diff -r /tmp/pre /tmp/post` must be empty).

**Deliverable:** PR with both WS4 items.

### Day 13 — Buffer / Phase E (if Checkpoint 2 GO) / Sprint-Close Prep

**Branch:** `sprint25-day13-buffer`.

**Objective:** Absorb slippage; optional Phase E routing; file Sprint 26 issues.

**Tasks:**
1. Buffer for any Batch 3 / WS4 tail.
2. **OPTIONAL (only if Checkpoint 2 was GO and schedule has slack):** Phase E routing — re-inspect #1141 (kand multi-solve driver re-verify), #1144 (launch post-Pattern-C re-check), #1147 (camshape). Drop anything that doesn't fit in the day.
3. **OPTIONAL stretch (only if slack):** Per Task 8 contingency, Option 1 short-circuit in `src/ad/index_mapping.py::enumerate_equation_instances` (srpchase + iswnm). Effort 4–6h; do NOT land unless ≥4h clear headroom.
4. File Sprint 26 carryforward issues (label `sprint-26`):
   - Translation timeouts: 4 of 5 hard timeouts (iswnm, sarf, mexls, nebrazil) unless Option 1 landed today.
   - `mine` `internal_error`.
   - Any Pattern E issue not resolved.
   - Original Pattern A Phase 2 cohort models (#1138, #1139, #1140, #1142, #1145, #1150) with Day 7 cohort-sweep classification labels — reclassified from "Pattern A" to whatever shape they actually are.
5. Update `KNOWN_UNKNOWNS.md` with end-of-sprint discoveries.

### Day 14 — Final Pipeline Retest

**Branch:** `sprint25-day14-retest`.

**Objective:** Definitive pipeline metrics per PR6.

**Tasks:**
1. Full pipeline: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2h15m).
2. Record final metrics: Parse / Translate / Solve / Match + 4 `outcome_category` counts.
3. Cross-check against `PLAN.md` §Sprint 25 Targets (revised).
4. Error-influx accounting (per PR7 + PR10 re-calibrated):
   - Alias-AD / Pattern C gross fixes vs new errors. Check against 30% budget.
   - Emitter-recovered gross fixes vs new errors. Check against 80–100% budget.
5. Commit updated `data/gamslib/gamslib_status.json`.

### Day 15 — Sprint Close + Retrospective

**Branch:** `sprint25-day15-retro`.

**Objective:** Write retrospective, update CHANGELOG + PROJECT_PLAN, file Sprint 26 recommendations.

**Tasks:**
1. Write `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` using Sprint 24 template:
   - Metrics delta against §Sprint 25 Targets (Revised).
   - Acceptance criteria pass/fail.
   - Went well / what could be improved.
   - **Special section:** Day 5 pivot retrospective — what the original Phase 2 assumption got wrong, how the investigation approach (capture traces, read emissions, disprove hypothesis) could have been run Pre-Sprint-25 to avoid the mid-sprint rewrite.
   - PR10 re-calibration outcome (did the 30% / 80–100% split hold against Pattern C's narrower scope?).
   - New recommendations (PR16+) for Sprint 26.
2. Update `CHANGELOG.md` Sprint 25 Summary.
3. Update `PROJECT_PLAN.md` Rolling KPIs.
4. File Sprint 26 recommendations — Pattern A cohort reclassification, Pattern C remainder, translation timeouts, Phase E remainders, any new discoveries.

---

## Contingency Plans (Revised)

### Risk 1: Pattern C Prototype Breaks Matching Models
**Trigger:** Day 6 prototype causes regression on any Tier 0/1/2 canary.
**Action:** Narrow the Pattern C gate. The conservative principle is: only suppress ±N enumeration when the equation body has zero IndexOffset nodes referring to the alias's base set. If narrowing doesn't preserve launch's fix, defer Pattern C to Sprint 26.
**Fallback:** Launch stays in current rel_diff state; Match target drops to +1 (ganges only).

### Risk 2: Pattern A Cohort Sweep Finds Real AD Bugs
**Trigger:** Day 7 inspection of #1138/1139/1140/1142/1145/1150 finds ≥2 actually Pattern-A-shaped models.
**Action:** Re-open Phase 2 in a narrowed form on Day 13 buffer. Only land if dispatch + Tier 1 canary stays clean.
**Fallback:** File as Sprint 26 carryforward with classification data from the sweep.

### Risk 3: qabel/abel PATH Solve Confirms Emission Bug (not solver noise)
**Trigger:** Day 8 rel_diff measurement shows systematic bias inconsistent with nonconvex-solver noise.
**Action:** Extend Day 8 to locate the `stat_x` / `nu_stateq` domain-shift bug. This may extend into Day 9 WS2 time; compensate by trimming Batch 2 scope if necessary.
**Fallback:** File qabel/abel as open Sprint 26 issues with precise emitter-bug localization.

### Risk 4: Checkpoint 2 NO-GO
**Trigger:** Day 11 full pipeline shows regression below baseline (Match < 54 OR Solve < 99).
**Action:** Day 12 reverts offending PRs; Phase E cancelled; Day 13 buffer used for revert stabilization.
**Fallback:** Sprint close with baseline-equivalent metrics but documented learnings.

### Risk 5: Error Influx Above Budget
**Trigger:** Day 14 retest shows alias-AD/Pattern C influx >30% OR emitter-recovered influx >100%.
**Action:** Classify new errors; file Sprint 26 issues. Document in retrospective as PR10 recalibration item for Sprint 26.

---

## Workstream to Issue Mapping (Revised)

### WS1: Alias-AD / Pattern C
- **Phase 1 (DONE):** Mechanical port — no issue IDs; architecture prep.
- **Phase 3 (Pattern C — NEW, Days 6–7):** new-issue (filed Day 6); indirectly covers #1143, #1146, #1277.
- **Phase 3.5 (Cohort sanity sweep — NEW, Day 7):** #1138, #1139, #1140, #1142, #1145, #1150 — **inspection only**, reclassification outputs go to `DAY7_COHORT_SWEEP.md` and Sprint 26 carryforward issues.
- **Phase 4 (qabel/abel PATH solve — NEW, Day 8):** #1138, #1139 (if real emission bug).
- **Phase 5 (Pattern E routing — OPTIONAL, Day 13):** #1141 (B→E), #1144, #1147 — contingent on Checkpoint 2 GO.

### WS2: Emitter Backlog
- **Batch 1 (DONE):** #1275 (presolve paths), #1280 (unquoted UEL dots).
- **Batch 2.5 (DONE):** #1289 (ganges calibration stripping).
- **Batch 2 (Days 8–9):** #1279 (robustlp scalar-widening), #1276 (fawley duplicate `.fx`), #1281 (lmp2 duplicate Parameter), #1292 (turkpow line wrap).
- **Batch 3 (Days 10–11):** #1277 (twocge mixed offsets — post-Pattern-C re-validation), #1278 (tautology), #1290 (ferts identifier length), #1291 (clearlak statement ordering).

### WS3: Determinism (DONE)
- #1283 (parser non-determinism): Option D fix + PR12 test harness — LANDED PR #1301.

### WS4: Small Priorities (Day 12)
- #1270 (multi-solve gate extension).
- #1271 (dispatcher refactor).

### WS5 (deferred to Sprint 26, unchanged):
- Translation timeouts (#1169, #1185, #1192 family + #1228 + Task 8's 5 models).
- `mine` (`internal_error` / `SetMembershipTest`).
- Pattern A cohort reclassification (#1138, #1139, #1140, #1142, #1145, #1150 — per Day 7 sweep outputs).

---

## Unknown 6.3 Verification Summary (Unchanged)

**Status:** ✅ VERIFIED via `../SPRINT_24/SPRINT_RETROSPECTIVE.md` §2 + `../SPRINT_24/SPRINT_LOG.md` Days 3–5.

- Sprint 23 `_alias_match` / `_same_root_set` / `_partial_collapse_sum` base layer + Sprint 24 Day 3–5 single-index-sum-collapse fix landed qabel and abel from mismatch/IOerror → `model_optimal` + mismatch-value. Day 5 Sprint 25 investigation confirmed the criterion AD is correct; remaining mismatch stems from KKT stateq emission (not AD) — further narrowing the scope of what alias-AD workstreams need to cover.
- Final Sprint 24 Match delta: +5 (49 → 54).
- PR13 "100% influx" applies specifically to previously-timeout-excluded models; NOT representative of alias-AD or Pattern C dynamics.

**Sprint 25 decision:** PR10 split into two sub-budgets — alias-AD 30%, emitter-recovered 80–100%. Match target calibrated against +2 Pattern C + 0 Phase 2 (dropped); stretch +2 via cohort sweep Pattern-C-shaped finds.

---

## Related Documents

- Prep task deliverables (all merged to main): `AUDIT_ALIAS_AD_CARRYFORWARD.md`, `INVESTIGATION_PARSER_NON_DETERMINISM.md`, `CATALOG_EMITTER_BACKLOG.md`, `ANALYSIS_RECOVERED_TRANSLATES.md`, `DESIGN_ALIAS_AD_ROLLOUT.md`, `DESIGN_SMALL_PRIORITIES.md`, `PROFILE_HARD_TIMEOUTS.md`, `BASELINE_METRICS.md`, `DESIGN_DETERMINISM_TESTS.md`.
- **Day 5 pivot evidence (new):** `DAY5_PATTERN_A_INVESTIGATION.md` (PR #1305).
- **Day 7 cohort sweep output (new):** `DAY7_COHORT_SWEEP.md` (to be created Day 7).
- Day-by-day execution prompts: `prompts/PLAN_PROMPTS.md` (revised to match this plan).
- Known unknowns + calibrated influx budgets: `KNOWN_UNKNOWNS.md`.
- Sprint 24 templates: `../SPRINT_24/PLAN.md`, `../SPRINT_24/prompts/PLAN_PROMPTS.md`.
