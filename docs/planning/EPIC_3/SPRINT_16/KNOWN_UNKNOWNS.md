# Sprint 16 Known Unknowns

**Created:** January 16, 2026  
**Status:** Active - Pre-Sprint 16  
**Purpose:** Proactive documentation of assumptions and unknowns for Sprint 16 Reporting, Gap Analysis & Targeted Parser Improvements

---

## Executive Summary

This document identifies all assumptions and unknowns for Sprint 16 features **before** implementation begins. Sprint 16 builds on Sprint 15's comprehensive baseline to create reporting infrastructure, perform systematic gap analysis, and implement targeted parser improvements.

**Sprint 16 Scope:**
1. Reporting Infrastructure - Status Summary Report Generator, Failure Analysis Report, Progress Tracking
2. Gap Analysis - Parse, Translation, and Solve failure analysis with Improvement Roadmap
3. Targeted Parser Improvements - Identify and implement fixes for top parse blockers
4. Retest After Improvements - Regression testing and metric comparison

**Reference:** See `docs/planning/EPIC_3/PROJECT_PLAN.md` lines 334-451 for complete Sprint 16 deliverables and acceptance criteria.

**Sprint 15 Key Results:**
- Parse success rate: 21.3% (34/160 models)
- Translation success rate: 50.0% (17/34 of parsed models)
- Solve success rate: 17.6% (3/17 of translated models)
- Full pipeline success rate: 0.6% (1/160 models)
- 47-category error taxonomy established
- Top parse blocker: lexer_invalid_char (109 models, 68.1%)

**Lessons from Previous Sprints:** The Known Unknowns process achieved excellent results:
- Sprint 15: 26 unknowns verified, comprehensive baseline established
- Sprint 14: 26 unknowns, all verified or deferred appropriately
- Sprint 13: 26 unknowns verified, 100% acceptance criteria met

---

## How to Use This Document

### Before Sprint 16 Day 1
1. Research and verify all **Critical** and **High** priority unknowns
2. Create minimal test cases for validation
3. Document findings in "Verification Results" sections
4. Update status: 🔍 INCOMPLETE → ✅ VERIFIED or ❌ WRONG (with correction)

### During Sprint 16
1. Review daily during standup
2. Add newly discovered unknowns
3. Update with implementation findings
4. Move resolved items to "Confirmed Knowledge"

### Priority Definitions
- **Critical:** Wrong assumption will break core functionality or require major refactoring (>8 hours)
- **High:** Wrong assumption will cause significant rework (4-8 hours)
- **Medium:** Wrong assumption will cause minor issues (2-4 hours)
- **Low:** Wrong assumption has minimal impact (<2 hours)

---

## Summary Statistics

**Total Unknowns:** 27  
**By Priority:**
- Critical: 7 (26%)
- High: 11 (41%)
- Medium: 7 (26%)
- Low: 2 (7%)

**By Category:**
- Category 1 (Status Summary Report Generator): 4 unknowns
- Category 2 (Failure Analysis Report): 3 unknowns
- Category 3 (Progress Tracking): 2 unknowns
- Category 4 (Parse Failure Gap Analysis): 4 unknowns
- Category 5 (Translation Failure Gap Analysis): 3 unknowns
- Category 6 (Solve Failure Gap Analysis): 2 unknowns
- Category 7 (Improvement Roadmap): 2 unknowns
- Category 8 (Identify Top Parse Blockers): 4 unknowns
- Category 9 (Implement Priority Parser Features): 3 unknowns

**Estimated Research Time:** 28-36 hours (spread across prep phase)

---

## Task-to-Unknown Mapping

This table maps each prep task to the unknowns it will verify:

| Prep Task | Description | Unknowns Verified |
|-----------|-------------|-------------------|
| Task 2 | Assess Current Baseline Metrics and Blockers | 4.1, 4.2, 5.1, 6.1, 8.1 |
| Task 3 | Research Report Generation Approaches | 1.1, 1.2, 1.3, 2.1 |
| Task 4 | Design Failure Analysis Report Schema | 2.2, 2.3, 4.3 |
| Task 5 | Survey GAMS Grammar Extension Patterns | 8.2, 9.1, 9.2 |
| Task 6 | Analyze Top Parse Blockers (lexer_invalid_char) | 4.4, 8.1, 8.3, 8.4 |
| Task 7 | Research PATH Syntax Error Patterns | 4.2, 6.2 |
| Task 8 | Design Progress Tracking Schema | 1.4, 3.1, 3.2 |
| Task 9 | Review Sprint 15 Deliverables and Learnings | 5.2, 5.3, 7.1, 7.2 |
| Task 10 | Plan Sprint 16 Detailed Schedule | All unknowns (integration) |

---

## Table of Contents

