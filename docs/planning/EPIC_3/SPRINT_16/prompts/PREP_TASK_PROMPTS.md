# Sprint 16 Prep Task Prompts

This document contains comprehensive prompts for executing each Sprint 16 preparation task. Each prompt includes the full task context, unknown verification requirements, and completion instructions.

---

## Table of Contents

1. [Task 2: Assess Current Baseline Metrics and Blockers](#task-2-assess-current-baseline-metrics-and-blockers)
2. [Task 3: Research Report Generation Approaches](#task-3-research-report-generation-approaches)
3. [Task 4: Design Failure Analysis Report Schema](#task-4-design-failure-analysis-report-schema)
4. [Task 5: Survey GAMS Grammar Extension Patterns](#task-5-survey-gams-grammar-extension-patterns)
5. [Task 6: Analyze Top Parse Blockers (lexer_invalid_char)](#task-6-analyze-top-parse-blockers-lexer_invalid_char)
6. [Task 7: Research PATH Syntax Error Patterns](#task-7-research-path-syntax-error-patterns)
7. [Task 8: Design Progress Tracking Schema](#task-8-design-progress-tracking-schema)
8. [Task 9: Review Sprint 15 Deliverables and Learnings](#task-9-review-sprint-15-deliverables-and-learnings)
9. [Task 10: Plan Sprint 16 Detailed Schedule](#task-10-plan-sprint-16-detailed-schedule)

---

# Task 2: Assess Current Baseline Metrics and Blockers

## Prompt

```
On branch `planning/sprint16-prep-task2`, complete Sprint 16 Prep Task 2: Assess Current Baseline Metrics and Blockers.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Unknowns to Verify:** 4.1, 4.2, 5.1, 6.1, 8.1

## Objective

Deep-dive into Sprint 15 baseline metrics to identify highest-impact improvement targets for Sprint 16.

## Why This Matters

Sprint 16 gap analysis and parser improvements must be prioritized by impact. Need to understand:
- Which parse errors block the most models?
- Which translate errors are parser-fixable vs fundamental?
- What is the "ceiling" for improvement without solver changes?

## What Needs to Be Done

### Step 1: Analyze Parse Failure Distribution
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome != "parse_success") | .parse_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- What percentage of parse failures are lexer vs parser errors?
- Are there clusters of similar failures?
- Which errors might be quick wins vs major grammar changes?

### Step 2: Analyze Translate Failure Distribution
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome != null and .translate_outcome != "translate_success") | .translate_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- Which translate errors correlate with specific model features?
- Are any translate errors fixable at parse stage?
- What is theoretical maximum translate success with perfect parsing?

### Step 3: Analyze Solve Failure Distribution
```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome != null and .solve_outcome != "solve_success") | .solve_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- Are solve failures due to MCP formulation or model characteristics?
- Which solve failures might be addressable in translation stage?

### Step 4: Create Impact Analysis Table

| Blocker | Count | % of Total | Fixable in Sprint 16? | Estimated Effort |
|---------|-------|------------|----------------------|------------------|
| lexer_invalid_char | 109 | 68.1% | Partially | High |
| path_syntax_error | 14 | 8.8% | Maybe | Medium |
| model_no_objective_def | 5 | 3.1% | No (model issue) | N/A |

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md` with:
   - Detailed breakdown of each error category
   - Impact ranking by model count
   - Fixability assessment
   - Recommended focus areas for Sprint 16

## Unknown Verification Requirements

After completing the analysis, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 4.1: What is the actual breakdown of lexer_invalid_char errors?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Add findings with specific counts for each subcategory
- Document evidence from error analysis

### Unknown 4.2: What GAMS syntax constructs cause path_syntax_error?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- List specific patterns found
- Document model examples

### Unknown 5.1: What is the actual breakdown of translation failures?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Add translation error counts by category
- Note correlation findings

### Unknown 6.1: What is the actual breakdown of solve failures?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document solve error distribution
- Note any patterns

### Unknown 8.1: Which parse blockers should be targeted in Sprint 16?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- List recommended targets with rationale
- Include effort estimates

## Update PREP_PLAN.md

1. Change Task 2 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary of work completed
4. Fill in "### Result" section with key findings
5. Check off all acceptance criteria:
   - [x] All error categories from taxonomy analyzed
   - [x] Count and percentage for each error type documented
   - [x] Fixability assessment for top 10 blockers
   - [x] Recommended Sprint 16 focus areas identified
   - [x] Document links to baseline_metrics.json and pipeline_results.json
   - [x] Unknowns 4.1, 4.2, 5.1, 6.1, 8.1 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 2: Assess Current Baseline Metrics and Blockers - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task2`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of work completed]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md` - [description]

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 4.1, 4.2, 5.1, 6.1, 8.1
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 2 marked complete

#### Key Findings
[List 3-5 key findings from analysis]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 2: Assess Current Baseline Metrics and Blockers

Create BASELINE_ANALYSIS.md with comprehensive error distribution analysis:
- Parse failures: [summary]
- Translate failures: [summary]
- Solve failures: [summary]

Key findings:
- [finding 1]
- [finding 2]
- [finding 3]

Verified unknowns: 4.1, 4.2, 5.1, 6.1, 8.1
Updated PREP_PLAN.md Task 2 status to COMPLETE"

git push
```

## Create Pull Request

After pushing, create a PR and wait for reviewer comments:

```bash
gh pr create --title "Sprint 16 Prep Task 2: Assess Current Baseline Metrics and Blockers" \
  --body "## Summary
Complete Sprint 16 Prep Task 2: Assess Current Baseline Metrics and Blockers

## Changes
- Created BASELINE_ANALYSIS.md with comprehensive error distribution
- Verified unknowns: 4.1, 4.2, 5.1, 6.1, 8.1
- Updated PREP_PLAN.md Task 2 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] BASELINE_ANALYSIS.md created with all required sections
- [ ] All 5 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 2 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 3: Research Report Generation Approaches

## Prompt

```
On branch `planning/sprint16-prep-task3`, complete Sprint 16 Prep Task 3: Research Report Generation Approaches.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3 hours  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns to Verify:** 1.1, 1.2, 1.3, 2.1

## Objective

Research approaches for automated report generation to inform Sprint 16 Priority 1 (Reporting Infrastructure) design.

## Why This Matters

Sprint 16 will create `generate_report.py` tool producing:
- GAMSLIB_STATUS.md - Overall status summary
- FAILURE_ANALYSIS.md - Detailed failure breakdown
- Progress tracking against historical baselines

Need to decide:
- Report format(s) - Markdown? JSON? HTML?
- Data sources - pipeline_results.json? Direct queries?
- Update frequency - On-demand? Automated CI?

## What Needs to Be Done

### Step 1: Survey Report Generation Libraries

Research Python libraries for report generation:

| Library | Pros | Cons | Best For |
|---------|------|------|----------|
| Jinja2 | Template-based, flexible | Requires templates | Markdown, HTML |
| tabulate | Simple tables | Limited formatting | Quick tables |
| Rich | Beautiful console output | Terminal-focused | Console reports |
| Markdown | Native Python | Basic features | Simple Markdown |

### Step 2: Analyze Existing Manual Reports

Review manually-created reports to understand patterns:
- `docs/testing/SPRINT_BASELINE.md` - Structure, metrics, tables
- `docs/testing/GAMSLIB_TESTING.md` - Model tracking, status tables

Extract common patterns:
- Summary statistics (counts, percentages)
- Model tables with status
- Error category breakdowns
- Comparison sections

### Step 3: Design Report Architecture

```
generate_report.py
├── data_loader.py        # Load pipeline_results.json
├── analyzers/
│   ├── status_analyzer.py    # Overall status metrics
│   ├── failure_analyzer.py   # Error breakdown analysis
│   └── progress_analyzer.py  # Historical comparison
├── renderers/
│   ├── markdown_renderer.py  # Render to Markdown
│   ├── json_renderer.py      # Render to JSON
│   └── html_renderer.py      # Render to HTML (optional)
└── templates/
    ├── status_report.md.j2
    └── failure_report.md.j2
```

### Step 4: Create Report Template Mockups

Design template structure for GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md.

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` with:
   - Library comparison and recommendation
   - Report architecture design
   - Template mockups for each report type
   - Implementation plan for Sprint 16

## Unknown Verification Requirements

After completing the research, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 1.1: What report output format(s) should generate_report.py support?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document recommended formats with rationale
- Include comparison of options considered

### Unknown 1.2: What metrics should be included in GAMSLIB_STATUS.md?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- List all metrics to include
- Document priority/ordering rationale

### Unknown 1.3: Should generate_report.py use a template system or string formatting?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document decision and rationale
- Include pros/cons analysis

### Unknown 2.1: What failure grouping granularity provides actionable insights?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document recommended grouping approach
- Include examples

## Update PREP_PLAN.md

1. Change Task 3 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with key decisions
5. Check off all acceptance criteria:
   - [x] At least 3 report generation approaches compared
   - [x] Recommended approach selected with rationale
   - [x] Architecture diagram/description created
   - [x] Template mockups for GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md
   - [x] Estimated implementation time for Sprint 16
   - [x] Unknowns 1.1, 1.2, 1.3, 2.1 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 3: Research Report Generation Approaches - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task3`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of research completed]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Report generation architecture and design

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 1.1, 1.2, 1.3, 2.1
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 3 marked complete

#### Key Decisions
- [Decision 1 with rationale]
- [Decision 2 with rationale]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 3: Research Report Generation Approaches

Create REPORT_DESIGN.md with:
- Library comparison (Jinja2, tabulate, Rich, etc.)
- Recommended approach: [approach]
- Report architecture design
- Template mockups for status and failure reports

Key decisions:
- [decision 1]
- [decision 2]

Verified unknowns: 1.1, 1.2, 1.3, 2.1
Updated PREP_PLAN.md Task 3 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 3: Research Report Generation Approaches" \
  --body "## Summary
Complete Sprint 16 Prep Task 3: Research Report Generation Approaches

## Changes
- Created REPORT_DESIGN.md with architecture and templates
- Verified unknowns: 1.1, 1.2, 1.3, 2.1
- Updated PREP_PLAN.md Task 3 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] REPORT_DESIGN.md created with all required sections
- [ ] All 4 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 3 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 4: Design Failure Analysis Report Schema

## Prompt

```
On branch `planning/sprint16-prep-task4`, complete Sprint 16 Prep Task 4: Design Failure Analysis Report Schema.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns to Verify:** 2.2, 2.3, 4.3

## Objective

Design the schema and content structure for FAILURE_ANALYSIS.md report that will guide parser improvement decisions.

## Why This Matters

Gap analysis in Sprint 16 depends on clear failure categorization and actionable insights. The failure analysis report must:
- Group failures by category and subcategory
- Identify patterns within error types
- Prioritize by fixability and impact
- Track improvement over time

## What Needs to Be Done

### Step 1: Design Failure Hierarchy Schema

```yaml
failure_analysis:
  parse_failures:
    lexer_errors:
      lexer_invalid_char:
        count: 109
        percentage: 68.1%
        subcategories:
          - pattern: "Dollar control"
            models: [model1, model2, ...]
            fixable: true
            effort: medium
```

### Step 2: Design Pattern Detection Rules

For lexer_invalid_char errors, define pattern detection:
```python
LEXER_ERROR_PATTERNS = {
    'dollar_control': r'\$[a-zA-Z]+',
    'embedded_code': r'\$call|\$execute',
    'special_chars': r'[^\x00-\x7F]',
    'macro_syntax': r'%[a-zA-Z]+%',
}
```

### Step 3: Design Improvement Roadmap Section

Create template for prioritizing improvements by impact/effort.

### Step 4: Design Comparison Section

Create template for tracking progress sprint-over-sprint.

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md` with:
   - Complete JSON/YAML schema for failure analysis data
   - Pattern detection rules for subcategorization
   - Report template structure
   - Comparison/progress tracking format

## Unknown Verification Requirements

After completing the design, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 2.2: Should FAILURE_ANALYSIS.md include example error messages?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document decision and rationale
- Include examples of how errors will be shown

### Unknown 2.3: How should improvement recommendations be generated?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document approach (auto-generated vs manual)
- Include recommendation template

### Unknown 4.3: How should parse failures be prioritized for improvement?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document prioritization formula/approach
- Include example priority ranking

## Update PREP_PLAN.md

1. Change Task 4 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with schema overview
5. Check off all acceptance criteria:
   - [x] Schema covers all error categories from taxonomy
   - [x] Subcategorization approach defined for top blockers
   - [x] Pattern detection rules documented
   - [x] Improvement roadmap template created
   - [x] Progress comparison format enables sprint-over-sprint tracking
   - [x] Unknowns 2.2, 2.3, 4.3 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 4: Design Failure Analysis Report Schema - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task4`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of schema design]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md` - Failure analysis schema and templates

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 2.2, 2.3, 4.3
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 4 marked complete

#### Schema Highlights
- [Highlight 1]
- [Highlight 2]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 4: Design Failure Analysis Report Schema

Create FAILURE_REPORT_SCHEMA.md with:
- Failure hierarchy schema (YAML/JSON)
- Pattern detection rules for error subcategorization
- Improvement roadmap template
- Progress tracking format

Verified unknowns: 2.2, 2.3, 4.3
Updated PREP_PLAN.md Task 4 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 4: Design Failure Analysis Report Schema" \
  --body "## Summary
Complete Sprint 16 Prep Task 4: Design Failure Analysis Report Schema

## Changes
- Created FAILURE_REPORT_SCHEMA.md with schema and templates
- Verified unknowns: 2.2, 2.3, 4.3
- Updated PREP_PLAN.md Task 4 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] FAILURE_REPORT_SCHEMA.md created with all required sections
- [ ] All 3 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 4 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 5: Survey GAMS Grammar Extension Patterns

## Prompt

```
On branch `planning/sprint16-prep-task5`, complete Sprint 16 Prep Task 5: Survey GAMS Grammar Extension Patterns.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Dependencies:** None  
**Unknowns to Verify:** 8.2, 9.1, 9.2

## Objective

Study existing GAMS grammar (`gams.lark`) to understand extension patterns and prepare for parser improvements.

## Why This Matters

Sprint 16 Priority 3 will modify the GAMS parser to handle more model syntax. Need to understand:
- Current grammar structure and patterns
- How to add new token types
- How to extend rules without breaking existing parsing
- Testing strategies for grammar changes

## What Needs to Be Done

### Step 1: Analyze Current Grammar Structure

```bash
wc -l src/nlp2mcp/parser/gams.lark
head -100 src/nlp2mcp/parser/gams.lark
```

Document:
- Total rule count
- Major section breakdown (statements, expressions, terminals)
- Token definition patterns
- Import/include patterns

### Step 2: Identify Grammar Extension Points

Find where new syntax can be added:
- Terminal definitions for new token types
- Rule alternatives for syntax variations
- Precedence handling for operators

### Step 3: Study Lark Extension Best Practices

Research Lark documentation for:
- Adding lexer modes (for embedded content)
- Handling ambiguous grammar
- Error recovery options
- Testing grammar changes

### Step 4: Create Grammar Extension Checklist

Create checklist for safely modifying the grammar.

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` with:
   - Current grammar analysis
   - Extension patterns and examples
   - Best practices from Lark documentation
   - Testing checklist for grammar changes

## Unknown Verification Requirements

After completing the survey, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 8.2: Can grammar extensions be made without breaking existing parses?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document findings on safe extension patterns
- Include specific examples and risks

### Unknown 9.1: What is the correct grammar change for dollar control comment blocks?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document recommended approach (regex pattern, lexer mode, etc.)
- Include example implementation

### Unknown 9.2: What testing strategy ensures parser changes don't regress?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document testing strategy
- Include checklist items

## Update PREP_PLAN.md

1. Change Task 5 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with key patterns identified
5. Check off all acceptance criteria:
   - [x] Grammar structure documented (rules, terminals, sections)
   - [x] At least 3 extension patterns with examples
   - [x] Lark-specific considerations documented
   - [x] Testing checklist comprehensive
   - [x] Potential risks/pitfalls identified
   - [x] Unknowns 8.2, 9.1, 9.2 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 5: Survey GAMS Grammar Extension Patterns - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task5`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of grammar survey]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` - Grammar extension patterns and guide

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 8.2, 9.1, 9.2
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 5 marked complete

#### Key Patterns
- [Pattern 1]
- [Pattern 2]
- [Pattern 3]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 5: Survey GAMS Grammar Extension Patterns

Create GRAMMAR_EXTENSION_GUIDE.md with:
- Current grammar analysis ([X] rules, [Y] terminals)
- Extension patterns: [list patterns]
- Lark best practices for lexer modes, ambiguity handling
- Testing checklist for grammar changes

Verified unknowns: 8.2, 9.1, 9.2
Updated PREP_PLAN.md Task 5 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 5: Survey GAMS Grammar Extension Patterns" \
  --body "## Summary
Complete Sprint 16 Prep Task 5: Survey GAMS Grammar Extension Patterns

## Changes
- Created GRAMMAR_EXTENSION_GUIDE.md with patterns and checklist
- Verified unknowns: 8.2, 9.1, 9.2
- Updated PREP_PLAN.md Task 5 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] GRAMMAR_EXTENSION_GUIDE.md created with all required sections
- [ ] All 3 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 5 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 6: Analyze Top Parse Blockers (lexer_invalid_char)

## Prompt

```
On branch `planning/sprint16-prep-task6`, complete Sprint 16 Prep Task 6: Analyze Top Parse Blockers (lexer_invalid_char).

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Dependencies:** Task 5 (Grammar Extension Patterns)  
**Unknowns to Verify:** 4.4, 8.1, 8.3, 8.4

## Objective

Deep analysis of lexer_invalid_char errors to identify specific causes and develop fix strategies.

## Why This Matters

lexer_invalid_char accounts for 109/160 models (68.1%) - by far the largest blocker. Understanding what characters/patterns cause these errors is essential for Sprint 16 parser improvements.

## What Needs to Be Done

### Step 1: Sample Failing Models

```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -20
```

### Step 2: Examine Error Messages

```bash
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -10); do
    echo "=== $model ==="
    cat tests/output/pipeline_results.json | jq -r ".models[] | select(.model_name == \"$model\") | .parse_error"
done
```

Look for patterns:
- Line numbers where errors occur
- Specific characters mentioned
- Common prefixes/patterns

### Step 3: Categorize by Root Cause

Create subcategories:
- dollar_control ($ontext, $offtext, etc.)
- embedded_execute ($call, $execute blocks)
- special_chars (Non-ASCII, control chars)
- unknown (Needs investigation)

### Step 4: Develop Fix Strategies

For each subcategory, document:
- Strategy (lexer mode, skip rule, expand character class)
- Effort (Low/Medium/High)
- Risk level

### Step 5: Prioritize for Sprint 16

Create priority table with models, fixability, effort, and Sprint 16 targets.

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` with:
   - Complete subcategorization of lexer_invalid_char
   - Model counts for each subcategory
   - Fix strategy for each subcategory
   - Sprint 16 implementation plan

## Unknown Verification Requirements

After completing the analysis, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 4.4: Are lexer_invalid_char errors from syntax we should support or intentionally exclude?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document which features to support vs exclude
- Include rationale for each decision

### Unknown 8.1: Which parse blockers should be targeted in Sprint 16?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED (if not already from Task 2)
- Refine targets based on deep analysis
- Include specific implementation recommendations

### Unknown 8.3: What is the correct approach to handle dollar control options?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document recommended approach
- Include example implementation

### Unknown 8.4: What specific characters cause lexer_invalid_char beyond dollar control?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- List all character types found
- Include fix strategy for each

## Update PREP_PLAN.md

1. Change Task 6 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with analysis summary
4. Fill in "### Result" section with subcategory breakdown
5. Check off all acceptance criteria:
   - [x] At least 80% of lexer_invalid_char errors categorized
   - [x] Top 3 subcategories have detailed fix strategies
   - [x] Effort estimates provided for each strategy
   - [x] Clear Sprint 16 targets based on impact/effort
   - [x] Example fixes documented for implementation
   - [x] Unknowns 4.4, 8.1, 8.3, 8.4 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 6: Analyze Top Parse Blockers (lexer_invalid_char) - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task6`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of lexer error analysis]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` - Lexer error subcategorization and fix strategies

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 4.4, 8.1, 8.3, 8.4
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 6 marked complete

#### Subcategories Found
| Subcategory | Count | % of lexer_invalid_char |
|-------------|-------|------------------------|
| [subcategory 1] | [count] | [%] |
| [subcategory 2] | [count] | [%] |

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 6: Analyze Top Parse Blockers (lexer_invalid_char)

Create LEXER_ERROR_ANALYSIS.md with:
- Subcategorization of 109 lexer_invalid_char errors
- [X]% categorized into [N] subcategories
- Fix strategies for each subcategory
- Sprint 16 implementation plan targeting [X] models

Subcategories:
- [subcategory 1]: [count] models
- [subcategory 2]: [count] models

Verified unknowns: 4.4, 8.1, 8.3, 8.4
Updated PREP_PLAN.md Task 6 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 6: Analyze Top Parse Blockers (lexer_invalid_char)" \
  --body "## Summary
Complete Sprint 16 Prep Task 6: Analyze Top Parse Blockers (lexer_invalid_char)

## Changes
- Created LEXER_ERROR_ANALYSIS.md with subcategorization and strategies
- Verified unknowns: 4.4, 8.1, 8.3, 8.4
- Updated PREP_PLAN.md Task 6 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] LEXER_ERROR_ANALYSIS.md created with all required sections
- [ ] All 4 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 6 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 7: Research PATH Syntax Error Patterns

## Prompt

```
On branch `planning/sprint16-prep-task7`, complete Sprint 16 Prep Task 7: Research PATH Syntax Error Patterns.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns to Verify:** 4.2, 6.2

## Objective

Analyze path_syntax_error failures to understand patterns and develop fix strategies.

## Why This Matters

path_syntax_error affects 14 models (8.8% of total). While smaller than lexer_invalid_char, these may be quicker wins if patterns are consistent.

## What Needs to Be Done

### Step 1: Identify Affected Models

```bash
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "path_syntax_error") | .model_name'
```

### Step 2: Examine Error Details

```bash
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome == "path_syntax_error") | {model: .model_name, error: .parse_error}'
```

### Step 3: Categorize Patterns

Look for:
- Include statements with paths
- Relative vs absolute paths
- Platform-specific path separators
- External file references

### Step 4: Develop Fix Strategies

Potential fixes:
- Normalize path syntax in preprocessing
- Handle include statements specially
- Ignore/skip external file references

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` with:
   - List of affected models
   - Pattern categorization
   - Fix strategies
   - Sprint 16 recommendations

