#!/usr/bin/env python3
"""Migrate gamslib_status.json from schema v2.0.0 to v2.1.0.

This script updates the database schema to v2.1.0 which adds:
- mcp_solve object for PATH solver results
- solution_comparison object for objective comparison
- model_stats object in parse_result
- Extended error_category enum (7 -> 36 values)
- New enums: solve_outcome_category, comparison_result_category

Changes from v2.0.0 to v2.1.0:
    New optional fields in model_entry:
        - mcp_solve: Results from PATH solver (replaces placeholder)
        - solution_comparison: Comparison between NLP and MCP solutions

    New optional field in parse_result:
        - model_stats: Model statistics from IR

    Extended enums:
        - error_category: 7 -> 36 values (Sprint 15 taxonomy)
        - solve_outcome_category: 10 values (new)
        - comparison_result_category: 7 values (new)

Migration is non-destructive:
    - All existing data preserved
    - New fields are optional (not added if not present)
    - Only schema_version and updated_date are modified

Usage:
    python scripts/gamslib/migrate_schema_v2.1.0.py                    # Migrate
    python scripts/gamslib/migrate_schema_v2.1.0.py --dry-run          # Preview
    python scripts/gamslib/migrate_schema_v2.1.0.py --validate         # Validate
    python scripts/gamslib/migrate_schema_v2.1.0.py --verbose          # Detailed

Options:
    --dry-run       Show what would be migrated without writing
    --validate      Validate output against schema.json v2.1.0
    --verbose       Show detailed progress information
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Paths
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
ARCHIVE_PATH = PROJECT_ROOT / "data" / "gamslib" / "archive"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_database(path: Path) -> dict[str, Any]:
    """Load gamslib_status.json from disk.

    Args:
        path: Path to gamslib_status.json file

    Returns:
        Parsed database dictionary

    Raises:
        FileNotFoundError: If database doesn't exist
        json.JSONDecodeError: If database is invalid JSON
    """
    logger.info(f"Loading database from {path}")
    with open(path) as f:
        database = json.load(f)
    version = database.get("schema_version", "unknown")
    model_count = len(database.get("models", []))
    logger.info(f"Loaded {model_count} models (schema v{version})")
    return database


def load_schema(path: Path) -> dict[str, Any]:
    """Load schema.json for validation.

    Args:
        path: Path to schema.json file

    Returns:
        Parsed schema dictionary
    """
    logger.info(f"Loading schema from {path}")
    with open(path) as f:
        return json.load(f)


def create_backup(source_path: Path, archive_path: Path) -> Path:
    """Create a backup of the database before migration.

    Args:
        source_path: Path to gamslib_status.json
        archive_path: Directory for backups

    Returns:
        Path to backup file
    """
    archive_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_name = f"gamslib_status_v2.0.0_backup_{timestamp}.json"
    backup_path = archive_path / backup_name

    logger.info(f"Creating backup: {backup_path}")
    with open(source_path) as src:
        content = src.read()
    with open(backup_path, "w") as dst:
        dst.write(content)

    return backup_path


def migrate_database(
    database: dict[str, Any],
    migration_date: str,
) -> dict[str, Any]:
    """Migrate database from v2.0.0 to v2.1.0.

    This migration is non-destructive - all existing data is preserved.
    Only the schema_version and updated_date are modified.

    Args:
        database: Original v2.0.0 database
        migration_date: ISO 8601 timestamp for updated_date

    Returns:
        Migrated v2.1.0 database
    """
    current_version = database.get("schema_version", "unknown")
    if current_version != "2.0.0":
        logger.warning(f"Expected schema v2.0.0, found v{current_version}")

    models = database.get("models", [])
    logger.info(f"Migrating {len(models)} models from v2.0.0 to v2.1.0...")

    # The v2.1.0 migration is non-destructive
    # - mcp_solve and solution_comparison are new optional fields
    # - They will be absent until populated by Sprint 15 testing
    # - No transformation of existing data needed

    # Update database metadata
    migrated = database.copy()
    migrated["schema_version"] = "2.1.0"
    migrated["updated_date"] = migration_date

    logger.info(f"Migration complete: schema_version updated to 2.1.0")
    return migrated


def validate_database(database: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Validate database against schema.

    Args:
        database: The migrated database
        schema: JSON Schema to validate against

    Returns:
        List of validation error messages (empty if valid)
    """
    try:
        from jsonschema import Draft7Validator
    except ImportError:
        logger.warning("jsonschema not installed, skipping validation")
        return ["jsonschema library not installed"]

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(database))

    error_messages = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path)
        error_messages.append(f"{path}: {error.message}")

    return error_messages


