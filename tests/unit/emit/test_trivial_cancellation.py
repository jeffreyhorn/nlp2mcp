"""Unit tests for _is_trivial_after_cancellation() and _contains_variable() in emit_gams.py.

Tests AST-level additive term cancellation used by section 2c (diagonal emptiness check)
for complementarity equations where VarRef terms cancel on the diagonal.

Also tests _contains_variable() recursive subtree traversal for VarRef/MultiplierRef.
"""

import pytest

from src.emit.emit_gams import (
    _collect_additive_terms,
    _contains_variable,
    _is_trivial_after_cancellation,
)
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    IndexOffset,
    LhsConditionalAssign,
    MultiplierRef,
    ParamRef,
    Prod,
    SetMembershipTest,
    Sum,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef


@pytest.mark.unit
class TestCollectAdditiveTerms:
    """Tests for _collect_additive_terms() helper."""

    def test_single_term(self):
        expr = VarRef("x", ("i",))
        result = _collect_additive_terms(expr)
        assert len(result) == 1
        assert result[0] == (1, expr)

    def test_addition(self):
        a = VarRef("x", ("i",))
        b = ParamRef("p", ("i",))
        expr = Binary("+", a, b)
        result = _collect_additive_terms(expr)
        assert len(result) == 2
        assert result[0] == (1, a)
        assert result[1] == (1, b)

    def test_subtraction(self):
        a = VarRef("x", ("i",))
        b = VarRef("x", ("j",))
        expr = Binary("-", a, b)
        result = _collect_additive_terms(expr)
        assert len(result) == 2
        assert result[0] == (1, a)
        assert result[1] == (-1, b)

    def test_unary_minus(self):
        a = VarRef("x", ("i",))
        expr = Unary("-", a)
        result = _collect_additive_terms(expr)
        assert len(result) == 1
        assert result[0] == (-1, a)

    def test_neg_one_multiply(self):
        a = VarRef("x", ("i",))
        expr = Binary("*", Const(-1.0), a)
        result = _collect_additive_terms(expr)
        assert len(result) == 1
        assert result[0] == (-1, a)

    def test_spatequ_pattern(self):
        """p(r,c) + TCost(r,r,c) - p(r,c) flattens to 3 terms."""
        p_rc = VarRef("P", ("r", "c"))
        tcost = ParamRef("TCost", ("r", "r", "c"))
        expr = Binary("-", Binary("+", p_rc, tcost), p_rc)
        result = _collect_additive_terms(expr)
        assert len(result) == 3
        signs = [s for s, _ in result]
        assert signs == [1, 1, -1]


