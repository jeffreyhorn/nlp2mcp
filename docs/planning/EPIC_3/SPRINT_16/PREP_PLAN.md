# Sprint 16 Preparation Plan

**Purpose:** Complete critical preparation tasks before Sprint 16 Reporting, Gap Analysis & Targeted Parser Improvements  
**Timeline:** Complete before Sprint 16 Day 1  
**Goal:** Establish reporting infrastructure, analyze pipeline gaps, and prepare parser improvement strategy

**Key Insight from Sprint 15:** Comprehensive baseline established with 47-category error taxonomy. Parse success at 21.3%, translate at 50%, solve at 17.6%, full pipeline at 0.6%. Primary blockers identified: lexer_invalid_char (109 models), path_syntax_error (14 models), model_no_objective_def (5 models).

---

## Executive Summary

Sprint 15 established comprehensive baseline metrics and error taxonomy for the GAMSLIB pipeline. Sprint 16 builds on this foundation with three priorities:

1. **Priority 1 (Reporting Infrastructure):** Build automated reporting tools to generate status summaries, failure analysis reports, and progress tracking - enabling ongoing visibility into pipeline health.

2. **Priority 2 (Gap Analysis):** Systematically analyze failures at each pipeline stage (parse, translate, solve) to identify root causes and prioritize improvements with maximum impact.

3. **Priority 3 (Targeted Parser Improvements):** Implement fixes for top 3-5 parse blockers identified in gap analysis, with retest to validate improvements.

This prep plan focuses on research, design, and setup tasks that must be completed before Sprint 16 Day 1 to prevent blocking issues and ensure efficient sprint execution.

---

## Prep Task Overview

| # | Task | Priority | Est. Time | Dependencies | Sprint 15 Foundation |
|---|------|----------|-----------|--------------|----------------------|
| 1 | Create Sprint 16 Known Unknowns List | Critical | 2-3h | None | Proactive unknown identification |
| 2 | Assess Current Baseline Metrics and Blockers | Critical | 2h | Task 1 | baseline_metrics.json, error taxonomy |
| 3 | Research Report Generation Approaches | High | 3h | Task 2 | Pipeline infrastructure exists |
| 4 | Design Failure Analysis Report Schema | High | 2-3h | Task 2 | 47-category taxonomy exists |
| 5 | Survey GAMS Grammar Extension Patterns | High | 3-4h | None | Parser infrastructure in place |
| 6 | Analyze Top Parse Blockers (lexer_invalid_char) | Critical | 3-4h | Task 5 | 109 models blocked |
| 7 | Research PATH Syntax Error Patterns | High | 2-3h | Task 2 | 14 models with path_syntax_error |
| 8 | Design Progress Tracking Schema | Medium | 2h | Task 3 | Need historical comparison |
| 9 | Review Sprint 15 Deliverables and Learnings | Medium | 1-2h | None | Consolidate sprint knowledge |
| 10 | Plan Sprint 16 Detailed Schedule | Critical | 2-3h | All tasks | Sprint planning |

**Total Estimated Time:** ~24-32 hours (~3-4 working days)

**Critical Path:** Tasks 1 → 2 → 6 → 10 (must complete before Sprint 16)

---

## Task 1: Create Sprint 16 Known Unknowns List

**Status:** ✅ COMPLETE  
**Priority:** Critical  
**Time Spent:** 3 hours  
**Deadline:** First prep task - complete immediately  
**Owner:** Development team  
**Dependencies:** None

### Objective

Create comprehensive list of known unknowns for Sprint 16, following the successful pattern from previous sprints that achieved proactive risk identification.

### Why This Matters

Sprint 16 involves significant new development (reporting infrastructure) and investigative work (gap analysis, parser improvements). Unknown factors could derail sprint progress:
- Which report formats are most useful?
- What causes lexer_invalid_char errors?
- How much parse improvement is achievable?
- Can we impact solve success rate through parser fixes alone?

### Background

Previous sprint Known Unknowns documents achieved excellent results:
- Sprint 5: 22 unknowns identified, zero late surprises
- Pattern: Categorize by sprint priority, assign verification method

Sprint 16 priorities from PROJECT_PLAN.md:
1. Reporting Infrastructure (~8-10h)
2. Gap Analysis (~6-8h)  
3. Targeted Parser Improvements (~10-14h)
4. Retest After Improvements (~2h)

### What Needs to Be Done

#### Step 1: Identify Reporting Infrastructure Unknowns
- What report formats needed? (Markdown, JSON, HTML?)
- Who is the audience for each report?
- What frequency of report generation?
- How to handle historical comparison?
- Where to store generated reports?

#### Step 2: Identify Gap Analysis Unknowns
- How to categorize parse failures beyond error type?
- What patterns exist within lexer_invalid_char?
- Are translate failures correlated with model complexity?
- How to identify "fixable" vs "fundamental" limitations?

#### Step 3: Identify Parser Improvement Unknowns
- What GAMS syntax causes lexer_invalid_char?
- Can grammar be extended without breaking existing parses?
- How to test parser changes without full pipeline rerun?
- What is realistic improvement target for Sprint 16?

