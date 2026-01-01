# db_manager.py Design Document

**Task:** Sprint 14 Prep Task 7 - Review Existing db_manager Patterns  
**Created:** 2026-01-01  
**Status:** Design Complete

---

## Executive Summary

This document specifies the design for `scripts/gamslib/db_manager.py`, a CLI tool for managing the GAMSLIB status database (`gamslib_status.json`). The design follows patterns established by existing GAMSLIB scripts to ensure consistency and maintainability.

---

## Existing Script Pattern Analysis

### Scripts Reviewed

| Script | Purpose | Lines | Key Patterns |
|--------|---------|-------|--------------|
| `discover_models.py` | Populate catalog from GAMSLIB | ~280 | argparse, dataclasses, report generation |
| `download_models.py` | Download .gms files | ~290 | logging module, batch processing, dry-run |
| `verify_convexity.py` | Run GAMS convexity verification | ~480 | Complex result classification, JSON I/O |
| `src/gamslib/catalog.py` | Catalog dataclasses | ~230 | Dataclass patterns, load/save methods |

### Common CLI Patterns

**1. Argument Parser Setup**
```python
parser = argparse.ArgumentParser(
    description="Description of script",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
    python script.py --option value
    python script.py --all --verbose
    """,
)
```

**2. Standard Arguments**
| Argument | Short | Type | Purpose |
|----------|-------|------|---------|
| `--verbose` | `-v` | flag | Detailed output |
| `--dry-run` | `-n` | flag | Preview without changes |
| `--all` | `-a` | flag | Process all items |
| `--model` | `-m` | repeatable | Specific model(s) |
| `--output` | `-o` | path | Output file path |
| `--force` | `-f` | flag | Overwrite existing |

**3. Logging Configuration**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)
```

**4. Path Constants**
```python
PROJECT_ROOT = Path(__file__).parent.parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
```

**5. Result Dataclasses**
```python
@dataclass
class OperationResult:
    total_attempted: int = 0
    successful: int = 0
    failed: int = 0
    errors: list[tuple[str, str]] = field(default_factory=list)
```

**6. Exit Codes**
- `0`: Success
- `1`: Failure (errors occurred)
- No other codes used in existing scripts

### Error Handling Patterns

```python
# Validation at startup
if not CATALOG_PATH.exists():
    logger.error(f"Catalog not found at {CATALOG_PATH}")
    sys.exit(1)

# Error collection during batch
for item in items:
    try:
        process(item)
    except Exception as e:
        result.add_failure(item.id, str(e))
        logger.error(f"Failed to process {item.id}: {e}")

# Summary at end
if result.failed > 0:
    sys.exit(1)
```

### JSON I/O Patterns

```python
# Load
def load_database(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)

# Save with consistent formatting
def save_database(path: Path, data: dict) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # Trailing newline
```

---

## db_manager.py Subcommand Design

### Essential Subcommands (Sprint 14)

| Subcommand | Priority | Description |
|------------|----------|-------------|
| `init` | Critical | Initialize database from catalog.json |
| `get` | Critical | Get single model details |
| `update` | Critical | Update model field(s) |
| `query` | Critical | Query models by criteria |
| `list` | High | List all models with summary |
| `validate` | High | Validate database against schema |
| `export` | High | Export to CSV/Markdown |
| `stats` | Medium | Show database statistics |

### Nice-to-Have Subcommands (Future)

| Subcommand | Priority | Description |
|------------|----------|-------------|
| `backup` | Low | Manual backup creation |
| `restore` | Low | Restore from backup |
| `migrate` | Low | Schema migration |
| `diff` | Low | Compare two database files |

---

## Subcommand Specifications

### `db_manager.py init`

**Purpose:** Initialize gamslib_status.json from catalog.json

**Usage:**
```bash
python scripts/gamslib/db_manager.py init [--force] [--dry-run]
```

**Arguments:**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--force` | flag | false | Overwrite existing database |
| `--dry-run` | flag | false | Show what would be created |

