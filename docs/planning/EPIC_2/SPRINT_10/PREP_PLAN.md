# Sprint 10 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 10 parse rate push to 100%  
**Timeline:** Complete before Sprint 10 Day 1  
**Goal:** Address Sprint 9 learnings and prepare for complete GAMSLIB Tier 1 parse coverage

**Key Insight from Sprint 9:** Features implemented ≠ models unlocked. Sprint 9 implemented 3 features (i++1 indexing, model sections, equation attributes) but achieved 0% parse rate improvement due to incomplete dependency analysis. Sprint 10 must perform complete blocker chain analysis BEFORE any implementation.

---

## Executive Summary

Sprint 9 Retrospective identified the root cause of parse rate plateau: implementing features without understanding complete dependency chains. Despite implementing i++1 indexing, himmel16.gms still fails due to a secondary blocker (level bound conflicts). Despite implementing equation attributes, mingamma.gms still fails due to a different blocker (abort$ in if-blocks).

Sprint 10 aims for 100% parse rate (10/10 Tier 1 GAMSLIB models) through:
1. **Phase 1 (Critical):** Complete dependency chain analysis for all 4 blocked models BEFORE implementation
2. **Phase 2 (Quick Win):** Comma-separated declarations (common GAMS pattern)
3. **Phase 3 (Targeted):** Implement only features required by complete blocker chains
4. **Phase 4 (Validation):** Mid-sprint checkpoint at Day 5 to validate impact
5. **Phase 5 (Quality):** Synthetic test suite to validate features in isolation

This prep plan focuses on research and analysis tasks that must be completed before Sprint 10 Day 1 to prevent repeating Sprint 9's issues.

**Current Status:**
- **Parse Rate:** 60% (6/10 models: mhw4d, rbrock, mathopt1, trig, hs62, mhw4dx)
- **Blocked Models:** circle (57% parsed), himmel16 (79% parsed), maxmin (40% parsed), mingamma (54% parsed)
- **Sprint 9 Features Implemented:** i++1 indexing, model sections, equation attributes (but models still blocked)

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint Goal Addressed |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 10 Known Unknowns List | Critical | 2-3 hours | None | Proactive unknown identification |
| 2 | Analyze circle.gms Complete Blocker Chain | Critical | 2 hours | Task 1 | Phase 1: Dependency analysis |
| 3 | Analyze himmel16.gms Complete Blocker Chain | Critical | 2 hours | Task 1 | Phase 1: Dependency analysis |
| 4 | Analyze maxmin.gms Complete Blocker Chain | Critical | 2-3 hours | Task 1 | Phase 1: Dependency analysis |
| 5 | Analyze mingamma.gms Complete Blocker Chain | Critical | 1-2 hours | Task 1 | Phase 1: Dependency analysis |
| 6 | Research Comma-Separated Declaration Patterns | High | 2 hours | None | Phase 2: Quick win preparation |
| 7 | Survey Existing GAMS Function Call Syntax | High | 2-3 hours | Task 2 | Phase 3: Function calls research |
| 8 | Research Nested/Subset Indexing Semantics | High | 3-4 hours | Task 4 | Phase 3: Complex indexing research |
| 9 | Design Synthetic Test Framework | High | 2-3 hours | Tasks 2-5 | Phase 5: Feature validation |
| 10 | Validate Sprint 9 Features Work in Isolation | Medium | 2 hours | Task 9 | Verify i++1, attributes, model sections |
| 11 | Set Up Mid-Sprint Checkpoint Infrastructure | Medium | 1-2 hours | None | Phase 4: Checkpoint automation |
| 12 | Plan Sprint 10 Detailed Schedule | Critical | 3-4 hours | All tasks | Sprint 10 execution planning |

**Total Estimated Time:** ~24-30 hours (~3-4 working days)

**Critical Path:** Tasks 1 → 2,3,4,5 → 12 (must complete before Sprint 10)

---

## Task 1: Create Sprint 10 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Sprint planning  
**Dependencies:** None

### Objective

Create proactive list of assumptions and unknowns for Sprint 10 to prevent incomplete dependency analysis and late feature discoveries.

### Why This Matters

**Sprint 9 Lesson:** Assumed features would unlock models without validating complete blocker chains. Result: 0% parse rate improvement despite 3 features implemented.

**Sprint 10 Risk:** Without knowing what we don't know about each blocker, we may implement features that don't unlock models.

**Examples of unknowns to identify:**
- Does fixing the primary blocker actually unlock the model, or are there secondary/tertiary blockers?
- Are there interactions between blockers that compound complexity?
- Do we understand the exact GAMS semantics for each feature?
- Can we test features in isolation before implementing in complex models?

### Background

Sprint 9 Known Unknowns List (`docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md`) achieved excellent results:
- 41 unknowns identified across 4 categories
- All critical unknowns resolved proactively
- Zero late surprises during sprint

However, the list focused on **implementation unknowns** (how to implement features), not **dependency unknowns** (what blockers actually prevent models from parsing).

Sprint 10 must identify:
- **Dependency Unknowns:** Are there hidden secondary/tertiary blockers?
- **Semantic Unknowns:** Do we understand exact GAMS behavior for each feature?
- **Validation Unknowns:** How do we test features work before integration?
- **Implementation Unknowns:** How complex is each feature to implement?

### What Needs to Be Done

#### Step 1: Review Sprint 9 Retrospective Findings (30 minutes)

Read `docs/planning/EPIC_2/SPRINT_9/RETROSPECTIVE.md` sections:
- Root Causes of Parse Rate Plateau (lines 245-290)
- What Went Wrong analysis (lines 190-244)
- Recommendations for Sprint 10 (lines 291-334)

Extract key unknowns about why features didn't unlock models.

#### Step 2: Identify Dependency Unknowns Per Model (1 hour)

For each blocked model (circle, himmel16, maxmin, mingamma):

**Template:**
```markdown
### Model: [model_name].gms

**Primary Blocker:** [known blocker]
**Unknowns:**
- Unknown D1: Are there secondary blockers after fixing primary?
- Unknown D2: Are there tertiary blockers after fixing secondary?
- Unknown D3: Do blockers interact (fixing one reveals/changes others)?
- Unknown D4: What percentage of file parses today? Will it increase after fix?
```

Review existing partial analyses:
- `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` (demonstrates proper blocker analysis)
- `docs/planning/EPIC_2/SPRINT_9/mingamma_blocker_analysis.md` (shows partial analysis)

#### Step 3: Identify Semantic/Technical Unknowns Per Feature (45 minutes)

For each feature to implement:

**Function Calls in Parameter Assignments:**
- Unknown T1: What functions are valid in parameter assignments? (smin, smax, uniform, normal, etc.)
- Unknown T2: Can function calls be nested?
- Unknown T3: How do we evaluate functions at parse time vs runtime?
- Unknown T4: Are there functions that require special handling?

**Level Bound Conflicts:**
- Unknown T5: What causes "conflicting level bound" errors?
- Unknown T6: Is this a parser issue or semantic validation issue?
- Unknown T7: Can multiple `.l` assignments coexist if values match?
- Unknown T8: Is this specific to indexed variables?

**Nested/Subset Indexing:**
- Unknown T9: What is exact syntax for subset domains?
- Unknown T10: Can subsets be multidimensional?
- Unknown T11: How do we resolve subset references in domains?
- Unknown T12: Are there performance implications?

**abort$ in If-Blocks:**
- Unknown T13: Is abort$(condition) currently parsed at all?
- Unknown T14: Is this grammar issue or AST validation issue?
- Unknown T15: What are valid abort$ locations?
- Unknown T16: How do we handle abort$ semantics?

**Comma-Separated Declarations:**
- Unknown T17: Do all declaration types support commas equally?
- Unknown T18: Can attributes be specified per variable in comma list?
- Unknown T19: What is grammar production for comma-separated lists?
- Unknown T20: Are there edge cases (trailing commas, etc.)?

#### Step 4: Identify Validation/Testing Unknowns (30 minutes)

- Unknown V1: How do we create minimal synthetic test for each feature?
- Unknown V2: What makes a good isolated feature test?
- Unknown V3: How do we verify features work before integration?
- Unknown V4: What regression tests are needed?
- Unknown V5: How do we measure parse rate improvement?

#### Step 5: Organize and Prioritize (15 minutes)

Create `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` with:

**Structure:**
```markdown
# Sprint 10 Known Unknowns

## Category 1: Dependency Chain Unknowns (Critical)
[Unknowns D1-D12]

## Category 2: Feature Semantic Unknowns (High)
[Unknowns T1-T20]

## Category 3: Validation/Testing Unknowns (High)
[Unknowns V1-V5]

## Category 4: Implementation Approach Unknowns (Medium)
[Implementation-specific unknowns]

## Resolution Plan
[Which unknowns resolve during prep, which during sprint]
```

Each unknown must include:
- **ID and Description**
- **Current Assumption**
- **Why It Matters** (impact if assumption wrong)
- **Verification Method** (how to resolve)
- **Priority** (Critical/High/Medium/Low)
- **Estimated Research Time**

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md`

**Total Unknowns:** 28 across 7 categories
- Category 1: Comprehensive Dependency Analysis (8 unknowns)
- Category 2: Comma-Separated Declarations (3 unknowns)
- Category 3: Function Calls in Parameters (5 unknowns)
- Category 4: Level Bound Conflict Resolution (3 unknowns)
- Category 5: Nested/Subset Indexing (5 unknowns - highest risk)
- Category 6: abort$ in If-Blocks (2 unknowns)
- Category 7: Synthetic Test Suite (2 unknowns)

**Priority Distribution:**
- Critical: 8 (29%) - Blocker chain completeness and model unlocking
- High: 11 (39%) - Feature implementation approach
- Medium: 7 (25%) - Implementation details
- Low: 2 (7%) - Process improvements

**Task-to-Unknown Mapping Table:** Created appendix showing which prep tasks verify which unknowns

**Cross-References:** Linked to PROJECT_PLAN.md, Sprint 9 RETROSPECTIVE.md, blocker analyses

### Result

Successfully created comprehensive Known Unknowns document addressing Sprint 9 lesson: focus on **dependency unknowns** (complete blocker chains) and **validation unknowns** (testing features work), not just implementation unknowns.

**Key Unknowns Identified:**
- **10.1.1-10.1.4:** Complete blocker chains for all 4 blocked models (critical for avoiding Sprint 9 repeat)
- **10.5.1:** Nested indexing go/no-go decision (critical - determines 100% vs 90% target)
- **10.7.2:** Sprint 9 features validation (must verify before building on them)

**Estimated Research Time:** 32-40 hours distributed across prep tasks 2-11

**Document includes:**
- Executive summary with Sprint 9 lessons
- How to use (before sprint, during sprint, priority definitions)
- Summary statistics
- 28 detailed unknowns with research questions and verification methods
- Template for adding new unknowns during sprint
- Task-to-Unknown mapping table
- Next steps for prep phase and sprint execution

### Verification

```bash
# Verify Known Unknowns document exists and is comprehensive
test -f docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
grep -c "Unknown" docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
# Should show 30+ unknowns

# Verify all categories present
grep "Category 1: Dependency Chain" docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
grep "Category 2: Feature Semantic" docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
grep "Category 3: Validation" docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md

# Verify priorities assigned
grep -E "(Critical|High|Medium|Low)" docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md | wc -l
# Should match unknown count
```

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` with 28 unknowns
- [x] All unknowns categorized (7 categories: Dependency Analysis, Comma-Separated, Function Calls, Level Bounds, Nested Indexing, abort$, Synthetic Tests)
- [x] All unknowns have priority, verification method, research time estimate
- [x] Resolution plan identifies which unknowns resolve during prep vs sprint (Task-to-Unknown mapping table)
- [x] Template for sprint updates defined

### Acceptance Criteria

- [x] Document contains 28 unknowns across 7 categories (target was ≥22 unknowns across ≥5 categories)
- [x] All Critical unknowns (8) have detailed verification plans with research questions and how to verify
- [x] All dependency unknowns (per model) identified (10.1.1-10.1.4 for circle, himmel16, maxmin, mingamma)
- [x] All feature semantic unknowns identified (function calls, level bounds, nested indexing, abort$, comma-separated)
- [x] All validation/testing unknowns identified (10.7.1-10.7.2 for synthetic tests and Sprint 9 feature validation)
- [x] Total research time estimated (32-40 hours aligned with prep task hours 24-30)
- [x] Cross-references to Sprint 9 retrospective findings (root cause analysis, lessons learned)
- [x] Cross-references to blocker analysis documents (tasks 2-5)

---

## Task 2: Analyze circle.gms Complete Blocker Chain

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Actual Time:** 1.5 hours  
**Completed:** 2025-11-23  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 10.1.1

### Objective

Perform line-by-line analysis of circle.gms to identify ALL blockers (primary, secondary, tertiary) that prevent parsing, not just the first error encountered.

### Why This Matters

**Current Status:** circle.gms is 57% parsed (16/28 lines)

**Sprint 9 Lesson:** himmel16.gms primary blocker (i++1 indexing) was fixed, but secondary blocker (level bounds) prevents model from parsing. Without complete analysis, implementing primary fix doesn't unlock model.

**Sprint 10 Goal:** Identify ALL blockers for circle.gms BEFORE implementation so we can prioritize correctly and set realistic expectations.

### Background

**Known Primary Blocker (from exploration):**
- Function calls in parameter assignments: `uniform(1,10)`, `smin(i, x(i))`
- Parser expects numeric constants, receives function call AST nodes

**Unknown Secondary Blockers:**
- Are there other syntax issues after fixing function calls?
- Are there semantic validation issues?
- What percentage will parse after primary fix?

**Related Documents:**
- Sprint 9 blocker analysis examples in `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md`
- Exploration report (from Task tool) showing 57% parse rate

### What Needs to Be Done

#### Step 1: Parse circle.gms with Current Parser (15 minutes)

