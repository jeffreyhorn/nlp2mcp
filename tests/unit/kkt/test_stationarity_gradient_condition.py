"""Tests for Stage 4 gradient-condition fallback in stationarity builder.

Issue #1112: When gradient entries for a variable all share a common
DollarConditional guard (from a conditioned objective sum), the stationarity
equation should inherit that guard — but only when Stages 1-3 found no
condition AND the variable has no unconditioned accesses in any constraint.
"""

from __future__ import annotations

import pytest

from src.ad.gradient import GradientVector, extract_gradient_conditions
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, DollarConditional, ParamRef, Sum, SymbolRef, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem
from src.kkt.stationarity import build_stationarity_equations


@pytest.mark.unit
class TestStationarityGradientConditionFallback:
    """Stage 4: gradient-derived condition applied to stationarity equations."""

    def test_gradient_condition_applied_via_stage4(self, manual_index_mapping):
        """Stage 4 gradient condition used when Stages 1-3 find nothing.

        x appears only in model.objective.expr (not in any equation body),
        so _find_variable_access_condition (Stage 1) won't find it in any
        equation.  Stages 2-3 also return None.  Stage 4 should apply the
        gradient-derived condition from kkt.gradient_conditions.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.sets["i"] = ["a", "b"]

        # Put x in objective.expr so it's counted as referenced, but NOT in
        # any equation body — this ensures Stages 1-3 return None.
        model.objective.expr = Sum(
            index_sets=("i",),
            condition=ParamRef("xw", ("i",)),
            body=VarRef("x", ("i",)),
        )

        # objdef references only obj (not x)
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("a",)), ("x", ("b",))])

        # Gradient entries carry the condition: deriv * (1$xw(i))
        cond = ParamRef("xw", ("i",))
        factor = DollarConditional(Const(1.0), cond)

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # d/d obj
        gradient.set_derivative(1, Binary("*", Const(2.0), factor))  # d/d x(a)
        gradient.set_derivative(2, Binary("*", Const(3.0), factor))  # d/d x(b)

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Populate gradient_conditions as assemble.py would
        kkt.gradient_conditions = extract_gradient_conditions(gradient)
        assert "x" in kkt.gradient_conditions

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        # Stage 4 should apply the exact gradient condition object
        assert stat_eq.condition is kkt.gradient_conditions["x"]

    def test_gradient_condition_skipped_when_unconditioned_access(self, manual_index_mapping):
        """Stage 4 gradient condition NOT used when variable has unconditioned access."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.sets["i"] = ["a", "b"]

        # Put x in objective.expr (not in objdef body)
        model.objective.expr = Sum(
            index_sets=("i",),
            condition=ParamRef("xw", ("i",)),
            body=VarRef("x", ("i",)),
        )

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        # eq1(i).. x(i) =e= 1  — UNCONDITIONED access in constraint
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i",)), Const(1.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("a",)), ("x", ("b",))],
            [("objdef", ()), ("eq1", ("a",)), ("eq1", ("b",))],
        )

        # Gradient entries carry the condition
        cond = ParamRef("xw", ("i",))
        factor = DollarConditional(Const(1.0), cond)

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), factor))
        gradient.set_derivative(2, Binary("*", Const(3.0), factor))

        # Jacobian: eq1 references x unconditionally
        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 1, Const(1.0))  # d eq1(a) / d x(a)
        J_eq.set_derivative(1, 2, Const(1.0))  # d eq1(b) / d x(b)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.gradient_conditions = extract_gradient_conditions(gradient)
        assert "x" in kkt.gradient_conditions

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        # Stage 4 must NOT apply gradient condition because eq1 accesses x
        # unconditionally — suppressing instances would be incorrect
        assert stat_eq.condition is None

    def test_gradient_condition_applied_when_eq_level_condition_guards(self, manual_index_mapping):
        """Stage 4 applied when constraint references x but has eq-level condition.

        eq1(i)$active(i).. x(i) =e= 1  — the equation-level $active(i) acts
        as an enclosing guard, so x is NOT truly unconditioned and Stage 4
        should still apply the gradient condition.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.sets["i"] = ["a", "b"]

        model.objective.expr = Sum(
            index_sets=("i",),
            condition=ParamRef("xw", ("i",)),
            body=VarRef("x", ("i",)),
        )

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Const(0.0)),
        )

        # eq1(i)$active(i).. x(i) =e= 1  — eq-level condition guards access
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i",)), Const(1.0)),
            condition=SymbolRef("active"),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("i",))

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ("a",)), ("x", ("b",))],
            [("objdef", ()), ("eq1", ("a",)), ("eq1", ("b",))],
        )

        cond = ParamRef("xw", ("i",))
        factor = DollarConditional(Const(1.0), cond)

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), factor))
        gradient.set_derivative(2, Binary("*", Const(3.0), factor))

        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        J_eq.set_derivative(0, 1, Const(1.0))
        J_eq.set_derivative(1, 2, Const(1.0))
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        kkt.gradient_conditions = extract_gradient_conditions(gradient)
        assert "x" in kkt.gradient_conditions

        stationarity = build_stationarity_equations(kkt)

        assert "stat_x" in stationarity
        stat_eq = stationarity["stat_x"]
        # Stage 4 SHOULD apply: eq1's equation-level $active(i) means x is
        # not accessed unconditionally, so the gradient condition is safe
        assert stat_eq.condition is kkt.gradient_conditions["x"]
