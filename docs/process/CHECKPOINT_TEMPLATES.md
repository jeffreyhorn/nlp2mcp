# Sprint Checkpoint Templates

## Overview

This document provides formal checkpoint templates for sprint execution. These checkpoints enable systematic mid-sprint reviews to catch issues early and make informed go/no-go decisions.

**Purpose:** Address Sprint 3 Retrospective Action 3.1: "Mid-sprint checkpoints were ad-hoc, not systematic"

**Checkpoints:**
- **Checkpoint 1:** Day 3 (New Features Initial Implementation)
- **Checkpoint 2:** Day 6 (Mid-Sprint Progress Review)
- **Checkpoint 3:** Day 8 (Pre-Completion Review)

---

## Checkpoint 1: Day 3 (New Features Initial Implementation)

### When/Duration/Format
- **When:** End of Day 3
- **Duration:** 30-45 minutes
- **Format:** Solo review with written report

### Review Questions

#### 1. Feature Completeness
- Are all new features from sprint plan at least scaffolded?
- Are function signatures defined and documented?
- Are test files created (even if tests are pending)?
- Are there any features not yet started?

#### 2. Known Unknowns Status
- Have any Known Unknowns been discovered during implementation?
- Are any assumptions made in planning proving incorrect?
- Do any features require research that wasn't anticipated?
- Are there any blockers that need immediate attention?

#### 3. Test Coverage
- Do all new functions have at least one test?
- Are happy path tests written and passing?
- What is current coverage percentage for new code?
- Are any features untestable in current form?

#### 4. Code Quality
- Does code pass mypy type checking?
- Does code pass ruff linting?
- Is code formatted with black?
- Are there any technical debt items accumulating?

### Artifacts to Review
- `pytest` output (all tests)
- `mypy` output (type checking)
- `ruff` output (linting)
- `pytest --cov` output (coverage report)
- Git diff/commit history since sprint start
- Documentation updates

### Acceptance Criteria
**PASS if ALL of the following are true:**
- [ ] All planned features are scaffolded
- [ ] All new functions have signatures and docstrings
- [ ] Test files exist for all new modules
- [ ] No new Known Unknowns discovered (or documented if found)
- [ ] Code passes mypy without errors
- [ ] Code passes ruff without errors
- [ ] Test coverage >= 70% for new code
- [ ] All existing tests still pass

**FAIL if ANY of the following are true:**
- [ ] Any planned feature not started
- [ ] Known Unknown discovered that blocks progress
- [ ] Type errors exist
- [ ] Test coverage < 70% for new code

### Decision Point

**GO:** Continue with implementation
- All acceptance criteria pass
- Sprint is on track for Day 10 completion

**NO-GO:** Stop and fix issues
- Any FAIL condition met
- Recovery plan required before proceeding

**Recovery Plan Template:**
```
Issue: [Describe what failed]
Impact: [How this affects sprint goals]
Fix Required: [Specific actions needed]
Time Estimate: [Hours to fix]
Revised Timeline: [Updated sprint schedule]
```

### Checkpoint 1 Report Template

