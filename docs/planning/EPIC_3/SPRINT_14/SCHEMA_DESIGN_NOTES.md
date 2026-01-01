# Schema Design Notes

**Task:** Sprint 14 Prep Task 5 - Design Database Schema Draft  
**Created:** January 1, 2026  
**Schema Version:** 2.0.0 (draft)

---

## Overview

This document explains the design rationale for `DRAFT_SCHEMA.json`, the JSON Schema that will define the structure of `data/gamslib/gamslib_status.json` in Sprint 14. The schema represents a major version bump from the existing `catalog.json` (v1.0.0) to accommodate the nlp2mcp pipeline tracking requirements.

---

## Design Decisions

### 1. Schema Draft Version: Draft-07

**Decision:** Use JSON Schema Draft-07

**Rationale:**
- Consistent with Task 3 research findings
- Full support in Python jsonschema library (v4.25.1)
- Simpler syntax than Draft 2020-12 (no `prefixItems`, `$dynamicRef`)
- Adequate for all our validation needs
- Lower validator overhead (no `unevaluatedProperties` checks)

**Implementation:**
```json
"$schema": "http://json-schema.org/draft-07/schema#"
```

### 2. Structure: Moderate Nesting (2 Levels)

**Decision:** Use nested objects for pipeline stages

**Rationale:**
- Logical grouping of related fields (convexity, parse, translate, solve)
- Easy to add new fields within each stage without polluting the namespace
- Intuitive query pattern: `model["nlp2mcp_parse"]["status"]`
- Extensible for future pipeline stages
- Maximum depth of 2 levels maintains simplicity

**Structure:**
```
model_entry
├── Core fields (model_id, model_name, gamslib_type, etc.)
├── convexity (nested object)
├── nlp2mcp_parse (nested object)
├── nlp2mcp_translate (nested object)
└── mcp_solve (nested object)
```

### 3. Required Fields Strategy

**Decision:** Minimal required fields at top level; required `status` within each stage

**Top-level required fields:**
- `model_id` - Primary identifier, always known
- `model_name` - Human-readable name, always available
- `gamslib_type` - Model classification, always present

**Stage-level required fields:**
- `status` - Always required when stage object is present

**Rationale:**
- Allows incremental population as models progress through pipeline
- Optional stage objects (absent when not yet tested)
- When a stage is present, `status` is mandatory for filtering/querying

### 4. Strict Validation with `additionalProperties: false`

**Decision:** Reject unknown fields at all levels

**Rationale:**
- Catches typos in field names during development
- Prevents schema drift over time
- Ensures data consistency across all entries
- Forces explicit schema updates for new fields

**Applied to:**
- Top-level database object
- `model_entry` definition
- All stage result definitions
- `error_detail` definition

### 5. Status Enumerations

**Decision:** Define explicit enum values for each stage

**convexity.status:**
- `verified_convex` - Confirmed convex (model_status=1)
- `likely_convex` - Probably convex (model_status=2, locally optimal)
- `locally_optimal` - Only locally optimal solution found
- `infeasible` - Model is infeasible
- `unbounded` - Model is unbounded
- `error` - Solver or execution error
- `excluded` - Excluded from testing (MIP, MINLP, etc.)
- `license_limited` - Exceeds demo license limits
- `unknown` - Status cannot be determined
- `not_tested` - Not yet tested

**nlp2mcp_parse.status:**
- `success` - Parsed successfully
- `failure` - Parse failed
- `partial` - Partial parse (some features unsupported)
- `not_tested` - Not yet tested

**nlp2mcp_translate.status:**
- `success` - Translated successfully
- `failure` - Translation failed
- `not_tested` - Not yet tested

**mcp_solve.status:**
- `success` - MCP solved, objectives match
- `failure` - MCP solve failed
- `mismatch` - MCP solved but objectives don't match
- `not_tested` - Not yet tested

### 6. GAMS Model Types

**Decision:** Expand enum to include all GAMS model types

**Enum values:**
```
LP, NLP, QCP, MIP, MINLP, MIQCP, MCP, CNS, DNLP, MPEC, RMPEC, EMP
```

**Rationale:**
- Existing catalog.json only uses LP, NLP, QCP, MIP, MINLP, MIQCP
- Added MCP, CNS, DNLP, MPEC, RMPEC, EMP for completeness
- Allows future expansion without schema changes

