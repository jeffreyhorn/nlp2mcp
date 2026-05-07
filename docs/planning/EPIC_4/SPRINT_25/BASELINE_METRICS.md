# Sprint 25 Day 0 Baseline Metrics + Scope Freeze

**Status:** ✅ FROZEN (Day 0)
**Date:** 2026-04-21
**Owner:** Prep Task 9
**Pipeline runner:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
**Run duration:** 8111.5s (~2h15m), exit 0
**Schema version:** v2.2.1
**Denominator:** 143 convex-continuous in-scope models (LOCKED)

---

## 1. Purpose

This document is the Sprint 25 Day 0 baseline, produced per Sprint 24 retrospective recommendation **PR6 ("Full pipeline baseline before sprint")** and the companion recommendation **PR15 ("Freeze pipeline scope before Day 0")**. It serves two functions:

1. **Baseline reference** — all Sprint 25 acceptance-criteria deltas (Parse, Translate, Solve, Match; error-category counts) are measured against the numbers recorded here.
2. **Scope freeze** — the 143-model denominator and the v2.2.1 exclusion set are committed for Sprint 25. No mid-sprint exclusion edits unless the multi-solve driver gate catches an additional model automatically (documented §5 below).

Sprint 24 ran with a mid-sprint scope shift (147 → 143 via the multi-solve driver exclusion) that complicated acceptance-criteria evaluation during review. PR15 and this document prevent a recurrence.

---

## 2. Baseline Headline Metrics (convex in-scope = 143)

| Metric                | Count | % of 143 |
|-----------------------|-------|----------|
| Parse success         | 143   | 100.0%   |
| Translate success     | 135   | 94.4%    |
| Solve success         | 99    | 69.2%    |
| Solution match (full pipeline success) | 54 | 37.8% |

### 2.1 Translate breakdown

