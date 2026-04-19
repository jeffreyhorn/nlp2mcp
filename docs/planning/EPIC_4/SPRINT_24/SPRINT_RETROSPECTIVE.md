# Sprint 24 Retrospective

**Created:** 2026-04-19
**Duration:** 15 sprint days (Day 0 – Day 14)
**Sprint Goal:** Solve ≥ 95, Match ≥ 55, path_syntax_error ≤ 15, path_solve_terminated ≤ 10, model_infeasible ≤ 8, Translate ≥ 97% of parsed, Parse 100%, Tests ≥ 4,400

---

## Executive Summary

Sprint 24 met **6 of 8** acceptance criteria, a substantial improvement over Sprint 23 (1/8). The sprint's highest-leverage wins were in **error-category reduction** rather than raw solve/match rate: `path_syntax_error` dropped 23 → 6 under the original Day 13 retest (then 11 after the doubled-timeout re-retest influx), `path_solve_terminated` hit exactly 10, and `model_infeasible` hit exactly 8 (down from a baseline of 14, with **zero gross influx** — substantially outperforming the PR10 50–60% influx budget). The multi-solve-driver exclusion (decomp, danwolfe) landed cleanly as a pre-translation gate. The alias-differentiation workstream made progress but the core #1111 family (now 11 open issues relabeled `sprint-25`: #1138–#1147, #1150) was not resolved. Translate and Match were the two misses — Translate 135/143 (94.4%) vs target ≥97%, Match 54 vs target ≥55 (one short).

**Key Outcome:** 99 models solve (up from 86). 54 models match (up from 49). Parse 100% on the 143-model pipeline scope. Translate 94.4% (135/143) under the doubled-timeout re-retest. 20 PRs merged. 4,522 tests passing (+158 from baseline). Doubled-timeout experiment confirmed that translation-timeout work alone is lower-leverage than expected — the 5 recovered translates all hit `path_syntax_error` at PATH compile because of emitter/stationarity bugs in the same family that Sprint 25's alias / offset / emitter-dedup issues target.

---

## Goals and Results

### Sprint 24 Objectives (original plan)

1. :white_check_mark: Parse ≥ 147/147 (100%) — achieved: 143/143 (100% of 143-scope; scope reduced from 147 by v2.2.1 exclusions)
2. :x: Translate ≥ 143/147 (97%) — achieved: 135/143 (94.4% of 143-scope; −2.6pp below target)
3. :white_check_mark: Solve ≥ 95 — achieved: 99
4. :x: Match ≥ 55 — achieved: 54 (−1 from target)
5. :white_check_mark: path_syntax_error ≤ 15 — achieved: 11 (6 in original Day 13 retest; 11 after doubled-timeout re-retest brought 5 translate recoveries that influxed 1:1 into path_syntax_error)
6. :white_check_mark: path_solve_terminated ≤ 10 — achieved: 10 (target exactly)
7. :white_check_mark: model_infeasible ≤ 8 — achieved: 8 (target exactly; baseline was 14 triage-scope, Δ = −6)
8. :white_check_mark: Tests ≥ 4,400 — achieved: 4,522

### Metrics Summary

| Metric | Baseline (Day 0) | Target | Stretch | Final (Day 13 Addendum) | Status |
|--------|------------------|--------|---------|-------------------------|--------|
| Parse | 147/147 (100%) | ≥ 147/147 | — | **143/143 (100%)** | :white_check_mark: (scope reduced to 143) |
| Translate | 140/147 (95.2%) | ≥ 143/147 (97%) | ≥ 145/147 | **135/143 (94.4%)** | :x: −2.6pp |
| Solve | 86 | ≥ 95 | ≥ 100 | **99** | :white_check_mark: |
| Match | 49 | ≥ 55 | ≥ 60 | **54** | :x: −1 |
| path_syntax_error | 23 | ≤ 15 | ≤ 12 | **11** | :white_check_mark: stretch |
| path_solve_terminated | 12 | ≤ 10 | ≤ 8 | **10** | :white_check_mark: |
| model_infeasible | 14 (triage) | ≤ 8 | ≤ 6 | **8** | :white_check_mark: |
| Tests | 4,364 | ≥ 4,400 | — | **4,522** | :white_check_mark: +158 |

### Pipeline Scope Changes

The pipeline scope shifted from 147 → 143 models during Sprint 24 due to schema v2.2.1 exclusions:

- **2 new `multi_solve_driver_out_of_scope`** exclusions (`decomp`, `danwolfe`) via PR #1265's validator gate
- **2 other models** moved out of the in-scope convex-continuous set

