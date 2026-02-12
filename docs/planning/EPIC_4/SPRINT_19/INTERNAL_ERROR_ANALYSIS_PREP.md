# Internal Error Analysis — Sprint 19 Prep Task 2

**Date:** 2026-02-12
**Branch:** `planning/sprint19-task2`
**Pipeline Data Version:** v1.1.0 (from `data/gamslib/gamslib_status.json`)
**Current Codebase Version:** v1.2.0

## Executive Summary

Of the **24 models** classified as `internal_error` in the v1.1.0 pipeline data, **21 now parse successfully** with the v1.2.0 codebase (Sprint 18 fixes). Only **3 models** still fail at the parse stage.

The `internal_error` classification was a catch-all bucket in `categorize_parse_error()` (`scripts/gamslib/error_taxonomy.py`) — it captured any error message that didn't match a specific pattern. The actual root causes fall into three distinct categories:

| Failure Category | Count | v1.2.0 Parse Status | Root Cause |
|---|---|---|---|
| No objective function | 12 | All 12 PASS | Post-parse validation error, not a parse failure |
| Circular dependency | 9 | All 9 PASS | Post-parse validation error, not a parse failure |
| Parser/semantic error | 3 | All 3 FAIL | Genuine parse-stage failures |
| **Total** | **24** | **21 pass, 3 fail** | |

**Key Finding:** The pipeline database is stale. Sprint 18 grammar and parser improvements silently resolved 21 of 24 `internal_error` models at the parse stage. A pipeline re-run is needed to update `gamslib_status.json`.

## Detailed Classification

### Category 1: No Objective Function (12 models)

These models parsed but failed `validate_model_structure()` in `src/validation/model.py:56` because they lack a standard objective function definition. The error was categorized as `internal_error` because `categorize_parse_error()` has no pattern for "no objective function" — this is actually a `model_no_objective_def` translation-stage category.

**All 12 now parse successfully with v1.2.0:**

| Model | v1.2.0 Parse | Vars | Eqs | Notes |
|---|---|---|---|---|
| camshape | PASS | 3 | 6 | Has vars/eqs — may have implicit objective |
| catmix | PASS | 0 | 0 | Loop-based/multi-solve model |
| chain | PASS | 3 | 3 | Has vars/eqs — may have implicit objective |
| danwolfe | PASS | 0 | 0 | Loop-based/multi-solve model |
| elec | PASS | 0 | 0 | Loop-based/multi-solve model |
| feasopt1 | PASS | 0 | 0 | Loop-based/multi-solve model |
| lnts | PASS | 4 | 4 | Has vars/eqs — may have implicit objective |
| partssupply | PASS | 0 | 0 | Loop-based/multi-solve model |
| polygon | PASS | 3 | 3 | Has vars/eqs — may have implicit objective |
| robot | PASS | 0 | 0 | Loop-based/multi-solve model |
| rocket | PASS | 8 | 6 | Has vars/eqs — may have implicit objective |
| srpchase | PASS | 0 | 0 | Loop-based/multi-solve model |

**Observations:**
- 5 models (camshape, chain, lnts, polygon, rocket) parse with non-zero vars/eqs — these have model content outside loops but may use non-standard objective patterns
- 7 models (catmix, danwolfe, elec, feasopt1, partssupply, robot, srpchase) parse with 0 vars/0 eqs — these likely define all model content inside loop blocks or use multi-solve patterns that the parser doesn't fully extract

**Sprint 19 Impact:** These models will encounter `model_no_objective_def` at the translation stage. Sprint 19 should decide whether to:
1. Support multi-solve/loop-based objective patterns
2. Accept these as out-of-scope (non-standard NLP patterns)

### Category 2: Circular Dependency (9 models)

These models parsed but failed `validate_circular_dependencies()` in `src/validation/model.py:212` because they have equations where variables define each other (e.g., `x = f(y), y = g(x)`). The error was categorized as `internal_error` because `categorize_parse_error()` has no pattern for "circular dependency".

**All 9 now parse successfully with v1.2.0:**

| Model | v1.2.0 Parse | Vars | Eqs | Circular Variables |
|---|---|---|---|---|
| chakra | PASS | 4 | 3 | y, k |
| dyncge | PASS | 31 | 29 | D, Z |
| glider | PASS | 13 | 12 | v_dot, vel |
| irscge | PASS | 25 | 25 | D, Z |
| lrgcge | PASS | 27 | 27 | D, Z |
| moncge | PASS | 26 | 26 | D, Z |
| quocge | PASS | 27 | 28 | D, Z |
| splcge | PASS | 7 | 7 | Z, F |
| twocge | PASS | 28 | 28 | D, Z |

**Observations:**
- 7 of 9 models are CGE (Computable General Equilibrium) models with D/Z circular dependencies — this is a well-known pattern in CGE modeling
- The circular dependency validation may be too strict for CGE models where simultaneous equation systems are expected
- All 9 have substantial vars/eqs, indicating they parse fully

**Sprint 19 Impact:** These models will encounter circular dependency validation at the translation stage. Sprint 19 should decide whether to:
1. Relax circular dependency validation for simultaneous equation systems
2. Add CGE-specific handling that tolerates known circular patterns

### Category 3: Parser/Semantic Errors (3 models — STILL FAILING)

These 3 models genuinely fail at the parse stage with v1.2.0. Each has a distinct root cause:

