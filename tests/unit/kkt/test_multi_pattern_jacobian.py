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


# ── Multi-pattern correction workflow (CI-runnable) ──────────────────


class TestMultiPatternCorrectionWorkflow:
    """End-to-end unit test exercising the multi-pattern detection and
    correction logic using the same helper sequence as
    ``_add_indexed_jacobian_terms``: fingerprint → group → pair →
    substitute → subtract.

    This runs in CI (no external files) and catches regressions in the
    composed workflow that the integration test (skipped in CI) covers
    with the real markov model.
    """

    def test_markov_like_correction(self):
        """Simulate the markov diagonal/off-diagonal pattern.

        Setup: constraint constr(sp,j) references z(s,i,sp) both
        directly (Kronecker delta on diagonal) and inside a sum
        (off-diagonal).

        Diagonal derivative:  1 - b*pi(s,i,sp,j)
        Off-diagonal derivative:  -(b*pi(s,i,sp,j))

        Expected correction: diagonal - off-diagonal = Const(1.0)
        """
        bpi_diag = Binary("*", ParamRef("b"), ParamRef("pi", ("s1", "i1", "s1", "i1")))
        diag_deriv = Binary("-", Const(1.0), bpi_diag)

        bpi_off1 = Binary("*", ParamRef("b"), ParamRef("pi", ("s1", "i1", "s1", "i2")))
        off1_deriv = Unary("-", bpi_off1)

        bpi_off2 = Binary("*", ParamRef("b"), ParamRef("pi", ("s1", "i1", "s2", "i1")))
        off2_deriv = Unary("-", bpi_off2)

        # Step 1: Fingerprint — diagonal has different structure than off-diagonal
        diag_key = _derivative_structure_key(diag_deriv)
        off1_key = _derivative_structure_key(off1_deriv)
        off2_key = _derivative_structure_key(off2_deriv)

        assert diag_key != off1_key, "Diagonal and off-diagonal should differ"
        assert off1_key == off2_key, "Off-diagonal entries should match"

        # Step 2: Group by structure key — majority = off-diagonal (2), minority = diagonal (1)
        groups: dict[str, list[str]] = {}
        for label, key in [("diag", diag_key), ("off1", off1_key), ("off2", off2_key)]:
            groups.setdefault(key, []).append(label)
        sorted_groups = sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True)
        assert len(sorted_groups) == 2
        majority_labels = sorted_groups[0][1]
        minority_labels = sorted_groups[1][1]
        assert len(majority_labels) == 2  # off-diagonal is majority
        assert len(minority_labels) == 1  # diagonal is minority

        # Step 3: Pair — find a minority+majority entry sharing same var col.
        # In markov, diagonal (sp=s,j=i) and off-diagonal (sp=s,j!=i) share
        # the same z(s,i,sp) column.  Simulate by picking diag + off1.
        paired_min_eq_idx = ("s1", "i1")  # diagonal: constr(s1,i1)
        paired_maj_eq_idx = ("s1", "i2")  # off-diagonal: constr(s1,i2)

        # Step 4: Build element substitution for majority → minority alignment
        elem_sub: dict[str, str] = {}
        for ei in range(len(paired_min_eq_idx)):
            if paired_maj_eq_idx[ei] != paired_min_eq_idx[ei]:
                elem_sub[paired_maj_eq_idx[ei]] = paired_min_eq_idx[ei]
        assert elem_sub == {"i2": "i1"}

        # Step 5: Substitute in off-diagonal derivative to align at diagonal point
        # off1_deriv has pi(s1,i1,s1,i2) — after sub, pi(s1,i1,s1,i1)
        maj_aligned = _substitute_elements(off1_deriv, elem_sub)
        # After substitution, indices should match diagonal's indices
        assert isinstance(maj_aligned, Unary)
        inner = maj_aligned.child
        assert isinstance(inner, Binary)
        pi_ref = inner.right
        assert isinstance(pi_ref, ParamRef)
        assert pi_ref.indices == ("s1", "i1", "s1", "i1")

        # Step 6: Subtract — correction = diag - aligned_off = 1
        correction = _subtract_and_cancel(diag_deriv, maj_aligned)
        assert isinstance(correction, Const)
        assert correction.value == 1.0

    def test_same_pattern_no_correction(self):
        """When all entries share the same structure, no correction needed."""
        d1 = Unary("-", Binary("*", ParamRef("b"), ParamRef("pi", ("a", "b"))))
        d2 = Unary("-", Binary("*", ParamRef("b"), ParamRef("pi", ("c", "d"))))
        d3 = Unary("-", Binary("*", ParamRef("b"), ParamRef("pi", ("e", "f"))))

        k1 = _derivative_structure_key(d1)
        k2 = _derivative_structure_key(d2)
        k3 = _derivative_structure_key(d3)

        # All same structure → single group → no multi-pattern detection
        assert k1 == k2 == k3
        groups: dict[str, int] = {}
        for k in [k1, k2, k3]:
            groups[k] = groups.get(k, 0) + 1
        assert len(groups) == 1, "Single pattern should produce one group"

    def test_unsafe_substitution_skips_correction(self):
        """When elem_sub keys collide with var indices, correction is skipped."""
        # Simulate: eq indices differ at "i1" → "i2", but var also uses "i1"
        paired_maj_eq_idx = ("s1", "i1")
        paired_min_eq_idx = ("s1", "i2")
        var_indices = ("x1", "i1")  # "i1" appears in var indices!

        elem_sub: dict[str, str] = {}
        for ei in range(len(paired_min_eq_idx)):
            if paired_maj_eq_idx[ei] != paired_min_eq_idx[ei]:
                elem_sub[paired_maj_eq_idx[ei]] = paired_min_eq_idx[ei]

        var_labels = {str(v) for v in var_indices}
        unsafe = bool(elem_sub and elem_sub.keys() & var_labels)
        assert unsafe, "Should detect collision between sub keys and var labels"
