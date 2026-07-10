"""Sprint 31 P1 Phase 2 / #1443: the ``--nlp-presolve`` dual transfer reads a
head-domain-offset inequality's marginal at the SHIFTED head label.

For ``pr(k,l+1,i,j)$c(l,i,j)..`` GAMS labels the generated equation instance —
and stores its marginal ``pr.m`` — at the shifted head label ``(k, l+1, i, j)``,
while the paired MCP multiplier ``lam_pr`` lives at the collapsed base domain
``(k, l, i, j)`` (``comp_pr`` is emitted at base ``l``). Before Phase 2 the
warm-start transfer read ``pr.m(k,l,i,j)`` (base) — the wrong instance — so
``lam_pr`` was initialised from a mis-aligned dual and the warm MCP stayed off
the NLP KKT point. Phase 2 shifts the read to ``pr.m(k,l+1,i,j)``.

The primary guard uses the committed always-run fixture
``tests/fixtures/head_offset_ir_roundtrip.gms`` (a mine-shaped head-offset
inequality); a second check exercises the real GAMSlib ``mine`` and skips when
the (gitignored) raw model is absent. The cold (non-presolve) emit must be
unaffected — the shift lives only in the presolve dual transfer.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "head_offset_ir_roundtrip.gms"
_MINE_SRC = _REPO_ROOT / "data" / "gamslib" / "raw" / "mine.gms"

# lam_pr.l(k,l,i,j) = abs(pr.m(k,l+1,i,j));   <- shifted head label on the RHS read
_SHIFTED = re.compile(r"lam_pr\.l\(k,l,i,j\)\s*=\s*abs\(pr\.m\(k,l\+1,i,j\)\)\s*;")
_BASE = re.compile(r"lam_pr\.l\(k,l,i,j\)\s*=\s*abs\(pr\.m\(k,l,i,j\)\)\s*;")


@pytest.fixture(autouse=True)
def _high_recursion_limit():
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        yield
    finally:
        sys.setrecursionlimit(old)


def _emit_mcp_for(gms_path: Path, *, nlp_presolve: bool) -> str:
    from src.ad.constraint_jacobian import compute_constraint_jacobian
    from src.ad.gradient import compute_objective_gradient
    from src.emit.emit_gams import emit_gams_mcp
    from src.ir.normalize import normalize_model
    from src.ir.parser import parse_model_file
    from src.kkt.assemble import assemble_kkt_system

    model = parse_model_file(str(gms_path))
    normalize_model(model)
    j_eq, j_ineq = compute_constraint_jacobian(model)
    grad = compute_objective_gradient(model)
    kkt = assemble_kkt_system(model, grad, j_eq, j_ineq)
    return emit_gams_mcp(
        kkt,
        nlp_presolve=nlp_presolve,
        source_file=str(gms_path) if nlp_presolve else None,
    )


# --- Primary guard: committed fixture (always runs in CI) --------------------


def test_presolve_transfer_is_head_shifted_fixture():
    assert _FIXTURE.exists(), f"missing committed fixture: {_FIXTURE}"
    out = _emit_mcp_for(_FIXTURE, nlp_presolve=True)
    assert _SHIFTED.search(out), (
        "Presolve dual transfer for the head-offset inequality `pr` must read the "
        "marginal at the SHIFTED head label pr.m(k,l+1,i,j); got:\n"
        + "\n".join(line for line in out.splitlines() if "lam_pr.l" in line)
    )
    assert _BASE.search(out) is None, "base-label transfer pr.m(k,l,i,j) must be gone"


def test_cold_emit_has_no_presolve_transfer_fixture():
    """The dual transfer is presolve-only — the cold (non-presolve) emit must
    contain NEITHER the shifted nor the base transfer (a shifted line leaking
    into the cold emit would be a bug too)."""
    assert _FIXTURE.exists(), f"missing committed fixture: {_FIXTURE}"
    out = _emit_mcp_for(_FIXTURE, nlp_presolve=False)
    offending = [line for line in out.splitlines() if "lam_pr.l" in line and "abs(pr.m(" in line]
    assert _SHIFTED.search(out) is None and _BASE.search(out) is None, (
        "Cold (non-presolve) emit must not contain a `lam_pr.l = abs(pr.m(...))` "
        "dual transfer (neither shifted (k,l+1,i,j) nor base (k,l,i,j)); found:\n"
        + "\n".join(offending)
    )


# --- Real GAMSlib mine (skips when the raw model is absent) ------------------


@pytest.mark.skipif(not _MINE_SRC.exists(), reason="mine.gms not available")
def test_presolve_transfer_is_head_shifted_mine():
    out = _emit_mcp_for(_MINE_SRC, nlp_presolve=True)
    assert _SHIFTED.search(out), "mine presolve transfer must be head-shifted"
    assert _BASE.search(out) is None
