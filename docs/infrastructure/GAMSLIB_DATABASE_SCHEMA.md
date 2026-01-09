# GAMSLIB Database Schema Documentation

**Schema Version:** 2.0.0  
**Schema Standard:** JSON Schema Draft-07  
**Database File:** `data/gamslib/gamslib_status.json`  
**Schema File:** `data/gamslib/schema.json`

---

## Table of Contents

1. [Overview](#overview)
2. [Schema Structure](#schema-structure)
3. [Top-Level Fields](#top-level-fields)
4. [Model Entry Fields](#model-entry-fields)
5. [Pipeline Stage Results](#pipeline-stage-results)
6. [Error Representation](#error-representation)
7. [Validation](#validation)
8. [Workflow Guide](#workflow-guide)
9. [Examples](#examples)
10. [Migration from v1.0.0](#migration-from-v100)

---

## Overview

The GAMSLIB status database tracks the progress of GAMSLIB models through the nlp2mcp pipeline. Each model entry contains:

- **Basic metadata** (ID, name, type, description)
- **Convexity verification results** (Sprint 13)
- **Parse results** (nlp2mcp parsing stage)
- **Translation results** (MCP conversion stage)
- **Solve results** (MCP solver verification)

The database uses **JSON Schema Draft-07** for validation and follows semantic versioning (MAJOR.MINOR.PATCH).

---

## Schema Structure

The database has a moderate nesting structure (maximum 2 levels):

```
database
├── schema_version: "2.0.0"
├── created_date: ISO 8601 timestamp
├── updated_date: ISO 8601 timestamp
├── gams_version: "51.3.0" (optional)
├── total_models: integer count
└── models: array of model entries
    ├── Core fields (model_id, model_name, gamslib_type, ...)
    ├── convexity: object (convexity verification results)
    ├── nlp2mcp_parse: object (parsing results)
    ├── nlp2mcp_translate: object (translation results)
    └── mcp_solve: object (solve results)
```

**Design Rationale:**
- **Nested objects** group related fields by pipeline stage
- **Maximum 2 levels** maintains simplicity and query efficiency
- **Optional stage objects** allow incremental population as models progress
- **Required `status` field** within each stage enables filtering/querying

---

## Top-Level Fields

These fields describe the database as a whole.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `schema_version` | string | **Yes** | Semantic version (e.g., "2.0.0"). Pattern: `^\d+\.\d+\.\d+$` |
| `created_date` | string | No | ISO 8601 timestamp when database was first created |
| `updated_date` | string | No | ISO 8601 timestamp of last modification |
| `gams_version` | string | No | GAMS version used to source models (e.g., "51.3.0") |
| `total_models` | integer | No | Total count of models in the database (≥ 0) |
| `models` | array | **Yes** | Array of model entry objects |

### Example

```json
{
  "schema_version": "2.0.0",
  "created_date": "2026-01-01T00:00:00Z",
  "updated_date": "2026-01-08T15:30:00Z",
  "gams_version": "51.3.0",
  "total_models": 219,
  "models": [...]
}
```

---

## Model Entry Fields

Each model entry has **17 possible fields**, with only 3 required at creation time.

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model_id` | string | **Yes** | Unique identifier (matches filename without .gms extension) |
| `sequence_number` | integer | No | Original sequence number in GAMSLIB (≥ 1) |
| `model_name` | string | **Yes** | Human-readable name of the model |
| `gamslib_type` | string | **Yes** | GAMS model type (see enum values below) |
| `source_url` | string (URI) | No | URL to download the raw .gms file |
| `web_page_url` | string (URI) | No | URL to the GAMSLIB documentation page |
| `description` | string | No | Brief description of the model |
| `keywords` | array[string] | No | Keywords/tags for the model |
| `download_status` | string | No | Download status: "downloaded", "failed", "pending" |
| `download_date` | string | No | ISO 8601 timestamp when model was downloaded |
| `file_path` | string | No | Relative path to the downloaded .gms file |
| `file_size_bytes` | integer | No | Size of the .gms file in bytes (≥ 0) |
| `notes` | string | No | Free-form notes about the model |
| `migrated_from` | string | No | Source file from migration (e.g., "catalog.json") |
| `migration_date` | string | No | ISO 8601 timestamp when entry was migrated |

### GAMS Model Types

The `gamslib_type` field must be one of these enum values:

- **LP** - Linear Programming
- **NLP** - Nonlinear Programming
- **QCP** - Quadratically Constrained Program
- **MIP** - Mixed Integer Programming
- **MINLP** - Mixed Integer Nonlinear Programming
- **MIQCP** - Mixed Integer Quadratically Constrained Program
- **MCP** - Mixed Complementarity Problem
- **CNS** - Constrained Nonlinear System
- **DNLP** - Nonlinear Programming with Discontinuous Derivatives
- **MPEC** - Mathematical Program with Equilibrium Constraints
- **RMPEC** - Relaxed Mathematical Program with Equilibrium Constraints
- **EMP** - Extended Mathematical Programming

### Minimal Valid Entry

Only 3 fields are required to create a valid model entry:

```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  "gamslib_type": "LP"
}
```

---

## Pipeline Stage Results

Each pipeline stage has its own nested object with a common pattern:
- **Required `status` field** - Enables filtering and querying
- **Optional metadata fields** - Timestamps, versions, metrics
- **Optional error field** - Structured error information

### Convexity Verification (`convexity`)

Results from convexity verification (Sprint 13).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | **Yes** | Verification status (see enum below) |
| `verification_date` | string | No | ISO 8601 timestamp when verification was performed |
| `solver` | string | No | Solver used (e.g., "CONOPT", "IPOPT") |
| `solver_status` | integer | No | GAMS solver status code (1 = normal completion) |
| `model_status` | integer | No | GAMS model status code (1 = optimal, 2 = locally optimal) |
| `objective_value` | number | No | Optimal objective value from solve |
| `solve_time_seconds` | number | No | Time to solve in seconds (≥ 0) |
| `error` | string | No | Error message if status is "error" or "license_limited" |

**Status Values:**

- `verified_convex` - Confirmed convex (model_status = 1, globally optimal)
- `likely_convex` - Probably convex (model_status = 2, locally optimal from multiple starts)
- `locally_optimal` - Only locally optimal solution found
- `infeasible` - Model is infeasible
- `unbounded` - Model is unbounded
- `error` - Solver or execution error
- `excluded` - Excluded from testing (e.g., MIP, MINLP)
- `license_limited` - Exceeds demo license limits
- `unknown` - Status cannot be determined
- `not_tested` - Not yet tested (default)

**Example:**

```json
{
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2025-12-15T10:30:00Z",
    "solver": "CONOPT",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": 153.675,
    "solve_time_seconds": 0.12
  }
}
```

### Parse Results (`nlp2mcp_parse`)

Results from the nlp2mcp parsing stage.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | **Yes** | Parse status (see enum below) |
| `parse_date` | string | No | ISO 8601 timestamp when parsing was performed |
| `nlp2mcp_version` | string | No | Version of nlp2mcp used (e.g., "0.10.0") |
| `parse_time_seconds` | number | No | Time to parse in seconds (≥ 0) |
| `variables_count` | integer | No | Number of variables extracted (≥ 0) |
| `equations_count` | integer | No | Number of equations extracted (≥ 0) |
| `error` | object | No | Structured error details (see Error Representation) |

**Status Values:**

- `success` - Parsed successfully
- `failure` - Parse failed completely
- `partial` - Partial parse (some features unsupported but model extracted)
- `not_tested` - Not yet tested (default)

**Example (Success):**

```json
{
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T14:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.45,
    "variables_count": 12,
    "equations_count": 8
  }
}
```

**Example (Failure):**

```json
{
  "nlp2mcp_parse": {
    "status": "failure",
    "parse_date": "2026-01-02T14:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.12,
    "error": {
      "category": "syntax_error",
      "message": "Unexpected token 'loop' at line 42",
      "line": 42,
      "column": 15
    }
  }
}
```

### Translation Results (`nlp2mcp_translate`)

Results from the MCP translation stage.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | **Yes** | Translation status (see enum below) |
| `translate_date` | string | No | ISO 8601 timestamp when translation was performed |
| `nlp2mcp_version` | string | No | Version of nlp2mcp used (e.g., "0.10.0") |
| `translate_time_seconds` | number | No | Time to translate in seconds (≥ 0) |
| `mcp_variables_count` | integer | No | Number of variables in MCP formulation (≥ 0) |
| `mcp_equations_count` | integer | No | Number of equations in MCP formulation (≥ 0) |
| `output_file` | string | No | Relative path to generated MCP .gms file |
| `error` | object | No | Structured error details (see Error Representation) |

**Status Values:**

- `success` - Translated successfully to MCP format
- `failure` - Translation failed
- `not_tested` - Not yet tested (default)

**Example:**

```json
{
  "nlp2mcp_translate": {
    "status": "success",
    "translate_date": "2026-01-02T14:01:00Z",
    "nlp2mcp_version": "0.10.0",
    "translate_time_seconds": 1.23,
    "mcp_variables_count": 24,
    "mcp_equations_count": 24,
    "output_file": "data/gamslib/mcp/alkyl_mcp.gms"
  }
}
```

### Solve Results (`mcp_solve`)

Results from solving the MCP reformulation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | **Yes** | Solve status (see enum below) |
| `solve_date` | string | No | ISO 8601 timestamp when solve was performed |
| `solver` | string | No | MCP solver used (e.g., "PATH") |
| `solver_status` | integer | No | GAMS solver status code |
| `model_status` | integer | No | GAMS model status code |
| `objective_value` | number | No | Objective value from MCP solve |
| `solve_time_seconds` | number | No | Time to solve MCP in seconds (≥ 0) |
| `objective_match` | boolean | No | True if MCP objective matches original NLP within tolerance |
| `tolerance` | number | No | Tolerance used for objective comparison (≥ 0) |
| `error` | object | No | Structured error details (see Error Representation) |

**Status Values:**

- `success` - MCP solved successfully, objectives match original NLP
- `failure` - MCP solve failed
- `mismatch` - MCP solved but objectives don't match original NLP
- `not_tested` - Not yet tested (default)

**Example:**

```json
{
  "mcp_solve": {
    "status": "success",
    "solve_date": "2026-01-02T14:02:00Z",
    "solver": "PATH",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": 1768.807,
    "solve_time_seconds": 0.34,
    "objective_match": true,
    "tolerance": 1e-6
  }
}
```

---

## Error Representation

All pipeline stages use a common structured error format.

### Error Detail Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | **Yes** | Error category for classification (see enum below) |
| `message` | string | **Yes** | Human-readable error message |
| `line` | integer | No | Line number where error occurred (≥ 1, for parse errors) |
| `column` | integer | No | Column number where error occurred (≥ 1, for parse errors) |
| `details` | string | No | Additional error details or stack trace |

### Error Categories

- `syntax_error` - Parser grammar failure or invalid GAMS syntax
- `unsupported_feature` - Valid GAMS feature not yet supported by nlp2mcp
- `missing_include` - $include file not found or cannot be loaded
- `timeout` - Operation exceeded time limit
- `solver_error` - Solver execution error
- `validation_error` - Model structure validation failure
- `internal_error` - Unexpected internal error (bug in nlp2mcp)

### Example

```json
{
  "error": {
    "category": "unsupported_feature",
    "message": "Function 'gamma' is not yet implemented in nlp2mcp",
    "line": 85,
    "column": 22,
    "details": "Supported functions: exp, log, log10, log2, sqrt, sin, cos, tan, power, min, max"
  }
}
```

---

## Validation

The database is validated against `data/gamslib/schema.json` using JSON Schema Draft-07.

### Validation Features

- **Strict validation** with `additionalProperties: false` at all levels
- **Type checking** for all fields (string, integer, number, boolean, array, object)
- **Enum validation** for status values and GAMS model types
- **Format validation** for URIs and version strings
- **Range validation** for numeric fields (e.g., counts ≥ 0)

### Validation Commands

**Validate entire database:**

```bash
python scripts/gamslib/db_manager.py validate
```

**Validate with custom schema:**

```bash
python scripts/gamslib/db_manager.py validate --schema path/to/schema.json
```

**Expected output (success):**

```
Validating data/gamslib/gamslib_status.json against schema...
  Schema version: 2.0.0
  Models to validate: 219

Validation PASSED
  All 219 entries are valid
```

**Expected output (failure):**

```
Validating data/gamslib/gamslib_status.json against schema...
  Schema version: 2.0.0
  Models to validate: 219

Validation FAILED with 3 errors:
  models.0.gamslib_type: 'INVALID_TYPE' is not one of ['LP', 'NLP', ...]
  models.5.nlp2mcp_parse.status: 'pending' is not one of ['success', 'failure', 'partial', 'not_tested']
  models.10.convexity.solve_time_seconds: -1.0 is less than the minimum of 0
```

### Validation in Update Operations

The `db_manager.py update` command automatically validates changes before saving:

```bash
# This will validate the change against the schema
python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success
```

If validation fails, the update is aborted and the database remains unchanged.

---

## Workflow Guide

This section describes the standard workflow for processing GAMSLIB models through the nlp2mcp pipeline.

### Standard Pipeline Workflow

```
1. Initialize Database
   ↓
2. Batch Parse (nlp2mcp parse)
   ↓
3. Batch Translate (nlp2mcp translate)
   ↓
4. Query/Export Results
```

### Step 1: Initialize Database

Create the database from the catalog.json migration:

```bash
# Initialize from catalog.json (migration)
python scripts/gamslib/db_manager.py init

# Or create empty database
python scripts/gamslib/db_manager.py init --empty

# Force overwrite existing database (creates backup)
python scripts/gamslib/db_manager.py init --force
```

**What happens:**
- Reads `data/gamslib/catalog.json`
- Migrates to new schema v2.0.0
- Creates `data/gamslib/gamslib_status.json`
- Validates against schema before saving

### Step 2: Batch Parse

Parse all candidate models (verified_convex + likely_convex):

```bash
# Parse all candidate models
python scripts/gamslib/batch_parse.py

# Parse with verbose output
python scripts/gamslib/batch_parse.py --verbose

# Test with first 5 models only
python scripts/gamslib/batch_parse.py --limit 5

# Parse a single model
python scripts/gamslib/batch_parse.py --model alkyl

# Dry run (show what would be done)
python scripts/gamslib/batch_parse.py --dry-run
```

**What happens:**
- Creates backup of database
- Finds all models with `convexity.status` = "verified_convex" or "likely_convex"
- Runs `nlp2mcp parse` on each model
- Updates `nlp2mcp_parse` field with results
- Saves database every 10 models (configurable with `--save-every`)
- Prints summary statistics

**Example output:**

```
Loading database from data/gamslib/gamslib_status.json
Found 45 candidate models (verified_convex + likely_convex)
nlp2mcp version: 0.10.0
Created backup: data/gamslib/archive/20260102_140000_gamslib_status.json

[  1/ 45]   2% Processing alkyl... (0 success, 0 failure, ~180s remaining)
[ 10/ 45]  22% Processing prodmix... (8 success, 2 failure, ~150s remaining)
...

BATCH PARSE SUMMARY
============================================================
Models processed: 45/45
  Success: 38 (84.4%)
  Failure: 7 (15.6%)
  Skipped: 0

Total time: 156.3s
Average time per model: 3.47s

Error categories:
  syntax_error: 5 (71%)
  unsupported_feature: 2 (29%)

Successful models (38):
  - alkyl
  - bearing
  ...
============================================================
```

### Step 3: Batch Translate

Translate all successfully parsed models to MCP format:

```bash
# Translate all successfully parsed models
python scripts/gamslib/batch_translate.py

# Translate with verbose output
python scripts/gamslib/batch_translate.py --verbose

# Test with first 3 models only
python scripts/gamslib/batch_translate.py --limit 3

# Translate a single model
python scripts/gamslib/batch_translate.py --model alkyl

# Dry run
python scripts/gamslib/batch_translate.py --dry-run
```

**What happens:**
- Creates backup of database
- Finds all models with `nlp2mcp_parse.status` = "success"
- Runs `nlp2mcp translate` on each model
- Generates MCP output files in `data/gamslib/mcp/`
- Updates `nlp2mcp_translate` field with results
- Saves database every 5 models (configurable with `--save-every`)
- Prints summary statistics

### Step 4: Query and Export

**List all models:**

```bash
# Summary view (default)
python scripts/gamslib/db_manager.py list

# Verbose view with model details
python scripts/gamslib/db_manager.py list --verbose

# Filter by type
python scripts/gamslib/db_manager.py list --type NLP

# Limit results
python scripts/gamslib/db_manager.py list --limit 10

# JSON output
python scripts/gamslib/db_manager.py list --format json

# Count only
python scripts/gamslib/db_manager.py list --format count
```

**Get model details:**

```bash
# Get full model details (table format)
python scripts/gamslib/db_manager.py get trnsport

# JSON output
python scripts/gamslib/db_manager.py get trnsport --format json

# Get specific field (supports dot notation)
python scripts/gamslib/db_manager.py get trnsport --field convexity.status
python scripts/gamslib/db_manager.py get trnsport --field nlp2mcp_parse.variables_count
```

**Update model fields:**

```bash
# Update a single field
python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success

# Update multiple fields
python scripts/gamslib/db_manager.py update trnsport \
  --set nlp2mcp_parse.status=success \
  --set nlp2mcp_parse.variables_count=6
```

### Backup and Recovery

**Automatic backups:**
- Created automatically before:
  - `init --force` (overwriting existing database)
  - `update` operations
  - Batch operations (`batch_parse.py`, `batch_translate.py`)
- Stored in `data/gamslib/archive/`
- Timestamped format: `YYYYMMDD_HHMMSS_gamslib_status.json`
- Maximum 10 backups kept (oldest automatically pruned)

**Manual restore:**

```bash
# List available backups
ls -lt data/gamslib/archive/

# Restore from backup
cp data/gamslib/archive/20260102_140000_gamslib_status.json data/gamslib/gamslib_status.json

# Validate restored database
python scripts/gamslib/db_manager.py validate
```

### Adding New Pipeline Stages

To add a new pipeline stage (e.g., `mcp_solve`):

1. **Update schema** (`data/gamslib/schema.json`):
   - Add new object definition (e.g., `solve_result`)
   - Add to `model_entry.properties`
   - Define status enum values
   - Add required fields and optional metadata

2. **Create batch processing script** (e.g., `scripts/gamslib/batch_solve.py`):
   - Load database
   - Find candidate models (e.g., `nlp2mcp_translate.status = "success"`)
   - Process each model
   - Update database with results
   - Save periodically

3. **Test and validate**:
   - Run on subset with `--limit`
   - Validate database after updates
   - Check error categorization

4. **Update documentation**:
   - Add stage to this document
   - Update workflow guide
   - Add examples

---

## Examples

### Complete Model Entry (All Stages)

```json
{
  "model_id": "alkyl",
  "sequence_number": 1,
  "model_name": "Alkylation Process Optimization",
  "gamslib_type": "NLP",
  "source_url": "https://www.gams.com/latest/gamslib_ml/alkyl.1",
  "web_page_url": "https://www.gams.com/latest/gamslib_ml/libhtml/alkyl.html",
  "description": "Optimization of an alkylation process",
  "keywords": ["chemical-engineering", "process-optimization", "nonlinear"],
  "download_status": "downloaded",
  "download_date": "2025-12-01T10:00:00Z",
  "file_path": "data/gamslib/raw/alkyl.gms",
  "file_size_bytes": 4521,
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2025-12-15T10:30:00Z",
    "solver": "CONOPT",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": -1768.807,
    "solve_time_seconds": 0.15
  },
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T14:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.52,
    "variables_count": 12,
    "equations_count": 8
  },
  "nlp2mcp_translate": {
    "status": "success",
    "translate_date": "2026-01-02T14:01:00Z",
    "nlp2mcp_version": "0.10.0",
    "translate_time_seconds": 1.23,
    "mcp_variables_count": 24,
    "mcp_equations_count": 24,
    "output_file": "data/gamslib/mcp/alkyl_mcp.gms"
  },
  "mcp_solve": {
    "status": "success",
    "solve_date": "2026-01-02T14:02:00Z",
    "solver": "PATH",
    "solver_status": 1,
    "model_status": 1,
    "objective_value": -1768.807,
    "solve_time_seconds": 0.34,
    "objective_match": true,
    "tolerance": 1e-6
  }
}
```

### Model with Parse Error

```json
{
  "model_id": "badmodel",
  "model_name": "Model with Unsupported Function",
  "gamslib_type": "NLP",
  "convexity": {
    "status": "verified_convex",
    "verification_date": "2025-12-15T11:00:00Z",
    "solver": "CONOPT",
    "solver_status": 1,
    "model_status": 1
  },
  "nlp2mcp_parse": {
    "status": "failure",
    "parse_date": "2026-01-02T14:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.08,
    "error": {
      "category": "unsupported_feature",
      "message": "Function 'gamma' is not yet implemented in nlp2mcp",
      "line": 85,
      "column": 22,
      "details": "Supported functions: exp, log, log10, log2, sqrt, sin, cos, tan, power, min, max"
    }
  }
}
```

### Incremental Model (Parse Only)

```json
{
  "model_id": "inprogress",
  "model_name": "Model In Progress",
  "gamslib_type": "NLP",
  "convexity": {
    "status": "likely_convex",
    "verification_date": "2025-12-15T12:00:00Z",
    "solver": "IPOPT",
    "solver_status": 1,
    "model_status": 2
  },
  "nlp2mcp_parse": {
    "status": "success",
    "parse_date": "2026-01-02T14:00:00Z",
    "nlp2mcp_version": "0.10.0",
    "parse_time_seconds": 0.45,
    "variables_count": 20,
    "equations_count": 15
  }
}
```

Note: Translation and solve stages are absent, indicating the model hasn't reached those stages yet.

---

## Migration from v1.0.0

The schema v2.0.0 represents a major restructuring from the v1.0.0 `catalog.json` format.

### Major Changes

1. **Database filename** changed from `catalog.json` to `gamslib_status.json`
2. **Schema version** bumped from 1.0.0 to 2.0.0
3. **Convexity fields** moved from flat structure to nested `convexity` object
4. **New pipeline stages** added: `nlp2mcp_parse`, `nlp2mcp_translate`, `mcp_solve`
5. **Structured errors** replace plain error strings
6. **Strict validation** with `additionalProperties: false`

### Field Mapping

| catalog.json (v1.0.0) | gamslib_status.json (v2.0.0) |
|----------------------|------------------------------|
| `convexity_status` | `convexity.status` |
| `verification_date` | `convexity.verification_date` |
| `solver_status` | `convexity.solver_status` |
| `model_status` | `convexity.model_status` |
| `objective_value` | `convexity.objective_value` |
| `solve_time_seconds` | `convexity.solve_time_seconds` |
| `verification_error` | `convexity.error` |

### Migration Script

The migration is performed automatically by `db_manager.py init`:

```bash
# Migrate from catalog.json to gamslib_status.json
python scripts/gamslib/db_manager.py init

# The migration:
# 1. Reads data/gamslib/catalog.json
# 2. Converts flat structure to nested structure
# 3. Adds schema metadata (schema_version, migration_date)
# 4. Validates against schema.json
# 5. Writes to data/gamslib/gamslib_status.json
```

**Manual migration:**

```python
from scripts.gamslib.migrate_catalog import load_catalog, migrate_catalog
from datetime import datetime, UTC

# Load old catalog
catalog = load_catalog("data/gamslib/catalog.json")

# Migrate to new schema
migration_date = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
database = migrate_catalog(catalog, migration_date)

# Save to new location
from scripts.gamslib.db_manager import save_database
save_database(database, "data/gamslib/gamslib_status.json")
```

### Compatibility Notes

- **No backward compatibility** - v2.0.0 is a breaking change
- **Old scripts** that read `catalog.json` will need updates
- **Migration metadata** is preserved in `migrated_from` and `migration_date` fields
- **Validation** ensures all migrated data conforms to new schema

---

## Additional Resources

- **Schema file:** `data/gamslib/schema.json`
- **Design rationale:** `docs/planning/EPIC_3/SPRINT_14/SCHEMA_DESIGN_NOTES.md`
- **Database manager:** `scripts/gamslib/db_manager.py`
- **Batch parsing:** `scripts/gamslib/batch_parse.py`
- **Batch translation:** `scripts/gamslib/batch_translate.py`

For questions or issues, consult the Sprint 14 documentation or create an issue.
