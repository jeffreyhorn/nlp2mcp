"""Tests for GAMS put statement parsing (Sprint 12 - Issue #447).

The put statement is used for writing output to files in GAMS.
We parse but don't process since file I/O is not relevant for NLP model extraction.
"""

from src.ir.parser import parse_model_text


class TestPutBasic:
    """Test basic put statement parsing."""

    def test_put_file_selection(self):
        """Test put with file handle: put f;"""
        source = """
file f / 'test.txt' /;
put f;
"""
        model = parse_model_text(source)
        # Put statements are parsed but not stored (mock/skip)
        assert model is not None

    def test_put_string(self):
        """Test put with string: put 'Hello World';"""
        source = """
file f / 'test.txt' /;
put f;
put 'Hello World';
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_string_with_newline(self):
        """Test put with string and newline: put 'Hello World' /;"""
        source = """
file f / 'test.txt' /;
put f;
put 'Hello World' /;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_empty(self):
        """Test empty put: put;"""
        source = """
file f / 'test.txt' /;
put f;
put;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutExpressions:
    """Test put statement with expressions."""

    def test_put_scalar(self):
        """Test put with scalar: put x;"""
        source = """
Scalar x / 5 /;
file f / 'test.txt' /;
put f;
put x;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_variable_level(self):
        """Test put with variable level: put x.l;"""
        source = """
Variable x;
file f / 'test.txt' /;
put f;
put x.l;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_expression(self):
        """Test put with expression: put (x + y);"""
        source = """
Scalar x / 5 /, y / 3 /;
file f / 'test.txt' /;
put f;
put (x + y);
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutMultipleItems:
    """Test put statement with multiple items."""

    def test_put_string_and_value(self):
        """Test put with string and value: put 'x = ' x;"""
        source = """
Scalar x / 5 /;
file f / 'test.txt' /;
put f;
put 'x = ' x;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_multiple_values(self):
        """Test put with multiple values: put x ',' y;"""
        source = """
Scalar x / 5 /, y / 3 /;
file f / 'test.txt' /;
put f;
put x ',' y;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_complex_output(self):
        """Test put with complex output: put 'x = ' x ' y = ' y /;"""
        source = """
Scalar x / 5 /, y / 3 /;
file f / 'test.txt' /;
put f;
put 'x = ' x ' y = ' y /;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutNewlines:
    """Test put statement newline handling."""

    def test_put_inline_newline(self):
        """Test put with inline newline: put 'line1' / 'line2';"""
        source = """
file f / 'test.txt' /;
put f;
put 'line1' / 'line2';
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_multiple_newlines(self):
        """Test put with multiple newlines: put 'a' / 'b' / 'c' /;"""
        source = """
file f / 'test.txt' /;
put f;
put 'a' / 'b' / 'c' /;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutclose:
    """Test putclose statement parsing."""

    def test_putclose_with_file(self):
        """Test putclose with file handle: putclose f;"""
        source = """
file f / 'test.txt' /;
put f;
put 'Hello';
putclose f;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_putclose_without_file(self):
        """Test putclose without file handle: putclose;"""
        source = """
file f / 'test.txt' /;
put f;
put 'Hello';
putclose;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutInControlFlow:
    """Test put statement inside control flow structures."""

    def test_put_in_if_block(self):
        """Test put inside if block."""
        source = """
Scalar x / 1 /;
file f / 'test.txt' /;
put f;
if(x > 0, put 'positive' /;);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_in_loop(self):
        """Test put inside loop."""
        source = """
Set i / 1*3 /;
file f / 'test.txt' /;
put f;
loop(i, put 'item' /;);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_putclose_in_if_block(self):
        """Test putclose inside if block."""
        source = """
Scalar x / 1 /;
file f / 'test.txt' /;
put f;
put 'Hello';
if(x > 0, putclose f;);
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutCaseInsensitive:
    """Test case insensitivity of put statements."""

    def test_put_uppercase(self):
        """Test uppercase PUT."""
        source = """
file f / 'test.txt' /;
PUT f;
PUT 'Hello' /;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_mixedcase(self):
        """Test mixed case Put."""
        source = """
file f / 'test.txt' /;
Put f;
Put 'Hello' /;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_putclose_uppercase(self):
        """Test uppercase PUTCLOSE."""
        source = """
file f / 'test.txt' /;
put f;
PUTCLOSE f;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutFormat:
    """Test put statement :width:decimals format specifiers (Sprint 19 Day 2)."""

    def test_put_format_width_decimals(self):
        """Test put with :width:decimals format: put x:8:2;"""
        source = """
scalar x / 1.5 /;
put x:8:2;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_width_only(self):
        """Test put with :width format (no decimals): put 'text':20;"""
        source = """
put 'Hello':20;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_string_with_format(self):
        """Test string item with format: put "RHS demand ",dl.tl:1;"""
        source = """
set dl / a, b /;
put "RHS demand ", dl.tl:1;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_multiple_items(self):
        """Test multiple items with format specifiers."""
        source = """
set i / i1, i2 /;
scalar x / 1.0 /;
parameter w(i) / i1 2.0, i2 3.0 /;
put x:20:10 w('i1'):20:10;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_in_loop(self):
        """Test put with format inside loop: loop(i, put pt(i):10:5;);"""
        source = """
set i / i1, i2 /;
parameter pt(i) / i1 1.0, i2 2.0 /;
loop(i, put pt(i):10:5;);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_expression_with_format(self):
        """Test parenthesized expression with format: put (1/card(s)):8:6;"""
        source = """
set s / s1, s2 /;
put (1/card(s)):8:6;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_with_newline(self):
        """Test put with format and trailing newline /."""
        source = """
scalar x / 1.0 /;
put x:12:4/;
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_format_mixed_items(self):
        """Test mix of formatted and unformatted items."""
        source = """
set i / i1 /;
scalar x / 1.0 /;
put 'label' x:20:10 /;
"""
        model = parse_model_text(source)
        assert model is not None


class TestPutNoSemicolon:
    """Test put statement without semicolon as final statement in loop/if (Sprint 19 Day 2)."""

    def test_put_nosemi_in_loop(self):
        """Test put without semicolon as final loop statement: loop(j, put j.tl);"""
        source = """
set j / j1, j2 /;
loop(j, put j.tl);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_nosemi_in_loop_with_newline(self):
        """Test put without semicolon with trailing newline: loop(i, put i.tl /);"""
        source = """
set i / i1, i2 /;
loop(i, put i.tl /);
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_nosemi_multiple_items(self):
        """Test put without semicolon with multiple items."""
        source = """
set j / j1 /;
parameter beta(j) / j1 0.5 /;
loop(j, put j.tl beta(j));
"""
        model = parse_model_text(source)
        assert model is not None

    def test_put_nosemi_with_format(self):
        """Test put without semicolon with format specifiers."""
        source = """
set i / i1 /;
parameter pt(i) / i1 1.0 /;
loop(i, put pt(i):10:5);
"""
        model = parse_model_text(source)
        assert model is not None
