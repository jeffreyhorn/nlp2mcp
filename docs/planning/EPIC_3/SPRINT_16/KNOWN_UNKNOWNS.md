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
**Verified:** 26 (96%)  
**Remaining:** 1 (4%)

**By Priority:**
- Critical: 7 (26%) - 6 verified, 1 remaining
- High: 11 (41%) - 11 verified, 0 remaining
- Medium: 7 (26%) - 7 verified, 0 remaining
- Low: 2 (7%) - 2 verified, 0 remaining

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
✅ Status: VERIFIED (Task 3)

**Verified Date:** January 16, 2026

**Decision:** Markdown (primary) + JSON (secondary)

**Rationale:**
- Markdown is human-readable, renders on GitHub, familiar to developers
- JSON enables CI integration, dashboards, programmatic analysis
- HTML deferred (can generate from Markdown if needed later)

**Libraries Selected:**
- Jinja2 for template-based Markdown generation
- tabulate for table formatting within templates

**Reference:** See `REPORT_DESIGN.md` for full library comparison.

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
✅ Status: VERIFIED (Task 3)

**Verified Date:** January 16, 2026

**Decision:** Include the following metrics in priority order:

1. **Pipeline Summary**
   - Total models in corpus
   - Full pipeline success count and rate (headline metric)
   - Per-stage success rates

2. **Stage Breakdown**
   - Attempted, success, failure counts per stage
   - Success rate percentage
   - Cascade skip count (for translate/solve)

3. **Model Type Analysis**
   - NLP, LP, QCP breakdown
   - Per-type success rates at each stage

4. **Top Blockers**
   - Error category name
   - Affected model count
   - Percentage of stage failures

5. **Environment Info**
   - nlp2mcp version, GAMS version, PATH solver version
   - Generation timestamp

6. **Historical Comparison** (when available)
   - Delta vs. previous baseline
   - Trend indicators

**Ordering Rationale:** Most important first (full pipeline success), then drill-down pattern (summary → stage → type → error details), actionable recommendations last.

**Reference:** See `REPORT_DESIGN.md` "Metrics for GAMSLIB_STATUS.md" section.

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
✅ Status: VERIFIED (Task 3)

**Verified Date:** January 16, 2026

**Decision:** Jinja2 templates with tabulate for table generation

**Rationale:**
1. **Separation of Concerns:** Templates separate content structure from data logic
2. **Maintainability:** Non-developers can modify report format without changing Python code
3. **Flexibility:** Jinja2 supports conditionals, loops, filters, and template inheritance
4. **Proven Pattern:** Used by Ansible, Flask, Django, and many documentation tools
5. **Dynamic Tables:** tabulate library handles table formatting within templates

**Comparison:**
| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| f-strings | Simple, no deps | Hard to maintain, no separation | Rejected |
| Jinja2 | Flexible, maintainable | Learning curve | Selected |

**Implementation:**
```python
from jinja2 import Environment, FileSystemLoader
from tabulate import tabulate
env = Environment(loader=FileSystemLoader('templates'))
env.filters['tabulate'] = lambda data, headers: tabulate(data, headers, tablefmt='github')
```

**Reference:** See `REPORT_DESIGN.md` "Library Comparison" section.

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
✅ Status: VERIFIED (Task 8)

**Verified Date:** January 19, 2026

**Decision:**
- **Timestamp format:** ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SS+00:00`)
- **Snapshot ID:** `sprint{N}_{YYYYMMDD}` format (e.g., `sprint15_20260115`)
- **Version tracking:** Three versions tracked:
  1. Schema version for progress_history.json evolution
  2. nlp2mcp version from `importlib.metadata.version("nlp2mcp")`
  3. Git commit hash from `git rev-parse HEAD` for exact reproducibility

**Implementation:**
```python
from datetime import datetime, timezone
from importlib.metadata import version
import subprocess

timestamp = datetime.now(timezone.utc).isoformat()
nlp2mcp_version = version("nlp2mcp")
git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
```

**Rationale:**
- ISO 8601 is sortable, unambiguous, internationally recognized
- Git commit hash enables exact reproducibility
- Snapshot ID is human-readable and unique per sprint-date

**Reference:** See `REPORT_DESIGN.md` "Progress Tracking Design" section.

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
✅ Status: VERIFIED (Task 3)

**Verified Date:** January 16, 2026

**Decision:** Two-level hierarchy (Stage → Error Category)

**Grouping Structure:**
1. **Level 1: Pipeline Stage** (Parse, Translate, Solve, Compare)
   - Provides immediate context for where issues occur
2. **Level 2: Error Category** (47-category taxonomy)
   - Full granularity preserved for actionability

**Grouping Rules:**
1. Show all categories (don't hide low-count errors)
2. Sort by count (highest-impact first)
3. Include both % of stage failures and % of total models
4. One representative error message per category
5. Include fix complexity and recommendation for each

**Example Output:**
```markdown
## Parse Failures (126 models, 78.8% of total)

