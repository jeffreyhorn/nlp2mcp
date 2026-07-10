"""Sprint 31 P1 Phase 2 / #1443: the shared head-offset index-map helper (Site 2).

`head_offset_marginal_index_map` centralises the head↔base correspondence the
`--nlp-presolve` dual transfer needs: for a head-domain-offset inequality like
`pr(k,l+1,i,j)`, GAMS stores the marginal `pr.m` at the SHIFTED head label
`(k, l+1, i, j)` while the MCP multiplier `lam_pr` is paired at the base
`(k, l, i, j)`, so the warm-start transfer must read `pr.m` at the shifted label.
"""

from __future__ import annotations

import sys

import pytest

from src.emit.emit_gams import head_offset_marginal_index_map
from src.ir.ast import Const, IndexOffset
from src.ir.symbols import EquationDef, Rel


def _parse_file(path: str):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ir.parser import parse_model_file

        return parse_model_file(path)
    finally:
        sys.setrecursionlimit(old)


def _eq(domain, head_offsets):
    return EquationDef(
        name="e",
        domain=domain,
        relation=Rel.GE,
        lhs_rhs=(None, None),
        head_domain_offsets=head_offsets,
    )


@pytest.mark.unit
def test_lead_head_offset_shifts_that_position():
    """`pr(k,l+1,i,j)` → the marginal read is `(k,l+1,i,j)`."""
    eq = _eq(
        ("k", "l", "i", "j"),
        (None, IndexOffset(base="l", offset=Const(1.0), circular=False), None, None),
    )
    assert head_offset_marginal_index_map(eq) == "(k,l+1,i,j)"


@pytest.mark.unit
def test_lag_head_offset_renders_minus():
    """A `t-1` head renders as `t-1` in the marginal read."""
    eq = _eq(
        ("t",),
        (IndexOffset(base="t", offset=Const(-1.0), circular=False),),
    )
    assert head_offset_marginal_index_map(eq) == "(t-1)"


@pytest.mark.unit
def test_no_head_offset_returns_none():
    """No head offset → None (caller keeps the plain base-domain read)."""
    assert head_offset_marginal_index_map(_eq(("i", "j"), (None, None))) is None
    assert head_offset_marginal_index_map(_eq(("i", "j"), None)) is None


@pytest.mark.unit
def test_scalar_equation_returns_none():
    """Domain-free equation → None."""
    assert head_offset_marginal_index_map(_eq((), ())) is None


@pytest.mark.unit
def test_offset_base_is_quoted_like_non_offset_branch():
    """A base that requires quoting is routed through `_quote_symbol` in the
    offset branch too (quoting + injection-safety), not emitted raw."""
    from src.emit.emit_gams import _quote_symbol

    eq = _eq(
        ("a-b",),
        (IndexOffset(base="a-b", offset=Const(1.0), circular=False),),
    )
    quoted = _quote_symbol("a-b")  # e.g. 'a-b'
    assert head_offset_marginal_index_map(eq) == f"({quoted}+1)"


@pytest.mark.unit
def test_mine_pr_equation_from_parse():
    """End-to-end: the real parsed mine `pr` equation maps to (k,l+1,i,j)."""
    m = _parse_file("data/gamslib/raw/mine.gms")
    if "pr" not in m.equations:
        pytest.skip("mine.gms not available (raw corpus absent)")
    assert head_offset_marginal_index_map(m.equations["pr"]) == "(k,l+1,i,j)"
    assert head_offset_marginal_index_map(m.equations["def"]) is None
