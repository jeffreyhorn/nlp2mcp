# Sprint 18: GAMS Emission Fixes - Day-by-Day Execution Prompts

> **Sprint Duration**: 14 working days (~56h), plus Day 0 initialization
> **Epic**: 4 - Production Readiness
> **Baseline**: v1.1.0 — Parse 61/160, Translate 42/61, Solve 12/42
> **Target**: Parse 65/160, Solve ≥22, path_syntax_error ≤2

**Note:** Day 0 is sprint initialization (setup, baseline validation) and is not counted in the 14 working days. Days 1-14 are the actual sprint execution days.

---

## Day 0: Sprint Initialization (Pre-Sprint)

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
python scripts/gamslib/run_full_test.py

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
python scripts/gamslib/run_full_test.py --verbose

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
python scripts/gamslib/run_full_test.py

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
- src/emit/emit_gams.py (emission logic)

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
python scripts/gamslib/run_full_test.py

# Generate metrics report
python scripts/gamslib/run_full_test.py --json
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
python scripts/gamslib/run_full_test.py

# Run path-specific tests
python -m pytest tests/ -k "path" -v

# Check path_syntax_error count
python scripts/gamslib/run_full_test.py | grep path_syntax_error
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
- src/emit/emit_gams.py: Path handling code

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
python scripts/gamslib/run_full_test.py

# Verify path_syntax_error target
python scripts/gamslib/run_full_test.py | grep -E "(path_syntax_error|Solve Results:)"
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
python scripts/gamslib/run_full_test.py

# Detailed failure report
python scripts/gamslib/run_full_test.py --only-failing --verbose
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

## Day 7: Domain Issue Investigation - Part 1

### Branch
```
sprint18/day7-domain-investigation-1
```

### Objective
Investigate domain violation errors (E170, E171) for the first 3 models to identify tractable fixes.

**Note:** *Plan revised based on Checkpoint 2 findings. Original plan targeted MCP infeasibility bugs, but path_syntax_error target (≤4) was not met (10 remain). Prioritizing domain violation investigation for the 6 models marked "⚠️ Investigate".*

### Prerequisites
- [ ] Day 6 checkpoint completed
- [ ] Checkpoint 2 findings documented (10 path_syntax_error, 4 architectural, 6 to investigate)
- [ ] Understanding of GAMS Error 170 (domain violation for element) and E171 (domain violation for set)

### Tasks
1. **Deep-dive on blend domain violation (E171)** (~1h)
   - Run `gams data/gamslib/mcp/blend_mcp.gms lo=3` to get detailed error
   - Examine which set/element causes domain violation
   - Trace back to emit code that generated the invalid reference
   - Document root cause and potential fix

2. **Deep-dive on sample domain violation (E171)** (~1h)
   - Run `gams data/gamslib/mcp/sample_mcp.gms lo=3` to get detailed error
   - Identify domain mismatch pattern
   - Compare with blend to see if same root cause
   - Document findings

3. **Deep-dive on like domain violation (E170)** (~1h)
   - Run `gams data/gamslib/mcp/like_mcp.gms lo=3` to get detailed error
   - E170 is element-level (vs E171 set-level) - understand difference
   - Check if lead/lag index handling is involved
   - Document root cause

4. **Implement fixes for tractable cases** (~1h)
   - If any of the 3 models have simple fixes, implement them
   - Add regression tests for any fixes
   - Run pipeline to verify fixes don't cause regressions

### Deliverables
- [ ] Root cause analysis for blend, sample, like
- [ ] Documentation of whether each is tractable or architectural
- [ ] Fixes implemented for any tractable cases
- [ ] SPRINT_LOG.md updated with Day 7 findings

### Quality Checks
```bash
# Run full test suite
python scripts/gamslib/run_full_test.py

# Check specific models
gams data/gamslib/mcp/blend_mcp.gms lo=3 2>&1 | tail -30
gams data/gamslib/mcp/sample_mcp.gms lo=3 2>&1 | tail -30
gams data/gamslib/mcp/like_mcp.gms lo=3 2>&1 | tail -30

# Run unit tests
make test
```

### Completion Criteria
- [ ] Root causes documented for blend, sample, like
- [ ] Each categorized as: tractable fix, architectural issue, or needs more investigation
- [ ] Any tractable fixes implemented and tested
- [ ] No regressions in existing solving models (19 should still solve)
- [ ] SPRINT_LOG.md updated with:
  - Detailed analysis for each model
  - Root cause categorization
  - Fixes implemented (if any)
  - Plan for Day 8 remaining models

