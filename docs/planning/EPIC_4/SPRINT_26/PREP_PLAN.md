# Sprint 26 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 26 begins
**Timeline:** Complete before Sprint 26 Day 1
**Goal:** Set up Sprint 26 for success — Pattern C Generalization, Pattern A Reclassification & Sprint 25 Carryforward (Match 60 → ≥ 64; Solve 104 → ≥ 108; path_syntax_error 12 → ≤ 6)

**Key Insight from Sprint 25:** Sprint 25 spent Days 1–4 on Phase 1 alias-AD work that produced no Match gain because the underlying Pattern A hypothesis was wrong about the cohort. The Day 5 pivot (`docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md`) disproved the hypothesis in one day via a reusable methodology — trace capture under `SPRINT25_DAY2_DEBUG=1` + emitted-artifact byte comparison against the formal symbolic derivative. **Sprint 26 prep MUST apply this methodology PRE-Day-0 to the Pattern C generalization hypothesis (Priority 1).** That is the single highest-leverage Sprint 25 process recommendation (PR16) and the primary mitigation for the alias-AD architectural-drift risk that has now hit three consecutive sprints.

Sprint 25 also surfaced two structural-emit failure modes that are now explicit prep concerns: (a) the #1308 Pattern C launch fix passed unit + compile-only validation but produced a locally-infeasible MCP at full PATH solve (mitigation: PR19 pre-merge solve-time validation); (b) the #1349 `.fx → .l` side-effect fix passed pindyck integration but introduced a clobbering bug on clearlak that was only caught by Copilot reading the regenerated `.gms` artifact during PR review (mitigation: PR14 reaffirmation — every emit-touching PR must include a regenerated `.gms` diff). Both mitigations are prep-task work items.

**Branching:** All prep task branches should be created from `main` and PRs should target `main`.

---

## Executive Summary

