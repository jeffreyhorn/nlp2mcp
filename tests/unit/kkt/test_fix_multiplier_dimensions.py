"""Test MultiplierRef dimension mismatch fixing.

Issue #1227: When a constraint has more dimensions than the variable
(e.g., mp(i,t) → stat_p(i)), MultiplierRef nodes may have fewer indices
than declared. _fix_multiplier_dimensions wraps these in Sum over the
missing dimensions.
"""

import pytest

from src.ir.ast import Binary, Const, MultiplierRef, Sum
from src.kkt.stationarity import _fix_multiplier_dimensions


class _FakeMultDef:
    def __init__(self, name: str, domain: tuple[str, ...]):
        self.name = name
        self.domain = domain


class _FakeKKT:
    def __init__(self, mult_defs: list[_FakeMultDef]):
        self.multipliers_eq = {d.name: d for d in mult_defs if d.name.startswith("nu_")}
        self.multipliers_ineq = {d.name: d for d in mult_defs if d.name.startswith("lam_")}


@pytest.mark.unit
class TestFixMultiplierDimensions:
    def test_wraps_missing_dimension_in_sum(self):
        """lam_mp(i) with declared domain (i,t) → sum(t, lam_mp(i,t))."""
        kkt = _FakeKKT([_FakeMultDef("lam_mp", ("i", "t"))])
        # expr: lam_mp(i) — missing dimension t
        expr = MultiplierRef("lam_mp", ("i",))
        result = _fix_multiplier_dimensions(expr, kkt)

        assert isinstance(result, Sum)
        assert result.index_sets == ("t",)
        inner = result.body
        assert isinstance(inner, MultiplierRef)
        assert inner.name == "lam_mp"
        assert inner.indices == ("i", "t")

    def test_correct_dimensions_unchanged(self):
        """lam_mp(i,t) with declared domain (i,t) → unchanged."""
        kkt = _FakeKKT([_FakeMultDef("lam_mp", ("i", "t"))])
        expr = MultiplierRef("lam_mp", ("i", "t"))
        result = _fix_multiplier_dimensions(expr, kkt)

        assert isinstance(result, MultiplierRef)
        assert result.indices == ("i", "t")

    def test_additive_terms_fixed_independently(self):
        """a + lam_mp(i) → a + sum(t, lam_mp(i,t))."""
        kkt = _FakeKKT([_FakeMultDef("lam_mp", ("i", "t"))])
        expr = Binary("+", Const(1.0), MultiplierRef("lam_mp", ("i",)))
        result = _fix_multiplier_dimensions(expr, kkt)

        assert isinstance(result, Binary)
        assert isinstance(result.left, Const)
        assert isinstance(result.right, Sum)
        assert result.right.index_sets == ("t",)

    def test_inside_sum_not_modified(self):
        """sum(t, lam_mp(i,t)) — already correct, not modified."""
        kkt = _FakeKKT([_FakeMultDef("lam_mp", ("i", "t"))])
        inner = MultiplierRef("lam_mp", ("i", "t"))
        expr = Sum(("t",), inner)
        result = _fix_multiplier_dimensions(expr, kkt)

        assert result is expr  # Unchanged
