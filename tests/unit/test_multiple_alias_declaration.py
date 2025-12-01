"""
Unit tests for multiple alias declarations in a single statement.

Tests the parser's ability to handle GAMS syntax like:
    Alias (i,nx), (j,ny);

Sprint 12 Day 4 - Blocker #3: multiple_alias_declaration
"""

import pytest

from src.ir.parser import ParseError, parse_model_text


def test_single_alias_pair_parentheses():
    """Test single alias pair with parentheses syntax."""
    source = """
    Set i / 1*5 /;
    Alias (i, nx);
    """
    model = parse_model_text(source)

    assert "i" in model.sets
    assert "nx" in model.aliases
    assert model.aliases["nx"].target == "i"


def test_multiple_alias_pairs():
    """Test multiple alias pairs in one statement (jbearing.gms pattern)."""
    source = """
    Set i / 1*5 /;
    Set j / 1*3 /;
    Alias (i,nx), (j,ny);
    """
    model = parse_model_text(source)

    assert "i" in model.sets
    assert "j" in model.sets
    assert "nx" in model.aliases
    assert "ny" in model.aliases
    assert model.aliases["nx"].target == "i"
    assert model.aliases["ny"].target == "j"


def test_three_alias_pairs():
    """Test three alias pairs in one statement."""
    source = """
    Set i / a, b, c /;
    Set j / 1*5 /;
    Set k / x, y /;
    Alias (i,i1), (j,j1), (k,k1);
    """
    model = parse_model_text(source)

    assert "i1" in model.aliases
    assert "j1" in model.aliases
    assert "k1" in model.aliases
    assert model.aliases["i1"].target == "i"
    assert model.aliases["j1"].target == "j"
    assert model.aliases["k1"].target == "k"


def test_multiple_alias_pairs_with_usage():
    """Test that aliases declared together can be used in equations."""
    source = """
    Set i / 1*3 /;
    Set j / 1*2 /;
    Alias (i,nx), (j,ny);

    Variable x(i,j);
    Variable z;
    Equation eq1(nx,ny);

    eq1(nx,ny).. z =e= x(nx,ny);
    """
    model = parse_model_text(source)

    assert "nx" in model.aliases
    assert "ny" in model.aliases
    assert "eq1" in model.equations
    assert model.equations["eq1"].domain == ("nx", "ny")


def test_mixed_alias_syntax():
    """Test that legacy alias syntax still works alongside new syntax."""
    source = """
    Set i / 1*5 /;
    Set j / 1*3 /;
    Set k / a, b /;

    Alias (i,nx), (j,ny);
    Alias kx, k;
    """
    model = parse_model_text(source)

    # New syntax
    assert "nx" in model.aliases
    assert "ny" in model.aliases
    assert model.aliases["nx"].target == "i"
    assert model.aliases["ny"].target == "j"

    # Legacy syntax
    assert "kx" in model.aliases
    assert model.aliases["kx"].target == "k"


def test_multiple_alias_statements():
    """Test multiple separate alias statements with multiple pairs each."""
    source = """
    Set i / 1*3 /;
    Set j / 1*2 /;
    Set k / a, b /;
    Set m / x, y, z /;

    Alias (i,i1), (j,j1);
    Alias (k,k1), (m,m1);
    """
    model = parse_model_text(source)

    assert len(model.aliases) == 4
    assert model.aliases["i1"].target == "i"
    assert model.aliases["j1"].target == "j"
    assert model.aliases["k1"].target == "k"
    assert model.aliases["m1"].target == "m"


def test_alias_with_quoted_names():
    """Test aliases with quoted names (GAMS escaped identifiers)."""
    source = """
    Set i / a, b, c /;
    Alias (i, 'i-alias');
    """
    model = parse_model_text(source)

    assert "i" in model.sets
    # Quoted identifiers are stored with quotes
    assert "'i-alias'" in model.aliases
    assert model.aliases["'i-alias'"].target == "i"


def test_multiple_aliases_of_same_set():
    """Test multiple aliases pointing to the same target set."""
    source = """
    Set i / 1*5 /;
    Set j / a, b /;
    Alias (i,i1), (i,i2), (j,j1);
    """
    model = parse_model_text(source)

    assert model.aliases["i1"].target == "i"
    assert model.aliases["i2"].target == "i"
    assert model.aliases["j1"].target == "j"


def test_jbearing_exact_pattern():
    """Test the exact alias pattern from jbearing.gms."""
    source = """
    Set i 'set i' / 0*5 /;
    Set j 'set j' / 0*5 /;

    Alias (i,nx), (j,ny);

    Variable x(i,j);
    Equation eq(nx,ny);
    eq(nx,ny).. x(nx,ny) =e= 0;
    """
    model = parse_model_text(source)

    assert "i" in model.sets
    assert "j" in model.sets
    assert "nx" in model.aliases
    assert "ny" in model.aliases
    assert model.aliases["nx"].target == "i"
    assert model.aliases["ny"].target == "j"
    assert "eq" in model.equations
    assert model.equations["eq"].domain == ("nx", "ny")


def test_alias_chain_with_multiple_declaration():
    """Test that alias chains work with multiple declarations."""
    source = """
    Set i / 1*3 /;
    Alias (i,i1), (i1,i2);
    """
    model = parse_model_text(source)

    assert model.aliases["i1"].target == "i"
    assert model.aliases["i2"].target == "i1"


def test_malformed_alias_pair_single_id():
    """Test that alias pair with only one ID raises parse error."""
    source = """
    Set i / 1*5 /;
    Alias (i);
    """
    # Grammar should reject this - alias_pair requires exactly 2 IDs
    with pytest.raises(ParseError):
        parse_model_text(source)


def test_malformed_alias_pair_three_ids():
    """Test that alias pair with three IDs raises parse error."""
    source = """
    Set i / 1*5 /;
    Set j / 1*3 /;
    Alias (i,j,k);
    """
    # Grammar should reject this - alias_pair requires exactly 2 IDs
    with pytest.raises(ParseError):
        parse_model_text(source)
