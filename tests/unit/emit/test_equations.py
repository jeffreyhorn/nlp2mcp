"""Unit tests for equation definition emission.

Tests verify correct emission of GAMS equation definitions from KKT system equations.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.equations import (
    _build_domain_condition,
    _collect_lead_lag_restrictions,
    emit_equation_def,
    emit_equation_definitions,
)
from src.emit.expr_to_gams import collect_index_aliases, resolve_index_conflicts
from src.ir.ast import Binary, Const, IndexOffset, Prod, Sum, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import ComplementarityPair, KKTSystem


def _create_minimal_kkt(model_ir: ModelIR) -> KKTSystem:
    """Create a minimal KKTSystem for testing."""
    gradient = GradientVector(num_cols=0, index_mapping={})
    J_eq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    J_ineq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    return KKTSystem(model_ir=model_ir, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)


@pytest.mark.unit
class TestEmitEquationDef:
    """Test emission of single equation definitions."""

    def test_scalar_equation_eq(self):
        """Test scalar equation with =E= relation."""
        eq_def = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(10)),
        )
        result, aliases = emit_equation_def("balance", eq_def)
        assert result == "balance.. x =E= 10;"
        assert aliases == set()

    def test_indexed_equation(self):
        """Test indexed equation.

        Single lowercase letters are domain variables and not quoted.
        """
        eq_def = EquationDef(
            name="balance",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i",)), Const(10)),
        )
        result, aliases = emit_equation_def("balance", eq_def)
        assert result == "balance(i).. x(i) =E= 10;"
        assert aliases == set()

    def test_multi_indexed_equation(self):
        """Test multi-indexed equation.

        Single lowercase letters are domain variables and not quoted.
        """
        eq_def = EquationDef(
            name="flow",
            domain=("i", "j"),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i", "j")), VarRef("y", ("j", "i"))),
        )
        result, aliases = emit_equation_def("flow", eq_def)
        assert result == "flow(i,j).. x(i,j) =E= y(j,i);"
        assert aliases == set()

    def test_equation_le_relation(self):
        """Test equation with =L= (less than or equal) relation."""
        eq_def = EquationDef(
            name="capacity",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(VarRef("x", ()), Const(100)),
        )
        result, aliases = emit_equation_def("capacity", eq_def)
        assert result == "capacity.. x =L= 100;"
        assert aliases == set()

    def test_equation_ge_relation(self):
        """Test equation with =G= (greater than or equal) relation."""
        eq_def = EquationDef(
            name="demand",
            domain=(),
            relation=Rel.GE,
            lhs_rhs=(VarRef("x", ()), Const(5)),
        )
        result, aliases = emit_equation_def("demand", eq_def)
        assert result == "demand.. x =G= 5;"
        assert aliases == set()

    def test_equation_with_binary_expression(self):
        """Test equation with binary expression on LHS."""
        lhs = Binary("+", VarRef("x", ()), VarRef("y", ()))
        eq_def = EquationDef(
            name="sum_constraint", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, Const(10))
        )
        result, aliases = emit_equation_def("sum_constraint", eq_def)
        assert result == "sum_constraint.. x + y =E= 10;"
        assert aliases == set()

    def test_equation_with_complex_expression(self):
        """Test equation with complex expression."""
        lhs = Binary("^", VarRef("x", ()), Const(2))
        rhs = Binary("*", Const(2), VarRef("y", ()))
        eq_def = EquationDef(name="nonlinear", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, rhs))
        result, aliases = emit_equation_def("nonlinear", eq_def)
        assert result == "nonlinear.. x ** 2 =E= 2 * y;"
        assert aliases == set()


@pytest.mark.unit
class TestEmitEquationDefinitions:
    """Test emission of all equation definitions from KKT system."""

    def test_empty_kkt_system(self):
        """Test with empty KKT system."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result, aliases = emit_equation_definitions(kkt)
        assert result == ""
        assert aliases == set()

    def test_stationarity_equations_only(self):
        """Test with only stationarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        # Add stationarity equation
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("*", Const(2), VarRef("x", ())), Const(0)),
        )

        result, aliases = emit_equation_definitions(kkt)
        assert "* Stationarity equations" in result
        assert "stat_x.. 2 * x =E= 0;" in result
        assert aliases == set()

    def test_multiple_stationarity_equations(self):
        """Test with multiple stationarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(0)),
        )
        kkt.stationarity["stat_y"] = EquationDef(
            name="stat_y",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("y", ()), Const(0)),
        )

        result, aliases = emit_equation_definitions(kkt)
        assert "stat_x.. x =E= 0;" in result
        assert "stat_y.. y =E= 0;" in result
        assert aliases == set()

    def test_inequality_complementarity(self):
        """Test with inequality complementarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        comp_eq = EquationDef(
            name="comp_g1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("slack_g1", ()), Const(0)),
        )
        kkt.complementarity_ineq["g1"] = ComplementarityPair(
            equation=comp_eq, variable="lambda_g1", variable_indices=()
        )

        result, aliases = emit_equation_definitions(kkt)
        assert "* Inequality complementarity equations" in result
        assert "comp_g1.. slack_g1 =E= 0;" in result
        assert aliases == set()

    def test_bound_complementarity(self):
        """Test with bound complementarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        # Lower bound complementarity
        comp_lo = EquationDef(
            name="comp_lo_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("-", VarRef("x", ()), Const(0)), Const(0)),
        )
        kkt.complementarity_bounds_lo[("x", ())] = ComplementarityPair(
            equation=comp_lo, variable="piL_x", variable_indices=()
        )

        # Upper bound complementarity
        comp_up = EquationDef(
            name="comp_up_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("-", Const(10), VarRef("x", ())), Const(0)),
        )
        kkt.complementarity_bounds_up[("x", ())] = ComplementarityPair(
            equation=comp_up, variable="piU_x", variable_indices=()
        )

        result, aliases = emit_equation_definitions(kkt)
        assert "* Lower bound complementarity equations" in result
        assert "comp_lo_x.. x - 0 =E= 0;" in result
        assert "* Upper bound complementarity equations" in result
        assert "comp_up_x.. 10 - x =E= 0;" in result
        assert aliases == set()

    def test_equality_equations(self):
        """Test with original equality equations."""
        model_ir = ModelIR()
        model_ir.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(10)),
        )
        model_ir.equalities = ["balance"]

        kkt = _create_minimal_kkt(model_ir)
        result, aliases = emit_equation_definitions(kkt)

        assert "* Original equality equations" in result
        assert "balance.. x =E= 10;" in result
        assert aliases == set()

    def test_all_equation_types(self):
        """Test with all types of equations."""
        model_ir = ModelIR()
        model_ir.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )
        model_ir.equalities = ["objdef"]

        kkt = _create_minimal_kkt(model_ir)

        # Add stationarity
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Const(1), Const(0)),
        )

        # Add inequality complementarity
        comp_ineq = EquationDef(
            name="comp_g1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("slack", ()), Const(0)),
        )
        kkt.complementarity_ineq["g1"] = ComplementarityPair(
            equation=comp_ineq, variable="lambda_g1", variable_indices=()
        )

        # Add bound complementarity
        comp_lo = EquationDef(
            name="comp_lo_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(0)),
        )
        kkt.complementarity_bounds_lo[("x", ())] = ComplementarityPair(
            equation=comp_lo, variable="piL_x", variable_indices=()
        )

        result, aliases = emit_equation_definitions(kkt)

        # Verify all sections present
        assert "* Stationarity equations" in result
        assert "* Inequality complementarity equations" in result
        assert "* Lower bound complementarity equations" in result
        assert "* Original equality equations" in result

        # Verify equations present
        assert "stat_x.." in result
        assert "comp_g1.." in result
        assert "comp_lo_x.." in result
        assert "objdef.." in result
        assert aliases == set()


