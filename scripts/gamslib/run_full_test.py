#!/usr/bin/env python3
"""Pipeline orchestrator for full nlp2mcp testing.

Runs the complete pipeline: Parse → Translate → Solve → Compare
with comprehensive filtering, cascade failure handling, and progress reporting.

Usage:
    python scripts/gamslib/run_full_test.py [OPTIONS]

Model Selection:
    --model NAME         Process single model by ID
    --type TYPE          Filter by GAMS type: LP, NLP, QCP
    --limit N            Process only first N models (after other filters)
    --random N           Process N random models (after other filters)

Status Filters:
    --parse-success      Only models that parsed successfully
    --parse-failure      Only models that failed parsing
    --translate-success  Only models that translated successfully
    --translate-failure  Only models that failed translation
    --solve-success      Only models that solved successfully
    --solve-failure      Only models that failed solving

Stage Control:
    --only-parse         Run only parse stage
    --only-translate     Run only translate stage (requires parse success)
    --only-solve         Run only solve stage (requires translate success)

Convenience:
    --only-failing       Re-run models where any stage failed
    --skip-completed     Skip models where all stages succeeded
    --quick              Shorthand for --limit=10

Output:
    --dry-run            Preview without execution
    --verbose, -v        Show detailed output for each model
    --quiet, -q          Suppress progress output, show only summary
    --json               Output results as JSON (machine-readable)

Examples:
    python scripts/gamslib/run_full_test.py --model trnsport --verbose
    python scripts/gamslib/run_full_test.py --quick
    python scripts/gamslib/run_full_test.py --only-parse --limit 5
    python scripts/gamslib/run_full_test.py --only-failing
    python scripts/gamslib/run_full_test.py --type LP --only-translate
    python scripts/gamslib/run_full_test.py --dry-run --type LP
    python scripts/gamslib/run_full_test.py --json > results.json
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import statistics
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.db_manager import (  # noqa: E402
    DATABASE_PATH,
    create_backup,
    load_database,
    save_database,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# =============================================================================
# Stage Imports (imported at runtime to avoid circular imports)
# =============================================================================


def get_parse_function():
    """Import and return the parse function from batch_parse."""
    from scripts.gamslib.batch_parse import parse_single_model

    return parse_single_model


def get_translate_function():
    """Import and return the translate function from batch_translate."""
    from scripts.gamslib.batch_translate import translate_single_model

    return translate_single_model


def get_solve_function():
    """Import and return the solve function from test_solve."""
    from scripts.gamslib.test_solve import solve_mcp

    return solve_mcp


def get_compare_function():
    """Import and return the compare function from test_solve."""
    from scripts.gamslib.test_solve import compare_solutions

    return compare_solutions


# =============================================================================
# Filter Validation
# =============================================================================


def validate_filters(args: argparse.Namespace) -> None:
    """Validate filter arguments for conflicts.

    Args:
        args: Parsed command line arguments

    Raises:
        ValueError: If conflicting filter arguments are specified
    """
    conflicts = []

    # Mutually exclusive status pairs
    if args.parse_success and args.parse_failure:
        conflicts.append("--parse-success and --parse-failure are mutually exclusive")
    if args.translate_success and args.translate_failure:
        conflicts.append("--translate-success and --translate-failure are mutually exclusive")
    if args.solve_success and args.solve_failure:
        conflicts.append("--solve-success and --solve-failure are mutually exclusive")

    # Only-* stage conflicts (can only run one stage with --only-*)
    only_flags = [args.only_parse, args.only_translate, args.only_solve]
    if sum(only_flags) > 1:
        conflicts.append("Only one --only-* flag can be specified at a time")

    # Cannot skip and only-run same stage (logic conflicts)
    # Note: We don't have --skip-parse etc. in MVP, but logic is ready for future

    if conflicts:
        raise ValueError("Filter conflicts:\n" + "\n".join(f"  - {c}" for c in conflicts))


# =============================================================================
# Filter Application
# =============================================================================


def get_candidate_models(database: dict[str, Any]) -> list[dict[str, Any]]:
    """Get list of candidate models for processing.

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