#### 3.1 gastrans — Index Count Mismatch

- **Error:** `ParseError: Parameter 'arep' expects 4 indices, got 2`
- **Location:** Line 114: `arep(aij,'lam') = lam(aij);`
- **Source:** `src/ir/parser.py:_handle_assign()` (line ~3282)
- **Root Cause:** The parameter `arep` is declared with 4 indices but the assignment uses only 2. This is valid GAMS (implicit index mapping) but our parser enforces strict index count matching.
- **Fix Complexity:** Medium — requires implementing GAMS implicit index mapping in assignment handling

#### 3.2 harker — Model Object Attribute Access

- **Error:** `ParserSemanticError: Symbol 'harkoli' not declared as a variable, parameter, equation, or model`
- **Location:** Line 183: `harkoli.objVal = 1;`
- **Source:** `src/ir/parser.py:_handle_assign()` (line ~3189)
- **Root Cause:** `harkoli` is a model name (from `Model harkoli /all/;`). The parser doesn't recognize model objects as valid targets for attribute access (`.objVal`). This is a GAMS model attribute access pattern.
- **Fix Complexity:** Low-Medium — requires recognizing model symbols in the symbol table and supporting `.objVal`, `.modelStat`, etc.

#### 3.3 mathopt4 — Unsupported attr_access Expression

- **Error:** `ParserSemanticError: Unsupported expression type: attr_access`
- **Location:** Line 49: `report('one','modelstat') = m.modelStat;`
- **Source:** `src/ir/parser.py:_expr()` (line ~3832)
- **Root Cause:** The expression `m.modelStat` uses model attribute access on the right-hand side of an assignment. The `_expr()` method doesn't support `attr_access` tree nodes.
- **Fix Complexity:** Low-Medium — same underlying issue as harker (model attribute access), just on the RHS instead of LHS

**Note:** harker and mathopt4 share the same root cause (model attribute access). Fixing this feature would resolve both models.

## Error Taxonomy Gap Analysis

The `categorize_parse_error()` function in `scripts/gamslib/error_taxonomy.py` has a classification gap: any error message that doesn't match a specific pattern falls through to `internal_error`. The 24 models expose two missing patterns:

| Error Pattern | Current Category | Correct Category | Correct Stage |
|---|---|---|---|
| "no objective function" | `internal_error` (parse) | `model_no_objective_def` | translate |
| "circular dependency" | `internal_error` (parse) | New: `validation_circular_dep` | validate |
| Index count mismatch | `internal_error` (parse) | `semantic_domain_error` | parse |
| Undeclared model symbol | `internal_error` (parse) | `semantic_undefined_symbol` | parse |
| Unsupported attr_access | `internal_error` (parse) | `parser_invalid_expression` | parse |

**Recommendation:** Update `categorize_parse_error()` to detect "no objective function" and "circular dependency" patterns, mapping them to appropriate categories. This would eliminate most of the `internal_error` bucket.

## Summary Statistics

### Original v1.1.0 Pipeline Classification
- **24 models** classified as `internal_error` at parse stage
- **0 models** tested at translate/solve stages (blocked by parse failure)

### Current v1.2.0 Re-analysis
- **21 models** (87.5%) now parse successfully — Sprint 18 fixes resolved these
- **3 models** (12.5%) still fail at parse stage
- **12 models** will encounter `model_no_objective_def` at translation
- **9 models** will encounter circular dependency validation at translation
- **2 of 3** remaining failures share the same root cause (model attribute access)

### Corrected Model Count
- The PROJECT_PLAN.md baseline assumed 23 `internal_error` models. The actual count is **24**.

## Actionable Recommendations for Sprint 19

1. **Re-run pipeline** with v1.2.0 to update `gamslib_status.json` — this will move 21 models out of `internal_error` and reveal their true translation-stage blockers
2. **Fix model attribute access** (harker + mathopt4) — medium effort, resolves 2 of 3 remaining parse failures
3. **Fix implicit index mapping** (gastrans) — medium effort, resolves 1 remaining parse failure
4. **Update error taxonomy** — add patterns for "no objective function" and "circular dependency" to prevent future `internal_error` misclassification
5. **Evaluate circular dependency tolerance** — determine if CGE models' simultaneous equation patterns should be supported

## Unknowns Verification

### Unknown 7.1: internal_error Failure Mode Distribution
- **Status:** VERIFIED
- **Finding:** 24 models (not 23) classified as `internal_error`. Distribution: 12 no-objective (50%), 9 circular-dependency (37.5%), 3 parser/semantic (12.5%). The `internal_error` bucket is primarily a categorization artifact — most errors have identifiable root causes.
- **Risk Assessment:** LOW — 87.5% of these models already parse with v1.2.0. Only 3 genuine parse failures remain.

### Unknown 7.2: internal_error Reclassification Feasibility
- **Status:** VERIFIED
- **Finding:** All 24 errors can be reclassified into specific categories. The `categorize_parse_error()` function needs 2 additional patterns ("no objective function" → `model_no_objective_def`, "circular dependency" → new category). The 3 remaining failures map to existing categories (`semantic_domain_error`, `semantic_undefined_symbol`, `parser_invalid_expression`).
- **Risk Assessment:** LOW — reclassification is straightforward. The taxonomy already has appropriate target categories for most cases.
