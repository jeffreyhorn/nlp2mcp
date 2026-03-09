"""Unit tests for fx_map emission in emit_gams_mcp().

Issue #1021: Numeric per-element .fx bounds from VariableDef.fx_map must be
re-emitted as .fx(...) = ...; lines in the MCP output, with literal UEL
quoting via _quote_uel.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import emit_gams_mcp
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import ObjSense, SetDef, VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem


@pytest.mark.unit
class TestFxMapEmission:
    """Tests for numeric fx_map emission in emit_gams_mcp()."""

    def test_scalar_fx_map_emitted(self, manual_index_mapping):
        """A variable with fx_map entries emits .fx(...) = ...; lines."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["h"] = SetDef(name="h", members=["CAP", "LAB"])

        pf = VariableDef(name="pf", domain=("h",), kind=VarKind.CONTINUOUS)
        pf.fx_map[("LAB",)] = 1.0
        model.variables["pf"] = pf

        index_mapping = manual_index_mapping([("obj", ()), ("pf", ("LAB",))])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        # LAB is a literal element (not a set name), so it should be quoted
        assert "pf.fx('LAB') = 1;" in result

    def test_multi_index_fx_map_emitted(self, manual_index_mapping):
        """fx_map with multi-dimensional indices emits proper .fx lines."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["r"] = SetDef(name="r", members=["Reg1", "Reg2"])
        model.sets["c"] = SetDef(name="c", members=["Com1"])

        x = VariableDef(name="X", domain=("r", "r", "c"), kind=VarKind.CONTINUOUS)
        x.fx_map[("Reg1", "Reg1", "Com1")] = 0.0
        x.fx_map[("Reg2", "Reg2", "Com1")] = 0.0
        model.variables["X"] = x

        index_mapping = manual_index_mapping([("obj", ()), ("X", ("Reg1", "Reg1", "Com1"))])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        # Elements are quoted because they're not domain variable names
        assert "X.fx('Reg1','Reg1','Com1') = 0;" in result
        assert "X.fx('Reg2','Reg2','Com1') = 0;" in result

    def test_fx_map_integer_formatting(self, manual_index_mapping):
        """Whole-number fx_map values are formatted as integers (no decimal)."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        model.sets["i"] = SetDef(name="i", members=["a"])

        x = VariableDef(name="x", domain=("i",), kind=VarKind.CONTINUOUS)
        x.fx_map[("a",)] = 5.0  # Should emit as "5", not "5.0"
        model.variables["x"] = x

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("a",))])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        assert "x.fx('a') = 5;" in result

    def test_no_fx_map_no_fx_lines(self, manual_index_mapping):
        """Variable without fx_map produces no .fx lines."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        x = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        model.variables["x"] = x

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        assert "x.fx(" not in result

    def test_fx_map_element_colliding_with_set_name(self, manual_index_mapping):
        """fx_map element that collides with a set/alias name must still be quoted.

        If set 'r' has member 'r' (self-referencing name), the element must be
        emitted as x.fx('r') not x.fx(r) — the latter would be interpreted by
        GAMS as a running index reference.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")
        model.variables["obj"] = VariableDef(name="obj", domain=(), kind=VarKind.CONTINUOUS)

        # Set 'i' with member 'i' — element name collides with set name
        model.sets["i"] = SetDef(name="i", members=["i", "j"])

        x = VariableDef(name="x", domain=("i",), kind=VarKind.CONTINUOUS)
        x.fx_map[("i",)] = 0.0
        model.variables["x"] = x

        index_mapping = manual_index_mapping([("obj", ()), ("x", ("i",))])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        result = emit_gams_mcp(kkt)

        # Must be quoted — bare 'i' would be a running index
        assert "x.fx('i') = 0;" in result
