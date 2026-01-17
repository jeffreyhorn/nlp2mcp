# Sprint 16 Report Generation Design

**Created:** January 16, 2026  
**Purpose:** Design document for automated report generation infrastructure  
**Sprint 16 Priority:** 1 (Reporting Infrastructure)

---

## Executive Summary

This document defines the architecture and implementation approach for Sprint 16's automated report generation system. The system will produce consistent, reproducible reports from pipeline test results, replacing manual report creation.

**Key Decisions:**
1. **Primary Format:** Markdown with optional JSON for programmatic access
2. **Template System:** Jinja2 for flexibility and maintainability
3. **Architecture:** Modular analyzers with pluggable renderers
4. **Data Source:** `baseline_metrics.json` and `pipeline_results.json`

---

## Library Comparison

### Evaluated Libraries

| Library | Version | Pros | Cons | Best For |
|---------|---------|------|------|----------|
| **Jinja2** | 3.1.x | Template-based, powerful filters, inheritance, well-documented | Requires template files, learning curve | Complex reports with reusable structure |
| **tabulate** | 0.9.x | Simple API, multiple output formats, minimal setup | Limited to tables only, no templating | Quick table generation |
| **Rich** | 13.x | Beautiful console output, progress bars, syntax highlighting | Terminal-focused, not file-oriented | Console/interactive reports |
| **f-strings** | Built-in | No dependencies, simple, fast | Hard to maintain for complex reports, no separation of concerns | Simple one-off formatting |
| **Markdown** | 3.x | Parse/render Markdown, extensions | Primarily for parsing not generation | Markdown validation |

### Recommendation: Jinja2 + tabulate

**Primary:** Jinja2 for overall report structure and templates  
**Secondary:** tabulate for table generation within templates

**Rationale:**
1. **Separation of Concerns:** Templates separate content structure from data logic
2. **Maintainability:** Non-developers can modify report format without changing Python code
3. **Flexibility:** Jinja2 supports conditionals, loops, filters, and template inheritance
4. **Proven Pattern:** Used by Ansible, Flask, Django, and many documentation tools
5. **Minimal Dependencies:** Jinja2 is lightweight (already used by many Python projects)

**Example Integration:**
```python
from jinja2 import Environment, FileSystemLoader
from tabulate import tabulate

env = Environment(loader=FileSystemLoader('templates'))
env.filters['tabulate'] = lambda data, headers: tabulate(data, headers, tablefmt='github')

template = env.get_template('status_report.md.j2')
report = template.render(metrics=metrics_data)
```

---

## Report Architecture

### Directory Structure

```
src/nlp2mcp/
└── reporting/
    ├── __init__.py
    ├── generate_report.py      # CLI entry point
    ├── data_loader.py          # Load and validate data sources
    ├── analyzers/
    │   ├── __init__.py
    │   ├── base.py             # Base analyzer class
    │   ├── status_analyzer.py  # Overall status metrics
    │   ├── failure_analyzer.py # Error breakdown analysis
    │   └── progress_analyzer.py # Historical comparison
    ├── renderers/
    │   ├── __init__.py
    │   ├── base.py             # Base renderer class
    │   ├── markdown_renderer.py
    │   └── json_renderer.py
    └── templates/
        ├── status_report.md.j2
        ├── failure_report.md.j2
        └── partials/
            ├── header.md.j2
            ├── summary_table.md.j2
            └── error_breakdown.md.j2
```

### Component Responsibilities

#### 1. Data Loader (`data_loader.py`)
- Load `baseline_metrics.json` (aggregated metrics)
- Load `pipeline_results.json` (per-model details) if needed
- Validate schema versions
- Provide typed data classes for type safety

```python
@dataclass
class PipelineMetrics:
    schema_version: str
    baseline_date: str
    environment: Environment
    parse: StageMetrics
    translate: StageMetrics
    solve: StageMetrics
    comparison: ComparisonMetrics
    full_pipeline: FullPipelineMetrics
```

#### 2. Analyzers (`analyzers/`)
Each analyzer processes raw metrics and produces analysis-ready data.

**StatusAnalyzer:**
- Overall success rates by stage
- Model type breakdown
- Environment info
- Comparison to baseline (if historical data available)

**FailureAnalyzer:**
- Error category distribution
- Top blockers by impact
- Improvement potential calculations
- Actionable recommendations

**ProgressAnalyzer:**
- Compare current vs. previous baseline
- Calculate deltas (improved, regressed, unchanged)
- Trend analysis over multiple snapshots

#### 3. Renderers (`renderers/`)
Transform analyzed data into output format.

**MarkdownRenderer:**
- Uses Jinja2 templates
- Produces GitHub-flavored Markdown
- Supports table of contents generation

