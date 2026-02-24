# Deferred Sprint 20 Issues Triage (13 Issues)

**Created:** 2026-02-24
**Sprint:** 21 (Priority 4 workstream)
**Budget:** 8-12h
**Status:** Triage complete, ready for Sprint 21 scheduling

---

## 1. Executive Summary

All 13 deferred Sprint 20 issues were reviewed against current pipeline status, Sprint 21 Priority 1-3 catalogs, and issue files. Of the 13 issues:

- **3 already resolved** (#763, #810, #835) — no Sprint 21 work needed
- **2 overlap with Priority 1** (#837, #840) — will be addressed by macro expansion work
- **2 overlap with Priority 3** (#810, #827) — partial benefit from path_syntax_error fixes
- **4 recommended for Sprint 21** (#789, #826, #828, #757) — tractable within budget
- **4 deferred to Sprint 22+** (#764, #765, #830, #827) — require architectural changes or are low leverage

Estimated Sprint 21 effort for recommended issues: **9-13h**. To stay within the 8-12h budget, treat #757 (2-3h) as a stretch/optional item.

---

## 2. Per-Issue Assessment

### 2.1 Issue #763: Chenery — AD Condition Propagation

| Field | Value |
|-------|-------|
| **Model** | chenery |
| **Issue File** | `docs/issues/completed/ISSUE_763_chenery-mcp-division-by-zero-del-parameter.md` |
| **Current Status** | **RESOLVED** — Fixed in Sprint 20 (PR merged) |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✓ Match ✓ |
| **Overlap** | None — already complete |
| **Recommendation** | **No action needed** |

**Notes:** The issue was division-by-zero from uninitialized calibration parameters. Fixed by adding transitive calibration closure and topological sorting of `.l` initialization. Chenery now solves with residual 3.98e-11.

---

### 2.2 Issue #764: Mexss — Accounting Variable Stationarity

| Field | Value |
|-------|-------|
| **Model** | mexss |
| **Issue File** | `docs/issues/ISSUE_764_mexss-mcp-locally-infeasible-accounting-variables.md` |
| **Current Status** | OPEN — requires refactoring `sameas` guard logic |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (locally infeasible) |
| **Overlap** | None — independent of Priorities 1-3 |
| **Est. Effort** | 8-12h (architectural: refactor `_add_indexed_jacobian_terms()` guard logic) |
| **Recommendation** | **Defer to Sprint 22+** |

**Notes:** The `sameas` guard in `_add_indexed_jacobian_terms()` incorrectly restricts scalar-constraint multiplier terms. This is an architectural refactor of the KKT assembly guard logic — too large for the deferred issues budget and doesn't overlap with other Sprint 21 work.

---

### 2.3 Issue #765: Orani — CGE Model Type Incompatible

| Field | Value |
|-------|-------|
| **Model** | orani |
| **Issue File** | `docs/issues/ISSUE_765_orani-mcp-locally-infeasible-fixed-variables-exogenous.md` |
| **Current Status** | OPEN — fundamental model class incompatibility |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (locally infeasible) |
| **Overlap** | None — independent of Priorities 1-3 |
| **Est. Effort** | Not fixable; requires model class detection and warning |
| **Recommendation** | **Defer to Sprint 22+** |

**Notes:** Orani is a linearized percentage-change CGE model with many exogenously fixed variables. Stationarity equations for fixed variables are structurally inconsistent. This model class is fundamentally incompatible with NLP→MCP conversion. The best approach is to detect this model class and emit a warning rather than attempting conversion.

---

### 2.4 Issue #757: Bearing — Non-convex Initialization

| Field | Value |
|-------|-------|
| **Model** | bearing |
| **Issue File** | `docs/issues/ISSUE_757_bearing-mcp-locally-infeasible.md` |
| **Current Status** | PARTIALLY RESOLVED — `.scale` emission added (#835), but PATH still locally infeasible |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (locally infeasible) |
| **Overlap** | Related to Sprint 20 Day 2-3 `.l` emission work |
| **Est. Effort** | 2-3h (investigate remaining infeasibility with `.scale` in place) |
| **Recommendation** | **Do in Sprint 21** |

**Notes:** Bearing is a non-convex NLP with bilinear terms and extreme coefficient variation (1e-6 to 1e8). Issue #835 (`.scale` emission) was resolved in Sprint 20 — emitter now outputs `.scale` attributes with `scaleOpt = 1`. However, bearing still fails. Remaining work: investigate whether `.l` initialization from the NLP solve improves PATH convergence. This is a good test case for validating Sprint 20's `.l` emission work.

---

### 2.5 Issue #810: LMP2 — Solve in Doubly-Nested Loop

| Field | Value |
|-------|-------|
| **Model** | lmp2 |
| **Issue File** | `docs/issues/completed/ISSUE_810_lmp2-solve-doubly-nested-loop.md` |
| **Current Status** | **RESOLVED** — Fixed in Sprint 20 (recursive extraction implemented) |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (path_syntax_error — Subcategory A: missing Table data) |
| **Overlap** | Resolved issue; remaining blocker addressed by Priority 3 Subcategory A |
| **Recommendation** | **No action needed** (remaining blocker is Table data, addressed by Priority 3) |

**Notes:** The doubly-nested loop solve extraction was fixed. LMP2 now reaches the solve stage but fails with GAMS $141 (missing Table data) — this is path_syntax_error Subcategory A, which will be addressed by Sprint 21 Priority 3 work.

---

### 2.6 Issue #826: Decomp — Empty Stationarity Equation

| Field | Value |
|-------|-------|
| **Model** | decomp |
| **Issue File** | `docs/issues/ISSUE_826_decomp-empty-stationarity-equation.md` |
| **Current Status** | OPEN — domain/subset index mismatch in stationarity builder |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (path_syntax_error) |
| **Overlap** | Independent — addresses a similar domain issue as Priority 3 Subcategory C but different root cause |
| **Est. Effort** | 3-4h (targeted fix: detect and handle empty stationarity equations) |
| **Recommendation** | **Do in Sprint 21** |

**Notes:** Variable `lam(ss)` declared over full set but equations access via dynamic subset `s(ss)`. Index replacement fails, producing empty stationarity equations. A pragmatic fix: detect empty stationarity equations post-generation and either eliminate them or add the variable to the objective function as a penalty. Both this issue and Priority 3 Subcategory C involve incorrect domain handling in stationarity generation, but the root causes differ: #826 is a dynamic subset mismatch while Subcategory C is an uncontrolled set issue.

---

### 2.7 Issue #827: GTM — Domain Violations from Zero-Fill

| Field | Value |
|-------|-------|
| **Model** | gtm |
| **Issue File** | `docs/issues/ISSUE_827_gtm-domain-violation-zero-fill.md` |
| **Current Status** | OPEN — parser zero-fills without domain validation |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (path_syntax_error — Subcategory B: domain violation) |
| **Overlap** | GTM is in Priority 3 Subcategory B (domain violation in emitted data) |
| **Est. Effort** | 6-8h (domain-aware zero-fill + topological sort for computed parameters) |
| **Recommendation** | **Defer to Sprint 22+** (high effort, partially addressed by Priority 3) |

**Notes:** GTM appears in path_syntax_error Subcategory B. The issue requires both domain-aware zero-filling in the parser and topological sorting for computed parameter assignments in the emitter. At 6-8h, this exceeds the budget for a single deferred issue. Priority 3 Subcategory B work (2-3h for emitter domain mapping) may partially address this, but the parser-side zero-fill fix is independent work.

---

### 2.8 Issue #828: IBM1 — Missing Bound Multipliers

| Field | Value |
|-------|-------|
| **Model** | ibm1 |
| **Issue File** | `docs/issues/ISSUE_828_ibm1-locally-infeasible-stationarity.md` |
| **Current Status** | OPEN — stationarity equations have nonzero cost constants |
| **Pipeline Status** | Parse ✓ Translate ✓ Solve ✗ (locally infeasible) |
| **Overlap** | None direct, but related to KKT bound handling |
| **Est. Effort** | 2-3h (investigate and fix bound resolution for parameter-assigned bounds) |
| **Recommendation** | **Do in Sprint 21** |

**Notes:** Stationarity equations contain nonzero cost constants (-0.03, -0.08, -0.17) suggesting that non-uniform upper bounds from parameter assignments (`x.up(s) = sup(s,"inventory")`) aren't correctly resolved during KKT generation. This is a focused debugging task: verify bound resolution at IR time and ensure per-instance bounds generate correct bound multipliers.

---

### 2.9 Issue #830: Gastrans — Jacobian Timeout (Dynamic Subset)

| Field | Value |
|-------|-------|
| **Model** | gastrans |
| **Issue File** | `docs/issues/ISSUE_830_gastrans-jacobian-dynamic-subset-timeout.md` |
| **Current Status** | OPEN — pipeline hangs during Jacobian computation (>60s) |
| **Pipeline Status** | Parse ✓ Translate ✗ (timeout) |
| **Overlap** | None — independent infrastructure issue |
| **Est. Effort** | 8-10h (dynamic subset member preservation + Jacobian sparsity) |
| **Recommendation** | **Defer to Sprint 22+** |

**Notes:** Dynamic subsets (`ap`, `as`, `aij`) have 0 static members in IR. Jacobian falls back to parent sets, causing combinatorial explosion: 24×20×20×7×7 = ~470,400 operations per equation. This is both a bug (IR doesn't preserve runtime-populated subset members) and a performance issue (Jacobian lacks sparsity optimization). At 8-10h, this exceeds the deferred issues budget. A quick mitigation (add Jacobian timeout with error message, ~1h) could be done as a quality-of-life improvement.

---

### 2.10 Issue #835: Bearing — .scale Emission

| Field | Value |
|-------|-------|
| **Model** | bearing |
| **Issue File** | `docs/issues/completed/ISSUE_835_bearing-scale-attribute-emission.md` |
| **Current Status** | **RESOLVED** — Fixed in Sprint 20 |
| **Pipeline Status** | (Same as #757 — bearing still locally infeasible) |
| **Overlap** | Merged with #757 assessment |
| **Recommendation** | **No action needed** |

**Notes:** `.scale` attribute emission was implemented: added `scale` field to `VariableDef`, parser stores `.scale` values, emitter outputs them with `scaleOpt = 1`. Bearing's remaining infeasibility is tracked under #757.

---

### 2.11 Issue #837: Springchain — Bracket Expr + Macro Expansion

| Field | Value |
|-------|-------|
| **Model** | springchain |
| **Issue File** | `docs/issues/ISSUE_837_springchain-bracket-expr-scalar-data.md` |
| **Current Status** | PARTIALLY RESOLVED — bracket expressions fixed; macro expansion OPEN |
| **Pipeline Status** | Parse ✗ (needs `$eval`/`$set`/`%macro%` expansion) |
| **Overlap** | **Full overlap with Priority 1** (macro/preprocessor expansion) |
| **Est. Effort** | 0h additional (addressed by Priority 1) |
| **Recommendation** | **Addressed by Priority 1 — no separate Sprint 21 work needed** |

**Notes:** Bracket expression support was added in Sprint 20. The remaining blocker is `$eval`/`$set`/`%macro%` expansion, which is exactly Sprint 21 Priority 1 (macro expansion). Related completed issue: #841 (springchain eval-set macro expansion). This will be resolved as part of Priority 1 work.

---

### 2.12 Issue #840: Saras — `%system.nlp%` System Macro

| Field | Value |
|-------|-------|
| **Model** | saras |
| **Issue File** | `docs/issues/ISSUE_840_saras-system-nlp-macro.md` |
| **Current Status** | OPEN — preprocessor doesn't expand `%system.*%` macros |
| **Pipeline Status** | Parse ✗ (lexer error from unexpanded `%` character) |
| **Overlap** | **Full overlap with Priority 1** (macro/preprocessor expansion) |
| **Est. Effort** | 0h additional (addressed by Priority 1) |
| **Recommendation** | **Addressed by Priority 1 — no separate Sprint 21 work needed** |

**Notes:** `%system.nlp%` is a GAMS system macro that resolves to the default NLP solver name. This is a subset of the general `%macro%` expansion work planned for Priority 1. Related completed issue: #836 (saras orphan bracket offtext). Once Priority 1 implements `%system.*%` macro expansion, saras should parse.

---

### 2.13 Issue #789: Min/Max in Objective Equations

| Field | Value |
|-------|-------|
| **Model** | (general — affects any model with min/max in objective) |
| **Issue File** | `docs/issues/ISSUE_789_minmax-reformulation-spurious-variables.md` |
| **Current Status** | PARTIALLY FIXED — spurious lambda variables removed; mathematical infeasibility for min/max in objective-defining equations remains |
| **Pipeline Status** | N/A (affects reformulation stage) |
| **Overlap** | None direct |
| **Est. Effort** | 2-3h (targeted fix: bypass epigraph reformulation for objective-defining min/max) |
| **Recommendation** | **Do in Sprint 21** |

**Notes:** The structural bug (spurious lambda variables) was fixed. The remaining issue is mathematical: when min/max defines the objective variable (`minimize z` where `z = min(x,y)`), the epigraph reformulation produces infeasible KKT conditions (`λ₀ + λ₁ = ν = -1` where λ ≥ 0). Fix: detect when min/max defines the objective and use direct constraints (`z ≤ x, z ≤ y`) instead of the auxiliary variable approach. This is a focused fix in `src/kkt/reformulation.py`.

---

## 3. Overlap Map

### Priority 1 (Macro/Preprocessor Expansion) Overlaps

| Deferred Issue | Model | Overlap Type | Notes |
|---------------|-------|-------------|-------|
| #837 | springchain | **Full** | Needs `$eval`/`$set`/`%macro%` expansion |
| #840 | saras | **Full** | Needs `%system.nlp%` expansion |

### Priority 2 (Internal Error Fixes) Overlaps

| Deferred Issue | Model | Overlap Type | Notes |
|---------------|-------|-------------|-------|
| (none) | — | — | No deferred issue models appear in the 7 internal_error models |

### Priority 3 (Path Syntax Error Fixes) Overlaps

| Deferred Issue | Model | Overlap Type | Notes |
|---------------|-------|-------------|-------|
| #810 | lmp2 | **Partial** | LMP2 in Subcategory A (missing Table data); issue itself resolved |
| #827 | gtm | **Partial** | GTM in Subcategory B (domain violation); separate root cause |

### No Overlap (Independent)

| Deferred Issue | Model | Notes |
|---------------|-------|-------|
| #764 | mexss | KKT guard logic refactor |
| #765 | orani | Model class incompatibility |
| #757 | bearing | Solver convergence |
| #826 | decomp | Empty stationarity (related domain issue) |
| #828 | ibm1 | Bound multiplier resolution |
| #830 | gastrans | Dynamic subset Jacobian |
| #789 | (general) | Min/max reformulation |

---

## 4. Recommended Sprint 21 Plan

### Do in Sprint 21 (4 issues, 9-13h)

| Priority | Issue | Model | Effort | Rationale |
|----------|-------|-------|--------|-----------|
| 1 | #789 | (general) | 2-3h | Fixes min/max reformulation for all affected models |
| 2 | #828 | ibm1 | 2-3h | Focused debugging of bound resolution |
| 3 | #826 | decomp | 3-4h | Independent of Priority 3; complements stationarity domain work |
| 4 | #757 | bearing | 2-3h | Validates Sprint 20 `.l`/`.scale` emission work |

**Total: 9-13h** (slightly above 8-12h budget; #757 can be dropped if time is tight)

### Already Resolved (3 issues, 0h)

| Issue | Model | Status |
|-------|-------|--------|
| #763 | chenery | Fixed in Sprint 20 |
| #810 | lmp2 | Fixed in Sprint 20 (remaining blocker is Priority 3) |
| #835 | bearing | Fixed in Sprint 20 (merged with #757) |

### Addressed by Priority 1 (2 issues, 0h additional)

| Issue | Model | Status |
|-------|-------|--------|
| #837 | springchain | Will be resolved by macro expansion work |
| #840 | saras | Will be resolved by `%system.*%` expansion work |

### Defer to Sprint 22+ (4 issues)

| Issue | Model | Reason |
|-------|-------|--------|
| #764 | mexss | 8-12h architectural refactor of KKT guard logic |
| #765 | orani | Fundamental model class incompatibility; needs detection/warning |
| #827 | gtm | 6-8h; partially addressed by Priority 3 Subcategory B |
| #830 | gastrans | 8-10h; requires dynamic subset infrastructure + Jacobian sparsity |

---

## 5. Quick Wins (Optional, 1-2h)

If time permits within the Sprint 21 budget, these small improvements are worthwhile:

1. **Gastrans Jacobian timeout** (~1h): Add a configurable iteration limit to `compute_constraint_jacobian()` with a clear error message, preventing silent hangs
2. **Orani model class detection** (~1h): Add a warning when a model has >50% fixed variables, suggesting it may not be suitable for NLP→MCP conversion

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| #789 fix introduces regressions in non-objective min/max | Medium | High | Keep existing epigraph reformulation for non-objective cases; only change objective-defining case |
| #828 bound investigation reveals deeper KKT issue | Medium | Medium | Time-box to 3h; defer if root cause is architectural |
| #826 empty stationarity fix is insufficient | Low | Medium | Post-generation detection catches all empty equations regardless of cause |
| #757 bearing remains infeasible after investigation | High | Low | Document findings for Sprint 22; bearing is known-difficult non-convex model |
| Priority 1 doesn't fully resolve #837/#840 | Low | Medium | Partial macro support may still leave some patterns unhandled |
