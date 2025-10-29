"""
Tests for Objective Gradient Computation (Day 7)

Test Coverage:
-------------
1. Finding objective expression (explicit expr)
2. Finding objective expression (objvar-defined-by-equation)
3. Error handling when objective not found
4. Computing gradient for min objectives
5. Computing gradient for max objectives (negated)
6. Scalar variable gradients
7. Indexed variable gradients
8. Sum aggregation in objectives
"""

from src.ad.gradient import (
    compute_gradient_for_expression,
    compute_objective_gradient,
    find_objective_expression,
)
from src.ir.ast import Binary, Call, Const, ParamRef, Sum, SymbolRef, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ObjSense, Rel, SetDef, VariableDef

# ============================================================================
# Test Finding Objective Expression
# ============================================================================


class TestFindObjectiveExpression:
    """Test finding objective expression from ModelIR."""

    def test_explicit_objective_expression(self):
        """Test objective with explicit expression."""
        model_ir = ModelIR()
        # min x^2
        obj_expr = Call("power", (VarRef("x"), Const(2.0)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        result = find_objective_expression(model_ir)

        assert result is obj_expr

    def test_objvar_defined_by_equation_lhs(self):
        """Test objective variable defined on LHS of equation."""
        model_ir = ModelIR()
        # obj =e= x^2
        obj_expr = Call("power", (VarRef("x"), Const(2.0)))
        model_ir.add_equation(EquationDef("obj_def", (), Rel.EQ, (SymbolRef("obj"), obj_expr)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)

        result = find_objective_expression(model_ir)

        assert result is obj_expr

    def test_objvar_defined_by_equation_rhs(self):
        """Test objective variable defined on RHS of equation."""
        model_ir = ModelIR()
        # x^2 =e= obj
        obj_expr = Call("power", (VarRef("x"), Const(2.0)))
        model_ir.add_equation(EquationDef("obj_def", (), Rel.EQ, (obj_expr, SymbolRef("obj"))))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)

        result = find_objective_expression(model_ir)

        assert result is obj_expr

    def test_no_objective_raises_error(self):
        """Test error when ModelIR has no objective."""
        model_ir = ModelIR()

        try:
            find_objective_expression(model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "no objective" in str(e).lower()

    def test_objvar_not_defined_raises_error(self):
        """Test error when objvar is not defined by any equation."""
        model_ir = ModelIR()
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)
        # No equation defining 'obj'

        try:
            find_objective_expression(model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not defined" in str(e).lower()
            assert "obj" in str(e)

    def test_ignores_indexed_equations(self):
        """Test that indexed equations are skipped when finding objvar."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        # Indexed equation: obj(i) =e= x(i)^2
        model_ir.add_equation(
            EquationDef(
                "indexed_obj",
                ("i",),
                Rel.EQ,
                (SymbolRef("obj"), Call("power", (VarRef("x", ("i",)), Const(2.0)))),
            )
        )
        # Scalar objective (should not find indexed equation)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)

        try:
            find_objective_expression(model_ir)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not defined" in str(e).lower()


# ============================================================================
# Test Gradient Computation - Minimization
# ============================================================================


class TestGradientMinimization:
    """Test gradient computation for minimization objectives."""

    def test_scalar_quadratic_objective(self):
        """Test gradient of min x^2."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        # min x^2
        obj_expr = Call("power", (VarRef("x"), Const(2.0)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(x^2)/∂x = 2*x
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        assert isinstance(deriv, Binary)
        assert deriv.op == "*"

    def test_two_variable_objective(self):
        """Test gradient of min x^2 + y^2."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))
        # min x^2 + y^2
        x_sq = Call("power", (VarRef("x"), Const(2.0)))
        y_sq = Call("power", (VarRef("y"), Const(2.0)))
        obj_expr = Binary("+", x_sq, y_sq)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(x^2 + y^2)/∂x = 2*x
        deriv_x = gradient.get_derivative_by_name("x")
        assert deriv_x is not None

        # ∂(x^2 + y^2)/∂y = 2*y
        deriv_y = gradient.get_derivative_by_name("y")
        assert deriv_y is not None

    def test_constant_objective(self):
        """Test gradient of constant objective is zero."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        # min 5
        obj_expr = Const(5.0)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(5)/∂x = 0
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        assert isinstance(deriv, Const)
        assert deriv.value == 0.0

    def test_linear_objective(self):
        """Test gradient of min x + y."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))
        # min x + y
        obj_expr = Binary("+", VarRef("x"), VarRef("y"))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(x + y)/∂x = 1 + 0 (from sum rule)
        deriv_x = gradient.get_derivative_by_name("x")
        assert deriv_x is not None
        # Result is Binary("+", Const(1.0), Const(0.0)) from sum rule
        assert isinstance(deriv_x, Binary)
        assert deriv_x.op == "+"

        # ∂(x + y)/∂y = 0 + 1 (from sum rule)
        deriv_y = gradient.get_derivative_by_name("y")
        assert deriv_y is not None
        assert isinstance(deriv_y, Binary)
        assert deriv_y.op == "+"


# ============================================================================
# Test Gradient Computation - Maximization
# ============================================================================


class TestGradientMaximization:
    """Test gradient computation for maximization objectives (negated)."""

    def test_max_linear_objective(self):
        """Test gradient of max x (should be -1)."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        # max x = min -x
        obj_expr = VarRef("x")
        model_ir.objective = ObjectiveIR(ObjSense.MAX, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # max x → gradient is -(∂x/∂x) = -1
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        from src.ir.ast import Unary

        assert isinstance(deriv, Unary)
        assert deriv.op == "-"

    def test_max_two_variables(self):
        """Test gradient of max x + y (should be -1, -1)."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))
        # max x + y
        obj_expr = Binary("+", VarRef("x"), VarRef("y"))
        model_ir.objective = ObjectiveIR(ObjSense.MAX, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # max (x+y) → gradient is -(1, 1) = (-1, -1)
        deriv_x = gradient.get_derivative_by_name("x")
        deriv_y = gradient.get_derivative_by_name("y")
        assert deriv_x is not None
        assert deriv_y is not None


# ============================================================================
# Test Indexed Variables
# ============================================================================


class TestGradientIndexedVariables:
    """Test gradient with indexed variables."""

    def test_indexed_variable_objective(self):
        """Test gradient of objective with indexed variables."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_var(VariableDef("x", ("i",)))
        # min sum(i, x(i)^2)
        x_sq = Call("power", (VarRef("x", ("i",)), Const(2.0)))
        obj_expr = Sum(("i",), x_sq)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(sum(i, x(i)^2))/∂x(i1) should exist
        deriv_i1 = gradient.get_derivative_by_name("x", ("i1",))
        assert deriv_i1 is not None

        # ∂(sum(i, x(i)^2))/∂x(i2) should exist
        deriv_i2 = gradient.get_derivative_by_name("x", ("i2",))
        assert deriv_i2 is not None

        # With sum collapse: ∂(sum(i, x(i)^2))/∂x(i1) = 2*x(i1)
        # The sum collapses because only the i=i1 term contributes
        # Result is no longer a Sum (which would be wrong), but a Binary expression
        assert isinstance(deriv_i1, Binary), "Derivative should collapse to Binary, not Sum"
        assert isinstance(deriv_i2, Binary), "Derivative should collapse to Binary, not Sum"

        # The derivative should reference the correct concrete index (i1, i2)
        # Structure may be (2*x(i1)^1)*1 due to power and chain rules, which is fine
        # Key test: verify it contains VarRef with correct index
        deriv_i1_str = repr(deriv_i1)
        assert "VarRef(x(i1))" in deriv_i1_str, (
            f"Derivative should contain x(i1), got: {deriv_i1_str}"
        )

        deriv_i2_str = repr(deriv_i2)
        assert "VarRef(x(i2))" in deriv_i2_str, (
            f"Derivative should contain x(i2), got: {deriv_i2_str}"
        )

    def test_mixed_scalar_and_indexed(self):
        """Test gradient with mix of scalar and indexed variables."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_var(VariableDef("y", ()))  # Scalar
        model_ir.add_var(VariableDef("x", ("i",)))  # Indexed
        # min y + sum(i, x(i))
        sum_expr = Sum(("i",), VarRef("x", ("i",)))
        obj_expr = Binary("+", VarRef("y"), sum_expr)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(y + sum(i, x(i)))/∂y = 1
        deriv_y = gradient.get_derivative_by_name("y")
        assert deriv_y is not None

        # ∂(y + sum(i, x(i)))/∂x(i1) = 1 (only the x(i1) term contributes)
        # Note: Current implementation treats all x instances the same symbolically,
        # producing sum(i, 1) for all x instances. Full index-aware differentiation
        # will be implemented in a future update.
        deriv_x_i1 = gradient.get_derivative_by_name("x", ("i1",))
        assert deriv_x_i1 is not None

    def test_sum_collapse_simple_sum(self):
        """Test that sum(i, x(i)) collapses correctly when differentiated."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2", "i3"]))
        model_ir.add_var(VariableDef("x", ("i",)))
        # min sum(i, x(i))
        obj_expr = Sum(("i",), VarRef("x", ("i",)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        # ∂(sum(i, x(i)))/∂x(i1) = 1 (not Sum(i, 1))
        deriv_i1 = gradient.get_derivative_by_name("x", ("i1",))
        assert deriv_i1 is not None
        assert isinstance(deriv_i1, Const), f"Expected Const(1.0), got {deriv_i1}"
        assert deriv_i1.value == 1.0

    def test_sum_collapse_with_parameter(self):
        """Test sum collapse with parameters: sum(i, c(i)*x(i))."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_var(VariableDef("x", ("i",)))
        # min sum(i, c(i)*x(i)) where c is a parameter
        # ∂(sum(i, c(i)*x(i)))/∂x(i1) = c(i1) (before simplification)
        cx = Binary("*", ParamRef("c", ("i",)), VarRef("x", ("i",)))
        obj_expr = Sum(("i",), cx)
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        deriv_i1 = gradient.get_derivative_by_name("x", ("i1",))
        assert deriv_i1 is not None
        # Should not be a Sum (collapse occurred)
        assert not isinstance(deriv_i1, Sum), f"Should collapse, not remain as Sum: {deriv_i1}"
        # Should contain ParamRef("c", ("i1",)) with correct index
        deriv_str = repr(deriv_i1)
        assert "ParamRef(c(i1))" in deriv_str, f"Should contain c(i1), got: {deriv_str}"

    def test_sum_no_collapse_different_indices(self):
        """Test that sum does NOT collapse when indices don't match pattern."""
        model_ir = ModelIR()
        model_ir.add_set(SetDef("i", ["i1", "i2"]))
        model_ir.add_set(SetDef("k", ["k1", "k2"]))
        model_ir.add_var(VariableDef("x", ("k",)))
        # min sum(i, x(k1)) - sum over i, but x is indexed by k (different dimension)
        # This should NOT collapse
        obj_expr = Sum(("i",), VarRef("x", ("k1",)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=obj_expr)

        gradient = compute_objective_gradient(model_ir)

        deriv_k1 = gradient.get_derivative_by_name("x", ("k1",))
        assert deriv_k1 is not None
        # Should remain as Sum because indices don't match pattern
        assert isinstance(deriv_k1, Sum), f"Expected Sum (no collapse), got {deriv_k1}"


# ============================================================================
# Test compute_gradient_for_expression
# ============================================================================


class TestGradientForExpression:
    """Test computing gradient for arbitrary expressions."""

    def test_simple_expression(self):
        """Test gradient of x^2."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))

        expr = Call("power", (VarRef("x"), Const(2.0)))
        gradient = compute_gradient_for_expression(expr, model_ir)

        # ∂(x^2)/∂x = 2*x
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        assert isinstance(deriv, Binary)

    def test_expression_with_negation(self):
        """Test gradient with negation flag."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))

        expr = VarRef("x")
        gradient = compute_gradient_for_expression(expr, model_ir, negate=True)

        # -∂x/∂x = -1
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        from src.ir.ast import Unary

        assert isinstance(deriv, Unary)
        assert deriv.op == "-"


# ============================================================================
# Test Objective from Defining Equation
# ============================================================================


class TestObjectiveFromDefiningEquation:
    """Test complete gradient computation when objective is defined by equation."""

    def test_objvar_equation_gradient(self):
        """Test gradient when objective is defined by equation."""
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        # obj =e= x^2
        obj_expr = Call("power", (VarRef("x"), Const(2.0)))
        model_ir.add_equation(EquationDef("obj_def", (), Rel.EQ, (SymbolRef("obj"), obj_expr)))
        model_ir.objective = ObjectiveIR(ObjSense.MIN, "obj", expr=None)

        gradient = compute_objective_gradient(model_ir)

        # ∂(x^2)/∂x = 2*x
        deriv = gradient.get_derivative_by_name("x")
        assert deriv is not None
        assert isinstance(deriv, Binary)
