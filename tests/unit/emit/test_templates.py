"""Unit tests for src/emit/templates.py

Tests GAMS template emission functions, especially:
- emit_variables() with Finding #4 (variable kind preservation)
- emit_kkt_sets() for KKT-specific sets
- emit_equations() placeholder
"""

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.templates import (
    emit_equations,
    emit_kkt_sets,
    emit_model,
    emit_solve,
    emit_variables,
)
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetDef, VariableDef, VarKind
from src.kkt.kkt_system import KKTSystem, MultiplierDef


def _create_minimal_kkt(model_ir: ModelIR) -> KKTSystem:
    """Create a minimal KKTSystem with empty gradient and jacobians for testing."""
    # Create empty gradient and jacobians (size doesn't matter for emit tests)
    gradient = GradientVector(num_cols=0, index_mapping={})
    J_eq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    J_ineq = JacobianStructure(num_rows=0, num_cols=0, index_mapping={})
    return KKTSystem(model_ir=model_ir, gradient=gradient, J_eq=J_eq, J_ineq=J_ineq)


class TestEmitVariables:
    """Test emit_variables() function - Finding #4: variable kind preservation."""

    def test_empty_variables(self):
        """Test with no variables."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)
        assert result == ""

    def test_single_continuous_variable(self):
        """Test single CONTINUOUS variable."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "Variables" in result
        assert "x" in result

    def test_single_positive_variable(self):
        """Test single POSITIVE variable."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.POSITIVE)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "Positive Variables" in result
        assert "x" in result

    def test_single_binary_variable(self):
        """Test single BINARY variable."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.BINARY)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "Binary Variables" in result
        assert "x" in result

    def test_single_integer_variable(self):
        """Test single INTEGER variable."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.INTEGER)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "Integer Variables" in result
        assert "x" in result

    def test_mixed_variable_kinds(self):
        """Test multiple variables with different kinds."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.CONTINUOUS)
        model_ir.variables["y"] = VariableDef(name="y", domain=(), kind=VarKind.POSITIVE)
        model_ir.variables["z"] = VariableDef(name="z", domain=(), kind=VarKind.BINARY)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "Variables" in result
        assert "Positive Variables" in result
        assert "Binary Variables" in result
        assert "x" in result
        assert "y" in result
        assert "z" in result

    def test_indexed_variables(self):
        """Test indexed variables with domains."""
        model_ir = ModelIR()
        model_ir.sets["i"] = SetDef(name="i", members=["i1", "i2"])
        model_ir.sets["j"] = SetDef(name="j", members=["j1", "j2"])
        model_ir.variables["x"] = VariableDef(name="x", domain=("i",), kind=VarKind.CONTINUOUS)
        model_ir.variables["y"] = VariableDef(name="y", domain=("i", "j"), kind=VarKind.POSITIVE)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        assert "x(i)" in result
        assert "y(i,j)" in result

    def test_multipliers_eq_continuous(self):
        """Test equality multipliers added to CONTINUOUS group."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        kkt.multipliers_eq = {
            "nu_eq1": MultiplierDef(
                name="nu_eq1", domain=(), kind="eq", associated_constraint="eq1"
            )
        }
        result = emit_variables(kkt)

        assert "Variables" in result
        assert "nu_eq1" in result

    def test_multipliers_ineq_positive(self):
        """Test inequality multipliers added to POSITIVE group."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        kkt.multipliers_ineq = {
            "lambda_ineq1": MultiplierDef(
                name="lambda_ineq1", domain=(), kind="ineq", associated_constraint="ineq1"
            )
        }
        result = emit_variables(kkt)

        assert "Positive Variables" in result
        assert "lambda_ineq1" in result

    def test_multipliers_bounds_positive(self):
        """Test bound multipliers added to POSITIVE group."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        kkt.multipliers_bounds_lo = {
            ("x", ()): MultiplierDef(
                name="pi_L_x", domain=(), kind="bound_lo", associated_constraint="x"
            )
        }
        kkt.multipliers_bounds_up = {
            ("y", ()): MultiplierDef(
                name="pi_U_y", domain=(), kind="bound_up", associated_constraint="y"
            )
        }
        result = emit_variables(kkt)

        assert "Positive Variables" in result
        assert "pi_L_x" in result
        assert "pi_U_y" in result

    def test_all_multiplier_types(self):
        """Test all multiplier types together."""
        model_ir = ModelIR()
        model_ir.variables["x"] = VariableDef(name="x", domain=(), kind=VarKind.POSITIVE)
        kkt = _create_minimal_kkt(model_ir)
        kkt.multipliers_eq = {
            "nu_eq1": MultiplierDef(
                name="nu_eq1", domain=(), kind="eq", associated_constraint="eq1"
            )
        }
        kkt.multipliers_ineq = {
            "lambda_ineq1": MultiplierDef(
                name="lambda_ineq1", domain=(), kind="ineq", associated_constraint="ineq1"
            )
        }
        kkt.multipliers_bounds_lo = {
            ("x", ()): MultiplierDef(
                name="pi_L_x", domain=(), kind="bound_lo", associated_constraint="x"
            )
        }
        result = emit_variables(kkt)

        # CONTINUOUS group should have equality multipliers
        assert "nu_eq1" in result
        # POSITIVE group should have primal variable, inequality and bound multipliers
        assert "x" in result
        assert "lambda_ineq1" in result
        assert "pi_L_x" in result


class TestEmitKKTSets:
    """Test emit_kkt_sets() function."""

    def test_empty_sets(self):
        """Test with no KKT sets."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_kkt_sets(kkt)
        assert result == ""

    def test_placeholder_returns_empty(self):
        """Test that emit_kkt_sets is currently a placeholder returning empty."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_kkt_sets(kkt)
        assert result == ""


class TestEmitEquations:
    """Test emit_equations() function for equation declarations."""

    def test_empty_equations(self):
        """Test with no equations."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_equations(kkt)
        # Should still emit "Equations\n;" even if empty
        assert "Equations" in result
        assert ";" in result

    def test_with_stationarity_equations(self):
        """Test with stationarity equations."""
        from src.ir.symbols import EquationDef, Rel

        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        # Add some stationarity equations
        kkt.stationarity = {
            "stat_x": EquationDef(name="stat_x", domain=(), relation=Rel.EQ, lhs_rhs=(None, None)),
            "stat_y": EquationDef(name="stat_y", domain=(), relation=Rel.EQ, lhs_rhs=(None, None)),
        }
        result = emit_equations(kkt)

        assert "Equations" in result
        assert "stat_x" in result
        assert "stat_y" in result


class TestEmitModel:
    """Test emit_model() placeholder function."""

    def test_placeholder_returns_empty(self):
        """Test that placeholder returns empty string."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_model(kkt)
        assert result == ""


class TestEmitSolve:
    """Test emit_solve() placeholder function."""

    def test_placeholder_returns_empty(self):
        """Test that placeholder returns empty string."""
        model_ir = ModelIR()
        kkt = _create_minimal_kkt(model_ir)
        result = emit_solve(kkt)
        assert result == ""