## Unknown Verification Requirements

After completing the research, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 4.2: What GAMS syntax constructs cause path_syntax_error?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED (if not already from Task 2)
- Document all patterns found
- Include model examples for each pattern

### Unknown 6.2: Are solve failures addressable in nlp2mcp or inherent model difficulties?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document findings on path-related solve issues
- Note any correlation between path errors and solve failures

## Update PREP_PLAN.md

1. Change Task 7 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with patterns found
5. Check off all acceptance criteria:
   - [x] All path_syntax_error models analyzed
   - [x] At least 2 distinct patterns identified
   - [x] Fix strategy for each pattern
   - [x] Clear recommendation for Sprint 16 scope
   - [x] Unknowns 4.2, 6.2 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 7: Research PATH Syntax Error Patterns - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task7`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of path error research]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` - Path syntax error analysis

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 4.2, 6.2
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 7 marked complete

#### Patterns Found
- [Pattern 1]: [count] models
- [Pattern 2]: [count] models

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 7: Research PATH Syntax Error Patterns

Create PATH_ERROR_ANALYSIS.md with:
- Analysis of 14 path_syntax_error models
- Pattern categorization: [list patterns]
- Fix strategies for each pattern
- Sprint 16 recommendations

Verified unknowns: 4.2, 6.2
Updated PREP_PLAN.md Task 7 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 7: Research PATH Syntax Error Patterns" \
  --body "## Summary
