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
|-------|----------------|--------------------|----------------|
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

---

# Progress Tracking Design

**Added:** January 19, 2026  
**Purpose:** Design schema and approach for tracking pipeline progress over time  
**Related Task:** Sprint 16 Prep Task 8

---

## Overview

Progress tracking enables:
1. **Sprint-over-sprint comparison:** Measure improvement from baseline
2. **Impact analysis:** Identify which fixes had most impact
3. **Regression detection:** Alert when success rates decrease
4. **Trend analysis:** Visualize progress over multiple sprints

---

## progress_history.json Schema

### Schema Version: 1.0.0

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Progress History",
  "description": "Schema for tracking nlp2mcp pipeline progress over time",
  "type": "object",
  "required": ["schema_version", "snapshots"],
  "properties": {
    "schema_version": {
      "type": "string",
      "description": "Schema version for forward compatibility",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "snapshots": {
      "type": "array",
      "description": "Ordered list of progress snapshots (newest first)",
      "items": { "$ref": "#/definitions/snapshot" }
    }
  },
  "definitions": {
    "snapshot": {
      "type": "object",
      "required": ["snapshot_id", "timestamp", "nlp2mcp_version", "metrics"],
      "properties": {
        "snapshot_id": {
          "type": "string",
          "description": "Unique identifier (sprint_date format)",
          "pattern": "^sprint\\d+_\\d{8}$"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp when snapshot was taken"
        },
        "nlp2mcp_version": {
          "type": "string",
          "description": "nlp2mcp version at time of snapshot"
        },
        "git_commit": {
          "type": "string",
          "description": "Git commit hash for exact reproducibility (optional - may be omitted for development snapshots with uncommitted changes)",
          "pattern": "^[0-9a-f]{40}$"
        },
        "sprint": {
          "type": "integer",
          "description": "Sprint number"
        },
        "label": {
          "type": "string",
          "description": "Human-readable label (e.g., 'Sprint 15 Baseline')"
        },
        "metrics": { "$ref": "#/definitions/metrics" },
        "model_status": { "$ref": "#/definitions/model_status" },
        "notes": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Optional notes about this snapshot"
        }
      }
    },
    "metrics": {
      "type": "object",
      "required": ["total_models", "parse", "translate", "solve", "full_pipeline"],
      "properties": {
        "total_models": { "type": "integer" },
        "parse": { "$ref": "#/definitions/stage_metrics" },
        "translate": { "$ref": "#/definitions/stage_metrics" },
        "solve": { "$ref": "#/definitions/stage_metrics" },
        "full_pipeline": {
          "type": "object",
          "properties": {
            "success": { "type": "integer" },
            "rate": { "type": "number" }
          }
        }
      }
    },
    "stage_metrics": {
      "type": "object",
      "required": ["attempted", "success", "failure", "rate"],
      "properties": {
        "attempted": { "type": "integer" },
        "success": { "type": "integer" },
        "failure": { "type": "integer" },
        "rate": { "type": "number", "minimum": 0, "maximum": 1 },
        "error_breakdown": {
          "type": "object",
          "additionalProperties": { "type": "integer" }
        }
      }
    },
    "model_status": {
      "type": "object",
      "description": "Per-model status for tracking individual progress",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "parse": { "type": "string" },
          "translate": { "type": "string" },
          "solve": { "type": "string" },
          "full_pipeline": { "type": "boolean" }
        }
      }
    }
  }
}
```

### Example progress_history.json

> **Note:** The `model_status` object in this example shows only 3 models for brevity. In practice, the actual snapshot contains all 160 models (~8KB).

```json
{
  "schema_version": "1.0.0",
  "snapshots": [
    {
      "snapshot_id": "sprint16_20260120",
      "timestamp": "2026-01-20T15:30:00+00:00",
      "nlp2mcp_version": "0.5.0",
      "git_commit": "abc123def4567890abc123def4567890abc123de",
      "sprint": 16,
      "label": "Sprint 16 - After Parser Improvements",
      "metrics": {
        "total_models": 160,
        "parse": {
          "attempted": 160,
          "success": 55,
          "failure": 105,
          "rate": 0.344,
          "error_breakdown": {
            "lexer_invalid_char": 85,
            "internal_error": 20
          }
        },
        "translate": {
          "attempted": 55,
          "success": 30,
          "failure": 25,
          "rate": 0.545
        },
        "solve": {
          "attempted": 30,
          "success": 15,
          "failure": 15,
          "rate": 0.500
        },
        "full_pipeline": {
          "success": 10,
          "rate": 0.0625
        }
      },
      "model_status": {
        "hs62": { "parse": "success", "translate": "success", "solve": "success", "full_pipeline": true },
        "trnsport": { "parse": "success", "translate": "success", "solve": "failure", "full_pipeline": false },
        "aircraft": { "parse": "lexer_invalid_char", "translate": null, "solve": null, "full_pipeline": false }
      },
      "notes": [
        "Parser improvements: keyword case handling, hyphenated elements",
        "21 additional models now parsing successfully"
      ]
    },
    {
      "snapshot_id": "sprint15_20260115",
      "timestamp": "2026-01-15T12:00:00+00:00",
      "nlp2mcp_version": "0.4.0",
      "git_commit": "def456abc7890120def456abc7890120def456ab",
      "sprint": 15,
      "label": "Sprint 15 Baseline",
      "metrics": {
        "total_models": 160,
        "parse": {
          "attempted": 160,
          "success": 34,
          "failure": 126,
          "rate": 0.213,
          "error_breakdown": {
            "lexer_invalid_char": 109,
            "internal_error": 17
          }
        },
        "translate": {
          "attempted": 34,
          "success": 17,
          "failure": 17,
          "rate": 0.500
        },
        "solve": {
          "attempted": 17,
          "success": 3,
          "failure": 14,
          "rate": 0.176
        },
        "full_pipeline": {
          "success": 1,
          "rate": 0.0063
        }
      },
      "notes": [
        "Initial baseline established",
        "Primary blocker: lexer_invalid_char (109 models)"
      ]
    }
  ]
}
```

---

## Timestamp and Versioning

### Timestamp Format

**Decision:** ISO 8601 format with timezone (`YYYY-MM-DDTHH:MM:SSZ`)

**Rationale:**
- Internationally recognized standard
- Sortable as strings
- Unambiguous timezone handling
- Native Python support via `datetime.isoformat()`

**Implementation:**
```python
from datetime import datetime, timezone

