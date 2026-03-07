"""Integration tests for uncontrolled index wrapping in stationarity equations.

Issue #949: Tests that stationarity equations correctly wrap uncontrolled
set indices in Sum nodes to avoid GAMS Error $149.

Two failure modes are covered:
1. Gradient component with subset indices not in the variable domain
2. Scalar stationarity with indexed constraints containing extra free indices
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, ParamRef, Sum, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, SetDef, VariableDef
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.stationarity import build_stationarity_equations


def _find_sum_indices(expr, target_indices: set[str]) -> bool:
    """Recursively check if the expression contains a Sum with the given indices."""
    if isinstance(expr, Sum):
        if set(expr.index_sets) == target_indices:
            return True
        # Check body too for nested Sums
        return _find_sum_indices(expr.body, target_indices)
    if isinstance(expr, Binary):
        return _find_sum_indices(expr.left, target_indices) or _find_sum_indices(
            expr.right, target_indices
        )
    return False


def _contains_any_sum(expr) -> bool:
    """Recursively check if the expression tree contains any Sum node."""
    if isinstance(expr, Sum):
        return True
    if isinstance(expr, Binary):
        return _contains_any_sum(expr.left) or _contains_any_sum(expr.right)
    return False


@pytest.mark.integration
class TestGradientUncontrolledIndices:
    """Failure Mode 1: Gradient term contains subset indices not in var domain."""

    def test_subset_index_in_gradient_wrapped_in_sum(self, manual_index_mapping):
        """Gradient contains c(p,t) but variable domain is (p, tt) where t ⊂ tt.

        Like the robert model: stat_x(p,tt) should wrap gradient c(p,t) in
        sum(t, ...) so that t is controlled.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Sets: tt is the superset, t is a subset of tt
        model.add_set(SetDef(name="tt", members=["1", "2", "3", "4"]))
        model.add_set(SetDef(name="t", members=["1", "2", "3"], domain=("tt",)))
        model.add_set(SetDef(name="p", members=["low", "medium", "high"]))

        # objdef references x(p,t) — uses subset index t
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("*", ParamRef("c", ("p", "t")), VarRef("x", ("p", "t"))),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("p", "tt"), lo=0.0)

        model.equalities = ["objdef"]

        # 4 instances: x(low,1), x(low,2), x(low,3), x(low,4) — simplified
        var_specs = [
            ("obj", ()),
            ("x", ("low", "1")),
            ("x", ("low", "2")),
            ("x", ("low", "3")),
            ("x", ("low", "4")),
        ]
        index_mapping = manual_index_mapping(var_specs, [("objdef", ())])

        gradient = GradientVector(num_cols=5, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        # Gradient for x: contains c(p,t) — uses subset index t, not tt
        for col_id in range(1, 5):
            gradient.set_derivative(col_id, ParamRef("c", ("p", "t")))

        J_eq = JacobianStructure(num_rows=1, num_cols=5, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=5, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=("p", "tt"), kind="bound_lo", associated_constraint="x"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        # The stationarity expression should contain a Sum over 't' to control it
        lhs = stat_eq.lhs_rhs[0]
        assert _find_sum_indices(lhs, {"t"}), (
            "Gradient with subset index 't' should be wrapped in sum(t, ...) "
            "to avoid GAMS Error $149"
        )

    def test_no_wrapping_when_all_indices_controlled(self, manual_index_mapping):
        """No Sum wrapping when gradient indices match the variable domain.

        Regression guard: if gradient only uses indices from var_domain,
        no additional Sum should be added.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.add_set(SetDef(name="i", members=["a", "b"]))

        # objdef references x(i) — same index as domain, no subset issue
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("*", ParamRef("c", ("i",)), VarRef("x", ("i",))),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",), lo=0.0)

        model.equalities = ["objdef"]

        var_specs = [("obj", ()), ("x", ("a",)), ("x", ("b",))]
        index_mapping = manual_index_mapping(var_specs, [("objdef", ())])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        # Gradient uses same index as domain — no wrapping needed
        gradient.set_derivative(1, ParamRef("c", ("i",)))
        gradient.set_derivative(2, ParamRef("c", ("i",)))

        J_eq = JacobianStructure(num_rows=1, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=("i",), kind="bound_lo", associated_constraint="x"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        lhs = stat_eq.lhs_rhs[0]
        # No Sum node should appear anywhere in the tree when all indices
        # are already controlled by the variable domain.
        assert not _contains_any_sum(
            lhs
        ), "No Sum wrapping expected when all gradient indices match var_domain"


@pytest.mark.integration
class TestScalarStationarityUncontrolledIndices:
    """Failure Mode 2: Scalar stationarity with indexed constraint extra indices."""

    def test_extra_index_in_indexed_constraint_derivative(self, manual_index_mapping):
        """Scalar variable with indexed constraint whose derivative has extra indices.

        Like dyncge: scalar variable sf, constraint eqII(j) has derivative
        containing pf(h,j) — after Sum(j, ...), h is still uncontrolled.
        The fix should wrap in an additional Sum(h, ...).
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.add_set(SetDef(name="j", members=["j1", "j2"]))
        model.add_set(SetDef(name="h", members=["CAP"]))

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        # Indexed constraint eqII(j) that contains pf(h,j)
        model.equations["eqII"] = EquationDef(
            name="eqII",
            domain=("j",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("sf", ()), Const(0.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["sf"] = VariableDef(name="sf", domain=(), lo=0.0)

        model.equalities = ["objdef", "eqII"]

        var_specs = [("obj", ()), ("sf", ())]
        eq_specs = [("objdef", ()), ("eqII", ("j1",)), ("eqII", ("j2",))]
        index_mapping = manual_index_mapping(var_specs, eq_specs)

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(0.0))

        J_eq = JacobianStructure(num_rows=3, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))
        # Derivative of eqII(j1) w.r.t. sf contains pf(h,j1) — h is extra
        J_eq.set_derivative(1, 1, ParamRef("pf", ("h", "j1")))
        J_eq.set_derivative(2, 1, ParamRef("pf", ("h", "j2")))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.multipliers_eq["nu_eqII"] = MultiplierDef(
            name="nu_eqII", domain=("j",), kind="eq", associated_constraint="eqII"
        )
        kkt.multipliers_bounds_lo[("sf", ())] = MultiplierDef(
            name="piL_sf", domain=(), kind="bound_lo", associated_constraint="sf"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_sf" in stationarity
        stat_eq = stationarity["stat_sf"]
        lhs = stat_eq.lhs_rhs[0]

        # Should contain Sum over h to wrap the uncontrolled index
        assert _find_sum_indices(lhs, {"h"}), (
            "Derivative with extra index 'h' beyond mult_domain ('j',) "
            "should be wrapped in sum(h, ...) to avoid GAMS Error $149"
        )

    def test_scalar_constraint_no_extra_wrapping(self, manual_index_mapping):
        """Scalar constraint contributing to scalar stationarity — no extra wrapping.

        Regression guard: when a scalar constraint contributes to a scalar
        stationarity equation, no Sum wrapping should be added.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        model.equations["con"] = EquationDef(
            name="con",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(5.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef", "con"]

        var_specs = [("obj", ()), ("x", ())]
        eq_specs = [("objdef", ()), ("con", ())]
        index_mapping = manual_index_mapping(var_specs, eq_specs)

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(2.0))

        J_eq = JacobianStructure(num_rows=2, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))
        J_eq.set_derivative(1, 1, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.multipliers_eq["nu_con"] = MultiplierDef(
            name="nu_con", domain=(), kind="eq", associated_constraint="con"
        )

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        lhs = stat_eq.lhs_rhs[0]
        # No Sum node should appear anywhere in the tree for a fully scalar
        # problem — no indices exist to wrap.
        assert not _contains_any_sum(
            lhs
        ), "No Sum wrapping expected for scalar constraint + scalar stationarity"
