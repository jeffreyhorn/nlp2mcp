"""
Integration tests for error recovery and validation.

Sprint 5 Day 4: Task 4.4 - Recovery Tests (≥20 tests)

These tests verify that nlp2mcp catches common modeling errors and provides
actionable error messages with helpful suggestions.
"""

import pytest

from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.model_ir import ModelIR, ObjectiveIR
from src.ir.symbols import EquationDef, ParameterDef, Rel, VariableDef
from src.utils.errors import ModelError, NumericalError
from src.validation.model import (
    validate_equations_reference_variables,
    validate_model_structure,
    validate_no_circular_definitions,
    validate_objective_defined,
)
from src.validation.numerical import (
    check_value_finite,
    validate_bounds,
    validate_expression_value,
    validate_parameter_values,
)

# =============================================================================
# Numerical Error Recovery Tests (10 tests)
# =============================================================================


def test_nan_parameter_detected():
    """Test that NaN in parameter values is caught with helpful message."""
    model = ModelIR()
    model.params["p"] = ParameterDef(name="p", domain=(), values={("1",): float("nan")})

    with pytest.raises(NumericalError) as exc_info:
        validate_parameter_values(model)

    assert "parameter 'p[1]'" in str(exc_info.value)
    assert "NaN" in str(exc_info.value)
    assert "Uninitialized parameters" in str(exc_info.value)


def test_inf_parameter_detected():
    """Test that Inf in parameter values is caught."""
    model = ModelIR()
    model.params["p"] = ParameterDef(name="p", domain=(), values={(): float("inf")})

    with pytest.raises(NumericalError) as exc_info:
        validate_parameter_values(model)

    assert "parameter 'p'" in str(exc_info.value)
    assert "Inf" in str(exc_info.value)


def test_negative_inf_parameter_detected():
    """Test that -Inf in parameter values is caught."""
    model = ModelIR()
    model.params["q"] = ParameterDef(name="q", domain=(), values={(): float("-inf")})

    with pytest.raises(NumericalError) as exc_info:
        validate_parameter_values(model)

    assert "parameter 'q'" in str(exc_info.value)
    assert "-Inf" in str(exc_info.value)


def test_multiple_parameters_first_nan_reported():
    """Test that first NaN parameter is reported when multiple exist."""
    model = ModelIR()
    model.params["p1"] = ParameterDef(name="p1", domain=(), values={(): 1.0})
    model.params["p2"] = ParameterDef(name="p2", domain=(), values={(): float("nan")})
    model.params["p3"] = ParameterDef(name="p3", domain=(), values={(): float("nan")})

    with pytest.raises(NumericalError) as exc_info:
        validate_parameter_values(model)

    # Should report one of the NaN parameters
    assert "NaN" in str(exc_info.value)


def test_expression_value_nan_detected():
    """Test that NaN expression values are caught."""
    with pytest.raises(NumericalError) as exc_info:
        validate_expression_value(float("nan"), "objective")

    assert "objective" in str(exc_info.value)
    assert "NaN" in str(exc_info.value)
    assert "not finite" in str(exc_info.value).lower()


def test_expression_value_inf_detected():
    """Test that Inf expression values are caught."""
    with pytest.raises(NumericalError) as exc_info:
        validate_expression_value(float("inf"), "constraint eq1")

    assert "constraint eq1" in str(exc_info.value)
    assert "Inf" in str(exc_info.value)


def test_check_value_finite_accepts_normal():
    """Test that finite values pass validation."""
    # Should not raise
    check_value_finite(0.0, "test")
    check_value_finite(3.14, "test")
    check_value_finite(-100.0, "test")
    check_value_finite(1e-300, "test")  # Very small but finite
    check_value_finite(1e300, "test")  # Very large but finite


def test_check_value_finite_rejects_nan():
    """Test that check_value_finite rejects NaN."""
    with pytest.raises(NumericalError) as exc_info:
        check_value_finite(float("nan"), "test value")

    assert "test value" in str(exc_info.value)
    assert "not finite" in str(exc_info.value).lower()


def test_validate_bounds_nan_lower():
    """Test that NaN lower bounds are caught."""
    with pytest.raises(NumericalError) as exc_info:
        validate_bounds(float("nan"), 10.0, "x")

    assert "variable 'x'" in str(exc_info.value)
    assert "Lower bound" in str(exc_info.value)
    assert "NaN" in str(exc_info.value)


