#!/usr/bin/env python3
"""Convexity verification script for GAMSLIB models.

This script verifies model convexity by running GAMS and analyzing solver output.
LP models are verified_convex (LP solver proves global optimality).
NLP/QCP models are likely_convex (local solver finds optimum but cannot prove global).
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
CATALOG_PATH = PROJECT_ROOT / "data" / "gamslib" / "catalog.json"
RAW_DIR = PROJECT_ROOT / "data" / "gamslib" / "raw"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ConvexityStatus(Enum):
    """Convexity verification status."""

    VERIFIED_CONVEX = "verified_convex"  # Proven convex (LP or global solver)
    LIKELY_CONVEX = "likely_convex"  # NLP solved, probably convex
    UNKNOWN = "unknown"  # Cannot determine
    NON_CONVEX = "non_convex"  # Known non-convex
    EXCLUDED = "excluded"  # Not in corpus (infeasible, unbounded, wrong type)
    ERROR = "error"  # Solve failed


# GAMS model status descriptions for better error messages
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


@dataclass
class VerificationResult:
    """Result of convexity verification for a single model."""

    model_id: str
    model_path: str
    convexity_status: str  # ConvexityStatus value
    solver_status: Optional[int]
    model_status: Optional[int]
    objective_value: Optional[float]
    solve_time_seconds: float
    timed_out: bool
    error_message: Optional[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


def parse_gams_listing(lst_content: str) -> dict:
    """Parse GAMS .lst file for solve status.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        dict with keys: solver_status, solver_status_text,
                       model_status, model_status_text, objective_value,
                       has_solve_summary, error_type
    """
    result = {
        "solver_status": None,
        "solver_status_text": None,
        "model_status": None,
        "model_status_text": None,
        "objective_value": None,
        "has_solve_summary": False,
        "error_type": None,
    }

    # Check for specific error conditions before looking for solve summary

    # Check for compilation errors (indicated by **** markers)
    if re.search(r"\*\*\*\* \$\d+", lst_content):
        result["error_type"] = "compilation_error"
        return result

    # Check for missing include files or data
    if "could not be opened" in lst_content.lower():
        result["error_type"] = "missing_file"
        return result

    # Check for execution errors (lines starting with exactly three asterisks)
    # Use regex to avoid matching **** MODEL STATUS lines containing "Error"
    if re.search(r"^\*\*\* (Execution error|Error)", lst_content, re.MULTILINE):
        result["error_type"] = "execution_error"
        return result

    # Validate that the listing file contains expected SOLVE SUMMARY content
    if "S O L V E      S U M M A R Y" not in lst_content:
        # Check if there's a SOLVE statement at all
        if not re.search(r"(?i)\bsolve\b", lst_content):
            result["error_type"] = "no_solve_statement"
        return result

    result["has_solve_summary"] = True

    # Patterns for status extraction
    solver_pattern = re.compile(r"\*\*\*\* SOLVER STATUS\s+(\d+)\s+(.*?)$", re.MULTILINE)
    model_pattern = re.compile(r"\*\*\*\* MODEL STATUS\s+(\d+)\s*(.*?)$", re.MULTILINE)
    objective_pattern = re.compile(
        r"\*\*\*\* OBJECTIVE VALUE\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
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

    return result


def classify_result(
    model_id: str,
    model_path: str,
    model_type: str,
    solver_status: Optional[int],
    model_status: Optional[int],
    objective_value: Optional[float],
    solve_time: float,
) -> VerificationResult:
    """Classify verification result based on status codes.

    Args:
        model_id: Model identifier
        model_path: Path to model file
        model_type: LP, NLP, or QCP
        solver_status: GAMS solver status code
        model_status: GAMS model status code
        objective_value: Objective function value
        solve_time: Time taken to solve

    Returns:
        VerificationResult with classification
    """
    # Check for solver failure
    if solver_status is None or solver_status != 1:
        solver_desc = SOLVER_STATUS_DESCRIPTIONS.get(solver_status, "Unknown")
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.ERROR.value,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message=f"Solver did not complete normally: {solver_desc} (status={solver_status})",
        )

    # Check for no model status
    if model_status is None:
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.ERROR.value,
            model_status=None,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message="No model status found in output",
        )

    # Exclude unbounded/infeasible
    if model_status in (3, 4, 5, 6, 18, 19):
        status_names = {
            3: "Unbounded",
            4: "Infeasible",
            5: "Locally Infeasible",
            6: "Intermediate Infeasible",
            18: "Unbounded - No Solution",
            19: "Infeasible - No Solution",
        }
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.EXCLUDED.value,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message=f"Model is {status_names.get(model_status, 'excluded')}",
        )

    # Error status codes
    if model_status in (11, 12, 13, 14, 17):
        model_desc = MODEL_STATUS_DESCRIPTIONS.get(model_status, "Unknown")
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.ERROR.value,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message=f"Solver error: {model_desc} (model status={model_status})",
        )

    # LP with optimal status
    if model_type == "LP" and model_status == 1:
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.VERIFIED_CONVEX.value,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message=None,
        )

    # NLP/QCP with status 1 or 2 (local solver)
    if model_type in ("NLP", "QCP") and model_status in (1, 2):
        return VerificationResult(
            model_id=model_id,
            model_path=model_path,
            convexity_status=ConvexityStatus.LIKELY_CONVEX.value,
            model_status=model_status,
            solver_status=solver_status,
            objective_value=objective_value,
            solve_time_seconds=solve_time,
            timed_out=False,
            error_message=None,
        )

    # Default to unknown
    return VerificationResult(
        model_id=model_id,
        model_path=model_path,
        convexity_status=ConvexityStatus.UNKNOWN.value,
        model_status=model_status,
        solver_status=solver_status,
        objective_value=objective_value,
        solve_time_seconds=solve_time,
        timed_out=False,
        error_message="Unexpected status combination",
    )


def verify_model(
    model_id: str,
    model_path: Path,
    model_type: str,
    timeout_seconds: int = 60,
) -> VerificationResult:
    """Verify convexity of a single GAMS model.

    Args:
        model_id: Model identifier
        model_path: Path to .gms file
        model_type: LP, NLP, or QCP
        timeout_seconds: Maximum solve time

    Returns:
        VerificationResult with status and details
    """
    # Skip non-candidate types
    if model_type not in ("LP", "NLP", "QCP"):
        return VerificationResult(
            model_id=model_id,
            model_path=str(model_path),
            convexity_status=ConvexityStatus.EXCLUDED.value,
            model_status=None,
            solver_status=None,
            objective_value=None,
            solve_time_seconds=0.0,
            timed_out=False,
            error_message=f"Model type {model_type} excluded from corpus",
        )

    # Ensure model_path is absolute for GAMS execution
    model_path_abs = Path(model_path).absolute()

    # Create temp directory for output
    with tempfile.TemporaryDirectory() as tmpdir:
        lst_path = os.path.join(tmpdir, "output.lst")

        # Select solver based on model type
        if model_type == "LP":
            solver_option = "LP=CPLEX"
        else:
            solver_option = "NLP=CONOPT"

        # Run GAMS
        start_time = time.time()
        try:
            result = subprocess.run(
                ["gams", str(model_path_abs), f"o={lst_path}", "lo=3", solver_option],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=tmpdir,
            )
            solve_time = time.time() - start_time
        except FileNotFoundError:
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=0.0,
                timed_out=False,
                error_message="GAMS executable not found in PATH",
            )
        except subprocess.TimeoutExpired:
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=timeout_seconds,
                timed_out=True,
                error_message=f"Timeout after {timeout_seconds} seconds",
            )

        # Check for compilation errors
        if result.returncode == 2:
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                timed_out=False,
                error_message="GAMS compilation error",
            )

        # Parse .lst file
        if not os.path.exists(lst_path):
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                timed_out=False,
                error_message="No listing file generated",
            )

        with open(lst_path) as f:
            lst_content = f.read()

        # Check for license errors
        if "The model exceeds the demo license limits" in lst_content:
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                timed_out=False,
                error_message="Model exceeds demo license limits",
            )

        parsed = parse_gams_listing(lst_content)

        # Handle specific error types detected during parsing
        if parsed.get("error_type"):
            error_messages = {
                "compilation_error": "GAMS compilation error in model file",
                "missing_file": "Model references missing include file or data",
                "execution_error": "GAMS execution error during model run",
                "no_solve_statement": "Model has no SOLVE statement",
            }
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                timed_out=False,
                error_message=error_messages.get(
                    parsed["error_type"], f"Unknown error type: {parsed['error_type']}"
                ),
            )

        if not parsed["has_solve_summary"]:
            return VerificationResult(
                model_id=model_id,
                model_path=str(model_path),
                convexity_status=ConvexityStatus.ERROR.value,
                model_status=None,
                solver_status=None,
                objective_value=None,
                solve_time_seconds=solve_time,
                timed_out=False,
                error_message="No solve summary found in listing file",
            )

        # Classify based on status codes
        return classify_result(
            model_id=model_id,
            model_path=str(model_path),
            model_type=model_type,
            solver_status=parsed["solver_status"],
            model_status=parsed["model_status"],
            objective_value=parsed["objective_value"],
            solve_time=solve_time,
        )


def load_catalog() -> dict:
    """Load the GAMSLIB catalog."""
    try:
        with open(CATALOG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Catalog file not found: {CATALOG_PATH}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in catalog: {e}")
        sys.exit(1)


def save_catalog(catalog: dict) -> None:
    """Save the GAMSLIB catalog."""
    try:
        with open(CATALOG_PATH, "w") as f:
            json.dump(catalog, f, indent=2)
            f.write("\n")
        logger.info(f"Catalog saved to: {CATALOG_PATH}")
    except OSError as e:
        logger.error(f"Failed to save catalog: {e}")
        sys.exit(1)


def update_catalog_entry(
    model: dict,
    result: VerificationResult,
) -> None:
    """Update a catalog entry with verification results.

    Args:
        model: The catalog model entry to update
        result: The verification result
    """
    # Always record convexity status and verification timestamp (UTC with Z suffix)
    model["convexity_status"] = result.convexity_status
    model["verification_date"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Only persist solver-related details when available to avoid polluting
    # the catalog with null values for non-applicable models.
    if result.solver_status is not None:
        model["solver_status"] = result.solver_status
    elif "solver_status" in model:
        del model["solver_status"]

    if result.model_status is not None:
        model["model_status"] = result.model_status
    elif "model_status" in model:
        del model["model_status"]

    if result.objective_value is not None:
        model["objective_value"] = result.objective_value
    elif "objective_value" in model:
        del model["objective_value"]

    if result.solve_time_seconds > 0:
        model["solve_time_seconds"] = round(result.solve_time_seconds, 3)
    elif "solve_time_seconds" in model:
        del model["solve_time_seconds"]

    # Record or clear any verification error message
    if result.error_message:
        model["verification_error"] = result.error_message
    elif "verification_error" in model:
        del model["verification_error"]


def get_model_type(model: dict) -> str:
    """Extract model type from catalog entry."""
    return model.get("gamslib_type", "UNKNOWN")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify convexity of GAMSLIB models")
    parser.add_argument(
        "--model",
        "-m",
        action="append",
        help="Verify specific model(s) by ID (can be repeated)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Verify all downloaded models",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=60,
        help="Timeout in seconds per model (default: 60)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be verified without running",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file for results (JSON format)",
    )
    parser.add_argument(
        "--update-catalog",
        "-u",
        action="store_true",
        help="Update catalog with verification results",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate arguments
    if not args.model and not args.all:
        parser.error("Either --model or --all is required")

    if args.timeout <= 0:
        parser.error("Timeout must be a positive integer")

    # Load catalog
    catalog = load_catalog()
    models = catalog.get("models", [])

    # Build model lookup
    model_lookup = {m.get("model_id"): m for m in models}

    # Determine which models to verify
    models_to_verify = []

    if args.all:
        # Verify all downloaded models
        for model in models:
            if model.get("download_status") == "downloaded":
                models_to_verify.append(model)
    else:
        # Verify specific models
        for model_id in args.model:
            if model_id not in model_lookup:
                logger.warning(f"Model not found in catalog: {model_id}")
                continue
            model = model_lookup[model_id]
            if model.get("download_status") != "downloaded":
                logger.warning(f"Model not downloaded: {model_id}")
                continue
            models_to_verify.append(model)

    if not models_to_verify:
        logger.error("No models to verify")
        sys.exit(1)

    logger.info(f"Models to verify: {len(models_to_verify)}")

    if args.dry_run:
        logger.info("Dry run - would verify:")
        for model in models_to_verify:
            model_type = get_model_type(model)
            logger.info(f"  {model.get('model_id')} ({model_type})")
        return

    # Run verification
    results = []
    verified_count = 0
    likely_count = 0
    excluded_count = 0
    error_count = 0

    for i, model in enumerate(models_to_verify, 1):
        model_id = model.get("model_id")
        model_type = get_model_type(model)
        model_path = RAW_DIR / f"{model_id}.gms"

        if not model_path.exists():
            logger.warning(f"Model file not found: {model_path}")
            continue

        pct = (i / len(models_to_verify)) * 100
        logger.info(
            f"[{i}/{len(models_to_verify)} {pct:.0f}%] Verifying {model_id} ({model_type})..."
        )

        result = verify_model(
            model_id=model_id,
            model_path=model_path,
            model_type=model_type,
            timeout_seconds=args.timeout,
        )

        results.append(result)

        # Update catalog entry if requested
        if args.update_catalog:
            update_catalog_entry(model, result)

        # Track counts
        if result.convexity_status == ConvexityStatus.VERIFIED_CONVEX.value:
            verified_count += 1
            logger.info(f"  -> VERIFIED_CONVEX (objective={result.objective_value})")
        elif result.convexity_status == ConvexityStatus.LIKELY_CONVEX.value:
            likely_count += 1
            logger.info(f"  -> LIKELY_CONVEX (objective={result.objective_value})")
        elif result.convexity_status == ConvexityStatus.EXCLUDED.value:
            excluded_count += 1
            logger.info(f"  -> EXCLUDED: {result.error_message}")
        else:
            error_count += 1
            logger.warning(f"  -> ERROR: {result.error_message}")

    # Summary
    logger.info("")
    logger.info("Verification Summary:")
    logger.info(f"  Total verified: {len(results)}")
    logger.info(f"  Verified convex (LP): {verified_count}")
    logger.info(f"  Likely convex (NLP/QCP): {likely_count}")
    logger.info(f"  Excluded: {excluded_count}")
    logger.info(f"  Errors: {error_count}")

    # Error breakdown if there are errors
    if error_count > 0:
        error_categories: dict[str, int] = {}
        for r in results:
            if r.convexity_status in (ConvexityStatus.ERROR.value, ConvexityStatus.UNKNOWN.value):
                # Categorize errors by type
                msg = r.error_message or "Unknown error"
                if "license limits" in msg.lower():
                    category = "License limits"
                elif "compilation error" in msg.lower():
                    category = "Compilation errors"
                elif "no solve summary" in msg.lower():
                    category = "No solve summary"
                elif "no solve statement" in msg.lower():
                    category = "No solve statement"
                elif "missing" in msg.lower() and "file" in msg.lower():
                    category = "Missing files"
                elif "execution error" in msg.lower():
                    category = "Execution errors"
                elif "timeout" in msg.lower():
                    category = "Timeouts"
                elif "solver did not complete" in msg.lower():
                    category = "Solver failures"
                elif "unexpected status" in msg.lower():
                    category = "Unexpected status"
                else:
                    category = "Other errors"
                error_categories[category] = error_categories.get(category, 0) + 1

        logger.info("")
        logger.info("Error Breakdown:")
        for category, count in sorted(error_categories.items(), key=lambda x: -x[1]):
            logger.info(f"  {category}: {count}")

    # Save catalog if requested
    if args.update_catalog:
        save_catalog(catalog)

    # Output results
    if args.output:
        output_data = {
            "verification_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_models": len(results),
            "verified_convex": verified_count,
            "likely_convex": likely_count,
            "excluded": excluded_count,
            "errors": error_count,
            "results": [r.to_dict() for r in results],
        }
        try:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            logger.info(f"Results written to: {args.output}")
        except OSError as e:
            logger.error(f"Failed to write output: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
