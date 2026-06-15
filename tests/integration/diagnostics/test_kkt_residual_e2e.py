"""End-to-end (GAMS-gated) test for the KKT-residual harness (Sprint 28 P9, Day 2).

Runs the full Architecture-A pipeline on launch — emit warm-started MCP, `nu`
sign-correct, `iterlim=0` residual eval, gdxdump parse, §2 self-check, relative-
residual verdict. Skips when GAMS or the (gitignored) raw model is absent, so CI
without a GAMS license / raw corpus is unaffected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "diagnostics"))

from kkt_residual import find_gams_tools, run_harness  # noqa: E402

LAUNCH = PROJECT_ROOT / "data" / "gamslib" / "raw" / "launch.gms"


@pytest.fixture
def gams_tools():
    tools = find_gams_tools()
    if tools is None:
        pytest.skip("GAMS/gdxdump not available")
    return tools


@pytest.mark.skipif(not LAUNCH.exists(), reason="raw launch.gms not present (gitignored corpus)")
def test_launch_residual_is_clean_and_self_check_consistent(gams_tools) -> None:
    # --no-cold-start: one solve. The dual transfer must be CONSISTENT and the
    # stationarity residual ~machine-zero after the nu sign correction (Day-2 finding).
    # Unique scratch under output/ (run_harness requires a path inside PROJECT_ROOT);
    # mkdtemp avoids xdist worker collisions on a shared dir name.
    import shutil
    import tempfile

    scratch_root = PROJECT_ROOT / "output"
    scratch_root.mkdir(exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="e2e_kkt_", dir=scratch_root))
    try:
        report = run_harness(
            LAUNCH, work, tol=1e-3, gdx=None, no_cold_start=True, gams_tools=gams_tools
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)

    assert report["dual_transfer"]["consistent"] is True
    assert report["dual_transfer"]["max_comp_infeasibility"] < 1e-3
    # Clean stationarity residual → not Case b; no cold start → a-vs-c unresolved.
    assert report["verdict"] == "case_a_or_c"
    assert report["max_residual_row"]["relative"] < 1e-6
