# Sprint 17 Translation Deep Dive

**Created:** January 28, 2026  
**Sprint:** 17 Prep - Task 3  
**Status:** Complete  
**Purpose:** Detailed analysis of 27 translation failures to identify root causes and prioritize fixes

---

## Executive Summary

This document provides a comprehensive analysis of all 27 translation failures from Sprint 16 baseline. The analysis categorizes errors by root cause, identifies code locations for fixes, and provides prioritized recommendations for Sprint 17.

**Sprint 16 Translation Baseline:**
| Metric | Value |
|--------|-------|
| Models Attempted | 48 (successfully parsed) |
| Translation Success | 21 (43.8%) |
| Translation Failure | 27 (56.2%) |

**Error Category Distribution:**
| Category | Count | % of Failures | Fix Location |
|----------|-------|---------------|--------------|
| `model_domain_mismatch` | 6 | 22.2% | `src/kkt/stationarity.py` |
| `diff_unsupported_func` | 6 | 22.2% | `src/ad/derivative_rules.py` |
| `model_no_objective_def` | 5 | 18.5% | `src/ad/gradient.py` |
| `unsup_index_offset` | 4 | 14.8% | `src/ir/ast.py` |
| `internal_error` | 3 | 11.1% | Various |
| `codegen_numerical_error` | 3 | 11.1% | `src/validation/numerical.py` |

**Key Findings:**
1. **AD Module Gaps:** 6 models fail due to missing derivative rules (gamma, card, ord, smin, loggamma)
2. **Domain Tracking:** 6 models fail due to incompatible index domains during KKT construction
3. **Objective Handling:** 5 models lack explicit objective-defining equations
4. **Index Arithmetic:** 4 models use lead/lag indexing (t-1, t+1) not yet supported

**Estimated Fix Impact:**
- Quick Wins (P1): 8-11 models fixable with ~10h effort
- Medium Effort (P2): 6-10 models fixable with ~14h additional effort
- Total Potential: 60-75% translation success rate achievable

---

## Table of Contents

