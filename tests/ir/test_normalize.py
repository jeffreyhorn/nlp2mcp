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
    text = dedent(
        """
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
        """
    )
    model = parser.parse_model_text(text)
    equations, bounds = normalize_model(model)
    assert model.normalized_bounds == bounds

    # Equation inequality flipped to <= form
    norm_e = equations["e"]
    assert norm_e.relation == Rel.LE

    # Lower bound becomes lo - x <= 0 for each index
    lo_i1 = bounds["x_lo(i1)"]
    assert lo_i1.relation == Rel.LE
    assert isinstance(lo_i1.expr, Binary)
    assert isinstance(lo_i1.expr.left, Const) and lo_i1.expr.left.value == 1.0
    assert isinstance(lo_i1.expr.right, VarRef) and lo_i1.expr.right.indices == ("i1",)

    # Upper bound becomes x - up <= 0
    up_i2 = bounds["x_up(i2)"]
    assert up_i2.relation == Rel.LE
    assert isinstance(up_i2.expr, Binary)
    assert isinstance(up_i2.expr.left, VarRef) and up_i2.expr.left.indices == ("i2",)
    assert isinstance(up_i2.expr.right, Const) and up_i2.expr.right.value == 5.0

    # Fixed scalar bound becomes equality
    fx = bounds["y_fx"]
    assert fx.relation == Rel.EQ


def test_ge_relation_flips_to_le():
    text = dedent(
        """
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =g= 5;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """
    )
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    norm = equations["g"]
    assert norm.relation == Rel.LE
    assert isinstance(norm.expr, Binary)
    assert isinstance(norm.expr.left, Const) and norm.expr.left.value == 5.0
    assert isinstance(norm.expr.right, VarRef)


def test_equality_remains_eq():
    text = dedent(
        """
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =e= 5;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """
    )
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    assert equations["g"].relation == Rel.EQ


def test_scalar_bounds_normalized():
    text = dedent(
        """
        Variables
            x
        ;

        x.lo = 0;
        x.up = 10;
        x.fx = 3;
        """
    )
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert set(bounds) == {"x_lo", "x_up", "x_fx"}
    assert bounds["x_lo"].relation == Rel.LE
    assert bounds["x_up"].relation == Rel.LE
    assert bounds["x_fx"].relation == Rel.EQ


def test_no_bounds_returns_empty():
    text = dedent(
        """
        Variables
            x
        ;

        Equations
            g
        ;

        g.. x =e= 0;

        Model m / g / ;
        Solve m using NLP minimizing x;
        """
    )
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert bounds == {}


def test_infinite_bounds_ignored():
    text = dedent(
        """
        Variables
            x ;

        x.lo = -INF;
        x.up = +INF;
        """
    )
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    assert bounds == {}


def test_scalar_equation_domain_metadata():
    text = dedent(
        """
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
        """
    )
    model = parser.parse_model_text(text)
    equations, _ = normalize_model(model)
    eq = equations["e"]
    assert eq.domain_sets == ()
    assert eq.expr_domain == ()
    assert eq.rank == 0


def test_normalized_bounds_metadata():
    text = dedent(
        """
        Sets
            i /i1, i2/ ;

        Variables
            x(i)
        ;

        x.lo(i) = 0;
        x.up(i) = 10;
        """
    )
    model = parser.parse_model_text(text)
    _, bounds = normalize_model(model)
    for eq in bounds.values():
        assert eq.domain_sets == ("i",)
        assert eq.expr_domain == ("i",)
        assert eq.rank == 1
