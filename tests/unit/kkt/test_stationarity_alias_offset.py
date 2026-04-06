"""Test alias offset correction in Jacobian transpose assembly.

Issue #1111: When a constraint contains sum(alias, ...) and the Jacobian
entry is from an offset group, the derivative coefficient should use
IndexOffset(alias, offset) instead of the base domain name.

Example: stateq(n,k).. x(n,k+1) = sum(np, a(n,np)*x(np,k))
For offset group (1,0): a(n,n) should become a(np+1,n)
"""

import pytest

from src.ir.ast import Binary, Const, IndexOffset, ParamRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, ParameterDef, SetDef
from src.kkt.stationarity import _apply_alias_offset_to_deriv


def _make_qabel_model_ir() -> ModelIR:
    """Build minimal ModelIR for qabel-style alias offset test."""
    ir = ModelIR()
    ir.sets["n"] = SetDef(name="n", members=["consumpt", "invest"])
    ir.sets["k"] = SetDef(name="k", members=["q1", "q2"])
    ir.aliases["np"] = AliasDef(name="np", target="n")
    ir.params["a"] = ParameterDef(name="a", domain=("n", "np"))
    return ir


@pytest.mark.unit
class TestApplyAliasOffsetToDeriv:
    """Test _apply_alias_offset_to_deriv produces correct IndexOffset."""

    def test_basic_offset_uses_alias(self):
        """a(n, n) with offset {n: 1} should produce a(np+1, n)."""
        ir = _make_qabel_model_ir()
        expr = ParamRef("a", ("n", "n"))
        offset_map = {"n": 1}
        preferred = {"n": "np"}

        result = _apply_alias_offset_to_deriv(expr, offset_map, ir, preferred)

        assert isinstance(result, ParamRef)
        assert result.name == "a"
        # Position 0: declared domain is 'n', matches offset → IndexOffset(np, 1)
        idx0 = result.indices[0]
        assert isinstance(idx0, IndexOffset), f"Expected IndexOffset, got {type(idx0)}"
        assert idx0.base == "np"
        assert idx0.offset == Const(1.0)
        # Position 1: declared domain is 'np' (not 'n'), no offset applied
        assert result.indices[1] == "n"

    def test_negative_offset(self):
        """a(n, n) with offset {n: -1} should produce a(np-1, n)."""
        ir = _make_qabel_model_ir()
        expr = ParamRef("a", ("n", "n"))
        offset_map = {"n": -1}
        preferred = {"n": "np"}

        result = _apply_alias_offset_to_deriv(expr, offset_map, ir, preferred)

        idx0 = result.indices[0]
        assert isinstance(idx0, IndexOffset)
        assert idx0.base == "np"
        assert idx0.offset == Const(-1.0)
        assert result.indices[1] == "n"

    def test_no_offset_unchanged(self):
        """a(n, n) with empty offset_map should be unchanged."""
        ir = _make_qabel_model_ir()
        expr = ParamRef("a", ("n", "n"))

        result = _apply_alias_offset_to_deriv(expr, {}, ir)

        assert result is expr  # Identity — no change

    def test_nested_in_binary(self):
        """Offset applied inside Binary expression."""
        ir = _make_qabel_model_ir()
        inner = ParamRef("a", ("n", "n"))
        expr = Binary("*", Const(-1.0), inner)
        offset_map = {"n": 1}
        preferred = {"n": "np"}

        result = _apply_alias_offset_to_deriv(expr, offset_map, ir, preferred)

        assert isinstance(result, Binary)
        assert isinstance(result.right, ParamRef)
        idx0 = result.right.indices[0]
        assert isinstance(idx0, IndexOffset)
        assert idx0.base == "np"
