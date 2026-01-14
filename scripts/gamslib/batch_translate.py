#!/usr/bin/env python3
"""Batch translate script for GAMSLIB models.

Runs nlp2mcp translation on all successfully parsed models and generates
MCP output files.

Usage:
    python scripts/gamslib/batch_translate.py [OPTIONS]

Options:
    --dry-run      Show what would be done without making changes
    --limit N      Process only first N models (for testing)
    --model ID     Process a single model by ID
    --verbose      Show detailed output for each model
    --save-every N Save database every N models (default: 5)

Filter Options:
    --parse-success       Only process models with parse success status
    --translate-success   Only process models with translate success status
    --translate-failure   Only process models with translate failure status
    --skip-completed      Skip models that already have successful translation
    --error-category CAT  Only process models with specific translate error category
    --model-type TYPE     Only process models of specific type (LP, NLP, QCP, etc.)

Validation Options:
    --validate     Validate generated MCP files using GAMS compile check

Examples:
    python scripts/gamslib/batch_translate.py
    python scripts/gamslib/batch_translate.py --dry-run
    python scripts/gamslib/batch_translate.py --limit 5 --verbose
    python scripts/gamslib/batch_translate.py --model alkyl
    python scripts/gamslib/batch_translate.py --parse-success --limit 10
    python scripts/gamslib/batch_translate.py --translate-failure --limit 5
    python scripts/gamslib/batch_translate.py --model-type NLP --limit 10
    python scripts/gamslib/batch_translate.py --validate
"""

from __future__ import annotations

import argparse
import logging
import subprocess
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
from scripts.gamslib.error_taxonomy import categorize_translate_error
from scripts.gamslib.utils import get_nlp2mcp_version

# Paths
RAW_MODELS_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"
MCP_OUTPUT_DIR = PROJECT_ROOT / "data" / "gamslib" / "mcp"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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
    if args.translate_success and args.translate_failure:
        conflicts.append("--translate-success and --translate-failure are mutually exclusive")

    # --skip-completed and --translate-failure don't conflict (different purposes)
    # --skip-completed skips successful, --translate-failure only runs failures

    if conflicts:
        raise ValueError("Filter conflicts:\n" + "\n".join(f"  - {c}" for c in conflicts))

    # Warn if --error-category used without failure filter
    if args.error_category and not args.translate_failure:
        logger.warning(
            "--error-category specified without --translate-failure. "
            "This may return empty results since error categories only exist on failed models."
        )


