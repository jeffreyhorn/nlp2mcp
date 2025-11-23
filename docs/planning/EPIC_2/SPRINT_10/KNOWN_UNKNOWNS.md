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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 2)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 3)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 4)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 5)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 6)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 6)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 6)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 7)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 7)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 7)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 7)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 3)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 3)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 8)  
**Decision required before Sprint 10 Day 1**

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 8)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 8)

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
🔍 **Status: INCOMPLETE**  
To be completed during prep phase (Task 5)

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
🔍 **Status: INCOMPLETE**  
To be validated during Task 5

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
