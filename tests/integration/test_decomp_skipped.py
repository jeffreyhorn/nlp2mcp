"""End-to-end CLI regression test for the multi-solve-driver gate.

PLAN_FIX_DECOMP: direct ``python -m src.cli data/gamslib/raw/decomp.gms``
must refuse to emit an MCP and exit with ``EXIT_MULTI_SOLVE_OUT_OF_SCOPE``
(exit code 4), printing a clear message that names both declared
models (``sub``, ``master``) and at least one equation-marginal
reference (``tbal.m``).

The critical regression guards:

- ``ibm1`` (single declared model, 5 repeated solves) must NOT be
  flagged. A separate unit in :mod:`tests.unit.validation.test_driver`
  covers the detector in isolation; this file spot-checks via the CLI
  so a missed wiring (e.g., forgetting to raise on the subprocess
  path) shows up here too.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW = PROJECT_ROOT / "data" / "gamslib" / "raw"

# Keep in sync with src/cli.py.
EXIT_MULTI_SOLVE_OUT_OF_SCOPE = 4


@pytest.mark.integration
@pytest.mark.slow
def test_cli_refuses_decomp_with_exit_code_4(tmp_path):
    """decomp is a Dantzig–Wolfe driver. CLI must refuse, exit 4."""
    src = RAW / "decomp.gms"
    if not src.exists():
        pytest.skip("decomp.gms not present (CI without gamslib raw)")

    out = tmp_path / "decomp_mcp.gms"
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(out)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_ROOT,
    )
    assert proc.returncode == EXIT_MULTI_SOLVE_OUT_OF_SCOPE, (
        f"Expected exit {EXIT_MULTI_SOLVE_OUT_OF_SCOPE}, got {proc.returncode}.\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    # Message must identify it as a multi-solve driver and name the
    # declared models + the dual-feedback symbol.
    stderr = proc.stderr.lower()
    assert "multi-solve driver" in stderr
    assert "sub" in stderr and "master" in stderr
    assert "tbal.m" in stderr
    # No MCP file should have been written.
    assert not out.exists(), "gate let the output file slip through"


@pytest.mark.integration
@pytest.mark.slow
def test_cli_allow_multi_solve_bypasses_gate(tmp_path):
    """``--allow-multi-solve`` must downgrade the refusal to a warning
    and still produce an output file (for development/debugging). The
    generated file is not expected to be solvable, but the bypass flag
    must work or we break our only escape hatch.
    """
    src = RAW / "decomp.gms"
    if not src.exists():
        pytest.skip("decomp.gms not present (CI without gamslib raw)")

    out = tmp_path / "decomp_mcp.gms"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(src),
            "--allow-multi-solve",
            "-o",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_ROOT,
    )
    assert proc.returncode == 0, (
        f"--allow-multi-solve should succeed; got {proc.returncode}.\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    assert "bypassing multi-solve-driver gate" in proc.stderr.lower()
    assert out.exists(), "translator did not emit an output file under --allow-multi-solve"


@pytest.mark.integration
@pytest.mark.slow
def test_cli_does_not_flag_ibm1(tmp_path):
    """ibm1 regression guard: single declared model, 5 solves. The
    detector must not trigger, the CLI must translate normally.
    """
    src = RAW / "ibm1.gms"
    if not src.exists():
        pytest.skip("ibm1.gms not present (CI without gamslib raw)")

    out = tmp_path / "ibm1_mcp.gms"
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(src), "-o", str(out)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=PROJECT_ROOT,
    )
    assert proc.returncode == 0, (
        f"ibm1 must not trigger the multi-solve gate; got exit {proc.returncode}.\n"
        f"stderr: {proc.stderr}"
    )
    assert "multi-solve driver" not in proc.stderr.lower()
    assert out.exists()