def apply_filters(models: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    """Apply filter arguments to model list.

    Filters are applied in order:
    1. Model selection (--model, --model-type)
    2. Parse status filters (--parse-success - required for translation)
    3. Translate status filters (--translate-success, --translate-failure, --skip-completed)
    4. Error filters (--error-category)
    5. Limit (--limit) - applied last

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

    if args.model_type:
        filtered = [m for m in filtered if m.get("gamslib_type") == args.model_type]

    # Phase 2: Parse status filters
    # For translation, we typically want parse_success=True (default behavior)
    # But allow explicit --parse-success flag for consistency with batch_parse
    if args.parse_success:
        filtered = [m for m in filtered if m.get("nlp2mcp_parse", {}).get("status") == "success"]

    # Phase 3: Translate status filters
    if args.translate_success:
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") == "success"
        ]

    if args.translate_failure:
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") == "failure"
        ]

    if args.skip_completed:
        # Skip models that already have successful translation
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") != "success"
        ]

    # Phase 4: Error filters
    if args.error_category:
        filtered = [
            m
            for m in filtered
            if m.get("nlp2mcp_translate", {}).get("error", {}).get("category")
            == args.error_category
        ]

    # Phase 5: Limit (applied last)
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
    if args.model_type:
        filters_applied.append(f"model_type={args.model_type}")
    if args.parse_success:
        filters_applied.append("parse-success")
    if args.translate_success:
        filters_applied.append("translate-success")
    if args.translate_failure:
        filters_applied.append("translate-failure")
    if args.skip_completed:
        filters_applied.append("skip-completed")
    if args.error_category:
        filters_applied.append(f"error-category={args.error_category}")
    if args.limit:
        filters_applied.append(f"limit={args.limit}")

    if filters_applied:
        logger.info(f"Filters applied: {', '.join(filters_applied)}")
        logger.info(f"Models after filtering: {len(filtered)} (from {total} candidates)")
    else:
        logger.info(f"No filters applied, processing all {len(filtered)} candidates")


# =============================================================================
# Translation Functions
# =============================================================================


def translate_single_model(model_path: Path, output_path: Path) -> dict[str, Any]:
    """Translate a single GAMS model to MCP format.

    Args:
        model_path: Path to the .gms file
        output_path: Path where MCP output should be written

    Returns:
        Dictionary with translation results:
        - status: "success" or "failure"
        - translate_time_seconds: Time taken to translate
        - output_file: Path to output file (if successful)
        - error: Error details dict (if failed)
    """
    start_time = time.perf_counter()
    result: dict[str, Any] = {}

    try:
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Run nlp2mcp via subprocess
        cmd = [
            sys.executable,
            "-m",
            "src.cli",
            str(model_path),
            "-o",
            str(output_path),
            "--quiet",
        ]

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        try:
            stdout, stderr = proc.communicate(timeout=60)  # 60 second timeout
            elapsed = time.perf_counter() - start_time

            if proc.returncode == 0:
                # Success - use 4 decimal precision for timing
                result = {
                    "status": "success",
                    "translate_time_seconds": round(elapsed, 4),
                    "output_file": str(output_path.relative_to(PROJECT_ROOT)),
                }
            else:
                # Translation failed
                error_msg = stderr if stderr else stdout
                category = categorize_translate_error(error_msg)
                result = {
                    "status": "failure",
                    "translate_time_seconds": round(elapsed, 4),
                    "error": {
                        "category": category,
                        "message": error_msg[:500],  # Truncate long messages
                    },
                }
        except subprocess.TimeoutExpired:
            # Kill the subprocess on timeout to prevent orphaned processes
            proc.kill()
            proc.communicate()  # Clean up the process
            elapsed = time.perf_counter() - start_time
            result = {
                "status": "failure",
                "translate_time_seconds": round(elapsed, 4),
                "error": {
                    "category": "timeout",
                    "message": "Translation timeout after 60 seconds",
                },
            }

    except Exception as e:
        elapsed = time.perf_counter() - start_time
        error_msg = str(e)
        category = categorize_translate_error(error_msg)

        result = {
            "status": "failure",
            "translate_time_seconds": round(elapsed, 4),
            "error": {
                "category": category,
                "message": error_msg[:500],  # Truncate long messages
            },
        }

    return result


def validate_mcp_file(mcp_path: Path) -> dict[str, Any]:
    """Validate an MCP file using GAMS compile check.

    Uses GAMS action=c to compile-check the generated MCP file without solving.

    Args:
        mcp_path: Path to the MCP .gms file to validate

    Returns:
        Dictionary with validation results:
        - valid: True if compilation succeeds, False otherwise
        - validation_time_seconds: Time taken to validate
        - error: Error message (if validation failed)
    """
    import shutil

    start_time = time.perf_counter()

    # Find GAMS executable
    gams_exe = shutil.which("gams")
    if not gams_exe:
        # Try common GAMS locations
        gams_paths = [
            "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
            "/opt/gams/gams",
            "C:\\GAMS\\win64\\gams.exe",
        ]
        for path in gams_paths:
            if Path(path).exists():
                gams_exe = path
                break

    if not gams_exe:
        return {
            "valid": False,
            "validation_time_seconds": round(time.perf_counter() - start_time, 4),
            "error": "GAMS executable not found",
        }

    try:
        # Run GAMS with action=c (compile only)
        cmd = [
            gams_exe,
            str(mcp_path),
            "action=c",  # Compile only, don't execute
            "lo=0",  # Suppress log output
            "o=/dev/null",  # Suppress listing file (Unix)
        ]

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout for compile check
        )

        elapsed = time.perf_counter() - start_time

        if proc.returncode == 0:
            return {
                "valid": True,
                "validation_time_seconds": round(elapsed, 4),
            }
        else:
            # Extract error from stderr or stdout
            error_msg = proc.stderr if proc.stderr else proc.stdout
            return {
                "valid": False,
                "validation_time_seconds": round(elapsed, 4),
                "error": error_msg[:500] if error_msg else "Compilation failed",
            }

    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "validation_time_seconds": round(time.perf_counter() - start_time, 4),
            "error": "Validation timeout after 30 seconds",
        }
    except Exception as e:
        return {
            "valid": False,
            "validation_time_seconds": round(time.perf_counter() - start_time, 4),
            "error": str(e)[:500],
        }


# =============================================================================
# Batch Processing
# =============================================================================


def get_parsed_models(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Get list of successfully parsed models for translation.

    Args:
        database: Loaded database dictionary

    Returns:
        List of model entries with nlp2mcp_parse.status == "success"
    """
    parsed = []
    for model in database.get("models", []):
        parse_status = model.get("nlp2mcp_parse", {}).get("status")
        if parse_status == "success":
            parsed.append(model)
    return parsed


def run_batch_translate(
    args: argparse.Namespace,
) -> dict[str, Any]:
    """Run batch translate on successfully parsed models.

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

    # Get successfully parsed models as base candidates
    candidates = get_parsed_models(database)
    total_parsed = len(candidates)
    logger.info(f"Found {total_parsed} successfully parsed models")

    # Apply filters (includes --model, --model-type, status filters, --limit)
    candidates = apply_filters(candidates, args)

    # Report filter summary
    report_filter_summary(candidates, total_parsed, args)

    # Check if any candidates remain after filtering
    if not candidates:
        if args.model:
            logger.error(f"Model not found or filtered out: {args.model}")
            return {"error": f"Model not found or filtered out: {args.model}"}
        logger.warning("No models match the specified filters")
        return {"error": "No models match filters"}

    # Get version
    nlp2mcp_version = get_nlp2mcp_version()
    logger.info(f"nlp2mcp version: {nlp2mcp_version}")

    # Create backup before batch operation
    if not args.dry_run:
        backup_path = create_backup()
        if backup_path:
            logger.info(f"Created backup: {backup_path}")

    # Statistics
    stats: dict[str, Any] = {
        "total": len(candidates),
        "processed": 0,
        "success": 0,
        "failure": 0,
        "skipped": 0,
        "successful_models": [],
        "error_categories": {},
        "start_time": time.perf_counter(),
    }
    # Validation stats (only if --validate is used)
    if args.validate:
        stats["validated"] = 0
        stats["validation_passed"] = 0
        stats["validation_failed"] = 0

    # Process each model
    for i, model in enumerate(candidates, 1):
        model_id = model.get("model_id", "unknown")
        model_path = RAW_MODELS_DIR / f"{model_id}.gms"
        output_path = MCP_OUTPUT_DIR / f"{model_id}_mcp.gms"

        # Progress reporting
        if i % 5 == 0 or i == 1:
            elapsed = time.perf_counter() - stats["start_time"]
            avg_time = elapsed / i
            remaining = (len(candidates) - i) * avg_time
            logger.info(
                f"[{i:3d}/{len(candidates)}] {i * 100 // len(candidates):3d}% "
                f"Translating {model_id}... "
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
                logger.info(f"  [DRY-RUN] Would translate {model_id}")
            stats["processed"] += 1
            continue

        # Translate the model
        if args.verbose:
            logger.info(f"  Translating {model_id}...")

        result = translate_single_model(model_path, output_path)
        stats["processed"] += 1

        # Update statistics
        if result["status"] == "success":
            stats["success"] += 1
            stats["successful_models"].append(model_id)
            if args.verbose:
                logger.info(
                    f"    SUCCESS: {result['translate_time_seconds']:.4f}s, "
                    f"output: {result['output_file']}"
                )

            # Validate MCP file if --validate flag is set
            if args.validate:
                validation_result = validate_mcp_file(output_path)
                stats["validated"] += 1
                if validation_result["valid"]:
                    stats["validation_passed"] += 1
                    if args.verbose:
                        logger.info(
                            f"    VALIDATED: {validation_result['validation_time_seconds']:.4f}s"
                        )
                else:
                    stats["validation_failed"] += 1
                    if args.verbose:
                        logger.info(
                            f"    VALIDATION FAILED: {validation_result.get('error', '')[:60]}"
                        )
                # Store validation result
                result["validation"] = validation_result
        else:
            stats["failure"] += 1
            # Track error categories
            error_category = result.get("error", {}).get("category", "unknown")
            stats["error_categories"][error_category] = (
                stats["error_categories"].get(error_category, 0) + 1
            )
            if args.verbose:
                error_msg = result.get("error", {}).get("message", "")
                logger.info(f"    FAILURE [{error_category}]: {error_msg[:60]}")

        # Update database entry
        translate_date = datetime.now(UTC).isoformat()
        translate_entry = {
            "status": result["status"],
            "translate_date": translate_date,
            "nlp2mcp_version": nlp2mcp_version,
            "translate_time_seconds": result.get("translate_time_seconds"),
        }
        if result["status"] == "success":
            translate_entry["output_file"] = result.get("output_file")
            # Add validation result if available
            if "validation" in result:
                translate_entry["validation"] = result["validation"]
        else:
            translate_entry["error"] = result.get("error")

        # Find and update model in database
        for db_model in database.get("models", []):
            if db_model.get("model_id") == model_id:
                db_model["nlp2mcp_translate"] = translate_entry
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
    """Print summary of batch translate results.

    Args:
        stats: Statistics dictionary from run_batch_translate
    """
    print("\n" + "=" * 60)
    print("BATCH TRANSLATE SUMMARY")
    print("=" * 60)

    print(f"\nModels processed: {stats['processed']}/{stats['total']}")
    print(f"  Success: {stats['success']} ({stats['success_rate']:.1f}%)")
    print(f"  Failure: {stats['failure']}")
    print(f"  Skipped: {stats['skipped']}")
    print(f"\nTotal time: {stats['total_time']:.1f}s")
    if stats["processed"] > 0:
        print(f"Average time per model: {stats['total_time'] / stats['processed']:.2f}s")

    # Print error categories if there were failures
    if stats.get("error_categories"):
        print("\nError categories:")
        for category, count in sorted(stats["error_categories"].items(), key=lambda x: -x[1]):
            print(f"  {category}: {count}")

    # Print validation stats if validation was run
    if "validated" in stats:
        print(f"\nValidation (GAMS compile check):")
        print(f"  Validated: {stats['validated']}")
        print(f"  Passed: {stats['validation_passed']}")
        print(f"  Failed: {stats['validation_failed']}")

    if stats["successful_models"]:
        print(f"\nSuccessful translations ({len(stats['successful_models'])}):")
        for model_id in sorted(stats["successful_models"]):
            print(f"  - {model_id}")

    print("=" * 60)


# =============================================================================
# CLI
# =============================================================================


def main() -> int:
    """Main entry point for batch translate script."""
    parser = argparse.ArgumentParser(
        description="Batch translate GAMSLIB models with nlp2mcp",
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
        default=5,
        help="Save database every N models (default: 5)",
    )

    # Filter arguments
    filter_group = parser.add_argument_group("Filter Options")
    filter_group.add_argument(
        "--parse-success",
        action="store_true",
        help="Only process models with parse success status (default behavior)",
    )
    filter_group.add_argument(
        "--translate-success",
        action="store_true",
        help="Only process models with translate success status",
    )
    filter_group.add_argument(
        "--translate-failure",
        action="store_true",
        help="Only process models with translate failure status",
    )
    filter_group.add_argument(
        "--skip-completed",
        action="store_true",
        help="Skip models that already have successful translation",
    )
    filter_group.add_argument(
        "--error-category",
        type=str,
        metavar="CATEGORY",
        help="Only process models with specific translate error category",
    )
    filter_group.add_argument(
        "--model-type",
        dest="model_type",
        type=str,
        metavar="TYPE",
        help="Only process models of specific type (LP, NLP, QCP, etc.)",
    )

    # Validation arguments
    validation_group = parser.add_argument_group("Validation Options")
    validation_group.add_argument(
        "--validate",
        action="store_true",
        help="Validate generated MCP files using GAMS compile check",
    )

    args = parser.parse_args()

    try:
        stats = run_batch_translate(args)
        if "error" in stats:
            logger.error(stats["error"])
            return 1
        print_summary(stats)
        return 0
    except Exception as e:
        logger.error(f"Batch translate failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
