"""Tests for automated fixture generation framework.

Sprint 9 Day 1: Validates that fixture generator creates valid IR nodes.
"""

import pytest

from src.ir.model_ir import ModelIR
from src.ir.symbols import ParameterDef, Rel, VariableDef, VarKind
from tests.fixtures.generate_fixtures import (
    create_bounded_variable_fixture,
    create_equation_fixture,
    create_model_fixture,
    create_parameter_fixture,
    create_simple_nlp_fixture,
    create_variable_fixture,
)


class TestCreateVariableFixture:
    """Test variable fixture creation."""

    def test_create_variable_fixture_positive(self):
        """Test creating a positive variable with bounds."""
        var = create_variable_fixture("x", "positive", (0, 10))

        assert var.name == "x"
        assert var.kind == VarKind.POSITIVE
        assert var.lo == 0
        assert var.up == 10

    def test_create_variable_fixture_free(self):
        """Test creating a free variable (no bounds)."""
        var = create_variable_fixture("y", "continuous")

        assert var.name == "y"
        assert var.kind == VarKind.CONTINUOUS
        assert var.lo is None
        assert var.up is None

    def test_create_variable_fixture_binary(self):
        """Test creating a binary variable."""
        var = create_variable_fixture("z", "binary")

        assert var.name == "z"
        assert var.kind == VarKind.BINARY

    def test_create_variable_fixture_integer(self):
        """Test creating an integer variable with bounds."""
        var = create_variable_fixture("n", "integer", (1, 100))

        assert var.name == "n"
        assert var.kind == VarKind.INTEGER
        assert var.lo == 1
        assert var.up == 100

    def test_create_variable_fixture_negative(self):
        """Test creating a negative variable."""
        var = create_variable_fixture("w", "negative", (None, -1))

        assert var.name == "w"
        assert var.kind == VarKind.NEGATIVE
        assert var.lo is None
        assert var.up == -1

    def test_create_variable_fixture_invalid_kind(self):
        """Test that invalid variable kind raises error."""
        with pytest.raises(ValueError, match="Invalid variable kind"):
            create_variable_fixture("x", "invalid_kind")


class TestCreateParameterFixture:
    """Test parameter fixture creation."""

    def test_create_parameter_fixture(self):
        """Test creating a parameter with scalar value."""
        param = create_parameter_fixture("a", 2.5)

        assert param.name == "a"
        assert param.domain == ()
        assert param.values == {(): 2.5}

    def test_create_parameter_fixture_zero(self):
        """Test creating a parameter with zero value."""
        param = create_parameter_fixture("b", 0.0)

        assert param.name == "b"
        assert param.values == {(): 0.0}

    def test_create_parameter_fixture_negative(self):
        """Test creating a parameter with negative value."""
        param = create_parameter_fixture("c", -3.14)

        assert param.name == "c"
        assert param.values == {(): -3.14}

    def test_create_parameter_fixture_with_domain(self):
        """Test creating an indexed parameter."""
        param = create_parameter_fixture("d", 5.0, ("i",))

        assert param.name == "d"
        assert param.domain == ("i",)
        assert param.values == {}  # Indexed params don't have scalar value


class TestCreateEquationFixture:
    """Test equation fixture creation."""

    def test_create_equation_fixture_simple_equality(self):
        """Test creating a simple equality equation."""
        eq = create_equation_fixture("obj", "x", "=e=", 0)

        assert eq.name == "obj"
        assert eq.relation == Rel.EQ
        assert eq.domain == ()

    def test_create_equation_fixture_multiplication(self):
        """Test creating equation with multiplication."""
        eq = create_equation_fixture("obj2", "a*x", "=e=", 0)

        assert eq.name == "obj2"
        assert eq.relation == Rel.EQ
        # lhs should be Binary with "*"
        lhs, rhs = eq.lhs_rhs
        assert lhs.op == "*"

    def test_create_equation_fixture_addition(self):
        """Test creating equation with addition."""
        eq = create_equation_fixture("con", "x + y", "=l=", 10)

        assert eq.name == "con"
        assert eq.relation == Rel.LE
        lhs, rhs = eq.lhs_rhs
        assert lhs.op == "+"

    def test_create_equation_fixture_subtraction(self):
        """Test creating equation with subtraction."""
        eq = create_equation_fixture("diff", "x - y", "=g=", 5)

        assert eq.name == "diff"
        assert eq.relation == Rel.GE
        lhs, rhs = eq.lhs_rhs
        assert lhs.op == "-"

    def test_create_equation_fixture_invalid_relation(self):
        """Test that invalid relation raises error."""
        with pytest.raises(ValueError, match="Invalid relation"):
            create_equation_fixture("bad", "x", "==", 0)


