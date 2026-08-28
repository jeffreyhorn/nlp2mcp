"""Tests for GAMS syntax validation.

These tests validate that the GAMS validation module works correctly
and that all golden reference files have valid GAMS syntax.
"""

import shutil
from pathlib import Path

import pytest

from src.validation.gams_check import (
    find_gams_executable,
    validate_gams_syntax,
    validate_gams_syntax_or_skip,
)


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

    def test_validate_simple_nlp_golden(self, tmp_path):
        """Test GAMS validation of simple_nlp_mcp.gms.

        Validated on a COPY. `validate_gams_syntax` runs GAMS with
        ``cwd=<file>.parent`` and reads ``<stem>.lst`` back from there, so
        pointing it at `tests/golden/` makes every xdist worker write and read
        build artifacts in one shared directory.
        """
        golden_file = Path("tests/golden/simple_nlp_mcp.gms")
        assert golden_file.exists(), f"Golden file not found: {golden_file}"

        test_file = tmp_path / golden_file.name
        shutil.copy(golden_file, test_file)

        error = validate_gams_syntax_or_skip(str(test_file))
        if error:
            pytest.fail(f"GAMS validation failed: {error}")


@pytest.mark.validation
class TestGAMSValidationErrors:
    """Test GAMS validation error handling."""

    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            validate_gams_syntax("nonexistent.gms")

    def test_validate_with_explicit_gams_path(self, tmp_path):
        """Test validation with explicit GAMS executable path."""
        golden_file = Path("tests/golden/scalar_nlp_mcp.gms")
        if not golden_file.exists():
            pytest.skip("Golden file not found")

        # Find GAMS first
        gams_exe = find_gams_executable()
        if gams_exe is None:
            pytest.skip("GAMS not available")

        # Copy golden file to tmp_path for isolation in parallel execution
        test_file = tmp_path / golden_file.name
        shutil.copy(golden_file, test_file)

        # Validate with explicit path
        success, message = validate_gams_syntax(str(test_file), gams_exe)
        assert success, f"Validation should succeed: {message}"
        assert message == "GAMS syntax valid"
