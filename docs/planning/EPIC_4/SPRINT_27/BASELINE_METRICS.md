# Sprint 27 Day 0 Baseline Metrics + Scope Freeze

**Status:** ✅ FROZEN (Day 0)
**Date:** 2026-05-28
**Owner:** Prep Task 3
**Pipeline runner:** `.venv/bin/python scripts/gamslib/run_full_test.py --quiet`
**Run duration:** 11422.1s (~3h10m), exit 0
**Schema version:** v2.2.1 (unchanged from Sprint 26 final)
**Denominator:** 142 convex-continuous in-scope models (LOCKED, matching Sprint 26 Day 13 (final))

---

## 1. Purpose

This document is the Sprint 27 Day 0 baseline, produced per Sprint 24 retrospective recommendation **PR6 ("Full pipeline baseline before sprint")**, the companion **PR15 ("Freeze pipeline scope before Day 0")**, and Sprint 25 retrospective recommendation **PR17 ("Track bucket transitions explicitly")** — both reaffirmed for Sprint 27 per Sprint 27 PREP_PLAN.md §Task 3. It serves three functions:

1. **Baseline reference** — all Sprint 27 acceptance-criteria deltas (Parse, Translate, Solve, Match; error-category counts) are measured against the numbers recorded here.
2. **Scope freeze** — the 142-model denominator and the v2.2.1 exclusion set are committed for Sprint 27. No mid-sprint exclusion edits unless permitted by the runtime-filter policy carried forward from Sprint 25 §5.
3. **Bucket-provenance baseline** — per-failing-model transition data ("Sprint 26 Day 13 (final) bucket → Sprint 27 Day 0 bucket") added in §6 below per **PR17**, with Sprint 26 Day 0 bucket also recorded where the model shifted mid-Sprint 26.

