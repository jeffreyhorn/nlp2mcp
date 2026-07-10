"""Sprint 31 P1 Phase 1 / #1443: parser plumbs the per-position domain head offset.

For a head-offset equation like `pr(k,l+1,i,j)`, the parser used to collapse the
`l+1` on domain position `l` to a bare `has_head_domain_offset=True` bool and store
`domain=('k','l','i','j')` (base labels). This test suite guards the richer
`EquationDef.head_domain_offsets` field (mirroring `declaration_domain`, #1327): the
per-position `IndexOffset` tuple aligned to `domain`, from which
`has_head_domain_offset` is now derived.

The fixture-based `test_roundtrip_fixture_*` cases are the Phase-1 completion gate
(design §4): green here ⇒ the IR plumbing is correct ⇒ proceed to Phase 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from src.ir.ast import Const, IndexOffset, ParamRef

FIXTURE = Path("tests/fixtures/head_offset_ir_roundtrip.gms")


def _parse(src: str):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ir.parser import parse_model_text

        return parse_model_text(src)
    finally:
        sys.setrecursionlimit(old)


def _parse_file(path: Path):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(50000)
    try:
        from src.ir.parser import parse_model_file

        return parse_model_file(path)
    finally:
        sys.setrecursionlimit(old)


# --------------------------------------------------------------------------- #
# Phase-1 gate: the committed mine-shaped round-trip fixture (design §4)
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_roundtrip_fixture_head_offset_position_and_amount():
    """`pr(k,l+1,i,j)` → head_domain_offsets carries the l+1 at position l only."""
    if not FIXTURE.exists():
        pytest.skip(f"fixture absent: {FIXTURE}")
    eq = _parse_file(FIXTURE).equations["pr"]

    assert eq.has_head_domain_offset is True
    assert eq.domain == ("k", "l", "i", "j")  # collapsed base labels

    off = eq.head_domain_offsets
    assert off is not None
    assert len(off) == len(eq.domain)  # aligned 1:1 with domain
    assert off[0] is None  # k: no head offset
    assert isinstance(off[1], IndexOffset)  # l: the head offset
    assert off[1].base == "l"
    assert off[1].offset == Const(1.0)
    assert off[1].circular is False
    assert off[2] is None and off[3] is None  # i, j: no head offset


@pytest.mark.unit
def test_roundtrip_fixture_body_param_offsets_preserved():
    """The tail param offsets li(k)/lj(k) stay in the body (unchanged by Phase 1)."""
    if not FIXTURE.exists():
        pytest.skip(f"fixture absent: {FIXTURE}")
    eq = _parse_file(FIXTURE).equations["pr"]
    lhs = eq.lhs_rhs[0]  # x(l, i+li(k), j+lj(k))
    assert any(
        isinstance(ix, IndexOffset) and isinstance(ix.offset, ParamRef) for ix in lhs.indices
    ), f"expected ParamRef body offsets in {lhs!r}"


# --------------------------------------------------------------------------- #
# Inline shapes: alignment, derivation, exclusions
# --------------------------------------------------------------------------- #


@pytest.mark.unit
def test_plain_equation_all_none_and_bool_false():
    """No head offset ⇒ tuple of None, aligned to domain, and the bool is False."""
    src = """
    Set i / i1*i3 /;
    Variable obj, x(i);
    Equation objdef, e(i);
    objdef.. obj =e= sum(i, x(i));
    e(i).. x(i) =g= 0;
    Model m / all /;
    Solve m using nlp minimizing obj;
    """
    eq = _parse(src).equations["e"]
    assert eq.has_head_domain_offset is False
    assert eq.head_domain_offsets == (None,)
    assert len(eq.head_domain_offsets) == len(eq.domain)


@pytest.mark.unit
def test_lag_head_offset_negative_const():
    """`kk(t-1)` head ⇒ IndexOffset('t', Const(-1.0), False) at that position."""
    src = """
    Set t / t1*t4 /;
    Variable obj, k(t);
    Equation objdef, kk(t);
    objdef.. obj =e= sum(t, k(t));
    kk(t-1).. k(t) =g= k(t-1);
    Model m / all /;
    Solve m using nlp minimizing obj;
    """
    eq = _parse(src).equations["kk"]
    assert eq.has_head_domain_offset is True
    off = eq.head_domain_offsets
    assert len(off) == 1
    assert isinstance(off[0], IndexOffset)
    assert off[0].base == "t"
    assert off[0].offset == Const(-1.0)
    assert off[0].circular is False


@pytest.mark.unit
def test_body_only_offset_leaves_head_none():
    """A body offset with no head offset ⇒ head_domain_offsets is all None."""
    src = """
    Set t / t1*t4 /;
    Variable obj, x(t);
    Equation objdef, e(t);
    objdef.. obj =e= sum(t, x(t));
    e(t).. x(t) =e= x(t-1);
    Model m / all /;
    Solve m using nlp minimizing obj;
    """
    eq = _parse(src).equations["e"]
    assert eq.has_head_domain_offset is False
    assert eq.head_domain_offsets == (None,)


@pytest.mark.unit
def test_scalar_equation_empty_tuple():
    """Scalar (domain-free) equation ⇒ empty tuple, bool False."""
    src = """
    Variable obj, x;
    Equation objdef, e;
    objdef.. obj =e= x;
    e.. x =g= 0;
    Model m / all /;
    Solve m using nlp minimizing obj;
    """
    eq = _parse(src).equations["e"]
    assert eq.has_head_domain_offset is False
    # domain-free equations go through the non-domain constructor → default None
    assert eq.head_domain_offsets in (None, ())


@pytest.mark.unit
def test_multi_index_alignment_offset_only_on_one_position():
    """Two-index head with an offset only on the second position stays aligned."""
    src = """
    Set i / i1*i3 /, t / t1*t4 /;
    Variable obj, x(i,t);
    Equation objdef, e(i,t);
    objdef.. obj =e= sum((i,t), x(i,t));
    e(i,t+1).. x(i,t) =g= x(i,t+1);
    Model m / all /;
    Solve m using nlp minimizing obj;
    """
    eq = _parse(src).equations["e"]
    assert eq.domain == ("i", "t")
    off = eq.head_domain_offsets
    assert len(off) == 2
    assert off[0] is None  # i: no offset
    assert isinstance(off[1], IndexOffset) and off[1].base == "t"
    assert off[1].offset == Const(1.0)
