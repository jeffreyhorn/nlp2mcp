# Issues to Address: Prioritized Low-Hanging Fruit

**Created:** 2026-03-16 (Sprint 22, Day 11)
**Context:** 67 open issues in `docs/issues/`. This analysis identifies the highest-impact, lowest-effort issues to address in the remaining sprint days.

**Current Pipeline (Day 11):**
- Solve: 80/130, Match: 41/80
- path_syntax_error: 31, path_solve_terminated: 7, model_infeasible: 9 (excl. 4 permanent)
- Translation failures: 25 models
- Parse failures: 3 models (lexer_invalid_char — intractable)

---

## Priority Tiers

### Tier 1: Quick Wins (1-2h each, high confidence)

These are well-understood fixes with clear implementation paths and low regression risk.

| # | Issue | Models | Current Status | Fix | Est. |
|---|---|---|---|---|---|
| 1 | **#913** marco | marco | path_syntax_error | Deduplicate parameter data entries (last-write-wins) in emitter | 1h |
| 2 | **#917** ps10_s_mn/ps5_s_mn | ps10_s_mn, ps5_s_mn | path_syntax_error | Emit loop-initialized parameters with representative values | 1-2h |
| 3 | **#950** mathopt4 | mathopt4 | mismatch (but has compilation error) | Filter out `m.modelStat` references in emitter (model attribute not valid after MCP replacement) | 0.5h |
| 4 | **#934** indus | indus | translate_failure | Add line-breaking in GAMS emitter for equations exceeding GAMS line length limit | 1-2h |
| 5 | **#1080** multi-solve classification | senstran, apl1p, apl1pca, aircraft | mismatch (false) | Add `multi_solve` flag to pipeline; reclassify 4 models as incomparable (improves match rate metric) | 1h |
| 6 | **#914** markov | markov | path_syntax_error | Preserve computed parameter assignments with repeated index names in emitter | 1h |

**Tier 1 impact:** 8 models advanced (2 path_syntax_error fixed, 1 translation fixed, 1 compilation fixed, 4 reclassified). ~5-7h total.

---

### Tier 2: Moderate Wins (2-3h each, good confidence)

Shared root causes that unblock multiple models, or single-model fixes with clear paths.

| # | Issue | Models | Current Status | Fix | Est. |
|---|---|---|---|---|---|
| 7 | **#935-938** digamma derivative | mingamma, mlbeta, mlgamma, robustlp | translate_failure (3), model_infeasible (1) | Implement `digamma(x)` derivative rule for `loggamma(x)` and `gamma(x)` — series expansion or rational approximation | 2-3h |
| 8 | **#910** gussrisk | gussrisk | path_syntax_error | Detect GUSS dict set pattern; emit dotted labels as quoted strings | 1-2h |
| 9 | **#939** maxmin | maxmin | path_syntax_error | Debug smin AST representation for multi-index domains | 1-2h |
| 10 | **#983** elec | elec | path_solve_terminated | Propagate set-based dollar conditions to prevent division-by-zero in `1/distance` terms | 2-3h |
| 11 | **#862** sambal | sambal, qsambal | path_solve_terminated | Propagate dollar conditions from collapsed sum expressions through AD to stationarity | 2-3h |
| 12 | **#1071** hs62 | hs62 | model_infeasible | Detect `sqr(expr) = 0` constraints and reformulate as `expr = 0` (LICQ fix) | 2h |

**Tier 2 impact:** 10 models advanced (4 translation fixed, 3 path_syntax_error, 2 path_solve_terminated, 1 model_infeasible). ~12-16h total.

---

### Tier 3: Medium Effort, Single Model (3-5h each)

Worth doing if time permits, but lower ROI than Tier 1-2.

| # | Issue | Models | Current Status | Fix | Est. |
|---|---|---|---|---|---|
| 13 | **#906** twocge | twocge | path_solve_terminated | Fix table continuation parsing + post-solve code ordering + cross-index trade equations | 3-4h |
| 14 | **#1061** tforss | tforss | path_syntax_error | Detect loop-assigned scalars initialized to NA; emit concrete values | 2-3h |
| 15 | **#953** paperco | paperco | path_syntax_error | Extract loop body parameter assignments; emit representative scenario values | 2-3h |
| 16 | **#952** lmp2 | lmp2 | path_syntax_error | Extract loop body statements to populate dynamic subsets and parameters | 3-4h |
| 17 | **#827** gtm | gtm | path_syntax_error | Domain-validate zero-filled parameters; topological sort parameter assignments | 3h |
| 18 | **#1041** cesam2 | cesam2 | path_solve_terminated | Fix set assignment emission ordering for dynamic subsets | 3h |
| 19 | **#986** lands | lands | mismatch (execution error) | NA-aware equation conditioning (`$(param <> na)`) | 2-3h |
| 20 | **#918** qdemo7 | qdemo7 | mismatch | Detect variables with empty stationarity; emit .fx for inactive index subsets | 2-3h |

