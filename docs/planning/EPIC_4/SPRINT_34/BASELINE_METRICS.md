# Sprint 34 — Day-0 Baseline Metrics + Genuine-Floor Re-Baseline

**Created:** 2026-07-18
**Prep Task:** 2 (Sprint 33 → Sprint 34 Day-0 Baseline + Genuine-Floor Re-Baseline)
**Day-0 code anchor:** `750803b2ee7472afe7443c395c02359b8f1ae3be` — the Sprint 33 close merge (PR #1581, `Merge pull request #1581 from jeffreyhorn/planning/sprint33-day13-close`)
**DB:** `data/gamslib/gamslib_status.json` (schema 2.2.1), md5 `6166acab90dcaff8789255f8ada83c54`

---

## 1. Summary

Sprint 34's Day-0 baseline **equals the Sprint 33 close** — recomputed from the committed DB, byte-for-byte reused (no fresh retest), because there is **no `src/`/`scripts/` drift** since the S33 close:

```
git diff --quiet 750803b2..HEAD -- src/ scripts/   →  clean (no drift)
```

| Metric (142 convex-candidate corpus) | Day-0 | Sprint 34 target |
|---|---|---|
| Parse | **142** | maintain 142 |
| Translate | **135** | maintain ≥ 135 (stretch +1 → 136 via #1385 sarf, P2) |
| Solve | **108** (64 cold + 44 presolve) | maintain 108 (stretch ≥ 110 via mine/fawley-forcing/bound-transfer/ganges) |
| Match (as-measured, 142) | **93** | maintain ≥ 93 |
| genuine floor (PR25) | **75** | ≥ 76 (mine [P1] / fawley [P3] cold-match) |
| model_infeasible | **7** | maintain ≤ 7 |
| path_syntax_error | **7** | maintain ≤ 7 |
| all-219 Match tally | **96** | (tracked; 93 candidates + 3 non-candidate) |
| Determinism | ✅ ×3 `{0,1,42}` | maintain |

**No change vs the Sprint 33 close** (the expected Day-0 state — the committed DB is the S33-close DB). Every Sprint-34 KPI delta is measured against this baseline and against the `--resolve-changed` code anchor `750803b2`.

> **Anchor note (differs from Sprint 33).** Unlike Sprint 33, the DB is **no longer byte-unchanged since `4cbf8bff`** — the S33 Day-11 P6 sample fix changed `sample_mcp.gms` + the DB (the DB's last modifying commit is `1568a531` "Sprint 33 Day 11 (P6): sample recovered"). `4cbf8bff` (the S31 close) is therefore **historical**; the Sprint-34 Day-0 code anchor for `--resolve-changed` is the **S33-close SHA `750803b2`**.

---

## 2. Day-0 anchor + provenance verification

- **Code anchor derivation** (portable, picks the close merge on `main`):
  ```bash
  S33=$(git log --first-parent main --grep='SPRINT 33 CLOSED' --format=%H -n 1)
  # → 750803b2ee7472afe7443c395c02359b8f1ae3be  (Merge pull request #1581 … planning/sprint33-day13-close)
  ```
- **Drift check:** `git diff --quiet 750803b2..HEAD -- src/ scripts/` → clean. Safe to reuse the committed DB with no fresh retest.
- **`--resolve-changed` at Day 0:**
  ```
  run_full_test.py --resolve-changed --since-commit 750803b2 --dry-run
  → GO: no emit goldens changed since 750803b2…
  ```
  0 changed goldens ⇒ the Day-0 tree matches the anchor.
- **Determinism ×3 `PYTHONHASHSEED` {0,1,42}** (byte-identical emit spot-check across the carryforward set):

  | Model | md5 (×3 seeds) | Verdict |
  |---|---|---|
  | mine (P1) | `a394cbc3dee15015aa099d7a84e0fa30` | byte-identical ✓ |
  | fawley (P3) | `d2eb48f11bdd2b6743151490ca993e6f` | byte-identical ✓ |
  | sample (P6, recovered) | `cf7d631f9a4fbde68528aa630a6bea40` | byte-identical ✓ |

  Consistent with the S33-close full-corpus determinism ✅ ×3 (blast radius from S33 = `sample_mcp.gms` only).

---

## 3. Day-0 bucket tally (142 convex candidates)

`get_candidate_models` = the 142 models with `convexity.status ∈ {verified_convex, likely_convex}` (142 of 219 total). Recomputed from the committed DB (`mcp_solve.outcome_category` + `solution_comparison.comparison_status`):

| Bucket | Count | Definition |
|---|---|---|
| Parse success | 142 | `nlp2mcp_parse.status = success` |
| Translate success | 135 | `nlp2mcp_translate.status = success` |
| **Solve success** | **108** | `mcp_solve.status = success` = 64 `model_optimal` (cold) + 44 `model_optimal_presolve` |
| **Match** | **93** | `solution_comparison.comparison_status = match` |
| model_infeasible | 7 | `outcome_category = model_infeasible` |
| path_syntax_error | 7 | `outcome_category = path_syntax_error` |
| path_solve_license | 9 | `outcome_category = path_solve_license` |
| path_solve_terminated | 4 | `outcome_category = path_solve_terminated` |
| non-translate (no solve) | 7 | `outcome_category = None` (never reached solve) |

### Bucket members (enumerated)

- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, `mine`, `rocket`
- **path_syntax_error (7):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `turkey`, `turkpow`
  *(the S33 8-member cohort minus `sample`, which recovered to Solve at the S33 close)*
- **non-candidate Match (all-219 minus the 142 corpus):** `ps2_f_s`, `ps2_s`, `ps3_s_gic` (3 → all-219 Match 96 = 93 candidate + 3 non-candidate)

---

## 4. Genuine-vs-methodology partition (PR25) — genuine floor 75

**Operational definition** (unchanged from PR25 / S32 / S33): the **methodology** set = `model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*) with the cold emit **byte-identical to its pre-fix state** — already-emit-correct models the broadened presolve-retry *validates*, not repeatable cross-term gains. The **genuine floor** = every other match: a cold match, OR a match whose cold emit a real fix *changed* (still genuine even if a non-convex model needs presolve to converge).

| Population | Count | Provenance |
|---|---|---|
| **Genuine, stable (floor)** | **75** | S33 Day-0 74 + the S33 P6 sample +1 (a genuine cold-emit correction: sample now cold-matches `model_optimal` @ 726.679, no longer `path_syntax_error`) |
| **Methodology-recovered** | **21** | `model_optimal_presolve` matches whose cold emit is byte-identical to pre-fix (incl. the CGE cluster `irscge`/`lrgcge`/`moncge`, cpack, himmel16, …) |
| **As-measured (all-219) Match** | **96** | 75 genuine + 21 methodology |

**Corroboration** — the all-219 Match (96) splits by `outcome_category` into **63 cold** (`model_optimal`) + **33 presolve** (`model_optimal_presolve`). Genuine floor 75 = 63 cold matches + 12 genuine-but-presolve-recovered; methodology 21 = the presolve-matches byte-identical to pre-fix (63 + 33 = 96 = 75 + 21). ✓

**Genuine floor = 75** is the Sprint-34 Day-0 anchor (the S33-close value; the ≥ 75 step was MET at the S33 close via the P6 sample cold-emit fix). It spans candidates **and** non-candidates, so it is not a 142-corpus-only count.

### Genuine-floor → ≥ 76 conversion map

Sprint-34 tracks that convert a `model_infeasible` candidate into a genuine cold match (+1 genuine floor each):

| Track | Day-0 bucket | +1 genuine floor if… |
|---|---|---|
| **mine** (P1 #1443) | `model_infeasible` (MS 5) | the head-offset dual-subsystem reconciliation cold-matches (infeasible → optimal) |
| **fawley** (P3 #1111/#1112) | `model_infeasible` (MS 5, LP 2899.25) | the constraint-index-diagonal `sameas` correction cold-matches — but fawley's +Solve is **H-b** (MS-5 persists), so the floor credit is contingent on the corrected cold emit counting under H-b (verified in Task 5, Unknown 3.3) |
| **camcge** (P5 #1330 → Epic 5) | `model_infeasible` (MS 4) | the dual-consistent Walras numéraire lands — **Epic-5-scoped, not an in-sprint mover** |

**Footnote-⁸ ramp alignment** (`PROJECT_PLAN.md` footnote ⁸, as renumbered by the Sprint-34 insertion): **S30 70 → S31 ≥ 73 → S32 actual 74 → S33 actual 75 → S34 ≥ 76 → S35 maintain ≥ 76 → S36 ≥ 77 → S37 ≥ 78.** Day-0 genuine floor **75** is the ramp's Sprint-34 anchor; Sprint 34 targets the **≥ 76** step, conditional on mine [P1] / fawley [P3] cold-matching. Per the Sprint-33 §3 lesson (borne out then beaten by P6): every deep KPI mover is a from-scratch AD/emit track that could REPLAN, so a **flat-75 close is the modal outcome** — but the P6 failure-cohort (ganges/gangesx) is a genuine bucket source, as S33's sample proved.

---

## 5. Per-carryforward-model provenance (Day-0 → expected Day-13)

| Model | Priority | conv | Day-0 bucket | MS | Expected Day-13 | Corpus |
|---|---|---|---|---|---|---|
| **mine** | P1 (Solve) | verified_convex | model_infeasible | 5 | MODEL STATUS 1 (+1 Solve, +1 genuine floor if cold-matches) OR H3 dual-architecture REPLAN | candidate |
| **sarf** | P2 (Translate) | verified_convex | non-translate (translate blow-up) | — | translate (+1 Translate → 136) OR timeout-re-trigger re-scoping | candidate |
| **fawley** | P3 (Solve/floor) | verified_convex | model_infeasible | 5 | genuine cold-emit correction (+1 genuine floor if it cold-matches); **+Solve is H-b** → forcing hand-off (P5) | candidate |
| **camcge** | P5 (Epic 5) | likely_convex | model_infeasible | 4 | stays model_infeasible (Epic-5-deferred; the dual-consistent Walras `/tmp`-to-MS-1 is the Epic-5 gate) | candidate |
| **rocket** | P5 (PATH) | likely_convex | model_infeasible | 5 | consultation input submitted (Sprint 35); +1 Solve conditional on forcing | candidate |
| **ganges** | P6 (failure-cohort) | likely_convex | path_syntax_error | — | translate-syntax diagnosis (`$141/$145/$149` root, distinct from sample's `$140`); +1 Solve if recovered | candidate |
| **gangesx** | P6 (failure-cohort) | likely_convex | path_syntax_error | — | same `$141/$145/$149` root as ganges (a single fix may recover both) | candidate |
| **agreste** | P6 (re-triage) | verified_convex | model_infeasible | 5 | scope-verify the double-`solve` scenario driver before treating CASE_B `stat_sales` as an emit bug | candidate |
| **sample** | P6 (RECOVERED S33) | likely_convex | **model_optimal (match, MS 1 @ 726.679)** | 1 | stays matched (the S33 genuine cold-emit fix; guarded by `test_sample_pruned_var_l_init.py`) | candidate |

**P4 (max-convention bound-transfer-sign track) — MAXIMIZE cohort:** the two Sprint-33 discovery cells are **fawley** (`bq.m < 0` at a lower bound) and **mine** (upper-bound multipliers). The full MAXIMIZE-cohort enumeration (the +Solve candidates vs the presolve-match regression-risk set) is **Task 6's** deliverable (Unknown 4.2); at Day 0 the track is a general warm-start-transfer gap, not yet a scoped cohort.

---

## 6. Known Unknowns verified by this task

- **Unknown 7.2 (primary)** — ✅ the Day-0 baseline = the S33 close (Solve 108 / Match 93 / genuine floor 75 / mi 7 / path_syntax_error 7 / Translate 135 / all-219 96); the PR25 anchor is **75** (not 74); the Day-0 code anchor is the **S33-close SHA `750803b2`** (`4cbf8bff` superseded by the S33 sample DB change, last DB commit `1568a531`).
- **Unknown 1.1 (Day-0-bucket aspect)** — ✅ mine is `model_infeasible` (MS 5) at Day 0, a candidate; the *fix-surface / value-invariance* aspect is verified by Task 3.
- **Unknown 3.1 (Day-0-bucket aspect)** — ✅ fawley is `model_infeasible` (MS 5, LP opt 2899.25) at Day 0, a candidate; the *constraint-index-diagonal correction* aspect is verified by Task 5.

---

**Document Status:** ✅ Complete — Sprint 34 Prep Task 2
**Last Updated:** 2026-07-18
**Owner:** Sprint 34 Planning Team
