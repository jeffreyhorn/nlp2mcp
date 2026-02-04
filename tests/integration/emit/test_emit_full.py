"""Integration tests for full GAMS MCP emission.

Tests the complete emission pipeline from KKT system to GAMS code.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import emit_gams_mcp
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef, VarKind
from src.kkt.assemble import assemble_kkt_system


@pytest.mark.integration
class TestFullGAMSEmission:
    """Test full GAMS emission from KKT systems."""

    def test_emit_minimal_nlp(self, manual_index_mapping):
        """Test emission for minimal NLP: min x^2."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0)

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        # Assemble KKT
        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        # Emit GAMS
        output = emit_gams_mcp(kkt)

        # Verify structure
        assert isinstance(output, str)
        assert len(output) > 0
        assert "Model mcp_model" in output
        assert "Solve mcp_model using MCP" in output
        assert "Variables" in output
        assert "Equations" in output

    def test_emit_preserves_variable_kinds(self, manual_index_mapping):
        """Test that variable kinds are preserved in emission."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary("+", VarRef("x", ()), VarRef("y", ())),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.POSITIVE)
        model.variables["y"] = VariableDef(name="y", domain=())

        model.equalities = ["objdef"]

        # Set up derivatives
        index_mapping = manual_index_mapping([("obj", ()), ("x", ()), ("y", ())])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Should have Positive Variables block (for x and multipliers)
        assert "Positive Variables" in output

    def test_emit_objective_equation_pairing(self, manual_index_mapping):
        """Test that objective defining equation is paired with objvar."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Objective equation should be paired with obj
        assert ".obj" in output

        # Should NOT have stationarity for obj
        assert "stat_obj" not in output

    def test_emit_with_inequality(self, manual_index_mapping):
        """Test emission with inequality constraints."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.equations["ineq1"] = EquationDef(
            name="ineq1",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(VarRef("x", ()), Const(10.0)),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]
        model.inequalities = ["ineq1"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())], [("ineq1", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_ineq.set_derivative(0, 1, Const(1.0))

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Should have inequality complementarity
        assert "lam_" in output or "comp_" in output

    def test_emit_with_bounds(self, manual_index_mapping):
        """Test emission with variable bounds."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), Binary("^", VarRef("x", ()), Const(2.0))),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=(), lo=0.0, up=10.0)

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Should have bound multipliers
        assert "piL_" in output or "piU_" in output

    def test_emit_without_comments(self, manual_index_mapping):
        """Test emission with comments disabled."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt, add_comments=False)

        # Should not have comment blocks
        assert "$onText" not in output
        assert "Generated by nlp2mcp" not in output

        # But still has essential structure
        assert "Model mcp_model" in output

    def test_emit_custom_model_name(self, manual_index_mapping):
        """Test emission with custom model name."""
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt, model_name="my_model")

        # Should use custom model name
        assert "Model my_model" in output
        assert "Solve my_model using MCP" in output

    def test_emit_with_prefix_variable_names(self, manual_index_mapping):
        """Test emission with variables that are prefixes of each other.

        Regression test for issue where 'x' would incorrectly match when
        looking for 'xy' in stationarity equation names.
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(
                VarRef("obj", ()),
                Binary(
                    "+",
                    VarRef("x", ()),
                    VarRef("xy", ()),
                ),
            ),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())
        model.variables["xy"] = VariableDef(name="xy", domain=())

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ()), ("xy", ())])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(1, Const(1.0))
        gradient.set_derivative(2, Const(1.0))

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Should have stationarity for both x and xy
        assert "stat_x" in output
        assert "stat_xy" in output

        # Should pair correctly: stat_x.x and stat_xy.xy
        assert "stat_x.x" in output
        assert "stat_xy.xy" in output

    def test_emit_alias_ordering(self, manual_index_mapping):
        """Test that sets and aliases are emitted in correct order.

        Sprint 17 Day 10 (Issue #621): Verify the full emission correctly
        orders sets and aliases to avoid undefined symbol errors.
        Order should be:
        1. Pre-alias sets (sets that don't depend on aliases)
        2. Pre-set aliases (aliases targeting pre-alias sets)
        3. Post-alias sets (sets that depend on aliases)
        4. Post-set aliases (aliases targeting post-alias sets)
        """
        from src.ir.symbols import AliasDef, SetDef

        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="obj")

        # Set i is pre-alias (no alias dependency)
        model.sets["i"] = SetDef(name="i", members=["i1", "i2", "i3"])
        # Set ij depends on alias j, so it's post-alias
        model.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        # Alias j targets pre-alias set i
        model.aliases["j"] = AliasDef(name="j", target="i")

        model.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )

        model.variables["obj"] = VariableDef(name="obj", domain=())
        model.variables["x"] = VariableDef(name="x", domain=())

        model.equalities = ["objdef"]

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)

        output = emit_gams_mcp(kkt)

        # Find positions of key elements in the output
        pos_set_i = output.find("i /i1, i2, i3/")
        pos_alias_j = output.find("Alias(i, j);")
        pos_set_ij = output.find("ij(i,j)")

        # Verify all elements are present
        assert pos_set_i != -1, "Set i should be in output"
        assert pos_alias_j != -1, "Alias j should be in output"
        assert pos_set_ij != -1, "Set ij should be in output"

        # Verify correct ordering: set i -> Alias j -> set ij
        assert pos_set_i < pos_alias_j, "Set i must come before Alias j"
        assert pos_alias_j < pos_set_ij, "Alias j must come before set ij"