1. [Error Category Analysis](#1-error-category-analysis)
2. [Model-Level Details](#2-model-level-details)
3. [Root Cause Summary](#3-root-cause-summary)
4. [Fix Prioritization](#4-fix-prioritization)
5. [Quick Wins](#5-quick-wins)
6. [Unknown Verification Summary](#6-unknown-verification-summary)

---

## 1. Error Category Analysis

### 1.1 diff_unsupported_func (6 models)

**Root Cause:** The AD module lacks derivative rules for certain GAMS intrinsic functions.

**Code Location:** `src/ad/derivative_rules.py` lines 540-570

**Currently Supported Functions:**
- power, exp, log, log10, log2, sqrt, sqr
- sin, cos, tan
- abs (with --smooth-abs flag)

**Missing Functions Found:**

| Function | Models Affected | Derivative Formula | Complexity |
|----------|-----------------|-------------------|------------|
| `gamma` | aircraft, orani | ψ(x)·Γ(x) where ψ is digamma | High - requires digamma |
| `loggamma` | mingamma | ψ(x) (digamma function) | High - requires digamma |
| `card` | hydro | Non-differentiable (set cardinality) | N/A - not differentiable |
| `ord` | markov | Non-differentiable (element position) | N/A - not differentiable |
| `smin` | maxmin | Smooth approximation needed | Medium - LogSumExp trick |

**Affected Models:**
1. **aircraft** (LP): Uses `gamma()` function
2. **hydro** (NLP): Uses `card()` - set cardinality (non-differentiable)
3. **markov** (LP): Uses `ord()` - element ordinal (non-differentiable)
4. **maxmin** (NLP): Uses `smin()` - smooth minimum
5. **mingamma** (NLP): Uses `loggamma()` - log of gamma function
6. **orani** (LP): Uses `gamma()` function

**Fix Strategy:**
- **Differentiable functions (gamma, loggamma, smin):** Add derivative rules to AD module
- **Non-differentiable functions (card, ord):** These are structural and cannot be differentiated; models using them for optimization may need reformulation or exclusion

**Effort Estimate:** 
- gamma/loggamma: 4h (need digamma implementation or library)
- smin: 2h (LogSumExp approximation)
- card/ord: Cannot fix - mark as known limitation

---

### 1.2 model_domain_mismatch (6 models)

**Root Cause:** Variable indices don't align with multiplier indices during KKT stationarity equation construction.

**Code Location:** `src/kkt/stationarity.py` lines 613-627

**Error Pattern:**
```
Incompatible domains for summation: variable domain ('m', 'k'), 
multiplier domain ('n', 'k'). Multiplier domain must be either 
a subset of variable domain or completely disjoint.
```

**Affected Models:**

| Model | Type | Variable Domain | Multiplier Domain | Pattern |
|-------|------|-----------------|-------------------|---------|
| abel | NLP | ('m', 'k') | ('n', 'k') | Partial overlap |
| himmel16 | NLP | ('i',) | ('i', 'j') | Superset multiplier |
| mexss | LP | ('c', 'i') | ('c', 'j') | Partial overlap |
| pak | LP | ('te',) | ('te', 'tf') | Superset multiplier |
| qabel | QCP | ('m', 'k') | ('n', 'k') | Partial overlap (same as abel) |
| robert | LP | ('p', 'tt') | ('p', 'tf') | Partial overlap |

**Root Cause Analysis:**
The domain validation in `stationarity.py` requires that multiplier domains be either:
1. A **subset** of variable domains, OR
2. **Completely disjoint** from variable domains

When domains partially overlap (e.g., both share 'k' but differ in 'm' vs 'n'), the current logic rejects them.

**Fix Strategy:**
1. **Option A - Improve domain alignment:** Enhance the KKT builder to handle partial overlaps by introducing intermediate summation indices
2. **Option B - Earlier detection:** Move domain validation to parsing/IR construction for better error messages
3. **Option C - Explicit index mapping:** Allow user hints for how to align domains

**Effort Estimate:** 6h (requires careful analysis of index semantics)

---

### 1.3 model_no_objective_def (5 models)

**Root Cause:** The objective variable is declared but no equation explicitly defines its value.

**Code Location:** 
- Error raised: `src/ad/gradient.py` lines 142-146
- Extraction attempted: `src/ir/normalize.py` lines 39-72

**Error Pattern:**
```
Objective variable 'f' is not defined by any equation. 
ObjectiveIR.expr is None and no defining equation found.
Available equations: ['objective', 'alkylshrnk', 'acidbal', ...]
```

**Affected Models:**

| Model | Type | Objective Var | Available Equations | Pattern |
|-------|------|---------------|---------------------|---------|
| alkyl | NLP | f | objective, alkylshrnk, acidbal, ... | Has 'objective' eq but not defining |
| bearing | NLP | pl | power_loss, pumping_energy, ... | Has related eq but different name |
| circle | NLP | r | enclosing | No defining equation |
| cpack | QCP | r | packing, enclosing | No defining equation |
| trussm | QCP | tau | stress, displacement, ... | No defining equation |

**Root Cause Analysis:**
These models have MINIMIZE/MAXIMIZE statements but the objective variable isn't defined by an equation of the form `objvar =e= expression`. The current extraction logic in `normalize.py` looks for:
1. `objvar =e= expr` (objective on LHS)
2. `expr =e= objvar` (objective on RHS)

Some models use indirect definitions or the objective is implicit.

**Fix Strategy:**
1. **Option A - Feasibility reformulation:** Add `minimize 0` or similar dummy objective for CNS-style problems
2. **Option B - Enhanced extraction:** Look for equations where objective variable appears and extract expression
3. **Option C - GAMS-style handling:** Research how GAMS CNS model type works and replicate

**Effort Estimate:** 4h (option B is most promising)

---

### 1.4 unsup_index_offset (4 models)

**Root Cause:** Lead/lag index operations (e.g., `X(t-1)`, `A(t+1)`) are not yet implemented in the IR.

**Code Location:** `src/ir/ast.py` lines 50, 71, 97, 119

**Error Pattern:**
```
IndexOffset not yet supported in this context: 
IndexOffset(base='t', offset=Unary(-, SymbolRef(-)), circular=False)
```

**Affected Models:**

| Model | Type | Index Pattern | Context |
|-------|------|---------------|---------|
| jobt | LP | t-1 | Time lag in equation |
| like | NLP | g+ | Lead operator (positive offset) |
| ramsey | NLP | t+ | Lead operator |
| whouse | LP | t-1 | Time lag in warehouse model |

**Root Cause Analysis:**
The parser correctly creates `IndexOffset` AST nodes, but downstream processing in `ast.py` raises `NotImplementedError` when trying to:
1. Extract indices from expressions
2. Evaluate domain membership
3. Generate GAMS code

**Fix Strategy:**
1. **Implement IndexOffset handling** in key AST visitor methods
2. **Handle in code generation:** Translate `X(t-1)` to proper GAMS syntax
3. **Handle in derivatives:** `∂/∂X(t) of X(t-1) = 0` when indices differ

**Effort Estimate:** 8h (significant IR changes needed)

---

### 1.5 internal_error (3 models)

**Root Cause:** Various internal errors during translation.

**Affected Models:**

| Model | Type | Error | Root Cause |
|-------|------|-------|------------|
| cclinpts | NLP | Unsupported unary operation 'not' | Boolean `not` in expression |
| chenery | NLP | Set element 'food+agr' invalid | Plus sign in set element name |
| pollut | NLP | Set element 'pulp+paper' invalid | Plus sign in set element name |

**Analysis:**

1. **cclinpts:** Uses boolean `not` operation which the AD module doesn't support for differentiation (correctly - boolean operations aren't differentiable)

2. **chenery/pollut:** Set elements contain `+` character which violates identifier rules. This is a GAMS syntax that our parser/IR doesn't support.

**Fix Strategy:**
- **cclinpts:** Cannot differentiate boolean expressions - mark as limitation
- **chenery/pollut:** Either sanitize set element names or extend validation rules

**Effort Estimate:** 2h (for set element sanitization)

---

### 1.6 codegen_numerical_error (3 models)

**Root Cause:** Parameter values contain invalid numbers (±Inf, NaN).

**Code Location:** `src/validation/numerical.py` line 35

**Affected Models:**

| Model | Type | Parameter | Invalid Value | Cause |
|-------|------|-----------|---------------|-------|
| decomp | LP | rep[2,gap] | +Inf | Likely division by zero in data |
| gastrans | NLP | Ndata[Antwerpen,slo] | -Inf | Likely log of zero or negative |
| ibm1 | LP | bspec[aluminum,maximum] | +Inf | Likely uninitialized parameter |

**Root Cause Analysis:**
These are model data issues, not nlp2mcp bugs. The models contain parameter calculations that produce infinite or undefined values.

**Fix Strategy:**
1. **Better error messages:** Report which GAMS line caused the invalid value
2. **Skip affected models:** These are fundamentally broken models
3. **Optional bounds checking:** Add configurable parameter validation

**Effort Estimate:** 1h (improved error reporting only)

---

## 2. Model-Level Details

### Complete Model List by Category

#### diff_unsupported_func (6 models)
| Model | Type | Function | Differentiable? | Fix Path |
|-------|------|----------|-----------------|----------|
| aircraft | LP | gamma | Yes (digamma) | Add rule |
| hydro | NLP | card | No | Limitation |
| markov | LP | ord | No | Limitation |
| maxmin | NLP | smin | Yes (smooth) | Add rule |
| mingamma | NLP | loggamma | Yes (digamma) | Add rule |
| orani | LP | gamma | Yes (digamma) | Add rule |

#### model_domain_mismatch (6 models)
| Model | Type | Var Domain | Mult Domain | Fix Complexity |
|-------|------|------------|-------------|----------------|
| abel | NLP | (m,k) | (n,k) | High |
| himmel16 | NLP | (i,) | (i,j) | Medium |
| mexss | LP | (c,i) | (c,j) | High |
| pak | LP | (te,) | (te,tf) | Medium |
| qabel | QCP | (m,k) | (n,k) | High |
| robert | LP | (p,tt) | (p,tf) | High |

#### model_no_objective_def (5 models)
| Model | Type | Obj Var | Pattern | Fix Complexity |
|-------|------|---------|---------|----------------|
| alkyl | NLP | f | Has 'objective' eq | Low |
| bearing | NLP | pl | Has related eq | Low |
| circle | NLP | r | Feasibility | Medium |
| cpack | QCP | r | Feasibility | Medium |
| trussm | QCP | tau | Feasibility | Medium |

#### unsup_index_offset (4 models)
| Model | Type | Offset | Pattern | Fix Complexity |
|-------|------|--------|---------|----------------|
| jobt | LP | t-1 | Lag | High |
| like | NLP | g+ | Lead | High |
| ramsey | NLP | t+ | Lead | High |
| whouse | LP | t-1 | Lag | High |

#### internal_error (3 models)
| Model | Type | Error | Fixable? |
|-------|------|-------|----------|
| cclinpts | NLP | 'not' operation | No |
| chenery | NLP | 'food+agr' element | Maybe |
| pollut | NLP | 'pulp+paper' element | Maybe |

#### codegen_numerical_error (3 models)
| Model | Type | Parameter | Value | Fixable? |
|-------|------|-----------|-------|----------|
| decomp | LP | rep[2,gap] | +Inf | No (data issue) |
| gastrans | NLP | Ndata[...] | -Inf | No (data issue) |
| ibm1 | LP | bspec[...] | +Inf | No (data issue) |

---

## 3. Root Cause Summary

### By Code Location

| Location | Category | Models | Fix Type |
|----------|----------|--------|----------|
| `src/ad/derivative_rules.py` | diff_unsupported_func | 6 | Add derivative rules |
| `src/kkt/stationarity.py` | model_domain_mismatch | 6 | Improve domain handling |
| `src/ad/gradient.py` | model_no_objective_def | 5 | Enhance objective extraction |
| `src/ir/ast.py` | unsup_index_offset | 4 | Implement IndexOffset |
| Various | internal_error | 3 | Case-by-case |
| Model data | codegen_numerical_error | 3 | Not fixable |

### By Fixability

| Fixability | Models | Categories |
|------------|--------|------------|
| Fixable (AD rules) | 4 | gamma, loggamma, smin |
| Fixable (code changes) | 11 | domain, objective, set elements |
| Requires IR redesign | 4 | index offset |
| Not differentiable | 2 | card, ord |
| Model data issues | 3 | numerical errors |
| Boolean logic | 1 | 'not' operation |

---

## 4. Fix Prioritization

### Priority Matrix

| Priority | Fix | Effort | Models | ROI (Models/Hour) |
|----------|-----|--------|--------|-------------------|
| P1 | Objective extraction enhancement | 4h | 5 | 1.25 |
| P1 | gamma/loggamma derivative rules | 4h | 3 | 0.75 |
| P1 | smin smooth approximation | 2h | 1 | 0.50 |
| P2 | Domain mismatch handling | 6h | 6 | 1.00 |
| P2 | Set element sanitization | 2h | 2 | 1.00 |
| P3 | IndexOffset support | 8h | 4 | 0.50 |
| -- | card/ord (not differentiable) | -- | 2 | N/A |
| -- | Numerical errors (data issues) | -- | 3 | N/A |
| -- | Boolean 'not' (not differentiable) | -- | 1 | N/A |

### Recommended Sprint 17 Order

**Phase 1: Quick Wins (10h, +9 models)**
1. Objective extraction enhancement - 4h, +5 models
2. gamma/loggamma derivatives - 4h, +3 models  
3. smin smooth approximation - 2h, +1 model

**Phase 2: Medium Effort (8h, +8 models)**
1. Domain mismatch handling - 6h, +6 models
2. Set element sanitization - 2h, +2 models

**Phase 3: Higher Effort (8h, +4 models)**
1. IndexOffset support - 8h, +4 models

**Not Addressed (6 models):**
- card/ord functions: 2 models (non-differentiable)
- Numerical errors: 3 models (model data issues)
- Boolean 'not': 1 model (non-differentiable)

---

## 5. Quick Wins

### Highest ROI Fixes

| Fix | Effort | Models Fixed | Implementation Notes |
|-----|--------|--------------|---------------------|
| **Objective extraction** | 4h | 5 | Enhance `find_objective_expression()` to search for any equation containing objective variable |
| **gamma derivative** | 3h | 3 | Add `_diff_gamma()` using digamma: d/dx Γ(x) = Γ(x)·ψ(x) |
| **smin approximation** | 2h | 1 | Use LogSumExp: smin(a,b) ≈ -log(exp(-a/τ) + exp(-b/τ))·τ |
| **Set element fix** | 2h | 2 | Sanitize or allow '+' in set element names |

### Expected Outcome After Quick Wins

| Metric | Before | After Quick Wins | Change |
|--------|--------|------------------|--------|
| Translation Success | 21/48 (43.8%) | 32/48 (66.7%) | +11 models |
| Translation Failure | 27 | 16 | -11 models |

---

## 6. Unknown Verification Summary

This analysis verifies the following unknowns from KNOWN_UNKNOWNS.md:

| Unknown | Status | Finding |
|---------|--------|---------|
| 1.1 | ✅ VERIFIED | 5 functions missing: gamma, loggamma, card, ord, smin. 3 are differentiable. |
| 1.2 | ✅ VERIFIED | Domain mismatch in KKT stationarity; partial index overlap causes errors. |
| 1.3 | ✅ VERIFIED | 5 models lack objective-defining equations; enhanced extraction can fix. |
| 1.4 | ✅ VERIFIED | 4 models use IndexOffset (t-1, t+1); requires IR implementation. |
| 1.5 | ✅ VERIFIED | No `unsup_dollar_cond` errors in current failures (was 0 models). |
| 1.6 | ✅ VERIFIED | 3 models have ±Inf/NaN in parameters; model data issues, not fixable. |
| 1.7 | ✅ VERIFIED | Fixes are largely independent; ~21 models potentially fixable. |

---

## Appendix A: Derivative Formulas for Missing Functions

### gamma(x) - Gamma Function
```
Γ(x) = ∫₀^∞ t^(x-1) e^(-t) dt

d/dx Γ(x) = Γ(x) · ψ(x)

where ψ(x) = d/dx ln(Γ(x)) is the digamma function
```

**Implementation:** Use `scipy.special.digamma` or implement polynomial approximation.

### loggamma(x) - Log Gamma Function
```
ln(Γ(x))

d/dx ln(Γ(x)) = ψ(x)  (digamma function)
```

**Implementation:** Same as gamma - needs digamma.

### smin(a, b) - Smooth Minimum
```
smin(a, b) = min(a, b)

Smooth approximation using LogSumExp:
smin(a, b) ≈ -τ · ln(exp(-a/τ) + exp(-b/τ))

d/da smin ≈ exp(-a/τ) / (exp(-a/τ) + exp(-b/τ))
d/db smin ≈ exp(-b/τ) / (exp(-a/τ) + exp(-b/τ))

where τ is smoothing parameter (smaller = closer to true min)
```

---

## Appendix B: Domain Mismatch Examples

### Example: abel model
```gams
* Variable x(m,k) - indexed over m and k
* Constraint c(n,k) - indexed over n and k
* 
* During KKT construction:
* - Variable domain: ('m', 'k')
* - Multiplier domain: ('n', 'k')
* - Domains share 'k' but differ in 'm' vs 'n'
* - Current logic rejects this as partial overlap
```

**Potential Fix:** Introduce explicit index mapping or summation:
```
∂L/∂x(m,k) = ... + Σₙ λ(n,k) · ∂c(n,k)/∂x(m,k)
```

---

## References

- [ERROR_ANALYSIS.md](ERROR_ANALYSIS.md) - Overall error analysis
- [KNOWN_UNKNOWNS.md](KNOWN_UNKNOWNS.md) - Sprint 17 unknowns tracking
- [sprint16_baseline_metrics.json](../../../../data/gamslib/sprint16_baseline_metrics.json) - Quantitative baseline
- [AD Module Documentation](../../../ad/DERIVATIVE_RULES.md) - Derivative rules reference
