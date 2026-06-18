"""Regression guard for #1387 + #1455 (Sprint 28 Day 9): cclinpts's objective is
an offset-indexed trapezoid sum

    object.. ObjV =e=    sum(j$(not last(j)),  [b('%last%') - b(j)]*[fb(j) - fb(j-1)])
                  +  0.5*sum(j$(not first(j)), [b(j) - b(j-1)]*[fb(j) - fb(j-1)]);

so ``b``/``fb`` appear at non-zero offsets of the sum index ``j`` (``b(j-1)``,
``fb(j-1)``) and a FIXED boundary literal ``b('%last%')`` → ``b('s30')``. The
stationarity gradient must:

- #1387: include the ``j+1`` offset cross-terms (the per-instance gradient of an
  offset-indexed sum is dropped by the generic collapse) — ``stat_b`` gets
  ``0.5*(fb(j+1)-fb(j))`` and ``stat_fb`` gets all four contributions; and
- #1455: keep the fixed boundary element ``b('s30')`` literal (mapping it to
  ``b(j)`` collapses ``b('s30')-b(j)`` to ``0``).

Emits cclinpts and checks the per-term shape. Skips when the (gitignored) raw
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
CCLINPTS = PROJECT_ROOT / "data" / "gamslib" / "raw" / "cclinpts.gms"


@pytest.mark.skipif(not CCLINPTS.exists(), reason="raw cclinpts.gms not present (gitignored corpus)")
def test_cclinpts_stat_b_stat_fb_offset_crossterms(tmp_path: Path) -> None:
    out = tmp_path / "cclinpts_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(CCLINPTS),
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
    stat_b_m = re.search(r"^stat_b\(j\)\.\..*?;", text, re.MULTILINE)
    stat_fb_m = re.search(r"^stat_fb\(j\)\.\..*?;", text, re.MULTILINE)
    assert stat_b_m is not None, "stat_b(j) not found"
    assert stat_fb_m is not None, "stat_fb(j) not found"
    stat_b = re.sub(r"\s+", "", stat_b_m.group(0))
    stat_fb = re.sub(r"\s+", "", stat_fb_m.group(0))

    # stat_b: diagonal Term-1/2 (fb(j)-fb(j-1)) AND the #1387 j+1 cross-term.
    assert "fb(j)-fb(j-1)" in stat_b, "stat_b missing diagonal fb(j)-fb(j-1)"
    assert "fb(j+1)-fb(j)" in stat_b, "stat_b missing #1387 j+1 cross-term fb(j+1)-fb(j)"
    assert "notfirst(j+1)" in stat_b, "stat_b j+1 cross-term missing the first(j+1) guard"

    # stat_fb: all four contributions, with the FIXED literal b('s30') preserved
    # (#1455) — not collapsed to b(j).
    assert 'b("s30")-b(j)' in stat_fb, "stat_fb missing Term-1-at-j b('s30')-b(j) (#1455 literal)"
    assert 'b("s30")-b(j+1)' in stat_fb, "stat_fb missing Term-1-at-j+1 b('s30')-b(j+1)"
    assert "b(j)-b(j-1)" in stat_fb, "stat_fb missing Term-2-at-j b(j)-b(j-1)"
    assert "b(j+1)-b(j)" in stat_fb, "stat_fb missing Term-2-at-j+1 b(j+1)-b(j)"
    # #1455: the boundary literal must NOT have collapsed to b(j)-b(j) = 0.
    assert "b(j)-b(j))" not in stat_fb, "stat_fb has a collapsed b(j)-b(j) (#1455 regressed)"
