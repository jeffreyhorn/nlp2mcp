#!/usr/bin/env python3
"""Batch parse script for GAMSLIB models.

Runs nlp2mcp parse on all candidate models (verified_convex + likely_convex)
and updates the database with results.

Usage:
    python scripts/gamslib/batch_parse.py [OPTIONS]

Options:
    --dry-run      Show what would be done without making changes
    --limit N      Process only first N models (for testing)
    --model ID     Process a single model by ID
    --verbose      Show detailed output for each model
    --save-every N Save database every N models (default: 10)

Examples:
    python scripts/gamslib/batch_parse.py
    python scripts/gamslib/batch_parse.py --dry-run
    python scripts/gamslib/batch_parse.py --limit 10 --verbose
    python scripts/gamslib/batch_parse.py --model prodmix
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
# Version Detection
# =============================================================================


def get_nlp2mcp_version() -> str:
    """Get the current nlp2mcp version from package metadata.

    Returns:
        Version string (e.g., "0.1.0") or "unknown" if not found
    """
    try:
        # Try importlib.metadata first (Python 3.8+)
        from importlib.metadata import version

        return version("nlp2mcp")
    except Exception as e:
        logger.debug(f"importlib.metadata version lookup failed: {e}")

    # Fallback: try reading from pyproject.toml
    try:
        pyproject = PROJECT_ROOT / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            for line in content.splitlines():
                if line.strip().startswith("version"):
                    # Parse: version = "0.1.0"
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        ver = parts[1].strip().strip('"').strip("'")
                        return ver
    except Exception as e:
        logger.debug(f"pyproject.toml version lookup failed: {e}")

    return "unknown"


# =============================================================================
# Error Categorization
# =============================================================================


def categorize_error(error_message: str) -> str:
    """Categorize a parse error into one of the defined categories.

    Categories from schema.json and PARSE_RATE_BASELINE.md:
    - syntax_error: Parser grammar failures
    - unsupported_feature: Unsupported GAMS functions (gamma, smin, etc.)
    - missing_include: Include file issues
    - timeout: Parse timeout
    - validation_error: Model structure validation failures
    - internal_error: Other/unknown errors

    Additional error patterns from baseline analysis
    (mapped to the schema-defined categories above):
    - no_objective: Model has no objective function -> syntax_error
    - domain_error: Variable domain issues -> validation_error
    - undefined_variable: Objective variable not defined -> validation_error

    Args:
        error_message: The error message string

    Returns:
        Error category string
    """
    msg_lower = error_message.lower()

    # Syntax errors (most common - 77% from baseline)
    if any(
        phrase in msg_lower
        for phrase in [
            "parse error",
            "unexpected character",
            "unexpected token",
            "syntax error",
            "unexpected eof",
        ]
    ):
        return "syntax_error"

    # No objective function
    if "no objective" in msg_lower or "objective function" in msg_lower:
        return "syntax_error"  # Map to syntax_error per schema

    # Unsupported functions
    if "not yet implemented" in msg_lower or "unsupported" in msg_lower:
        return "unsupported_feature"

    # Domain errors
    if "domain" in msg_lower or "incompatible" in msg_lower:
        return "validation_error"

    # Undefined variable
    if "not defined" in msg_lower or "undefined" in msg_lower:
        return "validation_error"

    # Include file issues
    if "include" in msg_lower or "file not found" in msg_lower:
        return "missing_include"

    # Timeout
    if "timeout" in msg_lower:
        return "timeout"

    # Default to internal_error for unknown issues
    return "internal_error"


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
        - parse_time_seconds: Time taken to parse
        - variables_count: Number of variables (if successful)
        - equations_count: Number of equations (if successful)
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

        # Success
        elapsed = time.perf_counter() - start_time
        result = {
            "status": "success",
            "parse_time_seconds": round(elapsed, 3),
            "variables_count": len(model.variables),
            "equations_count": len(model.equations),
        }

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        error_msg = str(e)
        category = categorize_error(error_msg)

        result = {
            "status": "failure",
            "parse_time_seconds": round(elapsed, 3),
            "error": {
                "category": category,
                "message": error_msg[:500],  # Truncate long messages
            },
        }

    return result


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
    # Load database
    logger.info(f"Loading database from {DATABASE_PATH}")
    database = load_database()

    # Get candidate models
    candidates = get_candidate_models(database)
    logger.info(f"Found {len(candidates)} candidate models (verified_convex + likely_convex)")

    # Filter for single model if specified
    if args.model:
        candidates = [m for m in candidates if m.get("model_id") == args.model]
        if not candidates:
            logger.error(f"Model not found or not a candidate: {args.model}")
            return {"error": f"Model not found: {args.model}"}

    # Apply limit
    if args.limit:
        candidates = candidates[: args.limit]
        logger.info(f"Limited to first {args.limit} models")

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
            parse_entry["variables_count"] = result.get("variables_count")
            parse_entry["equations_count"] = result.get("equations_count")
        else:
            parse_entry["error"] = result.get("error")

        # Find and update model in database
        for db_model in database.get("models", []):
            if db_model.get("model_id") == model_id:
                db_model["nlp2mcp_parse"] = parse_entry
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
