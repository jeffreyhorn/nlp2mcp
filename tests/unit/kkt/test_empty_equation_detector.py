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

    def test_include_inequalities_scans_inequalities(self):
        """include_inequalities=True should scan ModelIR.inequalities."""
        ir = _make_fawley_like_model()
        # Move mbal to inequalities
        ir.equalities = []
        ir.inequalities = ["mbal"]
        ir.equations["mbal"] = EquationDef(
            name="mbal",
            domain=("c",),
            relation=Rel.GE,
            lhs_rhs=ir.equations["mbal"].lhs_rhs,
        )

        # Without include_inequalities — should find nothing
        result = detect_empty_equation_instances(ir)
        assert "mbal" not in result

        # With include_inequalities — should find vacuum-res
        result = detect_empty_equation_instances(ir, include_inequalities=True)
        assert "mbal" in result
        assert ("vacuum-res",) in result["mbal"]

    def test_computed_param_expressions_detect_empty(self):
        """Coefficient params with expressions (no .values) should be analyzed."""
        ir = ModelIR()
        ir.sets["ca"] = SetDef(name="ca", members=["wheat", "seed"])
        ir.sets["cf"] = SetDef(name="cf", domain=("ca",), members=["wheat"])

        from src.ir.symbols import VariableDef

        ir.variables["x"] = VariableDef(name="x", domain=("ca",))

        # Computed coefficient: coeff(ca, cf) assigned only for cf members
        ir.params["coeff"] = ParameterDef(
            name="coeff",
            domain=("ca", "cf"),
            values={},
            expressions=[(("cf", "ca"), Binary("*", Const(1.0), Const(1.0)))],
        )

        # Equation: eq(ca).. sum(cf, coeff(ca,cf)*x(cf)) =E= 0
        eq_lhs = Sum(
            ("cf",),
            Binary("*", ParamRef("coeff", ("ca", "cf")), VarRef("x", ("cf",))),
        )
        ir.equations["eq"] = EquationDef(
            name="eq",
            domain=("ca",),
            relation=Rel.GE,
            lhs_rhs=(eq_lhs, Const(0.0)),
        )
        ir.inequalities = ["eq"]

        result = detect_empty_equation_instances(ir, include_inequalities=True)
        assert "eq" in result
        # "seed" is not in cf, so the assignment doesn't cover it
        assert ("seed",) in result["eq"]
        assert ("wheat",) not in result["eq"]