### 7. Error Representation: Structured with Categories

**Decision:** Use structured error objects with mandatory category and message

**error_detail properties:**
- `category` (required) - Error classification for filtering
- `message` (required) - Human-readable error message
- `line` (optional) - Source line number
- `column` (optional) - Source column number
- `details` (optional) - Additional information

**Error categories:**
- `syntax_error` - Parser grammar failure
- `unsupported_feature` - Valid GAMS but not supported by nlp2mcp
- `missing_include` - $include file not found
- `timeout` - Operation exceeded time limit
- `solver_error` - Solver execution error
- `validation_error` - Schema validation error
- `internal_error` - Unexpected internal error

**Rationale:**
- Categories enable querying by error type
- Structured format enables automated analysis
- Line/column enable precise error location for parse errors

### 8. Semantic Versioning

**Decision:** Use MAJOR.MINOR.PATCH pattern

**Semantics:**
- MAJOR: Breaking changes (removed fields, changed types, restructuring)
- MINOR: Backward-compatible additions (new optional fields)
- PATCH: Documentation/metadata updates only

**Current version:** 2.0.0 (major bump from v1.0.0 due to restructuring)

### 9. Date-Time Format

**Decision:** Use ISO 8601 format strings with `format: "date-time"`

**Note:** The jsonschema library does not strictly validate date-time format by default. Application code should validate timestamps using:
```python
datetime.fromisoformat(value.replace('Z', '+00:00'))
```

### 10. URI Format for URLs

**Decision:** Use `format: "uri"` for source_url and web_page_url

**Fields:**
- `source_url` - URL to download raw .gms file
- `web_page_url` - URL to GAMSLIB documentation page

---

## Field Inventory

### Top-Level Database Fields (6)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| schema_version | string | Yes | Semantic version (e.g., "2.0.0") |
| created_date | string | No | ISO 8601 creation timestamp |
| updated_date | string | No | ISO 8601 last modified timestamp |
| gams_version | string | No | GAMS version (e.g., "51.3.0") |
| total_models | integer | No | Count of models in database |
| models | array | Yes | Array of model_entry objects |

### Model Entry Fields (17)

| Field | Type | Required | From catalog.json | Description |
|-------|------|----------|-------------------|-------------|
| model_id | string | Yes | Yes | Unique identifier |
| sequence_number | integer | No | Yes | Original GAMSLIB sequence |
| model_name | string | Yes | Yes | Human-readable name |
| gamslib_type | string | Yes | Yes | GAMS model type enum |
| source_url | string | No | Yes | Download URL |
| web_page_url | string | No | Yes | Documentation URL |
| description | string | No | Yes | Brief description |
| keywords | array | No | Yes | Tags/keywords |
| download_status | string | No | Yes | Download status enum |
| download_date | string | No | Yes | Download timestamp |
| file_path | string | No | Yes | Relative file path |
| file_size_bytes | integer | No | Yes | File size |
| notes | string | No | Yes | Free-form notes |
| convexity | object | No | *Restructured* | Convexity results |
| nlp2mcp_parse | object | No | *New* | Parse results |
| nlp2mcp_translate | object | No | *New* | Translation results |
| mcp_solve | object | No | *New* | MCP solve results |

### Convexity Result Fields (8)

| Field | Type | Required | From catalog.json | Description |
|-------|------|----------|-------------------|-------------|
| status | string | Yes | convexity_status | Status enum |
| verification_date | string | No | verification_date | Timestamp |
| solver | string | No | *New* | Solver name |
| solver_status | integer | No | solver_status | GAMS code |
| model_status | integer | No | model_status | GAMS code |
| objective_value | number | No | objective_value | Optimal value |
| solve_time_seconds | number | No | solve_time_seconds | Solve time |
| error | string | No | verification_error | Error message |

### Parse Result Fields (7)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | string | Yes | Parse status enum |
| parse_date | string | No | Timestamp |
| nlp2mcp_version | string | No | Version used |
| parse_time_seconds | number | No | Parse time |
| variables_count | integer | No | Variables extracted |
| equations_count | integer | No | Equations extracted |
| error | object | No | Structured error |

