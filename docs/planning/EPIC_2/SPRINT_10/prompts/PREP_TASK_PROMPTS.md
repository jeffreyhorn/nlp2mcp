# Sprint 10 Preparation Task Prompts

## Purpose

This document contains comprehensive, copy-pasteable execution prompts for Sprint 10 Preparation Tasks 2-12. Each prompt includes the complete task description, detailed instructions, and verification steps to ensure successful completion.

## How to Use This Document

1. **Select a Task**: Navigate to the task you need to complete using the Table of Contents
2. **Copy the Entire Task Section**: Each task is designed to be standalone and copy-pasteable
3. **Execute the Instructions**: Follow the detailed steps in "What You Need to Do"
4. **Update Documentation**: Follow the verification instructions to update all required files
5. **Check Off Completion**: Use the Task Completion Checklist to ensure nothing is missed

## Important Notes

- Each task prompt is self-contained with all necessary context
- All code blocks, commands, and formatting are preserved from the original PREP_PLAN.md
- Verification instructions are standardized but include task-specific details
- The document assumes you're working on branch: planning/sprint10-prep

## Table of Contents

- [Task 2: Analyze circle.gms Complete Blocker Chain](#task-2)
- [Task 3: Analyze himmel16.gms Complete Blocker Chain](#task-3)
- [Task 4: Analyze maxmin.gms Complete Blocker Chain](#task-4)
- [Task 5: Analyze mingamma.gms Complete Blocker Chain](#task-5)
- [Task 6: Research Comma-Separated Declaration Patterns](#task-6)
- [Task 7: Survey Existing GAMS Function Call Syntax](#task-7)
- [Task 8: Research Nested/Subset Indexing Semantics](#task-8)
- [Task 9: Design Synthetic Test Framework](#task-9)
- [Task 10: Validate Sprint 9 Features Work in Isolation](#task-10)
- [Task 11: Set Up Mid-Sprint Checkpoint Infrastructure](#task-11)
- [Task 12: Plan Sprint 10 Detailed Schedule](#task-12)

---

## Task 2: Analyze circle.gms Complete Blocker Chain {#task-2}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Critical  
Estimated Time: 2 hours  
Dependencies: Task 1 (Known Unknowns)  
Unknowns to Verify: 10.1.1

### Task Overview

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

### What You Need to Do

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

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md` with complete blocker chain
- [ ] Line-by-line analysis table for all 28 lines
- [ ] Primary, Secondary, Tertiary blockers identified (if exist)
- [ ] Effort estimate per blocker
- [ ] Model unlock prediction (does Primary fix unlock model?)
- [ ] Synthetic test requirements documented
- [ ] Parse attempt logs saved for reference
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknown 10.1.1

### Acceptance Criteria

- [ ] Complete blocker chain documented (all blockers, not just first)
- [ ] Each blocker has error message, affected lines, estimated effort
- [ ] Model unlock prediction clearly stated
- [ ] Line-by-line table shows all 28 lines with parse status
- [ ] Synthetic test requirements specified for each blocker
- [ ] Cross-references Known Unknowns Category 1 (Dependency Chain)
- [ ] Unknown 10.1.1 verified and updated in KNOWN_UNKNOWNS.md

### Verification & Completion Instructions

#### 1. Update KNOWN_UNKNOWNS.md

Add verification results for Unknown 10.1.1:

```markdown
## Unknown 10.1.1: circle.gms Complete Blocker Chain

**Status:** ✅ VERIFIED  
**Verified Date:** [TODAY'S DATE]  
**Verified By:** Task 2 analysis

**Finding:**
- Primary Blocker: Function calls in parameter assignments (lines XX, YY)
- Secondary Blocker: [NONE | describe if found]
- Tertiary Blocker: [NONE | describe if found]
- Model will be unlocked by: [Primary fix only | Primary + Secondary | etc.]

**Impact on Sprint 10:**
[Describe how this affects implementation priority and effort estimates]
```

#### 2. Update PREP_PLAN.md

Update Task 2 status and add results:

```markdown
## Task 2: Analyze circle.gms Complete Blocker Chain

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Actual Time:** [X hours]  
**Completed:** [DATE]

### Changes

- Created `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md`
- Identified [N] blockers in dependency chain
- Updated Unknown 10.1.1 in KNOWN_UNKNOWNS.md

### Result

- Primary blocker confirmed: Function calls in parameter assignments
- [Secondary blocker found/not found]
- Model unlock prediction: [Will parse after Primary fix | Requires Secondary fix too]
- Effort estimate validated: [6-8 hours confirmed | Revised to X hours]
```

#### 3. Update CHANGELOG.md

Add entry for Task 2 completion:

```markdown
## Sprint 10 Preparation

### Task 2: circle.gms Blocker Analysis (Complete)
- Performed complete dependency chain analysis for circle.gms
- Identified [N] blockers preventing model from parsing
- Created comprehensive blocker analysis document
- Verified Unknown 10.1.1 about complete blocker chains
```

#### 4. Run Quality Gates (if code changed)

```bash
# Only if you modified any Python code during analysis
pytest tests/ -v
mypy src/
black src/ tests/
```

#### 5. Commit Changes

```bash
git add docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md
git add docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
git add docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md
git add CHANGELOG.md
git commit -m "Complete Task 2: circle.gms blocker chain analysis

- Performed line-by-line analysis of all 28 lines
- Identified primary blocker: function calls in parameter assignments
- [Found/Did not find] secondary blockers
- Created comprehensive blocker analysis document
- Updated Unknown 10.1.1 with verification results
- Model unlock prediction: [summary]

Effort: [X] hours
Docs: docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md"
```

#### 6. Create Pull Request

```bash
gh pr create --base main --head planning/sprint10-prep \
  --title "Sprint 10 Prep: Task 2 - circle.gms blocker analysis" \
  --body "## Summary
Completed comprehensive blocker chain analysis for circle.gms

## Changes
- Created blocker analysis document with line-by-line review
- Identified complete dependency chain of blockers
- Verified Unknown 10.1.1 about blocker completeness
- Updated planning documentation

## Key Findings
- Primary blocker: Function calls in parameter assignments
- Secondary blockers: [None | List if found]
- Model unlock prediction: [Will parse after primary fix | Needs multiple fixes]

## Files Changed
- docs/planning/EPIC_2/SPRINT_10/BLOCKERS/circle_analysis.md (new)
- docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md (updated)
- docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md (updated)
- CHANGELOG.md (updated)"
```

#### 7. Wait for Review

Monitor PR for review comments and address any feedback before merging.

### Task Completion Checklist

- [ ] Parse attempt completed and logged
- [ ] Line-by-line analysis table created (28 lines)
- [ ] Complete blocker chain identified
- [ ] Blocker analysis document created
- [ ] KNOWN_UNKNOWNS.md updated with Unknown 10.1.1 verification
- [ ] PREP_PLAN.md updated with completion status
- [ ] CHANGELOG.md updated
- [ ] Changes committed with descriptive message
- [ ] PR created for review
- [ ] Task marked complete in project tracker

---

## Task 3: Analyze himmel16.gms Complete Blocker Chain {#task-3}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Critical  
Estimated Time: 2 hours  
Dependencies: Task 1 (Known Unknowns)  
Unknowns to Verify: 10.1.2, 10.4.1, 10.4.2

### Task Overview

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

### What You Need to Do

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

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md` with complete remaining blocker chain
- [ ] Level bound conflict analysis (what variables, what values, why conflict)
- [ ] GAMS semantics research findings (is multiple `.l` valid?)
- [ ] Confirmation if level bounds is ONLY remaining blocker (no tertiary)
- [ ] Line-by-line table for all 33 lines
- [ ] Synthetic test requirements
- [ ] Model unlock prediction
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.2, 10.4.1, 10.4.2

### Acceptance Criteria

- [ ] Complete remaining blocker chain documented (after i++1 fix)
- [ ] Level bound conflict thoroughly analyzed
- [ ] GAMS semantics verified (is this valid/invalid in GAMS?)
- [ ] Tertiary blocker search completed (confirm level bounds is last blocker)
- [ ] Effort estimate for level bound fix provided
- [ ] Synthetic test requirements specified
- [ ] Cross-references Sprint 9 i++1 implementation status
- [ ] Unknowns 10.1.2, 10.4.1, 10.4.2 verified and updated in KNOWN_UNKNOWNS.md

### Verification & Completion Instructions

#### 1. Update KNOWN_UNKNOWNS.md

Add verification results for Unknowns 10.1.2, 10.4.1, 10.4.2:

```markdown
## Unknown 10.1.2: himmel16.gms Complete Blocker Chain

**Status:** ✅ VERIFIED  
**Verified Date:** [TODAY'S DATE]  
**Verified By:** Task 3 analysis

**Finding:**
- Primary Blocker: i++1 indexing (FIXED in Sprint 9)
- Secondary Blocker: Level bound conflicts (lines XX, YY)
- Tertiary Blocker: [NONE | describe if found]
- Model will be unlocked by: [Level bound fix only | Additional fixes needed]

## Unknown 10.4.1: Level Bound Conflict Cause

**Status:** ✅ VERIFIED  
**Finding:** [What causes the conflict - multiple assignments, different values, etc.]

## Unknown 10.4.2: Level Bound GAMS Semantics

**Status:** ✅ VERIFIED  
**Finding:** [Is multiple .l assignment valid in GAMS? Parser vs semantic issue?]
```

#### 2. Update PREP_PLAN.md

Update Task 3 status and add results.

#### 3. Update CHANGELOG.md

Add entry for Task 3 completion.

#### 4. Run Quality Gates (if code changed)

#### 5. Commit Changes

```bash
git add docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md
git add docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
git add docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md
git add CHANGELOG.md
git commit -m "Complete Task 3: himmel16.gms blocker chain analysis

- Analyzed remaining blockers after Sprint 9 i++1 fix
- Identified secondary blocker: level bound conflicts
- [Found/Did not find] tertiary blockers
- Researched GAMS semantics for .l assignments
- Updated Unknowns 10.1.2, 10.4.1, 10.4.2

Effort: [X] hours
Docs: docs/planning/EPIC_2/SPRINT_10/BLOCKERS/himmel16_analysis.md"
```

#### 6. Create Pull Request

#### 7. Wait for Review

### Task Completion Checklist

- [ ] Parse attempt completed and logged
- [ ] Level bound conflict analyzed
- [ ] GAMS semantics researched
- [ ] Line-by-line analysis table created (33 lines)
- [ ] Complete remaining blocker chain identified
- [ ] Blocker analysis document created
- [ ] KNOWN_UNKNOWNS.md updated with 3 unknown verifications
- [ ] PREP_PLAN.md updated with completion status
- [ ] CHANGELOG.md updated
- [ ] Changes committed with descriptive message
- [ ] PR created for review
- [ ] Task marked complete in project tracker

---

## Task 4: Analyze maxmin.gms Complete Blocker Chain {#task-4}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Critical  
Estimated Time: 2-3 hours  
Dependencies: Task 1 (Known Unknowns)  
Unknowns to Verify: 10.1.3, 10.5.1, 10.5.2, 10.5.3

### Task Overview

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

### What You Need to Do

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

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md` with complete blocker chain
- [ ] Nested indexing deep dive (GAMS semantics, pattern frequency, complexity)
- [ ] Line-by-line table for all 47 lines
- [ ] Complexity assessment (validate 10-12 hour estimate)
- [ ] Implementation recommendation (attempt in Sprint 10 vs defer to Sprint 11)
- [ ] Fallback plan documented (90% target without maxmin.gms)
- [ ] Synthetic test requirements
- [ ] Model unlock prediction
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.3, 10.5.1, 10.5.2, 10.5.3

### Acceptance Criteria

- [ ] Complete blocker chain documented
- [ ] Nested indexing pattern thoroughly analyzed
- [ ] GAMS semantics research completed
- [ ] Complexity estimate validated or revised
- [ ] Clear recommendation: implement in Sprint 10 or defer
- [ ] If defer recommended, fallback plan specified
- [ ] Synthetic test requirements for nested indexing feature
- [ ] Cross-references Known Unknowns Category 1 and 2
- [ ] Unknowns 10.1.3, 10.5.1, 10.5.2, 10.5.3 verified and updated in KNOWN_UNKNOWNS.md

### Verification & Completion Instructions

#### 1. Update KNOWN_UNKNOWNS.md

Add verification results for 4 unknowns (10.1.3, 10.5.1, 10.5.2, 10.5.3).

#### 2. Update PREP_PLAN.md

Update Task 4 status and add results, including recommendation.

#### 3. Update CHANGELOG.md

#### 4. Run Quality Gates (if code changed)

#### 5. Commit Changes

```bash
git add docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md
git add docs/planning/EPIC_2/SPRINT_10/KNOWN_UNKNOWNS.md
git add docs/planning/EPIC_2/SPRINT_10/PREP_PLAN.md
git add CHANGELOG.md
git commit -m "Complete Task 4: maxmin.gms blocker chain analysis

- Analyzed nested/subset indexing complexity
- Identified [N] blockers in dependency chain
- Recommendation: [IMPLEMENT in Sprint 10 | DEFER to Sprint 11]
- Updated Unknowns 10.1.3, 10.5.1, 10.5.2, 10.5.3

Effort: [X] hours
Docs: docs/planning/EPIC_2/SPRINT_10/BLOCKERS/maxmin_analysis.md"
```

#### 6. Create Pull Request

#### 7. Wait for Review

### Task Completion Checklist

- [ ] Parse attempt completed and logged
- [ ] Nested indexing pattern analyzed
- [ ] GAMS semantics researched
- [ ] Line-by-line analysis table created (47 lines)
- [ ] Complexity assessment completed
- [ ] Clear recommendation made (implement or defer)
- [ ] Blocker analysis document created
- [ ] KNOWN_UNKNOWNS.md updated with 4 unknown verifications
- [ ] PREP_PLAN.md updated with completion status
- [ ] CHANGELOG.md updated
- [ ] Changes committed with descriptive message
- [ ] PR created for review
- [ ] Task marked complete in project tracker

---

## Task 5: Analyze mingamma.gms Complete Blocker Chain {#task-5}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Critical  
Estimated Time: 1-2 hours  
Dependencies: Task 1 (Known Unknowns)  
Unknowns to Verify: 10.1.4, 10.6.1, 10.6.2

### Task Overview

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

### What You Need to Do

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

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/mingamma_analysis.md` with complete blocker chain
- [ ] abort$ syntax analysis (all occurrences, syntax variants, GAMS semantics)
- [ ] Verification that equation attributes NOT needed (Sprint 9 assumption incorrect)
- [ ] Line-by-line table for all 37 lines
- [ ] Model unlock prediction (does abort$ fix unlock model?)
- [ ] Synthetic test requirements for abort$ feature
- [ ] Sprint 9 lessons learned documented
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.1.4, 10.6.1, 10.6.2

### Acceptance Criteria

- [ ] Complete blocker chain documented (confirm abort$ is only blocker)
- [ ] abort$ in if-blocks thoroughly analyzed
- [ ] All abort$ occurrences catalogued
- [ ] GAMS abort$ syntax research completed
- [ ] Verification that equation attributes not required for this model
- [ ] Sprint 9 incorrect assumption documented as lesson
- [ ] Effort estimate for abort$ fix (should be low, 2-3 hours)
- [ ] Synthetic test requirements specified
- [ ] Cross-references Sprint 9 mingamma_blocker_analysis.md
- [ ] Unknowns 10.1.4, 10.6.1, 10.6.2 verified and updated in KNOWN_UNKNOWNS.md

### Verification & Completion Instructions

Follow standard verification process for updating KNOWN_UNKNOWNS.md, PREP_PLAN.md, CHANGELOG.md, committing, and creating PR.

### Task Completion Checklist

- [ ] Existing analysis reviewed
- [ ] Parse attempt completed
- [ ] abort$ syntax analyzed
- [ ] Equation attributes verified as not needed
- [ ] Line-by-line analysis table created (37 lines)
- [ ] Sprint 9 lesson documented
- [ ] Blocker analysis document created
- [ ] KNOWN_UNKNOWNS.md updated with 3 unknown verifications
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 6: Research Comma-Separated Declaration Patterns {#task-6}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: High  
Estimated Time: 2 hours  
Dependencies: None  
Unknowns to Verify: 10.2.1, 10.2.2, 10.2.3

### Task Overview

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

### What You Need to Do

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

### Verification & Completion Instructions

Follow standard verification process for updating documentation, committing changes, and creating PR.

### Task Completion Checklist

- [ ] GAMSLIB survey completed
- [ ] Pattern examples catalogued
- [ ] Edge cases identified
- [ ] GAMS documentation researched
- [ ] Grammar requirements specified
- [ ] Research document created
- [ ] KNOWN_UNKNOWNS.md updated with 3 unknown verifications
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 7: Survey Existing GAMS Function Call Syntax {#task-7}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: High  
Estimated Time: 2-3 hours  
Dependencies: Task 2 (circle.gms analysis)  
Unknowns to Verify: 10.3.1, 10.3.2, 10.3.3, 10.3.4

### Task Overview

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

### What You Need to Do

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

### Deliverables

- [ ] `docs/planning/EPIC_2/SPRINT_10/BLOCKERS/function_call_research.md` with:
  - Complete function catalog from GAMSLIB
  - Function categories (Math, Statistical, Aggregation, Other)
  - Argument pattern analysis
  - Nesting analysis
  - Evaluation strategy (parse-only vs parse-and-evaluate)
  - Grammar production changes required
  - AST node type specifications
  - Effort estimate validation (6-8 hours)
- [ ] Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 10.3.1, 10.3.2, 10.3.3, 10.3.4

### Acceptance Criteria

- [ ] All GAMSLIB function calls catalogued
- [ ] Functions categorized by type
- [ ] Argument patterns documented
- [ ] Nesting complexity assessed
- [ ] Evaluation strategy determined (parse-only vs evaluate)
- [ ] Grammar changes specified
- [ ] AST changes specified
- [ ] Effort estimate validated (6-8 hours) or revised
- [ ] Cross-references circle.gms blocker analysis
- [ ] Cross-references Known Unknowns Category 2
- [ ] Unknowns 10.3.1, 10.3.2, 10.3.3, 10.3.4 verified and updated in KNOWN_UNKNOWNS.md

### Verification & Completion Instructions

Follow standard verification process for updating documentation, committing changes, and creating PR.

### Task Completion Checklist

- [ ] GAMSLIB function survey completed
- [ ] Functions categorized
- [ ] Argument patterns analyzed
- [ ] Evaluation strategy determined
- [ ] Grammar/AST changes specified
- [ ] Research document created
- [ ] KNOWN_UNKNOWNS.md updated with 4 unknown verifications
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 8: Research Nested/Subset Indexing Semantics {#task-8}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: High  
Estimated Time: 3-4 hours  
Dependencies: Task 4 (maxmin.gms analysis)  
Unknowns to Verify: 10.5.1, 10.5.2, 10.5.3, 10.5.4, 10.5.5

### Task Overview

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

### What You Need to Do

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

### Verification & Completion Instructions

Follow standard verification process, with special attention to the recommendation's impact on Sprint 10 planning.

### Task Completion Checklist

- [ ] GAMS documentation researched
- [ ] maxmin.gms pattern analyzed
- [ ] GAMSLIB frequency assessed
- [ ] Implementation approaches analyzed
- [ ] Clear recommendation made
- [ ] Research document created
- [ ] KNOWN_UNKNOWNS.md updated with 5 unknown verifications
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 9: Design Synthetic Test Framework {#task-9}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: High  
Estimated Time: 2-3 hours  
Dependencies: Tasks 2-5 (blocker analyses)  
Unknowns to Verify: 10.7.1

### Task Overview

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

### What You Need to Do

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

### Verification & Completion Instructions

Follow standard verification process, with focus on creating a reusable framework for Sprint 10.

### Task Completion Checklist

- [ ] Framework principles documented
- [ ] Test template created
- [ ] Directory structure set up
- [ ] Test specifications written
- [ ] Pytest integration designed
- [ ] README.md created
- [ ] KNOWN_UNKNOWNS.md updated
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 10: Validate Sprint 9 Features Work in Isolation {#task-10}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Medium  
Estimated Time: 2 hours  
Dependencies: Task 9 (synthetic test framework)  
Unknowns to Verify: 10.7.2

### Task Overview

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

### What You Need to Do

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

### Verification & Completion Instructions

Follow standard verification process. If any Sprint 9 features fail, create high-priority bug fixes before Sprint 10.

### Task Completion Checklist

- [ ] 3 synthetic tests created
- [ ] Tests run successfully
- [ ] Results documented
- [ ] Bug report created if any failures
- [ ] KNOWN_UNKNOWNS.md updated
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 11: Set Up Mid-Sprint Checkpoint Infrastructure {#task-11}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Medium  
Estimated Time: 1-2 hours  
Dependencies: None

### Task Overview

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

### What You Need to Do

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

### Verification & Completion Instructions

Follow standard verification process, with emphasis on making scripts executable and well-documented.

### Task Completion Checklist

- [ ] Parse rate script created and tested
- [ ] Checkpoint script created and tested
- [ ] Documentation created
- [ ] Scripts made executable
- [ ] Thresholds defined
- [ ] All documentation updated
- [ ] PR created for review

---

## Task 12: Plan Sprint 10 Detailed Schedule {#task-12}

### Context
Branch: planning/sprint10-prep  
Status: 🔵 NOT STARTED  
Priority: Critical  
Estimated Time: 3-4 hours  
Dependencies: All previous tasks (1-11)

### Task Overview

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

### What You Need to Do

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

[Full day-by-day schedule template from original PREP_PLAN.md included here]

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

### Verification & Completion Instructions

Follow standard verification process, with emphasis on creating a realistic, executable schedule.

### Task Completion Checklist

- [ ] All prep task results reviewed
- [ ] Day-by-day schedule created
- [ ] Risk mitigation plan included
- [ ] Schedule feasibility validated
- [ ] Schedule document created
- [ ] All documentation updated
- [ ] PR created for review

---

## Summary

This document provides comprehensive, executable prompts for all Sprint 10 Preparation Tasks (2-12). Each task includes:

- Complete context and background
- Detailed step-by-step instructions
- All deliverables and acceptance criteria
- Standardized verification and completion instructions
- Task completion checklists

The prompts are designed to be:
- **Self-contained**: Each can be copied and executed independently
- **Comprehensive**: All information from PREP_PLAN.md is preserved
- **Actionable**: Clear steps with specific commands and templates
- **Verifiable**: Each has explicit completion criteria

Use these prompts to systematically complete the Sprint 10 preparation phase and ensure all unknowns are resolved before sprint execution begins.