```bash
# Run parser on circle.gms and capture ALL errors
python -c "
from src.ir.parser import parse_model_file
try:
    result = parse_model_file('tests/fixtures/gamslib/circle.gms')
    print('SUCCESS: Model parsed')
    print(f'Variables: {len(result.variables)}')
    print(f'Parameters: {len(result.params)}')
    print(f'Equations: {len(result.equations)}')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 | tee /tmp/circle_parse_attempt.log

# Examine error cascade
cat /tmp/circle_parse_attempt.log
```

Document:
- Line number of first error
- Error message
- Stack trace showing error origin

#### Step 2: Manual Line-by-Line Inspection (1 hour)

Read `tests/fixtures/gamslib/circle.gms` line by line:

For each line, document:
1. **Line number**
2. **Content** (GAMS syntax)
3. **Parse status** (likely to pass/fail with current parser)
4. **Blocker type** (if fails: grammar/semantic/other)
5. **Feature required** (to make line parse)
6. **Blocker priority** (Primary/Secondary/Tertiary based on line order)

**Template:**
```markdown
| Line | Content | Status | Blocker Type | Feature Required | Priority |
|------|---------|--------|--------------|------------------|----------|
| 40 | xmin = smin(i, x(i)); | FAIL | Grammar | Function call in assignment | Primary |
| 41 | ... | PASS | - | - | - |
```

#### Step 3: Test Blocker Order (30 minutes)

Manually fix each blocker in order and re-parse to discover next blocker:

1. Comment out line 40 (function call) and re-parse
2. If new error appears, document as Secondary blocker
3. Fix/comment and re-parse again
4. Continue until model parses or all blockers identified

Document complete chain:
```markdown
## Blocker Chain for circle.gms

**Primary Blocker:** Function calls in parameter assignment (line 40)
- Error: "Expected numeric constant, got function call"
- Lines affected: 40, [any others]
- Estimated fix effort: 6-8 hours

**Secondary Blocker:** [If discovered]
- Error: [error message]
- Lines affected: [line numbers]
- Estimated fix effort: [hours]

**Tertiary Blocker:** [If discovered]
- ...
```

#### Step 4: Create Blocker Analysis Document (15 minutes)

Create `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md`:

**Required sections:**
- Model Overview (current parse %, total lines)
- Complete Blocker Chain (Primary → Secondary → Tertiary)
- Line-by-Line Analysis Table
- Effort Estimates per Blocker
- Model Unlock Prediction (will fixing Primary unlock model? or need Secondary too?)
- Synthetic Test Requirements (minimal GAMS file to test each blocker fix)

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` (603 lines, 22KB)

**Analysis Completed:**
- Line-by-line analysis of all 56 lines in circle.gms
- Complete blocker chain identification: 3 blockers (Primary, Secondary, Tertiary)
- Parse attempt logged to `/tmp/circle_parse_attempt.log`
- Comprehensive documentation with effort estimates and recommendations

**Updated:** `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md`
- Unknown 10.1.1 marked as ✅ VERIFIED
- Added complete findings with blocker chain details
- Documented Sprint 10 implementation decision

### Result

**Complete Blocker Chain Identified:**

1. **PRIMARY BLOCKER (Lines 40-43):** Aggregation function calls in parameter assignments
   - `smin(i, x(i))`, `smax(i, x(i))`
   - Currently blocks at line 40
   - Affects 4 lines of parameter initialization

2. **SECONDARY BLOCKER (Line 48):** Mathematical function calls in variable assignments
   - `sqrt(sqr(a.l - xmin) + sqr(b.l - ymin))`
   - Would block after primary fix
   - Affects 1 line of variable level assignment

3. **TERTIARY BLOCKER (Lines 54-56):** Conditional abort statement
   - Multi-line if with compile-time variables
   - Would block after secondary fix
   - Affects 3 lines of execution control

**Key Findings:**

- **Progressive Parse Rates:** Current 70% → Primary fix 84% → Secondary fix 95% → Tertiary fix 100%
- **Critical Discovery:** Function calls already work in equation context (line 35: `sqr(x(i) - a)`)
- **Implementation Simplification:** Function call infrastructure exists; need to extend from equation to assignment context
- **Effort Revision:** 6-10 hours (down from 10-14) due to existing function call logic

**Sprint 10 Decision:**

✅ **IMPLEMENT:** Primary + Secondary blockers together (combined "function call support in assignments")
- Expected outcome: 95% parse success (53/56 lines)
- High ROI: Unlocks model structure and initialization logic

❌ **DEFER:** Tertiary blocker (conditional abort) to Sprint 11+
- Low ROI: Only 5% of remaining file
- Edge case pattern, can be addressed later

**Model Unlock Prediction:** circle.gms will NOT be 100% parseable after primary fix alone (contrary to original assumption). Requires both primary and secondary blockers to reach 95%, which is acceptable progress toward Sprint 10 goals.

### Verification

```bash
# Verify blocker analysis document exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md

# Verify contains blocker chain
grep "Primary Blocker" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md
grep "Secondary Blocker" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md

# Verify line-by-line table exists
grep "| Line |" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md

# Verify effort estimates present
grep -E "[0-9]+-[0-9]+ hours" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md
```

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` with complete blocker chain
- [x] Line-by-line analysis table for all 56 lines (file has 56 lines, not 28)
- [x] Primary, Secondary, Tertiary blockers identified (all 3 found)
- [x] Effort estimate per blocker
- [x] Model unlock prediction (does Primary fix unlock model? NO - requires Primary + Secondary)
- [x] Synthetic test requirements documented
- [x] Parse attempt logs saved for reference (/tmp/circle_parse_attempt.log)
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknown 10.1.1

### Acceptance Criteria

- [x] Complete blocker chain documented (all 3 blockers, not just first)
- [x] Each blocker has error message, affected lines, estimated effort
- [x] Model unlock prediction clearly stated (95% after Primary + Secondary, not 100%)
- [x] Line-by-line table shows all 56 lines with parse status
- [x] Synthetic test requirements specified for each blocker
- [x] Cross-references Known Unknowns Category 1 (Dependency Chain)
- [x] Unknown 10.1.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Analyze himmel16.gms Complete Blocker Chain

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Actual Time:** 1.5 hours  
**Completed:** 2025-11-23  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 10.1.2, 10.4.1, 10.4.2

### Objective

Perform line-by-line analysis of himmel16.gms to identify ALL remaining blockers after Sprint 9's i++1 indexing implementation.

### Why This Matters

**Current Status:** himmel16.gms is 79% parsed (26/33 lines)

**Sprint 9 Issue:** i++1 indexing was implemented (primary blocker), but model still fails to parse. Exploration identified secondary blocker: "Conflicting level bound for variable 'x'".

**Sprint 10 Critical Question:** Is level bound conflict the ONLY remaining blocker, or are there additional tertiary blockers?

### Background

**Known Primary Blocker (FIXED in Sprint 9):**
- ✅ Lead/lag indexing (`i++1`) - Implemented in Sprint 9
- Parser now supports `x(i++1)` syntax

**Known Secondary Blocker:**
- Level bound conflicts: Multiple `.l` assignments to same variable
- Error suggests semantic validation issue, not parse issue

**Unknown Tertiary Blockers:**
- Are there additional syntax issues?
- What exactly triggers "conflicting level bound" error?
- Will model parse after fixing level bound issue?

**Related Documents:**
- `docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md` - i++1 implementation details
- Exploration report showing 79% parse rate and level bound error

### What Needs to Be Done

#### Step 1: Parse himmel16.gms with Current Parser (15 minutes)

```bash
# Parse and capture errors
python -c "
from src.ir.parser import parse_model_file
try:
    result = parse_model_file('tests/fixtures/gamslib/himmel16.gms')
    print('SUCCESS: Model parsed')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 | tee /tmp/himmel16_parse_attempt.log

# Check if error is level bounds or something else
grep -i "level" /tmp/himmel16_parse_attempt.log
grep -i "conflict" /tmp/himmel16_parse_attempt.log
```

#### Step 2: Analyze Level Bound Conflict (45 minutes)

Search himmel16.gms for all `.l` assignments:

```bash
grep -n "\.l\s*=" tests/fixtures/gamslib/himmel16.gms
```

Document:
- Which variables have multiple `.l` assignments?
- What values are assigned?
- Are assignments to same variable or indexed variants?
- Is this valid GAMS (multiple assignments override) or invalid?

Research GAMS semantics:
- Check GAMS documentation for `.l` attribute behavior
- Can variable have multiple `.l` assignments?
- Does order matter (last wins)?
- Is this specific to indexed variables?

**Questions to Answer:**
1. What exactly is "conflicting"? (different values? same variable?)
2. Is this a parser error or semantic validation error?
3. Should parser allow this and let GAMS compiler decide?
4. Or should we track and validate `.l` assignments?

#### Step 3: Manual Line-by-Line Inspection (45 minutes)

Read all 33 lines of himmel16.gms:

Create table:
```markdown
| Line | Content | Status | Blocker | Feature Required | Priority |
|------|---------|--------|---------|------------------|----------|
| 46 | x(i)*y(i++1) - ... | PASS | None (i++1 fixed) | - | - |
| [n] | x.l(i) = ... | FAIL? | Level bounds | Conflict resolution | Secondary |
```

#### Step 4: Test If Only Blocker (15 minutes)

If level bound conflict is clear:
1. Manually remove or modify conflicting `.l` assignments
2. Re-parse to see if model parses
3. If parses → only blocker identified ✅
4. If fails → tertiary blocker exists, document it

#### Step 5: Create Blocker Analysis Document (15 minutes)

Create `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md`:

**Required sections:**
- Model Overview (79% parsed, 26/33 lines)
- Sprint 9 Status (i++1 primary blocker FIXED)
- Remaining Blocker Chain
- Level Bound Conflict Deep Dive
- GAMS Semantics Research Findings
- Model Unlock Prediction
- Synthetic Test Requirements

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` (714 lines, 23KB)

**Analysis Completed:**
- Line-by-line analysis of all 70 lines in himmel16.gms
- Root cause analysis of level bound conflict error
- Parser bug identification in `_expand_variable_indices` function
- GAMS semantics research for variable bounds
- Complete blocker chain documentation

**Updated:** `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md`
- Unknown 10.1.2 marked as ✅ VERIFIED (complete blocker chain)
- Unknown 10.4.1 marked as ✅ VERIFIED (parser bug in index expansion)
- Unknown 10.4.2 marked as ✅ VERIFIED (GAMS semantics confirmed)

### Result

**Complete Blocker Chain Identified:**

1. **PRIMARY BLOCKER (Lines ~47-50):** Lead/lag indexing (i++1, i--1)
   - Status: ✅ FIXED in Sprint 9
   - Evidence: Parser now reaches line 63 (vs ~line 47 in Sprint 8)
   - Parse improvement: 67% → 90%

2. **SECONDARY BLOCKER (Line 63):** Variable bound index expansion bug
   - Currently blocks at line 63: `x.l("5") = 0`
   - Error: "Conflicting level bound for variable 'x' at indices ('1',)"
   - Parse rate: 90% (63/70 lines)

3. **TERTIARY BLOCKER:** NONE - Confirmed no additional blockers

**Root Cause Discovered: Parser Bug**

**Location:** `src/ir/parser.py`, function `_expand_variable_indices` (line 2125)

**Bug:** Parser incorrectly expands literal string indices to ALL domain members instead of using only the specified literal.

**Example:**
```gams
x.fx("1") = 0  # Should affect ONLY index "1"
```
- Expected: Sets fx_map for index ("1",) only
- Actual (buggy): Sets fx_map for ALL indices ("1", "2", "3", "4", "5", "6")

**Why Error Message is Confusing:**
- Error says "indices ('1',)" but occurs at line 63 which sets `x.l("5")`
- This is actually CORRECT - the conflict IS at index "1"
- Line 57: `x.fx("1") = 0` → Bug sets l_map for ALL indices to 0
- Lines 60-62: Set l_map["1"] = 0.5 (same value, no conflict yet)
- Line 63: `x.l("5") = 0` → Bug tries to set l_map["1"] = 0 → **CONFLICT** (0.5 vs 0)

**GAMS Semantics Verified:**
- Multiple `.l` assignments on different indices: VALID in GAMS
- Mixing `.fx` and `.l` on different indices: VALID in GAMS
- himmel16.gms uses valid GAMS syntax - parser bug is blocking it

**Sprint 10 Decision:**

✅ **FIX:** Variable bound index expansion bug
- Effort: 3-4 hours (localized bug fix)
- Complexity: LOW-MEDIUM (single function)
- Risk: LOW (isolated change, clear test case)
- Confidence: 95%+
- Expected result: himmel16.gms from 90% → 100%

**Model Unlock Prediction:** himmel16.gms will parse completely (100%, 70/70 lines) after fixing the index expansion bug. This is a high-confidence prediction based on thorough line-by-line analysis.

### Verification

```bash
# Verify blocker analysis exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md

# Verify covers level bound issue
grep -i "level.*bound" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md

# Verify mentions Sprint 9 i++1 fix
grep "i++1" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md

# Verify complete blocker chain documented
grep -E "(Secondary|Tertiary)" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md
```

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` with complete remaining blocker chain
- [x] Level bound conflict analysis (what variables, what values, why conflict)
- [x] GAMS semantics research findings (is multiple `.l` valid?)
- [x] Confirmation if level bounds is ONLY remaining blocker (no tertiary)
- [x] Line-by-line table for all 33 lines
- [x] Synthetic test requirements
- [x] Model unlock prediction
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.2, 10.4.1, 10.4.2

### Acceptance Criteria

- [x] Complete remaining blocker chain documented (after i++1 fix)
- [x] Level bound conflict thoroughly analyzed
- [x] GAMS semantics verified (is this valid/invalid in GAMS?)
- [x] Tertiary blocker search completed (confirm level bounds is last blocker)
- [x] Effort estimate for level bound fix provided
- [x] Synthetic test requirements specified
- [x] Cross-references Sprint 9 i++1 implementation status
- [x] Unknowns 10.1.2, 10.4.1, 10.4.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Analyze maxmin.gms Complete Blocker Chain

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Actual Time:** 2.5 hours  
**Completed:** 2025-11-23  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 10.1.3, 10.5.1, 10.5.2, 10.5.3

