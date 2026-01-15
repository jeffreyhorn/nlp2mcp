# GAMSLIB Testing Guide

This guide explains how to run the full nlp2mcp pipeline tests against the GAMSLIB corpus.

## Prerequisites

- GAMS 51.3.0+ installed and on PATH
- PATH solver license (included with GAMS)
- Python 3.10+
- nlp2mcp package installed

```bash
# Verify setup
gams --version
python -c "import nlp2mcp; print(nlp2mcp.__version__)"
```

## Quick Start

### Run Full Pipeline Test

```bash
# Run all stages (parse → translate → solve → compare)
python scripts/gamslib/run_full_test.py

# With JSON output for CI/automation
python scripts/gamslib/run_full_test.py --json

# Verbose output with progress
python scripts/gamslib/run_full_test.py --verbose
```

### Run Individual Stages

```bash
# Parse only
python scripts/gamslib/batch_parse.py

# Translate only (requires successful parse)
python scripts/gamslib/batch_translate.py

# Solve only (requires successful translate)
python scripts/gamslib/batch_solve.py

# Compare only (requires successful solve)
python scripts/gamslib/batch_compare.py
```

## Test Scripts

### run_full_test.py

The main test orchestrator that runs all pipeline stages sequentially.

```bash
# Basic usage
python scripts/gamslib/run_full_test.py

# Options
python scripts/gamslib/run_full_test.py --json        # JSON output
python scripts/gamslib/run_full_test.py --verbose     # Detailed progress
python scripts/gamslib/run_full_test.py --dry-run     # Preview without running
```

**Output:**
```
=== GAMSLIB Full Pipeline Test ===

Stage 1: Parse (GAMS → AST)
  Processing 160 models...
  Success: 34 (21.3%)
  Failed: 126 (78.7%)

Stage 2: Translate (AST → MCP)
  Processing 34 models...
  Success: 17 (50.0%)
  Failed: 17 (50.0%)

Stage 3: Solve (MCP Execution)
  Processing 17 models...
  Success: 3 (17.6%)
  Failed: 14 (82.4%)

Stage 4: Compare (Solution Validation)
  Processing 3 models...
  Matched: 1 (33.3%)
  Mismatched: 2 (66.7%)

=== Summary ===
Full pipeline success: 1/160 (0.6%)
Successful model: hs62
```

### batch_parse.py

Parses GAMS models to AST using nlp2mcp.

```bash
# Parse all models
python scripts/gamslib/batch_parse.py

# Parse specific model
python scripts/gamslib/batch_parse.py --model hs62

# Force re-parse (skip cache)
python scripts/gamslib/batch_parse.py --force

# With timeout per model
python scripts/gamslib/batch_parse.py --timeout 30
```

### batch_translate.py

Translates parsed AST to MCP format.

```bash
# Translate all parsed models
python scripts/gamslib/batch_translate.py

# Translate specific model
python scripts/gamslib/batch_translate.py --model hs62

# Force re-translate
python scripts/gamslib/batch_translate.py --force
```

### batch_solve.py

Solves translated MCP files using PATH solver.

```bash
# Solve all translated models
python scripts/gamslib/batch_solve.py

# Solve specific model
python scripts/gamslib/batch_solve.py --model hs62

# With custom timeout
python scripts/gamslib/batch_solve.py --timeout 120
```

### batch_compare.py

Compares nlp2mcp solutions with GAMS reference solutions.

```bash
# Compare all solved models
python scripts/gamslib/batch_compare.py

# Compare specific model
python scripts/gamslib/batch_compare.py --model hs62

# With custom tolerance
python scripts/gamslib/batch_compare.py --tolerance 1e-4
```

## Database Queries

The test results are stored in `data/gamslib/gamslib_status.json`.

### Query Parse Results

```bash
# List all successfully parsed models
python scripts/gamslib/db_manager.py list --parse-status success

# Get parse details for a model
python scripts/gamslib/db_manager.py get hs62 --field nlp2mcp_parse

# Count by parse status
python scripts/gamslib/db_manager.py stats --stage parse
```

### Query Translate Results

```bash
# List translated models
python scripts/gamslib/db_manager.py list --translate-status success

# Get translate errors
python scripts/gamslib/db_manager.py list --translate-status error --format json
```

### Query Solve Results

```bash
# List solved models
python scripts/gamslib/db_manager.py list --solve-status success

# Get solve timing
python scripts/gamslib/db_manager.py get hs62 --field nlp2mcp_solve.timing_ms
```

### Query Compare Results

```bash
# List matched models
python scripts/gamslib/db_manager.py list --compare-status match

# Get comparison details
python scripts/gamslib/db_manager.py get hs62 --field nlp2mcp_compare
```

## Python API

### Run Tests Programmatically

```python
from scripts.gamslib.run_full_test import run_full_pipeline
from scripts.gamslib.db_manager import load_database

# Run full pipeline
results = run_full_pipeline(verbose=True)
print(f"Parse success: {results['parse']['success']}")
print(f"Translate success: {results['translate']['success']}")
print(f"Solve success: {results['solve']['success']}")
print(f"Compare matched: {results['compare']['matched']}")

# Query results from database
db = load_database()
for model in db["models"]:
    parse = model.get("nlp2mcp_parse", {})
    if parse.get("status") == "success":
        print(f"{model['model_id']}: parsed successfully")
```