Complete Sprint 16 Prep Task 7: Research PATH Syntax Error Patterns

## Changes
- Created PATH_ERROR_ANALYSIS.md with pattern analysis
- Verified unknowns: 4.2, 6.2
- Updated PREP_PLAN.md Task 7 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] PATH_ERROR_ANALYSIS.md created with all required sections
- [ ] All 2 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 7 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 8: Design Progress Tracking Schema

## Prompt

```
On branch `planning/sprint16-prep-task8`, complete Sprint 16 Prep Task 8: Design Progress Tracking Schema.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Dependencies:** Task 3 (Report Generation Research)  
**Unknowns to Verify:** 1.4, 3.1, 3.2

## Objective

Design schema for tracking pipeline progress over time, enabling sprint-over-sprint comparison.

## Why This Matters

Sprint 16 introduces targeted improvements. Need to measure:
- Improvement from baseline
- Which fixes had most impact
- Trend over multiple sprints

## What Needs to Be Done

### Step 1: Design Progress Database Schema

```json
{
  "progress_history": [
    {
      "sprint": 15,
      "date": "2025-01-15",
      "metrics": {
        "parse": {"success": 34, "total": 160, "rate": 0.213},
        "translate": {"success": 17, "total": 34, "rate": 0.500},
        "solve": {"success": 3, "total": 17, "rate": 0.176}
      },
      "changes": "Initial baseline"
    }
  ]
}
```

### Step 2: Design Comparison Report Format

Create markdown template for sprint-over-sprint comparison.

### Step 3: Design Model-Level Tracking

Track individual model progress across sprints.

## Deliverables

1. Update `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` with:
   - Progress tracking schema
   - Comparison report format
   - Model-level tracking design

## Unknown Verification Requirements

After completing the design, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 1.4: How should report timestamps and versioning be handled?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document timestamp format decision
- Include version tracking approach

### Unknown 3.1: What schema should progress_history.json follow?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document complete schema
- Include example entries

### Unknown 3.2: How to detect and alert on regressions?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document regression detection approach
- Include threshold decisions

## Update PREP_PLAN.md

1. Change Task 8 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with schema overview
5. Check off all acceptance criteria:
   - [x] Schema supports multi-sprint history
   - [x] Comparison metrics clearly defined
   - [x] Model-level tracking enables debugging
   - [x] Schema compatible with existing baseline_metrics.json
   - [x] Unknowns 1.4, 3.1, 3.2 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 8: Design Progress Tracking Schema - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task8`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of progress tracking design]