#### Step 4: Identify Retest Unknowns
- How long does full pipeline retest take?
- How to measure improvement vs baseline?
- What constitutes success for Sprint 16?

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` with:
- 15-25 unknowns across 4 categories
- Each unknown has: assumption, verification method, priority, resolution plan
- All Critical/High unknowns have research timeline

### Result

Comprehensive unknowns list enabling proactive risk management and targeted research.

### What Was Done

Created comprehensive `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md` with 27 unknowns across 9 categories.

**Statistics:**
- **Total Unknowns:** 27
- **By Priority:** 7 Critical (26%), 11 High (41%), 7 Medium (26%), 2 Low (7%)
- **By Category:**
  - Category 1 (Status Summary Report Generator): 4 unknowns
  - Category 2 (Failure Analysis Report): 3 unknowns
  - Category 3 (Progress Tracking): 2 unknowns
  - Category 4 (Parse Failure Gap Analysis): 4 unknowns
  - Category 5 (Translation Failure Gap Analysis): 3 unknowns
  - Category 6 (Solve Failure Gap Analysis): 2 unknowns
  - Category 7 (Improvement Roadmap): 2 unknowns
  - Category 8 (Identify Top Parse Blockers): 4 unknowns
  - Category 9 (Implement Priority Parser Features): 3 unknowns
- **Estimated Research Time:** 28-36 hours

**Task-to-Unknown Mapping:**
| Prep Task | Unknowns Verified |
|-----------|-------------------|
| Task 2 | 4.1, 4.2, 5.1, 6.1, 8.1 |
| Task 3 | 1.1, 1.2, 1.3, 2.1 |
| Task 4 | 2.2, 2.3, 4.3 |
| Task 5 | 8.2, 9.1, 9.2 |
| Task 6 | 4.4, 8.1, 8.3, 8.4 |
| Task 7 | 4.2, 6.2 |
| Task 8 | 1.4, 3.1, 3.2 |
| Task 9 | 5.2, 5.3, 7.1, 7.2 |
| Task 10 | All unknowns (integration) |

### Verification

- [x] Document created at `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`
- [x] Minimum 15 unknowns identified (27 total)
- [x] All unknowns categorized by sprint priority
- [x] All Critical/High unknowns have verification method
- [x] Research time estimated (28-36 hours)

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/KNOWN_UNKNOWNS.md`

### Acceptance Criteria

- [x] 15+ unknowns identified across all Sprint 16 priorities (27 unknowns)
- [x] Each unknown has assumption, verification method, and priority
- [x] All Critical unknowns have research plan with estimated time
- [x] Template for tracking resolution established
- [x] Unknowns cover all four Sprint 16 priorities

---

## Task 2: Assess Current Baseline Metrics and Blockers

**Status:** ✅ COMPLETE  
**Completed:** January 16, 2026  
**Priority:** Critical  
**Estimated Time:** 2 hours  
**Actual Time:** ~1.5 hours  
**Deadline:** Before Task 6  
**Owner:** Development team  
**Dependencies:** Task 1 (Known Unknowns)  
**Unknowns Verified:** 4.1, 4.2, 5.1, 6.1, 8.1

### Completion Summary

**Deliverable Created:** `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md`

**Key Findings:**
- Parse stage is primary bottleneck: 126/160 models (78.8%) fail to parse
- `lexer_invalid_char` dominates: 86.5% of parse failures (109/126 models)
- ALL solve failures (100%) are `path_syntax_error` - suggests systematic MCP generation issue
- Translation failures are diverse: 6 categories, no single dominant cause

**Unknowns Verified:**
- ✅ 4.1: Confirmed lexer_invalid_char breakdown (109 models, 86.5%)
- ❌ 4.2: CORRECTED - path_syntax_error is SOLVE stage, not parse (14 models at solve, 0 at parse)
- ✅ 5.1: Confirmed translation failure distribution across 6 categories
- ✅ 6.1: Confirmed 100% of solve failures are path_syntax_error
- ✅ 8.1: Confirmed Sprint 16 should target dollar control handling

**Sprint 16 Targets Set:**
- Minimum: +10% parse rate (to 31.3%)
- Target: +20% parse rate (to 41.3%)
- Stretch: +30% parse rate (to 51.3%)

### Objective

Deep-dive into Sprint 15 baseline metrics to identify highest-impact improvement targets for Sprint 16.

### Why This Matters

Sprint 16 gap analysis and parser improvements must be prioritized by impact. Need to understand:
- Which parse errors block the most models?
- Which translate errors are parser-fixable vs fundamental?
- What is the "ceiling" for improvement without solver changes?

### Background

Sprint 15 established baseline (from `baseline_metrics.json`):
- **Parse:** 34/160 success (21.3%), 126 failures
- **Translate:** 17/34 success (50% of parsed), 17 failures
- **Solve:** 3/17 success (17.6% of translated), 14 failures
- **Full Pipeline:** 1/160 success (0.6%)

Top parse blockers:
- lexer_invalid_char: 109 models (68.1% of all models)
- path_syntax_error: 14 models (8.8%)
- model_no_objective_def: 5 models (3.1%)

### What Needs to Be Done

#### Step 1: Analyze Parse Failure Distribution
```bash
# Review parse error breakdown
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome != "parse_success") | .parse_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- What percentage of parse failures are lexer vs parser errors?
- Are there clusters of similar failures?
- Which errors might be quick wins vs major grammar changes?

#### Step 2: Analyze Translate Failure Distribution
```bash
# Review translate error breakdown  
cat tests/output/pipeline_results.json | jq '.models[] | select(.translate_outcome != null and .translate_outcome != "translate_success") | .translate_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- Which translate errors correlate with specific model features?
- Are any translate errors fixable at parse stage?
- What is theoretical maximum translate success with perfect parsing?

#### Step 3: Analyze Solve Failure Distribution
```bash
# Review solve error breakdown
cat tests/output/pipeline_results.json | jq '.models[] | select(.solve_outcome != null and .solve_outcome != "solve_success") | .solve_outcome' | sort | uniq -c | sort -rn
```

Questions to answer:
- Are solve failures due to MCP formulation or model characteristics?
- Which solve failures might be addressable in translation stage?

#### Step 4: Create Impact Analysis Table