def apply_filters(
    models: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    """Apply filter arguments to model list.

    Filters are applied in order:
    1. Model selection (--model, --type)
    2. Status filters (--parse-success, --only-failing, etc.)
    3. Limit/random (--limit, --random) - applied last

    All filters use AND logic (all must match).

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

    if args.translate_success:
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") == "success"
        ]

    if args.translate_failure:
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") == "failure"
        ]

    if args.solve_success:
        filtered = [m for m in filtered if m.get("mcp_solve", {}).get("status") == "success"]

    if args.solve_failure:
        filtered = [m for m in filtered if m.get("mcp_solve", {}).get("status") == "failure"]

    if args.only_failing:
        filtered = [m for m in filtered if _has_any_failure(m)]

    if args.skip_completed:
        filtered = [m for m in filtered if not _is_fully_completed(m)]

    # Phase 3: Limit/random (applied last)
    if args.random:
        # Use deterministic seed based on filtered model IDs for reproducibility
        seed_basis = tuple(m.get("model_id", "") for m in filtered)
        rng = random.Random(hash(seed_basis))
        filtered = rng.sample(filtered, min(args.random, len(filtered)))
    elif args.limit:
        filtered = filtered[: args.limit]

    return filtered


def _has_any_failure(model: dict[str, Any]) -> bool:
    """Check if model has any failure status across pipeline stages.

    Args:
        model: Model dictionary

    Returns:
        True if any stage has failure status
    """
    parse_status = model.get("nlp2mcp_parse", {}).get("status")
    translate_status = model.get("nlp2mcp_translate", {}).get("status")
    solve_status = model.get("mcp_solve", {}).get("status")
    compare_status = model.get("solution_comparison", {}).get("comparison_status")

    return any(
        (
            parse_status == "failure",
            translate_status == "failure",
            solve_status == "failure",
            compare_status == "mismatch",
        )
    )


def _is_fully_completed(model: dict[str, Any]) -> bool:
    """Check if all stages completed successfully.

    A model is considered "fully completed" only when all stages succeeded
    AND comparison resulted in a match. Models where comparison was 'skipped'
    are NOT considered fully completed.

    Args:
        model: Model dictionary

    Returns:
        True if all stages completed successfully with match
    """
    parse_status = model.get("nlp2mcp_parse", {}).get("status")
    translate_status = model.get("nlp2mcp_translate", {}).get("status")
    solve_status = model.get("mcp_solve", {}).get("status")
    compare_status = model.get("solution_comparison", {}).get("comparison_status")

    return all(
        (
            parse_status == "success",
            translate_status == "success",
            solve_status == "success",
            compare_status == "match",
        )
    )


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
    if args.translate_success:
        filters_applied.append("translate-success")
    if args.translate_failure:
        filters_applied.append("translate-failure")
    if args.solve_success:
        filters_applied.append("solve-success")
    if args.solve_failure:
        filters_applied.append("solve-failure")
    if args.only_failing:
        filters_applied.append("only-failing")
    if args.skip_completed:
        filters_applied.append("skip-completed")
    if args.random:
        filters_applied.append(f"random={args.random}")
    if args.limit:
        filters_applied.append(f"limit={args.limit}")
    if args.quick:
        filters_applied.append("quick")

    if filters_applied:
        logger.info(f"Filters applied: {', '.join(filters_applied)}")

    logger.info(f"Selected {len(filtered)} of {total} models matching filters")

    if total - len(filtered) > 0:
        logger.info(f"Skipped {total - len(filtered)} models due to filters")


# =============================================================================
# Stage Orchestration
# =============================================================================


def run_parse_stage(
    model: dict[str, Any],
    model_path: Path,
    args: argparse.Namespace,
    stats: dict[str, Any],
) -> dict[str, Any]:
    """Run parse stage for a model.

    Args:
        model: Model dictionary from database
        model_path: Path to the .gms file
        args: Command line arguments
        stats: Statistics dictionary to update

    Returns:
        Parse result dictionary
    """
    from scripts.gamslib.utils import get_nlp2mcp_version

    parse_func = get_parse_function()

    if args.verbose:
        logger.info("    [PARSE] Starting...")

    result = parse_func(model_path)

    # Update model in database
    parse_date = datetime.now(UTC).isoformat()
    parse_entry = {
        "status": result["status"],
        "parse_date": parse_date,
        "nlp2mcp_version": get_nlp2mcp_version(),
        "parse_time_seconds": result.get("parse_time_seconds"),
    }

    # Collect timing data
    model_id = model.get("model_id", "unknown")
    parse_time = result.get("parse_time_seconds")
    if parse_time is not None:
        stats["parse_times"].append((model_id, parse_time))

    if result["status"] == "success":
        parse_entry["variables_count"] = result.get("variables_count")
        parse_entry["equations_count"] = result.get("equations_count")
        stats["parse_success"] += 1
        if args.verbose:
            logger.info(
                f"    [PARSE] SUCCESS: {result.get('variables_count', 0)} vars, "
                f"{result.get('equations_count', 0)} eqs"
            )
    else:
        parse_entry["error"] = result.get("error")
        stats["parse_failure"] += 1
        error_cat = result.get("error", {}).get("category", "unknown")
        stats["parse_errors"].append(error_cat)
        if args.verbose:
            logger.info(f"    [PARSE] FAILURE: {error_cat}")

    model["nlp2mcp_parse"] = parse_entry

    # Store model_statistics if available
    if result["status"] == "success" and "model_statistics" in result:
        model["model_statistics"] = result["model_statistics"]

    return result


def run_translate_stage(
    model: dict[str, Any],
    model_path: Path,
    output_path: Path,
    args: argparse.Namespace,
    stats: dict[str, Any],
) -> dict[str, Any]:
    """Run translate stage for a model.

    Args:
        model: Model dictionary from database
        model_path: Path to the .gms file
        output_path: Path for MCP output
        args: Command line arguments
        stats: Statistics dictionary to update

    Returns:
        Translate result dictionary
    """
    from scripts.gamslib.utils import get_nlp2mcp_version

    translate_func = get_translate_function()

    if args.verbose:
        logger.info("    [TRANSLATE] Starting...")

    result = translate_func(model_path, output_path)

    # Update model in database
    translate_date = datetime.now(UTC).isoformat()
    translate_entry = {
        "status": result["status"],
        "translate_date": translate_date,
        "nlp2mcp_version": get_nlp2mcp_version(),
        "translate_time_seconds": result.get("translate_time_seconds"),
    }

    # Collect timing data
    model_id = model.get("model_id", "unknown")
    translate_time = result.get("translate_time_seconds")
    if translate_time is not None:
        stats["translate_times"].append((model_id, translate_time))

    if result["status"] == "success":
        translate_entry["output_file"] = result.get("output_file")
        stats["translate_success"] += 1
        if args.verbose:
            logger.info(f"    [TRANSLATE] SUCCESS: {result.get('output_file')}")
    else:
        translate_entry["error"] = result.get("error")
        stats["translate_failure"] += 1
        error_cat = result.get("error", {}).get("category", "unknown")
        stats["translate_errors"].append(error_cat)
        if args.verbose:
            logger.info(f"    [TRANSLATE] FAILURE: {error_cat}")

    model["nlp2mcp_translate"] = translate_entry
    return result


def run_solve_stage(
    model: dict[str, Any],
    mcp_path: Path,
    args: argparse.Namespace,
    stats: dict[str, Any],
) -> dict[str, Any]:
    """Run solve stage for a model.

    Args:
        model: Model dictionary from database
        mcp_path: Path to the MCP .gms file
        args: Command line arguments
        stats: Statistics dictionary to update

    Returns:
        Solve result dictionary
    """
    solve_func = get_solve_function()

    if args.verbose:
        logger.info("    [SOLVE] Starting...")

    result = solve_func(mcp_path, timeout=60)

    # Update model in database
    solve_date = datetime.now(UTC).isoformat()
    solve_entry = {
        "status": result["status"],
        "solve_date": solve_date,
        "solver": "PATH",
        "solver_version": result.get("solver_version"),
        "solver_status": result.get("solver_status"),
        "solver_status_text": result.get("solver_status_text"),
        "model_status": result.get("model_status"),
        "model_status_text": result.get("model_status_text"),
        "objective_value": result.get("objective_value"),
        "solve_time_seconds": result.get("solve_time_seconds"),
        "iterations": result.get("iterations"),
        "outcome_category": result.get("outcome_category"),
    }

    # Collect timing data
    model_id = model.get("model_id", "unknown")
    solve_time = result.get("solve_time_seconds")
    if solve_time is not None:
        stats["solve_times"].append((model_id, solve_time))

    if result["status"] == "success":
        stats["solve_success"] += 1
        if args.verbose:
            obj = result.get("objective_value")
            obj_str = f"{obj:.6g}" if obj is not None else "N/A"
            logger.info(f"    [SOLVE] SUCCESS: objective={obj_str}")
    else:
        solve_entry["error"] = {
            "category": result.get("outcome_category"),
            "message": result.get("error", "Unknown error"),
        }
        stats["solve_failure"] += 1
        error_cat = result.get("outcome_category", "unknown")
        stats["solve_errors"].append(error_cat)
        if args.verbose:
            logger.info(f"    [SOLVE] FAILURE: {error_cat}")

    model["mcp_solve"] = solve_entry
    return result


def run_compare_stage(
    model: dict[str, Any],
    args: argparse.Namespace,
    stats: dict[str, Any],
) -> dict[str, Any]:
    """Run comparison stage for a model.

    Args:
        model: Model dictionary from database (must have mcp_solve results)
        args: Command line arguments
        stats: Statistics dictionary to update

    Returns:
        Comparison result dictionary
    """
    compare_func = get_compare_function()

    if args.verbose:
        logger.info("    [COMPARE] Starting...")

    result = compare_func(model)

    # Update model in database
    model["solution_comparison"] = result

    comparison_status = result.get("comparison_status")
    if comparison_status == "match":
        stats["compare_match"] += 1
        if args.verbose:
            logger.info("    [COMPARE] MATCH")
    elif comparison_status == "mismatch":
        stats["compare_mismatch"] += 1
        if args.verbose:
            logger.info(f"    [COMPARE] MISMATCH: {result.get('notes')}")
    else:
        stats["compare_skipped"] += 1
        if args.verbose:
            logger.info(f"    [COMPARE] SKIPPED: {result.get('notes')}")

    return result


def mark_cascade_not_tested(
    model: dict[str, Any],
    failed_stage: str,
    stats: dict[str, Any],
) -> None:
    """Mark downstream stages as not_tested due to upstream failure.

    For cascade skips, we set status to 'not_tested' without an error object,
    since the failure reason is already recorded in the upstream stage.
    The solution_comparison uses 'notes' field to indicate cascade skip.

    Args:
        model: Model dictionary to update
        failed_stage: The stage that failed ("parse", "translate", "solve")
        stats: Statistics dictionary to update
    """
    cascade_date = datetime.now(UTC).isoformat()

    if failed_stage == "parse":
        # Mark translate, solve, compare as not_tested
        # Don't include error object - status 'not_tested' is sufficient
        model["nlp2mcp_translate"] = {
            "status": "not_tested",
            "translate_date": cascade_date,
        }
        model["mcp_solve"] = {
            "status": "not_tested",
            "solve_date": cascade_date,
        }
        model["solution_comparison"] = {
            "comparison_status": "not_tested",
            "comparison_date": cascade_date,
            "notes": "Skipped due to parse failure",
        }
        stats["translate_cascade_skip"] += 1
        stats["solve_cascade_skip"] += 1
        stats["compare_cascade_skip"] += 1

    elif failed_stage == "translate":
        # Mark solve, compare as not_tested
        model["mcp_solve"] = {
            "status": "not_tested",
            "solve_date": cascade_date,
        }
        model["solution_comparison"] = {
            "comparison_status": "not_tested",
            "comparison_date": cascade_date,
            "notes": "Skipped due to translate failure",
        }
        stats["solve_cascade_skip"] += 1
        stats["compare_cascade_skip"] += 1

    elif failed_stage == "solve":
        # Mark compare as not_tested
        model["solution_comparison"] = {
            "comparison_status": "not_tested",
            "comparison_date": cascade_date,
            "notes": "Skipped due to solve failure",
        }
        stats["compare_cascade_skip"] += 1


def _determine_stages(args: argparse.Namespace) -> list[str]:
    """Determine which pipeline stages to run based on --only-* flags.

    Args:
        args: Parsed command line arguments

    Returns:
        List of stage names to run
    """
    stages: list[str] = []
    if not args.only_translate and not args.only_solve:
        stages.append("parse")
    if not args.only_parse and not args.only_solve:
        stages.append("translate")
    if not args.only_parse and not args.only_translate:
        stages.append("solve")
        stages.append("compare")
    return stages


def run_pipeline(
    model: dict[str, Any],
    database: dict[str, Any],
    args: argparse.Namespace,
    stats: dict[str, Any],
) -> None:
    """Run the full pipeline for a single model.

    Handles stage selection (--only-*) and cascade failure handling.

    Args:
        model: Model dictionary from database
        database: Full database (reserved for future cross-model lookups)
        args: Command line arguments
        stats: Statistics dictionary to update
    """
    model_id = model.get("model_id", "unknown")

    # Paths
    raw_models_dir = PROJECT_ROOT / "data" / "gamslib" / "raw"
    mcp_output_dir = PROJECT_ROOT / "data" / "gamslib" / "mcp"
    model_path = raw_models_dir / f"{model_id}.gms"
    mcp_path = mcp_output_dir / f"{model_id}_mcp.gms"

    # Check if model file exists
    if not model_path.exists():
        logger.warning(f"  Model file not found: {model_path}")
        stats["skipped"] += 1
        return

    # Determine which stages to run based on --only-* flags
    if args.only_translate:
        # For --only-translate: require existing parse success
        if model.get("nlp2mcp_parse", {}).get("status") != "success":
            if args.verbose:
                logger.info("  Skipped: requires parse success for --only-translate")
            stats["skipped"] += 1
            return
        run_parse = False
        run_translate = True
        run_solve = False
        run_compare = False
    elif args.only_solve:
        # For --only-solve: require existing translate success
        if model.get("nlp2mcp_translate", {}).get("status") != "success":
            if args.verbose:
                logger.info("  Skipped: requires translate success for --only-solve")
            stats["skipped"] += 1
            return
        run_parse = False
        run_translate = False
        run_solve = True
        run_compare = True
    elif args.only_parse:
        run_parse = True
        run_translate = False
        run_solve = False
        run_compare = False
    else:
        run_parse = True
        run_translate = True
        run_solve = True
        run_compare = True  # Compare only if solve is run

    # Stage 1: Parse
    if run_parse:
        result = run_parse_stage(model, model_path, args, stats)
        if result["status"] != "success":
            if run_translate or run_solve or run_compare:
                mark_cascade_not_tested(model, "parse", stats)
                if args.verbose:
                    logger.info("    [CASCADE] Downstream stages marked not_tested")
            return

    # Stage 2: Translate
    if run_translate:
        result = run_translate_stage(model, model_path, mcp_path, args, stats)
        if result["status"] != "success":
            if run_solve or run_compare:
                mark_cascade_not_tested(model, "translate", stats)
                if args.verbose:
                    logger.info("    [CASCADE] Downstream stages marked not_tested")
            return

    # Stage 3: Solve
    if run_solve:
        # Need MCP file to exist
        if not mcp_path.exists():
            # Try to get path from translate result in database
            translate_result = model.get("nlp2mcp_translate", {})
            if translate_result.get("output_file"):
                mcp_path = PROJECT_ROOT / translate_result["output_file"]

        if not mcp_path.exists():
            if args.verbose:
                logger.info("    [SOLVE] Skipped: MCP file not found")
            # mark_cascade_not_tested increments compare_cascade_skip
            mark_cascade_not_tested(model, "solve", stats)
            return

        result = run_solve_stage(model, mcp_path, args, stats)
        if result["status"] != "success":
            if run_compare:
                mark_cascade_not_tested(model, "solve", stats)
            return

    # Stage 4: Compare
    if run_compare:
        run_compare_stage(model, args, stats)


# =============================================================================
# Main Orchestration
# =============================================================================


def run_full_test(args: argparse.Namespace) -> dict[str, Any]:
    """Run the full test pipeline with filtering and orchestration.

    Args:
        args: Parsed command line arguments

    Returns:
        Statistics dictionary
    """
    # Validate filter arguments
    validate_filters(args)

    # Handle --quick shorthand
    if args.quick and not args.limit:
        args.limit = 10

    # Load database
    if not args.quiet:
        logger.info(f"Loading database from {DATABASE_PATH}")
    database = load_database()

    # Get candidate models
    candidates = get_candidate_models(database)
    total_candidates = len(candidates)
    if not args.quiet:
        logger.info(f"Found {total_candidates} candidate models (verified_convex + likely_convex)")

    # Apply filters
    filtered = apply_filters(candidates, args)

    # Report filter summary
    if not args.quiet:
        report_filter_summary(filtered, total_candidates, args)

    # Check if any models match
    if not filtered:
        if args.model:
            logger.error(f"Model not found or not a candidate: {args.model}")
            return {"error": f"Model not found: {args.model}"}
        logger.warning("No models match the specified filters")
        return {"error": "No models match filters", "total": 0}

    # Dry run mode
    if args.dry_run:
        stages = _determine_stages(args)
        stage_str = " → ".join(s.capitalize() for s in stages)

        # Count models by type
        type_counts: dict[str, int] = {}
        for model in filtered:
            model_type = model.get("gamslib_type", "Unknown")
            type_counts[model_type] = type_counts.get(model_type, 0) + 1

        print("\n" + "=" * 60)
        print("[DRY RUN] Pipeline Preview")
        print("=" * 60)
        print(f"\nWould process {len(filtered)} models through: {stage_str}")
        print("\nModels by type:")
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t}: {count}")

        if args.verbose or len(filtered) <= 20:
            print("\nModels to process:")
            for model in filtered:
                model_id = model.get("model_id", "unknown")
                model_type = model.get("gamslib_type", "?")
                print(f"  - {model_id} ({model_type})")
        else:
            print(f"\n(Use --verbose to see all {len(filtered)} model names)")

        print("=" * 60)

        if args.json:
            dry_run_result = {
                "dry_run": True,
                "models": len(filtered),
                "stages": stages,
                "by_type": type_counts,
                "model_ids": [m.get("model_id", "unknown") for m in filtered],
            }
            print(json.dumps(dry_run_result, indent=2))

        return {"dry_run": True, "models": len(filtered)}

    # Create backup before batch operation
    backup_path = create_backup()
    if backup_path and not args.quiet:
        logger.info(f"Created backup: {backup_path}")

    # Initialize statistics
    stats: dict[str, Any] = {
        "total": len(filtered),
        "processed": 0,
        "skipped": 0,
        # Parse stats
        "parse_success": 0,
        "parse_failure": 0,
        "parse_times": [],  # List of (model_id, time) for timing stats
        "parse_errors": [],  # List of error categories
        # Translate stats
        "translate_success": 0,
        "translate_failure": 0,
        "translate_cascade_skip": 0,
        "translate_times": [],
        "translate_errors": [],
        # Solve stats
        "solve_success": 0,
        "solve_failure": 0,
        "solve_cascade_skip": 0,
        "solve_times": [],
        "solve_errors": [],
        # Compare stats
        "compare_match": 0,
        "compare_mismatch": 0,
        "compare_skipped": 0,
        "compare_cascade_skip": 0,
        # Timing
        "start_time": time.perf_counter(),
    }

    # Determine active stages for progress reporting
    active_stages = [s.capitalize() for s in _determine_stages(args)]

    if not args.quiet:
        logger.info(f"\nPipeline stages: {' → '.join(active_stages)}")
        logger.info("=" * 60)

    # Process each model
    for i, model in enumerate(filtered, 1):
        model_id = model.get("model_id", "unknown")

        # Progress reporting
        if not args.quiet:
            elapsed = time.perf_counter() - stats["start_time"]
            avg_time = elapsed / i if i > 0 else 0
            remaining = (len(filtered) - i) * avg_time
            pct = i * 100 // len(filtered)
            logger.info(
                f"[{i:3d}/{len(filtered)}] {pct:3d}% Processing {model_id}... "
                f"(~{remaining:.0f}s remaining)"
            )

        # Run pipeline for this model
        run_pipeline(model, database, args, stats)
        stats["processed"] += 1

        # Periodic save (every 10 models)
        if stats["processed"] % 10 == 0:
            save_database(database)
            if args.verbose:
                logger.info(f"  Database saved ({stats['processed']} models processed)")

    # Final save
    save_database(database)
    if not args.quiet:
        logger.info("\nFinal database save complete")

    # Calculate final stats
    stats["end_time"] = time.perf_counter()
    stats["total_time"] = stats["end_time"] - stats["start_time"]

    return stats


def compute_timing_stats(times: list[tuple[str, float]]) -> dict[str, Any]:
    """Compute timing statistics from a list of (model_id, time) tuples.

    Args:
        times: List of (model_id, time_seconds) tuples

    Returns:
        Dictionary with timing statistics (mean, median, stddev, min, max, p90, p99)
    """
    if not times:
        return {}

    values = [t for _, t in times]
    sorted_values = sorted(values)
    n = len(values)

    def percentile(p: float) -> float:
        """Calculate percentile value."""
        k = (n - 1) * p / 100
        f = int(k)
        c = min(f + 1, n - 1)
        return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])

    return {
        "count": n,
        "mean": round(statistics.mean(values), 4),
        "median": round(statistics.median(values), 4),
        "stddev": round(statistics.pstdev(values), 4) if n > 1 else 0.0,
        "min": round(min(values), 4),
        "max": round(max(values), 4),
        "p90": round(percentile(90), 4),
        "p99": round(percentile(99), 4),
    }


def generate_summary(stats: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Generate comprehensive summary statistics.

    Args:
        stats: Raw statistics dictionary from run_full_test
        args: Command line arguments

    Returns:
        Structured summary dictionary suitable for JSON output
    """
    summary: dict[str, Any] = {
        "run_date": datetime.now(UTC).isoformat(),
        "total_models": stats["total"],
        "processed": stats["processed"],
        "skipped": stats["skipped"],
        "total_time_seconds": round(stats.get("total_time", 0), 2),
    }

    # Parse statistics
    if not args.only_translate and not args.only_solve:
        parse_total = stats["parse_success"] + stats["parse_failure"]
        if parse_total > 0:
            summary["parse"] = {
                "attempted": parse_total,
                "success": stats["parse_success"],
                "failure": stats["parse_failure"],
                "success_rate": round(stats["parse_success"] / parse_total, 4),
                "timing": compute_timing_stats(stats.get("parse_times", [])),
                "error_breakdown": dict(Counter(stats.get("parse_errors", []))),
            }

    # Translate statistics
    if not args.only_parse and not args.only_solve:
        translate_total = stats["translate_success"] + stats["translate_failure"]
        if translate_total > 0:
            summary["translate"] = {
                "attempted": translate_total,
                "success": stats["translate_success"],
                "failure": stats["translate_failure"],
                "cascade_skip": stats["translate_cascade_skip"],
                "success_rate": round(stats["translate_success"] / translate_total, 4),
                "timing": compute_timing_stats(stats.get("translate_times", [])),
                "error_breakdown": dict(Counter(stats.get("translate_errors", []))),
            }

    # Solve statistics
    if not args.only_parse and not args.only_translate:
        solve_total = stats["solve_success"] + stats["solve_failure"]
        if solve_total > 0:
            summary["solve"] = {
                "attempted": solve_total,
                "success": stats["solve_success"],
                "failure": stats["solve_failure"],
                "cascade_skip": stats["solve_cascade_skip"],
                "success_rate": round(stats["solve_success"] / solve_total, 4),
                "timing": compute_timing_stats(stats.get("solve_times", [])),
                "error_breakdown": dict(Counter(stats.get("solve_errors", []))),
            }

        # Compare statistics
        compare_total = stats["compare_match"] + stats["compare_mismatch"]
        summary["compare"] = {
            "attempted": compare_total,
            "match": stats["compare_match"],
            "mismatch": stats["compare_mismatch"],
            "skipped": stats["compare_skipped"],
            "cascade_skip": stats["compare_cascade_skip"],
            "match_rate": (
                round(stats["compare_match"] / compare_total, 4) if compare_total > 0 else 0.0
            ),
        }

    # Full pipeline success
    if not args.only_parse and not args.only_translate and not args.only_solve:
        full_success = stats["compare_match"]
        processed = stats["processed"]
        summary["full_pipeline"] = {
            "success": full_success,
            "total": processed,
            "success_rate": round(full_success / processed, 4) if processed > 0 else 0.0,
        }

    return summary


def print_summary(stats: dict[str, Any], args: argparse.Namespace) -> None:
    """Print summary of pipeline results.

    Args:
        stats: Statistics dictionary from run_full_test
        args: Command line arguments
    """
    summary = generate_summary(stats, args)

    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    print(f"\nModels processed: {summary['processed']}/{summary['total_models']}")
    if summary["skipped"] > 0:
        print(f"Models skipped: {summary['skipped']}")

    # Parse results
    if "parse" in summary:
        p = summary["parse"]
        print("\nParse Results:")
        print(f"  Success: {p['success']} ({p['success_rate'] * 100:.1f}%)")
        print(f"  Failure: {p['failure']}")
        if p.get("timing"):
            t = p["timing"]
            print(
                f"  Timing: mean={t['mean']:.2f}s, median={t['median']:.2f}s, p90={t['p90']:.2f}s"
            )
        if p.get("error_breakdown"):
            print("  Error breakdown:")
            for cat, count in sorted(p["error_breakdown"].items(), key=lambda x: -x[1]):
                print(f"    {cat}: {count}")

    # Translate results
    if "translate" in summary:
        tr = summary["translate"]
        print("\nTranslate Results:")
        print(f"  Success: {tr['success']} ({tr['success_rate'] * 100:.1f}%)")
        print(f"  Failure: {tr['failure']}")
        if tr["cascade_skip"] > 0:
            print(f"  Cascade skipped: {tr['cascade_skip']}")
        if tr.get("timing"):
            tm = tr["timing"]
            print(
                f"  Timing: mean={tm['mean']:.2f}s, median={tm['median']:.2f}s, p90={tm['p90']:.2f}s"
            )
        if tr.get("error_breakdown"):
            print("  Error breakdown:")
            for cat, count in sorted(tr["error_breakdown"].items(), key=lambda x: -x[1]):
                print(f"    {cat}: {count}")

    # Solve results
    if "solve" in summary:
        s = summary["solve"]
        print("\nSolve Results:")
        print(f"  Success: {s['success']} ({s['success_rate'] * 100:.1f}%)")
        print(f"  Failure: {s['failure']}")
        if s["cascade_skip"] > 0:
            print(f"  Cascade skipped: {s['cascade_skip']}")
        if s.get("timing"):
            tm = s["timing"]
            print(
                f"  Timing: mean={tm['mean']:.2f}s, median={tm['median']:.2f}s, p90={tm['p90']:.2f}s"
            )
        if s.get("error_breakdown"):
            print("  Error breakdown:")
            for cat, count in sorted(s["error_breakdown"].items(), key=lambda x: -x[1]):
                print(f"    {cat}: {count}")

    # Compare results
    if "compare" in summary:
        c = summary["compare"]
        if c["attempted"] > 0:
            print("\nComparison Results:")
            print(f"  Match: {c['match']} ({c['match_rate'] * 100:.1f}%)")
            print(f"  Mismatch: {c['mismatch']}")
        if c["skipped"] > 0:
            print(f"  Skipped: {c['skipped']}")
        if c["cascade_skip"] > 0:
            print(f"  Cascade skipped: {c['cascade_skip']}")

    # Full pipeline success
    if "full_pipeline" in summary:
        fp = summary["full_pipeline"]
        print(
            f"\nFull pipeline success: {fp['success']}/{fp['total']} ({fp['success_rate'] * 100:.1f}%)"
        )

    # Timing
    print(f"\nTotal time: {summary['total_time_seconds']:.1f}s")
    if summary["processed"] > 0:
        avg_time = summary["total_time_seconds"] / summary["processed"]
        print(f"Average time per model: {avg_time:.2f}s")

    print("=" * 60)


def print_json_summary(stats: dict[str, Any], args: argparse.Namespace) -> None:
    """Print summary as JSON.

    Args:
        stats: Statistics dictionary from run_full_test
        args: Command line arguments
    """
    summary = generate_summary(stats, args)
    print(json.dumps(summary, indent=2))


# =============================================================================
# CLI
# =============================================================================


def main() -> int:
    """Main entry point for pipeline orchestrator."""
    parser = argparse.ArgumentParser(
        description="Run full nlp2mcp pipeline: Parse → Translate → Solve → Compare",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Model selection
    selection_group = parser.add_argument_group("Model Selection")
    selection_group.add_argument(
        "--model",
        type=str,
        help="Process single model by ID",
    )
    selection_group.add_argument(
        "--type",
        type=str,
        choices=["LP", "NLP", "QCP", "MIP", "MINLP", "MIQCP"],
        help="Filter by GAMS type",
    )
    selection_group.add_argument(
        "--limit",
        type=int,
        help="Process only first N models (after other filters)",
    )
    selection_group.add_argument(
        "--random",
        type=int,
        help="Process N random models (after other filters)",
    )

    # Status filters
    status_group = parser.add_argument_group("Status Filters")
    status_group.add_argument(
        "--parse-success",
        action="store_true",
        help="Only models that parsed successfully",
    )
    status_group.add_argument(
        "--parse-failure",
        action="store_true",
        help="Only models that failed parsing",
    )
    status_group.add_argument(
        "--translate-success",
        action="store_true",
        help="Only models that translated successfully",
    )
    status_group.add_argument(
        "--translate-failure",
        action="store_true",
        help="Only models that failed translation",
    )
    status_group.add_argument(
        "--solve-success",
        action="store_true",
        help="Only models that solved successfully",
    )
    status_group.add_argument(
        "--solve-failure",
        action="store_true",
        help="Only models that failed solving",
    )

    # Stage control
    stage_group = parser.add_argument_group("Stage Control")
    stage_group.add_argument(
        "--only-parse",
        action="store_true",
        help="Run only parse stage",
    )
    stage_group.add_argument(
        "--only-translate",
        action="store_true",
        help="Run only translate stage (requires parse success)",
    )
    stage_group.add_argument(
        "--only-solve",
        action="store_true",
        help="Run only solve stage (requires translate success)",
    )

    # Convenience
    convenience_group = parser.add_argument_group("Convenience")
    convenience_group.add_argument(
        "--only-failing",
        action="store_true",
        help="Re-run models where any stage failed",
    )
    convenience_group.add_argument(
        "--skip-completed",
        action="store_true",
        help="Skip models where all stages succeeded",
    )
    convenience_group.add_argument(
        "--quick",
        action="store_true",
        help="Shorthand for --limit=10",
    )

    # Output
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without execution",
    )
    output_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed output for each model",
    )
    output_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress progress output, show only summary",
    )
    output_group.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (machine-readable)",
    )

    args = parser.parse_args()

    # JSON mode implies quiet (no progress logging)
    if args.json:
        args.quiet = True

    # Run pipeline
    try:
        stats = run_full_test(args)
        if "error" in stats:
            if args.json:
                print(json.dumps({"error": stats["error"]}))
            else:
                logger.error(stats["error"])
            return 1
        if not stats.get("dry_run"):
            if args.json:
                print_json_summary(stats, args)
            else:
                print_summary(stats, args)
        return 0
    except ValueError as e:
        logger.error(str(e))
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
