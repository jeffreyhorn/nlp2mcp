"""Tests for alias-aware differentiation (#1111).

Verifies that the AD engine correctly handles aliases between index sets
during symbolic differentiation, producing sameas() guards for free alias
indices while returning 0 for bound alias indices (from enclosing Sum/Prod).

Key test patterns:
- Free alias index → sameas() guard
- Bound alias index (sum-bound) → 0 (independent iteration)
- Alias chain resolution → same root set detection
- No aliases → identical derivatives (backward compatibility)
- Multi-dimensional alias matching
"""

from __future__ import annotations

import pytest

from src.ad.derivative_rules import (
    _alias_match,
    _same_root_set,
    differentiate_expr,
)
from src.config import Config
from src.ir.ast import Binary, Call, Const, IndexOffset, Sum, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, SetDef

pytestmark = pytest.mark.unit


# ============================================================================
# Helpers
# ============================================================================


def _make_config_with_aliases(*alias_defs: AliasDef, sets: list[SetDef] | None = None) -> Config:
    """Build a Config with a ModelIR containing the given aliases and sets."""
    model_ir = ModelIR()
    if sets:
        for s in sets:
            model_ir.add_set(s)
    for a in alias_defs:
        model_ir.add_alias(a)
    return Config(model_ir=model_ir)


# ============================================================================
# _same_root_set tests
# ============================================================================


class TestSameRootSet:
    """Tests for _same_root_set() alias chain resolution."""

    def test_same_name_returns_true(self):
        aliases = {}
        assert _same_root_set("n", "n", aliases) is True

    def test_direct_alias_returns_true(self):
        aliases = {"np": AliasDef("np", "n")}
        assert _same_root_set("n", "np", aliases) is True
        assert _same_root_set("np", "n", aliases) is True

    def test_chain_alias_returns_true(self):
        aliases = {
            "np": AliasDef("np", "n"),
            "npp": AliasDef("npp", "np"),
        }
        assert _same_root_set("n", "npp", aliases) is True
        assert _same_root_set("npp", "n", aliases) is True

    def test_unrelated_returns_false(self):
        aliases = {"np": AliasDef("np", "n")}
        assert _same_root_set("n", "k", aliases) is False

    def test_case_insensitive(self):
        """Root set comparison is case-insensitive (resolve returns .lower()).

        Note: case-insensitive dict *lookup* is provided by ModelIR.aliases
        (CaseInsensitiveDict). Here we test that the resolved root names are
        compared case-insensitively — "N" and "n" resolve to the same root.
        """
        aliases = {"np": AliasDef("np", "N")}  # target is uppercase "N"
        assert _same_root_set("n", "np", aliases) is True

    def test_plain_string_aliases(self):
        """Some test setups use plain strings instead of AliasDef objects."""
        aliases = {"np": "n"}
        assert _same_root_set("n", "np", aliases) is True


# ============================================================================
# _alias_match tests
# ============================================================================


class TestAliasMatch:
    """Tests for _alias_match() index matching with aliases."""

    def test_exact_match_returns_one(self):
        aliases = {"np": AliasDef("np", "n")}
        result = _alias_match(("n", "k"), ("n", "k"), aliases, frozenset())
        assert isinstance(result, Const) and result.value == 1.0

    def test_free_alias_produces_sameas(self):
        """x(np,k) vs wrt x(n,k): np is free → sameas(np,n)."""
        aliases = {"np": AliasDef("np", "n")}
        result = _alias_match(("np", "k"), ("n", "k"), aliases, frozenset())
        assert result is not None
        assert isinstance(result, Call)
        assert result.func == "sameas"

    def test_bound_alias_returns_none(self):
        """x(np,k) vs wrt x(n,k): np is bound → None (no match)."""
        aliases = {"np": AliasDef("np", "n")}
        result = _alias_match(("np", "k"), ("n", "k"), aliases, frozenset({"np"}))
        assert result is None

    def test_length_mismatch_returns_none(self):
        aliases = {"np": AliasDef("np", "n")}
        result = _alias_match(("np",), ("n", "k"), aliases, frozenset())
        assert result is None

    def test_unrelated_indices_returns_none(self):
        aliases = {"np": AliasDef("np", "n")}
        result = _alias_match(("i",), ("j",), aliases, frozenset())
        assert result is None

    def test_multi_alias_produces_product(self):
        """Two alias dimensions → sameas * sameas."""
        aliases = {
            "np": AliasDef("np", "n"),
            "kp": AliasDef("kp", "k"),
        }
        result = _alias_match(("np", "kp"), ("n", "k"), aliases, frozenset())
        assert result is not None
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_index_offset_not_alias_matched(self):
        """IndexOffset dimensions must not alias-match by base name alone.

        x(t+1) vs x(t) should return None, not Const(1.0).
        """
        aliases = {"tp": AliasDef("tp", "t")}
        offset = IndexOffset("t", Const(1.0), False)
        # Same base but different structure: t+1 vs t
        result = _alias_match((offset,), ("t",), aliases, frozenset())
        assert result is None

    def test_identical_index_offset_matches(self):
        """Structurally identical IndexOffsets should match."""
        aliases = {"tp": AliasDef("tp", "t")}
        offset = IndexOffset("t", Const(1.0), False)
        result = _alias_match((offset,), (offset,), aliases, frozenset())
        assert isinstance(result, Const) and result.value == 1.0