| Blocker | Count | % of Total | Fixable in Sprint 16? | Estimated Effort |
|---------|-------|------------|----------------------|------------------|
| lexer_invalid_char | 109 | 68.1% | Partially | High |
| path_syntax_error | 14 | 8.8% | Maybe | Medium |
| model_no_objective_def | 5 | 3.1% | No (model issue) | N/A |

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md` with:
- Detailed breakdown of each error category
- Impact ranking by model count
- Fixability assessment
- Recommended focus areas for Sprint 16

### Result

Clear understanding of where to focus Sprint 16 efforts for maximum impact.

### Verification

- [ ] Parse error distribution analyzed and documented
- [ ] Translate error distribution analyzed and documented
- [ ] Solve error distribution analyzed and documented
- [ ] Impact ranking table created
- [ ] Recommended focus areas identified

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/BASELINE_ANALYSIS.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.1, 4.2, 5.1, 6.1, 8.1

### Acceptance Criteria

- [ ] All error categories from taxonomy analyzed
- [ ] Count and percentage for each error type documented
- [ ] Fixability assessment for top 10 blockers
- [ ] Recommended Sprint 16 focus areas identified
- [ ] Document links to baseline_metrics.json and pipeline_results.json
- [ ] Unknowns 4.1, 4.2, 5.1, 6.1, 8.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 3: Research Report Generation Approaches

**Status:** ✅ COMPLETE  
**Completed:** January 16, 2026  
**Priority:** High  
**Estimated Time:** 3 hours  
**Actual Time:** ~2.5 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns Verified:** 1.1, 1.2, 1.3, 2.1

### Completion Summary

**Deliverable Created:** `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md`

**Key Decisions:**
1. **Output Formats:** Markdown (primary) + JSON (secondary), HTML deferred
2. **Template System:** Jinja2 for flexibility with tabulate for table generation
3. **Architecture:** Modular analyzers (status, failure, progress) with pluggable renderers
4. **Failure Grouping:** Two-level hierarchy (Stage → Error Category, full 47-category taxonomy)

**Unknowns Verified:**
- ✅ 1.1: Report format - Markdown + JSON
- ✅ 1.2: Status metrics - 6 priority-ordered sections defined
- ✅ 1.3: Template system - Jinja2 selected over f-strings
- ✅ 2.1: Failure grouping - Stage → Category with all errors shown

**Implementation Estimate:** 17 hours across 4 days

### Objective

Research approaches for automated report generation to inform Sprint 16 Priority 1 (Reporting Infrastructure) design.

### Why This Matters

Sprint 16 will create `generate_report.py` tool producing:
- GAMSLIB_STATUS.md - Overall status summary
- FAILURE_ANALYSIS.md - Detailed failure breakdown
- Progress tracking against historical baselines

Need to decide:
- Report format(s) - Markdown? JSON? HTML?
- Data sources - pipeline_results.json? Direct queries?
- Update frequency - On-demand? Automated CI?

### Background

Current state:
- `run_full_test.py` generates `pipeline_results.json` with comprehensive data
- Manual reports created in Sprint 15 (SPRINT_BASELINE.md, GAMSLIB_TESTING.md)
- No automated report generation exists

PROJECT_PLAN.md specifies:
- `generate_report.py` accepting `--format` and `--output` flags
- GAMSLIB_STATUS.md with success rates, model tables, filtering stats
- FAILURE_ANALYSIS.md with error breakdowns and improvement recommendations

### What Needs to Be Done

#### Step 1: Survey Report Generation Libraries

Research Python libraries for report generation:

| Library | Pros | Cons | Best For |
|---------|------|------|----------|
| Jinja2 | Template-based, flexible | Requires templates | Markdown, HTML |
| tabulate | Simple tables | Limited formatting | Quick tables |
| Rich | Beautiful console output | Terminal-focused | Console reports |
| Markdown | Native Python | Basic features | Simple Markdown |

#### Step 2: Analyze Existing Manual Reports

Review manually-created reports to understand patterns:
- `docs/testing/SPRINT_BASELINE.md` - Structure, metrics, tables
- `docs/testing/GAMSLIB_TESTING.md` - Model tracking, status tables

Extract common patterns:
- Summary statistics (counts, percentages)
- Model tables with status
- Error category breakdowns
- Comparison sections

#### Step 3: Design Report Architecture

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

#### Step 4: Create Report Template Mockups

Design template structure for GAMSLIB_STATUS.md:
```markdown
# GAMSLIB Pipeline Status Report

**Generated:** {{ timestamp }}
**Data Source:** {{ data_file }}
**Models Tested:** {{ total_models }}

## Executive Summary

- **Parse Success:** {{ parse_success }}/{{ total }} ({{ parse_pct }}%)
- **Translate Success:** {{ translate_success }}/{{ parsed }} ({{ translate_pct }}%)
- **Solve Success:** {{ solve_success }}/{{ translated }} ({{ solve_pct }}%)
- **Full Pipeline:** {{ full_success }}/{{ total }} ({{ full_pct }}%)

## Model Status Table

| Model | Parse | Translate | Solve | Status |
|-------|-------|-----------|-------|--------|
{% for model in models %}
| {{ model.name }} | {{ model.parse }} | {{ model.translate }} | {{ model.solve }} | {{ model.status }} |
{% endfor %}

## Filtering Statistics

- MVP Filter Applied: {{ mvp_filter }}
- Models Excluded: {{ excluded_count }}
...
```

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` with:
- Library comparison and recommendation
- Report architecture design
- Template mockups for each report type
- Implementation plan for Sprint 16

### Result

Clear design for reporting infrastructure ready for Sprint 16 implementation.

### Verification

- [ ] Library options researched and compared
- [ ] Existing manual reports analyzed for patterns
- [ ] Report architecture designed
- [ ] Template mockups created for each report type
- [ ] Implementation plan documented

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.1, 1.2, 1.3, 2.1

### Acceptance Criteria

- [ ] At least 3 report generation approaches compared
- [ ] Recommended approach selected with rationale
- [ ] Architecture diagram/description created
- [ ] Template mockups for GAMSLIB_STATUS.md and FAILURE_ANALYSIS.md
- [ ] Estimated implementation time for Sprint 16
- [ ] Unknowns 1.1, 1.2, 1.3, 2.1 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 4: Design Failure Analysis Report Schema

**Status:** ✅ COMPLETE  
**Completed:** January 16, 2026  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Actual Time:** ~2 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns Verified:** 2.2, 2.3, 4.3

### Completion Summary

**Deliverable Created:** `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md`

**Key Decisions:**
1. **Error Examples:** Include ONE representative error per category (200 char limit)
2. **Recommendations:** Semi-automated with pattern-to-recommendation mapping
3. **Prioritization:** Score = Models / Effort Hours (fixability filter applied)
4. **Progress Tracking:** Sprint-over-sprint delta comparison with newly passing/failing lists

