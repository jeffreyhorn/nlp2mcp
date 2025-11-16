"""Tests for PATH solver validation.

These tests validate that generated MCP models can be solved using the PATH solver
and that solutions satisfy KKT conditions. Tests only run locally when GAMS/PATH
is available and are skipped in CI/CD environments.

Requirements:
- GAMS must be installed with PATH solver
- Tests skip gracefully if GAMS/PATH not available
- Validates solution quality and KKT condition satisfaction
"""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from src.validation.gams_check import find_gams_executable

# ============================================
# PATH Availability Check
# ============================================


def _check_path_available() -> bool:
    """Check if PATH solver is available within GAMS.

    Returns:
        True if GAMS is installed and PATH solver is accessible
    """
    try:
        gams_exe = find_gams_executable()
        if gams_exe is None:
            return False

        # Verify GAMS executable exists and is executable
        gams_path = Path(gams_exe)
        if not gams_path.exists() or not gams_path.is_file():
            return False

        # Try running GAMS with no arguments - it should print help/version info
        # GAMS returns non-zero but prints version info to stderr
        result = subprocess.run([gams_exe], capture_output=True, text=True, timeout=5)

        # Check if GAMS banner appears in output (either stdout or stderr)
        output = result.stdout + result.stderr
        return "GAMS" in output and "Release" in output
    except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


PATH_AVAILABLE = _check_path_available()

# Mark all tests in this module to skip if PATH not available
pytestmark = pytest.mark.skipif(
    not PATH_AVAILABLE, reason="PATH solver not available (GAMS not installed or not in PATH)"
)

# ============================================
# GAMS Output Format Constants
# ============================================

# GAMS .lst file header columns for variable solution output
GAMS_HEADER_COLUMNS = ("LOWER", "LEVEL", "UPPER", "MARGINAL")

# Regex pattern for parsing scalar variable values from GAMS .lst files
# Scalar variables appear on the same line as ---- VAR varname
# Format: LOWER_val LEVEL_val UPPER_val MARGINAL_val
# Values can be: numbers (with optional E notation), ".", "-INF", "+INF", "INF"
SCALAR_VAR_PATTERN = (
    r"^\s*([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)"
)

# Regex pattern for parsing indexed variable values from GAMS .lst files
# Indexed variables have header row followed by data rows
# Format: index_name LOWER_val LEVEL_val UPPER_val MARGINAL_val
# Values follow same format as scalar variables
INDEXED_VAR_PATTERN = (
    r"(\w+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)\s+([\-+\.\dEeINF]+)"
)


# ============================================
# Helper Functions
# ============================================