timestamp = datetime.now(timezone.utc).isoformat()
# Output: "2026-01-19T15:30:00+00:00"
```

### Version Tracking

**Tracked Versions:**
1. **Schema version:** For progress_history.json schema evolution
2. **nlp2mcp version:** From `importlib.metadata.version("nlp2mcp")`
3. **Git commit hash:** From `git rev-parse HEAD` for exact reproducibility

**Version Access:**
```python
from importlib.metadata import version
import subprocess

nlp2mcp_version = version("nlp2mcp")
git_commit = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True
).strip()
```

### Snapshot ID Convention

**Format:** `sprint{N}_{YYYYMMDD}`

**Examples:**
- `sprint15_20260115` - Sprint 15 baseline
- `sprint16_20260120` - Sprint 16 post-improvement
- `sprint16_20260118` - Sprint 16 mid-sprint checkpoint

**Rationale:**
- Human-readable
- Sortable
- Unique (one snapshot per sprint-date combination)
- Allows multiple snapshots per sprint for mid-sprint checkpoints

---

## Comparison Report Format

### PROGRESS_REPORT.md Template

```jinja2
# Pipeline Progress Report

**Generated:** {{ timestamp }}  
**Comparing:** {{ current.label }} vs {{ baseline.label }}

---

## Summary

| Metric | Baseline | Current | Change | Trend |
|--------|----------|---------|--------|-------|
| Parse Rate | {{ "%.1f"|format(baseline.parse.rate * 100) }}% | {{ "%.1f"|format(current.parse.rate * 100) }}% | {{ "%+.1f"|format((current.parse.rate - baseline.parse.rate) * 100) }}% | {{ trend_icon(current.parse.rate, baseline.parse.rate) }} |
| Translate Rate | {{ "%.1f"|format(baseline.translate.rate * 100) }}% | {{ "%.1f"|format(current.translate.rate * 100) }}% | {{ "%+.1f"|format((current.translate.rate - baseline.translate.rate) * 100) }}% | {{ trend_icon(current.translate.rate, baseline.translate.rate) }} |
| Solve Rate | {{ "%.1f"|format(baseline.solve.rate * 100) }}% | {{ "%.1f"|format(current.solve.rate * 100) }}% | {{ "%+.1f"|format((current.solve.rate - baseline.solve.rate) * 100) }}% | {{ trend_icon(current.solve.rate, baseline.solve.rate) }} |
| Full Pipeline | {{ "%.1f"|format(baseline.full_pipeline.rate * 100) }}% | {{ "%.1f"|format(current.full_pipeline.rate * 100) }}% | {{ "%+.1f"|format((current.full_pipeline.rate - baseline.full_pipeline.rate) * 100) }}% | {{ trend_icon(current.full_pipeline.rate, baseline.full_pipeline.rate) }} |

