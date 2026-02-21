"""Unit tests for Issue #810: solve inside doubly-nested loop."""

import pytest

from src.ir.parser import parse_model_text, parse_text

pytestmark = pytest.mark.unit


class TestNestedLoopSolveExtraction:
    """Test solve extraction from doubly (and deeper) nested loops."""

    def test_doubly_nested_loop_solve(self):
        """solve inside loop(c, loop(i, solve ...)) should extract objective."""
        source = """
        Sets c / c1*c3 /, i / i1*i5 /;
        Variables obj, x(i);
        Equations defobj;
        defobj.. obj =e= sum(i, x(i));
        Model lmp2 / all /;

        loop(c,
           loop(i,
              solve lmp2 minimizing obj using nlp;
           );
        );
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"
        assert ir.model_name == "lmp2"

    def test_triply_nested_loop_solve(self):
        """solve inside three levels of nesting should extract objective."""
        source = """
        Sets a / a1 /, b / b1 /, c / c1 /;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;

        loop(a,
           loop(b,
              loop(c,
                 solve m minimizing obj using nlp;
              );
           );
        );
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"

    def test_single_nested_loop_solve_still_works(self):
        """Regression: single-level loop solve must still work."""
        source = """
        Sets i / i1*i5 /;
        Variables obj, x(i);
        Equations defobj;
        defobj.. obj =e= sum(i, x(i));
        Model m / all /;

        loop(i,
           solve m minimizing obj using nlp;
        );
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"

    def test_top_level_solve_still_works(self):
        """Regression: top-level solve (no loop) must still work."""
        source = """
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"

    def test_nested_loop_parses(self):
        """Doubly-nested loop with solve should parse successfully."""
        source = """
        Sets c / c1*c3 /, i / i1*i5 /;
        Variables obj, x(i);
        Equations defobj;
        defobj.. obj =e= sum(i, x(i));
        Model m / all /;

        loop(c,
           loop(i,
              solve m maximizing obj using nlp;
           );
        );
        """
        result = parse_text(source)
        assert result is not None

    def test_nested_loop_solve_maximizing(self):
        """solve ... maximizing inside nested loop should extract MAX sense."""
        source = """
        Sets c / c1 /, i / i1 /;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;

        loop(c,
           loop(i,
              solve m maximizing obj using nlp;
           );
        );
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"
        from src.ir.symbols import ObjSense

        assert ir.objective.sense == ObjSense.MAX
