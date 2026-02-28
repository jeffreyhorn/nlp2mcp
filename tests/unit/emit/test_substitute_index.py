"""Unit tests for _substitute_index() in emit_gams.py.

Tests AST-level index substitution used by section 2c (diagonal emptiness check)
for complementarity equations with same-set indices.
"""

from src.emit.emit_gams import _substitute_index
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    IndexOffset,
    MultiplierRef,
    ParamRef,
    Prod,
    SetAttrRef,
    SetMembershipTest,
    SubsetIndex,
    Sum,
    Unary,
    VarRef,
)


class TestSubstituteIndexBasic:
    """Basic substitution tests for leaf nodes."""

    def test_const_unchanged(self):
        expr = Const(3.14)
        result = _substitute_index(expr, "i", "j")
        assert result == Const(3.14)

    def test_varref_substitutes_matching_index(self):
        expr = VarRef("w", ("j",))
        result = _substitute_index(expr, "j", "i")
        assert result == VarRef("w", ("i",))

    def test_varref_preserves_non_matching_index(self):
        expr = VarRef("w", ("k",))
        result = _substitute_index(expr, "j", "i")
        assert result == VarRef("w", ("k",))

    def test_varref_multi_index(self):
        expr = VarRef("x", ("i", "j"))
        result = _substitute_index(expr, "j", "i")
        assert result == VarRef("x", ("i", "i"))

    def test_varref_preserves_attribute(self):
        expr = VarRef("x", ("j",), attribute="l")
        result = _substitute_index(expr, "j", "i")
        assert result == VarRef("x", ("i",), attribute="l")

    def test_paramref_substitutes(self):
        expr = ParamRef("theta", ("j",))
        result = _substitute_index(expr, "j", "i")
        assert result == ParamRef("theta", ("i",))

    def test_multiplierref_substitutes(self):
        expr = MultiplierRef("lam_ic", ("i", "j"))
        result = _substitute_index(expr, "j", "i")
        assert result == MultiplierRef("lam_ic", ("i", "i"))

    def test_set_attr_ref_substitutes(self):
        expr = SetAttrRef("j", "ord")
        result = _substitute_index(expr, "j", "i")
        assert result == SetAttrRef("i", "ord")

    def test_set_attr_ref_no_match(self):
        expr = SetAttrRef("k", "card")
        result = _substitute_index(expr, "j", "i")
        assert result == SetAttrRef("k", "card")


class TestSubstituteIndexComposite:
    """Tests for composite expression nodes."""

    def test_binary_both_sides(self):
        # w(j) - theta(j)*x(j)
        expr = Binary(
            "-",
            VarRef("w", ("j",)),
            Binary("*", ParamRef("theta", ("j",)), VarRef("x", ("j",))),
        )
        result = _substitute_index(expr, "j", "i")
        expected = Binary(
            "-",
            VarRef("w", ("i",)),
            Binary("*", ParamRef("theta", ("i",)), VarRef("x", ("i",))),
        )
        assert result == expected

    def test_unary(self):
        expr = Unary("-", VarRef("x", ("j",)))
        result = _substitute_index(expr, "j", "i")
        assert result == Unary("-", VarRef("x", ("i",)))

    def test_call_substitutes_args(self):
        # sqrt(x(j))
        expr = Call("sqrt", (VarRef("x", ("j",)),))
        result = _substitute_index(expr, "j", "i")
        assert result == Call("sqrt", (VarRef("x", ("i",)),))

    def test_dollar_conditional(self):
        # x(j) $ (ord(j) <= 5)
        expr = DollarConditional(
            VarRef("x", ("j",)),
            Binary("<=", SetAttrRef("j", "ord"), Const(5.0)),
        )
        result = _substitute_index(expr, "j", "i")
        expected = DollarConditional(
            VarRef("x", ("i",)),
            Binary("<=", SetAttrRef("i", "ord"), Const(5.0)),
        )
        assert result == expected


class TestSubstituteIndexAggregation:
    """Tests for Sum/Prod with bound-variable shadowing."""

    def test_sum_substitutes_free_index(self):
        # sum(k, x(j,k))  -- j is free, k is bound
        expr = Sum(("k",), VarRef("x", ("j", "k")))
        result = _substitute_index(expr, "j", "i")
        assert result == Sum(("k",), VarRef("x", ("i", "k")))

    def test_sum_skips_bound_index(self):
        # sum(j, x(j))  -- j is the bound variable, should NOT substitute
        expr = Sum(("j",), VarRef("x", ("j",)))
        result = _substitute_index(expr, "j", "i")
        # Should be unchanged because j is bound by the sum
        assert result == expr

    def test_sum_with_condition(self):
        # sum(k, x(j,k) $ (ord(j) > 1))
        expr = Sum(
            ("k",),
            VarRef("x", ("j", "k")),
            Binary(">", SetAttrRef("j", "ord"), Const(1.0)),
        )
        result = _substitute_index(expr, "j", "i")
        expected = Sum(
            ("k",),
            VarRef("x", ("i", "k")),
            Binary(">", SetAttrRef("i", "ord"), Const(1.0)),
        )
        assert result == expected

    def test_prod_skips_bound_index(self):
        expr = Prod(("j",), VarRef("x", ("j",)))
        result = _substitute_index(expr, "j", "i")
        assert result == expr

    def test_prod_substitutes_free_index(self):
        expr = Prod(("k",), VarRef("x", ("j", "k")))
        result = _substitute_index(expr, "j", "i")
        assert result == Prod(("k",), VarRef("x", ("i", "k")))


