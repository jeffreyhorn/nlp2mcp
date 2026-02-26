"""Tests for stationarity equation builder with mixed bounds.

Issue #828: When a variable has uniform lower bound but non-uniform upper bound
(or vice versa), the per-instance stationarity path must fall back to the
uniform bound key when the per-instance key is not found in multipliers.

Example: ibm1 has x(s) with lo=0 (uniform) and per-element up(s) (non-uniform).
The non-uniform upper bound triggers per-instance stationarity, but the lower
bound multiplier is stored at (x, ()) not (x, ("bin-1",)).
"""

from __future__ import annotations

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.ir.ast import Binary, Const, MultiplierRef, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem, MultiplierDef
from src.kkt.stationarity import build_stationarity_equations


def _find_multiplier_ref(expr, name_prefix: str) -> MultiplierRef | None:
    """Recursively find a MultiplierRef with a given name prefix in an expression tree."""
    if isinstance(expr, MultiplierRef) and expr.name.startswith(name_prefix):
        return expr
    if isinstance(expr, Binary):
        left = _find_multiplier_ref(expr.left, name_prefix)
        if left:
            return left
        return _find_multiplier_ref(expr.right, name_prefix)
    return None


@pytest.mark.unit
class TestMixedBoundsStationarity:
    """Tests for stationarity equations with mixed uniform/non-uniform bounds."""

    def test_uniform_lo_nonuniform_up_includes_piL(self, manual_index_mapping):
        """Issue #828: uniform lower bound + non-uniform upper bound.

        Variable x(s) with:
          - lo = 0 (uniform) → multiplier at (x, ()) with domain ("s",)
          - up("i1") = 10, up("i2") = 20 → multipliers at (x, ("i1",)), (x, ("i2",))

        Per-instance stationarity for x("i1") must include -piL_x("i1").
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Set s = {i1, i2}
        model.sets["s"] = ["i1", "i2"]

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("+", VarRef("x", ("s",)), Const(0.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("s",), lo=0.0)
        # Non-uniform upper bound
        model.variables["x"].up_map = {"i1": 10.0, "i2": 20.0}

        # Index mapping: obj, x("i1"), x("i2")
        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂obj/∂obj
        gradient.set_derivative(1, Const(1.0))  # ∂obj/∂x(i1)
        gradient.set_derivative(2, Const(1.0))  # ∂obj/∂x(i2)

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Uniform lower bound multiplier at (x, ()) with domain ("s",)
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=("s",), kind="bound_lo", associated_constraint="x"
        )

        # Non-uniform upper bound multipliers at per-instance keys
        kkt.multipliers_bounds_up[("x", ("i1",))] = MultiplierDef(
            name="piU_x_i1", domain=(), kind="bound_up", associated_constraint="x"
        )
        kkt.multipliers_bounds_up[("x", ("i2",))] = MultiplierDef(
            name="piU_x_i2", domain=(), kind="bound_up", associated_constraint="x"
        )

        stationarity = build_stationarity_equations(kkt)

        # Should have per-instance stationarity equations (triggered by non-uniform up)
        assert "stat_x_i1" in stationarity or "stat_x" in stationarity

        # Find the stationarity equation for x("i1") — check both naming patterns
        stat_eq = stationarity.get("stat_x_i1") or stationarity.get("stat_x")
        assert (
            stat_eq is not None
        ), f"Expected stat_x_i1 or stat_x, got keys: {list(stationarity.keys())}"

        # The LHS expression must contain a piL_x reference (lower bound multiplier)
        lhs = stat_eq.lhs_rhs[0]
        piL_ref = _find_multiplier_ref(lhs, "piL_x")
        assert piL_ref is not None, (
            "Issue #828: Lower bound multiplier piL_x not found in stationarity "
            "expression for x. This means the fallback to uniform key failed."
        )

    def test_nonuniform_lo_uniform_up_includes_piU(self, manual_index_mapping):
        """Symmetric case: non-uniform lower bound + uniform upper bound.

        Variable x(s) with:
          - lo("i1") = 1, lo("i2") = 2 → per-instance multipliers
          - up = 100 (uniform) → multiplier at (x, ()) with domain ("s",)

        Per-instance stationarity for x("i1") must include +piU_x("i1").
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.sets["s"] = ["i1", "i2"]

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("+", VarRef("x", ("s",)), Const(0.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("s",), up=100.0)
        # Non-uniform lower bound
        model.variables["x"].lo_map = {"i1": 1.0, "i2": 2.0}

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Non-uniform lower bound multipliers at per-instance keys
        kkt.multipliers_bounds_lo[("x", ("i1",))] = MultiplierDef(
            name="piL_x_i1", domain=(), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_lo[("x", ("i2",))] = MultiplierDef(
            name="piL_x_i2", domain=(), kind="bound_lo", associated_constraint="x"
        )

        # Uniform upper bound multiplier at (x, ())
        kkt.multipliers_bounds_up[("x", ())] = MultiplierDef(
            name="piU_x", domain=("s",), kind="bound_up", associated_constraint="x"
        )

        stationarity = build_stationarity_equations(kkt)

        # Find stationarity equation for x("i1")
        stat_eq = stationarity.get("stat_x_i1") or stationarity.get("stat_x")
        assert stat_eq is not None, f"Keys: {list(stationarity.keys())}"

        # Must include upper bound multiplier piU_x
        lhs = stat_eq.lhs_rhs[0]
        piU_ref = _find_multiplier_ref(lhs, "piU_x")
        assert piU_ref is not None, (
            "Issue #828: Upper bound multiplier piU_x not found in stationarity. "
            "The fallback to uniform key failed."
        )

    def test_both_uniform_bounds_no_fallback_needed(self, manual_index_mapping):
        """When both bounds are uniform, standard indexed path is used (no fallback)."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.sets["s"] = ["i1", "i2"]

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("+", VarRef("x", ("s",)), Const(0.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=("s",), lo=0.0, up=100.0)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Both bounds uniform at (x, ())
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=("s",), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_up[("x", ())] = MultiplierDef(
            name="piU_x", domain=("s",), kind="bound_up", associated_constraint="x"
        )

        stationarity = build_stationarity_equations(kkt)

        # Should produce indexed stationarity (stat_x, not stat_x_i1, stat_x_i2)
        assert "stat_x" in stationarity, f"Keys: {list(stationarity.keys())}"

        # Both piL and piU should appear
        lhs = stationarity["stat_x"].lhs_rhs[0]
        piL_ref = _find_multiplier_ref(lhs, "piL_x")
        piU_ref = _find_multiplier_ref(lhs, "piU_x")
        assert piL_ref is not None, "piL_x should appear in indexed stationarity"
        assert piU_ref is not None, "piU_x should appear in indexed stationarity"
