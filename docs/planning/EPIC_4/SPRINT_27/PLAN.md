# Sprint 27 Detailed Schedule (Day 0 + Days 1–13)

**Status:** ✅ READY — Sprint 27 prep complete (all 11 prep tasks; PRs #1402–#1411 merged); Sprint 27 ready to kick off Day 0
**Date:** 2026-05-31
**Owner:** Sprint 27 engineer
**Codifies:** Sprint 27 Prep Task 11 (Plan Sprint 27 Detailed Schedule)
**Inputs:** All 10 Sprint 27 prep-task deliverables (Tasks 1–10) + `PROJECT_PLAN.md` §"Sprint 27" canonical priorities + Sprint 26 PLAN.md structural reference

---

## 1. Sprint 27 Goal

Per `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27":

> Land the four Sprint 26 close-and-refile architectural reclassifications (#1381 Pattern C Phase B, #1385 Option 1 short-circuit, #1390 kand AD architecture, #1393 scalar-eq Sum-collapse) + tighten the Phase A Pattern C gate predicate that regressed 15 non-target models in Sprint 26 (#1398). Address comp_up subset/superset workstream (#1356 fawley + #1357 otpop), launch PATH-numerics divergence (#1378), in-place scalar-equation cross-term carryforward (#1335), mine ParamRef IndexOffset (#1224), and Day 6 close-and-refile carryforwards (#1387 cclinpts, #1388 camshape). Apply Sprint 26 retrospective process recommendations PR20–PR23. Fix the pre-existing pipeline absolute-path leak (#1400). **Push Match 59 → ≥ 66 and Solve 103 → ≥ 111.**

---

## 2. Acceptance Criteria (from PROJECT_PLAN.md §"Sprint 27" §Acceptance Criteria)

| Metric | Day 0 baseline | Sprint 27 target | Δ |
|---|---|---|---|
| **Solve** | 103 | ≥ 111 | +6 firm (#1381 ×2, #1398 qdemo7, #1357, #1356, #1388 per `PROJECT_PLAN.md` Sprint 27 §"Acceptance Criteria") + 2 conditional (#1385, #1224). **Caveat per Task 8 / `PRIORITY_7_FIX_SURFACE.md`:** #1388 is conditional on the Day 11 §4.6 3-way discriminator — Case (a)/(b) → +1 firm Solve as documented; Case (c) → Sprint 28 carryforward → +5 firm + 2 conditional = **+7 in Sprint 27 (Solve = 110, one below the ≥ 111 target) even with BOTH conditional gains landing**. Closing the +1 gap requires either an additional Sprint 27 recovery (e.g., #1374 fix surfacing a previously-blocked solve, or an opportunistic P6/P7/P8/P9 Day 10–12 gain) or a target revision recorded in the Day 13 retrospective (see §17 Risk Register). |
| **Match** | 59 | ≥ 66 | +7 firm (#1381 ×2, #1398 qdemo7, #1357, #1356, #1378, #1390) |
| **path_syntax_error** | 14 (was 17 at Sprint 26 final; 3 machine-variance churn into translate_timeout) | ≤ 6 | −8 to ≤ 6 |
| **path_solve_terminated** | 5 | ≤ 5 (maintain) | 0 |
| **model_infeasible** | 4 | ≤ 3 | −1 (#1388 camshape) |
| **Translate** | 131 (134 at Sprint 26 final; 3 timeout churn) | ≥ 135/142 | +4 firm + variance recovery |
| **Parse** | 142/142 | ≥ 142/142 | maintain 100% |
| **Tests** | 4,737 | ≥ 4,750 | +13 |
| **Determinism** | n/a | Byte-identical under ≥ 3 `PYTHONHASHSEED` values | new (PR12 guard) |
| **Process recs** | n/a | PR20 codified + 4 Phase 0 backlog sections authored; PR21 codified; PR22 script landed; PR23 checklist landed | done in prep (Tasks 2–10) |
| **PR19 widening** | 11 models | 30 models (12 Tier 0/1 + 18 Pattern C) | done Day 0 per Task 5 |

Per `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §2 — Sprint 27 Day 0 baseline frozen 2026-05-28 at Solve=103, Match=59, path_syntax_error=14, model_infeasible=4, Translate=131/142, Tests=4,737. The Day 0 numbers reflect machine-load variance pushing 3 models into translate_timeout — these are NOT Sprint 27 regressions.

---

## 3. Sequencing Constraints (from PREP_PLAN.md §Task 11 + prep-task outputs)

1. **Day 0 ONLY:** PR19 widening (Task 5; 10-min edit to `.github/path-solve-ci-targets.txt`) + Phase 0 codification application (Task 2; CONTRIBUTING.md §"Phase 0 Acceptance Gates" already merged) + AD architectural Phase 0 validation experiments (Task 6 PROCEED/REPLAN signal for #1390/#1385/#1393; ~3h on Day 0).
2. **Day 0 precedes Day 1 Priority 1 work** — the PR19 widening must be in place BEFORE the tightened gate predicate from #1398 lands, so similar gate-overreach catches at PR-review time.
3. **Priority 3 commits (starting Day 5 per §8) are PHASE-0-GATED** — Day 0 experiment results for #1390 / #1385 / #1393 determine which sub-priorities PROCEED at Day 5+ vs REPLAN to Sprint 28. (Day 4 is Priority 2 / #1381 Pattern C Phase B redesign, not Priority 3.) If any P3 sub-priority REPLANs, its budget rolls to Day 13 buffer.
4. **Priority 6 #1224 may bundle with Priority 3 #1385** (both touch `src/ad/index_mapping.py`) — Day 0 inspection of the file's structure determines bundle vs standalone (KU 6.1).
5. **Pipeline retest checkpoints:** Day 5, Day 10, Day 13 per PR6 — each invokes the PR22 audit script (`scripts/sprint_audit/changed_emit_artifacts.py`) to enumerate `*_mcp.gms` artifacts changed since the Day 0 anchor commit.
6. **Phase 0 gate is HARD** for any PR touching `src/ad/`, `src/kkt/`, or `src/emit/` — per PR20 codification in CONTRIBUTING.md (merged Sprint 27 prep Task 2 / PR #1403).
7. **PR14 reaffirmation** on every emit-affecting PR (regenerated `.gms` diff in the PR) — per CONTRIBUTING.md §"Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)".
8. **PR23 self-review** on any PR whose diff touches `.github/workflows/*.yml`/`.yaml`, `scripts/ci/*`, or `.github/actions/*` — 32-item checklist per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)". **PR23 does NOT apply to** pure `src/` PRs (those follow PR14 + PR20), nor to the Day 0 PR19 widening (which edits `.github/path-solve-ci-targets.txt` only and is outside PR23 scope per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope").

---

## 4. Day 0 — Sprint Kickoff (≤ 8h)

**Focus:** PR19 widening + Day-0 baseline + AD Phase 0 validation experiments → PROCEED/REPLAN binding signals for Priority 3 sub-priorities.

**Tasks:**

| # | Task | Effort | Deliverable |
|---|---|---|---|
| 0.1 | **Record Day 0 anchor commit SHA** in BOTH this PLAN.md §"Day 0 Anchor SHA" subsection below AND `SPRINT_LOG.md` §"Day 0 Anchor SHA" (top-level field near the beginning of that file). The SHA is used by the PR22 script for all mid-sprint retests; both files must carry the same recorded SHA so neither stays at `**TBD**`. | 0.1h | SHA recorded in both PLAN.md and SPRINT_LOG.md |
| 0.2 | **Run PR22 audit script** (`scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA>`) to produce the Day-0 audit baseline (should be empty — no emit changes yet). | 0.1h | `/tmp/sprint27_day0_baseline.md` (expected empty) |
| 0.3 | **PR19 widening** — edit `.github/path-solve-ci-targets.txt` per `PR19_WIDENING_DESIGN.md` §6 (add launch as Tier 1 hard-fail + 14 net-new #1398-affected models as Pattern C soft-fail). Open PR. PR23 self-review NOT required — the targets file is outside PR23 scope per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope". | 1h | PR open |
| 0.4 | **AD architectural Phase 0 validation experiment for #1390 kand** (per `PRIORITY_3_RISK_ASSESSMENT.md` §3 / Task 6). Prototype patch at `constraint_jacobian.py:903/1027` (predicate-guarded Sum vs per-instance enumeration); regenerate `kand_mcp.gms`; verify 22 phantom-offset terms collapse to 1. | 1h | Binding PROCEED/REPLAN signal recorded in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 |
| 0.5 | **AD architectural Phase 0 validation experiment for #1385 srpchase** (Option B runtime-guard). Prototype at `index_mapping.py:377` + `stationarity.py`; regenerate `srpchase_mcp.gms`; verify clean compile. | 1h | Binding PROCEED/REPLAN signal |
| 0.6 | **AD architectural Phase 0 validation experiment for #1393+#1335 otpop** (Approach C: extend `_is_concrete_instance_of` for symbolic supersets). Prototype at `derivative_rules.py:2607`; regenerate `otpop_mcp.gms`; verify `pi ≈ 4217.80` matches NLP. | 1h | Binding PROCEED/REPLAN signal |
| 0.7 | **Priority 1 Phase 0 — start hand-derivation on first 2 of 8 anchors** (launch + qdemo7 per `PRIORITY_1_ANCHOR_MAPPING.md` §4.1–4.2). Remaining 6 anchors continue on Day 1. | 2h | Hand-derived KKT for launch `stat_weight(s)` + qdemo7 `stat_xcrop(c)`; recorded in working notes |
| 0.8 | **KU 6.1 inspection** — read `src/ad/index_mapping.py` to decide bundle-with-#1385 vs standalone for #1224 (per `PRIORITY_3_RISK_ASSESSMENT.md` discussion + Unknown 6.1 research questions). | 0.5h | Bundle decision recorded in KU 6.1 |
| 0.9 | **Mid-day Day 0 wrap** — update KNOWN_UNKNOWNS.md: KUs 3.1/3.2/3.3 (Priority 3 sub-priority PROCEED/REPLAN) and 6.1 (bundle decision) move 🔍 INCOMPLETE → ✅ VERIFIED. Update PLAN.md with binding sub-priority budget allocations for Days 5–9 based on PROCEED count. | 0.8h | KU updates committed |

**Day 0 Anchor SHA:** `148662a5cfba7034920965e1c4e3bb38e40be184` — `main` tip at Sprint 27 Day 0 kickoff (2026-06-01). Used by `scripts/sprint_audit/changed_emit_artifacts.py --since-commit <SHA>` for every mid-sprint retest (Days 5, 10, 13).

**Day 0 success criteria:**
- [ ] PR19 widening PR opened (the `.github/path-solve-ci-targets.txt` edit is outside PR23 scope; PR description includes the rationale and the dry-run validation evidence from `PR19_WIDENING_DESIGN.md` §6).
- [ ] All 3 Priority 3 sub-priorities have binding PROCEED or REPLAN signals recorded in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5.
- [ ] 2 of 8 Priority 1 anchor KKT shapes hand-derived.
- [ ] KU 6.1 (#1224 bundle decision) ✅ VERIFIED.
- [ ] Day 0 anchor SHA recorded in BOTH PLAN.md §4 "Day 0 Anchor SHA" AND SPRINT_LOG.md §"Day 0 Anchor SHA".

---

## 5. Days 1–3 — Priority 1: Phase A Gate-Predicate Tightening (#1398) (~28h total; P1 budget 10–14h)

**Day-budget allocation:** Day 1 = 10h, Day 2 = 10h, Day 3 = 8h (sum 28h; matches the §14 Budget Summary table). The Day 1–3 budget exceeds the P1-only budget (10–14h) because Day 3 includes 3h of P2 Phase 0 hand-derivation (camcge `nu_ieq`) as the transition step into Day 4.

### Day 1 (~10h) — Phase 0 anchor completion + first prototype

| Task | Effort | Notes |
|---|---|---|
| Complete Phase 0 hand-derivation for 6 remaining anchors (ferts, sambal, ganges, sroute, turkpow, dinam) per `PRIORITY_1_ANCHOR_MAPPING.md` §4.3–4.7 | 5h | 7 distinct emit shapes covered; dinam has 2 distinct sub-shapes per §4.7 |
| Implement first prototype of tightened gate predicate at `src/kkt/stationarity.py` `_find_pattern_c_alias_sum` (per Task 6 Day 0 experiment + Task 4 anchor mapping) | 3h | Use Day 0 experiment-derived predicate signature |
| Regenerate `*_mcp.gms` for 8 anchors; byte-compare against hand-derived shapes | 1.5h | Per-anchor verification grep specs in `PRIORITY_1_ANCHOR_MAPPING.md` §4 |
| Buffer / commit | 0.5h | |

### Day 2 (~10h) — Full regression + PR open

| Task | Effort | Notes |
|---|---|---|
| Regenerate `*_mcp.gms` for all 15 #1398-affected models + launch | 2h | Per `BASELINE_METRICS.md` §6 affected-models list |
| Run pipeline tests + bucket-provenance check for affected models | 2h | qdemo7 must return to `compare_match`; egypt/ferts/shale to `path_solve_license`; etc. |
| Tier 0/1 byte-stability verification (regenerate all 12 Tier 0/1 canaries, diff vs main) | 1h | Per PR19 widening Task 5 |
| Author PR description (PR14 reaffirmation + PR20 Phase 0 acceptance-gate cross-reference) | 2h | Regenerated `.gms` diffs included in PR; PR description cross-references `PRIORITY_1_ANCHOR_MAPPING.md` §4 anchor-by-anchor hand-derived KKT shapes. PR23 not applicable — pure `src/kkt/stationarity.py` change, no workflow/CI files touched |
| Open PR; respond to first review iteration | 3h | |

### Day 3 (~8h) — PR review iteration + merge + transition

| Task | Effort | Notes |
|---|---|---|
| PR review iteration (target: ≤ 2 rounds; PR14 + PR20 disclosures pre-filled so reviewer can verify regenerated `.gms` against hand-derived KKT directly) | 3h | |
| Merge PR | 0.5h | |
| Verify PR19 widening CI fires correctly on the merged commit | 0.5h | Per Task 5 §7 PR-runtime projection |
| Start P2 Phase 0 hand-derivation for camcge `nu_ieq` cross-term (per `PROJECT_PLAN.md` Priority 2) | 3h | KU 2.1 still 🔍 INCOMPLETE; Day 0 PR19 widening Day 4 P2 commits gated on this |
| Buffer | 1h | |

**P1 success criteria:**
- [ ] 15 #1398-affected models recover to Day 0 baseline buckets (qdemo7 → compare_match; egypt/ferts/shale → path_solve_license; etc.).
- [ ] launch byte-stable vs Sprint 26 final emit (per KU 4.2).
- [ ] PR19 target list widened to 30 models per Task 5.
- [ ] All 4 Phase 0 KUs 1.1–1.4 ✅ VERIFIED (1.3 moves from INCOMPLETE).

---

## 6. Day 4 — Priority 2: Pattern C Phase B Redesign (#1381) (~12h; P2 budget 10–16h)

**Focus:** Land Pattern C Phase B redesign; camcge + cesam2 unblock to compare_match.

| Task | Effort | Notes |
|---|---|---|
| Finalize P2 Phase 0 hand-derivation (camcge + cesam2 `nu_ieq` cross-term) | 2h | Continuation from Day 3 |
| Implement Phase B build-from-source-Sum-body approach at `src/kkt/stationarity.py` | 4h | Per `PROJECT_PLAN.md` Priority 2 + Task 6 PROCEED-gated approach |
| Regenerate camcge + cesam2; verify hand-derived KKT byte-stable | 1.5h | KU 2.1 ✅ VERIFIED |
| Tier 0/1 canary byte-stability check (KU 2.3) | 1h | KU 2.3 ✅ VERIFIED |
| Author PR description (PR14 + PR20 Phase 0 cross-reference); open PR. PR23 not applicable — pure `src/kkt/stationarity.py` change | 2.5h | |
| Buffer / PR review prep | 1h | |

**P2 success criteria:**
- [ ] camcge + cesam2 unblock from `path_syntax_error` to `compare_match` (+2 Solve, +2 Match).
- [ ] #1381 closed.
- [ ] KUs 2.1, 2.2, 2.3 ✅ VERIFIED.

---

## 7. Day 5 — Checkpoint 1: Pipeline Retest + Priority 5 start + Priority 3 start (~10h)

**Focus:** Mid-sprint Checkpoint 1 (per PR6 / Sprint 26 retest cadence); start Priority 5 (comp_up) + Priority 3 first sub-priority.

| Task | Effort | Notes |
|---|---|---|
| **Run PR22 audit script** (`--since-commit <Day-0 SHA> --format markdown --mode retest`) → paste into SPRINT_LOG.md Day 5 entry | 0.5h | Should surface P1 #1398 + P2 #1381 regenerated artifacts |
| **Full pipeline retest** (`.venv/bin/python scripts/gamslib/run_full_test.py --quiet`) — checkpoint 1 | 3h (background) | Headline metrics + bucket-provenance update per PR17 |
| Author Day 5 SPRINT_LOG.md entry with checkpoint metrics + bucket-provenance table | 1h | |
| **Priority 5 #1356 fawley** — Phase 0 hand-derivation + first prototype patch per `PRIORITY_5_FIX_SURFACE.md` §3 (patch sites `complementarity.py:473-483` + `:485-494`) | 4h | KU 5.1 ✅ VERIFIED at prep; Day 5 implementation per §8 handoff |
| **Priority 3 first PROCEED sub-priority** (per Day 0 binding signal): if #1390 PROCEEDs → start implementation; else if #1385 → start; else if #1393 → start. Land first patch + regenerate. | 1.5h start | Continued Days 6–7 |

**Checkpoint 1 success criteria** (P1 merged Day 3 + P2 merged Day 4 → both gains expected at Day 5 retest):
- [ ] Pipeline retest shows **Solve ≥ 106** (Day 0 103 + **#1398 qdemo7 +1** from P1 Day 3 merge + #1381 camcge/cesam2 +2 from P2 Day 4 merge = 106).
- [ ] Pipeline retest shows **Match ≥ 62** (Day 0 59 + **#1398 qdemo7 +1** + #1381 ×2 = 62).
- [ ] PR22 script output includes camcge_mcp.gms + cesam2_mcp.gms + 15 #1398-affected `*_mcp.gms` artifacts + launch byte-stable diff.
- [ ] P5 #1356 Phase 0 hand-derivation complete; first prototype committed.

**Note:** Checkpoint 1 must catch a failed P1 #1398 recovery. If Solve = 105 / Match = 61 (i.e., only camcge+cesam2 recovered) the checkpoint **FAILS** even though +2 landed — that pattern indicates qdemo7 (and possibly other #1398-affected models) did not return to their Day 0 baseline buckets, requiring a Day 5/6 P1 re-investigation before Priority 3 begins.

---

## 8. Days 6–8 — Priority 3: AD Architectural Redesigns (#1390, #1385, #1393+#1335) + parallel Priority 5 (~36h total; P3 budget 30–48h)

**Day-budget allocation:** Day 6 = 12h, Day 7 = 12h, Day 8 = 12h.

**Sub-priority sequencing:** Serial implementation (per `PRIORITY_3_RISK_ASSESSMENT.md` §3.4 / KU 3.4 binding decision — serial preferred over coordinated; per-sub-priority Phase 0 gates passed independently on Day 0). Order: #1390 → #1385 → #1393+#1335 (driven by patch-site independence; #1390 in `constraint_jacobian.py`, #1385 in `index_mapping.py` + `stationarity.py`, #1393+#1335 in `derivative_rules.py`).

### Day 6 (~12h) — #1390 kand + P5 #1357 otpop start

| Task | Effort | Notes |
|---|---|---|
| #1390 implement predicate-guarded Sum at `constraint_jacobian.py:903 + :1027` | 6h | Per Task 6 Day 0 PROCEED + binding patch shape |
| #1390 Phase 0 verify (22 phantom-offset → 1; hand-derived KKT match on kand `stat_y(j,t,n)`) | 1.5h | KU 3.1 ✅ VERIFIED |
| #1390 Tier 0/1 byte-stability check | 1h | |
| **Priority 5 #1357 otpop** — Phase 0 + first patch (parallel; same patch sites as #1356) | 3h | KU 5.2 ✅ VERIFIED at prep (only 2 models in scope per fawley + otpop) |
| Buffer | 0.5h | |

### Day 7 (~12h) — #1390 PR + #1385 srpchase + P5 close

| Task | Effort | Notes |
|---|---|---|
| #1390 PR open (PR14 + PR20 Phase 0 cross-reference; PR23 not applicable — pure `src/ad/constraint_jacobian.py` change) + first review iteration | 3h | |
| #1385 implement Option B runtime-guard at `index_mapping.py:377` + `stationarity.py` | 6h | Per Task 6 PROCEED + Day 0 binding patch shape |
| #1385 Phase 0 verify (srpchase translates cleanly; KU 3.2 ✅ VERIFIED) | 1.5h | |
| **Priority 5 close** — PR open for combined fawley + otpop fix; Tier 0/1 clearlak byte-stability (KU 5.3 mitigation) | 1.5h | |

### Day 8 (~12h) — #1385 PR + #1393+#1335 otpop + P7 #1387 start

| Task | Effort | Notes |
|---|---|---|
| #1385 PR open (PR14 + PR20 Phase 0 cross-reference; PR23 not applicable — pure `src/ad/index_mapping.py` + `src/kkt/stationarity.py` change) + review iteration | 3h | |
| #1393+#1335 implement Approach C at `derivative_rules.py:2607` per Task 6 PROCEED | 5h | KU 3.3 ✅ VERIFIED at Day 0; binding approach selected |
| #1393+#1335 Phase 0 verify (otpop `pi ≈ 4217.80` matches NLP) | 1.5h | |
| **Priority 7 #1387 cclinpts** — Phase 0 hand-derivation (sign-flip + term-omission per `PRIORITY_7_FIX_SURFACE.md` §3) | 2h | KU 7.1 ✅ VERIFIED at prep |
| Buffer | 0.5h | |

**P3 success criteria:**
- [ ] #1390 kand cross-term reduces 22 → 1; closed.
- [ ] #1385 srpchase translates cleanly; iswnm/mexls/nebrazil/sarf unblock (+1 conditional Solve).
- [ ] #1393+#1335 otpop solves with `pi ≈ 4217.80`; #1335 closed.
- [ ] KUs 3.1–3.5 ✅ VERIFIED.

**P5 success criteria:**
- [ ] fawley + otpop unblock from `path_syntax_error` to `compare_match` (+2 Solve, +2 Match).
- [ ] #1356, #1357 closed.
- [ ] KUs 5.1–5.3 ✅ VERIFIED.

---

## 9. Day 9 — Priority 3 close + Priority 4 launch numerics start (~10h)

| Task | Effort | Notes |
|---|---|---|
| #1393+#1335 PR open + review iteration | 3h | |
| #1390/#1385/#1393 PR merges (any PRs still open from Days 6–8) | 1.5h | |
| **Priority 4 #1378 launch numerics** — investigate per `PROJECT_PLAN.md` Priority 4 (initial-point tuning, `--nlp-presolve`, NLP-warm-start, sign/scaling refinement); pick approach per KU 4.1 | 4h | KU 4.1 🔍 INCOMPLETE → ✅ VERIFIED |
| Buffer / context-switch overhead | 1.5h | |

**P4 success criteria:**
- [ ] launch MODEL STATUS 1 (or `model_optimal_presolve` recovery) with matching solution.
- [ ] #1378 closed.
- [ ] KU 4.1 ✅ VERIFIED; KU 4.2 (launch byte-stability anchor preserved) confirmed.

---

## 10. Day 10 — Checkpoint 2: Pipeline Retest + Priority 4 close + Priority 7 #1387 implement (~10h)

| Task | Effort | Notes |
|---|---|---|
| **Run PR22 audit script** (`--since-commit <Day-0 SHA>`) → paste into SPRINT_LOG.md Day 10 entry | 0.5h | Should now include P1+P2+P3+P5 artifacts (large diff) |
| **Full pipeline retest** — checkpoint 2 | 3h (background) | Per PR6 cadence |
| Author Day 10 SPRINT_LOG.md entry with metrics + bucket-provenance | 1h | |
| **Priority 4 close** — PR open + merge launch fix | 2h | |
| **Priority 7 #1387 cclinpts** — implement sign-flip + term-omission fixes at `derivative_rules.py:1847` + `stationarity.py:1352/1835` per `PRIORITY_7_FIX_SURFACE.md` §3 | 3.5h | |

**Checkpoint 2 success criteria** (P1 merged Day 3 + **P2 merged Day 4** (matching the Checkpoint 1 assumption that P2's gains appear in the Day 5 retest) + P5 Days 7–8 + P3 #1390 Day 7 + P3 #1385+#1393+#1335 Day 9 + P4 #1378 Day 10 → most planned Match recoveries should already be at the Sprint final target):
- [ ] **Solve ≥ 108** (Day 0 103 + 5 firm: **#1398 qdemo7 +1**, #1381 camcge/cesam2 +2, #1357 otpop +1, #1356 fawley +1). Launch's #1378 is a Match gain (mismatch → match), not Solve — corrected from the earlier "launch via #1378" attribution.
- [ ] **Match ≥ 66** (Day 0 59 + 7 firm: **#1398 qdemo7 +1**, #1381 ×2, #1357 +1, #1356 +1, **#1390 kand mismatch→match +1**, **#1378 launch mismatch→match +1** = +7 → 66). This already matches the Sprint 27 final target — Checkpoint 2 must NOT pass at Match = 63 with multiple planned recoveries silently failing.
- [ ] **path_syntax_error ≤ 6** (final target reached at Checkpoint 2 since P1 + P2 + P5 — the path_syntax_error contributors — all merge by Day 9). Day 0 14 − #1398 reductions (qdemo7, dinam, egypt, ferts, gangesx, shale, turkpow recoveries) − #1381 (camcge, cesam2) − #1357 (otpop) − #1356 (fawley) → ≤ 6.

**Note:** If any planned recovery fails to land by Day 10, the corresponding metric will undershoot the threshold and the checkpoint **FAILS**. The thresholds are intentionally set at the cumulative planned gain so a silent failure cannot pass.

---

## 11. Day 11 — Priority 7 #1388 camshape discriminator + #1387 close + Priority 6 #1224 start (~10h)

**Focus:** Day 0/1 NLP-warm-start runtime test for #1388 camshape (per `PRIORITY_7_FIX_SURFACE.md` §4.6 3-way discriminator); close #1387; start #1224 mine.

| Task | Effort | Notes |
|---|---|---|
| **#1388 camshape NLP-warm-start runtime test** per §4.6 — regenerate `camshape_mcp_presolve.gms` via `--nlp-presolve`; run with 10-symbol display pre-check; classify Case (a) / (b) / (c) per §4.6 discriminator | 2h | KU 7.2 🔍 INCOMPLETE → ✅ VERIFIED; binding 3-way classification |
| **#1388 fix or carryforward** based on discriminator: Case (a) ~4.5h emit-bug fix; Case (b) ~5.5h emit-bug + warm-start guidance; Case (c) ~1.25h Sprint 28 carryforward filing | 4.5h (Case a high) | Mitigation per §5.1 if overrun: trim 0.5h optional cleanup OR draw from Day 13 buffer |
| **#1387 close** — PR open + first review iteration | 2h | |
| **Priority 6 #1224 mine** start — implement per Day 0 KU 6.1 bundle decision; if bundled with #1385 this is brought forward from Day 12 | 1.5h | KU 6.1 binding decision applied |

**P7 success criteria:**
- [ ] #1387 cclinpts unblocked from `compare=mismatch (rel_diff=1.0)` to `compare_match` (+1 Match).
- [ ] #1388 camshape classified per §4.6: Case (a)/(b) → fix → +1 Solve; Case (c) → Sprint 28 carryforward filing.
- [ ] KUs 7.1, 7.2, 7.3 ✅ VERIFIED.

---

## 12. Day 12 — Priority 6 close + Priority 8 #1400 + Priority 9 #1374 (~10h)

| Task | Effort | Notes |
|---|---|---|
| **#1224 mine close** — finish implementation + Phase 0 + PR | 4h | KU 6.1 + KU 6.2 ✅ VERIFIED; mine next failure mode recorded |
| **Priority 8 #1400 pipeline absolute-path leak fix** at `scripts/gamslib/run_full_test.py:899` (`mcp_file_used` field) per `PROJECT_PLAN.md` Priority 8 | 2h | KU 8.1 ✅ VERIFIED at corrected scope (mcp_file_used only); KU 8.2 implementation choice (basename vs PROJECT_ROOT-relative) made here |
| **Priority 9 #1374 emit duplicate-init audit** — corpus sweep + targeted fix in `src/emit/` for most common shapes | 3h | KU 9.4 🔍 INCOMPLETE → ✅ VERIFIED; remaining shapes deferred to Sprint 28 per `PROJECT_PLAN.md` Priority 9 |
| Buffer | 1h | |

**P6/P8/P9 success criteria:**
- [ ] mine translates from `translate_internal_error` to `translate_success` (+1 Translate; Solve gain conditional per KU 6.2).
- [ ] Pipeline produces byte-identical `gamslib_status.json` across machines (modulo wall-time fields).
- [ ] #1374 corpus sweep recorded; targeted fix landed for common shapes.

---

## 13. Day 13 — Final Pipeline Retest + SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md (~8h)

**Focus:** Final checkpoint; close Sprint 27; author retrospective; record carryforwards for Sprint 28.

| Task | Effort | Notes |
|---|---|---|
| **Run PR22 audit script** (`--since-commit <Day-0 SHA>`) → final retest comparison surface | 0.5h | |
| **Final pipeline retest** under 3 `PYTHONHASHSEED` values (PR12 determinism guard) | 3h | Determinism acceptance criterion verification |
| Author Sprint 27 SPRINT_LOG.md final-day entry: headline metrics, bucket-provenance Sprint 26 final → Sprint 27 final, per-priority deliverables | 2h | |
| Author Sprint 27 SPRINT_RETROSPECTIVE.md (mirror Sprint 26 retrospective structure: What Went Well / What We'd Do Differently / Sprint 28 Recommendations / KU Coverage Summary) | 2h | |
| Buffer / Sprint 28 carryforward filings (issues that REPLANned or didn't fit budget) | 0.5h | |

**Day 13 success criteria:**
- [ ] All Sprint 27 acceptance criteria met OR explicitly carried forward to Sprint 28 with formal Phase 0 filing.
- [ ] Final metrics: Solve ≥ 111, Match ≥ 66, path_syntax_error ≤ 6, model_infeasible ≤ 3, Translate ≥ 135/142, Parse ≥ 142/142, Tests ≥ 4,750.
- [ ] Determinism: byte-identical `gamslib_status.json` under ≥ 3 `PYTHONHASHSEED` values (modulo wall-time).
- [ ] All 28 Sprint 27 KUs ✅ VERIFIED.
- [ ] SPRINT_LOG.md + SPRINT_RETROSPECTIVE.md authored.

---

## 14. Budget Summary

| Day | Hours | Cumulative | Workstreams |
|---|---|---|---|
| Day 0 | 8 | 8 | PR19 widening + AD Phase 0 ×3 + P1 anchor hand-derivation start |
| Day 1 | 10 | 18 | P1 anchors complete + first prototype |
| Day 2 | 10 | 28 | P1 full regression + PR open |
| Day 3 | 8 | 36 | P1 PR review/merge + P2 Phase 0 start |
| Day 4 | 12 | 48 | P2 implementation + PR |
| Day 5 | 10 | 58 | Checkpoint 1 + P5 start + P3 first sub-priority start |
| Day 6 | 12 | 70 | P3 #1390 + parallel P5 #1357 |
| Day 7 | 12 | 82 | P3 #1385 + P5 close |
| Day 8 | 12 | 94 | P3 #1393+#1335 + P7 #1387 start |
| Day 9 | 10 | 104 | P3 close + P4 launch numerics start |
| Day 10 | 10 | 114 | Checkpoint 2 + P4 close + P7 #1387 implement |
| Day 11 | 10 | 124 | P7 #1388 discriminator + #1387 close + P6 start |
| Day 12 | 10 | 134 | P6 close + P8 + P9 |
| Day 13 | 8 | 142 | Final retest + SPRINT_LOG + RETROSPECTIVE |
| **Total** | **142** | | **Within 168h cap; 26h slack** |

**Heaviest day:** 12h (Days 4, 6, 7, 8). All ≤ 12h ceiling. **Slack:** 168 − 142 = 26h (~15%) absorbs (a) Day 5 hypothesis-validation pivot work for any Priority 3 sub-priority that REPLANs on Day 0, (b) #1335's 3-approaches-to-evaluate uncertainty if Approach C fails Phase 0, (c) PR review iteration overhead for emit-affecting PRs, (d) #1388 Case (a) / Case (b) effort overrun (up to 1h over the 4.5h estimate per `PRIORITY_7_FIX_SURFACE.md` §5.1).

**Parallelization opportunities used:**
- Day 5: P5 #1356 fawley start runs in parallel with P3 first sub-priority (no patch-site overlap).
- Day 6: P3 #1390 + P5 #1357 (no patch-site overlap — `constraint_jacobian.py` vs `complementarity.py`).
- Day 7–8: P3 sub-priorities serial-by-PR but parallel with P7 #1387 prep + P5 close-out.
- Day 10–11: P4 launch close + P7 #1387 implement + P7 #1388 discriminator (no patch-site overlap).
- Day 12: P6 + P8 + P9 (3 independent priorities; no patch-site overlap).

---

## 15. Phase 0 Coverage Audit (per PR20 hard rule)

Every `src/`-touching priority has either (a) a **Phase 0 acceptance gate authored at prep stage** (prep-authored gate; KKT shape hand-derived and recorded in a prep-task doc before Sprint 27 Day 0), or (b) a **scheduled pre-commit inspection / corpus-sweep step** (P6 and P9 — the Phase 0 evidence is a Day 0 inspection or Day 12 corpus sweep rather than a prep-stage hand-derivation, because the scope is "inspect-then-decide" rather than "verify-against-known-target"):

| Priority | Issue(s) | Phase 0 evidence | Type | Status |
|---|---|---|---|---|
| Priority 1 | #1398 | `PRIORITY_1_ANCHOR_MAPPING.md` §4.1–4.7 (8 anchors) | Prep-authored gate | ✅ ready Day 0 |
| Priority 2 | #1381 | `PROJECT_PLAN.md` §"Priority 2" (camcge `nu_ieq`) | Prep-authored gate | ✅ ready Day 3 |
| Priority 3 | #1390/#1385/#1393+#1335 | `PRIORITY_3_RISK_ASSESSMENT.md` §3 (3 experiments) | Prep-authored gate (per-experiment design ready; binding PROCEED/REPLAN signal at Day 0) | ✅ ready Day 0 |
| Priority 4 | #1378 | `PROJECT_PLAN.md` §"Priority 4" + `PRIORITY_1_ANCHOR_MAPPING.md` §3 (launch byte-stability anchor) | Prep-authored gate (launch byte-stability anchor only; KU 4.1 fix-shape selection is the Day 9 implementation step) | ✅ ready Day 9 |
| Priority 5 | #1356/#1357 | `PRIORITY_5_FIX_SURFACE.md` §3 (patch sites + helpers) | Prep-authored gate | ✅ ready Day 5 |
| Priority 6 | #1224 | KU 6.1 inspection on Day 0 + `PROJECT_PLAN.md` §"Priority 6" | **Scheduled pre-commit inspection** (KU 6.1 = "does `src/ad/index_mapping.py` overlap with #1385's patch site?" — answerable only by reading the file, not pre-derivable) | ✅ scheduled Day 0 |
| Priority 7 | #1387/#1388 | `PRIORITY_7_FIX_SURFACE.md` §3 (#1387 sign-flip+term-omission) + §4 (#1388 3-way discriminator) | Prep-authored gate | ✅ ready Day 8/11 |
| Priority 8 | #1400 | Day 0 inspection + `PROJECT_PLAN.md` §"Priority 8" (corrected scope) | **Scheduled pre-commit inspection** (KU 8.1/8.2 = "is `run_full_test.py:899` the only leak field?" — answerable only by running the audit grep on the JSON, not pre-derivable) | ✅ scheduled Day 12 |
| Priority 9 | #1374 | KU 9.4 corpus sweep on Day 12 | **Scheduled pre-commit corpus sweep** (KU 9.4 = "how widespread is the duplicate-init pattern?" — answerable only by scanning the 134 translating models, not pre-derivable) | ✅ scheduled Day 12 |

**Coverage verdict:** all 9 priorities have an explicit Phase 0 evidence source. **6 priorities are covered by prep-authored gates** (P1, P2, P3, P4, P5, P7); **3 priorities are covered by scheduled inspection/sweep steps** (P6, P8, P9) where the answer fundamentally cannot be pre-derived at prep stage but is a deterministic mechanical check on Day 0 (P6, P8) or Day 12 (P9). The pre-commit inspection/sweep steps still satisfy PR20's intent — they produce a verified Phase 0 artifact (the inspection result or sweep output) BEFORE any src/ commit in that priority.

---

## 16. Known Unknowns Status Snapshot (Day 0 entry state)

Per `KNOWN_UNKNOWNS.md` at prep complete (audited 2026-05-31 by grepping every `Status:` line in the file and binning by emoji):

| Status | Count | KUs |
|---|---|---|
| ✅ VERIFIED at prep | 14 | 1.1, 1.2, 1.4, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 9.1, 9.3 |
| 🟡 PARTIALLY VERIFIED (design-ready; binding signal pending Day 0/1 experiment) | 3 | 3.1, 3.2, 4.2 |
| 🔍 INCOMPLETE (implementation-time) | 11 | 1.3, 2.1, 2.2, 2.3, 4.1, 6.1, 6.2, 8.1, 8.2, 9.2, 9.4 |
| **Total** | **28** | |

The 3 PARTIALLY VERIFIED KUs (3.1, 3.2, 4.2) have design-ready patch shapes per Tasks 6 and 4, with the binding PROCEED/REPLAN signal scheduled for the Day 0 AD-experiment block. KUs 3.1 and 3.2 move to ✅ VERIFIED when the Day 0 #1390 kand and #1385 srpchase prototypes produce binary PROCEED/REPLAN signals; KU 4.2 (launch byte-stability constraint on Priority 4 #1378) moves to ✅ VERIFIED when KU 4.1's Day 9 launch-numerics fix shape is selected.

The 11 INCOMPLETE KUs are **all implementation-time-dependent** (their answer is the output of running a prototype patch or experiment, not a prep-stage research question). They are scheduled for VERIFICATION on the day the relevant src/ work lands:
- KU 1.3 → Day 1–2
- KU 2.1, 2.2, 2.3 → Day 4
- KU 4.1 → Day 9
- KU 6.1 → Day 0 inspection
- KU 6.2 → Day 12
- KU 8.1, 8.2 → Day 12
- KU 9.4 → Day 12
- KU 9.2 → deferred to Sprint 28+ retrospective (reusability assessment)

**No INCOMPLETE KU blocks Sprint 27 start.** All blocking research (PROCEED/REPLAN signals, scope freezes, anchor mappings, patch-site identification, effort estimates) was resolved in prep tasks 1–10. The 3 PARTIALLY VERIFIED KUs are explicitly design-ready with Day 0 experiment slots — that's the intended state for the AD architectural redesign chain.

---

## 17. Risk Register + Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Day 0 AD experiment REPLANs all 3 P3 sub-priorities | Low (per Task 6 design-ready experiments) | High (P3 = 30–48h of sprint budget) | 26h slack absorbs at most 1 REPLAN; if all 3 REPLAN → trim to 4 sub-priorities + extend Sprint 28 |
| #1388 camshape Case (c) (Sprint 28 carryforward) | Medium (per Task 8 verdict — `PRIORITY_7_FIX_SURFACE.md` §4.6 binding 3-way discriminator) | **Medium:** #1388 is listed as a +1 firm Solve gain in §2 / `PROJECT_PLAN.md` Sprint 27 acceptance criteria; if Case (c) materializes, the firm count drops +6 → +5 and the planned Solve delta drops +8 → +7 → **Solve = 110, one below the ≥ 111 target** even with BOTH conditional gains (#1385 unblocking iswnm/mexls/nebrazil/sarf AND #1224 mine clean-solve) landing. Closing the +1 gap requires either an additional Sprint 27 recovery (e.g., #1374 fix surfacing a previously-blocked solve, or an opportunistic P6/P7/P8/P9 Day 10–12 gain) or a target revision recorded in the Day 13 retrospective. Filing itself is low-cost (~1.25h) | Carryforward template in `PRIORITY_7_FIX_SURFACE.md` §6; Day 13 buffer absorbs filing time; the §2 caveat documents the firm-count-impact path explicitly + identifies the +1 closure options (additional recovery vs target revision) so the Day 13 retrospective can attribute any Solve ≥ 111 miss to the §17 risk that materialized and record the chosen closure path |
| #1335 Approach C fails Phase 0 (need to fall back to Approach A or B) | Low-Medium (per Task 6) | Medium (~3h pivot per `PRIORITY_3_RISK_ASSESSMENT.md`) | Day 13 buffer + 26h sprint slack |
| Day 4 P2 byte-stability surface breaks Tier 0/1 canary (KU 2.3) | Low | Medium (~2h debug + repair) | clearlak byte-stability canary check codified at Day 4 + Day 7 P5 close |
| P1 PR review iteration exceeds Day 3 budget (CONTRIBUTING.md PR14 + PR20 disclosure conventions not yet battle-tested on the kind of multi-anchor regression PR Priority 1 produces) | Medium | Low (overflow into Day 4 slack) | PR description pre-fills the PR14 regenerated-`.gms` list AND the PR20 anchor-by-anchor Phase 0 cross-reference (per `PRIORITY_1_ANCHOR_MAPPING.md` §4) BEFORE requesting review, so the reviewer can verify each regenerated artifact against the corresponding hand-derived KKT directly |
| Day 11 P6 #1224 bundle decision (KU 6.1) shows bundle is wrong → mine becomes Day 12 work | Low | Low (1h shift) | Day 0 inspection completed before P3 #1385 starts (no rework downstream) |
| Pipeline retest variance (3 models on translate_timeout boundary; same machine-load risk as Day 0) | Medium | Low (cosmetic only — bucket-provenance documents the variance per PR17) | Re-run if Day 13 final retest shows > 3 translate_timeout models that weren't in scope; document machine-load variance per `BASELINE_METRICS.md` §6.1 |

---

## 18. Related Documents

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" (canonical priorities + Acceptance Criteria + Estimated Effort)
- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` (11-task prep plan; this PLAN.md is Task 11's deliverable)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` (28 KUs; per-day VERIFICATION schedule above)
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` (Day 0 baseline + scope freeze)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` (Day 0/1 anchor model handoff)
- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` (Day 0 widening apply)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` (Day 0 AD experiments)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` (Day 5 P5 handoff)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` (Day 8/11 P7 handoff)
- `docs/planning/EPIC_4/SPRINT_27/PR22_SCRIPT_DESIGN.md` (Day 5/10/13 retest invocation)
- `docs/planning/EPIC_4/SPRINT_27/PR23_CHECKLIST_DESIGN.md` (per-PR self-review checklist)
- `docs/planning/EPIC_4/SPRINT_27/prompts/PLAN_PROMPTS.md` (per-day execution prompts)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` (per-day log skeleton; filled in during execution)
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates", §"Emit-Affecting PRs", §"CI Workflow PR Checklist", §"Emit-PR `.gms` Diff Workflow"
