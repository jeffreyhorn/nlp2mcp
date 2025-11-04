"""PATH solver validation tests for min/max reformulations.

These tests verify that MCP models with min/max reformulations can be
solved successfully with the PATH solver.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest


def find_gams_executable():
    """Find GAMS executable in common locations."""
    if sys.platform == "darwin":  # macOS
        common_paths = [
            "/Applications/GAMS/gams",
            "/Library/Frameworks/GAMS.framework/Versions/Current/Resources/gams",
            "/usr/local/bin/gams",
        ]
    elif sys.platform == "win32":
        common_paths = [
            r"C:\GAMS\win64\gams.exe",
            r"C:\Program Files\GAMS\gams.exe",
        ]
    else:  # Linux
        common_paths = [
            "/opt/gams/gams",
            "/usr/local/bin/gams",
            "/usr/bin/gams",
        ]

    for path_str in common_paths:
        path = Path(path_str)
        if path.exists():
            return path

    # Try finding in PATH
    try:
        result = subprocess.run(
            ["which", "gams"] if sys.platform != "win32" else ["where", "gams"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip().split("\n")[0])
    except Exception:
        # Ignore exceptions when searching for GAMS in PATH; not all systems will have it installed.
        pass

    return None


def _solve_gams(gams_file: Path, gams_exe: Path) -> tuple[bool, str, dict]:
    """
    Solve a GAMS MCP model with PATH solver.

    Returns:
        (success, message, solution)
        - success: True if solve succeeded
        - message: Error or status message
        - solution: Dict of variable values
    """
    # Run GAMS
    subprocess.run(
        [str(gams_exe), str(gams_file), "lo=3"],
        capture_output=True,
        text=True,
        cwd=gams_file.parent,
        check=False,
    )

    # Parse listing file
    lst_file = gams_file.parent / (gams_file.stem + ".lst")
    if not lst_file.exists():
        return False, "No listing file generated", {}

    lst_content = lst_file.read_text()

    # Check model status
    model_status_match = re.search(r"\*\*\*\* MODEL STATUS\s+(\d+)", lst_content)
    if not model_status_match:
        return False, "Could not find MODEL STATUS in listing file", {}

    model_status = int(model_status_match.group(1))

    # Model Status codes:
    # 1 = Optimal
    # 2 = Locally Optimal
    # 3 = Unbounded
    # 4 = Infeasible
    # 5 = Locally Infeasible
    # ...

    if model_status in (1, 2):
        # Extract solution values
        solution = {}
        # Look for variable levels in solution report
        in_solution = False
        for line in lst_content.split("\n"):
            if "VARIABLE" in line and ".L" in line:
                in_solution = True
            if in_solution and "." in line:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        var_name = parts[0]
                        value = float(parts[1])
                        solution[var_name] = value
                    except (ValueError, IndexError):
                        continue

        return True, f"Model Status {model_status}: Optimal", solution
    else:
        return False, f"Model Status {model_status}: Not optimal", {}


def _check_kkt_residuals(lst_content: str, tolerance: float = 1e-4) -> tuple[bool, str]:
    """
    Check KKT residuals from PATH solver output.

    Returns:
        (kkt_ok, message)
    """
    # Look for PATH final statistics
    residual_match = re.search(r"Inf-Norm of Complementarity\s+\.\s+\.\s+([\d.e+-]+)", lst_content)
    if residual_match:
        residual = float(residual_match.group(1))
        if residual > tolerance:
            return False, f"Complementarity residual {residual:.2e} exceeds {tolerance}"

    # Look for PATH exit status
    if "EXIT - solution found" in lst_content:
        return True, "PATH found solution"
    elif "EXIT - other error" in lst_content:
        return False, "PATH exited with error"

    return True, "KKT conditions appear satisfied"


@pytest.mark.validation
@pytest.mark.skipif(
    find_gams_executable() is None,
    reason="GAMS executable not found - skipping PATH solver validation",
)
class TestPathSolverMinMax:
    """Validation tests for PATH solver on min/max reformulations."""

    @pytest.mark.xfail(
        reason="Min/max reformulation bug: spurious lambda variables cause infeasibility "
        "(see docs/issues/minmax-reformulation-spurious-variables.md)",
        strict=True,
    )
    def test_solve_min_max_test_mcp(self):
        """Test PATH solver on min_max_test_mcp.gms.

        Model: Minimize z where z = min(x, y)
        Bounds: x >= 1, y >= 2

        Expected solution: z = x = 1 (x is the minimum)

        **KNOWN BUG:** Currently fails with PATH Model Status 5 (Locally Infeasible)
        due to spurious lambda variables in reformulation. See investigation doc.
        """
        golden_file = Path("tests/golden/min_max_test_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        gams_exe = find_gams_executable()
        assert gams_exe is not None, "GAMS executable not found"

        # Solve the MCP
        success, message, solution = _solve_gams(golden_file, gams_exe)
        assert success, f"PATH solve failed: {message}"

        # Verify we got a solution
        assert len(solution) > 0, "No solution values extracted"

        # Check expected solution values (with tolerance)
        tol = 1e-3
        if "z" in solution:
            # z should be the minimum of x and y
            # With x.lo=1 and y.lo=2, minimum should be 1
            assert abs(solution["z"] - 1.0) < tol, f"Expected z=1, got z={solution['z']}"

        if "x" in solution:
            # x should be at its lower bound
            assert abs(solution["x"] - 1.0) < tol, f"Expected x=1, got x={solution['x']}"

        if "y" in solution:
            # y should be at its lower bound
            assert abs(solution["y"] - 2.0) < tol, f"Expected y=2, got y={solution['y']}"

        # Check KKT conditions
        lst_file = golden_file.parent / (golden_file.stem + ".lst")
        lst_content = lst_file.read_text()
        kkt_ok, kkt_msg = _check_kkt_residuals(lst_content)
        assert kkt_ok, f"KKT conditions not satisfied: {kkt_msg}"


@pytest.mark.validation
def test_min_max_mcp_generation():
    """Test that min/max examples can be converted to MCP.

    This test doesn't require GAMS - just verifies generation works.
    """
    golden_file = Path("tests/golden/min_max_test_mcp.gms")
    assert golden_file.exists(), "min_max_test_mcp.gms should exist"

    content = golden_file.read_text()

    # Check for auxiliary variable
    assert "aux_min_min_constraint_0" in content, "Should have auxiliary variable"

    # Check for complementarity conditions (new naming: comp_minmax_min_*)
    assert "comp_minmax_min_min_constraint_0_arg0" in content, "Should have comp for arg0"
    assert "comp_minmax_min_min_constraint_0_arg1" in content, "Should have comp for arg1"

    # Check for lambda variables (new naming: lam_minmax_min_*)
    assert "lam_minmax_min_min_constraint_0_arg0" in content, "Should have lambda for arg0"
    assert "lam_minmax_min_min_constraint_0_arg1" in content, "Should have lambda for arg1"

    # Verify structure is correct
    assert "Model mcp_model" in content, "Should have MCP model declaration"
    assert "Solve mcp_model using MCP" in content, "Should have solve statement"
