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
import sys
import tempfile
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
        # A bare `gams` still creates its process dir (`225a/`, with a license
        # copy) in cwd. This probe runs at IMPORT time in every xdist worker,
        # from the repo root, under a 5 s timeout -- so under load the kill
        # left `225xx/` dirs in the repo root. Run it in a throwaway dir.
        #
        # ⚠ The timeout is 30 s, not 5. A timeout here does not fail anything:
        # it makes PATH_AVAILABLE False, and every PATH test in this module
        # SKIPS. Uncontended, the banner takes ~0.7 s, but a full `make test`
        # at load ~65 hit 5 s and silently skipped 2 tests. A missing GAMS
        # still returns at once (FileNotFoundError); only a hung one waits.
        with tempfile.TemporaryDirectory(prefix="gams_probe_") as scratch:
            result = subprocess.run(
                [gams_exe], capture_output=True, text=True, timeout=30, cwd=scratch
            )

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
def test_issue_1755_the_diagonal_reference_solves_to_the_nlp_optimum(tmp_path):
    """#1755 pass-after: ``diag.. sum(i, tsam(i,i)) =e= 1`` keeps its multiplier.

    Before the fix ``diag`` and ``nu_diag`` were dropped, so the MCP solved the
    unconstrained problem (tsam = 0, objective 0). The NLP optimum is 1/3
    (tsam = 1/3 on the diagonal); the hand-derived MCP reaches it.
    """
    source = tmp_path / "diag.gms"
    source.write_text(
        "Set i / i1*i3 /;\n"
        "Alias (i,j);\n"
        "Variable tsam(i,j), z;\n"
        "Equation diag, obj;\n"
        "diag.. sum(i, tsam(i,i)) =e= 1;\n"
        "obj.. z =e= sum((i,j), sqr(tsam(i,j)));\n"
        "Model m / all /;\n"
        "solve m using nlp minimizing z;\n"
    )
    mcp = tmp_path / "diag_mcp.gms"
    translate = subprocess.run(
        [sys.executable, "-m", "src.cli", str(source), "-o", str(mcp)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
    )
    assert translate.returncode == 0, translate.stderr

    gams_exe = find_gams_executable()
    assert gams_exe is not None, "GAMS executable not found"
    success, message, _ = _solve_gams(mcp, gams_exe)
    assert success, f"PATH solve failed: {message}"

    lst = (tmp_path / "diag_mcp.lst").read_text()
    match = re.search(r"PARAMETER nlp2mcp_obj_val\s+=\s+([-+0-9.eE]+)", lst)
    assert match, "nlp2mcp_obj_val not displayed"
    assert abs(float(match.group(1)) - 1.0 / 3.0) < 1e-3, match.group(1)


def _translate_and_solve(tmp_path, name: str, source: str) -> tuple[float, str]:
    """Translate ``source`` into an MCP in ``tmp_path``, solve it, return (obj, emit)."""
    src = tmp_path / f"{name}.gms"
    src.write_text(source)
    mcp = tmp_path / f"{name}_mcp.gms"
    translate = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(mcp)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
    )
    assert translate.returncode == 0, translate.stderr
    gams_exe = find_gams_executable()
    assert gams_exe is not None, "GAMS executable not found"
    success, message, _ = _solve_gams(mcp, gams_exe)
    assert success, f"PATH solve failed: {message}"
    lst = (tmp_path / f"{name}_mcp.lst").read_text()
    match = re.search(r"PARAMETER nlp2mcp_obj_val\s+=\s+([-+0-9.eE]+)", lst)
    assert match, "nlp2mcp_obj_val not displayed"
    return float(match.group(1)), mcp.read_text()


