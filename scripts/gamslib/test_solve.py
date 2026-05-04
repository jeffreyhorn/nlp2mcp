#!/usr/bin/env python3
"""MCP solve testing script for GAMSLIB models.

Runs PATH solver on generated MCP files and records solve results.
Optionally compares NLP and MCP objective values using tolerance-based matching.

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

Comparison Options:
    --compare      Compare NLP and MCP solutions after solving
    --rtol FLOAT   Relative tolerance for objective comparison (default: 2e-3)
    --atol FLOAT   Absolute tolerance for objective comparison (default: 1e-8)

Examples:
    python scripts/gamslib/test_solve.py --translate-success
    python scripts/gamslib/test_solve.py --model chem --verbose
    python scripts/gamslib/test_solve.py --translate-success --limit 5 --dry-run
    python scripts/gamslib/test_solve.py --translate-success --compare --verbose
    python scripts/gamslib/test_solve.py --compare --rtol 1e-5 --atol 1e-7
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

import math

from scripts.gamslib.error_taxonomy import (
    COMPARE_BOTH_INFEASIBLE,
    COMPARE_MCP_FAILED,
    COMPARE_MULTI_SOLVE_SKIP,
    COMPARE_NLP_FAILED,
    COMPARE_OBJECTIVE_MATCH,
    COMPARE_OBJECTIVE_MISMATCH,
    COMPARE_STATUS_MISMATCH,
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

# Additional comparison result category not in error_taxonomy (error state)
COMPARE_NOT_PERFORMED = "compare_not_performed"

# Default tolerance values (based on solver defaults research)
DEFAULT_RTOL = 2e-3  # Relative tolerance for NLP↔MCP objective comparison
DEFAULT_ATOL = 1e-8  # Absolute tolerance (matches IPOPT)

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
    Checks first for the fixed-name sentinel scalar 'nlp2mcp_obj_val' emitted by
    the nlp2mcp emitter after the Solve statement (preferred), then falls back
    to a heuristic scan of common objective variable names.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        Objective value if found, None otherwise
    """
    # Primary: look for the fixed-name sentinel emitted by nlp2mcp:
    #   Scalar nlp2mcp_obj_val; nlp2mcp_obj_val = <objvar>.l; Display nlp2mcp_obj_val;
    # GAMS Display of a Scalar produces:
    #   ----    NNN PARAMETER nlp2mcp_obj_val          =     <value>
    # Use the last match in case a .lst file contains multiple solve runs.
    sentinel_pattern = re.compile(
        r"----\s+\d*\s*PARAMETER\s+nlp2mcp_obj_val\s+=\s+([-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?)",
        re.IGNORECASE,
    )
    sentinel_matches = list(sentinel_pattern.finditer(lst_content))
    if sentinel_matches:
        try:
            return float(sentinel_matches[-1].group(1))
        except ValueError:
            pass

    # Fallback: heuristic scan of common objective variable names.
    # Format: ---- VAR varname    LOWER     LEVEL     UPPER    MARGINAL
    obj_var_names = [
        "obj",
        "z",
        "objective",
        "cost",
        "profit",
        "total_cost",
        "totalcost",
        "total",
        "f",
        "fobj",
    ]

    for var_name in obj_var_names:
        pattern = (
            rf"---- VAR {var_name}\s+"
            r"([\-+\.\dEeINF]+)\s+"  # LOWER
            r"([\-+\.\dEeINF]+)\s+"  # LEVEL
            r"([\-+\.\dEeINF]+)\s+"  # UPPER
            r"([\-+\.\dEeINF]+)"  # MARGINAL
        )
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


def extract_path_version(lst_content: str) -> str | None:
    """Extract PATH solver version from .lst file.

    Looks for version string in the format "PATH Version: X.X.XX"
    that appears in the solver output section of the .lst file.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        Version string (e.g., "5.2.01") if found, None otherwise
    """
    # Look for PATH version in solver output
    # Format: "PATH Version: 5.2.01 (Mon Oct 27 13:31:58 2025)"
    match = re.search(r"PATH\s+Version:\s*(\d+\.\d+(?:\.\d+)?)", lst_content)
    if match:
        return match.group(1)
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


