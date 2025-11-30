# JSON Diagnostics Schema Design

**Date:** 2025-11-30  
**Sprint:** Epic 2 - Sprint 12 Prep Task 5  
**Purpose:** Design JSON schema for `--diagnostic-json` output  
**Version:** 1.0.0

---

## Executive Summary

**Problem:** Sprint 11 added text diagnostics but lacks machine-parseable JSON output for CI integration and trending.

**Solution:** Extend DiagnosticReport.to_json() with schema versioning, metadata, and standardized structure.

**Key Decisions:**
- **Format:** Single JSON object per model (not NDJSON)
- **Versioning:** SemVer (schema_version field)
- **Backward Compatibility:** --format flag (text default, json opt-in)
- **Complexity:** Direct serialization (no transformation needed)

---

## Schema Overview

### Version 1.0.0

**Top-level Fields:**
```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-11-30T12:34:56.789Z",
  "model_name": "rbrock.gms",
  "total_duration_ms": 45.23,
  "overall_success": true,
  "stages": { ... },
  "summary": { ... }
}
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | Yes | SemVer version (e.g., "1.0.0") |
| `generated_at` | string (ISO 8601) | Yes | UTC timestamp when report generated |
| `model_name` | string | Yes | GAMS model filename |
| `total_duration_ms` | number | Yes | Sum of all stage durations |
| `overall_success` | boolean | Yes | True if all stages succeeded |
| `stages` | object | Yes | Per-stage metrics (see below) |
| `summary` | object | Yes | Aggregate statistics (see below) |

---

## Stages Object

**Structure:**
```json
{
  "stages": {
    "Parse": {
      "duration_ms": 12.34,
      "success": true,
      "error": null,
      "details": { ... }
    },
    "Semantic Analysis": { ... },
    "Simplification": { ... },
    "IR Generation": { ... },
    "MCP Generation": { ... }
  }
}
```

**Stage Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `duration_ms` | number | Yes | Stage execution time in milliseconds |
| `success` | boolean | Yes | True if stage completed without errors |
| `error` | string \| null | Yes | Error message if failed, null if success |
| `details` | object | Yes | Stage-specific metadata (see below) |

**Stage-Specific Details:**

### Parse Stage
```json
{
  "details": {
    "lines": 150,
    "tokens": 1234
  }
}
```

### Semantic Analysis Stage
```json
{
  "details": {
    "symbols_declared": 25,
    "symbols_referenced": 30
  }
}
```

### Simplification Stage
```json
{
  "details": {
    "passes": 3,
    "expressions_simplified": 12,
    "constants_folded": 5
  }
}
```

### IR Generation Stage
```json
{
  "details": {
    "sets_generated": 5,
    "parameters_generated": 10,
    "variables_generated": 8
  }
}
```

### MCP Generation Stage
```json
{
  "details": {
    "output_lines": 200,
    "output_bytes": 5432
  }
}
```

---

## Summary Object

**Purpose:** Aggregate statistics across all stages for easy trending.

**Structure:**
```json
{
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 12.34,
    "semantic_duration_ms": 8.56,
    "simplification_duration_ms": 15.78,
    "ir_generation_duration_ms": 4.32,
    "mcp_generation_duration_ms": 4.23
  }
}
```

**Summary Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `stages_completed` | number | Count of stages that ran (success or failure) |
| `stages_failed` | number | Count of stages with success=false |
| `stages_skipped` | number | Count of stages not executed (early termination) |
| `parse_duration_ms` | number | Parse stage duration (0 if skipped) |
| `semantic_duration_ms` | number | Semantic stage duration (0 if skipped) |
| `simplification_duration_ms` | number | Simplification stage duration (0 if skipped) |
| `ir_generation_duration_ms` | number | IR Gen stage duration (0 if skipped) |
| `mcp_generation_duration_ms` | number | MCP Gen stage duration (0 if skipped) |

---

## Versioning Policy

### SemVer (Semantic Versioning)

**Format:** `MAJOR.MINOR.PATCH`

**Rules:**
- **MAJOR:** Incompatible schema changes (e.g., removing fields, changing types)
- **MINOR:** Backward-compatible additions (e.g., new optional fields)
- **PATCH:** Documentation or bugfix clarifications (no schema changes)

### Current Version: 1.0.0

**Version History:**
- **1.0.0** (2025-11-30): Initial schema design (Sprint 12 Prep)

### Future Evolution Examples

**1.1.0 - Add optional field (backward compatible):**
```json
{
  "schema_version": "1.1.0",
  "environment": {
    "python_version": "3.11.5",
    "platform": "darwin"
  }
}
```
- Consumers on 1.0.0 can ignore new fields
- Consumers on 1.1.0 can use new data

**2.0.0 - Breaking change (incompatible):**
```json
{
  "schema_version": "2.0.0",
  "stages": [
    { "name": "Parse", "duration_ms": 12.34, ... }
  ]
}
```
- Changed stages from object to array
- Requires migration guide
- Consumers must update parsers

### Migration Guide Template

When releasing a new MAJOR version:
1. Document all breaking changes
2. Provide migration examples (old → new)
3. Update schema_version in code
4. Add version detection in consumers

---

## Output Format Selection

### Decision: Single JSON Object (not NDJSON)

**Rationale:**

**Option A: Single JSON Object** ✅ SELECTED
```json
{ "schema_version": "1.0.0", "model_name": "rbrock.gms", ... }
```
- **Pros:** Simplest for CLI use case, easy to read/write, jq-friendly
- **Cons:** Not ideal for streaming multiple models
- **Use Case:** Sprint 12 CLI diagnostics for single model invocations

**Option B: NDJSON (Newline-Delimited JSON)**
```
{"schema_version":"1.0.0","model_name":"model1.gms",...}
{"schema_version":"1.0.0","model_name":"model2.gms",...}
```
- **Pros:** Streamable, append-friendly for batch processing
- **Cons:** More complex to parse, not needed for single-model CLI
- **Verdict:** ❌ Deferred - Not needed for Sprint 12 scope

**Option C: JSON Array**
```json
[
  { "schema_version": "1.0.0", "model_name": "model1.gms", ... },
  { "schema_version": "1.0.0", "model_name": "model2.gms", ... }
]
```
- **Pros:** Valid JSON, can contain multiple models
- **Cons:** Requires buffering entire array, not append-friendly
- **Verdict:** ❌ Rejected - Complexity without benefit

### Future: Batch Processing

If Sprint 13+ needs batch diagnostics for GAMSLib ingestion:
- Consider NDJSON for `scripts/measure_parse_rate.py --diagnostic-json`
- Keep single JSON object for CLI `gams2mcp --diagnostic-json`
- Add `--diagnostic-format` flag to choose (json | ndjson)

---

## Backward Compatibility

### --format Flag Approach

**Default Behavior:** Text output (Sprint 11)
```bash
gams2mcp model.gms --diagnostics
# Output: Text table to stderr
```

**JSON Output:** Opt-in via --format flag
```bash
gams2mcp model.gms --diagnostics --format json
# Output: JSON object to stderr
```

**Implementation:**
```python
if args.diagnostics:
    report = create_report(model_name)
    # ... run pipeline with DiagnosticContext ...
    
    if args.format == "json":
        print(json.dumps(report.to_json_v1(), indent=2), file=sys.stderr)
    else:
        print(report.to_text(), file=sys.stderr)
