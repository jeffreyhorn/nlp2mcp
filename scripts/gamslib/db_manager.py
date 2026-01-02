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
import json
import logging
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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

# Configure logging
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
            "schema_version": "2.0.0",
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

    models = database.get("models", [])

    # Filter by type if specified
    if args.type:
        models = [m for m in models if m.get("gamslib_type") == args.type]

    # Apply limit
    if args.limit and args.limit > 0:
        models = models[: args.limit]

    if args.format == "json":
        # JSON output
        output = {"total": len(models), "models": models}
        print(json.dumps(output, indent=2))

    elif args.format == "count":
        # Count only
        print(len(models))

    else:
        # Table output (default)
        print(f"\nGAMSLIB Status Database: {len(database.get('models', []))} models")
        print(f"Schema version: {database.get('schema_version', 'unknown')}")
        print("=" * 70)

        if args.type:
            print(f"Filtered by type: {args.type}")
            print(f"Showing: {len(models)} models")
            print("-" * 70)

        # Count by type
        type_counts: dict[str, int] = {}
        for m in database.get("models", []):
            t = m.get("gamslib_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        print("\nBy Model Type:")
        for t, count in sorted(type_counts.items()):
            print(f"  {t}: {count}")

        # Count by convexity status
        convexity_counts: dict[str, int] = {}
        for m in database.get("models", []):
            status = m.get("convexity", {}).get("status", "not_tested")
            convexity_counts[status] = convexity_counts.get(status, 0) + 1

        print("\nBy Convexity Status:")
        for status, count in sorted(convexity_counts.items()):
            print(f"  {status}: {count}")

        # Count by parse status
        parse_counts: dict[str, int] = {}
        for m in database.get("models", []):
            status = m.get("nlp2mcp_parse", {}).get("status", "not_tested")
            parse_counts[status] = parse_counts.get(status, 0) + 1

        print("\nBy Parse Status:")
        for status, count in sorted(parse_counts.items()):
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
    python scripts/gamslib/db_manager.py list --format json
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
    list_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show individual model list",
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
    }

    if args.command not in commands:
        logger.error(f"Unknown command: {args.command}")
        logger.error("Available commands: " + ", ".join(commands.keys()))
        return 1

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
