# Sprint 17 Prep Task Prompts

This document contains prompts for executing each prep task (Tasks 2-9) in Sprint 17 preparation.

**Usage:** Copy the appropriate prompt for your current task and execute it in a new conversation.

---

## Task 2: Detailed Error Analysis

### Prompt

```
On a new branch `planning/sprint17-task2`, complete Sprint 17 Prep Task 2: Detailed Error Analysis.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P0 - Critical  
**Estimated Time:** 3 hours  
**Unknowns to Verify:** 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5

### Objective
Analyze remaining error categories to understand patterns and fix complexity.

### Why This Matters
Sprint 16 revealed error category shifts. Understanding the exact nature of remaining errors enables targeted fixes rather than trial-and-error approaches.

### Background
Sprint 16 error distribution:
- `lexer_invalid_char`: 97 models (largest blocker)
- `path_syntax_error`: 8 models (MCP compilation)
- Translation failures: 27 models (various categories)
- Solve mismatches: 10 models

### What Needs to Be Done
1. Extract sample error messages for each category
2. Identify patterns across models within categories
3. Estimate fix complexity (trivial/moderate/complex)
4. Map errors to specific code locations
5. Document findings in analysis report

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/ERROR_ANALYSIS.md`** containing:
   - Error category breakdown with counts
   - At least 3 sample errors per major category
   - Pattern analysis for each category
   - Fix complexity estimates (trivial <1h, moderate 1-4h, complex >4h)
   - Recommended approach for each category
   - Priority ranking based on ROI (models/effort)

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 3.1: What subcategories exist within the 97 `lexer_invalid_char` errors?**
   - Update status: 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG with correction)
   - Add findings: Specific subcategory breakdown with counts
   - Add evidence: Error extraction queries and results
   - Add decision: Which subcategories are fixable

   **Unknown 3.3: What causes the 14 `internal_error` parse failures?**
   - Update status and add findings about specific error patterns
   - Document root causes identified

   **Unknown 4.1: Can error patterns be automatically categorized for faster triage?**
   - Update with assessment of categorization feasibility
   - Add regex patterns if applicable

   **Unknown 4.2: What error information is most useful for debugging?**
   - Document what info is currently captured
   - Identify gaps

   **Unknown 4.3: Are there correlations between error categories and model characteristics?**
   - Add correlation analysis results

   **Unknown 4.4: How should error analysis results feed into fix prioritization?**
   - Document the prioritization formula used
   - Validate against analyzed data

   **Unknown 4.5: What sample size is needed for reliable error pattern identification?**
   - Document methodology decision based on actual analysis

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 2 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All major error categories analyzed
     - [x] Sample errors extracted for each category
     - [x] Complexity estimates provided
     - [x] Patterns identified and documented
     - [x] Unknowns 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5 verified and updated in KNOWN_UNKNOWNS.md

4. **Update `CHANGELOG.md`** with task summary including:
   - Branch name
   - Key findings (error category breakdown, patterns identified)
   - Deliverables created
   - Unknowns verified

## Quality Gate

Before committing, run:
```bash
make typecheck && make lint && make format && make test
```

All checks must pass. If there are no Python code changes, this step can be skipped.

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 2: Detailed Error Analysis

Created ERROR_ANALYSIS.md with comprehensive error categorization:
- lexer_invalid_char: X subcategories identified
- internal_error: Y root causes found
- Translation failures: Z patterns documented
- Solve failures: W patterns documented

Verified Unknowns: 3.1, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5

Key findings:
- [List 2-3 key findings]

Updated PREP_PLAN.md Task 2 status to COMPLETE.
```

### Create Pull Request
After committing and pushing:
```bash
gh pr create --title "Sprint 17 Prep Task 2: Detailed Error Analysis" \
  --body "## Summary
Completed detailed error analysis for Sprint 17 preparation.

## Deliverables
- [ ] ERROR_ANALYSIS.md created
- [ ] KNOWN_UNKNOWNS.md updated (7 unknowns verified)
- [ ] PREP_PLAN.md Task 2 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 3.1: lexer_invalid_char subcategories
- 3.3: internal_error causes
- 4.1: Automatic categorization feasibility
- 4.2: Useful debugging info
- 4.3: Error/model correlations
- 4.4: Prioritization formula
- 4.5: Sample size methodology

