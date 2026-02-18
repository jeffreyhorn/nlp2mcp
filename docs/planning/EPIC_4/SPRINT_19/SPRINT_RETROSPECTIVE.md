# Sprint 19 Retrospective

**Created:** February 18, 2026
**Duration:** 14 sprint days (Day 0 – Day 14, February 2026)
**Sprint Goal:** Parse Rate ≥55%, lexer_invalid_char <30, IndexOffset AD Integration, ISSUE_670 cross-indexed sums

---

## Executive Summary

Sprint 19 was the largest sprint in Epic 4, combining Sprint 18 deferred items with new grammar work and a major AD integration project. It delivered on every core objective: parse rate jumped from 38.1% to 66.9% (of tested models), lexer_invalid_char dropped from 72 to 27 (target: <30), internal_error from 24 to 6, IndexOffset AD integration completed, and ISSUE_670 cross-indexed sum pattern resolved. Translate success grew by +25 models, solve success by +5, and 285 new tests were added with zero regressions across 39 PRs.

**Key Outcome:** 107/160 tested models now parse (66.9%), up from 61/160 (38.1%). 25 models solve successfully (up from 20). 9 models achieve full pipeline match (up from 7). All P1–P3 roadmap items delivered.

---

## Goals and Results

### Sprint 19 Objectives

