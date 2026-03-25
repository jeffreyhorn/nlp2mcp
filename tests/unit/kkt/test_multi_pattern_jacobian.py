"""Tests for multi-pattern Jacobian detection and correction (Issue #1110).

When a constraint body references a variable both directly AND inside a sum,
diagonal and off-diagonal entries have structurally different derivatives.
The stationarity builder should use the majority pattern for the main sum
and add a correction term for the minority pattern (Kronecker delta).
"""

from __future__ import annotations

import pytest

from src.ir.ast import (
    Binary,
    Const,
    DollarConditional,
    ParamRef,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.kkt.stationarity import (
    _derivative_structure_key,
    _substitute_elements,
    _subtract_and_cancel,
)

pytestmark = pytest.mark.unit

# ── _derivative_structure_key ────────────────────────────────────────


class TestDerivativeStructureKey:
    """Test structural fingerprinting of derivative ASTs."""

    def test_same_structure_same_key(self):
        """Identical AST shapes with different concrete indices → same key."""
        a = Binary("-", Const(1.0), Binary("*", ParamRef("b"), ParamRef("pi", ("x", "y"))))
        b = Binary("-", Const(1.0), Binary("*", ParamRef("b"), ParamRef("pi", ("a", "b"))))
        assert _derivative_structure_key(a) == _derivative_structure_key(b)

    def test_different_structure_different_key(self):
        """Structurally different ASTs → different keys."""
        # Diagonal: 1 - b*pi(...)
        diag = Binary("-", Const(1.0), Binary("*", ParamRef("b"), ParamRef("pi", ("x",))))
        # Off-diagonal: -(b*pi(...))
        off = Unary("-", Binary("*", ParamRef("b"), ParamRef("pi", ("x",))))
        assert _derivative_structure_key(diag) != _derivative_structure_key(off)

    def test_const_same(self):
        """Constants with same value → same key."""
        assert _derivative_structure_key(Const(1.0)) == _derivative_structure_key(Const(1.0))

    def test_const_different_values(self):
        """Constants with different values → different keys."""
        assert _derivative_structure_key(Const(1.0)) != _derivative_structure_key(Const(2.0))

    def test_param_arity_not_values(self):
        """ParamRef key uses arity, not concrete index values."""
        a = ParamRef("pi", ("x", "y", "z"))
        b = ParamRef("pi", ("a", "b", "c"))
        assert _derivative_structure_key(a) == _derivative_structure_key(b)

    def test_param_different_arity(self):
        """ParamRef with different arity → different key."""
        a = ParamRef("pi", ("x", "y"))
        b = ParamRef("pi", ("x", "y", "z"))
        assert _derivative_structure_key(a) != _derivative_structure_key(b)

    def test_dollar_conditional(self):
        """DollarConditional fingerprint includes both value and condition."""
        dc = DollarConditional(Const(1.0), ParamRef("flag"))
        plain = Const(1.0)
        assert _derivative_structure_key(dc) != _derivative_structure_key(plain)

    def test_sum_node(self):
        """Sum node fingerprint includes arity and body, not specific indices."""
        s1 = Sum(("i",), Binary("+", VarRef("x", ("i",)), Const(1.0)))
        s2 = Sum(("j",), Binary("+", VarRef("x", ("j",)), Const(1.0)))
        assert _derivative_structure_key(s1) == _derivative_structure_key(s2)

    def test_symbolref_normalized(self):
        """SymbolRef with different names → same key (normalized)."""
        a = SymbolRef("element_a")
        b = SymbolRef("element_b")
        assert _derivative_structure_key(a) == _derivative_structure_key(b)

    def test_symbolref_in_expr(self):
        """SymbolRef inside Binary doesn't affect structural key."""
        a = Binary("+", SymbolRef("x"), Const(1.0))
        b = Binary("+", SymbolRef("y"), Const(1.0))
        assert _derivative_structure_key(a) == _derivative_structure_key(b)


# ── _substitute_elements ─────────────────────────────────────────────


class TestSubstituteElements:
    """Test concrete element substitution in derivative ASTs."""

    def test_empty_subs(self):
        """Empty substitution dict → expression unchanged."""
        expr = ParamRef("pi", ("a", "b"))
        result = _substitute_elements(expr, {})
        assert result is expr  # identity, not copy

    def test_param_index_substitution(self):
        """Replace concrete index in ParamRef."""
        expr = ParamRef("pi", ("normal", "disrupted"))
        result = _substitute_elements(expr, {"normal": "disrupted"})
        assert result == ParamRef("pi", ("disrupted", "disrupted"))

    def test_nested_binary(self):
        """Substitution propagates through Binary nodes."""
        expr = Binary("*", ParamRef("b"), ParamRef("pi", ("a", "x")))
        result = _substitute_elements(expr, {"x": "y"})
        assert result == Binary("*", ParamRef("b"), ParamRef("pi", ("a", "y")))

    def test_unary_propagation(self):
        """Substitution propagates through Unary nodes."""
        expr = Unary("-", ParamRef("pi", ("old",)))
        result = _substitute_elements(expr, {"old": "new"})
        assert result == Unary("-", ParamRef("pi", ("new",)))

    def test_no_matching_indices(self):
        """No matching indices → expression unchanged."""
        expr = ParamRef("pi", ("a", "b"))
        result = _substitute_elements(expr, {"x": "y"})
        assert result is expr  # identity when no match

    def test_const_unchanged(self):
        """Const nodes are never modified."""
        expr = Const(42.0)
        result = _substitute_elements(expr, {"42": "99"})
        assert result is expr

    def test_varref_preserves_attribute(self):
        """VarRef substitution preserves the attribute field."""
        expr = VarRef("x", ("old",), "l")
        result = _substitute_elements(expr, {"old": "new"})
        assert result == VarRef("x", ("new",), "l")

    def test_symbolref_name_substitution(self):
        """SymbolRef name is substituted when it matches."""
        expr = SymbolRef("old_element")
        result = _substitute_elements(expr, {"old_element": "new_element"})
        assert result == SymbolRef("new_element")

    def test_symbolref_no_match(self):
        """SymbolRef unchanged when name doesn't match."""
        expr = SymbolRef("foo")
        result = _substitute_elements(expr, {"bar": "baz"})
        assert result is expr


# ── _subtract_and_cancel ─────────────────────────────────────────────


class TestSubtractAndCancel:
    """Test additive term collection and cancellation."""

    def test_identical_cancel_to_zero(self):
        """a - a = 0."""
        expr = ParamRef("x")
        result = _subtract_and_cancel(expr, expr)
        assert isinstance(result, Const) and result.value == 0.0

    def test_kronecker_delta_pattern(self):
        """(1 - b*pi) - (-(b*pi)) = 1.

        This is the core pattern from the markov model where the diagonal
        derivative is ``1 - b*pi(...)`` and the off-diagonal is ``-(b*pi(...))``.
        """
        bpi = Binary("*", ParamRef("b"), ParamRef("pi", ("a", "b", "c")))
        diag = Binary("-", Const(1.0), bpi)
        offdiag = Unary("-", bpi)
        result = _subtract_and_cancel(diag, offdiag)
        assert isinstance(result, Const) and result.value == 1.0

    def test_no_cancellation(self):
        """When terms don't match, nothing cancels."""
        a = ParamRef("x")
        b = ParamRef("y")
        result = _subtract_and_cancel(a, b)
        # Result should be x + (-(y)) or similar non-zero form
        assert not (isinstance(result, Const) and result.value == 0.0)

    def test_partial_cancellation(self):
        """(a + b) - a = b."""
        a = ParamRef("alpha")
        b = ParamRef("beta")
        ab = Binary("+", a, b)
        result = _subtract_and_cancel(ab, a)
        # The remaining term should be b with sign +1
        assert result == b

    def test_double_negation(self):
        """a - (-(a)) = 2*a (no cancellation)."""
        a = ParamRef("x")
        neg_a = Unary("-", a)
        result = _subtract_and_cancel(a, neg_a)
        # a - (-(a)) = a + a → two positive terms, no cancellation
        # Result should have both terms
        assert not (isinstance(result, Const) and result.value == 0.0)
