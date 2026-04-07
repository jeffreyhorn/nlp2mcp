"""Test IndexOffset base remapping in _replace_indices_in_expr.

When the AD engine differentiates through a sum with alias cross-terms,
_partial_collapse_sum substitutes symbolic sum indices with concrete element
values, producing IndexOffset nodes with concrete bases like
IndexOffset("i1", Const(1)).  _replace_indices_in_expr must remap such
concrete bases back to the declared domain name (IndexOffset("i", Const(1)))
while preserving symbolic bases (set names and aliases) as-is.
"""

import pytest

from src.ir.ast import Const, IndexOffset, ParamRef, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import AliasDef, ParameterDef, SetDef, VariableDef
from src.kkt.stationarity import _replace_indices_in_expr


def _make_polygon_ir() -> ModelIR:
    """Minimal ModelIR mimicking polygon: Set i / i1*i25 /; Alias(i,j);"""
    ir = ModelIR()
    ir.sets["i"] = SetDef(name="i", members=[f"i{k}" for k in range(1, 26)])
    ir.aliases["j"] = AliasDef(name="j", target="i")
    ir.variables["r"] = VariableDef(name="r", domain=("i",))
    ir.variables["theta"] = VariableDef(name="theta", domain=("i",))
    return ir


def _make_tfordy_ir() -> ModelIR:
    """Minimal ModelIR mimicking tfordy: Set t; Alias(t, tp);"""
    ir = ModelIR()
    ir.sets["t"] = SetDef(name="t", members=["1990", "1991", "1992"])
    ir.aliases["tp"] = AliasDef(name="tp", target="t")
    ir.params["avl"] = ParameterDef(name="avl", domain=("t", "tp"))
    return ir


def _build_element_to_set(ir: ModelIR, domain, instances):
    """Build element_to_set mapping the same way stationarity does."""
    from src.kkt.stationarity import _build_element_to_set_mapping

    return _build_element_to_set_mapping(ir, domain, instances)


@pytest.mark.unit
class TestReplaceIndicesIndexOffset:
    """Test _replace_indices_in_expr with IndexOffset bases."""

    def test_concrete_element_base_remapped_to_domain(self):
        """IndexOffset("i1", 1) in r(i1+1) should become IndexOffset("i", 1)."""
        ir = _make_polygon_ir()
        domain = ("i",)
        instances = [(0, ("i1",)), (1, ("i2",))]
        e2s = _build_element_to_set(ir, domain, instances)

        expr = VarRef("r", (IndexOffset("i1", Const(1.0), False),))
        result = _replace_indices_in_expr(expr, domain, e2s, ir, equation_domain=domain)

        assert isinstance(result, VarRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "i", f"Expected base 'i', got '{idx.base}'"
        assert idx.offset == Const(1.0)

    def test_symbolic_base_preserved(self):
        """IndexOffset("tp", 1) in avl(tp+1, tp) should NOT be remapped to t."""
        ir = _make_tfordy_ir()
        domain = ("t",)
        instances = [(0, ("1990",)), (1, ("1991",))]
        e2s = _build_element_to_set(ir, domain, instances)

        expr = ParamRef("avl", (IndexOffset("tp", Const(1.0), False), "tp"))
        result = _replace_indices_in_expr(expr, domain, e2s, ir, equation_domain=domain)

        assert isinstance(result, ParamRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "tp", f"Expected base 'tp' (preserved), got '{idx.base}'"

    def test_paramref_concrete_element_base_remapped_to_declared_domain(self):
        """IndexOffset("1990", 1) in avl(1990+1, tp) should become IndexOffset("t", 1)."""
        ir = _make_tfordy_ir()
        domain = ("t",)
        instances = [(0, ("1990",)), (1, ("1991",))]
        e2s = _build_element_to_set(ir, domain, instances)

        expr = ParamRef("avl", (IndexOffset("1990", Const(1.0), False), "tp"))
        result = _replace_indices_in_expr(expr, domain, e2s, ir, equation_domain=domain)

        assert isinstance(result, ParamRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "t", f"Expected base 't', got '{idx.base}'"
        assert idx.offset == Const(1.0)

    def test_set_name_base_preserved(self):
        """IndexOffset("i", 1) should remain IndexOffset("i", 1)."""
        ir = _make_polygon_ir()
        domain = ("i",)
        instances = [(0, ("i1",)), (1, ("i2",))]
        e2s = _build_element_to_set(ir, domain, instances)

        expr = VarRef("r", (IndexOffset("i", Const(1.0), False),))
        result = _replace_indices_in_expr(expr, domain, e2s, ir, equation_domain=domain)

        assert isinstance(result, VarRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base == "i", f"Expected base 'i' (preserved), got '{idx.base}'"

    def test_paramref_wildcard_domain_uses_element_mapping(self):
        """IndexOffset at wildcard position should use element_to_set, not '*'.

        This test covers a ParamRef with domain=("*", "c") where the
        IndexOffset appears at pos 0, the wildcard-declared dimension.
        In that case, replacement must fall back to element_to_set
        mapping and must not produce IndexOffset("*",1).
        """
        ir = ModelIR()
        ir.sets["c"] = SetDef(name="c", members=["c1", "c2", "c3"])
        ir.params["data"] = ParameterDef(name="data", domain=("*", "c"))
        domain = ("c",)
        instances = [(0, ("c1",)), (1, ("c2",))]
        e2s = _build_element_to_set(ir, domain, instances)

        # IndexOffset at pos 0 where declared domain is "*"
        expr = ParamRef("data", (IndexOffset("c1", Const(1.0), False), "c2"))
        result = _replace_indices_in_expr(expr, domain, e2s, ir, equation_domain=domain)

        assert isinstance(result, ParamRef)
        idx = result.indices[0]
        assert isinstance(idx, IndexOffset)
        assert idx.base != "*", "Wildcard '*' must not appear as IndexOffset base"
        assert idx.base == "c", f"Expected base 'c' (from element_to_set), got '{idx.base}'"
