"""Tests for GAMSLIB batch parse script."""

import argparse
import io
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path so we can import from scripts/
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.gamslib.batch_parse import (  # noqa: E402
    categorize_error,
    get_candidate_models,
    get_nlp2mcp_version,
    parse_single_model,
    print_summary,
    run_batch_parse,
)


class TestGetNlp2mcpVersion:
    """Tests for get_nlp2mcp_version function."""

    def test_version_from_importlib_metadata(self) -> None:
        """Test getting version from importlib.metadata."""
        with patch("importlib.metadata.version", return_value="0.2.5"):
            version = get_nlp2mcp_version()
            assert version == "0.2.5"

    def test_version_fallback_to_pyproject(self) -> None:
        """Test fallback to pyproject.toml when importlib.metadata fails."""
        pyproject_content = """
[project]
name = "nlp2mcp"
version = "0.3.1"
description = "Test"
"""

        def mock_version(name):
            raise Exception("Module not found")

        with patch("importlib.metadata.version", side_effect=mock_version):
            with patch.object(Path, "exists", return_value=True):
                with patch.object(Path, "read_text", return_value=pyproject_content):
                    version = get_nlp2mcp_version()
                    assert version == "0.3.1"

    def test_version_unknown_on_all_failures(self) -> None:
        """Test returns 'unknown' when all methods fail."""

        def mock_version(name):
            raise Exception("Module not found")

        with patch("importlib.metadata.version", side_effect=mock_version):
            with patch.object(Path, "exists", return_value=False):
                version = get_nlp2mcp_version()
                assert version == "unknown"


class TestCategorizeError:
    """Tests for categorize_error function."""

    def test_syntax_error_parse_error(self) -> None:
        """Test parse error is categorized as syntax_error."""
        error = "Parse error at line 10: unexpected token"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_syntax_error_unexpected_character(self) -> None:
        """Test unexpected character is categorized as syntax_error."""
        error = "Unexpected character '#' at position 5"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_syntax_error_unexpected_token(self) -> None:
        """Test unexpected token is categorized as syntax_error."""
        error = "Unexpected token 'END' on line 42"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_syntax_error_unexpected_eof(self) -> None:
        """Test unexpected EOF is categorized as syntax_error."""
        error = "Unexpected EOF while parsing model"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_no_objective_as_syntax_error(self) -> None:
        """Test no objective function is mapped to syntax_error."""
        error = "Model has no objective function defined"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_objective_function_error_specific(self) -> None:
        """Test specific objective function errors are categorized as syntax_error."""
        # "no objective function" should be caught
        error = "no objective function defined"
        category = categorize_error(error)
        assert category == "syntax_error"

        # "objective function not defined" should be caught
        error = "objective function not defined in model"
        category = categorize_error(error)
        assert category == "syntax_error"

    def test_objective_function_broad_pattern_not_matched(self) -> None:
        """Test broad 'objective function' patterns are not incorrectly categorized."""
        # Generic "objective function" mentions should NOT match as syntax_error
        # This prevents false positives like "Objective function validation failed"
        error = "Objective function validation failed"
        category = categorize_error(error)
        # Should fall through to internal_error since it doesn't match specific patterns
        assert category == "internal_error"

    def test_unsupported_feature_not_implemented(self) -> None:
        """Test 'not yet implemented' is categorized as unsupported_feature."""
        error = "Function 'gamma' is not yet implemented"
        category = categorize_error(error)
        assert category == "unsupported_feature"

    def test_unsupported_feature_unsupported(self) -> None:
        """Test 'unsupported' is categorized as unsupported_feature."""
        error = "Unsupported GAMS function: smin"
        category = categorize_error(error)
        assert category == "unsupported_feature"

    def test_validation_error_domain(self) -> None:
        """Test domain error is categorized as validation_error."""
        error = "Variable domain incompatible with constraint"
        category = categorize_error(error)
        assert category == "validation_error"

    def test_validation_error_incompatible(self) -> None:
        """Test incompatible error is categorized as validation_error."""
        error = "Incompatible types in expression"
        category = categorize_error(error)
        assert category == "validation_error"

    def test_validation_error_not_defined(self) -> None:
        """Test 'not defined' is categorized as validation_error."""
        error = "Variable 'x' is not defined in this scope"
        category = categorize_error(error)
        assert category == "validation_error"

    def test_validation_error_undefined(self) -> None:
        """Test 'undefined' is categorized as validation_error."""
        error = "Undefined variable reference in objective"
        category = categorize_error(error)
        assert category == "validation_error"

    def test_missing_include(self) -> None:
        """Test include file error is categorized as missing_include."""
        error = "Include file 'data.inc' not found"
        category = categorize_error(error)
        assert category == "missing_include"

    def test_missing_include_file_not_found(self) -> None:
        """Test file not found is categorized as missing_include."""
        error = "File not found: /path/to/model.gms"
        category = categorize_error(error)
        assert category == "missing_include"

    def test_timeout(self) -> None:
        """Test timeout is categorized as timeout."""
        error = "Parse timeout after 60 seconds"
        category = categorize_error(error)
        assert category == "timeout"

    def test_internal_error_unknown(self) -> None:
        """Test unknown error is categorized as internal_error."""
        error = "Something went wrong in the parser"
        category = categorize_error(error)
        assert category == "internal_error"

    def test_case_insensitive_matching(self) -> None:
        """Test error categorization is case-insensitive."""
        error = "PARSE ERROR at line 5"
        category = categorize_error(error)
        assert category == "syntax_error"


