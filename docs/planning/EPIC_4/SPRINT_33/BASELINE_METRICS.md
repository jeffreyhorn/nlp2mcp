# Sprint 33 — Day-0 Baseline Metrics

**Created:** 2026-07-16
**Purpose:** Establish the authoritative Sprint 33 Day-0 baseline (per-model bucket provenance) + reproduce the PR25 genuine-vs-methodology partition, so every Sprint-33 KPI delta is measured against a clean starting line (PR15 + PR17 + PR25).
**Prep Task:** 2 — verifies Unknowns 1.1 (Day-0 mine bucket), 3.1 (Day-0 fawley bucket), 7.2 (the genuine-floor anchor 74).

---

## 1. Day-0 anchor & drift check

| Anchor | Value |
|---|---|
| **Sprint 32 close SHA** | `ee51ed9e` (`Sprint 32 Day 13: Final retest + closeout — SPRINT 32 CLOSED`) |
| **DB byte-anchor** | `4cbf8bff` (Sprint 31 close) — the committed `gamslib_status.json` is **byte-unchanged since** `4cbf8bff` (md5 `a92b040924d20d693699d1861972780c`) |
| **src/scripts drift since S32 close** | **none** (`git diff --quiet ee51ed9e..HEAD -- src/ scripts/` empty — only docs landed via PR #1561/#1562) → **reuse the committed DB, no fresh ~4h retest** |
| **`--resolve-changed` checkpoint** | `--since-commit ee51ed9e --dry-run` → **GO: no emit goldens changed since ee51ed9e** (0 changed at Day 0) |
| **Determinism** | ✅ ×3 — mine emit byte-identical across `PYTHONHASHSEED` {0,1,42} (`ab4780e1cba94e409e7cb14d5eb20231`); re-affirms the S32-close ×3 result (no `src/` change ⇒ holds by construction) |

**Day-0 = Sprint 32 close.** The DB is reused as-is (no drift, no retest).

## 2. Outcome vs targets (Sprint 33)

| Metric (142 convex-candidate corpus) | Day-0 | Sprint 33 target |
|---|---|---|
| Parse | **142** | maintain ≥ 142 |
| Translate | **135** | +1 → 136 (via #1385 sarf [P2]) |
| Solve | **107** | ≥ 108 (stretch ≥ 109 / ≥ 110) |
| Match (as-measured) | **92** | maintain ≥ 92 |
| genuine floor | **74** | ≥ 75 (mine [P1] / fawley [P3] cold-matches) |
| model_infeasible | **7** | maintain ≤ 7 (−1 per mine / fawley / camcge recovery) |
| path_syntax_error | **8** | maintain ≤ 8 |
| path_solve_terminated | **4** | maintain ≤ 5 |
| Tests | **5,085** | ≥ 5,085 |
| all-219 Match tally | **95** | (tracked; 92 candidates + 3 non-candidate) |

## 3. Day-0 bucket tally (142 convex candidates)

`get_candidate_models` = the 142 models with `convexity.status ∈ {verified_convex, likely_convex}` (verified: 142 candidates out of 219 total). Recomputed from the committed DB:

| Bucket | Count | Derivation |
|---|---|---|
| Parse success | **142** | `nlp2mcp_parse.status = success` |
| Translate success | **135** | `nlp2mcp_translate.status = success` (7 non-translate) |
| **Solve** | **107** | 63 `model_optimal` (cold) + 44 `model_optimal_presolve` |
| **Match** (as-measured) | **92** | `solution_comparison.comparison_status = match` |
| model_infeasible | **7** | `mcp_solve.outcome_category = model_infeasible` |
| path_syntax_error | **8** | |
| path_solve_license | **9** | |
| path_solve_terminated | **4** | |
| non-translate | **7** | (no `mcp_solve`) |

Total: 63 + 44 + 9 + 8 + 7 + 7 + 4 = 142. ✓

**Bucket members (by `model_id`):**
- **model_infeasible (7):** `agreste`, `camcge`, `cesam`, `fawley`, `lnts`, `mine`, `rocket`
- **path_syntax_error (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`
- **path_solve_terminated (4):** `dyncge`, `elec`, `tricp`, `twocge`
- **path_solve_license (9):** `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `srpchase`, `tabora`, `tfordy`
- **non-translate (7):** `danwolfe`, `decomp`, `iswnm`, `mexls`, `nebrazil`, `saras`, `sarf`

## 4. Genuine-vs-methodology partition (PR25) — genuine floor 74

**Operational definition** (unchanged from PR25 / S32): the **methodology** set = `model_optimal_presolve` **AND** `comparison_status = match` whose **cold** MCP failed/mismatched (the warm-start was *required*) with the cold emit **byte-identical to its pre-fix state** — already-emit-correct models the broadened presolve-retry *validates*, not repeatable cross-term gains. The **genuine floor** = every other match: a cold match, OR a match whose cold emit a real fix *changed*.

| Population | Count | Provenance |
|---|---|---|
| **Genuine, stable (floor)** | **74** | S30 70 + S31 P2's +4 (polygon [candidate] + ps2_f_s / ps2_s / ps3_s_gic [non-candidate]) |
| **Methodology-recovered** | **21** | `model_optimal_presolve` matches whose cold emit is byte-identical to pre-fix (incl. the CGE cluster `irscge`/`lrgcge`/`moncge`, cpack, himmel16, …) |
| **As-measured (all-219) Match** | **95** | 74 genuine + 21 methodology |

**Genuine floor = 74** is the Day-0 anchor (S30 70 + P2's +4; re-baselined at S32 close after the ≥ 75 step was MISSED — mine/camcge REPLAN'd). It spans candidates **and** non-candidates, so it is not a 142-corpus-only count.

**Genuine-floor → ≥ 75 conversion map (Sprint 33 tracks that convert a `model_infeasible` candidate into a genuine cold match, +1 genuine floor each):**

| Track | Day-0 bucket | +1 genuine floor if… |
|---|---|---|
| **mine** (P1 #1443) | `model_infeasible` (MS 5) | the head-offset cross-term re-derivation cold-matches (infeasible → optimal) |
| **fawley** (P3 #1111/#1112) | `model_infeasible` (MS 5, LP 2899.25) | the second-index generalization cold-matches (infeasible → optimal) |
| **camcge** (P4 #1330 → Epic 5) | `model_infeasible` (MS 4) | the dual-consistent Walras numéraire lands (infeasible → optimal), Epic-5-scoped |

**Footnote-⁸ ramp alignment:** the genuine-floor ramp is **S30 70 → S31 74 → S32 actual 74 → S33 ≥ 75 → S34 maintain ≥ 75 → S35 ≥ 77 → S36 ≥ 78** (`PROJECT_PLAN.md` footnote ⁸, as renumbered by the Sprint 33 insertion). Day-0 genuine floor **74** is the ramp's anchor; Sprint 33 targets the **≥ 75** step, conditional on mine [P1] / fawley [P3] cold-matching (the Sprint-30-retro §3 warning: the ramp is NOT independent +1s — every S33 mover is a from-scratch AD/emit track that could REPLAN, so a flat-74 close is the modal outcome).

## 5. Per-carryforward-model provenance (Day-0 → expected Day-13)

| Model | Priority | conv | Day-0 bucket | MS | Expected Day-13 | Corpus |
|---|---|---|---|---|---|---|
| **mine** | P1 (Solve) | verified_convex | model_infeasible | 5 | MODEL STATUS 1 (+1 Solve, +1 genuine floor if cold-matches) OR further-architecture REPLAN | candidate |
| **sarf** | P2 (Translate) | verified_convex | non-translate (translate_timeout) | — | translate (+1 Translate → 136) OR re-scoping | candidate |
| **fawley** | P3 (Solve) | verified_convex | model_infeasible | 5 | MODEL STATUS 1 (+1 Solve, +1 genuine floor if cold-matches) OR gate-leak re-scoping | candidate |
| **camcge** | P4 (Epic 5) | likely_convex | model_infeasible | 4 | MODEL STATUS 1 (+1 Solve) OR per-model-numéraire Epic-5 finding | candidate |
| **rocket** | P5 (PATH) | likely_convex | model_infeasible | 5 | consultation input submitted (Sprint 34); +1 Solve conditional on forcing | candidate |
| **hhfair** | P5 (Case-c) | likely_convex | model_optimal (**mismatch**) | 1 | stays mismatch (documented `case_c_objdef`); forcing-explored | candidate |
| **irscge** | P5 (CGE cluster) | likely_convex | model_optimal_presolve (**match**, methodology) | 1 | stays methodology match (Case-c, non-convert) | candidate |
| **lrgcge** | P5 (CGE cluster) | likely_convex | model_optimal_presolve (**match**, methodology) | 1 | stays methodology match (Case-c, non-convert) | candidate |
| **moncge** | P5 (CGE cluster) | likely_convex | model_optimal_presolve (**match**, methodology) | 1 | stays methodology match (Case-c, non-convert) | candidate |
| **agreste** | P6 (re-triage) | verified_convex | model_infeasible | 5 | re-triaged (verify double-`solve` scope before any fix) OR recovered | candidate |
| **cesam** | P6 (re-triage) | likely_convex | model_infeasible | 4 | Case-c re-confirm (banked) | candidate |
| **lnts** | P6 (re-triage) | likely_convex | model_infeasible | 4 | Case-c re-confirm (banked) | candidate |

**Notes on the Day-0 buckets:**
- **mine** and **fawley** are the two firm +Solve/+genuine-floor levers — both `model_infeasible` candidates whose recovery lifts all three of {142-corpus Match, all-219 tally, genuine floor}.
- **sarf** is the sole +Translate lever (the only non-translate carryforward).
- **hhfair** is `model_optimal` (MS 1) but **mismatch** — it solves to a *spurious* optimum (the `case_c_objdef` signature), which is why it is a Case-c forcing problem, not an emit-fix candidate.
- **irscge/lrgcge/moncge** already **match** via the presolve warm-start (methodology) → converting them is not available (documented Case-c); they do not move the genuine floor.

## 6. Corpus scope (142 vs 219) — which population each KPI measures

| Population | Match | Note |
|---|---|---|
| **142-corpus (headline)** | **92** | the convex-candidate corpus; the authoritative headline scope |
| **all-219 tally** | **95** | +3 non-candidate `non_convex` matches: `ps2_f_s`, `ps2_s`, `ps3_s_gic` (persisted S31 Day 13) |
| **genuine cold-robustness floor** | **74** | spans candidates + non-candidates (S30 70 + P2's +4) |

The Sprint-31 P2 gains land **outside** the 142 corpus (`ps2_f_s`/`ps2_s`/`ps3_s_gic` are `non_convex` → non-candidates), so they lift the all-219 tally + the genuine floor but **not** the headline 142-corpus KPI. **Sprint 33's Solve movers (mine, fawley, camcge) ARE candidates**, so their gains lift all three.

---

**Day-0 anchor:** `ee51ed9e` (Sprint 32 close) · DB byte-unchanged since `4cbf8bff` · genuine floor 74 · 142-corpus Match 92 · all-219 Match 95 · Solve 107 · Translate 135 · model_infeasible 7 · determinism ✅ ×3.
**Owner:** Sprint 33 Planning Team
