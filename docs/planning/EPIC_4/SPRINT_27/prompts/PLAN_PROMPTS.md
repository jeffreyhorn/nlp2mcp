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
3. **Names the PRs to open** — each `src/`-touching PR follows PR14 (regenerated `.gms` in diff) + PR23 (32-item self-review) + PR20 (Phase 0 acceptance gate).
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
- `CONTRIBUTING.md` §"CI Workflow PR Checklist (PR23, ...)" (apply to PR19 widening PR)

**Tasks (in order):**

1. **Record Day 0 anchor SHA.** Run `git rev-parse HEAD` on `main`. Open `PLAN.md` §4 "Day 0 Anchor SHA" and replace `**TBD**` with the SHA. Commit on a `planning/sprint27-day0-setup` branch.
2. **Run PR22 baseline.** `.venv/bin/python scripts/sprint_audit/changed_emit_artifacts.py --since-commit <Day-0 SHA> --format markdown --mode retest > /tmp/sprint27_day0_baseline.md`. Expect output: 0 commits / 0 changes (Day 0 = anchor itself).
3. **PR19 widening.** Edit `.github/path-solve-ci-targets.txt` per `PR19_WIDENING_DESIGN.md` §6 (add launch as Tier 1 hard-fail; add 14 net-new #1398-affected models as Pattern C soft-fail). Run the PR23 32-item self-review in your scratch notes. Open PR. Expected file count: 1.
4. **AD experiment #1390 kand** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.1. Apply prototype at `src/ad/constraint_jacobian.py:903` + `:1027`. Regenerate `kand_mcp.gms`. Verify 22 phantom-offset `lam_dembalx(j,t+1,n+k)` terms collapse to 1 predicate-guarded Sum. Record binding signal in `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 table (PROCEED / REPLAN).
5. **AD experiment #1385 srpchase** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.2. Apply Option B runtime-guard at `src/ad/index_mapping.py:377` + `src/kkt/stationarity.py`. Regenerate `srpchase_mcp.gms`. Verify clean GAMS compile. Record binding signal.
6. **AD experiment #1393+#1335 otpop** per `PRIORITY_3_RISK_ASSESSMENT.md` §3.3. Apply Approach C at `src/ad/derivative_rules.py:2607`. Regenerate `otpop_mcp.gms`. Run NLP+MCP and verify `pi ≈ 4217.80` matches NLP. Record binding signal.
7. **Priority 1 anchor hand-derivation — launch + qdemo7.** Follow `PRIORITY_1_ANCHOR_MAPPING.md` §4.1 (launch `stat_weight(s)` byte-stability) and §4.2 (qdemo7 `stat_xcrop(c)` Pattern C). Hand-derive KKT, record in scratch notes for Day 1 continuation.
8. **KU 6.1 #1224 bundle inspection.** Read `src/ad/index_mapping.py`. Decide whether the #1224 `IndexOffset(ParamRef)` fix overlaps the #1385 patch site (`:377`). Record decision in `KNOWN_UNKNOWNS.md` Unknown 6.1.
9. **Update KNOWN_UNKNOWNS.md.** KUs 3.1, 3.2, 3.3, 6.1 → ✅ VERIFIED with binding signals. KU 3.4 + 3.5 cross-reference the §3.5 binding table.
10. **Open SPRINT_LOG.md Day 0 entry.** Record hours, deliverables, binding signals, KUs verified.

**Success criteria (Day 0):**
- [ ] Day 0 anchor SHA recorded in PLAN.md.
- [ ] PR19 widening PR open with PR23 32-item self-review filled in (≥ 27 ticked + ≤ 5 N/A annotations).
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

**Context:** Land the tightened predicate. Regenerate all 15 #1398-affected models + launch. Verify bucket-provenance recovery (qdemo7 → compare_match, etc.). Open PR with PR14 + PR23 self-review.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §5 "Day 2"
- `docs/planning/EPIC_4/SPRINT_27/BASELINE_METRICS.md` §6 (15 affected models + Day 0 buckets)
- `CONTRIBUTING.md` §"Emit-Affecting PRs — Required `.gms` Artifact in Diff (PR14)" + §"CI Workflow PR Checklist (PR23, ...)"

**Tasks:**

1. Regenerate `*_mcp.gms` for all 15 #1398-affected models + launch (`run_full_test.py --model <name>` or pipeline subset).
2. Run `scripts/gamslib/run_full_test.py --quiet` on the 15-model + launch subset. Verify bucket-provenance: qdemo7 → `compare_match`; egypt/ferts/shale → `path_solve_license`; sambal/qsambal/harker/tfordy/dinam/ganges/gangesx/sroute/turkpow → Day 0 baseline buckets; launch byte-stable.
3. Tier 0/1 byte-stability verification — regenerate all 12 Tier 0/1 canaries (per `PR19_WIDENING_DESIGN.md` §6 widened list), diff vs main. Expect zero diffs on non-affected canaries.
4. Author PR description: PR14 disclosure (list regenerated `.gms` files via PR22 audit-script invocation) + PR23 32-item self-review filled in.
5. Open PR. Respond to first review iteration.
6. EOD quality gate + SPRINT_LOG.md Day 2 entry.

**Success criteria (Day 2):**
- [ ] 15 #1398-affected models recovered to Day 0 baseline buckets.
- [ ] launch byte-stable.
- [ ] Tier 0/1 canaries byte-stable (zero diffs on non-affected models).
- [ ] PR open with PR14 + PR23 disclosures.
- [ ] First review iteration responded to.

---

## Day 3 Prompt — Priority 1 merge + Priority 2 Phase 0 start (~8h)

**Context:** Iterate Priority 1 PR to merge. Verify PR19 widening fires correctly on the merged commit. Start Priority 2 #1381 Phase 0 hand-derivation for camcge `nu_ieq`.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §5 "Day 3" + §6 "Day 4"
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 2" (Pattern C Phase B redesign)
- `docs/issues/ISSUE_1381_*.md` if present

**Tasks:**

1. PR review iteration on Priority 1 PR (expect ≤ 2 rounds per PR23 compression target).
2. Merge Priority 1 PR.
3. Verify PR19 widening CI fires correctly: trigger a no-op PR on the new widened target list; expect ~37s steady-state runtime per `PR19_WIDENING_DESIGN.md` §7 projection.
4. **Start Priority 2 Phase 0** — hand-derive KKT for camcge `nu_ieq` cross-term. Recorded in scratch notes. Identify cesam2 as second-anchor model (same Phase C-derived shape per `PROJECT_PLAN.md` Priority 2).
5. Update KNOWN_UNKNOWNS.md: KU 1.3 ✅ VERIFIED (gate predicate fires only on launch-shape); KU 1.1, 1.2, 1.4 already verified at prep.
6. SPRINT_LOG.md Day 3 entry. Update sprint cumulative metrics: Solve / Match unchanged but P1 unblocks Day 5 retest.

**Success criteria (Day 3):**
- [ ] Priority 1 PR merged to main.
- [ ] PR19 widening verified on a follow-up no-op PR.
- [ ] camcge Phase 0 hand-derivation complete.
- [ ] KU 1.3 ✅ VERIFIED.

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
5. Author PR description: PR14 + PR23 self-review. Open PR.
6. EOD quality gate + SPRINT_LOG.md Day 4 entry.

**Success criteria (Day 4):**
- [ ] Pattern C Phase B redesign committed.
- [ ] camcge + cesam2 regenerated; both unblock to `compare_match` (+2 Solve, +2 Match).
- [ ] Tier 0/1 canaries byte-stable.
- [ ] KUs 2.1, 2.2, 2.3 ✅ VERIFIED.
- [ ] PR open.

---

## Day 5 Prompt — Checkpoint 1: Pipeline Retest + Priority 5 start + Priority 3 first sub-priority (~10h)

**Context:** Mid-sprint Checkpoint 1 per PR6 cadence. Run full pipeline retest. Invoke PR22 audit script to enumerate emit-changed models. Start Priority 5 (#1356 fawley) + Priority 3 first PROCEED'd sub-priority from Day 0.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §7 "Day 5" (Checkpoint 1)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §3 + §8 (Day 5 handoff)
- Day 0 `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 binding signals (which P3 sub-priority started)

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
5. **Priority 3 first PROCEED sub-priority start** — apply prototype to main (lift from Day 0 experiment scratch branch); first regression test pass.

**Checkpoint 1 success criteria:**
- [ ] Pipeline retest shows Solve ≥ 105 (Day 0 +2 from camcge/cesam2; Match ≥ 61).
- [ ] PR22 audit script output captures camcge + cesam2 + 15 #1398 + launch artifacts.
- [ ] P5 #1356 first patch committed.
- [ ] P3 first sub-priority in progress.

---

## Day 6 Prompt — Priority 3 #1390 kand + parallel Priority 5 #1357 otpop (~12h)

**Context:** Implement #1390 kand per-instance enumeration redesign. In parallel, start P5 #1357 otpop (same patch sites as #1356 fawley).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 6"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.1 (#1390 binding patch shape) + §4 implementation guidance
- Day 0 `PRIORITY_3_RISK_ASSESSMENT.md` §3.5 binding signals for #1390

**Tasks:**

1. #1390 implement predicate-guarded Sum at `src/ad/constraint_jacobian.py:903 + :1027` per Day 0 binding patch shape.
2. Phase 0 verify: regenerate `kand_mcp.gms`; verify 22 phantom-offset `lam_dembalx(j,t+1,n+k)` terms collapse to 1 element. KU 3.1 ✅ VERIFIED.
3. Tier 0/1 byte-stability.
4. **Parallel: Priority 5 #1357 otpop** — apply Phase 0 + first patch (same `complementarity.py:473-483` + `:485-494` patch sites as #1356 fawley); regenerate `otpop_mcp.gms`.
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 6):**
- [ ] #1390 kand cross-term reduces 22 → 1 element.
- [ ] KU 3.1 ✅ VERIFIED.
- [ ] P5 #1357 otpop first patch committed.

---

## Day 7 Prompt — #1390 PR + Priority 3 #1385 srpchase + Priority 5 close (~12h)

**Context:** Open #1390 PR. Implement #1385 srpchase Option B runtime-guard. Close Priority 5 (#1356 + #1357 combined PR).

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 7"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.2 (#1385 binding patch shape)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_5_FIX_SURFACE.md` §8 (clearlak byte-stability mitigation per KU 5.3)

**Tasks:**

1. Open #1390 PR (PR14 + PR23 self-review).
2. #1385 implement Option B runtime-guard at `src/ad/index_mapping.py:377` + `src/kkt/stationarity.py` per Day 0 binding patch shape.
3. #1385 Phase 0 verify: regenerate `srpchase_mcp.gms`; verify clean GAMS compile; iswnm/mexls/nebrazil/sarf translates pass. KU 3.2 ✅ VERIFIED.
4. **Priority 5 close:** combined fawley + otpop PR open. Per `PRIORITY_5_FIX_SURFACE.md` §8, run clearlak byte-stability check (zero diff expected per KU 5.3 LOW regression risk).
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 7):**
- [ ] #1390 PR open.
- [ ] #1385 srpchase translates cleanly; iswnm/mexls/nebrazil/sarf unblock.
- [ ] P5 combined PR open with clearlak byte-stability proof.
- [ ] KUs 3.2, 5.1, 5.2, 5.3 ✅ VERIFIED.

---

## Day 8 Prompt — #1385 PR + Priority 3 #1393+#1335 + Priority 7 #1387 start (~12h)

**Context:** Open #1385 PR. Implement #1393+#1335 otpop Approach C. Start Priority 7 #1387 cclinpts Phase 0.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §8 "Day 8"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_3_RISK_ASSESSMENT.md` §3.3 (#1393+#1335 Approach C binding)
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §3 (#1387 sign-flip + term-omission specs)

**Tasks:**

1. Open #1385 PR. Iterate first review round.
2. #1393+#1335 implement Approach C at `src/ad/derivative_rules.py:2607` per Day 0 binding shape (extend `_is_concrete_instance_of` to recognize symbolic supersets).
3. Phase 0 verify: regenerate `otpop_mcp.gms`; run NLP+MCP; verify `pi ≈ 4217.80` matches NLP. KU 3.3 ✅ VERIFIED.
4. **Priority 7 #1387 cclinpts start** — hand-derive expected `stat_b(j)` (sign-flip fix) + `stat_fb(j)` (missing 3 of 4 cross-terms) per `PRIORITY_7_FIX_SURFACE.md` §3.
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 8):**
- [ ] #1385 PR review iteration in flight.
- [ ] #1393+#1335 otpop solves with `pi ≈ 4217.80`.
- [ ] #1387 Phase 0 hand-derivation complete.
- [ ] KU 3.3 ✅ VERIFIED.

---

## Day 9 Prompt — Priority 3 close + Priority 4 #1378 launch numerics start (~10h)

**Context:** Close all Priority 3 PRs. Start Priority 4 launch numerics investigation.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §9 "Day 9"
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 4" (launch PATH-numerics investigation)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` Unknown 4.1 + 4.2 research questions

**Tasks:**

1. #1393+#1335 PR open + review iteration.
2. Merge any P3 PRs still open from Days 6–8.
3. **Priority 4 #1378 launch numerics:** investigate per `PROJECT_PLAN.md` Priority 4 — try (a) initial-point tuning, (b) `--nlp-presolve`, (c) NLP-warm-start, (d) sign/scaling refinement in `_apply_pattern_c_swap_to_term`. Pick the approach that produces MODEL STATUS 1 or `model_optimal_presolve` recovery with matching solution. KU 4.1 ✅ VERIFIED.
4. Verify launch byte-stability anchor preserved (KU 4.2 — does the Priority 4 fix shape constrain launch byte-stability?).
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 9):**
- [ ] All Priority 3 PRs merged or in final review.
- [ ] launch MODEL STATUS 1 or `model_optimal_presolve` with matching solution.
- [ ] KUs 3.4, 3.5, 4.1, 4.2 ✅ VERIFIED.

