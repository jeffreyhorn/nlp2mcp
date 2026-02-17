"""Unit tests for special values (na, inf, eps) in scalar and parameter data.

Issue #564 follow-up: Extends special value support from param_data_value
to scalar_data_item and param_data_scalar rules.

Tests cover:
- Scalar data with na, inf, -inf, eps special values
- Parameter data with special values as indexed values
- Regression: numeric scalar data still works
"""

import math

from src.ir.parser import parse_model_text


class TestScalarSpecialValues:
    """Test that Scalar declarations accept special GAMS values."""

    def test_scalar_na(self):
        """Scalar with na value parses as NaN."""
        source = """
Scalar ca 'corrosion allowance' / na /;
"""
        model = parse_model_text(source)
        assert "ca" in model.params
        assert math.isnan(model.params["ca"].values[()])

    def test_scalar_inf(self):
        """Scalar with inf value parses as infinity."""
        source = """
Scalar x / inf /;
"""
        model = parse_model_text(source)
        assert "x" in model.params
        assert model.params["x"].values[()] == float("inf")

    def test_scalar_neg_inf(self):
        """Scalar with -inf value parses as negative infinity."""
        source = """
Scalar y / -inf /;
"""
        model = parse_model_text(source)
        assert "y" in model.params
        assert model.params["y"].values[()] == float("-inf")

    def test_scalar_eps(self):
        """Scalar with eps value parses as machine epsilon."""
        source = """
Scalar e / eps /;
"""
        model = parse_model_text(source)
        assert "e" in model.params
        # eps is a very small positive value (GAMS machine epsilon)
        val = model.params["e"].values[()]
        assert val > 0
        assert val < 1e-10

    def test_scalar_number_still_works(self):
        """Regression: numeric scalar data still parses correctly."""
        source = """
Scalar m / 12 /;
"""
        model = parse_model_text(source)
        assert "m" in model.params
        assert model.params["m"].values[()] == 12.0


class TestParamDataSpecialValues:
    """Test that indexed parameter data accepts special values."""

    def test_param_data_na(self):
        """Parameter data with na value for an index."""
        source = """
Set j / a, b, c /;
Parameter d(j) / a na, b 3, c 2 /;
"""
        model = parse_model_text(source)
        assert "d" in model.params
        assert math.isnan(model.params["d"].values[("a",)])
        assert model.params["d"].values[("b",)] == 3.0
        assert model.params["d"].values[("c",)] == 2.0

    def test_param_data_inf(self):
        """Parameter data with inf value for an index."""
        source = """
Set i / x, y /;
Parameter ub(i) / x inf, y 100 /;
"""
        model = parse_model_text(source)
        assert model.params["ub"].values[("x",)] == float("inf")
        assert model.params["ub"].values[("y",)] == 100.0

    def test_param_data_number_still_works(self):
        """Regression: numeric parameter data still parses correctly."""
        source = """
Set i / a, b /;
Parameter p(i) / a 1, b 2 /;
"""
        model = parse_model_text(source)
        assert model.params["p"].values[("a",)] == 1.0
        assert model.params["p"].values[("b",)] == 2.0