**Trend Icons:** ✅ Improved | ⚠️ Regressed | ➡️ Unchanged

---

## Stage Details

### Parse Stage

| Metric | Baseline | Current | Delta |
|--------|----------|---------|-------|
| Attempted | {{ baseline.parse.attempted }} | {{ current.parse.attempted }} | {{ current.parse.attempted - baseline.parse.attempted }} |
| Success | {{ baseline.parse.success }} | {{ current.parse.success }} | **{{ "%+d"|format(current.parse.success - baseline.parse.success) }}** |
| Failure | {{ baseline.parse.failure }} | {{ current.parse.failure }} | {{ current.parse.failure - baseline.parse.failure }} |
| Rate | {{ "%.1f"|format(baseline.parse.rate * 100) }}% | {{ "%.1f"|format(current.parse.rate * 100) }}% | **{{ "%+.1f"|format((current.parse.rate - baseline.parse.rate) * 100) }}%** |

{% if parse_changes.improved %}
**Newly Passing ({{ parse_changes.improved|length }} models):**
{% for model in parse_changes.improved[:10] %}
- {{ model }}
{% endfor %}
{% if parse_changes.improved|length > 10 %}
- ... and {{ parse_changes.improved|length - 10 }} more
{% endif %}
{% endif %}

{% if parse_changes.regressed %}
**⚠️ Regressions ({{ parse_changes.regressed|length }} models):**
{% for model in parse_changes.regressed %}
- {{ model.name }}: {{ model.previous }} → {{ model.current }}
{% endfor %}
{% endif %}

### Translate Stage

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Success | {{ baseline.translate.success }} | {{ current.translate.success }} | {{ current.translate.success - baseline.translate.success }} |
| Failure | {{ baseline.translate.failure }} | {{ current.translate.failure }} | {{ current.translate.failure - baseline.translate.failure }} |
| Rate | {{ "%.1f"|format(baseline.translate.rate * 100) }}% | {{ "%.1f"|format(current.translate.rate * 100) }}% | **{{ "%+.1f"|format((current.translate.rate - baseline.translate.rate) * 100) }}%** |

{% if translate_changes.improved %}
**Newly Passing ({{ translate_changes.improved|length }} models):**
{% for model in translate_changes.improved[:10] %}
- {{ model }}
{% endfor %}
{% if translate_changes.improved|length > 10 %}
- ... and {{ translate_changes.improved|length - 10 }} more
{% endif %}
{% endif %}

{% if translate_changes.regressed %}
**⚠️ Regressions ({{ translate_changes.regressed|length }} models):**
{% for model in translate_changes.regressed %}
- {{ model.name }}: {{ model.previous }} → {{ model.current }}
{% endfor %}
{% endif %}

### Solve Stage

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Success | {{ baseline.solve.success }} | {{ current.solve.success }} | {{ current.solve.success - baseline.solve.success }} |
| Failure | {{ baseline.solve.failure }} | {{ current.solve.failure }} | {{ current.solve.failure - baseline.solve.failure }} |
| Rate | {{ "%.1f"|format(baseline.solve.rate * 100) }}% | {{ "%.1f"|format(current.solve.rate * 100) }}% | **{{ "%+.1f"|format((current.solve.rate - baseline.solve.rate) * 100) }}%** |

{% if solve_changes.improved %}
**Newly Passing ({{ solve_changes.improved|length }} models):**
{% for model in solve_changes.improved[:10] %}
- {{ model }}
{% endfor %}
{% if solve_changes.improved|length > 10 %}
- ... and {{ solve_changes.improved|length - 10 }} more
{% endif %}
{% endif %}

{% if solve_changes.regressed %}
**⚠️ Regressions ({{ solve_changes.regressed|length }} models):**
{% for model in solve_changes.regressed %}
- {{ model.name }}: {{ model.previous }} → {{ model.current }}
{% endfor %}
{% endif %}

---

## Error Category Changes

### Parse Error Distribution

| Error Category | Baseline | Current | Change |
|----------------|----------|---------|--------|
{% for error in parse_error_changes %}
| `{{ error.category }}` | {{ error.baseline }} | {{ error.current }} | {{ "%+d"|format(error.delta) }} |
{% endfor %}

