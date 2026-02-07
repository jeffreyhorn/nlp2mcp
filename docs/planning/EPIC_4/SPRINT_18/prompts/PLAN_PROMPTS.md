# Sprint 18: GAMS Emission Fixes - Day-by-Day Execution Prompts

> **Sprint Duration**: 14 working days (~56h)
> **Epic**: 4 - Production Readiness
> **Baseline**: v1.1.0 — Parse 61/160, Translate 42/61, Solve 12/42
> **Target**: Parse 65/160, Solve ≥22, path_syntax_error ≤2

---

## Day 0: Sprint Initialization

### Branch
```
sprint18/day0-init
```

### Objective
Initialize Sprint 18 infrastructure, validate baseline metrics, and prepare development environment.

### Prerequisites
- [ ] Sprint 18 planning documents approved (PLAN.md, KNOWN_UNKNOWNS.md, PREP_PLAN.md)
- [ ] v1.1.0 tag exists and is accessible
- [ ] All Sprint 17 items merged to main
- [ ] Clean working directory on main branch

### Tasks
1. **Create Sprint 18 branch structure** (~0.5h)
   - Create sprint18/day0-init from main
   - Verify all planning documents are in place

2. **Validate baseline metrics** (~1h)
   - Run full pipeline test against v1.1.0
   - Confirm baseline: Parse 61/160, Translate 42/61, Solve 12/42
   - Document any deviations

3. **Initialize SPRINT_LOG.md** (~0.5h)
   - Create docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md
   - Record Day 0 activities and baseline confirmation

4. **Environment validation** (~0.5h)
   - Verify GAMS installation and license
   - Confirm all test dependencies installed
   - Run smoke test on sample model

### Deliverables
- [ ] Sprint branch created
- [ ] Baseline metrics confirmed and documented
- [ ] SPRINT_LOG.md initialized with Day 0 entry
- [ ] Development environment validated

### Quality Checks
```bash
# Validate baseline
python tests/gamslib/run_full_test.py

# Verify clean state
git status
```

### Completion Criteria
- [ ] Baseline metrics match expected values (Parse 61, Translate 42, Solve 12)
- [ ] SPRINT_LOG.md created with Day 0 entry including:
  - Sprint start timestamp
  - Baseline metrics confirmed
  - Environment validation results
- [ ] All quality checks pass

### PR & Review
- **PR Title**: `sprint18/day0-init: Sprint initialization and baseline validation`
- **PR Body**: Include baseline metrics table, environment validation results
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `initialization`

### Reference Documents
- PLAN.md: Lines 1-50 (Sprint Overview)
- PLAN.md: Lines 51-100 (Day 0 details)
- KNOWN_UNKNOWNS.md: Lines 1-50 (Risk overview)

---

## Day 1: Diagnostic Deep-Dive on Top Failures

### Branch
```
sprint18/day1-diagnostics
```

### Objective
Analyze top 10 failing models to identify root causes and prioritize fixes for maximum impact.

### Prerequisites
- [ ] Day 0 completed and merged
- [ ] Baseline metrics documented
- [ ] Access to GAMSLIB model files

### Tasks
1. **Identify top 10 failing models** (~1h)
   - Run pipeline to get failure list
   - Sort by error type frequency
   - Select representative failures for each category

2. **Analyze path_syntax_error failures** (~1.5h)
   - Examine models failing with path_syntax_error
   - Document AST patterns causing failures
   - Identify emit_gams.py code paths involved

3. **Analyze other emission failures** (~1.5h)
   - Review translate failures not related to path syntax
   - Categorize by error type (precedence, quoting, etc.)
   - Document patterns and proposed fixes

4. **Create prioritized fix list** (~1h)
   - Rank fixes by impact (models fixed per change)
   - Estimate effort for each fix
   - Document in SPRINT_LOG.md

