"""Unit tests for $macro directive preprocessing."""

from src.ir.preprocessor import (
    expand_macro_calls,
    extract_macro_definitions,
    strip_macro_directives,
)


def test_extract_macro_simple():
    """Test extraction of simple macro definition."""
    source = "$macro fx(t) sin(t)"
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t"], "sin(t)")}


def test_extract_macro_with_variable_reference():
    """Test extraction of macro with %variable% reference."""
    source = "$macro fx(t) %scale%*t"
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t"], "%scale%*t")}


def test_extract_macro_multiple_params():
    """Test extraction of macro with multiple parameters."""
    source = "$macro sum2(i,j,expr) sum(i, sum(j, expr))"
    macros = extract_macro_definitions(source)
    assert macros == {"sum2": (["i", "j", "expr"], "sum(i, sum(j, expr))")}


def test_extract_macro_with_whitespace():
    """Test extraction handles whitespace in parameter list."""
    source = "$macro fx(t , x) t*x"
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t", "x"], "t*x")}


def test_extract_macro_complex_body():
    """Test extraction of macro with complex body."""
    source = "$macro fx(t) sin(t) * cos(t-t*t)"
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t"], "sin(t) * cos(t-t*t)")}


def test_extract_multiple_macros():
    """Test extraction of multiple macro definitions."""
    source = """
    $macro fx(t) %fx%
    $macro fy(t) %fy%
    """
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t"], "%fx%"), "fy": (["t"], "%fy%")}


def test_extract_macro_case_insensitive():
    """Test that $macro directive is case-insensitive."""
    source = "$MACRO fx(t) sin(t)"
    macros = extract_macro_definitions(source)
    assert macros == {"fx": (["t"], "sin(t)")}


def test_extract_macro_no_params():
    """Test extraction of macro with no parameters."""
    source = "$macro pi() 3.14159"
    macros = extract_macro_definitions(source)
    assert macros == {"pi": ([], "3.14159")}


