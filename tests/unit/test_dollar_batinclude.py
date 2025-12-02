"""Unit tests for $batInclude directive preprocessing."""

from src.ir.preprocessor import preprocess_bat_includes


def test_batinclude_simple_substitution(tmp_path):
    """Test basic $batInclude with argument substitution."""
    # Create included file
    inc_file = tmp_path / "helper.inc"
    inc_file.write_text("Set s%1 /%2/;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude helper.inc foo bar"

    result = preprocess_bat_includes(main_file, source)

    assert "Set sfoo /bar/;" in result
    assert "$batInclude" not in result or "BEGIN BATINCLUDE" in result


def test_batinclude_multiple_arguments(tmp_path):
    """Test $batInclude with multiple arguments."""
    # Create included file
    inc_file = tmp_path / "data.inc"
    inc_file.write_text("Parameter p%1 /%2/;\nScalar s%3 /%4/;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude data.inc A 10 B 20"

    result = preprocess_bat_includes(main_file, source)

    assert "Parameter pA /10/;" in result
    assert "Scalar sB /20/;" in result


def test_batinclude_numeric_arguments(tmp_path):
    """Test $batInclude with numeric arguments."""
    # Create included file
    inc_file = tmp_path / "partition.inc"
    inc_file.write_text("Set nh 'intervals' / 1*%1 /;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude partition.inc 21"

    result = preprocess_bat_includes(main_file, source)

    assert "Set nh 'intervals' / 1*21 /;" in result


def test_batinclude_file_not_found(tmp_path):
    """Test $batInclude with missing file is commented out."""
    main_file = tmp_path / "main.gms"
    source = "$batInclude missing.inc arg1 arg2"

    result = preprocess_bat_includes(main_file, source)

    assert "Stripped" in result or "file not found" in result
    assert "missing.inc" in result


def test_batinclude_no_arguments(tmp_path):
    """Test $batInclude without arguments."""
    # Create included file
    inc_file = tmp_path / "simple.inc"
    inc_file.write_text("Scalar x / 5 /;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude simple.inc"

    result = preprocess_bat_includes(main_file, source)

    assert "Scalar x / 5 /;" in result


def test_batinclude_quoted_filename(tmp_path):
    """Test $batInclude with quoted filename."""
    # Create included file with spaces in name
    inc_file = tmp_path / "my file.inc"
    inc_file.write_text("Set i /%1/;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = '$batInclude "my file.inc" a'

    result = preprocess_bat_includes(main_file, source)

    assert "Set i /a/;" in result


def test_batinclude_preserves_non_directives(tmp_path):
    """Test that non-$batInclude lines are preserved."""
    main_file = tmp_path / "main.gms"
    source = """Set i / 1*5 /;
Scalar x / 10 /;"""

    result = preprocess_bat_includes(main_file, source)

    assert "Set i / 1*5 /;" in result
    assert "Scalar x / 10 /;" in result


def test_batinclude_case_insensitive(tmp_path):
    """Test that $batInclude is case-insensitive."""
    # Create included file
    inc_file = tmp_path / "test.inc"
    inc_file.write_text("Set s%1;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$BATINCLUDE test.inc foo"

    result = preprocess_bat_includes(main_file, source)

    assert "Set sfoo;" in result


def test_batinclude_multiline(tmp_path):
    """Test $batInclude with content before and after."""
    # Create included file
    inc_file = tmp_path / "middle.inc"
    inc_file.write_text("Parameter p%1 /%2/;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = """Scalar before / 1 /;
$batInclude middle.inc x 5
Scalar after / 2 /;"""

    result = preprocess_bat_includes(main_file, source)

    assert "Scalar before / 1 /;" in result
    assert "Parameter px /5/;" in result
    assert "Scalar after / 2 /;" in result


def test_batinclude_nested(tmp_path):
    """Test nested $batInclude directives."""
    # Create nested included file
    nested_file = tmp_path / "nested.inc"
    nested_file.write_text("Scalar nested%1 /%2/;")

    # Create middle included file that itself has $batInclude
    middle_file = tmp_path / "middle.inc"
    middle_file.write_text("$batInclude nested.inc A 10")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude middle.inc"

    result = preprocess_bat_includes(main_file, source)

    assert "Scalar nestedA /10/;" in result


def test_batinclude_argument_order(tmp_path):
    """Test that arguments are substituted in correct order."""
    # Create included file
    inc_file = tmp_path / "order.inc"
    inc_file.write_text("%1 %2 %3")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude order.inc first second third"

    result = preprocess_bat_includes(main_file, source)

    assert "first second third" in result


def test_batinclude_complex_arguments(tmp_path):
    """Test $batInclude with complex argument values."""
    # Create included file
    inc_file = tmp_path / "complex.inc"
    inc_file.write_text("Set colloc_%1 'type %1';")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude complex.inc nc4"

    result = preprocess_bat_includes(main_file, source)

    assert "Set colloc_nc4 'type nc4';" in result


def test_batinclude_gasoil_pattern(tmp_path):
    """Test actual pattern from gasoil.gms with copspart.inc."""
    # Create simplified copspart.inc
    cops_file = tmp_path / "copspart.inc"
    cops_file.write_text(
        """* Collocation points: %1
* Measurements: %2
Set nh / 1*%2 /;
Parameter rho('%1');"""
    )

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude copspart.inc nc4 21"

    result = preprocess_bat_includes(main_file, source)

    assert "* Collocation points: nc4" in result
    assert "* Measurements: 21" in result
    assert "Set nh / 1*21 /;" in result
    assert "Parameter rho('nc4');" in result


def test_batinclude_with_comments(tmp_path):
    """Test that $batInclude in comments is processed (edge case).

    Note: Current implementation processes $batInclude even in comments.
    This is acceptable since GAMS itself would process it too.
    """
    main_file = tmp_path / "main.gms"
    source = """* $batInclude test.inc arg
Set i / 1*5 /;"""

    result = preprocess_bat_includes(main_file, source)

    # Since file doesn't exist, it gets stripped
    assert "Stripped" in result or "file not found" in result
    assert "Set i / 1*5 /;" in result


def test_batinclude_relative_path(tmp_path):
    """Test $batInclude with relative path resolution."""
    # Create subdirectory
    subdir = tmp_path / "includes"
    subdir.mkdir()

    # Create included file in subdirectory
    inc_file = subdir / "data.inc"
    inc_file.write_text("Scalar s%1;")

    # Create main file in parent directory
    main_file = tmp_path / "main.gms"
    source = "$batInclude includes/data.inc x"

    result = preprocess_bat_includes(main_file, source)

    assert "Scalar sx;" in result


def test_batinclude_argument_with_special_chars(tmp_path):
    """Test $batInclude with arguments containing special characters."""
    # Create included file
    inc_file = tmp_path / "special.inc"
    inc_file.write_text("Set s /%1/;")

    # Create main file
    main_file = tmp_path / "main.gms"
    source = "$batInclude special.inc 'a-b'"

    result = preprocess_bat_includes(main_file, source)

    assert "Set s /'a-b'/;" in result
