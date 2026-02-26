"""Tests for Sprint 21 Day 5: senstran (if-stmt condition) and turkpow (dotted index).

Fixes:
- senstran: bare identifier / ref_indexed / funccall as if-stmt condition
- turkpow: dotted index in parameter data (e.g., hydro-4.1978 250)
"""

from src.ir.parser import parse_model_text


class TestBareIdentifierIfCondition:
    """Test bare identifier as if-statement condition (senstran pattern)."""

    def test_scalar_param_as_if_condition(self):
        """Test if(pors, ...) where pors is a scalar parameter."""
        gams = """\
Set i / a, b /;
Scalar pors / 1 /;
Parameter x(i);
x(i) = 0;
if(pors,
  x('a') = 10;
);
"""
        model = parse_model_text(gams)
        assert len(model.conditional_statements) >= 1

    def test_elseif_with_bare_identifier(self):
        """Test elseif with bare identifier condition."""
        gams = """\
Scalar flag1 / 0 /;
Scalar flag2 / 1 /;
Scalar result / 0 /;
if(flag1,
  result = 1;
elseif flag2,
  result = 2;
);
"""
        model = parse_model_text(gams)
        assert len(model.conditional_statements) >= 1


class TestFunccallIfCondition:
    """Test function call as if-statement condition."""

    def test_abs_as_if_condition(self):
        """Test if(abs(x), ...) — function call condition."""
        gams = """\
Scalar x / -5 /;
Scalar result / 0 /;
if(abs(x),
  result = 1;
);
"""
        model = parse_model_text(gams)
        assert len(model.conditional_statements) >= 1


class TestDottedIndexParameterData:
    """Test dotted index notation in parameter data (turkpow pattern)."""

    def test_dotted_index_two_dim(self):
        """Test hydro-4.1978 250 for Parameter p(m,te)."""
        gams = """\
Set m / 'hydro-1', 'hydro-2', 'hydro-3', 'hydro-4' /;
Set te / 1978, 1979, 1980 /;
Parameter hlo(m,te) /
  'hydro-4'.1978  250
  'hydro-4'.1979  300
  'hydro-1'.1980  100
/;
"""
        model = parse_model_text(gams)
        param = model.params["hlo"]
        assert ("hydro-4", "1978") in param.values
        assert param.values[("hydro-4", "1978")] == 250.0
        assert param.values[("hydro-4", "1979")] == 300.0
        assert param.values[("hydro-1", "1980")] == 100.0

    def test_dotted_index_with_numeric_index(self):
        """Test dotted index where second element is numeric year."""
        gams = """\
Set plant / 'plant-1', 'plant-2' /;
Set yr / 2000, 2001, 2002 /;
Parameter cap(plant,yr) /
  'plant-1'.2000  100
  'plant-1'.2001  150
  'plant-2'.2002  200
/;
"""
        model = parse_model_text(gams)
        param = model.params["cap"]
        assert param.values[("plant-1", "2000")] == 100.0
        assert param.values[("plant-1", "2001")] == 150.0
        assert param.values[("plant-2", "2002")] == 200.0