@pytest.mark.unit
class TestContainsVariable:
    """Tests for _contains_variable() recursive traversal."""

    def test_varref(self):
        assert _contains_variable(VarRef("x", ())) is True

    def test_multiplier_ref(self):
        assert _contains_variable(MultiplierRef("lam_eq", ())) is True

    def test_const(self):
        assert _contains_variable(Const(1.0)) is False

    def test_paramref(self):
        assert _contains_variable(ParamRef("p", ("i",))) is False

    def test_nested_in_call(self):
        expr = Call("exp", (VarRef("x", ()),))
        assert _contains_variable(expr) is True

    def test_nested_in_binary(self):
        expr = Binary("*", Const(2.0), VarRef("x", ()))
        assert _contains_variable(expr) is True

    def test_sum_body(self):
        expr = Sum(index_sets=("i",), body=VarRef("x", ("i",)))
        assert _contains_variable(expr) is True

    def test_sum_condition_with_varref(self):
        """VarRef in Sum condition must be detected."""
        expr = Sum(
            index_sets=("i",),
            body=Const(1.0),
            condition=VarRef("flag", ("i",)),
        )
        assert _contains_variable(expr) is True

    def test_prod_condition_with_varref(self):
        """VarRef in Prod condition must be detected."""
        expr = Prod(
            index_sets=("i",),
            body=ParamRef("a", ("i",)),
            condition=VarRef("active", ("i",)),
        )
        assert _contains_variable(expr) is True

    def test_dollar_conditional_condition_with_varref(self):
        """VarRef in DollarConditional condition must be detected."""
        expr = DollarConditional(
            value_expr=ParamRef("p", ("i",)),
            condition=VarRef("x", ("i",)),
        )
        assert _contains_variable(expr) is True

    def test_dollar_conditional_both_clean(self):
        """No VarRef anywhere in DollarConditional."""
        expr = DollarConditional(
            value_expr=ParamRef("p", ("i",)),
            condition=ParamRef("mask", ("i",)),
        )
        assert _contains_variable(expr) is False

    def test_sum_no_condition_clean(self):
        """Sum with clean body and no condition."""
        expr = Sum(index_sets=("i",), body=ParamRef("a", ("i",)))
        assert _contains_variable(expr) is False

    def test_index_offset_with_varref_in_offset(self):
        """VarRef nested in IndexOffset offset must be detected."""
        idx = IndexOffset(base="i", offset=VarRef("n", ()), circular=False)
        expr = ParamRef("p", (idx,))
        assert _contains_variable(expr) is True

    def test_index_offset_without_varref(self):
        """IndexOffset with Const offset — no variable."""
        idx = IndexOffset(base="i", offset=Const(1), circular=False)
        expr = ParamRef("p", (idx,))
        assert _contains_variable(expr) is False

    def test_set_membership_test_with_varref(self):
        """VarRef in SetMembershipTest indices must be detected."""
        expr = SetMembershipTest(set_name="s", indices=(VarRef("x", ()),))
        assert _contains_variable(expr) is True

    def test_set_membership_test_clean(self):
        """SetMembershipTest with only ParamRef indices — no variable."""
        expr = SetMembershipTest(set_name="s", indices=(ParamRef("p", ()),))
        assert _contains_variable(expr) is False

    def test_lhs_conditional_assign_with_varref_in_rhs(self):
        """VarRef in LhsConditionalAssign rhs must be detected."""
        expr = LhsConditionalAssign(
            rhs=VarRef("x", ("i",)),
            condition=ParamRef("mask", ("i",)),
        )
        assert _contains_variable(expr) is True

    def test_lhs_conditional_assign_clean(self):
        """LhsConditionalAssign with no variables — clean."""
        expr = LhsConditionalAssign(
            rhs=ParamRef("p", ("i",)),
            condition=ParamRef("mask", ("i",)),
        )
        assert _contains_variable(expr) is False