- **135 successes**
- **8 failures:**
  - 5 `timeout` (600s budget exceeded): `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase` — all share the `SetMembershipTest` / `enumerate_equation_instances` Cartesian-explosion pattern profiled in `PROFILE_HARD_TIMEOUTS.md` (Prep Task 8).
  - 3 `internal_error`:
    - `danwolfe`, `decomp` — multi-solve driver scripts, gated out at translate time (Sprint 24 issue #1270 gate).
    - `mine` — `internal_error` whose root message is a `UserWarning` from `src/ad/index_mapping.py` ("Failed to evaluate condition … SetMembershipTest … Set membership for 'c' cannot be evaluated statically because the set has no concrete members at compile time"). Same dynamic-subset family as the 5 timeouts; small priority candidate — see `DESIGN_SMALL_PRIORITIES.md`.

Translate timing (success only): mean 24.0s, median 4.3s, p90 ≈ 92s. Top 10 slowest (s): 335.7, 332.2, 322.6, 296.0, 258.5, 173.0, 165.6, 128.0, 123.6, 101.1.

### 2.2 Solve breakdown

- **99 successes** (includes 3 `model_optimal_presolve` recoveries: `bearing`, `mathopt3`, `rocket` — STATUS 5 retry with pre-solve).
- **36 failures** (by `outcome_category`):

| Category                 | Count | Models |
|--------------------------|-------|--------|
| `path_syntax_error`      | 11    | `clearlak`, `dinam`, `ferts`, `ganges`, `gangesx`, `indus`, `mathopt4`, `sample`, `saras`, `turkey`, `turkpow` |
| `path_solve_terminated`  | 10    | `camcge`, `cesam2`, `dyncge`, `elec`, `etamac`, `gtm`, `lmp2`, `maxmin`, `tricp`, `twocge` |
| `model_infeasible`       | 8     | `agreste`, `camshape`, `cesam`, `chain`, `fawley`, `korcge`, `lnts`, `robustlp` |
| `path_solve_license`     | 7     | `egypt`, `glider`, `robot`, `shale`, `sroute`, `tabora`, `tfordy` |

- **8 not_tested** (cascade-skipped because translate failed).

### 2.3 Solution comparison breakdown

| Status          | Count |
|-----------------|-------|
| `match`         | 54    |
| `mismatch`      | 39    |
| `skipped`       | 6     |
| `not_tested`    | 44    |

---

## 3. Scope Breakdown (219 → 143)

| Bucket                       | Count | Definition |
|------------------------------|-------|------------|
| **In-scope (convex-continuous)** | **143** | `convexity.status ∈ {likely_convex, verified_convex}` |
| — likely_convex              | 89    |            |
| — verified_convex            | 54    |            |
| Out-of-scope: explicit excluded | 21 | `convexity.status = excluded` — 14 MINLP + 7 legacy |
| Out-of-scope: convexity error   | 43 | `convexity.status = error` (mostly LP/NLP that failed pre-solve verification) |
| Out-of-scope: non-convex        | 7  | `convexity.status = non_convex` (7 `ps*_s*` sqrt-objective models) |
| Out-of-scope: unknown           | 5  | `convexity.status = unknown` |
| **Total**                    | **219** | — |

---

## 4. Frozen v2.2.1 Exclusion Set

The v2.2.1 schema records **23 total exclusions**. Twenty-one are tagged in the `convexity.status = excluded` bucket; two are recorded in `_migration_summary_v2_2_1.multi_solve_excluded=2` and surface at translate time via the driver gate rather than via the convexity field.

### 4.1 MINLP out-of-scope (14)

`alan`, `andean`, `feedtray`, `gastrans`, `gqapsdp`, `kqkpsdp`, `lop`, `maxcut`, `minlphi`, `nemhaus`, `nonsharp`, `qalan`, `trnspwl`, `trnspwlx`
— mixed-integer / discrete models; out of KKT scope (per `feedback_minlp_scope`).

### 4.2 Legacy exclusions (7)

`circpack`, `epscm`, `feasopt1`, `iobalance`, `meanvar`, `orani`, `trigx`
— pre-existing exclusions carried forward from earlier sprints (data-only / non-optimization / obsolete-formulation).

### 4.3 Multi-solve driver out-of-scope (2)

`danwolfe`, `decomp`
— Dantzig–Wolfe / Benders decomposition driver scripts. Convexity verification treats each inner solve as convex, so their recorded baseline status is `convexity.status = verified_convex` (included in the 143 denominator). The translate-time gate (issue #1270, shipped Sprint 24) rejects them because a single KKT transform cannot represent the converged solution of a multi-solve driver. **They are counted in the 143 denominator and show up with `nlp2mcp_translate.error.category = internal_error` plus `pipeline_status.reason = multi_solve_driver_out_of_scope`** — intentional, so the gate's effect is visible in the Sprint 25 baseline.

---

## 5. Scope Freeze (PR15)

**Decision:** The 143-model denominator and the v2.2.1 exclusion set are frozen for the duration of Sprint 25. Sprint 25 acceptance criteria — Parse, Translate, Solve, Match target deltas and error-category reductions — are evaluated against the baseline numbers in §2 and against 143 as the denominator.

**Policy for mid-sprint exclusion additions:**

- **Allowed automatically (no freeze break):** The multi-solve driver gate (`src/validation/driver.py`) is a runtime filter. If Sprint 25 work extends the gate's conjunction (issue #1270 follow-up) and the extended gate rejects additional models (e.g., `saras`), those models remain in the 143 denominator but appear as `translate.failure / multi_solve_driver_out_of_scope`. This is identical to the baseline handling of `danwolfe` and `decomp` and does **not** constitute a scope change requiring re-freeze.
- **Allowed automatically (no freeze break):** `convexity.status` reclassifications (e.g., `likely_convex` → `non_convex`) when sprint work surfaces ground-truth evidence about a model's mathematical structure (indefinite Hessian / lambda matrix, etc.). Reclassified models remain in the 219-corpus and the comparison set; their `solution_comparison.comparison_status` continues to be reported but is treated as informational (parallel to the existing 7 `non_convex` `ps*_s*` models). This is the same runtime-filter treatment as the multi-solve driver gate above and does **not** constitute a scope change requiring re-freeze. See §5.1 for the one Sprint 25 instance (`abel`).
- **Not allowed:** Adding `legacy_excluded` tags, removing models from the schema, or editing the MINLP set mid-sprint. Any such change requires an explicit Sprint 25 retrospective-style decision before being applied.

**Consequence:** Sprint 25 acceptance criteria — Match target, Solve target, error-category reductions — are **calibrated against the 143-denominator baseline** (Day 0). Mid-sprint reclassifications under the runtime-filter policy above may shift the as-of-Day-N in-scope count below 143 (Sprint 25 Day 14 final: 142 in-scope; see §5.1) without invalidating the calibration: the reclassified model is counted as a runtime-filter mismatch, identical to how the 7 baseline `non_convex` `ps*_s*` models are accounted. The Sprint 24 ambiguity (pipeline scope 143 vs triage scope 147) does not recur.

### 5.1 Sprint 25 Mid-Sprint Reclassification

**Identified during Sprint 26 Prep Task 2 (PR18 — Sprint 25 retrospective recommendation).**

**Model:** `abel`
**Prior `convexity.status`:** `likely_convex` (Sprint 25 Day 0 baseline)
**New `convexity.status`:** `non_convex` (Sprint 25 Day 4, 2026-04-25)
**Triggering commit:** `c922bb2d` — *"Mark abel non-convex in gamslib_status.json + file #1313 for warm-start fix"*
**Tracking issue:** [#1313](https://github.com/jeffreyhorn/nlp2mcp/issues/1313) (CLOSED during Sprint 25)
**Discovery context:** [`docs/planning/EPIC_4/SPRINT_25/DAY8_QABEL_ABEL_REASSESSMENT.md`](DAY8_QABEL_ABEL_REASSESSMENT.md) — Sprint 25 Day 8 qabel/abel PATH-solve reassessment.

**Reason for reclassification:** abel's lambda matrix has the off-diagonal asymmetric entry `lambda(money, gov-expend) = 0.444`. The symmetric part has eigenvalues approximately `[-0.047, 1.047]` — indefinite, making the criterion's `u`-quadratic genuinely non-convex. Multi-start NLP confirmed the NLP solver finds a unique objective (the linear `stateq` dynamics tightly constrain the feasible set, masking the indefiniteness for CONOPT), but the MCP/PATH formulation doesn't have that constraint-induced uniqueness — the KKT system genuinely has multiple stationary points and PATH converges to a different valid one than CONOPT. This is a property of the model, not the emitter — the MCP is mathematically correct.

**Policy classification:** **Runtime filter** (per §5 above, second "Allowed automatically" bullet — `convexity.status` reclassifications). Same handling as the existing 7 baseline `non_convex` models (`ps10_s, ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp`). abel remains in the 219-corpus and the comparison set; its `solution_comparison.comparison_status` stays as `mismatch` (informational only). The 143-denominator was **not** retroactively rewritten — Sprint 25 acceptance deltas remain calibrated against 143 (Day 0 baseline) — but the as-of-Day-14 in-scope count drops to **142** because abel is now in the runtime-filter (non-convex) bucket.

**Relationship to §5 freeze:** The §5 freeze prohibits schema/exclusion-set edits (legacy_excluded additions, MINLP-set edits, model removals). It does **not** prohibit `convexity.status` field changes that reflect newly-surfaced ground-truth evidence about a model's mathematical structure — those are explicitly permitted as a runtime-filter mechanism (§5, second "Allowed automatically" bullet). The Sprint 25 Day 14 final retest reports both the 142 as-of-Day-14 in-scope count AND the deltas-against-143 acceptance numbers (see CHANGELOG Sprint 25 Summary).

**Reversibility during Sprint 26:** **No.** The reclassification reflects a fundamental property of the abel model (indefinite lambda matrix) and is not a code-change artifact. #1313 (the warm-start fix that would have addressed the PATH convergence issue) was CLOSED during Sprint 25 — but closing it didn't restore convexity, only documented that the warm-start path doesn't apply. Sprint 26 baseline (Task 9) freezes scope at **142** in-scope.

**Sprint 26 implication:** `BASELINE_METRICS.md` Sprint 26 baseline (Task 9) uses 142 as the denominator throughout, matching the Sprint 25 Day 14 final scope. The 143 → 142 transition is a one-way change documented here for traceability; no further scope-shifts are anticipated barring discovery of additional non-convex models.

---

## 6. Pre-vs-Post Diff

Snapshot of `data/gamslib/gamslib_status.json` was taken prior to this retest (stored at `/tmp/task9-status-pre.json`, not committed). Comparison of pre vs post across all 219 entries:

- **Pipeline status fields (translate/solve/compare) identical for all 219 models.** No cascading status changes during the retest.
- **Three emitted `.gms` files changed:** `data/gamslib/mcp/chenery_mcp.gms`, `indus_mcp.gms`, `turkey_mcp.gms` — consistent with parser non-determinism tracked as issue #1283 (see `INVESTIGATION_PARSER_NON_DETERMINISM.md`). These diffs should not be described as harmless byte-level variance: #1283 can change emitted numeric content (e.g., shifted/missing parameter assignments observed on chenery), so the regenerated artifacts may be semantically different or corrupted until determinism is enforced. The committed files are a single non-deterministic realization; the pre-retest `gamslib_status.json` `comparison_status` values captured in §2.3 reflect behavior against whichever realization was present at each run, so downstream metrics are not invalidated by the specific realization chosen. Determinism enforcement via PR12 (Prep Task 10) is the Sprint 25 remedy; until it lands, treat these committed artifacts as advisory rather than authoritative.

---

## 7. Acceptance Criteria (from PREP_PLAN §Task 9)

- [x] Full pipeline run completed within doubled-budget allowance → **completed in ~2h15m** (acceptable. Tasks 8/10 unblock any budget-reduction work in-sprint.)
- [x] All 8 acceptance-criteria metrics recorded → Parse / Translate / Solve / Match + 4 `outcome_category` counts in §2
- [x] Scope-freeze decision documented with reasoning → §5
- [x] Cross-reference with Sprint 24 PR15 recommendation → §1, §5
- [x] Unknown 6.1 verified and updated in KNOWN_UNKNOWNS.md → see KU 6.1 Verification Results

---

## 8. Related Documents

- `PREP_PLAN.md` §Task 9 — this task's specification.
- `KNOWN_UNKNOWNS.md` §Unknown 6.1 — verification results recorded there.
- `PROFILE_HARD_TIMEOUTS.md` — explains the 5 `timeout` translate failures.
- `DESIGN_SMALL_PRIORITIES.md` — tracks `mine` (`internal_error`; condition-eval UserWarning) as a small-priority candidate.
- `INVESTIGATION_PARSER_NON_DETERMINISM.md` — explains the three byte-level diffs in §6.
- Sprint 24 retrospective PR6 and PR15 recommendations in `EPIC_4/SPRINT_24/`.