### Objective

Perform line-by-line analysis of maxmin.gms to identify ALL blockers, with focus on understanding nested/subset indexing requirements.

### Why This Matters

**Current Status:** maxmin.gms is 40% parsed (19/47 lines) - LOWEST parse rate

**Known Primary Blocker:** Nested/subset indexing in equation domains
- `defdist(low(n,nn)).. dist(low) =e= sqrt(...)`
- Where `low` is a 2D subset, not a simple index

**Complexity:** This is marked as HIGH RISK (10-12 hours effort) in Sprint 10 plan. Must understand exact requirements BEFORE implementation.

**Fallback Plan:** If too complex, defer to Sprint 11 and target 90% (9/10 models). But need complete analysis to make informed decision.

### Background

**Known Primary Blocker:**
- Nested/subset indexing: `defdist(low(n,nn))..` where `low(n,nn)` is 2D subset
- Parser error: "Unexpected character '('" - can't handle subset domain notation

**Unknown Complexity Questions:**
- Is this the ONLY blocker?
- How complex is nested indexing to implement?
- Are there similar patterns elsewhere in file?
- Can we simplify the requirement?

**Related Documents:**
- Exploration report showing 40% parse rate
- Sprint 10 PROJECT_PLAN.md marking this as High Risk feature

### What Needs to Be Done

#### Step 1: Parse maxmin.gms and Capture Error Cascade (15 minutes)

```bash
python -c "
from src.ir.parser import parse_model_file
try:
    result = parse_model_file('tests/fixtures/gamslib/maxmin.gms')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 | tee /tmp/maxmin_parse_attempt.log
```

#### Step 2: Study Nested Indexing Pattern (1 hour)

Read maxmin.gms sections with nested indexing:

**Questions to Answer:**
1. What is `low(n,nn)` syntax exactly?
   - Is `low` a set or subset?
   - Are `n, nn` indices or set elements?
   - How is this declared earlier in file?

2. How many times does this pattern appear?
   ```bash
   grep -n "low(n,nn)" tests/fixtures/gamslib/maxmin.gms
   grep -n "(\w\+(\w\+,\w\+))" tests/fixtures/gamslib/maxmin.gms
   ```

3. What is GAMS semantics for subset domains?
   - Check GAMS documentation
   - Is this common pattern in GAMS?
   - How does GAMS resolve subset references?

4. Can we simplify requirement?
   - Could we support simpler syntax first?
   - Is full nested indexing necessary?

Document findings:
```markdown
## Nested Indexing Analysis

**Pattern:** `defdist(low(n,nn))..`

**GAMS Semantics:**
- `low` is [set/subset/alias] declared as [...]
- `n, nn` are [indices/elements/...]
- This notation means [explanation]

**Frequency:** Appears [N] times in maxmin.gms at lines [...]

**Complexity Assessment:**
- Grammar changes required: [...]
- AST changes required: [...]
- Semantic resolution required: [...]
- Estimated effort: [hours] (validate 10-12 hour estimate)
```

#### Step 3: Line-by-Line Analysis (1 hour)

Create complete table for all 47 lines:

```markdown
| Line | Content | Status | Blocker | Feature | Priority |
|------|---------|--------|---------|---------|----------|
| 51 | defdist(low(n,nn)).. | FAIL | Grammar | Nested indexing | Primary |
| ... | | | | | |
```

Special attention to:
- How many lines blocked by nested indexing?
- Are there other blockers beyond nested indexing?
- What percentage would parse after fixing primary blocker?

#### Step 4: Test Blocker Order (30 minutes)

1. Comment out lines with nested indexing
2. Re-parse to discover secondary blockers
3. Document complete chain

#### Step 5: Assess Complexity and Create Recommendation (30 minutes)

**Complexity Assessment:**
- Can we implement in 10-12 hours? (confirm/revise estimate)
- Should we attempt in Sprint 10 or defer to Sprint 11?
- Is there a simpler intermediate step?

**Risk/Benefit Analysis:**
- **Benefit:** Unlock maxmin.gms (40% → 100%)
- **Risk:** High complexity, may consume sprint without success
- **Fallback:** Target 90% (9/10 models) without maxmin.gms

Create `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` with recommendation.

### Changes

**Created:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` (1,500+ lines)

**CRITICAL DISCOVERY: Function call infrastructure ALREADY EXISTS!**

**Survey Findings:**
- **19 unique functions** cataloged across 6 categories
- **90+ total occurrences** in GAMSLIB (8/10 models use function calls)
- **Maximum nesting depth:** 5 levels (maxmin.gms:83)
- **Nesting distribution:** 89% are depth ≤2 (deep nesting rare but exists)

**Function Categories:**
1. **Mathematical (10):** sqr, sqrt, power, log, abs, round, mod, ceil, max, min
2. **Aggregation (4):** smin, smax, sum, max
3. **Trigonometric (2):** sin, cos
4. **Statistical (1):** uniform
5. **Special (2):** gamma, loggamma
6. **Set (2):** ord, card

**Infrastructure Analysis:**
- ✅ Grammar rule exists: `func_call.3: FUNCNAME "(" arg_list? ")"` (gams_grammar.lark:315)
- ✅ Call AST node exists: `class Call(Expr)` (src/ir/ast.py:170)
- ✅ FUNCNAME token has 18/21 functions (86% coverage - missing: round, mod, ceil)
- ✅ Expression integration complete: atom → func_call → funccall
- ✅ Works in equation context already

**Evaluation Strategy Decision:**
- **Chosen:** Option C (Parse-only - store all as expressions)
- Add `expressions: dict[tuple[str, ...], Expr]` field to ParameterDef
- Store function calls as Call AST nodes (no evaluation needed)
- Consistent with equation handling (also stores expressions)

**Effort Estimate Revision:**
- **Original:** 6-8 hours (assumed infrastructure needed)
- **Revised:** 2.5-3 hours (infrastructure exists, only semantic handler work)
- **Reduction:** 62-71% effort reduction

**Breakdown:**
- Grammar changes: 5 min (add round, mod, ceil to FUNCNAME)
- IR changes: 30 min (add expressions field)
- Semantic handler: 1-1.5h (verify/fix parameter context)
- Testing: 1h
- **Total: 2.5-3 hours**

**Updated KNOWN_UNKNOWNS.md:** Verified all 4 unknowns (10.3.1-10.3.4)

### Result

**Objective achieved:** Complete understanding of function call requirements with major discovery about existing infrastructure.

**Key Findings:**

1. **Infrastructure Status:** COMPLETE ✅
   - Grammar, AST, and expression integration already support function calls
   - Only missing piece: semantic handler for parameter assignment context
   - 3 functions need to be added to FUNCNAME token (trivial 5-minute fix)

2. **Function Catalog:** 19 unique functions across 6 categories
   - circle.gms uses: uniform, sqrt, sqr, smin, smax (5 functions)
   - All 5 circle.gms functions already in FUNCNAME token ✅
   - Common patterns: Euclidean distance (sqrt of sum of sqr), aggregation (smin/smax)

3. **Nesting Complexity:** Maximum depth 5, but 89% are ≤2
   - Grammar supports arbitrary nesting through recursion ✅
   - No special implementation needed for nesting

4. **Evaluation Strategy:** Parse-only (Option C)
   - Store as expressions, don't evaluate at parse time
   - Defers evaluation to GAMS runtime
   - Consistent with equation handling
   - Simplest implementation (2.5-3h vs 6-8h)

5. **Argument Types:** All expressions supported
   - Constants, variables, indexed variables, arithmetic expressions, nested calls
   - Grammar: `arg_list: expr ("," expr)*` handles everything
   - No special-case argument handling needed

**Unknown Verification Results:**

✅ **Unknown 10.3.1 (Evaluation Strategy):** CORRECT - Parse-only is the right approach
- Add expressions field to ParameterDef
- Store Call AST nodes without evaluation
- Major effort reduction: 2.5-3h instead of 6-8h

✅ **Unknown 10.3.2 (Nesting Depth):** PARTIALLY WRONG - Depth can reach 5 levels (not just 1-2)
- Grammar already supports arbitrary nesting ✅
- 89% are depth ≤2, but 11% go deeper
- No implementation work needed (grammar handles it)

✅ **Unknown 10.3.3 (Function Categories):** CORRECT - Categories identified
- 6 categories: Mathematical, Aggregation, Trigonometric, Statistical, Special, Set
- All use same syntax (no category-specific parsing)
- Uniform implementation across categories

✅ **Unknown 10.3.4 (Grammar Infrastructure):** ASSUMPTION COMPLETELY WRONG - Infrastructure exists!
- Grammar changes: Only add 3 functions to FUNCNAME token (5 minutes)
- AST changes: None needed (Call node exists)
- Expression integration: Already complete
- Massive effort reduction from expected work

**Impact on Sprint 10:**
- **circle.gms implementation:** 2.5-3 hours (not 6-8 hours)
- **High confidence:** Infrastructure exists, low-risk implementation
- **Clear path:** Add expressions field, fix semantic handler, done
- **ROI:** Unlocks circle.gms from 57% → 95% (secondary blocker analysis in Task 2)

### Verification

```bash
# Verify analysis exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md

# Verify nested indexing analysis
grep -i "nested.*indexing" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md

# Verify complexity assessment
grep -i "complexity" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md

# Verify recommendation
grep -i "recommend" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md
```

### Changes

**Files Created:**
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` (2062 lines, comprehensive blocker analysis)

**Files Modified:**
- `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` (added 4 verification results: 10.1.3, 10.5.1, 10.5.2, 10.5.3)

**Analysis Completed:**
- Line-by-line analysis of all 108 lines in maxmin.gms
- Complete blocker chain identified (5 categories, 23 blocker lines total)
- Nested indexing complexity assessment (HIGH: 9/10 rating)
- GAMS subset domain semantics research
- Progressive parse rate analysis
- Implementation recommendation: DEFER to Sprint 11+

### Result

**Complete Blocker Chain Identified (5 Categories, 23 Lines):**

1. **PRIMARY BLOCKER (3 lines):** Subset/nested indexing in equation domains
   - Lines 51, 53, 55: `defdist(low(n,nn))..`, `mindist1(low)..`, `mindist1a(low(n,nn))..`
   - Error: "No terminal matches '(' in the current parser context, at line 51 col 12"
   - Grammar limitation: `id_list: ID ("," ID)*` only supports simple identifiers
   - Parse improvement: 18% → 51% (after fix)

2. **SECONDARY BLOCKER (2 lines):** Aggregation functions in equation domains
   - Lines 57, 59: `mindist2.. mindist =e= smin(low, dist(low));`
   - Same blocker as circle.gms (will be fixed by Sprint 10 function call implementation)
   - Parse improvement: 51% → 57% (after fix)

3. **TERTIARY BLOCKER (5 lines):** Multi-model declaration syntax
   - Lines 61-65: Multi-line model block with 4 models in one statement
   - Current grammar only supports single model per statement
   - Parse improvement: 57% → 65% (after fix)

4. **QUATERNARY BLOCKER (4 lines):** Loop with tuple domain
   - Lines 70-73: `loop((n,d), ...);` - nested parentheses for tuple iteration
   - Parse improvement: 65% → 69% (after fix)

5. **RELATED BLOCKERS (9 lines):** Lower priority features
   - Line 37: Set assignment with ord() functions
   - Line 78: Variable bounds with subset indexing  
   - Line 83: Function calls in parameter assignments (max, ceil, sqrt, card)
   - Line 87: Conditional option statement
   - Line 106: DNLP solver support
   - Parse improvement: 69% → 79% (after all fixes)

**Progressive Parse Rates:**
- **Current:** 18% (19/108 lines) - Fails at line 51 (nested indexing)
- **After Primary:** ~51% (55/108 lines) - Would fail at line 57 (aggregation functions)
- **After Primary + Secondary:** ~57% (61/108 lines) - Would fail at line 61 (multi-model)
- **After Primary + Secondary + Tertiary:** ~65% (70/108 lines) - Would fail at line 70 (loop tuple)
- **After ALL parse blockers:** 79% (85/108 lines) - Remaining are semantic issues

**Total Effort Required:**
- Primary blocker alone: 10-14 hours (HIGH complexity)
- All 5 blocker categories: 23-40 hours
- Far exceeds Sprint 10 capacity

**Nested Indexing Complexity Assessment (HIGH: 9/10):**

**Grammar Changes (3-4 hours):**
- Modify `equation_def` rule to support nested syntax
- Create new `domain_spec` rule for: simple IDs, subset references, nested subset with indices
- Most complex grammar change to date

**AST Changes (2-3 hours):**
- New structure for subset references with optional indices
- Distinguish: `equation(i,j)` vs `equation(subset)` vs `equation(subset(i,j))`

**Semantic Resolution (4-6 hours):**
- Resolve subset definitions at equation creation time
- Expand subset domains to actual index combinations
- Handle subset assignments: `low(n,nn) = ord(n) > ord(nn);`
- Track subset membership for domain expansion

**Testing (1-2 hours):**
- 7 test suites with 20+ test cases specified in analysis

**GAMS Subset Domain Semantics:**
- **Declaration:** `Set low(n,n);` - 2D subset with parent domain
- **Assignment:** `low(n,nn) = ord(n) > ord(nn);` - populates subset (lower triangle)
- **Usage:** `defdist(low(n,nn))..` generates equations ONLY for (n,nn) pairs where low(n,nn) is true
- **Shorthand:** `mindist1(low)..` is equivalent to `mindist1(low(n,nn))..` with inferred indices
- **Semantics:** Filters equation domain to subset members (conditional equation generation)