class TestSubstituteIndexOffset:
    """Tests for IndexOffset within VarRef indices and as standalone."""

    def test_index_offset_in_varref(self):
        # w(j+1) -> w(i+1)
        offset = IndexOffset("j", Const(1.0), False)
        expr = VarRef("w", (offset,))
        result = _substitute_index(expr, "j", "i")
        expected = VarRef("w", (IndexOffset("i", Const(1.0), False),))
        assert result == expected

    def test_index_offset_non_matching_base(self):
        # w(k+1) unchanged when substituting j->i
        offset = IndexOffset("k", Const(1.0), False)
        expr = VarRef("w", (offset,))
        result = _substitute_index(expr, "j", "i")
        assert result == expr

    def test_index_offset_with_expr_offset(self):
        # x(j + ord(j)) -> x(i + ord(i))
        offset = IndexOffset("j", SetAttrRef("j", "ord"), False)
        expr = VarRef("x", (offset,))
        result = _substitute_index(expr, "j", "i")
        expected = VarRef("x", (IndexOffset("i", SetAttrRef("i", "ord"), False),))
        assert result == expected

    def test_standalone_index_offset(self):
        expr = IndexOffset("j", Const(2.0), True)
        result = _substitute_index(expr, "j", "i")
        assert result == IndexOffset("i", Const(2.0), True)

    def test_standalone_index_offset_no_match(self):
        expr = IndexOffset("k", Const(2.0), False)
        result = _substitute_index(expr, "j", "i")
        assert result == expr


class TestSubstituteIndexSpecial:
    """Tests for SubsetIndex, SetMembershipTest, and edge cases."""

    def test_subset_index(self):
        expr = SubsetIndex("s", ("i", "j"))
        result = _substitute_index(expr, "j", "i")
        assert result == SubsetIndex("s", ("i", "i"))

    def test_subset_index_no_match(self):
        expr = SubsetIndex("s", ("i", "k"))
        result = _substitute_index(expr, "j", "i")
        assert result == expr

    def test_set_membership_test(self):
        # s(j)
        expr = SetMembershipTest("s", (VarRef("dummy", ("j",)),))
        result = _substitute_index(expr, "j", "i")
        expected = SetMembershipTest("s", (VarRef("dummy", ("i",)),))
        assert result == expected


class TestSubstituteIndexDiagonalPattern:
    """Tests for the specific diagonal emptiness pattern from section 2c.

    The IC constraint: w(i) - theta(i)*x(i) =G= w(j) - theta(i)*x(j)
    When substituting j->i, LHS stays the same, RHS becomes identical to LHS,
    making the equation trivially true (0 >= 0).
    """

    def test_ic_constraint_becomes_trivial(self):
        """After substituting j->i, LHS == RHS (structural equality)."""
        # LHS: w(i) - theta(i)*x(i)
        lhs = Binary(
            "-",
            VarRef("w", ("i",)),
            Binary("*", ParamRef("theta", ("i",)), VarRef("x", ("i",))),
        )
        # RHS: w(j) - theta(i)*x(j)
        rhs = Binary(
            "-",
            VarRef("w", ("j",)),
            Binary("*", ParamRef("theta", ("i",)), VarRef("x", ("j",))),
        )
        subst_rhs = _substitute_index(rhs, "j", "i")
        assert subst_rhs == lhs

    def test_subtraction_pattern_a_minus_a(self):
        """LHS - RHS becomes Binary('-', A, A) when equation is trivial on diagonal."""
        # Equation body as emitted: (w(i) - theta(i)*x(i)) - (w(j) - theta(i)*x(j)) =G= 0
        a_expr = Binary(
            "-",
            VarRef("w", ("i",)),
            Binary("*", ParamRef("theta", ("i",)), VarRef("x", ("i",))),
        )
        body_lhs = Binary(
            "-",
            a_expr,
            Binary(
                "-",
                VarRef("w", ("j",)),
                Binary("*", ParamRef("theta", ("i",)), VarRef("x", ("j",))),
            ),
        )
        body_rhs = Const(0.0)

        subst_lhs = _substitute_index(body_lhs, "j", "i")
        subst_rhs = _substitute_index(body_rhs, "j", "i")

        # After substitution, the subtracted part becomes identical to the minuend
        assert isinstance(subst_lhs, Binary)
        assert subst_lhs.op == "-"
        assert subst_lhs.left == subst_lhs.right
        assert subst_rhs == Const(0.0)