class TestCreateModelFixture:
    """Test complete model fixture creation."""

    def test_create_model_fixture_empty(self):
        """Test creating an empty model."""
        model = create_model_fixture()

        assert isinstance(model, ModelIR)
        assert len(model.variables) == 0
        assert len(model.params) == 0
        assert len(model.equations) == 0

    def test_create_model_fixture_with_variables(self):
        """Test creating model with variables only."""
        model = create_model_fixture(
            variables=[("x", "positive", (0, 10)), ("y", "continuous", None)]
        )

        assert len(model.variables) == 2
        assert "x" in model.variables
        assert "y" in model.variables
        assert model.variables["x"].kind == VarKind.POSITIVE
        assert model.variables["y"].kind == VarKind.CONTINUOUS

    def test_create_model_fixture_with_parameters(self):
        """Test creating model with parameters only."""
        model = create_model_fixture(parameters=[("a", 2.5), ("b", 3.0)])

        assert len(model.params) == 2
        assert "a" in model.params
        assert "b" in model.params
        assert model.params["a"].values == {(): 2.5}
        assert model.params["b"].values == {(): 3.0}

    def test_create_model_fixture_with_equations(self):
        """Test creating model with equations only."""
        model = create_model_fixture(
            equations=[("obj", "x", "=e=", 0), ("con", "x + y", "=l=", 10)]
        )

        assert len(model.equations) == 2
        assert "obj" in model.equations
        assert "con" in model.equations

    def test_create_model_fixture_complete(self):
        """Test creating a complete model with all components."""
        model = create_model_fixture(
            variables=[("x", "positive", (0, 10)), ("y", "continuous", None)],
            parameters=[("a", 2.5), ("b", 3.0)],
            equations=[("obj", "a*x", "=e=", 0), ("con", "x + y", "=l=", 10)],
        )

        assert len(model.variables) == 2
        assert len(model.params) == 2
        assert len(model.equations) == 2

        # Verify model is properly structured
        assert isinstance(model, ModelIR)
        assert all(isinstance(v, VariableDef) for v in model.variables.values())
        assert all(isinstance(p, ParameterDef) for p in model.params.values())


class TestConvenienceFunctions:
    """Test convenience fixture functions."""

    def test_create_simple_nlp_fixture(self):
        """Test creating a simple NLP model fixture."""
        model = create_simple_nlp_fixture()

        assert len(model.variables) == 2
        assert len(model.params) == 1
        assert len(model.equations) == 2

        # Verify variables
        assert "x" in model.variables
        assert "y" in model.variables
        assert model.variables["x"].kind == VarKind.POSITIVE
        assert model.variables["y"].kind == VarKind.POSITIVE

        # Verify parameter
        assert "a" in model.params
        assert model.params["a"].values == {(): 2.0}

        # Verify equations
        assert "obj" in model.equations
        assert "con" in model.equations

    def test_create_bounded_variable_fixture(self):
        """Test creating bounded variable fixture."""
        model = create_bounded_variable_fixture()

        assert len(model.variables) == 3

        # Verify bounded positive variable
        assert model.variables["x"].kind == VarKind.POSITIVE
        assert model.variables["x"].lo == 0
        assert model.variables["x"].up == 10

        # Verify free variable
        assert model.variables["y"].kind == VarKind.CONTINUOUS
        assert model.variables["y"].lo is None
        assert model.variables["y"].up is None

        # Verify binary variable
        assert model.variables["z"].kind == VarKind.BINARY


class TestFixtureValidation:
    """Test that generated fixtures are valid IR."""

    def test_fixture_is_serializable(self):
        """Test that generated fixtures can be used like real IR."""
        model = create_simple_nlp_fixture()

        # Should be able to add more components
        var = create_variable_fixture("z", "binary")
        model.add_var(var)

        assert len(model.variables) == 3
        assert "z" in model.variables

    def test_fixture_variables_have_required_fields(self):
        """Test that fixture variables have all required fields."""
        var = create_variable_fixture("x", "positive", (0, 10))

        # Check required fields exist
        assert hasattr(var, "name")
        assert hasattr(var, "kind")
        assert hasattr(var, "domain")
        assert hasattr(var, "lo")
        assert hasattr(var, "up")

    def test_fixture_parameters_have_required_fields(self):
        """Test that fixture parameters have all required fields."""
        param = create_parameter_fixture("a", 2.5)

        # Check required fields exist
        assert hasattr(param, "name")
        assert hasattr(param, "domain")
        assert hasattr(param, "values")

    def test_fixture_equations_have_required_fields(self):
        """Test that fixture equations have all required fields."""
        eq = create_equation_fixture("obj", "x", "=e=", 0)

        # Check required fields exist
        assert hasattr(eq, "name")
        assert hasattr(eq, "domain")
        assert hasattr(eq, "relation")
        assert hasattr(eq, "lhs_rhs")


class TestDeterministicGeneration:
    """Test that fixture generation is deterministic."""

    def test_same_inputs_same_output(self):
        """Test that same inputs generate same IR."""
        model1 = create_model_fixture(
            variables=[("x", "positive", (0, 10))], parameters=[("a", 2.5)]
        )

        model2 = create_model_fixture(
            variables=[("x", "positive", (0, 10))], parameters=[("a", 2.5)]
        )

        # Should have same structure
        assert len(model1.variables) == len(model2.variables)
        assert len(model1.params) == len(model2.params)

        # Should have same values
        assert model1.variables["x"].lo == model2.variables["x"].lo
        assert model1.variables["x"].up == model2.variables["x"].up
        assert model1.params["a"].values == model2.params["a"].values