## Key Findings
[Add 3-5 bullet points of key findings]
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 3: Translation Deep Dive

### Prompt

```
On a new branch `planning/sprint17-task3`, complete Sprint 17 Prep Task 3: Translation Deep Dive.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P1 - High  
**Estimated Time:** 3 hours  
**Dependencies:** Task 2  
**Unknowns to Verify:** 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

### Objective
Categorize and prioritize the 27 translation failures for targeted fixes.

### Why This Matters
Translation is the middle bottleneck. Fixing translation issues has multiplicative impact: each new model that translates becomes a candidate for solve success.

### Background
Translation failure categories from Sprint 16:
- `model_domain_mismatch`: 6 models (index domain issues)
- `diff_unsupported_func`: 6 models (missing derivative rules)
- `model_no_objective_def`: 5 models (objective handling)
- Other categories: 10 models

### What Needs to Be Done
1. Group all 27 translation failures by root cause
2. Identify which require AD changes vs emit changes
3. Prioritize by impact (models affected) and effort
4. Create fix plan with estimated hours per category
5. Identify quick wins (high impact, low effort)

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/TRANSLATION_ANALYSIS.md`** containing:
   - Complete list of 27 translation failures with error categories
   - Root cause analysis for each category
   - Code location identification (AD module vs emit module vs other)
   - Fix complexity estimates
   - Prioritized fix plan with hours per category
   - Quick wins clearly identified
   - Expected model impact for each fix

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 1.1: What specific functions are missing from the AD module that cause `diff_unsupported_func` errors?**
   - Update status: 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG)
   - List specific functions found (gamma, erf, etc.)
   - Document derivative formulas needed
   - Assess implementation complexity

   **Unknown 1.2: Can `model_domain_mismatch` errors be fixed by improving domain propagation in the IR?**
   - Document specific mismatch patterns found
   - Identify IR vs parser vs other causes
   - Assess fix feasibility

   **Unknown 1.3: How should `model_no_objective_def` errors be handled for feasibility problems?**
   - Document whether models are true feasibility problems
   - Propose handling approach (dummy objective, CNS, etc.)

   **Unknown 1.4: Can `unsup_index_offset` errors be resolved with enhanced index arithmetic?**
   - Document offset patterns found
   - Assess IR support requirements

   **Unknown 1.5: What causes `unsup_dollar_cond` errors and how complex is the fix?**
   - Document specific dollar conditional patterns
   - Assess fix complexity

   **Unknown 1.6: What causes `codegen_numerical_error` and is it data-dependent?**
   - Identify specific numerical operation causing error
   - Determine if fixable

   **Unknown 1.7: Will fixing translation issues improve the translate rate or reveal new issues?**
   - Analyze issue independence
   - Project expected improvement

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 3 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All 27 failures categorized
     - [x] Root causes identified
     - [x] Fix locations determined (AD/emit/other)
     - [x] Priority ranking established
     - [x] Unknowns 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 verified and updated in KNOWN_UNKNOWNS.md

4. **Update `CHANGELOG.md`** with task summary

## Quality Gate

Before committing, run:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 3: Translation Deep Dive

Created TRANSLATION_ANALYSIS.md with analysis of 27 translation failures:
- model_domain_mismatch: X models, [root cause summary]
- diff_unsupported_func: Y models, [functions identified]
- model_no_objective_def: Z models, [handling approach]
- Other categories: W models

Verified Unknowns: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7

Quick wins identified:
- [List quick wins]

Updated PREP_PLAN.md Task 3 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 3: Translation Deep Dive" \
  --body "## Summary
Completed deep dive analysis of 27 translation failures.

## Deliverables
- [ ] TRANSLATION_ANALYSIS.md created
- [ ] KNOWN_UNKNOWNS.md updated (7 unknowns verified)
- [ ] PREP_PLAN.md Task 3 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 1.1: Missing AD functions
- 1.2: Domain mismatch causes
- 1.3: No-objective handling
- 1.4: Index offset support
- 1.5: Dollar conditional complexity
- 1.6: Numerical error causes
- 1.7: Translation improvement cascade

## Key Findings
[Add findings]
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 4: MCP Compilation Analysis

### Prompt

