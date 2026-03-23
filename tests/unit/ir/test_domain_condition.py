"""Tests for domain condition extraction from nested equation domains.

Issue #1112: When an equation is defined with a restricted domain like
`eq(low(n,nn))..`, the parser should extract `low(n,nn)` as a condition
on the equation, rather than discarding the set restriction.
"""

from __future__ import annotations

import pytest

from src.ir.parser import parse_model_text


@pytest.mark.unit
class TestDomainConditionExtraction:
    """Test that nested domain elements generate equation conditions."""

    def test_nested_domain_creates_condition(self):
        """eq(low(n,nn)).. creates condition ParamRef('low', ('n', 'nn'))."""
        gams = """
Set n / a, b, c /;
Set low(n,n);
Alias(n, nn);
low(n,nn) = ord(n) > ord(nn);
Variable x;
Equation eq1(n,nn);
eq1(low(n,nn)).. x =e= 0;
Solve dummy using NLP minimizing x;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.domain == ("n", "nn")
        assert eq.condition is not None
        assert repr(eq.condition) == "ParamRef(low(n,nn))"

    def test_simple_domain_no_condition(self):
        """eq(i,j).. does NOT create a condition."""
        gams = """
Set i / a, b /;
Set j / x, y /;
Variable z;
Equation eq1(i,j);
eq1(i,j).. z =e= 0;
Solve dummy using NLP minimizing z;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.domain == ("i", "j")
        assert eq.condition is None

    def test_nested_domain_with_explicit_condition(self):
        """eq(low(n,nn))$active(n).. combines both conditions."""
        gams = """
Set n / a, b, c /;
Set low(n,n);
Set active(n) / a, b /;
Alias(n, nn);
low(n,nn) = ord(n) > ord(nn);
Parameter p(n);
Variable x;
Equation eq1(n,nn);
eq1(low(n,nn))$(active(n)).. x =e= 0;
Solve dummy using NLP minimizing x;
"""
        ir = parse_model_text(gams)
        eq = ir.equations.get("eq1")
        assert eq is not None
        assert eq.condition is not None
        # Should be Binary("and", ParamRef("low",...), ...)
        assert "low" in repr(eq.condition)
        assert "active" in repr(eq.condition)