---

## Day 10 Prompt — Checkpoint 2: Pipeline Retest + Priority 4 close + Priority 7 #1387 implement (~10h)

**Context:** Mid-sprint Checkpoint 2 per PR6. Full pipeline retest. PR22 audit-script invocation. Close Priority 4. Implement Priority 7 #1387 cclinpts.

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
3. Author Day 10 SPRINT_LOG.md checkpoint entry. Expected: Solve ≥ 108 (P1+P2+P3+P5 firm gains); Match ≥ 63.
4. **Priority 4 close** — merge launch fix PR.
5. **Priority 7 #1387 implement** — apply sign-flip fix at `stationarity.py:1352/1835` + term-omission fix at `derivative_rules.py:1847` (`_diff_sum`) per `PRIORITY_7_FIX_SURFACE.md` §3.
6. EOD quality gate + SPRINT_LOG.md.

**Checkpoint 2 success criteria:**
- [ ] Solve ≥ 108. Match ≥ 63. path_syntax_error ≤ 10.
- [ ] PR22 output captures all P1+P2+P3+P5 artifacts.
- [ ] Priority 4 PR merged.
- [ ] #1387 sign-flip + term-omission patches committed.

---

## Day 11 Prompt — Priority 7 #1388 discriminator + #1387 close + Priority 6 #1224 start (~10h)