**JsonRenderer:**
- Produces machine-readable JSON
- Useful for CI integration, dashboards
- Schema-validated output

### Data Flow

```
baseline_metrics.json ──┐
                        ├──► DataLoader ──► Analyzers ──► Renderers ──► Output Files
pipeline_results.json ──┘                      │              │
                                               │              ├── GAMSLIB_STATUS.md
                                               │              ├── FAILURE_ANALYSIS.md
                                               │              └── metrics.json
                                               │
                                          Templates (Jinja2)
```

---

## Report Specifications

### GAMSLIB_STATUS.md

**Purpose:** High-level status summary for quick understanding of pipeline health.

**Target Audience:** Developers, stakeholders, CI dashboards

**Sections:**

1. **Header**
   - Generation timestamp
   - nlp2mcp version
   - Data source file

2. **Executive Summary** (5-10 lines)
   - Full pipeline success rate
   - Key bottleneck stage
   - Improvement since last baseline (if available)

3. **Pipeline Stage Summary Table**
   | Stage | Attempted | Success | Rate | vs Baseline |
   |-------|-----------|---------|------|-------------|
   
4. **Success by Model Type**
   - NLP, LP, QCP breakdown
   - Identifies which model types need most attention

5. **Top Blockers** (condensed)
   - Top 3 error categories with model counts
   - Links to FAILURE_ANALYSIS.md for details

6. **Successful Models List**
   - Models that passed full pipeline
   - Quick reference for verified working models

7. **Footer**
   - Link to detailed failure analysis
   - Link to historical progress

### FAILURE_ANALYSIS.md

**Purpose:** Detailed error breakdown for improvement planning.

**Target Audience:** Developers working on parser/translator improvements

**Sections:**

1. **Header** (same as STATUS)

2. **Error Taxonomy Overview**
   - Total error categories (47 from Sprint 15)
   - Distribution across pipeline stages

3. **Parse Failures** (detailed)
   - Error category table with counts and percentages
   - Representative error message for each category
   - Recommended fix approach
   - Estimated complexity (Low/Medium/High)

4. **Translation Failures** (detailed)
   - Same structure as parse failures
   - Links between errors and GAMS features

5. **Solve Failures** (detailed)
   - Same structure
   - Distinguish nlp2mcp bugs vs. solver limitations

6. **Improvement Roadmap Summary**
   - Priority-ordered list of fixes
   - Impact estimate (models unblocked)
   - Effort estimate

7. **Model-Level Details** (optional, toggleable)
   - Per-model status table
   - Filterable by error category

---

## Template Mockups

### status_report.md.j2

```jinja2
# GAMSLIB Pipeline Status Report

**Generated:** {{ timestamp }}  
**nlp2mcp Version:** {{ environment.nlp2mcp_version }}  
**Data Source:** {{ data_source }}

---

## Executive Summary

{{ executive_summary }}

---

## Pipeline Stage Summary

| Stage | Attempted | Success | Failure | Success Rate |
|-------|-----------|---------|---------|--------------|
{% for stage in stages %}
| {{ stage.name }} | {{ stage.attempted }} | {{ stage.success }} | {{ stage.failure }} | {{ "%.1f"|format(stage.rate * 100) }}% |
{% endfor %}
| **Full Pipeline** | {{ full_pipeline.total }} | {{ full_pipeline.success }} | {{ full_pipeline.total - full_pipeline.success }} | {{ "%.1f"|format(full_pipeline.rate * 100) }}% |

---

## Success by Model Type

| Type | Parse | Translate | Solve | Full Pipeline |
|------|-------|-----------|-------|---------------|
{% for type in model_types %}
| {{ type.name }} | {{ "%.1f"|format(type.parse_rate * 100) }}% | {{ "%.1f"|format(type.translate_rate * 100) }}% | {{ "%.1f"|format(type.solve_rate * 100) }}% | {{ type.full_success }}/{{ type.total }} |
{% endfor %}

---

## Top Blockers

| Rank | Error Category | Models Affected | Stage | Priority |
|------|----------------|-----------------|-------|----------|
{% for blocker in top_blockers[:5] %}
| {{ loop.index }} | `{{ blocker.category }}` | {{ blocker.count }} | {{ blocker.stage }} | {{ blocker.priority }} |
{% endfor %}

See [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) for detailed breakdown.

---

## Successful Models

{% if successful_models %}
The following models complete the full pipeline successfully:

{% for model in successful_models %}
- **{{ model }}**
{% endfor %}
{% else %}
No models currently pass the full pipeline.
{% endif %}

---

*Report generated by `generate_report.py`*
```