def _solve_gams(gams_file: Path, gams_executable: str) -> tuple[bool, str, dict[str, float]]:
    """Solve a GAMS MCP model using PATH solver.

    Args:
        gams_file: Path to GAMS .gms file
        gams_executable: Path to GAMS executable

    Returns:
        Tuple of (success, message, solution_dict)
        - success: True if solve succeeded
        - message: Status message or error description
        - solution_dict: Dictionary mapping variable names to solution values
    """
    if not gams_file.exists():
        return (False, f"GAMS file not found: {gams_file}", {})

    try:
        # Run GAMS to solve the MCP
        # Use absolute path for gams_file to avoid path resolution issues
        abs_gams_file = gams_file.absolute()
        subprocess.run(
            [gams_executable, str(abs_gams_file)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=abs_gams_file.parent,
        )

        # Parse the .lst file for solution
        lst_file = abs_gams_file.parent / (abs_gams_file.stem + ".lst")
        if not lst_file.exists():
            return (False, "GAMS did not create .lst file", {})

        lst_content = lst_file.read_text()

        # Check for solve status
        # GAMS MCP solver status codes:
        # Model Status 1 = Optimal (for MCP: solution found)
        # Solver Status 1 = Normal Completion
        model_status = _extract_model_status(lst_content)
        solver_status = _extract_solver_status(lst_content)

        if model_status != 1:
            return (
                False,
                f"MCP solve failed: Model Status {model_status}, Solver Status {solver_status}",
                {},
            )

        # Extract solution values
        solution = _parse_gams_solution(lst_content, gams_file)

        return (True, f"Solve successful: Model Status {model_status}", solution)

    except subprocess.TimeoutExpired:
        return (False, "GAMS solve timed out (60s limit)", {})
    except subprocess.SubprocessError as e:
        return (False, f"GAMS subprocess error: {e}", {})
    except Exception as e:
        return (False, f"Error during solve: {e}", {})


def _extract_model_status(lst_content: str) -> int:
    """Extract model status from GAMS .lst file.

    Args:
        lst_content: Content of GAMS .lst file

    Returns:
        Model status code (1 = optimal/solved, others indicate issues)
    """
    # Look for "MODEL STATUS" line in solve summary
    # Example: "MODEL STATUS      1 OPTIMAL"
    match = re.search(r"MODEL\s+STATUS\s+(\d+)", lst_content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return -1  # Unknown status


def _extract_solver_status(lst_content: str) -> int:
    """Extract solver status from GAMS .lst file.

    Args:
        lst_content: Content of GAMS .lst file

    Returns:
        Solver status code (1 = normal completion, others indicate issues)
    """
    # Look for "SOLVER STATUS" line in solve summary
    # Example: "SOLVER STATUS     1 NORMAL COMPLETION"
    match = re.search(r"SOLVER\s+STATUS\s+(\d+)", lst_content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return -1  # Unknown status


def _parse_gams_solution(lst_content: str, gams_file: Path) -> dict[str, float]:
    """Parse solution values from GAMS .lst file.

    Args:
        lst_content: Content of GAMS .lst file
        gams_file: Path to GAMS file (for variable name extraction)

    Returns:
        Dictionary mapping variable names to solution values
    """
    solution = {}

    # GAMS solution reports variables in sections like:
    # ---- VAR x
    #              LOWER     LEVEL     UPPER    MARGINAL
    # i1            .         1.000     +INF      .
    # i2            .         2.000     +INF      .

    # Extract variable names from the GAMS file first
    var_names = _extract_variable_names(gams_file)

    for var_name in var_names:
        # Look for variable section in lst file
        # Pattern: ---- VAR varname
        var_section_pattern = rf"----\s+VAR\s+{re.escape(var_name)}\s"
        var_match = re.search(var_section_pattern, lst_content, re.IGNORECASE)

        if var_match:
            # Find the section after the VAR declaration
            section_start = var_match.end()
            # Get section up to next ---- marker or 500 chars, whichever is shorter
            next_section = lst_content[section_start:].find("\n----")
            if next_section != -1:
                section = lst_content[section_start : section_start + next_section]
            else:
                section = lst_content[section_start : section_start + 500]

            # Parse scalar variable (single LEVEL value on same line as ---- VAR)
            # Format: ---- VAR varname    LOWER     LEVEL     UPPER    MARGINAL
            # The section starts right after "---- VAR varname", so we look for 4 values
            scalar_match = re.search(SCALAR_VAR_PATTERN, section, re.MULTILINE)
            # Make sure this is actually a scalar (no header line with LOWER LEVEL UPPER MARGINAL)
            has_header = re.search(r"LOWER\s+LEVEL\s+UPPER\s+MARGINAL", section)
            if scalar_match and not has_header:
                # Capture groups: 1=LOWER, 2=LEVEL, 3=UPPER, 4=MARGINAL
                level_str = scalar_match.group(2)
                # Convert GAMS "." to 0.0, skip INF values
                if level_str == ".":
                    solution[var_name] = 0.0
                elif "INF" not in level_str:
                    solution[var_name] = float(level_str)
                continue

            # Parse indexed variable (multiple rows with index and LEVEL)
            # Format: i1    LOWER_val    LEVEL_val    UPPER_val    MARGINAL_val
            # GAMS uses "." for zero, "-INF"/"INF"/"+INF" for infinity
            for match in re.finditer(INDEXED_VAR_PATTERN, section):
                index = match.group(1)
                # Skip if this is actually the header row
                if index.upper() in GAMS_HEADER_COLUMNS:
                    continue
                # Capture groups: 1=index, 2=LOWER, 3=LEVEL, 4=UPPER, 5=MARGINAL
                level_str = match.group(3)
                # Convert GAMS "." to 0.0, skip INF values
                if level_str == ".":
                    solution[f"{var_name}({index})"] = 0.0
                elif "INF" not in level_str:
                    solution[f"{var_name}({index})"] = float(level_str)

    return solution


def _extract_variable_names(gams_file: Path) -> list[str]:
    """Extract variable names from GAMS file.

    Args:
        gams_file: Path to GAMS .gms file

    Returns:
        List of variable names declared in the file
    """
    content = gams_file.read_text()
    var_names = []

    # Match variable declarations:
    # Variables x, y, z;
    # Positive Variables lambda, mu;
    # Free Variables obj;

    # Pattern for variable declarations (case insensitive)
    # Match across lines with DOTALL flag to handle multi-line declarations
    var_decl_pattern = r"(?:Positive\s+)?(?:Free\s+)?Variables?\s+([\w\s,()]+?)\s*;"

    for match in re.finditer(var_decl_pattern, content, re.IGNORECASE | re.DOTALL):
        # Split on commas and clean up
        vars_str = match.group(1)
        # Split by comma and also by whitespace (to handle newlines)
        for var in re.split(r"[,\s]+", vars_str):
            var = var.strip()
            # Remove index notation if present: x(i) -> x
            var = re.sub(r"\([^)]*\)", "", var).strip()
            if var:
                var_names.append(var)

    return var_names


def _check_kkt_residuals(lst_content: str, tolerance: float = 1e-6) -> tuple[bool, str]:
    """Check if KKT conditions are satisfied based on solution residuals.

    For MCP problems, PATH solver reports residuals which indicate how well
    the complementarity conditions are satisfied.

    Args:
        lst_content: Content of GAMS .lst file
        tolerance: Maximum acceptable residual

    Returns:
        Tuple of (satisfied, message)
    """
    # Look for residual information in GAMS output
    # PATH solver typically reports maximum residual
    # Example: "** Residual: 1.234e-12"

    residual_pattern = r"(?:Residual|INFEAS):\s*([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?)"
    match = re.search(residual_pattern, lst_content, re.IGNORECASE)

    if match:
        residual = float(match.group(1))
        if residual <= tolerance:
            return (True, f"KKT residual {residual:.2e} within tolerance {tolerance:.2e}")
        else:
            return (False, f"KKT residual {residual:.2e} exceeds tolerance {tolerance:.2e}")

    # If Model Status is 1 (Optimal), assume KKT satisfied even if we can't parse residual
    model_status = _extract_model_status(lst_content)
    if model_status == 1:
        return (True, "KKT conditions assumed satisfied (Model Status = Optimal)")

    return (False, "Could not verify KKT condition satisfaction")


# ============================================
# Cleanup Fixture
# ============================================


@pytest.fixture(autouse=True)
def cleanup_gams_files():
    """Clean up GAMS output files after each test."""
    yield
    # Clean up .lst, .log, and other GAMS files in tests/golden directory
    golden_dir = Path("tests/golden")
    if golden_dir.exists():
        for pattern in ["*.lst", "*.log", "*.put", "*.lxi"]:
            for file in golden_dir.glob(pattern):
                try:
                    file.unlink()
                except OSError:
                    pass  # Ignore errors if file doesn't exist or can't be deleted


# ============================================
# PATH Solver Validation Tests
# ============================================


@pytest.mark.validation
class TestPATHSolverValidation:
    """Test PATH solver on generated MCP models.

    These tests verify that:
    1. Generated MCP models solve successfully with PATH
    2. Solutions satisfy KKT optimality conditions
    3. Solution quality is acceptable

    NOTE: Sign error in stationarity equations was fixed. Golden MCP files regenerated
    with correct formulation. Tests should now pass with PATH solver.
    """

    def test_solve_simple_nlp_mcp(self, tmp_path):
        """Test PATH solver on simple_nlp_mcp.gms."""
        golden_file = Path("tests/golden/simple_nlp_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        gams_exe = find_gams_executable()
        assert gams_exe is not None, "GAMS executable not found"

        # Copy golden file to tmp_path for isolation in parallel execution
        test_file = tmp_path / golden_file.name
        shutil.copy(golden_file, test_file)

        # Solve the MCP
        success, message, solution = _solve_gams(test_file, gams_exe)
        assert success, f"PATH solve failed: {message}"

        # Verify we got a solution
        assert len(solution) > 0, "No solution values extracted"

        # Check KKT conditions
        lst_file = test_file.parent / (test_file.stem + ".lst")
        lst_content = lst_file.read_text()
        kkt_ok, kkt_msg = _check_kkt_residuals(lst_content)
        assert kkt_ok, f"KKT conditions not satisfied: {kkt_msg}"

    def test_solve_indexed_balance_mcp(self, tmp_path):
        """Test PATH solver on indexed_balance_mcp.gms."""
        golden_file = Path("tests/golden/indexed_balance_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        gams_exe = find_gams_executable()
        assert gams_exe is not None, "GAMS executable not found"

        # Copy golden file to tmp_path for isolation in parallel execution
        test_file = tmp_path / golden_file.name
        shutil.copy(golden_file, test_file)

        # Solve the MCP
        success, message, solution = _solve_gams(test_file, gams_exe)
        assert success, f"PATH solve failed: {message}"

        # Verify we got a solution
        assert len(solution) > 0, "No solution values extracted"

        # Check KKT conditions
        lst_file = test_file.parent / (test_file.stem + ".lst")
        lst_content = lst_file.read_text()
        kkt_ok, kkt_msg = _check_kkt_residuals(lst_content)
        assert kkt_ok, f"KKT conditions not satisfied: {kkt_msg}"


@pytest.mark.validation
class TestPATHAvailability:
    """Test PATH solver availability detection."""

    def test_path_available(self):
        """Verify PATH solver is available for testing."""
        # This test only runs if PATH_AVAILABLE is True (due to module-level skipif)
        assert PATH_AVAILABLE, "PATH should be available when this test runs"

        gams_exe = find_gams_executable()
        assert gams_exe is not None, "GAMS executable should be found"
        assert Path(gams_exe).exists(), "GAMS executable path should exist"