### lexer_invalid_char (109 models, 86.5% of parse failures)
- Primary cause: Dollar control options ($ontext, $include)
- Fix complexity: Medium
- Recommendation: Implement lexer mode for region skipping
```

**Reference:** See `REPORT_DESIGN.md` "Failure Grouping Strategy" section.

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
✅ Status: VERIFIED (Task 4)

**Verified Date:** January 16, 2026

**Decision:** Yes, include ONE representative error message per category

**Rationale:**
1. Helps developers understand error context without running models
2. Single example per category prevents report bloat
3. Message truncated to 200 characters for readability
4. Source context included when available (up to 3 lines)
5. Line number included for quick navigation

**Format Designed:**
```yaml
example_error:
  model: "aircraft"
  message: "Unexpected character '$' at line 15..."
  context: "$ontext\nComment block\n$offtext"
  line: 15
```

**Reference:** See `FAILURE_REPORT_SCHEMA.md` "Error Message Examples" section.

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
✅ Status: VERIFIED (Task 4)

**Verified Date:** January 16, 2026

**Decision:** Semi-automated with pattern-to-recommendation mapping

**Approach:**
1. **Pattern Detection:** Regex patterns classify errors into subcategories
2. **Default Recommendations:** Each pattern has predefined recommendation
3. **Auto-Generation:** Recommendations generated from pattern rules
4. **Manual Override:** Metadata file allows expert annotation
5. **Flagged:** `auto_generated: true/false` indicates source

**Recommendation Format:**
```yaml
recommendation:
  action: "Implement lexer mode for region skipping"
  complexity: "medium"
  effort_hours: 8
  sprint_target: "Sprint 16"
  auto_generated: true
