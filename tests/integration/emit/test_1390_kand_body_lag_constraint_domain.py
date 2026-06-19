"""Regression guard for #1390 (Sprint 28 Day 10): an inequality constraint with
a BODY lead/lag offset must NOT have its complementarity domain restricted (nor
its multiplier fixed) by the inferred lead/lag bound.

kand's ``dembalx(j,tn(t,n)).. sum(i,a(j,i)*x(i,t)) + y(j,tn) =g= dem(n,j) +
eps*sum(tree(nn,n), y(j,t-1,nn))`` has the lag ``y(j,t-1,nn)`` in its BODY (not
its head domain). GAMS evaluates the out-of-range lag at the first period as 0,
so the constraint is defined at ALL ``tn(t,n)``. Previously the emit restricted
``comp_dembalx`` to ``ord(t)>1`` and fixed ``lam_dembalx=0`` at the first period
— dropping the first-period demand constraint and corrupting ``stat_x`` (the MCP
solved to a spurious 195.0 vs the LP optimum 2613.0). The fix mirrors the
equality path (restrict only for a head-domain offset).

Emits kand and checks the complementarity domain / multiplier fixing. Skips when
the (gitignored) raw model is absent, so CI without the corpus is unaffected.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parents[3]
KAND = PROJECT_ROOT / "data" / "gamslib" / "raw" / "kand.gms"


@pytest.mark.skipif(not KAND.exists(), reason="raw kand.gms not present (gitignored corpus)")
def test_kand_body_lag_constraint_not_domain_restricted(tmp_path: Path) -> None:
    out = tmp_path / "kand_mcp.gms"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "src.cli",
            str(KAND),
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

    comp = re.search(r"comp_dembalx\(j,t,n\)[^.]*\.\.", text)
    assert comp is not None, "comp_dembalx(j,t,n).. not found"
    comp_head = comp.group(0)
    # The complementarity must be defined over the full tn(t,n) domain, NOT
    # restricted to ord(t)>1 (the body-lag inferred bound).
    assert (
        "ord(t) > 1" not in comp_head
    ), f"comp_dembalx still restricted by the body-lag inferred bound: {comp_head!r}"

    # lam_dembalx must NOT be fixed by the body-lag bound (only the genuine
    # tn(t,n) domain fix is allowed).
    for m in re.finditer(r"lam_dembalx\.fx[^;]*;", text):
        assert "ord(t) > 1" not in m.group(
            0
        ), f"lam_dembalx fixed by the body-lag bound: {m.group(0)!r}"
