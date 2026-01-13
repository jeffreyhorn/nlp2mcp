#!/usr/bin/env python3
"""Batch parse script for GAMSLIB models.

Runs nlp2mcp parse on all candidate models (verified_convex + likely_convex)
and updates the database with results.

Usage:
    python scripts/gamslib/batch_parse.py [OPTIONS]

Options:
    --dry-run           Show what would be done without making changes
    --limit N           Process only first N models (for testing)
    --model ID          Process a single model by ID
    --verbose           Show detailed output for each model
    --save-every N      Save database every N models (default: 10)

Filter Options:
    --only-failing      Only process models with parse failure status
    --parse-success     Only process models with parse success status
    --parse-failure     Only process models with parse failure status
    --error-category C  Only process models with specific error category
    --type TYPE         Only process models of specific type (LP, NLP, QCP, etc.)

Examples:
    python scripts/gamslib/batch_parse.py
    python scripts/gamslib/batch_parse.py --dry-run
    python scripts/gamslib/batch_parse.py --limit 10 --verbose
    python scripts/gamslib/batch_parse.py --model prodmix
    python scripts/gamslib/batch_parse.py --only-failing --limit 10
    python scripts/gamslib/batch_parse.py --type NLP --limit 10
    python scripts/gamslib/batch_parse.py --error-category parser_unexpected_token --limit 5
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import (
    DATABASE_PATH,
    create_backup,
    load_database,
    save_database,
)
from scripts.gamslib.error_taxonomy import categorize_parse_error
from scripts.gamslib.utils import get_nlp2mcp_version

# Paths
RAW_MODELS_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Parse Functions
# =============================================================================


def parse_single_model(model_path: Path) -> dict[str, Any]:
    """Parse a single GAMS model and return results.

    Args:
        model_path: Path to the .gms file

    Returns:
        Dictionary with parse results:
        - status: "success" or "failure"
        - parse_time_seconds: Time taken to parse (4 decimal precision)
        - model_statistics: Dict with variables, equations, parameters, sets counts
        - error: Error details dict (if failed)
    """
    start_time = time.perf_counter()
    result: dict[str, Any] = {}

    try:
        # Import here to avoid loading parser until needed
        from src.ir.parser import parse_model_file
        from src.validation.model import validate_model_structure

        # Parse the model
        model = parse_model_file(model_path)

        # Validate structure
        validate_model_structure(model)

        # Extract model statistics
        elapsed = time.perf_counter() - start_time
        model_statistics = {
            "variables": len(model.variables),
            "equations": len(model.equations),
            "parameters": len(getattr(model, "parameters", {})),
            "sets": len(getattr(model, "sets", {})),
        }

        # Success - use 4 decimal precision for timing
        result = {
            "status": "success",
            "parse_time_seconds": round(elapsed, 4),
            "model_statistics": model_statistics,
            # Keep these for backward compatibility
            "variables_count": model_statistics["variables"],
            "equations_count": model_statistics["equations"],
        }

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        error_msg = str(e)
        category = categorize_parse_error(error_msg)

        result = {
            "status": "failure",
            "parse_time_seconds": round(elapsed, 4),
            "error": {
                "category": category,
                "message": error_msg[:500],  # Truncate long messages
            },
        }

    return result


# =============================================================================
# Filter Functions
# =============================================================================


def validate_filter_args(args: argparse.Namespace) -> None:
    """Validate filter arguments for conflicts.

    Args:
        args: Parsed command line arguments

    Raises:
        ValueError: If conflicting filter arguments are specified
    """
    conflicts = []

    # Check mutually exclusive status flags
    if args.parse_success and args.parse_failure:
        conflicts.append("--parse-success and --parse-failure are mutually exclusive")

    # --only-failing implies --parse-failure for parse stage
    if args.only_failing and args.parse_success:
        conflicts.append("--only-failing and --parse-success are mutually exclusive")

    if conflicts:
        raise ValueError("Filter conflicts:\n" + "\n".join(f"  - {c}" for c in conflicts))


def apply_filters(models: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    """Apply filter arguments to model list.

    Filters are applied in order:
    1. Model selection (--model, --type)
    2. Status filters (--parse-success, --parse-failure, --only-failing)
    3. Error filters (--error-category)
    4. Limit (--limit) - applied last

    Args:
        models: List of candidate model entries
        args: Parsed command line arguments

    Returns:
        Filtered list of model entries
    """
    filtered = models.copy()

    # Phase 1: Model selection
    if args.model:
        filtered = [m for m in filtered if m.get("model_id") == args.model]

    if args.type:
        filtered = [m for m in filtered if m.get("gamslib_type") == args.type]

    # Phase 2: Status filters
    if args.parse_success:
        filtered = [m for m in filtered if m.get("nlp2mcp_parse", {}).get("status") == "success"]

    if args.parse_failure:
        filtered = [m for m in filtered if m.get("nlp2mcp_parse", {}).get("status") == "failure"]

    if args.only_failing:
        # For batch_parse, "failing" means parse status is failure
        filtered = [m for m in filtered if m.get("nlp2mcp_parse", {}).get("status") == "failure"]

    # Phase 3: Error filters
    if args.error_category:
        filtered = [
            m
            for m in filtered
            if m.get("nlp2mcp_parse", {}).get("error", {}).get("category") == args.error_category
        ]

    # Phase 4: Limit (applied last)
    if args.limit:
        filtered = filtered[: args.limit]

    return filtered


def report_filter_summary(
    filtered: list[dict[str, Any]],
    total: int,
    args: argparse.Namespace,
) -> None:
    """Report filter results before processing.

    Args:
        filtered: List of filtered models
        total: Total number of candidate models before filtering
        args: Parsed command line arguments
    """
    filters_applied = []

    if args.model:
        filters_applied.append(f"model={args.model}")
    if args.type:
        filters_applied.append(f"type={args.type}")
    if args.parse_success:
        filters_applied.append("parse-success")
    if args.parse_failure:
        filters_applied.append("parse-failure")
    if args.only_failing:
        filters_applied.append("only-failing")
    if args.error_category:
        filters_applied.append(f"error-category={args.error_category}")
    if args.limit:
        filters_applied.append(f"limit={args.limit}")

    if filters_applied:
        logger.info(f"Filters applied: {', '.join(filters_applied)}")

    logger.info(f"Selected {len(filtered)} of {total} candidate models")

    if total - len(filtered) > 0 and not args.limit:
        logger.info(f"Skipped {total - len(filtered)} models due to filters")


# =============================================================================
# Batch Processing
# =============================================================================


def get_candidate_models(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Get list of candidate models for parsing.

    Candidates are models with convexity.status = 'verified_convex' or 'likely_convex'.

    Args:
        database: Loaded database dictionary

    Returns:
        List of model entries
    """
    candidates = []
    for model in database.get("models", []):
        status = model.get("convexity", {}).get("status")
        if status in ("verified_convex", "likely_convex"):
            candidates.append(model)
    return candidates