```markdown
# Checkpoint 1 Report - Day 3

**Date:** [YYYY-MM-DD]
**Sprint:** [Sprint Number]
**Reviewer:** [Your Name]

## Feature Completeness Status
- [ ] All features scaffolded
- [ ] Function signatures defined
- [ ] Test files created

**Not Started:** [List any features not started]
**Blockers:** [List any blockers]

## Known Unknowns
**New Unknowns Discovered:** [Yes/No]
- [List any new unknowns with brief description]

**Assumptions Incorrect:** [Yes/No]
- [List any incorrect assumptions]

## Test Coverage
- **New Code Coverage:** [X]%
- **Tests Passing:** [X/Y]
- **Tests Written:** [X]
- **Untestable Features:** [List any]

## Code Quality
- **mypy:** [Pass/Fail] - [X errors]
- **ruff:** [Pass/Fail] - [X errors]
- **black:** [Pass/Fail]

## Decision
- [ ] GO - Continue with implementation
- [ ] NO-GO - Stop and fix issues

**Justification:** [Brief explanation]

## Recovery Plan (if NO-GO)
**Issue:** [Description]
**Fix Required:** [Actions]
**Time Estimate:** [Hours]
**Revised Timeline:** [Updated schedule]

## Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

---

## Checkpoint 2: Day 6 (Mid-Sprint Progress Review)

### When/Duration/Format
- **When:** End of Day 6
- **Duration:** 45-60 minutes
- **Format:** Solo review with written report

### Review Questions

#### 1. Feature Completeness
- Are all features at least 80% implemented?
- Are all core functions working (even if edge cases remain)?
- Are any features falling behind schedule?
- Are there any features that need to be descoped?

#### 2. Known Unknowns Status
- Have all Known Unknowns from planning been addressed?
- Are any unknowns taking longer to resolve than expected?
- Have any new unknowns emerged that could derail sprint?
- Is research documentation complete for resolved unknowns?

#### 3. Test Coverage
- Are all happy path tests written and passing?
- Are edge case tests at least 50% complete?
- What is current coverage percentage for all new code?
- Are integration tests written and passing?

#### 4. Code Quality
- Does code pass all quality checks (mypy, ruff, black)?
- Are docstrings complete and accurate?
- Is technical debt being managed or accumulating?
- Are there any refactoring needs identified?

### Artifacts to Review
- `pytest` output (all tests)
- `mypy` output (type checking)
- `ruff` output (linting)
- `pytest --cov` output (coverage report)
- Git diff/commit history since Checkpoint 1
- Documentation updates
- KNOWN_UNKNOWNS.md status

### Acceptance Criteria
**PASS if ALL of the following are true:**
- [ ] All planned features >= 80% implemented
- [ ] All core functionality working
- [ ] All Known Unknowns resolved or have clear path to resolution
- [ ] Code passes mypy without errors
- [ ] Code passes ruff without errors
- [ ] Test coverage >= 85% for new code
- [ ] All existing tests still pass
- [ ] Documentation up to date

**FAIL if ANY of the following are true:**
- [ ] Any feature < 50% implemented
- [ ] Known Unknown blocking progress with no resolution plan
- [ ] Type errors exist
- [ ] Test coverage < 80% for new code
- [ ] Critical bugs discovered

### Decision Point

**GO:** Continue to completion
- All acceptance criteria pass
- Sprint is on track for Day 10 completion
- No major risks identified

**NO-GO:** Stop and replan
- Any FAIL condition met
- Sprint goals need adjustment
- Recovery plan or descoping required

**Descoping Decision Template:**
```
Feature to Descope: [Feature name]
Reason: [Why descoping is necessary]
Impact: [Effect on sprint goals]
Deferred To: [Future sprint or backlog]
Remaining Work: [What will still be completed]
```

### Checkpoint 2 Report Template

```markdown
# Checkpoint 2 Report - Day 6

**Date:** [YYYY-MM-DD]
**Sprint:** [Sprint Number]
**Reviewer:** [Your Name]

## Feature Completeness Status
- [ ] All features >= 80% implemented
- [ ] Core functionality working
- [ ] No features falling behind

**Implementation Progress:**
- [Feature 1]: [X]% complete
- [Feature 2]: [X]% complete
- [Feature 3]: [X]% complete

**Behind Schedule:** [List any features behind schedule]

## Known Unknowns
**Planning Unknowns Resolved:** [X/Y]
- [List any unresolved unknowns]

**New Unknowns Discovered:** [Yes/No]
- [List any new unknowns]

**Research Documentation:** [Complete/Incomplete]

## Test Coverage
- **New Code Coverage:** [X]%
- **Total Coverage:** [X]%
- **Tests Passing:** [X/Y]
- **Integration Tests:** [X/Y passing]
- **Edge Case Tests:** [X]% complete

## Code Quality
- **mypy:** [Pass/Fail] - [X errors]
- **ruff:** [Pass/Fail] - [X errors]
- **black:** [Pass/Fail]
- **Docstrings:** [Complete/Incomplete]
- **Technical Debt:** [Low/Medium/High]

## Decision
- [ ] GO - Continue to completion
- [ ] NO-GO - Stop and replan