#### Changes
**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Added progress tracking schema
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 1.4, 3.1, 3.2
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 8 marked complete

#### Schema Features
- [Feature 1]
- [Feature 2]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 8: Design Progress Tracking Schema

Update REPORT_DESIGN.md with:
- progress_history.json schema
- Sprint comparison report format
- Model-level tracking design
- Regression detection approach

Verified unknowns: 1.4, 3.1, 3.2
Updated PREP_PLAN.md Task 8 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 8: Design Progress Tracking Schema" \
  --body "## Summary
Complete Sprint 16 Prep Task 8: Design Progress Tracking Schema

## Changes
- Updated REPORT_DESIGN.md with progress tracking schema
- Verified unknowns: 1.4, 3.1, 3.2
- Updated PREP_PLAN.md Task 8 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] REPORT_DESIGN.md updated with progress tracking sections
- [ ] All 3 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 8 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 9: Review Sprint 15 Deliverables and Learnings

## Prompt

```
On branch `planning/sprint16-prep-task9`, complete Sprint 16 Prep Task 9: Review Sprint 15 Deliverables and Learnings.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Dependencies:** None  
**Unknowns to Verify:** 5.2, 5.3, 7.1, 7.2

## Objective

Consolidate learnings from Sprint 15 to inform Sprint 16 approach.

## Why This Matters

Sprint 15 was extensive (10 days). Key deliverables and learnings should be captured to:
- Avoid repeating mistakes
- Build on successful patterns
- Ensure continuity

## What Needs to Be Done

### Step 1: Review Sprint 15 Documentation

- docs/testing/SPRINT_BASELINE.md
- docs/guides/GAMSLIB_TESTING.md
- Error taxonomy in run_full_test.py
- README.md Sprint 15 section

### Step 2: Identify Key Learnings

Document:
- What worked well
- What was challenging
- What would do differently

### Step 3: Extract Actionable Items

Identify items for Sprint 16:
- Technical debt to address
- Patterns to replicate
- Approaches to avoid

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_15_REVIEW.md` with:
   - Deliverables summary
   - Key learnings
   - Recommendations for Sprint 16