Sprint 26 inherits the Sprint 25 carryforward backlog of 23 issues labeled `sprint-26` (4 net-new from Day 13 — #1354 camcge, #1355 cesam2, #1356 fawley, #1357 otpop — plus 19 carryforward including #1224 mine, #1306/#1307 Pattern C launch, #1334/#1335 AD residuals, #1138/#1139/#1140/#1142/#1145/#1150 Pattern A cohort, #1141/#1144/#1147 Phase E, and 5 hard timeouts). The single highest-leverage workstream is **Pattern C gate generalization** — widening the Sprint-25 launch-shape gate to cover plain-alias enumeration and `sameas`-decomposed SAM-block aliases, which alone is projected to drop `path_syntax_error` 12 → 6 and add +4 Solve / +3–4 Match.

This prep plan focuses on:

1. **Risk identification** — Sprint 26 Known Unknowns List covering Pattern C generalization correctness, Pattern A reclassification scope, Option 1 short-circuit feasibility, AD residuals on `otpop`, and the new process recommendations
2. **Pre-Sprint-0 hypothesis validation (PR16)** — Apply the Day 5 methodology to the Pattern C generalization hypothesis on 2–3 representative models BEFORE committing the 12–18h Priority 1 budget
3. **Pattern A cohort reclassification pre-work** — Per-issue action plan (subsume / close-and-refile / investigate further) using the Sprint 25 `DAY7_COHORT_SWEEP.md` classification
4. **Pattern E status survey** — Re-verify #1141/#1144/#1147 under post-Sprint-25 emit pipeline; some may have shifted bucket via the Sprint 25 fix-in-place series
5. **Translation timeout Option 1 design refresh** — Verify the `PROFILE_HARD_TIMEOUTS.md` design is still valid; identify exact `src/ad/index_mapping.py` patch sites
6. **AD residuals investigation recap** — Confirm `ISSUE_1334.md` / `ISSUE_1335.md` are still accurate; pin the otpop reproducer
7. **Pre-merge solve-time validation CI design (PR19)** — CI extension for emit-affecting changes; trigger list, target-model list, budget, integration with existing `make test` harness
8. **Bucket-provenance baseline + scope freeze (PR17 + PR15)** — Per-failing-model Sprint-25 → Sprint-26 bucket provenance on `BASELINE_METRICS.md`; freeze v2.2.x exclusions before Day 0
9. **Sprint 25 scope-shifted model identification (PR18)** — Track down the 1-model 143 → 142 reclassification from Sprint 25 Days 1–10
10. **CONTRIBUTING.md update for emit-PR `.gms` artifact diffs (PR14 reaffirmation)** — Hard rule: every PR touching `src/emit/*.py` must include at least one regenerated `.gms` artifact from an affected model
11. **Sprint planning** — Detailed 14-day schedule (Day 0 setup + Days 1–13 execution) with day-by-day prompts; ≤ 12 hours/day budget per the PROJECT_PLAN.md Sprint 26 entry

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 26 Known Unknowns List ✅ | Critical | 2–3h | None | All priorities — risk identification |
| 2 | Identify Sprint 25 Scope-Shifted Model (PR18) | Critical | 1–2h | None | Process — accurate baseline accounting |
| 3 | Pattern C Hypothesis Validation (PR16) | Critical | 6–8h | Task 1 | Priority 1: gate generalization (4 models) |
| 4 | Pattern A Cohort Reclassification Pre-Work | High | 3–4h | Task 1 | Priority 2: reclassify 6 issues |
| 5 | Pattern E Carryforward Status Survey | High | 2–3h | Task 1 | Priority 3: re-verify 3 issues |
| 6 | Profile Option 1 Short-Circuit Approach | High | 3–4h | Task 1 | Priority 4: srpchase + iswnm + 3 timeouts |
| 7 | AD Residuals (#1334, #1335) Investigation Recap | High | 2–3h | Task 1 | Priority 5: otpop convergence |
| 8 | Design Pre-Merge Solve-Time Validation CI (PR19) | High | 3–4h | Task 1 | Process — emit-change failure-mode mitigation |
| 9 | Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15) | Critical | 2–3h | Task 2 | All priorities — baseline metrics |
| 10 | Update CONTRIBUTING.md for Emit-PR `.gms` Diffs (PR14 Reaffirmation) | Medium | 1h | None | Process — emit-bug surfacing |
| 11 | Plan Sprint 26 Detailed Schedule | Critical | 3–4h | Tasks 1–10 | All priorities — sprint planning |

**Total Estimated Time:** 28–39 hours (~3.5–5 working days)

**Critical Path:** Task 1 → Task 3 → Task 11 (Pattern C hypothesis validation chain — the central new prep activity for Sprint 26)
**Secondary Path:** Task 2 → Task 9 → Task 11 (baseline + scope-shift documentation chain)
**Parallelizable:** Tasks 4 + 5 (cohort reclassification work); Tasks 6 + 7 (Option 1 + AD residuals); Task 8 (PR19 CI design); Task 10 (CONTRIBUTING.md)

---

## Task 1: Create Sprint 26 Known Unknowns List

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 2–3 hours (actual: ~2.5h)
**Completed:** 2026-05-07
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 26 to prevent late discoveries during implementation. This is the first task because it surfaces risks that inform the design of all other prep tasks — particularly the Pattern C hypothesis validation (Task 3), the Pattern A reclassification pre-work (Task 4), and the PR19 CI design (Task 8). This task also carries forward the four end-of-sprint unknowns from Sprint 25 (KU-33 through KU-36 in `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md`).

### Why This Matters

Sprint 25's end-of-sprint discoveries (KU-33 through KU-36) include the central observation for Sprint 26: **Pattern C generalizes beyond launch — at least 4 CGE/SAM-balance models exhibit phantom `nu_<eq>(i±N)` enumeration on stationarity equations whose source bodies have no alias-conditional guard.** Sprint 26's Priority 1 is built on this hypothesis. Per Sprint 25 retrospective process recommendation **PR16**, the hypothesis must be validated on 2–3 representative models PRE-Day-0 (Task 3 below); if disproved, Priority 1 must be replanned during prep, not mid-sprint.

Sprint 25 also surfaced **KU-34 (bucket churn confounds path_syntax_error metric)** — Sprint 26 prep must add bucket-provenance to `BASELINE_METRICS.md` (Task 9). And **KU-35 / KU-36** captured architectural invariants (multi-solve gate over-approximation; `_loop_tree_to_gams` bare-ID substitution) that must not silently regress in Sprint 26.

### Background

- Sprint 25 Known Unknowns: `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` (27 prep + 4 end-of-sprint KU-33..KU-36 across 6 categories + §End-of-Sprint Discoveries)
- Sprint 25 Retrospective: `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` (§"Sprint 26 Recommendations" Priorities 1–5; §"What We'd Do Differently" PR16–PR19 + PR14 reaffirmation)
- 23 issues labeled `sprint-26` in GitHub (4 net-new from Sprint 25 Day 13 + 19 carryforward)
- Sprint 25 carryforward end-of-sprint KUs to migrate into Sprint 26 numbering:
  - **KU-33** (Pattern C generalizes beyond launch) → directly drives Priority 1
  - **KU-34** (bucket churn dominates path_syntax_error metric) → drives Task 9 (bucket-provenance baseline)
  - **KU-35** (multi-solve gate over-approximation invariant) → regression-canary protection
  - **KU-36** (`_loop_tree_to_gams` bare-ID substitution invariant) → regression-canary protection

### What Needs to Be Done

1. **Review Sprint 25 carryforward / end-of-sprint KUs** — KU-33 through KU-36 continue into Sprint 26 with full text (not just pointers). Migrate into Sprint 26 numbering as Category 6 (Sprint 25 Carryforward).

2. **For each Priority area, brainstorm unknowns:**

   **Priority 1 (Pattern C Gate Generalization):**
   - Does the launch-shape gate's "alias-only conditional sum" detection extend cleanly to plain-alias enumeration (no `$cond` filter required)? Or does removing the `$cond` predicate break gate selectivity on quocge/prolog/irscge canaries?
   - Does the `sameas`-decomposed SAM-block alias case (cesam2 `nu_COLSUM(i±N)$(jj(i±N))`) require a separate detection path, or is it a generalization of the same shape?
   - Will the `_replace_indices_in_expr` ParamRef branch fix (#1334) interact with the Pattern C generalization, or are they independent?
   - How many of the 11 Tier 0/1 canary models contain `imat(i,j)`-style SAM-coefficient patterns that the broader gate might incorrectly fire on?
   - Is the consolidated `sum(j$(domain_filter), imat(j,i) * nu_<eq>(j))` form mathematically equivalent to the per-offset enumeration for all 4 target models, or only for camcge / cesam2 specifically?

   **Priority 2 (Pattern A Cohort Reclassification):**
   - For each of the 6 cohort issues (#1138, #1139, #1140, #1142, #1145, #1150), is the Sprint 25 Day 7 sweep classification still accurate after the Sprint 25 Day 11/12 fix-in-place series (which touched several upstream code paths)?
   - Which cohort issues should be **closed as duplicate of #1334** (subsumed by AD residuals), vs **closed as duplicate of new Priority 1 work** (subsumed by Pattern C generalization), vs **kept open with new tracking issues filed**?
   - Will closing #1138, #1139, #1140, #1142, #1145, #1150 surface any test xfails that were depending on those issue numbers in test docstrings?

   **Priority 3 (Pattern E Carryforward Re-Verification):**
   - Have any of #1141 (kand), #1144 (catmix), #1147 (camshape) shifted bucket via the Sprint 25 fix-in-place series #1338..#1352? In particular, catmix was on the Sprint 25 SetMembershipTest fix list (#1338) and may have been recovered.
   - Is Phase E (Pattern E routing per `DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4) still the right framing post-Sprint-25, or do the 3 issues fit a different shape now?

   **Priority 4 (Translation Timeout Option 1 Short-Circuit):**
   - Per `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` Task 8, the Option 1 short-circuit lands in `src/ad/index_mapping.py::enumerate_equation_instances` with supporting behavior in `resolve_set_members` (same file) and the static `SetMembershipTest` failure path in `src/ir/condition_eval.py`. Is this design still valid post-Sprint-25, or did the Sprint 25 #1338..#1341 IndexOffset / SetMembershipTest fixes shift the failure surface?
   - Will the Option 1 short-circuit recover only srpchase, or also unblock 1+ of {iswnm, mexls, nebrazil, sarf}? (Per S25 Prep Task 8: srpchase completes in 500s if budget extends to 900s; the others timeout at 900s.)
   - Should #1224 (mine ParamRef IndexOffset) be deferred to a separate effort, or bundled with Priority 4?

   **Priority 5 (AD Residuals #1334, #1335):**
   - Are the per-issue source-line references in `ISSUE_1334.md` / `ISSUE_1335.md` (file:line at `src/kkt/stationarity.py:5279–5310`, `:2295–2479`) still accurate after the Sprint 25 fix-in-place series touched stationarity.py?
   - Does the otpop NLP-warm-started MCP reproducer still produce the documented `LHS = -1.4157` residual on `stat_cd(ag-subsist)`?
   - Does fixing #1334 actually subsume #1357 (otpop `$171` domain violations from Day 13 carryforward), or are they independent bugs?

   **Process Recommendations (PR16–PR19 + PR14):**
   - Will the PR19 pre-merge solve-time validation CI extension produce flaky failures on Tier 0/1 canaries (PATH solve under tight budget)?
   - What's the right target list for PR19 — just the 4 Pattern C target models, or all 11 Tier 0/1 canaries, or some subset?
   - Will the PR16 hypothesis-validation methodology produce a binary signal on the Pattern C generalization hypothesis (clearly yes / clearly no) or an ambiguous result that doesn't drive a decision?
   - Will adding bucket-provenance to BASELINE_METRICS.md (PR17) confuse readers who expect aggregate counts only?
   - Does the PR14 reaffirmation rule for emit-PR `.gms` diffs need an exception for refactor-only PRs (e.g., the Sprint 25 #1271 dispatcher refactor was byte-diff verified across 141 models — that diff is "zero" but the rule says include one)?

   **Cross-cutting:**
   - What's the realistic Match-rate ceiling if Pattern C generalization succeeds on all 4 target models? (Sprint 25 retro projects +4 Match, but historically alias-AD landings have under-delivered.)
   - Will the Sprint 25 1-model scope shift (143 → 142) reverse during Sprint 26 work, returning the in-scope count to 143?

3. **Categorize by topic, prioritize by risk, define verification method.**

4. **Assign verification deadlines** (Day 0–1 for Critical, Day 2–3 for High, Day 5+ for Medium/Low).

5. **Create document** following `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` format, including a Task-to-Unknown mapping table that ties each prep task to the specific unknowns it researches.

### Changes

Created `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` with 26 unknowns across 6 categories (5 priorities + cross-cutting/process recommendations). Updated Tasks 2–10 of this PREP_PLAN with "Unknowns Verified" metadata lines mapping each prep task to the specific unknowns it researches. Added CHANGELOG.md entry under Sprint 26 Preparation summarizing Task 1 completion.

### Result

26 unknowns documented across 6 categories:

- **Category 1: Pattern C Gate Generalization** (6 KUs, 1.1–1.6) — gate selectivity, sameas-decomposed SAM-block detection, #1334 interaction, mathematical equivalence, canary risk, Day-5-methodology PROCEED/REPLAN signal.
- **Category 2: Pattern A Cohort Reclassification** (4 KUs, 2.1–2.4) — Day 7 sweep classification accuracy, per-issue action, test xfail surface, source/docs cross-references.
- **Category 3: Pattern E Carryforward Re-Verification** (3 KUs, 3.1–3.3) — bucket shift via S25 fix-in-place series, catmix-#1338 specific check, Phase E framing validity.
- **Category 4: Translation Timeout Option 1 Short-Circuit** (4 KUs, 4.1–4.4) — design validity, impact projection, #1224 deferral, determinism.
- **Category 5: AD Residuals (#1334, #1335)** (4 KUs, 5.1–5.4) — file:line currency, otpop reproducer, #1334 ↔ #1357 subsumption, #1335 tractability.
- **Category 6: Cross-Cutting & Process Recommendations** (5 KUs, 6.1–6.5) — PR19 flakiness, PR19 target list, PR17 readability, PR14 refactor exception, scope-shift reversal.

Priority distribution: Critical 6 (23%), High 9 (35%), Medium 8 (31%), Low 3 (12%) — close to the target ~25/40/25/10 mix. Research is performed across prep Tasks 2–11 per the Task-to-Unknown Mapping in `KNOWN_UNKNOWNS.md` Appendix; the authoritative scheduling budget remains the per-task total in this PREP_PLAN (28–39h across all 11 tasks).

Sprint 25 end-of-sprint KUs (KU-33, KU-34, KU-35, KU-36) carry forward into Sprint 26 prep at the Appendix level (drives Category 1 + Task 9 + regression-canary protection); KU-33 specifically is the basis for Sprint 26 Priority 1.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md && echo "EXISTS"
wc -l docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md
# Count only numbered unknowns (exclude template headers)
grep -cE "^## Unknown [0-9]+\.[0-9]+:" docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md
# Expected: 26
grep -cE "^# Category " docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md
# Expected: 6
```

### Deliverables

- ✅ `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` with 26 unknowns across 6 categories
- ✅ Task-to-Unknown mapping table (Appendix)
- ✅ Sprint 25 carryforward KU-33 through KU-36 migrated into Sprint 26 Appendix (with full text + drives-which-unknown forward-links)
- ✅ "Unknowns Verified" metadata added to PREP_PLAN.md Tasks 2–10 (Task 11 integrates all)
- ✅ CHANGELOG.md updated with Task 1 completion entry (under Sprint 26 Preparation)

### Acceptance Criteria

- [x] ≥ 20 unknowns documented (26 created)
- [x] All 5 priority areas have at least 3 unknowns each (Cat 1: 6, Cat 2: 4, Cat 3: 3, Cat 4: 4, Cat 5: 4, Cat 6: 5)
- [x] Sprint 25 end-of-sprint KUs (KU-33, KU-34, KU-35, KU-36) migrated to Sprint 26 numbering (Appendix: KU-33 → drives Cat 1; KU-34 → drives 6.3; KU-35/KU-36 → regression-canary protection)
- [x] All Critical/High unknowns have verification method + deadline assigned
- [x] Task-to-Unknown mapping table covers Tasks 2–11

---

## Task 2: Identify Sprint 25 Scope-Shifted Model (PR18)

**Status:** ✅ COMPLETE
**Priority:** Critical
**Estimated Time:** 1–2 hours (actual: ~1.5h)
**Completed:** 2026-05-07
**Deadline:** Before Sprint 26 Day 1 (must complete before Task 9 baseline)
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 6.5 (will Sprint 25 1-model scope shift reverse during Sprint 26?)

### Objective

Identify which model's convexity status changed during Sprint 25 Days 1–10 to cause the in-scope denominator to shift from 143 to 142, and document the reason in `BASELINE_METRICS.md` §5. This is **Sprint 25 retrospective process recommendation PR18**.

### Why This Matters

The Sprint 25 Day 14 final retest used 142 in-scope models; the Sprint 25 Day 0 baseline (`docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md`) used 143. The 1-model reduction is small (1/143 = 0.7%) and was treated as a runtime filter rather than a scope edit per `BASELINE_METRICS.md` §5 — but the specific model that shifted is currently undocumented. Sprint 26's bucket-provenance baseline (Task 9) cannot be accurate without resolving this. If the shift was triggered by a Sprint-25 code change (e.g., the Day 1 grammar / determinism work), Sprint 26 should know which model is affected and why.

### Background

- Sprint 25 retrospective §"What We'd Do Differently" #5 (PR18): "The 1-model 143 → 142 scope shift during Sprint 25 wasn't traced to a specific model. Sprint 26 prep should run a `git diff` between the Day 0 baseline `gamslib_status.json` and the Day 14 final to identify which model's convexity status changed and document the reason in the SPRINT_LOG."
- Sprint 25 Day 14 SPRINT_LOG: "Per `BASELINE_METRICS.md` §5, the scope-freeze policy treats convexity-status reclassification as a runtime filter (similar to the multi-solve gate handling of `danwolfe`/`decomp`) rather than a scope edit requiring re-freeze."
- Sprint 25 PROJECT_PLAN.md footnote ⁶: "identifying the specific model is a Sprint 26 prep item (see Sprint 25 retrospective PR18)."

### What Needs to Be Done

1. **Locate the Sprint 25 Day 0 baseline `gamslib_status.json`** — likely under `data/gamslib/archive/` (the earliest Sprint 25 archive, dated around 2026-04-21) or recoverable via `git log --follow data/gamslib/gamslib_status.json | head -50` to find the commit closest to Sprint 25 Day 0.

2. **Locate the Sprint 25 Day 14 final `gamslib_status.json`** — `git log --oneline -- data/gamslib/gamslib_status.json | grep "Sprint 25 Day 14"` should surface the commit (`58bcbdc1` or later).

3. **Diff the two snapshots** — focus on the `convexity.status` field per model. Identify which model(s) changed status and what the new status is.

4. **Determine the trigger** — for each changed model, look at git history of the model's `data/gamslib/raw/<model>.gms` file (if changed) or the convexity-detection code (`src/ir/...` if applicable) to identify the Sprint-25 commit that triggered the reclassification.

5. **Document the finding** in `BASELINE_METRICS.md` §5 ("Scope Freeze") — under a new sub-§"Sprint 25 Mid-Sprint Reclassification". Include: model name, prior status, new status, triggering commit (SHA + brief description), and the policy classification (runtime filter vs scope edit).

### Changes

- Added §5.1 "Sprint 25 Mid-Sprint Reclassification" to `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` documenting the abel `likely_convex` → `non_convex` reclassification with triggering commit `c922bb2d`, evidence (indefinite-eigenvalue lambda matrix from Sprint 25 Day 8 reassessment), and policy classification (runtime filter — same handling as the existing 7 `non_convex` `ps*_s*` models).
- Added a forward-link `> **Update (Sprint 26 Prep Task 2 — PR18):** ...` block to `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 §"Scope: 143 → 142" pointing at the new BASELINE_METRICS.md §5.1.
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknown 6.5 with full Verification Results (Status / Verified by / Date / Findings / Evidence / Decision).

### Result

The Sprint 25 scope-shifted model is **`abel`**, reclassified from `likely_convex` to `non_convex` on 2026-04-25 (Sprint 25 Day 4) via commit `c922bb2d`. The reclassification reflects a fundamental property of the abel model — the lambda matrix has indefinite symmetric-part eigenvalues approximately `[-0.047, 1.047]`, making the criterion's `u`-quadratic genuinely non-convex. Multi-start NLP showed CONOPT finds a unique objective only because the linear `stateq` dynamics tightly constrain the feasible set; the MCP/PATH formulation doesn't have that constraint-induced uniqueness, so PATH converges to a different valid stationary point. Tracked via #1313 (CLOSED during Sprint 25; closing did NOT restore convexity — it documented that the warm-start path doesn't apply). **Reversible during Sprint 26: NO.** Sprint 26 baseline (Task 9) freezes scope at 142 in-scope models, matching the Sprint 25 Day 14 final.

### Verification

```bash
# Locate Day 0 vs Day 14 baselines
ls data/gamslib/archive/ | sort
git log --oneline --diff-filter=M -- data/gamslib/gamslib_status.json | head -10

# Verify the abel reclassification is documented in BASELINE_METRICS.md §5.1
# (grep wider context — the §5.1 sub-section runs ~20 lines and the abel-specific
# Model/status lines start ~3-4 lines below the heading)
grep -A20 "Sprint 25 Mid-Sprint Reclassification" docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md | grep -E "Model:|likely_convex|non_convex|abel"
# Expected: lines naming abel + likely_convex → non_convex transition

# Verify forward-link in SPRINT_LOG.md Day 14
grep -A2 "Sprint 26 Prep Task 2 — PR18" docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md
# Expected: forward-link block under §"Scope: 143 → 142"
```

### Deliverables

- ✅ New sub-§5.1 "Sprint 25 Mid-Sprint Reclassification" in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md`
- ✅ abel model identified + new convexity status (`non_convex`) + triggering commit SHA (`c922bb2d`) documented inline
- ✅ Forward-link block added to `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry referencing the new sub-section
- ✅ Updated KNOWN_UNKNOWNS.md with verification results for Unknown 6.5

### Acceptance Criteria

- [x] Specific model identified by name (`abel`)
- [x] Triggering commit SHA + brief description (`c922bb2d` — "Mark abel non-convex in gamslib_status.json + file #1313 for warm-start fix")
- [x] Policy classification stated (runtime filter — same handling as the existing 7 `non_convex` `ps*_s*` models per `BASELINE_METRICS.md` §5)
- [x] `BASELINE_METRICS.md` §5 updated with the new sub-section (§5.1)
- [x] Unknown 6.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Pattern C Hypothesis Validation (PR16)

**Status:** ✅ COMPLETE
**Completed:** 2026-05-07
**Priority:** Critical
**Estimated Time:** 6–8 hours
**Actual Time:** ~5 hours
**Deadline:** Before Sprint 26 Day 1 (this is the Sprint 26 PR16 implementation; must complete before Priority 1 work begins)
**Owner:** Sprint planning + AD/KKT engineer
**Dependencies:** Task 1 (Pattern C unknowns inform validation focus)
**Unknowns Verified:** 1.1 (gate selectivity on canaries), 1.2 (sameas-decomposed SAM-block detection), 1.3 (#1334 interaction), 1.4 (mathematical equivalence), 1.5 (canary risk count), 1.6 (PROCEED/REPLAN signal binary)

### Objective

Apply the Sprint 25 Day 5 methodology — **trace capture + emitted-artifact byte comparison against formal symbolic derivative** — to the Pattern C generalization hypothesis on 2–3 representative target models BEFORE committing the 12–18h Priority 1 budget. If the hypothesis is disproved on any of the 2–3 models, replan Priority 1 during prep rather than mid-sprint.

### Why This Matters

This task is the codified instance of Sprint 25 retrospective process recommendation **PR16** ("Run hypothesis-validation pre-Sprint-0 for multi-issue workstreams sharing a single hypothesized root cause"). Sprint 25 spent Days 1–4 on Phase 1 alias-AD work that produced no Match gain because the underlying Pattern A hypothesis was wrong about the cohort. The Day 5 pivot disproved it in 1 day via this exact methodology. **Running it pre-Day-0 is the primary mitigation for the alias-AD architectural-drift risk that has now hit three consecutive sprints (S23, S24, S25).**

The Pattern C generalization hypothesis (per Sprint 25 retrospective Priority 1 + KU-33): the launch-shape gate's "alias-only conditional sum" detection (#1306, narrow) extends to **plain-alias enumeration (no `$cond` filter required)** AND **`sameas`-decomposed SAM-block aliases**. If true, generalizing the gate unblocks #1354 (camcge), #1355 (cesam2), #1356 (fawley), #1357 (otpop) plus removes the #1306 xfail — projected +4 Solve / +3–4 Match.

If the hypothesis is wrong (e.g., the bug surface differs across the 4 models, or the gate broadening regresses Tier 0/1 canaries), Sprint 26 needs to know **before** committing the 12–18h budget so Priority 1 can be replanned during prep.

### Background

- Sprint 25 Day 5 methodology: `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` §"TL;DR" + §"Evidence — AD layer is correct"
- Sprint 25 Day 7 cohort sweep (the per-model classification basis for the "Pattern C generalizes" hypothesis): `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table"
- Sprint 25 retrospective §"Day 5 Pivot Retrospective" (the methodology rationale + PR16 codification)
- Sprint 26 PROJECT_PLAN.md §Priority 1 explicitly calls out the pre-Sprint-0 hypothesis validation: "validate the 'plain-alias variant of Pattern C' hypothesis on 2–3 representative models (e.g. camcge + cesam2 + fawley) using the Day 5 methodology"
- 4 target models with in-tree issue docs:
  - `docs/issues/ISSUE_1354_camcge-phantom-indexoffset-stationarity-141.md`
  - `docs/issues/ISSUE_1355_cesam2-phantom-indexoffset-nu-colsum-141.md`
  - `docs/issues/ISSUE_1356_fawley-stationarity-domain-violations-171.md`
  - `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md`

### What Needs to Be Done

1. **Pick 3 representative target models** — recommended: camcge + cesam2 + fawley (covers the two `$141` shapes + the `$171` shape). otpop is held out as a fourth confirmation model since #1357 is "likely subsumed by #1334" per the issue doc.

2. **For each model, run the Day 5 methodology:**

   ```bash
   mkdir -p /tmp/sprint26-day0-validation
   for m in camcge cesam2 fawley; do
     SPRINT25_DAY2_DEBUG=1 .venv/bin/python -m src.cli \
       data/gamslib/raw/${m}.gms \
       -o /tmp/sprint26-day0-validation/${m}_mcp.gms \
       --skip-convexity-check --quiet \
       2> /tmp/sprint26-day0-validation/${m}_trace.stderr
   done
   ```

3. **For each model, hand-derive the formal KKT for one target stationarity equation** (the one carrying the phantom IndexOffset, per the ISSUE_*.md doc). Example for camcge: `stat_dk(i)`. Compute the expected derivative w.r.t. `dk(i)` from the source NLP using calculus rules — explicitly, no shortcuts.

4. **Byte-compare the emitted form against the hand-derived form.** The hypothesis is confirmed for that model iff the difference is exactly the phantom IndexOffset enumeration (and nothing else). If the difference includes other terms, the hypothesis is partial / wrong for that model.

5. **For each model, prototype the Pattern C generalization on a 1-line patch** in `src/kkt/stationarity.py`. The patch should remove the `$cond` filter check from the gate's predicate (and add `sameas`-block awareness for cesam2). Re-run the model and verify the emitted form matches the hand-derived form.

6. **Run the Tier 0/1 canary regression** (11 models — `dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive`) under the prototype patch. Any regressions are evidence that the broader gate is too permissive.

7. **Document the findings** in a new `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md`:
   - Per-model: hypothesis CONFIRMED / PARTIAL / DISPROVED
   - Per-model: hand-derived formal KKT excerpt + emitted-form excerpt + diff
   - Tier 0/1 canary regression results
   - Recommended patch shape for Sprint 26 Day 1
   - **Recommendation:** PROCEED with Priority 1 as planned / REPLAN Priority 1 (with proposed alternative)

### Changes

- Created `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` documenting per-model verdicts (camcge ✅, cesam2 ✅, fawley ❌, otpop ⚠), prototype-patch canary regression results (2 of 11 canaries + launch regress), the #1351 architectural blocker analysis, and the Sprint 26 Priority 1 replan recommendation.
- Saved hand-derived formal-KKT excerpts at `/tmp/sprint26-day0-validation/{camcge,cesam2,fawley}_formal_kkt.md` (advisory, not committed) — referenced from the validation doc.
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 with Status ✅ VERIFIED + Findings/Evidence/Decision per the validation doc.
- No source-code modifications (the prototype patch in `src/kkt/stationarity.py:4339` was applied for the canary regression experiment then reverted before commit; full source preserved in the validation doc §5).

### Result

**Recommendation: REPLAN Sprint 26 Priority 1.**

Per-model verdicts:
- **camcge (#1354):** ✅ CONFIRMED Pattern C plain-alias variant. 21 phantom-offset terms in `stat_dk`; formal KKT confirms equivalence to `sum(j, imat(j,i)*nu_ieq(j))`.
- **cesam2 (#1355):** ✅ CONFIRMED Pattern C `sameas`-decomposed variant. 18 phantom-offset terms in `stat_tsam`; sameas-block guards must be preserved by the consolidated builder.
- **fawley (#1356):** ❌ DISPROVED. 0 phantom offsets; `$171` errors trace to `comp_up_u(c)` referencing `crdat(c,"supply")` where `crdat` is on subset `cr` — comp_up subset/superset domain widening, NOT Pattern C.
- **otpop (#1357, held-out):** ⚠ PARTIAL. `$171` blocker is the same comp_up shape as fawley; the small `$141` cascade (5 phantom-offset markers) is the #1334 ParamRef bug. Primary classification: NOT Pattern C.

Tier 0/1 canary regression on prototype patch (broader gate, no `$cond` filter required):
- **3 of 12** byte-stable regressions (quocge, prolog, launch). Launch regression reproduces the Sprint 25 #1351 bug. Quocge and prolog are NEW regressions on canaries that were previously byte-stable.
- 122 gate firings on 11 canaries alone (vs expected 4–8 across all 142 in-scope models per Unknown 1.1) — broader predicate is far too permissive.

**Sprint 26 Priority 1 must be a TWO-PHASE workstream**, not a 1-line `$cond` removal:
- **Phase A (~6h):** Restore the launch fix per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" — make the consolidated zero-offset builder emit `sum(j$(domain_filter), <body>)` over the equation domain, preserving cross-element aggregation. Remove the `xfail` on `test_alias_only_conditional_sum_emits_no_phantom_offsets`.
- **Phase B (~6–10h):** Generalize the gate predicate to plain-alias (catches camcge) and `sameas`-decomposed (catches cesam2). Re-enable on the 2 confirmed Pattern C target sites only.

**Reduced target list 4 → 2** (camcge + cesam2). fawley + otpop reclassify to Priority 5 / a new comp_up subset-domain widening workstream.

**Revised projection:** +2 Solve / +2 Match (vs original +4 / +3–4). Sprint 26 retrospective will compare against this projection to validate PR16.

**PR16 (pre-Sprint-0 hypothesis validation) is validated as a high-value process recommendation.** ~5h of prep saves ~10–16h of mid-sprint waste. Recommend codifying PR16 into CONTRIBUTING.md as a sprint-prep checklist requirement for any sprint with 3+ issues claimed to share a single hypothesized root cause.

### Verification

```bash
# Trace files captured (3 primary targets — camcge, cesam2, fawley —
# plus 1 held-out model — otpop — per PATTERN_C_HYPOTHESIS_VALIDATION.md §1.1)
ls /tmp/sprint26-day0-validation/*_trace.stderr | wc -l   # Expected: 4
ls /tmp/sprint26-day0-validation/*_mcp.gms | wc -l        # Expected: 4

# Validation document exists
test -f docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md && echo "EXISTS"

# Per-model verdict sub-sections (§2.1 camcge, §2.2 cesam2, §2.3 fawley, §2.4 otpop held-out)
grep -cE "^### 2\.[1-4] " docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md   # Expected: 4

# Tier 0/1 canary rows in §4 (canary regression report) of PATTERN_C_HYPOTHESIS_VALIDATION.md.
# Narrowed via awk to the §4 section so this check specifically validates §4 — independent
# of any other table (e.g. §1.5's gate-firing table) that happens to share canary names.
awk '/^## 4\./,/^## 5\./' docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md \
  | grep -cE "^\| (dispatch|quocge|partssupply|prolog|sparta|gussrisk|ps2_f|ps3_f|ship|splcge|paklive) "   # Expected: 11
```

### Deliverables

- Trace files for 3 target models at `/tmp/sprint26-day0-validation/<model>_trace.stderr` (advisory, not committed)
- `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` with per-model hypothesis status + canary regression report + recommendation
- 1-line prototype patch (committed as a draft branch under `prototype/sprint26-pattern-c-validation` if the recommendation is PROCEED; left as a code excerpt in the validation doc otherwise)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6

### Acceptance Criteria

- [x] Day 5 methodology applied to 3 target models (camcge, cesam2, fawley)
- [x] Hand-derived formal KKT documented for at least 1 target stationarity equation per model
- [x] Byte-comparison vs emitted form documented per model
- [x] Prototype patch tested on Tier 0/1 canaries
- [x] Recommendation written: PROCEED / REPLAN with rationale
- [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Pattern A Cohort Reclassification Pre-Work

**Status:** ✅ COMPLETE
**Completed:** 2026-05-07
**Priority:** High
**Estimated Time:** 3–4 hours
**Actual Time:** ~2 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 2.1 (Day 7 sweep accuracy post-S25), 2.2 (per-issue action), 2.3 (test xfail surface), 2.4 (source/docs cross-references)

### Objective

For each of the 6 Pattern A cohort issues (#1138, #1139, #1140, #1142, #1145, #1150), produce a per-issue action plan: **subsume into existing tracker** (e.g., #1334) / **close as duplicate of new Priority 1 work** (subsumed by Pattern C generalization) / **close-and-refile** under correct shape / **investigate further** (Sprint 27). This is the prep work for Sprint 26 Priority 2 — the actual reclassification PRs land during execution.

### Why This Matters

Per Sprint 25 Day 7 cohort sweep, the original Pattern A cohort is **NOT** actually Pattern A; each issue needs reclassification to its true bug shape. Doing the per-issue action mapping during prep means Sprint 26 Priority 2 execution is mechanical — close issues, file successors, update labels — rather than investigative. This frees Sprint 26 budget for Priority 1 (Pattern C generalization) and Priority 5 (AD residuals).

### Background

- Sprint 25 Day 7 cohort sweep classification: `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table"
- Sprint 25 retrospective §Priority 2 details the per-issue classification:
  - #1138 → Pattern C plain-alias variant (likely subsumed by Sprint 26 Priority 1)
  - #1139 → AD-correct, pipeline-excluded (close with note)
  - #1140 → AD-correct multi-solve dynamics (separate investigation, defer to Sprint 27)
  - #1142 → Pattern C Bug #2 (#1307; subsumed by Sprint 26 Priority 1)
  - #1145 → offset-handling/condition-guard bug (file new Sprint 27 issue)
  - #1150 → split: qabel = Pattern C massive-enumeration variant (subsumed); abel = AD-correct/solver noise (close)
- Sprint 25 Audit: `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` (original Pattern A/B/C/D/E classification)
- #1311 (qabel/abel u-quadratic AD subset-domain bug) was identified during S25 Day 8 reassessment and CLOSED during Sprint 25 — that bug is fixed; Sprint 26 should NOT reopen related concerns.

### What Needs to Be Done

1. **For each of the 6 cohort issues, fetch current state** — `gh issue view #NNNN`. Confirm still OPEN with `sprint-26` label.

2. **For each issue, re-verify Sprint 25 Day 7 classification** — does it still match the current emit (post Sprint 25 fix-in-place series)? Run a quick translate + emit on the canonical model and grep for the documented bug fingerprint.

3. **For each issue, write a per-issue action note:**
   - **Subsume**: link to existing open tracker (e.g., "#1138 → subsumed by Sprint 26 Priority 1; close on Day 1 with forward-link")
   - **Close as resolved**: state evidence (e.g., "#1311 already resolved this bug; verify with grep on emit; close")
   - **Close-and-refile**: draft the new Sprint 27 issue title + body
   - **Investigate further**: Sprint 27 carryforward note; do not act in Sprint 26

4. **Compile into `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md`** — one section per issue with classification, action, and (if "close-and-refile") draft title + body.

5. **Cross-reference test xfails** — search `tests/` for any test that references the 6 cohort issue numbers in docstrings or `xfail(reason=...)`. Any closing must update those references.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` with one section per cohort issue (#1138, #1139, #1140, #1142, #1145, #1150). Each section: Day 7 classification + re-verification on current main + recommended action + closure mechanics.
- Re-verified all 6 cohort issues OPEN on current main with `sprint-26` label via `gh issue view`.
- Re-translated 7 canonical models on current main; saved emit at `/tmp/sprint26-task4-verify/<model>_mcp.gms` (advisory, not committed).
- Cross-referenced test xfails: 1 affected test (`test_alias_only_conditional_sum_emits_no_phantom_offsets`, already references #1142 via xfail reason).
- Cross-referenced src/ + docs/ for issue numbers: 1 source comment (`src/kkt/stationarity.py:4336`) needs update when #1142 closes; no other source/docs references outside `docs/issues/` and `docs/planning/`.
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 2.1, 2.2, 2.3, 2.4 with Status ✅ VERIFIED + Findings/Evidence/Decision.

### Result

**Per-issue action plan codified — Sprint 26 Priority 2 becomes mechanical closure work.**

| Issue | Day 7 → Re-verified | Sprint 26 action |
|---|---|---|
| #1138 (irscge family) | ✅ Pattern C plain-alias confirmed | Subsume into Sprint 26 Priority 1 Phase B (gate generalization) |
| #1139 (meanvar) | ✅ AD-correct confirmed | Close as not-a-bug |
| #1140 (ps2_f_s family) | ✅ AD-correct + now `non_convex` runtime-filter | Close as informational mismatch |
| #1142 (launch) | ⚠ Bug #1 fix rolled back via #1351 → both bugs pending | Subsume into Sprint 26 Priority 1 Phase A (consolidated builder fix) |
| #1145 (cclinpts) | ✅ Condition-guard / sign bug confirmed (NOT Pattern A) | Close-and-refile as Sprint 27 issue (draft title + body in plan) |
| #1150 (qabel + abel) | ❌ STALE — qabel "massive enumeration" GONE on current main; both halves now resolved | Close as resolved (#1312 fixed qabel massive lag enumeration; #1311 fixed the criterion u-gradient drop; abel reclassified `non_convex`) |

**Day 7 sweep accuracy:** 5 of 6 classifications still accurate on current main. 1 stale (#1150 qabel half — already resolved by Sprint 25 #1312 closure for the massive lag enumeration; #1311 separately addressed the criterion u-gradient drop). 1 needs Bug-#1-fix-rollback annotation (#1142 — addressed by Task 3 routing to Phase A).

**Test xfail impact:** 1 affected test (`test_alias_only_conditional_sum_emits_no_phantom_offsets` — already documented to un-xfail after Phase A lands).

**Source/docs reference impact:** 1 source comment update (`src/kkt/stationarity.py:4336`) when #1142 closes.

**Sprint 26 Priority 2 effort estimate:** Reduced from original 2-4h investigative work to **~1.5h mechanical closure** (4 closes + 1 close-and-refile + 1 forward-link to Priority 1 PR + 1 test xfail removal + 1 source comment update). Time saved → Priority 1 (Phase A + B) or Priority 5.

### Verification

```bash
# Action plan exists with per-issue sections
test -f docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md
grep -cE "^## Issue #(1138|1139|1140|1142|1145|1150)" docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md
# Expected: 6

# Test xfail cross-reference scan
grep -rE "#(1138|1139|1140|1142|1145|1150)" tests/ 2>/dev/null
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` with per-issue action plan
- Test-file cross-reference scan results (which tests reference the 6 issue numbers; what update is needed when closing each)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.1, 2.2, 2.3, 2.4

### Acceptance Criteria

- [x] All 6 cohort issues have a per-issue action note
- [x] Each note states: classification + action + (if refile) draft title + body
- [x] Test xfail cross-reference scan documented (zero affected tests OR list of affected tests + planned updates)
- [x] Unknowns 2.1, 2.2, 2.3, 2.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Pattern E Carryforward Status Survey

**Status:** ✅ COMPLETE
**Completed:** 2026-05-07
**Priority:** High
**Estimated Time:** 2–3 hours
**Actual Time:** ~1.5 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 1
**Unknowns Verified:** 3.1 (S25 fix-in-place series bucket-shift), 3.2 (catmix-#1338 specific check), 3.3 (Phase E framing validity)

### Objective

Re-verify the 3 Pattern E carryforward issues (#1141 kand, #1144 catmix, #1147 camshape) under the post-Sprint-25 emit pipeline. Some may have shifted bucket via the Sprint 25 fix-in-place series #1338..#1352 (in particular catmix was on the SetMembershipTest fix list #1338 and may have been recovered).

### Why This Matters

Phase E (Pattern E routing) was cancelled per the literal Sprint 25 Checkpoint 2 NO-GO routing on `path_syntax_error`. The 3 Phase E issues remain open with `sprint-26` label, but their bug shapes may have shifted via the Sprint 25 fix-in-place series. Re-verifying before Sprint 26 fix work begins prevents wasted effort on already-resolved or already-shifted issues.

### Background

- Sprint 25 Day 11 SPRINT_LOG: lists the fix-in-place series #1338..#1352. #1338 specifically is "expr_to_gams now handles IndexOffset as a direct index of SetMembershipTest" affecting catmix/glider/markov/tricp.
- Phase E original design: `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4
- Sprint 25 cohort sweep classified Pattern E (3 issues): `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md`
- Sprint 25 retrospective §Priority 3 (Pattern E carryforward): "Re-verify each before scoping Sprint 26 fix work."

### What Needs to Be Done

1. **For each of #1141, #1144, #1147, fetch current state** — `gh issue view`. Confirm OPEN, `sprint-26` labeled.

2. **For each issue, run translate + GAMS compile-only on the canonical model** (kand, catmix, camshape) using the current main. Solve status is read from `data/gamslib/gamslib_status.json` (Day 14 retest values), not re-run here — solve takes ~1–60s per model and the status file already has authoritative results from the latest pipeline retest. If a fresh solve is needed, follow each translate with `gams /tmp/sprint26-pattern-e/${m}_mcp.gms lo=2` (no `action=c`, default solve).

   ```bash
   mkdir -p /tmp/sprint26-pattern-e
   # Notes for the loop body below:
   # - The `&&` chain ensures gams only runs if translate succeeded.
   # - GAMS' `o=` flag overrides its default listing-file name (which would
   #   otherwise be `<input_basename>.lst`, e.g. `kand_mcp.lst`). The listing
   #   file holds GAMS' own error markers (e.g. $141, $171), which is what
   #   subsequent greps inspect.
   # - Comment lines are placed ABOVE the command (not between `\`-continued
   #   lines), because `\` joins lines in shell and a `#` after `&&` would
   #   silently swallow the rest of the command.
   for m in kand catmix camshape; do
     .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
       -o /tmp/sprint26-pattern-e/${m}_mcp.gms --skip-convexity-check --quiet \
       && gams /tmp/sprint26-pattern-e/${m}_mcp.gms action=c lo=2 \
              o=/tmp/sprint26-pattern-e/${m}_compile.lst || true
   done

   # Verify the artifact exists at the documented path (sanity check — `o=`
   # does override the default name; confirmed empirically on macOS GAMS 53):
   ls /tmp/sprint26-pattern-e/{kand,catmix,camshape}_compile.lst
   ```

3. **For each model, classify the current bug shape:**
   - **Resolved by Sprint 25 fix-in-place series**: model now translates AND solves → close with forward-link to landing commit
   - **Bucket shifted (different category)**: model now fails differently → close original, file new issue under correct category
   - **Unchanged Pattern E shape**: keep open, scope as Sprint 26 fix work in Priority 3

4. **Document in `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md`** — per-model: previous shape, current shape, recommended action.

### Changes

- Created `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` with one section per Phase E carryforward issue (#1141 kand, #1144 catmix, #1147 camshape). Each section: original Sprint-25 symptom + re-verification (translate + GAMS `action=c` compile + `gamslib_status.json` solve status) + verdict + closure mechanics.
- Re-verified all 3 issues OPEN on current main with `sprint-26` label via `gh issue view`.
- Translated + GAMS `action=c` compiled all 3 canonical models on current main; saved at `/tmp/sprint26-pattern-e/<model>_{mcp.gms,compile.lst}` (advisory, not committed) — all 3 translate exit=0 and compile exit=0 with no `$NNN` errors.
- Cross-referenced Sprint 25 SPRINT_LOG.md Day 11 for the #1338..#1352 fix-in-place series — confirmed catmix (#1144) was on the #1338 SetMembershipTest fix list.
- Cross-referenced #1160 (camshape follow-up to #1147) — verified CLOSED.
- Updated `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` Unknowns 3.1, 3.2, 3.3 with Status ✅ VERIFIED + Findings/Evidence/Decision.

### Result

**Per-model status outcome:**

| Issue | Model | Re-verified status (2026-05-07) | Sprint 26 Priority 3 action |
|---|---|---|---|
| #1141 | kand | ⚠ **Unchanged** — translates+compiles clean, solves Optimal, still 92.5% rel_diff | **Keep open** — Sprint 26 fix work needed (alias-AD residual) |
| #1144 | catmix | ✅ **Bucket shifted (largely resolved)** — was `model_infeasible`; now solves Optimal, 0.21% rel_diff | **Close as infeasibility-resolved** — Sprint 25 #1338 SetMembershipTest fix did the work |
| #1147 | camshape | ⚠ **Bucket shifted (new bug)** — was `path_syntax_error`; now `Locally Infeasible` (model_status=5) | **Close-and-refile as Sprint 27 issue** — original framing stale |

**Phase E framing assessment:** Original "Phase E" framing was valid for **only 1 of 3 models** (kand). catmix's bug was a `skip_lead_lag_inference` regression (NOT alias-AD), already resolved by Sprint 25 #1338. camshape's original `$141` compilation error was a bound-emission issue (NOT alias-AD), already resolved by #1147 partial fix + #1160 follow-up. **Recommendation: retire the "Phase E" label**; reclassify kand as a standalone alias-AD residual under Priority 5 (alongside #1334/#1335).

**Sprint 26 Priority 3 effort estimate:** Reduced from original 3-models / 6–10h investigative work to **1 model fix (kand, ~3–6h) + 2 closures (~30min mechanical)**. Time saved: ~3–4h freed for Priority 1 (Phase A + B), Priority 4 (Option 1), or Priority 5 (#1335).

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md
# Per-model verdict sub-sections in PATTERN_E_STATUS.md use
# `### Issue #NNNN: <model> — ...` headings (one per Phase E issue).
grep -cE "^### Issue #(1141|1144|1147): (kand|catmix|camshape)" \
  docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md
# Expected: 3
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` with per-model status + recommended action
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 3.1, 3.2, 3.3

### Acceptance Criteria

- [x] All 3 Phase E models re-verified
- [x] Per-model classification (Resolved / Bucket Shifted / Unchanged) with evidence
- [x] Sprint 26 fix scope updated (which of the 3 actually need fix work in Sprint 26)
- [x] Unknowns 3.1, 3.2, 3.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Profile Option 1 Short-Circuit Approach

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning + AD engineer
**Dependencies:** Task 1
**Unknowns Verified:** 4.1 (S25 design validity), 4.2 (impact projection), 4.3 (#1224 deferral decision), 4.4 (determinism)

### Objective

Verify that the Option 1 short-circuit design from Sprint 25 `PROFILE_HARD_TIMEOUTS.md` is still valid post-Sprint-25, identify exact `src/ad/index_mapping.py` patch sites, and draft the test fixture plan for srpchase + iswnm. Forecast whether Option 1 will recover only srpchase (the documented "tractable in 500s" model) or also unblock 1+ of {iswnm, mexls, nebrazil, sarf}.

### Why This Matters

Sprint 26 Priority 4 budgets 4–6h for Option 1 short-circuit landing. That budget is realistic only if the design is still valid (no Sprint 25 work shifted the failure surface) and the patch sites are pre-identified. Pre-Sprint-0 verification prevents the budget from blowing out into investigative work mid-sprint.

### Background

- Sprint 25 PROFILE_HARD_TIMEOUTS.md (the original Option 1 design): `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md`
  - Recommended fix sites: `src/ad/index_mapping.py::enumerate_equation_instances` (primary) + `resolve_set_members` (same file) + `src/ir/condition_eval.py` (static `SetMembershipTest` failure path)
  - srpchase completes in 500s (tractable); iswnm/sarf/mexls/nebrazil all timeout @ 900s
  - 5 timeouts share unified `ad_jacobian` `SetMembershipTest` Cartesian-explosion bottleneck
- Sprint 25 fix-in-place series #1338..#1341 (catmix/glider/markov/tricp translate via `expr_to_gams` IndexOffset handling for SetMembershipTest indices) — touched the SetMembershipTest path. Verify Option 1 site still applies.
- #1224 (mine ParamRef IndexOffset) is a separate architectural extension and is NOT bundled with Option 1.

### What Needs to Be Done

1. **Re-read `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` Option 1 design.**

2. **Verify the patch sites still exist and have the expected shape post-Sprint-25:**

   ```bash
   grep -nE "def enumerate_equation_instances|def resolve_set_members" src/ad/index_mapping.py
   grep -n "SetMembershipTest" src/ir/condition_eval.py
   ```

3. **Re-profile srpchase + 1 of {iswnm, mexls, nebrazil, sarf}** under current main with `SIGALRM` budget = 900s to confirm the bottleneck shape hasn't shifted.

4. **Draft the patch design** — short-circuit logic + flag/option (if any) + interaction with the existing fall-through path. Do NOT implement; just document the design.

5. **Draft the test fixture plan:**
   - Unit test for `enumerate_equation_instances` short-circuit logic
   - Integration test for srpchase translate completing under budget
   - Optional: integration test for 1+ of {iswnm, mexls, nebrazil, sarf} if profiling shows tractability

6. **Document in `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md`** — design + patch sites + test plan + projected impact (which models recover).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md

# Patch sites verified to exist
grep -c "def enumerate_equation_instances" src/ad/index_mapping.py   # Expected: 1
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` with design + patch sites + test plan + projected impact
- Updated profile data for srpchase + 1 other timeout model (advisory, captured in the design doc)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 4.3, 4.4

### Acceptance Criteria

- [ ] Patch sites verified to still exist in current `src/`
- [ ] srpchase profile re-confirmed (translate completes if budget extends)
- [ ] Patch design documented (no implementation yet)
- [ ] Test fixture plan documented
- [ ] Projected impact stated (which models the Sprint 26 work is expected to recover)
- [ ] Unknowns 4.1, 4.2, 4.3, 4.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: AD Residuals (#1334, #1335) Investigation Recap

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning + AD/KKT engineer
**Dependencies:** Task 1
**Unknowns Verified:** 5.1 (file:line currency), 5.2 (otpop reproducer), 5.3 (#1334 ↔ #1357 subsumption), 5.4 (#1335 tractability)

### Objective

Confirm `ISSUE_1334.md` and `ISSUE_1335.md` are still accurate after Sprint 25 fix-in-place series; verify the otpop NLP-warm-started reproducer; determine whether fixing #1334 actually subsumes #1357 (otpop `$171` from Day 13 carryforward) or if they are independent.

### Why This Matters

Sprint 26 Priority 5 budgets 8–14h for AD residuals. The two issues share the `_replace_indices_in_expr` + `_add_jacobian_transpose_terms_scalar` pair in `src/kkt/stationarity.py`. If the issue docs reference stale file:line numbers (post-Sprint-25 stationarity.py was modified by #1351 launch fix among others), Sprint 26 work will start with broken pointers. Pre-verification catches this.

The #1334 ↔ #1357 subsumption question matters for the bucket-provenance baseline (Task 9) — if #1357 (otpop) is subsumed, otpop's `path_syntax_error` count moves to Priority 5's accountability rather than Priority 1's.

### Background

- `docs/issues/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`
- `docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`
- `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md` — explicitly notes "likely subsumed by #1334"
- Sprint 25 Day 11 fix #1350 (srkandw `tn(t,t)` self-alias) modified `_remap_condition_to_domain` in `src/kkt/stationarity.py`; verify #1334's referenced lines still match.
- Sprint 25 retrospective §Priority 5 confirms: "Both target the `_replace_indices_in_expr` + `_add_jacobian_transpose_terms_scalar` pair in `src/kkt/stationarity.py`. Combined effort 8–14h."

### What Needs to Be Done

1. **Re-read ISSUE_1334.md and ISSUE_1335.md.** Confirm the file:line references match current `src/kkt/stationarity.py`.

   ```bash
   grep -nE "^def _replace_indices_in_expr|^def _add_jacobian_transpose_terms_scalar" \
     src/kkt/stationarity.py
   ```

2. **Re-run the otpop NLP-warm-started reproducer:**

   ```bash
   .venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
     -o /tmp/sprint26-otpop/otpop_mcp.gms --skip-convexity-check --quiet
   # NLP solve + dual transfer + MCP iterlim=0 per ISSUE_1334 §Diagnostic
   # Verify stat_x('1990') residual ≈ 760 (pre-fix) or whatever the current state shows
   ```

3. **Determine the #1334 ↔ #1357 relationship.** Re-emit otpop and compare the `$171` violation lines (217, 247) to the `_replace_indices_in_expr` ParamRef-substitution pattern documented in ISSUE_1334.md §Buggy Emit. If the patterns match: #1334 subsumes #1357 (close #1357 on Day 1 of fix landing). If they don't match: #1357 is independent and needs its own fix work.

4. **Draft the per-issue Sprint 26 work plan** — for each of #1334, #1335: prerequisite verification (does the reproducer still produce the documented residual?), fix approach (per ISSUE doc), and acceptance criteria.

5. **Document in `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md`.**

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md

# File:line references in ISSUE_1334 still match
grep -c "^def _replace_indices_in_expr" src/kkt/stationarity.py   # Expected: 1
grep -c "^def _add_jacobian_transpose_terms_scalar" src/kkt/stationarity.py   # Expected: 1
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md` with #1334 / #1335 / #1357 relationship analysis
- Confirmed file:line references (or updates to ISSUE_1334.md / ISSUE_1335.md if stale)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.1, 5.2, 5.3, 5.4

### Acceptance Criteria

- [ ] ISSUE_1334.md and ISSUE_1335.md verified accurate (or updated)
- [ ] otpop reproducer re-run; current residual documented
- [ ] #1334 ↔ #1357 subsumption decision made with evidence
- [ ] Sprint 26 fix scope clarified (do #1334 + #1335 alone close #1357, or are 3 issues to fix?)
- [ ] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Design Pre-Merge Solve-Time Validation CI (PR19)

**Status:** 🔵 NOT STARTED
**Priority:** High
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 26 Day 1 (CI extension lands during Sprint 26 execution per the PROJECT_PLAN.md schedule)
**Owner:** Sprint planning + CI engineer
**Dependencies:** Task 1
**Unknowns Verified:** 6.1 (PR19 flakiness on canaries), 6.2 (PR19 target list selection)

### Objective

Design the CI extension for emit-affecting changes per Sprint 25 retrospective process recommendation **PR19**. The extension runs a fast-suite `make test` PLUS a 30s PATH solve on a configurable target list when files under `src/emit/` or `src/kkt/stationarity.py` change. Specifically targets the structural-emit-change failure mode that bit Sprint 25's #1308 launch fix (passed unit + compile-only validation but produced locally-infeasible MCP at full PATH solve).

### Why This Matters

Sprint 25's #1308 Pattern C launch fix passed all unit tests and `gams action=c` compile-only validation, but produced a locally-infeasible MCP at full PATH solve. This was caught only via the Day 14 final pipeline retest, leading to the #1351 same-sprint rollback. Sprint 26's Priority 1 (Pattern C generalization) is structurally similar — emit-shape-changing — and PR19 is the codified mitigation.

### Background

- Sprint 25 retrospective §"What We'd Do Differently" #3 (PR19): "Structural gates that change emit shape should require a full PATH solve (or at minimum, a `model_optimal_presolve` round-trip) on the target model BEFORE merge."
- Existing CI: `make test` runs ~4,735 tests in ~10min. Target list for PR19 needs to add ~30s PATH solve per model = ~1.5min for 3 models.
- Sprint 26 PROJECT_PLAN.md §Priority 1 explicitly references PR19: "the structural emit change must pass a full PATH solve on each target model BEFORE merge — not just unit + compile-only."

### What Needs to Be Done

1. **Survey existing CI** — `.github/workflows/*.yml` to understand current trigger / job structure.

2. **Decide trigger conditions:**
   - File patterns: `src/emit/*.py`, `src/kkt/stationarity.py`, possibly `src/ad/derivative_rules.py`
   - PR-only (not push to main, since main should already be validated)
   - Skippable via PR label `skip-emit-solve-ci` for refactor-only PRs that don't change emit semantics (the label name is plain text — no brackets — to keep it consistent with the `byte-stable-refactor` label introduced in Task 10)

3. **Decide target model list:**
   - Minimum: the 4 Pattern C target models (camcge, cesam2, fawley, otpop) — ensures PR19 catches Pattern C work specifically
   - Recommended: + 3 Tier 0 canaries (dispatch, quocge, partssupply) — ensures PR19 catches regressions on previously-solving models
   - Configurable via `.github/path-solve-ci-targets.txt`

4. **Decide PATH timeout:**
   - 30s per model (per PR19's "or at minimum, a `model_optimal_presolve` round-trip" framing)
   - Total CI overhead: ~30s × 7 models = ~3.5min on top of `make test`

5. **Decide failure handling:**
   - Hard-fail on regression for any Tier 0 canary (these are byte-stable per `BASELINE_METRICS.md` §6 already)
   - Soft-fail on Pattern C target models (informational only — they're expected to fail until Sprint 26 lands the fix)
   - Posts a PR comment with per-model status

6. **Document in `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md`** — design + workflow YAML draft + target list + failure-handling policy + estimated CI overhead.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md

# Existing CI workflows surveyed
ls .github/workflows/ 2>&1
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` with trigger conditions + target list + timeout policy + failure handling
- Draft workflow YAML inline in the design doc (not yet committed to `.github/workflows/`)
- Target-list file design (`.github/path-solve-ci-targets.txt` format)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.1, 6.2

### Acceptance Criteria

- [ ] Trigger file patterns documented
- [ ] Target model list committed (≥ Pattern C 4 + ≥ 3 Tier 0 canaries)
- [ ] PATH timeout policy documented (default 30s, configurable)
- [ ] Failure handling policy documented (hard vs soft fail per model class)
- [ ] CI overhead estimate documented (acceptable for PR latency budget)
- [ ] Unknowns 6.1, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15)

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 2–3 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** Task 2 (need Sprint 25 scope-shift documented before recording the new baseline)
**Unknowns Verified:** 6.3 (PR17 readability), 6.5 (jointly with Task 2 — scope-shift policy decision)

### Objective

Run a full pipeline baseline per **PR6**, freeze the v2.2.x exclusion set per **PR15**, and add the per-failing-model bucket-provenance column ("Sprint 25 bucket → Sprint 26 bucket") to `BASELINE_METRICS.md` per Sprint 25 retrospective process recommendation **PR17**.

### Why This Matters

Sprint 25 retrospective KU-34 captured the central observation: Sprint metrics need to track bucket transitions, not just net counts. Sprint 25's `path_syntax_error` net delta was +1 (11 → 12), but the underlying composition changed substantially: 3 baseline syntax-error models resolved + 4 added (3 transfers + 1 regression). Net counts hide this.

PR17 codifies the requirement: the Sprint 26 baseline must include a per-failing-model "Sprint 25 bucket → Sprint 26 bucket" provenance column. Otherwise the same metric ambiguity will recur at Sprint 26 close.

### Background

- Sprint 25 `BASELINE_METRICS.md` §"Final Headline Metrics" table (the data this prep task extends with provenance)
- Sprint 25 Day 14 SPRINT_LOG entry already includes informal bucket transitions (per-model Day 0 → Day 14 transitions section); Sprint 26 prep formalizes this as a baseline column
- `BASELINE_METRICS.md` §5 (Scope Freeze) — already documents PR15 policy; Sprint 26 baseline maintains the 142-scope freeze (subject to Task 2's scope-shift documentation)
- Pipeline runner: `.venv/bin/python scripts/gamslib/run_full_test.py --quiet` (~2.5h runtime per Sprint 25 Day 14)

### What Needs to Be Done

1. **Pre-baseline check** — confirm Task 2 (scope-shifted model identified) is complete; the baseline write-up depends on accurately documenting the 142 in-scope set.

2. **Run full pipeline baseline:**

   ```bash
   .venv/bin/python scripts/gamslib/run_full_test.py --quiet 2>&1 | tee /tmp/sprint26-baseline.log
   ```

3. **Record headline metrics** — Parse / Translate / Solve / Match + 4 outcome_category counts. Compare against Sprint 25 final to confirm no inadvertent regressions between Sprint 25 close (2026-05-05) and Sprint 26 Day 0.

4. **Build bucket-provenance table** — for each model in any failure bucket (`path_syntax_error`, `path_solve_terminated`, `model_infeasible`, `path_solve_license`, `translate_failure_*`), record:
   - Model name
   - Sprint 25 Day 14 bucket (from Sprint 25 SPRINT_LOG.md Day 14 entry transition table)
   - Sprint 26 Day 0 bucket (from this baseline run)
   - Transition note (unchanged / changed / new failure / recovered)

5. **Freeze v2.2.x exclusion set** — confirm `data/gamslib/gamslib_status.json` exclusion list is unchanged from Sprint 25 final; record SHA or schema version in the baseline doc.

6. **Create `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md`** following Sprint 25 BASELINE_METRICS.md format, with the new bucket-provenance column included in §"Failure Composition" sub-table.

7. **Update `data/gamslib/gamslib_status.json`** if the baseline run produced changes (per Sprint 25 Day 14 prompt convention; commit as part of this prep task).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md
# Headline metrics recorded
grep -c "^| Parse " docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md   # Expected: ≥ 1
# Bucket-provenance table present
grep -c "Sprint 25 bucket" docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md   # Expected: ≥ 1
# Pipeline retest succeeded
grep "exit code" /tmp/sprint26-baseline.log | tail -1
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` with headline metrics + bucket-provenance column
- Updated `data/gamslib/gamslib_status.json` (committed)
- Updated `data/gamslib/mcp/*.gms` artifacts where regenerated (advisory per `BASELINE_METRICS.md` §6)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 6.3, 6.5

### Acceptance Criteria

- [ ] Full pipeline baseline run completed (exit 0)
- [ ] Headline metrics match Sprint 25 final (or deltas explained)
- [ ] Bucket-provenance column added per failing model
- [ ] Scope freeze documented (v2.2.x exclusion list unchanged)
- [ ] `gamslib_status.json` committed
- [ ] Unknowns 6.3, 6.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Update CONTRIBUTING.md for Emit-PR `.gms` Diffs (PR14 Reaffirmation)

**Status:** 🔵 NOT STARTED
**Priority:** Medium
**Estimated Time:** 1 hour
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** None
**Unknowns Verified:** 6.4 (refactor-only PR exception design)

### Objective

Add a hard contributor rule to `CONTRIBUTING.md`: every PR that touches `src/emit/*.py` (or `src/kkt/stationarity.py`) must include at least one regenerated `.gms` artifact from an affected model in the diff. This is the codified instance of Sprint 25 retrospective **PR14 reaffirmation**.

### Why This Matters

Sprint 25's #1349 `.fx → .l` side-effect fix passed pindyck integration tests but introduced a clobbering bug on clearlak that was only caught by Copilot reading the regenerated `.gms` artifact during PR #1360 review. The bug had been live in main for several days. PR14 from Sprint 24 originally called for mid-sprint "read the generated MCP" reviews; the Sprint 25 reaffirmation elevates this to a per-PR contributor rule for emit-affecting changes.

### Background

- Sprint 25 retrospective §"What We'd Do Differently" #4 (PR14 reaffirmation): "Reaffirm and elevate: every PR that touches `src/emit/*.py` should have at least one regenerated `.gms` artifact from an affected model in the diff, and reviewers should read the relevant section."
- Existing CONTRIBUTING.md (the file referenced in README.md §Contributing).
- Companion rule: PR19 CI extension (Task 8) — automates a portion of this concern but doesn't replace human review.

### What Needs to Be Done

1. **Read current `CONTRIBUTING.md`** to identify the right section for the new rule (likely a §"PR Submission Checklist" or §"Emit Changes" section).

2. **Draft the rule:**

   > **Emit-affecting PRs:** Every PR that modifies any file under `src/emit/` or `src/kkt/stationarity.py` MUST include at least one regenerated `.gms` artifact from an affected model in the diff. Use `.venv/bin/python -m src.cli data/gamslib/raw/<model>.gms -o data/gamslib/mcp/<model>_mcp.gms --skip-convexity-check --quiet` to regenerate. Reviewers MUST read the relevant section of the regenerated artifact. Refactor-only PRs that pass byte-diff verification across the corpus may apply the `byte-stable-refactor` PR label (no brackets — plain GitHub label name) and document the verification command in the PR description in lieu of an artifact diff.

3. **Add the rule** to the appropriate `CONTRIBUTING.md` section.

4. **Add a corresponding entry** to `.github/PULL_REQUEST_TEMPLATE.md` (if one exists) under the checklist.

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
grep -cE "Emit-affecting PRs|src/emit|byte-stable-refactor" CONTRIBUTING.md   # Expected: ≥ 3
test -f .github/PULL_REQUEST_TEMPLATE.md && \
  grep -cE "regenerated.*\.gms|Emit-affecting" .github/PULL_REQUEST_TEMPLATE.md
```

### Deliverables

- Updated `CONTRIBUTING.md` with the emit-PR `.gms` artifact rule
- Updated `.github/PULL_REQUEST_TEMPLATE.md` (if it exists)
- Updated KNOWN_UNKNOWNS.md with verification results for Unknown 6.4

### Acceptance Criteria

- [ ] CONTRIBUTING.md has the new rule with rationale + regeneration command + reviewer instruction
- [ ] Refactor-only exception documented (`byte-stable-refactor` label + PR description requirement)
- [ ] PULL_REQUEST_TEMPLATE.md (if it exists) updated with checklist entry
- [ ] Unknown 6.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Plan Sprint 26 Detailed Schedule

**Status:** 🔵 NOT STARTED
**Priority:** Critical
**Estimated Time:** 3–4 hours
**Deadline:** Before Sprint 26 Day 1
**Owner:** Sprint planning
**Dependencies:** Tasks 1–10

### Objective

Integrate the outputs of all prior prep tasks into a 14-day Sprint 26 execution schedule + per-day execution prompts. The schedule must respect the PROJECT_PLAN.md Sprint 26 entry's ≤ 12 hours/day budget (max 168h total; 50–75h estimated effort with substantial slack).

### Why This Matters

Sprint 26 has the highest-leverage workstream of the post-Sprint-25 backlog (Pattern C generalization), and the schedule must allocate the prep-validated Priority 1 work to specific days while reserving slack for the documented failure modes (Day 5 pivot if PR16 hypothesis validation fails; PR19 CI catching solve-time regressions; PR14 review pass on emit artifacts). The schedule must also accommodate the 14-day cadence (Day 0 setup + Days 1–13 execution) per the PROJECT_PLAN.md Sprint 26 entry.

### Background

- Sprint 26 PROJECT_PLAN.md entry (lines 931–1019): Goal, Components (5 priorities + process recs), Deliverables, Acceptance Criteria, Estimated Effort 50–75h, Risk Level MEDIUM
- Sprint 25 schedule template: `docs/planning/EPIC_4/SPRINT_25/PLAN.md` (15 days; Sprint 26 is 14 days, so adjust accordingly)
- Sprint 25 day-by-day prompts: `docs/planning/EPIC_4/SPRINT_25/prompts/PLAN_PROMPTS.md`
- All prior prep outputs from Tasks 1–10

### What Needs to Be Done

1. **Draft Sprint 26 schedule** at `docs/planning/EPIC_4/SPRINT_26/PLAN.md`:
   - **Day 0:** Prep-task review, sprint kickoff, baseline snapshot, branch setup
   - **Days 1–3:** Priority 1 Pattern C generalization (per Task 3 PROCEED-or-REPLAN recommendation; if PROCEED, the prototype patch from Task 3 lands here)
   - **Day 4:** Priority 1 wrap-up + initial canary regression test under PR19 CI
   - **Day 5:** Checkpoint 1 (Priority 1 lands; +3 to +5 path_syntax_error → solve evidence)
   - **Days 6–7:** Priority 2 Pattern A reclassification (per Task 4 action plan — should be mechanical close-and-refile work)
   - **Days 6–7 (parallel):** Priority 3 Pattern E carryforward (per Task 5 status survey)
   - **Days 8–9:** Priority 4 Translation timeout Option 1 short-circuit (per Task 6 design)
   - **Days 8–10 (parallel):** Priority 5 AD residuals #1334 + #1335 (per Task 7 recap)
   - **Day 10:** Checkpoint 2 (all 5 priorities landing or scoped)
   - **Day 11:** Process recs PR17 (bucket provenance baseline already from Task 9; refresh with mid-sprint findings) + PR19 CI extension landing
   - **Day 12:** Buffer / overflow / emit artifact review pass (PR14 reaffirmation)
   - **Day 13:** Final pipeline retest + metric capture + bucket transition documentation
   - **Day 14 N/A** (14-day sprint, Day 0 + Days 1–13 = 14 days total)

2. **Write day-by-day execution prompts** at `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` (mirror Sprint 25's PLAN_PROMPTS.md format, adjusted for 14-day cadence — Day 0 setup + Days 1–13 execution).

3. **Define checkpoint evaluation criteria:**
   - Checkpoint 1 (Day 5) GO / CONDITIONAL / NO-GO criteria — Priority 1 landed; ≥3 of 4 Pattern C target models recovered
   - Checkpoint 2 (Day 10) GO / CONDITIONAL / NO-GO criteria — all 5 priorities at landed-or-scoped state; aggregate Match Δ ≥ +3

4. **Allocate parallel work** — map Priority 2 + Priority 3 to Days 6–7 (mechanical reclassification work, low compute-time); Priority 4 + Priority 5 to Days 8–10.

5. **Per-day budget check** — confirm no day exceeds 12 hours per the PROJECT_PLAN.md ≤ 12h/day rule. Total ≤ 168h. Estimated work 50–75h leaves 90+ hours of slack.

6. **Update PREP_PLAN.md summary** (this file) with final prep-task status (all tasks marked complete).

### Changes

To be completed.

### Result

To be completed.

### Verification

```bash
test -f docs/planning/EPIC_4/SPRINT_26/PLAN.md
test -f docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md

# Schedule covers all 14 days (Day 0 + Days 1-13)
grep -c "^### Day " docs/planning/EPIC_4/SPRINT_26/PLAN.md   # Expected: ≥ 14

# 2 checkpoints defined
grep -cE "Checkpoint [12]" docs/planning/EPIC_4/SPRINT_26/PLAN.md   # Expected: ≥ 2
```

### Deliverables

- `docs/planning/EPIC_4/SPRINT_26/PLAN.md` — 14-day detailed schedule with per-day budget
- `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` — day-by-day execution prompts (Day 0 + Days 1–13)
- 2 checkpoint evaluation criteria (Day 5 and Day 10)
- Parallel-work allocation across Priorities 2–5
- Updated `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md` with final prep-task status (all 11 tasks COMPLETE)

### Acceptance Criteria

- [ ] Schedule covers all 14 days (Day 0 + Days 1–13)
- [ ] No day exceeds 12 hours of estimated work (per PROJECT_PLAN.md ≤ 12h/day)
- [ ] Total estimated work ≤ 168h (within 14-day budget); target 50–75h per PROJECT_PLAN.md
- [ ] 2 checkpoints defined with quantitative GO / NO-GO criteria
- [ ] Day-by-day prompts match Sprint 25's format
- [ ] Cross-references with all 10 prior prep-task outputs
- [ ] Sprint 25 carryforward KUs (KU-33..KU-36) referenced where they drive specific day-level work

---

## Summary

Sprint 26 preparation comprises 11 tasks spanning ~28–39 hours (3.5–5 working days), covering:

- **Risk identification** (Task 1): Sprint 26 Known Unknowns with ≥ 20 entries
- **Scope-shift documentation** (Task 2): Sprint 25 PR18 carryforward — identify 1-model 143 → 142 reclassification
- **Pattern C hypothesis validation** (Task 3): Sprint 26's central new prep activity — PR16 codification on 3 representative target models
- **Pattern A reclassification pre-work** (Task 4): Per-issue action plan for 6 cohort issues
- **Pattern E status survey** (Task 5): Re-verify 3 Phase E carryforwards under post-Sprint-25 emit pipeline
- **Option 1 short-circuit profile refresh** (Task 6): Verify Sprint 25 PROFILE_HARD_TIMEOUTS.md design still applies
- **AD residuals investigation recap** (Task 7): #1334 / #1335 / #1357 relationship + reproducer verification
- **PR19 CI design** (Task 8): Pre-merge solve-time validation for emit-affecting changes
- **Bucket-provenance baseline + scope freeze** (Task 9): PR17 + PR15 — establish Sprint 26 baseline with per-model transition data
- **CONTRIBUTING.md update** (Task 10): PR14 reaffirmation — emit-PR `.gms` artifact diff requirement
- **Sprint planning** (Task 11): 14-day detailed schedule + day-by-day prompts

### Success Criteria for Prep Phase

- [ ] **All 11 prep tasks complete** before Sprint 26 Day 1
- [x] `docs/planning/EPIC_4/SPRINT_26/KNOWN_UNKNOWNS.md` documents ≥ 20 unknowns across ≥ 6 categories (5 priorities + cross-cutting/process) — **DONE 2026-05-07: 26 unknowns, 6 categories**
- [ ] `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5 updated with Sprint 25 mid-sprint reclassification documentation (Task 2)
- [ ] `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` produces a clear PROCEED / REPLAN recommendation (Task 3)
- [ ] `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` has per-issue action notes for all 6 cohort issues (Task 4)
- [ ] `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` re-verifies all 3 Phase E models (Task 5)
- [ ] `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` confirms patch sites + draft test fixtures (Task 6)
- [ ] `docs/planning/EPIC_4/SPRINT_26/AD_RESIDUALS_RECAP.md` clarifies #1334 ↔ #1357 subsumption (Task 7)
- [ ] `docs/planning/EPIC_4/SPRINT_26/DESIGN_PR19_SOLVE_TIME_CI.md` specifies trigger + target list + timeout + failure handling (Task 8)
- [ ] `docs/planning/EPIC_4/SPRINT_26/BASELINE_METRICS.md` records Day 0 baseline with bucket-provenance column (Task 9)
- [ ] `CONTRIBUTING.md` has the emit-PR `.gms` artifact rule (Task 10)
- [ ] `docs/planning/EPIC_4/SPRINT_26/PLAN.md` + `docs/planning/EPIC_4/SPRINT_26/prompts/PLAN_PROMPTS.md` cover Day 0 + Days 1–13 (Task 11)

### Critical-Path Summary

**Pattern C hypothesis-validation chain (mandatory before Day 1):**
Task 1 → Task 3 → Task 11

**Baseline + scope-shift chain (mandatory before Day 1):**
Task 2 → Task 9 → Task 11

**Pattern A / Pattern E reclassification chain (mandatory before Day 1):**
Task 1 → Tasks 4 + 5 → Task 11

**Process-recommendations chain (mandatory before Day 1):**
Task 1 → Tasks 8 + 10 → Task 11

All chains converge at Task 11 (final schedule). The longest single chain is 3 tasks; with parallel execution across the four chains, the entire prep phase should complete in ~3–4 working days of focused effort.

---

## Appendix A: Document Cross-References

### Sprint 26 Inputs (read for prep)

- `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 26 (lines 931–1019: Goal, Components, Deliverables, Acceptance Criteria, Estimated Effort, Risk Level)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"Sprint 26 Recommendations" (Priorities 1–5) + §"What We'd Do Differently" (PR16–PR19 + PR14 reaffirmation)
- `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` §End-of-Sprint Discoveries (KU-33 through KU-36)
- `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 14 entry (per-model transitions, error-influx accounting)
- `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` (the data Task 9 baseline extends)
- `docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` (per-issue Pattern A reclassification basis)
- `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md` (PR16 methodology basis)
- `docs/planning/EPIC_4/SPRINT_25/PROFILE_HARD_TIMEOUTS.md` (Option 1 short-circuit design)
- `docs/planning/EPIC_4/SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` (original Pattern A/B/C/D/E classification)
- `docs/planning/EPIC_4/SPRINT_25/DESIGN_ALIAS_AD_ROLLOUT.md` (Phase E framing)
- `docs/planning/EPIC_4/GOALS.md` (Epic 4 strategic themes)

### Issue Tracking

23 issues labeled `sprint-26` (per Sprint 25 Day 13 + retrospective):

- **Pattern C target models (4 net-new from Day 13):**
  - #1354 (camcge phantom IndexOffset) — `docs/issues/ISSUE_1354_camcge-phantom-indexoffset-stationarity-141.md`
  - #1355 (cesam2 phantom IndexOffset on `nu_COLSUM`) — `docs/issues/ISSUE_1355_cesam2-phantom-indexoffset-nu-colsum-141.md`
  - #1356 (fawley `$171` domain violations) — `docs/issues/ISSUE_1356_fawley-stationarity-domain-violations-171.md`
  - #1357 (otpop `$171` domain violations — likely subsumed by #1334) — `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md`
- **Pattern A cohort:** #1138, #1139, #1140, #1142, #1145, #1150
- **Phase E carryforward:** #1141, #1144, #1147
- **Pattern C launch:** #1306, #1307
- **Translation timeouts:** #885 (sarf), #931 (iswnm), #932 (nebrazil), #1185 (mexls), #1228 (iswnm second variant)
- **Translation internal_error:** #1224 (mine ParamRef IndexOffset — `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md`)
- **AD residuals from Sprint 25 Day 11 fix-in-place series:** #1334 (`docs/issues/ISSUE_1334_ad-scalar-constraint-spurious-sum-on-subset-param-domain.md`), #1335 (`docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md`)

### Prior-Sprint Retrospectives (for process recommendations)

- Sprint 25: `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` (PR16–PR19 + PR14 reaffirmation review)
- Sprint 24: `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` (PR12–PR15 — PR14 origin)
- Sprint 23: `docs/planning/EPIC_4/SPRINT_23/SPRINT_RETROSPECTIVE.md` (PR9–PR11)
- Sprint 22: `docs/planning/EPIC_4/SPRINT_22/SPRINT_RETROSPECTIVE.md` (PR6–PR8)

### Related Research (reference only)

- `docs/research/multidimensional_indexing.md` — IndexOffset / alias theoretical background
- `docs/research/nested_subset_indexing_research.md` — subset/alias interaction
- `docs/research/minmax_objective_reformulation.md` — reformulation pattern (reference for future Epic 5 work)

### CHANGELOG Context

- `CHANGELOG.md` §[Unreleased] §"Sprint 25 Summary" — includes the 23-issue Sprint 26 backlog list
- `CHANGELOG.md` §[Unreleased] §"Sprint 25 Day 14" — final retest metrics (the prior-sprint baseline for Sprint 26)

---

**Document Created:** 2026-05-06
**Last Updated:** 2026-05-07 (Task 1 completed; Tasks 2–10 gained "Unknowns Verified" metadata)
**Total Prep Tasks:** 11
**Estimated Total Effort:** 28–39 hours
**Critical Path Length:** 3 tasks (longest chain — e.g., Task 1 → Task 3 → Task 11)
