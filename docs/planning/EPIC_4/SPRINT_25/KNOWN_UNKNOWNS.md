# Sprint 25 Known Unknowns

**Created:** 2026-04-19
**Status:** Active — Pre-Sprint 25
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 25 alias-aware differentiation carryforward, emitter/stationarity bug backlog, and smaller Priority 3–5 workstreams.

---

## Overview

This document identifies assumptions and unknowns for Sprint 25 **before** implementation begins. Sprint 25 carries forward the dominant workstream from Sprints 23 and 24 (alias-aware differentiation for ~20 models) and also clears the emitter/stationarity bug backlog surfaced by the Sprint 24 Day 13 review (8 tracked issues, including the #1283 non-determinism bug). Smaller priorities cover the multi-solve gate extension, a dispatcher refactor, and algorithmic attacks on 5 remaining hard translation timeouts.

**Sprint 25 Scope** (per `docs/planning/EPIC_4/PROJECT_PLAN.md` §Sprint 25, Weeks 15–16):

1. **Priority 1: Alias-Aware Differentiation Carryforward** (#1138–#1147, #1150) — 11 open issues, ~20 models. Target: Match 54 → ≥ 62.
2. **Priority 2: Emitter / Stationarity Bug Backlog** (#1275–#1281, #1283) — 8 issues; #1283 non-determinism fix first. Target: path_syntax_error 11 → ≤ 8; unblock 3+ `ganges`-family models.
3. **Priority 3: Multi-Solve Gate Extension** (#1270) — saras-style top-level `eq.m` reads (Approach A).
4. **Priority 4: Dispatcher Refactor** (#1271) — collapse `_loop_tree_to_gams` + `_loop_tree_to_gams_subst_dispatch`.
5. **Priority 5: Translation Timeout — Algorithmic** (#1169, #1185, #1192) — 5 remaining hard timeouts.

**Lessons from Previous Sprints** (Known Unknowns process continues to de-risk sprints):

- Sprint 22: 28 unknowns; early preprocessing research saved 20+ hours.
- Sprint 23: 32 unknowns; KU-27 (subset-superset domain) led to a high-impact fix; KU-31 (LP fast path) proved accurate.
- Sprint 24: 26 prep + 6 end-of-sprint KUs (KU-27..KU-32); KU-27 (Lark disambiguation) unblocked CI and surfaced the `requirements.txt` pinning lesson (KU-28); KU-31 correctly forecast the emitter backlog (#1275–#1281).

**Sprint 24 Key Learning** (from `docs/planning/EPIC_4/SPRINT_24/SPRINT_RETROSPECTIVE.md` §What We'd Do Differently): alias-AD Day-1 start is necessary but not sufficient — it must also be *defended* against urgent-fix interruptions. Two consecutive sprints have deferred the core fix. Sprint 25 prep front-loads the architectural decisions (Task 2 audit + Task 6 rollout design) so Day 1 starts with a contract, not exploration.

**Sprint 24 Carryforward KUs** (from `SPRINT_24/KNOWN_UNKNOWNS.md` §End-of-Sprint Discoveries):

- **KU-29** (saras-style multi-solve gate) → **Unknown 3.1 / 3.2** in this document
- **KU-30** (dispatcher duplication) → **Unknown 4.1 / 4.2** in this document
- **KU-31** (decomp emitter/assembly bugs) → subsumed by Priority 2 tracking issues #1268, #1269 (not in Sprint 25 scope; #1268 will land as part of #1271 refactor if touched)
- **KU-32** (sameas guard validation) → **Unknown 1.5** in this document

---

## How to Use This Document

### Before Sprint 25 Day 1

1. Research and verify all **Critical** and **High** priority unknowns during prep tasks (see §Appendix: Task-to-Unknown Mapping).
2. Create minimal test cases for validation where needed.
3. Document findings in the "Verification Results" subsection of each unknown.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 25

1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly-discovered unknowns in the "Newly Discovered" section (migrate into categories post-sprint).
3. Update with implementation findings as work progresses.
4. Flag any assumption that turns out wrong — don't quietly re-scope around it.

### Priority Definitions

- **Critical:** Wrong assumption will break a sprint priority or require major re-planning (>8 hours of rework).
- **High:** Wrong assumption will cause significant rework (4–8 hours).
- **Medium:** Wrong assumption will cause minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 27

**By Priority:**

- Critical: 7 (26%)
- High: 11 (41%)
- Medium: 7 (26%)
- Low: 2 (7%)

**By Category:**

- Category 1 (Alias-AD Carryforward): 8 unknowns
- Category 2 (Emitter / Stationarity Backlog): 6 unknowns
- Category 3 (Multi-Solve Gate Extension): 3 unknowns
- Category 4 (Dispatcher Refactor): 3 unknowns
- Category 5 (Translation Timeout — Algorithmic): 4 unknowns
- Category 6 (Pipeline Retest + Determinism): 3 unknowns

**Estimated Research Time:** 18–27 hours (spread across prep Tasks 2–10; see `PREP_PLAN.md` §Prep Task Overview for per-task budgets).

Note: the per-unknown `Estimated Research Time` fields in the detail sections below are work-item estimates used to scope individual investigations, not an additive total — multiple unknowns are verified in parallel within a single prep task (e.g., Task 2 covers 7 unknowns in one code-audit pass). The authoritative scheduling budget is the per-task total in PREP_PLAN.md.

---

## Table of Contents

1. [Category 1: Alias-Aware Differentiation Carryforward](#category-1-alias-aware-differentiation-carryforward)
2. [Category 2: Emitter / Stationarity Bug Backlog](#category-2-emitter--stationarity-bug-backlog)
3. [Category 3: Multi-Solve Gate Extension](#category-3-multi-solve-gate-extension)
4. [Category 4: Dispatcher Refactor](#category-4-dispatcher-refactor)
5. [Category 5: Translation Timeout — Algorithmic](#category-5-translation-timeout--algorithmic)
6. [Category 6: Pipeline Retest + Determinism](#category-6-pipeline-retest--determinism)
7. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Alias-Aware Differentiation Carryforward

Sprint 25's Priority 1 workstream — 11 open issues (#1138–#1147, #1150) affecting ~20 models. The single highest-leverage work for Match improvement. This category carries forward Sprint 24 KU-01 through KU-08.

## Unknown 1.1: Do the 11 alias-differentiation issues share a single root-cause pattern?

### Priority

**Critical** — Determines whether Sprint 25 needs one architectural change or 3–5 distinct fixes; drives the Day 1–12 rollout design.

### Assumption

The majority of the 11 open issues (#1138–#1147, #1150) fall into 2–3 distinct root-cause patterns (Pattern A = summation index, Pattern C = offset-alias, Pattern E = non-differentiation adjacency). A single architectural fix to the summation-context / alias-match logic will address Pattern A (≥ 6 of 11 issues), with incremental extensions for Pattern C.

### Research Questions

1. Sprint 24 classified patterns across 12 issues — does that classification still hold for the 11 issues remaining in Sprint 25?
2. Is #1150 (AD regression: distinct sum indices collapse) truly a separate Pattern, or a manifestation of Pattern A?
3. Do Pattern C offset-alias issues (#1143 polygon, #1146 himmel16) share a fix site with Pattern A, or need a distinct `IndexOffset`-aware code path?
4. Are any of the 11 issues actually non-differentiation bugs (Pattern E) that should be re-routed to other workstreams?
5. Does the Pattern classification change if the 54 currently-matching models are re-run under the current parser state?

### How to Verify

**Verification activity:** Prep Task 2 (Audit Alias-AD Carryforward State).

- For each of the 11 issues, re-run the reproducer (`src.cli` on the corpus model) and record the current failure signature.
- Group issues by the specific AD code path that fails.
- Compare against the Sprint 24 Pattern A/B/C/D classification in `docs/planning/EPIC_4/SPRINT_24/ANALYSIS_ALIAS_DIFFERENTIATION.md`.
- Produce a Pattern-per-issue table in `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md`.

### Risk if Wrong

- **4+ distinct fixes needed:** the 12-day alias-AD block is insufficient; sprint must defer ~half the issues to Sprint 26.
- **Hidden Pattern E cases:** fixing differentiation code won't help; per-model workstreams needed.
- **Regression risk underestimated:** what looks like Pattern A is actually Pattern C with a subtle difference, and the fix breaks previously-working matched models.

### Estimated Research Time

2–3 hours (per-issue reproduction + classification), part of Task 2's 3–4h budget.

### Owner

Prep Task 2 (Alias-AD carryforward audit).

### Verification Results

✅ **Status:** VERIFIED (with revision)

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - Sprint 24's 4-pattern classification (A/B/C/D) simplifies to 3 active patterns (A/C/E) after Day 9 investigations reclassified kand (#1141, was B → E) and launch (#1142, was D → A).
  - Pattern distribution: **A = 6 issues (#1138, #1139, #1140, #1142, #1145, #1150)**, **C = 2 issues (#1143, #1146)**, **E = 3 issues (#1141, #1144, #1147)**. Patterns B and D are empty.
  - Pattern A dominates (6 of 11 issues, ~16 comparison-scope models including ISSUE_1140's 7 PS-family models) — a single architectural change to the summation-context / multi-index partial-collapse path addresses them all. This matches the original assumption's "≥6 of 11 issues" threshold.
  - Pattern C (#1143 polygon, #1146 himmel16) requires a separate `IndexOffset.base` extraction in `_alias_match()` (~2–3h incremental on top of A).
  - Pattern E issues route out of alias-AD scope: #1141 → Priority 3 / multi-solve gate, #1144 → IR domain investigation (near-match at 0.2%), #1147 → post-fix empirical re-evaluation (now `model_infeasible`).
- **Evidence:**
  - Full classification table: `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 2
  - Day 9 reclassification: `SPRINT_24/SPRINT_LOG.md` Day 9 (#1225 for kand, #1226 for launch)
  - Landed vs stubbed inventory: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1
- **Decision:** Proceed with assumption — revised to **"Pattern A resolves 6 of 11 issues (≥ the assumed threshold); Pattern C needs a small incremental extension; Pattern E routes elsewhere."** Sprint 25 Priority 1's 12-day block is sufficient for Patterns A + C; B/D being empty shrinks the surface.

---

## Unknown 1.2: Will the alias-AD fix regress any of the 54 currently-matching models?

### Priority

**Critical** — Regressions on the 54-model baseline directly harm Match (target 54 → ≥62, +8). Budget: **≤1 regression tolerated** (which still yields net +7 toward target); ≥2 regressions put the ≥62 target at serious risk and trigger the "stop the sprint" procedure in Task 6's rollout design.

### Assumption

Fewer than 2 of the 54 currently-matching models will regress under the completed alias-AD fix. The `bound_indices` guard introduced in Sprint 24 Day 4 (`_apply_alias_offset_to_deriv`) prevents cross-domain leakage. Dispatch continues to match (per Sprint 24 Day 5 Checkpoint 1).

### Research Questions

1. Which of the 54 matching models actively use aliases? (Sprint 23 identified 8: dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge. Still current?)
2. Do any of the 54 matching models depend on the current (arguably-incorrect) derivative behavior for their match — i.e., fixing the AD changes their numerics enough to unmatch?
3. What's the canary-test list beyond dispatch? (Sprint 24 used quocge + marco + paklive as secondary canaries after Day 5 regressions were found.)
4. Can we generate a "golden file" snapshot of all 54 matching models' stationarity output pre-fix, then diff post-fix?
5. Is there a budget for "net positive" outcomes — if 1 model regresses and 8 new models match, is that acceptable?

### How to Verify

**Verification activity:** Prep Task 2 (carryforward audit produces canary list); Prep Task 6 (rollout design defines regression-guard infrastructure).

- Generate golden-file snapshot of all 54 matching models' MCP output.
- Define the canary-test ladder: dispatch (non-negotiable) → 7 other alias users → 5 recent-regression candidates (e.g., from Sprint 24 Day 5 Checkpoint 1 findings).
- Design a "stop the sprint" trigger if ≥ 2 regressions appear without a same-day root cause.

### Risk if Wrong

- **Sprint Match delta goes negative:** if +8 new matches but −3 regressions, net is +5 — still meets target, but close.
- **Checkpoint 1 NO-GO:** Day 5 evaluation rejects the phase, forcing a narrowed re-design.
- **Alias-AD gets deferred again:** third consecutive sprint with the same workstream as carryforward.

### Estimated Research Time

2 hours (generate golden files + design canary ladder), part of Task 2's 3–4h and Task 6's 3–4h budgets.

### Owner

Prep Task 2 + Prep Task 6.

### Verification Results

✅ **Status:** VERIFIED (partial — canary ladder produced; golden-file snapshot deferred to Task 6)

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - Re-verified alias-user set among the 54 matching models: **10 models** use aliases (not 8 as Sprint 23 reported). The +2 delta is: `nemhaus` dropped (MINLP-excluded via v2.2.0); `partssupply`, `prolog`, `sparta` joined the matching set during Sprint 24.
  - Current alias-user canary list: `dispatch, gussrisk, partssupply, prolog, ps2_f, ps3_f, quocge, ship, sparta, splcge`.
  - `marco` no longer in matching set (was a Sprint 24 Day 5 Checkpoint 1 regression candidate) — drop from canary ladder.
  - `paklive` remains in matching set and remains a regression-sensitive canary (S24 Day 5 fix via `_collect_bound_indices`).
  - Canary ladder produced: Tier 0 (dispatch), Tier 1 (9 alias users + paklive), Tier 2 (44 non-alias matching models via golden-file diff), Tier 3 (Pattern A targets), Tier 4 (Pattern C targets), Tier 5 (infeasibility-adjacent informational).
  - Golden-file snapshot generation itself is deferred to Task 6's rollout design.
- **Evidence:**
  - Canary ladder: `SPRINT_25/AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 5
  - Alias-user re-verification: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Appendix B + §Section 4
- **Decision:** Proceed with assumption — revised to **"≤1 regression tolerated (still yields +7 toward +8 target); canary ladder has 6 tiers (Tier 0 – Tier 5); Task 6 will define the per-tier gate criteria and golden-file infrastructure."**

---

## Unknown 1.3: Is #1150 (distinct sum indices collapse) the same bug as the #1137-family?

### Priority

**Critical** — Determines whether #1150 gets fixed as part of Priority 1's main patch or needs its own sub-workstream.

### Assumption

#1150 is a manifestation of Pattern A (summation index). The AD fix for the #1137-family (qabel/abel, CGE models) will also resolve #1150 as a byproduct.

### Research Questions

1. Does the #1150 reproducer share the same `_diff_sum` / `_partial_collapse_sum` call stack as qabel?
2. Sprint 24 Day 3's single-index sum collapse fix added new lag terms to qabel stat_u — did it also affect #1150's failing model?
3. Does #1150 involve multi-index sums (`sum((i,j), ...)`) that the single-index fix doesn't cover?
4. What's the minimum reproducer for #1150, and does it trigger in any other corpus model?

### How to Verify

- Re-run #1150 reproducer under current parser state; capture stack trace at failure.
- Cross-reference with Sprint 24 Day 3 findings in `SPRINT_LOG.md`.
- Decide: merge #1150 into the Pattern A fix scope, or track separately.

### Risk if Wrong

- Separate #1150 fix needed: +2–3h Sprint 25 effort, but small.
- Assumption right but fix order matters: fix Pattern A first, then verify #1150 is also resolved before closing.

### Estimated Research Time

1–2 hours, part of Task 2's budget.

### Owner

Prep Task 2 (audit + Pattern classification).

### Verification Results

✅ **Status:** VERIFIED

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - #1150 is classified as **Pattern A** alongside the #1137-family (qabel, abel in #1150; CGE/PS/meanvar in #1138–#1140). The root cause is the same upstream gap: the *multi-index partial-collapse* code path in `_partial_collapse_sum` does not apply the single-index `_find_var_indices_in_body`-guided concrete→symbolic free-index recovery that Day 3 added for single-index collapse.
  - Sprint 24 Day 3's single-index fix (landed) *already* applies to qabel and abel. Their residual mismatches (rd 8.2% / 29.8%) are from other assembly instances not covered by single-index collapse — implying the multi-index gap is the same underlying bug for both #1150 and #1138/#1140.
  - No evidence that #1150 needs a separate sub-workstream.
- **Evidence:**
  - Landed work inventory: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1 (Sprint 24 Day 3 entry)
  - Stubbed items: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1 (first "Stubbed" row: `_partial_collapse_sum` multi-index path)
  - Pattern table: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 2 (#1150 and #1138/#1140 all marked Pattern A)
- **Decision:** Proceed with assumption — #1150 merges into the Pattern A fix scope. Close #1150 after the Pattern A main patch lands and qabel/abel residual mismatch clears.

---

## Unknown 1.4: Does the summation-context fix affect all derivative rules or just a subset?

### Priority

**High** — Determines the code-change surface and therefore the review / test effort.

### Assumption

The summation-context threading only needs changes to `_diff_sum`, `_diff_varref`, and `_partial_collapse_sum`. Other derivative rules (`_diff_binary`, `_diff_unary`, `_diff_call`) pass the context through transparently. `_add_indexed_jacobian_terms` in `stationarity.py` does NOT need changes (operates at a higher level). (Reaffirming Sprint 24 KU-01's verified answer.)

### Research Questions

1. Has the AD architecture changed during Sprint 24 in ways that invalidate KU-01's answer?
2. Are there new derivative rules (added in Sprint 24) that don't participate in the context threading?
3. Does the stationarity builder's `_apply_alias_offset_to_deriv` post-processing need summation-context awareness?
4. Are there any `_diff_*` functions that short-circuit when the expression is already simplified — do they lose context in that path?

### How to Verify

- Re-audit `src/ad/` for all `_diff_*` functions and their callers (from `src/kkt/stationarity.py`).
- Trace one Pattern A example (qabel) end-to-end; confirm context reaches the leaves.
- Trace one Pattern C example (polygon) — does the offset-alias code path see the context?

### Risk if Wrong

- **Undocumented derivative rule:** a missing context handler in one rule could break only a specific model; hard to spot without the trace.
- **Fix landed but one model still fails:** need to re-audit mid-sprint.

### Estimated Research Time

2 hours, part of Task 2's budget.

### Owner

Prep Task 2.

### Verification Results

✅ **Status:** VERIFIED (revised)

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - Sprint 23/24 KU-01's answer (`_diff_sum`, `_diff_varref`, `_partial_collapse_sum` receive the summation-context; other `_diff_*` rules pass through transparently) **still holds**. `bound_indices` is threaded through every dispatch target (`src/ad/derivative_rules.py:138–168`) including `_diff_binary`, `_diff_unary`, `_diff_call`, `_diff_power`, `_diff_prod`, and all 15+ specialized function-diff rules.
  - **Revision:** the code-change surface for Sprint 25 extends beyond the three KU-01 functions. Additional fix sites identified by this audit:
    1. `_partial_collapse_sum` multi-index path (in `src/ad/derivative_rules.py`) — needs Day-3-equivalent concrete→symbolic recovery.
    2. `_alias_match` in `src/ad/derivative_rules.py:304–307` — needs `IndexOffset.base` extraction for Pattern C.
    3. `_apply_alias_offset_to_deriv` in `src/kkt/stationarity.py:1743` — multi-position offset handling (currently skipped at line 4389 when ambiguous).
  - `_add_indexed_jacobian_terms` and the representative-instance Jacobian-transpose logic in `build_stationarity_equations` were identified as the *deeper* root cause (Sprint 24 Day 1–2) but are **out of scope** for the first Sprint 25 patch round (Task 6 to confirm).
  - No evidence of new derivative rules added in Sprint 24 that break the threading.
- **Evidence:**
  - Sprint 24 landed inventory: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1
  - Fix-site map: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 3 (Pattern A subsection)
  - S24 SPRINT_LOG Day 1–3 on the Jacobian-transpose depth question
- **Decision:** Proceed with revised assumption — **"primary fix sites are `_partial_collapse_sum`, `_alias_match`, `_apply_alias_offset_to_deriv`; the Jacobian-assembly rewrite is an open question for Task 6 scoping."**

---

## Unknown 1.5: Does `sameas()` guard generation work correctly across all GAMS element types?

### Priority

**High** — `sameas()` guards are the correctness mechanism for alias disambiguation; silent failures on certain element types would corrupt stationarity on affected models.

### Assumption

GAMS `sameas(np, n)` guards emitted by `_alias_match()` work correctly for all element types: numeric (`/1*10/`), string (`/'alpha', 'beta'/`), hyphenated (`'light-ind'`), plus-signed (`'food+agr'`), and dotted (`'x1.l'`). (Partially verifies Sprint 24 KU-05 and end-of-sprint KU-32.)

### Research Questions

1. Does GAMS `sameas()` evaluate correctly when one or both arguments contain special characters (hyphens, plus signs, dots)?
2. Can `sameas()` guards be combined with existing dollar conditions (`$(...)` body) without scope conflicts?
3. What's the compile-time cost of `sameas()` guards on large CGE models (e.g., `twocge`, `korcge`, `lrgcge`)?
4. Does the emitter quote-wrap element names when emitting `sameas()` calls, or rely on them being valid bare identifiers?
5. Are there known GAMSLib models where `sameas()` would evaluate as `FALSE` unexpectedly (e.g., due to case-insensitive element matching)?

### How to Verify

**Verification activity:** Prep Task 6 (rollout design includes sameas-guard regression test matrix).

- Create a synthetic test with 5 element types (numeric, string, hyphenated, plus-signed, dotted); emit a `sameas()`-guarded MCP and verify GAMS compiles + produces expected results.
- Benchmark compile time with/without guards on `twocge` (largest known CGE model).
- Cross-reference with KU-32 status from Sprint 24.

### Risk if Wrong

- **Silent correctness failure:** MCP compiles but produces wrong numerics on models with dotted/hyphenated elements.
- **Compile-time blow-up:** large CGE models become slow to compile (impacts CI and user experience).

### Estimated Research Time

2 hours, part of Task 6's 3–4h budget.

### Owner

Prep Task 6 (rollout design).

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 1.6: Is the offset-alias Pattern C amenable to the same fix as Pattern A?

### Priority

**High** — Pattern C (polygon #1143, himmel16 #1146, cclinpts #1145) is the most architecturally complex sub-pattern and the failure mode for `stat_tz` in twocge (#1277).

### Assumption

Pattern C can be handled by extending the summation-context machinery with `IndexOffset.base` extraction in `_alias_match()`. The fix for Pattern A is a prerequisite but not a complete solution; Pattern C needs incremental add-on work (~2–3h) on top. (Reaffirms Sprint 24 KU-04.)

### Research Questions

1. Sprint 24 KU-04 estimated Pattern C fix success probability at 55–65% — has that changed based on subsequent findings?
2. Does polygon's complete 100% gradient failure indicate a deeper issue than him16's 43% partial failure, or are they the same root cause?
3. Does `#1277` twocge mixed-offset (`mu(j+1,r)` with `pq(j,r)`) require an even more complex extension, or is it the same as polygon?
4. Can Pattern C be feature-flagged separately from Pattern A (Pattern A lands Day 1–3, Pattern C lands Day 5–7)?

### How to Verify

**Verification activity:** Prep Task 2 (classification); Prep Task 6 (rollout Phase 2 targets Pattern C).

- Trace polygon's stationarity generation under current parser state.
- Compare against himmel16 and cclinpts traces.
- Examine `#1277` twocge `stat_tz` generation for same code path.

### Risk if Wrong

- Pattern C needs a separate workstream (+4–6h Sprint 25 effort).
- polygon mismatch (33.8%) persists into Sprint 26.

### Estimated Research Time

2 hours, part of Task 2's budget.

### Owner

Prep Task 2 + Prep Task 6.

### Verification Results

✅ **Status:** VERIFIED

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - Pattern C **depends on Pattern A** landing first. Polygon and himmel16 currently translate successfully (Day 6 IndexOffset.base emitter fix landed) but their derivative math is wrong; the upstream `_partial_collapse_sum` gap blocks correct body differentiation *before* `_alias_match` is even reached for the offset case.
  - The Sprint 24 KU-04 fix-success estimate (55–65%) assumes Pattern A already works. With Pattern A landed, Pattern C should be a small incremental extension: extend `_alias_match()` at `src/ad/derivative_rules.py:304–307` to handle the `IndexOffset` / plain-string mixed case by extracting `expr_idx.base` and calling `_same_root_set`, then emitting an offset-aware guard.
  - #1277 twocge mixed-offset (`mu(j+1,r)` with `pq(j,r)`) uses the same code path; if Pattern C is extensible, twocge benefits as a side effect.
  - Pattern C **can** be feature-flagged separately: Pattern A lands Day 1–3, Pattern C lands Day 5–7 (per Task 6's rollout plan).
  - Polygon's 100% mismatch vs himmel16's 43% is consistent with a single underlying bug, where polygon's entire objective depends on the alias-offset expression and himmel16 has some offset-free terms that partially resolve correctly.
- **Evidence:**
  - Stubbed Pattern C fix site: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1 (second "Stubbed" row)
  - Proposed fix code: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 3 (Pattern C subsection)
  - Dependency on Pattern A: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 3 ("Subsumed-By Relationships")
- **Decision:** Proceed with assumption — Pattern C is amenable to the same architectural family as Pattern A (summation-context), with an `IndexOffset.base` extension. Sequence: Pattern A Days 1–3 → Pattern C Days 5–7.

---

## Unknown 1.7: Will the alias-AD fix recover the 3 alias-related model_infeasible models?

### Priority

**High** — Sprint 25 targets model_infeasible 8 → ≤ 5 (−3); the 3 alias-related infeasibles (camshape, cesam, korcge) are the most plausible path to meeting that target.

### Assumption

Fixing alias-AD will recover camshape, cesam, and korcge from `model_infeasible`. Each has alias-related Jacobian accuracy bugs that cause PATH to return STATUS 5 (locally infeasible) at the initial point. (Continues Sprint 24 KU-14 / KU-16.)

### Research Questions

1. Are camshape, cesam, korcge all Pattern A (summation index), or do they span multiple Patterns?
2. Do the current Jacobian entries for these models match the expected KKT structure — what's the specific residual at the infeasibility?
3. For chenery (tracked separately under #1177 / KU-16), will the alias-AD fix resolve it, or does it need additional work (possibly also blocked by #1283 non-determinism)?
4. Are any of the 3 models expected to surface NEW bugs once the alias fix lands (e.g., they compile correctly but reveal a different failure)?

### How to Verify

**Verification activity:** Prep Task 2 (classify by Pattern + map to infeasibility models).

- Re-run each of camshape / cesam / korcge under current parser state; record the specific infeasibility signature.
- Cross-reference with Sprint 24 retrospective's model_infeasible categorization.
- Estimate recovery probability per model.

### Risk if Wrong

- Miss model_infeasible target (need ≤ 5, currently 8; each of 3 that doesn't recover costs one).
- Priority 1 effort yields less Match improvement than projected.

### Estimated Research Time

1–2 hours, part of Task 2's budget.

### Owner

Prep Task 2.

### Verification Results

✅ **Status:** VERIFIED (with lowered probability)

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - Current state (Day 13 Addendum): **camshape** translates+reaches PATH but returns Locally Infeasible (status 5, objective 6.2 after 48,314 iters); **cesam** returns Infeasible (status 4, objective 0.0, 0 iters); **korcge** returns Locally Infeasible (status 5, objective 338.561 after 770 iters).
  - Pattern classification: #1147 camshape is **Pattern E / A-adjacent** (not in the 11 open AD issues' direct Pattern A scope; recovery depends on whether Jacobian accuracy delta makes the initial point feasible). cesam and korcge are **not** in the 11 open AD issues — they're adjacent infeasibles attributed to alias-related assembly in Sprint 24 Day 7/13.
  - **Recovery is plausible but not guaranteed:**
    - cesam's STATUS 4 + objective=0 at iter 0 suggests a pre-PATH-iteration rejection, possibly Jacobian-sign or bound-setting issue that the alias-AD fix *could* address (recovery probability: moderate, ~40%).
    - korcge's STATUS 5 after 770 iters suggests PATH rejects the trajectory — if alias-AD corrects cross-term coefficients, the trajectory could change (recovery probability: ~35%).
    - camshape's STATUS 5 after 48k iters suggests PATH tried hard but failed — alias-AD fix may or may not resolve (recovery probability: ~40%).
  - **Expected recoveries:** ~1 of 3. Meeting the Sprint 25 model_infeasible target (`8 → ≤5`, −3) is at risk via this path alone and needs a supplementary recovery source (Priority 2 emitter fixes may help via #1275–#1281, or the 5 Category B PATH-convergence models via warm-start).
- **Evidence:**
  - Current infeasibility signatures: `data/gamslib/gamslib_status.json` (extracted in Task 2 data-collection step)
  - Sprint 24 Day 13 alias-related-infeasibility list: `SPRINT_24/SPRINT_LOG.md` Day 13 model_infeasible table
  - Pattern E→A-adjacent classification: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 2 row for #1147
- **Decision:** Revised assumption — **"~1 of 3 alias-related infeasibles will recover; meeting the −3 target will likely require secondary recoveries from Priority 2 emitter/stationarity fixes or Priority 1's Pattern A changing Jacobian numerics for models outside the 11-issue list."** Task 6's rollout design should include a mid-sprint checkpoint to re-run the infeasible trio and call the target.

---

## Unknown 1.8: Can the alias-AD fix be feature-flagged for incremental rollout?

### Priority

**Medium** — Feature-flagged rollout reduces blast radius; all-or-nothing rollout is higher risk but simpler.

### Assumption

The alias-AD fix cannot be feature-flagged — the changes are pervasive enough in the AD code path that toggling behavior per-model is impractical. Rollout must be all-or-nothing with the dispatch canary + golden-file regression as the safety net. (Revises Sprint 24 KU-06's VERIFIED answer given the carryforward context.)

### Research Questions

1. Did Sprint 24 land any portion of the alias-AD fix that's already permanently enabled? If so, we're already past "all or nothing."
2. Is there a sensible runtime flag (e.g., an env var or CLI option) that would let the fix be tested on subset of models before global enablement?
3. Does Python's module-level caching (`@lru_cache` on parser/grammar load) interact poorly with partial rollout?
4. What's the rollback procedure if Checkpoint 1 (Day 5) or Checkpoint 2 (Day 10) returns NO-GO?

### How to Verify

**Verification activity:** Prep Task 6 (rollout design addresses this directly).

- Document the current (Sprint 24) state of alias-AD changes in `src/ad/`.
- Decide: feature flag, incremental-by-Pattern, or all-or-nothing.
- Document the rollback procedure.

### Risk if Wrong

- No rollback plan: if Checkpoint 1 NO-GO, sprint loses Days 1–5 with no way to revert partially.
- Feature-flagged but forgotten: the flag stays off after sprint close, and the fix is "landed" but not active.

### Estimated Research Time

1 hour, part of Task 6's budget.

### Owner

Prep Task 6.

### Verification Results

✅ **Status:** VERIFIED (partial — inventory captured; rollback decision deferred to Task 6)

- **Verified by:** Task 2 (Alias-AD Carryforward Audit)
- **Date:** 2026-04-19
- **Findings:**
  - **Sprint 24 did land portions of the alias-AD fix that are already permanently enabled.** The `bound_indices` threading (Sprint 23), the Day 3 single-index sum collapse fix, the Day 4 `_apply_alias_offset_to_deriv` post-processing, and the Day 5 `_var_inside_alias_sum` narrowed guard are all live. This means "all or nothing" is inaccurate — we're partway through, and the canary-protected additions have been running since Sprint 24.
  - Feature-flag feasibility: the Sprint 25 additions (multi-index partial-collapse recovery, `IndexOffset.base` in `_alias_match`) could in principle be gated on a CLI flag or env var, but doing so would double the test matrix (with-flag / without-flag paths) and give zero operational benefit — there's no "some users want the old behavior" case. `bound_indices` guard already prevents regressions in the alias-free models. Recommend **no feature flag**.
  - **Rollback procedure:** git revert of the Sprint 25 PRs. Because the fixes are surgical (3 functions across 2 files), revert is clean. The Sprint 23 + Sprint 24 base layer remains intact. No database migration or state changes to worry about.
  - Task 6 should document the per-checkpoint rollback step (Checkpoint 1 Day 5, Checkpoint 2 Day 10) with exact `git revert` commands.
- **Evidence:**
  - Landed inventory: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1 (confirms what's already live)
  - Stubbed-vs-landed distinction: `AUDIT_ALIAS_AD_CARRYFORWARD.md` §Section 1 (third subsection)
- **Decision:** Revised assumption — **"no feature flag needed; rollback via git revert of the Sprint 25 PRs is the operational mechanism. Sprint 24 residue stays in place (it already passes all canary tests)."** Task 6 will codify the per-checkpoint revert procedure.

---

# Category 2: Emitter / Stationarity Bug Backlog

Sprint 25's Priority 2 workstream — 8 issues (#1275–#1281, #1283) surfaced during the Sprint 24 Day 13 review round. The leverage point for the 5 `ganges`-family recovered translates that don't currently solve.

## Unknown 2.1: What is the root cause of #1283 parser non-determinism?

### Priority

**Critical** — #1283 may have been quietly corrupting `chenery_mcp.gms` throughout Sprint 24, confounding the #1177 investigation. Until root-caused, every chenery-touching metric is suspect.

### Assumption

The non-determinism is caused by a `set`-based intermediate data structure in table-row-header expansion that relies on dict iteration order. The trigger is multi-value labels `(low,medium,high).ynot` interacting with hyphenated column headers (`light-ind`). Fix: replace `set` with `list` to force deterministic ordering.

### Research Questions

1. Under controlled `PYTHONHASHSEED` variation (0, 1, 42, 12345, …), what fraction of chenery runs produce corrupted output?
2. Is the bug in `src/ir/parser.py` table-row handling, `src/gams/gams_grammar.lark` rule definition, or in Lark's ambiguity resolution?
3. What's the minimum reproducer? (Smallest table with fewest columns that still triggers the bug.)
4. Does the bug produce exactly 2 variant outputs (one correct, one corrupt) or more?
5. Are there other GAMSLib models with `(v1,v2,v3).col` multi-row expansion that are silently affected?

### How to Verify

**Verification activity:** Prep Task 3 (investigate parser non-determinism).

- Run `src.cli chenery.gms` 20× with `PYTHONHASHSEED=0..19` and count correct vs corrupted runs.
- Find the minimum reproducer by progressively simplifying the table.
- Instrument parser code paths with targeted `logger.debug`.
- Identify the specific iteration order that produces corruption.

### Risk if Wrong

- **Root cause is deeper than iteration order:** regex backtracking or Lark ambiguity — significantly more work.
- **Other models affected:** every Sprint 24 and Sprint 25 metric on those models is unreliable.

### Estimated Research Time

2–3 hours (Task 3's full budget).

### Owner

Prep Task 3.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.2: How many corpus models besides chenery are affected by #1283?

### Priority

**High** — Scope of the non-determinism fix depends on whether it affects 1 model (chenery only) or N.

### Assumption

At most 3 corpus models use the `(v1,v2,v3).col` multi-row-label table pattern and are potentially affected. These are likely in the CGE family (twocge, korcge, stdcge) or economic-data-table family.

### Research Questions

1. Which GAMSLib models contain multi-row-label tables (`(a,b,c).col` syntax)?
2. Of those, which have corruption symptoms under `PYTHONHASHSEED` variation (not just textual differences — actual value corruption)?
3. Has any corpus model been quietly producing wrong metrics because of this?
4. Does the fix need to be validated on all affected models, or is chenery a sufficient canary?

### How to Verify

**Verification activity:** Prep Task 3 (non-determinism scope survey).

- `grep -E "^\s*\([a-z_]+(,\s*[a-z_]+)+\)\." data/gamslib/raw/*.gms` — find candidate models.
- Run each candidate 5× under different seeds; check for byte-differing output.
- Build list of affected models to include in the PR12 byte-stability test fixture.

### Risk if Wrong

- Under-estimate affected model count: #1283 fix verified only on chenery, regressions on silently-affected models.
- Over-estimate: PR12 test infrastructure bloated with models that aren't actually affected.

### Estimated Research Time

1 hour, part of Task 3's budget.

### Owner

Prep Task 3.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.3: Do the 3 presolve-path #1275 cases (robustlp, chain, mathopt3) require identical fixes?

### Priority

**High** — One fix for all three is 1–2h; per-model fixes are 3× that.

### Assumption

All 3 models (robustlp, chain, mathopt3) emit absolute `$include` paths via the same code path in `src/emit/original_symbols.py` (the `--nlp-presolve` wrapper emitter). A single fix repo-relativizing the path covers all 3.

### Research Questions

1. Is the emitter site single (good) or multiple (worse)?
2. Does the fix need to handle models whose source file is OUTSIDE the repo root (edge case)?
3. Does the fix need a fallback for environments where the working directory isn't the repo root?
4. Are there models where the original path is already correctly relative, and the fix shouldn't touch them?

### How to Verify

**Verification activity:** Prep Task 4 (emitter backlog categorization).

- Locate the emission site by grep.
- Verify all 3 models hit the same code path.
- Design a repo-relative path resolution strategy with fallback.

### Risk if Wrong

- Per-model fixes needed: +2–4h Sprint 25 effort.
- Edge case breaks: models with OS-specific paths produce new non-portable output.

### Estimated Research Time

1 hour, part of Task 4's budget.

### Owner

Prep Task 4.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.4: Are #1277 and #1278 subsumed by Priority 1 alias-AD work?

### Priority

**High** — Determines whether these two twocge bugs need dedicated effort or are incidentally fixed.

### Assumption

#1277 (twocge `stat_tz` mixed offsets) is subsumed by Pattern C fix (alias-AD Priority 1). #1278 (twocge `ord(r) <> ord(r)` tautology) is an AD substitution bug that is NOT subsumed by alias-AD — it's a separate substitution-preservation issue.

### Research Questions

1. Does the Pattern C extension (summation-context + IndexOffset) automatically fix #1277's mixed-offset pattern?
2. Is #1278's `ord(r) <> ord(r)` tautology traceable to the same `_replace_indices_in_expr` code path as alias-AD, or a different substitution pass?
3. After Pattern C fix lands, does twocge translate produce a non-tautological `ord(rr) <> ord(r)` condition?
4. Does twocge pass #1251 (empty trade equations) as a distinct bug even after #1277 / #1278 are fixed?

### How to Verify

**Verification activity:** Prep Task 4 (categorization); Task 6 (rollout design flags which post-Pattern-C verification tests to run).

- Trace #1277 and #1278 reproducers under current parser state.
- Identify the code paths involved in each.
- Decide: subsumed / partially subsumed / separate.

### Risk if Wrong

- #1278 re-surfaces after Priority 1 landing: need mid-sprint separate fix.
- #1277 NOT subsumed: adds 2–3h to Priority 2.

### Estimated Research Time

1.5 hours, part of Task 4's budget.

### Owner

Prep Task 4.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.5: Will #1281 (lmp2 duplicate Parameter) fix accidentally remove legitimate declarations from other models?

### Priority

**High** — A wrong dedup could silently break models that were relying on the redeclaration.

### Assumption

The duplicate `Parameter` declarations in `lmp2_mcp.gms` are purely from the emitter regenerating declarations already present in the inlined original source. No other in-scope model has this pattern because most models don't inline the original; they use `$include` indirection.

### Research Questions

1. Which models have `src.cli` emit an inlined original source (vs a `$include`)?
2. Of those, do any have a `Parameter`/`Set`/`Variable` that's re-declared for a legitimate reason (e.g., conditional-compile override)?
3. Does the fix's dedup logic correctly handle mixed-case names (`A` vs `a`)?
4. Are there `Parameter` declarations that appear multiple times with DIFFERENT domain signatures (legal override) that the fix shouldn't remove?

### How to Verify

**Verification activity:** Prep Task 4 (categorization surveys emitter patterns).

- Identify all in-scope models whose MCP uses inlined source.
- For each, check for duplicate `Parameter` / `Set` / `Variable` declarations.
- Design a dedup that flags ambiguous cases instead of silently deleting.

### Risk if Wrong

- Silent regression on 1+ models: they compile but produce subtly-wrong values.
- Fix lands but `lmp2` still doesn't solve due to a second blocker.

### Estimated Research Time

1 hour, part of Task 4's budget.

### Owner

Prep Task 4.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 2.6: Which `ganges`-family models are unblocked by each emitter fix?

### Priority

**Critical** — The 5 models (ganges, gangesx, ferts, clearlak, turkpow) are Sprint 25's most accessible Solve/Match leverage. If emitter fixes unblock 0 of them, Priority 2 adds correctness-only value; if they unblock 3+, Priority 2 is the Solve lead.

### Assumption

At least 3 of the 5 `ganges`-family models are unblocked by some subset of emitter fixes (#1275–#1281). Specifically: #1281 (duplicate Parameter) probably unblocks at least 1; #1275 (absolute paths) unblocks none directly (they don't use presolve); #1277/#1278 alias-AD fixes unblock ganges/gangesx indirectly.

### Research Questions

1. For each of the 5 models, what's the specific GAMS compile error they currently hit?
2. Map each error to one of the 8 tracked emitter bugs (#1275–#1281, #1283) or identify it as a new untracked bug.
3. Do any of the 5 models need fixes to problems NOT yet tracked? (New Sprint 25 issue needed?)
4. Which single emitter fix unblocks the most of the 5?
5. Is there a "fix-minimal" subset that unblocks 3 of the 5?

### How to Verify

**Verification activity:** Prep Task 5 (recovered-translate leverage analysis).

- For each model: run `gams <model>_mcp.gms action=c` to compile-check; record errors.
- Build a leverage matrix: rows = 5 models, columns = 8 emitter fixes.
- Rank fixes by model-unblocking leverage.

### Risk if Wrong

- 0 of the 5 are unblocked by Priority 2: Solve target (≥ 105) depends entirely on Priority 1.
- New bugs discovered: Priority 2 scope expands, other priorities compressed.

### Estimated Research Time

2 hours (Task 5's full budget).

### Owner

Prep Task 5.

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 3: Multi-Solve Gate Extension

Priority 3 workstream — Issue #1270 extends the pre-translation multi-solve driver gate to catch `saras`-style top-level `eq.m` reads. Carries forward Sprint 24 KU-29.

## Unknown 3.1: Does Approach A (cross-reference) produce false positives on corpus post-solve reporting?

### Priority

**Critical** — A false-positive breaks currently-translating models. The whole point of the narrow Sprint 24 gate was to avoid this failure mode.

### Assumption

Approach A (flag `eq.m` reads whose receiving parameter later appears in another declared model's constraint body) produces zero false positives on the current 143-model in-scope corpus. Post-solve reporting patterns (e.g., writing `eq.m` into a display-only parameter) don't satisfy the "later appears in another model's constraints" condition.

### Research Questions

1. Which in-scope corpus models have `eq.m` reads at top level (candidates for Approach A detection)?
2. For each candidate, does the receiving parameter appear in another declared model's constraint body?
3. Does `partssupply` (which was a critical false-positive canary in Sprint 24) pass Approach A?
4. Does `ibm1` (single-model multi-solve) continue to pass?
5. Are there edge cases like "parameter used in a reported expression but not in a constraint" that Approach A might mistakenly flag?

### How to Verify

**Verification activity:** Prep Task 7 (multi-solve gate scoping).

- Corpus survey: grep for `\.m` on scalar / indexed equation references at top level.
- For each candidate, trace the receiving parameter's downstream use.
- Build a test matrix: must-flag (saras), must-not-flag (partssupply, post-solve reporting fixtures, multi-stage display fixtures).

### Risk if Wrong

- Breaks partssupply or ibm1: direct regression of a Sprint 24 gain.
- Silent miss of saras: the workstream fails its goal.

### Estimated Research Time

1–1.5 hours, part of Task 7's 2–3h budget.

### Owner

Prep Task 7.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 3.2: Which corpus models besides `saras` should the extended gate catch?

### Priority

**High** — Scope of the fix; if only saras, it's a 1-model targeted change; if 5+ models, the gate's logic needs to generalize well.

### Assumption

Saras is the only in-scope corpus model that exhibits the top-level `eq.m` read pattern. Extended gate catches exactly 1 additional model.

### Research Questions

1. Beyond saras, are there other calibration / multi-stage models in the corpus with top-level `eq.m` reads?
2. Are any `multi_solve: true` models in `gamslib_status.json` (non-driver multi-solve) also candidates?
3. Does the extended gate need to handle models with `.l` (variable level) top-level reads too, or is `.m` scope sufficient?

### How to Verify

**Verification activity:** Prep Task 7 (corpus survey).

- Corpus grep as in 3.1.
- Cross-reference with `data/gamslib/gamslib_status.json` for `multi_solve: true` flags.

### Risk if Wrong

- Silent miss of another multi-solve driver: downstream metrics corrupted.
- Scope creep: gate extension drags on beyond the 2–3h budget.

### Estimated Research Time

1 hour, part of Task 7's budget.

### Owner

Prep Task 7.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 3.3: Does the extended gate interact with partssupply's `var.l` post-solve reporting?

### Priority

**Medium** — partssupply is a specific regression canary for the multi-solve gate.

### Assumption

Partssupply reads `util.l` / `x.l` (variable levels) in a post-solve reporting pattern. Since Approach A only flags `eq.m` (equation marginals) reads, partssupply is not affected by the extended gate.

### Research Questions

1. Does partssupply's current MCP output show any `eq.m` reads at top level?
2. If Approach A is extended to also flag `.l` reads (belt-and-suspenders), does partssupply get flagged?
3. Should the gate explicitly scope to equation marginals, or treat variable levels as weak driver signals?

### How to Verify

**Verification activity:** Prep Task 7 (test matrix must include partssupply).

- Trace partssupply under the extended gate.
- Ensure the regression guard test in `tests/unit/validation/test_driver.py::test_scan_partssupply_style_variable_level_is_not_driver` still passes.

### Risk if Wrong

- Direct partssupply regression after Sprint 24 investment to fix it.

### Estimated Research Time

0.5 hours, part of Task 7's budget.

### Owner

Prep Task 7.

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 4: Dispatcher Refactor

Priority 4 workstream — Issue #1271 collapses `_loop_tree_to_gams` and `_loop_tree_to_gams_subst_dispatch`. Carries forward Sprint 24 KU-30.

## Unknown 4.1: Is the substituting dispatcher genuinely equivalent to the canonical after refactor?

### Priority

**Medium** — Equivalence is the whole point of the refactor; drift = silent correctness bug.

### Assumption

The substituting dispatcher's behavior is identical to the canonical dispatcher's when called with an empty `token_subst_map`. All observed differences in Sprint 24 (partssupply's `dollar_cond` handlers, decomp's `bound_scalar` handlers) are bugs in the substituting dispatcher — fixing these before the refactor makes the two dispatchers byte-equivalent.

### Research Questions

1. Are there grammar rules where the two dispatchers SHOULD legitimately differ (e.g., rules that only apply inside a substituting context)?
2. Does the refactor preserve every existing grammar-rule handler, or might the unification simplification accidentally drop edge cases?
3. What's the byte-diff baseline BEFORE the refactor (is it truly zero, or are there pre-existing differences to be aware of)?

### How to Verify

**Verification activity:** Prep Task 7 (dispatcher refactor design).

- Compare dispatchers line-by-line; catalogue all rule handlers in each.
- Identify genuine vs accidental divergences.
- Design a byte-diff regression test across all currently-solving models.

### Risk if Wrong

- Post-refactor byte-diff reveals legitimate divergence: refactor has to preserve the conditional behavior (adds complexity).
- Silent correctness bug: one model loses a Sprint 24 gain.

### Estimated Research Time

1 hour, part of Task 7's budget.

### Owner

Prep Task 7.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 4.2: How many committed MCP outputs will byte-diff after the refactor?

### Priority

**Medium** — Target is zero. Any diff needs investigation.

### Assumption

After the refactor, translating every currently-solving model (99 models) produces byte-identical output to pre-refactor. Zero byte-diffs.

### Research Questions

1. Does the refactor change the order of emitted expressions (even if semantically equivalent)?
2. Does any whitespace / formatting behavior change?
3. Are there any generator-based emission patterns that have different iteration behavior under refactoring?

### How to Verify

**Verification activity:** Prep Task 7 (byte-diff regression strategy design).

- Before refactor: snapshot all 99 currently-solving MCP outputs into a temp dir.
- After refactor: regenerate and diff.
- Investigate any non-zero diff.

### Risk if Wrong

- Non-zero diffs appear: refactor PR needs to absorb fixes for any differences, extending scope.

### Estimated Research Time

0.5 hours, part of Task 7's budget (investigation only; actual byte-diff happens during implementation).

### Owner

Prep Task 7.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 4.3: Does the unified dispatcher add measurable translate-time overhead?

### Priority

**Low** — Performance regression is unlikely given the refactor is a unification, not an algorithmic change.

### Assumption

The unified dispatcher has ≤ 5% translate-time overhead relative to the pre-refactor baseline. The added branch (`if token_subst is not None`) is cheap enough to be noise-level.

### Research Questions

1. Is the hot path in translate actually the dispatcher, or something else (AD, parsing)?
2. Does Python's branch-prediction handle the new branch well?
3. Are there loop-body translates that hit this dispatcher 1000+ times per model?

### How to Verify

- Translate-time benchmark before / after the refactor on 5 representative models.
- Check `mean` and `p90` translate-time changes.

### Risk if Wrong

- Measurable slow-down on CI: test budget needs adjustment.

### Estimated Research Time

0.5 hours (deferred to implementation phase).

### Owner

Prep Task 7 (notes only; validation during implementation).

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 5: Translation Timeout — Algorithmic

Priority 5 (low-priority) workstream — Issues #1169, #1185, #1192. 5 models still time out at 600s: `iswnm`, `mexls`, `nebrazil`, `sarf`, `srpchase`. Per Sprint 24 retrospective finding PR13, translate-recovery alone is low-leverage for Match.

## Unknown 5.1: Is any of the 5 hard-timeout models tractable with targeted optimization?

### Priority

**High** — Determines whether Priority 5 is budgeted at 4–6h (one fix) or 0h (defer wholesale to Sprint 26).

### Assumption

At least 1 of the 5 models (likely `srpchase` given its small size: 107 lines, 3 equations) is tractable with a specific optimization — e.g., caching, loop-unrolling avoidance, or algorithmic replacement. The other 4 remain intractable at the current architecture.

### Research Questions

1. Under a 900s or 1200s budget, would any of the 5 complete? (Tests intractability vs budget.)
2. Which translate stage dominates each model's time (parse / IR build / normalize / AD / KKT assembly / emit)?
3. Is `srpchase`'s bottleneck the ScenRed stochastic library expansion (per Sprint 24 KU-19 note)?
4. Is `iswnm`'s bottleneck the empty-set `nb` interacting with instance enumeration (per Sprint 24 ISSUE_1228)?

### How to Verify

**Verification activity:** Prep Task 8 (profile hard timeouts).

- Instrument stage-timing for each of the 5 models.
- Run each under a 900s budget with profiling.
- Classify each as tractable / intractable / unclear.

### Risk if Wrong

- Estimate Priority 5 as tractable, spend 4–6h, produce 0 results.
- Estimate Priority 5 as intractable, miss a 1-model fix that was 30% over budget.

### Estimated Research Time

2 hours (Task 8's main budget).

### Owner

Prep Task 8.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 5.2: Where exactly does the 600s budget interrupt each model?

### Priority

**High** — Stage-level attribution is a prerequisite for any targeted optimization.

### Assumption

Each of the 5 hard-timeout models has a single dominant stage. `iswnm` / `nebrazil` / `mexls`: KKT assembly / instance enumeration. `sarf` / `srpchase`: AD or IR build (stochastic library expansion).

### Research Questions

1. What's the stage timing breakdown (parse / IR / normalize / AD / emit) for each model at the 600s mark?
2. Is any stage growing super-linearly in model size?
3. Are there per-stage caches that could help (e.g., memoize derivative computations)?

### How to Verify

**Verification activity:** Prep Task 8.

- Add stage-timing instrumentation to `scripts/gamslib/run_full_test.py` or `src/cli.py` --verbose.
- Run each of 5 under a 1200s budget (allow some to complete).
- Record per-stage timing.

### Risk if Wrong

- Misidentify bottleneck, propose wrong optimization.

### Estimated Research Time

1 hour, part of Task 8's budget.

### Owner

Prep Task 8.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 5.3: Would sparse Jacobian techniques help any of the 5 models?

### Priority

**Medium** — Sparse Jacobian was Sprint 24's KU-20 (INCOMPLETE). Still untested.

### Assumption

Sparse Jacobian techniques would help at most 1 of the 5 (likely `mexls` or `nebrazil`, which have large set cardinalities). The bottleneck for most is pattern-specific (ScenRed, SetMembershipTest, etc.) and not Jacobian density.

### Research Questions

1. What fraction of Jacobian entries are structurally zero for each of the 5 models? (Sparse Jacobian help requires high sparsity.)
2. Can sparsity be determined statically from the equation structure?
3. What's the implementation effort for sparse Jacobian in the stationarity builder?
4. Does sparse Jacobian interact with the LP fast path (Sprint 23)?

### How to Verify

**Verification activity:** Prep Task 8 (profile + sparsity estimate).

- For each model, estimate Jacobian non-zero density.
- Estimate speedup potential from skipping zero entries.

### Risk if Wrong

- Invest in sparse Jacobian infrastructure, doesn't help.
- Miss a quick sparse-Jacobian win.

### Estimated Research Time

1 hour, part of Task 8's budget.

### Owner

Prep Task 8.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 5.4: Is `srpchase` (small model, large timeout) a fundamentally different bottleneck?

### Priority

**Medium** — `srpchase` is the only tiny model (107 lines, 3 equations) that times out; suggests a pattern-specific issue, not scale.

### Assumption

`srpchase`'s bottleneck is the ScenRed stochastic library's macro expansion during parsing — a preprocessor-level issue, not an AD / KKT issue. Fix requires either macro evaluation or scope exclusion.

### Research Questions

1. Does `srpchase` even reach the IR / AD stages, or does it time out during parse?
2. Is the ScenRed library usage the dominant factor?
3. Should `srpchase` be considered for scope exclusion (similar to MINLP / multi-solve-driver exclusions)?
4. Are other models using ScenRed in the corpus affected similarly?

### How to Verify

**Verification activity:** Prep Task 8.

- Profile `srpchase` at the parse / preprocessor level.
- Identify ScenRed library patterns.

### Risk if Wrong

- Treat `srpchase` as algorithmic, miss that it's a preprocessor issue.
- Exclude `srpchase` unnecessarily.

### Estimated Research Time

0.5 hours, part of Task 8's budget.

### Owner

Prep Task 8.

### Verification Results

🔍 **Status:** INCOMPLETE

---

# Category 6: Pipeline Retest + Determinism

Cross-cutting infrastructure — PR6 (full pipeline baseline), PR12 (byte-stability tests), PR15 (scope freeze). Sprint 24 carryforward process recommendations.

## Unknown 6.1: Will the 143-model scope hold, or will new exclusions emerge mid-sprint?

### Priority

**Critical** — Mid-sprint scope change invalidates acceptance-criteria evaluation. PR15 is the Sprint 24 retrospective's direct response.

### Assumption

The 143-model scope (v2.2.1 exclusions: 14 MINLP, 7 legacy, 2 multi-solve driver) is stable throughout Sprint 25. Any new `multi_solve_driver_out_of_scope` exclusion introduced by the #1270 gate extension (saras-style) is handled transparently by the validator gate without requiring scope re-freeze.

### Research Questions

1. How many models does the extended #1270 gate catch as new `multi_solve_driver_out_of_scope` exclusions?
2. Does catching saras (or other new models) constitute a scope change that invalidates Sprint 25 acceptance criteria?
3. What's the policy for mid-sprint scope changes — freeze strictly, or allow gate-driven additions?

### How to Verify

**Verification activity:** Prep Task 9 (baseline + scope freeze).

- Snapshot v2.2.1 exclusion list in `SPRINT_25/BASELINE_METRICS.md`.
- Document policy for mid-sprint gate additions.

### Risk if Wrong

- Mid-sprint scope churn repeats the Sprint 24 ambiguity problem.
- Strict-freeze interpretation blocks legitimate gate extensions.

### Estimated Research Time

0.5 hours, part of Task 9's budget.

### Owner

Prep Task 9.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: What `PYTHONHASHSEED` sample size is sufficient for PR12 determinism tests?

### Priority

**Low** — Test-design question with easy conservative fallback (use 10 seeds).

### Assumption

5 fixed seeds (0, 1, 42, 12345, 99999) plus the CI default provide ≥ 95% confidence in catching `#1283`-class non-determinism. Running 10 seeds gives near-complete coverage at acceptable CI cost.

### Research Questions

1. What fraction of seeds produced `#1283` corruption on chenery during the Sprint 24 Day 13 Addendum investigation (`~33%`)?
2. With a 33% corruption rate, how many seeds are needed to hit confidence 0.95 that at least one seed catches it? (Answer: ~7 seeds.)
3. Is there a CI wall-clock budget for the per-commit byte-stability test?
4. Should the test rotate through a large seed pool (100+) and sample 5 each run, or fix the 5 for reproducibility?

### How to Verify

**Verification activity:** Prep Task 10 (determinism test design).

- Statistical analysis: given observed corruption rate, what sample size?
- CI budget check.

### Risk if Wrong

- Sample too small: `#1283`-class bugs slip through.
- Sample too large: CI budget exceeded.

### Estimated Research Time

0.5 hours, part of Task 10's budget.

### Owner

Prep Task 10.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Does the 80–100% translate-recovery influx assumption apply to alias-AD recoveries too?

### Priority

**Medium** — Drives Sprint 25 Match-target calibration. PR13 was formulated for translation-timeout recoveries; alias-AD recoveries may have different dynamics.

### Assumption

Translation-timeout recoveries (Sprint 24 Day 13 Addendum: 100% influx) are NOT representative of alias-AD recoveries. Alias-AD recoveries are more likely to produce `model_optimal` + `match` because the underlying MCP structure is correct — the bug was in the derivative values, not the model structure. Expected influx for alias-AD recoveries: 30–50% (in line with original PR10 estimate).

### Research Questions

1. When Sprint 24 Day 3's single-index-sum-collapse fix landed, what was the per-model outcome distribution? (Any models that went from mismatch → path_syntax_error?)
2. When Sprint 23's alias-aware differentiation landed, were there new error-category influx?
3. Is the "previously-timeout-excluded" cohort (Day 13 Addendum) uniquely bad because timeouts filter for pathological patterns?

### How to Verify

**Verification activity:** Prep Task 11 (schedule integration + budget calibration).

- Review Sprint 23 retrospective on translate-recovery influx rates.
- Review Sprint 24 Day 3 single-index-sum-collapse impact report.
- Calibrate Sprint 25 Match target's tolerance.

### Risk if Wrong

- Match target over-estimates alias-AD's Match contribution.
- Under-estimate: planning is overly conservative, morale hit from "apparent" under-performance.

### Estimated Research Time

1 hour, part of Task 11's budget.

### Owner

Prep Task 11.

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Template for Adding New Unknowns During Sprint

```markdown
## Unknown X.Y: [Short question or title]

### Priority

**[Critical/High/Medium/Low]** — [brief context]

### Assumption

[what we're assuming]

### Research Questions

1. [Question 1]
2. [Question 2]
3. [Question 3]

### How to Verify

[Method: test cases, experiments, code-read, survey, etc.]

### Risk if Wrong

[Impact on sprint]

### Estimated Research Time

[Hours]

### Owner

[Prep task, sprint day, or individual]

### Verification Results

🔍 **Status:** INCOMPLETE
```

---

## Newly Discovered Unknowns

_Add unknowns discovered during Sprint 25 execution here, then categorize post-sprint._

---

## Next Steps

1. **Prep Task 2 (Audit Alias-AD Carryforward)** — verifies Unknowns 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8
2. **Prep Task 3 (Investigate Parser Non-Determinism #1283)** — verifies Unknowns 2.1, 2.2
3. **Prep Task 4 (Categorize Emitter Bug Backlog)** — verifies Unknowns 2.3, 2.4, 2.5
4. **Prep Task 5 (Analyze Recovered-Translate Models)** — verifies Unknown 2.6
5. **Prep Task 6 (Design Alias-AD Rollout Plan)** — verifies Unknowns 1.5, 1.8 (and integrates 1.1–1.4, 1.6, 1.7)
6. **Prep Task 7 (Scope Multi-Solve Gate + Dispatcher Refactor)** — verifies Unknowns 3.1, 3.2, 3.3, 4.1, 4.2, 4.3
7. **Prep Task 8 (Profile Hard Translation Timeouts)** — verifies Unknowns 5.1, 5.2, 5.3, 5.4
8. **Prep Task 9 (Full Pipeline Baseline + Freeze Scope)** — verifies Unknown 6.1
9. **Prep Task 10 (Design Byte-Stability Test Infrastructure)** — verifies Unknown 6.2
10. **Prep Task 11 (Plan Sprint 25 Detailed Schedule)** — integrates all verified unknowns + verifies Unknown 6.3

During Sprint 25 execution:
- Daily standup review of 🔍 INCOMPLETE unknowns
- Update status as findings emerge
- Add Newly Discovered Unknowns when surfaced
- Cross-reference with Sprint 25 retrospective

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 25 prep tasks verify which unknowns. Prep Task 11 (Plan Sprint 25 Detailed Schedule) integrates all verified unknowns and explicitly calibrates Unknown 6.3 (alias-AD influx assumption).

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Audit Alias-AD Carryforward State | 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8 | Core alias-AD classification + regression risk analysis |
| Task 3: Investigate Parser Non-Determinism (#1283) | 2.1, 2.2 | Root-cause #1283 and survey affected models |
| Task 4: Categorize Emitter Bug Backlog (#1275–#1281) | 2.3, 2.4, 2.5 | Emitter-fix classification, subsume-opportunity analysis |
| Task 5: Analyze Recovered-Translate Models (ganges family) | 2.6 | Per-model compile-error mapping; leverage matrix |
| Task 6: Design Alias-AD Rollout Plan | 1.5, 1.8 | Sameas-guard validation, rollout-flag decision (integrates Task 2 findings on 1.1–1.4, 1.6, 1.7) |
| Task 7: Scope Multi-Solve Gate + Dispatcher Refactor | 3.1, 3.2, 3.3, 4.1, 4.2, 4.3 | Covers all of Categories 3 and 4 |
| Task 8: Profile Hard Translation Timeouts | 5.1, 5.2, 5.3, 5.4 | Covers all of Category 5 |
| Task 9: Full Pipeline Baseline + Freeze Scope (PR6 / PR15) | 6.1 | Scope-freeze policy documentation |
| Task 10: Design Byte-Stability Test Infrastructure (PR12) | 6.2 | Seed-set sample-size analysis |
| Task 11: Plan Sprint 25 Detailed Schedule | 6.3 (+ integrates all others) | Influx budget calibration + sprint schedule |

**Coverage:** All 27 unknowns are assigned to at least one prep task. Most Critical and High-priority unknowns are assigned to the same task that will act on the findings (e.g., Task 2 audits alias-AD AND its findings drive Task 6's rollout design).

**Deferred from Sprint 24** (now carried as Sprint 25 KUs):

- KU-29 (saras-style multi-solve) → Unknowns 3.1, 3.2
- KU-30 (dispatcher duplication) → Unknowns 4.1, 4.2
- KU-32 (sameas guard validation) → Unknown 1.5
- KU-13 / KU-17 (alias-AD regression risk) → subsumed by Unknown 1.2

---

**Document Created:** 2026-04-19
**Total Unknowns:** 27
**Sprint 24 Carryforward:** 4 KUs (KU-29 → 3.1/3.2, KU-30 → 4.1/4.2, KU-32 → 1.5, KU-13/17 → 1.2)