### Deliverables
- [ ] Top 10 failing models identified and documented
- [ ] Root cause analysis for each failure category
- [ ] Prioritized fix list with impact estimates
- [ ] SPRINT_LOG.md updated with Day 1 findings

### Quality Checks
```bash
# Run diagnostics
python tests/gamslib/run_full_test.py --verbose

# Verify documentation
cat docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md
```

### Completion Criteria
- [ ] All top 10 failures analyzed with root causes documented
- [ ] Fix prioritization complete with effort estimates
- [ ] SPRINT_LOG.md updated with:
  - Day 1 diagnostic findings
  - Failure categorization
  - Prioritized fix list
- [ ] Clear plan for Day 2 implementation

### PR & Review
- **PR Title**: `sprint18/day1-diagnostics: Failure analysis and fix prioritization`
- **PR Body**: Include failure category breakdown, prioritized fix list
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `diagnostics`, `analysis`

### Reference Documents
- PLAN.md: Lines 101-150 (Day 1 details)
- KNOWN_UNKNOWNS.md: Lines 100-200 (Unknown 1.x - Emission issues)

---

## Day 2: Quick Wins - Low-Hanging Fruit Fixes

### Branch
```
sprint18/day2-quick-wins
```

### Objective
Implement straightforward fixes identified on Day 1 that have high impact with low risk.

### Prerequisites
- [ ] Day 1 completed and merged
- [ ] Prioritized fix list available
- [ ] Understanding of quick-win opportunities

### Tasks
1. **Implement quoting fixes** (~1.5h)
   - Fix string literal quoting in emit_gams.py
   - Handle edge cases identified in diagnostics
   - Add test cases for fixed patterns

2. **Fix simple precedence issues** (~1.5h)
   - Address operator precedence in expressions
   - Add parentheses where needed
   - Test affected models

3. **Address minor emission bugs** (~1h)
   - Fix any small bugs identified
   - Improve error messages where helpful
   - Document changes

4. **Run regression tests** (~1h)
   - Full pipeline test
   - Verify no regressions
   - Document metrics improvement

### Deliverables
- [ ] Quick-win fixes implemented in emit_gams.py
- [ ] Test cases added for each fix
- [ ] Metrics improvement documented
- [ ] SPRINT_LOG.md updated with Day 2 progress

### Quality Checks
```bash
# Run full test suite
python tests/gamslib/run_full_test.py

# Check for regressions
git diff --stat

# Verify test coverage
python -m pytest tests/ -v
```

### Completion Criteria
- [ ] At least 2-3 models newly passing
- [ ] No regressions in previously passing models
- [ ] All new code has test coverage
- [ ] SPRINT_LOG.md updated with:
  - Fixes implemented
  - Models fixed
  - Metrics delta

### PR & Review
- **PR Title**: `sprint18/day2-quick-wins: Low-risk emission fixes`
- **PR Body**: Include before/after metrics, list of fixed models
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `emit_gams`

### Reference Documents
- PLAN.md: Lines 151-200 (Day 2 details)
- src/nlp2mcp/emit_gams.py (emission logic)

---

## Day 3: Checkpoint 1 - Progress Assessment

### Branch
```
sprint18/day3-checkpoint1
```

### Objective
First checkpoint - assess progress, validate approach, and adjust plan if needed.

### Prerequisites
- [ ] Day 2 completed and merged
- [ ] Quick-win fixes deployed
- [ ] Current metrics available

### Tasks
1. **Run full metrics assessment** (~1h)
   - Execute complete pipeline test
   - Compare against baseline and targets
   - Document progress percentage

2. **Analyze fix effectiveness** (~1h)
   - Review which fixes had most impact
   - Identify patterns in remaining failures
   - Assess if approach is working

3. **Plan adjustment if needed** (~1h)
   - If behind target: identify blockers
   - If ahead: consider stretch goals
   - Update remaining day plans as needed

4. **Stakeholder update** (~0.5h)
   - Prepare checkpoint summary
   - Document risks and mitigations
   - Update SPRINT_LOG.md