**Schema Highlights:**
- Complete JSON Schema for failure analysis data
- Pattern detection rules for lexer/translate/solve errors
- Improvement roadmap template with priority scoring
- Progress comparison format for regression detection

**Unknowns Verified:**
- ✅ 2.2: Include one error example per category
- ✅ 2.3: Semi-automated recommendations via pattern mapping
- ✅ 4.3: Priority formula: Models/Effort with fixability filter

### Objective

Design the schema and content structure for FAILURE_ANALYSIS.md report that will guide parser improvement decisions.

### Why This Matters

Gap analysis in Sprint 16 depends on clear failure categorization and actionable insights. The failure analysis report must:
- Group failures by category and subcategory
- Identify patterns within error types
- Prioritize by fixability and impact
- Track improvement over time

### Background

Sprint 15 error taxonomy has 47 outcome categories:
- Parse outcomes: 8 categories
- Translate outcomes: 21 categories  
- Solve outcomes: 18 categories

Top parse errors:
- lexer_invalid_char: 109 models - Need subcategorization
- path_syntax_error: 14 models - Need pattern analysis
- Other errors: Lower counts but may be quick wins

### What Needs to Be Done

#### Step 1: Design Failure Hierarchy Schema

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
          - pattern: "Embedded code"
            models: [model3, model4, ...]
            fixable: false
            reason: "Requires GAMS execution"
    parser_errors:
      path_syntax_error:
        count: 14
        percentage: 8.8%
        subcategories: [...]
  translate_failures:
    [similar structure]
  solve_failures:
    [similar structure]
```

#### Step 2: Design Pattern Detection Rules

For lexer_invalid_char errors, define pattern detection:
```python
LEXER_ERROR_PATTERNS = {
    'dollar_control': r'\$[a-zA-Z]+',  # $ontext, $offtext, $include
    'embedded_code': r'\$call|\$execute',
    'special_chars': r'[^\x00-\x7F]',  # Non-ASCII
    'macro_syntax': r'%[a-zA-Z]+%',
}
```

#### Step 3: Design Improvement Roadmap Section

```markdown
## Improvement Roadmap

### High Impact / Low Effort (Quick Wins)
| Issue | Models Affected | Estimated Fix | Sprint Target |
|-------|-----------------|---------------|---------------|
| ... | ... | ... | ... |

### High Impact / High Effort (Major Work)
| Issue | Models Affected | Estimated Fix | Sprint Target |
|-------|-----------------|---------------|---------------|
| ... | ... | ... | ... |

### Low Impact (Defer)
| Issue | Models Affected | Reason to Defer |
|-------|-----------------|-----------------|
| ... | ... | ... |
```

#### Step 4: Design Comparison Section

```markdown
## Progress Tracking

### Baseline (Sprint 15)
| Stage | Success | Failure | Rate |
|-------|---------|---------|------|
| Parse | 34 | 126 | 21.3% |
| Translate | 17 | 17 | 50.0% |
| Solve | 3 | 14 | 17.6% |

### Current (Sprint 16)
| Stage | Success | Failure | Rate | Delta |
|-------|---------|---------|------|-------|
| Parse | ?? | ?? | ??% | +??% |
| Translate | ?? | ?? | ??% | +??% |
| Solve | ?? | ?? | ??% | +??% |
```

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md` with:
- Complete JSON/YAML schema for failure analysis data
- Pattern detection rules for subcategorization
- Report template structure
- Comparison/progress tracking format

### Result

Clear schema enabling automated failure analysis report generation.

### Verification

- [ ] Failure hierarchy schema defined
- [ ] All 47 error categories mapped
- [ ] Pattern detection rules designed for top errors
- [ ] Improvement roadmap format defined
- [ ] Progress tracking format defined

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/FAILURE_REPORT_SCHEMA.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 2.2, 2.3, 4.3

### Acceptance Criteria

- [ ] Schema covers all error categories from taxonomy
- [ ] Subcategorization approach defined for top blockers
- [ ] Pattern detection rules documented
- [ ] Improvement roadmap template created
- [ ] Progress comparison format enables sprint-over-sprint tracking
- [ ] Unknowns 2.2, 2.3, 4.3 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 5: Survey GAMS Grammar Extension Patterns

**Status:** ✅ COMPLETE  
**Time Spent:** ~2 hours  
**Priority:** High  
**Estimated Time:** 3-4 hours  
**Deadline:** Before Task 6  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 8.2, 9.1, 9.2

### What Was Done

1. **Analyzed GAMS grammar structure** (`src/gams/gams_grammar.lark`)
   - 604 lines, ~80 rules, ~50 terminals
   - Uses Earley parser with `ambiguity="resolve"`
   - Well-organized sections: blocks, declarations, expressions, tokens

2. **Identified 5 extension patterns:**
   - Pattern 1: Adding new `%ignore` patterns (lowest risk)
   - Pattern 2: Adding new terminals with priorities
   - Pattern 3: Adding statement alternatives
   - Pattern 4: Extending existing rules
   - Pattern 5: Adding optional elements

3. **Researched Lark best practices:**
   - Terminal priorities (`.N` suffix) control matching order
   - Tree aliases (`-> name`) normalize different syntaxes
   - `%ignore` directive for content skipping at lexer level
   - Earley parser handles ambiguity gracefully

4. **Created comprehensive testing checklist:**
   - 4-layer testing approach (unit, regression, integration, IR validation)
   - Regression detection protocol
   - CI integration recommendations

5. **Analyzed dollar control handling:**
   - Grammar ALREADY has `%ignore /(?si)\$ontext.*?\$offtext/`
   - Issue likely: edge cases with whitespace, encoding
   - Recommended: Enhanced pattern or preprocessing approach

### Result

**Key Patterns Identified:**
1. **`%ignore` pattern enhancement** - Lowest risk approach for dollar control
2. **Statement alternatives** - Add new statements at end of `?stmt` rule
3. **Terminal priorities** - Use `.N` suffix to control matching order
4. **Preprocessing** - Python preprocessing before parsing for full control

**Critical Finding:** The grammar already handles `$ontext/$offtext` via `%ignore`. Sprint 16 should focus on enhancing the pattern or adding preprocessing, not grammar restructuring.

