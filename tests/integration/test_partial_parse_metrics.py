"""
Integration tests for partial parse metrics.
"""

from pathlib import Path

from src.ir.parser import parse_model_file
from src.utils.parse_progress import (
    calculate_parse_progress_from_file,
    extract_missing_features,
)


class TestPartialParseMetricsIntegration:
    """Integration tests for partial parse progress tracking."""

    def test_successful_parse_has_100_percent(self, tmp_path: Path):
        """Successful parse should report 100% progress."""
        # Create a simple valid GAMS model
        model_file = tmp_path / "test.gms"
        model_file.write_text("""
Set i / 1*10 /;
Parameter x(i);
Variable y;
""")

        # Parse should succeed
        parse_model_file(model_file)

        # Calculate progress metrics
        progress = calculate_parse_progress_from_file(model_file, error=None)

        assert progress["percentage"] == 100.0
        assert progress["lines_parsed"] == 3
        assert progress["lines_total"] == 3

    def test_failed_parse_has_partial_progress(self, tmp_path: Path):
        """Failed parse should report partial progress."""
        # Create a model that fails mid-file
        model_file = tmp_path / "test.gms"
        model_file.write_text("""
Set i / 1*10 /;
Set j / a, b, c /;
Invalid syntax here @@@
""")

        # Parse should fail
        error = None
        try:
            parse_model_file(model_file)
        except Exception as e:
            error = e

        assert error is not None

        # Calculate progress metrics
        progress = calculate_parse_progress_from_file(model_file, error)

        assert progress["percentage"] is not None
        assert progress["percentage"] < 100.0
        assert progress["lines_parsed"] < progress["lines_total"]

        # Extract missing features
        features = extract_missing_features(type(error).__name__, str(error), None)
        assert len(features) > 0

    def test_parse_progress_with_comments(self, tmp_path: Path):
        """Parse progress should skip comments correctly."""
        model_file = tmp_path / "test.gms"
        model_file.write_text("""
* This is a comment
Set i / 1*10 /;
* Another comment
Set j / a, b, c /;

Parameter x(i);
""")

        parse_model_file(model_file)
        progress = calculate_parse_progress_from_file(model_file, error=None)

        assert progress["percentage"] == 100.0
        # Should count only non-comment lines: Set i, Set j, Parameter x = 3 lines
        assert progress["lines_parsed"] == 3
        assert progress["lines_total"] == 3

    def test_parse_progress_with_multiline_comments(self, tmp_path: Path):
        """Parse progress should handle multiline comments."""
        model_file = tmp_path / "test.gms"
        model_file.write_text("""
Set i / 1*10 /;
$ontext
This is a long comment
spanning multiple lines
$offtext
Parameter x(i);
""")

        parse_model_file(model_file)
        progress = calculate_parse_progress_from_file(model_file, error=None)

        assert progress["percentage"] == 100.0
        # Should count only: Set i, Parameter x = 2 lines
        assert progress["lines_parsed"] == 2
        assert progress["lines_total"] == 2

    def test_missing_features_extracted_for_lead_lag(self, tmp_path: Path):
        """Lead/lag indexing now supported (Sprint 9)."""
        model_file = tmp_path / "test.gms"
        model_file.write_text("""
Set i / 1*10 /;
Parameter x(i);
Variable y(i);
Equation eq(i);
eq(i).. y(i) =e= x(i++1);
""")

        # Sprint 9: i++1 is now supported, should parse successfully
        model = parse_model_file(model_file)
        assert model is not None
        assert len(model.equations) == 1

        # Verify progress is 100%
        progress = calculate_parse_progress_from_file(model_file, error=None)
        assert progress["percentage"] == 100.0

        # No missing features to extract since parsing succeeded
        # Previously this test checked for lead/lag feature detection in errors
        # Now that lead/lag is supported, the test validates successful parsing

    def test_parse_empty_file(self, tmp_path: Path):
        """Empty file should parse successfully with 0 lines."""
        model_file = tmp_path / "empty.gms"
        model_file.write_text("")

        # Empty file should succeed (no syntax errors)
        parse_model_file(model_file)
        progress = calculate_parse_progress_from_file(model_file, error=None)

        assert progress["percentage"] == 100.0
        assert progress["lines_parsed"] == 0
        assert progress["lines_total"] == 0

    def test_parse_comments_only_file(self, tmp_path: Path):
        """File with only comments should parse successfully."""
        model_file = tmp_path / "comments.gms"
        model_file.write_text("""
* This is a comment
* Another comment

$ontext
Multiline comment
$offtext

* Final comment
""")

        parse_model_file(model_file)
        progress = calculate_parse_progress_from_file(model_file, error=None)

        assert progress["percentage"] == 100.0
        assert progress["lines_parsed"] == 0
        assert progress["lines_total"] == 0
