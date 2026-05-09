# Sprint 26 Day 0 Baseline Metrics + Scope Freeze

**Status:** ✅ FROZEN (Day 0)
**Date:** 2026-05-09
**Owner:** Prep Task 9
**Pipeline runner:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
**Run duration:** 12779.1s (~3h33m), exit 0
**Schema version:** v2.2.1 (unchanged from Sprint 25 final)
**Denominator:** 142 convex-continuous in-scope models (LOCKED, matching Sprint 25 Day 14 final)

---

## 1. Purpose

This document is the Sprint 26 Day 0 baseline, produced per Sprint 24 retrospective recommendation **PR6 ("Full pipeline baseline before sprint")**, the companion **PR15 ("Freeze pipeline scope before Day 0")**, and the new Sprint 25 retrospective recommendation **PR17 ("Track bucket transitions explicitly")**. It serves three functions:

1. **Baseline reference** — all Sprint 26 acceptance-criteria deltas (Parse, Translate, Solve, Match; error-category counts) are measured against the numbers recorded here.
2. **Scope freeze** — the 142-model denominator and the v2.2.1 exclusion set are committed for Sprint 26. No mid-sprint exclusion edits unless permitted by the runtime-filter policy carried forward from Sprint 25 §5.
3. **Bucket-provenance baseline** — per-failing-model transition data ("Sprint 25 Day 14 bucket → Sprint 26 Day 0 bucket") added in §4 below per **PR17**, addressing Sprint 25's KU-34 finding that bucket churn dominated the path_syntax_error metric.

Sprint 26 prep ran in docs-only PRs #1366–#1372; no `src/` code changed between Sprint 25 close and this baseline. Three models exhibit bucket churn in this baseline (clearlak, ganges, turkpow) — attributed to machine-load variance at the 600s translate timeout boundary, not to a code regression. See §4 for full details.

---

## 2. Baseline Headline Metrics (convex in-scope = 142)

| Metric | Sprint 25 Day 14 | Sprint 26 Day 0 | Δ | % of 142 |
|---|---|---|---|---|
| Parse success | 142 | 142 | 0 | 100.0% |
| Translate success | 133 | 130 | **−3** (machine-variance bucket churn — see §4) | 91.5% |
| Solve success | 104 | 104 | 0 | 73.2% |
| Solution match (full pipeline success) | 60 | 60 | 0 | 42.3% |