def test_validate_bounds_inconsistent():
    """Test that inconsistent bounds (lower > upper) are caught."""
    with pytest.raises(NumericalError) as exc_info:
        validate_bounds(10.0, 0.0, "x")

    assert "variable 'x'" in str(exc_info.value)
    assert "Lower bound (10.0) is greater than upper bound (0.0)" in str(exc_info.value)


# =============================================================================
# Model Structure Error Recovery Tests (10 tests)
# =============================================================================


def test_missing_objective_detected():
    """Test that missing objective is caught."""
    model = ModelIR()
    model.objective = None

    with pytest.raises(ModelError) as exc_info:
        validate_objective_defined(model)

    assert "no objective" in str(exc_info.value).lower()
    assert "Add an objective" in str(exc_info.value)


def test_undefined_objective_variable():
    """Test that undefined objective variable is caught."""
    model = ModelIR()
    model.objective = ObjectiveIR(
        objvar=None,
        sense="minimize",
        expr=Const(0.0),
    )

    with pytest.raises(ModelError) as exc_info:
        validate_objective_defined(model)

    assert "Objective variable is not defined" in str(exc_info.value)


def test_equation_with_no_variables():
    """Test that constant equations (no variables) are caught."""
    model = ModelIR()
    # Equation: 5 = 5 (no variables!)
    model.equations["const_eq"] = EquationDef(
        name="const_eq",
        domain=(),
        lhs_rhs=(Const(5.0), Const(5.0)),
        relation=Rel.EQ,
    )

    with pytest.raises(ModelError) as exc_info:
        validate_equations_reference_variables(model)

    assert "const_eq" in str(exc_info.value)
    assert "does not reference any variables" in str(exc_info.value)
    assert "Constant equations" in str(exc_info.value)


def test_circular_dependency_detected():
    """Test that circular variable definitions are caught."""
    model = ModelIR()

    # x = y
    model.equations["eq1"] = EquationDef(
        name="eq1",
        domain=(),
        lhs_rhs=(VarRef("x"), VarRef("y")),
        relation=Rel.EQ,
    )

    # y = x (circular!)
    model.equations["eq2"] = EquationDef(
        name="eq2",
        domain=(),
        lhs_rhs=(VarRef("y"), VarRef("x")),
        relation=Rel.EQ,
    )

    with pytest.raises(ModelError) as exc_info:
        validate_no_circular_definitions(model)

    assert "Circular dependency" in str(exc_info.value)
    assert "eq1" in str(exc_info.value) or "eq2" in str(exc_info.value)


def test_valid_model_passes_structure_validation():
    """Test that a well-formed model passes all structure validations."""
    model = ModelIR()

    # Add objective
    model.objective = ObjectiveIR(
        objvar="z",
        sense="minimize",
        expr=VarRef("x"),
    )

    # Add variables
    model.variables["x"] = VariableDef(name="x", domain=())
    model.variables["z"] = VariableDef(name="z", domain=())

    # Add defining equation: z = x^2
    model.equations["obj_def"] = EquationDef(
        name="obj_def",
        domain=(),
        lhs_rhs=(
            VarRef("z"),
            Call("power", (VarRef("x"), Const(2.0))),
        ),
        relation=Rel.EQ,
    )

    # Should not raise
    validate_model_structure(model)


def test_model_with_constraint_passes():
    """Test model with objective and constraints passes validation."""
    model = ModelIR()

    model.objective = ObjectiveIR(
        objvar="z",
        sense="minimize",
        expr=VarRef("z"),
    )

    model.variables["x"] = VariableDef(name="x", domain=())
    model.variables["z"] = VariableDef(name="z", domain=())

    # z = x^2
    model.equations["obj_def"] = EquationDef(
        name="obj_def",
        domain=(),
        lhs_rhs=(VarRef("z"), Call("power", (VarRef("x"), Const(2.0)))),
        relation=Rel.EQ,
    )

    # x <= 10
    model.equations["con1"] = EquationDef(
        name="con1",
        domain=(),
        lhs_rhs=(VarRef("x"), Const(10.0)),
        relation=Rel.LE,
    )

    # Should not raise
    validate_model_structure(model)


def test_equation_with_one_variable_passes():
    """Test that equations with at least one variable pass validation."""
    model = ModelIR()

    # x + 5 = 10 (has variable x)
    model.equations["eq1"] = EquationDef(
        name="eq1",
        domain=(),
        lhs_rhs=(
            Binary("+", VarRef("x"), Const(5.0)),
            Const(10.0),
        ),
        relation=Rel.EQ,
    )

    # Should not raise
    validate_equations_reference_variables(model)


