"""Unit tests for Sprint 20 Day 8 grammar extensions.

Tests for:
- Inline scalar data in Parameter blocks (/ value /)
- Parenthesized cross-product expansion in parameter data
- Multi-line parenthesized table row labels
- SOS2 variable kind
"""

import pytest

from src.ir.parser import parse_model_text

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
        assert ("a", "1") in ir.params["p"].values
        assert ("b", "2") in ir.params["p"].values
        assert ir.params["p"].values[("a", "1")] == 10.0


class TestSOS2Variable:
    """Test SOS2 variable kind parsing."""

    def test_sos2_variable_parses(self):
        """SOS2 Variable xs(i,j,s) should parse."""
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


class TestMultilineTableRowLabel:
    """Test multi-line parenthesized table row labels."""

    def test_multiline_paren_row_label(self):
        """Table row label (ground chips) spanning lines should parse."""
        source = """
        Set w / ground, chips /;
        Set p / 'pulp-1', 'pulp-2' /;
        Table cw(w,p) 'wood cost'
                       'pulp-1'  'pulp-2'
        (ground, chips)    40      55;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum((w,p), cw(w,p));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "cw" in ir.params