---

## Model-Level Changes

### Full Pipeline Status Changes

| Model | Baseline | Current | Notes |
|-------|----------|---------|-------|
{% for change in pipeline_changes %}
| {{ change.model }} | {{ change.baseline }} | {{ change.current }} | {{ change.notes }} |
{% endfor %}

---

*Report generated by `generate_report.py --compare`*
```

### Trend Icons Implementation

```python
def trend_icon(current: float, baseline: float, threshold: float = 0.001) -> str:
    """Return trend icon based on rate change."""
    delta = current - baseline
    if delta > threshold:
        return "✅"  # Improved
    elif delta < -threshold:
        return "⚠️"  # Regressed
    else:
        return "➡️"  # Unchanged
```

---

## Model-Level Tracking

### Purpose

Track individual model outcomes across sprints to:
1. **Identify improvements:** Which models started passing after fixes
2. **Detect regressions:** Which models stopped passing
3. **Debug issues:** Correlate model changes with code changes
4. **Validate fixes:** Confirm targeted models now succeed

### Schema

```json
{
  "model_status": {
    "hs62": {
      "parse": "success",
      "translate": "success", 
      "solve": "success",
      "full_pipeline": true
    },
    "trnsport": {
      "parse": "success",
      "translate": "success",
      "solve": "path_syntax_error",
      "full_pipeline": false
    },
    "aircraft": {
      "parse": "lexer_invalid_char",
      "translate": null,
      "solve": null,
      "full_pipeline": false
    }
  }
}
```

### Change Detection

```python
def detect_model_changes(current: dict, baseline: dict) -> dict:
    """Detect model-level changes between snapshots."""
    changes = {
        "parse": {"improved": [], "regressed": [], "unchanged": []},
        "translate": {"improved": [], "regressed": [], "unchanged": []},
        "solve": {"improved": [], "regressed": [], "unchanged": []},
        "full_pipeline": {"improved": [], "regressed": [], "unchanged": []}
    }
    
    all_models = set(current.keys()) | set(baseline.keys())
    
    for model in all_models:
        curr = current.get(model, {})
        base = baseline.get(model, {})
        
        for stage in ["parse", "translate", "solve"]:
            curr_status = curr.get(stage)
            base_status = base.get(stage)
            
            if curr_status == "success" and base_status != "success":
                changes[stage]["improved"].append(model)
            elif curr_status != "success" and base_status == "success":
                # Only count as regression if model previously existed AND was successful
                # (base_status == "success" already ensures it existed and was successful)
                changes[stage]["regressed"].append({
                    "name": model,
                    "previous": base_status,
                    "current": curr_status
                })
            else:
                changes[stage]["unchanged"].append(model)
        
        # Full pipeline
        curr_full = curr.get("full_pipeline", False)
        base_full = base.get("full_pipeline", False)
        if curr_full and not base_full:
            changes["full_pipeline"]["improved"].append(model)
        elif not curr_full and base_full:
            changes["full_pipeline"]["regressed"].append(model)
    
    return changes