# ============================================================================
# differentiate_expr with alias-aware matching
# ============================================================================


class TestAliasDifferentiation:
    """Integration tests for alias-aware differentiation."""

    def test_free_alias_varref(self):
        """d/d(x(n,k)) of x(np,k) where Alias(n,np) → sameas(np,n)."""
        config = _make_config_with_aliases(AliasDef("np", "n"))
        expr = VarRef("x", ("np", "k"))
        result = differentiate_expr(expr, "x", ("n", "k"), config)
        # Should produce sameas(np, n) — a Call node
        assert isinstance(result, Call)
        assert result.func == "sameas"

    def test_bound_alias_in_sum_returns_zero(self):
        """d/d(p(i)) of sum(j, p(j)) where Alias(i,j), j is sum-bound → sum of zeros.

        When j is bound by the enclosing sum, p(j) should NOT alias-match p(i)
        because j is an independent iteration variable. The sum preserves and
        each body derivative is 0, giving sum(j, 0).

        Note: The sum collapse mechanism handles concrete instance matching
        (e.g., p('a')), not symbolic alias matching. Symbolic alias matching
        in sum contexts is a separate concern (sum collapse with alias awareness)
        that may be addressed in future work.
        """
        config = _make_config_with_aliases(
            AliasDef("j", "i"),
            sets=[SetDef("i", ["a", "b", "c"])],
        )
        # sum(j, p(j)) differentiated w.r.t. p(i)
        # j is bound by the sum → alias match returns None → body derivative is 0
        expr = Sum(("j",), VarRef("p", ("j",)))
        result = differentiate_expr(expr, "p", ("i",), config)
        # Result: sum(j, 0) — the sum is preserved with zero body derivative
        assert isinstance(result, Sum)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_dispatch_pattern_no_spurious_match(self):
        """dispatch: Alias(i,j); sum((i,j), p(i)*b(i,j)*p(j)) w.r.t. p(i).

        p(j) should NOT match p(i) because j is bound by the sum.
        The derivative of p(j) w.r.t. p(i) should be 0.
        """
        config = _make_config_with_aliases(
            AliasDef("j", "i"),
            sets=[SetDef("i", ["a", "b", "c"])],
        )
        # Just test the inner VarRef: d/d(p(i)) of p(j) with j in bound_indices
        expr = VarRef("p", ("j",))
        result = differentiate_expr(expr, "p", ("i",), config, bound_indices=frozenset({"j"}))
        assert isinstance(result, Const) and result.value == 0.0

    def test_no_alias_unchanged(self):
        """Without aliases, behavior is identical to before."""
        config = Config()  # No model_ir
        expr = VarRef("x", ("i",))
        # Exact match
        result = differentiate_expr(expr, "x", ("i",), config)
        assert isinstance(result, Const) and result.value == 1.0
        # Mismatch
        result = differentiate_expr(expr, "x", ("j",), config)
        assert isinstance(result, Const) and result.value == 0.0

    def test_no_alias_empty_aliases(self):
        """With empty aliases dict, no alias matching attempted."""
        model_ir = ModelIR()
        config = Config(model_ir=model_ir)
        expr = VarRef("x", ("i",))
        result = differentiate_expr(expr, "x", ("j",), config)
        assert isinstance(result, Const) and result.value == 0.0

    def test_alias_in_sum_body_free(self):
        """sum(k, x(np,k)) w.r.t. x(n,k1) where Alias(n,np).

        np is NOT a sum index (k is), so np is free.
        The sum collapses at k=k1, producing sameas(np,n).
        """
        config = _make_config_with_aliases(
            AliasDef("np", "n"),
            sets=[SetDef("k", ["k1", "k2"])],
        )
        expr = Sum(("k",), VarRef("x", ("np", "k")))
        result = differentiate_expr(expr, "x", ("n", "k1"), config)
        # Sum collapses (k matches k1), body derivative of x(np,k) w.r.t. x(n,k)
        # should produce sameas(np,n) since np is free
        assert isinstance(result, Call)
        assert result.func == "sameas"

    def test_alias_through_binary_expr(self):
        """d/d(x(n)) of (2*x(np)) where Alias(n,np) → 2 * sameas(np,n)."""
        config = _make_config_with_aliases(AliasDef("np", "n"))
        expr = Binary("*", Const(2.0), VarRef("x", ("np",)))
        result = differentiate_expr(expr, "x", ("n",), config)
        # Product rule: 0 * x(np) + 2 * sameas(np,n)
        # After simplification (if any): 2 * sameas(np,n)
        # Without simplification: Binary("+", Binary("*", VarRef(...), Const(0)), Binary("*", Const(2), sameas))
        assert result is not None
        # The result should contain a sameas call somewhere
        assert _contains_sameas(result)


def _contains_sameas(expr) -> bool:
    """Check if expression tree contains a sameas() Call."""
    if isinstance(expr, Call) and expr.func == "sameas":
        return True
    if isinstance(expr, Binary):
        return _contains_sameas(expr.left) or _contains_sameas(expr.right)
    return False
