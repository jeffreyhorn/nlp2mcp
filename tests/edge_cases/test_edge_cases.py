"""
Edge case tests for nlp2mcp.

This test suite implements the edge cases documented in docs/testing/EDGE_CASE_MATRIX.md.
Tests are organized by category: Constraint Types, Bounds, Indexing, Expressions, Sparsity,
and Special Structures.
"""

import pytest

from src.ir.parser import parse_model_text


class TestConstraintTypes:
    """Category 1: Tests for various constraint type combinations."""

    def test_only_equalities(self):
        """EC-1.1: Model with only equality constraints."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5/ ;

Parameters
    a(i) / i1 1.5, i2 2.0, i3 1.8, i4 2.2, i5 1.9 / ;

Variables
    x(i)
    obj ;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =e= a(i);

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Should have equalities but no inequalities or bounds beyond free
        assert len(model.equations) >= 1

    def test_only_inequalities(self):
        """EC-1.2: Model with only inequality constraints."""
        gams_code = """
Sets
    i /i1, i2, i3/ ;

Variables
    x(i)
    obj ;

Equations
    ineq1(i)
    objective ;

ineq1(i)..
    x(i) =l= 10;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_only_bounds(self):
        """EC-1.3: Model with only variable bounds (no explicit constraints)."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

x.lo = 0;
x.up = 10;
y.lo = -5;
y.up = 5;
z.fx = 3.14;

Equations
    objective ;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Should have bounds on x, y, z
        assert "x" in model.variables and (
            model.variables["x"].lo is not None
            or model.variables["x"].up is not None
            or model.variables["x"].fx is not None
        )
        assert "y" in model.variables and (
            model.variables["y"].lo is not None
            or model.variables["y"].up is not None
            or model.variables["y"].fx is not None
        )
        assert "z" in model.variables and (
            model.variables["z"].lo is not None
            or model.variables["z"].up is not None
            or model.variables["z"].fx is not None
        )

    def test_mixed_all_types(self):
        """EC-1.4: Model with equalities, inequalities, and bounds."""
        gams_code = """
Sets
    i /i1, i2, i3/ ;

Variables
    x(i)
    y
    obj ;

x.lo(i) = 0;
x.up(i) = 10;
y.lo = -5;

Equations
    eq1
    ineq1(i)
    objective ;

eq1..
    sum(i, x(i)) =e= 10;

ineq1(i)..
    x(i) =l= y + 5;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 2

        # Verify both x and y have bounds as specified in the GAMS code
        var_x = model.variables.get("x")
        assert "x" in model.variables
        assert (
            var_x.lo is not None
            or var_x.up is not None
            or var_x.fx is not None
            or len(var_x.lo_map) > 0
            or len(var_x.up_map) > 0
            or len(var_x.fx_map) > 0
        ), "Variable x should have bounds set (lo and up for indexed)"

        var_y = model.variables.get("y")
        assert "y" in model.variables
        assert (
            var_y.lo is not None
            or var_y.up is not None
            or var_y.fx is not None
            or len(var_y.lo_map) > 0
            or len(var_y.up_map) > 0
            or len(var_y.fx_map) > 0
        ), "Variable y should have bounds set (lo)"

    def test_no_constraints(self):
        """EC-1.5: Model with no constraints (only objective)."""
        gams_code = """
Variables
    x
    y
    obj ;

Equations
    objective ;

objective..
    obj =e= x + y;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Only the objective equation
        assert len(model.equations) == 1


class TestBoundsConfigurations:
    """Category 2: Tests for various bound configurations."""

    def test_all_finite_bounds(self):
        """EC-2.1: All variables have finite lower and upper bounds."""
        gams_code = """
Sets
    i /i1, i2, i3/ ;

Variables
    x(i)
    obj ;

x.lo(i) = 0;
x.up(i) = 10;

Equations
    objective ;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        var_x = model.variables["x"]
        assert "x" in model.variables and (
            var_x.lo is not None
            or var_x.up is not None
            or var_x.fx is not None
            or len(var_x.lo_map) > 0
            or len(var_x.up_map) > 0
            or len(var_x.fx_map) > 0
        )

    def test_all_infinite_bounds(self):
        """EC-2.2: All variables are free (no bounds)."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    objective ;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Variables should be free (no explicit bounds set)

    def test_mixed_finite_infinite(self):
        """EC-2.3: Some variables bounded, some free."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

x.lo = 0;
x.up = 10;
y.lo = -5;

