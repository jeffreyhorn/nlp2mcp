"""Unit tests for Sprint 20 Day 8 grammar extensions.

Tests for:
- Inline scalar data in Parameter blocks (/ value /)
- Parenthesized cross-product expansion in parameter data
- Multi-line parenthesized table row labels
- SOS1/SOS2 variable kind
"""

import pytest

from src.ir.parser import parse_model_text
from src.ir.symbols import VarKind

pytestmark = pytest.mark.unit


class TestInlineScalarData:
    """Test scalar parameters declared with inline / value / syntax."""

    def test_param_bare_value_integer(self):
        """Parameter with bare integer value: funds / 500 /."""
        source = """
        Parameter funds 'total funds' / 500 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= funds;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "funds" in ir.params
        assert ir.params["funds"].values.get(()) == 500.0

    def test_param_bare_value_decimal(self):
        """Parameter with bare decimal value: stderr / .05 /."""
        source = """
        Parameter stderr 'standard error' / .05 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= stderr;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "stderr" in ir.params
        assert abs(ir.params["stderr"].values.get(()) - 0.05) < 1e-10

    def test_param_bare_value_scientific(self):
        """Parameter with scientific notation value: delta / 1e-8 /."""
        source = """
        Parameter delta 'small number' / 1e-8 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= delta;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "delta" in ir.params
        assert abs(ir.params["delta"].values.get(()) - 1e-8) < 1e-20


class TestParamCrossExpansion:
    """Test (list).(list) cross-product expansion in parameter data."""

    def test_cross_product_param_data(self):
        """(a,b).(1,2) value expands to a.1=val, a.2=val, b.1=val, b.2=val."""
        source = """
        Set i / a, b /;
        Set j / '1', '2' /;
        Parameter p(i,j) / (a,b).('1','2') 10 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum((i,j), p(i,j));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        # Verify all four cross-product combinations exist with correct values
        for key in [("a", "1"), ("a", "2"), ("b", "1"), ("b", "2")]:
            assert key in ir.params["p"].values
            assert ir.params["p"].values[key] == 10.0


class TestSOSVariable:
    """Test SOS1/SOS2 variable kind parsing."""

    def test_sos2_variable_parses(self):
        """SOS2 Variable xs(i,j,s) should parse with correct kind."""
        source = """
        Set i / i1 /;
        Set j / j1 /;
        Set s / s1 /;
        SOS2 Variable xs(i,j,s);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum((i,j,s), xs(i,j,s));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "xs" in ir.variables
        assert ir.variables["xs"].kind == VarKind.SOS2

    def test_sos1_variable_parses(self):
        """SOS1 Variable w(i) should parse with correct kind."""
        source = """
        Set i / i1, i2 /;
        SOS1 Variable w(i);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(i, w(i));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "w" in ir.variables
        assert ir.variables["w"].kind == VarKind.SOS1


class TestMultilineTableRowLabel:
    """Test multi-line parenthesized table row labels."""

    def test_multiline_paren_row_label(self):
        """Table row label spanning multiple lines should be joined by preprocessor."""
        source = (
            "Set w / ground, chips /;\n"
            "Set p / 'pulp-1', 'pulp-2' /;\n"
            "Table cw(w,p) 'wood cost'\n"
            "                   'pulp-1'  'pulp-2'\n"
            "(ground,\n"
            " chips)              40      55;\n"
            "Variables obj;\n"
            "Equations defobj;\n"
            "defobj.. obj =e= sum((w,p), cw(w,p));\n"
            "Model m / all /;\n"
            "solve m minimizing obj using nlp;\n"
        )
        # parse_model_text routes through parse_text which calls
        # join_multiline_table_row_parens before grammar parsing
        ir = parse_model_text(source)
        assert "cw" in ir.params
        cw_values = ir.params["cw"].values
        assert cw_values[("ground", "pulp-1")] == 40.0
        assert cw_values[("chips", "pulp-2")] == 55.0
