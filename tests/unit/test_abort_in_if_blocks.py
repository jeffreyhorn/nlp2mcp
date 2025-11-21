"""
Unit tests for abort$ statements with square bracket conditionals.

Tests the fix for GitHub Issue #278:
- abort$ statements with square bracket conditionals: abort$[expr] "message";
- abort$ statements with parenthesis conditionals: abort$(expr) "message";
- abort$ statements without conditionals: abort "message";

Note: Full semantic processing tests for abort in if-blocks are covered by
mingamma.gms fixture parsing, which is verified in the GAMSLib dashboard tests.
"""

from src.ir.parser import parse_model_text


class TestAbortStatementSyntax:
    """Test abort$ statement syntax variations."""

    def test_abort_with_square_brackets_and_message(self):
        """Test abort$[condition] "message" syntax."""
        code = """
        Scalar x / 5 /;
        abort$[x > 3] "x is too large";
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_with_square_brackets_no_message(self):
        """Test abort$[condition] syntax without message."""
        code = """
        Scalar x / 5 /;
        abort$[x > 3];
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_with_parentheses_and_message(self):
        """Test abort$(condition) "message" syntax."""
        code = """
        Scalar x / 5 /;
        abort$(x > 3) "x is too large";
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_with_parentheses_no_message(self):
        """Test abort$(condition) syntax without message."""
        code = """
        Scalar x / 5 /;
        abort$(x > 3);
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_plain_conditional_with_message(self):
        """Test abort$ expr "message" syntax (no brackets)."""
        code = """
        Scalar x / 5 /;
        abort$ x > 3 "x is too large";
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_message_only(self):
        """Test abort "message" without conditional."""
        code = """
        abort "Execution stopped";
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_plain_no_message_no_condition(self):
        """Test abort; with no message or condition."""
        code = """
        abort;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_abort_complex_condition_square_brackets(self):
        """Test abort with complex logical condition using OR."""
        code = """
        Scalar x1delta / 0.001 /;
        Scalar y1delta / 0.0001 /;
        Scalar xtol / 0.00005 /;
        Scalar ytol / 0.000001 /;
        abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results";
        """
        result = parse_model_text(code)
        assert result is not None