### Objective

Study existing GAMS grammar (`gams.lark`) to understand extension patterns and prepare for parser improvements.

### Why This Matters

Sprint 16 Priority 3 will modify the GAMS parser to handle more model syntax. Need to understand:
- Current grammar structure and patterns
- How to add new token types
- How to extend rules without breaking existing parsing
- Testing strategies for grammar changes

### Background

Current grammar location: `src/gams/gams_grammar.lark`
Current lexer: Lark-based with Earley parsing (not LALR)

Known issues to address:
- Dollar control options ($ontext, $offtext, etc.)
- Special characters causing lexer_invalid_char
- Path syntax variations

### What Needs to Be Done

#### Step 1: Analyze Current Grammar Structure

```bash
# Review grammar file structure
wc -l src/nlp2mcp/parser/gams.lark
head -100 src/nlp2mcp/parser/gams.lark
```

Document:
- Total rule count
- Major section breakdown (statements, expressions, terminals)
- Token definition patterns
- Import/include patterns

#### Step 2: Identify Grammar Extension Points

Find where new syntax can be added:
- Terminal definitions for new token types
- Rule alternatives for syntax variations
- Precedence handling for operators

Document extension patterns:
```lark
// Pattern 1: Adding new keyword
NEW_KEYWORD: "keyword"i

// Pattern 2: Adding to statement alternatives
statement: assignment | declaration | NEW_STATEMENT

// Pattern 3: Adding optional syntax
declaration: name ["(" indices ")"] [bounds]
```

#### Step 3: Study Lark Extension Best Practices

Research Lark documentation for:
- Adding lexer modes (for embedded content)
- Handling ambiguous grammar
- Error recovery options
- Testing grammar changes

#### Step 4: Create Grammar Extension Checklist

```markdown
## Grammar Extension Checklist

### Before Making Changes
- [ ] Create failing test case for new syntax
- [ ] Backup current grammar
- [ ] Identify specific grammar rule to modify

### Making Changes
- [ ] Add terminal definition if new token
- [ ] Add rule or rule alternative
- [ ] Update any imports/includes
- [ ] Check for ambiguity with existing rules

### After Making Changes
- [ ] Run failing test - should pass
- [ ] Run full test suite - no regressions
- [ ] Run pipeline on GAMSLIB - check impact
- [ ] Document change in grammar changelog
```

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md` with:
- Current grammar analysis
- Extension patterns and examples
- Best practices from Lark documentation
- Testing checklist for grammar changes

### Result

Guide enabling safe, systematic grammar improvements in Sprint 16.

### Verification

- [x] Current grammar analyzed and documented
- [x] Extension patterns identified and documented
- [x] Lark best practices researched
- [x] Testing checklist created
- [x] Guide ready for Sprint 16 use

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/GRAMMAR_EXTENSION_GUIDE.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 8.2, 9.1, 9.2

### Acceptance Criteria

- [x] Grammar structure documented (rules, terminals, sections)
- [x] At least 3 extension patterns with examples
- [x] Lark-specific considerations documented
- [x] Testing checklist comprehensive
- [x] Potential risks/pitfalls identified
- [x] Unknowns 8.2, 9.1, 9.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 6: Analyze Top Parse Blockers (lexer_invalid_char)

**Status:** ✅ COMPLETE  
**Completed:** January 18, 2026  
**Priority:** Critical  
**Estimated Time:** 3-4 hours  
**Actual Time:** ~3 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** Task 5 (Grammar Extension Patterns)  
**Unknowns Verified:** 4.4, 8.1, 8.3, 8.4

### Completion Summary

**Deliverable Created:** `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md`

**Critical Finding:** The original assumption that dollar control causes lexer errors was INCORRECT. The grammar already handles `$ontext/$offtext` correctly. Errors occur in GAMS data syntax that the grammar doesn't fully support.

**Key Results:**
- Analyzed 219 GAMS models (expanded from original 160)
- 59 models parse successfully (27%)
- 153 models fail with lexer errors (70%)
- 7 models fail with internal errors (3%)

**Error Subcategorization:**

| Subcategory | Count | % of Lexer Errors | Fixability |
|-------------|-------|-------------------|------------|
| Complex set data | 91 | 59% | Partial |
| Tuple syntax `(a,b).c` | 12 | 8% | Yes |
| Numeric context | 11 | 7% | Yes |
| Keyword case | 9 | 6% | Yes (Low effort) |
| Operator context | 9 | 6% | Partial |
| Quoted descriptions | 7 | 5% | Yes |
| Dot notation | 5 | 3% | Partial |
| Hyphenated elements | 3 | 2% | Yes (Low effort) |
| Abort statement | 3 | 2% | Yes (Low effort) |

**Sprint 16 Targets:**
- Priority 1 (Low-effort): 26 models, 2.5 days
- Priority 2 (Medium-effort): 19 models, 2.5 days
- Expected improvement: 39-47% parse rate (from 27%)

**Unknowns Verified:**
- ✅ 4.4: CORRECTED - Most errors are from syntax we SHOULD support, not exclude
- ✅ 8.1: Updated targets based on actual root causes
- ✅ 8.3: CORRECTED - Dollar control already handled; focus on data syntax
- ✅ 8.4: Complete character analysis (no encoding issues, all standard ASCII)

### Objective

Deep analysis of lexer_invalid_char errors to identify specific causes and develop fix strategies.

### Why This Matters

lexer_invalid_char accounts for 109/160 models (68.1%) - by far the largest blocker. Understanding what characters/patterns cause these errors is essential for Sprint 16 parser improvements.

Potential causes:
- Dollar control options ($ontext, $offtext, $if, etc.)
- Special GAMS characters
- Non-ASCII characters in comments
- Embedded code blocks

### Background

From Sprint 15 baseline:
- 109 models fail with lexer_invalid_char
- This single error category represents 68.1% of all failures
- Fixing even 50% would dramatically improve parse rate

### What Needs to Be Done

#### Step 1: Sample Failing Models

```bash
# Get list of models with lexer_invalid_char
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -20
```

#### Step 2: Examine Error Messages

```bash
# For each failing model, examine the actual error
for model in $(cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "lexer_invalid_char") | .model_name' | head -10); do
    echo "=== $model ==="
    cat tests/output/pipeline_results.json | jq -r ".models[] | select(.model_name == \"$model\") | .parse_error"
