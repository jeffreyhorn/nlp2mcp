"""
End-to-end integration tests for convexity warning system.

Tests the full pipeline: GAMS → parse → convexity check → warning output.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Mark all tests in this module as slow (CLI subprocess overhead)
pytestmark = pytest.mark.slow


@pytest.fixture
def fixtures_dir():
    """Path to convexity test fixtures."""
    return Path(__file__).parent.parent / "fixtures" / "convexity"


def test_cli_convexity_warnings_nonconvex_circle(fixtures_dir, tmp_path):
    """Test CLI shows convexity warnings for nonconvex circle model."""
    input_file = fixtures_dir / "nonconvex_circle.gms"
    output_file = tmp_path / "output.gms"

    # Run CLI
    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0, f"CLI failed: {result.stderr}"

    # Should contain convexity warning
    assert "Convexity Warnings" in result.stdout or "W301" in result.stdout
    assert "Nonlinear equality" in result.stdout or "nonlinear_equality" in result.stdout

    # Should mention documentation
    assert "Docs:" in result.stdout or "docs/errors" in result.stdout


def test_cli_skip_convexity_check(fixtures_dir, tmp_path):
    """Test --skip-convexity-check suppresses warnings."""
    input_file = fixtures_dir / "nonconvex_circle.gms"
    output_file = tmp_path / "output.gms"

    # Run CLI with --skip-convexity-check
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(input_file),
            "-o",
            str(output_file),
            "--skip-convexity-check",
            "-v",
        ],
        capture_output=True,
        text=True,
    )

    # Should succeed
    assert result.returncode == 0

    # Should NOT contain convexity warnings
    assert "Convexity Warnings" not in result.stdout
    assert "W301" not in result.stdout


def test_cli_convexity_trig_warnings(fixtures_dir, tmp_path):
    """Test CLI detects trigonometric functions."""
    input_file = fixtures_dir / "nonconvex_trig.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Should detect W302 (trigonometric)
    assert "W302" in result.stdout or "Trigonometric" in result.stdout


def test_cli_convexity_bilinear_warnings(fixtures_dir, tmp_path):
    """Test CLI detects bilinear terms."""
    input_file = fixtures_dir / "nonconvex_bilinear.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Should detect W303 (bilinear)
    assert "W303" in result.stdout or "Bilinear" in result.stdout


def test_cli_convexity_quotient_warnings(fixtures_dir, tmp_path):
    """Test CLI detects variable quotients."""
    input_file = fixtures_dir / "nonconvex_quotient.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Should detect W304 (quotient)
    assert "W304" in result.stdout or "quotient" in result.stdout


def test_cli_convexity_odd_power_warnings(fixtures_dir, tmp_path):
    """Test CLI detects odd powers."""
    input_file = fixtures_dir / "nonconvex_odd_power.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Should detect W305 (odd power)
    assert "W305" in result.stdout or "Odd power" in result.stdout


def test_cli_convexity_multiple_warnings(fixtures_dir, tmp_path):
    """Test CLI shows multiple warnings for complex model."""
    input_file = fixtures_dir / "nonconvex_trig.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # nonconvex_trig.gms should trigger multiple patterns
    # (at least trig and possibly nonlinear equality)
    stdout = result.stdout

    # Count warning patterns
    has_warnings = "Convexity Warnings" in stdout or any(f"W30{i}" in stdout for i in range(1, 6))
    assert has_warnings, "Expected at least one convexity warning"


def test_cli_output_format_with_warnings(fixtures_dir, tmp_path):
    """Test warning format includes equation names and doc links."""
    input_file = fixtures_dir / "nonconvex_circle.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    stdout = result.stdout

    # Should include structured information
    assert "Equation:" in stdout  # Equation name should be shown
    assert "Docs:" in stdout  # Documentation link should be shown

    # Should have helpful text
    assert "heuristic" in stdout or "false positive" in stdout


def test_cli_convexity_does_not_block_conversion(fixtures_dir, tmp_path):
    """Test that convexity warnings don't prevent model conversion."""
    input_file = fixtures_dir / "nonconvex_circle.gms"
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    # Should succeed despite warnings
    assert result.returncode == 0

    # Output file should be created
    assert output_file.exists()

    # Output should contain MCP model
    output_content = output_file.read_text()
    assert "Model" in output_content or "Equation" in output_content


@pytest.mark.parametrize(
    "fixture_name,expected_code",
    [
        ("nonconvex_circle.gms", "W301"),  # Nonlinear equality
        ("nonconvex_trig.gms", "W302"),  # Trigonometric
        ("nonconvex_bilinear.gms", "W303"),  # Bilinear
        ("nonconvex_quotient.gms", "W304"),  # Quotient
        ("nonconvex_odd_power.gms", "W305"),  # Odd power
    ],
)
def test_cli_specific_error_codes(fixtures_dir, tmp_path, fixture_name, expected_code):
    """Test each fixture generates its expected error code."""
    input_file = fixtures_dir / fixture_name
    output_file = tmp_path / "output.gms"

    result = subprocess.run(
        [sys.executable, "-m", "src.cli", str(input_file), "-o", str(output_file), "-v"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert expected_code in result.stdout, f"Expected {expected_code} in output for {fixture_name}"
