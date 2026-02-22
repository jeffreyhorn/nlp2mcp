"""Unit tests for issue #816 (mexls yes$/no$ support) and #817 (cesam2 loop/sum fixes).

Tests for:
- yes/no as boolean expression values (yes=1, no=0)
- yes$(condition) and no$(condition) conditional boolean values
- $sum(...) condition (aggregate function in dollar condition without parens)
- Wildcard (*) in set and variable domain declarations
- Loop with indexed dollar condition: loop((i,j)$FUNC(i,j), ...)
- Square bracket delimiters for sum/prod/smax/smin aggregation
"""

import pytest

from src.ir.parser import parse_model_text

pytestmark = pytest.mark.unit


class TestYesNoValues:
    """Test yes/no as boolean expression values."""

    def test_yes_value(self):
        """Plain 'yes' evaluates to 1.0."""
        source = """
        Set i / a /;
        Parameter p(i);
        p(i) = yes;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(i, p(i));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params

    def test_no_value(self):
        """Plain 'no' evaluates to 0.0."""
        source = """
        Set i / a /;
        Parameter p(i);
        p(i) = no;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(i, p(i));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params


class TestYesNoCondition:
    """Test yes$(condition) and no$(condition) expressions."""

    def test_yes_dollar_simple(self):
        """yes$(1 = 0) parses as conditional boolean."""
        source = """
        Set i / a /;
        Parameter p(i);
        p(i) = yes$(1 = 0);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(i, p(i));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params

    def test_yes_dollar_ref(self):
        """yes$km(i) parses (dollar followed by ref_indexed)."""
        source = """
        Set i / a, b /;
        Parameter km(i) / a 1, b 0 /;
        Parameter p(i);
        p(i) = yes$km(i);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(i, p(i));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params

    def test_yes_dollar_sum(self):
        """yes$sum(i, expr) parses (dollar followed by sum without wrapping parens)."""
        source = """
        Set i / a, b /;
        Set j / x /;
        Parameter q(i) / a 1, b 0 /;
        Parameter p(j);
        p(j) = yes$sum(i, q(i) > 0);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(j, p(j));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params

    def test_yes_dollar_complex_sum(self):
        """yes$(sum(mm$(not cond), expr <> 0) = 0) — nested conditions in sum."""
        source = """
        Set mm / m1, m2 /;
        Set im / i1 /;
        Set pm / p1 /;
        Parameter mmpos(mm,im) / m1.i1 1 /;
        Parameter bm(mm,pm) / m1.p1 5, m2.p1 3 /;
        Parameter p(pm,im);
        p(pm,im) = yes$(sum(mm$(not mmpos(mm,im)), bm(mm,pm) <> 0) = 0);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum((pm,im), p(pm,im));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params


class TestDollarSumCondition:
    """Test $sum(...) as a condition (aggregate function after dollar without parens)."""

    def test_lvalue_dollar_sum(self):
        """lvalue$sum(i, expr) = ... parses correctly."""
        source = """
        Set i / a, b /;
        Set j / x /;
        Parameter q(i,j) / a.x 1, b.x 0 /;
        Parameter p(j);
        p(j)$sum(i, q(i,j) <> 0) = 1;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum(j, p(j));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params


class TestWildcardDomain:
    """Test wildcard (*) in set and variable domain declarations."""

    def test_set_with_wildcard_domain(self):
        """Set xpos(i,j,*) — wildcard in set domain."""
        source = """
        Set i / a /;
        Set j / b /;
        Set xpos(i,j,*);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "xpos" in ir.sets
        assert ir.sets["xpos"].domain == ("i", "j", "*")

    def test_variable_with_wildcard_domain(self):
        """Variable x(i,j,*) — wildcard in variable domain."""
        source = """
        Set i / a /;
        Set j / b /;
        Variable x(i,j,*);
        Variables obj;
        Equations defobj;
        defobj.. obj =e= 0;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "x" in ir.variables
        assert ir.variables["x"].domain == ("i", "j", "*")


class TestLoopIndexedCondition:
    """Test loop((i,j)$FUNC(i,j), body) — indexed condition on loop domain."""

    def test_loop_paren_filtered_indexed(self):
        """loop((i,j)$NONZERO(i,j), body) with function call condition."""
        source = """
        Set i / a, b /;
        Set j / x, y /;
        Parameter NONZERO(i,j) / a.x 1, b.y 1 /;
        Parameter p(i,j);
        loop((i,j)$NONZERO(i,j),
            p(i,j) = 1;
        );
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum((i,j), p(i,j));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "p" in ir.params


class TestSquareBracketAggregation:
    """Test sum[...], prod[...], smax[...], smin[...] with square brackets."""

    def test_sum_square_brackets(self):
        """sum[i, expr] using square bracket delimiters."""
        source = """
        Set i / a, b /;
        Parameter p(i) / a 1, b 2 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= sum[i, p(i)];
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "defobj" in ir.equations

    def test_prod_square_brackets(self):
        """prod[i, expr] using square bracket delimiters."""
        source = """
        Set i / a, b /;
        Parameter p(i) / a 1, b 2 /;
        Variables obj;
        Equations defobj;
        defobj.. obj =e= prod[i, p(i)];
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "defobj" in ir.equations
