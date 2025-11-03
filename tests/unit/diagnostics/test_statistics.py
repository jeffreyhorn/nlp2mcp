"""Tests for model statistics computation."""

from src.ad.gradient import GradientVector
from src.ad.jacobian import JacobianStructure
from src.diagnostics.statistics import ModelStatistics, compute_model_statistics
from src.ir.ast import Const
from src.ir.model_ir import ModelIR
from src.ir.symbols import EquationDef, Rel
from src.kkt.kkt_system import ComplementarityPair, KKTSystem, MultiplierDef


class TestModelStatistics:
    """Test ModelStatistics dataclass and formatting."""

    def test_format_report_basic(self):
        """Test formatted report generation."""
        stats = ModelStatistics(
            num_equations=10,
            num_variables=8,
            num_nonzeros=25,
            num_stationarity=5,
            num_complementarity_ineq=3,
            num_complementarity_bounds_lo=1,
            num_complementarity_bounds_up=1,
            num_primal_vars=5,
            num_multipliers_eq=1,
            num_multipliers_ineq=1,
            num_multipliers_bounds_lo=1,
            num_multipliers_bounds_up=0,
            jacobian_density=0.31,
        )

        report = stats.format_report()

        assert "MODEL STATISTICS" in report
        assert "Total equations:" in report and "10" in report
        assert "Total variables:" in report and "8" in report
        assert "Nonzero entries:" in report and "25" in report
        assert "Jacobian density:" in report and "31.00%" in report
        assert "Stationarity equations:" in report and "5" in report

    def test_zero_values(self):
        """Test with zero counts."""
        stats = ModelStatistics(
            num_equations=0,
            num_variables=0,
            num_nonzeros=0,
            num_stationarity=0,
            num_complementarity_ineq=0,
            num_complementarity_bounds_lo=0,
            num_complementarity_bounds_up=0,
            num_primal_vars=0,
            num_multipliers_eq=0,
            num_multipliers_ineq=0,
            num_multipliers_bounds_lo=0,
            num_multipliers_bounds_up=0,
            jacobian_density=0.0,
        )

        report = stats.format_report()
        assert "Total equations:" in report and "0" in report


class TestComputeModelStatistics:
    """Test compute_model_statistics function."""

    def test_simple_kkt_system(self):
        """Test with simple KKT system."""
        # Create minimal ModelIR
        model = ModelIR()

        # Create gradient with 2 variables
        gradient = GradientVector(num_cols=2)
        gradient.set_derivative(0, Const(1.0))
        gradient.set_derivative(1, Const(2.0))

        # Create empty Jacobians
        J_eq = JacobianStructure(num_rows=1, num_cols=2)
        J_eq.set_derivative(0, 0, Const(1.0))

        J_ineq = JacobianStructure(num_rows=1, num_cols=2)
        J_ineq.set_derivative(0, 1, Const(1.0))

        # Create KKT system
        kkt = KKTSystem(
            model_ir=model,
            gradient=gradient,
            J_eq=J_eq,
            J_ineq=J_ineq,
        )

        # Add stationarity equations (one per variable)
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Const(0.0), Const(0.0)),
        )
        kkt.stationarity["stat_y"] = EquationDef(
            name="stat_y",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Const(0.0), Const(0.0)),
        )

        # Add multipliers
        kkt.multipliers_eq["nu_g1"] = MultiplierDef(
            name="nu_g1", domain=(), kind="eq", associated_constraint="g1"
        )
        kkt.multipliers_ineq["lam_h1"] = MultiplierDef(
            name="lam_h1", domain=(), kind="ineq", associated_constraint="h1"
        )

        # Add complementarity pairs
        kkt.complementarity_ineq["h1"] = ComplementarityPair(
            equation=EquationDef(
                name="h1",
                domain=(),
                relation=Rel.LE,
                lhs_rhs=(Const(0.0), Const(0.0)),
            ),
            variable="lam_h1",
            variable_indices=(),
        )

        # Compute statistics
        stats = compute_model_statistics(kkt)

        # Verify counts
        assert stats.num_primal_vars == 2
        assert stats.num_stationarity == 2
        assert stats.num_multipliers_eq == 1
        assert stats.num_multipliers_ineq == 1
        assert stats.num_complementarity_ineq == 1
        assert stats.num_complementarity_bounds_lo == 0
        assert stats.num_complementarity_bounds_up == 0

        # Total equations = stationarity + complementarity
        assert stats.num_equations == 3  # 2 stat + 1 ineq comp

        # Total variables = primal + multipliers
        assert stats.num_variables == 4  # 2 primal + 1 eq + 1 ineq

        assert stats.num_nonzeros > 0
        assert 0.0 <= stats.jacobian_density <= 1.0

    def test_with_bounds(self):
        """Test with bound multipliers."""
        model = ModelIR()
        gradient = GradientVector(num_cols=2)
        J_eq = JacobianStructure(num_rows=0, num_cols=2)
        J_ineq = JacobianStructure(num_rows=0, num_cols=2)

        kkt = KKTSystem(
            model_ir=model,
            gradient=gradient,
            J_eq=J_eq,
            J_ineq=J_ineq,
        )

        # Add stationarity
        kkt.stationarity["stat_x"] = EquationDef(
            name="stat_x",
            domain=(),
            relation=Rel.EQ,
            lhs_rhs=(Const(0.0), Const(0.0)),
        )

        # Add bound multipliers
        kkt.multipliers_bounds_lo[("x",)] = MultiplierDef(
            name="pi_x_lo", domain=(), kind="bound_lo"
        )
        kkt.multipliers_bounds_up[("x",)] = MultiplierDef(
            name="pi_x_up", domain=(), kind="bound_up"
        )

        # Add bound complementarity
        kkt.complementarity_bounds_lo[("x",)] = ComplementarityPair(
            equation=EquationDef(
                name="bound_x_lo",
                domain=(),
                relation=Rel.GE,
                lhs_rhs=(Const(0.0), Const(0.0)),
            ),
            variable="pi_x_lo",
        )
        kkt.complementarity_bounds_up[("x",)] = ComplementarityPair(
            equation=EquationDef(
                name="bound_x_up",
                domain=(),
                relation=Rel.LE,
                lhs_rhs=(Const(0.0), Const(0.0)),
            ),
            variable="pi_x_up",
        )

        stats = compute_model_statistics(kkt)

        assert stats.num_complementarity_bounds_lo == 1
        assert stats.num_complementarity_bounds_up == 1
        assert stats.num_multipliers_bounds_lo == 1
        assert stats.num_multipliers_bounds_up == 1

    def test_empty_kkt_system(self):
        """Test with empty KKT system."""
        model = ModelIR()
        gradient = GradientVector(num_cols=0)
        J_eq = JacobianStructure(num_rows=0, num_cols=0)
        J_ineq = JacobianStructure(num_rows=0, num_cols=0)

        kkt = KKTSystem(
            model_ir=model,
            gradient=gradient,
            J_eq=J_eq,
            J_ineq=J_ineq,
        )

        stats = compute_model_statistics(kkt)

        assert stats.num_equations == 0
        assert stats.num_variables == 0
        assert stats.num_nonzeros == 0
        assert stats.jacobian_density == 0.0