**Partial Implementation Analysis:**
- **NOT FEASIBLE:** maxmin.gms uses both 1-level (`low`) and 2-level (`low(n,nn)`) patterns
- **Interdependent:** 1-level is shorthand requiring 2-level semantics
- **All-or-nothing:** Must implement full nested indexing or defer entirely
- **No value in partial:** 1-level alone doesn't unlock any models

**Sprint 10 Decision: DEFER maxmin.gms to Sprint 11+**

**Recommendation Rationale:**
1. **HIGH RISK:** Nested indexing alone is 10-14 hours, could consume entire sprint without success
2. **LOW ROI:** Only unlocks 1 model (maxmin.gms), only to 51% not 100%
3. **MULTIPLE DEPENDENCIES:** Full maxmin.gms requires 5 blocker categories (23-40 hours total)
4. **FALLBACK VIABLE:** Target 90% (9/10 models) with circle.gms + himmel16.gms (9-14 hours)
5. **BETTER SEQUENCING:** Implement simpler, well-understood features first
6. **COMPLEXITY:** Highest complexity feature to date (9/10 rating)

**Alternative Strategy: Target 90% Success Rate**
- **Implement:** circle.gms function calls (6-10 hours)
- **Implement:** himmel16.gms parser bug fix (3-4 hours)
- **Defer:** maxmin.gms to Sprint 11
- **Expected Outcome:** 9/10 models parsing = 90% success rate
- **Total Effort:** 9-14 hours (fits comfortably in sprint)
- **Risk Level:** LOW-MEDIUM (well-understood blockers, clear fix approaches)

**Unknowns Verified:**
- ✅ Unknown 10.1.3: Complete blocker chain (PRIMARY assumption was WRONG - 5 categories, not just nested indexing)
- ✅ Unknown 10.5.1: Complexity level (10-14 hours confirmed, HIGH risk)
- ✅ Unknown 10.5.2: GAMS semantics (subset domains filter equation generation)
- ✅ Unknown 10.5.3: Partial implementation (NOT feasible, all-or-nothing)

**Model Unlock Prediction:**
- After nested indexing only: maxmin.gms from 18% → 51%
- After all 5 blocker categories: maxmin.gms from 18% → 79%
- Full 100% requires semantic fixes beyond parser scope
- **Confidence:** 95%+ in blocker analysis accuracy

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` with complete blocker chain
- [x] Nested indexing deep dive (GAMS semantics, pattern frequency, complexity)
- [x] Line-by-line table for all 108 lines
- [x] Complexity assessment (validated 10-14 hour estimate)
- [x] Implementation recommendation (DEFER to Sprint 11)
- [x] Fallback plan documented (90% target without maxmin.gms)
- [x] Synthetic test requirements
- [x] Model unlock prediction
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.3, 10.5.1, 10.5.2, 10.5.3

### Acceptance Criteria

- [x] Complete blocker chain documented
- [x] Nested indexing pattern thoroughly analyzed
- [x] GAMS semantics research completed
- [x] Complexity estimate validated (10-14 hours confirmed)
- [x] Clear recommendation: DEFER to Sprint 11
- [x] Fallback plan specified (target 90% with circle.gms + himmel16.gms)
- [x] Synthetic test requirements for nested indexing feature
- [x] Cross-references Known Unknowns Category 1 and 5
- [x] Unknowns 10.1.3, 10.5.1, 10.5.2, 10.5.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Analyze mingamma.gms Complete Blocker Chain

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 1-2 hours  
**Actual Time:** 1.5 hours  
**Completed:** 2025-11-23  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 10.1.4, 10.6.1, 10.6.2

### Objective

Perform line-by-line analysis of mingamma.gms to verify abort$ in if-blocks is the ONLY remaining blocker (not equation attributes as initially assumed).

### Why This Matters

**Current Status:** mingamma.gms is 54% parsed (20/37 lines)

**Sprint 9 Issue:** Equation attributes were implemented assuming this would unlock mingamma.gms. But model still fails with different error: abort$ statement in if-block body.

**Sprint 10 Critical Question:** Is abort$ in if-blocks the ONLY blocker, or did Sprint 9's incorrect assumption mask additional issues?

### Background

**Incorrect Sprint 9 Assumption:**
- Assumed mingamma.gms needed equation attributes (`.l`, `.m`)
- Implemented equation attributes feature
- Model still blocked by abort$ in if-blocks

**Actual Primary Blocker:**
- `abort$(condition)` statements inside if-block bodies
- Parser/grammar doesn't support this construct
- Error: "Unexpected character ')'" at line 60

**Existing Partial Analysis:**
- `docs/planning/EPIC_2/SPRINT_9/mingamma_blocker_analysis.md` exists
- Shows parse attempt and identifies abort$ issue
- But doesn't confirm if ONLY blocker

### What Needs to Be Done

#### Step 1: Review Existing Analysis (15 minutes)

Read `docs/planning/EPIC_2/SPRINT_9/mingamma_blocker_analysis.md`:
- What blockers are identified?
- What percentage analyzed?
- Is blocker chain complete or partial?

#### Step 2: Parse mingamma.gms with Current Parser (15 minutes)

```bash
python -c "
from src.ir.parser import parse_model_file
try:
    result = parse_model_file('tests/fixtures/gamslib/mingamma.gms')
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
" 2>&1 | tee /tmp/mingamma_parse_attempt.log

# Check error location and type
grep -n "line 60" /tmp/mingamma_parse_attempt.log
grep "abort" /tmp/mingamma_parse_attempt.log
```

#### Step 3: Analyze abort$ Syntax (30 minutes)

Find all abort$ statements in mingamma.gms:

```bash
grep -n "abort" tests/fixtures/gamslib/mingamma.gms
```

Document:
- How many abort$ statements?
- Are they all in if-blocks or elsewhere too?
- What is exact syntax: `abort$[...]` or `abort$(...)`?
- Are there other conditional abort patterns?

Research GAMS abort$ syntax:
- Valid locations for abort$ (global, if-blocks, loops, etc.)
- Syntax variations (abort, abort$, $abort, etc.)
- Semantics (when does abort execute?)

#### Step 4: Line-by-Line Analysis (30 minutes)

Create table for all 37 lines:

```markdown
| Line | Content | Status | Blocker | Feature | Priority |
|------|---------|--------|---------|---------|----------|
| 60 | abort$(condition) | FAIL | Grammar | abort$ in if-block | Primary |
```

#### Step 5: Test If Only Blocker (15 minutes)

1. Comment out abort$ statements
2. Re-parse
3. If parses → only blocker ✅
4. If fails → document secondary blocker

#### Step 6: Verify Equation Attributes Not Needed (15 minutes)

Check if mingamma.gms actually uses equation attributes:

```bash
grep -E "\.l\s*=|\.m\s*=" tests/fixtures/gamslib/mingamma.gms
```

If no equation attributes found:
- Document that Sprint 9 assumption was incorrect
- Equation attributes implemented but not required for this model
- Lesson learned for Sprint 10: validate assumptions with grep

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify analysis exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md

# Verify abort$ analysis
grep "abort" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md

# Verify equation attributes checked
grep -i "equation.*attribute" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md

# Verify Sprint 9 lesson documented
grep "Sprint 9" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md
```

### Changes

**Files Created:**
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` (1604 lines, comprehensive blocker analysis)

**Files Modified:**
- `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` (added 3 verification results: 10.1.4, 10.6.1, 10.6.2)

**Analysis Completed:**
- Line-by-line analysis of all 63 lines in mingamma.gms
- abort$ syntax analysis (Sprint 9 status verified)
- Equation attributes verification (NOT used in mingamma.gms - Sprint 9 assumption WRONG)
- Complete blocker chain identified (NEW blocker discovered)
- Sprint 9 lessons learned documentation

### Result

**Critical Discovery: Sprint 9 Assumption Was COMPLETELY WRONG**

**Sprint 9 Claimed:**
- Primary blocker: Equation attributes (`.l`, `.m` on equations)
- Secondary blocker: abort$ in if-blocks

**Actual Truth:**
1. **Equation attributes:** NOT USED in mingamma.gms
   - Verified with: `grep -E "y1def\.|y2def\." tests/fixtures/gamslib/mingamma.gms`
   - Result: NO equation attribute access found
   - Only VARIABLE attributes used: x1.l, x2.l, y1.l, y2.l, x1.lo, x2.lo
   - Sprint 9 confused variable attributes with equation attributes

2. **abort$ in if-blocks:** ✅ WAS actual blocker, correctly fixed in Sprint 9
   - Lines 59, 62: `abort$[condition] "message";`
   - Syntax uses SQUARE BRACKETS, not parentheses
   - Status: ✅ FIXED in Sprint 9 (now parses correctly)

**NEW Blocker Discovered:**

**PRIMARY BLOCKER (Lines 30-38): Comma-Separated Scalar Declarations with Inline Values**

```gams
Scalar
   x1opt   / 1.46163214496836   /
   x1delta
   x2delta
   y1opt   / 0.8856031944108887 /
   y1delta
   y2delta
   y2opt;
```

**Problem:** Grammar supports comma-separated scalar lists OR scalars with inline values, but NOT BOTH in same declaration.

**Current Grammar (gams_grammar.lark line 66-69):**
```
scalar_decl: ID desc_text "/" scalar_data_items "/" (ASSIGN expr)?      -> scalar_with_data
           | ID desc_text ASSIGN expr                                   -> scalar_with_assign
           | ID desc_text                                               -> scalar_plain
           | ID "," id_list                                             -> scalar_list
```

**Issue:** `scalar_list` doesn't support inline values. Need to support MIXED declarations where some scalars have `/value/` and others don't.

**Complete Blocker Chain:**
- **PRIMARY (Sprint 9):** abort$ in if-blocks - ✅ FIXED  
- **SECONDARY (NEW):** Comma-separated scalar declarations with inline values - TO FIX in Sprint 10
- **TERTIARY:** None

**Error Details:**
- Error location: Line 41, column 13
- Error message: "Undefined symbol 'y1opt' referenced [context: assignment]"
- Root cause: Parser doesn't register scalars declared in comma-separated format with inline values
- Parse rate: 65% (41/63 lines before semantic error)

**Progressive Parse Rates:**
- **Current:** 65% (41/63 lines) - Fails at first use of comma-separated scalar (line 41)
- **After fixing comma-separated scalars:** 100% (63/63 lines) - No other blockers found
- **Confidence:** 95%+ (tested by commenting out scalar references - file parses completely)

**Sprint 9 Lessons Learned:**

1. **Verification Failure:**
   - Assumed equation attributes needed WITHOUT grep verification
   - Simple `grep -E "eq.*\.l|eq.*\.m"` would have shown no usage
   - Wasted implementation effort on unnecessary feature

2. **Incomplete Blocker Analysis:**
   - Sprint 9 analysis stopped at first blocker (abort$)
   - Didn't discover secondary blocker (comma-separated scalars)
   - Should have tested with blocker commented out

3. **Hidden Semantic Blockers:**
   - Comma-separated scalar blocker causes SEMANTIC error (undefined symbol)
   - Not immediately obvious as parse blocker
   - Requires deeper analysis to discover

**Sprint 10 Decision: IMPLEMENT**

**Comma-Separated Scalar Declarations with Inline Values:**
- **Effort:** 4-6 hours (LOW-MEDIUM complexity)
- **Complexity:** Extend grammar to support mixed declarations
- **Expected outcome:** mingamma.gms from 65% → 100%
- **Confidence:** 95%+ (no other blockers found)

**Rationale:**
1. LOW-MEDIUM complexity (4-6 hours)
2. Unlocks mingamma.gms completely (65% → 100%)
3. Common GAMS pattern (likely used in other models)
4. Clean implementation (extends existing scalar declaration logic)
5. Fits Sprint 10 alongside circle.gms + himmel16.gms

**Updated Sprint 10 Scope:**
- circle.gms: Function calls (6-10 hours)
- himmel16.gms: Parser bug fix (3-4 hours)
- mingamma.gms: Comma-separated scalar declarations (4-6 hours)
- **Total:** 13-20 hours for 3 models (excellent ROI)
- **Expected outcome:** 9/10 models parsing (90% success rate)

**Unknowns Verified:**
- ✅ Unknown 10.1.4: Sprint 9 assumption COMPLETELY WRONG (equation attributes NOT used, comma-separated scalars is actual blocker)
- ✅ Unknown 10.6.1: abort$ syntax verified (uses square brackets, ✅ FIXED in Sprint 9)
- ✅ Unknown 10.6.2: If-block grammar verified (✅ FIXED in Sprint 9, no additional work needed)

**Model Unlock Prediction:**
- After comma-separated scalar fix: mingamma.gms from 65% → 100%
- Confidence: 95%+ in complete parse success

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` with complete blocker chain
- [x] abort$ syntax analysis (all occurrences, syntax variants, GAMS semantics)
- [x] Verification that equation attributes NOT needed (Sprint 9 assumption incorrect)
- [x] Line-by-line table for all 63 lines
- [x] Model unlock prediction (comma-separated scalar fix unlocks to 100%)
- [x] Synthetic test requirements for comma-separated scalar declarations
- [x] Sprint 9 lessons learned documented
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.4, 10.6.1, 10.6.2

### Acceptance Criteria

- [x] Complete blocker chain documented (abort$ FIXED, comma-separated scalars is actual blocker)
- [x] abort$ in if-blocks thoroughly analyzed (Sprint 9 implementation verified)
- [x] All abort$ occurrences catalogued (2 statements, both in if-blocks)
- [x] GAMS abort$ syntax research completed (square brackets, boolean expressions)
- [x] Verification that equation attributes not required for this model
- [x] Sprint 9 incorrect assumption documented as lesson
- [x] Effort estimate for actual blocker (comma-separated scalars: 4-6 hours)
- [x] Synthetic test requirements specified
- [x] Cross-references Sprint 9 mingamma_blocker_analysis.md
- [x] Unknowns 10.1.4, 10.6.1, 10.6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Research Comma-Separated Declaration Patterns

