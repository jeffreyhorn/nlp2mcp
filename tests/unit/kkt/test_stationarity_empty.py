"""Tests for empty stationarity equation detection (#826).

When a variable's stationarity equation simplifies to 0 =E= 0 (e.g., because
the stationarity builder can't propagate derivatives through subset access
patterns), the equation must be removed and the variable fixed to 0.
"""

from __future__ import annotations

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.stationarity import build_stationarity_equations


@pytest.mark.unit
class TestEmptyStationarityDetection:
    """Tests for detecting and removing empty stationarity equations."""

    def _make_model_with_extra_var(self, manual_index_mapping, extra_has_jacobian: bool):
        """Helper: creates a model with obj, x (has gradient), and lam (may have zero Jacobian).

        Both x and lam appear in equation bodies (so they pass the referenced check).
        x always has a nonzero gradient. lam's Jacobian column is either populated
        or left empty depending on extra_has_jacobian.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # obj =e= x + lam  (both referenced)
        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("+", VarRef("x", ()), VarRef("lam", ())),
            ),
        )
        # eq1.. x + lam =e= 1 (non-objdef equation so Jacobian terms are included)
        model.equations["eq1"] = EquationDef(
            name="eq1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("+", VarRef("x", ()), VarRef("lam", ())), Const(1.0)),
        )
        model.equalities = {"objdef", "eq1"}

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())
        model.variables["lam"] = VariableDef(name="lam", domain=())

        vars_list = [("obj", ()), ("x", ()), ("lam", ())]
        eqs_list = [("objdef", ()), ("eq1", ())]
        index_mapping = manual_index_mapping(vars_list, eqs_list)

        # Gradient: d(obj)/d(obj)=1, d(obj)/d(x)=1, d(obj)/d(lam)=0
        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(0.0))

        # Jacobian for equalities (2 rows: objdef, eq1)
        J_eq = JacobianStructure(num_rows=2, num_cols=3, index_mapping=index_mapping)
        # objdef: d(obj-x-lam)/d(obj)=1, d/d(x)=-1, d/d(lam)=-1
        J_eq.set_derivative(0, 0, Const(1.0))
        J_eq.set_derivative(0, 1, Const(-1.0))
        J_eq.set_derivative(0, 2, Const(-1.0))
        # eq1: d(x+lam-1)/d(x)=1
        J_eq.set_derivative(1, 1, Const(1.0))
        if extra_has_jacobian:
            # lam has nonzero Jacobian in eq1
            J_eq.set_derivative(1, 2, Const(1.0))
        # else: lam column in eq1 is empty (simulating failed derivative propagation)

        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.multipliers_eq["nu_eq1"] = MultiplierDef(
            name="nu_eq1", domain=(), kind="eq", associated_constraint="eq1"
        )

        return kkt

    def test_empty_stationarity_detected(self, manual_index_mapping):
        """Issue #826: Variable with zero Jacobian column has empty stationarity.

        When lam has zero gradient AND zero Jacobian column in non-objdef
        equations, its stationarity simplifies to 0 =E= 0. This should be
        detected and the variable recorded in empty_stationarity_vars.
        The equation is kept in the dict (for MCP pairing) but the emitter
        will fix the variable to 0.
        """
        kkt = self._make_model_with_extra_var(manual_index_mapping, extra_has_jacobian=False)
        stationarity = build_stationarity_equations(kkt)

        # lam has empty stationarity → recorded in empty_stationarity_vars
        assert "stat_lam" in stationarity  # kept for MCP pairing
        assert "lam" in kkt.empty_stationarity_vars

        # x still has non-empty stationarity
        assert "stat_x" in stationarity
        assert "x" not in kkt.empty_stationarity_vars

    def test_nonempty_stationarity_not_removed(self, manual_index_mapping):
        """Variable with nonzero Jacobian column keeps its stationarity."""
        kkt = self._make_model_with_extra_var(manual_index_mapping, extra_has_jacobian=True)
        stationarity = build_stationarity_equations(kkt)

        # lam has nonzero Jacobian → stationarity kept
        assert "stat_lam" in stationarity
        assert "lam" not in kkt.empty_stationarity_vars

        # x also kept
        assert "stat_x" in stationarity