1. ✅ Reduce lexer_invalid_char to <30 (achieved: 27)
2. ✅ Complete IndexOffset AD integration
3. ✅ Fix ISSUE_670 cross-indexed sum pattern (GAMS Error 149)
4. ✅ Fix ISSUE_672 case sensitivity
5. ✅ Fix ISSUE_392/399 table parsing (subset verification)
6. ✅ Fix compound set data grammar (Subcategories A/B/F/I)
7. ✅ Resolve open issues from sprint backlog (#774, #766, #671 and others)

### Metrics Summary

| Metric | Baseline (Sprint 18) | Committed Target | Achieved | Status |
|--------|----------------------|------------------|----------|--------|
| Parse Rate (tested) | 38.1% (61/160) | ≥55% (88/160) | **66.9% (107/160)** | Exceeded |
| lexer_invalid_char | 72 | <30 | **27** | ✅ Met |
| internal_error (pipeline) | 24 | <15 | **6** | ✅ Exceeded |
| Translate Success | 48 | 55+ | **73** | Exceeded |
| Solve Success | 20 | 25+ | **25** | ✅ Met |
| Full Pipeline Match | 7 | 10+ | **9** | ⚠️ Below target |
| Tests | 3,294 | 3,350+ | **3,579** | Exceeded |
| Regressions | 0 | 0 | **0** | ✅ Met |

### Target vs. Actual Analysis

- **Parse Rate:** Dramatically exceeded the 55% target, reaching 66.9%. The compound set data grammar work (Days 8–9) alone unblocked ~27 models across Subcategories A, B, and I. Subcategory F grammar fixes on Day 11 added ~10 more.

- **lexer_invalid_char:** Met with room to spare (27 vs <30). The grammar additions addressing Subcategories A/B/F/I covered the vast majority of lexer-level failures.

- **internal_error:** The 24 baseline internal errors were almost entirely resolved. Only 6 remain — all requiring architectural changes beyond this sprint's scope.

- **Translate Success:** Substantially exceeded the 55+ target (73 models). ISSUE_670 fix + ISSUE_672 case sensitivity fix + table parsing fix collectively unblocked many models that had previously parsed but not translated.

- **Solve Success:** Met exactly at 25 (target: 25+). Notable new solvers: house (ISSUE_670 fix), abel, chakra, hhmax, himmel16, mathopt1.

- **Full Pipeline Match:** Missed target of 10+ by 1 (achieved 9). The 9 matching models are: ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport.

- **IndexOffset AD:** Fully delivered (Days 12–13): `_substitute_index()` helper, `_apply_index_substitution()` for VarRef/ParamRef/DollarConditional with IndexOffset bases, `offset_paren`/`offset_func` parser fixes.

---

## What Worked Well

### 1. Compound Set Data Grammar (Days 8–9)

The decision to systematically tackle LEXER_ERROR_CATALOG Subcategories A through I (rather than model-by-model triage) was the sprint's highest-leverage move. A single well-structured grammar PR on Day 8 unblocked 5 out of 12 Subcategory A models, and Day 9 completed the full Subcategory A/B/I sweep (+42 models parsing). The key grammar additions — `range_expr` in set element lists, `set_tuple_cross_expansion`, outer parentheses in set members, `tuple_suffix_expansion_label` in table row labels — were identified by analyzing patterns across all blocked models simultaneously.

**Outcome:** ~42 models unblocked in 2 days. The subcategory taxonomy proved essential for grouping related fixes and estimating scope accurately.

### 2. ISSUE_670 Cross-Indexed Sum Fix (Days 5–7)

The `_collect_free_indices()` + Sum-wrapping approach for uncontrolled indices resolved the deepest and most widespread translation blocker in the codebase. The fix was split across 3 days (Part 1 indexed path, Part 2 scalar path + static subsets, Day 7 wrap-up with 6 models), demonstrating that staged delivery of complex fixes prevents large context-window commits and makes review tractable.

**Outcome:** 6 models (orani, robert, abel, qabel, and others) now translate and solve. Orani, previously considered "not fixable," turned out to be fully resolved as a bonus.

### 3. Day 1 Rapid Issue Triage

The sprint opened by immediately addressing a backlog of open GitHub issues from Sprint 18 (PRs #707–#743), closing ~20 issues in the first 2 days before any planned sprint work. This cleared the issue queue and prevented context-switching mid-sprint.

**Outcome:** ~20 issues resolved before structured sprint work began. The sprint "started clean."

### 4. Checkpoint Discipline

Both checkpoints were evaluated formally:
- **Checkpoint 1 (Day 6):** ISSUE_670 complete, abel/qabel solving, 66.5% parse rate at that point → GO
- **Checkpoint 2 (Day 11):** All P1–P3 items done, lexer_invalid_char 27, parse 66.9% → GO

The checkpoints provided natural decision points for scope adjustment and gave confidence to proceed with the IndexOffset AD work (Days 12–13) rather than pivoting to lower-priority items.

### 5. IndexOffset AD Integration (Days 12–13)

A complex, multi-file feature delivered cleanly in 2 days. The `expr_fn` callback pattern threading the expression evaluator into offset processing was the key architectural insight — it avoided circular dependencies between static helpers and instance methods. The staged approach (Part 1: core substitution infrastructure, Part 2: parser hooks) kept each PR reviewable.

**Outcome:** `mine`, `ampl`, `tabora`, `otpop`, `sparta` unblocked. 23 new unit tests.

### 6. Late-Sprint Issue Resolution (Day 14)

The Day 14 sweep of remaining open issues (#774 shale, #766 robert) fixed two non-trivial bugs efficiently: the singleton equation quoted-domain pattern and the subset/superset index mismatch in `_replace_matching_indices()`. The identification that #671 (orani) was already resolved by prior work — and closing it — demonstrated good backlog hygiene.

---

## What Could Be Improved

### 1. Full Pipeline Match Target Missed

The target of 10+ full pipeline matches was missed by 1 (achieved 9). The gap is that several models now solve (PATH model status 1) but produce different objective values than the original GAMS solve — typically due to missing variable initialization (`.l` assignments) or scaling. These models are "close" to matching but require emitter-level changes beyond parse/translate.

**Lesson:** The full pipeline match metric lags behind translate/solve improvements by at least one sprint. Future sprints should set this target conservatively and track "models within ε of reference solution" as a leading indicator.

### 2. `lop` Model Silently Excluded

The `lop` model was excluded from the pipeline mid-sprint due to Jacobian explosion (billions of entries), changing the effective denominator from 161 to 160. This was not formally documented in the sprint log at the time, creating a confusing 159/160 baseline discrepancy in the metrics.

**Lesson:** Denominator changes (model additions/exclusions) should be documented explicitly in the sprint log with a dated entry and the reason. The sprint baseline metrics should be pinned at the start-of-sprint snapshot.

### 3. Day 13 Validation Exposed 5 New Issues Late

The Day 13 IndexOffset validation run identified 5 new issues (#780–#784) in the final days of the sprint, requiring Day 14 fixes. While these were all resolved, it compressed Day 14 with less time for pipeline retesting and documentation.

**Lesson:** Model validation runs should happen earlier (e.g., Day 10–11) so there is buffer to address newly-discovered issues without crowding sprint close activities.

### 4. "Not Fixable" Assessment Was Premature for #671

Issue #671 (orani) was initially documented as "not fixable in Sprint 19" during Day 14 triage, when in fact the ISSUE_670 fix had already resolved it. The error was caught quickly by the user, but it reflects insufficient pipeline verification before making not-fixable declarations.

**Lesson:** Before marking an issue as not fixable, verify the current pipeline status against the actual model. A quick `python -m src.cli <model>` smoke test takes 30 seconds and prevents false negatives.

### 5. Parse Rate Denominator Confusion

The sprint baseline was recorded as "61/159" but the actual tested count was 160 from the start (the 159 was likely from a pre-lop-exclusion snapshot). This caused confusion when computing final metrics.

**Lesson:** Always use the count from `gamslib_status.json` directly (`nlp2mcp_parse` key present) rather than manual counting. Automate the baseline snapshot at sprint start.

### 6. Deferred Issues Accumulating

5 issues (#753, #757, #763, #764, #765) were deferred to future sprints. While each has a clear documented reason (IR+emitter for `.l`, `.scale` emission, AD condition propagation, KKT accounting variables, CGE exogenous variables), they represent an accumulating backlog of solver-infeasibility patterns that will eventually require an architectural sprint.

**Lesson:** Consider a dedicated "solver quality" sprint (or epic) in the near future that addresses the common root causes: variable initialization emission, scaling, and accounting variable detection.

---

## Key Technical Decisions

### 1. Subcategory Taxonomy for Grammar Fixes

**Decision:** Organize all 72 lexer_invalid_char models into lettered subcategories (A: compound set data, B: cascading, F: declaration gaps, I: function variants) and fix by subcategory rather than individually.

**Rationale:** Models in the same subcategory share the same root grammar gap. Fixing the grammar once unblocks all of them simultaneously.

**Outcome:** +46 parse successes from subcategory-targeted grammar fixes. Without taxonomization, the same work would have required 46 individual investigations.

### 2. ISSUE_670: `_collect_free_indices()` + Sum-Wrapping

**Decision:** After `_replace_indices_in_expr()`, collect any remaining free indices in the derivative expression that are not controlled by the equation domain or multiplier domain, and wrap them in an additional `Sum` node.

**Rationale:** The cross-indexed sum pattern generates derivative terms with "stray" indices from the original constraint's inner sum. These are not bugs in the derivative but in the emission — GAMS Error 149 ("set not under control") is a scope issue, not a math issue. The fix is to explicitly bound these indices with a Sum.

**Outcome:** Clean, general solution that handled all 6 ISSUE_670-affected models without model-specific special cases.

### 3. `expr_fn` Callback for IndexOffset Processing

**Decision:** Add an `expr_fn: Callable[[Tree], Expr] | None = None` parameter to `_process_index_expr()` and `_process_index_list()` to thread the expression evaluator into offset processing.

**Rationale:** The `_process_index_expr()` helper is a static-style function that doesn't have access to the `GAMSParser` instance's `_expr()` method. The callback pattern avoids making it an instance method (which would require large refactoring) while enabling recursive expression evaluation for complex offset expressions like `i+li(k)`.

**Outcome:** Clean architecture. `offset_paren` and `offset_func` (including `ref_indexed` variants) now fully supported.

### 4. Issue #766 Subset Guard in `_replace_matching_indices()`

**Decision:** When the Issue #730 override fires (use `element_to_set[idx]` over `target_set`), add a guard that checks if `target_set` is a proper subset of an equation-domain set. If so, the narrower declared domain is intentional — skip the override.

**Rationale:** The #730 override was designed for alias sets (where the declared domain name is an alias of an equation-domain set). It incorrectly replaced `t` → `tt` for parameters declared over the subset `t`, producing GAMS Error 171 domain violations. The subset check using `SetDef.domain` relationships is the correct discriminator.

**Outcome:** robert model generates valid MCP. The fix generalizes to any model where a parameter's declared domain is a proper subset of the stationarity equation's domain.

### 5. Singleton Equation Detection (#774)

**Decision:** In `_handle_eqn_def_domain()`, check raw token values using `_is_string_literal()` before calling `_ensure_sets()`. If all domain elements are quoted string literals, use the equation's declared domain from `_equation_domains` instead.

**Rationale:** GAMS allows `eq("literal")..` as a singleton instantiation — the equation is defined for exactly one set element rather than iterating over a set. The `_domain_list()` function strips quotes, making it impossible to distinguish a set name from a set element literal after the fact. The check must happen on raw tokens.

**Outcome:** shale model translates successfully. The fix correctly handles both `mmr3("2000-04")..` (scalar equation) and the general case where an equation has a declared domain that happens to be indexed with a literal.

---

## Checkpoint Summary

| Checkpoint | Target Date | Criteria | Actual | Status |
|------------|-------------|----------|--------|--------|
| CP1 | Day 6 | ISSUE_670 Part 1, abel/qabel translate | ✅ ISSUE_670 complete, 66.5% parse | ✅ GO |
| CP2 | Day 11 | P1–P3 done, lexer_invalid_char <30 | ✅ 27 lexer errors, all P1–P3 done | ✅ GO |

---

## Deliverables Summary

### Code Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| Special values grammar (na/inf/eps/undf) | `src/gams/gams_grammar.lark` | ✅ PR #750 |
| circle deterministic fix (execseed) | `src/ir/parser.py` | ✅ PR #750 |
| Put statement format specifiers | `src/gams/gams_grammar.lark` | ✅ PR #745 |
| Reserved word quoting in emit | `src/emit/expr_to_gams.py` | ✅ PR #745 |
| ISSUE_672 case sensitivity (CaseInsensitiveDict) | `src/ir/parser.py` | ✅ PR #756 |
| ISSUE_670 Part 1: indexed path + `_collect_free_indices()` | `src/kkt/stationarity.py` | ✅ PR #758 |
| ISSUE_759+760 abel domain restriction | `src/kkt/stationarity.py` | ✅ PR #761 |
| ISSUE_670 Part 2: scalar path + static subsets | `src/kkt/stationarity.py` | ✅ PR #762 |
| ISSUE_670 wrap-up (6 models clean) | `src/kkt/stationarity.py` | ✅ PR #770 |
| Compound set data grammar (Subcategory A Part 1) | `src/gams/gams_grammar.lark`, preprocessor | ✅ PR #773 |
| Compound set data grammar (Subcategory A/B/I complete) | `src/gams/gams_grammar.lark`, preprocessor | ✅ PR #775 |
| Table parsing fix (ISSUE_392/399) | `src/ir/parser.py` | ✅ PR #777 |
| Subcategory F grammar fixes (8 additions) | `src/gams/gams_grammar.lark`, `src/ir/parser.py` | ✅ PR #778 |
| IndexOffset AD integration (Part 1) | `src/ir/parser.py`, `src/ad/` | ✅ PR #779 |
| IndexOffset validation + offset_paren/offset_func fix | `src/ir/parser.py` | ✅ PR #785 |
| Issues #780–#784 (5 models unblocked) | `src/ir/parser.py`, `src/gams/gams_grammar.lark` | ✅ PR #786 |
| Issue #774 shale singleton equation | `src/ir/parser.py` | ✅ PR #787 |
| Issue #766 robert subset/superset index guard | `src/kkt/stationarity.py` | ✅ PR #787 |
| 20+ open issue fixes (PRs #707–#743) | Various | ✅ PRs #707–#743 |

### Documentation Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| SPRINT_LOG.md | `docs/planning/EPIC_4/SPRINT_19/SPRINT_LOG.md` | ✅ Complete |
| PLAN.md (all days) | `docs/planning/EPIC_4/SPRINT_19/PLAN.md` | ✅ Complete |
| CHANGELOG.md update | `CHANGELOG.md` | ✅ Complete |
| Issue files (7 fixed → completed/) | `docs/issues/completed/` | ✅ Complete |
| Issue files (5 deferred, status updated) | `docs/issues/` | ✅ Complete |
| SPRINT_RETROSPECTIVE.md | `docs/planning/EPIC_4/SPRINT_19/` | ✅ This document |

### Test Deliverables

| Area | New Tests | Notes |
|------|-----------|-------|
| Special values / circle | ~10 | Grammar + determinism tests |
| Put statement / reserved words | ~12 | Format specifier variants |
| ISSUE_672 case sensitivity | ~15 | CaseInsensitiveDict coverage |
| ISSUE_670 cross-indexed sums | ~20 | Stationarity sum-wrapping |
| Compound set data grammar | ~30 | Range expansion, tuple labels, table rows |
| Table parsing (ISSUE_392/399) | ~25 | Subset verification, continuation |
| Subcategory F grammar | ~15 | NONNEGATIVE_K, eqn_head_mixed, smax/smin |
| IndexOffset AD integration | 23 | `TestIndexOffsetDerivative`, 1 xfail |
| offset_paren/offset_func | 4 | `TestOffsetParenIndexing` |
| Issue-specific fixes | ~131 | PRs #707–#743, #786, #787 |
| **Total Sprint 19** | **~285** | 3,294 → 3,579 |

---

## PR Summary

### Prep Phase (Planning PRs)

| PR | Title | Status |
|----|-------|--------|
| #693–#701 | Sprint 19 planning tasks (prep, prompts, workstreams) | ✅ Merged |

### Sprint Day PRs

| Day | PR | Title | Status |
|-----|-----|-------|--------|
| 0 | #702 | Sprint 19 Day 0: Init + baseline | ✅ Merged |
| 1 | #707 | Sprint 19 Day 1: Setup + quick wins | ✅ Merged |
| 1 | #708 | Fix issues #703–#706 | ✅ Merged |
| 1 | #712 | Fix issues #709–#711 | ✅ Merged |
| 1 | #717 | Fix issues #713–#715 | ✅ Merged |
| 1 | #721 | Fix issues #718–#720 | ✅ Merged |
| 1 | #725 | Fix issues #722–#724 | ✅ Merged |
| 1 | #728 | Fix issues #726–#727 | ✅ Merged |
| 1 | #731 | Fix issues #729–#730 | ✅ Merged |
| 1 | #734 | Fix issue #732 | ✅ Merged |
| 1 | #735 | Fix issue #733 | ✅ Merged |
| 1 | #737 | Fix issue #730 (follow-up) | ✅ Merged |
| 1 | #740 | Fix issues #738–#739 | ✅ Merged |
| 1 | #743 | Fix issues #741–#742 | ✅ Merged |
| 2 | #745 | Put statement format + reserved word quoting | ✅ Merged |
| 3 | #750/#754 | Special values grammar + circle deterministic fix | ✅ Merged |
| 4 | #756 | ISSUE_672 case sensitivity fix | ✅ Merged |
| 5 | #758 | ISSUE_670 Part 1: cross-indexed sums | ✅ Merged |
| 6 | #761 | ISSUE_759+760: abel domain restriction | ✅ Merged |
| 6 | #762 | ISSUE_670 complete + Checkpoint 1 | ✅ Merged |
| 7 | #770 | ISSUE_670 wrap-up + house model | ✅ Merged |
| 8 | #773 | Compound set data grammar (Part 1) | ✅ Merged |
| 9 | #775 | Compound set data complete + model/solve | ✅ Merged |
| 10 | #777 | Table parsing fix (ISSUE_392/399) | ✅ Merged |
| 11 | #778 | Declaration gaps + Checkpoint 2 | ✅ Merged |
| 12 | #779 | IndexOffset AD integration | ✅ Merged |
| 13 | #785 | IndexOffset validation + offset_paren fix | ✅ Merged |
| 14 | #786 | Fix issues #780–#784 | ✅ Merged |
| 14 | #787 | Fix #774, #766, close #671 | ✅ Merged |
| 14 | #788 | Sprint close: CHANGELOG, PLAN, SPRINT_LOG | In Review |

**Total: ~39 PRs merged in Sprint 19** (including prep planning PRs)

---

## Models Unblocked This Sprint

### Parse Stage (selected highlights)

Subcategory A (compound set data): kand, paklive, marco, china, shale, and ~12 more
Subcategory B (cascading from A): ~15 models
Subcategory F (declaration/syntax gaps): wall, robustlp, solveopt, tricp, imsl, qdemo7, and ~4 more
Subcategory I (function variants): pdi, qsambal, mlbeta, mlgamma, sambal
IndexOffset models: mine, ampl, tabora, otpop, sparta

### Translate/Solve Stage

Models newly solving (Sprint 18 → Sprint 19): abel, aircraft, ajax, alkyl, apl1pca, chakra, demo1, hhmax, himmel16, house, mathopt1, port, process (+13 new solvers)

### Full Pipeline Match (9 models)

ajax, blend, demo1, himmel11, house, mathopt2, prodmix, rbrock, trnsport

---

## Recommendations for Sprint 20

### Priority 1: Variable Initialization Emission (`.l` assignments)

**Target:** circle, bearing, and other models that solve but produce PATH model status 5 (locally infeasible).

The root cause for several deferred issues (#753 circle, #757 bearing) is that the MCP translator doesn't emit variable level initializations from `.l` assignments in the original model. PATH is highly sensitive to starting points — without good initialization, it fails to find a KKT solution even when the MCP is correctly formulated.

**Fix:** Emit `.l` initialization statements from the IR in the prolog of the generated MCP file. The IR already parses these assignments; it's primarily an emitter gap.

**Expected Impact:** +2–4 models solving. Low-to-medium effort.

### Priority 2: Accounting Variable Detection (#764 mexss)

**Target:** mexss and similar models with auxiliary/identity variables.

Accounting variables (e.g., `xmarket = sum(p, x(p))`) should not get stationarity equations — they are definitional identities, not optimization variables. Generating stationarity for them produces an over-constrained MCP.

**Fix:** Detect variables that appear only on the LHS of equality constraints with no objective contribution (pure identities) and exclude them from the stationarity system.

**Expected Impact:** +1–3 models solving. Medium effort, requires design work first.

### Priority 3: AD Condition Propagation (#763 chenery)

**Target:** chenery and models with conditional denominators.

The chenery model uses `$` conditions to guard denominators in equations (e.g., `x / del(i)` where `del(i) = 0` for some `i`). The AD system produces derivatives without these guards, causing GAMS EXECERROR = 1 (division by zero).

**Fix:** Propagate the enclosing `$` condition through derivative expressions, or detect division-by-parameter patterns and add guards automatically.

**Expected Impact:** +1 model solving. Medium-to-high effort (AD condition propagation is architectural).

### Priority 4: Remaining lexer_invalid_char Models (27 remaining)

**Target:** Further reduce from 27 toward 0.

With Subcategories A/B/F/I addressed, the remaining 27 lexer failures likely fall into new subcategories. A fresh taxonomy pass (similar to the LEXER_ERROR_CATALOG work) should identify the next highest-leverage grammar additions.

**Expected Impact:** +10–15 models parsing. Medium effort.

### Priority 5: Full Pipeline Match Rate

**Target:** 10+ full pipeline matches (currently 9).

The gap between solve success (25) and full pipeline match (9) suggests that many solved models produce different objective values than the reference. Investigate whether `.l` initialization, scaling, or other initialization issues are the cause, and whether solution comparison tolerances need adjustment.

### Process Recommendations

1. **Run pipeline smoke test before declaring issues "not fixable."** A 30-second CLI run reveals current status and prevents false negatives like #671.

2. **Document denominator changes immediately.** Any model exclusion (like `lop`) should be logged with a dated entry in SPRINT_LOG.md at the time of exclusion, not reconstructed later.

3. **Run model validation earlier (Day 10–11)** rather than Day 13 to allow buffer for newly-discovered issues before sprint close.

4. **Snapshot `gamslib_status.json` at sprint start** and pin the baseline metrics from that snapshot to avoid confusion from mid-sprint updates.

5. **Track "models within 1% of reference objective"** as a leading indicator for full pipeline match, to give earlier visibility into solve quality issues.

---

## Metrics for Tracking

### Sprint 19 Final Metrics

| Metric | Value |
|--------|-------|
| Parse Success | 107/160 tested (66.9%) |
| Translate Success | 73/107 (68.2%) |
| Solve Success | 25/73 (34.2%) |
| Full Pipeline Match | 9/160 (5.6%) |
| Tests | 3,579 passing |
| PRs Merged | ~39 |
| lexer_invalid_char | 27 |
| internal_error (pipeline) | 6 |

### Error Category Trends

| Category | Sprint 17 End | Sprint 18 End | Sprint 19 End | Change (S18→S19) |
|----------|--------------|--------------|--------------|------------------|
| lexer_invalid_char | 74 | 72 | 27 | **-45** |
| internal_error (pipeline) | 23 | 24 | 6 | **-18** |
| semantic_undefined_symbol | 2 | ~5 | 5 | ~0 |
| model_no_objective_def | — | — | 14 | new category |
| parser_invalid_expression | — | — | 1 | new |

### 25 Solving Models

abel, aircraft, ajax, alkyl, apl1p, apl1pca, blend, chakra, chem, demo1, dispatch, hhmax, himmel11, himmel16, house, mathopt1, mathopt2, mhw4d, mhw4dx, port, process, prodmix, rbrock, trig, trnsport

---

## Appendix: Daily Summary

| Day | Focus | Key Outcome |
|-----|-------|-------------|
| Day 0 | Init | Baseline verified: 61/160 parse, 48 translate, 20 solve, 7 match |
| Day 1 | Issue triage | ~20 open issues from Sprint 18 resolved (PRs #707–#743) |
| Day 2 | Put statements | Put format specifiers + reserved word quoting (+6 models parse) |
| Day 3 | Special values | na/inf/eps/undf grammar + circle deterministic fix |
| Day 4 | ISSUE_672 | CaseInsensitiveDict case sensitivity fix |
| Day 5 | ISSUE_670 Part 1 | `_collect_free_indices()` + indexed path Sum-wrapping |
| Day 6 | ISSUE_670 complete | Scalar path + static subsets + Checkpoint 1 GO (66.5% parse) |
| Day 7 | ISSUE_670 wrap-up | All 6 affected models translate cleanly; house model solves |
| Day 8 | Compound set Part 1 | `range_expr`, `set_tuple_cross_expansion`, table row labels (+5 models) |
| Day 9 | Compound set complete | All Subcategory A/B/I models parse (+42 models total) |
| Day 10 | Table parsing | ISSUE_392/399 subset verification fix |
| Day 11 | Subcategory F | NONNEGATIVE_K, smax/smin, eqn_head_mixed_list + Checkpoint 2 GO |
| Day 12 | IndexOffset AD Part 1 | `_substitute_index()`, VarRef/ParamRef/DollarConditional support |
| Day 13 | IndexOffset validation | offset_paren/offset_func fix; 5 new issues filed (#780–#784) |
| Day 14 | Sprint close | Fix #780–#784, #774, #766; close #671; document deferred issues |

---

## Conclusion

Sprint 19 was a high-execution sprint that delivered on all core objectives and substantially exceeded parse targets. The subcategory taxonomy for grammar work, staged delivery of the ISSUE_670 fix, and checkpoint discipline were the standout process successes. The parse rate went from 38.1% to 66.9% — the largest single-sprint parse improvement in the project's history.

The main gaps were the full pipeline match target (9 vs 10+) and the accumulation of solver-quality deferred issues. These point to a clear Sprint 20 agenda: emission of variable initializations, accounting variable detection, and continued lexer_invalid_char reduction.

**Sprint 19 Success:**
- ✅ Parse rate: 38.1% → 66.9% (+46 models, target ≥55%)
- ✅ lexer_invalid_char: 72 → 27 (target <30)
- ✅ internal_error: 24 → 6 (target <15)
- ✅ Translate success: 48 → 73 (+25 models)
- ✅ Solve success: 20 → 25 (+5 models, target 25+)
- ✅ IndexOffset AD integration complete
- ✅ ISSUE_670 cross-indexed sum pattern resolved
- ✅ 3,579 tests passing, zero regressions
- ✅ ~39 PRs merged across 14 days
- ⚠️ Full pipeline match: 9 (target 10+, missed by 1)

Sprint 20 has a clear path: emit `.l` initializations, accounting variable detection, AD condition propagation, and continued parse improvements.

---

## References

- [SPRINT_LOG.md](SPRINT_LOG.md) — Daily progress log
- [PLAN.md](PLAN.md) — Sprint plan and workstreams
- [CHANGELOG.md](../../../../CHANGELOG.md) — Full change history
- [ISSUE_670 Design Doc](../../EPIC_4/SPRINT_19/ISSUE_670_DESIGN.md) — Cross-indexed sum design
- [docs/issues/completed/](../../../issues/completed/) — Resolved issue files
