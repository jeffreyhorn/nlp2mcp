# GAMSLib Integration

This document describes the GAMSLib model ingestion and conversion tracking system implemented in Sprint 6.

## Overview

The GAMSLib integration provides automated ingestion of GAMS benchmark models with comprehensive tracking of parsing, conversion, and solving success rates. The system generates both machine-readable JSON reports and human-readable Markdown dashboards.

## Quick Start

### Running Ingestion

```bash
# Run full ingestion pipeline with dashboard generation
make ingest-gamslib

# Or run manually with custom paths
python scripts/ingest_gamslib.py \
    --input tests/fixtures/gamslib \
    --output reports/gamslib_ingestion_sprint6.json \
    --dashboard docs/status/GAMSLIB_CONVERSION_STATUS.md
```

### Viewing Results

- **Dashboard:** [`docs/status/GAMSLIB_CONVERSION_STATUS.md`](../status/GAMSLIB_CONVERSION_STATUS.md)
- **JSON Report:** `reports/gamslib_ingestion_sprint6.json`

## Components

### 1. Ingestion Script (`scripts/ingest_gamslib.py`)

The ingestion script processes GAMSLib models and generates comprehensive reports.

**Features:**
- Parses all `.gms` files in a directory
- Captures parse success/failure status
- Records detailed error messages and types
- Calculates KPI metrics (parse%, convert%, solve%)
- Generates JSON report for programmatic access
- Optionally generates Markdown dashboard for human viewing

**Usage:**
```bash
python scripts/ingest_gamslib.py [OPTIONS]

Options:
  --input PATH       Directory containing .gms files
                     (default: tests/fixtures/gamslib)
  
  --output PATH      Output JSON report file
                     (default: reports/gamslib_ingestion_sprint6.json)
  
  --dashboard PATH   Optional: Generate Markdown dashboard
                     (e.g., docs/status/GAMSLIB_CONVERSION_STATUS.md)
```

### 2. Makefile Target (`make ingest-gamslib`)

Convenient one-command ingestion pipeline.

**What it does:**
1. Checks that GAMSLib models exist in `tests/fixtures/gamslib`
2. Runs ingestion script with standard paths
3. Generates both JSON report and Markdown dashboard
4. Displays summary with file locations

**Prerequisites:**
```bash
# Download GAMSLib models (one-time setup)
./scripts/download_gamslib_nlp.sh
```

### 3. Conversion Dashboard

The dashboard provides at-a-glance visibility into GAMSLib conversion status.

**Location:** `docs/status/GAMSLIB_CONVERSION_STATUS.md`

**Sections:**
1. **Overall KPIs** - Parse%, Convert%, Solve%, End-to-End success rates
2. **Model Status** - Per-model results with status icons
3. **Error Breakdown** - Categorized error counts
4. **Failure Details** - Detailed error messages for debugging

## KPI Definitions

### Parse Rate
Percentage of models that parse successfully without syntax errors.

```
Parse Rate = (Models Parsed Successfully / Total Models) × 100%
```

**Sprint 6 Target:** ≥10% (at least 1 model out of 10)

### Convert Rate
Percentage of successfully parsed models that convert to MCP format.

```
Convert Rate = (Models Converted / Models Parsed) × 100%
```

**Sprint 6 Status:** Not yet implemented (shows 0%)

### Solve Rate
Percentage of converted models that solve successfully with PATH.

```
Solve Rate = (Models Solved / Models Converted) × 100%
```

**Sprint 6 Status:** Not yet implemented (shows 0%)

### End-to-End Success
Percentage of models that complete the full parse → convert → solve pipeline.

```
E2E Rate = (Models Solved / Total Models) × 100%
```

**Sprint 6 Status:** Not yet implemented (shows 0%)

## Dashboard Interpretation

### Status Icons

- **✅ Success** - Stage completed successfully
- **❌ Failed** - Stage failed with error
- **`-`** - Stage not attempted (prerequisite failed or not implemented)
- **⚠️** - Warning or not yet implemented

### Reading the KPI Table

Example:
```markdown
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Parse Rate | 60.0% (6/10) | ≥10% | ✅ |
```

- **Value:** Shows percentage and fraction (6 out of 10 models parsed)
- **Target:** Minimum acceptable threshold
- **Status:** ✅ if target met, ❌ if not met

### Understanding Model Status

Example:
```markdown
| Model | Parse | Convert | Solve | E2E | Notes |
|-------|-------|---------|-------|-----|-------|
| trig  | ✅    | -       | -     | ❌  | Parsed successfully |
```

- **trig** parsed successfully
- Convert/Solve stages not attempted (shown as `-`)
- E2E is ❌ because the full pipeline hasn't been implemented yet
- Notes explain current status

## Common Parse Errors

### UnexpectedToken
**Cause:** Parser encountered unexpected syntax  
**Example:** Missing semicolon, typo in keyword  
**Fix:** Check GAMS syntax near reported line number

### VisitError
**Cause:** Internal parser error during tree traversal  
**Example:** Unsupported language feature, complex expression  
**Fix:** May require parser enhancement

### LarkError
**Cause:** Grammar doesn't recognize syntax  
**Example:** Advanced GAMS features not yet supported  
**Fix:** May require grammar extension