def run_batch_parse(
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Run batch parse on candidate models.

    Args:
        args: Parsed command line arguments

    Returns:
        Summary statistics dictionary
    """
    # Validate filter arguments
    validate_filter_args(args)

    # Load database
    logger.info(f"Loading database from {DATABASE_PATH}")
    database = load_database()

    # Get candidate models
    candidates = get_candidate_models(database)
    total_candidates = len(candidates)
    logger.info(f"Found {total_candidates} candidate models (verified_convex + likely_convex)")

    # Apply filters (includes --model, --type, status filters, --limit)
    candidates = apply_filters(candidates, args)

    # Check if any models match filters
    if not candidates:
        if args.model:
            logger.error(f"Model not found or not a candidate: {args.model}")
            return {"error": f"Model not found: {args.model}"}
        logger.warning("No models match the specified filters")
        return {"error": "No models match filters", "total": 0, "processed": 0}

    # Report filter summary
    report_filter_summary(candidates, total_candidates, args)

    # Get version
    nlp2mcp_version = get_nlp2mcp_version()
    logger.info(f"nlp2mcp version: {nlp2mcp_version}")

    # Create backup before batch operation
    if not args.dry_run:
        backup_path = create_backup()
        if backup_path:
            logger.info(f"Created backup: {backup_path}")

    # Statistics
    stats = {
        "total": len(candidates),
        "processed": 0,
        "success": 0,
        "failure": 0,
        "skipped": 0,
        "error_categories": {},
        "successful_models": [],
        "start_time": time.perf_counter(),
    }

    # Process each model
    for i, model in enumerate(candidates, 1):
        model_id = model.get("model_id", "unknown")
        model_path = RAW_MODELS_DIR / f"{model_id}.gms"

        # Progress reporting every 10 models
        if i % 10 == 0 or i == 1:
            elapsed = time.perf_counter() - stats["start_time"]
            avg_time = elapsed / i
            remaining = (len(candidates) - i) * avg_time
            logger.info(
                f"[{i:3d}/{len(candidates)}] {i * 100 // len(candidates):3d}% "
                f"Processing {model_id}... "
                f"({stats['success']} success, {stats['failure']} failure, "
                f"~{remaining:.0f}s remaining)"
            )

        # Check if file exists
        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}")
            stats["skipped"] += 1
            continue

        if args.dry_run:
            if args.verbose:
                logger.info(f"  [DRY-RUN] Would parse {model_id}")
            stats["processed"] += 1
            continue

        # Parse the model
        if args.verbose:
            logger.info(f"  Parsing {model_id}...")

        result = parse_single_model(model_path)
        stats["processed"] += 1

        # Update statistics
        if result["status"] == "success":
            stats["success"] += 1
            stats["successful_models"].append(model_id)
            if args.verbose:
                logger.info(
                    f"    SUCCESS: {result['variables_count']} vars, "
                    f"{result['equations_count']} eqs, "
                    f"{result['parse_time_seconds']:.2f}s"
                )
        else:
            stats["failure"] += 1
            category = result.get("error", {}).get("category", "unknown")
            stats["error_categories"][category] = stats["error_categories"].get(category, 0) + 1
            if args.verbose:
                logger.info(
                    f"    FAILURE ({category}): {result.get('error', {}).get('message', '')[:80]}"
                )

        # Update database entry
        parse_date = datetime.now(UTC).isoformat()
        parse_entry = {
            "status": result["status"],
            "parse_date": parse_date,
            "nlp2mcp_version": nlp2mcp_version,
            "parse_time_seconds": result.get("parse_time_seconds"),
        }
        if result["status"] == "success":
            # Keep variables_count/equations_count for backward compatibility
            parse_entry["variables_count"] = result.get("variables_count")
            parse_entry["equations_count"] = result.get("equations_count")
        else:
            parse_entry["error"] = result.get("error")

        # Find and update model in database
        for db_model in database.get("models", []):
            if db_model.get("model_id") == model_id:
                db_model["nlp2mcp_parse"] = parse_entry
                # Store model_statistics as separate object on success
                if result["status"] == "success" and "model_statistics" in result:
                    db_model["model_statistics"] = result["model_statistics"]
                break

        # Save periodically
        if stats["processed"] % args.save_every == 0:
            save_database(database)
            if args.verbose:
                logger.info(f"  Saved database ({stats['processed']} models processed)")

    # Final save
    if not args.dry_run:
        save_database(database)
        logger.info("Final database save complete")

    # Calculate final stats
    stats["end_time"] = time.perf_counter()
    stats["total_time"] = stats["end_time"] - stats["start_time"]
    stats["success_rate"] = (
        (stats["success"] / stats["processed"] * 100) if stats["processed"] > 0 else 0
    )

    return stats


def print_summary(stats: dict[str, Any]) -> None:
    """Print summary of batch parse results.

    Args:
        stats: Statistics dictionary from run_batch_parse
    """
    print("\n" + "=" * 60)
    print("BATCH PARSE SUMMARY")
    print("=" * 60)

    print(f"\nModels processed: {stats['processed']}/{stats['total']}")
    print(f"  Success: {stats['success']} ({stats['success_rate']:.1f}%)")
    print(f"  Failure: {stats['failure']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"\nTotal time: {stats['total_time']:.1f}s")
    if stats["processed"] > 0:
        print(f"Average time per model: {stats['total_time'] / stats['processed']:.2f}s")

    if stats["error_categories"]:
        print("\nError categories:")
        for category, count in sorted(stats["error_categories"].items(), key=lambda x: -x[1]):
            pct = count / stats["failure"] * 100 if stats["failure"] > 0 else 0
            print(f"  {category}: {count} ({pct:.0f}%)")

    if stats["successful_models"]:
        print(f"\nSuccessful models ({len(stats['successful_models'])}):")
        for model_id in sorted(stats["successful_models"]):
            print(f"  - {model_id}")

    print("=" * 60)


# =============================================================================
# CLI
# =============================================================================


def main() -> int:
    """Main entry point for batch parse script."""
    parser = argparse.ArgumentParser(
        description="Batch parse GAMSLIB models with nlp2mcp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only first N models",
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Process a single model by ID",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each model",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=10,
        help="Save database every N models (default: 10)",
    )

    # Filter arguments
    filter_group = parser.add_argument_group("Filter Options")
    filter_group.add_argument(
        "--only-failing",
        action="store_true",
        help="Only process models with parse failure status",
    )
    filter_group.add_argument(
        "--parse-success",
        action="store_true",
        help="Only process models with parse success status",
    )
    filter_group.add_argument(
        "--parse-failure",
        action="store_true",
        help="Only process models with parse failure status",
    )
    filter_group.add_argument(
        "--error-category",
        type=str,
        metavar="CATEGORY",
        help="Only process models with specific error category",
    )
    filter_group.add_argument(
        "--type",
        type=str,
        metavar="TYPE",
        help="Only process models of specific type (LP, NLP, QCP, etc.)",
    )

    args = parser.parse_args()

    try:
        stats = run_batch_parse(args)
        if "error" in stats:
            logger.error(stats["error"])
            return 1
        print_summary(stats)
        return 0
    except Exception as e:
        logger.error(f"Batch parse failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