**Behavior:**
1. Check if gamslib_status.json exists (fail if exists and no --force)
2. Load catalog.json
3. Transform entries to new schema format
4. Create backup of catalog.json before writing
5. Write gamslib_status.json with schema_version 2.0.0

**Output:**
```
Initializing gamslib_status.json from catalog.json...
  Source models: 219
  Migrated: 219
  Schema version: 2.0.0
Database initialized: data/gamslib/gamslib_status.json
```

---

### `db_manager.py get`

**Purpose:** Get details for a single model

**Usage:**
```bash
python scripts/gamslib/db_manager.py get MODEL_ID [--format json|yaml|table]
```

**Arguments:**
| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `MODEL_ID` | positional | required | Model identifier |
| `--format` | choice | table | Output format |

**Output (table):**
```
Model: trnsport
========================================
model_id:       trnsport
model_name:     A Transportation Problem
gamslib_type:   LP

Convexity:
  status:       verified_convex
  solver_status: 1
  model_status:  1

Parse:
  status:       not_tested
```

**Output (json):**
```json
{
  "model_id": "trnsport",
  "model_name": "A Transportation Problem",
  ...
}
```

---

### `db_manager.py update`

**Purpose:** Update field(s) for a model

**Usage:**
```bash
python scripts/gamslib/db_manager.py update MODEL_ID FIELD VALUE [--field FIELD VALUE ...]
```

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `MODEL_ID` | positional | Model identifier |
| `FIELD` | positional | Field path (dot notation) |
| `VALUE` | positional | New value |
| `--field` | repeatable | Additional field=value pairs |

**Examples:**
```bash
# Update parse status
python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success

# Update multiple fields
python scripts/gamslib/db_manager.py update trnsport \
  nlp2mcp_parse.status success \
  --field nlp2mcp_parse.parse_time_sec 0.05 \
  --field nlp2mcp_parse.nlp2mcp_version 0.10.0
```

**Behavior:**
1. Load database
2. Find model by ID (error if not found)
3. Validate field path exists in schema
4. Update field(s)
5. Validate updated entry against schema
6. Save database

---

### `db_manager.py query`

**Purpose:** Query models by criteria

**Usage:**
```bash
python scripts/gamslib/db_manager.py query [--type TYPE] [--convexity-status STATUS] \
  [--parse-status STATUS] [--translate-status STATUS] [--solve-status STATUS] \
  [--format json|table|count] [--limit N]
```

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `--type` | choice | Filter by gamslib_type (LP, NLP, QCP) |
| `--convexity-status` | choice | Filter by convexity status |
| `--parse-status` | choice | Filter by parse status |
| `--translate-status` | choice | Filter by translate status |
| `--solve-status` | choice | Filter by solve status |
| `--format` | choice | Output format (default: table) |
| `--limit` | int | Limit results |

**Examples:**
```bash
# All verified_convex models
python scripts/gamslib/db_manager.py query --convexity-status verified_convex

# LP models that parsed successfully
python scripts/gamslib/db_manager.py query --type LP --parse-status success

# Count only
python scripts/gamslib/db_manager.py query --parse-status success --format count
```

**Output (table):**
```
Query Results: 4 models
----------------------------------------
model_id    type   convexity        parse      translate
----------------------------------------
prodmix     LP     verified_convex  success    not_tested
rbrock      NLP    likely_convex    success    not_tested
hs62        NLP    likely_convex    success    not_tested
himmel11    QCP    likely_convex    success    not_tested
```

---

### `db_manager.py list`

**Purpose:** List all models with summary info

**Usage:**
```bash
python scripts/gamslib/db_manager.py list [--type TYPE] [--format table|json]
```

**Output:**
```
GAMSLIB Status Database: 219 models
========================================

By Type:
  LP:  57
  NLP: 153
  QCP: 9

By Convexity Status:
  verified_convex: 57
  likely_convex:   103
  excluded:        41
  error:           18

By Parse Status:
  success:    4
  failure:    26
  not_tested: 189
```