### Deliverables
- [ ] Checkpoint 1 metrics report
- [ ] Progress assessment document
- [ ] Updated plan (if adjustments needed)
- [ ] SPRINT_LOG.md with checkpoint entry

### Quality Checks
```bash
# Full pipeline test
python tests/gamslib/run_full_test.py

# Generate metrics report
python tests/gamslib/run_full_test.py --report
```

### Completion Criteria
- [ ] **Target**: Solve ≥14 (baseline + 2)
- [ ] Progress on track or plan adjusted
- [ ] SPRINT_LOG.md updated with:
  - Checkpoint 1 metrics
  - Progress assessment
  - Any plan adjustments
- [ ] Clear path forward for Days 4-6

### PR & Review
- **PR Title**: `sprint18/day3-checkpoint1: First progress checkpoint`
- **PR Body**: Include metrics comparison table, progress assessment
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `checkpoint`

### Reference Documents
- PLAN.md: Lines 201-250 (Day 3 checkpoint details)
- PLAN.md: Lines 450-470 (Success criteria)

---

## Day 4: Path Syntax Error Fixes - Part 1

### Branch
```
sprint18/day4-path-syntax-1
```

### Objective
Begin addressing path_syntax_error failures - the primary blocker for solve count improvement.

### Prerequisites
- [ ] Day 3 checkpoint completed
- [ ] path_syntax_error patterns documented
- [ ] Understanding of emit_gams.py path handling

### Tasks
1. **Analyze path emission patterns** (~1h)
   - Review how paths are currently emitted
   - Identify incorrect patterns
   - Document expected vs actual output

2. **Implement path quoting fixes** (~2h)
   - Fix path string quoting in emit_gams.py
   - Handle Windows/Unix path differences
   - Add proper escaping

3. **Fix path concatenation issues** (~1.5h)
   - Address issues with path building
   - Fix separator handling
   - Test edge cases

4. **Add targeted tests** (~0.5h)
   - Create tests for path handling
   - Cover identified edge cases
   - Verify fixes

### Deliverables
- [ ] Path quoting fixes implemented
- [ ] Path concatenation fixes implemented
- [ ] New test cases for path handling
- [ ] SPRINT_LOG.md updated

### Quality Checks
```bash
# Run full test suite
python tests/gamslib/run_full_test.py

# Run path-specific tests
python -m pytest tests/ -k "path" -v

# Check path_syntax_error count
python tests/gamslib/run_full_test.py | grep path_syntax_error
```

### Completion Criteria
- [ ] path_syntax_error count reduced by at least 2
- [ ] No regressions in other error types
- [ ] Path handling tests passing
- [ ] SPRINT_LOG.md updated with:
  - Path fixes implemented
  - Error count reduction
  - Remaining path issues

### PR & Review
- **PR Title**: `sprint18/day4-path-syntax-1: Path emission fixes part 1`
- **PR Body**: Include path_syntax_error count before/after
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `path-syntax`

### Reference Documents
- PLAN.md: Lines 251-300 (Day 4 details)
- KNOWN_UNKNOWNS.md: Lines 200-300 (path_syntax_error unknowns)
- src/nlp2mcp/emit_gams.py: Path handling code

---

## Day 5: Path Syntax Error Fixes - Part 2

### Branch
```
sprint18/day5-path-syntax-2
```

### Objective
Continue path_syntax_error fixes, targeting remaining patterns and edge cases.

### Prerequisites
- [ ] Day 4 completed and merged
- [ ] Part 1 path fixes working
- [ ] Remaining path issues documented

### Tasks
1. **Address remaining path patterns** (~2h)
   - Fix additional path emission issues
   - Handle complex path expressions
   - Test model-specific cases

2. **Fix path in different contexts** (~1.5h)
   - Address paths in PUT statements
   - Fix paths in include directives
   - Handle paths in options

