"""Unit tests for stochastic function detection and execseed injection.

Sprint 19 Day 3: When a model uses stochastic functions like uniform() or
normal() in parameter assignments, the MCP emitter injects
``option execseed = 12345;`` to make the output deterministic.
"""

from src.emit.original_symbols import (
    _expr_contains_stochastic,
    has_stochastic_parameters,
)
from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef


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
