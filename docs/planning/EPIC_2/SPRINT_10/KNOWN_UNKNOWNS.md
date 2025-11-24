# Sprint 10 Known Unknowns

**Created:** November 23, 2025  
**Status:** Active - Pre-Sprint 10  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 10 complete GAMSLIB Tier 1 parse coverage through comprehensive dependency analysis and targeted feature implementation

---

## Overview

This document identifies all assumptions and unknowns for Sprint 10 **before** implementation begins. This addresses the critical Sprint 9 lesson: features implemented ≠ models unlocked without complete blocker chain analysis.

**Sprint 9 Retrospective Key Finding:** Despite implementing 3 features (i++1 indexing, model sections, equation attributes), parse rate remained at 40% (0% improvement). Root cause: incomplete dependency analysis. Features were implemented but models still blocked by undiscovered secondary/tertiary blockers.

**Sprint 10 Scope:**
1. **Phase 1:** Comprehensive Dependency Analysis (6-9h) - Identify ALL blockers BEFORE implementation
2. **Phase 2:** Comma-Separated Declarations (4-6h) - Quick win, common GAMS pattern  
3. **Phase 3:** Targeted Feature Implementation (20-26h) - Only features required by complete blocker chains
4. **Phase 4:** Mid-Sprint Checkpoint (1-2h) - Day 5 validation to catch issues early
5. **Phase 5:** Synthetic Test Suite (3-4h) - Validate features work in isolation

**Sprint 10 Goal:** 100% parse rate (10/10 Tier 1 GAMSLIB models) through complete dependency analysis and targeted feature implementation.

**Current Status:**
- **Parse Rate:** 60% (6/10 models: mhw4d, rbrock, mathopt1, trig, hs62, mhw4dx)
- **Blocked Models:** circle (57%), himmel16 (79%), maxmin (40%), mingamma (54%)

**Reference:** See `docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md` for complete preparation task breakdown.

**Lessons from Sprint 9:**
- ✅ Known Unknowns process worked: 41 unknowns identified, all resolved proactively
- ❌ Blocker analysis incomplete: Only identified primary blockers, not secondary/tertiary
- ❌ Feature validation missing: Cannot test i++1 works due to himmel16.gms secondary blockers
- ❌ Impact validation delayed: Discovered 0% improvement on Day 10, should have checked Day 5

**Sprint 10 Improvement:** This document focuses on **dependency unknowns** (complete blocker chains) and **validation unknowns** (how to test features work), not just implementation unknowns.

---

## How to Use This Document

### Before Sprint 10 Day 1
1. Research and verify all **Critical** and **High** priority unknowns during prep phase
2. Create minimal test cases for validation (synthetic tests)
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE -> ✅ COMPLETE or ❌ WRONG (with correction)

### During Sprint 10
1. Review daily during standup (especially dependency unknowns)
2. Add newly discovered unknowns (e.g., tertiary blockers found during implementation)
3. Update with implementation findings
4. **Day 5 Checkpoint:** Validate assumptions about models unlocking

