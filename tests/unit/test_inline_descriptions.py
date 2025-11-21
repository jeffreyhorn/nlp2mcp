"""Test inline text descriptions in declarations.

Sprint 9 - GitHub Issue #277: Support inline text descriptions in scalar declarations.

Note: Currently only scalar declarations support inline descriptions. Parameter, variable,
and equation inline descriptions are not yet implemented due to grammar ambiguity issues.
"""

from src.ir.parser import parse_model_text


class TestScalarInlineDescriptions:
    """Test scalar declarations with inline descriptions."""

    def test_scalar_with_inline_description(self):
        """Test scalar declaration with inline description."""
        gams_code = """
        Scalar
           diff optcr - relative distance from global;
        """
        model = parse_model_text(gams_code)
        assert "diff" in model.params

    def test_scalar_with_data_and_description(self):
        """Test scalar with description and data."""
        gams_code = """
        Scalar
           global global solution / -0.262725145e5 /;
        """
        model = parse_model_text(gams_code)
        assert "global" in model.params
        assert model.params["global"].values == {(): -0.262725145e5}


class TestHS62Integration:
    """Test that hs62.gms parses successfully with inline descriptions."""

    def test_hs62_parses(self):
        """Test that hs62.gms parses successfully with inline descriptions."""
        with open("tests/fixtures/gamslib/hs62.gms") as f:
            gams_code = f.read()

        model = parse_model_text(gams_code)
        # Verify the scalar with inline description was parsed
        assert "diff" in model.params
        assert "global" in model.params


class TestComplexDescriptions:
    """Test complex description patterns."""

    def test_description_with_hyphens(self):
        """Test description containing hyphens."""
        gams_code = """
        Scalar
           myvar this-is-a-complex-description;
        """
        model = parse_model_text(gams_code)
        assert "myvar" in model.params

    def test_description_with_multiple_words(self):
        """Test description with multiple words."""
        gams_code = """
        Scalar
           test a long description with many words;
        """
        model = parse_model_text(gams_code)
        assert "test" in model.params
