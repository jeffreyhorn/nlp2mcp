"""
Unit tests for $set directive preprocessing.

Tests support for GAMS $set directives and %variable% substitution.
"""

from src.ir.preprocessor import expand_macros, extract_set_directives, strip_set_directives


def test_extract_simple_set():
    """Test extracting a simple $set directive."""
    source = "$set n 10"
    macros = extract_set_directives(source)
    assert macros == {"n": "10"}


def test_extract_multiple_sets():
    """Test extracting multiple $set directives."""
    source = """
    $set n 10
    $set m 20
    $set path "c:\\data"
    """
    macros = extract_set_directives(source)
    assert macros == {"n": "10", "m": "20", "path": "c:\\data"}


def test_extract_set_with_quoted_value():
    """Test $set with quoted string value."""
    source = '$set path "c:\\data\\models"'
    macros = extract_set_directives(source)
    assert macros == {"path": "c:\\data\\models"}


def test_extract_set_case_insensitive():
    """Test that $SET, $set, $Set all work."""
    source = """
    $SET n 10
    $set m 20
    $Set p 30
    """
    macros = extract_set_directives(source)
    assert macros == {"n": "10", "m": "20", "p": "30"}


def test_extract_set_overrides():
    """Test that later $set overrides earlier ones."""
    source = """
    $set n 10
    $set n 20
    """
    macros = extract_set_directives(source)
    assert macros == {"n": "20"}


def test_extract_set_with_macro_reference():
    """Test $set value containing %macro% reference."""
    source = "$set np %n%+1"
    macros = extract_set_directives(source, {"n": "10"})
    assert macros == {"np": "10+1"}


def test_extract_set_nested_macros():
    """Test nested macro expansion in $set values."""
    source = """
    $set a 5
    $set b %a%*2
    $set c %b%+1
    """
    macros = extract_set_directives(source)
    assert macros == {"a": "5", "b": "5*2", "c": "5*2+1"}


def test_extract_set_in_conditional():
    """Test extracting $set from $if line."""
    source = "$if set n $set np %n%"
    macros = extract_set_directives(source, {"n": "10"})
    assert macros == {"np": "10"}


def test_expand_simple_macro():
    """Test expanding a simple %variable% reference."""
    source = "Set i /1*%n%/;"
    result = expand_macros(source, {"n": "10"})
    assert result == "Set i /1*10/;"


def test_expand_multiple_macros():
    """Test expanding multiple different macros."""
    source = "Set i /1*%n%/; Set j /1*%m%/;"
    result = expand_macros(source, {"n": "10", "m": "20"})
    assert result == "Set i /1*10/; Set j /1*20/;"


def test_expand_macro_multiple_times():
    """Test same macro used multiple times."""
    source = "x = %n% + %n% * 2"
    result = expand_macros(source, {"n": "5"})
    assert result == "x = 5 + 5 * 2"


def test_expand_macro_unknown_unchanged():
    """Test unknown macros are left unchanged."""
    source = "Set i /1*%unknown%/;"
    result = expand_macros(source, {"n": "10"})
    assert result == "Set i /1*%unknown%/;"


def test_strip_simple_set():
    """Test stripping a simple $set directive."""
    source = "$set n 10\nSet i /1*10/;"
    result = strip_set_directives(source)
    assert result == "* [Stripped: $set n 10]\nSet i /1*10/;"


def test_strip_set_preserves_indentation():
    """Test that stripping preserves indentation."""
    source = "    $set n 10\n    Set i;"
    result = strip_set_directives(source)
    assert result == "    * [Stripped: $set n 10]\n    Set i;"


def test_strip_set_in_conditional():
    """Test stripping $set in $if line."""
    source = "$if set n $set np %n%\nSet i;"
    result = strip_set_directives(source)
    assert result == "* [Stripped: $if set n $set np %n%]\nSet i;"


def test_elec_gms_pattern():
    """Test actual pattern from elec.gms."""
    source = """
$if not set n $set n 10
$set np %n%+1

Set i /1*%n%/;
Set ip /1*%np%/;
"""
    # Extract macros (simulating the full pipeline)
    from src.ir.preprocessor import extract_conditional_sets

    cond_macros = extract_conditional_sets(source)
    set_macros = extract_set_directives(source, cond_macros)
    macros = {**cond_macros, **set_macros}

    # Expand macros
    expanded = expand_macros(source, macros)

    # Check that %n% and %np% were expanded
    assert "%n%" not in expanded or expanded.count("%n%") < source.count("%n%")
    assert "1*10" in expanded  # %n% expanded to 10
    assert "/1*10+1/" in expanded  # %np% expanded to 10+1


def test_set_with_scientific_notation():
    """Test $set with scientific notation value."""
    source = "$set tol 1e-6"
    macros = extract_set_directives(source)
    assert macros == {"tol": "1e-6"}


def test_set_with_expression():
    """Test $set with arithmetic expression."""
    source = "$set formula 2*x+3"
    macros = extract_set_directives(source)
    assert macros == {"formula": "2*x+3"}


def test_set_empty_value():
    """Test $set with empty value."""
    source = "$set flag"
    # This should either not match or extract empty value
    macros = extract_set_directives(source)
    # Empty values might not be captured, that's OK
    assert "flag" not in macros or macros["flag"] == ""