done
```

Look for patterns:
- Line numbers where errors occur
- Specific characters mentioned
- Common prefixes/patterns

#### Step 3: Categorize by Root Cause

Create subcategories:

| Subcategory | Description | Count | Example |
|-------------|-------------|-------|---------|
| dollar_control | $ontext, $offtext, etc. | ?? | model_x.gms:15 |
| embedded_execute | $call, $execute blocks | ?? | model_y.gms:42 |
| special_chars | Non-ASCII, control chars | ?? | model_z.gms:8 |
| unknown | Needs investigation | ?? | - |

#### Step 4: Develop Fix Strategies

For each subcategory:

**Dollar Control:**
- Strategy: Add lexer mode for dollar regions
- Effort: Medium (new lexer mode)
- Risk: May affect other parsing

**Embedded Execute:**
- Strategy: Skip/ignore these blocks
- Effort: Low (lexer skip rule)
- Risk: Loss of functionality

**Special Characters:**
- Strategy: Expand character class in lexer
- Effort: Low (terminal modification)
- Risk: Minimal

#### Step 5: Prioritize for Sprint 16

| Subcategory | Models | Fixable? | Effort | Sprint 16 Target |
|-------------|--------|----------|--------|------------------|
| dollar_control | ?? | Yes | Medium | Yes |
| special_chars | ?? | Yes | Low | Yes |
| embedded_execute | ?? | Partial | Low | Yes (skip) |

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md` with:
- Complete subcategorization of lexer_invalid_char
- Model counts for each subcategory
- Fix strategy for each subcategory
- Sprint 16 implementation plan

### Result

Clear understanding of lexer errors and actionable fix strategies for Sprint 16.

### Verification

- [x] All 153 models with lexer_invalid_char categorized (expanded from original 109)
- [x] Subcategories defined with counts (11 distinct subcategories)
- [x] Fix strategy for each subcategory
- [x] Effort estimates for each fix (Low/Medium/High)
- [x] Sprint 16 targets defined (Priority 1: 26 models, Priority 2: 19 models)

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/LEXER_ERROR_ANALYSIS.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.4, 8.1, 8.3, 8.4

### Acceptance Criteria

- [x] At least 80% of lexer_invalid_char errors categorized (100% categorized)
- [x] Top 3 subcategories have detailed fix strategies
- [x] Effort estimates provided for each strategy
- [x] Clear Sprint 16 targets based on impact/effort
- [x] Example fixes documented for implementation
- [x] Unknowns 4.4, 8.1, 8.3, 8.4 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 7: Research PATH Syntax Error Patterns

**Status:** ✅ COMPLETE  
**Completed:** January 19, 2026  
**Priority:** High  
**Estimated Time:** 2-3 hours  
**Actual Time:** ~2 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** Task 2 (Baseline Analysis)  
**Unknowns Verified:** 4.2, 6.2

### Completion Summary

**Deliverable Created:** `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md`

**Critical Finding:** The `path_syntax_error` name is misleading - these are NOT PATH solver errors or file path issues. They are **GAMS compilation errors** in generated MCP files caused by bugs in `src/emit/emit_gams.py`.

**Key Results:**
- Analyzed all 14 models with solve-stage path_syntax_error
- ALL 14 failures (100%) are addressable nlp2mcp code generation bugs
- 0 failures are due to PATH solver issues or inherent model difficulties

**Error Pattern Distribution:**

| Pattern | Count | Root Cause |
|---------|-------|------------|
| Unary minus before parens | 10 | `-(expr)` should be `(-1)*(expr)` |
| Set element quoting | 3 | Inconsistent quoting in generated code |
| Scalar declaration | 1 | Missing identifier name |

**Sprint 16 Fix Impact:**
- Current solve rate: 17.6% (3/17 translated models)
- Expected after fixes: 76-100% (13-17/17 translated models)
- Implementation effort: 9-15 hours total

**Unknowns Verified:**
- ✅ 4.2: VERIFIED - path_syntax_error is code generation bug, not file paths
- ✅ 6.2: VERIFIED - ALL solve failures are addressable nlp2mcp bugs

### Objective

Analyze path_syntax_error failures to understand patterns and develop fix strategies.

### Why This Matters

path_syntax_error affects 14 models (8.8% of total). While smaller than lexer_invalid_char, these may be quicker wins if patterns are consistent.

### Background

path_syntax_error was originally (incorrectly) thought to indicate:
- ~~File path issues in GAMS code~~
- ~~Include statement problems~~
- ~~Reference to external files~~

**CORRECTED:** path_syntax_error actually indicates GAMS compilation errors in generated MCP files - bugs in nlp2mcp's code generation, not PATH solver or file path issues.

### What Needs to Be Done

#### Step 1: Identify Affected Models

```bash
# List models with path_syntax_error
cat tests/output/pipeline_results.json | jq -r '.models[] | select(.parse_outcome == "path_syntax_error") | .model_name'
```

#### Step 2: Examine Error Details

```bash
# Get error details for each model
cat tests/output/pipeline_results.json | jq '.models[] | select(.parse_outcome == "path_syntax_error") | {model: .model_name, error: .parse_error}'
```

#### Step 3: Categorize Patterns

Look for:
- Include statements with paths
- Relative vs absolute paths
- Platform-specific path separators
- External file references

#### Step 4: Develop Fix Strategies