1. [Category 1: Reporting Infrastructure - Status Summary Report Generator](#category-1-reporting-infrastructure---status-summary-report-generator)
2. [Category 2: Reporting Infrastructure - Failure Analysis Report](#category-2-reporting-infrastructure---failure-analysis-report)
3. [Category 3: Reporting Infrastructure - Progress Tracking](#category-3-reporting-infrastructure---progress-tracking)
4. [Category 4: Gap Analysis - Parse Failure Gap Analysis](#category-4-gap-analysis---parse-failure-gap-analysis)
5. [Category 5: Gap Analysis - Translation Failure Gap Analysis](#category-5-gap-analysis---translation-failure-gap-analysis)
6. [Category 6: Gap Analysis - Solve Failure Gap Analysis](#category-6-gap-analysis---solve-failure-gap-analysis)
7. [Category 7: Gap Analysis - Improvement Roadmap](#category-7-gap-analysis---improvement-roadmap)
8. [Category 8: Targeted Parser Improvements - Identify Top Parse Blockers](#category-8-targeted-parser-improvements---identify-top-parse-blockers)
9. [Category 9: Targeted Parser Improvements - Implement Priority Parser Features](#category-9-targeted-parser-improvements---implement-priority-parser-features)
10. [Template for New Unknowns](#template-for-new-unknowns)
11. [Next Steps](#next-steps)
12. [Appendix: Task-to-Unknown Mapping Details](#appendix-task-to-unknown-mapping-details)

---

# Category 1: Reporting Infrastructure - Status Summary Report Generator

## Unknown 1.1: What report output format(s) should generate_report.py support?

### Priority
**High** - Affects implementation scope and user experience

### Assumption
The report generator should produce Markdown as primary format with optional JSON for programmatic access, following the pattern of manually-created Sprint 15 reports.

### Research Questions
1. Is Markdown sufficient for all use cases or do we need HTML?
2. What Markdown rendering will be used (GitHub, static site generator)?
3. Should JSON be a separate output or embedded in Markdown?
4. What templating approach works best (Jinja2, f-strings, dedicated library)?
5. How do other optimization testing frameworks format reports?

### How to Verify

**Test Case 1: Analyze existing manual reports**
```bash
# Review structure of Sprint 15 reports
head -100 docs/testing/SPRINT_BASELINE.md
head -100 docs/testing/GAMSLIB_TESTING.md
```

**Test Case 2: Test Jinja2 for Markdown generation**
```python
from jinja2 import Template
template = Template("# Status Report\n- Parse: {{ parse_rate }}%")
print(template.render(parse_rate=21.3))
```

**Test Case 3: Survey optimization testing frameworks**
- CUTEst: Report format?
- GAMSLIB official: Report format?
- Optimization benchmarking tools: Common formats?

### Risk if Wrong
- Creating multiple formats increases maintenance burden
- Wrong format limits adoption/usability
- Template complexity delays implementation

### Estimated Research Time
2 hours (format survey, template testing)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.2: What metrics should be included in GAMSLIB_STATUS.md?

### Priority
**High** - Affects report usefulness

### Assumption
Status report should include: total models, convex models, parse/translate/solve success rates, full pipeline success, error distribution by category, and filtering statistics.

### Research Questions
1. What metrics are most actionable for identifying improvements?
2. Should we include per-model tables or just aggregates?
3. How granular should error categorization be in summary?
4. What comparisons to baseline should be shown?
5. What is the ideal report length (quick summary vs. comprehensive)?

### How to Verify

**Test Case 1: Review Sprint 15 baseline_metrics.json**
```bash
cat tests/output/baseline_metrics.json | jq '.'
# What metrics are already tracked?
```

**Test Case 2: Analyze PROJECT_PLAN.md requirements**
```
From PROJECT_PLAN.md Sprint 16:
- Total models in corpus
- Models verified as convex
- Parse/translate/solve success rates
- Overall pipeline success rate
- Group by failure type
```

**Test Case 3: User research (hypothetical)**
- What would a developer want to see first?
- What enables quick identification of improvement targets?

### Risk if Wrong
- Report too verbose: Users skip important information
- Report too sparse: Missing actionable insights
- Wrong metrics: Can't track improvement over time

### Estimated Research Time
1-2 hours (requirements analysis, mockup design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.3: Should generate_report.py use a template system or string formatting?

### Priority
**Medium** - Affects code maintainability

### Assumption
Jinja2 templates provide the best balance of flexibility and maintainability for report generation, allowing non-developers to modify report formats.

### Research Questions
1. Is Jinja2 already a project dependency?
2. What's the learning curve for Jinja2 templates?
3. Would f-strings suffice for our report complexity?
4. How to handle dynamic tables in templates?
5. What's the testing strategy for template-based reports?

### How to Verify

**Test Case 1: Check project dependencies**
```bash
grep -i jinja pyproject.toml
# Is Jinja2 already installed?
```

**Test Case 2: Create prototype with both approaches**
```python
# Approach 1: Jinja2
from jinja2 import Environment, FileSystemLoader
# ...

# Approach 2: f-strings
report = f"# Status\n- Parse: {parse_rate}%\n"
```

**Test Case 3: Estimate complexity**
- Number of tables to generate
- Number of conditional sections
- Need for loops/iteration

### Risk if Wrong
- Over-engineering: Jinja2 for simple reports
- Under-engineering: f-strings can't handle dynamic content
- Maintenance burden: Hard to modify reports

### Estimated Research Time
1 hour (prototype both approaches)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 1.4: How should report timestamps and versioning be handled?

### Priority
**Low** - Affects traceability

### Assumption
Reports should include generation timestamp, nlp2mcp version, and data source file path for reproducibility and debugging.

### Research Questions
1. What timestamp format is most useful (ISO 8601, human-readable)?
2. How to include nlp2mcp version programmatically?
3. Should git commit hash be included for exact reproducibility?
4. How to handle reports generated from outdated data?
5. Should old reports be archived or overwritten?

### How to Verify

**Test Case 1: Check version access**
```python
# Can we access nlp2mcp version?
from importlib.metadata import version
print(version("nlp2mcp"))
```

**Test Case 2: Review existing reports**
```bash
grep -i "generated\|version\|date" docs/testing/SPRINT_BASELINE.md
```

### Risk if Wrong
- Reports without timestamps cause confusion
- Missing version info prevents bug reproduction
- Overwriting history loses trend analysis

### Estimated Research Time
30 minutes (quick decisions)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 2: Reporting Infrastructure - Failure Analysis Report

## Unknown 2.1: What failure grouping granularity provides actionable insights?

### Priority
**High** - Affects report usefulness for improvement planning

### Assumption
Failures should be grouped at two levels: (1) high-level category (parse/translate/solve) and (2) specific error type from the 47-category taxonomy, with model counts and percentage.

### Research Questions
1. Is the 47-category taxonomy too granular for summary reports?
2. Should we create "rollup" categories for common themes?
3. How to present nested groupings (category → subcategory → models)?
4. What error threshold is significant (e.g., show only errors affecting >3 models)?
5. How do other testing frameworks group failures?

### How to Verify

**Test Case 1: Analyze current error distribution**
```bash
# Get error category distribution
cat tests/output/pipeline_results.json | jq '.models[] | .parse_outcome' | sort | uniq -c | sort -rn
```

**Test Case 2: Test different grouping approaches**
- All 47 categories: Too much?
- Only top 10: Miss long tail?
- Hierarchical: Category → specific error → models

**Test Case 3: Review IMPROVEMENT_ROADMAP requirements**
```
From PROJECT_PLAN.md:
- List gaps with priority (HIGH/MEDIUM/LOW)
- Estimate fix complexity
- Map to remaining sprint work
```

### Risk if Wrong
- Too granular: Report overwhelming, key issues lost
- Too aggregated: Can't identify specific fixes
- Wrong grouping: Improvement priorities unclear

### Estimated Research Time
2 hours (error analysis, grouping design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.2: Should FAILURE_ANALYSIS.md include example error messages?

### Priority
**Medium** - Affects debugging utility

### Assumption
Failure analysis should include representative error messages for each category to help developers understand the root cause without running individual models.

### Research Questions
1. How long are typical error messages?
2. Do error messages contain sensitive/variable information?
3. Should we show 1 example or multiple per category?
4. How to format code/error in Markdown readably?
5. Will error messages change as parser evolves?

### How to Verify

**Test Case 1: Sample error messages**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome == "lexer_invalid_char") | .parse_error' | head -5
```

**Test Case 2: Check error message length**
```bash
# Average length of error messages
cat tests/output/pipeline_results.json | jq -r '.models[] | .parse_error // empty' | awk '{print length}' | sort -n | tail -20
```

### Risk if Wrong
- No examples: Developers must run failing models to understand errors
- Too many examples: Report becomes unwieldy
- Stale examples: Confusing after parser changes

### Estimated Research Time
1 hour (error analysis, format decision)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 2.3: How should improvement recommendations be generated?

### Priority
**High** - Affects actionability of failure analysis

### Assumption
Improvement recommendations can be derived from error patterns: high-count errors with low fix complexity should be prioritized. Manual annotation may be needed for fix complexity estimates.

### Research Questions
1. Can fix complexity be estimated automatically from error type?
2. Should recommendations be generated or manually maintained?
3. How to connect error categories to specific grammar/parser changes?
4. What format for recommendations (table, prose, checklist)?
5. How do recommendations flow to IMPROVEMENT_ROADMAP.md?

### How to Verify

**Test Case 1: Categorize fix complexity**
```
lexer_invalid_char (109 models):
  - Dollar control: Medium (lexer mode)
  - Special chars: Low (regex update)
  - Unknown: High (requires analysis)
```

**Test Case 2: Review parser/grammar structure**
```bash
wc -l src/nlp2mcp/parser/gams.lark
# Understanding grammar helps estimate fix complexity
```

### Risk if Wrong
- Auto-generated recommendations: May be wrong or misleading
- Manual only: Becomes stale quickly
- Wrong complexity estimates: Mispriorize improvements

### Estimated Research Time
2 hours (complexity analysis, format design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 3: Reporting Infrastructure - Progress Tracking

## Unknown 3.1: What schema should progress_history.json follow?

### Priority
**Medium** - Affects historical analysis capability

### Assumption
progress_history.json should store timestamped snapshots with success rates, error counts, and nlp2mcp version, enabling trend analysis and regression detection.

### Research Questions
1. What granularity for snapshots (per-run, per-day, per-sprint)?
2. Should individual model status changes be tracked?
3. How to handle schema changes over time?
4. What's the expected file size after many snapshots?
5. Should this be JSON or SQLite for querying?

### How to Verify

**Test Case 1: Design schema**
```json
{
  "snapshots": [
    {
      "timestamp": "2026-01-16T10:00:00Z",
      "nlp2mcp_version": "0.4.0",
      "parse": {"success": 34, "total": 160, "rate": 0.213},
      "translate": {"success": 17, "total": 34, "rate": 0.500},
      "solve": {"success": 3, "total": 17, "rate": 0.176},
      "notes": "Sprint 15 baseline"
    }
  ]
}
```

**Test Case 2: Estimate storage**
- Per snapshot: ~500 bytes
- 100 snapshots: ~50KB (manageable as JSON)

### Risk if Wrong
- Too granular: Large file, slow queries
- Too sparse: Can't identify when regressions occurred
- Wrong schema: Migration pain later

### Estimated Research Time
1 hour (schema design, storage estimation)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 3.2: How to detect and alert on regressions?

### Priority
**Medium** - Affects development confidence

### Assumption
Regression detection should compare current run to previous snapshot and flag if any success rate decreases, with configurable thresholds (e.g., alert if >2% regression).

### Research Questions
1. What constitutes a regression vs. statistical noise?
2. Should individual model regressions be tracked?
3. How to present regression alerts (exit code, report section)?
4. What tolerance for "no change" (exactly equal vs. ±1%)?
5. Should CI fail on regression?

### How to Verify

**Test Case 1: Define regression criteria**
```python
def is_regression(current, baseline, threshold=0.02):
    return (baseline - current) > threshold
```

**Test Case 2: Test with simulated data**
- Baseline: 21.3% parse rate
- Current: 20.0% parse rate
- Is this significant regression?

### Risk if Wrong
- Too sensitive: False alarms, alert fatigue
- Too lenient: Miss real regressions
- No alerts: Regressions go unnoticed

### Estimated Research Time
1 hour (threshold design, alerting approach)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 4: Gap Analysis - Parse Failure Gap Analysis

## Unknown 4.1: What is the actual breakdown of lexer_invalid_char errors?

### Priority
**Critical** - lexer_invalid_char blocks 109/160 models (68.1%)

### Assumption
lexer_invalid_char errors are primarily caused by dollar control options ($ontext, $offtext, $include), embedded code ($call, $execute), and special characters, which can be categorized by examining error messages and source files.

### Research Questions
1. What percentage of lexer_invalid_char are dollar control options?
2. What percentage are embedded GAMS execution commands?
3. What percentage are special/non-ASCII characters?
4. Are there other unexpected causes?
5. What is the effort to fix each subcategory?

### How to Verify

**Test Case 1: Sample failing models**
```bash
# Get 20 models with lexer_invalid_char
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -20
```

**Test Case 2: Examine error patterns**
```bash
# Check for common patterns in error messages
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .parse_error' | grep -o "Unexpected character.*" | sort | uniq -c | sort -rn
```

**Test Case 3: Examine source files for patterns**
```bash
# Check for dollar control in failing models
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -5); do
    echo "=== $model ==="
    grep -n '^\$' data/gamslib/raw/$model.gms | head -5
done
```

### Risk if Wrong
- Wrong subcategorization leads to wrong fix priorities
- Over-investment in minor subcategories
- Underestimate complexity of major subcategories

### Estimated Research Time
3-4 hours (comprehensive error analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.2: What GAMS syntax constructs cause path_syntax_error?

### Priority
**High** - path_syntax_error affects 14 models (8.8%)

### Assumption
path_syntax_error is caused by file path references in GAMS models ($include, $batinclude, file paths), which may be fixable by improving path handling in the lexer.

### Research Questions
1. What specific syntax triggers path_syntax_error?
2. Are these include/batinclude statements?
3. Are paths relative or absolute?
4. Can we skip/ignore external file references?
5. What is the fix complexity?

### How to Verify

**Test Case 1: List models with path_syntax_error**
```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "path_syntax_error") | "\(.model_name): \(.parse_error)"'
```

**Test Case 2: Examine source files**
```bash
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "path_syntax_error") | .model_name'); do
    echo "=== $model ==="
    head -30 data/gamslib/raw/$model.gms
done
```

### Risk if Wrong
- Over-engineer path handling for uncommon cases
- Ignore fixable issues
- Conflate path errors with other lexer errors

### Estimated Research Time
2 hours (error analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.3: How should parse failures be prioritized for improvement?

### Priority
**High** - Affects Sprint 16 parser improvement focus

### Assumption
Parse failures should be prioritized by: (1) model count (most models unblocked), (2) fix complexity (prefer low/medium), and (3) downstream value (convex models more valuable).

### Research Questions
1. What weighting between model count and fix complexity?
2. Should convex models be weighted higher?
3. How to estimate fix complexity without implementing?
4. What's the marginal value of fixing each category?
5. Is there a "point of diminishing returns"?

### How to Verify

**Test Case 1: Create priority matrix**
```
Error Category    | Models | Fix Complexity | Priority Score
lexer_invalid_char| 109    | Medium-High    | ?
path_syntax_error | 14     | Medium         | ?
model_no_obj_def  | 5      | N/A (model)    | Skip
```

**Test Case 2: Calculate maximum improvement potential**
- If we fix lexer_invalid_char: Parse rate from 21.3% to up to 89.4%
- If we fix path_syntax_error: Additional 8.8%
- What's realistic target for Sprint 16?

### Risk if Wrong
- Fix low-impact errors first
- Underestimate complexity, overcommit
- Ignore high-value convex models

### Estimated Research Time
2 hours (prioritization framework design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 4.4: Are lexer_invalid_char errors from syntax we should support or intentionally exclude?

### Priority
**Critical** - Affects scope of parser improvements

### Assumption
Some GAMS features causing lexer_invalid_char (e.g., $call, $execute, embedded Python) should be intentionally excluded as they require GAMS execution, not just parsing.

### Research Questions
1. What dollar control options are essential for model definition?
2. What options are execution-time only and can be skipped?
3. Can we distinguish "parse-needed" from "execute-needed" constructs?
4. What is the GAMS community expectation for preprocessor handling?
5. Should we document intentional exclusions?

### How to Verify

**Test Case 1: Categorize dollar control options**
```
Parse-needed (must support):
- $ontext/$offtext (comments)
- $include (static file inclusion)
- $if/$else/$endif (conditional compilation)

Execute-needed (can skip):
- $call (shell commands)
- $execute (GAMS commands)
- $echo (output)
```

**Test Case 2: Survey GAMS preprocessor documentation**
- What are all dollar control options?
- Which affect model structure vs. execution?

### Risk if Wrong
- Try to support impossible features (GAMS execution)
- Exclude features that could be supported
- Confusion about tool scope

### Estimated Research Time
2 hours (GAMS documentation research)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 5: Gap Analysis - Translation Failure Gap Analysis

## Unknown 5.1: What is the actual breakdown of translation failures?

### Priority
**High** - 17 models fail translation (50% of parsed)

### Assumption
Translation failures are caused by unsupported functions (card, ord, gamma), unsupported constructs (IndexOffset), and missing objective definitions.

### Research Questions
1. What percentage of translation failures are unsupported functions?
2. What percentage are structural issues (no objective, domain mismatch)?
3. Can any translation failures be fixed at parse stage?
4. What's the effort to support additional functions?
5. Are there common patterns we're missing?

### How to Verify

**Test Case 1: Analyze translation errors**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome != null and .translate_outcome != "translate_success") | .translate_outcome' | sort | uniq -c | sort -rn
```

**Test Case 2: Review specific error messages**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome != null and .translate_outcome != "translate_success") | "\(.model_name): \(.translate_error)"'
```

### Risk if Wrong
- Focus on wrong translation improvements
- Miss low-hanging fruit
- Overestimate improvement potential

### Estimated Research Time
2 hours (error analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.2: Are translation failures fixable in Sprint 16 or beyond?

### Priority
**Medium** - Affects sprint planning

### Assumption
Some translation failures (e.g., unsupported intrinsic functions) require significant effort and should be deferred to Sprint 17, while others (e.g., improved error handling) can be addressed in Sprint 16.

### Research Questions
1. What translation fixes are "quick wins" (<2 hours)?
2. What translation fixes are major efforts (>8 hours)?
3. Should Sprint 16 focus only on parser, not translation?
4. What's the dependency between parser and translation fixes?
5. What's the expected ROI of translation fixes?

### How to Verify

**Test Case 1: Review Sprint 17 scope**
```
From PROJECT_PLAN.md Sprint 17:
- Translation Improvements (~8-10h)
- Identify Top Translation Blockers
- Implement Translation Fixes
```

**Test Case 2: Estimate translation fix complexity**
- Add gamma function: High (calculus, special cases)
- Improve error messages: Low
- Handle IndexOffset: Medium (domain analysis)

### Risk if Wrong
- Overcommit Sprint 16 to translation work
- Miss parser improvements in Sprint 16
- Duplicate effort between sprints

### Estimated Research Time
1 hour (scope analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 5.3: Do translation failures correlate with model characteristics?

### Priority
**Medium** - Affects improvement strategy

### Assumption
Translation failures may correlate with model complexity (number of variables, equations) or specific GAMS features used, enabling better targeting of improvements.

### Research Questions
1. Are larger models more likely to fail translation?
2. Do certain GAMS features (e.g., sets, parameters) correlate with failures?
3. Are LP models more likely to translate successfully than NLP?
4. Does model domain (transportation, economics) affect translation?
5. Can we predict translation success from parsed IR?

### How to Verify

**Test Case 1: Compare model characteristics**
```bash
# Get characteristics of successful vs. failed translations
# (Requires extracting model stats from IR)
```

**Test Case 2: Check model type correlation**
```bash
# Compare LP vs. NLP vs. MIP translation success
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome != null) | {model: .model_name, type: .gamslib_type, outcome: .translate_outcome}'
```

### Risk if Wrong
- Miss important correlation, wrong improvement strategy
- Over-complicate analysis for weak correlations
- Waste time on non-actionable insights

### Estimated Research Time
1-2 hours (correlation analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 6: Gap Analysis - Solve Failure Gap Analysis

## Unknown 6.1: What is the actual breakdown of solve failures?

### Priority
**High** - 14 models fail solve (82.4% of translated)

### Assumption
Solve failures are primarily due to PATH solver issues, not nlp2mcp translation bugs, based on Sprint 15 baseline showing high solve failure rate.

### Research Questions
1. What percentage are PATH solver convergence issues?
2. What percentage are generated MCP syntax errors?
3. What percentage are objective mismatches (nlp2mcp bug)?
4. Are there patterns in solve failures?
5. Can any solve failures be fixed in translation stage?

### How to Verify

**Test Case 1: Analyze solve outcomes**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome != null and .solve_outcome != "solve_success") | .solve_outcome' | sort | uniq -c | sort -rn
```

**Test Case 2: Check for objective mismatches**
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome == "compare_objective_mismatch") | .model_name'
```

### Risk if Wrong
- Attribute solver issues to nlp2mcp bugs
- Miss actual nlp2mcp bugs in solve stage
- Over-invest in unfixable solver issues

### Estimated Research Time
2 hours (solve error analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 6.2: Are solve failures addressable in nlp2mcp or inherent model difficulties?

### Priority
**Medium** - Affects improvement expectations

### Assumption
Many solve failures are inherent model difficulties (non-convex, poorly scaled) or PATH solver limitations, not nlp2mcp bugs.

### Research Questions
1. What percentage of solve failures are nlp2mcp bugs?
2. What percentage are inherent to the model?
3. Can we improve solve rate by better MCP generation?
4. Are there PATH solver configuration improvements?
5. What is realistic solve success target?

### How to Verify

**Test Case 1: Compare NLP and MCP solve status**
```bash
# Models where NLP succeeded but MCP failed = potential nlp2mcp issue
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome == "compare_status_mismatch") | .model_name'
```

**Test Case 2: Review PATH solver settings**
- Are we using optimal PATH settings?
- Could different tolerances improve solve rate?

### Risk if Wrong
- Chase unfixable solve issues
- Miss actual nlp2mcp improvements
- Set unrealistic targets

### Estimated Research Time
1-2 hours (analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 7: Gap Analysis - Improvement Roadmap

## Unknown 7.1: What format should IMPROVEMENT_ROADMAP.md follow?

### Priority
**Medium** - Affects usability and adoption

### Assumption
Improvement roadmap should list gaps prioritized by impact and effort, with clear ownership and target sprint, following standard product roadmap formats.

### Research Questions
1. What fields should each improvement item have?
2. How to represent priority (HIGH/MEDIUM/LOW or numeric)?
3. Should improvements be grouped by category or priority?
4. How to link to specific error categories?
5. How to track roadmap progress?

### How to Verify

**Test Case 1: Survey roadmap formats**
- GitHub project boards
- Markdown-based roadmaps
- Optimization tool changelogs

**Test Case 2: Design schema**
```markdown
## Improvement Roadmap

### HIGH Priority
| Issue | Models Affected | Effort | Target Sprint | Status |
|-------|-----------------|--------|---------------|--------|
| Dollar control handling | 109 | Medium | 16 | In Progress |
```

### Risk if Wrong
- Roadmap not actionable
- Wrong priority representation
- Difficult to track progress

### Estimated Research Time
1 hour (format design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 7.2: How should improvement priorities be determined?

### Priority
**High** - Affects Sprint 16 focus

### Assumption
Priorities should be determined by a scoring formula: Score = (Models Affected) × (Convex Weight) / (Effort Estimate), favoring high-impact, low-effort improvements.

### Research Questions
1. What weights for models vs. effort vs. convexity?
2. Should we use linear or non-linear scoring?
3. How to estimate effort before implementation?
4. Should subjective factors (risk, dependencies) be included?
5. How to handle uncertainty in estimates?

### How to Verify

**Test Case 1: Apply scoring formula**
```python
# Example scoring
def priority_score(models, convex_pct, effort):
    return (models * (1 + convex_pct)) / effort

# Dollar control: 109 models, 70% convex, effort=3
score_dollar = priority_score(109, 0.7, 3)  # = 61.7

# Path syntax: 14 models, 50% convex, effort=2
score_path = priority_score(14, 0.5, 2)  # = 10.5
```

**Test Case 2: Compare to intuitive priorities**
- Does scoring match expert judgment?
- Are there obvious mistakes?

### Risk if Wrong
- Wrong priorities, suboptimal sprint focus
- Over-engineer scoring, delay decisions
- Ignore important subjective factors

### Estimated Research Time
1 hour (scoring design)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 8: Targeted Parser Improvements - Identify Top Parse Blockers

## Unknown 8.1: Which parse blockers should be targeted in Sprint 16?

### Priority
**Critical** - Defines Sprint 16 parser improvement scope

### Assumption
Sprint 16 should target lexer_invalid_char (specifically dollar control options) and path_syntax_error as the top blockers, aiming to unblock 50+ models.

### Research Questions
1. What is the actual fix complexity for dollar control?
2. Can we fix a subset of dollar control (e.g., $ontext/$offtext only)?
3. What is realistic target for Sprint 16 (30% improvement?)?
4. Should we target multiple small issues or one large issue?
5. What is dependency between different blockers?

### How to Verify

**Test Case 1: Estimate improvement potential**
```
If we fix:
- $ontext/$offtext: Unblocks ~X models
- $include: Unblocks ~Y models
- Path syntax: Unblocks 14 models
Total potential: X + Y + 14 models
```

**Test Case 2: Review parser change complexity**
```bash
# Analyze grammar structure
cat src/nlp2mcp/parser/gams.lark | head -50
```

### Risk if Wrong
- Target wrong blockers, miss improvement goals
- Underestimate complexity, miss deadlines
- Over-commit, create regressions

### Estimated Research Time
2-3 hours (blocker analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 8.2: Can grammar extensions be made without breaking existing parses?

### Priority
**Critical** - Affects parser improvement safety

### Assumption
Grammar extensions for new GAMS constructs can be added as optional rules without breaking existing successful parses, if carefully designed with proper precedence.

### Research Questions
1. What is the current grammar structure?
2. How to add new rules without conflicts?
3. What testing strategy ensures no regressions?
4. Can Lark handle ambiguous grammar gracefully?
5. What is the risk of subtle parsing changes?

### How to Verify

**Test Case 1: Review Lark grammar features**
```python
# Test adding optional rules
from lark import Lark
grammar = """
start: statement+
statement: old_statement | new_statement
old_statement: "old" NAME
new_statement: "new" NAME
NAME: /[a-z]+/
"""
```

**Test Case 2: Run regression tests**
```bash
# Run all existing parser tests
pytest tests/ir/test_parser.py -v
```

### Risk if Wrong
- Grammar changes break existing parsing
- Subtle behavioral changes undetected
- Major refactoring needed mid-sprint

### Estimated Research Time
2 hours (grammar analysis, regression testing)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 8.3: What is the correct approach to handle dollar control options?

### Priority
**Critical** - Dollar control is the largest blocker (109 models)

### Assumption
Dollar control options can be handled by adding a lexer mode that skips content between $ontext/$offtext and treats $include as comments (since we can't follow includes).

### Research Questions
1. Does Lark support lexer modes for region skipping?
2. Should $include content be skipped or fail gracefully?
3. How to handle nested dollar control ($if inside $ontext)?
4. What about $setglobal, $setlocal (macro definitions)?
5. Should we preprocess files or handle in grammar?

### How to Verify

**Test Case 1: Test Lark lexer modes**
```python
# Can we skip regions in Lark?
from lark import Lark
grammar = """
%ignore /$ontext[\\s\\S]*?$offtext/m
"""
```

**Test Case 2: Analyze dollar control usage in GAMSLIB**
```bash
# What dollar control options are used?
grep -rh '^\$' data/gamslib/raw/*.gms | sed 's/ .*//' | sort | uniq -c | sort -rn | head -20
```

### Risk if Wrong
- Choose wrong implementation approach, major refactoring
- Partially handle dollar control, inconsistent behavior
- Create security issues (code injection via $include)

### Estimated Research Time
3 hours (Lark research, GAMSLIB analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 8.4: What specific characters cause lexer_invalid_char beyond dollar control?

### Priority
**High** - May reveal additional quick wins

### Assumption
Beyond dollar control, lexer_invalid_char may be caused by extended ASCII, Unicode characters, or unusual GAMS syntax variants.

### Research Questions
1. What characters besides '$' trigger lexer_invalid_char?
2. Are there encoding issues (UTF-8 vs. Latin-1)?
3. Can character class in lexer be extended easily?
4. Are there GAMS syntax variants we don't support?
5. What's the fix complexity for each character type?

### How to Verify

**Test Case 1: Extract error character from messages**
```bash
# Get specific characters mentioned in errors
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .parse_error' | grep -o "character '[^']*'" | sort | uniq -c | sort -rn
```

**Test Case 2: Check for encoding issues**
```bash
# Look for non-ASCII in failing models
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -10); do
    file data/gamslib/raw/$model.gms
    grep -P '[^\x00-\x7F]' data/gamslib/raw/$model.gms | head -1
done
```

### Risk if Wrong
- Miss quick wins for character fixes
- Over-complicate for rare edge cases
- Introduce encoding-related bugs

### Estimated Research Time
1-2 hours (character analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Category 9: Targeted Parser Improvements - Implement Priority Parser Features

## Unknown 9.1: What is the correct grammar change for dollar control comment blocks?

### Priority
**Critical** - Enables largest parser improvement

### Assumption
Dollar control comment blocks ($ontext/$offtext) can be handled by adding a regex pattern to skip them in the Lark lexer, similar to how regular comments are handled.

### Research Questions
1. What is the exact regex pattern for $ontext/$offtext?
2. How to handle case sensitivity ($ONTEXT vs $ontext)?
3. Where does the pattern go in gams.lark?
4. How to test the change thoroughly?
5. What edge cases exist (nested, unclosed)?

### How to Verify

**Test Case 1: Create regex pattern**
```python
import re
# Test pattern on sample content
pattern = re.compile(r'\$ontext.*?\$offtext', re.IGNORECASE | re.DOTALL)
test = "$ontext\nThis is a comment\n$offtext"
assert pattern.match(test)
```

**Test Case 2: Test with Lark**
```python
from lark import Lark
grammar = """
%ignore /\\$[Oo][Nn][Tt][Ee][Xx][Tt][\\s\\S]*?\\$[Oo][Ff][Ff][Tt][Ee][Xx][Tt]/
"""
```

**Test Case 3: Test with GAMSLIB models**
```bash
# Try parsing a model with $ontext/$offtext
python -m src.cli data/gamslib/raw/MODEL_WITH_ONTEXT.gms -o /dev/null
```

### Risk if Wrong
- Wrong pattern fails to skip blocks
- Pattern too greedy, skips real content
- Case sensitivity issues

### Estimated Research Time
2 hours (pattern development and testing)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 9.2: What testing strategy ensures parser changes don't regress?

### Priority
**High** - Ensures parser improvement quality

### Assumption
Parser changes should be validated by: (1) running all existing parser tests, (2) re-running batch_parse on GAMSLIB to check no regressions, and (3) verifying newly-passing models actually parse correctly.

### Research Questions
1. What is the current parser test coverage?
2. How long does full GAMSLIB batch_parse take?
3. How to detect subtle parsing changes (same pass/fail but different IR)?
4. Should we add golden file tests for IR output?
5. What CI checks should be added?

### How to Verify

**Test Case 1: Check current test coverage**
```bash
pytest tests/ir/test_parser.py --cov=src/ir/parser --cov-report=term-missing
```

**Test Case 2: Benchmark batch_parse time**
```bash
time python scripts/gamslib/batch_parse.py --dry-run
```

**Test Case 3: Design regression detection**
```python
# Compare before/after model status
def check_regression(before_json, after_json):
    for model in before_json:
        if before_json[model].parse_success and not after_json[model].parse_success:
            return f"REGRESSION: {model}"
    return "OK"
```

### Risk if Wrong
- Silent regressions undetected
- Over-testing slows development
- False positives block valid changes

### Estimated Research Time
1-2 hours (test coverage analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

## Unknown 9.3: How many models can realistically be unblocked in Sprint 16?

### Priority
**High** - Sets expectations for sprint success

### Assumption
Sprint 16 can realistically unblock 30-50 additional models (improving parse rate from 21.3% to ~40-50%), primarily through dollar control handling.

### Research Questions
1. What is the maximum potential if all lexer_invalid_char are fixed?
2. What percentage of lexer_invalid_char are dollar control only?
3. What is realistic implementation scope in ~10-14 hours?
4. What is acceptable minimum improvement to declare success?
5. Should we set stretch goals vs. minimum goals?

### How to Verify

**Test Case 1: Calculate maximum potential**
```python
# Maximum if all lexer_invalid_char fixed
current_parse = 34  # Sprint 15 baseline
lexer_blocked = 109
max_parse = current_parse + lexer_blocked  # = 143/160 = 89.4%
```

**Test Case 2: Estimate dollar-control-only subset**
```bash
# How many lexer_invalid_char are dollar control?
# (Requires analysis from Unknown 4.1)
```

**Test Case 3: Set targets**
```
Minimum success: +10% parse rate (from 21.3% to 31.3%, +16 models)
Target: +20% parse rate (from 21.3% to 41.3%, +32 models)
Stretch: +30% parse rate (from 21.3% to 51.3%, +48 models)
```

### Risk if Wrong
- Overpromise, underdeliver
- Underpromise, miss easy wins
- Wrong metrics for success

### Estimated Research Time
1 hour (potential analysis)

### Owner
Development team

### Verification Results
🔍 Status: INCOMPLETE

---

# Template for New Unknowns

## Unknown X.Y: [Short descriptive title]

### Priority
**[Critical/High/Medium/Low]** - [Brief justification]

### Assumption
[State the assumption being made]

### Research Questions
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]
4. [Specific question 4]
5. [Specific question 5]

### How to Verify

**Test Case 1: [Description]**
```bash
# Commands or code to verify
```

**Test Case 2: [Description]**
```bash
# Commands or code to verify
```

### Risk if Wrong
[What happens if assumption is incorrect]

### Estimated Research Time
[X hours]

### Owner
[Development team/specific person]

### Verification Results
🔍 Status: INCOMPLETE

---

# Next Steps

## Pre-Sprint 16 Research Priorities

1. **Critical (verify before Sprint 16 Day 1):**
   - Unknown 4.1: lexer_invalid_char breakdown
   - Unknown 4.4: Dollar control support scope
   - Unknown 8.1: Parse blocker targets
   - Unknown 8.2: Grammar extension safety
   - Unknown 8.3: Dollar control approach
   - Unknown 9.1: Grammar change for $ontext/$offtext

2. **High (verify in first days of sprint):**
   - Unknown 1.1: Report format
   - Unknown 1.2: Status report metrics
   - Unknown 2.1: Failure grouping granularity
   - Unknown 2.3: Improvement recommendations
   - Unknown 4.2: path_syntax_error causes
   - Unknown 4.3: Prioritization framework
   - Unknown 5.1: Translation failure breakdown
   - Unknown 7.2: Improvement priority formula
   - Unknown 8.4: Other lexer_invalid_char causes
   - Unknown 9.2: Regression testing strategy
   - Unknown 9.3: Realistic improvement targets

3. **Medium (can verify during implementation):**
   - Unknown 1.3: Template system choice
   - Unknown 2.2: Example error messages
   - Unknown 3.1: Progress history schema
   - Unknown 3.2: Regression detection
   - Unknown 5.2: Translation fix sprint
   - Unknown 5.3: Translation correlation analysis
   - Unknown 6.2: Solve failure addressability
   - Unknown 7.1: Roadmap format

4. **Low (can defer if needed):**
   - Unknown 1.4: Timestamp handling
   - Unknown 6.1: Solve failure breakdown

## Research Assignments

| Task | Unknowns | Prep Task Reference |
|------|----------|---------------------|
| Baseline analysis | 4.1, 4.2, 5.1, 6.1, 8.1 | Task 2 |
| Report research | 1.1, 1.2, 1.3, 2.1 | Task 3 |
| Schema design | 2.2, 2.3, 4.3 | Task 4 |
| Grammar survey | 8.2, 9.1, 9.2 | Task 5 |
| Lexer analysis | 4.4, 8.1, 8.3, 8.4 | Task 6 |
| Path error analysis | 4.2, 6.2 | Task 7 |
| Progress tracking | 1.4, 3.1, 3.2 | Task 8 |
| Sprint 15 review | 5.2, 5.3, 7.1, 7.2 | Task 9 |
| Schedule integration | All | Task 10 |

---

# Appendix: Task-to-Unknown Mapping Details

This section provides detailed rationale for which prep tasks verify which unknowns.

## Task 2: Assess Current Baseline Metrics and Blockers

**Unknowns Verified:** 4.1, 4.2, 5.1, 6.1, 8.1

**Rationale:**
- **4.1** (lexer_invalid_char breakdown): Task 2 analyzes error distributions from baseline_metrics.json and pipeline_results.json, which will reveal the subcategories of lexer_invalid_char errors.
- **4.2** (path_syntax_error causes): Task 2's error distribution analysis will identify path_syntax_error patterns.
- **5.1** (translation failure breakdown): Task 2 examines translate error distribution and categorization.
- **6.1** (solve failure breakdown): Task 2 analyzes solve outcome distribution from baseline data.
- **8.1** (parse blocker targets): Task 2's impact ranking table identifies which blockers should be targeted.

## Task 3: Research Report Generation Approaches

**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1

**Rationale:**
- **1.1** (report output formats): Task 3 specifically researches and compares report generation libraries and formats.
- **1.2** (status report metrics): Task 3 analyzes existing manual reports to extract common metrics patterns.
- **1.3** (template system choice): Task 3 prototypes both Jinja2 and f-string approaches.
- **2.1** (failure grouping granularity): Task 3's report design work determines how failures should be grouped.

## Task 4: Design Failure Analysis Report Schema

**Unknowns Verified:** 2.2, 2.3, 4.3

**Rationale:**
- **2.2** (example error messages): Task 4 designs the schema for including representative errors.
- **2.3** (improvement recommendations): Task 4's roadmap section design addresses how recommendations are generated.
- **4.3** (prioritization framework): Task 4 designs the impact/effort ranking format.

## Task 5: Survey GAMS Grammar Extension Patterns

**Unknowns Verified:** 8.2, 9.1, 9.2

**Rationale:**
- **8.2** (grammar extension safety): Task 5 analyzes grammar structure and extension patterns.
- **9.1** (dollar control grammar change): Task 5 researches Lark-specific patterns for region skipping.
- **9.2** (regression testing strategy): Task 5 creates checklist for testing grammar changes.

## Task 6: Analyze Top Parse Blockers (lexer_invalid_char)

**Unknowns Verified:** 4.4, 8.1, 8.3, 8.4

**Rationale:**
- **4.4** (support vs exclude scope): Task 6's categorization determines which features to support vs. intentionally exclude.
- **8.1** (parse blocker targets): Task 6 provides detailed analysis for target selection.
- **8.3** (dollar control approach): Task 6 examines dollar control usage patterns in GAMSLIB.
- **8.4** (other lexer characters): Task 6's character analysis identifies non-dollar causes.

## Task 7: Research PATH Syntax Error Patterns

**Unknowns Verified:** 4.2, 6.2

**Rationale:**
- **4.2** (path_syntax_error causes): Task 7 focuses specifically on path_syntax_error analysis.
- **6.2** (solve failure addressability): Task 7's analysis may reveal if path errors affect solve stage.

## Task 8: Design Progress Tracking Schema

**Unknowns Verified:** 1.4, 3.1, 3.2

**Rationale:**
- **1.4** (timestamp/versioning): Task 8's schema design addresses timestamp format and version tracking.
- **3.1** (progress_history.json schema): Task 8 specifically designs this schema.
- **3.2** (regression detection): Task 8's comparison section design addresses regression alerting.

## Task 9: Review Sprint 15 Deliverables and Learnings

**Unknowns Verified:** 5.2, 5.3, 7.1, 7.2

**Rationale:**
- **5.2** (translation fix sprint): Task 9's scope review clarifies Sprint 16 vs 17 boundaries.
- **5.3** (translation correlation): Task 9's retrospective may reveal patterns from Sprint 15.
- **7.1** (roadmap format): Task 9 reviews how Sprint 15 documented improvements.
- **7.2** (priority determination): Task 9 extracts lessons on prioritization from Sprint 15.

## Task 10: Plan Sprint 16 Detailed Schedule

**Unknowns Verified:** All unknowns (integration)

**Rationale:**
- Task 10 synthesizes findings from all other tasks and must consider all unknowns when creating the schedule. Any unresolved Critical unknowns must be flagged as sprint risks.
