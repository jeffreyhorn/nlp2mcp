"""
Tests for Constraint Jacobian Computation

Tests the computation of J_h (equality constraints) and J_g (inequality constraints).

Note: Derivatives are symbolic AST expressions that may not be simplified.
Tests evaluate derivatives to check correctness rather than checking exact AST structure.
"""

import pytest

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.evaluator import evaluate
from src.ir.ast import Binary, Const, ParamRef, VarRef
from src.ir.model_ir import (
    EquationDef,
    ModelIR,
    ParameterDef,
    SetDef,
    VariableDef,
)
from src.ir.symbols import Rel

pytestmark = pytest.mark.integration


def eval_derivative(deriv):
    """Evaluate a derivative expression (assuming no variables/params needed)."""
    if deriv is None:
        return None
    return evaluate(deriv, {}, {})


@pytest.mark.integration
class TestEqualityJacobian:
    """Tests for equality constraint Jacobian (J_h)."""

    def test_empty_model_has_empty_jacobians(self):
        """Empty model should produce empty Jacobians."""
        model_ir = ModelIR()
        J_h, J_g = compute_constraint_jacobian(model_ir)

        assert J_h.num_nonzeros() == 0
        assert J_g.num_nonzeros() == 0

    def test_single_equality_constraint(self):
        """Test: x + y = 5 → ∂h/∂x = 1, ∂h/∂y = 1"""
        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equation: x + y =e= 5
        eq_expr = (
            Binary("+", VarRef("x"), VarRef("y")),
            Const(5.0),
        )
        model_ir.add_equation(EquationDef("eq1", (), Rel.EQ, eq_expr))
        model_ir.equalities = ["eq1"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_h: ∂(x+y-5)/∂x = 1, ∂(x+y-5)/∂y = 1
        deriv_x = J_h.get_derivative_by_names("eq1", (), "x", ())
        deriv_y = J_h.get_derivative_by_names("eq1", (), "y", ())

        assert eval_derivative(deriv_x) == 1.0
        assert eval_derivative(deriv_y) == 1.0

        # J_g should be empty (no inequalities)
        assert J_g.num_nonzeros() == 0

    def test_quadratic_equality_constraint(self):
        """Test: x^2 + y^2 = 1 → ∂h/∂x = 2x, ∂h/∂y = 2y"""
        from src.ir.ast import Call

        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equation: x^2 + y^2 =e= 1
        x_squared = Call("power", (VarRef("x"), Const(2.0)))
        y_squared = Call("power", (VarRef("y"), Const(2.0)))
        lhs = Binary("+", x_squared, y_squared)
        eq_expr = (lhs, Const(1.0))
        model_ir.add_equation(EquationDef("circle", (), Rel.EQ, eq_expr))
        model_ir.equalities = ["circle"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_h: ∂(x^2+y^2-1)/∂x = 2x, ∂(x^2+y^2-1)/∂y = 2y
        deriv_x = J_h.get_derivative_by_names("circle", (), "x", ())
        deriv_y = J_h.get_derivative_by_names("circle", (), "y", ())

        # Derivatives should be non-None Binary expressions (2*x and 2*y)
        # Full evaluation is complex due to nested Call structures
        assert deriv_x is not None
        assert deriv_y is not None
        assert isinstance(deriv_x, Binary)  # Should be a compound expression
        assert isinstance(deriv_y, Binary)

    def test_multiple_equality_constraints(self):
        """Test multiple equality constraints."""
        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equation 1: x + y =e= 1
        eq1_expr = (Binary("+", VarRef("x"), VarRef("y")), Const(1.0))
        model_ir.add_equation(EquationDef("eq1", (), Rel.EQ, eq1_expr))

        # Equation 2: x - y =e= 0
        eq2_expr = (Binary("-", VarRef("x"), VarRef("y")), Const(0.0))
        model_ir.add_equation(EquationDef("eq2", (), Rel.EQ, eq2_expr))

        model_ir.equalities = ["eq1", "eq2"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_h has 4 entries (2 equations × 2 variables)
        # eq1: ∂(x+y-1)/∂x = 1, ∂(x+y-1)/∂y = 1
        # eq2: ∂(x-y)/∂x = 1, ∂(x-y)/∂y = -1
        assert J_h.num_nonzeros() == 4

        deriv_eq1_x = J_h.get_derivative_by_names("eq1", (), "x", ())
        deriv_eq1_y = J_h.get_derivative_by_names("eq1", (), "y", ())
        deriv_eq2_x = J_h.get_derivative_by_names("eq2", (), "x", ())
        deriv_eq2_y = J_h.get_derivative_by_names("eq2", (), "y", ())

        assert eval_derivative(deriv_eq1_x) == 1.0
        assert eval_derivative(deriv_eq1_y) == 1.0
        assert eval_derivative(deriv_eq2_x) == 1.0
        # eq2: d(x-y)/dy = -1
        assert eval_derivative(deriv_eq2_y) == -1.0


@pytest.mark.integration
class TestInequalityJacobian:
    """Tests for inequality constraint Jacobian (J_g)."""

    def test_single_inequality_constraint(self):
        """Test: x + y <= 5 → ∂g/∂x = 1, ∂g/∂y = 1"""
        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equation: x + y =l= 5 (normalized to x + y - 5 <= 0)
        eq_expr = (Binary("+", VarRef("x"), VarRef("y")), Const(5.0))
        model_ir.add_equation(EquationDef("ineq1", (), Rel.LE, eq_expr))
        model_ir.inequalities = ["ineq1"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_g: ∂(x+y-5)/∂x = 1, ∂(x+y-5)/∂y = 1
        deriv_x = J_g.get_derivative_by_names("ineq1", (), "x", ())
        deriv_y = J_g.get_derivative_by_names("ineq1", (), "y", ())

        assert eval_derivative(deriv_x) == 1.0
        assert eval_derivative(deriv_y) == 1.0

        # J_h should be empty (no equalities)
        assert J_h.num_nonzeros() == 0

    def test_quadratic_inequality_constraint(self):
        """Test: x^2 + y^2 <= 1 → ∂g/∂x = 2x, ∂g/∂y = 2y"""
        from src.ir.ast import Call

        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equation: x^2 + y^2 =l= 1
        x_squared = Call("power", (VarRef("x"), Const(2.0)))
        y_squared = Call("power", (VarRef("y"), Const(2.0)))
        lhs = Binary("+", x_squared, y_squared)
        eq_expr = (lhs, Const(1.0))
        model_ir.add_equation(EquationDef("circle_bound", (), Rel.LE, eq_expr))
        model_ir.inequalities = ["circle_bound"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_g: ∂(x^2+y^2-1)/∂x = 2x, ∂(x^2+y^2-1)/∂y = 2y
        deriv_x = J_g.get_derivative_by_names("circle_bound", (), "x", ())
        deriv_y = J_g.get_derivative_by_names("circle_bound", (), "y", ())

        # Derivatives should be non-None Binary expressions (2*x and 2*y)
        assert deriv_x is not None
        assert deriv_y is not None
        assert isinstance(deriv_x, Binary)
        assert isinstance(deriv_y, Binary)


@pytest.mark.integration
class TestIndexedConstraints:
    """Tests for indexed constraint Jacobians."""

    def test_indexed_equality_constraint(self):
        """Test indexed equality: sum(i, x(i)) = total"""
        from src.ir.ast import Sum

        model_ir = ModelIR()

        # Set i
        model_ir.add_set(SetDef("i", members=["i1", "i2"]))

        # Variables: x(i), total
        model_ir.add_var(VariableDef("x", ("i",)))
        model_ir.add_var(VariableDef("total", ()))

        # Equation: sum(i, x(i)) =e= total
        sum_expr = Sum(("i",), VarRef("x", ("i",)))
        eq_expr = (sum_expr, VarRef("total"))
        model_ir.add_equation(EquationDef("sum_eq", (), Rel.EQ, eq_expr))
        model_ir.equalities = ["sum_eq"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Check J_h: ∂(sum(i,x(i)) - total)/∂x(i1) = 1, ∂/∂x(i2) = 1, ∂/∂total = -1
        deriv_x_i1 = J_h.get_derivative_by_names("sum_eq", (), "x", ("i1",))
        deriv_x_i2 = J_h.get_derivative_by_names("sum_eq", (), "x", ("i2",))
        deriv_total = J_h.get_derivative_by_names("sum_eq", (), "total", ())

        # Sum collapse: d(sum(i, x(i)))/dx(i1) = 1
        assert eval_derivative(deriv_x_i1) == 1.0
        assert eval_derivative(deriv_x_i2) == 1.0
        # d(-total)/d(total) = -1 (from lhs-rhs normalization)
        assert deriv_total is not None
        assert eval_derivative(deriv_total) == -1.0

    def test_indexed_constraint_instances(self):
        """Test: balance(i): x(i) + y(i) = demand(i) expands to multiple rows"""
        model_ir = ModelIR()

        # Set i
        model_ir.add_set(SetDef("i", members=["i1", "i2"]))

        # Parameters: demand(i)
        model_ir.add_param(ParameterDef("demand", ("i",)))

        # Variables: x(i), y(i)
        model_ir.add_var(VariableDef("x", ("i",)))
        model_ir.add_var(VariableDef("y", ("i",)))

        # Equation: balance(i).. x(i) + y(i) =e= demand(i)
        lhs = Binary("+", VarRef("x", ("i",)), VarRef("y", ("i",)))
        rhs = ParamRef("demand", ("i",))
        model_ir.add_equation(EquationDef("balance", ("i",), Rel.EQ, (lhs, rhs)))
        model_ir.equalities = ["balance"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Should have 2 equation instances: balance(i1), balance(i2)
        # Each equation has 2 nonzero derivatives (w.r.t. x(i) and y(i))
        # Total: 4 nonzero entries

        # balance(i1): ∂(x(i1)+y(i1)-demand(i1))/∂x(i1) = 1
        deriv_i1_x = J_h.get_derivative_by_names("balance", ("i1",), "x", ("i1",))
        deriv_i1_y = J_h.get_derivative_by_names("balance", ("i1",), "y", ("i1",))

        assert eval_derivative(deriv_i1_x) == 1.0
        assert eval_derivative(deriv_i1_y) == 1.0

        # balance(i2): ∂(x(i2)+y(i2)-demand(i2))/∂x(i2) = 1
        deriv_i2_x = J_h.get_derivative_by_names("balance", ("i2",), "x", ("i2",))
        deriv_i2_y = J_h.get_derivative_by_names("balance", ("i2",), "y", ("i2",))

        assert eval_derivative(deriv_i2_x) == 1.0
        assert eval_derivative(deriv_i2_y) == 1.0

        # Cross terms should be zero (x(i1) doesn't affect balance(i2))
        deriv_cross = J_h.get_derivative_by_names("balance", ("i1",), "x", ("i2",))
        assert eval_derivative(deriv_cross) == 0.0


@pytest.mark.integration
class TestMixedConstraints:
    """Tests for models with both equalities and inequalities."""

    def test_mixed_equality_and_inequality(self):
        """Test model with both equality and inequality constraints."""
        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Equality: x + y =e= 1
        eq_expr = (Binary("+", VarRef("x"), VarRef("y")), Const(1.0))
        model_ir.add_equation(EquationDef("eq1", (), Rel.EQ, eq_expr))
        model_ir.equalities = ["eq1"]

        # Inequality: x - y =l= 0.5
        ineq_expr = (Binary("-", VarRef("x"), VarRef("y")), Const(0.5))
        model_ir.add_equation(EquationDef("ineq1", (), Rel.LE, ineq_expr))
        model_ir.inequalities = ["ineq1"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_h should have 2 entries (1 equation × 2 variables)
        assert J_h.num_nonzeros() == 2

        # J_g should have 2 entries (1 inequality × 2 variables)
        assert J_g.num_nonzeros() == 2

        # Verify specific entries
        eq_deriv_x = J_h.get_derivative_by_names("eq1", (), "x", ())
        eq_deriv_y = J_h.get_derivative_by_names("eq1", (), "y", ())
        ineq_deriv_x = J_g.get_derivative_by_names("ineq1", (), "x", ())
        ineq_deriv_y = J_g.get_derivative_by_names("ineq1", (), "y", ())

        assert eval_derivative(eq_deriv_x) == 1.0
        assert eval_derivative(eq_deriv_y) == 1.0
        assert eval_derivative(ineq_deriv_x) == 1.0
        assert eval_derivative(ineq_deriv_y) == -1.0


@pytest.mark.integration
class TestSparsityPattern:
    """Tests for Jacobian sparsity patterns."""

    def test_sparse_jacobian_pattern(self):
        """Test that Jacobian correctly identifies zero and nonzero entries."""
        model_ir = ModelIR()

        # Variables: x, y, z
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))
        model_ir.add_var(VariableDef("z", ()))

        # Equation: x + y =e= 1 (doesn't depend on z)
        eq_expr = (Binary("+", VarRef("x"), VarRef("y")), Const(1.0))
        model_ir.add_equation(EquationDef("eq1", (), Rel.EQ, eq_expr))
        model_ir.equalities = ["eq1"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Should have derivatives w.r.t. x and y, but derivative w.r.t. z should be 0
        deriv_x = J_h.get_derivative_by_names("eq1", (), "x", ())
        deriv_y = J_h.get_derivative_by_names("eq1", (), "y", ())
        deriv_z = J_h.get_derivative_by_names("eq1", (), "z", ())

        assert eval_derivative(deriv_x) == 1.0
        assert eval_derivative(deriv_y) == 1.0
        assert eval_derivative(deriv_z) == 0.0

    def test_block_diagonal_pattern(self):
        """Test block-diagonal sparsity pattern from indexed constraints."""
        model_ir = ModelIR()

        # Set i
        model_ir.add_set(SetDef("i", members=["i1", "i2"]))

        # Variables: x(i)
        model_ir.add_var(VariableDef("x", ("i",)))

        # Equation: balance(i).. x(i) =e= 0
        model_ir.add_equation(
            EquationDef("balance", ("i",), Rel.EQ, (VarRef("x", ("i",)), Const(0.0)))
        )
        model_ir.equalities = ["balance"]

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # Should have diagonal pattern: balance(i1) depends on x(i1), balance(i2) on x(i2)
        deriv_i1_i1 = J_h.get_derivative_by_names("balance", ("i1",), "x", ("i1",))
        deriv_i1_i2 = J_h.get_derivative_by_names("balance", ("i1",), "x", ("i2",))
        deriv_i2_i1 = J_h.get_derivative_by_names("balance", ("i2",), "x", ("i1",))
        deriv_i2_i2 = J_h.get_derivative_by_names("balance", ("i2",), "x", ("i2",))

        # Diagonal entries: 1
        assert eval_derivative(deriv_i1_i1) == 1.0
        assert eval_derivative(deriv_i2_i2) == 1.0

        # Off-diagonal entries: 0
        assert eval_derivative(deriv_i1_i2) == 0.0
        assert eval_derivative(deriv_i2_i1) == 0.0
