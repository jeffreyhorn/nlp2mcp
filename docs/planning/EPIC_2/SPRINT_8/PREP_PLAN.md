# Sprint 8 Preparation Plan

**Sprint:** Epic 2 - Sprint 8 (Parser Maturity & Developer Experience)  
**Duration:** Weeks 5-6  
**Version:** v0.8.0  
**Strategy:** 60% Parser Maturity + 40% Infrastructure/UX (Hybrid)

---

## Executive Summary

Sprint 8 focuses on **incremental parse rate improvement** (20% → 25%) with **enhanced developer UX** through parser error line numbers and improved diagnostics. This sprint applies lessons learned from Sprint 7 retrospective, prioritizing conservative targets, complete feature implementations, and high-impact UX improvements.

**Sprint 8 Goals:**
1. **Parse Rate:** 20% → 25% (conservative, achievable target)
2. **Parser Error UX:** 100% of parse errors show file/line/column
3. **Feature Analysis:** Per-model dependency matrix for all 10 GAMSLib models
4. **Partial Metrics:** Statement-level parse success tracking
5. **Quality:** All existing tests pass, comprehensive test coverage for new features

**Key Differences from Sprint 7:**
- **Conservative targets** based on retrospective (25% vs 30%)
- **Per-model analysis** before feature selection (not feature-based assumptions)
- **Complete implementations** over partial/mock implementations
- **40% effort on UX/Infrastructure** (parser error line numbers, partial metrics)

**Preparation Effort:** 42-56 hours (~5-7 working days)  
**Critical Path:** Tasks 1 → 2 → 3, 7 → 9 → 10

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|------------------------|
| 1 | Create Sprint 8 Known Unknowns List | Critical | 4-6 hours | None | Proactive risk management |
| 2 | Analyze GAMSLib Per-Model Feature Dependencies | Critical | 8-10 hours | Task 1 | Feature dependency matrix |
| 3 | Research Option Statement Syntax | Critical | 6-8 hours | Task 2 | Option statement implementation |
| 4 | Design Parser Error Line Number Tracking | Critical | 4-6 hours | None | Parser error UX (100% coverage) |
| 5 | Design Partial Parse Metrics | High | 4-5 hours | Task 2 | Statement-level success tracking |
| 6 | Research Error Message Enhancement Patterns | High | 3-4 hours | Task 4 | Improved error messages |
| 7 | Survey High-ROI Parser Features | High | 5-7 hours | Task 2 | Feature prioritization (indexed assignments vs function calls) |
| 8 | Create Parser Test Fixture Strategy | High | 3-4 hours | Tasks 2, 3, 7 | Test coverage planning |
| 9 | Design Dashboard Enhancements | Medium | 3-4 hours | Task 5 | Partial metrics visualization |
| 10 | Plan Sprint 8 Detailed Schedule | Critical | 6-8 hours | All tasks | Sprint 8 execution planning |

**Total Estimated Time:** 42-56 hours (~5-7 working days)

**Critical Path:** Tasks 1 → 2 → 3, 7 → 9 → 10 (must complete before Sprint 8 Day 1)

---

## Task 1: Create Sprint 8 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 4-6 hours  
**Deadline:** Before Sprint 8 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Identify and document all known unknowns for Sprint 8 across parser maturity, UX improvements, and infrastructure enhancements. Proactively address risks before they block sprint execution.

### Why This Matters

Sprint 7 retrospective showed that feature-based analysis missed model-specific complexity. Sprint 8 uses a different approach (per-model analysis, conservative targets, UX focus). Unknowns help identify gaps in this new strategy.

**Key questions:**
- How complex is option statement semantic handling?
- What's the parser overhead of line number tracking for ALL parse errors?
- How to measure "partial parse" percentage accurately?
- Which feature (indexed assignments vs function calls) has higher ROI?
- How to generate actionable error message suggestions?

### Background

Sprint 7 Known Unknowns doc had 22-30 unknowns across 5 categories. Sprint 8 has different focus areas:
- **Parser Features:** Option statements, one additional high-ROI feature
- **UX Infrastructure:** Parser error line numbers, error message enhancements
- **Metrics:** Per-model feature matrix, partial parse tracking
- **Testing:** Fixture strategy for new features

From Sprint 7 retrospective (lines 138-183):
- "Create per-model feature dependency matrix before sprint planning"
- "Extend line number tracking to parser errors (estimated 4-6 hours)"
- "Consider partial parse metrics (e.g., parsed 80% of statements)"

### What Needs to Be Done

**1. Parser Enhancement Unknowns (8-10 unknowns expected)**

1.1. **Option Statement Complexity**
   - Assumption: Option statement parsing is "straightforward semantic handling"
   - Verification: Survey GAMS documentation for all option types and their semantics
   - Priority: Critical (blocks option implementation)

1.2. **Option Statement Scope**
   - Assumption: Basic options (limrow, limcol) are sufficient for mhw4dx.gms
   - Verification: Catalog all option statements in 10 GAMSLib models
   - Priority: High (affects parse rate target)

1.3. **Indexed Assignments vs Function Calls ROI**
   - Assumption: One of these features unlocks 2+ models
   - Verification: Per-model dependency analysis (Task 2)
   - Priority: Critical (determines Sprint 8 feature selection)

1.4. **Indexed Assignment Complexity**
   - Assumption: "Simple indexed assignments" are 6-8 hours
   - Verification: Research GAMS indexed assignment syntax variations
   - Priority: High (if selected as Sprint 8 feature)

1.5. **Function Call Syntax Scope**
   - Assumption: "Function call improvements" means argument parsing
   - Verification: Survey failed models for function call patterns
   - Priority: High (if selected as Sprint 8 feature)

**2. UX Infrastructure Unknowns (5-7 unknowns expected)**

2.1. **Parser Error Line Number Overhead**
   - Assumption: "Very Low risk" because infrastructure exists
   - Verification: Profile parser with Lark metadata extraction on all parse points
   - Priority: Medium (4-6 hour estimate seems accurate based on Sprint 7)

2.2. **Parser Error Coverage**
   - Assumption: 100% coverage achievable across all parser error types
   - Verification: Catalog all error types (UnexpectedCharacters, ParserSemanticError, etc.)
   - Priority: High (acceptance criterion)

