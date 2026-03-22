"""Sprint 23 Day 1 tests — unit and integration.

Unit tests (in-memory, no I/O):
1. LhsConditionalAssign in expr_to_gams (fallback to RHS)
2. LhsConditionalAssign stripping in _bound_expr

Integration tests (subprocess translation of GAMSlib models):
3. Expression-based bounds emitted for complementarity variables
4. Priority 3 POSITIVE init clamping to .up
5. execError reset after computed parameters
6. LhsConditionalAssign translate recovery
"""

import os
import subprocess
import sys

import pytest

from src.emit.expr_to_gams import expr_to_gams
from src.ir.ast import (
    Binary,
    Const,
    LhsConditionalAssign,
    ParamRef,
    SymbolRef,
)
from src.kkt.complementarity import _bound_expr
from src.kkt.partition import BoundDef


@pytest.mark.unit
class TestLhsConditionalAssignExprToGams:
    """LhsConditionalAssign should emit only the RHS in expr_to_gams."""

    def test_simple_lhs_conditional(self):
        """LhsConditionalAssign emits rhs expression."""
        node = LhsConditionalAssign(
            rhs=ParamRef("b", ("r",)),
            condition=SymbolRef("cond"),
        )
        result = expr_to_gams(node)
        assert result == "b(r)"

    def test_lhs_conditional_nested_in_binary(self):
        """LhsConditionalAssign inside Binary emits correctly."""
        node = Binary(
            "+",
            Const(1),
            LhsConditionalAssign(
                rhs=ParamRef("x", ("i",)),
                condition=SymbolRef("flag"),
            ),
        )
        result = expr_to_gams(node)
        assert result == "1 + x(i)"

    def test_lhs_conditional_with_complex_rhs(self):
        """LhsConditionalAssign with arithmetic RHS."""
        node = LhsConditionalAssign(
            rhs=Binary("*", ParamRef("a"), Const(2)),
            condition=Binary(">", SymbolRef("i"), Const(0)),
        )
        result = expr_to_gams(node)
        assert result == "a * 2"


@pytest.mark.unit
class TestBoundExprLhsConditional:
    """_bound_expr should strip LhsConditionalAssign wrapper."""

    def test_bound_expr_strips_lhs_conditional(self):
        """_bound_expr returns .rhs from LhsConditionalAssign."""
        rhs = ParamRef("b", ("r",))
        cond = SymbolRef("cond")
        lca = LhsConditionalAssign(rhs=rhs, condition=cond)
        bd = BoundDef("up", 0.0, ("r",), expr=lca)
        result = _bound_expr(bd)
        assert result is rhs

    def test_bound_expr_passes_through_normal_expr(self):
        """_bound_expr returns expr unchanged when not LhsConditionalAssign."""
        expr = ParamRef("ub", ("i",))
        bd = BoundDef("up", 0.0, ("i",), expr=expr)
        result = _bound_expr(bd)
        assert result is expr

    def test_bound_expr_const_fallback(self):
        """_bound_expr returns Const(value) when no expr."""
        bd = BoundDef("lo", 5.0, ("i",))
        result = _bound_expr(bd)
        assert isinstance(result, Const) and result.value == 5.0


def _translate_model(gms_path: str) -> str:
    """Helper: translate a .gms file via CLI and return the MCP code."""
    import tempfile

    with tempfile.NamedTemporaryFile(suffix="_mcp.gms", delete=False) as f:
        out_path = f.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", gms_path, "-o", out_path],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            pytest.fail(f"Translation failed: {result.stderr}")
        with open(out_path) as f:
            return f.read()
    finally:
        if os.path.exists(out_path):
            os.unlink(out_path)


@pytest.mark.integration
class TestExprBasedBoundsForComplementarity:
    """Expression-based bounds must be emitted even for complementarity vars."""

    def test_rocket_expr_bound_emitted(self):
        """Verify expression-based .up is emitted for rocket model."""
        gms_path = os.path.join("data", "gamslib", "raw", "rocket.gms")
        if not os.path.exists(gms_path):
            pytest.skip("rocket.gms not available")
        code = _translate_model(gms_path)
        assert "t.up(h) = T_c * m_0 * g_0;" in code


@pytest.mark.integration
class TestPositiveInitClamping:
    """Priority 3 POSITIVE default init should be clamped to .up."""

    def test_gtm_positive_init_clamped(self):
        """s.l(i) = 1 must be followed by min(s.l(i), s.up(i)) clamp."""
        gms_path = os.path.join("data", "gamslib", "raw", "gtm.gms")
        if not os.path.exists(gms_path):
            pytest.skip("gtm.gms not available")
        code = _translate_model(gms_path)
        assert "s.l(i) = 1;" in code
        assert "s.l(i) = min(s.l(i), s.up(i));" in code


@pytest.mark.integration
class TestExecErrorReset:
    """execError = 0 should appear after computed parameter assignments."""

    def test_exec_error_reset_present(self):
        """Models with computed parameters should have execError = 0."""
        # Use gtm which has computed parameters (supc, supb, supa, etc.)
        gms_path = os.path.join("data", "gamslib", "raw", "gtm.gms")
        if not os.path.exists(gms_path):
            pytest.skip("gtm.gms not available")
        code = _translate_model(gms_path)
        assert "execError = 0;" in code


@pytest.mark.integration
class TestLhsConditionalTranslateRecovery:
    """Models that previously failed with LhsConditionalAssign should translate."""

    @pytest.mark.parametrize("model", ["ampl", "agreste", "cesam", "korcge"])
    def test_translate_succeeds(self, model):
        """Model should translate without error."""
        gms_path = os.path.join("data", "gamslib", "raw", f"{model}.gms")
        if not os.path.exists(gms_path):
            pytest.skip(f"{model}.gms not available")
        code = _translate_model(gms_path)
        assert "Solve mcp_model using MCP" in code