**Justification:** [Brief explanation]

## Descoping Plan (if needed)
**Features to Descope:** [List]
**Reason:** [Explanation]
**Impact:** [Effect on goals]
**Deferred To:** [Future sprint/backlog]

## Recovery Plan (if NO-GO)
**Issue:** [Description]
**Fix Required:** [Actions]
**Time Estimate:** [Hours]
**Revised Timeline:** [Updated schedule]

## Risks Identified
1. [Risk 1 - mitigation plan]
2. [Risk 2 - mitigation plan]

## Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

---

## Checkpoint 3: Day 8 (Pre-Completion Review)

### When/Duration/Format
- **When:** End of Day 8
- **Duration:** 60-90 minutes
- **Format:** Solo review with written report

### Review Questions

#### 1. Feature Completeness
- Are all features 100% implemented (or descoped)?
- Do all features work correctly with all test cases?
- Are there any incomplete items that need sprint extension?
- Is the feature set ready for production use?

#### 2. Known Unknowns Status
- Have ALL Known Unknowns been resolved and documented?
- Is all research documentation complete and reviewed?
- Are any assumptions still unverified?
- Is KNOWN_UNKNOWNS.md updated and accurate?

#### 3. Test Coverage
- Are ALL tests written and passing?
- Are edge cases fully tested?
- Is coverage >= 85% for all new code?
- Are integration tests comprehensive?
- Have manual tests been performed?

#### 4. Code Quality
- Does code pass all quality checks with zero errors?
- Are all docstrings complete, accurate, and up to date?
- Is code review complete (self-review at minimum)?
- Are there any technical debt items to address?
- Is code ready for merge?

### Artifacts to Review
- `pytest` output (all tests, 100% passing)
- `mypy` output (zero errors)
- `ruff` output (zero errors)
- `pytest --cov` output (>= 85% coverage)
- Git diff/commit history for entire sprint
- All documentation updates
- KNOWN_UNKNOWNS.md final state
- Code self-review notes

### Acceptance Criteria
**PASS if ALL of the following are true:**
- [ ] All planned features 100% implemented (or properly descoped)
- [ ] All tests passing (100%)
- [ ] All Known Unknowns resolved and documented
- [ ] Code passes mypy with zero errors
- [ ] Code passes ruff with zero errors
- [ ] Test coverage >= 85% for new code
- [ ] All documentation complete and accurate
- [ ] Code self-review completed
- [ ] Sprint goals achieved

**FAIL if ANY of the following are true:**
- [ ] Any feature incomplete without descoping plan
- [ ] Any tests failing
- [ ] Any Known Unknowns unresolved
- [ ] Type errors or linting errors exist
- [ ] Test coverage < 85%
- [ ] Documentation incomplete

### Decision Point

**GO:** Complete sprint and merge
- All acceptance criteria pass
- Sprint goals achieved
- Code ready for production

**EXTEND:** Need 1-2 more days
- Minor items incomplete
- Extension plan clear and bounded
- Sprint goals still achievable

**NO-GO:** Sprint failed
- Major features incomplete
- Critical bugs exist
- Need to roll back or restart

**Sprint Extension Template:**
```
Extension Needed: [1 or 2 days]
Reason: [Why extension is necessary]
Remaining Work: [Specific items to complete]
Extension Goals: [What will be accomplished]
Final Deadline: [New completion date]
Risk: [Why extension vs. descoping]
```

### Checkpoint 3 Report Template

