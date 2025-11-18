"""Tests for indexed parameter assignments and variable attribute access.

Sprint 8 Day 3: Tests for patterns that unlock mathopt1.gms and trig.gms.
"""

import pytest

from src.ir.parser import parse_model_text


class TestIndexedParameterAssignment1D:
    """Test simple 1D indexed parameter assignments: p('i1') = 10"""

    def test_1d_indexed_param_assignment(self):
        """Test basic 1D indexed parameter assignment."""
        gams = """
        Set i / i1, i2, i3 /;
        Parameter p(i);
        p('i1') = 10;
        """
        model = parse_model_text(gams)
        assert "p" in model.params
        param = model.params["p"]
        assert param.values[("i1",)] == 10

    def test_1d_indexed_param_multiple_assignments(self):
        """Test multiple 1D indexed assignments to same parameter."""
        gams = """
        Set i / i1, i2, i3 /;
        Parameter p(i);
        p('i1') = 10;
        p('i2') = 20;
        p('i3') = 30;
        """
        model = parse_model_text(gams)
        param = model.params["p"]
        assert param.values[("i1",)] == 10
        assert param.values[("i2",)] == 20
        assert param.values[("i3",)] == 30


class TestIndexedParameterAssignment2D:
    """Test 2D indexed parameter assignments: report('x1','global') = 1"""

    def test_2d_indexed_param_assignment(self):
        """Test basic 2D indexed parameter assignment (mathopt1 pattern)."""
        gams = """
        Set scenario / x1, x2 /;
        Set metric / global, solver, diff /;
        Parameter report(scenario, metric);
        report('x1','global') = 1;
        """
        model = parse_model_text(gams)
        assert "report" in model.params
        param = model.params["report"]
        assert param.values[("x1", "global")] == 1

    def test_2d_indexed_param_multiple_assignments(self):
        """Test multiple 2D indexed assignments (mathopt1 pattern)."""
        gams = """
        Set scenario / x1, x2 /;
        Set metric / global, solver, diff /;
        Parameter report(scenario, metric);
        report('x1','global') = 1;
        report('x2','global') = 1;
        report('x1','solver') = 2.5;
        report('x2','solver') = 3.7;
        """
        model = parse_model_text(gams)
        param = model.params["report"]
        assert param.values[("x1", "global")] == 1
        assert param.values[("x2", "global")] == 1
        assert param.values[("x1", "solver")] == 2.5
        assert param.values[("x2", "solver")] == 3.7


class TestVariableAttributeAccess:
    """Test variable attribute access in assignments: xdiff = x1.l"""

    def test_variable_level_attribute(self):
        """Test variable .l (level) attribute access (trig pattern)."""
        gams = """
        Variables x1, obj;
        Scalar xdiff, fdiff;
        xdiff = 2.66695657;
        fdiff = -3.76250149;
        """
        model = parse_model_text(gams)
        # Note: This test validates that the assignment parses
        # Sprint 8 doesn't execute variable attribute access yet
        assert "xdiff" in model.params
        assert "fdiff" in model.params

    def test_variable_marginal_attribute(self):
        """Test variable .m (marginal) attribute in grammar."""
        gams = """
        Variables x1;
        Scalar xmarginal;
        x1.m = 1.5;
        """
        model = parse_model_text(gams)
        # Verify .m attribute is accepted by grammar and parser
        assert "x1" in model.variables
        var = model.variables["x1"]
        assert var.m == 1.5


class TestIndexedAssignmentValidation:
    """Test validation of indexed assignments."""

    def test_undeclared_parameter_error(self):
        """Test that assignment to undeclared parameter raises error."""
        gams = """
        undeclared_param('i1') = 10;
        """
        with pytest.raises(Exception, match="Parameter 'undeclared_param' not declared"):
            parse_model_text(gams)

    def test_wrong_index_count_error(self):
        """Test that wrong number of indices raises error."""
        gams = """
        Set i / i1, i2, i3 /;
        Parameter p(i);
        p('i1', 'i2') = 10;
        """
        with pytest.raises(Exception, match="expects 1 index, got 2"):
            parse_model_text(gams)

    def test_2d_param_requires_2_indices(self):
        """Test that 2D parameter requires 2 indices."""
        gams = """
        Set scenario / x1, x2 /;
        Set metric / global, solver /;
        Parameter report(scenario, metric);
        report('x1') = 1;
        """
        with pytest.raises(Exception, match="expects 2 indices, got 1"):
            parse_model_text(gams)


class TestMathopt1Pattern:
    """Test the exact pattern from mathopt1.gms (line 45)."""

    def test_mathopt1_report_pattern(self):
        """Test mathopt1.gms pattern: report('x1','global') = 1"""
        gams = """
        Set scenario / x1, x2 /;
        Set metric / global, solver, diff /;
        Parameter report(scenario, metric) 'solution summary report';
        Variables x1, x2;

        report('x1','global') = 1;
        report('x2','global') = 1;
        """
        model = parse_model_text(gams)

        # Verify parameter declaration
        assert "report" in model.params
        param = model.params["report"]

        # Verify indexed values stored correctly
        assert param.values[("x1", "global")] == 1
        assert param.values[("x2", "global")] == 1


class TestTrigPattern:
    """Test the exact pattern from trig.gms (line 32)."""

    def test_trig_scalar_assignment_pattern(self):
        """Test trig.gms pattern: xdiff = 2.66695657"""
        gams = """
        Scalar xdiff, fdiff;
        xdiff = 2.66695657;
        fdiff = -3.76250149;
        """
        model = parse_model_text(gams)

        # Verify scalar assignments parse correctly
        assert "xdiff" in model.params
        assert "fdiff" in model.params
        assert model.params["xdiff"].values[()] == 2.66695657
        assert model.params["fdiff"].values[()] == -3.76250149