```
On a new branch `planning/sprint17-task4`, complete Sprint 17 Prep Task 4: MCP Compilation Analysis.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P1 - High  
**Estimated Time:** 2 hours  
**Dependencies:** Task 2  
**Unknowns to Verify:** 2.1, 2.4

### Objective
Investigate the 8 `path_syntax_error` models to understand MCP compilation failures.

### Why This Matters
These 8 models successfully translate but fail MCP compilation - they're "almost there." Fixing these path syntax errors directly adds to solve success.

### Background
Path syntax errors occur when generated MCP code has invalid GAMS syntax. Sprint 16 fixed some patterns but 8 remain.

### What Needs to Be Done
1. Generate MCP files for all 8 affected models
2. Compile each manually with GAMS
3. Document exact error locations and messages
4. Identify patterns in emit_gams.py causing issues
5. Propose fixes

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/MCP_COMPILATION_ANALYSIS.md`** containing:
   - List of all 8 path_syntax_error models
   - For each model:
     - Generated MCP file (or location)
     - Exact GAMS error message and error code
     - Line/column of error in generated file
     - Source construct causing the issue
     - Root cause in emit_gams.py (file and approximate location)
   - Pattern summary: How many models share each error pattern
   - Proposed fixes with effort estimates
   - Priority ordering based on models affected

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 2.1: What causes the 8 remaining `path_syntax_error` failures?**
   - Update status: 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG)
   - List specific GAMS error codes encountered
   - Document patterns in emit_gams.py
   - Provide evidence: Error messages and code locations

   **Unknown 2.4: Are objective mismatches due to numerical tolerance or actual bugs?**
   - If applicable during MCP analysis, document any objective-related findings
   - Otherwise note: "Will be verified in Task 6"

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 4 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All 8 models analyzed
     - [x] MCP files generated and saved
     - [x] GAMS errors captured
     - [x] Root causes in emit_gams.py identified
     - [x] Unknowns 2.1, 2.4 verified and updated in KNOWN_UNKNOWNS.md

4. **Update `CHANGELOG.md`** with task summary

## Analysis Commands

To identify affected models:
```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.solve_outcome == "path_syntax_error") | .model_name'
```

To generate MCP for a model:
```bash
python -m nlp2mcp.cli data/gamslib/raw/MODEL.gms --emit-only -o /tmp/MODEL_mcp.gms
```

To compile with GAMS:
```bash
gams /tmp/MODEL_mcp.gms
```

## Quality Gate

Before committing, run:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 4: MCP Compilation Analysis

Created MCP_COMPILATION_ANALYSIS.md analyzing 8 path_syntax_error models:
- Error pattern 1: X models - [description]
- Error pattern 2: Y models - [description]

Verified Unknowns: 2.1, 2.4

Root causes identified in emit_gams.py:
- [List specific code locations]

Proposed fixes:
- [List fixes with effort estimates]

Updated PREP_PLAN.md Task 4 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 4: MCP Compilation Analysis" \
  --body "## Summary
Analyzed 8 path_syntax_error models to identify MCP compilation issues.

## Deliverables
- [ ] MCP_COMPILATION_ANALYSIS.md created
- [ ] KNOWN_UNKNOWNS.md updated (2 unknowns verified)
- [ ] PREP_PLAN.md Task 4 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 2.1: Path syntax error causes
- 2.4: Objective mismatch analysis (if applicable)

## Error Patterns Found
[List patterns]

## Proposed Fixes
[List fixes with effort]
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 5: Lexer/Parser Improvement Plan

### Prompt

```
I requested another review on PR #585...

PR #585 (https://github.com/jeffreyhorn/nlp2mcp/pull/585) has review comments. Use gh to:

1. Fetch and list all review comments
2. Fix each issue in the code
3. **Run quality checks: make typecheck && make lint && make format && make testif any code (python) files were modified.  You don't need to run these quality checks if only documentation has changed.**
4. **All must pass before proceeding**
5. Commit fixes: "Address PR #585 review comments" (single commit, list all fixes in body)
6. Push changes
7. Reply to each comment with: "Fixed in <commit_sha>. [specific explanation]"

If any comment is unclear or quality checks fail, stop and ask me.
```

---

## Task 6: Solve Failure Investigation Plan

### Prompt

