"""
Production hardening tests for large models.

Tests that nlp2mcp can handle realistic large-scale problems.
"""

import subprocess
import time
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "large_models"


class TestLargeModelHandling:
    """Test nlp2mcp handles large models correctly."""

    @pytest.mark.slow
    def test_250_model_converts(self, tmp_path):
        """Test: 250-variable model converts successfully."""
        model = FIXTURES_DIR / "resource_allocation_250.gms"
        output = tmp_path / "test_250_mcp.gms"

        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0

    @pytest.mark.slow
    def test_500_model_converts(self, tmp_path):
        """Test: 500-variable model converts in reasonable time."""
        model = FIXTURES_DIR / "resource_allocation_500.gms"
        output = tmp_path / "test_500_mcp.gms"

        start = time.time()
        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=90,
        )
        elapsed = time.time() - start

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0
        assert elapsed < 90, f"Conversion too slow: {elapsed:.1f}s"
        print(f"\n500-variable model: {elapsed:.2f}s conversion time")

    @pytest.mark.slow
    def test_1k_model_converts(self, tmp_path):
        """Test: 1K-variable model converts in reasonable time."""
        model = FIXTURES_DIR / "resource_allocation_1k.gms"
        output = tmp_path / "test_1k_mcp.gms"

        start = time.time()
        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        elapsed = time.time() - start

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0
        assert elapsed < 120, f"Conversion too slow: {elapsed:.1f}s"
        print(f"\n1K-variable model: {elapsed:.2f}s conversion time")

    @pytest.mark.slow
    def test_1k_model_output_quality(self, tmp_path):
        """Test: 1K-variable model produces valid MCP output."""
        model = FIXTURES_DIR / "resource_allocation_1k.gms"
        output = tmp_path / "test_1k_quality_mcp.gms"

        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        assert result.returncode == 0

        # Read output and check for expected MCP structures
        content = output.read_text()

        # Should have KKT conditions
        assert "Stationarity" in content or "stationarity" in content
        assert "Complementarity" in content or "complementarity" in content

        # Should have multiplier variables
        assert "lam_" in content or "lambda" in content

        # Should solve using MCP
        assert "MCP" in content or "mcp" in content

        print(f"\n1K-variable model: {len(content)} bytes of MCP output")
