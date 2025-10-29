"""
Tests for Jacobian Structure (Day 7)

Test Coverage:
-------------
1. JacobianStructure creation and storage
2. Setting and getting derivatives
3. Row and column queries
4. Nonzero entry tracking
5. Density computation
6. GradientVector creation and storage
7. Gradient component queries
"""

from src.ad.jacobian import GradientVector, JacobianStructure
from src.ir.ast import Binary, Const, VarRef

# ============================================================================
# Test JacobianStructure
# ============================================================================


class TestJacobianStructureBasics:
    """Test basic Jacobian structure operations."""

    def test_empty_jacobian(self):
        """Test creating empty Jacobian structure."""
        jac = JacobianStructure(num_rows=3, num_cols=2)

        assert jac.num_rows == 3
        assert jac.num_cols == 2
        assert jac.num_nonzeros() == 0
        assert jac.density() == 0.0

    def test_set_and_get_derivative(self):
        """Test setting and retrieving a derivative."""
        jac = JacobianStructure(num_rows=2, num_cols=2)
        expr = Const(1.0)

        jac.set_derivative(0, 0, expr)

        result = jac.get_derivative(0, 0)
        assert result is expr
        assert jac.num_nonzeros() == 1

    def test_get_nonexistent_derivative_returns_none(self):
        """Test getting a derivative that doesn't exist returns None."""
        jac = JacobianStructure(num_rows=2, num_cols=2)

        result = jac.get_derivative(0, 1)
        assert result is None

    def test_multiple_derivatives(self):
        """Test setting multiple derivatives."""
        jac = JacobianStructure(num_rows=2, num_cols=3)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 1, Const(2.0))
        jac.set_derivative(1, 2, Const(3.0))

        assert jac.num_nonzeros() == 3
        assert isinstance(jac.get_derivative(0, 0), Const)
        assert isinstance(jac.get_derivative(0, 1), Const)
        assert isinstance(jac.get_derivative(1, 2), Const)
        assert jac.get_derivative(0, 2) is None

    def test_overwrite_derivative(self):
        """Test overwriting an existing derivative."""
        jac = JacobianStructure(num_rows=2, num_cols=2)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 0, Const(2.0))

        result = jac.get_derivative(0, 0)
        assert isinstance(result, Const)
        assert result.value == 2.0
        assert jac.num_nonzeros() == 1  # Still just one entry


class TestJacobianRowColumn:
    """Test row and column queries."""

    def test_get_row(self):
        """Test retrieving all entries in a row."""
        jac = JacobianStructure(num_rows=2, num_cols=3)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 2, Const(3.0))
        jac.set_derivative(1, 1, Const(2.0))

        row0 = jac.get_row(0)
        assert len(row0) == 2
        assert 0 in row0
        assert 2 in row0
        assert 1 not in row0

    def test_get_empty_row(self):
        """Test retrieving an empty row."""
        jac = JacobianStructure(num_rows=2, num_cols=2)

        row0 = jac.get_row(0)
        assert len(row0) == 0

    def test_get_col(self):
        """Test retrieving all entries in a column."""
        jac = JacobianStructure(num_rows=3, num_cols=2)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(1, 0, Const(2.0))
        jac.set_derivative(2, 1, Const(3.0))

        col0 = jac.get_col(0)
        assert len(col0) == 2
        assert 0 in col0
        assert 1 in col0
        assert 2 not in col0

    def test_get_empty_col(self):
        """Test retrieving an empty column."""
        jac = JacobianStructure(num_rows=2, num_cols=2)

        col0 = jac.get_col(0)
        assert len(col0) == 0


class TestJacobianSparsity:
    """Test sparsity tracking and computation."""

    def test_get_nonzero_entries(self):
        """Test getting list of all nonzero (row, col) pairs."""
        jac = JacobianStructure(num_rows=2, num_cols=3)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 2, Const(3.0))
        jac.set_derivative(1, 1, Const(2.0))

        entries = jac.get_nonzero_entries()
        assert len(entries) == 3
        assert (0, 0) in entries
        assert (0, 2) in entries
        assert (1, 1) in entries

    def test_density_computation(self):
        """Test density calculation."""
        jac = JacobianStructure(num_rows=2, num_cols=3)

        # 2 nonzeros out of 2*3=6 total
        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(1, 1, Const(2.0))

        assert jac.density() == 2 / 6

    def test_density_empty_jacobian(self):
        """Test density of empty Jacobian."""
        jac = JacobianStructure(num_rows=0, num_cols=0)
        assert jac.density() == 0.0

    def test_density_fully_dense(self):
        """Test density of fully dense Jacobian."""
        jac = JacobianStructure(num_rows=2, num_cols=2)

        jac.set_derivative(0, 0, Const(1.0))
        jac.set_derivative(0, 1, Const(1.0))
        jac.set_derivative(1, 0, Const(1.0))
        jac.set_derivative(1, 1, Const(1.0))

        assert jac.density() == 1.0