### Priority Definitions
- **Critical:** Wrong assumption will prevent models from unlocking or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework or delay (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues or scope adjustments (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 28  
**By Priority:**
- Critical: 8 (unknowns about complete blocker chains and model unlocking)
- High: 11 (unknowns requiring upfront research before implementation)
- Medium: 7 (unknowns that can be resolved during implementation)
- Low: 2 (nice-to-know, low impact)

**By Category:**
- Category 1: Comprehensive Dependency Analysis - 8 unknowns (critical blocker chains)
- Category 2: Comma-Separated Declarations - 3 unknowns
- Category 3: Function Calls in Parameters - 5 unknowns
- Category 4: Level Bound Conflict Resolution - 3 unknowns
- Category 5: Nested/Subset Indexing - 5 unknowns (highest risk)
- Category 6: abort$ in If-Blocks - 2 unknowns
- Category 7: Synthetic Test Suite - 2 unknowns

**Estimated Research Time:** 32-40 hours (distributed across prep tasks 2-11)

---

## Table of Contents

1. [Category 1: Comprehensive Dependency Analysis](#category-1-comprehensive-dependency-analysis)
2. [Category 2: Comma-Separated Declarations](#category-2-comma-separated-declarations)
3. [Category 3: Targeted Feature Implementation - Function Calls in Parameter Assignments](#category-3-targeted-feature-implementation---function-calls-in-parameter-assignments)
4. [Category 4: Targeted Feature Implementation - Level Bound Conflict Resolution](#category-4-targeted-feature-implementation---level-bound-conflict-resolution)
5. [Category 5: Targeted Feature Implementation - Nested/Subset Indexing in Domains](#category-5-targeted-feature-implementation---nestedsubset-indexing-in-domains)
6. [Category 6: Targeted Feature Implementation - abort$ in If-Block Bodies](#category-6-targeted-feature-implementation---abort-in-if-block-bodies)
7. [Category 7: Synthetic Test Suite](#category-7-synthetic-test-suite)
8. [Template: Adding New Unknowns](#template-adding-new-unknowns)
9. [Next Steps](#next-steps)
10. [Appendix: Task-to-Unknown Mapping](#appendix-task-to-unknown-mapping)

---

# Category 1: Comprehensive Dependency Analysis

**Sprint 9 Lesson:** Implementing primary blocker doesn't unlock model if secondary/tertiary blockers exist. Must identify COMPLETE blocker chain before implementation.

**Examples:**
- himmel16.gms: Primary blocker (i++1) fixed in Sprint 9, but model still fails due to secondary blocker (level bounds)
- mingamma.gms: Assumed equation attributes needed, but actual blocker is abort$ in if-blocks

**Sprint 10 Critical Need:** Document complete blocker chains (Primary → Secondary → Tertiary) for all 4 blocked models BEFORE any implementation.

---

## Unknown 10.1.1: circle.gms Complete Blocker Chain

### Priority
**Critical** - Wrong assumption = implement function calls but model still blocked

### Assumption
circle.gms primary blocker is function calls in parameter assignments (`uniform(1,10)`, `smin(i, x(i))`), and there are NO secondary blockers preventing parse after fixing this.

### Research Questions
1. After commenting out lines with function calls, does circle.gms parse?
2. Are there additional syntax errors in other lines?
3. What is complete line-by-line parse status for all 28 lines?
4. Are there semantic validation issues after parse succeeds?
5. Will implementing function calls actually unlock this model to 100% parse?

### How to Verify
```bash
# Test: Comment out function call lines and re-parse
cp tests/fixtures/gamslib/circle.gms /tmp/circle_test.gms
# Manually comment out line 40 (function call)
python -c "from src.ir.parser import parse_model_file; parse_model_file('/tmp/circle_test.gms')"
# If passes → only blocker
# If fails → secondary blocker exists
```

### Risk if Wrong
- **High:** Implement function calls (6-8 hours) but circle.gms still doesn't parse
- Model remains at 57% parse rate
- Sprint goal of 100% (10/10 models) not achieved

### Estimated Research Time
2 hours (Task 2: Analyze circle.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 2)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 2 - circle.gms Complete Blocker Chain Analysis

**Finding:** The assumption was PARTIALLY WRONG. circle.gms has THREE blockers in dependency chain, not zero secondary blockers.

**Complete Blocker Chain Identified:**

1. **PRIMARY BLOCKER (Lines 40-43):** Aggregation function calls
   - `smin(i, x(i))` and `smax(i, x(i))` in parameter assignments
   - Currently blocks at line 40 
   - Affects: 4 lines of parameter initialization
   - Parse rate if unfixed: 70% (39/56 lines)

2. **SECONDARY BLOCKER (Line 48):** Mathematical function calls  
   - `sqrt(sqr(a.l - xmin) + sqr(b.l - ymin))` in variable level assignment
   - Would block AFTER fixing primary blocker
   - Affects: 1 line of variable initialization
   - Parse rate after primary fix: 84% (47/56 lines)

3. **TERTIARY BLOCKER (Lines 54-56):** Conditional abort statement
   - Multi-line `if(..., abort "stop")` with compile-time variables
   - Would block AFTER fixing secondary blocker
   - Affects: 3 lines of execution control
   - Parse rate after secondary fix: 95% (53/56 lines)

**Evidence:**
- Comprehensive line-by-line analysis documented in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md`
- Parse attempt log at `/tmp/circle_parse_attempt.log` shows failure at line 40
- Manual inspection of all 56 lines identified blocker dependency chain
- Function calls already work in equation context (line 35: `sqr(x(i) - a)`), confirming implementation only needs extension to assignment context

**Decision/Outcome:**

**IMPLEMENT TOGETHER in Sprint 10:** Primary + Secondary blockers
- Combined feature: "Function call support in parameter/variable assignments"
- Revised effort: 6-10 hours (down from 10-14 due to existing function call logic in equations)
- Expected outcome: 95% parse success (53/56 lines)
- High ROI: Unlocks model structure, parameter initialization, and variable starting values

**DEFER to Sprint 11+:** Tertiary blocker (conditional abort)
- Low ROI: Only 5% of remaining file
- Edge case: Conditional abort with compile-time variables is uncommon pattern
- Can be addressed in future sprint without blocking Sprint 10 goals

**Impact on Sprint 10:**
- Moderate scope increase: Must handle both aggregation (smin/smax) and mathematical (sqrt/sqr) functions
- Significant complexity reduction: Function call AST nodes and parser logic already exist for equations
- Main task: Extend existing equation context logic to assignment context
- circle.gms will reach 95% parse after implementation (excellent progress toward 100% goal)

**Critical Insight:** Function calls already work in equation definitions (line 35 successfully parses `sqr(x(i) - a)`), which means function call infrastructure exists. Implementation effort is primarily about context extension, not building from scratch.

---

## Unknown 10.1.2: himmel16.gms Secondary Blocker Details

### Priority
**Critical** - i++1 already implemented but model still blocked

### Assumption
himmel16.gms secondary blocker is level bound conflicts (multiple `.l` assignments), and there are NO tertiary blockers after fixing this.

### Research Questions
1. What exactly causes "conflicting level bound" error? (which variables, which assignments)
2. Is this a parser error or semantic validation error?
3. After resolving level bound conflicts, does himmel16.gms parse to 100%?
4. Are there tertiary blockers after fixing level bounds?
5. Is the error in GAMS semantics (multiple `.l` invalid) or our parser validation?

### How to Verify
```bash
# Test: Remove duplicate .l assignments
grep -n "\.l\s*=" tests/fixtures/gamslib/himmel16.gms
# Modify to have only one .l per variable, re-parse
# If passes → only remaining blocker
# If fails → tertiary blocker exists
```

### Risk if Wrong
- **Critical:** Implement level bound resolution (2-3 hours) but himmel16.gms still doesn't parse
- Sprint 9 work (i++1 implementation) wasted if model never unlocks
- Model remains at 79% parse rate

### Estimated Research Time
2 hours (Task 3: Analyze himmel16.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 3)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 3 - himmel16.gms Complete Blocker Chain Analysis

**Finding:** The assumption was CORRECT. Level bound conflict is the ONLY remaining blocker, with NO tertiary blockers.

**Complete Blocker Chain:**

1. **PRIMARY BLOCKER (Lines ~47-50):** Lead/lag indexing (i++1, i--1)
   - Status: ✅ FIXED in Sprint 9
   - Evidence: Parser now successfully reaches line 63 (90% of file)
   - Sprint 8: Blocked at ~67% (line 47)
   - Sprint 9: Reaches 90% (line 63)

2. **SECONDARY BLOCKER (Line 63):** Variable bound index expansion bug
   - Currently blocks at line 63: `x.l("5") = 0`
   - Error: "Conflicting level bound for variable 'x' at indices ('1',)"
   - Parse rate: 90% (63/70 lines)

3. **TERTIARY BLOCKER:** NONE - Confirmed no additional blockers after line 63

**Root Cause Identified:**

This is a **PARSER BUG**, not a GAMS semantics issue or missing feature.

**Bug Description:** Parser's `_expand_variable_indices` function incorrectly expands literal string indices to ALL domain members instead of using only the specified literal.

**Example:**
```gams
x.fx("1") = 0  # Should affect ONLY index "1"
```

**Expected:** Sets fx_map for index "1" only  
**Actual:** Sets fx_map for ALL indices ("1", "2", "3", "4", "5", "6") ← BUG!

**Why Error Message Says Index '1':**
1. Line 57: `x.fx("1") = 0` → Bug sets fx_map AND l_map for ALL indices to 0
2. Lines 60-62: `x.l("2")`, `x.l("3")`, `x.l("4") = 0.5` → Bug sets l_map["1"] = 0.5
3. Line 63: `x.l("5") = 0` → Bug tries to set l_map["1"] = 0 → CONFLICT (0.5 vs 0)

The conflict IS at index "1", it just manifests when parsing line 63!

**Evidence:**
- Comprehensive line-by-line analysis of all 70 lines
- Parse attempt log at `/tmp/himmel16_parse_attempt.log`
- No additional syntax blockers after line 63
- Only `solve` statement remains (standard syntax)

**Decision/Outcome:**

**IMPLEMENT in Sprint 10:** Fix variable bound index expansion bug
- Location: `src/ir/parser.py`, function `_expand_variable_indices` (line 2125)
- Fix: Distinguish between set names (expand) and literal values (use as-is)
- Effort: 3-4 hours (localized bug fix)
- Complexity: LOW-MEDIUM (single function)
- Risk: LOW (isolated change with clear test case)
- Expected result: himmel16.gms from 90% → 100%

**Impact on Sprint 10:**
- This is a bug fix, not a new feature implementation
- High confidence fix (95%+) based on clear root cause analysis
- himmel16.gms will unlock completely after fix
- Fix likely benefits other models with mixed bound types (.fx + .l)

**GAMS Semantics Verified:**
- Having `.fx("1") = 0` and `.l("2") = 0.5` is VALID in GAMS (different indices)
- Multiple `.l` assignments on different indices is VALID
- Parser currently incorrectly rejects this valid GAMS code

**Model Unlock Prediction:** himmel16.gms will reach 100% parse (70/70 lines) after fixing the bound index expansion bug.

---

## Unknown 10.1.3: maxmin.gms Nested Indexing Scope

### Priority
**Critical** - Highest complexity feature (10-12 hours), go/no-go decision

### Assumption
maxmin.gms primary and only blocker is nested/subset indexing (`defdist(low(n,nn))..`), with no secondary blockers.

### Research Questions
1. After handling nested indexing, does maxmin.gms parse to 100%?
2. Are there other syntax issues in the remaining 27 lines (currently 19/47 parse)?
3. How many lines are blocked by nested indexing vs other issues?
4. Is nested indexing the ONLY blocker preventing 40% → 100% parse?
5. If we defer nested indexing, can we still achieve 90% (9/10 models)?

### How to Verify
```bash
# Test: Comment out all nested indexing lines
grep -n "low(n,nn)" tests/fixtures/gamslib/maxmin.gms
# Comment those lines, re-parse
# Check parse rate on remaining lines
# If high → nested indexing is main blocker
# If low → other blockers exist
```

### Risk if Wrong
- **Critical:** Spend 10-12 hours on nested indexing but maxmin.gms still doesn't parse (secondary blockers)
- OR: Defer nested indexing but discover other quick fixes could unlock model
- Wrong decision = wasted sprint effort or missed opportunity

### Estimated Research Time
2-3 hours (Task 4: Analyze maxmin.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 4)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 4 - maxmin.gms Blocker Chain Analysis  
**Time Spent:** 2.5 hours

**Finding:** Assumption was PARTIALLY WRONG - nested indexing is primary blocker, but there are MULTIPLE secondary/tertiary blockers.

**Complete Blocker Chain:**
1. **PRIMARY BLOCKER (3 lines):** Subset/nested indexing in equation domains
   - Lines 51, 53, 55: `defdist(low(n,nn))..`, `mindist1(low)..`, `mindist1a(low(n,nn))..`
   - Error: "No terminal matches '(' in the current parser context, at line 51 col 12"
   - Grammar limitation: `id_list: ID ("," ID)*` only supports simple identifiers

2. **SECONDARY BLOCKER (2 lines):** Aggregation functions in equation domains
   - Lines 57, 59: `smin(low, dist(low))` and `smin(low(n,nn), sqrt(...))`
   - Same blocker as circle.gms (will be fixed by Sprint 10 function call implementation)

3. **TERTIARY BLOCKER (5 lines):** Multi-model declaration syntax
   - Lines 61-65: Multi-line model block with 4 models in one statement
   - Current grammar only supports single model per statement

4. **QUATERNARY BLOCKER (4 lines):** Loop with tuple domain
   - Lines 70-73: `loop((n,d), ...);` - nested parentheses for tuple iteration

5. **RELATED BLOCKERS (9 lines):** Lower priority features
   - Line 37: Set assignment with `ord()` functions
   - Line 78: Variable bounds with subset indexing
   - Line 83: Function calls in parameter assignments (max, ceil, sqrt, card)
   - Line 87: Conditional option statement `if(card(n) > 9, option ...)`
   - Line 106: DNLP solver (grammar only supports NLP)

**Total Blocker Lines:** 23 lines (19 parse blockers + 4 semantic blockers)

**Progressive Parse Rates:**
- **Current:** 18% (19/108 lines) - Fails at line 51 (nested indexing)
- **After Primary fix:** ~51% (55/108 lines) - Would fail at line 57 (aggregation functions)
- **After Primary + Secondary:** ~57% (61/108 lines) - Would fail at line 61 (multi-model)
- **After Primary + Secondary + Tertiary:** ~65% (70/108 lines) - Would fail at line 70 (loop tuple)
- **After ALL parse blockers:** 79% (85/108 lines) - Remaining are semantic issues

**Answer to Research Questions:**
1. **Does maxmin.gms parse to 100% after nested indexing?** NO - Only reaches ~51% (55/108 lines)
2. **Are there other syntax issues?** YES - 4 additional blocker categories (20 lines)
3. **How many lines blocked?** 23 total (3 primary, 20 secondary+)
4. **Is nested indexing the ONLY blocker?** NO - It's the first blocker, but 4 more categories exist
5. **Can we achieve 90% (9/10) if we defer?** YES - circle.gms + himmel16.gms = 9/10 models

**Impact:** Original assumption that "nested indexing is primary AND ONLY blocker" was WRONG. There are 4 additional blocker categories beyond nested indexing. This strengthens the case for DEFERRING maxmin.gms to Sprint 11+.

**Complexity Assessment:** Nested indexing alone is 10-14 hours. Full maxmin.gms support requires 23-40 hours total (all 5 blocker categories).

**Sprint 10 Decision:** DEFER maxmin.gms entirely. Target 90% (9/10 models) by fixing circle.gms + himmel16.gms.

**Documentation:** Complete analysis in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` (750 lines)

---

## Unknown 10.1.4: mingamma.gms Correct Primary Blocker

### Priority
**High** - Sprint 9 assumed equation attributes, was wrong

### Assumption
mingamma.gms primary and only blocker is abort$ in if-block bodies, NOT equation attributes as Sprint 9 assumed.

### Research Questions
1. Does mingamma.gms actually use equation attributes (`.l`, `.m` on equations)?
2. After fixing abort$ in if-blocks, does mingamma.gms parse to 100%?
3. Are there other blockers beyond abort$?
4. Why did Sprint 9 assume equation attributes? (lesson for blocker analysis)
5. How many abort$ statements exist and where?

### How to Verify
```bash
# Check for equation attributes in mingamma.gms
grep -E "eq.*\.l|eq.*\.m" tests/fixtures/gamslib/mingamma.gms
# If none found → Sprint 9 assumption was wrong

# Test: Comment out abort$ statements
grep -n "abort" tests/fixtures/gamslib/mingamma.gms
# Comment those lines, re-parse
# If passes → only blocker
```

### Risk if Wrong
- **Medium:** Sprint 9 implemented equation attributes unnecessarily (wasn't needed for mingamma)
- Implement abort$ (2-3 hours) but model still doesn't parse (other blockers)
- Lesson: always verify assumptions with grep before implementing

### Estimated Research Time
1-2 hours (Task 5: Analyze mingamma.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 5)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 5 - mingamma.gms Blocker Chain Analysis  
**Time Spent:** 1.5 hours

**Finding:** Sprint 9 assumption was COMPLETELY WRONG on multiple fronts.

**Complete Analysis:**

1. **Does mingamma.gms use equation attributes?** NO
   - Verified with: `grep -E "y1def\.|y2def\." tests/fixtures/gamslib/mingamma.gms`
   - Result: No equation attribute access found
   - Only variable attributes used: x1.l, x2.l, y1.l, y2.l, x1.lo, x2.lo

2. **After fixing abort$ in if-blocks, does mingamma parse to 100%?** NO
   - abort$ in if-blocks WAS fixed in Sprint 9 (lines 59, 62 now parse)
   - But NEW blocker discovered: Comma-separated scalar declarations with inline values
   - File fails at line 41 (65% parse rate)

3. **Are there other blockers beyond abort$?** YES
   - **NEW PRIMARY BLOCKER:** Comma-separated scalar declarations with mixed inline values (lines 30-38)
   - Pattern: `Scalar x1opt /1.46/, x1delta, y1opt /0.88/, y1delta;`
   - Grammar doesn't support mixing scalars with and without inline values
   - This blocker was hidden because it causes semantic error (undefined symbol)

4. **Why did Sprint 9 assume equation attributes?**
   - Incorrect assumption based on insufficient analysis
   - Did NOT verify with grep before implementing
   - Confused variable attributes (.l on variables) with equation attributes (.l on equations)
   - Lesson: ALWAYS verify assumptions with code search before implementing

5. **How many abort$ statements and where?**
   - 2 abort$ statements: lines 59 and 62
   - Both inside if-block bodies
   - Syntax: `abort$[condition] "message";` (uses square brackets)
   - Status: ✅ FIXED in Sprint 9

**Complete Blocker Chain:**
- **PRIMARY (Sprint 9):** abort$ in if-blocks - ✅ FIXED
- **SECONDARY (NEW):** Comma-separated scalar declarations with inline values - TO FIX in Sprint 10
- **TERTIARY:** None

**Sprint 9 Lessons Learned:**

1. **Verification Failure:**
   - Assumed equation attributes needed WITHOUT verifying with grep
   - Simple `grep -E "eq.*\.l|eq.*\.m"` would have shown no usage
   - Wasted implementation effort on unnecessary feature

2. **Incomplete Blocker Analysis:**
   - Sprint 9 analysis stopped at first blocker (abort$)
   - Didn't discover secondary blocker (comma-separated scalars)
   - Should have tested with blocker commented out to find secondary blockers

3. **Hidden Semantic Blockers:**
   - Comma-separated scalar blocker causes SEMANTIC error (undefined symbol)
   - Not immediately obvious as parse blocker
   - Requires deeper analysis to discover

**Impact:**
- Equation attributes: Implemented but NOT needed for mingamma.gms (wasted effort)
- abort$ in if-blocks: ✅ Correctly implemented (was actual blocker)
- Comma-separated scalars: Discovered in Task 5 (would have been Sprint 10 surprise)

**Actual Blocker for Sprint 10:**
- Comma-separated scalar declarations with inline values
- Effort: 4-6 hours (LOW-MEDIUM complexity)
- Expected outcome: mingamma.gms from 65% → 100%

**Documentation:** Complete analysis in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` (1604 lines)

---

## Unknown 10.1.5: Secondary Blocker Detection Method

### Priority
**High** - Process improvement for future sprints

### Assumption
Commenting out primary blocker lines and re-parsing is sufficient to discover secondary blockers.

### Research Questions
1. Does this method reliably find all secondary blockers?
2. Are there cases where secondary blockers only appear after primary is fixed (not visible by commenting)?
3. Should we implement primary blocker in isolation first, then re-analyze?
4. What is best practice for complete blocker chain analysis?
5. How do we know when we've found ALL blockers (not just first 2-3)?

### How to Verify
- Apply method to all 4 blocked models (Tasks 2-5)
- Compare findings to actual implementation results
- Document any tertiary blockers discovered during implementation (should be zero if method works)

### Risk if Wrong
- **Medium:** Miss tertiary blockers during prep, discover during implementation
- Repeat Sprint 9 issue (features complete but models still blocked)

### Estimated Research Time
Ongoing during Tasks 2-5 (no dedicated time, part of methodology validation)

### Owner
Development team (Prep Tasks 2-5)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be validated through Tasks 2-5 execution

---

## Unknown 10.1.6: Parse Rate Percentage Calculation Accuracy

### Priority
**Low** - Affects metrics but not functionality

### Assumption
Current parse rate percentage calculations (57% for circle, 79% for himmel16, etc.) accurately reflect progress and will increase after fixing blockers.

### Research Questions
1. How are parse percentages calculated? (lines parsed / total lines?)
2. Do percentages include comments and blank lines?
3. Will fixing primary blocker predictably increase percentage?
4. Are percentages useful for estimating how "close" we are to full parse?
5. Should we track statement-level parse (declarations, equations) instead of lines?

### How to Verify
```bash
# Check parse percentage calculation in dashboard
python scripts/dashboard.py
# Verify calculation methodology
# Test: Fix one blocker, re-measure, check if percentage increases as expected
```

### Risk if Wrong
- **Low:** Metrics misleading but doesn't affect actual functionality
- May over/under-estimate progress

### Estimated Research Time
Minimal (check during blocker analysis, no dedicated time)

### Owner
Development team

### Verification Results
🔍 **Status: INCOMPLETE**  
Low priority, validate during Tasks 2-5 if time permits

---

## Unknown 10.1.7: Blocker Interaction Effects

### Priority
**Medium** - Could affect implementation order

### Assumption
Blockers are independent - fixing one doesn't change/reveal others (except cascading discovery of secondary after primary).

### Research Questions
1. Can fixing blocker A inadvertently fix blocker B? (positive interaction)
2. Can fixing blocker A make blocker B worse or create blocker C? (negative interaction)
3. Is there an optimal order to fix blockers?
4. Do any blockers have dependencies on each other?
5. Should we fix all primary blockers before any secondary, or model-by-model?

### How to Verify
- Document blocker chains for all 4 models (Tasks 2-5)
- Look for common patterns or interactions
- Consider: Does fixing function calls in circle help with other models?

### Risk if Wrong
- **Medium:** Implement features in suboptimal order
- May discover unexpected interactions during implementation

### Estimated Research Time
1 hour (part of Tasks 2-5 analysis)

### Owner
Development team (Prep Tasks 2-5)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be analyzed during Tasks 2-5

---

## Unknown 10.1.8: Semantic Validation vs Parse Errors

### Priority
**Medium** - Affects how we categorize and fix issues

### Assumption
Most remaining blockers are parse errors (grammar/syntax), not semantic validation errors (conflicting constraints, type mismatches).

### Research Questions
1. Which blockers are parse errors (parser can't process syntax)?
2. Which blockers are semantic errors (parser succeeds but validation fails)?
3. Should semantic errors be fixed in parser or post-parse validation?
4. Is "conflicting level bound" a parse error or semantic error?
5. How do we test each type of fix?

### How to Verify
```bash
# For each blocker, determine error source:
# - Parse error: raised during parse_model_file()
# - Semantic error: raised after parse succeeds, during validation
# Check error stack traces and error messages
```

### Risk if Wrong
- **Medium:** Implement fix in wrong layer (parser vs validator)
- May create technical debt or incorrect architecture

### Estimated Research Time
1 hour (part of Tasks 2-5 error analysis)

### Owner
Development team (Prep Tasks 2-5)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be determined during Tasks 2-5

---

# Category 2: Comma-Separated Declarations

**Sprint 10 Phase 2:** Quick win (4-6 hours) - common GAMS pattern, low risk.

**Goal:** Support `Variable x1, x2, x3;` instead of requiring separate lines.

---

## Unknown 10.2.1: Comma-Separated Pattern Frequency

### Priority
**Medium** - Affects benefit/cost ratio

### Assumption
Comma-separated declarations are common in GAMS code and supporting this improves real-world compatibility significantly.

### Research Questions
1. How many GAMSLIB models use comma-separated declarations?
2. What percentage of GAMS code uses this pattern?
3. Does any blocked model need this to parse? (unlikely but verify)
4. Is this quick win worth 4-6 hours of effort?
5. Which declaration types use commas most? (Variable, Parameter, Equation, Set)

### How to Verify
```bash
# Survey GAMSLIB for pattern frequency
grep -r "^[[:space:]]*Variable.*," tests/fixtures/gamslib/ | wc -l
grep -r "^[[:space:]]*Parameter.*," tests/fixtures/gamslib/ | wc -l
grep -r "^[[:space:]]*Equation.*," tests/fixtures/gamslib/ | wc -l

# Check if any blocked model needs this
grep "Variable.*," tests/fixtures/gamslib/{circle,himmel16,maxmin,mingamma}.gms
```

### Risk if Wrong
- **Low:** Implement feature that's rarely used (low benefit)
- OR: Skip feature that would improve compatibility (missed opportunity)

### Estimated Research Time
2 hours (Task 6: Research Comma-Separated Declaration Patterns)

### Owner
Development team (Prep Task 6)

### Verification Results
✅ **Status: VERIFIED** (Task 6 completed 2025-11-23)

**Finding:** Comma-separated declarations are **EXTREMELY COMMON** (80% of models), MUCH MORE than assumed 40-50%.

**Complete Analysis:**
1. **How many models use this pattern?** → **8/10 models (80%)**
   - Variable: 7/10 models (70%)
   - Equation: 6/10 models (60%)
   - Parameter: 1/10 models (10%)
   - Scalar: 2/10 models (20%)
   - Set: 0/10 models (0%)

2. **Total instances found:** 16 instances across 10 models
   - Average: 1.6 comma-separated declarations per model

3. **Does any blocked model need this?** → **YES - mingamma.gms**
   - mingamma.gms uses Scalar comma-separated with inline values (lines 30-38)
   - This is the SECONDARY blocker discovered in Task 5
   - Variable comma-separated used in: mingamma (line 13), rbrock (line 13), trig (line 15)

4. **Is this quick win worth 4-6 hours?** → **YES - HIGH ROI**
   - Affects 80% of models (fundamental GAMS pattern, not edge case)
   - Unlocks mingamma.gms to 100% parse (currently 65%)
   - Simplifies 7 other models that already parse

5. **Which types use commas most?** → **Variable and Equation (60% each)**

**Impact:** This is a **HIGH-PRIORITY** feature, not optional. Affects majority of models.

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` Section 1
**Reference:** `docs/planning/EPIC_2/SPRINT_10/comma_separated_examples.txt`

---

## Unknown 10.2.2: Comma-Separated with Attributes

### Priority
**High** - Affects grammar complexity

### Assumption
Comma-separated declarations are simple lists without per-item attributes: `Variable x, y, z;` not `Variable x /lo 0/, y, z /up 10/;`

### Research Questions
1. Can attributes be specified per item in comma-separated list?
2. Does GAMS support mixed attributes: `Positive Variable x, y; Free Variable z;` on one line?
3. What is exact grammar for comma-separated declarations?
4. Are there edge cases (trailing commas, empty items)?
5. How complex is the implementation (simple list vs attribute handling)?

### How to Verify
```bash
# Survey GAMSLIB for pattern variations
grep -r "Variable.*,.*/" tests/fixtures/gamslib/  # Attributes in comma list
grep -r "Variable.*,.*," tests/fixtures/gamslib/ | head -20  # Multiple commas

# Check GAMS documentation for syntax specification
```

### Risk if Wrong
- **High:** Implement simple comma list but real GAMS uses attributes
- Grammar becomes more complex than 4-6 hour estimate
- OR: Over-engineer for attributes that aren't used

### Estimated Research Time
2 hours (Task 6: Research Comma-Separated Declaration Patterns)

### Owner
Development team (Prep Task 6)

### Verification Results
✅ **Status: VERIFIED** (Task 6 completed 2025-11-23)

**Finding:** GAMS officially supports mixing inline values with plain declarations. **This is VALID GAMS syntax.**

**Complete Analysis:**
1. **Can attributes be specified per item?** → **NO per-item attributes**
   - Type modifiers (Positive, Negative) apply to ALL items: `Positive Variable x, y, z;`
   - NO per-item bounds found: `Variable x /lo 0/, y;` NOT used in GAMSLib
   - Scalar inline values ARE supported: `Scalar x1 /5.0/, x2;` (different from bounds)

2. **Does GAMS support mixed attributes?** → **NO mixed types on one line**
   - `Positive Variable x, y; Free Variable z;` NOT valid (separate statements required)
   - Type modifier applies uniformly to all items in comma-separated list

3. **Exact grammar for comma-separated declarations:**
   - Variable: `[var_type] variable[s] var_name [text] {, var_name [text]}`
   - Scalar: `scalar[s] scalar_name [text] [/value/] {, scalar_name [text] [/value/]}`
   - **KEY:** Scalar inline values `/value/` are OPTIONAL PER ITEM

4. **Edge cases found:** → **NONE in GAMSLib**
   - NO trailing commas in any model
   - NO inline comments within comma lists
   - Consistent whitespace handling (all use standard spacing)

5. **Implementation complexity:** → **SIMPLE for most, MEDIUM for Scalar**
   - Variable, Parameter, Equation: ✅ ALREADY SUPPORTED via `id_list` rule
   - Scalar: ❌ NEEDS FIX - `scalar_list` doesn't support inline values

**GAMS Documentation Evidence:**
```gams
Scalar
    rho  "discount rate"                           / .15 /
    irr  "internal rate of return"
    life "financial lifetime of productive units"  / 20  /;
```
This official example shows `rho` and `life` with inline values, `irr` without - ALL IN ONE STATEMENT.

**Impact:** Parser MUST support Scalar inline value mixing (mingamma.gms blocker).

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` Section 3
**Source:** https://www.gams.com/latest/docs/UG_DataEntry.html

---

## Unknown 10.2.3: Grammar Production Changes Scope

### Priority
**Medium** - Affects implementation time estimate

### Assumption
Grammar changes for comma-separated declarations are straightforward (change NAME to NAME ("," NAME)*) and can be done in 4-6 hours including tests.

### Research Questions
1. Which grammar rules need changes? (variable_declaration, parameter_declaration, equation_declaration)
2. Are AST changes required or just grammar?
3. How many test cases needed for coverage?
4. Do comma-separated declarations interact with other parser features?
5. Is 4-6 hour estimate realistic based on grammar complexity?

### How to Verify
- Review current grammar in `src/gams/gams_grammar.lark`
- Identify exact rules to change
- Estimate work: grammar changes + AST + tests
- Compare to actual effort in Sprint 10

### Risk if Wrong
- **Medium:** Underestimate complexity, takes 8-10 hours instead of 4-6
- Delays other features

### Estimated Research Time
Included in Task 6 (2 hours total includes this analysis)

### Owner
Development team (Prep Task 6)

### Verification Results
✅ **Status: VERIFIED** (Task 6 completed 2025-11-23)

**Finding:** Assumption was WRONG. Only Scalar needs grammar changes (NOT 4 types). Grammar work is 0.5-1.0h (NOT 2-3h).

**Complete Analysis:**
1. **Which grammar rules need changes?** → **ONLY Scalar declarations**
   - Variable: ✅ ALREADY SUPPORTS comma-separated (via `var_list` with `id_list`)
   - Parameter: ✅ ALREADY SUPPORTS comma-separated (via `param_list`)
   - Equation: ✅ ALREADY SUPPORTS comma-separated (via `eqn_head_list`)
   - Scalar: ❌ NEEDS FIX - `scalar_list` rule doesn't support inline values

2. **Are AST changes required?** → **NO - IR already handles scalars**
   - Need to add `scalar_item` rule (2 alternatives)
   - Modify `scalar_list` to use `scalar_item ("," scalar_item)*`
   - No new AST nodes required

3. **How many test cases needed?** → **7 test suites (comprehensive coverage)**
   - Simple comma-separated (no inline values)
   - All with inline values
   - Mixed inline values (mingamma.gms pattern)
   - Single scalar with value
   - Negative values
   - Scientific notation
   - With description text

4. **Do comma-separated declarations interact with other features?** → **NO**
   - Grammar changes are localized to Scalar declarations
   - No dependencies on other parser features
   - Backward compatible (existing tests unaffected)

5. **Is 4-6 hour estimate realistic?** → **YES - validated breakdown:**
   - Grammar changes: 0.5-1.0h (NOT 2-3h - only Scalar needs work)
   - Semantic handler: 2.0-2.5h
   - Test coverage: 1.5-2.0h
   - **Total: 4.0-5.5 hours** ✅

**Grammar Changes Required:**
```lark
scalar_decl: ID desc_text "/" scalar_data_items "/" (ASSIGN expr)?      -> scalar_with_data
           | ID desc_text ASSIGN expr                                   -> scalar_with_assign
           | scalar_item ("," scalar_item)*                             -> scalar_list
           | ID desc_text                                               -> scalar_plain

scalar_item: ID desc_text "/" scalar_data_items "/"                     -> scalar_item_with_data
           | ID desc_text                                               -> scalar_item_plain
```

**Impact:** Implementation is SIMPLER than expected. Most work is semantic handling (2-2.5h), not grammar (0.5-1h).

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/comma_separated_research.md` Sections 4-6

---

# Category 3: Targeted Feature Implementation - Function Calls in Parameter Assignments

**Unlocks:** circle.gms (57% → 100%)  
**Effort:** 6-8 hours (Medium risk)  
**Blocker:** `p = uniform(1,10)`, `xmin = smin(i, x(i))`

---

## Unknown 10.3.1: Function Call Evaluation Strategy

### Priority
**Critical** - Affects implementation approach and effort

### Assumption
We only need to PARSE function call syntax in parameter assignments, not EVALUATE them. GAMS compiler handles evaluation later.

### Research Questions
1. Does parser need to evaluate function calls or just store as AST?
2. What does current IR store for parameters? (values or expressions?)
3. Can we defer evaluation to GAMS compile/runtime?
4. Which functions appear in GAMSLIB parameter assignments?
5. Do any functions require special handling (e.g., random number generation)?

### How to Verify
```bash
# Check current IR parameter handling
grep -A10 "class.*Parameter" src/ir/ast.py
# Does it store expressions or just values?

# Survey functions in GAMSLIB
grep -rn "=\s*\w\+(" tests/fixtures/gamslib/*.gms | grep -E "(uniform|normal|smin|smax)" | head -20
```

### Risk if Wrong
- **Critical:** Implement parse-only but GAMS needs evaluation (major refactoring)
- OR: Implement evaluation when parse-only sufficient (wasted effort 2-4 hours)

### Estimated Research Time
2-3 hours (Task 7: Survey Existing GAMS Function Call Syntax)

### Owner
Development team (Prep Task 7)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 7 - GAMS Function Call Syntax Research

**Finding:** The assumption was CORRECT. Parse-only strategy is the right approach.

**Complete Analysis:**

1. **Does parser need to evaluate function calls?** → **NO**
   - Equations store expressions as AST (not evaluated)
   - Parameters can follow same pattern
   - Evaluation deferred to GAMS runtime
   - Our scope: Parse → IR conversion only

2. **What does current IR store for parameters?** → **Values (float)**
   - Current: `ParameterDef.values: dict[tuple[str, ...], float]`
   - Limitation: Cannot store expressions
   - Solution: Add `expressions: dict[tuple[str, ...], Expr]` field

3. **Can we defer evaluation to GAMS?** → **YES**
   - GAMS evaluates expressions at compile/runtime
   - Consistent with equation handling (also stores expressions)
   - No evaluation engine needed in parser

4. **Which functions appear in GAMSLIB parameter assignments?** → **19 unique functions**
   - Mathematical (10): sqr, sqrt, power, log, abs, round, mod, ceil, max, min
   - Aggregation (4): smin, smax, sum, max
   - Trigonometric (2): sin, cos
   - Statistical (1): uniform
   - Special (2): gamma, loggamma
   - Set (2): ord, card

5. **Do functions require special handling?** → **uniform and aggregation functions require runtime evaluation**
   - `uniform(1,10)`: Non-deterministic (runtime only)
   - `smin(i, x(i))`: Requires set iteration (runtime)
   - `sqrt(2)`: Could evaluate but unnecessary

**Implementation Decision: Option C (Store all as expressions)**
- Add `expressions` field to ParameterDef
- Store all function calls as Call AST nodes
- No evaluation engine needed
- Effort: 2.5-3 hours (not original 6-8 hours)

**Impact:** Major effort reduction from 6-8 hours to 2.5-3 hours (62-71% reduction) due to parse-only approach.

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` Section 6, 9.1

---

## Unknown 10.3.2: Function Call Nesting Depth

### Priority
**High** - Affects grammar complexity

### Assumption
Function calls in parameters are mostly flat (`uniform(1,10)`) or single-level nested (`smin(i, x(i))`), not deeply nested.

### Research Questions
1. What is maximum nesting depth in GAMSLIB? (`f(g(h(x)))`?)
2. Does grammar need to support arbitrary nesting?
3. How common are nested function calls?
4. Can we start with flat functions and add nesting later if needed?
5. Does nesting affect AST node structure significantly?

### How to Verify
```bash
# Find nested function calls
grep -rn "=\s*\w\+(\w\+(" tests/fixtures/gamslib/ | head -20
# Count nesting levels in examples

# Specific check in circle.gms
grep "=" tests/fixtures/gamslib/circle.gms | grep "("
```

### Risk if Wrong
- **High:** Implement flat functions but GAMS uses nesting (incomplete feature)
- Grammar needs revision during sprint

### Estimated Research Time
Included in Task 7 (2-3 hours total includes nesting analysis)

### Owner
Development team (Prep Task 7)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 7 - GAMS Function Call Syntax Research

**Finding:** The assumption was PARTIALLY WRONG. Functions are NOT "mostly flat or single-level nested" - nesting can reach up to 5 levels.

**Complete Analysis:**

1. **Maximum nesting depth in GAMSLIB?** → **5 levels (not 1-2)**
   - Example: `1/max(ceil(sqrt(card(n)))-1,1)` (maxmin.gms:83)
   - Nesting breakdown: Division → max → ceil → sqrt → card
   - Original assumption underestimated maximum depth

2. **Does grammar need to support arbitrary nesting?** → **YES, but already supported ✅**
   - Grammar ALREADY supports arbitrary nesting through recursion
   - `atom → func_call`, `func_call → arg_list`, `arg_list → expr`, `expr → atom`
   - Recursive grammar handles any depth automatically
   - No implementation work needed

3. **How common are nested function calls?** → **89% are depth ≤2, but 11% go deeper**
   - Nesting depth distribution:
     - Depth 1 (no nesting): 67% (~60 occurrences)
     - Depth 2: 22% (~20 occurrences)
     - Depth 3: 9% (~8 occurrences)
     - Depth 4: 1% (~1 occurrence)
     - Depth 5: 1% (~1 occurrence)
   - While uncommon, deep nesting DOES exist and must be supported

4. **Can we start with flat functions and add nesting later?** → **NO NEED**
   - Grammar already handles all depths ✅
   - Infrastructure complete (no incremental approach needed)
   - Nesting "just works" with existing expression grammar

5. **Does nesting affect AST node structure significantly?** → **YES, but handled automatically**
   - Nested Call nodes: `Call("sqrt", (Call("sqr", (VarRef("x1"),)),))`
   - Call.children() method provides AST traversal
   - No special implementation required beyond existing Call node

**Common Nesting Patterns Found:**
- `sqrt(sqr(...) + sqr(...))` - Euclidean distance (8 occurrences)
- `smin(subset, sqrt(sum(...)))` - Aggregation with nested math (5 occurrences)
- `sqr(sqr(x1) - x2)` - Nested mathematical operations (3 occurrences)

**Impact:** While assumption about typical depth was wrong, no additional work needed since grammar already supports arbitrary nesting through recursion.

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` Sections 4, 5.3, 9.2

---

## Unknown 10.3.3: Function Name Validation

### Priority
**Medium** - Affects error handling

### Assumption
Any identifier followed by `()` is valid function call syntax; we don't validate function names during parsing.

### Research Questions
1. Should parser validate function names against known GAMS functions?
2. Does GAMS allow user-defined functions in parameter assignments?
3. How do we handle unknown function names? (parse anyway or error?)
4. Is there a definitive list of valid GAMS functions?
5. Should validation happen at parse time or later?

### How to Verify
- Check GAMS documentation for function list
- Test with invalid function name: `p = invalidfunc(1,2);`
- See how GAMS handles it (parse vs compile error)

### Risk if Wrong
- **Low:** Allow invalid functions (GAMS compiler will catch later)
- OR: Too strict validation (reject valid user functions)

### Estimated Research Time
Included in Task 7 (part of function survey)

### Owner
Development team (Prep Task 7)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 7 - GAMS Function Call Syntax Research

**Finding:** The assumption was CORRECT. Function categories have been identified and don't require different parsing approaches.

**Complete Analysis:**

1. **Should parser validate function names against known GAMS functions?** → **NO - Parse any identifier**
   - Parse-only approach: Accept any `IDENTIFIER(args)` syntax
   - GAMS compiler validates function names later
   - Keeps parser simple and flexible

2. **Does GAMS allow user-defined functions?** → **NOT in parameter assignments (GAMSLIB context)**
   - All 19 functions found are built-in GAMS functions
   - No user-defined function calls in parameter context
   - GAMS does support extrinsic functions but not in this context

3. **How to handle unknown function names?** → **Parse anyway, defer validation**
   - Grammar accepts any identifier in FUNCNAME pattern
   - Creates Call AST node regardless
   - GAMS runtime reports error if function invalid
   - Consistent with parse-only philosophy

4. **Is there definitive list of valid GAMS functions?** → **YES - 19 functions cataloged**
   - **6 categories identified:**
     - Mathematical (10): sqr, sqrt, power, log, abs, round, mod, ceil, max, min
     - Aggregation (4): smin, smax, sum, max
     - Trigonometric (2): sin, cos
     - Statistical (1): uniform
     - Special (2): gamma, loggamma
     - Set (2): ord, card
   - **Current FUNCNAME token:** Has 18/21 functions (86% coverage)
   - **Missing from token:** round, mod, ceil (need to add)

5. **Should validation happen at parse time or later?** → **LATER (GAMS runtime)**
   - Parse time: Syntax checking only (identifier + parentheses + args)
   - Compile time: Symbol resolution (GAMS)
   - Runtime: Function evaluation (GAMS)
   - Separation of concerns: Parser handles syntax, GAMS handles semantics

**Categories and Parsing:**
- **Do categories need different handling?** → **NO for parse-only**
  - All use same syntax: `func_name(arg1, arg2, ...)`
  - All stored as `Call(func_name, args)` AST node
  - Category only matters for GAMS evaluation (not our scope)
  - Uniform parsing across all categories

**Implementation Impact:**
- Add 3 missing functions (round, mod, ceil) to FUNCNAME token: 5 minutes
- No category-specific parsing logic needed
- No runtime validation needed
- Simple, uniform implementation

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` Sections 2, 5.1, 9.3

---

## Unknown 10.3.4: Function Argument Types

### Priority
**Medium** - Affects AST design

### Assumption
Function arguments can be constants, variables, or expressions: `smin(i, x(i))` where `i` is set, `x(i)` is variable reference.

### Research Questions
1. What argument types are valid? (constants, variables, indices, expressions)
2. Do we parse arguments as general expressions or specific types?
3. How do we handle set references like `i` in `smin(i, x(i))`?
4. Does AST need special nodes for set arguments vs value arguments?
5. Can arguments be other function calls (nested)?

### How to Verify
```bash
# Survey function argument patterns in GAMSLIB
grep -rn "smin\|smax\|sum" tests/fixtures/gamslib/*.gms | head -20
# Analyze argument structures

# Check circle.gms specifically
grep "smin\|smax" tests/fixtures/gamslib/circle.gms
```

### Risk if Wrong
- **Medium:** AST design inadequate for argument types (refactoring needed)

### Estimated Research Time
Included in Task 7 (part of function call analysis)

### Owner
Development team (Prep Task 7)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 7 - GAMS Function Call Syntax Research

**Finding:** The assumption was CORRECT. Function call infrastructure ALREADY EXISTS - no grammar production changes needed.

**Complete Analysis:**

1. **What argument types are valid?** → **Constants, variables, indices, expressions (ALL)**
   - **Level 1:** Constants: `uniform(1,10)`, `sqrt(2)`
   - **Level 2:** Simple variables: `sqr(x1)`, `log(y1opt)`
   - **Level 3:** Indexed variables: `sqr(x(i))`, `smin(i, x(i))`
   - **Level 4:** Arithmetic expressions: `sqr(x1-1)`, `log((x1+x2+x3+0.03)/(...))`
   - **Level 5:** Nested function calls: `sqrt(sqr(...) + sqr(...))`

2. **Do we parse arguments as general expressions or specific types?** → **General expressions ✅**
   - Grammar: `arg_list: expr ("," expr)*`
   - Each argument is full expression (supports nesting, operations, etc.)
   - No special-case argument types
   - Maximum flexibility

3. **How to handle set references like `i` in `smin(i, x(i))`?** → **Already handled as symbols**
   - Set identifier `i` parsed as symbol reference
   - Expression grammar includes `symbol_plain` alternative
   - No special AST node needed
   - Works with existing infrastructure

4. **Does AST need special nodes for set arguments vs value arguments?** → **NO ✅**
   - All arguments stored as `Expr` in `Call.args: tuple[Expr, ...]`
   - Set reference is just `SymbolRef("i")` (existing node)
   - Variable reference is `VarRef("x", ("i",))` (existing node)
   - Call AST node handles all uniformly

5. **Can arguments be other function calls (nested)?** → **YES, already supported ✅**
   - Example: `sqrt(sqr(a.l - xmin) + sqr(b.l - ymin))`
   - Inner `sqr` calls are arguments to outer `sqrt`
   - Grammar recursion handles this: `expr → atom → func_call → arg_list → expr`
   - No special implementation needed

**CRITICAL DISCOVERY:**

**Grammar Infrastructure EXISTS:**
- ✅ `func_call.3: FUNCNAME "(" arg_list? ")"` (gams_grammar.lark:315)
- ✅ `arg_list: expr ("," expr)*` (gams_grammar.lark:316)
- ✅ `atom → func_call → funccall` (expression integration)
- ✅ `Call` AST node exists (src/ir/ast.py:170)
- ✅ Works in equation context already

**Only Missing Piece:**
- Semantic handler for parameter assignment context (may not create Call nodes currently)
- Grammar and AST are complete ✅

**Argument Complexity Distribution:**
- Constants only: 17% (~15 occurrences)
- Simple variables: 28% (~25 occurrences)
- Indexed variables: 33% (~30 occurrences)
- Complex expressions: 22% (~20 occurrences)

**Implementation Effort Revision:**
- **Grammar changes:** 5 minutes (add round, mod, ceil to FUNCNAME token)
- **AST changes:** 0 hours (Call node exists)
- **Semantic handler:** 1-1.5 hours (verify/fix parameter context handling)
- **IR changes:** 30 minutes (add expressions field to ParameterDef)
- **Testing:** 1 hour
- **Total: 2.5-3 hours** (NOT 6-8 hours - 62-71% reduction)

**Reference:** `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` Sections 3, 5, 7, 8, 9.4

---

## Unknown 10.3.5: Grammar Production Location

### Priority
**Low** - Implementation detail

### Assumption
Function call grammar should be added to parameter_assignment rule, not as general expression everywhere.

### Research Questions
1. Where in grammar should function_call production go?
2. Should function calls be allowed in all expressions or just parameter assignments?
3. Do equations also use function calls? (Yes, likely - but not circle.gms blocker)
4. Is scoped grammar better (just parameter assignments now) or general (expressions)?
5. Will this affect equation parsing or other features?

### How to Verify
- Review grammar structure in `src/gams/gams_grammar.lark`
- Check if expressions already support function calls (they might!)
- Determine minimal change needed for circle.gms

### Risk if Wrong
- **Low:** Suboptimal grammar organization (can refactor later)

### Estimated Research Time
Minimal (part of implementation planning, no dedicated prep time)

### Owner
Development team (during Sprint 10 implementation)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be determined during implementation

---

# Category 4: Targeted Feature Implementation - Level Bound Conflict Resolution

**Unlocks:** himmel16.gms (79% → 100%)  
**Effort:** 2-3 hours (Low risk)  
**Blocker:** Multiple `.l` assignments to same variable cause "conflicting level bound" error

---

## Unknown 10.4.1: Level Bound Conflict Root Cause

### Priority
**Critical** - Determines fix approach

### Assumption
"Conflicting level bound" error is semantic validation issue (multiple `.l` assignments), not parse error. Parser should allow multiple assignments; validator should handle them.

### Research Questions
1. Where does "conflicting level bound" error originate? (parser or semantic validator?)
2. Which variables in himmel16.gms have multiple `.l` assignments?
3. Is this GAMS-valid syntax (last assignment wins) or GAMS-invalid (error)?
4. Should we track `.l` assignments and validate, or allow all and let GAMS decide?
5. Is this specific to indexed variables or all variables?

### How to Verify
```bash
# Find all .l assignments in himmel16.gms
grep -n "\.l\s*=" tests/fixtures/gamslib/himmel16.gms

# Parse himmel16.gms and examine error stack trace
python -c "
from src.ir.parser import parse_model_file
try:
    parse_model_file('tests/fixtures/gamslib/himmel16.gms')
except Exception as e:
    import traceback
    traceback.print_exc()
" 2>&1 | grep -A5 "level"

# Check GAMS documentation for .l attribute semantics
```

### Risk if Wrong
- **Critical:** Fix in wrong layer (parser vs validator) or wrong approach
- May not resolve error or create new issues

### Estimated Research Time
2 hours (Task 3: Analyze himmel16.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 3)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 3 - himmel16.gms Complete Blocker Chain Analysis

**Finding:** The assumption was PARTIALLY WRONG. The error is indeed from the parser (not just semantic validation), BUT the root cause is a PARSER BUG in index expansion, not intentional validation.

**Root Cause Identified:**

**Location:** `src/ir/parser.py`, function `_expand_variable_indices` (line 2125)

**Bug:** Parser incorrectly expands literal string indices to ALL domain members instead of using only the specified literal value.

**Example from himmel16.gms:**
```gams
Set i /1*6/;
Variable x(i);

x.fx("1") = 0;  # Should set fx ONLY for index "1"
```

**Expected behavior:**
- Creates fx_map entry for index ("1",) only
- Does NOT affect indices ("2",), ("3",), etc.

**Actual (buggy) behavior:**
- Calls `_expand_variable_indices` which expands to ALL set members
- Creates fx_map entries for ("1",), ("2",), ("3",), ("4",), ("5",), ("6",)
- Also sets implicit l_map for ALL indices

**Why Conflict Occurs:**
1. Line 57: `x.fx("1") = 0` → Bug sets fx_map AND l_map for ALL indices ("1" through "6")
2. Lines 60-62: `x.l("2") = 0.5`, `x.l("3") = 0.5`, `x.l("4") = 0.5`
   - Bug expands each to ALL indices
   - Sets l_map["1"] = 0.5 (conflicts with implicit 0 from fx)
3. Line 63: `x.l("5") = 0` → Bug expands to ALL indices
   - Tries to set l_map["1"] = 0
   - **CONFLICT:** l_map["1"] already has 0.5

**Error Origin:**
- Error thrown from: `_set_bound_value` at parser.py:1988
- Called by: `_apply_variable_bound` at parser.py:1934
- Root cause in: `_expand_variable_indices` at parser.py:2125

**Parser vs Validator:**
- This IS a parser error (thrown during parsing)
- NOT a separate semantic validation step
- Parser incorrectly expands indices during bound application

**Fix Approach:**
Modify `_expand_variable_indices` to distinguish:
- Set/alias names → expand to all members
- Literal strings ("1", "2", etc.) → use as-is, don't expand

**Estimated Fix:** 3-4 hours (localized change, clear test case)

**Evidence:**
- Detailed stack trace analysis in himmel16_analysis.md
- Code inspection of parser.py index expansion logic
- Test case: himmel16.gms lines 57-68

---

## Unknown 10.4.2: GAMS Level Attribute Semantics

### Priority
**High** - Determines if our implementation matches GAMS behavior

### Assumption
In GAMS, multiple `.l` assignments are valid and last assignment wins (similar to Python variable assignment).

### Research Questions
1. What does GAMS do with multiple `.l` assignments? (last wins, error, merge?)
2. Does order matter? (sequential assignments)
3. Are there cases where multiple `.l` are expected/common?
4. Does `.l` behavior differ for scalars vs indexed variables?
5. Should our parser match GAMS behavior exactly or be more permissive?

### How to Verify
- Check GAMS documentation for `.l` (level) attribute
- Create test GAMS file with multiple `.l` assignments
- Run in GAMS (if available) to see behavior
- Or: Survey GAMSLIB for patterns

### Risk if Wrong
- **Medium:** Implement behavior that doesn't match GAMS (incorrect semantics)
- Generated code may not work in GAMS

### Estimated Research Time
Included in Task 3 (2 hours total includes semantics research)

### Owner
Development team (Prep Task 3)

### Verification Results
✅ **Status: VERIFIED**  
**Verification Date:** 2025-11-23  
**Verified By:** Task 3 - himmel16.gms Complete Blocker Chain Analysis

**Finding:** The assumption was CORRECT. In GAMS, multiple `.l` assignments on different indices are VALID, and the parser should allow them.

**GAMS Semantics Verified:**

**Multiple `.l` Assignments:**
- VALID in GAMS to have `.l` assignments on different indices: `x.l("1") = 0`, `x.l("2") = 0.5`
- VALID in GAMS to mix `.fx` and `.l` on different indices: `x.fx("1") = 0`, `x.l("2") = 0.5`
- Last assignment wins if same index assigned multiple times
- Sequential assignments are processed in order

**Attribute Behavior:**
- `.l` = Level/starting value for solver (initial point)
- `.fx` = Fixed bound (sets both .lo and .up to same value, variable cannot change)
- `.lo` = Lower bound
- `.up` = Upper bound

**Index-Specific:**
For indexed variables like `x(i)`, bounds are per-index:
- `x.fx("1") = 0` only fixes index "1"
- `x.l("2") = 0.5` only sets level for index "2"
- These DO NOT conflict - they affect different indices

**Our Parser's Bug:**
The parser currently INCORRECTLY rejects this valid GAMS syntax because it expands literal indices to ALL domain members. This is a bug in our implementation, not a difference in semantics philosophy.

**Expected Behavior:**
Our parser should match GAMS behavior exactly:
- Allow multiple `.l` assignments on different indices
- Allow mixing `.fx`, `.l`, `.lo`, `.up` on different indices
- Track bounds per-index, not globally per variable
- Only conflict if SAME index gets conflicting values (e.g., `.lo("1") = 5` and `.up("1") = 3`)

**Evidence:**
- himmel16.gms is valid GAMS code (from official GAMSLIB)
- Pattern `x.fx("1")` + `x.l("2")` appears in production GAMS models
- No GAMS documentation suggests this should error
- Parser bug is preventing valid code from parsing

**Conclusion:** Our parser must be fixed to match GAMS semantics. The current behavior is incorrect.

---

## Unknown 10.4.3: Implementation Complexity

### Priority
**Low** - Validates effort estimate

### Assumption
Fixing level bound conflicts is simple (2-3 hours): either remove validation check or track last assignment per variable.

### Research Questions
1. Where is "conflicting level bound" check implemented?
2. Is it single-line fix (remove check) or multi-line (track assignments)?
3. Are there test cases to update?
4. Does fix affect other attribute types (`.lo`, `.up`, `.fx`, `.m`)?
5. Is 2-3 hour estimate realistic?

### How to Verify
```bash
# Find conflicting level bound check in codebase
grep -rn "conflicting.*level" src/
grep -rn "level.*bound" src/

# Estimate change scope (lines of code, files affected)
```

### Risk if Wrong
- **Low:** Underestimate complexity (takes 4-5 hours instead of 2-3)
- Minor schedule impact

### Estimated Research Time
Minimal (check during Task 3, no dedicated time)

### Owner
Development team (Prep Task 3)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be validated during Task 3

---

# Category 5: Targeted Feature Implementation - Nested/Subset Indexing in Domains

**Unlocks:** maxmin.gms (40% → 100%)  
**Effort:** 10-12 hours (HIGH RISK - most complex feature)  
**Blocker:** `defdist(low(n,nn))..` where `low(n,nn)` is 2D subset domain  
**Decision Point:** Implement in Sprint 10 or defer to Sprint 11?

---

## Unknown 10.5.1: Nested Indexing Complexity Level

### Priority
**Critical** - Go/no-go decision for Sprint 10

### Assumption
Nested/subset indexing requires 10-12 hours to implement, but this is based on incomplete understanding. Actual complexity may be higher.

### Research Questions
1. What exactly is `low(n,nn)` syntax in GAMS?
2. How does GAMS resolve subset domains at compile time?
3. What grammar changes are required? (recursive domain expressions?)
4. What AST changes are required? (nested index nodes?)
5. Is 10-12 hours realistic or optimistic?
6. Should we attempt in Sprint 10 or defer to Sprint 11 (target 90% instead of 100%)?

### How to Verify
- Study maxmin.gms subset declarations (Task 4)
- Research GAMS documentation on subset domains
- Create complexity assessment: grammar + AST + semantic + tests
- Compare to Sprint 8 option statements (6-8h) and Sprint 9 i++1 (8-10h)
- Make recommendation: IMPLEMENT or DEFER

### Risk if Wrong
- **Critical:** Attempt implementation but runs >12 hours (consumes sprint, other features delayed)
- OR: Defer but could have implemented in time (miss 100% target unnecessarily)

### Estimated Research Time
3-4 hours (Task 8: Research Nested/Subset Indexing Semantics)

### Owner
Development team (Prep Task 8) - Makes recommendation

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 4 - maxmin.gms Blocker Chain Analysis  
**Time Spent:** 2.5 hours (combined with Unknown 10.1.3)

**Finding:** Assumption was OPTIMISTIC - actual complexity is 10-14 hours for nested indexing alone, 23-40 hours for full maxmin.gms support.

**Complexity Assessment - Nested Indexing (HIGH: 9/10):**

**Grammar Changes Required:**
- Modify `equation_def` rule to support nested syntax: `ID "(" domain_spec ")" ..`
- Create new `domain_spec` rule to handle:
  - Simple identifiers: `i, j`
  - Subset references: `low`
  - Nested subset with indices: `low(n,nn)`
- Current limitation: `id_list: ID ("," ID)*` only accepts simple IDs
- Estimated: 3-4 hours

**AST Changes Required:**
- Equation domain nodes need new structure to represent subsets
- Must distinguish: `equation(i,j)` vs `equation(subset)` vs `equation(subset(i,j))`
- Add subset reference nodes with optional index expressions
- Estimated: 2-3 hours

**Semantic Resolution Required:**
- Resolve subset definitions at equation creation time
- Expand subset domains to actual index combinations: `low(n,nn)` → all (n,nn) where ord(n) > ord(nn)
- Handle subset assignments: `low(n,nn) = ord(n) > ord(nn);`
- Track subset membership for domain expansion
- Estimated: 4-6 hours

**Testing Required:**
- 7 test suites with 20+ test cases (see maxmin_analysis.md)
- Estimated: 1-2 hours

**Total Effort:** 10-14 hours (nested indexing alone)

**Comparison to Previous Features:**
- Sprint 8 option statements: 6-8 hours (MEDIUM complexity)
- Sprint 9 i++1 lead/lag: 8-10 hours (MEDIUM-HIGH complexity)
- Sprint 10 nested indexing: 10-14 hours (HIGH complexity)
- **Risk Level:** HIGH - Most complex feature to date

**Answer to Research Questions:**
1. **What is `low(n,nn)` syntax?** Subset domain - restricts equation to subset of index combinations
2. **How does GAMS resolve?** At compile time, expands to filtered index combinations based on subset definition
3. **Grammar changes?** Recursive domain expressions (new `domain_spec` rule)
4. **AST changes?** Nested index nodes with subset references
5. **Is 10-12 hours realistic?** YES for nested indexing alone, but maxmin.gms has 4 additional blocker categories
6. **Implement or defer?** **DEFER to Sprint 11+**

**RECOMMENDATION: DEFER**

**Rationale:**
1. **HIGH RISK:** Could consume 10-14 hours without success
2. **LOW ROI:** Only unlocks 1 model (maxmin.gms 40% → 51%)
3. **MULTIPLE DEPENDENCIES:** Requires function calls + multi-model + loop tuples for 100%
4. **FALLBACK VIABLE:** Target 90% (9/10 models) without maxmin.gms
5. **BETTER SEQUENCING:** Implement simpler features first (circle.gms, himmel16.gms)

**Sprint 10 Decision:** DEFER nested indexing. Target 90% (9/10 models) with circle.gms + himmel16.gms (9-14 hours total).

**Documentation:** Complete complexity assessment in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` (Section 12)

---

## Unknown 10.5.2: GAMS Subset Domain Semantics

### Priority
**High** - Understanding required for implementation

### Assumption
Subset domains restrict equation domain to subset of indices, and GAMS resolves this at compile time based on subset definition.

### Research Questions
1. How are subsets declared in GAMS? (`Set low(n,nn);`?)
2. How does `defdist(low(n,nn))..` differ from `defdist(n,nn)..`?
3. Does subset domain mean "for all (n,nn) in low" (iteration)?
4. How do we represent this in IR? (filtered domain? subset reference?)
5. Is this common pattern in GAMS or maxmin.gms-specific?

### How to Verify
```bash
# Study maxmin.gms subset declarations
grep -n "Set\|set" tests/fixtures/gamslib/maxmin.gms | grep -i "low"

# Find how low is used
grep -n "low" tests/fixtures/gamslib/maxmin.gms

# Survey GAMSLIB for similar patterns
grep -rn "(\w\+(.*))\.\.". tests/fixtures/gamslib/ | head -20
```

### Risk if Wrong
- **High:** Misunderstand semantics, implement wrong behavior
- Parsing works but generated MCP incorrect

### Estimated Research Time
Included in Task 8 (3-4 hours total includes semantics research)

### Owner
Development team (Prep Task 8)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 4 - maxmin.gms Blocker Chain Analysis  
**Time Spent:** 2.5 hours (combined with Unknowns 10.1.3 and 10.5.1)

**Finding:** Assumption was CORRECT - subset domains do restrict equation domains to subset members, resolved at compile time.

**GAMS Subset Domain Semantics:**

**1. How are subsets declared?**
```gams
Set
   n        'number of points'   / p1*p13 /
   low(n,n) 'lower triangle';     // 2D subset declaration

Alias (n,nn);

low(n,nn) = ord(n) > ord(nn);     // Subset assignment
```
- **Declaration:** `Set subset_name(parent_set, ...);` - declares subset with domain
- **Assignment:** `subset(i,j) = condition;` - populates subset based on condition
- **Example:** `low(n,nn)` is true when ord(n) > ord(nn) (lower triangle of n×n matrix)

**2. How does `defdist(low(n,nn))..` differ from `defdist(n,nn)..`?**

WITHOUT subset (full domain):
```gams
defdist(n,nn)..  // Defines equation for ALL (n,nn) pairs
                 // If n = {p1,p2,p3}, creates 3×3 = 9 equations
```

WITH subset (filtered domain):
```gams
defdist(low(n,nn))..  // Defines equation ONLY for (n,nn) WHERE low(n,nn) = true
                      // If n = {p1,p2,p3} and low = lower triangle
                      // Creates only 3 equations: (p2,p1), (p3,p1), (p3,p2)
```

**3. Does subset domain mean iteration?**
Yes - "for all (n,nn) in low" means "for each (n,nn) pair where low(n,nn) is true"

**4. How to represent in IR?**
Two approaches:
- **Option A:** Filtered domain - store subset reference, expand at equation creation
- **Option B:** Pre-expanded domain - resolve subset membership, store explicit index list
- **Recommended:** Option A (more flexible, matches GAMS semantics)

**5. Is this common pattern?**
Moderately common in GAMSLIB:
- Used for triangular matrices (avoid duplicate constraints)
- Used for conditional equation generation
- maxmin.gms uses it extensively (5 occurrences)

**Pattern Frequency in maxmin.gms:**
- Line 37: Subset assignment `low(n,nn) = ord(n) > ord(nn);`
- Line 51: `defdist(low(n,nn))..` - nested subset with indices
- Line 53: `mindist1(low)..` - subset reference shorthand
- Line 55: `mindist1a(low(n,nn))..` - nested subset with indices
- Line 59: `smin(low(n,nn), ...)` - subset in aggregation
- Line 78: `dist.l(low(n,nn)) = ...` - subset in variable bounds

**Shorthand Syntax:**
- `equation(low)..` is shorthand for `equation(low(n,nn))..`
- Parser must infer indices from subset dimensionality
- Adds complexity to implementation

**Answer to Research Questions:**
1. **Subset declaration:** `Set subset_name(domain1, domain2, ...);`
2. **Semantic difference:** Filters equation domain to subset members only
3. **Iteration meaning:** Yes - generates equation for each member of subset
4. **IR representation:** Subset reference node with index expansion at creation time
5. **Pattern frequency:** Moderately common - used for conditional equation generation

**Impact on Implementation:**
- Must support both `equation(subset(i,j))` (explicit indices) AND `equation(subset)` (inferred indices)
- Must resolve subset definitions before equation expansion
- Shorthand syntax adds complexity (automatic index inference)

**Documentation:** Complete semantics research in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` (Section 11)

---

## Unknown 10.5.3: Partial Implementation Feasibility

### Priority
**Medium** - Affects defer vs implement decision

### Assumption
If full nested indexing is too complex, we cannot implement partial support (simpler subset syntax) in Sprint 10.

### Research Questions
1. Can we support `domain(subset)` (1-level) without supporting `domain(subset(a,b))` (2-level)?
2. Is there intermediate syntax we could handle?
3. Would partial implementation unlock any models?
4. Is partial better than deferring entirely?
5. Or is it all-or-nothing (full nested or defer)?

### How to Verify
- Analyze maxmin.gms: does it use only 2-level nesting or deeper?
- Survey GAMSLIB: what nesting levels appear?
- Assess: could we handle common case (2-level) and defer rare cases (3+ levels)?

### Risk if Wrong
- **Medium:** Defer entirely when partial could work (missed opportunity)
- OR: Attempt partial but it doesn't unlock any models (wasted effort)

### Estimated Research Time
Included in Task 8 (part of complexity assessment)

### Owner
Development team (Prep Task 8)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 4 - maxmin.gms Blocker Chain Analysis  
**Time Spent:** 2.5 hours (combined with Unknowns 10.1.3, 10.5.1, 10.5.2)

**Finding:** Assumption was CORRECT - partial implementation is NOT feasible, it's all-or-nothing.

**Partial Implementation Analysis:**

**maxmin.gms Nesting Patterns:**
- **1-level:** `mindist1(low)..` - subset reference without indices (3 occurrences)
- **2-level:** `defdist(low(n,nn))..` - subset with explicit indices (2 occurrences)
- **Complexity:** BOTH patterns must be supported together

**Can we support 1-level without 2-level?**
**NO** - Both patterns appear in same file, interdependent:
```gams
mindist1(low)..        mindist =l= dist(low);        // 1-level (shorthand)
mindist1a(low(n,nn)).. mindist =l= sqrt(sum(...));   // 2-level (explicit)
```
- Both reference same subset `low(n,nn)`
- 1-level is shorthand that requires parsing 2-level semantics
- Cannot implement 1-level without understanding 2-level structure

**Is there intermediate syntax?**
**NO** - No simpler subset patterns found in GAMSLIB Tier 1:
- Either files don't use subsets at all
- Or files use full nested indexing (both 1-level and 2-level)
- No "subset-lite" syntax exists

**Would partial implementation unlock any models?**
**NO** - maxmin.gms requires BOTH 1-level and 2-level:
- Even if we implement 1-level only, still blocked by 2-level patterns
- Must implement full nested indexing to unlock maxmin.gms
- No other Tier 1 model uses subsets

**Is partial better than deferring entirely?**
**NO** - Partial provides zero value:
- Doesn't unlock any models
- Still requires significant implementation (6-8 hours for 1-level)
- Leaves incomplete feature in codebase
- Better to defer entirely and implement complete feature in Sprint 11

**All-or-nothing?**
**YES** - Must implement full nested indexing (both patterns) or defer entirely:
- 1-level alone: 6-8 hours, unlocks 0 models
- 2-level alone: 4-6 hours, unlocks 0 models  
- Full nested indexing: 10-14 hours, unlocks 1 model (maxmin.gms 40% → 51%)
- Full maxmin.gms support: 23-40 hours (all 5 blocker categories)

**Answer to Research Questions:**
1. **Can we support 1-level without 2-level?** NO - Interdependent in same file
2. **Is there intermediate syntax?** NO - No subset-lite patterns exist
3. **Would partial unlock models?** NO - maxmin.gms needs both patterns
4. **Is partial better than defer?** NO - Zero value, incomplete feature
5. **All-or-nothing?** YES - Full implementation or defer entirely

**Decision Impact:**
- Partial implementation is NOT an option
- Choice is binary: FULL nested indexing (10-14 hours) OR DEFER
- Analysis strongly supports DEFER given:
  - HIGH complexity (10-14 hours for subset alone)
  - LOW ROI (only 1 model, only to 51% not 100%)
  - HIGH risk (most complex feature to date)
  - BETTER alternatives (circle.gms + himmel16.gms = 9/10 models in 9-14 hours)

**Sprint 10 Decision:** DEFER nested indexing entirely. No partial implementation.

**Documentation:** Partial implementation feasibility analysis in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` (Section 13)

---

## Unknown 10.5.4: Alternative Solutions

### Priority
**Medium** - Affects decision options

### Assumption
Only solution is full grammar support for nested indexing. No simpler alternatives exist.

### Research Questions
1. Could we transform nested syntax to non-nested during preprocessing?
2. Could we expand subset domains to explicit indices?
3. Is there GAMS workaround (equivalent non-nested syntax)?
4. Can we request GAMSLIB provide non-nested version of maxmin.gms?
5. Are there other GAMSLIB models with easier subset syntax to start with?

### How to Verify
- Research GAMS preprocessing capabilities
- Check if subset expansion is feasible
- Survey GAMSLIB for alternative subset usage patterns
- Assess transformation complexity vs direct implementation

### Risk if Wrong
- **Low:** Miss simpler solution, implement complex one
- OR: Pursue alternative that's actually harder

### Estimated Research Time
Minimal (part of Task 8 if time permits)

### Owner
Development team (Prep Task 8)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be explored during Task 8 if decision unclear

---

## Unknown 10.5.5: Fallback Plan if Deferred

### Priority
**Medium** - Planning for 90% scenario

### Assumption
If we defer nested indexing, Sprint 10 targets 90% (9/10 models) instead of 100%, and this is acceptable outcome.

### Research Questions
1. Is 90% acceptable for Sprint 10 given Epic 2 goals?
2. Would 9/10 models meet stakeholder expectations?
3. How do we communicate 90% target vs 100% goal?
4. Does Sprint 11 have capacity for nested indexing + other goals?
5. Are there other quick wins to compensate for deferring maxmin?

### How to Verify
- Review Epic 2 goals: is 90% sufficient for parser maturity?
- Check Sprint 11 plan: does it have room for nested indexing?
- Identify alternative high-value features for Sprint 10 if defer

### Risk if Wrong
- **Low:** Set wrong expectations (promise 100% but deliver 90%)
- Stakeholder dissatisfaction

### Estimated Research Time
Minimal (planning consideration, no dedicated research)

### Owner
Sprint planning (Task 12)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be addressed during Task 12 scheduling

---

# Category 6: Targeted Feature Implementation - abort$ in If-Block Bodies

**Unlocks:** mingamma.gms (54% → 100%)  
**Effort:** 2-3 hours (Low risk - grammar extension)  
**Blocker:** `abort$(condition)` statements inside if-block bodies not supported

---

## Unknown 10.6.1: abort$ Syntax Variations

### Priority
**High** - Ensures complete implementation

### Assumption
abort$ syntax in if-blocks is just `abort$(condition);` with no variations.

### Research Questions
1. What are all abort$ syntax forms? (`abort`, `abort$`, `$abort`, others?)
2. Can abort$ appear outside if-blocks? (we may already support some locations)
3. What condition syntax is valid? (boolean expression, $-conditions, etc.)
4. Are there abort$ variants we need to handle? (`abort$[...]` with brackets?)
5. How many abort$ statements in mingamma.gms? (all in if-blocks or some elsewhere?)

### How to Verify
```bash
# Find all abort statements in mingamma.gms
grep -n "abort" tests/fixtures/gamslib/mingamma.gms

# Survey GAMSLIB for abort$ variations
grep -rn "abort" tests/fixtures/gamslib/*.gms | head -30

# Check if abort used outside if-blocks
grep -rn "^\s*abort" tests/fixtures/gamslib/*.gms | grep -v "if" | head -10
```

### Risk if Wrong
- **Medium:** Implement only `abort$(...)` but mingamma.gms uses `abort$[...]` (syntax error)
- OR: Miss abort$ in other locations (incomplete feature)

### Estimated Research Time
1-2 hours (Task 5: Analyze mingamma.gms Complete Blocker Chain)

### Owner
Development team (Prep Task 5)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 5 - mingamma.gms Blocker Chain Analysis  
**Time Spent:** 1.5 hours (combined with Unknown 10.1.4)

**Finding:** abort$ syntax in mingamma.gms uses SQUARE BRACKETS `abort$[condition]`, not parentheses. Sprint 9 implemented this correctly.

**abort$ Syntax Analysis:**

1. **What are all abort$ syntax forms in mingamma.gms?**
   ```bash
   grep -n "abort" tests/fixtures/gamslib/mingamma.gms
   ```
   - Line 59: `abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results with gamma";`
   - Line 62: `abort$[abs(x2delta) > xtol or abs(y2delta) > ytol] "inconsistent results with loggamma";`
   - **Syntax:** `abort$[condition] "message";` (uses SQUARE BRACKETS)

2. **Can abort$ appear outside if-blocks?**
   - In mingamma.gms: NO - both abort$ statements are inside if-blocks (lines 58-60, 61-63)
   - General GAMS: YES - abort can appear at top level
   - Current grammar (line 231): `abort_stmt: "abort"i ("$" expr)? STRING? SEMI`
   - Top-level abort is already supported, if-block abort was the blocker

3. **What condition syntax is valid?**
   - Boolean expressions with comparison operators: `abs(x1delta) > xtol`
   - Logical operators: `or`, `and`
   - No `$-conditions` found in mingamma.gms
   - Uses SQUARE BRACKETS `[...]` not parentheses `(...)`

4. **Are there abort$ variants to handle?**
   - `abort$[...]` with square brackets: YES (mingamma.gms uses this)
   - `abort$(...)` with parentheses: NOT in mingamma.gms
   - Plain `abort` without condition: NOT in mingamma.gms
   - Status: Sprint 9 implementation handles square bracket syntax correctly

5. **How many abort$ statements and where?**
   - Total: 2 abort$ statements
   - Line 59: Inside first if-block (checking m1.solveStat)
   - Line 62: Inside second if-block (checking m2.solveStat)
   - All in if-blocks: YES (0 at top level)

**Sprint 9 Implementation Status:**
- ✅ abort$ in if-blocks: FIXED in Sprint 9
- ✅ Square bracket syntax: Correctly supported
- ✅ Boolean expressions: Correctly parsed
- ✅ String messages: Correctly parsed

**Verification Test:**
- Commented out all scalar references (which cause undefined symbol errors)
- Kept abort$ lines intact (lines 59, 62)
- Result: ✅ File parsed successfully through abort$ statements
- Confirms: abort$ in if-blocks is fully functional

**GAMSLIB Survey (broader patterns):**
Not needed for mingamma.gms analysis - Sprint 9 implementation handles the pattern correctly.

**Answer to Research Questions:**
1. **Syntax forms:** `abort$[condition] "message";` with square brackets
2. **Outside if-blocks:** Not in mingamma.gms (but top-level already supported)
3. **Condition syntax:** Boolean expressions with comparison and logical operators
4. **Variants:** Square bracket syntax (correctly implemented in Sprint 9)
5. **Location:** 2 statements, both inside if-blocks

**Impact on Sprint 10:**
- abort$ in if-blocks: ✅ Already complete (Sprint 9)
- No additional work needed for abort$ feature
- mingamma.gms blocker is comma-separated scalar declarations (different feature)

**Documentation:** Complete abort$ analysis in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` (Section 7)

---

## Unknown 10.6.2: If-Block Grammar Structure

### Priority
**Medium** - Implementation approach

### Assumption
Adding abort$ to if-block bodies is simple grammar change: add `abort_statement` to if_block_body production.

### Research Questions
1. What is current if-block grammar structure?
2. What statements are already allowed in if-block bodies?
3. Is abort$ the only missing statement type?
4. How do we handle abort$ in nested if-blocks?
5. Is 2-3 hour estimate realistic for grammar + tests?

### How to Verify
```bash
# Check current grammar for if-blocks
grep -A10 "if.*block" src/gams/gams_grammar.lark

# Check what statements are currently allowed
grep -B5 -A5 "if_block" src/gams/gams_grammar.lark
```

### Risk if Wrong
- **Low:** Underestimate complexity (takes 4-5 hours instead of 2-3)
- Minor schedule impact

### Estimated Research Time
Included in Task 5 (part of abort$ analysis)

### Owner
Development team (Prep Task 5)

### Verification Results
✅ **Status: VERIFIED**  
**Date:** November 23, 2025  
**Task:** Prep Task 5 - mingamma.gms Blocker Chain Analysis  
**Time Spent:** 1.5 hours (combined with Unknowns 10.1.4, 10.6.1)

**Finding:** abort$ in if-blocks was ALREADY implemented in Sprint 9. No additional grammar work needed.

**If-Block Grammar Analysis:**

**Current Grammar Structure:**
```bash
grep -A10 "if_stmt" src/gams/gams_grammar.lark
```

Sprint 9 already added support for statements in if-block bodies, including abort$.

**What statements are allowed in if-block bodies?**
- Assignment statements
- abort$ statements (ADDED in Sprint 9)
- Other statements supported by the grammar

**Is abort$ the only missing statement type?**
- abort$ is NO LONGER missing - it was implemented in Sprint 9
- Current blocker for mingamma.gms is comma-separated scalar declarations (different feature)

**How do nested if-blocks work?**
- Sprint 9 implementation handles nested if-blocks correctly
- No issues found in testing

**Was 2-3 hour estimate realistic?**
- N/A - Sprint 9 already completed this work
- Actual implementation: Part of Sprint 9 abort$ in if-blocks feature
- Tests: `tests/unit/test_abort_in_if_blocks.py` exists and passes

**Verification:**
- Tested mingamma.gms with scalar references commented out
- abort$ statements at lines 59, 62 parse successfully
- Confirms: If-block grammar correctly supports abort$ statements

**Sprint 9 Implementation:**
- ✅ Grammar changes: Complete
- ✅ If-block body statements: Complete  
- ✅ abort$ support: Complete
- ✅ Tests: Complete (test_abort_in_if_blocks.py)

**Impact on Sprint 10:**
- No work needed for if-block grammar
- No work needed for abort$ feature
- mingamma.gms blocker is comma-separated scalar declarations (lines 30-38)

**Answer to Research Questions:**
1. **Current if-block structure:** Supports statement lists in bodies (implemented Sprint 9)
2. **Allowed statements:** Assignments, abort$, and other statement types
3. **Missing statement types:** None for mingamma.gms use case
4. **Nested if-blocks:** Handled correctly by Sprint 9 implementation
5. **Estimate realistic:** Sprint 9 completed this work successfully

**Documentation:** If-block grammar analysis in `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` (Section 7)

---

# Category 7: Synthetic Test Suite

**Sprint 10 Phase 5:** Validate features work in isolation  
**Sprint 9 Lesson:** Cannot test i++1 works because himmel16.gms has secondary blockers

---

## Unknown 10.7.1: Synthetic Test Design Principles

### Priority
**High** - Foundation for all synthetic tests

### Assumption
Synthetic tests should be minimal (5-15 lines), test ONE feature, and have clear pass/fail criteria.

### Research Questions
1. What makes a good synthetic test? (minimal, isolated, validating)
2. How minimal is "minimal"? (declarations only, or minimal realistic model?)
3. Should synthetic tests be parseable only or also semantically valid?
4. How do we ensure tests are truly isolated (no feature interactions)?
5. What test framework integrations needed (pytest parametrization)?

### How to Verify
- Design template for synthetic tests (Task 9)
- Create examples for each feature
- Validate: can we tell if feature works from test result?
- Test with known-working feature (e.g., basic variable declaration)

### Risk if Wrong
- **Medium:** Synthetic tests too complex (interact with other features, unclear results)
- OR: Tests too simple (don't actually validate feature works)

### Estimated Research Time
2-3 hours (Task 9: Design Synthetic Test Framework)

### Owner
Development team (Prep Task 9)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 9)

---

## Unknown 10.7.2: Sprint 9 Feature Validation

### Priority
**High** - Prerequisite for Sprint 10 features

### Assumption
Sprint 9 features (i++1 indexing, equation attributes, model sections) actually work correctly, we just can't test them with complex models due to secondary blockers.

### Research Questions
1. Does i++1 indexing work in isolation? (create synthetic test to verify)
2. Do equation attributes work? (mingamma.gms doesn't use them, was Sprint 9 implementation correct?)
3. Do model sections work? (hs62.gms now parses, but does feature work generally?)
4. Are there bugs in Sprint 9 features hidden by complex model failures?
5. Should we fix any Sprint 9 feature bugs before implementing Sprint 10 features?

### How to Verify
```bash
# Create synthetic tests for Sprint 9 features (Task 10)
# tests/synthetic/i_plusplus_indexing.gms
# tests/synthetic/equation_attributes.gms
# tests/synthetic/model_sections.gms

# Run tests - all should PASS
pytest tests/synthetic/test_synthetic.py -k "sprint_9"

# If any fail → bug in Sprint 9 implementation, must fix before Sprint 10
```

### Risk if Wrong
- **High:** Sprint 9 features have bugs, we build Sprint 10 features on broken foundation
- Cascading failures, difficult debugging

### Estimated Research Time
2 hours (Task 10: Validate Sprint 9 Features Work in Isolation)

### Owner
Development team (Prep Task 10)

### Verification Results
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 10)  
**Must verify BEFORE Sprint 10 implementation begins**

---

# Template: Adding New Unknowns

When discovering new unknowns during Sprint 10, use this template:

```markdown
## Unknown 10.X.Y: [Title]

### Priority
**[Critical/High/Medium/Low]** - [One-line impact description]

### Assumption
[What we currently assume to be true]

### Research Questions
1. [Specific question about assumption]
2. [Another specific question]
3. [...]
4. [...]
5. [...]

### How to Verify
[Concrete experiments, test cases, or research methods]

\`\`\`bash
# Verification commands
[commands here]
\`\`\`

### Risk if Wrong
- **[Priority]:** [What happens if assumption is incorrect]
- [Additional impacts]

### Estimated Research Time
[Hours] ([Which task or "discovered during Day X"])

### Owner
[Team member or "Development team"]

### Verification Results
🔍 **Status: INCOMPLETE**  
[To be updated when researched]
```

---

# Next Steps

## Pre-Sprint 10 (Prep Phase)

### Week Before Sprint 10 Day 1
1. ✅ **Complete Prep Tasks 2-11** (verify all Critical/High unknowns)
   - Task 2: Verify Unknowns 10.1.1 (circle.gms complete chain)
   - Task 3: Verify Unknowns 10.1.2, 10.4.1, 10.4.2 (himmel16.gms + level bounds)
   - Task 4: Verify Unknowns 10.1.3, 10.5.1, 10.5.2 (maxmin.gms + nested indexing decision)
   - Task 5: Verify Unknowns 10.1.4, 10.6.1 (mingamma.gms + abort$)
   - Task 6: Verify Unknowns 10.2.1, 10.2.2, 10.2.3 (comma-separated declarations)
   - Task 7: Verify Unknowns 10.3.1, 10.3.2 (function calls)
   - Task 8: Verify Unknowns 10.5.1, 10.5.2, 10.5.3 (nested indexing - CRITICAL DECISION)
   - Task 9: Verify Unknown 10.7.1 (synthetic test framework)
   - Task 10: Verify Unknown 10.7.2 (Sprint 9 features validation)
   - Task 11: Set up checkpoint infrastructure

2. ✅ **Update This Document** with verification results
   - Change status from 🔍 INCOMPLETE to ✅ COMPLETE or ❌ WRONG
   - Document findings in "Verification Results" sections
   - Add new unknowns discovered during prep
   - Update estimated research time based on actual time spent

3. ✅ **Make Critical Decisions**
   - Unknown 10.5.1: IMPLEMENT or DEFER nested indexing?
   - Adjust Sprint 10 target: 100% (10/10) or 90% (9/10)?
   - Update SCHEDULE.md based on decision

## During Sprint 10

### Daily Review
- **Standup:** Review relevant unknowns for day's work
- **End of Day:** Update unknowns with implementation findings
- **Add Discoveries:** Document new unknowns as they arise

### Day 5 Checkpoint
- **Validate Assumptions:** Check if models unlocking as expected
- **Unknown Review:** Were any unknowns WRONG? What impact?
- **Adjust:** Pivot if assumptions incorrect (Unknown 10.1.5 - detection method)

### Sprint 10 Completion
- **Final Update:** Mark all unknowns resolved
- **Retrospective:** Which unknowns were most valuable? Which were missed?
- **Sprint 11 Prep:** Use lessons to improve next Known Unknowns list

---

# Appendix: Task-to-Unknown Mapping

This table shows which prep tasks verify which unknowns:

| Prep Task | Unknowns Verified | Notes |
|-----------|-------------------|-------|
| **Task 1: Create Known Unknowns** | All unknowns | Creates this document with all 28 unknowns |
| **Task 2: Analyze circle.gms Chain** | 10.1.1 | Complete blocker chain for circle.gms (function calls primary, any secondary?) |
| **Task 3: Analyze himmel16.gms Chain** | 10.1.2, 10.4.1, 10.4.2 | Complete blocker chain + level bounds semantics research |
| **Task 4: Analyze maxmin.gms Chain** | 10.1.3, 10.5.1, 10.5.2, 10.5.3 | Complete blocker chain + nested indexing complexity assessment |
| **Task 5: Analyze mingamma.gms Chain** | 10.1.4, 10.6.1, 10.6.2 | Verify abort$ is blocker (not eq attrs) + syntax variations |
| **Task 6: Comma-Separated Research** | 10.2.1, 10.2.2, 10.2.3 | Pattern frequency, attribute handling, grammar scope |
| **Task 7: Function Call Survey** | 10.3.1, 10.3.2, 10.3.3, 10.3.4 | Evaluation strategy, nesting, validation, argument types |
| **Task 8: Nested Indexing Research** | 10.5.1, 10.5.2, 10.5.3, 10.5.4, 10.5.5 | **CRITICAL DECISION:** Implement or defer? Complexity + semantics + alternatives |
| **Task 9: Synthetic Test Framework** | 10.7.1 | Design principles for isolated feature tests |
| **Task 10: Validate Sprint 9 Features** | 10.7.2 | Verify i++1, eq attrs, model sections work in isolation |
| **Task 11: Checkpoint Infrastructure** | 10.1.6 | Validates parse rate calculation accuracy |
| **Task 12: Sprint 10 Schedule** | 10.5.5, 10.1.7 | Integrates all findings, blocker order, defer decision |

### Cross-Task Dependencies

**Blocker Detection Methodology (Unknown 10.1.5):**
- Validated through Tasks 2-5 execution
- If method works: all secondary blockers found during prep
- If method fails: discover tertiary blockers during sprint (should be zero)

**Blocker Interactions (Unknown 10.1.7):**
- Analyzed across Tasks 2-5 findings
- Task 12 uses to determine implementation order

**Semantic vs Parse Errors (Unknown 10.1.8):**
- Determined during Tasks 2-5 error analysis
- Affects implementation approach for each feature

### Unknown Prioritization

**Must Verify Before Day 1 (Critical):**
- 10.1.1 (circle complete chain)
- 10.1.2 (himmel16 secondary blocker)
- 10.1.3 (maxmin complete chain)
- 10.3.1 (function call evaluation strategy)
- 10.4.1 (level bound root cause)
- 10.5.1 (nested indexing complexity - **GO/NO-GO DECISION**)
- 10.7.2 (Sprint 9 features work)

**Should Verify Before Day 1 (High):**
- 10.1.4 (mingamma correct blocker)
- 10.2.2 (comma-separated with attributes)
- 10.3.2 (function call nesting)
- 10.4.2 (level attribute GAMS semantics)
- 10.5.2 (subset domain semantics)
- 10.6.1 (abort$ syntax variations)
- 10.7.1 (synthetic test design)

**Can Verify During Sprint (Medium/Low):**
- All other unknowns (implementation details, process improvements, metrics)

---

**Last Updated:** November 23, 2025  
**Document Version:** 1.0 (Pre-Sprint 10)  
**Next Review:** Sprint 10 Day 1 (after all prep tasks complete)  
**Status:** 🔍 Active - Unknowns being researched during prep phase
