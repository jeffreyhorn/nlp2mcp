"""Unit tests for equation definition emission.

Tests verify correct emission of GAMS equation definitions from KKT system equations.
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.equations import emit_equation_def, emit_equation_definitions
from src.ir.ast import Binary, Const, VarRef
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import ComplementarityPair, KKTSystem


def _create_minimal_kkt(model_ir: ModelIR) -> KKTSystem:
    """Create a minimal KKTSystem for testing."""
    gradient = GradientVector(num_cols=0, index_mapping={})
    J_eq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    J_ineq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    return KKTSystem(model_ir=model_ir, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)


@pytest.mark.unit
class TestEmitEquationDef:
    """Test emission of single equation definitions."""

    def test_scalar_equation_eq(self):
        """Test scalar equation with =E= relation."""
        eq_def = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(10)),
        )
        result = emit_equation_def("balance", eq_def)
        assert result == "balance.. x =E= 10;"

    def test_indexed_equation(self):
        """Test indexed equation.

        Single lowercase letters are domain variables and not quoted.
        """
        eq_def = EquationDef(
            name="balance",
            domain=("i",),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i",)), Const(10)),
        )
        result = emit_equation_def("balance", eq_def)
        assert result == "balance(i).. x(i) =E= 10;"

    def test_multi_indexed_equation(self):
        """Test multi-indexed equation.

        Single lowercase letters are domain variables and not quoted.
        """
        eq_def = EquationDef(
            name="flow",
            domain=("i", "j"),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ("i", "j")), VarRef("y", ("j", "i"))),
        )
        result = emit_equation_def("flow", eq_def)
        assert result == "flow(i,j).. x(i,j) =E= y(j,i);"

    def test_equation_le_relation(self):
        """Test equation with =L= (less than or equal) relation."""
        eq_def = EquationDef(
            name="capacity",
            domain=(),
            relation=Rel.LE,
            lhs_rhs=(VarRef("x", ()), Const(100)),
        )
        result = emit_equation_def("capacity", eq_def)
        assert result == "capacity.. x =L= 100;"

    def test_equation_ge_relation(self):
        """Test equation with =G= (greater than or equal) relation."""
        eq_def = EquationDef(
            name="demand",
            domain=(),
            relation=Rel.GE,
            lhs_rhs=(VarRef("x", ()), Const(5)),
        )
        result = emit_equation_def("demand", eq_def)
        assert result == "demand.. x =G= 5;"

    def test_equation_with_binary_expression(self):
        """Test equation with binary expression on LHS."""
        lhs = Binary("+", VarRef("x", ()), VarRef("y", ()))
        eq_def = EquationDef(
            name="sum_constraint", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, Const(10))
        )
        result = emit_equation_def("sum_constraint", eq_def)
        assert result == "sum_constraint.. x + y =E= 10;"

    def test_equation_with_complex_expression(self):
        """Test equation with complex expression."""
        lhs = Binary("^", VarRef("x", ()), Const(2))
        rhs = Binary("*", Const(2), VarRef("y", ()))
        eq_def = EquationDef(name="nonlinear", domain=(), relation=Rel.EQ, lhs_rhs=(lhs, rhs))
        result = emit_equation_def("nonlinear", eq_def)
        assert result == "nonlinear.. x ** 2 =E= 2 * y;"


@pytest.mark.unit
class TestEmitEquationDefinitions:
    """Test emission of all equation definitions from KKT system."""

    def test_empty_kkt_system(self):
        """Test with empty KKT system."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_equation_definitions(kkt)
        assert result == ""

    def test_stationarity_equations_only(self):
        """Test with only stationarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        # Add stationarity equation
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("*", Const(2), VarRef("x", ())), Const(0)),
        )

        result = emit_equation_definitions(kkt)
        assert "* Stationarity equations" in result
        assert "stat_x.. 2 * x =E= 0;" in result

    def test_multiple_stationarity_equations(self):
        """Test with multiple stationarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(0)),
        )
        kkt.stationarity["stat_y"] = EquationDef(
            name="stat_y",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("y", ()), Const(0)),
        )

        result = emit_equation_definitions(kkt)
        assert "stat_x.. x =E= 0;" in result
        assert "stat_y.. y =E= 0;" in result

    def test_inequality_complementarity(self):
        """Test with inequality complementarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        comp_eq = EquationDef(
            name="comp_g1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("slack_g1", ()), Const(0)),
        )
        kkt.complementarity_ineq["g1"] = ComplementarityPair(
            equation=comp_eq, variable="lambda_g1", variable_indices=()
        )

        result = emit_equation_definitions(kkt)
        assert "* Inequality complementarity equations" in result
        assert "comp_g1.. slack_g1 =E= 0;" in result

    def test_bound_complementarity(self):
        """Test with bound complementarity equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)

        # Lower bound complementarity
        comp_lo = EquationDef(
            name="comp_lo_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("-", VarRef("x", ()), Const(0)), Const(0)),
        )
        kkt.complementarity_bounds_lo[("x", ())] = ComplementarityPair(
            equation=comp_lo, variable="piL_x", variable_indices=()
        )

        # Upper bound complementarity
        comp_up = EquationDef(
            name="comp_up_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Binary("-", Const(10), VarRef("x", ())), Const(0)),
        )
        kkt.complementarity_bounds_up[("x", ())] = ComplementarityPair(
            equation=comp_up, variable="piU_x", variable_indices=()
        )

        result = emit_equation_definitions(kkt)
        assert "* Lower bound complementarity equations" in result
        assert "comp_lo_x.. x - 0 =E= 0;" in result
        assert "* Upper bound complementarity equations" in result
        assert "comp_up_x.. 10 - x =E= 0;" in result

    def test_equality_equations(self):
        """Test with original equality equations."""
        model_ir = ModelIR()
        model_ir.equations["balance"] = EquationDef(
            name="balance",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(10)),
        )
        model_ir.equalities = ["balance"]

        kkt = _create_minimal_kkt(model_ir)
        result = emit_equation_definitions(kkt)

        assert "* Original equality equations" in result
        assert "balance.. x =E= 10;" in result

    def test_all_equation_types(self):
        """Test with all types of equations."""
        model_ir = ModelIR()
        model_ir.equations["objdef"] = EquationDef(
            name="objdef",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("obj", ()), VarRef("x", ())),
        )
        model_ir.equalities = ["objdef"]

        kkt = _create_minimal_kkt(model_ir)

        # Add stationarity
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Const(1), Const(0)),
        )

        # Add inequality complementarity
        comp_ineq = EquationDef(
            name="comp_g1",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("slack", ()), Const(0)),
        )
        kkt.complementarity_ineq["g1"] = ComplementarityPair(
            equation=comp_ineq, variable="lambda_g1", variable_indices=()
        )

        # Add bound complementarity
        comp_lo = EquationDef(
            name="comp_lo_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(VarRef("x", ()), Const(0)),
        )
        kkt.complementarity_bounds_lo[("x", ())] = ComplementarityPair(
            equation=comp_lo, variable="piL_x", variable_indices=()
        )

        result = emit_equation_definitions(kkt)

        # Verify all sections present
        assert "* Stationarity equations" in result
        assert "* Inequality complementarity equations" in result
        assert "* Lower bound complementarity equations" in result
        assert "* Original equality equations" in result

        # Verify equations present
        assert "stat_x.." in result
        assert "comp_g1.." in result
        assert "comp_lo_x.." in result
        assert "objdef.." in result