2.3. **Error Message Suggestion Generation**
   - Assumption: "Did you mean?" hints are straightforward
   - Verification: Research error message pattern libraries (Python's difflib, Rust diagnostics)
   - Priority: Medium (3-5 hour budget may be tight)

2.4. **Error Context Extraction**
   - Assumption: Lark provides sufficient context for actionable suggestions
   - Verification: Test Lark error context on failed GAMSLib models
   - Priority: Medium

**3. Metrics & Analysis Unknowns (4-6 unknowns expected)**

3.1. **Partial Parse Measurement**
   - Assumption: Can count "statements parsed" vs "total statements"
   - Verification: Define what counts as a "statement" (declarations? assignments? equations?)
   - Priority: Critical (acceptance criterion: "himmel16: 85% parsed")

3.2. **Per-Model Feature Matrix Effort**
   - Assumption: 3-4 hours to create dependency matrix for all 10 models
   - Verification: Prototype analysis on 2-3 models to estimate per-model time
   - Priority: High (Task 2 estimate validation)

3.3. **Feature Dependency Chains**
   - Assumption: Most models need 1-2 features to parse
   - Verification: Manual inspection of each failed model's error cascade
   - Priority: Critical (affects parse rate achievability)

3.4. **Dashboard Partial Metrics Visualization**
   - Assumption: Can extend existing dashboard to show percentages
   - Verification: Design mockup for "himmel16: 85% parsed, needs [i++1, model sections]"
   - Priority: Medium

**4. Testing & Quality Unknowns (3-4 unknowns expected)**

4.1. **Option Statement Test Coverage**
   - Assumption: Can reuse fixture strategy from Sprint 7 (34 fixtures)
   - Verification: Estimate number of option statement variations to test
   - Priority: High

4.2. **Parser Error Line Number Test Strategy**
   - Assumption: Can verify line numbers in all error types
   - Verification: Design test approach for 5+ error types
   - Priority: High

4.3. **Partial Parse Metric Testing**
   - Assumption: Can unit test statement counting logic
   - Verification: Design test cases for edge cases (nested statements, multi-line)
   - Priority: Medium

**5. Sprint Planning Unknowns (2-3 unknowns expected)**

5.1. **60/40 Split Achievability**
   - Assumption: 60% parser (15-20h) + 40% UX (10-15h) = 25-35h total
   - Verification: Sum of Task 2-9 estimates should align with 25-35h
   - Priority: High

5.2. **Sprint 8 vs Sprint 8b Boundary**
   - Assumption: Sprint 8 delivers 25% parse rate, Sprint 8b delivers 30%
   - Verification: Confirm feature split based on per-model analysis
   - Priority: Medium

5.3. **Conservative Target Padding**
   - Assumption: 25% target (2.5 models) allows for one feature underperforming
   - Verification: Scenario planning for "option statements unlock 0 models"
   - Priority: Medium

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md` (1,200+ lines)

**Document Structure:**
- Executive Summary with Sprint 8 context and strategic shift
- How to Use This Document with priority definitions
- Summary Statistics: 27 unknowns across 8 categories
- Table of Contents
- 8 categories of unknowns (27 total)
- Template for adding new unknowns during sprint
- Next Steps section
- Appendix with Task-to-Unknown mapping table
- Cross-references to relevant documents

**Categories Created:**
1. Parser Enhancements - Option Statements (3 unknowns)
2. Parser Enhancements - Per-Model Feature Analysis (3 unknowns)
3. Parser Enhancements - High-ROI Feature (3 unknowns)
4. Infrastructure & UX - Parser Error Line Numbers (4 unknowns)
5. Infrastructure & UX - Improved Error Messages (4 unknowns)
6. Metrics & Analysis - Partial Parse Metrics (4 unknowns)
7. Testing & Quality (3 unknowns)
8. Sprint Planning & Execution (3 unknowns)

**Priority Distribution:**
- Critical: 7 unknowns (26%)
- High: 11 unknowns (41%)
- Medium: 7 unknowns (26%)
- Low: 2 unknowns (7%)

**Research Time:** 32-42 hours (aligns with 42-56 hour prep phase)

### Result

Successfully created comprehensive Sprint 8 Known Unknowns document with 27 unknowns across 8 categories. Document follows Sprint 7 format with enhancements:

**Key Achievements:**
- ✅ 27 unknowns documented (target: 22-30)
- ✅ All unknowns have: assumption, research questions, verification method, priority, owner, risk assessment
- ✅ Task-to-Unknown mapping table showing which prep tasks verify which unknowns
- ✅ Updated PREP_PLAN.md Tasks 2-10 with "Unknowns Verified" metadata
- ✅ All Critical unknowns (7) have verification plans assigned to specific tasks
- ✅ Coverage across all Sprint 8 components (parser, UX, metrics, testing, planning)

**Novel Additions (vs Sprint 7):**
- 8 categories instead of 5 (more granular organization by Sprint 8 components)
- Task-to-Unknown mapping table in Appendix
- "Unknowns Verified" metadata added to all prep tasks in PREP_PLAN.md

**Verification Coverage:**
- Task 2 verifies: 2.1, 2.2, 2.3 (per-model analysis unknowns)
- Task 3 verifies: 1.1, 1.2, 1.3 (option statement unknowns)
- Task 4 verifies: 4.1, 4.2, 4.3, 4.4 (parser error line number unknowns)
- Task 5 verifies: 6.1, 6.2, 6.3, 6.4 (partial parse metrics unknowns)
- Task 6 verifies: 5.1, 5.2, 5.3, 5.4 (error message enhancement unknowns)
- Task 7 verifies: 3.1, 3.2, 3.3 (high-ROI feature unknowns)
- Task 8 verifies: 7.1, 7.2, 7.3 (testing unknowns)
- Task 9 verifies: 6.4 (dashboard unknowns)
- Task 10 verifies: 8.1, 8.2, 8.3 (sprint planning unknowns)

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md

# Should contain required sections
grep -q "Parser Enhancement" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md
grep -q "UX Infrastructure" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md
grep -q "Metrics & Analysis" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md
grep -q "Testing & Quality" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md
grep -q "Sprint Planning" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md

# Count unknowns (should be 22-30)
grep -c "^## Unknown" docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
- 22-30 unknowns documented across 5 categories
- Each unknown has: assumption, verification method, priority, owner
- Research time estimated for all Critical/High unknowns
- Cross-referenced with PROJECT_PLAN.md Sprint 8 deliverables

### Acceptance Criteria

- [x] Document created with 22+ unknowns across 5 categories (✅ 27 unknowns across 8 categories, exceeds 22+ across 5)
- [x] All unknowns have assumption, verification method, priority
- [x] All Critical unknowns have verification plan and timeline
- [x] Unknowns cover all Sprint 8 components (parser, UX, metrics, testing)
- [x] Template for updates defined
- [x] Research time estimated (should align with prep task times) (✅ 32-42 hours)
- [x] Cross-referenced with PROJECT_PLAN.md and Sprint 7 RETROSPECTIVE.md

---

## Task 2: Analyze GAMSLib Per-Model Feature Dependencies

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 8-10 hours  
**Actual Time:** ~8 hours  
**Completed:** 2025-11-17  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 2.1, 2.2, 2.3

### Objective

Create comprehensive feature dependency matrix for all 10 GAMSLib models showing: (1) which features each model needs to parse, (2) which models are "close" (1-2 features away), (3) feature unlock rates, (4) recommended Sprint 8 feature priority.

**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md`

### Why This Matters

Sprint 7 retrospective identified this as critical gap: *"Didn't deeply analyze what each individual model needs to parse... some models have multiple blocking issues (e.g., circle.gms needs preprocessor AND function call syntax)."*

Feature-based analysis (Sprint 7 approach) assumed preprocessor unlocks 3 models. Actual result: unlocked 1 model (20% vs 30% target). Per-model analysis prevents this.

**Key questions:**
- Which models need only 1 feature to parse? (high ROI targets for Sprint 8)
- Which feature appears in most models? (option statements? indexed assignments?)
- What's the realistic parse rate for Sprint 8? (25%? 30%? depends on overlap)
- Should Sprint 8 prioritize indexed assignments or function calls?

### Background

From Sprint 7 RETROSPECTIVE.md (lines 146-160):
> **Recommendations for Sprint 8:**
> - Create per-model feature dependency matrix before sprint planning
> - Understand which models are "close" to parsing (1-2 features away)
> - Map out multi-feature dependencies
> - Prioritize models with single blocking issues

Current GAMSLib status (from `docs/status/GAMSLIB_CONVERSION_STATUS.md`):
- **Parsing:** mhw4d.gms ✅, rbrock.gms ✅ (20%)
- **Failing:** circle, himmel16, hs62, mathopt1, maxmin, mhw4dx, mingamma, trig (80%)

Sprint 8 targets (from PROJECT_PLAN.md lines 84-148):
- Option statements (unlocks mhw4dx.gms - known)
- One additional feature: indexed assignments OR function calls (TBD - depends on this analysis)

### What Needs to Be Done

**1. Per-Model Error Deep Dive (3-4 hours)**

For each of the 8 failing models, document:
- Primary error message and location
- Root cause (missing feature? parser bug? grammar limitation?)
- Secondary errors (what breaks if primary is fixed?)
- Estimated parsing percentage if primary error fixed
- Dependencies (which features needed for full parse)

**Models to analyze:**
1. **circle.gms** - Last seen: ParserSemanticError on uniform() function call
2. **himmel16.gms** - Last seen: UnexpectedCharacters on i++1 (lead/lag indexing)
3. **hs62.gms** - Last seen: UnexpectedCharacters on model section (mx)
4. **mathopt1.gms** - Last seen: ParserSemanticError on indexed assignment
5. **maxmin.gms** - Last seen: UnexpectedCharacters on low(n,nn) nested indexing
6. **mhw4dx.gms** - Last seen: UnexpectedCharacters on option limCol
7. **mingamma.gms** - Last seen: UnexpectedCharacters on model section (m2)
8. **trig.gms** - Last seen: ParserSemanticError on bound_scalar

**For each model, create:**
```markdown
### Model: circle.gms

**Primary Error:**
- Type: ParserSemanticError
- Location: Line 32, column 15
- Message: "Assignments must use numeric constants; got Call(uniform, ...)"
- Code: `size = uniform(1.0, 10.0);`

**Root Cause:**
- Missing feature: Function calls in assignments
- Parser expects numeric constants, gets function call AST node

**Secondary Errors (if primary fixed):**
- Likely: Additional preprocessor directives ($if not set)
- Possible: Set range syntax if used elsewhere in model

**Parsing Percentage if Primary Fixed:**
- Estimated: 70-80% (function calls fix, but preprocessor may block)

**Full Parse Dependencies:**
- [ ] Function call syntax in assignments (6-8 hours)
- [ ] Preprocessor directives (already implemented in Sprint 7)
- Total features needed: 2 (multiple-feature dependency)

**Priority for Sprint 8:**
- Medium-Low (needs 2 features, both Medium complexity)
```

**2. Feature Dependency Matrix (2-3 hours)**

Create table showing feature overlap across models:

| Feature | Complexity | Effort | Models Needing | Unlock Rate | Priority |
|---------|------------|--------|----------------|-------------|----------|
| Option statements | Low | 6-8h | mhw4dx, ? | 10-20% | High |
| Indexed assignments | Medium | 6-8h | mathopt1, ? | ?% | TBD |
| Function calls in assignments | Medium | 6-8h | circle, ? | ?% | TBD |
| Lead/lag indexing (i++1) | High | 8-10h | himmel16 | 10% | Low (Sprint 8b) |
| Model sections (mx) | Medium | 5-6h | hs62, mingamma | 20% | Low (Sprint 8b) |
| Nested indexing | High | 8-10h | maxmin | 10% | Low |
| ... | ... | ... | ... | ... | ... |

**3. Sprint 8 Feature Recommendation (2-3 hours)**

Based on matrix, recommend:
- **Confirmed Sprint 8 Feature:** Option statements (known to unlock mhw4dx)
- **Candidate Sprint 8 Feature:** Indexed assignments OR Function calls
  - Calculate unlock rate for each
  - Estimate combined parse rate (option + candidate)
  - Validate 25% target achievability
  - Recommend priority

**Analysis framework:**
```markdown
## Sprint 8 Feature Recommendation

### Confirmed: Option Statements
- Unlocks: mhw4dx.gms (confirmed)
- Unlock rate: +10% (2/10 → 3/10)
- Effort: 6-8 hours
- Risk: Low
- Status: Include in Sprint 8

### Candidate A: Indexed Assignments
- Appears in: mathopt1.gms, [others?]
- Potential unlock rate: +10% (if only mathopt1) or +20% (if 2 models)
- Effort: 6-8 hours
- Complexity: Medium (grammar changes)
- Combined with options: 30% parse rate (realistic)

### Candidate B: Function Calls in Assignments
- Appears in: circle.gms, [others?]
- Potential unlock rate: +0% (circle needs 2 features) or +10% (if unlocks 1 model)
- Effort: 6-8 hours
- Complexity: Medium
- Combined with options: 20-30% parse rate

### Recommendation: [TBD based on matrix]
- Rationale: [Higher unlock rate / fewer dependencies / Sprint 8b deferral strategy]
- Parse rate projection: 25% (conservative) to 30% (optimistic)
- Risk assessment: [LOW/MEDIUM]
```

**4. Models "Close" to Parsing (1 hour)**

Identify quick wins:
- Models needing only 1 feature (high priority for Sprint 8)
- Models needing 2 features where 1 is already implemented (Sprint 7 features)
- Models needing 2 features where both are Sprint 8 candidates

**5. Sprint 8b Boundary Recommendation (<1 hour)**

List features deferred to Sprint 8b:
- Advanced indexing (i++1) - himmel16.gms
- Model sections (mx) - hs62.gms, mingamma.gms
- Other high-complexity features

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (650+ lines)

**Per-Model Analysis:**
- Analyzed all 8 failing GAMSLib models with comprehensive error analysis
- Documented primary errors, root causes, secondary errors, and parsing percentages
- Identified 6 models with single-feature dependencies (75% of failing models)
- Identified 2 models with multi-feature dependencies (circle: 2 features, maxmin: 2 features)

**Feature Dependency Matrix:**
- Created comprehensive matrix with 6 features analyzed
- Calculated empirical unlock rates for each feature
- Option statements: Unlocks mhw4dx.gms (+10% parse rate)
- Indexed assignments: Unlocks mathopt1.gms + trig.gms (+20% parse rate)
- Multiple model definitions: Unlocks hs62.gms + mingamma.gms (+20% parse rate)
- Lead/lag indexing: Unlocks himmel16.gms (+10% parse rate)
- Function calls: Unlocks circle.gms (+10% parse rate, but needs 2 features total)
- Nested indexing: Unlocks maxmin.gms (+10% parse rate, but needs 2 features total)

**Sprint 8 Recommendation:**
- Confirmed: Option statements (unlocks mhw4dx, +10%, 6-8 hours, Low complexity)
- Recommended: Indexed assignments over function calls (unlocks 2 models vs 1 model)
- Combined parse rate projection: 30% conservative (3/10), 50% optimistic (5/10)
- Exceeds Sprint 8 target of 25-30% in optimistic scenario

**Sprint 8b Boundary:**
- Deferred: Multiple model definitions (5-6h, Medium complexity, +20% unlock rate)
- Deferred: Function calls in assignments (6-8h, Medium complexity, +10% unlock rate)
- Deferred: Lead/lag indexing (8-10h, High complexity, +10% unlock rate)
- Deferred to Sprint 9+: Nested indexing (10-12h, High complexity, +10% unlock rate)

**Unknown Verification:**
- 2.1: ✅ Per-model analysis completed in 8 hours (within 8-10 hour estimate)
- 2.2: ✅ 6 single-feature models identified (75% of failing models)
- 2.3: ✅ Per-model methodology superior to Sprint 7 feature-based analysis

### Result

**Key Achievements:**
1. ✅ High-confidence Sprint 8 feature recommendation: Option statements + Indexed assignments
2. ✅ Parse rate projection: 30% conservative, 50% optimistic (meets/exceeds 25-30% target)
3. ✅ Identified 3 quick-win models for Sprint 8 (mhw4dx, mathopt1, trig)
4. ✅ Clear Sprint 8b roadmap with 3 deferred features
5. ✅ Methodology validation: Per-model analysis prevents Sprint 7-style underestimation

**Impact on Sprint 8 Planning:**
- Sprint 8 will implement option statements (6-8h) + indexed assignments (6-8h) = 12-16h total
- Combined unlock rate: +30% (best case: +50%)
- Single-feature models prioritized over multi-feature models
- High confidence (95%) in conservative estimate, high confidence (80%) in optimistic estimate

**Methodology Insights:**
- Per-model analysis took 8 hours (within estimate), confirmed as feasible approach
- Explicit dependency mapping prevents feature-based underestimation from Sprint 7
- 75% of failing models have single-feature dependencies - excellent news for Sprint 8/8b velocity

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md

# Should contain all 8 failed models
grep -q "circle.gms" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md
grep -q "himmel16.gms" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md
grep -q "mhw4dx.gms" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md

# Should have feature dependency matrix
grep -q "| Feature | Complexity | Effort |" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md

# Should have recommendation
grep -q "Sprint 8 Feature Recommendation" docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/GAMSLIB_FEATURE_MATRIX.md` (400+ lines)
- Per-model analysis for all 8 failing models
- Feature dependency matrix with unlock rates
- Sprint 8 feature recommendation (indexed assignments vs function calls)
- Models "close" to parsing (1-2 features away)
- Sprint 8b feature boundary

### Acceptance Criteria

- [x] All 8 failing models analyzed with primary/secondary errors
- [x] Feature dependency matrix created with unlock rates
- [x] Sprint 8 feature recommendation provided with rationale
- [x] Parse rate projection for Sprint 8 (30% conservative, 50% optimistic - exceeds 25-30% target)
- [x] Models "close" to parsing identified (6 single-feature models)
- [x] Sprint 8b boundary defined (3 deferred features documented)
- [x] Cross-referenced with Sprint 7 RETROSPECTIVE.md recommendations

---

## Task 3: Research Option Statement Syntax

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Actual Time:** ~7 hours  
**Deadline:** 1 week before Sprint 8 Day 1  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 2 (Feature Matrix - confirms option statements are Sprint 8 priority)  
**Unknowns Verified:** 1.1, 1.2, 1.3

### Objective

Comprehensive research of GAMS option statement syntax, semantics, and usage patterns to design parser implementation for Sprint 8. Focus on basic options (limrow, limcol) that unlock mhw4dx.gms while cataloging other option types for future work.

### Why This Matters

Option statements are confirmed high-priority for Sprint 8 (unlocks mhw4dx.gms = +10% parse rate). PROJECT_PLAN.md estimates 6-8 hours with "Low risk (grammar extension, semantic handling straightforward)". This research validates that estimate and identifies any hidden complexity.

From Sprint 7 retrospective: *"Prefer complete implementations of fewer features over partial implementations of many."* Need to define scope clearly: what's "basic options" vs deferred to Sprint 8b/9?

### Background

From `docs/status/GAMSLIB_CONVERSION_STATUS.md`, mhw4dx.gms fails on:
```
option limCol = 0, limRow = 0;
       ^
No terminal matches 'l' in the current parser context
```

Parser doesn't recognize `option` keyword at statement level. Need to:
1. Add `option` to grammar as statement type
2. Parse option name and value
3. Handle semantic meaning (or mock for Sprint 8)

From Sprint 7 fixtures, `tests/fixtures/statements/04_option_statement.gms` documents:
> Note: Option statements not yet supported, so they are commented out

Sprint 8 will uncomment and implement these.

### What Needs to Be Done

**1. GAMS Documentation Survey (2-3 hours)**

Survey official GAMS documentation for option statement syntax:
- Statement format: `option name = value;` or `option name;` (boolean)?
- Value types: Integer? Float? String? Boolean?
- Multi-option format: `option a = 1, b = 2;` (comma-separated)?
- Scope rules: Global? Local to model? File-level?
- Common options: limrow, limcol, solprint, sysout, decimals, etc.

**Create catalog:**
```markdown
## Option Statement Syntax Patterns

### Basic Integer Options (Sprint 8 Target)
- `option limrow = 0;` - Limit number of rows in listing
- `option limcol = 0;` - Limit number of columns in listing
- `option decimals = 3;` - Decimal places in output
- Format: `option <name> = <integer>;`

### Boolean Options
- `option solprint = off;` - Suppress solution listing
- Format: `option <name> = on|off;` or `option <name>;` (implicitly on)

### Multi-Option Statements
- `option limrow = 0, limcol = 0, solprint = off;`
- Format: Comma-separated list

### String Options
- `option title = "My Model";`
- Format: `option <name> = "<string>";`

### Specialized Options (Defer to Sprint 8b/9)
- Solver-specific options
- File I/O options
- Advanced formatting options
```

**2. GAMSLib Usage Analysis (1-2 hours)**

Scan all 10 GAMSLib models for option statement usage:
```bash
grep -n "^option\|^ option" tests/fixtures/gamslib/*.gms
```

Catalog:
- Which models use options? (mhw4dx known, others?)
- Which option types? (Integer? Boolean? String?)
- How many options per model?
- Any edge cases or complex usage?

**Example output:**
```markdown
## GAMSLib Option Usage

### mhw4dx.gms
- Line 37: `option limCol = 0, limRow = 0;`
- Type: Multi-option, integer values
- Sprint 8 target: YES (unlocks model)

### [other models if applicable]
- Line X: `option ...`
- Type: ...
- Sprint 8 scope: YES/NO

### Summary
- Models using options: 2/10
- Sprint 8 scope options: limrow, limcol (integer)
- Deferred options: [list]
```

**3. Grammar Design (2-3 hours)**

Design Lark grammar rules for option statements:

**Option 1: Simple approach (Sprint 8)**
```lark
// Add to statement-level grammar
statement: ... | option_stmt

option_stmt: "option" option_list ";"
option_list: option_item ("," option_item)*
option_item: NAME "=" (INTEGER | "on" | "off")

// NAME already defined
// INTEGER already defined
```

**Option 2: Comprehensive (Sprint 8b if needed)**
```lark
option_stmt: "option" option_list ";"
option_list: option_item ("," option_item)*
option_item: NAME "=" option_value
option_value: INTEGER | FLOAT | STRING | "on" | "off"
```

**Semantic handling:**
- Sprint 8: Store in AST, don't process (mock/skip approach)
- Future: Map to nlp2mcp behavior (e.g., limrow affects output verbosity)

**4. Test Fixture Planning (1 hour)**

Identify test cases for option statements:
```markdown
## Option Statement Test Fixtures

### Fixture 1: Single Integer Option
```gams
option limrow = 0;
```
Expected: Parse successfully, store in AST

### Fixture 2: Multi-Option Statement
```gams
option limrow = 0, limcol = 0;
```
Expected: Parse successfully, store multiple options

### Fixture 3: Boolean Option
```gams
option solprint = off;
```
Expected: Parse successfully

### Fixture 4: Option in Context (mhw4dx pattern)
```gams
Set i / 1*10 /;
option limrow = 0, limcol = 0;
Scalar x;
```
Expected: Parse successfully, option doesn't break surrounding statements

### Edge Cases
- Empty option list (syntax error)
- Missing semicolon (syntax error)
- Invalid option name (accept any NAME in Sprint 8)
- Invalid value type (e.g., `option limrow = "string";` - error or accept?)
```

**5. Implementation Effort Validation (1 hour)**

Validate PROJECT_PLAN.md estimate (6-8 hours):
- Grammar changes: 1-2 hours (straightforward)
- AST node creation: 1 hour
- Test fixtures: 2-3 hours (4 fixtures + edge cases)
- Integration testing: 1-2 hours (verify mhw4dx.gms parses)
- Documentation: 1 hour

**Total: 6-9 hours** ✅ (matches estimate)

If complexity higher than expected (e.g., semantic handling required), document risk and recommend scope reduction.

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (750+ lines)

**GAMS Documentation Survey:**
- Comprehensive syntax catalog from official GAMS documentation
- 6 value type categories documented (boolean, integer, real, string, identifier, operation)
- Multi-option statement format confirmed (comma or EOL separated)
- Scope rules documented (sequential execution, reassignment allowed)
- Edge cases identified (no expressions allowed, option names not reserved)

**GAMSLib Usage Analysis:**
- Scanned all 10 GAMSLib models for option statement usage
- Found 3 models using options (30%): mhw4dx, maxmin, mingamma
- All usage is basic integer options: limrow, limcol, decimals
- Multi-option statements present in 2 of 3 models
- No advanced features (projection, per-identifier) in GAMSLib

**Grammar Design:**
- Designed Lark grammar rules for Sprint 8 scope
- `option_stmt`, `option_list`, `option_item`, `option_value` rules
- Supports integer values and on/off boolean keywords
- Extensible design for Sprint 8b additions (float, string values)
- AST node design (OptionStatement dataclass)

**Test Fixture Planning:**
- Identified 8 test cases (5 positive + 3 edge cases)
- Single option, multi-option, multiple statements, options in context
- Boolean on/off support (grammar only)
- Edge cases: empty list, missing semicolon, case insensitivity

**Implementation Effort Validation:**
- Detailed breakdown: 7.5 hours (within 6-8 hour estimate)
- Grammar changes: 1 hour
- AST node creation: 1 hour
- Test fixtures: 3 hours
- Integration testing: 1.5 hours
- Documentation: 1 hour

**Unknown Verification:**
- 1.1: ✅ Semantic handling is straightforward (mock/store approach confirmed)
- 1.2: ✅ Sprint 8 scope (basic integer options) covers 100% of GAMSLib usage
- 1.3: ✅ Option statements are sole blocker for mhw4dx.gms (+10% parse rate confirmed)

### Result

**Key Achievements:**
1. ✅ Comprehensive GAMS option statement syntax documented
2. ✅ Sprint 8 scope validated (basic integer options sufficient for 100% GAMSLib coverage)
3. ✅ Lark grammar designed and ready for implementation
4. ✅ 8 test fixtures planned (positive + edge cases)
5. ✅ 6-8 hour implementation estimate confirmed (detailed breakdown: 7.5 hours)
6. ✅ All 3 unknowns (1.1, 1.2, 1.3) verified with high confidence
7. ✅ Clear Sprint 8 vs Sprint 8b boundary defined

**Sprint 8 Implementation Ready:**
- Grammar rules: 5 rules designed (`option_stmt`, `option_list`, `option_item`, `option_value`)
- Semantic approach: Mock/store (no behavior implementation)
- Test coverage: 8 fixtures cover all Sprint 8 scope patterns
- Unlock confirmation: mhw4dx.gms (+10% parse rate: 2/10 → 3/10)

**Sprint 8 Scope (Confirmed):**
- Integer value options (limrow, limcol, decimals)
- Boolean on/off keywords (grammar support)
- Multi-option statements (comma-separated)
- Case-insensitive keywords and option names
- Mock/store semantic handling

**Sprint 8b Scope (Deferred):**
- Per-identifier display customization (`:` syntax)
- Projection/permutation operations (`<`, `<=`, `>`)
- Float/string value options
- Semantic processing (map options to nlp2mcp behavior)

**Risk Assessment:**
- Complexity: Low (grammar extension only)
- Implementation risk: Low (no interaction with other features)
- Testing risk: Low (straightforward syntax patterns)
- Schedule risk: None (7.5 hour estimate within 6-8 hour range)

**Impact on Sprint 8:**
- Option statements ready for implementation
- High confidence in +10% parse rate unlock
- Clear implementation path reduces Sprint 8 risk
- Exceeds conservative 25% parse rate target (reaches 30% with options alone)

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md

# Should contain syntax patterns
grep -q "Basic Integer Options" docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md

# Should have grammar design
grep -q "option_stmt" docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md

# Should validate effort estimate
grep -q "6-8 hours" docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/OPTION_STATEMENT_RESEARCH.md` (200+ lines)
- GAMS option syntax catalog
- GAMSLib usage analysis
- Lark grammar design
- Test fixture plan (4+ fixtures)
- Effort estimate validation

### Acceptance Criteria

- [x] Option syntax patterns documented (integer, boolean, multi-option, string)
- [x] GAMSLib usage analyzed (which models, which options)
- [x] Lark grammar designed for Sprint 8 scope
- [x] Test fixtures identified (4+ cases) (✅ 8 cases: 5 positive + 3 edge cases)
- [x] Implementation effort validated (6-8 hours confirmed or adjusted) (✅ 7.5 hours confirmed)
- [x] Sprint 8 vs Sprint 8b scope defined (basic options vs advanced)
- [x] Semantic handling approach decided (mock/skip vs full processing) (✅ mock/store approach)

---

## Task 4: Design Parser Error Line Number Tracking

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 4-6 hours  
**Actual Time:** 5 hours  
**Completed:** 2025-11-17  
**Owner:** Development team (UX specialist)  
**Dependencies:** None (builds on Sprint 7 convexity line number infrastructure)  
**Unknowns Verified:** 4.1, 4.2, 4.3, 4.4

### Objective

Design approach to extend SourceLocation tracking from convexity warnings (Sprint 7) to ALL parser errors, achieving 100% coverage of parse errors with file/line/column information. Build on existing infrastructure for low-risk, high-impact UX improvement.

### Why This Matters

Sprint 7 delivered line number tracking for convexity warnings (W301-W305), dramatically improving developer experience. PROJECT_PLAN.md identifies parser error line numbers as Sprint 8 high priority: *"Extend SourceLocation tracking to parser errors (builds on Sprint 7 work)... Risk: Very Low (infrastructure exists)"*

Sprint 7 retrospective recommendation: *"Parser error messages should also include line numbers (Sprint 8 candidate)... Low-effort, high-impact UX improvement (estimated 4-6 hours)"*

**Current state:**
- Convexity warnings: ✅ Line numbers (format: "W301 in eq (10:1): message")
- Parser errors: ❌ No line numbers (just error message and type)

**Target state:**
- Parser errors: ✅ Line numbers (format: "E101: Parse error at file.gms:15:8: message")

### Background

From Sprint 7 Day 8 (CHANGELOG.md lines 270-350), line number tracking implementation:
- **SourceLocation dataclass:** Already exists in `src/ir/symbols.py`
- **Lark metadata extraction:** `_extract_source_location()` in `src/ir/parser.py`
- **Integration pattern:** Add `source_location` field to data structures
- **String formatting:** `SourceLocation.__str__()` produces "file.gms:15:8" or "15:8"

**Existing infrastructure:**
- ✅ SourceLocation dataclass with line, column, filename
- ✅ Lark metadata extraction helper
- ✅ Pattern for propagating location through normalization
- ✅ String formatting for user-facing output

**Gap:**
- ❌ Parser errors don't capture Lark metadata
- ❌ No SourceLocation field in parser exception types
- ❌ Error messages don't include location in output

From Sprint 7 convexity implementation (6 hours total):
- Phase 1: IR structure (1 hour)
- Phase 2: Parser integration (1 hour)
- Phase 3: Normalization preservation (1 hour)
- Phase 4: Consumer integration (1 hour)
- Phase 5: Testing (2 hours)

Parser errors are simpler (no normalization step), so 4-6 hours is reasonable.

### What Needs to Be Done

**1. Survey Parser Error Types (1-2 hours)**

Catalog all parser error types in codebase:
```bash
# Find all parser error raises
grep -r "raise.*Error" src/ir/parser.py src/ir/normalize.py

# Find exception definitions
grep -r "class.*Error" src/
```

**Create catalog:**
```markdown
## Parser Error Types

### Lark-Native Errors (from grammar)
1. **UnexpectedCharacters** - Token not recognized
   - Example: "No terminal matches 'm' at line 35 col 4"
   - Source: Lark parser, generated automatically
   - Location: ✅ Already includes line/column from Lark

2. **UnexpectedToken** - Wrong token in context
   - Example: "Unexpected token Token('RPAR', ')') at line 10"
   - Source: Lark parser
   - Location: ✅ Already includes line/column

### Custom Parser Errors (nlp2mcp-specific)
3. **ParserSemanticError** - Semantic validation failure
   - Example: "Assignments must use numeric constants; got Call(...)"
   - Source: `src/ir/parser.py` validation logic
   - Location: ❌ No line/column tracking
   - Fix: Extract from Lark Tree metadata before validation

4. **UnsupportedSyntaxError** - Feature not yet implemented
   - Example: "Indexed assignments not supported yet"
   - Source: Parser feature flags
   - Location: ❌ No line/column tracking
   - Fix: Extract from Lark Tree metadata

### Other Errors
5. **[List any other custom errors]**

## Coverage Analysis
- Lark errors: ✅ Already have line numbers (Lark provides)
- Custom errors: ❌ Need enhancement (4-5 error types)
```

**2. Design Location Extraction Pattern (1-2 hours)**

Design how to extract location for custom errors:

**Pattern 1: Extract from Lark Tree before validation**
```python
# Before Sprint 8
def _handle_assignment(self, tree):
    # Validate
    if not is_numeric_constant(tree.children[1]):
        raise ParserSemanticError(f"Must use numeric constants; got {tree.children[1]}")

# After Sprint 8
def _handle_assignment(self, tree):
    # Extract location FIRST
    location = self._extract_source_location(tree)
    
    # Validate
    if not is_numeric_constant(tree.children[1]):
        raise ParserSemanticError(
            f"Must use numeric constants; got {tree.children[1]}",
            location=location  # Pass location to exception
        )
```

**Pattern 2: Enhance exception classes**
```python
# Before Sprint 8
class ParserSemanticError(Exception):
    def __init__(self, message: str):
        self.message = message

# After Sprint 8
class ParserSemanticError(Exception):
    def __init__(self, message: str, location: SourceLocation | None = None):
        self.message = message
        self.location = location
    
    def __str__(self) -> str:
        if self.location:
            return f"E301: {self.message} at {self.location}"
        return f"E301: {self.message}"
```

**Pattern 3: CLI error formatting**
```python
# In main CLI or error handler
try:
    parse_gams_model(file_path)
except ParserSemanticError as e:
    if e.location:
        print(f"Parse error at {e.location}: {e.message}", file=sys.stderr)
    else:
        print(f"Parse error: {e.message}", file=sys.stderr)
```

**3. Identify All Error Raise Points (1 hour)**

List all locations in parser that raise custom errors:
```bash
grep -n "raise ParserSemanticError\|raise UnsupportedSyntaxError" src/ir/parser.py
```

**For each raise point, document:**
- Function name
- Error type
- Current message
- How to extract location (which Lark Tree node)
- Estimated effort to fix (usually <10 lines)

**4. Test Strategy Design (1 hour)**

Design how to test line number coverage:

**Test approach:**
```python
def test_parser_semantic_error_has_line_number():
    """ParserSemanticError includes line number"""
    gams_code = """
    Set i / 1*10 /;
    Scalar x;
    x = uniform(1, 10);  # Line 4: function call not supported
    """
    
    with pytest.raises(ParserSemanticError) as exc_info:
        parse_gams_model(gams_code)
    
    # Verify error has location
    assert exc_info.value.location is not None
    assert exc_info.value.location.line == 4
    assert "uniform" in str(exc_info.value)
```

**Coverage test:**
```python
def test_all_parser_errors_have_line_numbers():
    """All custom parser errors include line numbers (100% coverage)"""
    error_test_cases = [
        ("ParserSemanticError", "x = uniform(1, 10);", 1),
        ("UnsupportedSyntaxError", "x(i) = y(i);", 1),
        # ... add case for each custom error type
    ]
    
    for error_type, code, expected_line in error_test_cases:
        with pytest.raises(Exception) as exc_info:
            parse_gams_model(code)
        assert exc_info.value.location is not None
        assert exc_info.value.location.line == expected_line
```

**5. Effort Breakdown (< 1 hour)**

Validate 4-6 hour estimate:
- Error type survey: 1-2 hours
- Design patterns: 1-2 hours
- Exception class enhancement: 0.5-1 hour (2-3 exception classes)
- Parser raise point updates: 1-2 hours (5-10 raise points, ~5-10 min each)
- Test implementation: 1-2 hours (5+ test cases)

**Total: 4.5-8 hours** (slightly over estimate, but acceptable)

If time tight, defer non-critical error types to Sprint 8b.

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` [577 lines]

**Error Type Catalog:**
- Surveyed 2 Lark-native errors (UnexpectedCharacters, UnexpectedToken)
- Surveyed 6 custom errors (ParserSemanticError, ConditionEvaluationError, CircularIncludeError, IncludeDepthExceededError, ValueError, ParseError)
- Determined 58/58 parser errors (100%) already have line numbers via `_error()` helper
- Identified 21 non-parser errors (preprocessor/normalization) not in scope

**Location Extraction Patterns:**
- Documented existing `_error()` helper (parser.py:1010-1024) that extracts location for all 58 raise points
- Documented `_node_position()` helper (parser.py:1027-1042) that extracts line/column from Lark Tree/Token
- Documented `_extract_source_location()` helper (parser.py:1044-1058) from Sprint 7
- Identified gap: ParserSemanticError used instead of ParseError (better UX)

**Exception Class Analysis:**
- ParserSemanticError: Used for all 58 parser errors, already has line/column
- ParseError (errors.py): Unused by parser, has superior UX (source line display, caret pointer, suggestions)
- Recommendation: Consolidate on ParseError class for consistency

**Error Raise Point Inventory:**
- 58 raise points in parser.py using `raise self._error(...)` pattern
- All 58 points already extract location via `_error()` helper
- 2 Lark error types (UnexpectedToken, UnexpectedCharacters) need wrapping in ParseError

**Test Strategy:**
- Designed 5 new test fixtures: 2 for Lark wrapping, 3 for semantic errors with suggestions
- Parameterized test approach for all error types
- Coverage verification: Run existing tests, verify all error paths include location

**Effort Validation:**
- Wrap Lark errors in ParseError: 1 hour
- Create `_parse_error()` helper similar to `_error()`: 1 hour
- Migrate top 5 error types to include suggestions: 1 hour
- Add test fixtures: 1 hour
- **Total: 4 hours** ✅ Within 4-6 hour estimate

**Updated:** `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
- Unknown 4.1: ✅ VERIFIED - 58 custom error raise points already use `_error()` helper
- Unknown 4.2: ✅ VERIFIED - Lark errors have line/column, need wrapping for consistency
- Unknown 4.3: ✅ VERIFIED - 5 new test fixtures needed for 100% coverage
- Unknown 4.4: ✅ VERIFIED - Negligible overhead (only on exceptional path)

### Result

**Critical Discovery:** Parser errors already have 100% line number coverage via the `_error()` helper method. The gap is not infrastructure—it's UX. ParserSemanticError is used throughout, but ParseError (in errors.py) provides superior user experience with source line display, caret pointer, and actionable suggestions.

**Implementation Scope Clarified:**
1. **Wrap Lark errors** in ParseError for consistent formatting
2. **Migrate from ParserSemanticError to ParseError** for better UX
3. **Add suggestions** to top 5 most common error types
4. **Add test fixtures** for new error wrapping

**Not needed:** Build location extraction infrastructure (already exists from Sprint 7)

**Effort Estimate Validated:** 4 hours confirmed (within 4-6 hour estimate from PROJECT_PLAN.md)

**Documentation Quality:** PARSER_ERROR_LINE_NUMBERS.md provides comprehensive design with:
- Executive summary of key findings
- Complete error type catalog (8 types identified)
- Current coverage analysis (58/58 parser errors have line numbers)
- Detailed analysis of `_error()` helper implementation
- Side-by-side comparison: ParserSemanticError vs ParseError UX
- Test strategy with 5 concrete fixtures
- Validated implementation effort breakdown

**Sprint 8 Ready:** All unknowns verified, design complete, effort validated. Implementation can proceed with confidence.

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md

# Should catalog error types
grep -q "UnexpectedCharacters" docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md
grep -q "ParserSemanticError" docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md

# Should have design patterns
grep -q "Extract from Lark Tree" docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md

# Should validate effort
grep -q "4-6 hours" docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/PARSER_ERROR_LINE_NUMBERS.md` (150+ lines)
- Parser error type catalog (Lark-native vs custom)
- Location extraction patterns
- Exception class enhancement design
- Parser raise point inventory
- Test strategy for 100% coverage
- Effort validation

### Acceptance Criteria

- [x] All parser error types cataloged (Lark + custom) - 8 error types identified
- [x] Location extraction pattern designed for custom errors - Documented `_error()`, `_node_position()`, `_extract_source_location()` helpers
- [x] Exception class enhancements specified - Migrate from ParserSemanticError to ParseError
- [x] All raise points identified (5-10 locations) - 58 raise points found in parser.py
- [x] Test strategy defined for 100% coverage - 5 new test fixtures designed
- [x] Effort estimate validated (4-6 hours confirmed or adjusted) - 4 hours confirmed
- [x] Sprint 8 vs Sprint 8b scope defined (critical vs nice-to-have errors) - Core work: Lark wrapping + ParseError migration

---

## Task 5: Design Partial Parse Metrics

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 4-5 hours  
**Actual Time:** 6 hours  
**Completed:** 2025-11-17  
**Owner:** Development team (Metrics specialist)  
**Dependencies:** Task 2 (Per-model analysis - defines what "partial parse" means per model)  
**Unknowns Verified:** 6.1, 6.2, 6.3, 6.4

### Objective

Design system to track and report statement-level parse success for models that partially parse. Enables dashboard to show "himmel16: 85% parsed, needs [i++1 indexing]" instead of binary "FAILED".

### Why This Matters

Sprint 7 retrospective recommendation: *"Consider 'partial parse' metric (e.g., 'parsed 80% of statements')... Shows progress on models that partially parse, more nuanced understanding of parser maturity."*

Binary pass/fail hides progress:
- **Current:** himmel16 = FAILED (0%)
- **Better:** himmel16 = 85% parsed (only i++1 indexing missing)

This motivates work on "almost-there" models and provides better ROI visibility.

**Acceptance criterion from PROJECT_PLAN.md:**
> Dashboard shows statement-level parse success (e.g., "himmel16: 85% parsed")

### Background

Current dashboard (`docs/status/GAMSLIB_CONVERSION_STATUS.md`) shows:
```markdown
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
```

Target dashboard:
```markdown
| himmel16 | 🟡 85% | - | - | ❌ | Parsed 45/53 statements. Missing: [i++1 indexing] |
```

**Key questions:**
- What counts as a "statement"? (Declarations? Assignments? Equations? Comments?)
- How to measure "parsed X out of Y"? (Count AST nodes? Line-based? Statement-based?)
- How to identify which features are missing? (From error messages? Manual annotation?)
- How to display in dashboard? (Percentage? Fraction? Color coding?)

### What Needs to Be Done

**1. Define "Statement" for Parsing Metrics (1-2 hours)**

Survey GAMS statement types and decide what to count:

**Option A: Count top-level declarations**
```gams
Set i / 1*10 /;        # 1 statement
Scalar x;              # 1 statement  
Parameter a;           # 1 statement
Variable y;            # 1 statement
Equation eq;           # 1 statement
eq.. y =e= sum(i, x);  # 1 statement

# Total: 6 statements
```

**Option B: Count all statements (declarations + assignments + equations)**
```gams
Set i / 1*10 /;        # 1 statement
Scalar x / 5 /;        # 1 statement (declaration + initialization)
x = 10;                # 1 statement (assignment)
Parameter a(i);        # 1 statement
a(i) = i.val;          # 1 statement

# Total: 5 statements
```

**Option C: Line-based (exclude comments/blanks)**
```gams
Set i / 1*10 /;        # Line 1
Scalar x;              # Line 2
# Comment               (skip)
                        (skip)
x = 10;                # Line 3

# Total: 3 statements
```

**Recommendation:**
- Count **top-level statements** (declarations, equations, assignments, solve, model, etc.)
- Exclude comments, blank lines, preprocessor directives
- Multi-line statements count as 1 (e.g., multi-line equations)

**2. Design Counting Mechanism (1-2 hours)**

**Approach 1: AST node counting (preferred)**
```python
def count_parsed_statements(ast: Tree) -> Tuple[int, int]:
    """
    Returns (statements_parsed, total_statements)
    
    Counts top-level statement nodes in AST.
    """
    parsed = 0
    for child in ast.children:
        if child.data in ["set_decl", "scalar_decl", "parameter_decl", 
                          "variable_decl", "equation_decl", "equation_def",
                          "assignment", "solve_stmt", "model_decl"]:
            parsed += 1
    
    # Total = parsed (what we got) + unparsed (what failed)
    # Challenge: How to get "unparsed" count?
    return (parsed, total)
```

**Approach 2: Pre-parse statement detection**
```python
def count_total_statements(gams_code: str) -> int:
    """
    Regex-based statement counting before parsing.
    
    Counts lines starting with statement keywords (Set, Scalar, etc.)
    or containing statement patterns (x = ..., eq.., etc.)
    """
    statements = 0
    for line in gams_code.split('\n'):
        line = line.strip()
        if not line or line.startswith('*'):  # Skip blank/comments
            continue
        if re.match(r'^(Set|Scalar|Parameter|Variable|Equation|Model|Solve)\b', line):
            statements += 1
        elif re.match(r'^\w+\s*\(.*\)\s*\.\.', line):  # Equation definition
            statements += 1
        elif re.match(r'^\w+\s*=\s*', line):  # Assignment
            statements += 1
    return statements
```

**Approach 3: Hybrid (use both)**
```python
def measure_partial_parse(gams_file: Path) -> Dict[str, any]:
    """Measure partial parse success"""
    code = gams_file.read_text()
    total_statements = count_total_statements(code)  # Pre-parse
    
    try:
        ast = parse_gams_model(gams_file)
        parsed_statements = count_parsed_statements(ast)  # Post-parse
        success_rate = parsed_statements / total_statements if total_statements > 0 else 0
        
        return {
            "status": "SUCCESS" if success_rate == 1.0 else "PARTIAL",
            "parsed": parsed_statements,
            "total": total_statements,
            "percentage": f"{success_rate * 100:.0f}%",
            "missing_features": []  # Extracted from error
        }
    except ParserError as e:
        # Parse failed, count statements up to error line
        parsed_statements = count_statements_up_to_line(code, e.location.line)
        return {
            "status": "FAILED",
            "parsed": parsed_statements,
            "total": total_statements,
            "percentage": f"{parsed_statements / total_statements * 100:.0f}%",
            "missing_features": extract_missing_features(e)  # From error message
        }
```

**3. Design Missing Feature Extraction (1 hour)**

Map error messages to missing features:

```python
ERROR_TO_FEATURE = {
    "No terminal matches '+'.*i\\+\\+1": "Lead/lag indexing (i++1)",
    "option.*not supported": "Option statements",
    "Indexed assignments not supported": "Indexed assignments",
    "No terminal matches 'm'.*mx.*objdef": "Model sections (mx)",
    # ... add more patterns
}

def extract_missing_features(error: ParserError) -> List[str]:
    """Extract feature names from error message"""
    for pattern, feature in ERROR_TO_FEATURE.items():
        if re.search(pattern, str(error)):
            return [feature]
    return ["Unknown feature"]
```

**4. Dashboard Integration Design (1 hour)**

Design how partial metrics appear in dashboard:

**Before Sprint 8:**
```markdown
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
```

**After Sprint 8:**
```markdown
| Model | Parse | Partial | Convert | E2E | Notes |
|-------|-------|---------|---------|-----|-------|
| himmel16 | 🟡 85% | 45/53 | - | ❌ | Missing: Lead/lag indexing (i++1) |
| circle | 🟡 70% | 28/40 | - | ❌ | Missing: Function calls in assignments |
| mhw4d | ✅ 100% | 156/156 | - | ❌ | Fully parsed |
```

**Color coding:**
- ✅ 100%: Full parse success
- 🟡 50-99%: Partial parse
- ⚠️ 25-49%: Low parse rate
- ❌ 0-24%: Parse failed

**5. Ingestion Pipeline Update (<1 hour)**

Update `scripts/ingest_gamslib.py` to collect partial metrics:

```python
# In ingest_gamslib.py
for model_file in gamslib_models:
    metrics = measure_partial_parse(model_file)
    
    report_entry = {
        "model_name": model_file.stem,
        "parse_status": metrics["status"],
        "parse_percentage": metrics["percentage"],
        "parsed_statements": metrics["parsed"],
        "total_statements": metrics["total"],
        "missing_features": metrics["missing_features"],
        # ... existing fields
    }
```

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` [876 lines]

**Statement Definition:**
- Defined "statement" as **"Logical lines"** (non-empty, non-comment lines)
- Pragmatic choice: Parser doesn't support partial parsing (Lark Earley stops on first syntax error, no partial AST)
- Granularity: Counts lines with code content (excludes blank lines, `*` comments, `$ontext...$offtext` blocks)
- True statement counting would require parser modifications (10+ hours), line-based provides sufficient approximation

**Counting Mechanism:**
- **Line scanning approach** (no parsing required)
- `count_logical_lines(source)` - Counts non-empty, non-comment lines in full source
- `calculate_parse_progress(source, error_line)` - Counts lines before error vs total
- Works for both syntax errors (partial parse) and semantic errors (full parse + error after)
- Implementation complexity: Low (2 hours for counting logic + tests)

**Missing Feature Extraction:**
- **Pattern matching on error messages** (regex-based)
- Two extraction methods:
  - Lark syntax errors: Heuristic patterns (i++1 detection, short model syntax, etc.)
  - Semantic errors: Explicit "not supported" message patterns
- Coverage: 70-80% of GAMSLib failures can be annotated with specific features
- Example mappings:
  - `i++1` in error → "i++1 indexing (lead/lag)"
  - `got Call(uniform)` → "function calls in assignments"
  - `option.*not supported` → "option statements"

**Dashboard Integration:**
- **New columns:** "Progress" and "Missing Features" (backward compatible)
- **Enhanced Parse column:** ✅ (100%) / ⚠️ (partial) / ❌ (failed)
- **Progress format:** "92% (22/24)" showing lines_parsed/total_lines
- **Missing features format:** Comma-separated list, limit to 2 for readability
- **New KPIs:** Average parse progress, models >90% parsed, partial success rate
- Backward compatible: Existing columns unchanged, new columns are additive

**Ingestion Pipeline:**
- **Enhanced ModelResult dataclass** with new optional fields:
  - `parse_progress_lines_parsed` (int)
  - `parse_progress_total_lines` (int)
  - `parse_progress_percentage` (float)
  - `missing_features` (list[str])
  - `error_line` (int)
- **Updated parse_model()** function to read source, extract error line, count lines, extract features
- **Enhanced calculate_kpis()** with partial parse metrics (avg progress, high progress count, etc.)
- **Schema version field** in JSON report for future migrations

**Effort Validation:**
- Line counting logic: 2 hours
- Missing feature extraction: 2 hours
- Ingestion pipeline updates: 1 hour
- Dashboard template updates: 1 hour
- **Total: 6 hours** (slightly over 4-5 hour estimate, but within acceptable range)

**Updated:** `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
- Unknown 6.1: ✅ VERIFIED - Statement = logical lines (pragmatic approximation)
- Unknown 6.2: ✅ VERIFIED - Line scanning works for all cases (no parser required)
- Unknown 6.3: ✅ VERIFIED - Pattern matching achieves 70-80% coverage
- Unknown 6.4: ✅ VERIFIED - Dashboard changes fully backward compatible

### Result

**Key Finding:** Parser does **not** support partial parsing (Lark Earley parser stops on first syntax error with no partial AST). Sprint 8 will use **line-based progress tracking** as pragmatic approximation instead of true statement counting.

**Implementation Scope Clarified:**
1. **Line counting** instead of statement counting (avoids 10+ hours of parser modifications)
2. **Pattern matching** for missing feature extraction (70-80% coverage achievable)
3. **Dashboard enhancement** with new columns (backward compatible)
4. **Ingestion pipeline** updates with optional new fields

**Design Quality:** PARTIAL_PARSE_METRICS.md provides comprehensive design with:
- Executive summary of key findings (no partial parsing support)
- Statement definition rationale (logical lines vs true statements)
- Detailed counting algorithm (handles multiline comments, blank lines, etc.)
- Missing feature extraction patterns with coverage estimates
- Dashboard mockup with before/after examples
- Validation examples (himmel16: 92%, circle: 100%, mhw4d: 100%)
- Backward compatibility analysis (JSON schema, markdown table, CI)
- Future enhancements roadmap (error-recovering parser, ML-based extraction, etc.)

**Validation Examples:**
- **himmel16.gms:** 92% (22/24 lines), needs [i++1 indexing]
- **circle.gms:** 100% (24/24 lines), needs [function calls in assignments] (semantic error after full parse)
- **mhw4d.gms:** 100% (18/18 lines), no errors ✅

**Dashboard Enhancement Preview:**
```markdown
| Model | Parse | Progress | Missing Features | Convert | Solve | E2E |
|-------|-------|----------|------------------|---------|-------|-----|
| himmel16 | ⚠️ | 92% (22/24) | i++1 indexing | - | - | ❌ |
| circle | ⚠️ | 100% (24/24) | function calls | - | - | ❌ |
| mhw4d | ✅ | 100% (18/18) | - | ⚠️ | - | ❌ |
```

**Sprint 8 Ready:** All unknowns verified, design complete, effort validated (6 hours = upper bound). Implementation can proceed with confidence. Line-based approach is pragmatic tradeoff between accuracy and implementation effort.

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md

# Should define statement counting
grep -q "Count top-level statements" docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md

# Should have dashboard mockup
grep -q "🟡 85%" docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md

# Should validate effort
grep -q "4-5 hours" docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/PARTIAL_PARSE_METRICS.md` (150+ lines)
- Statement definition for metrics
- Counting mechanism design (pre-parse + post-parse)
- Missing feature extraction patterns
- Dashboard integration mockup
- Ingestion pipeline update design

### Acceptance Criteria

- [x] "Statement" defined for counting - Logical lines (non-empty, non-comment)
- [x] Counting mechanism designed - Line scanning (no parsing required)
- [x] Missing feature extraction patterns created - Pattern matching on error messages (70-80% coverage)
- [x] Dashboard mockup shows partial percentages - "himmel16: 92% (22/24)"
- [x] Ingestion pipeline updates specified - Enhanced ModelResult with optional new fields
- [x] Effort estimate validated - 6 hours (within acceptable range)
- [x] Works with existing dashboard format - Backward compatible (new columns additive)

---

## Task 6: Research Error Message Enhancement Patterns

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Actual Time:** ~4 hours  
**Completed:** 2025-11-17  
**Owner:** Development team (UX specialist)  
**Dependencies:** Task 4 (Parser error line numbers - provides foundation)  
**Unknowns Verified:** 5.1, 5.2, 5.3, 5.4

### Objective

Research error message enhancement patterns from mature parsers (Rust, Python, TypeScript) to design actionable, helpful error messages for GAMS parser. Focus on "did you mean?" suggestions, syntax fix hints, and documentation links.

### Why This Matters

PROJECT_PLAN.md Sprint 8 component: *"Improved Error Messages - Enhance parser error messages with actionable suggestions, add 'did you mean?' hints for common mistakes (Effort: 3-5 hours)"*

Current error messages are cryptic:
```
No terminal matches '+' in the current parser context, at line 46 col 39
Expected one of: * RPAR * COMMA
```

Better error message (target):
```
Parse error at himmel16.gms:46:39
  areadef(i).. area(i) =e= 0.5*(x(i)*y(i++1) - y(i)*x(i++1));
                                      ^^^^
Error: Lead/lag indexing not supported yet

Hint: GAMS allows i++1 and i--1 for sequential indexing, but this
      parser doesn't support it yet. This feature is planned for Sprint 8b.

Help: See docs/PARSER_LIMITATIONS.md for current parser capabilities
```

**Sprint 7 retrospective:** *"UX improvements are low-effort, high-impact."*

### Background

Sprint 7 delivered line number tracking (Task 4 extends this). Now we have location, need helpful messages.

Best practices from other parsers:
- **Rust:** Detailed error explanations with code snippets and suggestions
- **Python 3.10+:** "Did you mean?" for typos, multi-line context
- **TypeScript:** Type mismatch hints, documentation links
- **ESLint:** Auto-fix suggestions with `--fix` flag

### What Needs to Be Done

**1. Survey Error Message Best Practices (1-2 hours)**

Research 3-5 mature parsers for error message patterns:

**Rust compiler errors:**
```
error[E0425]: cannot find value `x` in this scope
  --> src/main.rs:5:10
   |
5  |     println!("{}", x);
   |                    ^ not found in this scope
   |
help: a local variable with a similar name exists
   |
3  |     let y = 10;
   |         ^
```

**Python 3.10+ errors:**
```
NameError: name 'prin' is not defined. Did you mean: 'print'?
```

**TypeScript errors:**
```
Property 'lenght' does not exist on type 'string'. Did you mean 'length'?
```

**Create catalog:**
```markdown
## Error Message Patterns

### Pattern 1: "Did you mean?" for typos
- When: Identifier not found, close match exists
- Example: "Set 'indeces' not found. Did you mean 'indices'?"
- Technique: Levenshtein distance, difflib.get_close_matches()

### Pattern 2: Code context with caret
- When: Syntax error at specific location
- Example: Show line with ^^^^ under error location
- Technique: Extract source line, calculate column offset

### Pattern 3: Explain the rule
- When: Semantic error (valid syntax, invalid meaning)
- Example: "Option statements must use = for assignment, not :="
- Technique: Error-specific explanations

### Pattern 4: Suggest fix
- When: Common mistake with known fix
- Example: "Missing semicolon. Try adding ';' at end of line."
- Technique: Pattern matching on error context

### Pattern 5: Documentation link
- When: Feature not supported or advanced syntax
- Example: "See docs/GAMS_FEATURES.md for supported set syntax"
- Technique: Map error types to doc sections
```

**2. Categorize GAMS Parser Errors (1 hour)**

Map GAMS errors to enhancement patterns:

```markdown
## GAMS Error Categories

### Category A: Unsupported Features (suggest future support)
- i++1 indexing → "Lead/lag indexing planned for Sprint 8b"
- option statements → "Option statements added in Sprint 8"
- indexed assignments → "Indexed assignments planned for Sprint 8"

### Category B: Syntax Typos (did you mean?)
- Set 'indeces' → "Did you mean 'indices'?"
- Equation 'obj_def' → "Did you mean 'objdef'?"
- Parameter typo → Suggest closest match

### Category C: Missing Punctuation (show fix)
- Missing semicolon → "Try adding ';' at end of line X"
- Missing comma in set → "Set elements should be comma-separated"

### Category D: Semantic Errors (explain rule)
- Function calls in assignments → "Assignments must use constants or parameters"
- Invalid index → "Index 'j' not defined in set declaration"

### Category E: Complex Syntax (documentation link)
- Multi-dimensional sets → "See docs/ADVANCED_SETS.md"
- Conditional equations → "See docs/EQUATIONS.md#conditional"
```

**3. Design Enhancement Framework (1 hour)**

Design system to enhance error messages:

**Error message class:**
```python
@dataclass
class EnhancedError:
    """Enhanced error with context and suggestions"""
    error_type: str  # "E301", "E302", etc.
    message: str  # Core error message
    location: SourceLocation  # File/line/column
    code_context: str | None  # Source line with error
    caret_offset: int | None  # Column for ^^^^
    hint: str | None  # Actionable suggestion
    help_link: str | None  # Documentation URL
    
    def format(self) -> str:
        """Format for CLI output"""
        lines = []
        lines.append(f"{self.error_type}: {self.message} at {self.location}")
        
        if self.code_context:
            lines.append(f"  {self.code_context}")
            if self.caret_offset:
                lines.append(f"  {' ' * self.caret_offset}^^^^")
        
        if self.hint:
            lines.append(f"\nHint: {self.hint}")
        
        if self.help_link:
            lines.append(f"Help: {self.help_link}")
        
        return '\n'.join(lines)
```

**Enhancement rules:**
```python
ENHANCEMENT_RULES = {
    "i\\+\\+1": {
        "hint": "Lead/lag indexing (i++1, i--1) planned for Sprint 8b",
        "help": "docs/PARSER_LIMITATIONS.md#indexing"
    },
    "option.*not supported": {
        "hint": "Option statements added in Sprint 8",
        "help": "docs/GAMS_FEATURES.md#options"
    },
    # ... more rules
}

def enhance_error(error: ParserError) -> EnhancedError:
    """Add context, hints, help to parser error"""
    for pattern, enhancement in ENHANCEMENT_RULES.items():
        if re.search(pattern, str(error)):
            return EnhancedError(
                error_type=f"E{error.code}",
                message=error.message,
                location=error.location,
                code_context=extract_code_context(error),
                hint=enhancement.get("hint"),
                help_link=enhancement.get("help")
            )
    return EnhancedError(...)  # Default enhancement
```

**4. Test Strategy (<1 hour)**

Design tests for error message quality:

```python
def test_unsupported_feature_error_has_hint():
    """Unsupported features include helpful hint"""
    code = "x(i) = y(i++1);"  # i++1 not supported
    
    try:
        parse_gams_model(code)
    except ParserError as e:
        enhanced = enhance_error(e)
        assert "Lead/lag indexing" in enhanced.hint
        assert "Sprint 8b" in enhanced.hint
        assert "docs/PARSER_LIMITATIONS.md" in enhanced.help_link

def test_typo_error_suggests_close_match():
    """Typos in identifiers suggest close matches"""
    code = """
    Set i / 1*10 /;
    Set j / 1*5 /;
    Scalar x;
    x = sum(k, ...);  # Typo: k not defined, should be i or j
    """
    
    try:
        parse_gams_model(code)
    except ParserError as e:
        enhanced = enhance_error(e)
        assert "Did you mean" in enhanced.hint
        assert "i" in enhanced.hint or "j" in enhanced.hint
```

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` [1184 lines]

**Error Message Pattern Survey:**
- Surveyed 6 patterns from Rust (rustc), Python (CPython 3.10+), and TypeScript (tsc)
- Pattern 1: Source context + caret pointer (HIGH applicability to GAMS)
- Pattern 2: "Did you mean?" suggestions (HIGH applicability)
- Pattern 3: Contextual hints (HIGH applicability)
- Pattern 4: Multi-line context (MEDIUM applicability, defer to Sprint 8b)
- Pattern 5: Documentation links (LOW applicability, defer to Sprint 9+)
- Pattern 6: Fix-it automation (LOW applicability, requires LSP integration)
- Created comprehensive comparison table with effort estimates

**GAMS Error Categorization:**
- Identified 5 error categories with frequency analysis:
  - Category 1: Keyword typos (5-10%, HIGH priority) → difflib suggestions
  - Category 2: Unsupported features (60-70%, HIGH priority) → Explanatory messages + roadmap
  - Category 3: Punctuation errors (15-20%, HIGH priority) → Context-aware hints
  - Category 4: Semantic errors (10-15%, MEDIUM priority) → Expected vs actual explanations
  - Category 5: Structural errors (5-10%, LOW priority, defer)
- Each category mapped to specific enhancement patterns
- Auto-detection logic designed for categorizing errors

**Enhancement Framework Design:**
- Designed ErrorEnhancer class architecture
- Created EnhancedError dataclass with source line, caret pointer, suggestions
- Designed 12 enhancement rules covering 80%+ of GAMS parse errors:
  - Rule 1: Keyword typo detection (difflib with 0.6 cutoff)
  - Rule 2: Set bracket error ([...] → /.../)
  - Rule 3: Missing semicolon detection
  - Rule 4: Unsupported feature explanation
  - Rule 5: Function call error hints
  - Rule 6: Option name typo detection
  - Rule 7: Lead/lag indexing explanation
  - Rule 8: Model section syntax hints
  - Rule 9: Unmatched parentheses
  - Rule 10: Indexed assignment hints
  - Rule 11: Expected vs actual type explanations
  - Rule 12: Case sensitivity hints
- Integration points with parse_text() and parse_file() specified

**Test Strategy:**
- Designed 5 test fixtures covering main error categories:
  - Fixture 1: Keyword typo (Scaler → Scalar)
  - Fixture 2: Set bracket error ([...] → /.../)
  - Fixture 3: Missing semicolon detection
  - Fixture 4: Unsupported feature explanation
  - Fixture 5: Function call limitation hints
- Coverage tests to ensure all categories generate suggestions
- Integration tests for CLI error display

**Effort Validation:**
- Phase 1: Core infrastructure (1.5 hours)
- Phase 2: Suggestion rules (1.5 hours)
- Phase 3: Integration (0.5 hours)
- Phase 4: Testing (1 hour)
- **Total: 4.5 hours** (within 3-5 hour estimate)
- Risk assessment: LOW (standalone component, no parser modifications)

**Updated:** `docs/planning/EPIC_2/SPRINT_8/KNOWN_UNKNOWNS.md`
- Unknown 5.1: ✅ VERIFIED - "Did you mean?" suggestions feasible with difflib (80%+ precision)
- Unknown 5.2: ✅ VERIFIED - 6 patterns identified, Patterns 1-3 selected for Sprint 8
- Unknown 5.3: ✅ VERIFIED - 5 categories with tailored enhancement approaches
- Unknown 5.4: ✅ VERIFIED - Lark provides sufficient context (error type, token, location, source line)

### Result

**Key Achievements:**
1. ✅ Comprehensive pattern survey from mature parsers (Rust, Python, TypeScript)
2. ✅ GAMS error categorization with frequency analysis (5 categories)
3. ✅ Enhancement framework designed (ErrorEnhancer + 12 rules)
4. ✅ Sprint 8 scope defined (Patterns 1-3, Categories 1-3 = 4.5 hours)
5. ✅ All 4 unknowns (5.1-5.4) verified with high confidence
6. ✅ Implementation ready design with test strategy

**Error Message Enhancement Impact:**
- **80-100% of errors** will get actionable guidance
- **60-70% of errors** (unsupported features) get clear explanations with roadmap references
- **15-20% of errors** (punctuation) get actionable corrections
- **5-10% of errors** (typos) get "did you mean?" suggestions

**Sprint 8 Implementation Scope:**
- Pattern 1: Source context + caret (extend existing ParseError) - 1 hour
- Pattern 2: "Did you mean?" for keyword typos - 1 hour
- Pattern 3: Contextual hints for punctuation errors - 1.5 hours
- Rules 1-5: Core enhancement rules - 1 hour
- **Total Sprint 8: 4.5 hours** (HIGH priority)

**Sprint 8b Deferrals:**
- Rules 6-12: Additional enhancement rules - 2-3 hours
- Pattern 4: Multi-line context - 5-6 hours
- Category 5: Structural errors - 2-3 hours

**User Experience Impact:**
- Reduces time to fix parse errors (faster iteration)
- Lowers learning curve for new GAMS users
- Professional, polished error messages (improves tool perception)
- Proven patterns from industry-leading parsers (Rust, Python, TypeScript)

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md

# Should catalog patterns
grep -q "Did you mean" docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md

# Should have enhancement rules
grep -q "i\\+\\+1" docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md

# Should validate effort
grep -q "3-5 hours" docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/ERROR_MESSAGE_ENHANCEMENTS.md` (120+ lines)
- Error message pattern catalog (5+ patterns)
- GAMS error categorization
- Enhancement framework design
- Enhancement rules (10+ patterns)
- Test strategy

### Acceptance Criteria

- [x] Error message patterns cataloged from 3+ mature parsers (✅ 6 patterns from Rust, Python, TypeScript)
- [x] GAMS errors categorized (unsupported, typos, punctuation, semantic, complex) (✅ 5 categories identified with frequency analysis)
- [x] Enhancement framework designed (EnhancedError class) (✅ ErrorEnhancer + EnhancedError dataclasses)
- [x] Enhancement rules created (10+ error patterns) (✅ 12 rules covering 80%+ of errors)
- [x] Test strategy defined (✅ 5 test fixtures + coverage tests + integration tests)
- [x] Effort estimate validated (3-5 hours) (✅ 4.5 hours confirmed)
- [x] Builds on Task 4 (parser error line numbers) (✅ Extends ParseError with suggestions)

---

## Task 7: Survey High-ROI Parser Features

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 5-7 hours  
**Actual Time:** ~6 hours  
**Completed:** 2025-11-17  
**Owner:** Development team (Parser specialist)  
**Dependencies:** Task 2 (Feature matrix - identifies indexed assignments vs function calls ROI)  
**Unknowns Verified:** 3.1, 3.2, 3.3

### Objective

Deep research on the second Sprint 8 feature (indexed assignments OR function calls based on Task 2 analysis). Validate effort estimate (6-8 hours), identify complexity risks, and design implementation approach.

### Why This Matters

PROJECT_PLAN.md Sprint 8: *"One Additional High-ROI Feature (choose based on analysis) - Either: Simple indexed assignments (if unlocks 2+ models) OR: Function call syntax improvements (if unlocks 2+ models) - Effort: 6-8 hours, Risk: Medium"*

Task 2 feature matrix determines which feature has higher ROI. This task provides implementation-ready design for the selected feature.

**Critical decision:** Sprint 8 success (25% parse rate) depends on choosing the right feature. Wrong choice = wasted effort + missed target.

### Background

Sprint 7 retrospective: *"Prefer complete implementations of fewer features over partial implementations of many."* Need full implementation, not mock/skip.

**Candidate A: Indexed Assignments**
- Example: `x(i) = y(i);` or `a(i) = b(i) + c(i);`
- Complexity: Medium (grammar changes, semantic validation)
- Known model: mathopt1.gms
- Unknown: How many other models?

**Candidate B: Function Calls in Assignments**
- Example: `x = uniform(1.0, 10.0);` or `y = sqrt(z);`
- Complexity: Medium (parse function calls, validate contexts)
- Known model: circle.gms (but needs preprocessor too)
- Unknown: Single-feature unlock or multi-feature dependency?

### What Needs to Be Done

**1. Review Task 2 Feature Recommendation (1 hour)**

Extract from Task 2 GAMSLIB_FEATURE_MATRIX.md:
- Which feature was recommended? (indexed assignments or function calls)
- What's the unlock rate? (10%? 20%?)
- Which models depend on it?
- Any multi-feature dependencies?

**If indexed assignments recommended, proceed to Section 2A.**  
**If function calls recommended, proceed to Section 2B.**

**2A. Indexed Assignments Deep Dive (4-6 hours if selected)**

**2A.1. GAMS Syntax Survey (1-2 hours)**

Survey GAMS documentation for indexed assignment patterns:

```markdown
## Indexed Assignment Syntax

### Simple Indexed Assignment
```gams
Set i / 1*10 /;
Parameter a(i), b(i);
a(i) = 5;           # Constant assignment
b(i) = a(i);        # Copy from another parameter
```

### Arithmetic Indexed Assignment
```gams
a(i) = b(i) + c(i);     # Addition
a(i) = 2 * b(i);        # Multiplication with constant
a(i) = b(i) / c(i);     # Division
```

### Indexed Assignment with Functions
```gams
a(i) = sqrt(b(i));      # Function call on indexed parameter
a(i) = sin(i.val);      # Using .val attribute
```

### Multi-Dimensional Indexed Assignment
```gams
Set i, j;
Parameter a(i,j), b(i,j);
a(i,j) = b(i,j) + 1;    # 2D assignment
```

### Conditional Indexed Assignment
```gams
a(i)$(ord(i) > 5) = b(i);    # Conditional filter
```

**Sprint 8 Scope:** Simple arithmetic (no conditionals, no .val, defer to Sprint 8b)
```

**2A.2. Grammar Design (1-2 hours)**

Design Lark grammar for indexed assignments:

```lark
// Current: Assignments only support scalars
assignment: NAME "=" expression ";"

// Sprint 8: Add indexed assignments
assignment: NAME index_list? "=" expression ";"
index_list: "(" NAME ("," NAME)* ")"

// Example matches:
// x = 5;           -> NAME="x", index_list=None, expression=Const(5)
// a(i) = 10;       -> NAME="a", index_list=["i"], expression=Const(10)
// b(i,j) = a(i,j); -> NAME="b", index_list=["i","j"], expression=...
```

**Semantic validation:**
- Indices must be defined sets
- LHS indices must match RHS indices (a(i) = b(i) OK, a(i) = b(j) error)
- Parameter must be declared as indexed

**2A.3. Implementation Plan (1 hour)**

Break down implementation:
- Grammar changes: 1 hour
- AST node creation (IndexedAssignment): 1 hour
- Semantic validation: 2-3 hours
  - Check indices are defined
  - Check index arity matches declaration
  - Check RHS expression uses same indices
- Test fixtures: 2-3 hours (4+ test cases)

**Total: 6-9 hours** (matches estimate)

**2A.4. Test Fixture Design (1 hour)**

Identify test cases:
```markdown
### Fixture 1: Simple Indexed Assignment
```gams
Set i / 1*5 /;
Parameter a(i);
a(i) = 10;
```
Expected: Parse successfully

### Fixture 2: Arithmetic Indexed Assignment
```gams
Set i / 1*5 /;
Parameter a(i), b(i), c(i);
a(i) = b(i) + c(i);
```
Expected: Parse successfully

### Fixture 3: Multi-Dimensional (if scope permits)
```gams
Set i, j;
Parameter a(i,j);
a(i,j) = 5;
```
Expected: Parse successfully OR defer to Sprint 8b

### Fixture 4: Index Mismatch (error case)
```gams
Set i, j;
Parameter a(i), b(j);
a(i) = b(j);  # Error: index mismatch
```
Expected: Semantic error
```

**2B. Function Calls in Assignments Deep Dive (4-6 hours if selected)**

**2B.1. GAMS Function Call Survey (1-2 hours)**

Survey GAMS built-in functions and call syntax:

```markdown
## Function Call Syntax

### Numeric Functions
- `sqrt(x)` - Square root
- `exp(x)` - Exponential
- `log(x)` - Natural log
- `sin(x), cos(x), tan(x)` - Trigonometric
- `abs(x)` - Absolute value
- `power(x, y)` or `x ** y` - Exponentiation

### Random Functions
- `uniform(a, b)` - Uniform random in [a, b]
- `normal(mean, stddev)` - Normal distribution

### Aggregation Functions
- `sum(i, expr)` - Already supported in expressions
- `prod(i, expr)` - Product (defer to Sprint 8b?)

### String Functions (defer to Sprint 8b)
- `card(set)` - Cardinality
- `ord(element)` - Ordinal position

**Sprint 8 Scope:** Numeric functions only (sqrt, exp, log, sin, cos, uniform, etc.)
```

**2B.2. Grammar Design (1-2 hours)**

Function calls already parsed in expressions (sum works). Need to enable in assignment RHS:

```lark
// Current: Expressions support some function calls (sum)
expression: ... | function_call

function_call: NAME "(" argument_list? ")"
argument_list: expression ("," expression)*

// Sprint 8: Expand function_call to cover more built-ins
// No grammar change needed, just semantic validation

// Validate function names:
BUILTIN_FUNCTIONS = ["sqrt", "exp", "log", "sin", "cos", "tan", 
                     "abs", "uniform", "normal"]

def validate_function_call(name: str):
    if name not in BUILTIN_FUNCTIONS:
        raise ParserSemanticError(f"Unknown function: {name}")
```

**Semantic handling:**
- Parse function calls (may already work?)
- Validate function names against whitelist
- Defer evaluation to runtime (parser doesn't execute)

**2B.3. Implementation Plan (1 hour)**

Break down implementation:
- Grammar audit: 0.5 hour (check if already supported)
- Function whitelist: 0.5 hour
- Semantic validation: 2-3 hours
  - Built-in function check
  - Argument count validation (sqrt expects 1 arg, uniform expects 2)
- Test fixtures: 2-3 hours (5+ functions)

**Total: 5-7.5 hours** (matches estimate)

**2B.4. Test Fixture Design (1 hour)**

Identify test cases:
```markdown
### Fixture 1: sqrt Function
```gams
Scalar x, y;
x = 10;
y = sqrt(x);
```
Expected: Parse successfully

### Fixture 2: Trigonometric Functions
```gams
Scalar angle, result;
angle = 3.14159;
result = sin(angle);
```
Expected: Parse successfully

### Fixture 3: uniform Random
```gams
Scalar x;
x = uniform(1.0, 10.0);
```
Expected: Parse successfully (circle.gms pattern)

### Fixture 4: Nested Function Calls
```gams
Scalar x;
x = sqrt(abs(-25));
```
Expected: Parse successfully

### Fixture 5: Unknown Function (error case)
```gams
Scalar x;
x = unknown_func(10);
```
Expected: Semantic error
```

**3. Risk Assessment (1 hour)**

Identify implementation risks:

**Indexed Assignments Risks:**
- Index validation complexity (set membership, arity matching)
- Multi-dimensional indexing edge cases
- Conditional assignments ($-filters) out of scope

**Function Calls Risks:**
- Argument type checking (e.g., sqrt needs numeric, not set)
- Argument count validation (uniform needs exactly 2 args)
- Nested function calls (sqrt(abs(x)))

**Mitigation:**
- Start with simple cases, defer complex to Sprint 8b
- Comprehensive test coverage for edge cases
- Clear error messages for unsupported patterns

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md` [896 lines]

**Feature Selection:**
- Reviewed Task 2 recommendation: **Indexed assignments** selected over function calls
- Rationale: Higher ROI (unlocks 2 models vs 1 model), +20% parse rate vs +10%
- Confirmed choice based on per-model dependency analysis

**GAMS Syntax Survey:**
- Documented 4 syntax patterns for indexed assignments:
  1. Simple 1D indexed assignment (`p('i1') = 10;`)
  2. Multi-dimensional 2D/3D (`report('x1','global') = 1;`)
  3. Variable attribute access (`xdiff = x1.l;`)
  4. Indexed expressions on RHS (`data('diff') = data('global') - data('solver');`)
- Complexity assessment: Medium (grammar minimal, semantic handling moderate)
- All patterns found in mathopt1.gms and trig.gms (unlocked models)

**Grammar Design:**
- Lark grammar changes: **1 line** (add `.m` to BOUND_K token for marginal attribute)
- Grammar already 95% supports indexed assignments via existing `ref_indexed` rule
- Integration points: `lvalue` rule already includes `ref_indexed` and `ref_bound`
- Estimated grammar effort: **15 minutes** (minimal changes)

**Implementation Plan:**
- Phase 1: Grammar extension (15 minutes) - Extend BOUND_K token
- Phase 2: Semantic handlers (4.5 hours) - Indexed params, var attributes, expressions
- Phase 3: Testing (1.5 hours) - 5 test fixtures + integration tests
- Phase 4: Documentation (30 minutes) - CHANGELOG + docs
- **Total: 6.5 hours** (within 6-8 hour estimate, +1.5h risk buffer = 8h upper bound)

**Test Fixture Design:**
- Designed 5 test fixtures covering all patterns:
  1. Simple 1D indexed assignment (basic case)
  2. Multi-dimensional 2D (mathopt1.gms pattern)
  3. Variable attributes (trig.gms pattern)
  4. Indexed expressions (mathopt1.gms RHS pattern)
  5. Error handling - index count mismatch (validation)
- Coverage: 100% of GAMS syntax patterns + error cases

**Risk Assessment:**
- Risk 1: Variable attribute semantics (Medium/Low) - Store as initial values, document limitation
- Risk 2: Indexed params in expressions (High/Low) - Create ParameterRef IR node
- Risk 3: Index validation complexity (Low/Very Low) - Validate count only, defer domain checks
- Risk 4: Grammar ambiguity (Low/Very Low) - Priority rules prevent conflicts
- **Overall Risk: Medium** (acceptable for Sprint 8)

### Result

**Feature Confirmed: Indexed Assignments**
- Task 2 recommendation validated: Indexed assignments > Function calls (2 models vs 1 model)
- Deep dive confirms appropriate choice for Sprint 8
- No hidden complexity found in GAMS syntax or implementation

**Models Unlocked:**
- mathopt1.gms (95% confidence) - Primary blocker: 2D indexed assignments
- trig.gms (85% confidence) - Primary blocker: Variable `.l` attribute access
- Combined unlock rate: +20% parse rate (3/10 → 5/10 models)

**Effort Estimate Validated:**
- Original estimate: 6-8 hours (from PROJECT_PLAN.md)
- Detailed breakdown: 6.5 hours (grammar 15min + semantic 4.5h + testing 1.5h + docs 30min)
- Risk buffer: +1.5 hours for edge cases
- **Total with buffer: 8 hours** (upper bound confirmed)

**Sprint 8 Impact:**
- Option statements: +10% (2/10 → 3/10)
- Indexed assignments: +20% (3/10 → 5/10)
- **Combined: 50% parse rate optimistic, 40% conservative**
- Exceeds Sprint 8 target of 25-30% parse rate

**Implementation Ready:**
- Grammar design complete (1 line change identified)
- Semantic handler pseudocode documented
- Test fixtures designed (5 cases)
- Risk mitigation strategies defined
- Clear Sprint 8 vs Sprint 8b boundary (all patterns in scope)

### Verification

```bash
# Document should exist (one of these based on Task 2 recommendation)
test -f docs/planning/EPIC_2/SPRINT_8/INDEXED_ASSIGNMENTS_RESEARCH.md || \
test -f docs/planning/EPIC_2/SPRINT_8/FUNCTION_CALLS_RESEARCH.md

# Should have syntax survey
grep -q "Syntax" docs/planning/EPIC_2/SPRINT_8/*_RESEARCH.md

# Should have grammar design
grep -q "grammar\|Grammar" docs/planning/EPIC_2/SPRINT_8/*_RESEARCH.md

# Should validate effort
grep -q "6-8 hours" docs/planning/EPIC_2/SPRINT_8/*_RESEARCH.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/[INDEXED_ASSIGNMENTS|FUNCTION_CALLS]_RESEARCH.md` (200+ lines)
- GAMS syntax survey for selected feature
- Grammar design (Lark rules)
- Implementation plan with effort breakdown
- Test fixture design (4-5 fixtures)
- Risk assessment

### Acceptance Criteria

- [x] Task 2 feature recommendation reviewed
- [x] Selected feature (indexed assignments OR function calls) researched in depth
- [x] GAMS syntax patterns cataloged
- [x] Grammar design completed
- [x] Implementation plan created with 6-8 hour breakdown
- [x] Test fixtures identified (4-5 cases)
- [x] Risks assessed and mitigations identified
- [x] Sprint 8 vs Sprint 8b scope defined (simple vs complex cases)

---

## Task 8: Create Parser Test Fixture Strategy

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours (Actual: 3.5 hours)  
**Deadline:** 1 week before Sprint 8 Day 1  
**Owner:** Development team (Test specialist)  
**Dependencies:** Tasks 2, 3, 7 (Feature analysis, Option research, High-ROI feature research)  
**Unknowns Verified:** 7.1, 7.2, 7.3

### Objective

Define comprehensive test fixture strategy for Sprint 8 parser features (option statements, indexed assignments OR function calls, partial parse metrics). Follow Sprint 7 fixture pattern (34 fixtures created).

### Why This Matters

Sprint 7 delivered 34 test fixtures (9 preprocessor + 8 sets + 8 multidim + 9 statements) with comprehensive expected_results.yaml documentation. Sprint 8 needs similar fixture strategy for new features.

Sprint 7 retrospective: *"Fixture documentation prevents future rework... fixtures document supported AND unsupported syntax... expected failures explicitly tested."*

PROJECT_PLAN.md acceptance criteria: *"All existing tests pass, new features have comprehensive test coverage."*

### Background

Sprint 7 fixture structure (from CHANGELOG.md):
- **Directory:** `tests/fixtures/[feature_name]/`
- **Fixtures:** `01_simple.gms`, `02_complex.gms`, etc. (numbered)
- **Metadata:** `expected_results.yaml` (expected parse status, notes)
- **Documentation:** `README.md` (fixture purpose, coverage)

Example from Sprint 7:
```
tests/fixtures/statements/
├── 01_model_declaration.gms       ✅ Expected success
├── 02_solve_basic.gms              ✅ Expected success
├── 04_option_statement.gms         ❌ Expected failure (not supported)
├── 08_assignment_indexed.gms       ❌ Expected failure (by design)
├── expected_results.yaml
└── README.md
```

Sprint 8 will uncomment `04_option_statement.gms` and make it pass.

### What Needs to Be Done

**1. Option Statement Fixtures (1 hour)**

Based on Task 3 research, create option fixture plan:

```markdown
## Option Statement Fixtures

### Directory: tests/fixtures/options/

### Fixture 01: Single Integer Option
**File:** `01_single_integer_option.gms`
```gams
$onText
Fixture 01: Single Integer Option
Tests: Basic option statement with integer value
Priority: High
$offText

option limrow = 0;
```
**Expected:** Parse success
**Validates:** Basic option syntax

### Fixture 02: Multi-Option Statement
**File:** `02_multi_option.gms`
```gams
option limrow = 0, limcol = 0;
```
**Expected:** Parse success
**Validates:** Comma-separated options (mhw4dx.gms pattern)

### Fixture 03: Boolean Option
**File:** `03_boolean_option.gms`
```gams
option solprint = off;
```
**Expected:** Parse success OR defer to Sprint 8b
**Validates:** Boolean option values

### Fixture 04: Option in Model Context
**File:** `04_option_in_context.gms`
```gams
Set i / 1*10 /;
option limrow = 0;
Scalar x / 5 /;
```
**Expected:** Parse success
**Validates:** Option doesn't break surrounding statements

### Fixture 05: Invalid Option Syntax (error case)
**File:** `05_invalid_option.gms`
```gams
option limrow;  # Missing value
```
**Expected:** Parse error
**Validates:** Error handling
```

**2. High-ROI Feature Fixtures (1-1.5 hours)**

Based on Task 7 research (indexed assignments OR function calls):

**If Indexed Assignments:**
```markdown
### Directory: tests/fixtures/indexed_assignments/

### Fixture 01: Simple Indexed Assignment
**File:** `01_simple_indexed.gms`
```gams
Set i / 1*5 /;
Parameter a(i);
a(i) = 10;
```

### Fixture 02: Arithmetic Indexed
**File:** `02_arithmetic.gms`
```gams
Set i / 1*5 /;
Parameter a(i), b(i), c(i);
a(i) = b(i) + c(i);
```

### Fixture 03: Multi-Dimensional (if scope permits)
### Fixture 04: Index Mismatch Error
### Fixture 05: Undefined Index Error
```

**If Function Calls:**
```markdown
### Directory: tests/fixtures/function_calls/

### Fixture 01: sqrt Function
### Fixture 02: Trigonometric Functions
### Fixture 03: uniform Random (circle.gms pattern)
### Fixture 04: Nested Function Calls
### Fixture 05: Unknown Function Error
```

**3. Partial Parse Metric Fixtures (<1 hour)**

Create test models with known partial parse percentages:

```markdown
### Directory: tests/fixtures/partial_parse/

### Fixture 01: 100% Parse Success
**File:** `01_full_success.gms`
```gams
Set i / 1*10 /;
Scalar x / 5 /;
```
**Expected:** 100% (2/2 statements)

### Fixture 02: 50% Parse Success
**File:** `02_half_success.gms`
```gams
Set i / 1*10 /;
x(i) = y(i++1);  # i++1 not supported (Sprint 8b)
```
**Expected:** 50% (1/2 statements)

### Fixture 03: 0% Parse Failure
**File:** `03_immediate_failure.gms`
```gams
invalid syntax here
```
**Expected:** 0% (0/1 statements)
```

**4. expected_results.yaml Design (30 min)**

Design YAML structure for Sprint 8 fixtures:

```yaml
# tests/fixtures/options/expected_results.yaml
fixtures:
  01_single_integer_option:
    parse_status: SUCCESS
    description: "Basic option statement with integer value"
    sprint: 8
    priority: High
    
  02_multi_option:
    parse_status: SUCCESS
    description: "Comma-separated options (mhw4dx.gms pattern)"
    sprint: 8
    validates: "Multi-option syntax"
    
  05_invalid_option:
    parse_status: FAILED
    error_type: ParserSemanticError
    description: "Missing option value should fail"
    sprint: 8
    validates: "Error handling"

# tests/fixtures/indexed_assignments/expected_results.yaml (if selected)
fixtures:
  01_simple_indexed:
    parse_status: SUCCESS
    description: "Simple indexed assignment with constant"
    sprint: 8
    unlocks: "mathopt1.gms partial support"
  
  04_index_mismatch:
    parse_status: FAILED
    error_type: ParserSemanticError
    description: "Index mismatch should fail semantic validation"
    sprint: 8

# tests/fixtures/partial_parse/expected_results.yaml
fixtures:
  01_full_success:
    parse_status: SUCCESS
    partial_percentage: 100
    statements_parsed: 2
    total_statements: 2
    
  02_half_success:
    parse_status: PARTIAL
    partial_percentage: 50
    statements_parsed: 1
    total_statements: 2
    missing_features: ["Lead/lag indexing (i++1)"]
```

**5. README.md Templates (30 min)**

Create README template for each fixture directory:

```markdown
# Option Statement Test Fixtures

**Sprint:** 8  
**Feature:** Option statement parsing  
**Priority:** High (unlocks mhw4dx.gms)

## Overview

This directory contains test fixtures for GAMS option statement parsing. Option statements control GAMS behavior (output limits, solver options, etc.). Sprint 8 implements basic options (limrow, limcol) to unlock mhw4dx.gms.

## Fixtures

| # | Fixture | Description | Status | Notes |
|---|---------|-------------|--------|-------|
| 01 | Single Integer Option | `option limrow = 0;` | ✅ Pass | Basic syntax |
| 02 | Multi-Option | `option limrow = 0, limcol = 0;` | ✅ Pass | mhw4dx.gms pattern |
| 03 | Boolean Option | `option solprint = off;` | ✅ Pass | On/off values |
| 04 | Option in Context | Options with sets/scalars | ✅ Pass | Integration test |
| 05 | Invalid Syntax | Missing value | ❌ Fail | Error handling |

## Expected Results

See `expected_results.yaml` for detailed expectations.

## Sprint 8 Scope

- ✅ Integer options (limrow, limcol, decimals)
- ✅ Boolean options (on/off)
- ✅ Multi-option statements
- ⚠️ String options - Deferred to Sprint 8b
- ⚠️ Solver-specific options - Deferred to Sprint 8b

## Coverage

- Basic syntax: Fixtures 01, 02
- Boolean values: Fixture 03
- Integration: Fixture 04
- Error handling: Fixture 05

**Total:** 5 fixtures (4 success, 1 error)
```

### Changes

To be completed during Task 8 execution.

### Result

To be completed during Task 8 execution.

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md

# Should plan option fixtures
grep -q "Option Statement Fixtures" docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md

# Should plan high-ROI feature fixtures
grep -q "indexed_assignments\|function_calls" docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md

# Should have YAML structure
grep -q "expected_results.yaml" docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (150+ lines)
- Option statement fixture plan (5 fixtures)
- High-ROI feature fixture plan (5 fixtures for indexed assignments OR function calls)
- Partial parse metric fixture plan (3 fixtures)
- expected_results.yaml structure design
- README.md templates for fixture directories

### Acceptance Criteria

- [x] Option statement fixtures planned (5 fixtures: 4 success, 1 error)
- [x] High-ROI feature fixtures planned (5 fixtures based on Task 7)
- [x] Partial parse metric fixtures planned (3 fixtures: 100%, 50%, 0%)
- [x] expected_results.yaml structure defined
- [x] README.md templates created
- [x] Follows Sprint 7 fixture pattern (numbered files, YAML metadata, README)
- [x] Total: 13+ fixtures planned across 3 feature areas

### Completion Summary

**Completed:** 2025-11-17  
**Actual Time:** 3.5 hours  
**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/TEST_FIXTURE_STRATEGY.md` (896 lines)

**Key Findings:**

1. **13 fixtures designed** covering 100% of Sprint 8 feature scope:
   - **Option Statements (5 fixtures):** Single integer, multiple options, decimals, placement, mhw4dx pattern
   - **Indexed Assignments (5 fixtures):** 1D simple, 2D multi-dim, variable attributes (.l), indexed expressions, error handling
   - **Partial Parse Metrics (3 fixtures):** himmel16 pattern (~80%), circle pattern (~70%), complete success (100%)

2. **Extended YAML schema** with backward compatibility:
   - All Sprint 7 fields preserved (description, expected_status, priority, etc.)
   - New optional fields: option_statements, indexed_assignments, variable_attributes, parse_percentage, missing_features
   - New status value: "PARTIAL" alongside SUCCESS/FAILED

3. **Three README templates** created following Sprint 7 pattern

4. **Implementation plan** with 5 phases and 3.5 hour effort estimate

**Unknowns Verified:**
- ✅ **7.1:** Sprint 7 fixture pattern fully reusable (saves 4-6 hours)
- ✅ **7.2:** 13 fixtures sufficient for comprehensive coverage (3.5 hour total effort)
- ✅ **7.3:** Hybrid approach (real patterns in synthetic fixtures) selected

**Impact:**
- Test strategy ready for Sprint 8 implementation
- Fixture creation effort fits within Sprint 8 testing budget
- All Sprint 8 features (option statements, indexed assignments, partial metrics) have test coverage

---

## Task 9: Design Dashboard Enhancements

**Status:** ✅ COMPLETE  
**Priority:** Medium  
**Estimated Time:** 3-4 hours (Actual: 3.5 hours)  
**Deadline:** 1 week before Sprint 8 Day 1  
**Owner:** Development team (Metrics specialist)  
**Dependencies:** Task 5 (Partial parse metrics design)  
**Unknowns Verified:** 6.4

### Objective

Design enhancements to `docs/status/GAMSLIB_CONVERSION_STATUS.md` dashboard to display partial parse metrics, missing features, and color-coded status. Maintain backward compatibility with existing dashboard format.

### Why This Matters

Current dashboard shows binary pass/fail (✅ or ❌). Sprint 8 adds partial parse metrics to show progress on "almost-there" models.

PROJECT_PLAN.md acceptance criterion: *"Dashboard shows statement-level parse success (e.g., 'himmel16: 85% parsed')"*

Task 5 designed partial metrics calculation. This task designs visualization.

### Background

Current dashboard (from `docs/status/GAMSLIB_CONVERSION_STATUS.md`):

```markdown
| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| mhw4d | ✅ | - | - | ❌ | Parsed successfully |
| himmel16 | ❌ | - | - | ❌ | Parse error: UnexpectedCharacters |
```

Target dashboard (Sprint 8):

```markdown
| Model | Parse | Partial | Convert | Solve | E2E | Notes |
|-------|-------|---------|---------|-------|-----|-------|
| mhw4d | ✅ 100% | 156/156 | - | - | ❌ | Fully parsed |
| himmel16 | 🟡 85% | 45/53 | - | - | ❌ | Missing: Lead/lag indexing (i++1) |
| circle | 🟡 70% | 28/40 | - | - | ❌ | Missing: Function calls |
| hs62 | ⚠️ 40% | 12/30 | - | - | ❌ | Missing: Model sections (mx) |
```

### What Needs to Be Done

**1. Dashboard Mockup Design (1-2 hours)**

Create ASCII mockup of enhanced dashboard:

```markdown
## Enhanced Dashboard Design

### New Column: "Partial"

Displays statement-level parse success as fraction (e.g., "45/53")

- **Full success (100%):** Hide fraction (just show "✅ 100%")
- **Partial success (50-99%):** Show fraction (e.g., "🟡 85%" + "45/53")
- **Low success (25-49%):** Show fraction with warning (e.g., "⚠️ 40%" + "12/30")
- **Failure (0-24%):** Show as failed (e.g., "❌ 10%" + "3/30")

### Color Coding

- ✅ Green checkmark: 100% parsed
- 🟡 Yellow circle: 50-99% parsed (partial success)
- ⚠️ Warning: 25-49% parsed (low parse rate)
- ❌ Red X: 0-24% parsed (parse failed)

### Notes Column Enhancement

- **Before:** "Parse error: UnexpectedCharacters"
- **After:** "Missing: Lead/lag indexing (i++1), Model sections (mx)"

**Full Dashboard Mockup:**

```markdown
# GAMSLib Conversion Status Dashboard

**Generated:** 2025-11-XX XX:XX:XX
**Sprint:** Sprint 8
**Total Models:** 10
**Report:** [`gamslib_ingestion_sprint8.json`](../../reports/gamslib_ingestion_sprint8.json)

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate** | 25.0% (2.5/10) | ≥25% | ✅ |
| **Parse Rate (Partial)** | 60.0% (6/10 ≥50%) | - | 📊 |
| **Convert Rate** | 0.0% (0/2.5) | ≥50% | ⚠️ Sprint 8: Not implemented |

**Sprint 8 Target:** ✅ Parse ≥25% (2.5/10 models, including partial) - ✅ MET

---

## Model Status

| Model | Parse | Partial | Convert | Solve | E2E | Notes |
|-------|-------|---------|---------|-------|-----|-------|
| circle | 🟡 70% | 28/40 | - | - | ❌ | Missing: Function calls in assignments |
| himmel16 | 🟡 85% | 45/53 | - | - | ❌ | Missing: Lead/lag indexing (i++1) |
| hs62 | ⚠️ 40% | 12/30 | - | - | ❌ | Missing: Model sections (mx) |
| mathopt1 | 🟡 75% | 33/44 | - | - | ❌ | Missing: Indexed assignments |
| maxmin | ⚠️ 35% | 14/40 | - | - | ❌ | Missing: Nested indexing |
| mhw4d | ✅ 100% | 156/156 | 🟡 | - | ❌ | Fully parsed, conversion in progress |
| mhw4dx | ✅ 100% | 82/82 | 🟡 | - | ❌ | Unlocked by option statements (Sprint 8) |
| mingamma | ⚠️ 45% | 18/40 | - | - | ❌ | Missing: Model sections (m2) |
| rbrock | ✅ 100% | 89/89 | 🟡 | - | ❌ | Fully parsed |
| trig | 🟡 60% | 24/40 | - | - | ❌ | Missing: bound_scalar syntax |

**Legend:**
- ✅ 100%: Full parse success
- 🟡 50-99%: Partial parse (most statements parsed)
- ⚠️ 25-49%: Low parse rate (some progress)
- ❌ 0-24%: Parse failed (minimal progress)

---

## Parse Progress Summary

### Fully Parsed (100%)
- mhw4d.gms (156/156 statements)
- mhw4dx.gms (82/82 statements) - **Sprint 8 unlock**
- rbrock.gms (89/89 statements)

**Count:** 3/10 (30%) - Exceeds Sprint 8 target (25%)

### Partial Parse (50-99%)
- himmel16.gms: 85% (45/53) - 1 feature away (i++1)
- mathopt1.gms: 75% (33/44) - 1 feature away (indexed assignments)
- circle.gms: 70% (28/40) - 1 feature away (function calls)
- trig.gms: 60% (24/40) - 1 feature away (bound_scalar)

**Count:** 4/10 (40%) - Good candidates for Sprint 8b

### Low Parse (25-49%)
- mingamma.gms: 45% (18/40) - Needs model sections
- hs62.gms: 40% (12/30) - Needs model sections
- maxmin.gms: 35% (14/40) - Needs nested indexing

**Count:** 3/10 (30%) - Sprint 8b/9 targets
```

**2. Ingestion Script Updates (1 hour)**

Design changes to `scripts/ingest_gamslib.py`:

```python
# Add to JSON report structure
report_entry = {
    "model_name": model_file.stem,
    "parse_status": "SUCCESS" | "PARTIAL" | "FAILED",
    "parse_percentage": 85,  # NEW
    "parsed_statements": 45,  # NEW
    "total_statements": 53,   # NEW
    "missing_features": ["Lead/lag indexing (i++1)"],  # NEW
    "parse_error": error_message if failed else None,
    "parse_error_type": error_type if failed else None,
    # ... existing fields
}

# Add to dashboard generation
def generate_dashboard_row(entry):
    # Determine status icon
    if entry["parse_percentage"] == 100:
        status_icon = "✅"
    elif entry["parse_percentage"] >= 50:
        status_icon = "🟡"
    elif entry["parse_percentage"] >= 25:
        status_icon = "⚠️"
    else:
        status_icon = "❌"
    
    # Format partial column
    if entry["parse_percentage"] < 100:
        partial = f"{entry['parsed_statements']}/{entry['total_statements']}"
    else:
        partial = f"{entry['total_statements']}/{entry['total_statements']}"
    
    # Format notes
    if entry["missing_features"]:
        notes = f"Missing: {', '.join(entry['missing_features'])}"
    elif entry["parse_status"] == "SUCCESS":
        notes = "Fully parsed"
    else:
        notes = f"Parse error: {entry['parse_error_type']}"
    
    return f"| {entry['model_name']} | {status_icon} {entry['parse_percentage']}% | {partial} | - | - | ❌ | {notes} |"
```

**3. Dashboard Template Design (1 hour)**

Create Jinja2 or Python template for dashboard generation:

```python
DASHBOARD_TEMPLATE = """
# GAMSLib Conversion Status Dashboard

**Generated:** {timestamp}
**Sprint:** Sprint {sprint_number}
**Total Models:** {total_models}
**Report:** [`{report_filename}`](../../reports/{report_filename})

---

## Overall KPIs

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Parse Rate (Full)** | {full_parse_rate}% ({full_parse_count}/{total_models}) | ≥25% | {parse_status} |
| **Parse Rate (Partial ≥50%)** | {partial_parse_rate}% ({partial_count}/{total_models}) | - | 📊 |
| **Average Parse %** | {avg_parse_percent}% | - | 📊 |

---

## Model Status

| Model | Parse | Partial | Convert | Solve | E2E | Notes |
|-------|-------|---------|---------|-------|-----|-------|
{model_rows}

**Legend:**
- ✅ 100%: Full parse success
- 🟡 50-99%: Partial parse
- ⚠️ 25-49%: Low parse rate
- ❌ 0-24%: Parse failed

---

## Parse Progress Summary

### Fully Parsed (100%)
{fully_parsed_list}

**Count:** {fully_parsed_count}/{total_models} ({fully_parsed_rate}%)

### Partial Parse (50-99%)
{partial_parsed_list}

**Count:** {partial_count}/{total_models} ({partial_rate}%)
"""

def generate_dashboard(report: Dict) -> str:
    # Calculate KPIs
    fully_parsed = [m for m in report["models"] if m["parse_percentage"] == 100]
    partial_parsed = [m for m in report["models"] if 50 <= m["parse_percentage"] < 100]
    
    # Render template
    return DASHBOARD_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        sprint_number=8,
        total_models=len(report["models"]),
        full_parse_count=len(fully_parsed),
        full_parse_rate=len(fully_parsed) / len(report["models"]) * 100,
        partial_count=len(partial_parsed),
        # ... other fields
    )
```

**4. Backward Compatibility Check (<1 hour)**

Verify existing dashboard consumers still work:
- CI workflow (`.github/workflows/gamslib-regression.yml`) reads parse rate
- Makefile (`make ingest-gamslib`) generates dashboard
- Existing scripts don't break with new columns

**Changes needed:**
- None expected (adding columns doesn't break readers)
- CI regression check still reads `parse_rate_percent` from JSON (unchanged)

### Changes

To be completed during Task 9 execution.

### Result

To be completed during Task 9 execution.

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md

# Should have mockup
grep -q "🟡 85%" docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md

# Should have ingestion updates
grep -q "parse_percentage" docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md

# Should check backward compatibility
grep -q "Backward Compatibility" docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (120+ lines)
- Dashboard mockup with partial metrics
- Color coding scheme (✅ 🟡 ⚠️ ❌)
- Ingestion script update design
- Dashboard template design
- Backward compatibility analysis

### Acceptance Criteria

- [x] Dashboard mockup shows partial parse percentages
- [x] Color coding defined (100%, 75-99%, 25-74%, <25%)
- [x] "Progress" column displays parse percentages + line counts
- [x] "Missing Features" column shows blockers
- [x] Ingestion script updates designed
- [x] Dashboard template created
- [x] Backward compatibility verified (CI still works)
- [x] Follows existing dashboard format

### Completion Summary

**Completed:** 2025-11-17  
**Actual Time:** 3.5 hours  
**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/DASHBOARD_ENHANCEMENTS.md` (821 lines)

**Key Findings:**

1. **Enhanced Dashboard Mockup:**
   - New columns: "Status" (color-coded), "Progress" (% + line counts), "Missing Features"
   - Example: `himmel16 | 🟡 PARTIAL | 92% (22/24) | i++1 indexing`
   - Replaces binary ✅/❌ with granular 4-level status

2. **Color Coding Scheme:**
   - ✅ GREEN (100%): Full parse success
   - 🟡 YELLOW (75-99% or 100% semantic): Mostly parsed, needs 1-2 features
   - ⚠️ ORANGE (25-74%): Partially parsed, major blockers
   - ❌ RED (<25%): Early failure, fundamental issues

3. **Ingestion Script Updates:**
   - Line counting: `count_logical_lines(source)` - handles comments, blanks
   - Progress calculation: `(lines_parsed / lines_total) × 100`
   - Feature extraction: Pattern matching on error messages (8+ patterns)
   - Status determination: Threshold-based (100% → ✅, 75-99% → 🟡, etc.)
   - Estimated: ~140 lines of new code

4. **Dashboard Template:**
   - Modified header: "Parse" → "Status", add "Progress", add "Missing Features"
   - Row format: `| {model} | {✅/🟡/⚠️/❌ + label} | {%} ({parsed}/{total}) | {features} | ...`
   - Legend updated: 4-level status descriptions
   - Example: `mhw4d | ✅ PASS | 100% (18/18) | - | - | - | ❌`

5. **Backward Compatibility:**
   - ✅ Sprint 7 data displays correctly (100% or 0%, "-" for missing features)
   - ✅ No breaking changes to CI or existing workflows
   - ✅ New fields optional in JSON schema (old parsers ignore)
   - ✅ Schema versioning: v1.0 (Sprint 7) → v2.0 (Sprint 8)

**Unknown Verified:**
- ✅ **6.4:** Dashboard can show partial metrics with minor refactoring (4 hours)
  - No breaking changes, fully backward compatible
  - Pure additive changes (new columns, enhanced symbols)

**Implementation Effort:**
- Ingestion script: 2 hours
- Dashboard template: 1 hour
- Testing: 1 hour
- **Total: 4 hours** (confirmed from Task 9 design)

**Impact:**
- Visibility into partial progress: himmel16 is 92% done, not "failed"
- Feature-based roadmap: Missing features drive Sprint 8b/9 planning
- User motivation: Progress visible even when not at 100%
- Example improvement: "60% of models parse ≥75%" vs "20% binary parse rate"

---

## Task 10: Plan Sprint 8 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 6-8 hours  
**Deadline:** Before Sprint 8 Day 1  
**Owner:** Development team (Sprint lead)  
**Dependencies:** All tasks (1-9)
**Unknowns Verified:** 8.1, 8.2, 8.3

### Objective

Create detailed day-by-day execution plan for Sprint 8, incorporating findings from all prep tasks. Define specific deliverables, effort estimates, checkpoints, and quality gates.

**Deliverable:** `docs/planning/EPIC_2/SPRINT_8/PLAN.md`

### Why This Matters

Sprint 7 PLAN.md (2000+ lines) provided detailed daily breakdown, checkpoint criteria, and quality gates. Sprint 8 needs similar rigor for 25-35 hour execution.

All prep tasks (1-9) feed into this plan:
- Task 1: Known Unknowns → Risk mitigation strategies
- Task 2: Feature matrix → Feature priority and parse rate targets
- Task 3: Option research → Day 1-2 implementation plan
- Task 4: Parser error line numbers → Day 3-4 implementation plan
- Task 5: Partial metrics → Day 5-6 implementation plan
- Task 6: Error enhancements → Day 7 implementation plan
- Task 7: High-ROI feature → Day 8-9 implementation plan
- Task 8: Test fixtures → Daily test coverage targets
- Task 9: Dashboard → Day 10 integration

### Background

Sprint 8 structure (from PROJECT_PLAN.md):
- **Duration:** Weeks 5-6 (~10 working days)
- **Effort:** 25-35 hours
- **Strategy:** 60% Parser (15-20h) + 40% UX (10-15h)
- **Checkpoints:** TBD (likely 3-4 checkpoints like Sprint 7)

Sprint 7 had 4 checkpoints:
- Checkpoint 0: Prep complete (Day 0)
- Checkpoint 1: GAMSLib retest after parser changes (Day 5)
- Checkpoint 2: Test performance optimized (Day 7)
- Checkpoint 3: CI automation + fixtures complete (Day 9)
- Checkpoint 4: Sprint complete & released (Day 10)

### What Needs to Be Done

**1. Day-by-Day Breakdown (3-4 hours)**

Create 10-day execution plan:

```markdown
## Sprint 8 Day-by-Day Plan

### Day 0: Sprint Kickoff & Setup (2-3 hours)

**Objective:** Finalize prep, set up Sprint 8 branch, verify quality checks pass

**Tasks:**
- Review all prep task deliverables (Tasks 1-9)
- Validate Known Unknowns are addressed
- Create Sprint 8 branch: `sprint8-parser-maturity-ux`
- Run baseline quality checks: `make typecheck lint format test`
- Confirm GAMSLib baseline: 20% parse rate (mhw4d, rbrock)

**Deliverables:**
- Sprint 8 branch created
- Baseline quality checks: ✅ 1287 tests passing
- Prep task review complete

**Checkpoint 0 Criteria:**
- [ ] All prep tasks complete (Tasks 1-9)
- [ ] Known Unknowns documented
- [ ] Feature matrix complete (Task 2)
- [ ] Sprint 8 branch created
- [ ] Baseline quality checks passing

---

### Days 1-2: Option Statement Implementation (6-8 hours)

**Objective:** Implement option statement parsing to unlock mhw4dx.gms

**Tasks (Day 1, 3-4 hours):**
- Add `option` keyword to grammar (Task 3 design)
- Create AST node for option statements
- Implement basic semantic handling (store, don't process)
- Create test fixtures 01-03 (single option, multi-option, boolean)

**Tasks (Day 2, 3-4 hours):**
- Implement integration tests (fixture 04)
- Add error handling (fixture 05)
- Test against mhw4dx.gms (should now parse)
- Run GAMSLib ingestion: verify 30% parse rate (mhw4d, rbrock, mhw4dx)

**Deliverables:**
- Option statement grammar changes
- 5 test fixtures passing
- mhw4dx.gms parsing successfully
- Parse rate: 30% (3/10 models)

**Quality Gates:**
- All existing tests pass (1287 tests)
- New option tests pass (5 fixtures)
- mhw4dx.gms parses (verified with `make ingest-gamslib`)

---

### Days 3-4: Parser Error Line Numbers (4-6 hours)

**Objective:** Extend SourceLocation tracking to all parser errors (100% coverage)

**Tasks (Day 3, 2-3 hours):**
- Enhance exception classes (ParserSemanticError, UnsupportedSyntaxError)
- Update 5-10 raise points in parser.py (Task 4 inventory)
- Add location extraction to validation functions

**Tasks (Day 4, 2-3 hours):**
- Create test suite for line number coverage
- Verify all error types have line numbers (100% coverage test)
- Update CLI error formatting
- Test against failed GAMSLib models

**Deliverables:**
- All custom parser errors include line numbers
- Test suite: 100% coverage verified
- CLI shows "Parse error at file.gms:15:8: message"

**Quality Gates:**
- All existing tests pass
- 100% error type coverage (test_all_parser_errors_have_line_numbers passes)
- Failed GAMSLib models show line numbers

---

### Days 5-6: Partial Parse Metrics & Dashboard (7-9 hours)

**Objective:** Implement statement-level parse tracking and dashboard visualization

**Tasks (Day 5, 3-4 hours):**
- Implement statement counting (Task 5 design)
- Add partial metrics to ingestion pipeline
- Create 3 partial parse test fixtures (100%, 50%, 0%)
- Test metric calculation on GAMSLib models

**Tasks (Day 6, 4-5 hours):**
- Update dashboard template (Task 9 design)
- Generate enhanced dashboard with partial metrics
- Add color coding (✅ 🟡 ⚠️ ❌)
- Verify backward compatibility (CI still works)

**Deliverables:**
- Partial parse metrics in JSON report
- Enhanced dashboard shows "himmel16: 85% (45/53)"
- Color-coded status indicators
- 3 partial parse test fixtures

**Quality Gates:**
- All existing tests pass
- Partial metrics accurate on test fixtures
- Dashboard backward compatible
- CI regression check still works

**Checkpoint 1 Criteria:**
- [ ] Option statements implemented (mhw4dx.gms parses)
- [ ] Parse rate ≥30% (3/10 models)
- [ ] Parser error line numbers: 100% coverage
- [ ] Partial parse metrics implemented
- [ ] Dashboard enhanced with partial metrics
- [ ] All quality checks passing

---

### Day 7: Error Message Enhancements (3-5 hours)

**Objective:** Add actionable hints and help links to parser errors

**Tasks:**
- Implement EnhancedError class (Task 6 design)
- Create enhancement rules (10+ error patterns)
- Add "did you mean?" for typos (difflib integration)
- Add documentation links for unsupported features
- Test enhanced errors on GAMSLib failures

**Deliverables:**
- EnhancedError framework
- 10+ enhancement rules
- Improved error messages for common failures

**Quality Gates:**
- All existing tests pass
- Enhanced errors tested (5+ test cases)
- GAMSLib failures show helpful hints

---

### Days 8-9: High-ROI Feature Implementation (6-8 hours)

**Objective:** Implement second Sprint 8 feature (indexed assignments OR function calls)

**Based on Task 2 recommendation, implement ONE of:**

**Option A: Indexed Assignments (if selected)**
- Day 8: Grammar changes, AST nodes, simple cases (3-4 hours)
- Day 9: Semantic validation, test fixtures, mathopt1.gms test (3-4 hours)

**Option B: Function Calls (if selected)**
- Day 8: Function whitelist, validation, simple cases (3-4 hours)
- Day 9: Nested calls, test fixtures, circle.gms test (3-4 hours)

**Deliverables:**
- Grammar changes for selected feature
- 5 test fixtures passing
- Target model progress (mathopt1.gms or circle.gms)

**Quality Gates:**
- All existing tests pass
- New feature tests pass (5 fixtures)
- Parse rate progress documented

**Checkpoint 2 Criteria:**
- [ ] Error message enhancements complete
- [ ] High-ROI feature implemented (indexed assignments OR function calls)
- [ ] Test fixtures created (5+ per feature)
- [ ] Parse rate ≥25% (acceptance criterion met)
- [ ] All quality checks passing

---

### Day 10: Sprint Review & Release (6-8 hours)

**Objective:** Complete Sprint 8, release v0.8.0

**Tasks:**
- Run full QA: `make test`, `make typecheck lint format`
- Run GAMSLib ingestion: verify ≥25% parse rate
- Verify acceptance criteria (all ✅)
- Update CHANGELOG.md
- Update PROJECT_PLAN.md (mark Sprint 8 complete)
- Create Sprint 8 retrospective
- Tag v0.8.0 release

**Deliverables:**
- v0.8.0 released
- Sprint 8 retrospective complete
- All documentation updated

**Checkpoint 3 (Final) Criteria:**
- [ ] Parse rate ≥25% (2.5/10 models) ✅
- [ ] Parser error line numbers: 100% ✅
- [ ] Feature matrix complete ✅
- [ ] Partial metrics in dashboard ✅
- [ ] All quality checks passing ✅
- [ ] v0.8.0 tagged and released ✅
```

**2. Checkpoint Definitions (1-2 hours)**

Define 3-4 checkpoints with clear criteria:

```markdown
## Checkpoint Definitions

### Checkpoint 0: Prep Complete (Day 0)
**Objective:** All preparation verified before Sprint 8 begins
- All prep tasks complete (Tasks 1-9)
- Known Unknowns documented
- Feature matrix analyzed
- Sprint 8 branch created
- Baseline quality checks passing

### Checkpoint 1: Core Features Complete (Day 6)
**Objective:** Option statements, parser error line numbers, partial metrics implemented
- Parse rate ≥30% (option statements unlock mhw4dx)
- Parser error line numbers: 100% coverage
- Partial parse metrics working
- Dashboard enhanced

### Checkpoint 2: All Features Complete (Day 9)
**Objective:** High-ROI feature, error enhancements complete
- Parse rate ≥25% (conservative target met)
- Error message enhancements complete
- High-ROI feature implemented
- All test fixtures passing

### Checkpoint 3: Sprint Complete & Released (Day 10)
**Objective:** v0.8.0 released, all goals met
- All acceptance criteria met
- Quality checks passing
- v0.8.0 tagged
- Retrospective complete
```

**3. Effort Allocation Validation (1 hour)**

Verify 25-35 hour total aligns with daily breakdown:

```markdown
## Effort Allocation

| Days | Activity | Hours | Percentage |
|------|----------|-------|------------|
| 0 | Sprint kickoff | 2-3 | 8% |
| 1-2 | Option statements | 6-8 | 24% |
| 3-4 | Parser error line numbers | 4-6 | 18% |
| 5-6 | Partial metrics & dashboard | 7-9 | 28% |
| 7 | Error enhancements | 3-5 | 12% |
| 8-9 | High-ROI feature | 6-8 | 24% |
| 10 | Sprint review & release | 6-8 | 24% |

**Total:** 34-47 hours (slightly over 25-35 estimate)

**Adjustment:** If time tight, defer error enhancements (Day 7) to Sprint 8b.
**Adjusted Total:** 31-42 hours (within target)
```

**4. Quality Gates & Testing Strategy (1 hour)**

Define continuous quality checks:

```markdown
## Quality Gates

### Daily Quality Checks (all days)
- `make typecheck` - Must pass
- `make lint` - Must pass
- `make format` - Apply formatting
- `make test` - All tests must pass (no regressions)

### Feature-Specific Gates
- **Option statements:** mhw4dx.gms must parse
- **Parser error line numbers:** 100% coverage test must pass
- **Partial metrics:** Accuracy test on 3 fixtures must pass
- **High-ROI feature:** 5 test fixtures must pass

### Checkpoint Gates
- Checkpoint 1: Parse rate ≥30%, partial metrics working
- Checkpoint 2: Parse rate ≥25%, all features complete
- Checkpoint 3: All acceptance criteria met, v0.8.0 tagged
```

**5. Risk Mitigation (1 hour)**

Plan for Known Unknowns and risks:

```markdown
## Risk Mitigation

### Risk 1: Option statements more complex than estimated
- **Mitigation:** Task 3 research validates 6-8h estimate
- **Contingency:** Defer boolean/string options to Sprint 8b, focus on integer options only

### Risk 2: High-ROI feature underperforms (unlocks 0 models)
- **Mitigation:** Task 2 feature matrix confirms unlock rate
- **Contingency:** 25% target still met with option statements alone (30% achieved)

### Risk 3: Partial metrics counting is inaccurate
- **Mitigation:** Task 5 design defines "statement" clearly
- **Contingency:** Start with approximate count, refine in Sprint 8b

### Risk 4: Sprint 8 effort exceeds 35 hours
- **Mitigation:** Defer error enhancements (Day 7) to Sprint 8b
- **Impact:** Still meets core goals (parse rate, line numbers, partial metrics)
```

**6. Cross-Reference All Prep Tasks (<1 hour)**

Link each day to relevant prep tasks:

```markdown
## Prep Task → Sprint Day Mapping

| Prep Task | Sprint Days | Deliverables Used |
|-----------|-------------|-------------------|
| Task 1: Known Unknowns | Day 0 | Risk mitigation throughout sprint |
| Task 2: Feature Matrix | Days 1-2, 8-9 | Feature priority, unlock rate validation |
| Task 3: Option Research | Days 1-2 | Grammar design, test fixtures |
| Task 4: Parser Error Line Numbers | Days 3-4 | Design patterns, raise point inventory |
| Task 5: Partial Metrics | Days 5-6 | Counting mechanism, dashboard mockup |
| Task 6: Error Enhancements | Day 7 | Enhancement rules, error patterns |
| Task 7: High-ROI Feature | Days 8-9 | Grammar design, test fixtures |
| Task 8: Test Fixtures | Days 1-9 | Fixture plans for all features |
| Task 9: Dashboard Enhancements | Day 6 | Dashboard template, ingestion updates |
| Task 10: Sprint Plan | All days | This document |
```

### Changes

To be completed during Task 10 execution.

### Result

To be completed during Task 10 execution.

### Verification

```bash
# Document should exist
test -f docs/planning/EPIC_2/SPRINT_8/PLAN.md

# Should have 10-day breakdown
grep -q "Day 0" docs/planning/EPIC_2/SPRINT_8/PLAN.md
grep -q "Day 10" docs/planning/EPIC_2/SPRINT_8/PLAN.md

# Should have checkpoint definitions
grep -q "Checkpoint 0" docs/planning/EPIC_2/SPRINT_8/PLAN.md
grep -q "Checkpoint 3" docs/planning/EPIC_2/SPRINT_8/PLAN.md

# Should cross-reference prep tasks
grep -q "Task 2: Feature Matrix" docs/planning/EPIC_2/SPRINT_8/PLAN.md
```

### Deliverables

- `docs/planning/EPIC_2/SPRINT_8/PLAN.md` (1500+ lines, similar to Sprint 7 PLAN.md)
- Day-by-day breakdown (Days 0-10)
- Checkpoint definitions (3-4 checkpoints)
- Effort allocation breakdown (25-35 hours)
- Quality gates and testing strategy
- Risk mitigation plans
- Cross-reference to all prep tasks

### Acceptance Criteria

- [ ] 10-day execution plan created (Days 0-10)
- [ ] Each day has: objective, tasks, deliverables, quality gates
- [ ] Checkpoints defined with clear criteria (3-4 checkpoints)
- [ ] Effort allocation validated (25-35 hours total)
- [ ] Quality gates specified (daily checks + feature-specific)
- [ ] Risk mitigation plans created
- [ ] All prep tasks (1-9) cross-referenced
- [ ] Sprint 8 acceptance criteria mapped to specific days
- [ ] Format matches Sprint 7 PLAN.md (consistent structure)

---

## Summary

### Total Prep Effort

**Estimated Time:** 42-56 hours (~5-7 working days)

### Critical Path

**Tasks 1 → 2 → 3, 7 → 9 → 10** (must complete sequentially)

**Timeline:**
- Week 1: Tasks 1-5 (research & analysis)
- Week 2: Tasks 6-9 (design & planning)
- Week 3: Task 10 (detailed schedule)

### Success Criteria

Sprint 8 prep is complete when:
- [ ] All 10 prep tasks complete
- [ ] Known Unknowns documented (22-30 unknowns)
- [ ] Per-model feature matrix created (all 10 models analyzed)
- [ ] Feature recommendation made (indexed assignments OR function calls)
- [ ] Option statement research complete (grammar designed)
- [ ] Parser error line number design complete
- [ ] Partial parse metrics design complete
- [ ] Error message enhancement patterns cataloged
- [ ] High-ROI feature research complete
- [ ] Test fixture strategy defined (13+ fixtures planned)
- [ ] Dashboard enhancements designed
- [ ] Detailed Sprint 8 PLAN.md created (1500+ lines)
- [ ] All designs validated with 25-35 hour effort estimate

### Sprint 8 Ready Checklist

Before Sprint 8 Day 1:
- [ ] PREP_PLAN.md reviewed and approved
- [ ] All 10 prep tasks executed
- [ ] PLAN.md created and reviewed
- [ ] Team aligned on Sprint 8 goals and approach
- [ ] Baseline quality checks passing (1287 tests)
- [ ] GAMSLib baseline confirmed (20% parse rate)

---

## Appendix: Document Cross-References

### Sprint Planning Documents
- `docs/planning/EPIC_2/PROJECT_PLAN.md` (lines 84-148) - Sprint 8 goals and components
- `docs/planning/EPIC_2/SPRINT_7/RETROSPECTIVE.md` - Sprint 7 lessons learned
- `docs/planning/EPIC_2/SPRINT_7/PREP_PLAN.md` - Format reference
- `docs/planning/EPIC_2/SPRINT_6/PREP_PLAN.md` - Format reference

### GAMSLib Analysis
- `docs/status/GAMSLIB_CONVERSION_STATUS.md` - Current dashboard (20% baseline)
- `reports/gamslib_ingestion_sprint6.json` - Baseline metrics

### Research Documents
- `docs/research/` - General research notes (if applicable)

### Sprint 7 Deliverables (Reference for Sprint 8)
- Line number tracking implementation (Day 8)
- Test fixture strategy (34 fixtures created)
- CI automation (regression detection)
- Retrospective recommendations

### Epic Goals
- `docs/planning/EPIC_2/GOALS.md` - Overall Epic 2 objectives

---

**Document Status:** 🔵 NOT STARTED (To be completed during prep phase)  
**Target Completion:** 1 week before Sprint 8 Day 1  
**Owner:** Development team  
**Reviewers:** Sprint lead, parser specialists, UX specialists
