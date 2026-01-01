# GAMSLIB Usage Guide

This guide explains how to use the GAMSLIB scripts for model discovery, download, and convexity verification.

## Prerequisites

- GAMS 51.3.0+ installed and on PATH
- Python 3.10+
- `gamslib` command available (comes with GAMS installation)

Verify GAMS installation:
```bash
gams --version
gamslib --help
```

## Directory Structure

```
data/gamslib/
├── catalog.json          # Model catalog with metadata
├── convexity_report.md   # Summary report of verification results
├── verification_results.json  # Detailed verification output
├── raw/                  # Downloaded .gms files
│   ├── trnsport.gms
│   ├── blend.gms
│   └── ...
└── mcp/                  # Generated MCP files (future)

scripts/gamslib/
├── discover_models.py    # Discover LP/NLP/QCP models
├── download_models.py    # Download models from GAMSLIB
└── verify_convexity.py   # Verify model convexity
```

## 1. Discover Models

The discovery script scans GAMSLIB for LP, NLP, and QCP models and populates the catalog.

### Usage

```bash
# Discover all models and update catalog
python scripts/gamslib/discover_models.py

# Preview discovery without updating catalog
python scripts/gamslib/discover_models.py --dry-run

# Verbose output
python scripts/gamslib/discover_models.py --verbose
```

### Output

- Updates `data/gamslib/catalog.json` with discovered models
- Generates `data/gamslib/discovery_report.md` with statistics

### Example Output

```
Discovering models from GAMSLIB...
Discovery complete!
  Total GAMSLIB models: 437
  Included: 219 (LP: 86, NLP: 120, QCP: 13)
  Excluded: 218
  Failed: 0

Catalog updated: 219 new models added
Report generated: data/gamslib/discovery_report.md
```

## 2. Download Models

The download script extracts models from GAMSLIB to the local filesystem.

### Usage

```bash
# Download all pending models
python scripts/gamslib/download_models.py --all

# Download specific model(s)
python scripts/gamslib/download_models.py --model trnsport
python scripts/gamslib/download_models.py --model trnsport --model blend

# Force re-download (overwrite existing)
python scripts/gamslib/download_models.py --all --force

# Preview what would be downloaded
python scripts/gamslib/download_models.py --all --dry-run

# Verbose output with progress
python scripts/gamslib/download_models.py --all --verbose
```

### Options

| Option | Description |
|--------|-------------|
| `--model MODEL` | Download specific model by ID (repeatable) |
| `--all` | Download all pending models from catalog |
| `--force` | Re-download even if file exists |
| `--dry-run` | Show what would be downloaded |
| `--verbose` | Show detailed progress |
| `--batch-size N` | Save catalog every N downloads (default: 10) |

### Output

- Downloads models to `data/gamslib/raw/`
- Updates catalog with download status, date, file path, and size
- Logs errors to `data/gamslib/download_errors.log`

## 3. Verify Convexity

The verification script runs GAMS models and classifies them by convexity.

### Usage

```bash
# Verify all downloaded models
python scripts/gamslib/verify_convexity.py --all

# Verify and update catalog
python scripts/gamslib/verify_convexity.py --all --update-catalog

# Verify specific model(s)
python scripts/gamslib/verify_convexity.py --model trnsport
python scripts/gamslib/verify_convexity.py --model trnsport --model blend

# Save results to JSON file
python scripts/gamslib/verify_convexity.py --all --output results.json

# Set custom timeout (default: 60 seconds)
python scripts/gamslib/verify_convexity.py --all --timeout 120

# Preview what would be verified
python scripts/gamslib/verify_convexity.py --all --dry-run
```

### Options

| Option | Description |
|--------|-------------|
| `--model MODEL` | Verify specific model by ID (repeatable) |
| `--all` | Verify all downloaded models |
| `--update-catalog` | Update catalog with verification results |
| `--output FILE` | Save results to JSON file |
| `--timeout SECS` | Timeout per model (default: 60) |
| `--verbose` | Show detailed progress |
| `--dry-run` | Show what would be verified |

### Classification

| Status | Description | Criteria |
|--------|-------------|----------|
| `verified_convex` | Proven convex | LP with MODEL STATUS 1 (Optimal) |
| `likely_convex` | Probably convex | NLP/QCP with STATUS 1 or 2 |
| `excluded` | Not in corpus | Infeasible, unbounded, wrong type |
| `error` | Verification failed | Timeout, license limit, compilation error |