3. **Comprehensive path testing** (~1h)
   - Run all models with path usage
   - Document remaining issues
   - Create regression tests

4. **Update documentation** (~0.5h)
   - Document path handling approach
   - Update SPRINT_LOG.md
   - Note any known limitations

### Deliverables
- [ ] Remaining path fixes implemented
- [ ] Comprehensive path tests added
- [ ] Documentation updated
- [ ] SPRINT_LOG.md with Day 5 progress

### Quality Checks
```bash
# Full pipeline test
python tests/gamslib/run_full_test.py

# Verify path_syntax_error target
python tests/gamslib/run_full_test.py | grep -E "(path_syntax_error|Solve:)"
```

### Completion Criteria
- [ ] path_syntax_error ≤4 (progress toward ≤2 target)
- [ ] All identified path patterns addressed
- [ ] No regressions
- [ ] SPRINT_LOG.md updated with:
  - Day 5 fixes
  - Current path_syntax_error count
  - Remaining issues for Day 6

### PR & Review
- **PR Title**: `sprint18/day5-path-syntax-2: Path emission fixes part 2`
- **PR Body**: Include cumulative path_syntax_error reduction
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `path-syntax`

### Reference Documents
- PLAN.md: Lines 301-350 (Day 5 details)
- Day 4 PR for context on part 1 fixes

---

## Day 6: Checkpoint 2 - Mid-Sprint Assessment

### Branch
```
sprint18/day6-checkpoint2
```

### Objective
Mid-sprint checkpoint - comprehensive progress review and plan adjustment.

### Prerequisites
- [ ] Day 5 completed and merged
- [ ] Path syntax fixes deployed
- [ ] Current metrics available

### Tasks
1. **Comprehensive metrics review** (~1h)
   - Full pipeline test with detailed output
   - Compare against all targets
   - Calculate progress percentage

2. **Analyze remaining gaps** (~1.5h)
   - Identify models still failing
   - Categorize remaining issues
   - Assess effort to close gaps

3. **Risk assessment** (~1h)
   - Review KNOWN_UNKNOWNS.md
   - Update risk status
   - Identify any new risks

4. **Plan second half of sprint** (~0.5h)
   - Adjust Days 7-11 if needed
   - Prioritize remaining work
   - Update SPRINT_LOG.md

### Deliverables
- [ ] Checkpoint 2 metrics report
- [ ] Gap analysis document
- [ ] Risk assessment update
- [ ] Adjusted plan for Days 7-11

### Quality Checks
```bash
# Full pipeline test
python tests/gamslib/run_full_test.py

# Detailed failure report
python tests/gamslib/run_full_test.py --failures-only
```

### Completion Criteria
- [ ] **Target**: Solve ≥17 (50% of improvement)
- [ ] **Target**: path_syntax_error ≤4
- [ ] Mid-sprint assessment complete
- [ ] SPRINT_LOG.md updated with:
  - Checkpoint 2 metrics
  - Gap analysis
  - Updated plan if needed
  - Risk status

### PR & Review
- **PR Title**: `sprint18/day6-checkpoint2: Mid-sprint assessment`
- **PR Body**: Include progress chart, risk assessment, plan adjustments
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `checkpoint`

### Reference Documents
- PLAN.md: Lines 351-400 (Day 6 checkpoint details)
- KNOWN_UNKNOWNS.md: Full document for risk review

---

## Day 7: Expression Emission Fixes

### Branch
```
sprint18/day7-expressions
```

### Objective
Fix expression emission issues including operator precedence, function calls, and complex expressions.

### Prerequisites
- [ ] Day 6 checkpoint completed
- [ ] Expression issues identified from diagnostics
- [ ] Understanding of emit_gams.py expression handling

### Tasks
1. **Fix operator precedence** (~1.5h)
   - Review precedence handling in emit_gams.py
   - Add parentheses where needed
   - Handle edge cases