@pytest.mark.unit
class TestIndexAliasing:
    """Test index aliasing to avoid GAMS Error 125.

    GAMS Error 125 "Set is under control already" occurs when an equation's
    domain index is reused inside a sum expression. These tests verify that
    conflicting indices are detected and replaced with aliases.
    """

    def test_collect_index_aliases_no_conflict(self):
        """Test that non-conflicting sum indices don't need aliases."""
        # sum(j, x(j)) with equation domain (i,)
        expr = Sum(("j",), VarRef("x", ("j",)))
        aliases = collect_index_aliases(expr, ("i",))
        assert aliases == set()

    def test_collect_index_aliases_with_conflict(self):
        """Test that conflicting sum indices are detected."""
        # sum(i, x(i)) with equation domain (i,)
        expr = Sum(("i",), VarRef("x", ("i",)))
        aliases = collect_index_aliases(expr, ("i",))
        assert aliases == {"i"}

    def test_collect_index_aliases_multiple_conflicts(self):
        """Test detection of multiple conflicting indices."""
        # sum(i, sum(j, x(i,j))) with equation domain (i, j)
        inner_sum = Sum(("j",), VarRef("x", ("i", "j")))
        outer_sum = Sum(("i",), inner_sum)
        aliases = collect_index_aliases(outer_sum, ("i", "j"))
        assert aliases == {"i", "j"}

    def test_collect_index_aliases_nested_sum(self):
        """Test detection of conflicts in nested sums."""
        # sum(i, sum(i, x(i))) - inner i conflicts with equation domain (i,)
        inner_sum = Sum(("i",), VarRef("x", ("i",)))
        outer_sum = Sum(("k",), inner_sum)
        aliases = collect_index_aliases(outer_sum, ("i",))
        assert aliases == {"i"}

    def test_resolve_index_conflicts_no_conflict(self):
        """Test that non-conflicting expressions are unchanged."""
        # sum(j, x(j)) with equation domain (i,)
        expr = Sum(("j",), VarRef("x", ("j",)))
        result = resolve_index_conflicts(expr, ("i",))
        # Should be unchanged
        assert isinstance(result, Sum)
        assert result.index_sets == ("j",)
        assert result.body.indices == ("j",)

    def test_resolve_index_conflicts_simple(self):
        """Test resolution of simple index conflict."""
        # sum(i, x(i)) with equation domain (i,)
        # Should become sum(i__, x(i__))
        expr = Sum(("i",), VarRef("x", ("i",)))
        result = resolve_index_conflicts(expr, ("i",))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i__",)
        assert result.body.indices == ("i__",)

    def test_resolve_index_conflicts_multiple_indices(self):
        """Test resolution with multiple conflicting indices."""
        # sum((i, j), x(i,j)) with equation domain (i, j)
        # Should become sum((i__, j__), x(i__, j__))
        expr = Sum(("i", "j"), VarRef("x", ("i", "j")))
        result = resolve_index_conflicts(expr, ("i", "j"))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i__", "j__")
        assert result.body.indices == ("i__", "j__")

    def test_resolve_index_conflicts_partial(self):
        """Test resolution when only some indices conflict."""
        # sum((i, k), x(i,k)) with equation domain (i,)
        # Should become sum((i__, k), x(i__, k))
        expr = Sum(("i", "k"), VarRef("x", ("i", "k")))
        result = resolve_index_conflicts(expr, ("i",))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i__", "k")
        assert result.body.indices == ("i__", "k")

    def test_resolve_index_conflicts_nested(self):
        """Test resolution in nested binary expressions."""
        # sum(i, x(i) + y(i)) with equation domain (i,)
        expr = Sum(("i",), Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",))))
        result = resolve_index_conflicts(expr, ("i",))
        assert isinstance(result, Sum)
        assert result.index_sets == ("i__",)
        body = result.body
        assert isinstance(body, Binary)
        assert body.left.indices == ("i__",)
        assert body.right.indices == ("i__",)

    def test_emit_equation_def_with_index_conflict(self):
        """Test that emit_equation_def detects and resolves index conflicts."""
        # stat_x(i).. sum(i, x(i)) =E= 0
        # Should become stat_x(i).. sum(i__, x(i__)) =E= 0
        # and return {"i"} as aliases needed
        eq_def = EquationDef(
            name="stat_x",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(Sum(("i",), VarRef("x", ("i",))), Const(0)),
        )
        result, aliases = emit_equation_def("stat_x", eq_def)
        assert "stat_x(i).." in result
        assert "sum(i__," in result
        assert "x(i__)" in result
        assert aliases == {"i"}

    def test_emit_equation_def_multi_index_conflict(self):
        """Test emit_equation_def with multiple conflicting indices."""
        # stat_outp(g,m).. sum(g, p(g)) + sum(m, q(m)) =E= 0
        # Should use g__ and m__ in the sums
        lhs = Binary(
            "+",
            Sum(("g",), VarRef("p", ("g",))),
            Sum(("m",), VarRef("q", ("m",))),
        )
        eq_def = EquationDef(
            name="stat_outp",
            domain=("g", "m"),
            relation=Rel.EQ,
            lhs_rhs=(lhs, Const(0)),
        )
        result, aliases = emit_equation_def("stat_outp", eq_def)
        assert "stat_outp(g,m).." in result
        assert "sum(g__," in result
        assert "sum(m__," in result
        assert aliases == {"g", "m"}


@pytest.mark.unit
class TestLeadLagDomainRestrictions:
    """Test automatic domain restriction inference for lead/lag expressions.

    When equations use lead (k+1) or lag (t-1) indexing on domain variables,
    the equation needs domain conditions to prevent out-of-bounds access:
    - k+1 requires ord(k) <= card(k) - 1 (or card(k) - n for k+n)
    - t-1 requires ord(t) > 1 (or ord(t) > n for t-n)
    """

    def test_build_domain_condition_lead_offset_1(self):
        """Test building domain condition for lead offset of 1."""
        # k+1 needs ord(k) <= card(k) - 1
        lead_offsets = {"k": 1}
        lag_offsets: dict[str, int] = {}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        assert result == "ord(k) <= card(k) - 1"

    def test_build_domain_condition_lag_offset_1(self):
        """Test building domain condition for lag offset of 1."""
        # t-1 needs ord(t) > 1
        lead_offsets: dict[str, int] = {}
        lag_offsets = {"t": 1}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        assert result == "ord(t) > 1"

    def test_build_domain_condition_lead_offset_2(self):
        """Test building domain condition for lead offset of 2."""
        # i+2 needs ord(i) <= card(i) - 2
        lead_offsets = {"i": 2}
        lag_offsets: dict[str, int] = {}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        assert result == "ord(i) <= card(i) - 2"

    def test_build_domain_condition_lag_offset_2(self):
        """Test building domain condition for lag offset of 2."""
        # i-2 needs ord(i) > 2
        lead_offsets: dict[str, int] = {}
        lag_offsets = {"i": 2}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        assert result == "ord(i) > 2"

    def test_build_domain_condition_both_lead_and_lag(self):
        """Test building domain condition with both lead and lag."""
        # k+1 and t-1 in same equation
        lead_offsets = {"k": 1}
        lag_offsets = {"t": 1}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        # Both conditions should be present with 'and'
        assert result is not None
        assert "ord(k) <= card(k) - 1" in result
        assert "ord(t) > 1" in result
        assert " and " in result

    def test_build_domain_condition_empty(self):
        """Test building domain condition with no restrictions."""
        lead_offsets: dict[str, int] = {}
        lag_offsets: dict[str, int] = {}
        result = _build_domain_condition(lead_offsets, lag_offsets)
        assert result is None

    def test_collect_lead_lag_restrictions_simple_lead(self):
        """Test collecting lead restriction from simple lead expression."""
        # x(k+1) with domain (k,)
        expr = VarRef("x", (IndexOffset("k", Const(1), circular=False),))
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("k",))
        assert lead_offsets == {"k": 1}
        assert lag_offsets == {}

    def test_collect_lead_lag_restrictions_simple_lag(self):
        """Test collecting lag restriction from simple lag expression."""
        # x(t-1) with domain (t,)
        expr = VarRef("x", (IndexOffset("t", Const(-1), circular=False),))
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("t",))
        assert lead_offsets == {}
        assert lag_offsets == {"t": 1}

    def test_collect_lead_lag_restrictions_non_domain_index(self):
        """Test that non-domain indices don't generate restrictions."""
        # x(j+1) with domain (i,) - j is not in domain
        expr = VarRef("x", (IndexOffset("j", Const(1), circular=False),))
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("i",))
        assert lead_offsets == {}
        assert lag_offsets == {}

    def test_collect_lead_lag_restrictions_in_binary(self):
        """Test collecting restrictions from binary expression."""
        # x(k+1) + y(k) with domain (k,)
        expr = Binary(
            "+",
            VarRef("x", (IndexOffset("k", Const(1), circular=False),)),
            VarRef("y", ("k",)),
        )
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("k",))
        assert lead_offsets == {"k": 1}
        assert lag_offsets == {}

    def test_collect_lead_lag_restrictions_max_offset(self):
        """Test that maximum offset is tracked when multiple offsets exist."""
        # x(i+1) + y(i+2) - the max lead offset for i is 2
        expr = Binary(
            "+",
            VarRef("x", (IndexOffset("i", Const(1), circular=False),)),
            VarRef("y", (IndexOffset("i", Const(2), circular=False),)),
        )
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("i",))
        assert lead_offsets == {"i": 2}
        assert lag_offsets == {}

    def test_emit_equation_def_with_lead(self):
        """Test emit_equation_def adds domain condition for lead."""
        # eq(k).. x(k+1) =E= y(k)
        # Should emit: eq(k)$(ord(k) <= card(k) - 1).. x(k+1) =E= y(k);
        eq_def = EquationDef(
            name="eq",
            domain=("k",),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("x", (IndexOffset("k", Const(1), circular=False),)),
                VarRef("y", ("k",)),
            ),
        )
        result, aliases = emit_equation_def("eq", eq_def)
        assert "$(ord(k) <= card(k) - 1)" in result
        assert aliases == set()

    def test_emit_equation_def_with_lag(self):
        """Test emit_equation_def adds domain condition for lag."""
        # eq(t).. x(t-1) =E= y(t)
        # Should emit: eq(t)$(ord(t) > 1).. x(t-1) =E= y(t);
        eq_def = EquationDef(
            name="eq",
            domain=("t",),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("x", (IndexOffset("t", Const(-1), circular=False),)),
                VarRef("y", ("t",)),
            ),
        )
        result, aliases = emit_equation_def("eq", eq_def)
        assert "$(ord(t) > 1)" in result
        assert aliases == set()

    def test_emit_equation_def_combines_with_existing_condition(self):
        """Test that inferred condition is combined with existing condition."""
        # eq(k)$(k.val > 5).. x(k+1) =E= y(k)
        # Should emit: eq(k)$((k.val > 5) and (ord(k) <= card(k) - 1))..
        eq_def = EquationDef(
            name="eq",
            domain=("k",),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("x", (IndexOffset("k", Const(1), circular=False),)),
                VarRef("y", ("k",)),
            ),
            condition="k.val > 5",
        )
        result, aliases = emit_equation_def("eq", eq_def)
        assert "$((" in result
        assert "k.val > 5" in result
        assert "ord(k) <= card(k) - 1" in result
        assert " and " in result
        assert aliases == set()

    def test_emit_equation_def_no_restriction_for_scalar(self):
        """Test that scalar equations don't get domain restrictions."""
        # eq.. x =E= y (no domain)
        eq_def = EquationDef(
            name="eq",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), VarRef("y", ())),
        )
        result, aliases = emit_equation_def("eq", eq_def)
        assert "$" not in result
        assert aliases == set()

    def test_collect_lead_lag_restrictions_sum_shadows_domain(self):
        """Test that sum-local indices don't generate restrictions.

        When a sum binds an index that matches the equation domain,
        lead/lag inside that sum should not cause equation-level restrictions.
        """
        # sum(i, x(i+1)) with equation domain (i,)
        # The i inside sum is sum-local, not the equation domain i
        expr = Sum(("i",), VarRef("x", (IndexOffset("i", Const(1), circular=False),)))
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("i",))
        # Should NOT generate restrictions since i is bound by sum
        assert lead_offsets == {}
        assert lag_offsets == {}

    def test_collect_lead_lag_restrictions_prod_shadows_domain(self):
        """Test that prod-local indices don't generate restrictions.

        When a prod binds an index that matches the equation domain,
        lead/lag inside that prod should not cause equation-level restrictions.
        """
        # prod(i, x(i+1)) with equation domain (i,)
        # The i inside prod is prod-local, not the equation domain i
        expr = Prod(("i",), VarRef("x", (IndexOffset("i", Const(1), circular=False),)))
        lead_offsets, lag_offsets = _collect_lead_lag_restrictions(expr, ("i",))
        # Should NOT generate restrictions since i is bound by prod
        assert lead_offsets == {}
        assert lag_offsets == {}
