"""
Tests for sum aggregation differentiation.

Day 5: Tests for sum(indices, expr) derivatives.
"""

import pytest

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import (
    Binary,
    Call,
    Const,
    DollarConditional,
    ParamRef,
    SetMembershipTest,
    Sum,
    SymbolRef,
    VarRef,
)

pytestmark = pytest.mark.unit

# ============================================================================
# Basic Sum Differentiation Tests
# ============================================================================


@pytest.mark.unit
class TestBasicSumDifferentiation:
    """Tests for basic sum aggregation differentiation."""

    def test_sum_of_indexed_variable(self):
        """Test d/dx sum(i, x(i)) = sum(i, 0) when differentiating w.r.t. scalar x"""
        # sum(i, x(i))
        expr = Sum(("i",), VarRef("x", ("i",)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0) because x(i) doesn't match scalar x
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_of_constant(self):
        """Test d/dx sum(i, 5) = sum(i, 0)"""
        # sum(i, 5)
        expr = Sum(("i",), Const(5.0))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_of_parameter(self):
        """Test d/dx sum(i, c) where c is a parameter = sum(i, 0)"""
        # sum(i, c)
        expr = Sum(("i",), ParamRef("c"))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_of_different_variable(self):
        """Test d/dx sum(i, y(i)) where y != x = sum(i, 0)"""
        # sum(i, y(i))
        expr = Sum(("i",), VarRef("y", ("i",)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0


# ============================================================================
# Sum with Arithmetic Operations
# ============================================================================


@pytest.mark.unit
class TestSumWithArithmetic:
    """Tests for sum aggregation with arithmetic expressions."""

    def test_sum_of_product(self):
        """Test d/dx sum(i, c*x(i)) where c is parameter = sum(i, c*1 + x*0)"""
        # sum(i, c*x(i))
        expr = Sum(("i",), Binary("*", ParamRef("c"), VarRef("x", ("i",))))
        result = differentiate_expr(expr, "x")

        # Product rule: d/dx(c*x) = x*dc/dx + c*dx/dx = x*0 + c*1
        # Should be: sum(i, x(i)*0 + c*1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Left term should be x(i) * 0 (from x * dc/dx)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "*"
        assert isinstance(result.body.left.left, VarRef)
        assert result.body.left.left.name == "x"
        assert isinstance(result.body.left.right, Const)
        assert result.body.left.right.value == 0.0

        # Right term should be c * 0 (from c * dx(i)/dx where x(i) != x)
        assert isinstance(result.body.right, Binary)
        assert result.body.right.op == "*"
        assert isinstance(result.body.right.left, ParamRef)
        assert result.body.right.left.name == "c"
        assert isinstance(result.body.right.right, Const)
        assert result.body.right.right.value == 0.0

    def test_sum_of_addition(self):
        """Test d/dx sum(i, x(i) + y(i)) = sum(i, 0 + 0) when x is scalar"""
        # sum(i, x(i) + y(i))
        expr = Sum(("i",), Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",))))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 0 + 0) because x(i) and y(i) don't match scalar x
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Both should be 0 (x(i) and y(i) don't match scalar x)
        assert isinstance(result.body.left, Const)
        assert result.body.left.value == 0.0
        assert isinstance(result.body.right, Const)
        assert result.body.right.value == 0.0

    def test_sum_of_power(self):
        """Test d/dx sum(i, x(i)^2) = sum(i, 2*x(i))"""
        # sum(i, x(i)^2)
        inner = Call("power", (VarRef("x", ("i",)), Const(2.0)))
        expr = Sum(("i",), inner)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, 2*x(i)^1 * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"


# ============================================================================
# Multiple Indices
# ============================================================================


@pytest.mark.unit
class TestMultipleIndices:
    """Tests for sum with multiple index variables."""

    def test_sum_two_indices(self):
        """Test d/dx sum((i,j), x(i,j)) = sum((i,j), 0) when x is scalar"""
        # sum((i,j), x(i,j))
        expr = Sum(("i", "j"), VarRef("x", ("i", "j")))
        result = differentiate_expr(expr, "x")

        # Should be: sum((i,j), 0) because x(i,j) doesn't match scalar x
        assert isinstance(result, Sum)
        assert result.index_sets == ("i", "j")
        assert isinstance(result.body, Const)
        assert result.body.value == 0.0

    def test_sum_two_indices_with_product(self):
        """Test d/dx sum((i,j), a(i)*x(i,j)) = sum((i,j), a(i)*1 + x(i,j)*0)"""
        # sum((i,j), a(i)*x(i,j)) where a is parameter
        expr = Sum(("i", "j"), Binary("*", ParamRef("a", ("i",)), VarRef("x", ("i", "j"))))
        result = differentiate_expr(expr, "x")

        # Product rule: d/dx(a*x) = x*da/dx + a*dx/dx = x*0 + a*1
        # Should be: sum((i,j), x(i,j)*0 + a(i)*1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i", "j")
        assert isinstance(result.body, Binary)
        assert result.body.op == "+"

        # Left term should be x(i,j) * 0 (from x * da/dx)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "*"
        assert isinstance(result.body.left.left, VarRef)
        assert result.body.left.left.name == "x"
        assert result.body.left.left.indices == ("i", "j")
        assert isinstance(result.body.left.right, Const)
        assert result.body.left.right.value == 0.0

        # Right term should be a(i) * 0 (from a * dx(i,j)/dx where x(i,j) != x)
        assert isinstance(result.body.right, Binary)
        assert result.body.right.op == "*"
        assert isinstance(result.body.right.left, ParamRef)
        assert result.body.right.left.name == "a"
        assert result.body.right.left.indices == ("i",)
        assert isinstance(result.body.right.right, Const)
        assert result.body.right.right.value == 0.0


# ============================================================================
# Nested Sums (Basic)
# ============================================================================


@pytest.mark.unit
class TestNestedSums:
    """Tests for nested sum aggregations."""

    def test_nested_sum_simple(self):
        """Test d/dx sum(i, sum(j, x(i,j))) = sum(i, sum(j, 0)) when x is scalar"""
        # sum(i, sum(j, x(i,j)))
        inner_sum = Sum(("j",), VarRef("x", ("i", "j")))
        expr = Sum(("i",), inner_sum)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, sum(j, 0)) because x(i,j) doesn't match scalar x
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Sum)
        assert result.body.index_sets == ("j",)
        assert isinstance(result.body.body, Const)
        assert result.body.body.value == 0.0

    def test_nested_sum_with_constant(self):
        """Test d/dx sum(i, sum(j, c)) = sum(i, sum(j, 0))"""
        # sum(i, sum(j, c))
        inner_sum = Sum(("j",), Const(5.0))
        expr = Sum(("i",), inner_sum)
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, sum(j, 0))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Sum)
        assert result.body.index_sets == ("j",)
        assert isinstance(result.body.body, Const)
        assert result.body.body.value == 0.0


# ============================================================================
# Complex Expressions
# ============================================================================


@pytest.mark.unit
class TestComplexSumExpressions:
    """Tests for complex expressions within sums."""

    def test_sum_of_exp(self):
        """Test d/dx sum(i, exp(x(i))) = sum(i, exp(x(i)))"""
        # sum(i, exp(x(i)))
        expr = Sum(("i",), Call("exp", (VarRef("x", ("i",)),)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, exp(x(i)) * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"

        # Left should be exp(x(i))
        assert isinstance(result.body.left, Call)
        assert result.body.left.func == "exp"

    def test_sum_of_log(self):
        """Test d/dx sum(i, log(x(i))) = sum(i, 1/x(i))"""
        # sum(i, log(x(i)))
        expr = Sum(("i",), Call("log", (VarRef("x", ("i",)),)))
        result = differentiate_expr(expr, "x")

        # Should be: sum(i, (1/x(i)) * 1)
        assert isinstance(result, Sum)
        assert result.index_sets == ("i",)
        assert isinstance(result.body, Binary)
        assert result.body.op == "*"

        # Left should be 1/x(i)
        assert isinstance(result.body.left, Binary)
        assert result.body.left.op == "/"


# ============================================================================
# Dollar Condition Boolean Indicator Tests (Issue #1077)
# ============================================================================


@pytest.mark.unit
class TestDollarConditionBooleanIndicator:
    """Ensure collapsed dollar conditions produce 0/1 indicators, not raw values."""

    def test_paramref_condition_becomes_dollar_indicator(self):
        """Issue #1077: sum(j$mh(j), x(j)) differentiated w.r.t. x(j1).

        The dollar condition mh(j) is a ParamRef.  When the sum collapses
        (concrete index j1 triggers collapse), the condition must become
        ``1$(mh(j))`` (a DollarConditional), NOT the raw ``mh(j)`` value
        used as a coefficient.

        Issue #1085: The condition stays symbolic (using sum index j, not
        concrete j1) so that _replace_indices_in_expr can correctly map
        it to the stationarity domain without ambiguity.
        """
        # sum(j$mh(j), x(j))  differentiated w.r.t. x(j1)
        expr = Sum(
            ("j",),
            VarRef("x", ("j",)),
            condition=ParamRef("mh", ("j",)),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("j1",))

        # Sum collapses: result = 1 * 1$(mh(j))
        assert isinstance(result, Binary)
        assert result.op == "*"

        # One operand should be the DollarConditional wrapping the ParamRef
        if isinstance(result.right, DollarConditional):
            dc = result.right
        elif isinstance(result.left, DollarConditional):
            dc = result.left
        else:
            pytest.fail(
                f"Expected DollarConditional in result, got: "
                f"left={type(result.left).__name__}, right={type(result.right).__name__}"
            )

        assert isinstance(dc.value_expr, Const)
        assert dc.value_expr.value == 1.0
        assert isinstance(dc.condition, ParamRef)
        assert dc.condition.name == "mh"
        # Issue #1085: Condition stays symbolic (j, not j1)
        assert dc.condition.indices == ("j",)

        # Verify the other operand is Const(1.0) (the derivative of x(j) w.r.t. x(j1))
        other = result.left if isinstance(result.right, DollarConditional) else result.right
        assert isinstance(other, Const)
        assert other.value == 1.0

    def test_set_membership_condition_stays_symbolic_on_collapse(self):
        """SetMembershipTest condition stays symbolic when a sum collapses.

        sum(j$ri(j), x(j)) differentiated w.r.t. x(j1):
        The SetMembershipTest ri(j) stays as ri(j) after collapse, wrapped
        as 1$(ri(j)).  Issue #1085: Keeping the condition symbolic avoids
        ambiguity when concrete values belong to multiple sets.
        """
        # sum(j$ri(j), x(j))  differentiated w.r.t. x(j1)
        expr = Sum(
            ("j",),
            VarRef("x", ("j",)),
            condition=SetMembershipTest("ri", (SymbolRef("j"),)),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("j1",))

        # Sum collapses: result = 1 * 1$(ri(j))
        assert isinstance(result, Binary)
        assert result.op == "*"

        if isinstance(result.right, DollarConditional):
            dc = result.right
        elif isinstance(result.left, DollarConditional):
            dc = result.left
        else:
            pytest.fail(
                f"Expected DollarConditional in result, got: "
                f"left={type(result.left).__name__}, right={type(result.right).__name__}"
            )

        assert isinstance(dc.value_expr, Const)
        assert dc.value_expr.value == 1.0
        assert isinstance(dc.condition, SetMembershipTest)
        assert dc.condition.set_name == "ri"
        # Issue #1085: Condition stays symbolic (j, not j1)
        assert len(dc.condition.indices) == 1
        assert isinstance(dc.condition.indices[0], SymbolRef)
        assert dc.condition.indices[0].name == "j"


@pytest.mark.unit
class TestPartialIndexMatchDollarConditions:
    """Ensure dollar conditions stay symbolic on partial-index-match collapse.

    Issue #1085: When wrt_indices has MORE indices than the sum, the
    partial-index-match path collapses the sum but must keep conditions
    in symbolic form (using sum index names, not concrete values).
    """

    def test_paramref_condition_stays_symbolic_partial_match(self):
        """sum(j$mh(j), x(i,j)) differentiated w.r.t. x(i1,j1).

        Partial-index-match: wrt has 2 indices, sum has 1.
        After collapse, condition mh(j) must stay symbolic (j, not j1).
        """
        # sum(j$mh(j), x(i1,j)) — the body uses concrete i1 + symbolic j
        expr = Sum(
            ("j",),
            VarRef("x", ("i1", "j")),
            condition=ParamRef("mh", ("j",)),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("i1", "j1"))

        # Sum collapses via partial-index-match: j matches j1
        # Result = 1 * 1$(mh(j))
        assert isinstance(result, Binary)
        assert result.op == "*"

        if isinstance(result.right, DollarConditional):
            dc = result.right
        elif isinstance(result.left, DollarConditional):
            dc = result.left
        else:
            pytest.fail(
                f"Expected DollarConditional in result, got: "
                f"left={type(result.left).__name__}, right={type(result.right).__name__}"
            )

        assert isinstance(dc.condition, ParamRef)
        assert dc.condition.name == "mh"
        # Issue #1085: Condition stays symbolic (j, not j1)
        assert dc.condition.indices == ("j",)

    def test_setmembership_condition_stays_symbolic_partial_match(self):
        """sum(j$ri(j), x(i,j)) differentiated w.r.t. x(i1,j1).

        Partial-index-match with SetMembershipTest condition.
        """
        expr = Sum(
            ("j",),
            VarRef("x", ("i1", "j")),
            condition=SetMembershipTest("ri", (SymbolRef("j"),)),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("i1", "j1"))

        assert isinstance(result, Binary)
        assert result.op == "*"

        if isinstance(result.right, DollarConditional):
            dc = result.right
        elif isinstance(result.left, DollarConditional):
            dc = result.left
        else:
            pytest.fail(
                f"Expected DollarConditional in result, got: "
                f"left={type(result.left).__name__}, right={type(result.right).__name__}"
            )

        assert isinstance(dc.condition, SetMembershipTest)
        assert dc.condition.set_name == "ri"
        assert len(dc.condition.indices) == 1
        assert isinstance(dc.condition.indices[0], SymbolRef)
        assert dc.condition.indices[0].name == "j"


@pytest.mark.unit
class TestPartialCollapseDollarConditions:
    """Ensure dollar conditions are preserved on partial-collapse.

    Issue #1085: When wrt_indices has FEWER indices than the sum, the
    _partial_collapse_sum path collapses matched dimensions and wraps
    remaining dimensions in a new Sum, preserving conditions.
    """

    def test_paramref_condition_preserved_partial_collapse(self):
        """sum((i,j)$mh(i,j), x(i)) differentiated w.r.t. x(i1).

        Partial collapse: i matches i1, j remains as sum dimension.
        Condition mh(i,j) must be preserved on the remaining Sum.
        """
        expr = Sum(
            ("i", "j"),
            VarRef("x", ("i",)),
            condition=ParamRef("mh", ("i", "j")),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("i1",))

        # Partial collapse: result should be Sum(("j",), body, condition=mh(i,j))
        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        # The condition must be preserved on the remaining Sum
        assert result.condition is not None
        assert isinstance(result.condition, ParamRef)
        assert result.condition.name == "mh"

    def test_setmembership_condition_preserved_partial_collapse(self):
        """sum((i,j)$ri(i,j), x(i)) differentiated w.r.t. x(i1).

        Partial collapse with SetMembershipTest condition preserved on Sum.
        """
        expr = Sum(
            ("i", "j"),
            VarRef("x", ("i",)),
            condition=SetMembershipTest("ri", (SymbolRef("i"), SymbolRef("j"))),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("i1",))

        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        assert result.condition is not None
        assert isinstance(result.condition, SetMembershipTest)
        assert result.condition.set_name == "ri"

    def test_condition_becomes_indicator_when_fully_collapsed(self):
        """sum((i,j)$mh(i,j), x(i,j)) differentiated w.r.t. x(i1,j1).

        When all sum indices match (full collapse via _partial_collapse_sum),
        the condition must become a 1$(cond) indicator with symbolic indices.
        """
        expr = Sum(
            ("i", "j"),
            VarRef("x", ("i", "j")),
            condition=ParamRef("mh", ("i", "j")),
        )
        result = differentiate_expr(expr, "x", wrt_indices=("i1", "j1"))

        # Full collapse: result = 1 * 1$(mh(i,j))
        assert isinstance(result, Binary)
        assert result.op == "*"

        if isinstance(result.right, DollarConditional):
            dc = result.right
        elif isinstance(result.left, DollarConditional):
            dc = result.left
        else:
            pytest.fail(
                f"Expected DollarConditional in result, got: "
                f"left={type(result.left).__name__}, right={type(result.right).__name__}"
            )

        assert isinstance(dc.condition, ParamRef)
        assert dc.condition.name == "mh"
        # Condition stays symbolic (i,j not i1,j1)
        assert dc.condition.indices == ("i", "j")


def test_diff_sum_variable_constant_wrt_alias_index():
    """Issue #1157: d/dp(R1,C1) [sum(cc, B(R1,C1,cc)*p(R1,C1))] should preserve the sum.

    When variable p(R1,C1) doesn't depend on the sum index cc (an alias of c),
    the derivative should pass through the sum: sum(cc, B(R1,C1,cc) * 1).
    Previously, the partial-index-match path incorrectly collapsed the sum
    because its zero-check missed structurally-zero expressions.
    """
    from src.ad.derivative_rules import _is_structurally_zero, differentiate_expr
    from src.config import Config
    from src.ir.ast import Binary, ParamRef, Sum, VarRef
    from src.ir.model_ir import ModelIR, SetDef
    from src.ir.symbols import AliasDef

    # Build minimal model with sets r, c and alias cc
    model = ModelIR()
    model.sets["r"] = SetDef(name="r", domain=(), members=["Reg1", "Reg2"])
    model.sets["c"] = SetDef(name="c", domain=(), members=["Com1", "Com2"])
    model.aliases["cc"] = AliasDef(name="cc", target="c")

    config = Config()
    config.model_ir = model

    # sum(cc, BetaD(Reg1,Com1,cc) * p(Reg1,Com1))
    body = Binary(
        "*",
        ParamRef("BetaD", ("Reg1", "Com1", "cc")),
        VarRef("p", ("Reg1", "Com1")),
    )
    sum_expr = Sum(("cc",), body, None)

    # Differentiate w.r.t. p(Reg1, Com1)
    result = differentiate_expr(sum_expr, "p", ("Reg1", "Com1"), config)

    # Result should be a Sum (not collapsed) with correct, non-zero body
    assert isinstance(result, Sum), f"Expected Sum, got {type(result).__name__}: {result}"
    assert result.index_sets == ("cc",)
    assert not _is_structurally_zero(result.body), "Body derivative should not be zero"

    # Body is product rule: BetaD * dp/dp + p * dBetaD/dp = BetaD * 1 + p * 0
    # Structured as Binary(+, Binary(*, p, 0), Binary(*, BetaD, 1))
    assert isinstance(result.body, Binary), f"Expected Binary body, got {type(result.body)}"
    # The non-zero term should contain BetaD(Reg1,Com1,cc) * Const(1.0)
    right_term = result.body.right
    assert isinstance(right_term, Binary) and right_term.op == "*"
    assert isinstance(right_term.left, ParamRef)
    assert right_term.left.name == "BetaD"
    assert right_term.left.indices == ("Reg1", "Com1", "cc")
    from src.ir.ast import Const

    assert isinstance(right_term.right, Const) and right_term.right.value == 1.0
