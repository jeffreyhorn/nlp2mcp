"""Unit tests for Issue #807, #808, #809 fixes."""

import pytest

from src.ir.parser import parse_model_text, parse_text

pytestmark = pytest.mark.unit


class TestIssue807McpSolveWithoutObjective:
    """Test MCP/CNS solve statements without objective function."""

    def test_solve_mcp_without_objective(self):
        """solve m using mcp; should parse without objective."""
        source = """
        Equations eq1;
        Variables x;
        eq1.. x =e= 0;
        Model m / eq1.x /;
        solve m using mcp;
        """
        result = parse_text(source)
        assert result is not None

    def test_solve_mcp_without_objective_ir(self):
        """IR should have no objective for MCP solve without one."""
        source = """
        Equations eq1;
        Variables x;
        eq1.. x =e= 0;
        Model m / eq1.x /;
        solve m using mcp;
        """
        ir = parse_model_text(source)
        assert ir.model_name == "m"
        assert ir.objective is None

    def test_solve_cns_without_objective(self):
        """solve m using cns; should parse without objective."""
        source = """
        Equations eq1;
        Variables x;
        eq1.. x =e= 0;
        Model m / eq1.x /;
        solve m using cns;
        """
        result = parse_text(source)
        assert result is not None

    def test_solve_with_objective_still_works(self):
        """Existing solve with objective must still work."""
        source = """
        Variables x, obj;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m using nlp minimizing obj;
        """
        ir = parse_model_text(source)
        assert ir.objective is not None
        assert ir.objective.objvar == "obj"


class TestIssue808LoopTupleDollarCondition:
    """Test loop with tuple domain and bare dollar condition."""

    def test_loop_tuple_bare_dollar(self):
        """loop((i,j)$flag, ...) should parse with bare ID condition."""
        source = """
        Sets i, j;
        Scalar flag / 1 /;
        Parameter c(i,j);
        loop((i,j)$flag,
           c(i,j) = 0;
        );
        """
        result = parse_text(source)
        assert result is not None

    def test_loop_single_bare_dollar(self):
        """loop(i$flag, ...) should parse with bare ID condition."""
        source = """
        Sets i;
        Scalar flag / 1 /;
        Parameter c(i);
        loop(i$flag,
           c(i) = 0;
        );
        """
        result = parse_text(source)
        assert result is not None

    def test_loop_tuple_paren_dollar_still_works(self):
        """loop((i,j)$(expr), ...) must still work."""
        source = """
        Sets i, j;
        Scalar flag / 1 /;
        Parameter c(i,j);
        loop((i,j)$(flag > 0),
           c(i,j) = 0;
        );
        """
        result = parse_text(source)
        assert result is not None


class TestIssue809ErrorfFunction:
    """Test errorf function recognition in expressions."""

    def test_errorf_simple(self):
        """errorf(x) should parse as a function call."""
        source = """
        Variables x, y;
        Equations eq;
        eq.. y =e= errorf(x);
        """
        result = parse_text(source)
        assert result is not None

    def test_errorf_negative_arg(self):
        """errorf(-x) should parse with unary minus in argument."""
        source = """
        Variables x, y;
        Equations eq;
        eq.. y =e= errorf(-x);
        """
        result = parse_text(source)
        assert result is not None

    def test_errorf_in_complex_expression(self):
        """errorf in binary minus context: a*errorf(-b) - c*errorf(-d)."""
        source = """
        Variables x, y, z, w;
        Equations eq;
        eq.. x =e= y*errorf(-z) - y*errorf(-w);
        """
        result = parse_text(source)
        assert result is not None