---

### `db_manager.py validate`

**Purpose:** Validate database against JSON schema

**Usage:**
```bash
python scripts/gamslib/db_manager.py validate [--schema PATH] [--verbose]
```

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `--schema` | path | Custom schema path (default: DRAFT_SCHEMA.json) |
| `--verbose` | flag | Show all validation errors |

**Output (success):**
```
Validating gamslib_status.json against schema...
  Schema version: 2.0.0
  Models validated: 219
  Errors: 0
Validation passed.
```

**Output (failure):**
```
Validating gamslib_status.json against schema...
  Schema version: 2.0.0
  Models validated: 219
  Errors: 3

Validation Errors:
  trnsport: convexity.status: 'invalid' is not one of [...]
  hs62: nlp2mcp_parse.status: 'unknown' is not valid
  ...

Validation failed.
```

---

### `db_manager.py export`

**Purpose:** Export database to different formats

**Usage:**
```bash
python scripts/gamslib/db_manager.py export --format csv|markdown|json \
  [--output PATH] [--fields FIELD,...] [--query ...]
```

**Arguments:**
| Argument | Type | Description |
|----------|------|-------------|
| `--format` | choice | Export format |
| `--output` | path | Output file (default: stdout) |
| `--fields` | list | Comma-separated field list |
| `--query` | flags | Same as query subcommand (filter before export) |

**Examples:**
```bash
# Export all to CSV
python scripts/gamslib/db_manager.py export --format csv -o models.csv

# Export successful parses to Markdown
python scripts/gamslib/db_manager.py export --format markdown \
  --parse-status success -o PARSE_SUCCESS.md

# Export specific fields
python scripts/gamslib/db_manager.py export --format csv \
  --fields model_id,gamslib_type,convexity.status,nlp2mcp_parse.status
```

---

### `db_manager.py stats`

**Purpose:** Show database statistics

**Usage:**
```bash
python scripts/gamslib/db_manager.py stats [--format table|json]
```

**Output:**
```
GAMSLIB Status Database Statistics
========================================
Database: data/gamslib/gamslib_status.json
Schema version: 2.0.0
Last updated: 2026-01-15T10:30:00Z
Total models: 219

Pipeline Summary:
-----------------------------------------
Stage           Success  Failure  Not Tested
-----------------------------------------
Convexity       160      41       18
Parse           4        26       189
Translate       0        0        219
Solve           0        0        219

Success Rates (tested only):
  Convexity: 79.6% (160/201)
  Parse:     13.3% (4/30)
  Translate: N/A (no tests)
  Solve:     N/A (no tests)
```

---

## Implementation Guidelines

### File Structure

```
scripts/gamslib/
├── db_manager.py          # Main CLI entry point
├── catalog.py             # Existing - model dataclasses (reuse)
└── db_manager/            # New package (optional)
    ├── __init__.py
    ├── commands.py        # Subcommand implementations
    ├── schema.py          # Schema validation
    └── export.py          # Export format handlers
```

### Recommended: Single File Implementation

For Sprint 14, implement db_manager.py as a single file (~400-600 lines) following the pattern of existing scripts. Modularization can be done in future sprints if needed.

### Code Structure