### Example Output

```
Models to verify: 219
[1/219] Verifying trnsport (LP)...
  -> VERIFIED_CONVEX (objective=153.675)
[2/219] Verifying blend (LP)...
  -> VERIFIED_CONVEX (objective=4.98)
[3/219] Verifying circle (NLP)...
  -> LIKELY_CONVEX (objective=4.5742)
...

Verification Summary:
  Total verified: 219
  Verified convex (LP): 57
  Likely convex (NLP/QCP): 103
  Excluded: 4
  Errors: 55
```

## 4. Query the Catalog

The catalog is a JSON file that can be queried programmatically.

### Python Example

```python
import json
from pathlib import Path

# Load catalog
with open("data/gamslib/catalog.json") as f:
    catalog = json.load(f)

# Get all models
models = catalog["models"]
print(f"Total models: {len(models)}")

# Filter by type
lp_models = [m for m in models if m["gamslib_type"] == "LP"]
nlp_models = [m for m in models if m["gamslib_type"] == "NLP"]
print(f"LP models: {len(lp_models)}")
print(f"NLP models: {len(nlp_models)}")

# Filter by convexity status
verified = [m for m in models if m.get("convexity_status") == "verified_convex"]
likely = [m for m in models if m.get("convexity_status") == "likely_convex"]
print(f"Verified convex: {len(verified)}")
print(f"Likely convex: {len(likely)}")

# Get specific model
trnsport = next((m for m in models if m["model_id"] == "trnsport"), None)
if trnsport:
    print(f"trnsport objective: {trnsport.get('objective_value')}")
```

### Using the Catalog Dataclass

```python
from scripts.gamslib.catalog import GamslibCatalog

# Load catalog
catalog = GamslibCatalog.load(Path("data/gamslib/catalog.json"))

# Query methods
lp_models = catalog.get_models_by_type("LP")
downloaded = catalog.get_models_by_status("downloaded")
trnsport = catalog.get_model_by_id("trnsport")

# Update model
catalog.update_model("trnsport", notes="Classic transportation problem")
catalog.save(Path("data/gamslib/catalog.json"))
```

## 5. Common Workflows

### Full Pipeline (Discovery → Download → Verification)

```bash
# Step 1: Discover models
python scripts/gamslib/discover_models.py --verbose

# Step 2: Download all models
python scripts/gamslib/download_models.py --all --verbose

# Step 3: Verify convexity and update catalog
python scripts/gamslib/verify_convexity.py --all --update-catalog --output data/gamslib/verification_results.json
```

### Verify a Single Model

```bash
# Download and verify a specific model
python scripts/gamslib/download_models.py --model trnsport
python scripts/gamslib/verify_convexity.py --model trnsport --verbose
```

### Refresh Verification

```bash
# Re-verify all models (e.g., after GAMS update)
python scripts/gamslib/verify_convexity.py --all --update-catalog
```

## 6. Troubleshooting

### GAMS Not Found

```
Error: gamslib command not found - is GAMS installed and on PATH?
```

**Solution:** Add GAMS to your PATH:
```bash
export PATH="/path/to/gams:$PATH"
```

### License Limit Errors

```
Error: Model exceeds demo license limits
```

**Explanation:** The GAMS demo license has size limits (LP: 2000 rows/cols, NLP: 1000 rows/cols). Large models will fail with this error. A full GAMS license is required for these models.

### Compilation Errors

```
Error: GAMS compilation error
```

**Explanation:** Some GAMSLIB models require external include files or data files not present in the standalone .gms file. These models are marked as errors.

### No Solve Summary

```
Error: No solve summary found in listing file
```

**Explanation:** Some models demonstrate special features (async solves, grid computing, scenario management) and don't produce standard solve summaries.

## References

- [GAMSLIB Documentation](https://www.gams.com/latest/gamslib_ml/libhtml/index.html)
- [GAMS Model Solve](https://www.gams.com/latest/docs/UG_ModelSolve.html)
- [Model Status Codes](https://www.gams.com/latest/docs/UG_GAMSReturnCodes.html)
- `docs/research/GAMSLIB_MODEL_TYPES.md` - Model type documentation
- `data/gamslib/convexity_report.md` - Verification results summary