class TestGetCandidateModels:
    """Tests for get_candidate_models function."""

    def test_get_verified_convex_models(self) -> None:
        """Test getting verified_convex models."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
                {"model_id": "model2", "convexity": {"status": "excluded"}},
            ]
        }
        candidates = get_candidate_models(database)
        assert len(candidates) == 1
        assert candidates[0]["model_id"] == "model1"

    def test_get_likely_convex_models(self) -> None:
        """Test getting likely_convex models."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "likely_convex"}},
                {"model_id": "model2", "convexity": {"status": "error"}},
            ]
        }
        candidates = get_candidate_models(database)
        assert len(candidates) == 1
        assert candidates[0]["model_id"] == "model1"

    def test_get_both_verified_and_likely_convex(self) -> None:
        """Test getting both verified_convex and likely_convex models."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
                {"model_id": "model2", "convexity": {"status": "likely_convex"}},
                {"model_id": "model3", "convexity": {"status": "excluded"}},
            ]
        }
        candidates = get_candidate_models(database)
        assert len(candidates) == 2
        assert candidates[0]["model_id"] == "model1"
        assert candidates[1]["model_id"] == "model2"

    def test_get_no_candidates(self) -> None:
        """Test when no candidate models exist."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "excluded"}},
                {"model_id": "model2", "convexity": {"status": "error"}},
            ]
        }
        candidates = get_candidate_models(database)
        assert len(candidates) == 0

    def test_get_empty_database(self) -> None:
        """Test with empty database."""
        database = {"models": []}
        candidates = get_candidate_models(database)
        assert len(candidates) == 0

    def test_get_missing_convexity_field(self) -> None:
        """Test models without convexity field are excluded."""
        database = {
            "models": [
                {
                    "model_id": "model1",
                },
                {"model_id": "model2", "convexity": {"status": "verified_convex"}},
            ]
        }
        candidates = get_candidate_models(database)
        assert len(candidates) == 1
        assert candidates[0]["model_id"] == "model2"