```python
#!/usr/bin/env python3
"""GAMSLIB status database manager.

Usage:
    python scripts/gamslib/db_manager.py COMMAND [OPTIONS]

Commands:
    init      Initialize database from catalog.json
    get       Get model details
    update    Update model field(s)
    query     Query models by criteria
    list      List all models
    validate  Validate against schema
    export    Export to CSV/Markdown
    stats     Show statistics
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
SCHEMA_PATH = PROJECT_ROOT / "docs" / "planning" / "EPIC_3" / "SPRINT_14" / "DRAFT_SCHEMA.json"
BACKUP_DIR = PROJECT_ROOT / "data" / "gamslib" / "archive"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Subcommand implementations
def cmd_init(args: argparse.Namespace) -> int: ...
def cmd_get(args: argparse.Namespace) -> int: ...
def cmd_update(args: argparse.Namespace) -> int: ...
def cmd_query(args: argparse.Namespace) -> int: ...
def cmd_list(args: argparse.Namespace) -> int: ...
def cmd_validate(args: argparse.Namespace) -> int: ...
def cmd_export(args: argparse.Namespace) -> int: ...
def cmd_stats(args: argparse.Namespace) -> int: ...


def main() -> None:
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Add subcommand parsers...
    
    args = parser.parse_args()
    
    # Dispatch to subcommand
    commands = {
        "init": cmd_init,
        "get": cmd_get,
        "update": cmd_update,
        "query": cmd_query,
        "list": cmd_list,
        "validate": cmd_validate,
        "export": cmd_export,
        "stats": cmd_stats,
    }
    
    sys.exit(commands[args.command](args))


if __name__ == "__main__":
    main()
```

### Backup Strategy

**Automatic Backups:**
- Before `init` (if database exists with --force)
- Before `update` (optional, configurable)

**Backup Implementation:**
```python
def create_backup(db_path: Path) -> Path:
    """Create timestamped backup of database."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{timestamp}_{db_path.name}"
    shutil.copy(db_path, backup_path)
    logger.info(f"Backup created: {backup_path}")
    return backup_path

def prune_backups(keep_count: int = 10) -> None:
    """Remove old backups, keeping most recent."""
    backups = sorted(BACKUP_DIR.glob("*_gamslib_status.json"))
    for old in backups[:-keep_count]:
        old.unlink()
        logger.debug(f"Pruned backup: {old}")
```

### Validation Integration

```python
from jsonschema import Draft7Validator

def validate_entry(entry: dict, schema: dict) -> list[str]:
    """Validate entry against schema, return list of errors."""
    validator = Draft7Validator(schema["definitions"]["model_entry"])
    errors = []
    for error in validator.iter_errors(entry):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append(f"{path}: {error.message}")
    return errors
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_db_manager.py

def test_init_creates_database(tmp_path):
    """Test init subcommand creates database."""
    ...

def test_get_returns_model(sample_database):
    """Test get subcommand returns model details."""
    ...

def test_update_modifies_field(sample_database):
    """Test update subcommand modifies field."""
    ...

def test_query_filters_correctly(sample_database):
    """Test query subcommand filters models."""
    ...
```

### Integration Tests

```bash
# Test full workflow
python scripts/gamslib/db_manager.py init --dry-run
python scripts/gamslib/db_manager.py init
python scripts/gamslib/db_manager.py get trnsport
python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success
python scripts/gamslib/db_manager.py query --parse-status success
python scripts/gamslib/db_manager.py validate
python scripts/gamslib/db_manager.py export --format csv
python scripts/gamslib/db_manager.py stats
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| jsonschema | >=4.0.0 | Schema validation |
| (stdlib) | - | argparse, json, logging, pathlib |

No new dependencies required beyond existing project requirements.

---

## Summary

### Key Design Decisions

1. **Follow existing patterns:** db_manager.py uses the same CLI, logging, and error handling patterns as discover_models.py and download_models.py

2. **Single file implementation:** Start with ~500 lines in one file; modularize later if needed

3. **Subcommand architecture:** 8 essential subcommands cover all Sprint 14 use cases

4. **Automatic backups:** Before destructive operations, with pruning

5. **Schema validation:** Integrated with jsonschema library

6. **Consistent output formats:** Table (human), JSON (scripting), CSV/Markdown (reports)

### Sprint 14 Scope

| Priority | Subcommands | Notes |
|----------|-------------|-------|
| Must have | init, get, update, query, validate | Core functionality |
| Should have | list, export, stats | Reporting functionality |
| Could have | backup, restore | Convenience features |
| Won't have | migrate, diff | Future sprints |

---

## Document History

- 2026-01-01: Initial creation (Sprint 14 Prep Task 7)