def objectives_match(
    nlp_obj: float,
    mcp_obj: float,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> tuple[bool, str]:
    """Check if NLP and MCP objectives match within tolerance.

    Uses combined tolerance formula: |a - b| <= atol + rtol * max(|a|, |b|)

    This formula is the NumPy/SciPy standard and handles:
    - Values near zero (absolute tolerance dominates)
    - Large values (relative tolerance dominates)
    - Symmetric comparison (order doesn't matter)

    Args:
        nlp_obj: Objective value from NLP solve
        mcp_obj: Objective value from MCP solve
        rtol: Relative tolerance (default 1e-4)
        atol: Absolute tolerance (default 1e-8, matches IPOPT)

    Returns:
        Tuple of (match: bool, reason: str)
        - match: True if objectives match within tolerance
        - reason: Human-readable description of result
    """
    # Handle NaN values
    if math.isnan(nlp_obj) or math.isnan(mcp_obj):
        return (False, "NaN in objective value")

    # Handle Infinity values
    if math.isinf(nlp_obj) or math.isinf(mcp_obj):
        if values_close(nlp_obj, mcp_obj, rtol, atol):
            return (True, "Both objectives are infinite with same sign")
        return (False, "Infinity in objective value")

    # Delegate numeric comparison to values_close
    diff = abs(nlp_obj - mcp_obj)
    max_abs = max(abs(nlp_obj), abs(mcp_obj))
    tolerance = atol + rtol * max_abs

    if values_close(nlp_obj, mcp_obj, rtol, atol):
        return (True, f"Match within tolerance (diff={diff:.2e}, tol={tolerance:.2e})")
    else:
        return (False, f"Mismatch: diff={diff:.2e} > tolerance={tolerance:.2e}")


def values_close(
    a: float,
    b: float,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> bool:
    """Check if two values are close using combined tolerance.

    Uses: |a - b| <= atol + rtol * max(|a|, |b|)

    Handles NaN and Inf gracefully (returns False for NaN, True for matching Inf).
    """
    if math.isnan(a) or math.isnan(b):
        return False
    if math.isinf(a) or math.isinf(b):
        return math.isinf(a) and math.isinf(b) and (a > 0) == (b > 0)
    diff = abs(a - b)
    return diff <= atol + rtol * max(abs(a), abs(b))


def _parse_gams_value(s: str) -> float | None:
    """Parse a GAMS .lst numeric value.

    Handles: numbers, scientific notation, '.' (zero), 'EPS' (zero),
    '-INF', '+INF', 'INF', 'UNDF' (undefined → None).
    """
    s = s.strip()
    if s in (".", "EPS"):
        return 0.0
    if s == "UNDF":
        return None
    if s in ("INF", "+INF"):
        return float("inf")
    if s == "-INF":
        return float("-inf")
    try:
        return float(s)
    except ValueError:
        return None


def extract_variable_values(
    lst_content: str,
) -> dict[str, dict[str, float]]:
    """Extract primal variable LEVEL values from a GAMS .lst file.

    Parses both scalar and indexed variable sections.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        Dict mapping variable names to {index_key: level_value}.
        Scalar variables use '' as the index key.
        Example: {'x': {'': 5.0}, 'y': {'i1': 1.0, 'i2': 2.0}}
    """
    variables: dict[str, dict[str, float]] = {}
    # 4-column value token — accept any non-whitespace and let _parse_gams_value interpret
    val_tok = r"(\S+)"
    scalar_pat = re.compile(
        rf"^----\s+VAR\s+(\S+)\s+{val_tok}\s+{val_tok}\s+{val_tok}\s+{val_tok}",
        re.MULTILINE,
    )
    indexed_header = re.compile(r"^----\s+VAR\s+(\S+)\s*$", re.MULTILINE)
    data_row = re.compile(
        rf"^(\S+)\s+{val_tok}\s+{val_tok}\s+{val_tok}\s+{val_tok}",
        re.MULTILINE,
    )

    # Pass 1: scalar variables (all 4 values on same line as ---- VAR)
    for m in scalar_pat.finditer(lst_content):
        name = m.group(1)
        level = _parse_gams_value(m.group(3))  # LEVEL is 2nd column
        if level is not None:
            variables[name] = {"": level}

    # Pass 2: indexed variables (header line, then column header, then data rows)
    for m in indexed_header.finditer(lst_content):
        name = m.group(1)
        if name in variables:
            continue  # already parsed as scalar
        start = m.end()
        # Look for the LOWER/LEVEL/UPPER/MARGINAL header in nearby text (~300 chars)
        header_region = lst_content[start : start + 300]
        if not re.search(r"LOWER\s+LEVEL\s+UPPER\s+MARGINAL", header_region):
            continue
        # Find where header line ends, then parse data rows until next section
        header_match = re.search(r"MARGINAL\s*\n", header_region)
        if not header_match:
            continue
        data_start = start + header_match.end()
        # Parse data rows until blank line or next section marker
        vals: dict[str, float] = {}
        pos = data_start
        while pos < len(lst_content):
            line_end = lst_content.find("\n", pos)
            if line_end == -1:
                line = lst_content[pos:]
                line_end = len(lst_content)
            else:
                line = lst_content[pos:line_end]
            stripped = line.strip()
            if not stripped or stripped.startswith("----"):
                break
            row_m = data_row.match(stripped)
            if row_m:
                idx = row_m.group(1)
                level = _parse_gams_value(row_m.group(3))  # LEVEL column
                if level is not None:
                    vals[idx] = level
            pos = line_end + 1
        if vals:
            variables[name] = vals

    return variables


def extract_equation_marginals(
    lst_content: str,
) -> dict[str, dict[str, float]]:
    """Extract equation MARGINAL (dual) values from a GAMS .lst file.

    Parses both scalar and indexed equation sections.

    Args:
        lst_content: Contents of the .lst file

    Returns:
        Dict mapping equation names to {index_key: marginal_value}.
        Scalar equations use '' as the index key.
    """
    equations: dict[str, dict[str, float]] = {}
    val_tok = r"(\S+)"
    scalar_pat = re.compile(
        rf"^----\s+EQU\s+(\S+)\s+{val_tok}\s+{val_tok}\s+{val_tok}\s+{val_tok}",
        re.MULTILINE,
    )
    indexed_header = re.compile(r"^----\s+EQU\s+(\S+)\s*$", re.MULTILINE)
    data_row = re.compile(
        rf"^(\S+)\s+{val_tok}\s+{val_tok}\s+{val_tok}\s+{val_tok}",
        re.MULTILINE,
    )

    # Pass 1: scalar equations
    for m in scalar_pat.finditer(lst_content):
        name = m.group(1)
        marginal = _parse_gams_value(m.group(5))  # MARGINAL is 4th column
        if marginal is not None:
            equations[name] = {"": marginal}

    # Pass 2: indexed equations
    for m in indexed_header.finditer(lst_content):
        name = m.group(1)
        if name in equations:
            continue
        start = m.end()
        header_region = lst_content[start : start + 300]
        if not re.search(r"LOWER\s+LEVEL\s+UPPER\s+MARGINAL", header_region):
            continue
        header_match = re.search(r"MARGINAL\s*\n", header_region)
        if not header_match:
            continue
        data_start = start + header_match.end()
        vals: dict[str, float] = {}
        pos = data_start
        while pos < len(lst_content):
            line_end = lst_content.find("\n", pos)
            if line_end == -1:
                line = lst_content[pos:]
                line_end = len(lst_content)
            else:
                line = lst_content[pos:line_end]
            stripped = line.strip()
            if not stripped or stripped.startswith("----"):
                break
            row_m = data_row.match(stripped)
            if row_m:
                idx = row_m.group(1)
                marginal = _parse_gams_value(row_m.group(5))  # MARGINAL column
                if marginal is not None:
                    vals[idx] = marginal
            pos = line_end + 1
        if vals:
            equations[name] = vals

    return equations


def compare_variable_values(
    nlp_vars: dict[str, dict[str, float]],
    mcp_vars: dict[str, dict[str, float]],
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> dict[str, Any]:
    """Compare primal or dual variable values between NLP and MCP solutions.

    For each variable present in both solutions, computes:
    - max absolute difference across all indices
    - max relative difference across all indices
    - count of indices that diverge beyond tolerance

    Args:
        nlp_vars: Variables from NLP solution {name: {index: value}}
        mcp_vars: Variables from MCP solution {name: {index: value}}
        rtol: Relative tolerance
        atol: Absolute tolerance

    Returns:
        Dict with:
        - variables_compared: number of variables compared
        - variables_matched: number fully within tolerance
        - variables_diverged: number with at least one index outside tolerance
        - max_abs_diff: overall maximum absolute difference
        - max_rel_diff: overall maximum relative difference
        - worst_variable: name of variable with largest difference
        - per_variable: list of per-variable summaries (sorted by max abs diff descending, capped at the 10 worst entries)
    """
    common_vars = set(nlp_vars) & set(mcp_vars)
    per_variable: list[dict[str, Any]] = []
    overall_max_abs = 0.0
    overall_max_rel = 0.0
    worst_var = ""
    matched = 0
    diverged = 0

    for var_name in sorted(common_vars):
        nlp_vals = nlp_vars[var_name]
        mcp_vals = mcp_vars[var_name]
        common_idx = set(nlp_vals) & set(mcp_vals)
        if not common_idx:
            continue

        var_max_abs = 0.0
        var_max_rel = 0.0
        var_diverged = 0
        for idx in common_idx:
            a, b = nlp_vals[idx], mcp_vals[idx]
            if math.isnan(a) or math.isnan(b) or math.isinf(a) or math.isinf(b):
                if not values_close(a, b, rtol, atol):
                    var_diverged += 1
                continue
            diff = abs(a - b)
            max_abs = max(abs(a), abs(b))
            rel = diff / max_abs if max_abs > 0 else (0.0 if diff == 0 else float("inf"))
            var_max_abs = max(var_max_abs, diff)
            var_max_rel = max(var_max_rel, rel)
            if not values_close(a, b, rtol, atol):
                var_diverged += 1

        if var_max_abs > overall_max_abs or (var_diverged > 0 and not worst_var):
            overall_max_abs = max(overall_max_abs, var_max_abs)
            worst_var = var_name
        overall_max_rel = max(overall_max_rel, var_max_rel)

        if var_diverged == 0:
            matched += 1
        else:
            diverged += 1

        per_variable.append(
            {
                "name": var_name,
                "indices_compared": len(common_idx),
                "indices_diverged": var_diverged,
                "max_abs_diff": var_max_abs,
                "max_rel_diff": var_max_rel,
            }
        )

    # Sort by max abs diff descending
    per_variable.sort(key=lambda v: v["max_abs_diff"], reverse=True)

    return {
        "variables_compared": len(per_variable),
        "variables_matched": matched,
        "variables_diverged": diverged,
        "max_abs_diff": overall_max_abs,
        "max_rel_diff": overall_max_rel,
        "worst_variable": worst_var,
        "per_variable": per_variable[:10],  # Top 10 worst
    }


def compare_solutions(
    model: dict[str, Any],
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> dict[str, Any]:
    """Compare NLP and MCP solutions using decision tree.

    Decision tree with 7 outcomes:
    1. objective_match - Both solved optimally, objectives match
    2. objective_mismatch - Both solved optimally, objectives differ
    3. both_infeasible - Both NLP and MCP are infeasible
    4. status_mismatch (nlp_optimal) - NLP optimal but MCP failed/infeasible
    5. status_mismatch (mcp_optimal) - MCP optimal but NLP failed/infeasible
    6. nlp_solve_failed - NLP solve failed (no valid reference)
    7. mcp_solve_failed - MCP solve failed

    Args:
        model: Model dictionary with convexity and mcp_solve results
        rtol: Relative tolerance for objective comparison
        atol: Absolute tolerance for objective comparison

    Returns:
        Dictionary with comparison results matching solution_comparison_result schema
    """
    from datetime import UTC, datetime

    result: dict[str, Any] = {
        "comparison_status": "not_tested",
        "comparison_date": datetime.now(UTC).isoformat(),
        "nlp_objective": None,
        "mcp_objective": None,
        "absolute_difference": None,
        "relative_difference": None,
        "objective_match": None,
        "tolerance_absolute": atol,
        "tolerance_relative": rtol,
        "nlp_solver_status": None,
        "nlp_model_status": None,
        "mcp_solver_status": None,
        "mcp_model_status": None,
        "status_match": None,
        "comparison_result": COMPARE_NOT_PERFORMED,
        "notes": None,
    }

    # Get convexity (NLP) results
    convexity = model.get("convexity", {})
    nlp_solver_status = convexity.get("solver_status")
    nlp_model_status = convexity.get("model_status")
    nlp_objective = convexity.get("objective_value")

    result["nlp_solver_status"] = nlp_solver_status
    result["nlp_model_status"] = nlp_model_status
    result["nlp_objective"] = nlp_objective

    # Get MCP solve results
    mcp_solve = model.get("mcp_solve", {})
    mcp_solver_status = mcp_solve.get("solver_status")
    mcp_model_status = mcp_solve.get("model_status")
    mcp_objective = mcp_solve.get("objective_value")

    result["mcp_solver_status"] = mcp_solver_status
    result["mcp_model_status"] = mcp_model_status
    result["mcp_objective"] = mcp_objective

    # Check if NLP solve was successful (solver status 1, model status 1 or 2)
    nlp_solved = nlp_solver_status == 1 and nlp_model_status in (1, 2)
    nlp_infeasible = nlp_model_status in (4, 5, 6, 19)

    # Check if MCP solve was successful
    mcp_solved = mcp_solver_status == 1 and mcp_model_status in (1, 2)
    mcp_infeasible = mcp_model_status in (4, 5, 6, 19)

    # Decision tree
    # Case 0: Multi-solve model — NLP reference is from a different solve iteration
    if model.get("multi_solve"):
        result["comparison_status"] = "skipped"
        result["comparison_result"] = COMPARE_MULTI_SOLVE_SKIP
        result["notes"] = (
            "Multi-solve model: NLP reference captures a different solve iteration "
            "than the MCP formulation — objective comparison not meaningful"
        )
        return result

    # Case 7: NLP solve failed (no convexity data or failed solve)
    if not convexity or convexity.get("status") in ("error", "excluded", "license_limited"):
        result["comparison_status"] = "skipped"
        result["comparison_result"] = COMPARE_NLP_FAILED
        result["notes"] = f"NLP convexity status: {convexity.get('status', 'missing')}"
        return result

    # Case 6: MCP solve failed
    if not mcp_solve or mcp_solve.get("status") == "failure":
        result["comparison_status"] = "skipped"
        result["comparison_result"] = COMPARE_MCP_FAILED
        result["notes"] = f"MCP solve status: {mcp_solve.get('status', 'missing')}"
        return result

    # Case 3: Both infeasible
    if nlp_infeasible and mcp_infeasible:
        result["comparison_status"] = "match"
        result["comparison_result"] = COMPARE_BOTH_INFEASIBLE
        result["status_match"] = True
        result["notes"] = "Both NLP and MCP are infeasible (consistent result)"
        return result

    # Case 4: NLP optimal but MCP not optimal
    if nlp_solved and not mcp_solved:
        result["comparison_status"] = "mismatch"
        result["comparison_result"] = COMPARE_STATUS_MISMATCH
        result["status_match"] = False
        result["notes"] = (
            f"NLP optimal (status {nlp_model_status}) but MCP not optimal (status {mcp_model_status})"
        )
        return result

    # Case 5: MCP optimal but NLP not optimal
    if mcp_solved and not nlp_solved:
        result["comparison_status"] = "mismatch"
        result["comparison_result"] = COMPARE_STATUS_MISMATCH
        result["status_match"] = False
        result["notes"] = (
            f"MCP optimal (status {mcp_model_status}) but NLP not optimal (status {nlp_model_status})"
        )
        return result

    # Both solved optimally - compare objectives
    if nlp_solved and mcp_solved:
        result["status_match"] = True

        # Check if objectives are available
        if nlp_objective is None:
            result["comparison_status"] = "error"
            result["comparison_result"] = COMPARE_NOT_PERFORMED
            result["notes"] = "NLP objective value not available"
            return result

        if mcp_objective is None:
            result["comparison_status"] = "error"
            result["comparison_result"] = COMPARE_NOT_PERFORMED
            result["notes"] = "MCP objective value not available"
            return result

        # Calculate differences
        diff = abs(nlp_objective - mcp_objective)
        result["absolute_difference"] = diff

        # Relative difference (protect against division by zero)
        max_abs = max(abs(nlp_objective), abs(mcp_objective), 1e-10)
        result["relative_difference"] = diff / max_abs

        # Compare objectives
        match, reason = objectives_match(nlp_objective, mcp_objective, rtol, atol)
        result["objective_match"] = match

        if match:
            # Case 1: Objectives match
            result["comparison_status"] = "match"
            result["comparison_result"] = COMPARE_OBJECTIVE_MATCH
            result["notes"] = reason
        else:
            # Case 2: Objectives mismatch
            result["comparison_status"] = "mismatch"
            result["comparison_result"] = COMPARE_OBJECTIVE_MISMATCH
            result["notes"] = reason

        return result

    # Fallback: neither optimal nor infeasible in expected pattern
    result["comparison_status"] = "error"
    result["comparison_result"] = COMPARE_NOT_PERFORMED
    result["notes"] = (
        f"Unexpected status combination: NLP({nlp_solver_status}/{nlp_model_status}), MCP({mcp_solver_status}/{mcp_model_status})"
    )
    return result


def solve_mcp(mcp_path: Path, timeout: int = 120) -> dict[str, Any]:
    """Solve an MCP model using PATH solver.

    Args:
        mcp_path: Path to the MCP .gms file
        timeout: Maximum solve time in seconds (default: 120)

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

    # Find GAMS executable — prefer versioned paths over PATH lookup
    # (PATH may find an older version with expired license)
    gams_exe = None
    for path in [
        "/Library/Frameworks/GAMS.framework/Versions/53/Resources/gams",
        "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
        "/opt/gams/gams",
        "C:\\GAMS\\win64\\gams.exe",
    ]:
        if Path(path).exists():
            gams_exe = path
            break
    if not gams_exe:
        gams_exe = shutil.which("gams")

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
            # Run GAMS with PATH solver. cwd must be the project root so that
            # the repo-relative `$include "data/gamslib/raw/<model>.gms"` line
            # emitted by `--nlp-presolve` resolves (#1275 changed the include
            # from absolute to repo-relative). ScrDir keeps scratch files
            # (`225a/`, .gdx, .pf) out of the project tree.
            cmd = [
                gams_exe,
                str(mcp_path),
                f"o={lst_path}",
                "lo=3",  # Detailed log output
                f"reslim={timeout}",  # Time limit
                f"ScrDir={tmpdir}",
            ]

            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10,  # Allow extra time for GAMS overhead
                cwd=str(PROJECT_ROOT),
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

        # Extract PATH solver version from .lst file
        path_version = extract_path_version(lst_content)

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
            "solver_version": path_version,
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
                desc = SOLVER_STATUS_DESCRIPTIONS.get(int(solver_status), "Unknown") if solver_status is not None else "Unknown"
                result["error"] = f"Solver: {desc} (status {solver_status})"
            elif model_status not in (1, 2):
                desc = MODEL_STATUS_DESCRIPTIONS.get(int(model_status), "Unknown") if model_status is not None else "Unknown"
                result["error"] = f"Model: {desc} (status {model_status})"
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
        "solver_version": solve_result.get("solver_version"),
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

    # Print comparison results if enabled
    if stats.get("comparison_enabled"):
        print("\n" + "-" * 40)
        print("SOLUTION COMPARISON RESULTS")
        print("-" * 40)

        if stats.get("comparison_results"):
            print("\nComparison outcomes:")
            for cat, count in sorted(
                stats["comparison_results"].items(),
                key=lambda x: -x[1],
            ):
                print(f"  {cat}: {count}")

        if stats.get("objective_matches"):
            print(f"\nObjective matches ({len(stats['objective_matches'])}):")
            for model_id in sorted(stats["objective_matches"]):
                print(f"  - {model_id}")

        if stats.get("objective_mismatches"):
            print(f"\nObjective MISMATCHES ({len(stats['objective_mismatches'])}):")
            for model_id in sorted(stats["objective_mismatches"]):
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
        # Comparison stats (only populated if --compare is used)
        "comparison_enabled": args.compare,
        "comparison_results": {},
        "objective_matches": [],
        "objective_mismatches": [],
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
        result = solve_mcp(mcp_file, timeout=120)

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
        target_model = None
        for m in all_models:
            if m.get("model_id") == model_id:
                update_model_solve_result(m, result)
                target_model = m
                break

        # Update stats
        if result["status"] == "success":
            stats["success"] += 1
            stats["successful_models"].append(model_id)
        else:
            stats["failure"] += 1

        outcome = result.get("outcome_category", "unknown")
        stats["outcome_categories"][outcome] = stats["outcome_categories"].get(outcome, 0) + 1

        # Run solution comparison if enabled
        if args.compare and target_model:
            comparison = compare_solutions(target_model, rtol=args.rtol, atol=args.atol)
            target_model["solution_comparison"] = comparison

            # Log comparison result
            comp_result = comparison.get("comparison_result", "unknown")
            stats["comparison_results"][comp_result] = (
                stats["comparison_results"].get(comp_result, 0) + 1
            )

            if comp_result == COMPARE_OBJECTIVE_MATCH:
                stats["objective_matches"].append(model_id)
            elif comp_result == COMPARE_OBJECTIVE_MISMATCH:
                stats["objective_mismatches"].append(model_id)

            if args.verbose:
                logger.info(f"  Comparison: {comparison['comparison_status']}")
                if comparison.get("nlp_objective") is not None:
                    logger.info(f"  NLP objective: {comparison['nlp_objective']}")
                if comparison.get("mcp_objective") is not None:
                    logger.info(f"  MCP objective: {comparison['mcp_objective']}")
                if comparison.get("notes"):
                    logger.info(f"  Notes: {comparison['notes']}")

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

    # Comparison arguments
    compare_group = parser.add_argument_group("Comparison Options")
    compare_group.add_argument(
        "--compare",
        action="store_true",
        help="Compare NLP and MCP solutions after solving",
    )
    compare_group.add_argument(
        "--rtol",
        type=float,
        default=DEFAULT_RTOL,
        help=f"Relative tolerance for objective comparison (default: {DEFAULT_RTOL})",
    )
    compare_group.add_argument(
        "--atol",
        type=float,
        default=DEFAULT_ATOL,
        help=f"Absolute tolerance for objective comparison (default: {DEFAULT_ATOL})",
    )

    args = parser.parse_args()

    return run_batch_solve(args)


if __name__ == "__main__":
    sys.exit(main())