### Translate Result Fields (8)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | string | Yes | Translation status enum |
| translate_date | string | No | Timestamp |
| nlp2mcp_version | string | No | Version used |
| translate_time_seconds | number | No | Translation time |
| mcp_variables_count | integer | No | MCP variables |
| mcp_equations_count | integer | No | MCP equations |
| output_file | string | No | Output file path |
| error | object | No | Structured error |

### Solve Result Fields (10)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| status | string | Yes | Solve status enum |
| solve_date | string | No | Timestamp |
| solver | string | No | MCP solver (e.g., PATH) |
| solver_status | integer | No | GAMS solver code |
| model_status | integer | No | GAMS model code |
| objective_value | number | No | MCP objective |
| solve_time_seconds | number | No | Solve time |
| objective_match | boolean | No | Objectives match |
| tolerance | number | No | Match tolerance |
| error | object | No | Structured error |

### Error Detail Fields (5)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| category | string | Yes | Error category enum |
| message | string | Yes | Error message |
| line | integer | No | Source line |
| column | integer | No | Source column |
| details | string | No | Additional info |

---

## Migration from catalog.json (v1.0.0)

### Field Mapping

| catalog.json (flat) | gamslib_status.json (nested) |
|---------------------|------------------------------|
| convexity_status | convexity.status |
| verification_date | convexity.verification_date |
| solver_status | convexity.solver_status |
| model_status | convexity.model_status |
| objective_value | convexity.objective_value |
| solve_time_seconds | convexity.solve_time_seconds |
| verification_error | convexity.error |

### New Fields (v2.0.0)

- `convexity.solver` - Explicit solver name
- `nlp2mcp_parse` - Entire object (new pipeline stage)
- `nlp2mcp_translate` - Entire object (new pipeline stage)
- `mcp_solve` - Entire object (new pipeline stage)

### Migration Script Location

Migration will be implemented in Sprint 14:
- Script: `scripts/gamslib/migrate_schema.py`
- Strategy: Eager migration (one-time conversion)

---

## Validation Examples

### Minimal Valid Entry

```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP"
}
```

### Full Entry with All Stages

```json
{
  "model_id": "trnsport",
  "sequence_number": 218,
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP",
  "source_url": "https://www.gams.com/latest/gamslib_ml/trnsport.218",
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2026-01-01T14:00:00Z",
    "solver": "CONOPT",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": 153.675,
    "solve_time_seconds": 0.12
  },
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T10:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "variables_count": 6,
    "equations_count": 5
  },
  "nlp2mcp_translate": {
    "status": "success",
    "translate_date": "2026-01-02T10:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "output_file": "data/gamslib/mcp/trnsport_mcp.gms"
  },
  "mcp_solve": {
    "status": "success",
    "solver": "PATH",
    "objective_value": 153.675,
    "objective_match": true,
    "tolerance": 1e-6
  }
}
```

### Entry with Parse Error

```json
{
  "model_id": "badmodel",
  "model_name": "Model with Parse Error",
  "gamslib_type": "NLP",
  "nlp2mcp_parse": {
    "status": "failure",
    "parse_date": "2026-01-02T10:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "error": {
      "category": "syntax_error",
      "message": "Unexpected token 'loop' at line 42",
      "line": 42,
      "column": 15
    }
  }
}
```

---

## Unknowns Addressed

This schema design implements decisions from the following unknowns (verified across Tasks 3-5):

| ID | Question | Resolution | Verified In |
|----|----------|------------|-------------|
| 2.2 | Nested vs flat structure | Nested (2 levels for pipeline stages) | Task 3 |
| 2.3 | Required vs optional fields | 3 required at top, status required per stage | Task 4 |
| 2.4 | Field naming convention | snake_case (consistent with catalog.json) | Task 5 |
| 2.5 | Error representation | Structured with category, message, optional line/column | Task 4 |
| 2.6 | Status values per stage | Defined enums per stage type | Task 5 |
| 2.7 | Schema versioning strategy | Semantic versioning (MAJOR.MINOR.PATCH) | Task 3 |
| 4.3 | MCP output organization | output_file field with relative path | Task 5 |

**Note:** Unknowns 2.4, 2.6, and 4.3 were newly verified in Task 5. Unknowns 2.2, 2.3, 2.5, and 2.7 were verified in Tasks 3 and 4.

---

## Document History

- January 1, 2026: Initial creation (Sprint 14 Prep Task 5)
