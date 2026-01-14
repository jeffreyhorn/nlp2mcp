#!/usr/bin/env python3
"""MCP solve testing script for GAMSLIB models.

Runs PATH solver on generated MCP files and records solve results.

Usage:
    python scripts/gamslib/test_solve.py [OPTIONS]

Options:
    --dry-run      Show what would be done without making changes
    --limit N      Process only first N models (for testing)
    --model ID     Process a single model by ID
    --verbose      Show detailed output for each model
    --save-every N Save database every N models (default: 5)

Filter Options:
    --translate-success  Only process models with successful translation
    --model-type TYPE    Only process models of specific type (LP, NLP, QCP, etc.)

Examples:
    python scripts/gamslib/test_solve.py --translate-success
    python scripts/gamslib/test_solve.py --model chem --verbose
    python scripts/gamslib/test_solve.py --translate-success --limit 5 --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.error_taxonomy import (
    MODEL_INFEASIBLE,
    MODEL_LOCALLY_OPTIMAL,
    MODEL_OPTIMAL,
    MODEL_UNBOUNDED,
    PATH_SOLVE_EVAL_ERROR,
    PATH_SOLVE_ITERATION_LIMIT,
    PATH_SOLVE_LICENSE,
    PATH_SOLVE_TERMINATED,
    PATH_SOLVE_TIME_LIMIT,
    PATH_SYNTAX_ERROR,
)

# Database paths
DATABASE_PATH = PROJECT_ROOT / "data" / "gamslib" / "gamslib_status.json"
MCP_DIR = PROJECT_ROOT / "data" / "gamslib" / "mcp"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# GAMS model status descriptions
MODEL_STATUS_DESCRIPTIONS = {
    1: "Optimal",
    2: "Locally Optimal",
    3: "Unbounded",
    4: "Infeasible",
    5: "Locally Infeasible",
    6: "Intermediate Infeasible",
    7: "Intermediate Non-Optimal",
    8: "Integer Solution",
    9: "Intermediate Non-Integer",
    10: "Integer Infeasible",
    11: "Licensing Problem",
    12: "Error Unknown",
    13: "Error No Solution",
    14: "No Solution Returned",
    15: "Solved Unique",
    16: "Solved",
    17: "Solved Singular",
    18: "Unbounded - No Solution",
    19: "Infeasible - No Solution",
}

# GAMS solver status descriptions
SOLVER_STATUS_DESCRIPTIONS = {
    1: "Normal Completion",
    2: "Iteration Interrupt",
    3: "Resource Interrupt",
    4: "Terminated by Solver",
    5: "Evaluation Error Limit",
    6: "Capability Problem",
    7: "Licensing Problem",
    8: "User Interrupt",
    9: "Error Setup Failure",
    10: "Error Solver Failure",
    11: "Error Internal Solver Error",
    12: "Solve Processing Skipped",
    13: "Error System Failure",
}


def load_database(db_path: Path = DATABASE_PATH) -> dict[str, Any]:
    """Load the GAMSLIB status database."""
    logger.info(f"Loading database from {db_path}")
    with open(db_path) as f:
        return json.load(f)


def save_database(db: dict[str, Any], db_path: Path = DATABASE_PATH) -> None:
    """Save the GAMSLIB status database with atomic write."""
    temp_path = db_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(db, f, indent=2)
    temp_path.replace(db_path)


def get_translated_models(db: dict[str, Any]) -> list[dict[str, Any]]:
    """Get models that have been successfully translated to MCP."""
    translated = []
    for model in db.get("models", []):
        translate_result = model.get("nlp2mcp_translate", {})
        if translate_result.get("status") == "success":
            translated.append(model)
    return translated


def parse_gams_listing(lst_content: str) -> dict[str, Any]:
    """Parse GAMS .lst file for solve status.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        dict with keys: solver_status, solver_status_text,
                       model_status, model_status_text, objective_value,
                       iterations, resource_usage, has_solve_summary, error_type
    """
    result: dict[str, Any] = {
        "solver_status": None,
        "solver_status_text": None,
        "model_status": None,
        "model_status_text": None,
        "objective_value": None,
        "iterations": None,
        "resource_usage": None,
        "has_solve_summary": False,
        "error_type": None,
    }

    # Check for compilation errors (indicated by **** NNN or ERROR(S) count)
    if (
        re.search(r"\*\*\*\* \d+ ERROR", lst_content)  # **** 74 ERROR(S)
        or re.search(r"\*\*\*\*\s+\d+\s+\S+.*(domain|symbol|error)", lst_content, re.IGNORECASE)
        or re.search(r"\*\*\*\* \$\d+", lst_content)  # **** $NNN (older format)
    ):
        result["error_type"] = "compilation_error"
        return result

    # Check for license limits
    if "exceeds the demo license limits" in lst_content:
        result["error_type"] = "license_limit"
        return result

    # Check for missing include files or data
    if "could not be opened" in lst_content.lower():
        result["error_type"] = "missing_file"
        return result

    # Check for execution errors
    if re.search(r"^\*\*\* (Execution error|Error)", lst_content, re.MULTILINE):
        result["error_type"] = "execution_error"
        return result

    # Validate that the listing file contains expected SOLVE SUMMARY content
    if "S O L V E      S U M M A R Y" not in lst_content:
        result["error_type"] = "no_solve_summary"
        return result

    result["has_solve_summary"] = True

    # Patterns for status extraction
    solver_pattern = re.compile(r"\*\*\*\* SOLVER STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
    model_pattern = re.compile(r"\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
    objective_pattern = re.compile(
        r"\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
        re.MULTILINE,
    )
    resource_pattern = re.compile(
        r"RESOURCE USAGE, LIMIT\s+([\d.]+)\s+([\d.]+)",
        re.MULTILINE,
    )
    iteration_pattern = re.compile(
        r"ITERATION COUNT, LIMIT\s+(\d+)\s+(\d+)",
        re.MULTILINE,
    )

    # Find last occurrence of each (handles multiple solves)
    solver_matches = list(solver_pattern.finditer(lst_content))
    if solver_matches:
        match = solver_matches[-1]
        result["solver_status"] = int(match.group(1))
        result["solver_status_text"] = match.group(2).strip()

    model_matches = list(model_pattern.finditer(lst_content))
    if model_matches:
        match = model_matches[-1]
        result["model_status"] = int(match.group(1))
        result["model_status_text"] = match.group(2).strip()

    objective_matches = list(objective_pattern.finditer(lst_content))
    if objective_matches:
        match = objective_matches[-1]
        result["objective_value"] = float(match.group(1))

    resource_matches = list(resource_pattern.finditer(lst_content))
    if resource_matches:
        match = resource_matches[-1]
        result["resource_usage"] = float(match.group(1))

    iteration_matches = list(iteration_pattern.finditer(lst_content))
    if iteration_matches:
        match = iteration_matches[-1]
        result["iterations"] = int(match.group(1))

    return result


def extract_objective_from_variables(lst_content: str) -> float | None:
    """Extract objective value from variable section of .lst file.

    MCP models may not have an explicit OBJECTIVE VALUE line.
    This attempts to extract it from a variable named 'obj' or similar.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        Objective value if found, None otherwise
    """
    # Look for ---- VAR obj or similar patterns
    # Format: ---- VAR varname    LOWER     LEVEL     UPPER    MARGINAL
    obj_patterns = [
        r"---- VAR obj\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)",
        r"---- VAR z\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)",
    ]

    for pattern in obj_patterns:
        match = re.search(pattern, lst_content, re.IGNORECASE)
        if match:
            level_str = match.group(2)
            try:
                if level_str in (".", "EPS"):
                    return 0.0
                elif level_str in ("-INF", "+INF", "INF"):
                    return float("inf") if "+" in level_str or level_str == "INF" else float("-inf")
                else:
                    return float(level_str)
            except ValueError:
                continue

    return None


def categorize_solve_outcome(
    solver_status: int | None,
    model_status: int | None,
    error_type: str | None,
) -> str:
    """Categorize MCP solve outcome.

    Args:
        solver_status: GAMS solver status code
        model_status: GAMS model status code
        error_type: Error type from .lst parsing

    Returns:
        Solve outcome category string
    """
    # Handle error types from parsing
    if error_type == "compilation_error":
        return PATH_SYNTAX_ERROR
    if error_type == "license_limit":
        return PATH_SOLVE_LICENSE
    if error_type in ("missing_file", "execution_error", "no_solve_summary"):
        return PATH_SOLVE_TERMINATED

    # Check solver status
    if solver_status is None:
        return PATH_SOLVE_TERMINATED
    if solver_status == 2:
        return PATH_SOLVE_ITERATION_LIMIT
    if solver_status == 3:
        return PATH_SOLVE_TIME_LIMIT
    if solver_status == 4:
        return PATH_SOLVE_TERMINATED
    if solver_status == 5:
        return PATH_SOLVE_EVAL_ERROR
    if solver_status == 7:
        return PATH_SOLVE_LICENSE
    if solver_status != 1:
        return PATH_SOLVE_TERMINATED

    # Solver completed normally, check model status
    if model_status is None:
        return PATH_SOLVE_TERMINATED
    if model_status == 1:
        return MODEL_OPTIMAL
    if model_status == 2:
        return MODEL_LOCALLY_OPTIMAL
    if model_status == 3:
        return MODEL_UNBOUNDED
    if model_status in (4, 5, 6, 19):
        return MODEL_INFEASIBLE

    return PATH_SOLVE_TERMINATED


def solve_mcp(mcp_path: Path, timeout: int = 60) -> dict[str, Any]:
    """Solve an MCP model using PATH solver.

    Args:
        mcp_path: Path to the MCP .gms file
        timeout: Maximum solve time in seconds (default: 60)

    Returns:
        Dictionary with solve results:
        - status: "success" or "failure"
        - solver_status: GAMS solver status code
        - solver_status_text: Description of solver status
        - model_status: GAMS model status code
        - model_status_text: Description of model status
        - objective_value: Objective function value (if available)
        - solve_time_seconds: Time taken to solve
        - iterations: Number of PATH iterations
        - outcome_category: Error taxonomy category
        - error: Error message (if failed)
    """
    start_time = time.perf_counter()

    # Find GAMS executable
    gams_exe = shutil.which("gams")
    if not gams_exe:
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
            "status": "failure",
            "solver_status": None,
            "solver_status_text": None,
            "model_status": None,
            "model_status_text": None,
            "objective_value": None,
            "solve_time_seconds": round(time.perf_counter() - start_time, 4),
            "iterations": None,
            "outcome_category": PATH_SOLVE_TERMINATED,
            "error": "GAMS executable not found",
        }

    mcp_path = Path(mcp_path).absolute()

    with tempfile.TemporaryDirectory() as tmpdir:
        lst_path = Path(tmpdir) / "output.lst"

        try:
            # Run GAMS with PATH solver
            cmd = [
                gams_exe,
                str(mcp_path),
                f"o={lst_path}",
                "lo=3",  # Detailed log output
                f"reslim={timeout}",  # Time limit
            ]

            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10,  # Allow extra time for GAMS overhead
                cwd=tmpdir,
            )

            elapsed = time.perf_counter() - start_time

        except subprocess.TimeoutExpired:
            return {
                "status": "failure",
                "solver_status": 3,  # Resource Interrupt
                "solver_status_text": "Resource Interrupt",
                "model_status": None,
                "model_status_text": None,
                "objective_value": None,
                "solve_time_seconds": round(time.perf_counter() - start_time, 4),
                "iterations": None,
                "outcome_category": PATH_SOLVE_TIME_LIMIT,
                "error": f"Timeout after {timeout} seconds",
            }

        # Parse .lst file
        if not lst_path.exists():
            return {
                "status": "failure",
                "solver_status": None,
                "solver_status_text": None,
                "model_status": None,
                "model_status_text": None,
                "objective_value": None,
                "solve_time_seconds": round(elapsed, 4),
                "iterations": None,
                "outcome_category": PATH_SOLVE_TERMINATED,
                "error": "No .lst file generated",
            }

        lst_content = lst_path.read_text()
        parsed = parse_gams_listing(lst_content)

        # Get objective value (try explicit line first, then variable extraction)
        objective = parsed.get("objective_value")
        if objective is None:
            objective = extract_objective_from_variables(lst_content)

        # Categorize outcome
        outcome = categorize_solve_outcome(
            parsed.get("solver_status"),
            parsed.get("model_status"),
            parsed.get("error_type"),
        )

        # Build result
        solver_status = parsed.get("solver_status")
        model_status = parsed.get("model_status")

        # Determine success
        is_success = (
            solver_status == 1 and model_status in (1, 2) and parsed.get("error_type") is None
        )

        result: dict[str, Any] = {
            "status": "success" if is_success else "failure",
            "solver_status": solver_status,
            "solver_status_text": (
                SOLVER_STATUS_DESCRIPTIONS.get(solver_status, "Unknown") if solver_status else None
            ),
            "model_status": model_status,
            "model_status_text": (
                MODEL_STATUS_DESCRIPTIONS.get(model_status, "Unknown") if model_status else None
            ),
            "objective_value": objective,
            "solve_time_seconds": round(elapsed, 4),
            "iterations": parsed.get("iterations"),
            "outcome_category": outcome,
        }

        if not is_success:
            if parsed.get("error_type"):
                result["error"] = f"Parse error: {parsed['error_type']}"
            elif solver_status != 1:
                result["error"] = (
                    f"Solver: {SOLVER_STATUS_DESCRIPTIONS.get(solver_status, 'Unknown')}"
                )
            elif model_status not in (1, 2):
                result["error"] = f"Model: {MODEL_STATUS_DESCRIPTIONS.get(model_status, 'Unknown')}"
            else:
                result["error"] = "Unknown error"

        return result


def update_model_solve_result(
    model: dict[str, Any],
    solve_result: dict[str, Any],
) -> None:
    """Update model entry with solve result.

    Args:
        model: Model dictionary to update
        solve_result: Solve result from solve_mcp()
    """
    model["mcp_solve"] = {
        "status": solve_result["status"],
        "solve_date": datetime.now(UTC).isoformat(),
        "solver": "PATH",
        # NOTE: PATH solver version is hardcoded based on current GAMS 51.3.0 installation.
        # Update this value if the underlying GAMS/PATH installation uses a different version.
        "solver_version": "5.2.01",
        "solver_status": solve_result["solver_status"],
        "solver_status_text": solve_result["solver_status_text"],
        "model_status": solve_result["model_status"],
        "model_status_text": solve_result["model_status_text"],
        "objective_value": solve_result["objective_value"],
        "solve_time_seconds": solve_result["solve_time_seconds"],
        "iterations": solve_result["iterations"],
        "outcome_category": solve_result["outcome_category"],
    }

    if "error" in solve_result:
        model["mcp_solve"]["error"] = {
            "category": solve_result["outcome_category"],
            "message": solve_result["error"],
        }


def apply_filters(
    models: list[dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    """Apply filter arguments to model list.

    Args:
        models: List of model dictionaries
        args: Parsed command-line arguments

    Returns:
        Filtered list of models
    """
    filtered = models

    # Filter by specific model
    if args.model:
        filtered = [m for m in filtered if m.get("model_id") == args.model]

    # Filter by model type
    if args.model_type:
        filtered = [m for m in filtered if m.get("type", "").upper() == args.model_type.upper()]

    # Filter by translation success
    if args.translate_success:
        filtered = [
            m for m in filtered if m.get("nlp2mcp_translate", {}).get("status") == "success"
        ]

    # Apply limit last
    if args.limit:
        filtered = filtered[: args.limit]

    return filtered


def report_filter_summary(
    total: int,
    filtered: int,
    args: argparse.Namespace,
) -> None:
    """Log summary of applied filters.

    Args:
        total: Total number of models before filtering
        filtered: Number of models after filtering
        args: Parsed command-line arguments
    """
    filters = []
    if args.model:
        filters.append(f"model={args.model}")
    if args.model_type:
        filters.append(f"type={args.model_type}")
    if args.translate_success:
        filters.append("translate-success")
    if args.limit:
        filters.append(f"limit={args.limit}")

    if filters:
        logger.info(f"Filters applied: {', '.join(filters)}")
    logger.info(f"Models after filtering: {filtered} (from {total} candidates)")


def print_summary(stats: dict[str, Any]) -> None:
    """Print solve summary.

    Args:
        stats: Statistics dictionary with solve results
    """
    print("\n" + "=" * 60)
    print("MCP SOLVE SUMMARY")
    print("=" * 60)

    total = stats["total"]
    success = stats["success"]
    failure = stats["failure"]
    skipped = stats["skipped"]

    print(f"\nModels processed: {total - skipped}/{total}")
    if total - skipped > 0:
        pct = success / (total - skipped) * 100
        print(f"  Success: {success} ({pct:.1f}%)")
        print(f"  Failure: {failure}")
    print(f"  Skipped: {skipped}")

    print(f"\nTotal time: {stats['total_time']:.1f}s")
    if success + failure > 0:
        avg = stats["total_time"] / (success + failure)
        print(f"Average time per model: {avg:.2f}s")

    # Print outcome categories
    if stats.get("outcome_categories"):
        print("\nOutcome categories:")
        for cat, count in sorted(
            stats["outcome_categories"].items(),
            key=lambda x: -x[1],
        ):
            print(f"  {cat}: {count}")

    # Print successful models
    if stats.get("successful_models"):
        print(f"\nSuccessful solves ({len(stats['successful_models'])}):")
        for model_id in sorted(stats["successful_models"]):
            print(f"  - {model_id}")

    print("=" * 60)


def run_batch_solve(args: argparse.Namespace) -> int:
    """Run batch MCP solve.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Load database
    db = load_database()
    all_models = db.get("models", [])

    # Get translated models (baseline for filtering)
    translated_models = get_translated_models(db)
    logger.info(f"Found {len(translated_models)} successfully translated models")

    # Apply filters
    models_to_process = apply_filters(translated_models, args)
    report_filter_summary(len(translated_models), len(models_to_process), args)

    if not models_to_process:
        logger.warning("No models to process after filtering")
        return 0

    # Initialize stats
    stats: dict[str, Any] = {
        "total": len(models_to_process),
        "success": 0,
        "failure": 0,
        "skipped": 0,
        "total_time": 0.0,
        "outcome_categories": {},
        "successful_models": [],
    }

    start_time = time.perf_counter()
    save_counter = 0

    for i, model in enumerate(models_to_process, 1):
        model_id = model.get("model_id", "unknown")
        mcp_file = MCP_DIR / f"{model_id}_mcp.gms"

        # Progress logging
        pct = (i / len(models_to_process)) * 100
        remaining = (
            (time.perf_counter() - start_time) / i * (len(models_to_process) - i) if i > 1 else 0
        )
        logger.info(
            f"[{i:3}/{len(models_to_process)}] {pct:4.0f}% Solving {model_id}... "
            f"({stats['success']} success, {stats['failure']} failure, ~{remaining:.0f}s remaining)"
        )

        # Check MCP file exists
        if not mcp_file.exists():
            logger.warning(f"  MCP file not found: {mcp_file}")
            stats["skipped"] += 1
            continue

        if args.dry_run:
            logger.info(f"  [DRY RUN] Would solve: {mcp_file}")
            stats["skipped"] += 1
            continue

        # Solve MCP
        result = solve_mcp(mcp_file, timeout=60)

        if args.verbose:
            logger.info(f"  Status: {result['status']}")
            logger.info(f"  Solver: {result['solver_status']} ({result['solver_status_text']})")
            logger.info(f"  Model: {result['model_status']} ({result['model_status_text']})")
            if result.get("objective_value") is not None:
                logger.info(f"  Objective: {result['objective_value']}")
            logger.info(f"  Time: {result['solve_time_seconds']:.4f}s")
            if result.get("error"):
                logger.info(f"  Error: {result['error']}")

        # Update model in database
        # Find the model in all_models (not just translated)
        for m in all_models:
            if m.get("model_id") == model_id:
                update_model_solve_result(m, result)
                break

        # Update stats
        if result["status"] == "success":
            stats["success"] += 1
            stats["successful_models"].append(model_id)
        else:
            stats["failure"] += 1

        outcome = result.get("outcome_category", "unknown")
        stats["outcome_categories"][outcome] = stats["outcome_categories"].get(outcome, 0) + 1

        # Periodic save
        save_counter += 1
        if save_counter >= args.save_every:
            save_database(db)
            logger.info("Database saved")
            save_counter = 0

    # Final save
    if not args.dry_run:
        save_database(db)
        logger.info("Final database save complete")

    stats["total_time"] = time.perf_counter() - start_time
    print_summary(stats)

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run MCP solve testing on GAMSLIB models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Standard arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only first N models (for testing)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Process a single model by ID",
    )
    parser.add_argument(
        "--verbose",
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
        "--translate-success",
        action="store_true",
        help="Only process models with successful translation",
    )
    filter_group.add_argument(
        "--model-type",
        type=str,
        default=None,
        help="Only process models of specific type (LP, NLP, QCP, etc.)",
    )

    args = parser.parse_args()

    return run_batch_solve(args)


if __name__ == "__main__":
    sys.exit(main())