## Unknown Verification Requirements

After completing the review, update `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:

### Unknown 5.2: Are translation failures fixable in Sprint 16 or beyond?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document which translation issues are Sprint 16 scope
- Note deferred items for Sprint 17

### Unknown 5.3: Do translation failures correlate with model characteristics?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document any correlations found in Sprint 15 data
- Note patterns for Sprint 16 focus

### Unknown 7.1: What format should IMPROVEMENT_ROADMAP.md follow?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document recommended format
- Reference Sprint 15 patterns

### Unknown 7.2: How should improvement priorities be determined?
- Update status from 🔍 INCOMPLETE to ✅ VERIFIED
- Document prioritization approach
- Include lessons from Sprint 15

## Update PREP_PLAN.md

1. Change Task 9 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with key learnings
5. Check off all acceptance criteria:
   - [x] All major Sprint 15 deliverables listed
   - [x] At least 5 key learnings documented
   - [x] At least 3 actionable recommendations for Sprint 16
   - [x] Technical debt items identified if any
   - [x] Unknowns 5.2, 5.3, 7.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 9: Review Sprint 15 Deliverables and Learnings - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task9`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of Sprint 15 review]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_15_REVIEW.md` - Sprint 15 learnings and recommendations

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Verified unknowns 5.2, 5.3, 7.1, 7.2
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 9 marked complete

#### Key Learnings
- [Learning 1]
- [Learning 2]
- [Learning 3]

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 9: Review Sprint 15 Deliverables and Learnings

Create SPRINT_15_REVIEW.md with:
- Sprint 15 deliverables summary
- Key learnings: [list 5+ learnings]
- Recommendations for Sprint 16: [list recommendations]
- Technical debt identified: [list if any]

Verified unknowns: 5.2, 5.3, 7.1, 7.2
Updated PREP_PLAN.md Task 9 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 9: Review Sprint 15 Deliverables and Learnings" \
  --body "## Summary
Complete Sprint 16 Prep Task 9: Review Sprint 15 Deliverables and Learnings

## Changes
- Created SPRINT_15_REVIEW.md with learnings and recommendations
- Verified unknowns: 5.2, 5.3, 7.1, 7.2
- Updated PREP_PLAN.md Task 9 status to COMPLETE
- Updated CHANGELOG.md

## Checklist
- [ ] SPRINT_15_REVIEW.md created with all required sections
- [ ] All 4 unknowns verified in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 9 acceptance criteria checked
- [ ] CHANGELOG.md updated"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

# Task 10: Plan Sprint 16 Detailed Schedule

## Prompt

```
On branch `planning/sprint16-prep-task10`, complete Sprint 16 Prep Task 10: Plan Sprint 16 Detailed Schedule.