```
On a new branch `planning/sprint17-task6`, complete Sprint 17 Prep Task 6: Solve Failure Investigation Plan.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P1 - High  
**Estimated Time:** 2 hours  
**Dependencies:** Task 2  
**Unknowns to Verify:** 2.2, 2.3, 2.5

### Objective
Plan investigation and fixes for solve failures and mismatches.

### Why This Matters
Sprint 17 targets 80% solve success (currently 52.4%). Understanding solve failures enables targeted improvements to reach this goal.

### Background
Solve failure categories to investigate:
- PATH solver configuration issues
- Initial point problems
- Scaling/conditioning problems
- Numerical tolerance mismatches
- Actual nlp2mcp bugs

### What Needs to Be Done
1. Categorize all solve failures by root cause
2. Identify PATH solver configuration opportunities
3. Assess initial point handling improvements
4. Evaluate tolerance adjustment options
5. Create investigation and fix plan

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/SOLVE_INVESTIGATION_PLAN.md`** containing:
   - Complete categorization of solve failures
   - For each failure category:
     - Models affected
     - Specific error/mismatch details
     - Root cause analysis
     - Whether it's a nlp2mcp bug, solver issue, or model issue
   - PATH solver configuration analysis:
     - Current settings
     - Potential improvements
     - Expected impact
   - Tolerance analysis:
     - Current comparison thresholds
     - Objective value differences observed
     - Recommended adjustments
   - Prioritized investigation/fix plan
   - Assessment of 80% target feasibility

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 2.2: Why do 10 models have solve failures/mismatches despite successful translation?**
   - Update status: 🔍 INCOMPLETE → ✅ VERIFIED (or ❌ WRONG)
   - Categorize the 10 failures by type
   - Identify which are fixable vs inherent

   **Unknown 2.3: Can PATH solver configuration be improved to handle more models?**
   - Document current PATH settings
   - List available options researched
   - Provide recommendations

   **Unknown 2.5: Is 80% solve success rate achievable given model complexity?**
   - Provide assessment based on failure analysis
   - Identify how many failures are fixable
   - Recommend adjusted target if needed

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 6 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All solve failures categorized
     - [x] Root causes identified
     - [x] Fix options evaluated
     - [x] Impact estimates provided
     - [x] Unknowns 2.2, 2.3, 2.5 verified and updated in KNOWN_UNKNOWNS.md

4. **Update `CHANGELOG.md`** with task summary

## Quality Gate

Before committing, run:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 6: Solve Failure Investigation Plan

Created SOLVE_INVESTIGATION_PLAN.md with analysis of solve failures:
- Fixable nlp2mcp bugs: X models
- PATH configuration issues: Y models
- Inherent model issues: Z models

Verified Unknowns: 2.2, 2.3, 2.5

80% target assessment: [ACHIEVABLE/NEEDS ADJUSTMENT]

Recommended actions:
- [List key recommendations]

Updated PREP_PLAN.md Task 6 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 6: Solve Failure Investigation Plan" \
  --body "## Summary
Created investigation plan for solve failures and mismatches.

## Deliverables
- [ ] SOLVE_INVESTIGATION_PLAN.md created
- [ ] KNOWN_UNKNOWNS.md updated (3 unknowns verified)
- [ ] PREP_PLAN.md Task 6 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 2.2: Solve failure root causes
- 2.3: PATH solver configuration options
- 2.5: 80% target feasibility

## Key Findings
[Add findings]
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 7: Documentation Inventory

### Prompt

```
On a new branch `planning/sprint17-task7`, complete Sprint 17 Prep Task 7: Documentation Inventory.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P2 - Medium  
**Estimated Time:** 1 hour  
**Dependencies:** None  
**Unknowns to Verify:** None (documentation-focused task)

### Objective
Inventory existing documentation and identify gaps for v1.1.0 release.

### Why This Matters
Sprint 17 includes user documentation as a major deliverable. Understanding what exists and what's missing enables efficient documentation work.

### Background
Sprint 17 documentation deliverables:
- `docs/guides/GAMSLIB_TESTING.md` - User guide for GAMSLIB testing
- Infrastructure documentation updates
- Release notes

### What Needs to Be Done
1. List all existing documentation files
2. Assess completeness and accuracy
3. Identify gaps requiring new documentation
4. Prioritize documentation tasks
5. Estimate effort for each doc task

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/DOCUMENTATION_PLAN.md`** containing:
   - Complete inventory of existing documentation:
     - `docs/` directory structure
     - Each file with brief description
     - Last update date
     - Completeness assessment (complete/partial/outdated/missing)
   - Gap analysis:
     - Required docs for v1.1.0 that don't exist
     - Existing docs that need updates
     - Nice-to-have docs
   - Prioritized documentation task list:
     - P0: Required for release
     - P1: Important for users
     - P2: Nice to have
   - Effort estimates for each doc task
   - Recommended Sprint 17 day allocation

2. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 7 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All docs directories scanned
     - [x] Gaps identified
     - [x] Priority ranking established
     - [x] Effort estimates provided

3. **Update `CHANGELOG.md`** with task summary

## Inventory Commands

```bash
# List all markdown files
find docs -name "*.md" -type f | sort

# Check recent updates
find docs -name "*.md" -type f -exec stat -f "%Sm %N" -t "%Y-%m-%d" {} \; | sort -r | head -20
```

## Quality Gate

No code changes expected. If any Python changes are made:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 7: Documentation Inventory

Created DOCUMENTATION_PLAN.md with:
- Inventory of X existing documentation files
- Y gaps identified for v1.1.0
- Z hours estimated for documentation work

Required for release:
- [List P0 docs]

Nice to have:
- [List P2 docs]

Updated PREP_PLAN.md Task 7 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 7: Documentation Inventory" \
  --body "## Summary
Inventoried existing documentation and identified gaps for v1.1.0.

## Deliverables
- [ ] DOCUMENTATION_PLAN.md created
- [ ] PREP_PLAN.md Task 7 marked COMPLETE
- [ ] CHANGELOG.md updated

## Documentation Summary
- Existing docs: X files
- Gaps identified: Y items
- Estimated effort: Z hours

## Priority Breakdown
| Priority | Items | Hours |
|----------|-------|-------|
| P0 (Required) | A | B |
| P1 (Important) | C | D |
| P2 (Nice to have) | E | F |
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 8: Release Checklist

### Prompt

```
On a new branch `planning/sprint17-task8`, complete Sprint 17 Prep Task 8: Release Checklist.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P2 - Medium  
**Estimated Time:** 1 hour  
**Dependencies:** Task 7  
**Unknowns to Verify:** 5.1, 5.2, 5.3, 5.4

### Objective
Create comprehensive checklist for v1.1.0 release.

### Why This Matters
Sprint 17 culminates in the v1.1.0 release. A thorough checklist ensures nothing is missed and the release is professional and complete.

### Background
Release requirements from PROJECT_PLAN.md:
- Update CHANGELOG
- Update version to v1.1.0
- Create release notes
- Tag release
- Ensure all tests passing
- Documentation complete

### What Needs to Be Done
1. List all release artifacts
2. Define quality gates for release
3. Create step-by-step release process
4. Identify release blockers to monitor
5. Plan release communication

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/RELEASE_CHECKLIST.md`** containing:
   - Pre-release verification steps:
     - Code quality gates
     - Test requirements
     - Documentation requirements
     - Metrics targets
   - Artifact preparation:
     - Version bumps (where?)
     - CHANGELOG updates
     - Release notes template
   - Release execution steps:
     - Git tag creation
     - GitHub release creation
     - Any deployment steps
   - Post-release verification:
     - Smoke tests
     - Documentation live check
   - Rollback plan (if needed)
   - Release blockers to monitor during sprint

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 5.1: How accurate are effort estimates for grammar/lexer changes?**
   - Review Sprint 16 estimates vs actuals
   - Document estimation accuracy
   - Provide recommendations for Sprint 17 estimates

   **Unknown 5.2: What's the typical testing overhead for each fix type?**
   - Document testing standards
   - Estimate overhead percentages

   **Unknown 5.3: Are there hidden dependencies between fixes that affect ordering?**
   - Map any identified dependencies
   - Note if fixes can be parallelized

   **Unknown 5.4: How should we handle fixes that require major refactoring?**
   - Define "major refactoring" threshold
   - Document defer vs implement criteria

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 8 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All release artifacts listed
     - [x] Quality gates defined
     - [x] Step-by-step process documented
     - [x] Blockers identified
     - [x] Unknowns 5.1, 5.2, 5.3, 5.4 verified and updated in KNOWN_UNKNOWNS.md