```

**Backward Compatibility Guarantees:**
- ✅ Existing scripts using --diagnostics unchanged (text default)
- ✅ No breaking changes to DiagnosticReport API
- ✅ JSON output opt-in only
- ✅ Future --format values: json-compact, ndjson, etc.

---

## Example JSON Files

### Example 1: Success (rbrock.gms)

**Scenario:** All 5 stages complete successfully

**File:** `docs/planning/EPIC_2/SPRINT_12/examples/success.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-11-30T12:34:56.789Z",
  "model_name": "rbrock.gms",
  "total_duration_ms": 45.23,
  "overall_success": true,
  "stages": {
    "Parse": {
      "duration_ms": 12.34,
      "success": true,
      "error": null,
      "details": {
        "lines": 150,
        "tokens": 1234
      }
    },
    "Semantic Analysis": {
      "duration_ms": 8.56,
      "success": true,
      "error": null,
      "details": {
        "symbols_declared": 25,
        "symbols_referenced": 30
      }
    },
    "Simplification": {
      "duration_ms": 15.78,
      "success": true,
      "error": null,
      "details": {
        "passes": 3,
        "expressions_simplified": 12,
        "constants_folded": 5
      }
    },
    "IR Generation": {
      "duration_ms": 4.32,
      "success": true,
      "error": null,
      "details": {
        "sets_generated": 5,
        "parameters_generated": 10,
        "variables_generated": 8
      }
    },
    "MCP Generation": {
      "duration_ms": 4.23,
      "success": true,
      "error": null,
      "details": {
        "output_lines": 200,
        "output_bytes": 5432
      }
    }
  },
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 12.34,
    "semantic_duration_ms": 8.56,
    "simplification_duration_ms": 15.78,
    "ir_generation_duration_ms": 4.32,
    "mcp_generation_duration_ms": 4.23
  }
}
```

---

### Example 2: Partial Success with Warnings

**Scenario:** All stages complete but simplification has warnings in details

**File:** `docs/planning/EPIC_2/SPRINT_12/examples/partial.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-11-30T12:35:12.456Z",
  "model_name": "complex.gms",
  "total_duration_ms": 78.91,
  "overall_success": true,
  "stages": {
    "Parse": {
      "duration_ms": 18.23,
      "success": true,
      "error": null,
      "details": {
        "lines": 450,
        "tokens": 3456
      }
    },
    "Semantic Analysis": {
      "duration_ms": 12.67,
      "success": true,
      "error": null,
      "details": {
        "symbols_declared": 75,
        "symbols_referenced": 82
      }
    },
    "Simplification": {
      "duration_ms": 35.89,
      "success": true,
      "error": null,
      "details": {
        "passes": 5,
        "expressions_simplified": 42,
        "constants_folded": 18,
        "warnings": [
          "Complex nested expression at line 125 - may benefit from manual refactoring",
          "High recursion depth in equation system - consider simplification"
        ]
      }
    },
    "IR Generation": {
      "duration_ms": 7.45,
      "success": true,
      "error": null,
      "details": {
        "sets_generated": 12,
        "parameters_generated": 25,
        "variables_generated": 18
      }
    },
    "MCP Generation": {
      "duration_ms": 4.67,
      "success": true,
      "error": null,
      "details": {
        "output_lines": 550,
        "output_bytes": 15678
      }
    }
  },
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 18.23,
    "semantic_duration_ms": 12.67,
    "simplification_duration_ms": 35.89,
    "ir_generation_duration_ms": 7.45,
    "mcp_generation_duration_ms": 4.67
  }
}
```

---

### Example 3: Parse Failure (Early Termination)

**Scenario:** Parse stage fails, subsequent stages skipped

**File:** `docs/planning/EPIC_2/SPRINT_12/examples/failure.json`

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-11-30T12:36:45.123Z",
  "model_name": "invalid.gms",
  "total_duration_ms": 8.45,
  "overall_success": false,
  "stages": {
    "Parse": {
      "duration_ms": 8.45,
      "success": false,
      "error": "Syntax error at line 42: Unexpected token 'INVALID_KEYWORD'",
      "details": {
        "lines": 100,
        "tokens": 0,
        "error_line": 42,
        "error_column": 15
      }
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

---

## Implementation Notes for Sprint 12

### Code Changes Required

**1. Update DiagnosticReport.to_json()** (src/ir/diagnostics.py:116-131)

Current implementation:
```python
def to_json(self) -> dict[str, Any]:
    return {
        "model_name": self.model_name,
        "total_duration_ms": self.total_duration_ms,
        "overall_success": self.overall_success,
        "stages": { ... }
    }
