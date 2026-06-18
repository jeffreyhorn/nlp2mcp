"""Regression guard for #1449 (Day 7 follow-on): under ``--nlp-presolve``, a
domain-widened param must NOT be declared at its widened (parent) domain (that
collides with the ``$include`` source's subset declaration → GAMS ``$184``).
Instead the source param is declared at its subset domain and a ``<p>__pw``
companion at the widened domain is emitted after the ``$include`` for the MCP
body to use.

Emits otpop with ``--nlp-presolve`` and checks the companion pattern. Skips
when the (gitignored) raw model is absent, so CI without the corpus is
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
def test_otpop_presolve_emits_widened_companions(tmp_path: Path) -> None:
    out = tmp_path / "otpop_mcp_presolve.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(OTPOP),
            "-o",
            str(out),
            "--nlp-presolve",
            "--quiet",
            "--skip-convexity-check",
        ],
        cwd=str(PROJECT_ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    text = out.read_text(encoding="utf-8")

    # db is widened (db(tt) in stat_p). Under presolve it must be declared at its
    # SOURCE domain db(t) (matching the include), with a db__pw(tt) companion.
    assert "Parameter db__pw(tt);" in text
    assert "db__pw(t) = db(t);" in text
    # The companion must be declared AFTER the $include (so the source owns db(t)).
    include_pos = text.index("$include")
    assert text.index("Parameter db__pw(tt);") > include_pos
    # The MCP body must reference the companion, not the (now subset-domain) db
    # at the widened index — i.e. no bare `db(tt)` survives in the stationarity.
    stat_p = re.search(r"stat_p\(tt\)\.\..*?;", text, re.DOTALL)
    assert stat_p is not None
    stat_p_nz = re.sub(r"\s+", "", stat_p.group(0))
    assert "db__pw(tt)" in stat_p_nz
    assert "db(tt)" not in stat_p_nz  # the widened reference was rewritten
