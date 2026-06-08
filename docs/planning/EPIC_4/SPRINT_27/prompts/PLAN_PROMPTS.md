# Sprint 27 Per-Day Execution Prompts

**Status:** ✅ READY — Sprint 27 ready to kick off Day 0
**Date:** 2026-05-31
**Owner:** Sprint 27 engineer
**Codifies:** Sprint 27 Prep Task 11 (per-day execution prompts)
**Companion to:** `docs/planning/EPIC_4/SPRINT_27/PLAN.md` (canonical day-by-day schedule with hour budgets + success criteria)

---

## How to Use

Each section below is a self-contained prompt for one Sprint 27 day. Each prompt:

1. **References the canonical PLAN.md day section** — read `PLAN.md` §"Day N" alongside the prompt before starting.
2. **Lists prep-task deliverables to read** — the Phase 0 anchor specs, patch sites, and effort estimates live there.
3. **Names the PRs to open** — each `src/`-touching PR follows **PR14** (regenerated `.gms` in diff) + **PR20** (Phase 0 acceptance gate cross-reference). **PR23 self-review applies only when the diff additionally touches `.github/workflows/*.yml`/`.yaml`, `scripts/ci/*`, or `.github/actions/*`** (per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" scope clauses); a pure `src/` PR with no workflow/CI changes does NOT require PR23. The PR19 widening PR (Day 0) edits `.github/path-solve-ci-targets.txt` only and is also outside PR23 scope.
4. **Names the pipeline-retest invocation** for checkpoint days (Days 5, 10, 13) — including the PR22 audit-script command.
5. **Has explicit success criteria** mirroring PLAN.md but expressed as one-line check items the engineer can ✅ at end-of-day.

The prompts are designed for **direct invocation** — the engineer copies the day's prompt into a fresh session and runs it.

---

## Cross-Cutting Rules (every day)

- **PR14 reaffirmation** — every `src/emit/`, `src/kkt/stationarity.py`, `src/kkt/complementarity.py`, `src/ad/derivative_rules.py`, `src/ad/constraint_jacobian.py` PR MUST include at least one regenerated `*_mcp.gms` artifact in the diff. Reviewers read the regenerated section.
- **PR20 Phase 0 acceptance gate** — every `src/ad/`, `src/kkt/`, `src/emit/` PR MUST cross-reference a Phase 0 doc with hand-derived KKT shape verified byte-stable on a concrete target. No exception.
- **PR23 self-review** — every CI-workflow PR (`.github/workflows/*.yml`/`.yaml`, `scripts/ci/*`, `.github/actions/*`) fills in the 32-item checklist in the PR description BEFORE requesting review.
- **PR22 audit script** at every mid-sprint retest (Days 5, 10, 13): `scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA> --format markdown --mode retest`.
- **Quality gate** before every commit: `make typecheck && make format && make lint && make test`. All four must pass.
- **End-of-day:** update `SPRINT_LOG.md` Day N section with hours actually spent, deliverables landed, KUs verified, and any carryforward to the next day.

---

## Day 0 Prompt — Sprint Kickoff (~8h)

**Context:** Sprint 27 begins today. Today's focus is PR19 widening + 3 AD architectural Phase 0 validation experiments → binding PROCEED/REPLAN signals for Priority 3 sub-priorities (#1390, #1385, #1393+#1335). Without these binding signals, Day 4–8 Priority 3 implementation effort is unconstrained.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §4 "Day 0"
- `docs/planning/EPIC_4/SPRINT_27/PR19_WIDENING_DESIGN.md` §6 (10-min edit spec)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.1–3.3 (3 experiments)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §4.1–4.2 (launch + qdemo7 anchors)
- `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" (scope clauses — note that PR23 does **NOT** apply to the PR19 widening, which edits `.github/path-solve-ci-targets.txt` only; the scope is `.github/workflows/*.yml`/`.yaml`, `scripts/ci/*`, `.github/actions/*`)

**Tasks (in order):**

1. **Record Day 0 anchor SHA in BOTH PLAN.md AND SPRINT_LOG.md.** Run `git rev-parse HEAD` on `main`. Open `PLAN.md` §4 "Day 0 Anchor SHA" and replace `**TBD**` with the SHA. Then open `SPRINT_LOG.md` §"Day 0 Anchor SHA" (top-level section, near the beginning of the file) and replace its `**TBD**` with the same SHA. **Both files need the same recorded SHA** — `PLAN.md` is the canonical schedule reference and `SPRINT_LOG.md` is what mid-sprint retest entries cite for `--since-commit <SHA>` paste-ins; leaving either at `TBD` causes confusion later. Commit both edits on a `planning/sprint27-day0-setup` branch.
2. **Run PR22 baseline.** `.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA> --format markdown --mode retest > /tmp/sprint27_day0_baseline.md`. Expect output: 0 commits / 0 changes (Day 0 = anchor itself).
3. **PR19 widening.** Edit `.github/path-solve-ci-targets.txt` per `PR19_WIDENING_DESIGN.md` §6 (add launch + 14 net-new #1398-affected models as Pattern C soft-fail — **launch corrected Day 0 from tier=1 to pattern-c: MODEL STATUS 5 Locally Infeasible, the #1378 target**). Open PR. PR23 self-review NOT required — the targets file is outside PR23 scope per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope" (PR23 applies to `.github/workflows/*.yml`/`.yaml`, `scripts/ci/*`, `.github/actions/*` only). Include the PR19 widening dry-run validation evidence from `PR19_WIDENING_DESIGN.md` §6 in the PR description. Expected file count: 1.
4. **AD experiment #1390 kand** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.1. Apply prototype at `src/ad/constraint_jacobian.py:903` + `:1027`. Regenerate `kand_mcp.gms`. Verify 22 phantom-offset `lam_dembalx(j,t+1,n+k)` terms collapse to 1 predicate-guarded Sum. Record binding signal in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 table (PROCEED / REPLAN).
5. **AD experiment #1385 srpchase** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.2. Apply Option B runtime-guard at `src/ad/index_mapping.py:377` + `src/kkt/stationarity.py`. Regenerate `srpchase_mcp.gms`. Verify clean GAMS compile. Record binding signal.
6. **AD experiment #1393+#1335 otpop** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.3. Apply Approach C at `src/ad/derivative_rules.py:2607`. Regenerate `otpop_mcp.gms`. Run NLP+MCP and verify `pi ≈ 4217.80` matches NLP. Record binding signal.
7. **Priority 1 anchor hand-derivation — launch + qdemo7.** Follow `PRIORITY_1_ANCHOR_MAPPING.md` §4.1 (launch `stat_weight(s)` byte-stability) and §4.2 (qdemo7 `stat_xcrop(c)` Pattern C). Hand-derive KKT, record in scratch notes for Day 1 continuation.
8. **KU 6.1 #1224 bundle inspection.** Read `src/ad/index_mapping.py`. Decide whether the #1224 `IndexOffset(ParamRef)` fix overlaps the #1385 patch site (`:377`). Record decision in `KNOWN_UNKNOWNS.md` Unknown 6.1.
9. **Update KNOWN_UNKNOWNS.md.** KUs 3.1, 3.2, 3.3, 6.1 → ✅ VERIFIED with binding signals. KU 3.4 + 3.5 cross-reference the §3.5 binding table.
10. **Open SPRINT_LOG.md Day 0 entry.** Record hours, deliverables, binding signals, KUs verified.

**Success criteria (Day 0):**
- [ ] Day 0 anchor SHA recorded in BOTH `PLAN.md` §4 "Day 0 Anchor SHA" AND `SPRINT_LOG.md` §"Day 0 Anchor SHA" — neither file may remain at `**TBD**`.
- [ ] PR19 widening PR open with the dry-run validation evidence from `PR19_WIDENING_DESIGN.md` §6 in the PR description (PR23 self-review NOT required for this targets-file-only PR per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope").
- [ ] All 3 Priority 3 sub-priorities have binding PROCEED or REPLAN signals.
- [ ] 2 of 8 Priority 1 anchor KKT shapes hand-derived.
- [ ] KU 6.1 (#1224 bundle decision) ✅ VERIFIED.
- [ ] SPRINT_LOG.md Day 0 entry committed.

---

## Day 1 Prompt — Priority 1 Phase 0 + first prototype (~10h)

**Context:** Continue Priority 1 #1398 work from Day 0. Complete Phase 0 hand-derivation for the remaining 6 anchors. Land first prototype of the tightened gate predicate. Verify 8-anchor byte-stability.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §5 "Day 1"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_1_ANCHOR_MAPPING.md` §4.3–4.7 (6 remaining anchors: ferts, sambal, ganges, sroute, turkpow, dinam)
- Day 0 scratch notes (launch + qdemo7 hand-derived KKT)
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates" (PR20)

**Tasks:**

1. Complete Phase 0 hand-derivation for 6 remaining anchors per `PRIORITY_1_ANCHOR_MAPPING.md` §4.3–4.7. dinam has 2 distinct sub-shapes (per §4.7) — derive both. Record all 8 hand-derived KKTs in scratch notes.
2. Implement first prototype of tightened `_find_pattern_c_alias_sum` gate predicate at `src/kkt/stationarity.py` per Day 0 AD-experiment-derived predicate signature.
3. Regenerate `*_mcp.gms` for 8 anchors. Byte-compare against hand-derived KKT shapes. Apply the §4 grep specs from `PRIORITY_1_ANCHOR_MAPPING.md` to verify each anchor.
4. If any anchor diverges → iterate predicate (Day 1 budget includes 1.5h for verification + 0.5h buffer).
5. Run `make typecheck && make format && make lint && make test` before EOD commit.
6. Update SPRINT_LOG.md Day 1 entry.

**Success criteria (Day 1):**
- [ ] All 8 anchor KKT shapes hand-derived + recorded.
- [ ] First prototype tightened gate predicate committed to `planning/sprint27-day1-p1` branch.
- [ ] All 8 anchors byte-stable vs hand-derived KKT (or specific divergences recorded for Day 2 iteration).
- [ ] KU 1.3 (gate predicate fires correctly on launch-shape only) status updated.

---

## Day 2 Prompt — Priority 1 full regression + PR open (~10h)

**Context:** Land the tightened predicate. Regenerate all 15 #1398-affected models + launch. Verify bucket-provenance recovery (qdemo7 → compare_match, etc.). Open PR with **PR14 reaffirmation + PR20 Phase 0 cross-reference** (the predicate change is in `src/kkt/stationarity.py` — pure `src/` change, so PR23 does NOT apply per `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope").

> ✅ **DAY 2 COMPLETE (2026-06-03).** All tasks done: regeneration, bucket-provenance, Tier 0/1 byte-stability, the §4.2/§4.4 grep-spec correction (carryforward commit `4de59037`), and **PR #1414 opened, reviewed, and MERGED to main (`853000ef`)** — Priority 1 #1398 landed. Note for reference: `PRIORITY_1_ANCHOR_MAPPING.md` §4.2 (ferts) + §4.4 (ganges) grep specs were corrected (they had documented the buggy gate-mangled baseline; qdemo7 §4.1 was already correct).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §5 "Day 2"
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §6 (15 affected models + Day 0 buckets)
- `CONTRIBUTING.md` §"Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)" + §"Phase 0 Acceptance Gates (PR20, ...)" (PR23 NOT applicable to this `src/`-only PR per the `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" §"Scope" subsection)

**Tasks:**

1. ✅ DONE (carryforward). Regenerate `*_mcp.gms` for all 15 #1398-affected models + launch (`run_full_test.py --model <name>`). 9 artifacts changed; 6 affected + launch + 11 canaries byte-identical.
2. ✅ DONE (carryforward). Bucket-provenance (Day 0 → Day 2): qdemo7 → `compare_match`; egypt/ferts/shale/srpchase → `path_solve_license`; ganges → `path_syntax_error` (recovered from translate_timeout); sambal/qsambal/harker → compare_mismatch; tfordy/sroute → path_solve_license; **dinam/gangesx/turkpow → `path_syntax_error` (residual PRE-EXISTING non-#1398 errors — turkpow byte-identical to baseline, dinam −2 errors; file as Sprint 28 candidates)**; launch byte-stable. **No regressions.**
3. ✅ DONE (carryforward). Tier 0/1 byte-stability — all 11 canaries + `launch` byte-identical vs main (zero diffs).
4. ✅ DONE (PR #1414). Authored PR description: **PR14 disclosure** (9 regenerated `.gms` files in diff) + **PR20 Phase 0 cross-reference** (`PRIORITY_1_ANCHOR_MAPPING.md` §4 anchor-by-anchor hand-derived KKT shapes). PR23 N/A — pure `src/kkt/stationarity.py` change.
5. ✅ DONE. PR #1414 opened; one review comment (ferts §4.2 header consistency) addressed; **merged to main (`853000ef`)**.
6. ✅ DONE. Quality gate green (`make test` → 4737 passed, 10 skipped, 1 xfailed); SPRINT_LOG Day 2 entry recorded.

**Success criteria (Day 2):**
- [x] 15 #1398-affected models at Day 0 baseline buckets or better — **no regressions** (qdemo7 → compare_match; egypt/ferts/shale/srpchase → path_solve_license). dinam/gangesx/turkpow stay at path_syntax_error from pre-existing non-#1398 errors → Sprint 28 candidates.
- [x] launch byte-stable.
- [x] Tier 0/1 canaries byte-stable (zero diffs on non-affected models).
- [x] PR open with PR14 + PR20 Phase 0 disclosures (PR23 not applicable to this `src/`-only PR) — **PR #1414**.
- [x] First review iteration responded to (ferts §4.2 header consistency) — **PR #1414 MERGED to main (`853000ef`)**.

---

## Day 3 Prompt — Priority 1 merge + Priority 2 Phase 0 start (~8h)

**Context:** Verify PR19 widening fires correctly on the merged commit. Start Priority 2 #1381 Phase 0 hand-derivation for camcge `nu_ieq`. (**Priority 1 #1398 already merged early** — PR #1414 → main `853000ef`, 2026-06-03 — so the "iterate + merge" tasks below are ✅ DONE; Day 3's live work is tasks 3–6.)

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §5 "Day 3" + §6 "Day 4"
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 2" (Pattern C Phase B redesign)
- `docs/issues/ISSUE_1381_*.md` if present

**Tasks:**

1. ✅ DONE. PR review iteration on Priority 1 PR #1414 (one round: ferts §4.2 header consistency).
2. ✅ DONE. Priority 1 PR #1414 merged to main (`853000ef`).
3. ✅ DONE. Verify PR19 widening CI fires correctly. Verified via **PR #1414's** `pr19-emit-solve-validation` run (it touches the trigger paths) — **passed at 37s** (~`PR19_WIDENING_DESIGN.md` §7 projection); launch soft-fails as pattern-c, Tier 0/1 hard-fail all pass. A dedicated no-op PR was unnecessary. (If verifying a future emit-only change that does NOT touch the trigger paths, trigger a no-op PR on the target list instead.)
4. ✅ DONE. **Priority 2 Phase 0 started** — hand-derived camcge `nu_ieq` (stat_dk) cross-term + all 5 camcge consolidation variants; identified cesam2 (dim-mismatch B-3) as second anchor. Recorded in `DAY3_P2_PHASE0_NOTES.md`.
5. ✅ DONE. KNOWN_UNKNOWNS.md: KU 1.3 ✅ VERIFIED (Day 1, in PR #1414); KU 2.1 → 🟡 PARTIALLY VERIFIED (Day 3 hand-derivation); KU 1.1/1.2/1.4 verified at prep.
6. ✅ DONE. SPRINT_LOG.md Day 3 entry recorded. Solve/Match unchanged (P1 unblocks the Day 5 retest).

**Success criteria (Day 3):**
- [x] Priority 1 PR merged to main (PR #1414, `853000ef`).
- [x] PR19 widening verified — fired on PR #1414 (touches the trigger paths) and **passed (37s)**; a dedicated no-op PR was unnecessary.
- [x] camcge Phase 0 hand-derivation complete — all 5 consolidation variants in `DAY3_P2_PHASE0_NOTES.md` (cesam2 B-3 identified; finalizes Day 4).
- [x] KU 1.3 ✅ VERIFIED (Day 1).

---

## Day 4 Prompt — Priority 2 Pattern C Phase B implement (~12h)

**Context:** Land Pattern C Phase B redesign. camcge + cesam2 unblock from `path_syntax_error` to `compare_match` (+2 Solve, +2 Match).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §6 "Day 4"
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 2"
- Day 3 camcge Phase 0 hand-derivation notes

**Tasks:**

1. Finalize Phase 0 hand-derivation (camcge + cesam2 `nu_ieq` cross-term).
2. Implement Pattern C Phase B "build consolidated multiplier term from source Sum body structure" at `src/kkt/stationarity.py`. Per `PROJECT_PLAN.md` Priority 2, the approach intercepts BEFORE element-to-set substitution (which collapses alias name on the launch-shape Phase A swap).
3. Regenerate camcge + cesam2 `*_mcp.gms`. Verify hand-derived KKT byte-stable for `nu_ieq` cross-term.
4. Tier 0/1 canary byte-stability check (KU 2.3).
5. Author PR description: PR14 + PR20 Phase 0 cross-reference (cite the camcge + cesam2 `nu_ieq` cross-term Phase 0 from Day 3/4 hand-derivation). PR23 not applicable — pure `src/kkt/stationarity.py` change. Open PR.
6. EOD quality gate + SPRINT_LOG.md Day 4 entry.

**Success criteria (Day 4):**
- [ ] Pattern C Phase B redesign committed.
- [ ] camcge + cesam2 regenerated; both unblock to `compare_match` (+2 Solve, +2 Match).
- [ ] Tier 0/1 canaries byte-stable.
- [ ] KUs 2.1, 2.2, 2.3 ✅ VERIFIED.
- [ ] PR open.

---

## Day 5 Prompt — Checkpoint 1: Pipeline Retest + Priority 5 start + Priority 3 first sub-priority (~10h)

**Context:** Mid-sprint Checkpoint 1 per PR6 cadence. Run full pipeline retest. Invoke PR22 audit script to enumerate emit-changed models. Start Priority 5 (#1356 fawley). **Per the Option 1 re-plan (Day 0 binding signals: all 3 P3 prep sites disproven), there is no "P3 first sub-priority" to lift — instead, run the #1390 re-scoped Phase 0 on the `stationarity.py` layer** to decide whether #1390 implements Days 6–7.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §7 "Day 5" + the §2 Option 1 re-plan banner + §8 (re-planned P3)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §3 + §8 (Day 5 handoff)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.5 (#1390 REPLAN evidence: `_apply_offset_substitution` fires 22×) + §8.5 (binding table + redirected surface)

**Tasks:**

1. **PR22 audit script invocation:**
   ```bash
   .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
       --since-commit <Day-0 SHA> --format markdown --mode retest \
       > /tmp/sprint27_day5_retest.md
   ```
   Paste output into SPRINT_LOG.md Day 5 entry. Expected: P1 #1398 (15+launch) + P2 #1381 (camcge+cesam2) artifacts.
2. **Full pipeline retest:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (background). Track headline metrics + bucket-provenance per PR17.
3. Author Day 5 SPRINT_LOG.md checkpoint entry: headline metrics (Solve/Match/path_syntax_error counts), bucket-provenance table (Day 0 → Day 5 transitions), KU updates.
4. **Priority 5 #1356 fawley start** per `PRIORITY_5_FIX_SURFACE.md` §3 + §8: author helpers `_extract_subset_predicate` + `_bound_expr_subset_dependency` at `src/kkt/complementarity.py`; apply Patch A+B at `:473-483` + `:485-494`; regenerate `fawley_mcp.gms`.
5. **#1390 re-scoped Phase 0** (Option 1 re-plan): hand-derive the predicate-guarded-Sum collapse on the `stationarity.py` offset re-symbolization layer (`_collect_lead_lag_offsets:95` → `_apply_offset_substitution:2433` / `_apply_alias_offset_to_deriv:2264` — the functions that fire 22× = the 22 kand phantom terms). Prototype the collapse (model-guarded), regenerate `kand_mcp.gms`, verify the 22 `lam_dembalx(j,t+1,n±k)` terms become 1 predicate-guarded Sum + Tier 0/1 byte-stable. Record a binding **re-PROCEED / re-REPLAN** signal in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5.
6. **Verify the otpop interaction:** at this retest, check whether otpop reached compare_match from #1357 alone, or still needs the deferred #1393+#1335 — this determines whether the #1357 firm Solve gain holds (see PLAN.md §2 Solve row).

**Checkpoint 1 success criteria** (P1 merged Day 3 + P2 merged Day 4 → both gains expected at Day 5 retest):
- [ ] Pipeline retest shows **Solve ≥ 106** (Day 0 103 + **#1398 qdemo7 +1** + #1381 camcge/cesam2 +2 = 106). A reading of 105 indicates qdemo7 did not recover — investigate P1 before Day 6.
- [ ] Pipeline retest shows **Match ≥ 62** (Day 0 59 + **#1398 qdemo7 +1** + #1381 ×2 = 62).
- [ ] PR22 audit script output captures camcge + cesam2 + 15 #1398 + launch artifacts.
- [ ] P5 #1356 first patch committed.
- [ ] **#1390 re-scoped Phase 0 binding signal recorded** (re-PROCEED → implement Days 6–7; re-REPLAN → defer #1390 to Sprint 28, redirect Days 6–7 to P7/P4, Match → 65 per §17).

---

## Day 6 Prompt — Priority 3 #1390 implement (re-scoped to `stationarity.py`) + parallel Priority 5 #1357 otpop (~12h)

**Context:** Implement #1390 on the **redirected `stationarity.py` offset re-symbolization layer** (the Day 0 AD site `constraint_jacobian.py:903/1027` was disproven). **Gated on the Day 5 #1390 re-scoped Phase 0** — if it re-REPLAN'd, SKIP #1390, file a Sprint 28 carryforward, redirect this slot to P7 #1387 / P4, and note Match → 65 (§17). In parallel, start P5 #1357 otpop.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 6" (re-planned)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.5 (#1390 binding REPLAN + redirected surface) + §8.5
- Day 5 #1390 re-scoped Phase 0 result + scratch notes

**Tasks (if Day 5 re-PROCEED'd):**

1. #1390 implement the predicate-guarded-Sum collapse at `src/kkt/stationarity.py` (`_apply_offset_substitution:2433` / `_apply_alias_offset_to_deriv:2264` / `_collect_lead_lag_offsets:95`) — **NOT** `constraint_jacobian.py:903/1027`. Collapse the 22 per-offset `lam_dembalx(j,t+1,n±k)` terms into one `sum(n_inner$tree(n,n_inner), eps*lam_dembalx(j,t+1,n_inner))$(tn(t+1,n_inner))`.
2. Phase 0 verify: regenerate `kand_mcp.gms`; verify the 22 phantom-offset terms collapse to 1 predicate-guarded Sum; byte-compare against the Day 5 hand-derived KKT. KU 3.1 ✅ re-VERIFIED on the redirected layer.
3. Tier 0/1 byte-stability (regenerate all 11 Tier 0/1 canaries + `launch` byte-stability anchor, diff vs main — `launch` is PR19 pattern-c after the Day 0 correction but is still byte-checked here).
4. **Parallel: Priority 5 #1357 otpop** — apply Phase 0 + first patch (same `complementarity.py:473-483` + `:485-494` patch sites as #1356 fawley); regenerate `otpop_mcp.gms`.
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 6):**
- [ ] #1390 kand 22 → 1 predicate-guarded Sum on the `stationarity.py` layer (OR #1390 deferred + redirected if Day 5 re-REPLAN'd).
- [ ] KU 3.1 re-verified on the redirected layer.
- [ ] P5 #1357 otpop first patch committed.

---

## Day 7 Prompt — #1390 PR + #1385 translate-time-only short-circuit + Priority 5 close (~12h)

**Context:** Open the #1390 PR (if it landed). Implement #1385 as a **translate-time-only** short-circuit (the cross-term emit half is DEFERRED to Sprint 28 per the §7 scoped-PROCEED rule). Close Priority 5 (#1356 + #1357 combined PR).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 7" (re-planned)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §4.5 (#1385 SCOPED-PROCEED: translate >180s→6.0s validated; cross-terms unproven) + §8.5
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §8 (clearlak byte-stability mitigation per KU 5.3)

**Tasks:**

1. Open the #1390 PR (if Day 6 landed it) with PR14 + PR20 Phase 0 cross-reference to the **`stationarity.py`** redirected shape (cite the Day 5/6 hand-derived kand `stat_y(j,t,n)` collapse). PR23 not applicable — pure `src/kkt/stationarity.py` change.
2. #1385 implement the **translate-time-only** short-circuit: generalize the single-`SetMembershipTest` detection to skip enumeration at `src/ad/index_mapping.py:377` (Day 0-validated: srpchase >180s → **6.0s**), plus a runtime-guard equation-body emit at `src/kkt/stationarity.py`. **Do NOT attempt the J_gᵀ·lam cross-terms** — file a Sprint 28 follow-on issue for them.
3. #1385 Phase 0 verify: regenerate `srpchase_mcp.gms`; verify translate <10s + clean GAMS compile + no quoted-literal set-name indices. Document the deferred-cross-term scope in the PR. KU 3.2 ✅ VERIFIED **as scoped (translate-time only)**. Note: this is a **Translate** gain, not a Solve gain — iswnm/mexls/nebrazil/sarf do NOT reach compare_match this sprint.
4. **Priority 5 close:** combined fawley + otpop PR open. Per `PRIORITY_5_FIX_SURFACE.md` §8, run clearlak byte-stability check (zero diff expected per KU 5.3 LOW regression risk).
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 7):**
- [ ] #1390 PR open (if landed Day 6).
- [ ] #1385 srpchase translates <10s, clean compile; Sprint 28 cross-term issue filed.
- [ ] P5 combined PR open with clearlak byte-stability proof.
- [ ] KUs 3.2 (scoped), 5.1, 5.2, 5.3 ✅ VERIFIED.

---

## Day 8 Prompt — #1385 PR + #1393+#1335 Sprint 28 carryforward + Priority 7 #1387 implement (pulled forward) (~12h)

**Context:** Open the #1385 PR. **Do NOT implement #1393+#1335** — Approach C was disproven Day 0; file the Sprint 28 carryforward instead. Use the freed budget to **implement P7 #1387** (pulled forward from Day 10).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 8" (re-planned)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §5.6 (#1393+#1335 Approach C REPLAN; redirected surfaces) + §5.5 fallback rule
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §3 (#1387 sign-flip + term-omission specs)

**Tasks:**

1. Open #1385 PR (PR14 + PR20). State the scoped/translate-only boundary + link the Sprint 28 cross-term issue. Iterate first review round.
2. **#1393+#1335 Sprint 28 carryforward filing** (replaces implementation): file the issue with the Day 0 evidence — Approach C inert (`_is_concrete_instance_of` never reached, byte-identical emit); #1393 redirects to the `stationarity.py` symbolic-collapse path; #1335 needs a `card(t)-ord(t)` offset evaluator (`_try_eval_offset`). They are now **distinct** fixes. Use the carryforward template in `PRIORITY_3_RISK_ASSESSMENT.md` §5.5.
3. **Priority 7 #1387 cclinpts — Phase 0 hand-derivation AND implement** (pulled forward from Day 10): hand-derive `stat_b(j)` (sign-flip) + `stat_fb(j)` (missing 3 of 4 cross-terms) per `PRIORITY_7_FIX_SURFACE.md` §3, then implement at `src/ad/derivative_rules.py:1847` + `src/kkt/stationarity.py:1352/1835`. Regenerate `cclinpts_mcp.gms`; verify against hand-derived KKT.
4. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 8):**
- [ ] #1385 PR review iteration in flight.
- [ ] #1393+#1335 Sprint 28 carryforward filed (NOT implemented).
- [ ] #1387 Phase 0 hand-derivation complete AND implemented; cclinpts emit matches hand-derived KKT.
- [ ] KU 3.3 reflects the Day 0 REPLAN + Sprint 28 deferral (already updated Day 0).

---

## Day 9 Prompt — Priority 3 close + P7 #1387 close (pulled forward) + Priority 4 #1378 launch numerics start (~10h)

**Context:** Merge the remaining Priority 3 PRs (#1390 if it landed + #1385 translate-only — **#1393+#1335 has NO PR**, it was filed as a Sprint 28 carryforward Day 8). Open the **P7 #1387 PR** (implemented Day 8 — pulled forward from Day 11). Start Priority 4 launch numerics.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §9 "Day 9" (re-planned)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 4" (launch PATH-numerics investigation)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` Unknown 4.1 + 4.2 research questions

**Tasks:**

1. Merge any P3 PRs still open from Days 6–7 (#1390 if landed; #1385 translate-only). #1393+#1335 = no PR (Sprint 28 carryforward).
2. **P7 #1387 PR open** (implemented Day 8) with PR14 + PR20 cross-reference; first review iteration. (Pulled forward from Day 11.)
3. **Priority 4 #1378 launch numerics:** investigate per `PROJECT_PLAN.md` Priority 4 — try (a) initial-point tuning, (b) `--nlp-presolve`, (c) NLP-warm-start, (d) sign/scaling refinement in `_apply_pattern_c_swap_to_term`. Pick the approach that produces MODEL STATUS 1 or `model_optimal_presolve` recovery with matching solution. KU 4.1 ✅ VERIFIED.
4. Verify launch byte-stability anchor preserved (KU 4.2 — does the Priority 4 fix shape constrain launch byte-stability?).
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 9):**
- [ ] P3 PRs merged or in final review (#1390 if landed + #1385 scoped); #1393+#1335 carryforward filed (no PR).
- [ ] P7 #1387 PR open.
- [ ] launch MODEL STATUS 1 or `model_optimal_presolve` with matching solution.
- [ ] KUs 4.1, 4.2 ✅ VERIFIED (3.4/3.5 verified Day 0).

---

## Day 10 Prompt — Checkpoint 2: Pipeline Retest + Priority 4 close + Priority 7 #1387 merge (~10h)

**Context:** Mid-sprint Checkpoint 2 per PR6. Full pipeline retest. PR22 audit-script invocation. Close Priority 4. **Merge** Priority 7 #1387 (implemented Day 8, PR'd Day 9 — pulled forward under the Option 1 re-plan). Freed ~2.5h → start P6 #1224 / P9 #1374 early if convenient.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §10 "Day 10" (Checkpoint 2)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §3 (patch sites)

**Tasks:**

1. **PR22 audit script:**
   ```bash
   .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
       --since-commit <Day-0 SHA> --format markdown --mode retest \
       > /tmp/sprint27_day10_retest.md
   ```
   Paste into SPRINT_LOG.md Day 10. Expected: P1+P2+P3+P5 artifacts (large diff).
2. **Full pipeline retest** — Checkpoint 2.
3. Author Day 10 SPRINT_LOG.md checkpoint entry. Expected (Option 1 re-plan): **Solve ≥ 108** (Day 0 +5 firm: #1398 qdemo7 +1, #1381 ×2, #1357, #1356 — verify #1357 otpop held despite the #1393+#1335 deferral) and **Match ≥ 65 firm / 66 if #1390 re-scope landed** (Day 0 +6 firm: #1398 qdemo7 +1, #1381 ×2, #1357, #1356, #1378 launch +1; **#1390 kand +1 conditional** on the Day 5 re-scoped Phase 0). #1385 is translate-only → a Translate gain, not Solve/Match.
4. **Priority 4 close** — merge launch fix PR.
5. **Priority 7 #1387 merge** (implemented Day 8, PR'd Day 9). Freed time → optionally start P6 #1224 / P9 #1374 early.
6. EOD quality gate + SPRINT_LOG.md.

**Checkpoint 2 success criteria** (re-planned):
- [ ] **Solve ≥ 108** (Day 0 103 + 5 firm: #1398 qdemo7 +1, #1381 ×2, #1357, #1356; launch's #1378 is a Match gain not Solve). If #1357 otpop slipped (needs deferred #1393+#1335) → Solve = 107; re-classify per PLAN.md §2.
- [ ] **Match ≥ 65 firm; 66 if the #1390 re-scope landed** (Day 0 59 + 6 firm + #1390 conditional). A reading of 62 indicates firm recoveries silently failed — investigate before Day 11. Match = 65 (with #1390 deferred) is an at-target-minus-one result to record per §17, not a checkpoint failure.
- [ ] **path_syntax_error ≤ 6** (all path_syntax_error contributors P1+P2+P5 merged by Day 9; the final-target threshold should already be met).
- [ ] PR22 output captures all P1+P2(+P3 #1390 if landed)+P5 artifacts.
- [ ] Priority 4 PR merged; #1387 merged.

---

## Day 11 Prompt — Priority 7 #1388 discriminator + Priority 6 #1224 start (~10h)

**Context:** Run the §4.6 3-way discriminator on #1388 camshape. Classify Case (a) / (b) / (c). Start #1224 mine (standalone). **#1387 was implemented Day 8 + closed Day 9–10** under the Option 1 re-plan, so it is NOT on Day 11; the freed ~2h is slack.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §11 "Day 11"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §4.6 (NLP-warm-start + 10-symbol display pre-check + 3-way discriminator)
- Day 0 KU 6.1 decision for #1224 (**STANDALONE**)

**Tasks:**

1. **#1388 camshape NLP-warm-start runtime test:**
   - Regenerate `camshape_mcp_presolve.gms` via `.venv/bin/python -m src.cli data/gamslib/raw/camshape.gms --nlp-presolve -o /tmp/camshape_mcp_presolve.gms --quiet`.
   - Inject `display` statement for all 10 warm-startable symbols (3 primals + 7 multipliers per `PRIORITY_7_FIX_SURFACE.md` §4.6 display pre-check).
   - Run `gams /tmp/camshape_mcp_presolve.gms o=/tmp/camshape_mcp_warm.lst lo=2`.
   - Verify all 10 display blocks show NLP-solution-derived values (NOT MCP defaults).
   - Classify Case (a) MS 1 obj≈4.2841 / Case (b) MS 5 + non-inert shape divergence / Case (c) MS 5 + no non-inert shape divergence per §4.6.
2. **#1388 fix or carryforward** based on discriminator:
   - Case (a): emit-bug fix at Candidate A `src/kkt/stationarity.py:1835` OR Candidate B `src/ad/constraint_jacobian.py:903 + :1027` per §4.4. ~4.5h.
   - Case (b): emit-bug fix + add warm-start guidance to `data/gamslib/mcp/camshape_mcp_presolve.gms` defaults. ~5.5h.
   - Case (c): file Sprint 28 carryforward per §6 template. ~1.25h.
3. **Priority 6 #1224 start (standalone)** — Day 0 KU 6.1 decided **STANDALONE** (no `index_mapping.py` overlap with #1385; the `IndexOffset(ParamRef)` surface is `constraint_jacobian.py:_try_eval_offset:133` + `derivative_rules.py:2793`). Implement per `PROJECT_PLAN.md` §"Priority 6" — do NOT bundle with #1385.
4. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 11):**
- [ ] #1388 camshape classified per §4.6 3-way discriminator.
- [ ] #1388 fix landed (Case a/b) OR Sprint 28 carryforward filed (Case c).
- [ ] #1224 mine implementation started (standalone).
- [ ] KUs 7.2, 7.3 ✅ VERIFIED (7.1 verified at prep; #1387 delivered Day 8–10).

---

## Day 12 Prompt — Priority 6 #1224 FULL (carried from Day 11) + Priority 8 #1400 + Priority 9 #1374 (~10h)

**Context:** **Implement #1224 IN FULL — it was NOT started on Day 11** (Day 11 was consumed by the #1388 §4.6 discriminator dive + the #1424 subset-corruption emit bug it surfaced; fixed in PR #1425). So Day 12 does #1224 **start-to-finish** (Phase 0 + implement + PR), not just "close." Then fix the pipeline absolute-path leak (#1400) and audit + targeted-fix #1374 emit duplicate-init bugs. **Day 12 is the tightest day of the sprint** — if #1224 runs long, slip #1374 first (then #1400) to the Day 13 buffer; #1224 is the priority.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §12 "Day 12" (note the Day-11 carryforward callout)
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 6" (#1224 mine) + §"Priority 8" (#1400 corrected scope — `scripts/gamslib/run_full_test.py:899` `mcp_file_used` only; no `solve_mcp.py`)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` Unknown 6.1 (#1224 STANDALONE), 6.2, 8.1, 8.2, 9.4

**Tasks:**

1. **#1224 mine — FULL implementation (carried from Day 11; NOT started there):** Phase 0 acceptance gate (PR20 — this touches `src/ad/`) **AND** implement **AND** PR. **STANDALONE** per Day-0 KU 6.1 — the `IndexOffset(ParamRef)` surface is `src/ad/constraint_jacobian.py:_try_eval_offset:133` + `src/ad/derivative_rules.py:2793`; NO `index_mapping.py`/#1385 overlap; do **NOT** bundle with #1385. Document mine's next failure mode (KU 6.2): `path_syntax_error`, `model_infeasible`, `compare_match`, or other.
2. **Priority 8 #1400 fix** at `scripts/gamslib/run_full_test.py:899`. Choose KU 8.2 implementation: basename only (always `data/gamslib/mcp/<model>_mcp_presolve.gms`) OR `PROJECT_ROOT`-relative. Run the audit grep against a recent pipeline JSON: `grep -oE '"[^"]+": "/[^"]+"' data/gamslib/gamslib_status.json | sort -u`. If `mcp_file_used` is the only leak field, KU 8.1 ✅ VERIFIED at corrected scope. _(Slippable to Day 13 if #1224 overruns.)_
3. **Priority 9 #1374 corpus sweep** — scan all 134 translating `*_mcp.gms` artifacts for duplicate `var.l(idx) = val` patterns. Document count + shapes in working notes. Apply targeted fix in `src/emit/` for the most common 1–2 shapes. Defer remaining to Sprint 28 per `PROJECT_PLAN.md` Priority 9. KU 9.4 ✅ VERIFIED. _(**First to slip to Day 13 buffer** if #1224 overruns.)_
4. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 12):**
- [ ] **#1224 mine implemented start-to-finish (Phase 0 + impl + PR)** — translates from `translate_internal_error` to `translate_success` (+1 Translate; Solve gain conditional per KU 6.2). **Non-negotiable Day-12 deliverable.**
- [ ] #1400 pipeline path leak fixed; `gamslib_status.json` produces byte-identical output across machines. _(May slip to Day 13.)_
- [ ] #1374 audit complete; targeted fix landed for most common shapes. _(First to slip to Day 13.)_
- [ ] KUs 6.1, 6.2, 8.1, 8.2, 9.4 ✅ VERIFIED.

---

## Day 13 Prompt — Final Retest + SPRINT_LOG + SPRINT_RETROSPECTIVE (~8h)

**Context:** Final pipeline retest under multiple `PYTHONHASHSEED` values. Author Sprint 27 SPRINT_LOG.md final-day entry + Sprint 27 SPRINT_RETROSPECTIVE.md. File Sprint 28 carryforwards.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §13 "Day 13"
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` (structural reference)
- Sprint 27 SPRINT_LOG.md (cumulative entries from Days 0–12)

**Tasks:**

1. **Final PR22 audit script:**
   ```bash
   .venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py \
       --since-commit <Day-0 SHA> --format markdown --mode retest \
       > /tmp/sprint27_day13_final.md
   ```
2. **Final pipeline retest under 3 `PYTHONHASHSEED` values** (PR12 determinism guard). Run pipeline 3× with `PYTHONHASHSEED=0`, `PYTHONHASHSEED=1`, `PYTHONHASHSEED=42`. Diff `gamslib_status.json` outputs (modulo wall-time fields). Expect zero diff.
3. **Author Sprint 27 SPRINT_LOG.md final-day entry:** headline metrics (Solve / Match / path_syntax_error / model_infeasible / Translate / Parse / Tests), bucket-provenance Sprint 26 final → Sprint 27 final, per-priority deliverables landed + carryforwards filed.
4. **Author Sprint 27 SPRINT_RETROSPECTIVE.md** mirroring Sprint 26 structure: What Went Well / What We'd Do Differently / Sprint 28 Recommendations / KU Coverage Summary. Reference the 11 prep PRs (#1402–#1411) + the per-priority implementation PRs + the 4 process recommendations (PR20–PR23) all delivered in prep.
5. **File Sprint 28 carryforwards** for any priority that REPLANned: #1388 Case (c) if camshape was Sprint 28; #1374 remaining shapes; any other partial deliverables. Use `PRIORITY_7_FIX_SURFACE.md` §6 carryforward template.
6. Final SPRINT_LOG.md commit.

**Success criteria (Day 13):**
- [ ] Final metrics meet acceptance criteria: Solve ≥ 111, Match ≥ 66, path_syntax_error ≤ 6, model_infeasible ≤ 3, Translate ≥ 135/142, Parse ≥ 142/142, Tests ≥ 4,750.
- [ ] Determinism: byte-identical `gamslib_status.json` under 3 `PYTHONHASHSEED` values.
- [ ] All 28 Sprint 27 KUs ✅ VERIFIED.
- [ ] SPRINT_LOG.md final entry committed.
- [ ] SPRINT_RETROSPECTIVE.md authored.
- [ ] Sprint 28 carryforwards filed.

---

## Pipeline Retest Cadence Summary (Days 5, 10, 13)

Each retest day follows the same checklist:

1. **Day 0 anchor SHA reminder:** `<Day-0 SHA>` was recorded in `PLAN.md` §4 on Day 0. Use this exact SHA in every `--since-commit` invocation across Days 5, 10, 13.
2. **PR22 audit script:** `.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA> --format markdown --mode retest > /tmp/sprint27_dayN_retest.md`
3. **Full pipeline run:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (background; ~3h).
4. **Headline-metrics extraction:** Solve, Match, path_syntax_error, path_solve_terminated, model_infeasible, path_solve_license, Translate, Parse, Tests counts.
5. **Bucket-provenance update per PR17:** transitions table Day 0 → Day N for the failing models touched by Sprint 27 priorities.
6. **SPRINT_LOG.md Day N checkpoint entry:** headline metrics + bucket-provenance table + PR22 output reference + KUs verified at this checkpoint + any anomalies (machine-variance, etc.).

---

## Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` (canonical schedule)
- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` (prep tasks completed)
- `docs/planning/EPIC_4/SPRINT_27/SPRINT_LOG.md` (per-day log; filled in during execution)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` (28 KUs; per-day verification schedule)
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` (Day 0 baseline)
- `docs/planning/EPIC_4/SPRINT_27/prompts/PREP_TASK_PROMPTS.md` (companion: prep-task execution prompts for Tasks 1–11)
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates", §"Emit-Affecting PRs", §"CI Workflow PR Checklist", §"Emit-PR `.gms` Diff Workflow"
