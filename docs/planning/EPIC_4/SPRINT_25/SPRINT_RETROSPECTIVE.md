# Sprint 25 Retrospective

**Created:** 2026-05-05
**Duration:** 16 sprint days (Day 0 – Day 15) — 1 day longer than Sprint 24 to absorb the Day 5 pivot
**Sprint Goal (Revised post-pivot):** Parse ≥ 143/143, Translate ≥ 135/143, Solve ≥ 100, Match ≥ 56, path_syntax_error ≤ 7, path_solve_terminated ≤ 9, model_infeasible ≤ 7, Tests ≥ 4,560 (8 acceptance criteria)
**Original Sprint Goal (pre-pivot):** Solve ≥ 105, Match ≥ 62, premised on a Pattern A alias-AD cohort sweep that the Day 5 investigation disproved (see §"Day 5 Pivot Retrospective" below)

---

## Executive Summary

Sprint 25 met **6 of 8** Revised acceptance criteria, with **4 of 8 reaching STRETCH** thresholds (Parse + Tests met; the 4 stretch wins below). The biggest wins were in **error-category reduction** rather than translate-rate growth: `path_solve_terminated` dropped 10 → 5 (stretch threshold ≤ 8), `model_infeasible` dropped 8 → 4 (stretch ≤ 5), Solve gained +5 to 104 (stretch ≥ 102), Match gained +6 to 60 (stretch ≥ 58). The two misses were Translate (135 → 133, −2) and `path_syntax_error` (11 → 12, +1). Both misses are driven by **bucket churn** — Sprint 25 fixes resolved 3 baseline `path_syntax_error` models (`mathopt4`, `saras`, `ferts`) and the upstream translate / SetMembershipTest fixes unblocked 3 previously-not-translating models (`camcge`, `cesam2`, `fawley`) into the syntax-error bucket; separately, `otpop` regressed from solving into the same bucket. saras was additionally caught by the Day 12 multi-solve gate (#1270) and moved from `path_syntax_error` to `translate_internal_error` — same net failure status, gated earlier in the pipeline by design.

The single most important narrative beat of Sprint 25 was the **Day 5 pivot** (`DAY5_PATTERN_A_INVESTIGATION.md`, PR #1305), which disproved the Pattern A hypothesis underpinning the original 8–12 day Phase 2 cohort rollout. Three Phase 1 target models (`qabel`, `abel`, `launch`) were reasoned to share a single root cause in `_partial_collapse_sum`'s multi-index recovery; trace capture under `SPRINT25_DAY2_DEBUG=1` plus byte-comparing the emitted KKT against the formal symbolic derivative showed all three have AD-correct emission. The bug surface lives elsewhere — Pattern C (alias-of-IndexOffset) for `launch`; KKT stationarity stateq sign/offset/domain handling for `qabel/abel`; and a subset-of-domain AD bug for `qabel/abel`'s `u`-quadratic that was eventually traced to issue #1311 (CLOSED during the sprint). The pivot collapsed the original 8 alias-AD issues into a Pattern C narrow fix (#1306, #1307, #1351) and an evidence-based deferral of the Pattern A cohort to Sprint 26 reclassification.

**Key Outcome:** 104 models solve (up from 99). 60 models match (up from 54). Parse 142/142 (100% of post-Sprint-25 in-scope set). Translate 133/142 (93.7%) — 2 below baseline due to the 1-model scope shift + Day 12 saras gate. Tests 4,735 passing (+213 net from Sprint 24 baseline; the suite was at 4,733 after Day 12 PR #1353 close, with +2 unit tests added by the PR #1360 review fix during Day 14). 9 PRs merged across the sprint (5 PR review iterations on PR #1353 alone, plus the Day 11/12/13/14 retest cycle). The Sprint 26 backlog comprises **5 issues filed during Day 13 (1 closed as duplicate of pre-existing #1224) → 4 net-new open + 19 carryforward = 23 total** under the `sprint-26` label.

---

## Goals and Results

### Sprint 25 Objectives (Revised post-Day-5)

1. :white_check_mark: Parse 142/142 (100%) — achieved (scope narrowed by 1 mid-sprint via convexity reclassification)
2. :x: Translate ≥ 135/143 — achieved 133/142 (−2 net; Day 12 saras gate accounts for −1 plus 1-model scope shift)
3. :white_check_mark: Solve ≥ 100 — achieved 104 (stretch ≥ 102 also met)
4. :white_check_mark: Match ≥ 56 — achieved 60 (stretch ≥ 58 also met)
5. :x: path_syntax_error ≤ 7 — achieved 12 (5 above target — bucket churn: 3 baseline syntax-error models resolved (mathopt4, saras, ferts) + 3 transfers from `path_solve_terminated`/`model_infeasible` after upstream translate fixes (camcge, cesam2, fawley) + 1 regression from solving (otpop) = +1 net)
6. :white_check_mark: path_solve_terminated ≤ 9 — achieved 5 (stretch ≤ 8 also met)
7. :white_check_mark: model_infeasible ≤ 7 — achieved 4 (stretch ≤ 5 also met)
8. :white_check_mark: Tests ≥ 4,560 — achieved 4,735 (+175 above target; 4,733 at Day 12, +2 from Day 14 PR #1360 review fix)

### Metrics Summary

| Metric | Baseline (Day 0) | Target | Stretch | Final (Day 14) | Status |
|--------|------------------|--------|---------|----------------|--------|
| Parse | 143/143 (100%) | ≥ 143/143 | — | **142/142 (100%)** | :white_check_mark: (1-model scope shift) |
| Translate | 135/143 (94.4%) | ≥ 135/143 | ≥ 137/143 | **133/142 (93.7%)** | :x: −2 net (saras gate + scope shift) |
| Solve | 99 | ≥ 100 | ≥ 102 | **104** | :white_check_mark: stretch |
| Match | 54 | ≥ 56 | ≥ 58 | **60** | :white_check_mark: stretch |
| path_syntax_error | 11 | ≤ 7 | ≤ 5 | **12** | :x: +1 (bucket churn) |
| path_solve_terminated | 10 | ≤ 9 | ≤ 8 | **5** | :white_check_mark: stretch |
| model_infeasible | 8 | ≤ 7 | ≤ 5 | **4** | :white_check_mark: stretch |
| Tests | 4,522 | ≥ 4,560 | — | **4,735** | :white_check_mark: +213 |

### Pipeline Scope Changes

The pipeline scope shifted from 143 → 142 models during Sprint 25 (visible by the Day 11 retest, before the Day 14 final). Per `BASELINE_METRICS.md` §5, the scope-freeze policy treats convexity-status reclassification as a runtime filter (similar to the multi-solve gate handling of `danwolfe` / `decomp`) rather than a scope edit requiring re-freeze. The 1-model reclassification was a Sprint 25 Days 1–10 side-effect that was already reflected in the Day 11 retest data and did not change Day 14 conclusions because all metric ratios use 142.

### Final Error Category Breakdown

**Translate failures (baseline 8 → Day 14 final 9 out of 142 in-scope):**

| Category | Baseline (Day 0, 143-scope) | Day 14 (142-scope) | Delta vs baseline |
|----------|------------------------------|--------------------|----|
| timeout | 5 | 5 | 0 (`iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase` unchanged) |
| internal_error | 3 | 4 | +1 (`saras` newly gated by Day 12 #1270; `danwolfe`, `decomp`, `mine` unchanged) |

**Solve failures (baseline 36 → Day 14 final 29 out of 133 translated):**

| Category | Baseline (Day 0, 143-scope) | Day 14 (142-scope) | Delta vs baseline |
|----------|------------------------------|--------------------|----|
| path_syntax_error | 11 | 12 | +1 (bucket churn — see §"Day 14 Bucket Churn") |
| path_solve_terminated | 10 | 5 | **−5** (stretch) |
| model_infeasible | 8 | 4 | **−4** (stretch) |
| path_solve_license | 7 | 8 | +1 (`ferts` transferred from `path_syntax_error` after #1290 fix unblocked compile but the model exceeds demo-license limits) |

### model_infeasible Accounting (PR7)

- **Baseline:** 8 models (143-scope)
- **Gross fixes:** 4 (chain, korcge, robustlp, fawley moved out of model_infeasible — 3 to solving, 1 transferred to `path_syntax_error`)
- **Gross influx:** 0 — **no baseline-solving model became infeasible during Sprint 25**
- **Net change:** −4 (8 → 4)

**Current 4 infeasible (all carryforward):** agreste, camshape, cesam, lnts.

**Zero gross influx into `model_infeasible`** matches Sprint 24's pattern — the second consecutive sprint with no infeasibility regressions among baseline-solving models.

### Day 14 Bucket Churn (the +1 path_syntax_error)

The `path_syntax_error` count moved 11 → 12 net, but composition changed substantially:

- **Resolved (3):** `mathopt4` (now solves to mismatch), `saras` (translate-gated by #1270), `ferts` (transferred to `path_solve_license` after the #1290 identifier-length fix unblocked compile).
- **Bucket additions (4):** `camcge` + `cesam2` (transferred from `path_solve_terminated` after #1338 / #1342 / #1344 SetMembershipTest fixes unblocked translate; surfaced new compile-time `$141` errors on phantom IndexOffset — #1354 / #1355), `fawley` (transferred from `model_infeasible` after #1276 / #1130 / #1133 — surfaced `$171` domain violations — #1356), `otpop` (regressed from solving — #1357, likely subsumed by #1334).
- **Stayed (8):** `clearlak`, `dinam`, `ganges`, `gangesx`, `indus`, `sample`, `turkey`, `turkpow`.

This pattern is captured as **KU-34** in `KNOWN_UNKNOWNS.md` §"End-of-Sprint Discoveries": Sprint metrics should track bucket transitions, not just net counts.

---

## Day 5 Pivot Retrospective

The Day 5 investigation (`DAY5_PATTERN_A_INVESTIGATION.md`, PR #1305) was the single most important methodological event of Sprint 25. It deserves a dedicated section because the lessons reshape how future multi-issue alias-AD workstreams should be planned.

### What the original Pattern A hypothesis got wrong

The pre-Day-5 plan assumed an 8-day Phase 2 cohort sweep across `#1138`, `#1139`, `#1140`, `#1142`, `#1145`, `#1150` (six issues, ~16 comparison-scope models), all scoped against a single Pattern A root cause: "multi-index concrete→symbolic recovery in `_partial_collapse_sum` unblocks the cohort." Phase 1 (Days 1–3) would land the Pattern A primitive; Phase 2 would roll it across the six issues. The Sprint 25 Match target `≥ 60` (stretch ≥ 62) was premised on this cohort recovering ~5–7 models.

The Day 1–3 Phase 1 work landed the `_find_var_indices_in_body` mechanical port to `_partial_collapse_sum` without behavioral change (PR #1304). Day 5 then attempted to validate the hypothesis on the three Phase 1 targets (`qabel`, `abel`, `launch`) — and found **none of them are blocked by Pattern A**. The AD layer emits byte-correct symmetric quadratic forms for `qabel`/`abel`'s criterion. The `launch` rel_diff (0.17) traces to a Pattern C variant (alias-of-IndexOffset, eventually documented as #1306 + #1307) in the KKT stationarity emitter, not the AD layer. The `qabel`/`abel` rel_diffs trace to the stateq Lagrangian term's sign/offset/domain handling AND a separate AD-subset-domain bug (eventually filed and CLOSED as #1311).

**The hypothesis was correct in isolation** (Pattern A IS a real shape; the Sprint 23 base layer for it works correctly) **but wrong about the bug surface of the cohort**. The cohort issues were originally classified as Pattern A on rel_diff symptom alone, without tracing back to the actual emitter / AD source.

### The evidence methodology that disproved it

Three steps, each cheap individually but powerful in combination:

1. **Trace capture under `SPRINT25_DAY2_DEBUG=1`**. The Day 2 PR added gated `[SPRINT25_DAY2]` debug-print statements to `src/ad/derivative_rules.py::_diff_varref` and `_partial_collapse_sum` (greppable by `[SPRINT25_DAY2][<tag>]`). Total per-model trace size: 3k–231k lines. Filterable down to the few hundred lines of interest by tag.

2. **Read the emitted GAMS**. Not the IR, not the trace alone — the actual `*_mcp.gms` artifact byte-compared against a hand-derived KKT for the criterion (and stationarity) of each Phase 1 model. For `qabel`/`abel`, this took ~1h per model and produced byte-identical output to the formal symmetric-quadratic-form derivative. That single observation refuted Pattern A for that pair immediately — the AD doesn't have a missing term; it produces the correct gradient.

3. **Compare to the formal symbolic derivative**. Not "the derivative we expect" — the derivative literally derived by hand from the criterion using calculus rules. Without this anchor, "the AD is wrong" tends to be ambiguous (which term? which sign? which guard?). With it, the question becomes a binary equality check.

### Reusable across future sprints

The methodology — **trace + emitted artifact + formal derivative** — is reusable for any multi-issue workstream that shares a hypothesized root cause. The cost is bounded (~1h–2h per model for the comparison; 1 day total to investigate 3 candidate models). The signal is strong (correct vs. byte-different is unambiguous). The result either confirms the hypothesis or — as in Sprint 25 — disproves it cheaply enough that a sprint can pivot mid-execution.

### **PR16 (new for Sprint 26): Pre-Sprint-0 Hypothesis Validation for Multi-Issue Workstreams**

When a sprint plans an N-day workstream rolling a single fix across M issues that share a hypothesized root cause:

> Run the validation methodology — trace capture + emitted-artifact byte-comparison against formal derivative on 2–3 representative models from M — **before** Sprint Day 0, as part of prep tasks. Budget 1–2 prep days for this; it is much cheaper than the Day 5 pivot cost. If the hypothesis is disproved, replan the workstream during prep rather than mid-sprint.

Sprint 25 spent Days 1–4 on Phase 1 work that produced no Match gain because the underlying hypothesis was wrong about the cohort. Sprint 26 will carry the Pattern A reclassification (~6 issues) into a state where the Day 5 methodology is the FIRST thing applied during prep, not Day 5.

---

## What Went Well

### 1. Day 5 Pivot Was Executed Cleanly Mid-Sprint

The Day 5 evidence-driven pivot landed without sprint cancellation or major Match-target degradation. The replanned schedule (Pattern C earlier on Days 6–7, Pattern A cohort sweep on Day 7 to confirm the pivot's correctness on the other 6 cohort models, qabel/abel PATH-solve reassessment on Day 8) absorbed the change with one extra day (Day 14 → Day 15 sprint extension). The Match target (≥ 56) was met **above stretch (60)** despite dropping the Pattern A cohort projection of +5–7 — recovered via the Pattern C launch fix (Bug #1 only), the closed #1311 AD-subset-domain bug, and the cascade of upstream emitter fixes that unblocked previously-non-translating models.

### 2. Fix-In-Place Series #1338..#1352 (Day 11 / 12)

Rather than reverting Sprint 25 Days 1–10 work after the original Checkpoint 2 NO-GO (Match 52, Solve 92), Day 11 / 12 fixed the regressions in place via nine targeted issues. Key landing patterns:

- **#1338..#1341** — `expr_to_gams` IndexOffset handling for SetMembershipTest indices (catmix/glider/markov/tricp translate)
- **#1342..#1343** — subset/alias keys in `up_expr_map`/`lo_expr_map` (shale/egypt translate)
- **#1345..#1347** — `solve_mcp` cwd + ScrDir for repo-relative `$include` (bearing/mathopt3/rocket presolve)
- **#1348** — china subset chain expansion + LhsConditionalAssign recursion
- **#1349** — pindyck `.fx → .l` side-effect preservation (later restructured per PR #1360 review)
- **#1350** — srkandw `tn(t,t)` self-alias remap via condition's set declared domain
- **#1351** — launch Pattern C consolidation rollback (xfail #1306; carryforward)
- **#1352** — qdemo7 table column alignment after preprocessor apostrophe-shift

Outcome: Match 52 → 60 (+8 vs pre-fix), Solve 92 → 104 (+12 vs pre-fix), `model_infeasible` 14 → 4 (−10 vs pre-fix). Five of six Checkpoint 2 criteria moved from NO-GO to GO; the sole residual NO-GO (`path_syntax_error`) was bucket churn, not a new structural regression.

### 3. WS4 Small Priorities (#1270 + #1271) Landed Cleanly on Day 12

Both shipped via PR #1353 with byte-diff verification. **#1270** (multi-solve gate Approach A): saras flagged as primal/dual driver via transitive cross-reference (`top_level_marginal_reads` → cross-ref into constraint bodies); 7 canary models (`gussrisk`, `sparta`, `partssupply`, `ibm1`, `imsl`, `otpop`, `turkey`) correctly excluded. **#1271** (dispatcher refactor): ~140 LOC removed, byte-diff verified across all 141 currently-translating models (zero diffs). PR #1353 went through 5 rounds of Copilot review iterations (commits `ddb37e2b`, `0a608357`, `282386df`, `3ed64c6e`) — useful test of the review iteration workflow at scale.

### 4. Cohort Sweep Methodology (Day 7)

The Day 7 cohort sweep (`DAY7_COHORT_SWEEP.md`) re-classified all 6 Pattern A cohort issues against the actual emitter output: #1138 → Pattern C plain-alias variant; #1139 → AD-correct (pipeline-excluded); #1140 → AD-correct multi-solve dynamics; #1142 → Pattern C Bug #2 (#1307); #1145 → offset-handling/condition-guard bug; #1150 → split (qabel = Pattern C massive-enumeration variant; abel = AD-correct nonconvex/solver-noise). The sweep is the per-issue evidence base for Sprint 26's reclassification work; it took ~1 day and produced reusable per-model classification data.

### 5. Determinism Infrastructure Landed Day 1 (PR #1301)

PR #1301 shipped the Option D grammar fix for #1283 (Lark `_resolve_ambiguities` post-parse disambiguation that prefers row layouts packing the most `table_value` children) plus the PR12 byte-stability test harness (5 Tier 0/1 fixtures × 5 fixed `PYTHONHASHSEED` values for the per-commit fast suite, plus a nightly full-corpus × 2 seeds). Tier 0/1 canaries remained 11/11 byte-identical across the sprint.

### 6. PR Review Iterations Worked End-to-End

Multiple PRs cycled through Copilot review with substantive technical issues caught at review time and fixed before merge:

- **PR #1353** (5 iterations): docstring direction inversion in `_params_referenced_in_any_constraint_body`, scope-neutral error message in `MultiSolveDriverError`, redundant `CaseInsensitiveDict` lowercase-set comprehension, parser hook over-approximation widened, `dollar_cond` `children[1]` was DOLLAR token not RHS (latent bug fix), test fixtures aligned with real grammar shape, `_emit_loop_node` token_subst threading completed.
- **PR #1360** (2 iterations): `clearlak_mcp.gms` revealed an emitter ordering bug — the Issue #1349 `.fx → .l` overrides were emitted under "Variable Bounds" before the bulk POSITIVE init's `var.l(t,n) = 1` clobbered them; fix integrated overrides INTO each variable's init group via `fx_to_l_overrides_by_var: dict[str, list[str]]` so the topo sort sees them; stale "PR #1360 review (Copilot)" attribution stripped from long-lived source comments; SPRINT_LOG mismatch on "no .py modified" corrected to distinguish initial retest commit from review-fix commits.

These review-driven catches reduced latent bug surface measurably; they also illustrate the value of **reading the generated `.gms` artifact** at review time (PR14 from the Sprint 24 retro), which surfaced #1360's emit-ordering bug.

---

## What Could Be Improved

### 1. The 8-day Phase 2 Pattern A Plan Was Built on an Untested Hypothesis

The Sprint 25 plan committed 8 days to a Phase 2 cohort sweep before the Day 5 hypothesis-validation exercise had been run. The validation cost (1 day) was lower than the cost of the lost Days 1–4 Phase 1 work plus the Day 5–6 pivot. Sprint 26 prep should run hypothesis validation BEFORE committing schedule (PR16, see §"Day 5 Pivot Retrospective").

### 2. Bucket Churn Confounds the path_syntax_error Metric

Sprint 25's `path_syntax_error` net delta was +1 (11 → 12), but the underlying composition changed substantially: 3 baseline syntax-error models resolved (mathopt4, saras, ferts) and 4 newly-failing ones appeared — 3 driven by upstream translate fixes unblocking previously-not-reaching-PATH models (camcge, cesam2, fawley) plus 1 regression from solving (otpop, baseline `solve_success` → `path_syntax_error`). Net counts hide this. KU-34 captures the recommendation: future sprints should track bucket transitions explicitly with a "Sprint 24 bucket → Sprint 25 bucket" provenance column on `BASELINE_METRICS.md`. PR17 below.

### 3. Pattern C Fix on launch Required a Same-Sprint Rollback (#1351)

PR #1308 (Day 6 Pattern C consolidation gate) correctly suppressed phantom `nu_dweight(s±k)` offsets but the downstream zero-offset builder lost the cross-element aggregation entirely, causing launch to go locally-infeasible. #1351 dropped the gate; the original per-offset enumeration is mathematically over-counted but PATH finds a feasible point matching Day 0. The xfail (`tests/unit/kkt/test_pattern_c_alias_offset_gate.py`) is a known carryforward for Sprint 26 (proper sum-over-equation-domain rewrite). The lesson: structural gates that change emit shape need solve-time validation BEFORE merge, not just unit-test validation. The compile-only validation under `action=c` would have shown a Normal completion (it did — see DAY7_COHORT_SWEEP.md Task 2); the LOCAL INFEASIBLE only surfaced at full PATH solve.

### 4. 1-Model Scope Shift Mid-Sprint Replayed the Sprint 24 Issue

The pipeline scope moved 143 → 142 mid-sprint via convexity reclassification of one model. Sprint 24 retrospective explicitly recommended PR15 (freeze pipeline scope before Day 0) — followed for the explicit exclusion set, but a runtime convexity check still moved one model out-of-scope during Sprint 25 Days 1–10. The denominator change is small (1/143 = 0.7%) and the policy under `BASELINE_METRICS.md` §5 treats this as a runtime filter rather than a scope edit, so accounting wasn't materially affected, but the model that moved out is unidentified in the Day 14 metrics — that's a Sprint 25 retrospective item (which model? what triggered the reclassification?). PR18 below.

### 5. PR #1349's Original Fix Introduced a Latent Emitter Bug

The Day 11/12 fix-in-place series #1349 (preserve `.fx → .l` side-effect) was correct for pindyck (its target model) but didn't anticipate clearlak-shape models where the same variable has both an `_fx_`-replaced source `var.fx(idx) = val` AND a bulk POSITIVE / denominator-FREE `var.l(t,n) = 1` init. The bulk init clobbered the per-instance overrides for ~120 elements, defeating the fix. The bug landed un-noticed at merge and was caught only by Copilot's review of `data/gamslib/mcp/clearlak_mcp.gms` at PR #1360. **The lesson reinforces PR14**: the generated `.gms` artifact is part of the diff and deserves review; emitter bugs are visible in committed artifacts long before they surface as solve failures. Both clearlak and pindyck would have been caught with a 5-minute "read the relevant section of the .gms" review.

---

## What We'd Do Differently

### 1. Run Hypothesis-Validation Pre-Sprint-0 (PR16)

For any multi-issue workstream sharing a single hypothesized root cause, run the Day 5 methodology (trace capture + emitted-artifact byte comparison against formal derivative, on 2–3 representative models) BEFORE Sprint Day 0 as part of prep. Budget 1–2 prep days. If the hypothesis is disproved, replan during prep rather than mid-sprint.

### 2. Track Bucket Transitions Explicitly (PR17)

Sprint baselines should include per-model bucket provenance ("Sprint 24 bucket → Sprint 25 bucket") so that net deltas don't hide composition changes. Add a "bucket provenance" column to `BASELINE_METRICS.md` that lists each failing model's prior-sprint bucket alongside the current-sprint bucket. The Day 14 SPRINT_LOG entry already does this informally for Sprint 25 — Sprint 26 prep should formalize it.

### 3. Add Pre-Merge Solve-Time Validation for Structural Emit Changes (PR19)

PR #1308's Pattern C gate passed unit tests + compile-only validation but produced a locally-infeasible MCP at full PATH solve. Structural gates that change emit shape should require a full PATH solve (or at minimum, a `model_optimal_presolve` round-trip) on the target model BEFORE merge — not just unit + compile-only validation. Sprint 26 should consider extending CI to run a fast-suite `make test` PLUS a 30s PATH solve on a configurable target list when emit-affecting `.py` files change.

### 4. Read the Generated .gms in Review (PR14 from Sprint 24 — Reaffirm)

PR14 from the Sprint 24 retro called for mid-sprint "read the generated MCP" review passes. Sprint 25's PR #1360 emit-ordering bug in clearlak_mcp.gms (~120 lines of clobbered `.l` overrides) would have been caught with a 5-minute manual read at the original PR #1349 merge. Reaffirm and elevate: every PR that touches `src/emit/*.py` should have at least one regenerated `.gms` artifact from an affected model in the diff, and reviewers should read the relevant section.

### 5. Identify the Sprint-25 Scope-Shifted Model (PR18)

The 1-model 143 → 142 scope shift during Sprint 25 wasn't traced to a specific model. Sprint 26 prep should run a `git diff` between the Day 0 baseline `gamslib_status.json` and the Day 14 final to identify which model's convexity status changed and document the reason in the SPRINT_LOG.

---

## Sprint 26 Recommendations

Based on Sprint 25 findings and the 23 issues labeled `sprint-26`:

### Priority 1: Pattern C Gate Generalization (#1354, #1355, #1356, #1357, #1306, #1307)

The Pattern C launch-shaped gate (#1306 narrowing) needs to be widened to detect plain-alias enumeration (no `$cond` filter required) and `sameas`-decomposed SAM-block aliases. KU-33 captures the discovery: at least 4 CGE/SAM-balance models exhibit phantom `nu_<eq>(i±N)` enumeration on stationarity equations whose source bodies have no alias-conditional guard. Likely unblocks #1354 (camcge), #1355 (cesam2), #1356 (fawley), #1357 (otpop) — plus #1306/#1307 (the original launch fix needs the proper sum-over-equation-domain rewrite to remove the `xfail`). Estimated impact: +3 to +5 path_syntax_error → solve.

### Priority 2: Pattern A Cohort Reclassification (#1138, #1139, #1140, #1142, #1145, #1150)

Per the Day 7 cohort sweep, the original Pattern A cohort is not Pattern A. Sprint 26 Day 0 prep should reclassify each issue per `DAY7_COHORT_SWEEP.md` §"Classification Table" (Pattern C plain-alias variant, AD-correct multi-solve dynamics, offset-handling/condition-guard, etc.) and either close the original issue with a forward link or update its title/labels to match. After reclassification, file new tracking issues for the genuine bugs in their correct categories. Note: #1311 (qabel/abel u-quadratic AD subset-domain bug) was identified during Day 8 reassessment and CLOSED during Sprint 25 — that bug is fixed.

### Priority 3: Pattern E Carryforward (#1141, #1144, #1147)

Phase E (Pattern E routing) was cancelled per the literal Checkpoint 2 NO-GO routing on `path_syntax_error`. The three open Pattern E issues remain unresolved and may need re-investigation under the post-Sprint-25 emit pipeline (some may have shifted bucket via the Sprint 25 fix-in-place series). Re-verify each before scoping Sprint 26 fix work.

### Priority 4: Translation Timeout — Algorithmic (#885, #931, #932, #1185, #1228, #1224)

5 hard timeouts (`iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`) plus the `mine` `internal_error` (#1224, ParamRef-valued IndexOffset). Per Prep Task 8 in Sprint 25 (`PROFILE_HARD_TIMEOUTS.md`), all 5 timeouts share the `SetMembershipTest` / `enumerate_equation_instances` Cartesian-explosion pattern. Option 1 short-circuit (in `src/ad/index_mapping.py::enumerate_equation_instances`) is a single architectural fix that should unblock at least srpchase and possibly iswnm. 4–6h effort estimate.

### Priority 5: AD Residuals from Day 11 Fix-in-Place Series (#1334, #1335)

Two open AD-correctness issues filed during Sprint 25 Day 11 investigation:
- **#1334**: `_add_jacobian_transpose_terms_scalar` wraps Jacobian in spurious `Sum(("t__",), ...)` when ParamRef domain is a strict subset of equation domain (otpop confirmed). Likely subsumes #1357.
- **#1335**: Missing dzdef/dp cross-term in `stat_p` when `zdef` references `p` via time-reversal-indexed offset (otpop residual after #1334 partial fix).

Both target the `_replace_indices_in_expr` + `_add_jacobian_transpose_terms_scalar` pair in `src/kkt/stationarity.py`. Combined effort 8–14h.

### Suggested Sprint 26 Targets

| Metric | Sprint 25 Final | Sprint 26 Target |
|--------|-----------------|-------------------|
| Parse | 142/142 (100%) | ≥ 142/142 (maintain) |
| Translate | 133/142 (93.7%) | ≥ 135/142 (95%; +2 via #1224 mine fix or Option 1 short-circuit) |
| Solve | 104 | ≥ 108 (+4 via Pattern C generalization #1354/#1355) |
| Match | 60 | ≥ 64 (+4 via combined Pattern C generalization + #1334/#1335 AD fixes) |
| path_syntax_error | 12 | ≤ 6 (−6 via Pattern C generalization removing camcge/cesam2/fawley/otpop) |
| path_solve_terminated | 5 | ≤ 5 (maintain) |
| model_infeasible | 4 | ≤ 4 (maintain — most carryforwards need investigative work) |
| Tests | 4,735 | ≥ 4,750 |

Rationale: Pattern C generalization is the single highest-leverage workstream (4 path_syntax_error → solve = +4 Solve, +3–4 Match). The Pattern A reclassification work doesn't add net Match by itself but is prep for genuine Sprint 27 fixes. Translation timeout work should target the Option 1 short-circuit (Sprint 25 Day 13 deferral) for srpchase + possibly iswnm = +1–2 Translate.

---

## Process Recommendation Review

### PR6: Full Pipeline for All Definitive Metrics

**Status:** FOLLOWED. Day 11, Day 11 revised retest, Day 14 final retest all used `run_full_test.py --quiet`. The Day 11 → Day 11 revised flow (after the fix-in-place series) was a useful demonstration of using mid-sprint pipeline runs to validate fix-in-place vs revert decisions.

### PR7: Track model_infeasible Gross Fixes and Gross Influx

**Status:** FOLLOWED. Day 14 retest explicitly recorded: 4 gross fixes (chain, korcge, robustlp, fawley), 0 gross influx, −4 net.

### PR8: Absolute Counts and Percentages

**Status:** FOLLOWED. All tables include both absolute counts and percentages with the scope denominator (143 vs 142) explicit.

### PR9: Set Targets Against Actual Pipeline Scope

**Status:** PARTIALLY FOLLOWED. Targets were set against the 143-baseline; the mid-sprint shift to 142 was small enough not to materially change conclusions, but the "which model shifted out and why" question remains unaddressed (PR18 below).

### PR10: Budget for Error Category Influx — Re-Calibrated Outcome

**Status:** Re-calibration HELD on the alias-AD side; emitter recovery influx was within the upper bound but on the high end.

The Sprint 24 retro recommended re-calibration: 30% influx for alias-AD recoveries, 80–100% for emitter recoveries. Sprint 25 results:

- **Alias-AD / Pattern C (30% budget):** 0% — no alias-AD-attributable new failures. Pattern C launch fix (Bug #1) recovered 0 net Match (Bug #2 still open as #1307); did not introduce any regressions. ✅ Within budget.
- **Emitter recovery (80–100% budget):** 71% (5 influx / 7 fixes). The 5 influx breaks down as 1 new failure (otpop) + 4 bucket transfers (camcge, cesam2, fawley, ferts moved between failure categories without net resolution). Emitter recoveries that translate-unblocked previously-failing models systematically surface fresh syntax-time symptoms — KU-33 captures this as a generalizable observation. ✅ Within the 80–100% upper bound, but on the high end; future sprints should expect this pattern to recur.

### PR11: Highest-Leverage Fix in Days 1–5

**Status:** PARTIALLY FOLLOWED but disrupted by the Day 5 pivot. The original "highest-leverage" was Pattern A Phase 1 → Phase 2 cohort. Post-pivot, the highest-leverage was #1289 ganges (landed Day 4, in scope as planned). The Pattern C work moved earlier (Days 6–7) and absorbed what was Pattern A's planned slot.

### PR12: Byte-Stability Determinism Tests

**Status:** FOLLOWED — landed Day 1 (PR #1301). Tier 0/1 canaries 11/11 byte-identical across all sprint retests. Sprint 25 demonstrated the harness works as intended; no determinism regressions surfaced.

### PR13: 100% Influx Budget for Previously-Timeout-Excluded Translate Recoveries

**Status:** FOLLOWED. Sprint 25 did not unblock new translate recoveries (the 5 hard timeouts remain). PR13 was untested in Sprint 25; it remains the recommended budget.

### PR14: Mid-Sprint "Read the Generated MCP" Review Pass

**Status:** PARTIALLY FOLLOWED. Day 13 buffer included some artifact inspection (Pattern C analysis on camcge/cesam2 emit), but no dedicated review pass. PR #1360's Copilot-caught emit-ordering bug demonstrates the value of artifact review; reaffirm and elevate for Sprint 26.

### PR15: Freeze Pipeline Scope Before Day 0

**Status:** FOLLOWED for the explicit exclusion set, but a runtime convexity check still moved 1 model out-of-scope during Sprint 25 Days 1–10. The policy in `BASELINE_METRICS.md` §5 covers this case (treated as runtime filter), but identifying which model shifted is a Sprint 26 prep item (PR18).

### New Recommendations for Sprint 26

**PR16:** Run hypothesis-validation pre-Sprint-0 for multi-issue workstreams sharing a single hypothesized root cause. Trace capture + emitted-artifact byte comparison against formal derivative on 2–3 representative models. Budget 1–2 prep days.

**PR17:** Add bucket provenance to `BASELINE_METRICS.md`. Each failing model carries its prior-sprint bucket alongside the current-sprint bucket so net deltas don't hide composition changes.

**PR18:** Identify the 1-model 143 → 142 scope shift from Sprint 25. Document the model and the reclassification reason in Sprint 26's `BASELINE_METRICS.md` §5.

**PR19:** Add pre-merge solve-time validation for structural emit changes. CI should run a fast-suite `make test` PLUS a 30s PATH solve on a configurable target list when emit-affecting `.py` files change. PR #1308 (Pattern C gate) would have been caught earlier.

---

## Final Metrics Comparison (Sprint 20–25)

| Metric | S20 Final | S21 Final | S22 Final | S23 Final | S24 Final | S25 Final | S25 Delta |
|--------|-----------|-----------|-----------|-----------|-----------|-----------|-----------|
| Parse | 132/160 (82.5%) | 154/157 (98.1%) | 156/160 (97.5%) | 147/147 (100%) | 143/143 (100%) | **142/142 (100%)** | scope −1 |
| Translate | 120/132 (90.9%) | 137/154 (89.0%) | 141/156 (90.4%) | 140/147 (95.2%) | 135/143 (94.4%) | **133/142 (93.7%)** | −2 (saras gate + scope shift) |
| Solve | 33/120 (27.5%) | 65/137 (47.4%) | 89/141 (63.1%) | 86/140 (61.4%) | 99/135 (73.3%) | **104/133 (78.2%)** | +5 |
| Match | 16/160 (10.0%) | 30/157 (19.1%) | 47/160 (29.4%) | 49/147 (33.3%) | 54/143 (37.8%) | **60/142 (42.3%)** | +6 |
| path_syntax_error | 48 | 41 | 20 | 23 | 11 | **12** | +1 (bucket churn) |
| path_solve_terminated | 29 | 12 | 10 | 12 | 10 | **5** | −5 |
| model_infeasible | 12 | 15 | 12 | 11 | 8 | **4** | −4 |
| Tests | ~3,500 | 3,957 | 4,209 | 4,364 | 4,522 | **4,735** | +213 |

---

## Acknowledgments

Sprint 25's 9 merged PRs touched 5 workstreams over 16 days. The Day 5 pivot — disproving the Pattern A hypothesis on three Phase 1 models in one day, replanning the sprint mid-execution — was the single most important methodological event and is the basis for Sprint 26's PR16 (pre-Sprint-0 hypothesis validation). The fix-in-place series #1338..#1352 (Day 11 / 12) recovered the original Checkpoint 2 NO-GO into a CONDITIONAL GO (5/6 criteria stretch, sole NO-GO bucket churn), avoiding what would have been substantial rework if the team had instead reverted Sprint 25 Days 1–10 work. WS4 small priorities (#1270 multi-solve gate Approach A, #1271 dispatcher refactor) landed cleanly via PR #1353 with byte-diff verification across all 141 currently-translating models. The PR #1360 Copilot-caught emit-ordering bug in clearlak_mcp.gms — surfaced from `data/gamslib/mcp/clearlak_mcp.gms` lines 240+ rather than from a unit test failure — is a concrete reminder that the generated `.gms` artifact is part of every PR diff and deserves review.
