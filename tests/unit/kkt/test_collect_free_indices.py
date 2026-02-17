"""Unit tests for _collect_free_indices() utility function.

Issue #670: Detects uncontrolled set indices in stationarity derivative
expressions that need to be wrapped in Sum nodes to avoid GAMS Error 149.
"""

import pytest

from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    MultiplierRef,
    ParamRef,
    Prod,
    SetMembershipTest,
    Sum,
    SymbolRef,
    Unary,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef
from src.kkt.stationarity import _collect_free_indices

pytestmark = pytest.mark.unit


def _make_model(*set_names: str, aliases: dict[str, str] | None = None) -> ModelIR:
    """Build a minimal ModelIR with the given set names registered."""
    model = ModelIR()
    for name in set_names:
        model.sets[name] = SetDef(name=name, domain=(), members=None)
    if aliases:
        for alias, original in aliases.items():
            model.aliases[alias] = original
    return model


class TestCollectFreeIndicesBasic:
    """Basic cases: single refs, no sums."""

    def test_empty_expr_returns_empty(self):
        model = _make_model("n", "k")
        assert _collect_free_indices(Const(1.0), model) == set()

    def test_paramref_with_known_index(self):
        model = _make_model("n", "np")
        expr = ParamRef("a", ("n", "np"))
        assert _collect_free_indices(expr, model) == {"n", "np"}

    def test_varref_with_known_index(self):
        model = _make_model("n", "k")
        expr = VarRef("x", ("n", "k"))
        assert _collect_free_indices(expr, model) == {"n", "k"}

    def test_literal_string_not_a_set_excluded(self):
        """Quoted element labels like 'domestic' are not set names — excluded."""
        model = _make_model("c", "s")
        expr = ParamRef("p", ("c", "domestic"))
        assert _collect_free_indices(expr, model) == {"c"}

    def test_unknown_index_excluded(self):
        """Index names not registered as sets or aliases are excluded."""
        model = _make_model("n")
        expr = ParamRef("a", ("n", "xyz"))
        assert _collect_free_indices(expr, model) == {"n"}

    def test_alias_counted_as_free(self):
        """Alias names (like 'np' aliasing 'n') are recognised as set indices."""
        model = _make_model("n", aliases={"np": "n"})
        expr = ParamRef("w", ("n", "np"))
        assert _collect_free_indices(expr, model) == {"n", "np"}

    def test_multiplierref_with_known_index(self):
        """MultiplierRef indices are walked the same as VarRef/ParamRef."""
        model = _make_model("n", "k")
        expr = MultiplierRef("nu_eq", ("n", "k"))
        assert _collect_free_indices(expr, model) == {"n", "k"}

    def test_multiplierref_partial_known_indices(self):
        """MultiplierRef with one known set index and one literal label."""
        model = _make_model("k")
        expr = MultiplierRef("nu_eq", ("k", "domestic"))
        assert _collect_free_indices(expr, model) == {"k"}

    def test_multiplierref_bound_by_sum(self):
        """MultiplierRef index bound by enclosing Sum is not free."""
        model = _make_model("n", "k")
        inner = MultiplierRef("nu_eq", ("n", "k"))
        expr = Sum(("k",), inner)
        assert _collect_free_indices(expr, model) == {"n"}