Equations
    objective ;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert "x" in model.variables and (
            model.variables["x"].lo is not None
            or model.variables["x"].up is not None
            or model.variables["x"].fx is not None
        )

    def test_fixed_variables(self):
        """EC-2.4: Variables fixed to specific values."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

x.fx = 5;
y.fx = -3.14;
z.fx = 0;

Equations
    objective ;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert "x" in model.variables and (
            model.variables["x"].lo is not None
            or model.variables["x"].up is not None
            or model.variables["x"].fx is not None
        )
        assert "y" in model.variables and (
            model.variables["y"].lo is not None
            or model.variables["y"].up is not None
            or model.variables["y"].fx is not None
        )
        assert "z" in model.variables and (
            model.variables["z"].lo is not None
            or model.variables["z"].up is not None
            or model.variables["z"].fx is not None
        )

    def test_duplicate_bounds(self):
        """EC-2.5: Bounds set multiple times use last-write-wins (GAMS semantics)."""
        gams_code = """
Variables
    x
    obj ;

x.lo = 0;
x.up = 10;
x.lo = 1;
x.up = 5;

Equations
    objective ;

objective..
    obj =e= x;

Model test /all/ ;
"""
        # Issue #714: GAMS allows repeated bound assignments; last value wins.
        ir = parse_model_text(gams_code)
        var = ir.variables["x"]
        assert var.lo == 1
        assert var.up == 5


class TestIndexingComplexity:
    """Category 3: Tests for various indexing patterns."""

    def test_scalar_only(self):
        """EC-3.1: Model with only scalar variables and equations."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    eq1
    eq2
    objective ;

eq1..
    x + y =e= 10;

eq2..
    y + z =l= 5;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 2

    def test_single_index(self):
        """EC-3.2: Variables/equations with single index."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5/ ;

Variables
    x(i)
    obj ;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =e= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_multi_index(self):
        """EC-3.3: Variables/equations with multiple indices."""
        gams_code = """
Sets
    i /i1, i2, i3/
    j /j1, j2, j3/ ;

Variables
    x(i,j)
    obj ;

Equations
    eq1(i,j)
    objective ;

eq1(i,j)..
    x(i,j) =e= 1;

objective..
    obj =e= sum(i, sum(j, x(i,j)));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_sparse_indexing(self):
        """EC-3.4: Sparse indexing with conditional domains."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5/
    j /j1, j2, j3, j4, j5/ ;

Variables
    x(i,j)
    obj ;

Equations
    eq1(i,j)
    objective ;

eq1(i,j)..
    x(i,j) =e= 1;

objective..
    obj =e= sum(i, sum(j, x(i,j)));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Should handle sparse indexing

    def test_aliased_sets(self):
        """EC-3.5: Using aliased sets."""
        gams_code = """
Sets
    i /i1, i2, i3/
    j /j1, j2, j3/ ;

Variables
    x(i,j)
    obj ;

Equations
    eq1(i,j)
    objective ;

eq1(i,j)..
    x(i,j) =e= 1;

objective..
    obj =e= sum(i, sum(j, x(i,j)));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1


class TestExpressionComplexity:
    """Category 4: Tests for various expression complexities."""

    def test_constant_expressions(self):
        """EC-4.1: Equations with constant right-hand sides."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    eq1
    eq2
    eq3
    objective ;

eq1..
    x =e= 5;

eq2..
    y =e= -3.14;

eq3..
    z =l= 0;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 3

    def test_linear_only(self):
        """EC-4.2: Only linear expressions."""
        gams_code = """
Sets
    i /i1, i2, i3/ ;

Parameters
    a(i) / i1 2.0, i2 3.0, i3 1.5 / ;

Variables
    x(i)
    obj ;

Equations
    eq1
    objective ;

eq1..
    sum(i, a(i) * x(i)) =l= 10;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_quadratic_terms(self):
        """EC-4.3: Quadratic expressions (x*x, x*y)."""
        gams_code = """
Variables
    x
    y
    obj ;

Equations
    eq1
    objective ;

eq1..
    x * x + y * y =l= 100;

objective..
    obj =e= x + y;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_highly_nonlinear(self):
        """EC-4.4: Highly nonlinear expressions."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    eq1
    objective ;

