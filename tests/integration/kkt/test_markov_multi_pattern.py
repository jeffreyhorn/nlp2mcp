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

# This test ran in NO CI lane for months, which is why it stayed red unnoticed:
# ci.yml excludes `slow` in both its branches, and nightly.yml's determinism
# sweep is PATH-SCOPED to tests/integration/test_pipeline_determinism.py, so
# markers alone cannot route anything into it. nightly.yml now carries an
# explicit step for this file (see "Run markov σ=sp end-to-end backstop").
# The `determinism` marker is deliberately NOT used: it is registered for
# byte-stability-across-PYTHONHASHSEED tests, which this is not.
# The fast in-process guard is
# tests/unit/kkt/test_shape_markov_diagonal_kronecker.py; this is the
# end-to-end backstop.
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

        # Sharpened to the σ=sp target form (Sprint 37 Day 3). The previous
        # assertions expected a `sum(...) * nu_constr(s__kkt1,...)` shape, which
        # was the *partially* corrected emit: it still carried one spurious
        # offset group per set element. The landed fix collapses those entirely,
        # so asserting on `s__kkt1` would now be asserting on the bug.

        # 1. The Kronecker diagonal is a bare additive term, not summed over
        #    indices it does not depend on.
        assert re.search(
            r"\+ nu_constr\(s,i\)(?!\))", stat_z
        ), f"Expected a bare additive nu_constr(s,i) diagonal in stat_z, got:\n{stat_z}"

        # 2. The off-diagonal collapses to a single sum over j, at the σ=sp
        #    slice, with the coupling parameter carrying the variable's own
        #    third index at both positions 2 and 4.
        assert re.search(
            r"sum\(j,[^;]*pi\(s,i,sp,j,sp\)[^;]*nu_constr\(sp,j\)", stat_z
        ), f"Expected the collapsed σ=sp off-diagonal sum in stat_z, got:\n{stat_z}"

        # 3. No spurious offset groups remain (45 before the fix, 0 after).
        assert not re.search(r"s__kkt\d+", stat_z), (
            "stat_z still contains s__kktN offset groups — the σ=sp entries are "
            f"being enumerated per set element, got:\n{stat_z}"
        )

        # 4. The Kronecker `1` is no longer fused into the off-diagonal
        #    coefficient.
        assert "1 - b *" not in stat_z, (
            "the Kronecker delta is still fused into the off-diagonal "
            f"coefficient, got:\n{stat_z}"
        )
