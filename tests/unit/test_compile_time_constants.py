"""
Unit tests for compile-time constants (%...% syntax).

Tests the fix for GitHub Issue #281:
- Compile-time constants with simple identifiers: %identifier%
- Compile-time constants with dotted paths: %path.to.value%
- Compile-time constants in various expression contexts
"""

from pathlib import Path

import pytest

from src.ir.parser import parse_model_text


class TestCompileTimeConstantSyntax:
    """Test compile-time constant syntax variations."""

    def test_simple_compile_time_constant(self):
        """Test %identifier% syntax."""
        code = """
        Scalar x / 5 /;
        Scalar y;
        y = %myconst%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_dotted_path_compile_time_constant(self):
        """Test %path.to.value% syntax."""
        code = """
        Scalar x / 5 /;
        Scalar y;
        y = %system.date%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_compile_time_constant_in_comparison(self):
        """Test compile-time constant in comparison expression."""
        code = """
        Scalar x / 5 /;
        Scalar result;
        result = x > %threshold%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_compile_time_constant_with_dotted_path_in_comparison(self):
        """Test %solveStat.capabilityProblems% pattern from mingamma.gms."""
        code = """
        Scalar solveStat / 1 /;
        Scalar result;
        result = solveStat <> %solveStat.capabilityProblems%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_compile_time_constant_in_arithmetic(self):
        """Test compile-time constant in arithmetic expression."""
        code = """
        Scalar x / 5 /;
        Scalar y;
        y = x + %offset%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_multiple_compile_time_constants(self):
        """Test multiple compile-time constants in same expression."""
        code = """
        Scalar result;
        result = %min% + %max%;
        """
        result = parse_model_text(code)
        assert result is not None

    def test_compile_time_constant_in_function_call(self):
        """Test compile-time constant as function argument."""
        code = """
        Scalar result;
        result = sqrt(%value%);
        """
        result = parse_model_text(code)
        assert result is not None

    def test_nested_dotted_path(self):
        """Test deeply nested dotted path."""
        code = """
        Scalar result;
        result = %system.config.optimization.level%;
        """
        result = parse_model_text(code)
        assert result is not None


class TestCompileTimeConstantsInControlFlow:
    """Test compile-time constants in control flow statements."""

    def test_compile_time_constant_in_if_condition(self):
        """Test compile-time constant in if-statement condition."""
        code = """
        Scalar x / 5 /;
        if(x <> %flag%,
            display x;
        );
        """
        result = parse_model_text(code)
        assert result is not None

    def test_mingamma_pattern(self):
        """Test the exact pattern from mingamma.gms lines 58-60."""
        code = """
        Scalar x1delta / 0.001 /;
        Scalar y1delta / 0.0001 /;
        Scalar xtol / 0.00005 /;
        Scalar ytol / 0.000001 /;

        Variable x1;
        Equation dummy;
        dummy.. x1 =e= 5;
        Model m1 / dummy /;
        solve m1 minimizing x1 using nlp;

        if(m1.solveStat <> %solveStat.capabilityProblems%,
            abort$[abs(x1delta) > xtol or abs(y1delta) > ytol] "inconsistent results with gamma";
        );
        """
        result = parse_model_text(code)
        assert result is not None


class TestMingammaGrammarParses:
    """Test that mingamma.gms parses at the grammar level."""

    def test_mingamma_grammar_parsing(self):
        """Test that mingamma.gms parses successfully at grammar level.

        Note: Full semantic parsing fails due to unsupported gamma()/loggamma() functions,
        but the compile-time constant syntax (%...%) now works correctly.
        """
        fixture_path = Path("tests/fixtures/gamslib/mingamma.gms")

        # Skip if fixture doesn't exist (for environments without GAMSLib)
        if not fixture_path.exists():
            pytest.skip(f"Fixture file not found: {fixture_path}")

        from src.ir.parser import parse_text

        with open(fixture_path) as f:
            code = f.read()

        # Should parse at grammar level without raising an exception
        tree = parse_text(code)
        assert tree is not None