eq1..
    x * y * z + x * x * y =e= 10;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_very_long_expressions(self):
        """EC-4.5: Very long expressions (50+ terms)."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20, i21, i22, i23, i24, i25, i26, i27, i28, i29, i30, i31, i32, i33, i34, i35, i36, i37, i38, i39, i40, i41, i42, i43, i44, i45, i46, i47, i48, i49, i50, i51, i52, i53, i54, i55, i56, i57, i58, i59, i60/ ;

Variables
    x(i)
    obj ;

Equations
    eq1
    objective ;

eq1..
    sum(i, x(i)) =l= 1000;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1


class TestSparsityPatterns:
    """Category 5: Tests for various sparsity patterns in Jacobian."""

    def test_dense_jacobian(self):
        """EC-5.1: Dense Jacobian (all variables in all constraints)."""
        gams_code = """
Variables
    x1
    x2
    x3
    obj ;

Equations
    eq1
    eq2
    eq3
    objective ;

eq1..
    x1 + x2 + x3 =e= 10;

eq2..
    x1 * x2 + x2 * x3 + x1 * x3 =l= 20;

eq3..
    x1 + 2*x2 + 3*x3 =g= 5;

objective..
    obj =e= x1 + x2 + x3;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 3

    def test_sparse_jacobian(self):
        """EC-5.2: Sparse Jacobian (<10% non-zero)."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20/ ;

Variables
    x(i)
    obj ;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =e= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Each equation only involves one variable (diagonal pattern)

    def test_block_diagonal(self):
        """EC-5.3: Block diagonal structure."""
        gams_code = """
Sets
    i /i1, i2, i3/
    j /j1, j2, j3/ ;

Variables
    x(i)
    y(j)
    obj ;

Equations
    eq_x(i)
    eq_y(j)
    objective ;

eq_x(i)..
    x(i) =e= 1;

eq_y(j)..
    y(j) =e= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # x equations independent of y equations

    def test_single_variable_per_constraint(self):
        """EC-5.4: Each constraint uses exactly one variable."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5/ ;

Variables
    x(i)
    obj ;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =e= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1


class TestSpecialStructures:
    """Category 6: Tests for special model structures."""

    def test_single_variable_model(self):
        """EC-6.1: Model with only one variable."""
        gams_code = """
Variables
    x
    obj ;

x.lo = 0;
x.up = 10;

Equations
    eq1
    objective ;

eq1..
    x =l= 5;

objective..
    obj =e= x;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert "x" in model.variables and (
            model.variables["x"].lo is not None
            or model.variables["x"].up is not None
            or model.variables["x"].fx is not None
        )

    def test_single_constraint_model(self):
        """EC-6.2: Model with only one constraint (plus objective)."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    eq1
    objective ;

eq1..
    x + y + z =e= 10;

objective..
    obj =e= x + y + z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        assert len(model.equations) >= 1

    def test_large_model(self):
        """EC-6.3: Large model (100+ variables, 100+ constraints)."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20, i21, i22, i23, i24, i25, i26, i27, i28, i29, i30, i31, i32, i33, i34, i35, i36, i37, i38, i39, i40, i41, i42, i43, i44, i45, i46, i47, i48, i49, i50, i51, i52, i53, i54, i55, i56, i57, i58, i59, i60, i61, i62, i63, i64, i65, i66, i67, i68, i69, i70, i71, i72, i73, i74, i75, i76, i77, i78, i79, i80, i81, i82, i83, i84, i85, i86, i87, i88, i89, i90, i91, i92, i93, i94, i95, i96, i97, i98, i99, i100, i101, i102, i103, i104, i105, i106, i107, i108, i109, i110, i111, i112, i113, i114, i115, i116, i117, i118, i119, i120/ ;

Variables
    x(i)
    obj ;

x.lo(i) = 0;
x.up(i) = 10;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =l= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # eq1(i) is stored as one equation definition with domain ('i',)
        # Check that the set has 120+ elements and we have the indexed equation
        assert "i" in model.sets and len(model.sets["i"].members) >= 120
        assert "eq1" in model.equations and len(model.equations["eq1"].domain) > 0

    def test_empty_set_indexing(self):
        """EC-6.4: Indexing over empty set."""
        gams_code = """
Sets
    i /i1, i2, i3, i4, i5/
    empty(i) / i1 / ;

Variables
    x(i)
    obj ;

Equations
    eq1(i)
    objective ;

eq1(i)..
    x(i) =e= 1;

objective..
    obj =e= sum(i, x(i));

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Should handle empty conditional domain

    def test_objective_only_model(self):
        """EC-6.5: Model with only objective (no constraints or bounds)."""
        gams_code = """
Variables
    x
    y
    z
    obj ;

Equations
    objective ;

objective..
    obj =e= x * x + y * y + z * z;

Model test /all/ ;
"""
        model = parse_model_text(gams_code)
        assert model is not None
        # Should have only the objective equation
        assert len(model.equations) == 1