```

### Storage Considerations

**Full model_status in every snapshot?**
- **Pros:** Self-contained, easy comparison
- **Cons:** Redundant data, larger file size

**Decision:** Store full model_status for each snapshot
- 160 models × ~50 bytes each = ~8KB per snapshot
- 50 snapshots = ~400KB total (acceptable)
- Simplifies comparison logic
- Enables offline analysis without needing multiple files

---

## Regression Detection

### Detection Criteria

A **regression** occurs when:
1. **Rate regression:** Success rate decreases by more than threshold
2. **Model regression:** A previously passing model now fails
3. **Error increase:** An error category count increases

### Threshold Configuration

```python
REGRESSION_THRESHOLDS = {
    # Rate-based thresholds (relative change)
    "parse_rate": 0.02,      # 2% regression triggers alert
    "translate_rate": 0.02,
    "solve_rate": 0.02,
    "full_pipeline_rate": 0.01,  # More sensitive for full pipeline
    
    # Model-based thresholds (absolute count)
    "max_model_regressions": 0,  # Any model regression is flagged
    
    # Error category thresholds
    "error_increase_threshold": 5,  # Flag if any error category increases by >5
}
```

### Detection Algorithm

```python
def detect_regressions(current: dict, baseline: dict, thresholds: dict) -> dict:
    """Detect regressions between current and baseline snapshots."""
    regressions = {
        "rate_regressions": [],
        "model_regressions": [],
        "error_increases": [],
        "has_regressions": False
    }
    
    # Check rate regressions
    for stage in ["parse", "translate", "solve"]:
        curr_rate = current["metrics"][stage]["rate"]
        base_rate = baseline["metrics"][stage]["rate"]
        threshold = thresholds.get(f"{stage}_rate", 0.02)
        
        if (base_rate - curr_rate) > threshold:
            regressions["rate_regressions"].append({
                "stage": stage,
                "baseline": base_rate,
                "current": curr_rate,
                "delta": curr_rate - base_rate,
                "threshold": threshold
            })
            regressions["has_regressions"] = True
    
    # Check full pipeline rate
    curr_full = current["metrics"]["full_pipeline"]["rate"]
    base_full = baseline["metrics"]["full_pipeline"]["rate"]
    if (base_full - curr_full) > thresholds.get("full_pipeline_rate", 0.01):
        regressions["rate_regressions"].append({
            "stage": "full_pipeline",
            "baseline": base_full,
            "current": curr_full,
            "delta": curr_full - base_full
        })
        regressions["has_regressions"] = True
    
    # Check model regressions
    model_changes = detect_model_changes(
        current.get("model_status", {}),
        baseline.get("model_status", {})
    )
    
    for stage in ["parse", "translate", "solve", "full_pipeline"]:
        regressed = model_changes[stage]["regressed"]
        # Flag regressions if count exceeds threshold (default 0 means any regression is flagged)
        if len(regressed) > thresholds.get("max_model_regressions", 0):
            regressions["model_regressions"].extend([
                {"stage": stage, **r} if isinstance(r, dict) else {"stage": stage, "model": r}
                for r in regressed
            ])
            regressions["has_regressions"] = True
    
    # Check error category increases
    for stage in ["parse", "translate", "solve"]:
        curr_errors = current["metrics"][stage].get("error_breakdown", {})
        base_errors = baseline["metrics"][stage].get("error_breakdown", {})
        
        for error, curr_count in curr_errors.items():
            base_count = base_errors.get(error, 0)
            if (curr_count - base_count) > thresholds.get("error_increase_threshold", 5):
                regressions["error_increases"].append({
                    "stage": stage,
                    "error": error,
                    "baseline": base_count,
                    "current": curr_count,
                    "delta": curr_count - base_count
                })
                regressions["has_regressions"] = True
    
    return regressions
```

### Alert Output

**Console Output:**
```
⚠️ REGRESSIONS DETECTED

Rate Regressions:
  - Parse: 21.3% → 19.5% (-1.8%) [threshold: 2.0%]

Model Regressions:
  - trnsport: parse success → lexer_invalid_char
  - hs62: solve success → path_syntax_error

Error Increases:
  - Parse/internal_error: 17 → 25 (+8) [threshold: 5]

Run with --details for full analysis.
```

**CI Integration:**
```python
def check_regressions_exit_code(regressions: dict) -> int:
    """Return exit code for CI integration."""
    if regressions["has_regressions"]:
        return 1  # Non-zero exit code fails CI
    return 0
```

### CLI Support

```bash
# Compare to previous snapshot and check for regressions
python -m nlp2mcp.reporting.generate_report --compare --check-regressions

# Compare to specific baseline
python -m nlp2mcp.reporting.generate_report --compare --baseline sprint15_20260115

# Fail CI on regression
python -m nlp2mcp.reporting.generate_report --check-regressions --fail-on-regression
```

---

## Integration with Existing Infrastructure

### Compatibility with baseline_metrics.json

The progress_history.json schema is designed to be compatible with the existing `baseline_metrics.json` format:

| baseline_metrics.json Field | progress_history.json Equivalent |
|-----------------------------|----------------------------------|
| `schema_version` | `schema_version` (different versioning) |
| `baseline_date` | `snapshots[].timestamp` |
| `sprint` | `snapshots[].sprint` |
| `environment` | Snapshot-level fields: `nlp2mcp_version` and `git_commit` |
| `total_models` | `snapshots[].metrics.total_models` |
| `parse.*` | `snapshots[].metrics.parse.*` |
| `translate.*` | `snapshots[].metrics.translate.*` |
| `solve.*` | `snapshots[].metrics.solve.*` |
| `full_pipeline.*` | `snapshots[].metrics.full_pipeline.*` |

### Conversion Utility

```python
def _parse_sprint(sprint_value) -> int:
    """
    Robustly parse a sprint identifier from baseline_metrics.json.
    
    Supports:
    - integer values (returned as-is)
    - strings like "Sprint 15" (case-insensitive)
    - strings containing just the numeric sprint, e.g. "15"
    """
    if isinstance(sprint_value, int):
        return sprint_value
    
    if isinstance(sprint_value, str):
        raw = sprint_value.strip()
        # Handle strings starting with "Sprint" (any case)
        if raw.lower().startswith("sprint"):
            parts = raw.split()
            if parts:
                candidate = parts[-1].rstrip(".,;:)")
                if candidate.isdigit():
                    return int(candidate)
        # Fallback: raw numeric string
        if raw.isdigit():
            return int(raw)
    
    raise ValueError(f"Unsupported sprint format: {sprint_value!r}")


