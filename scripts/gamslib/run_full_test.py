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

Examples:
    python scripts/gamslib/run_full_test.py --model trnsport --verbose
    python scripts/gamslib/run_full_test.py --quick
    python scripts/gamslib/run_full_test.py --only-parse --limit 5
    python scripts/gamslib/run_full_test.py --only-failing
    python scripts/gamslib/run_full_test.py --type LP --only-translate
"""

from __future__ import annotations

import argparse
import logging
import random
import sys
import time
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
        if args.verbose:
            error_cat = result.get("error", {}).get("category", "unknown")
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

    if result["status"] == "success":
        translate_entry["output_file"] = result.get("output_file")
        stats["translate_success"] += 1
        if args.verbose:
            logger.info(f"    [TRANSLATE] SUCCESS: {result.get('output_file')}")
    else:
        translate_entry["error"] = result.get("error")
        stats["translate_failure"] += 1
        if args.verbose:
            error_cat = result.get("error", {}).get("category", "unknown")
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
        if args.verbose:
            logger.info(f"    [SOLVE] FAILURE: {result.get('outcome_category')}")

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
        logger.info("\n[DRY RUN] Would process the following models:")
        stages = _determine_stages(args)
        for model in filtered:
            model_id = model.get("model_id", "unknown")
            logger.info(f"  - {model_id}: {' → '.join(stages)}")
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
        # Translate stats
        "translate_success": 0,
        "translate_failure": 0,
        "translate_cascade_skip": 0,
        # Solve stats
        "solve_success": 0,
        "solve_failure": 0,
        "solve_cascade_skip": 0,
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


def print_summary(stats: dict[str, Any], args: argparse.Namespace) -> None:
    """Print summary of pipeline results.

    Args:
        stats: Statistics dictionary from run_full_test
        args: Command line arguments
    """
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    total = stats["total"]
    processed = stats["processed"]
    skipped = stats["skipped"]

    print(f"\nModels processed: {processed}/{total}")
    if skipped > 0:
        print(f"Models skipped: {skipped}")

    # Parse results (if parse was run)
    if not args.only_translate and not args.only_solve:
        parse_total = stats["parse_success"] + stats["parse_failure"]
        if parse_total > 0:
            parse_pct = stats["parse_success"] / parse_total * 100
            print(f"\nParse Results:")
            print(f"  Success: {stats['parse_success']} ({parse_pct:.1f}%)")
            print(f"  Failure: {stats['parse_failure']}")

    # Translate results (if translate was run)
    if not args.only_parse and not args.only_solve:
        translate_total = stats["translate_success"] + stats["translate_failure"]
        if translate_total > 0:
            translate_pct = stats["translate_success"] / translate_total * 100
            print(f"\nTranslate Results:")
            print(f"  Success: {stats['translate_success']} ({translate_pct:.1f}%)")
            print(f"  Failure: {stats['translate_failure']}")
        if stats["translate_cascade_skip"] > 0:
            print(f"  Cascade skipped: {stats['translate_cascade_skip']}")

    # Solve results (if solve was run)
    if not args.only_parse and not args.only_translate:
        solve_total = stats["solve_success"] + stats["solve_failure"]
        if solve_total > 0:
            solve_pct = stats["solve_success"] / solve_total * 100
            print(f"\nSolve Results:")
            print(f"  Success: {stats['solve_success']} ({solve_pct:.1f}%)")
            print(f"  Failure: {stats['solve_failure']}")
        if stats["solve_cascade_skip"] > 0:
            print(f"  Cascade skipped: {stats['solve_cascade_skip']}")

        # Compare results
        compare_total = stats["compare_match"] + stats["compare_mismatch"]
        if compare_total > 0:
            compare_pct = stats["compare_match"] / compare_total * 100
            print(f"\nComparison Results:")
            print(f"  Match: {stats['compare_match']} ({compare_pct:.1f}%)")
            print(f"  Mismatch: {stats['compare_mismatch']}")
        if stats["compare_skipped"] > 0:
            print(f"  Skipped: {stats['compare_skipped']}")
        if stats["compare_cascade_skip"] > 0:
            print(f"  Cascade skipped: {stats['compare_cascade_skip']}")

    # Overall pipeline success
    if not args.only_parse and not args.only_translate and not args.only_solve:
        full_success = stats["compare_match"]
        if processed > 0:
            full_pct = full_success / processed * 100
            print(f"\nFull pipeline success: {full_success}/{processed} ({full_pct:.1f}%)")

    # Timing
    print(f"\nTotal time: {stats['total_time']:.1f}s")
    if processed > 0:
        avg_time = stats["total_time"] / processed
        print(f"Average time per model: {avg_time:.2f}s")

    print("=" * 60)


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

    args = parser.parse_args()

    # Run pipeline
    try:
        stats = run_full_test(args)
        if "error" in stats:
            logger.error(stats["error"])
            return 1
        if not stats.get("dry_run"):
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
