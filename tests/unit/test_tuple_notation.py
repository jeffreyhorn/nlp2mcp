"""Tests for tuple notation in set declarations (Issue #356).

GAMS supports two tuple notations:
1. Basic tuples: a.b → (a, b)
2. Tuple expansion: a.(b,c,d) → (a,b), (a,c), (a,d)
"""

from src.ir.parser import parse_model_text


def test_basic_tuple():
    """Test basic tuple notation: a.b"""
    source = """
    Set n / a, b, c /;
    Set pairs(n,n) / a.b, b.c /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["a.b", "b.c"]


def test_basic_tuple_with_description():
    """Test tuple with description: a.b "description" """
    source = """
    Set n / a, b /;
    Set pairs(n,n) / a.b "edge from a to b" /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["a.b"]


def test_tuple_expansion_simple():
    """Test simple tuple expansion: nw.(w,cc)"""
    source = """
    Set n / nw, w, cc /;
    Set pairs(n,n) / nw.(w,cc) /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["nw.w", "nw.cc"]


def test_tuple_expansion_single_element():
    """Test tuple expansion with single element: a.(b)"""
    source = """
    Set n / a, b /;
    Set pairs(n,n) / a.(b) /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["a.b"]


def test_tuple_expansion_many_elements():
    """Test tuple expansion with many elements"""
    source = """
    Set n / nw, w, cc, x, y /;
    Set pairs(n,n) / nw.(w,cc,x,y) /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["nw.w", "nw.cc", "nw.x", "nw.y"]


def test_multiple_tuple_expansions():
    """Test multiple tuple expansions: nw.(w,cc), e.(n,s)"""
    source = """
    Set n / nw, e, w, cc, s /;
    Set pairs(n,n) / nw.(w,cc), e.(n,s) /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["nw.w", "nw.cc", "e.n", "e.s"]


def test_mixed_tuple_notation():
    """Test expansion mixed with basic tuples"""
    source = """
    Set n / nw, e, w, cc, s, se, sw /;
    Set pairs(n,n) / nw.(w,cc), s.se, s.sw /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["nw.w", "nw.cc", "s.se", "s.sw"]


def test_water_exact_pattern():
    """Test exact pattern from water.gms line 26"""
    source = """
    Set n / nw, e, cc, w, sw, s, se /;
    Set a(n,n) / nw.(w,cc,n), e.(n,cc,s,se), cc.(w,sw,s,n), s.se, s.sw, sw.w /;
    """
    model = parse_model_text(source)
    assert "a" in model.sets

    expected = [
        # nw.(w,cc,n) expands to:
        "nw.w",
        "nw.cc",
        "nw.n",
        # e.(n,cc,s,se) expands to:
        "e.n",
        "e.cc",
        "e.s",
        "e.se",
        # cc.(w,sw,s,n) expands to:
        "cc.w",
        "cc.sw",
        "cc.s",
        "cc.n",
        # Basic tuples:
        "s.se",
        "s.sw",
        "sw.w",
    ]

    assert model.sets["a"].members == expected
    assert len(model.sets["a"].members) == 14


def test_tuple_with_regular_elements():
    """Test tuples mixed with regular single elements"""
    source = """
    Set n / a, b, c, d /;
    Set pairs(n,n) / a.b, c, d /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    # Note: 'c' and 'd' are single elements (1D), not tuples (2D)
    # This may cause validation errors but should parse
    assert model.sets["pairs"].members == ["a.b", "c", "d"]


def test_tuple_expansion_no_descriptions():
    """Test expansion - descriptions after expansion not supported in grammar"""
    source = """
    Set n / nw, e, w, cc /;
    Set pairs(n,n) / nw.(w,cc), e.cc /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["nw.w", "nw.cc", "e.cc"]


# Issue #612: Tests for tuple prefix expansion (a,b).c syntax
def test_tuple_prefix_expansion_simple():
    """Test prefix tuple expansion: (jan,feb).wet"""
    source = """
    Set tw / (jan,feb).wet, (mar,apr).dry /;
    """
    model = parse_model_text(source)
    assert "tw" in model.sets
    assert model.sets["tw"].members == ["jan.wet", "feb.wet", "mar.dry", "apr.dry"]


def test_tuple_prefix_expansion_multiline():
    """Test tuple prefix expansion across multiple lines (Issue #612).

    GAMS allows omitting commas between set members when they're on separate lines.
    This test verifies that the parser handles this correctly for prefix tuple expansion.
    """
    source = """
    Set tw / (jan,feb).wet
             (mar,apr).dry /;
    """
    model = parse_model_text(source)
    assert "tw" in model.sets
    expected_members = ["jan.wet", "feb.wet", "mar.dry", "apr.dry"]
    assert model.sets["tw"].members == expected_members


def test_tuple_prefix_expansion_clearlak_pattern():
    """Test exact pattern from clearlak.gms lines 42-43.

    tw(t,w)  'relates months to weather conditions' /(jan,feb).wet
                                                    (mar,apr).dry  /
    """
    source = """
    Set t / jan, feb, mar, apr /;
    Set w / wet, dry /;
    Set tw(t,w) 'relates months to weather conditions' / (jan,feb).wet
                                                         (mar,apr).dry /;
    """
    model = parse_model_text(source)
    assert "tw" in model.sets
    expected_members = ["jan.wet", "feb.wet", "mar.dry", "apr.dry"]
    assert model.sets["tw"].members == expected_members


def test_mixed_prefix_and_suffix_expansion():
    """Test mixing prefix (a,b).c and suffix a.(b,c) expansion in same set."""
    source = """
    Set pairs / (a,b).x, y.(c,d) /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    # (a,b).x expands to a.x, b.x
    # y.(c,d) expands to y.c, y.d
    assert model.sets["pairs"].members == ["a.x", "b.x", "y.c", "y.d"]


def test_tuple_prefix_expansion_single_element():
    """Test prefix expansion with single element: (a).b"""
    source = """
    Set pairs / (a).b /;
    """
    model = parse_model_text(source)
    assert "pairs" in model.sets
    assert model.sets["pairs"].members == ["a.b"]