### Test Individual Models

```python
from scripts.gamslib.batch_parse import parse_model
from scripts.gamslib.batch_translate import translate_model
from scripts.gamslib.batch_solve import solve_model
from scripts.gamslib.batch_compare import compare_solution

# Test a single model through the pipeline
model_id = "hs62"

# Parse
parse_result = parse_model(model_id)
if parse_result["status"] == "success":
    print(f"Parsed: {parse_result['variables_count']} variables")
    
    # Translate
    translate_result = translate_model(model_id)
    if translate_result["status"] == "success":
        print(f"Translated: {translate_result['mcp_path']}")
        
        # Solve
        solve_result = solve_model(model_id)
        if solve_result["status"] == "success":
            print(f"Solved: objective = {solve_result['objective_value']}")
            
            # Compare
            compare_result = compare_solution(model_id)
            print(f"Compare: {compare_result['status']}")
```

## Unit Tests

### Run pytest Tests

```bash
# Run all GAMSLIB-related tests
pytest tests/test_gamslib/ -v

# Run specific test file
pytest tests/test_gamslib/test_parse.py -v
pytest tests/test_gamslib/test_translate.py -v
pytest tests/test_gamslib/test_solve.py -v
pytest tests/test_gamslib/test_compare.py -v

# Run with coverage
pytest tests/test_gamslib/ --cov=scripts/gamslib --cov-report=term-missing
```

### Test File Structure

```
tests/test_gamslib/
├── test_parse.py      # Parse stage tests
├── test_translate.py  # Translate stage tests
├── test_solve.py      # Solve stage tests
├── test_compare.py    # Compare stage tests
└── conftest.py        # Shared fixtures
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: GAMSLIB Pipeline Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: pip install -e ".[dev]"
        
      - name: Run pipeline tests
        run: python scripts/gamslib/run_full_test.py --json
        
      - name: Run unit tests
        run: pytest tests/test_gamslib/ -v
```

### JSON Output Format

The `--json` flag produces machine-readable output:

```json
{
  "timestamp": "2025-01-15T12:00:00Z",
  "stages": {
    "parse": {
      "total": 160,
      "success": 34,
      "failed": 126,
      "rate": 0.2125
    },
    "translate": {
      "total": 34,
      "success": 17,
      "failed": 17,
      "rate": 0.5
    },
    "solve": {
      "total": 17,
      "success": 3,
      "failed": 14,
      "rate": 0.176
    },
    "compare": {
      "total": 3,
      "matched": 1,
      "mismatched": 2,
      "rate": 0.333
    }
  },
  "full_pipeline": {
    "success": 1,
    "total": 160,
    "rate": 0.006,
    "models": ["hs62"]
  }
}
```

## Performance Benchmarks

### Current Baseline (Sprint 15)

| Stage | Success Rate | Mean Time |
|-------|--------------|-----------|
| Parse | 21.3% (34/160) | 141.5 ms |
| Translate | 50.0% (17/34) | 3.7 ms |
| Solve | 17.6% (3/17) | 172.7 ms |
| Compare | 33.3% (1/3) | - |
| **Full Pipeline** | **0.6% (1/160)** | - |

### Timing Breakdown

```bash
# Get timing statistics
python scripts/gamslib/db_manager.py stats --timing

# Output:
# Parse timing (successful):
#   Mean: 141.5 ms, Median: 125.8 ms, P99: 421.4 ms
# Translate timing (successful):
#   Mean: 3.7 ms, Median: 3.7 ms, P99: 5.8 ms
# Solve timing (successful):
#   Mean: 172.7 ms, Median: 170.4 ms, P99: 184.0 ms
```

## Troubleshooting

### Common Errors

#### lexer_invalid_char (109 models)
The GAMS lexer encounters unsupported characters.
**Fix:** Improve lexer to handle extended GAMS syntax.

#### path_syntax_error (14 models)
The generated MCP has syntax issues for PATH solver.
**Fix:** Debug MCP output format for affected models.

#### model_no_objective_def (5 models)
The translator cannot find/extract the objective function.
**Fix:** Improve objective extraction logic.

### Debug Mode

```bash
# Run with debug output
DEBUG=1 python scripts/gamslib/run_full_test.py --verbose

# Check specific model
python scripts/gamslib/batch_parse.py --model problematic_model --debug
```

### Log Files

- Parse errors: `data/gamslib/logs/parse_errors.log`
- Translate errors: `data/gamslib/logs/translate_errors.log`
- Solve errors: `data/gamslib/logs/solve_errors.log`

## References

- [GAMSLIB_USAGE.md](GAMSLIB_USAGE.md) - Database and discovery guide
- [GAMSLIB_CONVERSION_STATUS.md](../status/GAMSLIB_CONVERSION_STATUS.md) - Current status dashboard
- [SPRINT_BASELINE.md](../planning/EPIC_3/SPRINT_15/SPRINT_BASELINE.md) - Sprint 15 baseline metrics
- [baseline_metrics.json](../../data/gamslib/baseline_metrics.json) - Machine-readable metrics
