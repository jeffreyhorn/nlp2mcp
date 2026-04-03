# Alias Differentiation Root Cause Analysis

**Created:** 2026-04-03
**Sprint:** 24 (Prep Task 2)
**Issues Analyzed:** #1137-#1147, #1150 (12 issues, 17 models)

---

## Executive Summary

All 12 alias-differentiation issues were classified into 5 root cause patterns. The dominant pattern (A: summation index not tracked) accounts for 5 of 12 issues and ~14 models. The Sprint 23 design document's `bound_indices` mechanism directly addresses Patterns A-C. Patterns D and E require separate fixes. Regression risk is very low — only 8 of 49 matching models use aliases (16.3%), and the `bound_indices` guard specifically prevents the known regression vector, and the `bound_indices` guard specifically prevents the Sprint 22 dispatch regression.

**Key Finding:** A single architectural change (summation-context tracking via `bound_indices` in `_diff_varref`) addresses 8-9 of 12 issues. 2 issues (#1144, #1147) are non-differentiation bugs requiring separate fixes.

---

## Pattern Classification

### Pattern A: Summation Index Not Tracked Through Derivative Chain

**Issues:** #1137 (qabel/abel), #1138 (CGE models), #1139 (meanvar), #1140 (PS-family), #1145 (cclinpts)
**Models:** ~14 (qabel, abel, irscge, lrgcge, moncge, stdcge, meanvar, ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps5_s_mn, ps10_s_mn, cclinpts)
**Fix Success Estimate:** 75-85%

**Root Cause:** `_diff_varref()` in `src/ad/derivative_rules.py` uses exact index-tuple matching. When differentiating `x(np, k)` w.r.t. `x(n, k)` where `Alias(n, np)`, the function returns 0 because `('np', 'k') != ('n', 'k')`. The correct result is `sameas(np, n)` — a guard that GAMS evaluates at runtime.

**Evidence:**
- qabel: Cross-terms present but missing alias guards in stationarity
- irscge: CES derivatives mostly correct; fine-tuning needed on multi-level aliases
- meanvar: Quadratic form shows renamed aliases but cross-diagonal terms incomplete

**Fix:** Add `_alias_match()` helper that checks alias relationships and returns `sameas()` guards. Thread `bound_indices` through the derivative chain to prevent matching bound summation variables (the Sprint 22 dispatch regression).

### Pattern B: Alias-to-Root-Set Mapping Fails in Jacobian Construction

**Issues:** #1141 (kand)
**Models:** kand (92.5% mismatch)
**Fix Success Estimate:** 55%

**Root Cause:** kand uses a tree structure with `Alias(n, nn)` where the element-to-set mapping produces flat assignments insufficient for tree traversal. The Jacobian builder's `element_to_set` mapping doesn't handle hierarchical alias relationships.

**Evidence:**
- kand stationarity equations show significant structural differences from expected KKT
- The tree structure means aliases appear at multiple nesting levels

**Fix:** The basic `_alias_match()` fix should help, but may need enhancement for multi-level nesting. Post-implementation investigation recommended.

### Pattern C: Offset + Alias Interaction

**Issues:** #1143 (polygon), #1146 (himmel16)
**Models:** polygon (100% mismatch), himmel16 (43% mismatch)
**Fix Success Estimate:** 55-65%

**Root Cause:** When aliases interact with IndexOffset (e.g., `sum(j(i+1), r(i+1)*r(i)*...)`), the offset is applied to an alias index, creating a compound expression that the current derivative chain cannot resolve. polygon shows complete gradient failure (MCP objective = 0.0 vs NLP 0.78).

**Evidence:**
- polygon stationarity has `theta(i1+1)` and `r(i1+1)` — concrete element offsets instead of symbolic
- himmel16 has circular offset (`++`) interaction with aliases

**Fix:** The `_alias_match()` helper needs to extract `IndexOffset.base` for comparison and generate appropriate offset guards. This is the highest-risk pattern — the design addresses it but implementation requires careful offset handling.

### Pattern D: Condition-Scope Shadowing in Dollar Conditionals

**Issues:** #1142 (launch)
**Models:** launch (17.4% mismatch)
**Fix Success Estimate:** 50%

**Root Cause:** launch uses alias substitution in ordinal conditions like `$(ge(ss,s))` where the alias scope interacts with dollar-condition propagation. The derivative chain doesn't properly scope aliases within conditional guards.

**Evidence:**
- launch stationarity shows conditional alias references that shadow outer scope

**Fix:** Partially addressed by `_alias_match()` with bound_indices, but condition-scope interaction may need separate attention. This is orthogonal to the main alias fix.

### Pattern E: Non-Differentiation Issues

**Issues:** #1144 (catmix), #1147 (camshape)
**Models:** catmix (model_infeasible), camshape (compilation error)
**Fix Success Estimate:** 0% from alias fix alone

**Root Cause:**
- **catmix (#1144):** Pre-existing domain inference bug in the IR — aliases cause incorrect domain assignment. Not a derivative issue.
- **camshape (#1147):** Malformed alias emission in the stationarity builder — `_collect_ad_generated_aliases` produces invalid GAMS syntax. Debugging needed in emitter, not AD.

**Fix:** Both require separate targeted fixes unrelated to the summation-context tracking design.

---

## Classification Table

| Issue | Model(s) | Pattern | Rel. Diff | Fix Prob. | Effort |
|-------|----------|---------|-----------|-----------|--------|
| #1137 | qabel, abel | A | 29.8% | 85% | Included in main fix |
| #1138 | irscge, lrgcge, moncge, stdcge | A | 1.0-2.2% | 80% | Included in main fix |
| #1139 | meanvar | A | 12.3% | 75% | Included in main fix |
| #1140 | ps2_s, ps3_s, ps3_s_gic, ps3_s_mn, ps5_s_mn, ps10_s_mn | A | 0.5-27% | 75% | Included in main fix |
| #1141 | kand | B | 92.5% | 55% | +2h post-investigation |
| #1142 | launch | D | 17.4% | 50% | +2h post-investigation |
| #1143 | polygon | C | 100% | 65% | Included but high risk |
| #1144 | catmix | E | N/A (infeasible) | 0% | Separate IR fix |
| #1145 | cclinpts | A | 69.9% | 60% | Included in main fix |
| #1146 | himmel16 | C | 43.0% | 55% | Included but edge case |
| #1147 | camshape | E | N/A (syntax err) | 5% | Separate emitter fix |
| #1150 | (AD regression) | A | N/A | 80% | Included in main fix |

---

## Effort Estimate Per Pattern

| Pattern | Fix Approach | Estimated Effort | Models Affected |
|---------|-------------|-----------------|-----------------|
| A: Summation index | `_alias_match()` + `bound_indices` threading | 8-10h | ~14 models |
| B: Root-set mapping | Post-implementation investigation | +2h | 1 model |
| C: Offset-alias | `IndexOffset.base` extraction in `_alias_match()` | Included in A | 2 models |
| D: Condition-scope | Post-implementation investigation | +2h | 1 model |
| E: Non-differentiation | Separate PRs | 3-4h each | 2 models |

**Total for main fix (Patterns A-C):** 8-10h
**Total including post-investigation (B, D):** 12-14h
**Separate fixes (E):** 6-8h (not in main fix scope)

---

## Regression Risk Assessment

### Matching Models Using Aliases

Of 49 currently-matching models, **8 use aliases** (16.3%):
- dispatch, gussrisk, nemhaus, ps2_f, ps3_f, quocge, ship, splcge

**dispatch is the critical regression canary:**
- Uses `Alias(i,j)` with `sum((i,j), p(i)*b(i,j)*p(j))`
- Sprint 22 naive fix broke this because `j` incorrectly matched `i`
- The `bound_indices` mechanism specifically prevents this: when `j` is bound (sum variable), no alias match is generated

### Risk Level: VERY LOW

- **41 non-alias matching models:** Zero risk — alias code path unreachable
- **8 alias matching models:** Protected by `bound_indices` guard
- **dispatch test:** Must pass FIRST before any further testing

### Recommended Regression Test Strategy

1. **Canary test:** dispatch must match before/after
2. **Golden-file comparison:** Generate stationarity output for all 49 matching models before the fix
3. **Full pipeline:** Run all 86 solving models after the fix
4. **Per-pattern tests:** Unit tests for each pattern's alias matching behavior

---

## Implementation Recommendations

1. **Start with helpers** (`_alias_match`, `_same_root_set`) — unit-testable in isolation
2. **Thread `bound_indices`** through `_diff_sum` → `_diff_varref` chain
3. **Run dispatch regression** immediately after enabling alias matching
4. **Test Pattern A models** (qabel, irscge, meanvar) as first validation
5. **Test Pattern C models** (polygon) as risk validation
6. **Post-implementation:** Investigate kand (B) and launch (D) if they don't improve
7. **Separate PRs:** catmix (#1144) and camshape (#1147) are not alias-differentiation fixes
