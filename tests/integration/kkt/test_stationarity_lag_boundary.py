"""Integration tests for Issue #1134: boundary-row filtering in lag-indexed equations.

When a lag-indexed equation like v_eqn(h-1) creates a Jacobian row for the
boundary instance (h0), that row may have dense derivatives against all
variable instances, producing many singleton offset groups.  The filter in
_add_indexed_jacobian_terms() should discard these boundary artifacts while
preserving legitimate structural offsets.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.fixture
def rocket_mcp_content(tmp_path):
    """Translate rocket.gms and return the generated MCP content."""
    rocket_gms = Path("data/gamslib/raw/rocket.gms")
    if not rocket_gms.exists():
        pytest.skip("data/gamslib/raw/rocket.gms not available")

    output_file = tmp_path / "rocket_mcp.gms"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [str(rocket_gms), "-o", str(output_file), "--quiet", "--skip-convexity-check"],
    )
    assert result.exit_code == 0, f"CLI failed: {result.output}"
    return output_file.read_text(encoding="utf-8")


class TestRocketLagBoundaryFilter:
    """rocket stationarity should be sparse after the #1134 fix."""

    def test_stat_g_has_sparse_nu_v_eqn_terms(self, rocket_mcp_content):
        """stat_g(h) should have 2-3 nu_v_eqn terms, not 52."""
        for line in rocket_mcp_content.splitlines():
            if line.startswith("stat_g(h).."):
                count = line.count("nu_v_eqn")
                assert count <= 3, (
                    f"stat_g(h) has {count} nu_v_eqn terms (expected ≤3). "
                    f"Boundary offset filter may not be working."
                )
                assert count >= 2, (
                    f"stat_g(h) has {count} nu_v_eqn terms (expected ≥2). "
                    f"Structural offsets may have been incorrectly filtered."
                )
                return
        pytest.fail("stat_g(h) equation not found in output")

    def test_stat_d_has_sparse_nu_v_eqn_terms(self, rocket_mcp_content):
        """stat_d(h) should have 2-3 nu_v_eqn terms, not 52."""
        for line in rocket_mcp_content.splitlines():
            if line.startswith("stat_d(h).."):
                count = line.count("nu_v_eqn")
                assert count <= 3, f"stat_d(h) has {count} nu_v_eqn terms (expected ≤3)"
                assert count >= 2, f"stat_d(h) has {count} nu_v_eqn terms (expected ≥2)"
                return
        pytest.fail("stat_d(h) equation not found in output")
