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

Two test layers:

1. **Subprocess on real gamslib**: ``@pytest.mark.slow`` — skipped in
   fast CI and skipped altogether when ``data/gamslib/raw/`` is absent
   (CI checkouts don't ship the raw corpus).
2. **In-process CliRunner on synthetic fixtures**: always runs in fast
   CI; exercises the full CLI wiring (option parsing, exit code, error
   message, ``--allow-multi-solve`` bypass) without depending on the
   gamslib corpus. Addresses the review concern that the subprocess
   tests skip by default and so never exercise the gate in CI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from click.testing import CliRunner

from src.cli import EXIT_MULTI_SOLVE_OUT_OF_SCOPE, main

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW = PROJECT_ROOT / "data" / "gamslib" / "raw"

# ---------------------------------------------------------------------------
# Synthetic fixtures — minimal GAMS sources that exercise the gate without
# needing the (uncommitted) gamslib raw corpus.
# ---------------------------------------------------------------------------

SYNTHETIC_DRIVER_GMS = dedent("""\
    * Minimal Dantzig-Wolfe-style driver pattern: 2 declared models,
    * 2 distinct solve targets in a loop that reads an equation dual
    * (bal.m) between solves. MUST be refused by the multi-solve gate.
    Variables x, z1, z2;
    Positive Variables x;
    Equations eq1, eq2, bal;
    eq1.. z1 =e= x;
    eq2.. z2 =e= x;
    bal.. x =l= 1;

    Model sub / eq1, bal /;
    Model master / eq2, bal /;

    Scalar price /0/;
    Set t /t1, t2/;
    Loop(t,
        price = -bal.m;
        Solve sub using NLP minimizing z1;
        Solve master using NLP minimizing z2;
    );
    """)

SYNTHETIC_SINGLE_MODEL_MULTI_SOLVE_GMS = dedent("""\
    * ibm1-style regression fixture: one declared model, repeated
    * solves on the same model. MUST NOT be flagged as a driver.
    Sets i /i1, i2, i3/;
    Parameters a(i) /i1 1, i2 2, i3 3/;
    Variables x(i), obj;
    Equations objective, balance(i);
    objective.. obj =e= sum(i, a(i) * x(i));
    balance(i).. x(i) =g= 0;

    Model alloy / all /;
    Set t /t1, t2/;
    Loop(t,
        Solve alloy using NLP minimizing obj;
        Solve alloy using NLP minimizing obj;
    );
    """)


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


# ---------------------------------------------------------------------------
# Synthetic-fixture CLI tests — run in fast CI; don't depend on gamslib raw.
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_cli_refuses_synthetic_driver_exit_code_4(tmp_path):
    """CliRunner invocation on an inline synthetic driver fixture. The
    gate must fire, exit 4, and the error must name both declared models
    and the equation-marginal symbol. Runs in fast CI (no gamslib raw).
    """
    src = tmp_path / "synthetic_driver.gms"
    src.write_text(SYNTHETIC_DRIVER_GMS)
    out = tmp_path / "synthetic_driver_mcp.gms"

    result = CliRunner().invoke(
        main,
        [str(src), "-o", str(out), "--quiet"],
    )

    assert result.exit_code == EXIT_MULTI_SOLVE_OUT_OF_SCOPE, (
        f"Expected exit {EXIT_MULTI_SOLVE_OUT_OF_SCOPE}, got {result.exit_code}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    stderr = result.stderr.lower()
    assert "multi-solve driver" in stderr
    assert "sub" in stderr and "master" in stderr
    assert "bal.m" in stderr
    assert not out.exists(), "gate let the output file slip through"


@pytest.mark.integration
def test_cli_allow_multi_solve_bypasses_synthetic_driver(tmp_path):
    """``--allow-multi-solve`` must downgrade the refusal to a stderr
    warning. The translator may still fail downstream on a hand-rolled
    fixture, but the gate itself must emit its bypass warning — that's
    the specific wiring this test pins.
    """
    src = tmp_path / "synthetic_driver.gms"
    src.write_text(SYNTHETIC_DRIVER_GMS)
    out = tmp_path / "synthetic_driver_mcp.gms"

    result = CliRunner().invoke(
        main,
        [str(src), "--allow-multi-solve", "-o", str(out), "--quiet"],
    )

    # Regardless of downstream translation outcome, the gate's bypass
    # warning must have been emitted and the exit code must NOT be 4.
    assert result.exit_code != EXIT_MULTI_SOLVE_OUT_OF_SCOPE, (
        "--allow-multi-solve still tripped the gate; "
        f"exit={result.exit_code}, stderr={result.stderr}"
    )
    assert "bypassing multi-solve-driver gate" in result.stderr.lower()


@pytest.mark.integration
def test_cli_does_not_flag_synthetic_single_model_multi_solve(tmp_path):
    """Single-model multi-solve (ibm1 pattern) must NOT trip the gate.
    The CLI may succeed or fail downstream for other reasons; what we're
    asserting is ONLY that exit 4 is not produced and that no
    multi-solve-driver message appears in stderr.
    """
    src = tmp_path / "synthetic_single_model.gms"
    src.write_text(SYNTHETIC_SINGLE_MODEL_MULTI_SOLVE_GMS)
    out = tmp_path / "synthetic_single_model_mcp.gms"

    result = CliRunner().invoke(
        main,
        [str(src), "-o", str(out), "--quiet"],
    )

    assert result.exit_code != EXIT_MULTI_SOLVE_OUT_OF_SCOPE, (
        f"single-model multi-solve was wrongly flagged as a driver; "
        f"exit={result.exit_code}, stderr={result.stderr}"
    )
    assert "multi-solve driver" not in result.stderr.lower()


# ---------------------------------------------------------------------------
# Subprocess-on-real-gamslib tests — slow; skipped when raw corpus absent.
# ---------------------------------------------------------------------------


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
