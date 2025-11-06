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

    def test_small_model_converts(self):
        """Test: 10-variable model converts successfully."""
        model = FIXTURES_DIR / "resource_allocation_small.gms"
        output = Path("/tmp/test_small_mcp.gms")

        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0

    def test_medium_model_converts(self):
        """Test: 50-variable model converts successfully."""
        model = FIXTURES_DIR / "resource_allocation_medium.gms"
        output = Path("/tmp/test_medium_mcp.gms")

        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0

    @pytest.mark.slow
    def test_large_model_converts(self):
        """Test: 100-variable model converts in reasonable time."""
        model = FIXTURES_DIR / "resource_allocation_large.gms"
        output = Path("/tmp/test_large_mcp.gms")

        start = time.time()
        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        elapsed = time.time() - start

        assert result.returncode == 0, f"Conversion failed: {result.stderr}"
        assert output.exists()
        assert output.stat().st_size > 0
        assert elapsed < 30, f"Conversion too slow: {elapsed:.1f}s"
        print(f"\n100-variable model: {elapsed:.2f}s conversion time")

    @pytest.mark.slow
    def test_large_model_output_quality(self):
        """Test: 100-variable model produces valid MCP output."""
        model = FIXTURES_DIR / "resource_allocation_large.gms"
        output = Path("/tmp/test_large_quality_mcp.gms")

        result = subprocess.run(
            ["nlp2mcp", str(model), "-o", str(output)],
            capture_output=True,
            text=True,
            timeout=60,
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

        print(f"\n100-variable model: {len(content)} bytes of MCP output")
