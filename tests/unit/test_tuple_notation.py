"""Tests for tuple notation in set declarations (Issue #356).

GAMS supports two tuple notations:
1. Basic tuples: a.b → (a, b)
2. Tuple expansion: a.(b,c,d) → (a,b), (a,c), (a,d)
"""

import pytest

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