**Net headline:** Solve and Match held steady. The Translate −3 is bucket churn (3 path_syntax_error models in Sprint 25 Day 14 → translate_timeout in Sprint 26 Day 0); see §4 for per-model transitions. **No structural regressions attributable to Sprint 26 prep PRs (#1366–#1372 were all docs-only).**

### 2.1 Translate breakdown

- **130 successes**
- **12 failures** (bucket name in tables / §4 = `translate_<category>`; raw `nlp2mcp_translate.error.category` shown in backticks):
  - **8 `translate_timeout`** (raw category `timeout`; 600s budget exceeded):
    - 5 unchanged from Sprint 25 final: `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase` — `SetMembershipTest` / `enumerate_equation_instances` Cartesian-explosion pattern (Sprint 25 `PROFILE_HARD_TIMEOUTS.md`; Sprint 26 Priority 4 Option 1 short-circuit candidates per Task 6 design).
    - 3 new at Day 0: `clearlak` (480.7s → 600.1s), `ganges` (386.9s → 600.7s), `turkpow` (379.8s → 600.1s) — translate-flaky at the 600s budget boundary; pipeline ran ~37% slower overall (12779s vs Sprint 25's 9310s) due to machine-load variance, pushing these 3 over the timeout. **Not a Sprint 26 prep regression** — Sprint 26 prep PRs were all docs-only.
  - **4 `translate_internal_error`** (raw category `internal_error`; unchanged from Sprint 25 final):
    - `danwolfe`, `decomp` — multi-solve driver scripts, gated at translate (issue #1270).
    - `saras` — multi-solve driver, newly gated by Sprint 25 Day 12 #1270 Approach A.
    - `mine` — `internal_error` from `src/ad/index_mapping.py` UserWarning (#1224 — `IndexOffset(ParamRef)` deferred to Sprint 27 per Task 6 #1224 deferral decision).

Translate timing (success only, n=130): mean 33.4s, median 7.2s, p90 ≈ 66s. Top 10 slowest (s): 546.2, 508.6, 376.1, 289.7, 264.3, 237.6, 210.9, 128.5, 127.5, 101.0. (Sprint 25 final top 10: 335.7, 332.2, 322.6, 296.0, 258.5, 173.0, 165.6, 128.0, 123.6, 101.1 — this run is ~37% slower across the board, consistent with the bucket-churn attribution.)

### 2.2 Solve breakdown

- **104 successes** (includes 5 `model_optimal_presolve` recoveries: `bearing`, `chain`, `mathopt3`, `robustlp`, `rocket` — STATUS 5 retry with pre-solve. Note: `chain` and `robustlp` are Sprint 25 emitter-fix recoveries.)
- **26 failures** (by `outcome_category`):

| Category | Sprint 25 Day 14 | Sprint 26 Day 0 | Δ | Models (Day 0) |
|---|---|---|---|---|
| `path_syntax_error` | 12 | 9 | **−3** | `camcge`, `cesam2`, `dinam`, `fawley`, `gangesx`, `indus`, `otpop`, `sample`, `turkey` |
| `path_solve_terminated` | 5 | 5 | 0 | `dyncge`, `elec`, `maxmin`, `tricp`, `twocge` |
| `model_infeasible` | 4 | 4 | 0 | `agreste`, `camshape`, `cesam`, `lnts` |
| `path_solve_license` | 8 | 8 | 0 | `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `tabora`, `tfordy` |

The path_syntax_error −3 is **the same 3-model bucket churn** as Translate +3: `clearlak`, `ganges`, `turkpow` were path_syntax_error at Sprint 25 Day 14 (translated successfully but PATH compile-failed at solve), and now hit the 600s translate timeout at Day 0 instead. They're still failing — just at an earlier pipeline stage.

- **12 not_tested** (cascade-skipped because translate failed: 8 timeout + 4 internal_error).

### 2.3 Solution comparison breakdown

| Status | Sprint 25 Day 14 | Sprint 26 Day 0 | Δ |
|---|---|---|---|
| `match` | 60 | 60 | 0 |
| `mismatch` | 38 | 38 | 0 |
| `skipped` | 6 | 6 | 0 |
| `not_tested` | 38 (= 12 syntax + 5 term + 4 inf + 8 lic + 9 translate) | 38 (= 9 syntax + 5 term + 4 inf + 8 lic + 12 translate) | 0 (composition shifted) |

---

## 3. Scope Breakdown (219 → 142)

| Bucket | Count | Definition |
|---|---|---|
| **In-scope (convex-continuous)** | **142** | `convexity.status ∈ {likely_convex, verified_convex}` |
| — likely_convex | 88 | (Sprint 25 Day 14 final value preserved) |
| — verified_convex | 54 | |
| Out-of-scope: explicit excluded | 21 | `convexity.status = excluded` — 14 MINLP + 7 legacy |
| Out-of-scope: convexity error | 43 | `convexity.status = error` (LP/NLP that failed pre-solve verification) |
| Out-of-scope: non-convex | **8** | `convexity.status = non_convex` — 7 baseline `ps*_s*` sqrt-objective models + **`abel`** (Sprint 25 Day 4 reclassification, see Sprint 25 BASELINE_METRICS §5.1) |
| Out-of-scope: unknown | 5 | `convexity.status = unknown` |
| **Total** | **219** | — |

The 219-model corpus and the 142-in-scope denominator are unchanged from Sprint 25 Day 14 final.

---

## 4. Bucket Provenance (PR17) — Per-Failing-Model Transitions

**Per Sprint 25 retrospective recommendation PR17 (KU-34):** record per-failing-model bucket transitions so Sprint 26 acceptance-criteria evaluation can distinguish bucket churn (model moves between failure categories) from real regressions (model moves from success to failure or vice versa).

### 4.1 Models that changed bucket between Sprint 25 Day 14 and Sprint 26 Day 0

**3 models, all attributed to machine-load variance at the 600s translate timeout boundary** (no Sprint 26 prep PR touched `src/`):

| Model | Sprint 25 Day 14 bucket | Sprint 26 Day 0 bucket | Transition note | Translate time pre → post |
|---|---|---|---|---|
| `clearlak` | `path_syntax_error` (translates, PATH compile-fails) | `translate_timeout` | Bucket churn | 480.7s → 600.1s |
| `ganges` | `path_syntax_error` | `translate_timeout` | Bucket churn | 386.9s → 600.7s |
| `turkpow` | `path_syntax_error` | `translate_timeout` | Bucket churn | 379.8s → 600.1s |

**All 3 still fail; net failure count is unchanged.** They moved earlier in the pipeline because the Sprint 26 Day 0 baseline run was ~37% slower overall (machine load), pushing translate times that were 380–480s into the 600s timeout.

**Comparison-model translate-time growth (succeeded both runs, evidence of machine-load variance):** `gangesx` 336.8s → 508.6s (+51%), `turkey` 133.8s → 237.6s (+77%), `indus` 127.2s → 210.9s (+66%). The 3 churn-out models had the same kind of growth; they were just close enough to the 600s boundary to cross it.

### 4.2 Per-bucket Day 14 → Day 0 composition

#### `path_syntax_error` (12 → 9)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `clearlak` | path_syntax_error | translate_timeout | **Churn** (machine variance, see §4.1) |
| `ganges` | path_syntax_error | translate_timeout | **Churn** (machine variance, see §4.1) |
| `turkpow` | path_syntax_error | translate_timeout | **Churn** (machine variance, see §4.1) |
| `dinam` | path_syntax_error | path_syntax_error | Stayed (Sprint 26 carryforward) |
| `gangesx` | path_syntax_error | path_syntax_error | Stayed |
| `indus` | path_syntax_error | path_syntax_error | Stayed |
| `sample` | path_syntax_error | path_syntax_error | Stayed |
| `turkey` | path_syntax_error | path_syntax_error | Stayed |
| `camcge` | path_syntax_error | path_syntax_error | Stayed (Sprint 25 Day 14 bucket transfer; Sprint 26 Priority 1 target — issue #1354 Pattern C variant) |
| `cesam2` | path_syntax_error | path_syntax_error | Stayed (Sprint 25 Day 14 bucket transfer; Sprint 26 Priority 1 target — issue #1355 Pattern C variant) |
| `fawley` | path_syntax_error | path_syntax_error | Stayed (Sprint 25 Day 14 bucket transfer; issue #1356 — Sprint 27 carryforward per Task 4) |
| `otpop` | path_syntax_error | path_syntax_error | Stayed (Sprint 25 Day 14 regression; issue #1357 — Sprint 27 carryforward per Task 4 / Task 7) |

#### `path_solve_terminated` (5 → 5)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `dyncge`, `elec`, `maxmin`, `tricp`, `twocge` | path_solve_terminated | path_solve_terminated | All stayed |

#### `model_infeasible` (4 → 4)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `agreste`, `camshape`, `cesam`, `lnts` | model_infeasible | model_infeasible | All stayed |

#### `path_solve_license` (8 → 8)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `egypt`, `ferts`, `glider`, `robot`, `shale`, `sroute`, `tabora`, `tfordy` | path_solve_license | path_solve_license | All stayed (`ferts` was Sprint 25 Day 14 bucket transfer from path_syntax_error after #1290) |

#### `translate_timeout` (5 → 8)

(Day 14 / Day 0 cells use the bucket label `translate_timeout`; the underlying `nlp2mcp_translate.error.category` is `timeout`.)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase` | translate_timeout | translate_timeout | All stayed (Sprint 26 Priority 4 candidates per Task 6 design) |
| `clearlak`, `ganges`, `turkpow` | path_syntax_error | translate_timeout | **Churn-in** (machine variance; see §4.1) |

#### `translate_internal_error` (4 → 4)

(Day 14 / Day 0 cells use the bucket label `translate_internal_error`; the underlying `nlp2mcp_translate.error.category` is `internal_error`.)

| Model | Sprint 25 Day 14 | Sprint 26 Day 0 | Note |
|---|---|---|---|
| `danwolfe`, `decomp` | translate_internal_error | translate_internal_error | Multi-solve drivers (gated by #1270) |
| `mine` | translate_internal_error | translate_internal_error | `IndexOffset(ParamRef)` (#1224, Sprint 27 deferral per Task 6) |
| `saras` | translate_internal_error | translate_internal_error | Multi-solve driver (gated by Sprint 25 Day 12 #1270 Approach A) |

### 4.3 Why the bucket-provenance column matters for Sprint 26 acceptance evaluation (per PR17)

Sprint 25's KU-34 finding: a "+1 path_syntax_error" headline metric concealed −3 / +4 churn (3 resolved, 4 newly transferred from other failure buckets). The same pattern would have been invisible in a strict aggregate-counts review.

**Sprint 26 acceptance criteria** (per `PROJECT_PLAN.md` §"Sprint 26 Targets") should be evaluated with bucket provenance:

- **Translate** target ≥ 135/142: at least +5 from Day 0's 130. To net +5, Sprint 26 must (a) recover the 3 machine-variance churn-outs (Priority 4 Option 1 short-circuit unblocks the boundary models) AND (b) add at least 2 more (per Task 6 projection). If Priority 4 only recovers the 3 churn-outs, headline reads +3 but no real progress vs Sprint 25 final.
- **path_syntax_error** target ≤ 6: from Day 0's 9. Net −3. Sprint 26 Priority 1 (Pattern C generalization) targets `camcge` + `cesam2` (per Task 3 PATTERN_C_HYPOTHESIS_VALIDATION REPLAN); successful fix lands −2 there. The 3 machine-variance churn-outs returning to path_syntax_error (as Priority 4 lands and they translate again) would push the count back UP — bucket provenance lets the retest distinguish "Pattern C fix landed" from "Priority 4 reverted machine-variance churn".
- **Solve** target ≥ 108: +4 from Day 0's 104. Sprint 26 Priorities 1 + 4 + 5 must net +4 from various code paths. PR17 bucket provenance ensures we don't double-count a model that goes translate_timeout → path_syntax_error → solve_success across two consecutive Day-N retests.

The bucket-provenance column in this baseline is the explicit input to Sprint 26 Day-N evaluation per PR17.

---

## 5. Frozen v2.2.1 Exclusion Set (PR15)

The Sprint 26 Day 0 **exclusion set** (Sprint 25 baseline terminology) records **24 models**, unchanged from Sprint 25 Day 14 final. The exclusion set is the union of:

- **21 `excluded`** — `convexity.status = excluded` (the 14 MINLP + 7 legacy entries detailed in §5.1 / §5.2 below)
- **3 translate-gated multi-solve drivers** — `convexity.status = verified_convex` (so they're counted in the 142-in-scope denominator) BUT gated at translate time with `nlp2mcp_translate.error.category = internal_error`: `danwolfe` and `decomp` (Sprint 24 baseline #1270) plus `saras` (Sprint 25 Day 12 #1270 Approach A addition; detailed in §5.3)

The exclusion set is **distinct from the broader out-of-scope count in §3**, which totals 77 (= 219 − 142) and includes the `error` (43) / `non_convex` (8) / `unknown` (5) buckets that are not part of the formally-frozen exclusion set. The exclusion set is the policy-frozen surface PR15 commits to keeping stable mid-sprint; the broader out-of-scope buckets are runtime-filter classifications that may shift via the §5.4 reclassification policy (e.g., the abel `likely_convex → non_convex` reclassification documented in Sprint 25 §5.1 changed an in-scope model to `non_convex` without breaking the exclusion-set freeze).

(Note: Sprint 25 BASELINE_METRICS.md §4 reported "23 total exclusions" — that count predated the Sprint 25 Day 12 saras addition. The corrected Sprint 26 Day 0 count is **24 = 21 excluded + 3 translate-gated multi-solve drivers**.)

### 5.1 MINLP out-of-scope (14)

`alan`, `andean`, `feedtray`, `gastrans`, `gqapsdp`, `kqkpsdp`, `lop`, `maxcut`, `minlphi`, `nemhaus`, `nonsharp`, `qalan`, `trnspwl`, `trnspwlx`

### 5.2 Legacy exclusions (7)

`circpack`, `epscm`, `feasopt1`, `iobalance`, `meanvar`, `orani`, `trigx`

### 5.3 Multi-solve driver translate-time gate (3)

This subsection is the translate-time runtime-filter analog of §5.1 / §5.2 (which are convexity-status `excluded` exclusions). Counted in the 142 denominator; appear at translate time with `nlp2mcp_translate.error.category = internal_error`.

**Sprint 24 baseline (2 models)** — gated by issue #1270 (multi-solve driver detection):

`danwolfe`, `decomp` — Dantzig-Wolfe / Benders decomposition driver scripts.

**Sprint 25 Day 12 addition (1 model)** — gated by issue #1270 Approach A (top-level `eq.m` cross-reference walking transitively into constraint bodies):

`saras` — primal/dual driver (calibuc.m / calibul.m → cGam → constraint-body chain). Per §5.4 below, this is permitted under the "Multi-solve driver gate extensions" runtime-filter policy and does NOT constitute a scope change.

All 3 are `convexity.status = verified_convex` so they remain in the 142 denominator. The "(2)" header in the prior revision referred to Sprint 24's count and excluded the Sprint 25 saras addition; corrected here to "(3)" to match the actual frozen-state count for Sprint 26 Day 0.

### 5.4 Scope-freeze policy carried forward from Sprint 25 §5

The same scope-freeze rules apply to Sprint 26:

- **Allowed automatically (no freeze break):** Multi-solve driver gate extensions (e.g., further `_top_level_marginal_reads` refinements landing during Sprint 26) and `convexity.status` reclassifications based on newly-surfaced ground-truth evidence (per Sprint 25 §5 second "Allowed automatically" bullet, applied to abel during Sprint 25 Day 4 — see Sprint 25 BASELINE_METRICS §5.1).
- **Not allowed:** Adding `legacy_excluded` tags, removing models from the schema, or editing the MINLP set mid-sprint without an explicit retrospective-style decision.

**Sprint 26 reversibility check (per Task 2 Unknown 6.5 verification):** the Sprint 25 abel `likely_convex → non_convex` reclassification is **NOT reversible during Sprint 26** (indefinite lambda matrix is a structural property of the model). Sprint 26 baseline freezes scope at 142 throughout.

---

## 6. Pre-vs-Post Diff

Snapshot of `data/gamslib/gamslib_status.json` was taken prior to this retest (stored at `/tmp/sprint26-task9-status-pre.json`, not committed). Comparison of pre vs post across all 219 entries:

- **Pipeline status fields:** 3 in-scope models changed bucket (clearlak, ganges, turkpow — see §4.1). All 3 transitions are translate-stage timeouts attributable to machine-load variance, not pipeline regressions.
- **22 emitted `.gms` files changed** in the 130-translates-success set. Per Sprint 25 BASELINE_METRICS §6 and the PR12 byte-stability harness (#1283 grammar-determinism enforcement), these regenerated artifacts are **advisory** until per-model byte-stability is enforced for all 142 in-scope models. The 11 Tier 0/1 canaries are byte-stable per the PR12 harness; the regenerated artifacts here are mostly outside that subset.

---

## 7. Acceptance Criteria (from PREP_PLAN.md §Task 9)

- [x] Full pipeline run completed within doubled-budget allowance → completed in ~3h33m (machine-load variance vs Sprint 25's ~2h35m; well within doubled budget)
- [x] All 8 acceptance-criteria metrics recorded → Parse / Translate / Solve / Match + 4 `outcome_category` counts in §2
- [x] Bucket-provenance column added per PR17 → §4 (per-failing-model Sprint 25 → Sprint 26 transitions)
- [x] Scope-freeze decision documented → §5 (carried forward from Sprint 25 §5)
- [x] Cross-reference with Sprint 24 PR15 + Sprint 25 PR17 recommendations → §1, §4, §5
- [x] Unknowns 6.3, 6.5 verified and updated in KNOWN_UNKNOWNS.md → see Unknown 6.3 / 6.5 Verification Results

---

## 8. Related Documents

- `PREP_PLAN.md` §Task 9 — this task's specification.
- `KNOWN_UNKNOWNS.md` §Unknowns 6.3, 6.5 — verification results recorded there.
- Sprint 25 `BASELINE_METRICS.md` — format this baseline extends; §5.1 documents the abel reclassification.
- Sprint 25 `SPRINT_LOG.md` Day 14 — informal bucket-provenance source for §4 Sprint 25 Day 14 column.
- Sprint 25 `SPRINT_RETROSPECTIVE.md` §"What We'd Do Differently" #2 (PR17 origin) + KU-34 (bucket churn).
- `PROFILE_HARD_TIMEOUTS.md` (Sprint 25 prep Task 8) — explains the 5 baseline `timeout` translate failures.
- `DESIGN_OPTION_1_SHORT_CIRCUIT.md` (Sprint 26 prep Task 6) — design for Priority 4 Option 1 short-circuit that targets the 5 baseline timeouts + likely the 3 churn-out boundary models.
- `PATTERN_C_HYPOTHESIS_VALIDATION.md` (Sprint 26 prep Task 3) — Sprint 26 Priority 1 REPLAN scope: camcge + cesam2 in path_syntax_error.
- `PATTERN_A_RECLASSIFICATION_PLAN.md` (Sprint 26 prep Task 4) — fawley + otpop deferred to Sprint 27 alongside fawley #1356 / #1357 comp_up subset/superset workstream.
- `AD_RESIDUALS_RECAP.md` (Sprint 26 prep Task 7) — #1334 / #1335 fix sites in `src/kkt/stationarity.py` (`_add_indexed_jacobian_terms`) + `src/ad/constraint_jacobian.py` (`if eq_domain:` gate).