### failure_report.md.j2

```jinja2
# GAMSLIB Failure Analysis Report

**Generated:** {{ timestamp }}  
**nlp2mcp Version:** {{ environment.nlp2mcp_version }}  
**Data Source:** {{ data_source }}

---

## Error Distribution Overview

| Stage | Total Failures | Unique Error Types | Dominant Error |
|-------|----------------|--------------------| ---------------|
{% for stage in stages %}
| {{ stage.name }} | {{ stage.failures }} | {{ stage.error_types }} | {{ stage.dominant_error }} ({{ "%.1f"|format(stage.dominant_pct * 100) }}%) |
{% endfor %}

---

## Parse Failures

**Total:** {{ parse.failures }} models ({{ "%.1f"|format(parse.failure_rate * 100) }}% of attempted)

### Error Breakdown

| Category | Count | % of Failures | Fix Complexity | Recommendation |
|----------|-------|---------------|----------------|----------------|
{% for error in parse.errors %}
| `{{ error.category }}` | {{ error.count }} | {{ "%.1f"|format(error.percentage * 100) }}% | {{ error.complexity }} | {{ error.recommendation }} |
{% endfor %}

{% for error in parse.errors %}
### {{ error.category }}

**Count:** {{ error.count }} models ({{ "%.1f"|format(error.percentage * 100) }}% of parse failures)

**Representative Error:**
```
{{ error.example_message }}
```

**Root Cause:** {{ error.root_cause }}

**Recommended Fix:** {{ error.fix_approach }}

**Estimated Effort:** {{ error.effort_hours }} hours

---

{% endfor %}

## Translation Failures

**Total:** {{ translate.failures }} models ({{ "%.1f"|format(translate.failure_rate * 100) }}% of attempted)

### Error Breakdown

| Category | Count | % of Failures | Fix Complexity | Recommendation |
|----------|-------|---------------|----------------|----------------|
{% for error in translate.errors %}
| `{{ error.category }}` | {{ error.count }} | {{ "%.1f"|format(error.percentage * 100) }}% | {{ error.complexity }} | {{ error.recommendation }} |
{% endfor %}

---

## Solve Failures

**Total:** {{ solve.failures }} models ({{ "%.1f"|format(solve.failure_rate * 100) }}% of attempted)

### Error Breakdown

| Category | Count | % of Failures | Fix Complexity | Recommendation |
|----------|-------|---------------|----------------|----------------|
{% for error in solve.errors %}
| `{{ error.category }}` | {{ error.count }} | {{ "%.1f"|format(error.percentage * 100) }}% | {{ error.complexity }} | {{ error.recommendation }} |
{% endfor %}

---

## Improvement Roadmap

Based on impact analysis, prioritized fixes:

| Priority | Error Category | Models Unblocked | Effort | ROI Score |
|----------|----------------|------------------|--------|-----------|
{% for item in roadmap %}
| {{ item.priority }} | `{{ item.category }}` | {{ item.models }} | {{ item.effort }} | {{ "%.1f"|format(item.roi) }} |
{% endfor %}

---

*Report generated by `generate_report.py`*
```

---

## Metrics for GAMSLIB_STATUS.md

### Required Metrics (Priority Order)

1. **Pipeline Summary**
   - Total models in corpus
   - Full pipeline success count and rate
   - Per-stage success rates

2. **Stage Breakdown**
   - Attempted, success, failure counts
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
   - nlp2mcp version
   - GAMS version
   - PATH solver version
   - Generation timestamp

6. **Historical Comparison** (when available)
   - Delta vs. previous baseline
   - Trend indicators (↑ improved, ↓ regressed, → unchanged)

### Metric Ordering Rationale

1. **Most Important First:** Full pipeline success is the ultimate metric
2. **Drill-Down Pattern:** Summary → Stage → Type → Error details
3. **Actionable Last:** Improvement recommendations follow diagnosis

---

## Failure Grouping Strategy

### Recommended Approach: Two-Level Hierarchy

**Level 1: Pipeline Stage**
- Parse, Translate, Solve, Compare
- Provides immediate context for where issues occur

**Level 2: Error Category**
- Use existing 47-category taxonomy from Sprint 15
- Group by specific error type (e.g., `lexer_invalid_char`, `model_no_objective_def`)

### Grouping Rules

1. **Show All Categories:** Don't hide low-count errors (may become important after fixes)
2. **Sort by Count:** Highest-impact errors first
3. **Include Percentages:** Both % of stage failures and % of total models
4. **Representative Examples:** One sample error message per category
5. **Actionable Labels:** Include fix complexity and recommendation

### Example Grouping Output