def baseline_to_snapshot(baseline: dict, snapshot_id: str) -> dict:
    """Convert baseline_metrics.json to progress_history snapshot format."""
    baseline_date = baseline['baseline_date']
    
    # Handle both date-only (YYYY-MM-DD) and datetime strings
    if 'T' in baseline_date:
        # Already has time component - ensure timezone
        if '+' not in baseline_date and 'Z' not in baseline_date:
            timestamp = f"{baseline_date}+00:00"
        else:
            timestamp = baseline_date.replace('Z', '+00:00')
    else:
        # Date-only string - add default noon UTC time
        timestamp = f"{baseline_date}T12:00:00+00:00"
    
    return {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp,
        "nlp2mcp_version": baseline["environment"]["nlp2mcp_version"],
        "sprint": _parse_sprint(baseline.get("sprint")),
        "label": f"{baseline.get('sprint', 'Unknown')} Baseline",
        "metrics": {
            "total_models": baseline["total_models"],
            "parse": {
                "attempted": baseline["parse"]["attempted"],
                "success": baseline["parse"]["success"],
                "failure": baseline["parse"]["failure"],
                "rate": baseline["parse"]["success_rate"],
                "error_breakdown": baseline["parse"].get("error_breakdown", {})
            },
            "translate": {
                "attempted": baseline["translate"]["attempted"],
                "success": baseline["translate"]["success"],
                "failure": baseline["translate"]["failure"],
                "rate": baseline["translate"]["success_rate"],
                "error_breakdown": baseline["translate"].get("error_breakdown", {})
            },
            "solve": {
                "attempted": baseline["solve"]["attempted"],
                "success": baseline["solve"]["success"],
                "failure": baseline["solve"]["failure"],
                "rate": baseline["solve"]["success_rate"],
                "error_breakdown": baseline["solve"].get("error_breakdown", {})
            },
            "full_pipeline": {
                "success": baseline["full_pipeline"]["success"],
                "rate": baseline["full_pipeline"]["success_rate"]
            }
        },
        "notes": baseline.get("notes", [])
    }
```

---

## Unknown Verification Summary

### Unknown 1.4: How should report timestamps and versioning be handled?

**Status:** ✅ VERIFIED (Task 8)

**Decision:**
- **Timestamp format:** ISO 8601 with timezone (`YYYY-MM-DDTHH:MM:SSZ`)
- **Snapshot ID:** `sprint{N}_{YYYYMMDD}` format
- **Version tracking:** Schema version, nlp2mcp version, and git commit hash

**Rationale:**
- ISO 8601 is sortable, unambiguous, internationally recognized
- Git commit hash enables exact reproducibility
- Schema versioning enables forward compatibility

### Unknown 3.1: What schema should progress_history.json follow?

**Status:** ✅ VERIFIED (Task 8)

**Decision:** JSON Schema with:
- Top-level: `schema_version`, `snapshots` array
- Per-snapshot: `snapshot_id`, `timestamp`, `nlp2mcp_version`, `git_commit`, `metrics`, `model_status`
- Metrics: `parse`, `translate`, `solve`, `full_pipeline` with rates and error breakdowns
- Model status: Per-model outcomes for change tracking

**Storage:** ~8KB per snapshot, acceptable for JSON storage

### Unknown 3.2: How to detect and alert on regressions?

**Status:** ✅ VERIFIED (Task 8)

**Decision:**
- **Rate thresholds:** 2% for stage rates, 1% for full pipeline
- **Model regressions:** Any model regression is flagged (threshold: 0)
- **Error increases:** Flag if any error category increases by >5

**Alert mechanisms:**
- Console output with clear formatting
- Non-zero exit code for CI integration (`--fail-on-regression`)
- Detailed model-level change report
