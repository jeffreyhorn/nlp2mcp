#!/usr/bin/env python3
"""GAMSLIB status database manager.

This script provides CLI tools for managing the gamslib_status.json database.
It supports initialization, validation, querying, and export operations.

Usage:
    python scripts/gamslib/db_manager.py COMMAND [OPTIONS]

Commands:
    init      Initialize database (from migration or empty)
    validate  Validate database against schema
    list      List all models with summary
    get       Get model details (Day 4)
    update    Update model field(s) (Day 4)
    query     Query models by criteria (Day 5)
    export    Export to CSV/Markdown (Day 5)
    stats     Show statistics (Day 5)

Examples:
    python scripts/gamslib/db_manager.py validate
    python scripts/gamslib/db_manager.py list --format table
    python scripts/gamslib/db_manager.py init --force
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Sentinel value to distinguish "field not found" from "field value is None"
_NOT_FOUND = object()

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
BACKUP_DIR = PROJECT_ROOT / "data" / "gamslib" / "archive"

# Backup settings
MAX_BACKUPS = 10

# Configure logging defensively: only if no handlers are configured yet
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
logger = logging.getLogger(__name__)


# =============================================================================
# Database I/O Functions
# =============================================================================


def load_database(path: Path = DATABASE_PATH) -> dict[str, Any]:
    """Load database from JSON file.

    Args:
        path: Path to database file

    Returns:
        Parsed database dictionary

    Raises:
        FileNotFoundError: If database doesn't exist
        json.JSONDecodeError: If database is invalid JSON
    """
    logger.debug(f"Loading database from {path}")
    with open(path) as f:
        return json.load(f)


def save_database(data: dict[str, Any], path: Path = DATABASE_PATH) -> None:
    """Save database to JSON file with atomic write.

    Uses a temp file and rename to avoid corruption on failure.

    Args:
        data: Database dictionary to save
        path: Output path
    """
    logger.debug(f"Saving database to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first
    temp_path = path.with_suffix(".json.tmp")
    with open(temp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # Trailing newline

    # Atomic rename
    temp_path.replace(path)
    logger.debug(f"Saved {len(data.get('models', []))} models to {path}")


def load_schema(path: Path = SCHEMA_PATH) -> dict[str, Any]:
    """Load JSON schema for validation.

    Args:
        path: Path to schema file

    Returns:
        Parsed schema dictionary
    """
    logger.debug(f"Loading schema from {path}")
    with open(path) as f:
        return json.load(f)


# =============================================================================
# Backup Functions
# =============================================================================


def create_backup(db_path: Path = DATABASE_PATH) -> Path | None:
    """Create timestamped backup of database.

    Args:
        db_path: Path to database file to backup

    Returns:
        Path to backup file, or None if source doesn't exist
    """
    if not db_path.exists():
        logger.debug(f"No backup needed - {db_path} doesn't exist")
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"{timestamp}_{db_path.name}"
    shutil.copy(db_path, backup_path)
    logger.info(f"Backup created: {backup_path}")

    # Prune old backups
    prune_backups()

    return backup_path


def prune_backups(keep_count: int = MAX_BACKUPS) -> int:
    """Remove old backups, keeping most recent.

    Args:
        keep_count: Number of backups to keep

    Returns:
        Number of backups pruned
    """
    if not BACKUP_DIR.exists():
        return 0

    backups = sorted(BACKUP_DIR.glob("*_gamslib_status.json"))
    to_prune = backups[:-keep_count] if len(backups) > keep_count else []

    for old in to_prune:
        old.unlink()
        logger.debug(f"Pruned backup: {old}")

    return len(to_prune)


def list_backups() -> list[Path]:
    """List all backup files.

    Returns:
        List of backup file paths, sorted by timestamp (newest last)
    """
    if not BACKUP_DIR.exists():
        return []
    return sorted(BACKUP_DIR.glob("*_gamslib_status.json"))


# =============================================================================
# Validation Functions
# =============================================================================


def validate_database(
    database: dict[str, Any],
    schema: dict[str, Any],
) -> list[dict[str, str]]:
    """Validate database against schema.

    Args:
        database: The database to validate
        schema: JSON Schema to validate against

    Returns:
        List of error dictionaries with 'path' and 'message' keys
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        logger.error("jsonschema library not installed")
        return [{"path": "(library)", "message": "jsonschema not installed"}]

    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(database):
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        errors.append({"path": path, "message": error.message})

    return errors


