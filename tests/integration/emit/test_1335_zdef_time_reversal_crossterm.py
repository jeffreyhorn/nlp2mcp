"""Regression guard for #1335 (Day 7): a variable referenced via a time-reversal
offset ``p(t + (card(t) - ord(t)))`` inside a scalar ``sum(t, …)`` constraint
(otpop's ``zdef``) maps every iterate to the LAST element, so it is a constant
column. Differentiating w.r.t. that column must PRESERVE the sum — yielding the
``stat_p`` cross-term ``((-1)*v*sum(t, 0.365*(xb(t)-x(t))))*nu_zdef`` guarded by
``sameas(tt,'1990')`` — not collapse it (which dropped the term entirely).

Emits otpop and checks the cross-term is present with the last-element guard.
Skips when the (gitignored) raw model is absent, so CI without the corpus is
unaffected.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OTPOP = PROJECT_ROOT / "data" / "gamslib" / "raw" / "otpop.gms"


@pytest.mark.skipif(not OTPOP.exists(), reason="raw otpop.gms not present (gitignored corpus)")
def test_otpop_zdef_crossterm_present_in_stat_p(tmp_path: Path) -> None:
    out = tmp_path / "otpop_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(OTPOP),
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
    match = re.search(r"stat_p\(tt\)\.\..*?;", text, re.DOTALL)
    if match is None:
        pytest.fail("no `stat_p(tt).. ... ;` statement found in the otpop emit")
    stat_p = re.sub(r"\s+", "", match.group(0))

    # The zdef cross-term must be present, sum-preserving, guarded at the last
    # element (#1335). Before the fix `nu_zdef` was entirely absent from stat_p.
    assert "nu_zdef" in stat_p, "stat_p is still missing its nu_zdef cross-term (#1335 regressed)"
    assert "sum(t,0.365*(xb(t)-x(t)))" in stat_p
    assert "nu_zdef)$(sameas(tt,'1990'))" in stat_p
    # It must NOT collapse to a single t (the bug would have dropped the sum).
    assert "sum(t__" not in stat_p.split("nu_zdef")[0][-80:]
