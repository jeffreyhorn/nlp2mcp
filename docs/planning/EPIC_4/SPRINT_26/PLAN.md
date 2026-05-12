# Sprint 26 Detailed Plan

**Created:** 2026-05-09
**Sprint Duration:** 14 days (Day 0 – Day 13)
**Effort:** ~50–75h estimated total; budget ~12h/day = 168h max — substantial slack absorbs Day-1 PROCEED-vs-REPLAN routing risk + Priority 5 #1334 re-investigation overhead.
**Risk Level:** MEDIUM — Pattern C is the third sprint touching this code path; mitigation = pre-Sprint hypothesis validation already executed in Task 3 (PR16 methodology).
**Baseline:** Sprint 26 Day 0 baseline (committed by Prep Task 9, `BASELINE_METRICS.md`) — Parse 142/142 (100%), Translate 130/142 (91.5%), Solve 104, Match 60, Tests 4,735. Scope LOCKED at **142** in-scope per PR15 (carrying forward Sprint 25 abel reclassification — see Sprint 25 BASELINE_METRICS §5.1).

---

## Executive Summary

Sprint 26 is the post-Sprint-25 carryforward sprint focused on five priorities (schedule revised Day 3 per Phase B reclassification to Sprint 27 #1381):

- **Priority 1 (Day 1 only — REVISED Day 3): Pattern C Phase A landed (launch fix).** Phase A restored the Sprint 25 #1351 launch fix via consolidated zero-offset builder rewrite (PR #1379, Day 2 validation PR #1380). **Phase B (camcge + cesam2 generalization) reclassified to Sprint 27 #1381** — the swap-based transform doesn't generalize to plain-alias bodies; needs a builder redesign (10–16h) intercepting BEFORE element-to-set substitution. fawley + otpop reclassify out of Priority 1 (see Priority 2 / Priority 5 routing). Days 3 freed; Day 4 absorbs Priority 4 + Priority 5 #1334 forward-pull.
- **Priority 4 (Day 4 — PULLED FORWARD from Day 8): Translation timeout Option 1 short-circuit.** Per Task 6 design, 4–6h budget, projected +1–2 Translate gain (srpchase HIGH; iswnm/sarf/mexls/nebrazil LOW–MEDIUM). #1224 deferred to Sprint 27.
- **Priority 5 (Day 4 + Days 9–10 — Day 4 #1334 investigation PULLED FORWARD from Day 8): AD residuals #1334 + #1335.** Per Task 7 recap, scope decision: 2 of 3 originally-bundled issues (#1334 + #1335 in Sprint 26; #1357 deferred to Sprint 27 alongside fawley #1356 as a "comp_up subset/superset" workstream). Day 4 = #1334 investigation + scoping (no `src/`); Day 9 = #1334 fix completion + #1335 start; Day 10 = wrap + Checkpoint 2. Re-estimated 8–18h.
- **Priority 2 (Days 6–7): Pattern A cohort reclassification — MECHANICAL.** Per Task 4, 6 cohort issues = 4 closures + 1 close-and-refile + 1 forward-link to Sprint 27 #1381 (camcge fix deferred). Effort dropped from original 4–6h investigative to ~1.5h mechanical.
- **Priority 3 (Days 6–7, parallel): Pattern E carryforward.** Per Task 5, scope reduced from 3 models to 1 (kand alias-AD). catmix and camshape closures are mechanical.

Process recommendations PR12, PR14, PR15, PR17, PR18 have already landed via Sprint 26 prep (Tasks 9, 10). PR19 design landed via Task 8; **CI extension implementation lands during Sprint 26 Day 11** per the Task 8 design doc.

Day 8 is now buffer (Priority 4 + Priority 5 #1334 investigation pulled forward to Day 4). Day 12 is the standard PR14 emit-artifact review pass on the models with emit changes this sprint (launch / srpchase / otpop).

**Two checkpoints** at Days 5 and 10 (criteria below).

**Day 13 final pipeline retest** with bucket-provenance comparison vs Day 0 baseline (per PR17).

---

## Sprint 26 Targets (per PROJECT_PLAN.md §Sprint 26 Acceptance Criteria + Task 9 baseline — UPDATED Day 3 per Phase B reclassification to Sprint 27 #1381)

| Metric | Day 0 (Task 9 baseline) | Sprint 26 Target (revised Day 3) | Stretch | Net needed |
|---|---|---|---|---|
| Parse | 142/142 (100%) | ≥ 142/142 | — | 0 (invariant) |
| Translate | 130/142 (91.5%) | ≥ 132/142 (maintain churn-outs + ≥ 2 from Priority 4) | ≥ 135/142 | **+2** (Priority 4 short-circuit recovers srpchase / iswnm) |
| Solve | 104 | ≥ 104 (maintain) | ≥ 106 | **0** (Priority 5 +1–2 stretch from #1334 / #1335; Phase A/B Solve gains deferred to Sprint 27 #1378 + #1381) |
| Match | 60 | ≥ 60 (maintain) | ≥ 62 | **0** (same rationale as Solve) |
| path_syntax_error | 9 | ≤ 9 (maintain) | ≤ 8 | **0** (Phase B camcge/cesam2 deferred — they stay in path_syntax_error this sprint) |
| path_solve_terminated | 5 | ≤ 5 | ≤ 4 | maintain (Sprint 25 floor) |
| model_infeasible | 4 | ≤ 4 | ≤ 3 | maintain |
| Tests | 4,735 | ≥ 4,737 (Day 1 floor: baseline 4,735 + 2 Phase A regression tests already landed) | ≥ 4,745 | +2 already booked Day 1 (PR #1379); Sprint 26 remaining work adds modest additional test coverage as a stretch |

**Day 3 target revision rationale:** Phase B's swap-based transform doesn't generalize to plain-alias bodies (Day 3 discovery — element-to-set substitution collapses alias and eq-domain names before the swap can run). Phase B redesign (camcge + cesam2) deferred to Sprint 27 #1381. Sprint 26 Solve / Match / path_syntax_error targets relaxed to maintain; Sprint 26 still delivers Phase A (launch consolidated emit, Day 1 PR #1379) + Priority 2/3/4/5 work.

**Bucket-provenance evaluation** (per PR17, Task 9 §4.3): Sprint 26 Day-N retests must distinguish bucket churn from real regressions. The 3 Day-0 machine-variance churn-outs (clearlak / ganges / turkpow `path_syntax_error → translate_timeout`) are expected to return to `path_syntax_error` once Priority 4 lands the Option 1 short-circuit — the count moving back UP is NOT a regression. The retest must read the per-model bucket-provenance column to disambiguate.

---

## Workstream Allocation

| Priority | Days | Effort | Lead deliverable |
|---|---|---|---|
| 1 — Pattern C Phase A | 1 (Days 2 validation, Day 3 reclassification) | ~6h actual | Phase A landed Day 1 PR #1379; #1306 xfail removed; consolidated launch emit. **Phase B (camcge + cesam2) reclassified Day 3 to Sprint 27 #1381** (swap-based transform doesn't generalize to plain-alias). Days 3 freed; Day 4 absorbs Priority 4 + Priority 5 #1334 investigation forward-pull. |
| 4 — Option 1 short-circuit | **4 (PULLED FORWARD from Day 8)** | ~4–6h | srpchase translates; +1–2 Translate |
| 5 — AD residuals — #1334 investigation + scoping (no `src/`) | **4 (PULLED FORWARD from Day 8)** | ~3–4h | Re-investigation of 2026-05-05 #1334 closure; Approach 1 fix scoped/sketched in `SPRINT_LOG.md` Day 4 entry. Implementation lands Day 9. |
| **Checkpoint 1** (Day 5) | 5 | n/a | Phase A GO/NO-GO routing (Phase B rows reclassified to Sprint 27 #1381) |
| 2 — Pattern A reclassification | 6–7 | ~1.5h | 4 closures + 1 close-and-refile + 1 forward-link |
| 3 — Pattern E carryforward (kand) | 6–7 (parallel) | ~3–6h | kand alias-AD fix OR Sprint 27 carryforward |
| Buffer / absorb slippage | 8 | ~6h | Catch up on Days 4 / 6 / 7 slippage; optionally forward-pull Day 12 PR14 review or Day 9 #1335 start |
| 5 — AD residuals — #1334 fix completion + #1335 start | 9 | ~5–8h | Continue Approach 1 from Day 4; otpop `sum(t__, ...)` lines disappear; #1335 scalar-equation-gate fix start |
| 5 — AD residuals — wrap (NLP-warm-started reproducer) | 10 | ~4–6h | otpop NLP-warm-started MCP converges to `pi ≈ 4217.80` |
| **Checkpoint 2** (Day 10) | 10 | n/a | All 5 priorities landed-or-scoped |
| 6 — PR19 CI extension | 11 | ~4–8h | `.github/workflows/pr19-emit-solve-validation.yml` lands |
| 7 — Buffer / PR14 emit-artifact review | 12 | ~4–6h | Mid-sprint "read the regenerated `.gms`" pass on the models with emit changes this sprint (launch / srpchase / otpop — Phase B targets camcge / cesam2 deferred to Sprint 27 #1381 per Day 3) |
| 8 — Final pipeline retest + close | 13 | ~3–6h | Day 13 baseline + bucket-provenance comparison; CHANGELOG; Sprint 26 retrospective scaffold |

**Parallel-work justification:**
- Day 4: Priority 4 (`src/ad/index_mapping.py`) + Priority 5 #1334 investigation (`src/kkt/stationarity.py`) touch different files. The ad/* surface shared dependency means PR landing order matters but the work itself is parallel-safe.
- Days 6–7: Priority 2 (mechanical issue closures, GitHub-only) + Priority 3 (kand fix in `src/`) have no shared file surface — safe to run in parallel.
- Day 9: continuation of Priority 5 #1334 fix + #1335 start touches the same `src/` surface but in sequenced sub-tasks (not parallel) — single PR per day.

**Per-day budget sanity check:** No day exceeds 12h estimated work. Heaviest days: Day 1 (~6–8h Phase A scoping + prototype), Day 4 (~4–6h Priority 4 + ~3–4h Priority 5 #1334 start = ~7–10h after Day 3 reclassification pulled Priority 4/5 forward). All within budget.

---

## Daily Schedule

### Day 0 — Setup & Kickoff

**Branch:** `sprint26-day0-kickoff` (docs-only PR for `SPRINT_LOG.md` Day 0 entry; no `src/` changes).
**Effort:** ~2h.

**Objective:** Verify Day 0 baseline against `BASELINE_METRICS.md` (Task 9), initialize `SPRINT_LOG.md`, confirm all 11 prep tasks closed, set Sprint 26 milestone on GitHub.

**Tasks:**
1. Verify `data/gamslib/gamslib_status.json` matches `BASELINE_METRICS.md` Day 0 metrics: Parse 142, Translate 130, Solve 104, Match 60.
2. Initialize `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 0 entry per Sprint 25 SPRINT_LOG.md format.
3. Confirm GitHub issue labels:
   - **`sprint-26` label** (Sprint 26 Day 1–13 in-scope work):
     - Priority 1: #1306, #1307, #1354, #1355
     - Priority 2: #1138, #1139, #1140, #1142, #1145, #1150 (closing this sprint per Task 4)
     - Priority 3: #1141, #1144, #1147 (closing or fixing per Task 5)
     - Priority 4: #885, #931, #932, #1185, #1228 (#1224 deferred per Task 6)
     - Priority 5: #1334, #1335
   - **`sprint-27` label** (deferred work — must NOT carry `sprint-26`):
     - #1357 (otpop `comp_up` subset/superset, deferred per Task 7 — file as Sprint 27 carryforward at Day 13 close per §Day 13)
     - #1356 (fawley `comp_up`, deferred per Task 4)
     - #1374 (emit duplicate-init bugs, surfaced during Task 9 PR review)
     - #1224 (mine `ParamRef` IndexOffset, deferred per Task 6)
4. Read all Task 3–10 prep outputs as briefing material:
   - `PATTERN_C_HYPOTHESIS_VALIDATION.md` (REPLAN recommendation — drives Day 1)
   - `PATTERN_A_RECLASSIFICATION_PLAN.md` (Day 6–7)
   - `PATTERN_E_STATUS.md` (Day 6–7)
   - `DESIGN_OPTION_1_SHORT_CIRCUIT.md` (Day 4 — pulled forward from Day 8 per Day 3 reschedule)
   - `AD_RESIDUALS_RECAP.md` (Day 4 + Day 9–10 — #1334 investigation pulled forward to Day 4 per Day 3 reschedule)
   - `DESIGN_PR19_SOLVE_TIME_CI.md` (Day 11)
   - `BASELINE_METRICS.md` (Day 13 retest comparison basis)

### Day 1 — Priority 1 Phase A: Restore Launch Fix (Consolidated Zero-Offset Builder Rewrite)

**Branch:** `sprint26-day1-pattern-c-phase-a`.
**Effort:** ~6–8h.

**Objective:** Per Task 3 REPLAN finding, fix the consolidated zero-offset builder in `src/kkt/stationarity.py:4318–4346` (currently disabled by Sprint 25 #1351 via hardcoded `allow_nonzero_offsets = True`). Rewrite the builder to emit `sum(j$(domain_filter), <body>)` correctly, allowing the launch fix to be re-enabled without producing the launch / quocge / prolog regressions Task 3's prototype patch surfaced.

**Tasks:**
1. Read Task 3 prototype patch evidence: `src/kkt/stationarity.py:4339` is currently hardcoded `allow_nonzero_offsets = True`. Task 3 confirmed that flipping this to a broader gate predicate without fixing the downstream consolidated builder reproduces Sprint 25 #1351's launch failure on 3 of 12 canary outputs (quocge, prolog, launch).
2. Diff Sprint 25 #1306 (the original launch fix) vs Sprint 25 #1351 (the rollback) to identify the consolidated zero-offset builder code path. Both PRs touch `src/kkt/stationarity.py` consolidator logic.
3. Implement the rewrite per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)": `sum(ss$ge(s,ss), -nu_dweight(ss))` instead of the over-counting `sum(ss, -1$ge(ss,s) * nu_dweight(s))` per-offset enumeration.
4. Re-enable the Pattern C gate for the launch case (remove the `if eq_def_for_gate is not None:` guard so the gate-predicate branch no longer no-ops).
5. Tier 0 dispatch canary: must remain byte-identical.
6. Tier 1 canary (10 models): must match golden.
7. Re-run the test that #1351 marked `xfail (strict=True)` — it should now PASS.

**PR14 obligation:** Include the regenerated `data/gamslib/mcp/launch_mcp.gms` in the PR diff. Reviewers must read the `stat_iweight` block.

**Deliverable:** PR for Phase A. `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` flips from xfail to pass.

### Day 2 — Priority 1 Phase A: Validation + Phase B Scoping

**Branch:** `sprint26-day2-pattern-c-phase-a-validation`.
**Effort:** ~5–7h.

**Objective:** Validate Day 1's Phase A patch on the broader corpus. Begin Phase B scoping for camcge + cesam2.

**Tasks:**
1. Full 54-model Tier 0/1/2 golden-file regression (per Sprint 25 SPRINT_LOG.md Day 0 list). Document any regressions.
2. Translate launch + run full PATH solve. Confirm rel_diff improves vs Sprint 25 final.
3. **Phase B scoping** (camcge): inspect `data/gamslib/mcp/camcge_mcp.gms` (currently translates with phantom-offset emit per Task 3 finding). Identify the gate condition that needs to fire for camcge. Per Task 3, camcge needs the gate predicate broadened beyond launch's specific conditional shape to detect plain-alias enumeration.
4. **Phase B scoping** (cesam2): same as camcge but with `sameas`-decomposed SAM-block aliases. Per Task 3, cesam2's gate predicate needs to also recognize `sameas` block guards as Pattern C triggers.
5. Tier 0 + Tier 1 canary.

**Deliverable:** PR for Phase A validation + Phase B scoping notes.

### Day 3 — RECLASSIFIED to Sprint 27 #1381 (Phase B redesign — see SPRINT_LOG.md Day 3)

**Original objective:** Pattern C gate generalization for camcge (#1354).

**Reclassification reason:** Day 3 attempt to extend Phase A's swap-based transform via gate-predicate relaxation produced mathematically wrong emits on plain-alias bodies (camcge + 11 other byte-shifted canaries). Element-to-set substitution collapses the alias name to its canonical (same as the eq-domain index) BEFORE the swap can run, breaking Phase A's swap assumption. See `SPRINT_LOG.md` Day 3 entry for full design discovery + rollback.

**Deferred to Sprint 27 #1381:** Pattern C Phase B redesign (camcge + cesam2 + likely other plain-alias variants currently in the path_syntax_error bucket). Estimated 10–16h across Phase B-1 / B-2 / B-3 sub-scopes.

**Day 3 deliverable shipped:** Docs-only PR with `SPRINT_LOG.md` Day 3 entry, `PLAN.md` reclassification, and Sprint 27 #1381 carryforward issue. No `src/` changes.

### Day 4 — Priority 4 Option 1 Short-Circuit + Priority 5 #1334 Re-Investigation (Parallel) — PULLED FORWARD FROM DAY 8

**Branch:** `sprint26-day4-priority-4-and-5-start`.
**Effort:** ~7–10h (Priority 4 ~4–6h + Priority 5 #1334 investigation ~3–4h).

**Pulled forward from Day 8 because Day 4's original Phase B cesam2 work reclassified to Sprint 27 #1381 (see Day 3).** Day 8 is now buffer (see below).

**Objective:** Land Priority 4 Option 1 short-circuit per Task 6 design. Begin Priority 5 #1334 re-investigation per Task 7 recap.

**Priority 4 tasks (per Task 6 DESIGN_OPTION_1_SHORT_CIRCUIT.md):**
1. Implement Option 1 short-circuit at `src/ad/index_mapping.py::enumerate_equation_instances` (line 377) per Task 6 patch design.
2. Add supporting changes to `resolve_set_members` (line 115) and `src/ir/condition_eval.py` SetMembershipTest evaluation path.
3. Add 1 unit test (synthetic dynamic-subset case) + 1 integration test (srpchase translates).
4. Tier 0 + Tier 1 canary.
5. Re-profile srpchase under SIGALRM 900s (expected: 846s → < 10s per Task 6 projection). Re-profile iswnm + sarf + mexls + nebrazil (LOW–MEDIUM confidence per Task 6).

**Priority 5 #1334 tasks (per Task 7 AD_RESIDUALS_RECAP.md):**
1. Re-investigate the 2026-05-05 GitHub closure of #1334. Per Task 7, the otpop bug pattern is STILL VISIBLE in current main emit (2× `sum(t__, ...)` lines on `nu_kdef`) despite the closure. Determine: was the closure for a sibling sub-shape, or was it premature?
2. If sibling: file successor issue with the otpop reproducer. If premature: re-open #1334.
3. Scope and sketch the Approach 1 fix per ISSUE_1334.md (patch site `_replace_indices_in_expr` ParamRef branch at `src/kkt/stationarity.py:2448+`); document the change shape in the SPRINT_LOG.md Day 4 entry. **Do NOT commit `src/` changes on Day 4** — the Priority 5 PR is investigation + scoping only. Implementation lands Day 9 alongside #1335.

**PR14 obligation:** Priority 4 PR includes regenerated `data/gamslib/mcp/srpchase_mcp.gms` (or a comparable Tier 0/1 canary).

**Deliverable:** PR for Priority 4 Option 1 (separate from Priority 5 to keep diff scope manageable) + Day 4 #1334 investigation note in `SPRINT_LOG.md`.

### Day 5 — Checkpoint 1 + Buffer

**Branch:** `sprint26-day5-checkpoint1`.
**Effort:** ~4–6h.

**Objective:** Evaluate Checkpoint 1 (Priority 1 landed); buffer for Phase A/B slippage.

**Tasks:**
1. Targeted pipeline retest: translate + solve on the 3 models in scope (launch / srpchase / otpop) + 11 Tier 0/1 canaries. Full pipeline retest deferred to Day 13 (would cost ~3.5h here; not justified mid-sprint). Model list updated Day 3: dropped camcge / cesam2 / fawley (Phase B deferred to Sprint 27 #1381); added launch (Phase A landed Day 1 — smoke-check) + srpchase (Priority 4 Day 4 target).
2. Evaluate **Checkpoint 1** criteria below.
3. If GO: continue Days 6–7 Priorities 2 + 3 as planned.
4. If CONDITIONAL GO: scope-back current open items (Priority 4 stretch recoveries — iswnm / sarf / mexls / nebrazil — that didn't land Day 4; Priority 5 #1334 routing decision still pending); document residual scope as Sprint 27 carryforward. Phase B (camcge + cesam2) is already deferred to Sprint 27 #1381 per Day 3 — no scope-back needed there.
5. If NO-GO: assess revert vs forward-fix; potentially extend Day 5 into Day 6 to land a Phase A-only fix.

#### Checkpoint 1 criteria (Day 5 evaluation — UPDATED Day 3 per Phase B reclassification to Sprint 27 #1381)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Phase A landed: gate restored + correct emit shape + xfail removed | yes | yes | no |
| launch PATH solve to MODEL STATUS 1 | stretch — deferred to Sprint 27 #1378 | n/a | n/a |
| camcge solves to MODEL STATUS 1 | n/a — deferred to Sprint 27 #1381 | n/a | n/a |
| cesam2 solves to MODEL STATUS 1 | n/a — deferred to Sprint 27 #1381 | n/a | n/a |
| Priority 4 Option 1 short-circuit: srpchase translates | yes | n/a | no |
| Priority 4 stretch: ≥ 1 of {iswnm, sarf, mexls, nebrazil} also recovers | stretch | stretch | stretch (does not count toward routing) |
| Priority 5 #1334 routing decision documented (re-opened or successor filed) | yes | yes | no |
| Tier 0 + Tier 1 canaries (11 models) | All match golden | All match golden | > 0 regression |
| Tier 0/1/2 (54 models combined) golden-file regression | 0 regression | ≤ 1 regression (documented) | > 1 regression |

**Routing (revised Day 3 per Phase B reclassification + Priority 4/5 #1334 forward-pull to Day 4):**

- **GO** (≥ 5 of 5 gating rows green — Phase A landed + Priority 4 srpchase translates + Priority 5 #1334 routing + 2 canary rows): Continue Days 6+ as planned. **Realistic Sprint 26 Solve / Match Δ now bounded by Priority 4 (srpchase) + Priority 5 (#1334 / #1335 on otpop) only** — Phase A's launch and Phase B's camcge + cesam2 all deferred to Sprint 27 #1378 + #1381. Sprint 26 Solve / Match targets relaxed to maintain baseline.
- **CONDITIONAL GO** (Priority 4 lands srpchase but other Priority 4 candidates don't recover, OR Priority 5 #1334 routing is "successor filed" but underlying issue not yet re-opened): proceed; Day 8 buffer absorbs the partial-Priority-4 follow-up. Reclassify residual scope to Sprint 27 if needed.
- **NO-GO** (Phase A regression OR srpchase fails to translate OR canary regression > 1): Days 6+ buffer for revert + scope-back. Phase A unlikely to regress at this point (already landed Day 1 PR #1379 + validated Day 2 PR #1380 byte-stable on 54 canaries).

**Note:** stretch rows (launch PATH solve; ≥ 1 additional Priority 4 model) don't count toward GO routing; they're tracked for sprint-retrospective metrics + Day 13 final retest reporting.

**Note:** Phase B (camcge + cesam2) reclassified to Sprint 27 #1381 per Day 3 discovery — the swap-based transform doesn't generalize to plain-alias bodies. Day 3 freed; Day 4 absorbs Priority 4 Option 1 + Priority 5 #1334 re-investigation forward-pull (originally Day 8); Day 8 is now buffer.

**Deliverable:** PR (or revert) per checkpoint outcome + `SPRINT_LOG.md` Day 5 entry documenting decision.

### Day 6 — Priority 2 Pattern A Cohort Reclassification (Mechanical) + Priority 3 kand (Parallel)

**Branch:** `sprint26-day6-priority-2-and-3`.
**Effort:** ~4–6h (Priority 2 ~1.5h + Priority 3 ~3–4h kand investigation).

**Objective:** Mechanical close-and-refile per Task 4 + scope kand fix work per Task 5.

**Priority 2 tasks (per Task 4 PATTERN_A_RECLASSIFICATION_PLAN.md):**
1. **#1138** (irscge family): close-and-forward-link to Sprint 27 #1381 (Phase B redesign — camcge / cesam2 plain-alias generalization). Per Day 3 reclassification, the Phase B builder redesign that would close #1138 is deferred to Sprint 27. Forward-link to #1381 in the close comment so the cohort-issue tracking stays accurate.
2. **#1139** (meanvar): close as `not-a-bug` with note that meanvar is `legacy_excluded`.
3. **#1140** (PS-family): close as informational-mismatch with note that all 7 ps*_s* models are `non_convex` runtime-filter (per Prep Task 2).
4. **#1142** (launch): close as duplicate of Sprint 26 Priority 1 Phase A (launch fix already re-landed Day 1).
5. **#1145** (cclinpts): close-and-refile as new Sprint 27 issue per Task 4 draft title + body.
6. **#1150** (qabel + abel): close as resolved (#1311 + #1312 already CLOSED in Sprint 25; abel reclassified `non_convex`).

**Priority 3 tasks (per Task 5 PATTERN_E_STATUS.md):**
1. **#1144** (catmix): close as bucket-shifted-resolved (Sprint 25 #1338 fix recovered it; rel_diff 0.21% within tolerance).
2. **#1147** (camshape): close-and-refile as Sprint 27 issue per Task 5 draft title + body.
3. **#1141** (kand): begin scoping the alias-AD fix. Capture `SPRINT25_DAY2_DEBUG=1` trace; identify the gradient-mismatch source. Continue Day 7.

**Deliverable:** 6 GitHub issue closures + 1 Sprint 27 issue created (#1145 successor) + 2 GitHub issue closures (#1144, #1147) + 1 Sprint 27 issue created (#1147 successor); kand fix-scope notes in branch commit message or `SPRINT_LOG.md`.

### Day 7 — Priority 3 kand Fix + Test xfail Cleanup

**Branch:** `sprint26-day7-priority-3-kand`.
**Effort:** ~4–6h.

**Objective:** Land kand alias-AD fix (or carryforward to Sprint 27); un-xfail the 1 affected test per Task 4 finding.

**Tasks:**
1. Implement kand alias-AD fix per Day 6 scoping. Per Task 5, kand still has 92.5% rel_diff that didn't bucket-shift in Sprint 25; this is a genuine residual.
2. Un-xfail `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` (per Task 4 §"Test xfail impact" — the test references #1142 in its xfail reason, and #1142 closed Day 6).
3. Update `src/kkt/stationarity.py:4336` comment that references #1142 (per Task 4 §"Source ref scan").
4. If kand fix is intractable in 4–6h, close-and-refile as Sprint 27 issue (per Task 5's contingency note).
5. Tier 0 + Tier 1 + Tier 2 golden-file regression.

**PR14 obligation:** If kand fix lands, include regenerated `data/gamslib/mcp/kand_mcp.gms`.

**Deliverable:** PR for kand fix (or carryforward) + xfail-removal cleanup.

### Day 8 — Buffer (Priority 4 + Priority 5 #1334 investigation moved to Day 4)

**Branch:** none required (buffer day).
**Effort:** ~6h available.

**Reschedule note (Day 3 update):** Priority 4 Option 1 short-circuit + Priority 5 #1334 re-investigation work originally scheduled here was pulled forward to **Day 4** when Phase B reclassified to Sprint 27 #1381 freed Day 4.

**Day 8 available uses (in priority order):**

1. **Absorb Days 4 / 6 / 7 slippage** — if any priority slipped, catch up here.
2. **Forward-pull Priority 5 #1335** — originally Day 9. If Day 4's #1334 investigation completed cleanly and Day 9 can absorb #1335 start without crowding, leave on Day 9. Otherwise scope #1335 onto Day 8.
3. **Forward-pull Day 12's PR14 emit-artifact review pass** — if Day 4 + 9 produced multiple regenerated `.gms` artifacts (srpchase, otpop, possibly others), do the mid-sprint PR14 read-through here.
4. **Sprint 27 #1381 (Pattern C Phase B redesign) — start Phase B-1 design notes** if other buffer uses are exhausted. Do NOT begin src/ implementation in Sprint 26 (per Day 3 deferral); design notes only.

### Day 9 — Priority 5 #1334 Fix + #1335 Start

**Branch:** `sprint26-day9-priority-5-1334-and-1335`.
**Effort:** ~5–8h.

**Objective:** Land Priority 5 #1334 fix per Day 4 scoping. Begin #1335 fix.

**Priority 5 #1334 tasks:**
1. Complete Approach 1 implementation: ParamRef-branch alignment when `param_domain` is a strict subset of `equation_domain` AND a parallel VarRef has been substituted to use the eq domain variable (per ISSUE_1334.md §Approach 1, line 76).
2. Add unit test in `tests/unit/kkt/`: minimal `ModelIR` with scalar `kdef.. k = sum(t, p(t)*x(t))` over `t ⊂ tt`; assert no `sum(t__, ...)` wrap in `stat_x(tt)`.
3. Translate otpop fresh; verify `sum(t__, ...) * nu_kdef` lines disappear from `stat_p` and `stat_x`.

**Priority 5 #1335 tasks (per AD_RESIDUALS_RECAP.md §3.2):**
1. Implement scalar-equation gating fix at `src/ad/constraint_jacobian.py:986` + `:1107` (the `if eq_domain:` gate that currently skips `_resolve_index_offsets` + `_expand_sums_with_unresolved_offsets` for scalar equations like `zdef`).
2. Add unit test asserting `nu_zdef` cross-term emission in `stat_p` body for the otpop time-reversal-on-`p` shape.
3. Translate otpop fresh; verify `awk '/^stat_p\(.*\)\.\./, /=E= 0;/' otpop_mcp.gms | grep -c nu_zdef` returns ≥ 1 (per Task 7 §What-needs-to-be-done verification recipe).

**Deliverable:** PR for #1334 + #1335 (combined, since both touch otpop and share verification recipe). PR14 obligation: include regenerated `data/gamslib/mcp/otpop_mcp.gms`.

### Day 10 — Priority 5 Wrap + Checkpoint 2

**Branch:** `sprint26-day10-checkpoint2`.
**Effort:** ~4–6h.

**Objective:** Wrap Priority 5 (#1334 / #1335 final validation: full NLP-warm-started reproducer per Task 7 §"deferred to Sprint 26 Priority 5 fix work" — that's the acceptance gate). Evaluate Checkpoint 2.

**Tasks:**
1. Run the full otpop NLP-warm-started reproducer per ISSUE_1334.md §Diagnostic: NLP solve via baseline GAMS + dual-multiplier transfer + MCP run with `iterlim=0` + `Inf-Norm` residual capture on `stat_x('1990')` ≈ 760 (pre-fix) → ≈ 0 (post-fix).
2. Confirm otpop's NLP-warm-started MCP converges to `pi ≈ 4217.80` (matches NLP, per ISSUE_1334.md §Diagnostic).
3. Targeted pipeline retest on the 3 Priority-affected models in scope (srpchase, kand, otpop) + the 11 Tier 0/1 canaries. (camcge + cesam2 deferred to Sprint 27 #1381 per Day 3.)
4. Evaluate **Checkpoint 2** criteria below.

#### Checkpoint 2 criteria (Day 10 evaluation — UPDATED Day 3 per Phase B reclassification)

| Criterion | GO | CONDITIONAL GO | NO-GO |
|---|---|---|---|
| Match Δ vs Day 0 | ≥ +1 | ≥ 0 (maintain) | ≤ -1 |
| Solve Δ vs Day 0 | ≥ +1 | ≥ 0 (maintain) | ≤ -1 |
| Priority 1 Phase A landed | yes (already true — PR #1379) | yes | no |
| Priority 4 srpchase translates | yes | n/a | no |
| Priority 5 otpop NLP-warm-started MCP residual ≈ 0 | yes | rel_diff < pre-fix but not 0 | no improvement |
| Tier 0 + Tier 1 canaries | All match golden | All match golden | > 0 regression |

**Δ-threshold rationale (revised Day 3):** Original Δ targets (≥ +3 Solve / ≥ +3 Match) assumed Phase B would contribute +2 Solve / +2 Match from camcge + cesam2. With Phase B deferred to Sprint 27 #1381, realistic Sprint 26 max Δ is bounded by Priority 4 (srpchase translate recovery, +1 Solve if PATH solves) + Priority 5 (#1334 / #1335 otpop fix, +1 Solve potentially). GO Δ relaxed to ≥ +1; CONDITIONAL GO Δ relaxed to maintain (≥ 0); NO-GO Δ relaxed to ≤ -1 (actual regression).

- **GO** (≥ 5 of 6 rows green): Days 11–13 proceed per planned schedule (PR19 implementation + buffer + final retest).
- **CONDITIONAL GO** (3–4 of 6 green): Days 11–13 trim scope. PR19 may slip to a Day-12 fast-track implementation; Day 12 buffer reabsorbed for Priority 5 follow-up if otpop didn't fully resolve.
- **NO-GO** (≤ 2 of 6 green, OR any regression in Match / Solve / canaries): Days 11–12 buffer for revert + scope-back; Day 13 final retest captures whatever shipped.

**Deliverable:** Checkpoint 2 decision documented in `SPRINT_LOG.md` Day 10 entry.

### Day 11 — PR19 CI Extension Implementation

**Branch:** `sprint26-day11-pr19-ci-extension`.
**Effort:** ~4–8h.

**Objective:** Implement PR19 per Task 8 design. The design doc (`DESIGN_PR19_SOLVE_TIME_CI.md`) specifies the workflow YAML, target list, helper scripts, and SHA256-pinned GAMS demo install.

**Tasks:**
1. Land `.github/workflows/pr19-emit-solve-validation.yml` per Task 8 §"Draft Workflow YAML".
2. Land `.github/path-solve-ci-targets.txt` per Task 8 §"Target Model List" (15 models = 11 Tier 0/1 hard-fail + 4 Pattern C soft-fail).
3. Land `scripts/ci/parse_pr19_targets.py` (~30 LOC per Task 8) + `scripts/ci/run_pr19_solves.py` (~80 LOC per Task 8).
4. Capture the GAMS installer SHA256 (per Task 8 Open Questions Q1) and replace the `<TO BE FILLED IN BY SPRINT 26 IMPLEMENTATION>` placeholder.
5. Smoke-test PR19 on this branch: open this PR, observe the workflow fires (this PR touches `.github/workflows/`), and verify the bypass path works by adding the `skip-emit-solve-ci` label.
6. **Promotion check:** Phase B (camcge / cesam2) deferred to Sprint 27 #1381 per Day 3 — leave `tier=pattern-c` on those rows in `.github/path-solve-ci-targets.txt` (soft-fail). Promotion to `tier=1` is a Sprint 27 task after the Phase B redesign lands.

**Deliverable:** PR for PR19 CI extension implementation.

### Day 12 — Buffer / PR14 Emit-Artifact Review Pass

**Branch:** `sprint26-day12-buffer`.
**Effort:** ~4–6h.

**Objective:** Mid-sprint "read the regenerated `.gms`" pass on the models with emit changes this sprint per PR14 reaffirmation in CONTRIBUTING.md (Task 10). Buffer for any Days 1–11 slippage.

**Tasks:**
1. Read `data/gamslib/mcp/launch_mcp.gms` (Phase A, Day 1), `srpchase_mcp.gms` (Priority 4, Day 4), `otpop_mcp.gms` (Priority 5, Day 9), plus any other artifacts that regenerated this sprint, end-to-end. Look for clobber patterns / ordering bugs / spurious Sum-wraps / missing cross-terms (per Task 10 reviewer-checklist + CONTRIBUTING.md §"What reviewers must do"). Model list updated Day 3: dropped camcge / cesam2 / fawley (Phase B deferred to Sprint 27 #1381).
2. If any new bugs surface: file as Sprint 27 issues unless trivially fixable in 1–2h.
3. Buffer: absorb any Days 1–11 slippage. Examples:
   - PR19 implementation slipped to Day 12 → finish here.
   - Priority 5 otpop full reproducer didn't pass Day 10 → Day 12 deep-dive.
   - Priority 1 Phase B regressions on Tier 2 models needed scope-back → finalize.
4. **NO new architectural work** — this is buffer, not slip-prevention.

**Deliverable:** PR (if any work landed) + Sprint 27 carryforward issues (if any).

### Day 13 — Final Pipeline Retest + Sprint Close

**Branch:** `sprint26-day13-final-retest`.
**Effort:** ~3–6h.

**Objective:** Full pipeline retest (per PR6); compare against Day 0 baseline (Task 9 BASELINE_METRICS.md) with explicit bucket-provenance evaluation (per PR17). File Sprint 26 retrospective scaffold.

**Tasks:**
1. Run `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~3h estimated based on Task 9 Day 0 baseline timing).
2. Compare per-bucket counts vs Day 0:
   - Parse, Translate, Solve, Match (headline metrics)
   - path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license (failure-bucket counts)
   - Per-model bucket-provenance table per PR17 (Task 9 §4 format) — distinguish bucket churn from real regressions.
3. Update `data/gamslib/gamslib_status.json` (commit per Sprint 25 Day 14 convention).
4. Compose Sprint 26 final-headline-metrics block in `SPRINT_LOG.md` Day 13.
5. Compose Sprint 26 retrospective scaffold (`SPRINT_RETROSPECTIVE.md`) — what went well / what didn't / process recommendations for Sprint 27.
6. Update `CHANGELOG.md` Sprint 26 Summary entry.
7. Update `PROJECT_PLAN.md` Sprint 26 Final Status footnote (per Sprint 25 footnote ⁶ precedent).
8. File Sprint 27 carryforward issues (label `sprint-27`):
   - Any unaddressed Priority 1–5 work from Days 1–10 Checkpoint outcomes.
   - #1357 (otpop comp_up subset/superset, deferred per Task 7).
   - #1356 (fawley comp_up subset/superset, deferred per Task 4).
   - #1374 (emit duplicate-init bugs, surfaced during Task 9 PR review).
   - #1224 (mine ParamRef IndexOffset, deferred per Task 6).

**Deliverable:** PR with `gamslib_status.json` update + `SPRINT_LOG.md` Day 13 + `SPRINT_RETROSPECTIVE.md` + `CHANGELOG.md` Sprint 26 Summary + Sprint 27 carryforward issues filed.

---

## Process Requirements (Carried Forward + New)

- **PR6** (Full pipeline for definitive metrics): Day 5 targeted retest + Day 10 targeted retest + Day 13 full retest.
- **PR7** (Track gross fixes vs gross influx): per-bucket transitions in `SPRINT_LOG.md` daily entries.
- **PR8** (Absolute counts and percentages): all metrics tables in `SPRINT_LOG.md` follow Sprint 25 format.
- **PR9** (Targets against frozen 142-scope): all Sprint 26 targets calibrated against the Day 0 142-scope baseline.
- **PR10** (Error influx budgets): same Sprint 25 calibration applies — alias-AD/Pattern C 30%, emitter recovery 80–100%, multi-solve gate 0%.
- **PR12** (Determinism harness): unchanged — runs every PR per existing `tests/integration/test_pipeline_determinism.py`.
- **PR14 reaffirmation** (per Task 10): every emit-affecting PR includes a regenerated `_mcp.gms` artifact in the diff (CONTRIBUTING.md hard rule). Day 12 dedicated mid-sprint review pass.
- **PR15** (Scope freeze): 142-scope locked per Task 9 BASELINE_METRICS.md §5; no mid-sprint exclusion edits.
- **PR16** (Pre-Sprint hypothesis validation): applied to Priority 1 in Task 3 (PATTERN_C_HYPOTHESIS_VALIDATION.md).
- **PR17** (Bucket-provenance baseline): applied in Task 9 BASELINE_METRICS.md §4. Day 13 final retest extends with Day-13-vs-Day-0 transitions.
- **PR18** (Scope-shift identification): applied in Task 2 (Sprint 25 abel reclassification documented).
- **PR19** (Pre-merge solve-time validation CI): designed in Task 8; implementation Day 11.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Priority 1 Phase A consolidated builder rewrite breaks > 1 Tier 2 model | Medium | High | Day 5 Checkpoint 1 NO-GO routing; Day 1 keeps the prototype branch isolated until Day 2 validation. Sprint 25 #1351 rollback experience documented in Task 3 §Recommendation. |
| Priority 5 #1334 GitHub closure was premature; otpop bug doesn't actually resolve with documented Approach 1 | Medium | Medium | Day 4 re-investigation budgeted ~3–4h before committing to fix work. If Approach 1 doesn't work, Approach 2 fallback per ISSUE_1334.md §Approach 2 (targeted suppression in `_add_indexed_jacobian_terms`). If both fail, scope-back Priority 5 to #1335-only and Sprint 27-carryforward #1334. |
| Priority 4 Option 1 short-circuit recovers srpchase but breaks Tier 0/1 canary determinism | Low | Medium | Per Task 6 §"Determinism preserved by construction" — placeholder uses domain set names, no `set`/`dict` iteration, PR12 byte-stable harness will validate. If determinism breaks, revert + Sprint 27 carryforward. |
| Day 0 machine-variance churn-outs (clearlak / ganges / turkpow translate timeouts) recover via Priority 4 but headline reads as +3 path_syntax_error regression | High | Low | Day 13 retest applies bucket-provenance evaluation per PR17 (Task 9 §4.3) — explicit table distinguishes bucket churn from real regression. CHANGELOG narrates the disambiguation. |
| PR19 CI extension implementation slips past Day 11 due to GAMS demo installer issues | Medium | Low | Task 8 §"Open Questions" already flagged installer URL stability + license activation + caching as Sprint 26 implementation risks. Day 11 has 4–8h budget; Day 12 buffer absorbs slip if needed. Self-hosted runner with full GAMS license is the documented fallback per Task 8 design. |

---

## Related Documents

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 26 (lines 931–1019) — sprint goal, components, deliverables, acceptance criteria, estimated effort, risk level.
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"Sprint 26 Recommendations" + §"What We'd Do Differently" — Priorities 1–5 + PR16–PR19 + PR14 reaffirmation rationale.
- `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` — 11 prep tasks completed before Day 0.
- `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` — 26 unknowns, all VERIFIED before Day 0.
- `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` — Day 0 baseline + bucket-provenance.
- `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` — Task 3 REPLAN recommendation that drives Day 1 + Day 5 Checkpoint 1 routing.
- `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` — Task 4 per-issue Day 6 plan.
- `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` — Task 5 per-issue Day 6/7 plan.
- `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` — Task 6 patch design + test fixtures.
- `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md` — Task 7 #1334/#1335 fix-site detail.
- `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` — Task 8 PR19 design that drives Day 11.
- `CONTRIBUTING.md` §"Emit-Affecting PRs" — Task 10 PR14 reaffirmation rule applied to all emit-affecting PRs Days 1–11.
- `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts (companion to this PLAN.md).