## Troubleshooting

### "No .gms files found"

**Problem:** Ingestion script can't find model files

**Solution:**
```bash
# Download models first
./scripts/download_gamslib_nlp.sh

# Verify models exist
ls tests/fixtures/gamslib/*.gms
```

### Parse rate is 0%

**Problem:** No models parse successfully

**Possible causes:**
1. Models use advanced GAMS features not yet supported
2. Parser grammar needs extension
3. Models have syntax incompatible with current parser

**Solution:**
1. Check error details in dashboard "Failure Details" section
2. Review `docs/research/gamslib_parse_errors.md` for known issues
3. File GitHub issues for unsupported features

### Dashboard not generated

**Problem:** JSON report exists but dashboard missing

**Solution:**
```bash
# Generate dashboard from existing report
python scripts/ingest_gamslib.py \
    --output reports/gamslib_ingestion_sprint6.json \
    --dashboard docs/status/GAMSLIB_CONVERSION_STATUS.md
```

Note: The script regenerates the JSON report even if it exists. To generate only the dashboard from an existing report, you'll need to run ingestion again (this updates the report).

## Ingestion Cadence

### Sprint 6
**Cadence:** Manual, as needed  
**Process:** Developer runs `make ingest-gamslib` manually

### Sprint 7+ (Planned)
**Cadence:** Weekly or per-sprint  
**Process:** Semi-automated via `make` target  
**Future:** Potentially fully automated via CI/CD

## File Locations

```
nlp2mcp/
├── scripts/
│   ├── ingest_gamslib.py          # Ingestion script
│   └── download_gamslib_nlp.sh    # Model downloader
├── reports/
│   └── gamslib_ingestion_sprint6.json   # JSON report
├── docs/
│   ├── status/
│   │   └── GAMSLIB_CONVERSION_STATUS.md  # Dashboard
│   ├── features/
│   │   └── gamslib_integration.md        # This file
│   └── research/
│       ├── gamslib_parse_errors.md       # Error analysis
│       ├── dashboard_design.md           # Dashboard design doc
│       └── ingestion_schedule.md         # Automation strategy
└── tests/fixtures/gamslib/         # Downloaded models
    ├── trig.gms
    ├── circle.gms
    └── ...
```

## JSON Report Format

The JSON report follows this structure:

```json
{
  "sprint": "Sprint 6",
  "total_models": 10,
  "models": [
    {
      "model_name": "trig",
      "gms_file": "trig.gms",
      "parse_status": "SUCCESS",
      "parse_error": null,
      "parse_error_type": null
    },
    {
      "model_name": "circle",
      "gms_file": "circle.gms",
      "parse_status": "FAILED",
      "parse_error": "Unexpected token...",
      "parse_error_type": "UnexpectedToken"
    }
  ],
  "kpis": {
    "total_models": 10,
    "parse_success": 6,
    "parse_failed": 4,
    "parse_rate_percent": 60.0,
    "convert_success": 0,
    "convert_failed": 0,
    "convert_rate_percent": 0.0,
    "solve_success": 0,
    "solve_failed": 0,
    "solve_rate_percent": 0.0,
    "sprint6_target_models": 10,
    "sprint6_target_parse_rate": 10.0,
    "sprint6_target_convert_rate": 50.0,
    "meets_sprint6_targets": true
  }
}
```

### Field Descriptions

**Model Fields:**
- `model_name`: Base name of the model (without .gms extension)
- `gms_file`: Filename of the GAMS source
- `parse_status`: "SUCCESS" or "FAILED"
- `parse_error`: Error message (null if success)
- `parse_error_type`: Exception class name (null if success)

**KPI Fields:**
- `total_models`: Number of models processed
- `parse_success`: Models that parsed successfully
- `parse_failed`: Models that failed parsing
- `parse_rate_percent`: Parse success rate (0-100)
- `convert_*`: Conversion metrics (Sprint 6: all 0)
- `solve_*`: Solving metrics (Sprint 6: all 0)
- `meets_sprint6_targets`: Boolean indicating if targets met

## Future Enhancements

### Sprint 7
- Implement MCP conversion tracking
- Update Convert Rate metrics
- Add conversion error categorization

### Sprint 8+
- Implement PATH solving integration
- Update Solve Rate metrics
- Add solve error categorization
- E2E success tracking
- Historical trend charts
- Automated CI/CD ingestion

## References

- **Dashboard Design:** [`docs/research/dashboard_design.md`](../research/dashboard_design.md)
- **Ingestion Strategy:** [`docs/research/ingestion_schedule.md`](../research/ingestion_schedule.md)
- **Parse Error Analysis:** [`docs/research/gamslib_parse_errors.md`](../research/gamslib_parse_errors.md)
- **Sprint 6 Plan:** [`docs/planning/EPIC_2/SPRINT_6/PLAN.md`](../planning/EPIC_2/SPRINT_6/PLAN.md)

## Support

For issues or questions:
1. Check the dashboard "Failure Details" section for specific errors
2. Review error analysis in `docs/research/gamslib_parse_errors.md`
3. File GitHub issues for bugs or feature requests
4. See Sprint 6 planning documents for context and decisions
