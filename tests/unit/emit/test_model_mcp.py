"""Unit tests for MCP model declaration emission.

Tests emit_model_mcp() to verify correct equation-variable pairing
in the Model MCP declaration block.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.model import emit_model_mcp
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, VariableDef
from src.kkt.kkt_system import KKTSystem
from src.kkt.stationarity import build_stationarity_equations


@pytest.mark.unit
class TestMCPPairingSimpleVariableObjective:
    """Test MCP pairing when the objective is a simple variable (no defining equation).

    GitHub Issue #624: When the objective is 'minimize r' with no defining equation
    like 'objdef.. obj =E= expr', the variable r still needs stationarity and
    its stat_r.r pairing must appear in the Model MCP declaration.
    """

    def test_simple_variable_objective_included_in_pairing(self, manual_index_mapping):
        """Test that stat_r.r appears in MCP model when objective is 'minimize r'.

        Simulates the circle.gms pattern:
        - Objective: minimize r (simple variable, no defining equation)
        - Variables: a, b, r
        - The stationarity equation stat_r is generated (needs_stationarity=True)
        - The pairing stat_r.r must appear in Model mcp_model / ... /;
        """
        model = ModelIR()
        model.objective = ObjectiveIR(sense=ObjSense.MIN, objvar="r")

        # No objdef equation - this is a simple variable objective
        model.variables["r"] = VariableDef(name="r", domain=(), lo=0.0)
        model.variables["a"] = VariableDef(name="a", domain=())
        model.variables["b"] = VariableDef(name="b", domain=())

        # Add a constraint that references a, b, and r
        # Use a + b - r =L= 0 so that r is NOT a bare VarRef on either side
        # (otherwise extract_objective_info would treat this as objdef for r)
        model.equations["circle"] = EquationDef(
            name="circle",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(
                Binary("-", Binary("+", VarRef("a", ()), VarRef("b", ())), VarRef("r", ())),
                Const(0.0),
            ),
        )
        model.inequalities = ["circle"]
        model.equalities = []

        # Set up KKT system
        index_mapping = manual_index_mapping([("r", ()), ("a", ()), ("b", ())])

        gradient = GradientVector(num_cols=3, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))  # ∂r/∂r = 1
        gradient.set_derivative(1, Const(0.0))  # ∂r/∂a = 0
        gradient.set_derivative(2, Const(0.0))  # ∂r/∂b = 0

        J_eq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=3, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)

        # Build stationarity (should include stat_r because needs_stationarity=True)
        kkt.stationarity = build_stationarity_equations(kkt)

        assert (
            "stat_r" in kkt.stationarity
        ), "stat_r should be generated for simple variable objective"

        # Emit model MCP declaration
        model_text = emit_model_mcp(kkt)

        # Verify stat_r.r is in the model declaration
        assert (
            "stat_r.r" in model_text
        ), f"stat_r.r pairing missing from MCP model declaration. Model text:\n{model_text}"
        assert "stat_a.a" in model_text
        assert "stat_b.b" in model_text

    def test_standard_objective_with_defining_equation_excludes_objvar(self, manual_index_mapping):
        """Test that stat_obj is NOT generated for standard 'obj =E= expr' objectives.

        When there IS a defining equation like 'objdef.. obj =E= x^2',
        the objective variable should NOT have a stationarity equation.
        """
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

        index_mapping = manual_index_mapping(
            [("obj", ()), ("x", ())],
            [("objdef", ())],
        )

        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))

        J_eq = JacobianStructure(num_rows=1, num_cols=2, index_mapping=index_mapping)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = KKTSystem(model_ir=model, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)
        kkt.stationarity = build_stationarity_equations(kkt)

        # stat_obj should NOT exist for standard objective
        assert "stat_obj" not in kkt.stationarity

        model_text = emit_model_mcp(kkt)

        # stat_obj.obj should NOT be in model declaration
        assert "stat_obj.obj" not in model_text
        # stat_x.x should be present
        assert "stat_x.x" in model_text