## Task Overview

**Status:** Not Started → ✅ COMPLETE  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Dependencies:** All previous tasks (Tasks 1-9)  
**Unknowns to Verify:** All unknowns (integration review)

## Objective

Create detailed day-by-day schedule for Sprint 16 based on prep task findings.

## Why This Matters

Sprint 16 has 26-34 hours of estimated work across four priorities. Need clear schedule to:
- Ensure all work fits in sprint timeframe
- Sequence work correctly (dependencies)
- Identify potential bottlenecks

## What Needs to Be Done

### Step 1: Synthesize Prep Task Findings

Review deliverables from Tasks 1-9:
- Task 1: Known unknowns (KNOWN_UNKNOWNS.md)
- Task 2: Baseline analysis (BASELINE_ANALYSIS.md)
- Task 3: Report design (REPORT_DESIGN.md)
- Task 4: Failure schema (FAILURE_REPORT_SCHEMA.md)
- Task 5: Grammar guide (GRAMMAR_EXTENSION_GUIDE.md)
- Task 6: Lexer analysis (LEXER_ERROR_ANALYSIS.md)
- Task 7: Path analysis (PATH_ERROR_ANALYSIS.md)
- Task 8: Progress tracking (in REPORT_DESIGN.md)
- Task 9: Sprint 15 review (SPRINT_15_REVIEW.md)