**Status:** ✅ COMPLETE  
**Actual Time:** 2.0 hours  
**Completed:** 2025-11-23  
**Priority:** High  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 10.2.1, 10.2.2, 10.2.3

### Objective

Research GAMS comma-separated declaration syntax to understand exact grammar requirements before implementation in Sprint 10 Phase 2.

### Why This Matters

**Sprint 10 Phase 2:** Comma-separated declarations marked as "Quick Win" (4-6 hours)

**Current Gap:** Parser requires separate lines for each declaration:
```gams
Variable x1;
Variable x2;
Variable x3;
```

**GAMS Standard:** Supports comma-separated declarations:
```gams
Variable x1, x2, x3;
Parameter a, b, c;
Equation eq1, eq2, eq3;
```

**Risk:** Without understanding edge cases and attribute handling, "quick win" could become complex debugging.

### Background

**Declaration Types to Support:**
- Variable declarations (Free, Positive, Negative, Binary, Integer)
- Parameter declarations
- Equation declarations
- Potentially: Set, Scalar, Alias

**Unknown Edge Cases:**
- Can attributes be specified per variable? `Variable x1 /lo 0/, x2, x3 /up 10/;`
- Trailing commas allowed? `Variable x1, x2, x3,;`
- Whitespace handling? `Variable x1,x2,x3;` vs `Variable x1 , x2 , x3;`
- Mixed types? `Variable x1; Parameter p1, p2;` (should not be allowed)
- Inline text after comma? `Variable x1, * comment * x2;`

### What Needs to Be Done

#### Step 1: Survey GAMSLIB Models for Patterns (45 minutes)

Search all GAMSLIB fixtures for comma-separated declarations:

```bash
# Find all comma-separated Variable declarations
grep -n "^[[:space:]]*Variable" tests/fixtures/gamslib/*.gms | grep ","

# Find all comma-separated Parameter declarations
grep -n "^[[:space:]]*Parameter" tests/fixtures/gamslib/*.gms | grep ","

# Find all comma-separated Equation declarations
grep -n "^[[:space:]]*Equation" tests/fixtures/gamslib/*.gms | grep ","

# Count occurrences
grep -r "^[[:space:]]*Variable.*," tests/fixtures/gamslib/ | wc -l
grep -r "^[[:space:]]*Parameter.*," tests/fixtures/gamslib/ | wc -l
grep -r "^[[:space:]]*Equation.*," tests/fixtures/gamslib/ | wc -l
```

Document:
- How many instances found?
- Which files use this pattern most?
- Are there edge cases in real GAMS code?

#### Step 2: Extract and Catalog Pattern Variations (30 minutes)

For each pattern found, extract to `docs/planning/EPIC_2/SPRINT_10/comma_separated_examples.txt`:

```markdown
## Variable Declarations

### Simple Comma-Separated
File: model1.gms, Line 15
`Variable x1, x2, x3;`

### With Attributes
File: model2.gms, Line 20
`Positive Variable y1, y2;`

### Complex (if found)
File: model3.gms, Line 25
`Variable x1 /lo 0/, x2;`

## Parameter Declarations
[...]

## Equation Declarations
[...]
```

#### Step 3: Research GAMS Documentation (30 minutes)

Check GAMS official documentation:
- Comma-separated declaration syntax specification
- Attribute handling in comma lists
- Edge cases and restrictions
- Error conditions

Document findings in research notes.

#### Step 4: Identify Grammar Production Requirements (15 minutes)

Based on patterns found, specify grammar changes needed:

Current grammar (approximate):
```lark
variable_declaration: "Variable" NAME ";"
```

Required grammar:
```lark
variable_declaration: "Variable" name_list ";"
name_list: NAME ("," NAME)*
```

Questions:
- Is simple comma list sufficient?
- Do we need to support attributes in list?
- How to handle edge cases (trailing commas, etc.)?

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify examples file exists
test -f docs/planning/EPIC_2/SPRINT_10/comma_separated_examples.txt

# Verify pattern counts documented
grep -c "File:" docs/planning/EPIC_2/SPRINT_10/comma_separated_examples.txt
# Should show multiple examples

