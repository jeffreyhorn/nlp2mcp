"""Unit tests for .l expression capture in VariableDef.

Sprint 20 Day 1: Tests for expression-based .l assignments (non-constant RHS).
"""

from textwrap import dedent

from src.ir import parser
from src.ir.ast import Binary, Const, VarRef


def test_scalar_l_assignment_expression():
    """Test scalar .l assignment with expression: a.l = (xmin+xmax)/2."""
    text = dedent("""
        Parameters
            xmin
            xmax
        ;

        xmin = 1.0;
        xmax = 5.0;

        Variables
            a
            obj
        ;

        a.l = (xmin + xmax) / 2;

        Equations objdef;
        objdef.. obj =e= a;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    # Verify a.l_expr is populated
    assert "a" in model.variables
    var_a = model.variables["a"]
    assert var_a.l_expr is not None
    assert isinstance(var_a.l_expr, Binary)
    assert var_a.l_expr.op == "/"

    # The expression should be: (xmin + xmax) / 2
    # Top level: division by 2
    assert isinstance(var_a.l_expr.right, Const)
    assert var_a.l_expr.right.value == 2.0


def test_indexed_l_assignment_expression():
    """Test indexed .l assignment with expression: x.l(i) = data(i)."""
    text = dedent("""
        Set i / i1, i2, i3 /;

        Parameters
            data(i)
        ;

        data('i1') = 1.0;
        data('i2') = 2.0;
        data('i3') = 3.0;

        Variables
            x(i)
            obj
        ;

        x.l(i) = data(i);

        Equations objdef;
        objdef.. obj =e= sum(i, x(i));

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    # Verify x.l_expr_map is populated
    assert "x" in model.variables
    var_x = model.variables["x"]
    assert var_x.l_expr_map is not None
    assert len(var_x.l_expr_map) > 0

    # Should have entry for index 'i'
    assert ("i",) in var_x.l_expr_map
    expr = var_x.l_expr_map[("i",)]
    assert expr is not None


def test_chained_l_assignment():
    """Test chained .l assignment referencing another variable: b.l = a.l + 1."""
    text = dedent("""
        Variables
            a
            b
            obj
        ;

        a.l = 2.0;
        b.l = a.l + 1;

        Equations objdef;
        objdef.. obj =e= a + b;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    # a.l = 2.0 should be stored as constant (not expression)
    var_a = model.variables["a"]
    assert var_a.l == 2.0
    assert var_a.l_expr is None  # Constant assignment doesn't use l_expr

    # b.l = a.l + 1 should be stored as expression
    var_b = model.variables["b"]
    assert var_b.l_expr is not None
    assert isinstance(var_b.l_expr, Binary)
    assert var_b.l_expr.op == "+"

    # Left side should be VarRef to 'a' with attribute 'l'
    assert isinstance(var_b.l_expr.left, VarRef)
    assert var_b.l_expr.left.name == "a"
    assert var_b.l_expr.left.attribute == "l"


def test_constant_l_assignment_not_stored_as_expression():
    """Test that constant .l assignments still use the old l field, not l_expr."""
    text = dedent("""
        Variables
            x
            obj
        ;

        x.l = 5.0;

        Equations objdef;
        objdef.. obj =e= x;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    var_x = model.variables["x"]
    # Constant values should still use the scalar .l field
    assert var_x.l == 5.0
    # l_expr should remain None for constant assignments
    assert var_x.l_expr is None


def test_mixed_constant_and_expression_l_assignments():
    """Test model with both constant and expression-based .l assignments."""
    text = dedent("""
        Parameters
            p1
            p2
        ;

        p1 = 10.0;
        p2 = 20.0;

        Variables
            a
            b
            c
            obj
        ;

        a.l = 1.0;
        b.l = p1 * 2;
        c.l = p1 + p2;

        Equations objdef;
        objdef.. obj =e= a + b + c;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    var_a = model.variables["a"]
    assert var_a.l == 1.0
    assert var_a.l_expr is None

    var_b = model.variables["b"]
    assert var_b.l is None  # Non-constant, so scalar field not used
    assert var_b.l_expr is not None
    assert isinstance(var_b.l_expr, Binary)

    var_c = model.variables["c"]
    assert var_c.l is None
    assert var_c.l_expr is not None
    assert isinstance(var_c.l_expr, Binary)


def test_l_assignment_overwrite_constant_then_expression():
    """Last-write-wins when .l is assigned constant then expression for same variable."""
    text = dedent("""
        Parameters
            p1
        ;

        p1 = 10.0;

        Variables
            x
            obj
        ;

        x.l = 1.0;
        x.l = p1 * 2;

        Equations objdef;
        objdef.. obj =e= x;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    var_x = model.variables["x"]
    # Final assignment is an expression, so l_expr should be set and l cleared
    assert var_x.l is None
    assert var_x.l_expr is not None
    assert isinstance(var_x.l_expr, Binary)


def test_l_assignment_overwrite_expression_then_constant():
    """Last-write-wins when .l is assigned expression then constant for same variable."""
    text = dedent("""
        Parameters
            p1
        ;

        p1 = 10.0;

        Variables
            x
            obj
        ;

        x.l = p1 * 2;
        x.l = 1.0;

        Equations objdef;
        objdef.. obj =e= x;

        Model m / all /;
        Solve m using NLP minimizing obj;
    """)

    model = parser.parse_model_text(text)

    var_x = model.variables["x"]
    # Final assignment is constant, so l should be set and l_expr cleared
    assert var_x.l == 1.0
    assert var_x.l_expr is None