Targets were set against the 147-model baseline; acceptance percentages are evaluated on the current 143-scope (so `≥ 97%` translates to `≥ 139/143`).

### Final Error Category Breakdown

**Translate failures (baseline 7 → Day 13 Addendum 8 out of 143 parsed):**

Baseline values below are the end-of-Sprint-23 counts from `SPRINT_23/SPRINT_RETROSPECTIVE.md` (147-pipeline scope), since Sprint 24 inherited the Sprint 23 final state as its Day 0.

| Category | Baseline (end of S23, 147-scope) | Day 13 (pre-bump, 143-scope) | Day 13 Addendum (post-bump, 143-scope) | Delta vs baseline |
|----------|----------|-------------------|------------------------------|---------------------|
| timeout | 6 | 10 | **5** | −1 |
| internal_error | 1 | 3 | 3 | +2 |

The `timeout` row spiked to 10 during Sprint 24 (two models that had been on the edge of the 300s budget in Sprint 23 regressed under the then-current parser state) before the PR #1274 timeout doubling brought it back down to 5. The `internal_error` delta of +2 is tracked (mostly `mine` re-surfacing after the SetMembershipTest fix from Sprint 23 regressed under interactions with Sprint 24 work).

**Solve failures (baseline 54 → Day 13 Addendum 36 out of 135 translated):**

Baseline values below are the end-of-Sprint-23 counts on the 147-pipeline scope. Sprint 24's pipeline-scope `model_infeasible` baseline is **11**; the **14** used elsewhere in this retrospective is the triage-scope baseline from PLAN.md, which includes models outside the 147-scope that later moved into the 143-scope (see footnote ⁵ in PROJECT_PLAN.md Rolling KPIs).

| Category | Baseline (end of S23, 147-scope) | Day 13 | Day 13 Addendum | Delta vs baseline |
|----------|----------|--------|------------------|---------------------|
| path_syntax_error | 23 | 6 | 11 | −12 |
| path_solve_terminated | 12 | 10 | 10 | −2 |
| model_infeasible | 11 | 8 | 8 | −3 (pipeline-scope) / −6 (triage-scope) |
| path_solve_license | 8 | 7 | 7 | −1 |

### model_infeasible Accounting (PR7)

- **Baseline:** 14 models (triage scope)
- **Gross fixes:** 6 (cesam2, qabel, abel, stdcge, lrgcge, moncge recovered)
- **Gross influx:** 0 — **no baseline-solving model became infeasible during Sprint 24**
- **Net change:** −6 (14 → 8)

