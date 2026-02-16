"""Unit tests for solve statements inside loop bodies (Issue #749).

Tests cover:
- Solve inside loop extracts objective variable and sense
- Top-level solve still works (regression)
- Solve inside loop with multi-model declaration
"""

from src.ir.parser import parse_model_text


class TestSolveInsideLoop:
    """Test that solve statements inside loop bodies are extracted."""

    def test_solve_inside_loop_extracts_objective(self):
        """Solve statement inside a loop sets model_ir.objective."""
        source = """
Set i / a, b /;
Set t / 1*3 /;
Parameter p(i);
Variable x(i), Util;
Positive Variable x;
Equation obj, rev(i);

obj.. Util =e= sum(i, p(i) * x(i));
rev(i).. x(i) =g= 0.01;

Model m / all /;

loop(t,
   p(i) = 1;
   solve m maximizing Util using nlp;
);
"""
        model = parse_model_text(source)
        assert model.objective is not None
        assert model.objective.objvar == "Util"
        assert model.objective.sense.name == "MAX"

    def test_solve_inside_loop_sets_model_name(self):
        """Solve inside loop sets model_name."""
        source = """
Set i / a, b /;
Set t / 1*3 /;
Parameter p(i);
Variable x(i), Util;
Positive Variable x;
Equation obj, rev(i);

obj.. Util =e= sum(i, p(i) * x(i));
rev(i).. x(i) =g= 0.01;

Model mymod / all /;

loop(t,
   solve mymod maximizing Util using nlp;
);
"""
        model = parse_model_text(source)
        assert model.model_name == "mymod"

    def test_toplevel_solve_still_works(self):
        """Top-level solve (regression test) still works."""
        source = """
Set i / a, b /;
Parameter p(i) / a 1, b 2 /;
Variable x(i), z;
Equation obj;

obj.. z =e= sum(i, p(i) * x(i));

Model m / all /;
Solve m using NLP minimizing z;
"""
        model = parse_model_text(source)
        assert model.objective is not None
        assert model.objective.objvar == "z"
        assert model.objective.sense.name == "MIN"

    def test_solve_inside_loop_multi_model(self):
        """Solve inside loop with multi-model declaration."""
        source = """
Set i / a, b /;
Set t / 1*3 /;
Parameter p(i);
Variable x(i), Util;
Positive Variable x;
Equation obj;
Equation rev(i);

obj.. Util =e= sum(i, p(i) * x(i));
rev(i).. x(i) =g= 0.01;

Model
   m1 / obj, rev /
   m2 / obj, rev /;

loop(t,
   p(i) = 1;
   solve m1 maximizing Util using nlp;
);
"""
        model = parse_model_text(source)
        assert model.objective is not None
        assert model.objective.objvar == "Util"
        assert "m1" in model.declared_models
        assert "m2" in model.declared_models