4. **Update `CHANGELOG.md`** with task summary

## Quality Gate

No code changes expected. If any Python changes are made:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 8: Release Checklist

Created RELEASE_CHECKLIST.md for v1.1.0:
- X pre-release verification steps
- Y artifacts to prepare
- Z release execution steps
- Post-release verification included

Verified Unknowns: 5.1, 5.2, 5.3, 5.4

Quality gates defined:
- [List key quality gates]

Updated PREP_PLAN.md Task 8 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 8: Release Checklist" \
  --body "## Summary
Created comprehensive release checklist for v1.1.0.

## Deliverables
- [ ] RELEASE_CHECKLIST.md created
- [ ] KNOWN_UNKNOWNS.md updated (4 unknowns verified)
- [ ] PREP_PLAN.md Task 8 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 5.1: Effort estimate accuracy
- 5.2: Testing overhead standards
- 5.3: Fix dependencies
- 5.4: Major refactoring criteria

## Checklist Summary
- Pre-release steps: X
- Artifacts: Y
- Release steps: Z
- Quality gates: W
" --base main
```

Wait for reviewer comments before merging.
```

---

## Task 9: Plan Sprint 17 Detailed Schedule

### Prompt

```
On a new branch `planning/sprint17-task9`, complete Sprint 17 Prep Task 9: Plan Sprint 17 Detailed Schedule.

## Task Objectives

**Status:** Not Started → COMPLETE  
**Priority:** P0 - Critical  
**Estimated Time:** 2 hours  
**Dependencies:** Tasks 1-8 (all previous prep tasks)  
**Unknowns to Verify:** 3.5, 3.6

### Objective
Create detailed day-by-day schedule for Sprint 17 based on prep findings.

### Why This Matters
Sprint 17 is ambitious with 26-34 hours of planned work. A detailed schedule ensures efficient execution and proper prioritization.

### Background
Sprint 17 components from PROJECT_PLAN.md:
- Translation Improvements (~8-10h)
- Solve Improvements (~6-8h)
- Final Assessment (~6-8h)
- Documentation & Release (~6-8h)

### What Needs to Be Done
1. Review all prep task findings
2. Prioritize Sprint 17 work based on discoveries
3. Allocate tasks to sprint days
4. Identify dependencies and sequencing
5. Build in contingency for unknowns
6. Create SPRINT_LOG.md template

## Prerequisites

Before starting this task, ensure Tasks 2-8 are complete and their findings are available:
- ERROR_ANALYSIS.md (Task 2)
- TRANSLATION_ANALYSIS.md (Task 3)
- MCP_COMPILATION_ANALYSIS.md (Task 4)
- LEXER_IMPROVEMENT_PLAN.md (Task 5)
- SOLVE_INVESTIGATION_PLAN.md (Task 6)
- DOCUMENTATION_PLAN.md (Task 7)
- RELEASE_CHECKLIST.md (Task 8)

## Deliverables

1. **Create `docs/planning/EPIC_3/SPRINT_17/SPRINT_SCHEDULE.md`** containing:
   - Sprint 17 header with goals and targets
   - Day-by-day schedule (Days 1-10):
     - Each day's focus area
     - Specific tasks with time estimates
     - Expected deliverables
     - Dependencies on previous days
   - Checkpoint markers (CP1, CP2, etc.)
   - Contingency buffer allocation
   - Release day clearly marked
   - Metrics tracking table (to be filled during sprint)
   - Template sections for daily updates

2. **Update `docs/planning/EPIC_3/SPRINT_17/KNOWN_UNKNOWNS.md`** with verification results for:

   **Unknown 3.5: How much of the 70% parse target depends on lexer fixes vs other improvements?**
   - Integrate findings from Task 5 (LEXER_IMPROVEMENT_PLAN.md)
   - Provide final breakdown
   - Assess target achievability

   **Unknown 3.6: Will parse improvements reveal new translation or solve issues?**
   - Project cascade effects based on all prep findings
   - Factor into schedule

3. **Update `docs/planning/EPIC_3/SPRINT_17/PREP_PLAN.md`:**
   - Change Task 9 status: `Not Started` → `COMPLETE`
   - Check off all verification items:
     - [x] All Sprint 17 work items scheduled
     - [x] Dependencies respected
     - [x] Total hours realistic (26-34h)
     - [x] Contingency included
     - [x] Unknowns 3.5, 3.6 verified and updated in KNOWN_UNKNOWNS.md
   - Update "Success Criteria for Prep Phase" section:
     - [x] All prep tasks complete

4. **Update `CHANGELOG.md`** with task summary

## Schedule Template

```markdown
## Day 1: [Focus]
- [ ] Task A (Xh)
- [ ] Task B (Yh)
**Deliverables:** ...
**Checkpoint:** CP1 (if applicable)

