"""Integration test for multi-pattern Jacobian correction (Issue #1110).

Moved from tests/unit/ because this test shells out to the CLI via subprocess
and does filesystem I/O, which conflicts with the unit marker definition.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]


class TestMarkovMultiPatternIntegration:
    """Integration test using the markov GAMSlib model."""

    @pytest.fixture
    def markov_gms(self):
        """Path to markov.gms; skip if not available.

        Uses the real markov model because the multi-pattern Jacobian
        requires a constraint with both a direct VarRef and a summed
        VarRef to the same variable — a structure that's difficult to
        reproduce with an inline minimal fixture without also needing
        the full AD + KKT pipeline to generate the correct stat_z.
        Skipped in CI where raw GAMSlib files are absent.
        """
        path = os.path.join("data", "gamslib", "raw", "markov.gms")
        if not os.path.exists(path):
            pytest.skip("markov.gms not available (CI)")
        return path

    def test_markov_stationarity_has_correction_term(self, markov_gms):
        """stat_z should contain nu_constr(s,i) as a direct correction term.

        Before the fix, stat_z had:
            sum((s__kkt1,j), (1 - b*pi(...)) * nu_constr(s__kkt1,j))
        which incorrectly applied the +1 Kronecker delta to ALL pairings.

        After the fix, stat_z should have:
            sum((s__kkt1,j), (-b*pi(...)) * nu_constr(s__kkt1,j))
            + nu_constr(s,i)
        separating the diagonal correction from the off-diagonal sum.
        """
        with tempfile.NamedTemporaryFile(suffix=".gms", mode="w", delete=False) as f:
            output_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli", markov_gms, "-o", output_path],
                capture_output=True,
                text=True,
                timeout=120,
            )
            assert result.returncode == 0, f"CLI failed: {result.stderr}"

            with open(output_path) as f:
                content = f.read()
        finally:
            os.remove(output_path)

        # Find stat_z equation
        for line in content.splitlines():
            if line.startswith("stat_z("):
                stat_z = line
                break
        else:
            pytest.fail("stat_z equation not found in MCP output")

        # The correction term nu_constr(s,i) should appear as a direct
        # (non-summed) term, separate from the sum over (s__kkt1,j).
        assert (
            "nu_constr(s,i)" in stat_z
        ), f"Expected direct nu_constr(s,i) correction term in stat_z, got:\n{stat_z}"

        # The sum should use the off-diagonal derivative (no +1 Kronecker).
        # It should NOT contain "(1 - b * pi" inside the sum.
        sum_match = re.search(r"sum\([^)]+\),\s*(.+?)\s*\*\s*nu_constr\(s__kkt1", stat_z)
        assert (
            sum_match is not None
        ), f"Expected sum(...) * nu_constr(s__kkt1,...) pattern in stat_z, got:\n{stat_z}"
        sum_deriv = sum_match.group(1)
        assert (
            "1 -" not in sum_deriv and "1 +" not in sum_deriv
        ), f"Sum derivative should be pure off-diagonal (no Kronecker delta), got: {sum_deriv}"
