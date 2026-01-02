#!/usr/bin/env python3
"""Migrate catalog.json to gamslib_status.json with the new v2.0.0 schema.

This script transforms the Sprint 13 catalog.json (v1.0.0) to the new
gamslib_status.json format (v2.0.0) with nested pipeline stage tracking.

Field Mapping (catalog.json -> gamslib_status.json):
    Core fields (direct copy):
        - model_id, sequence_number, model_name, gamslib_type
        - source_url, web_page_url, description, keywords
        - download_status, download_date, file_path, file_size_bytes, notes

    Convexity fields (nested under "convexity" object):
        - convexity_status -> convexity.status
        - verification_date -> convexity.verification_date
        - solver_status -> convexity.solver_status
        - model_status -> convexity.model_status
        - objective_value -> convexity.objective_value
        - solve_time_seconds -> convexity.solve_time_seconds
        - verification_error -> convexity.error

    New fields added:
        - migrated_from: "catalog.json"
        - migration_date: current UTC timestamp

    Pipeline stages (absent after migration):
        - nlp2mcp_parse: not present (not yet tested)
        - nlp2mcp_translate: not present (not yet tested)
        - mcp_solve: not present (not yet tested)

Usage:
    python scripts/gamslib/migrate_catalog.py                    # Migrate and save
    python scripts/gamslib/migrate_catalog.py --dry-run          # Preview without saving
    python scripts/gamslib/migrate_catalog.py --validate         # Validate output
    python scripts/gamslib/migrate_catalog.py --verbose          # Show detailed progress

Options:
    --dry-run       Show what would be migrated without writing
    --validate      Validate output against schema.json
    --verbose       Show detailed progress information
    --output PATH   Output path (default: data/gamslib/gamslib_status.json)
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
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
SCHEMA_PATH = PROJECT_ROOT / "data" / "gamslib" / "schema.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"

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


def load_catalog(path: Path) -> dict[str, Any]:
    """Load catalog.json from disk.

    Args:
        path: Path to catalog.json file

    Returns:
        Parsed catalog dictionary

    Raises:
        FileNotFoundError: If catalog.json doesn't exist
        json.JSONDecodeError: If catalog.json is invalid JSON
    """
    logger.info(f"Loading catalog from {path}")
    with open(path) as f:
        catalog = json.load(f)
    logger.info(f"Loaded {len(catalog.get('models', []))} models from catalog")
    return catalog


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


def transform_entry(entry: dict[str, Any], migration_date: str) -> dict[str, Any]:
    """Transform a single catalog entry to the new schema format.

    Args:
        entry: Original catalog.json model entry
        migration_date: ISO 8601 timestamp for migration_date field

    Returns:
        Transformed entry matching gamslib_status.json schema
    """
    # Start with core fields that map directly
    new_entry: dict[str, Any] = {
        "model_id": entry["model_id"],
        "model_name": entry["model_name"],
        "gamslib_type": entry["gamslib_type"],
    }

    # Optional direct-mapped fields (only include if present and non-empty)
    optional_direct = [
        "sequence_number",
        "source_url",
        "web_page_url",
        "description",
        "download_status",
        "download_date",
        "file_path",
        "file_size_bytes",
    ]

    for field in optional_direct:
        if field in entry and entry[field] is not None:
            new_entry[field] = entry[field]

    # Keywords - only include if non-empty array
    if entry.get("keywords") and len(entry["keywords"]) > 0:
        new_entry["keywords"] = entry["keywords"]

    # Notes - only include if non-empty string
    if entry.get("notes") and entry["notes"].strip():
        new_entry["notes"] = entry["notes"]

    # Migration metadata
    new_entry["migrated_from"] = "catalog.json"
    new_entry["migration_date"] = migration_date

    # Build convexity object from flat fields
    convexity_status = entry.get("convexity_status")
    if convexity_status:
        convexity: dict[str, Any] = {"status": convexity_status}

        # Optional convexity fields
        if "verification_date" in entry and entry["verification_date"]:
            convexity["verification_date"] = entry["verification_date"]

        if "solver_status" in entry and entry["solver_status"] is not None:
            convexity["solver_status"] = entry["solver_status"]

        if "model_status" in entry and entry["model_status"] is not None:
            convexity["model_status"] = entry["model_status"]

        if "objective_value" in entry and entry["objective_value"] is not None:
            convexity["objective_value"] = entry["objective_value"]

        if "solve_time_seconds" in entry and entry["solve_time_seconds"] is not None:
            convexity["solve_time_seconds"] = entry["solve_time_seconds"]

        # verification_error -> convexity.error
        if "verification_error" in entry and entry["verification_error"]:
            convexity["error"] = entry["verification_error"]

        new_entry["convexity"] = convexity

    # Pipeline stages are NOT added - they're absent until tested
    # nlp2mcp_parse, nlp2mcp_translate, mcp_solve will be absent

    return new_entry


def migrate_catalog(
    catalog: dict[str, Any],
    migration_date: str,
) -> dict[str, Any]:
    """Migrate entire catalog to new schema format.

    Args:
        catalog: Original catalog.json content
        migration_date: ISO 8601 timestamp for migration

    Returns:
        New database in gamslib_status.json format
    """
    models = catalog.get("models", [])
    logger.info(f"Migrating {len(models)} models...")

    transformed_models = []
    for i, entry in enumerate(models):
        transformed = transform_entry(entry, migration_date)
        transformed_models.append(transformed)
        if (i + 1) % 50 == 0:
            logger.info(f"  Migrated {i + 1}/{len(models)} models")

    # Build new database structure
    database: dict[str, Any] = {
        "schema_version": "2.0.0",
        "created_date": migration_date,
        "updated_date": migration_date,
        "total_models": len(transformed_models),
        "models": transformed_models,
    }

    # Preserve gams_version if present
    if catalog.get("gams_version"):
        database["gams_version"] = catalog["gams_version"]

    logger.info(f"Migration complete: {len(transformed_models)} models transformed")
    return database


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
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(database, f, indent=2)
    logger.info(f"Saved {len(database.get('models', []))} models to {path}")


def print_migration_summary(
    source_catalog: dict[str, Any],
    database: dict[str, Any],
) -> None:
    """Print migration summary statistics."""
    source_models = source_catalog.get("models", [])
    dest_models = database.get("models", [])

    print("\n" + "=" * 60)
    print("MIGRATION SUMMARY")
    print("=" * 60)
    print(f"Source: catalog.json (v{source_catalog.get('schema_version', 'unknown')})")
    print(f"Destination: gamslib_status.json (v{database.get('schema_version')})")
    print(f"\nModels migrated: {len(dest_models)}/{len(source_models)}")
    print(f"Schema version: {database.get('schema_version')}")
    print(f"Migration date: {database.get('created_date')}")

    # Count convexity statuses
    status_counts: dict[str, int] = {}
    for model in dest_models:
        convexity = model.get("convexity", {})
        status = convexity.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    print("\nConvexity Status Distribution:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print("=" * 60)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate catalog.json to gamslib_status.json (v2.0.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/gamslib/migrate_catalog.py                    # Migrate and save
    python scripts/gamslib/migrate_catalog.py --dry-run          # Preview only
    python scripts/gamslib/migrate_catalog.py --validate         # Validate output
    python scripts/gamslib/migrate_catalog.py -v --validate      # Verbose + validate
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
        help="Validate output against schema.json",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed progress information",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"Output path (default: {DEFAULT_OUTPUT_PATH})",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=CATALOG_PATH,
        help=f"Input catalog path (default: {CATALOG_PATH})",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load source catalog
    try:
        catalog = load_catalog(args.catalog)
    except FileNotFoundError:
        logger.error(f"Catalog not found: {args.catalog}")
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in catalog: {e}")
        return 1

    # Perform migration
    migration_date = get_utc_timestamp()
    database = migrate_catalog(catalog, migration_date)

    # Print summary
    print_migration_summary(catalog, database)

    # Validate if requested
    if args.validate:
        try:
            schema = load_schema(SCHEMA_PATH)
            errors = validate_database(database, schema)
            if errors:
                logger.error(f"Validation failed with {len(errors)} errors:")
                for error in errors[:10]:  # Show first 10 errors
                    logger.error(f"  - {error}")
                if len(errors) > 10:
                    logger.error(f"  ... and {len(errors) - 10} more errors")
                return 1
            logger.info("Validation passed: all entries valid")
            print("\nValidation: PASSED")
        except FileNotFoundError:
            logger.error(f"Schema not found: {SCHEMA_PATH}")
            return 1

    # Save unless dry-run
    if args.dry_run:
        logger.info("Dry run - not saving output")
        print("\n[DRY RUN] No files written")
    else:
        save_database(database, args.output)
        print(f"\nOutput saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