2. **Fix function call emission** (~1.5h)
   - Address issues with built-in functions
   - Fix argument emission
   - Handle nested calls

3. **Address complex expressions** (~1.5h)
   - Fix multi-operator expressions
   - Handle conditional expressions
   - Test with affected models

4. **Regression testing** (~0.5h)
   - Run full suite
   - Verify no new failures
   - Document improvements

### Deliverables
- [ ] Expression emission fixes implemented
- [ ] Tests for expression handling
- [ ] Models fixed documented
- [ ] SPRINT_LOG.md updated

### Quality Checks
```bash
# Run full test suite
python tests/gamslib/run_full_test.py

# Run expression-specific tests
python -m pytest tests/ -k "expression" -v
```

### Completion Criteria
- [ ] Expression-related failures reduced
- [ ] No regressions
- [ ] New expression tests passing
- [ ] SPRINT_LOG.md updated with:
  - Expression fixes implemented
  - Models fixed
  - Metrics improvement

### PR & Review
- **PR Title**: `sprint18/day7-expressions: Expression emission fixes`
- **PR Body**: Include before/after for expression-related failures
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `expressions`

### Reference Documents
- PLAN.md: Lines 401-430 (Day 7 details)
- src/nlp2mcp/emit_gams.py: Expression emission code

---

## Day 8: Statement Emission Fixes

### Branch
```
sprint18/day8-statements
```

### Objective
Fix statement emission issues including SET, PARAMETER, and other GAMS statement types.

### Prerequisites
- [ ] Day 7 completed and merged
- [ ] Statement issues identified
- [ ] Understanding of statement emission

### Tasks
1. **Fix SET statement emission** (~1.5h)
   - Address set definition issues
   - Fix set operation emission
   - Handle dynamic sets

2. **Fix PARAMETER emission** (~1.5h)
   - Address parameter declaration issues
   - Fix data assignment emission
   - Handle tables

3. **Fix other statement types** (~1.5h)
   - Address MODEL, SOLVE statements
   - Fix EQUATION emission
   - Handle VARIABLE declarations

4. **Integration testing** (~0.5h)
   - Test statement combinations
   - Verify model completeness
   - Document results

### Deliverables
- [ ] Statement emission fixes implemented
- [ ] Tests for statement handling
- [ ] Integration tests passing
- [ ] SPRINT_LOG.md updated

### Quality Checks
```bash
# Run full test suite
python tests/gamslib/run_full_test.py

# Check specific statement tests
python -m pytest tests/ -k "statement" -v
```

### Completion Criteria
- [ ] Statement-related failures reduced
- [ ] No regressions
- [ ] Integration tests passing
- [ ] SPRINT_LOG.md updated with:
  - Statement fixes implemented
  - Affected models
  - Progress toward targets

### PR & Review
- **PR Title**: `sprint18/day8-statements: Statement emission fixes`
- **PR Body**: Include statement fix summary, affected models
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `statements`

### Reference Documents
- PLAN.md: Lines 431-450 (Day 8 details)
- src/nlp2mcp/emit_gams.py: Statement emission code

---

## Day 9: Edge Cases and Corner Cases

### Branch
```
sprint18/day9-edge-cases
```

### Objective
Address edge cases and corner cases that weren't covered in earlier fixes.

### Prerequisites
- [ ] Day 8 completed and merged
- [ ] Edge cases identified from testing
- [ ] Understanding of remaining failures

### Tasks
1. **Analyze remaining failures** (~1h)
   - Review models still failing
   - Identify unique patterns
   - Categorize edge cases

2. **Fix model-specific issues** (~2h)
   - Address individual model quirks
   - Fix rare patterns
   - Handle special cases

3. **Improve error handling** (~1h)
   - Better error messages for unfixed cases
   - Graceful degradation where possible
   - Document limitations

4. **Comprehensive testing** (~1h)
   - Full regression suite
   - Edge case specific tests
   - Document coverage