def save_database(database: dict[str, Any], path: Path) -> None:
    """Save database to JSON file.

    Args:
        database: Database dictionary to save
        path: Output path
    """
    logger.info(f"Saving database to {path}")
    with open(path, "w") as f:
        json.dump(database, f, indent=2)
    logger.info(f"Saved {len(database.get('models', []))} models to {path}")


def print_migration_summary(
    source_db: dict[str, Any],
    migrated_db: dict[str, Any],
    backup_path: Path | None,
) -> None:
    """Print migration summary statistics."""
    source_models = source_db.get("models", [])

    print("\n" + "=" * 60)
    print("SCHEMA MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Source version: {source_db.get('schema_version', 'unknown')}")
    print(f"Target version: {migrated_db.get('schema_version')}")
    print(f"Models: {len(source_models)}")
    print(f"Updated date: {migrated_db.get('updated_date')}")

    if backup_path:
        print(f"\nBackup created: {backup_path}")

    # Schema changes summary
    print("\nSchema Changes in v2.1.0:")
    print("  + mcp_solve object (PATH solver results)")
    print("  + solution_comparison object (objective comparison)")
    print("  + model_stats object in parse_result")
    print("  + error_category enum extended (7 -> 36 values)")
    print("  + solve_outcome_category enum (10 values)")
    print("  + comparison_result_category enum (7 values)")

    print("\nData Changes:")
    print("  - All existing data preserved (non-destructive)")
    print("  - New fields are optional (added by Sprint 15 testing)")

    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate gamslib_status.json from schema v2.0.0 to v2.1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/gamslib/migrate_schema_v2.1.0.py                    # Migrate
    python scripts/gamslib/migrate_schema_v2.1.0.py --dry-run          # Preview
    python scripts/gamslib/migrate_schema_v2.1.0.py --validate         # Validate
    python scripts/gamslib/migrate_schema_v2.1.0.py -v --validate      # Both
        """,
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview migration without writing output",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate output against schema.json v2.1.0",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup (not recommended)",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DATABASE_PATH,
        help=f"Database path (default: {DATABASE_PATH})",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load source database
    try:
        database = load_database(args.database)
    except FileNotFoundError:
        logger.error(f"Database not found: {args.database}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in database: {e}")
        return 1

    # Check current version
    current_version = database.get("schema_version", "unknown")
    if current_version == "2.1.0":
        logger.info("Database already at v2.1.0, no migration needed")
        print("\nDatabase is already at schema v2.1.0 - no migration needed")
        return 0

    if current_version != "2.0.0":
        logger.error(f"Cannot migrate from v{current_version} - expected v2.0.0")
        return 1

    # Create backup unless skipped or dry-run
    backup_path = None
    if not args.dry_run and not args.no_backup:
        backup_path = create_backup(args.database, ARCHIVE_PATH)

    # Perform migration
    migration_date = get_utc_timestamp()
    migrated_db = migrate_database(database, migration_date)

    # Print summary
    print_migration_summary(database, migrated_db, backup_path)

    # Validate if requested
    if args.validate:
        try:
            schema = load_schema(SCHEMA_PATH)
            errors = validate_database(migrated_db, schema)
            if errors:
                logger.error(f"Validation failed with {len(errors)} errors:")
                for error in errors[:10]:  # Show first 10 errors
                    logger.error(f"  - {error}")
                if len(errors) > 10:
                    logger.error(f"  ... and {len(errors) - 10} more errors")
                return 1
            logger.info("Validation passed: all entries valid against v2.1.0 schema")
            print("\nValidation: PASSED")
        except FileNotFoundError:
            logger.error(f"Schema not found: {SCHEMA_PATH}")
            return 1

    # Save unless dry-run
    if args.dry_run:
        logger.info("Dry run - not saving output")
        print("\n[DRY RUN] No files written")
    else:
        save_database(migrated_db, args.database)
        print(f"\nDatabase updated: {args.database}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
