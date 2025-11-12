# GAMS Model Library NLP Models

**Source:** https://www.gams.com/47.6/gamslib_ml/libhtml/  
**Purpose:** Test fixtures for Sprint 6 GAMSLib Bootstrapping  
**License:** GAMS Model Library (publicly available)

## Overview

This directory contains NLP (Nonlinear Programming) models downloaded from the GAMS Model Library for testing the nlp2mcp parser and MCP reformulation pipeline.

Models are organized into tiers based on complexity and parser compatibility:
- **Tier 1:** 10 simple models for initial Sprint 6 testing (70-90% expected parse success)
- **Tier 2:** 10 medium models for Sprint 7 (50-70% expected parse success)
- **Tier 3:** Complex models for future sprints (30-50% expected parse success)

## Usage

### Download Models

Download all Tier 1 models (10 models):
```bash
./scripts/download_gamslib_nlp.sh
```

Force re-download all models:
```bash
./scripts/download_gamslib_nlp.sh --force
```

Preview what would be downloaded:
```bash
./scripts/download_gamslib_nlp.sh --dry-run
```

Clean up downloaded files:
```bash
./scripts/download_gamslib_nlp.sh --clean
```

Show help:
```bash
./scripts/download_gamslib_nlp.sh --help
```

### Download Artifacts

After running the download script, you'll find:
- `<model>.gms` - GAMS source files
- `<model>.html` - Model documentation (when available)
- `manifest.csv` - Download manifest with file sizes and status
- `download.log` - Download log with timestamps and durations

## Tier 1 Model Manifest (Sprint 6 Target)

| # | Name | Description | Type | Size | Convexity | Status |
|---|------|-------------|------|------|-----------|--------|
| 1 | trig | Simple Trigonometric Example | NLP | Small | Non-convex | Not downloaded |
| 2 | rbrock | Rosenbrock Test Function | NLP | Small | Non-convex | Not downloaded |
| 3 | himmel16 | Area of Hexagon Test Problem | NLP | Small | Non-convex | Not downloaded |
| 4 | hs62 | Hock-Schittkowski Problem 62 | NLP | Small | Unknown | Not downloaded |
| 5 | mhw4d | Nonlinear Test Problem | NLP | Small | Non-convex | Not downloaded |
| 6 | mhw4dx | MHW4D with Additional Tests | NLP | Small | Non-convex | Not downloaded |
| 7 | circle | Circle Enclosing Points - SNOPT | NLP | Small | Convex | Not downloaded |
| 8 | maxmin | Max Min Location of Points | DNLP | Small | Non-convex | Not downloaded |
| 9 | mathopt1 | MathOptimizer Example 1 | NLP | Small | Unknown | Not downloaded |
| 10 | mingamma | Minimal y of GAMMA(x) | DNLP | Small | Unknown | Not downloaded |

**Expected Parse Success:** 7-9 out of 10 models (70-90%)

### Model Selection Rationale

Models selected for:
- **Simple syntax:** Parseable with current nlp2mcp capabilities
- **Small size:** <10 variables and equations for quick testing
- **Feature coverage:** Mix of trig functions, power functions, constraints
- **Convexity diversity:** Mix of convex and non-convex problems
- **Test value:** Well-known problems (Rosenbrock, Hock-Schittkowski, COPS 2.0)

### Known Issues

- **himmel16:** May have lag/lead operators (++), might need manual fixes
- **maxmin:** Involves min/max operations, tests our reformulation capability
- Some models may lack HTML documentation (script will warn but continue)

## Tier 2 Models (Future - Sprint 7)

Tier 2 includes 10 medium-complexity models:
- trigx, polygon, elec, chain, minsurf
- pool, haverly, mhw4dxx
- process, chem

See `docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md` for complete catalog.

## File Format

### manifest.csv

CSV format with columns:
- `name` - Model name (without .gms extension)
- `description` - Brief model description
- `gms_file` - Whether .gms file exists (true/false)
- `html_file` - Whether .html documentation exists (true/false)
- `gms_size_bytes` - Size of .gms file in bytes
- `download_status` - SUCCESS, INVALID, or NOT_DOWNLOADED

### download.log

CSV format with columns:
- `timestamp` - ISO 8601 timestamp (UTC)
- `model` - Model name
- `status` - SUCCESS, FAILED, or SKIPPED
- `message` - Status message
- `duration_seconds` - Download duration in seconds

## Model Verification

The download script validates each .gms file by checking for GAMS keywords:
- `Variable` or `Equation` or `Model` or `Solve`

Invalid files are automatically re-downloaded (up to 3 retry attempts).

## Integration with nlp2mcp

These models serve as test fixtures for:

1. **Parser Testing** - Validate GAMS syntax parsing
   ```bash
   python -m nlp2mcp tests/fixtures/gamslib/trig.gms
   ```

2. **Convexity Analysis** - Test convexity detection algorithms
   ```python
   from nlp2mcp.convexity import analyze_convexity
   result = analyze_convexity("tests/fixtures/gamslib/trig.gms")
   ```

3. **MCP Reformulation** - Validate KKT reformulation
   ```bash
   python -m nlp2mcp tests/fixtures/gamslib/rbrock.gms -o output/rbrock_mcp.gms
   ```

4. **Batch Testing** - Process all models for statistics
   ```bash
   for model in tests/fixtures/gamslib/*.gms; do
       python -m nlp2mcp "$model" -o "output/$(basename $model)"
   done
   ```

## Sprint 6 Success Metrics

Target KPIs from `EPIC_2/SPRINT_6/PREP_PLAN.md`:

- **Parse Success Rate:** ≥70% (7/10 models)
- **Convexity Detection:** Classify all 10 models as convex/non-convex
- **MCP Generation:** Generate valid MCP for ≥50% of parsed models
- **Download Time:** <5 minutes for all 10 models

## Notes

- Models are **unmodified** from GAMS Model Library
- Original .gms files preserved for reproducibility
- GAMS version **47.6** pinned for reproducible builds
- Models are **public domain** (GAMS Model Library license)
- Documentation (.html files) provide problem background and references

## Troubleshooting

### Download fails with "curl: command not found"

Install curl:
```bash
# macOS
brew install curl

# Ubuntu/Debian
sudo apt-get install curl
```

### Download fails with "connection timeout"

Retry with:
```bash
./scripts/download_gamslib_nlp.sh --force
```

The script automatically retries up to 3 times per model.

### Invalid .gms file format

If validation fails, the script will automatically retry. If it continues to fail:
1. Check the GAMS Model Library website is accessible
2. Verify the model exists in version 47.6
3. Try downloading manually from: https://www.gams.com/47.6/gamslib_ml/

### Script shows "Already exists" but files are corrupt

Re-download with:
```bash
./scripts/download_gamslib_nlp.sh --force
```

## References

- **GAMS Model Library:** https://www.gams.com/latest/gamslib_ml/
- **nlp2mcp Documentation:** `docs/`
- **Model Catalog:** `docs/planning/EPIC_2/SPRINT_6/GAMSLIB_NLP_CATALOG.md`
- **Sprint 6 Plan:** `docs/planning/EPIC_2/SPRINT_6/PREP_PLAN.md`

## Version History

- **2025-11-12:** Initial Tier 1 download infrastructure (10 models)
- Future: Tier 2 and Tier 3 expansions
