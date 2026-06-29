# Sprint 29 Detailed Schedule (Day 0 + Days 1–13)

**Sprint:** 29 (Weeks 23–24 — Sprint 28 carryforwards + cold-convex robustness + AD/KKT backlog + Epic-5 scoping)
**Budget:** ≤ 12 h/day × 14 days = 168 h cap; estimated work ~96–134 h (per the §14 budget table — the lower bound assumes the REPLAN-prone tracks P1 #1443 + P2 #1462-residual + P7 #1111/#1112 partially slip to Sprint 30).
**Risk:** HIGH (three REPLAN-prone diagnosis tracks; the Sprint 24–28 pattern is that deep AD/non-convex/presolve fixes prove multi-bug).
**Authored:** Sprint 29 Prep Task 10, integrating prep Tasks 1–9.

---

## 1. Sprint 29 Goal

Land the Sprint 28 Solve/Match carryforwards the Day-13 retest deferred (#1443 mine, #1462 rocket, #1385) and attack the **cold-convex robustness** gap the retrospective surfaced (the 21 Case-b cold-emit bugs from the Task-3 survey), produce the camcge → Epic 5 scoping observation, clear the AD/KKT cross-term backlog (#1447 maxmin, the objective-mismatch cohort, the offset-alias gradient #1146/#1143), and wire the checkpoint re-solve + re-baseline infra. Targets: **Solve 107 → ≥ 109** (firm via mine + rocket, **both REPLAN-gated**); **Match maintain ≥ 92 / stretch ≥ 96**; **model_infeasible 7 → ≤ 5**; **Translate ≥ 135**; **Tests ~4,935 → ≥ 4,960**. See `PROJECT_PLAN.md` §"Sprint 29".

> **Re-baseline floor (PR25, Task 2):** the as-measured Match 92 = **genuine 68 + ~24 methodology**. Sprint 29's genuine-floor target is **68**; the cold-convex Case-b work (P4/P7) is **Match-neutral cold-robustness** that *raises the genuine floor* (68 → up to ~89) without moving the as-measured 92. Only mine (#1443) + rocket (#1462) + hhfair (#1236) are headline-moving. Track genuine vs methodology separately at every checkpoint.

## 2. Acceptance Criteria (from `PROJECT_PLAN.md` §"Sprint 29")

- **Solve** ≥ 109 (= 107 + mine #1443 + rocket #1462 — **both firm only if Case b PROCEED**; REPLAN-gated per Task 5, so ≥ 109 is at-risk and the lower bound is 107–108).
- **Match** maintain ≥ 92 (the re-baselined Rolling-KPI floor); the **genuine floor** rises 68 → ~89 via the cold-convex Case-b work, but per §1 that is **Match-neutral on the as-measured KPI** (the Case-b models already match warm), so it lifts the genuine floor, **not** the as-measured 92. **Stretch ≥ 96** is the `PROJECT_PLAN` target, but the only as-measured headline-movers are rocket (+1) + hhfair (+1, if Case b) → 94; reaching 96 needs additional genuine `mismatch → match` conversions beyond the scoped set (or a methodology change) — the cold-only recoveries do **not** count toward the as-measured KPI under the current methodology.
- **model_infeasible** ≤ 5 (-2 via mine + rocket; camcge stays infeasible → Epic 5).
- **Translate** ≥ 135 (maintain; +Translate if a #1385 timeout target recovers); **Parse** ≥ 142.
- **Tests** ≥ 4,960; **Determinism** byte-identical under 3× `PYTHONHASHSEED` (PR12).
- **Infra:** the checkpoint `--resolve-changed` re-solve + the PR25 re-baseline step land (Priority 8); the offset-alias property-test fixtures (`shape7`/`shape8`) guard the P7 fix.
- **Quality:** all gates pass; fixes carry regression tests; emit-touching PRs include regenerated `.gms` diffs (PR14) and pass golden-staleness (PR26) + the new `--resolve-changed` checkpoint.

## 3. Sequencing Constraints (from the prep-task outputs)

- **Tooling already built (Task 6 audit):** the KKT-residual harness, the divergence detector, and the golden-staleness gate all cover the Sprint-29 classes with **no Day-0 extension** — so, unlike Sprint 28, there is **no harness-build front-load**; diagnosis starts Day 0.
- **Day-0 traces (PR24, Task 4):** every Phase-0 gate already carries a Day-0 harness verdict; Day 0 confirms + fills the `Traced Fix-Surface (Day-0)` `file:line` before any `src/`.
- **REPLAN gates (Task 5):** #1443 mine (convex ⇒ no Case-c; the pivot is single-site vs distributed multi-site re-derivation — **lean REPLAN-aware**), #1462 rocket-residual (the `_fx_` warm-start lands either way as presolve robustness; only the +1 Solve/Match is at risk on intrinsic non-convergence — **lean REPLAN-aware**), #1111/#1112 offset-alias (single-row integer residual ⇒ **lean PROCEED**; REPLAN only if it threads the alias-AD core). Each carries an explicit Sprint-30 exit + budget reallocation.
- **Cold-convex partition (Task 3):** 21 Case-b / 4 Case-c / 3 Case-a / 2 inconclusive. The **Class-A shared "objective/defining cross-term" fix** (one `stationarity.py` correction) plausibly lands maxmin + himmel16 + like + catmix + polygon (~6–8); the **Class-B CGE family** (irscge/lrgcge/moncge/stdcge/marco) is gated to the camcge/Epic-5 family; the 2 inconclusive (paperco/weapons) need a harness-trace before counting. **Match-neutral** (genuine-floor lift).
- **P4 ⊃ P7 overlap:** himmel16 (#1146) + polygon (#1143) are **both** cold-convex Class-A leads **and** the P7 offset-alias pair — the same `_partial_collapse_sum`/`_diff_varref` fix lands them in both buckets (Task 9). Schedule them once.
- **P6 collapses to hhfair (Task 9):** quocge → Epic 5 (CGE numéraire), prolog resolved, sambal/qsambal Match-neutral (consolidate via #1112); **hhfair (#1236) is the only live +Match** — gated on first fixing its residual-emit compile (`$141`/`$257`).
- **camcge → Epic 5 (Task 7):** Priority 5 is a **write-up only, no `src/`** (the scoping doc is pre-drafted).
- **Re-baseline (Task 8):** after any retry-trigger / comparison-logic / scope change, recompute the genuine-vs-methodology split; report headline deltas attributable.

---

## 4. Day 0 — Kickoff + Day-0 Traces (≤ 6 h)

- Confirm the Day-0 baseline = Sprint 28 final (`BASELINE_METRICS.md`; the committed DB recomputes to Solve 107 / Match 92 / model_infeasible 7). **Verify** `git diff 803a259a..HEAD -- src/ scripts/` is empty before skipping the retest (expected empty per Unknown 8.3); if non-empty, run a fresh retest.
- **Day-0 traces (PR24)** for the REPLAN-prone + lead tracks: mine (#1443, 3-site head-offset), rocket (#1462, `_fx_`-at-`h0`), the cold-convex Class-A leads (maxmin/himmel16/like/catmix/polygon), and hhfair (#1236 — first reproduce the `$141`/`$257` residual-emit-compile blocker). Instrument the candidate surfaces, emit each `<model>_mcp.gms`, locate the offending row, and **fill the `Traced Fix-Surface (Day-0)` `file:line`** in each Phase-0 gate.
- **PR25 Day-0 tally + re-baseline floor:** restate genuine 68 / methodology ~24; firm headline path = mine + rocket (REPLAN-gated).
- **Est:** ~6 h (lighter than Sprint 28 — the harness already exists). **Risk:** the prep-doc surfaces are hypotheses (Sprint 27: 4× wrong) — the traces are why Day 0 exists.

## 5. Days 1–2 — Priority 2: #1462 rocket — `_fx_`-multiplier warm-start + residual (front-loaded) (~8–14 h)

- **Front-loaded because the root cause is known** (Task 5 Track B). **Day 1:** land the general `nu_<var>_fx_<idx>.l = <var>.m(<idx>)` `_fx_`-multiplier warm-start in the presolve emit — **sprint-wide presolve robustness, firm regardless of rocket** — and verify **zero regression** across the Layer-4-unfix set (`grep -l "#1449 (Layer 4)" data/gamslib/mcp/*_mcp_presolve.gms` → otpop/chain/cclinpts/rocket) + the full presolve golden set.
- **Day 2 (REPLAN-gated, Unknown 2.2):** complete the `_fx_`-at-`h0` warm-start for all of ht/v/m + the degenerate-bound suppression probe. **PROCEED** if rocket → MS 1 / `compare_objective_match` (**+1 Solve / +1 Match**); **REPLAN to Sprint 30 forcing** if MS-5 persists with a clean residual (intrinsic non-convergence). REPLAN frees ~4–8h → Priority-6 hhfair.
- **Verifies:** 2.1, 2.2, 2.3. **REPLAN exit explicit.**

## 6. Days 3–4 — Priority 4 + Priority 7: cold-convex Class-A + offset-alias shared fix (~10–14 h)

- **The single highest-ROI work (Task 3 §8):** one `src/kkt/stationarity.py` (+ `src/ad/derivative_rules.py` `_partial_collapse_sum`/`_diff_varref`) correction of the **objective/defining-variable cross-term** plausibly lands the Class-A leads — maxmin (`stat_mindist` 1.0, #1447), himmel16 (`stat_area` 2.0, #1146), polygon (`stat_theta` 0.49, #1143), like (`stat_p` 2.0), catmix (`stat_x1` 0.95). **This is both the P4 Class-A fix and the P7 offset-alias fix** (himmel16/polygon are the intersection).
- **Property-test fixtures (Task 9):** add `tests/fixtures/crossterm_shapes/shape7_offset_alias_cyclic.gms` (himmel16 `i++1`) + `tests/fixtures/crossterm_shapes/shape8_offset_alias_successor.gms` (polygon `ord(j)=ord(i)+1`) to `tests/integration/emit/test_ad_crossterm_shapes.py` to guard the fix.
- **Match-neutral (Task 3 §3b):** these already match warm — the gain is **genuine-floor lift** (68 → up to ~73+) + cold robustness, *not* headline Match. Harness Case-a (residual → 0) on each is the acceptance.
- **REPLAN-gated (Unknown 7.2):** PROCEED if the fix gates to the cyclic/successor shape without threading the #1111/#1112 core; else REPLAN the architecture track to Sprint 30. **Per-day:** Day 3 — the shared cross-term fix + maxmin/himmel16/polygon; Day 4 — like/catmix + the two fixtures + full-corpus byte-stability/re-solve + PR.
- **Verifies:** 4.1, 4.2, 7.1, 7.2, 7.3.

## 7. Day 5 — Checkpoint 1 + Priority 4 Class-C (model-specific) (~10 h)

- **Checkpoint 1 (Task 8):** the new `--resolve-changed --since-commit <Day-0 SHA>` re-solve of the changed-golden set + golden-staleness + the **PR25 tally with the re-baseline step** (recompute genuine/methodology if any methodology change landed). GO/NO-GO: any changed-golden model regressed → investigate.
- **P4 Class-C (model-specific cold-emit bugs, as budget allows):** the large-residual standalone Case-b models — tforss (`stat_v` 2052), markov (`stat_z` 13), robert (`stat_x` 7.2), harker (`stat_s` 2.16) — each a per-model `stat_*` fix (Match-neutral genuine-floor). Take the cheapest-localizable first; this is REPLAN-slack-absorbing fill.
- **Verifies:** 4.1 (continued). **Re-baseline check explicit.**

## 8. Days 6–7 — Priority 1: #1443 mine — head-domain-offset (REPLAN-gated) (~10–16 h)

- **Task-5 gate (Unknown 1.1): lean REPLAN-aware.** mine is a **convex LP** (monotone LCP — no Case-c escape), so the pivot is **single-site vs distributed multi-site re-derivation**, not Case-b-vs-Case-c. **Day 6:** map the cold-INFES by row-type (49 INFES across `comp_pr`/`comp_lo_x`/`comp_up_x`/`stat_x`/`def`); apply the coordinated 3-site head-offset index map — (1) `comp_pr` emission, (2) the `--nlp-presolve` dual transfer (`src/emit/emit_gams.py` `_emit_nlp_presolve` ~line 1281, `lam_<eq>.l = abs(<eq>.m)`), (3) the landed `stat_x` cross-term.
- **Day 7:** if the coordinated fix drives the cold LCP to MS 1 → **+1 Solve firm (genuine)**, PR; **REPLAN to Sprint 30** (head-domain-offset emit-architecture workstream) if the INFES stays distributed or each site only exposes the next. Prior leans REPLAN (Day-4 evidence: 22/30 `stat_x` systemic, no single-tweak fix). REPLAN frees ~10–16h → Priority-4 Case-b.
- **Verifies:** 1.1, 1.2, 1.3. **REPLAN exit explicit.**

## 9. Day 8 — Priority 6: #1236 hhfair (the only live +Match) (~10 h)

- **hhfair is the only live P6 +Match (Task 9):** **first** fix the residual-emit-compile blocker (the harness `$141`/`$257` from the domain-widened `n(tl)` / `n(0)=0` fixup), **then** read the harness verdict on the CES/`prod` `stat_*` rows. **PROCEED** if Case b on a CES/product row → fix the log-derivative product gradient + CES chain-rule (**+1 Match**); **REPLAN to Sprint 30** if Case c (non-convex `prod`/CES nest).
- **sambal/qsambal #1112 consolidation check (Unknown 6.2):** confirm whether the `$xw(i,j)` dollar-condition fix overlaps the offset-alias #1112 work (a side-effect Match-neutral resolution).
- **Verifies:** 6.1, 6.2, 6.3 (reconfirmed). quocge/prolog/sambal/qsambal carry **no +Match** (Epic 5 / resolved / Match-neutral).

## 10. Days 9–10 — Priority 3: #1385 translation-timeout cross-terms + Checkpoint 2 (~10–16 h)

- **#1385 (Task 4 structural gate):** pick the smallest viable timeout target (iswnm/sarf/mexls/nebrazil — Unknown 3.2 emit-size probe), then land the **atomic** runtime-guard equation-body re-emit + the `J_gᵀ·lam` cross-terms (a re-emit without cross-terms = an inconsistent MCP — Unknown 3.1). **Target:** the smallest target → translate-success (**+Translate ≥ 1**). No quoted-set-name multiplier indices (the Day-4 `nu_slack("srn")` bug).
- **Day 10 = Checkpoint 2 (Task 8):** `--resolve-changed` + golden-staleness + PR25 re-baseline tally.
- **Per-day:** Day 9 — smallest-target select + hand-derive + implement the atomic re-emit + cross-terms; Day 10 — Checkpoint 2 + close #1385 (or re-defer the cross-term half if intractable).
- **Verifies:** 3.1, 3.2, 3.3.

## 11. Day 11 — Priority 5: camcge → Epic 5 write-up (no `src/`) + Priority 8 infra build (~10 h)

- **P5 camcge (Task 7, no `src/`):** finalize `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (the scoping doc is pre-drafted) — confirm #1330 → Epic 5, no Sprint-29 `src/`. ~3 h.
- **P8 infra build (Task 8 design):** build the checkpoint `--resolve-changed` mode (`run_full_test.py`: re-solve the `changed_emit_artifacts.py` set, bucket-diff vs the committed DB, GO/NO-GO) + the PR25 re-baseline step in the projection template. ~7 h. **Verifies:** 8.1, 8.2, 8.4.

## 12. Day 12 — Priority 4 Class-B / inconclusive + REPLAN-slack absorption (~10 h)

- **P4 Class-B CGE family (gated):** harness-trace irscge/lrgcge/moncge/stdcge/marco (`stat_pz`≈1.0) — confirm whether they are the camcge Walras family (→ Epic 5, no fix) or a localizable cross-term; do **not** count as Sprint-29 wins without the trace.
- **The 2 inconclusive (paperco dual-transfer, weapons harness-abort):** re-trace to disposition.
- **REPLAN-slack absorption:** if mine (#1443) and/or rocket (#1462) REPLAN'd, their freed ~14–24 h pre-allocates here (more Class-C cold-convex genuine-floor conversions + the P6 sambal/qsambal #1112 side-effect).
- **Verifies:** 4.3 (Class-B disposition).

## 13. Day 13 — Final Retest + Closeout (~8 h, tight)

- **Final 3× `PYTHONHASHSEED` retest** (PR12 determinism guard) over the full 142-model pipeline + golden-staleness + the `--resolve-changed` check.
- **PR25 final projection tally + re-baseline:** realized Solve/Match vs target, each delta labeled genuine vs methodology; record the new genuine floor.
- `SPRINT_LOG.md` final entry + `SPRINT_RETROSPECTIVE.md` + Sprint 30 carryforward filings for any REPLAN'd track (#1443 / #1462-residual / #1111-#1112 / camcge-Epic-5 as applicable).

---

## 14. Budget Summary

| Day(s) | Work | Est (h) |
|---|---|---|
| 0 | Kickoff + Day-0 traces | ~6 |
| 1–2 | P2 #1462 rocket `_fx_` warm-start + residual (REPLAN-gated) | ~12 |
| 3–4 | P4+P7 cold-convex Class-A + offset-alias shared fix + fixtures | ~12 |
| 5 | Checkpoint 1 + P4 Class-C (model-specific) | ~10 |
| 6–7 | P1 #1443 mine head-domain-offset (REPLAN-gated) | ~14 |
| 8 | P6 #1236 hhfair (the only live +Match) | ~10 |
| 9–10 | P3 #1385 timeout cross-terms + Checkpoint 2 | ~13 |
| 11 | P5 camcge Epic-5 write-up (no `src/`) + P8 infra build | ~10 |
| 12 | P4 Class-B/inconclusive + REPLAN-slack | ~10 |
| 13 | Final retest + closeout | ~8 |
| **Total** | | **~105 h** (mid-estimate; ~96 h lower if P1/P2 REPLAN early, ~134 h upper if all PROCEED) |

**Fits the 168 h cap** with ≥ 34 h slack at the mid-estimate; **no day > 12 h** (heaviest ~10 h). The lower bound assumes the REPLAN-prone tracks (P1 #1443, P2 #1462-residual, P7 #1111/#1112) partially slip per Task 5 (~30–48 h at-risk; the firm parts — rocket presolve robustness + the cold-convex genuine-floor + P8 infra — land regardless).

## 15. Phase 0 Coverage Audit (PR20 + PR24)

All 10 implementation tracks have a Phase-0 gate authored in prep (Task 4): `docs/issues/ISSUE_{1443,1462,1385,1447,1332,1247,1239,1236,1146,1143}_*.md`. Each gate's `Traced Fix-Surface (Day-0)` line is filled on Day 0 before any `src/`. (camcge #1330 has its gate but is Epic-5 write-up only; quocge/prolog are NO-OP gates — already-banked/resolved.)

## 16. Known Unknowns Status Snapshot + In-Sprint VERIFICATION Day

All **28 prep unknowns are VERIFIED** (prep Tasks 1–9); none remain INCOMPLETE at Day 0. The in-sprint days re-confirm the fix-surface hypotheses against the live traces (PR24) and pin the REPLAN PROCEED/REPLAN decisions:

| Unknowns | Owning priority | CONFIRM/decide day |
|---|---|---|
| 1.1, 1.2, 1.3 | P1 mine (REPLAN) | Days 6–7 |
| 2.1, 2.2, 2.3 | P2 rocket (REPLAN) | Days 1–2 |
| 3.1, 3.2, 3.3 | P3 #1385 | Days 9–10 |
| 4.1, 4.2, 4.3 | P4 cold-convex | Days 3–5, 12 |
| 5.1, 5.2, 5.3 | P5 camcge → Epic 5 | Day 11 (no `src/`) |
| 6.1, 6.2, 6.3 | P6 hhfair | Day 8 |
| 7.1, 7.2, 7.3, 7.4 | P7 offset-alias (REPLAN) | Days 3–4 |
| 8.1, 8.2, 8.3, 8.4 | P8 infra + baseline | Day 0 (baseline) + Day 11 (build) |

## 17. Risk Register + Mitigations

| Risk | Mitigation |
|---|---|
| Prep-doc fix surface wrong (Sprint 27: 4×) | PR24 Day-0 traces (§4); Phase-0 PROCEED cites the *traced* surface |
| REPLAN-prone track is architectural / non-convex (mine, rocket, P7) | Task-5 REPLAN gates (§5/§6/§8) with explicit Sprint-30 exits + budget reallocation — a slip is planned |
| Cold-convex Case-b mistaken for headline +Match | PR25 re-baseline (§7/§13): the 21 Case-b are Match-neutral genuine-floor, tracked separately from as-measured Match |
| Broken solve hides behind a byte-stable golden (the rocket #1462 lesson) | the `--resolve-changed` checkpoint re-solve at Day 5/Day 10 (Task 8) surfaces it mid-sprint |
| Methodology change silently inflates Match (Day-9 lesson) | the PR25 re-baseline step at every checkpoint (Task 8) |
| Day over-pack (Sprint 27 Day-12 lesson) | No day > 12 h (heaviest ~10 h); P4 Class-C / Class-B are slack-absorbing fill, not commitments |
| Stale forward-looking prompts (Sprint 27) | PLAN_PROMPTS.md states only the day's scope; no claim about not-yet-done work |

## 18. Prep-Task → PR Mapping

| Prep task | Deliverable | PR |
|---|---|---|
| (insert) | PROJECT_PLAN Sprint 29 | #1464 |
| 1 | KNOWN_UNKNOWNS + PREP_PLAN + prompts | #1465 |
| 2 | BASELINE_METRICS (genuine/methodology) | #1466 |
| 3 | COLD_CONVEX_COHORT_SURVEY (21 Case-b) | #1467 |
| 4 | Phase-0 gates (10 tracks) + ISSUE_1462 | #1468 |
| 5 | REPLAN_RISK_ASSESSMENT (3 tracks) | #1469 |
| 6 | TOOLING_READINESS_AUDIT | #1470 |
| 7 | EPIC_5/CGE_DEGENERACY_SCOPING | #1471 |
| 8 | PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN | #1472 |
| 9 | BACKLOG_FIX_SURFACE_ANALYSIS | #1473 |
| 10 | PLAN + PLAN_PROMPTS (this) | #1474 |

## 19. Related Documents

- `PREP_PLAN.md`, `KNOWN_UNKNOWNS.md`, `BASELINE_METRICS.md` (Task 2), `COLD_CONVEX_COHORT_SURVEY.md` (Task 3)
- `REPLAN_RISK_ASSESSMENT.md` (Task 5), `TOOLING_READINESS_AUDIT.md` (Task 6), `docs/planning/EPIC_5/CGE_DEGENERACY_SCOPING.md` (Task 7)
- `PRIORITY_8_CHECKPOINT_RESOLVE_DESIGN.md` (Task 8), `BACKLOG_FIX_SURFACE_ANALYSIS.md` (Task 9)
- The 10 Phase-0 gates: `docs/issues/ISSUE_{1443,1462,1385,1447,1332,1247,1239,1236,1146,1143}_*.md` (Task 4)
- `CONTRIBUTING.md` §"Phase 0 Acceptance Gates" + §"Projection Discipline" (PR24/PR25)
- `prompts/PLAN_PROMPTS.md` (per-day execution prompts)
