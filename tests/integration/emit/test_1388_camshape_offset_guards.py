"""Regression guard for #1388 (Day 5): offset cross-terms in stationarity must be
guarded by the equation membership condition at the OFFSET (neighbor) index, not
the current index — e.g. lam_convexity(i+1) by `$(middle(i+1))`, not `$(middle(i))`.

Emits camshape and checks the corrected guards. Skips when the (gitignored) raw
model is absent, so CI without the corpus is unaffected.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CAMSHAPE = PROJECT_ROOT / "data" / "gamslib" / "raw" / "camshape.gms"


@pytest.mark.skipif(
    not CAMSHAPE.exists(), reason="raw camshape.gms not present (gitignored corpus)"
)
def test_camshape_offset_crossterm_guards_use_neighbor_index(tmp_path: Path) -> None:
    out = tmp_path / "camshape_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(CAMSHAPE),
            "-o",
            str(out),
            "--quiet",
            "--skip-convexity-check",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    text = out.read_text(encoding="utf-8")
    # Capture the full `stat_r(i).. ... ;` statement across newlines, then strip all
    # whitespace, so the guard is robust to line-wrapping / indentation changes.
    match = re.search(r"stat_r\(i\)\.\..*?;", text, re.DOTALL)
    if match is None:
        pytest.fail("no `stat_r(i).. ... ;` statement found in the camshape emit")
    stat_r = re.sub(r"\s+", "", match.group(0))

    def nz(s: str) -> str:
        return re.sub(r"\s+", "", s)

    # Neighbor cross-terms must be guarded at the OFFSET index (the fix).
    assert nz("lam_convexity(i+1))$(ord(i) <= card(i) - 1))$(middle(i+1))") in stat_r
    assert nz("lam_convexity(i-1))$(ord(i) > 1))$(middle(i-1))") in stat_r
    assert nz("lam_convex_edge1(i-1))$(ord(i) > 1))$(first(i-1))") in stat_r
    assert nz("lam_convex_edge3(i+1))$(ord(i) <= card(i) - 1))$(last(i+1))") in stat_r

    # The old (buggy) current-index guards on the neighbor terms must be gone.
    assert nz("lam_convexity(i+1))$(ord(i) <= card(i) - 1))$(middle(i))") not in stat_r
    assert nz("lam_convex_edge1(i-1))$(ord(i) > 1))$(first(i))") not in stat_r

    # The SELF term (offset 0) keeps the current-index guard — not over-shifted.
    assert nz("lam_convexity(i))$(middle(i))") in stat_r