@pytest.mark.unit
class TestIsTrivialAfterCancellation:
    """Tests for _is_trivial_after_cancellation()."""

    def test_perfect_cancellation(self):
        """p(r,c) - p(r,c) =G= 0 → trivially zero (all terms cancel)."""
        p = VarRef("P", ("r", "c"))
        lhs = Binary("-", p, p)
        rhs = Const(0.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is True

    def test_spatequ_pattern_with_zero_param_data(self):
        """p(r,c) + TCost(r,r,c) - p(r,c) =G= 0 — trivial when TCost diagonal is 0."""
        p = VarRef("P", ("r", "c"))
        tcost = ParamRef("TCost", ("r", "r", "c"))
        lhs = Binary("-", Binary("+", p, tcost), p)
        rhs = Const(0.0)

        model_ir = ModelIR()
        tcost_def = ParameterDef(name="TCost", domain=("r", "rr", "c"))
        # Diagonal entries (r=rr) are zero
        tcost_def.values[("A", "A", "X")] = 0
        tcost_def.values[("B", "B", "Y")] = 0
        # Off-diagonal entries can be nonzero
        tcost_def.values[("A", "B", "X")] = 5.0
        model_ir.params["TCost"] = tcost_def

        assert _is_trivial_after_cancellation(lhs, rhs, model_ir=model_ir) is True

    def test_spatequ_pattern_with_nonzero_diagonal_param(self):
        """p(r,c) + TCost(r,r,c) - p(r,c) =G= 0 — NOT trivial when diagonal TCost != 0."""
        p = VarRef("P", ("r", "c"))
        tcost = ParamRef("TCost", ("r", "r", "c"))
        lhs = Binary("-", Binary("+", p, tcost), p)
        rhs = Const(0.0)

        model_ir = ModelIR()
        tcost_def = ParameterDef(name="TCost", domain=("r", "rr", "c"))
        tcost_def.values[("A", "A", "X")] = 3.0  # Nonzero diagonal!
        model_ir.params["TCost"] = tcost_def

        assert _is_trivial_after_cancellation(lhs, rhs, model_ir=model_ir) is False

    def test_remaining_varref_not_trivial(self):
        """x(i) + p(i) =G= 0 — VarRef remains, not trivial."""
        lhs = Binary("+", VarRef("x", ("i",)), ParamRef("p", ("i",)))
        rhs = Const(0.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is False

    def test_remaining_nonzero_const_not_trivial(self):
        """x(i) - x(i) + 5 =G= 0 — Const(5) remains, not trivial."""
        x = VarRef("x", ("i",))
        lhs = Binary("+", Binary("-", x, x), Const(5.0))
        rhs = Const(0.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is False

    def test_rhs_nonzero_not_trivial(self):
        """x(i) - x(i) =G= 1 — RHS is nonzero, not trivial."""
        x = VarRef("x", ("i",))
        lhs = Binary("-", x, x)
        rhs = Const(1.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is False

    def test_nested_varref_in_call_not_trivial(self):
        """exp(x(i)) - exp(x(i)) + p(i) =G= 0 — Call terms cancel but p(i) remains."""
        exp_x = Call("exp", (VarRef("x", ("i",)),))
        lhs = Binary("+", Binary("-", exp_x, exp_x), ParamRef("p", ("i",)))
        rhs = Const(0.0)
        # Without model_ir, ParamRef can't be verified as zero
        assert _is_trivial_after_cancellation(lhs, rhs) is False

    def test_no_model_ir_paramref_not_trivial(self):
        """Without model_ir, remaining ParamRef is not provably zero."""
        p = VarRef("P", ("r", "c"))
        tcost = ParamRef("TCost", ("r", "r", "c"))
        lhs = Binary("-", Binary("+", p, tcost), p)
        rhs = Const(0.0)
        # No model_ir provided — can't verify param data
        assert _is_trivial_after_cancellation(lhs, rhs) is False

    def test_remaining_const_zero_is_trivial(self):
        """x(i) - x(i) + 0 =G= 0 — only Const(0) remains, trivially zero."""
        x = VarRef("x", ("i",))
        lhs = Binary("+", Binary("-", x, x), Const(0.0))
        rhs = Const(0.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is True

    def test_paramref_no_repeated_indices_all_zero(self):
        """ParamRef with no repeated indices — falls back to checking ALL entries are zero."""
        x = VarRef("x", ("i",))
        p = ParamRef("p", ("i",))
        lhs = Binary("+", Binary("-", x, x), p)
        rhs = Const(0.0)

        model_ir = ModelIR()
        pdef = ParameterDef(name="p", domain=("i",))
        pdef.values[("a",)] = 0
        pdef.values[("b",)] = 0
        model_ir.params["p"] = pdef

        assert _is_trivial_after_cancellation(lhs, rhs, model_ir=model_ir) is True

    def test_paramref_no_repeated_indices_some_nonzero(self):
        """ParamRef with no repeated indices and nonzero entries — not trivial."""
        x = VarRef("x", ("i",))
        p = ParamRef("p", ("i",))
        lhs = Binary("+", Binary("-", x, x), p)
        rhs = Const(0.0)

        model_ir = ModelIR()
        pdef = ParameterDef(name="p", domain=("i",))
        pdef.values[("a",)] = 0
        pdef.values[("b",)] = 7.0
        model_ir.params["p"] = pdef

        assert _is_trivial_after_cancellation(lhs, rhs, model_ir=model_ir) is False

    def test_const_int_vs_float_cancellation(self):
        """Const(5) and Const(5.0) must cancel despite different repr().

        Frozen dataclass equality: Const(5) == Const(5.0) is True,
        but repr(Const(5)) != repr(Const(5.0)).  Using the Expr object
        itself as dict key ensures correct cancellation.
        """
        # a + Const(5) - Const(5.0) =G= 0 — the constants should cancel
        a = VarRef("a", ("i",))
        lhs = Binary("-", Binary("+", a, Const(5)), Binary("+", a, Const(5.0)))
        rhs = Const(0.0)
        assert _is_trivial_after_cancellation(lhs, rhs) is True