class TestCollectFreeIndicesWithSums:
    """Sum-bound indices must not be counted as free."""

    def test_sum_bound_index_excluded(self):
        """An index bound by an enclosing Sum is not free."""
        model = _make_model("n", "np", "k")
        inner = ParamRef("w", ("n", "np", "k"))
        expr = Sum(("np",), inner)
        # np is bound by Sum; n and k are free
        assert _collect_free_indices(expr, model) == {"n", "k"}

    def test_sum_binds_multiple_indices(self):
        model = _make_model("n", "np", "k")
        inner = ParamRef("w", ("n", "np", "k"))
        expr = Sum(("np", "k"), inner)
        assert _collect_free_indices(expr, model) == {"n"}

    def test_nested_sums_both_bind(self):
        model = _make_model("n", "np", "k")
        innermost = ParamRef("w", ("n", "np", "k"))
        inner_sum = Sum(("np",), innermost)
        outer_sum = Sum(("k",), inner_sum)
        assert _collect_free_indices(outer_sum, model) == {"n"}

    def test_prod_binds_index(self):
        """Prod (product operator) also binds its index_sets."""
        model = _make_model("i", "j")
        inner = ParamRef("a", ("i", "j"))
        expr = Prod(("j",), inner, condition=None)
        assert _collect_free_indices(expr, model) == {"i"}

    def test_sum_condition_also_walks(self):
        """Indices in the Sum's condition are also walked (with sum indices bound)."""
        model = _make_model("i", "j", "k")
        body = ParamRef("a", ("i", "j"))
        condition = ParamRef("mask", ("j", "k"))
        expr = Sum(("j",), body, condition=condition)
        # j bound by sum; i and k are free
        assert _collect_free_indices(expr, model) == {"i", "k"}


class TestCollectFreeIndicesCompositeExprs:
    """Binary, Unary, Call, DollarConditional expressions."""

    def test_binary_collects_both_sides(self):
        model = _make_model("n", "k", "m")
        left = ParamRef("a", ("n", "k"))
        right = VarRef("x", ("m", "k"))
        expr = Binary("*", left, right)
        assert _collect_free_indices(expr, model) == {"n", "k", "m"}

    def test_unary_collects_child(self):
        model = _make_model("i")
        inner = ParamRef("p", ("i",))
        expr = Unary("-", inner)
        assert _collect_free_indices(expr, model) == {"i"}

    def test_call_collects_all_args(self):
        model = _make_model("i", "j")
        expr = Call("sqr", (ParamRef("a", ("i",)), VarRef("x", ("j",))))
        assert _collect_free_indices(expr, model) == {"i", "j"}

    def test_dollar_conditional_collects_value_expr_and_condition(self):
        model = _make_model("i", "j")
        value_expr = ParamRef("a", ("i",))
        cond = VarRef("mask", ("j",))
        # DollarConditional(value_expr, condition)
        expr = DollarConditional(value_expr=value_expr, condition=cond)
        assert _collect_free_indices(expr, model) == {"i", "j"}

    def test_sum_inside_binary(self):
        """Sum deep inside a Binary — bound indices don't propagate outside the sum."""
        model = _make_model("n", "np", "k")
        inner = Sum(("np",), ParamRef("w", ("n", "np", "k")))
        outer = Binary("+", inner, ParamRef("b", ("n",)))
        # np is bound inside the Sum; n appears free in both sides; k free in sum body
        assert _collect_free_indices(outer, model) == {"n", "k"}


class TestCollectFreeIndicesAbelPattern:
    """Reproduce the abel model cross-indexed sum pattern (core ISSUE_670 case)."""

    def test_abel_pattern_np_is_free(self):
        """In abel, derivative of criterion w.r.t. x(n,k) contains 'np' as a free index.

        The derivative expression looks like: a(n, np) — where 'np' comes from the
        original sum(np, w(n,np,k)*x(np,k)) after differentiation collapses x(np,k)
        to a(n,np) (symbolically). 'np' is not in var_domain=(n,k) nor in the multiplier
        domain (e.g. mult_domain=(k,n)) used for the criterion, but when checking after
        domain-based wrapping, it should be detected.
        """
        model = _make_model("n", "k", aliases={"np": "n"})
        # Simulate the derivative expression: a(n, np) * nu_criterion
        deriv = ParamRef("a", ("n", "np"))
        assert _collect_free_indices(deriv, model) == {"n", "np"}

    def test_abel_pattern_np_bound_by_existing_sum(self):
        """If np is already inside a Sum, it should NOT appear as free."""
        model = _make_model("n", "k", aliases={"np": "n"})
        deriv = Sum(("np",), ParamRef("a", ("n", "np")))
        assert _collect_free_indices(deriv, model) == {"n"}

    def test_no_free_indices_simple_case(self):
        """Simple derivative with no cross-indexed terms — no free indices."""
        model = _make_model("n", "k")
        # d/dx(n,k) of a simple constraint eq(n,k).. c(n,k)*x(n,k) = f(n,k)
        # gives Const(c_val) or ParamRef("c", ("n","k")) — all controlled
        deriv = ParamRef("c", ("n", "k"))
        # n and k appear free, but they are in var_domain — the integration code
        # computes uncontrolled = free - controlled, so this is the right result from
        # _collect_free_indices alone (caller subtracts controlled)
        assert _collect_free_indices(deriv, model) == {"n", "k"}