### Step 2: Create Day-by-Day Schedule

```markdown
## Sprint 16 Schedule

### Days 1-2: Reporting Infrastructure
- Day 1: Implement generate_report.py framework, status analyzer
- Day 2: Implement failure analyzer, template rendering

### Days 3-4: Gap Analysis
- Day 3: Parse failure deep-dive, pattern documentation
- Day 4: Translate/solve analysis, improvement roadmap

### Days 5-8: Parser Improvements
- Day 5: Implement dollar control handling
- Day 6: Implement special character fixes
- Day 7: Implement path syntax fixes
- Day 8: Integration testing, edge cases

### Days 9-10: Retest and Documentation
- Day 9: Full pipeline retest, measure improvements
- Day 10: Update documentation, Sprint 16 retrospective
```

### Step 3: Identify Dependencies and Critical Path

Document task dependencies and critical path.

### Step 4: Define Success Criteria

Sprint 16 success metrics:
- Parse success rate: Target 35%+ (from 21.3%)
- Translate success rate: Maintain 50%+
- Full pipeline: Target 5%+ (from 0.6%)
- Reports: GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md generated

## Deliverables

1. Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md` with:
   - Day-by-day schedule
   - Dependency diagram
   - Success criteria
   - Risk mitigation plan

## Unknown Verification Requirements

Review ALL unknowns in `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`:
- Verify all Critical and High unknowns have been verified
- Update any remaining unknowns with final status
- Flag any unresolved Critical unknowns as sprint risks

## Update PREP_PLAN.md

1. Change Task 10 status: `**Status:** Not Started` → `**Status:** ✅ COMPLETE`
2. Add `**Time Spent:** X hours` after Status
3. Add "### What Was Done" section with summary
4. Fill in "### Result" section with schedule overview
5. Check off all acceptance criteria:
   - [x] Day-by-day schedule complete
   - [x] All Sprint 16 priorities scheduled
   - [x] Dependencies clearly marked
   - [x] Success criteria quantified
   - [x] Ready for Sprint 16 Day 1
   - [x] All unknowns reviewed and final status updated in KNOWN_UNKNOWNS.md

## Update CHANGELOG.md

Add entry under `## [Unreleased]`:

```markdown
### Sprint 16 Prep Task 10: Plan Sprint 16 Detailed Schedule - YYYY-MM-DD

**Branch:** `planning/sprint16-prep-task10`  
**Status:** ✅ COMPLETE

#### Summary
[Brief description of schedule planning]

#### Changes
**New Files:**
- `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md` - Sprint 16 day-by-day schedule

**Modified Files:**
- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` - Final status review for all unknowns
- `docs/planning/EPIC_3/SPRINT_16/PREP_PLAN.md` - Task 10 marked complete, prep phase complete

#### Sprint 16 Overview
- **Duration:** [X] days
- **Parse Target:** 35%+ (from 21.3%)
- **Full Pipeline Target:** 5%+ (from 0.6%)
- **Key Deliverables:** [list]

---
```

Also add a summary entry for Sprint 16 Prep completion:

```markdown
### Sprint 16 Prep Phase Complete - YYYY-MM-DD

**Status:** ✅ ALL 10 TASKS COMPLETE

**Prep Deliverables:**
- KNOWN_UNKNOWNS.md (27 unknowns, [X] verified)
- BASELINE_ANALYSIS.md
- REPORT_DESIGN.md
- FAILURE_REPORT_SCHEMA.md
- GRAMMAR_EXTENSION_GUIDE.md
- LEXER_ERROR_ANALYSIS.md
- PATH_ERROR_ANALYSIS.md
- SPRINT_15_REVIEW.md
- SPRINT_SCHEDULE.md

**Ready for Sprint 16 Day 1**

---
```

## Quality Gate

If any Python code is created or modified:
```bash
make typecheck && make lint && make format && make test
```

## Commit and Push

```bash
git add -A
git commit -m "Complete Sprint 16 Prep Task 10: Plan Sprint 16 Detailed Schedule

Create SPRINT_SCHEDULE.md with:
- Day-by-day schedule for Sprint 16
- Dependency diagram
- Success criteria (Parse 35%+, Pipeline 5%+)
- Risk mitigation plan

Sprint 16 Prep Phase Complete:
- All 10 tasks complete
- [X] unknowns verified
- Ready for Sprint 16 Day 1

Updated PREP_PLAN.md Task 10 status to COMPLETE"

git push
```

## Create Pull Request

```bash
gh pr create --title "Sprint 16 Prep Task 10: Plan Sprint 16 Detailed Schedule [PREP COMPLETE]" \
  --body "## Summary
Complete Sprint 16 Prep Task 10: Plan Sprint 16 Detailed Schedule

This completes the Sprint 16 Prep Phase. All 10 tasks are now complete.

## Changes
- Created SPRINT_SCHEDULE.md with day-by-day plan
- Final review of all unknowns in KNOWN_UNKNOWNS.md
- Updated PREP_PLAN.md Task 10 status to COMPLETE
- Updated CHANGELOG.md with prep phase completion

## Sprint 16 Prep Summary
- **Tasks Completed:** 10/10
- **Unknowns Verified:** [X]/27
- **Deliverables Created:** 9 documents
- **Ready for:** Sprint 16 Day 1

## Checklist
- [ ] SPRINT_SCHEDULE.md created with all required sections
- [ ] All unknowns reviewed and status updated in KNOWN_UNKNOWNS.md
- [ ] PREP_PLAN.md Task 10 acceptance criteria checked
- [ ] CHANGELOG.md updated with task and prep completion entries"
```

Then fetch and address any reviewer comments:
```bash
gh pr view --comments
```
```

---

## Usage Notes

### Executing Tasks in Order

Tasks should generally be executed in order, respecting dependencies:
- Task 1 ✅ (already complete)
- Tasks 2, 5, 9 can run in parallel (no dependencies on each other)
- Task 3 depends on Task 2
- Task 4 depends on Task 2
- Task 6 depends on Task 5
- Task 7 depends on Task 2
- Task 8 depends on Task 3
- Task 10 depends on ALL other tasks

### Suggested Execution Order

1. **Parallel Group 1:** Tasks 2, 5, 9 (can run simultaneously)
2. **Parallel Group 2:** Tasks 3, 4, 6, 7 (after their dependencies complete)
3. **Sequential:** Task 8 (after Task 3)
4. **Final:** Task 10 (after all others)

### Quality Reminders

- Always run quality checks before committing Python code
- Always update KNOWN_UNKNOWNS.md with verification results
- Always update PREP_PLAN.md with task completion status
- Always update CHANGELOG.md with task summary
- Always create PR and wait for reviewer feedback