## Day 2: [Focus]
...
```

## Quality Gate

No code changes expected. If any Python changes are made:
```bash
make typecheck && make lint && make format && make test
```

## Commit and PR

### Commit Message Format
```
Complete Sprint 17 Prep Task 9: Plan Sprint 17 Detailed Schedule

Created SPRINT_LOG.md with 10-day schedule:
- Days 1-3: [Focus area]
- Days 4-6: [Focus area]
- Days 7-8: [Focus area]
- Days 9-10: [Focus area]

Total planned: Xh (within 26-34h target)
Contingency: Yh

Verified Unknowns: 3.5, 3.6

Key scheduling decisions:
- [List key decisions]

All prep tasks complete. Ready for Sprint 17.
Updated PREP_PLAN.md Task 9 status to COMPLETE.
```

### Create Pull Request
```bash
gh pr create --title "Sprint 17 Prep Task 9: Plan Sprint 17 Detailed Schedule" \
  --body "## Summary
Created detailed 10-day schedule for Sprint 17 based on all prep findings.

## Deliverables
- [ ] SPRINT_LOG.md created with day-by-day schedule
- [ ] KNOWN_UNKNOWNS.md updated (2 unknowns verified)
- [ ] PREP_PLAN.md Task 9 marked COMPLETE
- [ ] CHANGELOG.md updated

## Unknowns Verified
- 3.5: Parse target breakdown (final)
- 3.6: Cascade effects projection

## Schedule Summary
| Phase | Days | Focus | Hours |
|-------|------|-------|-------|
| Phase 1 | 1-3 | [focus] | X |
| Phase 2 | 4-6 | [focus] | Y |
| Phase 3 | 7-8 | [focus] | Z |
| Phase 4 | 9-10 | [focus] | W |
| **Total** | 10 | | **X+Y+Z+W** |

## Prep Phase Complete
All 9 prep tasks complete. Sprint 17 ready to begin.
" --base main
```

Wait for reviewer comments before merging.
```

---

## Summary: Task Execution Order

Execute tasks in this order (respecting dependencies):

1. **Task 2: Detailed Error Analysis** (no deps)
2. **Task 7: Documentation Inventory** (no deps, can parallel with Task 2)
3. **Task 3: Translation Deep Dive** (depends on Task 2)
4. **Task 4: MCP Compilation Analysis** (depends on Task 2)
5. **Task 6: Solve Failure Investigation Plan** (depends on Task 2)
6. **Task 5: Lexer/Parser Improvement Plan** (depends on Tasks 2, 3)
7. **Task 8: Release Checklist** (depends on Task 7)
8. **Task 9: Plan Sprint 17 Detailed Schedule** (depends on Tasks 1-8)

## Unknown Verification Summary

| Task | Unknowns Verified |
|------|-------------------|
| Task 2 | 3.1*, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5 |
| Task 3 | 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7 |
| Task 4 | 2.1, 2.4 |
| Task 5 | 3.1 (primary), 3.2, 3.4, 3.5* |
| Task 6 | 2.2, 2.3, 2.5 |
| Task 7 | - |
| Task 8 | 5.1, 5.2, 5.3, 5.4 |
| Task 9 | 3.5 (finalized), 3.6 |

*Note: Unknown 3.1 is partially verified by Task 2 and primarily verified by Task 5. Unknown 3.5 is partially verified by Task 5 and finalized by Task 9.

**Total Unknowns:** 27  
**Verified by Tasks 2-9:** 27 unique unknowns (100%, some verified across multiple tasks)
