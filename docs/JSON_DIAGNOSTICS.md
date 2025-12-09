# JSON Diagnostics Output

**Version:** 1.0.0  
**Sprint:** Epic 2 - Sprint 12 Day 7

## Overview

The nlp2mcp CLI supports JSON-formatted diagnostic output for machine-parseable pipeline metrics. This enables CI integration, historical trending, and automated analysis of conversion performance.

## Usage

### Basic Usage

```bash
# Text output (default)
nlp2mcp model.gms --diagnostics

# JSON output
nlp2mcp model.gms --diagnostics --format json

# JSON output to file (via stderr redirect)
nlp2mcp model.gms --diagnostics --format json 2> diagnostics.json
```

### Output Location

Diagnostic output is written to **stderr**, allowing separation from the main MCP output which goes to stdout or the specified output file.

```bash
# MCP to file, diagnostics to stdout
nlp2mcp model.gms -o output.gms --diagnostics --format json 2>&1

# MCP to stdout, diagnostics to file
nlp2mcp model.gms --diagnostics --format json 2> diagnostics.json
```

## Schema Version 1.0.0

### Top-Level Structure

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-12-09T12:34:56.789+00:00",
  "model_name": "rbrock.gms",
  "total_duration_ms": 45.23,
  "overall_success": true,
  "stages": { ... },
  "summary": { ... }
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | SemVer version (e.g., "1.0.0") |
| `generated_at` | string | ISO 8601 UTC timestamp |
| `model_name` | string | GAMS model filename |
| `total_duration_ms` | number | Sum of all stage durations |
| `overall_success` | boolean | True if all stages succeeded |
| `stages` | object | Per-stage metrics |
| `summary` | object | Aggregate statistics |

### Stages Object

Each stage contains:

```json
{
  "Parse": {
    "duration_ms": 12.34,
    "success": true,
    "error": null,
    "details": {
      "sets": 5,
      "parameters": 10,
      "variables": 8,
      "equations": 3
    }
  }
}
```

### Pipeline Stages

1. **Parse** - GAMS source to IR model
2. **Semantic Analysis** - Validation and structure checks
3. **Simplification** - Model normalization and reformulation
4. **IR Generation** - Derivative computation and KKT assembly
5. **MCP Generation** - GAMS MCP code emission

### Summary Object

```json
{
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 12.34,
    "semantic_duration_ms": 0.08,
    "simplification_duration_ms": 2.54,
    "ir_generation_duration_ms": 3.52,
    "mcp_generation_duration_ms": 0.45
  }
}
```

## CI Integration Examples

### GitHub Actions: Store as Artifact

```yaml
- name: Run conversion with diagnostics
  run: |
    nlp2mcp model.gms -o output.gms --diagnostics --format json 2> diagnostics.json

- name: Upload diagnostics
  uses: actions/upload-artifact@v4
  with:
    name: diagnostics
    path: diagnostics.json
```

### Extract Metrics with jq

```bash
# Check overall success
jq -r '.overall_success' diagnostics.json

# Get total duration
jq -r '.total_duration_ms' diagnostics.json

# Get parse stage details
jq -r '.stages.Parse.details' diagnostics.json

# Check for failures
jq -r 'select(.overall_success == false) | .model_name' diagnostics.json
```

### Batch Processing

```bash
# Process multiple models
for model in *.gms; do
  nlp2mcp "$model" -o "out_${model}" --diagnostics --format json 2> "${model%.gms}.diag.json"
done

# Aggregate results
jq -s '[.[] | {name: .model_name, success: .overall_success, duration: .total_duration_ms}]' *.diag.json
```

## Example Output

### Success Case

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-12-09T19:34:02.348542+00:00",
  "model_name": "rbrock.gms",
  "total_duration_ms": 373.60,
  "overall_success": true,
  "stages": {
    "Parse": {
      "duration_ms": 367.88,
      "success": true,
      "error": null,
      "details": {
        "sets": 0,
        "parameters": 4,
        "variables": 3,
        "equations": 1
      }
    },
    "Semantic Analysis": {
      "duration_ms": 0.07,
      "success": true,
      "error": null,
      "details": {
        "equalities": 0,
        "inequalities": 0
      }
    },
    "Simplification": {
      "duration_ms": 1.79,
      "success": true,
      "error": null,
      "details": {
        "vars_added": 0,
        "eqs_added": 0,
        "normalized_equations": 1
      }
    },
    "IR Generation": {
      "duration_ms": 3.39,
      "success": true,
      "error": null,
      "details": {
        "gradient_cols": 3,
        "eq_jacobian_rows": 1,
        "ineq_jacobian_rows": 4,
        "stationarity_eqs": 2
      }
    },
    "MCP Generation": {
      "duration_ms": 0.47,
      "success": true,
      "error": null,
      "details": {
        "output_lines": 107,
        "output_bytes": 2664
      }
    }
  },
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 367.88,
    "semantic_duration_ms": 0.07,
    "simplification_duration_ms": 1.79,
    "ir_generation_duration_ms": 3.39,
    "mcp_generation_duration_ms": 0.47
  }
}
```

### Failure Case

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-12-09T12:36:45.123+00:00",
  "model_name": "invalid.gms",
  "total_duration_ms": 8.45,
  "overall_success": false,
  "stages": {
    "Parse": {
      "duration_ms": 8.45,
      "success": false,
      "error": "Syntax error at line 42: Unexpected token",
      "details": {}
    }
  },
  "summary": {
    "stages_completed": 1,
    "stages_failed": 1,
    "stages_skipped": 4,
    "parse_duration_ms": 8.45,
    "semantic_duration_ms": 0,
    "simplification_duration_ms": 0,
    "ir_generation_duration_ms": 0,
    "mcp_generation_duration_ms": 0
  }
}
```

## Schema Validation

The JSON schema is available at `docs/schemas/diagnostics_v1.0.0.json`.

```bash
# Validate with jsonschema (Python)
pip install jsonschema
jsonschema -i diagnostics.json docs/schemas/diagnostics_v1.0.0.json

# Validate with ajv (Node.js)
npx ajv validate -s docs/schemas/diagnostics_v1.0.0.json -d diagnostics.json
```

## Versioning Policy

The schema follows Semantic Versioning (SemVer):

- **MAJOR:** Incompatible schema changes (removing fields, changing types)
- **MINOR:** Backward-compatible additions (new optional fields)
- **PATCH:** Documentation or clarification changes

Consumers should check `schema_version` and handle unknown fields gracefully.

## Related Documentation

- [Sprint 12 JSON Diagnostics Schema Design](planning/EPIC_2/SPRINT_12/JSON_DIAGNOSTICS_SCHEMA.md)
- [CI Regression Guardrails](CI_REGRESSION_GUARDRAILS.md)