**Context:** Run the §4.6 3-way discriminator on #1388 camshape. Classify Case (a) / (b) / (c). Close #1387 PR. Start #1224 mine.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §11 "Day 11"
- `docs/planning/EPIC_4/SPRINT_27/PRIORITY_7_FIX_SURFACE.md` §4.6 (NLP-warm-start + 10-symbol display pre-check + 3-way discriminator)
- Day 0 KU 6.1 bundle decision for #1224

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
3. **#1387 PR close** — merge.
4. **Priority 6 #1224 start** — apply bundle-vs-standalone decision from Day 0 KU 6.1. If bundled with #1385: this is brought forward from Day 12 (Day 0 verified the index_mapping.py overlap). Implement per `PROJECT_PLAN.md` §"Priority 6".
5. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 11):**
- [ ] #1388 camshape classified per §4.6 3-way discriminator.
- [ ] #1388 fix landed (Case a/b) OR Sprint 28 carryforward filed (Case c).
- [ ] #1387 PR merged.
- [ ] KUs 7.1, 7.2, 7.3 ✅ VERIFIED.

---

## Day 12 Prompt — Priority 6 close + Priority 8 #1400 + Priority 9 #1374 (~10h)

**Context:** Close #1224. Fix the pipeline absolute-path leak (#1400). Audit + targeted fix for #1374 emit duplicate-init bugs.

