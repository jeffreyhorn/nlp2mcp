"""Tests for GAMS file statement parsing (GitHub Issue #434).

The file statement declares a file handle for output operations.
Since file I/O is not relevant for NLP model extraction, we parse
but don't process these statements (mock/skip approach).
"""

from src.ir.parser import parse_model_text


def test_file_statement_basic():
    """Test basic file statement with simple string path."""
    source = """
file f / 'output.txt' /;
"""
    # Main test: parsing should succeed without error
    model = parse_model_text(source)
    # File statements are parsed but not stored in model
    assert model is not None


def test_file_statement_double_quotes():
    """Test file statement with double-quoted path."""
    source = """
file myfile / "data/results.csv" /;
"""
    model = parse_model_text(source)
    assert model is not None


def test_file_statement_compile_time_const():
    """Test file statement with compile-time constant path (like in inscribedsquare.gms)."""
    source = """
file f / '%gams.scrdir%gnuplot.in' /;
"""
    model = parse_model_text(source)
    assert model is not None


def test_file_statement_with_other_statements():
    """Test file statement alongside other model statements."""
    source = """
Set i / i1, i2 /;
Parameter x(i) / i1 1, i2 2 /;

file results / 'output.txt' /;

Scalar total / 0 /;
"""
    model = parse_model_text(source)
    assert "i" in model.sets
    assert "x" in model.params
    assert "total" in model.params


def test_file_statement_multiple():
    """Test multiple file statements."""
    source = """
file f1 / 'output1.txt' /;
file f2 / 'output2.txt' /;
file log / 'debug.log' /;
"""
    model = parse_model_text(source)
    assert model is not None


def test_file_statement_case_insensitive():
    """Test FILE keyword is case insensitive."""
    source = """
FILE f / 'output.txt' /;
"""
    model = parse_model_text(source)
    assert model is not None


def test_file_statement_mixed_case():
    """Test File keyword with mixed case."""
    source = """
File f / 'output.txt' /;
"""
    model = parse_model_text(source)
    assert model is not None
