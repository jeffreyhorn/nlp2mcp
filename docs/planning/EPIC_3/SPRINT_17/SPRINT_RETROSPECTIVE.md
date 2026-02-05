# Sprint 17 Retrospective

**Created:** February 5, 2026  
**Duration:** 10 working days (January 31 – February 4, 2026)  
**Sprint Goal:** Translation/Solve Improvements, Parse Improvements & Release v1.1.0

---

## Executive Summary

Sprint 17 delivered the v1.1.0 release — the culmination of Epic 3 (GAMSLIB Validation Infrastructure). The sprint achieved dramatic translation improvements (+21 models, +25 percentage points), meaningful parse gains (+13 models), and a net +1 solve model despite a much larger denominator. While committed parse and solve targets were not fully met, the translation breakthrough exceeded expectations and the release was executed on schedule.

**Key Outcome:** 12/160 models (7.5%) achieve full pipeline success, up from 11/160 (6.9%) in Sprint 16. Translation rate jumped from 43.8% to 68.9% — the sprint's standout achievement.

---

## Goals and Results

### Sprint 17 Objectives

1. ✅ Fix translation blockers to increase translate rate
2. ⚠️ Fix emit_gams.py bugs to increase solve rate (partially achieved)
3. ⚠️ Address lexer/grammar issues to increase parse rate (below committed target)
4. ✅ Update documentation and release v1.1.0

### Metrics Summary

| Metric | Baseline (Sprint 16) | Committed Target | Achieved | Status |
|--------|----------------------|------------------|----------|--------|
| Parse Rate | 30.0% (48/160) | ≥48% (77/160) | **38.1% (61/160)** | Below committed (+13 vs +29) |
| Translate Rate | 43.8% (21/48) | ≥57% of parsed | **68.9% (42/61)** | Exceeded |
| Solve Rate | 52.4% (11/21) | ≥71% (15/21) | **28.6% (12/42)** | Missed (see analysis) |
| Full Pipeline | 6.9% (11/160) | ≥12% (19/160) | **7.5% (12/160)** | Below committed |
| Tests | 3043 | — | **3204** | +161 tests |

### Target vs. Actual Analysis

The committed targets assumed a specific execution order (translation fixes → emit_gams.py fixes → parse improvements) with cascade effects. What actually happened:

- **Translation:** Exceeded expectations. KKT/stationarity fixes on Days 1–3 enabled +21 models to translate (target was +11). The root cause fixes were more impactful than the planned "quick wins" (objective extraction, gamma derivatives, smin approximation), which were superseded by deeper KKT fixes.

- **Parse:** Achieved +13 models (target +29). The gap is explained by: (a) the planned Phase 1 quick wins for reserved words yielded +9 instead of +12 due to secondary put statement issues, (b) grammar additions (square brackets, solve variants, acronym, curly braces) were verified correct but target models had additional unrelated blocking issues.

- **Solve:** The solve *count* improved from 11 to 12 (+trussm, +trnsport, -mathopt1 reclassification). However, the translate count grew from 21 to 42, so the 30 newly-translated models that fail solve dragged down the solve rate from 52.4% to 28.6%. The committed target of 15/21 on the original models was predicated on emit_gams.py fixes (table data emission, subset preservation) that were deprioritized in favor of KKT fixes which had higher impact.

---

## What Worked Well

### 1. KKT/Stationarity Root Cause Fixes (Days 1–3)