Potential fixes:
- Normalize path syntax in preprocessing
- Handle include statements specially
- Ignore/skip external file references

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md` with:
- List of affected models
- Pattern categorization
- Fix strategies
- Sprint 16 recommendations

### Result

Understanding of path errors and strategies for fixing or working around them.

### Verification

- [x] All 14 models examined
- [x] Error patterns identified (3 distinct patterns)
- [x] Fix strategies documented
- [x] Effort estimates provided (9-15 hours total)

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/PATH_ERROR_ANALYSIS.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 4.2, 6.2

### Acceptance Criteria

- [x] All path_syntax_error models analyzed (14 models)
- [x] At least 2 distinct patterns identified (3 patterns: unary minus, set quoting, scalar declaration)
- [x] Fix strategy for each pattern (targeting `src/emit/emit_gams.py`)
- [x] Clear recommendation for Sprint 16 scope (9-15 hours, 76-100% solve rate expected)
- [x] Unknowns 4.2, 6.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 8: Design Progress Tracking Schema

**Status:** ✅ COMPLETE  
**Completed:** January 19, 2026  
**Priority:** Medium  
**Estimated Time:** 2 hours  
**Actual Time:** ~1.5 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** Task 3 (Report Generation Research)  
**Unknowns Verified:** 1.4, 3.1, 3.2

### Completion Summary

**Deliverable Updated:** `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md` - Added comprehensive "Progress Tracking Design" section

**Key Decisions:**
1. **Schema:** JSON Schema v1.0.0 with `snapshots` array containing metrics and model_status
2. **Timestamp:** ISO 8601 format with timezone
3. **Snapshot ID:** `sprint{N}_{YYYYMMDD}` format for human readability
4. **Version tracking:** Schema version, nlp2mcp version, git commit hash
5. **Model tracking:** Full model_status in each snapshot (~8KB per snapshot)
6. **Regression detection:** Three-tier (rate, model, error) with configurable thresholds

**Schema Highlights:**
- Compatible with existing `baseline_metrics.json`
- Includes conversion utility `baseline_to_snapshot()`
- Supports ~50 snapshots in ~400KB (acceptable JSON size)
- Per-model status enables change detection and debugging

**Regression Thresholds:**
- Rate: 2% for stages, 1% for full pipeline
- Model: Any regression flagged (threshold: 0)
- Error: Flag if category increases by >5

**Unknowns Verified:**
- ✅ 1.4: Timestamp/versioning - ISO 8601, snapshot IDs, three-version tracking
- ✅ 3.1: Schema design - Complete JSON Schema with examples
- ✅ 3.2: Regression detection - Three-tier with CI integration

### Objective

Design schema for tracking pipeline progress over time, enabling sprint-over-sprint comparison.

### Why This Matters

Sprint 16 introduces targeted improvements. Need to measure:
- Improvement from baseline
- Which fixes had most impact
- Trend over multiple sprints

### Background

Current tracking:
- baseline_metrics.json captures Sprint 15 baseline
- pipeline_results.json has per-model results
- No historical comparison infrastructure

### What Needs to Be Done

#### Step 1: Design Progress Database Schema

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
    },
    {
      "sprint": 16,
      "date": "2025-01-XX",
      "metrics": {...},
      "changes": "Parser improvements for dollar control"
    }
  ]
}
```

#### Step 2: Design Comparison Report Format

```markdown
## Progress Summary

| Sprint | Parse Rate | Δ | Translate Rate | Δ | Solve Rate | Δ |
|--------|------------|---|----------------|---|------------|---|
| 15 (baseline) | 21.3% | - | 50.0% | - | 17.6% | - |
| 16 | ??% | +??% | ??% | +??% | ??% | +??% |
```

#### Step 3: Design Model-Level Tracking

Track individual model progress:
```json
{
  "model_progress": {
    "model_name": {
      "sprint_15": "lexer_invalid_char",
      "sprint_16": "parse_success",
      "improvement": true
    }
  }
}
```

### Changes

Add to `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md`:
- Progress tracking schema
- Comparison report format
- Model-level tracking design

### Result

Comprehensive progress tracking design enabling automated sprint-over-sprint comparison with:
- JSON Schema v1.0.0 for `progress_history.json`
- Comparison report template (PROGRESS_REPORT.md)
- Model-level change detection algorithm
- Three-tier regression detection with CI integration

### Verification

- [x] Progress database schema defined (JSON Schema v1.0.0)
- [x] Comparison report format designed (Jinja2 template with trend icons)
- [x] Model-level tracking approach defined (full status per snapshot)
- [x] Integration with reporting infrastructure planned (CLI flags, conversion utilities)

### Deliverables

- Updates to `docs/planning/EPIC_3/SPRINT_16/REPORT_DESIGN.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 1.4, 3.1, 3.2

### Acceptance Criteria

- [x] Schema supports multi-sprint history (snapshots array, unlimited history)
- [x] Comparison metrics clearly defined (rate deltas, trend icons, model changes)
- [x] Model-level tracking enables debugging (per-model status, change detection)
- [x] Schema compatible with existing baseline_metrics.json (includes conversion utility)
- [x] Unknowns 1.4, 3.1, 3.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 9: Review Sprint 15 Deliverables and Learnings

**Status:** Not Started  
**Priority:** Medium  
**Estimated Time:** 1-2 hours  
**Deadline:** Before Sprint 16 Day 1  
**Owner:** Development team  
**Dependencies:** None  
**Unknowns Verified:** 5.2, 5.3, 7.1, 7.2

### Objective

Consolidate learnings from Sprint 15 to inform Sprint 16 approach.

### Why This Matters

Sprint 15 was extensive (10 days). Key deliverables and learnings should be captured to:
- Avoid repeating mistakes
- Build on successful patterns
- Ensure continuity

### Background

Sprint 15 accomplishments:
- run_full_test.py MVP pipeline
- 47-category error taxonomy
- baseline_metrics.json
- JSON database schema v2.1.0
- test_solve.py test suite

### What Needs to Be Done

#### Step 1: Review Sprint 15 Documentation

- SPRINT_BASELINE.md
- GAMSLIB_TESTING.md
- Error taxonomy in run_full_test.py
- README.md Sprint 15 section

#### Step 2: Identify Key Learnings

Document:
- What worked well
- What was challenging
- What would do differently

#### Step 3: Extract Actionable Items

Identify items for Sprint 16:
- Technical debt to address
- Patterns to replicate
- Approaches to avoid

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_15_REVIEW.md` with:
- Deliverables summary
- Key learnings
- Recommendations for Sprint 16

### Result