### PR & Review
- **PR Title**: `sprint18/day7-domain-investigation-1: Domain violation analysis part 1`
- **PR Body**: Include root cause analysis table, categorization of each model
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `investigation`, `domain-violation`

### Reference Documents
- PLAN.md: Day 7 section (Domain Issue Investigation - Part 1)
- SPRINT_LOG.md: Day 6 Checkpoint 2 findings
- src/emit/expr_to_gams.py: Index/domain handling code
- src/emit/original_symbols.py: Parameter/set emission code

---

## Day 8: Domain Issue Investigation - Part 2

### Branch
```
sprint18/day8-domain-investigation-2
```

### Objective
Continue domain violation investigation for the remaining 3 models (robert, mexss, orani).

### Prerequisites
- [ ] Day 7 completed and merged
- [ ] Root cause analysis for blend, sample, like documented
- [ ] Understanding of patterns found in Day 7

### Tasks
1. **Deep-dive on robert domain violation (E170)** (~1h)
   - Run `gams data/gamslib/mcp/robert_mcp.gms lo=3` to get detailed error
   - E170 is element-level - check if related to lead/lag index handling
   - Compare with like model (also E170) for common patterns
   - Document root cause and potential fix

2. **Deep-dive on mexss domain violations (E170/171)** (~1h)
   - Run `gams data/gamslib/mcp/mexss_mcp.gms lo=3` to get detailed error
   - Has both E170 and E171 - multiple domain issues
   - Identify each issue separately
   - Document root causes

3. **Deep-dive on orani dynamic domain extension** (~1h)
   - Run `gams data/gamslib/mcp/orani_mcp.gms lo=3` to get detailed error
   - Known issue: Models extend sets at runtime with computed elements (e.g., `"total"`)
   - Determine if this is fundamentally architectural or has workaround
   - Document findings

4. **Implement fixes for tractable cases** (~1h)
   - If any of the 3 models have simple fixes, implement them
   - Consider if patterns from Day 7 apply here
   - Add regression tests for any fixes

### Deliverables
- [ ] Root cause analysis for robert, mexss, orani
- [ ] Complete categorization of all 6 "investigate" models
- [ ] Fixes implemented for any tractable cases
- [ ] SPRINT_LOG.md updated with Day 8 findings

### Quality Checks
```bash
# Run full test suite
python scripts/gamslib/run_full_test.py

# Check specific models
gams data/gamslib/mcp/robert_mcp.gms lo=3 2>&1 | tail -30
gams data/gamslib/mcp/mexss_mcp.gms lo=3 2>&1 | tail -30
gams data/gamslib/mcp/orani_mcp.gms lo=3 2>&1 | tail -30

# Run unit tests
make test
```

### Completion Criteria
- [ ] Root causes documented for robert, mexss, orani
- [ ] All 6 "investigate" models now categorized (from Days 7-8)
- [ ] Summary table: which are fixable vs architectural
- [ ] Any tractable fixes implemented and tested
- [ ] No regressions in existing solving models
- [ ] SPRINT_LOG.md updated with:
  - Detailed analysis for each model
  - Complete categorization summary
  - Fixes implemented (if any)
  - Updated path_syntax_error breakdown

### PR & Review
- **PR Title**: `sprint18/day8-domain-investigation-2: Domain violation analysis part 2`
- **PR Body**: Include complete categorization table for all 10 path_syntax_error models
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `investigation`, `domain-violation`

### Reference Documents
- PLAN.md: Day 8 section (Domain Issue Investigation - Part 2)
- Day 7 PR for patterns found
- SPRINT_LOG.md: Day 6 Checkpoint 2 + Day 7 findings

---

## Day 9: Issue Documentation + Architectural Analysis

### Branch
```
sprint18/day9-issue-documentation
```

### Objective
Document all findings from Days 7-8 as formal issue files, categorize architectural limitations, and update project tracking.

### Prerequisites
- [ ] Day 8 completed and merged
- [ ] All 10 path_syntax_error models analyzed
- [ ] Clear categorization: 4 architectural + 6 investigated (some may now be architectural too)

### Tasks
1. **Create ISSUE_*.md for architectural limitations** (~1.5h)
   - ISSUE_680_abel_cross_indexed_sums.md - Cross-indexed sums with dynamic subsets
   - ISSUE_681_qabel_cross_indexed_sums.md - Same pattern as abel
   - ISSUE_682_chenery_cross_indexed_sums.md - Cross-indexed sums + table wildcard
   - ISSUE_683_mingamma_missing_psi_function.md - GAMS lacks psi/digamma function
   - Include: root cause, GAMS error, why it's architectural, potential future fix approach