```

New implementation (to_json_v1):
```python
def to_json_v1(self) -> dict[str, Any]:
    """Format report as JSON with schema v1.0.0."""
    from datetime import datetime, timezone
    
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_name": self.model_name,
        "total_duration_ms": self.total_duration_ms,
        "overall_success": self.overall_success,
        "stages": {
            stage.value: {
                "duration_ms": metrics.duration_ms,
                "success": metrics.success,
                "error": metrics.error,
                "details": metrics.details,
            }
            for stage, metrics in self.stages.items()
        },
        "summary": self._build_summary()
    }

def _build_summary(self) -> dict[str, Any]:
    """Build summary object from stages."""
    all_stages = list(Stage)
    completed = len(self.stages)
    failed = sum(1 for m in self.stages.values() if not m.success)
    skipped = len(all_stages) - completed
    
    return {
        "stages_completed": completed,
        "stages_failed": failed,
        "stages_skipped": skipped,
        "parse_duration_ms": self.stages.get(Stage.PARSE, StageMetrics(Stage.PARSE)).duration_ms,
        "semantic_duration_ms": self.stages.get(Stage.SEMANTIC, StageMetrics(Stage.SEMANTIC)).duration_ms,
        "simplification_duration_ms": self.stages.get(Stage.SIMPLIFICATION, StageMetrics(Stage.SIMPLIFICATION)).duration_ms,
        "ir_generation_duration_ms": self.stages.get(Stage.IR_GENERATION, StageMetrics(Stage.IR_GENERATION)).duration_ms,
        "mcp_generation_duration_ms": self.stages.get(Stage.MCP_GENERATION, StageMetrics(Stage.MCP_GENERATION)).duration_ms,
    }