Sprint 27 prep ran in docs-only PRs (#1402 Sprint 27 prep scaffolding + #1403 Sprint 27 Prep Task 2); no `src/` code changed between Sprint 26 close (last src/ commit was 8d4cc4ac on Sprint 26 Day 1, no subsequent src/ commits) and this baseline. **3 models exhibit bucket churn in this baseline (clearlak, ganges, srpchase) — attributed to machine-load variance at the 600s translate timeout boundary, not to a code regression.** See §6.1 for full details. Same pattern as Sprint 26 Day 0 baseline (which had clearlak/ganges/turkpow churn under a slower runner).

---

## 2. Baseline Headline Metrics (convex in-scope = 142)

| Metric | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Δ | % of 142 |
|---|---|---|---|---|
| Parse success | 142 | 142 | 0 | 100.0% |
| Translate success | 134 | 131 | **−3** (machine-variance bucket churn — see §6) | 92.3% |
| Solve success | 103 | 103 | 0 | 72.5% |
| Solution match (full pipeline success) | 59 | 59 | 0 | 41.5% |

**Net headline:** Solve and Match held steady. The Translate −3 is bucket churn (3 path_syntax_error models in Sprint 26 Day 13 final → translate_timeout in Sprint 27 Day 0); see §6 for per-model transitions. **No structural regressions attributable to Sprint 27 prep PRs (#1402 + #1403 were all docs-only).**

### 2.1 Translate breakdown

- **131 successes**
- **11 failures**:
  - **7 `translate_timeout`** (raw category `timeout`; 600s budget exceeded):
    - 4 unchanged from Sprint 26 Day 13 final: `iswnm`, `mexls`, `nebrazil`, `sarf` — `SetMembershipTest` / `enumerate_equation_instances` Cartesian-explosion pattern (Sprint 25 `PROFILE_HARD_TIMEOUTS.md`; Sprint 27 Priority 3 #1385 target via Option 1 short-circuit redesign).
    - 3 new at Day 0: `clearlak` (128.6s → 600.1s), `ganges` (227.3s → 600.6s), `srpchase` (274.2s → 600.2s) — translate-flaky at the 600s budget boundary; this run was slower than Sprint 26 Day 13 (~3h10m vs Day 13's ~1h26m due to machine-load variance), pushing these 3 over the timeout. **Not a Sprint 27 prep regression** — Sprint 27 prep PRs (#1402 + #1403) were all docs-only.
  - **4 `translate_internal_error`** (raw category `internal_error`; unchanged from Sprint 26 Day 13 final):
    - `danwolfe`, `decomp`, `saras` — multi-solve driver scripts, gated at translate (issue #1270 + Sprint 25 Day 12 #1270 Approach A for saras).
    - `mine` — `internal_error` from `src/ad/index_mapping.py` UserWarning (#1224 — `IndexOffset(ParamRef)` Sprint 27 Priority 6 target).

Translate timing (success only, n=131): mean 57.6s, median 5.9s, p90 ≈ 116.7s.

### 2.2 Solve breakdown

- **103 successes** (97 `model_optimal` + 6 `model_optimal_presolve`)
- **28 failures** (by `outcome_category`):

| Category | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Δ Day 13 → Day 0 | Models (Sprint 27 Day 0) |
|---|---|---|---|---|---|
| `path_syntax_error` | 9 | 17 | **14** | **−3** (machine-variance churn — clearlak/ganges/srpchase moved to translate_timeout) | `camcge`, `cesam2`, `dinam`, `egypt`, `fawley`, `ferts`, `gangesx`, `indus`, `otpop`, `qdemo7`, `sample`, `shale`, `turkey`, `turkpow` |
| `path_solve_terminated` | 5 | 5 | 5 | 0 | `dyncge`, `elec`, `maxmin`, `tricp`, `twocge` |
| `model_infeasible` | 4 | 4 | 4 | 0 | `agreste`, `camshape`, `cesam`, `lnts` |
| `path_solve_license` | 8 | 5 | 5 | 0 | `glider`, `robot`, `sroute`, `tabora`, `tfordy` |

The path_syntax_error −3 is **the same 3-model bucket churn** as Translate −3: `clearlak`, `ganges`, `srpchase` were path_syntax_error at Sprint 26 Day 13 final (translated successfully but PATH compile-failed at solve), and now hit the 600s translate timeout at Day 0 instead. They're still failing — just at an earlier pipeline stage.

- **11 not_tested** (cascade-skipped because translate failed: 7 timeout + 4 internal_error).

### 2.3 Solution comparison breakdown

| Status | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Δ Day 13 → Day 0 |
|---|---|---|---|---|
| `match` | 60 | 59 | 59 | 0 |
| `mismatch` | 38 | 38 | 38 | 0 |
| `skipped` | 6 | 6 | 6 | 0 |
| `not_tested` | 38 (= 9 syntax + 5 term + 4 inf + 8 lic + 12 translate) | 39 (= 17 syntax + 5 term + 4 inf + 5 lic + 8 translate) | 39 (= 14 syntax + 5 term + 4 inf + 5 lic + 11 translate) | 0 (composition shifted from solve-stage to translate-stage) |

---

## 3. Tests Baseline

- **Sprint 26 Day 13 final:** 4,737 passed / 10 skipped / 1 xfailed (per CHANGELOG.md Sprint 26 Summary)
- **Sprint 27 Day 0:** Inherits Sprint 26 final test count (no `src/` or `tests/` changes between Sprint 26 close and this baseline). Full `make test` run is part of the standard pre-commit quality gate; counts reproduce.
- **Sprint 27 target:** ≥ 4,750 (matches Sprint 26 floor + room for ≥ 13 new tests across Priorities 1–9 work)

---

## 4. Determinism Baseline (PR12 byte-stability guard reaffirmation)

Sprint 27 Day 0 retest was run under default `PYTHONHASHSEED`. Per Sprint 24 retrospective recommendation **PR12**, full pipeline output should be byte-identical under ≥ 3 different `PYTHONHASHSEED` values. Sprint 27 inherits the PR12 guard requirement:

- **Sprint 27 acceptance criterion** (per PROJECT_PLAN.md Sprint 27): Full pipeline produces byte-identical output under at least 3 different `PYTHONHASHSEED` values
- **Sprint 27 Day 0 baseline:** PYTHONHASHSEED variation testing deferred to Sprint 27 Day 5 / Day 10 checkpoint retests (the Day 0 baseline retest is single-seed; PR12 byte-stability is verified at checkpoints + final retest per PR12's "≥ 3 seeds" requirement)

The PR12 byte-stability guard requires a separate harness run (`tests/integration/test_pipeline_determinism.py` covers the 5 fast fixtures `chenery`, `abel`, `partssupply`, `ps2_f`, `himmel11` under `make test`); the canonical 54-canary Tier 0/1/2 byte-stability evidence is Sprint 26 Day 2 PR #1380 (still valid since no `src/` changes Days 3–13 of Sprint 26 or post-Sprint 26).

---

## 5. Frozen v2.2.1 Exclusion Set (PR15) + Scope Freeze

The Sprint 27 Day 0 **exclusion set** records **24 models**, unchanged from Sprint 26 Day 13 final. The exclusion set is the union of:

- **21 `excluded`** — `convexity.status = excluded` (the 14 MINLP + 7 legacy entries detailed in §5.1 / §5.2 below)
- **3 translate-gated multi-solve drivers** — `convexity.status = verified_convex` (so they're counted in the 142-in-scope denominator) BUT gated at translate time with `nlp2mcp_translate.error.category = internal_error`: `danwolfe`, `decomp`, `saras` (detailed in §5.3)

The exclusion set is **distinct from the broader out-of-scope count**, which totals 77 (= 219 − 142) and includes the `error` (43) / `non_convex` (8) / `unknown` (5) buckets that are not part of the formally-frozen exclusion set.

### 5.1 MINLP out-of-scope (14)

`alan`, `andean`, `feedtray`, `gastrans`, `gqapsdp`, `kqkpsdp`, `lop`, `maxcut`, `minlphi`, `nemhaus`, `nonsharp`, `qalan`, `trnspwl`, `trnspwlx`

### 5.2 Legacy exclusions (7)

`circpack`, `epscm`, `feasopt1`, `iobalance`, `meanvar`, `orani`, `trigx`

### 5.3 Multi-solve driver translate-time gate (3)

Counted in the 142 denominator; appear at translate time with `nlp2mcp_translate.error.category = internal_error`:

- `danwolfe`, `decomp` — Sprint 24 baseline (gated by issue #1270)
- `saras` — Sprint 25 Day 12 addition (gated by issue #1270 Approach A — top-level `eq.m` cross-reference walking transitively into constraint bodies)

All 3 are `convexity.status = verified_convex` so they remain in the 142 denominator.

### 5.4 Scope-freeze policy carried forward from Sprint 25 §5 / Sprint 26 §5.4

Same scope-freeze rules apply to Sprint 27:

- **Allowed automatically (no freeze break):** Multi-solve driver gate extensions and `convexity.status` reclassifications based on newly-surfaced ground-truth evidence (per Sprint 25 §5 second "Allowed automatically" bullet, applied to abel during Sprint 25 Day 4 — see Sprint 25 BASELINE_METRICS §5.1).
- **Not allowed:** Adding `legacy_excluded` tags, removing models from the schema, or editing the MINLP set mid-sprint without an explicit retrospective-style decision.

**Sprint 27 reversibility check:** the Sprint 25 abel `likely_convex → non_convex` reclassification is **NOT reversible during Sprint 27** (indefinite lambda matrix is a structural property of the model — verified Sprint 26 Prep Task 2 Unknown 6.5). Sprint 27 baseline freezes scope at 142 throughout, same as Sprint 26.

---

## 6. Bucket Provenance (PR17) — Per-Failing-Model Transitions

**Per Sprint 25 retrospective recommendation PR17 (KU-34):** record per-failing-model bucket transitions so Sprint 27 acceptance-criteria evaluation can distinguish bucket churn (model moves between failure categories) from real regressions (model moves from success to failure or vice versa).

### 6.1 Models that changed bucket between Sprint 26 Day 13 (final) and Sprint 27 Day 0

**3 models, all attributed to machine-load variance at the 600s translate timeout boundary** (no Sprint 27 prep PR touched `src/`):

| Model | Sprint 26 Day 13 (final) bucket | Sprint 27 Day 0 bucket | Transition note | Translate time pre → post |
|---|---|---|---|---|
| `clearlak` | `path_syntax_error` (translates, PATH compile-fails) | `translate_timeout` | Bucket churn (recurring — same pattern as Sprint 26 Day 0 baseline) | 128.6s → 600.1s |
| `ganges` | `path_syntax_error` | `translate_timeout` | Bucket churn (recurring — same pattern as Sprint 26 Day 0 baseline) | 227.3s → 600.6s |
| `srpchase` | `path_syntax_error` | `translate_timeout` | Bucket churn (newly surfaced at the boundary; Sprint 26 Day 0 had this model but the boundary-crosser then was `turkpow` not `srpchase` — exact mix depends on runner machine load) | 274.2s → 600.2s |

**All 3 still fail; net failure count is unchanged.** They moved earlier in the pipeline because the Sprint 27 Day 0 baseline run was slower than the Sprint 26 Day 13 retest (~3h10m vs ~1h26m), pushing translate times that were 128–274s into the 600s timeout. **Comparison: Sprint 26 Day 0 baseline (~3h33m, similar-speed runner) had the same kind of churn on clearlak/ganges/turkpow** — the boundary-crosser identity shifts run-to-run but the count (~3 models) is stable.

### 6.2 Per-bucket Sprint 26 Day 13 (final) → Sprint 27 Day 0 composition

#### `path_syntax_error` (17 → 14)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `clearlak` | translate_timeout | path_syntax_error | **translate_timeout** | **Churn-out** (machine variance, see §6.1) |
| `ganges` | translate_timeout | path_syntax_error | **translate_timeout** | **Churn-out** (machine variance, see §6.1) |
| `srpchase` | translate_timeout | path_syntax_error | **translate_timeout** | **Churn-out** (machine variance, see §6.1) |
| `camcge` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (Sprint 27 Priority 2 target — #1381 Pattern C Phase B redesign) |
| `cesam2` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (Sprint 27 Priority 2 target — #1381 Pattern C Phase B redesign) |
| `dinam` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (Sprint 27 Priority 1 target — #1398 Phase 0 anchor model, 2 distinct emit shapes) |
| `egypt` | path_solve_license | path_syntax_error | path_syntax_error | Sprint 27 Priority 1 #1398-affected (was path_solve_license at Sprint 26 Day 0 before Day 1 PR #1379 Phase A regression) |
| `fawley` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (Sprint 27 Priority 5 target — #1356 comp_up subset/superset; Phase 0 authored in Sprint 27 Prep Task 2) |
| `ferts` | path_solve_license | path_syntax_error | path_syntax_error | Sprint 27 Priority 1 #1398-affected (same as egypt) |
| `gangesx` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed; Sprint 27 Priority 1 #1398-affected |
| `indus` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (pre-existing path_syntax_error; not in #1398 scope) |
| `otpop` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (Sprint 27 Priority 5 target — #1357 comp_up subset/superset; Phase 0 authored in Sprint 27 Prep Task 2) |
| `qdemo7` | compare_match | path_syntax_error | path_syntax_error | **Phase A gate-overreach regression** — Sprint 27 Priority 1 #1398 primary target (+1 firm Solve / +1 firm Match recovery once fixed) |
| `sample` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (pre-existing; not in #1398 scope) |
| `shale` | path_solve_license | path_syntax_error | path_syntax_error | Sprint 27 Priority 1 #1398-affected (same as egypt) |
| `turkey` | path_syntax_error | path_syntax_error | path_syntax_error | Stayed (pre-existing; not in #1398 scope) |
| `turkpow` | translate_timeout | path_syntax_error | path_syntax_error | Stayed (NOT churned this run; Sprint 27 Priority 1 #1398-affected per Sprint 26 Day 13 mixed-attribution) |

#### `path_solve_terminated` (5 → 5)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `dyncge`, `elec`, `maxmin`, `tricp`, `twocge` | path_solve_terminated | path_solve_terminated | path_solve_terminated | All stayed |

#### `model_infeasible` (4 → 4)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `agreste`, `cesam`, `lnts` | model_infeasible | model_infeasible | model_infeasible | All stayed |
| `camshape` | model_infeasible | model_infeasible | model_infeasible | Stayed (Sprint 27 Priority 7 target — #1388 Locally Infeasible; Phase 0 authored in Sprint 27 Prep Task 2 with PROCEED-with-condition verdict pending Sprint 27 Day 0/1 NLP-warm-start test) |

#### `path_solve_license` (5 → 5)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `egypt`, `ferts`, `shale` | path_solve_license | path_syntax_error | path_syntax_error | (Not in this bucket post-Sprint-26 — moved to path_syntax_error due to Sprint 26 #1398 Phase A gate regression; see path_syntax_error table) |
| `glider`, `robot`, `sroute`, `tabora`, `tfordy` | path_solve_license | path_solve_license | path_solve_license | All stayed (Sprint 27 Priority 1 #1398-affected: `tfordy`, `sroute`) |

#### `translate_timeout` (4 → 7)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `iswnm`, `mexls`, `nebrazil`, `sarf` | translate_timeout | translate_timeout | translate_timeout | All stayed (Sprint 27 Priority 3 candidates via #1385 Option 1 short-circuit redesign) |
| `clearlak`, `ganges` | translate_timeout | path_syntax_error | translate_timeout | **Churn-back** (machine variance — see §6.1) |
| `srpchase` | translate_timeout | path_syntax_error | translate_timeout | **Churn-back** (machine variance — see §6.1) |
| `turkpow` | translate_timeout | path_syntax_error | path_syntax_error | (Not in this bucket post-Sprint-26 Day 13 — stayed at path_syntax_error this run; runner just barely fast enough vs srpchase which crossed) |

#### `translate_internal_error` (4 → 4)

| Model | Sprint 26 Day 0 | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|---|
| `danwolfe`, `decomp`, `saras` | translate_internal_error | translate_internal_error | translate_internal_error | Multi-solve drivers (gated by #1270 / Sprint 25 Day 12 #1270 Approach A) |
| `mine` | translate_internal_error | translate_internal_error | translate_internal_error | `IndexOffset(ParamRef)` (#1224 — Sprint 27 Priority 6) |

#### `compare_mismatch` (38 → 38)

All 38 are `model_optimal` or `model_optimal_presolve` solves where the MCP solution doesn't match the NLP solution. Sprint 27 doesn't directly target the mismatch cohort except via emit-bug fixes that may incidentally improve specific mismatch cases.

Models (Sprint 27 Day 0): `catmix`, `cclinpts` (Sprint 27 Priority 7 target — #1387 condition-guard/sign bug), `chain`, `chakra`, `chenery`, `china`, `circle`, `cpack`, `etamac`, `harker` (Sprint 27 Priority 1 #1398-affected, mismatch sub-bucket), `hhfair`, `himmel16`, `imsl`, `irscge`, `kand` (Sprint 27 Priority 3 target — #1390 per-instance enumeration redesign), `launch` (Sprint 27 Priority 4 target — #1378 PATH-numerics divergence), `like`, `lmp2`, `lrgcge`, `marco`, `markov`, `mathopt1`, `mathopt4`, `mingamma`, `moncge`, `paperco`, `polygon`, `prodsp2`, `qsambal` (Sprint 27 Priority 1 #1398-affected), `robert`, `sambal` (Sprint 27 Priority 1 #1398-affected), `spatequ`, `srkandw`, `stdcge`, `tforss`, `trig`, `weapons`, `worst` (38 total)

#### `compare_skipped` (6 → 6)

| Model | Sprint 26 Day 13 (final) | Sprint 27 Day 0 | Note |
|---|---|---|---|
| `aircraft`, `apl1p`, `apl1pca`, `ps10_s_mn`, `ps5_s_mn`, `senstran` | compare_skipped | compare_skipped | All stayed — comparison harness skips these (typically `ps*_s*` due to `non_convex` runtime filter; aircraft/apl1p/apl1pca/senstran due to NLP-side comparison-skip conditions) |

### 6.3 Why bucket-provenance matters for Sprint 27 acceptance evaluation (per PR17)

Sprint 27's acceptance criteria (per PROJECT_PLAN.md §Sprint 27) must be evaluated with bucket provenance because:

- **Priority 1 (#1398) recovery is bucket-transition-positive**: 15 models currently in path_syntax_error / path_solve_license / mismatch should return to their Day 0 bucket (e.g., qdemo7 compare_match, egypt path_solve_license, sambal mismatch); the headline metric improvement requires distinguishing fix-driven transitions from regression-driven transitions.
- **Translate target ≥ 135**: net +1 from Day 0 (131). Sprint 27 Priority 3 #1385 unblocks iswnm/mexls/nebrazil/sarf if Option 1 short-circuit lands; bucket provenance distinguishes "translate recovery via #1385" from "machine-variance translate-timeout flake on the boundary models" (clearlak/ganges/srpchase/turkpow — Sprint 26 + Sprint 27 historical pattern).
- **Match target ≥ 66**: +7 from Day 0 (59). Multiple priorities contribute: #1381 (+2 camcge/cesam2), #1398 qdemo7 recovery (+1), #1357 (+1), #1356 (+1), #1378 launch (+1), #1390 kand (+1). PR17 bucket provenance ensures we don't double-count a model that transitions through multiple buckets across consecutive Day-N retests.

The bucket-provenance column in this baseline is the explicit input to Sprint 27 Day-N evaluation per PR17.

---

## 7. Sprint 27 Target Metrics (from PROJECT_PLAN.md §Sprint 27)

| Metric | Sprint 27 Day 0 baseline | Sprint 27 Target | Δ Required | Source |
|---|---|---|---|---|
| Parse success | 142/142 | ≥ 142/142 | maintain | PROJECT_PLAN.md Sprint 27 Acceptance Criteria |
| Translate success | 131/142 | ≥ 135/142 | +4 (note: PROJECT_PLAN target was +1 vs Day 0's anticipated 134; revised to +4 here vs actual Day 0 of 131, since machine-variance churn left Translate at 131. Net "real" target unchanged: recover the 3 churn models AND add +1 net via #1385/#1224) | PROJECT_PLAN.md Sprint 27 |
| Solve success | 103 | ≥ 111 | +8 (+6 firm + 2 conditional) | PROJECT_PLAN.md Sprint 27 |
| Solution match | 59 | ≥ 66 | +7 | PROJECT_PLAN.md Sprint 27 |
| path_syntax_error | 14 | ≤ 6 | −8 (PROJECT_PLAN said −11 vs anticipated 17; revised to −8 vs actual 14, since churn-out models are now in translate_timeout. Net effect same: target path_syntax_error count ≤ 6) | PROJECT_PLAN.md Sprint 27 |
| path_solve_terminated | 5 | ≤ 5 | maintain | PROJECT_PLAN.md Sprint 27 |
| model_infeasible | 4 | ≤ 3 | −1 (via camshape #1388) | PROJECT_PLAN.md Sprint 27 |
| Tests | 4,737 | ≥ 4,750 | +13 | PROJECT_PLAN.md Sprint 27 |

**Note on Translate target ambiguity:** PROJECT_PLAN.md Sprint 27 §Acceptance Criteria said "Translate ≥ 135/142 (up from 134/142; +1 via #1385 unblocking iswnm/mexls/nebrazil/sarf OR #1224 unblocking mine)". The "from 134" framing anticipated no machine-variance churn at Sprint 27 Day 0. Actual Day 0 is 131 due to clearlak/ganges/srpchase churn-out. Two interpretations:

- (a) **Hold absolute target ≥ 135**: requires recovery of the 3 churn models AND +1 net via #1385/#1224 = +4 from Day 0
- (b) **Hold relative target +1**: target becomes ≥ 132 from Day 0; the 3 churn-back recoveries are gravy

Sprint 27 retrospective should clarify this. **For Day-N evaluation: use bucket provenance to distinguish #1385 / #1224 fix wins from machine-variance churn-back recoveries; this lets the Sprint 27 final retrospective categorize as fix-driven vs run-variance vs both.**

**Delta breakdown (per CHANGELOG.md Sprint 26 Summary §"Sprint 27 Recommendations" + PROJECT_PLAN.md Sprint 27 §Acceptance Criteria):**

- **Solve +6 firm**: #1381 camcge/cesam2 [+2] + #1398 qdemo7 recovery [+1] + #1357 otpop [+1] + #1356 fawley [+1] + #1388 camshape [+1]
- **Solve +2 conditional**: #1385 [+1 conditional on iswnm/mexls/nebrazil/sarf subsequently solving] + #1224 [+1 conditional on mine subsequently solving cleanly]
- **Match +7**: #1381 [+2] + #1398 qdemo7 [+1] + #1357 [+1] + #1356 [+1] + #1378 launch mismatch→match [+1] + #1390 kand mismatch→match [+1]
- **path_syntax_error −8**: #1398 [up to 9 currently-affected models recover — of which 11 are in path_syntax_error (qdemo7/egypt/ferts/shale/dinam/fawley/gangesx/turkpow at Day 0, plus the 3 churn-backs once they translate again)] + #1381 [camcge, cesam2] + #1357 [otpop]; well above the 8 needed to reach ≤ 6

---

## 8. Acceptance Criteria (from PREP_PLAN.md §Task 3)

- [x] Full pipeline run completed within budget allowance (1–3.5h target) → completed in ~3h10m (within budget)
- [x] All 8 acceptance-criteria metrics recorded → Parse / Translate / Solve / Match + 4 `outcome_category` counts in §2
- [x] Bucket-provenance column added per PR17 → §6 (per-failing-model Sprint 26 → Sprint 27 transitions)
- [x] Scope-freeze decision documented → §5 (carried forward from Sprint 26 §5)
- [x] Unknown 1.1 verified and updated in KNOWN_UNKNOWNS.md → all 15 #1398-affected models confirmed at non-compare_match buckets (10 path_syntax_error, 2 translate_timeout churn-back ganges/srpchase, 2 path_solve_license tfordy/sroute, 3 compare_mismatch sambal/qsambal/harker — solves `model_optimal` but `compare_mismatch`)

---

## 9. Related Documents

- `docs/planning/EPIC_4/SPRINT_27/PREP_PLAN.md` §Task 3 — this task's specification.
- `docs/planning/EPIC_4/SPRINT_27/KNOWN_UNKNOWNS.md` §Unknown 1.1 — verification results recorded there.
- `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` — format this baseline extends; §5 / §5.1 documents the abel reclassification policy.
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_LOG.md` Day 13 — informal bucket-provenance source for §6 Sprint 26 Day 13 (final) column.
- `docs/planning/EPIC_4/SPRINT_26/SPRINT_RETROSPECTIVE.md` §"Sprint 27 Recommendations" — full per-priority rationale for §7 Sprint 27 targets.
- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 27 — canonical source-of-truth for §7 target metrics.