2. **Create ISSUE_*.md for remaining domain violations** (~1.5h)
   - Create issue files for any of the 6 investigated models that are NOT fixable
   - Document root cause and why fix is not tractable in Sprint 18
   - Note if these could be fixed in future sprints with more effort

3. **Update KNOWN_UNKNOWNS.md with findings** (~0.5h)
   - Mark resolved unknowns from Days 1-8
   - Add any new unknowns discovered during investigation
   - Update risk assessments based on findings

4. **Move completed issues to docs/issues/completed/** (~0.5h)
   - Move any issues that were fixed in Days 1-8
   - Update issue status in each file
   - Ensure issue tracking is organized

### Deliverables
- [ ] ISSUE_*.md files for all architectural limitations (4+ files)
- [ ] ISSUE_*.md files for unfixable domain violations
- [ ] Updated KNOWN_UNKNOWNS.md
- [ ] Organized docs/issues/ directory
- [ ] SPRINT_LOG.md updated with Day 9 summary

### Quality Checks
```bash
# Verify issue files created
ls -la docs/issues/ISSUE_68*.md

# Check KNOWN_UNKNOWNS updates
git diff docs/planning/EPIC_4/SPRINT_18/KNOWN_UNKNOWNS.md

# Verify no code regressions (documentation-only day)
make test
```

### Completion Criteria
- [ ] All architectural issues documented with clear explanations
- [ ] Each issue file includes: root cause, GAMS error code, reproduction steps, why architectural
- [ ] KNOWN_UNKNOWNS.md updated with checkpoint findings
- [ ] Issue tracking organized and up-to-date
- [ ] SPRINT_LOG.md updated with:
  - Issue files created
  - KNOWN_UNKNOWNS changes
  - Summary of architectural vs tractable issues

### PR & Review
- **PR Title**: `sprint18/day9-issue-documentation: Document architectural limitations`
- **PR Body**: List all issue files created, summary of findings
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `documentation`, `issue-tracking`

### Reference Documents
- PLAN.md: Day 9 section (Issue Documentation + Architectural Analysis)
- Days 7-8 PRs for root cause analysis
- docs/issues/README.md for issue file format

---

## Day 10: Final Fixes & Testing

### Branch
```
sprint18/day10-final-fixes
```

### Objective
Implement any remaining tractable fixes identified during Days 7-9, run full pipeline retest, and verify no regressions.

### Prerequisites
- [ ] Day 9 completed and merged
- [ ] Issue documentation complete
- [ ] Clear list of which fixes are tractable vs architectural

### Tasks
1. **Implement remaining tractable fixes** (~1.5h)
   - Review Day 7-8 findings for any fixes that weren't implemented yet
   - Implement highest-impact remaining fixes
   - Add regression tests for each fix

2. **Full pipeline retest on all 160 models** (~1.5h)
   - Run `python scripts/gamslib/run_full_test.py`
   - Capture updated metrics for all stages
   - Compare against Checkpoint 2 metrics

3. **Run full test suite** (~0.5h)
   - Run `make test` to verify all unit/integration tests pass
   - Run `make typecheck && make lint` for code quality
   - Fix any issues found

4. **Verify no regressions in solving models** (~0.5h)
   - Confirm 19+ models still solve (Checkpoint 2 had 19)
   - Check that previously solving models didn't regress
   - Document any changes in solve count

### Deliverables
- [ ] Remaining tractable fixes implemented
- [ ] Full pipeline retest results
- [ ] Updated `gamslib_status.json`
- [ ] All tests passing
- [ ] SPRINT_LOG.md updated with Day 10 metrics

### Quality Checks
```bash
# Full pipeline test
python scripts/gamslib/run_full_test.py

# Full test suite
make test

# Code quality
make typecheck && make lint

# Check solve count
python -c "
import json
with open('data/gamslib/gamslib_status.json') as f:
    db = json.load(f)
count = sum(1 for m in db['models'] 
            if m.get('mcp_solve', {}).get('status') == 'success')
print(f'Solve count: {count}')
"
```

### Completion Criteria
- [ ] All tractable fixes from Days 7-9 implemented
- [ ] Full pipeline retest complete with metrics captured
- [ ] Solve count ≥19 (no regression from Checkpoint 2)
- [ ] All tests passing (unit, integration, typecheck, lint)
- [ ] SPRINT_LOG.md updated with:
  - Final fixes implemented
  - Full pipeline metrics
  - Comparison to Checkpoint 2
  - Ready for Checkpoint 3

### PR & Review
- **PR Title**: `sprint18/day10-final-fixes: Final fixes and pipeline retest`
- **PR Body**: Include metrics comparison table (Day 0 → Checkpoint 2 → Day 10)
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `bug-fix`, `testing`

### Reference Documents
- PLAN.md: Day 10 section (Final Fixes & Testing)
- Days 7-9 PRs for fixes to implement
- SPRINT_LOG.md for Checkpoint 2 metrics baseline

---

## Day 11: Documentation & Checkpoint 3

### Branch
```
sprint18/day11-checkpoint3
```

### Objective
Final documentation updates, create FIX_ROADMAP.md for future sprints, and complete Checkpoint 3 assessment.

### Prerequisites
- [ ] Day 10 completed and merged
- [ ] Final pipeline metrics captured
- [ ] Issue documentation complete

### Tasks
1. **Update SPRINT_LOG.md with final metrics** (~1h)
   - Add Day 11 entry with complete sprint summary
   - Include metrics progression: Day 0 → Checkpoint 2 → Final
   - Document all fixes implemented during sprint
   - List all issues created/resolved

2. **Update GAMSLIB_STATUS.md** (~0.5h)
   - Reflect current pipeline metrics
   - Update failure category breakdown
   - Note architectural limitations discovered

3. **Create FIX_ROADMAP.md for Sprint 19+** (~1h)
   - Prioritize remaining fixes by ROI (models fixed / effort)
   - Document architectural issues that need design work
   - Estimate effort for each category
   - Recommend Sprint 19 focus areas

4. **Checkpoint 3: Sprint review** (~1.5h)
   - Compare final metrics to original targets
   - Assess what was achieved vs planned
   - Document lessons learned
   - Go/no-go assessment for sprint completion

### Deliverables
- [ ] SPRINT_LOG.md complete with all days documented
- [ ] GAMSLIB_STATUS.md updated
- [ ] FIX_ROADMAP.md created with prioritized future work
- [ ] Checkpoint 3 assessment documented

### Quality Checks
```bash
# Verify documentation complete
cat docs/planning/EPIC_4/SPRINT_18/SPRINT_LOG.md | tail -50

# Check FIX_ROADMAP created
cat docs/planning/EPIC_4/SPRINT_18/FIX_ROADMAP.md

# Final metrics verification
python scripts/gamslib/run_full_test.py --dry-run
```

### Completion Criteria
**Checkpoint 3 Criteria:**
- [ ] All tractable path_syntax_error fixes merged
- [ ] Architectural issues documented with ISSUE_*.md files
- [ ] Solve count maintained at ≥19 (no regressions)
- [ ] FIX_ROADMAP.md created for future sprints
- [ ] All tests passing

**Sprint Assessment:**
- [ ] SPRINT_LOG.md complete with all days
- [ ] Metrics documented: final path_syntax_error count, solve count, match count
- [ ] Clear handoff for Sprint 19 with prioritized roadmap

### PR & Review
- **PR Title**: `sprint18/day11-checkpoint3: Final documentation and Checkpoint 3`
- **PR Body**: Include sprint metrics summary, Checkpoint 3 assessment, link to FIX_ROADMAP.md
- **Reviewers**: Project maintainer
- **Labels**: `sprint-18`, `checkpoint`, `documentation`

### Reference Documents
- PLAN.md: Day 11 section (Documentation & Checkpoint 3)
- All Sprint 18 SPRINT_LOG.md entries
- Day 10 metrics for final numbers

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
python scripts/gamslib/run_full_test.py
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
python scripts/gamslib/run_full_test.py

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
- PLAN.md: "Day 14: Sprint Completion" section
- PLAN.md: Full document for retrospective reference
- KNOWN_UNKNOWNS.md: For retrospective on risk handling

---

## Quick Reference

### Sprint 18 Targets
| Metric | Baseline | Target |
|--------|----------|--------|
| Parse | 61/160 | 65/160 |
| Solve | 12/42 | ≥22 |
| path_syntax_error | 17 | ≤2 |

### Checkpoint Schedule
| Checkpoint | Day | Solve Target | path_syntax_error Target |
|------------|-----|--------------|--------------------------|
| 1 | Day 3 | ≥14 | - |
| 2 | Day 6 | ≥17 | ≤4 |
| 3 | Day 11 | ≥22 | ≤2 |

### Key Files
- `src/emit/emit_gams.py` - Primary emission logic
- `scripts/gamslib/run_full_test.py` - Full pipeline test
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
