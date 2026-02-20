"""Unit tests for Issue #807, #808, #809 fixes."""

from src.ad.derivative_rules import differentiate_expr
from src.ir.ast import Binary, Call, Const, VarRef
from src.ir.parser import parse_model_text, parse_text


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


class TestErrorfDerivative:
    """Test errorf derivative rule: d(errorf(u))/dx = (2/sqrt(pi)) * exp(-sqr(u)) * du/dx."""

    def test_errorf_derivative_simple(self):
        """d(errorf(x))/dx = (2/sqrt(pi)) * exp(-sqr(x)) * 1."""
        expr = Call("errorf", (VarRef("x"),))
        result = differentiate_expr(expr, "x")
        # Structure: (2/sqrt(pi)) * exp(-sqr(x)) * dx/dx
        assert isinstance(result, Binary)
        assert result.op == "*"
        # Right side is dx/dx = 1
        assert isinstance(result.right, Const)
        assert result.right.value == 1.0
        # Left side is (2/sqrt(pi)) * exp(-sqr(x))
        coeff = result.left
        assert isinstance(coeff, Binary)
        assert coeff.op == "*"
        # coeff.left = 2/sqrt(pi)
        assert isinstance(coeff.left, Binary)
        assert coeff.left.op == "/"
        # coeff.right = exp(-sqr(x))
        assert isinstance(coeff.right, Call)
        assert coeff.right.func == "exp"

    def test_errorf_derivative_chain_rule(self):
        """d(errorf(2*x))/dx applies chain rule."""
        inner = Binary("*", Const(2.0), VarRef("x"))
        expr = Call("errorf", (inner,))
        result = differentiate_expr(expr, "x")
        # Should be: (2/sqrt(pi)) * exp(-sqr(2*x)) * d(2*x)/dx
        assert isinstance(result, Binary)
        assert result.op == "*"

    def test_errorf_derivative_wrt_other_var(self):
        """d(errorf(x))/dy = 0."""
        expr = Call("errorf", (VarRef("x"),))
        result = differentiate_expr(expr, "y")
        # Inner derivative is 0, so whole thing should simplify or be 0-multiplied
        assert isinstance(result, Binary)
        assert result.op == "*"
        # The darg/dx part should be Const(0.0)
        assert isinstance(result.right, Const)
        assert result.right.value == 0.0

    def test_errorf_wrong_arity(self):
        """errorf with wrong number of args raises ValueError."""
        import pytest

        expr = Call("errorf", (VarRef("x"), VarRef("y")))
        with pytest.raises(ValueError, match="errorf.*expects 1 argument"):
            differentiate_expr(expr, "x")