```
## Parse Failures (126 models, 78.8% of total)

### lexer_invalid_char (109 models, 86.5% of parse failures)
- Primary cause: Dollar control options ($ontext, $include)
- Fix complexity: Medium
- Recommendation: Implement lexer mode for region skipping

### internal_error (17 models, 13.5% of parse failures)  
- Primary cause: Grammar edge cases
- Fix complexity: High (requires investigation)
- Recommendation: Analyze after dollar control fixes
```

---

## Implementation Plan

### Sprint 16 Implementation Timeline

| Day | Task | Hours | Deliverable |
|-----|------|-------|-------------|
| 1 | Set up reporting module structure | 2 | `src/nlp2mcp/reporting/` skeleton |
| 1 | Implement DataLoader | 2 | Load and validate baseline_metrics.json |
| 2 | Implement StatusAnalyzer | 2 | Status metrics extraction |
| 2 | Implement FailureAnalyzer | 2 | Error breakdown logic |
| 3 | Create Jinja2 templates | 3 | status_report.md.j2, failure_report.md.j2 |
| 3 | Implement MarkdownRenderer | 2 | Render templates to files |
| 4 | Implement CLI entry point | 1 | `generate_report.py` with argparse |
| 4 | Add JSON output option | 1 | JsonRenderer for CI integration |
| 4 | Testing and refinement | 2 | Unit tests, integration tests |

**Total Estimated Time:** 17 hours

### Dependencies to Add

```toml
# pyproject.toml
[project.dependencies]
jinja2 = ">=3.1.0"
tabulate = ">=0.9.0"
```

### CLI Interface

```bash
# Generate all reports
python -m nlp2mcp.reporting.generate_report

# Generate specific report
python -m nlp2mcp.reporting.generate_report --report status
python -m nlp2mcp.reporting.generate_report --report failure

# Output formats
python -m nlp2mcp.reporting.generate_report --format markdown  # default
python -m nlp2mcp.reporting.generate_report --format json

# Custom data source
python -m nlp2mcp.reporting.generate_report --data path/to/metrics.json

# Output directory
python -m nlp2mcp.reporting.generate_report --output docs/reports/
```

---

## Unknown Verification Summary

### Unknown 1.1: Report Output Formats
**Decision:** Markdown (primary) + JSON (secondary)

**Rationale:**
- Markdown is human-readable, renders on GitHub, familiar to developers
- JSON enables CI integration, dashboards, programmatic analysis
- HTML deferred (can generate from Markdown if needed later)

### Unknown 1.2: Metrics for GAMSLIB_STATUS.md
**Decision:** See "Metrics for GAMSLIB_STATUS.md" section above

**Key Metrics:**
1. Full pipeline success rate (headline metric)
2. Per-stage success rates with counts
3. Model type breakdown
4. Top 5 blockers
5. Successful model list
6. Environment/version info

### Unknown 1.3: Template System vs String Formatting
**Decision:** Jinja2 templates

**Rationale:**
- Separation of concerns (templates vs. logic)
- Easier maintenance and modification
- Supports complex conditional logic
- Industry standard for report generation
- tabulate for table formatting within templates

### Unknown 2.1: Failure Grouping Granularity
**Decision:** Two-level hierarchy (Stage → Error Category)

**Rationale:**
- Stage grouping provides immediate context
- Full 47-category taxonomy preserved for actionability
- Sort by count for impact visibility
- Include all categories (no threshold cutoff)
- Representative examples aid debugging

---

## Appendix: Existing Report Analysis

### SPRINT_BASELINE.md Structure

1. Header with metadata (version, date, models)
2. Executive Summary table
3. Per-stage sections with:
   - Success rate table
   - Timing statistics table
   - Success by model type table
   - Error distribution table
   - Analysis paragraph
4. Comparison stage details
5. Full pipeline success details
6. Key findings summary

**Patterns to Preserve:**
- Clear section headers with `---` separators
- Consistent table formatting (GitHub-flavored Markdown)
- Analysis paragraphs after data tables
- Metric tables before narrative

### GAMSLIB_TESTING.md Structure

1. Prerequisites section
2. Quick start examples
3. Detailed script documentation
4. Output examples

**Not Applicable to Status Reports:** This is a user guide, not a status report.

---

## Conclusion

The proposed architecture provides:
- **Modularity:** Easy to add new analyzers or renderers
- **Maintainability:** Templates separate from logic
- **Extensibility:** JSON output enables future integrations
- **Consistency:** Automated generation ensures uniform reports
- **Efficiency:** 17 hours estimated implementation time

Sprint 16 should proceed with Jinja2 + tabulate approach, implementing the core status and failure reports first, with progress tracking as a follow-on enhancement.
