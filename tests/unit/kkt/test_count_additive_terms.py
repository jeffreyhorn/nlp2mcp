"""Sprint 31 P2 (#1111/#1112): `_count_additive_terms` term-counting for the
offset-path interior-representative selection.

The offset path re-symbolizes ONE representative instance's objective gradient
and generalizes it to every interior row, so it must pick the instance carrying
the MOST additive offset images (an interior column), not a boundary column that
drops one image. `_count_additive_terms` scores each candidate; it must see
through the maximize-negation, `Const`/condition-factor scaling, `Sum` wrappers,
AND the `DollarConditional` condition wrapper/factor forms that gradient.py
produces for a *conditioned* objective (else a conditioned additive gradient
under-counts and a boundary instance is chosen, re-dropping the cross-term).
"""

from __future__ import annotations

import pytest

from src.ir.ast import Binary, Const, DollarConditional, Sum, SymbolRef, Unary, VarRef
from src.kkt.stationarity import _count_additive_terms

# VarRef.indices are `tuple[str | IndexOffset, ...]` — use bare string indices,
# the representative AST shape (the parser emits `VarRef("x", ("i",))`).
_A = VarRef("x", ("i",))
_B = VarRef("y", ("i",))
_ADD = Binary("+", _A, _B)  # two additive terms
_COND = SymbolRef("c")  # a condition is an Expr; SymbolRef is a valid condition
_COND_FACTOR = DollarConditional(value_expr=Const(1.0), condition=_COND)  # `1$(c)`


@pytest.mark.unit
def test_plain_additive():
    assert _count_additive_terms(_ADD) == 2
    assert _count_additive_terms(Binary("-", _ADD, _A)) == 3


@pytest.mark.unit
def test_single_product_is_one_term():
    assert _count_additive_terms(Binary("*", _A, _B)) == 1


@pytest.mark.unit
def test_maximize_negation_transparent():
    assert _count_additive_terms(Unary("-", _ADD)) == 2
    assert _count_additive_terms(Unary("+", _ADD)) == 2


@pytest.mark.unit
def test_const_scale_distributes():
    # polygon's `0.5 * (A + B)`
    assert _count_additive_terms(Binary("*", Const(0.5), _ADD)) == 2
    assert _count_additive_terms(Binary("*", _ADD, Const(0.5))) == 2


@pytest.mark.unit
def test_sum_transparent():
    assert _count_additive_terms(Sum(("k",), _ADD)) == 2


@pytest.mark.unit
def test_dollar_conditional_wrapper_pattern1():
    """gradient.py pattern 1: `DollarConditional(value, cond)` — the condition must
    be transparent so an additive conditioned gradient counts its images."""
    assert _count_additive_terms(DollarConditional(value_expr=_ADD, condition=_COND)) == 2


@pytest.mark.unit
def test_condition_factor_pattern2():
    """gradient.py pattern 2: `value * DollarConditional(Const(1.0), cond)` — the
    condition factor is const-like, so `(A+B)*1$(c)` distributes to two terms."""
    assert _count_additive_terms(Binary("*", _ADD, _COND_FACTOR)) == 2
    assert _count_additive_terms(Binary("*", _COND_FACTOR, _ADD)) == 2


@pytest.mark.unit
def test_polygon_shape_conditioned_single_image_is_one():
    """A single conditioned offset image `(sin*r) * 1$(cond)` is ONE term (the
    condition factor scales a product, it does not add terms) — so an interior
    row with two such images (count 2) still outranks a boundary row (count 1)."""
    product = Binary("*", _A, _B)
    assert _count_additive_terms(Binary("*", product, _COND_FACTOR)) == 1
    # lone condition factor is one term
    assert _count_additive_terms(_COND_FACTOR) == 1
    # boundary (1 image) vs interior (2 images) ordering
    interior = Unary("-", Binary("*", Const(0.5), Binary("+", product, product)))
    boundary = Unary("-", Binary("*", Const(0.5), product))
    assert _count_additive_terms(interior) > _count_additive_terms(boundary)
