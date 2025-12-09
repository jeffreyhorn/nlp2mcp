# CI Regression Guardrails

This document describes the regression guardrails implemented in the CI pipeline to ensure code quality and track pipeline performance over time.

## Overview

The CI workflow (`.github/workflows/ci.yml`) includes several guardrails:

1. **Fast Test Suite** - Quick tests run in parallel for rapid feedback
2. **Full Test Suite with Coverage** - Complete test run with coverage reporting
3. **JSON Diagnostics Generation** - Pipeline performance metrics for all tier 1 models
4. **Test Pyramid Visualization** - Test distribution analysis

## JSON Diagnostics Artifacts

### Purpose

The CI pipeline generates JSON diagnostics for all tier 1 models on every run. These artifacts:
- Track pipeline performance over time
- Enable historical trend analysis
- Help identify performance regressions
- Provide debugging information for failures

### How It Works

The CI runs the nlp2mcp CLI with `--diagnostics --format json` on each tier 1 model:

```bash
for model in models/tier1/*.gms; do
  model_name=$(basename "$model" .gms)
  python -m src.cli "$model" --diagnostics --format json 2> "diagnostics/${model_name}.json" || true
done
```

### Artifact Storage

- **Artifact name**: `pipeline-diagnostics`
- **Location**: `diagnostics/` directory
- **Retention**: 90 days
- **Format**: JSON v1.0.0 schema (see `docs/schemas/diagnostics_v1.0.0.json`)

### Accessing Artifacts

1. Navigate to the GitHub Actions run
2. Click on the "Artifacts" section at the bottom
3. Download `pipeline-diagnostics.zip`
4. Extract to view individual model JSON files

### JSON Schema

Each diagnostics file follows schema v1.0.0:

```json
{
  "schema_version": "1.0.0",
  "generated_at": "2025-01-15T10:30:00+00:00",
  "model_name": "transport",
  "total_duration_ms": 156.7,
  "overall_success": true,
  "stages": {
    "parse": {
      "duration_ms": 45.2,
      "success": true,
      "error": null,
      "details": {"sets": 2, "parameters": 3, "variables": 1, "equations": 2}
    },
    "semantic": {...},
    "simplification": {...},
    "ir_generation": {...},
    "mcp_generation": {...}
  },
  "summary": {
    "stages_completed": 5,
    "stages_failed": 0,
    "stages_skipped": 0,
    "parse_duration_ms": 45.2,
    "semantic_duration_ms": 12.3,
    "simplification_duration_ms": 8.1,
    "ir_generation_duration_ms": 52.4,
    "mcp_generation_duration_ms": 38.7
  }
}
```

## Using Diagnostics for Regression Detection

### Manual Analysis

Download artifacts from two CI runs and compare:

```bash
# Compare parse times
jq '.stages.parse.duration_ms' run1/transport.json run2/transport.json

# Check for new failures
jq 'select(.overall_success == false) | .model_name' run2/*.json
```

### Dashboard Integration

The diagnostics artifacts are designed to feed into a dashboard (see `scripts/generate_dashboard.py`) for:
- Time-series performance charts
- Stage-by-stage breakdown
- Failure trend analysis
- Model coverage tracking

## Test Pyramid Artifact

The CI also generates a test pyramid visualization showing the distribution of unit, integration, and end-to-end tests. This helps maintain a healthy testing strategy.

- **Artifact name**: `test-pyramid`
- **File**: `docs/testing/TEST_PYRAMID.md`

## Future Enhancements

1. **Automated Regression Alerts** - GitHub Actions to flag significant performance regressions
2. **Historical Dashboard** - Aggregate diagnostics over time for trend analysis
3. **Tier 2 Coverage** - Extend diagnostics to tier 2 models as parsing support improves
4. **Performance Thresholds** - Fail CI if stage durations exceed configured limits