### Deliverables
- [ ] Edge case fixes implemented
- [ ] Improved error handling
- [ ] Edge case documentation
- [ ] SPRINT_LOG.md updated

### Quality Checks
```bash
# Full pipeline test
python tests/gamslib/run_full_test.py

# Verify solve count progress
python tests/gamslib/run_full_test.py | grep "Solve:"
```

### Completion Criteria
- [ ] Known edge cases addressed
- [ ] Error handling improved
- [ ] No regressions
- [ ] SPRINT_LOG.md updated with:
  - Edge cases fixed
  - Known limitations
  - Progress status

### PR & Review
- **PR Title**: `sprint18/day9-edge-cases: Edge case and corner case fixes`
- **PR Body**: Include edge case summary, limitations documented
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `edge-cases`

### Reference Documents
- PLAN.md: Lines 451-470 (Day 9 details)
- Previous day PRs for context

---

## Day 10: Final Fixes and Optimization

### Branch
```
sprint18/day10-final-fixes
```

### Objective
Final implementation push - address any remaining fixable issues before final testing.

### Prerequisites
- [ ] Day 9 completed and merged
- [ ] Clear list of remaining issues
- [ ] Understanding of what's achievable

### Tasks
1. **Priority remaining fixes** (~2h)
   - Implement highest-impact remaining fixes
   - Focus on solve count improvement
   - Address path_syntax_error if not at target

2. **Code cleanup** (~1h)
   - Remove debug code
   - Clean up temporary workarounds
   - Ensure code quality

3. **Performance check** (~0.5h)
   - Verify no performance regression
   - Check emission speed
   - Document any concerns

4. **Prepare for final testing** (~0.5h)
   - Ensure all changes merged
   - Clean working directory
   - Update SPRINT_LOG.md

### Deliverables
- [ ] Final fixes implemented
- [ ] Code cleaned up
- [ ] Ready for final testing
- [ ] SPRINT_LOG.md updated

### Quality Checks
```bash
# Full pipeline test
python tests/gamslib/run_full_test.py

# Code quality check
python -m pytest tests/ -v
ruff check src/
```

### Completion Criteria
- [ ] All planned fixes implemented
- [ ] Code quality checks passing
- [ ] Ready for Day 11 final testing
- [ ] SPRINT_LOG.md updated with:
  - Final fixes summary
  - Pre-final-test metrics
  - Any remaining concerns

### PR & Review
- **PR Title**: `sprint18/day10-final-fixes: Final implementation fixes`
- **PR Body**: Include final fix summary, code cleanup notes
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `final`

### Reference Documents
- PLAN.md: Lines 471-490 (Day 10 details)
- All previous Sprint 18 PRs

---

## Day 11: Checkpoint 3 - Full Pipeline Retest

### Branch
```
sprint18/day11-checkpoint3
```

### Objective
Final checkpoint - comprehensive pipeline retest and success criteria validation.

### Prerequisites
- [ ] Day 10 completed and merged
- [ ] All fixes deployed
- [ ] Clean working directory

### Tasks
1. **Full pipeline retest** (~1.5h)
   - Run complete test suite
   - Capture all metrics
   - Compare against targets

2. **Success criteria validation** (~1h)
   - Verify Solve ≥22 (target)
   - Verify path_syntax_error ≤2 (target)
   - Document any gaps

3. **Failure analysis** (~1h)
   - Document remaining failures
   - Categorize as fixable vs out-of-scope
   - Note for future sprints

4. **Final metrics report** (~0.5h)
   - Create comprehensive report
   - Compare baseline to final
   - Update SPRINT_LOG.md

### Deliverables
- [ ] Final metrics report
- [ ] Success criteria assessment
- [ ] Remaining failure documentation
- [ ] SPRINT_LOG.md with final metrics