def test_multiple_equations_all_must_have_variables():
    """Test that all equations must reference variables."""
    model = ModelIR()

    # Valid: x + 5 = 10
    model.equations["eq1"] = EquationDef(
        name="eq1",
        domain=(),
        lhs_rhs=(Binary("+", VarRef("x"), Const(5.0)), Const(10.0)),
        relation=Rel.EQ,
    )

    # Invalid: 2 = 3 (no variables!)
    model.equations["bad_eq"] = EquationDef(
        name="bad_eq",
        domain=(),
        lhs_rhs=(Const(2.0), Const(3.0)),
        relation=Rel.EQ,
    )

    with pytest.raises(ModelError) as exc_info:
        validate_equations_reference_variables(model)

    assert "bad_eq" in str(exc_info.value)


def test_self_defining_equation_not_circular():
    """Test that x = f(x) is not flagged as circular (it's valid)."""
    model = ModelIR()

    # x = x + 1 (self-referential but not circular between variables)
    model.equations["eq1"] = EquationDef(
        name="eq1",
        domain=(),
        lhs_rhs=(
            VarRef("x"),
            Binary("+", VarRef("x"), Const(1.0)),
        ),
        relation=Rel.EQ,
    )

    # Should not raise (this is a fixed-point equation, not a circular dependency)
    validate_no_circular_definitions(model)


def test_chain_dependency_not_circular():
    """Test that x=f(y), y=f(z) is not circular."""
    model = ModelIR()

    # x = y + 1
    model.equations["eq1"] = EquationDef(
        name="eq1",
        domain=(),
        lhs_rhs=(VarRef("x"), Binary("+", VarRef("y"), Const(1.0))),
        relation=Rel.EQ,
    )

    # y = z + 1
    model.equations["eq2"] = EquationDef(
        name="eq2",
        domain=(),
        lhs_rhs=(VarRef("y"), Binary("+", VarRef("z"), Const(1.0))),
        relation=Rel.EQ,
    )

    # Should not raise
    validate_no_circular_definitions(model)


# =============================================================================
# Boundary Condition Tests (5 tests)
# =============================================================================


def test_validate_bounds_valid_finite():
    """Test that valid finite bounds pass validation."""
    # Should not raise
    validate_bounds(0.0, 10.0, "x")
    validate_bounds(-100.0, 100.0, "y")
    validate_bounds(None, 10.0, "z")  # Only upper bound
    validate_bounds(0.0, None, "w")  # Only lower bound
    validate_bounds(None, None, "v")  # Unbounded


def test_validate_bounds_nan_upper():
    """Test that NaN upper bounds are caught."""
    with pytest.raises(NumericalError) as exc_info:
        validate_bounds(0.0, float("nan"), "x")

    assert "variable 'x'" in str(exc_info.value)
    assert "Upper bound" in str(exc_info.value)


def test_validate_bounds_equal_ok():
    """Test that equal bounds (fixed variable) are OK."""
    # Should not raise - this fixes a variable
    validate_bounds(5.0, 5.0, "x")


def test_parameters_with_valid_values_pass():
    """Test that parameters with all finite values pass validation."""
    model = ModelIR()
    model.params["p1"] = ParameterDef(name="p1", domain=(), values={(): 1.0})
    model.params["p2"] = ParameterDef(name="p2", domain=(), values={(): -3.14})
    model.params["p3"] = ParameterDef(name="p3", domain=(), values={("1",): 0.0, ("2",): 100.0})

    # Should not raise
    validate_parameter_values(model)


def test_empty_model_parameters_pass():
    """Test that model with no parameters passes validation."""
    model = ModelIR()

    # Should not raise
    validate_parameter_values(model)


# =============================================================================
# Test Count Verification
# =============================================================================


def test_recovery_test_count():
    """
    Verify that we have at least 20 recovery tests as required.

    This is a meta-test to ensure Day 4 acceptance criteria is met.
    """
    # Count all test functions in this module
    import sys

    current_module = sys.modules[__name__]
    test_functions = [
        name
        for name in dir(current_module)
        if name.startswith("test_") and callable(getattr(current_module, name))
    ]

    # Exclude this meta-test itself
    test_functions = [name for name in test_functions if name != "test_recovery_test_count"]

    assert (
        len(test_functions) >= 20
    ), f"Day 4 requires ≥20 recovery tests, found {len(test_functions)}"
