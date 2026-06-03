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
| **Solve** | 103 | ≥ 111 (**AT RISK** post-Day-0) | +6 firm (#1381 ×2, #1398 qdemo7, #1357, #1356, #1388 per `PROJECT_PLAN.md` Sprint 27 §"Acceptance Criteria") + ~~2 conditional (#1385, #1224)~~ → **1 conditional (#1224 only)** after the Option 1 re-plan. **Caveat per Task 8 / `PRIORITY_7_FIX_SURFACE.md`:** #1388 is conditional on the Day 11 §4.6 3-way discriminator — Case (a)/(b) → +1 firm Solve as documented; Case (c) → Sprint 28 carryforward → +5 firm + conditional. **REVISED post-Day-0 binding signals (Option 1 re-plan):** #1385's conditional Solve (iswnm/mexls/nebrazil/sarf) is **deferred to Sprint 28** — Sprint 27 lands #1385 as translate-time-only (cross-term emit deferred), so it yields a Translate gain, not a Solve gain. #1393+#1335 is **deferred to Sprint 28** (Approach C disproven; Approach B needed). **Interaction risk to verify at Day 5/Checkpoint 1:** if otpop requires BOTH #1357 (P5 comp_up) AND #1393+#1335 (P3 scalar-eq) to reach compare_match, deferring #1393+#1335 may also defer the **#1357 firm Solve gain** (otpop) — re-classify at Checkpoint 1. With these revisions Solve ≥ 111 is at risk; the closure path (additional recovery or target revision) is recorded in the Day 13 retrospective per §17. |
| **Match** | 59 | ≥ 66 (**AT RISK** post-Day-0) | **REVISED post-Day-0 binding signals (Option 1 re-plan):** +6 firm (#1381 ×2, #1398 qdemo7, #1357, #1356, #1378) + **#1390 +1 now CONDITIONAL** on the Day 5 re-scoped Phase 0 (the #1390 fix moved from the disproven AD site to the `stationarity.py` offset re-symbolization layer — see §8 + `PRIORITY_3_RISK_ASSESSMENT.md` §8.5). If the re-scoped Phase 0 PROCEEDs and #1390 lands → Match = 66; if it REPLANs → Match = 65 (target miss recorded in the Day 13 retrospective per §17). |
| **path_syntax_error** | 14 (was 17 at Sprint 26 final; 3 machine-variance churn into translate_timeout) | ≤ 6 | −8 to ≤ 6 |
| **path_solve_terminated** | 5 | ≤ 5 (maintain) | 0 |
| **model_infeasible** | 4 | ≤ 3 | −1 (#1388 camshape) |
| **Translate** | 131 (134 at Sprint 26 final; 3 timeout churn) | ≥ 135/142 | +4 firm + variance recovery |
| **Parse** | 142/142 | ≥ 142/142 | maintain 100% |
| **Tests** | 4,737 | ≥ 4,750 | +13 |
| **Determinism** | n/a | Byte-identical under ≥ 3 `PYTHONHASHSEED` values | new (PR12 guard) |
| **Process recs** | n/a | PR20 codified + 4 Phase 0 backlog sections authored; PR21 codified; PR22 script landed; PR23 checklist landed | done in prep (Tasks 2–10) |
| **PR19 widening** | 11 models | 30 models (11 Tier 0/1 + 19 Pattern C; `launch` corrected to pattern-c Day 0 — MODEL STATUS 5, the #1378 target) | done Day 0 per Task 5 |

Per `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §2 — Sprint 27 Day 0 baseline frozen 2026-05-28 at Solve=103, Match=59, path_syntax_error=14, model_infeasible=4, Translate=131/142, Tests=4,737. The Day 0 numbers reflect machine-load variance pushing 3 models into translate_timeout — these are NOT Sprint 27 regressions.

> 🔁 **OPTION 1 RE-PLAN (Day 0 binding-signal response — adopted 2026-06-01).** The Day 0 Phase 0 experiments returned #1390 REPLAN, #1393+#1335 REPLAN, #1385 SCOPED-PROCEED — all three prep patch sites were mis-scoped to the AD layer; the real surface is the KKT stationarity/emit layer (`PRIORITY_3_RISK_ASSESSMENT.md` §8.5). **Priority 3 is re-planned as follows:** **(a)** re-scope **#1390** to the `stationarity.py` offset re-symbolization layer and re-run Phase 0 on Day 5; implement Days 6–7 if it PROCEEDs (preserves the +1 Match). **(b)** Land **#1385** as a translate-time-only short-circuit (Day 7); defer its cross-term emit (and the conditional Solve) to Sprint 28. **(c)** Defer **#1393+#1335** to Sprint 28 with a carryforward filing (Day 8). **(d)** Redirect the freed budget to pull **P7 #1387** forward (implement Day 8, close Day 9), giving Days 10–11 added slack. §§7–10, §14, §17 below reflect this re-plan.

---

## 3. Sequencing Constraints (from PREP_PLAN.md §Task 11 + prep-task outputs)

1. **Day 0 ONLY:** PR19 widening (Task 5; 10-min edit to `.github/path-solve-ci-targets.txt`) + Phase 0 codification application (Task 2; CONTRIBUTING.md §"Phase 0 Acceptance Gates" already merged) + AD architectural Phase 0 validation experiments (Task 6 PROCEED/REPLAN signal for #1390/#1385/#1393; ~3h on Day 0).
2. **Day 0 precedes Day 1 Priority 1 work** — the PR19 widening must be in place BEFORE the tightened gate predicate from #1398 lands, so similar gate-overreach catches at PR-review time.
3. **Priority 3 commits are PHASE-0-GATED — Day 0 RESULT (binding): 2 REPLAN + 1 SCOPED-PROCEED, all due to AD-layer patch-site misattribution.** Under the Option 1 re-plan: **#1390** gets a Day 5 *re-scoped* Phase 0 on the `stationarity.py` offset re-symbolization layer (implement Days 6–7 only if it PROCEEDs); **#1385** lands translate-time-only on Day 7 (cross-terms → Sprint 28); **#1393+#1335** is deferred to Sprint 28 (Day 8 carryforward filing). (Day 4 is Priority 2 / #1381 Pattern C Phase B redesign, not Priority 3.) Freed P3 budget is redirected to pull P7 #1387 forward (§8 Day 8 + §9 Day 9); any residual rolls to Day 13 buffer. See `PRIORITY_3_RISK_ASSESSMENT.md` §8.5.
4. **Priority 6 #1224 — Day 0 RESOLVED: STANDALONE** (KU 6.1). The premise that #1224 and #1385 both touch `src/ad/index_mapping.py` is false — `index_mapping.py` has no `IndexOffset`/`ParamRef` code; #1224's surface is `constraint_jacobian.py`/`derivative_rules.py`. No bundle; #1224 stays standalone Day 11–12.
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
| 0.3 | **PR19 widening** — edit `.github/path-solve-ci-targets.txt` per `PR19_WIDENING_DESIGN.md` §6 (add launch + 14 net-new #1398-affected models as Pattern C soft-fail — **launch corrected Day 0 from tier=1 to pattern-c: it is MODEL STATUS 5 Locally Infeasible (the #1378 target), so it cannot be a hard-fail canary**). Open PR. PR23 self-review NOT required — the targets file is outside PR23 scope per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope". | 1h | PR open |
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

> ✅ **Carryforward done (2026-06-03):** the regeneration, bucket-provenance, Tier 0/1 byte-stability, and the `PRIORITY_1_ANCHOR_MAPPING.md` §4.2/§4.4 grep-spec correction are **already complete** on branch `planning/sprint27-day1-p1` (commit `4de59037`); see SPRINT_LOG Day 2. **Only the PR-open + review iteration remain.** Provenance result: **qdemo7 → compare_match** (the +1 Solve/Match anchor); egypt/ferts/shale/srpchase → path_solve_license; ganges → path_syntax_error (from translate_timeout); **dinam/gangesx/turkpow stay at path_syntax_error from PRE-EXISTING non-#1398 errors** (turkpow byte-identical to baseline; dinam has fewer errors) → Sprint 28 candidates. **No regressions.**

| Task | Effort | Notes |
|---|---|---|
| Regenerate `*_mcp.gms` for all 15 #1398-affected models + launch | 2h | ✅ DONE (carryforward) — 9 artifacts changed (dinam, egypt, fawley, ferts, ganges, gangesx, qdemo7, shale, srpchase); 6 affected + launch + 11 canaries byte-identical |
| Run pipeline tests + bucket-provenance check for affected models | 2h | ✅ DONE — qdemo7 → `compare_match`; egypt/ferts/shale/srpchase → `path_solve_license`; ganges → `path_syntax_error` (from timeout); dinam/gangesx/turkpow → `path_syntax_error` (residual pre-existing, non-#1398); sambal/qsambal/harker → compare_mismatch; tfordy/sroute → path_solve_license |
| Tier 0/1 byte-stability verification (regenerate all 11 Tier 0/1 canaries + `launch` byte-stability anchor, diff vs main) | 1h | ✅ DONE (carryforward) — all 11 canaries + launch byte-identical. `launch` is PR19 pattern-c but still byte-checked here as the #1379 anchor |
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
- [x] 15 #1398-affected models recover to Day 0 baseline buckets (✅ no regressions): qdemo7 → compare_match; egypt/ferts/shale/srpchase → path_solve_license; ganges → path_syntax_error (from timeout). **Caveat:** dinam/gangesx/turkpow remain at path_syntax_error — their Pattern C emit is now correct, but they carry **pre-existing non-#1398 errors** ($140/$170/$171 in other equations; turkpow byte-identical to baseline, dinam −2 errors). These are NOT #1398 recoveries → **file as Sprint 28 candidates**.
- [x] launch byte-stable vs Sprint 26 final emit (per KU 4.2). ✅
- [x] PR19 target list widened to 30 models per Task 5. ✅ (Day 0, PR #1413 merged)
- [x] All 4 Phase 0 KUs 1.1–1.4 ✅ VERIFIED (1.3 moved from INCOMPLETE on Day 1).
- [x] **P1 #1398 PR opened + merged** — PR #1414 (PR14: 9 regenerated `_mcp.gms` in diff; PR20: cross-ref `DAY0_ANCHOR_SCRATCH_NOTES.md` + `PRIORITY_1_ANCHOR_MAPPING.md` §4; PR23 N/A). **Merged to main 2026-06-03 (`853000ef`).** Priority 1 COMPLETE.

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
| **Priority 3 #1390 re-scoped Phase 0** (Option 1 re-plan; Day 0 #1390 REPLAN'd the AD site): hand-derive the predicate-guarded-Sum collapse at the `stationarity.py` offset re-symbolization layer (`_collect_lead_lag_offsets:95` → `_apply_offset_substitution:2433` / `_apply_alias_offset_to_deriv:2264`, which fired 22× = the 22 kand phantom terms per `PRIORITY_3_RISK_ASSESSMENT.md` §3.5). Produce a binding **re-PROCEED/REPLAN** signal. | 1.5h | If re-PROCEED → implement Days 6–7; if re-REPLAN → defer #1390 to Sprint 28 + redirect Day 6–7 to P7/P4 (Match → 65, record §17) |

**Checkpoint 1 success criteria** (P1 merged Day 3 + P2 merged Day 4 → both gains expected at Day 5 retest):
- [ ] Pipeline retest shows **Solve ≥ 106** (Day 0 103 + **#1398 qdemo7 +1** from P1 Day 3 merge + #1381 camcge/cesam2 +2 from P2 Day 4 merge = 106).
- [ ] Pipeline retest shows **Match ≥ 62** (Day 0 59 + **#1398 qdemo7 +1** + #1381 ×2 = 62).
- [ ] PR22 script output includes camcge_mcp.gms + cesam2_mcp.gms + 15 #1398-affected `*_mcp.gms` artifacts + launch byte-stable diff.
- [ ] P5 #1356 Phase 0 hand-derivation complete; first prototype committed.
- [ ] **#1390 re-scoped Phase 0 binding signal recorded** (re-PROCEED → Days 6–7 implement; re-REPLAN → defer + redirect). Verify the otpop #1357↔#1393+#1335 interaction (does deferring #1393+#1335 jeopardize the #1357 Solve gain?) and re-classify if needed.

**Note:** Checkpoint 1 must catch a failed P1 #1398 recovery. If Solve = 105 / Match = 61 (i.e., only camcge+cesam2 recovered) the checkpoint **FAILS** even though +2 landed — that pattern indicates qdemo7 (and possibly other #1398-affected models) did not return to their Day 0 baseline buckets, requiring a Day 5/6 P1 re-investigation before Priority 3 begins.

---

## 8. Days 6–8 — Priority 3 (RE-PLANNED per Option 1): #1390 re-scoped + #1385 translate-only + #1393/#1335 deferred + P7 #1387 pulled forward + parallel Priority 5 (~36h total)

> 🔁 **THIS SECTION IS THE OPTION 1 RE-PLAN** (Day 0 binding signals: #1390 REPLAN, #1393+#1335 REPLAN, #1385 SCOPED-PROCEED — all three prep patch sites were mis-scoped to the AD layer; the real surface is `src/kkt/stationarity.py`, per `PRIORITY_3_RISK_ASSESSMENT.md` §8.5). The original "implement 3 AD redesigns at `constraint_jacobian.py`/`index_mapping.py`/`derivative_rules.py`" schedule is **superseded** — those sites are disproven. **Do NOT implement at the AD sites.**

**Day-budget allocation:** Day 6 = 12h, Day 7 = 12h, Day 8 = 12h.

**Re-planned sequencing:** **#1390** (re-scoped to `stationarity.py` offset re-symbolization; Day 5 re-Phase-0 → implement Days 6–7 IF re-PROCEED) → **#1385** (translate-time-only short-circuit, Day 7; cross-terms deferred to Sprint 28) → **#1393+#1335** (Sprint 28 carryforward filing, Day 8 — Approach C disproven). Freed budget pulls **P7 #1387** forward (implement Day 8, was Day 10). All `src/kkt/stationarity.py` PRs require a fresh Phase 0 acceptance gate (PR20) on the redirected layer before commit.

### Day 6 (~12h) — #1390 implement (re-scoped to `stationarity.py`) + P5 #1357 otpop start

**Gated on the Day 5 #1390 re-scoped Phase 0.** If it re-REPLAN'd, skip the #1390 rows, defer #1390 to Sprint 28 (Match → 65, record §17), and pull P7 #1387 / P4 forward into this slot instead.

| Task | Effort | Notes |
|---|---|---|
| #1390 implement predicate-guarded-Sum collapse at the `stationarity.py` offset re-symbolization layer (`_apply_offset_substitution:2433` / `_apply_alias_offset_to_deriv:2264` / `_collect_lead_lag_offsets:95`) — **NOT** `constraint_jacobian.py:903/1027` (Day 0-disproven) | 6h | Per Day 5 re-scoped Phase 0; collapse the 22 per-offset `lam_dembalx(j,t+1,n±k)` terms into 1 predicate-guarded Sum |
| #1390 Phase 0 verify (22 phantom-offset → 1; hand-derived KKT match on kand `stat_y(j,t,n)`) | 1.5h | KU 3.1 re-verified on the redirected layer |
| #1390 Tier 0/1 byte-stability check | 1h | |
| **Priority 5 #1357 otpop** — Phase 0 + first patch (parallel; same patch sites as #1356) | 3h | KU 5.2 ✅ VERIFIED at prep (only 2 models in scope per fawley + otpop) |
| Buffer | 0.5h | |

### Day 7 (~12h) — #1390 PR + #1385 translate-time-only short-circuit + P5 close

| Task | Effort | Notes |
|---|---|---|
| #1390 PR open (PR14 + PR20 Phase 0 cross-reference to the redirected `stationarity.py` shape; PR23 not applicable — pure `src/kkt/stationarity.py` change) + first review iteration | 3h | |
| #1385 implement **translate-time-only** short-circuit: generalize the single-`SetMembershipTest` detection to skip enumeration at `index_mapping.py:377` (Day 0-validated: srpchase **>180s → 6.0s**) + runtime-guard equation-body emit at `stationarity.py`. **Cross-term emit (J_gᵀ·lam) is explicitly DEFERRED to Sprint 28** per the §7 scoped-PROCEED rule. | 5h | Yields a **Translate** gain (srpchase + any same-shape models out of translate_timeout), NOT a Solve gain. Phase 0 re-check: clean GAMS compile + no quoted-literal indices |
| #1385 Phase 0 verify (translate <10s; clean compile; documents the deferred-cross-term scope) + open issue for the Sprint 28 cross-term follow-on | 1.5h | KU 3.2 ✅ VERIFIED as scoped |
| **Priority 5 close** — PR open for combined fawley + otpop fix; Tier 0/1 clearlak byte-stability (KU 5.3 mitigation) | 1.5h | |

### Day 8 (~12h) — #1385 PR + #1393+#1335 Sprint 28 carryforward + P7 #1387 implement (pulled forward)

| Task | Effort | Notes |
|---|---|---|
| #1385 PR open (PR14 + PR20; PR23 not applicable — `src/ad/index_mapping.py` + `src/kkt/stationarity.py`) + review iteration | 3h | PR description states the scoped/translate-only boundary explicitly |
| **#1393+#1335 Sprint 28 carryforward filing** (replaces the disproven Approach-C implementation): file the issue with the Day 0 evidence (Approach C inert; redirected to `stationarity.py` symbolic-collapse / the `card(t)-ord(t)` offset evaluator for #1335) per `PRIORITY_3_RISK_ASSESSMENT.md` §5.5 fallback | 1.5h | #1393 and #1335 are now **distinct** fixes; both → Sprint 28 |
| **Priority 7 #1387 cclinpts implement (pulled forward from Day 10):** Phase 0 hand-derivation (sign-flip + term-omission per `PRIORITY_7_FIX_SURFACE.md` §3) **AND** implement at `derivative_rules.py:1847` + `stationarity.py:1352/1835` | 6.5h | KU 7.1 ✅ VERIFIED at prep; uses freed P3 budget |
| Buffer | 1h | |

**P3 success criteria (re-planned):**
- [ ] #1390 (if Day 5 re-PROCEED): kand cross-term reduces 22 → 1 on the `stationarity.py` layer; closed. (If re-REPLAN: deferred to Sprint 28, Match → 65 recorded.)
- [ ] #1385 srpchase translates <10s (translate-time-only); clean compile; **cross-terms + conditional Solve deferred to Sprint 28** (issue filed).
- [ ] #1393+#1335 Sprint 28 carryforward filed (NOT implemented in Sprint 27).
- [ ] KUs 3.1–3.5 reflect the Day 0 binding signals + re-plan (already updated Day 0).

**P5 success criteria:**
- [ ] fawley + otpop unblock from `path_syntax_error` to `compare_match` (+2 Solve, +2 Match).
- [ ] #1356, #1357 closed.
- [ ] KUs 5.1–5.3 ✅ VERIFIED.

---

## 9. Day 9 — Priority 3 close + P7 #1387 close (pulled forward) + Priority 4 launch numerics start (~10h)

| Task | Effort | Notes |
|---|---|---|
| #1390 (if landed) + #1385 PR merges (any P3 PRs still open from Days 6–7) | 1.5h | #1393+#1335 has NO PR (Sprint 28 carryforward filed Day 8) |
| **P7 #1387 close** (pulled forward from Day 11 — implemented Day 8): PR open + first review iteration | 2h | Was Day 10–11; moved up using freed P3 budget |
| **Priority 4 #1378 launch numerics** — investigate per `PROJECT_PLAN.md` Priority 4 (initial-point tuning, `--nlp-presolve`, NLP-warm-start, sign/scaling refinement); pick approach per KU 4.1 | 4h | KU 4.1 🔍 INCOMPLETE → ✅ VERIFIED |
| Buffer / context-switch overhead | 2.5h | |

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
| **P7 #1387 merge** (implemented Day 8, PR opened Day 9 — merge here) | 1h | Moved up from Day 10–11 via freed P3 budget |
| Slack / pull-forward buffer (freed by the Option 1 re-plan; e.g., start P6 #1224 or P9 #1374 early) | 2.5h | Was #1387 implement (now Day 8) |

**Checkpoint 2 success criteria** (P1 merged Day 3 + **P2 merged Day 4** (matching the Checkpoint 1 assumption that P2's gains appear in the Day 5 retest) + P5 Days 7–8 + P3 #1390 Day 7 + P3 #1385+#1393+#1335 Day 9 + P4 #1378 Day 10 → most planned Match recoveries should already be at the Sprint final target):
- [ ] **Solve ≥ 108** (Day 0 103 + 5 firm: **#1398 qdemo7 +1**, #1381 camcge/cesam2 +2, #1357 otpop +1, #1356 fawley +1). Launch's #1378 is a Match gain (mismatch → match), not Solve. **Re-plan caveat:** #1385's conditional Solve is no longer expected here (translate-time-only → Sprint 28). **Verify the #1357 otpop Solve actually landed** — if otpop needs #1393+#1335 (deferred) to reach compare_match, the #1357 +1 may slip, giving Solve = 107 (re-classify per §2 Solve row).
- [ ] **Match ≥ 65 firm; 66 if the #1390 re-scope landed** (Day 0 59 + 6 firm: **#1398 qdemo7 +1**, #1381 ×2, #1357 +1, #1356 +1, **#1378 launch mismatch→match +1** = +6 → 65) **+ #1390 kand mismatch→match +1 (conditional on the Day 5 re-scoped Phase 0)** → 66. Checkpoint 2 must NOT pass at Match = 62 with the firm recoveries silently failing; a reading of 65 (with #1390 deferred) is an at-target-minus-one result to record per §17, not a checkpoint failure.
- [ ] **path_syntax_error ≤ 6** (final target reached at Checkpoint 2 since P1 + P2 + P5 — the path_syntax_error contributors — all merge by Day 9). Day 0 14 − #1398 reductions (qdemo7, dinam, egypt, ferts, gangesx, shale, turkpow recoveries) − #1381 (camcge, cesam2) − #1357 (otpop) − #1356 (fawley) → ≤ 6.

**Note:** If any planned recovery fails to land by Day 10, the corresponding metric will undershoot the threshold and the checkpoint **FAILS**. The thresholds are intentionally set at the cumulative planned gain so a silent failure cannot pass.

---

## 11. Day 11 — Priority 7 #1388 camshape discriminator + Priority 6 #1224 start (~10h)

**Focus:** Day 0/1 NLP-warm-start runtime test for #1388 camshape (per `PRIORITY_7_FIX_SURFACE.md` §4.6 3-way discriminator); start #1224 mine. (**#1387 close moved to Day 9** under the Option 1 re-plan — implemented Day 8, closed Day 9/10 — freeing ~2h here.)

| Task | Effort | Notes |
|---|---|---|
| **#1388 camshape NLP-warm-start runtime test** per §4.6 — regenerate `camshape_mcp_presolve.gms` via `--nlp-presolve`; run with 10-symbol display pre-check; classify Case (a) / (b) / (c) per §4.6 discriminator | 2h | KU 7.2 🔍 INCOMPLETE → ✅ VERIFIED; binding 3-way classification |
| **#1388 fix or carryforward** based on discriminator: Case (a) ~4.5h emit-bug fix; Case (b) ~5.5h emit-bug + warm-start guidance; Case (c) ~1.25h Sprint 28 carryforward filing | 4.5h (Case a high) | Mitigation per §5.1 if overrun: trim 0.5h optional cleanup OR draw from Day 13 buffer |
| **Priority 6 #1224 mine** start — implement standalone per Day 0 KU 6.1 decision (**STANDALONE, not bundled with #1385** — no `index_mapping.py` overlap; surface is `constraint_jacobian.py`/`derivative_rules.py`) | 2h | KU 6.1 binding decision applied |
| Slack (freed by moving #1387 close to Day 9) | 1.5h | |

**P7 success criteria:**
- [ ] #1387 cclinpts unblocked from `compare=mismatch (rel_diff=1.0)` to `compare_match` (+1 Match) — **delivered Day 8–9 under the re-plan**.
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
| Buffer / Sprint 28 carryforward filings (issues that REPLANned or didn't fit budget) | 0.5h | Includes: #1385 cross-terms + #1393+#1335 (P3 re-plan); **dinam/gangesx/turkpow residual non-#1398 path_syntax_error** (Day 2 finding — `$140`/`$170`/`$171` in non-Pattern-C equations; #1398 emit is correct but these models carry independent errors) |

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
| Day 5 | 10 | 58 | Checkpoint 1 + P5 start + **#1390 re-scoped Phase 0** (stationarity layer) |
| Day 6 | 12 | 70 | **#1390 implement (stationarity layer, if re-PROCEED)** + parallel P5 #1357 |
| Day 7 | 12 | 82 | #1390 PR + **#1385 translate-time-only** + P5 close |
| Day 8 | 12 | 94 | #1385 PR + **#1393+#1335 → Sprint 28 filing** + **P7 #1387 implement (pulled fwd)** |
| Day 9 | 10 | 104 | P3 PR merges + **P7 #1387 close** + P4 launch numerics start |
| Day 10 | 10 | 114 | Checkpoint 2 + P4 close + **P7 #1387 merge** + slack |
| Day 11 | 10 | 124 | P7 #1388 discriminator + P6 #1224 start (standalone) + slack |
| Day 12 | 10 | 134 | P6 close + P8 + P9 |
| Day 13 | 8 | 142 | Final retest + SPRINT_LOG + RETROSPECTIVE |
| **Total** | **142** | | **Within 168h cap; 26h slack** |

**Heaviest day:** 12h (Days 4, 6, 7, 8). All ≤ 12h ceiling. **Slack:** 168 − 142 = 26h (~15%), now augmented by the Option 1 re-plan (which converts ~30–48h of disproven P3 implementation into ~12h: #1390 re-scoped + #1385 translate-only + #1393/#1335 filing, with P7 #1387 pulled forward into the gap). The slack absorbs (a) the Day 5 **#1390 re-scoped Phase 0** — if it re-REPLANs, Days 6–7 redirect to P4/P7 and Match → 65 (§17); (b) the #1390 stationarity-layer implementation being a larger/less-certain effort than the original AD-site estimate; (c) PR review iteration overhead for emit-affecting PRs; (d) #1388 Case (a)/(b) effort overrun (up to 1h over the 4.5h estimate per `PRIORITY_7_FIX_SURFACE.md` §5.1); (e) the Sprint 28 carryforward filings for #1385 cross-terms + #1393+#1335.

**Parallelization opportunities used:**
- Day 5: P5 #1356 fawley start runs in parallel with P3 first sub-priority (no patch-site overlap).
- Day 6: P3 #1390 (re-scoped) + P5 #1357 (no patch-site overlap — `stationarity.py` vs `complementarity.py`).
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
| ✅ **MATERIALIZED Day 0** — AD experiments returned 2 REPLAN (#1390, #1393+#1335) + 1 SCOPED-PROCEED (#1385); root cause = all 3 prep patch sites mis-scoped to the AD layer (real surface = `stationarity.py`) | Was Low; **occurred** | High (P3 = 30–48h budget) | **Resolved via the Option 1 re-plan** (§2 banner + §8): #1390 re-scoped to `stationarity.py` (Day 5 re-Phase-0) preserving the +1 Match if it re-PROCEEDs; #1385 translate-time-only (cross-terms → Sprint 28); #1393+#1335 → Sprint 28 filing; freed budget pulls P7 #1387 forward. Match ≥66 + Solve ≥111 now both AT RISK — closure/target-revision recorded in the Day 13 retrospective. See `PRIORITY_3_RISK_ASSESSMENT.md` §8.5. |
| #1388 camshape Case (c) (Sprint 28 carryforward) | Medium (per Task 8 verdict — `PRIORITY_7_FIX_SURFACE.md` §4.6 binding 3-way discriminator) | **Medium:** #1388 is listed as a +1 firm Solve gain in §2 / `PROJECT_PLAN.md` Sprint 27 acceptance criteria; if Case (c) materializes, the firm count drops +6 → +5 and the planned Solve delta drops +8 → +7 → **Solve = 110, one below the ≥ 111 target** even with BOTH conditional gains (#1385 unblocking iswnm/mexls/nebrazil/sarf AND #1224 mine clean-solve) landing. Closing the +1 gap requires either an additional Sprint 27 recovery (e.g., #1374 fix surfacing a previously-blocked solve, or an opportunistic P6/P7/P8/P9 Day 10–12 gain) or a target revision recorded in the Day 13 retrospective. Filing itself is low-cost (~1.25h) | Carryforward template in `PRIORITY_7_FIX_SURFACE.md` §6; Day 13 buffer absorbs filing time; the §2 caveat documents the firm-count-impact path explicitly + identifies the +1 closure options (additional recovery vs target revision) so the Day 13 retrospective can attribute any Solve ≥ 111 miss to the §17 risk that materialized and record the chosen closure path |
| ✅ **MATERIALIZED Day 0** — #1335/#1393 Approach C failed Phase 0 (inert; `_is_concrete_instance_of` never reached) | Was Low-Medium; **occurred** | Medium | **Resolved: deferred to Sprint 28** (Day 8 carryforward filing) rather than mid-sprint pivot to Approach A/B — #1393 and #1335 are now distinct fixes on the `stationarity.py` symbolic-collapse + `card(t)-ord(t)` offset-evaluator surfaces. |
| Day 4 P2 byte-stability surface breaks Tier 0/1 canary (KU 2.3) | Low | Medium (~2h debug + repair) | clearlak byte-stability canary check codified at Day 4 + Day 7 P5 close |
| P1 PR review iteration exceeds Day 3 budget (CONTRIBUTING.md PR14 + PR20 disclosure conventions not yet battle-tested on the kind of multi-anchor regression PR Priority 1 produces) | Medium | Low (overflow into Day 4 slack) | PR description pre-fills the PR14 regenerated-`.gms` list AND the PR20 anchor-by-anchor Phase 0 cross-reference (per `PRIORITY_1_ANCHOR_MAPPING.md` §4) BEFORE requesting review, so the reviewer can verify each regenerated artifact against the corresponding hand-derived KKT directly |
| ✅ **RESOLVED Day 0** — KU 6.1 #1224 bundle decision | n/a | Low | Day 0 inspection → **STANDALONE** (no `index_mapping.py` overlap with #1385; #1224 surface is `constraint_jacobian.py`/`derivative_rules.py`). #1224 stays Day 11–12 standalone. |
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