### Quality Checks
```bash
# Full pipeline test - final
python tests/gamslib/run_full_test.py

# Generate final report
python tests/gamslib/run_full_test.py --report

# Verify targets
echo "Target: Solve ≥22, path_syntax_error ≤2"
```

### Completion Criteria
- [ ] **SUCCESS**: Solve ≥22 AND path_syntax_error ≤2
- [ ] OR documented explanation if targets not met
- [ ] SPRINT_LOG.md updated with:
  - Final metrics (Parse, Translate, Solve)
  - path_syntax_error count
  - Success/gap assessment
  - Remaining failures documented

### PR & Review
- **PR Title**: `sprint18/day11-checkpoint3: Final pipeline retest`
- **PR Body**: Include final metrics table, success criteria status
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `checkpoint`, `final-test`

### Reference Documents
- PLAN.md: Lines 491-520 (Day 11 details)
- PLAN.md: Lines 458-459 (Success criteria: Solve ≥22, path_syntax_error ≤2)

---

## Day 12: Documentation and CHANGELOG

### Branch
```
sprint18/day12-documentation
```

### Objective
Document all Sprint 18 changes, update CHANGELOG, and prepare release notes.

### Prerequisites
- [ ] Day 11 checkpoint completed
- [ ] Final metrics confirmed
- [ ] All fixes merged

### Tasks
1. **Update CHANGELOG.md** (~1.5h)
   - Document all Sprint 18 fixes
   - Group by category
   - Include metrics improvement

2. **Update technical documentation** (~1.5h)
   - Document emit_gams.py changes
   - Update architecture docs if needed
   - Add any new patterns

3. **Create release notes draft** (~1h)
   - Summarize Sprint 18 achievements
   - Highlight key improvements
   - Note any limitations

4. **Update project documentation** (~0.5h)
   - PROJECT_PLAN.md updates
   - README updates if needed
   - SPRINT_LOG.md final entry

### Deliverables
- [ ] CHANGELOG.md updated
- [ ] Technical documentation updated
- [ ] Release notes draft
- [ ] All project docs updated

### Quality Checks
```bash
# Verify documentation
cat CHANGELOG.md | head -50

# Check for broken links
# (manual review)

# Verify consistency
grep -r "Sprint 18" docs/
```

### Completion Criteria
- [ ] CHANGELOG.md complete with all fixes
- [ ] Documentation accurate and complete
- [ ] Release notes ready for review
- [ ] SPRINT_LOG.md updated with:
  - Documentation completed
  - CHANGELOG entries
  - Release notes status

### PR & Review
- **PR Title**: `sprint18/day12-documentation: Sprint 18 documentation`
- **PR Body**: Include documentation summary, CHANGELOG preview
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `documentation`

### Reference Documents
- CHANGELOG.md: Current state
- PLAN.md: Lines 521-550 (Day 12 details)
- All Sprint 18 PRs for reference

---

## Day 13: Code Review and Cleanup

### Branch
```
sprint18/day13-cleanup
```

### Objective
Final code review, cleanup, and preparation for sprint completion.

### Prerequisites
- [ ] Day 12 completed and merged
- [ ] Documentation complete
- [ ] All Sprint 18 code merged

### Tasks
1. **Code review pass** (~2h)
   - Review all Sprint 18 changes
   - Check for code quality issues
   - Verify test coverage

2. **Final cleanup** (~1.5h)
   - Remove any TODOs
   - Clean up comments
   - Ensure consistent style

3. **Test suite verification** (~1h)
   - Run all tests
   - Verify coverage
   - Check for flaky tests

4. **Prepare for merge** (~0.5h)
   - Ensure clean history
   - Prepare merge strategy
   - Update SPRINT_LOG.md

### Deliverables
- [ ] Code review complete
- [ ] All cleanup done
- [ ] Tests verified
- [ ] Ready for final merge

### Quality Checks
```bash
# Full test suite
python -m pytest tests/ -v

# Code quality
ruff check src/
ruff format --check src/

# Full pipeline
python tests/gamslib/run_full_test.py
```