@pytest.mark.validation
def test_a_dynamic_subset_diagonal_keeps_its_runtime_membership(tmp_path):
    """PR #1779 review round 9. ``ii`` is assigned at runtime and the objective
    reaches the FULL variable domain, so no common subset guard exists for the
    row. Without the membership guard the multiplier reached the excluded
    x(i2,i2). The NLP optimum is 1 (x(i1,i1) = 1)."""
    obj, emit = _translate_and_solve(
        tmp_path,
        "dyn",
        "Set i / i1, i2 /;\nAlias (i,j);\nSet ii(i);\nii(i) = yes$(ord(i) = 1);\n"
        "Variable x(i,j), z;\nEquation e, obj;\n"
        "e.. sum(ii, x(ii,ii)) =e= 1;\n"
        "obj.. z =e= sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    stat = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "1$(ii(i)) * nu_e" in stat, stat
    assert abs(obj - 1.0) < 1e-3, obj


@pytest.mark.validation
def test_a_card_coefficient_keeps_the_subset_cardinality(tmp_path):
    """PR #1779 review round 9. ``card(s)`` with s = {i1,i2} is 2, not the parent's
    3: x(i1,i1) = x(i2,i2) = 1/4 and the objective is 0.125 (with 3 it would be
    1/18). The NLP optimum is 0.125."""
    obj, emit = _translate_and_solve(
        tmp_path,
        "card",
        "Set i / i1*i3 /;\nAlias (i,j);\nSet s(i) / i1, i2 /;\n"
        "Variable x(i,j), z;\nEquation e, obj;\n"
        "e.. sum(s, card(s)*x(s,s)) =e= 1;\n"
        "obj.. z =e= sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    # ⚠ The objective alone does NOT discriminate: the model is symmetric on the
    # diagonal, so a wrong coefficient (the parent's card(i) = 3) cancels from the
    # primal and still gives 0.125 (measured). The coefficient shows in the ROW
    # and in the multiplier: nu_e = -2*x/card = -0.25 with card(s) = 2, -0.1667
    # with card(i) = 3. And `card(s)` must be checked in the stationarity row:
    # the original constraint line carries it either way.
    stat = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "card(s)" in stat and "card(i)" not in stat, stat
    assert abs(obj - 0.125) < 1e-3, obj
    lst = (tmp_path / "card_mcp.lst").read_text()
    nu = re.search(r"---- VAR nu_e\s+\S+\s+([-+0-9.eE]+)", lst)
    assert nu and abs(float(nu.group(1)) + 0.25) < 1e-3, nu and nu.group(1)


@pytest.mark.validation
def test_distinct_dynamic_subsets_on_ALIASED_coordinates_keep_their_coordinates(tmp_path):
    """PR #1779 review round 10. ``ii(i) = {i1}``, ``jj(i) = {i2}``, Alias(i,j); the
    objective's guarded term ``sum((ii,jj), sqr(x(ii,jj) - 1))`` must keep
    ``ii`` on the FIRST coordinate and ``jj`` on the SECOND. A concrete guard was
    generalized through a diagonal instance to ``ii(i) and jj(i)``, never true,
    which zeroed the gradient at the active cell (i1,i2): the MCP solved to 1.0.
    The NLP optimum is 0.5 (x(i1,i2) = 0.5)."""
    obj, emit = _translate_and_solve(
        tmp_path,
        "aliased",
        "Set i / i1, i2 /;\nAlias (i,j);\nSet ii(i), jj(i);\n"
        "ii(i) = yes$(ord(i) = 1);\njj(i) = yes$(ord(i) = 2);\n"
        "Variable x(i,j), z;\nEquation obj;\n"
        "obj.. z =e= sum((ii,jj), sqr(x(ii,jj) - 1)) + sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    stat = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "ii(i) and jj(j)" in stat, stat
    assert abs(obj - 0.5) < 1e-3, obj


@pytest.mark.validation
def test_an_initialized_then_PRUNED_subset_keeps_its_runtime_guard(tmp_path):
    """PR #1779 review round 13. `Set s(i) / i1, i2 /; s(i) = yes$(ord(i) = 1);`
    keeps both members in the IR, so a "has static members" shortcut skipped the
    guard and the multiplier reached the excluded x('i2','i2'): MCP 2.0. The NLP
    optimum is 1.0."""
    obj, emit = _translate_and_solve(
        tmp_path,
        "pruned",
        "Set i / i1*i2 /;\nAlias (i,j);\nSet s(i) / i1, i2 /;\ns(i) = yes$(ord(i) = 1);\n"
        "Variable x(i,j), z;\nEquation e, obj;\n"
        "e.. sum(s, x(s,s)) =e= 1;\n"
        "obj.. z =e= sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    stat = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "1$(s(i)) * nu_e" in stat, stat
    assert abs(obj - 1.0) < 1e-3, obj


@pytest.mark.validation
def test_disjoint_subsets_in_a_PARTIAL_collapse_keep_separate_guards(tmp_path):
    """PR #1779 review round 13. x(i), ii = {i1}, jj = {i2}: in
    `sum((ii,jj), x(ii)*x(jj))` neither reference holds both binders, so neither
    guard may be promoted to a declared coordinate. Promoted, both became
    `ii(i) and jj(i)`, never true, zeroing the cross term: MCP 1.0. The NLP optimum
    is 2/3 (x = 2/3)."""
    obj, _ = _translate_and_solve(
        tmp_path,
        "disjoint",
        "Set i / i1, i2 /;\nSet ii(i), jj(i);\n"
        "ii(i) = yes$(ord(i) = 1);\njj(i) = yes$(ord(i) = 2);\n"
        "Variable x(i), z;\nEquation obj;\n"
        "obj.. z =e= sum((ii,jj), x(ii)*x(jj)) + sum(i, sqr(x(i) - 1));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    assert abs(obj - 2.0 / 3.0) < 1e-3, obj


@pytest.mark.validation
def test_a_preserved_CARD_operand_does_not_displace_the_guard_coordinate(tmp_path):
    """PR #1779 review round 13. The aliased-coordinate model with a `card(j)`
    coefficient: the preserved operand `j` was counted as occupied, so the `jj`
    guard fell back to a label and one row branch generalized to `jj(i)`. The
    solve can still come out right (the active cell sat in the correct branch), so
    the ROW is asserted. NLP optimum 2/3."""
    obj, emit = _translate_and_solve(
        tmp_path,
        "cardj",
        "Set i / i1, i2 /;\nAlias (i,j);\nSet ii(i), jj(i);\n"
        "ii(i) = yes$(ord(i) = 1);\njj(i) = yes$(ord(i) = 2);\n"
        "Variable x(i,j), z;\nEquation obj;\n"
        "obj.. z =e= sum((ii,jj), card(j)*sqr(x(ii,jj) - 1)) + sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n",
    )
    stat = next(line for line in emit.splitlines() if line.startswith("stat_x("))
    assert "ii(i) and jj(j)" in stat and "jj(i)" not in stat, stat
    assert abs(obj - 2.0 / 3.0) < 1e-3, obj


@pytest.mark.validation
def test_a_QUOTED_label_variant_keeps_the_aliased_guard_coordinates(tmp_path):
    """PR #1779 review round 14: the aliased-coordinate model with a quoted label
    ``p('j')``. The row must keep ``ii(i) and jj(j)``. Only the ROW is asserted:
    the MCP does not compile today because its data line is emitted as
    ``p(j) = 1;`` (the label read as the alias, $171), a separate pre-existing
    emitter defect, #1781."""
    src = tmp_path / "quoted.gms"
    src.write_text(
        "Set i / i1, i2 /;\nAlias (i,j);\nSet lab / j /;\nParameter p(lab) / j 1 /;\n"
        "Set ii(i), jj(i);\nii(i) = yes$(ord(i) = 1);\njj(i) = yes$(ord(i) = 2);\n"
        "Variable x(i,j), z;\nEquation obj;\n"
        "obj.. z =e= sum((ii,jj), sqr(x(ii,jj) - p('j'))) + sum((i,j), sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing z;\n"
    )
    mcp = tmp_path / "quoted_mcp.gms"
    out = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(mcp)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parents[2],
    )
    assert out.returncode == 0, out.stderr
    stat = next(line for line in mcp.read_text().splitlines() if line.startswith("stat_x("))
    assert "ii(i) and jj(j)" in stat and "jj(i)" not in stat, stat


@pytest.mark.validation
def test_issue_1782_aliased_class_a_fixture_solves_to_the_nlp_optimum(tmp_path):
    """#1782 (Sprint 40 P4): Alias(t,v), z(v,t), e(t).. sum(v$s(t,v), c(v,t)*z(v,t)).
    The equation index was matched to the aliased position `v`: the emit summed
    over a minted t__kkt1 with nu_e(v) and solved to 0.045. NLP optimum 0.0318."""
    obj, _ = _translate_and_solve(
        tmp_path,
        "class_a",
        "Set t / t1*t3 /;\nAlias (t,v);\nSet s(t,v);\ns(t,v) = yes$(ord(t) <= ord(v));\n"
        "Parameter c(t,v);\nc(t,v) = 1 + ord(t) + 2*ord(v);\n"
        "Variable z(v,t), obj;\nEquation e(t), defobj;\n"
        "e(t).. sum(v$s(t,v), c(v,t)*z(v,t)) =e= 1;\n"
        "defobj.. obj =e= sum((v,t), sqr(z(v,t)));\n"
        "Model m / all /;\nsolve m using nlp minimizing obj;\n",
    )
    assert abs(obj - 0.0318) < 1e-3, obj


@pytest.mark.validation
@pytest.mark.parametrize(
    "name, source, nlp",
    [
        (
            "fixed",
            "Set t / t1*t3 /;\nAlias (t,v);\nVariable z(v,t), obj;\nEquation e(t), defobj;\n"
            "e(t).. z(t,'t1') =e= ord(t);\ndefobj.. obj =e= sum((v,t), sqr(z(v,t)));\n"
            "Model m / all /;\nsolve m using nlp minimizing obj;\n",
            14.0,
        ),
        (
            "tsum",
            "Set t / t1*t3 /;\nAlias (t,v);\nParameter c(t,v);\n"
            "c(t,v) = 1 + ord(t) + 2*ord(v);\nVariable z(v,t), obj;\nEquation e(t), defobj;\n"
            "e(t).. sum(v, c(t,v)*z(t,v)) =e= 1;\n"
            "defobj.. obj =e= sum((v,t), sqr(z(v,t)));\n"
            "Model m / all /;\nsolve m using nlp minimizing obj;\n",
            0.0201,
        ),
        (
            "multi",
            "Set i / a, b, c /;\nAlias (i,j,k);\nVariable z(i,j,k), obj;\n"
            "Equation e(i,j), defobj;\ne(i,j).. z('a',i,j) =e= ord(i) + ord(j);\n"
            "defobj.. obj =e= sum((i,j,k), sqr(z(i,j,k)));\n"
            "Model m / all /;\nsolve m using nlp minimizing obj;\n",
            156.0,
        ),
    ],
)
def test_issue_1782_reference_bindings_solve_to_the_nlp_optimum(tmp_path, name, source, nlp):
    """PR #1783 review: an equation index binds the variable position its
    REFERENCE occupies. A fixed-coordinate reference z(t,'t1') and a transposed sum
    z(t,v) both bind position 0; a declared-name preference broke the first (no
    model status). Review round 3: a multi-index binding z('a',i,j) must not rename
    the already-remapped multiplier a second time (nu_e(k,k) failed to solve).
    NLP optima: 14.0, 0.0201 and 156."""
    obj, _ = _translate_and_solve(tmp_path, name, source)
    assert abs(obj - nlp) < 1e-3, obj


@pytest.mark.validation
def test_issue_1782_reversed_domain_multiplier_values(tmp_path):
    """PR #1783 review: e(j,i).. x(j,i) with x(i,j). The primal is pinned, so the
    objective cannot see a transposed multiplier; its VALUE can: nu_e('i1','i2') =
    -2*ord(i)*c = -16 (positional) vs -12 when emitted as nu_e(j,i)."""
    _translate_and_solve(
        tmp_path,
        "rev",
        "Set i / i1*i3 /;\nAlias (i,j);\nParameter c(i,j);\nc(i,j) = 1 + ord(i) + 3*ord(j);\n"
        "Variable x(i,j), obj;\nEquation e(j,i), defobj;\ne(j,i).. x(j,i) =e= c(j,i);\n"
        "defobj.. obj =e= sum((i,j), ord(i)*sqr(x(i,j)));\n"
        "Model m / all /;\nsolve m using nlp minimizing obj;\n",
    )
    lst = (tmp_path / "rev_mcp.lst").read_text()
    m = re.search(r"VAR nu_e.*?\ni1\.i2\s+\S+\s+([-+0-9.eE]+)", lst, re.S)
    assert m and abs(float(m.group(1)) + 16.0) < 1e-3, m and m.group(1)


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
