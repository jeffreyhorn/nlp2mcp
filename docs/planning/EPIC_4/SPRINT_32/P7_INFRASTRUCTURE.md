# Sprint 32 Day 12 — P7 Infrastructure (property fixtures · genuine-floor tracking · checkpoint · Epic-4 SUMMARY)

**Date:** 2026-07-15
**Day:** 12 (Priority 7 — infrastructure + REPLAN-slack)
**Outcome:** ✅ Infrastructure right-sized to what landed; genuine-floor tracking recomputed (floor **74**, S32 ≥ 75 **MISSED**); the Epic-4 `SUMMARY.md` skeleton begun. Docs-only (no `src/`; no new fixtures needed).

---

## 1. Property-catalog fixtures — deferred with P1/P2 (add only for tracks that landed)

The planned **shape12** (head-offset 4th-site bound-multiplier — guards the P1 emit) and **shape13** (sarf 4-D `task` sparsification — guards the P2 emit) were contingent on **P1 (mine)** and **P2 (sarf)** landing. **Both REPLAN'd** (mine Day 1, 5th coupling; sarf Day 6, symbolic-emit re-scope) — the emit paths they would guard **do not exist**. Per the Day-12 gate ("add only for tracks that landed"), **shape12 + shape13 are NOT added**; they defer to Sprint 33 alongside the tracks they guard. The `test_ad_crossterm_shapes.py` catalog stays at **shapes 1–11**.

**What DID land is already guarded** (no new catalog fixtures needed):

| Landed this sprint | Guarding tests | Where |
|---|---|---|
| camcge P3 step-1 — scalar-`fx` marginal warm-start transfer + the symmetric unfix (`emit_gams.py`) | `test_fx_warmstart_emitted_for_scalar_fixed_variable`, `test_fx_unfix_emitted_for_scalar_fixed_variable` | `tests/unit/emit/test_presolve_fx_warmstart.py` (Day 4) |
| P5 — objective-defining-intermediate-variable Case-c classifier (`kkt_residual.py`) | `TestObjdefCaseCClassifier` (9 tests: `_var_from_stat_label`, `_cold_is_spurious`, `_is_objdef_intermediate_var`, the D1∧D3 reclassification + guards) | `tests/unit/diagnostics/test_kkt_residual_harness.py` (Day 10) |

## 2. Genuine-floor tracking recompute (PR25, footnote-⁸ ramp)

Recomputed from the committed DB (`get_candidate_models`, 142-corpus) — **byte-unchanged since `4cbf8bff`** (`git diff 4cbf8bff..HEAD -- data/gamslib/gamslib_status.json data/gamslib/mcp/` is empty; the only `src/` emit change, camcge step-1 in `emit_gams.py`, changed **no golden** — camcge has no committed presolve golden):

| KPI | Day-0 (S31 final) | S32 Day-12 | S32 target (footnote ⁸) |
|---|---|---|---|
| Parse | 142 | **142** | 142 |
| Translate | 135 | **135** | ≥ 135 (+1 via sarf) — **MISSED** (sarf REPLAN'd) |
| Solve | 107 | **107** | ≥ 109 (+2 mine+camcge) — **MISSED** (both REPLAN'd) |
| Match (142-corpus) | 92 | **92** | maintain ≥ 92 — ✅ |
| **Genuine floor** | **74** | **74** | **≥ 75 — MISSED** |
| model_infeasible | 7 | **7** | ≤ 5 — **MISSED** |

**The S32 ≥ 75 genuine-floor step is MISSED (floor holds at 74).** Per the Sprint-30 §3 / Sprint-31 §3 conditionality lesson, the ramp advances only via an emit-changing cold-match — the S32 movers were mine [P1] + camcge [P3] cold-matching **or** a P6 emit gain; **all REPLAN'd or re-triaged**, so no genuine cold-match landed. camcge step-1 is a genuine **emit-correctness** fix (`stat_mps` → Case-a) but does **not** make camcge solve/cold-match (it needs step-2 Walras, Epic-5-deferred), so it moves no bucket.

**Footnote-⁸ ramp update (for the PROJECT_PLAN, S33+):** the genuine-floor ramp anchor is **74 at S32 close** (not the projected ≥ 75). The S33 target should re-baseline to **maintain ≥ 74** with the S32-banked emit fixes (fawley qsb/pbal sameas, the #1111/#1112 second-index generalization) as the next genuine-floor levers, not carry the missed ≥ 75.

## 3. `--resolve-changed` checkpoint refresh

The Day-0 anchor **`4cbf8bff`** remains valid: `.venv/bin/python scripts/gamslib/run_full_test.py --resolve-changed --since-commit 4cbf8bff --dry-run` = **GO (0 emit goldens changed)**. The only emit-touching landing (camcge step-1) changed **no committed golden** (camcge is `model_infeasible`, no presolve golden). So there is **no new checkpoint target** to add this sprint — the anchor + the golden-staleness gate already cover the Sprint-32 emit surface. When the Sprint-33 fawley/#1111-#1112 fix lands and changes `fawley_mcp*.gms`, `--resolve-changed --since-commit 4cbf8bff` will select it automatically.

## 4. Epic-4 `SUMMARY.md` skeleton (S30-retro §5 front-loading)

Authored `docs/planning/EPIC_4/SUMMARY.md` — the sprint-by-sprint groundwork (one row per Sprint 18–35, headline KPI deltas + the firm landing + the REPLAN'd carryforwards), to fill in at Epic-4 close. Seeded from the closed-sprint record (S27 Match 62 → … → S31/S32 Match 92 / genuine floor 74) + the PROJECT_PLAN forward plan (S33–S35).

## 5. Disposition

- **No `src/` change; no new test fixtures** (shape12/shape13 deferred with P1/P2; what landed is already guarded). **REPLAN-slack absorbed:** the freed mine/camcge/sarf/P6 budget flowed to P7 (this infrastructure + the banked-diagnosis write-ups) — the durable leverage that always lands.
- **Genuine floor 74** (S32 ≥ 75 missed); the footnote-⁸ ramp re-baselines to the honest 74 anchor. Checkpoint anchor `4cbf8bff` stands. The Epic-4 `SUMMARY.md` skeleton is begun.

---

**Document Created:** 2026-07-15
**Owner:** Sprint 32 execution