# =============================================================================
# Subcommand: init
# =============================================================================


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize database from migration or create empty.

    If gamslib_status.json already exists, requires --force to overwrite.
    Creates a backup before overwriting when --force is used.
    """
    if DATABASE_PATH.exists() and not args.force:
        logger.error(f"Database already exists: {DATABASE_PATH}")
        logger.error("Use --force to overwrite (backup will be created)")
        return 1

    if args.dry_run:
        logger.info("[DRY RUN] Would initialize database")
        if DATABASE_PATH.exists():
            logger.info("[DRY RUN] Would create backup of existing database")
        return 0

    # Create backup if overwriting
    if DATABASE_PATH.exists():
        backup_path = create_backup()
        if backup_path:
            logger.info(f"Backed up existing database to {backup_path}")

    if args.empty:
        # Create empty database
        database = {
            "schema_version": "2.1.0",
            "created_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_date": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_models": 0,
            "models": [],
        }
        save_database(database)
        logger.info(f"Created empty database: {DATABASE_PATH}")
    else:
        # Run migration from catalog.json
        if not CATALOG_PATH.exists():
            logger.error(f"Catalog not found: {CATALOG_PATH}")
            return 1

        # Import and run migration
        from scripts.gamslib.migrate_catalog import load_catalog, migrate_catalog

        catalog = load_catalog(CATALOG_PATH)
        migration_date = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        database = migrate_catalog(catalog, migration_date)

        # Validate before saving
        schema = load_schema()
        errors = validate_database(database, schema)
        if errors:
            logger.error(f"Migration produced invalid database: {len(errors)} errors")
            for err in errors[:5]:
                logger.error(f"  {err['path']}: {err['message']}")
            return 1

        save_database(database)
        logger.info(f"Initialized database with {len(database['models'])} models")

    print(f"\nDatabase initialized: {DATABASE_PATH}")
    return 0


# =============================================================================
# Subcommand: validate
# =============================================================================


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate database against JSON schema."""
    # Load database
    if not DATABASE_PATH.exists():
        logger.error(f"Database not found: {DATABASE_PATH}")
        return 1

    try:
        database = load_database()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database: {e}")
        return 1

    # Load schema
    schema_path = args.schema if args.schema else SCHEMA_PATH
    if not schema_path.exists():
        logger.error(f"Schema not found: {schema_path}")
        return 1

    try:
        schema = load_schema(schema_path)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in schema: {e}")
        return 1

    # Validate
    print(f"Validating {DATABASE_PATH} against schema...")
    print(f"  Schema version: {database.get('schema_version', 'unknown')}")
    print(f"  Models to validate: {len(database.get('models', []))}")

    errors = validate_database(database, schema)

    if errors:
        print(f"\nValidation FAILED with {len(errors)} errors:")
        for err in errors[:20]:  # Show first 20 errors
            print(f"  {err['path']}: {err['message']}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more errors")
        return 1

    print("\nValidation PASSED")
    print(f"  All {len(database.get('models', []))} entries are valid")
    return 0


# =============================================================================
# Subcommand: list
# =============================================================================


