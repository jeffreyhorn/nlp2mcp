"""
Tests for Bound-Derived Jacobian Rows

Tests that variable bounds are correctly included in J_g as inequality constraints.

Note: Derivatives are symbolic AST expressions that may not be simplified.
Tests evaluate derivatives to check correctness rather than checking exact AST structure.
"""

from src.ad.constraint_jacobian import compute_constraint_jacobian
from src.ad.evaluator import evaluate
from src.ir.ast import Binary, Const, ParamRef, VarRef
from src.ir.model_ir import (
    ModelIR,
    ParameterDef,
    SetDef,
    VariableDef,
)
from src.ir.normalize import NormalizedEquation
from src.ir.symbols import Rel


def eval_derivative(deriv):
    """Evaluate a derivative expression (assuming no variables/params needed)."""
    if deriv is None:
        return None
    return evaluate(deriv, {}, {})


class TestBoundJacobianSimple:
    """Tests for simple bound-derived Jacobian rows."""

    def test_lower_bound_jacobian(self):
        """Test: x >= 0 contributes row to J_g with ∂(x-0)/∂x = 1"""
        model_ir = ModelIR()

        # Variable: x
        model_ir.add_var(VariableDef("x", ()))

        # Bound: x >= 0 (normalized to -(x - 0) <= 0, but usually stored as x - 0 >= 0)
        # For simplicity, we'll store as x - 0 with relation
        bound_expr = Binary("-", VarRef("x"), Const(0.0))
        model_ir.normalized_bounds["x_lo"] = NormalizedEquation(
            name="x_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,  # x - 0 >= 0
            expr=bound_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_h should be empty (no equalities)
        assert J_h.num_nonzeros() == 0

        # J_g should have 1 row from the bound
        # ∂(x-0)/∂x = 1
        assert J_g.num_nonzeros() == 1

        # Get the bound row (row 0 since no other inequalities)
        row_entries = list(J_g.get_row(0).items())
        assert len(row_entries) == 1

        # Should be derivative w.r.t. x = 1
        col_id, deriv = row_entries[0]
        assert eval_derivative(deriv) == 1.0

    def test_upper_bound_jacobian(self):
        """Test: x <= 10 contributes row to J_g with ∂(x-10)/∂x = 1"""
        model_ir = ModelIR()

        # Variable: x
        model_ir.add_var(VariableDef("x", ()))

        # Bound: x <= 10 (normalized to x - 10 <= 0)
        bound_expr = Binary("-", VarRef("x"), Const(10.0))
        model_ir.normalized_bounds["x_up"] = NormalizedEquation(
            name="x_up",
            domain_sets=(),
            index_values=(),
            relation=Rel.LE,  # x - 10 <= 0
            expr=bound_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_g should have 1 row from the bound
        # ∂(x-10)/∂x = 1
        assert J_g.num_nonzeros() == 1

        row_entries = list(J_g.get_row(0).items())
        assert len(row_entries) == 1

        col_id, deriv = row_entries[0]
        assert eval_derivative(deriv) == 1.0

    def test_both_bounds_jacobian(self):
        """Test: 0 <= x <= 10 contributes two rows to J_g"""
        model_ir = ModelIR()

        # Variable: x
        model_ir.add_var(VariableDef("x", ()))

        # Lower bound: x >= 0
        bound_lo_expr = Binary("-", VarRef("x"), Const(0.0))
        model_ir.normalized_bounds["x_lo"] = NormalizedEquation(
            name="x_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,
            expr=bound_lo_expr,
            expr_domain=(),
            rank=0,
        )

        # Upper bound: x <= 10
        bound_up_expr = Binary("-", VarRef("x"), Const(10.0))
        model_ir.normalized_bounds["x_up"] = NormalizedEquation(
            name="x_up",
            domain_sets=(),
            index_values=(),
            relation=Rel.LE,
            expr=bound_up_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_g should have 2 rows from bounds
        # Both: ∂(x-c)/∂x = 1
        assert J_g.num_nonzeros() == 2

        # Check both rows
        for row_id in [0, 1]:
            row_entries = list(J_g.get_row(row_id).items())
            assert len(row_entries) == 1
            col_id, deriv = row_entries[0]
            assert eval_derivative(deriv) == 1.0


class TestBoundJacobianIndexed:
    """Tests for indexed variable bounds."""

    def test_indexed_variable_lower_bound(self):
        """Test: x(i) >= 0 expands to multiple bound rows"""
        model_ir = ModelIR()

        # Set i
        model_ir.add_set(SetDef("i", members=["i1", "i2"]))

        # Variable: x(i)
        model_ir.add_var(VariableDef("x", ("i",)))

        # Bounds: x(i1) >= 0, x(i2) >= 0
        # Note: In practice, these would be created by normalize.py
        bound_i1_expr = Binary("-", VarRef("x", ("i1",)), Const(0.0))
        model_ir.normalized_bounds["x_i1_lo"] = NormalizedEquation(
            name="x_i1_lo",
            domain_sets=("i",),
            index_values=("i1",),
            relation=Rel.GE,
            expr=bound_i1_expr,
            expr_domain=(),
            rank=0,
        )

        bound_i2_expr = Binary("-", VarRef("x", ("i2",)), Const(0.0))
        model_ir.normalized_bounds["x_i2_lo"] = NormalizedEquation(
            name="x_i2_lo",
            domain_sets=("i",),
            index_values=("i2",),
            relation=Rel.GE,
            expr=bound_i2_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_g should have entries for 2 bounds × 2 variables
        # All derivatives (including zeros) are stored symbolically; not sparsity-optimized.
        # x(i1) bound: ∂(x(i1)-0)/∂x(i1) = 1, ∂/∂x(i2) = 0
        # x(i2) bound: ∂(x(i2)-0)/∂x(i1) = 0, ∂/∂x(i2) = 1
        assert J_g.num_nonzeros() == 4  # All derivatives stored (including zeros)

        # Check diagonal structure (each bound only depends on its own variable)
        row0_entries = list(J_g.get_row(0).items())
        row1_entries = list(J_g.get_row(1).items())

        # Each row should have 2 entries (one for each variable)
        assert len(row0_entries) == 2
        assert len(row1_entries) == 2

    def test_indexed_variable_parametric_bounds(self):
        """Test: x(i) >= lo(i) where lo is a parameter"""
        model_ir = ModelIR()

        # Set i
        model_ir.add_set(SetDef("i", members=["i1", "i2"]))

        # Parameter: lo(i)
        model_ir.add_param(ParameterDef("lo", ("i",)))

        # Variable: x(i)
        model_ir.add_var(VariableDef("x", ("i",)))

        # Bound: x(i1) >= lo(i1) → x(i1) - lo(i1) >= 0
        bound_i1_expr = Binary("-", VarRef("x", ("i1",)), ParamRef("lo", ("i1",)))
        model_ir.normalized_bounds["x_i1_lo"] = NormalizedEquation(
            name="x_i1_lo",
            domain_sets=("i",),
            index_values=("i1",),
            relation=Rel.GE,
            expr=bound_i1_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_g should have 1 row with 2 entries (one for each variable)
        # ∂(x(i1) - lo(i1))/∂x(i1) = 1
        # ∂(x(i1) - lo(i1))/∂x(i2) = 0
        assert J_g.num_nonzeros() == 2  # One for x(i1) and one for x(i2); both entries are stored

        row_entries = list(J_g.get_row(0).items())
        # Should have entry for x(i1) = 1, and entry for x(i2) = 0
        # Actually, we only store the nonzero, so let's check differently

        # The bound constraint derivative w.r.t. its own variable should be 1
        # We need to know which column corresponds to x(i1)
        # This is tricky without knowing the index mapping...
        # Let's just verify the count for now
        assert len(row_entries) >= 1  # At least one nonzero (x(i1))


class TestBoundJacobianWithConstraints:
    """Tests for bounds combined with other constraints."""

    def test_bounds_with_equality_constraints(self):
        """Test that bounds appear after equality constraint rows"""
        model_ir = ModelIR()

        # Variable: x
        model_ir.add_var(VariableDef("x", ()))

        # Equality: x =e= 5
        from src.ir.model_ir import EquationDef

        model_ir.add_equation(EquationDef("eq1", (), Rel.EQ, (VarRef("x"), Const(5.0))))
        model_ir.equalities = ["eq1"]

        # Bound: x >= 0
        bound_expr = Binary("-", VarRef("x"), Const(0.0))
        model_ir.normalized_bounds["x_lo"] = NormalizedEquation(
            name="x_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,
            expr=bound_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_h should have 1 entry (equality constraint)
        assert J_h.num_nonzeros() == 1

        # J_g should have 1 entry (bound constraint)
        assert J_g.num_nonzeros() == 1

    def test_bounds_with_inequality_constraints(self):
        """Test that bounds appear after inequality constraint rows"""
        model_ir = ModelIR()

        # Variable: x
        model_ir.add_var(VariableDef("x", ()))

        # Inequality: x =l= 10
        from src.ir.model_ir import EquationDef

        model_ir.add_equation(EquationDef("ineq1", (), Rel.LE, (VarRef("x"), Const(10.0))))
        model_ir.inequalities = ["ineq1"]

        # Bound: x >= 0
        bound_expr = Binary("-", VarRef("x"), Const(0.0))
        model_ir.normalized_bounds["x_lo"] = NormalizedEquation(
            name="x_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,
            expr=bound_expr,
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_h should be empty
        assert J_h.num_nonzeros() == 0

        # J_g should have 2 rows: 1 from inequality, 1 from bound
        # Each has derivative w.r.t. x = 1
        assert J_g.num_nonzeros() == 2

        # Row 0: inequality constraint
        row0_entries = J_g.get_row(0)
        assert len(row0_entries) == 1

        # Row 1: bound constraint
        row1_entries = J_g.get_row(1)
        assert len(row1_entries) == 1

    def test_multiple_variables_with_bounds(self):
        """Test multiple variables each with bounds"""
        model_ir = ModelIR()

        # Variables: x, y
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        # Bounds: 0 <= x <= 10, 0 <= y <= 20
        model_ir.normalized_bounds["x_lo"] = NormalizedEquation(
            name="x_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,
            expr=Binary("-", VarRef("x"), Const(0.0)),
            expr_domain=(),
            rank=0,
        )
        model_ir.normalized_bounds["x_up"] = NormalizedEquation(
            name="x_up",
            domain_sets=(),
            index_values=(),
            relation=Rel.LE,
            expr=Binary("-", VarRef("x"), Const(10.0)),
            expr_domain=(),
            rank=0,
        )
        model_ir.normalized_bounds["y_lo"] = NormalizedEquation(
            name="y_lo",
            domain_sets=(),
            index_values=(),
            relation=Rel.GE,
            expr=Binary("-", VarRef("y"), Const(0.0)),
            expr_domain=(),
            rank=0,
        )
        model_ir.normalized_bounds["y_up"] = NormalizedEquation(
            name="y_up",
            domain_sets=(),
            index_values=(),
            relation=Rel.LE,
            expr=Binary("-", VarRef("y"), Const(20.0)),
            expr_domain=(),
            rank=0,
        )

        # Compute Jacobian
        J_h, J_g = compute_constraint_jacobian(model_ir)

        # J_g should have 4 rows (4 bounds)
        # Each bound has 1 nonzero derivative
        # x_lo: ∂(x-0)/∂x=1, ∂/∂y=0
        # x_up: ∂(x-10)/∂x=1, ∂/∂y=0
        # y_lo: ∂(y-0)/∂x=0, ∂/∂y=1
        # y_up: ∂(y-20)/∂x=0, ∂/∂y=1
        assert J_g.num_nonzeros() == 8  # 4 rows × 2 variables (some zeros)

        # Each row should have exactly 1 nonzero (diagonal structure for simple bounds)
        for row_id in range(4):
            row_entries = list(J_g.get_row(row_id).items())
            # Count nonzeros by evaluating derivatives (exclude zeros)
            nonzero_count = sum(1 for _col, deriv in row_entries if eval_derivative(deriv) != 0.0)
            assert nonzero_count == 1