**Current 8 infeasible:**
- **Alias-related (3):** camshape, cesam, korcge → tracked under alias-differentiation carryforward (#1138–#1147, #1150)
- **PATH convergence / Category B (5):** agreste, chain, fawley, lnts, robustlp → tracked under KU-18 as likely requiring warm-start / PATH-parameter work

**Zero gross influx was a significantly better outcome than the PR10 50–60% budget forecast.**

---

## What Went Well

### 1. Multi-Solve Driver Exclusion (PR #1265)

Added a three-condition pre-translation gate (`src/validation/driver.py::validate_single_optimization`) that refuses Dantzig–Wolfe / column-generation / primal-dual driver scripts whose converged objective is an iterative fixed point rather than any single NLP's answer. Two in-scope targets (`decomp`, `danwolfe`) are now cleanly excluded with exit code 4, a `--allow-multi-solve` dev escape hatch, and a `multi_solve_driver_out_of_scope` taxonomy entry in the v2.2.1 schema migration. Regression-guarded by 13 tests covering `ibm1` and `partssupply` as false-positive canaries.

### 2. path_syntax_error Halved (Stretch Target Met Initially)

The Day 13 retest showed `path_syntax_error` at 6 (stretch target ≤12 met). The Day 13 addendum brought it back to 11 due to translate-recovery influx, but that still comfortably meets the primary ≤15 target. Biggest contributors: the partssupply $ifThen / dollar_cond emitter fix (PR #1264) and the multi-solve-driver exclusion removing 2 always-failing models from the category.

### 3. model_infeasible Target Met With Zero Influx

Recovered 6 models from the baseline model_infeasible count (14 → 8) with no regressions — a rare outcome. The PR10 influx budget (50–60%) proved dramatically over-conservative for this sprint. The remaining 8 cluster cleanly into alias-related (3) and PATH-convergence / Category B (5), both tracked for Sprint 25.

### 4. Lark Grammar Ambiguity Root-Cause Fix (PR #1267)

The long-standing `test_model_all_except_single` CI failure was traced to a Lark 1.1.9 vs 1.2+ grammar-ambiguity behavior difference (not xdist / parser-state as originally hypothesized). A defensive code-level fix in `src/ir/parser.py::_extract_model_refs` makes the IR builder robust to either Lark alternative, unblocking CI green for the first time in 5+ main merges. Useful process lesson captured in KU-28 about `requirements.txt` pinning vs `pyproject.toml` lower bounds.

### 5. Sprint Planning Infrastructure Continued to Scale

15-day schedule with 2 checkpoints, day-by-day prompts, and 26 prep-time Known Unknowns (+ 6 more end-of-sprint discoveries) continued to provide effective structure. Checkpoint 1 and Checkpoint 2 both drove scope decisions that kept the sprint on track. The close-prep pass (Day 12) cleanly separated deferred work into Sprint 25 tracking issues.

### 6. 20 PRs Merged, Quality Gate Green Throughout

20 merged PRs across the sprint: per-model fixes (partssupply, turkey, china, feedtray, fawley, harker, rocket), architectural work (multi-solve gate, alias progress), close-prep (Day 12 issues, Day 13 retests), and tooling (doubled timeouts). Full test suite grew from 4,364 → 4,522 (+158 tests) with no sustained regressions.

---

## What Could Be Improved

### 1. Alias Differentiation Didn't Fully Land

The #1111 / alias-differentiation family was identified as the single highest-leverage workstream for Sprint 24, but only partial progress landed. 11 open alias issues (#1138–#1147, #1150) are deferred to Sprint 25. The sprint's Match result (54 vs target 55) is a direct consequence — Match is essentially entirely blocked on alias-differentiation correctness. Future sprints targeting Match should budget the architectural work more realistically.

### 2. Translate-Recovery Influx Was 100% (Worse Than PR10's 50–60%)

The Day 13 addendum's doubled-timeout experiment confirmed that **every one** of the 5 newly-translating models (ganges, gangesx, ferts, clearlak, turkpow) went straight to `path_syntax_error` — a 100% influx rate, much higher than the 50–60% PR10 budget projected. This is consistent with the models being previously timeout-excluded not because they were on the edge of tractability, but because the same underlying translator / emitter bugs that cause their PATH compile failures also slow down their translation. **Translation-timeout work has lower near-term match-rate leverage than originally scoped.**

### 3. Non-Deterministic Parser Bug Surfaced Late

A parser non-determinism bug in multi-row-label tables like `(low,medium,high).ynot` (#1283) was only discovered at Day 13 Addendum review — three back-to-back CLI runs on the same `chenery.gms` produced 2 correct + 1 corrupted outputs. This has been quietly corrupting `chenery_mcp.gms` on some pipeline runs throughout the sprint (and possibly Sprint 23), potentially confounding the #1177 chenery investigation. Future sprints should add byte-stability regression tests across multiple `PYTHONHASHSEED` values.

### 4. Scope Shift Mid-Sprint Created Accounting Complexity

The pipeline scope moving from 147 → 143 during Sprint 24 (v2.2.1 exclusions) made target-vs-actual evaluation ambiguous. The `model_infeasible` baseline had to be stated as 14 (triage-scope) rather than 11 (original pipeline scope) because several baseline infeasibles were outside the 147-scope but inside the 143-scope. Future sprints should freeze exclusions before Day 0 or explicitly track both the original and adjusted scopes.

### 5. Translation Timeouts Remain Real for 5 Models

Under the doubled 600s translate budget, **5 models still time out**: `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`. These are genuinely intractable at the current scale and would need algorithmic improvements (sparse Jacobian, profiling-driven optimization) rather than simple budget increases.

---

## What We'd Do Differently

### 1. Start Alias Differentiation on Day 1 (as originally planned) and Defend the Time

The plan called for alias work Days 1–7, but Days 4–7 were absorbed by other urgent fixes. Protecting that time block — treating it like a meeting you can't move — is necessary because the architectural complexity doesn't shrink to fit a compressed schedule.

### 2. Set Tighter Translate Targets Against Realistic Recovery Ceiling

Sprint 24's ≥143/147 (97%) translate target assumed 3 recoveries in Sprint 24 cycle. Achieved +5 translates under doubled-timeout experiment but 0 reached solve. Future translate targets should include a **"translate + solve"** variant to avoid rewarding recoveries that don't improve end-to-end pipeline results.

### 3. Run the Full Pipeline Multiple Times at Each Milestone

The non-determinism in #1283 means any single pipeline run can silently produce corrupted output for models using multi-row-label tables. Treat single pipeline runs as suspect for affected models; re-run 3× and use the majority result, or fix #1283 before trusting metrics.

### 4. Promote Emitter-Level Hygiene Work Earlier

Days 11–13 review surfaced 7 new emitter/stationarity bugs (#1275–#1281, #1283) in previously-committed artifacts. These were latent throughout the sprint. Running a dedicated "read the generated MCP" review pass mid-sprint would have caught them earlier and avoided the Day 13 review round of filing 7 tracking issues.

---

## Sprint 25 Recommendations

Based on Sprint 24 findings and the 18+ issues labeled `sprint-25`:

### Priority 1: Alias-Aware Differentiation Carryforward (#1138–#1147, #1150)

11 open issues affecting the same ~20 models identified in Sprint 23. The single highest-leverage workstream for improving Match rate. Sprint 25 should start this on Day 1 and reserve 8–12 days for the full scope. KU-29 / KU-30 / KU-31 / KU-32 in `SPRINT_24/KNOWN_UNKNOWNS.md` capture the open sub-questions.

### Priority 2: Emitter/Stationarity Bug Backlog (#1275–#1281, #1283)

8 issues surfaced by the Day 13 review round covering:
- **#1275** — presolve $include absolute paths
- **#1276** — fawley duplicate `.fx` emission
- **#1277** — twocge `stat_tz` mixed offsets
- **#1278** — twocge `ord(r) <> ord(r)` tautology
- **#1279** — robustlp `defobj(i)` scalar-equation widening
- **#1280** — mathopt4 unquoted UELs with dots
- **#1281** — lmp2 duplicate `Parameter` declarations
- **#1283** — non-deterministic multi-row-label table parsing

Most are small-to-medium-effort; collectively they are the leverage point for the 5 "recovered translates that don't solve" (ganges, gangesx, ferts, clearlak, turkpow). Recommend pairing #1283 (non-determinism) very early — it may be confounding other investigations.

### Priority 3: Translation Timeout — Algorithmic, Not Budgetary (#1169, #1185, #1192)

5 remaining hard timeouts (iswnm, mexls, nebrazil, sarf, srpchase) need algorithmic improvements, not further budget increases. KU-19 / KU-20 in SPRINT_24 / SPRINT_24 KNOWN_UNKNOWNS.md call out profiling + sparse Jacobian as candidate directions. Low near-term Match leverage per the addendum finding; prioritize after #1275–#1283.

### Priority 4: Multi-Solve Gate Extension (#1270)

Extend the driver-detection gate (PR #1265) to catch saras-style top-level `eq.m` reads. KU-29 captures three candidate approaches (cross-reference / sequence awareness / allowlist); pick Approach A.

### Priority 5: Dispatcher Refactor (#1271)

Collapse `_loop_tree_to_gams` and `_loop_tree_to_gams_subst_dispatch` into one parameterized dispatcher. Eliminates the recurring "added handler in one but not the other" class of bugs (hit in PR #1264 for partssupply, in #1268 for the decomp bound_scalar case, and will hit again otherwise).

### Suggested Sprint 25 Targets

| Metric | Sprint 24 Final | Sprint 25 Target |
|--------|-----------------|------------------|
| Parse | 143/143 (100%) | ≥ 143/143 (maintain) |
| Translate | 135/143 (94.4%) | ≥ 137/143 (96%; +2) |
| Solve | 99 | ≥ 105 (+6 via alias AD) |
| Match | 54 | ≥ 62 (+8 via alias AD) |
| path_syntax_error | 11 | ≤ 8 (−3 via emitter fixes #1275–#1281) |
| path_solve_terminated | 10 | ≤ 8 (−2) |
| model_infeasible | 8 | ≤ 5 (−3 via alias AD recovery) |
| Tests | 4,522 | ≥ 4,550 |

Rationale: the Sprint 25 alias-AD workstream, if fully landed, is projected to recover ~8 mismatching models → Match, plus ~3 infeasibility recoveries. The emitter/stationarity cleanup on the doubled-timeout-recovered models (ganges family) should reduce path_syntax_error below Sprint 24's low of 6 and ideally add 2–3 solves if any of those models actually have valid MCP structures underneath.

---

## Process Recommendation Review

### PR6: Full Pipeline for All Definitive Metrics

**Status:** FOLLOWED. Both Day 13 retests and the Day 13 Addendum used `run_full_test.py --quiet`. The doubled-timeout re-retest validated the original numbers and surfaced the 100% influx finding.

### PR7: Track model_infeasible Gross Fixes and Gross Influx

**Status:** FOLLOWED. Day 13 retest explicitly recorded: 6 gross fixes, 0 gross influx, −6 net.

### PR8: Absolute Counts and Percentages

**Status:** FOLLOWED. All tables include both absolute counts and percentages, with the scope denominator (147 vs 143) explicit.

### PR9: Set Targets Against Actual Pipeline Scope

**Status:** PARTIALLY FOLLOWED. Targets were set against the 147-baseline; the 147→143 mid-sprint shift created some ambiguity in evaluating the Translate target specifically. Sprint 25 should freeze the scope before Day 0.

### PR10: Budget for Error Category Influx

**Status:** FOLLOWED for the plan; **finding for Sprint 25: the 50–60% budget was too low**. Day 13 Addendum measured a 100% influx rate on the 5 newly-translating models. Update PR10 for Sprint 25 to project 80–100% influx for the specific subclass of "previously-timeout-excluded models" — these are latent emitter bugs, not valid-MCP-but-PATH-hard cases.

### PR11: Highest-Leverage Fix (Alias Differentiation) in Days 1–5

**Status:** PARTIALLY FOLLOWED. Alias work started Day 1 but was interrupted by Sprint 24 per-model urgent fixes. Days 4–7 were lost to other priorities. Reaffirm for Sprint 25.

### New Recommendations for Sprint 25

**PR12:** Add a byte-stability regression test across multiple `PYTHONHASHSEED` values for the full pipeline output. Non-determinism like #1283 should be caught by CI, not by reviewers reading generated `.gms` files.

**PR13:** Budget **100% influx** for "previously-timeout-excluded" translate recoveries; these are latent emitter bugs, not valid-MCP-but-hard-for-PATH cases. When fixing a timeout issue, plan for the immediate downstream path_syntax_error fix in the same sprint or defer the recovery.

**PR14:** Run a mid-sprint "read the generated MCP" review pass on a sample of models (5–10 randomly picked from in-scope). Issues #1275–#1281 / #1283 were all latent emitter bugs visible in committed artifacts — they're cheap to spot with 10 minutes of manual inspection and much more expensive to surface via downstream symptoms.

**PR15:** Freeze pipeline scope (v2.2.x exclusions) before Day 0 of each sprint. Mid-sprint scope shifts make target-vs-actual evaluation ambiguous (as experienced with the 147→143 shift during Sprint 24).

---

## Final Metrics Comparison (Sprint 20–24)

| Metric | S20 Final | S21 Final | S22 Final | S23 Final | S24 Final | S24 Delta |
|--------|-----------|-----------|-----------|-----------|-----------|-----------|
| Parse | 132/160 (82.5%) | 154/157 (98.1%) | 156/160 (97.5%) | 147/147 (100%) | **143/143 (100%)** | scope −4 |
| Translate | 120/132 (90.9%) | 137/154 (89.0%) | 141/156 (90.4%) | 140/147 (95.2%) | **135/143 (94.4%)** | −5 (scope shift) |
| Solve | 33/120 (27.5%) | 65/137 (47.4%) | 89/141 (63.1%) | 86/140 (61.4%) | **99/135 (73.3%)** | +13 |
| Match | 16/160 (10.0%) | 30/157 (19.1%) | 47/160 (29.4%) | 49/147 (33.3%) | **54/143 (37.8%)** | +5 |
| path_syntax_error | 48 | 41 | 20 | 23 | **11** | −12 |
| path_solve_terminated | 29 | 12 | 10 | 12 | **10** | −2 |
| model_infeasible | 12 | 15 | 12 | 11 | **8** | −3 |
| Tests | ~3,500 | 3,957 | 4,209 | 4,364 | **4,522** | +158 |

---

## Acknowledgments

Sprint 24's 20 merged PRs touched 5 workstreams over 15 days. The multi-solve gate (PR #1265) alone resolved two long-standing stuck models (decomp, danwolfe) that had been confounding baseline metrics since Sprint 19. The partssupply $ifThen fix (PR #1264) unblocked a model that had blocked 3 consecutive sprints. And the doubled-timeout experiment (PR #1274 + Day 13 Addendum PR #1282), while producing no new solves, provided the clearest data yet that translation-timeout work alone has lower near-term leverage than planning assumptions suggested — a finding that will materially reshape Sprint 25 prioritization.