class TestParseSingleModel:
    """Tests for parse_single_model function."""

    def test_successful_parse(self, tmp_path: Path) -> None:
        """Test successful model parse."""
        # Create a simple test model file
        model_file = tmp_path / "test_model.gms"
        model_file.write_text(
            """
* Simple test model
Variables x, y, obj;
Positive Variables x, y;

Equations
    objective   Define objective function
    constraint  Define constraint;

objective.. obj =e= x + y;
constraint.. x + y =l= 10;

Model test_model /all/;
Solve test_model using lp minimizing obj;
"""
        )

        # Mock the parser and validator
        mock_model = MagicMock()
        mock_model.variables = {"x": {}, "y": {}, "obj": {}}
        mock_model.equations = {"objective": {}, "constraint": {}}

        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
            with patch("src.validation.model.validate_model_structure"):
                result = parse_single_model(model_file)

        assert result["status"] == "success"
        assert "parse_time_seconds" in result
        assert result["parse_time_seconds"] >= 0
        assert result["variables_count"] == 3
        assert result["equations_count"] == 2

    def test_parse_failure_syntax_error(self, tmp_path: Path) -> None:
        """Test parse failure due to syntax error."""
        model_file = tmp_path / "bad_model.gms"
        model_file.write_text("Invalid GAMS syntax $$$ ###")

        with patch("src.ir.parser.parse_model_file") as mock_parse:
            mock_parse.side_effect = Exception("Parse error: unexpected token")
            result = parse_single_model(model_file)

        assert result["status"] == "failure"
        assert "parse_time_seconds" in result
        assert result["error"]["category"] == "syntax_error"
        assert "Parse error" in result["error"]["message"]

    def test_parse_failure_validation_error(self, tmp_path: Path) -> None:
        """Test parse failure due to validation error."""
        model_file = tmp_path / "invalid_model.gms"
        model_file.write_text("* Model with validation issues")

        mock_model = MagicMock()
        mock_model.variables = {"x": {}}
        mock_model.equations = {}

        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
            with patch("src.validation.model.validate_model_structure") as mock_validate:
                mock_validate.side_effect = Exception("Variable 'y' is not defined")
                result = parse_single_model(model_file)

        assert result["status"] == "failure"
        assert result["error"]["category"] == "validation_error"
        assert "not defined" in result["error"]["message"]

    def test_parse_failure_unsupported_feature(self, tmp_path: Path) -> None:
        """Test parse failure due to unsupported feature."""
        model_file = tmp_path / "unsupported_model.gms"
        model_file.write_text("* Model with unsupported functions")

        with patch("src.ir.parser.parse_model_file") as mock_parse:
            mock_parse.side_effect = Exception("Function 'gamma' is not yet implemented")
            result = parse_single_model(model_file)

        assert result["status"] == "failure"
        assert result["error"]["category"] == "unsupported_feature"
        assert "not yet implemented" in result["error"]["message"]

    def test_parse_truncates_long_error_messages(self, tmp_path: Path) -> None:
        """Test that long error messages are truncated to 500 characters."""
        model_file = tmp_path / "error_model.gms"
        model_file.write_text("* Model with long error")

        long_error = "Error: " + "x" * 600  # Create 600+ char error

        with patch("src.ir.parser.parse_model_file") as mock_parse:
            mock_parse.side_effect = Exception(long_error)
            result = parse_single_model(model_file)

        assert result["status"] == "failure"
        assert len(result["error"]["message"]) == 500

    def test_parse_records_timing(self, tmp_path: Path) -> None:
        """Test that parse timing is recorded for both success and failure."""
        model_file = tmp_path / "timing_model.gms"
        model_file.write_text("* Test timing")

        # Test success timing
        mock_model = MagicMock()
        mock_model.variables = {}
        mock_model.equations = {}

        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
            with patch("src.validation.model.validate_model_structure"):
                result = parse_single_model(model_file)

        assert "parse_time_seconds" in result
        assert isinstance(result["parse_time_seconds"], (int, float))
        assert result["parse_time_seconds"] >= 0