```

**Pattern-to-Recommendation Example:**
```python
'dollar_control': {
    'regex': r'\$(?:ontext|offtext|include|...)',
    'recommendation': 'Implement lexer mode for region skipping',
    'fix_complexity': 'medium',
}
```

**Reference:** See `FAILURE_REPORT_SCHEMA.md` "Improvement Recommendation System" section.

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
✅ Status: VERIFIED (Task 8)

**Verified Date:** January 19, 2026

**Decision:** JSON Schema (v1.0.0) with the following structure:

**Top-Level:**
- `schema_version`: Semantic version string for forward compatibility
- `snapshots`: Array of progress snapshots (newest first)

**Per-Snapshot:**
- `snapshot_id`: Unique identifier (`sprint{N}_{YYYYMMDD}` format)
- `timestamp`: ISO 8601 timestamp
- `nlp2mcp_version`: Version at time of snapshot
- `git_commit`: 40-character commit hash for reproducibility
- `sprint`: Integer sprint number
- `label`: Human-readable label (e.g., "Sprint 15 Baseline")
- `metrics`: Stage-by-stage success rates and error breakdowns
- `model_status`: Per-model outcomes for change tracking
- `notes`: Optional array of notes

**Metrics Structure:**
```json
{
  "total_models": 160,
  "parse": { "attempted": 160, "success": 34, "failure": 126, "rate": 0.213, "error_breakdown": {...} },
  "translate": { "attempted": 34, "success": 17, "failure": 17, "rate": 0.500, "error_breakdown": {...} },
  "solve": { "attempted": 17, "success": 3, "failure": 14, "rate": 0.176, "error_breakdown": {...} },
  "full_pipeline": { "success": 1, "rate": 0.0063 }
}
```

**Storage Estimate:**
- ~8KB per snapshot (160 models × ~50 bytes each)
- 50 snapshots = ~400KB (acceptable for JSON)

**Compatibility:** Designed to be compatible with existing `baseline_metrics.json`. Includes conversion utility `baseline_to_snapshot()`.

**Reference:** See `REPORT_DESIGN.md` "progress_history.json Schema" section for complete JSON Schema.

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
✅ Status: VERIFIED (Task 8)

**Verified Date:** January 19, 2026

**Decision:** Three-tier regression detection with configurable thresholds:

**Detection Criteria:**
1. **Rate regression:** Success rate decreases by more than threshold
2. **Model regression:** A previously passing model now fails
3. **Error increase:** An error category count increases significantly

**Threshold Configuration:**
```python
REGRESSION_THRESHOLDS = {
    "parse_rate": 0.02,           # 2% regression triggers alert
    "translate_rate": 0.02,
    "solve_rate": 0.02,
    "full_pipeline_rate": 0.01,   # More sensitive for full pipeline
    "max_model_regressions": 0,   # Any model regression is flagged
    "error_increase_threshold": 5  # Flag if error category increases by >5
}
```

**Rationale for Thresholds:**
- **2% rate threshold:** Balances sensitivity vs. noise; 3-4 model changes
- **0 model regressions:** Any previously passing model regressing is important
- **5 error increase:** Small variations expected; flag significant changes only

**Alert Mechanisms:**
1. **Console output:** Clear formatting with icons (⚠️, ✅, ➡️)
2. **CI integration:** Non-zero exit code via `--fail-on-regression` flag
3. **Detailed report:** Model-level change report for debugging

**CLI Support:**
```bash
python -m nlp2mcp.reporting.generate_report --compare --check-regressions
python -m nlp2mcp.reporting.generate_report --check-regressions --fail-on-regression
```

**Reference:** See `REPORT_DESIGN.md` "Regression Detection" section for detection algorithm.

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
✅ Status: PARTIALLY VERIFIED (Task 2)

**Verified Date:** January 16, 2026

**Finding:** Analysis of baseline_metrics.json confirms:
- 109 models fail with `lexer_invalid_char` (86.5% of parse failures)
- 17 models fail with `internal_error` (13.5% of parse failures)

**Key Insight:** The 86.5% concentration in a single error category suggests focused improvement on dollar control handling is the correct strategy.

**Subcategory Breakdown:** Not yet verified - requires detailed model file analysis in Task 6. Assumption of 80-90% dollar control-related remains reasonable but needs confirmation.

**Correction:** None - assumption validated by data.

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
✅ Status: VERIFIED (Tasks 2 + 7)

**Verified Date:** January 19, 2026

**Finding:** The original assumption was INCORRECT. Analysis reveals:
- **0 models** have parse-stage `path_syntax_error`
- **14 models** have SOLVE-stage `path_syntax_error` (100% of solve failures)

**Correction:** `path_syntax_error` is NOT caused by GAMS file path references ($include, $batinclude). It occurs at the SOLVE stage and indicates **GAMS compilation errors in generated MCP files** - not PATH solver issues.

**Task 7 Deep Analysis - Actual Error Patterns:**

| Error Code | Count | Description | Root Cause |
|------------|-------|-------------|------------|
| 445 | 46 | Operator sequence | Unary minus before parentheses |
| 924 | 24 | MCP separator | Wrong syntax in model statement |
| 171, 340 | 14 | Domain/quoting | Inconsistent set element quoting |
| 145, 148 | 8 | Index issues | Domain propagation bugs |

**Error Categories by Model Type:**

1. **Unary Minus Pattern (10 models):** `-(expr)` should be `(-1)*(expr)`
   - himmel11, house, least, mathopt1, mathopt2, mhw4d, mhw4dx, process, rbrock, sample

2. **Set Element Quoting (3 models):** Inconsistent quoting of set elements
   - chem, dispatch, port

3. **Scalar Declaration (1 model):** Missing identifier name
   - dispatch

**Fix Strategy:**
- Priority 1: Fix unary minus formatting (10 models, 2-4h)
- Priority 2: Consistent set element quoting (3 models, 4-6h)
- Priority 3: Scalar declaration fix (1 model, 1-2h)

**Expected Improvement:** 17.6% → 76-100% solve rate for translated models

**Reference:** See `PATH_ERROR_ANALYSIS.md` for complete analysis.

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
✅ Status: VERIFIED (Task 4)

**Verified Date:** January 16, 2026

**Decision:** Priority Score = Models Affected / Effort Hours (only for fixable errors)

**Formula Details:**
- `Models Affected`: Count of models blocked by this error
- `Fixability`: Boolean filter; non-fixable errors are excluded (scored as 0.0)
- `Effort Hours`: Estimated implementation time

**Example Priority Ranking:**

| Error | Models | Fixable | Effort | Score |
|-------|--------|---------|--------|-------|
| lexer_invalid_char (dollar) | 87 | Yes | 8h | 10.88 |
| special_chars | 10 | Yes | 2h | 5.00 |
| path_syntax_error | 14 | Yes | 6h | 2.33 |
| internal_error | 17 | Yes | 12h | 1.42 |
| embedded_code | 12 | No | N/A | 0.00 |

**Rationale:**
1. Simple, transparent formula
2. Prioritizes high-impact, low-effort fixes
3. Excludes unfixable issues automatically (score = 0)
4. Can be extended with model type weights if needed

**Implementation:**
```python
def calculate_priority_score(models, fixable, effort):
    if not fixable or effort <= 0:
        return 0.0
    return round(models / effort, 2)
