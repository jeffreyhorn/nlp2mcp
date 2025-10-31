"""Tests for GAMS syntax validation.

These tests validate that the GAMS validation module works correctly
and that all golden reference files have valid GAMS syntax.
"""

from pathlib import Path

import pytest

from src.validation.gams_check import (
    find_gams_executable,
    validate_gams_syntax,
    validate_gams_syntax_or_skip,
)


@pytest.fixture(autouse=True)
def cleanup_gams_files():
    """Clean up GAMS output files after each test."""
    yield
    # Clean up .lst and .log files in tests/golden directory
    golden_dir = Path("tests/golden")
    if golden_dir.exists():
        for pattern in ["*.lst", "*.log"]:
            for file in golden_dir.glob(pattern):
                try:
                    file.unlink()
                except OSError:
                    pass  # Ignore errors if file doesn't exist or can't be deleted


@pytest.mark.validation
class TestGAMSExecutableDetection:
    """Test GAMS executable detection."""

    def test_find_gams_executable(self):
        """Test that GAMS executable can be found."""
        gams_exe = find_gams_executable()
        # GAMS may or may not be installed - this just tests the function works
        assert gams_exe is None or Path(gams_exe).exists()


@pytest.mark.validation
class TestGAMSValidation:
    """Test GAMS syntax validation on golden files.

    All tests now pass after fixing GitHub issue #47 (Indexed Stationarity Equations).
    """

    def test_validate_simple_nlp_golden(self):
        """Test GAMS validation of simple_nlp_mcp.gms."""
        golden_file = Path("tests/golden/simple_nlp_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        error = validate_gams_syntax_or_skip(str(golden_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")

    def test_validate_bounds_nlp_golden(self):
        """Test GAMS validation of bounds_nlp_mcp.gms."""
        golden_file = Path("tests/golden/bounds_nlp_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        error = validate_gams_syntax_or_skip(str(golden_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")

    def test_validate_indexed_balance_golden(self):
        """Test GAMS validation of indexed_balance_mcp.gms."""
        golden_file = Path("tests/golden/indexed_balance_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        error = validate_gams_syntax_or_skip(str(golden_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")

    def test_validate_nonlinear_mix_golden(self):
        """Test GAMS validation of nonlinear_mix_mcp.gms."""
        golden_file = Path("tests/golden/nonlinear_mix_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        error = validate_gams_syntax_or_skip(str(golden_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")

    def test_validate_scalar_nlp_golden(self):
        """Test GAMS validation of scalar_nlp_mcp.gms."""
        golden_file = Path("tests/golden/scalar_nlp_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        error = validate_gams_syntax_or_skip(str(golden_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")


@pytest.mark.validation
class TestGAMSValidationErrors:
    """Test GAMS validation error handling."""

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            validate_gams_syntax("nonexistent.gms")

    def test_validate_with_explicit_gams_path(self):
        """Test validation with explicit GAMS executable path."""
        golden_file = Path("tests/golden/scalar_nlp_mcp.gms")
        if not golden_file.exists():
            pytest.skip("Golden file not found")

        # Find GAMS first
        gams_exe = find_gams_executable()
        if gams_exe is None:
            pytest.skip("GAMS not available")

        # Validate with explicit path
        success, message = validate_gams_syntax(str(golden_file), gams_exe)
        assert success, f"Validation should succeed: {message}"
        assert message == "GAMS syntax valid"
