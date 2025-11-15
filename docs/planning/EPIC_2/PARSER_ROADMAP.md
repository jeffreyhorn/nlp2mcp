# GAMS Parser Roadmap (Sprints 8-10)

**Created:** November 14, 2025  
**Purpose:** Comprehensive catalog of GAMS syntax features and implementation roadmap  
**Scope:** Parser enhancements beyond Sprint 7 (Waves 2-4)  
**Baseline:** Sprint 7 - 30-40% GAMSLib parse rate (3-4/10 models)  
**Target:** Sprint 10 - 70-90% GAMSLib parse rate (7-9/10 models)

---

## Executive Summary

This document catalogs **52 GAMS syntax features** across 5 categories and provides a phased implementation roadmap for Sprints 8-10. Analysis shows a clear progression path from high-ROI quick wins to complex advanced features.

**Key Findings:**
- **Wave 1 (Sprint 7):** Preprocessor directives + set range syntax → 30-40% parse rate (COMPLETE/IN PROGRESS)
- **Wave 2 (Sprint 8):** Statement-level features (solve, model, option, scalars) → 50-70% parse rate
- **Wave 3 (Sprint 9):** Advanced expressions + control flow → 80% parse rate
- **Wave 4 (Sprint 10):** Display, assignments, advanced sets → 90% parse rate

**Total Estimated Effort:** 110-150 hours across Sprints 8-10 (36-50 hours per sprint)

**ROI Analysis:** Top 10 features unlock 60% of models with 40% of effort (high concentration of value)

---

## Table of Contents