def test_expand_macro_call_simple():
    """Test expansion of simple macro call."""
    source = "x =e= fx(y);"
    macro_defs = {"fx": (["t"], "sin(t)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(y);"


def test_expand_macro_call_with_nested_parens():
    """Test expansion of macro call with nested parentheses."""
    source = "x =e= fx(t('1'));"
    macro_defs = {"fx": (["t"], "sin(t) * cos(t)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(t('1')) * cos(t('1'));"


def test_expand_macro_call_multiple_params():
    """Test expansion of macro call with multiple parameters."""
    source = "total =e= sum2(i, j, data(i,j));"
    macro_defs = {"sum2": (["i", "j", "expr"], "sum(i, sum(j, expr))")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "total =e= sum(i, sum(j, data(i,j)));"


def test_expand_macro_call_complex_arg():
    """Test expansion with complex argument expressions.

    Note: GAMS performs textual substitution without adding parentheses.
    The user must add parentheses in the macro definition if needed.
    """
    source = "x =e= fx(t-1);"
    macro_defs = {"fx": (["t"], "2*t")}
    result = expand_macro_calls(source, macro_defs)
    # Textual substitution: t -> (t-1), so 2*t becomes 2*t-1
    assert result == "x =e= 2*t-1;"


def test_expand_macro_call_multiple_calls():
    """Test expansion of multiple macro calls on same line."""
    source = "x =e= fx(t('1')) + fx(t('2'));"
    macro_defs = {"fx": (["t"], "sin(t)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(t('1')) + sin(t('2'));"


def test_expand_macro_call_no_expansion():
    """Test that undefined macros are not expanded."""
    source = "x =e= fx(y);"
    macro_defs = {}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= fx(y);"


def test_expand_macro_call_argument_mismatch():
    """Test that macro with wrong number of arguments is not expanded."""
    source = "x =e= fx(y, z);"
    macro_defs = {"fx": (["t"], "sin(t)")}
    result = expand_macro_calls(source, macro_defs)
    # Should not expand - argument count mismatch
    assert result == "x =e= fx(y, z);"


def test_expand_macro_preserves_non_macro_functions():
    """Test that non-macro function calls are preserved."""
    source = "x =e= sin(y) + fx(z);"
    macro_defs = {"fx": (["t"], "cos(t)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(y) + cos(z);"


def test_strip_macro_directives():
    """Test stripping $macro directives."""
    source = """$macro fx(t) %fx%
x =e= fx(y);"""
    result = strip_macro_directives(source)
    expected = """* [Stripped: $macro fx(t) %fx%]
x =e= fx(y);"""
    assert result == expected


def test_strip_macro_preserves_indentation():
    """Test that stripping preserves indentation."""
    source = "  $macro fx(t) sin(t)\nx =e= y;"
    result = strip_macro_directives(source)
    expected = "  * [Stripped: $macro fx(t) sin(t)]\nx =e= y;"
    assert result == expected


def test_inscribedsquare_pattern():
    """Test actual pattern from inscribedsquare.gms.

    Note: For complex expressions with spaces, use separate $set directives
    or use extract_set_directives instead of extract_conditional_sets.
    """
    # Use the approach that works: separate $set after conditional check
    source = """$if not set fx $set fx sin(t)*cos(t-t*t)
$if not set fy $set fy t*sin(t)

$macro fx(t) %fx%
$macro fy(t) %fy%

Equations
  e1x, e1y;

e1x.. fx(t('1')) =E= x;
e1y.. fy(t('1')) =E= y;"""

    # Use extract_set_directives which handles complex expressions
    from src.ir.preprocessor import expand_macros, extract_set_directives

    # extract_set_directives uses [^;\n]+ which captures everything to end of line
    macros = extract_set_directives(source)
    assert macros == {"fx": "sin(t)*cos(t-t*t)", "fy": "t*sin(t)"}

    content = expand_macros(source, macros)

    # Then extract and expand $macro definitions
    macro_defs = extract_macro_definitions(content)
    assert macro_defs == {
        "fx": (["t"], "sin(t)*cos(t-t*t)"),
        "fy": (["t"], "t*sin(t)"),
    }

    content = expand_macro_calls(content, macro_defs)

    # Verify expansions
    assert "fx(t('1'))" not in content
    assert "fy(t('1'))" not in content
    assert "sin(t('1'))*cos(t('1')-t('1')*t('1'))" in content
    assert "t('1')*sin(t('1'))" in content


def test_macro_with_complex_nested_parens():
    """Test macro expansion with deeply nested parentheses."""
    source = "x =e= fx(t(i,j('k')));"
    macro_defs = {"fx": (["t"], "sin(t) + cos(t)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(t(i,j('k'))) + cos(t(i,j('k')));"


def test_macro_parameter_boundary_matching():
    """Test that parameter substitution uses word boundaries."""
    source = "x =e= fx(t);"
    # Parameter 't' should not match 'test' or 'at'
    macro_defs = {"fx": (["t"], "test + t + at")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= test + t + at;"


def test_macro_empty_body():
    """Test macro with empty/minimal body.

    Note: The regex requires .+ (at least one character) for the body,
    so truly empty macros are not supported. This matches GAMS behavior.
    """
    source = "$macro noop(x) x"
    macros = extract_macro_definitions(source)
    assert macros == {"noop": (["x"], "x")}


def test_expand_macro_multiple_macros():
    """Test expansion with multiple different macros."""
    source = "x =e= fx(t) + fy(s);"
    macro_defs = {"fx": (["t"], "sin(t)"), "fy": (["s"], "cos(s)")}
    result = expand_macro_calls(source, macro_defs)
    assert result == "x =e= sin(t) + cos(s);"


def test_macro_with_operators_in_args():
    """Test macro call with operators in arguments.

    Note: GAMS performs textual substitution. The argument replaces
    the parameter without adding extra parentheses.
    """
    source = "x =e= fx(a+b*c);"
    macro_defs = {"fx": (["t"], "2*t")}
    result = expand_macro_calls(source, macro_defs)
    # t is replaced with a+b*c, so 2*t becomes 2*a+b*c
    assert result == "x =e= 2*a+b*c;"


def test_macro_multi_pass_expansion():
    """Test that our implementation does multi-pass macro expansion.

    Note: Our implementation processes all macros in the dictionary,
    which means if a macro body contains another macro call, it will
    be expanded. This is actually useful behavior.
    """
    source = "x =e= fx(t);"
    macro_defs = {"fx": (["t"], "fy(t)"), "fy": (["s"], "sin(s)")}
    result = expand_macro_calls(source, macro_defs)
    # fx(t) expands to fy(t), then fy(t) expands to sin(t)
    # This happens because we iterate over all macros in the dict
    assert result == "x =e= sin(t);"


def test_macro_case_sensitive_names():
    """Test that macro names are case-sensitive."""
    source = "x =e= FX(t);"
    macro_defs = {"fx": (["t"], "sin(t)")}
    result = expand_macro_calls(source, macro_defs)
    # Should not expand - case mismatch
    assert result == "x =e= FX(t);"