```

**2. Add --format CLI Flag** (src/cli.py or main entry point)

```python
parser.add_argument(
    "--format",
    choices=["text", "json"],
    default="text",
    help="Diagnostic output format (default: text)"
)
```

**3. Update Diagnostic Output Logic**

```python
if args.diagnostics:
    if args.format == "json":
        import json
        print(json.dumps(report.to_json_v1(), indent=2), file=sys.stderr)
    else:
        print(report.to_text(), file=sys.stderr)
```

**4. Add Tests** (tests/test_diagnostics.py)

```python
def test_json_v1_schema():
    """Verify JSON output conforms to v1.0.0 schema."""
    report = DiagnosticReport(model_name="test.gms")
    # ... add stages ...
    
    json_output = report.to_json_v1()
    
    assert json_output["schema_version"] == "1.0.0"
    assert "generated_at" in json_output
    assert "summary" in json_output
    assert json_output["summary"]["stages_completed"] == 5
```

---

## CI Integration Use Cases

### Use Case 1: Store Diagnostics as Artifacts

```yaml
# .github/workflows/ci.yml
- name: Run GAMSLib ingestion with diagnostics
  run: |
    for model in gamslib/*.gms; do
      gams2mcp "$model" --diagnostics --format json > "artifacts/$(basename $model).diag.json" 2>&1
    done

- name: Upload diagnostic artifacts
  uses: actions/upload-artifact@v3
  with:
    name: diagnostics
    path: artifacts/*.diag.json
```

### Use Case 2: Extract Performance Metrics for Trending

```bash
# Extract total duration from all models
jq -r '[.model_name, .total_duration_ms] | @csv' artifacts/*.diag.json > performance.csv

# Find slowest stage across models
jq -r '.stages | to_entries | max_by(.value.duration_ms) | [input_filename, .key, .value.duration_ms] | @csv' artifacts/*.diag.json
```

### Use Case 3: Detect Failures in CI

```bash
# Check if any model failed
failed_models=$(jq -r 'select(.overall_success == false) | .model_name' artifacts/*.diag.json)

if [ -n "$failed_models" ]; then
  echo "❌ Failed models: $failed_models"
  exit 1
fi
```

---

## Schema Validation

### JSON Schema (Optional Enhancement)

For strict validation, a JSON Schema can be defined:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GAMS-to-MCP Diagnostic Report",
  "type": "object",
  "required": ["schema_version", "generated_at", "model_name", "total_duration_ms", "overall_success", "stages", "summary"],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "model_name": {
      "type": "string"
    },
    "total_duration_ms": {
      "type": "number",
      "minimum": 0
    },
    "overall_success": {
      "type": "boolean"
    },
    "stages": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["duration_ms", "success", "error", "details"],
        "properties": {
          "duration_ms": { "type": "number", "minimum": 0 },
          "success": { "type": "boolean" },
          "error": { "type": ["string", "null"] },
          "details": { "type": "object" }
        }
      }
    },
    "summary": {
      "type": "object",
      "required": ["stages_completed", "stages_failed", "stages_skipped"],
      "properties": {
        "stages_completed": { "type": "number", "minimum": 0 },
        "stages_failed": { "type": "number", "minimum": 0 },
        "stages_skipped": { "type": "number", "minimum": 0 }
      }
    }
  }
}
```

**Validation Command:**
```bash
# Install jsonschema validator
pip install jsonschema

# Validate example
jsonschema -i examples/success.json schema.json
```

**Verdict:** ❌ Deferred to Sprint 13+ (not critical for initial implementation)

---

## Performance Considerations

### Overhead Analysis

**Text Output:**
- String concatenation: ~0.1ms for 5 stages
- No serialization overhead

**JSON Output:**
- json.dumps(): ~0.2-0.5ms for typical report
- indent=2: +0.1ms (human-readable)
- indent=None: Faster, but less readable

**Recommendation:**
- CLI: Use indent=2 (readability > speed)
- CI batch: Use indent=None (speed > readability)
- Add --json-compact flag for compact output

### Memory Usage

**Typical Report Size:**
- Text: ~2KB
- JSON (indented): ~3-4KB
- JSON (compact): ~2KB

**Batch Processing (40 models):**
- Memory: ~160KB total
- Negligible impact on pipeline

---

## Unknowns Resolution

### Unknown 3.1: Schema Design Complexity

**Question:** Can DiagnosticReport be directly serialized, or does it need transformation?

**Answer:** ✅ Direct serialization with minor enhancements
- Current `to_json()` method is 90% complete
- Add: schema_version, generated_at, summary fields
- No major refactoring required

**Evidence:**
- DiagnosticReport already uses simple types (str, float, bool, dict)
- StageMetrics.details is dict[str, Any] - already JSON-compatible
- Only additions needed: metadata fields

**Impact:** Low complexity - Sprint 12 Day 7 can implement in <4 hours

---

### Unknown 3.2: Output Format Selection

**Question:** NDJSON, JSON array, or single object?

**Answer:** ✅ Single JSON object per model

**Rationale:**
- CLI use case: One model per invocation → one JSON object
- Simplest to implement and consume
- jq-friendly for CI scripts
- NDJSON deferred to future batch processing needs

**Trade-offs:**
- ✅ Simple, standard JSON
- ❌ Not optimized for streaming multiple models
- Future: Add NDJSON support if measure_parse_rate.py needs it

**Impact:** Clear decision enables straightforward implementation

---

### Unknown 3.3: Backward Compatibility

**Question:** How to add JSON without breaking existing --diagnostics users?

**Answer:** ✅ --format flag with text default

**Approach:**
```bash
# Existing behavior (text)
gams2mcp model.gms --diagnostics

# New behavior (JSON, opt-in)
gams2mcp model.gms --diagnostics --format json
```

**Guarantees:**
- ✅ No breaking changes to existing scripts
- ✅ Text remains default
- ✅ JSON opt-in via explicit flag
- ✅ Future formats (json-compact, ndjson) can be added

**Test Coverage:**
- Unit tests: Both text and JSON outputs
- Integration tests: CLI with --format flag
- Regression: Verify text output unchanged

**Impact:** Zero risk to existing users, smooth migration path

---

## Summary

### Schema v1.0.0 Highlights

- **Format:** Single JSON object
- **Versioning:** SemVer with schema_version field
- **Backward Compatible:** --format flag, text default
- **Complete Coverage:** All data from text diagnostics
- **CI-Ready:** Examples validate with jq
- **Low Complexity:** Direct serialization, no refactoring

### Implementation Checklist

- [ ] Add to_json_v1() method to DiagnosticReport
- [ ] Add _build_summary() helper method
- [ ] Add --format CLI flag
- [ ] Update diagnostic output logic
- [ ] Create example JSON files (3)
- [ ] Add unit tests for JSON schema
- [ ] Update documentation
- [ ] Validate examples with jq

### Sprint 12 Component 3 Readiness

This design provides:
- ✅ Clear schema structure for implementation
- ✅ Versioning strategy for future evolution
- ✅ Backward compatibility guarantees
- ✅ Validation examples
- ✅ CI integration patterns

Component 3 (Days 7-8) can proceed with confidence.
