"""Tests for GAMSLIB batch parse script."""

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

    def test_objective_function_error(self) -> None:
        """Test objective function error is categorized as syntax_error."""
        error = "Objective function validation failed"
        category = categorize_error(error)
        assert category == "syntax_error"

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

        # Test failure timing
        with patch("src.ir.parser.parse_model_file") as mock_parse:
            mock_parse.side_effect = Exception("Test error")
            result = parse_single_model(model_file)

        assert "parse_time_seconds" in result
        assert isinstance(result["parse_time_seconds"], (int, float))
        assert result["parse_time_seconds"] >= 0