**Read first:**
- `docs/planning/EPIC_4/SPRINT_27/PLAN.md` §12 "Day 12"
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §"Sprint 27" §"Priority 8" (#1400 corrected scope — `scripts/gamslib/run_full_test.py:899` `mcp_file_used` only; no `solve_mcp.py`)
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` Unknown 8.1, 8.2, 9.4

**Tasks:**

1. **#1224 mine close** — finish implementation + Phase 0 + PR. Document mine's next failure mode (KU 6.2): `path_syntax_error`, `model_infeasible`, `compare_match`, or other.
2. **Priority 8 #1400 fix** at `scripts/gamslib/run_full_test.py:899`. Choose KU 8.2 implementation: basename only (always `data/gamslib/mcp/<model>_mcp_presolve.gms`) OR `PROJECT_ROOT`-relative. Run the audit grep against a recent pipeline JSON: `grep -oE '"[^"]+": "/[^"]+"' data/gamslib/gamslib_status.json | sort -u`. If `mcp_file_used` is the only leak field, KU 8.1 ✅ VERIFIED at corrected scope.
3. **Priority 9 #1374 corpus sweep** — scan all 134 translating `*_mcp.gms` artifacts for duplicate `var.l(idx) = val` patterns. Document count + shapes in working notes. Apply targeted fix in `src/emit/` for the most common 1–2 shapes. Defer remaining to Sprint 28 per `PROJECT_PLAN.md` Priority 9. KU 9.4 ✅ VERIFIED.
4. EOD quality gate + SPRINT_LOG.md.

**Success criteria (Day 12):**
- [ ] #1224 mine PR merged.
- [ ] #1400 pipeline path leak fixed; `gamslib_status.json` produces byte-identical output across machines.
- [ ] #1374 audit complete; targeted fix landed for most common shapes.
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
