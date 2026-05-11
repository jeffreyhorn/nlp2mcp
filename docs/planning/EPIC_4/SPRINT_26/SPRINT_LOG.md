# Sprint 26 Log

**Sprint:** 26 — Pattern C Generalization + Pattern A Reclassification + Phase E Carryforward + Translation Timeout Option 1 Short-Circuit + AD Residuals (#1334 / #1335)
**Duration:** 14 days (Day 0 – Day 13)
**Baseline:** Parse 142/142, Translate 130/142, Solve 104, Match 60, Tests 4,735 (frozen Day 0 per Sprint 26 prep Task 9 + PR15 scope freeze; see [`BASELINE_METRICS.md`](BASELINE_METRICS.md))

---

## Sprint 26 Targets

| Metric | Baseline (142-scope) | Target | Stretch |
|---|---|---|---|
| Parse | 142/142 (100%) | ≥ 142/142 | — |
| Translate | 130/142 (91.5%) | ≥ 135/142 | ≥ 137/142 |
| Solve | 104 | ≥ 108 | ≥ 110 |
| Match | 60 | ≥ 64 | ≥ 66 |
| path_syntax_error | 9 | ≤ 6 | ≤ 4 |
| path_solve_terminated | 5 | ≤ 5 | ≤ 4 |
| model_infeasible | 4 | ≤ 4 | ≤ 3 |
| Tests | 4,735 | ≥ 4,750 | — |

See [`PLAN.md`](PLAN.md) for the full 14-day schedule and [`prompts/PLAN_PROMPTS.md`](prompts/PLAN_PROMPTS.md) for per-day execution prompts.

---

## Daily Progress

### Day 0 — Setup & Kickoff

**Status:** COMPLETE (2026-05-11)
**Branch:** `sprint26-day0-kickoff`

| Task | Status |
|---|---|
| Verify Day 0 baseline matches `BASELINE_METRICS.md` §2 | ✅ Parse 142/142, Translate 130/142, Solve 104, Match 60 (exact match — all 9 buckets in §2.1/§2.2/§2.3 match live `gamslib_status.json`) |
| Initialize `SPRINT_LOG.md` Day 0 entry | ✅ This entry |
| Confirm GitHub issue labels (`sprint-26` + `sprint-27`) | ✅ See §"Issue label confirmation" below |
| Read Task 3–10 prep-task outputs as briefing material | ✅ All 7 documents read; key findings captured in §"Prep-task briefing summary" below |

#### Baseline verification (per-bucket)

| Bucket | BASELINE_METRICS.md | Day 0 live | Match |
|---|---|---|---|
| `compare_match` | 60 | 60 | ✅ |
| `compare_mismatch` | 38 | 38 | ✅ |
| `compare_skipped` | 6 | 6 | ✅ |
| `solve_path_syntax_error` | 9 | 9 | ✅ |
| `solve_path_solve_license` | 8 | 8 | ✅ |
| `solve_path_solve_terminated` | 5 | 5 | ✅ |
| `solve_model_infeasible` | 4 | 4 | ✅ |
| `translate_timeout` | 8 | 8 | ✅ |
| `translate_internal_error` | 4 | 4 | ✅ |
| **Total in-scope** | **142** | **142** | ✅ |

Headline metrics: Parse 142/142, Translate 130/142, Solve 104, Match 60 — exact match to `BASELINE_METRICS.md` §2 frozen by PR #1373 (commit `f1cdb91f`).

#### Issue label confirmation

**`sprint-26` label** (Sprint 26 Day 1–13 in-scope work):

- Priority 1 (Pattern C generalization): #1306, #1307, #1354, #1355
- Priority 2 (Pattern A cohort reclassification — mechanical closures per Task 4): #1138, #1139, #1140, #1142, #1145, #1150
- Priority 3 (Pattern E carryforward — kand only per Task 5): #1141, #1144, #1147
- Priority 4 (Translation timeout Option 1 short-circuit): #885, #931, #932, #1185, #1228
- Priority 5 (AD residuals): #1334, #1335

**`sprint-27` label** (deferred work — must NOT carry `sprint-26`):

- #1357 (otpop `comp_up` subset/superset; deferred per Task 7 AD_RESIDUALS_RECAP.md)
- #1356 (fawley `comp_up`; deferred per Task 4 PATTERN_A_RECLASSIFICATION_PLAN.md)
- #1374 (emit duplicate-init bugs; surfaced during Task 9 PR review)
- #1224 (mine `ParamRef` IndexOffset; deferred per Task 6 DESIGN_OPTION_1_SHORT_CIRCUIT.md)

**Label-state fix-up performed during Day 0** (verified all 20 `sprint-26` issues correctly labeled; the 4 deferrals needed correction):

| Issue | Before | After |
|---|---|---|
| #1357 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |
| #1356 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |
| #1374 | (no sprint label) | `sprint-27` added |
| #1224 | `sprint-26` | `sprint-27` (created label; `sprint-26` removed) |

New `sprint-27` label created on the repo (color `0E8A16`, matching `sprint-25` / `sprint-26` convention). Final verification confirmed all 4 deferrals carry `sprint-27` only.

#### Prep-task briefing summary

All 7 prep-task outputs read as Sprint 26 briefing material (each drives one or more day-level prompts):

| Document | Drives | Key finding |
|---|---|---|
| `PATTERN_C_HYPOTHESIS_VALIDATION.md` (Task 3) | Day 1, Days 3–4 | **REPLAN**: Priority 1 split into Phase A (Day 1 — restore #1306 launch fix via consolidated zero-offset builder rewrite, removes #1351 rollback) + Phase B (Days 3–4 — generalize gate to camcge + cesam2). fawley + otpop reclassified out of Priority 1. |
| `PATTERN_A_RECLASSIFICATION_PLAN.md` (Task 4) | Day 6 | 6 cohort issues = 4 mechanical closures + 1 close-and-refile + 1 forward-link to Priority 1 PR. ~1.5h GitHub-only work. |
| `PATTERN_E_STATUS.md` (Task 5) | Day 6 | Scope reduced 3 → 1 model (kand alias-AD). catmix and camshape closures are mechanical. |
| `DESIGN_OPTION_1_SHORT_CIRCUIT.md` (Task 6) | Day 8 | Patch sites confirmed in `src/ad/index_mapping.py::enumerate_equation_instances`; ~4–6h implementation budget; projected +1–2 Translate from srpchase. |
| `AD_RESIDUALS_RECAP.md` (Task 7) | Days 8–10 | #1334 fix-site corrected to `_add_indexed_jacobian_terms:4228` (not scalar-only `_add_jacobian_transpose_terms_scalar:5421`). #1357 explicitly NOT subsumed; deferred to Sprint 27. |
| `DESIGN_PR19_SOLVE_TIME_CI.md` (Task 8) | Day 11 | `.github/workflows/pr19-emit-solve-validation.yml` design; PATH solver under 30s budget on 11 Tier 0/1 canaries; GAMS demo install in CI. |
| `BASELINE_METRICS.md` (Task 9) | Day 13 | Day 0 baseline frozen + bucket-provenance column (PR17) for Day 13 retest comparison. 3 Day-0 machine-variance churn-outs (clearlak / ganges / turkpow) tracked separately. |

Sprint 25 carryforward KUs (KU-33 through KU-36) referenced in `PLAN.md`:

- KU-33 (Pattern C generalization) → Days 1–5 (Task 3 drives)
- KU-34 (bucket churn dominates `path_syntax_error`) → Day 13 retest comparison (PR17 evaluation)
- KU-35 (Sprint 25 PR #1351 launch rollback) → Day 1 Phase A
- KU-36 (otpop `$171` vs `$141`) → Days 8–10 Priority 5 + Sprint 27 #1357 deferral

#### Notes

- All 11 Sprint 26 prep tasks ✅ COMPLETE (PRs #1365, #1366–#1373, #1375, #1376). Final Prep-Task Status table in `PREP_PLAN.md` §"Final Prep-Task Status".
- All 26 Sprint 26 Known Unknowns (KUs 1.1–6.5) ✅ VERIFIED in `KNOWN_UNKNOWNS.md`.
- Day 0 commit + PR ships this `SPRINT_LOG.md` initialization only; no `src/` changes.

---

### Day 1 — Priority 1 Phase A: Restore Launch Fix (Consolidated Zero-Offset Builder Rewrite)

**Status:** COMPLETE (2026-05-11)
**Branch:** `sprint26-day1-pattern-c-phase-a`

| Task | Status |
|---|---|
| Diff #1306 vs #1351 to identify consolidator code path | ✅ Identified: `_add_indexed_jacobian_terms` gate site (`src/kkt/stationarity.py:4318–4346`) + downstream offset-group consolidation. #1351 hardcoded `allow_nonzero_offsets = True`; #1306 had the predicate-based gate. |
| Implement the rewrite per Sprint 25 SPRINT_LOG.md Day 11 follow-up | ✅ New helpers `_find_eq_domain_index_in_expr`, `_find_pattern_c_alias_sum`, `_apply_pattern_c_swap_to_term`, `_expr_references_var`. The transform applies an alias↔eq-domain swap to the auto Sum-wrapped term so the consolidated emit shape is the GAMS-equivalent of the target `sum(ss$ge(s,ss), -nu_dweight(ss))`. |
| Re-enable Pattern C gate; capture `pattern_c_info` for transform | ✅ Removed `allow_nonzero_offsets = True` hardcode and the no-op `if eq_def_for_gate is not None: pass` branch. Restored the original #1306 gate logic with the additional `_expr_references_var(sum.body, var_name)` check (prevents spurious firing on variables outside the alias sum — discovered during initial impl when `stat_weight(s)` regressed to `nu_dweight(ss)`). |
| Tier 0 dispatch canary byte-identical | ✅ Byte-identical to `data/gamslib/mcp/dispatch_mcp.gms`. |
| Tier 1 canary (10 models) byte-identical | ✅ 10/10 byte-identical to golden artifacts (quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive). The `$cond`-required predicate stays narrow — does NOT fire on plain-alias enumeration shapes like quocge's `sum(i, ax(i,j)*pq(i))`. |
| Re-enable xfail test + strengthen assertions | ✅ `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets` xfail decorator removed; assertions extended to check `nu_dweight(ss)` present, `nu_dweight(s)` absent, `ge(s,ss)` present. Both Pattern C unit tests pass. |
| Translate launch fresh; verify stat_iweight body shape | ✅ Emit: `sum(ss, ((-1) * 1$(ge(s,ss))) * nu_dweight(ss))` (single consolidated term, alias-indexed mult, swapped condition). All 5 phantom-offset `nu_dweight(s±k)` terms eliminated. Same fix applies to `stat_pweight`. |
| PR14 obligation: regenerate `data/gamslib/mcp/launch_mcp.gms` | ✅ Regenerated; included in PR diff. |
| `make typecheck && make lint && make format && make test` | ✅ 4,737 passed, 10 skipped, 1 xfailed (above ≥ 4,750 Sprint 26 target — counts updated upward by the strengthened Pattern C test + new shape-recovery test). |

#### Launch PATH solve regression (deferred to Sprint 27 #1378)

Phase A's mathematically correct KKT emit produces a different KKT system from the Sprint 25 #1351 over-counted form. PATH converged on the over-counted system (MODEL STATUS 1 Optimal, obj=2731.711) but stalls on the correct system (MODEL STATUS 5 Locally Infeasible, 6194 iterations, `defvt` complementarity residual ~3.2e+04).

- **Mathematical verification:** Resolved Phase A `stat_iweight(stage-3)..  ... - nu_dweight(1) - nu_dweight(2) - nu_dweight(3) ... =E= 0` matches the hand-derived `-sum_{k<=s} nu_dweight(k)` from the Lagrangian.
- **Root cause:** Sprint 25 #1351 emitted `stat_iweight(stage-s)..  ... - card({ss:ss>=s})*sum_k nu_dweight(k) + ...` (per-row weighted; same primal but DIFFERENT multiplier system). PATH found a numerical fix for the wrong system that doesn't transfer to the right one.
- **Filed:** Sprint 27 issue #1378 ("launch PATH solve regresses to MODEL STATUS 5 with mathematically correct Phase A KKT") with `sprint-27` label, investigation paths: PATH initial-point / preprocessing tuning, NLP-warm-start, sign/scaling refinement in `_apply_pattern_c_swap_to_term`.
- **Day 5 Checkpoint 1 impact:** `PLAN.md` updated — "launch PATH solve to MODEL STATUS 1" is now a stretch row (does not count toward GO/CONDITIONAL GO/NO-GO routing); the gating criteria are camcge + cesam2 + Phase A landing + canaries (5 rows, ≥ 4 of 5 to GO).

#### Notes

- The Pattern C gate predicate (`_body_has_index_offset_on_sets` + the new variable-scope check) is conservative — requires the source body to have an aliased conditional sum referencing the equation's domain (launch shape only). Phase B (Days 3–4) broadens the gate to plain-alias (camcge) and `sameas`-decomposed (cesam2) variants.
- Day 1 builds on `_rewrite_subset_to_superset` for the alias↔eq-domain swap — a single rename map `{alias: eq_dom, eq_dom: alias}` works because the helper does single-pass per-node lookups (no chained re-application).

---
