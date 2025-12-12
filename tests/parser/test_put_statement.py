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