class TestJacobianWithIndexMapping:
    """Test Jacobian with IndexMapping integration."""

    def test_get_derivative_by_names(self):
        """Test retrieving derivative using variable/equation names."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef

        # Create simple model
        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))
        model_ir.add_equation(EquationDef("g1", (), Rel.LE, (None, None)))

        # Build mapping
        mapping = build_index_mapping(model_ir)

        # Create Jacobian with mapping
        jac = JacobianStructure(
            index_mapping=mapping, num_rows=mapping.num_eqs, num_cols=mapping.num_vars
        )

        # Set derivative: ∂g1/∂x = 1
        jac.set_derivative(0, 0, Const(1.0))

        # Retrieve by names
        result = jac.get_derivative_by_names("g1", (), "x", ())
        assert isinstance(result, Const)
        assert result.value == 1.0

    def test_get_derivative_by_names_not_found(self):
        """Test retrieving non-existent derivative by names returns None."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import EquationDef, Rel, VariableDef

        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_equation(EquationDef("g1", (), Rel.LE, (None, None)))

        mapping = build_index_mapping(model_ir)
        jac = JacobianStructure(index_mapping=mapping)

        # No derivative set
        result = jac.get_derivative_by_names("g1", (), "x", ())
        assert result is None

    def test_get_derivative_by_names_without_mapping_raises_error(self):
        """Test that get_derivative_by_names requires index_mapping."""
        jac = JacobianStructure()

        try:
            jac.get_derivative_by_names("g1", (), "x", ())
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "index_mapping" in str(e).lower()


# ============================================================================
# Test GradientVector
# ============================================================================


class TestGradientVectorBasics:
    """Test basic gradient vector operations."""

    def test_empty_gradient(self):
        """Test creating empty gradient vector."""
        grad = GradientVector(num_cols=3)

        assert grad.num_cols == 3
        assert grad.num_nonzeros() == 0

    def test_set_and_get_derivative(self):
        """Test setting and retrieving gradient component."""
        grad = GradientVector(num_cols=2)
        expr = Const(2.0)

        grad.set_derivative(0, expr)

        result = grad.get_derivative(0)
        assert result is expr
        assert grad.num_nonzeros() == 1

    def test_get_nonexistent_derivative_returns_none(self):
        """Test getting non-existent component returns None."""
        grad = GradientVector(num_cols=2)

        result = grad.get_derivative(1)
        assert result is None

    def test_multiple_components(self):
        """Test setting multiple gradient components."""
        grad = GradientVector(num_cols=3)

        grad.set_derivative(0, Const(1.0))
        grad.set_derivative(1, Const(2.0))
        grad.set_derivative(2, Binary("+", VarRef("x"), Const(1.0)))

        assert grad.num_nonzeros() == 3
        assert isinstance(grad.get_derivative(0), Const)
        assert isinstance(grad.get_derivative(2), Binary)

    def test_get_all_derivatives(self):
        """Test retrieving all gradient components."""
        grad = GradientVector(num_cols=3)

        grad.set_derivative(0, Const(1.0))
        grad.set_derivative(2, Const(3.0))

        all_derivs = grad.get_all_derivatives()
        assert len(all_derivs) == 2
        assert 0 in all_derivs
        assert 2 in all_derivs
        assert 1 not in all_derivs


class TestGradientWithIndexMapping:
    """Test gradient vector with IndexMapping integration."""

    def test_get_derivative_by_name(self):
        """Test retrieving gradient component by variable name."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import VariableDef

        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))
        model_ir.add_var(VariableDef("y", ()))

        mapping = build_index_mapping(model_ir)
        grad = GradientVector(index_mapping=mapping, num_cols=mapping.num_vars)

        # Set ∂f/∂x = 2
        grad.set_derivative(0, Const(2.0))

        # Retrieve by name
        result = grad.get_derivative_by_name("x")
        assert isinstance(result, Const)
        assert result.value == 2.0

    def test_get_derivative_by_name_not_found(self):
        """Test retrieving non-existent gradient by name returns None."""
        from src.ad.index_mapping import build_index_mapping
        from src.ir.model_ir import ModelIR
        from src.ir.symbols import VariableDef

        model_ir = ModelIR()
        model_ir.add_var(VariableDef("x", ()))

        mapping = build_index_mapping(model_ir)
        grad = GradientVector(index_mapping=mapping)

        # No derivative set
        result = grad.get_derivative_by_name("x")
        assert result is None

    def test_get_derivative_by_name_without_mapping_raises_error(self):
        """Test that get_derivative_by_name requires index_mapping."""
        grad = GradientVector()

        try:
            grad.get_derivative_by_name("x")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "index_mapping" in str(e).lower()