1. [Feature Catalog](#feature-catalog)
2. [GAMSLib Usage Analysis](#gamslib-usage-analysis)
3. [Feature Dependency Graph](#feature-dependency-graph)
4. [Effort & Impact Estimates](#effort--impact-estimates)
5. [ROI Rankings](#roi-rankings)
6. [Sprint 8 Roadmap (Wave 2)](#sprint-8-roadmap-wave-2)
7. [Sprint 9 Roadmap (Wave 3)](#sprint-9-roadmap-wave-3)
8. [Sprint 10 Roadmap (Wave 4)](#sprint-10-roadmap-wave-4)
9. [Feature Dependencies](#feature-dependencies)
10. [Implementation Priorities](#implementation-priorities)

---

## Feature Catalog

### Category 1: Preprocessing & Macros (7 features)

| # | Feature | Description | Currently Supported? | Sprint |
|---|---------|-------------|---------------------|--------|
| 1.1 | `$if not set` | Conditional compilation | ❌ | 7 (Wave 1) |
| 1.2 | `$set variable value` | Set macro variable | ❌ | 7 (Wave 1) |
| 1.3 | `%variable%` | Macro expansion | ❌ | 7 (Wave 1) |
| 1.4 | `$include "file"` | File inclusion | ✅ **DONE** | - |
| 1.5 | `$if` / `$else` / `$endif` | Advanced conditionals | ❌ | 9 (Wave 3) |
| 1.6 | `$ontext` / `$offtext` | Multi-line comments | ❌ | 10 (Wave 4) |
| 1.7 | `$eolCom` / `$inlineCom` | Comment control | ❌ | 10 (Wave 4) |

**Priority:** Critical (Wave 1 features block 20% of models)  
**Status:** Sprint 7 in progress (Task 3 complete, implementation pending)

---

### Category 2: Set Features (9 features)

| # | Feature | Description | Currently Supported? | Sprint |
|---|---------|-------------|---------------------|--------|
| 2.1 | `Set i / el1, el2 /` | Explicit set elements | ✅ **DONE** | - |
| 2.2 | `Set i / 1*10 /` | Numeric range notation | ❌ | 7 (Wave 1) |
| 2.3 | `Set i / p1*p10 /` | String range notation | ❌ | 7 (Wave 1) |
| 2.4 | `Set ij(i,j)` | Multi-dimensional sets | ✅ **DONE** | - |
| 2.5 | `Set i(j)` | Indexed/filtered sets | ❌ | 8 (Wave 2) |
| 2.6 | `Set i /system.date/` | Dynamic sets | ❌ | 9 (Wave 3) |
| 2.7 | Set operations | `union`, `intersect`, `card()` | ❌ | 9 (Wave 3) |
| 2.8 | `alias(i, ii)` | Set aliases | ✅ **DONE** | - |
| 2.9 | Ordered sets | `ord()`, `card()` | ❌ | 9 (Wave 3) |

**Priority:** High (Wave 1 features block 10% of models)  
**Status:** Sprint 7 in progress (set range syntax)

---

### Category 3: Parameter & Data Features (8 features)

| # | Feature | Description | Currently Supported? | Sprint |
|---|---------|-------------|---------------------|--------|
| 3.1 | `Parameter p(i)` | Indexed parameters | ✅ **DONE** | - |
| 3.2 | `Parameter p / data /` | Inline data | ✅ **DONE** | - |
| 3.3 | `Table t(i,j)` | Table declarations | ✅ **DONE** | - |
| 3.4 | `Scalar x, y, z` | Multiple scalar decl | ❌ | 8 (Wave 2) |
| 3.5 | `x = value;` | Assignment statements | ❌ | 8 (Wave 2) |
| 3.6 | `p(i) = expr;` | Indexed assignments | ❌ | 8 (Wave 2) |
| 3.7 | `p(i)$(condition) = expr` | Conditional assignments | ❌ | 9 (Wave 3) |
| 3.8 | `$load` / `$gdxin` | External data loading | ❌ | 10 (Wave 4) |

**Priority:** Medium (Wave 2 features unlock 10% of models)  
**Status:** Most data features already supported

---

### Category 4: Variable & Equation Features (10 features)

| # | Feature | Description | Currently Supported? | Sprint |
|---|---------|-------------|---------------------|--------|
| 4.1 | `Variable x` | Basic variables | ✅ **DONE** | - |
| 4.2 | `Positive Variable x` | Variable kinds | ✅ **DONE** | - |
| 4.3 | `Variable x(i,j)` | Indexed variables | ✅ **DONE** | - |
| 4.4 | `x.lo = 0; x.up = 10` | Variable bounds | ✅ **DONE** | - |
| 4.5 | `x.l = 5` | Level initialization | ❌ | 8 (Wave 2) |
| 4.6 | `x.m` | Marginal values | ❌ | 8 (Wave 2) |
| 4.7 | `x.fx = 5` | Fixed variables | ❌ | 8 (Wave 2) |
| 4.8 | `Equation eq(i)` | Indexed equations | ✅ **DONE** | - |
| 4.9 | `eq.. expr =e= expr` | Equation definitions | ✅ **DONE** | - |
| 4.10 | `eq.l`, `eq.m` | Equation attributes | ❌ | 9 (Wave 3) |

**Priority:** Medium (most core features done, attributes are optional)  
**Status:** Core features complete, attributes deferred

---

### Category 5: Statement & Control Features (18 features)

| # | Feature | Description | Currently Supported? | Sprint |
|---|---------|-------------|---------------------|--------|
| 5.1 | `Solve m using nlp` | Basic solve | ✅ **DONE** | - |
| 5.2 | `Solve m min obj using nlp` | Solve with objective | ❌ | 8 (Wave 2) |
| 5.3 | `Model m / all /` | Model with equation list | ❌ | 8 (Wave 2) |
| 5.4 | `Models m / all /` | Plural keyword | ❌ | 8 (Wave 2) |
| 5.5 | `option limRow = 0` | Option statements | ❌ | 8 (Wave 2) |
| 5.6 | `display x, y` | Display statements | ❌ | 9 (Wave 3) |
| 5.7 | `loop(i, ...)` | Loop statements | ❌ | 9 (Wave 3) |
| 5.8 | `if(condition, ...)` | Conditional execution | ❌ | 9 (Wave 3) |
| 5.9 | `while(condition, ...)` | While loops | ❌ | 10 (Wave 4) |
| 5.10 | `for(i=1 to 10, ...)` | For loops | ❌ | 10 (Wave 4) |
| 5.11 | `abort$(condition)` | Conditional abort | ❌ | 10 (Wave 4) |
| 5.12 | `put / putclose` | File output | ❌ | 10 (Wave 4) |
| 5.13 | `execute` | System commands | ❌ | 10 (Wave 4) |
| 5.14 | `$phantom` | Phantom sets | ❌ | 10 (Wave 4) |
| 5.15 | `$batInclude` | Batch include | ❌ | 10 (Wave 4) |
| 5.16 | `file` / `files` | File declarations | ❌ | 10 (Wave 4) |
| 5.17 | `acronym` | Acronyms | ❌ | 10 (Wave 4) |
| 5.18 | `abort` | Unconditional abort | ❌ | 10 (Wave 4) |

**Priority:** Mixed (solve/model/option are high priority, control flow is low)  
**Status:** Core solve done, statement-level features needed for Sprint 8

---

## GAMSLib Usage Analysis

### Failed Models Feature Analysis

Based on GAMSLib failure analysis (Task 2), here's which features block which models:

| Model | Blocking Feature(s) | Category | Priority |
|-------|---------------------|----------|----------|
| circle.gms | `$if not set`, `$set`, `%macro%` | Preprocessing | Critical |
| maxmin.gms | `$if not set`, `$set` | Preprocessing | Critical |
| himmel16.gms | Set range `/ 1*6 /` | Sets | High |
| trig.gms | Multiple scalar decl `Scalar x, y` | Parameters | High |
| hs62.gms | Model declaration `m / eq1 /` | Statements | Medium |
| mingamma.gms | Model declaration `m / eq1 /` | Statements | Medium |
| mhw4dx.gms | `option` statement | Statements | Medium |
| rbrock.gms | `Solve m min obj using nlp` | Statements | Medium |
| mathopt1.gms | `Models` (plural) | Statements | Low |

**Current Parse Rate:** 10% (1/10 models: hs62.gms partially parses)  
**Sprint 7 Target:** 30-40% (3-4/10 models)  
**Sprint 8 Target:** 50-70% (5-7/10 models)  
**Sprint 9 Target:** 80% (8/10 models)  
**Sprint 10 Target:** 90% (9/10 models)

### Feature Frequency in Failed Models

| Feature Category | Models Using | % of Failed Models |
|------------------|--------------|-------------------|
| Preprocessor directives | 2 | 22% |
| Set range syntax | 1 | 11% |
| Multiple scalar decl | 1 | 11% |
| Model declaration | 2 | 22% |
| Option statements | 1 | 11% |
| Solve with min/max | 1 | 11% |
| Models keyword | 1 | 11% |

**Insight:** No single feature dominates. Steady progress across categories needed.

---

## Feature Dependency Graph

```
Wave 1 (Sprint 7)
├── Preprocessor directives ($if, $set, %macro%) [CRITICAL]
│   └── Unlocks: circle.gms, maxmin.gms (+20%)
└── Set range syntax (1*10) [HIGH]
    └── Unlocks: himmel16.gms (+10%)

Wave 2 (Sprint 8)
├── Multiple scalar declarations [HIGH]
│   └── Unlocks: trig.gms (+10%)
├── Model declaration (m / eq1, eq2 /) [MEDIUM]
│   └── Unlocks: hs62.gms, mingamma.gms (+20%)
├── Solve with objective (min/max) [MEDIUM]
│   └── Unlocks: rbrock.gms (+10%)
├── Option statements [MEDIUM]
│   └── Unlocks: mhw4dx.gms (+10%)
└── Models keyword (plural) [LOW]
    └── Unlocks: mathopt1.gms (+10%)

Wave 3 (Sprint 9) - Advanced Features
├── Display statements
├── Loop statements
├── Conditional execution
├── Set operations
└── Dynamic assignments

Wave 4 (Sprint 10) - Specialized Features
├── File I/O (put/putclose)
├── Execute statements
├── Advanced preprocessor
└── Data loading ($gdxin)
```

**Dependencies:**
- No circular dependencies detected
- Preprocessor features are foundational (used by many models)
- Statement-level features are mostly independent

---

## Effort & Impact Estimates

### Effort Scale
- **Low:** 1-3 hours (simple grammar additions)
- **Medium:** 4-6 hours (grammar + transformer logic)
- **High:** 7-12 hours (complex parsing + semantic analysis)
- **Very High:** 13+ hours (major refactoring or new subsystems)

### Impact Scale
- **Critical:** Unlocks 20%+ of models
- **High:** Unlocks 10-20% of models
- **Medium:** Unlocks 5-10% of models
- **Low:** Unlocks <5% of models

### Top 30 Features by Effort/Impact

| Rank | Feature | Effort | Impact | Models Unlocked | ROI Score |
|------|---------|--------|--------|----------------|-----------|
| 1 | `Models` keyword | Low | High | 1 (10%) | 10.0 |
| 2 | Multiple scalar decl | Low | High | 1 (10%) | 6.7 |
| 3 | Set range syntax | Medium | High | 1 (10%) | 2.5 |
| 4 | Preprocessor ($if/$set) | High | Critical | 2 (20%) | 2.5 |
| 5 | Option statements | Medium | High | 1 (10%) | 2.5 |
| 6 | Model declaration | Medium | Critical | 2 (20%) | 4.0 |
| 7 | Solve with min/max | Medium | High | 1 (10%) | 2.0 |
| 8 | Variable `.l` attribute | Low | Medium | TBD | 3.3 |
| 9 | Variable `.m` attribute | Low | Medium | TBD | 3.3 |
| 10 | Variable `.fx` | Low | Medium | TBD | 3.3 |
| 11 | Indexed assignments | Medium | Medium | TBD | 1.7 |
| 12 | Indexed sets `Set i(j)` | Medium | Medium | TBD | 1.7 |
| 13 | Display statements | Medium | Low | 0 | 0.8 |
| 14 | Advanced $if/$else | High | Low | 0 | 0.4 |
| 15 | Conditional assignments | High | Medium | TBD | 0.8 |
| 16 | Set operations | High | Low | 0 | 0.4 |
| 17 | Loop statements | High | Low | 0 | 0.4 |
| 18 | Conditional execution | High | Low | 0 | 0.4 |
| 19 | Equation `.l` / `.m` | Medium | Low | 0 | 0.8 |
| 20 | Dynamic sets | High | Low | 0 | 0.4 |
| 21 | `ord()` / `card()` | Medium | Low | 0 | 0.8 |
| 22 | While loops | High | Very Low | 0 | 0.3 |
| 23 | For loops | High | Very Low | 0 | 0.3 |
| 24 | File output (put) | Very High | Very Low | 0 | 0.2 |
| 25 | Execute statements | Very High | Very Low | 0 | 0.2 |
| 26 | $ontext/$offtext | Medium | Very Low | 0 | 0.4 |
| 27 | $eolCom | Low | Very Low | 0 | 1.0 |
| 28 | $gdxin | Very High | Very Low | 0 | 0.2 |
| 29 | Abort statements | Medium | Very Low | 0 | 0.4 |
| 30 | Phantom sets | Very High | Very Low | 0 | 0.2 |

**ROI Score = (Impact in %) / (Effort in hours)**

---

## ROI Rankings

### Tier 1: Excellent ROI (>4.0)

1. **`Models` keyword** (ROI: 10.0)
   - Effort: 1-2h | Impact: 10% | Models: mathopt1.gms
   - **Action:** Include in Sprint 8 Wave 2

2. **Multiple scalar declarations** (ROI: 6.7)
   - Effort: 2-3h | Impact: 10% | Models: trig.gms
   - **Action:** Include in Sprint 8 Wave 2

3. **Model declaration** (ROI: 4.0)
   - Effort: 4-6h | Impact: 20% | Models: hs62.gms, mingamma.gms
   - **Action:** Include in Sprint 8 Wave 2

### Tier 2: Good ROI (2.0-4.0)

4. **Variable attributes** (`.l`, `.m`, `.fx`) (ROI: 3.3 each)
   - Effort: 2-3h each | Impact: 5-10% | Models: TBD
   - **Action:** Include in Sprint 8 Wave 2

5. **Preprocessor directives** (ROI: 2.5)
   - Effort: 6-8h | Impact: 20% | Models: circle.gms, maxmin.gms
   - **Action:** Sprint 7 Wave 1 (IN PROGRESS)

6. **Set range syntax** (ROI: 2.5)
   - Effort: 3-4h | Impact: 10% | Models: himmel16.gms
   - **Action:** Sprint 7 Wave 1 (IN PROGRESS)

7. **Option statements** (ROI: 2.5)
   - Effort: 3-4h | Impact: 10% | Models: mhw4dx.gms
   - **Action:** Include in Sprint 8 Wave 2

8. **Solve with min/max** (ROI: 2.0)
   - Effort: 4-6h | Impact: 10% | Models: rbrock.gms
   - **Action:** Include in Sprint 8 Wave 2

### Tier 3: Moderate ROI (1.0-2.0)

9. **Indexed assignments** (ROI: 1.7)
10. **Indexed sets** (ROI: 1.7)
11. **$eolCom** (ROI: 1.0)

### Tier 4: Low ROI (<1.0)

All remaining features (display, loops, file I/O, etc.)

**Decision:** Focus Sprint 8 on Tier 1-2 features (ROI > 2.0)

---

## Sprint 8 Roadmap (Wave 2)

**Goal:** 50-70% GAMSLib parse rate (5-7/10 models)  
**Focus:** Statement-level features and variable attributes  
**Estimated Effort:** 25-35 hours

### Priority 1: Quick Wins (7-10 hours)

**A. Models Keyword (Plural)** - 1-2 hours
- **What:** Support `Models m / all /` in addition to `Model m / all /`
- **Why:** Unlocks mathopt1.gms (+10%)
- **Implementation:**
  ```lark
  model_stmt: ("Model"i | "Models"i) ID "/" id_list "/" SEMI
  ```
- **Complexity:** Trivial (grammar terminal addition)

**B. Multiple Scalar Declarations** - 2-3 hours
- **What:** Support `Scalar x, y, z;` syntax
- **Why:** Unlocks trig.gms (+10%)
- **Implementation:**
  ```lark
  scalars_block: ("Scalars"i | "Scalar"i) scalar_decl ("," scalar_decl)* SEMI
  ```
- **Complexity:** Low (grammar update + transformer)

**C. Variable .l/.m/.fx Attributes** - 4-5 hours
- **What:** Support `x.l = 5`, `x.m`, `x.fx = 10`
- **Why:** Common GAMS pattern for initialization
- **Implementation:** Extend assignment parsing for dotted attributes
- **Complexity:** Medium (grammar + IR extension)

### Priority 2: High-Impact Features (12-18 hours)

**D. Model Declaration with Equation List** - 4-6 hours
- **What:** Support `Model m / eq1, eq2, eq3 /`
- **Why:** Unlocks hs62.gms, mingamma.gms (+20%)
- **Implementation:**
  ```lark
  model_stmt: ("Model"i | "Models"i) ID "/" id_list "/" SEMI
            | ("Model"i | "Models"i) ID "/" "all" "/" SEMI
  ```
- **Complexity:** Medium (model block parsing)

**E. Solve with Objective** - 4-6 hours
- **What:** Support `Solve m minimizing obj using nlp`
- **Why:** Unlocks rbrock.gms (+10%)
- **Implementation:**
  ```lark
  solve_stmt: "Solve"i ID ("minimizing"i | "maximizing"i) ID "using"i solver_type SEMI
  ```
- **Complexity:** Medium (solve statement grammar revision)

**F. Option Statements** - 4-6 hours
- **What:** Support `option limRow = 0, limCol = 0;`
- **Why:** Unlocks mhw4dx.gms (+10%)
- **Implementation:**
  ```lark
  option_stmt: "option"i option_item ("," option_item)* SEMI
  option_item: ID ASSIGN (NUMBER | STRING)
  ```
- **Complexity:** Medium (new statement type)

### Total Wave 2 Impact

**Models Unlocked:** 5 additional models (mathopt1, trig, hs62, mingamma, mhw4dx, rbrock)  
**Parse Rate Improvement:** 10% → 60-70% (50-60% gain)  
**Effort:** 25-35 hours  
**ROI:** 1.7-2.4% per hour (excellent)

### Acceptance Criteria

- [ ] `Models` keyword supported (mathopt1.gms parses)
- [ ] Multiple scalar declarations supported (trig.gms parses)
- [ ] Variable attributes `.l`, `.m`, `.fx` supported
- [ ] Model declaration with equation list supported (hs62.gms, mingamma.gms parse)
- [ ] Solve with objective supported (rbrock.gms parses)
- [ ] Option statements supported (mhw4dx.gms parses)
- [ ] All quality checks pass (typecheck, lint, format, test)
- [ ] Parse rate ≥ 60% (6/10 models minimum)

---

## Sprint 9 Roadmap (Wave 3)

**Goal:** 80% GAMSLib parse rate (8/10 models)  
**Focus:** Advanced expressions, control flow, and remaining gaps  
**Estimated Effort:** 35-45 hours

### Priority 1: Expression Features (12-16 hours)

**A. Conditional Assignments** - 6-8 hours
- **What:** `p(i)$(condition) = expr`
- **Complexity:** High (conditional parsing + filtering)

**B. Set Operations** - 6-8 hours
- **What:** `union`, `intersect`, `card()`, `ord()`
- **Complexity:** High (new expression types)

### Priority 2: Control Flow (15-20 hours)

**C. Display Statements** - 4-6 hours
- **What:** `display x, y, z;`
- **Complexity:** Medium (new statement type)

**D. Loop Statements** - 6-8 hours
- **What:** `loop(i, statement);`
- **Complexity:** High (control flow + scope)

**E. Conditional Execution** - 5-6 hours
- **What:** `if(condition, statement);`
- **Complexity:** High (control flow)

### Priority 3: Advanced Features (8-10 hours)

**F. Indexed Sets** - 4-5 hours
- **What:** `Set active(i)` (filtered sets)
- **Complexity:** Medium (set filtering)

**G. Equation Attributes** - 4-5 hours
- **What:** `eq.l`, `eq.m` (equation level/marginal)
- **Complexity:** Medium (attribute parsing)

### Total Wave 3 Impact

**Models Unlocked:** +2 models (expected)  
**Parse Rate Improvement:** 60-70% → 80% (10-20% gain)  
**Effort:** 35-45 hours  
**ROI:** 0.3-0.6% per hour (moderate)

### Acceptance Criteria

- [ ] Conditional assignments supported
- [ ] Set operations implemented
- [ ] Display statements supported
- [ ] Loop statements supported
- [ ] Conditional execution supported
- [ ] Indexed sets supported
- [ ] Equation attributes supported
- [ ] Parse rate ≥ 80% (8/10 models minimum)

---

## Sprint 10 Roadmap (Wave 4)

**Goal:** 90% GAMSLib parse rate (9/10 models)  
**Focus:** Specialized features and edge cases  
**Estimated Effort:** 40-60 hours

### Priority 1: File I/O (15-20 hours)

**A. Put/Putclose Statements** - 10-15 hours
- **What:** File output statements
- **Complexity:** Very High (new subsystem)

**B. $gdxin / $load** - 5-5 hours
- **What:** External data loading
- **Complexity:** High (preprocessor + data loading)

### Priority 2: Advanced Preprocessor (10-15 hours)

**C. $if / $else / $endif** - 6-8 hours
- **What:** Full conditional compilation
- **Complexity:** High (preprocessor state machine)

**D. $ontext / $offtext** - 4-6 hours
- **What:** Multi-line comment blocks
- **Complexity:** Medium (lexer modification)

**E. $eolCom / $inlineCom** - 2-3 hours
- **What:** Comment delimiters
- **Complexity:** Low-Medium (lexer modification)

### Priority 3: Control Flow (8-12 hours)

**F. While/For Loops** - 6-8 hours
- **What:** `while(condition, ...)`, `for(i=1 to 10, ...)`
- **Complexity:** High (loop control)

**G. Abort Statements** - 2-4 hours
- **What:** `abort`, `abort$(condition)`
- **Complexity:** Low-Medium (error handling)

### Priority 4: Edge Cases (7-13 hours)

**H. Execute Statements** - 3-5 hours
- **What:** System command execution
- **Complexity:** Medium (subprocess handling)

**I. File Declarations** - 2-3 hours
- **What:** `file f; files f1, f2;`
- **Complexity:** Low-Medium (new symbol type)

**J. Acronyms** - 2-5 hours
- **What:** `acronym ac;`
- **Complexity:** Medium (symbol table extension)

### Total Wave 4 Impact

**Models Unlocked:** +1 model (expected)  
**Parse Rate Improvement:** 80% → 90% (10% gain)  
**Effort:** 40-60 hours  
**ROI:** 0.2-0.3% per hour (low, but completes coverage)

### Acceptance Criteria

- [ ] File I/O supported (put/putclose)
- [ ] External data loading supported ($gdxin)
- [ ] Advanced preprocessor conditionals supported
- [ ] Multi-line comments supported
- [ ] While/for loops supported
- [ ] Abort statements supported
- [ ] Execute statements supported
- [ ] Parse rate ≥ 90% (9/10 models minimum)

---

## Feature Dependencies

### No Dependencies (Can Implement Anytime)

- `Models` keyword
- Multiple scalar declarations
- Variable attributes (`.l`, `.m`, `.fx`)
- Equation attributes (`.l`, `.m`)
- Option statements
- Display statements
- `$eolCom` / `$inlineCom`

### Depends on Preprocessor

- Macro expansion `%var%` depends on `$set`
- Advanced conditionals `$if/$else` depend on basic `$if`

### Depends on Sets

- Set operations depend on basic set declarations (DONE)
- Indexed sets depend on multi-dimensional sets (DONE)

### Depends on Variables

- Variable attributes depend on variable declarations (DONE)

### Depends on Control Flow

- While/for loops depend on basic loop statements
- Conditional execution depends on expression evaluation

---

## Implementation Priorities

### Must Have (Sprint 8)

1. ✅ Models keyword (1-2h, ROI: 10.0)
2. ✅ Multiple scalar declarations (2-3h, ROI: 6.7)
3. ✅ Model declaration (4-6h, ROI: 4.0)
4. ✅ Variable attributes (4-5h, ROI: 3.3)
5. ✅ Solve with objective (4-6h, ROI: 2.0)
6. ✅ Option statements (4-6h, ROI: 2.5)

**Total:** 19-28 hours, unlocks 50-60% of models

### Should Have (Sprint 9)

7. Indexed assignments (4-6h, ROI: 1.7)
8. Indexed sets (4-5h, ROI: 1.7)
9. Display statements (4-6h, ROI: 0.8)
10. Set operations (6-8h, ROI: 0.4)

**Total:** 18-25 hours, unlocks additional 10-20% of models

### Nice to Have (Sprint 10)

11. Loop statements (6-8h, ROI: 0.4)
12. Conditional execution (5-6h, ROI: 0.4)
13. Advanced preprocessor (10-15h, ROI: 0.4)
14. File I/O (15-20h, ROI: 0.2)

**Total:** 36-49 hours, completes remaining 10% of models

---

## Conclusion

This roadmap provides a clear path from Sprint 7's 30-40% parse rate to Sprint 10's 90% parse rate through three focused waves:

- **Wave 2 (Sprint 8):** Statement-level features → 60-70% parse rate (19-28 hours)
- **Wave 3 (Sprint 9):** Advanced expressions + control flow → 80% parse rate (18-25 hours)
- **Wave 4 (Sprint 10):** Specialized features + edge cases → 90% parse rate (36-49 hours)

**Key Insights:**
1. **ROI-driven prioritization:** Top 6 features (19-28h) unlock 50-60% of models
2. **Diminishing returns:** Later features have lower ROI but increase coverage
3. **No blocking dependencies:** Features can be implemented in parallel
4. **Realistic targets:** Each sprint has achievable scope (20-40 hours)

**Recommendation:** Execute Wave 2 in Sprint 8 to achieve 60-70% parse rate with excellent ROI.