def cmd_list(args: argparse.Namespace) -> int:
    """List all models with summary."""
    # Load database
    if not DATABASE_PATH.exists():
        logger.error(f"Database not found: {DATABASE_PATH}")
        return 1

    try:
        database = load_database()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database: {e}")
        return 1

    all_models = database.get("models", [])
    models = all_models
    is_filtered = False

    # Filter by type if specified
    if args.type:
        models = [m for m in models if m.get("gamslib_type") == args.type]
        is_filtered = True

    # Apply limit
    if args.limit is not None:
        if args.limit < 0:
            logger.error(
                f"Invalid limit value: {args.limit}. Limit must be a non-negative integer (0 means no limit)."
            )
            return 1
        if args.limit > 0:
            models = models[: args.limit]

    if args.format == "json":
        # JSON output
        output = {
            "total": len(models),
            "total_in_database": len(all_models),
            "models": models,
        }
        print(json.dumps(output, indent=2))

    elif args.format == "count":
        # Count only
        print(len(models))

    else:
        # Table output (default)
        print(f"\nGAMSLIB Status Database: {len(all_models)} models")
        print(f"Schema version: {database.get('schema_version', 'unknown')}")
        print("=" * 70)

        if is_filtered:
            print(f"Filtered by type: {args.type}")
            print(f"Showing: {len(models)} of {len(all_models)} models")
            print("-" * 70)

        # Use filtered models for stats when filter is active
        stats_models = models if is_filtered else all_models

        # Count by type
        type_counts: dict[str, int] = {}
        for m in stats_models:
            t = m.get("gamslib_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        print("\nBy Model Type:")
        for t, count in sorted(type_counts.items()):
            print(f"  {t}: {count}")

        # Count by convexity status
        convexity_counts: dict[str, int] = {}
        for m in stats_models:
            status = m.get("convexity", {}).get("status", "not_tested")
            convexity_counts[status] = convexity_counts.get(status, 0) + 1

        print("\nBy Convexity Status:")
        for status, count in sorted(convexity_counts.items()):
            print(f"  {status}: {count}")

        # Count by parse status
        parse_counts: dict[str, int] = {}
        for m in stats_models:
            status = m.get("nlp2mcp_parse", {}).get("status", "not_tested")
            parse_counts[status] = parse_counts.get(status, 0) + 1

        print("\nBy Parse Status:")
        for status, count in sorted(parse_counts.items()):
            print(f"  {status}: {count}")

        # Count by MCP solve status (Sprint 15)
        solve_counts: dict[str, int] = {}
        for m in stats_models:
            status = m.get("mcp_solve", {}).get("status", "not_tested")
            solve_counts[status] = solve_counts.get(status, 0) + 1

        # Only show if any models have been tested
        if any(s != "not_tested" for s in solve_counts.keys()):
            print("\nBy MCP Solve Status:")
            for status, count in sorted(solve_counts.items()):
                print(f"  {status}: {count}")

        # Count by solution comparison status (Sprint 15)
        comp_counts: dict[str, int] = {}
        for m in stats_models:
            status = m.get("solution_comparison", {}).get("comparison_status", "not_tested")
            comp_counts[status] = comp_counts.get(status, 0) + 1

        # Only show if any models have been compared
        if any(s != "not_tested" for s in comp_counts.keys()):
            print("\nBy Solution Comparison Status:")
            for status, count in sorted(comp_counts.items()):
                print(f"  {status}: {count}")

        # Show model list if requested or if filtering
        if args.verbose or args.type or args.limit:
            print("\n" + "-" * 70)
            print(f"{'model_id':<20} {'type':<6} {'convexity':<18} {'parse':<12}")
            print("-" * 70)
            for m in models:
                model_id = m.get("model_id", "?")
                model_type = m.get("gamslib_type", "?")
                convexity = m.get("convexity", {}).get("status", "not_tested")
                parse = m.get("nlp2mcp_parse", {}).get("status", "not_tested")
                print(f"{model_id:<20} {model_type:<6} {convexity:<18} {parse:<12}")

        print("=" * 70)

    return 0


# =============================================================================
# Subcommand: get
# =============================================================================


def find_model(database: dict[str, Any], model_id: str) -> dict[str, Any] | None:
    """Find a model by ID in the database.

    Args:
        database: The loaded database
        model_id: Model identifier to find

    Returns:
        The model entry dict, or None if not found
    """
    for model in database.get("models", []):
        if model.get("model_id") == model_id:
            return model
    return None


def get_nested_value(data: dict[str, Any], field_path: str, default: Any = _NOT_FOUND) -> Any:
    """Get a value from a nested dictionary using dot notation.

    Args:
        data: The dictionary to search
        field_path: Dot-separated path (e.g., "convexity.status")
        default: Value to return if path not found (default: _NOT_FOUND sentinel)

    Returns:
        The value at the path, or default if not found
    """
    parts = field_path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default
    return current


def format_model_table(model: dict[str, Any]) -> str:
    """Format a model entry as a human-readable table.

    Args:
        model: The model entry dict

    Returns:
        Formatted string representation
    """
    lines = []
    lines.append(f"Model: {model.get('model_id', '?')}")
    lines.append("=" * 50)

    # Basic fields
    lines.append(f"model_id:       {model.get('model_id', '?')}")
    lines.append(f"model_name:     {model.get('model_name', '?')}")
    lines.append(f"gamslib_type:   {model.get('gamslib_type', '?')}")

    if model.get("sequence_number"):
        lines.append(f"sequence_number: {model.get('sequence_number')}")

    if model.get("description"):
        lines.append(f"description:    {model.get('description')}")

    # Convexity section
    if "convexity" in model:
        lines.append("")
        lines.append("Convexity:")
        conv = model["convexity"]
        lines.append(f"  status:        {conv.get('status', 'not_tested')}")
        if conv.get("solver_status") is not None:
            lines.append(f"  solver_status: {conv.get('solver_status')}")
        if conv.get("model_status") is not None:
            lines.append(f"  model_status:  {conv.get('model_status')}")
        if conv.get("solver"):
            lines.append(f"  solver:        {conv.get('solver')}")
        if conv.get("objective_value") is not None:
            lines.append(f"  objective:     {conv.get('objective_value')}")

    # Parse section
    if "nlp2mcp_parse" in model:
        lines.append("")
        lines.append("Parse:")
        parse = model["nlp2mcp_parse"]
        lines.append(f"  status:        {parse.get('status', 'not_tested')}")
        if parse.get("nlp2mcp_version"):
            lines.append(f"  version:       {parse.get('nlp2mcp_version')}")
        if parse.get("variables_count") is not None:
            lines.append(f"  variables:     {parse.get('variables_count')}")
        if parse.get("equations_count") is not None:
            lines.append(f"  equations:     {parse.get('equations_count')}")

    # Translate section
    if "nlp2mcp_translate" in model:
        lines.append("")
        lines.append("Translate:")
        trans = model["nlp2mcp_translate"]
        lines.append(f"  status:        {trans.get('status', 'not_tested')}")

    # MCP Solve section (Sprint 15)
    if "mcp_solve" in model:
        lines.append("")
        lines.append("MCP Solve:")
        solve = model["mcp_solve"]
        lines.append(f"  status:        {solve.get('status', 'not_tested')}")
        if solve.get("solver"):
            lines.append(f"  solver:        {solve.get('solver')}")
        if solve.get("solver_version"):
            lines.append(f"  version:       {solve.get('solver_version')}")
        if solve.get("solver_status") is not None:
            lines.append(f"  solver_status: {solve.get('solver_status')}")
        if solve.get("model_status") is not None:
            lines.append(f"  model_status:  {solve.get('model_status')}")
        if solve.get("objective_value") is not None:
            lines.append(f"  objective:     {solve.get('objective_value')}")
        if solve.get("solve_time_seconds") is not None:
            lines.append(f"  solve_time:    {solve.get('solve_time_seconds'):.4f}s")
        if solve.get("outcome_category"):
            lines.append(f"  outcome:       {solve.get('outcome_category')}")

    # Solution Comparison section (Sprint 15)
    if "solution_comparison" in model:
        lines.append("")
        lines.append("Solution Comparison:")
        comp = model["solution_comparison"]
        lines.append(f"  status:        {comp.get('comparison_status', 'not_tested')}")
        if comp.get("objective_match") is not None:
            match_str = "YES" if comp.get("objective_match") else "NO"
            lines.append(f"  objective_match: {match_str}")
        if comp.get("nlp_objective") is not None:
            lines.append(f"  nlp_objective:   {comp.get('nlp_objective')}")
        if comp.get("mcp_objective") is not None:
            lines.append(f"  mcp_objective:   {comp.get('mcp_objective')}")
        if comp.get("absolute_difference") is not None:
            lines.append(f"  abs_diff:        {comp.get('absolute_difference'):.2e}")
        if comp.get("relative_difference") is not None:
            lines.append(f"  rel_diff:        {comp.get('relative_difference'):.2e}")
        if comp.get("comparison_result"):
            lines.append(f"  result:          {comp.get('comparison_result')}")

    return "\n".join(lines)


def cmd_get(args: argparse.Namespace) -> int:
    """Get details for a single model."""
    # Load database
    if not DATABASE_PATH.exists():
        logger.error(f"Database not found: {DATABASE_PATH}")
        return 1

    try:
        database = load_database()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database: {e}")
        return 1

    # Find model
    model = find_model(database, args.model_id)
    if model is None:
        logger.error(f"Model not found: {args.model_id}")
        return 1

    # If --field specified, get only that field
    if args.field:
        value = get_nested_value(model, args.field)
        if value is _NOT_FOUND:
            logger.error(f"Field not found: {args.field}")
            return 1

        if args.format == "json":
            print(json.dumps(value, indent=2))
        else:
            # For simple values, just print them
            if isinstance(value, (dict, list)):
                print(json.dumps(value, indent=2))
            elif value is None:
                print("null")
            else:
                print(value)
        return 0

    # Output full model
    if args.format == "json":
        print(json.dumps(model, indent=2))
    else:
        # Table format (default)
        print(format_model_table(model))

    return 0


# =============================================================================
# Subcommand: update
# =============================================================================


def set_nested_value(data: dict[str, Any], field_path: str, value: Any) -> dict[str, Any]:
    """Set a value in a nested dictionary using dot notation.

    Creates intermediate dictionaries if they don't exist.

    Args:
        data: The dictionary to modify (will be modified in place)
        field_path: Dot-separated path (e.g., "convexity.status")
        value: The value to set

    Returns:
        The modified dictionary
    """
    parts = field_path.split(".")
    current = data

    # Navigate/create path up to the last part
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            # Overwrite non-dict value with empty dict
            current[part] = {}
        current = current[part]

    # Set the final value
    current[parts[-1]] = value
    return data


def parse_value(value_str: str) -> Any:
    """Parse a string value into the appropriate Python type.

    Attempts to parse as JSON first, then falls back to string.

    Args:
        value_str: String representation of value

    Returns:
        Parsed value (int, float, bool, None, or string)
    """
    # Try JSON parsing first (handles true/false/null, numbers, arrays, objects)
    try:
        return json.loads(value_str)
    except json.JSONDecodeError:
        pass

    # Return as string
    return value_str


def validate_model_entry(model: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    """Validate a single model entry against the schema.

    Args:
        model: The model entry to validate
        schema: The full database schema

    Returns:
        List of error dictionaries with 'path' and 'message' keys
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        logger.error("jsonschema library not installed")
        return [{"path": "(library)", "message": "jsonschema not installed"}]

    # Create a validator with the full schema to resolve $ref
    # We wrap the model in a database structure to validate against the full schema
    test_database = {
        "schema_version": "2.0.0",
        "models": [model],
    }

    validator = Draft7Validator(schema)
    errors = []

    for error in validator.iter_errors(test_database):
        # Filter to only errors in the model entry (skip schema_version errors etc)
        path_parts = list(error.absolute_path)
        if len(path_parts) >= 2 and path_parts[0] == "models" and path_parts[1] == 0:
            # Remove "models.0." prefix from path
            field_path = ".".join(str(p) for p in path_parts[2:]) or "(root)"
            errors.append({"path": field_path, "message": error.message})

    return errors


def cmd_update(args: argparse.Namespace) -> int:
    """Update field(s) for a model."""
    # Load database
    if not DATABASE_PATH.exists():
        logger.error(f"Database not found: {DATABASE_PATH}")
        return 1

    try:
        database = load_database()
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database: {e}")
        return 1

    # Find model index
    model_index = None
    for i, model in enumerate(database.get("models", [])):
        if model.get("model_id") == args.model_id:
            model_index = i
            break

    if model_index is None:
        logger.error(f"Model not found: {args.model_id}")
        return 1

    # Make a copy of the model for modification
    original_model = database["models"][model_index]
    updated_model = copy.deepcopy(original_model)

    # Collect all field=value updates
    updates = []

    # First positional field and value
    if args.field and args.value:
        updates.append((args.field, args.value))

    # Additional --set field=value pairs
    if args.set:
        for field_value in args.set:
            if "=" not in field_value:
                logger.error(f"Invalid --set format: {field_value} (expected field=value)")
                return 1
            field, value = field_value.split("=", 1)
            updates.append((field, value))

    if not updates:
        logger.error("No updates specified")
        return 1

    # Apply updates
    for field_path, value_str in updates:
        parsed_value = parse_value(value_str)
        set_nested_value(updated_model, field_path, parsed_value)
        logger.debug(f"Set {field_path} = {parsed_value}")

    # Validate the updated model against schema
    try:
        schema = load_schema()
        errors = validate_model_entry(updated_model, schema)
        if errors:
            logger.error("Validation failed after update:")
            for err in errors:
                logger.error(f"  {err['path']}: {err['message']}")
            logger.error("Update aborted. Database unchanged.")
            return 1
    except Exception as e:
        logger.error(f"Schema validation error: {e}")
        return 1

    # Create backup after validation succeeds, before modifying database
    backup_path = create_backup()
    if backup_path:
        logger.debug(f"Backup created before update: {backup_path}")

    # Update the database
    database["models"][model_index] = updated_model

    # Update the updated_date
    database["updated_date"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Save the database
    save_database(database)

    print(f"Updated model: {args.model_id}")
    for field_path, value_str in updates:
        print(f"  {field_path} = {parse_value(value_str)}")

    return 0


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GAMSLIB status database manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/gamslib/db_manager.py validate
    python scripts/gamslib/db_manager.py list
    python scripts/gamslib/db_manager.py list --type LP
    python scripts/gamslib/db_manager.py get trnsport
    python scripts/gamslib/db_manager.py get trnsport --format json
    python scripts/gamslib/db_manager.py get trnsport --field convexity.status
    python scripts/gamslib/db_manager.py update trnsport nlp2mcp_parse.status success
    python scripts/gamslib/db_manager.py update trnsport --set nlp2mcp_parse.status=success
    python scripts/gamslib/db_manager.py init --force
        """,
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init subcommand
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize database",
        description="Initialize gamslib_status.json from catalog.json migration",
    )
    init_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Overwrite existing database (creates backup first)",
    )
    init_parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what would be done without making changes",
    )
    init_parser.add_argument(
        "--empty",
        action="store_true",
        help="Create empty database instead of migrating from catalog.json",
    )

    # validate subcommand
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate database against schema",
        description="Validate gamslib_status.json against schema.json",
    )
    validate_parser.add_argument(
        "--schema",
        type=Path,
        help=f"Custom schema path (default: {SCHEMA_PATH})",
    )

    # list subcommand
    list_parser = subparsers.add_parser(
        "list",
        help="List all models",
        description="List all models with summary statistics",
    )
    list_parser.add_argument(
        "--type",
        "-t",
        choices=["LP", "NLP", "QCP", "MIP", "MINLP", "MIQCP"],
        help="Filter by model type",
    )
    list_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json", "count"],
        default="table",
        help="Output format (default: table)",
    )
    list_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        help="Limit number of results",
    )

    # get subcommand
    get_parser = subparsers.add_parser(
        "get",
        help="Get model details",
        description="Get details for a single model by ID",
    )
    get_parser.add_argument(
        "model_id",
        help="Model identifier (e.g., trnsport)",
    )
    get_parser.add_argument(
        "--format",
        "-f",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    get_parser.add_argument(
        "--field",
        help="Get only a specific field (supports dot notation, e.g., convexity.status)",
    )

    # update subcommand
    update_parser = subparsers.add_parser(
        "update",
        help="Update model field(s)",
        description="Update field(s) for a model. Validates against schema before saving.",
    )
    update_parser.add_argument(
        "model_id",
        help="Model identifier (e.g., trnsport)",
    )
    update_parser.add_argument(
        "field",
        nargs="?",
        help="Field path to update (supports dot notation, e.g., nlp2mcp_parse.status)",
    )
    update_parser.add_argument(
        "value",
        nargs="?",
        help="New value for the field",
    )
    update_parser.add_argument(
        "--set",
        "-s",
        action="append",
        metavar="FIELD=VALUE",
        help="Set field=value pair (can be used multiple times)",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to subcommand
    commands = {
        "init": cmd_init,
        "validate": cmd_validate,
        "list": cmd_list,
        "get": cmd_get,
        "update": cmd_update,
    }

    if args.command not in commands:
        logger.error(f"Unknown command: {args.command}")
        logger.error("Available commands: " + ", ".join(commands.keys()))
        return 1

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
