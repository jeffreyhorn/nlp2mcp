"""Unit tests for Subcategory A compound set data grammar extensions.

Sprint 20 Day 7: Tests for multi-word set elements, numeric-prefix tuples,
and deep dotted table row labels with parenthesized sub-lists.
"""

import pytest

from src.ir.parser import parse_model_text, parse_text

pytestmark = pytest.mark.unit


class TestMultiWordSetElements:
    """Test multi-word set elements (e.g. 'wire rod')."""

    def test_multiword_element_with_desc(self):
        """Two bare words followed by a quoted description -> single element."""
        source = """
        Set p / plate 'plate production',
               wire rod 'rolling of wire rod',
               tinning 'tin production' /;
        Variables obj, x(p);
        Equations defobj;
        defobj.. obj =e= sum(p, x(p));
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "wire rod" in ir.sets["p"].members

    def test_multiword_element_parses(self):
        """Multi-word element should parse without error."""
        source = """
        Set i / wire rod 'description' /;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "wire rod" in ir.sets["i"].members


class TestNumericPrefixTuples:
    """Test numeric-prefix tuples in set data (e.g. 1.sicartsa)."""

    def test_number_dot_id_tuple(self):
        """Numeric prefix like 1.sicartsa should parse as tuple."""
        source = """
        Set o / 1*3 /;
        Set is / sicartsa, ahmsa, fundidora /;
        Set own(o,is) / 1.sicartsa, 2.ahmsa, 3.fundidora /;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "1.sicartsa" in ir.sets["own"].members

    def test_number_dot_paren_expansion(self):
        """Numeric prefix with parenthesized expansion like 4.(a,b)."""
        source = """
        Set o / 1*5 /;
        Set is / hylsa, hylsap, tamsa /;
        Set own(o,is) / 4.(hylsa,hylsap), 5.tamsa /;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        ir = parse_model_text(source)
        assert "4.hylsa" in ir.sets["own"].members
        assert "4.hylsap" in ir.sets["own"].members
        assert "5.tamsa" in ir.sets["own"].members


class TestDottedLabelParenthesizedSubList:
    """Test deep dotted table row labels with parenthesized sub-lists."""

    def test_dotted_label_with_paren_suffix(self):
        """Table row like wheat.bullock.standard.(heavy,january) should parse."""
        source = """
        Sets c / wheat /, t / bullock /, s / standard /,
             w / heavy, january /;
        Table landcw(c,t,s,w) 'land requirements'
                              heavy  january
        wheat.bullock.standard.(heavy,january)  1  1 ;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        tree = parse_text(source)
        assert tree is not None

    def test_two_level_dotted_paren(self):
        """Table row like crop.activity.(sch-1,sch-2) should parse."""
        source = """
        Sets c / alfalfa /, a / spray /,
             s / 'sch-1', 'sch-2' /;
        Table labor(c,a,s) 'labor requirements'
                           'sch-1'  'sch-2'
        alfalfa.spray.('sch-1','sch-2')  1  1 ;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        tree = parse_text(source)
        assert tree is not None

    def test_single_element_dot_paren_still_works(self):
        """Regression: single elem.(a,b) table row label still works."""
        source = """
        Sets c / sorghum /, t / bullock, 'semi-mech' /;
        Table req(c,t) 'requirements'
                       bullock  'semi-mech'
        sorghum.(bullock,'semi-mech')  1  1 ;
        Variables obj, x;
        Equations defobj;
        defobj.. obj =e= x;
        Model m / all /;
        solve m minimizing obj using nlp;
        """
        tree = parse_text(source)
        assert tree is not None
