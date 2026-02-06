# Sprint 18 Schema Design: Corpus Reclassification

**Created:** February 6, 2026
**Status:** DRAFT - Pending Review
**Task:** Task 8 of PREP_PLAN.md
**Author:** Development Team

---

## Overview

This document specifies the schema changes required for Sprint 18 corpus reclassification. Based on findings from Tasks 2-7, the primary need is tracking GAMS syntax validation results. The originally anticipated exclusion categories (`excluded_infeasible`, `excluded_unbounded`) are **not needed** per Task 7 findings.

**Key Findings from Prep Tasks:**
- Task 2 (CORPUS_SURVEY.md): All 160 models compile successfully with GAMS - zero syntax errors found
- Task 7 (KNOWN_UNKNOWNS.md Unknown 1.4, 1.5): Both `model_infeasible` models (circle, house) are MCP formulation bugs, not inherently infeasible NLPs
- No unbounded models found in corpus

**Design Goals:**
1. Track GAMS syntax validation results per model
2. Support future exclusion if syntax errors are discovered
3. Enable metrics recalculation with reduced valid corpus
4. Minimize changes to existing reporting infrastructure

---

## Table of Contents

1. [Schema Changes](#schema-changes)
2. [JSON Examples](#json-examples)
3. [Metrics Recalculation Rules](#metrics-recalculation-rules)
4. [Reporting Script Impact Analysis](#reporting-script-impact-analysis)
5. [Migration Strategy](#migration-strategy)
6. [Implementation Checklist](#implementation-checklist)

---

## Schema Changes

### 1. New Field: `gams_syntax`

**Location:** `model_entry` (same level as `nlp2mcp_parse`, `mcp_solve`, etc.)

**Purpose:** Record results of GAMS `action=c` syntax validation

**Schema Definition:**

```json
"gams_syntax": {
  "type": "object",
  "description": "Results from GAMS syntax validation (gams action=c)",
  "required": ["status"],
  "additionalProperties": false,
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "failure", "not_tested"],
      "description": "Syntax validation status (success=compiles, failure=syntax error)"
    },
    "validation_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when validation was performed"
    },
    "gams_version": {
      "type": "string",
      "description": "GAMS version used for validation (e.g., '51.3.0')"
    },
    "validation_time_seconds": {
      "type": "number",
      "minimum": 0,
      "description": "Time to run gams action=c in seconds"
    },
    "exit_code": {
      "type": "integer",
      "description": "GAMS exit code (0=success, 2=compilation error)"
    },
    "error_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of errors reported in .lst file (0 if valid)"
    },
    "warning_count": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of warnings reported in .lst file"
    },
    "errors": {
      "type": "array",
      "description": "Array of error details (only present when status='failure')",
      "items": {
        "type": "object",
        "required": ["code", "message", "line"],
        "additionalProperties": false,
        "properties": {
          "code": {
            "type": "integer",
            "description": "GAMS error code (e.g., 140, 148)"
          },
          "message": {
            "type": "string",
            "description": "Error message text"
          },
          "line": {
            "type": "integer",
            "minimum": 1,
            "description": "Line number in source file"
          }
        }
      }
    }
  },
  "if": {
    "properties": { "status": { "const": "failure" } }
  },
  "then": {
    "required": ["status", "errors", "error_count"]
  },
  "else": {
    "not": { "required": ["errors"] }
  }
}
```

### 2. New Field: `exclusion`

**Location:** `model_entry` (top level, alongside `model_id`)

**Purpose:** Mark models as excluded from valid corpus with reason tracking

**Design Decision:** Per Task 7 findings (Unknown 1.5), only `syntax_error` exclusion reason is currently needed. However, the schema supports extensibility for future categories.

**Schema Definition:**

```json
"exclusion": {
  "type": "object",
  "description": "Exclusion status and reason for corpus reclassification",
  "required": ["excluded"],
  "additionalProperties": false,
  "properties": {
    "excluded": {
      "type": "boolean",
      "description": "True if model is excluded from valid corpus"
    },
    "reason": {
      "type": "string",
      "enum": ["syntax_error", "data_dependency", "license_restricted", "other"],
      "description": "Reason for exclusion (required if excluded=true)"
    },
    "exclusion_date": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when model was excluded"
    },
    "details": {
      "type": "string",
      "description": "Human-readable explanation of exclusion (required if reason='other')"
    },
    "reversible": {
      "type": "boolean",
      "default": true,
      "description": "True if exclusion can be reversed (e.g., GAMS team fixes syntax)"
    }
  },
  "if": {
    "properties": { "excluded": { "const": true } }
  },
  "then": {
    "required": ["excluded", "reason"]
  },
  "else": {
    "properties": {
      "reason": false,
      "exclusion_date": false,
      "details": false
    }
  },
  "allOf": [
    {
      "if": {
        "properties": { "reason": { "const": "other" } }
      },
      "then": {
        "required": ["details"]
      }
    }
  ]
}
```

**Exclusion Reason Definitions:**

| Reason | Definition | Current Count |
|--------|------------|---------------|
| `syntax_error` | Model has GAMS-level compilation errors (fails `gams action=c`) | 0 |
| `data_dependency` | Model requires external data files or runtime dependencies | Reserved |
| `license_restricted` | Model requires licensed features not available in test environment | Reserved |
| `other` | Other exclusion reason (requires details field) | Reserved |

**Note:** `infeasible` and `unbounded` exclusion reasons are intentionally NOT included per Task 7 findings. Models with `model_infeasible` or `model_unbounded` MCP results remain in the valid corpus as bugs to fix.

### 3. Schema Version Bump

**Change:** `schema_version` from `"2.0.0"` to `"2.1.0"`

**Justification:** Adding optional fields (`gams_syntax`, `exclusion`) is a minor (backward-compatible) change. Existing tools that don't recognize these fields will ignore them.

---

## JSON Examples

### Example 1: Model with Valid GAMS Syntax (Typical Case)

```json
{
  "model_id": "himmel11",
  "model_name": "Chemical Equilibrium Problem",
  "gamslib_type": "NLP",
  "gams_syntax": {
    "status": "success",
    "validation_date": "2026-02-06T10:30:00Z",
    "gams_version": "51.3.0",
    "validation_time_seconds": 0.15,
    "exit_code": 0,
    "error_count": 0,
    "warning_count": 0
  },
  "nlp2mcp_parse": {
    "status": "success",
    "...": "..."
  }
}
```

### Example 2: Model with GAMS Syntax Error (Hypothetical)

```json
{
  "model_id": "hypothetical_model",
  "model_name": "Example Model with Syntax Error",
  "gamslib_type": "NLP",
  "gams_syntax": {
    "status": "failure",
    "validation_date": "2026-02-06T10:30:00Z",
    "gams_version": "51.3.0",
    "validation_time_seconds": 0.12,
    "exit_code": 2,
    "error_count": 1,
    "warning_count": 0,
    "errors": [
      {
        "code": 148,
        "message": "Dimension different",
        "line": 45
      }
    ]
  },
  "exclusion": {
    "excluded": true,
    "reason": "syntax_error",
    "exclusion_date": "2026-02-06T10:30:00Z",
    "details": "GAMS compilation error: Dimension different (line 45)",
    "reversible": true
  },
  "nlp2mcp_parse": {
    "status": "not_tested"
  }
}
```

### Example 3: Model NOT Excluded (MCP Infeasible but NLP Feasible)

Per Task 7 findings, models like `circle` and `house` remain in the valid corpus:

```json
{
  "model_id": "circle",
  "model_name": "Smallest Circle Problem",
  "gamslib_type": "NLP",
  "gams_syntax": {
    "status": "success",
    "validation_date": "2026-02-06T10:30:00Z",
    "gams_version": "51.3.0",
    "exit_code": 0,
    "error_count": 0,
    "warning_count": 0
  },
  "mcp_solve": {
    "status": "failure",
    "outcome_category": "model_infeasible",
    "model_status": 5,
    "model_status_text": "Locally Infeasible"
  },
  "notes": "MCP infeasibility is a formulation bug - original NLP solves optimally. See KNOWN_UNKNOWNS.md Unknown 1.4."
}
```

**Key Point:** No `exclusion` field is present because the model is NOT excluded. The `model_infeasible` outcome is tracked in `mcp_solve.outcome_category` for debugging purposes, but the model remains in the valid corpus denominator.

### Example 4: Model Not Yet Tested

```json
{
  "model_id": "newmodel",
  "model_name": "New Model",
  "gamslib_type": "NLP",
  "gams_syntax": {
    "status": "not_tested"
  },
  "nlp2mcp_parse": {
    "status": "not_tested"
  }
}
```

---

## Metrics Recalculation Rules

### Current Metrics (v1.1.0 Baseline)

| Metric | Formula | v1.1.0 Value |
|--------|---------|--------------|
| Parse Rate | parse_success / total_models | 61/160 = 38.1% |
| Translate Rate | translate_success / parse_success | 42/61 = 68.9% |
| Solve Rate | solve_success / translate_success | 12/42 = 28.6% |
| Full Pipeline | full_success / total_models | 12/160 = 7.5% |

### Proposed Metrics with Valid Corpus

**Definition:** `valid_corpus = total_models - excluded_count`

| Metric | New Formula | With 0 Excluded | With 5 Excluded (Hypothetical) |
|--------|-------------|-----------------|-------------------------------|
| Parse Rate | parse_success / valid_corpus | 61/160 = 38.1% | 61/155 = 39.4% |
| Translate Rate | translate_success / parse_success | 42/61 = 68.9% | 42/61 = 68.9% |
| Solve Rate | solve_success / translate_success | 12/42 = 28.6% | 12/42 = 28.6% |
| Full Pipeline | full_success / valid_corpus | 12/160 = 7.5% | 12/155 = 7.7% |

**Key Rules:**

1. **Parse Rate and Full Pipeline** use `valid_corpus` as denominator
2. **Translate Rate** uses `parse_success` as denominator (unchanged)
3. **Solve Rate** uses `translate_success` as denominator (unchanged)
4. **Excluded models** are never counted in success numerators (they didn't reach the stage)

### Backward Compatibility

**Recommendation:** Track both metrics for transparency during transition:

```json
{
  "metrics": {
    "total_corpus": 160,
    "valid_corpus": 160,
    "excluded_count": 0,
    "parse": {
      "rate_vs_total": 0.381,
      "rate_vs_valid": 0.381
    },
    "full_pipeline": {
      "rate_vs_total": 0.075,
      "rate_vs_valid": 0.075
    }
  }
}
```

### Historical Baseline Handling

**Decision:** Do NOT retroactively recalculate v1.1.0 baseline.

**Rationale:**
1. No models are currently excluded (Task 2 found 0 syntax errors)
2. Retroactive changes would break historical comparisons
3. If exclusions are added later, document the denominator change clearly

**Documentation Format:**
```
Sprint 18 Results:
- Parse: 65/160 (40.6%) [valid corpus = 160, excluded = 0]
- Note: Metrics use valid corpus. See SCHEMA_DESIGN.md for definition.
```

---

## Reporting Script Impact Analysis

### Files Analyzed

| File | Primary Function | Changes Needed |
|------|------------------|----------------|
| `src/reporting/data_loader.py` | Loads `baseline_metrics.json` | None (uses aggregate file) |
| `src/reporting/analyzers/status_analyzer.py` | Calculates status summaries | Minor (add valid_corpus support) |
| `src/reporting/analyzers/failure_analyzer.py` | Analyzes failure categories | None |
| `src/reporting/analyzers/progress_analyzer.py` | Sprint comparison | Minor (handle denominator change) |
| `src/reporting/generate_report.py` | CLI entry point | None |
| `src/reporting/renderers/markdown_renderer.py` | Renders markdown reports | Minor (display valid_corpus) |

### Detailed Analysis

#### `data_loader.py`

**Current Behavior:** Loads from `baseline_metrics.json`, not `gamslib_status.json`

**Impact:** None for Sprint 18. The `baseline_metrics.json` is manually curated and already contains `total_models`. Adding `valid_corpus` and `excluded_count` fields to this file is trivial.

**Future Consideration:** If we want automatic exclusion filtering from `gamslib_status.json`, we'd need to add a loader function that:
1. Reads `gamslib_status.json`
2. Filters out models where `exclusion.excluded == true`
3. Recalculates aggregate metrics

This is out of scope for Sprint 18 since no models are excluded.

#### `status_analyzer.py`

**Current Code:**
```python
@dataclass
class StatusSummary:
    parse_rate: float
    translate_rate: float
    solve_rate: float
    pipeline_rate: float
    # ...
```

**Proposed Change:** Add `valid_corpus` and `excluded_count` to `StatusSummary`:
```python
@dataclass
class StatusSummary:
    total_models: int
    valid_corpus: int
    excluded_count: int
    parse_rate: float  # now: parse_success / valid_corpus
    # ...
```

**Effort:** 1-2 hours (Sprint 18 implementation, if any exclusions are added)

#### `progress_analyzer.py`

**Current Behavior:** Compares rates between sprints

**Impact:** If denominator changes between sprints (e.g., Sprint 17 used 160, Sprint 18 uses 155), the comparison needs to note this. Otherwise, a "regression" could be flagged when the rate actually improved.

**Proposed Change:** Add `denominator_note` to comparison output:
```python
@dataclass
class ComparisonSummary:
    # ...
    denominator_changed: bool
    denominator_note: Optional[str]  # e.g., "Sprint 18 uses valid_corpus=155 (5 excluded)"
```

**Effort:** 1 hour (only needed if exclusions are added)

#### `markdown_renderer.py`

**Proposed Change:** Display valid corpus count in report header:

Current:
```markdown
## Pipeline Status Summary
- **Total Models:** 160
```

Proposed:
```markdown
## Pipeline Status Summary
- **Total Models:** 160
- **Valid Corpus:** 160 (0 excluded)
```

**Effort:** 30 minutes

### Summary: No Immediate Changes Required

Since Task 2 found 0 GAMS syntax errors, no models need to be excluded. The reporting scripts will continue to work as-is with `total_models = valid_corpus = 160`.

**Deferred Work:** If models are excluded in the future:
1. Update `baseline_metrics.json` to include `valid_corpus` and `excluded_count`
2. Update `StatusSummary` dataclass
3. Update `ComparisonSummary` for denominator change handling
4. Update markdown renderer to display exclusion information

---

## Migration Strategy

### Phase 1: Schema Update (Sprint 18)

1. **Update `schema.json`:**
   - Add `gams_syntax` definition to `definitions`
   - Add `exclusion` definition to `definitions`
   - Add both as optional properties to `model_entry`
   - Bump `schema_version` to `"2.1.0"`

2. **Update `gamslib_status.json`:**
   - Add `gams_syntax` field to all 160 models (from Task 2 survey results)
   - No `exclusion` fields needed (no models excluded)
   - Bump `schema_version` to `"2.1.0"`

### Phase 2: Validation Script (Sprint 18)

Create `test_syntax.py` to:
1. Run `gams action=c` on all models in valid corpus
2. Update `gams_syntax` field in `gamslib_status.json`
3. Flag any models that fail (add `exclusion` field)
4. Generate `SYNTAX_ERROR_REPORT.md` (expected to be empty)

### Phase 3: Reporting Updates (Deferred)

Only implement if models are excluded:
1. Update `baseline_metrics.json` format
2. Update reporting scripts to use `valid_corpus`
3. Update markdown templates

### Rollback Plan

If the schema changes cause issues:
1. `gams_syntax` and `exclusion` fields are optional
2. Existing tools will ignore unknown fields
3. Revert `schema_version` to `"2.0.0"` if needed

---

## Implementation Checklist

### Sprint 18 Required (Schema Only)

- [ ] Update `data/gamslib/schema.json`:
  - [ ] Add `gams_syntax` definition
  - [ ] Add `exclusion` definition
  - [ ] Add both to `model_entry` properties
  - [ ] Bump version to `"2.1.0"`
- [ ] Create `test_syntax.py` script:
  - [ ] Run `gams action=c` on all models
  - [ ] Parse .lst file for errors
  - [ ] Update `gamslib_status.json` with results
  - [ ] Generate `SYNTAX_ERROR_REPORT.md`
- [ ] Update `gamslib_status.json`:
  - [ ] Add `gams_syntax` field to all models
  - [ ] Bump version to `"2.1.0"`
- [ ] Documentation:
  - [ ] SCHEMA_DESIGN.md (this document)
  - [ ] Update KNOWN_UNKNOWNS.md (Unknowns 1.5, 1.6, 4.2)
  - [ ] Update CHANGELOG.md

### Deferred (Only If Exclusions Added)

- [ ] Update `baseline_metrics.json` format
- [ ] Update `StatusSummary` dataclass
- [ ] Update `ComparisonSummary` dataclass
- [ ] Update markdown renderer
- [ ] Update progress comparison logic

---

## Appendix: Schema Diff

### `schema.json` Changes

```diff
{
-  "schema_version": "2.0.0",
+  "schema_version": "2.1.0",
   ...
   "definitions": {
     "model_entry": {
       "properties": {
+        "gams_syntax": {
+          "$ref": "#/definitions/gams_syntax_result",
+          "description": "Results from GAMS syntax validation (gams action=c)"
+        },
+        "exclusion": {
+          "$ref": "#/definitions/exclusion_status",
+          "description": "Exclusion status for corpus reclassification"
+        },
         ...
       }
     },
+    "gams_syntax_result": {
+      "type": "object",
+      "description": "Results from GAMS syntax validation",
+      "required": ["status"],
+      "additionalProperties": false,
+      "properties": {
+        "status": { "type": "string", "enum": ["success", "failure", "not_tested"] },
+        "validation_date": { "type": "string", "format": "date-time" },
+        "gams_version": { "type": "string" },
+        "validation_time_seconds": { "type": "number", "minimum": 0 },
+        "exit_code": { "type": "integer" },
+        "error_count": { "type": "integer", "minimum": 0 },
+        "warning_count": { "type": "integer", "minimum": 0 },
+        "errors": {
+          "type": "array",
+          "items": {
+            "type": "object",
+            "required": ["code", "message", "line"],
+            "additionalProperties": false,
+            "properties": {
+              "code": { "type": "integer" },
+              "message": { "type": "string" },
+              "line": { "type": "integer", "minimum": 1 }
+            }
+          }
+        }
+      },
+      "if": { "properties": { "status": { "const": "failure" } } },
+      "then": { "required": ["status", "errors", "error_count"] },
+      "else": { "not": { "required": ["errors"] } }
+    },
+    "exclusion_status": {
+      "type": "object",
+      "description": "Exclusion status for corpus reclassification",
+      "required": ["excluded"],
+      "additionalProperties": false,
+      "properties": {
+        "excluded": { "type": "boolean" },
+        "reason": { "type": "string", "enum": ["syntax_error", "data_dependency", "license_restricted", "other"] },
+        "exclusion_date": { "type": "string", "format": "date-time" },
+        "details": { "type": "string" },
+        "reversible": { "type": "boolean", "default": true }
+      },
+      "if": { "properties": { "excluded": { "const": true } } },
+      "then": { "required": ["excluded", "reason"] },
+      "else": { "properties": { "reason": false, "exclusion_date": false, "details": false } },
+      "allOf": [
+        {
+          "if": { "properties": { "reason": { "const": "other" } } },
+          "then": { "required": ["details"] }
+        }
+      ]
+      }
+    }
   }
}
```

---

## Document History

- February 6, 2026: Initial creation (Task 8 of PREP_PLAN.md)