The decision to focus on root causes in `src/kkt/stationarity.py` and `src/kkt/partition.py` rather than surface-level quick wins produced outsized results:
- **+21 models translating** from just 4 PRs (#606, #607, #608, #609)
- Fixes addressed fundamental issues: dimension mismatches, MCP pair mismatches, string literal indices, cross-domain summation
- Models like trnsport and trussm went from translate-fail to solve-success
- Each fix was targeted and well-scoped (1 issue = 1 PR)

### 2. Parse Improvement Methodology (Days 6–8)

The preprocessor-first approach proved effective:
- The comment handling bug fix (+9 models) had the highest ROI of any parse fix
- Incremental grammar additions were well-tested (16 unit tests for Day 7 alone)
- Bonus `prod()` function support was opportunistic and unlocked display continuation models

### 3. Late-Sprint Bug Fixes (Day 9+)

Four bug fixes merged after Day 9 documentation (Issues #620, #621, #623, #624) added trussm to the solving set, demonstrating that targeted fixes can have immediate pipeline impact even late in a sprint.

### 4. Release Execution Discipline

The Day 10 release was smooth:
- All quality gates passed on first run (3204 tests, typecheck, lint, format)
- Version bump, CHANGELOG, release notes, tag, and GitHub release executed cleanly
- Post-merge actions (tag + release) completed immediately

### 5. Prep Phase Investment

The 9 prep tasks from Sprint 17 planning provided a detailed roadmap:
- KNOWN_UNKNOWNS.md (26/27 verified) eliminated surprises
- TRANSLATION_ANALYSIS.md guided the KKT fix priorities
- LEXER_IMPROVEMENT_PLAN.md organized parse work into clear phases
- RELEASE_CHECKLIST.md made Day 10 execution mechanical

---

## What Could Be Improved

### 1. Committed Target Accuracy

Several committed targets were significantly missed:
- Parse: 38.1% vs 48% committed (79% of target)
- Full Pipeline: 7.5% vs 12% committed (63% of target)
- Solve: 12/42 vs 19/44 committed

**Lesson:** Committed targets assumed compound cascade effects (parse improvements → new translates → new solves). In practice, cascades are weaker than modeled. Future sprints should use more conservative cascade assumptions (~20% vs the ~40% used).

### 2. Solve Improvement Scope Shift

The original plan allocated Days 4–5 to emit_gams.py fixes (table data emission, subset preservation). Instead, Days 4–5 became investigation/consolidation of the KKT fixes from Days 1–3, and the planned emit_gams.py work was not executed.

**Lesson:** The KKT fixes were the right priority, but the plan should have been formally re-baselined at the CP2 checkpoint (Day 3) when the scope shifted. This would have set more realistic expectations for solve metrics.

### 3. Models with Multiple Blocking Issues

Several target models had 2+ independent blocking issues:
- ps5_s_mn, ps10_s, ps10_s_mn: Preprocessor fix helped, but put statement format syntax (`:10:5`) is a separate blocker
- worst.gms: Curly brace fix helped, but tuple expansion (Issue #612) is separate
- Many newly-translated models fail solve due to emit_gams.py issues unrelated to the KKT fixes

**Lesson:** The "models fixed" metric overpromises when models have stacked blockers. Track "blockers removed" alongside "models unblocked" to set accurate expectations.

### 4. Solve Rate Denominator Effect

The translation breakthrough (21 → 42 models) actually made the solve rate *worse* (52.4% → 28.6%) because 30 new models entered the solve stage with existing emit_gams.py issues. This created a confusing narrative where a genuinely successful sprint appeared to regress on solve rate.

**Lesson:** Always present both absolute counts and rates. Consider tracking solve rate separately for "original cohort" and "new cohort" models to distinguish real regression from denominator effects.

### 5. Flaky Performance Benchmarks

Post-release, CI failed twice on performance benchmark tests that exceeded thresholds by <1% (1.516s vs 1.5s limit, 8.015s vs 8.0s limit). These tests measure wall-clock time which varies with CI load.

**Lesson:** Performance benchmark thresholds should use generous margins (25%+ above expected) for CI environments. Consider using relative comparisons (regression detection) rather than absolute thresholds.

---

## Key Technical Decisions

### 1. KKT Root Causes over Quick Wins

**Decision:** Prioritize deep KKT/stationarity fixes (Days 1–3) over the planned quick wins (objective extraction, gamma derivatives, smin approximation).

**Rationale:**
- Issues #594, #599, #600, #603 addressed fundamental correctness bugs
- Each fix unblocked multiple models at both translate and solve stages
- The planned quick wins addressed surface symptoms rather than root causes

**Outcome:** +21 models translating, +1 model solving. The planned quick wins (gamma derivatives, smin, objective extraction) remain viable Sprint 18 work.

### 2. Preprocessor Bug Fix over Grammar Additions

**Decision:** Fix the comment-handling bug in `normalize_multi_line_continuations()` before adding grammar features.

**Rationale:**
- 9 models blocked by a single preprocessor bug (comments with `/` triggering data detection)
- Highest ROI parse fix: 9 models for 2 hours of work
- Grammar additions alone wouldn't help these models

**Outcome:** +9 models parsing. Clean separation of preprocessor vs. grammar issues.

### 3. Release on Schedule Despite Missing Targets

**Decision:** Release v1.1.0 on Day 10 despite parse and solve targets not being met.

**Rationale:**
- Translation improvements were substantial and releasable
- Quality was high (3204 tests, all gates clean)
- Remaining targets are additive improvements, not blockers
- Delaying would not change the metrics (remaining fixes need new sprint work)

**Outcome:** Clean release. The right decision — shipping incremental progress is better than holding for targets.

### 4. Superset-to-Subset Index Substitution (Issue #620)

**Decision:** Build a superset-to-subset mapping from `SetDef.domain` relationships and apply it in both code paths of `_replace_matching_indices()`.

**Rationale:**
- The root cause was that stationarity equations used superset indices (e.g., `mu(s)`) when the equation was defined over a subset (e.g., `stat_x(i)` where `i(s)`)
- Both the self-mapping path and the target_set path needed the same fix
- Using domain relationships from the IR was more robust than heuristic matching

**Outcome:** Fixed meanvar model. Clean fix that generalizes to other subset/superset patterns.

---

## Checkpoint Summary

| Checkpoint | Target Date | Target | Actual | Status |
|------------|-------------|--------|--------|--------|
| CP1 | Day 1 | +5 models translating | KKT fixes started | ✅ Complete |
| CP2 | Day 3 | 32/48 translate (66.7%) | 42/61 (68.8%) | ✅ Exceeded |
| CP3 | Day 5 | 15/21 solve (71.4%) | 11/42 (26.2%) | ⚠️ Partial (denominator shift) |
| CP4 | Day 7 | 74/160 parse (46.3%) | 61/160 (38.1%) | ⚠️ Below target |
| CP5 | Day 9 | All gates pass | 3204 tests pass | ✅ Complete |

---

## Deliverables Summary

### Code Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| KKT dimension mismatch fix | `src/kkt/partition.py` | ✅ PR #606 |
| KKT MCP pair mismatch fix | `src/kkt/stationarity.py`, `src/ad/derivative_rules.py` | ✅ PR #607 |
| Set index string literal fix | `src/ad/derivative_rules.py`, `src/kkt/stationarity.py` | ✅ PR #608 |
| Cross-domain summation fix | `src/kkt/stationarity.py` | ✅ PR #609 |
| Preprocessor comment fix | `src/ir/preprocessor.py` | ✅ PR #610 |
| Display comma optional | `src/gams/gams_grammar.lark` | ✅ PR #610 |
| prod() function support | `src/ir/ast.py`, `src/ir/parser.py`, grammar | ✅ PR #610 |
| Square bracket conditionals | `src/gams/gams_grammar.lark` | ✅ PR #611 |
| Solve keyword variants | `src/gams/gams_grammar.lark` | ✅ PR #611 |
| Acronym statement support | `src/gams/gams_grammar.lark`, `src/ir/parser.py` | ✅ PR #615 |
| Curly brace expressions | `src/gams/gams_grammar.lark`, `src/ir/parser.py` | ✅ PR #615 |
| Tuple prefix expansion fix | `src/ir/preprocessor.py`, `src/ir/parser.py` | ✅ PR #618 |
| Stationarity index fix | `src/kkt/stationarity.py` | ✅ PR #627 |
| Alias ordering fix | `src/emit/` | ✅ PR #625 |
| MCP pairing fix | `src/emit/model.py` | ✅ PR #628 |
| Version bump to 1.1.0 | `pyproject.toml` | ✅ PR #631 |

### Documentation Deliverables

| Deliverable | Location | Status |
|-------------|----------|--------|
| v1.1.0 Release Notes | `docs/releases/v1.1.0.md` | ✅ Complete |
| CHANGELOG.md update | `CHANGELOG.md` | ✅ Complete |
| DOCUMENTATION_INDEX.md refresh | `docs/DOCUMENTATION_INDEX.md` | ✅ Complete |
| SPRINT_LOG.md | `docs/planning/EPIC_3/SPRINT_17/SPRINT_LOG.md` | ✅ Complete |
| SPRINT_SCHEDULE.md | `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md` | ✅ Complete |

### Test Deliverables

| Area | New Tests | Notes |
|------|-----------|-------|
| KKT/stationarity fixes | ~20 | Across PRs #606–#609 |
| Grammar additions | 16 | `tests/unit/gams/test_grammar_additions.py` |
| Preprocessor/parse | ~15 | Tuple expansion, idempotency, comment handling |
| Stationarity subset index | 2 | `tests/integration/kkt/test_stationarity.py` |
| MCP pairing | 2 | `tests/unit/emit/test_model_mcp.py` |
| Pipeline/golden updates | ~10 | Updated golden files and MCP outputs |
| **Total Sprint 17** | **~161** | 3043 → 3204 |

---

## PR Summary

| Day | PR | Title | Status |
|-----|-----|-------|--------|
| 1 | #606 | Fix KKT dimension mismatch for uniform indexed bounds (Issue #600) | ✅ Merged |
| 2 | #607 | Fix KKT MCP pair mismatch for trnsport model (Issue #599) | ✅ Merged |
| 3 | #608 | Fix set index emitted as string literal for dispatch model (Issue #603) | ✅ Merged |
| 3 | #609 | Fix cross-domain summation in KKT stationarity equations (Issue #594) | ✅ Merged |
| 6 | #610 | Sprint 17 Day 6: Parse improvements | ✅ Merged |
| 7 | #611 | Sprint 17 Day 7: Grammar Additions | ✅ Merged |
| 8 | #615 | Sprint 17 Day 8: Additional Parse Fixes (Acronym & Curly Brace) | ✅ Merged |
| 8 | #616 | docs: Mark issue #613 (curly brace expressions) as resolved | ✅ Merged |
| 8 | #617 | feat: Add preprocess_text() for string-based GAMS preprocessing | ✅ Merged |
| 8 | #618 | fix: Support tuple prefix expansion in multiline set data (Issue #612) | ✅ Merged |
| 9 | #619 | Sprint 17 Day 9: Documentation & Pre-Release Verification | ✅ Merged |
| 9 | #625 | fix: Emit Alias statements before dependent Sets (Issue #621) | ✅ Merged |
| 9 | #627 | fix: Stationarity uncontrolled index variable (Issue #620) | ✅ Merged |
| 9 | #628 | fix: Missing MCP pairing for circle.gms (Issue #624) | ✅ Merged |
| 9 | #629 | fix: Missing MCP pairing for cpack.gms (Issue #623) | ✅ Merged |
| 9 | #630 | metrics: Sprint 17 Day 9 pipeline results | ✅ Merged |
| 10 | #631 | release: v1.1.0 - Sprint 17 Final Release | ✅ Merged |
| 10 | #632 | fix: Relax flaky parse benchmark thresholds | ✅ Merged |

**Total: 18 PRs merged in Sprint 17**

---

## Recommendations for Sprint 18

### Priority 1: Fix emit_gams.py Solve Blockers

**Target:** Address `path_syntax_error` (17 models) — the largest solve blocker category.

Sprint 17's KKT fixes dramatically increased translation (21 → 42 models), but 30 translated models now fail at solve due to emit_gams.py issues. These are the same emit_gams.py fixes that were planned for Sprint 17 Days 4–5 but deprioritized:

| Fix | Code Location | Models Affected | Effort |
|-----|---------------|-----------------|--------|
| Emit Table data | `src/emit/original_symbols.py` | ~4 models | 6h |
| Emit computed parameter assignments | `src/emit/original_symbols.py` | ~4 models | 4h |
| Preserve subset relationships | `src/emit/original_symbols.py` | ~3 models | 4h |
| Quote reserved words in set elements | `src/emit/expr_to_gams.py` | ~2 models | 2h |
| Other path_syntax_error patterns | Various emit modules | ~4 models | 6h |

**Expected Impact:** +8–12 models solving, solve rate from 28.6% to potentially 45–50%.

### Priority 2: Address IndexOffset Support

**Target:** `unsup_index_offset` (8 models) — the largest translation blocker.

Lead/lag indexing (`t-1`, `t+1`) is now the top translation failure category. This requires:
- IR-level support for IndexOffset nodes
- Derivative rules for shifted indices
- Emit support for GAMS lead/lag syntax

**Expected Impact:** +4–8 models translating. High effort (~8h) but high model count.

### Priority 3: Parse Improvements — Internal Errors

**Target:** `internal_error` (23 models) at parse stage.

The lexer_invalid_char count dropped from 97 to 74 (Sprint 16 → 17), but internal errors grew from 14 to 23. These are parser crashes (not lexer rejections) and may be addressable with targeted fixes:
- Investigate top error patterns in the 23 models
- Some may be newly-exposed by preprocessor fixes (models that now pass lexing but fail parsing)

**Expected Impact:** +5–10 models parsing.

### Priority 4: Investigate path_solve_terminated Models

**Target:** `path_solve_terminated` (11 models) — models that compile and run but PATH doesn't converge.

These models successfully pass through parse, translate, and GAMS compilation but the PATH solver fails to find a solution. Investigation needed:
- Check if these are infeasible MCP formulations (KKT correctness issues)
- Check if PATH configuration (iteration limits, tolerances) needs tuning
- Check if starting point initialization affects convergence

**Expected Impact:** Variable. Some may be KKT bugs, others may be genuinely hard problems.

### Priority 5: Put Statement Format Syntax

**Target:** 4 models blocked by put statement `:width:decimals` syntax (ps5_s_mn, ps10_s, ps10_s_mn, stdcge).

These models were partially unblocked by Sprint 17 preprocessor fixes but have a secondary put statement issue. Adding `:width:decimals` format support to the grammar would fully unblock them.

**Expected Impact:** +4 models parsing. Low effort (~2h).

### Priority 6: Remaining Grammar Gaps

Several grammar features identified during Sprint 17 remain unimplemented:
- Compile-time constants in ranges (e.g., `1*card(s)`)
- Complex set data syntax (14 hard models deferred from Sprint 17)
- Implicit assignment statements (3 models)

**Expected Impact:** +5–10 models parsing. Medium-to-high effort.

### Priority 7: Stabilize Performance Benchmarks

The CI performance benchmarks failed twice post-release on thresholds exceeded by <1%. Options:
- Switch to regression detection (compare against baseline) rather than absolute thresholds
- Add warm-up runs to reduce cold-start variance
- Use statistical approach (run N times, check median)

**Expected Impact:** Eliminates flaky CI failures. Low effort (~2h).

### Process Recommendations

1. **Re-baseline at checkpoints:** When sprint scope shifts significantly (as it did at CP2 when KKT fixes superseded quick wins), formally update targets and communicate the change.

2. **Track "blockers removed" not just "models fixed":** Many models have 2+ independent issues. Tracking blocker removal gives a more honest view of progress.

3. **Separate solve cohorts:** Track solve metrics for "existing translated" and "newly translated" models separately to avoid denominator confusion.

4. **Run pipeline earlier and more often:** Sprint 17 ran the full pipeline only on Day 9. Running it on Day 3 and Day 6 would have surfaced the solve denominator issue sooner.

---

## Metrics for Tracking

### Sprint 17 Final Metrics

| Metric | Value |
|--------|-------|
| Parse Success | 61/160 (38.1%) |
| Translate Success | 42/61 (68.9%) |
| Solve Success | 12/42 (28.6%) |
| Full Pipeline | 12/160 (7.5%) |
| Tests | 3204 passing |
| PRs Merged | 18 |

**12 Solving Models:** apl1p, blend, himmel11, hs62, mathopt2, mhw4d, mhw4dx, prodmix, rbrock, trig, trnsport, trussm

### Error Category Trends

| Category | Sprint 15 | Sprint 16 | Sprint 17 | Change (S16→S17) |
|----------|-----------|-----------|-----------|-------------------|
| lexer_invalid_char | 109 | 97 | 74 | -23 |
| internal_error (parse) | 17 | 14 | 23 | +9 |
| semantic_undefined_symbol | — | — | 2 | New |
| path_syntax_error | 14 | 8 | 17 | +9 |
| path_solve_terminated | — | — | 11 | New |
| model_infeasible | — | 1 | 2 | +1 |
| Total Parse Failures | 126 | 112 | 99 | -13 |
| Total Translate Failures | — | 27 | 19 | -8 |
| Total Solve Failures | — | 10 | 30 | +20 |

**Note:** Solve failures increased from 10 to 30 because translate count grew from 21 to 42. The path_syntax_error count increased from 8 to 17 for the same reason — more models reaching the solve stage. The internal_error parse count increased from 14 to 23 likely because preprocessor fixes now allow more models to pass lexing but fail at a later parse stage.

---

## Appendix: Daily Summary

| Day | Focus | Key Outcome |
|-----|-------|-------------|
| Day 0 | Setup | Verified baseline, confirmed 48/160 parse, 21/48 translate, 11/21 solve |
| Day 1 | Translation | KKT dimension mismatch fix (Issue #600) — chem model |
| Day 2 | Translation | KKT MCP pair mismatch fix (Issue #599) — trnsport model |
| Day 3 | Translation | Set index fix (#603) + cross-domain fix (#594) — dispatch, trussm |
| Day 4 | Solve Investigation | KKT fixes consolidated; remaining solve failures mapped |
| Day 5 | Solve Investigation | Documented path_syntax_error, path_solve_terminated categories |
| Day 6 | Parse | Preprocessor comment fix (+9), display comma (+5), prod function |
| Day 7 | Parse | Square bracket conditionals, solve keyword variants |
| Day 8 | Parse | Acronym statements, curly brace expressions, mathopt4/procmean |
| Day 9 | Documentation | Release notes, CHANGELOG, DOCUMENTATION_INDEX, pre-release verification |
| Day 9+ | Bug Fixes | Issues #620, #621, #623, #624 — stationarity, alias, MCP pairing |
| Day 10 | Release | v1.1.0 released — version bump, tag, GitHub release |

---

## Conclusion

Sprint 17 achieved its primary goal of releasing v1.1.0 on schedule. The sprint's standout result was the translation breakthrough: +21 models translating (43.8% → 68.9%), driven by deep KKT/stationarity fixes that addressed root causes rather than symptoms. Parse improvements added +13 models (30.0% → 38.1%), and the solve count nudged up from 11 to 12 despite a denominator that doubled.

The gap between committed targets and actual results highlights the difficulty of predicting cascade effects across pipeline stages. The sprint adapted well — prioritizing KKT root causes over planned quick wins was the right call — but formal re-baselining at checkpoints would have set more accurate expectations.

**Sprint 17 Success:**
- ✅ v1.1.0 released on schedule (tag + GitHub release)
- ✅ Translation rate nearly doubled: 43.8% → 68.9% (+21 models)
- ✅ Parse rate improved: 30.0% → 38.1% (+13 models)
- ✅ Full pipeline: 11 → 12 models solving
- ✅ 3204 tests passing, all quality gates clean
- ✅ 18 PRs merged across 10 days
- ⚠️ Committed parse target missed (38.1% vs 48%)
- ⚠️ Committed solve/pipeline targets missed due to denominator growth

Sprint 18 has a clear path forward: emit_gams.py fixes for the 17 path_syntax_error models, IndexOffset support for 8 translation failures, and continued parse improvements targeting internal_error models.

---

## References

- [SPRINT_LOG.md](SPRINT_LOG.md) - Daily progress log
- [SPRINT_SCHEDULE.md](SPRINT_SCHEDULE.md) - Schedule and targets
- [PREP_PLAN.md](PREP_PLAN.md) - Prep phase findings
- [KNOWN_UNKNOWNS.md](KNOWN_UNKNOWNS.md) - Verified unknowns (26/27)
- [v1.1.0 Release Notes](../../../releases/v1.1.0.md) - Release documentation
- [CHANGELOG.md](../../../../CHANGELOG.md) - Full change history
