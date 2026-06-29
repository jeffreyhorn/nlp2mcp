# Sprint 29 Log

**Sprint:** 29 (Sprint 28 carryforwards + cold-convex robustness + AD/KKT backlog + Epic-5 scoping)
**Plan:** `PLAN.md` · **Prompts:** `prompts/PLAN_PROMPTS.md` · **Baseline:** `BASELINE_METRICS.md`
**Day-0 baseline (= Sprint 28 final):** Parse 142 · Translate 135 · Solve 107 · Match 92 · model_infeasible 7 · Tests ~4,935.
**Targets:** Solve ≥ 109 (mine + rocket, both REPLAN-gated) · Match maintain ≥ 92 / stretch ≥ 96 (genuine floor 68 → up) · model_infeasible ≤ 5 · Translate ≥ 135 · Tests ≥ 4,960 · determinism ×3 seeds.

## Cumulative Metrics Tracker

| Metric | Day 0 | Day 5 (CP1) | Day 10 (CP2) | Day 13 (final) | Target |
|---|---|---|---|---|---|
| Solve | 107 | — | — | — | ≥ 109 |
| Match (as-measured) | 92 | — | — | — | ≥ 92 / stretch 96 |
| Match (genuine floor) | 68 | — | — | — | 68 → up (cold-robustness) |
| model_infeasible | 7 | — | — | — | ≤ 5 |
| Translate | 135 | — | — | — | ≥ 135 |
| Tests | ~4,935 | — | — | — | ≥ 4,960 |

---

## Day 0 — Kickoff + Day-0 Traces (2026-06-29)

**Scope:** baseline confirmation + Day-0 `kkt_residual.py` traces (PR24) for the REPLAN-prone + lead tracks; fill each Phase-0 gate's `Traced Fix-Surface (Day-0)` line. **No `src/` change** (per the Day-0 prompt). Docs-only.

### Baseline gate — PASS
`git diff 803a259a..HEAD -- src/ scripts/` is **empty** → `src/` + `scripts/` are byte-identical to the Sprint-28 baseline commit, so the committed `gamslib_status.json` stands as the Day-0 baseline (Solve 107 / Match 92 / model_infeasible 7). No fresh retest (Unknown 8.3 ✅). **Tooling (Task 6):** the KKT-residual harness, divergence detector, and golden-staleness gate are present and audited-ready — no Day-0 extension.

### Day-0 harness verdicts — all 8 RE-CONFIRMED vs the prep-time (Task 4) Day-0 status

| Track | Model | Verdict | max-residual row | rel | Prep | Note |
|---|---|---|---|---|---|---|
| P1 #1443 | mine | Case b | `stat_x(4,1,1)` | 1.33 | 1.333 | ✅ convex LP, dual-transfer CONSISTENT |
| P2 #1462 | rocket | Case b | `stat_step` | 0.497 | 0.497 | ✅ `_fx_`-at-`h0` warm-start absent |
| P4/P7 #1447 | maxmin | Case b | `stat_mindist` | 1.00 | 1.000 | ✅ **hypothesis corrected** (see below) |
| P4/P7 #1146 | himmel16 | Case b | `stat_area(1)` | 2.00 | 2.000 | ✅ cyclic + objvar-gradient sign |
| P4/P7 #1143 | polygon | Case b | `stat_theta(i12)` | 0.492 | 0.492 | ✅ dropped offset-image cross-term |
| P4 (Class-A) | like | Case b | `stat_p(three)` | 2.00 | 2.0 | ✅ folds into the Class-A lead (#1447) |
| P4 (Class-A) | catmix | Case b | `stat_x1(0)` | 0.952 | 0.95 | ✅ folds into the Class-A lead |
| P6 #1236 | hhfair | **ERROR** (blocker) | — | — | `$141`/`$257` | ✅ blocker reproduced + root localized |

Every prep verdict held on current `main` — **no drift**. JSON reports in `/tmp/day0_<model>.json`.

### Traced fix-surfaces (PR24) — filled in each Phase-0 gate
- **mine #1443:** three sites pinned — `stat_x` cross-term (landed #1224) `src/kkt/stationarity.py:5562-5570`; presolve dual transfer `src/emit/emit_gams.py:1281` (`lam_pr.l = abs(pr.m)`, same-index, sign-discarding); `comp_pr` head var `x(l+1,i,j)`. Residual is in the LP row despite consistent dual transfer → the `l+1`/`±li`/`±lj` correspondence is not aligned across the three sites (corroborates Task-5 lean-REPLAN).
- **rocket #1462:** `nu_*_fx_h0` declared + used in `stat_ht/m/v` but the presolve dual-transfer block (`emit_gams.py:1281-1310`) emits **no `nu_*_fx_*` init** → starts at 0 → `stat_step` residual. Layer-4 unfix `_emit_presolve_fx_unfix` at `emit_gams.py:1090`.
- **maxmin #1447 — ⚠️ prep hypothesis CORRECTED (PR24 catch):** the dropped term is the **objective gradient `-1`** (maxmin maximizes `mindist`), not the constraint sum (the `sum((n,nn)$low, lam_mindist1a)` **is** present). Surface: the objvar stationarity assembly in `src/kkt/stationarity.py` (`build_stationarity_equations`:2090 → `_build_indexed_stationarity_expr`:2650 / objective-gradient merge :2222).
- **himmel16 #1146:** two candidate surfaces (root disambiguates Day 3) — (a) cyclic `i++1` decomposed into `i+5`$(ord≤card-5)+`i-1`$(ord>1) in `stat_x`/`stat_y` (`derivative_rules.py` circular branch ~:1866); (b) the `stat_area` `-1` objvar-defining gradient interacting with the signed `nu_areadef` transfer (raw −2.0). Integer 2.0 = 2× maxmin's 1.0.
- **polygon #1143:** clean **dropped predecessor offset-image cross-term** — `stat_theta` has the own-row gradient but not the `+0.5*r(i)*r(i-1)*cos(...)` term from the `i-1` row (where `theta(i+1)` resolves to `theta(i)`). Surface: `derivative_rules.py` non-circular successor branch (~:1989/:2022) over `j(i+1)`.
- **hhfair #1236:** `$141` blocker reproduced (13 errors); root = the dual-transfer block emits multiplier inits over the **widened `tl` domain** (`nu_budget.l(tl) = -(budget.m(tl))`) reading unpopulated `.m('0')` (set split `tl /'0'..'3'/` vs active `t /'1'..'3'/`, propagated by the domain-widened `n(tl)`). Fix surface = restrict the transfer to the active subset (`emit_gams.py:1281-1310`); verdict gated on the Day-8 compile fix.

### PR25 Day-0 tally (genuine vs methodology)
- **As-measured baseline:** Solve 107 · Match 92 (= **genuine 68 + ~24 methodology**).
- **Firm headline path:** mine (#1443) + rocket (#1462), both `model_infeasible`/MS-5 → Solve, **both REPLAN-gated** (Task 5). hhfair (#1236) the lone live +Match (gated on the compile fix).
- **Cold-convex Class-A (maxmin/himmel16/polygon/like/catmix):** all **Case b but already match warm** → **Match-neutral genuine-floor lift** (68 → up), not as-measured Match.
- **No `src/` change today** → metrics unchanged from baseline.

### Deliverables
6 Phase-0 gates updated (`docs/issues/ISSUE_{1443,1462,1447,1146,1143,1236}_*.md`) + this Day-0 SPRINT_LOG entry. Docs-only; no quality-gate-relevant source touched.
