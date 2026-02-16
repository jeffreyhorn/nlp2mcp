"""Unit tests for src/emit/templates.py

Tests GAMS template emission functions, especially:
- emit_variables() with Finding #4 (variable kind preservation)
- emit_kkt_sets() for KKT-specific sets
- emit_equations() placeholder
"""

import pytest

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.emit.templates import (
    _build_dynamic_subset_map,
    _remap_domain,
    emit_equations,
    emit_kkt_sets,
    emit_model,
    emit_solve,
    emit_variables,
)
from src.ir.ast import Const
from src.ir.model_ir import ModelIR
from src.ir.symbols import SetAssignment, SetDef, VariableDef, VarKind
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


@pytest.mark.unit
class TestBuildDynamicSubsetMap:
    """Test _build_dynamic_subset_map() for Issue #739."""

    def test_empty_model(self):
        """No sets or assignments yields empty map."""
        model_ir = ModelIR()
        assert _build_dynamic_subset_map(model_ir) == {}

    def test_static_set_not_included(self):
        """Sets with static members are not considered dynamic."""
        model_ir = ModelIR()
        model_ir.sets["im"] = SetDef(name="im", members=["a", "b"], domain=("i",))
        # No set_assignments — even though it has a domain, it's static
        assert _build_dynamic_subset_map(model_ir) == {}

    def test_dynamic_subset_detected(self):
        """Dynamic subset with assignment and no static members is detected."""
        model_ir = ModelIR()
        model_ir.sets["i"] = SetDef(name="i", members=["a", "b", "c"])
        model_ir.sets["im"] = SetDef(name="im", members=[], domain=("i",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="im", indices=("i",), expr=Const(1.0), location=None)
        )
        result = _build_dynamic_subset_map(model_ir)
        assert result == {"im": "i"}

    def test_multiple_dynamic_subsets(self):
        """Multiple dynamic subsets mapping to same or different parents."""
        model_ir = ModelIR()
        model_ir.sets["i"] = SetDef(name="i", members=["a", "b"])
        model_ir.sets["im"] = SetDef(name="im", members=[], domain=("i",))
        model_ir.sets["ie"] = SetDef(name="ie", members=[], domain=("i",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="im", indices=("i",), expr=Const(1.0), location=None)
        )
        model_ir.set_assignments.append(
            SetAssignment(set_name="ie", indices=("i",), expr=Const(1.0), location=None)
        )
        result = _build_dynamic_subset_map(model_ir)
        assert result == {"im": "i", "ie": "i"}

    def test_set_with_members_excluded(self):
        """Dynamic set assignment exists but set has static members — not remapped."""
        model_ir = ModelIR()
        model_ir.sets["k"] = SetDef(name="k", members=["k1"], domain=("j",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="k", indices=("j",), expr=Const(1.0), location=None)
        )
        # Has static members, so excluded
        assert _build_dynamic_subset_map(model_ir) == {}

    def test_multi_dimensional_domain_excluded(self):
        """Sets with multi-dimensional domain are excluded."""
        model_ir = ModelIR()
        model_ir.sets["ij"] = SetDef(name="ij", members=[], domain=("i", "j"))
        model_ir.set_assignments.append(
            SetAssignment(set_name="ij", indices=("i", "j"), expr=Const(1.0), location=None)
        )
        assert _build_dynamic_subset_map(model_ir) == {}

    def test_case_insensitive_matching(self):
        """Set name matching is case-insensitive."""
        model_ir = ModelIR()
        model_ir.sets["IM"] = SetDef(name="IM", members=[], domain=("i",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="im", indices=("i",), expr=Const(1.0), location=None)
        )
        result = _build_dynamic_subset_map(model_ir)
        assert result == {"im": "i"}


@pytest.mark.unit
class TestRemapDomain:
    """Test _remap_domain() for Issue #739."""

    def test_empty_domain(self):
        """Empty domain returns empty tuple."""
        assert _remap_domain((), {"im": "i"}) == ()

    def test_no_remapping_needed(self):
        """Domain with no dynamic subsets is unchanged."""
        assert _remap_domain(("i", "j"), {"im": "i"}) == ("i", "j")

    def test_single_remapping(self):
        """Single dynamic subset is remapped."""
        assert _remap_domain(("im",), {"im": "i"}) == ("i",)

    def test_multiple_remappings(self):
        """Multiple dynamic subsets in same domain are remapped."""
        assert _remap_domain(("im", "ie"), {"im": "i", "ie": "i"}) == ("i", "i")

    def test_mixed_remapping(self):
        """Mix of dynamic and static indices."""
        assert _remap_domain(("im", "j"), {"im": "i"}) == ("i", "j")

    def test_case_insensitive(self):
        """Remapping is case-insensitive."""
        assert _remap_domain(("IM",), {"im": "i"}) == ("i",)

    def test_empty_map(self):
        """Empty dynamic map leaves domain unchanged."""
        assert _remap_domain(("im", "j"), {}) == ("im", "j")


@pytest.mark.unit
class TestEmitVariablesDynamicSubsets:
    """Test emit_variables() with dynamic subset domain remapping (Issue #739)."""

    def test_dynamic_subset_domain_remapped_in_declaration(self):
        """Variable with dynamic subset domain emits parent set in declaration."""
        model_ir = ModelIR()
        model_ir.sets["i"] = SetDef(name="i", members=["a", "b"])
        model_ir.sets["im"] = SetDef(name="im", members=[], domain=("i",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="im", indices=("i",), expr=Const(1.0), location=None)
        )
        model_ir.variables["x"] = VariableDef(name="x", domain=("im",), kind=VarKind.CONTINUOUS)
        kkt = _create_minimal_kkt(model_ir)
        result = emit_variables(kkt)

        # Declaration should use parent set "i", not dynamic subset "im"
        assert "x(i)" in result
        assert "x(im)" not in result


@pytest.mark.unit
class TestEmitEquationsDynamicSubsets:
    """Test emit_equations() with dynamic subset domain remapping (Issue #739)."""

    def test_dynamic_subset_domain_remapped_in_equation_declaration(self):
        """Equation with dynamic subset domain emits parent set in declaration."""
        from src.ir.symbols import EquationDef, Rel

        model_ir = ModelIR()
        model_ir.sets["i"] = SetDef(name="i", members=["a", "b"])
        model_ir.sets["im"] = SetDef(name="im", members=[], domain=("i",))
        model_ir.set_assignments.append(
            SetAssignment(set_name="im", indices=("i",), expr=Const(1.0), location=None)
        )
        # Add an equality equation with dynamic subset domain
        model_ir.equations["pmdef"] = EquationDef(
            name="pmdef",
            domain=("im",),
            relation=Rel.EQ,
            lhs_rhs=(Const(1.0), Const(0.0)),
        )
        model_ir.equalities.append("pmdef")

        kkt = _create_minimal_kkt(model_ir)
        result = emit_equations(kkt)

        # Declaration should use parent set "i", not dynamic subset "im"
        assert "pmdef(i)" in result
        assert "pmdef(im)" not in result
