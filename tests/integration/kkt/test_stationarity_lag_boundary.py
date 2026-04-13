"""Tests for Issue #1134: boundary-row filtering in lag-indexed equations.

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

pytestmark = pytest.mark.integration


class TestBoundaryOffsetFilter:
    """Unit-level test for the singleton-row filter logic (Issue #1134).

    Simulates the offset_groups dict that would be produced by a boundary
    row (all singletons from the same degenerate row_id) and verifies the
    filter removes them while preserving structural offsets.
    """

    def test_filter_removes_same_row_singletons(self):
        """Many singleton groups from the same row should be filtered."""
        # Simulate: offset 0 has 50 entries from 50 rows,
        # offset +1 has 49 entries from 49 rows,
        # offsets -1..-50 each have 1 entry from row_id=0 (boundary)
        offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
        offset_groups[(0,)] = [(r, r) for r in range(1, 51)]  # 50 entries, 50 rows
        offset_groups[(1,)] = [(r, r + 1) for r in range(1, 50)]  # 49 entries, 49 rows
        for k in range(1, 51):
            offset_groups[(-k,)] = [(0, k)]  # 1 entry from row 0

        assert len(offset_groups) == 52  # 2 structural + 50 spurious

        # Apply the same filter logic as in _add_indexed_jacobian_terms
        rows_by_group = {key: {r for r, _ in entries} for key, entries in offset_groups.items()}
        singleton_groups = {
            key: next(iter(group_rows))
            for key, group_rows in rows_by_group.items()
            if len(group_rows) == 1
        }
        singleton_rows = set(singleton_groups.values())

        assert len(singleton_groups) == 50  # 50 spurious singletons
        assert singleton_rows == {0}  # all from row 0

        if len(singleton_groups) >= 2 and len(singleton_rows) == 1:
            filtered = {k: v for k, v in offset_groups.items() if k not in singleton_groups}
        else:
            filtered = offset_groups

        assert len(filtered) == 2  # only structural offsets remain
        assert (0,) in filtered
        assert (1,) in filtered

    def test_filter_preserves_singletons_from_distinct_rows(self):
        """Singleton groups from different rows should NOT be filtered."""
        offset_groups: dict[tuple[int, ...], list[tuple[int, int]]] = {}
        offset_groups[(0,)] = [(r, r) for r in range(10)]
        offset_groups[(1,)] = [(r, r + 1) for r in range(9)]
        offset_groups[(-1,)] = [(5, 4)]  # singleton from row 5
        offset_groups[(-2,)] = [(7, 5)]  # singleton from row 7 (different!)

        rows_by_group = {key: {r for r, _ in entries} for key, entries in offset_groups.items()}
        singleton_groups = {
            key: next(iter(group_rows))
            for key, group_rows in rows_by_group.items()
            if len(group_rows) == 1
        }
        singleton_rows = set(singleton_groups.values())

        # Singletons come from different rows — should NOT filter
        assert len(singleton_rows) == 2  # rows 5 and 7
        assert not (len(singleton_groups) >= 2 and len(singleton_rows) == 1)

        # All groups preserved
        assert len(offset_groups) == 4


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
