"""Tests for Issue #1134: boundary-row filtering in lag-indexed equations.

When a lag-indexed equation like v_eqn(h-1) creates a Jacobian row for the
boundary instance (h0), that row may have dense derivatives against all
variable instances, producing many singleton offset groups.  The filter in
_filter_boundary_singleton_offset_groups() should discard these boundary
artifacts while preserving legitimate structural offsets.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from src.cli import main
from src.kkt.stationarity import _filter_boundary_singleton_offset_groups

pytestmark = pytest.mark.integration


class TestBoundaryOffsetFilter:
    """Test _filter_boundary_singleton_offset_groups() directly."""

    def test_filter_removes_same_row_singletons(self):
        """Many singleton groups from the same row should be filtered."""
        offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
        offset_groups[(0,)] = [(r, r) for r in range(1, 51)]
        offset_groups[(1,)] = [(r, r + 1) for r in range(1, 50)]
        for k in range(1, 51):
            offset_groups[(-k,)] = [(0, k)]  # all from row 0

        assert len(offset_groups) == 52

        filtered = _filter_boundary_singleton_offset_groups(offset_groups)

        assert len(filtered) == 2
        assert (0,) in filtered
        assert (1,) in filtered

    def test_filter_preserves_singletons_from_distinct_rows(self):
        """Singleton groups from different rows should NOT be filtered."""
        offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
        offset_groups[(0,)] = [(r, r) for r in range(10)]
        offset_groups[(1,)] = [(r, r + 1) for r in range(9)]
        offset_groups[(-1,)] = [(5, 4)]  # singleton from row 5
        offset_groups[(-2,)] = [(7, 5)]  # singleton from row 7

        filtered = _filter_boundary_singleton_offset_groups(offset_groups)

        # Singletons from different rows — all preserved
        assert len(filtered) == 4

    def test_filter_noop_when_two_or_fewer_groups(self):
        """With ≤2 groups, filter is a no-op."""
        offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {
            (0,): [(1, 1), (2, 2)],
            (1,): [(0, 1)],
        }
        filtered = _filter_boundary_singleton_offset_groups(offset_groups)
        assert filtered is offset_groups  # same object, untouched


@pytest.mark.slow
class TestRocketLagBoundaryFilter:
    """End-to-end: rocket stationarity should be sparse (requires raw model)."""

    @pytest.fixture
    def rocket_mcp_content(self, tmp_path):
        rocket_gms = Path("data/gamslib/raw/rocket.gms")
        if not rocket_gms.exists():
            pytest.skip("data/gamslib/raw/rocket.gms not available")
        output_file = tmp_path / "rocket_mcp.gms"
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                str(rocket_gms),
                "-o",
                str(output_file),
                "--quiet",
                "--skip-convexity-check",
            ],
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        return output_file.read_text(encoding="utf-8")

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
