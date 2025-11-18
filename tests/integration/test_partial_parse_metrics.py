"""
Integration tests for partial parse metrics in ingestion script.
"""

from pathlib import Path

from scripts.ingest_gamslib import ModelResult, parse_model


class TestPartialParseMetricsIntegration:
    """Integration tests for partial parse progress tracking."""

    def test_successful_parse_has_100_percent(self, tmp_path: Path):
        """Successful parse should report 100% progress."""
        # Create a simple valid GAMS model
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
Set i / 1*10 /;
Parameter x(i);
Variable y;
"""
        )

        result = parse_model(model_file)

        assert result.parse_status == "SUCCESS"
        assert result.parse_progress_percentage == 100.0
        assert result.parse_progress_lines_parsed == 3
        assert result.parse_progress_lines_total == 3
        assert result.missing_features == []

    def test_failed_parse_has_partial_progress(self, tmp_path: Path):
        """Failed parse should report partial progress."""
        # Create a model that fails mid-file
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
Set i / 1*10 /;
Set j / a, b, c /;
Invalid syntax here @@@
"""
        )

        result = parse_model(model_file)

        assert result.parse_status == "FAILED"
        assert result.parse_progress_percentage is not None
        assert result.parse_progress_percentage < 100.0
        assert result.parse_progress_lines_parsed is not None
        assert result.parse_progress_lines_parsed < result.parse_progress_lines_total
        assert result.missing_features is not None
        assert len(result.missing_features) > 0

    def test_parse_progress_with_comments(self, tmp_path: Path):
        """Parse progress should skip comments correctly."""
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
* This is a comment
Set i / 1*10 /;
* Another comment
Set j / a, b, c /;

Parameter x(i);
"""
        )

        result = parse_model(model_file)

        assert result.parse_status == "SUCCESS"
        assert result.parse_progress_percentage == 100.0
        # Should count only non-comment lines: Set i, Set j, Parameter x = 3 lines
        assert result.parse_progress_lines_parsed == 3
        assert result.parse_progress_lines_total == 3

    def test_parse_progress_with_multiline_comments(self, tmp_path: Path):
        """Parse progress should handle multiline comments."""
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
Set i / 1*10 /;
$ontext
This is a long comment
spanning multiple lines
$offtext
Parameter x(i);
"""
        )

        result = parse_model(model_file)

        assert result.parse_status == "SUCCESS"
        assert result.parse_progress_percentage == 100.0
        # Should count only: Set i, Parameter x = 2 lines
        assert result.parse_progress_lines_parsed == 2
        assert result.parse_progress_lines_total == 2

    def test_missing_features_extracted_for_lead_lag(self, tmp_path: Path):
        """Missing features should detect lead/lag indexing."""
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
Set i / 1*10 /;
Parameter x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1);
"""
        )

        result = parse_model(model_file)

        # This will fail because i++1 is not supported
        assert result.parse_status == "FAILED"
        assert result.missing_features is not None
        assert any("lead/lag" in f.lower() or "i++" in f.lower() for f in result.missing_features)

    def test_missing_features_for_semantic_errors(self, tmp_path: Path):
        """Semantic errors should also report missing features."""
        # Create a model that triggers a semantic error
        # Note: This depends on what semantic errors the parser produces
        # For now, we'll just verify the structure is correct
        model_file = tmp_path / "test.gms"
        model_file.write_text(
            """
Set i / 1*10 /;
Parameter x;
x = 5;
"""
        )

        result = parse_model(model_file)

        # Even if it succeeds or fails, it should have all the new fields
        assert hasattr(result, "parse_progress_percentage")
        assert hasattr(result, "parse_progress_lines_parsed")
        assert hasattr(result, "parse_progress_lines_total")
        assert hasattr(result, "missing_features")

    def test_model_result_dataclass_fields(self):
        """ModelResult should have all required fields."""
        # Create a minimal ModelResult
        result = ModelResult(
            model_name="test",
            gms_file="test.gms",
            parse_status="SUCCESS",
            parse_error=None,
            parse_error_type=None,
            parse_progress_percentage=100.0,
            parse_progress_lines_parsed=10,
            parse_progress_lines_total=10,
            missing_features=[],
        )

        # Verify all Sprint 8 Day 7 fields exist
        assert result.parse_progress_percentage == 100.0
        assert result.parse_progress_lines_parsed == 10
        assert result.parse_progress_lines_total == 10
        assert result.missing_features == []

    def test_model_result_with_partial_progress(self):
        """ModelResult should handle partial progress correctly."""
        result = ModelResult(
            model_name="test",
            gms_file="test.gms",
            parse_status="FAILED",
            parse_error="Syntax error",
            parse_error_type="UnexpectedToken",
            parse_progress_percentage=75.0,
            parse_progress_lines_parsed=15,
            parse_progress_lines_total=20,
            missing_features=["lead/lag indexing (i++1, i--1)", "option statements"],
        )

        assert result.parse_status == "FAILED"
        assert result.parse_progress_percentage == 75.0
        assert result.parse_progress_lines_parsed == 15
        assert result.parse_progress_lines_total == 20
        assert len(result.missing_features) == 2
        assert "lead/lag indexing" in result.missing_features[0]

    def test_parse_empty_file(self, tmp_path: Path):
        """Empty file should parse successfully with 0 lines."""
        model_file = tmp_path / "empty.gms"
        model_file.write_text("")

        result = parse_model(model_file)

        # Empty file should succeed (no syntax errors)
        assert result.parse_status == "SUCCESS"
        assert result.parse_progress_percentage == 100.0
        assert result.parse_progress_lines_parsed == 0
        assert result.parse_progress_lines_total == 0

    def test_parse_comments_only_file(self, tmp_path: Path):
        """File with only comments should parse successfully."""
        model_file = tmp_path / "comments.gms"
        model_file.write_text(
            """
* This is a comment
* Another comment

$ontext
Multiline comment
$offtext

* Final comment
"""
        )

        result = parse_model(model_file)

        assert result.parse_status == "SUCCESS"
        assert result.parse_progress_percentage == 100.0
        assert result.parse_progress_lines_parsed == 0
        assert result.parse_progress_lines_total == 0