### Completion Criteria
- [ ] All code reviewed and approved
- [ ] No outstanding TODOs
- [ ] All tests passing
- [ ] SPRINT_LOG.md updated with:
  - Code review findings
  - Cleanup completed
  - Test verification results

### PR & Review
- **PR Title**: `sprint18/day13-cleanup: Final code review and cleanup`
- **PR Body**: Include code review summary, cleanup notes
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `cleanup`

### Reference Documents
- PLAN.md: Lines 551-580 (Day 13 details)
- All Sprint 18 source changes

---

## Day 14: Sprint Completion and Retrospective

### Branch
```
sprint18/day14-completion
```

### Objective
Complete Sprint 18, run retrospective, and prepare handoff to next sprint.

### Prerequisites
- [ ] Day 13 completed and merged
- [ ] All Sprint 18 work complete
- [ ] Final metrics confirmed

### Tasks
1. **Final merge to main** (~1h)
   - Merge all Sprint 18 branches
   - Create release tag (v1.2.0)
   - Verify main is clean

2. **Sprint retrospective** (~1.5h)
   - Document what went well
   - Document what could improve
   - Capture lessons learned

3. **Handoff preparation** (~1h)
   - Document remaining work for future sprints
   - Update PROJECT_PLAN.md
   - Create handoff notes

4. **Sprint completion** (~0.5h)
   - Close Sprint 18 items
   - Archive sprint documents
   - Final SPRINT_LOG.md entry

### Deliverables
- [ ] All code merged to main
- [ ] Release tag created
- [ ] Retrospective document
- [ ] Handoff notes for next sprint
- [ ] SPRINT_LOG.md completed

### Quality Checks
```bash
# Verify main is clean
git checkout main
git pull
python tests/gamslib/run_full_test.py

# Verify tag
git tag -l | grep v1.2.0
```

### Completion Criteria
- [ ] v1.2.0 tag created
- [ ] All Sprint 18 branches merged
- [ ] Retrospective documented
- [ ] SPRINT_LOG.md final entry with:
  - Sprint completion confirmation
  - Final metrics summary
  - Retrospective highlights
  - Next sprint handoff notes

### PR & Review
- **PR Title**: `sprint18/day14-completion: Sprint 18 completion`
- **PR Body**: Include retrospective summary, final metrics, handoff notes
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `completion`

### Reference Documents
- PLAN.md: Lines 581-620 (Day 14 details)
- PLAN.md: Full document for retrospective reference
- KNOWN_UNKNOWNS.md: For retrospective on risk handling

---

## Quick Reference

### Sprint 18 Targets
| Metric | Baseline | Target |
|--------|----------|--------|
| Parse | 61/160 | 65/160 |
| Solve | 12/42 | ≥22 |
| path_syntax_error | 6+ | ≤2 |

### Checkpoint Schedule
| Checkpoint | Day | Solve Target | path_syntax_error Target |
|------------|-----|--------------|--------------------------|
| 1 | Day 3 | ≥14 | - |
| 2 | Day 6 | ≥17 | ≤4 |
| 3 | Day 11 | ≥22 | ≤2 |

### Key Files
- `src/nlp2mcp/emit_gams.py` - Primary emission logic
- `tests/gamslib/run_full_test.py` - Full pipeline test
- `docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md` - Sprint progress log
- `docs/planning/EPIC_4/SPRINT_18/PLAN.md` - Sprint plan
- `docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md` - Risk tracking

### Branch Naming Convention
```
sprint18/dayN-description
```

### PR Labels
- `sprint-18` - All Sprint 18 PRs
- `bug-fix` - Bug fix PRs
- `checkpoint` - Checkpoint PRs
- `documentation` - Documentation PRs
- `path-syntax` - Path syntax related
- `expressions` - Expression related
- `statements` - Statement related
