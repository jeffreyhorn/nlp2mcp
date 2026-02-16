"""Unit tests for stochastic function detection and execseed injection.

Sprint 19 Day 3: When a model uses stochastic functions like uniform() or
normal() in parameter assignments, the MCP emitter injects
``execseed = 12345;`` to make the output deterministic.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.emit_gams import emit_gams_mcp
from src.emit.original_symbols import (
    _expr_contains_stochastic,
    has_stochastic_parameters,
)
from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, ParameterDef, Rel, VariableDef
from src.kkt.assemble import assemble_kkt_system


class TestExprContainsStochastic:
    """Test _expr_contains_stochastic helper."""

    def test_uniform_call(self):
        """uniform() is stochastic."""
        expr = Call("uniform", (Const(1.0), Const(10.0)))
        assert _expr_contains_stochastic(expr) is True

    def test_normal_call(self):
        """normal() is stochastic."""
        expr = Call("normal", (Const(0.0), Const(1.0)))
        assert _expr_contains_stochastic(expr) is True

    def test_nested_stochastic(self):
        """Stochastic call nested in a binary expression."""
        expr = Binary("+", Call("uniform", (Const(1.0), Const(10.0))), Const(5.0))
        assert _expr_contains_stochastic(expr) is True

    def test_deterministic_call(self):
        """log() is not stochastic."""
        expr = Call("log", (VarRef("x", ()),))
        assert _expr_contains_stochastic(expr) is False

    def test_plain_const(self):
        """A constant is not stochastic."""
        assert _expr_contains_stochastic(Const(42.0)) is False

    def test_case_insensitive(self):
        """Stochastic detection is case-insensitive."""
        expr = Call("Uniform", (Const(1.0), Const(10.0)))
        assert _expr_contains_stochastic(expr) is True


class TestHasStochasticParameters:
    """Test has_stochastic_parameters on ModelIR."""

    def test_model_with_stochastic_param(self):
        """ModelIR with a uniform() parameter expression returns True."""
        model = ModelIR()
        p = ParameterDef(name="x", domain=("i",))
        p.expressions.append((("p1",), Call("uniform", (Const(1.0), Const(10.0)))))
        model.params["x"] = p
        assert has_stochastic_parameters(model) is True

    def test_model_without_stochastic_param(self):
        """ModelIR with only deterministic expressions returns False."""
        model = ModelIR()
        p = ParameterDef(name="c", domain=("i",))
        p.expressions.append((("a",), Binary("*", Const(2.0), Const(3.0))))
        model.params["c"] = p
        assert has_stochastic_parameters(model) is False

    def test_empty_model(self):
        """ModelIR with no parameters returns False."""
        model = ModelIR()
        assert has_stochastic_parameters(model) is False

    def test_predefined_constants_skipped(self):
        """Predefined GAMS constants are never flagged as stochastic."""
        model = ModelIR()
        # pi is a predefined constant — even if it had expressions, skip it
        p = ParameterDef(name="pi")
        p.expressions.append(((), Call("uniform", (Const(0.0), Const(1.0)))))
        model.params["pi"] = p
        assert has_stochastic_parameters(model) is False


class TestExecseedEmission:
    """Integration tests: verify execseed appears in emitted GAMS code."""

    @pytest.mark.integration
    def test_execseed_emitted_for_stochastic_model(self, manual_index_mapping):
        """emit_gams_mcp includes 'execseed = 12345;' when model has uniform()."""
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

        # Add a stochastic parameter
        p = ParameterDef(name="data", domain=("i",))
        p.expressions.append((("p1",), Call("uniform", (Const(1.0), Const(10.0)))))
        model.params["data"] = p

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
        output = emit_gams_mcp(kkt)

        assert "execseed = 12345;" in output

    @pytest.mark.integration
    def test_execseed_not_emitted_for_deterministic_model(self, manual_index_mapping):
        """emit_gams_mcp omits execseed when model has no stochastic functions."""
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

        index_mapping = manual_index_mapping([("obj", ()), ("x", ())])
        gradient = GradientVector(num_cols=2, index_mapping=index_mapping)
        gradient.set_derivative(1, Binary("*", Const(2.0), VarRef("x", ())))
        J_eq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2, index_mapping=index_mapping)

        kkt = assemble_kkt_system(model, gradient, J_eq, J_ineq)
        output = emit_gams_mcp(kkt)

        assert "execseed" not in output