class TestCollectFreeIndicesSetMembershipAndSymbolRef:
    """SetMembershipTest, SymbolRef, and case-insensitive index handling."""

    def test_symbolref_known_set_is_free(self):
        """A bare SymbolRef whose name is a known set is treated as a free index."""
        model = _make_model("i")
        expr = SymbolRef("i")
        assert _collect_free_indices(expr, model) == {"i"}

    def test_symbolref_unknown_name_excluded(self):
        """SymbolRef whose name is not a known set is ignored."""
        model = _make_model("i")
        expr = SymbolRef("j")
        assert _collect_free_indices(expr, model) == set()

    def test_symbolref_bound_by_sum_excluded(self):
        """SymbolRef bound by an enclosing Sum is not free."""
        model = _make_model("i")
        expr = Sum(("i",), SymbolRef("i"))
        assert _collect_free_indices(expr, model) == set()

    def test_set_membership_test_walks_indices(self):
        """SetMembershipTest index expressions (e.g. rn(i)) expose free index i."""
        model = _make_model("i", "j")
        # rn(i, j) — both i and j are free
        expr = SetMembershipTest("rn", (SymbolRef("i"), SymbolRef("j")))
        assert _collect_free_indices(expr, model) == {"i", "j"}

    def test_set_membership_test_bound_index_excluded(self):
        """Index inside SetMembershipTest that is bound by enclosing Sum is not free."""
        model = _make_model("i", "j")
        inner = SetMembershipTest("rn", (SymbolRef("i"), SymbolRef("j")))
        expr = Sum(("i",), inner)
        assert _collect_free_indices(expr, model) == {"j"}

    def test_dollar_conditional_with_set_membership(self):
        """DollarConditional whose condition is a SetMembershipTest exposes indices."""
        model = _make_model("i", "j")
        value_expr = ParamRef("a", ("i",))
        cond = SetMembershipTest("rn", (SymbolRef("j"),))
        expr = DollarConditional(value_expr=value_expr, condition=cond)
        assert _collect_free_indices(expr, model) == {"i", "j"}

    def test_mixed_case_index_name_recognised(self):
        """Mixed-case index names are matched and returned as lowercase."""
        model = _make_model("n", "k")
        # VarRef index 'N' matches set 'n'; returned normalized to lowercase
        expr = VarRef("x", ("N", "K"))
        assert _collect_free_indices(expr, model) == {"n", "k"}

    def test_mixed_case_alias_recognised(self):
        """Alias lookup is case-insensitive; returned name is lowercase."""
        model = _make_model("n", aliases={"NP": "n"})
        expr = ParamRef("a", ("NP",))
        assert _collect_free_indices(expr, model) == {"np"}

    def test_mixed_case_bound_index_excluded(self):
        """Sum binding 'i' (lowercase) also suppresses uppercase 'I' in the body."""
        model = _make_model("i")
        # Sum binds ('i',); body uses 'I' — case-insensitive binding must suppress it
        inner = ParamRef("a", ("I",))
        expr = Sum(("i",), inner)
        assert _collect_free_indices(expr, model) == set()

    def test_mixed_case_bound_index_uppercase_binder(self):
        """Sum binding 'I' (uppercase) also suppresses lowercase 'i' in the body."""
        model = _make_model("i")
        inner = ParamRef("a", ("i",))
        expr = Sum(("I",), inner)
        assert _collect_free_indices(expr, model) == set()
