# GAMSLib Parser Failure Analysis

**Created:** 2025-11-14  
**Sprint:** Sprint 7 Prep (Task 2)  
**Purpose:** Detailed analysis of 9 GAMSLib parser failures to prioritize Sprint 7 parser enhancements  
**Baseline:** Sprint 6 - 10% parse rate (1/10 models parsed)  
**Target:** Sprint 7 - 30% parse rate (3/10 models parsed)

---

## Executive Summary

Analysis of 9 failed GAMSLib models reveals **3 primary failure categories** blocking 30% parse rate achievement:

1. **Preprocessor Directives** (2 models) - `$if`, `$set` commands cause immediate parse failure
2. **Set Range Syntax** (1 model) - `Set i / 1*6 /` notation not recognized  
3. **Statement-Level Features** (6 models) - Multiple identifiers, option statements, solve keyword issues

**Key Finding:** Preprocessor directives and set range syntax are **quick wins** that would unlock 3 additional models, raising the parse rate to 4/10 (40%), with estimated 9-12 hours of implementation effort.

**Recommendation:** Prioritize preprocessor mocking and set range syntax for Sprint 7 to achieve 30%+ parse rate goal.

---

## Table of Contents

1. [Failure Summary](#failure-summary)
2. [Detailed Model Analysis](#detailed-model-analysis)
3. [Feature Categorization](#feature-categorization)
4. [Feature Impact Matrix](#feature-impact-matrix)
5. [Quick Wins vs Hard Problems](#quick-wins-vs-hard-problems)
6. [Recommended Priority](#recommended-priority)
7. [Sprint 7 Implementation Plan](#sprint-7-implementation-plan)

---

## Failure Summary

**Total Failed:** 9/10 models (90% failure rate)  
**Error Type:** All failures are `UnexpectedCharacters` parser errors  
**Root Cause:** Missing GAMS syntax features in Lark grammar

### Models by Failure Category

| Category | Count | Models | Unlock Potential |
|----------|-------|--------|------------------|
| Preprocessor Directives | 2 | circle, maxmin | 20% → 30% |
| Set Range Syntax | 1 | himmel16 | 30% → 40% |
| Multiple Variable Declarations | 1 | trig | 40% → 50% |
| Model Declaration | 2 | hs62, mingamma | (Chained dependency) |
| Option Statement | 1 | mhw4dx | 50% → 60% |
| Solve Keyword Parsing | 1 | rbrock | 60% → 70% |
| Models Keyword | 1 | mathopt1 | 70% → 80% |

**Critical Path to 30%:** Preprocessor directives (2 models) = **30% parse rate (3/10 models)**  
**Critical Path to 40%:** + Set range syntax (1 model) = **40% parse rate (4/10 models)**

---

## Detailed Model Analysis

### 1. circle.gms

**Status:** ❌ Parse Failed  
**Error Line:** 16  
**Error Context:**
```gams
$if not set size $set size 10
```

**Root Cause:** Preprocessor directive `$if` and `$set` not recognized by grammar

**Missing Features:**
- `$if not set` conditional directive
- `$set` variable assignment directive
- Macro expansion `%size%` (line 18: `Set i / p1*p%size% /`)

**Impact:** Blocks parsing immediately in file header (line 16)

**Dependency Chain:** 
1. Must handle `$if`/`$set` directives
2. Must handle macro expansion `%var%`
3. Must handle set range with macro: `p1*p%size%`

**Estimated Unlock Effort:** 6-8 hours (preprocessor mocking + macro expansion)

---

### 2. himmel16.gms

**Status:** ❌ Parse Failed  
**Error Line:** 28  
**Error Context:**
```gams
Set i 'indices for the 6 points' / 1*6 /;
```

**Root Cause:** Set range syntax `1*6` not recognized

**Missing Features:**
- Numeric range syntax: `1*6` (shorthand for `1, 2, 3, 4, 5, 6`)
- Set element range notation

**Impact:** Blocks parsing of set declarations with range notation

**Dependency Chain:**
1. Must extend grammar to recognize `NUMBER STAR NUMBER` in set element lists
2. Parser transformer must expand range into individual elements

**Estimated Unlock Effort:** 3-4 hours (grammar update + transformer logic)

---

### 3. hs62.gms

**Status:** ❌ Parse Failed  
**Error Line:** 35  
**Error Context:**
```gams
mx / objdef, eq1x /;
```

**Root Cause:** Multiple identifiers in model declaration not recognized

**Missing Features:**
- Model declaration with multiple equations: `mx / eq1, eq2 /`
- Equation list syntax in model block

**Impact:** Blocks models that explicitly list constituent equations

**Dependency Chain:**
1. Must recognize identifier before `/` as model name
2. Must parse comma-separated equation list inside `/.../ `

**Estimated Unlock Effort:** 4-6 hours (model declaration grammar extension)

**Note:** This is likely a **cascading error** - the actual issue may be earlier in the file (line 35 is late in parsing). Needs deeper investigation.

---

### 4. mathopt1.gms

**Status:** ❌ Parse Failed  
**Error Line:** 38  
**Error Context:**
```gams
Models m / all /;
```

**Root Cause:** `Models` keyword (plural) not recognized

**Missing Features:**
- `Models` keyword (plural form of `Model`)
- Possibly a GAMS-specific synonym or legacy syntax

**Impact:** Blocks files using `Models` instead of `Model`

**Dependency Chain:**
1. Add `Models` as grammar terminal (alias for `Model`)
2. Handle in parser transformer

**Estimated Unlock Effort:** 1-2 hours (simple grammar addition)

---

### 5. maxmin.gms

**Status:** ❌ Parse Failed  
**Error Line:** 28  
**Error Context:**
```gams
$if not set points $set points 13
```

**Root Cause:** Preprocessor directive `$if` and `$set` (same as circle.gms)

**Missing Features:**
- `$if not set` conditional directive
- `$set` variable assignment directive

**Impact:** Identical to circle.gms - blocks parsing at preprocessor directive

**Dependency Chain:** Same as circle.gms

**Estimated Unlock Effort:** 0 hours (unlocked by fixing circle.gms preprocessor issue)

---

### 6. mhw4dx.gms

**Status:** ❌ Parse Failed  
**Error Line:** 37  
**Error Context:**
```gams
option limCol = 0, limRow = 0;
```

**Root Cause:** `option` statement not recognized

**Missing Features:**
- `option` keyword and statement syntax
- Multiple option assignments in single statement

**Impact:** Blocks files using GAMS option configuration

**Dependency Chain:**
1. Add `option` keyword to grammar
2. Parse `identifier = value` pairs (comma-separated)

**Estimated Unlock Effort:** 3-4 hours (option statement grammar + transformer)

---

### 7. mingamma.gms

**Status:** ❌ Parse Failed  
**Error Line:** 26  
**Error Context:**
```gams
m2 / y2def /;
```

**Root Cause:** Similar to hs62.gms - model declaration with equation list

**Missing Features:**
- Model declaration: `modelname / equationlist /`

**Impact:** Same as hs62.gms

**Dependency Chain:** Same as hs62.gms

**Estimated Unlock Effort:** 0 hours (unlocked by fixing hs62.gms model declaration)

---

### 8. rbrock.gms

**Status:** ❌ Parse Failed  
**Error Line:** 24  
**Error Context:**
```gams
solve rosenbr minimizing f using nlp;
```

**Root Cause:** Parser expects `USING` keyword but finds `minimizing`

**Missing Features:**
- `solve` statement with `minimizing` keyword before `using`
- Current parser may expect: `solve model using solver`
- Actual GAMS syntax: `solve model {minimizing|maximizing} objective using solver`

**Impact:** Blocks files specifying optimization direction in solve statement

**Dependency Chain:**
1. Update `solve` statement grammar to include optional `{minimizing|maximizing} objective`
2. Handle objective variable specification

**Estimated Unlock Effort:** 4-6 hours (solve statement grammar revision)

---

### 9. trig.gms

**Status:** ❌ Parse Failed  
**Error Line:** 31  
**Error Context:**
```gams
Scalar xdiff, fdiff;
```

**Root Cause:** Multiple scalar declarations in single statement not recognized

**Missing Features:**
- Comma-separated scalar declarations: `Scalar x, y, z;`
- Current parser likely expects: `Scalar x; Scalar y; Scalar z;`

**Impact:** Blocks files using compact scalar declaration syntax

**Dependency Chain:**
1. Update scalar declaration grammar to accept comma-separated list
2. Parser transformer must create multiple Scalar nodes

**Estimated Unlock Effort:** 2-3 hours (scalar declaration grammar extension)

---

## Feature Categorization

### Preprocessor Features
- `$if not set variable` - Conditional directive
- `$set variable value` - Variable assignment
- `%variable%` - Macro expansion

**Models Blocked:** circle, maxmin (2 models)

---

### Set Features
- Range syntax: `1*6` (expand to `1, 2, 3, 4, 5, 6`)
- Range with prefix: `p1*p10` (expand to `p1, p2, ..., p10`)

**Models Blocked:** himmel16 (1 model), circle (chained after preprocessor)

---

### Declaration Features
- Multiple scalar declaration: `Scalar x, y, z;`
- Model declaration with equation list: `model_name / eq1, eq2 /`
- `Models` keyword (plural)

**Models Blocked:** trig (1 model), hs62, mingamma (2 models), mathopt1 (1 model)

---

### Statement Features
- `option` statement: `option limRow = 0;`
- `solve` with optimization direction: `solve model minimizing obj using nlp`

**Models Blocked:** mhw4dx (1 model), rbrock (1 model)

---

## Feature Impact Matrix

| Feature | Models Blocked | Complexity | Est. Effort | Priority | Unlock Rate |
|---------|----------------|------------|-------------|----------|-------------|
| **Preprocessor directives** (`$if`, `$set`) | 2 (circle, maxmin) | High | 6-8h | **Critical** | +20% (10%→30%) |
| **Set range syntax** (`1*6`) | 1 (himmel16) | Medium | 3-4h | **High** | +10% (30%→40%) |
| **Multiple scalar declaration** | 1 (trig) | Low | 2-3h | **High** | +10% (40%→50%) |
| **Model declaration** (`m / eq1 /`) | 2 (hs62, mingamma) | Medium | 4-6h | **Medium** | +20% (50%→70%) |
| **Option statement** | 1 (mhw4dx) | Low | 3-4h | **Medium** | +10% (70%→80%) |
| **Solve with min/max** | 1 (rbrock) | Medium | 4-6h | **Medium** | +10% (80%→90%) |
| **Models keyword** (plural) | 1 (mathopt1) | Low | 1-2h | **Low** | +10% (90%→100%) |

**Total Estimated Effort:** 23-33 hours

---

## Quick Wins vs Hard Problems

### Quick Wins (High ROI)

Features with high ROI (<6 hours effort):

1. **Set Range Syntax** (3-4 hours)
   - Unlocks: himmel16 (+10%)
   - Complexity: Medium (grammar + transformer)
   - ROI: **High** (10% unlock / 4h = 2.5% per hour)

2. **Multiple Scalar Declaration** (2-3 hours)
   - Unlocks: trig (+10%)
   - Complexity: Low (simple grammar change)
   - ROI: **High** (10% unlock / 3h = 3.3% per hour)

3. **Models Keyword** (1-2 hours)
   - Unlocks: mathopt1 (+10%)
   - Complexity: Low (add grammar terminal)
   - ROI: **Very High** (10% unlock / 2h = 5% per hour)

**Quick Wins Total:** 3 models, 6-9 hours, 30% unlock

---

### Medium-Effort Features

Features requiring 4-6 hours:

1. **Model Declaration with Equation List** (4-6 hours)
   - Unlocks: hs62, mingamma (+20%)
   - Complexity: Medium (model block parsing)
   - ROI: **Medium** (20% unlock / 5h = 4% per hour)

2. **Option Statement** (3-4 hours)
   - Unlocks: mhw4dx (+10%)
   - Complexity: Low-Medium (new statement type)
   - ROI: **Medium** (10% unlock / 4h = 2.5% per hour)

3. **Solve Statement with Min/Max** (4-6 hours)
   - Unlocks: rbrock (+10%)
   - Complexity: Medium (solve grammar revision)
   - ROI: **Medium** (10% unlock / 5h = 2% per hour)

**Medium-Effort Total:** 4 models, 11-16 hours, 50% unlock

---

### Hard Problems (High Complexity)

Features requiring >6 hours or complex implementation:

1. **Preprocessor Directives** (6-8 hours)
   - Unlocks: circle, maxmin (+20%)
   - Complexity: High (lexer/parser interaction, macro expansion)
   - ROI: **Medium** (20% unlock / 7h = 2.9% per hour)
   - **Note:** High impact (2 models) but higher complexity
   - **Dependency:** Macro expansion needed for set range in circle.gms

**Hard Problems Total:** 2 models, 6-8 hours, 20% unlock

---

## Recommended Priority

### Sprint 7 Critical Priority (Target: 30% Parse Rate)

**Goal:** Unlock 2 additional models (10% → 30% = 3/10 models)

**Recommended Feature Set:**

1. **Preprocessor Directive Mocking** (6-8 hours) - **CRITICAL**
   - Mock `$if`, `$set` directives (recognize and skip/log)
   - Mock macro expansion `%var%` (replace with default or skip)
   - **Unlocks:** circle, maxmin (+20%)
   - **Rationale:** Blocks 2 models at file header; must fix to make progress

2. **Set Range Syntax** (3-4 hours) - **HIGH**
   - Parse `1*6` and `p1*p10` range notation
   - Expand to individual elements in transformer
   - **Unlocks:** himmel16 (+10%)
   - **Rationale:** Simple feature, high ROI, gets to 40% parse rate

**Total Sprint 7 Critical:** 9-12 hours, **+20% parse rate (30% total = 3/10 models)**

---

### Sprint 7 Optional Priority (Stretch Goal: 50%+ Parse Rate)

If Critical features complete early:

3. **Multiple Scalar Declaration** (2-3 hours)
   - **Unlocks:** trig (+10%)
   - **Rationale:** Very simple, high ROI

4. **Models Keyword** (1-2 hours)
   - **Unlocks:** mathopt1 (+10%)
   - **Rationale:** Trivial implementation

**Total Sprint 7 Optional:** 3-5 hours, **+20% parse rate (60% total)**

---

### Sprint 8 Deferred (Wave 2)

Features deferred to Sprint 8+ due to lower priority or complexity:

5. **Model Declaration with Equation List** (4-6 hours)
   - **Unlocks:** hs62, mingamma (+20%)
   
6. **Option Statement** (3-4 hours)
   - **Unlocks:** mhw4dx (+10%)
   
7. **Solve Statement with Min/Max** (4-6 hours)
   - **Unlocks:** rbrock (+10%)

**Total Sprint 8:** 11-16 hours, **+40% parse rate (100% total)**

---

## Sprint 7 Implementation Plan

### Phase 1: Preprocessor Directive Mocking (6-8 hours)

**Approach:** Mock/skip directives rather than full preprocessing

**Implementation Steps:**

1. **Grammar Extension** (2 hours)
   ```lark
   preprocessor_directive: "$" DIRECTIVE_NAME directive_args? NEWLINE
   DIRECTIVE_NAME: "if" | "set" | "include" | "ontext" | "offtext" | ...
   directive_args: /[^\n]+/
   ```

2. **Transformer Logic** (2 hours)
   - Log directive encountered (for debugging)
   - Skip directive (don't add to IR)
   - Store `$set` values in symbol table (for future macro expansion)

3. **Macro Expansion** (2-3 hours)
   - Recognize `%variable%` syntax in grammar
   - Replace with value from symbol table or default
   - Handle undefined macros gracefully (warning + default)

4. **Testing** (1 hour)
   - Test on circle.gms, maxmin.gms
   - Verify models parse successfully
   - Check IR correctness

**Deliverables:**
- Updated `src/gams/grammar.lark` with preprocessor rules
- Updated `src/gams/parser.py` with directive handling
- Tests: `tests/parser/test_preprocessor.py`

**Success Criteria:**
- circle.gms parses successfully
- maxmin.gms parses successfully
- Parse rate: 10% → 30%

---

### Phase 2: Set Range Syntax (3-4 hours)

**Approach:** Extend set element grammar to recognize range notation

**Implementation Steps:**

1. **Grammar Extension** (1 hour)
   ```lark
   set_element: ID | NUMBER | set_range
   set_range: (ID | NUMBER) "*" (ID | NUMBER)
   ```

2. **Transformer Logic** (1-2 hours)
   - Detect `range` node in set element list
   - Expand numeric ranges: `1*6` → `["1", "2", "3", "4", "5", "6"]`
   - Expand prefixed ranges: `p1*p6` → `["p1", "p2", "p3", "p4", "p5", "p6"]`
   - Handle edge cases (invalid ranges, non-sequential)

3. **Testing** (1 hour)
   - Test on himmel16.gms
   - Test edge cases (reverse ranges, large ranges)

**Deliverables:**
- Updated `src/gams/grammar.lark` with range syntax
- Updated `src/ir/` with range expansion logic
- Tests: `tests/parser/test_set_range.py`

**Success Criteria:**
- himmel16.gms parses successfully
- Range notation expanded correctly in IR
- Parse rate: 30% → 40%

---

## Cross-References

- **PROJECT_PLAN.md (Sprint 7):** Lines 45-92 specify 30% parse rate goal
- **KNOWN_UNKNOWNS.md:**
  - Unknown 1.3: Is 30% GAMSLib parse rate achievable in Sprint 7?
  - Unknown 3.1: Is 30% parse rate achievable with planned parser enhancements?
- **PREP_PLAN.md (Task 2):** Lines 155-295 define this analysis task

---

## Conclusions

### Key Findings

1. **30% Parse Rate is Achievable** ✅
   - 2 models (circle, maxmin) unlocked by preprocessor mocking
   - Estimated effort: 6-8 hours
   - Result: 10% → 30% parse rate

2. **40% Parse Rate is Highly Achievable** ✅
   - Add set range syntax (+3-4 hours)
   - Result: 30% → 40% parse rate
   - Total effort: 9-12 hours

3. **60%+ Parse Rate is Possible (Stretch)** ⚠️
   - Add multiple scalar declaration (+2-3 hours)
   - Add Models keyword (+1-2 hours)
   - Result: 40% → 60% parse rate
   - Total effort: 12-17 hours

4. **100% Parse Rate Requires Sprint 8** ❌
   - Remaining features: 11-16 hours
   - Defer to Sprint 8 (Wave 2)

### Recommendations

**For Sprint 7:**

✅ **DO:** Implement preprocessor mocking + set range syntax (9-12 hours)
- Guarantees 30% parse rate goal
- Likely achieves 40% parse rate
- Manageable complexity

⚠️ **CONSIDER:** Add quick wins if time permits (multiple scalar, Models keyword)
- Low risk (+3-5 hours)
- High ROI (60% parse rate)

❌ **DON'T:** Attempt 100% parse rate in Sprint 7
- Requires 20+ hours of parser work
- Detracts from other Sprint 7 goals (test performance, convexity, CI)
- Better suited for focused Sprint 8 parser effort

**Success Metrics:**
- ✅ **Minimum:** 30% parse rate (circle, maxmin unlocked)
- ✅ **Target:** 40% parse rate (+ himmel16 unlocked)
- 🎯 **Stretch:** 60% parse rate (+ trig, mathopt1 unlocked)

---

**Analysis Completed:** 2025-11-14  
**Analyst:** Sprint 7 Prep Team  
**Next Steps:** Verify Unknown 1.3 and 3.1 in KNOWN_UNKNOWNS.md
