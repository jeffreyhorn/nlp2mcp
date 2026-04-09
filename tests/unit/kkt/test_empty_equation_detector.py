"""Tests for empty equation instance detection.

Issue #1133: Detect equation instances where no variable appears due to
sparse coefficient data or set membership conditions.
"""

import pytest

from src.ir.ast import (
    Binary,
    Const,
    DollarConditional,
    ParamRef,
    SetMembershipTest,
    Sum,
    SymbolRef,
    VarRef,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, ParameterDef, Rel, SetDef
from src.kkt.empty_equation_detector import detect_empty_equation_instances


def _make_fawley_like_model() -> ModelIR:
    """Build a minimal model mimicking fawley's mbal(c) equation."""
    ir = ModelIR()
    ir.sets["c"] = SetDef(name="c", members=["steel", "fuel", "vacuum-res"])
    ir.sets["p"] = SetDef(name="p", members=["proc1", "proc2"])
    ir.sets["cr"] = SetDef(name="cr", domain=("c",), members=["steel"])

    # Parameter ap(c,p) — sparse: only has entries for steel and fuel
    ir.params["ap"] = ParameterDef(
        name="ap",
        domain=("c", "p"),
        values={("steel", "proc1"): 1.0, ("fuel", "proc2"): 2.0},
    )

    # Variable declarations
    from src.ir.symbols import VariableDef

    ir.variables["u"] = VariableDef(name="u", domain=("c",))
    ir.variables["z"] = VariableDef(name="z", domain=("p",))

    # Equation: mbal(c).. u(c)$cr(c) + sum(p, ap(c,p)*z(p)) =E= 0
    eq_body_lhs = Binary(
        "+",
        # u(c)$cr(c)
        DollarConditional(
            VarRef("u", ("c",)),
            SetMembershipTest("cr", (SymbolRef("c"),)),
        ),
        # sum(p, ap(c,p)*z(p))
        Sum(
            ("p",),
            Binary("*", ParamRef("ap", ("c", "p")), VarRef("z", ("p",))),
        ),
    )
    ir.equations["mbal"] = EquationDef(
        name="mbal",
        domain=("c",),
        relation=Rel.EQ,
        lhs_rhs=(eq_body_lhs, Const(0.0)),
    )
    ir.equalities = ["mbal"]

    return ir


@pytest.mark.unit
class TestEmptyEquationDetector:
    def test_detects_empty_instance_from_sparse_data(self):
        """vacuum-res should be empty: not in cr, ap has no entries."""
        ir = _make_fawley_like_model()
        result = detect_empty_equation_instances(ir)

        assert "mbal" in result
        empty_instances = result["mbal"]
        assert ("vacuum-res",) in empty_instances

    def test_non_empty_instances_not_detected(self):
        """steel and fuel should NOT be empty."""
        ir = _make_fawley_like_model()
        result = detect_empty_equation_instances(ir)

        empty_instances = result.get("mbal", set())
        assert ("steel",) not in empty_instances
        assert ("fuel",) not in empty_instances

    def test_unconditional_variable_prevents_empty(self):
        """Adding an unconditional variable reference prevents empty detection."""
        ir = _make_fawley_like_model()

        # Add unconditional variable to mbal
        from src.ir.symbols import VariableDef

        ir.variables["invent"] = VariableDef(name="invent", domain=("c",))
        old_lhs = ir.equations["mbal"].lhs_rhs[0]
        new_lhs = Binary("+", old_lhs, VarRef("invent", ("c",)))
        ir.equations["mbal"] = EquationDef(
            name="mbal",
            domain=("c",),
            relation=Rel.EQ,
            lhs_rhs=(new_lhs, Const(0.0)),
        )

        result = detect_empty_equation_instances(ir)
        # No empty instances because invent(c) is unconditional
        assert "mbal" not in result

    def test_relevant_equations_filter(self):
        """Only analyzes equations in relevant_equations when provided."""
        ir = _make_fawley_like_model()

        # With filter excluding mbal
        result = detect_empty_equation_instances(ir, relevant_equations={"other_eq"})
        assert "mbal" not in result

        # With filter including mbal
        result = detect_empty_equation_instances(ir, relevant_equations={"mbal"})
        assert "mbal" in result