# Verify grammar requirements documented
grep "grammar" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md
```

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/comma_separated_examples.txt` with real GAMSLIB patterns
- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` with:
  - Pattern frequency analysis
  - Edge cases identified
  - GAMS documentation findings
  - Grammar production requirements
  - Implementation complexity assessment
- [ ] Validation that 4-6 hour estimate is accurate
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.2.1, 10.2.2, 10.2.3

### Acceptance Criteria

- [ ] All comma-separated patterns in GAMSLIB catalogued
- [ ] Pattern frequency documented (how common is this?)
- [ ] Edge cases identified and documented
- [ ] GAMS documentation researched
- [ ] Grammar production changes specified
- [ ] Complexity assessment confirms 4-6 hour estimate
- [ ] No surprising edge cases that increase complexity
- [ ] Cross-references Known Unknowns Category 2 (Semantic)
- [ ] Unknowns 10.2.1, 10.2.2, 10.2.3 verified and updated in KNOWN_UNKNOWNS.md

### Changes

- Created `comma_separated_examples.txt` with 14 instances catalogued from 10 GAMSLib models
- Created `comma_separated_research.md` (comprehensive research document, ~1500 lines)
- Updated KNOWN_UNKNOWNS.md with 3 unknown verifications (10.2.1, 10.2.2, 10.2.3)
- Surveyed 10 GAMSLib models for comma-separated patterns across 5 declaration types
- Researched GAMS official documentation for syntax specifications
- Identified grammar production requirements (only Scalar needs changes)

### Result

**CRITICAL FINDING: Comma-separated declarations are EXTREMELY COMMON (80% of models), not optional.**

**Pattern Frequency (MUCH higher than assumed):**
- Variable: 7/10 models (70%) - 7 instances
- Equation: 6/10 models (60%) - 6 instances
- Scalar: 2/10 models (20%) - 2 instances (1 is mingamma.gms blocker)
- Parameter: 1/10 models (10%) - 1 instance
- Set: 0/10 models (0%)
- **Total: 8/10 models (80%) use comma-separated declarations** (assumed 40-50%)

**Grammar Status Discovery:**
- Variable: ✅ ALREADY SUPPORTED (via `var_list` rule with `id_list`)
- Parameter: ✅ ALREADY SUPPORTED (via `param_list` rule)
- Equation: ✅ ALREADY SUPPORTED (via `eqn_head_list` rule)
- Scalar: ❌ NEEDS FIX - `scalar_list` rule doesn't support inline values

**GAMS Documentation Confirmation:**
- Mixing inline values with plain declarations is **VALID GAMS syntax** (officially documented)
- Type modifiers (Positive, Negative) apply to ALL items in comma-separated list
- No per-item attributes found (only type-level modifiers)
- No edge cases found (no trailing commas, inline comments, mixed types)

**mingamma.gms Blocker Confirmed:**
- Lines 30-38: Scalar comma-separated with mixed inline values
- Pattern: 7 scalars, some with `/value/`, some without
- This is the SECONDARY blocker discovered in Task 5
- Unlocking this pattern enables mingamma.gms: 65% → 100%

**Effort Estimate Validated:**
- Grammar changes: 0.5-1.0h (NOT 2-3h - only Scalar needs work)
- Semantic handler: 2.0-2.5h
- Test coverage: 1.5-2.0h
- **Total: 4.0-5.5 hours** ✅ (within original 4-6h estimate)

**Implementation Approach Defined:**
- Add `scalar_item` rule with 2 alternatives (`scalar_item_with_data`, `scalar_item_plain`)
- Modify `scalar_list` to use `scalar_item ("," scalar_item)*`
- No AST changes required (IR already handles scalars)
- 7 test suites specified for comprehensive coverage

**Sprint 10 Impact:**
- HIGH-PRIORITY feature (affects 80% of models, not niche pattern)
- Unlocks mingamma.gms to 100% parse
- Simplifies 7 other models that already parse
- Expected outcome: 8/10 → 9/10 models (90% success rate)

**Unknowns Verified:**
- 10.2.1: ✅ Frequency is 80% (NOT assumed 40-50%) - HIGH-PRIORITY
- 10.2.2: ✅ Mixing inline values is valid GAMS syntax (documented)
- 10.2.3: ✅ Only Scalar needs grammar changes (NOT 4 types) - grammar work is 0.5-1.0h (NOT 2-3h)

**All deliverables created, all acceptance criteria met.**

---

## Task 7: Survey Existing GAMS Function Call Syntax {#task-7}

**Status:** ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Actual Time:** 2.5 hours  
**Completed:** 2025-11-23  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (circle.gms analysis)  
**Unknowns Verified:** 10.3.1, 10.3.2, 10.3.3, 10.3.4

### Objective

Survey GAMS function call syntax in parameter assignments to understand requirements for implementing circle.gms primary blocker fix.

### Why This Matters

**circle.gms Primary Blocker:** Function calls in parameter assignments
- `uniform(1,10)`, `smin(i, x(i))`, etc.

**Implementation Risk (6-8 hours):** AST changes for parameter initialization

**Research Questions:**
- What functions are used in GAMSLIB models?
- Are function calls nested?
- How do we evaluate vs just parse?
- Are there special functions that need custom handling?

### Background

**Current Parser Behavior:**
- Parameter assignments expect numeric constants: `p = 5;`
- Function calls fail: `p = uniform(1,10);`

**Required Behavior:**
- Parse function call syntax in assignments
- Store function call AST for later evaluation
- May not need to evaluate during parsing (GAMS does this)

**Related:**
- circle.gms uses: `uniform(1,10)`, `smin(i, x(i))`
- Unknown: what other functions exist? how complex are calls?

### What Needs to Be Done

#### Step 1: Survey GAMSLIB for Function Calls in Assignments (1 hour)

Search all GAMSLIB models for function call patterns in parameter context:

```bash
# Find parameter declarations with function calls
grep -n "^\s*\w\+\s*=\s*\w\+(" tests/fixtures/gamslib/*.gms | head -20

# Find specific functions
grep -rn "uniform(" tests/fixtures/gamslib/
grep -rn "normal(" tests/fixtures/gamslib/
grep -rn "smin(" tests/fixtures/gamslib/
grep -rn "smax(" tests/fixtures/gamslib/
grep -rn "sqrt(" tests/fixtures/gamslib/
grep -rn "exp(" tests/fixtures/gamslib/
grep -rn "log(" tests/fixtures/gamslib/
```

Catalog:
- Function names found
- Argument patterns (constants, variables, expressions)
- Nesting level (function calls within function calls)
- Frequency of each function

#### Step 2: Categorize Functions by Type (45 minutes)

Create categories:

**Mathematical Functions:**
- `sqrt`, `exp`, `log`, `sin`, `cos`, `tan`, `power`

**Statistical Functions:**
- `uniform`, `normal`

**Aggregation Functions:**
- `smin`, `smax`, `sum`

**Other:**
- Custom functions?
- Special GAMS functions?

For each category, document:
- Argument types (scalar, indexed, expression)
- Evaluation semantics (parse-time, compile-time, runtime)
- Implementation complexity

#### Step 3: Analyze Evaluation Requirements (30 minutes)

Question: Do we need to EVALUATE function calls during parsing, or just PARSE them?

**Option A: Parse Only**
- Store function call as AST node
- Don't evaluate during parsing
- GAMS compiler evaluates later
- **Effort:** Lower (just grammar changes)

**Option B: Parse and Evaluate**
- Parse to AST
- Evaluate to get numeric value
- Store value in IR
- **Effort:** Higher (need evaluation engine)

Research which option is required:
- Check how current parser handles parameters
- Does IR store expressions or values?
- What does GAMS do at parse vs compile vs runtime?

#### Step 4: Create Implementation Strategy (15 minutes)

Based on findings, specify:

**Grammar Changes:**
```lark
parameter_assignment: NAME "=" (NUMBER | function_call) ";"
function_call: NAME "(" argument_list ")"
argument_list: expression ("," expression)*
```

**AST Changes:**
- Add FunctionCall node type
- Store function name, arguments
- Evaluation strategy (parse-time vs later)

**Effort Validation:**
- Confirm 6-8 hour estimate
- Or revise based on complexity found

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify function catalog exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md

# Verify function categories documented
grep -E "(Mathematical|Statistical|Aggregation)" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md

# Verify evaluation strategy specified
grep -i "evaluation" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md
```

### Deliverables

- [x] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` (1,500+ lines) with:
  - [x] Complete function catalog from GAMSLIB (19 unique functions, 90+ occurrences)
  - [x] Function categories (6 categories: Mathematical, Aggregation, Trigonometric, Statistical, Special, Set)
  - [x] Argument pattern analysis (5 complexity levels, distribution statistics)
  - [x] Nesting analysis (max depth 5, distribution across depths)
  - [x] Evaluation strategy (Option C: parse-only, store as expressions)
  - [x] Grammar production changes required (add 3 functions to FUNCNAME: 5 minutes)
  - [x] AST node type specifications (Call node exists, no changes needed)
  - [x] Effort estimate validation (REVISED: 2.5-3 hours, 62-71% reduction from original 6-8h)
- [x] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.3.1, 10.3.2, 10.3.3, 10.3.4

### Acceptance Criteria

- [x] All GAMSLIB function calls catalogued (19 unique functions across 8/10 models)
- [x] Functions categorized by type (6 categories with complete taxonomy)
- [x] Argument patterns documented (5 complexity levels with distribution)
- [x] Nesting complexity assessed (max depth 5, 89% are ≤2 levels)
- [x] Evaluation strategy determined (parse-only, Option C selected)
- [x] Grammar changes specified (add round, mod, ceil to FUNCNAME token)
- [x] AST changes specified (none needed - Call node exists)
- [x] Effort estimate revised (6-8h → 2.5-3h due to existing infrastructure)
- [x] Cross-references circle.gms blocker analysis (Task 2)
- [x] Cross-references Known Unknowns Category 3 (Function Calls in Parameters)
- [x] Unknowns 10.3.1, 10.3.2, 10.3.3, 10.3.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Research Nested/Subset Indexing Semantics

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Task 4 (maxmin.gms analysis)  
**Unknowns Verified:** 10.5.1, 10.5.2, 10.5.3, 10.5.4, 10.5.5

### Objective

Research GAMS nested/subset indexing semantics to determine implementation complexity and inform Sprint 10 go/no-go decision for maxmin.gms.

### Why This Matters

**maxmin.gms Primary Blocker:** Nested/subset indexing `defdist(low(n,nn))..`

**High Risk:** Sprint 10 plan allocates 10-12 hours but marks as High Risk

**Sprint 10 Decision:** Attempt implementation or defer to Sprint 11?
- If defer → target 90% (9/10 models)
- If attempt → risk consuming sprint without success

**This Research Informs Decision:** Complete semantic understanding required before committing to implementation.

### Background

**Pattern:** `defdist(low(n,nn)).. dist(low) =e= sqrt(...)`

**Questions:**
- What is `low(n,nn)` exactly? (subset? set? indexed set?)
- How does GAMS resolve this at compile time?
- Is this common GAMS pattern or rare edge case?
- Can we support partial functionality (simpler subset syntax)?

**Related Documents:**
- Task 4 maxmin.gms blocker analysis (dependency)
- Sprint 10 PROJECT_PLAN.md risk mitigation section

### What Needs to Be Done

#### Step 1: Study GAMS Documentation on Subsets (1 hour)

Research GAMS documentation:
- Set and subset declarations
- Subset indexing syntax
- Domain restrictions
- Subset references in equation domains

Document:
```markdown
## GAMS Subset Semantics

### Declaration Syntax
[How subsets are declared in GAMS]

### Indexing Syntax
[How subsets are used as indices]

### Domain Restrictions
[How subsets restrict equation domains]

### Resolution Process
[How GAMS resolves subset references]
```

#### Step 2: Analyze maxmin.gms Subset Declarations (1 hour)

Read maxmin.gms to find how `low` is declared:

```bash
# Find set/subset declarations
grep -n "Set\|set\|Subset\|subset" tests/fixtures/gamslib/maxmin.gms

# Find low declaration
grep -n "low" tests/fixtures/gamslib/maxmin.gms | head -10
```

Understand:
- Is `low` a Set, Subset, or Alias?
- What are `n, nn` (indices or elements)?
- How is relationship between `low`, `n`, `nn` established?
- Is this standard GAMS or advanced feature?

Create diagram:
```
Set n "original set"
Set low(n,nn) "2D subset"
Equation defdist(low(n,nn)) "equation indexed by subset"
```

#### Step 3: Search GAMSLIB for Similar Patterns (45 minutes)

Find how common nested/subset indexing is:

```bash
# Search for equation domains with nested parentheses
grep -rn "^\s*\w\+(\w\+(.*))\.\.". tests/fixtures/gamslib/

# Count occurrences
grep -rc "(\w\+(.*))\.\.". tests/fixtures/gamslib/ | grep -v ":0"
```

If rare (1-2 models only):
- Lower priority feature
- Consider defer to Sprint 11

If common (5+ models):
- Higher priority
- Must implement for GAMSLIB coverage

#### Step 4: Assess Implementation Approaches (1 hour)

**Approach A: Full Nested Indexing Support**
- Support arbitrary nesting: `domain(subset(a,b,c))`
- Grammar: recursive domain expressions
- Complexity: High (10-12 hours estimate valid)
- Benefit: Complete GAMS compatibility

**Approach B: Limited Subset Support**
- Support single-level: `domain(subset)` but not `domain(subset(a,b))`
- Grammar: simpler production
- Complexity: Medium (6-8 hours)
- Benefit: May unlock most models, defer complex cases

**Approach C: Defer to Sprint 11**
- Target 90% (9/10 models) without maxmin.gms
- Complexity: None (Sprint 10)
- Benefit: Risk mitigation, more time for research

For each approach:
- Grammar changes required
- AST changes required
- Semantic resolution complexity
- Estimated effort
- Risk assessment

#### Step 5: Make Recommendation (30 minutes)

Based on:
- GAMS semantics complexity
- Pattern frequency in GAMSLIB
- Implementation approach analysis
- Sprint 10 capacity (32-46 hours total)

**Recommendation Framework:**
```markdown
## Nested/Subset Indexing: Sprint 10 Decision

### Complexity Assessment
- GAMS semantics: [Simple/Medium/Complex]
- Pattern frequency: [Rare/Moderate/Common]
- Implementation effort: [6-8/10-12/15+ hours]

### Recommendation
[IMPLEMENT / DEFER]

### Rationale
[Why this decision is appropriate]

### If IMPLEMENT:
- Approach: [A/B]
- Days allocated: [2-3]
- Risk mitigation: [...]

### If DEFER:
- Sprint 10 target: 90% (9/10 models)
- Sprint 11 planning: [...]
- Interim workaround: [if any]
```

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify research document exists
test -f docs/planning/EPIC_2/SPRINT_10/BLOCKERS/nested_indexing_research.md

# Verify GAMS semantics documented
grep "GAMS.*semantics" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/nested_indexing_research.md

# Verify recommendation present
grep -i "recommend" docs/planning/EPIC_2/SPRINT_10/BLOCKERS/nested_indexing_research.md
```

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/nested_indexing_research.md` with:
  - GAMS subset semantics explanation
  - maxmin.gms subset declaration analysis
  - Pattern frequency in GAMSLIB
  - Implementation approach options (A, B, C)
  - Complexity assessment per approach
  - Clear recommendation: IMPLEMENT or DEFER
  - Rationale for recommendation
  - If IMPLEMENT: specific approach and risk mitigation
  - If DEFER: Sprint 10 adjusted target and Sprint 11 plan
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.5.1, 10.5.2, 10.5.3, 10.5.4, 10.5.5

### Acceptance Criteria

- [ ] GAMS subset semantics thoroughly researched
- [ ] maxmin.gms subset pattern fully understood
- [ ] Pattern frequency in GAMSLIB documented
- [ ] At least 3 implementation approaches analyzed
- [ ] Each approach has effort estimate and risk assessment
- [ ] Clear recommendation with strong rationale
- [ ] If defer recommended, Sprint 10 target adjusted to 90%
- [ ] Cross-references maxmin.gms blocker analysis (Task 4)
- [ ] Cross-references Known Unknowns Category 2 and 4
- [ ] Unknowns 10.5.1, 10.5.2, 10.5.3, 10.5.4, 10.5.5 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Design Synthetic Test Framework

**Status:** 🔵 NOT STARTED  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Tasks 2-5 (blocker analyses)  
**Unknowns Verified:** 10.7.1

### Objective

Design framework for creating minimal synthetic GAMS test files that validate individual features in isolation, addressing Sprint 9's inability to validate feature implementations.

### Why This Matters

**Sprint 9 Lesson:** Cannot validate i++1 indexing works correctly because himmel16.gms has secondary blockers. Feature may have bugs hidden by other failures.

**Sprint 10 Phase 5:** Synthetic test suite for feature validation

**Required Tests:**
- Sprint 9 features: i++1 indexing, equation attributes, model sections
- Sprint 10 features: function calls, level bounds, nested indexing, abort$, comma-separated

**Without Synthetic Tests:** Cannot distinguish feature bugs from secondary blocker issues.

### Background

**Current Testing Approach:**
- Parse complex GAMSLIB models (himmel16.gms, etc.)
- If fails, can't tell if feature implementation is wrong or secondary blocker exists

**Synthetic Testing Approach:**
- Create minimal GAMS file testing ONE feature
- If fails, feature implementation definitely wrong
- If passes, feature works (blockers in complex models are separate issues)

**Example:**
```gams
* Synthetic test: i++1 indexing
Set i /i1*i3/;
Variable x(i);
Equation test(i);
test(i).. x(i) =e= x(i++1);  * Test i++1 syntax
```

If this minimal file parses → i++1 implementation works
If fails → i++1 implementation has bugs

### What Needs to Be Done

#### Step 1: Define Synthetic Test Principles (30 minutes)

Document test design principles:

**Minimal:**
- Only declarations needed for feature
- No extra complexity
- Typically 5-15 lines

**Isolated:**
- Tests ONE feature only
- No interaction with other features
- No complex GAMS constructs

**Validating:**
- If test passes, feature definitely works
- If test fails, feature definitely broken
- Clear pass/fail criteria

**Automatable:**
- Can run via pytest
- Clear success criteria
- Fast execution (<1 second)

#### Step 2: Design Test Structure (1 hour)

Create template for synthetic tests:

```gams
* Synthetic Test: [FEATURE NAME]
* Purpose: Validate [feature] works in isolation
* Expected: [PARSE SUCCESS / PARSE FAILURE / specific behavior]
*
* Feature: [description]
* Minimal Example: [what makes this test minimal]

[GAMS code - minimal declarations and feature usage]

* Verification:
* - Parser should [succeed/fail]
* - IR should contain [expected elements]
* - No other features required
```

Create directory structure:
```
tests/synthetic/
├── README.md (explains synthetic test framework)
├── i_plusplus_indexing.gms
├── equation_attributes.gms
├── model_sections.gms
├── function_calls.gms
├── level_bounds.gms
├── nested_indexing.gms
├── abort_in_if_blocks.gms
├── comma_separated_declarations.gms
└── test_synthetic.py (pytest file)
```

#### Step 3: Specify Test Cases Per Feature (1 hour)

For each feature, specify:

**i++1 Indexing:**
```markdown
### Feature: Lead/Lag Indexing

**Minimal Test:**
- Set with 3+ elements
- Variable indexed by set
- Equation using i++1 in expression
- No other features

**Expected Result:**
- Parse succeeds
- IR contains equation with i++1 reference
- No semantic errors

**Test File:** `tests/synthetic/i_plusplus_indexing.gms`
```

**Function Calls in Parameters:**
```markdown
### Feature: Function Calls in Parameter Assignments

**Minimal Test:**
- Parameter declaration
- Assignment with function call: p = uniform(1,10)
- No variables, equations, or complex features

**Expected Result:**
- Parse succeeds
- IR contains parameter with FunctionCall AST node
- Function name and arguments captured

**Test File:** `tests/synthetic/function_calls.gms`
```

Repeat for all features:
- Equation attributes
- Model sections
- Level bounds
- Nested indexing
- abort$ in if-blocks
- Comma-separated declarations

#### Step 4: Design Pytest Integration (30 minutes)

Create `tests/synthetic/test_synthetic.py`:

```python
"""
Synthetic tests for individual parser features.

Each test validates ONE feature in isolation using minimal GAMS code.
Tests should be fast (<1s each) and have clear pass/fail criteria.
"""

import pytest
from pathlib import Path
from src.ir.parser import parse_model_file

SYNTHETIC_DIR = Path(__file__).parent

@pytest.mark.parametrize("test_file,should_parse", [
    ("i_plusplus_indexing.gms", True),
    ("equation_attributes.gms", True),
    ("model_sections.gms", True),
    # Sprint 10 features (initially expected to fail, then pass after implementation)
    ("function_calls.gms", False),  # Will pass after implementing
    ("level_bounds.gms", False),
    ("nested_indexing.gms", False),
    ("abort_in_if_blocks.gms", False),
    ("comma_separated_declarations.gms", False),
])
def test_synthetic_feature(test_file, should_parse):
    """Test that feature works in isolation."""
    file_path = SYNTHETIC_DIR / test_file
    
    if should_parse:
        # Feature should work
        result = parse_model_file(str(file_path))
        assert result is not None
    else:
        # Feature not yet implemented (expected to fail)
        with pytest.raises(Exception):
            parse_model_file(str(file_path))
```

Update test expectations as features implemented during Sprint 10.

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify synthetic test directory exists
test -d tests/synthetic

# Verify README exists
test -f tests/synthetic/README.md

# Verify test files exist (initially can be templates)
ls tests/synthetic/*.gms | wc -l
# Should be >= 8 files

# Verify pytest integration
test -f tests/synthetic/test_synthetic.py

# Run synthetic tests (will fail for unimplemented features)
pytest tests/synthetic/test_synthetic.py -v
```

### Deliverables

- [ ] `tests/synthetic/README.md` explaining synthetic test framework
- [ ] Synthetic test design principles documented
- [ ] Test template defined
- [ ] Directory structure created: `tests/synthetic/`
- [ ] Test file specifications for 8+ features:
  - i++1 indexing (Sprint 9)
  - Equation attributes (Sprint 9)
  - Model sections (Sprint 9)
  - Function calls (Sprint 10)
  - Level bounds (Sprint 10)
  - Nested indexing (Sprint 10)
  - abort$ in if-blocks (Sprint 10)
  - Comma-separated declarations (Sprint 10)
- [ ] Pytest integration designed (`test_synthetic.py`)
- [ ] Template GAMS files created (can be minimal stubs for prep)
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknown 10.7.1

### Acceptance Criteria

- [ ] Synthetic test framework principles documented
- [ ] Test template clearly defined
- [ ] Directory structure created
- [ ] Specifications for 8+ features documented
- [ ] Each specification includes minimal test description
- [ ] Each specification includes expected parse result
- [ ] Pytest integration designed with parametrized tests
- [ ] Tests can run (initially fail for unimplemented features - expected)
- [ ] Cross-references blocker analyses (Tasks 2-5)
- [ ] Cross-references Known Unknowns Category 3 (Validation)
- [ ] Unknown 10.7.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Validate Sprint 9 Features Work in Isolation

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** Task 9 (synthetic test framework)  
**Unknowns Verified:** 10.7.2

### Objective

Create and run synthetic tests for Sprint 9 features (i++1 indexing, equation attributes, model sections) to verify implementations work correctly in isolation.

### Why This Matters

**Sprint 9 Status:** Features implemented but cannot validate they work because target models still blocked by secondary issues.

**Critical Question:** Do Sprint 9 features actually work, or do they have bugs hidden by complex model failures?

**Sprint 10 Dependency:** Before implementing Sprint 10 features, we should know Sprint 9 features are solid.

### Background

**Sprint 9 Features Implemented:**
1. **i++1 Indexing:** Lead/lag operators (i++1, i--1)
2. **Equation Attributes:** Parsing .l, .m on equations
3. **Model Sections:** Multi-line model declarations with `/` syntax

**Validation Gap:**
- himmel16.gms still fails (has secondary blocker)
- hs62.gms now parses (success!) ✅
- mingamma.gms still fails (different blocker than assumed)

**Unknown:** Do i++1 and equation attributes actually work? Or just untested due to complex model failures?

### What Needs to Be Done

#### Step 1: Create Synthetic Test for i++1 Indexing (30 minutes)

Create `tests/synthetic/i_plusplus_indexing.gms`:

```gams
* Synthetic Test: i++1 Lead/Lag Indexing
* Purpose: Validate lead/lag operators work in isolation
* Expected: Parse succeeds, IR contains circular indexing

Set i "simple set" /i1*i5/;
Variable x(i) "test variable";
Equation test(i) "test equation with i++1";

test(i).. x(i) =e= x(i++1) + x(i--1);

* Verification:
* - Should parse successfully
* - Equation should reference i++1 and i--1
* - No errors about index syntax
```

Run test:
```bash
python -c "
from src.ir.parser import parse_model_file
result = parse_model_file('tests/synthetic/i_plusplus_indexing.gms')
print(f'SUCCESS: Parsed')
print(f'Equations: {len(result.equations)}')
# Verify equation contains i++1 reference
"
```

If fails → i++1 implementation has bugs, must fix before Sprint 10
If passes → i++1 works, himmel16.gms failure is secondary blocker ✅

#### Step 2: Create Synthetic Test for Equation Attributes (30 minutes)

Create `tests/synthetic/equation_attributes.gms`:

```gams
* Synthetic Test: Equation Attributes
* Purpose: Validate .l, .m attribute parsing
* Expected: Parse succeeds, attributes captured

Variable x "test variable";
Equation eq "test equation";

eq.. x =e= 5;
eq.l = 10;  * Level attribute
eq.m = 2;   * Marginal attribute

* Verification:
* - Should parse successfully
* - Equation should have .l and .m attributes
* - Attribute values stored in IR
```

Run test and verify parse succeeds.

If fails → equation attributes broken
If passes → equation attributes work, mingamma.gms has different blocker ✅

#### Step 3: Create Synthetic Test for Model Sections (30 minutes)

Create `tests/synthetic/model_sections.gms`:

```gams
* Synthetic Test: Model Sections
* Purpose: Validate multi-line model declarations
* Expected: Parse succeeds

Variable x;
Equation eq;
eq.. x =e= 0;

Model test /
    eq
/;

* Verification:
* - Should parse successfully
* - Model declaration captured
```

Run test.

Note: hs62.gms now parses, suggesting model sections work. This test confirms.

#### Step 4: Update Pytest with Sprint 9 Tests (30 minutes)

Update `tests/synthetic/test_synthetic.py`:

```python
@pytest.mark.parametrize("test_file,feature,should_pass", [
    # Sprint 9 features (should all pass now)
    ("i_plusplus_indexing.gms", "i++1 indexing", True),
    ("equation_attributes.gms", "equation attributes", True),
    ("model_sections.gms", "model sections", True),
    
    # Sprint 10 features (not yet implemented)
    ("function_calls.gms", "function calls", False),
    ("level_bounds.gms", "level bounds", False),
    ("nested_indexing.gms", "nested indexing", False),
    ("abort_in_if_blocks.gms", "abort$ in if-blocks", False),
    ("comma_separated_declarations.gms", "comma-separated declarations", False),
])
def test_synthetic_parser_feature(test_file, feature, should_pass):
    """Test individual parser features in isolation."""
    # ...
```

Run tests:
```bash
pytest tests/synthetic/test_synthetic.py -v -k "sprint_9"
```

All Sprint 9 tests should pass. If any fail, feature implementation has bugs that must be fixed.

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify Sprint 9 synthetic tests exist
test -f tests/synthetic/i_plusplus_indexing.gms
test -f tests/synthetic/equation_attributes.gms
test -f tests/synthetic/model_sections.gms

# Run Sprint 9 synthetic tests
pytest tests/synthetic/test_synthetic.py -v

# All Sprint 9 tests should PASS
pytest tests/synthetic/test_synthetic.py -v | grep "PASSED" | wc -l
# Should be >= 3
```

### Deliverables

- [ ] `tests/synthetic/i_plusplus_indexing.gms` testing i++1 feature
- [ ] `tests/synthetic/equation_attributes.gms` testing .l, .m attributes
- [ ] `tests/synthetic/model_sections.gms` testing multi-line model declarations
- [ ] Pytest integration in `test_synthetic.py`
- [ ] Test run results documented
- [ ] If any tests fail: bug report for Sprint 9 features
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknown 10.7.2

### Acceptance Criteria

- [ ] All 3 Sprint 9 synthetic tests created
- [ ] Tests are minimal (5-15 lines each)
- [ ] Tests validate ONE feature each
- [ ] Tests run via pytest
- [ ] All Sprint 9 tests PASS (if fail, bugs must be fixed before Sprint 10)
- [ ] Test results documented
- [ ] Confirms Sprint 9 features work in isolation
- [ ] Cross-references Sprint 9 feature implementations
- [ ] Cross-references synthetic test framework (Task 9)
- [ ] Unknown 10.7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 11: Set Up Mid-Sprint Checkpoint Infrastructure

**Status:** 🔵 NOT STARTED  
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Development team  
**Dependencies:** None

### Objective

Set up automated infrastructure for Sprint 10 Day 5 mid-sprint checkpoint to validate parse rate improvement matches projections.

### Why This Matters

**Sprint 9 Lesson:** Features complete by Day 5, but 0% parse rate improvement discovered only on Day 10. Too late to pivot.

**Sprint 10 Phase 4:** Mid-sprint checkpoint at Day 5 to validate impact

**Checkpoint Decision:**
- If parse rate improving → continue with remaining features
- If parse rate flat → investigate why, pivot if needed

**Infrastructure Needed:**
- Script to measure parse rate
- Dashboard to show progress
- Automated checkpoint execution

### Background

**Sprint 10 Goal:** 60% → 100% parse rate (40 percentage point increase)

**Day 5 Expectation:** Should see progress toward 100%
- If implementing function calls → circle.gms should parse
- If implementing level bounds → himmel16.gms should parse
- If no progress → investigate immediately, not on Day 10

**Checkpoint Process:**
1. Run parser on all 10 models
2. Calculate parse rate percentage
3. Compare to baseline (60%)
4. Compare to projection (based on features completed)
5. Alert if behind projection

### What Needs to Be Done

#### Step 1: Create Parse Rate Measurement Script (30 minutes)

Create `scripts/measure_parse_rate.py`:

```python
#!/usr/bin/env python3
"""
Measure parse rate across GAMSLIB Tier 1 models.

Usage:
    python scripts/measure_parse_rate.py [--verbose]

Output:
    Parse rate percentage and per-model status
"""

import sys
from pathlib import Path
from src.ir.parser import parse_model_file

TIER1_MODELS = [
    "circle", "himmel16", "hs62", "mathopt1", 
    "maxmin", "mhw4d", "mhw4dx", "mingamma", 
    "rbrock", "trig"
]

def check_parse(model_name):
    """Check if model parses successfully."""
    try:
        path = f"tests/fixtures/gamslib/{model_name}.gms"
        parse_model_file(path)
        return True
    except Exception:
        return False

def main():
    verbose = "--verbose" in sys.argv
    
    results = {}
    for model in TIER1_MODELS:
        results[model] = check_parse(model)
        if verbose:
            status = "✅ PASS" if results[model] else "❌ FAIL"
            print(f"{model:15} {status}")
    
    total = len(TIER1_MODELS)
    passing = sum(results.values())
    rate = (passing / total) * 100
    
    print(f"\nParse Rate: {rate:.0f}% ({passing}/{total} models)")
    print(f"Passing: {', '.join(m for m,p in results.items() if p)}")
    print(f"Failing: {', '.join(m for m,p in results.items() if not p)}")
    
    return 0 if passing == total else 1

if __name__ == "__main__":
    sys.exit(main())
```

Test script:
```bash
python scripts/measure_parse_rate.py --verbose
```

#### Step 2: Create Checkpoint Script (30 minutes)

Create `scripts/sprint10_checkpoint.sh`:

```bash
#!/bin/bash
# Sprint 10 Mid-Sprint Checkpoint (Day 5)
# Validates parse rate improvement matches projections

set -e

echo "============================================"
echo "Sprint 10 Mid-Sprint Checkpoint (Day 5)"
echo "============================================"
echo ""

# Baseline (Sprint 10 Day 0)
BASELINE_RATE=60
BASELINE_COUNT=6

# Target (Sprint 10 Day 10)
TARGET_RATE=100
TARGET_COUNT=10

# Day 5 Projection (should be progressing toward target)
# Assume linear progress: Day 5 should be ~80% (6 + 2 models)
DAY5_MIN_RATE=70  # Conservative: should have unlocked at least 1 more model
DAY5_MIN_COUNT=7

echo "Baseline (Day 0): ${BASELINE_RATE}% (${BASELINE_COUNT}/10 models)"
echo "Target (Day 10): ${TARGET_RATE}% (${TARGET_COUNT}/10 models)"
echo "Day 5 Minimum Expected: ${DAY5_MIN_RATE}% (${DAY5_MIN_COUNT}/10 models)"
echo ""

# Measure current parse rate
echo "Measuring current parse rate..."
python scripts/measure_parse_rate.py --verbose > /tmp/checkpoint_results.txt
cat /tmp/checkpoint_results.txt
echo ""

# Extract parse rate
CURRENT_RATE=$(grep "Parse Rate:" /tmp/checkpoint_results.txt | grep -oE "[0-9]+%")
CURRENT_COUNT=$(grep "Parse Rate:" /tmp/checkpoint_results.txt | grep -oE "[0-9]+/10" | cut -d/ -f1)

echo "============================================"
echo "Checkpoint Results"
echo "============================================"
echo "Current: ${CURRENT_RATE} (${CURRENT_COUNT}/10 models)"
echo "Baseline: ${BASELINE_RATE}% (${BASELINE_COUNT}/10)"
echo "Progress: +$((CURRENT_COUNT - BASELINE_COUNT)) models"
echo ""

# Check if on track
if [ "$CURRENT_COUNT" -ge "$DAY5_MIN_COUNT" ]; then
    echo "✅ ON TRACK: Parse rate improving as expected"
    echo "   Continue with remaining features"
    exit 0
else
    echo "⚠️  BEHIND PROJECTION: Parse rate not improving as expected"
    echo ""
    echo "Action Required:"
    echo "  1. Investigate why features aren't unlocking models"
    echo "  2. Review blocker analysis assumptions"
    echo "  3. Check for secondary blockers not identified"
    echo "  4. Consider pivot: focus on models closest to parsing"
    echo ""
    echo "Models still failing:"
    grep "❌ FAIL" /tmp/checkpoint_results.txt || true
    echo ""
    exit 1
fi
```

Make executable:
```bash
chmod +x scripts/sprint10_checkpoint.sh
```

#### Step 3: Document Checkpoint Process (15 minutes)

Create `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md`:

```markdown
# Sprint 10 Mid-Sprint Checkpoint (Day 5)

## Purpose
Validate parse rate improvement matches projections to catch issues early.

## When to Run
**Sprint 10 Day 5** (midpoint of 2-week sprint)

## How to Run
```bash
./scripts/sprint10_checkpoint.sh
```

## Expected Results

### On Track (✅)
- Parse rate ≥70% (7+/10 models)
- At least 1 model unlocked since Day 0
- Progress toward 100% target visible

**Action:** Continue with remaining features

### Behind Projection (⚠️)
- Parse rate <70% (<7/10 models)
- No models unlocked since Day 0
- Features implemented but models still blocked

**Actions:**
1. Investigate why features aren't unlocking models
2. Review blocker analysis - were assumptions correct?
3. Check for hidden secondary/tertiary blockers
4. Pivot strategy if needed

## Interpretation

**If feature implemented but model still blocked:**
- Secondary blocker exists (not identified in prep)
- Blocker analysis was incomplete
- Must perform deeper analysis before continuing

**If no features completed by Day 5:**
- Implementation taking longer than estimated
- Reassess sprint scope
- May need to reduce target (e.g., 90% instead of 100%)
```

#### Step 4: Add to Sprint 10 Schedule (15 minutes)

Add checkpoint to sprint plan with reminder to run on Day 5.

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify scripts exist and are executable
test -x scripts/measure_parse_rate.py
test -x scripts/sprint10_checkpoint.sh

# Verify documentation exists
test -f docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md

# Test parse rate script runs
python scripts/measure_parse_rate.py --verbose

# Test checkpoint script runs (will show current baseline)
./scripts/sprint10_checkpoint.sh
```

### Deliverables

- [ ] `scripts/measure_parse_rate.py` to measure parse rate across 10 models
- [ ] `scripts/sprint10_checkpoint.sh` to run Day 5 checkpoint
- [ ] `docs/planning/EPIC_2/SPRINT_10/CHECKPOINT.md` documenting process
- [ ] Scripts are executable and tested
- [ ] Checkpoint thresholds defined (70% minimum for Day 5)
- [ ] Action steps defined for on-track and behind-projection scenarios

### Acceptance Criteria

- [ ] Parse rate measurement script works correctly
- [ ] Checkpoint script runs and validates against thresholds
- [ ] Thresholds set appropriately (Day 5 minimum: 70%, 7/10 models)
- [ ] Documentation explains when and how to run checkpoint
- [ ] Documentation defines actions for each scenario
- [ ] Scripts tested with current codebase (baseline: 60%)
- [ ] Cross-references Sprint 10 Phase 4 (Mid-Sprint Checkpoint)
- [ ] Cross-references Sprint 9 retrospective lesson (late discovery issue)

---

## Task 12: Plan Sprint 10 Detailed Schedule

**Status:** 🔵 NOT STARTED  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Sprint 10 Day 1  
**Owner:** Sprint planning  
**Dependencies:** All previous tasks (1-11)

### Objective

Create detailed day-by-day schedule for Sprint 10 execution, incorporating all prep research findings and blocker analysis results.

### Why This Matters

**Sprint 10 Phases:** 5 phases over 2 weeks (10 working days)
1. Dependency Analysis (6-9 hours)
2. Comma-Separated Declarations (4-6 hours)
3. Targeted Feature Implementation (20-26 hours)
4. Mid-Sprint Checkpoint (1-2 hours)
5. Synthetic Test Suite (3-4 hours)

**Total Effort:** 32-46 hours in ~40-hour sprint

**Dependency:** Task 8 (nested indexing research) informs if maxmin.gms attempted or deferred
- If attempt: full 100% target
- If defer: adjust to 90% target

**Schedule Must Account For:**
- Blocker dependencies (can't test fix until implemented)
- Checkpoint at Day 5
- Risk mitigation (high-complexity features)
- Buffer time for unknowns

### Background

**Sprint 10 Structure:**
- 2 weeks = 10 working days
- ~4 hours/day = ~40 hours total
- Must fit 32-46 hours of work

**Critical Dependencies:**
- Dependency analysis (Phase 1) must complete BEFORE implementation (Phase 3)
- Checkpoint (Phase 4) must occur on Day 5
- Synthetic tests (Phase 5) should run throughout, not just at end

**Inputs from Prep Tasks:**
- Task 1: Known unknowns to monitor
- Tasks 2-5: Blocker chains per model
- Task 6: Comma-separated declaration requirements
- Task 7: Function call implementation approach
- Task 8: Nested indexing decision (implement or defer)
- Task 9: Synthetic test framework
- Task 10: Sprint 9 feature validation results
- Task 11: Checkpoint infrastructure

### What Needs to Be Done

#### Step 1: Review All Prep Task Results (1 hour)

Read deliverables from Tasks 1-11:
- Known Unknowns list
- 4 blocker analyses
- Research documents
- Synthetic test framework
- Checkpoint setup

Extract key inputs for scheduling:
- Which features have blocker chains fully analyzed?
- Which features are high risk?
- What is nested indexing decision?
- What effort estimates were validated?

#### Step 2: Create Day-by-Day Schedule (2 hours)

Create `docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md`:

**Template:**

```markdown
# Sprint 10 Detailed Schedule

## Week 1 (Days 1-5)

### Day 1: Phase 1 Dependency Analysis + Quick Win Start
**Time: 4 hours**

**Morning (2 hours):**
- [ ] Final review of blocker analyses (Tasks 2-5 results)
- [ ] Confirm all dependency chains documented
- [ ] Create BLOCKER_ANALYSIS.md consolidation

**Afternoon (2 hours):**
- [ ] Start Phase 2: Comma-separated declarations
- [ ] Grammar changes
- [ ] Initial tests

**Deliverables:**
- Complete BLOCKER_ANALYSIS.md with all 4 models
- Comma-separated grammar updated

**Risks:**
- Blocker analysis may reveal gaps from prep

---

### Day 2: Comma-Separated Declarations (Complete)
**Time: 4 hours**

**All Day:**
- [ ] Complete comma-separated implementation
- [ ] AST changes
- [ ] Parser updates
- [ ] Unit tests
- [ ] Integration tests
- [ ] Synthetic test validation

**Deliverables:**
- Comma-separated declarations working
- Tests passing
- Feature validated in synthetic test

**Milestone:** Phase 2 complete ✅

---

### Day 3: Phase 3 Feature Implementation (Start)
**Time: 4 hours**

**Choice based on Task 8 (Nested Indexing Research):**

**Option A: If attempting maxmin.gms**
- [ ] Start nested indexing (10-12 hour feature)
- [ ] Grammar research
- [ ] Initial grammar changes

**Option B: If deferring maxmin.gms**
- [ ] Start function calls (6-8 hour feature)
- [ ] Grammar changes
- [ ] AST updates

**Deliverables:**
- First feature implementation in progress

**Risks:**
- Features may be more complex than estimated

---

### Day 4: Feature Implementation (Continue)
**Time: 4 hours**

**Continue Day 3 feature:**
- [ ] Complete implementation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Synthetic test validation

**Deliverables:**
- First feature complete OR significant progress

**Prepare for Day 5 Checkpoint:**
- [ ] Ensure parse rate script ready
- [ ] Document features completed so far

---

### Day 5: MID-SPRINT CHECKPOINT + Feature Implementation
**Time: 4 hours**

**Morning (1 hour): CHECKPOINT**
- [ ] Run `./scripts/sprint10_checkpoint.sh`
- [ ] Measure parse rate
- [ ] Compare to baseline (60%)
- [ ] Evaluate progress

**Decision Point:**
- ✅ On track (≥70%, 7+/10 models) → Continue
- ⚠️ Behind (< 70%) → Investigate and pivot

**Afternoon (3 hours):**
- [ ] Continue feature implementation
- [ ] Start next feature (level bounds or abort$)

**Deliverables:**
- Checkpoint results documented
- Decision made (continue or pivot)
- Additional feature in progress

---

## Week 2 (Days 6-10)

### Day 6: Feature Implementation (Continue)
**Time: 4 hours**

**Continue features from Phase 3:**
- [ ] Level bound conflict resolution (2-3 hours)
- [ ] abort$ in if-blocks (2-3 hours)
- [ ] Tests for each

**Deliverables:**
- 2-3 features complete by end of day

---

### Day 7: Feature Implementation (Final) + Testing
**Time: 4 hours**

**Morning (2 hours):**
- [ ] Complete any remaining features
- [ ] Final integration tests

**Afternoon (2 hours):**
- [ ] Run all GAMSLIB models
- [ ] Measure parse rate
- [ ] Document which models now parse

**Deliverables:**
- All Phase 3 features complete
- Parse rate measured

---

### Day 8: Phase 5 Synthetic Test Suite
**Time: 4 hours**

**All Day:**
- [ ] Create synthetic tests for all new features
- [ ] Validate i++1 indexing works (Sprint 9)
- [ ] Validate equation attributes work (Sprint 9)
- [ ] Validate model sections work (Sprint 9)
- [ ] Validate new Sprint 10 features
- [ ] Run full synthetic test suite

**Deliverables:**
- Synthetic test suite complete
- All tests passing (for implemented features)

---

### Day 9: Validation + Documentation
**Time: 4 hours**

**Morning (2 hours):**
- [ ] Run full test suite (1400+ tests)
- [ ] Fix any regressions
- [ ] Update GAMSLIB_CONVERSION_STATUS.md

**Afternoon (2 hours):**
- [ ] Document parse rate achievement
- [ ] Update sprint status
- [ ] Prepare for Day 10 completion

**Deliverables:**
- All tests passing
- Documentation updated
- Parse rate confirmed

---

### Day 10: Sprint Completion + Retrospective
**Time: 4 hours**

**Morning (2 hours):**
- [ ] Final parse rate measurement
- [ ] Verify 100% (or 90% if maxmin deferred)
- [ ] Tag v0.10.0 release

**Afternoon (2 hours):**
- [ ] Sprint 10 retrospective
- [ ] Document lessons learned
- [ ] Identify Sprint 11 preparation needs

**Deliverables:**
- Sprint 10 complete
- v0.10.0 released
- Retrospective documented

---

## Contingency Plans

### If Nested Indexing Too Complex
**Trigger:** Day 3-5, nested indexing not progressing
**Action:** 
- Defer maxmin.gms to Sprint 11
- Adjust target to 90% (9/10 models)
- Focus on other features

### If Behind Schedule at Checkpoint
**Trigger:** Day 5, <70% parse rate
**Action:**
- Investigate blocker analysis assumptions
- Identify quick wins
- Reduce scope if needed

### If Feature Implementation Blocked
**Trigger:** Any day, feature has unexpected complexity
**Action:**
- Review blocker analysis
- Check for secondary blockers
- Adjust schedule, defer if needed
```

#### Step 3: Create Risk Mitigation Plan (30 minutes)

For each high-risk item:
- **Nested indexing (10-12 hours):** Defer decision point on Day 3
- **Function calls (6-8 hours):** Budget extra time if eval needed
- **Secondary blockers:** Checkpoint catches early

Document mitigation strategies.

#### Step 4: Validate Schedule Feasibility (30 minutes)

Check:
- Total hours in schedule ≤ 40
- Critical path identified
- Dependencies respected
- Buffer time for unknowns
- Checkpoint properly placed

Adjust if needed.

### Changes

*To be completed during prep phase*

### Result

*To be completed during prep phase*

### Verification

```bash
# Verify schedule document exists
test -f docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md

# Verify contains all 10 days
grep -c "### Day" docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md
# Should be 10

# Verify checkpoint on Day 5
grep "Day 5.*CHECKPOINT" docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md

# Verify contingency plans
grep -i "contingency" docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md
```

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md` with day-by-day plan
- [ ] All 10 days scheduled with tasks and deliverables
- [ ] Mid-sprint checkpoint on Day 5
- [ ] Phases properly distributed across days
- [ ] Dependencies respected in ordering
- [ ] Contingency plans for high-risk items
- [ ] Risk mitigation strategies documented
- [ ] Total hours validated (≤40)

### Acceptance Criteria

- [ ] Schedule covers all 10 days of Sprint 10
- [ ] Each day has 4 hours of work planned
- [ ] Phase 1 (Dependency Analysis) on Day 1
- [ ] Phase 2 (Comma-separated) on Days 1-2
- [ ] Phase 3 (Feature Implementation) on Days 3-7
- [ ] Phase 4 (Checkpoint) on Day 5
- [ ] Phase 5 (Synthetic Tests) on Day 8
- [ ] Validation and completion on Days 9-10
- [ ] Dependencies respected (analysis before implementation)
- [ ] Checkpoint properly integrated
- [ ] Contingency plans for nested indexing, behind schedule, blocked features
- [ ] Total scheduled hours ≤ 40
- [ ] Cross-references all prep tasks (1-11)
- [ ] Cross-references blocker analyses
- [ ] Cross-references Sprint 10 PROJECT_PLAN.md phases

---

## Summary

### Total Estimated Prep Time
- **Minimum:** 24 hours (~3 working days)
- **Maximum:** 30 hours (~4 working days)
- **Critical Path:** Tasks 1 → 2,3,4,5 → 8 → 12 (must complete before Sprint 10)

### Critical Path Tasks
1. **Task 1:** Create Known Unknowns List (foundation for all analysis)
2. **Tasks 2-5:** Complete blocker analyses (understand what to implement)
3. **Task 8:** Nested indexing research (informs 100% vs 90% target decision)
4. **Task 12:** Create detailed schedule (execution plan)

### Success Criteria

**Prep Phase Complete When:**
- [ ] All 30+ unknowns documented with verification plans
- [ ] All 4 models have complete blocker chain analyses
- [ ] Nested indexing decision made (implement or defer)
- [ ] Synthetic test framework designed and Sprint 9 features validated
- [ ] Checkpoint infrastructure ready
- [ ] Detailed day-by-day schedule created
- [ ] No surprises remain (all assumptions validated or documented as unknowns)

**Sprint 10 Ready When:**
- [ ] Know exact features to implement (from blocker analyses)
- [ ] Know implementation approach (from research tasks)
- [ ] Know validation strategy (synthetic tests)
- [ ] Know decision points (checkpoint on Day 5, nested indexing on Day 3)
- [ ] Know risks and mitigations (contingency plans)

### Integration with Sprint 10

**Prep deliverables feed into Sprint 10 phases:**

- **Phase 1 (Dependency Analysis):** Uses Tasks 2-5 blocker analyses
- **Phase 2 (Comma-Separated):** Uses Task 6 research
- **Phase 3 (Features):** Uses Tasks 7-8 implementation research
- **Phase 4 (Checkpoint):** Uses Task 11 infrastructure
- **Phase 5 (Synthetic Tests):** Uses Tasks 9-10 framework

**Known Unknowns (Task 1) monitors throughout sprint**

---

## Appendix: Document Cross-References

### Sprint 10 Planning Documents
- `docs/planning/EPIC_2/PROJECT_PLAN.md` (lines 286-433) - Sprint 10 goals and phases
- `docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md` - To be created (Task 1)
- `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/*.md` - To be created (Tasks 2-5, 6-8)
- `docs/planning/EPIC_2/SPRINT_10/SCHEDULE.md` - To be created (Task 12)

### Sprint 9 Reference Documents
- `docs/planning/EPIC_2/SPRINT_9/RETROSPECTIVE.md` - Root cause analysis, recommendations
- `docs/planning/EPIC_2/SPRINT_9/MHW4DX_BLOCKER_ANALYSIS.md` - Example of complete blocker analysis
- `docs/planning/EPIC_2/SPRINT_9/mingamma_blocker_analysis.md` - Partial analysis example
- `docs/planning/EPIC_2/SPRINT_9/KNOWN_UNKNOWNS.md` - Sprint 9 unknown tracking example
- `docs/planning/EPIC_2/SPRINT_9/LEAD_LAG_INDEXING_RESEARCH.md` - i++1 implementation details

### Research Documents
- Exploration report (from Task tool analysis) - GAMSLIB blocker summary

### Epic Goals
- `docs/planning/EPIC_2/GOALS.md` - Epic 2 objectives (parse rate, conversion pipeline)

### Follow-On Items
- Sprint 9 follow-ons feed into Sprint 10 planning

---

**Last Updated:** [To be updated during prep phase]  
**Status:** 🔵 NOT STARTED  
**Next Action:** Begin Task 1 (Create Known Unknowns List)
