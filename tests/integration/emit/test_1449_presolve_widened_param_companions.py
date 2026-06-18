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
    include_pos = text.index("$include")

    # db is referenced at its PARENT index `db(tt)` in stat_p, so it needs a
    # widened companion: declared at the source domain `db(t)` (to agree with the
    # $include) with a `db__pw(tt)` companion, emitted AFTER the $include.
    assert "Parameter db__pw(tt);" in text
    assert "db__pw(t) = db(t);" in text
    assert text.index("Parameter db__pw(tt);") > include_pos

    # stat_p references the companion at the parent index; the bare `db(tt)` is
    # gone (rewritten).
    stat_p = re.search(r"stat_p\(tt\)\.\..*?;", text, re.DOTALL)
    assert stat_p is not None
    stat_p_nz = re.sub(r"\s+", "", stat_p.group(0))
    assert "db__pw(tt)" in stat_p_nz
    assert "db(tt)" not in stat_p_nz

    # Over-rename guard (the original-equation corruption fixed here): the
    # re-emitted ORIGINAL `dem` equation must keep the SUBSET-index `db(t)` — NOT
    # the companion. Renaming it would override the source's `dem` algebra
    # globally (GAMS binds equation algebra to its last `..`), corrupting the
    # embedded NLP (db__pw is 0 when the NLP solves).
    dem = re.search(r"\bdem\(t\)\.\..*?;", text, re.DOTALL)
    assert dem is not None
    dem_nz = re.sub(r"\s+", "", dem.group(0))
    assert "db(t)" in dem_nz
    assert "db__pw" not in dem_nz

    # Over-widened params referenced only at the subset index (del/xb) get NO
    # companion (they stay at their source domain, valid against the include).
    assert "del__pw" not in text
    assert "xb__pw" not in text

    # Layer-4: the source $include's `x.fx(th)` fixes x('1974'), which the MCP
    # instead fixes via the active `x_fx_1974` equation — so it is unfixed here.
    assert "x.lo('1974')" in text
    assert "x.up('1974')" in text
