# Sprint 26 Known Unknowns

**Created:** 2026-05-07
**Status:** Active — Pre-Sprint 26
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 26 — Pattern C Generalization, Pattern A Reclassification, Phase E re-verification, Translation Timeout Option 1 Short-Circuit, AD Residuals (#1334/#1335), and the Sprint 25 retrospective process recommendations PR16–PR19 + PR14 reaffirmation.

---

## Overview

This document identifies all assumptions and unknowns for Sprint 26 features **before** implementation begins. Sprint 26 is the third consecutive sprint to target alias-aware differentiation correctness as Priority 1 (after S24's launch attempt and S25's narrow-gate Pattern C fix); the central new prep activity is **Pattern C hypothesis validation pre-Day-0** (Task 3 of `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md`, codifying Sprint 25 retrospective PR16). Sprint 26 also inherits 23 issues labeled `sprint-26` (4 net-new from Sprint 25 Day 13 — #1354 camcge, #1355 cesam2, #1356 fawley, #1357 otpop — plus 19 carryforward).

**Sprint 26 Scope** (per `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 26 entry, Weeks 17–18, 14-day sprint at ≤ 12h/day):

1. **Priority 1: Pattern C Gate Generalization** (#1354/#1355/#1356/#1357 + #1306/#1307) — widen launch-shape gate to plain-alias enumeration + sameas-decomposed SAM blocks
2. **Priority 2: Pattern A Cohort Reclassification** (#1138/#1139/#1140/#1142/#1145/#1150) — per Day 7 sweep
3. **Priority 3: Pattern E Carryforward Re-Verification** (#1141/#1144/#1147) — Phase E was cancelled in Sprint 25
4. **Priority 4: Translation Timeout — Option 1 Short-Circuit** (#885/#931/#932/#1185/#1228 + defers #1224)
5. **Priority 5: AD Residuals from Sprint 25 Day 11 Fix-In-Place Series** (#1334, #1335)
6. **Process Recommendations:** PR16 (pre-Sprint-0 hypothesis validation), PR17 (bucket provenance baseline), PR18 (Sprint 25 scope-shift identification), PR19 (pre-merge solve-time validation CI), PR14 reaffirmation (read-the-generated-MCP rule)

**Reference:** See `docs/planning/EPIC_4/PROJECT_PLAN.md` Sprint 26 entry (Goal, Components, Deliverables, Acceptance Criteria, Estimated Effort 50–75h, Risk Level MEDIUM).

**Lessons from Previous Sprints:**

- Sprint 22: 28 unknowns; early preprocessing research saved 20+ hours.
- Sprint 23: 32 unknowns; KU-27 (subset-superset domain) led to a high-impact fix.
- Sprint 24: 26 prep + 6 end-of-sprint KUs (KU-27..KU-32); KU-27 (Lark disambiguation) unblocked CI and surfaced the `requirements.txt` pinning lesson (KU-28).
- Sprint 25: 27 prep + 4 end-of-sprint KUs (KU-33..KU-36); KU-33 directly drives this sprint's Priority 1; KU-34 drives PR17.

**Sprint 25 Key Learning** (from `docs/planning/EPIC_4/SPRINT_25/SPRINT_RETROSPECTIVE.md` §"Day 5 Pivot Retrospective"): Sprint 25 spent Days 1–4 on Phase 1 alias-AD work that produced no Match gain because the underlying Pattern A hypothesis was wrong about the cohort. The Day 5 pivot disproved the hypothesis in 1 day via trace + emitted-artifact + formal-derivative methodology. **Sprint 26's PR16 is the codified version of that methodology applied PRE-Day-0** to the Pattern C generalization hypothesis. This is the single highest-value prep activity for Sprint 26.

**Sprint 25 Carryforward KUs** (from `docs/planning/EPIC_4/SPRINT_25/KNOWN_UNKNOWNS.md` §End-of-Sprint Discoveries):

- **KU-33** (Pattern C generalizes beyond launch) → directly drives Priority 1 (this sprint's Category 1)
- **KU-34** (bucket churn dominates path_syntax_error metric) → drives PR17 bucket-provenance baseline (Task 9 of `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md`)
- **KU-35** (multi-solve gate over-approximation invariant) → regression-canary protection during Sprint 26
- **KU-36** (`_loop_tree_to_gams` bare-ID substitution invariant) → regression-canary protection during Sprint 26

---

## How to Use This Document

### Before Sprint 26 Day 1

1. Research and verify all **Critical** and **High** priority unknowns during prep tasks (see §"Appendix: Task-to-Unknown Mapping").
2. Create minimal test cases for validation where needed.
3. Document findings in the "Verification Results" subsection of each unknown.
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED (with evidence) or ❌ WRONG (with correction and new assumption).

### During Sprint 26

1. Review daily during standup — especially unknowns marked 🔍 INCOMPLETE.
2. Add newly-discovered unknowns in the "Newly Discovered" section (migrate into categories post-sprint).
3. Update with implementation findings as work progresses.
4. Flag any assumption that turns out wrong — don't quietly re-scope around it.

### Priority Definitions

- **Critical:** Wrong assumption will break a sprint priority or require major re-planning (>8 hours of rework). For Sprint 26, this includes any unknown whose disconfirmation would force the Pattern C generalization hypothesis (Priority 1) to be replanned during execution.
- **High:** Wrong assumption will cause significant rework (4–8 hours).
- **Medium:** Wrong assumption will cause minor issues (2–4 hours).
- **Low:** Wrong assumption has minimal impact (<2 hours).

---

## Summary Statistics

**Total Unknowns:** 26

**By Priority:**

- Critical: 6 (23%)
- High: 9 (35%)
- Medium: 8 (31%)
- Low: 3 (12%)

**By Category:**

- Category 1 (Pattern C Gate Generalization): 6 unknowns
- Category 2 (Pattern A Cohort Reclassification): 4 unknowns
- Category 3 (Pattern E Carryforward Re-Verification): 3 unknowns
- Category 4 (Translation Timeout — Option 1 Short-Circuit): 4 unknowns
- Category 5 (AD Residuals #1334 / #1335): 4 unknowns
- Category 6 (Cross-Cutting & Process Recommendations): 5 unknowns

**Estimated Research Time:** 28–36 hours (work-item estimates; per-unknown numbers sum higher than the prep-task budget because many unknowns are verified in parallel within a single prep task — see §"Appendix: Task-to-Unknown Mapping" for which task verifies which unknowns. The authoritative scheduling budget is the per-task total in `docs/planning/EPIC_4/SPRINT_26/PREP_PLAN.md`: 28–39h across Tasks 1–11.)

---

## Table of Contents

1. [Category 1: Pattern C Gate Generalization](#category-1-pattern-c-gate-generalization)
2. [Category 2: Pattern A Cohort Reclassification](#category-2-pattern-a-cohort-reclassification)
3. [Category 3: Pattern E Carryforward Re-Verification](#category-3-pattern-e-carryforward-re-verification)
4. [Category 4: Translation Timeout — Option 1 Short-Circuit](#category-4-translation-timeout--option-1-short-circuit)
5. [Category 5: AD Residuals (#1334, #1335)](#category-5-ad-residuals-1334-1335)
6. [Category 6: Cross-Cutting & Process Recommendations](#category-6-cross-cutting--process-recommendations)

---

# Category 1: Pattern C Gate Generalization

Priority 1 workstream — Issues #1354 (camcge), #1355 (cesam2), #1356 (fawley), #1357 (otpop) plus #1306/#1307 (launch). Drives KU-33 from Sprint 25 §End-of-Sprint Discoveries.

## Unknown 1.1: Does removing the `$cond` filter from the Pattern C gate's predicate break selectivity on Tier 0/1 canaries?

### Priority

**Critical** — If removing the `$cond` filter is too permissive, the broader gate fires on Tier 0/1 canary models (dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive) and regresses byte-stable emit. That kills the Priority 1 hypothesis before any of the 4 target models recover.

### Assumption

The Sprint 25 launch-shape Pattern C gate (#1306 narrowing — fires only on alias-only conditional sums with a `$ge(ss, s)`-style filter) generalizes by simply dropping the `$cond` predicate, with no further changes to the gate logic. The remaining predicates (alias-only, IndexOffset present, etc.) are sufficient to keep canary models out of the gate's match set.

### Research Questions

1. How many of the 11 Tier 0/1 canary models contain an "alias-only conditional sum" pattern that the launch gate currently rejects ONLY because of the `$cond` predicate?
2. Does the launch gate's `$ge(ss, s)`-shaped predicate share machinery with the broader `$cond` check, or are they independent?
3. If we replace "must have `$cond`" with "may have `$cond`", what other predicates need strengthening to compensate?
4. Does the gate's "alias-only" predicate (no concrete `IndexOffset`-shaped offsets) need refinement when `$cond` is absent?
5. Are there models in the 142 in-scope set (beyond the 4 Pattern C targets and 11 canaries) that would unexpectedly enter the gate's match set?

### How to Verify

**Test Case 1: Apply prototype patch, run Tier 0/1 canary regression**

The "baseline" is the committed `data/gamslib/mcp/<model>_mcp.gms` artifacts from the current main branch — these are the canonical pipeline outputs and are byte-stable across `PYTHONHASHSEED` per the PR12 determinism harness (per `data/gamslib/mcp/`'s tracked status). Diffing the patched emit against the committed artifact catches any regression introduced by the prototype patch.

```bash
# Apply the 1-line patch from Task 3 (PREP_PLAN.md) that removes the `$cond` filter
# Then byte-diff Tier 0/1 canary outputs against the committed baseline
mkdir -p /tmp/sprint26-canary-regression
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
    -o /tmp/sprint26-canary-regression/${m}_mcp.gms --skip-convexity-check --quiet
  diff -q data/gamslib/mcp/${m}_mcp.gms /tmp/sprint26-canary-regression/${m}_mcp.gms
done
```

Expected: zero byte-diffs (since the committed baseline reflects current main, before the patch). Any diff means the broader gate is firing on a canary that the narrow gate didn't touch.

> **Note on the historical `/tmp/sprint25-golden/` reference:** earlier drafts of this section pointed at `/tmp/sprint25-golden/<model>_mcp.gms`, which was the Sprint 25 Day 0 golden directory generated by `docs/planning/EPIC_4/SPRINT_25/PLAN.md` Day 0 setup. That `/tmp/` directory is ephemeral and not guaranteed to exist for Sprint 26 prep work. Use `data/gamslib/mcp/<model>_mcp.gms` (the committed artifacts from current main) as the baseline instead — these are always available and reflect the latest merged state.

**Test Case 2: Survey full corpus for unintended gate activation**

The prototype patch from Task 3 (the 1-line `$cond` removal) does NOT yet emit any debug marker on its own — neither `SPRINT26_PATTERN_C_DEBUG` nor `PATTERN_C_GATE_FIRED` exist in the codebase. To survey gate activations across the full corpus, the prototype patch must include a **temporary instrumentation print** at the gate-fire site. Add the following line inside the gate's match branch in `src/kkt/stationarity.py` (alongside the prototype-patch change), gated on a model name so it's easy to attribute:

```python
import sys  # if not already imported
print(f"[SPRINT26_PATTERN_C_GATE_FIRED] model={model_ir.model_name} eq={equation_name}", file=sys.stderr)
```

Pattern modeled after Sprint 25's `[SPRINT25_DAY2][<tag>]` debug-print convention (per `docs/planning/EPIC_4/SPRINT_25/DAY5_PATTERN_A_INVESTIGATION.md`). The tag MUST be removed before the prototype patch merges — it's prep-time instrumentation only, not a permanent feature.

Then count gate firings across the 142 in-scope set:

```bash
.venv/bin/python scripts/gamslib/run_full_test.py --only-translate --quiet 2>&1 | \
  grep -c "\[SPRINT26_PATTERN_C_GATE_FIRED\]"
```

Expected: 4–8 firings (the 4 target models + possibly launch + a small number of true-positive Pattern C variants). If >12, gate is too permissive (false positives on previously-clean models). If <4, gate is too narrow (the prototype isn't catching the targets it's supposed to). The exact firing count + per-model attribution is what gets recorded in `PATTERN_C_HYPOTHESIS_VALIDATION.md`.

Alternative if temporary instrumentation is undesirable: use the existing `SPRINT25_DAY2_DEBUG=1` env var (which traces `_diff_varref` + `_partial_collapse_sum` per Sprint 25 convention), grep for `_partial_collapse_sum` entries on the 4 target models, and confirm the Pattern C path is being hit. This is less precise than the dedicated marker but doesn't require code changes.

### Risk if Wrong

- **Gate too permissive:** Tier 0/1 canaries regress; Sprint 26 must abort Priority 1 mid-sprint, replicating the Sprint 25 #1308 → #1351 rollback pattern.
- **Gate too narrow after refinement:** target models don't actually fire the broader gate; Priority 1 lands without Match gain.
- **Hidden third predicate needed:** the Pattern C generalization isn't a simple `$cond` removal; needs additional design work in prep, not Sprint 26 Day 1.

### Estimated Research Time

3 hours (within Task 3 hypothesis-validation budget — prototype patch + canary regression + survey)

### Owner

AD/KKT engineer (Task 3)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:** Broader gate (no `$cond` filter) is **far too permissive**. Prototype patch fired 122 times across the 11 Tier 0/1 canaries (vs expected 4–8 firings across the entire 142 in-scope set). Most firings produced no byte diff because the matched offset_groups have only a single zero-offset key already, but **2 of 11 canaries (quocge, prolog) plus launch (12th model) regressed byte-stably**. The regressions reproduce the Sprint 25 #1351 bug shape: per-offset terms collapse into single zero-offset terms, losing cross-element aggregation.

**Evidence:**

- Prototype patch applied at `src/kkt/stationarity.py:4339` re-enabling the gate with broader predicate; reverted before commit. See `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` §1.5 for the patch source.
- Canary regression table: `PATTERN_C_HYPOTHESIS_VALIDATION.md` §4. quocge `stat_pq`, `stat_rt`, `stat_tm`, `stat_tz` lose per-offset terms; prolog `stat_q(i,t)` loses 4 of 5 condition-guarded terms; launch `stat_iweight`, `stat_pweight` reproduce the #1351 bug.
- `/tmp/sprint26-prototype-canaries/{quocge,prolog,launch}_mcp.gms` vs `/tmp/sprint26-baseline-canaries/` — diff excerpts in `PATTERN_C_HYPOTHESIS_VALIDATION.md` §1.6.

**Decision:** REPLAN — the simple `$cond` removal is **structurally insufficient**. The downstream consolidated zero-offset builder must first be fixed (Phase A in the replanned Sprint 26 Priority 1) per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups (revised)" before any gate widening can land safely.

---

## Unknown 1.2: Is `sameas`-decomposed SAM-block alias detection a generalization of the launch-shape gate, or a separate detection path?

### Priority

**Critical** — cesam2 (#1355) is one of the 4 Pattern C target models and exhibits a `nu_COLSUM(i±N)$(jj(i±N))` pattern where the `$(jj(i±N))` guard is from a `sameas`-decomposed SAM block. If this is a fundamentally different detection problem from the launch shape, Priority 1 needs a more substantial design change than a simple gate widening.

### Assumption

The cesam2 `sameas`-decomposed SAM-block alias case is a generalization of the same alias-detection logic as the launch-shape gate, just with an additional `sameas` guard on the alias index. Adding `sameas`-aware predicate to the existing gate logic is sufficient; no separate detection path is needed.

### Research Questions

1. In cesam2's emitted `stat_tsam(i,j)`, what is the source equation that generates the `$(jj(i±N))` pattern? Is the source's `tsam(i,j)` declaration shape responsible, or is it the AD layer that introduces the `jj` guard?
2. Does the `sameas`-conditional cross product in the source (`sameas('ACT', 'CAP') and ...`) get decomposed at parse time or at AD time?
3. Is `jj` a subset of `i`, an alias of `i`, or a separate set with `sameas`-based membership? (Determines whether the gate predicate needs alias-detection or subset-detection.)
4. Does adding `sameas`-aware logic to the existing gate also fire correctly on camcge/fawley/otpop, or is `sameas` cesam2-specific?
5. Is there a single unified predicate that catches both the launch shape and the cesam2 shape, or are they two separate predicates with overlap?

### How to Verify

**Test Case 1: Inspect cesam2 emit + source**

```bash
# Get the cesam2 source's tsam declaration + the emitted stat_tsam
grep -nE "Equation tsam|tsam\(" data/gamslib/raw/cesam2.gms | head -10
.venv/bin/python -m src.cli data/gamslib/raw/cesam2.gms -o /tmp/cesam2.gms --skip-convexity-check --quiet
grep -nA5 "^stat_tsam" /tmp/cesam2.gms | head -30
```

Expected: identify whether `jj` is alias / subset / separate set; identify which AD code path produces the `sameas`-decomposed offset cross-product.

**Test Case 2: Hand-derive formal KKT for cesam2's `tsam(i,j)`**

Compute `∂tsam(i,j)/∂tsam_var(k,l)` from the source NLP. Determine the expected form (with or without explicit `sameas` guards). Compare against the emitted form.

**Test Case 3: Survey other models for `sameas`-decomposed alias patterns**

```bash
# Note: `sameas(` is a GAMS-specific function call; no word-boundary anchor needed
# (POSIX ERE doesn't support `\b`; `(^|[^[:alnum:]_])` would be the portable form,
# but `sameas(` is distinctive enough on its own).
grep -rE "sameas\(" data/gamslib/raw/*.gms 2>/dev/null | wc -l   # count lines mentioning sameas
grep -lE "sameas\(" data/gamslib/raw/*.gms 2>/dev/null | head -10  # which models
```

Expected: identify any other model in the 142 in-scope set that uses `sameas`-decomposed cross-products and would be affected by the new logic.

### Risk if Wrong

- **Separate detection path needed:** Priority 1 effort estimate jumps from 12–18h to 18–28h; Sprint 26 may not land cesam2 (#1355).
- **`sameas` predicate too permissive:** other models with `sameas` patterns regress; canary set enlarges and bug surface widens.
- **Source-vs-AD decomposition is different from assumed:** the "fix the gate" approach is wrong; need to fix the AD layer instead, which is a different code path entirely.

### Estimated Research Time

2 hours (within Task 3 budget — cesam2 source inspection + hand-derived KKT + sameas corpus survey)

### Owner

AD/KKT engineer (Task 3)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:** cesam2's `sameas`-decomposed SAM-block alias case **is** a generalization of the launch-shape gate — the AD layer enumerates the alias `j` over `i`'s positions via offsets gated by `ord(j) = N`. Hand-derived formal KKT for `stat_tsam(i,j)` confirms a clean `nu_COLSUM(j)$(jj(j) and <sameas-block-guard>)` form. The 18 per-offset terms in the current emit are mathematically equivalent to this single sum-form term, but require the consolidated builder to merge the equation-domain summation with the sameas-block guard.

**Evidence:**

- Hand-derived formal KKT: `/tmp/sprint26-day0-validation/cesam2_formal_kkt.md`
- Buggy emit excerpt: `/tmp/sprint26-day0-validation/cesam2_mcp.gms` line 300 — 18 `nu_COLSUM(i±N)` terms gated by `ord(j) = N` selectors.
- Source: `data/gamslib/raw/cesam2.gms:387` — `COLSUM(jj).. sum(ii, TSAM(ii,jj)) =e= Y(jj);`. Alias `Alias(i,j), (ii,jj);`.
- Prototype gate firings on cesam2: 24.

**Decision:** Sprint 26 Phase B (gate generalization) must include sameas-block-guard preservation. Same code path as the launch fix (Phase A) — not a separate detection path — but the consolidated builder needs to merge `sum(j$(jj(j)), ...)` with the `<sameas-block-guard>` correctly.

---

## Unknown 1.3: Will the Pattern C generalization interact with the #1334 ParamRef substitution fix?

### Priority

**High** — Both #1334 and the Pattern C generalization touch `src/kkt/stationarity.py` and both target otpop. If they interact, Sprint 26 needs to land them in a specific order, and the canary regression for one may need to include the other's patch state.

### Assumption

#1334 (`_replace_indices_in_expr` ParamRef branch fix) and Pattern C generalization (`_partial_collapse_sum` or similar) are orthogonal — they touch different functions in `src/kkt/stationarity.py` and can be landed in either order without test interference.

### Research Questions

1. Does `_replace_indices_in_expr` get called by the Pattern C gate code path, or are the two functions in unrelated control flow?
2. Does fixing #1334 first change the otpop emit shape such that the Pattern C target pattern no longer appears (i.e., #1334 actually subsumes #1357 — see Unknown 5.3)?
3. Does the Pattern C gate widening expose any latent #1334-class bugs that were masked by the narrow gate?
4. Are there shared helper functions (e.g., `_collect_bound_indices`, `_alias_match`) that both fixes modify?

### How to Verify

**Test Case 1: Code-path dependency analysis**

```bash
# Find call relationships
grep -nE "_replace_indices_in_expr|_partial_collapse_sum|_apply_alias_offset_to_deriv" \
  src/kkt/stationarity.py | head -30
```

**Test Case 2: Apply patches in opposite orders**

Apply #1334 patch first → run otpop translate → record emit. Apply Pattern C patch second → record emit. Compare to: Pattern C first → otpop emit → #1334 second → emit. If both orderings produce the same final emit, the patches are orthogonal.

### Risk if Wrong

- **Interaction means landing order matters:** Sprint 26 sequence must put one fix before the other; canary regression for the second includes the first's patch state. Adds coordination overhead.
- **#1334 subsumes #1357:** the Pattern C target list shrinks from 4 to 3 (camcge/cesam2/fawley); otpop is fixed by Priority 5 work instead. This affects Priority 1 budget allocation and Match-gain projection.

### Estimated Research Time

2 hours (within Task 3 + Task 7 — code-path analysis + opposite-order patch experiment)

### Owner

AD/KKT engineer (Task 3 + Task 7)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:**

- Code-path orthogonality (camcge/cesam2): Pattern C generalization works on `_compute_index_offset_key` + offset_groups consolidation in `src/kkt/stationarity.py:4318–4346`. #1334 (`_replace_indices_in_expr` ParamRef branch) is in `src/kkt/stationarity.py:2295–2479` — different function, different control flow. The two patches can land in either order without test interference.
- **otpop subsumption by #1334 confirmed**: per the original issue doc and verified via this task — otpop `$141` errors trace to phantom-offset markers (`nu_adef(tt+1)`, `nu_pdef(tt+2)`, etc., 5 markers total) which match the #1334 spurious-Sum-on-subset-ParamRef bug pattern. otpop's primary `$171` blocker is the comp_up subset/superset shape (same as fawley), unrelated to either Pattern C or #1334.
- **Pattern C target list shrinks 4 → 2** (camcge, cesam2 only). otpop reclassifies to #1334 + comp_up subset-domain workstream.

**Evidence:**

- otpop emit static analysis: `grep -oE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+" /tmp/sprint26-day0-validation/otpop_mcp.gms` → 5 markers (`nu_adef(tt+1)` ×2, `nu_pdef(tt+2)`, `nu_pdef(tt+1)`, `nu_adef(tt+4)`).
- otpop GAMS lst: `/tmp/sprint26-day0-validation/otpop.lst` — `$171` at lines 221, 253 (comp_up_x), `$141` at 321 (downstream cascade).
- Issue doc itself: `docs/issues/ISSUE_1357_otpop-stationarity-domain-violations-171.md` §"Diagnostic / Possible Subsumption" already flagged subsumption by #1334.

**Decision:** Sprint 26 Priority 1 budget allocation excludes otpop. otpop's `$141` portion subsumed by Priority 5 (#1334). otpop's `$171` portion routes to a new comp_up subset-domain widening workstream (alongside fawley's reclassification) — out of Pattern C scope.

---

## Unknown 1.4: Is the consolidated `sum(j$(domain_filter), imat(j,i) * nu_<eq>(j))` form mathematically equivalent to the per-offset enumeration across all 4 target models?

### Priority

**Critical** — If the consolidated form is NOT mathematically equivalent to the per-offset enumeration for some target models, the Pattern C generalization produces a structurally-different (and incorrect) MCP for those models. PR19 pre-merge solve-time validation should catch this, but discovering it during prep prevents wasted Sprint 26 effort.

### Assumption

For each of the 4 Pattern C target models (camcge, cesam2, fawley, otpop), the consolidated `sum(j$(j ∈ valid-domain-of-imat-second-index), imat(j,i) * nu_<eq>(j))` form is mathematically equivalent to the buggy per-offset enumeration `+ ((-1) * imat(i,i)) * nu_<eq>(i) + (((-1) * imat(i+1,i)) * nu_<eq>(i+1))$(ord(i) <= card(i)-1) + ...`. Both forms compute the correct Lagrangian contribution from the eq's body's `sum_j imat(i,j) * <var>(j)` term to `stat_<var>(i)`.

### Research Questions

1. Does the per-offset enumeration's set of `(±N, ord(i) <= card(i) - N)` guards correctly cover every element of the second-index domain? (E.g., for `i ∈ {1..N}`, do the offsets `{-N..+N}` × the guards correctly produce one term per `j ∈ {1..N}`?)
2. Is the per-offset enumeration over-counting or under-counting any element? (Sprint 25 #1351 found that the launch consolidation gate was under-counting because the consolidated form lost cross-element aggregation.)
3. Does the consolidated `sum(j$(domain_filter), ...)` form's `domain_filter` accurately encode the second-index domain restriction? (E.g., for `imat(i,j)` declared on `(c,c)` with `c` a subset of `i`, the filter must restrict `j ∈ c`.)
4. Are there edge cases (empty subset, single-element domain, alias chains) where the two forms diverge?
5. Does the consolidated form need a `$onMultiR` or similar GAMS pragma to compile correctly under PATH?

### How to Verify

**Test Case 1: Element-by-element comparison on small models**

Pick the smallest of the 4 target models (likely fawley or otpop). For each `i` in the equation's domain, manually enumerate the per-offset terms and the consolidated `sum(j, ...)` terms. Confirm they produce identical sets.

**Test Case 2: Sprint 25 #1351 cross-check**

The Sprint 25 launch-Pattern-C consolidation rollback (#1351, see `docs/planning/EPIC_4/SPRINT_25/SPRINT_LOG.md` Day 11) documented "the consolidated zero-offset Sum lost the cross-element aggregation entirely." Confirm the new Sprint 26 consolidation form does NOT have the same loss-of-aggregation bug. Specifically, the consolidated form must iterate over ALL elements of the second-index domain, not just the `j = i` element.

**Test Case 3: Symbolic comparison via SymPy**

Pick a representative camcge stationarity equation. Build the per-offset enumeration as a SymPy expression. Build the consolidated `sum(j, ...)` as a SymPy expression. Compute the symbolic difference. Confirm zero (or document why the difference is non-zero).

### Risk if Wrong

- **Forms not equivalent:** Pattern C generalization produces incorrect MCPs for some target models. PR19 catches this at solve time, but Priority 1 effort is wasted.
- **Forms equivalent for camcge/cesam2 but not fawley/otpop:** Priority 1 lands for 2 of 4 targets; Sprint 26 Match gain is 1/2 of projected.
- **Sprint 25 #1351 mistake repeated:** the new consolidation drops cross-element aggregation; locally-infeasible MCPs at solve time. PR19 mitigates but Sprint 26 schedule slips.

### Estimated Research Time

3 hours (within Task 3 + Task 9 — element-enumeration comparison on 1 target model + #1351 cross-check + SymPy verification)

### Owner

AD/KKT engineer (Task 3)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:** The per-offset enumeration **IS** mathematically equivalent to a `sum(j$(domain_filter), ...)` form on camcge and cesam2 — but only because `card(i)` happens to equal the total offset range (camcge `card(i)=11`, ±10 offsets; cesam2 `card(i)=10`, ±9 offsets). The current emit is correct in spirit but rejected at GAMS compile-time due to symbolic out-of-domain references (`$141` errors). However, **the consolidated builder's current implementation is structurally incomplete** — it collapses all offset_groups under a single zero-offset key without restoring the `sum(...)` form. The Sprint 25 #1351 evidence (and the Task 3 prototype experiment regenerating the bug on quocge/prolog/launch) confirms this.

**Evidence:**

- camcge: `card(i)=11`, offsets `{-10..+10}`, 21 per-offset terms cover all 11 elements `j ∈ {1..11}` per `i`. Hand-derived formal KKT confirms equivalence to `sum(j, imat(j,i)*nu_ieq(j))`. See `/tmp/sprint26-day0-validation/camcge_formal_kkt.md`.
- cesam2: `card(i)=10`, offsets `{-9..+9}`, 18 per-offset terms (gated by `ord(j)=N`) cover all 10 elements via the `j = i + N` selector. Hand-derived formal KKT confirms equivalence to `nu_COLSUM(j)$(jj(j))`. See `/tmp/sprint26-day0-validation/cesam2_formal_kkt.md`.
- fawley: NO per-offset enumeration present in emit. Bug is in comp_up subset/superset, NOT Pattern C. See `/tmp/sprint26-day0-validation/fawley_formal_kkt.md`.
- Sprint 25 #1351 cross-check passed: the prototype patch reproduces the loss-of-aggregation bug. The new Sprint 26 consolidation form (Phase A) MUST iterate over the equation domain with the body's condition, not collapse to `nu_<eq>(i)` only. See `PATTERN_C_HYPOTHESIS_VALIDATION.md` §1.6 launch diff.
- SymPy comparison NOT performed (deemed unnecessary given the structural argument from card(i) coverage and the launch #1351 reproduction).

**Decision:** Sprint 26 Phase A must rewrite the consolidated zero-offset builder to emit `sum(j$(domain_filter), <body>)` over the equation domain, preserving cross-element aggregation. The mathematical equivalence between per-offset enumeration and the consolidated sum form is confirmed for camcge and cesam2 — but only after Phase A's correct implementation (NOT the current collapsed form).

---

## Unknown 1.5: How many Tier 0/1 canary models contain `imat(i,j)`-style SAM-coefficient patterns at risk of incorrect gate firing?

### Priority

**Medium** — Drives the size of the canary regression set for Task 3. If 0 of 11 canaries have `imat`-shaped patterns, the regression is fast and clean; if 5+ do, prep needs additional analysis to confirm the broader gate doesn't fire on them.

### Assumption

Most Tier 0/1 canary models (dispatch, quocge, partssupply, prolog, sparta, gussrisk, ps2_f, ps3_f, ship, splcge, paklive) do NOT contain SAM-coefficient `imat(i,j)`-style patterns, so the broader Pattern C gate naturally doesn't fire on them. Maybe 1–2 (CGE-family canaries — quocge, splcge) might have similar shapes; the rest are safe.

### Research Questions

1. Of the 11 Tier 0/1 canaries, which ones are CGE family (with SAM-coefficient matrices)?
2. For the CGE-family canaries (quocge, splcge), do their stationarity equations currently emit per-offset `nu_<eq>(i±N)` patterns that the broader gate would consolidate?
3. If a canary's emit changes, would the new emit still be byte-stable (idempotent under repeated runs) and produce a solving MCP?

### How to Verify

**Test Case 1: Categorize canaries by SAM presence**

```bash
# Note: `\b` isn't a word-boundary in POSIX ERE; using `grep -w` for portability.
# `-w` matches whole words (boundary on `[a-zA-Z0-9_]`), so `imat` matches but
# `imat_extra` doesn't. `[a-z]+coef`-suffix matches still need a regex pattern;
# we use the portable POSIX-ERE `(^|[^[:alnum:]_])` boundary for that one.
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  echo "=== $m ==="
  imat=$(grep -cw imat "data/gamslib/raw/${m}.gms" 2>/dev/null || echo 0)
  sam=$(grep -cw SAM "data/gamslib/raw/${m}.gms" 2>/dev/null || echo 0)
  coef=$(grep -cE "(^|[^[:alnum:]_])[a-z]+coef([^[:alnum:]_]|$)" "data/gamslib/raw/${m}.gms" 2>/dev/null || echo 0)
  echo "  imat=$imat sam=$sam coef-suffixed=$coef"
done
```

**Test Case 2: For each at-risk canary, inspect current emit for phantom-offset patterns**

```bash
for m in quocge splcge; do
  grep -cE "nu_[a-zA-Z_]+\([^)]+\+[0-9]+\)" data/gamslib/mcp/${m}_mcp.gms 2>/dev/null
done
```

Expected: count of phantom-offset terms per canary. If non-zero, the canary may behave like a Pattern C target (good — gate should fire) or may be a true-positive canary (bad — gate should not fire). Determined by Test Case 3.

**Test Case 3: For each at-risk canary, check if current MCP solves and matches**

Use `data/gamslib/gamslib_status.json` to confirm each at-risk canary is currently `solve_success` + `match`. If yes, gate must NOT change emit (or must produce equivalent MCP that still solves+matches).

### Risk if Wrong

- **Many canaries at risk:** Task 3 prep budget needs to expand to cover detailed regression on 5+ canaries instead of 0–2.
- **Canary regresses unexpectedly during Sprint 26 Day 3+:** Priority 1 must rollback (Sprint 25 #1308 → #1351 pattern repeats).

### Estimated Research Time

1 hour (within Task 3 — corpus survey + emit grep on at-risk canaries)

### Owner

AD/KKT engineer (Task 3)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:** Of the 11 Tier 0/1 canaries, the prototype broader-gate patch fires on 9 (all except `dispatch`, `sparta`, `gussrisk`). Most firings are no-op (single offset_group, gate consolidation has no effect). However, **2 of 11 canaries (quocge, prolog) regress byte-stably** under the prototype patch, with multiple stationarity equations losing per-offset terms and collapsing to single zero-offset terms.

| Canary | Firings | Byte-diff | Notes |
|---|---|---|---|
| dispatch | 0 | byte-stable | non-CGE |
| **quocge** | 67 | **REGRESSED** (14 diff lines) | CGE family (`ax(i,j)`); `stat_pq, stat_rt, stat_tm, stat_tz` lose per-offset terms |
| partssupply | 4 | byte-stable | |
| **prolog** | 13 | **REGRESSED** (4 diff lines) | `stat_q(i,t)` loses 4 of 5 condition-guarded terms |
| sparta | 0 | byte-stable | |
| gussrisk | 0 | byte-stable | |
| ps2_f | 4 | byte-stable | |
| ps3_f | 4 | byte-stable | |
| ship | 6 | byte-stable | |
| splcge | 14 | byte-stable | CGE family — at-risk pattern present but offset_groups already consolidated correctly |
| paklive | 10 | byte-stable | lead/lag model, the gate's IndexOffset-presence guard correctly prevents firing |

**Evidence:**

- Prototype run output: `/tmp/sprint26-prototype-canaries/<m>_mcp.gms` and `<m>_gate.stderr`.
- Diff excerpts: `PATTERN_C_HYPOTHESIS_VALIDATION.md` §1.6 (quocge `stat_pq` losing `(i+1)/(i-1)` terms; prolog `stat_q(i,t)` losing 4 of 5 sameas-block terms).
- Counter-evidence from byte-stable cases: paklive's lead/lag pattern + splcge's CGE shape don't regress because the existing IndexOffset-on-domain check (`_body_has_index_offset_on_sets`) correctly excludes them.

**Decision:** The broader gate is not bounded by the launch shape — it activates on any model with an alias-only inner sum where the source body lacks a concrete IndexOffset. The Sprint 26 Phase B predicate must be tighter than the prototype's "no IndexOffset" check; it must also require the source body's expansion to currently produce per-offset terms that need consolidation (and NOT activate on canaries where the offset_groups already correctly consolidate). Combined with the Phase A consolidated-builder fix, this should reduce gate firings to 4–8 across the full 142 in-scope set as originally projected.

---

## Unknown 1.6: Will the Task 3 Day-5-methodology prototype produce a binary PROCEED / REPLAN signal, or an ambiguous result that doesn't drive a decision?

### Priority

**Critical** — The entire Task 3 PR16 prep activity hinges on this. The Day 5 methodology in Sprint 25 produced a clean "AD is correct" signal because the comparison was byte-equality vs the formal derivative. If the Sprint 26 Pattern C generalization produces partial agreement (e.g., camcge+cesam2 confirm, fawley diverges by 1 term), the decision becomes ambiguous and the prep methodology fails to deliver the expected unambiguous signal.

### Assumption

Applying the Day 5 methodology (trace + emitted-artifact byte comparison against formal symbolic derivative) to the Pattern C generalization on 3 representative target models will produce a clean per-model PROCEED / DISPROVE / PARTIAL-DISPROVE classification. If 3/3 PROCEED, Sprint 26 commits the budget. If 1+ DISPROVE, replan. If PARTIAL-DISPROVE on 1 of 3, treat as DISPROVE (be conservative).

### Research Questions

1. Is the formal derivative for camcge/cesam2/fawley's stationarity equations tractable to hand-derive (≤ 30 minutes per model)?
2. Are the emitted forms small enough (≤ 100 lines) to byte-compare line-by-line?
3. What's the expected result for otpop (#1357) — does the Pattern C generalization apply, or is otpop subsumed by #1334 (per Unknown 5.3)? Held-out otpop is the 4th model after PROCEED on 3.
4. If 1 of 3 produces PARTIAL-DISPROVE, what's the decision rule — defer that model to Sprint 27, or replan all of Priority 1?

### How to Verify

**Test Case 1: Hand-derive the formal KKT for one stationarity equation per target model in 30 minutes each**

Pick the simplest stationarity equation from each model's source (camcge `stat_dk`, cesam2 `stat_tsam`, fawley `stat_<simple>`). Write out the formal derivative on paper or in `/tmp/sprint26-day0-validation/<model>_formal_kkt.md`.

**Test Case 2: Byte-compare emitted vs formal**

Use `diff -u` or a small Python script to count matching/diverging terms per model. Document the diverging terms (these are the Pattern C bug sites).

**Test Case 3: Decision rule documentation**

In `PATTERN_C_HYPOTHESIS_VALIDATION.md`, codify the decision rule: 3/3 PROCEED → Sprint 26 commits Priority 1 budget; 2/3 PROCEED → defer the disproved model to Sprint 27, proceed with 2-target Priority 1; 1/3 or 0/3 PROCEED → replan Priority 1 entirely (most likely action: defer Pattern C generalization to Sprint 27 and pull AD residuals #1334/#1335 to Priority 1).

### Risk if Wrong

- **Methodology produces ambiguous signal:** Sprint 26 can't make a clean PROCEED/REPLAN decision; effort gets wasted on Day 1 of Sprint 26 trying to interpret prep findings.
- **Formal derivative is intractable to hand-derive:** the Day 5 methodology can't be applied to Pattern C; prep needs a different validation approach (e.g., SymPy comparison, test-vector-based comparison).

### Estimated Research Time

2 hours (within Task 3 — methodology pre-flight on 1 target model before committing the 6–8h Task 3 budget)

### Owner

AD/KKT engineer (Task 3)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 3 (Pattern C Hypothesis Validation PR16)
**Date:** 2026-05-07

**Findings:** The methodology produced an **unambiguous REPLAN signal** with concrete per-model verdicts:

| Model | Verdict | Evidence shape |
|---|---|---|
| camcge | ✅ CONFIRMED Pattern C plain-alias variant | 21 phantom-offset terms in stat_dk; formal KKT derived in 30 minutes |
| cesam2 | ✅ CONFIRMED Pattern C `sameas`-decomposed variant | 18 phantom-offset terms in stat_tsam; formal KKT derived in 30 minutes |
| fawley | ❌ DISPROVED — not Pattern C | 0 phantom offsets; bug is comp_up subset/superset |
| otpop (held-out) | ❌ DISPROVED — primarily not Pattern C | 5 phantom offsets but #1334; primary blocker is comp_up subset/superset |

**Decision rule application:** 2/3 PROCEED on Pattern C → defer disproved models. **BUT** the architectural blocker (#1351 consolidated builder is broken) means even the 2 confirmed sites can't be unblocked by gate widening alone. Final recommendation: **REPLAN with two-phase scope** (Phase A consolidated-builder fix + Phase B gate generalization for 2 targets), reducing target list 4 → 2 (camcge + cesam2 only) and reducing projected gain (+2 Solve / +2 Match instead of +4 / +3–4).

**Evidence:**

- Hand-derived formal KKT excerpts at `/tmp/sprint26-day0-validation/<model>_formal_kkt.md` (3 models × ~30 min each = 90 min total).
- Byte-comparison: `grep -oE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+"` on each emit — phantom-offset count is the binary indicator (>0 = candidate Pattern C; 0 = disproved).
- GAMS lst inspection for fawley/otpop: confirmed both are comp_up subset/superset domain widening, not Pattern C.
- Decision document: `docs/planning/EPIC_4/SPRINT_26/PATTERN_C_HYPOTHESIS_VALIDATION.md` records the per-model verdicts, decision rule application, and Sprint 26 Priority 1 replan with revised scope/effort/projection.

**Decision:** PR16 methodology validated. The methodology produced a clean, actionable signal in ~5h of prep work. Estimate: ~5h prep saves ~10–16h of mid-sprint waste — net savings ~5–11h. Recommendation: codify PR16 into CONTRIBUTING.md / sprint-prep checklist for any future sprint with 3+ issues claimed to share a single hypothesized root cause.

---

# Category 2: Pattern A Cohort Reclassification

Priority 2 workstream — Issues #1138, #1139, #1140, #1142, #1145, #1150 per the Day 7 cohort sweep classification.

## Unknown 2.1: Is the Sprint 25 Day 7 sweep classification still accurate after the Sprint 25 fix-in-place series #1338..#1352?

### Priority

**High** — The Day 7 sweep was conducted on 2026-04-24, BEFORE the Sprint 25 Day 11 fix-in-place series #1338..#1352 landed (which touched #1338..#1341 IndexOffset/SetMembershipTest, #1348 china subset chain, #1349 pindyck `.fx → .l`, #1350 srkandw `tn(t,t)` self-alias, #1351 launch Pattern C rollback). Some of the cohort issues' bug fingerprints may have shifted via these fixes. Reclassification action plan needs to verify each issue's current state, not just rely on the Day 7 sweep.

### Assumption

The Day 7 cohort sweep classifications (Pattern C plain-alias variant for #1138; AD-correct/pipeline-excluded for #1139; AD-correct multi-solve dynamics for #1140; Pattern C Bug #2 for #1142; offset-handling/condition-guard for #1145; split for #1150 — qabel = Pattern C massive-enumeration, abel = AD-correct/solver noise) remain accurate post Sprint 25 fix-in-place series.

### Research Questions

1. For each cohort issue, run the canonical model translate + emit on current main and grep for the documented bug fingerprint. Does the fingerprint still appear?
2. Did any of #1338..#1352 fix the cohort issue's underlying bug as a side-effect?
3. For #1142 (subsumed by #1307 Pattern C Bug #2): is the #1307 fix scheduled in Sprint 26 Priority 1, or does it need separate work?
4. For #1150 (split into qabel/abel): did Sprint 25 #1311 (closed during S25) actually fix abel?

### How to Verify

**Test Case 1: Per-issue fingerprint re-verification**

```bash
# For each issue, fetch the canonical model + grep for the bug fingerprint.
# Issues with no documented fingerprint (e.g., #1139 meanvar — currently
# pipeline-excluded; #1140 ps2_f_s — multi-solve dynamics, not a single-line
# pattern; #1145 cclinpts — offset-handling bug requires manual emit inspection)
# are flagged for manual verification rather than auto-grepped, since an empty
# fingerprint would make `grep -cE ""` match every line and produce a misleading
# non-zero count.
for issue_model in "1138:irscge:nu_eqpzs.*\\+" "1139:meanvar:" "1140:ps2_f_s:" "1142:launch:nu_dweight.*\\+" "1145:cclinpts:" "1150:qabel:k-[0-9]+"; do
  issue=$(echo "$issue_model" | cut -d: -f1)
  model=$(echo "$issue_model" | cut -d: -f2)
  fingerprint=$(echo "$issue_model" | cut -d: -f3-)
  echo "=== Issue #$issue / $model ==="
  if [ -z "$fingerprint" ]; then
    echo "  (no auto-greppable fingerprint — manual emit inspection required;"
    echo "   see docs/issues/ISSUE_${issue}_*.md for the bug shape and re-emit"
    echo "   data/gamslib/mcp/${model}_mcp.gms to inspect)"
    continue
  fi
  if [ -f "data/gamslib/mcp/${model}_mcp.gms" ]; then
    count=$(grep -cE "$fingerprint" "data/gamslib/mcp/${model}_mcp.gms")
    echo "  fingerprint matches: $count"
    [ "$count" = "0" ] && echo "  (no match — possibly resolved by S25 fix-in-place series)"
  else
    echo "  (data/gamslib/mcp/${model}_mcp.gms not found — re-emit before checking)"
  fi
done
```

**Test Case 2: Sprint 25 #1311 outcome check**

Verify #1311 is CLOSED and the qabel/abel u-quadratic AD subset-domain bug fix landed. Check that abel's emit no longer has the `Const(0.0)` u-derivative documented in `docs/planning/EPIC_4/SPRINT_25/DAY8_QABEL_ABEL_REASSESSMENT.md`.

```bash
gh issue view 1311 --json state | head -3
grep -E "u\(.*\)" data/gamslib/mcp/abel_mcp.gms | head -5
```

### Risk if Wrong

- **Day 7 classifications stale:** Reclassification action plan (Task 4) is wrong; Sprint 26 work on Priority 2 produces incorrect issue closures.
- **Some cohort bugs already fixed by #1338..#1352:** Sprint 26 Priority 2 budget can shrink (good); some `sprint-26` labeled issues should be closed during prep, not during execution.

### Estimated Research Time

2 hours (within Task 4 — per-issue grep + #1311 outcome cross-check)

### Owner

Sprint planning (Task 4)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 4 (Pattern A Cohort Reclassification Pre-Work)
**Date:** 2026-05-07

**Findings:** 5 of 6 Day 7 classifications still accurate on current main; 1 stale (#1150 qabel half — already resolved by Sprint 25 #1312 closure for the massive lag enumeration; the related #1311 closure separately fixed the criterion u-gradient drop). One classification needs a Bug-#1-fix-rollback caveat (#1142 — Sprint 25 Day 11 #1351 rolled back the Day 6 PR #1308 fix, so launch's emit has the phantom offsets again).

| Issue | Day 7 → Re-verified status | Evidence (current emit on main, 2026-05-07) |
|---|---|---|
| #1138 | ✅ Pattern C plain-alias confirmed | `stat_pq(i)` has `nu_eqpzs(i+1)$(ord(i) <= card(i) - 1)` and `(i-1)$(ord(i) > 1)`. Same family as quocge / camcge (#1354). |
| #1139 | ✅ AD-correct confirmed | Phantom-offset count = 0 in meanvar emit. Clean Sprint-24 renamed-alias sums. `legacy_excluded` per v2.2.1 schema. |
| #1140 | ✅ AD-correct confirmed (additional context: now `non_convex` runtime-filter) | Phantom-offset count = 0 in ps2_f_s emit. All 7 PS-family models reclassified `non_convex` per `BASELINE_METRICS.md` §5. |
| #1142 | ⚠ Day 7 said Bug #1 "fixed Day 6"; current main has Bug #1 BACK due to #1351 rollback | `stat_iweight(s)` emit has `nu_dweight(s±1)`, `(s±2)` per-offset terms. Bug #2 still pending (#1307 OPEN). Both addressed by Sprint 26 Priority 1 Phase A per Task 3 REPLAN recommendation. |
| #1145 | ✅ Condition-guard / sign bug confirmed (NOT Pattern A) | `stat_b(j)` and `stat_fb(j)` have legitimate `(j-1) * 1$((not last(j)))` / `1$((not first(j)))` offset terms matching the source body. Not an AD bug. |
| #1150 (qabel half) | ❌ STALE — Day 7 said "k-9..k-68 massive enumeration"; current main has only `k-1`/`k+1` | Resolved by **#1312** (CLOSED 2026-04-25 during S25 — *"Pattern C variant: stationarity emits massive phantom stateq lag enumeration on qabel (k-9 .. k-68)"*) for the enumeration fix; related **#1311** (CLOSED 2026-04-25 — *"AD: criterion's u-quadratic gradient dropped to Const(0.0) when sum index is a subset of variable's domain"*) separately addressed the criterion-derivative half. Both contributed to making qabel and abel emits structurally identical (only `k` set definition differs). |
| #1150 (abel half) | ✅ AD-correct confirmed (additional context: now `non_convex` runtime-filter) | Reclassified `non_convex` on 2026-04-25 per `BASELINE_METRICS.md` §5.1 (Sprint 26 Prep Task 2). |

**Evidence:**

- Re-verification artifacts at `/tmp/sprint26-task4-verify/<model>_mcp.gms` for all 7 canonical models (irscge, meanvar, ps2_f_s, launch, cclinpts, qabel, abel) — translate exit=0 on current main.
- Phantom-offset grep: `grep -cE "nu_[a-zA-Z_]+\([a-zA-Z]+[+-][0-9]+" <emit>` — yields 0 for meanvar / ps2_f_s, ≥1 for irscge / launch (confirming Pattern C shape), and 0 for cclinpts (confirming non-Pattern-A).
- qabel offset enumeration: `grep -oE "k[+-][0-9]+" qabel_mcp.gms | sort -u` returns only `k-1`, `k+1` — directly contradicting Day 7's "k-9..k-68" claim.
- `gh issue view` (GitHub authoritative) confirms all 6 cohort issues OPEN with `sprint-26` label; related issues #1311, #1312, #1334 all CLOSED on GitHub. Note: the in-repo issue doc `docs/issues/ISSUE_1334_*.md` still marks `Status: OPEN` and is stale relative to GitHub state — flagged for cleanup as part of Priority 5 work.

**Decision:** Day 7 classifications remain authoritative for 5 of 6 issues. #1150 qabel half is updated to "resolved by #1312 (massive lag enumeration) + #1311 (criterion u-gradient)". #1142 needs the Bug-#1-fix-rollback annotation (already addressed by Task 3 routing to Phase A).

---

## Unknown 2.2: Per cohort issue, what is the correct Sprint 26 action — subsume vs close-as-resolved vs close-and-refile vs investigate further?

### Priority

**Medium** — Each of the 6 cohort issues needs a specific action. The Day 7 sweep gave per-issue classifications but didn't translate them into actions. This unknown drives the per-issue decision matrix in Task 4's PATTERN_A_RECLASSIFICATION_PLAN.md.

### Assumption

Per Sprint 25 retrospective §Priority 2:

- #1138 → subsume into Sprint 26 Priority 1 (Pattern C generalization)
- #1139 → close-as-resolved (AD-correct, pipeline-excluded)
- #1140 → close-and-refile under "multi-solve dynamics" or defer to Sprint 27 investigation
- #1142 → subsume into #1307 (Pattern C Bug #2; addressed by Sprint 26 Priority 1)
- #1145 → close-and-refile as "offset-handling/condition-guard bug" (Sprint 27)
- #1150 → split: close abel-portion as resolved (#1311 fixed it); subsume qabel-portion into Sprint 26 Priority 1

### Research Questions

1. For each "subsume" action, does the parent issue (Priority 1 #1306/#1307 or Priority 5 #1334) actually claim coverage? File a forward-link comment on the cohort issue noting the subsumption.
2. For each "close-and-refile" action, what's the new issue's title, body, and Sprint 27 label?
3. For each "close-as-resolved" action, what's the evidence (commit SHA, test name, or `gamslib_status.json` entry)?
4. Does any cohort issue have GitHub linkages (cross-issue references, blocking labels) that need to be updated when closing?

### How to Verify

**Test Case 1: Per-issue evidence collection**

For each cohort issue, write the action note in the format:

```markdown
## Issue #NNNN

**Day 7 classification:** [from DAY7_COHORT_SWEEP.md]
**Current emit fingerprint:** [from Unknown 2.1 verification]
**Recommended action:** [subsume / close-as-resolved / close-and-refile / investigate]
**Action evidence:** [commit SHA, parent issue, or new-issue draft body]
**GitHub linkages:** [cross-references to update]
```

### Risk if Wrong

- **Subsume action without parent coverage:** the cohort issue is closed but the bug isn't actually addressed; user-visible regression.
- **Close-as-resolved without evidence:** future contributors re-discover the same bug because there's no test pinning the resolution.

### Estimated Research Time

1.5 hours (within Task 4 — per-issue action note + GitHub linkage check)

### Owner

Sprint planning (Task 4)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 4 (Pattern A Cohort Reclassification Pre-Work)
**Date:** 2026-05-07

**Findings:** Per-issue actions documented in `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md` (one section per issue). Action distribution:

| Issue | Action | Parent / new tracker |
|---|---|---|
| #1138 | **Subsume into Sprint 26 Priority 1 Phase B** (gate generalization to plain-alias) | Phase B PR will close #1138 with forward-link |
| #1139 | **Close as not-a-bug** | meanvar is `legacy_excluded`; AD-correct emit verified |
| #1140 | **Close as informational mismatch** | All 7 PS-family models now `non_convex` runtime-filter; AD-correct emit verified |
| #1142 | **Subsume into Sprint 26 Priority 1 Phase A** (consolidated builder fix per Sprint 25 SPRINT_LOG.md Day 11 §"Open follow-ups") | Phase A PR will close #1142, #1306, #1307 (all share root cause) |
| #1145 | **Close-and-refile as Sprint 27 issue** "cclinpts: stat_b/stat_fb condition-guard or sign bug producing ~70% rel_diff" | Draft title + body in §"Issue #1145" of the reclassification plan |
| #1150 | **Close as resolved (both halves)** | qabel massive lag enumeration resolved by #1312 (CLOSED 2026-04-25); criterion u-gradient drop separately resolved by #1311 (CLOSED 2026-04-25); abel reclassified `non_convex` per Sprint 26 Prep Task 2 |

**Evidence:**

- Per-issue action notes with classification + action + (if "close-and-refile") draft new-issue title + body in `docs/planning/EPIC_4/SPRINT_26/PATTERN_A_RECLASSIFICATION_PLAN.md`.
- Parent-issue coverage verified: Sprint 26 Priority 1 Phase A (per Task 3 REPLAN recommendation) addresses launch / Bug #1 / Bug #2 — covers #1142 / #1306 / #1307. Phase B addresses plain-alias variant — covers #1138 + camcge (#1354).
- Resolution evidence for #1150: `gh issue view 1311 --json state` returns CLOSED; current emit comparison confirms qabel/abel byte-identical (only `k` set definition differs).

**Decision:** Sprint 26 Priority 2 reduces from "investigative cohort sweep" to **mechanical closure work** — 4 issue closures, 1 close-and-refile, 1 forward-link to Priority 1 PR. Estimated execution: ~1.5h (vs original 2-4h). Time saved → Priority 1 (Phase A + B) or Priority 5 (#1334 follow-up + #1335).

---

## Unknown 2.3: Will closing the 6 cohort issues surface test xfails depending on those issue numbers in their docstrings?

### Priority

**Medium** — Sprint 25 #1306 launch fix introduced an `xfail(strict=True)` on `tests/unit/kkt/test_pattern_c_alias_offset_gate.py` that references the issue number in its `reason=` argument. If any cohort issue has similar test linkages, closing the issue without updating the test produces a stale-reason error.

### Assumption

A small number of test files (≤3) reference cohort issue numbers in `xfail(reason=...)` arguments, docstrings, or comments. Closing the cohort issues requires a synchronized test-update commit.

### Research Questions

1. How many test files reference each of #1138, #1139, #1140, #1142, #1145, #1150?
2. Are the references in `xfail(reason=...)` arguments (which need synchronized update) or just docstring comments (which are advisory)?
3. Are there test files that depend on the cohort issue's bug being present (e.g., a regression-canary test that would FAIL if the bug is fixed)?

### How to Verify

**Test Case 1: Recursive grep across tests/**

```bash
# Note: `\b` isn't a word-boundary in POSIX ERE; using a numeric boundary
# `([^0-9]|$)` to ensure `#1138` doesn't match `#11380` etc.
for issue in 1138 1139 1140 1142 1145 1150; do
  echo "=== #$issue ==="
  grep -rE "#${issue}([^0-9]|\$)" tests/ 2>/dev/null
done
```

**Test Case 2: xfail-specific search**

```bash
grep -rEB1 -A2 "xfail.*reason.*113[8-9]|xfail.*reason.*114[02-7]|xfail.*reason.*1150" tests/ 2>/dev/null
```

### Risk if Wrong

- **Stale-reason errors on PRs that close cohort issues:** CI fails on the closing PR; need follow-up commit to clean.
- **Hidden regression-canary tests:** Sprint 26 Priority 2 work breaks tests it didn't intend to touch.

### Estimated Research Time

1 hour (within Task 4 — recursive grep + per-reference inspection)

### Owner

Sprint planning (Task 4)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 4 (Pattern A Cohort Reclassification Pre-Work)
**Date:** 2026-05-07

**Findings:** **Exactly 1 affected test** — `tests/unit/kkt/test_pattern_c_alias_offset_gate.py::test_alias_only_conditional_sum_emits_no_phantom_offsets`. The test is currently `xfail(strict=True)` with `reason=` explicitly tracking the Phase A fix as the un-xfail trigger:

```python
@pytest.mark.xfail(
    reason=(
        "Issue #1351: the Pattern C consolidation gate from #1306 (which this "
        "test covers) suppressed phantom ±N offsets correctly but the "
        "downstream zero-offset builder loses the cross-element aggregation, "
        ...
        "is tracked under the launch comparison-mismatch family (#1226, #945, "
        "#1142). Once that lands, remove this xfail."
    ),
    strict=True,
)
def test_alias_only_conditional_sum_emits_no_phantom_offsets(tmp_path):
```

When Sprint 26 Priority 1 Phase A lands and the test starts passing, the `xfail` decorator and the `reason=` block need to be removed (the docstring already references #1142 + #1226 + #945 — same family, all subsumed into Phase A).

**No other tests reference any of the 6 cohort issue numbers** in xfail reasons, docstrings, or comments. Verified via `grep -rE "#?(1138|1139|1140|1142|1145|1150)" tests/`.

**Evidence:**

- Recursive grep output (only match): `tests/unit/kkt/test_pattern_c_alias_offset_gate.py:51-63` — the existing #1142 reference is in the `xfail.reason=` block.
- No regression-canary tests depend on the cohort bug being present.

**Decision:** When Sprint 26 Priority 1 Phase A PR lands, the same PR (or an immediate follow-up) must remove the `xfail(strict=True)` decorator from `test_alias_only_conditional_sum_emits_no_phantom_offsets`. The test is `strict=True` so a stale-xfail-passing failure will catch the missing un-xfail commit. No other test updates needed for the Pattern A cohort closures.

---

## Unknown 2.4: Does any cohort issue have hidden dependencies on docstring-level references in `src/` or `docs/`?

### Priority

**Low** — Source-level docstring references to issue numbers don't break tests but produce stale documentation. Worth knowing but doesn't drive Sprint 26 scope.

### Assumption

Source-level (and docs-level) references to cohort issue numbers are scattered (estimated ≤ 20 references across `src/`, `docs/`) and can be batch-updated as part of the Sprint 26 Priority 2 issue closures.

### Research Questions

1. How many `src/`-level references to cohort issue numbers exist?
2. How many `docs/`-level references (excluding `docs/issues/ISSUE_*.md` and `docs/planning/`) exist?
3. Are any references in user-visible documentation (README.md, CONTRIBUTING.md, public-facing API docs)?

### How to Verify

```bash
# Note: `\b` isn't a word-boundary in POSIX ERE; using `([^0-9]|$)` numeric
# boundary so `#1138` doesn't match `#11380`.
for issue in 1138 1139 1140 1142 1145 1150; do
  echo "=== #$issue ==="
  grep -rcE "#${issue}([^0-9]|\$)" src/ 2>/dev/null
  grep -rcE "#${issue}([^0-9]|\$)" docs/ --include="*.md" 2>/dev/null | grep -vE "/issues/|/planning/"
done
```

### Risk if Wrong

- **Stale doc references after closing cohort issues:** future readers see references to closed issues without forward-links.

### Estimated Research Time

0.5 hours (within Task 4 — recursive grep)

### Owner

Sprint planning (Task 4)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 4 (Pattern A Cohort Reclassification Pre-Work)
**Date:** 2026-05-07

**Findings:** **1 source-level reference** to a cohort issue number outside `docs/issues/` and `docs/planning/`:

| Path | Line | Reference | Update needed when |
|---|---|---|---|
| `src/kkt/stationarity.py` | 4336 | `# via the launch comparison-mismatch family (#1226, #945, #1142)` | When #1142 closes (subsumed into Phase A PR) — replace with forward-link to the Phase A PR |

**No other src/ references** to any of the 6 cohort issue numbers. **No docs/ references** outside `docs/planning/` (which are the prep planning docs themselves) and `docs/issues/` (which IS the issue documentation directory and should retain references).

**Evidence:**

- Recursive grep output (only matches outside `docs/issues/` and `docs/planning/`):
  ```
  src/kkt/stationarity.py:4336:                # via the launch comparison-mismatch family (#1226, #945, #1142)
  ```
- No README.md, CONTRIBUTING.md, or other user-visible documentation references the 6 cohort issue numbers.

**Decision:** Sprint 26 Priority 2 closure of #1142 (subsumed into Phase A PR) MUST include an update to the `src/kkt/stationarity.py:4336` comment to replace `(#1226, #945, #1142)` with a forward-link to the Phase A PR. No other source/docs updates needed for the Pattern A cohort closures.

---

# Category 3: Pattern E Carryforward Re-Verification

Priority 3 workstream — Issues #1141 (kand), #1144 (catmix), #1147 (camshape). Phase E was cancelled per Sprint 25 literal Checkpoint 2 NO-GO routing.

## Unknown 3.1: Did the Sprint 25 fix-in-place series #1338..#1352 shift any of #1141 / #1144 / #1147 bucket via side-effects?

### Priority

**High** — If any Phase E carryforward was inadvertently fixed (or its bucket shifted) by Sprint 25's fix-in-place series, Sprint 26 Priority 3 budget can shrink. catmix specifically was on the Sprint 25 #1338 list (catmix translate via `expr_to_gams` IndexOffset handling for SetMembershipTest indices).

### Assumption

At least one of #1141 / #1144 / #1147 has its bucket shifted via the Sprint 25 fix-in-place series — most likely catmix (#1144) via #1338, since #1338 specifically targeted catmix translate.

### Research Questions

1. What is each Phase E model's current bucket per `data/gamslib/gamslib_status.json` (post-Sprint-25)?
2. Was the bucket different at the Sprint 25 Day 0 baseline?
3. If shifted, which Sprint 25 commit triggered the shift?
4. Does the new bucket match a different category (e.g., catmix moved from `path_syntax_error` to `path_solve_terminated`)?

### How to Verify

**Test Case 1: Per-model current status query**

```bash
.venv/bin/python <<'EOF'
import json
d = json.loads(open('data/gamslib/gamslib_status.json').read())
for mid in ('kand', 'catmix', 'camshape'):
  m = next((x for x in d['models'] if x['model_id']==mid), None)
  if m:
    t = (m.get('nlp2mcp_translate') or {}).get('status', '?')
    s = m.get('mcp_solve') or {}
    cat = (s.get('error') or {}).get('category') or s.get('outcome_category') or '?'
    cmp = (m.get('solution_comparison') or {}).get('comparison_status', '?')
    print(f"{mid:12s} translate={t} solve_cat={cat} cmp={cmp}")
EOF
```

**Test Case 2: Sprint 25 baseline vs Sprint 25 final diff**

Use the Sprint 25 Day 0 baseline `gamslib_status.json` (Task 2 output) vs current to identify per-model transitions for the 3 Phase E models specifically.

### Risk if Wrong

- **Phase E bucket shifted unexpectedly:** Sprint 26 Priority 3 has wrong target list; effort spent on already-recovered models.
- **catmix already fixed (per #1338):** can close #1144 during prep; Sprint 26 Priority 3 reduces from 3 to 2 models.

### Estimated Research Time

1.5 hours (within Task 5 — per-model status query + S25-baseline diff)

### Owner

Sprint planning (Task 5)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 5 (Pattern E Carryforward Status Survey)
**Date:** 2026-05-07

**Findings:** **2 of 3 Phase E issues had their bucket shifted by the Sprint 25 fix-in-place series** — only #1141 (kand) is unchanged.

| Issue | Model | Original | Re-verified status (gamslib_status.json + GAMS compile-only) | Bucket shift? |
|---|---|---|---|---|
| #1141 | kand | mismatch (92.5% rel_diff) | translates clean, compiles clean, solves Optimal, **mismatch (92.5% rel_diff)** | ❌ Unchanged |
| #1144 | catmix | model_infeasible (101 INFES eqs) | translates clean, compiles clean, solves **Optimal**, mismatch 0.21% rel_diff | ✅ Shifted (resolved) |
| #1147 | camshape | path_syntax_error | translates clean, compiles clean, solves **Locally Infeasible** (model_status=5) | ✅ Shifted (new bug) |

**Evidence:**

- Re-verification artifacts at `/tmp/sprint26-pattern-e/{kand,catmix,camshape}_{mcp.gms,compile.lst}` — all 3 translate exit=0, compile exit=0 with no `$NNN` errors.
- `data/gamslib/gamslib_status.json` Day 14 retest:
  - `kand.mcp_solve.model_status = 1` (Optimal); `solution_comparison.relative_difference = 0.9254`
  - `catmix.mcp_solve.model_status = 1` (Optimal); `solution_comparison.relative_difference = 0.00208` (0.21%)
  - `camshape.mcp_solve.model_status = 5` (Locally Infeasible); `solution_comparison.comparison_status = "not_tested"`
- Sprint 25 SPRINT_LOG.md Day 11 attributes catmix recovery to **#1338** (`expr_to_gams now handles IndexOffset as a direct index of SetMembershipTest`, affecting catmix/glider/markov/tricp).
- camshape: original `$141` issue partially fixed during Sprint 23/24 work; follow-up #1160 (CLOSED, *"camshape: MCP pairing error — stat_rdiff.rdiff unmatched equation"*) addressed pairing fix; new Locally Infeasible is a distinct bug not subsumed by either #1147 or #1160.

**Decision:** Sprint 26 Priority 3 fix scope **shrinks from 3 models to 1 (kand)**. catmix closes as resolved; camshape closes-and-refiles as a new Sprint 27 issue tracking the new infeasibility. Per-model action plan documented in `docs/planning/EPIC_4/SPRINT_26/PATTERN_E_STATUS.md` §"Per-model status".

---

## Unknown 3.2: Specifically — was catmix recovered by Sprint 25 #1338 (which was on the SetMembershipTest fix list)?

### Priority

**High** — Direct test of the most likely Sprint-25-side-effect-fix among the 3 Phase E models. If yes, #1144 closes during Sprint 26 prep with no further action; Sprint 26 Priority 3 shrinks by 33%.

### Assumption

#1338 (catmix translate via `expr_to_gams` IndexOffset handling for SetMembershipTest indices) actually fixed catmix's compile-time failure, but #1144 (which is about runtime/solve-time alias-domain inference, per the Day 7 sweep) is a separate bug that #1338 does NOT address.

### Research Questions

1. Does catmix currently translate (status `success` per gamslib_status.json)?
2. Does the resulting MCP compile successfully under PATH (`gams catmix_mcp.gms action=c`)?
3. Does it solve? If yes, does it match? If no, what's the failure category?
4. What was #1144's original bug fingerprint (per `ISSUE_1144_catmix-alias-domain-inference-mismatch.md`)? Does that fingerprint still appear in catmix's emit?

### How to Verify

**Test Case 1: catmix end-to-end pipeline**

```bash
.venv/bin/python -m src.cli data/gamslib/raw/catmix.gms \
  -o /tmp/sprint26-pattern-e/catmix_mcp.gms --skip-convexity-check --quiet
gams /tmp/sprint26-pattern-e/catmix_mcp.gms action=c lo=2
gams /tmp/sprint26-pattern-e/catmix_mcp.gms lo=2 > /tmp/catmix_solve.log 2>&1
grep "MODEL STATUS" /tmp/catmix_solve.log
```

**Test Case 2: Read ISSUE_1144 + grep for its fingerprint**

```bash
grep -nE "alias.*domain|inference|mismatch" docs/issues/ISSUE_1144*.md | head -10
# Then grep for the documented buggy emit pattern in current catmix_mcp.gms
```

### Risk if Wrong

- **catmix actually unchanged:** Sprint 26 Priority 3 still has 3 models; estimated 4–6h holds.
- **catmix recovered to mismatch:** #1144 closes; Sprint 26 Priority 3 has 2 models.

### Estimated Research Time

1 hour (within Task 5 — catmix end-to-end pipeline + #1144 fingerprint check)

### Owner

Sprint planning (Task 5)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 5 (Pattern E Carryforward Status Survey)
**Date:** 2026-05-07

**Findings:** **catmix WAS recovered by Sprint 25 #1338.** The original `model_infeasible` (101 INFES equations) reported in #1144 is gone — catmix now translates and compiles cleanly, and solves to Optimal with 0.21% rel_diff (essentially solver-noise level).

**Evidence:**

- `gh pr/issue` cross-reference: Sprint 25 SPRINT_LOG.md Day 11 §"Revised Checkpoint 2 evaluation" attributes catmix's recovery to **#1338** (*"expr_to_gams now handles IndexOffset as a direct index of SetMembershipTest"*). The fix-in-place series targeted catmix/glider/markov/tricp specifically.
- Pipeline status (current main): `nlp2mcp_translate.status = success`; `mcp_solve.status = success`, `model_status = 1 (Optimal)`, `objective_value = -0.048`; `solution_comparison.comparison_status = mismatch` with `relative_difference = 0.00208` (0.21%, within solver tolerance for this scale).
- Original #1144 fingerprint (per `docs/issues/ISSUE_1144_*.md`): "regressed from `model_optimal` to `model_infeasible` due to ... PR #1076 ... `skip_lead_lag_inference=True`". The current emit no longer exhibits this regression — domain inference is correctly applied for ode1/ode2 lead-indexed equations.

**Decision:** Close #1144 during Sprint 26 Day 1 as "infeasibility resolved by S25 #1338 SetMembershipTest fix series". Optional Sprint 27 follow-up if user-side metric tracking cares about the residual 0.21% rel_diff (low priority — informational level).

---

## Unknown 3.3: Is "Phase E" still the right framing for #1141 / #1144 / #1147 post-Sprint-25?

### Priority

**Medium** — Phase E was a Sprint 25 design construct (`DESIGN_ALIAS_AD_ROLLOUT.md` §Phase 4) for "alias-AD bug shapes that don't fit Patterns A/B/C/D". Post Sprint 25, the Pattern A/C/E dichotomy may have changed. If "Phase E" no longer maps cleanly, Sprint 26 should rename or fold these into other categories.

### Assumption

The "Phase E" designation can stay as-is for Sprint 26 Priority 3 — these 3 issues are the residual alias-AD work that doesn't fit the broader Pattern C generalization (Priority 1) or the Pattern A reclassification (Priority 2).

### Research Questions

1. Per the Day 7 cohort sweep, how was each of #1141 / #1144 / #1147 classified?
2. Does any of the 3 issues fit the broader Pattern C shape that Priority 1 will fix?
3. Does any of the 3 issues fit a "Pattern A reclassification" shape that should be folded into Priority 2?

### How to Verify

**Test Case 1: Re-read DAY7_COHORT_SWEEP.md classification**

```bash
grep -nE "1141|1144|1147" docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md | head -20
```

**Test Case 2: Per-issue forward-classification**

For each of #1141, #1144, #1147, decide: (a) fold into Priority 1 (Pattern C generalization), (b) fold into Priority 2 (cohort reclassification), (c) keep as standalone Priority 3 work.

### Risk if Wrong

- **"Phase E" keeps but is stale:** Sprint 26 documentation uses confusing terminology that doesn't match the real bug shapes.
- **Should fold into other priority:** Sprint 26 Priority 3 work redistributes; budget reallocates.

### Estimated Research Time

0.5 hours (within Task 5 — sweep doc re-read + per-issue classification decision)

### Owner

Sprint planning (Task 5)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 5 (Pattern E Carryforward Status Survey)
**Date:** 2026-05-07

**Findings:** "Phase E" framing is **invalid for 2 of 3 models** post-Sprint-25. Only #1141 (kand) is genuinely an alias-AD bug requiring Sprint 26 fix work. The original Phase E grouping was based on bug shapes that have since been reclassified or resolved by Sprint 25 work:

| Model | Original Phase E classification | True bug shape (post-S25) | Phase E framing valid? |
|---|---|---|---|
| kand | Alias-AD gradient (tree structure) | Genuine alias-AD bug — `_alias_match`-related, applies to `flow(n,nn)` arc-set differentiation | ✅ Yes |
| catmix | Alias-AD domain inference | Was a `skip_lead_lag_inference=True` regression from PR #1076 — NOT alias-AD; resolved by S25 #1338 | ❌ No |
| camshape | Alias-AD compilation error | Was a bound-emission `$141` error (lo_map/up_map not emitted) — NOT alias-AD; resolved by #1147 partial fix + #1160 follow-up; current Locally Infeasible is a distinct new bug | ❌ No |

**Evidence:**

- Day 7 cohort sweep (`docs/planning/EPIC_4/SPRINT_25/DAY7_COHORT_SWEEP.md` §"Classification Table") shows the original Phase E grouping was made under the assumption all 3 shared an alias-AD root cause.
- catmix issue doc (`docs/issues/ISSUE_1144_*.md`) §"Root Cause Analysis" identifies the cause as "PR #1076 (Sprint 22 Day 7 WS3, whouse fix) ... `skip_lead_lag_inference=True`" — domain inference, not alias-AD.
- camshape issue doc (`docs/issues/ISSUE_1147_*.md`) §"Fix Applied (Partial)" identifies the cause as "emitter did not emit numeric per-element bounds from `lo_map`/`up_map`" — bound emission, not alias-AD. Subsequent #1160 (CLOSED) addressed the residual pairing error.

**Decision:** Sprint 26 should **retire the "Phase E" label**. Specifically:

- **#1141 (kand):** Reclassify as a standalone alias-AD residual; fold under **Priority 5 (AD residuals)** alongside #1334/#1335. Apply the Day 5 methodology (trace + emitted-artifact + formal-derivative byte comparison) per Sprint 26 Prep Task 3 PR16 process.
- **#1144 (catmix):** Close as resolved (per Unknown 3.2).
- **#1147 (camshape):** Close-and-refile as new Sprint 27 issue (per `PATTERN_E_STATUS.md` §"Issue #1147").

Sprint 26 Priority 3 effective scope: **1 model fix (kand) + 2 closures**. Total effort: ~3–6h (vs original ~6–10h estimate).

---

# Category 4: Translation Timeout — Option 1 Short-Circuit

Priority 4 workstream — Issues #885 (sarf), #931 (iswnm), #932 (nebrazil), #1185 (mexls), #1228 (iswnm second variant); defers #1224 (mine ParamRef IndexOffset).

## Unknown 4.1: Is the Sprint 25 Option 1 short-circuit design still valid post-Sprint-25 #1338..#1341 SetMembershipTest fixes?

### Priority

**Critical** — Sprint 26 Priority 4 budget (4–6h) assumes the Sprint 25 design (`PROFILE_HARD_TIMEOUTS.md`) still applies. If #1338..#1341 (which targeted SetMembershipTest paths) shifted the failure surface, the design needs refresh — and the budget overruns.

### Assumption

The Sprint 25 Option 1 short-circuit design — landing in `src/ad/index_mapping.py::enumerate_equation_instances` (primary) + `resolve_set_members` (same file) + `src/ir/condition_eval.py` (static `SetMembershipTest` failure path) — is still valid. The Sprint 25 #1338..#1341 fixes targeted `expr_to_gams` (a different file path) and `_process_expr_map_bound` (another different path); they did NOT touch the Option 1 patch sites.

### Research Questions

1. Do the Option 1 patch sites still exist in current `src/ad/index_mapping.py` and `src/ir/condition_eval.py` with the expected function signatures?
2. Did Sprint 25 #1338..#1341 modify any code in `src/ad/index_mapping.py` or `src/ir/condition_eval.py`?
3. Does the `enumerate_equation_instances` function still hit the documented Cartesian-explosion fallback for srpchase/iswnm?
4. Are there new code paths (introduced by #1338..#1341 or other Sprint 25 commits) that bypass `enumerate_equation_instances` for the same models?

### How to Verify

**Test Case 1: Patch sites exist**

```bash
grep -nE "def enumerate_equation_instances|def resolve_set_members" src/ad/index_mapping.py
grep -nE "SetMembershipTest" src/ir/condition_eval.py | head -10
```

**Test Case 2: Sprint 25 modification history**

```bash
git log --oneline --diff-filter=M -- src/ad/index_mapping.py src/ir/condition_eval.py | head -10
# Check if any of #1338..#1341 commits show in the history
```

**Test Case 3: srpchase still hits the documented bottleneck**

```bash
# Re-profile srpchase with SIGALRM 900s
mkdir -p /tmp/sprint26-profile
timeout 900 .venv/bin/python -m src.cli data/gamslib/raw/srpchase.gms \
  -o /tmp/sprint26-profile/srpchase_mcp.gms --skip-convexity-check --quiet \
  > /tmp/sprint26-profile/srpchase.log 2>&1
echo "Exit code: $?"
```

Expected: srpchase still completes in ~500s (per Sprint 25 PROFILE_HARD_TIMEOUTS.md).

### Risk if Wrong

- **Patch sites moved:** Task 6 design refresh needed; budget grows from 3–4h to 6–8h.
- **Failure surface shifted:** Option 1 doesn't apply; need a different approach for Priority 4.

### Estimated Research Time

1.5 hours (within Task 6 — patch-site verification + Sprint 25 git log + srpchase re-profile)

### Owner

AD engineer (Task 6)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 6 (Profile Option 1 Short-Circuit Approach)
**Date:** 2026-05-07

**Findings:** Sprint 25 PROFILE_HARD_TIMEOUTS.md Option 1 design is **still valid** post-Sprint-25 #1338..#1341. Patch sites all exist with the same shape on current main:

| Patch site | Sprint 25 line ref | Current main line | Modified during S25? |
|---|---|---|---|
| `src/ad/index_mapping.py::enumerate_equation_instances` | "around line 430" warning emit | line 377 (def), line 452 (warning) | ❌ No (only `resolve_set_members` was touched by #1311) |
| `src/ad/index_mapping.py::resolve_set_members` | lines 177-178, 279 (logger.warning) | lines 188, 198, 294, 301 | ✅ Yes — #1311 added `quiet: bool` kwarg; logger.warning still at lines 188 / 198 / 294 / 301 |
| `src/ir/condition_eval.py` SetMembershipTest evaluation | "around line 417" | line 377 (case), line 417 (raise message) | ❌ No (zero S25 commits to this file) |

Sprint 25 commits to patch-site files: only `src/ad/index_mapping.py` was modified, by `21e1767a` (Fix #1311 — AD subset-membership recognition) + `6273a998` (PR #1310 review). The #1311 fix added the `quiet: bool = False` kwarg to `resolve_set_members` for AD's per-call membership check; it didn't change `enumerate_equation_instances`. The #1338..#1341 fix-in-place series (commit `12548337`) targeted `src/emit/expr_to_gams.py` for IndexOffset-in-SetMembershipTest indices (catmix/glider/markov/tricp), which is unrelated to the Option 1 enumeration path.

Re-profile of srpchase under SIGALRM 900s on current main confirms unchanged bottleneck shape:

```json
{"model": "srpchase", "status": "complete (ad_jacobian)", "total": 846.02,
 "stages": [["preprocess", 0.06], ["parse+ir_build", 2.54], ["normalize", 0.06],
            ["ad_gradient", 0.81], ["ad_jacobian", 842.55]]}
```

ad_jacobian = 99.6% of total time (vs PROFILE_HARD_TIMEOUTS.md's 466s ad_jacobian = 93% of total — same shape; absolute time variance is machine/load-dependent). Same `Dynamic subset 'srn' has no static members; falling back to parent set 'n' (1001 members)` + `Set membership for 'leaf' cannot be evaluated statically` warning signatures emit at the documented locations.

**Evidence:**

- Patch-site grep output (Section 1.1 of `PATTERN_E_STATUS.md`'s sister design doc — `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` §1.1).
- Sprint 25 git log of `src/ad/index_mapping.py` and `src/ir/condition_eval.py` (DESIGN_OPTION_1_SHORT_CIRCUIT.md §1.2).
- `/tmp/sprint26-task6-profile/srpchase.json` — current-main profile result.
- `/tmp/sprint26-task6-profile/srpchase.log` — 18 warning-signature lines on current main vs 23 (8 + 15) in Sprint 25 §2.2; the 5-line reduction is attributable to #1311's `quiet=True` suppression of fallback warnings from AD's `_is_concrete_instance_of` membership check.

**Decision:** Sprint 26 Priority 4 budget (4–6h) holds. Option 1 patch design proceeds as documented in `docs/planning/EPIC_4/SPRINT_26/DESIGN_OPTION_1_SHORT_CIRCUIT.md` §2.

---

## Unknown 4.2: Will the Option 1 short-circuit recover only srpchase, or also unblock 1+ of {iswnm, mexls, nebrazil, sarf}?

### Priority

**High** — Sprint 26 Translate target is ≥ 135/142 (+2 from Sprint 25 final 133). If Option 1 only recovers srpchase (+1), the second translate-recovery must come from elsewhere (e.g., #1224 mine if pulled in). If Option 1 recovers 2+ models, Sprint 26 Translate target is comfortably hit by Priority 4 alone.

### Assumption

Option 1 unblocks srpchase (per Sprint 25 PROFILE_HARD_TIMEOUTS.md "srpchase completes in 500s"). Among {iswnm, mexls, nebrazil, sarf}, at most 1 model is also unblocked — the remaining 3 are too far over the 600s budget to recover even with the short-circuit.

### Research Questions

1. Per Sprint 25 PROFILE_HARD_TIMEOUTS.md, how far over budget are iswnm / mexls / nebrazil / sarf at 900s SIGALRM? (i.e., do they complete in 901s or 1500s+?)
2. Does the short-circuit reduce per-equation-instance work by a constant factor (e.g., 2×) or a variable factor (model-dependent)?
3. For the model with the lowest over-budget margin (smallest 900s overshoot), what's the projected post-short-circuit translate time?

### How to Verify

**Test Case 1: Re-profile {iswnm, mexls, nebrazil, sarf} with extended SIGALRM**

```bash
for m in iswnm mexls nebrazil sarf; do
  timeout 1800 .venv/bin/python -m src.cli data/gamslib/raw/${m}.gms \
    -o /tmp/sprint26-profile/${m}_mcp.gms --skip-convexity-check --quiet \
    > /tmp/sprint26-profile/${m}.log 2>&1
  echo "$m exit code: $?"
done
```

Expected: identify the 1 model (if any) that completes in < 1800s. That's the second-most-likely Option 1 candidate after srpchase.

**Test Case 2: Estimate short-circuit speedup factor**

Per the documented bottleneck shape (`SetMembershipTest` Cartesian explosion), estimate the speedup the short-circuit produces. If the short-circuit eliminates an O(n^k) term (where n is set size and k is equation arity), the speedup may be enormous on smaller models.

### Risk if Wrong

- **Only srpchase recovered:** Sprint 26 Translate target = 134/142 (one short of ≥ 135). Need to pull #1224 or accept missing target.
- **2+ recovered:** Sprint 26 Translate target comfortably met; possibly hit STRETCH ≥ 137/142.

### Estimated Research Time

1 hour (within Task 6 — extended-budget re-profile of 4 models + speedup estimation)

### Owner

AD engineer (Task 6)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 6 (Profile Option 1 Short-Circuit Approach)
**Date:** 2026-05-07

**Findings:** **Projected recovery: +1 to +2 models** (srpchase HIGH confidence; iswnm MEDIUM; sarf/mexls/nebrazil LOW-MEDIUM). Same projection as Sprint 25 PROFILE_HARD_TIMEOUTS.md §4.3 contingency analysis ("0–2 model" gain).

| Model | Sprint 25 status | Sprint 26 (post Option 1) projected | Confidence | Notes |
|---|---|---|---|---|
| srpchase | translate timeout @ 600s pipeline (completes @ 900s in 466–846s) | translate **completes < 30s** | HIGH | 1 dynamic subset (srn → n, 1001 members), 2 affected eqs, well-bounded |
| iswnm | timeout @ 900s | translate likely completes | MEDIUM | 1 dynamic subset (nb), 4 warnings, simpler than srpchase |
| sarf | timeout @ 900s | translate may complete | MEDIUM-LOW | 1 dynamic subset, eq structure heavier than iswnm |
| mexls | timeout @ 900s | translate may partially recover | LOW | 3 dynamic subsets — short-circuit collapses each but residual enumeration may still time out |
| nebrazil | timeout @ 900s | translate may partially recover | LOW | 4 dynamic subsets, 116 fallback warnings — heavy multi-subset Cartesian |

**Evidence:**

- 120s confirmation profiles on the 4 timeout models (`/tmp/sprint26-task6-profile/{iswnm,sarf,mexls,nebrazil}.json` + `.log`) — all 4 timed out, all 4 still inside `ad_jacobian` once they reach it. nebrazil's 188-line warning trail on current main confirms the same multi-subset Cartesian explosion is firing as Sprint 25 reported (50 + 116 = 166 in §2.2 table).
- An extended-budget profile of iswnm under SIGALRM 1800s is running in background (`/tmp/sprint26-task6-profile/iswnm-1800.{json,log}`); per Sprint 25 PROFILE_HARD_TIMEOUTS §1.2 ("> 865s in ad_jacobian"), iswnm was clearly in the asymptotic intractable region at 900s, so 1800s is unlikely to recover it without the architectural fix — extended profile result will inform but not change the fundamental projection.
- Per Sprint 25 retrospective §"Translate-recovery is low-leverage for near-term Match gains" (PR13 finding): translate-recovered models hit downstream emitter / stationarity bugs, so a +1 to +2 Translate gain projects to **0 to +1 Solve gain** in Sprint 26.

**Decision:** Sprint 26 Priority 4 lands Option 1 with realistic projection of +1–2 Translate / 0–+1 Solve. srpchase is the high-confidence target; iswnm is a probable bonus; the 3 multi-subset cases are uncertain. Test fixture plan (DESIGN_OPTION_1_SHORT_CIRCUIT.md §3) ships an integration test for srpchase only; iswnm/sarf/mexls/nebrazil tests deferred until post-implementation profiling shows tractability.

---

## Unknown 4.3: Should #1224 (mine ParamRef IndexOffset) be deferred to a separate effort or bundled with Priority 4?

### Priority

**Medium** — Per Sprint 26 Priority 4 description in PROJECT_PLAN.md: "Defer #1224 (mine ParamRef IndexOffset) to a separate effort — the IndexOffset offset-as-Expr extension is a larger architectural change." Need to confirm the deferral decision is correct given Sprint 26 budget.

### Assumption

#1224 requires a non-trivial IndexOffset architectural extension (allowing the offset to be an Expr, not just an int) that's out of Sprint 26 scope. Defer to Sprint 27 or later.

### Research Questions

1. What's the rough effort estimate for #1224's IndexOffset architectural extension?
2. Are there test fixtures (mine.gms beyond) that would benefit from the extension?
3. Could a narrower mine-specific fix (without the architectural extension) deliver the same Translate +1 in Sprint 26?

### How to Verify

**Test Case 1: Read ISSUE_1224 + estimate effort**

```bash
cat docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md
```

**Test Case 2: Check for mine-only narrow fix**

Inspect mine's source. The `ParamRef(li(k))` offset is on a single equation `pr(k,l+1,i,j)$c(l,i,j)`. A narrow fix could specialize for "ParamRef on the leading index of an equation domain" rather than general "ParamRef as offset in any IndexOffset".

### Risk if Wrong

- **#1224 is actually narrow-scope:** can land in Sprint 26 alongside Option 1; Translate target +1.
- **#1224 is wider than estimated:** even the narrow fix is out of scope; Sprint 26 holds the deferral.

### Estimated Research Time

1 hour (within Task 6 — read ISSUE_1224 + estimate + narrow-fix feasibility check)

### Owner

AD engineer (Task 6)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 6 (Profile Option 1 Short-Circuit Approach)
**Date:** 2026-05-07

**Findings:** **DEFER #1224 to Sprint 27+.** #1224 is an architectural extension (`IndexOffset.offset: Const → Expr`) orthogonal to Option 1's `SetMembershipTest` enumeration fallback fix; bundling them would expand Sprint 26 Priority 4 from ~4–6h to ~10–14h with substantially higher risk surface.

| Aspect | Option 1 (this Sprint 26 Priority 4) | #1224 (Sprint 27+ candidate) |
|---|---|---|
| Touch site | `src/ad/index_mapping.py::enumerate_equation_instances` | `src/ir/ast.py::IndexOffset` (offset field type) + `src/ad/constraint_jacobian.py` (validation) + downstream KKT/emit |
| Bug shape | Cartesian-fallback enumeration (5 affected models) | Parameter-valued offsets (1 affected model: mine) |
| Effort | ~4–6h | 6–10h (narrow path #1: enumerate at IR build) — 12–20h (full path #2: Expr-typed offsets) |
| Risk surface | Narrow (single helper + one new entry-condition predicate) | Broad (IndexOffset is core IR; affects every downstream path) |

Per `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md`:
- mine equation: `pr(k,l+1,i,j)$c(l,i,j).. x(l,i+li(k),j+lj(k)) =g= x(l+1,i,j);`
- `li(k)`/`lj(k)` are 4-element parameters (Set k = `{ne, se, sw, nw}`)
- Three fix paths documented; narrowest (path #1: enumerate at IR build time) is still 6–10h alone

**Evidence:**

- `docs/issues/ISSUE_1224_mine-paramref-index-offset-unsupported.md` §"Potential Fix Approaches" lists three options with effort estimates.
- DESIGN_OPTION_1_SHORT_CIRCUIT.md §5 documents the deferral decision with full rationale.
- Sprint 26 PREP_PLAN.md §Task 6 background already noted: *"#1224 (mine ParamRef IndexOffset) is a separate architectural extension and is NOT bundled with Option 1."* Task 6 verification confirms this stance.

**Decision:** Sprint 26 Priority 4 lands Option 1 alone. File a `sprint-27-candidate` comment on #1224 noting:
- Sprint 26 explicitly considered and deferred per Task 6 design analysis (this entry).
- Recommended Sprint 27 fix path: #1 (enumerate at IR build time) — 6–10h, narrowest scope.
- Alternative path #2 (Expr-typed IndexOffset.offset) would be a multi-sprint architectural change — defer until there's evidence of >1 affected model.

---

## Unknown 4.4: Will the Option 1 short-circuit produce flaky or non-deterministic behavior on edge-case dynamic-subset inputs?

### Priority

**Medium** — The short-circuit returns "include unevaluable instances by default" (per the documented warning text). If the set of "unevaluable instances" depends on dict iteration order or other non-deterministic state, the short-circuit could produce different MCPs across runs, violating PR12 byte-stability guarantees.

### Assumption

The Option 1 short-circuit is deterministic — the set of "unevaluable instances" is fully determined by the AST shape, not by iteration order or set membership timing.

### Research Questions

1. Does `enumerate_equation_instances` use any data structures with iteration-order dependency (sets, dicts pre-Python-3.7)?
2. Does the short-circuit's "include all unevaluable instances by default" decision make use of any global state that could vary across runs?
3. After the short-circuit lands, will the PR12 determinism harness still pass (5 fixtures × 5 seeds byte-equivalent)?

### How to Verify

**Test Case 1: Code-path determinism inspection**

Read `enumerate_equation_instances` and the short-circuit insertion point. Identify any iteration over `dict.items()` / `set` / similar non-deterministic structures.

**Test Case 2: Determinism test post-prototype**

Apply the Option 1 prototype patch. Run the PR12 determinism harness (`tests/integration/test_pipeline_determinism.py`):

```bash
.venv/bin/python -m pytest tests/integration/test_pipeline_determinism.py -v 2>&1 | tail -15
```

Expected: all 6 (or however many) determinism tests pass.

### Risk if Wrong

- **Non-deterministic emit:** PR12 fails on Sprint 26 Day 1; Option 1 needs determinism patches before merge.
- **Determinism guaranteed:** safe to land Option 1 in Sprint 26 without additional plumbing.

### Estimated Research Time

1 hour (within Task 6 — code inspection + determinism test on prototype)

### Owner

AD engineer (Task 6)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 6 (Profile Option 1 Short-Circuit Approach)
**Date:** 2026-05-07

**Findings:** Option 1 short-circuit is **deterministic by construction** — produces identical output across runs/seeds.

**Reasoning (per code inspection of `enumerate_equation_instances` and the proposed short-circuit in DESIGN_OPTION_1_SHORT_CIRCUIT.md §2):**

1. **Detection predicate** (`_is_dynamic_subset_membership_short_circuit`) inspects `model_ir` structure: set name, `set_def.domain`, `set_def.members`. All three are deterministic per Sprint 25 PR12 byte-stable harness.
2. **Placeholder result** is a single-element list `[tuple(eq_domain)]` — no sort, no hash-dependent ordering, no `set` / `frozenset` introduced.
3. **No `dict` iteration** whose order depends on `PYTHONHASHSEED` is added to the new code path.
4. **Downstream emit path** (existing `src/kkt/stationarity.py::_build_indexed_stationarity_expr`, `src/emit/equations.py::emit_equation_definition`) already handles symbolic-index instances deterministically (per Sprint 25 #1306 / #1351 / #1308 prior art on `stat_<eq>(i)..` symbolic equation heads).
5. **Existing fallback path** (lines 437-475 of `enumerate_equation_instances`) is unchanged — short-circuit fires BEFORE the cross-product loop; if predicate returns False, control falls through with no semantic change.

**Evidence:**

- DESIGN_OPTION_1_SHORT_CIRCUIT.md §2.5 explicitly documents the determinism analysis.
- Sprint 25 PR12 byte-stable harness (5 fixtures × 5 seeds) is the post-implementation validation gate — the Sprint 26 Priority 4 PR must run `tests/integration/emit/test_*_byte_stable.py` and pass.
- The new helper functions (`_is_dynamic_subset_membership_short_circuit`, `_build_symbolic_instance_placeholder` per DESIGN doc §2.3) introduce no `set` / `dict` / hash-order dependent constructs.

**Decision:** Determinism is preserved by construction. Sprint 26 Priority 4 PR includes a determinism unit test (DESIGN_OPTION_1_SHORT_CIRCUIT.md §3.1 Test 6: run with `PYTHONHASHSEED=0` and `PYTHONHASHSEED=42`, assert identical output) plus the existing PR12 byte-stable integration suite as the regression gate.

---

# Category 5: AD Residuals (#1334, #1335)

Priority 5 workstream — both target the `_replace_indices_in_expr` + `_add_jacobian_transpose_terms_scalar` pair in `src/kkt/stationarity.py`. Confirmed on otpop.

## Unknown 5.1: Are the file:line references in ISSUE_1334.md / ISSUE_1335.md still accurate after the Sprint 25 fix-in-place series touched stationarity.py?

### Priority

**High** — Sprint 25 #1350 (srkandw `tn(t,t)` self-alias) modified `_remap_condition_to_domain` in `src/kkt/stationarity.py`; Sprint 25 #1351 (launch Pattern C rollback) also modified the file. Stale file:line references means Sprint 26 work starts with broken pointers.

### Assumption

The file:line references in ISSUE_1334 (`src/kkt/stationarity.py:5279–5310` for `_add_jacobian_transpose_terms_scalar`; `:2295–2479` for `_replace_indices_in_expr`) are within ±20 lines of accuracy post Sprint 25 fix-in-place series — close enough that the function names alone identify the targets.

### Research Questions

1. Do the function definitions (`def _add_jacobian_transpose_terms_scalar`, `def _replace_indices_in_expr`) still exist in `src/kkt/stationarity.py`?
2. What are the current line numbers?
3. Are the function bodies semantically the same as documented in ISSUE_1334.md, or did Sprint 25 modify the internals?

### How to Verify

```bash
grep -nE "^def _add_jacobian_transpose_terms_scalar|^def _replace_indices_in_expr|^def _remap_condition_to_domain" \
  src/kkt/stationarity.py
# Compare to ISSUE_1334.md / ISSUE_1335.md documented line numbers
```

### Risk if Wrong

- **References stale by >20 lines:** Sprint 26 Priority 5 work starts with confusion; need to refresh ISSUE_1334.md / ISSUE_1335.md before fix work begins.
- **Function bodies modified:** Sprint 25 changes may have affected the documented bug shape; need to re-confirm reproducer (Unknown 5.2).

### Estimated Research Time

0.5 hours (within Task 7 — grep + line-number cross-reference)

### Owner

AD/KKT engineer (Task 7)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 7 (AD Residuals Investigation Recap)
**Date:** 2026-05-07

**Findings:**

| Doc | File:line references at filing | Current main | Status | Action taken |
|---|---|---|---|---|
| ISSUE_1334.md | `src/kkt/stationarity.py:5279–5310` (_add_jacobian_transpose_terms_scalar), `:2295–2479` (_replace_indices_in_expr) | line 5421 (def), line 2330 (def) | **STALE** (drift +142 / +35 lines) | **Synced 2026-05-07** in this PR — 3 references updated with explicit "was X; resynced 2026-05-07" notes |
| ISSUE_1335.md | `src/ad/constraint_jacobian.py:133–202` (_try_eval_offset), `:204–260` (_resolve_idx), `derivative_rules.py:1847+` (_diff_sum) | lines 133, 204, 1847 (all defs) | **ACCURATE** (all match exactly) | No changes needed |

**Sprint 25 modifications to fix-site files:**
- `src/kkt/stationarity.py` (7 commits between 2026-04-15 and 2026-05-06): #1351 launch Pattern C rollback, #1350 srkandw, #1278 alias-position ord, #1192 bounds-aware conditional, #1306 Pattern C prototype + PR reviews. None directly modified `_replace_indices_in_expr` or `_add_jacobian_transpose_terms_scalar` — line drift is from surrounding code growth.
- `src/ad/constraint_jacobian.py` (1 commit): #1348 / #1349 china + pindyck. Did not touch `_try_eval_offset` or `_resolve_idx`.
- `src/ad/derivative_rules.py` (multiple commits): #1311, #1312, #1330, several PR reviews. Did not touch `_diff_sum`.

**Evidence:**

- `grep -nE "^def _add_jacobian_transpose_terms_scalar|^def _replace_indices_in_expr" src/kkt/stationarity.py` returns lines 2330, 5421.
- `grep -nE "^def _try_eval_offset|^def _resolve_idx" src/ad/constraint_jacobian.py` returns lines 133, 204.
- `grep -nE "^def _diff_sum" src/ad/derivative_rules.py` returns line 1847.
- `git log --pretty="format:%h %s" --diff-filter=AM --since="2026-04-15" --until="2026-05-06" -- <file>` for each file (see AD_RESIDUALS_RECAP.md §1.1, §1.2).

**Decision:** ISSUE_1334.md file:line references resynced in this PR (commit ahead). ISSUE_1335.md needs no changes. Sprint 26 Priority 5 work begins with accurate pointers.

---

## Unknown 5.2: Does the otpop NLP-warm-started reproducer still produce the documented `LHS = -1.4157` residual on `stat_cd(ag-subsist)`?

### Priority

**High** — ISSUE_1334.md documents the otpop reproducer with specific residual values. If Sprint 25 changes shifted those values (or fixed the bug as a side-effect), Sprint 26 Priority 5 work starts with stale baselines.

### Assumption

Running otpop translate + NLP solve + dual transfer + MCP iterlim=0 still produces `stat_cd(ag-subsist)` LHS ≈ -1.4157 (per ISSUE_1334.md §Diagnostic). Sprint 25 changes did NOT inadvertently fix #1334 or shift its residual.

### Research Questions

1. Does the otpop translate currently succeed?
2. Does the otpop NLP solve under `gams otpop.gms`?
3. What are the per-equation residuals at the NLP-warm-start (specifically `stat_cd(ag-subsist)`, `stat_x('1990')`, `stat_p('1986')`)?
4. Are the residuals materially different from the documented values?

### How to Verify

```bash
mkdir -p /tmp/sprint26-otpop
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
  -o /tmp/sprint26-otpop/otpop_mcp.gms --skip-convexity-check --quiet
# Apply the manual NLP solve + dual transfer + MCP iterlim=0 steps from ISSUE_1334.md §Diagnostic
# (typically requires a custom script; document the procedure in AD_RESIDUALS_RECAP.md)
```

### Risk if Wrong

- **Residuals shifted:** Sprint 26 fix needs new acceptance criteria; ISSUE docs need refresh.
- **Bug fixed inadvertently:** #1334 closes during prep; Sprint 26 Priority 5 budget shrinks 8–14h to 4–8h.

### Estimated Research Time

1.5 hours (within Task 7 — otpop reproducer rerun + residual measurement)

### Owner

AD/KKT engineer (Task 7)

### Verification Results

✅ **Status:** VERIFIED — STATIC FINGERPRINT ONLY (full numerical reproducer DEFERRED to Sprint 26 Priority 5 fix work)
**Verified by:** Task 7 (AD Residuals Investigation Recap)
**Date:** 2026-05-07

**Scope of verification (important — read before relying on this entry):**

The unknown as originally phrased asks whether the **full NLP-warm-started reproducer still produces `LHS = -1.4157` on `stat_cd(ag-subsist)` plus the documented residuals on `stat_x('1990')` / `stat_p('1986')`**. Task 7 did **NOT** run the full reproducer (NLP solve + dual transfer + MCP iterlim=0 + per-equation residual capture is a ~30+ minute end-to-end exercise requiring custom GAMS scripts that are out of scope for a 2–3 hour prep task).

What Task 7 **DID** verify is the **static-emit fingerprint** — the presence of the `sum(t__, ...)` spurious-Sum pattern documented in ISSUE_1334.md §"Buggy Emit" — in current main's otpop emit. The static fingerprint is a **sufficient indicator** that the bug is still present (if the wrong-shape emit is generated, the wrong-residual numerics necessarily follow), but it is **NOT a substitute for the numerical residual measurement** that Sprint 26 Priority 5 fix work should perform as the pre/post acceptance gate.

The original numerical baselines (per ISSUE_1334.md §Diagnostic) — `stat_cd(ag-subsist)` LHS = -1.4157, `Inf-Norm of Minimum Map` 2.35e+02 on `stat_p('1986')` — remain the documented Sprint 26 acceptance targets. Sprint 26 Priority 5 fix work owns re-measuring them.

**Findings (static fingerprint check):** **#1334 bug pattern is STILL VISIBLE in otpop's emit on current main** despite #1334 being CLOSED on GitHub (closed 2026-05-05). otpop's `stat_p(tt)` and `stat_x(tt)` both contain the spurious `sum(t__, ...)` wrap on `nu_kdef` that ISSUE_1334.md §"Buggy Emit" documents:

```
stat_p(tt).. ... + sum(t__, ((-1) * (del(t__) * x(tt) * 0.365 * (1 - c))) * nu_kdef)$(t(tt)) - piL_p(tt) =E= 0;
stat_x(tt).. ... + sum(t__, ((-1) * (del(t__) * 0.365 * (1 - c) * p(tt))) * nu_kdef)$(t(tt)) + ... =E= 0;
```

This means the GitHub closure (2026-05-05) likely addressed a sibling sub-shape but did NOT fix the otpop-specific case. **Sprint 26 Priority 5 must re-investigate the closure** and either re-open #1334 or file a successor issue capturing the still-extant otpop emit pattern.

**Evidence:**

- `grep -E "sum\(t__" /tmp/sprint26-task7/otpop_mcp.gms` returns 2 matches (in `stat_p` and `stat_x`).
- AD_RESIDUALS_RECAP.md §2.2 documents the exact lines.
- `gh issue view 1334 --json state` returns `"state":"CLOSED", "closedAt":"2026-05-05T19:27:18Z"` — the closure is real but the bug pattern persists.

**Decision:** Sprint 26 Priority 5 Day 1: open the GitHub issue tracker and either:
- Re-open #1334 with a comment explaining "post-closure verification confirms the otpop spurious-sum pattern is still present in current main emit", linking AD_RESIDUALS_RECAP.md §2.2.
- OR file a successor issue (e.g., "#1XXX: residual otpop spurious `sum(t__, ...)` after #1334 closure — fix-in-place series didn't fully resolve") with cross-references.
Add ~2h to the Priority 5 budget for this re-investigation step.

---

## Unknown 5.3: Does fixing #1334 actually subsume #1357 (otpop `$171` from Sprint 25 Day 13), or are they independent bugs?

### Priority

**Critical** — Sprint 25 #1357 is documented as "likely subsumed by #1334" in its issue body. Sprint 26 needs to confirm this for two reasons: (a) bucket-provenance baseline accounting (Task 9) — does otpop's path_syntax_error count attribute to Priority 1 (Pattern C) or Priority 5 (#1334)?; (b) Match-gain projection — if #1334 alone fixes otpop (#1357), Pattern C generalization doesn't need to target otpop.

### Assumption

#1334 (spurious `Sum(("t__",), ...)` wrap on subset-domain ParamRef) IS the root cause of #1357 (otpop `$171` domain violations from Day 13 carryforward). Fixing #1334 closes #1357 with no separate work needed.

### Research Questions

1. Does the otpop emit's `$171` violation lines (217, 247) actually contain the `sum(t__, ...)` pattern documented in ISSUE_1334.md §"Buggy Emit (otpop)"?
2. If yes, the subsumption claim is confirmed. If no, #1357 is independent and needs its own fix work.
3. What's the current Sprint 26 in-scope set's `path_syntax_error` count after subsumption (12 minus how many other bucket transitions)?

### How to Verify

```bash
.venv/bin/python -m src.cli data/gamslib/raw/otpop.gms \
  -o /tmp/sprint26-otpop/otpop_mcp.gms --skip-convexity-check --quiet
sed -n '210,250p' /tmp/sprint26-otpop/otpop_mcp.gms | grep -E "sum\(t__|sum\(t,"
```

Expected if subsumption holds: lines 217 / 247 reference the `sum(t__, ...)` pattern from ISSUE_1334.

### Risk if Wrong

- **Subsumption fails:** Sprint 26 needs separate fix for #1357; Priority 1 Pattern C target list shrinks but Priority 5 budget grows.
- **Subsumption confirmed:** Pattern C target list includes camcge/cesam2/fawley (3 models, not 4); Match-gain projection adjusts.

### Estimated Research Time

1 hour (within Task 7 — otpop emit grep + ISSUE_1334 fingerprint comparison)

### Owner

AD/KKT engineer (Task 7)

### Verification Results

✅ **Status:** VERIFIED (with correction to assumption)
**Verified by:** Task 7 (AD Residuals Investigation Recap)
**Date:** 2026-05-07

**Findings:** **#1334 does NOT subsume #1357.** They are independent bugs in different code paths with different bug shapes.

| Bug | Code path | Bug shape | Manifestation |
|---|---|---|---|
| #1334 | `src/kkt/stationarity.py::_add_jacobian_transpose_terms_scalar` (line 5421) + `_replace_indices_in_expr` (line 2330) | Spurious `Sum(("t__",), ...)` wrap on Jacobian-transpose cross-term when ParamRef domain is a strict subset of equation domain | Numerical: KKT point differs from NLP optimum (otpop solves to `pi=2307.07` vs NLP `pi=4217.80`). Visible in stat_p / stat_x emit as `sum(t__, ...) * nu_kdef`. |
| #1357 | `src/kkt/complementarity.py` + `src/emit/emit_gams.py` (bound-fixup emission) | Subset/superset domain widening in `comp_up_<var>` and `piU_<var>.fx` references — `xb(tt)` referenced where `xb` is on subset `t` and `tt` is superset | Compile-time: GAMS `$171` "Domain violation for set" at lst lines 220, 252 in otpop_mcp.gms (corresponding to source lines 217, 247 — `comp_up_x(tt)$(t(tt) and xb(tt) < inf)..` and `piU_x.fx(tt)$(not (t(tt) and xb(tt) < inf)) = 0;`). Same shape as fawley #1356. |

The ISSUE_1357.md note "likely subsumed by #1334" was a working hypothesis filed Sprint 25 Day 13 but is **DISPROVED by Task 3 + Task 4 + Task 7 evidence**:
- Task 3 PATTERN_C_HYPOTHESIS_VALIDATION §2.4 first observed that otpop's `$171` is in comp_up_x, not in stationarity.
- Task 4 PATTERN_A_RECLASSIFICATION_PLAN identified the same comp_up subset/superset shape on fawley #1356.
- Task 7 (this) confirms the patterns differ: otpop's `$171` errors trace to lst lines 220/252 (comp_up + piU.fx), but ISSUE_1334's spurious `sum(t__, ...)` pattern is in stat_p and stat_x — different lines, different code paths.

**Evidence:**

- `/tmp/sprint26-task7/otpop_compile.lst` line 220-221: `$171 $171` markers point at line 217 of otpop_mcp.gms which reads `comp_up_x(tt)$(t(tt) and xb(tt) < inf).. xb(tt) - x(tt) =G= 0;`. The marker columns hit the `xb(tt)` references.
- `/tmp/sprint26-task7/otpop_compile.lst` line 253-254: `$171` marker points at line 247 reading `piU_x.fx(tt)$(not (t(tt) and xb(tt) < inf)) = 0;`. Same `xb(tt)` shape.
- ISSUE_1334.md §"Buggy Emit (otpop)" documents the `sum(t__, ...)` pattern in `stat_p` / `stat_x` — different code path entirely from comp_up_x and piU.fx.
- ISSUE_1357.md fix-site listing: `src/kkt/stationarity.py:2295–2479` and `:5279–5310` (note: those are the #1334 fix sites — ISSUE_1357 was filed under the "likely subsumed by #1334" hypothesis). Per Task 7 finding, the actual fix sites for #1357 are `src/kkt/complementarity.py` + `src/emit/emit_gams.py`.

**Decision:** Sprint 26 Priority 5 scope decision (per AD_RESIDUALS_RECAP.md §4):
- #1334 (re-investigate + fix the still-visible spurious-sum pattern): 4–10h
- #1335 (narrow AD fix): 4–8h
- #1357 (independent comp_up subset/superset fix, same shape as fawley #1356): **DEFER to Sprint 27** alongside fawley as a "comp_up subset/superset domain widening" workstream (matches Task 4 PATTERN_A_RECLASSIFICATION_PLAN.md §"Issue #1145" close-and-refile pattern).

Sprint 26 Priority 5 lands #1334 + #1335. Re-estimated combined effort: **~8–18h** (low end 8h fits the 8–14h budget cleanly; high end 18h exceeds by 4h, primarily due to the #1334 closure re-investigation overhead). Schedule risk noted for Sprint 26 Day 0 review. otpop's `$141` cascade resolves when #1334 + #1335 land; otpop's `$171` resolves separately in Sprint 27 alongside fawley #1356.

---

## Unknown 5.4: Is #1335 a tractable Sprint-26-level fix or does it require larger architectural change?

### Priority

**Medium** — ISSUE_1335 documents "Missing dzdef/dp cross-term in stat_p when zdef references p via time-reversal-indexed offset" — sounds narrow but may have wide blast radius if it touches the same `_replace_indices_in_expr` machinery as #1334.

### Assumption

#1335 is a narrow fix at the same `_add_jacobian_transpose_terms_scalar` site as #1334, and can land in 4–8h of Sprint 26 effort (per the combined #1334 + #1335 estimate of 8–14h).

### Research Questions

1. Per ISSUE_1335.md, what's the specific code path that produces the missing cross-term?
2. Is it the same function as #1334, or an adjacent function?
3. Does fixing #1335 require any IR-level changes (vs. KKT-assembly changes only)?
4. Does the fix apply only to time-reversal-indexed offsets (otpop-specific) or to all reversal-indexed offsets generally?

### How to Verify

```bash
cat docs/issues/ISSUE_1335_ad-missing-zdef-cross-term-time-reversal-index.md | head -60
```

### Risk if Wrong

- **#1335 is wider than #1334:** Sprint 26 Priority 5 budget needs to expand from 8–14h to 12–20h.
- **#1335 narrow:** combined #1334 + #1335 fits in 8h; possibly leaves room for #1224 (mine) bundling.

### Estimated Research Time

1 hour (within Task 7 — read ISSUE_1335 + identify code path + estimate)

### Owner

AD/KKT engineer (Task 7)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 7 (AD Residuals Investigation Recap)
**Date:** 2026-05-07

**Findings:** **#1335 is a narrow Sprint-26-level fix.** Per Task 7 source inspection (refining ISSUE_1335.md §"Where to Look"), the actual fix site is the `if eq_domain:` gate at `src/ad/constraint_jacobian.py:986` (and the inequality counterpart at `:1107`) that **skips the offset-resolution / sum-expansion pipeline for scalar equations**. The `_resolve_index_offsets` (line 88) and `_expand_sums_with_unresolved_offsets` (line 327) calls are gated behind `if eq_domain:` — for `zdef` (scalar, `eq_domain == ()`), they never run. **No architectural change required**.

The fix shape (refined from ISSUE_1335.md §"Root Cause (suspected)"): the per-instance substitution path (`_expand_sum_body` at line 484 substitutes `t → t'` and then calls `_resolve_index_offsets`, which evaluates `ord('1990')` correctly) **already works for indexed equations**. What's missing is invoking that pipeline for scalar equations whose body contains sums with offset arithmetic. The fix should EITHER (a) extend the gate to fire for scalar equations with sum-internal offset arithmetic, OR (b) hoist the sum-internal offset resolution earlier in the differentiation pipeline so it runs regardless of `eq_domain` shape. ISSUE_1335.md's original framing ("substitute `t → t'` BEFORE `_try_eval_offset`") was correct in spirit but misattributed the gap — the substitution code path exists and works; it's just not invoked for scalar equations.

**Evidence:**

- `grep -nE "^def _try_eval_offset|^def _resolve_idx" src/ad/constraint_jacobian.py` returns lines 133, 204 — matches ISSUE_1335.md exactly.
- `grep -nE "^def _diff_sum" src/ad/derivative_rules.py` returns line 1847 — matches.
- otpop emit on current main: `stat_p(tt)..` has NO `nu_zdef` term (verified via `grep -nE "nu_zdef" /tmp/sprint26-task7/otpop_mcp.gms`). The `nu_zdef` references that exist (line 91 declaration, line 209 stat_x cross-term, line 210 stat_z, line 298 pairing) confirm the bug is specifically the missing `(zdef, p('1990'))` Jacobian entry — exactly what ISSUE_1335 documents.
- Fix is local to AD/constraint_jacobian — no IR-level changes, no KKT-assembly changes, no emit-side changes.

**Decision:** Sprint 26 Priority 5 lands #1335 in 4–8h per ISSUE_1335.md estimate. Combined with #1334 fix, otpop's NLP-warm-started MCP should converge to `pi ≈ 4217.80` (per ISSUE_1335.md §Tests). #1335 is also the ONLY known model affected — no broader corpus impact projected.

---

# Category 6: Cross-Cutting & Process Recommendations

Process recommendations from Sprint 25 retrospective: PR16 (already applied via Task 3), PR17 (bucket provenance baseline), PR18 (scope-shifted model identification), PR19 (pre-merge solve-time validation CI), PR14 reaffirmation (read-the-MCP rule).

## Unknown 6.1: Will the PR19 pre-merge solve-time validation CI extension produce flaky failures on Tier 0/1 canaries (PATH solve under tight budget)?

### Priority

**High** — If PR19 is flaky, Sprint 26 PRs spend disproportionate time waiting for re-runs and reviewers lose confidence in the new CI signal. Need to budget the PATH-solve timeout generously enough to avoid flakes while still catching real regressions.

### Assumption

A 30-second PATH-solve budget per model is sufficient for the 11 Tier 0/1 canaries. The current canary models all solve in <10s on the Sprint 25 reference machine; the 30s budget provides 3× margin for CI machine variance.

### Research Questions

1. What's the current PATH-solve time for each Tier 0/1 canary on the local dev machine?
2. What's the typical CI machine slowdown factor vs local dev (per other slow-test data)?
3. Are any of the 11 canaries close to a 30s threshold even with the 3× margin?
4. Should the budget be configurable per model (some need 60s+) or a flat 30s?

### How to Verify

```bash
# Time each canary's PATH solve locally
for m in dispatch quocge partssupply prolog sparta gussrisk ps2_f ps3_f ship splcge paklive; do
  t0=$(date +%s)
  gams data/gamslib/mcp/${m}_mcp.gms lo=0 > /dev/null 2>&1
  echo "$m: $(($(date +%s) - t0))s"
done
```

### Risk if Wrong

- **30s too tight:** PR19 produces flaky failures; reviewers ignore the signal; bug surface remains uncaught.
- **30s too loose:** PR latency grows; reviewers complain about CI time.

### Estimated Research Time

1 hour (within Task 8 — local timing + CI slowdown estimate)

### Owner

CI engineer (Task 8)

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.2: What's the right target list for PR19 — just the 4 Pattern C target models, all 11 Tier 0/1 canaries, or some subset?

### Priority

**High** — The PR19 design needs an explicit target list. Too narrow misses regressions (e.g., emit change breaks a canary that's not in the list); too broad inflates PR latency.

### Assumption

The PR19 target list should include: (a) the 4 Pattern C target models (camcge, cesam2, fawley, otpop) — for soft-fail informational signal during Sprint 26; (b) 3+ Tier 0 canaries (dispatch, quocge, partssupply) — for hard-fail regression detection. Total: 7 models × 30s = ~3.5min CI overhead, which is acceptable.

### Research Questions

1. How many CI minutes does the existing `make test` consume? Is +3.5min material?
2. Should the soft-fail / hard-fail distinction be configurable in `.github/path-solve-ci-targets.txt`?
3. Are there any non-canary in-scope models that have caught emit regressions historically? (Suggests they should be in the PR19 target list.)
4. Should the target list expand to all 11 Tier 0/1 canaries for safety, or can we trust 3 to catch most regressions?

### How to Verify

**Test Case 1: Survey existing CI duration**

```bash
# From recent CI logs, find the total runtime of the test workflow
gh run list --workflow CI --limit 5 --json conclusion,createdAt,updatedAt | python3 -c "
import json, sys
runs = json.load(sys.stdin)
for r in runs:
    print(r['createdAt'], r['updatedAt'], r['conclusion'])
"
```

**Test Case 2: Historical canary-catch analysis**

Survey the last ~10 PRs that touched `src/emit/*.py` or `src/kkt/stationarity.py`. For each, check if the PR review comments or CI failures referenced any non-canary model emit changes.

### Risk if Wrong

- **Target list too narrow:** Sprint 26 emit regressions on non-target models slip through; user-visible bugs.
- **Target list too broad:** PR latency inflates; CI cost grows; reviewer fatigue.

### Estimated Research Time

1 hour (within Task 8 — CI duration survey + historical PR analysis)

### Owner

CI engineer (Task 8)

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.3: Will adding bucket-provenance to BASELINE_METRICS.md confuse readers who expect aggregate counts only?

### Priority

**Low** — Documentation usability concern. Worth knowing but doesn't drive Sprint 26 scope.

### Assumption

Adding a per-failing-model "Sprint 25 bucket → Sprint 26 bucket" provenance column to `BASELINE_METRICS.md` clarifies metric attribution without obscuring the aggregate counts (which remain in the main metrics table at the top of the doc).

### Research Questions

1. Is the bucket-provenance column added as a separate sub-section (preserving the aggregate-counts top section) or interleaved?
2. Are there other docs (CHANGELOG, PROJECT_PLAN, README) that reference BASELINE_METRICS aggregate counts and would be affected by reformatting?

### How to Verify

Mock up the new BASELINE_METRICS.md format with the bucket-provenance column. Get reader feedback on clarity.

### Risk if Wrong

- **Confusing format:** future contributors mis-read metrics; no operational impact.

### Estimated Research Time

0.5 hours (within Task 9 — format mockup + skim review)

### Owner

Sprint planning (Task 9)

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.4: Does the PR14 emit-PR `.gms` artifact rule need an exception for refactor-only PRs that pass byte-diff verification?

### Priority

**Medium** — Sprint 25 PR #1353 (#1271 dispatcher refactor) was byte-diff verified across 141 models — that diff is "zero" by design. If the PR14 rule says "include one regenerated `.gms` artifact in the diff", refactor-only PRs would either violate the rule or include a redundant `.gms` artifact. Need an explicit exception.

### Assumption

Adding a `byte-stable-refactor` PR label + a PR-description requirement (document the byte-diff verification command and result) is sufficient to grant the exception without weakening the rule's enforcement.

### Research Questions

1. How many Sprint 24/25 PRs would have qualified for the `byte-stable-refactor` exception?
2. Is the exception self-policing (reviewers check the label + description) or enforced by CI?
3. Does the exception apply only to `src/emit/` PRs or also to `src/kkt/stationarity.py` PRs?

### How to Verify

Survey Sprint 24/25 PR titles for refactor-only candidates (`refactor:`, `Dispatcher`, `unify`, `consolidate` keywords). Count: how many would have used the exception?

### Risk if Wrong

- **No exception:** refactor-only PRs include redundant `.gms` artifacts; PR diffs grow unnecessarily.
- **Exception too permissive:** non-refactor PRs use the label to skip the artifact requirement; PR14 enforcement weakens.

### Estimated Research Time

0.5 hours (within Task 10 — Sprint 24/25 PR title survey)

### Owner

Sprint planning (Task 10)

### Verification Results

🔍 **Status:** INCOMPLETE

---

## Unknown 6.5: Will the Sprint 25 1-model scope shift (143 → 142) reverse during Sprint 26?

### Priority

**Low** — The shifted model is currently undocumented (Task 2 PR18 work). If it reverses during Sprint 26 (e.g., a dependency-of-convexity-detection fix lands), the Sprint 26 final retest's in-scope count returns to 143; bucket-provenance baseline (Task 9) needs to handle the count change.

### Assumption

The Sprint 25 scope shift was triggered by a one-way change (e.g., a model became permanently classified as non-convex). It will NOT reverse during Sprint 26 unless explicitly addressed.

### Research Questions

1. Per Task 2's findings, what triggered the Sprint 25 scope shift?
2. Is the trigger reversible (e.g., a code-change affecting convexity detection that could be reverted)?
3. If reversible, is reverting the scope shift in scope for Sprint 26?

### How to Verify

Depends on Task 2 outcome. If Task 2 finds the shift was triggered by `src/`-level code, this unknown asks whether reverting that code is in scope for Sprint 26.

### Risk if Wrong

- **Scope reverses:** Sprint 26 final retest reports 143 in-scope; baseline accounting needs adjustment.
- **Scope stable:** no impact.

### Estimated Research Time

0.5 hours (within Task 9 — depends on Task 2's findings)

### Owner

Sprint planning (Tasks 2 + 9)

### Verification Results

✅ **Status:** VERIFIED
**Verified by:** Task 2 (Identify Sprint 25 Scope-Shifted Model PR18)
**Date:** 2026-05-07

**Findings:**

- Shifted model: **`abel`**
- Prior `convexity.status`: `likely_convex` (Sprint 25 Day 0 baseline)
- New `convexity.status`: `non_convex` (Sprint 25 Day 4, 2026-04-25)
- Triggering commit: `c922bb2d` — *"Mark abel non-convex in gamslib_status.json + file #1313 for warm-start fix"*
- Tracking issue: [#1313](https://github.com/jeffreyhorn/nlp2mcp/issues/1313) — CLOSED during Sprint 25
- Discovery context: `docs/planning/EPIC_4/SPRINT_25/DAY8_QABEL_ABEL_REASSESSMENT.md` (Day 8 qabel/abel PATH-solve reassessment surfaced the indefinite-eigenvalue lambda matrix)
- Reversibility during Sprint 26: **NO** — the reclassification reflects a fundamental property of the abel model (indefinite lambda matrix `lambda(money, gov-expend) = 0.444`; symmetric-part eigenvalues approximately `[-0.047, 1.047]`). #1313 closed during Sprint 25 didn't restore convexity (it documented that the warm-start path doesn't apply).

**Evidence:**

- Diff command: `git show d8574a7d:data/gamslib/gamslib_status.json` vs `git show 58bcbdc1:data/gamslib/gamslib_status.json` filtered on `convexity.status` per model — exactly 1 model differs (`abel`).
- Triggering-commit log: `git log -1 --format=full c922bb2d` documents the indefinite-eigenvalue diagnosis + multi-start NLP confirmation + Sprint 25 Day 8 verification path.
- abel joins the existing 7 `non_convex` models (`ps10_s, ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp`) under the same handling (kept in comparison set, `solution_comparison.comparison_status` remains `mismatch`, informational).

**Decision:**

- Sprint 26 baseline (Task 9) freezes scope at **142** in-scope, matching the Sprint 25 Day 14 final.
- The 143 → 142 transition is one-way and documented in `docs/planning/EPIC_4/SPRINT_25/BASELINE_METRICS.md` §5.1 "Sprint 25 Mid-Sprint Reclassification" (added by Task 2).
- No further scope-shifts anticipated barring discovery of additional non-convex models. Sprint 26 baseline accounting uses 142 throughout.

---

## Newly Discovered Unknowns

_Add unknowns discovered during Sprint 26 execution here, then categorize post-sprint._

---

## Template for Adding New Unknowns During Sprint

```markdown
## Unknown X.Y: [Question/Assumption]

### Priority
**[Critical/High/Medium/Low]** - [One-line impact]

### Assumption
[State the assumption being made]

### Research Questions
1. [Question 1]
2. [Question 2]
...

### How to Verify
[Test cases, experiments, analysis to validate assumption]

### Risk if Wrong
[Impact if assumption is incorrect]

### Estimated Research Time
[Hours] ([brief description of research activities])

### Owner
[Team/Person responsible]

### Verification Results
🔍 **Status:** INCOMPLETE
```

---

## Next Steps

**Before Sprint 26 Day 1:**

1. **Prep Task 2 (Identify Sprint 25 Scope-Shifted Model PR18)** — verifies Unknowns 6.5
2. **Prep Task 3 (Pattern C Hypothesis Validation PR16)** — verifies Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
3. **Prep Task 4 (Pattern A Cohort Reclassification Pre-Work)** — verifies Unknowns 2.1, 2.2, 2.3, 2.4
4. **Prep Task 5 (Pattern E Carryforward Status Survey)** — verifies Unknowns 3.1, 3.2, 3.3
5. **Prep Task 6 (Profile Option 1 Short-Circuit Approach)** — verifies Unknowns 4.1, 4.2, 4.3, 4.4
6. **Prep Task 7 (AD Residuals Investigation Recap)** — verifies Unknowns 5.1, 5.2, 5.3, 5.4
7. **Prep Task 8 (Design Pre-Merge Solve-Time Validation CI PR19)** — verifies Unknowns 6.1, 6.2
8. **Prep Task 9 (Bucket-Provenance Baseline + Scope Freeze PR17 + PR15)** — verifies Unknowns 6.3, 6.5 (jointly with Task 2)
9. **Prep Task 10 (Update CONTRIBUTING.md for Emit-PR `.gms` Diffs PR14)** — verifies Unknown 6.4
10. **Prep Task 11 (Plan Sprint 26 Detailed Schedule)** — integrates all verified unknowns

During Sprint 26 execution:

- Daily standup review of 🔍 INCOMPLETE unknowns
- Update status as findings emerge
- Add Newly Discovered Unknowns when surfaced
- Cross-reference with Sprint 26 retrospective

---

## Appendix: Task-to-Unknown Mapping

This table shows which Sprint 26 prep tasks verify which unknowns. Prep Task 11 (Plan Sprint 26 Detailed Schedule) integrates all verified unknowns into the 14-day execution schedule.

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| Task 2: Identify Sprint 25 Scope-Shifted Model (PR18) | 6.5 | Identifies the model + reason; Task 9 documents in BASELINE_METRICS.md §5 |
| Task 3: Pattern C Hypothesis Validation (PR16) | 1.1, 1.2, 1.3, 1.4, 1.5, 1.6 | Day 5 methodology applied to 3 target models; produces PROCEED/REPLAN signal for Sprint 26 Priority 1 |
| Task 4: Pattern A Cohort Reclassification Pre-Work | 2.1, 2.2, 2.3, 2.4 | Per-issue action plan for 6 cohort issues; test xfail scan |
| Task 5: Pattern E Carryforward Status Survey | 3.1, 3.2, 3.3 | Re-verify 3 Phase E models under post-Sprint-25 emit pipeline |
| Task 6: Profile Option 1 Short-Circuit Approach | 4.1, 4.2, 4.3, 4.4 | Verify Sprint 25 PROFILE_HARD_TIMEOUTS.md design + impact projection + #1224 deferral decision + determinism |
| Task 7: AD Residuals (#1334, #1335) Investigation Recap | 5.1, 5.2, 5.3, 5.4 | File:line currency + reproducer + #1334 ↔ #1357 subsumption + #1335 tractability |
| Task 8: Design Pre-Merge Solve-Time Validation CI (PR19) | 6.1, 6.2 | Flakiness risk + target list selection |
| Task 9: Bucket-Provenance Baseline + Scope Freeze (PR17 + PR15) | 6.3, 6.5 (with Task 2) | Format usability + scope-shift policy decision |
| Task 10: Update CONTRIBUTING.md for Emit-PR `.gms` Diffs (PR14 Reaffirmation) | 6.4 | Refactor-only exception design |
| Task 11: Plan Sprint 26 Detailed Schedule | (integrates all) | Sprint 26 14-day schedule + day-by-day prompts |

**Coverage:** All 26 Sprint 26 prep-time unknowns are assigned to at least one prep task. Most Critical and High-priority unknowns are assigned to the same task that will act on the findings (e.g., Task 3 verifies all 6 Pattern C unknowns AND its findings drive Task 11's Day 1–4 schedule allocation).

**Carryforward from Sprint 25** (now informing Sprint 26 prep):

- **KU-33** (Pattern C generalizes beyond launch) → directly drives Category 1 — see Unknowns 1.1, 1.2, 1.4
- **KU-34** (bucket churn dominates path_syntax_error metric) → drives Task 9 PR17 work — see Unknown 6.3
- **KU-35** (multi-solve gate over-approximation invariant) → regression-canary protection (no specific unknown; tested via Sprint 26 final retest)
- **KU-36** (`_loop_tree_to_gams` bare-ID substitution invariant) → regression-canary protection (no specific unknown; tested via Sprint 26 final retest)

---

**Document Created:** 2026-05-07
**Last Updated:** 2026-05-07
**Total Unknowns:** 26
**Owner:** Sprint 26 Planning Team
**Review Frequency:** Daily during Sprint 26