Consolidated knowledge transfer from Sprint 15 to Sprint 16.

### Verification

- [ ] All Sprint 15 deliverables reviewed
- [ ] Key learnings documented
- [ ] Actionable recommendations for Sprint 16

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/SPRINT_15_REVIEW.md`
- Updated KNOWN_UNKNOWNS.md with verification results for Unknowns 5.2, 5.3, 7.1, 7.2

### Acceptance Criteria

- [ ] All major Sprint 15 deliverables listed
- [ ] At least 5 key learnings documented
- [ ] At least 3 actionable recommendations for Sprint 16
- [ ] Technical debt items identified if any
- [ ] Unknowns 5.2, 5.3, 7.1, 7.2 verified and updated in KNOWN_UNKNOWNS.md

---

## Task 10: Plan Sprint 16 Detailed Schedule

**Status:** Not Started  
**Priority:** Critical  
**Estimated Time:** 2-3 hours  
**Deadline:** Final prep task - complete after all others  
**Owner:** Development team  
**Dependencies:** All previous tasks  
**Unknowns Verified:** All unknowns (integration)

### Objective

Create detailed day-by-day schedule for Sprint 16 based on prep task findings.

### Why This Matters

Sprint 16 has 26-34 hours of estimated work across four priorities. Need clear schedule to:
- Ensure all work fits in sprint timeframe
- Sequence work correctly (dependencies)
- Identify potential bottlenecks

### Background

PROJECT_PLAN.md Sprint 16 estimates:
- Reporting Infrastructure: ~8-10h
- Gap Analysis: ~6-8h
- Targeted Parser Improvements: ~10-14h
- Retest After Improvements: ~2h
- Total: ~26-34h

### What Needs to Be Done

#### Step 1: Synthesize Prep Task Findings

Gather insights from:
- Task 1: Known unknowns requiring research
- Task 2: Baseline analysis priorities
- Task 3: Report generation approach
- Task 4: Failure analysis schema
- Task 5: Grammar extension patterns
- Task 6: Lexer error fix strategies
- Task 7: Path error fix strategies
- Task 8: Progress tracking schema
- Task 9: Sprint 15 learnings

#### Step 2: Create Day-by-Day Schedule

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

#### Step 3: Identify Dependencies and Critical Path

```
Day 1-2 (Reporting) ─┬─> Day 3-4 (Gap Analysis) ─┬─> Day 9 (Retest)
                     │                           │
                     └─> Day 5-8 (Parser) ───────┘
```

Critical path: Reporting → Gap Analysis → Retest

#### Step 4: Define Success Criteria

Sprint 16 success metrics:
- Parse success rate: Target 35%+ (from 21.3%)
- Translate success rate: Maintain 50%+
- Full pipeline: Target 5%+ (from 0.6%)
- Reports: GAMSLIB_STATUS.md, FAILURE_ANALYSIS.md generated

### Changes

Create `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md` with:
- Day-by-day schedule
- Dependency diagram
- Success criteria
- Risk mitigation plan

### Result

Clear, actionable schedule for Sprint 16 execution.

### Verification

- [ ] All prep task findings incorporated
- [ ] Schedule fits sprint timeframe
- [ ] Dependencies identified
- [ ] Success criteria defined
- [ ] Risks identified with mitigation

### Deliverables

- `docs/planning/EPIC_3/SPRINT_16/SPRINT_SCHEDULE.md`
- Updated KNOWN_UNKNOWNS.md with final status for all unknowns

### Acceptance Criteria

- [ ] Day-by-day schedule complete
- [ ] All Sprint 16 priorities scheduled
- [ ] Dependencies clearly marked
- [ ] Success criteria quantified
- [ ] Ready for Sprint 16 Day 1
- [ ] All unknowns reviewed and final status updated in KNOWN_UNKNOWNS.md

---

## Success Criteria Summary

Sprint 16 Prep is complete when:

1. **Known Unknowns:** 15+ unknowns identified and documented
2. **Baseline Analysis:** Top blockers analyzed with fix strategies
3. **Report Design:** Architecture and templates ready
4. **Failure Schema:** Report schema enables actionable analysis
5. **Grammar Guide:** Extension patterns documented
6. **Lexer Analysis:** lexer_invalid_char categorized with fix strategies
7. **Path Analysis:** path_syntax_error patterns identified
8. **Progress Tracking:** Schema enables sprint comparison
9. **Sprint 15 Review:** Learnings captured
10. **Schedule:** Day-by-day plan ready

---

## Appendix: Document Cross-References

### Sprint 16 Reference Documents

| Document | Purpose | Location |
|----------|---------|----------|
| PROJECT_PLAN.md | Sprint 16 goals (lines 334-451) | docs/planning/EPIC_3/ |
| baseline_metrics.json | Sprint 15 baseline | tests/output/ |
| pipeline_results.json | Per-model results | tests/output/ |
| run_full_test.py | Pipeline infrastructure | tests/ |
| gams.lark | GAMS grammar | src/nlp2mcp/parser/ |
| SPRINT_BASELINE.md | Sprint 15 baseline doc | docs/testing/ |

### Prep Task Deliverables

| Task | Deliverable | Location |
|------|-------------|----------|
| 1 | KNOWN_UNKNOWNS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 2 | BASELINE_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 3 | REPORT_DESIGN.md | docs/planning/EPIC_3/SPRINT_16/ |
| 4 | FAILURE_REPORT_SCHEMA.md | docs/planning/EPIC_3/SPRINT_16/ |
| 5 | GRAMMAR_EXTENSION_GUIDE.md | docs/planning/EPIC_3/SPRINT_16/ |
| 6 | LEXER_ERROR_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 7 | PATH_ERROR_ANALYSIS.md | docs/planning/EPIC_3/SPRINT_16/ |
| 8 | (Updates to REPORT_DESIGN.md) | docs/planning/EPIC_3/SPRINT_16/ |
| 9 | SPRINT_15_REVIEW.md | docs/planning/EPIC_3/SPRINT_16/ |
| 10 | SPRINT_SCHEDULE.md | docs/planning/EPIC_3/SPRINT_16/ |
