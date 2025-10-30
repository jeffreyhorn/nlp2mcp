"""Unit tests for variable kind preservation in emission.

Tests verify correct preservation of variable kinds (Finding #4):
- Primal variables grouped by their kind (Positive/Binary/Integer/etc.)
- Multipliers added to correct groups (free → CONTINUOUS, positive → POSITIVE)
- Correct GAMS block names emitted
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.templates import emit_variables
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import ObjSense, VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem, MultiplierDef


@pytest.mark.unit
class TestEmitVariableKinds:
    """Test variable kind preservation in emission."""

    def test_continuous_variables(self, manual_index_mapping):
        """Test emission of continuous (free) variables."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        assert "Variables" in result
        assert "obj" in result
        assert "x" in result
        # Should not have Positive Variables block
        assert "Positive Variables" not in result

    def test_positive_variables(self, manual_index_mapping):
        """Test emission of positive variables."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.POSITIVE)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        assert "Positive Variables" in result
        assert "x" in result

    def test_binary_variables(self, manual_index_mapping):
        """Test emission of binary variables."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["y"] = VariableDef(name="y", domain=(), kind=VarKind.BINARY)

        index_mapping = manual_index_mapping([("obj", ()), ("y", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        assert "Binary Variables" in result
        assert "y" in result

    def test_integer_variables(self, manual_index_mapping):
        """Test emission of integer variables."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["z"] = VariableDef(name="z", domain=(), kind=VarKind.INTEGER)

        index_mapping = manual_index_mapping([("obj", ()), ("z", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        assert "Integer Variables" in result
        assert "z" in result

    def test_mixed_variable_kinds(self, manual_index_mapping):
        """Test emission with multiple variable kinds."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.POSITIVE)
        model.variables["y"] = VariableDef(name="y", domain=(), kind=VarKind.BINARY)
        model.variables["z"] = VariableDef(name="z", domain=(), kind=VarKind.INTEGER)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ()), ("y", ()), ("z", ())])
        gradient = GradientVector(num_cols=4, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=4, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=4, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        # All four blocks should be present
        assert "Variables" in result
        assert "Positive Variables" in result
        assert "Binary Variables" in result
        assert "Integer Variables" in result
        # Each variable in correct block
        lines = result.split("\n")
        assert any(
            "obj" in line and "Variables" in result[: result.index(line)]
            for line in lines
            if "obj" in line
        )

    def test_equality_multipliers_are_continuous(self, manual_index_mapping):
        """Test that equality multipliers (ν) are in Variables block."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        # Add equality multiplier
        kkt.multipliers_eq["nu_balance"] = MultiplierDef(
            name="nu_balance", domain=(), kind="eq", associated_constraint="balance"
        )

        result = emit_variables(kkt)
        assert "Variables" in result
        assert "nu_balance" in result
        # Verify it's in Variables block, not Positive Variables
        vars_section = (
            result.split("Positive Variables")[0] if "Positive Variables" in result else result
        )
        assert "nu_balance" in vars_section

    def test_inequality_multipliers_are_positive(self, manual_index_mapping):
        """Test that inequality multipliers (λ) are in Positive Variables block."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        # Add inequality multiplier
        kkt.multipliers_ineq["lam_capacity"] = MultiplierDef(
            name="lam_capacity", domain=(), kind="ineq", associated_constraint="capacity"
        )

        result = emit_variables(kkt)
        assert "Positive Variables" in result
        assert "lam_capacity" in result

    def test_bound_multipliers_are_positive(self, manual_index_mapping):
        """Test that bound multipliers (π^L, π^U) are in Positive Variables block."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(
            name="x", domain=(), kind=VarKind.CONTINUOUS, lo=0.0, up=10.0
        )

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        # Add bound multipliers (use tuple keys)
        kkt.multipliers_bounds_lo[("x", ())] = MultiplierDef(
            name="piL_x", domain=(), kind="bound_lo", associated_constraint="x"
        )
        kkt.multipliers_bounds_up[("x", ())] = MultiplierDef(
            name="piU_x", domain=(), kind="bound_up", associated_constraint="x"
        )

        result = emit_variables(kkt)
        assert "Positive Variables" in result
        assert "piL_x" in result
        assert "piU_x" in result

    def test_indexed_variables_with_domain(self, manual_index_mapping):
        """Test emission of indexed variables with domain."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = VariableDef(name="x", domain=("i",), kind=VarKind.POSITIVE)

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i1",)), ("x", ("i2",))])
        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        result = emit_variables(kkt)
        assert "Positive Variables" in result
        # Should have domain in declaration
        assert "x(i)" in result