---

### Tier 4: High Effort or Low Impact (defer to Sprint 23)

| Issue(s) | Models | Why Defer |
|---|---|---|
| #926-933 Translation timeouts | dinam, egypt, ferts, ganges, gangesx, iswnm, nebrazil, tricp | LP-specific fast path is architectural; 6h+ |
| #885 sarf timeout | sarf | Combinatorial explosion; requires sparsity-aware Jacobian |
| #830 gastrans timeout | gastrans | Dynamic subset preservation; deep parser change |
| #871/#882 camcge | camcge | Multiple interacting bugs; subset conditioning + bound complementarity |
| #1038 spatequ | spatequ | Jacobian domain mismatch; deep KKT assembly fix |
| #1049 pak | pak | 3 interacting bugs across stationarity + AD |
| #970 twocge infeasible | twocge | Deep stationarity + initialization issues |
| #757 bearing | bearing | Requires variable scaling (.scale) support |
| #1070 prolog | prolog | CES singularity; fractional exponent numerical issues |
| #958-964 ps family mismatches | ps2_f_s, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps3_s_scp, ps10_s | Multi-solve warm-start infrastructure; 6h+ |
| #789 minmax reformulation | (test cases) | Fundamental formulation issue in objective min/max |
| #945 launch | launch | Per-instance stationarity consolidation; deep refactor |
| #956 nonsharp | nonsharp | 4 interacting bugs; high regression risk |
| #1089 qabel alias | qabel | Secondary issue deferred; nonconvex mismatch expected |
| #1068 agreste | agreste | Alias-aware sum differentiation; architectural change |
| #765 orani | orani | Permanently incompatible (linearized CGE) |
| #1081 sparta | sparta | Root cause not yet determined |
| #890 lop, #892 partssupply, #896 turkey | lop, partssupply, turkey | Parse errors (grammar additions needed); models may not advance past translation |
| #894 srkandw, #895 srpchase | srkandw, srpchase | Blocked by other parser issues (#975, #976) |
| #907 tforss (NA+KKT) | tforss | Multiple bugs; #1061 is simpler subset |
| #940 mexls | mexls | Universal set '*' support; architectural |
| #944 ps5_s_mn | ps5_s_mn | Multi-solve pattern incompatibility |
| #955 danwolfe | danwolfe | Async grid computing grammar; unrelated to NLP |
| #1030 unify parse | (code quality) | No model impact |
| #1062 tricp | tricp | 760 unmatched variables; deep domain conditioning |

---

## Recommended 2-Day Plan

### Day 12: Tier 1 Quick Wins (~5h)

| Priority | Issue | Models Fixed | Time |
|---|---|---|---|
| 1 | **#913** marco dedup | marco → solve | 1h |
| 2 | **#917** ps loop params | ps10_s_mn, ps5_s_mn → solve | 1.5h |
| 3 | **#950** mathopt4 modelStat | mathopt4 → solve/match | 0.5h |
| 4 | **#934** indus line-break | indus → translate | 1.5h |
| 5 | **#914** markov param | markov → solve | 1h |

**Expected outcome:** +5 models advancing (3 path_syntax_error → solve, 1 translate → solve, 1 mismatch → match)

### Day 13: Best of Tier 2 (~5h)

| Priority | Issue | Models Fixed | Time |
|---|---|---|---|
| 1 | **#935-938** digamma | mingamma, mlbeta, mlgamma → translate; robustlp → solve | 2.5h |
| 2 | **#1071** hs62 LICQ | hs62 → solve | 2h |
| 3 | **#910** gussrisk | gussrisk → solve | 1h |

**Expected outcome:** +5 models advancing (3 translate_failure → solve, 1 model_infeasible → solve, 1 path_syntax_error → solve)

### Total 2-Day Impact

| Metric | Day 11 | After 2 Days | Delta |
|---|---|---|---|
| Solve (est.) | 80 | ~88-90 | +8-10 |
| Match (est.) | 41 | ~44-46 | +3-5 |
| path_syntax_error | 31 | ~26 | -5 |
| model_infeasible | 9 | ~8 | -1 |
| Translation failures | 25 | ~21 | -4 |

---

## Issue-to-Model Cross-Reference

Models appearing in multiple issues (fix one, may partially fix another):
- **tforss**: #907 (full), #1061 (subset — NA scalar only)
- **camcge**: #871, #882 (both needed for full fix)
- **twocge**: #906, #970 (both needed; #906 is prerequisite)
- **ps5_s_mn**: #917, #944 (different root causes)
- **mingamma/mlbeta/mlgamma/robustlp**: #935-938 (shared digamma fix)