```

**Reference:** See `FAILURE_REPORT_SCHEMA.md` "Prioritization Formula" section.

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
✅ Status: VERIFIED (Task 6)

**Verified Date:** January 18, 2026

**Critical Finding:** The original assumption was INCORRECT. Analysis of 153 lexer_invalid_char errors reveals:

**Dollar control is NOT the primary cause.** The grammar already handles `$ontext/$offtext` correctly via:
```lark
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments
%ignore /\$(?![\(\s])[a-z]+[^\n]*/i    // Other $ directives
```

**Actual Causes - Syntax We SHOULD Support:**

| Cause | Models | Should Support? | Reason |
|-------|--------|-----------------|--------|
| Hyphenated set elements | 91+ | **YES** | Core GAMS data syntax |
| Tuple expansion `(a,b).c` | 12 | **YES** | Standard GAMS feature |
| Numeric context in data | 11 | **YES** | Common parameter syntax |
| Keyword case (`Free Variable`) | 9 | **YES** | GAMS is case-insensitive |
| Quoted set descriptions | 7 | **YES** | Standard set declaration |

**Syntax to Intentionally Exclude:**

| Syntax | Reason |
|--------|--------|
| `%variable%` compile-time | Requires GAMS preprocessor execution |
| `$include` content | Cannot follow external files |
| `$call`, `$execute` | Runtime commands, not model definition |

**Correction to Assumption:** The vast majority of lexer errors (>90%) are from GAMS syntax we SHOULD support, not features to exclude. The fix strategy should focus on:
1. Extending `SET_ELEMENT_ID` to handle hyphenated elements with numbers
2. Adding tuple expansion syntax support
3. Improving keyword case handling

**Reference:** See `LEXER_ERROR_ANALYSIS.md` for complete subcategory breakdown and fix strategies.

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
✅ Status: VERIFIED (Task 2)

**Verified Date:** January 16, 2026

**Finding:** Analysis of baseline_metrics.json confirms translation failures distributed across 6 categories:

| Error Category | Count | Percentage |
|----------------|-------|------------|
| `model_no_objective_def` | 5 | 29.4% |
| `diff_unsupported_func` | 5 | 29.4% |
| `unsup_index_offset` | 3 | 17.6% |
| `model_domain_mismatch` | 2 | 11.8% |
| `unsup_dollar_cond` | 1 | 5.9% |
| `codegen_numerical_error` | 1 | 5.9% |

**Key Insight:** No single dominant failure category - improvements require multiple targeted fixes. The assumption about unsupported functions and missing objectives is correct.

**Correction:** None - assumption validated by data.

**Recommendation:** Defer translation improvements to Sprint 17 as planned; focus Sprint 16 on parser improvements.

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
✅ Status: VERIFIED (Task 9)

**Verified Date:** January 20, 2026

**Decision:** Translation improvements should be deferred to Sprint 17 with specific exceptions.

**Sprint 16 Scope (Quick Wins Only):**
- None identified. All translation fixes require significant effort or depend on parser improvements first.

**Sprint 17 Scope (Major Efforts):**

| Fix | Models | Effort | Rationale |
|-----|--------|--------|-----------|
| `model_no_objective_def` | 5 | High | Requires feasibility reformulation design |
| `diff_unsupported_func` | 5 | High | Requires new derivative rules (gamma, etc.) |
| `unsup_index_offset` | 3 | Medium | Requires domain arithmetic analysis |
| `model_domain_mismatch` | 2 | Medium | Requires improved domain propagation |
| `unsup_dollar_cond` | 1 | Medium | Requires conditional expression handling |
| `codegen_numerical_error` | 1 | Low | Edge case fix |

**Rationale for Deferral:**
1. **Cascade effect:** Parser improvements in Sprint 16 will change which models reach translation
2. **ROI:** Parse improvements unblock 109+ models vs. translation fixes affecting 17 models
3. **Dependencies:** Some translation issues may resolve with better parsing
4. **Sprint scope:** Sprint 16 already has reporting infrastructure + parse improvements

**Sprint 15 Learning:** Translation success rate (50%) is acceptable for Sprint 16. Focus effort on parse stage where failure rate is 78.8%.

**Reference:** See `SPRINT_15_REVIEW.md` Recommendation 5 for detailed rationale.

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
✅ Status: VERIFIED (Task 9)

**Verified Date:** January 20, 2026

**Finding:** YES - Translation failures correlate with model type and specific GAMS features.

**Correlation Analysis from Sprint 15 Baseline:**

| Model Type | Parse Attempts | Parse Success | Translate Attempts | Translate Success | Translate Rate |
|------------|----------------|---------------|---------------------|-------------------|----------------|
| NLP | 94 | 26 (27.7%) | 26 | 14 (53.8%) | Higher |
| LP | 57 | 5 (8.8%) | 5 | 2 (40.0%) | Lower |
| QCP | 9 | 3 (33.3%) | 3 | 1 (33.3%) | Lowest |

**Key Correlations Identified:**

1. **Model Type → Translation Success:**
   - NLP models translate better (53.8%) than LP (40.0%) or QCP (33.3%)
   - Likely because NLP models in GAMSLIB are simpler/more standardized

2. **Feature → Failure Category:**
   - Models using `card()`, `ord()` → `diff_unsupported_func`
   - Models with complex indexing → `unsup_index_offset`
   - Models without explicit minimize/maximize → `model_no_objective_def`

3. **Complexity → Translation:**
   - Models that parse successfully tend to be simpler
   - Simpler models also translate better (selection bias)

**Actionable Insight:** As Sprint 16 parser improvements enable more complex models to parse, expect translation success rate to DECREASE initially (more complex models entering translation stage).

**Sprint 16 Implication:** Monitor translation rate closely after parser improvements. A temporary drop is expected and acceptable.

**Reference:** See `baseline_metrics.json` for raw data and `SPRINT_15_REVIEW.md` Learning 7.

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
✅ Status: VERIFIED (Task 2)

**Verified Date:** January 16, 2026

**Finding:** Analysis of baseline_metrics.json reveals a striking pattern:
- **ALL 14 solve failures (100%)** are `path_syntax_error`
- No other solve failure categories exist

**Key Insight:** This single-cause pattern suggests a systematic issue in MCP generation rather than diverse model problems. Fixing the root cause could potentially unblock all 14 models simultaneously.

**Correction:** The assumption about "PATH solver issues" is partially correct, but the cause is likely MCP syntax generation errors in nlp2mcp, not inherent PATH solver limitations.

**Additional Finding:** Only 3 models solved successfully, with 1 (hs62) matching the reference solution and 2 having objective mismatches.

**Recommendation:** Task 7 should investigate the specific MCP syntax patterns causing PATH rejection.

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
✅ Status: VERIFIED (Task 7)

**Verified Date:** January 19, 2026

**Critical Finding:** ALL 14 solve failures (100%) are addressable nlp2mcp bugs, NOT inherent model difficulties or PATH solver limitations.

**Analysis Results:**

| Category | Count | Addressable? | Root Cause |
|----------|-------|--------------|------------|
| Code generation bugs | 14 | **YES** | MCP file syntax errors |
| PATH solver issues | 0 | N/A | None found |
| Model difficulties | 0 | N/A | None found |

**Breakdown of nlp2mcp Bugs:**

1. **Unary minus formatting (10 models):** `src/emit/emit_gams.py` emits `-(expr)` which GAMS rejects
2. **Set element quoting (3 models):** Inconsistent quoting in generated code
3. **Scalar declaration (1 model):** Missing identifier names

**Key Insight:** The assumption that "many solve failures are inherent model difficulties" was INCORRECT. All failures are due to bugs in nlp2mcp's MCP code generation that can be systematically fixed.

**Realistic Targets:**

| Metric | Current | After Fixes |
|--------|---------|-------------|
| Solve rate (of translated) | 17.6% (3/17) | 76-100% (13-17/17) |
| Full pipeline success | 0.6% (1/160) | Potentially 5-10% |

**Recommendation:** Prioritize fixing `emit_gams.py` in Sprint 16 - high impact, addressable bugs.

**Reference:** See `PATH_ERROR_ANALYSIS.md` for complete analysis including specific code changes needed.

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
✅ Status: VERIFIED (Task 9)

**Verified Date:** January 20, 2026

**Decision:** Use table-based format grouped by priority, with status tracking.

**Recommended Format:**

```markdown
# IMPROVEMENT_ROADMAP.md

## Sprint 16 Improvements

### HIGH Priority (Score > 5.0)

| ID | Issue | Models | Effort | Score | Target | Status |
|----|-------|--------|--------|-------|--------|--------|
| P-1 | Keyword case handling | 9 | 4h | 2.25 | Sprint 16 | Planned |
| P-2 | Hyphenated set elements | 6 | 4h | 1.50 | Sprint 16 | Planned |
| S-1 | Unary minus formatting | 10 | 4h | 2.50 | Sprint 16 | Planned |

### MEDIUM Priority (Score 2.0-5.0)

| ID | Issue | Models | Effort | Score | Target | Status |
|----|-------|--------|--------|-------|--------|--------|
| P-3 | Tuple expansion syntax | 12 | 12h | 1.00 | Sprint 16 | Planned |

### LOW Priority / Deferred

| ID | Issue | Models | Reason | Target |
|----|-------|--------|--------|--------|
| T-1 | Unsupported functions | 5 | High complexity | Sprint 17 |
```

**Field Definitions:**
- **ID:** Prefix indicates stage (P=Parse, T=Translate, S=Solve)
- **Issue:** Brief description of the problem
- **Models:** Count of models affected
- **Effort:** Estimated hours to implement
- **Score:** Priority score = Models / Effort
- **Target:** Target sprint for implementation
- **Status:** Planned → In Progress → Done

**Grouping Rationale:**
1. Group by priority (HIGH/MEDIUM/LOW) for quick scanning
2. Within priority, sort by score descending
3. Deferred items in separate section with reason

**Linking to Error Categories:**
- Each roadmap item links to error taxonomy category
- Example: "P-1: Keyword case handling" → `lexer_invalid_char` → `keyword_case` subcategory

**Progress Tracking:**
- Status field updated during sprint
- Completion marked with date in Notes column
- Metrics updated in progress_history.json after implementation

**Reference:** See Sprint 15 pattern in `SPRINT_BASELINE.md` "Recommendations" section.

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
✅ Status: VERIFIED (Task 9)

**Verified Date:** January 20, 2026

**Decision:** Use simplified formula: **Score = Models Affected / Effort Hours**

**Rationale for Simplicity:**
1. **Convex weight unnecessary:** All 160 target models are already verified_convex or likely_convex
2. **Linear scaling sufficient:** Non-linear formulas add complexity without clear benefit
3. **Subjective factors:** Include as tiebreakers, not in formula
4. **Uncertainty handling:** Use effort ranges (e.g., 4-8h) and take midpoint

**Priority Bands:**
- **HIGH (Score > 2.0):** Immediate Sprint 16 focus
- **MEDIUM (Score 1.0-2.0):** Sprint 16 if time permits
- **LOW (Score < 1.0):** Defer to Sprint 17

**Example Application (from Sprint 15 data):**

| Issue | Models | Effort | Score | Priority |
|-------|--------|--------|-------|----------|
| Keyword case | 9 | 4h | 2.25 | HIGH |
| Unary minus (emit) | 10 | 4h | 2.50 | HIGH |
| Hyphenated elements | 6 | 4h | 1.50 | MEDIUM |
| Tuple expansion | 12 | 12h | 1.00 | MEDIUM |
| Unsupported functions | 5 | 16h | 0.31 | LOW |

**Tiebreaker Factors (when scores are equal):**
1. **Risk:** Lower risk wins
2. **Dependencies:** Fewer dependencies wins
3. **Confidence:** Higher confidence effort estimate wins

**Sprint 15 Learning:** The assumption that convexity weighting matters was INCORRECT. Since we filter to convex models upfront, all models in scope have equal value.

**Reference:** See `FAILURE_REPORT_SCHEMA.md` for full prioritization framework and Task 4 verification results.

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
✅ Status: VERIFIED (Task 2)

**Verified Date:** January 16, 2026

**Finding:** Baseline analysis confirms Sprint 16 should target:

| Priority | Target | Models | Rationale |
|----------|--------|--------|-----------|
| **PRIMARY** | `lexer_invalid_char` (dollar control) | ~87 | 86.5% of parse failures, medium fix complexity |
| **SECONDARY** | `path_syntax_error` (solve stage) | 14 | 100% of solve failures, investigate in Task 7 |
| **DEFER** | `internal_error` | 17 | May resolve with dollar control fixes |
| **SKIP** | Translation failures | 17 | Defer to Sprint 17 as planned |

**Improvement Targets:**
- Minimum: +10% parse rate (from 21.3% to 31.3%, +16 models)
- Target: +20% parse rate (from 21.3% to 41.3%, +32 models)
- Stretch: +30% parse rate (from 21.3% to 51.3%, +48 models)

**Correction:** None - assumption about targeting dollar control is validated by data.

**Key Insight:** Focused effort on dollar control ($ontext/$offtext, $include) could yield 50-80 additional parsing models. This is the highest-ROI improvement for Sprint 16.

**Update from Task 6:** Analysis reveals dollar control is already handled. The actual targets should be:

| Priority | Target | Models | Effort | Days |
|----------|--------|--------|--------|------|
| 1 | Keyword case (`Free Variable`) | 9 | Low | 0.5 |
| 1 | Hyphenated elements (number-start) | 3 | Low | 0.5 |
| 1 | Abort statement syntax | 3 | Low | 0.5 |
| 1 | Numeric context in param data | 11 | Medium | 1 |
| 2 | Tuple expansion syntax | 12 | Medium | 1.5 |
| 2 | Quoted set descriptions | 7 | Medium | 1 |

**Revised Improvement Targets:**
- Minimum: +26 models (Priority 1), parse rate to 39%
- Target: +45 models (P1 + P2), parse rate to 47%
- Stretch: +55 models, parse rate to 52%

**Reference:** See `LEXER_ERROR_ANALYSIS.md` for detailed analysis.

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
✅ Status: VERIFIED (Task 5)

**Verified Date:** January 18, 2026

**Finding:** YES - Grammar extensions can be made safely without breaking existing parses.

**Key Evidence:**

1. **Parser Configuration:** The grammar uses Earley parser with `ambiguity="resolve"`, which gracefully handles ambiguous grammars by automatically selecting the simplest derivation.

2. **Extension Patterns Identified:**
   - **Pattern 1 (Lowest Risk):** Add new `%ignore` patterns for content skipping - lexer-level, doesn't affect parse rules
   - **Pattern 2 (Low Risk):** Add new statement types at end of `?stmt` alternatives - minimal precedence impact
   - **Pattern 3 (Medium Risk):** Extend existing rules with additional alternatives using same tree alias

3. **Current Grammar Structure:**
   - 604 lines, ~80 rules, ~50 terminals
   - Well-organized sections (blocks, declarations, expressions, tokens)
   - Already handles `$ontext/$offtext` via `%ignore /(?si)\$ontext.*?\$offtext/`

4. **Safety Mechanisms:**
   - Terminal priorities (`.N` suffix) control matching order
   - Tree aliases (`-> name`) normalize different syntaxes
   - Earley parser tolerates ambiguity without failing

**Recommendation:** Use `%ignore` pattern enhancement (lowest risk) for dollar control improvements. This approach:
- Operates at lexer level, before parsing
- Cannot break existing parse rules
- Easy to test and revert if needed

**Reference:** See `GRAMMAR_EXTENSION_GUIDE.md` for detailed patterns and testing checklist.

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
✅ Status: VERIFIED (Task 6)

**Verified Date:** January 18, 2026

**Critical Finding:** Dollar control is ALREADY HANDLED correctly in the grammar!

**Current Implementation (gams_grammar.lark):**
```lark
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments (case insensitive, dotall)
%ignore /\$(?![\(\s])[a-z]+[^\n]*/i    // Other $ directives (skip to EOL)
```

**Verification:** All 219 models in GAMSLIB contain `$ontext/$offtext` blocks. The grammar successfully skips them - errors occur AFTER the dollar control blocks, in regular GAMS syntax.

**Analysis of Actual Blockers:**

The 153 lexer errors are caused by GAMS data syntax, NOT dollar control:

| Root Cause | Models | Example |
|------------|--------|---------|
| Hyphenated set elements with numbers | 91+ | `/ 1964-i, route-1 /` |
| Tuple expansion syntax | 12 | `(a,b).c` |
| Numeric values in set context | 11 | `/ plant-1 9 /` |
| Keyword case variations | 9 | `Free Variable` |
| Quoted descriptions after hyphens | 7 | `/ cotton-h 'cotton' /` |

**Updated Approach for Sprint 16:**

Instead of enhancing dollar control handling, focus on:

1. **Extend SET_ELEMENT_ID pattern** to handle number-hyphen-letter sequences:
   ```lark
   // Current: /[a-zA-Z_][a-zA-Z0-9_+\-]*/
   // Enhanced: /[a-zA-Z0-9_][a-zA-Z0-9_+\-]*/  // Allow number start
   ```

2. **Add tuple expansion rule:**
   ```lark
   tuple_expansion: "(" id_list ")" ("." ID)?
   ```

3. **Add combined keywords:**
   ```lark
   free_var_decl: "Free"i "Variable"i var_list
   ```

**Correction to Assumption:** Dollar control is NOT the blocker. The assumption was fundamentally wrong. The correct approach targets GAMS data syntax extensions.

**Reference:** See `LEXER_ERROR_ANALYSIS.md` for complete analysis and `GRAMMAR_EXTENSION_GUIDE.md` for implementation patterns.

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
✅ Status: VERIFIED (Task 6)

**Verified Date:** January 18, 2026

**Finding:** Complete character analysis of 153 lexer errors. NO encoding issues found - all errors are from standard ASCII characters in valid GAMS syntax contexts.

**Character Distribution:**

| Character | Count | Primary Cause | Fix Strategy |
|-----------|-------|---------------|--------------|
| `'` (quote) | 25 | Inline descriptions in set data | Extend set_member rule |
| `,` (comma) | 20 | Abort syntax, tuple data | Fix abort_stmt, tuples |
| `1`-`9` (digits) | 25+ | Numeric values in set context | Improve num/id disambiguation |
| `(` (paren) | 14 | Tuple expansion `(a,b).c` | Add tuple_expansion rule |
| `/` (slash) | 7 | Data delimiters in unexpected context | Case-by-case |
| `*` (asterisk) | 6 | Operator/range in data context | Case-by-case |
| `V`, `F` (letters) | 10 | `Variable`, `Free` keyword case | Add combined keywords |
| `.` (dot) | 5 | Dot notation variations | Case-by-case |
| `-` (hyphen) | 4 | Hyphenated identifiers | Extend SET_ELEMENT_ID |

**Key Insights:**

1. **No encoding issues:** All characters are standard ASCII (0x00-0x7F)
2. **No extended ASCII/Unicode:** No special characters or foreign text
3. **Context matters:** The same character (`,`, `.`) fails in different contexts for different reasons

**Quick Wins Identified:**

| Fix | Characters | Models | Effort |
|-----|------------|--------|--------|
| Keyword case (`Free Variable`) | `V`, `F` | 9 | Low |
| Hyphenated number-start | `-`, digits | 6 | Low |
| Abort syntax | `,` | 3 | Low |

**Correction to Assumption:** The assumption about extended ASCII/Unicode was INCORRECT. All errors are from standard ASCII characters appearing in valid GAMS syntax that the grammar doesn't fully support. The issue is grammar coverage, not character encoding.

**Reference:** See `LEXER_ERROR_ANALYSIS.md` "Character Analysis" section for complete breakdown.

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
✅ Status: VERIFIED (Task 5)

**Verified Date:** January 18, 2026

**Finding:** The grammar ALREADY handles `$ontext/$offtext` via an `%ignore` directive. The issue is likely pattern edge cases.

**Current Implementation (gams_grammar.lark line ~597):**
```lark
%ignore /(?si)\$ontext.*?\$offtext/    // Block comments (case insensitive)
```

**Pattern Analysis:**
- `(?si)` - Case insensitive (`i`) and dotall mode (`s` - dot matches newlines)
- `\$ontext` - Literal dollar sign followed by "ontext"
- `.*?` - Non-greedy match of any characters (including newlines due to `s` flag)
- `\$offtext` - Literal dollar sign followed by "offtext"

**Why Models May Still Fail:**

1. **Whitespace before `$`:** Pattern requires `$` at exact position; leading whitespace not handled
2. **Line-start anchoring:** Some GAMS files may have `$ontext` not at line start
3. **Encoding issues:** Non-ASCII characters in skipped content may cause lexer errors
4. **Other dollar directives:** `$include`, `$call`, `$if` etc. handled by separate pattern that may miss variations

**Recommended Enhancement (Option A - Enhanced Pattern):**
```lark
// Handle whitespace before $ontext
%ignore /(?sim)^\s*\$ontext.*?\$offtext/
```

**Recommended Enhancement (Option B - Preprocessing):**
```python
def preprocess_gams(source: str) -> str:
    """Remove dollar control blocks before parsing."""
    import re
    # Remove $ontext...$offtext blocks (case insensitive, multiline)
    source = re.sub(r'(?si)\$ontext.*?\$offtext', '', source)
    return source
```

**Edge Cases to Test:**
1. `$ONTEXT` / `$OFFTEXT` (uppercase) - Should work with `(?i)` flag
2. `  $ontext` (indented) - May need `^\s*` prefix
3. Nested `$if` inside `$ontext` - Should be skipped entirely
4. Unclosed `$ontext` - Should fail gracefully (lexer error)

**Sprint 16 Recommendation:** Start with Option A (pattern enhancement). If insufficient, implement Option B (preprocessing) which provides full control.

**Reference:** See `GRAMMAR_EXTENSION_GUIDE.md` "Dollar Control Handling" section.

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
✅ Status: VERIFIED (Task 5)

**Verified Date:** January 18, 2026

**Finding:** Comprehensive testing strategy defined with 4-layer approach.

**Testing Strategy:**

**Layer 1: Unit Tests (Fast - Run on Every Change)**
```bash
pytest tests/parser/ tests/unit/gams/test_parser.py -v
```
- 19 parser feature test files in `tests/parser/`
- Core parser tests in `tests/unit/gams/test_parser.py`
- Performance tests in `tests/unit/gams/test_parser_performance.py`
- **Purpose:** Verify specific syntax features work correctly

**Layer 2: Regression Baseline (Medium - Run Before/After)**
```bash
# Before change
python scripts/gamslib/batch_parse.py --json > baseline.json

# After change  
python scripts/gamslib/batch_parse.py --json > after.json

# Compare - NO previously-passing models should fail
python -c "
import json
before = json.load(open('baseline.json'))
after = json.load(open('after.json'))
for model in before['models']:
    if before['models'][model]['parse_success'] and not after['models'][model]['parse_success']:
        print(f'REGRESSION: {model}')
"
```
- **Purpose:** Ensure no existing functionality breaks

**Layer 3: GAMSLIB Integration (Slow - Run Before Merge)**
```bash
python scripts/gamslib/batch_parse.py --verbose
```
- Full 160-model test on GAMSLIB corpus
- Records parse success/failure for each model
- **Purpose:** Measure real-world improvement

**Layer 4: IR Validation (Spot Check)**
```bash
# For newly-passing models, verify IR is reasonable
python -c "from src.ir.parser import parse_model_file; m = parse_model_file('model.gms'); print(m.sets, m.variables)"
```
- **Purpose:** Ensure parsing produces correct intermediate representation

**Regression Detection Protocol:**

| Check | Frequency | Failure Action |
|-------|-----------|----------------|
| Unit tests pass | Every commit | Block merge |
| No regressions in baseline | Before PR | Block merge |
| Parse rate improves | Before merge | Informational |
| IR spot-check | New models | Informational |

**Existing Test Coverage:**
- `tests/parser/` - 19 feature-specific test files
- `tests/unit/gams/test_parser.py` - Core parsing tests
- `tests/unit/gams/test_parser_performance.py` - Performance benchmarks

**CI Integration Recommendation:**
```yaml
# Add to CI pipeline
- name: Parser Regression Check
  run: |
    python scripts/gamslib/batch_parse.py --limit 34 --parse-success --json > baseline.json
    # (Make changes)
    python scripts/gamslib/batch_parse.py --limit 34 --parse-success --json > after.json
    python scripts/check_regression.py baseline.json after.json
```

**Reference:** See `GRAMMAR_EXTENSION_GUIDE.md` "Testing Checklist" section.

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
