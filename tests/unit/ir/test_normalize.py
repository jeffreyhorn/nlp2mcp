"""Normalization tests covering canonical equations and bounds."""

import importlib
from textwrap import dedent

from src.ir import parser
from src.ir.ast import Binary, Const, VarRef
from src.ir.normalize import normalize_model
from src.ir.symbols import Rel


def test_normalize_exports_expected_names():
    normalize = importlib.import_module("src.ir.normalize")
    for attr in ("NormalizedEquation", "normalize_equation", "normalize_model"):
        assert hasattr(normalize, attr), f"normalize.py should export {attr}"


def test_model_ir_loads_without_side_effects():
    model_ir = importlib.import_module("src.ir.model_ir")
    assert hasattr(model_ir, "ModelIR"), "model_ir.py should define ModelIR"


def test_normalize_includes_variable_bounds():
    text = dedent("""
        Sets
            i /i1, i2/ ;

        Variables
            x(i)
            y ;

        Equations
            e(i)
        ;

        e(i).. x(i) =g= y;

        x.lo(i) = 1;
        x.up(i) = 5;
        y.fx = 3;

        Model m / e / ;
        Solve m using NLP minimizing y;
        """)
    model = parser.parse_model_text(text)
    equations, bounds = normalize_model(model)
    assert model.normalized_bounds == bounds

    # Equation inequality flipped to <= form
    norm_e = equations["e"]
    assert norm_e.relation == Rel.LE

    # Lower bound becomes lo - x <= 0 for each index
    # Bound names use underscores for valid GAMS identifiers: x_lo_i1, not x_lo(i1)
    lo_i1 = bounds["x_lo_i1"]
    assert lo_i1.relation == Rel.LE
    assert isinstance(lo_i1.expr, Binary)
    assert isinstance(lo_i1.expr.left, Const) and lo_i1.expr.left.value == 1.0
    assert isinstance(lo_i1.expr.right, VarRef) and lo_i1.expr.right.indices == ("i1",)

    # Upper bound becomes x - up <= 0
    up_i2 = bounds["x_up_i2"]
    assert up_i2.relation == Rel.LE
    assert isinstance(up_i2.expr, Binary)
    assert isinstance(up_i2.expr.left, VarRef) and up_i2.expr.left.indices == ("i2",)
    assert isinstance(up_i2.expr.right, Const) and up_i2.expr.right.value == 5.0

    # Fixed scalar bound becomes equality
    fx = bounds["y_fx"]
    assert fx.relation == Rel.EQ


def test_ge_relation_flips_to_le():
    text = dedent("""
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =g= 5;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """)
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    norm = equations["g"]
    assert norm.relation == Rel.LE
    assert isinstance(norm.expr, Binary)
    assert isinstance(norm.expr.left, Const) and norm.expr.left.value == 5.0
    assert isinstance(norm.expr.right, VarRef)


def test_equality_remains_eq():
    text = dedent("""
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =e= 5;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """)
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    assert equations["g"].relation == Rel.EQ


def test_scalar_bounds_normalized():
    text = dedent("""
        Variables
            x
        ;

        x.lo = 0;
        x.up = 10;
        x.fx = 3;
        """)
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert set(bounds) == {"x_lo", "x_up", "x_fx"}
    assert bounds["x_lo"].relation == Rel.LE
    assert bounds["x_up"].relation == Rel.LE
    assert bounds["x_fx"].relation == Rel.EQ


def test_no_bounds_returns_empty():
    text = dedent("""
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =e= 0;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """)
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert bounds == {}


def test_infinite_bounds_ignored():
    text = dedent("""
        Variables
            x ;

        x.lo = -INF;
        x.up = +INF;
        """)
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert bounds == {}


def test_scalar_equation_domain_metadata():
    text = dedent("""
        Scalars a / 1 /;

        Variables
            x
        ;

        Equations
            e
        ;

        e.. x =e= a;

        Model m / e / ;
        Solve m using NLP minimizing x;
        """)
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    eq = equations["e"]
    assert eq.domain_sets == ()
    assert eq.expr_domain == ()
    assert eq.rank == 0


