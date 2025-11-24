"""Integration tests for function calls in parameter assignments.

Sprint 10 Day 5: Test function call patterns from circle.gms and other real models.
These tests verify that function calls are properly detected, stored as expressions,
and work in realistic scenarios.
"""

from src.ir.ast import Call
from src.ir.parser import parse_model_file


class TestMathematicalFunctions:
    """Test mathematical functions (sqrt, sqr, exp, log, etc.) in parameter assignments."""

    def test_sqrt_sqr_pythagorean(self, tmp_path):
        """Test sqrt/sqr pattern from circle.gms line 48.

        Pattern: r.l = sqrt(sqr(a.l - xmin) + sqr(b.l - ymin));

        Simplified version without variable attributes for Day 5.
        """
        test_file = tmp_path / "test_pythagorean.gms"
        test_file.write_text(
            """
Parameter a, b, xmin, ymin, r;
a = 3;
b = 4;
xmin = 1;
ymin = 2;
r = sqrt(sqr(a - xmin) + sqr(b - ymin));
"""
        )
        model = parse_model_file(test_file)

        # Simple parameters should have values
        assert model.params["a"].values[()] == 3
        assert model.params["b"].values[()] == 4
        assert model.params["xmin"].values[()] == 1
        assert model.params["ymin"].values[()] == 2

        # r should have function call expression
        assert "r" in model.params
        param = model.params["r"]

        assert () in param.expressions
        assert () not in param.values

        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "sqrt"
        # The argument is a Binary expression (sqr(...) + sqr(...))
        assert len(expr.args) == 1

    def test_nested_mathematical_functions(self, tmp_path):
        """Test nested mathematical function calls."""
        test_file = tmp_path / "test_nested_math.gms"
        test_file.write_text(
            """
Parameter x, result;
x = 2;
result = log(exp(sqrt(x)));
"""
        )
        model = parse_model_file(test_file)

        assert "result" in model.params
        param = model.params["result"]

        assert () in param.expressions
        expr = param.expressions[()]

        # Top-level function should be log
        assert isinstance(expr, Call)
        assert expr.func == "log"
        assert len(expr.args) == 1

    def test_power_function(self, tmp_path):
        """Test power function in parameter assignment."""
        test_file = tmp_path / "test_power.gms"
        test_file.write_text(
            """
Parameter base, exponent, result;
base = 2;
exponent = 3;
result = power(base, exponent);
"""
        )
        model = parse_model_file(test_file)

        assert "result" in model.params
        param = model.params["result"]

        assert () in param.expressions
        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "power"
        assert len(expr.args) == 2


class TestMixedAssignments:
    """Test mixed scenarios with both simple values and function calls."""

    def test_mixed_simple_and_function_calls(self, tmp_path):
        """Test that simple assignments and function calls coexist properly."""
        test_file = tmp_path / "test_mixed.gms"
        test_file.write_text(
            """
Parameter a, b, c, d;
a = 10;
b = 20;
c = sqrt(a);
d = log(b);
"""
        )
        model = parse_model_file(test_file)

        # Simple assignments should be in values
        assert model.params["a"].values[()] == 10
        assert model.params["b"].values[()] == 20
        assert () not in model.params["a"].expressions
        assert () not in model.params["b"].expressions

        # Function calls should be in expressions
        assert () in model.params["c"].expressions
        assert () not in model.params["c"].values
        assert model.params["c"].expressions[()].func == "sqrt"

        assert () in model.params["d"].expressions
        assert () not in model.params["d"].values
        assert model.params["d"].expressions[()].func == "log"

    def test_function_call_with_simple_expression(self, tmp_path):
        """Test function calls mixed with arithmetic expressions."""
        test_file = tmp_path / "test_mixed_expr.gms"
        test_file.write_text(
            """
Parameter a, b, c;
a = 5;
b = 3;
c = sqrt(a + b);
"""
        )
        model = parse_model_file(test_file)

        assert "c" in model.params
        param = model.params["c"]

        assert () in param.expressions
        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "sqrt"
        # Argument is a binary expression (a + b)
        assert len(expr.args) == 1


class TestRoundModCeilFunctions:
    """Test the newly added functions from Day 4 (round, mod, ceil)."""

    def test_round_function(self, tmp_path):
        """Test round function in parameter assignment."""
        test_file = tmp_path / "test_round.gms"
        test_file.write_text(
            """
Parameter x, rounded;
x = 3.7;
rounded = round(x);
"""
        )
        model = parse_model_file(test_file)

        assert "rounded" in model.params
        param = model.params["rounded"]

        assert () in param.expressions
        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "round"

    def test_mod_function(self, tmp_path):
        """Test mod function in parameter assignment."""
        test_file = tmp_path / "test_mod.gms"
        test_file.write_text(
            """
Parameter a, b, remainder;
a = 10;
b = 3;
remainder = mod(a, b);
"""
        )
        model = parse_model_file(test_file)

        assert "remainder" in model.params
        param = model.params["remainder"]

        assert () in param.expressions
        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "mod"
        assert len(expr.args) == 2

    def test_ceil_function(self, tmp_path):
        """Test ceil function in parameter assignment."""
        test_file = tmp_path / "test_ceil.gms"
        test_file.write_text(
            """
Parameter x, ceiling;
x = 3.2;
ceiling = ceil(x);
"""
        )
        model = parse_model_file(test_file)

        assert "ceiling" in model.params
        param = model.params["ceiling"]

        assert () in param.expressions
        expr = param.expressions[()]
        assert isinstance(expr, Call)
        assert expr.func == "ceil"


class TestBackwardCompatibility:
    """Test that existing functionality still works correctly."""

    def test_simple_scalar_assignments_unchanged(self, tmp_path):
        """Verify simple scalar assignments continue to work as before."""
        test_file = tmp_path / "test_backward_compat.gms"
        test_file.write_text(
            """
Scalar a /10/, b /20/;
Parameter c, d;
c = 30;
d = 40;
"""
        )
        model = parse_model_file(test_file)

        # All should be simple value assignments
        assert model.params["a"].values[()] == 10
        assert model.params["b"].values[()] == 20
        assert model.params["c"].values[()] == 30
        assert model.params["d"].values[()] == 40

        # None should have expressions
        for param_name in ["a", "b", "c", "d"]:
            assert () not in model.params[param_name].expressions

    def test_indexed_parameter_simple_values(self, tmp_path):
        """Verify indexed parameters with simple values work correctly."""
        test_file = tmp_path / "test_indexed_simple.gms"
        test_file.write_text(
            """
Set i / i1*i3 /;
Parameter x(i);
x('i1') = 10;
x('i2') = 20;
x('i3') = 30;
"""
        )
        model = parse_model_file(test_file)

        param = model.params["x"]
        assert ("i1",) in param.values
        assert ("i2",) in param.values
        assert ("i3",) in param.values
        assert param.values[("i1",)] == 10
        assert param.values[("i2",)] == 20
        assert param.values[("i3",)] == 30

        # No expressions should be stored
        assert len(param.expressions) == 0
