# Failure Analysis Report Schema

**Created:** January 16, 2026  
**Purpose:** Schema and content structure for FAILURE_ANALYSIS.md report  
**Sprint 16 Priority:** 1 (Reporting Infrastructure)

---

## Executive Summary

This document defines the data schema, pattern detection rules, and report templates for the failure analysis report system. The schema enables consistent tracking of errors across sprints and supports automated improvement recommendations.

**Key Design Decisions:**
1. **Error Examples:** Include one representative error message per category
2. **Recommendations:** Semi-automated using pattern-to-recommendation mapping
3. **Prioritization:** Impact × Fixability / Effort scoring formula
4. **Progress Tracking:** Sprint-over-sprint delta comparison

---

## Table of Contents

1. [Failure Analysis Data Schema](#failure-analysis-data-schema)
2. [Pattern Detection Rules](#pattern-detection-rules)
3. [Error Message Examples](#error-message-examples)
4. [Improvement Recommendation System](#improvement-recommendation-system)
5. [Prioritization Formula](#prioritization-formula)
6. [Progress Tracking Schema](#progress-tracking-schema)
7. [Report Template Structure](#report-template-structure)
8. [Unknown Verification Summary](#unknown-verification-summary)

---

## Failure Analysis Data Schema

### JSON Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "FailureAnalysis",
  "type": "object",
  "required": ["schema_version", "generated_at", "baseline_ref", "stages"],
  "properties": {
    "schema_version": {
      "type": "string",
      "description": "Schema version for backwards compatibility",
      "example": "1.0.0"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Report generation timestamp"
    },
    "baseline_ref": {
      "type": "string",
      "description": "Reference to baseline_metrics.json used",
      "example": "data/gamslib/baseline_metrics.json"
    },
    "environment": {
      "$ref": "#/definitions/Environment"
    },
    "summary": {
      "$ref": "#/definitions/FailureSummary"
    },
    "stages": {
      "type": "object",
      "properties": {
        "parse": { "$ref": "#/definitions/StageFailures" },
        "translate": { "$ref": "#/definitions/StageFailures" },
        "solve": { "$ref": "#/definitions/StageFailures" }
      }
    },
    "roadmap": {
      "type": "array",
      "items": { "$ref": "#/definitions/ImprovementItem" }
    },
    "comparison": {
      "$ref": "#/definitions/SprintComparison"
    }
  },
  "definitions": {
    "Environment": {
      "type": "object",
      "properties": {
        "nlp2mcp_version": { "type": "string" },
        "gams_version": { "type": "string" },
        "python_version": { "type": "string" }
      }
    },
    "FailureSummary": {
      "type": "object",
      "properties": {
        "total_models": { "type": "integer" },
        "total_failures": { "type": "integer" },
        "unique_error_types": { "type": "integer" },
        "dominant_stage": { "type": "string" },
        "dominant_error": { "type": "string" }
      }
    },
    "StageFailures": {
      "type": "object",
      "required": ["attempted", "failures", "error_categories"],
      "properties": {
        "attempted": { "type": "integer" },
        "failures": { "type": "integer" },
        "failure_rate": { "type": "number" },
        "error_categories": {
          "type": "array",
          "items": { "$ref": "#/definitions/ErrorCategory" }
        }
      }
    },
    "ErrorCategory": {
      "type": "object",
      "required": ["name", "count", "percentage"],
      "properties": {
        "name": {
          "type": "string",
          "description": "Error category identifier (e.g., lexer_invalid_char)"
        },
        "count": {
          "type": "integer",
          "description": "Number of models with this error"
        },
        "percentage": {
          "type": "number",
          "description": "Percentage of stage failures"
        },
        "percentage_of_total": {
          "type": "number",
          "description": "Percentage of all models"
        },
        "subcategories": {
          "type": "array",
          "items": { "$ref": "#/definitions/ErrorSubcategory" }
        },
        "example_error": {
          "$ref": "#/definitions/ErrorExample"
        },
        "recommendation": {
          "$ref": "#/definitions/Recommendation"
        },
        "affected_models": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of model names affected"
        }
      }
    },
    "ErrorSubcategory": {
      "type": "object",
      "properties": {
        "pattern_name": {
          "type": "string",
          "description": "Subcategory identifier (e.g., dollar_control)"
        },
        "pattern_regex": {
          "type": "string",
          "description": "Regex used for detection"
        },
        "count": { "type": "integer" },
        "percentage": { "type": "number" },
        "models": {
          "type": "array",
          "items": { "type": "string" }
        },
        "fixable": { "type": "boolean" },
        "fix_complexity": {
          "type": "string",
          "enum": ["low", "medium", "high", "n/a"]
        }
      }
    },
    "ErrorExample": {
      "type": "object",
      "properties": {
        "model": {
          "type": "string",
          "description": "Model name where error occurred"
        },
        "message": {
          "type": "string",
          "description": "Truncated error message (max 200 chars)"
        },
        "context": {
          "type": "string",
          "description": "Source code context if available"
        },
        "line": {
          "type": "integer",
          "description": "Line number if available"
        }
      }
    },
    "Recommendation": {
      "type": "object",
      "properties": {
        "action": {
          "type": "string",
          "description": "Recommended fix action"
        },
        "complexity": {
          "type": "string",
          "enum": ["low", "medium", "high"]
        },
        "effort_hours": {
          "type": "number",
          "description": "Estimated hours to implement"
        },
        "sprint_target": {
          "type": "string",
          "description": "Target sprint for fix (e.g., Sprint 16, Sprint 17, Deferred)"
        },
        "auto_generated": {
          "type": "boolean",
          "description": "Whether recommendation was auto-generated"
        }
      }
    },
    "ImprovementItem": {
      "type": "object",
      "required": ["rank", "error_category", "priority_score"],
      "properties": {
        "rank": { "type": "integer" },
        "error_category": { "type": "string" },
        "stage": { "type": "string" },
        "models_affected": { "type": "integer" },
        "fix_complexity": { "type": "string" },
        "effort_hours": { "type": "number" },
        "priority_score": { "type": "number" },
        "sprint_target": { "type": "string" },
        "status": {
          "type": "string",
          "enum": ["not_started", "in_progress", "completed", "deferred"]
        }
      }
    },
    "SprintComparison": {
      "type": "object",
      "properties": {
        "previous_sprint": { "type": "string" },
        "current_sprint": { "type": "string" },
        "comparison_date": { "type": "string", "format": "date" },
        "parse_delta": { "$ref": "#/definitions/StageDelta" },
        "translate_delta": { "$ref": "#/definitions/StageDelta" },
        "solve_delta": { "$ref": "#/definitions/StageDelta" },
        "newly_passing": {
          "type": "object",
          "properties": {
            "parse": { "type": "array", "items": { "type": "string" } },
            "translate": { "type": "array", "items": { "type": "string" } },
            "solve": { "type": "array", "items": { "type": "string" } }
          }
        },
        "newly_failing": {
          "type": "object",
          "properties": {
            "parse": { "type": "array", "items": { "type": "string" } },
            "translate": { "type": "array", "items": { "type": "string" } },
            "solve": { "type": "array", "items": { "type": "string" } }
          }
        },
        "error_changes": {
          "type": "array",
          "items": { "$ref": "#/definitions/ErrorChange" }
        }
      }
    },
    "ErrorChange": {
      "type": "object",
      "properties": {
        "category": { "type": "string" },
        "previous_count": { "type": "integer" },
        "current_count": { "type": "integer" },
        "delta": { "type": "integer" },
        "note": { "type": "string" }
      }
    },
    "StageDelta": {
      "type": "object",
      "properties": {
        "previous_success": { "type": "integer" },
        "current_success": { "type": "integer" },
        "previous_rate": { "type": "number" },
        "current_rate": { "type": "number" },
        "delta": { "type": "number" },
        "delta_models": { "type": "integer" },
        "trend": {
          "type": "string",
          "enum": ["improved", "regressed", "unchanged"]
        }
      }
    }
  }
}
```

### YAML Example Instance

```yaml
schema_version: "1.0.0"
generated_at: "2026-01-16T10:30:00Z"
baseline_ref: "data/gamslib/baseline_metrics.json"

environment:
  nlp2mcp_version: "0.1.0"
  gams_version: "51.3.0"
  python_version: "3.12.8"

summary:
  total_models: 160
  total_failures: 157
  unique_error_types: 9
  dominant_stage: "parse"
  dominant_error: "lexer_invalid_char"

stages:
  parse:
    attempted: 160
    failures: 126
    failure_rate: 0.788
    error_categories:
      - name: "lexer_invalid_char"
        count: 109
        percentage: 86.5
        percentage_of_total: 68.1
        subcategories:
          - pattern_name: "dollar_control"
            pattern_regex: "\\$[a-zA-Z]+"
            count: 87
            percentage: 79.8
            fixable: true
            fix_complexity: "medium"
          - pattern_name: "embedded_code"
            pattern_regex: "\\$(call|execute)"
            count: 12
            percentage: 11.0
            fixable: false
            fix_complexity: "n/a"
          - pattern_name: "special_chars"
            pattern_regex: "[^\\x00-\\x7F]"
            count: 10
            percentage: 9.2
            fixable: true
            fix_complexity: "low"
        example_error:
          model: "aircraft"
          message: "Unexpected character '$' at line 15, column 1"
          context: "$ontext\nThis is a comment block..."
          line: 15
        recommendation:
          action: "Implement lexer mode for dollar control region skipping"
          complexity: "medium"
          effort_hours: 8
          sprint_target: "Sprint 16"
          auto_generated: true
        affected_models:
          - "aircraft"
          - "blend"
          - "chemical"
          # ... truncated

      - name: "internal_error"
        count: 17
        percentage: 13.5
        percentage_of_total: 10.6
        example_error:
          model: "ramsey"
          message: "Parser internal error: unexpected token IDENTIFIER"
          line: 42
        recommendation:
          action: "Investigate grammar edge cases after dollar control fixes"
          complexity: "high"
          effort_hours: 12
          sprint_target: "Sprint 17"
          auto_generated: true

  translate:
    attempted: 34
    failures: 17
    failure_rate: 0.5
    error_categories:
      - name: "model_no_objective_def"
        count: 5
        percentage: 29.4
        percentage_of_total: 3.1
        example_error:
          model: "feasibility1"
          message: "Model has no objective function definition"
        recommendation:
          action: "Document as intentional limitation for feasibility models"
          complexity: "low"
          effort_hours: 1
          sprint_target: "Sprint 16"
          auto_generated: true
      # ... other translate errors

  solve:
    attempted: 17
    failures: 14
    failure_rate: 0.824
    error_categories:
      - name: "path_syntax_error"
        count: 14
        percentage: 100.0
        percentage_of_total: 8.75
        example_error:
          model: "portfolio"
          message: "PATH solver error: syntax error in MCP file at line 23"
        recommendation:
          action: "Investigate MCP generation for quoting and formatting issues"
          complexity: "medium"
          effort_hours: 6
          sprint_target: "Sprint 16"
          auto_generated: true

roadmap:
  - rank: 1
    error_category: "lexer_invalid_char"
    stage: "parse"
    models_affected: 109
    fix_complexity: "medium"
    effort_hours: 8
    priority_score: 13.63
    sprint_target: "Sprint 16"
    status: "not_started"
  - rank: 2
    error_category: "path_syntax_error"
    stage: "solve"
    models_affected: 14
    fix_complexity: "medium"
    effort_hours: 6
    priority_score: 2.33
    sprint_target: "Sprint 16"
    status: "not_started"
  # ... continued

comparison:
  previous_sprint: "Sprint 14"
  current_sprint: "Sprint 15"
  comparison_date: "2026-01-15"
  parse_delta:
    previous_success: 24
    current_success: 34
    previous_rate: 0.15
    current_rate: 0.213
    delta: 0.063
    delta_models: 10
    trend: "improved"
  translate_delta:
    previous_success: 15
    current_success: 17
    previous_rate: 0.45
    current_rate: 0.50
    delta: 0.05
    delta_models: 2
    trend: "improved"
  solve_delta:
    previous_success: 4
    current_success: 3
    previous_rate: 0.20
    current_rate: 0.176
    delta: -0.024
    delta_models: -1
    trend: "regressed"
  newly_passing:
    parse:
      - "hs62"
      - "trig"
    translate: []
    solve: []
  newly_failing:
    parse: []
    translate: []
    solve:
      - "complex_model_1"
```

---

## Pattern Detection Rules

### Lexer Error Patterns

For `lexer_invalid_char` errors, the following pattern detection rules classify subcategories:

```python
"""
Pattern detection rules for lexer_invalid_char subcategorization.
Applied to both error messages and source file content.
"""

LEXER_ERROR_PATTERNS = {
    # Dollar control options - fixable with lexer mode
    'dollar_control': {
        'regex': r'\$(?:ontext|offtext|include|batinclude|if|else|endif|setglobal|setlocal|title|eolcom|inlinecom)',
        'description': 'GAMS dollar control directives for comments and includes',
        'fixable': True,
        'fix_complexity': 'medium',
        'recommendation': 'Implement lexer mode for region skipping',
    },
    
    # Embedded execution commands - intentionally unsupported
    'embedded_code': {
        'regex': r'\$(?:call|execute|execute_loadpoint|execute_unload|gdxin|gdxout)',
        'description': 'GAMS embedded execution commands requiring runtime',
        'fixable': False,
        'fix_complexity': 'n/a',
        'recommendation': 'Document as intentional exclusion (requires GAMS runtime)',
    },
    
    # Macro syntax - potentially fixable
    'macro_syntax': {
        'regex': r'%[a-zA-Z_][a-zA-Z0-9_]*%',
        'description': 'GAMS macro variable references',
        'fixable': True,
        'fix_complexity': 'high',
        'recommendation': 'Implement macro expansion support (Sprint 17+)',
    },
    
    # Special/non-ASCII characters - easy fix
    'special_chars': {
        'regex': r'[^\x00-\x7F]',
        'description': 'Non-ASCII characters in source',
        'fixable': True,
        'fix_complexity': 'low',
        'recommendation': 'Extend lexer character class to support UTF-8',
    },
    
    # Semicolon in unexpected position
    'unexpected_semicolon': {
        'regex': r';;|;\s*;',
        'description': 'Double or malformed semicolons',
        'fixable': True,
        'fix_complexity': 'low',
        'recommendation': 'Handle empty statements in grammar',
    },
}


def classify_lexer_error(error_message: str, source_content: str | None = None) -> str:
    """
    Classify a lexer_invalid_char error into a subcategory.
    
    Args:
        error_message: The error message from the parser
        source_content: Optional source file content for context
        
    Returns:
        Subcategory name (e.g., 'dollar_control', 'special_chars')
    """
    import re
    
    # Check error message first
    for pattern_name, pattern_info in LEXER_ERROR_PATTERNS.items():
        if re.search(pattern_info['regex'], error_message, re.IGNORECASE):
            return pattern_name
    
    # Check source content if available
    if source_content:
        for pattern_name, pattern_info in LEXER_ERROR_PATTERNS.items():
            if re.search(pattern_info['regex'], source_content):
                return pattern_name
    
    # Default: unknown subcategory
    return 'unknown'
```

### Translate Error Patterns

```python
"""
Pattern detection rules for translate-stage error classification.
"""

TRANSLATE_ERROR_PATTERNS = {
    'unsupported_function': {
        'regex': r'(?:gamma|erf|erfc|sign|ceil|floor|mod|div)',
        'description': 'Mathematical functions not yet supported',
        'fixable': True,
        'fix_complexity': 'medium',
        'recommendation': 'Implement function support in differentiator',
    },
    
    'index_arithmetic': {
        'regex': r'\w+\s*\(\s*\w+\s*[+-]\s*\d+\s*\)',
        'description': 'Index expressions with +/- offsets',
        'fixable': True,
        'fix_complexity': 'high',
        'recommendation': 'Implement domain analysis for index arithmetic',
    },
    
    'domain_operation': {
        'regex': r'(?:card|ord|sum\s+\(.*,)',
        'description': 'Set/domain operations',
        'fixable': True,
        'fix_complexity': 'medium',
        'recommendation': 'Implement set operation support',
    },
}
```

### Solve Error Patterns

```python
"""
Pattern detection rules for solve-stage error classification.
"""

SOLVE_ERROR_PATTERNS = {
    'mcp_syntax': {
        'regex': r'syntax error|unexpected token',
        'description': 'Generated MCP file has syntax errors',
        'fixable': True,
        'fix_complexity': 'medium',
        'recommendation': 'Review MCP code generation for quoting and formatting',
    },
    
    'bounds_error': {
        'regex': r'bound|infeasible|unbounded',
        'description': 'Variable bounds issues',
        'fixable': True,
        'fix_complexity': 'low',
        'recommendation': 'Review bounds propagation in translator',
    },
    
    'convergence_failure': {
        'regex': r'convergence|iteration limit|no solution',
        'description': 'Solver convergence issues',
        'fixable': False,
        'fix_complexity': 'n/a',
        'recommendation': 'Document as solver limitation',
    },
}
```

---

## Error Message Examples

### Design Decision: Include Representative Examples

**Decision:** Include ONE representative error message per category

**Rationale:**
1. Helps developers understand error context without running models
2. Single example avoids report bloat
3. Message truncated to 200 chars for readability
4. Source context included when available (3 lines)

### Example Format

Each error category includes an `example_error` object:

```yaml
example_error:
  model: "aircraft"           # Model where error occurred
  message: "Unexpected..."    # Error message (max 200 chars)
  context: |                  # Source context (optional)
    $ontext
    This is a comment block
    $offtext
  line: 15                    # Line number (if available)
```

### Template Rendering

```jinja2
### {{ error.name }} ({{ error.count }} models, {{ "%.1f"|format(error.percentage) }}%)

**Representative Error:**
```
Model: {{ error.example_error.model }}
Line: {{ error.example_error.line }}
Message: {{ error.example_error.message }}
```

{% if error.example_error.context %}
**Source Context:**
```gams
{{ error.example_error.context }}
```
{% endif %}
```

---

## Improvement Recommendation System

### Design Decision: Semi-Automated Recommendations

**Decision:** Use pattern-to-recommendation mapping with manual override capability

**Approach:**
1. **Auto-generated:** Default recommendations derived from pattern detection rules
2. **Manual override:** Allow manual annotation in metadata file
3. **Flagged:** `auto_generated` field indicates source

### Recommendation Template

```yaml
recommendation:
  action: "Clear action statement"      # What to do
  complexity: "low|medium|high"         # Implementation difficulty
  effort_hours: 8                       # Estimated hours
  sprint_target: "Sprint 16"            # When to address
  auto_generated: true                  # Source indicator
```

### Recommendation Generation Logic

```python
def generate_recommendation(
    error_category: str,
    subcategory: str | None,
    models_affected: int,
    pattern_info: dict | None
) -> dict:
    """
    Generate improvement recommendation for an error category.
    
    Args:
        error_category: Error type (e.g., 'lexer_invalid_char')
        subcategory: Detected subcategory (e.g., 'dollar_control')
        models_affected: Number of models with this error
        pattern_info: Pattern detection info if available
        
    Returns:
        Recommendation dictionary
    """
    # Default recommendations by error category
    DEFAULT_RECOMMENDATIONS = {
        'lexer_invalid_char': {
            'action': 'Extend lexer to handle additional syntax',
            'complexity': 'medium',
            'effort_hours': 8,
            'sprint_target': 'Sprint 16',
        },
        'internal_error': {
            'action': 'Debug parser internals and fix edge cases',
            'complexity': 'high',
            'effort_hours': 12,
            'sprint_target': 'Sprint 17',
        },
        'model_no_objective_def': {
            'action': 'Document as limitation for feasibility models',
            'complexity': 'low',
            'effort_hours': 1,
            'sprint_target': 'Sprint 16',
        },
        'path_syntax_error': {
            'action': 'Review MCP generation for syntax issues',
            'complexity': 'medium',
            'effort_hours': 6,
            'sprint_target': 'Sprint 16',
        },
    }
    
    # Start with default
    recommendation = DEFAULT_RECOMMENDATIONS.get(error_category, {
        'action': 'Investigate and categorize',
        'complexity': 'unknown',
        'effort_hours': 4,
        'sprint_target': 'TBD',
    }).copy()
    
    # Override with pattern-specific recommendation if available
    if pattern_info and 'recommendation' in pattern_info:
        recommendation['action'] = pattern_info['recommendation']
        recommendation['complexity'] = pattern_info.get('fix_complexity', 'medium')
    
    # Adjust sprint target based on complexity and impact
    if models_affected > 50 and recommendation['complexity'] != 'high':
        recommendation['sprint_target'] = 'Sprint 16'  # High impact, prioritize
    elif recommendation['complexity'] == 'high':
        recommendation['sprint_target'] = 'Sprint 17'  # Complex, defer
    
    recommendation['auto_generated'] = True
    return recommendation
```

---

## Prioritization Formula

### Priority Score Calculation

**Formula:** `Priority Score = Models Affected / Effort Hours` (only for fixable errors)

Where:
- `Models Affected`: Number of models blocked by this error
- `Effort Hours`: Estimated implementation hours
- Non-fixable errors return score of 0.0 (excluded from prioritization)

### Priority Score Implementation

```python
def calculate_priority_score(
    models_affected: int,
    fixable: bool,
    effort_hours: float,
) -> float:
    """
    Calculate improvement priority score.
    
    Args:
        models_affected: Number of models with this error
        fixable: Whether the error is fixable in nlp2mcp
        effort_hours: Estimated hours to fix
        
    Returns:
        Priority score (higher = higher priority)
    """
    # Non-fixable errors are excluded from prioritization
    if not fixable or effort_hours <= 0:
        return 0.0
    
    # Score: models per hour of effort
    score = models_affected / effort_hours
    
    return round(score, 2)


# Example priority calculation
priorities = [
    {
        'error': 'lexer_invalid_char',
        'models': 109,
        'fixable': True,
        'effort': 8,
        'score': calculate_priority_score(109, True, 8),  # 13.63
    },
    {
        'error': 'path_syntax_error',
        'models': 14,
        'fixable': True,
        'effort': 6,
        'score': calculate_priority_score(14, True, 6),  # 2.33
    },
    {
        'error': 'internal_error',
        'models': 17,
        'fixable': True,
        'effort': 12,
        'score': calculate_priority_score(17, True, 12),  # 1.42
    },
    {
        'error': 'embedded_code',
        'models': 12,
        'fixable': False,
        'effort': 0,
        'score': calculate_priority_score(12, False, 0),  # 0.0
    },
]
```

### Priority Ranking Example

| Rank | Error Category | Models | Fixable | Effort | Score | Sprint Target |
|------|----------------|--------|---------|--------|-------|---------------|
| 1 | lexer_invalid_char (dollar_control) | 87 | Yes | 8h | 10.88 | Sprint 16 |
| 2 | lexer_invalid_char (special_chars) | 10 | Yes | 2h | 5.00 | Sprint 16 |
| 3 | path_syntax_error | 14 | Yes | 6h | 2.33 | Sprint 16 |
| 4 | internal_error | 17 | Yes | 12h | 1.42 | Sprint 17 |
| 5 | model_no_objective_def | 5 | N/A | 1h | 0.00 | Document |
| 6 | lexer_invalid_char (embedded_code) | 12 | No | N/A | 0.00 | Exclude |

---

## Progress Tracking Schema

### Sprint-over-Sprint Comparison

```yaml
comparison:
  previous_sprint: "Sprint 15"
  current_sprint: "Sprint 16"
  comparison_date: "2026-01-20"
  
  # Stage-level deltas
  parse_delta:
    previous_success: 34
    current_success: 68
    previous_rate: 0.213
    current_rate: 0.425
    delta: 0.212
    delta_models: 34
    trend: "improved"
    
  translate_delta:
    previous_success: 17
    current_success: 34
    previous_rate: 0.500
    current_rate: 0.500
    delta: 0.0
    delta_models: 17
    trend: "unchanged"
    
  solve_delta:
    previous_success: 3
    current_success: 10
    previous_rate: 0.176
    current_rate: 0.294
    delta: 0.118
    delta_models: 7
    trend: "improved"

  # Model-level changes
  newly_passing:
    parse:
      - "aircraft"
      - "blend"
      - "chemical"
      # ... 31 more
    translate:
      - "hs63"
      - "hs64"
    solve:
      - "portfolio"
      
  newly_failing:
    parse: []
    translate: []
    solve:
      - "edge_case_model"  # Regression detected
      
  # Error category changes
  error_changes:
    - category: "lexer_invalid_char"
      previous_count: 109
      current_count: 22
      delta: -87
      note: "Dollar control handling implemented"
    - category: "path_syntax_error"
      previous_count: 14
      current_count: 4
      delta: -10
      note: "MCP quoting fixes"
```

### Progress Tracking Template

```jinja2
## Sprint Progress: {{ comparison.previous_sprint }} → {{ comparison.current_sprint }}

### Success Rate Changes

| Stage | Previous | Current | Delta | Trend |
|-------|----------|---------|-------|-------|
{% for stage in ['parse', 'translate', 'solve'] %}
{% set delta = comparison[stage + '_delta'] %}
| {{ stage|capitalize }} | {{ "%.1f"|format(delta.previous_rate * 100) }}% | {{ "%.1f"|format(delta.current_rate * 100) }}% | {{ "%+.1f"|format(delta.delta * 100) }}% | {{ '↑' if delta.trend == 'improved' else ('↓' if delta.trend == 'regressed' else '→') }} |
{% endfor %}

### Newly Passing Models

{% if comparison.newly_passing.parse %}
**Parse:** {{ comparison.newly_passing.parse|length }} models
{% for model in comparison.newly_passing.parse[:5] %}
- {{ model }}
{% endfor %}
{% if comparison.newly_passing.parse|length > 5 %}
- ... and {{ comparison.newly_passing.parse|length - 5 }} more
{% endif %}
{% endif %}

### Regressions

{% set has_regressions = comparison.newly_failing.parse|length + comparison.newly_failing.translate|length + comparison.newly_failing.solve|length > 0 %}
{% if has_regressions %}
⚠️ **Regressions detected:**
{% for stage, models in comparison.newly_failing.items() %}
{% for model in models %}
- {{ model }} ({{ stage }})
{% endfor %}
{% endfor %}
{% else %}
✅ No regressions detected.
{% endif %}
```

---

## Report Template Structure

### FAILURE_ANALYSIS.md Template

```jinja2
# GAMSLIB Failure Analysis Report

**Generated:** {{ timestamp }}  
**nlp2mcp Version:** {{ environment.nlp2mcp_version }}  
**Baseline:** {{ baseline_ref }}

---

## Executive Summary

- **Total Models:** {{ summary.total_models }}
- **Total Failures:** {{ summary.total_failures }} ({{ "%.1f"|format(summary.total_failures / summary.total_models * 100) }}%)
- **Unique Error Types:** {{ summary.unique_error_types }}
- **Dominant Blocker:** `{{ summary.dominant_error }}` ({{ summary.dominant_stage }} stage)

---

## Error Distribution by Stage

| Stage | Attempted | Failures | Rate | Top Error |
|-------|-----------|----------|------|-----------|
{% for stage_name, stage in stages.items() %}
| {{ stage_name|capitalize }} | {{ stage.attempted }} | {{ stage.failures }} | {{ "%.1f"|format(stage.failure_rate * 100) }}% | {{ stage.error_categories[0].name if stage.error_categories else 'N/A' }} |
{% endfor %}

---

{% for stage_name, stage in stages.items() %}
## {{ stage_name|capitalize }} Failures

**Total:** {{ stage.failures }} failures ({{ "%.1f"|format(stage.failure_rate * 100) }}% of attempted)

{% for error in stage.error_categories %}
### {{ error.name }}

| Metric | Value |
|--------|-------|
| Count | {{ error.count }} |
| % of {{ stage_name }} failures | {{ "%.1f"|format(error.percentage) }}% |
| % of all models | {{ "%.1f"|format(error.percentage_of_total) }}% |

{% if error.subcategories %}
**Subcategories:**

| Pattern | Count | Fixable | Complexity |
|---------|-------|---------|------------|
{% for sub in error.subcategories %}
| {{ sub.pattern_name }} | {{ sub.count }} | {{ '✓' if sub.fixable else '✗' }} | {{ sub.fix_complexity }} |
{% endfor %}
{% endif %}

{% if error.example_error %}
**Representative Error:**
```
Model: {{ error.example_error.model }}
{% if error.example_error.line %}Line: {{ error.example_error.line }}{% endif %}
{{ error.example_error.message }}
```
{% endif %}

{% if error.recommendation %}
**Recommendation:**
- **Action:** {{ error.recommendation.action }}
- **Complexity:** {{ error.recommendation.complexity }}
- **Effort:** {{ error.recommendation.effort_hours }} hours
- **Target:** {{ error.recommendation.sprint_target }}
{% endif %}

---

{% endfor %}
{% endfor %}

## Improvement Roadmap

| Rank | Error | Stage | Models | Effort | Score | Target | Status |
|------|-------|-------|--------|--------|-------|--------|--------|
{% for item in roadmap %}
| {{ item.rank }} | `{{ item.error_category }}` | {{ item.stage }} | {{ item.models_affected }} | {{ item.effort_hours }}h | {{ "%.2f"|format(item.priority_score) }} | {{ item.sprint_target }} | {{ item.status }} |
{% endfor %}

---

{% if comparison %}
## Progress vs Previous Sprint

{{ comparison.previous_sprint }} → {{ comparison.current_sprint }}

| Stage | Previous | Current | Delta |
|-------|----------|---------|-------|
{% for stage in ['parse', 'translate', 'solve'] %}
{% set d = comparison[stage + '_delta'] %}
| {{ stage|capitalize }} | {{ "%.1f"|format(d.previous_rate * 100) }}% | {{ "%.1f"|format(d.current_rate * 100) }}% | {{ "%+.1f"|format(d.delta * 100) }}% |
{% endfor %}

{% if comparison.newly_passing %}
### Newly Passing Models
{% for stage, models in comparison.newly_passing.items() if models %}
**{{ stage|capitalize }}:** {{ models|join(', ') }}
{% endfor %}
{% endif %}

{% endif %}

---

*Report generated by `generate_report.py`*
```

---

## Unknown Verification Summary

### Unknown 2.2: Should FAILURE_ANALYSIS.md include example error messages?

**Decision:** Yes, include ONE representative error message per category

**Rationale:**
1. Helps developers understand error context without running individual models
2. Single example per category prevents report bloat
3. Message truncated to 200 characters for readability
4. Source context included when available (up to 3 lines)
5. Line number included when available for quick navigation

**Format:**
```yaml
example_error:
  model: "aircraft"
  message: "Unexpected character '$' at line 15..."
  context: "$ontext\nComment block\n$offtext"
  line: 15
```

### Unknown 2.3: How should improvement recommendations be generated?

**Decision:** Semi-automated with pattern-to-recommendation mapping

**Approach:**
1. **Pattern Detection:** Regex patterns classify errors into subcategories
2. **Default Recommendations:** Each pattern has a default recommendation
3. **Auto-Generation:** Recommendations generated from pattern rules
4. **Manual Override:** Metadata file allows manual annotation
5. **Flagged:** `auto_generated: true/false` indicates source

**Benefits:**
- Consistent recommendations across reports
- Reduces manual effort
- Allows expert override when needed
- Traceable recommendation source

### Unknown 4.3: How should parse failures be prioritized for improvement?

**Decision:** Priority Score = Models Affected / Effort Hours (only for fixable errors)

**Formula Details:**
- `Models Affected`: Count of models blocked by this error
- `Fixability`: Boolean filter; non-fixable errors are excluded (scored as 0.0)
- `Effort Hours`: Estimated implementation time

**Example Rankings:**
| Error | Models | Fixable | Effort | Score |
|-------|--------|---------|--------|-------|
| lexer_invalid_char (dollar) | 87 | Yes | 8h | 10.88 |
| special_chars | 10 | Yes | 2h | 5.00 |
| path_syntax_error | 14 | Yes | 6h | 2.33 |
| internal_error | 17 | Yes | 12h | 1.42 |
| embedded_code | 12 | No | N/A | 0.00 |

**Rationale:**
- Simple, transparent formula
- Prioritizes high-impact, low-effort fixes
- Excludes unfixable issues automatically
- Can be extended with model type weights if needed

---

## Appendix: Error Category Reference

### Parse Stage Errors

| Category | Description | Typical Cause |
|----------|-------------|---------------|
| `lexer_invalid_char` | Unexpected character in input | Dollar control, special chars |
| `internal_error` | Parser exception | Grammar edge case |

### Translate Stage Errors

| Category | Description | Typical Cause |
|----------|-------------|---------------|
| `model_no_objective_def` | No objective function | Feasibility model |
| `diff_unsupported_func` | Unsupported math function | gamma, erf, etc. |
| `unsup_index_offset` | Index arithmetic | x(i+1) syntax |
| `model_domain_mismatch` | Domain inference failure | Complex set ops |
| `unsup_dollar_cond` | Dollar conditional | $if in expression |
| `codegen_numerical_error` | Code gen numeric issue | Overflow/precision |

### Solve Stage Errors

| Category | Description | Typical Cause |
|----------|-------------|---------------|
| `path_syntax_error` | MCP syntax error | Code gen issue |
| `solver_convergence` | No solution found | Model difficulty |
| `bounds_violation` | Infeasible bounds | Translation bug |
