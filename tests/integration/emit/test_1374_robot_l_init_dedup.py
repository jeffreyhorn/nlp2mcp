"""Regression guard for #1374: a ``.fx → .l`` per-instance override that exactly
duplicates a denominator-guard bulk ``.l`` init (same element, same value) must
NOT be re-emitted.

robot has ``rho.fx(firstlast) = 4.5`` (firstlast = {h0, h50}) AND a
denominator-guard init that sets ``rho.l(h) = 4.5`` for every h (rho appears in
``1/rho``-type derivatives). The fx-derived override (``rho.l('h0')=4.5``,
``rho.l('h50')=4.5``) is redundant with the bulk init and was emitted twice.

Emits robot and checks each duplicated ``.l`` line appears once. Skips when the
(gitignored) raw model is absent.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ROBOT = PROJECT_ROOT / "data" / "gamslib" / "raw" / "robot.gms"


@pytest.mark.skipif(not ROBOT.exists(), reason="raw robot.gms not present (gitignored corpus)")
def test_robot_no_duplicate_l_init(tmp_path: Path) -> None:
    out = tmp_path / "robot_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(ROBOT),
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
    # The fx-derived boundary overrides must each appear exactly once.
    assert len(re.findall(r"rho\.l\('h0'\) = 4\.5;", text)) == 1
    assert len(re.findall(r"rho\.l\('h50'\) = 4\.5;", text)) == 1
    # No exact-duplicate `.l` init lines anywhere.
    l_lines = [ln.strip() for ln in text.splitlines() if re.match(r"^\s*[A-Za-z_]\w*\.l\b", ln)]
    dups = {ln for ln in l_lines if l_lines.count(ln) > 1}
    assert not dups, f"duplicate .l init lines: {sorted(dups)}"
