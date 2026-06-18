"""Regression guard for #1452 (Day 7 follow-on): a variable referenced via an
``ord``-driven lag offset inside a sum over the coefficient's set —
otpop's ``pdef(tt).. pd(tt) =e= sum(n, alpha(n)*p(tt-(ord(n)-1)))`` — expands
into per-lead offset groups, one per element of ``n``. Each group's coefficient
``alpha`` is then a SINGLE offset-determined element (``alpha('1')`` at lead 0,
``alpha('2')`` at lead +1, ``alpha('3')`` at lead +2), NOT a free sum index.

Before the fix, the stationarity re-symbolization mapped that concrete element
back to the iterator ``n`` and re-summed it (the generic free-index path), so
all three leads collapsed to the identical ``sum(n, (-alpha(n))*nu_pdef(tt+k))``
— losing the per-lead weights and breaking otpop's match. The fix pins the
offset-driving set's element so each lead keeps its concrete weight.

Emits otpop and checks the three per-lead ``stat_p`` cross-terms are present
with their distinct concrete ``alpha`` elements and NO residual ``sum(n, ...)``.
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
def test_otpop_pdef_per_lead_weights_in_stat_p(tmp_path: Path) -> None:
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

    # Each lead keeps its OWN concrete alpha element (the #1452 fix). Lead 0 has
    # no offset; leads +1/+2 are guarded by the tail-of-horizon `ord<=card-k`.
    assert 'alpha("1"))*nu_pdef(tt)' in stat_p, "lead-0 pdef weight missing/wrong (#1452)"
    assert (
        'alpha("2"))*nu_pdef(tt+1))$(ord(tt)<=card(tt)-1)' in stat_p
    ), "lead-+1 weight wrong (#1452)"
    assert (
        'alpha("3"))*nu_pdef(tt+2))$(ord(tt)<=card(tt)-2)' in stat_p
    ), "lead-+2 weight wrong (#1452)"

    # The pre-fix collapse re-summed the pinned element: there must be NO
    # `sum(n, ...)` over the pdef coefficient in stat_p anymore.
    assert (
        "sum(n," not in stat_p
    ), "stat_p still re-sums the pdef coefficient over n (#1452 regressed)"
    assert (
        "alpha(n)" not in stat_p
    ), "stat_p still re-symbolizes alpha to the iterator n (#1452 regressed)"