def test_normalized_bounds_metadata():
    """Test metadata for bounds that expand to per-element equations.

    When x.lo(i) = 0 is used, the parser expands this to per-element bounds
    (one for each element of i). These create scalar equations (not indexed)
    because each equation is for a specific element, not a domain variable.

    This avoids invalid GAMS syntax like x_fx(1)(i) when element indices are
    embedded in the equation name (e.g., x_fx(1).. x("1") - 0 =E= 0).
    """
    text = dedent("""
        Sets
            i /i1, i2/ ;

        Variables
            x(i)
        ;

        x.lo(i) = 0;
        x.up(i) = 10;
        """)
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    # Per-element bounds create scalar equations (domain_sets = ())
    # Each equation applies to a specific element, not indexed over domain
    for eq in bounds.values():
        assert eq.domain_sets == ()
        # Expression domain also becomes scalar for per-element bounds
        assert eq.expr_domain == ()
        assert eq.rank == 0


# Tests for Issue #19: Objective Expression Extraction Before Normalization


def test_normalize_extracts_objective_expression_lhs():
    """Test that normalize_model() populates ObjectiveIR.expr when objvar is on LHS."""
    text = dedent("""
        Variables
            x
            obj ;

        Equations
            objective ;

        objective.. obj =e= x;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # Before normalization: expr should be None
    assert model.objective is not None
    assert model.objective.expr is None
    assert model.objective.objvar == "obj"

    # After normalization: expr should be populated
    normalize_model(model)
    assert model.objective.expr is not None

    # Expression should be x (from RHS of: obj =e= x)
    assert isinstance(model.objective.expr, VarRef)
    assert model.objective.expr.name == "x"


def test_normalize_extracts_objective_expression_rhs():
    """Test that normalize_model() populates ObjectiveIR.expr when objvar is on RHS."""
    text = dedent("""
        Variables
            x
            obj ;

        Equations
            objective ;

        objective.. x =e= obj;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # Before normalization: expr should be None
    assert model.objective.expr is None

    # After normalization: expr should be populated
    normalize_model(model)
    assert model.objective.expr is not None

    # Expression should be x (from LHS of: x =e= obj)
    assert isinstance(model.objective.expr, VarRef)
    assert model.objective.expr.name == "x"


def test_normalize_extracts_complex_objective_expression():
    """Test objective extraction with complex expressions."""
    text = dedent("""
        Variables
            x
            y
            obj ;

        Equations
            objective ;

        objective.. obj =e= x * x + y;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # Before normalization: expr should be None
    assert model.objective.expr is None

    # After normalization: expr should be populated
    normalize_model(model)
    assert model.objective.expr is not None

    # Expression should be x*x + y (Binary addition)
    assert isinstance(model.objective.expr, Binary)
    assert model.objective.expr.op == "+"


def test_normalize_preserves_existing_objective_expr():
    """Test that normalize_model() doesn't overwrite existing ObjectiveIR.expr."""
    text = dedent("""
        Variables
            x
            obj ;

        Equations
            objective ;

        objective.. obj =e= x;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # Manually set objective.expr before normalization
    existing_expr = Const(42.0)
    model.objective.expr = existing_expr

    # After normalization: expr should remain unchanged
    normalize_model(model)
    assert model.objective.expr is existing_expr


def test_normalize_handles_objective_without_defining_equation():
    """Test that normalize_model() gracefully handles objectives without defining equations.

    Some models minimize a simple variable (e.g., 'minimize obj') without an equation
    like 'obj =e= expr'. This is valid - the objective expression remains None and
    will be handled by the AD code as a simple variable reference.
    """
    text = dedent("""
        Variables
            x
            obj ;

        Equations
            some_equation ;

        some_equation.. x =e= 5;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # Before normalization: objective.expr should be None
    assert model.objective.expr is None

    # Normalization should succeed without raising an error
    normalize_model(model)

    # After normalization: objective.expr is still None (no defining equation found)
    # This is OK - the objective is just the variable 'obj' itself
    assert model.objective.expr is None
    assert model.objective.objvar == "obj"


def test_normalize_skips_indexed_objective_equations():
    """Test that objective extraction skips indexed equations."""
    text = dedent("""
        Sets
            i /i1, i2/ ;

        Variables
            x(i)
            obj ;

        Equations
            indexed_eq(i)
            scalar_eq ;

        indexed_eq(i).. obj =e= x(i);
        scalar_eq.. obj =e= 5;

        Model test /all/;
        Solve test using NLP minimizing obj;
        """)
    model = parser.parse_model_text(text)

    # After normalization: should use scalar_eq, not indexed_eq
    normalize_model(model)
    assert model.objective.expr is not None

    # Expression should be Const(5) from scalar_eq
    assert isinstance(model.objective.expr, Const)
    assert model.objective.expr.value == 5.0