class TestRunBatchParse:
    """Tests for run_batch_parse function."""

    def _make_args(
        self,
        dry_run: bool = False,
        limit: int | None = None,
        model: str | None = None,
        verbose: bool = False,
        save_every: int = 10,
    ) -> argparse.Namespace:
        """Create argparse.Namespace with default values."""
        return argparse.Namespace(
            dry_run=dry_run,
            limit=limit,
            model=model,
            verbose=verbose,
            save_every=save_every,
        )

    def test_dry_run_does_not_modify_database(self, tmp_path: Path) -> None:
        """Test dry run mode doesn't modify the database."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
            ]
        }
        model_file = tmp_path / "model1.gms"
        model_file.write_text("* Test model")

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database") as mock_save:
                with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                    args = self._make_args(dry_run=True)
                    stats = run_batch_parse(args)

        # save_database should not be called in dry run
        mock_save.assert_not_called()
        assert stats["processed"] == 1
        assert "nlp2mcp_parse" not in database["models"][0]

    def test_limit_restricts_models_processed(self, tmp_path: Path) -> None:
        """Test limit argument restricts number of models processed."""
        database = {
            "models": [
                {"model_id": f"model{i}", "convexity": {"status": "verified_convex"}}
                for i in range(10)
            ]
        }

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args(dry_run=True, limit=3)
                        stats = run_batch_parse(args)

        assert stats["total"] == 3

    def test_single_model_filter(self, tmp_path: Path) -> None:
        """Test processing a single specific model."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
                {"model_id": "target_model", "convexity": {"status": "verified_convex"}},
                {"model_id": "model3", "convexity": {"status": "verified_convex"}},
            ]
        }
        model_file = tmp_path / "target_model.gms"
        model_file.write_text("* Target model")

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args(dry_run=True, model="target_model")
                        stats = run_batch_parse(args)

        assert stats["total"] == 1

    def test_model_not_found_returns_error(self) -> None:
        """Test error when specified model is not found."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
            ]
        }

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            args = self._make_args(model="nonexistent_model")
            stats = run_batch_parse(args)

        assert "error" in stats
        assert "not found" in stats["error"].lower()

    def test_skips_missing_model_files(self, tmp_path: Path) -> None:
        """Test that missing model files are skipped."""
        database = {
            "models": [
                {"model_id": "missing_model", "convexity": {"status": "verified_convex"}},
            ]
        }
        # Don't create the file - it should be skipped

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        args = self._make_args()
                        stats = run_batch_parse(args)

        assert stats["skipped"] == 1
        assert stats["processed"] == 0

    def test_successful_parse_updates_database(self, tmp_path: Path) -> None:
        """Test successful parse updates database with results."""
        database = {
            "models": [
                {"model_id": "good_model", "convexity": {"status": "verified_convex"}},
            ]
        }
        model_file = tmp_path / "good_model.gms"
        model_file.write_text("* Good model")

        mock_model = MagicMock()
        mock_model.variables = {"x": {}, "y": {}}
        mock_model.equations = {"eq1": {}}

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
                            with patch("src.validation.model.validate_model_structure"):
                                args = self._make_args()
                                stats = run_batch_parse(args)

        assert stats["success"] == 1
        assert stats["failure"] == 0
        assert "nlp2mcp_parse" in database["models"][0]
        assert database["models"][0]["nlp2mcp_parse"]["status"] == "success"
        assert database["models"][0]["nlp2mcp_parse"]["variables_count"] == 2
        assert database["models"][0]["nlp2mcp_parse"]["equations_count"] == 1

    def test_failed_parse_updates_database_with_error(self, tmp_path: Path) -> None:
        """Test failed parse updates database with error information."""
        database = {
            "models": [
                {"model_id": "bad_model", "convexity": {"status": "verified_convex"}},
            ]
        }
        model_file = tmp_path / "bad_model.gms"
        model_file.write_text("* Bad model")

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        with patch("src.ir.parser.parse_model_file") as mock_parse:
                            mock_parse.side_effect = Exception("Parse error: invalid syntax")
                            args = self._make_args()
                            stats = run_batch_parse(args)

        assert stats["success"] == 0
        assert stats["failure"] == 1
        assert stats["error_categories"]["syntax_error"] == 1
        assert "nlp2mcp_parse" in database["models"][0]
        assert database["models"][0]["nlp2mcp_parse"]["status"] == "failure"
        assert database["models"][0]["nlp2mcp_parse"]["error"]["category"] == "syntax_error"

    def test_periodic_save(self, tmp_path: Path) -> None:
        """Test database is saved periodically based on save_every."""
        database = {
            "models": [
                {"model_id": f"model{i}", "convexity": {"status": "verified_convex"}}
                for i in range(5)
            ]
        }
        for i in range(5):
            model_file = tmp_path / f"model{i}.gms"
            model_file.write_text(f"* Model {i}")

        mock_model = MagicMock()
        mock_model.variables = {}
        mock_model.equations = {}

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database") as mock_save:
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
                            with patch("src.validation.model.validate_model_structure"):
                                args = self._make_args(save_every=2)
                                run_batch_parse(args)

        # Should save at processed=2, processed=4, and final save = 3 calls
        assert mock_save.call_count == 3

    def test_calculates_success_rate(self, tmp_path: Path) -> None:
        """Test success rate calculation."""
        database = {
            "models": [
                {"model_id": "model1", "convexity": {"status": "verified_convex"}},
                {"model_id": "model2", "convexity": {"status": "verified_convex"}},
            ]
        }
        for model_id in ["model1", "model2"]:
            model_file = tmp_path / f"{model_id}.gms"
            model_file.write_text(f"* {model_id}")

        mock_model = MagicMock()
        mock_model.variables = {}
        mock_model.equations = {}

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
                            with patch("src.validation.model.validate_model_structure"):
                                args = self._make_args()
                                stats = run_batch_parse(args)

        assert stats["success_rate"] == 100.0

    def test_tracks_successful_models(self, tmp_path: Path) -> None:
        """Test successful model IDs are tracked."""
        database = {
            "models": [
                {"model_id": "success_model", "convexity": {"status": "verified_convex"}},
            ]
        }
        model_file = tmp_path / "success_model.gms"
        model_file.write_text("* Success model")

        mock_model = MagicMock()
        mock_model.variables = {}
        mock_model.equations = {}

        with patch("scripts.gamslib.batch_parse.load_database", return_value=database):
            with patch("scripts.gamslib.batch_parse.save_database"):
                with patch("scripts.gamslib.batch_parse.create_backup", return_value=None):
                    with patch("scripts.gamslib.batch_parse.RAW_MODELS_DIR", tmp_path):
                        with patch("src.ir.parser.parse_model_file", return_value=mock_model):
                            with patch("src.validation.model.validate_model_structure"):
                                args = self._make_args()
                                stats = run_batch_parse(args)

        assert "success_model" in stats["successful_models"]


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_prints_basic_stats(self) -> None:
        """Test basic statistics are printed."""
        stats = {
            "total": 10,
            "processed": 8,
            "success": 6,
            "failure": 2,
            "skipped": 2,
            "success_rate": 75.0,
            "total_time": 10.5,
            "error_categories": {},
            "successful_models": [],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "8/10" in output
        assert "Success: 6" in output
        assert "75.0%" in output
        assert "Failure: 2" in output
        assert "Skipped: 2" in output
        assert "10.5s" in output

    def test_prints_error_categories(self) -> None:
        """Test error categories are printed."""
        stats = {
            "total": 10,
            "processed": 10,
            "success": 5,
            "failure": 5,
            "skipped": 0,
            "success_rate": 50.0,
            "total_time": 20.0,
            "error_categories": {
                "syntax_error": 3,
                "unsupported_feature": 2,
            },
            "successful_models": [],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "syntax_error: 3" in output
        assert "unsupported_feature: 2" in output
        assert "60%" in output  # 3/5 = 60%

    def test_prints_successful_models(self) -> None:
        """Test successful model list is printed."""
        stats = {
            "total": 3,
            "processed": 3,
            "success": 2,
            "failure": 1,
            "skipped": 0,
            "success_rate": 66.7,
            "total_time": 5.0,
            "error_categories": {},
            "successful_models": ["model_a", "model_b"],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "Successful models (2)" in output
        assert "model_a" in output
        assert "model_b" in output

    def test_handles_zero_processed(self) -> None:
        """Test handles zero processed models gracefully."""
        stats = {
            "total": 5,
            "processed": 0,
            "success": 0,
            "failure": 0,
            "skipped": 5,
            "success_rate": 0,
            "total_time": 0.1,
            "error_categories": {},
            "successful_models": [],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "0/5" in output
        assert "Skipped: 5" in output

    def test_prints_average_time_per_model(self) -> None:
        """Test average time per model is printed."""
        stats = {
            "total": 4,
            "processed": 4,
            "success": 4,
            "failure": 0,
            "skipped": 0,
            "success_rate": 100.0,
            "total_time": 8.0,
            "error_categories": {},
            "successful_models": ["m1", "m2", "m3", "m4"],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        assert "2.00s" in output  # 8.0 / 4 = 2.0

    def test_handles_zero_failures_in_error_categories(self) -> None:
        """Test handles case with zero failures when showing error categories."""
        stats = {
            "total": 2,
            "processed": 2,
            "success": 2,
            "failure": 0,
            "skipped": 0,
            "success_rate": 100.0,
            "total_time": 2.0,
            "error_categories": {},
            "successful_models": ["m1", "m2"],
        }

        captured_output = io.StringIO()
        with patch("sys.stdout", captured_output):
            print_summary(stats)

        output = captured_output.getvalue()
        # Should not contain "Error categories:" section when no errors
        assert "Error categories:" not in output