```markdown
# Checkpoint 3 Report - Day 8

**Date:** [YYYY-MM-DD]
**Sprint:** [Sprint Number]
**Reviewer:** [Your Name]

## Feature Completeness Status
- [ ] All features 100% implemented
- [ ] All features tested and working
- [ ] No incomplete items

**Feature Status:**
- [Feature 1]: [Complete/Incomplete/Descoped]
- [Feature 2]: [Complete/Incomplete/Descoped]
- [Feature 3]: [Complete/Incomplete/Descoped]

**Incomplete Items:** [List any incomplete items]
**Descoped Items:** [List any descoped items with justification]

## Known Unknowns
**All Unknowns Resolved:** [Yes/No]
- [List any unresolved unknowns]

**Research Documentation:** [Complete/Incomplete]
- [List any incomplete documentation]

**KNOWN_UNKNOWNS.md Updated:** [Yes/No]

## Test Coverage
- **New Code Coverage:** [X]%
- **Total Coverage:** [X]%
- **Tests Passing:** [X/Y] ([X]%)
- **Integration Tests:** [X/Y passing]
- **Edge Case Tests:** [Complete/Incomplete]
- **Manual Testing:** [Complete/Incomplete]

**Test Issues:** [List any test failures or gaps]

## Code Quality
- **mypy:** [Pass/Fail] - [X errors]
- **ruff:** [Pass/Fail] - [X errors]
- **black:** [Pass/Fail]
- **Docstrings:** [Complete/Incomplete]
- **Code Review:** [Complete/Incomplete]
- **Technical Debt:** [Low/Medium/High]

**Quality Issues:** [List any remaining issues]

## Documentation Status
- [ ] All new functions documented
- [ ] README updated
- [ ] Research docs complete
- [ ] KNOWN_UNKNOWNS.md updated
- [ ] Examples/tutorials updated (if applicable)

**Documentation Gaps:** [List any gaps]

## Sprint Goals Achievement
**Original Goals:**
1. [Goal 1] - [Achieved/Not Achieved]
2. [Goal 2] - [Achieved/Not Achieved]
3. [Goal 3] - [Achieved/Not Achieved]

**Goals Achievement Rate:** [X/Y] ([X]%)

## Decision
- [ ] GO - Complete sprint and merge
- [ ] EXTEND - Need 1-2 more days
- [ ] NO-GO - Sprint failed

**Justification:** [Brief explanation]

## Extension Plan (if EXTEND)
**Extension Needed:** [1-2 days]
**Reason:** [Explanation]
**Remaining Work:** [Specific items]
**Extension Goals:** [What will be accomplished]
**Final Deadline:** [Date]

## Sprint Retrospective Notes
**What Went Well:**
1. [Item 1]
2. [Item 2]

**What Needs Improvement:**
1. [Item 1]
2. [Item 2]

**Action Items for Next Sprint:**
1. [Action 1]
2. [Action 2]

## Next Steps
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]
```

---

## Using These Templates

### Setting Reminders

**Day 3 Checkpoint:**
```bash
# Set calendar reminder for end of Day 3
# Review time: 30-45 minutes
# Block off time in calendar
```

**Day 6 Checkpoint:**
```bash
# Set calendar reminder for end of Day 6
# Review time: 45-60 minutes
# Block off time in calendar
```

**Day 8 Checkpoint:**
```bash
# Set calendar reminder for end of Day 8
# Review time: 60-90 minutes
# Block off time in calendar
# This is critical - do not skip
```

### Best Practices

1. **Don't Skip Checkpoints:** Even if you feel you're "on track", do the formal review
2. **Be Honest:** The checkpoints only work if you're honest about what's failing
3. **Document Everything:** Write the report even if everything passes
4. **Act on NO-GO:** If you hit NO-GO, actually stop and fix issues
5. **Track Patterns:** Look for recurring issues across sprints
6. **Update Templates:** If a checkpoint question doesn't help, modify it

### Integration with Sprint Process

**Before Sprint Start:**
- Set all three checkpoint reminders in calendar
- Review checkpoint templates to remind yourself of expectations
- Plan time for checkpoint reviews in sprint schedule

**During Sprint:**
- Complete each checkpoint on schedule
- File checkpoint reports in sprint documentation folder
- Use checkpoint results to adjust daily plans

**After Sprint:**
- Review all checkpoint reports in retrospective
- Identify patterns across checkpoints
- Update templates based on what worked/didn't work

### Checkpoint Report Storage

Save checkpoint reports in:
```
docs/planning/SPRINT_[N]/
├── CHECKPOINT_1_REPORT.md
├── CHECKPOINT_2_REPORT.md
└── CHECKPOINT_3_REPORT.md
```

This creates a historical record for future reference and pattern analysis.
