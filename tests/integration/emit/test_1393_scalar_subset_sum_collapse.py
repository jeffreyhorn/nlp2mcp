"""Regression guard for #1393 (Day 6): a scalar-constraint Jacobian term whose
derivative re-symbolizes a SUBSET parameter to a synthetic ``__`` alias (e.g.
``del(t__)`` for ``Set t(tt)``) must COLLAPSE the alias back to the variable's
domain index with a subset-membership guard — NOT wrap it in ``sum(t__, …)``,
which over-counts the stationarity row by ``|subset|``.

Covers:
- otpop  ``kdef.. k =e= sum(t, del(t)*…*x(t))``  (the reported #1393 case)
- chenery ``tb`` scalar constraint summing ``h(t)``/``g(t)`` over ``t``
- china   ``cdef`` scalar constraint summing ``cxfert(cf)``

Each model is emitted fresh to ``tmp_path`` and inspected. Skips when the
(gitignored) raw model is absent, so CI without the corpus is unaffected.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW = PROJECT_ROOT / "data" / "gamslib" / "raw"


def _emit(model: str, tmp_path: Path) -> str:
    out = tmp_path / f"{model}_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(RAW / f"{model}.gms"),
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
    return out.read_text(encoding="utf-8")


def _stmt(text: str, lhs: str) -> str:
    """Return the `<lhs>.. ... ;` statement with all whitespace stripped."""
    match = re.search(re.escape(lhs) + r"\.\..*?;", text, re.DOTALL)
    if match is None:
        pytest.fail(f"no `{lhs}.. ... ;` statement found in the emit")
    return re.sub(r"\s+", "", match.group(0))


@pytest.mark.skipif(
    not (RAW / "otpop.gms").exists(), reason="raw otpop.gms not present (gitignored corpus)"
)
def test_otpop_kdef_crossterm_collapses_no_subset_sum(tmp_path: Path) -> None:
    text = _emit("otpop", tmp_path)
    # No BARE (over-counting) sum over the synthetic subset alias on nu_kdef.
    assert re.search(r"sum\(t__,[^;]*nu_kdef", text) is None
    stat_x = _stmt(text, "stat_x(tt)")
    # The kdef term collapsed to a sameas-guarded singleton sum (domain-safe).
    assert "sum(t__$(sameas(t__,tt)),((-1)*(del(t__)*0.365*(1-c)*p(tt)))*nu_kdef)$(t(tt))" in stat_x


@pytest.mark.skipif(
    not (RAW / "chenery.gms").exists(), reason="raw chenery.gms not present (gitignored corpus)"
)
def test_chenery_tb_crossterm_collapses_no_subset_sum(tmp_path: Path) -> None:
    text = _emit("chenery", tmp_path)
    # The over-counting BARE sums over the t__ alias on lam_tb must be gone...
    assert re.search(r"sum\(t__,[^;]*lam_tb", text) is None
    # ...replaced by sameas-guarded singleton sums in stat_e / stat_m.
    assert "sum(t__$(sameas(t__,i)),((-1)*h(t__))*lam_tb)$(t(i))" in _stmt(text, "stat_e(i)")
    assert "sum(t__$(sameas(t__,i)),g(t__)*lam_tb)$(t(i))" in _stmt(text, "stat_m(i)")


@pytest.mark.skipif(
    not (RAW / "china.gms").exists(), reason="raw china.gms not present (gitignored corpus)"
)
def test_china_cdef_crossterm_collapses_no_subset_sum(tmp_path: Path) -> None:
    text = _emit("china", tmp_path)
    stat_xfert = _stmt(text, "stat_xfert(ca)")
    # The cdef cross-term collapsed to a sameas-guarded singleton; no BARE sum.
    assert re.search(r"sum\(cf__,[^)]*nu_cdef", stat_xfert) is None
    assert "sum(cf__$(sameas(cf__,ca)),((-1)*cxfert(cf__))*nu_cdef)$(cf(ca))" in stat_xfert
